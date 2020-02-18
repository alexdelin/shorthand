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
    "int", "line", "date", "bool", "real",
    "range", "enum", "size", "regexp"]


class RecordSet(object):
    """Record Set object which holds the field configuration
    and full record contents for one type of records in a GNU
    recfile
    """

    def __init__(self, config):
        super(RecordSet, self).__init__()
        if config:
            if self.validate_config(config):
                self.config = config
            else:
                raise ValueError('Got Invalid configuration')
        else:
            self.config = {}
        self.fields = {}
        self.records = []

    def validate_config(self, config):
        '''Validate configuration for a record set
        '''
        return True

    def validate_record(self, record):
        '''Validate an individual record against its defined
        type and properties
        '''

        # Validate Mandatory Fields
        for mandatory_field in self.config.get('mandatory', []):
            if mandatory_field not in record.keys():
                return f'Missing mandatory field {mandatory_field}'

        # Validate Unique Fields
        for unique_field in self.config.get('unique', []):
            if len(record.get('unique', [])) > 1:
                return f'More than 1 value found for unique field {unique_field}'

        # Validate Allowed Fields
        # Validate Prohibited Fields
        # Validate Primary Key
        # Validate Size Constraint
        # Validate types of all specified fields
            # Validate int field
            # Validate line field
            # Validate date field
            # Validate bool field
            # Validate real field
            # Validate range field
            # Validate enum field
            # Validate size field
            # Validate regexp field
        # Auto-generate fields
        # Add a new field to the field list
        return False

    def insert(self, records):
        '''Insert raw dictionaries into the record set
        Typically only called by internal methods
        '''
        for record in records:
            error_message = self.validate_record(record)
            if not error_message:
                self.records.append(record)
            else:
                raise ValueError(f'Validation Error: {error_message} in record {record}')

    def get_rec(self):
        '''Serialize the record set to recfile format
        '''
        pass

    def save_rec(self, file_path):
        '''Write the contents of the record set to a file in recfile format
        '''
        pass

    def insert_rec(self, records_string):
        '''Insert one or more new records into the record set from a string
        in recfile format
        '''
        pass

    def get_csv(self):
        '''Serialize the record set to a string of CSV data
        '''
        pass

    def insert_csv(self, csv_data):
        '''Import CSV data to update the record set
        '''
        pass

    def get_json(self):
        '''serialize the record set to a JSON string
        '''
        return json.dumps(self.records)

    def insert_json(self, json_data):
        '''Import JSON data to update the record set
        '''
        records = json.loads(json_data)
        self.insert(records)

    def get_fields(self):
        '''Get all of the fields present in the record set
        '''
        return self.fields

    def get_record_count(self):
        '''Get the total number of records in the record set
        '''
        return len(self.records)

    def all(self):
        '''Get all records in the record set as a list of dictionaries
        '''
        return self.records


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

    elif linked_type_name == 'size':
        if len(extra_params) != 1:
            raise ValueError('Only a single size limit can be specified for a size type')
        else:
            return {
                'type': 'size',
                'limit': extra_params[0]
            }

    elif linked_type_name == 'regexp':
        extra_params_string = ' '.join(extra_params).strip()
        return {
            'type': 'regexp',
            'pattern': extra_params_string
        }

    else:
        raise ValueError(f'Unknown type {linked_type_name} specified')


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

    print('--- Got config ---')
    print(json.dumps(record_set_config))

    record_set = RecordSet(config=record_set_config)

    records = []
    current_record = {}
    for idx, line in enumerate(split_lines):

        if not line.strip():
            # Empty line
            if current_record:
                records.append(current_record)
                current_record = {}
                continue
            else:
                continue

        if re.match(r'[a-zA-Z][a-zA-Z0-9_]*: .*', line):
            # A field value
            split_line = line.split(':', 1)
            key = split_line[0]
            value = split_line[1].lstrip(' ')
            current_record.setdefault(key, [])
            current_record[key].append(value)
            continue

        if line[0] == '%':
            # we have reached the start of a new record set
            if current_record:
                raise ValueError('Found the start of a new record set '
                                 'in the middle of a record')
            continue

    record_set.insert(records)

    print('--- Record Set JSON ---')
    print(record_set.get_json())

    return record_set


load_from_file('/Users/alexdelin/code/shorthand/sublime_plugins/test.rec')


