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
	print(user_list)

	for user in user_list:
		sock.send(b"accept\n")
		sock.recv(100500)
		sock.send(user.encode())
		sock.recv(100500)
		sock.send(b"y\n")
		sock.recv(100500)
		sock.send(b'show\n')
		data = sock.recv(100500)
		print(data.decode())
	sock.close()