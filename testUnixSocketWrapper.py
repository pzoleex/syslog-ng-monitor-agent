import sys
import unittest
import xmlrunner
import os
from UnixSocketWrapper import *


class TestUnixSocketWrapper(unittest.TestCase):

    def setUp(self):
        self.wrapper = UnixSocketWrapper()

    def test_do_command(self):
        result = self.wrapper.do_command("STATS\n")
        self.assertTrue(len(result) > 0)

    def test_not_available_socket(self):
        with self.assertRaises(Exception):
            self.wrapper = UnixSocketWrapper('/tmp/fooo')

if __name__ == "__main__":
    unittest.main(
        testRunner=xmlrunner.XMLTestRunner(output=os.environ.get('WORKSPACE', '/tmp') + '/unittests_junit_dir'))
