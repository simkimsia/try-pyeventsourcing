# -*- coding: utf-8 -*-
from typing import List

from eventsourcing.domain import Aggregate, event


class Dog(Aggregate):
    """
    doc string for Dog
    """
    @event("Registered")
    def __init__(self, name: str) -> None:
        self.name = name
        self.tricks: List[str] = []

    @event("TrickAdded")
    def add_trick(self, trick: str) -> None:
        """
        doc string for add_trick
        """
        self.tricks.append(trick)


class Todos(Aggregate):
    """
    doc string for Todos
    """
    @event("Started")
    def __init__(self, name: str) -> None:
        self.name = name
        self.items: List[str] = []

    @event("ItemAdded")
    def add_item(self, item: str) -> None:
        """
        doc string for add_item
        """
        self.items.append(item)
