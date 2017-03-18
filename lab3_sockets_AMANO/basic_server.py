import socket
import sys

class Server:
    def __init__(self, port = None):
        self.hostname = "localhost"
        self.port = int(port)
        self.server_socket = socket.socket()
        self.server_socket.bind((self.hostname, self.port))
        self.server_socket.listen(5)

    def send(self, message):
        self.socket.connect((self.hostname, self.port))
        self.socket.send(message)

    def accept(self, message):
        return self.socket.connect((self.hostname, self.port))


args = sys.argv
if len(args) != 2:
    print "Insufficient input. Please provide port"
    sys.exit();
serversocket = Server(args[1])
while 1:
    (clientsocket, address) = serversocket.accept()
    ct = client_thread(clientsocket)
