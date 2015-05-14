import socket
import sys
import select


class UnixSocketWrapper(object):

    def __init__(self, unix_socket_path='/var/lib/syslog-ng/syslog-ng.ctl'):
        self.unix_socket_path = unix_socket_path
        self.socket = None
        self.socket = self.__connect()

    def __connect(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        print("Connection to %s" % self.unix_socket_path)
        sock.connect(self.unix_socket_path)
        return sock

    def __disconnect(self):
        print("Closing socket")
        self.socket.close()

    def do_command(self, command):
        self.send(command)
        return self.read()

    def send(self, command):
        self.socket.sendall(command)

    def read(self, timeout=3):
        result = ""
        ready = select.select([self.socket], [], [], timeout)[0]
        while (ready):
            result += self.socket.recv(8192)
            ready = select.select([self.socket], [], [], timeout)[0]
        return result

    def __del__(self):
        if self.socket:
            self.__disconnect()
