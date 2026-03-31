"""PawPal+ core business logic: Task, Pet, Owner, and Scheduler classes."""

from datetime import datetime


class Task:
    """Represents a single pet care activity with a description, time, frequency, and completion status."""

    def __init__(self, description: str, time: str, frequency: str = "daily"):
        """Initialize a Task with a description, scheduled time, and frequency."""
        self.description = description
        self.time = time  # e.g. "08:00", "14:30"
        self.frequency = frequency  # e.g. "daily", "weekly", "once"
        self.completed = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.completed = True

    def reset(self):
        """Reset completion status (e.g. for a new day)."""
        self.completed = False

    def __repr__(self):
        """Return a developer-friendly string representation of the task."""
        status = "✓" if self.completed else "○"
        return f"[{status}] {self.time} — {self.description} ({self.frequency})"


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
        """Remove a task by its description."""
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


class Scheduler:
    """The brain of PawPal+: retrieves, sorts, and manages tasks across all of an owner's pets."""

    def __init__(self, owner: Owner):
        """Initialize the Scheduler with a reference to an Owner."""
        self.owner = owner

    def get_todays_schedule(self) -> list[tuple[Pet, Task]]:
        """Return all tasks sorted chronologically by scheduled time."""
        all_tasks = self.owner.get_all_tasks()
        return sorted(all_tasks, key=lambda pair: pair[1].time)

    def get_pending_tasks(self) -> list[tuple[Pet, Task]]:
        """Return only incomplete tasks, sorted by time."""
        return [(pet, task) for pet, task in self.get_todays_schedule()
                if not task.completed]

    def detect_conflicts(self) -> list[tuple[Task, Task]]:
        """Return pairs of tasks scheduled at the exact same time."""
        schedule = self.get_todays_schedule()
        conflicts = []
        for i in range(len(schedule)):
            for j in range(i + 1, len(schedule)):
                if schedule[i][1].time == schedule[j][1].time:
                    conflicts.append((schedule[i][1], schedule[j][1]))
        return conflicts

    def mark_task_complete(self, pet_name: str, task_description: str) -> bool:
        """Mark a specific task as complete; return True if found, False otherwise."""
        for pet in self.owner.owned_pets:
            if pet.name == pet_name:
                for task in pet.tasks:
                    if task.description == task_description:
                        task.mark_complete()
                        return True
        return False

    def print_schedule(self):
        """Print today's full schedule to the terminal in a readable format."""
        schedule = self.get_todays_schedule()
        print(f"\n{'=' * 45}")
        print(f"  PawPal+ Today's Schedule — {self.owner.name}")
        print(f"{'=' * 45}")
        if not schedule:
            print("  No tasks scheduled.")
        for pet, task in schedule:
            status = "✓ Done" if task.completed else "○ Pending"
            print(f"  {task.time}  [{pet.name:10s}]  {task.description:<25s}  {status}")
        print(f"{'=' * 45}\n")
