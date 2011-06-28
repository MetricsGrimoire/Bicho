2011-06-27  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/backends/sf.py: Fix #296  Import statement for dateutils moved to
  top.

2011-06-24  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/info.py, NEWS, debian/changelog, debian/control, setup.py: Update
  information about project in Debian files and NEWS

  * Bicho/db/database.py: Fix #294 - Duplicate entry in issues_watchers

2011-06-17  Juan Francisco Gato Luis <jfcogato@libresoft.es>

  * Bicho/backends/jira.py: fixed bug parsing security in extra data for jira

  * Bicho/backends/jira.py: fixed bug with description tags

2011-06-14  Juan Francisco Gato Luis <jfcogato@libresoft.es>

  * Bicho/db/database.py: fixed bugs about incremental support, now we control
  if data is stored or not to add new one

2011-06-13  Luis Cañas Díaz <lcanas@libresoft.es>

  * debian/bicho.1, debian/changelog, debian/control, debian/copyright,
  debian/rules, doc/bicho.1, setup.py: Fix the errors in the Debian files  Fix
  the Debian packaging bugs: #181, #182, #183, #184, #185, #186, #187, #188
  ,#189, #190, #191, #192

2011-06-14  Juan Francisco Gato Luis <jfcogato@libresoft.es>

  * Bicho/backends/bg.py, Bicho/backends/jira.py, Bicho/backends/sf.py,
  Bicho/db/database.py: fixed datetime bug with timezone, now we don't store
  the timezone. next features will fix that.

2011-06-13  Juan Francisco Gato Luis <jfcogato@libresoft.es>

  * Bicho/backends/bg.py: fixed bug parsing votes, now control the int value or
  None data

  * Bicho/backends/bg.py, Bicho/backends/jira.py, Bicho/backends/sf.py: added
  python-dateutil library support to parse dates and fix the formats bugs

  * Bicho/backends/jira.py: fixed bug #5988 errors in parse datetimes

2011-06-10  Luis Cañas Díaz <lcanas@libresoft.es>

  * README, doc/database/bicho.png, doc/database/database_schema.png: Improve
  the README file and rename the database image schema

  * README, doc/database/bicho.png, doc/database/database_schema.png: Improve
  the README file and rename the database image schema

2011-06-02  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/backends/jira.py: Replace print with printerr when printing errors in
  Jira backend

2011-06-03  Juan Francisco Gato Luis <jfcogato@libresoft.es>

  * Bicho/backends/sf.py: added incremental support to sf backend

2011-06-02  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/backends/jira.py: Replace print with printerr when printing errors in
  Jira backend

2011-06-02  Juan Francisco Gato Luis <jfcogato@libresoft.es>

  * Bicho/backends/bg.py, Bicho/backends/jira.py, Bicho/db/database.py: added
  incremental support for bugzilla and jira

2011-05-30  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/backends/sf.py: Improve the exception handling, sanitizing the output
  and fix parse errors.  The exception handling is now more useful. The output
  has been rewritten to be similar to the rest of backends. The whole backend
  has been improved with little changes. This backend is still unstable.

  * Bicho/backends/sf.py: Improve the exception handling, sanitizing the output
  and fix parse errors.  The exception handling is now more useful. The output
  has been rewritten to be similar to the rest of backends. The whole backend
  has been improved with little changes. This backend is still unstable.

2011-05-27  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/backends/jira.py: Sanitize output for jira backend

  * Bicho/backends/bg.py: Sanitize output for bugzilla backend

  * Bicho/Bicho.py, Bicho/backends/HTMLUtils.py, Bicho/backends/bg.py,
  Bicho/backends/jira.py, Bicho/backends/sf.py, Bicho/common.py,
  Bicho/db/database.py, Bicho/db/mysql.py, Bicho/main.py, setup.py: Fix #285 -
  removed unused libraries

  * Bicho/backends/bg.py, Bicho/db/database.py: Handle the exception thrown by
  the error #287  The bug #287 is not fixed yet, this workaround avoids bicho
  to crash with Unicode encoding errors.

  * Bicho/backends/jira.py: Sanitize output for jira backend

  * Bicho/backends/bg.py: Sanitize output for bugzilla backend

  * Bicho/Bicho.py, Bicho/backends/HTMLUtils.py, Bicho/backends/bg.py,
  Bicho/backends/jira.py, Bicho/backends/sf.py, Bicho/common.py,
  Bicho/db/database.py, Bicho/db/mysql.py, Bicho/main.py, setup.py: Fix #285 -
  removed unused libraries

  * Bicho/backends/bg.py, Bicho/db/database.py: Handle the exception thrown by
  the error #287  The bug #287 is not fixed yet, this workaround avoids bicho
  to crash with Unicode encoding errors.

