from scapy.all import *
from scapy.contrib.bgp import *
import mysql.connector
from mysql.connector import Error

# MySQL reading from PCAP. Not super needed  ao 26 Jul 2023

def check_exists(asn, ip):
    print(f'SELECT EXISTS(SELECT * FROM network WHERE asn={asn} AND ip="{ip}"')
    query = "SELECT EXISTS(SELECT * FROM network WHERE asn=%s AND ip=%s)"
    args = (asn, ip)

    try:
        conn = mysql.connector.connect(host='192.168.1.11', database='my_database', user='my_user', password='my_password')
        cursor = conn.cursor()
        cursor.execute(query, args)
        result = cursor.fetchone()
        return result[0] == 1
    except Error as error:
        print(f'Error: {error}')
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# Read the pcap file
packets = rdpcap('/home/gokies/Downloads/justtwo.pcap')

# Iterate over the packets
for packet in packets:
    checked = dict()

    if BGPUpdate in packet:
    # for bgp_update in packet.getlayer(1):
        # bgp_update = packet[BGPUpdate]
        counter = 0
        while True:
            bgp_update = packet.getlayer(counter)
            if bgp_update is None:
                break
            counter += 1

            try:
                path_attributes = bgp_update.path_attr
                print(path_attributes)
                for path_entry in path_attributes:
                    type_code = path_entry.type_code
                    if type_code == 2:
                        print("ASN:", path_entry.attribute.segments[0].segment_value)
                        asn = path_entry.attribute.segments[0].segment_value[-1]
                        # print("Last Segment Value:", asn)
                
                for count, nlri in enumerate(bgp_update.nlri):
                    ip = str(nlri.prefix)
                    print("IP:", ip)
                    location = f"{asn} {ip}"
                    checked[location] = check_exists(asn, ip)
                    # print(check_exists(asn, ip))
            except:
                pass
    print(checked)
# tcpdump -i any port 179 -w example.pcap
