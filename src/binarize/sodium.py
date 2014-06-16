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

import base64
import collections
import ctypes
import ctypes.util

_library = ctypes.util.find_library('sodium')
if not _library:
    raise OSError('unable to find libsodium')
    
_libsodium = ctypes.CDLL(_library)
_libsodium.sodium_version_string.restype = ctypes.c_char_p
_libsodium.crypto_box_primitive.restype = ctypes.c_char_p
_libsodium.crypto_secretbox_primitive.restype = ctypes.c_char_p
_libsodium.crypto_sign_primitive.restype = ctypes.c_char_p
_libsodium.crypto_auth_primitive.restype = ctypes.c_char_p

_libsodium.sodium_init()

_Version = collections.namedtuple('Version', ['string', 'major', 'minor'])

version_string = _libsodium.sodium_version_string().decode('ascii')
version_major = _libsodium.sodium_library_version_major()
version_minor = _libsodium.sodium_library_version_minor()

version = _Version(version_string, version_major, version_minor)

def randombytes(size):
    buffer = ctypes.create_string_buffer(size)
    _libsodium.randombytes(buffer, size)
    return buffer.raw

class Key(bytes):
    @classmethod
    def from_hex(cls, key):
        return cls(base64.b16decode(key.upper().encode('ascii')))
    
    @classmethod
    def from_base32(cls, key):
        return cls(base64.b32decode(key.encode('ascii')))
        
    @classmethod
    def from_base64(cls, key):
        return cls(base64.b64decode(key.encode('ascii')))
    
    @property
    def hex(self):
        return base64.b16encode(self).decode('ascii')
    
    @property
    def base32(self):
        return base64.b32encode(self).decode('ascii')
    
    @property
    def base64(self):
        return base64.b64encode(self).decode('ascii')
    
class Box():
    PUBLIC_KEY_SIZE = _libsodium.crypto_box_publickeybytes()
    SECRET_KEY_SIZE = _libsodium.crypto_box_secretkeybytes()
    NONCE_SIZE = _libsodium.crypto_box_noncebytes()
    PRIMITIVE = _libsodium.crypto_box_primitive().decode('ascii')
    
    _SHARED_KEY_SIZE = _libsodium.crypto_box_beforenmbytes()    
    _ZERO_SIZE = _libsodium.crypto_box_zerobytes()
    _ZERO_BOX_SIZE = _libsodium.crypto_box_boxzerobytes()
    _MAC_SIZE = _libsodium.crypto_box_macbytes()
    
    @staticmethod
    def generate_public_key(secret_key):
        public_key = ctypes.create_string_buffer(Box.PUBLIC_KEY_SIZE)
        assert not _libsodium.crypto_scalarmult_base(public_key, secret_key)
        return Key(public_key.raw)
    
    @staticmethod
    def generate_keypair():
        public_key = ctypes.create_string_buffer(Box.PUBLIC_KEY_SIZE)
        secret_key = ctypes.create_string_buffer(Box.SECRET_KEY_SIZE)
        assert not _libsodium.crypto_box_keypair(public_key, secret_key)
        return Key(public_key.raw), Key(secret_key.raw)
    
    @classmethod
    def generate(cls):
        return cls(*Box.generate_keypair())
    
    def __init__(self, public_key, secret_key):
        if isinstance(public_key, Key):
            self._public_key = public_key
        else:
            self._public_key = Key(public_key)
        if isinstance(secret_key, Key):
            self._secret_key = secret_key
        else:
            self._secret_key = Key(secret_key)
        assert len(self._public_key) == Box.PUBLIC_KEY_SIZE
        assert len(self._secret_key) == Box.SECRET_KEY_SIZE
        shared_key = ctypes.create_string_buffer(self._SHARED_KEY_SIZE)
        assert not _libsodium.crypto_box_beforenm(shared_key, public_key,
                                                  secret_key)
        self._shared_key = shared_key.raw
        
    @property
    def public_key(self):
        return self._public_key
    
    @property
    def secret_key(self):
        return self._secret_key
     
    def encrypt(self, message, nonce=None):
        nonce = nonce or randombytes(Box.NONCE_SIZE)
        assert len(nonce) == Box.NONCE_SIZE
        plaintext = b'\x00' * Box._ZERO_SIZE + message
        length = len(plaintext)
        ciphertext = ctypes.create_string_buffer(length)
        assert not _libsodium.crypto_box_afternm(ciphertext, plaintext, length,
                                                 nonce, self._shared_key)
        return nonce + ciphertext.raw[Box._ZERO_BOX_SIZE:]

    def decrypt(self, message, nonce=None):
        if nonce:
            ciphertext = message
        else:
            nonce = message[:Box.NONCE_SIZE]
            ciphertext = message[Box.NONCE_SIZE:]
        assert len(nonce) == Box.NONCE_SIZE
        ciphertext = b'\x00' * Box._ZERO_BOX_SIZE + ciphertext
        length = len(ciphertext)
        plaintext = ctypes.create_string_buffer(length)
        assert not _libsodium.crypto_box_open_afternm(plaintext, ciphertext,
                                                      length, nonce,
                                                      self._shared_key)
        return plaintext.raw[Box._ZERO_SIZE:]