2011-05-24  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/backends/bg.py, Bicho/common.py, Bicho/db/database.py,
  Bicho/db/mysql.py: Fix #82 Add a table to relate issues and watchers/CC  The
  changes allow to store all the people who is watching the issue/bug for each
  bug. The new table's name is 'issues_watchers'

  * Bicho/backends/bg.py, Bicho/common.py, Bicho/db/database.py,
  Bicho/db/mysql.py: Fix #82 Add a table to relate issues and watchers/CC  The
  changes allow to store all the people who is watching the issue/bug for each
  bug. The new table's name is 'issues_watchers'

2011-05-23  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/backends/bg.py: Fix #286 in the Bugzilla backend.  The extra database
  fields remain with NULL when no data is extracted.

  * Bicho/backends/bg.py: Fix error with the dup_id parameter for the Bugzilla
  backend  The dup_id parameter was not converted to integer. Now it is.

2011-05-19  Juan Francisco Gato Luis <jfcogato@libresoft.es>

  * Bicho/backends/jira.py: added incremental support, if you use a bug url,
  this bug is loaded in the project/tracker database

  * Bicho/backends/jira.py: fixed bugs catching exceptions: when there are no
  html tags or when a bug is deleted and try parse it

2011-05-12  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/Config.py, Bicho/backends/bg.py, Bicho/main.py: Add delay support in
  the Bugzilla backend  The delay parameter has been fixed to be 0 by default,
  the bugzilla backend waits this interval of time between petitions.

  * bin/bicho: Add copyright and license

2011-04-07  Juan Francisco Gato Luis <jfcogato@libresoft.es>

  * Bicho/backends/jira.py: fixed bugs about the parsed description of bugs

  * Bicho/backends/jira.py: fixed loop to download all the bugs xml

  * Bicho/backends/jira.py: jira backend completed

2011-03-24  Santiago Dueñas <sduenas@libresoft.es>

  * doc/database/bicho.png, doc/database/bicho.xml: Update the database
  documentation  New tables (those from Bugzilla and SF.net) has been added to
  the database schema.

2011-03-17  Luis Cañas Díaz <lcanas@libresoft.es>

  * README: Include the Changes done by sduenas in the README file

  * bicho: Remove useless man bicho file

2011-03-10  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/backends/bg.py: Add Bugzilla backend which supports the new database
  schema  Bugzilla backend updated with a extra table to store all the
  information provided by the HTML + XML feeds for each bug. The XML parsing
  method is clearer now as it uses directories to store the content of the
  tags.

2011-03-08  Santiago Dueñas <sduenas@libresoft.es>

  * Bicho/Makefile.am, Bicho/backends/Makefile.am: Remove deprecated stuff

  * Bicho/backends/ParserSFBugs.py, Bicho/backends/sf.py: SourceForge backend
  refactorized

  * Bicho/db/database.py, Bicho/db/mysql.py, setup.py: Support for storing
  non-common issue tracking data  Implementing the abstract class 'DBBackend',
  Bicho's issue tracking backends can now store extracted data non common to
  other issue tracking systems.

  * Bicho/database.py, Bicho/db/__init__.py, Bicho/db/database.py,
  Bicho/db/mysql.py: Add modular support for database engines

  * Bicho/Bicho.py, Bicho/main.py: Tracker's URL is now passed on creating
  backend objects

  * Bicho/main.py: Fix typo

2011-03-03  Juan Francisco Gato Luis <jfcogato@libresoft.es>

  * Bicho/backends/jira.py: The parse of jira is finished, now we have to store
  the data in the database

2011-03-02  Juan Francisco Gato Luis <jfcogato@libresoft.es>

  * Bicho/backends/jira.py: adding alpha version of jira backend

