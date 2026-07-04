#include "journal.hpp"

#include <iomanip>
#include <sstream>

namespace runtime {

std::string quote_json(const std::string& value) {
    std::ostringstream out;
    out << '"';
    for (const char ch : value) {
        if (ch == '"' || ch == '\\') {
            out << '\\';
        }
        out << ch;
    }
    out << '"';
    return out.str();
}

std::string fixed_json(double value) {
    std::ostringstream out;
    out << std::fixed << std::setprecision(4) << value;
    return out.str();
}

void Journal::append(std::string event_json) {
    std::lock_guard<std::mutex> lock(mutex_);
    events_.push_back(std::move(event_json));
}

void Journal::heartbeat(const std::string& component, const std::string& status) {
    std::ostringstream out;
    out << "{";
    out << "\"event\":\"heartbeat\",";
    out << "\"component\":" << quote_json(component) << ",";
    out << "\"status\":" << quote_json(status);
    out << "}";
    append(out.str());
}

void Journal::signal_received(const Signal& signal) {
    std::ostringstream out;
    out << "{";
    out << "\"event\":\"signal_received\",";
    out << "\"signal_id\":" << quote_json(signal.signal_id) << ",";
    out << "\"symbol\":" << quote_json(signal.symbol) << ",";
    out << "\"segment\":" << quote_json(signal.segment) << ",";
    out << "\"side\":" << quote_json(side_name(signal.side)) << ",";
    out << "\"score\":" << fixed_json(signal.score) << ",";
    out << "\"confidence\":" << fixed_json(signal.confidence) << ",";
    out << "\"requested_quantity\":" << signal.requested_quantity;
    out << "}";
    append(out.str());
}

void Journal::risk_decision(const Signal& signal, const RiskDecision& decision) {
    std::ostringstream out;
    out << "{";
    out << "\"event\":\"risk_decision\",";
    out << "\"signal_id\":" << quote_json(signal.signal_id) << ",";
    out << "\"symbol\":" << quote_json(signal.symbol) << ",";
    out << "\"accepted\":" << (decision.accepted ? "true" : "false") << ",";
    out << "\"reason\":" << quote_json(decision.reason) << ",";
    out << "\"approved_quantity\":" << decision.approved_quantity << ",";
    out << "\"projected_notional\":" << fixed_json(decision.projected_notional);
    out << "}";
    append(out.str());
}

void Journal::order_intent(const OrderIntent& intent) {
    std::ostringstream out;
    out << "{";
    out << "\"event\":\"order_intent\",";
    out << "\"client_order_id\":" << quote_json(intent.client_order_id) << ",";
    out << "\"signal_id\":" << quote_json(intent.signal_id) << ",";
    out << "\"symbol\":" << quote_json(intent.symbol) << ",";
    out << "\"segment\":" << quote_json(intent.segment) << ",";
    out << "\"side\":" << quote_json(side_name(intent.side)) << ",";
    out << "\"action\":" << quote_json(action_name(intent.action)) << ",";
    out << "\"quantity\":" << intent.quantity << ",";
    out << "\"reference_price\":" << fixed_json(intent.reference_price) << ",";
    out << "\"limit_price\":" << fixed_json(intent.limit_price) << ",";
    out << "\"replace_count\":" << intent.replace_count;
    out << "}";
    append(out.str());
}

void Journal::fill(const Fill& fill) {
    std::ostringstream out;
    out << "{";
    out << "\"event\":\"execution_fill\",";
    out << "\"client_order_id\":" << quote_json(fill.client_order_id) << ",";
    out << "\"symbol\":" << quote_json(fill.symbol) << ",";
    out << "\"segment\":" << quote_json(fill.segment) << ",";
    out << "\"side\":" << quote_json(side_name(fill.side)) << ",";
    out << "\"quantity\":" << fill.quantity << ",";
    out << "\"fill_price\":" << fixed_json(fill.fill_price) << ",";
    out << "\"notional\":" << fixed_json(fill.notional) << ",";
    out << "\"fee\":" << fixed_json(fill.fee);
    out << "}";
    append(out.str());
}

void Journal::state_snapshot(const std::string& state_json) {
    std::ostringstream out;
    out << "{";
    out << "\"event\":\"state_snapshot\",";
    out << "\"state\":" << state_json;
    out << "}";
    append(out.str());
}

std::string Journal::report_json() const {
    std::lock_guard<std::mutex> lock(mutex_);
    std::ostringstream out;
    out << "{\n";
    out << "  \"runtime\": \"cpp_trading_runtime\",\n";
    out << "  \"language\": \"C++20\",\n";
    out << "  \"components\": [\"hot_state\", \"risk_authority\", \"order_manager\", \"journal\", \"worker_queues\"],\n";
    out << "  \"events\": [\n";
    for (std::size_t i = 0; i < events_.size(); ++i) {
        out << "    " << events_[i];
        if (i + 1 < events_.size()) {
            out << ",";
        }
        out << "\n";
    }
    out << "  ]\n";
    out << "}\n";
    return out.str();
}

}  // namespace runtime
