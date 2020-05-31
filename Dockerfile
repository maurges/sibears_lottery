FROM opensuse/leap:15.1

RUN zypper refresh && zypper install -y libQt5Network-devel libQt5Sql-devel gcc8-c++ make

RUN useradd -m lottery
ADD --chown=lottery:users \
    main.cpp Server.cpp Store.cpp StringGenerator.cpp \
    defines.h Server.h Store.h StringGenerator.h \
    Makefile oleg-service.pro \
    /home/lottery/

WORKDIR /home/lottery
RUN make
