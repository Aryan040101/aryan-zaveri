cmake_minimum_required(VERSION 3.16)
project(cpp_trading_runtime_demo LANGUAGES CXX)

add_executable(cpp_trading_runtime
    src/hot_state.cpp
    src/journal.cpp
    src/order_manager.cpp
    src/risk_authority.cpp
    src/trading_runtime_main.cpp
)

target_include_directories(cpp_trading_runtime PRIVATE include)
target_compile_features(cpp_trading_runtime PRIVATE cxx_std_20)
target_compile_options(cpp_trading_runtime PRIVATE -Wall -Wextra -pedantic)
