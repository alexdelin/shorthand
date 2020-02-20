import csv
import re
import json
import uuid
import copy
from datetime import datetime

from dateutil import parser


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
                        if field_value[:2] == '0x':
                            num_value = int(field_value[2:], 16)
                            processed_record[field_name].append(num_value)
                        else:
                            num_value = float(field_value)
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
                        return f'value {field_value} of field {field_name} does not match regex {pattern}', None

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
        prohibited_fields = self.config.get('prohibited', [])
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
        return list(self.fields.keys())

    def get_record_count(self):
        '''Get the total number of records in the record set
        '''
        return len(self.records)

    def all(self):
        '''Get all records in the record set as a list of dictionaries
        '''
        return self.records
