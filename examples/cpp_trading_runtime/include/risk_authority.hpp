#pragma once

#include "hot_state.hpp"
#include "runtime_types.hpp"

namespace runtime {

class RiskAuthority {
public:
    explicit RiskAuthority(RiskLimits limits);

    RiskDecision evaluate(const Signal& signal, const HotStateStore& state, long now_ms) const;

private:
    RiskLimits limits_;
};

}  // namespace runtime