2011-02-25  Santiago Dueñas <sduenas@libresoft.es>

  * Bicho/common.py, Bicho/database.py: Add support to store different types
  and versions of trackers

  * Bicho/database.py: Missing 'attachment' MySQL query added

  * Bicho/common.py: Fix typos on 'common' module

  * Bicho/common.py: Fix initialization of attribs into Change class

2011-02-24  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/database.py: Fix error: DBChange instance expects an integer as
  fourth parameter

  * Bicho/database.py: Add miss variable in _insert_change method

  * Bicho/database.py: Changes on DBComment: var comment renamed to text

  * Bicho/database.py: Fix error: DBComment instance expects an integer as
  second parameter

2011-02-22  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/database.py: Fix typo in the name of a SQL table

2011-02-18  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/database.py: Changes on the MySQL database schema  Add a new table
  for different trackers and its versions called 'tracker_types'. There is also
  a new field in the comment table to take into account the number of comment
  (useful for bugzilla)

2011-02-17  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/database.py: Method 'getDatabase' renamed to 'get_database'

2011-02-14  Santiago Dueñas <sduenas@libresoft.es>

  * Bicho/Config.py, Bicho/info.py, Bicho/main.py, bin/bicho: Fixes #282 Use
  optparse instead of getopt

2011-02-08  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/backends/sf.py, Bicho/database.py: Fixes #277. OptionsStore is now
  Config

  * Bicho/backends/bg.py: Fixes #276. It wasn't using the new module
  Bicho.database

2010-12-28  Santiago Dueñas <sduenas@libresoft.es>

  * doc/database/bicho.png, doc/database/bicho.xml: Database documentation

  * Bicho/backends/sf.py: SourceForge backend addapted to the new database
  schema  Specific fields are not yet implemented.

  * Bicho/Bicho.py, Bicho/Bug.py, Bicho/SqlBug.py, Bicho/common.py,
  Bicho/database.py: New database schema.  A new and improved database schema
  has been developed. This new feature still uses Storm as an ORM and adds some
  methods for accessing the database.  The new schema also addresses the
  comments from issues #258, #259 and #261.  Trackers specific fields should be
  implemented in future.

2010-12-27  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/Bicho.py, Bicho/Bug.py, Bicho/Config.py, Bicho/SqlBug.py,
  Bicho/backends/HTMLUtils.py, Bicho/backends/ParserSFBugs.py,
  Bicho/backends/__init__.py, Bicho/backends/bg.py, Bicho/backends/sf.py,
  Bicho/info.py, Bicho/main.py, Bicho/utils.py, bicho, setup.py: Copyright
  statement updated to Copyright (C) 2011 GSyC/LibreSoft, Universidad Rey Juan
  Carlos

2010-12-23  Luis Cañas Díaz <lcanas@libresoft.es>

  * AUTHORS: carlosgc added to AUTHORS file

  * setup.py: bicho-web package deleted and URL changed from setup.py. It fixes
  #268

  * README: README file improved. Fixes #264

2010-12-20  Luis Cañas Díaz <lcanas@libresoft.es>

  * Bicho/Bicho.py, Bicho/Config.py, Bicho/SqlBug.py, Bicho/backends/bg.py,
  Bicho/config.py, Bicho/info.py, Bicho/main.py, Bicho/utils.py, bicho,
  config.sample: Improved argument handling and configuration file. Fixes #263 
  I've used the argument handling used in cvsanaly and apply it to bicho. Now
  we have more options (debug mode, version, optional delay) and the
  configuration file is similar to the one used by cvsanaly.  I've also divided
  the utils.py functions and the Config class. This part is very similar in
  cvsanaly.

  * AUTHORS: Names added to the AUTHORS file

  * bicho: License header added to main bicho file

2010-12-20  Juan Francisco Gato Luis <jfcogato@libresoft.es>

  * Bicho/backends/bg.py: added author

  * Bicho/backends/bg.py: The html parser now has a more clear source code

2010-12-16  Juan Francisco Gato Luis <jfcogato@libresoft.es>

  * Bicho/backends/bg.py: added Beatifulsoup support

2010-02-17  Daniel Izquierdo Cortázar <dizquierdo@libresoft.es>

	* config.py: File needed for setup (anyway, file to be removed in the future)


2009-12-11  Francisco Rivas  <frivas@libresoft.es>

	* setup.py :

		Release 0.4

 
2009-12-11  Francisco Rivas  <frivas@libresoft.es>

	* setup.py : Change Version

		Changes to this file for change the version (r-7157)


