# -*- coding: utf-8 -*-
#
# Copyright (C) 2011-2013 GSyC/LibreSoft, Universidad Rey Juan Carlos
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

"""
Bicho backends framework.

.. note::

   This framework has been taken from Greenwitch project. It's based on
   the code from the book Rytis Sileika's 'Pro Python System Administration'.
"""

import os
import sys


class BackendImportError(Exception):
    """Exception raised when an error occurs importing a backend."""

    def __init__(self, name, error=None):
        if error is not None and not isinstance(error, Exception):
            raise TypeError('expected type Exception in error parameter.')
        self.name = name
        self.error = error

    def __str__(self):
        msg = 'error importing backend %s.' % self.name
        if self.error is not None:
            msg += ' %s' % repr(self.error)
        return msg


class BackendDoesNotExist(Exception):
    """Exception raised when a backend is not found."""

    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'backend %s not found.' % self.name


class Backend(object):
    """Abstract class for backends."""

    def __init__(self, name):
        self._name = name

    @property
    def name(self):
        return self._name


class BackendManager(object):
    """Class for managing backends."""

    def __init__(self, path=None, debug=False):
        self._path = path or os.path.dirname(__file__)
        self._debug = debug
        self._backends = {}
        self._load_backends()

    @property
    def backends(self):
        return self._backends.keys()

    @property
    def debug(self):
        return self._debug

    @property
    def path(self):
        return self._path

    def get(self, name):
        try:
            return self._backends[name]
        except KeyError:
            raise BackendDoesNotExist(name)

    def _load_backends(self):
        backends = self._find_backends()
        for backend in backends:
            b = backend()
            self._backends[b.name] = b

    def _find_backends(self):
        filenames = [fn for fn in os.listdir(self._path)]
        candidates = [fn for fn in filenames \
                      if os.path.isdir(os.path.join(self._path, fn))]
        backends = self._import_backends(candidates)
        return backends

    def _import_backends(self, candidates):
        if not self._path in sys.path:
            sys.path.append(self._path)

        for candidate in candidates:
            try:
                __import__(candidate)
            except Exception, e:
                ex = BackendImportError(candidate, e)

                if self._debug:
                    raise ex
                else:
                    print ex

        # Checks whether the backends were imported from the
        # given modules
        backends = [b for b in Backend.__subclasses__()
                    if b.__module__ in candidates]
        return backends
