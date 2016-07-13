PATHNAME=$(shell pwd)
BASENAME=$(shell basename $(PATHNAME))


all: sdist

######################################################################
# INSTALLATION
######################################################################

pip:
	pip install -r requirements.txt

dist:
	make -f Makefile pip

sdist: clean
	python setup.py sdist --formats=gztar

install:
	pip install dist/*.tar.gz

test: clean
	pip install --upgrade dist/*.tar.gz

######################################################################
# TEST INSTALLATION
######################################################################

test-install:
	pip install -r test-requirements.txt

######################################################################
# PYPI
######################################################################

pip-upload: clean
	python setup.py sdist --format=gztar upload -r local

pip-register:
	python setup.py register -r local

#####################################################################
# CLEAN
#####################################################################

clean:
	find . -name "*~" -exec rm {} \;  
	find . -name "*.pyc" -exec rm {} \;  
	rm -rf build dist docs/build
	rm -f *~ 
	rm -rf *.egg-info .egg*
	#cd doc; make clean
	echo "clean done"


#############################################################################
# SPHINX DOC
#############################################################################

html:
	make -f Makefile sphinx

sphinx:
	cd doc; make html

view: html
	open doc/build/html/index.html
