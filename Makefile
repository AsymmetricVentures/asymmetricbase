
all: clean build sync
	
	
clean:
	rm -rf build dist *.deb MANIFEST

build:
	python setup.py bdist_rpm
	sudo alien -dc dist/*.noarch.rpm

sync:
	rsync -avh *.deb jayson:
	rsync -avh *.deb westpoint: