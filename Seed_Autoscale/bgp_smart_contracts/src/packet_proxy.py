from scapy.all import *
from scapy.contrib.bgp import *
from pymongo import MongoClient


def check_exists(asn, ip):
    # Create a MongoClient instance
    client = MongoClient('172.22.0.2', 27017, username='root', password='root')
    db = client.data.ROOT

    result = list(db.find({'prefix/masks.ip': ip}))

    is_found = False
    
    for entry in result:
        if entry["asn"] == asn:
            is_found = True
            break

    # Close the connection
    client.close()

    return is_found

# Iterate over the packets
def proxy(packet):
    if BGPUpdate in packet:
        counter = 0
        while True:
            bgp_update = packet.getlayer(counter)
            if bgp_update is None:
                break
            counter += 1

            try:
                path_attributes = bgp_update.path_attr
                for path_entry in path_attributes:
                    type_code = path_entry.type_code
                    if type_code == 2:
                        asn = path_entry.attribute.segments[0].segment_value[-1]
                        # print("Last Segment Value:", asn)
                
                for count, nlri in enumerate(bgp_update.nlri):
                    ip = str(nlri.prefix)
                    print(f"{asn} {ip}")
                    print(check_exists(asn, ip))
            except:
                return 0
            
# tcpdump -i any port 179 -w example.pcap
while True:
    sniff(prn=lambda x:x.proxy, filter="port 179")