class SecretBox():    
    KEY_SIZE = _libsodium.crypto_secretbox_keybytes()
    NONCE_SIZE = _libsodium.crypto_secretbox_noncebytes()    
    PRIMITIVE = _libsodium.crypto_secretbox_primitive().decode('ascii')
    
    _ZERO_SIZE = _libsodium.crypto_secretbox_zerobytes()
    _ZERO_BOX_SIZE = _libsodium.crypto_secretbox_boxzerobytes()    
    _MAC_SIZE = _libsodium.crypto_secretbox_macbytes()
    
    @staticmethod
    def generate_key():
        return Key(randombytes(SecretBox.KEY_SIZE))
    
    @classmethod
    def generate(cls):
        return cls(SecretBox.generate_key())
    
    def __init__(self, key):
        assert len(key) == SecretBox.KEY_SIZE
        if isinstance(key, Key):
            self._key = key
        else:
            self._key = Key(key)

    @property
    def key(self):
        return self._key
    
    def encrypt(self, message, nonce=None):
        nonce = nonce or randombytes(SecretBox.NONCE_SIZE)
        assert len(nonce) == SecretBox.NONCE_SIZE
        plaintext = b'\x00' * SecretBox._ZERO_SIZE + message
        length = len(plaintext)
        ciphertext = ctypes.create_string_buffer(length)
        assert not _libsodium.crypto_secretbox(ciphertext, plaintext, length,
                                               nonce, self._key)
        return nonce + ciphertext.raw[SecretBox._ZERO_BOX_SIZE:]
        
    def decrypt(self, message, nonce=None):
        if nonce:
            ciphertext = message
        else:
            nonce = message[:SecretBox.NONCE_SIZE]
            ciphertext = message[SecretBox.NONCE_SIZE:]
        assert len(nonce) == SecretBox.NONCE_SIZE
        ciphertext = b'\x00' * SecretBox._ZERO_BOX_SIZE + ciphertext
        length = len(ciphertext)
        plaintext = ctypes.create_string_buffer(length)
        assert not _libsodium.crypto_secretbox_open(plaintext, ciphertext,
                                                    length, nonce, self._key)
        return plaintext[SecretBox._ZERO_SIZE:]

