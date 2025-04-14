from abc import ABC, abstractmethod
from typing import TypeVar

TRepository = TypeVar("TRepository")


class RepositoryProvider(ABC):
    @abstractmethod
    def __getitem__(self, base_repository_class: type[TRepository]) -> TRepository: ...
