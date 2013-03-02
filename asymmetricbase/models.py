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

#@PydevCodeAnalysisIgnore
from django.db.models import * # @UnusedWildImport
from fields import (DollarField, IntegerRangeField, EnumField, ZERO_DOLLARS,
	COMMENT_LENGTH, LONG_MESSAGE_LENGTH, LONG_NAME_LENGTH, SHORT_MESSAGE_LENGTH, SHORT_NAME_LENGTH,
	CommentField, LongMessageField, LongNameField, ShortMessageField, ShortNameField, UUIDField)
from _models import * # @UnusedWildImport

