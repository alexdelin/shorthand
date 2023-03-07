#!/usr/bin/env/python

import argparse
import logging

from shorthand.utils.config import _get_notes_config, CONFIG_FILE_LOCATION
from shorthand.elements.todos import _get_todos
from shorthand.stamping import _stamp_notes


log = logging.getLogger(__name__)


def run():
    args = parse_args()
    main(args)


def main(args):
    """Main method
    """

    notes_config = _get_notes_config()
    notes_directory = notes_config['notes_directory']

    if args.action == 'stamp':
        cli_stamp_notes(notes_config)

    elif args.action == 'list':
        log.info('Listing Todos')
        print(_get_todos(notes_directory, args.status))


def cli_stamp_notes(notes_config):
    log.info('Stamping Notes')
    changes = _stamp_notes(notes_config['notes_directory'],
                           grep_path=notes_config['grep_path'])
    for file in changes.keys():
        print(f'\n<<--{file}-->>')
        for change in changes[file]:
            print('    {line_num}(old):{old}'.format(
                line_num=change['line_number'], old=change['before']))
            print('    {line_num}(new):{new}'.format(
                line_num=change['line_number'], new=change['after']))


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--action', required=True,
                        choices=['stamp', 'list'],
                        help='Action to take')
    parser.add_argument('--status', required=False,
                        choices=['completed', 'incomplete', 'skipped'],
                        default='incomplete',
                        help='To-Do Status to show')
    parser.add_argument('--config', required=False,
                        default=CONFIG_FILE_LOCATION,
                        help='Config file to use')
    return parser.parse_args()


if __name__ == '__main__':
    run()
