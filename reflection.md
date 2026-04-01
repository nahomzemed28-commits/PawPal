# PawPal+ Design Reflection

## Phase 1: System Design with UML + AI Support

### Step 1: Understanding the Problem

#### Scenario Analysis
Read the README.md to understand PawPal+ and identify the core actions:

**Three Core Actions a User Should Perform:**
1. 
2. 
3. 

**Document your answers above as you work through the design.**

---

### 1a. Initial Design

**Classes Designed:**
- List the main classes you identified (e.g., Owner, Pet, Task, Scheduler)
- For each class, describe:
  - **Responsibilities**: What does this class manage?
  - **Key Attributes**: What data does it hold?
  - **Key Methods**: What actions can it perform?

*Example format:*
```
Owner
- Responsibility: Represent a pet owner and manage their pets
- Attributes: name, email, owned_pets
- Methods: add_pet(), remove_pet(), view_all_tasks()
```

---

### 1b. Design Changes

**AI Feedback & Refinements:**
- Document any feedback Copilot provided about your initial design
- List changes you made and explain why
- Include any potential logic bottlenecks or improvements identified

---

### 1c. UML Diagram

**Mermaid Class Diagram:**
Paste your Mermaid.js class diagram here to visualize the system architecture.

```mermaid
classDiagram
    direction TD
    
    [Paste your generated Mermaid diagram here]
```

---

## Phase 2: Core Logic Implementation

### 2a. Scheduling Algorithm

The Scheduler uses Python's `sorted()` with a `lambda` key on the task's `time` string:

```python
sorted(all_tasks, key=lambda pair: pair[1].time)
```

Because times are stored in `"HH:MM"` 24-hour format, lexicographic string sorting produces correct chronological order without needing to parse them into datetime objects. This keeps the code simple and fast (O(n log n)).

### 2b. Conflict Detection — Tradeoffs

**Strategy chosen:** Group tasks by their exact `HH:MM` time slot using a `defaultdict`, then flag any slot containing more than one task.

**Tradeoff:** The system only detects *exact time matches* — it does not model task durations or overlapping windows. For example, a 30-minute walk starting at 08:00 and a feeding at 08:15 would not be flagged as a conflict, even though they overlap in real life.

**Why this tradeoff was made:**
- Task durations are not stored in the data model (adding them would require a `duration` field and more complex interval-overlap logic).
- For a basic scheduling assistant, exact-time conflict warnings are the most common and useful signal.
- The implementation returns `ConflictWarning` objects with readable `.message()` strings rather than raising exceptions — it warns without crashing, which is the right behavior for a scheduling tool.

**What would be needed to improve this:**
- Add a `duration_minutes: int` field to `Task`.
- Use an interval-overlap algorithm (check if `[start_a, start_a + dur_a]` overlaps `[start_b, start_b + dur_b]`) instead of exact equality.

### 2c. Recurring Tasks

When `mark_task_complete()` is called via the Scheduler, it checks the task's `frequency`. For `"daily"`, `"weekly"`, and `"monthly"` tasks, it calls `task.next_occurrence()` which uses Python's `timedelta` to compute the next due date and returns a fresh, uncompleted `Task` object. That task is appended to the pet's task list. `"once"` tasks return `None` from `next_occurrence()` and no new task is created.

---

## Phase 3: CLI & Testing
*(To be completed in the next phase)*

### 3a. Demo Script Results

### 3b. Test Coverage

---

## Phase 4: Streamlit UI
*(To be completed in the next phase)*

### 4a. UI Design

### 4b. User Feedback

---

## Final Reflection: AI-Human Collaboration

**What went well:**

**Challenges encountered:**

**Key learnings about AI-assisted development:**

**Tradeoffs discovered:**
