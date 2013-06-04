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

import sys
import unittest

if not '..' in sys.path:
    sys.path.insert(0, '..')

from Bicho.backends import Backend


# Backends for unit tests
class FakeBackend(Backend):

    def __init__(self):
        super(FakeBackend, self).__init__('FakeBackend')


class UnnamedBackend(Backend):

    def __init__(self):
        super(UnnamedBackend, self).__init__()


class BackendTest(unittest.TestCase):

    def test_backend(self):
        backend = FakeBackend()
        self.assertEqual('FakeBackend', backend.name)

    def test_unnamed_backend(self):
        self.assertRaises(TypeError, UnnamedBackend)

    def test_readonly_properties(self):
        backend = FakeBackend()
        self.assertRaises(AttributeError, setattr, backend, 'name', 'ErrorName')
        self.assertEqual('FakeBackend', backend.name)


if __name__ == "__main__":
    unittest.main()
