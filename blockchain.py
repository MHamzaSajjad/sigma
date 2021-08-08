# You do NOT need to import any other libraries
import hashlib
from datetime import datetime
import time
import pickle

class Block:
    # The constructor initializes all the components of a block
    def __init__(self, data, previous_block_hash = '0'):
        self.timestamp = datetime.now().strftime("%d/%m/%Y") # Timestamps add a factor of verification when checking a block's validity
        self.nonce = 0 # This adds randomization to the mix when the block is mined
        self.data = data #1 block contains 1 transaction
        self.previous_block_hash = previous_block_hash
        self.hash = self.calculate_hash()

    # Returns the SHA256 hash of a concatenated string containing the nonce, timestamp, data and previous block's hash (in the same order). Remember to encoded
    # the string before hashing it!
    def calculate_hash(self):
        # YOUR CODE HERE
        concat_string = str(self.nonce) + self.timestamp + self.data + self.previous_block_hash #concatenating as given above
        hash_string = hashlib.sha256(concat_string.encode('utf-8')).hexdigest() #encoding the concatenating string in utf-8, then hashing it in sha256
        return hash_string

    # Requires a miner to provide a proof of work before they could modify the blockchain
    def mine_block(self, difficulty):
        # YOUR CODE HERE
        check = False
        while not check: #loop will keep running until 'proof of work' is fulfilled (number of zeroes at start == difficulty)
            num_zeroes_start = 0
            for i in range(difficulty): #checking if the first difficulty number of characters in hash string are zeroes or not
                if(self.hash[i] == '0'):
                    num_zeroes_start += 1
                else:
                    break
            if(num_zeroes_start == difficulty): #if number of zeroes at start are equal to difficulty, okay, else generate hash again and check again
                check = True
            else:
                self.nonce += 1 #increment nonce
                self.hash = self.calculate_hash() #calculate hash again (mining)

def open_chain_from_file():
    file = open("blockchain.txt", "r")
    i = 0
    chain = Blockchain(1, "")
    for line in file.readlines():
        line = line.rstrip('\n')
        if i == 0:
            diff = int(line)
            chain.difficulty = diff
            i += 1
        else:
            line = line[1:-2]
            var_list = line.split()
            

            new_block = Block(var_list[2], var_list[3])
            new_block.timestamp = var_list[0]
            new_block.nonce = int(var_list[1])
            new_block.hash = var_list[4]
            chain.add_block(new_block)
    return chain


class Blockchain:
    # The constructor initializes a chain containing just the genesis block
    def __init__(self, difficulty, genesis_block_data):
        self.difficulty = difficulty
        self.chain = [self.create_genesis_block(genesis_block_data)]

    # Initializes and returns the first block in a chain
    def create_genesis_block(self, data):
        # YOUR CODE HERE
        genesis_block = Block(data) #initialise genesis block, default value of previous block hash already set to ''
        return genesis_block

    # Adds a new block to the end of the chain. Remember blocks need to be mined before they can be added!
    def add_block(self, block):
        # YOUR CODE HERE
        block.mine_block(self.difficulty) #mine the block to see if proof of work is provided
        self.chain.append(block) #then append to the blockchain once its mined successfully (according to given difficulty)

    # Returns the block that was most recently added
    def get_latest_block(self):
        # YOUR CODE HERE
        return self.chain[-1] #-1 index gives the last block in the list (latest added block)

    # Returns a bool which indicates whether the chain is still valid or have been tampered with
    def is_chain_valid(self):
        # YOUR CODE HERE
        genesis_block = self.chain[0] #getting first block from chain as genesis block
        calc_hash = genesis_block.calculate_hash() #checking genesis block's hash
        if(calc_hash != genesis_block.hash): #if calculated hash does not match stored hash, return False
            return False
        calc_prev_hash = calc_hash #storing in prev hash for next comparison
        for block in self.chain[1:]: #checking after genesis block
            calc_hash = block.calculate_hash() #checking each block's hash
            if(calc_hash != block.hash):  #if calculated hash does not match stored hash, return False
                return False
            if(calc_prev_hash != block.previous_block_hash): #checking each block's stored previous block hash with calculated previous block hash
                return False
            calc_prev_hash = calc_hash #storing in prev hash for next comparison (in next iteration)
        return True


    # Prints the data and hashes of each block in the chain
    def print_chain(self):
        # YOUR CODE HERE
        for block in self.chain:
            print("Data:", block.data, "Hash:", block.hash) #printing data and hash of each block in the block chain in a loop
            print()

    def store_chain_in_file(self):
        file = open("blockchain.txt", "w")
        file.write(str(self.difficulty))
        file.write("\n")
        for block in self.chain:
            file.write(str(block.timestamp) + " " + str(block.nonce) + " " + str(block.data) + " " + str(block.previous_block_hash) + " " + str(block.hash))
            file.write("\n")
        file.close()

    


if __name__ == "__main__":

    difficulty = 4
    chain = Blockchain(difficulty, "0")
    chain.store_chain_in_file()