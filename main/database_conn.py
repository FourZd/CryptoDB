from typing import Text
from peewee import *
from web3.auto import w3, Web3
from web3.middleware import geth_poa_middleware

BSC_PROVIDER = Web3.HTTPProvider('https://bsc-dataseed1.binance.org/')
W3_BSC = Web3(BSC_PROVIDER)
W3_BSC.middleware_onion.inject(geth_poa_middleware, layer=0)

ETH_PROVIDER = Web3.HTTPProvider('https://mainnet.infura.io/v3/6bc510d9c9664ba9bffd221e9dd7f666')
W3_ETH = Web3(ETH_PROVIDER)

webdb = PostgresqlDatabase('webdb', user='fourzd', password='1234qwer',
                              host='localhost', port=5432)

class ProccessedBlocks(Model):
    blockchain = TextField()
    number = IntegerField()
    
    class Meta:
        database = webdb


class DBOrganization():
  
    def __init__(self):
        pass
    def initialize_db(self):
        webdb.connect()
        webdb.create_tables([ProccessedBlocks], safe = True)
        webdb.close()
    def default_block(self): #if there's no information in the DB, set a number of the last block
        blockchains = [
            {'name': 'eth', 'id': 1, 'provider': W3_ETH}, 
            {'name': 'bsc', 'id': 2, 'provider': W3_BSC}
            ]
            
        for blockchain in blockchains:
            try:
                ProccessedBlocks.get_by_id(blockchain.get('id')) 
            except DoesNotExist:
                default_block = ProccessedBlocks.insert(blockchain = blockchain.get('name'),
                                number=blockchain.get('provider').eth.get_block('latest')['number']).execute()
            else:
                print('Block already exists')
                restart_call = input('Do you want to reset it to the last existing eth block? Y/n')
                if restart_call == 'Y':
                    res = (ProccessedBlocks
                    .update(number=blockchain.get('provider').eth.get_block('latest')['number'])
                    .where(ProccessedBlocks.blockchain == blockchain.get('name'))
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
