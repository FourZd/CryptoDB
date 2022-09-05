from sqlite3 import Timestamp
from web3.auto import w3
from loguru import logger
from time import time, sleep
from hexbytes import HexBytes
import psycopg2
import sys
import os
from web3 import Web3
from multiprocessing import Process
import numpy
import signal
from web3.middleware import geth_poa_middleware
import datetime

ETH = Web3.HTTPProvider('https://mainnet.infura.io/v3/6bc510d9c9664ba9bffd221e9dd7f666')
ETH_PROVIDER = Web3(ETH)

BSC = Web3.HTTPProvider('https://bsc-dataseed1.binance.org/')
BSC_PROVIDER = Web3(BSC)
BSC_PROVIDER.middleware_onion.inject(geth_poa_middleware, layer=0)

class Timeout(): #simply timeout class, its neccesary in the future code
  """Timeout class using ALARM signal"""
  class Timeout(Exception): pass


  def __init__(self, sec):
    self.sec = sec


  def __enter__(self):
    signal.signal(signal.SIGALRM, self.raise_timeout)
    signal.alarm(self.sec)


  def __exit__(self, *args):
    signal.alarm(0) # disable alarm


  def raise_timeout(self, *args):
    raise Timeout.Timeout()


class BlockProccessing: #  get TXs from the choosen block

    def __init__(self, provider): 
        self.provider = provider

    def get_tx_payload(self, current_block_number): # parsing TX addresses from block information and adds it to the set
        tx_payload = set() #set of unique transactions from the block
        get_block = self.provider.eth.get_block(current_block_number) #get all block info
        print('BlockProccessing №', current_block_number, 'info was successfully uploaded')
        raw_tx_payload = get_block['transactions'] #get transactions from all info payload
        for elem in raw_tx_payload:
            tx_payload.add(HexBytes.hex(elem)) #add tx to set
        return tx_payload #returning transactions


class TxCheck():

    def __init__(self, blockchain, provider):
        self.provider = provider
        self.blockchain = blockchain
        if self.blockchain == 'eth':
            self.blockchain_id = 1
        elif self.blockchain == 'bsc':
            self.blockchain_id = 2


    def server_call(self, tx_payload):
        for tx in tx_payload:
            try:
                try:
                    with Timeout(1):
                        tx_attributes = self.provider.eth.get_transaction_receipt(tx) #gets all info about transaction
                except Timeout.Timeout:
                    tx_attributes = self.provider.eth.get_transaction_receipt(tx) #if timeout bug, trying to get info again
                if tx_attributes['contractAddress'] != None: #contract creation transactions have contractAddress atr, so this is what we're looking for
                    print('Found!', tx_attributes['contractAddress'])
                    tx_info = {
                        'address': tx_attributes['contractAddress'],
                        'creator': tx_attributes['from'],
                        'block_number': tx_attributes['blockNumber'],
                        'creation_datetime': datetime.datetime.fromtimestamp(
                            self.provider.eth.get_block(tx_attributes['blockNumber'])['timestamp']),
                        'blockchain_id': self.blockchain_id
                    }
                    self.append_to_db(tx_info) 
                        
                #else:
                    print('Not creation tx, keep searching...', '\n', 'From:', tx_attributes['from'], 'To:', tx_attributes['to'])
            except Exception as e: 
                print(e, tx)
                print('Transaction not found!')
            

    def append_to_db(self, tx_info): #appending contract transactions to database
        conn = psycopg2.connect(database='webdb', user='fourzd', password='1234qwer',
                                  host='localhost', port=5432)
        cursor = conn.cursor()
        print(list(tx_info.values()))
        cursor.execute("""INSERT INTO cryptocurrencies_smartcontract (
                        address, creator, block_number, creation_datetime, blockchain_id)
                          VALUES(%s, %s, %s, %s, %s)""", (list(tx_info.values())))
        conn.commit()
        conn.close()


    def main(self, block_payload): #main script, creating 12 proccesses for fast-working(async doesnt work with web3 somewhy)
        proccesses = []
        start_time = time()
        l = numpy.array_split(numpy.array(block_payload), 6)
        for array in l:
            proc = Process(target=self.server_call, args=(array, ))
            proccesses.append(proc)
        for p in proccesses:
            try:
                p.start()
            except ValueError as ve:
                print('Theres a problem on server')
        for p in proccesses:
            p.join()
        work_time = "\n --- %s seconds ---" % (time() - start_time)
        print("--- %s seconds ---" % (time() - start_time))
        with open('time.txt', 'a', encoding='utf-8') as log:
            log.write(str(work_time))
            log.write(str(l))
        

