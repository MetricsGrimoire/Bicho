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

import Cookie
import time
import urlparse
from threading import Thread
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler


class MockHTTPHandler(BaseHTTPRequestHandler):
    """HTTP requests handler"""

    def index(self):
        auth = '0'

        if 'Cookie' in self.headers:
            c = Cookie.SimpleCookie(self.headers["Cookie"])
            auth = c['logged'].value

        if auth == '1':
            message = 'Welcome admin'
        else:
            message = 'It works :-)'

        self.send_response(200, 'Ok')
        self.end_headers()
        self.wfile.write(message)

    def fail(self, qs):
        if (not qs) or (not 'error' in qs):
            self.send_error(400, 'Bad request')
        else:
            code = qs['error'][0]

            if code == '404':
                self.send_error(404, 'Not found')
            elif code == '500':
                self.send_error(500, 'Internal server error')
            elif code == '503':
                self.send_error(503, 'Service unavailable')
            elif code == 'timeout':
                time.sleep(self.server.timeout)
            else:
                self.send_error(400, 'Bad request')

    def login(self, qs):
        user, password = self._get_login_data(qs)

        self.send_response(200, 'Ok')

        if user == 'admin' and password == 'admin':
            message = 'Logged in'
            c = Cookie.SimpleCookie()
            c['logged'] = '1'
            self.send_header('Set-Cookie', c.output(header=''))
        else:
            message = 'Not logged in'

        self.end_headers()
        self.wfile.write(message)

    def not_found(self):
        self.send_error(404, 'Not found')

    def do_GET(self):
        parts = urlparse.urlparse(self.path)
        qs = self._parse_GET_query(parts.query)

        if parts.path == '/' or parts.path == '/index.html':
            self.index()
        elif parts.path == '/fail':
            self.fail(qs)
        else:
            self.not_found()

    def do_POST(self):
        parts = urlparse.urlparse(self.path)
        qs = self._parse_POST_query()

        if parts.path == '/login':
            self.login(qs)
        else:
            self.not_found()

    def _parse_GET_query(self, query):
        if not query:
            return None
        return urlparse.parse_qs(query)

    def _parse_POST_query(self):
        length = int(self.headers.getheader('Content-Length'))
        content = self.rfile.read(length)
        return urlparse.parse_qs(content)

    def _get_login_data(self, qs):
        user = None
        password = None

        if 'user' in qs:
            user = qs['user'][0]
        if 'password' in qs:
            password = qs['password'][0]

        return user, password


class MockHTTPServer(Thread, HTTPServer):
    """HTTP server for unit tests"""

    def __init__(self, host, port, filepath, timeout=10):
        HTTPServer.__init__(self, (host, port), MockHTTPHandler)
        Thread.__init__(self)
        self.setDaemon(True)
        self.filepath = filepath
        self.timeout = timeout

    def run(self):
        self.serve_forever()