2009-12-11  Francisco Rivas  <frivas@libresoft.es>

	* AUTHORS : Updated, added Francisco Rivas
	* ChangeLog : Updated
	* NEWS : Updated
	* autogen.sh : Deleted we do not need it, we use distutils
	* configure.in : Deleted we do not need it, we use distutils
	* Makefile.am : Deleted we do not need it, we use distutils
	* bicho.in : Deleted we do not need it, we use distutils 
		
		Some files deleted because we are using distutils to install and
		deploy the application. (r-7156) 
 
2009-12-11  Francisco Rivas  <frivas@libresoft.es>

  * common/ : Deleted we do not need it, we use distutils 
	* common/bicho-autogen.sh : Deleted we do not need it, we use distutils 

		Some files deleted because we are using distutils to install and
		deploy the application. (r-7155) 
 

2009-23-10  Francisco Rivas  <frivas@libresoft.es>

	* bicho/trunk/doc/bicho.1 : Bicho man page

		Added a SYNOPSIS section in man page (r-7150)
 
 
2009-23-10  Francisco Rivas  <frivas@libresoft.es>

	* bicho/trunk/setup.py : Installer

		Needed modification to installer script to install the man page (r-7148)
 

2009-23-10  Francisco Rivas  <frivas@libresoft.es>

	* bicho/trunk/doc/bicho.1 : Man page of bicho

		Adding a man page (r-7147)
 

2009-23-10  Francisco Rivas  <frivas@libresoft.es>

	* bicho/trunk/doc/UserManual.txt : User manual of bicho

		Adding a basic user manual (r-7146)
 

2009-02-10  Francisco Rivas  <frivas@libresoft.es>

	* bicho/trunk/bicho : Launcher
	*	bicho/trunk/bin/bicho : Launcher
	* bicho/trunk/setup.py : distutils-based Installer

	 Added installer and needed files (r-7143)

 
2009-02-10  Francisco Rivas  <frivas@libresoft.es>

	* bicho/trunk/Bicho/backends/sf.py: Fixing bugs #133 #134 and show number of bug
	analyzed during the process

	 Bug #133 : The number of bugs reported by the application is wrong 
	 Bug #134 : the amount of bugs analyzed was wrong because it did not
	 handle well the offset bugs, it means, the links of each page of bugs
	 (r-7142)

 
2009-23-09  Francisco Rivas  <frivas@libresoft.es>

	* bicho/trunk/Bicho/SqlBug.py: Fixing Bug #83 : Types of field in ddbb

	 For instance, some of SubmittedDate field should use type Date and
	 not Varchar(128)(r-7141) 

 
2009-23-09  Francisco Rivas  <frivas@libresoft.es>

	* bicho/trunk/Bicho/backends/sf.py: Fixing Bug #129 : First line removed

	 The first line of every description (detail) of a bug is removed.(r-7140) 

 
2009-23-09  Francisco Rivas  <frivas@libresoft.es>

	* bicho/trunk/Bicho/backends/sf.py: Fixing Bug #126 : Support for attachments

	 Bicho writes the information in attachments table in a wrong way (r-7139) 

 
2009-23-09  Francisco Rivas  <frivas@libresoft.es>

	* bicho/trunk/Bicho/backends/sf.py: Fixing Bug #125 : Support for SF Changes

	 Writes information of a bug whithout taking in account if it has
	 changes or not in Changes table (r-7138) 

 
2009-22-09  Francisco Rivas  <frivas@libresoft.es>

	* bicho/trunk/Bicho/backends/sf.py: Fixing Bug #124 : Support for comments

	 Bicho writes information in Comments table in wrong way (r-7137) 

 
2009-22-09  Francisco Rivas  <frivas@libresoft.es>

	* bicho/trunk/Bicho/backends/sf.py: Added GeneralInfo processing and store in db
	methods

	Added methods to store information in GeneralInfo table (r-7136) 


2009-21-09  Francisco Rivas  <frivas@libresoft.es>

	* bicho/trunk/Bicho/utils.py: Added some functions used in SF parser

	There are some functions that the new parser use (r-7134)
 

2009-21-09  Francisco Rivas  <frivas@libresoft.es>

	* bicho/trunk/Bicho/backends/sf.py: New SF Parser, testing

	New parser for SoureForge, still testing. (r-7133)
 

