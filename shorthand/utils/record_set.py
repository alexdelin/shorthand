import csv
import re
import json
import uuid
import copy
from datetime import datetime

from dateutil import parser

from shorthand.utils.rec_lib import get_hex_int


UUID_PATTERN = r'^[0-9A-F]{8}-[0-9A-F]{4}-4[0-9A-F]{3}-[89AB][0-9A-F]{3}-[0-9A-F]{12}$'

ALL_TYPES = [
    "int", "line", "date", "bool", "real", "uuid",
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

        # check that all custom types referenced actually exist
        for custom_type in config.get('custom_types', {}).keys():
            link_depth = 1
            next_type = config.get('custom_types').get(custom_type)
            while True:
                if link_depth > 10:
                    raise ValueError(f'Exceeded custom type link threshold of 10 for custom type {custom_type}')
                if not next_type:
                    raise ValueError(f'custom type {custom_type} is not defined')
                elif next_type.get('type') == 'custom':
                    next_type = config.get('custom_types').get(next_type['name'])
                    link_depth += 1
                    continue
                elif next_type.get('type') in ALL_TYPES:
                    # We found a valid type definition
                    break

        # check that prohibited and/or non-allowed fields are not referenced
        has_prohibited_fields = False
        if config.get('prohibit'):
            prohibited_fields = config.get('prohibit')
            has_prohibited_fields = True
        else:
            prohibited_fields = []

        has_allowed_fields = False
        if config.get('allowed'):
            allowed_fields = config.get('allowed')
            has_allowed_fields = True
        else:
            allowed_fields = []

        if config.get('mandatory'):
            for mandatory_field in config.get('mandatory', []):
                if has_prohibited_fields and mandatory_field in prohibited_fields:
                    raise ValueError(f'Prohibited field {mandatory_field} specified as mandatory')
                if has_allowed_fields and mandatory_field not in allowed_fields:
                    raise ValueError(f'Non-allowed field {mandatory_field} specified as mandatory')

        if config.get('unique'):
            for unique_field in config.get('unique', []):
                if has_prohibited_fields and unique_field in prohibited_fields:
                    raise ValueError(f'Prohibited field {unique_field} specified as unique')
                if has_allowed_fields and unique_field not in allowed_fields:
                    raise ValueError(f'Non-allowed field {unique_field} specified as unique')

        if config.get('key'):
            key_field = config.get('key', [])
            if has_prohibited_fields and key_field in prohibited_fields:
                raise ValueError(f'Prohibited field {key_field} specified as prmary key')
            if has_allowed_fields and key_field not in allowed_fields:
                raise ValueError(f'Non-allowed field {key_field} specified as primary key')

        if config.get('field_types', {}).keys():
            for typed_field in config.get('field_types', {}).keys():
                if has_prohibited_fields and typed_field in prohibited_fields:
                    raise ValueError(f'Prohibited field {typed_field} has a type defined')
                if has_allowed_fields and typed_field not in allowed_fields:
                    raise ValueError(f'Non-allowed field {typed_field} has a type defined')

        if config.get('sort'):
            for sort_field in config.get('sort', []):
                if has_prohibited_fields and sort_field in prohibited_fields:
                    raise ValueError(f'Prohibited field {sort_field} specified as sort')
                if has_allowed_fields and sort_field not in allowed_fields:
                    raise ValueError(f'Non-allowed field {sort_field} specified as sort')

        # check that regexp types are valid
        regexp_types = [type_def for type_def in config.get('custom_types', {}).values() if type_def['type'] == 'regexp']
        regexp_types.extend([type_def for type_def in config.get('field_types', {}).values() if type_def['type'] == 'regexp'])
        for regexp_type in regexp_types:
            re_pattern = regexp_type.get('pattern')
            is_valid = True
            if not re_pattern:
                is_valid = False
            try:
                re.compile(re_pattern)
            except re.error:
                is_valid = False
            if not is_valid:
                raise ValueError(f'Regex pattern "{regexp_type.get("pattern")}" is invalid')

        # check that range types are valid
        range_types = [type_def for type_def in config.get('custom_types', {}).values() if type_def['type'] == 'range']
        range_types.extend([type_def for type_def in config.get('field_types', {}).values() if type_def['type'] == 'range'])
        for range_type in range_types:

            max_value = range_type.get('max')
            min_value = range_type.get('min')
            if isinstance(min_value, int) and isinstance(max_value, int):
                if min_value >= max_value:
                    raise ValueError(f"Invalid range with maximum value {max_value} and minimum value {min_value}")
            elif not isinstance(min_value, (int, type(None))) and not isinstance(max_value, (int, type(None))):
                raise ValueError(f'Invalid range type {range_type}. Max and min must be either integers or None')

        # check that size types are valid
        size_types = [type_def for type_def in config.get('custom_types', {}).values() if type_def['type'] == 'size']
        size_types.extend([type_def for type_def in config.get('field_types', {}).values() if type_def['type'] == 'size'])
        for size_type in size_types:
            if not size_type.get('limit') > 0:
                raise ValueError(f'Size types must have a limit greater than zero')

        # check that enum types are valid
        enum_types = [type_def for type_def in config.get('custom_types', {}).values() if type_def['type'] == 'enum']
        enum_types.extend([type_def for type_def in config.get('field_types', {}).values() if type_def['type'] == 'enum'])
        for enum_type in enum_types:
            if not enum_type.get('values'):
                raise ValueError(f'Enum types must specify all allowed values')

        # check that size constraints for the record set are valid
        if config.get('size'):

            if config.get('size', {})['amount'] <= 0:
                raise ValueError('Size limit for a record set must be greater than zero')

        # check all auto-generated fields have a supported type
        for auto_field in config.get('auto', []):

            auto_field_type = config.get('field_types', {}).get(auto_field, {})
            if auto_field_type.get('type') == 'custom':
                auto_field_type = config.get('custom_types', {}).get(auto_field_type['name'])

            if auto_field_type.get('type') not in ['date', 'int', 'uuid']:
                raise ValueError(f'Cannot auto-generate a value for field {auto_field} of type {auto_field_type.get("type")}')

        # If we have not found any issues
        return True

    def validate_record(self, record: dict):
        '''Validate an individual record against its defined
        type and properties. Modifies the contents of the record
        if needed.

        Returns a tuple of (error_message, processed_record)
        '''

        processed_record = copy.deepcopy(record)

        # Validate types of all specified fields
        for field_name, field_values in record.items():
            field_type = self.config.get('field_types', {}).get(field_name, {})

            # Get the full type definition if it is a custom type
            if field_type.get('type') == 'custom':
                field_type = self.config.get('custom_types', {}).get(field_type['name'])

            # Validate int field
            if field_type.get('type') == 'int':
                processed_record[field_name] = []
                for field_value in field_values:
                    try:
                        if field_value[:2] == '0x' or field_value[:3] == '-0x':
                            num_value = get_hex_int(field_value)
                        else:
                            num_value = int(field_value)
                        processed_record[field_name].append(num_value)
                    except ValueError:
                        return f"can't convert value \"{field_value}\" of field \"{field_name}\" to an int", None

            # Validate line field
            if field_type.get('type') == 'line':
                for field_value in field_values:
                    if '\n' in field_value:
                        return f'value "{field_value}" of line type field "{field_name}" contains a newline character', None

            # Validate date field
            if field_type.get('type') == 'date':
                for field_value in field_values:
                    try:
                        _ = parser.parse(field_value)
                    except:
                        return f'cannot parse date value "{field_value}" of field "{field_name}"', None

            # Validate bool field
            if field_type.get('type') == 'bool':
                for field_value in field_values:
                    if field_value not in ['0', '1', 'true', 'false', 'yes', 'no']:
                        return f'Value {field_value} for bool field {field_name} is not allowed', None

            # Validate real field
            if field_type.get('type') == 'real':
                processed_record[field_name] = []
                for field_value in field_values:
                    try:
                        num_value = float(field_value)
                        processed_record[field_name].append(num_value)
                    except ValueError:
                        return f"can't convert value \"{field_value}\" of field \"{field_name}\" to a float", None

            # Validate range field
            if field_type.get('type') == 'range':
                max_value = field_type.get('max')
                min_value = field_type.get('min')
                processed_record[field_name] = []
                for field_value in field_values:
                    try:
                        if field_value[:2] == '0x' or field_value[:3] == '-0x':
                            num_value = get_hex_int(field_value)
                            processed_record[field_name].append(num_value)
                        else:
                            num_value = int(field_value)
                            processed_record[field_name].append(num_value)
                    except ValueError:
                        return f"can't convert value \"{field_value}\" of field \"{field_name}\" to a float", None
                    if max_value and num_value > max_value:
                        return f'Value {field_value} of field {field_name} exceeds the maximum range value {max_value}', None
                    if min_value and num_value < min_value:
                        return f'Value {field_value} of field {field_name} is below the minimum range value {min_value}', None

            # Validate enum field
            if field_type.get('type') == 'enum':
                allowed_values = field_type.get('values', [])
                for field_value in field_values:
                    if field_value not in allowed_values:
                        return f'value {field_value} of field {field_name} is not in allowed values {allowed_values}', None

            # Validate size field
            if field_type.get('type') == 'size':
                size_limit = field_type['limit']
                for field_value in field_values:
                    if len(field_value) > size_limit:
                        return f'Value {field_value} of field {field_name} is above the field\'s size limit of {size_limit} characters', None

            # Validate regexp field
            if field_type.get('type') == 'regexp':
                pattern = field_type['pattern']
                for field_value in field_values:
                    if not re.match(pattern, field_value):
                        return f'value "{field_value}" of field {field_name} does not match regex {pattern}', None

            # Validate uuid field
            if field_type.get('type') == 'uuid':
                for field_value in field_values:
                    if not re.match(UUID_PATTERN, field_value):
                        return f'value "{field_value}" of uuid field {field_name} is not a valid UUID4', None

            # Auto-generate field values if needed
            for auto_field in self.config.get('auto', []):

                # Only auto-generate a field value if one doesn't already exist
                if not record.get(auto_field):

                    auto_field_type = self.config.get('field_types', {}).get(auto_field)
                    if auto_field_type.get('type') == 'custom':
                        auto_field_type = self.config.get('custom_types', {}).get(auto_field_type['name'])

                    if auto_field_type.get('type') == 'date':
                        timestamp = datetime.now().strftime('%Y-%m-%d')
                        processed_record[auto_field] = [timestamp]

                    elif auto_field_type.get('type') == 'int':
                        max_field_value = max([max(r[auto_field]) for r in self.records])
                        new_value = max_field_value + 1
                        processed_record[auto_field] = [new_value]

                    elif auto_field_type.get('type') == 'uuid':
                        new_uuid == uuid.uuid4()
                        processed_record[auto_field] = [new_uuid]

                    else:
                        return f'Cannot auto-generate a value for field {auto_field} of type {auto_field_type.get("type")}', None

        # Validate Mandatory Fields
        for mandatory_field in self.config.get('mandatory', []):
            if mandatory_field not in processed_record.keys():
                return f'Missing mandatory field {mandatory_field}', None

        # Validate Unique Fields
        for unique_field in self.config.get('unique', []):
            if len(processed_record.get(unique_field, [])) > 1:
                return f'More than 1 value found for unique field {unique_field}', None

        # Validate Allowed Fields
        allowed_fields = self.config.get('allowed')
        if allowed_fields:
            for field_name in processed_record.keys():
                if field_name not in allowed_fields:
                    return f'field {field_name} not in allowed fields {allowed_fields}', None

        # Validate Prohibited Fields
        prohibited_fields = self.config.get('prohibit', [])
        for prohibited_field in prohibited_fields:
            if prohibited_field in processed_record.keys():
                return f'prohibited field {prohibited_field} present in record', None

        # Validate Primary Key
        primary_key_field = self.config.get('key')
        if primary_key_field:
            if not processed_record.get(primary_key_field):
                return f'Missing primary key field {primary_key_field}', None
            if len(processed_record.get(primary_key_field)) > 1:
                return f'Primary key field {primary_key_field} can only have a single value per record', None
            if self.primary_keys.get(processed_record[primary_key_field][0]):
                return f'Primary key value {processed_record[primary_key_field][0]} already exists for field {primary_key_field}', None

        # validate record set size constraint only if it is a less than or less than or equal to constraint
        size_condition = self.config.get('size', {}).get('condition')
        if size_condition in ['<', '<=']:
            size_limit = self.config.get('size', {}).get('amount')
            if size_condition == '<=':
                size_limit = size_limit + 1
            if len(self.records) > size_limit:
                return f'adding another record will exceed the size limit of {size_limit} in the record set', None

        for field_name, field_values in processed_record.items():
            # Add a new field to the field list
            if not self.fields.get(field_name):
                self.fields[field_name] = True

        return False, processed_record

    def validate_size_constraint(self):
        size_constraint = self.config.get('size')
        if not size_constraint:
            return
        constraint_condition = size_constraint.get('condition')
        current_length = len(self.records)
        constraint_amount = size_constraint.get('amount')
        if constraint_condition == '==' and current_length != constraint_amount:
            raise ValueError(f'Record set must have {constraint_amount} records but has {current_length}')
        elif constraint_condition == '<' and current_length >= constraint_amount:
            raise ValueError(f'Record set must have less than {constraint_amount} records but has {current_length}')
        elif constraint_condition == '<=' and current_length > constraint_amount:
            raise ValueError(f'Record set must have {constraint_amount} records or less but has {current_length}')
        elif constraint_condition == '>' and current_length <= constraint_amount:
            raise ValueError(f'Record set must have more than {constraint_amount} records but has {current_length}')
        elif constraint_condition == '>=' and current_length < constraint_amount:
            raise ValueError(f'Record set must have {constraint_amount} records or more but has {current_length}')

    def insert(self, records):
        '''Insert raw dictionaries into the record set
        Typically only called by internal methods
        '''
        for record in records:
            error_message, processed_record = self.validate_record(record)
            if not error_message:
                primary_key_field = self.config.get('key')
                if primary_key_field:
                    self.primary_keys[processed_record[primary_key_field][0]] = True
                self.records.append(processed_record)
            else:
                raise ValueError(f'Validation Error: {error_message} in record {record}')

        #TODO- check that size constraints are still met
        self.validate_size_constraint()

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
        return list(self.fields.keys())

    def get_record_count(self):
        '''Get the total number of records in the record set
        '''
        return len(self.records)

    def all(self):
        '''Get all records in the record set as a list of dictionaries
        '''
        return self.records
