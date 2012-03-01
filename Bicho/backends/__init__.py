# Copyright (C) 2011 GSyC/LibreSoft, Universidad Rey Juan Carlos
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# Authors: Daniel Izquierdo Cortazar <dizquierdo@gsyc.escet.urjc.es>
#

import os
import glob

__all__ = ['Backend']

class BackendUnknownError (Exception):
    '''Unkown engine type'''


class Backend:

    _backends = {}

    @staticmethod
    def register_backend (backend_name, backend_class):
        Backend._backends[backend_name] = backend_class

    @staticmethod
    def _get_backend (backend_name):
        if backend_name not in Backend._backends:
            try:
                __import__ ('Bicho.backends.%s' % backend_name)
            except ImportError:
                raise

        if backend_name not in Backend._backends:
            raise BackendUnknownError ('Backend type %s not registered' % backend_name)
    
        return Backend._backends[backend_name]
    
    @staticmethod
    def create_backend (backend_name):
        backend_class = Backend._get_backend (backend_name)
        return backend_class ()
    
    @staticmethod
    def get_all_backends ():
        # we should clean this directory
        backends = []
        not_backends = ('HTMLParser.py', 'HTMLUtils.py', '__init__.py')
        for fname in glob.glob( os.path.join(os.path.dirname(__file__), '*.py') ):
            if os.path.basename(fname) not in not_backends:
                backends.append(os.path.basename(fname))
        return backends