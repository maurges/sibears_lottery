#!/usr/bin/env python3
import asyncio
import concurrent.futures
import os.path
import pickle
import random
import string
import sys
import timeit
from asyncio import open_connection, get_event_loop, StreamReader, StreamWriter
from traceback import TracebackException
from typing import Optional, NoReturn, Dict, Tuple, Set

OK, CORRUPT, MUMBLE, DOWN, CHECKER_ERROR = 101, 102, 103, 104, 110
PORT = 2339


def verdict(exit_code: int, public: str = "", private: str = "") -> NoReturn:
    if len(public) > 0:
        print(public)
    if len(private) > 0:
        print(private, file=sys.stderr)
    sys.exit(exit_code)

def verdict_ok() -> NoReturn:
    verdict(OK)
def corrupt(details: str) -> NoReturn:
    verdict(CORRUPT, "Corrupt", details)
def mumble(details: str) -> NoReturn:
    verdict(MUMBLE, "Mumble", details)
def down(details: str) -> NoReturn:
    verdict(DOWN, "Down", details)


def rand_string(length: int = 16) -> bytes:
    letters = string.ascii_letters + string.digits
    name = "".join(random.choice(letters) for _ in range(length))
    return name.encode()

class Storage:
    users: Dict[bytes, bytes]
    used_flags: Set[str]
    admin_password: bytes
    store_path: str
    def __init__(self, path: str) -> None:
        self.store_path = path
        # default values
        self.users = {}
        self.used_flags = set()
        self.admin_password = b"ZVwXtuORgXLfaLtBIqqDwCuD4MthWHTS"
    def dump(self) -> None:
        with open(self.store_path, "wb") as f:
            pickle.dump(self, f)
    @staticmethod
    def load(path: str) -> 'Storage':
        if os.path.isfile(path):
            with open(path, "rb") as f:
                store = pickle.load(f)
                store.store_path = path
                return store
        else:
            default = Storage(path)
            default.dump()
            return default

async def timed(aw):
    return await asyncio.wait_for(aw, timeout=5.0)

admin_lock = asyncio.Lock()
exchange_lock = asyncio.Lock()

async def auth_user(store, name, pwd) -> Tuple[StreamReader, StreamWriter]:
    reader, writer = await open_connection(host, PORT)
    await timed(reader.readuntil(b": "))
    writer.write(name + b"\n")
    await timed(reader.readuntil(b": "))
    writer.write(pwd + b"\n")
    await timed(reader.readuntil(b"> "))
    store.users[name] = pwd

    store.dump()
    return (reader, writer)

async def auth_admin(store) -> Tuple[StreamReader, StreamWriter]:
    async with admin_lock:
        reader, writer = await open_connection(host, PORT)
        await timed(reader.readuntil(b": "))
        name, pwd = b"admin", store.admin_password
        writer.write(name + b"\n")
        await timed(reader.readuntil(b": "))
        writer.write(pwd + b"\n")
        new_pwd_str = await timed(reader.readline())

        if new_pwd_str == b"Incorrect password\n":
            mumble("Bad admin password")

        awaited_prefix = b"New password: '"
        awaited_suffix = b"'\n"
        good_response = (new_pwd_str.startswith(awaited_prefix) and
                         new_pwd_str.endswith(awaited_suffix))
        if not good_response:
            mumble(f"Can't login as admin, response: {new_pwd_str}")
        new_pwd = new_pwd_str[len(awaited_prefix) : -len(awaited_suffix)]
        store.admin_password = new_pwd
        store.dump()
    return (reader, writer)


async def check(store: Storage, host: str) -> NoReturn:
    if len(store.users) == 0:
        verdict_ok()

    async def check_admin_names() -> None:
        user = random.choice(list(store.users.keys()))
        reader, writer = await auth_admin(store)
        writer.write(b"name\n")
        await timed(reader.readuntil(b": "))
        writer.write(user + b"\n")
        resp = await timed(reader.readuntil(b"> "))
        if not resp.endswith(b"has won\n> "):
            mumble("Can't win user by name")

    async def check_show() -> None:
        user = random.choice(list(store.users.keys()))
        pwd = store.users[user]
        reader, writer = await auth_user(store, user, pwd)
        writer.write(b"show\n")
        await timed(reader.readuntil(b"> "))

    async def check_list() -> None:
        store_users = set(store.users.keys())
        user = random.choice(list(store.users.keys()))
        pwd = store.users[user]
        reader, writer = await auth_user(store, user, pwd)
        writer.write(b"list\n")
        resp = await timed(reader.readuntil(b"> "))
        quoted = resp.rstrip(b"> ").rstrip().split(b" ")
        names = list(x[1:-1] for x in quoted)
        if store_users.issubset(names):
            pass
        else:
            mumble(f"Missing registered users: {store_users} vs {names}")

    async def check_exchange() -> None:
        async with exchange_lock:
            user1 = random.choice(list(store.users.keys()))
            user2 = random.choice(list(store.users.keys()))
            pwd1, pwd2 = store.users[user1], store.users[user2]
            r1, w1 = await auth_user(store, user1, pwd1)
            r2, w2 = await auth_user(store, user2, pwd2)
            #
            w1.write(b"show\n")
            resp1 = await timed(r1.readuntil(b"> "))
            flag1 = resp1.rstrip(b"> ")
            w2.write(b"show\n")
            resp2 = await timed(r2.readuntil(b"> "))
            flag2 = resp2.rstrip(b"> ")
            #
            w1.write(b"exchange\n")
            await timed(r1.readuntil(b": "))
            w1.write(user2 + b"\n")
            await timed(r1.readline())
            w2.write(b"accept\n")
            await timed(r2.readuntil(b"trade: "))
            w2.write(user1 + b"\n")
            await timed(r2.readline())
            w2.write(b"y")
            await timed(r2.readline())
            #
            w1.write(b"show\n")
            resp1 = await timed(r1.readuntil(b"> "))
            new_flag1 = resp1.rstrip(b"> ")
            w2.write(b"show\n")
            resp2 = await timed(r2.readuntil(b"> "))
            new_flag2 = resp2.rstrip(b"> ")
            if flag1 == new_flag2 and flag2 == new_flag1:
                pass
            else:
                mumble("Couldn't exchange")

    actions = [check_admin_names, check_exchange, check_list, check_show]
    random.shuffle(actions)
    for action in actions:
        await action()
    # if none exited, all is good
    verdict_ok()

