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
import sys
import os
from aiohttp import ClientSession
from web3 import Web3, AsyncHTTPProvider
from web3.eth import AsyncEth
from web3.net import AsyncNet
from web3.geth import Geth, AsyncGethTxPool
from multiprocessing import Process
import numpy
import signal

#YOU HAVE TO CONNECT TO LIGHTNODE FIRST $geth --syncmode light
#IT WONT WORK OTHER WAY

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


class TxFromBlock: #  get TXs from the choosen block

    def __init__(self): 
        pass


    def get_tx_payload(self, current_block_number): # parsing TX addresses from block information and adds it to the set
        tx_payload = set() #set of unique transactions from the block
        current_block = w3.eth.get_block(current_block_number) #get all block info
        print('Transactions of block №', current_block_number, 'was successfully parsed')
        raw_tx_payload = current_block['transactions'] #get transactions from all info payload
        for elem in raw_tx_payload:
            tx_payload.add(HexBytes.hex(elem)) #add tx to set
        return tx_payload #returning transactions


class TxCheck():

    def __init__(self):
        pass


    def server_call(self, tx_payload):
        for tx in tx_payload:
            try:
                try:
                    with Timeout(1):
                        tx_attributes = w3.eth.get_transaction_receipt(tx) #gets all info about transaction
                except Timeout.Timeout:
                    tx_attributes = w3.eth.get_transaction_receipt(tx) #if timeout bug, trying to get info again
                if tx_attributes['contractAddress'] != None: #contract creation transactions have contractAddress atr, so this is what we're looking for
                    print('Found!', tx_attributes['contractAddress'])
                    self.append_to_db(tx_attributes['contractAddress']) 
                        
                else:
                    print('Not creation tx, keep searching...', '\n', 'From:', tx_attributes['from'], 'To:', tx_attributes['to'])
            except Exception as e: 
                print(e, tx)
                print('Transaction not found!')
            

    def append_to_db(self, tx): #appending contract transactions to database
        conn = sqlite3.connect(os.path.join(sys.path[0], 'CryptoDB'))
        cursor = conn.cursor()
        address = tx
        append = cursor.execute(f"INSERT INTO ethcontracts (smart_contract) VALUES(?)", (address,))
        conn.commit()


    def main(self, block_payload): #main script, creating 12 proccesses for fast-working(async doesnt work with web3 somewhy)
        proccesses = []
        start_time = time()
        l = numpy.array_split(numpy.array(block_payload), 12)
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


    def __init__(self):
        self.conn = sqlite3.connect(os.path.join(sys.path[0], 'CryptoDB'))
        self.cursor = self.conn.cursor()
    

    def get_last_block(self): #getting last saved block from the database, if theres none - asking if user want to create default(last) value
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


    def update_last_block(self, completed_block_number): #after one cycle, adding next block number to DB
        next_block_number_to_use = completed_block_number + 1
        change_number_to_default = self.cursor.execute(f"REPLACE INTO proccessedblocks values (1, {next_block_number_to_use})")
        self.conn.commit()
        print('Next block to use: №', next_block_number_to_use)

class MainProccess(): #just a starter for script cycle


    def __init__(self):
        self.dbcommunication = DBCommunnication()
        self.tx_from_block = TxFromBlock()
        self.tx_checker = TxCheck()
        self.number_to_parse = None
        self.tx_payload = None


    def start_work(self):
        while True: #theres no reason to stop this cycle
            self.number_to_parse = self.dbcommunication.get_last_block() #last block number from DB
            self.tx_payload = list(self.tx_from_block.get_tx_payload(self.number_to_parse)) #parsing txs from block
            self.tx_checker.main(self.tx_payload) #checking if tx creates contract
            self.dbcommunication.update_last_block(self.number_to_parse) #adding next block to the DB



main = MainProccess()
main.start_work()
