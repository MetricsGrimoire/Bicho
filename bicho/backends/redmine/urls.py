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
#

"""
URLs generator for Redmine tracker
"""

import urlparse
import urllib

from bicho.exceptions import InvalidBaseURLError


# URL suffixes
ISSUES_SUFFIX = 'issues'
JSON_SUFFIX = '.json'
PROJECT_SUFFIX = 'projects/'
STATUSES_SUFFIX = 'issue_statuses'
USERS_SUFFIX = 'users/'

# URL parameters
INCLUDE_PARAM = 'include'
PAGE_PARAM = 'page'
SORT_PARAM = 'sort'
STATUS_PARAM = 'status_id'
UPDATED_ON_PARAM = 'updated_on'

# Values
JOURNALS_VALUE = 'journals'
UPDATED_ON_VALUE = 'updated_on'
STATUS_VALUE = '*'


class RedmineURLGenerator(object):
    """Redmine's URLs generator

     Builds the different URLs needed for crawling a Redmine tracker site.

    :param base_url: URL used to build requested specific URLs
    :type base_url: str
    :param version: version of the tracker
    :type version: str

    :raise InvalidBaseURLError: when base_url parameter is not valid
    """
    def __init__(self, base_url, version=None):
        self.base_url = base_url
        self.version = version

    @property
    def base_url(self):
        return self._url_parts.geturl()

    @base_url.setter
    def base_url(self, value):
        self._url_parts = self._parse_base_url(value)

    def get_issues_summary_url(self, product=None, from_date=None, page=None):
        qs = {STATUS_PARAM: STATUS_VALUE,
              SORT_PARAM: UPDATED_ON_VALUE}

        if product:
            suffix = PROJECT_SUFFIX + product + '/' + ISSUES_SUFFIX + JSON_SUFFIX
        else:
            suffix = ISSUES_SUFFIX + JSON_SUFFIX

        if from_date:
            qs[UPDATED_ON_PARAM] = '>=' + from_date
        if page:
            qs[PAGE_PARAM] = page

        return self._get_url(suffix, qs)

    def get_issue_url(self, issue_id):
        if not issue_id:
            raise ValueError('issue_id cannot be None or empty')

        qs = {INCLUDE_PARAM: JOURNALS_VALUE}

        suffix = ISSUES_SUFFIX + '/' + issue_id + JSON_SUFFIX

        return self._get_url(suffix, qs)

    def get_statuses_url(self):
        suffix = STATUSES_SUFFIX + JSON_SUFFIX
        return self._get_url(suffix, {})

    def get_user_url(self, user_id):
        if not user_id:
            raise ValueError('user_id cannot be None or empty')
        suffix = USERS_SUFFIX + user_id + JSON_SUFFIX
        return self._get_url(suffix, {})

    def _parse_base_url(self, url):
        if not url:
            msg = 'Empty URL'
            raise InvalidBaseURLError(url=url, cause=msg)

        parts = urlparse.urlparse(url)

        # Possible errors
        if parts.query:
            msg = 'Query parameters found'
            raise InvalidBaseURLError(url=url, cause=msg)
        elif parts.path[-5:] == '.json':
            msg = 'URL related to a JSON'
            raise InvalidBaseURLError(url=url, cause=msg)

        # Add trailing slash to avoid future problems joining paths with
        # urljoin function. Without this slash, the path of the base URL
        # will be ignored and overwritten by the second parameter in urljoin.
        path = parts.path
        if parts.path[-1] != '/':
            path = parts.path + '/'

        parts = urlparse.ParseResult(parts.scheme, parts.netloc, path,
                                     None, None, None)
        return parts

    def _get_url(self, suffix, qs):
        if qs is None:
            qs = {}
        query = urllib.urlencode(qs, True)
        url = urlparse.ParseResult(self._url_parts.scheme, self._url_parts.netloc,
                                   self._url_parts.path + suffix,
                                   None, query, None)
        return url.geturl()
