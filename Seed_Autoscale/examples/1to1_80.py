#!/usr/bin/env python3
# encoding: utf-8

from seedemu.layers import Base, Routing, Ebgp, Ibgp, Ospf, PeerRelationship, Dnssec
from seedemu.services import WebService, DomainNameService, DomainNameCachingService
from seedemu.services import CymruIpOriginService, ReverseDomainNameService, BgpLookingGlassService
from seedemu.compiler import Docker, Graphviz
from seedemu.hooks import ResolvConfHook
from seedemu.core import Emulator, Service, Binding, Filter
from seedemu.layers import Router
from seedemu.raps import OpenVpnRemoteAccessProvider
from seedemu.utilities import Makers
from typing import List, Tuple, Dict
import argparse
import random

#Process command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('-d', type=int, required = False,
                    help="proxy deployment percentage")
FLAGS = parser.parse_args()
###############################################################################
emu     = Emulator()
base    = Base()
routing = Routing()
ebgp    = Ebgp()
ibgp    = Ibgp()
ospf    = Ospf()
web     = WebService()
ovpn    = OpenVpnRemoteAccessProvider()


###############################################################################
ix2 = base.createInternetExchange(2)
ix3 = base.createInternetExchange(3)
ix4 = base.createInternetExchange(4)
ix5 = base.createInternetExchange(5)
ix6 = base.createInternetExchange(6)
ix7 = base.createInternetExchange(7)
ix8 = base.createInternetExchange(8)
ix9 = base.createInternetExchange(9)
ix10 = base.createInternetExchange(10)
ix11 = base.createInternetExchange(11)
ix12 = base.createInternetExchange(12)
ix13 = base.createInternetExchange(13)
ix14 = base.createInternetExchange(14)
ix15 = base.createInternetExchange(15)
ix16 = base.createInternetExchange(16)
ix17 = base.createInternetExchange(17)
ix18 = base.createInternetExchange(18)
ix19 = base.createInternetExchange(19)
ix20 = base.createInternetExchange(20)
ix21 = base.createInternetExchange(21)
ix22 = base.createInternetExchange(22)
ix23 = base.createInternetExchange(23)
ix24 = base.createInternetExchange(24)
ix25 = base.createInternetExchange(25)
ix26 = base.createInternetExchange(26)
ix27 = base.createInternetExchange(27)
ix28 = base.createInternetExchange(28)
ix29 = base.createInternetExchange(29)
ix30 = base.createInternetExchange(30)
ix31 = base.createInternetExchange(31)
ix32 = base.createInternetExchange(32)
ix33 = base.createInternetExchange(33)
ix34 = base.createInternetExchange(34)
ix35 = base.createInternetExchange(35)
ix36 = base.createInternetExchange(36)
ix37 = base.createInternetExchange(37)
ix38 = base.createInternetExchange(38)
ix39 = base.createInternetExchange(39)
ix40 = base.createInternetExchange(40)
ix41 = base.createInternetExchange(41)
ix42 = base.createInternetExchange(42)
ix43 = base.createInternetExchange(43)
ix44 = base.createInternetExchange(44)
ix45 = base.createInternetExchange(45)
ix46 = base.createInternetExchange(46)
ix47 = base.createInternetExchange(47)
ix48 = base.createInternetExchange(48)
ix49 = base.createInternetExchange(49)
ix50 = base.createInternetExchange(50)
ix51 = base.createInternetExchange(51)
ix52 = base.createInternetExchange(52)
ix53 = base.createInternetExchange(53)
ix54 = base.createInternetExchange(54)
ix55 = base.createInternetExchange(55)
ix56 = base.createInternetExchange(56)
ix57 = base.createInternetExchange(57)
ix58 = base.createInternetExchange(58)
ix59 = base.createInternetExchange(59)
ix60 = base.createInternetExchange(60)
ix61 = base.createInternetExchange(61)
ix62 = base.createInternetExchange(62)
ix63 = base.createInternetExchange(63)
ix64 = base.createInternetExchange(64)
ix65 = base.createInternetExchange(65)
ix66 = base.createInternetExchange(66)
ix67 = base.createInternetExchange(67)
ix68 = base.createInternetExchange(68)
ix69 = base.createInternetExchange(69)
ix70 = base.createInternetExchange(70)
ix71 = base.createInternetExchange(71)
ix72 = base.createInternetExchange(72)
ix73 = base.createInternetExchange(73)
ix74 = base.createInternetExchange(74)
ix75 = base.createInternetExchange(75)
ix76 = base.createInternetExchange(76)
ix77 = base.createInternetExchange(77)
ix78 = base.createInternetExchange(78)
ix79 = base.createInternetExchange(79)
ix80 = base.createInternetExchange(80)
ix81 = base.createInternetExchange(81)



