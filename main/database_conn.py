from typing import Text
from peewee import *
from web3.auto import w3

CryptoDB = SqliteDatabase('/home/fourzd/CryptoDB/main/CryptoDB')

class ProccessedBlocks(Model):
    id = BigAutoField()
    number = IntegerField()
    

    class Meta:
        database = CryptoDB 
class EthContracts(Model):
    id = BigAutoField()
    smart_contract = TextField()


    class Meta:
        database = CryptoDB
class DBOrganization():
  
    def __init__(self):
        pass


    def initialize_db(self):
        CryptoDB.connect()
        CryptoDB.create_tables([ProccessedBlocks], safe = True)
        CryptoDB.create_tables([EthContracts], safe = True)
        CryptoDB.close()
    

    def default_block(self): #if there's no information in the DB, set a number of the last block
        try:
            ProccessedBlocks.get_by_id(1) != 0
        except DoesNotExist:
            default_block = ProccessedBlocks.insert(id=1, number=w3.eth.get_block('latest')['number']).execute()
        else:
            print('Block already exists')
            restart_call = input('Do you want to reset it to the last existing block? Y/n')
            if restart_call == 'Y':
                res = (ProccessedBlocks
                .update(number=w3.eth.get_block('latest')['number'])
                .where(ProccessedBlocks.id == '1')
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
