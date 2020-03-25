#include <QCoreApplication>

#include "Server.h"
#include "Store.h"

auto main(int argc, char *argv[]) -> int
{
    QCoreApplication a(argc, argv);

    Ticket::qtRegister();
    store::initDb();

    auto server = Server();
    constexpr qint16 Port = 2339;
    server.listen(QHostAddress::Any, Port);

    return a.exec();
}

