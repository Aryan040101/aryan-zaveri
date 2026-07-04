#include "blocking_queue.hpp"
#include "hot_state.hpp"
#include "journal.hpp"
#include "order_manager.hpp"
#include "risk_authority.hpp"

#include <atomic>
#include <iostream>
#include <thread>
#include <vector>

namespace runtime {

std::vector<Signal> sample_signals() {
    return {
        {"sig-001", "INDEX_TREND", "derivatives", Side::Buy, 0.82, 0.76, 80, 10000},
        {"sig-002", "SECTOR_REVERSAL", "cash", Side::Sell, -0.71, 0.69, 120, 10020},
        {"sig-003", "MACRO_THEME", "cash", Side::Buy, 0.48, 0.52, 90, 10040},
        {"sig-004", "INDEX_TREND", "derivatives", Side::Buy, 0.79, 0.73, 50, 10060},
    };
}

void seed_quotes(HotStateStore& state) {
    state.update_quote({"INDEX_TREND", 101.10, 101.18, 9950});
    state.update_quote({"SECTOR_REVERSAL", 87.42, 87.50, 9960});
    state.update_quote({"MACRO_THEME", 144.70, 144.86, 8000});
}

}  // namespace runtime

int main() {
    using namespace runtime;

    constexpr long now_ms = 10000;
    HotStateStore state;
    seed_quotes(state);

    RiskLimits limits;
    limits.global_notional_limit = 75000.0;
    limits.segment_notional_limit = 30000.0;
    limits.symbol_notional_limit = 18000.0;
    limits.max_active_orders = 3;
    limits.min_confidence = 0.60;
    limits.max_quote_age_ms = 1500;

    BlockingQueue<Signal> signal_queue;
    BlockingQueue<OrderIntent> order_queue;
    RiskAuthority risk(limits);
    OrderManager orders(5.0);
    Journal journal;
    std::atomic<int> accepted{0};
    std::atomic<int> rejected{0};
    std::atomic<int> filled{0};

    journal.heartbeat("cpp_trading_runtime", "started");
    journal.state_snapshot(state.snapshot_json());

    std::thread risk_worker([&] {
        while (auto signal = signal_queue.pop()) {
            journal.signal_received(*signal);
            const RiskDecision decision = risk.evaluate(*signal, state, now_ms);
            journal.risk_decision(*signal, decision);
            if (!decision.accepted) {
                ++rejected;
                continue;
            }
            const auto quote = state.quote_for(signal->symbol);
            if (!quote) {
                ++rejected;
                continue;
            }
            OrderIntent intent = orders.build_intent(*signal, decision, *quote);
            state.add_working_order(intent);
            journal.order_intent(intent);
            order_queue.push(intent);
            ++accepted;
        }
        order_queue.close();
    });

    std::thread order_worker([&] {
        while (auto intent = order_queue.pop()) {
            const auto quote = state.quote_for(intent->symbol);
            if (!quote) {
                continue;
            }
            OrderIntent adjusted = orders.adapt_price(*intent, *quote);
            journal.order_intent(adjusted);
            const Fill fill = orders.simulate_fill(adjusted);
            state.apply_fill(fill);
            state.remove_working_order(intent->client_order_id);
            journal.fill(fill);
            ++filled;
        }
    });

    for (const Signal& signal : sample_signals()) {
        signal_queue.push(signal);
    }
    signal_queue.close();

    risk_worker.join();
    order_worker.join();

    journal.state_snapshot(state.snapshot_json());
    journal.heartbeat("cpp_trading_runtime", "stopped");

    std::cout << journal.report_json();
    return 0;
}
