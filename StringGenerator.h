#pragma once

#include <QString>
#include <random>

// Description: deterministic latin string generator

class StringGenerator
{
    // Lewis, Goodman, Miller parameters for base 256
    std::linear_congruential_engine<unsigned char, 167, 0, 255> m_gen;
    std::uniform_int_distribution<unsigned char> m_dis;

public:
    StringGenerator(const QString&);
    void reseed(const QString&);
    auto generate(size_t) -> QString;
};
