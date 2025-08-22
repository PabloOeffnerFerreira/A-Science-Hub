# A Science Hub (ASH)

## Overview

A Science Hub is a desktop application that provides tools for physics, chemistry, biology, geology, and mathematics. It includes calculators, converters, simulators, and reference utilities. The interface is built with PyQt6 and designed for clarity and usability.

## Features

**Biology**

* Codon lookup
* GC content calculator
* Frame translation
* Transcription and translation tools
* Sequence parsing utilities
* Population growth models
* pH calculator
* Osmosis tonicity calculator

**Chemistry**

* Element explorer
* Property grapher
* Isotope notation
* Molar mass calculator
* Molecule library with 3D viewer
* Phase predictor
* Reaction balancer
* Electron shell visualiser

**Electricity**

* Coulomb force calculator
* Electric field visualiser
* Magnetic field calculators and helpers
* RC circuit helper
* Ohm’s law calculator
* Induction tools

**Mechanics**

* Speed and acceleration calculators
* Kinetic energy calculator
* Drag force calculator
* Projectile motion simulator
* Terminal velocity calculator
* Lens and mirror equation solver

**Geology**

* Mineral explorer and identifier
* Radioactive dating
* Half-life calculator
* Plate boundary designer
* Plate velocity calculator

**Mathematics**

* Algebraic calculator
* Function plotter
* Quadratic solver
* Triangle solver
* Vector calculator with 3D visualisation

**Panel Tools**

* Unit converter
* SI prefix combiner and splitter
* Significant figures calculator
* Notation converter
* Scientific constants lookup
* Quantity checker
* Scientific calculator
* Log viewer
* Quick search
* Window manager

## Project Structure

```
core/        # Core logic, data, databases, functions
UI/          # Panels, windows, assets
tools/       # Scientific tools by category
storage/     # User data: logs, results, images, formulas, favourites
documents/   # Documentation and release notes
misc/        # Tests, helpers, templates
```

## Installation

Clone the repository and install the dependencies:

```bash
pip install -r requirements.txt
```

## Running

Start the application with:

```bash
python main.py
```

## Documentation

Full documentation is available in the `documents/` directory:

* `documentation.md` (English)
* `documentation.de.md` (German)
* `documentation.pt-BR.md` (Portuguese)
* Installation guides in multiple languages
* Release notes under `documents/rnotes/`

## Screenshots

#### Main Window
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/5d3b6e45-3164-4e8a-ae39-5598ef29c41d" />

