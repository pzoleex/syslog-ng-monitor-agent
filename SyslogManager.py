import os
import tempfile
import socket
from AgentExec import AgentExec
from UnixSocketWrapper import UnixSocketWrapper


class SyslogManager(object):

    def __init__(self, slng_control_socket_path, slng_bin='/usr/sbin/syslog-ng', agent_exec=AgentExec()):
        self.slng_bin = slng_bin
        self.agent_exec = agent_exec
        self.slng_control_socket_path = slng_control_socket_path
        self.slng_control_socket_manager = self.__get_slng_control_socket_manager()

    def get_running_config(self):
        tmp_file = tempfile.NamedTemporaryFile()
        command = [self.slng_bin, "-s", "--preprocess-into=%s" % tmp_file.name]
        try:
            self.agent_exec.run_command(command)
        except OSError, e:
            print("Error during getting config, command: %s, reason: %s" % (command, e))
        result = "".join(tmp_file.readlines())
        tmp_file.close()
        return result

    def get_stats(self):
        if self.slng_control_socket_manager is None:
            self.slng_control_socket_manager = self.__get_slng_control_socket_manager()

        if self.slng_control_socket_manager == None:
            result = "No data\n"
        else:
            result = self.slng_control_socket_manager.do_command('STATS\n')
        return result

    def is_alive(self):
        stats = self.get_stats()
        if 'No data' in stats:
            result = 'no\n'
        else:
            if (len(stats) > 0):
                result = 'yes\n'
            else:
                result = 'no\n'
        return result

    def __get_slng_control_socket_manager(self):
        try:
            slng_control_socket_manager = UnixSocketWrapper(self.slng_control_socket_path)
        except socket.error:
            slng_control_socket_manager = None
        return slng_control_socket_manager
