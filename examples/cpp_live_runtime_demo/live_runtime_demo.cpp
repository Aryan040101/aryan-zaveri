#include <atomic>
#include <condition_variable>
#include <cstddef>
#include <deque>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <mutex>
#include <optional>
#include <regex>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <unordered_map>
#include <utility>
#include <vector>

namespace {

struct Signal {
    std::string symbol;
    std::string segment;
    std::string side;
    std::string timeframe;
    double reference_price = 0.0;
    int quantity = 0;
    double confidence = 0.0;
};

struct RiskContract {
    double global_capital_limit = 0.0;
    double cash_segment_limit = 0.0;
    double derivatives_segment_limit = 0.0;
    double max_order_notional = 0.0;
    double min_confidence = 0.0;
    double max_slippage_bps = 0.0;
};

struct RiskDecision {
    bool accepted = false;
    std::string reason;
    double projected_notional = 0.0;
};

struct OrderIntent {
    std::string symbol;
    std::string segment;
    std::string side;
    int quantity = 0;
    double reference_price = 0.0;
    double limit_price = 0.0;
    std::string reason;
};

template <typename T>
class BlockingQueue {
public:
    void push(T value) {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            queue_.push_back(std::move(value));
        }
        cv_.notify_one();
    }

    std::optional<T> pop() {
        std::unique_lock<std::mutex> lock(mutex_);
        cv_.wait(lock, [&] { return closed_ || !queue_.empty(); });
        if (queue_.empty()) {
            return std::nullopt;
        }
        T value = std::move(queue_.front());
        queue_.pop_front();
        return value;
    }

    void close() {
        {
            std::lock_guard<std::mutex> lock(mutex_);
            closed_ = true;
        }
        cv_.notify_all();
    }

private:
    std::mutex mutex_;
    std::condition_variable cv_;
    std::deque<T> queue_;
    bool closed_ = false;
};

std::string read_file(const std::string& path) {
    std::ifstream in(path);
    if (!in) {
        throw std::runtime_error("could not open " + path);
    }
    std::ostringstream ss;
    ss << in.rdbuf();
    return ss.str();
}

std::string json_string(const std::string& object, const std::string& key) {
    const std::regex pattern("\"" + key + "\"\\s*:\\s*\"([^\"]*)\"");
    std::smatch match;
    if (!std::regex_search(object, match, pattern)) {
        throw std::runtime_error("missing string field: " + key);
    }
    return match[1].str();
}

double json_number(const std::string& object, const std::string& key) {
    const std::regex pattern("\"" + key + "\"\\s*:\\s*(-?[0-9]+(?:\\.[0-9]+)?)");
    std::smatch match;
    if (!std::regex_search(object, match, pattern)) {
        throw std::runtime_error("missing numeric field: " + key);
    }
    return std::stod(match[1].str());
}

std::vector<std::string> json_objects(const std::string& document) {
    std::vector<std::string> objects;
    const std::regex pattern("\\{[^{}]*\\}");
    for (std::sregex_iterator it(document.begin(), document.end(), pattern), end; it != end; ++it) {
        objects.push_back(it->str());
    }
    return objects;
}

RiskContract parse_contract(const std::string& document) {
    RiskContract contract;
    contract.global_capital_limit = json_number(document, "global_capital_limit");
    contract.cash_segment_limit = json_number(document, "cash_segment_limit");
    contract.derivatives_segment_limit = json_number(document, "derivatives_segment_limit");
    contract.max_order_notional = json_number(document, "max_order_notional");
    contract.min_confidence = json_number(document, "min_confidence");
    contract.max_slippage_bps = json_number(document, "max_slippage_bps");
    return contract;
}

Signal parse_signal(const std::string& object) {
    Signal signal;
    signal.symbol = json_string(object, "symbol");
    signal.segment = json_string(object, "segment");
    signal.side = json_string(object, "side");
    signal.timeframe = json_string(object, "timeframe");
    signal.reference_price = json_number(object, "reference_price");
    signal.quantity = static_cast<int>(json_number(object, "quantity"));
    signal.confidence = json_number(object, "confidence");
    return signal;
}

