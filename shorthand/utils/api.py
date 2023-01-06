import logging
from typing import Generic, Optional, TypeVar, TypedDict, Union, Type

from werkzeug.datastructures import MultiDict


log = logging.getLogger(__name__)


T = TypeVar('T')
class WrappedResponse(TypedDict, Generic[T]):
    count: int
    items: list[T]


ArgType = TypeVar('ArgType', int, float, bool, str)


def get_request_argument(args: MultiDict[str, str], name: str,
                         arg_type: Type[ArgType] = str,
                         default: Optional[ArgType] = '',
                         required: bool = False) -> ArgType:
    '''Get a parameter from the requet arguments (parameters)

       name: The name of the provided argument
       type: The type of value in the argument. Values are:
             string, bool, int, float
       default: Default value to use if the request argument is not provided
    '''
    if arg_type not in [str, bool, int, float]:
        raise ValueError(f'Invalid arg type {arg_type}')

    if default and type(default) != arg_type:
        raise ValueError(f'Invalid default value {default} provided, ' +
                         f'does not match type {arg_type}')

    if required and name not in args.keys():
        raise ValueError(f'Required request argument {name} not provided')

    if arg_type == str:
        return args.get(name, default, str) # type: ignore
    elif arg_type == bool:
        raw_arg = args.get(name, default)
        if str(raw_arg).lower() == 'true':
            return True # type: ignore
        elif str(raw_arg).lower() == 'false':
            return False # type: ignore
        else:
            raise ValueError(f'Cannot convert value {raw_arg} of request ' +
                             f'argument {name} to a boolean')
    elif arg_type == int:
        return args.get(name, default, int) # type: ignore
    else:
        return args.get(name, default, float) # type: ignore


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
        raise ValueError(f'Invalid Response data of type ' +
                         f'{type(response_data)} received')
