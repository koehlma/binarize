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

__all__ = ['ABCType', 'register', 'Type']

class ABCType(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __len__(self):
        return self.size
    
    @property
    @abc.abstractmethod
    def name(self):
        raise NotImplemented()
    
    @property
    @abc.abstractmethod
    def size(self):
        raise NotImplemented()
        
    @abc.abstractmethod
    def pack(self, obj, **options):
        raise NotImplemented()
    
    @abc.abstractmethod
    def unpack(self, data, pointer=0, **options):
        raise NotImplemented()

register = ABCType.register

class Type():
    def __len__(self):
        return self.size
        
    @property
    def name(self):
        raise NotImplemented()
    
    @property
    def size(self):
        raise NotImplemented()
    
    def pack(self, obj, **options):
        raise NotImplemented()
    
    def unpack(self, data, pointer=0, **options):
        raise NotImplemented()

ABCType.register(Type)
