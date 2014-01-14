# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Bitergia
# Copyright (C) 2007-2013 GSyC/LibreSoft, Universidad Rey Juan Carlos
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Authors:
#         Santiago Dueñas <sduenas@libresoft.es>
#

import sys
import unittest

if not '..' in sys.path:
    sys.path.insert(0, '..')

from bicho.exceptions import BichoException, UnmarshallingError


# RegExps for testing exceptions
KEYERROR_INSTANCE_REGEXP = 'instance'
KEYERROR_CAUSE_REGEXP = 'cause'


# Mock classes for testing BichoException base class
class MockSubClassExceptionNoArgs(BichoException):
    message = "Mock exception without args"


class MockSubClassExceptionArgs(BichoException):
    message = "Mock exception with args. Error: %(code)s %(msg)s"


class TestBichoException(unittest.TestCase):

    def test_base_exception_no_args(self):
        e = BichoException()

        self.assertEqual('Unknown error', str(e))
        self.assertEqual(u'Unknown error', unicode(e))

    def test_base_exception_args(self):
        # On this test, arguments are not included in
        # the error message
        e = BichoException(code=404, msg='Not Found')

        self.assertEqual('Unknown error', str(e))
        self.assertEqual(u'Unknown error', unicode(e))

    def test_subclass_exception_no_args(self):
        # Arguments are ignored
        e = MockSubClassExceptionNoArgs(code=404, msg='Not Found')

        self.assertEqual('Mock exception without args', str(e))
        self.assertEqual(u'Mock exception without args', unicode(e))

    def test_subclass_exception_args(self):
        # Arguments are included in the exception message
        e = MockSubClassExceptionArgs(code=404, msg='Not Found')

        self.assertEqual('Mock exception with args. Error: 404 Not Found',
                         str(e))
        self.assertEqual(u'Mock exception with args. Error: 404 Not Found',
                         unicode(e))

    def test_subclass_exception_invalid_args(self):
        # Some arguments required to create the exception message are
        # not given. This raises an KeyError.
        kwargs = {'code' : 404, 'error' : 'Not Found'}
        self.assertRaises(KeyError, MockSubClassExceptionArgs, **kwargs)


class TestUnmarshallingError(unittest.TestCase):

    def test_error_message(self):
        # Make sure that prints the correct error
        e = UnmarshallingError(instance='Identity',
                               cause='Invalid email address')
        self.assertEqual('error unmarshalling object to Identity. Invalid email address',
                         str(e))
        self.assertEqual(u'error unmarshalling object to Identity. Invalid email address',
                         unicode(e))

    def test_no_args(self):
        # Check whether raises a KeyError exception when
        # the required parameters are not given
        kwargs = {}
        self.assertRaisesRegexp(KeyError, KEYERROR_INSTANCE_REGEXP,
                                UnmarshallingError, **kwargs)

        kwargs = {'cause' : 'could not convert Unicode chars'}
        self.assertRaisesRegexp(KeyError, KEYERROR_INSTANCE_REGEXP,
                                UnmarshallingError, **kwargs)

        kwargs = {'instance' : 'MockClass'}
        self.assertRaisesRegexp(KeyError, KEYERROR_CAUSE_REGEXP,
                                UnmarshallingError, **kwargs)


if __name__ == "__main__":
    unittest.main()
