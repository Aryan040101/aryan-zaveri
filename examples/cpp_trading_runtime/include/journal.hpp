#pragma once

#include "runtime_types.hpp"

#include <mutex>
#include <string>
#include <vector>

namespace runtime {

class Journal {
public:
    void heartbeat(const std::string& component, const std::string& status);
    void signal_received(const Signal& signal);
    void risk_decision(const Signal& signal, const RiskDecision& decision);
    void order_intent(const OrderIntent& intent);
    void fill(const Fill& fill);
    void state_snapshot(const std::string& state_json);
    std::string report_json() const;

private:
    void append(std::string event_json);

    mutable std::mutex mutex_;
    std::vector<std::string> events_;
};

std::string quote_json(const std::string& value);
std::string fixed_json(double value);

}  // namespace runtime
