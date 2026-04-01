"""
Full integration check — exercises every function in pawpal_system.py
and verifies every app.py import works cleanly.
Run with: python3 integration_check.py
"""

import os, sys, json, tempfile
from datetime import date, timedelta

# ── Import everything the app uses ────────────────────────────────────────────
from pawpal_system import (
    Task, Pet, Owner, Scheduler, ConflictWarning,
    PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_LOW, PRIORITY_EMOJI,
    _PRIORITY_ORDER,
)

PASS = "  ✅"
FAIL = "  ❌"
errors = []

def check(label, condition, detail=""):
    if condition:
        print(f"{PASS} {label}")
    else:
        print(f"{FAIL} {label}  ← {detail}")
        errors.append(label)

def section(title):
    print(f"\n{'─'*55}\n  {title}\n{'─'*55}")

# ══════════════════════════════════════════════════════════
# 1. TASK
# ══════════════════════════════════════════════════════════
section("1. Task — creation & defaults")
t = Task("Morning walk", "07:00", "daily")
check("description stored",     t.description == "Morning walk")
check("time stored",            t.time == "07:00")
check("frequency stored",       t.frequency == "daily")
check("due_date defaults today",t.due_date == date.today())
check("completed starts False", t.completed is False)
check("default priority medium",t.priority == PRIORITY_MEDIUM)

section("1b. Task — mark_complete / reset")
t.mark_complete()
check("mark_complete → True",   t.completed is True)
t.reset()
check("reset → False",          t.completed is False)

section("1c. Task — next_occurrence")
daily = Task("Walk", "07:00", "daily", due_date=date.today())
nxt = daily.next_occurrence()
check("daily next due = today+1",   nxt.due_date == date.today() + timedelta(days=1))
check("daily next not completed",   nxt.completed is False)
check("daily preserves description",nxt.description == "Walk")
check("daily preserves time",       nxt.time == "07:00")
check("daily preserves priority",   nxt.priority == PRIORITY_MEDIUM)

weekly = Task("Meds", "08:00", "weekly", due_date=date.today(), priority=PRIORITY_HIGH)
nxt_w = weekly.next_occurrence()
check("weekly next due = today+7",  nxt_w.due_date == date.today() + timedelta(days=7))
check("weekly preserves priority",  nxt_w.priority == PRIORITY_HIGH)

monthly = Task("Flea", "09:00", "monthly", due_date=date.today())
nxt_m = monthly.next_occurrence()
check("monthly next due = today+30", nxt_m.due_date == date.today() + timedelta(days=30))

once = Task("Vet", "10:00", "once")
check("once next_occurrence = None", once.next_occurrence() is None)

section("1d. Task — to_dict / from_dict round-trip")
t2 = Task("Evening walk", "18:00", "weekly", priority=PRIORITY_HIGH)
t2.mark_complete()
d = t2.to_dict()
check("to_dict has all keys", all(k in d for k in ["description","time","frequency","due_date","priority","completed"]))
t2r = Task.from_dict(d)
check("from_dict description", t2r.description == t2.description)
check("from_dict time",        t2r.time == t2.time)
check("from_dict frequency",   t2r.frequency == t2.frequency)
check("from_dict priority",    t2r.priority == t2.priority)
check("from_dict completed",   t2r.completed == t2.completed)
check("from_dict due_date",    t2r.due_date == t2.due_date)

# ══════════════════════════════════════════════════════════
# 2. PET
# ══════════════════════════════════════════════════════════
section("2. Pet — creation & task management")
pet = Pet("Luna", "Dog", 3)
check("name stored",    pet.name == "Luna")
check("species stored", pet.species == "Dog")
check("age stored",     pet.age == 3)
check("tasks empty",    pet.tasks == [])

pet.add_task(Task("Walk",    "07:00", "daily"))
pet.add_task(Task("Feeding", "08:00", "daily"))
pet.add_task(Task("Meds",    "09:00", "weekly", priority=PRIORITY_HIGH))
check("add_task count=3", len(pet.tasks) == 3)

