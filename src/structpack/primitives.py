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
StructPack primitive data types
'''

import datetime
import decimal
import ipaddress
import struct
import uuid

__all__ = ['unpack_sint8', 'pack_sint8', 'unpack_uint8', 'pack_uint8',
           'unpack_sint16', 'pack_sint16', 'unpack_uint16', 'pack_uint16', 
           'unpack_sint32', 'pack_sint32', 'unpack_uint32', 'pack_uint32', 
           'unpack_sint64', 'pack_sint64', 'unpack_uint64', 'pack_uint64',
           'unpack_float', 'pack_float', 'unpack_double', 'pack_double',
           'unpack_decimal32', 'pack_decimal32', 'unpack_decimal64',
           'pack_decimal64', 'unpack_decimal128', 'pack_decimal128',
           'unpack_varint', 'pack_varint', 'unpack_length', 'pack_length',
           'unpack_uuid', 'pack_uuid', 'unpack_ipv4', 'pack_ipv4',
           'unpack_ipv6', 'pack_ipv6', 'unpack_date', 'pack_date',
           'unpack_time', 'pack_time']

_struct_sint8 = struct.Struct('!b')

def unpack_sint8(data, pointer=0):
    '''
    Unpacks a signed 8-bit integer.
    '''
    return pointer + 1, _struct_sint8.unpack(data[pointer:pointer + 1])[0]

def pack_sint8(integer):
    '''
    Packs a signed 8-bit integer.
    '''
    yield _struct_sint8.pack(integer)

_struct_uint8 = struct.Struct('!B')

def unpack_uint8(data, pointer=0):
    '''
    Unpacks an unsigned 8-bit integer.
    '''
    return pointer + 1, _struct_uint8.unpack(data[pointer:pointer + 1])[0]

def pack_uint8(integer):
    '''
    Packs an unsigned 8-bit integer.
    '''
    yield _struct_uint8.pack(integer)

_struct_sint16 = struct.Struct('!h')

def unpack_sint16(data, pointer=0):
    '''
    Unpacks a signed 16-bit integer.
    '''
    return pointer + 2, _struct_sint16.unpack(data[pointer:pointer + 2])[0]
    
def pack_sint16(integer):
    '''
    Packs a signed 16-bit integer.
    '''
    yield _struct_sint16.pack(integer)

_struct_uint16 = struct.Struct('!H')

def unpack_uint16(data, pointer=0):
    '''
    Unpacks an unsigned 16-bit integer.
    '''
    return pointer + 2, _struct_uint16.unpack(data[pointer:pointer + 2])[0]

def pack_uint16(integer):
    '''
    Packs an unsigned 16-bit integer.
    '''
    yield _struct_uint16.pack(integer)

_struct_sint32 = struct.Struct('!i')

def unpack_sint32(data, pointer=0):
    '''
    Unpacks a signed 32-bit integer.
    '''
    return pointer + 4, _struct_sint32.unpack(data[pointer:pointer + 4])[0]

def pack_sint32(integer):
    '''
    Packs a signed 32-bit integer.
    '''
    yield _struct_sint32.pack(integer)

_struct_uint32 = struct.Struct('!I')

def unpack_uint32(data, pointer=0):
    '''
    Unpacks an unsigned 32-bit integer.
    '''
    return pointer + 4, _struct_uint32.unpack(data[pointer:pointer + 4])[0]

def pack_uint32(integer):
    '''
    Packs an unsigned 32-bit integer.
    '''
    yield _struct_uint32.pack(integer)

_struct_sint64 = struct.Struct('!q')

def unpack_sint64(data, pointer=0):
    '''
    Unpacks a signed 64-bit integer.
    '''
    return pointer + 8, _struct_sint64.unpack(data[pointer:pointer + 8])[0]
    
def pack_sint64(integer):
    '''
    Packs a signed 64-bit integer.
    '''
    yield _struct_sint64.pack(integer)

_struct_uint64 = struct.Struct('!Q')

def unpack_uint64(data, pointer=0):
    '''
    Unpacks an unsigned 64-bit integer.
    '''
    return pointer + 8, _struct_uint64.unpack(data[pointer:pointer + 8])[0]
    
def pack_uint64(integer):
    '''
    Packs an unsigned 64-bit integer.
    '''
    yield _struct_uint64.pack(integer)

_struct_float = struct.Struct('!f')

def unpack_float(data, pointer=0):
    '''
    Unpacks an IEEE 754 single precision float. 
    '''
    return pointer + 4, _struct_float.unpack(data[pointer:pointer + 4])[0]
    
def pack_float(number):
    '''
    Packs an IEEE 754 single precision float.
    '''
    yield _struct_float.pack(number)
    
_struct_double = struct.Struct('!d')

def unpack_double(data, pointer=0):
    '''
    Unpacks an IEEE 754 double precision float. 
    '''
    return pointer + 8, _struct_double.unpack(data[pointer:pointer + 8])[0]

def pack_double(number):
    '''
    Packs an IEEE 754 double precision float.
    '''
    yield _struct_double.pack(number)
    
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

def _unpack_length_8(data, pointer=0):
    length = (int.from_bytes(data[pointer:pointer + 2], 'big') & 8191) + 128 
    return pointer + 2, length

def _unpack_length_16(data, pointer=0):
    length = (int.from_bytes(data[pointer:pointer + 3], 'big') & 2097151) + 8320
    return pointer + 3, length

def _unpack_length_32(data, pointer=0):
    length = (int.from_bytes(data[pointer:pointer + 5], 'big') &
              137438953471) + 2105472
    return pointer + 5, length

def _unpack_length_64(data, pointer=0):
    length = (int.from_bytes(data[pointer:pointer + 9], 'big') &
              590295810358705651711) + 137441058944
    return pointer + 9, length

_LENGTH_SIZES = [_unpack_length_8, _unpack_length_16, _unpack_length_32,
                 _unpack_length_64]

def unpack_length(data, pointer=0):
    '''
    Unpacks a length.
    '''
    if data[pointer] >> 7:
        return _LENGTH_SIZES[(data[pointer] >> 5) & 3](data, pointer)
    else:
        return pointer + 1, data[pointer]

def pack_length(length):
    '''
    Packs a length.
    '''
    if length < 128:
        yield bytes([length])
    elif length < 8320:
        yield (32768 | (length - 128)).to_bytes(2, 'big')
    elif length < 2105472:
        yield (10485760 | (length - 8320)).to_bytes(3, 'big')
    elif length < 137441058944:
        yield (824633720832 | (length - 2105472)).to_bytes(5, 'big')
    elif length < 590295810496146710656:
        yield (4132070672510939561984 | (length - 137441058944)
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
