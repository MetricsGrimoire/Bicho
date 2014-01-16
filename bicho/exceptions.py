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
Common exceptions.
"""

class BichoException(Exception):
    """Base class exception.

    Derived classes can overwrite error message declaring
    'message property.
    """

    message = 'Unknown error'

    def __init__(self, **kwargs):
        super(BichoException, self).__init__(kwargs)
        self.msg = self.message % kwargs

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return unicode(self.msg)


class UnmarshallingError(BichoException):
    """Exception raised when an error is found unmarshalling objects".

    :param instance: type of the instance that was being unmarshalled
    :type instance: str
    :param cause: reason why the exception was raised
    :type cause: str
    """

    message = 'error unmarshalling object to %(instance)s. %(cause)s'


class InvalidBaseURLError(BichoException):
    """"Exception raised when the URL provided as basis is invalid.

    :param url: invalid URL
    :type url: str
    :param cause: reason why the URL is invalid
    :type cause: str
    """

    message = 'error in URL %(url)s. %(cause)s'
