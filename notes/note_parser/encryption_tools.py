'''
Encryption tools for noteparser.

This module includes tools for helping with managing two
copies of notes repos on a single machine.
1. An encrypted copy of the notes, which can be stored
   in an untrusted medium like a github repo, google drive, etc
2. A decrypted copy of the notes which can be used for working
   on the notes.

The tools included here are used to keep both copies of the notes in sync.
'''

from noteparser.utils.crypto import AESCipher
from noteparser.utils.config import get_notes_config


NOTES_CONFIG = get_notes_config()
notes
encryption_key = NOTES_CONFIG.get('encryption_key')


def pack_notes():
    '''Take the current state of the unencrypted notes and
    apply any changes to the encrypted version of the notes
    '''
    pass
