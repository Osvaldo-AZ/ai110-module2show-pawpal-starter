import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Task, Pet, TaskCategory, Priority


def test_mark_complete_changes_status():
    task = Task(
        name="Morning Walk",
        category=TaskCategory.WALK,
        priority=Priority.HIGH,
        duration_minutes=30,
    )
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Mochi", species="dog")
    assert len(pet.tasks) == 0

    pet.tasks.append(Task(
        name="Breakfast",
        category=TaskCategory.FEED,
        priority=Priority.HIGH,
        duration_minutes=10,
    ))
    assert len(pet.tasks) == 1
