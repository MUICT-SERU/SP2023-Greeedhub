from collections import UserList
from typing import TypeVar, Iterable as Iterable

T = TypeVar('T')
_LimitedListT = TypeVar('_LimitedListT')


class LimitedList(UserList):
    """
    Represents a List, which is Limited in its size.
    If a lower limit is set the list will refuse to have less items than this limit. If the List is filled with as many
    items as the upper limit is set it will refuse to have more items added to it.
    """

    def __init__(self, initlist=None, lower_limit: int=None, upper_limit: int = None):
        """
        :param initlist: initializing collection of items
        :param lower_limit: upper limit to set for the count of items, to be set on construction, read-only property
                            later. If the limit is None or 0 the list is unlimited
        :param upper_limit: upper limit to set for the count of items, to be set on construction, read-only property
                            later. If the limit is None or 0 the list is unlimited
        :raises: ValueError if a negative limit is tried to be passed or upper limit is smaller than lower limit
        :raises: OverflowError if count of initlist items is smaller than lower or greater than upper limit
        """

        LimitedList.__check_limits(initlist, lower_limit, upper_limit)
        self._upper_limit: int = upper_limit
        self._lower_limit: int = lower_limit
        super(LimitedList, self).__init__(initlist)

    @property
    def upper_limit(self) -> int:
        """
        :return: the upper limit set on construction
        """
        return self._upper_limit

    @property
    def lower_limit(self) -> int:
        """
        :return: the lower limit set on construction
        """
        return self._lower_limit

    def append(self, item: T) -> None:
        if self._upper_limit is not None and self._upper_limit != 0:
            if len(self.data) >= self._upper_limit:
                raise OverflowError("This List has got an upper limit of {} you cannot add more items"
                                    .format(self._upper_limit))
        super().append(item)

    def insert(self, i: int, item: T) -> None:
        if self._upper_limit is not None and self._upper_limit != 0:
            if len(self.data) >= self._upper_limit:
                raise OverflowError("This List has got an upper limit of {} you cannot add more items"
                                    .format(self._upper_limit))
        super().insert(i, item)

    def extend(self, other: Iterable[T]) -> None:
        if self._upper_limit is not None and self._upper_limit != 0:
            if len(self.data) >= self._upper_limit:
                raise OverflowError("This List has got an upper limit of {} you cannot add more items"
                                    .format(self._upper_limit))
        super().extend(other)

    def pop(self, i: int = ...) -> T:
        if self.lower_limit is not None and self.lower_limit != 0:
            if len(self.data) - i < self.lower_limit:
                raise OverflowError("This List has got a lower limit of {} you cannot remove requested count of items"
                                    .format(self.lower_limit))
        return super().pop(i)

    def remove(self, item: T) -> None:
        if self.lower_limit is not None and self.lower_limit != 0:
            if len(self.data) <= self.lower_limit:
                raise OverflowError("This List has got a lower limit of {} you cannot remove more items"
                                    .format(self.lower_limit))
        super().remove(item)

    def __add__(self: _LimitedListT, other: Iterable[T]) -> _LimitedListT:
        if self.upper_limit is not None and self.upper_limit != 0:
            if len(self.data) >= self.upper_limit:
                raise OverflowError("This List has got an upper limit of {} you cannot add more items"
                                    .format(self.upper_limit))
        return super().__add__(other)

    def __iadd__(self: _LimitedListT, other: Iterable[T]) -> _LimitedListT:
        if self.upper_limit is not None and self.upper_limit != 0:
            if len(self.data) >= self.upper_limit:
                raise OverflowError("This List has got an upper limit of {} you cannot add more items"
                                    .format(self.upper_limit))
        return super().__iadd__(other)

    @staticmethod
    def __check_limits(self, initlist, lower_limit, upper_limit):
        if lower_limit is not None and lower_limit != 0:
            if lower_limit < 0:
                raise ValueError("Lower limit cannot be negative")
            if initlist is not None:
                if len(initlist) < lower_limit:
                    raise OverflowError("Size of Initializer is smaller than lower limit")
        if upper_limit is not None and upper_limit != 0:
            if upper_limit < 0:
                raise ValueError("Upper limit cannot be negative")
            if initlist is not None:
                if len(initlist) > upper_limit:
                    raise OverflowError("Size of Initializer is greater than upper limit")
        if upper_limit is not None and lower_limit is not None:
            if upper_limit != 0 and lower_limit != 0:
                if upper_limit < lower_limit:
                    raise ValueError("Upper limit can not be smaller than lower limit")

