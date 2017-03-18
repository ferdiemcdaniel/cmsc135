import socket
import select
import sys
import time

class Client:
    def __init__(self, name=None, hostname = None, port = None):
        self.hostname = hostname
        self.port = int(port)
        self.client_socket = socket.socket()
        self.connectService()
        self.name = name
        self.run()

    def command(self, command = None):
        if command[0] == "/list":
            self.client_socket.send("%s" %command[0])
        elif(len(command) != 2):
            print "error"
        else:
            self.client_socket.send("%s %s %s" %(command[0], command[1], self.name))

    def run(self):
        while True:
            socket_list = [sys.stdin, self.client_socket]
            readable, writable, exception = select.select(socket_list, [], [])

            for s in readable:
                if s == self.client_socket:
                    data = s.recv(4096)
                    if not data:
                        print >>sys.stderr, '\ndisconnected from chat server'
                        sys.exit()
                    else:
                        sys.stdout.write(data)
                        sys.stdout.write('[Me] ');
                        sys.stdout.flush()
                else:
                    msg = sys.stdin.readline()
                    if msg.startswith('/'):
                        self.command(msg.split())
                    else:
                        self.client_socket.send("%s: %s" % (self.name,msg))

    def connectService(self):
        print >>sys.stderr, 'connecting to %s port %s' % (self.hostname, self.port)
        self.client_socket.settimeout(2)
        try:
            self.client_socket.connect((self.hostname, self.port))
        except:
            print 'Unable to connect'
            sys.exit()

        print 'Connected to remote host. You can start sending messages'
        sys.stdout.write('[Me] '); sys.stdout.flush()

args = sys.argv
if len(args) != 4:
    print "Insufficient input. Please provide your name, address and port"
    print 'Usage : python basic_client.py your_name hostname port'
    sys.exit();
Client(args[1], args[2], args[3])
