# Copyright (C) 2007  GSyC/LibreSoft
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

from storm.locals import *
import Bug

class SqlBug (object):
    __storm_table__ = "Bugs"
    
    id = Int ()
    Summary = Unicode ()
    Description = Unicode()
    DateSubmitted = DateTime()
    Status = Int ()
    Priority = Int ()
    Category = Unicode ()
    Group = Unicode ()
    AssignedTo = Unicode ()
    SubmittedBy = Unicode ()
    
    def __init__ (self, bug):
        id = bug.id
        Summary = bug.Summary 
        Description = bug.Description 
        DateSubmitted = bug.DateSubmitted 
        Status = bug.Status 
        Priority = bug.Priority 
        Category = bug.Category 
        Group = bug.Group 
        AssignedTo = bug.AssignedTo 
        SubmittedBy = bug.SubmittedBy 
 
    
##    Table must be like next:

##    "CREATE TABLE  `Prueba_Bicho`.`Bugs` (" + 
##    "`id` int(11) NOT NULL auto_increment," + 
##    "`Summary` tinytext NOT NULL," + 
##    "`Description` tinytext NOT NULL,"+
##    "`DateSubmitted` datetime NOT NULL,"+
##    "`Status` varchar(64) NOT NULL,"+
##    "`Priority` varchar(64) NOT NULL,"+
##    "`Category` varchar(128) NOT NULL,"+
##    "`Group` varchar(128) NOT NULL,"+
##    "`AssignedTo` varchar(128) NOT NULL,"+
##    "`SubmittedBy` varchar(128) NOT NULL,"+
##    "PRIMARY KEY  (`id`)"+
##    ") ENGINE=InnoDB DEFAULT CHARSET=latin1")

    
