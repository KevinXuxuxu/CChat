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

class printer:

    def p(self, ident, msg):
        if ident == "json":
            self.printmsg(msg)
        elif ident == "info":
            print(msg)
        elif ident == "bc":
            print(msg+'\n')
        elif ident == ':':
            print msg,
            
    def printmsg(self, emsg):
    #pdb.set_trace()
        d = json.loads(emsg)
        data = u''
        global __uname__
        if d['name'] != __uname__:
            data = d['data']+u'\n'
        print((u"{}  from {} at {}\n").format(data, d['name'], d['time']))

Printer = printer()

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
    names = []
    hsock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    def __init__(self):
        global __port__
        global __uname__
        self.hsock.bind(('', __port__))
        self.names.append(__uname__)
    
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
                Printer.p("bc",d['name']+" has quit.")
                self.send(emsg, None)
                self.sockets[i].close()
                self.alive[i] = False
                self.names.remove(d['name'])
                break
            if d.has_key('term'):
                self.sockets[i].close()
                self.alive[i] = False
                break
            Printer.p('json',emsg)
            self.send(emsg, self.sockets[i])

    def sendTrd(self):
        while True:
            msg = raw_input()
            emsg = encode(msg,True)
            self.send(emsg, None)

            if msg == "q":
                Printer.p("info","you closed the chat room.")
                ts = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
                global __port__
                ts.connect(("localhost",__port__))
                ts.send("terminate")
                ts.close()
                break
            Printer.p('json',emsg)

    def lisRecvTrd(self):
        self.hsock.listen(5)
        while True:
            clisock, (remoteHost, remotePort) = self.hsock.accept()
            clisock.send("name?")
            cliname = clisock.recv(1024)
            if cliname == "terminate" and remoteHost == "127.0.0.1":
                self.closeAll()
                break
            while cliname in self.names:
                clisock.send(json.dumps({'data':'name '+cliname+' is taken, please enter a new name.', 'broadcast':True}))
                cliname = clisock.recv(1024)
            clisock.send(json.dumps({"data":"confirm"}))

            bc = "%s from [%s:%s] joined." % (cliname, remoteHost, remotePort)
            Printer.p('bc',bc)
            ebc = json.dumps({'data':bc, 'broadcast':True})
            self.send(ebc, clisock)
            
            self.sockets.append(clisock)
            self.alive.append(True)
            self.names.append(cliname)
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
    Printer.p('bc',"Chat room started!")
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
            Printer.p('info',"quiting")
            break
        Printer.p('json',emsg)

def clirecv(sock):
    while True:
        emsg = sock.recv(1024)
        d = json.loads(emsg)
        if d.has_key('broadcast'):
            Printer.p('bc',d['data'])
        elif d.has_key('quit'):
            global __uname__
            if d['name'] == __uname__:
                break
            else:
                Printer.p('bc',d['name']+" has quit.")
        elif d.has_key('term'):
            Printer.p('bc',"host has closed the chat room, enter q to quit.")
            sock.send(emsg)
            break
        else:
            Printer.p('json',emsg)
                

def tcpClient(addr, port):
    clisock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    try:
        clisock.connect((addr, port))
    except Exception as e:
        print(e)
        return
    Printer.p('info',"waiting for response...")
    res = clisock.recv(1024)
    if res != "name?":
        Printer.p('info',"connection failed!")
        return
    while True:
        global __uname__
        clisock.send(__uname__)
        res = clisock.recv(1024)
        eres = json.loads(res)
        if not eres.has_key('broadcast'):
            break
        Printer.p('info',eres['data'])
        Printer.p(':', "new name:")
        __uname__ = raw_input()
    Printer.p('bc',"joined!")
    
    tsend = th.Thread(target=clisend, args=(clisock,))
    trecv = th.Thread(target=clirecv, args=(clisock,))
    tsend.setDaemon(True)
    trecv.setDaemon(True)
    tsend.start()
    trecv.start()
    tsend.join()
    clisock.close()
    Printer.p('info',"you quited the chat room.")
    
def main():
    Printer.p('info',"Welcome to Cchat.")
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
        elif read == "info":
            # global __port__, __uname__
            print(u"port:   {}\nname:   {}".format(__port__, __uname__))
        
        print ">>",
        read = raw_input()

if __name__ == "__main__":
    main()
