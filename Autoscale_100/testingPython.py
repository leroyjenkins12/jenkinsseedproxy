from pymongo import MongoClient
# from random import randint
client = MongoClient('10.12.0.12', 27017)
# mydb = client["bgp_db"]

with open('testing123.txt', 'w') as dummy:
    dummy.write(client.list_database_names())
