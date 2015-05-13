import socket
import sys
from optparse import OptionParser, OptionGroup
import signal
import select
import time
from threading import Thread
import os
import re
import SocketServer
import threading
from UnixSocketWrapper import UnixSocketWrapper

STOP_ALL_THREADS = False
ACCEPTED_COMMANDS = ['stats']

usage = "usage: %prog"
version = "1.0"
parser = OptionParser(usage, version=version)
parser.add_option("-v", "--verbose", help = "Verbose mode", action="store_true", dest="verbose", default=False)

(opts, args) = parser.parse_args()

unix_socket = None
accepted_commands = ['stats']

class ThreadedTCPRequestHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        while (True and not STOP_ALL_THREADS):
            readable, writable, errored = select.select([self.request], [], [], 1)
            if (readable):
                try:
                    command = self.request.recv(1024)
                except socket.error:
                    pass
                if command:
                    result = do_command(command.strip())
                    if result is not None:
                        self.request.sendall(result)
                else:
                    self.request.close()
                    return
        self.request.close()

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass

def do_command(command):
    global unix_socket
    result = None
    if command == 'stats':
        if unix_socket is None:
            unix_socket = UnixSocketWrapper()
        result = unix_socket.do_command('STATS\n')
    return result

def signal_handler(signal, frame):
    global STOP_ALL_THREADS
    print('You pressed Ctrl+C, exiting')
    STOP_ALL_THREADS = True
    server.shutdown()
    sys.exit(0)
    
if __name__ == "__main__":
    global server
    signal.signal(signal.SIGINT, signal_handler)
    
    print("Press CTRL+C to exit")

    server = ThreadedTCPServer(('', 1219), ThreadedTCPRequestHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    server_thread.daemon = True
    server_thread.start()
    while (True):
        time.sleep(1)
