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
#         Luis Cañas Díaz <lcanas@libresoft.es>
#

"""
HTTP download manager
"""

import cookielib
import socket
import urllib
import urllib2

from bicho.exceptions import BichoException


class ConnectionError(BichoException):
    """Exception raised when an connection error is found.

    :param error: cause of the error
    :type error: str
    """
    message = 'connection error. %(error)s.'


class TimeoutError(ConnectionError):
    """Exception raised when a timeout occurs on the connection."""
    message = 'timed out.'


class HTTPError(BichoException):
    """Exception raised when a HTTP response with a code error arrives.

    :param code: code error
    :type code: str
    :param message: error message
    :type message: str
    """
    message = 'Error %(code)s: %(message)s.'


class HTTPDownloadManager(object):
    """Manager for downloading contents from a site using the HTTP protocol"""

    def __init__(self):
        self.opener = self._init_opener()

    def login(self, url, **kargs):
        """Authenticates the manager in a website

        :param url: URL used to log in
        :type: str
        :param args: login parameters
        :type args: dict

        :returns: the contents from the login URL
        :rtype: str

        :raise HTTPError: when a HTTP response with a code error arrives
        :raise TimeoutError: when a timeout occurs
        :raise ConnectionError: when an error is found during the connection

        :TODO: how to know if the login procedure succeed
        """
        params = urllib.urlencode(kargs)
        request = urllib2.Request(url, params)
        return self._open(request)

    def get(self, url):
        """Get the contents from the given URL

        :param url: network object to open
        :type url: str

        :returns: the contents from the URL
        :rtype: str

        :raise HTTPError: when a HTTP response with a code error arrives
        :raise TimeoutError: when a timeout occurs
        :raise ConnectionError: when an error is found during the connection
        """
        return self._open(url)

    def _init_opener(self):
        """Initialize a connection handler"""
        # Create cookies handler
        cj = cookielib.CookieJar()
        ch = urllib2.HTTPCookieProcessor(cj)

        # Set the cookies handler
        opener = urllib2.build_opener(ch)
        urllib2.install_opener(opener)
        return opener

    def _open(self, url_or_request):
        """Open a URL and get its contents

        :param url_or_request: URL to open or HTTP request to send
        :type url_or_request: str or urllib2.Request

        :returns: the contents from the URL
        :rtype: str

        :raise HTTPError: when a HTTP response with a code error arrives
        :raise TimeoutError: when a timeout occurs
        :raise ConnectionError: when an error is found during the connection
        """
        assert(isinstance(url_or_request, str) or
               isinstance(url_or_request, urllib2.Request))

        try:
            response = urllib2.urlopen(url_or_request)
            return response.read()
        except urllib2.HTTPError, e:
            raise HTTPError(code=e.code, message=e.msg)
        except urllib2.URLError, e:
            raise ConnectionError(error=repr(e))
        except socket.timeout:
            raise TimeoutError()
