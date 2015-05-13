import socket, sys, select

class UnixSocketWrapper(object):
    def __init__(self, unix_socket_path = '/opt/syslog-ng/var/run/syslog-ng.ctl'):
        self.unix_socket_path = unix_socket_path
        self.socket = self.__connect()

    def __connect(self):
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        print("Connection to %s" % self.unix_socket_path)
        try:
            sock.connect(self.unix_socket_path)
        except socket.error, msg:
            raise Exception("Unable to connect, reason: %s", msg)
        return sock

    def __disconnect(self):
        print("Closing socket")
        self.socket.close()

    def do_command(self, command):
        print("Executing command: %s" % command)
        self.send(command)
        return self.read()

    def send(self, command):
        print("Command sent: %s" % command)
        self.socket.sendall(command)

    def read(self):
        result = ""
        ready = select.select([self.socket], [], [], 1)[0]
        while (ready):
            result += self.socket.recv(8192)
            ready = select.select([self.socket], [], [], 1)[0]
        return result

    def __del__(self):
        if self.socket:
            self.__disconnect()
