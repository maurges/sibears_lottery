#include <QCoreApplication>

#include "Server.h"
#include "Store.h"
#include "StringGenerator.h"
#include "defines.h"

auto main(int argc, char *argv[]) -> int
{
    auto app = QCoreApplication(argc, argv);

    auto str = QString("ZVwXtuORgXLfaLtBIqqDwCuD4MthWHTS");
    qDebug() << str;
    for (int i = 0; i < 10; ++i) {
        auto gen = StringGenerator(str);
        str = gen.generate(str.length());
        qDebug() << str;
    }

//    Ticket::qtRegister();
//    store::initDb("192.168.56.1");
//
//    auto server = Server();
//    constexpr qint16 Port = 2339;
//    server.listen(QHostAddress::Any, Port);

    return app.exec();
}