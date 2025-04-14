from collections.abc import Callable
from contextlib import contextmanager
from typing import (
    Generic,
    TypeVar,
    cast,
)

T = TypeVar("T")


class InstanceGetterProxy(Generic[T]):
    def __init__(self, instance_getter: Callable[[], T]):
        self.__instance_getter = instance_getter

    def __getattr__(self, name):
        return getattr(self.__instance_getter(), name)


class StackTopProxy(Generic[T]):
    """A typed stack with context manager and proxy facilities."""

    def __init__(self) -> None:
        self.__stack: list[T] = []
        self.__stack_top_proxy = InstanceGetterProxy(lambda: self.top)

    def push(self, item: T):
        """Inserts an item at the top of the stack."""
        self.__stack.append(item)

    def pop(self) -> T:
        """Removes an item from the top of the stack and returns it."""
        return self.__stack.pop()

    @property
    def top(self) -> T | None:
        """Returns the topmost item on the stack without removing it."""
        if self.__stack:
            return self.__stack[-1]

        return None

    @property
    def top_proxy(self) -> T:
        """Returns a typed proxy for the topmost item on the stack."""
        return cast(T, self.__stack_top_proxy)

    @contextmanager
    def use(self, item: T):
        """Inserts an item at the top of the stack, yields it and then removes it."""
        try:
            self.push(item)
            yield item
        finally:
            self.pop()
