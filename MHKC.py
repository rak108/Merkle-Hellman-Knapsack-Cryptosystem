from random import randint

class merklehellmanusers:

    def __init__(self, name):
        self.name = name
        self.w = []
        self.q = 0
        self.r = 0
        self.b = []
        self.maxcharacters = 200
        self.maxbinarylength = self.maxcharacters*8
        self.keygeneration()


    def keygeneration(self):
        maxnumberofbits = 50
        sum = 0
        for i in range(self.maxbinarylength):
            self.w.append(sum + randint(1,2**maxnumberofbits))
            sum += self.w[i]
        self.q = sum + randint(1,2**maxnumberofbits)
        self.r = self.q-1
        for i in range(self.maxbinarylength):
            self.b.append((self.w[i]*self.r)%self.q)

    def encryption(self, message):
        binarymessage = ""
        for letter in message:
              binarymessage += (bin(ord(letter)).lstrip("0b")).zfill(8)

        if len(binarymessage) < self.maxbinarylength:
              binarymessage = binarymessage.zfill(self.maxbinarylength)
  
        cipher = 0
        for i in range(0,len(binarymessage)):
            cipher += self.b[i]*int(binarymessage[i],2)
  
        return cipher


    def egcd(self,a, b):
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = self.egcd(b % a, a)
            return (g, x - (b // a) * y, y)

    def modinv(self,a, m):
        g, x, y = self.egcd(a, m)
        if g != 1:
            raise Exception('modular inverse does not exist')
        else:
            return (x%m + m) % m

    def decryption(self, cipher):
        plaintext = ""
        binarystring = ""
        cipherint = cipher
        modularinverse = self.modinv(self.r,self.q)
        inversecipher = (cipherint*modularinverse)%self.q
        for i in range(len(self.w)-1,-1,-1):
            if self.w[i] <= inversecipher:
                inversecipher -= self.w[i]
                binarystring += "1"
            else:
                binarystring += "0"

        binarystring = binarystring[::-1]
        for i in range (0,len(binarystring),8):
            letter = binarystring[i:i+8]
            check = int(letter,2)
            if check != 0:
                plaintext += chr(int(letter,2))
    
        return plaintext

def communication(user1,user2):
    choice = 0
    ciphertext_user1 = []
    ciphertext_user2 = []
    messages_user1 = []
    messages_user2 = []
    while(choice != 3):
        print("\n ----------------------------------------- MAIN MENU -------------------------------------------")
        ip1 = input("\n Choose one of the following options : \n 1. Log in as "+n1+"\n 2. Log in as "+n2+"\n 3. Exit \n\n >> ")
        try:
            choice = int(ip1)
        except:
            pass
        if(choice == 1):
            ans = 0
            print("\n Logged in as "+user1.name)
            while(ans != 3):
                ip2 = input("\n Choose one of the following options : \n 1. Send message to "+user2.name+".\n 2. Check messages. \n 3. Return to main menu. \n\n >> ")
                try:
                    ans = int(ip2)
                except:
                    pass
                if(ans == 1):
                    messages = input("\n Enter message: ")
                    cipher = user2.encryption(messages)
                    ciphertext_user1.append(cipher)
                    print("\n Message sent.")
                    print("\n Encrypted message sent :\n")
                    print(cipher)
                    
                elif(ans == 2):
                    if(ciphertext_user2):
                        for i in ciphertext_user2:
                            messages_user1.append(user1.decryption(i))
                        print("\nYou have received the following messages from "+ user2.name +" :\n")
                        for j in messages_user1:
                            print(j)
                    else:
                        print("\n No new messages received.")
                    messages_user1.clear()
                    ciphertext_user2.clear()
                elif(ans == 3):
                    print("\n Logged out from "+user1.name+".")
                else:
                    print("\nInvalid Choice.")
        elif(choice == 2):
            ans = 0
            print("\n Logged in as "+user2.name)
            while(ans != 3):
                ip2 = input("\n Choose one of the following options : \n 1. Send message to "+user1.name+".\n 2. Check messages. \n 3. Return to main menu. \n\n >> ")
                try:
                    ans = int(ip2)
                except:
                    pass
                if(ans == 1):
                    messages = input("\n Enter message: ")
                    cipher = user1.encryption(messages)
                    ciphertext_user2.append(user1.encryption(messages))
                    print("\n Message sent.")
                    print("\n Encrypted message sent :\n")
                    print(cipher)
                elif(ans == 2):
                    if(ciphertext_user1):
                        for i in ciphertext_user1:
                            messages_user2.append(user2.decryption(i))
                        print("\nYou have received the following messages from " + user1.name + " :\n")
                        for j in messages_user2:
                            print(j)
                    else:
                        print("No new messages received.")
                    messages_user2.clear()
                    ciphertext_user1.clear()
                elif(ans == 3):
                    print("\n Logged out from "+user2.name+".")
                else:
                    print("\nInvalid choice.")
                    
        elif(choice==  3):
            print("\n\n Goodbye!")
        else:
            print("\nInvalid Choice.")
            
            

if __name__ == "__main__":
     
    n1 = input("\n Enter the name of the first user : ")
    user1 = merklehellmanusers(n1)

    n2 = input("\n Enter the name of the second user : ")
    user2 = merklehellmanusers(n2)

    communication(user1,user2)
