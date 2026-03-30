# logic layer
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time, datetime, timedelta
from enum import Enum


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

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def to_dict(self) -> dict:
        """Return a plain-dict representation of this task."""
        return {
            "name": self.name,
            "category": self.category.value,
            "priority": self.priority.name.lower(),
            "duration_minutes": self.duration_minutes,
            "preferred_time_of_day": self.preferred_time_of_day,
            "is_required": self.is_required,
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
        tagged: list[tuple[str, Task]] = []
        for pet in self.pets:
            for task in pet.get_applicable_tasks():
                tagged.append((pet.name, task))
        return tagged


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

@dataclass
class Schedule:
    date: date
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    skipped_tasks: list[tuple[Task, str]] = field(default_factory=list)  # (task, reason skipped)
    total_minutes_used: int = 0

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

        return schedule

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
        parts = []
        if task.is_required:
            parts.append("required task")
        parts.append(f"{task.priority.name.lower()} priority")
        if task.preferred_time_of_day:
            parts.append(f"preferred time: {task.preferred_time_of_day}")
        return ", ".join(parts)
