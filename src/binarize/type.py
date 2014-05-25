# -*- coding:utf-8 -*-
#
# Copyright (C) 2014, Maximilian Köhl <linuxmaxi@googlemail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import abc

from collections import namedtuple

class Type(metaclass=abc.ABCMeta):
    name = None
    
    @classmethod
    @abc.abstractmethod
    def pack(cls, instance, **options):
        raise NotImplemented()
    
    @classmethod
    @abc.abstractmethod
    def unpack(cls, data, pointer=0, **options):
        raise NotImplemented()

PrimitiveType = namedtuple('PrimitiveType', ['name', 'unpack', 'pack'])

Type.register(PrimitiveType)
