# use utf-8

__author__ = "KevinXuxuxu", "Tenut"
__email__ = "kevin.xu.fangzhou@gmail.com", "treamug@gmail.com"

__uname__ = "Host"
__port__ = 9527

"""
this is a chatting commandline tool
"""

import threading as th
import socket as sk
import re
import json
from time import asctime
import pdb

def printmsg(emsg):
    #pdb.set_trace()
    d = json.loads(emsg)
    data = u''
    global __uname__
    if d['name'] != __uname__:
        data = d['data']+u'\n'
    print((u"{}  from {} at {}\n").format(data, d['name'], d['time']))

def encode(msg,host):
    global __uname__
    d = {'data':msg, 'name':__uname__, 'time':asctime()}
    if msg == 'q':
        if host: d['term']=True
        else: d['quit']=True
    m = json.dumps(d)
    return m

class host:
    sockets = []
    alive = []
    hsock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    def __init__(self):
        global __port__
        self.hsock.bind(('', __port__))
    
    def send(self, msg, esock):
        for i in range(0,len(self.sockets)):
            s = self.sockets[i]
            if s != esock and self.alive[i]:
                s.send(msg)

    def closeAll(self):
        for i in range(0,len(self.sockets)):
            s = self.sockets[i]
            if self.alive[i]:
                s.close()

    def recv(self, i):
        while True:
            emsg = self.sockets[i].recv(1024)
            
            try:
                d = json.loads(emsg)
            except Exception as e:
                print(e)
                print("----"+emsg+"----")
                break
                
            if d.has_key('quit'):
                print(d['name']+" has quit.\n")
                self.send(emsg, None)
                self.sockets[i].close()
                self.alive[i] = False
                break
            if d.has_key('term'):
                self.sockets[i].close()
                self.alive[i] = False
                break
            printmsg(emsg)
            self.send(emsg, self.sockets[i])

    def sendTrd(self):
        while True:
            msg = raw_input()
            emsg = encode(msg,True)
            self.send(emsg, None)

            if msg == "q":
                print("you closed the chat room.")
                ts = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
                global __port__
                ts.connect(("localhost",__port__))
                ts.send("terminate")
                ts.close()
                break
            printmsg(emsg)

    def lisRecvTrd(self):
        self.hsock.listen(5)
        while True:
            clisock, (remoteHost, remotePort) = self.hsock.accept()
            clisock.send("confirm")
            cliname = clisock.recv(1024)
            if cliname == "terminate" and remoteHost == "127.0.0.1":
                self.closeAll()
                break

            bc = "%s from [%s:%s] joined." % (cliname, remoteHost, remotePort)
            print(bc+'\n')
            ebc = json.dumps({'data':bc, 'broadcast':True})
            self.send(ebc, clisock)
            
            self.sockets.append(clisock)
            self.alive.append(True)
            t = th.Thread(target=self.recv, args=(len(self.sockets)-1,))
            t.setDaemon(True)
            t.start()

    def start(self):
        tlis = th.Thread(target=self.lisRecvTrd, args=())
        tsend = th.Thread(target=self.sendTrd, args=())
        tlis.setDaemon(True)
        tsend.setDaemon(True)
        tlis.start()
        tsend.start()
        tlis.join()
        self.hsock.close()
        
def tcpServer():
    h = host()
    print("Chat room started!\n")
    h.start()
    del(h)

def clisend(sock):
    while True:
        global __uname__
        msg = raw_input()
        emsg = encode(msg,False)
        try:
            sock.send(emsg)
        except Exception as e:
            if msg != 'q':
                print(e)
                break
        if msg == 'q':
            print("quiting")
            break
        printmsg(emsg)

def clirecv(sock):
    while True:
        emsg = sock.recv(1024)
        d = json.loads(emsg)
        if d.has_key('broadcast'):
            print(d['data']+'\n')
        elif d.has_key('quit'):
            global __uname__
            if d['name'] == __uname__:
                break
            else:
                print(d['name']+" has quit.\n")
        elif d.has_key('term'):
            print("host has closed the chat room, enter q to quit.")
            sock.send(emsg)
            break
        else:
            printmsg(emsg)
                

def tcpClient(addr, port):
    clisock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    try:
        clisock.connect((addr, port))
    except Exception as e:
        print(e)
        return
    print("waiting for response...")
    res = clisock.recv(1024)
    if res != "confirm":
        print("connection failed!")
        return
    print("joined!")
    global __uname__
    clisock.send(__uname__)
    tsend = th.Thread(target=clisend, args=(clisock,))
    trecv = th.Thread(target=clirecv, args=(clisock,))
    tsend.setDaemon(True)
    trecv.setDaemon(True)
    tsend.start()
    trecv.start()
    tsend.join()
    clisock.close()
    print("you quited the chat room.")
    
def main():
    print("Welcome to Cchat.")
    print(">>"),
    read = raw_input()
    while read != "quit":
        if read == "host":
            tcpServer()
        elif read == "connect":
            print "where?",
            address = raw_input()
            (addr, port) = re.split(':', address)
            tcpClient(addr, int(port))
        elif read == "name":
            global __uname__
            __uname__ = raw_input()
            #print __uname__
            print "new name set."
        elif read == "port":
            global __port__
            __port__ = int(raw_input())
            print "new port set."
        
        print ">>",
        read = raw_input()

if __name__ == "__main__":
    main()
