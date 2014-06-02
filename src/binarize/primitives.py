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

'''
Binarize - Primitive Data Types
'''

import datetime
import decimal
import functools
import ipaddress
import struct
import uuid

from .type import Type

__all__ = ['Primitive',
           'struct_sint8', 'struct_uint8', 'struct_sint16', 'struct_uint16',
           'struct_sint32', 'struct_uint32', 'struct_sint64', 'struct_uint64',
           'unpack_sint8', 'pack_sint8', 'unpack_uint8', 'pack_uint8',
           'unpack_sint16', 'pack_sint16', 'unpack_uint16', 'pack_uint16',
           'unpack_sint32', 'pack_sint32', 'unpack_uint32', 'pack_uint32',
           'unpack_sint64', 'pack_sint64', 'unpack_uint64', 'pack_uint64',
           'unpack_float', 'pack_float', 'unpack_double', 'pack_double',
           'unpack_decimal32', 'pack_decimal32',
           'unpack_decimal64', 'pack_decimal64',
           'unpack_decimal128', 'pack_decimal128',
           'unpack_varint', 'pack_varint', 'unpack_size', 'pack_size',
           'unpack_uuid', 'pack_uuid', 'unpack_ipv4', 'pack_ipv4',
           'unpack_ipv6', 'pack_ipv6', 'unpack_date', 'pack_date',
           'unpack_time', 'pack_time', 'unpack_bytes', 'pack_bytes',
           'unpack_string', 'pack_string', 'unpack_boolean', 'pack_boolean', 
           'SINT8', 'UINT8', 'SINT16', 'UINT16', 'SINT32', 'UINT32', 'SINT64',
           'UINT64', 'FLOAT', 'DOUBLE', 'DECIMAL32', 'DECIMAL64', 'DECIMAL128',
           'VARINT', 'SIZE', 'UUID', 'IPV4', 'IPV6', 'DATE', 'TIME', 'BYTES',
           'STRING', 'BOOLEAN']

class Primitive(Type):
    __slots__ = ['name', 'unpack', 'pack', 'size', 'options', 'base']
    
    def __init__(self, name, unpack, pack, size=None, options=None, base=None):
        self.name = name
        self.unpack = unpack
        self.pack = pack
        self.options = options or {}
        self.size = size or self.options.get('size', None)
        self.base = base

    def __call__(self, **options):
        new_options = dict(self.options)
        new_options.update(options)
        unpack = functools.partial(self.unpack, **new_options)
        functools.update_wrapper(unpack, self.unpack)
        pack = functools.partial(self.pack, **new_options)
        functools.update_wrapper(pack, self.pack)        
        return Primitive(self.name, unpack, pack, self.size, new_options,
                         self.base or self)
    
    def __eq__(self, other):
        assert isinstance(other, Primitive)
        if self.base is None and other.base is None:
            return id(self) == id(other)
        return self.base == other.base and self.options == other.options
    
    def __str__(self):
        if self.options:
            options = ', '.join('{}={}'.format(name, value)
                                for name, value in self.options.items())
            return '<Primitive:{}, {}>'.format(self.name, options)
        else:
            return '<Primitive:{}>'.format(self.name)

struct_sint8 = struct.Struct('!b')
struct_uint8 = struct.Struct('!B')
struct_sint16 = struct.Struct('!h')
struct_uint16 = struct.Struct('!H')
struct_sint32 = struct.Struct('!i')
struct_uint32 = struct.Struct('!I')
struct_sint64 = struct.Struct('!q')
struct_uint64 = struct.Struct('!Q')
struct_float = struct.Struct('!f')
struct_double = struct.Struct('!d')

def unpack_sint8(data, pointer=0):
    '''
    Unpacks a signed 8-bit integer.
    '''
    return pointer + 1, struct_sint8.unpack(data[pointer:pointer + 1])[0]

def pack_sint8(integer):
    '''
    Packs a signed 8-bit integer.
    '''
    yield struct_sint8.pack(integer)

def unpack_uint8(data, pointer=0):
    '''
    Unpacks an unsigned 8-bit integer.
    '''
    return pointer + 1, struct_uint8.unpack(data[pointer:pointer + 1])[0]

