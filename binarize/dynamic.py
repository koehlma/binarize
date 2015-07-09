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

import decimal
import enum
import ipaddress
import uuid

from . import primitives

class Control(enum.Enum):
    END = 0

def pack(structure):
    if isinstance(structure, bool):
        if structure:
            yield b'\xcd'
        else:
            yield b'\xce'
    elif isinstance(structure, int):
        if structure < 0:
            structure *= -1
            if structure < 32:
                yield bytes([32 | structure])
            elif structure < 2 ** 8:
                yield b'\xc1'
                yield primitives.struct_uint8.pack(structure)
            elif structure < 2 ** 16:
                yield b'\xc3'
                yield primitives.struct_uint16.pack(structure)
            elif structure < 2 ** 32:
                yield b'\xc5'
                yield primitives.struct_uint32.pack(structure)
            elif structure < 2 ** 64:
                yield b'\xc7'
                yield primitives.struct_uint64.pack(structure)
        else:
            if structure < 32:
                yield bytes([structure])
            elif structure < 2 ** 8:
                yield b'\xc0'
                yield primitives.struct_uint8.pack(structure)
            elif structure < 2 ** 16:
                yield b'\xc2'
                yield primitives.struct_uint16.pack(structure)
            elif structure < 2 ** 32:
                yield b'\xc4'
                yield primitives.struct_uint32.pack(structure)
            elif structure < 2 ** 64:
                yield b'\xc6'
                yield primitives.struct_uint64.pack(structure)
    elif isinstance(structure, float):
        yield b'\xc8'
        yield primitives.struct_double.pack(structure)
    elif isinstance(structure, str):
        encoded = structure.encode('utf-8')
        length = len(encoded)
        if length < 32:
            yield bytes([64 | length])
        elif length < 2 ** 8:
            yield b'\xd8'
            yield primitives.struct_uint8.pack(length)
        elif length < 2 ** 16:
            yield b'\xd9'
            yield primitives.struct_uint16.pack(length)
        elif length < 2 ** 32:
            yield b'\xda'
            yield primitives.struct_uint32.pack(length)
        elif length < 2 ** 64:
            yield b'\xdb'
            yield primitives.struct_uint64.pack(length)
        else:
            raise ValueError()
        yield encoded
    elif isinstance(structure, bytes):
        length = len(structure)
        if length < 32:
            yield bytes([96 | length])
        elif length < 2 ** 8:
            yield b'\xdc'
            yield primitives.struct_uint8.pack(length)
        elif length < 2 ** 16:
            yield b'\xdd'
            yield primitives.struct_uint16.pack(length)
        elif length < 2 ** 32:
            yield b'\xde'
            yield primitives.struct_uint32.pack(length)
        elif length < 2 ** 64:
            yield b'\xdf'
            yield primitives.struct_uint64.pack(length)
        else:
            raise ValueError()
        yield structure
    elif structure is None:
        yield b'\xcf'
    elif isinstance(structure, (list, tuple)):
        length = len(structure)
        if length < 32:
            yield bytes([128 | length])
        else:
            yield b'\xd5'
        for item in structure:
            yield from pack(item)
        if length > 31:
            yield b'\xd7'
    elif isinstance(structure, dict):
        length = len(structure)
        if length < 32:
            yield bytes([160 | length])
        else:
            yield b'\xd6'
        for key, value in structure.items():
            yield from pack(key)
            yield from pack(value)
        if length > 31:
            yield b'\xd7'
    elif isinstance(structure, decimal.Decimal):
        yield b'\xcc'
        yield from primitives.pack_decimal128(structure)
    elif isinstance(structure, ipaddress.IPv4Address):
        yield b'\xd2'
        yield structure.packed
    elif isinstance(structure, ipaddress.IPv6Address):
        yield b'\xd3'
        yield structure.packed
    elif isinstance(structure, uuid.UUID):
        yield b'\xd4'
        yield structure.bytes

def encode(structure):
    return b''.join(pack(structure))

