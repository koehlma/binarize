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

import collections

from .type import Type

class Field():
    __slots__ = ['type', 'store', 'options', 'name']
       
    def __init__(self, type_, name=None, store=False, **options):
        self.type = type_
        self.store = store
        self.options = options
        self.name = name
    
    def __str__(self):
        if not self.options:
            return '<Field name={}, type={}>'.format(self.name, self.type.name)
        options = ', '.join('{}={}'.format(name, value)
                            for name, value in self.options.items())
        return '<Field name={}, type={}, {}>'.format(self.name, self.type.name,
                                                     options)
            
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
            elif isinstance(value, Type):
                fields[name] = Field(value)
        if 'fields' in members:
            for name, field in members['fields']:
                fields[name] = field
                field.name = name
        for name in fields:
            if name in members:
                del members[name]                
        members['fields'] = fields
        members['names'] = list(fields.keys())
        return type.__new__(cls, name, bases, members)
    
    def __str__(cls):
        fields = ', '.join(str(field) for field in cls.fields.values())
        return '<Structure:{} [{}]>'.format(cls.name, fields)
    
class Structure(metaclass=StructureMeta):
    __slots__ = ['values']
      
    def __init__(self, *arguments, **values):
        for index, value in enumerate(arguments):
            values[self.names[index]] = value
        self.values = values
    
    def __str__(self):
        fields = ', '.join('{}={}'.format(name, self.values[name])
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
        return b''.join(self.pack(self))
    
    @classmethod
    def decode(cls, data):
        return cls.unpack(data)[1]
    
    @classmethod
    def pack(cls, structure):
        for name, field in cls.fields.items():
            yield from field.type.pack(structure.values[name], **field.options)
    
    @classmethod
    def unpack(cls, data, pointer=0):
        values = []
        for field in cls.fields.values():
            pointer, value = field.type.unpack(data, pointer, **field.options)
            values.append(value)
        return pointer, cls(*values)
    
Type.register(Structure)
