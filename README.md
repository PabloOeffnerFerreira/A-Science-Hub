# A Science Hub (ASH)

A modular offline-first science application for exploration, computation, and visualization.

## Features

- **Main Window**
  - Integrated panels for quick tools and information
  - Simple Tools Panel with mini utilities
  - Welcome Panel with live system and application statistics
  - Session Info Panel with action count and last tool used
  - Window Manager for opening, closing, and managing tool windows
  - Category Sidebar for browsing tools by discipline

- **Tool Categories**
  - Mechanics
  - Electricity
  - Chemistry
  - Biology
  - Geology
  - Math

- **Mini Tools**
  - Unit Converter
  - Notation Converter
  - Decimal Time Converter
  - SI Prefix Combiner/Splitter
  - Significant Figures Tool
  - Scientific Constants Lookup
  - Dimensional Equation Checker
  - Simple Calculator
  - Scientific Quantity Checker

- **System**
  - Offline-first operation
  - Persistent settings and layout storage
  - Live CPU load, RAM, disk usage, uptime, and process memory stats
  - Automatic session start tracking
  - Path management through centralized `paths.py`

## Structure

- `core/` — Core logic, utilities, and data handling
- `UI/` — User interface panels, windows, and styles
- `tools/` — Tool logic, grouped by scientific category
- `storage/` — Logs, images, results, formulas, and favourites
- `documents/` — Documentation and release notes
- `misc/` — Tests and helper scripts

## Requirements

- Python 3.11+
- PyQt6
- psutil


Install dependencies:
```bash
pip install -r requirements.txt
Running
bash
Copy
Edit
python main.py
```
Current Status
Stage: Alpha I

Version: Pre-release

Build: dev

Tools functional with visual integration

Window Manager fully operational

Sidebar functional visually, tool launching integration planned