def unpack(buffer, pointer=0):
    constructor = buffer[pointer]
    pointer += 1
    group = constructor >> 5
    if group == 0:
        structure = constructor
    elif group == 1:
        structure = -(constructor & 31)
    elif group == 2:
        length = constructor & 31
        structure = buffer[pointer:pointer + length].decode('utf-8')
        pointer += length
    elif group == 3:
        length = constructor & 31
        structure = buffer[pointer:pointer + length]
        pointer += length
    elif group == 4:
        length = constructor & 31
        structure = []
        for index in range(length):
            pointer, item = unpack(buffer, pointer)
            structure.append(item)
    elif group == 5:
        length = constructor & 31
        structure = {}
        for index in range(length):
            pointer, key = unpack(buffer, pointer)
            pointer, value = unpack(buffer, pointer)
            structure[key] = value
    elif group == 6:
        if constructor == 192:
            structure = buffer[pointer]
            pointer += 1
        elif constructor == 193:
            structure = -buffer[pointer]
            pointer += 1
        elif constructor == 194:
            data = buffer[pointer:pointer + 2]
            structure = primitives.struct_uint16.unpack(data)[0]
            pointer += 2
        elif constructor == 195:
            data = buffer[pointer:pointer + 2]
            structure = -primitives.struct_uint16.unpack(data)[0]
            pointer += 2
        elif constructor == 196:
            data = buffer[pointer:pointer + 4]
            structure = primitives.struct_uint32.unpack(data)[0]
            pointer += 4
        elif constructor == 197:
            data = buffer[pointer:pointer + 4]
            structure = -primitives.struct_uint32.unpack(data)[0]
            pointer += 4
        elif constructor == 198:
            data = buffer[pointer:pointer + 8]
            structure = primitives.struct_uint64.unpack(data)[0]
            pointer += 8
        elif constructor == 199:
            data = buffer[pointer:pointer + 8]
            structure = -primitives.struct_uint64.unpack(data)[0]
            pointer += 8
        elif constructor == 200:
            data = buffer[pointer:pointer + 4]
            structure = primitives.struct_float.unpack(data)[0]
            pointer += 4
        elif constructor == 201:
            data = buffer[pointer:pointer + 8]
            structure = primitives.struct_double.unpack(data)[0]
            pointer += 8
        elif constructor == 202:
            pointer, structure = primitives.unpack_decimal32(buffer, pointer)
        elif constructor == 203:
            pointer, structure = primitives.unpack_decimal64(buffer, pointer)
        elif constructor == 204:
            pointer, structure = primitives.unpack_decimal128(buffer, pointer)
        elif constructor == 205:
            structure = True
        elif constructor == 206:
            structure = False
        elif constructor == 207:
            structure = None
        elif constructor == 208:
            pointer, structure = primitives.unpack_varint(buffer, pointer)
        elif constructor == 209:
            pointer, structure = primitives.unpack_varint(buffer, pointer)
            structure *= -1
        elif constructor == 210:
            structure = ipaddress.IPv4Address(buffer[pointer:pointer + 4])
            pointer += 4
        elif constructor == 211:
            structure = ipaddress.IPv6Address(buffer[pointer:pointer + 8])
            pointer += 8
        elif constructor == 212:
            structure = uuid.UUID(bytes=buffer[pointer:pointer + 16])
            pointer += 16
        elif constructor == 213:
            structure = []
            while True:
                pointer, item = unpack(buffer, pointer)
                if item is Control.END:
                    break
                structure.append(item)
        elif constructor == 214:
            structure = {}
            while True:
                pointer, key = unpack(buffer, pointer)
                if key is Control.END:
                    break
                pointer, value = unpack(buffer, pointer)
                structure[key] = value
        elif constructor == 215:
            structure = Control.END
        elif constructor == 216:
            length = buffer[pointer]
            pointer += 1
            structure = buffer[pointer:pointer + length].decode('utf-8')
            pointer += length
        elif constructor == 217:
            length = struct_uint16.unpack(buffer[pointer:pointer + 2])[0]
            pointer += 2
            structure = buffer[pointer:pointer + length].decode('utf-8')
            pointer += length
        elif constructor == 218:
            length = struct_uint32.unpack(buffer[pointer:pointer + 4])[0]
            pointer += 4
            structure = buffer[pointer:pointer + length].decode('utf-8')
            pointer += length
        elif constructor == 219:
            length = struct_uint32.unpack(buffer[pointer:pointer + 8])[0]
            pointer += 8
            structure = buffer[pointer:pointer + length].decode('utf-8')
            pointer += length
        elif constructor == 220:
            length = buffer[pointer]
            pointer += 1
            structure = buffer[pointer:pointer + length]
            pointer += length
        elif constructor == 221:
            length = struct_uint16.unpack(buffer[pointer:pointer + 2])[0]
            pointer += 2
            structure = buffer[pointer:pointer + length]
            pointer += length
        elif constructor == 222:
            length = struct_uint32.unpack(buffer[pointer:pointer + 4])[0]
            pointer += 4
            structure = buffer[pointer:pointer + length]
            pointer += length
        elif constructor == 223:
            length = struct_uint32.unpack(buffer[pointer:pointer + 8])[0]
            pointer += 8
            structure = buffer[pointer:pointer + length]
            pointer += length
    return pointer, structure

def decode(buffer):
    return unpack(buffer)[1]

if __name__ == '__main__':
    message = encode({'compact' : True, 'schema' : 0})
    print(message)
    print(decode(message))

