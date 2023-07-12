from pymongo import MongoClient

# Administrative Actions

def get_asn(collection, ip):
    data = collection.find({"prefix/masks.ip":ip}, {"_id":0, "asn":1})
    all_asn = data[0]["asn"]
    

def get_prefixes(collection, asn):
    data = collection.find({"public_key":asn}, {"_id":0, "prefix/masks":1})
    all_prefixes = data[0]["prefix/masks"]
    prefixes = [prefix["ip"] for prefix in all_prefixes]
    return prefixes

def register_asn(collection, asn):
    pass

def register_prefixes(collection, asn, ip):
    pass

def remove_asn(collection, asn):
    pass

def remove_prefix(collection, asn, ip):
    pass

def request_contact(collection, ip):
    data = collection.find({"ip":ip})

def register_contact(collection, ip):
    pass

client = MongoClient('127.21.0.2', 27017, username='root', password='root')
db = client["my_database"]
collection = db["ASN"]