def pack_uint8(integer):
    '''
    Packs an unsigned 8-bit integer.
    '''
    yield struct_uint8.pack(integer)

def unpack_sint16(data, pointer=0):
    '''
    Unpacks a signed 16-bit integer.
    '''
    return pointer + 2, struct_sint16.unpack(data[pointer:pointer + 2])[0]
    
def pack_sint16(integer):
    '''
    Packs a signed 16-bit integer.
    '''
    yield struct_sint16.pack(integer)

def unpack_uint16(data, pointer=0):
    '''
    Unpacks an unsigned 16-bit integer.
    '''
    return pointer + 2, struct_uint16.unpack(data[pointer:pointer + 2])[0]

def pack_uint16(integer):
    '''
    Packs an unsigned 16-bit integer.
    '''
    yield struct_uint16.pack(integer)

def unpack_sint32(data, pointer=0):
    '''
    Unpacks a signed 32-bit integer.
    '''
    return pointer + 4, struct_sint32.unpack(data[pointer:pointer + 4])[0]

def pack_sint32(integer):
    '''
    Packs a signed 32-bit integer.
    '''
    yield struct_sint32.pack(integer)

def unpack_uint32(data, pointer=0):
    '''
    Unpacks an unsigned 32-bit integer.
    '''
    return pointer + 4, struct_uint32.unpack(data[pointer:pointer + 4])[0]

def pack_uint32(integer):
    '''
    Packs an unsigned 32-bit integer.
    '''
    yield struct_uint32.pack(integer)

def unpack_sint64(data, pointer=0):
    '''
    Unpacks a signed 64-bit integer.
    '''
    return pointer + 8, struct_sint64.unpack(data[pointer:pointer + 8])[0]
    
def pack_sint64(integer):
    '''
    Packs a signed 64-bit integer.
    '''
    yield struct_sint64.pack(integer)

def unpack_uint64(data, pointer=0):
    '''
    Unpacks an unsigned 64-bit integer.
    '''
    return pointer + 8, struct_uint64.unpack(data[pointer:pointer + 8])[0]
    
def pack_uint64(integer):
    '''
    Packs an unsigned 64-bit integer.
    '''
    yield struct_uint64.pack(integer)

def unpack_float(data, pointer=0):
    '''
    Unpacks an IEEE 754 single precision float. 
    '''
    return pointer + 4, struct_float.unpack(data[pointer:pointer + 4])[0]
    
def pack_float(number):
    '''
    Packs an IEEE 754 single precision float.
    '''
    yield struct_float.pack(number)
   
def unpack_double(data, pointer=0):
    '''
    Unpacks an IEEE 754 double precision float. 
    '''
    return pointer + 8, struct_double.unpack(data[pointer:pointer + 8])[0]

def pack_double(number):
    '''
    Packs an IEEE 754 double precision float.
    '''
    yield struct_double.pack(number)

def _decimal_unpack_special(sign, integer):
    if (integer >> 3) & 1:
        if (integer >> 2) & 1:
            return decimal.Decimal('sNaN')
        else:
            return decimal.Decimal('NaN')
    else:
        if sign:
            return decimal.Decimal('-Infinity')
        else:
            return decimal.Decimal('Infinity')
            
def _decimal_pack_special(decimal, size):
    if decimal.is_infinite():
        if decimal.is_signed():
            return b'\xf8' + b'\x00' * (size - 1)
        else:
            return b'\x78' + b'\x00' * (size - 1)
    elif decimal.is_nan():
        if decimal.is_qnan():
            return b'\x7c' + b'\x00' * (size - 1)
        else:
            return b'\x7e' + b'\x00' * (size - 1)
    else:
        raise ValueError()

def unpack_decimal32(data, pointer=0):
    '''
    Unpacks an IEEE 754-2008 32-bit decimal floating point number.
    '''
    integer = int.from_bytes(data[pointer:pointer + 4], 'big')
    sign = integer >> 31
    if (integer >> 29) & 3 == 3:
        if (integer >> 27) & 3 == 3:
            return pointer + 4, _decimal_unpack_special(sign, integer >> 23)
        exponent = ((integer >> 21) & 255) - 101
        significand = 8388608 | (integer & 2097151)
    else:
        exponent = ((integer >> 23) & 255) - 101
        significand = integer & 8388607
    digits = tuple(map(int, str(significand)))
    return pointer + 4, decimal.Decimal((sign, digits, exponent))
    
