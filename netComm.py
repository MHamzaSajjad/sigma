import socket
from threading import Thread
import random
import rsa
import json



class Client:

    def __init__(self, username, pubKey, PrivKey):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None)
        self.port = random.randint(10000, 40000)
        self.sock.bind(('', self.port))
        self.name = username
        self.public_key = pubKey
        self.private_key = PrivKey

    def menu(self):

        while True:

            print('Enter 1 to see items available\nEnter 2 to sell an item\nEnter 3 to buy an item\n')

            option = int(input())

            if(option == 1): #displays all the items in the Store.txt file
                file = open("Store.txt", "r")

                item_info = file.readline()

                while(item_info != ""):
                    print(item_info)

                    item_info = file.readline()
                
                file.close()

                print("")
            
            elif(option == 2): #adds to the Store.txt file

                item = input("Enter the item name: ")
                price = input("Enter item price: ")
                publicKey = input("Enter your public key")

                item_data = str(item) + " " + str(price) + " " + str(publicKey)

                file = open("Store.txt", "a")
                file.write(item_data)

                file.close()

            
            #elif(option == 3): #tells the seller of the transaction and adds it to the currently unconfirmed transactions list





    def receive_handler(self):
        '''
        Waits for a message and deals with it
        '''
        while True:

            dataString, address = self.sock.recvfrom(4096)

            print(dataString.decode("utf-8"))


if __name__ == "__main__":

    userName = input("Enter username: ")
    
    
    # creats public private key pairs
    # and adds the public key to the open list in keys.txt

    


    (pubkey, privkey) = rsa.newkeys(256)  #creates public private key pair
    user = Client(userName, pubkey, privkey)

    pubN = pubkey.n
    pubE = pubkey.e

    pubkey_add = str(pubN) + " " + str(pubE) + " " + user.port #saves public key and port to a file

    file = open("keys.txt", "a")
    file.write(str_pubkey)
    file.close()

    print(user.sock)
    try:
        # Start receiving Messages
        T = Thread(target=user.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        user.menu() #add
    except (KeyboardInterrupt, SystemExit):
        sys.exit()