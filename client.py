import tkinter
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
from math import gcd
import random
import re

def primRoots(modulo):
    required_set = {num for num in range(1, modulo) if gcd(num, modulo) == 1 }
    return [g for g in range(1, modulo) if required_set == {pow(g, powers, modulo) for powers in range(1, modulo)}]

def key_gen_npkc_mhkc(maxbinarylength):
    maxnumberofbits = 50
    sum = 0
    q = 2971 # Has to be greater than maxbinarylength

    primitive_roots = primRoots(q)
    alpha = random.choice(primitive_roots)

    m = len(primitive_roots)

    b = []

    for i in range(maxbinarylength):
        b.append(sum + random.randint(1,2**maxnumberofbits))
        sum += b[i]

    p = sum + 1

    while gcd(alpha,p)!=1:
        p+=1

    j = p % m
    w = b[j:j+m]

    x = []

    for i in w:
        x.append((alpha*i) % p)
    
    return m,p,w,b,q,alpha,x

def text_to_binary(message):
    binarymessage = ""
    for letter in message:
        binarymessage += (bin(ord(letter)).lstrip("0b")).zfill(8)
    if len(binarymessage) < 2160:
        binarymessage = binarymessage.zfill(2160)
    return binarymessage

def encryption(msg, m, x):
    message = text_to_binary(msg)
    i = 0
    index = 0
    result = 0
    cipher = []
    for i in range(0,len(message),m):
        temp = message[i:i+m]
        result = 0
        for j in range(len(x)):
            result += int(temp[j]) * x[j]
        cipher.append(result)

    ans = " ".join(str(ints) for ints in cipher)
    return ans

def binary_to_string(binarystring):
    plaintext = ""
    for i in range (0,len(binarystring),8):
        letter = binarystring[i:i+8]
        check = int(letter,2)
        if check != 0:
            plaintext += chr(check)
    return plaintext

def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = egcd(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return (x%m + m) % m

def decryption(c, p, alpha, m, w):
    cipher = c.split()
    for s in cipher:
        if not (s.isnumeric()):
            return c
    cipher = [int(x) for x in cipher if x.isnumeric()]
    modularinverse = modinv(alpha, p)
    binarystring = ""
    plaintext = ""
    for i in range(len(cipher)):
        inversecipher = (cipher[i] * modularinverse) % p
        binarystring = ""
        for i in range(len(w)-1,-1,-1):
            if w[i] <= inversecipher:
                inversecipher -= w[i]
                binarystring += "1"
            else:
                binarystring += "0"
        binarystring = binarystring[::-1]
        block = binary_to_string(binarystring)
        plaintext += block

    return plaintext

def receive():
    global keys, Name, user_pubkeys
    while True:
        try:
            msg = sock.recv(BUFSIZ).decode("utf8")
            mg = re.split(":-- ", msg)
            if len(mg)>1:
                msg = mg[1]
            if msg == "Greetings! Now type your name and press enter!":
                msg_list.insert(tkinter.END, msg)
                continue
            if msg == "!mhkc#":
                k = " ".join(str(ints) for ints in keys[6])
                m = str(keys[0])
                sendmsg = "!mhkcs# " + m + " " + k + "@"
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
                continue
            elif msg.split()[0] == "!mhkcs#":
                message = ""
                while True:
                    message += msg
                    if message[-1]=="@":
                        message=message[:-1]
                        break
                    msg = sock.recv(BUFSIZ).decode("utf8")
                msg = message
                m = msg.split()
                user_pubkeys[0] = int(m[1])
                sub = len(m[0]) + len(m[1]) + 2
                user_pubkeys[1] = (list(map(int,msg[sub:].split())))
                continue
            decmsg = decryption(msg, keys[1], keys[5], keys[0], keys[2])
            finalmsg = msg
            if len(mg)>1:
                    finalmsg = mg[0] + ": " + decmsg 
            msg_list.insert(tkinter.END, finalmsg)
        except OSError:
            break

def send(event=None):
    global keys, nameset, Name, user_pubkeys
    msg = my_msg.get()
    my_msg.set("")
    if msg == "#quit":
        sock.send(bytes(msg, "utf8"))
        sock.close()
        top.quit()
        return
    if not nameset:
        Name = msg
        nameset = True
        sock.send(bytes(msg, "utf8"))
        return
    encmsg = encryption(msg, user_pubkeys[0], user_pubkeys[1])
    sock.send(bytes(encmsg, "utf8"))
    msg_list.insert(tkinter.END, Name+ ": "+ msg)

def on_closing(event=None):
    my_msg.set("#quit")
    send()

top = tkinter.Tk()
top.title("Merkle Hellman Chat App")
messages_frame = tkinter.Frame(top)

my_msg = tkinter.StringVar()  # For the messages to be sent.
my_msg.set("")
scrollbar = tkinter.Scrollbar(messages_frame)  # To navigate through past messages.
msg_list = tkinter.Listbox(messages_frame, height=15, width=70, yscrollcommand=scrollbar.set)
scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
msg_list.pack(side=tkinter.LEFT, fill=tkinter.BOTH)
msg_list.pack()

messages_frame.pack()

button_label = tkinter.Label(top, text="Enter Message:")
button_label.pack()
entry_field = tkinter.Entry(top, textvariable=my_msg, foreground="Red")
entry_field.bind("<Return>", send)
entry_field.pack()
send_button = tkinter.Button(top, text="Send", command=send)
send_button.pack()

quit_button = tkinter.Button(top, text="Quit", command=on_closing)
quit_button.pack()

top.protocol("WM_DELETE_WINDOW", on_closing)

maxbinarylength = 2160
keys = key_gen_npkc_mhkc(maxbinarylength)
user_pubkeys = []
user_pubkeys.append(keys[0])
user_pubkeys.append(keys[6])
nameset = False
Name = ""

HOST = "127.0.0.1"
PORT = 5000
BUFSIZ = 1024
ADDR = (HOST, PORT)
sock = socket(AF_INET, SOCK_STREAM)
sock.connect(ADDR)

receive_thread = Thread(target=receive)
receive_thread.start()
tkinter.mainloop()  # Starts GUI execution.