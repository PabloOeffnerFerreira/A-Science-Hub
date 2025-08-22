# A Science Hub (ASH)

## Overview

A Science Hub is a desktop application that provides tools for physics, chemistry, biology, geology, and mathematics. It includes calculators, converters, simulators, and reference utilities. The interface is built with PyQt6.

## Features

* **Biology**: codon lookup, GC content, frame translation, transcription/translation, sequence tools, population growth, pH calculator, osmosis tonicity
* **Chemistry**: element explorer, property grapher, isotope notation, molar mass, molecule library with 3D viewer, phase predictor, reaction balancer, shell visualiser
* **Electricity**: Coulomb force, electric and magnetic field calculators/visualisers, RC circuit helper, Ohm’s law, induction tools
* **Mechanics**: speed, acceleration, kinetic energy, drag force, projectile motion, terminal velocity, lens/mirror equation
* **Geology**: mineral explorer, mineral identifier, radioactive dating, half-life calculator, plate boundary designer, plate velocity
* **Math**: algebraic calculator, function plotter, quadratic solver, triangle solver, vector calculator
* **Panel Tools**: unit converter, SI prefix combiner/splitter, sig figs, notation converter, constants lookup, quantity checker, scientific calculator, log viewer, quick search, window manager

## Structure

```
core/        # Core logic, data, databases, functions
UI/          # Panels, windows, assets
tools/       # Scientific tools by category
storage/     # User data: logs, results, images, formulas, favourites
documents/   # Documentation and release notes
misc/        # Tests, helpers, templates
```

## Installation

```bash
pip install -r requirements.txt
```

## Running

```bash
python main.py
```
