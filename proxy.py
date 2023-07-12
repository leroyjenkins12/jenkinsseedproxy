from scapy.all import *
from scapy.contrib.bgp import *
import mysql.connector
from mysql.connector import Error


def check_exists(asn, ip):
    # print(f'SELECT EXISTS(SELECT * FROM network WHERE asn={asn} AND ip="{ip}"')
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
    sniff(prn=lambda x:x.proxy, count=5, filter="port 179")