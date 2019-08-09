'''
A module for very simple and reasonably
efficint encryption & decryption via AES

This implementation is designed to produce deterministic but
pseudo-random initialization vectors for use with AES-CBC
encryption.
    - While this is not widely considered best practice, the
      property of having deterministic encryption is extremely
      useful for tracking line-level file changes
    - The security implications of this approach are acceptable
      for this use case. Attackers will be able to tell that two
      lines are identical (even across files) and will know the
      hash of each line, but each of these weaknesses have
      negligible impact on the overall security of the approach
'''

import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher(object):

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw, iv):
        '''Encrypt a string, using an initialization vector
        which is specified manually
        '''
        raw = self._pad(raw)
        # iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        '''Decrypt a string encrypted using the `encrypt()` method
        '''
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        '''Ensure that the total length is a multiple of 32 characters (256 bits)
        with at least 1 character always added
        '''
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        '''Remove the extra padding characters at the end added by `_pad()`
        '''
        return s[:-ord(s[len(s)-1:])]


def encrypt_file_path(cipher, file_path):
    '''Encrypts a file path deterministically such that
    the folder structure is preserved
    '''
    pass


def encrypt_file_contents(cipher, file_path, file_contents):
    '''Encrypts the
    '''
    pass
