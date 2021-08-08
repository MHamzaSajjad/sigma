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

    def del_from_file(self, itemName, quantity): #add new item or decrease old items quantity and write back updated dictionary
        items_loaded = self.load_store()

        if(itemName in items_loaded):
            temp_tup = items_loaded[itemName]

            final_quantity = temp_tup[1] - quantity
            if(final_quantity <= 0):
                del items_loaded[itemName]

            else:
                items_loaded[itemName] = (temp_tup[0], final_quantity, temp_tup[2])
        
        string_to_write = json.dumps(items_loaded)

        file = open("Store.txt", "w")
        file.write(string_to_write)


    #reads dictionary of format {itemName:(publicKey, quantity, price) ...}
    def load_store(self): #used to load the dictionary in Store.txt
        file = open("Store.txt", "r")
        items = file.read()
        items = json.loads(items)

        return items

    #reads dictionary of format {portNumber:(N, E) ...}  
    def load_keys(self): #loads key dictionary for use
        file = open("keys.txt", "r")
        keys = file.read()
        keys = json.loads(keys)

        return keys


    def menu(self):

        while True:

            print('Enter 1 to see items available\nEnter 2 to sell an item\nEnter 3 to buy an item\n')

            option = int(input())

            if(option == 1): #displays all the items in the Store.txt file
                file = open("Store.txt", "r")

                item_info = file.read()  #reads dictionary of format {itemName:(publicKey, quantity, price) ...}

                item_info = json.loads(item_info)

                for key in item_info.keys():
                    tup = item_info[key]
                    print("Item name:", key, "quatity available:", tup[1], "price:", tup[2], "seller public key:", tup[0])

                print("")
            
            elif(option == 2): #adds to the Store.txt file assuming two people don't sell same item

                item = input("Enter the item name: ")
                price = input("Enter item price: ")
                quantity = input("Enter item quantity: ")

                items_loaded = self.load_store()

                if item in items_loaded: #if already exists only increase quantity
                    temp_tup = items_loaded[item]

                    items_loaded[item] = (temp_tup[0], temp_tup[1] + quantity, temp_tup[2])

                else: #if doesn't exists create entry
                    items_loaded[item] = ((self.public_key.n, self.public_key.e), quantity, price)



            
            elif(option == 3): #tells the seller of the transaction and adds it to the currently unconfirmed transactions list
                
                money_in_wallet = get_from_hash() #need to be added (optional idea)

                item = input("Enter item you want to buy: ")
                quantity = input("Enter the quantity: ")

                items_loaded = self.load_store()

                if(not(item in items_loaded)): #if item does not exists
                    print("That item is not found\n")
                    continue

                temp_tup = items_loaded[item]

                item_price = temp_tup[2]
                item_quantity = temp_tup[1]

                if(money_in_wallet >= (item_price * quantity)):
                    #tell the seller you want to buy
                    keys_loaded = self.load_keys()

                    port_to_send = None

                    for key in keys_loaded.keys():
                        if (keys_loaded[key] == items_loaded[item][0]):
                            port_to_send = key
                            break

                    message = "buy|" + item + "|" + quantity
                    message = message.encode("utf-8")
                    signature = rsa.sign(message, self.private_key, "SHA-1")

                    self.sock.sendto(message +"|".encode("utf-8")+signature, ("localhost", port_to_send))

                    #recieve confirmation from seller

                    #both use each other's public keys decode a message sent with private key to confirm identity

                    #create data struct for blockchain or add to unconfirm transactions

                    #add item to blockchain by itself or just wait for miner to do it

                    #message seller item was sold


    def receive_handler(self):
        '''
        Waits for a message and deals with it
        '''
        while True:

            dataString, address = self.sock.recvfrom(4096)

            recv_message = dataString.decode("utf-8")
            recv_message = recv_message.split("|")

            if(recv_message[0] == "buy"):
                print("Someone wants to buy", recv_message[2], recv_message[1])
                keys_loaded = self.load_keys()
                pubkey = rsa.PublicKey(keys_loaded[address[1]][0], keys_loaded[address[1]][1])

                m = recv_message[0] + "|" + recv_message[1] + "|" + recv_message[2]
                m = m.encode("utf-8")

                sig = recv_message[-1].encode("utf-8")

                if(rsa.verify(m, sig, pubkey) == "SHA-1"):
                    print("Buyer is authenticated")

                    msg = "sellerConf".encode("utf-8")

                    signature = rsa.sign(msg, self.private_key, "SHA-1")
                    self.sock.sendto(msg + "|".encode("utf-8")+signature, address)
                
                else:
                    print("Buyer was not authenticated")
                    continue

                
            elif(recv_message[0] == "sellerConf"): #do transactions
                keys_loaded = self.load_keys()

                pubkey = rsa.PublicKey(keys_loaded[address[1]][0], keys_loaded[address[1]][1])

                msg = recv_message[1].encode("utf-8")
                sig = recv_message[-1].encode("utf-8")

                if(rsa.verify(msg, sig, pubkey) == "SHA-1"):
                    print("seller verified")




if __name__ == "__main__":

    userName = input("Enter username: ")
    
    
    # creats public private key pairs
    # and adds the public key to the open list in keys.txt

    (pubkey, privkey) = rsa.newkeys(256)  #creates public private key pair
    user = Client(userName, pubkey, privkey)

    pubN = pubkey.n  #seperated as rsa.PublicKey is not JSON serialisable
    pubE = pubkey.e

    keys_loaded = user.load_keys()

    keys_loaded[user.port] = (pubN, pubE)

    file = open("keys.txt", "w")
    keys_string = json.dumps(keys_loaded)
    file.write(keys_string)
    file.close()

    #print(user.sock)
    try:
        # Start receiving Messages
        T = Thread(target=user.receive_handler)
        T.daemon = True
        T.start()
        # Start Client
        user.menu() #add
    except (KeyboardInterrupt, SystemExit):
        sys.exit()