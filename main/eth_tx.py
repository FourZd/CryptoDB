from concurrent.futures import ThreadPoolExecutor
from optparse import Values
from web3.auto import w3
from loguru import logger
from time import time
from hexbytes import HexBytes
import sqlite3
from database_conn import *


class TxFromBlock:

    def __init__(self, payload):
        self.payload = payload #get raw information about the last eth_block
        self.block_id = self.payload['number']
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


class RelevanceCheck():

    def __init__(self):
        self.new_block = w3.eth.get_block('latest')
        self.new_block_id = self.new_block['number']


    def block_comparison(self, old_block): # COMPARE LAST PROCCESSED BLOCK AND MOST RECENT BLOCK
        if self.new_block_id == CryptoDB.last_block_number():
            return TxFromBlock(CryptoDB.last_block_number())
        elif self.new_block_id > CryptoDB.last_block_number():
            next_block = CryptoDB.last_block_number() + 1
            return next_block
        else:
            raise Exception

def get_last_block():
    last_block = w3.eth.get_block('latest')
    return last_block


get_tx = TxFromBlock(get_last_block())
payload = get_tx.get_tx_payload()
check_tx = TxChecker()
tx_pl = check_tx.check_tx()

logger.add("dev_logs", format="{time} {level} {message}") #just logs
logger.info(tx_pl) #just logs