def pack_decimal32(decimal):
    '''
    Packs an IEEE 754-2008 32-bit decimal floating point number.
    '''
    if not decimal.is_finite():
        yield _decimal_pack_special(decimal, 4)
        return
    sign, digits, exponent = decimal.as_tuple()
    if len(digits) > 7 or (not -101 <= exponent <= 90):
        raise ValueError()
    significand = int(''.join(map(str, digits)))
    if significand >> 21 == 4:
        yield ((sign << 31) | (3 << 29) | ((exponent + 101) << 21) |
               (significand & 2097151)).to_bytes(4,'big')
    else:
        yield ((sign << 31) | ((exponent + 101) << 23) |
               significand).to_bytes(4, 'big')

def unpack_decimal64(data, pointer=0):
    '''
    Unpacks an IEEE 754-2008 64-bit decimal floating point number.
    '''
    integer = int.from_bytes(data[pointer:pointer + 8], 'big')
    sign = integer >> 63
    if (integer >> 61) & 3 == 3:
        if (integer >> 59) & 3 == 3:
            return pointer + 8, _decimal_unpack_special(sign, integer >> 55)
        exponent = ((integer >> 51) & 1023) - 398
        significand = 9007199254740992 | (integer & 2251799813685247)
    else:
        exponent = ((integer >> 53) & 1023) - 398
        significand = integer & 9007199254740991
    digits = tuple(map(int, str(significand)))
    return pointer + 8, decimal.Decimal((sign, digits, exponent))
    
def pack_decimal64(decimal):
    '''
    Packs an IEEE 754-2008 64-bit decimal floating point number.
    '''
    if not decimal.is_finite():
        yield _decimal_pack_special(decimal, 8)
        return
    sign, digits, exponent = decimal.as_tuple()
    if len(digits) > 16 or (not -398 <= exponent <= 369):
        raise ValueError()
    significand = int(''.join(map(str, digits)))
    if significand >> 51 == 4:
        yield ((sign << 63) | (3 << 61) | ((exponent + 398) << 51) |
               (significand & 2251799813685247)).to_bytes(8, 'big')
    else:
        yield ((sign << 63) | ((exponent + 398) << 53) |
               significand).to_bytes(8, 'big')

def unpack_decimal128(data, pointer=0):
    '''
    Unpacks an IEEE 754-2008 128-bit decimal floating point number.
    '''
    integer = int.from_bytes(data[pointer:pointer + 16], 'big')
    sign = integer >> 127
    if (integer >> 125) & 3 == 3:
        if (integer >> 123) & 3 == 3:
            return pointer + 16, _decimal_unpack_special(sign, integer >> 119)
        exponent = ((integer >> 111) & 16383) - 6176
        significand = (10384593717069655257060992658440192 |
                       (integer & 2596148429267413814265248164610047))
    else:
        exponent = ((integer >> 113) & 16383) - 6176
        significand = integer & 10384593717069655257060992658440191
    digits = tuple(map(int, str(significand)))
    return pointer + 16, decimal.Decimal((sign, digits, exponent))
    
def pack_decimal128(decimal):
    '''
    Packs an IEEE 754-2008 128-bit decimal floating point number.
    '''
    if not decimal.is_finite():
        yield _decimal_pack_special(decimal, 16)
        return
    sign, digits, exponent = decimal.as_tuple()
    if len(digits) > 34 or (not -6176 <= exponent <= 6111):
        raise ValueError()
    significand = int(''.join(map(str, digits)))
    if significand >> 111 == 4:
        yield ((sign << 127) | (3 << 125) | ((exponent + 6176) << 111) |
               (significand & 2596148429267413814265248164610047)
               ).to_bytes(16, byteorder='big')
    else:
        yield ((sign << 127) | ((exponent + 6176) << 113) |
               significand).to_bytes(16, byteorder='big')

def unpack_varint(data, pointer=0):
    '''
    Unpacks a variable length integer.
    '''
    integer, shift = 0, 0
    while True:
        integer |= (data[pointer] & 127) << shift
        if not data[pointer] & 128:
            break
        pointer += 1
        shift += 7
    return pointer + 1, integer

