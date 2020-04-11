# Lottery
Sibears training service

The service is made up of a Qt C++ service and a python3 subservice.

## Authors

Service, checker, description: d86leader

## Requirements

- C++17 compiler (g++>=8.0, clang++>=8.0, g++=9.0 works)
- QtCore, QtNetwork, QtSql >= 5.9 (5.14 works)
- mysql>=15.1
- python3>=3.6.10
- python3-aiomysql=0.0.20
- systemctl

## Setup

1. Run `make` to build c++ service in th `build` directory
2. Create systemctl service named `lottery.service` with binary `build/oleg-service`
3. Run helper service as root with cwd `./helper`, it uses the ssl keys located there
4. Run the checker with cwd `./checker`, it uses the ssl keys located there

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

[First sploit](./sploits/lottery_1.py) Author [Alamov Vldimir](https://github.com/RockThisParty)
[Second sploit](./sploits/lottery_2.py) Author [Komarova Tatyana](https://github.com/alex8h)
