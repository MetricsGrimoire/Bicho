Testing Bicho
=============

We currently have automated tests for two Bicho backends:

* Launchpad
* Allura

To run Launchpad tests, change "root" and "root" on lines 47 and 48 of launchpad.py to correspond to your database username and password, then run:

$ python run_tests.py launchpad

This test checks the final result of an analysis (they are not unit tests). The test basically executes bicho against Glance, a project with some data reviewed by hand, and compares the results of some queries. It is not rocket science, but with the tricky examples it is useful. It will take several minutes to run.

To run Allura tests, change "root" and "" on lines 133 and 134 of test_allura.py to correspond to your database username and password, then run:

$ python test_allura.py

This uses the Python unittest module and the already-downloaded input in the data/allura/ directory to test the backend. It should run in under a second.

If you are writing a new backend, please also add a standalone testrunner like test_allura.py and data in a subdirectory of tests/data/ .