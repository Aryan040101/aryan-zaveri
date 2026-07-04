#pragma once

#include "hot_state.hpp"
#include "runtime_types.hpp"

namespace runtime {

class OrderManager {
public:
    explicit OrderManager(double max_slippage_bps);

    OrderIntent build_intent(const Signal& signal, const RiskDecision& decision, const MarketQuote& quote);
    OrderIntent adapt_price(const OrderIntent& intent, const MarketQuote& quote) const;
    Fill simulate_fill(const OrderIntent& intent) const;

private:
    double max_slippage_bps_;
};

}  // namespace runtime
