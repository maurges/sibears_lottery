#include "defines.h"
#include "StringGenerator.h"


StringGenerator::StringGenerator(const QString& seed)
: m_dis ('0', 'z')
{
    reseed(seed);
}


void StringGenerator::reseed(const QString& str)
{
    for (let& unicode : str)
    {
        let mixer = m_dis(m_gen);
        let c = unicode.toLatin1();
        m_gen.seed(mixer + c);
    }
}


auto StringGenerator::generate(size_t length) -> QString
{
    auto str = QString();
    for (size_t i = 0; i < length; ++i)
    {
        str.append(m_dis(m_gen));
    }
    return str;
}
