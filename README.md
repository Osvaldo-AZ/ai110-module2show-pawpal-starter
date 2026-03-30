# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The scheduling logic in `pawpal_system.py` goes beyond a basic task list. The following features were added to make the planner more useful for a real pet owner.

### Task filtering

`Owner.filter_tasks()` lets you query tasks across all pets in a single call. You can filter by completion status, pet name, or both at once:

```python
owner.filter_tasks(completed=False, pet_name="Mochi")
```

### Recurring tasks

`Task` supports `recurrence` (`"daily"` or `"weekly"`) and a `due_date`. When you call `Scheduler.complete_task()`, the task is marked done and a fresh copy is automatically created for the next occurrence and added back to the pet's task list — no manual re-entry needed.

```python
next_task = scheduler.complete_task("Mochi", morning_walk)
# next_task.due_date == today + 1 day
```

### Conflict detection

Two methods detect scheduling overlaps using interval math (`start_A < end_B and start_B < end_A`):

| Method | Strategy | Best for |
|---|---|---|
| `detect_conflicts(schedule)` | O(n²) — checks every pair | Detailed diagnostics, `explain()` output |
| `warn_on_conflicts(schedule)` | O(n log n) — single sorted pass | Quick validation, UI banners |

Both catch same-pet and cross-pet overlaps. `detect_conflicts` is thorough; `warn_on_conflicts` trades completeness for speed and returns a plain warning string or `None`.

### Known tradeoffs

- The scheduler uses a **greedy algorithm**: tasks are sorted by priority and placed in the first available slot. Skipped tasks are not retried even if a smaller task would have fit.
- `preferred_time_of_day` influences sort order but does not constrain the actual assigned time slot.
- `warn_on_conflicts` can miss overlaps between non-adjacent tasks; use `detect_conflicts` when full coverage is required.
- If a recurring task has no `due_date`, `next_occurrence()` anchors to today's date rather than the original schedule date.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
