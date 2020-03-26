#include <QCoreApplication>

#include "Server.h"
#include "Store.h"

auto main(int argc, char *argv[]) -> int
{
    auto app = QCoreApplication(argc, argv);

    Ticket::qtRegister();
    store::initDb("192.168.56.1");

    auto server = Server();
    constexpr qint16 Port = 2339;
    server.listen(QHostAddress::Any, Port);

    return app.exec();
}