def pack_varint(integer):
    '''
    Packs a variable length integer.
    '''
    while integer > 127:
        yield bytes([integer & 127 | 128])
        integer >>= 7
    yield bytes([integer])

def _unpack_size_8(data, pointer=0):
    size = (int.from_bytes(data[pointer:pointer + 2], 'big') & 8191) + 128 
    return pointer + 2, size

def _unpack_size_16(data, pointer=0):
    size = (int.from_bytes(data[pointer:pointer + 3], 'big') & 2097151) + 8320
    return pointer + 3, size

def _unpack_size_32(data, pointer=0):
    size = (int.from_bytes(data[pointer:pointer + 5], 'big') &
              137438953471) + 2105472
    return pointer + 5, size

def _unpack_size_64(data, pointer=0):
    size = (int.from_bytes(data[pointer:pointer + 9], 'big') &
              590295810358705651711) + 137441058944
    return pointer + 9, size

_SIZES = [_unpack_size_8, _unpack_size_16, _unpack_size_32,
          _unpack_size_64]

def unpack_size(data, pointer=0):
    '''
    Unpacks a size.
    '''
    if data[pointer] >> 7:
        return _SIZES[(data[pointer] >> 5) & 3](data, pointer)
    else:
        return pointer + 1, data[pointer]

def pack_size(size):
    '''
    Packs a size.
    '''
    if size < 128:
        yield bytes([size])
    elif size < 8320:
        yield (32768 | (size - 128)).to_bytes(2, 'big')
    elif size < 2105472:
        yield (10485760 | (size - 8320)).to_bytes(3, 'big')
    elif size < 137441058944:
        yield (824633720832 | (size - 2105472)).to_bytes(5, 'big')
    elif size < 590295810496146710656:
        yield (4132070672510939561984 | (size - 137441058944)
               ).to_bytes(9, 'big')
    else:
        raise ValueError()

def unpack_uuid(data, pointer=0):
    '''
    Unpacks an UUID.
    '''
    return pointer + 16, uuid.UUID(bytes=data[pointer:pointer + 16])

def pack_uuid(uuid):
    '''
    Packs an UUID.
    '''
    yield uuid.bytes

def unpack_ipv4(data, pointer=0):
    '''
    Unpacks an IPv4 address.
    '''
    return pointer + 4, ipaddress.IPv4Address(data[pointer:pointer + 4])

def pack_ipv4(ipv4address):
    '''
    Packs an IPv4 address.
    '''
    yield ipv4address.packed

def unpack_ipv6(data, pointer=0):
    '''
    Unpacks an IPv6 address.
    '''
    return pointer + 16, ipaddress.IPv6Address(data[pointer:pointer + 16])
    
def pack_ipv6(ipv6address):
    '''
    Packs an IPv4 address.
    '''
    yield ipv6address.packed

def unpack_date(data, pointer=0):
    '''
    Unpacks a date.
    '''
    integer = int.from_bytes(data[pointer:pointer + 3], 'big')
    day = integer >> 19
    month = (integer >> 15) & 15
    year = (integer >> 1) & 16383
    return pointer + 3, datetime.date(year, month, day)

def pack_date(date):
    '''
    Packs a date.
    '''
    yield ((date.day << 19) | (date.month << 15) | (date.year << 1)
           ).to_bytes(3, 'big')

def unpack_time(data, pointer=0):
    '''
    Unpacks a time.
    '''
    integer = int.from_bytes(data[pointer:pointer + 3], 'big')
    hour = integer >> 19
    minute = (integer >> 13) & 63
    second = (integer >> 7) & 63
    pointer += 3
    if (integer >> 6) & 1:
        microsecond = (((integer & 15) << 16) |
                       int.from_bytes(data[pointer:pointer + 2], 'big'))
        pointer += 2
    else:
        microsecond = 0
    if (integer >> 5) & 1:
        integer = int.from_bytes(data[pointer:pointer + 2], 'big')
        sign = (-1) ** (integer >> 15)
        minutes = sign * ((integer >> 4) & 2047)
        tzinfo = datetime.timezone(datetime.timedelta(minutes=minutes))
        pointer += 2
    else:
        tzinfo = None
    return pointer, datetime.time(hour, minute, second, microsecond, tzinfo)