class Signing():    
    SIGNATURE_SIZE = _libsodium.crypto_sign_bytes()
    
    VERIFY_KEY_SIZE = _libsodium.crypto_sign_publickeybytes()
    SIGN_KEY_SIZE = _libsodium.crypto_sign_secretkeybytes()
    PRIMITIVE = _libsodium.crypto_sign_primitive().decode('ascii')
    
    SEED_SIZE = _libsodium.crypto_sign_seedbytes()
    
    class Message(bytes):
        @property
        def signature(self):
            return self[:Signing.SIGNATURE_SIZE]
        
        @property
        def message(self):
            return self[Signing.SIGNATURE_SIZE:]
        
    @staticmethod
    def generate_seed():
        return Key(randombytes(Signing.SEED_SIZE))
    
    @staticmethod
    def generate_keypair(seed=None):
        verify_key = ctypes.create_string_buffer(Signing.VERIFY_KEY_SIZE)
        sign_key = ctypes.create_string_buffer(Signing.SIGN_KEY_SIZE)        
        if seed:
            assert len(seed) == Signing.SEED_SIZE
            assert not _libsodium.crypto_sign_seed_keypair(verify_key,
                                                           sign_key, seed)
        else:
            assert not _libsodium.crypto_sign_keypair(verify_key, sign_key)
        return Key(verify_key), Key(sign_key)
    
    @classmethod
    def generate(cls, seed=None):
        verify_key, sign_key = Signer.generate_keypair(seed)
        return cls(verify_key, sign_key, seed)
    
    def __init__(self, verify_key, sign_key=None, seed=None):
        if isinstance(verify_key, Key):
            self._verify_key = verify_key
        else:
            self._verify_key = Key(verify_key)
        if  sign_key is None:
            self._sign_key = None
        elif isinstance(sign_key, Key):
            self._sign_key = sign_key
        else:
            self._sign_key = Key(sign_key)
        if seed is None:
            self._seed = None
        elif isinstance(seed, Key):
            self._seed = seed
        else:
            self._seed = Key(seed)

    @property
    def verify_key(self):
        return self._verify_key
    
    @property
    def sign_key(self):
        return self._sign_key
    
    @property
    def seed(self):
        return self._seed
    
    def sign(self, message):
        assert self._sign_key is not None
        length = len(message)
        signature = ctypes.create_string_buffer(length +
                                                Signing.SIGNATURE_SIZE)
        assert not _libsodium.crypto_sign(signature,
                                          ctypes.pointer(ctypes.c_ulonglong()),
                                          message, length, self._sign_key)
        return Signing.Message(signature.raw)
        
    def verify(self, message, signature=None):
        if signature:
            signed_message = signature + message
        else:
            signed_message = message
        length = len(signed_message)
        message = ctypes.create_string_buffer(length)
        message_length = ctypes.pointer(ctypes.c_ulonglong())
        assert not _libsodium.crypto_sign_open(message, message_length,
                                               signed_message, length,
                                               self._verify_key)
        return signed_message[Signing.SIGNATURE_SIZE:]

class Authentication():
    TOKEN_SIZE = _libsodium.crypto_auth_bytes()
    KEY_SIZE = _libsodium.crypto_auth_keybytes()    
    PRIMITIVE = _libsodium.crypto_auth_primitive()
    
    class Message(bytes):
        @property
        def token(self):
            return self[:Authentication.TOKEN_SIZE]
        
        @property
        def message(self):
            return self[Authentication.TOKEN_SIZE:]
    
    @staticmethod
    def generate_key():
        return Key(randombytes(Authentication.KEY_SIZE))
    
    @classmethod
    def generate(cls):
        return cls(Authentication.generate_key())
    
    def __init__(self, key):
        assert len(key) == Authentication.KEY_SIZE
        if isinstance(key, Key):
            self._key = key
        else:
            self._key = Key(key)
    
    def auth(self, message):
        length = len(message)
        token = ctypes.create_string_buffer(Authentication.TOKEN_SIZE)
        assert not _libsodium.crypto_auth(token, message, length, self._key)
        return Authentication.Message(token.raw + message)
    
    def verify(self, message, token=None):
        if not token:
             token = message[:Authentication.TOKEN_SIZE]
             message = message[Authentication.TOKEN_SIZE:]
        length = len(message)
        assert not _libsodium.crypto_auth_verify(token, message, length,
                                                 self._key)
        return message

if __name__ == '__main__':
    # Public Key Cryptography
    pbob, sbob = Box.generate_keypair()
    palice, salice = Box.generate_keypair()
    
    bob = Box(palice, sbob)
    alice = Box(pbob, salice)

    message = bob.encrypt(b'Hello Alice!')
    print(alice.decrypt(message))

    message = alice.encrypt(b'Hello Bob!')
    print(bob.decrypt(message))

    
    # Secret Key Cryptography
    secret = SecretBox.generate_key()

    bob = SecretBox(secret)
    alice = SecretBox(secret)

    message = bob.encrypt(b'Hello Alice!')
    print(alice.decrypt(message))

    message = alice.encrypt(b'Hello Bob!')
    print(bob.decrypt(message))
    
    
    # Digital Signatures
    vbob, sbob = Signing.generate_keypair()
    valice, salice = Signing.generate_keypair()
        
    bob = Signing(vbob, sbob)
    alice = Signing(valice, salice)
    
    alice_bob = Signing(vbob)
    bob_alice = Signing(valice)
    
    message = bob.sign(b'Hello Alice!')
    print(alice_bob.verify(message))
    
    message = alice.sign(b'Hello Bob!')
    print(bob_alice.verify(message))
    
    
    # HMAC based Authentication
    secret = Authentication.generate_key()
       
    bob = Authentication(secret)
    alice = Authentication(secret)
    
    message = bob.auth(b'Hello Alice!')
    print(alice.verify(message))
    
    message = alice.auth(b'Hello Bob!')
    print(bob.verify(message))
