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

import enum
import os
import sys
import uuid

__path__ = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(__path__, os.pardir))

import binarize

class TestEnum(enum.Enum):
    TEST1 = 'string'
    TEST2 = ('tuple', 1, 2, 3)

class Test1(binarize.Structure):
    field1 = binarize.UINT8
    field2 = binarize.STRING(size=20)
    field3 = binarize.UUID

class Test2(Test1):
    field4 = TestEnum

class Test3(binarize.Structure):
    test2 = Test2
    abc = binarize.STRING(size=3)

if __name__ == '__main__':
    print(Test1)
    print(Test2)
    print(Test3)
    test1 = Test1(34, 'abcdef', uuid.uuid4())
    print(test1)
    print(test1.encode())
    print(Test1.decode(test1.encode()))
    test2 = Test2(255, 'abc123', uuid.uuid4(), TestEnum.TEST2)
    print(test2)
    print(test2.encode())
    print(Test2.decode(test2.encode()))
    test3 = Test3(test2, 'abc')
    print(test3)
    print(test3.encode())
    print(test3.decode(test3.encode()))
