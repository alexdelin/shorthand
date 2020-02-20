import csv
import re
import json

from dateutil import parser


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
        self.primary_keys = {}

    def validate_config(self, config):
        '''Validate configuration for a record set
        '''
        
        # check that prohibited fields are not referenced
        # check that non-allowed fields are not referenced
        # check that regexes are valid
        # check that ranges are valid
        # check all auto-generated fields have a supported type
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
        allowed_fields = self.config.get('allowed')
        if allowed_fields:
            for field_name in record.keys():
                if field_name not in allowed_fields:
                    return f'field {field_name} not in allowed fields {allowed_fields}'

        # Validate Prohibited Fields
        prohibited_fields = self.config.get('prohibited', [])
        for prohibited_field in prohibited_fields:
            if prohibited_field in record.keys():
                return f'prohibited field {prohibited_field} present in record'

        # Validate Primary Key
        primary_key_field = self.config.get('key')
        if primary_key_field:
            if not record.get(primary_key_field):
                return f'Missing primary key field {primary_key_field}'
            if len(record.get(primary_key_field)) > 1:
                return f'Primary key field {primary_key_field} can only have a single value per record'
            if self.primary_keys.get(record[primary_key_field][0]):
                return f'Primary key value {record[primary_key_field][0]} already exists for field {primary_key_field}'
                
        # validate record set size constraint only if it is a less than or less than or equal to constraint
        size_condition = self.config.get('size', {}).get('condition')
        if size_condition in ['<', '<=']:
            size_limit = self.config.get('size', {}).get('limit')
            if size_condition == '<=':
                size_limit = size_limit + 1
            if len(self.records) > size_limit:
                return f'adding another record will exceed the size limit of {size_limit} in the record set'

        # Validate types of all specified fields
        for field_name, field_values in record.items():
            field_type = self.config.get('field_types', {}).get(field_name)

            # Get the full type definition if it is a custom type
            if field_type['type'] == 'custom':
                field_type = self.config.get('custom_types', {}).get(field_type['name'])

            # Validate int field
            if field_type['type'] == 'int':
                for field_value in field_values:
                    try:
                        _ = int(field_value)
                    except ValueError:
                        return f"can't convert value \"{field_value}\" of field \"{field_name}\" to an int"

            # Validate line field
            if field_type['type'] == 'line':
                for field_value in field_values:
                    if '\n' in field_value:
                        return f'value "{field_value}" of line type field "{field_name}" contains a newline character '

            # Validate date field
            if field_type['type'] == 'date':
                for field_value in field_values:
                    try:
                        _ = parser.parse(field_value)
                    except:
                        return f'cannot parse date value "{field_value}" of field "{field_name}"'

            # Validate bool field
            if field_type['type'] == 'bool':
                for field_value in field_values:
                    if field_value not in ['0', '1', 'true', 'false', 'yes', 'no']:
                        return f'Value {field_value} for bool field {field_name} is not allowed'

            # Validate real field
            if field_type['type'] == 'real':
                for field_value in field_values:
                    try:
                        _ = float(field_value)
                    except ValueError:
                        return f"can't convert value \"{field_value}\" of field \"{field_name}\" to a float"

            # Validate range field
            if field_type['type'] == 'range':
                max_value = field_type.get('max')
                min_value = field_type.get('min')
                for field_value in field_values:
                    try:
                        if field_value[:2] == '0x':
                            float_value = int(field_value[2:], 16)
                        else:
                            float_value = float(field_value)
                    except ValueError:
                        return f"can't convert value \"{field_value}\" of field \"{field_name}\" to a float"
                    if max_value and float_value > max_value:
                        return f'Value {field_value} of field {field_name} exceeds the maximum range value {max_value}'
                    if min_value and float_value < min_value:
                        return f'Value {field_value} of field {field_name} is below the minimum range value {min_value}'

            # Validate enum field
            if field_type['type'] == 'enum':
                allowed_values = field_type.get('values', [])
                for field_value in field_values:
                    if field_value not in allowed_values:
                        return f'value {field_value} of field {field_name} is not in allowed values {allowed_values}'

            # Validate size field
            if field_type['type'] == 'size':
                size_limit = field_type['limit']
                for field_value in field_values:
                    if len(field_value) > size_limit:
                        return f'Value {field_value} of field {field_name} is above the field\'s size limit of {size_limit} characters'

            # Validate regexp field
            if field_type['type'] == 'regexp':
                pattern = field_type['pattern']
                for field_value in field_values:
                    if not re.match(pattern, field_value):
                        return f'value {field_value} of field {field_name} does not match regex {pattern}'

            #TODO- Auto-generate field values if needed
            for auto_field in self.config.get('auto', []):
                pass

            # Add a new field to the field list
            if not self.fields.get(field_name):
                self.fields[field_name] = True

        return False

    def insert(self, records):
        '''Insert raw dictionaries into the record set
        Typically only called by internal methods
        '''
        for record in records:
            error_message = self.validate_record(record)
            if not error_message:
                primary_key_field = self.config.get('key')
                if primary_key_field:
                    self.primary_keys[record[primary_key_field][0]] = True
                self.records.append(record)
            else:
                raise ValueError(f'Validation Error: {error_message} in record {record}')

        #TODO- check that size constrains are still met

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

            if max_value[:2] == '0x':
                max_value = int(max_value[2:], 16)
            else:
                max_value = float(max_value)

        elif len(extra_params) == 2:
            # Both max and min are specified
            min_value = extra_params[0]
            max_value = extra_params[1]

            if max_value[:2] == '0x':
                max_value = int(max_value[2:], 16)
            elif max_value == 'MAX':
                max_value = None
            else:
                max_value = float(max_value)

            if min_value[:2] == '0x':
                min_value = int(min_value[2:], 16)
            elif min_value == 'MIN':
                min_value = None
            else:
                min_value = float(min_value)

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
            size_limit = extra_params[0]
            if size_limit[:2] == '0x':
                size_limit = int(size_limit, 16)
            else:
                size_limit = int(size_limit)
            return {
                'type': 'size',
                'limit': size_limit
            }

    elif linked_type_name == 'regexp':
        regex_pattern = ' '.join(extra_params).strip().strip('/')
        return {
            'type': 'regexp',
            'pattern': regex_pattern
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

            if key == 'key':
                if len(value.strip().split(' ')) > 1:
                    raise ValueError('Only a single field can be specified as a primary key')
                record_set_config[key] = value.strip()

            if key == 'size':

                split_value = value.strip().split(' ')
                if len(split_value) == 1:
                    # Only a specific number of records is specified
                    amount = int(split_value[0])
                    record_set_config[key] = {
                        'amount': amount,
                        'condition': '=='
                    }

                elif len(split_value) == 2:
                    # A condition and number of records is specified
                    condition = split_value[0]
                    if condition not in ['==', '<', '>', '<=', '>=']:
                        raise ValueError(f'Unknown condition {condition} specified')
                    amount = int(split_value[1])
                    record_set_config[key] = {
                        'amount': amount,
                        'condition': condition
                    }

                else:
                    raise ValueError(f'Invalid size condition "{value}" specified')

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
                        # We are referencing a custom type that exists
                        type_definition = {
                            'type': 'custom',
                            'name': type_name
                        }
                        record_set_config['field_types'][field_name] = type_definition
                    elif type_name in ALL_TYPES:
                        # We are referencing a builtin type
                        type_definition_string = ' '.join(split_value[1:])
                        type_definition = process_type_definition(type_definition_string)
                        record_set_config['field_types'][field_name] = type_definition
                    else:
                        # We are referencing a custom type that doesn't exist
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


