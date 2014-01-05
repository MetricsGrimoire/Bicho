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
#         Luis Cañas Díaz <lcanas@libresoft.es>
#

"""
HTTP download manager
"""

import cookielib
import socket
import urllib
import urllib2


class ConnectionError(Exception):
    """Exception raised when an connection error is found"""

    def __init__(self, error=None):
        if error is not None and not isinstance(error, Exception):
            raise TypeError('expected type Exception in error parameter.')
        self.error = error

    def __str__(self):
        msg = 'connection error.'
        if self.error is not None:
            msg += ' %s' % repr(self.error)
        return msg


class TimeoutError(ConnectionError):
    """Exception raised when a timeout occurs on the connection"""

    def __init__(self):
        ConnectionError.__init__(self)

    def __str__(self):
        return 'timed out.'


class HTTPError(Exception):
    """Exception raised when a HTTP response with a code error arrives"""

    def __init__(self, code, msg):
        self.code = code
        self.msg = msg

    def __str__(self):
        return 'Error %s: %s.' % (self.code, self.msg)


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
            raise HTTPError(e.code, e.msg)
        except urllib2.URLError, e:
            raise ConnectionError(e)
        except socket.timeout:
            raise TimeoutError()
