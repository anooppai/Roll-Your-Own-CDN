#! /usr/bin/env python
from BaseHTTPServer import HTTPServer,BaseHTTPRequestHandler
import urllib
import sys
import os
import sqlite3
import binascii
import zlib
import commands
import re
from threading import Thread

global origin
MAX_LIMIT = 9.5 * 1024 * 1024


def get_ip():
    ifconfig = commands.getoutput("ifconfig -a")
    iplist = re.findall(r'inet addr:(.*?) ', ifconfig)
    for ip in iplist:
        if ip != '127.0.0.1':
            return ip



class MyHandler(BaseHTTPRequestHandler):
    def do_GET(s):
        print "IN"
        try:
            thread = Thread(target = s.myThread())
            thread.start()
        except:
            print "Error when starting threads"
            s.send_error(404, "Problem loading file")

    def fetchFromOrigin(retrievedPath, getcursor):
        """

        :rtype: object
        """
        fetch_request = 'http://' + origin + ':8080' + retrievedPath
        readContent = urllib.urlopen(fetch_request).read()
        #readContent = getContent.read()
        gatherData = buffer(zlib.compress(readContent))
        fileInfo = os.stat('primary.db')
        sizeOfCache = fileInfo.st_size

        return sizeOfCache, readContent, gatherData

    def fetchFromCache(retrievedPath, getcursor):
        cacheDataObject = getcursor.execute("SELECT data FROM Cache"
                                " WHERE path =:retrievedPath",{"path":retrievedPath})
        dataValue = getcursor.fetchone()
        hitsObj = getcursor.execute("SELECT hits FROM Cache"
                                " WHERE path =:retrievedPath",{"path":retrievedPath})
        getHits = getcursor.fetchone()
        getHitsZero = getHits[0]
        getHitsZero = getHitsZero + 1
        dataValue = zlib.decompress(dataValue[0])
        return dataValue, getHitsZero

    def myThread(s, *args):
        print "Hi"
        database = sqlite3.connect('primary.db')
        getcursor = database.cursor()
        retrievedPath = s.path
        obj = getcursor.execute("SELECT path FROM Cache"
                                " WHERE path =:retrievedPath",{"path":retrievedPath})
        updatedPath = getcursor.fetchone()
        if updatedPath != None:
            readContent, getHitsZero = s.fetchFromCache(retrievedPath, getcursor)
            getcursor.execute("UPDATE Cache SET hits =:getHitsZero "
                              "WHERE path=:retrievedPath", {"Hits": getHitsZero, "Path": retrievedPath})

        else:
            sizeOfCache, readContent, gatherData = s.fetchFromOrigin(retrievedPath, getcursor)
            if ((len(readContent)) + sizeOfCache < MAX_LIMIT):
                getcursor.execute("INSERT INTO Cache(data, path, hits) VALUES(?, ?, ?)", (gatherData, retrievedPath, 1))
            else:
                getcursor.execute(
                    "DELETE FROM Cache WHERE path = (SELECT path from Cache where hits = (SELECT MIN(hits) from Cache))")
                getcursor.execute("INSERT INTO Cache(data, path, hits) VALUES(?, ?, ?)", (gatherData, retrievedPath, 1))

        database.commit()
        database.close()
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write(readContent)

def readPortAndOrigin():
    if sys.argv[1] != "-p":
        print "Invalid port specified"
        sys.exit(0)
    else:
        port_num = int(sys.argv[2])
    if sys.argv[3] != "-o":
        print "Specified origin is invalid"
        sys.exit(0)
    else:
        origin = str(sys.argv[4])
    return port_num, origin

def main():
    if len(sys.argv) != 5:
        print "Invalid number of arguments specified!"
        sys.exit(0)
    else:
        port_num, origin = readPortAndOrigin()
    server_class = HTTPServer
    #ip = get_ip()
    #print "Port ",port_num
    httpd = server_class(('', port_num), MyHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
	main()



