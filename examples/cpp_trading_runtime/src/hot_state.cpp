#include "hot_state.hpp"

#include "journal.hpp"

#include <sstream>

namespace runtime {

void HotStateStore::update_quote(MarketQuote quote) {
    std::lock_guard<std::mutex> lock(mutex_);
    quotes_[quote.symbol] = std::move(quote);
}

std::optional<MarketQuote> HotStateStore::quote_for(const std::string& symbol) const {
    std::lock_guard<std::mutex> lock(mutex_);
    const auto it = quotes_.find(symbol);
    if (it == quotes_.end()) {
        return std::nullopt;
    }
    return it->second;
}

bool HotStateStore::has_open_position(const std::string& symbol) const {
    std::lock_guard<std::mutex> lock(mutex_);
    const auto it = positions_.find(symbol);
    return it != positions_.end() && it->second.quantity != 0;
}

void HotStateStore::add_working_order(const OrderIntent& intent) {
    std::lock_guard<std::mutex> lock(mutex_);
    working_orders_[intent.client_order_id] = intent;
    const double notional = intent.reference_price * intent.quantity;
    global_reserved_ += notional;
    segment_reserved_[intent.segment] += notional;
}

void HotStateStore::remove_working_order(const std::string& client_order_id) {
    std::lock_guard<std::mutex> lock(mutex_);
    const auto it = working_orders_.find(client_order_id);
    if (it == working_orders_.end()) {
        return;
    }
    const double notional = it->second.reference_price * it->second.quantity;
    global_reserved_ -= notional;
    segment_reserved_[it->second.segment] -= notional;
    working_orders_.erase(it);
}

int HotStateStore::active_order_count() const {
    std::lock_guard<std::mutex> lock(mutex_);
    return static_cast<int>(working_orders_.size());
}

void HotStateStore::apply_fill(const Fill& fill) {
    std::lock_guard<std::mutex> lock(mutex_);
    auto& position = positions_[fill.symbol];
    position.symbol = fill.symbol;
    position.segment = fill.segment;
    position.side = fill.side;
    const int old_quantity = position.quantity;
    const int new_quantity = old_quantity + fill.quantity;
    if (new_quantity <= 0) {
        positions_.erase(fill.symbol);
        return;
    }
    const double old_notional = position.avg_price * old_quantity;
    const double new_notional = old_notional + fill.fill_price * fill.quantity;
    position.quantity = new_quantity;
    position.avg_price = new_notional / new_quantity;
}

double HotStateStore::symbol_notional(const std::string& symbol) const {
    std::lock_guard<std::mutex> lock(mutex_);
    double total = 0.0;
    const auto pos = positions_.find(symbol);
    const auto quote = quotes_.find(symbol);
    if (pos != positions_.end() && quote != quotes_.end()) {
        total += mid_price(quote->second) * pos->second.quantity;
    }
    for (const auto& [_, order] : working_orders_) {
        if (order.symbol == symbol) {
            total += order.reference_price * order.quantity;
        }
    }
    return total;
}

double HotStateStore::segment_notional(const std::string& segment) const {
    std::lock_guard<std::mutex> lock(mutex_);
    double total = 0.0;
    const auto reserved = segment_reserved_.find(segment);
    if (reserved != segment_reserved_.end()) {
        total += reserved->second;
    }
    for (const auto& [symbol, position] : positions_) {
        if (position.segment != segment) {
            continue;
        }
        const auto quote = quotes_.find(symbol);
        if (quote != quotes_.end()) {
            total += mid_price(quote->second) * position.quantity;
        }
    }
    return total;
}

double HotStateStore::global_notional() const {
    std::lock_guard<std::mutex> lock(mutex_);
    double total = global_reserved_;
    for (const auto& [symbol, position] : positions_) {
        const auto quote = quotes_.find(symbol);
        if (quote != quotes_.end()) {
            total += mid_price(quote->second) * position.quantity;
        }
    }
    return total;
}

std::string HotStateStore::snapshot_json() const {
    std::lock_guard<std::mutex> lock(mutex_);
    std::ostringstream out;
    out << "{";
    out << "\"quotes\":" << quotes_.size() << ",";
    out << "\"working_orders\":" << working_orders_.size() << ",";
    out << "\"positions\":" << positions_.size() << ",";
    out << "\"global_reserved\":" << fixed_json(global_reserved_);
    out << "}";
    return out.str();
}

}  // namespace runtime
