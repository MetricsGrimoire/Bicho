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
URLs generator for Bugzilla tracker
"""

import urllib
import urlparse

from bicho.exceptions import InvalidBaseURLError


# Bugzilla versions that follow the old style queries
OLD_STYLE_VERSIONS = ['3.2.3', '3.2.2']

# URL suffixes
BUGLIST_SUFFIX = 'buglist.cgi'
LOGIN_SUFFIX = 'index.cgi'
SHOW_ACTIVITY_SUFFIX = 'show_activity.cgi'
SHOW_BUG_SUFFIX = 'show_bug.cgi'

# URL parameters
CHFIELDFROM_PARAM = 'chfieldfrom'
COLUMNLIST_PARAM = 'columnlist'
CTYPE_PARAM = 'ctype'
EXCLUDEFIELD_PARAM = 'excludefield'
ISSUES_ID_PARAM = 'id'
ORDER_PARAM = 'order'
PRODUCT_PARAM = 'product'

# Column list values
COLUMN_ATTACHMENT_DATA = 'attachmentdata'
COLUMN_BUG_ID = 'bug_id'
COLUMN_DATE_NEW_STYLE = 'changeddate'
COLUMN_DATE_OLD_STYLE = 'Last+Changed'

# Content-type values
CTYPE_CSV = 'csv'
CTYPE_XML = 'xml'


class BugzillaURLGenerator(object):
    """Bugzilla's URLs generator

     Builds the different URLs needed for crawling a Bugzilla tracker site.
     Depending on version of the tracker, URLs follow different schemas.
     By default, URLs for 4.x series will be built.

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

    def get_login_url(self):
        return self._get_url(LOGIN_SUFFIX, {})

    def get_metadata_url(self):
        qs = {CTYPE_PARAM : CTYPE_XML}
        return self._get_url(SHOW_BUG_SUFFIX, qs)

    def get_issues_summary_url(self, product=None, from_date=None):
        if self.version in OLD_STYLE_VERSIONS:
            order = COLUMN_DATE_OLD_STYLE
            # TODO: try to check this
            # if from_date is not None:
            #    day = from_date[:from_date.index(' ')]
            #    date = day
        else:
            order = COLUMN_DATE_NEW_STYLE

        qs = {CTYPE_PARAM : CTYPE_CSV,
              ORDER_PARAM : order,
              COLUMNLIST_PARAM : '%s,%s' % (COLUMN_BUG_ID, order)}

        if product:
            qs[PRODUCT_PARAM] = product
        if from_date:
            qs[CHFIELDFROM_PARAM] = from_date

        return self._get_url(BUGLIST_SUFFIX, qs)

    def get_issues_description_url(self, issues):
        if not issues:
            raise ValueError('issues cannot be None or empty')

        qs = {CTYPE_PARAM : CTYPE_XML,
              EXCLUDEFIELD_PARAM : COLUMN_ATTACHMENT_DATA,
              ISSUES_ID_PARAM: issues}
        return self._get_url(SHOW_BUG_SUFFIX, qs)

    def get_activity_url(self, issue_id):
        if not issue_id:
            raise ValueError('issue_id cannot be None or empty')

        qs = {ISSUES_ID_PARAM: issue_id}
        return self._get_url(SHOW_ACTIVITY_SUFFIX, qs)

    def _parse_base_url(self, url):
        if not url:
            msg = 'Empty URL'
            raise InvalidBaseURLError(url=url, cause=msg)

        parts = urlparse.urlparse(url)

        # Possible errors
        if parts.query:
            msg = 'Query parameters found'
            raise InvalidBaseURLError(url=url, cause=msg)
        elif parts.path[-4:] == '.cgi':
            msg = 'URL related to a CGI'
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
        query = urllib.urlencode(qs, True)
        url = urlparse.ParseResult(self._url_parts.scheme, self._url_parts.netloc,
                                   self._url_parts.path + suffix,
                                   None, query, None)
        return url.geturl()
