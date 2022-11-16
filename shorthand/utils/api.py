import logging
from typing import Generic, TypeVar, TypedDict


log = logging.getLogger(__name__)


T = TypeVar('T')
class WrappedResponse(TypedDict, Generic[T]):
    count: int
    items: list[T]


def get_request_argument(args, name, arg_type='string', default=None,
                         required=False):
    '''Get a parameter from the requet arguments (parameters)

       name: The name of the provided argument
       type: The type of value in the argument. Values are:
             'string', 'bool', 'int', 'float'
       default: Default value to use if the request argument is not provided
    '''
    if arg_type not in ['string', 'bool', 'int', 'float']:
        raise ValueError(f'Invalid arg type {arg_type}')

    if required and name not in args.keys():
        raise ValueError(f'Required request argument {name} not provided')

    if arg_type == 'string':
        return args.get(name, default, str)
    elif arg_type == 'bool':
        raw_arg = args.get(name, default)
        if str(raw_arg).lower() == 'true':
            return True
        elif str(raw_arg).lower() == 'false':
            return False
        else:
            raise ValueError(f'Cannot convert value {raw_arg} of request '
                             f'argument {name} to a boolean')
    elif arg_type == 'int':
        return args.get(name, default, int)
    else:
        return args.get(name, default, float)


def wrap_response_data(response_data: T) -> WrappedResponse[T]:
    '''Wraps response data returned by the API into a consistent format
    Lists of data are wrapped to the form:
    {
        "count": <int>,
        "items": <list-data>
    }
    '''
    if isinstance(response_data, list):
        return {
            "count": len(response_data),
            "items": response_data
        }
    else:
        raise ValueError(f'Invalid Response data of type '
                         f'{type(response_data)} received')