pet.tasks[0].mark_complete()
pending = pet.get_pending_tasks()
check("get_pending_tasks excludes completed", len(pending) == 2)
check("get_pending_tasks correct tasks",      all(not t.completed for t in pending))

pet.remove_task("Walk")
check("remove_task reduces count", len(pet.tasks) == 2)
check("remove_task correct item",  all(t.description != "Walk" for t in pet.tasks))

section("2b. Pet — to_dict / from_dict")
pet2 = Pet("Mochi", "Cat", 5)
pet2.add_task(Task("Playtime", "12:00", "daily", priority=PRIORITY_LOW))
pet2.add_task(Task("Flea",     "19:00", "monthly"))
d2 = pet2.to_dict()
check("to_dict has tasks key",    "tasks" in d2)
check("to_dict task count",       len(d2["tasks"]) == 2)
pet2r = Pet.from_dict(d2)
check("from_dict name",           pet2r.name == "Mochi")
check("from_dict task count",     len(pet2r.tasks) == 2)
check("from_dict task priority",  pet2r.tasks[0].priority == PRIORITY_LOW)

# ══════════════════════════════════════════════════════════
# 3. OWNER
# ══════════════════════════════════════════════════════════
section("3. Owner — creation & pet management")
owner = Owner("Nahom", "nahom@test.com")
check("name stored",  owner.name == "Nahom")
check("email stored", owner.email == "nahom@test.com")
check("no pets",      owner.owned_pets == [])

luna  = Pet("Luna",  "Dog", 3)
mochi = Pet("Mochi", "Cat", 5)
luna.add_task(Task("Walk",       "07:00", "daily",  priority=PRIORITY_MEDIUM))
luna.add_task(Task("Meds",       "08:00", "weekly", priority=PRIORITY_HIGH))
mochi.add_task(Task("Feeding",   "08:00", "daily",  priority=PRIORITY_HIGH))
mochi.add_task(Task("Playtime",  "12:00", "daily",  priority=PRIORITY_LOW))
owner.add_pet(luna)
owner.add_pet(mochi)
check("add_pet count=2",    len(owner.owned_pets) == 2)

all_tasks = owner.get_all_tasks()
check("get_all_tasks count=4", len(all_tasks) == 4)
check("get_all_tasks tuples",  all(isinstance(p, Pet) and isinstance(t, Task) for p,t in all_tasks))

owner.remove_pet("Mochi")
check("remove_pet count=1", len(owner.owned_pets) == 1)
check("remove_pet correct", owner.owned_pets[0].name == "Luna")
owner.add_pet(mochi)  # re-add for remaining tests

# ══════════════════════════════════════════════════════════
# 4. SCHEDULER — sorting & filtering
# ══════════════════════════════════════════════════════════
section("4. Scheduler — sorting")
scheduler = Scheduler(owner)
schedule = scheduler.get_todays_schedule()
check("schedule returns 4 items", len(schedule) == 4)

# Priority order: High first (Meds 08:00 HIGH, Feeding 08:00 HIGH), then Medium (Walk 07:00), then Low (Playtime 12:00)
priorities = [t.priority for _, t in schedule]
hi_indices  = [i for i,p in enumerate(priorities) if p == PRIORITY_HIGH]
lo_indices  = [i for i,p in enumerate(priorities) if p == PRIORITY_LOW]
check("high tasks before low tasks", max(hi_indices) < min(lo_indices))

# Within same priority, time should be ascending
high_tasks = [(p,t) for p,t in schedule if t.priority == PRIORITY_HIGH]
high_times = [t.time for _,t in high_tasks]
check("same-priority tasks time-sorted", high_times == sorted(high_times))

section("4b. Scheduler — filtering")
luna_tasks = scheduler.filter_by_pet("Luna")
check("filter_by_pet Luna count=2",    len(luna_tasks) == 2)
check("filter_by_pet all Luna",        all(p.name == "Luna" for p,_ in luna_tasks))

luna_ci = scheduler.filter_by_pet("luna")
check("filter_by_pet case-insensitive", len(luna_ci) == 2)

