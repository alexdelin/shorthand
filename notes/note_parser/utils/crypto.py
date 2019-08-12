'''
A module for very simple and reasonably
efficint encryption & decryption via AES
with hashes for quickly comparing between
plaintext and encrypted content
'''

import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class CryptoHelper(object):

    def __init__(self, key):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        '''Encrypt a string, using an initialization vector
        which is specified manually
        '''
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.urlsafe_b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        '''Decrypt a string encrypted using the `encrypt()` method
        '''
        enc = base64.urlsafe_b64decode(enc)
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

    def hash_string(self, input_string, size=20):

        complete_hash = hashlib.sha256(input_string).hexdigest()
        truncated_hash = complete_hash[-size:]
        return truncated_hash

    def mask_string(self, input_string):
        '''Consumes a string to process, and returns a string that includes
        both a truncated hash of the input contents and an encrypted copy of
        the input contents
        '''

        content_hash = self.hash_string(input_string)
        encrypted_content = cipher.encrypt(input_string)
        full_output = content_hash + '@' + encrypted_content
        return full_output

    def unmask_string(self, masked_string):
        '''Consumes a masked string and decrypts the encrypted contents
        and verifies the hash of the contents
        '''
        split_mask = masked_string.split('@')
        content_hash = split_mask[0]
        encrypted_content = split_mask[1]
        decrypted_content = self.decrypt(encrypted_content)
        decrypted_hash = self.hash_string(decrypted_content)
        if decrypted_hash != content_hash:
            raise ValueError('Computed hash does not match expected value')
        return decrypted_content
