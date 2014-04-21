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

from __future__ import absolute_import, division, print_function, unicode_literals

from django.http import HttpResponseRedirect

from .base import AsymBaseView

class ErrorBaseView(AsymBaseView):
	login_required = False
	@classmethod
	def as_view(cls, **initkwargs):
		v = super(AsymBaseView, cls).as_view(**initkwargs)
		
		def view(request, *args, **kwargs):
			response = v(request, *args, **kwargs)
			if not isinstance(response, HttpResponseRedirect):
				response.render()
			return response
		return view

class PermissionDeniedView(ErrorBaseView):
	template_name = '403.djhtml'

class NotFoundView(ErrorBaseView):
	template_name = '404.djhtml'

class ServerErrorView(ErrorBaseView):
	template_name = '500.djhtml'
