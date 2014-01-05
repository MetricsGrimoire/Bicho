# -*- coding: utf-8 -*-
#
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

from bicho.backends.downloader import ConnectionError, TimeoutError, HTTPError,\
    HTTPDownloadManager
from mock_http_server import MockHTTPServer


# HTTP server configuration
HTTP_HOST = 'localhost'
HTTP_PORT = 8000
TEST_FILES_DIRNAME = '/tmp'
TIMEOUT = 5


class TestConnectionError(unittest.TestCase):

    def test_type(self):
        # Check whether raises a TypeError exception when
        # is not given an Exception class as third parameter
        self.assertRaises(TypeError, ConnectionError, False)

    def test_error_message(self):
        # Make sure that prints the correct error
        e = ConnectionError()
        self.assertEqual('connection error.', str(e))

        e = ConnectionError(Exception())
        self.assertEqual('connection error. Exception()', str(e))


class TestTimeoutError(unittest.TestCase):

    def test_error_message(self):
        # Make sure that prints the correct error
        e = TimeoutError()
        self.assertEqual('timed out.', str(e))


class TestHTTPError(unittest.TestCase):

    def test_error_message(self):
        # Make sure that prints the correct error
        e = HTTPError('404', 'Not found')
        self.assertEqual('Error 404: Not found.', str(e))


class TestDownloadManager(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.httpd = MockHTTPServer(HTTP_HOST, HTTP_PORT, TEST_FILES_DIRNAME)
        cls.httpd.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def test_get(self):
        # Test if the manager can download a web page
        manager = HTTPDownloadManager()

        response = manager.get('http://localhost:8000/index.html')
        self.assertEqual('It works :-)', response)
        response = manager.get('http://localhost:8000/')
        self.assertEqual('It works :-)', response)

    def test_404_error(self):
        # Test if it raises a 404 error
        manager = HTTPDownloadManager()
        self.assertRaisesRegexp(HTTPError, 'Error 404: Not found', manager.get,
                                url='http://localhost:8000/fail?error=404')

    def test_500_error(self):
        # Test if it raises a 500 error
        manager = HTTPDownloadManager()
        self.assertRaisesRegexp(HTTPError, 'Error 500: Internal server error', manager.get,
                                url='http://localhost:8000/fail?error=500')

    def test_503_error(self):
        # Test if it raises a 503 error
        manager = HTTPDownloadManager()
        self.assertRaisesRegexp(HTTPError, 'Error 503: Service unavailable', manager.get,
                                url='http://localhost:8000/fail?error=503')

    def test_timeout_error(self):
        # Test if an exception is raised when there is a time out in
        # the connection
        # Set the default socket timeout
        import socket
        socket.setdefaulttimeout(TIMEOUT)

        manager = HTTPDownloadManager()
        self.assertRaisesRegexp(TimeoutError, 'timed out', manager.get,
                                url='http://localhost:8000/fail?error=timeout')

        # Reset to default
        socket.setdefaulttimeout(None)

    def test_connection_error(self):
        # Test if an exception is raised when an error is found
        # during the connection
        manager = HTTPDownloadManager()
        self.assertRaisesRegexp(ConnectionError, 'connection error. URLError', manager.get,
                                url='http://localhost:9000/fail?error=timeout')

    def test_login(self):
        # Test if the login process works
        manager = HTTPDownloadManager()
        response = manager.login('http://localhost:8000/login',
                                 user='admin', password='admin')
        self.assertEqual('Logged in', response)
        response = manager.get('http://localhost:8000/')
        self.assertEqual('Welcome admin', response)

    def test_login_invalid_params(self):
        # Test if the login process works 
        manager = HTTPDownloadManager()
        response = manager.login('http://localhost:8000/login',
                                 user='user', password='password')
        self.assertEqual('Not logged in', response)
        response = manager.get('http://localhost:8000/')
        self.assertEqual('It works :-)', response)


if __name__ == '__main__':
    unittest.main()
