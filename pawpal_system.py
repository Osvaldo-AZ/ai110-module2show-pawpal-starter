# logic layer
from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import date, time, datetime, timedelta
from enum import Enum
from itertools import combinations

# Constant — recurrence intervals used by Task.next_occurrence()
_RECURRENCE_INTERVALS: dict[str, timedelta] = {
    "daily": timedelta(days=1),
    "weekly": timedelta(weeks=1),
}


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class TaskCategory(Enum):
    WALK = "walk"
    FEED = "feed"
    MEDS = "meds"
    GROOMING = "grooming"
    ENRICHMENT = "enrichment"
    OTHER = "other"


class Priority(Enum):
    HIGH = 3
    MEDIUM = 2
    LOW = 1


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Task:
    name: str
    category: TaskCategory
    priority: Priority
    duration_minutes: int
    preferred_time_of_day: str = ""  # e.g. "morning", "evening"
    is_required: bool = False
    completed: bool = False
    recurrence: str = ""        # "daily", "weekly", or "" for one-off
    due_date: date | None = None

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def next_occurrence(self) -> Task | None:
        """Return a new Task for the next recurrence, or None if this is a one-off.

        Creates a copy of this task with completed reset to False and due_date
        advanced by the recurrence interval defined in _RECURRENCE_INTERVALS.

        Note: if due_date is None, today's date is used as the baseline.  This
        means calling next_occurrence() on a task that was never given a due_date
        anchors the next occurrence to the current day, not to when the task was
        originally created.

        Returns:
            A new Task for the next occurrence, or None if recurrence is unset.
        """
        if self.recurrence not in _RECURRENCE_INTERVALS:
            return None
        base = self.due_date or date.today()
        return replace(self, completed=False, due_date=base + _RECURRENCE_INTERVALS[self.recurrence])

    def to_dict(self) -> dict:
        """Return a plain-dict representation of this task."""
        return {
            "name": self.name,
            "category": self.category.value,
            "priority": self.priority.name.lower(),
            "duration_minutes": self.duration_minutes,
            "preferred_time_of_day": self.preferred_time_of_day,
            "is_required": self.is_required,
            "recurrence": self.recurrence or "none",
            "due_date": str(self.due_date) if self.due_date else "—",
        }


@dataclass
class ScheduledTask:
    task: Task
    assigned_time: time  # e.g. time(8, 0) for 8:00 AM
    pet_name: str = ""
    reason: str = ""


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    age: int = 0
    special_needs: list[str] = field(default_factory=list)
    tasks: list[Task] = field(default_factory=list)

    def get_applicable_tasks(self) -> list[Task]:
        """Return tasks valid for this pet's species (e.g. no walks for cats)."""
        excluded: set[TaskCategory] = set()
        if self.species.lower() != "dog":
            excluded.add(TaskCategory.WALK)
        return [t for t in self.tasks if t.category not in excluded]


