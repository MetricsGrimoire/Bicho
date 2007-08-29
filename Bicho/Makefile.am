SUBDIRS = backends

bichodir = $(pyexecdir)/Bicho
bicho_PYTHON = 		\
	__init__.py	\
	Bicho.py	\
	Bug.py		\
	config.py	\
	main.py		\
	SqlBug.py	\
	utils.py

nodist_bicho_PYTHON = config.py

CLEANFILES = config.py
EXTRA_DIST = config.py.in

all-local: config.py

config.py: config.py.in
	sed							\
		-e s!\@PACKAGE_NAME\@!$(PACKAGE_NAME)!		\
		-e s!\@PACKAGE_VERSION\@!$(PACKAGE_VERSION)! 	\
		< $< > $@
