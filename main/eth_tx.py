from concurrent.futures import ThreadPoolExecutor
from web3.auto import w3
from loguru import logger
from time import time
from hexbytes import HexBytes

class TxFromBlock:

    def __init__(self):
        self.payload = w3.eth.get_block('latest') #get raw information about the last eth_block
        self.tx_payload = set() #unique txs


    def get_tx_payload(self): # parsing TX addresses from block information and adds it to the set
        raw_tx_payload = self.payload['transactions'] 
        for elem in raw_tx_payload:
            self.tx_payload.add(HexBytes.hex(elem))
        return self.tx_payload



class TxChecker(ThreadPoolExecutor): #checks if tx is creating new contract and if so - adds it to the DB

    def __init__(self):
        self.checked_tx = []


    def check_tx(self):
        start_time = time()
        for tx in payload:
            try:
                tx_attributes = w3.eth.get_transaction_receipt(tx)
                if tx_attributes['contractAddress'] != None:
                    print('Found!', tx_attributes['contractAddress'])
                else:
                    print('Not creation tx, keep searching...', '\n', 'From:', tx_attributes['from'], 'To:', tx_attributes['to'])
            except Exception:
                print('Transaction not found!')
            
        print("--- %s seconds ---" % (time() - start_time))
        return self.checked_tx


get_tx = TxFromBlock()
payload = get_tx.get_tx_payload()
check_tx = TxChecker()
tx_pl = check_tx.check_tx()

logger.add("dev_logs", format="{time} {level} {message}") #just logs
logger.info(tx_pl) #just logs

