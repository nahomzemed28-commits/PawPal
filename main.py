"""Demo script verifying all Phase 4 algorithmic features in the terminal."""

from pawpal_system import Task, Pet, Owner, Scheduler


def section(title: str):
    print(f"\n{'─' * 50}")
    print(f"  {title}")
    print(f"{'─' * 50}")


def main():
    # ── Setup ─────────────────────────────────────────────────────────────────
    owner = Owner(name="Nahom", email="nahom@pawpal.com")

    luna = Pet(name="Luna", species="Dog", age=3)
    mochi = Pet(name="Mochi", species="Cat", age=5)
    owner.add_pet(luna)
    owner.add_pet(mochi)

    # Tasks added intentionally out of chronological order to prove sorting works
    luna.add_task(Task("Evening walk",        "18:00", "daily"))
    luna.add_task(Task("Morning walk",        "07:00", "daily"))
    luna.add_task(Task("Breakfast feeding",   "08:00", "daily"))
    luna.add_task(Task("Heartworm meds",      "08:00", "weekly"))  # conflict with Mochi below

    mochi.add_task(Task("Playtime",           "12:00", "daily"))
    mochi.add_task(Task("Breakfast feeding",  "08:00", "daily"))   # same time as Luna's meds
    mochi.add_task(Task("Flea treatment",     "19:00", "once"))

    scheduler = Scheduler(owner)

    # ── 1. SORTING ────────────────────────────────────────────────────────────
    section("1. Sorted Full Schedule (tasks were added out of order)")
    scheduler.print_schedule()

    # ── 2. FILTERING by pet ───────────────────────────────────────────────────
    section("2a. Filter — Luna's tasks only")
    scheduler.print_schedule(scheduler.filter_by_pet("Luna"))

    section("2b. Filter — Mochi's tasks only")
    scheduler.print_schedule(scheduler.filter_by_pet("Mochi"))

    # ── 3. FILTERING by status ────────────────────────────────────────────────
    # Mark a couple complete first
    scheduler.mark_task_complete("Luna", "Morning walk")
    scheduler.mark_task_complete("Mochi", "Playtime")

    section("3a. Filter — completed tasks only")
    scheduler.print_schedule(scheduler.filter_by_status(completed=True))

    section("3b. Filter — pending tasks only")
    scheduler.print_schedule(scheduler.filter_by_status(completed=False))

    # ── 4. FILTERING by frequency ─────────────────────────────────────────────
    section("4. Filter — daily tasks only")
    scheduler.print_schedule(scheduler.filter_by_frequency("daily"))

    # ── 5. RECURRING TASKS ────────────────────────────────────────────────────
    section("5. Recurring task — completing 'Evening walk' (daily) auto-schedules next occurrence")
    luna_tasks_before = len(luna.tasks)
    scheduler.mark_task_complete("Luna", "Evening walk")
    luna_tasks_after = len(luna.tasks)
    print(f"  Luna's task count before: {luna_tasks_before}")
    print(f"  Luna's task count after:  {luna_tasks_after}  (new occurrence appended)")
    newest = luna.tasks[-1]
    print(f"  New task: {newest}")

    section("6. Recurring task — completing 'Heartworm meds' (weekly) auto-schedules next")
    meds_before = len(luna.tasks)
    scheduler.mark_task_complete("Luna", "Heartworm meds")
    meds_after = len(luna.tasks)
    print(f"  Luna's task count before: {meds_before}")
    print(f"  Luna's task count after:  {meds_after}")
    print(f"  New task: {luna.tasks[-1]}")

    # ── 6. CONFLICT DETECTION ─────────────────────────────────────────────────
    section("7. Conflict detection — tasks at the same time slot")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  {warning.message()}")
    else:
        print("  No conflicts detected.")

    # ── 7. ONCE-OFF task does NOT recur ──────────────────────────────────────
    section("8. 'once' frequency — completing Flea treatment should NOT create next occurrence")
    mochi_before = len(mochi.tasks)
    scheduler.mark_task_complete("Mochi", "Flea treatment")
    mochi_after = len(mochi.tasks)
    print(f"  Mochi's task count before: {mochi_before}")
    print(f"  Mochi's task count after:  {mochi_after}  (should be same — no recurrence)")


if __name__ == "__main__":
    main()
