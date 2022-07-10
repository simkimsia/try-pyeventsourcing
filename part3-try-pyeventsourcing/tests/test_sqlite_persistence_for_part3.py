import os
import pathlib

part3 = pathlib.Path(__file__).parent.parent.absolute()

db_path = part3 / 'database' / 'part3_try_pyeventsourcing.db'

# Use SQLite for persistence.
os.environ['PERSISTENCE_MODULE'] = 'eventsourcing.sqlite'

# Configure SQLite database URI. Either use a file-based DB;
os.environ['SQLITE_DBNAME'] = str(db_path)

# # or use an in-memory DB with cache not shared, only works with single thread;
# os.environ['SQLITE_DBNAME'] = ':memory:'

# # or use an unnamed in-memory DB with shared cache, works with multiple threads;
# os.environ['SQLITE_DBNAME'] = 'file::memory:?mode=memory&cache=shared'

# # or use a named in-memory DB with shared cache, to create distinct databases.
# os.environ['SQLITE_DBNAME'] = 'file:application1?mode=memory&cache=shared'

# Set optional lock timeout (default 5s).
os.environ['SQLITE_LOCK_TIMEOUT'] = '10'  # seconds

# -*- coding: utf-8 -*-
from eventsourcing.persistence import IntegrityError

from part3_try_pyeventsourcing.application import DogSchool


def test_sqlite3_database():
    """
    https://eventsourcing.readthedocs.io/en/stable/topics/tutorial/part3.html#database-configuration
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
    expected_num_visible = len(tricks) if expect_visible_in_db else 0

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
