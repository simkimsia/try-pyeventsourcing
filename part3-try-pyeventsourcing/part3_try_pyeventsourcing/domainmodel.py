# -*- coding: utf-8 -*-
from typing import List

from eventsourcing.application import Application
from eventsourcing.domain import Aggregate, event


class DogSchool(Application):
    def register_dog(self, name):
        dog = Dog(name)
        self.save(dog)
        return dog.id

    def add_trick(self, dog_id, trick):
        dog = self.repository.get(dog_id)
        dog.add_trick(trick=trick)
        self.save(dog)

    def get_dog(self, dog_id):
        dog = self.repository.get(dog_id)
        return {'name': dog.name, 'tricks': tuple(dog.tricks)}

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
