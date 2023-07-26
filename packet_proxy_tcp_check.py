from scapy.all import *
from scapy.contrib.bgp import *
from pymongo import MongoClient

#For packet resizing. Most current file to work on ao 26 Jul 2023
# Functionality uncertain

def check_exists(asn, ip):
    # Create a MongoClient instance
    client = MongoClient('10.100.0.0', 27017, username='root', password='root')
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
    pkt = IP(packet.get_payload())
    m_pkt = MutablePacket(pkt)

    print(packet.summary())
    print(m_pkt.show())
    if BGPUpdate in packet:
        seen = []
        counter = 0
        while True:
            bgp_update = packet.getlayer(counter)
            if bgp_update is None:
                # print("end of packet at", counter)
                break
            counter += 1

            try:
                if hasattr(bgp_update, 'path_attr'):
                    path_attributes = bgp_update.path_attr
                    # for path_entry in path_attributes:
                    #     type_code = path_entry.type_code
                    #     if type_code == 2:
                    #         asn = path_entry.attribute.segments[0].segment_value[-1]
                    #         for count, nlri in enumerate(bgp_update.nlri):
                    #             ip = str(nlri.prefix)
                    #             if ip in seen:
                    #                 print(f"On layer {counter} repeated: {asn} {ip}")
                    #             else:
                    #                 print(f"On layer {counter}: {asn} {ip}")
                    #                 seen.append(ip)
                    #             # print(check_exists(asn, ip))
                    #     else:e66aecc9db2b
                    #         print(f"On layer {counter}: Type code error: {type_code}")

                    path_entry = path_attributes[1]
                    type_code = path_entry.type_code
                    if type_code == 2:
                        asn = path_entry.attribute.segments[0].segment_value[-1]
                        for count, nlri in enumerate(bgp_update.nlri):
                            ip = str(nlri.prefix)
                            if ip in seen:
                                # print(f"On layer {counter} repeated: {asn} {ip}")
                                pass
                            else:
                                print(f"On layer {counter}: {asn} {ip}")
                                seen.append(ip)
                                existsResult = check_exists(asn, ip)
                                if existsResult == True:
                                    print("NLRI " + str(count) + " passed authorization...checking next ASN")
                                elif existsResult == False:
                                    handle_unregistered_advertisement(m_pkt, nlri, validationResult, update)
                                #elif validationResult == validatePrefixResult.prefixOwnersDoNotMatch:
                                #    handle_invalid_advertisement(m_pkt, nlri, validationResult, update)
                                else:
                                    print("error. should never get here. received back unknown validationResult: " + str(validationResult))   
                    else:
                        # print(f"On layer {counter}: Type code error: {type_code}")
                        pass
                            
                else:
                    # print(f"On layer {counter}: No attributes, breaking")
                    break
            except:
                pass
    else:
        print("BGP Update not found in packet")
        pass
            
# tcpdump -i any port 179 -w example.pcap
try:
    sniff(prn=proxy, filter="port 179", iface="ix100")
    # sniff(prn=lambda x:x.summary(), filter="port 179")
except KeyboardInterrupt:
    pass

# from scapy.all import *
# sniff(prn=lambda x:x.summary(), filter="port 179", iface="ix12")