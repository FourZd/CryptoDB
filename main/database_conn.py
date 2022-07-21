from peewee import *
from eth_tx import *

CryptoDB = SqliteDatabase('/home/fourzd/CryptoDB/main/CryptoDB')

class ProccessedBlocks(Model):
    number = IntegerField()

    class Meta:
        database = CryptoDB 

class DBase():
  
    def __init__(self):
        pass

    def initialize_db(self):
        CryptoDB.connect()
        CryptoDB.create_tables([ProccessedBlocks], safe = True)
        CryptoDB.close()
    

    def replace_block(self):
        id = ProccessedBlocks.get(ProccessedBlocks.id == 1)
        id.delete_instance() 
        export_info = ProccessedBlocks(number=f'{eth_tx.get_tx.block_id}')
        export_info.save()

    
    def last_block_number(self):
        import_info = ProccessedBlocks.get_by_id(1)
        return import_info


crypto_db = DBase()
crypto_db.initialize_db()
crypto_db.replace_block()
crypto_db.last_block_number()


