#!/usr/bin/env python
# vim: sts=4 ts=8 et ai

"""#################################################################
This program is free software: you can redistribute it and/or modify

it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
##################################################################"""

import socket
from optparse import OptionParser, OptionGroup
from SyslogManager import SyslogManager
import ssl
import os
import signal
import sys

accepted_commands = ['stats', 'show_config', 'is_alive']


def do_command(command):
    result = None
    print("Executing command: %s" % command)
    if command not in accepted_commands:
        result = "Unknown command: %s\n" % command
    else:
        print("Executing command: %s" % command)
        if command == 'stats':
            result = syslog_manager.get_stats()
        elif command == 'show_config':
            result = syslog_manager.get_running_config()
        elif command == 'is_alive':
            result = syslog_manager.is_alive()
    return result


def deal_with_client(ssl_stream):
    data = ssl_stream.read()
    while data:
        if not process_data(ssl_stream, data):
            break
        data = ssl_stream.read()


def process_data(ssl_stream, data):
    result = do_command(data.strip())
    ssl_stream.sendall(result)
    return False


def server_certs_exist():
    if not os.path.isfile(opts.server_cert) or not os.path.isfile(opts.server_key):
        parser.error("server cert and key are required but do not exist, for more information see --help")
        return False
    return True

def signal_handler(signal, frame):
    print('You pressed Ctrl+C, exiting')
    sys.exit(0)

if __name__ == "__main__":
    global syslog_manager
    signal.signal(signal.SIGINT, signal_handler)
    usage = "usage: %prog listen_ip [options]"
    version = "1.0"
    parser = OptionParser(usage, version=version)
    parser.add_option("-p", "--port", help="port to listen, default: 2121", dest="port", default=2121)
    parser.add_option("-u", "--unix-socket", help="unix socket path of syslog-ng, default: /var/lib/syslog-ng/syslog-ng.ctl",
                      dest="unix_socket_path", default="/var/lib/syslog-ng/syslog-ng.ctl")
    parser.add_option("-b", "--syslog-bin", help="the path of the syslog-ng bin, default: /usr/sbin/syslog-ng", dest="slng_bin", default="/usr/sbin/syslog-ng")

    parser.add_option("-c", "--cert", help="server cert, default: server-cert.pem", dest="server_cert", default="server-cert.pem")
    parser.add_option("-k", "--key", help="server key, default: server-key.pem", dest="server_key", default="server-key.pem")
    parser.add_option("-a", "--ca-cert", help="server CA cert, default: cacert.pem", dest="ca_cert", default="cacert.pem")
    parser.add_option("-n", "--no-validate-cert", help="don't validate the client certificate. Default: validate ",
                      action="store_false", dest="validate", default=True)

    (opts, args) = parser.parse_args()

    ip = ''
    if len(args) > 0:
        ip = args[0]

    if not server_certs_exist():
        sys.exit(1)

    bindsocket = socket.socket()
    bindsocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    bindsocket.bind((ip, opts.port))
    bindsocket.listen(5)

    syslog_manager = SyslogManager(opts.unix_socket_path, opts.slng_bin)

    print("Press CTRL+C to exit")
    while True:
        try:
            newsocket, fromaddr = bindsocket.accept()
            print("Incoming connection from %s" % str(fromaddr))

            cert_reqs = ssl.CERT_NONE
            ca_certs = None
            if opts.validate:
                cert_reqs = ssl.CERT_REQUIRED
                ca_certs = opts.ca_cert

            ssl_stream = ssl.wrap_socket(
                newsocket, server_side=True, certfile=opts.server_cert, keyfile=opts.server_key, cert_reqs=cert_reqs, ca_certs=ca_certs)
            try:
                deal_with_client(ssl_stream)
            finally:
                print("Connection closing to %s" % str(fromaddr))
                ssl_stream.shutdown(socket.SHUT_RDWR)
                ssl_stream.close()
        except ssl.SSLError, e:
            print("SSL error, closing connection, reason: %s" % e)
            newsocket.shutdown(socket.SHUT_WR)
        except Exception, e:
            print("Exception in main thread, ignoring. Reason: %s" % e)
