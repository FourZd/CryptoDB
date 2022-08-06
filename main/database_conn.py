from typing import Text
from peewee import *
from web3.auto import w3, Web3
from web3.middleware import geth_poa_middleware

bsc_provider = Web3.HTTPProvider('https://bsc-dataseed1.binance.org/')
w3_bsc = Web3(bsc_provider)
w3_bsc.middleware_onion.inject(geth_poa_middleware, layer=0)

eth_provider = Web3.HTTPProvider('https://mainnet.infura.io/v3/6bc510d9c9664ba9bffd221e9dd7f666')
w3_eth = Web3(eth_provider)

CryptoDB = SqliteDatabase('/home/fourzd/CryptoDB/main/CryptoDB')

class ProccessedBlocks(Model):
    blockchain = TextField()
    number = IntegerField()
    

    class Meta:
        database = CryptoDB 


class SmartContracts(Model):
    id = BigAutoField()
    contract = TextField()
    blockchain = TextField()
    block_number = IntegerField()


    class Meta:
        database = CryptoDB


class DBOrganization():
  
    def __init__(self):
        pass


    def initialize_db(self):
        CryptoDB.connect()
        CryptoDB.create_tables([ProccessedBlocks], safe = True)
        CryptoDB.create_tables([SmartContracts], safe = True)
        CryptoDB.close()
    

    def default_block(self): #if there's no information in the DB, set a number of the last block
        #id 1 = ETH
        #id 2 = BSC
        try:
            ProccessedBlocks.get_by_id(1) 
        except DoesNotExist:
            default_block = ProccessedBlocks.insert(blockchain = 'eth', number=w3_eth.eth.get_block('latest')['number']).execute()
        else:
            print('Block already exists')
            restart_call = input('Do you want to reset it to the last existing eth block? Y/n')
            if restart_call == 'Y':
                res = (ProccessedBlocks
                .update(number=w3_eth.eth.get_block('latest')['number'])
                .where(ProccessedBlocks.blockchain == 'eth')
                .execute())
            elif restart_call == 'n':
                print('Restart call skipped')
            else:
                raise Exception('Wrong input')
        try:
            ProccessedBlocks.get_by_id(2)
        except DoesNotExist:
            default_block = ProccessedBlocks.insert(blockchain = 'bsc', number=w3_bsc.eth.get_block('latest')['number']).execute()
        else:
            print('Block already exists')
            restart_call = input('Do you want to reset it to the last existing bsc block? Y/n')
            if restart_call == 'Y':
                res = (ProccessedBlocks
                .update(number=w3_bsc.eth.get_block('latest')['number'])
                .where(ProccessedBlocks.blockchain == 'bsc')
                .execute())
            elif restart_call == 'n':
                print('Restart call skipped')
            else:
                raise Exception('Wrong input')
def start_db():
    crypto_db = DBOrganization()
    crypto_db.initialize_db()
    crypto_db.default_block()
start_db()