async def put_flag(store: Storage, host: str, flag_id: str, flag_data: str, vuln
        ) -> NoReturn:
    ticket = [str(byte) for byte in flag_data.encode()]
    assert len(ticket) == 32
    ticket_str = " ".join(ticket)

    name, pwd = rand_string(), rand_string()
    reader, writer = await auth_user(store, name, pwd)

    writer.write(b"buy\n")
    await timed(reader.readuntil(b": "))
    writer.write(ticket_str.encode() + b"\n")
    await timed(reader.readuntil(b"> "))

    writer.write(b"show\n")
    data = await timed(reader.readuntil(b"> "))
    put_flag = data[2:34].decode()
    if put_flag == flag_data:
        store.used_flags.add(put_flag)
        store.dump()
        verdict_ok()
    else:
        mumble(f"Bad flag: {put_flag}")

async def get_flag(store: Storage, host: str, flag_id: str, flag_data: str, vuln
        ) -> NoReturn:
    reader, writer = await auth_admin(store)
    writer.write(b"number\n")
    await timed(reader.readuntil(b": "))
    writer.write(flag_data.encode() + b"\n")
    resp = await timed(reader.readline())
    postfix = b" has won, yay\n"
    if not resp.endswith(postfix):
        corrupt(f"Flag {flag_data} doesn't exist or malformed reply: {resp!r}")

    # check for non-existing flag
    flag = rand_string(32)
    while rand_string in store.used_flags:
        flag = rand_string(32)
    writer.write(b"number\n")
    await timed(reader.readuntil(b": "))
    writer.write(flag + b"\n")
    resp = await timed(reader.readline())
    if not resp.startswith(b"Ticket does not exist"):
        mumble("Non-existant flag exists")
    else:
        verdict_ok()

async def stress_test(store: Storage, host: str) -> NoReturn:
    real_exit = sys.exit
    def fake_exit(code: int) -> None:
        if code == OK:
            pass
        else:
            real_exit(code)
    sys.exit = fake_exit #type: ignore

    task_amount = random.randrange(100, 200)
    print(f"spawning {task_amount} workers")

    async def wrapped_get() -> None:
        flag = random.choice(list(store.used_flags))
        await get_flag(store, host, "", flag, None)
    async def wrapped_put() -> None:
        flag = rand_string(32).decode()
        await put_flag(store, host, "", flag, None)
    async def wrapped_check() -> None:
        await check(store, host)

    distr = [wrapped_get, wrapped_put, wrapped_check, wrapped_check, wrapped_check]
    tasks = [random.choice(distr)() for _ in range(task_amount)]
    start = timeit.default_timer()
    await asyncio.gather(*tasks)
    end = timeit.default_timer()
    sys.exit = real_exit
    print(f"all workers finished in {end - start} seconds")
    verdict_ok()


if __name__ == "__main__":
    try:
        command = sys.argv[1]
        host = sys.argv[2]

        dbname = f"storage-{host}-{PORT}.dump"
        store = Storage.load(dbname)
        loop = get_event_loop()

        if command == "check":
            loop.run_until_complete(check(store, host))

        elif command == "put":
            flag_id, flag_data, vuln = sys.argv[3:]
            loop.run_until_complete(put_flag(store, host, flag_id, flag_data, vuln))

        elif command == "get":
            flag_id, flag_data, vuln = sys.argv[3:]
            loop.run_until_complete(get_flag(store, host, flag_id, flag_data, vuln))

        elif command == "stresstest":
            loop.run_until_complete(stress_test(store, host))
            verdict_ok()

        else:
            verdict(CHECKER_ERROR, "Wrong action", "Wrong action: " + command)

    except IndexError as e:
        trace = "".join(TracebackException.from_exception(e).format())
        verdict(CHECKER_ERROR, "Not enough arguments", trace)
    except ValueError as e:
        trace = "".join(TracebackException.from_exception(e).format())
        verdict(CHECKER_ERROR, "Not enough arguments", trace)
    except ConnectionRefusedError as e:
        trace = "".join(TracebackException.from_exception(e).format())
        down(trace)
    except AssertionError as e:
        trace = "".join(TracebackException.from_exception(e).format())
        verdict(CHECKER_ERROR, "Bad parameters", trace)
    except concurrent.futures._base.TimeoutError as e:
        trace = "".join(TracebackException.from_exception(e).format())
        mumble(trace)
    except Exception as e:
        trace = "".join(TracebackException.from_exception(e).format())
        verdict(CHECKER_ERROR, "Other error", trace)

    verdict(CHECKER_ERROR, "Checker error (CE)", "No verdict")
