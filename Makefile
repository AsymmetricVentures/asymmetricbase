# -*- coding: utf-8 -*-
#    Asymmetric Base Framework - A collection of utilities for django frameworks
#    Copyright (C) 2013  Asymmetric Ventures Inc.
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; version 2 of the License.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


all: clean build sync
	

clean:
	rm -rf build dist *.deb MANIFEST asymmetricbase.egg-info
	- sudo rm -rf asymmetricbase.egg-info

build: clean
	python setup.py bdist_rpm
	sudo alien -dc dist/*.noarch.rpm

sync: build
	rsync -avh *.deb jayson:
	rsync -avh *.deb westpoint:

clean_compiled_templates:
	find . -name "*_compiled.py" -print |xargs rm