# logic layer
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, time
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
    preferred_time_of_day: str = ""   # e.g. "morning", "evening"
    is_required: bool = False

    def to_dict(self) -> dict:
        pass


@dataclass
class ScheduledTask:
    task: Task
    assigned_time: time  # e.g. time(8, 0) for 8:00 AM
    reason: str = ""


@dataclass
class Pet:
    name: str
    species: str
    breed: str = ""
    age: int = 0
    special_needs: list[str] = field(default_factory=list)

    def get_applicable_tasks(self) -> list[Task]:
        pass


@dataclass
class Owner:
    name: str
    available_minutes_per_day: int
    start_time: time = field(default_factory=lambda: time(8, 0))  # default: 8:00 AM
    preferred_times: list[str] = field(default_factory=list)  # e.g. ["morning", "evening"]

    def get_available_time(self) -> int:
        pass


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
        pass

    def get_summary(self) -> str:
        pass

    def explain(self) -> str:
        pass


# ---------------------------------------------------------------------------
# Scheduler (logic engine)
# ---------------------------------------------------------------------------

class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]) -> None:
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate_plan(self) -> Schedule:
        pass

    def _sort_by_priority(self) -> list[Task]:
        # Sort key: required first, then by priority value (high=3 first), then by preferred time
        pass

    def _fits_in_time(self, task: Task, minutes_used: int) -> bool:
        pass

    def _explain_choice(self, task: Task) -> str:
        pass
