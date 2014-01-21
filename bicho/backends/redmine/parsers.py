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

from bicho.common import IssueSummary
from bicho.exceptions import UnmarshallingError
from bicho.backends.parsers import JSONParser
from bicho.backends.redmine.model import RedmineIdentity, RedmineStatus, RedmineIssuesSummary


# Tokens
CREATED_ON_TOKEN = 'created_on'
ID_TOKEN = 'id'
ISSUES_TOKEN = 'issues'
ISSUE_STATUSES_TOKEN = 'issue_statuses'
IS_CLOSED_TOKEN = 'is_closed'
IS_DEFAULT_TOKEN = 'is_default'
FIRSTNAME_TOKEN = 'firstname'
LASTNAME_TOKEN = 'lastname'
LAST_LOGIN_ON_TOKEN = 'last_login_on'
LIMIT_TOKEN = 'limit'
LOGIN_TOKEN = 'login'
MAIL_TOKEN = 'mail'
NAME_TOKEN = 'name'
TOTAL_COUNT_TOKEN = 'total_count'
OFFSET_TOKEN = 'offset'
UPDATED_ON_TOKEN = 'updated_on'


class RedmineIdentityParser(JSONParser):
    """JSON parser for parsing identities from Redmine.

    :param json: JSON stream containing identities
    :type json: str
    """

    def __init__(self, json):
        super(RedmineIdentityParser, self).__init__(json)

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


class RedmineStatusesParser(JSONParser):
    """JSON parser for parsing available statuses on Redmine.

    :param json: JSON stream with a list of statuses
    :type json: str
    """

    def __init__(self, json):
        super(RedmineStatusesParser, self).__init__(json)

    @property
    def statuses(self):
        return self._unmarshal()

    def _unmarshal(self):
        try:
            issue_statuses = self._data[ISSUE_STATUSES_TOKEN]
            return [self._unmarshal_status(status)\
                    for status in issue_statuses]
        except KeyError, e:
            raise UnmarshallingError(instance='list(RedmineStatus)', cause=repr(e))

    def _unmarshal_status(self, status):
        try:
            status_id = self._unmarshal_str(status[ID_TOKEN])
            name = self._unmarshal_str(status[NAME_TOKEN])

            if IS_CLOSED_TOKEN in status:
                is_closed = status[IS_CLOSED_TOKEN]
            else:
                is_closed = False

            if IS_DEFAULT_TOKEN in status:
                is_default = status[IS_DEFAULT_TOKEN]
            else:
                is_default = False

            return RedmineStatus(status_id, name, is_closed, is_default)
        except KeyError, e:
            raise UnmarshallingError(instance='RedmineStatus', cause=repr(e))

    def _unmarshal_str(self, s, not_empty=False):
        if s is None:
            return None
        elif not_empty and s == u'':
            return None
        return unicode(s)


class RedmineIssuesSummaryParser(JSONParser):
    """JSON parser for parsing a summary of issues.

    :param json: JSON stream with a list of issues
    :type json: str
    """

    def __init__(self, json):
        super(RedmineIssuesSummaryParser, self).__init__(json)

    @property
    def summary(self):
        return self._unmarshal()

    def _unmarshal(self):
        try:
            # Unmarshal metadata
            total_count = self._unmarshal_str(self._data[TOTAL_COUNT_TOKEN])
            offset = self._unmarshal_str(self._data[OFFSET_TOKEN])
            limit = self._unmarshal_str(self._data[LIMIT_TOKEN])

            # Unmarshal issues summary
            issues_summary = self._unmarshal_summary(self._data[ISSUES_TOKEN])

            # Create summary instance
            summary = RedmineIssuesSummary(total_count, offset, limit)

            for issue_summary in issues_summary:
                summary.add_summary(issue_summary)

            return summary
        except KeyError, e:
            raise UnmarshallingError(instance='RedmineIssuesSummary', cause=repr(e))

    def _unmarshal_summary(self, redmine_issues):
        return [self._unmarshal_issue_summary(redmine_issue)
                for redmine_issue in redmine_issues]

    def _unmarshal_issue_summary(self, redmine_issue):
        try:
            issue_id = self._unmarshal_str(redmine_issue[ID_TOKEN])
            changed_on = self._unmarshal_timestamp(redmine_issue[UPDATED_ON_TOKEN])
            return IssueSummary(issue_id, changed_on)
        except KeyError, e:
            raise UnmarshallingError(instance='IssueSummary', cause=repr(e))

    def _unmarshal_str(self, s, not_empty=False):
        if s is None:
            return None
        elif not_empty and s == u'':
            return None
        return unicode(s)

    def _unmarshal_timestamp(self, redmine_ts):
        try:
            str_ts = self._unmarshal_str(redmine_ts)
            return dateutil.parser.parse(str_ts).replace(tzinfo=None)
        except Exception, e:
            raise UnmarshallingError(instance='datetime', cause=repr(e))
