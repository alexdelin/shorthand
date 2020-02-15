import csv


ALLOWED_CONFIG_KEYS = [
    "rec", "mandatory", "unique", "key",
    "allowed", "prohibit", "size", "typedef",
    "type", "auto", "sort", "doc"]

FIELD_LIST_FIELDS = [
    'mandatory', 'unique', 'allowed',
    'prohibit', 'auto', 'sort']

PRIMITIVE_TYPES = [
    "int", "line", "date", "bool", "real"]


def load_from_file(file_path):
    '''Load one or more record sets from a rec file
    '''

    with open(file_path, 'r') as rec_file_object:
        rec_file_content = rec_file_object.read()

    return load_from_string(rec_file_content)


def load_from_string(input_string):
    '''Load one or more record sets from a string
    1. Read out all record set config from the file, and
       instantiate a new RecordSet object with that config
    2. Add each record into the record set until all are
       consumed
    3. Return the resulting record set object
    '''

    split_lines = input_string.split('\n')
    field_config = {}
    # Loop through all lines until we reach the end of the field config
    field_config_start = False
    field_config_item = None
    for idx, line in enumerate(split_lines):

        if not line.strip():
            # Blank Line
            if field_config_start:
                break
            else:
                continue

        if line[0] == '#':
            # Comments
            continue

        if line[0] not in ['+', '%']:
            if field_config_start:
                raise ValueError(f'Invalid Syntax. Line "{line}" in field '
                                 f'config does not start with either "%" '
                                 f'or "+"')
                                 
        if line[0] == '+':
            # we already got this content when 
            # processing the line above
            continue

        #TODO - switch over to using a regex
        if line[0] == '%':
            key = line.split(':', 1)[0][1:]
            value = line.split(':', 2)[1].strip()
            # check to see if there is more to the value on the next line
            lookahead = 1
            while true:
                next_line = split_lines[idx + lookahead]
                if next_line[0] == '+' and len(next_line.strip()) > 2:
                    value = value + ' ' + next_line.strip()
                    #TODO- handle comments in enum definitions
                    lookahead += 1
                else:
                    break

            if key not in ALLOWED_CONFIG_KEYS:
                raise ValueError(f'unknown config key {key} specified')

            if key == 'rec':
                # only keep the first word
                field_config[key] = value.strip().split(' ')[0]

            if key in FIELD_LIST_FIELDS:
                # keep a list of fields
                field_config[key] = value.strip().split(' ')

            if key == 'doc':
                field_config[key] = value.strip()
                
            if key == 'typedef':
                pass
                
            if key == 'type':
                pass

    return field_config


print(load_from_file('/Users/alexdelin/code/shorthand/sublime_plugins/test.rec'))


class RecordSet(object):
    """Record Set object which holds the field configuration
    and full record contents for one type of records in a GNU
    recfile
    """

    def __init__(self, arg):
        super(RecordSet, self).__init__()
        self.arg = arg
        self.fields = {}
        self.records = []

    def get_csv():
        '''Serialize the record set to a string of CSV data
        '''
        pass

    def get_fields():
        '''Get all of the fields present in the record set
        '''
        pass

    def insert():
        '''Insert a new record into the record set
        '''
        pass