std::vector<Signal> parse_signals(const std::string& document) {
    std::vector<Signal> signals;
    for (const auto& object : json_objects(document)) {
        signals.push_back(parse_signal(object));
    }
    return signals;
}

std::string quoted(const std::string& value) {
    std::ostringstream out;
    out << '"';
    for (const char c : value) {
        if (c == '"' || c == '\\') {
            out << '\\';
        }
        out << c;
    }
    out << '"';
    return out.str();
}

std::string fixed2(double value) {
    std::ostringstream out;
    out << std::fixed << std::setprecision(2) << value;
    return out.str();
}

class Journal {
public:
    void append(std::string event) {
        std::lock_guard<std::mutex> lock(mutex_);
        events_.push_back(std::move(event));
    }

    std::string to_json(int accepted, int rejected, int filled) const {
        std::ostringstream out;
        out << "{\n";
        out << "  \"runtime\": \"cpp_live_runtime_demo\",\n";
        out << "  \"events\": [\n";
        for (std::size_t i = 0; i < events_.size(); ++i) {
            out << "    " << events_[i];
            if (i + 1 < events_.size()) {
                out << ",";
            }
            out << "\n";
        }
        out << "  ],\n";
        out << "  \"summary\": {\n";
        out << "    \"accepted\": " << accepted << ",\n";
        out << "    \"rejected\": " << rejected << ",\n";
        out << "    \"filled\": " << filled << "\n";
        out << "  }\n";
        out << "}\n";
        return out.str();
    }

private:
    mutable std::mutex mutex_;
    std::vector<std::string> events_;
};

class RiskAuthority {
public:
    explicit RiskAuthority(RiskContract contract) : contract_(contract) {}

    RiskDecision evaluate(const Signal& signal) {
        const double notional = signal.reference_price * signal.quantity;
        std::lock_guard<std::mutex> lock(mutex_);

        if (signal.confidence < contract_.min_confidence) {
            return {false, "confidence_below_threshold", notional};
        }
        if (notional > contract_.max_order_notional) {
            return {false, "order_notional_limit", notional};
        }
        if (global_reserved_ + notional > contract_.global_capital_limit) {
            return {false, "global_capital_limit", notional};
        }
        if (segment_reserved_[signal.segment] + notional > segment_limit(signal.segment)) {
            return {false, "segment_capital_limit", notional};
        }

        global_reserved_ += notional;
        segment_reserved_[signal.segment] += notional;
        return {true, "approved_by_risk_authority", notional};
    }

    void release(const OrderIntent& intent) {
        const double notional = intent.reference_price * intent.quantity;
        std::lock_guard<std::mutex> lock(mutex_);
        global_reserved_ -= notional;
        segment_reserved_[intent.segment] -= notional;
    }

    double max_slippage_bps() const {
        return contract_.max_slippage_bps;
    }

private:
    double segment_limit(const std::string& segment) const {
        if (segment == "cash") {
            return contract_.cash_segment_limit;
        }
        return contract_.derivatives_segment_limit;
    }

    RiskContract contract_;
    std::mutex mutex_;
    double global_reserved_ = 0.0;
    std::unordered_map<std::string, double> segment_reserved_;
};

double adaptive_limit_price(const Signal& signal, double max_slippage_bps) {
    const double lean = (max_slippage_bps / 10000.0) * 0.35;
    if (signal.side == "BUY") {
        return signal.reference_price * (1.0 + lean);
    }
    return signal.reference_price * (1.0 - lean);
}

