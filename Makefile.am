SUBDIRS = Bicho

bin_SCRIPTS = bicho

bicho: bicho.in
	sed -e s!\@pyexecdir\@!@pyexecdir@! < $< > $@
	chmod a+x $@

EXTRA_DIST = 		\
	COPYING		\
	README		\
	bicho.in

CLEANFILES = bicho
