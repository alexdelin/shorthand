import csv
import re
import json


ALLOWED_CONFIG_KEYS = [
    "rec", "mandatory", "unique", "key",
    "allowed", "prohibit", "size", "typedef",
    "type", "auto", "sort", "doc"]

FIELD_LIST_FIELDS = [
    'mandatory', 'unique', 'allowed',
    'prohibit', 'auto', 'sort']

PRIMITIVE_TYPES = [
    "int", "line", "date", "bool", "real"]

ALL_TYPES = [
    "int", "line", "date", "bool", "real", "range", "enum"]


def load_from_file(file_path):
    '''Load one or more record sets from a rec file
    '''

    with open(file_path, 'r') as rec_file_object:
        rec_file_content = rec_file_object.read()

    return load_from_string(rec_file_content)


def process_type_definition(definition_string):
    '''Process a type definition from a string
    '''
    split_value = definition_string.split(' ')
    linked_type_name = split_value[0]
    extra_params = split_value[1:]

    if linked_type_name in PRIMITIVE_TYPES:
        return {'type': linked_type_name}

    elif linked_type_name == 'range':

        if len(extra_params) == 1:
            # Only the max is specified
            min_value = 0
            max_value = extra_params[0]

        elif len(extra_params) == 2:
            # Both max and min are specified
            min_value = extra_params[0]
            max_value = extra_params[1]

        else:
            # We have either no values specified for the range or more than 2
            raise ValueError(f'range type definition for type {custom_type_name} '
                             f'must specify either a max value or max and min value')

        return {
            'type': 'range',
            'min': min_value,
            'max': max_value
        }

    elif linked_type_name == 'enum':
        extra_params_string = ' '.join(extra_params)
        no_comments = re.sub(r'( ?)\(.*?\)', '', extra_params_string)
        return {
            'type': 'enum',
            'values': no_comments.split(' ')
        }

    else:
        raise valueError(f'Unknown type {linked_type_name} specified')


def load_from_string(input_string):
    '''Load one or more record sets from a string
    1. Read out all record set config from the file, and
       instantiate a new RecordSet object with that config
    2. Add each record into the record set until all are
       consumed
    3. Return the resulting record set object
    '''

    split_lines = input_string.split('\n')
    record_set_config = {
        'custom_types': {},
        'field_types': {}
    }
    # Loop through all lines until we reach the end of the field config
    config_start = False
    field_config_item = None
    for idx, line in enumerate(split_lines):

        if not line.strip():
            # Blank Line
            if config_start:
                break
            else:
                continue

        if line[0] == '#':
            # Comments
            continue

        if line[0] not in ['+', '%']:
            if config_start:
                raise ValueError(f'Invalid Syntax. Line "{line}" in field '
                                 f'config does not start with either "%" '
                                 f'or "+"')

        if line[0] == '+':
            # we already got this content when
            # processing the line above
            continue

        #TODO - switch over to using a regex
        if line[0] == '%':
            config_start = True
            key = line.split(':', 1)[0][1:]
            value = line.split(':', 2)[1].strip()
            # check to see if there is more to the value on the next line
            lookahead = 1
            while True:
                next_line = split_lines[idx + lookahead]

                if not next_line.strip():
                    break

                if next_line[0] == '+' and len(next_line.strip()) > 2:
                    value = value + ' ' + next_line.strip()[2:]
                    #TODO- handle comments in enum definitions
                    lookahead += 1

                else:
                    break

            if key not in ALLOWED_CONFIG_KEYS:
                raise ValueError(f'unknown config key {key} specified')

            if key == 'rec':
                # only keep the first word
                record_set_config[key] = value.strip().split(' ')[0]

            if key in FIELD_LIST_FIELDS:
                # keep a list of fields
                record_set_config[key] = value.strip().split(' ')

            if key == 'doc':
                record_set_config[key] = value.strip()

            if key == 'typedef':
                split_value = value.split(' ')
                custom_type_name = split_value[0]
                type_definition_string = ' '.join(split_value[1:])
                type_definition = process_type_definition(type_definition_string)
                record_set_config['custom_types'][custom_type_name] = type_definition

            if key == 'type':
                '''
                Handling for type assignments
                Needs to work with:
                    %type: WasGood bool
                    %type: WasGood was_good_type
                    %type: Pages range 0 MAX
                '''
                split_value = value.split(' ')
                if len(split_value) < 2:
                    raise ValueError(f'Invalid type assignment: {line}')
                elif len(split_value) == 2:
                    # We are assigning the field to either a primitive type
                    # or a custom type
                    field_name = split_value[0]
                    type_name = split_value[1]
                    if type_name in record_set_config['custom_types'].keys():
                        type_definition = record_set_config['custom_types'][type_name]
                        record_set_config['field_types'][field_name] = type_definition
                    elif type_name in ALL_TYPES:
                        type_definition_string = ' '.join(split_value[1:])
                        type_definition = process_type_definition(type_definition_string)
                        record_set_config['field_types'][field_name] = type_definition
                    else:
                        raise ValueError(f'Undefined type {type_name} specified '
                                         f'for field {field_name}')

    print('Got config ---')
    print(json.dumps(record_set_config))

    record_set = RecordSet(config=record_set_config)


load_from_file('/Users/alexdelin/code/shorthand/sublime_plugins/test.rec')


class RecordSet(object):
    """Record Set object which holds the field configuration
    and full record contents for one type of records in a GNU
    recfile
    """

    def __init__(self, config):
        super(RecordSet, self).__init__()
        self.config = config
        self.fields = {}
        self.records = []

    def dump():
        '''Serialize the record set to recfile format
        '''
        pass

    def save(file_path):
        '''Write the contents of the record set to a file in recfile format
        '''
        pass

    def get_csv():
        '''Serialize the record set to a string of CSV data
        '''
        pass

    def import_csv(csv_data):
        '''Import CSV data to update the record set
        '''
        pass

    def get_fields():
        '''Get all of the fields present in the record set
        '''
        return self.fields

    def get_record_count():
        '''Get the total number of records in the record set
        '''
        return len(self.records)

    def insert(records_string):
        '''Insert one or more new records into the record set from a string
        in recfile format
        '''
        pass

    def all():
        '''Get all records in the record set as a list
        '''
        return self.records