###############################################################################
# 5 Transit ASes -> 100-105
# 12 Stub ASes -> 106-117
# Total num ASes of 17
total_ASes =  160
if FLAGS.d:       
  dep_percentage = FLAGS.d/100
  true_count = int(total_ASes * dep_percentage)
  false_count = total_ASes - true_count
  proxy = [True] * true_count + [False] * false_count
  #random.seed(0) 
  random.shuffle(proxy)
else: # no percentage specified, do not deploy proxy
  proxy = [False] * total_ASes
  
###############################################################################
# Create Transit Autonomous Systems 

##Tier 1 ASes
#None in this toplogy

## Tier 2 ASes: QTY - 8
Makers.makeTransitAs(base, 85, [2, 81], [(2, 81)], proxy[0])
Makers.makeTransitAs(base, 86, [2, 11], [(2, 11)], proxy[1])
Makers.makeTransitAs(base, 87, [11, 27], [(11, 27)], proxy[2])
Makers.makeTransitAs(base, 88, [27, 42], [(27, 42)], proxy[3])
Makers.makeTransitAs(base, 89, [56, 42], [(56, 42)], proxy[4])
Makers.makeTransitAs(base, 90, [42, 20], [(42, 20)], proxy[5])
Makers.makeTransitAs(base, 91, [12, 20], [(12, 20)], proxy[6])
Makers.makeTransitAs(base, 92, [6, 12], [(6, 12)], proxy[7])
Makers.makeTransitAs(base, 93, [12, 28], [(12, 28)], proxy[8])
Makers.makeTransitAs(base, 94, [12, 3], [(12, 3)], proxy[9])
Makers.makeTransitAs(base, 95, [28, 43], [(28, 43)], proxy[10])
Makers.makeTransitAs(base, 96, [43, 57], [(43, 57)], proxy[11])
Makers.makeTransitAs(base, 97, [57, 78], [(57, 78)], proxy[12])
Makers.makeTransitAs(base, 98, [55, 67], [(55, 67)], proxy[13])
Makers.makeTransitAs(base, 99, [55, 41], [(55, 41)], proxy[14])
Makers.makeTransitAs(base, 100, [41, 27], [(41, 27)], proxy[15])
Makers.makeTransitAs(base, 101, [40, 26], [(40, 26)], proxy[16])
Makers.makeTransitAs(base, 102, [55, 40], [(55, 40)], proxy[17])
Makers.makeTransitAs(base, 103, [66, 55], [(66, 55)], proxy[18])
Makers.makeTransitAs(base, 104, [66, 79], [(66, 79)], proxy[19])
Makers.makeTransitAs(base, 105, [80, 66], [(80, 66)], proxy[20])
Makers.makeTransitAs(base, 106, [65, 54], [(65, 54)], proxy[21])
Makers.makeTransitAs(base, 107, [54, 39], [(54, 39)], proxy[22])
Makers.makeTransitAs(base, 108, [39, 25], [(39, 25)], proxy[23])
Makers.makeTransitAs(base, 109, [18, 25], [(18, 25)], proxy[24])
Makers.makeTransitAs(base, 110, [10, 25], [(10, 25)], proxy[25])
Makers.makeTransitAs(base, 111, [10, 26], [(10, 26)], proxy[26])
Makers.makeTransitAs(base, 112, [18, 9], [(18, 9)], proxy[27])
Makers.makeTransitAs(base, 113, [9, 17], [(9, 17)], proxy[28])
Makers.makeTransitAs(base, 114, [8, 5], [(8, 5)], proxy[29])
Makers.makeTransitAs(base, 115, [17, 16], [(17, 16)], proxy[30])
Makers.makeTransitAs(base, 116, [16, 8], [(16, 8)], proxy[31])
Makers.makeTransitAs(base, 117, [16, 22], [(16, 22)], proxy[32])
Makers.makeTransitAs(base, 118, [22, 23], [(22, 23)], proxy[33])
Makers.makeTransitAs(base, 119, [23, 36], [(23, 36)], proxy[34])
Makers.makeTransitAs(base, 120, [24, 37], [(24, 37)], proxy[35])
Makers.makeTransitAs(base, 121, [38, 52], [(38, 52)], proxy[36])
Makers.makeTransitAs(base, 122, [24, 38], [(24, 38)], proxy[37])
Makers.makeTransitAs(base, 123, [53, 38], [(53, 38)], proxy[38])
Makers.makeTransitAs(base, 124, [64, 52], [(64, 52)], proxy[39])
Makers.makeTransitAs(base, 125, [51, 72], [(51, 72)], proxy[40])
Makers.makeTransitAs(base, 126, [51, 63], [(51, 63)], proxy[41])
Makers.makeTransitAs(base, 127, [36, 51], [(36, 51)], proxy[42])
Makers.makeTransitAs(base, 128, [36, 50], [(36, 50)], proxy[43])
Makers.makeTransitAs(base, 129, [35, 50], [(35, 50)], proxy[44])
Makers.makeTransitAs(base, 130, [50, 71], [(50, 71)], proxy[45])
Makers.makeTransitAs(base, 131, [62, 73], [(62, 73)], proxy[46])
Makers.makeTransitAs(base, 132, [33, 62], [(33, 62)], proxy[47])
Makers.makeTransitAs(base, 133, [21, 34], [(21, 34)], proxy[48])
Makers.makeTransitAs(base, 134, [15, 21], [(15, 21)], proxy[49])
Makers.makeTransitAs(base, 135, [8, 15], [(8, 15)], proxy[50])
Makers.makeTransitAs(base, 136, [81, 4], [(81, 4)], proxy[51])
Makers.makeTransitAs(base, 137, [7, 14], [(7, 14)], proxy[52])
Makers.makeTransitAs(base, 138, [4, 14], [(4, 14)], proxy[53])
Makers.makeTransitAs(base, 139, [14, 32], [(14, 32)], proxy[54])
Makers.makeTransitAs(base, 140, [32, 33], [(32, 33)], proxy[55])
Makers.makeTransitAs(base, 141, [32, 48], [(32, 48)], proxy[56])
Makers.makeTransitAs(base, 142, [47, 48], [(47, 48)], proxy[57])
Makers.makeTransitAs(base, 143, [48, 49], [(48, 49)], proxy[58])
Makers.makeTransitAs(base, 144, [49, 74], [(49, 74)], proxy[59])
Makers.makeTransitAs(base, 145, [47, 70], [(47, 70)], proxy[60])
Makers.makeTransitAs(base, 146, [46, 61], [(46, 61)], proxy[61])
Makers.makeTransitAs(base, 147, [60, 75], [(60, 75)], proxy[62])
Makers.makeTransitAs(base, 148, [60, 76], [(60, 76)], proxy[63])
Makers.makeTransitAs(base, 149, [45, 60], [(45, 60)], proxy[64])
Makers.makeTransitAs(base, 150, [45, 46], [(45, 46)], proxy[65])
Makers.makeTransitAs(base, 151, [31, 46], [(31, 46)], proxy[66])
Makers.makeTransitAs(base, 152, [19, 31], [(19, 31)], proxy[67])
Makers.makeTransitAs(base, 153, [7, 19], [(7, 19)], proxy[68])
Makers.makeTransitAs(base, 154, [13, 30], [(13, 30)], proxy[69])
Makers.makeTransitAs(base, 155, [29, 13], [(29, 13)], proxy[70])
Makers.makeTransitAs(base, 156, [44, 30], [(44, 30)], proxy[71])
Makers.makeTransitAs(base, 157, [18, 24], [(18, 24)], proxy[72])
Makers.makeTransitAs(base, 158, [44, 59], [(44, 59)], proxy[73])
Makers.makeTransitAs(base, 159, [44, 58], [(44, 58)], proxy[74])
Makers.makeTransitAs(base, 160, [68, 58], [(68, 58)], proxy[75])
Makers.makeTransitAs(base, 161, [68, 77], [(68, 77)], proxy[76])
Makers.makeTransitAs(base, 162, [59, 69], [(59, 69)], proxy[77])
Makers.makeTransitAs(base, 163, [45, 59], [(45, 59)], proxy[78])
#Makers.makeTransitAs(base, 164, [187, 188], [(187, 188)], proxy[79])
#####################################################################
Makers.makeStubAs(emu, base, 249, 81, [None], proxy[159])
Makers.makeStubAs(emu, base, 170, 2, [None], proxy[80])
Makers.makeStubAs(emu, base, 171, 3, [None], proxy[81])
Makers.makeStubAs(emu, base, 172, 4, [None], proxy[82])
Makers.makeStubAs(emu, base, 173, 5, [None], proxy[83])
Makers.makeStubAs(emu, base, 174, 6, [None], proxy[84])
Makers.makeStubAs(emu, base, 175, 7, [None], proxy[85])
Makers.makeStubAs(emu, base, 176, 8, [None], proxy[86])
Makers.makeStubAs(emu, base, 177, 9, [None], proxy[87])
Makers.makeStubAs(emu, base, 178, 10, [None], proxy[88])
Makers.makeStubAs(emu, base, 179, 11, [None], proxy[89])
Makers.makeStubAs(emu, base, 180, 12, [None], proxy[90])
Makers.makeStubAs(emu, base, 181, 13, [None], proxy[91])
Makers.makeStubAs(emu, base, 182, 14, [None], proxy[92])
Makers.makeStubAs(emu, base, 183, 15, [None], proxy[93])
Makers.makeStubAs(emu, base, 184, 16, [None], proxy[94])
Makers.makeStubAs(emu, base, 185, 17, [None], proxy[95])
Makers.makeStubAs(emu, base, 186, 18, [None], proxy[96])
Makers.makeStubAs(emu, base, 187, 19, [None], proxy[97])
Makers.makeStubAs(emu, base, 188, 20, [None], proxy[98])
Makers.makeStubAs(emu, base, 189, 21, [None], proxy[99])
Makers.makeStubAs(emu, base, 190, 22, [None], proxy[100])
Makers.makeStubAs(emu, base, 191, 23, [None], proxy[101])
Makers.makeStubAs(emu, base, 192, 24, [None], proxy[102])
Makers.makeStubAs(emu, base, 193, 25, [None], proxy[103])
Makers.makeStubAs(emu, base, 194, 26, [None], proxy[104])
Makers.makeStubAs(emu, base, 195, 27, [None], proxy[105])
Makers.makeStubAs(emu, base, 196, 28, [None], proxy[106])
Makers.makeStubAs(emu, base, 197, 29, [None], proxy[107])
Makers.makeStubAs(emu, base, 198, 30, [None], proxy[108])
Makers.makeStubAs(emu, base, 199, 31, [None], proxy[109])
Makers.makeStubAs(emu, base, 200, 32, [None], proxy[110])
Makers.makeStubAs(emu, base, 201, 33, [None], proxy[111])
Makers.makeStubAs(emu, base, 202, 34, [None], proxy[112])
Makers.makeStubAs(emu, base, 203, 35, [None], proxy[113])
Makers.makeStubAs(emu, base, 204, 36, [None], proxy[114])
Makers.makeStubAs(emu, base, 205, 37, [None], proxy[115])
Makers.makeStubAs(emu, base, 206, 38, [None], proxy[116])
Makers.makeStubAs(emu, base, 207, 39, [None], proxy[117])
Makers.makeStubAs(emu, base, 208, 40, [None], proxy[118])
Makers.makeStubAs(emu, base, 209, 41, [None], proxy[119])
Makers.makeStubAs(emu, base, 210, 42, [None], proxy[120])
Makers.makeStubAs(emu, base, 211, 43, [None], proxy[121])
Makers.makeStubAs(emu, base, 212, 44, [None], proxy[122])
Makers.makeStubAs(emu, base, 213, 45, [None], proxy[123])
Makers.makeStubAs(emu, base, 214, 46, [None], proxy[124])
Makers.makeStubAs(emu, base, 215, 47, [None], proxy[125])
Makers.makeStubAs(emu, base, 216, 48, [None], proxy[126])
Makers.makeStubAs(emu, base, 217, 49, [None], proxy[127])
Makers.makeStubAs(emu, base, 218, 50, [None], proxy[128])
Makers.makeStubAs(emu, base, 219, 51, [None], proxy[129])
Makers.makeStubAs(emu, base, 220, 52, [None], proxy[130])
Makers.makeStubAs(emu, base, 221, 53, [None], proxy[131])
Makers.makeStubAs(emu, base, 222, 54, [None], proxy[132])
Makers.makeStubAs(emu, base, 223, 55, [None], proxy[133])
Makers.makeStubAs(emu, base, 224, 56, [None], proxy[134])
Makers.makeStubAs(emu, base, 225, 57, [None], proxy[135])
Makers.makeStubAs(emu, base, 226, 58, [None], proxy[136])
Makers.makeStubAs(emu, base, 227, 59, [None], proxy[137])
Makers.makeStubAs(emu, base, 228, 60, [None], proxy[138])
Makers.makeStubAs(emu, base, 229, 61, [None], proxy[139])
Makers.makeStubAs(emu, base, 230, 62, [None], proxy[140])
Makers.makeStubAs(emu, base, 231, 63, [None], proxy[141])
Makers.makeStubAs(emu, base, 232, 64, [None], proxy[142])
Makers.makeStubAs(emu, base, 233, 65, [None], proxy[143])
Makers.makeStubAs(emu, base, 234, 66, [None], proxy[144])
Makers.makeStubAs(emu, base, 235, 67, [None], proxy[145])
Makers.makeStubAs(emu, base, 236, 68, [None], proxy[146])
Makers.makeStubAs(emu, base, 237, 69, [None], proxy[147])
Makers.makeStubAs(emu, base, 238, 70, [None], proxy[148])
Makers.makeStubAs(emu, base, 239, 71, [None], proxy[149])
Makers.makeStubAs(emu, base, 240, 72, [None], proxy[150])
Makers.makeStubAs(emu, base, 241, 73, [None], proxy[151])
Makers.makeStubAs(emu, base, 242, 74, [None], proxy[152])
Makers.makeStubAs(emu, base, 243, 75, [None], proxy[153])
Makers.makeStubAs(emu, base, 244, 76, [None], proxy[154])
Makers.makeStubAs(emu, base, 245, 77, [None], proxy[155])
Makers.makeStubAs(emu, base, 246, 78, [None], proxy[156])
Makers.makeStubAs(emu, base, 247, 79, [None], proxy[157])
Makers.makeStubAs(emu, base, 248, 80, [None], proxy[158])




