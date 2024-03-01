import logging
from multiprocessing import Lock
from typing import Callable, TypeVar, Generic, Dict, List, Union

T = TypeVar('T')


class PQDict(Generic[T]):
    def __init__(self, max_size: int):
        self._accessed_queue: List[str] = []
        self._max_size = max_size
        self._queue_lock = Lock()
        self._data: Dict[str, T] = {}
        self._in_transaction = False

    def __enter__(self):
        self.begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_transaction()
        return self

    def in_transaction(self):
        return self._in_transaction

    def begin_transaction(self):
        self._in_transaction = True
        self._queue_lock.acquire()

    def end_transaction(self):
        self._in_transaction = False
        self._queue_lock.release()

    def compute_and_set_accessor(self, fun: Callable) -> Callable:
        def helper(key: str, *args, **kwargs) -> Union[T, None]:
            return self.compute_and_set(key, fun = fun, *args, **kwargs) # type: ignore
        return helper

    def compute_if_not_value_accessor(self, fun: Callable, stored_value: Union[T, None] = None) -> Callable:
        def helper(key: str, value: Union[T, None] = None, *args, **kwargs) -> Union[T, None]:
            if value is not None:
                return self.compute_if_not_value(key, fun = fun, value = value, *args, **kwargs) # type: ignore
            elif stored_value is not None:
                return self.compute_if_not_value(key, fun = fun, value = stored_value, *args, **kwargs) # type: ignore
            else:
                return self.compute_if_not_value(key, fun = fun, value = None, *args, **kwargs) # type: ignore
        return helper

    def compute_if_not_exists_accessor(self, fun: Callable) -> Callable:
        def helper(key: str, *args, **kwargs) -> Union[T, None]:
            return self.compute_if_not_exists(key, fun = fun, *args, **kwargs) # type: ignore
        return helper

    def compute_and_set(self, key: str, fun: Callable, *args, **kwargs):
        if not self._in_transaction:
            with self._queue_lock:
                return self._set(key = key, value = fun(*args, **kwargs), should_lock = True)
        else:
            return self._set(key = key, value = fun(*args, **kwargs), should_lock = False)

    def compute_if_not_value(self, key: str, value: Union[T, None], fun: Callable, *args, **kwargs) -> Union[T, None]:
        def determine_compute():
            if value is None:
                return self.compute_if_not_exists(key, fun, *args, **kwargs)
            else:
                return self.__safe_compute_if_not_value_helper(key, fun, target_val = value, *args, **kwargs)

        if not self._in_transaction:
            with self._queue_lock:
                return determine_compute()
        else:
            return determine_compute()

    def compute_if_not_exists(self, key: str, fun: Callable, *args, **kwargs) -> Union[T, None]:
        if not self._in_transaction:
            with self._queue_lock:
                return self.__safe_compute_if_not_value_helper(key, fun, *args, **kwargs)
        else:
            return self.__safe_compute_if_not_value_helper(key, fun, *args, **kwargs)

    def get(self, key: str, default: Union[T, None] = None) -> Union[T, None]:
        return self._get(key, default, should_lock = True)

    def _get(self, key: str, default: Union[T, None] = None, should_lock = True) -> Union[T, None]:
        if key in self._data.keys():
            x = self._data.get(key)
            self._accessed_item(key, should_lock)
            return x
        else:
            return default

    def _accessed_item(self, key: str, should_lock = True):
        # Don't try to reaquire the lock if already in a transaction.
        if should_lock and not self._in_transaction:
            with self._queue_lock:
                self.__safe_update_queue_helper(key)
        else:
            self.__safe_update_queue_helper(key)

    def set(self, key: str, value: T) -> T:
        x = self._set(key, value, should_lock = True)
        self._accessed_item(key, should_lock = True)
        return x

    def _set(self, key: str, value: T, should_lock = True) -> T:
        self._data.update({key: value})
        return value

    def contains(self, key: str) -> bool:
        return self._contains(key, should_lock = True)

    def _contains(self, key: str, should_lock: bool) -> bool:
        return self._get(key, None, should_lock) is not None

    def __safe_compute_if_not_value_helper(self, key: str, fun: Callable,
                                           target_val: Union[T, None] = None, *args, **kwargs) -> Union[T, None]:
        current_val = self._get(key, should_lock = False, default = target_val)

        if (target_val is None and current_val is None) or \
                (target_val is None and target_val is not None) or \
                (target_val is not None and current_val != target_val):
            return self._set(key = key, value = fun(*args, **kwargs), should_lock = False)
        else:
            return current_val

    def __safe_update_queue_helper(self, key: str):
        if len(self._accessed_queue) >= self._max_size:
            logging.debug("PQDict size exceeded, removing one element: " + str(self._max_size))
            last_item = self._accessed_queue.pop(0)
            if last_item in self._data.keys():
                self._data.pop(last_item)
        else:
            # Move the key is at the beginning of the queue (the end)
            if key in self._accessed_queue:
                self._accessed_queue.remove(key)
            self._accessed_queue.append(key)
