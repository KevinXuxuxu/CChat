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

def input(sock):
    while True:
        global __uname__
        ipt = raw_input()
        if ipt == "q":
            print "terminate"
            try:
                sock.send(__uname__+" terminated the conversation.")
            except Exception as e:
                pass
            break
        print "  from "+__uname__
        print
        try:
            sock.send(ipt + "\n" + "  from "+__uname__+"\n")
        except Exception as e:
            print e
            break
    #sock.close()

def recieve(sock):
    while True:
        rcv = sock.recv(1024)
        if ":" not in rcv:
            print rcv
            break
        print rcv
        print

def conversation(sock):
    threads = []
    threads.append(th.Thread(target=input, args=(sock,)))
    threads.append(th.Thread(target=recieve, args=(sock,)))
    for t in threads:
        t.setDaemon(True)
        t.start()
    threads[1].join()
    threads[0].join()
    sock.close()
    print "conversation over."

def tcpServer():
    srvsock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    srvsock.bind(('', __port__))
    srvsock.listen(5)

    print "waiting for connection"

    #while True:
    clisock, (remoteHost, remotePort) = srvsock.accept()
    print "[%s:%s] trying to connected" % (remoteHost, remotePort)
    confirm = raw_input()
    clisock.send(confirm)

    conversation(clisock)
    
    #clisock.close()

def tcpClient(addr, port):
    clisock = sk.socket(sk.AF_INET, sk.SOCK_STREAM)
    try:
        clisock.connect((addr, int(port)))
    except Exception as e:
        print e
        return
    print "waiting for acception..."
    #while True:
    confirm = clisock.recv(1024)
    if not confirm or confirm == "n":
        print "connection failed"
        clisock.close()
        return
    
    print "confirmed."
    conversation(clisock)    
        
        
def main():
    print "Welcome to Cchat."
    print ">>",
    read = raw_input()
    while read != "quit":
        if read == "host":
            tcpServer()
        elif read == "connect":
            print "where?",
            address = raw_input()
            (addr, port) = re.split(':', address)
            tcpClient(addr, port)
        elif read == "name":
            global __uname__
            __uname__ = raw_input()
            #print __uname__
            print "new name set."

        print ">>",
        read = raw_input()

if __name__ == "__main__":
    main()