@dataclass
class Owner:
    name: str
    available_minutes_per_day: int
    start_time: time = field(default_factory=lambda: time(8, 0))  # default: 8:00 AM
    preferred_times: list[str] = field(default_factory=list)      # e.g. ["morning", "evening"]
    pets: list[Pet] = field(default_factory=list)

    def get_available_time(self) -> int:
        """Return the number of minutes the owner has available today."""
        return self.available_minutes_per_day

    def get_all_tasks(self) -> list[tuple[str, Task]]:
        """Collect applicable tasks from every pet, paired with the pet's name."""
        return [
            (pet.name, task)
            for pet in self.pets
            for task in pet.get_applicable_tasks()
        ]

    def filter_tasks(
        self,
        *,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[tuple[str, Task]]:
        """Return tasks filtered by completion status and/or pet name.

        Delegates to get_all_tasks(), so species-excluded tasks (e.g. walks for
        non-dogs) are never included in the results regardless of filters applied.
        Both filters are applied in a single pass over the task list.

        Args:
            completed: If True, return only completed tasks.  If False, return
                       only incomplete tasks.  If None, completion is not filtered.
            pet_name:  If given, return only tasks belonging to that pet
                       (case-insensitive).  If None, all pets are included.

        Returns:
            A list of (pet_name, Task) tuples matching all supplied filters.
        """
        return [
            (pn, t) for pn, t in self.get_all_tasks()
            if (pet_name is None or pn.lower() == pet_name.lower())
            and (completed is None or t.completed == completed)
        ]


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

@dataclass
class Schedule:
    date: date
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    skipped_tasks: list[tuple[Task, str]] = field(default_factory=list)  # (task, reason skipped)
    total_minutes_used: int = 0
    conflicts: list[tuple[ScheduledTask, ScheduledTask]] = field(default_factory=list)

    def add_task(self, scheduled_task: ScheduledTask) -> None:
        """Append a scheduled task and update the running time total."""
        self.scheduled_tasks.append(scheduled_task)
        self.total_minutes_used += scheduled_task.task.duration_minutes

    def get_summary(self) -> str:
        """Return a compact, time-ordered list of scheduled and skipped tasks."""
        lines = [
            f"Schedule for {self.date} — "
            f"{len(self.scheduled_tasks)} task(s), {self.total_minutes_used} min used"
        ]
        for st in self.scheduled_tasks:
            lines.append(
                f"  {st.assigned_time.strftime('%I:%M %p')}  "
                f"[{st.pet_name}] {st.task.name} ({st.task.duration_minutes} min)"
            )
        if self.skipped_tasks:
            skipped_names = ", ".join(t.name for t, _ in self.skipped_tasks)
            lines.append(f"  Skipped: {skipped_names}")
        if self.conflicts:
            lines.append(f"  WARNING: {len(self.conflicts)} time conflict(s) detected!")
            for a, b in self.conflicts:
                lines.append(
                    f"    [{a.pet_name}] {a.task.name} vs [{b.pet_name}] {b.task.name}"
                )
        return "\n".join(lines)

    def explain(self) -> str:
        """Return a per-task explanation including any skipped tasks and their reasons."""
        lines = ["=== Daily Plan Explanation ==="]
        for st in self.scheduled_tasks:
            lines.append(
                f"• [{st.pet_name}] {st.task.name} at {st.assigned_time.strftime('%I:%M %p')}: {st.reason}"
            )
        if self.skipped_tasks:
            lines.append("\nSkipped tasks:")
            for task, reason in self.skipped_tasks:
                lines.append(f"• {task.name}: {reason}")
        if self.conflicts:
            lines.append("\nTime conflicts:")
            for a, b in self.conflicts:
                a_end = (datetime.combine(date.today(), a.assigned_time)
                         + timedelta(minutes=a.task.duration_minutes)).time()
                b_end = (datetime.combine(date.today(), b.assigned_time)
                         + timedelta(minutes=b.task.duration_minutes)).time()
                lines.append(
                    f"• [{a.pet_name}] {a.task.name} "
                    f"({a.assigned_time.strftime('%I:%M %p')}–{a_end.strftime('%I:%M %p')}) "
                    f"overlaps [{b.pet_name}] {b.task.name} "
                    f"({b.assigned_time.strftime('%I:%M %p')}–{b_end.strftime('%I:%M %p')})"
                )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler (logic engine)
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner) -> None:
        """Store the owner and pre-fetch all applicable tasks from their pets."""
        self.owner = owner
        self.tasks: list[tuple[str, Task]] = owner.get_all_tasks()  # (pet_name, task)

    def generate_plan(self) -> Schedule:
        """Build and return a Schedule by fitting sorted tasks into the owner's available time."""
        schedule = Schedule(date=date.today())
        sorted_tasks = self._sort_by_priority()
        minutes_used = 0
        current_dt = datetime.combine(date.today(), self.owner.start_time)

        for pet_name, task in sorted_tasks:
            if self._fits_in_time(task, minutes_used):
                schedule.add_task(ScheduledTask(
                    task=task,
                    assigned_time=current_dt.time(),
                    pet_name=pet_name,
                    reason=self._explain_choice(task),
                ))
                current_dt += timedelta(minutes=task.duration_minutes)
                minutes_used += task.duration_minutes
            else:
                remaining = self.owner.available_minutes_per_day - minutes_used
                schedule.skipped_tasks.append(
                    (task, f"Not enough time remaining ({remaining} min left, needs {task.duration_minutes} min)")
                )

        schedule.conflicts = self.detect_conflicts(schedule)
        return schedule

    @staticmethod
    def _to_minutes(t: time) -> int:
        """Convert a time object to minutes since midnight."""
        return t.hour * 60 + t.minute

    def detect_conflicts(self, schedule: Schedule) -> list[tuple[ScheduledTask, ScheduledTask]]:
        """Return all pairs of scheduled tasks whose time windows overlap.

        Uses itertools.combinations to evaluate every unique pair in O(n²) time.
        Two tasks conflict when their intervals [start, start+duration) intersect,
        i.e. start_A < end_B AND start_B < end_A.  Detects both same-pet and
        cross-pet overlaps.  For a fast single-pass alternative that trades
        completeness for speed, use warn_on_conflicts() instead.

        Args:
            schedule: The Schedule whose scheduled_tasks list will be checked.

        Returns:
            A list of (ScheduledTask, ScheduledTask) pairs that overlap in time.
            Returns an empty list when the schedule is conflict-free.
        """
        return [
            (a, b)
            for a, b in combinations(schedule.scheduled_tasks, 2)
            if self._to_minutes(a.assigned_time) < self._to_minutes(b.assigned_time) + b.task.duration_minutes
            and self._to_minutes(b.assigned_time) < self._to_minutes(a.assigned_time) + a.task.duration_minutes
        ]

    def warn_on_conflicts(self, schedule: Schedule) -> str | None:
        """Lightweight O(n log n) conflict check — returns a warning string or None.

        Sorts tasks by start time once, then walks the list linearly keeping a
        running end-time cursor.  If the next task starts before the cursor,
        a conflict is recorded.  Advances the cursor only when a task ends later
        than the current furthest end, so non-adjacent overlaps against an earlier
        task can be missed — use detect_conflicts() when complete coverage matters.

        Args:
            schedule: The Schedule whose scheduled_tasks list will be checked.

        Returns:
            A multi-line warning string listing each detected conflict, or None
            if the schedule is clean.
        """
        sorted_tasks = sorted(
            schedule.scheduled_tasks,
            key=lambda st: self._to_minutes(st.assigned_time),
        )

        warnings: list[str] = []
        running_end = 0       # minutes since midnight of the furthest end seen so far
        last_st: ScheduledTask | None = None

        for st in sorted_tasks:
            start = self._to_minutes(st.assigned_time)
            if start < running_end and last_st is not None:
                warnings.append(
                    f"[{st.pet_name}] '{st.task.name}' at "
                    f"{st.assigned_time.strftime('%I:%M %p')} overlaps "
                    f"[{last_st.pet_name}] '{last_st.task.name}' "
                    f"(ends {(running_end // 60):02d}:{(running_end % 60):02d})"
                )
            end = start + st.task.duration_minutes
            if end > running_end:
                running_end = end
                last_st = st

        if not warnings:
            return None
        return "Schedule conflict warning:\n" + "\n".join(f"  - {w}" for w in warnings)

    def complete_task(self, pet_name: str, task: Task) -> Task | None:
        """Mark a task complete and register its next occurrence if it recurs.

        Marks the task done, then — if recurrence is set — creates the next
        instance, appends it to the correct pet's task list, and adds it to
        the scheduler's internal task list so future generate_plan() calls
        include it.

        Returns the newly created Task, or None for one-off tasks.
        """
        task.mark_complete()
        next_task = task.next_occurrence()
        if next_task is None:
            return None
        for pet in self.owner.pets:
            if pet.name.lower() == pet_name.lower():
                pet.tasks.append(next_task)
                self.tasks.append((pet.name, next_task))
                break
        return next_task

    def _sort_by_priority(self) -> list[tuple[str, Task]]:
        """Sort tasks: required first, then by descending priority, then by preferred time."""
        return sorted(
            self.tasks,
            key=lambda pair: (
                not pair[1].is_required,               # False (required) sorts before True (optional)
                -pair[1].priority.value,               # higher value = higher priority, so negate
                pair[1].preferred_time_of_day or "z",  # empty preferred_time_of_day sorts last
            ),
        )

    def _fits_in_time(self, task: Task, minutes_used: int) -> bool:
        """Return True if the task fits within the owner's remaining available time."""
        return minutes_used + task.duration_minutes <= self.owner.available_minutes_per_day

    def _explain_choice(self, task: Task) -> str:
        """Build a human-readable string explaining why this task was scheduled."""
        return ", ".join(filter(None, [
            "required task" if task.is_required else "",
            f"{task.priority.name.lower()} priority",
            f"preferred time: {task.preferred_time_of_day}" if task.preferred_time_of_day else "",
        ]))
