"""Demo script to verify PawPal+ backend logic in the terminal."""

from pawpal_system import Task, Pet, Owner, Scheduler


def main():
    # --- Create Owner ---
    owner = Owner(name="Nahom", email="nahom@pawpal.com")

    # --- Create Pets ---
    luna = Pet(name="Luna", species="Dog", age=3)
    mochi = Pet(name="Mochi", species="Cat", age=5)

    owner.add_pet(luna)
    owner.add_pet(mochi)

    # --- Add Tasks to Luna ---
    luna.add_task(Task("Morning walk", "07:00", "daily"))
    luna.add_task(Task("Breakfast feeding", "08:00", "daily"))
    luna.add_task(Task("Heartworm medication", "08:00", "weekly"))  # conflict with Mochi below
    luna.add_task(Task("Evening walk", "18:00", "daily"))

    # --- Add Tasks to Mochi ---
    mochi.add_task(Task("Breakfast feeding", "08:00", "daily"))
    mochi.add_task(Task("Playtime", "12:00", "daily"))
    mochi.add_task(Task("Flea treatment", "19:00", "monthly"))

    # --- Create Scheduler ---
    scheduler = Scheduler(owner)

    # --- Print Full Schedule ---
    scheduler.print_schedule()

    # --- Mark a task complete and reprint ---
    scheduler.mark_task_complete("Luna", "Morning walk")
    scheduler.mark_task_complete("Mochi", "Breakfast feeding")

    print("After completing Luna's morning walk and Mochi's breakfast:\n")
    scheduler.print_schedule()

    # --- Show pending tasks only ---
    pending = scheduler.get_pending_tasks()
    print(f"  {len(pending)} task(s) still pending today.\n")

    # --- Detect conflicts ---
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        print("  ⚠ Scheduling conflicts detected:")
        for t1, t2 in conflicts:
            print(f"    {t1.time} — '{t1.description}' clashes with '{t2.description}'")
        print()


if __name__ == "__main__":
    main()
