from subprocess import check_output


class AgentExec(object):

    def run_command(self, cmd=[]):
        return check_output(cmd)
