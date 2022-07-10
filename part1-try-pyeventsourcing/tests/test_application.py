# -*- coding: utf-8 -*-
from part1_try_pyeventsourcing.application import DogSchool


def test_dog_school() -> None:
    """
    loom url here: https://www.loom.com/share/2186678ab46b45aa821c6ecb5b102505
    from https://eventsourcing.readthedocs.io/en/stable/topics/tutorial/part1.html#project-structure
    to https://eventsourcing.readthedocs.io/en/stable/topics/tutorial/part1.html#exercise

    https://eventsourcing.readthedocs.io/en/stable/topics/tutorial/part1.html#project-structure:~:text=Then%20run%20the%20test%20function%20and%20see%20that%20it%20fails.
    tells us to fail because DogSchool and Dog are not created yet. ✅

    https://eventsourcing.readthedocs.io/en/stable/topics/tutorial/part1.html#project-structure:~:text=Then%20add%20the%20DogSchool%20application%20and%20the%20Dog%20aggregate%20code.%20Then%20run%20the%20test%20function%20again%20and%20see%20that%20it%20passes.
    tells us to add DogSchool and Dog and make sure the test pass. ✅
    """

    # Construct application object.
    app = DogSchool()

    # Call application command methods.
    dog_id = app.register_dog("Fido")
    app.add_trick(dog_id, "roll over")
    app.add_trick(dog_id, "fetch ball")

    # Call application query method.
    assert app.get_dog(dog_id) == {
        "name": "Fido",
        "tricks": ("roll over", "fetch ball"),
    }
