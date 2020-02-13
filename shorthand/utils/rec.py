import csv


ALLOWED_CONFIG_KEYS = [
    "rec", "mandatory", "unique", "key",
    "allowed", "prohibit", "size", "typedef",
    "type", "auto", "sort", "doc"]


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

    field_config = {}
    # Loop through all lines until we reach the end of the field config
    field_config_start = False
    field_config_item = None
    for line in input_string.split('\n'):

        if line[0] == '#':
            # Comments
            continue

        if not line.strip():
            # Blank Line
            if field_config_start:
                break

        if line[0] not in ['+', '%']:
            if field_config_start:
                raise ValueError(f'Invalid Syntax. Line "{line}" in field '\
                                 f'config does not start with either "%" '\
                                 f'or "+"')

        #TODO - switch over to using a regex
        if line[0] == '%':
            key = line.split(':', 1)[0][1:]
            if key not in ALLOWED_CONFIG_KEYS:
                raise ValueError(f'unknown config key {key} specified')


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
