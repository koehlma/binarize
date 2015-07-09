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
import collections
import enum

from .primitives import *
from .type import ABCType, Type

__all__ = ['EnumType', 'Field', 'StructureMeta', 'StructureType', 'Structure']

class EnumType(Type):
    __slots__ = ['name', 'enum', 'items', 'size']
    
    def __init__(self, enum, varint=False, name=None):
        self.name = name or enum.__name__
        self.enum = enum
        self.items = list(self.enum)
        length = len(self.items)
        if varint:
            self._pack = pack_varint
            self._unpack = unpack_varint
            self.size = None
        elif length < 256:
            self._pack = pack_uint8
            self._unpack = unpack_uint8
            self.size = 1
        elif length < 65536:
            self._pack = pack_uint16
            self._unpack = unpack_uint16
            self.size = 2
        else:
            raise ValueError()
    
    def __str__(self):
        return '<Enum:{}>'.format(self.name)
    
    def pack(self, enum):
        yield from self._pack(self.items.index(enum))
    
    def unpack(self, data, pointer=0):
        pointer, index = self._unpack(data, pointer)
        return pointer, self.items[index]

class Field():
    __slots__ = ['type', 'name']
       
    def __init__(self, type_, name=None, **options):
        self.type = type_
        self.name = name
    
    def __str__(self):
        return '<Field name="{}", type="{}">'.format(self.name, self.type)
        
class StructureMeta(type):
    @classmethod
    def __prepare__(metacls, name, bases):
        return collections.OrderedDict()
    
    def __new__(cls, name, bases, members):
        members['name'] = name
        fields = collections.OrderedDict()       
        for base in bases:
            if issubclass(base, Structure):
                fields.update(base.fields)
        for name, value in members.items():
            if isinstance(value, Field):
                fields[name] = value
                value.name = name
            elif isinstance(value, ABCType):
                fields[name] = Field(value, name)
            elif isinstance(getattr(value, 'type', None), ABCType):
                fields[name] = Field(value.type, name)
            elif isinstance(value, enum.EnumMeta):
                fields[name] = Field(EnumType(value), name)
        if 'fields' in members:
            for name, field in members['fields']:
                fields[name] = field
                field.name = name
        for name in fields:
            if name in members:
                del members[name]
        members['type'] = StructureType(members['name'], fields)               
        members['fields'] = fields
        try:
            members['size'] = sum(field.type.size for field in fields.values())
        except TypeError:
            members['size'] = None
        members['names'] = list(fields.keys())
        NewStructure = type.__new__(cls, name, bases, members)
        members['type'].structure = NewStructure
        return NewStructure
    
    def __str__(cls):
        fields = ', '.join(str(field) for field in cls.fields.values())
        return '<Structure:{} [{}]>'.format(cls.name, fields)

class StructureType(Type):
    __slots__ = ['name', 'fields', 'structure']
    
    def __init__(self, name, fields, structure=None):
        self.name = name
        self.fields = fields
        self.structure = structure
    
    def __str__(self):
        fields = ', '.join(str(field) for field in self.fields.values())
        return '<StructureType:{} [{}]>'.format(self.name, fields)
    
    def pack(self, structure):
        for name, field in self.fields.items():
            yield from field.type.pack(structure[name])
   
    def unpack(self, data, pointer=0):
        values = []
        for field in self.fields.values():
            pointer, value = field.type.unpack(data, pointer)
            values.append(value)
        return pointer, self.structure(*values)


class Structure(metaclass=StructureMeta):
    __slots__ = ['values']
      
    def __init__(self, *arguments, **values):
        for index, value in enumerate(arguments):
            values[self.names[index]] = value
        self.values = values
    
    def __str__(self):
        fields = ', '.join('{}="{}"'.format(name, self.values[name])
                           for name in self.names)
        return '<Structure:{} {}>'.format(self.name, fields)
    
    def __bytes__(self):
        return self.encode()
    
    def __getitem__(self, name):
        return self.values[name]
    
    def __setitem__(self, name, value):
        self.values[name] = value
    
    def __getattr__(self, name):
        if name in self.values:
            return self.values[name]
        raise AttributeError()    
               
    def __setattr__(self, name, value):
        if name in self.names:
            self.values[name] = value
        else:
            super().__setattr__(name, value)
            
    def encode(self):
        return b''.join(self.type.pack(self))
    
    @classmethod
    def decode(cls, data):
        return cls.type.unpack(data)[1]
