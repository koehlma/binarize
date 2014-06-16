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
import binascii
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

class EncodeableBytesMixin():
    @classmethod
    def from_hex(cls, key):
        return cls(binascii.unhexlify(key.upper().encode('ascii')))
    
    @classmethod
    def from_base32(cls, key):
        return cls(base64.b32decode(key.encode('ascii')))
        
    @classmethod
    def from_base64(cls, key):
        return cls(base64.b64decode(key.encode('ascii')))
    
    @property
    def hex(self):
        return binascii.hexlify(self).decode('ascii')
    
    @property
    def base32(self):
        return base64.b32encode(self).decode('ascii')
    
    @property
    def base64(self):
        return base64.b64encode(self).decode('ascii')

class HashableBytesMixin():
    @property
    def sha256(self):
        return hash_sha256(self)
    
    @property
    def sha512(self):
        return hash_sha512(self)
    
class Key(bytes, EncodeableBytesMixin, HashableBytesMixin):
    def __str__(self):
        return '<Key: "{}">'.format(self.base64)

class Seed(bytes, EncodeableBytesMixin, HashableBytesMixin):
    def __str__(self):
        return '<Seed: "{}">'.format(self.hex)

class Digest(bytes, EncodeableBytesMixin, HashableBytesMixin):
    def __str__(self):
        return '<Digest: "{}">'.format(self.hex)

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
        return Seed(randombytes(Signing.SEED_SIZE))
    
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
        elif isinstance(seed, Seed):
            self._seed = seed
        else:
            self._seed = Seed(seed)

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

class Hash():
    name = None
    size = None     
    algorithm = None  
    
    def __bytes__(self):
        return self.digest
    
class SHA256(Hash):
    name = 'sha256'
    size = _libsodium.crypto_hash_sha256_bytes()
    
    class State(ctypes.Structure):
        _fields_ = [('state', ctypes.c_uint * 8),
                    ('count', ctypes.c_uint * 2),
                    ('buffer', ctypes.c_char * 64)]  

    State.size = ctypes.sizeof(State)
    
    def __init__(self, inital=None):
        self._state = SHA256.State()
        self._pointer = ctypes.pointer(self._state)
        _libsodium.crypto_hash_sha256_init(self._pointer)
        if inital: self.update(inital)
    
    def update(self, chunk):
        _libsodium.crypto_hash_sha256_update(self._pointer, chunk, len(chunk))
    
    @property
    def digest(self):
        state = SHA256.State()
        pointer = ctypes.pointer(state)
        ctypes.memmove(pointer, self._pointer, SHA256.State.size)
        digest = ctypes.create_string_buffer(SHA256.size)
        _libsodium.crypto_hash_sha256_final(pointer, digest)
        return Digest(digest.raw)
    
class SHA512(Hash):
    name = 'sha512'
    size = _libsodium.crypto_hash_sha512_bytes()
    
    class State(ctypes.Structure):
        _fields_ = [('state', ctypes.c_uint64 * 8),
                    ('count', ctypes.c_uint64 * 2),
                    ('buffer', ctypes.c_char * 128)]  

    State.size = ctypes.sizeof(State)
    
    def __init__(self, inital=None):
        self._state = SHA512.State()
        self._pointer = ctypes.pointer(self._state)
        _libsodium.crypto_hash_sha512_init(self._pointer)
        if inital: self.update(inital)
    
    def update(self, chunk):
        _libsodium.crypto_hash_sha512_update(self._pointer, chunk, len(chunk))
    
    @property
    def digest(self):
        state = SHA512.State()
        pointer = ctypes.pointer(state)
        ctypes.memmove(pointer, self._pointer, SHA512.State.size)
        digest = ctypes.create_string_buffer(SHA512.size)
        _libsodium.crypto_hash_sha512_final(pointer, digest)
        return Digest(digest.raw)

class BLAKE2(Hash):
    name = 'blake2'
    min_size = _libsodium.crypto_generichash_blake2b_bytes_min()
    max_size = _libsodium.crypto_generichash_blake2b_bytes_max()
    default_size = _libsodium.crypto_generichash_blake2b_bytes()
    size = range(min_size, max_size + 1)
    min_key_size = _libsodium.crypto_generichash_blake2b_keybytes_min()
    max_key_size = _libsodium.crypto_generichash_blake2b_keybytes_max()
    default_key_size = _libsodium.crypto_generichash_blake2b_keybytes()
    key_size = range(min_key_size, max_key_size + 1)
    SALT_SIZE = _libsodium.crypto_generichash_blake2b_saltbytes()
    PERSONAL_SIZE = _libsodium.crypto_generichash_blake2b_personalbytes()
    
def hash_sha256(buffer):
    digest = ctypes.create_string_buffer(SHA256.size)
    _libsodium.crypto_hash_sha256(digest, buffer, len(buffer))
    return Digest(digest.raw)

def hash_sha512(buffer):
    digest = ctypes.create_string_buffer(SHA512.size)
    _libsodium.crypto_hash_sha512(digest, buffer, len(buffer))
    return Digest(digest.raw)

def hash_blake2(buffer, size=BLAKE2.default_size, key=None, salt=None,
                personal=None):
    assert size in BLAKE2.size
    digest = ctypes.create_string_buffer(size)
    if key:
        key_length = len(key)
        assert key_length in BLAKE2.key_size
    else:
        key_length = 0    
    if salt and personal:
        assert len(salt) == BLAKE2.SALT_SIZE
        assert len(personal) == BLAKE2.PERSONAL_SIZE
        _libsodium.crypto_generichash_blake2b_salt_personal(digest, size,
                                                            buffer,
                                                            len(buffer),
                                                            key, key_length,
                                                            salt, personal)
    else:
        _libsodium.crypto_generichash_blake2b(digest, size, buffer,
                                              len(buffer), key, key_length) 
    return Digest(digest.raw)

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
    
    
    # Hashing
    import hashlib
    
    msg = b'Hello World!'
    
    sha256 = SHA256()
    sha256.update(msg)
    
    print(sha256.digest)   
    print(hashlib.sha256(msg).hexdigest())
    
    sha512 = SHA512()
    sha512.update(msg)
     
    print(sha512.digest)
    print(hashlib.sha512(msg).hexdigest())
    
    print(hash_blake2(msg))
    
