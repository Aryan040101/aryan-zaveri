#pragma once

#include <optional>
#include <string>

namespace runtime {

enum class Side {
    Buy,
    Sell,
};

enum class OrderAction {
    Open,
    Close,
};

struct MarketQuote {
    std::string symbol;
    double bid = 0.0;
    double ask = 0.0;
    long updated_at_ms = 0;
};

struct Signal {
    std::string signal_id;
    std::string symbol;
    std::string segment;
    Side side = Side::Buy;
    double score = 0.0;
    double confidence = 0.0;
    int requested_quantity = 0;
    long created_at_ms = 0;
};

struct RiskLimits {
    double global_notional_limit = 100000.0;
    double segment_notional_limit = 50000.0;
    double symbol_notional_limit = 25000.0;
    int max_active_orders = 4;
    double min_confidence = 0.60;
    long max_quote_age_ms = 1500;
};

struct RiskDecision {
    bool accepted = false;
    std::string reason;
    int approved_quantity = 0;
    double projected_notional = 0.0;
};

struct OrderIntent {
    std::string client_order_id;
    std::string signal_id;
    std::string symbol;
    std::string segment;
    Side side = Side::Buy;
    OrderAction action = OrderAction::Open;
    int quantity = 0;
    double reference_price = 0.0;
    double limit_price = 0.0;
    int replace_count = 0;
};

struct Fill {
    std::string client_order_id;
    std::string symbol;
    std::string segment;
    Side side = Side::Buy;
    int quantity = 0;
    double fill_price = 0.0;
    double notional = 0.0;
    double fee = 0.0;
};

struct Position {
    std::string symbol;
    std::string segment;
    Side side = Side::Buy;
    int quantity = 0;
    double avg_price = 0.0;
};

inline std::string side_name(Side side) {
    return side == Side::Buy ? "BUY" : "SELL";
}

inline std::string action_name(OrderAction action) {
    return action == OrderAction::Open ? "OPEN" : "CLOSE";
}

inline double mid_price(const MarketQuote& quote) {
    return (quote.bid + quote.ask) / 2.0;
}

}  // namespace runtime
