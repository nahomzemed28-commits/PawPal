"""Automated tests for PawPal+ core logic."""

import pytest
from pawpal_system import Task, Pet, Owner, Scheduler


# ── Task tests ──────────────────────────────────────────────────────────────

def test_mark_complete_changes_status():
    """Task completion status should be False by default, True after mark_complete()."""
    task = Task("Morning walk", "07:00", "daily")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_reset_clears_completion():
    """Calling reset() on a completed task should set completed back to False."""
    task = Task("Evening walk", "18:00", "daily")
    task.mark_complete()
    task.reset()
    assert task.completed is False


# ── Pet tests ────────────────────────────────────────────────────────────────

def test_add_task_increases_count():
    """Adding a task to a Pet should increase its task list by one."""
    pet = Pet(name="Luna", species="Dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task("Feeding", "08:00", "daily"))
    assert len(pet.tasks) == 1
    pet.add_task(Task("Walk", "17:00", "daily"))
    assert len(pet.tasks) == 2


def test_get_pending_tasks_excludes_completed():
    """get_pending_tasks() should only return tasks that are not completed."""
    pet = Pet(name="Mochi", species="Cat", age=2)
    t1 = Task("Feeding", "08:00", "daily")
    t2 = Task("Playtime", "12:00", "daily")
    pet.add_task(t1)
    pet.add_task(t2)
    t1.mark_complete()
    pending = pet.get_pending_tasks()
    assert len(pending) == 1
    assert pending[0].description == "Playtime"


# ── Scheduler tests ──────────────────────────────────────────────────────────

def test_schedule_sorted_by_time():
    """get_todays_schedule() should return tasks in chronological order."""
    owner = Owner("Test Owner", "test@test.com")
    pet = Pet("Buddy", "Dog", 1)
    pet.add_task(Task("Evening walk", "18:00", "daily"))
    pet.add_task(Task("Morning walk", "07:00", "daily"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    schedule = scheduler.get_todays_schedule()
    times = [task.time for _, task in schedule]
    assert times == sorted(times)


def test_detect_conflicts_finds_same_time():
    """detect_conflicts() should flag tasks scheduled at the exact same time."""
    owner = Owner("Test Owner", "test@test.com")
    pet = Pet("Buddy", "Dog", 1)
    pet.add_task(Task("Medication", "08:00", "daily"))
    pet.add_task(Task("Feeding", "08:00", "daily"))
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) > 0


def test_mark_task_complete_via_scheduler():
    """Scheduler.mark_task_complete() should return True and update the task."""
    owner = Owner("Test Owner", "test@test.com")
    pet = Pet("Buddy", "Dog", 1)
    task = Task("Morning walk", "07:00", "daily")
    pet.add_task(task)
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    result = scheduler.mark_task_complete("Buddy", "Morning walk")
    assert result is True
    assert task.completed is True
