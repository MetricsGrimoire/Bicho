 Description
-----------

Bicho is a command line based tool used to parse bug/issue tracking 
systems. It gets all the information associated to issues and store 
them in a relation database.

Currently it supports:
- Bugzilla
- Sourceforge.net (abandoned)
- Jira
- Launchpad
- Allura (unstable)
- Github (unstable)
- Google Code (unstable)
- Redmine (unstable, no changes)


 License
---------

Bicho is licensed under GNU General Public License (GPL), version 2 or later.


 Download
----------

Home page:
* http://metricsgrimoire.github.com/Bicho/

Releases:
* https://github.com/MetricsGrimoire/Bicho/downloads

Latest version:
* git://github.com/MetricsGrimoire/Bicho.git


 Requirements
------------

 * Python >= 2.4
 * Python Storm. Depending on the database driver to be used you'll also need
 one of the following python libraries:
   - mysqldb or psycopg2 or pysqlite2 (unstable with PostgreSQL; MySQL is recommended - default engine should be set to MYISAM)
   - python-launchpadlib (for Launchpad backend)
 * Beautiful Soup library: error-tolerant HTML parser for Python
 * python-feedparser


 Installation
-------------

 You can install bicho running the setup.py script:

  # python setup.py install

 For the impatients:

  $ bicho --help


 Running Bicho
--------------

It is very important to use a delay, if you run Bicho against big sites with a
delay between bug petitions your IP address could be banned!

E1. Getting information from a project that uses Bugzilla, like Bicho ;)

$ bicho --db-user-out=[DB USER] --db-password-out=[DB PASS] --db-database-out=[DB NAME] -d 15 -b bg -u https://bugzilla.libresoft.es/buglist.cgi?product=bicho

E2. Getting information from a project hosted in sourceforge.net

$ bicho --db-user-out=[DB USER] --db-password-out=[DB PASS] --db-database-out=[DB NAME] -d 15 -b sf -u "http://sourceforge.net/tracker/?atid=516295&group_id=66938"

E3. Getting information from a project using JIRA

$ bicho --db-user-out=[DB USER] --db-password-out=[DB PASS] --db-database-out=[DB NAME] -d 15 -b jira -u http://support.petalslink.com/browse/PETALSMASTER

E4. Getting information from a project using Launchpad

$ bicho --db-user-out=[DB USER] --db-password-out=[DB PASS] --db-database-out=[DB NAME] -d 15 -b lp -u https://bugs.launchpad.net/openstack

E5. Getting information from a project using Allura

$ bicho --db-user-out=[DB USER] --db-password-out=[DB PASS] --db-database-out=[DB NAME] -d 15 -b allura -u http://sourceforge.net/rest/p/allura/tickets

E6. Getting information from a project using Github

$ bicho --db-user-out=[DB USER] --db-password-out=[DB PASS] --db-database-out=[DB NAME] -b github -u https://api.github.com/repos/composer/composer/issues --backend-user=[GITHUB USER] --backend-password=[GITHUB PASS]

E7. Getting information from a project using Google Code
$ bicho --db-user-out=[DB USER] --db-password-out=[DB PASS] --db-database-out=[DB NAME] -d 15 -b googlecode -u https://code.google.com/feeds/issues/p/apv

E8. Getting information from a project using Redmine
$ bicho --db-user-out=[DB USER] --db-password-out=[DB PASS] --db-database-out=[DB NAME] --backend-user=[REDMINE USER] --backend-password=[REDMINE PASSWORD] -d 1 -b redmine -u https://www.bitergia.net/issues.json


 Roadmap
---------

0.93:
* The updated list of bugs to be fixed can be found here https://github.com/MetricsGrimoire/Bicho/issues?milestone=1&page=1&state=open
* Incremental support broken by issues updated during the download bug #28
* Incorrect order downloading issues from Bugzilla #20
* Incoherent number of issues after webkit analysis bug bugzilla support #26
* Error in database character sets while comparing dates #8
* Problem cloning repo in case insensitive systems #12
* Incremental feature doesn't support multiple projects in the same database #30

1.0:
* https://github.com/MetricsGrimoire/Bicho/issues?milestone=2&page=1&state=open
* issues_log for bugzilla and launchpad
** Launchad support for issues_log table enhancement launchpad support #24
** More efficient and cleaner code for the table issues_log for bugzilla
* New table with information about executions (date, issues downloaded, etc ..)
* Tests, tests and tests
* Improved debug mode with more useful details
* Network fault tolerance (in order to survive to connection issues)
* New backends:
** FusionForge


 Improving Bicho
----------------

Source code, wiki and ITS available on Github:
* https://github.com/MetricsGrimoire/Bicho

Please write to the developers mailing at
* metrics-grimoire _at _ lists.libresoft.es

If you want to receive updates about new versions, and keep in touch
with the development team, consider subscribing to the list. It is a
very low traffic list (< 1 msg a day):

* https://lists.libresoft.es/listinfo/metrics-grimoire


 Credits
--------

Bicho has been originally developed by the GSyC/LibreSoft group at the
Universidad Rey Juan Carlos in Mostoles, near Madrid (Spain). It is
part of a wider research on libre software engineering, aimed to gain
knowledge on how libre software is developed and maintained.


 FAQ
----

F1. Bicho crashed with 'UnicodeEncodeError' exception

UnicodeEncodeError appears when it is not possible to write the data in the
database with the encoding used by this one, to avoid that set your database to
use UTF-8. For instance:

CREATE DATABASE [DB NAME] CHARACTER SET utf8 COLLATE utf8_unicode_ci;

F2. What is the database schema?

There is a nice PNG schema in the directory /doc/database

F3. How can I create a new backend?

Tell us through the contact information above that you want to create a new
backend, we'll try to give you as much information as possible.

F4. How can I submit a bug?

Use the github issue tracker https://github.com/MetricsGrimoire/Bicho/issues
