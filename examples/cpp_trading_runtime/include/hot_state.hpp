#pragma once

#include "runtime_types.hpp"

#include <mutex>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

namespace runtime {

class HotStateStore {
public:
    void update_quote(MarketQuote quote);
    std::optional<MarketQuote> quote_for(const std::string& symbol) const;

    bool has_open_position(const std::string& symbol) const;
    void add_working_order(const OrderIntent& intent);
    void remove_working_order(const std::string& client_order_id);
    int active_order_count() const;

    void apply_fill(const Fill& fill);
    double symbol_notional(const std::string& symbol) const;
    double segment_notional(const std::string& segment) const;
    double global_notional() const;
    std::string snapshot_json() const;

private:
    mutable std::mutex mutex_;
    std::unordered_map<std::string, MarketQuote> quotes_;
    std::unordered_map<std::string, OrderIntent> working_orders_;
    std::unordered_map<std::string, Position> positions_;
    std::unordered_map<std::string, double> segment_reserved_;
    double global_reserved_ = 0.0;
};

}  // namespace runtime