pending_all = scheduler.get_pending_tasks()
check("get_pending_tasks all pending", len(pending_all) == 4)

done_tasks = scheduler.filter_by_status(completed=True)
check("filter_by_status done=0", len(done_tasks) == 0)

weekly_tasks = scheduler.filter_by_frequency("weekly")
check("filter_by_frequency weekly=1", len(weekly_tasks) == 1)
check("filter_by_frequency correct",  weekly_tasks[0][1].description == "Meds")

high_tasks2 = scheduler.filter_by_priority(PRIORITY_HIGH)
check("filter_by_priority high=2",    len(high_tasks2) == 2)

low_tasks = scheduler.filter_by_priority(PRIORITY_LOW)
check("filter_by_priority low=1",     len(low_tasks) == 1)

# ══════════════════════════════════════════════════════════
# 5. SCHEDULER — mark_task_complete + recurrence
# ══════════════════════════════════════════════════════════
section("5. Scheduler — mark_task_complete + recurrence")
result_ok = scheduler.mark_task_complete("Luna", "Walk")
check("mark_complete returns True",        result_ok is True)
check("task is now complete",              luna.tasks[0].completed is True)
check("daily recurrence appended",        len(luna.tasks) == 3)
check("new task not completed",           luna.tasks[-1].completed is False)
check("new task due tomorrow",            luna.tasks[-1].due_date == date.today() + timedelta(days=1))

# Pending should now be 3 (one done)
pending_now = scheduler.get_pending_tasks()
check("pending count after complete=4",   len(pending_now) == 4)  # Walk done, Walk-next added

done_now = scheduler.filter_by_status(completed=True)
check("done count after complete=1",      len(done_now) == 1)

result_bad_pet  = scheduler.mark_task_complete("Ghost", "Walk")
result_bad_task = scheduler.mark_task_complete("Luna",  "Nonexistent")
check("unknown pet returns False",         result_bad_pet  is False)
check("unknown task returns False",        result_bad_task is False)

section("5b. once task does not recur")
mochi.add_task(Task("Vet", "10:00", "once"))
before = len(mochi.tasks)
scheduler.mark_task_complete("Mochi", "Vet")
check("once task no new occurrence", len(mochi.tasks) == before)
check("once task marked complete",   mochi.tasks[-1].completed is True)

# ══════════════════════════════════════════════════════════
# 6. CONFLICT DETECTION
# ══════════════════════════════════════════════════════════
section("6. Conflict detection")
# Luna: Walk(done,07:00), Meds(08:00 HIGH), Walk-next(07:00 pending)
# Mochi: Feeding(08:00 HIGH), Playtime(12:00), Vet(done,10:00)
conflicts = scheduler.detect_conflicts()
conflict_times = {w.time for w in conflicts}
check("conflict at 08:00 detected",  "08:00" in conflict_times)
check("conflict at 07:00 detected",  "07:00" in conflict_times)  # original+recurring Walk
check("all warnings have message",   all(len(w.message()) > 0 for w in conflicts))
check("message contains time",       all(w.time in w.message() for w in conflicts))

# No conflicts when all times are distinct
solo_owner = Owner("Solo", "s@s.com")
solo_pet = Pet("Solo", "Dog", 1)
solo_pet.add_task(Task("A", "07:00", "once"))
solo_pet.add_task(Task("B", "08:00", "once"))
solo_pet.add_task(Task("C", "09:00", "once"))
solo_owner.add_pet(solo_pet)
solo_sched = Scheduler(solo_owner)
check("no conflicts when times distinct", solo_sched.detect_conflicts() == [])

# ══════════════════════════════════════════════════════════
# 7. SLOT SUGGESTER
# ══════════════════════════════════════════════════════════
section("7. Slot suggester")
slot = scheduler.next_available_slot(after="06:00", step_minutes=30)
check("next_available_slot returns string", isinstance(slot, str))
check("next_available_slot HH:MM format",  len(slot) == 5 and slot[2] == ":")

occupied = {t.time for _, t in scheduler.get_todays_schedule()}
check("next_available_slot not occupied", slot not in occupied)

