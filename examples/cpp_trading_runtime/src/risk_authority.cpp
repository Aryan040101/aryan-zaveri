#include "risk_authority.hpp"

namespace runtime {

RiskAuthority::RiskAuthority(RiskLimits limits) : limits_(limits) {}

RiskDecision RiskAuthority::evaluate(const Signal& signal, const HotStateStore& state, long now_ms) const {
    const auto quote = state.quote_for(signal.symbol);
    if (!quote) {
        return {false, "missing_quote", 0, 0.0};
    }
    if (now_ms - quote->updated_at_ms > limits_.max_quote_age_ms) {
        return {false, "stale_quote", 0, 0.0};
    }
    if (signal.confidence < limits_.min_confidence) {
        return {false, "confidence_below_threshold", 0, 0.0};
    }
    if (signal.requested_quantity <= 0) {
        return {false, "quantity_zero", 0, 0.0};
    }
    if (state.has_open_position(signal.symbol)) {
        return {false, "duplicate_position", 0, 0.0};
    }
    if (state.active_order_count() >= limits_.max_active_orders) {
        return {false, "active_order_limit", 0, 0.0};
    }

    const double reference = mid_price(*quote);
    const double projected = reference * signal.requested_quantity;
    if (state.global_notional() + projected > limits_.global_notional_limit) {
        return {false, "global_notional_limit", 0, projected};
    }
    if (state.segment_notional(signal.segment) + projected > limits_.segment_notional_limit) {
        return {false, "segment_notional_limit", 0, projected};
    }
    if (state.symbol_notional(signal.symbol) + projected > limits_.symbol_notional_limit) {
        return {false, "symbol_notional_limit", 0, projected};
    }
    return {true, "approved_by_risk_authority", signal.requested_quantity, projected};
}

}  // namespace runtime