2009-31-08  Daniel Izquierdo Cortazar  <dizquierdo@libresoft.es>

	* Bicho/backends/bg.py: added support for Apache bugzilla

	Added support for Apache bugzilla, bug #81


2009-29-07  Daniel Izquierdo Cortazar  <dizquierdo@libresoft.es>

	* Bicho/backends/bg.py: fixing bug #24

	Fixed bug #24


2009-29-07  Daniel Izquierdo Cortazar  <dizquierdo@gsyc.es>

	* Bicho/Bug.py: Added field resolution
	* Bicho/backends/bg.py: Fixed bug #17 - 
	Bicho fail to concatenate 'str' and 'NoneType' objects

	Fixed bug #17
	Thanks to Guido Conaldi for his report.


2009-24-07  Daniel Izquierdo Cortazar  <dizquierdo@gsyc.es>

	* Bicho/SqlBug.py: Added support for the missed fields in Storm.
	* Bicho/backends/bg.py: Added support for the missed fields.

	There is a new table in Bugzilla named as Bugzilla_Data
	where missing fields were added.
	It has also added the resolution field.


2009-23-02  Daniel Izquierdo Cortazar  <dizquierdo@gsyc.es>

	* configure.in:

	Release 0.3


2009-23-02  Daniel Izquierdo Cortazar  <dizquierdo@gsyc.es>

	* Bicho/backends/bg.py: filtered blank characters

	Data from activity in bugzilla backend improved


2009-23-02  Santiago Dueñas Domínguez  <sduenas@gsyc.es>

	* README:

	Fixed example.
	

2009-19-02  Santiago Dueñas Domínguez  <sduenas@gsyc.es>

	* Bicho/main.py:
	* Bicho/utils.py:

	Some config file bugs fixed.


2009-19-02  Santiago Dueñas Domínguez  <sduenas@gsyc.es>

	* Bicho/backends/Makefile.am:

	Added missed file to the makefile.


2009-05-02 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.es>

	* Bicho/backends/bg.py: KDE bugzilla support added

	Bicho retrieves data from KDE's bugzilla.


2009-27-01 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.es>

	* Bicho/backends/bg.py: Minor bug fixed

	Bicho retrieves comments


2009-14-01 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.es>

	* Bicho/backends/bg.py: Now it inserts GeneralInfo

	General Info is stored


2009-01-01 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.es>

	* Bicho/backends/bg.py: Comments data is now stored

	Comments are stored in the database


2009-04-01 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.es>

	* Bicho/backends/bg.py: Stores information in the database

	"Changes" information is now stored in mysql format


2009-03-01 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.es>

	* Bicho/backends/bg.py: It retrieves changes information

	Changes information is not stored yet. Just the HTML parser
	which creates a list of changes which will be stored in the future


2008-12-22 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.es>

	* main.py: New option for parsing bugzillas added
	* backends/bg.py: bugzilla backend added

	Given support for bugzilla analysis. So far, basic information
	is stored in the database. No comments, no changes.


2008-12-19 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.es>

	* configure.in:

	Release 0.21


2008-12-18 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.es>

	* Bicho/bicho.conf: Trunk file to default options

	Trunk config file to default options


2008-12-18 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.es>

	* configure.in:

	Release 0.2


2008-09-04 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.escet.urjc.es>

	* Bicho/backends/sf.py: Now, it recognises the name of the project and
	the name of the tracker
	* Bicho/SqlBug.py: Added a new storm object, GeneralInfo, which
	contains general info about: project, url, tracker's name, date
	* Bicho/Bug.py: GeneralInfo object added

	Now, it detects the project name, url, tracker's name and date of
	analysis. That info is stored in a database


