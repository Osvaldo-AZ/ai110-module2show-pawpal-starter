# Testing Ground
from datetime import time

from pawpal_system import (
    Owner, Pet, Task,
    TaskCategory, Priority,
    Scheduler,
)

# ---------------------------------------------------------------------------
# Define pets
# ---------------------------------------------------------------------------

mochi = Pet(
    name="Mochi",
    species="dog",
    breed="Shiba Inu",
    age=3,
)

luna = Pet(
    name="Luna",
    species="cat",
    age=5,
)

# ---------------------------------------------------------------------------
# Add tasks to each pet
# ---------------------------------------------------------------------------

mochi.tasks = [
    Task(
        name="Morning Walk",
        category=TaskCategory.WALK,
        priority=Priority.HIGH,
        duration_minutes=30,
        preferred_time_of_day="morning",
        is_required=True,
    ),
    Task(
        name="Breakfast",
        category=TaskCategory.FEED,
        priority=Priority.HIGH,
        duration_minutes=10,
        preferred_time_of_day="morning",
        is_required=True,
    ),
    Task(
        name="Flea & Tick Meds",
        category=TaskCategory.MEDS,
        priority=Priority.MEDIUM,
        duration_minutes=5,
        preferred_time_of_day="morning",
    ),
    Task(
        name="Fetch / Play",
        category=TaskCategory.ENRICHMENT,
        priority=Priority.LOW,
        duration_minutes=20,
        preferred_time_of_day="evening",
    ),
]

luna.tasks = [
    Task(
        name="Breakfast",
        category=TaskCategory.FEED,
        priority=Priority.HIGH,
        duration_minutes=5,
        preferred_time_of_day="morning",
        is_required=True,
    ),
    Task(
        name="Brush Coat",
        category=TaskCategory.GROOMING,
        priority=Priority.MEDIUM,
        duration_minutes=15,
        preferred_time_of_day="evening",
    ),
    Task(
        name="Interactive Toy Session",
        category=TaskCategory.ENRICHMENT,
        priority=Priority.LOW,
        duration_minutes=10,
        preferred_time_of_day="evening",
    ),
]

# ---------------------------------------------------------------------------
# Create owner and attach pets
# ---------------------------------------------------------------------------

jordan = Owner(
    name="Jordan",
    available_minutes_per_day=90,
    start_time=time(7, 30),   # day starts at 7:30 AM
    preferred_times=["morning", "evening"],
    pets=[mochi, luna],
)

# ---------------------------------------------------------------------------
# Generate and print the schedule
# ---------------------------------------------------------------------------

scheduler = Scheduler(owner=jordan)
plan = scheduler.generate_plan()

print("=" * 50)
print("         TODAY'S SCHEDULE — PawPal+")
print("=" * 50)
print(plan.get_summary())
print()
print(plan.explain())
print("=" * 50)
