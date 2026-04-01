"""PawPal+ core business logic: Task, Pet, Owner, and Scheduler classes."""

from datetime import date, timedelta
from collections import defaultdict


class Task:
    """Represents a single pet care activity with a description, time, frequency, and completion status."""

    # How many days until the next occurrence for each frequency
    _RECURRENCE_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}

    def __init__(self, description: str, time: str, frequency: str = "daily",
                 due_date: date | None = None):
        """Initialize a Task with a description, scheduled time, frequency, and optional due date."""
        self.description = description
        self.time = time              # "HH:MM" string, e.g. "08:00"
        self.frequency = frequency   # "daily" | "weekly" | "monthly" | "once"
        self.due_date = due_date or date.today()
        self.completed = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def reset(self):
        """Reset completion status (e.g. at the start of a new day)."""
        self.completed = False

    def next_occurrence(self) -> "Task | None":
        """Return a fresh Task for the next scheduled occurrence, or None if frequency is 'once'."""
        days = self._RECURRENCE_DAYS.get(self.frequency)
        if days is None:
            return None
        next_date = self.due_date + timedelta(days=days)
        return Task(self.description, self.time, self.frequency, next_date)

    def __repr__(self):
        """Return a developer-friendly string representation of the task."""
        status = "✓" if self.completed else "○"
        return f"[{status}] {self.time} — {self.description} ({self.frequency}, due {self.due_date})"


class Pet:
    """Stores pet details and maintains a list of care tasks."""

    def __init__(self, name: str, species: str, age: int):
        """Initialize a Pet with a name, species, and age."""
        self.name = name
        self.species = species
        self.age = age
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, description: str):
        """Remove all tasks matching the given description."""
        self.tasks = [t for t in self.tasks if t.description != description]

    def get_pending_tasks(self) -> list[Task]:
        """Return all incomplete tasks for this pet."""
        return [t for t in self.tasks if not t.completed]

    def __repr__(self):
        """Return a developer-friendly string representation of the pet."""
        return f"Pet({self.name}, {self.species}, age={self.age})"


class Owner:
    """Manages multiple pets and provides unified access to all their tasks."""

    def __init__(self, name: str, email: str):
        """Initialize an Owner with a name and email address."""
        self.name = name
        self.email = email
        self.owned_pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        """Register a pet under this owner."""
        self.owned_pets.append(pet)

    def remove_pet(self, pet_name: str):
        """Remove a pet by name."""
        self.owned_pets = [p for p in self.owned_pets if p.name != pet_name]

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs across every owned pet."""
        return [(pet, task) for pet in self.owned_pets for task in pet.tasks]

    def __repr__(self):
        """Return a developer-friendly string representation of the owner."""
        return f"Owner({self.name}, {len(self.owned_pets)} pet(s))"


class ConflictWarning:
    """Represents a detected scheduling conflict between two tasks."""

    def __init__(self, time: str, pet_a: Pet, task_a: Task, pet_b: Pet, task_b: Task):
        """Store the conflicting time slot and both (pet, task) pairs."""
        self.time = time
        self.pet_a = pet_a
        self.task_a = task_a
        self.pet_b = pet_b
        self.task_b = task_b

    def message(self) -> str:
        """Return a human-readable warning string (never raises, never crashes)."""
        return (
            f"⚠ Conflict at {self.time}: "
            f"'{self.task_a.description}' ({self.pet_a.name}) "
            f"clashes with '{self.task_b.description}' ({self.pet_b.name})"
        )

    def __repr__(self):
        """Return the conflict warning message."""
        return self.message()


class Scheduler:
    """The brain of PawPal+: sorts, filters, manages recurring tasks, and detects conflicts."""

    def __init__(self, owner: Owner):
        """Initialize the Scheduler with a reference to an Owner."""
        self.owner = owner

    # ── Sorting ──────────────────────────────────────────────────────────────

    def get_todays_schedule(self) -> list[tuple[Pet, Task]]:
        """Return all tasks sorted chronologically by time (HH:MM string sort is correct for 24h)."""
        all_tasks = self.owner.get_all_tasks()
        return sorted(all_tasks, key=lambda pair: pair[1].time)

    # ── Filtering ────────────────────────────────────────────────────────────

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return only incomplete tasks, sorted by time."""
        return [(pet, task) for pet, task in self.get_todays_schedule()
                if not task.completed]

    def filter_by_pet(self, pet_name: str) -> list[tuple[Pet, Task]]:
        """Return all tasks (sorted) belonging to a specific pet, matched case-insensitively."""
        return [
            (pet, task) for pet, task in self.get_todays_schedule()
            if pet.name.lower() == pet_name.lower()
        ]

    def filter_by_status(self, completed: bool) -> list[tuple[Pet, Task]]:
        """Return tasks filtered by completion status, sorted by time."""
        return [
            (pet, task) for pet, task in self.get_todays_schedule()
            if task.completed == completed
        ]

    def filter_by_frequency(self, frequency: str) -> list[tuple[Pet, Task]]:
        """Return tasks matching a specific frequency (e.g. 'daily', 'weekly'), sorted by time."""
        return [
            (pet, task) for pet, task in self.get_todays_schedule()
            if task.frequency.lower() == frequency.lower()
        ]

    # ── Recurring tasks ──────────────────────────────────────────────────────

    def mark_task_complete(self, pet_name: str, task_description: str) -> bool:
        """Mark a task complete and automatically schedule its next occurrence if recurring.

        Returns True if the task was found, False otherwise.
        For daily/weekly/monthly tasks, a new Task is appended with the next due date.
        """
        for pet in self.owner.owned_pets:
            if pet.name.lower() != pet_name.lower():
                continue
            for task in pet.tasks:
                if task.description.lower() != task_description.lower():
                    continue
                task.mark_complete()
                next_task = task.next_occurrence()
                if next_task:
                    pet.add_task(next_task)
                return True
        return False

    # ── Conflict detection ───────────────────────────────────────────────────

    def detect_conflicts(self) -> list[ConflictWarning]:
        """Return a list of ConflictWarning objects for every pair of tasks sharing the same time.

        Strategy: group tasks by time slot using a dict, then flag any slot with >1 task.
        This is O(n) in grouping and never crashes — it returns warnings, not exceptions.
        The tradeoff: only exact HH:MM matches are detected; overlapping durations are not.
        """
        by_time: dict[str, list[tuple[Pet, Task]]] = defaultdict(list)
        for pet, task in self.get_todays_schedule():
            by_time[task.time].append((pet, task))

        warnings: list[ConflictWarning] = []
        for time_slot, entries in by_time.items():
            for i in range(len(entries)):
                for j in range(i + 1, len(entries)):
                    pet_a, task_a = entries[i]
                    pet_b, task_b = entries[j]
                    warnings.append(ConflictWarning(time_slot, pet_a, task_a, pet_b, task_b))
        return warnings

    # ── Printing ─────────────────────────────────────────────────────────────

    def print_schedule(self, pairs: list[tuple[Pet, Task]] | None = None):
        """Print a formatted schedule table; defaults to the full sorted schedule if no pairs given."""
        pairs = pairs if pairs is not None else self.get_todays_schedule()
        width = 50
        print(f"\n{'=' * width}")
        print(f"  PawPal+ Schedule — {self.owner.name}")
        print(f"{'=' * width}")
        if not pairs:
            print("  No tasks to display.")
        for pet, task in pairs:
            status = "✓ Done" if task.completed else "○ Pending"
            print(f"  {task.time}  [{pet.name:10s}]  {task.description:<25s}  {status}")
        print(f"{'=' * width}\n")
