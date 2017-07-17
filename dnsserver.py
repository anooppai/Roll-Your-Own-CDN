#! /usr/bin/env python
import urllib
import json
import math
import thread
import sys
import os
import socket
from struct import pack,unpack

EARTH_RADIUS = 6373

def readPortAndOrigin():
    if sys.argv[1] == "-p":
        port_num = int(sys.argv[2])
    else:
        print "Invalid port specified"
        sys.exit(0)
    if sys.argv[3] == "-n":
        if sys.argv[4] == "cs5700cdn.example.com":
            cdn = sys.argv[4]
        else:
            print "Invalid CDN name"
            sys.exit(0)
    else:
        print "DNS flag not specified"
        sys.exit(0)
    return port_num, cdn

def main():
    dictionary = {}
    if len(sys.argv) != 5:
        print "Invalid number of arguments specified!"
        sys.exit(0)
    else:
        port_num, cdn = readPortAndOrigin()
    mysocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    mysocket.connect(("david.choffnes.com", 80))
    ip = mysocket.getsockname()[0]
    mysocket.close()
    newsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    newsocket.bind((ip, port_num))
    while 1:
        content = newsocket.recvfrom(653555)
        thread.start_new_thread(getInfoPerRequest, (newsocket, content, dictionary, cdn))
    newsocket.close()


#def performUnpack(content, newsocket, getNearestIP, cdn):



def getDistance(latitude, longitude, server_loc):

    val1 = (90.0 - latitude) * (math.pi/180.0)
    val2 = (90.0 - server_loc[0]) * (math.pi/180.0)

    theta1 = longitude * (math.pi/180.0)
    theta2 = server_loc[1] * (math.pi/180.0)

    dist = (math.sin(val1) * math.sin(val2) * math.cos(theta1 - theta2) +
            math.cos(val1) * math.cos(val2))

    return (math.acos(dist)) * EARTH_RADIUS


def getInfoPerRequest(newsocket, content, dictionary, cdn):
    replica_servers_location = {
        '54.67.25.76': [37.3388, -121.8914],
        '54.210.1.206': [39.0481, -77.4728],
        '35.161.203.105': [45.8696, -119.6880],
        '52.213.13.179': [53.3389, -6.2595],
        '52.196.161.198': [35.6427, 139.7677],
        '54.255.148.115': [1.2855, 103.8565],
        '13.54.30.86': [-33.8612, 151.1982],
        '52.67.177.90': [-23.5464, -46.6289],
        '35.156.54.135': [50.1167, 8.6833]}

    requestedIP = content[1]
    if requestedIP[0] not in dictionary:
        data = urllib.urlopen(url = 'http://ipinfo.io/'+str(requestedIP[0])+'/json').read()
        json_response = json.loads(data)
        loc = json_response["loc"]
        latitude, longitude = loc.split(',')
        #latitude = float (response["latitude"])
        #longitude = float (response["longitude"])
        for a_replica in replica_servers_location:
            per_replica_loc = replica_servers_location[a_replica]
            per_replica_loc = getDistance(latitude, longitude, per_replica_loc)
            replica_servers_location[a_replica] = per_replica_loc
        getNearestIP = min(replica_servers_location, key= replica_servers_location.get)
        dictionary[requestedIP[0]] = getNearestIP
    else:
        getNearestIP = dictionary[requestedIP[0]]
    content = content[0].strip()
    performUnpack(content, newsocket, getNearestIP, cdn, requestedIP)


def performUnpack(content, newsocket, getNearestIP, cdn, requestedIP):
    start_sub = 1
    unpacked = unpack('!6H', content[:12])
    final_header = content[0:2] + '\x81\x80' + pack('!4H', unpacked[2], 1, 0, 0)
    header_less = content[12:]
    subdomain_length = unpack('!B', header_less[0])
    while(subdomain_length[0] != 0):
        end_sub = start_sub + subdomain_length[0]
        unpack_sub = str(subdomain_length[0]) + 's'
        if var:
            var = var + '.' + unpack(unpack_sub, header_less[start_sub : end_sub])[0]
        else:
            var = unpack(unpack_sub, header_less[start_sub : end_sub])[0]
        body_unpack = header_less[end_sub]
        subdomain_length = unpack('!B', body_unpack)
        start_sub = end_sub + 1
    if var == cdn:
        dns_response_packet = pack('!HHHLH4s', 0xC00C, 0x0001, 0x0001, 60, 4, socket.inet_aton(getNearestIP))
        q = content[12: 12+(end_sub+5)]
        dnspack = final_header + q + dns_response_packet
        newsocket.sendto(dnspack, requestedIP)
    else:
        print "Some error occured"
        sys.exit(0)
    return

main()





