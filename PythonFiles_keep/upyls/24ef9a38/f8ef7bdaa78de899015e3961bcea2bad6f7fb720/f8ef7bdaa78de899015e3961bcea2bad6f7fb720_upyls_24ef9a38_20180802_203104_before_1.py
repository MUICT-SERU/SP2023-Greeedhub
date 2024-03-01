from collections.__init__ import UserList
from typing import TypeVar, Iterable as Iterable

_T = TypeVar('_T')
_LimitedListT = TypeVar('_LimitedListT')


class LimitedList(UserList):
    """
    Represents a List, which is Limited in its size. If the List is filled with as many items as the limit is set it
    will refuse to have more items added to it.
    """

    def __init__(self, initlist=None, limit: int=None):
        if limit < 0:
            raise ValueError("Limit cannot be negative")
        if limit is not None and limit != 0:
            if initlist is not None:
                if len(initlist) > limit:
                    raise OverflowError("Size of Initializer is greater than limit")
        self._limit: int = limit
        super(LimitedList, self).__init__(initlist)
        
    @property
    def limit(self) -> int:
        return self._limit

    def __add__(self: _LimitedListT, other: Iterable[_T]) -> _LimitedListT:
        if self.limit is not None and self.limit != 0:
            if len(self.data) >= self.limit:
                raise OverflowError("This List has got a Limit of {} you cannot add more items".format(self.limit))
        return super().__add__(other)

    def __iadd__(self: _LimitedListT, other: Iterable[_T]) -> _LimitedListT:
        if self.limit is not None and self.limit != 0:
            if len(self.data) >= self.limit:
                raise OverflowError("This List has got a Limit of {} you cannot add more items".format(self.limit))
        return super().__iadd__(other)

    def append(self, item: _T) -> None:
        if self._limit is not None and self._limit != 0:
            if len(self.data) >= self._limit:
                raise OverflowError("This List has got a Limit of {} you cannot add more items".format(self._limit))
        super().append(item)

    def insert(self, i: int, item: _T) -> None:
        if self._limit is not None and self._limit != 0:
            if len(self.data) >= self._limit:
                raise OverflowError("This List has got a Limit of {} you cannot add more items".format(self._limit))
        super().insert(i, item)

    def extend(self, other: Iterable[_T]) -> None:
        if self._limit is not None and self._limit != 0:
            if len(self.data) >= self._limit:
                raise OverflowError("This List has got a Limit of {} you cannot add more items".format(self._limit))
        super().extend(other)