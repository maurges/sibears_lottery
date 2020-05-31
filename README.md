# Lottery
Sibears training service

The service is made up of a Qt C++ service and a python3 subservice.

## Authors

Service, checker, description: d86leader

Sploits: [Alamov Vldimir](https://github.com/RockThisParty), [Komarova Tatyana](https://github.com/alex8h)

## Requirements

- C++17 compiler (g++>=8.0, clang++>=8.0, g++=9.0 works)
- QtCore, QtNetwork, QtSql >= 5.9 (5.14 works)
- libQt5Sql5-mysql for QtSql
- python3>=3.6.10
- mysql-connector-python==8.0.18
- systemctl

## Setup

1. To build: run `make` to build c++ service in th `build` directory
3. To start: run helper service with cwd `./helper`, it uses the ssl keys located there
4. To check: run the checker with cwd `./checker`, it uses the ssl keys located there

Checker also will dump and read its database to and from CWD.

## Vulnerabilities

1. It is possible to accept a ticket exchange with a user who never invited you
   to exchange. Fix by reverting commit
   6f4209bbba2fc317f2a24dad29e36adb594257d4 (=

2. The admin password generator is deterministic, which means that as all teams
   start with the same password, it's possible to generate current password for
   any team. Fix by changing random generator to non-deterministic or at least
   unknown to other teams.

3. An off-by one vulnerability in ticket purchase allows you to overwrite
   `m_state` for current handler. Fix by being more careful with ticket.data
   index

### Exploits

[First sploit](./sploits/lottery_1.py)

[Second sploit](./sploits/lottery_2.py)

[Third sploit](./sploits/lottery_3.py)
