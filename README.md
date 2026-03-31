# PawPal+ 🐾

A smart pet care management system that helps owners keep their furry friends happy and healthy.

## Overview

PawPal+ is an intelligent pet care management application designed to help pet owners manage daily routines including:
- **Feedings** - Track and schedule regular meal times for each pet
- **Walks** - Log exercise and outdoor time
- **Medications** - Set reminders for vital medication schedules
- **Appointments** - Manage vet visits and grooming appointments

The system uses algorithmic logic to organize and prioritize tasks, helping owners stay on top of their pets' care needs.

## Key Features

- Track multiple pets and their individual care requirements
- Organize daily tasks with intelligent scheduling
- Detect scheduling conflicts
- Manage recurring vs. one-time tasks
- View today's tasks prioritized by importance

## Technology Stack

- **Backend**: Python with Object-Oriented Programming (OOP)
- **UI**: Streamlit (modern web dashboard)
- **Testing**: pytest for automated test suites

## Project Structure

```
PawPal/
├── pawpal_system.py      # Core business logic and classes
├── demo.py              # CLI demo script for testing backend
├── test_pawpal.py       # Automated test suite
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── reflection.md       # Design reflection and learnings
```

## Getting Started

### Phase 1: System Design with UML + AI Support
- Design modular system architecture using OOP
- Create UML diagrams to visualize relationships
- Implement class skeletons

### Phase 2: Core Logic Implementation
- Build scheduling algorithms
- Implement conflict detection
- Handle recurring tasks

### Phase 3: CLI Verification
- Create demo script to test system behavior
- Write pytest test suites

### Phase 4: Streamlit UI
- Create modern web dashboard
- Connect to backend logic

## Installation

```bash
pip install -r requirements.txt
```

## License

MIT License
