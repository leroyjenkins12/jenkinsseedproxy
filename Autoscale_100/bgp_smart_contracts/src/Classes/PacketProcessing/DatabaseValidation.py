import pymongo

client = pymongo.MongoClient('10.12.0.12', 27017)
db = client["bgp_db"]
collection = db["known_bgp"]
def db_validate(segment, txSender):
    ret = collection.find({'containers.labels.net_0_address': segment}, {'containers.labels.asn': 1})
    if ret.count() == 0:
        return 1
    elif ret == txSender:
        return 0
    else:
        return 2