# Create real-world AS.
# AS11872 is the Syracuse University's autonomous system

as11872 = base.createAutonomousSystem(11872)
as11872.createRealWorldRouter('rw').joinNetwork('ix2', '10.2.0.118')


###############################################################################
# Peering via RS (route server). The default peering mode for RS is PeerRelationship.Peer, 
# which means each AS will only export its customers and their own prefixes. 
# We will use this peering relationship to peer all the ASes in an IX.
# None of them will provide transit service for others. 


ebgp.addRsPeers(81, [249, 85, 136])
ebgp.addRsPeers(2, [170, 85, 86, 11872])
ebgp.addRsPeers(3, [171, 94])
ebgp.addRsPeers(4, [172, 136,138])
ebgp.addRsPeers(5, [173, 114])
ebgp.addRsPeers(6, [174, 92])
ebgp.addRsPeers(7, [175, 153, 137])
ebgp.addRsPeers(8, [176, 114,116,135])
ebgp.addRsPeers(9, [177, 112, 113])
ebgp.addRsPeers(10, [178, 110, 111])
ebgp.addRsPeers(11, [179, 86, 87])
ebgp.addRsPeers(12, [180, 91, 92, 93, 94])
ebgp.addRsPeers(13, [181, 154, 155])
ebgp.addRsPeers(14, [182, 137, 138, 139])
ebgp.addRsPeers(15, [183, 135, 134])
ebgp.addRsPeers(16, [184, 115, 116, 117])
ebgp.addRsPeers(17, [185, 113, 115])
ebgp.addRsPeers(18, [186, 109, 112, 157])
ebgp.addRsPeers(19, [187, 152, 153])
ebgp.addRsPeers(20, [188, 90, 91])
ebgp.addRsPeers(21, [189, 133, 134])
ebgp.addRsPeers(22, [190, 117, 118])
ebgp.addRsPeers(23, [191, 119, 118])
ebgp.addRsPeers(24, [192, 157, 120, 122])
ebgp.addRsPeers(25, [193, 108, 109, 110])
ebgp.addRsPeers(26, [194, 101, 111])
ebgp.addRsPeers(27, [195, 87, 88, 100])
ebgp.addRsPeers(28, [196, 95, 93])
ebgp.addRsPeers(29, [197, 155])
ebgp.addRsPeers(30, [198, 156, 154])
ebgp.addRsPeers(31, [199, 151, 152])
ebgp.addRsPeers(32, [200, 139, 140, 141])
ebgp.addRsPeers(33, [201, 140, 132])
ebgp.addRsPeers(34, [202, 133])
ebgp.addRsPeers(35, [203, 129])
ebgp.addRsPeers(36, [204, 119, 127])
ebgp.addRsPeers(37, [205, 120])
ebgp.addRsPeers(38, [206, 122, 123, 121])
ebgp.addRsPeers(39, [207, 107, 108])
ebgp.addRsPeers(40, [208, 101, 102])
ebgp.addRsPeers(41, [209, 100, 99])
ebgp.addRsPeers(42, [210, 88, 89, 90])
ebgp.addRsPeers(43, [211, 95, 96])
ebgp.addRsPeers(44, [212, 156, 158, 159])
ebgp.addRsPeers(45, [213, 149, 150, 163])
ebgp.addRsPeers(46, [214, 150, 151, 146])
ebgp.addRsPeers(47, [215, 142, 145])
ebgp.addRsPeers(48, [216, 141, 142, 143])
ebgp.addRsPeers(49, [217, 143, 144])
ebgp.addRsPeers(50, [218, 128, 129, 130])
ebgp.addRsPeers(51, [219, 125, 126, 127])
ebgp.addRsPeers(52, [220, 121, 124])
ebgp.addRsPeers(53, [221, 123])
ebgp.addRsPeers(54, [222, 106, 107])
ebgp.addRsPeers(55, [223, 98, 99, 102, 103])
ebgp.addRsPeers(56, [224, 89])
ebgp.addRsPeers(57, [225, 96, 97])
ebgp.addRsPeers(58, [226, 159, 160])
ebgp.addRsPeers(59, [227, 163, 158, 162])
ebgp.addRsPeers(60, [228, 149, 148, 147])
ebgp.addRsPeers(61, [229, 146])
ebgp.addRsPeers(62, [230, 131, 132])
ebgp.addRsPeers(63, [231, 126])
ebgp.addRsPeers(64, [232, 124])
ebgp.addRsPeers(65, [233, 106])
ebgp.addRsPeers(66, [234, 103, 104, 105])
ebgp.addRsPeers(67, [235, 98])
ebgp.addRsPeers(68, [236, 160, 161])
ebgp.addRsPeers(69, [237, 162])
ebgp.addRsPeers(70, [238, 145])
ebgp.addRsPeers(71, [239, 130])
ebgp.addRsPeers(72, [240, 125])
ebgp.addRsPeers(73, [241, 131])
ebgp.addRsPeers(74, [242, 144])
ebgp.addRsPeers(75, [243, 147])
ebgp.addRsPeers(76, [244, 148])
ebgp.addRsPeers(77, [245, 161])
ebgp.addRsPeers(78, [246, 97])
ebgp.addRsPeers(79, [247, 104])
ebgp.addRsPeers(80, [248, 105])


####AVG IX Connection = 238/32 = 2.975 ASes, 1.9625 without Stubs.




# Add layers to the emulator
emu.addLayer(base)
emu.addLayer(routing)
emu.addLayer(ebgp)
emu.addLayer(ibgp)
emu.addLayer(ospf)
emu.addLayer(web)

# Save it to a component file, so it can be used by other emulators
emu.dump('base-component.bin')

# Uncomment the following if you want to generate the final emulation files
emu.render()
emu.compile(Docker(), './output_1to1_80', override=True)
