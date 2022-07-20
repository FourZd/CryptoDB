from peewee import *
from eth_tx import get_tx

CryptoDB = SqliteDatabase('/home/fourzd/CryptoDB/main/CryptoDB')

class ProccessedBlocks(Model):
    number = IntegerField()

    class Meta:
        database = CryptoDB 

class CryptoDB():
    
    def __init__(self):
        pass

    
    def initialize_db():
        CryptoDB.connect()
        CryptoDB.create_tables([ProccessedBlocks], safe = True)
        CryptoDB.close()
    

    def replace_block():
        id = ProccessedBlocks.get(ProccessedBlocks.id == 1)
        id.delete_instance() 
        export_info = ProccessedBlocks(number=f'{get_tx.block_id}')
        export_info.save()

    
    def last_block_number():
        import_info = ProccessedBlocks.get_by_id(1)
        return import_info


crypto_db = CryptoDB()
crypto_db.initialize_db()
crypto_db.replace_block()
crypto_db.last_block_number()


