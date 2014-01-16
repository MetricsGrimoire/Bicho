# -*- coding: utf-8 -*-
#
# Copyright (C) 2014 Bitergia
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
#         Santiago Dueñas <sduenas@bitergia.com>
#

"""
Redmine's tracker data model.
"""

import datetime

from bicho.common import Identity


class RedmineIdentity(Identity):
    """An identity from Redmine.

    :param user_id: user identifier of the identity
    :type user_id: str
    :param name: name of the identity
    :type name: str
    :param email: email of the identity
    :type email: str
    :param login: nick of the user
    :type login: str
    :param created_on: date when this identity was created
    :type created_on: datetime.datetime
    :param last_login_on: last time this identity logged in
    :type last_login_on: datetime.datetime
    """

    def __init__(self, user_id, name=None, email=None,
                 login=None, created_on=None, last_login_on=None):
        super(RedmineIdentity, self).__init__(user_id, name, email)
        self.login = login
        self.created_on = created_on
        self.last_login_on = last_login_on

    @property
    def created_on(self):
        return self._created_on

    @created_on.setter
    def created_on(self, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError('Parameter "created_on" should be a %s instance. %s given.' %
                            ('datetime', value.__class__.__name__))
        self._created_on = value

    @property
    def last_login_on(self):
        return self._last_login_on

    @last_login_on.setter
    def last_login_on(self, value):
        if value is not None and not isinstance(value, datetime.datetime):
            raise TypeError('Parameter "last_login_on" should be a %s instance. %s given.' %
                            ('datetime', value.__class__.__name__))
        self._last_login_on = value
