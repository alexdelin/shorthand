# Git Utilities
import logging
from subprocess import Popen, PIPE


log = logging.getLogger(__name__)


def pull_repo(notes_directory, git_path='git'):
    '''pull the git repo containing the notes
    '''
    pull_command = f'cd {notes_directory} && {git_path} pull'
    proc = Popen(pull_command,
                 stdout=PIPE, stderr=PIPE,
                 shell=True)
    output, err = proc.communicate()
    if err:
        log.error(f'Unable to pull notes directory {notes_directory}. Got Error: {err}')
        raise ValueError(f'Got error when attempting to pull notes directory {err}')
    else:
        log.info(f'Successfully pulled notes directory {notes_directory}')
        return f'Successfully pulled notes directory {notes_directory}'
