#include <iostream>
#include "ql/quantlib.hpp"

int main() {
    using namespace QuantLib;
    auto date = Date(2, August, 2019);
    std::cout << date << '\n';
    return 0;
}
