#include "order_manager.hpp"

#include <algorithm>
#include <sstream>

namespace runtime {

OrderManager::OrderManager(double max_slippage_bps) : max_slippage_bps_(max_slippage_bps) {}

OrderIntent OrderManager::build_intent(const Signal& signal, const RiskDecision& decision, const MarketQuote& quote) {
    const double reference = mid_price(quote);
    const double lean = (max_slippage_bps_ / 10000.0) * 0.35;
    const double limit = signal.side == Side::Buy ? reference * (1.0 + lean) : reference * (1.0 - lean);
    std::ostringstream id;
    id << "public-" << signal.signal_id;
    return OrderIntent{
        id.str(),
        signal.signal_id,
        signal.symbol,
        signal.segment,
        signal.side,
        OrderAction::Open,
        decision.approved_quantity,
        reference,
        limit,
        0,
    };
}

OrderIntent OrderManager::adapt_price(const OrderIntent& intent, const MarketQuote& quote) const {
    OrderIntent adjusted = intent;
    const double mid = mid_price(quote);
    const double spread = std::max(0.0, quote.ask - quote.bid);
    const double spread_half = spread / 2.0;
    const double cap = mid * (max_slippage_bps_ / 10000.0);
    const double improvement = std::min(spread_half * 0.50, cap);
    adjusted.limit_price = intent.side == Side::Buy ? quote.bid + improvement : quote.ask - improvement;
    adjusted.replace_count = intent.replace_count + 1;
    return adjusted;
}

Fill OrderManager::simulate_fill(const OrderIntent& intent) const {
    const double fee_bps = 2.0;
    const double notional = intent.limit_price * intent.quantity;
    return Fill{
        intent.client_order_id,
        intent.symbol,
        intent.segment,
        intent.side,
        intent.quantity,
        intent.limit_price,
        notional,
        notional * fee_bps / 10000.0,
    };
}

}  // namespace runtime
