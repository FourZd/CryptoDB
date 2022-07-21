from concurrent.futures import ThreadPoolExecutor
from optparse import Values
from web3.auto import w3
from loguru import logger
from time import time, sleep
from hexbytes import HexBytes
import sqlite3
from peewee import *
import sys
import os
import asyncio

class TxFromBlock: #  get TXs from the choosen block

    def __init__(self, current_block_number):
        self.current_block_number = current_block_number #get raw information about the last eth_block
        self.tx_payload = set() #unique txs
        self.current_block = None

    def get_current_block(self):
        self.current_block = w3.eth.get_block(self.current_block_number)
    def get_tx_payload(self): # parsing TX addresses from block information and adds it to the set
        print('Transactions of block №', self.current_block_number, 'was successfully parsed')
        raw_tx_payload = self.current_block['transactions'] 
        for elem in raw_tx_payload:
            self.tx_payload.add(HexBytes.hex(elem))
        return self.tx_payload



class TxChecker(ThreadPoolExecutor): #checks if tx is creating new contract and if so - adds it to the DB

    def __init__(self):
        self.checked_tx = []


    def check_tx(self):
        start_time = time()
        for tx in current_block_number:
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
        self.new_block_id = w3.eth.get_block('latest')['number']


    def block_comparison(self, old_block):
        pass # COMPARE LAST PROCCESSED BLOCK AND MOST RECENT BLOCK
        #if self.new_block_id == CryptoDB.current_block_number():
            #return TxFromBlock(CryptoDB.current_block_number())
        #elif self.new_block_id > CryptoDB.current_block_number():
            #next_block = CryptoDB.last_block_numbяer() + 1
            #return next_block
       # if ProccessedBlocks.select().where(ProccessedBlocks.id == '0'): #if theres info in the DB
            #id = ProccessedBlocks.get(ProccessedBlocks.id == 0) 
            #id.delete_instance() 
            #export_info = ProccessedBlocks(number=w3.eth.get_block('latest')['number'])
            #export_info.save()
        #else:
            #raise Exception


class DBCommunnication():
    def __init__(self):
        self.conn = sqlite3.connect(os.path.join(sys.path[0], 'CryptoDB'))
        self.cursor = self.conn.cursor()
    
    def get_last_block(self):
        try:
            query = self.cursor.execute('SELECT number FROM proccessedblocks WHERE rowid == 1')
            result = query.fetchone()
            return result[0]
        except TypeError as e:
            print('It looks like you did not set neither desired block number nor default')
            choose_block_number = input('Do you want to do it now? Y/n')
            if choose_block_number == 'Y':
                desired_or_default = int(input('Do you want to set desired number, or set by default(last existing)? 1/2'))
                if desired_or_default == 1:
                    desired_number_set = int(input('Write the desired block number'))
                    change_number_to_desired = self.cursor.execute(f"INSERT INTO proccessedblocks values (1, {desired_number_set})")
                    self.conn.commit()
                    print('Your number was successfully changed to desired:', desired_number_set)
                    return desired_number_set
                elif desired_or_default == 2:
                    print('Setting current block as default(last exists)')
                    default_block_num = w3.eth.get_block('latest')['number']
                    change_number_to_default = self.cursor.execute(f"INSERT INTO proccessedblocks values (1, {default_block_num})")
                    self.conn.commit()
                    return default_block_num
                else:
                    raise Exception('Invalid input')
            elif choose_block_number == 'n':
                print('Accepted. Closing app...')
                sleep(3)
                sys.exit()
            else:
                raise Exception('Invalid input')

    def update_last_block(self, completed_block_number):
        next_block_number_to_use = completed_block_number + 1
        change_number_to_default = self.cursor.execute(f"REPLACE INTO proccessedblocks values (1, {next_block_number_to_use})")
        self.conn.commit()
        print('Next block to use: №', next_block_number_to_use)
db_communication = DBCommunnication()
number_to_parse = db_communication.get_last_block() # get number of block
get_tx = TxFromBlock(number_to_parse)
get_tx.get_current_block()
current_block_number = get_tx.get_tx_payload()
check_tx = TxChecker()
tx_pl = check_tx.check_tx()
db_communication.update_last_block(number_to_parse)
logger.add("dev_logs", format="{time} {level} {message}") #just logs
logger.info(tx_pl) #just logs