# After a fully occupied stretch
busy_owner = Owner("Busy", "b@b.com")
busy_pet = Pet("Busy", "Dog", 1)
for h in range(7, 12):
    busy_pet.add_task(Task(f"Task{h}", f"{h:02d}:00", "once"))
busy_owner.add_pet(busy_pet)
busy_sched = Scheduler(busy_owner)
next_slot = busy_sched.next_available_slot(after="06:00", step_minutes=60)
check("skips all occupied hours", next_slot == "12:00")

suggestions = scheduler.suggest_slots(count=5, step_minutes=15)
check("suggest_slots count=5",           len(suggestions) == 5)
check("suggest_slots all unique",        len(suggestions) == len(set(suggestions)))
check("suggest_slots none occupied",     all(s not in occupied for s in suggestions))

# ══════════════════════════════════════════════════════════
# 8. JSON PERSISTENCE
# ══════════════════════════════════════════════════════════
section("8. JSON persistence — Owner.save_to_json / load_from_json")
with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
    tmp_path = f.name

try:
    owner.save_to_json(tmp_path)
    check("file created",           os.path.exists(tmp_path))

    raw = json.loads(open(tmp_path).read())
    check("JSON has name key",      "name" in raw)
    check("JSON has owned_pets",    "owned_pets" in raw)

    reloaded = Owner.load_from_json(tmp_path)
    check("reloaded type Owner",    isinstance(reloaded, Owner))
    check("reloaded name",          reloaded.name == owner.name)
    check("reloaded pet count",     len(reloaded.owned_pets) == len(owner.owned_pets))

    orig_tasks  = sum(len(p.tasks) for p in owner.owned_pets)
    load_tasks  = sum(len(p.tasks) for p in reloaded.owned_pets)
    check("reloaded task count",    orig_tasks == load_tasks)

    orig_pris = [t.priority for p in owner.owned_pets for t in p.tasks]
    load_pris = [t.priority for p in reloaded.owned_pets for t in p.tasks]
    check("reloaded priorities",    orig_pris == load_pris)

    orig_comp = [t.completed for p in owner.owned_pets for t in p.tasks]
    load_comp = [t.completed for p in reloaded.owned_pets for t in p.tasks]
    check("reloaded completed flags", orig_comp == load_comp)

    orig_dates = [str(t.due_date) for p in owner.owned_pets for t in p.tasks]
    load_dates = [str(t.due_date) for p in reloaded.owned_pets for t in p.tasks]
    check("reloaded due_dates",     orig_dates == load_dates)
finally:
    os.unlink(tmp_path)

# Missing file → blank Owner
blank = Owner.load_from_json("/tmp/__no_such_file_pawpal__.json")
check("missing file → blank Owner",     isinstance(blank, Owner))
check("missing file → 0 pets",          len(blank.owned_pets) == 0)

# ══════════════════════════════════════════════════════════
# 9. APP.PY IMPORTS (verify no NameError on import)
# ══════════════════════════════════════════════════════════
section("9. app.py import-level symbols")
import ast
src = open("app.py").read()
tree = ast.parse(src)
imported_names = set()
for node in ast.walk(tree):
    if isinstance(node, ast.ImportFrom) and node.module == "pawpal_system":
        for alias in node.names:
            imported_names.add(alias.asname or alias.name)

required = {"Task","Pet","Owner","Scheduler","PRIORITY_HIGH","PRIORITY_MEDIUM",
            "PRIORITY_LOW","PRIORITY_EMOJI","_PRIORITY_ORDER"}
check("all required names imported from pawpal_system", required.issubset(imported_names),
      detail=f"missing: {required - imported_names}")
check("app.py parses without SyntaxError", True)  # we already parsed it above

# ══════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════
print(f"\n{'═'*55}")
if errors:
    print(f"  ❌ {len(errors)} check(s) FAILED:")
    for e in errors:
        print(f"     • {e}")
else:
    print(f"  ✅ All checks passed — no issues found.")
print(f"{'═'*55}\n")

sys.exit(1 if errors else 0)
