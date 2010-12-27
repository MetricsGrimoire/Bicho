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

__all__ = [
    'Backend',
    'create_backend',
    'register_backend'
]

class BackendUnknownError (Exception):
    '''Unkown engine type'''


class Backend:

    def __init__ (self):
        pass
        #self.url = None

#    def set_url (self, url):
#        self.url = url
        
    def run (self):
        raise NotImplementedError

_backends = {}
def register_backend (backend_name, backend_class):
    _backends[backend_name] = backend_class

def _get_backend (backend_name):
    if backend_name not in _backends:
        try:
            __import__ ('Bicho.backends.%s' % backend_name)
        except ImportError:
            raise

    if backend_name not in _backends:
        raise BackendUnknownError ('Backend type %s not registered' % backend_name)

    return _backends[backend_name]

def create_backend (backend_name):
    backend_class = _get_backend (backend_name)
    return backend_class ()
