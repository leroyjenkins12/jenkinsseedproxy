import pymongo
from Utils.Utils import *
from ipaddress import IPv4Address


client = pymongo.MongoClient('10.3.0.3', 27017)
db = client["bgp_db"]
collection = db["known_bgp"]

def db_validate(segment, tx_sender):

    inIP = IPv4Address(segment[1])
    inSubnet = int(segment[2])
    inASN = int(segment[0])

    print ("Validating segment: AS" + str(inASN)+ " , " + str(inIP) + "/" + str(inSubnet))
    
    tx_sender.generate_transaction_object("IANA", "IANA_CONTRACT_ADDRESS")
    # print("Transaction setup complete for: " + tx_sender_name)
    
    ret = collection.find({'containers.labels.net_0_address': inIP + "/" + inSubnet},
                          {{'containers.labels.asn':1,'_id':0}})
    if ret.count() == 0:
        return (validatePrefixResult.prefixNotRegistered)
    elif ret == tx_sender.getASN: #bettter approach
        return (validatePrefixResult.prefixValid)
    else:
        return (validatePrefixResult.prefixOwnersDoNotMatch)