2008-09-02 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.escet.urjc.es>

	* Bicho/Bug.py: Added support for field "changes" from SourceForge
	HTML (bug's history)
	* Bicho/SqlBug.py: Added support for bug's history, new table for
	sqlite, mysql and postgres
	* Bicho/backends/sf.py: "Changes" are added
	* Bicho/backends/ParserSFBugs.py: The statets machine was modified.
	Now "changes" HTML is supported

	Changes from SourceForge HTML is now recorded and stored in the
	database


2007-10-29 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.escet.urjc.es>

	* Bicho/backends/ParserSFBugs.py: Fixed [#330] Error parsing information from a bug in SourceForge

	Fixed: [#330] Error parsing information from a bug in SourceForge


2007-10-25 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.escet.urjc.es>

	* Bicho/backends/ParserSFBugs.py: Added source code to unify in the same file SourceForge parser functionality
	* Bicho/backends/HTMLUtils.py: Used just for HTML Utils (join urls and so on)
	* Bicho/backends/sf.py: Parser for getting links was renamed

	Unification of SourceForge parser in just one file


2007-10-13 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.escet.urjc.es>

	* Bicho/utils.py: Added path option (to store dowloaded web pages)
	* Bicho/bicho.conf: Added path option (by default /tmp/bicho/)
	* Bicho/backends/sf.py: Store web pages functionality added 
	* Bicho/main.py: Path option added

	Bicho stores downloaded web pages


2007-09-10 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.escet.urjc.es>

	* configure.in:

	Release 0.1


2007-09-10 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.escet.urjc.es>

	* Bicho/bicho.conf: config file added

	Added config file


2007-09-09 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.escet.urjc.es>

	* Bicho/Bug.py: Added Attachment class
	* Bicho/SqlBug.py: Added support for new class Attachment (class storm
	DBAttachment and sql queries to create table Attachment in mysql,
	postgres and sqlite)
	* Bicho/backends/sf.py: Modified to add Attachments to database
	* Bicho/backends/ParserSFBugs.py: Added more states to parse HTML
	which contains attachments and some bugs were fixed (related to 
	comments)
	
	Attachments are registered in this version and they are stored in the
	database.


2007-09-08 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.escet.urjc.es>

	* Bicho/Bug.py: Added "Comment" class
	* Bicho/SqlBug.py: Added support for new class "Comment" (class storm
	DBComment and sql queries to create table Comment in mysql, postgres
	and sqlite)
	* Bicho/backends/sf.py: Modified to add Comments to database
	* Bicho/backends/ParserSFBugs.py: Added four more states to parse HTML
	which contains comments.
	
	Comments are registered in this version and they are stored in the
	database.


2007-09-07 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.escet.urjc.es>

	* Bicho/main.py: Added support for config file (it must be in
	Bicho/bicho.conf)
	* Bicho/Bicho.py: Minor changes (to support options store class)
	* Bicho/backends/sf.py: Minor changes (to support options store class)
	* Bicho/utils.py: Modified Options store class (new options added)
	* Bicho/SqlBug.py: Minor changes (to support options store class)

	Added support for file config and added options for an input database
	(eg: bugzilla support)


2007-09-06 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.escet.urjc.es>

	* Bicho/SqlBug.py: Modified to use Singleton pattern
	* Bicho/utils.py: Here you can find the class which is the
	singleton and it contains all the options obtained by command line
	* Bicho/backends/sf.py: Modified to use Singleton pattern
	* Bicho/backends/__init__.py: Modified to use Singleton pattern
	* Bicho/Bicho.py: Modified to use Singleton pattern
	* Bicho/main.py: Modified to use Singleton pattern and added options
	for database (output format in bicho)
	
	Added singleton pattern. Now the class Opt_CommandLine has
	a shared variable with values. This class will be use by each object
	which needs to access command line options given by user.


2007-09-06 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.escet.urjc.es>
	
	* Bicho/SqlBug.py: Added simple factory pattern (supporting now
	more databases, but not implemented)
	* Bicho/backends/sf.py: Brief changes made to use that pattern
	* Bicho/main.py: Deleted command line options (they must be added
	in future)

	Added simple factory pattern and cleaned command line options.


2007-09-02 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.escet.urjc.es>

	* Bicho/Bug.py: Cleaning code
	* Bicho/SqlBug.py: Added support only for MySQL using Storm
	* Bicho/backends/sf.py: Comments deleted/Added support for MySQL
	* Bicho/backends/HTMLUtils.py: Cleaning code/Fixed a bug
	* Bicho/backends/ParserSFBugs.py: Cleaning code
	* Bicho/Bicho.py: Cleaning code

	Added support for MySQL access (be careful the string to access
	is hardcoded) and some comments have been deleted.
	

2007-08-29 Daniel Izquierdo Cortazar  <dizquierdo@gsyc.escet.urjc.es>

	* Initial import
	
