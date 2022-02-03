from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import re

clients = {}
addresses = {}

MAX_CONNECTIONS = 2
HOST = "127.0.0.1"
PORT = 5000
BUFSIZ = 1024
ADDR = (HOST, PORT)
SOCK = socket(AF_INET, SOCK_STREAM)
SOCK.bind(ADDR)


def accept_incoming_connections():
    while True:
        client, client_address = SOCK.accept()
        if len(clients) >= MAX_CONNECTIONS:
            client.send("Connection overflow. Max amount is {MAX_CONNECTIONS}".encode())
            client.close()
            continue
        print("%s:%s has connected." % client_address)
        client.send("Greetings! ".encode("utf8"))
        client.send("Now type your name and press enter!".encode("utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client, client_address)).start()


def handle_client(conn, addr):
    name = conn.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type #quit to exit.' % name
    conn.sendall(bytes(welcome, "utf8"))
    msg = "%s from [%s] has joined the chat!" % (name, "{}:{}".format(addr[0], addr[1]))
    broadcast(bytes(msg, "utf8"))
    clients[conn] = name
    if (len(clients) == MAX_CONNECTIONS):
        broadcast(bytes("!mhkc#", "utf8"))
    while True:
        msg = conn.recv(BUFSIZ)
        if msg.decode("utf8").split()[0] == "!mhkcs#":
            msg = msg.decode("utf8")
            message = ""
            while True:
                message += msg
                if message[-1]=="@":
                    message=message[:-1]
                    break
                msg = conn.recv(BUFSIZ).decode("utf8")
            exchangekeys(conn, message+"@")
        elif msg != bytes("#quit", "utf8"):
            sendmessage(conn, msg, name + ":-- ")
        else:
            conn.close()
            del clients[conn]
            print("%s:%s has disconnected." % addresses[conn])
            del addresses[conn]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            break


def sendmessage(cli, msg, prefix=""):
    for sock in clients:
        if not cli == sock:
            sock.send(bytes(prefix, "utf8") + msg)

def broadcast(msg, prefix=""):
    for sock in clients:
        sock.sendall(bytes(prefix, "utf8") + msg)

def exchangekeys(cli, sendmsg):
    for sock in clients:
        if not cli == sock:
                x = 0
                bytesmsg = bytes(sendmsg, "utf8")
                while True:
                    y = x+BUFSIZ
                    if (y>len(bytesmsg)):
                        y = len(bytesmsg)
                    blockdata = bytesmsg[x:y]
                    sock.sendall(blockdata)
                    if (y==len(bytesmsg)):
                        break                    
                    x = y         


if __name__ == "__main__":
    SOCK.listen(5) 
    print("Chat Server has Started !!")
    print("Waiting for connections...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SOCK.close()