def pack_time(time):
    '''
    Packs a time.
    '''
    integer = (time.hour << 19) | (time.minute << 13) | (time.second << 7)
    size = 3
    if time.microsecond: integer |= 1 << 6
    if time.tzinfo: integer |= 1 << 5
    if time.microsecond:
        integer <<= 16
        integer |= time.microsecond
        size += 2
    if time.tzinfo:
        offset = time.utcoffset()
        if offset:
            integer <<= 16
            minutes = int(offset.total_seconds() / 60)
            if minutes < 0:
                integer |= 1 << 15
            integer |= abs(minutes) << 4
            size += 2
    yield integer.to_bytes(size, 'big')

def unpack_bytes(data, pointer=0, size=-1, fill=b'\x00'):
    '''
    Unpacks Bytes.
    '''
    if size < 0:
        pointer, size = unpack_size(data, pointer)
    return pointer + size, data[pointer:pointer + size]

def pack_bytes(bytes_, size=-1, fill=b'\x00'):
    '''
    Packs Bytes.
    '''
    if size < 0:
        yield from pack_size(len(bytes_))
        yield bytes_
    else:
        missing = size - len(bytes_)
        if missing < 0 or (missing > 0 and fill is None):
            raise ValueError()
        yield bytes_
        yield fill * missing

def unpack_string(data, pointer=0, size=-1, fill=b' ', encoding='utf-8'):
    '''
    Unpacks a string.
    '''
    pointer, bytes_ = unpack_bytes(data, pointer, size)
    return pointer, bytes_.decode(encoding)

def pack_string(string, size=-1, fill=b' ', encoding='utf-8'):
    '''
    Packs a string.
    '''
    yield from pack_bytes(string.encode(encoding), size, fill)

def unpack_boolean(data, pointer=0):
    '''
    Unpacks a boolean value.
    '''
    if data[pointer]:
        return pointer + 1, True
    return pointer + 1, False

def pack_boolean(boolean):
    '''
    Packs a boolean value.
    '''
    if boolean:
        yield b'\x01'
    else:
        yield b'\x00'

SINT8 = Primitive('SINT8', unpack_sint8, pack_sint8, 1)
UINT8 = Primitive('UINT8', unpack_uint8, pack_uint8, 1)
SINT16 = Primitive('SINT16', unpack_sint16, pack_sint16, 2)
UINT16 = Primitive('UINT16', unpack_uint16, pack_uint16, 2)
SINT32 = Primitive('SINT32', unpack_sint32, pack_sint32, 4)
UINT32 = Primitive('UINT32', unpack_uint32, pack_uint32, 4)
SINT64 = Primitive('SINT64', unpack_sint64, pack_sint64, 8)
UINT64 = Primitive('UINT64', unpack_uint64, pack_uint64, 8)
FLOAT = Primitive('FLOAT', unpack_float, pack_float, 4)
DOUBLE = Primitive('DOUBLE', unpack_double, pack_double, 8)

DECIMAL32 = Primitive('DECIMAL32', unpack_decimal32, pack_decimal32, 4)
DECIMAL64 = Primitive('DECIMAL64', unpack_decimal64, pack_decimal64, 8)
DECIMAL128 = Primitive('DECIMAL128', unpack_decimal128, pack_decimal128, 16)

VARINT = Primitive('VARINT', unpack_varint, pack_varint)

SIZE = Primitive('SIZE', unpack_size, pack_size)

UUID = Primitive('UUID', unpack_uuid, pack_uuid, 16)

IPV4 = Primitive('IPV4', unpack_ipv4, pack_ipv4, 4)
IPV6 = Primitive('IPV6', unpack_ipv6, pack_ipv6, 16)

DATE = Primitive('DATE', unpack_date, pack_date)
TIME = Primitive('TIME', unpack_time, pack_time)

BYTES = Primitive('BYTES', unpack_bytes, pack_bytes)
STRING = Primitive('STRING', unpack_string, pack_string)

BOOLEAN = Primitive('BOOLEAN', unpack_boolean, pack_boolean, 1)
