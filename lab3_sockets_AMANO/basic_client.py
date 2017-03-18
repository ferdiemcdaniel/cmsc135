import socket
import sys

class Client:
    def __init__(self, hostname = None, port = None):
        self.hostname = hostname
        self.port = int(port)

    def send(self, message):
        self.socket.connect((self.hostname, self.port))
        self.socket.send(message)


args = sys.argv
if len(args) != 3:
    print "Insufficient input. Please provide address and port"
    sys.exit();
client = Client(args[1], args[2])
msg = raw_input()
client.send(msg)
