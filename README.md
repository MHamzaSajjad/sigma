# Sigma

It has two script files netComm.py and blockchain.py. netComm.py is run by each client. It creates public and private key pairs for each and saves the public key with the address in keys.txt. The file Store.txt contains the items people want to sell. blockchain.py contains the functions for blockchain. If a client wants to sell something it will be added to the dictionary stored in the Store.txt file. Client and seller will exchange signatures to authenticate and then buyer will make the transaction.
