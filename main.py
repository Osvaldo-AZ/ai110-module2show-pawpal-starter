# Testing Ground
from datetime import date, time

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
# Add tasks OUT OF ORDER (low → high priority, optional before required)
# ---------------------------------------------------------------------------

mochi.tasks = [
    Task(
        name="Fetch / Play",
        category=TaskCategory.ENRICHMENT,
        priority=Priority.LOW,
        duration_minutes=20,
        preferred_time_of_day="evening",
    ),
    Task(
        name="Flea & Tick Meds",
        category=TaskCategory.MEDS,
        priority=Priority.MEDIUM,
        duration_minutes=5,
        preferred_time_of_day="morning",
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
        name="Morning Walk",
        category=TaskCategory.WALK,
        priority=Priority.HIGH,
        duration_minutes=30,
        preferred_time_of_day="morning",
        is_required=True,
    ),
]

luna.tasks = [
    Task(
        name="Interactive Toy Session",
        category=TaskCategory.ENRICHMENT,
        priority=Priority.LOW,
        duration_minutes=10,
        preferred_time_of_day="evening",
    ),
    Task(
        name="Brush Coat",
        category=TaskCategory.GROOMING,
        priority=Priority.MEDIUM,
        duration_minutes=15,
        preferred_time_of_day="evening",
    ),
    Task(
        name="Breakfast",
        category=TaskCategory.FEED,
        priority=Priority.HIGH,
        duration_minutes=5,
        preferred_time_of_day="morning",
        is_required=True,
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
# Demo filter_tasks BEFORE scheduling
# ---------------------------------------------------------------------------

print("=" * 50)
print("  FILTER DEMO (before scheduling)")
print("=" * 50)

all_tasks = jordan.filter_tasks()
print(f"\nAll tasks ({len(all_tasks)} total):")
for pet_name, task in all_tasks:
    status = "[done]" if task.completed else "[    ]"
    req    = " [required]" if task.is_required else ""
    print(f"  {status} [{pet_name}] {task.name} — {task.priority.name}{req}")

mochi_tasks = jordan.filter_tasks(pet_name="Mochi")
print(f"\nMochi's tasks only ({len(mochi_tasks)}):")
for _, task in mochi_tasks:
    print(f"  [{task.priority.name}] {task.name}")

incomplete = jordan.filter_tasks(completed=False)
print(f"\nIncomplete tasks ({len(incomplete)}):")
for pet_name, task in incomplete:
    print(f"  [{pet_name}] {task.name}")

# ---------------------------------------------------------------------------
# Generate and print the schedule
# (sorting happens inside Scheduler._sort_by_priority)
# ---------------------------------------------------------------------------

scheduler = Scheduler(owner=jordan)
plan = scheduler.generate_plan()

print()
print("=" * 50)
print("         TODAY'S SCHEDULE — PawPal+")
print("=" * 50)
print(plan.get_summary())
print()
print(plan.explain())
print("=" * 50)

# ---------------------------------------------------------------------------
# Mark some tasks complete, then re-filter to show completed vs incomplete
# ---------------------------------------------------------------------------

# Mark the first two scheduled tasks as done
for st in plan.scheduled_tasks[:2]:
    st.task.mark_complete()

print()
print("  FILTER DEMO (after marking 2 tasks complete)")
print("=" * 50)

completed_tasks = jordan.filter_tasks(completed=True)
print(f"\nCompleted tasks ({len(completed_tasks)}):")
for pet_name, task in completed_tasks:
    print(f"  [done] [{pet_name}] {task.name}")

still_pending = jordan.filter_tasks(completed=False)
print(f"\nStill pending ({len(still_pending)}):")
for pet_name, task in still_pending:
    print(f"  [    ] [{pet_name}] {task.name}")

luna_incomplete = jordan.filter_tasks(completed=False, pet_name="Luna")
print(f"\nLuna's incomplete tasks ({len(luna_incomplete)}):")
for _, task in luna_incomplete:
    print(f"  [    ] {task.name}")

print("=" * 50)

# ---------------------------------------------------------------------------
# Recurrence demo
# ---------------------------------------------------------------------------

print()
print("=" * 50)
print("  RECURRENCE DEMO")
print("=" * 50)

# Add a daily and a weekly recurring task to Mochi
daily_walk = Task(
    name="Evening Walk",
    category=TaskCategory.WALK,
    priority=Priority.HIGH,
    duration_minutes=20,
    preferred_time_of_day="evening",
    is_required=True,
    recurrence="daily",
    due_date=date.today(),
)
weekly_bath = Task(
    name="Bath Time",
    category=TaskCategory.GROOMING,
    priority=Priority.MEDIUM,
    duration_minutes=30,
    preferred_time_of_day="morning",
    recurrence="weekly",
    due_date=date.today(),
)
mochi.tasks.append(daily_walk)
mochi.tasks.append(weekly_bath)

print(f"\nBefore completing -- Mochi has {len(mochi.tasks)} tasks")

# complete_task marks done and registers next occurrence
next_walk = scheduler.complete_task("Mochi", daily_walk)
next_bath = scheduler.complete_task("Mochi", weekly_bath)

print(f"After completing  -- Mochi has {len(mochi.tasks)} tasks")
print()

for label, original, nxt in [
    ("Evening Walk (daily)", daily_walk, next_walk),
    ("Bath Time (weekly)",   weekly_bath, next_bath),
]:
    print(f"  {label}")
    print(f"    Original  -- completed: {original.completed}, due: {original.due_date}")
    if nxt:
        print(f"    Next copy -- completed: {nxt.completed}, due: {nxt.due_date}")
    print()

# One-off task produces no next occurrence
one_off = Task(
    name="Vet Visit",
    category=TaskCategory.OTHER,
    priority=Priority.HIGH,
    duration_minutes=60,
    recurrence="",  # one-off
    due_date=date.today(),
)
mochi.tasks.append(one_off)
result = scheduler.complete_task("Mochi", one_off)
print(f"  Vet Visit (one-off) -- next_occurrence returned: {result}")

print()
print("=" * 50)

# ---------------------------------------------------------------------------
# Conflict detection demo
# ---------------------------------------------------------------------------

print()
print("=" * 50)
print("  CONFLICT DETECTION DEMO")
print("=" * 50)

from pawpal_system import Schedule, ScheduledTask

shared_scheduler = Scheduler(owner=jordan)

# --- Scenario 1: exact same start time (same pet) ---
# Mochi: Breakfast and Flea Meds both at 08:00
same_time_plan = Schedule(date=date.today())
same_time_plan.add_task(ScheduledTask(
    task=Task("Breakfast",     TaskCategory.FEED, Priority.HIGH,   10, is_required=True),
    assigned_time=time(8, 0),
    pet_name="Mochi",
))
same_time_plan.add_task(ScheduledTask(
    task=Task("Flea Meds",     TaskCategory.MEDS, Priority.MEDIUM, 5),
    assigned_time=time(8, 0),  # exact same time as Breakfast
    pet_name="Mochi",
))
same_time_plan.add_task(ScheduledTask(
    task=Task("Evening Walk",  TaskCategory.WALK, Priority.HIGH,   20),
    assigned_time=time(18, 0), # separate slot — no conflict
    pet_name="Mochi",
))

same_time_plan.conflicts = shared_scheduler.detect_conflicts(same_time_plan)
warning = shared_scheduler.warn_on_conflicts(same_time_plan)

print("\n--- Scenario 1: two tasks at exactly the same time (same pet) ---")
print(f"detect_conflicts found: {len(same_time_plan.conflicts)} conflict(s)")
print(warning if warning else "No warning.")
print()
print(same_time_plan.get_summary())

# --- Scenario 2: exact same start time (different pets) ---
# Mochi's Morning Walk and Luna's Breakfast both at 08:00
cross_pet_plan = Schedule(date=date.today())
cross_pet_plan.add_task(ScheduledTask(
    task=Task("Morning Walk",   TaskCategory.WALK, Priority.HIGH, 30, is_required=True),
    assigned_time=time(8, 0),
    pet_name="Mochi",
))
cross_pet_plan.add_task(ScheduledTask(
    task=Task("Luna Breakfast", TaskCategory.FEED, Priority.HIGH,  5, is_required=True),
    assigned_time=time(8, 0),  # same start as Mochi's Walk
    pet_name="Luna",
))
cross_pet_plan.add_task(ScheduledTask(
    task=Task("Brush Coat",     TaskCategory.GROOMING, Priority.MEDIUM, 15),
    assigned_time=time(9, 0),  # separate slot — no conflict
    pet_name="Luna",
))

cross_pet_plan.conflicts = shared_scheduler.detect_conflicts(cross_pet_plan)
warning = shared_scheduler.warn_on_conflicts(cross_pet_plan)

print("\n--- Scenario 2: two tasks at exactly the same time (different pets) ---")
print(f"detect_conflicts found: {len(cross_pet_plan.conflicts)} conflict(s)")
print(warning if warning else "No warning.")
print()
print(cross_pet_plan.get_summary())

print()
print("=" * 50)
