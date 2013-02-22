# -*- coding: utf-8 -*-
#
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
# Authors:
#       Daniel Izquierdo Cortazar <dizquierdo@libresoft.es>
#       Luis Cañas Díaz <lcanas@libresoft.es>
#       Santiago Dueñas <sduenas@libresoft.es>
#       Alvaro del Castillo <acs@bitergia.com>
#

import pprint
import sys

from Config import Config, ErrorLoadingConfig, InvalidConfig

from backends import Backend
from utils import printerr, printdbg

from post_processing import IssueLogger


def main():
    """
    """
    # Note: Default values for options are defined on
    # configuration module
    usage = 'Usage: %prog [options]'

    try:
        Config.set_config_options(usage)
    except (ErrorLoadingConfig, InvalidConfig), e:
        printerr(str(e))
        sys.exit(2)

    try:
        backend = Backend.create_backend(Config.backend)
    except ImportError, e:
        printerr("Backend ''" + Config.backend + "'' not exists. " + str(e))
        sys.exit(2)
    printdbg("Bicho object created, options and backend initialized")
    backend.run()

    try:
        ilogger = IssueLogger.create_logger(Config.backend)
    except ImportError, e:
        printerr("Logger ''" + Config.backend + "'' doesn't exist. " + str(e))
        sys.exit(2)
    printdbg("Bicho logger object created")
    ilogger.run()

if __name__ == "__main__":
    main()
