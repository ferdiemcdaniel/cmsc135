import socket
import sys
import select
import Queue

SOCKET_LIST = dict()
CHANNELS = []

class Server:
    def __init__(self, port = None):
        self.hostname = "localhost"
        self.port = int(port)
        self.message_queues = {}
        self.server_socket = socket.socket()
        self.server_socket.setblocking(0)
        self.server_socket.bind((self.hostname, self.port))
        self.server_socket.listen(5)
        self.setupSelect()
        self.run()

    def setupSelect(self):
        self.inputs = [ self.server_socket ]
        self.outputs = []
        self.READ_ONLY = select.POLLIN | select.POLLPRI | select.POLLHUP | select.POLLERR
        self.READ_WRITE = self.READ_ONLY | select.POLLOUT
        self.poller = select.poll()
        self.poller.register(self.server_socket,self.READ_ONLY)
        self.fd_to_socket = { self.server_socket.fileno(): self.server_socket}

    def broadcast (self, server_socket, sock, group, message):
        for key in SOCKET_LIST:
            value = SOCKET_LIST[key]
            if value["connection"] != server_socket and value["connection"] != sock and value["channel"] == group:
                try :
                    value["connection"].send(message)
                except :
                    value.close()
                    if value in SOCKET_LIST:
                        del SOCKET_LIST[value["connection"][1]]

    def create(self, group, name, connection):
        if not group in CHANNELS:
            CHANNELS.append(group)
            connection.send("\rSuccessfully created channel %s\n"% group)
            SOCKET_LIST[connection.getpeername()[1]]["channel"] = group
            SOCKET_LIST[connection.getpeername()[1]]["name"] = name

    def list(self, connection):
        if len(CHANNELS) > 0:
            msg = "\n".join(CHANNELS) + "\n"
        else:
            msg = "no channels available yet\n"
        connection.send(msg)

    def join(self, group, name, connection):
        print connection.getpeername()[1]
        if group in CHANNELS:
            if SOCKET_LIST[connection.getpeername()[1]]["channel"] == group:
                connection.send("\nYou're already in that channel\n")
            else:
                SOCKET_LIST[connection.getpeername()[1]]["channel"] = group
                SOCKET_LIST[connection.getpeername()[1]]["name"] = name
                connection.send("\rSuccesfully joined channel %s\n"% group)
                self.broadcast(self.server_socket, connection, group, "%s has joined this channel\n" % name)

    def execute_command(self, command, s):
        args = command.split()
        if("create" in args[0]):
            self.create(args[1],args[2],s)
        elif("join" in args[0]):
            self.join(args[1],args[2], s)
        elif("list" in args[0]):
            self.list(s)

    def run(self):
        while True:
            print >>sys.stderr, '\nwaiting for the next event'
            timeout = 1000
            events = self.poller.poll(timeout)
            for fd, flag in events:
                s = self.fd_to_socket[fd]

                if flag & (select.POLLIN | select.POLLPRI):
                    if s is self.server_socket:
                        connection, client_address = self.server_socket.accept()
                        SOCKET_LIST[client_address[1]] = {"connection": connection, "channel": ""}
                        print >>sys.stderr, 'new connection from', client_address
                        connection.setblocking(0)
                        self.fd_to_socket[ connection.fileno() ] = connection
                        self.poller.register(connection, self.READ_ONLY)
                        self.message_queues[connection] = Queue.Queue()
                    else:
                        data = s.recv(4096)
                        if data:
                            print >>sys.stderr,  'received "%s" from %s' % (data, s.getpeername())
                            if(data.startswith('/')):
                                self.execute_command(data,s)
                            else:
                                if not SOCKET_LIST[s.getpeername()[1]]["channel"] == "":
                                    self.broadcast(self.server_socket, s, SOCKET_LIST[s.getpeername()[1]]["channel"], "\r" +  data)
                                else:
                                    s.send("Please join a channel or create one\n")
                        else:
                            print >>sys.stderr, 'closing', client_address, 'after reading no data'
                            if s in SOCKET_LIST:
                                SOCKET_LIST.remove(s)
                            self.broadcast(self.server_socket, s, SOCKET_LIST[s.getpeername()[1]]["channel"], "\r %s has left\n" % SOCKET_LIST[s.getpeername()[1]]["name"])
                            self.poller.unregister(s)
                            s.close()

                            del self.message_queues[s]

                elif flag & select.POLLHUP:
                    print >>sys.stderr, 'closing', client_address, 'after receiving HUP'
                    self.poller.unregister(s)
                    s.close()

                elif flag & select.POLLERR:
                    print >>sys.stderr, 'handling exceptional condition for', s.getpeername()
                    self.poller.unregister(s)
                    s.close()

                    del self.messages_queues[s]

    

args = sys.argv
if len(args) != 2:
    print "Insufficient input. Please provide a port"
    print 'Usage : python basic_server.py port'
    sys.exit();
Server(args[1]);
