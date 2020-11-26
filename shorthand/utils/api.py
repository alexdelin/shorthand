import logging


log = logging.getLogger(__name__)


def wrap_response_data(response_data):
    '''Wraps response data returned by the API into a consistent format
    Lists of data are wrapped to the form:
    {
        "count": <int>,
        "items": <list-data>
    }
    Dictionaries of data are wrapped to the form:
    {
        "count": 1,
        "items": <dict-data>
    }
    '''
    if isinstance(response_data, list):
        return {
            "count": len(response_data),
            "items": response_data
        }
    elif isinstance(response_data, dict):
        return {
            "count": 1,
            "items": response_data
        }
    else:
        raise ValueError(f'Invalid Response data of type '
                         f'{type(response_data)} received')
