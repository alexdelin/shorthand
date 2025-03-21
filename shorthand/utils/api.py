import logging
from typing import Generic, List, TypeVar, TypedDict, Required
from shorthand.elements.todos import TodoStats


log = logging.getLogger(__name__)


T = TypeVar('T')
class WrappedResponse(TypedDict, Generic[T], total=False):
    count: Required[int]
    items: Required[List[T]]
    meta: TodoStats


def wrap_response_data(response_data: List[T]) -> WrappedResponse[T]:
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
