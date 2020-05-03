#include <iostream>
#include <random>
#include <ctime>
#include <string>
#define let auto

using fi32 = std::uint_fast32_t;

using namespace std;
mt19937 m_gen;
uniform_int_distribution<uint_fast32_t> m_dis('0', 'z');

void reseed(string str)
{
    for (int i=0;i<32;i++)
    {
            let mixer = m_dis(m_gen);
            cout << "mixer: " << mixer << endl;
            let c = str[i];
            //cout << "c:" << c << endl;
            m_gen.seed(mixer + c);
            //cout << "m_gen:" << m_gen << endl;
    }
}

auto generate(size_t length)
{
    string str;
    for (size_t i = 0; i < length; ++i)
    {
            let c = static_cast<unsigned char>(m_dis(m_gen));
            str += c;
    }
    return str;
}

int main()
{
    //cout << "m_gen:" << m_gen << endl;
    reseed("ZVwXtuORgXLfaLtBIqqDwCuD4MthWHTS");
    //cout << "m_gen1:" << m_gen << endl;
    //m_gen.seed('ZVwXtuORgXLfaLtBIqqDwCuD4MthWHTS');
    cout << "My number: " << generate(32) << endl;
}