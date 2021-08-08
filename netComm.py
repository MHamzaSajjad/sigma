import socket
from threading import Thread
import random
import rsa
import json
import blockchain
import pickle



class Client:

    def __init__(self, pubKey, PrivKey):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(None)
        self.port = random.randint(10000, 40000)
        self.sock.bind(('', self.port))
        self.public_key = pubKey
        self.private_key = PrivKey
        self.money = 50

    def del_from_file(self, itemName, quantity): #add new item or decrease old items quantity and write back updated dictionary
        items_loaded = self.load_store()

        if(itemName in items_loaded):
            temp_tup = items_loaded[itemName]

            final_quantity = int(temp_tup[1]) - int(quantity)
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

    def get_money_from_chain(self, pubKey):
        # bc_file = open("blockchain.txt", "rb")
        # chain = blockchain.Blockchain(4, "")
        # chain = pickle.load(bc_file)
        # bc_file.close()
        chain = blockchain.open_chain_from_file()
        if chain.is_chain_valid():
            for block in chain:
                transact = block.data.split()
                if pubKey == transact[0]: #if sender
                    self.money -= int(transact[2])
                elif pubkey == transact[1]: #if receiver
                    self.money += int(transact[2])
            





    def menu(self):

        while True:

            print('\nEnter 1 to see items available\nEnter 2 to sell an item\nEnter 3 to buy an item\nEnter 4 to print blockchain\nEnter 5 to quit\n')

            option = int(input())

            if(option == 1): #displays all the items in the Store.txt file
                file = open("Store.txt", "r")

                item_info = file.read()  #reads dictionary of format {itemName:(publicKey, quantity, price) ...}

                item_info = json.loads(item_info)

                for key in item_info.keys():
                    tup = item_info[key]
                    print("Item name:", key, "\nquantity available:", tup[1], "\nprice:", tup[2], "\nseller public key:", tup[0])

                print("")
            
            elif(option == 2): #adds to the Store.txt file assuming two people don't sell same item

                item = input("Enter the item name: ")
                price = input("Enter item price: ")
                quantity = input("Enter item quantity: ")

                items_loaded = self.load_store()

                if item in items_loaded: #if already exists only increase quantity
                    temp_tup = items_loaded[item]

                    items_loaded[item] = (temp_tup[0], int(temp_tup[1]) + int(quantity), temp_tup[2])

                else: #if doesn't exists create entry
                    items_loaded[item] = ((self.public_key.n, self.public_key.e), quantity, price)

                store = open("Store.txt", "w")
                store.write(json.dumps(items_loaded))
                store.close()


            
            elif(option == 3): #tells the seller of the transaction and adds it to the currently unconfirmed transactions list
                

                item = input("Enter item you want to buy: ")
                quantity = input("Enter the quantity: ")

                items_loaded = self.load_store()

                if(not(item in items_loaded)): #if item does not exists
                    print("That item is not found\n")
                    continue

                temp_tup = items_loaded[item]

                item_price = int(temp_tup[2])
                item_quantity = int(temp_tup[1])

                self.get_money_from_chain(str((self.public_key.n, self.public_key.e)))
                money_in_wallet = self.money

                if int(quantity) > int(item_quantity):
                    print("Not enough product in stock.")
                    continue

                if(int(money_in_wallet) >= (int(item_price) * int(quantity))):
                    #tell the seller you want to buy
                    keys_loaded = self.load_keys()

                    port_to_send = None

                    for key in keys_loaded.keys():
                        if (keys_loaded[key] == items_loaded[item][0]):
                            port_to_send = key
                            break

                    message = "buy|" + str(item) + "|" + str(quantity)
                    message = message.encode("utf-8")
                    signature = rsa.sign(message, self.private_key, "SHA-1")

                    self.sock.sendto(message + "|".encode("utf-8")+ signature, ("localhost", int(port_to_send)))
                    
                    #receive confirmation from seller

                    #both use each other's public keys decode a message sent with private key to confirm identity



                    #update blockchain file
                    chain = blockchain.open_chain_from_file()

                    chain.add_block(blockchain.Block(str((self.public_key.n, self.public_key.e)) + " " + str(temp_tup[0]) + " " + str((item_price * quantity)), chain.get_latest_block().hash)) #add transaction in one block and add to blockchain after mining / showing proof of work
                    #transaction format: sender receiver amount

                    chain.store_chain_in_file()
                    

                    self.del_from_file(item, quantity) #update item's quantity in store
                    
                
                else:
                    print("Not enough tokens in wallet to buy", quantity, item)
            elif(option == 4):
                chain = blockchain.open_chain_from_file()
                chain.print_chain()
            elif(option == 5):
                break
            else:
                print("Invalid option.")


    def receive_handler(self):
        '''
        Waits for a message and deals with it
        '''
        while True:

            dataString, address = self.sock.recvfrom(4096)

            print(dataString.decode("utf-8"))


if __name__ == "__main__":

    
    # creats public private key pairs
    # and adds the public key to the open list in keys.txt

    (pubkey, privkey) = rsa.newkeys(512)  #creates public private key pair
    user = Client(pubkey, privkey)

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
        exit()