std::string risk_event_json(const Signal& signal, const RiskDecision& decision) {
    std::ostringstream out;
    out << "{";
    out << "\"event\":\"risk_decision\",";
    out << "\"symbol\":" << quoted(signal.symbol) << ",";
    out << "\"segment\":" << quoted(signal.segment) << ",";
    out << "\"side\":" << quoted(signal.side) << ",";
    out << "\"accepted\":" << (decision.accepted ? "true" : "false") << ",";
    out << "\"reason\":" << quoted(decision.reason) << ",";
    out << "\"projected_notional\":" << fixed2(decision.projected_notional);
    out << "}";
    return out.str();
}

std::string intent_event_json(const OrderIntent& intent) {
    std::ostringstream out;
    out << "{";
    out << "\"event\":\"order_intent\",";
    out << "\"symbol\":" << quoted(intent.symbol) << ",";
    out << "\"segment\":" << quoted(intent.segment) << ",";
    out << "\"side\":" << quoted(intent.side) << ",";
    out << "\"quantity\":" << intent.quantity << ",";
    out << "\"reference_price\":" << fixed2(intent.reference_price) << ",";
    out << "\"limit_price\":" << fixed2(intent.limit_price) << ",";
    out << "\"reason\":" << quoted(intent.reason);
    out << "}";
    return out.str();
}

std::string fill_event_json(const OrderIntent& intent, double fill_price) {
    std::ostringstream out;
    out << "{";
    out << "\"event\":\"execution_fill\",";
    out << "\"symbol\":" << quoted(intent.symbol) << ",";
    out << "\"side\":" << quoted(intent.side) << ",";
    out << "\"quantity\":" << intent.quantity << ",";
    out << "\"fill_price\":" << fixed2(fill_price) << ",";
    out << "\"source\":\"synthetic_execution_engine\"";
    out << "}";
    return out.str();
}

OrderIntent build_intent(const Signal& signal, const RiskDecision& decision, double max_slippage_bps) {
    return OrderIntent{
        signal.symbol,
        signal.segment,
        signal.side,
        signal.quantity,
        signal.reference_price,
        adaptive_limit_price(signal, max_slippage_bps),
        decision.reason
    };
}

double simulated_fill_price(const OrderIntent& intent) {
    const double micro_slip = 0.0001;
    if (intent.side == "BUY") {
        return intent.limit_price * (1.0 + micro_slip);
    }
    return intent.limit_price * (1.0 - micro_slip);
}

}  // namespace

int main(int argc, char** argv) {
    const std::string contract_path = argc > 1 ? argv[1] : "examples/cpp_live_runtime_demo/risk_contract.json";
    const std::string signals_path = argc > 2 ? argv[2] : "examples/cpp_live_runtime_demo/sample_signals.json";

    const RiskContract contract = parse_contract(read_file(contract_path));
    const std::vector<Signal> signals = parse_signals(read_file(signals_path));

    BlockingQueue<Signal> signal_queue;
    BlockingQueue<OrderIntent> order_queue;
    Journal journal;
    RiskAuthority risk(contract);
    std::atomic<int> accepted{0};
    std::atomic<int> rejected{0};
    std::atomic<int> filled{0};

    std::thread risk_worker([&] {
        while (auto signal = signal_queue.pop()) {
            const RiskDecision decision = risk.evaluate(*signal);
            journal.append(risk_event_json(*signal, decision));
            if (!decision.accepted) {
                ++rejected;
                continue;
            }
            ++accepted;
            const OrderIntent intent = build_intent(*signal, decision, risk.max_slippage_bps());
            journal.append(intent_event_json(intent));
            order_queue.push(intent);
        }
        order_queue.close();
    });

    std::thread execution_worker([&] {
        while (auto intent = order_queue.pop()) {
            const double fill_price = simulated_fill_price(*intent);
            journal.append(fill_event_json(*intent, fill_price));
            risk.release(*intent);
            ++filled;
        }
    });

    for (const auto& signal : signals) {
        signal_queue.push(signal);
    }
    signal_queue.close();

    risk_worker.join();
    execution_worker.join();

    std::cout << journal.to_json(accepted.load(), rejected.load(), filled.load());
    return 0;
}
