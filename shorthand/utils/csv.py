# CSV Utilities

import csv
from io import StringIO
from typing import Any

from shorthand.types import CSVData


def _convert_to_csv(data: list[Any]) -> CSVData:
    '''Convert a list of dictionaries into CSV format
       All dictionaries should have the same keys
    '''

    if not isinstance(data, list):
        raise ValueError(f'Data to convert to CSV must be provided '
                         f'as a list. Got {type(data)}')

    for record in data:
        if not isinstance(record, dict):
            raise ValueError(f'Record to convert to CSV must be provded '
                             f'as a dict. got {type(record)}')

    csv_string = StringIO()
    writer = csv.DictWriter(csv_string, fieldnames=data[0].keys())
    writer.writeheader()
    for record in data:
        writer.writerow(record)
    return csv_string.getvalue()
