from part3_try_pyeventsourcing.domainmodel import Todos


def test():

    # Start a list of todos, and add some items.
    todos1 = Todos(name='Shopping list')
    todos1.add_item('bread')
    todos1.add_item('milk')
    todos1.add_item('eggs')

    # Check the state of the aggregate.
    assert todos1.name == 'Shopping list'
    assert todos1.items == [
        'bread',
        'milk',
        'eggs',
    ]

    # Check the aggregate events.
    events = todos1.collect_events()
    assert len(events) == 4
    assert isinstance(events[0], Todos.Started)
    assert events[0].name == 'Shopping list'
    assert isinstance(events[1], Todos.ItemAdded)
    assert events[1].item == 'bread'
    assert isinstance(events[2], Todos.ItemAdded)
    assert events[2].item == 'milk'
    assert isinstance(events[3], Todos.ItemAdded)
    assert events[3].item == 'eggs'

    # Reconstruct aggregate from events.
    copy = None
    for e in events:
        copy = e.mutate(copy)
    assert copy == todos1

    # Create and test another aggregate.
    todos2 = Todos(name='Household repairs')
    assert todos1 != todos2
    events = todos2.collect_events()
    assert len(events) == 1
    assert isinstance(events[0], Todos.Started)
    assert events[0].name == 'Household repairs'
    assert events[0].mutate(None) == todos2
