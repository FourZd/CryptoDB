
from concurrent.futures import ThreadPoolExecutor
from optparse import Values
from web3.auto import w3
from web3.eth import (
    AsyncEth,
)
from loguru import logger
from time import time, sleep
from hexbytes import HexBytes
import sqlite3
from peewee import *
import sys
import os
import asyncio
from aiohttp import ClientSession
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from web3.net import AsyncNet
from web3.geth import Geth, AsyncGethTxPool



class AsyncConnect(AsyncHTTPProvider):
    def __init__(self):
        pass
    async def start_connection(self):
        w3 = Web3(
        AsyncHTTPProvider(endpoint_uri),
        modules={'eth': (AsyncEth,),
            'net': (AsyncNet,),
            'geth': (Geth,
                {'txpool': (AsyncGethTxPool,),
                'personal': (AsyncGethPersonal,),
                'admin' : (AsyncGethAdmin,)})},
        middlewares=[]   # See supported middleware section below for middleware options
        )
        custom_session = ClientSession()  # If you want to pass in your own session
        await w3.provider.cache_async_session(custom_session) 
class TxFromBlock: #  get TXs from the choosen block

    def __init__(self, current_block_number):
        self.current_block_number = current_block_number #get raw information about the last eth_block
        self.tx_payload = set() #unique txs
        self.current_block = None

    def get_tx_payload(self): # parsing TX addresses from block information and adds it to the set
        self.current_block = w3.eth.get_block(self.current_block_number)
        print('Transactions of block №', self.current_block_number, 'was successfully parsed')
        raw_tx_payload = self.current_block['transactions'] 
        for elem in raw_tx_payload:
            self.tx_payload.add(HexBytes.hex(elem))
        return self.tx_payload



class AsyncProccess():
    def __init__(self):
        self.count = 0

    async def server_call(self, tx):

        self.count += 1
        print('Tx No', self.count)
        try:
            tx_attributes = await w3.eth.get_transaction_receipt(tx)
            
            if tx_attributes['contractAddress'] != None:
                print('Found!', tx_attributes['contractAddress'])
            else:
                print('Not creation tx, keep searching...', '\n', 'From:', tx_attributes['from'], 'To:', tx_attributes['to'])

        except Exception as e:
            print(e)
            print('Transaction not found!')

            
    async def run_tasks(self, block_payload):
        
        tasks = [self.server_call(tx) for tx in block_payload]
        asyncio.gather(*tasks)
        
    def main(self, block_payload):
        asyncio.run(self.run_tasks(block_payload))
        

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
current_block_number = get_tx.get_tx_payload()
async_proc = AsyncProccess()
start_time = time()
print("--- %s seconds ---" % (time() - start_time))
async_proc.main(current_block_number)
print('GOVNO')
db_communication.update_last_block(number_to_parse)
logger.add("dev_logs", format="{time} {level} {message}") #just logs
