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
