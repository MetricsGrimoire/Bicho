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
#         Santiago Dueñas <sduenas@bitergia.com>
#         Alvaro del Castillo <acs@bitergia.com>
#

"""
Parsers for Redmine tracker.
"""

import dateutil.parser

from bicho.exceptions import UnmarshallingError
from bicho.backends.parsers import JSONParser
from bicho.backends.redmine.model import RedmineIdentity


# Tokens
CREATED_ON_TOKEN = 'created_on'
ID_TOKEN = 'id'
FIRSTNAME_TOKEN = 'firstname'
LASTNAME_TOKEN = 'lastname'
LAST_LOGIN_ON_TOKEN = 'last_login_on'
LOGIN_TOKEN = 'login'
MAIL_TOKEN = 'mail'


class RedmineIdentityParser(JSONParser):
    """JSON parser for parsing identities from Redmine.

    :param json: JSON stream containing identities
    :type json: str
    """

    def __init__(self, json):
        JSONParser.__init__(self, json)

    @property
    def identity(self):
        return self._unmarshal()

    def _unmarshal(self):
        return self._unmarshal_identity(self._data)

    def _unmarshal_identity(self, redmine_user):
        try:
            user = redmine_user['user']
            user_id = self._unmarshal_str(user[ID_TOKEN])

            # Unmarshal identity name
            firstname = user[FIRSTNAME_TOKEN]
            lastname = user[LASTNAME_TOKEN]
            name = self._unmarshal_name(firstname, lastname)

            mail = self._unmarshal_str(user[MAIL_TOKEN])
            login = self._unmarshal_str(user[LOGIN_TOKEN])
            created_on = self._unmarshal_timestamp(user[CREATED_ON_TOKEN])
            last_login_on = self._unmarshal_timestamp(user[LAST_LOGIN_ON_TOKEN])

            return RedmineIdentity(user_id, name, mail, login,
                                   created_on, last_login_on)
        except KeyError, e:
            raise UnmarshallingError(instance='RedmineIdentity', cause=repr(e))

    def _unmarshal_name(self, firstname, lastname):
        name = self._unmarshal_str(firstname) + ' ' + self._unmarshal_str(lastname)
        return name

    def _unmarshal_timestamp(self, redmine_ts):
        try:
            str_ts = self._unmarshal_str(redmine_ts)
            return dateutil.parser.parse(str_ts).replace(tzinfo=None)
        except Exception, e:
            raise UnmarshallingError(instance='datetime', cause=repr(e))

    def _unmarshal_str(self, s, not_empty=False):
        if s is None:
            return None
        elif not_empty and s == u'':
            return None
        return unicode(s)
