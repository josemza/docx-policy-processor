from typing import Generic, Protocol, TypeVar

T = TypeVar("T")


class Repository(Protocol, Generic[T]):
    """Protocol base to keep services decoupled from persistence details."""
