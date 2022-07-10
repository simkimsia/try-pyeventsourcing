# -*- coding: utf-8 -*-
from eventsourcing.application import Application
from eventsourcing.persistence import IntegrityError

from part3_try_pyeventsourcing.application import DogSchool


def test_dog_school() -> None:
    """
    taken from https://eventsourcing.readthedocs.io/en/stable/topics/tutorial/part3.html#:~:text=We%20can%20construct%20an%20application%20object%2C%20and%20call%20its%20methods.
    """
    application = DogSchool()

    dog_id = application.register_dog(name='Fido')
    application.add_trick(dog_id, trick='roll over')
    application.add_trick(dog_id, trick='fetch ball')

    dog_details = application.get_dog(dog_id)
    assert dog_details['name'] == 'Fido'
    assert dog_details['tricks'] == ('roll over', 'fetch ball')

def test_methods() -> None:
    """
    https://eventsourcing.readthedocs.io/en/stable/topics/tutorial/part3.html#applications-in-more-detail
    """
    application = DogSchool()
    assert isinstance(application, Application)

    assert application.save
    assert application.repository
    assert application.repository.get

def test_command_methods() -> None:
    """
    https://eventsourcing.readthedocs.io/en/stable/topics/tutorial/part3.html#command-methods
    until
    https://eventsourcing.readthedocs.io/en/stable/topics/tutorial/part3.html#notification-log
    """
    application = DogSchool()
    dog_id = application.register_dog(name='Fido')

    application.add_trick(dog_id, trick='roll over')
    application.add_trick(dog_id, trick='fetch ball')
    application.add_trick(dog_id, trick='play dead')

    dog_details = application.get_dog(dog_id)

    assert dog_details['name'] == 'Fido'
    assert dog_details['tricks'] == ('roll over', 'fetch ball', 'play dead')
    assert application.notification_log

    # First "page" of event notifications.
    notifications = application.notification_log.select(
        start=1, limit=2
    )
    assert [n.id for n in notifications] == [1, 2]

    assert 'Dog.Registered' in notifications[0].topic
    assert b'Fido' in notifications[0].state
    assert dog_id == notifications[0].originator_id

    assert 'Dog.TrickAdded' in notifications[1].topic
    assert b'roll over' in notifications[1].state
    assert dog_id == notifications[1].originator_id

    # Next "page" of event notifications.
    notifications = application.notification_log.select(
        start=notifications[-1].id + 1, limit=2
    )
    assert [n.id for n in notifications] == [3, 4]

    assert 'Dog.TrickAdded' in notifications[0].topic
    assert b'fetch ball' in notifications[0].state
    assert dog_id == notifications[0].originator_id

    assert 'Dog.TrickAdded' in notifications[1].topic
    assert b'play dead' in notifications[1].state
    assert dog_id == notifications[1].originator_id


def test_database_config():
    """
    https://eventsourcing.readthedocs.io/en/stable/topics/tutorial/part3.html#database-configuration
    https://eventsourcing.readthedocs.io/en/stable/topics/tutorial/part3.html#development-environment


    """

    app = DogSchool()
    expect_visible_in_db = True

    # Check app has zero event notifications.
    assert len(app.notification_log.select(start=1, limit=10)) == 0

    # Create a new aggregate.
    dog_id = app.register_dog(name='Fido')

    # Execute application commands.
    app.add_trick(dog_id, trick='roll over')
    app.add_trick(dog_id, trick='fetch ball')

    # Check recorded state of the aggregate.
    dog_details = app.get_dog(dog_id)
    assert dog_details['name'] == 'Fido'
    assert dog_details['tricks'] == ('roll over', 'fetch ball')

    # Execute another command.
    app.add_trick(dog_id, trick='play dead')

    # Check recorded state of the aggregate.
    dog_details = app.get_dog(dog_id)
    assert dog_details['name'] == 'Fido'
    assert dog_details['tricks'] == ('roll over', 'fetch ball', 'play dead')

    # Check values are (or aren't visible) in the database.
    tricks = [b'roll over', b'fetch ball', b'play dead']
    if expect_visible_in_db:
        expected_num_visible = len(tricks)
    else:
        expected_num_visible = 0

    actual_num_visible = 0
    notifications = app.notification_log.select(start=1, limit=10)
    for notification in notifications:
        for trick in tricks:
            if trick in notification.state:
                actual_num_visible += 1
                break
    assert expected_num_visible == actual_num_visible

    # Get historical state (at version 3, before 'play dead' happened).
    old = app.repository.get(dog_id, version=3)
    assert len(old.tricks) == 2
    assert old.tricks[-1] == 'fetch ball'  # last thing to have happened was 'fetch ball'

    # Check app has four event notifications.
    notifications = app.notification_log.select(start=1, limit=10)
    assert len(notifications) == 4

    # Optimistic concurrency control (no branches).
    old.add_trick(trick='future')
    try:
        app.save(old)
    except IntegrityError:
        pass
    else:
        raise Exception("Shouldn't get here")

    # Check app still has only four event notifications.
    notifications = app.notification_log.select(start=1, limit=10)
    assert len(notifications) == 4

    # Create eight more aggregate events.
    dog_id = app.register_dog(name='Millie')
    app.add_trick(dog_id, trick='shake hands')
    app.add_trick(dog_id, trick='fetch ball')
    app.add_trick(dog_id, trick='sit pretty')

    dog_id = app.register_dog(name='Scrappy')
    app.add_trick(dog_id, trick='come')
    app.add_trick(dog_id, trick='spin')
    app.add_trick(dog_id, trick='stay')

    # Get the new event notifications from the reader.
    last_id = notifications[-1].id
    notifications = app.notification_log.select(start=last_id + 1, limit=10)
    assert len(notifications) == 8