class DBCommunnication(): 


    def __init__(self, blockchain, provider):
        self.provider = provider
        self.blockchain = blockchain
        if self.blockchain == 'eth':
            self.blockchain_id = 1
        elif self.blockchain == 'bsc':
            self.blockchain_id = 2

    def get_last_block(self): #getting last saved block from the database, if theres none - asking if user want to create default(last) value
        conn = psycopg2.connect(database='webdb', user='fourzd', password='1234qwer',
                                  host='localhost', port=5432)
        cursor = conn.cursor()
        try:
            cursor.execute(f'SELECT number FROM proccessedblocks WHERE blockchain = %s;', [self.blockchain, ])
            result = cursor.fetchone()
            conn.close()
            return result[0]
        except TypeError as e:
            print('It looks like you did not set neither desired block number nor default')
            choose_block_number = input('Do you want to do it now? Y/n')
            if choose_block_number == 'Y':
                desired_or_default = int(input('Do you want to set desired number, or set by default(last existing)? 1/2'))
                if desired_or_default == 1:
                    desired_number_set = int(input('Write the desired block number'))
                    change_number_to_desired = cursor.execute(
                        "INSERT INTO proccessedblocks (id, blockchain, number) VALUES(%s)", 
                        (self.blockchain_id, self.blockchain, desired_number_set,)
                        )
                    conn.commit()
                    conn.close()
                    print('Your number was successfully changed to desired:', desired_number_set)
                    return desired_number_set
                elif desired_or_default == 2:
                    print('Setting current block as default(last exists)')
                    default_block_num = self.provider.eth.get_block('latest')['number']
                    change_number_to_default = self.cursor.execute(
                        "INSERT INTO proccessedblocks (id, blockchain, number) VALUES(%s)", 
                        (self.blockchain_id, self.blockchain, default_block_num,)
                        )
                    conn.commit()
                    conn.close()
                    return default_block_num
                else:
                    raise Exception('Invalid input')
            elif choose_block_number == 'n':
                print('Accepted. Closing app...')
                sleep(3)
                sys.exit()
            else:
                raise Exception('Invalid input')


    def update_last_block(self, completed_block_number): #after one cycle, adding next block number to DB
        latest_block = self.provider.eth.get_block('latest')['number']
        if latest_block == completed_block_number:
            print('Completed last available block, waiting for next one...')
            while latest_block == completed_block_number:
                latest_block = self.provider.eth.get_block('latest')['number']
            print('New block was created, continuing...')
        next_block_number_to_use = completed_block_number + 1
        conn = psycopg2.connect(database='webdb', user='fourzd', password='1234qwer',
                                  host='localhost', port=5432)
        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE proccessedblocks SET number = %s WHERE blockchain = %s", (next_block_number_to_use, self.blockchain,))
        conn.commit()
        conn.close()
        print('Next block to use: №', next_block_number_to_use)

class MainProccess(): #just a starter for script cycle


    def __init__(self, blockchain, provider):
        self.dbcommunication = DBCommunnication(blockchain, provider)
        self.tx_from_block = BlockProccessing(provider)
        self.tx_checker = TxCheck(blockchain, provider)


    def start_work(self):
        while True:
            number_to_parse = self.dbcommunication.get_last_block() #last block number from DB
            self.tx_payload = list(self.tx_from_block.get_tx_payload(number_to_parse)) #parsing txs from block
            self.tx_checker.main(self.tx_payload) #checking if tx creates contract
            self.dbcommunication.update_last_block(number_to_parse) #adding next block to the DB



eth_main = MainProccess(blockchain = 'eth', provider = ETH_PROVIDER)
bsc_main = MainProccess(blockchain = 'bsc', provider = BSC_PROVIDER)
#tron_main = MainProccess()