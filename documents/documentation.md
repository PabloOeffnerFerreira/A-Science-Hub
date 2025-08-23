# A Science Hub (ASH) – Documentation

> Documentation started: 22 Aug 2025  
> Author: Pablo Oeffner Ferreira  
> Scope: Document every tool, panel, and feature in ASH (user + developer oriented)  
> Version: Draft v0.1

---

## 0) How to Use This Documentation
Each tool is described using a consistent template:

**Name:** …  
**Category:** Biology | Chemistry | Electricity | Mechanics | Geology | Math | Panel Tools  
**Version:** vX.Y (YYYY-MM-DD)  

**Purpose**  
Short explanation of what the tool does and when to use it.  

**Inputs**  
- Input 1 (unit: …, valid ranges …)  
- Input 2 …  

**Outputs**  
- Main result(s) with unit  
- Any visualizations, plots, or exports  

**UI & Interaction**  
Main widgets, fields, and buttons.  

**Algorithm / Equations**  
- Formula(s) with symbols defined  
- Notes about methods, libraries used  

**Units & Conversion**  
- Which unit categories are supported  
- Internal base units (SI) and exceptions  

**Edge Cases & Validation**  
- Handling of invalid/empty input, division by zero, etc.  

**Data Sources**  
- JSON/DB files accessed (e.g. ptable.json, reactions.db)  

**Logging & Export**  
- What gets logged (values, plots, results)  
- Storage path conventions  

**Chaining**  
- Whether the tool’s outputs can be used by others (chain mode ready?)  

**Tests**  
- Notes on test coverage (or reference to files in `misc/tests/`)  

**Known Limitations / TODO**  
Future improvements or open issues.

---

## 1) Platform Overview

### Architecture (high-level)
- **core/** → shared logic, data, registries, loaders  
- **tools/** → domain-specific tools (biology, chemistry, …)  
- **UI/** → PyQt6 windows, panels, layouts, assets  
- **storage/** → user logs, results, favourites, images, formulas  
- **documents/** → docs and release notes (multi-language)  
- **misc/** → helpers, templates, and tests  

### Key Features
- **Tool auto-registration**: dropping a `*.py` file into the correct folder adds it to ASH automatically.  
- **Window Manager**: list/open/close tools, quicksearch overlay, session info.  
- **Export system**: plots/images/data stored under `storage/results/` with timestamped filenames.  
- **Logging**: all actions (tool launches, conversions, calculations) recorded in `storage/logs/`.  

---
The main window
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/5d3b6e45-3164-4e8a-ae39-5598ef29c41d" />
---

### Panel Tool: Unit Converter
**Category:** Panel Tools  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Convert numerical values between units across many scientific categories. Handles both linear (factor-based) and non-linear (formula-based) conversions.  

**Inputs**  
- **Category** (Length, Mass, Time, Temperature, …)  
- **From Unit** (e.g. m, kg, J, °C, …)  
- **To Unit** (e.g. ft, lb, cal, °F, …)  
- **Value** (float; decimal separator “.”, commas auto-replaced)  

**Outputs**  
- Converted value in the target unit  
- Optional log entry in `storage/logs/`  

**UI & Interaction**  
- Dropdown for category  
- Dropdowns for from-unit and to-unit  
- Input field for value  
- Result field displays conversion  

**Algorithm / Equations**  
- Linear categories: `result = value * factor[from] / factor[to]`  
- Temperature: handled as special case with formulas:  
  - `K = °C + 273.15`  
  - `K = (°F − 32) × 5/9 + 273.15`  
  - Reverse formulas for °C and °F  

**Units & Conversion**  
Categories and units supported (as of v1.0):

- **Length**: m, mile, yard, foot, inch, nautical mile, angstrom, light year, astronomical unit, parsec  
- **Mass**: g, kg, tonne, lb, oz, stone, atomic mass unit, solar mass, earth mass  
- **Time**: s, min, h, day, week, month, year, century  
- **Temperature**: C, K, F  
- **Area**: m², hectare, acre, ft², in², mi²  
- **Volume**: m³, L, cup (US), tbsp (US), tsp (US), gal (US), qt (US), pt (US), ft³, in³  
- **Speed**: m/s, km/h, mph, knot, ft/s, c (speed of light)  
- **Pressure**: Pa, bar, atm, mmHg, torr, psi, mbar  
- **Energy**: J, cal, kcal, Wh, kWh, eV, BTU, ft-lb  
- **Power**: W, hp, ft-lb/s, BTU/h  
- **Electric Charge**: C, Ah, e (elementary charge)  
- **Electric Potential**: V  
- **Electric Current**: A  
- **Frequency**: Hz, rpm  
- **Data Size**: bit, byte  
- **Luminance**: cd/m², nit, stilb, foot-lambert  
- **Force**: N, dyn, lbf, kgf, ozf  
- **Angle**: rad, deg, grad, arcmin, arcsec, revolution  
- **Magnetic Field**: T, G  
- **Illuminance**: lux, ph, foot-candle  
- **Radioactivity**: Bq, Ci, dpm 

**Edge Cases & Validation**  
- Invalid unit → raises ValueError but caught and shown as “Error” in UI  
- Empty fields → clears result  
- Exponent errors (e.g. `m^`) handled with “Missing exponent” message  

**Data Sources**  
- `core/data/units/conversion_data.py` (unit definitions & factors)  
- `core/data/units/si_prefixes.py` (SI prefix multipliers)  

**Logging & Export**  
- Each conversion appended to log  
- No file export (only log + UI result)  

**Chaining**  
- Output values can be consumed by other tools once chain mode is enabled  

**Tests**  
- Conversion correctness verified manually (esp. °C↔K↔°F)  
- Potential to add automated tests under `misc/tests/`  

**Known Limitations / TODO**  
- Add logarithmic scales (pH, dB) as special cases  
- Add pretty-print symbols (°C, °F) in UI instead of plain “C”, “F”  

---
### Panel Tool: Simple Calculator
**Category:** Panel Tools  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Evaluate mathematical expressions with support for variables, assignments, and common math functions/constants. Provides a lightweight alternative to the full scientific calculator.

**Inputs**  
- Expression (string):  
  - Plain math (e.g. `2+3`, `3*sin(pi/6)`)  
  - Assignments (e.g. `a=2`, `b=3*a`)  

**Outputs**  
- Numerical result displayed in the output field  
- Stored variables shown as removable chips  
- Last result also stored as `ans`  

**UI & Interaction**  
- **Input field** for expression or assignment  
- **Reset Vars** button clears all stored variables  
- **Output field** shows evaluation result  
- **Variable chips list** shows all defined variables, each with a remove button  

**Algorithm / Evaluation**  
- Evaluations handled by `SafeEvaluator` class:  
  - Wraps Python `eval` with restricted environment (`math` module only, no builtins):contentReference[oaicite:2]{index=2}  
  - Supports math functions (e.g. `sin`, `cos`, `sqrt`), constants (`pi`, `e`)  
  - Supports variable storage via assignment (`x=...`)  
  - `ans` variable stores the last evaluated result  
- On every keystroke, input is scheduled for re-evaluation after 200 ms debounce:contentReference[oaicite:3]{index=3}  

**Units & Conversion**  
- Purely numeric; no unit support (SI prefix/units handled in other tools)  

**Edge Cases & Validation**  
- Empty expression → clears output  
- Invalid expressions → result field is cleared  
- Non-numeric results → shown as raw string  

**Data Sources**  
- Uses Python `math` module for functions and constants  
- No external data files required  

**Logging & Export**  
- No log or file export (local session only)  

**Chaining**  
- Variables can be reused across calculations in the same session  
- Results not exported to other tools yet (future chain mode candidate)  

**Tests**  
- Manual checks for arithmetic, trig, assignments, and `ans` reuse  
- No automated tests yet  

**Known Limitations / TODO**  
- No unit handling (by design)  
- No support for complex numbers  
- Only one-line expressions (no multi-line history)  
- Could add optional persistent storage of variables across sessions  

---
### Panel Tool: Quantity Checker
**Category:** Panel Tools  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Lookup and verify physical quantities, their symbols, and their associated SI units depending on regional conventions (EU, UK/US, BR). Useful for students and professionals who need to cross-check scientific notation and units.

**Inputs**  
- **Region**: select convention set (EU, UK/US, BR)  
- **Search Mode**: choose how to search (Quantity name, Q symbol, Unit symbol)  
- **Selector**: dropdown list of items depending on chosen mode  

**Outputs**  
- **Q.Name**: full English name of the quantity (e.g., “Force”)  
- **Q.Symbol**: standardized symbol depending on region (e.g., `F`)  
- **U.Name**: SI unit name (e.g., “newton”)  
- **U.Symbol**: SI unit symbol (e.g., `N`)  

**UI & Interaction**  
- Three dropdowns: region, search mode, selector list  
- Four read-only fields displaying the resolved information  
- Values update dynamically when region, mode, or selection changes  

**Algorithm / Data Handling**  
- Loads definitions from `quantities.json` (via `quantities.py`):contentReference[oaicite:3]{index=3}  
- Maintains indexes for fast lookup: by quantity name, by Q symbol, by unit symbol  
- Backend (`quantity_checker.py`) provides:
  - `regions()` → available region sets  
  - `options_for(region, mode)` → items for selector list  
  - `describe(region, mode, key)` → returns dictionary of {q_name, q_sym, u_name, u_sym}:contentReference[oaicite:4]{index=4}  

**Units & Conversion**  
- Uses canonical SI unit names and symbols stored in data files  
- Region-specific Q symbols (e.g., “l” vs “L” for litre) 
-  
**Quantities Supported**  
(All regions: EU, UK/US, BR — Q symbols differ by region)

- **Length** — unit: metre (m), Q symbol: l  
- **Mass** — unit: kilogram (kg), Q symbol: m  
- **Time** — unit: second (s), Q symbol: t  
- **Electric current** — unit: ampere (A), Q symbol: I  
- **Thermodynamic temperature** — unit: kelvin (K), Q symbol: T  
- **Amount of substance** — unit: mole (mol), Q symbol: n  
- **Luminous intensity** — unit: candela (cd), Q symbol: Iᵥ  
- **Electric potential difference** — unit: volt (V), Q symbol:  
  - EU: U  
  - UK/US: V  
  - BR: v  
- **Electric charge** — unit: coulomb (C), Q symbol: Q  
- **Magnetic flux density** — unit: tesla (T), Q symbol: B  
- **Magnetic field strength** — unit: ampere per metre (A/m), Q symbol: H  
- **Electrical resistance** — unit: ohm (Ω), Q symbol: R  
- **Capacitance** — unit: farad (F), Q symbol: C  
- **Inductance** — unit: henry (H), Q symbol: L  
- **Power** — unit: watt (W), Q symbol: P  
- **Energy** — unit: joule (J), Q symbol: E  
- **Work** — unit: joule (J), Q symbol: W  
- **Force** — unit: newton (N), Q symbol: F  
- **Pressure** — unit: pascal (Pa), Q symbol: p  
- **Frequency** — unit: hertz (Hz), Q symbol: f

**Edge Cases & Validation**  
- Empty selection clears output fields  
- Unknown key returns `None` → clears output gracefully  

**Data Sources**  
- `core/data/quantities.json` (path from `QUANTITIES_JSON_PATH`):contentReference[oaicite:5]{index=5}  
- Structured as array of objects: names, unit_name, unit_symbol, region-specific Q symbols  

**Logging & Export**  
- No logs or exports (local lookup only)  

**Chaining**  
- Provides validated unit/quantity metadata, potentially useful for chain mode in the future (e.g., feeding correct symbols into calculators)  

**Tests**  
- Manual tests: verify correctness of names/symbols across regions  
- No automated tests yet  

**Known Limitations / TODO**  
- Currently limited to three regions (EU, UK/US, BR)  
- Planned: move **region selector** into global Settings panel for consistency (instead of per-tool dropdown)  
- Could expand JSON with additional languages or extended unit systems  

---
### Panel Tool: Significant Figures
**Category:** Panel Tools  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Count the number of significant figures in a number and round a number to a specified number of significant figures.  

**Inputs**  
- **Value**: string-form number (supports scientific notation, decimals, leading/trailing zeros, etc.)  
  - Examples: `0.00340`, `1.20e3`, `-45.00`, `.056`  
- **Sig figs**: dropdown choice  
  - `auto` → use the number’s own significant figure count  
  - 1–12 → manual override  

**Outputs**  
- **Count**: number of significant figures detected in the input  
- **Rounded**: the value rounded to the chosen number of significant figures  

**UI & Interaction**  
- Value input field (editable)  
- Sig figs dropdown (`auto`, 1–12)  
- Read-only outputs for Count and Rounded  
- Updates triggered live when typing or when changing dropdown  

**Algorithm / Implementation**  
- `count_sigfigs(s)`:contentReference[oaicite:2]{index=2}:  
  - Normalizes string (removes `+`, handles negatives and decimals).  
  - Handles scientific notation by splitting on `e`/`E`.  
  - For decimals: strips leading zeros on left, counts remaining digits.  
  - For integers: strips leading and trailing zeros, counts remaining digits.  
- `round_sigfigs(s, n)`:contentReference[oaicite:3]{index=3}:  
  - Converts to `Decimal`, applies `ROUND_HALF_UP`.  
  - Uses general format (`.{n}g`) to preserve significant figures.  
  - Returns empty string if invalid, `"0"` if input is zero.  

**Units & Conversion**  
- Purely numeric; no unit involvement.  

**Edge Cases & Validation**  
- Empty input → clears outputs  
- Invalid number → outputs empty string  
- Input `0` → correctly yields `0` with sig figs  
- Input with only zeros → treated as zero (0 sig figs)  

**Data Sources**  
- Functions defined in `core/data/functions/sigfigs.py`  
- No external files required  

**Logging & Export**  
- No logs or exports; local interactive usage only  

**Chaining**  
- Possible candidate for chain mode (e.g., rounding outputs before passing to calculators)  

**Tests**  
- Manual examples:  
  - `0.00340` → Count = 3, Rounded (3) = `0.00340`  
  - `1.20e3` → Count = 3, Rounded (2) = `1.2e3`  
- No automated test suite yet  

**Known Limitations / TODO**  
- Does not handle complex numbers  
- Does not preserve exact formatting (e.g., input `1.200` may round to `1.2e3` form)  
- Could expand dropdown beyond 12 sig figs if needed  

---
### Panel Tool: Notation Converter
**Category:** Panel Tools  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Convert numbers between standard decimal notation and scientific notation, with optional control over significant digits.

**Inputs**  
- **Decimal input**: e.g., `12345.678`, `0.00123`  
- **Scientific input**: e.g., `1.2345678e+4`, `1.23e-3`  
- **Sig digits dropdown**:  
  - `auto` → keeps all available digits  
  - `1–15` → rounds result to selected significant digits  

**Outputs**  
- **→ Decimal**: number in plain decimal notation  
- **→ Scientific**: number in scientific notation  

**UI & Interaction**  
- Two input fields: Decimal and Scientific (linked)  
- Two output fields: show conversion results  
- Sig digits dropdown controls rounding  
- Typing in Decimal updates both outputs; typing in Scientific updates both outputs  
- Auto-detection of active field ensures consistency  

**Algorithm / Implementation**  
- Backend conversion handled by `convert(input, sig_digits)` function (in `notation_converter.py`)  
- Supports rounding via significant digits parameter  
- If input invalid or empty → outputs cleared  
- Active source (`dec` or `sci`) remembered so digit changes reapply correctly:contentReference[oaicite:1]{index=1}  

**Units & Conversion**  
- Purely numeric; no physical units involved  

**Edge Cases & Validation**  
- Empty string → clears outputs  
- Invalid string → clears outputs  
- Extreme values → handled gracefully via scientific notation formatting  
- Rounding set to `auto` preserves original precision  

**Data Sources**  
- Internal function only, no external data files  

**Logging & Export**  
- No logs or file exports  

**Chaining**  
- Potential use in chain mode (feeding cleaned numeric values into calculators)  

**Tests**  
- Example 1: Decimal `12345.678` → Scientific `1.2345678e+4`  
- Example 2: Scientific `1.23e-3` → Decimal `0.00123`  
- Example 3: Decimal `12345.678` + Sig digits = 3 → Scientific `1.23e+4`  

**Known Limitations / TODO**  
- Rounding may not preserve formatting style exactly (e.g., may switch to exponential form sooner than expected)  
- Dropdown max = 15 significant digits; could be expanded  
- Could add “engineering notation” mode (exponents multiple of 3) in future  

---

### Panel Tool: Scientific Constants Lookup
**Category:** Panel Tools  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Browse, search, and reference key scientific constants grouped into categories. Displays value, unit, description, and whether the constant is defined exactly or experimentally determined.

**Inputs**  
- **Category**: dropdown list of constant groups  
- **Constant**: dropdown list of constants in the selected category  

**Outputs**  
- **Value**: numerical value (formatted to ~12 significant digits)  
- **Unit**: SI unit (or dimensionless if applicable)  
- **About**: description text, includes “Exact: Yes/No” indicator  

**UI & Interaction**  
- Two dropdowns (Category, Constant)  
- Three read-only fields (Value, Unit, About)  
- Category switch automatically reloads the Constant dropdown  

**Algorithm / Implementation**  
- Categories and constants loaded from `constants_data`:contentReference[oaicite:4]{index=4}  
- `list_categories()` → returns available categories:contentReference[oaicite:5]{index=5}  
- `list_constants(cat)` → returns all constants in a category:contentReference[oaicite:6]{index=6}  
- `get(cat, name)` → returns full record with metadata:contentReference[oaicite:7]{index=7}  

**Units & Conversion**  
- Constants stored in SI units (e.g., m/s, J·s, Pa)  
- Some are dimensionless (e.g., α, α⁻¹)  

**Constants Supported**

- **Fundamental Constants**  
  - Speed of light (c) = 2.99792458e8 m/s (exact)  
  - Planck constant (h) = 6.62607015e-34 J·s (exact)  
  - Reduced Planck constant (ħ) = 1.054571817e-34 J·s (exact)  
  - Elementary charge (e) = 1.602176634e-19 C (exact)  
  - Avogadro constant (N_A) = 6.02214076e23 1/mol (exact)  
  - Boltzmann constant (k_B) = 1.380649e-23 J/K (exact)  
  - Molar gas constant (R) = 8.31446261815324 J/(mol·K) (exact)  
  - Fine-structure constant (α) = 7.2973525693e-3 (CODATA 2018)  
  - Inverse fine-structure constant (α⁻¹) = 137.035999084 (CODATA 2018)  

- **Electromagnetic Constants**  
  - Magnetic constant (μ₀) = 1.25663706212e-6 N/A² (CODATA 2018)  
  - Electric constant (ε₀) = 8.8541878128e-12 F/m (CODATA 2018)  
  - Coulomb constant (k_e) = 8.9875517923e9 N·m²/C² (CODATA 2018)  
  - Josephson constant (K_J) = 483597.8484e9 Hz/V (exact)  
  - von Klitzing constant (R_K) = 25812.80745 Ω (exact)  

- **Thermodynamic Constants**  
  - Stefan–Boltzmann constant (σ) = 5.670374419e-8 W/(m²·K⁴) (exact)  
  - Wien displacement constant (b) = 2.897771955e-3 m·K (CODATA 2018)  

- **Particle Masses**  
  - Electron mass (m_e) = 9.1093837015e-31 kg (CODATA 2018)  
  - Proton mass (m_p) = 1.67262192369e-27 kg (CODATA 2018)  
  - Neutron mass (m_n) = 1.67492749804e-27 kg (CODATA 2018)  
  - Muon mass (m_μ) = 1.883531627e-28 kg (CODATA 2018)  
  - Tau mass (m_τ) = 3.16754e-27 kg (CODATA 2018)  

- **Quantum Constants**  
  - Magnetic flux quantum (Φ₀) = 2.067833848e-15 Wb (CODATA 2018)  
  - Conductance quantum (G₀) = 7.748091729e-5 S (CODATA 2018)  

- **Astronomical/Standards**  
  - Standard acceleration of gravity (g₀) = 9.80665 m/s² (exact)  
  - Standard atmosphere (atm) = 101325 Pa (exact)  

**Edge Cases & Validation**  
- If no constant selected, clears outputs  
- Handles both exact and approximate constants  

**Data Sources**  
- `core/data/databases/constants_data.py` → static dictionary of constants:contentReference[oaicite:8]{index=8}  

**Logging & Export**  
- No logs or export features  

**Chaining**  
- Could supply constant values directly to calculators in chain mode  

**Tests**  
- Manual checks: verifying values match CODATA 2018  
- No automated tests yet  

**Known Limitations / TODO**  
- Constants fixed to CODATA 2018; future update might refresh values  
- Could add search by symbol (currently only by name)  
- Could expand categories (astronomy, material properties, etc.)  

---

### Panel Tool: SI Prefix Combiner / Splitter
**Category:** Panel Tools  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Convert between SI-prefixed units by combining or splitting values into a new prefix and base unit. Displays both the converted value and the equivalent base value.

**Inputs**  
- **Value (numeric)**: number to convert (validated, supports scientific notation)  
- **Input Prefix**: one of standard SI prefixes (Y, Z, E, P, T, G, M, k, h, da, d, c, m, μ, n, p, f, a, z, y, or none):contentReference[oaicite:3]{index=3}  
- **Unit**: base SI unit (collected via `collect_si_units()`)  
- **Output Prefix**: target prefix  

**Outputs**  
- **Output Value**: numeric value expressed with the target prefix  
- **Base Value**: numeric value expressed in the unprefixed base unit  

**UI & Interaction**  
- Input row: Value, Prefix dropdown, Unit dropdown  
- Output row: Result field, Prefix dropdown  
- Base Value: read-only field showing expanded SI form  
- Live updates when any input changes  

**Algorithm / Implementation**  
- Core function: `combine_split(value, in_prefix, in_unit, out_prefix)`:contentReference[oaicite:4]{index=4}  
  - Calls `si_prefix_tools.compute_combined_and_base()`  
  - Returns both converted value (to target prefix) and equivalent base value  
- SI prefixes defined in `si_prefixes.py`:contentReference[oaicite:5]{index=5}  

**Units & Conversion**  
- SI prefix factors:  
  - Y = 1e24, Z = 1e21, E = 1e18, P = 1e15, T = 1e12, G = 1e9, M = 1e6, k = 1e3, h = 1e2, da = 1e1  
  - (no prefix) = 1  
  - d = 1e-1, c = 1e-2, m = 1e-3, μ = 1e-6, n = 1e-9, p = 1e-12, f = 1e-15, a = 1e-18, z = 1e-21, y = 1e-24  

**Edge Cases & Validation**  
- Empty or invalid value → clears outputs  
- Non-numeric input blocked by `QDoubleValidator`  
- If invalid prefix/unit combination → returns `None`  

**Data Sources**  
- Prefix factors: `core/data/units/si_prefixes.py`:contentReference[oaicite:6]{index=6}  
- SI unit collection: `si_prefix_tools.collect_si_units()`  

**Logging & Export**  
- No logs or exports  

**Chaining**  
- Output values can be reused by calculators (potential chain mode integration)  

**Tests**  
- Example 1: Input `1 km`, Output Prefix = `M` → Output `0.001 Mm`, Base `1000 m`  
- Example 2: Input `5 μm`, Output Prefix = `n` → Output `5000 nm`, Base `5e-6 m`  

**Known Limitations / TODO**  
- Unit list restricted to SI base/derived units collected at runtime  
- No support for non-SI units (ft, lb, etc.)  
- Could expand to include binary prefixes (Ki, Mi, Gi) for data size  

---

### Panel Tool: Dimensional Equation Checker
**Category:** Panel Tools  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Verify dimensional consistency of equations by comparing the physical dimensions of left-hand and right-hand expressions. Useful for validating derived formulas in physics and engineering.

**Inputs**  
- **Left**: string expression representing a unit (e.g., `N`)  
- **Right**: string expression representing an equivalent unit combination (e.g., `kg*m/s^2`)  

**Outputs**  
- **Result**:  
  - `OK (dimensions match)` if both sides reduce to same dimension  
  - `Mismatch` if inconsistent  
  - `Error` if parsing fails  
- **Detail**: formatted dimension breakdown for both sides (e.g., `L: M^1 · L^1 · T^-2   R: M^1 · L^1 · T^-2`)  

**UI & Interaction**  
- Two editable fields (Left, Right)  
- Live validation upon typing  
- Read-only status field for result  
- Detail label showing dimensional analysis  

**Algorithm / Implementation**  
- Tokenizes input expressions (`_tokenize`)  
  - Supports symbols, numbers, parentheses, operators (`*`, `/`, `^`)  
  - Rejects invalid characters (e.g., stray `'`) with friendly error  
- Parses into dimension dictionaries (`_parse_expr`, `_parse_term`, `_parse_factor`)  
- Each unit symbol mapped to its base dimensional exponents via `_unit_dims()`  
  - Base dimensions: M (mass), L (length), T (time), I (current), Θ (temperature), N (amount of substance), J (luminous intensity)  
  - Derived/Composite: Hz, N, Pa, J, W, C, V, Ω/ohm, S, F, T, H, Wb, lm, lx  
  - Convenience: min, h as time units  
- Prefix handling:  
  - SI prefixes supported (Y, Z, E, P, T, G, M, k, h, da, d, c, m, μ/u, n, p, f, a, z, y)  
  - Grams (`g`, `mg`, etc.) mapped to base mass (`kg`)  

**Units & Conversion**  
- Full SI base units and many derived units supported  
- Custom composites easily extendable in `_unit_dims()`  

**Edge Cases & Validation**  
- Missing closing parenthesis → “Missing ')'”  
- Stray `^` or no exponent → “Exponent must be a number”  
- Unknown symbol → “Unknown unit: …”  
- Invalid character (e.g., `kg'`) → “Invalid character: '”  
- Empty input → clears output  

**Data Sources**  
- Hardcoded definitions inside `_unit_dims()`  
- No external JSON/DB required  

**Logging & Export**  
- No logs or exports  

**Chaining**  
- Could feed validated dimension results into calculators for automatic formula checks  

**Tests**  
- Example 1: `N` vs `kg*m/s^2` → OK (dimensions match)  
- Example 2: `Pa` vs `N/m^2` → OK  
- Example 3: `J` vs `N*m` → OK  
- Example 4: `W` vs `J/s` → OK  
- Example 5: `V` vs `J/C` → OK  
- Example 6: `N` vs `kg*m/s` → Mismatch  

**Known Limitations / TODO**  
- Limited to SI and a set of derived units  
- No support for non-SI (e.g., pound, foot)  
- No logarithmic or dimensionless “pseudo-units” (like dB)  
- Could add user-extensible unit dictionary  

---

### Panel Tool: Decimal Time Converter
**Category:** Panel Tools  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Convert between standard H:M:S (hours, minutes, seconds) and decimal hours. Useful for calculations where time in fractional hours is required (e.g., speed, work hours, astronomy).

**Inputs**  
- **H:M:S fields**:  
  - Hours (integer or float)  
  - Minutes (0–59, float allowed)  
  - Seconds (0–59, float allowed)  
- **Decimal hours field**:  
  - Value as a float (supports comma `,` or dot `.` as decimal separator)  

**Outputs**  
- From H:M:S → Decimal hours (8 decimal places)  
- From Decimal hours → H, M, S (seconds with 2 decimal places)  

**UI & Interaction**  
- First form: enter hours, minutes, seconds → shows decimal hours  
- Second form: enter decimal hours → shows hours, minutes, seconds  
- Auto-updates live when typing in either direction  

**Algorithm / Implementation**  
- `to_decimal(h, m, s)`:contentReference[oaicite:3]{index=3}:  
  - Normalizes inputs, defaults to 0 if empty  
  - Computes `hours + minutes/60 + seconds/3600` via `hms_to_hours()`:contentReference[oaicite:4]{index=4}  
  - Returns formatted float with 8 decimals  
- `from_decimal(hours)`:contentReference[oaicite:5]{index=5}:  
  - Converts float into H, M, S via `hours_to_hms()`:contentReference[oaicite:6]{index=6}  
  - Returns tuple (h, m, s) with seconds to 2 decimals  
- Extra helpers in `time_tools.py`:  
  - `minutes_to_hours`, `hours_to_minutes`, `seconds_to_hours`, `hours_to_seconds`  
  - `parse_time_string(s)` to flexibly parse inputs like `1h30m` or `1:30:00`  
  - `format_hms(h,m,s)` for display (`compact` or `colon` modes)  

**Units & Conversion**  
- Strictly hours, minutes, seconds ↔ decimal hours  
- No date or timezone handling  

**Edge Cases & Validation**  
- Invalid input → clears outputs  
- Empty fields treated as 0  
- Seconds rounded to 2 decimal places on reverse conversion  

**Data Sources**  
- Internal functions only; no external JSON/DB  

**Logging & Export**  
- No logs or exports  

**Chaining**  
- Decimal output can feed into calculators (e.g., speed = distance/time)  

**Tests**  
- Example 1: H:M:S = `1:30:00` → Decimal = `1.50000000`  
- Example 2: H:M:S = `0:45:30` → Decimal ≈ `0.75833333`  
- Example 3: Decimal = `2.75` → H:M:S = `2 h 45 m 0.00 s`  

**Known Limitations / TODO**  
- Limited to ≤ 24h (no day handling)  
- No negative times currently supported  
- Could add “colon” formatting mode in UI (HH:MM:SS)  

---

### Panel Tool: Welcome Panel
**Category:** Panel Tools  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Provides the landing page when the app starts. Displays a welcome message, app metadata, session info, and live system statistics.

**Inputs**  
- No direct user input (read-only panel)  

**Outputs**  
- Welcome message  
- **App Info** (title, version, build, language, region, theme, stage, session start, last tool opened)  
- **System Info** (OS, Python version, CPU load, RAM, disk, uptime, process memory)  

**UI & Interaction**  
- Static label: “Welcome to A Science Hub — your science hub for exploration and discovery.”  
- Divider line  
- Scrollable stats grid (grouped sections: App, System)  
- Auto-refresh every 1.5 seconds  

**Algorithm / Implementation**  
- Collects data via `get_welcome_stats()`:contentReference[oaicite:1]{index=1}:  
  - **App** section from `get_app_snapshot()`:  
    - Title  
    - Version  
    - Build  
    - Language  
    - Region  
    - Theme  
    - Stage  
    - Session start (formatted local time)  
    - Last tool opened  
  - **System** section from `get_system_snapshot()`:  
    - OS  
    - Python version  
    - CPU count  
    - CPU load %  
    - RAM total  
    - Disk total (C:)  
    - Disk free (C:)  
    - Uptime (human-readable)  
    - Process memory usage  
- Values displayed as **StatChip** widgets (styled mini-panels with key + value):contentReference[oaicite:2]{index=2}  

**Units & Conversion**  
- Memory and disk formatted with `human_bytes()` (bytes → KB, MB, GB):contentReference[oaicite:3]{index=3}  

**Edge Cases & Validation**  
- If no stats available → empty panel  
- Invalid session time → shown as raw string  
- Missing values default to `"N/A"`  

**Data Sources**  
- `core.data.info.py` for constants (APP_NAME, DEVELOPER, GITHUB_REPO, VERSION, BUILD, STAGE, DESCRIPTION):contentReference[oaicite:4]{index=4}  
- `core.utils.system_info.get_system_snapshot()`  
- `core.utils.app_info.get_app_snapshot()`  
- `core.utils.usage_stats.get_last_tool_opened()`  

**Logging & Export**  
- No logs or exports  

**Chaining**  
- Not applicable  

**Tests**  
- Manual check: stats refresh every 1.5 seconds  
- Verify Last Tool changes after opening a tool  

**Known Limitations / TODO**  
- Currently read-only  
- Could later add clickable shortcuts (GitHub repo, docs, settings)  
- System info limited to local machine (Windows-style disk label “C:”)  

---

### Panel Tool: Log Panel
**Category:** Panel Tools  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Central interface for viewing and managing logs generated by ASH tools. Provides filtering, pinning, deletion, and export features.

**Inputs**  
- **Search bar**: text filter (matches timestamp, tool, action, data, tags)  
- **Pinned toggle**: button to show all or only pinned logs  
- **Context menu actions** (per log): Pin/Unpin, Delete, Copy Action, Copy Data  
- **Dropdown menu actions**:  
  - Clear All (ignore pinned)  
  - Clear All (including pinned)  
  - Export as CSV  
  - Export as TXT  

**Outputs**  
- Table of log entries with columns: Pin, Time, Tool, Action, Data, Tags  
- Exported files:  
  - `logs_export.csv` → structured CSV with columns (time, tool, action, data, tags, pinned)  
  - `logs_export.txt` → plain text with formatted log lines  

**UI & Interaction**  
- Top bar with search, pin filter toggle, and actions dropdown:contentReference[oaicite:5]{index=5}  
- Table widget displays logs; clicking pin column toggles pinned state  
- Right-click menu on table rows provides quick actions (Pin/Unpin, Delete, Copy)  

**Algorithm / Implementation**  
- Backend:  
  - `LogController` manages JSON file `logs.json` in `storage/logs/`:contentReference[oaicite:6]{index=6}  
  - Functional API (`add_log_entry`, `get_logs`, `delete_log`, `pin_log`, `clear_logs`) in `log.py`:contentReference[oaicite:7]{index=7}  
  - Signals: `log_bus.log_added` emitted whenever new entry is added:contentReference[oaicite:8]{index=8}  
  - `log_writer.py` supports writing timestamped JSON files to disk and reading them back:contentReference[oaicite:9]{index=9}  
- Log entries include:  
  - `timestamp`, `tool`, `action`, `data`, `tags`, `pinned`  

**Units & Conversion**  
- Not applicable  

**Edge Cases & Validation**  
- Missing or invalid `logs.json` → handled safely (empty list):contentReference[oaicite:10]{index=10}  
- JSON decode errors → ignored gracefully  
- Pin/unpin state preserved in log file  

**Data Sources**  
- Log file path: `storage/logs/logs.json`  
- Exports: `storage/logs/logs_export.csv` and `logs_export.txt`  

**Logging & Export**  
- Every tool can call `add_log_entry()` to add entries automatically  
- Users can manually export logs from the panel  

**Chaining**  
- Logs are passive; not directly consumable by other tools  

**Tests**  
- Manual test: add logs via tools, check appear in panel  
- Test pin/unpin toggling and persistence  
- Test search filter across tool name, action, and tags  

**Known Limitations / TODO**  
- No advanced filtering (by date range, tag only, etc.)  
- No GUI confirmation dialogs for destructive actions (e.g., clear all)  
- Logs stored in a single JSON file; could grow large over time  
- Potential feature: export/import logs across sessions  

---

### Panel Tool: Window Manager
**Category:** Panel Tools  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Provides a centralized interface to manage all open ASH tool windows. Users can list, focus, minimize, restore, or close windows directly from the panel.

**Inputs**  
- Window selection (row in the table)  
- Button actions: Focus, Minimize, Restore, Close, Close All  

**Outputs**  
- Table of open windows with:  
  - **ID**: unique UUID assigned to each window  
  - **Title**: window title  
  - **State**: current state (`normal`, `focused`, `minimized`)  

**UI & Interaction**:contentReference[oaicite:3]{index=3}  
- Table widget listing open windows (ID, Title, State)  
- Action buttons:  
  - **Focus** → brings selected window to foreground  
  - **Minimize** → minimizes selected window  
  - **Restore** → restores window to normal state  
  - **Close** → closes selected window  
  - **Close All** → closes all windows  
- Auto-refresh triggered on open/close/change events via `bus`  

**Algorithm / Implementation**:contentReference[oaicite:4]{index=4}  
- Backend managed by `WM` class:  
  - `open(title, widget_factory)` → creates new window with UUID, restores geometry from saved settings, emits `bus.opened`  
  - `adopt(title, win)` → registers an existing QWidget into WM  
  - `close(wid)` / `close_all()` → closes windows, emits `bus.closed`  
  - `focus(wid)` → raises window, marks state = focused, emits `bus.changed`  
  - `minimize(wid)` → minimizes window, updates state  
  - `restore(wid)` → shows window normally, raises & activates  
  - `list()` / `list_windows()` → returns current managed windows as dicts `{id, title, state}`  
- Geometry persistence:  
  - Saved to `WM_FILE` under key `wm_layout`  
  - On close: `_save_geometry()` writes x, y, w, h per window  
  - On reopen: `_restore_geometry()` applies last saved size/position  

**Units & Conversion**  
- Not applicable  

**Edge Cases & Validation**  
- If geometry data invalid (negative sizes) → ignored  
- If invalid `wid` passed to functions → safely ignored  
- Windows cleanly unregistered on `destroyed` or `finished` signals  

**Data Sources**  
- Settings file `WM_FILE` (JSON) stores per-window geometry  
- `core.utils.wm_events.bus` for signals (opened, closed, changed)  

**Logging & Export**  
- No logs or exports  

**Chaining**  
- Not applicable  

**Tests**  
- Manual test: open multiple tools, verify list updates  
- Test closing, minimizing, restoring via panel buttons  
- Check geometry persistence across app restarts  

**Known Limitations / TODO**  
- `window_api.py` currently a placeholder:contentReference[oaicite:5]{index=5}  
- No search/filter in window list  
- No ability to rename or group windows  
- Multi-monitor awareness could be improved  

---

### Tool: Molecule Library (PubChem)
**Category:** Chemistry  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Search molecules in PubChem by name, CID, SMILES, InChI, or InChIKey. Displays molecular properties, synonyms, 2D images, and an interactive 3D viewer. Supports saving images and logging queries.

**Inputs**  
- **Query type**: dropdown with options `auto`, `name`, `cid`, `smiles`, `inchi`, `inchikey`  
- **Query string**: free text (e.g., `aspirin`, `2244`, `CC(=O)OC1=CC=CC=C1C(=O)O`, `InChI=...`, `BSYNRYMUTXBXSQ-UHFFFAOYSA-N`)  
- **Buttons**:  
  - **Search** → fetch results from PubChem  
  - **Save Image…** → export molecule PNG to file  
  - **Open 3D…** → launch interactive 3D viewer  

**Outputs**  
- **Matches list**: one or more CIDs returned by PubChem  
- **Molecule details**:  
  - Name (IUPAC or synonym)  
  - CID  
  - PNG preview (scalable)  
  - Properties table (formula, weight, SMILES, InChI, XLogP, H-bond counts, etc.)  
  - Synonyms (up to 25 from PubChem)  

**UI & Interaction**:contentReference[oaicite:1]{index=1}  
- Split view:  
  - **Left** → list of matching CIDs  
  - **Right** → details panel (image, name, properties, buttons)  
- Clicking a CID loads and displays image + properties  
- Save button exports PNG to user-selected path  
- Open 3D launches an embedded `py3Dmol` viewer in a PyQt6 `QWebEngineView`  

**Algorithm / Implementation**  
- `_resolve_cids(kind, term)` queries PubChem REST API (by name/SMILES/InChI/ID)  
- `_properties_for_cid(cid)` fetches molecular data (formula, weight, SMILES, InChI, TPSA, H-bond donors/acceptors, rotatable bonds, synonyms, etc.)  
- `_png_for_cid(cid)` retrieves 2D PNG (large or medium size)  
- `_molblock_3d_for_cid(cid)` attempts to fetch SDF (3D first, fallback 2D)  
- `_molblock_from_smiles(smiles)` generates 3D conformer with RDKit if no PubChem 3D available  
- `Molecule3DViewer` → wrapper dialog embedding `py3Dmol` viewer  

**Units & Conversion**  
- Molecular properties displayed as-is from PubChem (no conversion applied)  

**Edge Cases & Validation**  
- No results → “No results.” message in details panel  
- No image → “No image.” displayed instead of PNG  
- Save attempt with no image → warning shown  
- No 3D data available → “No 3D model available.”  

**Data Sources**  
- PubChem REST API (`pug` endpoints: `/compound/name`, `/compound/cid`, `/compound/smiles`, `/compound/inchi`, `/compound/inchikey`)  
- Properties: Canonical/Isomeric SMILES, InChI, InChIKey, Formula, Masses, TPSA, XLogP, H-bond counts, rotatable bonds, charge, synonyms  

**Logging & Export**  
- Logs actions via `add_log_entry`:  
  - `"Query"` (with query type, string, result count)  
  - `"QueryNoResults"`  
  - `"SaveImage"` (with CID + file path)  
  - `"Open3D"` (with CID + has_smiles flag)  
- PNG images saved to user-selected directory (default: `IMAGES_DIR`)  

**Chaining**  
- CID, SMILES, and molecular properties could be chained to other chemistry tools in future (e.g., Reaction Balancer, Shell Viewer)  

**Tests**  
- Example 1: Query `aspirin` → CID 2244, formula `C9H8O4`, MW ≈ 180.16 g/mol  
- Example 2: Query `2244` → returns aspirin  
- Example 3: Query `BSYNRYMUTXBXSQ-UHFFFAOYSA-N` (InChIKey) → returns aspirin  
- Example 4: Query `CCO` (SMILES) → ethanol  

**Known Limitations / TODO**  
- Requires internet connection (depends on PubChem API)  
- No caching → repeated queries refetch every time  
- 3D viewer may fail if RDKit cannot generate conformer  
- Could add batch search mode (multiple queries at once)  

---

### Tool: Shell Visualiser

**Category:** Chemistry
**Version:** v2.0 (2025-08-22)

**Purpose**
Visualize electron shell structures of atoms in both 2D and 3D. Provides an illustrative view of electrons, shells, and nucleus composition. Useful for teaching atomic structure, ion formation, and general chemistry visualization.

**Inputs**

* **Element Symbol**: text input (e.g., `H`, `He`, `Fe`)
* **Charge**: optional integer (e.g., `+3`, `-2`)

**Outputs**

* 2D schematic of electron shells (electrons as dots, shells as circles, nucleus labeled)
* 3D interactive model with rotating camera, nucleus cluster (protons in red, neutrons in grey), electron rings, and moving electrons
* Status message confirming rendering or saved export

**UI & Interaction**

* Text entry for element symbol and charge
* Buttons:

  * **Draw** → render shells in both 2D and 3D
  * **Export Image** → save snapshot of current tab (2D figure or 3D render)
  * **Start/Stop Animation** → toggle orbiting electrons and rotating camera
* Tabs:

  * **2D View** (matplotlib with navigation toolbar)
  * **3D View** (PyQtGraph OpenGL; shown if available)
* Status label shows rendering info or save path

**Algorithm / Implementation**

* Loads element data via `load_element_data()`
* Electron shells adjusted for ionic charge (`adjust_shells_for_charge`)
* Proton and neutron counts derived from JSON data (`get_protons`, `get_atomic_mass`)
* **2D rendering**: matplotlib circles for shells and electrons, nucleus labeled
* **3D rendering**:

  * Protons and neutrons as shaded spheres clustered in nucleus
  * Shell rings drawn as line plots
  * Electrons as spheres positioned along rings
  * Label rendered above nucleus with formatted ion symbol
  * Optional animation updates electron positions and rotates camera

**Units & Conversion**

* Illustrative only (not to physical scale)

**Edge Cases & Validation**

* Invalid element symbol → warning popup
* Missing shell data → warning popup
* Charge adjustment gracefully handles anions/cations
* If 3D stack unavailable, tool still functions in 2D

**Data Sources**

* Periodic table JSON via `chemistry_utils.load_element_data()`
* Keys used: `shells`, `atomicNumber`, `atomicMass`

**Logging & Export**

* 2D exports via `export_figure()`
* 3D exports via OpenGL framebuffer capture + `imageio`
* Log entries record symbol, charge, shells, and image path

**Chaining**

* Provides shell data and saved images for reuse in teaching tools or chain mode

**Tests**

* `H` → single electron
* `He` → 2 electrons in first shell
* `Ne` → 2 + 8 distribution
* `Fe³⁺` → adjusted electron shells with 3 fewer electrons
* Large-Z atoms scaled automatically to fit view

**Known Limitations / TODO**

* Depends on external JSON database for element data
* 3D visualization requires `pyqtgraph.opengl` (falls back to 2D if unavailable)
* Nucleus distribution randomized (not physically accurate)
* Future work: export SVG, higher-res 3D, or orbital hybridization models

---


### Tool: Element Comparator
**Category:** Chemistry  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Compare properties of up to three elements side by side. Highlights differences visually and supports filtering by property categories. Useful for quickly contrasting atomic, chemical, and physical traits.

**Inputs**  
- **Element selectors**: three dropdowns (editable, auto-filled with periodic table symbols)  
- **Property tabs**: checkboxes grouped into categories (Atomic, Chemical, Physical)  
  - **Select All / Select None** buttons per category  
- **Filter**: text field to search properties by name/description  
- **Compare button**: generates comparison table  

**Outputs**  
- Comparison table:  
  - First column: Property name  
  - Subsequent columns: values for each chosen element  
  - Numeric values formatted to 3 decimals + unit  
  - Highlights:  
    - Largest numeric value → **bold blue**  
    - Smallest numeric value → *italic red*  
    - Non-numeric differing values → italic  

**UI & Interaction**:contentReference[oaicite:1]{index=1}  
- Three element dropdowns  
- Tab widget with categories: Atomic, Chemical, Physical  
- Property checkboxes with tooltips (description)  
- Filter field hides checkboxes dynamically  
- “Compare” button → fills table with selected properties and formatted values  
- Table supports sorting by column  

**Algorithm / Implementation**  
- Element data loaded via `load_element_data()` from `ptable.json`:contentReference[oaicite:2]{index=2}  
- `PROPERTY_METADATA` defines:  
  - Key → Label, Unit, Category, Description, Numeric flag  
- Properties implemented:  
  - **Atomic**:  
    - Atomic Number (protons)  
    - Atomic Mass (u)  
  - **Chemical**:  
    - Electronegativity (Pauling scale)  
    - Type (category, e.g., metal, noble gas)  
    - Oxidation States (list of common states)  
  - **Physical**:  
    - Boiling Point (K)  
    - Melting Point (K)  
    - Density (g/cm³)  
- `_compare()` builds table:  
  - Validates unique elements  
  - Collects checked properties  
  - Formats values with `_fmt()`  
  - Applies highlighting (max/min numeric, differing categorical values)  

**Units & Conversion**  
- Atomic Mass: u  
- Electronegativity: Pauling (dimensionless)  
- Boiling/Melting Point: K  
- Density: g/cm³  

**Edge Cases & Validation**  
- Duplicate elements selected → warning “Select different elements.”  
- Unknown symbol → warning “not found”  
- Missing property value → shown as em-dash `—`  
- Non-numeric lists (oxidation states) → joined string  

**Data Sources**  
- `ptable.json`: periodic table database (symbols, names, atomic number, mass, shells, etc.)  
- `PROPERTY_METADATA` inside tool defines property metadata  

**Logging & Export**  
- No logging or export built-in  

**Chaining**  
- Could integrate with Shell Visualiser or Molecule Library (e.g., compare → visualize shell)  

**Tests**  
- Example 1: Compare H, He, Li → shows differences in atomic mass and properties  
- Example 2: Compare Fe, Cu, Zn → density and boiling point highlighted  
- Example 3: Compare noble gases → oxidation states show italics for differences  

**Known Limitations / TODO**  
- Only 3 elements supported simultaneously  
- Properties limited to metadata keys (AtomicNumber, Mass, Electronegativity, BoilingPoint, MeltingPoint, Density, Type, OxidationStates)  
- No export (CSV/PNG) option yet  
- Could expand metadata to include radii, conductivity, heat capacity, etc.  

---

### Tool: Element Comparator
**Category:** Chemistry  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Compare properties of up to three elements side by side. Highlights differences visually and supports filtering by property categories. Useful for quickly contrasting atomic, chemical, and physical traits.

**Inputs**  
- **Element selectors**: three dropdowns (editable, auto-filled with periodic table symbols)  
- **Property tabs**: checkboxes grouped into categories (Atomic, Chemical, Physical)  
  - **Select All / Select None** buttons per category  
- **Filter**: text field to search properties by name/description  
- **Compare button**: generates comparison table  

**Outputs**  
- Comparison table:  
  - First column: Property name  
  - Subsequent columns: values for each chosen element  
  - Numeric values formatted to 3 decimals + unit  
  - Highlights:  
    - Largest numeric value → **bold blue**  
    - Smallest numeric value → *italic red*  
    - Non-numeric differing values → italic  

**UI & Interaction**:contentReference[oaicite:1]{index=1}  
- Three element dropdowns  
- Tab widget with categories: Atomic, Chemical, Physical  
- Property checkboxes with tooltips (description)  
- Filter field hides checkboxes dynamically  
- “Compare” button → fills table with selected properties and formatted values  
- Table supports sorting by column  

**Algorithm / Implementation**  
- Element data loaded via `load_element_data()` from `ptable.json`:contentReference[oaicite:2]{index=2}  
- `PROPERTY_METADATA` defines:  
  - Key → Label, Unit, Category, Description, Numeric flag  
- Properties implemented:  
  - **Atomic**:  
    - Atomic Number (protons)  
    - Atomic Mass (u)  
  - **Chemical**:  
    - Electronegativity (Pauling scale)  
    - Type (category, e.g., metal, noble gas)  
    - Oxidation States (list of common states)  
  - **Physical**:  
    - Boiling Point (K)  
    - Melting Point (K)  
    - Density (g/cm³)  
- `_compare()` builds table:  
  - Validates unique elements  
  - Collects checked properties  
  - Formats values with `_fmt()`  
  - Applies highlighting (max/min numeric, differing categorical values)  

**Units & Conversion**  
- Atomic Mass: u  
- Electronegativity: Pauling (dimensionless)  
- Boiling/Melting Point: K  
- Density: g/cm³  

**Edge Cases & Validation**  
- Duplicate elements selected → warning “Select different elements.”  
- Unknown symbol → warning “not found”  
- Missing property value → shown as em-dash `—`  
- Non-numeric lists (oxidation states) → joined string  

**Data Sources**  
- `ptable.json`: periodic table database (symbols, names, atomic number, mass, shells, etc.)  
- `PROPERTY_METADATA` inside tool defines property metadata  

**Logging & Export**  
- No logging or export built-in  

**Chaining**  
- Could integrate with Shell Visualiser or Molecule Library (e.g., compare → visualize shell)  

**Tests**  
- Example 1: Compare H, He, Li → shows differences in atomic mass and properties  
- Example 2: Compare Fe, Cu, Zn → density and boiling point highlighted  
- Example 3: Compare noble gases → oxidation states show italics for differences  

**Known Limitations / TODO**  
- Only 3 elements supported simultaneously  
- Properties limited to metadata keys (AtomicNumber, Mass, Electronegativity, BoilingPoint, MeltingPoint, Density, Type, OxidationStates)  
- No export (CSV/PNG) option yet  
- Could expand metadata to include radii, conductivity, heat capacity, etc.  

---

### Tool: Element Viewer
**Category:** Chemistry  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Browse and inspect periodic table elements. Provides quick search, detailed property display, and a favorites system.

**Inputs**  
- **Search box**: free text, matches across name, symbol, number, category, shells, electron configuration, appearance, summary  
- **Favorites checkbox**: toggle between all elements and favorites only  
- **Refresh button**: reloads the element list  
- **List selection**: choose an element to view its details  

**Outputs**  
- **Element details panel**:  
  - Name and Symbol  
  - Atomic Number  
  - Category  
  - Atomic Mass (g/mol)  
  - Shell configuration  
  - Electron configuration  
  - Density (g/cm³)  
  - Melting Point (K)  
  - Boiling Point (K)  
  - Appearance  
  - Summary (text description)  

**UI & Interaction**:contentReference[oaicite:1]{index=1}  
- Top bar: Search, “Show Favorites Only” checkbox, Refresh button  
- Main list: Elements sorted by atomic number, labelled as `"Sym  Name   (Number)"`  
  - Favorites highlighted in **gold** and bold font  
- “Toggle Favorite” button: add/remove selected element from favorites  
- Details panel: shows structured properties in formatted HTML (Consolas font, read-only)  

**Algorithm / Implementation**  
- `load_element_data()` loads element dataset from `ptable.json` (periodic table)  
- `_flatten_elements()` builds searchable element dicts with `"search_blob"` field for efficient filtering  
- Search filter → matches substring in `search_blob`  
- Favorites stored in JSON at `ELEMENT_FAVS_PATH` (if path defined)  
  - `_load_favs()` loads favorites (set of symbols)  
  - `_save_favs()` writes favorites persistently  

**Units & Conversion**  
- Mass: g/mol  
- Density: g/cm³  
- Temperature: K  

**Edge Cases & Validation**  
- No matching elements → clears list and details  
- Missing fields in JSON → displays em-dash `—`  
- No selection → disables favorite toggle action  

**Data Sources**  
- `ptable.json` (element database)  
  - Fields: name, symbol, number, category, atomic_mass, shells, electron_configuration, density, melt, boil, appearance, summary  
- Favorites file: `ELEMENT_FAVS_PATH` (JSON set of element symbols)  

**Logging & Export**  
- No logging or exports  

**Chaining**  
- Not directly chainable, but can feed symbols into other chemistry tools (e.g., Shell Visualiser, Molecule Library)  

**Tests**  
- Example 1: Search `"Fe"` → list shows Iron, details display atomic number 26, density 7.87 g/cm³  
- Example 2: Favorites toggle → shows only starred elements  
- Example 3: Search `"noble gas"` → filters He, Ne, Ar, etc.  

**Known Limitations / TODO**  
- No graphing (see Property Grapher for trends)  
- Favorites tied to single storage path only (no per-user profiles)  
- No export of details to file  
- Could add sorting by property (e.g., by mass, electronegativity)  

---

### Tool: Isotopic Notation
**Category:** Chemistry  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Compute isotopic notation for an element given its symbol and mass number. Displays proton/neutron composition, atomic mass, and natural abundance if available, along with a nucleon pie chart.

**Inputs**  
- **Element Symbol**: string (e.g., `H`, `He`, `Fe`)  
- **Mass Number (A)**: integer  

**Outputs**  
- **Isotopic Notation**: formatted as `Aₛᵧₘ` (e.g., ¹⁴C, ²³⁸U)  
- **Element info**:  
  - Name  
  - Symbol  
  - Atomic Number (Z, protons)  
  - Neutrons (A − Z)  
  - Atomic Mass (u)  
  - Natural Abundance (%) if known  
- **Pie Chart**: showing proton vs neutron composition  
- **Exported Chart**: PNG file saved to disk with timestamped filename  

**UI & Interaction**:contentReference[oaicite:1]{index=1}  
- Two text inputs: element symbol, mass number  
- “Calculate” button → computes info and renders chart  
- “Export Chart” button → saves pie chart (if not already saved)  
- Read-only result box: formatted HTML output (notation, info, path to saved image)  

**Algorithm / Implementation**  
- Loads element dataset via `load_element_data()` (from `ptable.json`)  
- Checks inputs: symbol present, mass number integer, A ≥ Z  
- Finds isotope data in `el["isotopes"]` list if available  
- Computes:  
  - Neutrons = A − Z  
  - Atomic Mass = isotope mass if found, otherwise element’s average mass  
  - Abundance = isotope abundance if found  
- Renders pie chart (protons vs neutrons) with Matplotlib  
- Saves chart via `export_figure()` to `IMAGES_DIR` if available  
- Logs action with `add_log_entry` (tool = Isotopic Notation, action = Compute)  

**Units & Conversion**  
- Atomic Mass: unified atomic mass units (u)  
- Abundance: percentage (formatted to 3 decimals, or “Unknown”)  

**Edge Cases & Validation**  
- Missing symbol → error “Element symbol not found”  
- Non-integer mass number → error “Mass number must be an integer”  
- A < Z → error “Mass number cannot be less than atomic number”  
- Unknown isotope mass → falls back to average atomic mass  
- No abundance data → “Unknown” shown  

**Data Sources**  
- `ptable.json` (element dataset with isotopes if included)  
- `chemistry_utils.load_element_data()` for element lookup  

**Logging & Export**  
- Logs: tool = `"Isotopic Notation"`, action = `"Compute"`, data includes symbol, A, Z, neutrons, image path  
- PNG chart export stored in `IMAGES_DIR` (if defined), else default directory  

**Chaining**  
- Computed isotopic data could be reused in nuclear physics tools or decay calculators  

**Tests**  
- Example 1: Symbol = `C`, A = `14` → 14₍C₎, Z = 6, N = 8, abundance ≈ low, pie chart 6p:8n  
- Example 2: Symbol = `U`, A = `238` → 238₍U₎, Z = 92, N = 146, chart 92p:146n  
- Example 3: Invalid: `H`, A = `0` → error message  

**Known Limitations / TODO**  
- Requires isotope data in JSON for exact masses and abundances  
- Currently 2D pie chart only; could expand to show multiple isotope abundances for same element  
- No direct link to Half-Life Calculator (future chain mode candidate)  

---

### Tool: Molar Mass Calculator
**Category:** Chemistry  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Calculate the molar mass (molecular weight) of a chemical compound from its molecular formula. Supports hydrates and provides a detailed breakdown per element.

**Inputs**  
- **Formula**: molecular formula string (e.g., `H2O`, `C6H12O6`, `CuSO4·5H2O`)  

**Outputs**  
- Text report with:  
  - Each element’s contribution → symbol, name, count, subtotal in g/mol  
  - List of unknown/massless elements (if any)  
  - **Total Molecular Weight** in g/mol  

**UI & Interaction**:contentReference[oaicite:1]{index=1}  
- Text field for formula entry (with placeholder examples)  
- Buttons: **Calculate**, **Clear**  
- Output area (read-only text box) for breakdown + result  
- Clear button wipes input and output  

**Algorithm / Implementation**  
- Uses `parse_hydrate(formula)` from `chemistry_utils` to parse chemical formulas (handles hydrates with “·”)  
- Iterates over element counts:  
  - Looks up atomic mass using `atomic_mass_u(data)` from element dataset  
  - Computes subtotal = atomic mass × count  
  - Accumulates into `total_mass`  
- Unknown elements or missing mass flagged separately  
- Logs each calculation via `add_log_entry` with formula, total mass, and breakdown  

**Units & Conversion**  
- Mass reported in grams per mole (g/mol)  

**Edge Cases & Validation**  
- Empty input → message: “Please enter a molecular formula.”  
- Parsing errors → “Error parsing formula: …”  
- Unknown symbols or missing atomic mass → listed under “Unknown or massless elements”  
- Hydrates supported (e.g., `CuSO4·5H2O`)  

**Data Sources**  
- `ptable.json` via `load_element_data()`  
- Functions from `chemistry_utils.py`:  
  - `parse_hydrate(formula)` → returns element counts dict  
  - `atomic_mass_u(data)` → retrieves atomic mass  

**Logging & Export**  
- Each calculation logged with tool = `"Molar Mass Calculator"`, action = `"Compute"`, data = {formula, mass_g_mol, breakdown}  
- No file export (result text only in UI)  

**Chaining**  
- Outputs (molar mass, breakdown) could feed into Reaction Balancer or Phase Predictor tools in chain mode  

**Tests**  
- Example 1: Formula `H2O` → H ×2 = 2.01588, O ×1 = 15.99900 → Total ≈ 18.015 g/mol  
- Example 2: Formula `C6H12O6` → C ×6, H ×12, O ×6 → Total ≈ 180.156 g/mol  
- Example 3: Formula `CuSO4·5H2O` → includes hydrate, total ≈ 249.685 g/mol  
- Example 4: Formula with invalid element (e.g., `Xx2`) → listed as unknown  

**Known Limitations / TODO**  
- No advanced parser (cannot handle parentheses or complex notations like `(NH4)2SO4`)  
- Relies on `ptable.json` → incomplete/missing elements will cause “Unknown” messages  
- No export to CSV/PNG yet (UI only)  
- Could expand to show average molar mass for mixtures  

---

### Tool: Phase Predictor
**Category:** Chemistry  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Predict the physical phase (solid, liquid, gas) of an element at a given temperature and pressure using its melting and boiling points.

**Inputs**  
- **Element Symbol**: string (e.g., `H`, `Fe`, `O`)  
- **Temperature**: number with unit suffix (`°C`, `°F`, `K`)  
  - Examples: `25`, `77F`, `300K`  
- **Pressure** (optional): number in atm (default = 1 atm)

**Outputs**  
- **Melting point** (K)  
- **Boiling point** (K)  
- **Predicted phase** at given T, P (colored: blue = solid, orange = liquid, red = gas)

**UI & Interaction**:contentReference[oaicite:0]{index=0}  
- Inputs: symbol, temperature, pressure  
- **Check Phase** button triggers evaluation  
- Result shown as formatted HTML in a label

**Algorithm / Implementation**:contentReference[oaicite:1]{index=1}  
- Loads element data via `load_element_data()`  
- Parses temperature with `parse_temperature(...)` and converts to Kelvin via `to_kelvin(...)`  
- Retrieves `melt` and `boil` (fallbacks: `MeltingPoint`, `BoilingPoint`)  
- Logic:  
  - `T < melt → solid`  
  - `melt ≤ T < boil → liquid`  
  - `T ≥ boil → gas`  
- Displays a formatted message with MP, BP, and colored phase; logs action via `add_log_entry(...)`

**Units & Conversion**  
- Temperature internally in Kelvin; inputs may be °C/°F/K (auto-converted)

**Edge Cases & Validation**:contentReference[oaicite:2]{index=2}  
- Invalid temperature format → red error (“Enter a valid temperature…”)  
- Unknown element symbol → red error  
- Missing melting/boiling data → message “No melting or boiling point data available.” and log `NoData`

**Data Sources**  
- Periodic table dataset from `load_element_data()` (ptable JSON)

**Logging & Export**:contentReference[oaicite:3]{index=3}  
- Logs:  
  - `Predict` with `{symbol, T_K, P_atm, phase}`  
  - `NoData` if element lacks MP/BP

**Chaining**  
- Phase result could feed into future thermodynamics tools (e.g., density/viscosity by phase)

**Tests**  
- `Fe`, `T=300K` → Solid  
- `H2O`, `T=298K` → Liquid (with correct MP/BP shown)  
- `Ne`, `T=350K` → Gas

**Known Limitations / TODO**  
- Ignores pressure dependence of phase boundaries (uses 1 atm MP/BP)  
- Elements lacking MP/BP cannot be predicted  
- Could add support for phase diagrams and sublimation where relevant

---

### Tool: Reaction Balancer
**Category:** Chemistry  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Automatically balance chemical reactions. Accepts one or more unbalanced reactions, applies stoichiometric balancing, and outputs balanced equations.

**Inputs**  
- **Reaction(s)**: text input (one per line)  
  - Uses `+` between species  
  - Uses `->` or `=` as reaction arrow  
  - Examples:  
    - `H2 + O2 -> H2O`  
    - `C3H8 + O2 = CO2 + H2O`

**Outputs**  
- Balanced chemical equation(s), one per input line  
- Error messages for invalid/unbalanceable inputs  

**UI & Interaction**:contentReference[oaicite:1]{index=1}  
- Instruction label with usage examples  
- Multiline text box (monospace font) for reaction input  
- Buttons:  
  - **Balance All** → balances every line in input  
  - **Copy Selected** → copies highlighted result(s) from output list  
- Output list: shows balanced reactions or red-highlighted error messages  

**Algorithm / Implementation**  
- Backend uses `balance_reaction(rxn)` from `chemistry_utils` to compute stoichiometric coefficients  
- `format_balanced(coeffs, reactants, products)` builds readable equation string  
- Each successful balancing is added to the list widget and logged  
- Failures are displayed in red and logged as `"Error"`  

**Units & Conversion**  
- Stoichiometric (no unit conversions; pure integer ratios)

**Edge Cases & Validation**  
- Empty lines ignored  
- Invalid syntax (bad arrow, missing species) → error entry  
- Reactions that cannot be balanced → error entry  
- Copy attempted with no selection → warning popup  

**Data Sources**  
- Reaction balancing algorithm from `core.data.functions.chemistry_utils`  

**Logging & Export**  
- Logs via `add_log_entry`:  
  - Action = `"Balance"` with `{input, output}`  
  - Action = `"Error"` with `{input, error}`  
- No file export; results stay in list until copied manually  

**Chaining**  
- Balanced equations could be exported to thermodynamic/kinetic modules (future chain mode)

**Tests**  
- Example 1: `H2 + O2 -> H2O` → `2 H2 + O2 -> 2 H2O`  
- Example 2: `C3H8 + O2 -> CO2 + H2O` → `C3H8 + 5 O2 -> 3 CO2 + 4 H2O`  
- Example 3: Invalid input `ABC -> XYZ` → Error entry  

**Known Limitations / TODO**  
- Only handles reactions written with plain formulas (no state symbols like (aq), (s), etc.)  
- Cannot currently balance redox equations with electron notation (`e-`)  
- No export to file (only copy to clipboard)  
- Could add support for ionic equations and half-reaction balancing

---

### Tool: Codon Lookup
**Category:** Biology  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Lookup RNA codons (triplets of A, U, G, C) and map them to amino acids. Shows the corresponding amino acid, its functional group, and a pie chart of amino acid group distributions with the queried group highlighted.

**Inputs**  
- **Codon**: string (3 characters, composed of A, U, G, C; e.g., `AUG`, `UUU`, `GGA`)  

**Outputs**  
- Amino acid (3-letter abbreviation, e.g., Met, Phe, Gly)  
- Group classification (Hydrophobic, Polar, Charged, Stop Codon)  
- Pie chart showing distribution of amino acid groups, with queried group exploded/highlighted  

**UI & Interaction**  
- Text field for codon input (placeholder: `AUG, UUU, GGA …`)  
- Buttons:  
  - **Lookup** → performs lookup and updates result field + chart  
  - **Copy** → copies text output to clipboard  
  - **Export Chart…** → saves current pie chart as an image  
- Output area: text field (read-only) showing codon, amino acid, and group  
- Embedded Matplotlib figure canvas showing distribution pie chart  

**Algorithm / Implementation**  
- Uses `CODON_TABLE` (RNA codon → amino acid mapping) from `bio_utils.py`:contentReference[oaicite:0]{index=0}  
- Uses `AMINO_ACID_GROUPS` (amino acid → group mapping):contentReference[oaicite:1]{index=1}  
- `_lookup()` method:  
  - Validates codon (length = 3, only A/U/G/C)  
  - Looks up amino acid and group  
  - Displays results in text output  
  - Calls `_plot_group_highlight(group)`  
  - Adds log entry (`Lookup`)  
- `_plot_group_highlight(target_group)` method:  
  - Counts occurrences of groups across codon table  
  - Draws pie chart of Hydrophobic, Polar, Charged, Stop Codon  
  - Explodes slice of target group  
- `_export()` method:  
  - Calls `export_figure(self.fig)`  
  - Appends saved path to output field  
  - Logs export action  
- Errors handled with `_err(msg)` → shows message in output and logs  

**Units & Conversion**  
- No units involved (biological categorical mapping only)  

**Edge Cases & Validation**  
- Invalid codon length or characters → error message: “Codon must be exactly 3 of A,U,G,C.”  
- Unknown codon not in table → error: “Unknown codon: …”  
- Export failures → error message with exception text  

**Data Sources**  
- `bio_utils.py` (`CODON_TABLE`, `AMINO_ACID_GROUPS`):contentReference[oaicite:2]{index=2}  
- Internal logging (`add_log_entry`)  
- Figure export via `core.data.functions.image_export.export_figure`:contentReference[oaicite:3]{index=3}  

**Logging & Export**  
- Logs entries under tool name `"Codon Lookup"`:  
  - `"Lookup"` with `{codon, aa, group}`  
  - `"ExportChart"` with `{path}`  
  - `"Error"` with `{msg}`  
- Chart export produces PNG file saved to user-selected path  

**Chaining**  
- Amino acid and group data could be chained into protein/nucleotide analysis tools in the future  

**Tests**  
- Example 1: Codon `AUG` → Amino acid = Met, Group = Hydrophobic  
- Example 2: Codon `UUU` → Amino acid = Phe, Group = Hydrophobic  
- Example 3: Codon `UGA` → Amino acid = STOP, Group = Stop Codon  
- Example 4: Invalid codon `XYZ` → error  

**Known Limitations / TODO**  
- Only supports RNA codons (DNA codons with T not accepted)  
- Amino acid groups simplified into 4 categories; no finer classifications  
- Pie chart always based on static codon table (no dynamic filtering)  
- Could add full protein translation mode (input mRNA sequence → amino acid chain)  

---

### Tool: Frame Translation
**Category:** Biology  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Translate DNA sequences into amino acid sequences across all six reading frames (+1..+3 and −1..−3). Supports ORF detection, reverse-complement inclusion, and visualisation of codon-to-amino-acid mapping with color-coded tracks.

**Inputs**  
- **DNA sequence**: text input (accepts A/T/C/G and IUPAC codes; `U` auto-converted to `T`)  
- **Options**:  
  - *Stop at first stop (*)*: truncate translation at the first stop codon  
  - *ORF mode*: only translate open reading frames starting at `AUG` and ending at stop  
  - *Include reverse-complement frames*: include −1..−3 in addition to forward frames  
  - *Show amino-acid letters*: overlay one-letter AA codes on the visualization  

**Outputs**  
- Text summary of translations per frame (forward frames always shown; ORF or linear mode)  
- Graphical display of all frames with codons represented as colored blocks:  
  - Green = Methionine (start)  
  - Red = Stop codon (*)  
  - Grey = Other amino acids  
- Labels with amino acid one-letter codes if enabled  

**UI & Interaction**  
- Input field (multi-line) for DNA sequence  
- Checkboxes for options (stop-first, ORF, reverse frames, show letters)  
- Button: **Translate & Visualise**  
- Output text area (read-only) summarizing translation  
- Matplotlib canvas with navigation toolbar for zoom/pan  

**Algorithm / Implementation**  
- `_sanitize_dna(s)` cleans input: removes whitespace, uppercases, replaces `U`→`T`, keeps IUPAC bases:contentReference[oaicite:0]{index=0}  
- `_rc_dna(s)` computes reverse complement:contentReference[oaicite:1]{index=1}  
- `_to_aa(codon)` maps codon → amino acid (3-letter from `CODON_TABLE`, then → 1-letter from `AA1`):contentReference[oaicite:2]{index=2}  
- `translate_linear(dna, frame_offset, stop_first)` → linear frame translation, returns AA string + codon spans:contentReference[oaicite:3]{index=3}  
- `translate_orfs(dna, frame_offset)` → detects ORFs starting at `AUG`, stops at stop codons, returns spans + AA strings:contentReference[oaicite:4]{index=4}  
- `_render_tracks(...)` draws visualization:  
  - Forward frames at y = 2.5, 1.5, 0.5  
  - Reverse frames (if enabled) at y = −0.5, −1.5, −2.5  
  - Codons drawn as rectangles, colored by type, optional AA letter overlay  
  - Ruler on x-axis = nucleotide positions (0-based)  
- `_label_aa(...)` evenly distributes AA letters across codon span:contentReference[oaicite:5]{index=5}  
- `_run()` orchestrates: validates sequence, runs translation, updates text + plot, logs action  

**Units & Conversion**  
- Not applicable (purely symbolic sequence translation)  

**Edge Cases & Validation**  
- Input too short (<3 bases) → error message in output  
- Unknown codons → mapped to `X`  
- ORF without stop codon → drawn as open-ended until sequence end  
- Empty input → clears outputs  

**Data Sources**  
- Codon table from `core.data.functions.bio_utils.CODON_TABLE`:contentReference[oaicite:6]{index=6}  
- Amino acid 1-letter mapping (`AA1`) defined locally in tool:contentReference[oaicite:7]{index=7}  
- Logging via `add_log_entry`  

**Logging & Export**  
- Logs under tool = `"Frame Translation (with visualisation)"`:  
  - Action = `"Translate"` with data: `{len, stop_first, orf_mode, include_rev, show_letters}`  
- No file export; visualization is interactive only  

**Chaining**  
- Translated sequences and ORFs could feed into other biology tools (e.g., protein property calculators)  

**Tests**  
- Example 1: Input `"ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG"` (standard test seq)  
  - Frame +1 (linear) → yields M-A-I-V-M-G-R-*...  
- Example 2: ORF mode with `ATG...TAA` → detects ORF from start to stop  
- Example 3: Reverse complement with same input → −1..−3 show valid translations  
- Example 4: Invalid characters or too short input → “Sequence too short”  

**Known Limitations / TODO**  
- Only handles DNA input (not direct RNA, though U→T auto-conversion allowed)  
- ORF detection requires `AUG` as start codon (strict)  
- No export of translation results as FASTA or text  
- Could add amino acid frequency plots or frame score summaries  
- No integration yet with sequence parsers or alignment tools  

---

### Tool: GC Content Calculator
**Category:** Biology  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Calculate the percentage of guanine (G) and cytosine (C) nucleotides in a DNA sequence. GC content is often used to estimate DNA stability and identify genome characteristics.

**Inputs**  
- **DNA sequence**: string of nucleotides (A, T, C, G).  

**Outputs**  
- **GC Content**: percentage value displayed with 2 decimal precision.  
- Example: `GC Content: 42.50%`  

**UI & Interaction**  
- Single-line text input for DNA sequence  
- Button: **Compute** → triggers calculation  
- Result label displays percentage or error message  

**Algorithm / Implementation**  
- Input sequence normalized to uppercase and stripped of whitespace:contentReference[oaicite:0]{index=0}  
- Calculation uses `Bio.SeqUtils.gc_fraction(seq)` from Biopython (returns fraction of G and C bases):contentReference[oaicite:1]{index=1}  
- Multiplied by 100 to give percentage  
- Success → result shown + logged  
- Failure (invalid characters, empty sequence) → error message + error log  

**Units & Conversion**  
- Output in **percentage (%)**  

**Edge Cases & Validation**  
- Empty input → error message  
- Invalid characters in sequence → Biopython raises error, caught and displayed  
- Lowercase input handled automatically (converted to uppercase)  

**Data Sources**  
- Uses Biopython `gc_fraction` for calculation:contentReference[oaicite:2]{index=2}  
- Logging via `core.data.functions.log.add_log_entry`  

**Logging & Export**  
- Logs under tool = `"GC Content"`:  
  - Action = `"Compute"` with `{input, gc_percent}` and tags `["bio", "dna"]`  
  - Action = `"Error"` with `{input, error}`  

**Chaining**  
- Output percentage can be passed into other tools (e.g., sequence analysis, genome profiling)  

**Tests**  
- Example 1: Input `"ATGC"` → GC Content = `50.00%`  
- Example 2: Input `"AAAA"` → GC Content = `0.00%`  
- Example 3: Input `"GGGGCC"` → GC Content = `100.00%`  
- Example 4: Invalid input `"XYZ"` → Error  

**Known Limitations / TODO**  
- Only works with standard DNA bases; IUPAC ambiguity codes not supported  
- No FASTA file input (manual sequence entry only)  
- Could extend to support multiple sequences or batch input  
- Could integrate with sequence parsers for direct file analysis  

---

### Tool: Molecular Weight Calculator
**Category:** Biology  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Estimate the molecular weight (MW) of a nucleotide or protein sequence. Supports DNA, RNA, and proteins by summing approximate base or residue weights.

**Inputs**  
- **Sequence**: string (DNA/RNA bases `A, T, G, C, U` or protein one-letter codes).  
  - Multi-line and space-separated input is accepted (whitespace removed automatically).  

**Outputs**  
- Approximate MW in Daltons (Da), displayed in the format:  
  - `"Approximate DNA/RNA MW: X Da"`  
  - `"Approximate Protein MW: X Da"`  
- Error message if sequence contains invalid characters.  

**UI & Interaction**  
- Multi-line text box for sequence input  
- Button: **Calculate** → runs MW calculation  
- Output label shows result or error  

**Algorithm / Implementation**  
- Input sequence normalized: uppercase, whitespace/newlines removed:contentReference[oaicite:0]{index=0}  
- Two internal dictionaries:  
  - `DNA_W`: base weights (A = 313.21, T = 304.20, G = 329.21, C = 289.18, U = 290.17):contentReference[oaicite:1]{index=1}  
  - `PROT_W`: residue weights for 20 standard amino acids (one-letter codes):contentReference[oaicite:2]{index=2}  
- Logic:  
  - If all characters ∈ `DNA_W` → sum base weights → DNA/RNA MW  
  - Else if all characters ∈ `PROT_W` → sum residue weights → Protein MW  
  - Else → “Sequence contains invalid characters.”  
- Result displayed in UI and logged with sequence length  

**Units & Conversion**  
- Output molecular weight in **Daltons (Da)**  

**Edge Cases & Validation**  
- Empty input → `"Please enter a sequence."`  
- Mixed characters (not purely DNA/RNA or purely protein) → error message  
- RNA input allowed (`U` recognized with its own weight)  

**Data Sources**  
- Static weight tables (`DNA_W`, `PROT_W`) embedded in tool:contentReference[oaicite:3]{index=3}  
- Logging via `core.data.functions.log.add_log_entry`  

**Logging & Export**  
- Logs under tool = `"Molecular Weight Calculator"`:  
  - Action = `"Calculate"` with `{len, msg}`  
- No export functionality  

**Chaining**  
- Output MW could feed into other analysis tools (e.g., concentration, stoichiometry calculators)  

**Tests**  
- Example 1: Sequence `"ATGC"` → MW ≈ 313.21 + 304.20 + 329.21 + 289.18 = `1235.80 Da`  
- Example 2: Sequence `"MSTNPKPQRKTKRNTNRRPQDVKFPGG"` → MW ≈ sum of PROT_W values  
- Example 3: Empty input → error `"Please enter a sequence."`  
- Example 4: Sequence with invalid character `"ABZ"` → error `"Sequence contains invalid characters."`  

**Known Limitations / TODO**  
- Simplified MW estimates: does not account for water loss during polymerization  
- No handling of modified bases or amino acids  
- No support for ambiguous nucleotide codes (IUPAC)  
- Could add FASTA input support and export to CSV/FASTA with MW annotations  

---

### Tool: Osmosis & Tonicity
**Category:** Biology  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Assess tonicity and predict the direction of water movement across a semi-permeable membrane, based on internal and external solute concentrations.

**Inputs**  
- **Internal concentration (mM)**: numeric field for solute concentration inside the cell.  
- **External concentration (mM)**: numeric field for solute concentration outside the cell.  

**Outputs**  
- Text classification of the tonicity condition:  
  - `"Hypertonic inside: Water leaves the cell"`  
  - `"Hypotonic inside: Water enters the cell"`  
  - `"Isotonic: No net water movement"`  

**UI & Interaction**  
- Two numeric input fields (internal, external)  
- Button: **Assess** → evaluates condition  
- Result label displays tonicity message  

**Algorithm / Implementation**  
- Attempts to parse both inputs as floats:contentReference[oaicite:0]{index=0}  
- Logic:  
  - If `inside > outside` → Hypertonic inside → water exits cell  
  - If `inside < outside` → Hypotonic inside → water enters cell  
  - If equal → Isotonic → no net flow  
- Errors (non-numeric input) produce `"Invalid input."`  

**Units & Conversion**  
- Inputs/outputs in millimolar (mM)  
- No internal conversions; direct numeric comparison  

**Edge Cases & Validation**  
- Non-numeric input → `"Invalid input."`  
- Identical values (inside = outside) → isotonic message  
- Negative concentrations not explicitly handled (interpreted as floats without validation)  

**Data Sources**  
- No external databases required  
- Logging via `core.data.functions.log.add_log_entry`  

**Logging & Export**  
- Logs under tool = `"Osmosis & Tonicity"`:  
  - Action = `"Assess"` with `{in, out, msg}`  
  - Action = `"Error"` with `{msg}`  

**Chaining**  
- Tonicity result could be used by future cell biology or physiology modules  

**Tests**  
- Example 1: Inside = 200, Outside = 100 → `"Hypertonic inside: Water leaves the cell"`  
- Example 2: Inside = 100, Outside = 200 → `"Hypotonic inside: Water enters the cell"`  
- Example 3: Inside = 150, Outside = 150 → `"Isotonic: No net water movement"`  
- Example 4: Invalid input (e.g., `"abc"`) → `"Invalid input."`  

**Known Limitations / TODO**  
- Simplified model; ignores osmotic pressure formulas and non-ideal effects  
- No validation against negative or unrealistic values  
- Could add graphical illustration of cell volume change  
- Could expand to support osmotic pressure (π = iCRT) for more precise predictions  

---

### Tool: Pairwise Alignment
**Category:** Biology  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Perform global pairwise sequence alignment using the Needleman–Wunsch (NW) algorithm with affine gap penalties. Provides both the aligned sequences and a visual match/mismatch representation.

**Inputs**  
- **Sequence A**: string (DNA, RNA, or protein)  
- **Sequence B**: string (DNA, RNA, or protein)  
- **Scoring parameters**:  
  - Match score (default = 1)  
  - Mismatch penalty (default = −1)  
  - Gap opening penalty (default = −2)  
  - Gap extension penalty (default = −1)  

**Outputs**  
- Text-based alignment in 3 lines:  
  - Top: aligned sequence A  
  - Middle: match line (`|` for match, `.` for mismatch, space for gap)  
  - Bottom: aligned sequence B  
  - Final line: `Score=X`  

**UI & Interaction**  
- Two text fields for input sequences  
- Four numeric spinners for scoring values (range: match/mismatch = −10..10, gap penalties = −50..0)  
- Button: **Align** → runs alignment  
- Output field: fixed-width font (Consolas, 11pt) for alignment display  

**Algorithm / Implementation**  
- `_nw_align(a, b, match, mismatch, gap_open, gap_extend)` implements NW with affine gaps:contentReference[oaicite:0]{index=0}  
  - Uses three DP matrices: `M` (match/mismatch), `X` (gap in A), `Y` (gap in B)  
  - Traceback constructs aligned strings for A and B  
  - Returns `(aln_a, aln_b, score)`  
- `pretty_alignment(...)` builds formatted 3-line alignment + score:contentReference[oaicite:1]{index=1}  
- `_do_align()` orchestrates input handling, runs NW, formats result, logs action  

**Units & Conversion**  
- Alignment score is unitless (based on scoring scheme)  

**Edge Cases & Validation**  
- Missing sequence(s) → error: `"Enter both sequences."`  
- Empty strings not allowed  
- Handles any alphabet (A/T/C/G or amino acids), though case-normalized to uppercase  
- Extreme scoring values allowed within defined ranges  

**Data Sources**  
- No external libraries required (pure Python implementation)  
- Logging via `core.data.functions.log.add_log_entry`  

**Logging & Export**  
- Logs under tool = `"Pairwise Alignment (NW, affine gaps)"`:  
  - Action = `"Align"` with `{len_a, len_b, score}`  
- No file export (alignment shown in UI only)  

**Chaining**  
- Aligned sequences could feed into downstream tools (e.g., similarity scoring, motif detection)  

**Tests**  
- Example 1: A = `"GATTACA"`, B = `"GCATGCU"` with defaults → produces classical NW alignment with score  
- Example 2: Identical sequences `"AAAA"` and `"AAAA"` → full match, score = 4  
- Example 3: One empty sequence `"ATCG"`, `""` → output handled as error  
- Example 4: Adjusting gap penalties shows expected alignment differences  

**Known Limitations / TODO**  
- Global alignment only; no local (Smith–Waterman) support  
- No visualization of alignment statistics (percent identity, gap count)  
- Not optimized for very long sequences (DP is O(n·m))  
- Could add FASTA input/output support and alignment export  

---

### Tool: pH Calculator
**Category:** Biology / Chemistry  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Calculate the pH or pOH of a solution given either hydrogen ion concentration [H⁺] or hydroxide ion concentration [OH⁻].

**Inputs**  
- **H⁺ concentration [mol/L]**: numeric field (optional, must be > 0)  
- **OH⁻ concentration [mol/L]**: numeric field (optional, must be > 0)  
- Only one field should be filled; if both are filled → error  

**Outputs**  
- If [H⁺] provided: `pH = X.XX`  
- If [OH⁻] provided: `pOH = X.XX, pH = X.XX`  
- Error messages:  
  - `"Enter only one concentration."` (both fields filled)  
  - `"Enter at least one concentration."` (no input)  
  - `"Invalid input."` (non-numeric or non-positive values)  

**UI & Interaction**  
- Two input fields: one for H⁺, one for OH⁻  
- Button: **Calculate** → performs calculation  
- Output label displays result or error  

**Algorithm / Implementation**  
- Reads user input from text fields:contentReference[oaicite:0]{index=0}  
- If both inputs provided → error  
- If H⁺ input:  
  - Convert to float  
  - If ≤ 0 → error  
  - pH = −log₁₀([H⁺]):contentReference[oaicite:1]{index=1}  
- If OH⁻ input:  
  - Convert to float  
  - If ≤ 0 → error  
  - pOH = −log₁₀([OH⁻])  
  - pH = 14 − pOH:contentReference[oaicite:2]{index=2}  
- If neither input provided → error  
- Result displayed in output label and logged  

**Units & Conversion**  
- Inputs expected in **mol/L**  
- Output is dimensionless (pH / pOH scale)  

**Edge Cases & Validation**  
- Zero or negative input → invalid  
- Both inputs given → error  
- Empty input → error  
- Large/small scientific notation inputs allowed (float conversion)  

**Data Sources**  
- Internal calculation using `math.log10`:contentReference[oaicite:3]{index=3}  
- Logging via `core.data.functions.log.add_log_entry`  

**Logging & Export**  
- Logs under tool = `"pH Calculator"`:  
  - Action = `"Calculate"` with `{H, OH, msg}`  

**Chaining**  
- Output pH can feed into biochemical or environmental analysis tools  

**Tests**  
- Example 1: [H⁺] = 1e−3 → pH = 3.00  
- Example 2: [OH⁻] = 1e−4 → pOH = 4.00, pH = 10.00  
- Example 3: [H⁺] = −1 (invalid) → error  
- Example 4: Both [H⁺] and [OH⁻] entered → error `"Enter only one concentration."`  

**Known Limitations / TODO**  
- Assumes standard 25 °C conditions ([H⁺][OH⁻] = 1e−14); no temperature adjustment  
- No support for buffered solutions or polyprotic acids/bases  
- Could add automatic detection if both H⁺ and OH⁻ are given and consistent  
- Could add graphical pH scale visualization  

---

### Tool: Population Growth Calculator
**Category:** Biology  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Calculate exponential population growth over time using the standard growth model equation:  
\[
N(t) = N₀ \cdot e^{rt}
\]  
where N₀ = initial population, r = growth rate, and t = time.

**Inputs**  
- **Initial Population (N₀)**: numeric field (float, ≥ 0)  
- **Growth Rate (r)**: per time unit (float; can be positive or negative)  
- **Time (t)**: numeric field representing elapsed time  

**Outputs**  
- Population size after t time units:  
  - Example: `"Population after 10 time units: 4523.17"`  
- Error message if input invalid: `"Invalid input."`  

**UI & Interaction**  
- Three numeric input fields: initial population, growth rate, time  
- Button: **Calculate** → runs exponential growth equation  
- Result label displays calculated population or error  

**Algorithm / Implementation**  
- Reads values from text fields and converts to floats:contentReference[oaicite:0]{index=0}  
- Uses exponential model: `N = N0 * exp(r * t)`:contentReference[oaicite:1]{index=1}  
- Displays result rounded to 2 decimals  
- Exceptions (invalid input) caught → outputs `"Invalid input."`  
- Logs all calculations  

**Units & Conversion**  
- Inputs dimensionless except growth rate (per time unit)  
- Output = population size (same units as N₀, no conversion)  

**Edge Cases & Validation**  
- Non-numeric input → `"Invalid input."`  
- Negative growth rate (r < 0) → supported (decay model)  
- Zero initial population (N₀ = 0) → always 0  
- Large t or r → may cause overflow in exponential  

**Data Sources**  
- Internal calculation with `math.exp`:contentReference[oaicite:2]{index=2}  
- Logging via `core.data.functions.log.add_log_entry`  

**Logging & Export**  
- Logs under tool = `"Population Growth Calculator"`:  
  - Action = `"Calculate"` with `{N0, r, t, msg}`  

**Chaining**  
- Output population size could feed into ecological or epidemiological models  

**Tests**  
- Example 1: N₀ = 100, r = 0.05, t = 10 → N ≈ 164.87  
- Example 2: N₀ = 50, r = −0.1, t = 5 → N ≈ 30.33  
- Example 3: Invalid inputs `"abc"` for growth rate → `"Invalid input."`  
- Example 4: N₀ = 0, r = 0.2, t = 10 → N = 0  

**Known Limitations / TODO**  
- Only models simple exponential growth (no logistic or carrying c

---

### Tool: Reverse Complement
**Category:** Biology  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Generate the reverse complement of a DNA sequence. Commonly used in genomics to analyze the opposite strand of DNA.

**Inputs**  
- **DNA sequence**: string containing nucleotides (A, T, C, G).  

**Outputs**  
- Reverse complement sequence as a string.  
- Example: `"Reverse Complement: TGCA"`  
- Error message if input is invalid.  

**UI & Interaction**  
- Single-line text input for DNA sequence  
- Button: **Compute** → calculates reverse complement  
- Output label displays result or error  

**Algorithm / Implementation**  
- Input normalized to uppercase and stripped of whitespace:contentReference[oaicite:0]{index=0}  
- Uses Biopython `Seq(seq).reverse_complement()` for computation:contentReference[oaicite:1]{index=1}  
- If successful: result shown + logged  
- If error (invalid input) → error message displayed + logged  

**Units & Conversion**  
- No units (purely symbolic DNA sequence manipulation)  

**Edge Cases & Validation**  
- Empty input → error  
- Invalid characters not recognized by Biopython → error  
- Case-insensitive (converted to uppercase automatically)  

**Data Sources**  
- Biopython `Seq` class:contentReference[oaicite:2]{index=2}  
- Logging via `core.data.functions.log.add_log_entry`  

**Logging & Export**  
- Logs under tool = `"Reverse Complement"`:  
  - Action = `"Compute"` with `{input, result}`, tags = `["bio", "dna"]`  
  - Action = `"Error"` with `{input, error}`  

**Chaining**  
- Reverse complement sequence could be passed into translation, GC content, or alignment tools  

**Tests**  
- Example 1: Input `"ATGC"` → Reverse complement = `"GCAT"`  
- Example 2: Input `"aaaa"` → Reverse complement = `"TTTT"`  
- Example 3: Input with invalid chars `"XYZ"` → error  
- Example 4: Empty input → error  

**Known Limitations / TODO**  
- Only supports DNA sequences (RNA not directly handled)  
- No FASTA file input support (manual entry only)  
- Could add batch mode for multiple sequences  
- Could extend to return both reverse and complement separately  

---

### Tool: Sequence File Parser
**Category:** Biology  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Open and parse DNA/RNA/protein sequence files in FASTA or GenBank format. Displays sequence information (ID, length, sequence) for each record in the file.

**Inputs**  
- **File input**: user-selected FASTA (`.fasta`, `.fa`) or GenBank (`.gb`, `.gbk`) file.  

**Outputs**  
- Parsed sequence records displayed in text format, including:  
  - Sequence ID  
  - Sequence length  
  - Raw sequence (as string)  
- Example output block:  

ID: seq1
Length: 350
Sequence:
ATGCTAGCTAG...
--------------

- Error message shown if parsing fails.  

**UI & Interaction**  
- Button: **Open File** → opens file dialog for FASTA/GenBank files:contentReference[oaicite:0]{index=0}  
- Output area: read-only text box with parsed results  
- Multiple records concatenated with separators  

**Algorithm / Implementation**  
- Uses Biopython `SeqIO.parse` to load sequences:contentReference[oaicite:1]{index=1}  
- Attempts FASTA parsing first; if no records, falls back to GenBank:contentReference[oaicite:2]{index=2}  
- Iterates through records and formats output with ID, length, and sequence  
- On success: displays results and logs action  
- On failure: error message displayed + logged  

**Units & Conversion**  
- No units (sequences are symbolic strings)  

**Edge Cases & Validation**  
- Empty or invalid file → error message  
- File not selected → no action  
- Files with zero records in FASTA → fallback to GenBank parser  
- Very large sequences → displayed in full (no truncation)  

**Data Sources**  
- Biopython `SeqIO` library:contentReference[oaicite:3]{index=3}  
- Logging via `core.data.functions.log.add_log_entry`  

**Logging & Export**  
- Logs under tool = `"Seq Parser"`:  
- Action = `"Parse"` with `{file, records}`, tags = `["bio", "seqio"]`  
- Action = `"Error"` with `{file, error}`  

**Chaining**  
- Parsed sequences could feed into downstream tools (translation, alignment, GC content analysis)  

**Tests**  
- Example 1: FASTA file with two sequences → both parsed and displayed with IDs and lengths  
- Example 2: GenBank file → correctly parsed into annotated sequence output  
- Example 3: Invalid file type → error `"Error: ..." `  
- Example 4: Empty FASTA → fallback to GenBank; if also empty → error  

**Known Limitations / TODO**  
- Displays raw sequences only; no annotation details from GenBank records  
- No batch export (only in-app viewing)  
- No truncation for very large sequences (may overload UI)  
- Could extend to show sequence features, metadata, or save parsed results to file  

---

### Tool: DNA Transcription & Translation
**Category:** Biology  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Simulate transcription and translation of a DNA sequence. Produces the corresponding mRNA sequence and the protein sequence derived from codon mapping, and visualizes codon usage frequencies.

**Inputs**  
- **DNA sequence**: string containing nucleotides (A, T, C, G).  
  - Whitespace ignored  
  - Case-insensitive (converted to uppercase)  

**Outputs**  
- **mRNA sequence** (T → U conversion)  
- **Protein sequence** as amino acid codes (joined by `-`)  
- **Codon usage chart** (horizontal bar chart of codon frequencies)  
- Error messages for invalid input (e.g., non-ATCG characters)  

**UI & Interaction**  
- Single-line text field for DNA sequence input:contentReference[oaicite:0]{index=0}  
- Buttons:  
  - **Translate** → performs transcription & translation  
  - **Copy Result** → copies text output to clipboard  
  - **Export Chart…** → saves codon usage chart  
- Output area: read-only text box showing mRNA and protein sequences  
- Embedded Matplotlib canvas showing codon usage chart  

**Algorithm / Implementation**  
- `_translate()`:contentReference[oaicite:1]{index=1}  
  - Cleans input (`A,T,C,G` only)  
  - Transcribes DNA → mRNA by replacing T with U  
  - Splits mRNA into codons (triplets)  
  - Translates codons using `CODON_TABLE` from `bio_utils.py`  
  - Stores codons for plotting  
  - Displays mRNA and protein sequence in text output  
  - Plots codon usage chart  
  - Logs `"Translate"` with `{len, codons}`  
- `_plot_codon_usage(codons)`:contentReference[oaicite:2]{index=2}  
  - Counts codon occurrences (`Counter`)  
  - Plots horizontal bar chart (codon vs. frequency)  
- `_copy()`:contentReference[oaicite:3]{index=3}  
  - Copies output text to clipboard  
  - Logs `"Copy"`  
- `_export_chart()`:contentReference[oaicite:4]{index=4}  
  - Exports figure via `export_figure`  
  - Appends saved path to output  
  - Logs `"ExportChart"`  
  - On error, logs `"Error"`  
- `_err(msg)` → displays error message in output and logs  

**Units & Conversion**  
- Not applicable (symbolic sequence processing only)  

**Edge Cases & Validation**  
- Empty input → error `"DNA must contain only A,T,C,G."`  
- Invalid characters in sequence → error message  
- Length not divisible by 3 → last incomplete codon ignored  

**Data Sources**  
- Codon table from `core.data.functions.bio_utils.CODON_TABLE`:contentReference[oaicite:5]{index=5}  
- Logging via `core.data.functions.log.add_log_entry`  
- Figure export via `core.data.functions.image_export.export_figure`  

**Logging & Export**  
- Logs under tool = `"DNA Transcription & Translation"`:  
  - Action = `"Translate"` with `{len, codons}`  
  - Action = `"Copy"`  
  - Action = `"ExportChart"` with `{path}`  
  - Action = `"Error"` with `{msg}`  

**Chaining**  
- Output protein sequence could be chained to protein property or alignment tools  

**Tests**  
- Example 1: Input `"ATGGCCATTGTAATGGGCCGCTGAAAGGGTGCCCGATAG"` →  
  - mRNA = `"AUGGCCAUUGUAAUGGGCCGCUGAAAGGGUGCCCGAUAG"`  
  - Protein = `Met-Ala-Ile-Val-Met-Gly-Arg-STOP-…`  
- Example 2: Input with invalid chars `"ATXGC"` → error  
- Example 3: Empty input → error  
- Example 4: Codon usage chart shows counts of each codon  

**Known Limitations / TODO**  
- Uses standard codon table only (no alternative genetic codes)  
- Outputs amino acids as 3-letter codes (expandable to 1-letter or full names)  
- Stops not treated as explicit termination (simply labeled `"STOP"`)  
- No FASTA file import (manual entry only)  
- Could add option for full protein translation (ORFs, stop codon termination)  

---

### Tool: Coulomb Force Calculator
**Category:** Electricity  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Calculate the electrostatic force between two point charges using Coulomb’s law:  
\[
F = k \cdot \frac{|q_1 \cdot q_2|}{r^2}
\]  
where \(k = 8.9875517923 \times 10^9 \ \text{N·m²/C²}\), \(q_1, q_2\) are charges, and \(r\) is distance.

**Inputs**  
- **q₁ (Coulombs)**: charge 1, default `1e-6 C`  
- **q₂ (Coulombs)**: charge 2, default `-2e-6 C`  
- **Distance r (m)**: separation between charges, default `0.05 m`  

**Outputs**  
- Magnitude of electrostatic force in Newtons (N)  
- Nature of force: `"repulsive"` if charges have same sign, `"attractive"` if opposite  
- Example: `|F| = 7.19 N (attractive)`  

**UI & Interaction**  
- Three input fields (q₁, q₂, r):contentReference[oaicite:0]{index=0}  
- Button: **Compute** → calculates force  
- Output label displays result or error  

**Algorithm / Implementation**  
- Reads inputs as floats:contentReference[oaicite:1]{index=1}  
- Validates `r > 0`, else raises error  
- Computes Coulomb force: `F = K * abs(q1 * q2) / (r * r)`:contentReference[oaicite:2]{index=2}  
- Determines nature:  
  - If `q1 * q2 > 0` → repulsive  
  - If `q1 * q2 < 0` → attractive  
- Displays formatted output with 6 significant figures  
- Logs success or error  

**Units & Conversion**  
- Inputs: Coulombs (C), meters (m)  
- Output: Newtons (N)  

**Edge Cases & Validation**  
- Zero or negative distance → error `"Invalid input."`  
- Non-numeric input → error `"Invalid input."`  
- Very small distances may cause large forces (no explicit cap)  

**Data Sources**  
- Constant \(K = 8.9875517923 \times 10^9\) hardcoded:contentReference[oaicite:3]{index=3}  
- Logging via `core.data.functions.log.add_log_entry`  

**Logging & Export**  
- Logs under tool = `"Coulomb Force Calculator"`:  
  - Action = `"Compute"` with `{q1, q2, r, F, nature}`  
  - Action = `"Error"` with `{msg}`  

**Chaining**  
- Force output could be chained to mechanics tools (e.g., motion under forces)  

**Tests**  
- Example 1: q₁ = 1e−6 C, q₂ = −2e−6 C, r = 0.05 m → F ≈ 7.19 N (attractive)  
- Example 2: q₁ = 1e−6 C, q₂ = 1e−6 C, r = 0.1 m → F ≈ 0.898 N (repulsive)  
- Example 3: Invalid input `"abc"` → error  
- Example 4: r = 0 → error  

**Known Limitations / TODO**  
- Only supports point charges in vacuum (no dielectric constant support)  
- No vector output (magnitude only)  
- Could add unit prefixes (µC, nC, etc.)  
- Could visualize forces as arrows between charges  

---

### Tool: Electric Field Visualiser (two charges)
**Category:** Electricity  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Plot electric field lines generated by two point charges and overlay a heatmap of field magnitude (log10|E|). Useful for visual intuition about superposition and charge configurations.

**Inputs**  
- **q₁ (C)**, **x₁ (m)**, **y₁ (m)**  
- **q₂ (C)**, **x₂ (m)**, **y₂ (m)**  
- **Plot half-width H (m)**: range is `[-H, +H]` on both axes  
- **Grid N**: resolution (N × N)

**Outputs**  
- Streamplot of field lines  
- Semi-transparent heatmap of `log10(|E|)`  
- Charge markers (q₁ red, q₂ blue)

**UI & Interaction**  
- Inputs for charge values and positions, plot range and grid size  
- **Plot field** button renders the figure  
- **Export Image…** button saves the current figure  
- Matplotlib navigation toolbar for zoom/pan

**Algorithm / Implementation**  :contentReference[oaicite:0]{index=0}  
- Constant \(K = 8.9875517923 \times 10^9\) (vacuum)  
- Build grid: `xs, ys = linspace(-H, H, N)` → `X, Y = meshgrid(xs, ys)`  
- For each charge \(q\) at \((x_q, y_q)\):  
  - \(\Delta x = X - x_q\), \(\Delta y = Y - y_q\), \(r = \sqrt{\Delta x^2 + \Delta y^2} + 10^{-12}\)  
  - \(E_x = K q \Delta x / r^3\), \(E_y = K q \Delta y / r^3\)  
- Superpose fields: `Ex = E1x + E2x`, `Ey = E1y + E2y`; magnitude `E = sqrt(Ex**2 + Ey**2)`  
- Plot: `ax.streamplot(X, Y, Ex, Ey, density=1.2, linewidth=1, arrowsize=1)`  
- Heatmap: `imshow(log10(E + 1e-12), extent=[-H,H,-H,H], origin="lower", alpha=0.3)`  
- Scatter charge positions; add colorbar `"log10|E|"`  
- Log action `"Plot"` with all parameters

**Units & Conversion**  
- Inputs: C (charge), m (position/range)  
- Field is visual; colorbar is `log10(|E|)` (|E| in N·C⁻¹)

**Edge Cases & Validation**  
- Singularities avoided via `+1e-12` in \(r\)  
- `N` parsed via `int(float(text))` (non-integer strings like `"25"` or `"25.0"` accepted)  
- Any conversion/parse failure → error logged

**Data Sources**  
- No external data; uses core logging and figure export helpers

**Logging & Export**  
- `"Plot"` with `{q1,q2,x1,y1,x2,y2,H,N}`  
- `"Error"` with `{msg}`  
- Export via **Export Image…** button

**Chaining**  
- None (visual-only output)

**Tests**  
- Dipole: `q1=+5e-6` at (−0.2, 0), `q2=−5e-6` at (+0.2, 0), `H=0.6`, `N=25` → characteristic dipole lines  
- Like charges (both positive) → field lines diverge; midline is a null of normal component  
- Smaller `H` or larger `N` adjusts view/resolution

**Known Limitations / TODO**  
- Vacuum only (no dielectric constant εᵣ)  
- Exactly two point charges only  
- Heatmap shows |E|, not true potential V  
- No numeric probe for E at a clicked point

---

### Tool: Ferromagnetism Helper
**Category:** Electricity / Magnetism  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Provide a quick explanation of ferromagnetism, common ferromagnetic materials, and their properties. Designed as a simple reference/lookup tool rather than a calculator.

**Inputs**  
- None (static knowledge-based tool).  

**Outputs**  
- Text block with:  
  - Definition of ferromagnetism  
  - List of common ferromagnetic elements/materials (e.g., Fe, Co, Ni, alloys)  
  - Short note on domains and hysteresis  
- Error only if display fails.  

**UI & Interaction**  
- Static informational UI window  
- Displays explanatory text about ferromagnetism  
- No input fields  
- No export  

**Algorithm / Implementation**  
- Loads static predefined text into the output field (no calculations, no external calls)   
- Provides overview of ferromagnetism, emphasizing:  
  - Strong magnetic ordering  
  - Alignment of magnetic domains  
  - Materials: iron, cobalt, nickel, and some alloys  
  - Hysteresis effect  

**Units & Conversion**  
- Not applicable (text-only explanatory tool)  

**Edge Cases & Validation**  
- None (no user input)  

**Data Sources**  
- Static text defined in code   
- Logging via `core.data.functions.log.add_log_entry`  

**Logging & Export**  
- Logs under tool = `"Ferromagnetism Helper"`:  
  - Action = `"Open"` or `"View"` (depending on implementation)  
- No export feature  

**Chaining**  
- None (reference tool only)  

**Tests**  
- Opening tool displays static explanation with no error  

**Known Limitations / TODO**  
- Purely descriptive; no calculations or simulations  
- Could expand with interactive magnetic domain diagrams  
- Could integrate with magnetic field calculators for combined usage  

---

### Tool: Magnetic Field Calculator
**Category:** Electricity / Magnetism  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Calculate and plot magnetic fields for three canonical configurations:  
1. Infinite straight wire (radial dependence)  
2. Circular current loop (on-axis field)  
3. Long solenoid (on-axis interior field)  

**Inputs**  
- **Geometry**: dropdown (`Infinite straight wire`, `Circular loop`, `Long solenoid`)  
- **I (A)**: current through conductor  
- **r (m)**:  
  - Wire → radial distance  
  - Loop → loop radius  
  - Solenoid → coil radius  
- **N (turns)**: integer (for loop/solenoid)  
- **L (m)**: solenoid length (for solenoid only)  
- **Plot range**: `x_min`, `x_max` (axis or radial distance)

**Outputs**  
- Line plot of B vs. distance (radial or axial depending on geometry)  
- Axis labels, grid, and title with geometry info  
- Example: `"B(x) along axis of loop (R=0.05 m, N=500)"`  

**UI & Interaction**  
- Dropdown for geometry:contentReference[oaicite:0]{index=0}  
- Input fields for current, radius, turns, length, and plot range  
- Buttons:  
  - **Compute / Plot** → generates B-field plot  
  - **Export Image…** → saves current figure  
- Matplotlib toolbar for zoom/pan  
- Embedded figure canvas  

**Algorithm / Implementation**  
- Constant: \(\mu_0 = 4π × 10^{-7}\) H/m:contentReference[oaicite:1]{index=1}  
- For each geometry:  
  - **Infinite straight wire**: \(B(r) = \frac{\mu_0 I}{2πr}\)  
  - **Circular loop (N turns)**: \(B(x) = \frac{\mu_0 I R^2}{2 (R^2 + x^2)^{3/2}} \cdot N\)  
  - **Long solenoid**: \(B ≈ \mu_0 \cdot \frac{N}{L} \cdot I\) (uniform interior field)  
- Uses `numpy.linspace` to build x-axis, `matplotlib` for plotting:contentReference[oaicite:2]{index=2}  
- If `xmax ≤ xmin`, defaults to `[0, max(0.1, 4|r|)]`  
- Logs successful plot with all parameters  

**Units & Conversion**  
- Current: amperes (A)  
- Lengths: meters (m)  
- Field: tesla (T)  

**Edge Cases & Validation**  
- Division by zero avoided via `np.clip(xs, 1e-6, None)` in wire formula  
- Missing/invalid inputs → logged as error (no crash)  
- Ensures `N ≥ 1` in loop mode  

**Data Sources**  
- Physics formulas implemented directly:contentReference[oaicite:3]{index=3}  
- Logging via `core.data.functions.log.add_log_entry`  
- Export via `core.data.functions.image_export.export_figure`  

**Logging & Export**  
- Logs under tool = `"Magnetic Field Calculator (wire / loop / solenoid)"`:  
  - Action = `"Plot"` with `{geom, I, r, N, L, xmin, xmax}`  
  - Action = `"Error"` with `{msg}`  

**Chaining**  
- B-field plots could be inputs to electromagnetism simulations or force calculators  

**Tests**  
- Example 1: Wire, I=5 A, r range 0–0.2 m → B decreases as 1/r  
- Example 2: Loop, I=5 A, R=0.05 m, N=500, range 0–0.2 → bell-shaped curve centered at x=0  
- Example 3: Solenoid, I=5 A, N=500, L=0.4 m → flat constant line (uniform field)  
- Example 4: xmax ≤ xmin → auto-corrected range  

**Known Limitations / TODO**  
- Only models idealized geometries (infinite wire, perfect loop, infinitely long solenoid)  
- No off-axis field calculation  
- No vector visualization (magnitude only)  
- Could add support for finite solenoids and Helmholtz coils  

---

### Tool: Magnetic Flux & Induction
**Category:** Electricity / Magnetism  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Simulate electromagnetic induction via Faraday’s law. Calculates and plots the induced EMF in a coil given different magnetic field profiles (linear or sinusoidal).

**Inputs**  
- **N (turns)**: number of coil turns (default 200)  
- **A (m²)**: coil area (default 0.01)  
- **dB/dt (T/s)**: magnetic field rate of change (for linear profile, default 0.5)  
- **Profile**: dropdown:  
  - `"Linear B(t) = B0 + k·t"`  
  - `"Sinusoidal B(t) = B0 + ΔB·sin(ω·t)"`  
- **B0 (T)**: base magnetic field (default 0.0)  
- **ΔB (T)**: amplitude of sinusoidal variation (default 0.2)  
- **ω (rad/s)**: angular frequency (default 50.0)  
- **t_max (s)**: simulation time span (default 2.0)  

**Outputs**  
- Line plot of EMF (in volts) vs. time  
- Title indicating chosen profile and parameters  
- Example: `"EMF for sinusoidal B(t) with ΔB=0.2, ω=50.0"`  

**UI & Interaction**  
- Input fields for N, A, B0, ΔB, ω, dB/dt, t_max:contentReference[oaicite:0]{index=0}  
- Dropdown for profile type  
- Buttons:  
  - **Plot EMF** → runs calculation and updates plot  
  - **Export Image…** → saves figure via export_figure  
- Embedded Matplotlib figure with navigation toolbar  

**Algorithm / Implementation**  
- Builds time array: `t = np.linspace(0, tmax, 800)`:contentReference[oaicite:1]{index=1}  
- For linear profile:  
  - \( B(t) = B0 + k·t \), with slope from dB/dt input  
- For sinusoidal profile:  
  - \( B(t) = B0 + ΔB·sin(ω·t) \)  
- EMF computed via Faraday’s law:  
  \[
  \text{EMF}(t) = -N·A·\frac{dB}{dt}
  \]  
  implemented as `-N*A*np.gradient(B,t)`  
- Plots EMF vs. time with grid and legend  
- Logs `"PlotEMF"` action with parameters  

**Units & Conversion**  
- N (unitless), A (m²), B (T), dB/dt (T/s), ω (rad/s), t (s)  
- Output EMF in volts (V)  

**Edge Cases & Validation**  
- Invalid numeric inputs → error logged  
- Negative/zero values accepted (coil parameters not restricted)  
- Linear gradient computed numerically, so discontinuities in input avoided  

**Data Sources**  
- Physics formulas directly implemented:contentReference[oaicite:2]{index=2}  
- Logging via `core.data.functions.log.add_log_entry`  
- Export via `core.data.functions.image_export.export_figure`  

**Logging & Export**  
- Logs under tool = `"Magnetic Flux & Induction (Faraday)"`:  
  - Action = `"PlotEMF"` with `{N, A, profile, B0, dBdt/ΔB, ω, tmax}`  
  - Action = `"Error"` with `{msg}`  

**Chaining**  
- EMF vs. time data could be fed into circuit simulators or energy calculators  

**Tests**  
- Example 1: N=200, A=0.01, dB/dt=0.5, linear profile → constant EMF trace  
- Example 2: Sinusoidal, ΔB=0.2, ω=50 → EMF sinusoidal with phase shift  
- Example 3: B0 nonzero → offset in magnetic field, EMF unaffected (depends only on variation)  
- Example 4: Invalid input `"abc"` → error  

**Known Limitations / TODO**  
- Only supports uniform B-field profiles (linear or sinusoidal)  
- No spatial variation across coil area  
- Numerical derivative may introduce small noise  
- Could add support for arbitrary user-defined B(t) functions  
- Could display flux Φ(t) alongside EMF  

---

### Tool: Magnetic Field Lines (Magnoline)
**Category:** Electricity / Magnetism  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Visualize magnetic field lines from user-defined point dipole-like magnets. Supports placing multiple magnets with strengths and positions, then plots the resulting field lines via superposition.

**Inputs**  
- **Magnet parameters**:  
  - X position (float)  
  - Y position (float)  
  - Strength (float, positive = red pole, negative = blue pole)  

**Outputs**  
- Streamplot of magnetic field lines from defined magnets  
- Scatter markers for magnets with color-coded polarity  
- Status updates with number of magnets defined  

**UI & Interaction**  
- Input fields for X, Y, and Strength:contentReference[oaicite:0]{index=0}  
- Buttons:  
  - **Add magnet** → adds magnet to list and updates scatter  
  - **Clear magnets** → removes all magnets and resets axes  
  - **Draw field lines** → computes and displays superposed field lines  
  - **Export image…** → saves current figure  
- Magnet list (QListWidget) showing added magnets  
- Status label with updates (e.g., “3 magnet(s) defined.”)  
- Hover tooltips: show coordinates and strength when mouse hovers over magnet markers:contentReference[oaicite:1]{index=1}  

**Algorithm / Implementation**  
- Field computed on grid (80 × 80, range ±5):contentReference[oaicite:2]{index=2}  
- For each magnet at (mx, my, strength):  
  - Compute dipole-like contributions:  
    - \(dx = X - mx\), \(dy = Y - my\), \(r^2 = dx^2 + dy^2\), \(r^5 = (r^2)^{2.5}\)  
    - \(B_x += -3·s·dx·dy / r^5\)  
    - \(B_y += s·(2dy^2 − dx^2) / r^5\)  
- Normalize vectors where |B| > 1e−14  
- Use `matplotlib.streamplot` to plot field lines  
- Overlay magnets with colored circles and text labels of strength  

**Units & Conversion**  
- Inputs and outputs are in arbitrary units (strength is unitless)  
- Spatial units: arbitrary (canvas scaled −5..+5 by default)  

**Edge Cases & Validation**  
- Input fields validated by regex (`[-+]?[0-9]*\.?[0-9]+`):contentReference[oaicite:3]{index=3}  
- Adding invalid values shows warning message  
- No magnets defined → draw attempt shows warning  
- Zero distance protected (`r^2=0` replaced by 1e−12)  

**Data Sources**  
- Purely computational, no external data  
- Logging via `core.data.functions.log.add_log_entry`:contentReference[oaicite:4]{index=4}  
- Export via `core.data.functions.image_export.export_figure`  

**Logging & Export**  
- Logs under tool = `"Magnoline"`:  
  - `"add_magnet"` with `{x,y,strength}`  
  - `"clear_magnets"` with `{count}`  
  - `"draw_field"` with `{magnets}`  
- Export creates PNG with suggested name `"magnoline_field"`  

**Chaining**  
- Outputs are visual; could integrate into electromagnetism suites or teaching modules  

**Tests**  
- Example 1: One magnet at (0,0), strength +1 → radial outward field lines  
- Example 2: Two magnets, +1 at (−1,0), −1 at (+1,0) → dipole field pattern  
- Example 3: Clear magnets → canvas reset to empty grid  
- Example 4: Hover mouse over magnet → tooltip shows coordinates and strength  

**Known Limitations / TODO**  
- Simple dipole-like model (not exact physics)  
- Strength is arbitrary scaling, not calibrated to real dipole moment  
- Only 2D visualization in XY plane  
- No dynamic dragging or interactive placement (manual entry only)  
- Could add saving/loading of magnet configurations  
- Could add field magnitude heatmap overlay  

---

### Tool: Ohm’s Law
**Category:** Electricity  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Solve for one of {Voltage V, Current I, Resistance R} given the other two, with basic unit selection.

**Inputs**  
- **Voltage V**: numeric + unit dropdown `{V, mV, kV}`  
- **Current I**: numeric + unit dropdown `{A, mA, kA}`  
- **Resistance R**: numeric + unit dropdown `{Ω, mΩ, kΩ, MΩ}`  
- Instruction label: “Enter any two; leave one blank.”

**Outputs**  
- Computed quantity shown as:  
  - `Voltage = … V` or  
  - `Current = … A` or  
  - `Resistance = … Ω`  
- Errors:  
  - `Fill exactly two fields.`  
  - `Invalid input.`

**UI & Interaction**  
- Three rows (V, I, R), each with a QLineEdit and QComboBox for units【:contentReference[oaicite:0]{index=0}】  
- Button **Solve** → performs calculation  
- Result QLabel displays the formatted answer or error【:contentReference[oaicite:1]{index=1}】

**Algorithm / Implementation**  
- Parse text fields; exactly two must be filled【:contentReference[oaicite:2]{index=2}】  
- Convert entered values to base units via `_to_base` (m→÷1000, k→×1000, MΩ→×1e6)【:contentReference[oaicite:3]{index=3}】  
- Compute using Ohm’s law:  
  - If V missing: `V = I · R`  
  - If I missing: `I = V / R`  
  - If R missing: `R = V / I`  
- Convert result back to the currently selected unit using `_from_base` and render with 6 sig figs【:contentReference[oaicite:4]{index=4}】  
- On exceptions (parse errors, divide-by-zero), show `Invalid input.`

**Units & Conversion**  
- Voltage: V, mV, kV  
- Current: A, mA, kA  
- Resistance: Ω, mΩ, kΩ, MΩ  
- Base units: V, A, Ω

**Edge Cases & Validation**  
- Must provide exactly two fields; otherwise → `Fill exactly two fields.`  
- Non-numeric input → `Invalid input.`  
- Division by zero (e.g., computing R or I with I=0) → caught as error → `Invalid input.`

**Data Sources**  
- None external; pure arithmetic with unit scaling【:contentReference[oaicite:5]{index=5}】

**Logging & Export**  
- Logs under tool = `"Ohm's Law"`:  
  - Action `"Solve"` with `{V, I, R}` in base units and computed `label`  
  - Action `"Error"` with `{msg}`【:contentReference[oaicite:6]{index=6}】  
- No file export

**Chaining**  
- Output value can feed into circuit helpers (e.g., power computations in other tools)

**Tests**  
- Example 1: I=2 A, R=5 Ω → V = **10 V**  
- Example 2: V=12 V, R=3 Ω → I = **4 A**  
- Example 3: V=5 V, I=2 mA → R = **2.5 kΩ**  
- Example 4: Only one or all three filled → `Fill exactly two fields.`  
- Example 5: I=0 A, V=5 V → division error → `Invalid input.`

**Known Limitations / TODO**  
- No direct power (P) computation; could add P=VI, P=I²R, P=V²/R  
- Limited unit set (no µ-prefixes)  
- No tolerance/uncertainty handling

---

### Tool: RC Circuit Helper
**Category:** Electricity / Circuits  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Visualize charging and discharging behavior of a capacitor in a simple RC circuit. Provides plots of capacitor voltage vs. time and highlights the characteristic time constant τ = R·C.

**Inputs**  
- **R (Ω)**: resistance (default 1000 Ω):contentReference[oaicite:0]{index=0}  
- **C (F)**: capacitance (default 0.00047 F):contentReference[oaicite:1]{index=1}  
- **V_in (V)**: input voltage for charging or initial voltage for discharging (default 5.0 V):contentReference[oaicite:2]{index=2}  
- **Mode**: dropdown: `Charging` or `Discharging`:contentReference[oaicite:3]{index=3}  
- **t_max (s)**: maximum simulation time (default 2.0 s):contentReference[oaicite:4]{index=4}

**Outputs**  
- Line plot of capacitor voltage vs. time  
- X-axis: time (s), Y-axis: voltage (V)  
- Title includes mode and computed time constant, e.g. `"Charging: τ = R·C = 0.47 s"`:contentReference[oaicite:5]{index=5}

**UI & Interaction**  
- Input fields for R, C, Vin, t_max, and mode selector  
- Buttons:  
  - **Plot** → computes curve and renders figure  
  - **Export Image…** → saves figure using `export_figure`:contentReference[oaicite:6]{index=6}  
- Embedded Matplotlib plot with toolbar  

**Algorithm / Implementation**  
- Compute time constant: `τ = R·C`:contentReference[oaicite:7]{index=7}  
- Generate time array: `t = np.linspace(0, tmax, 600)`  
- For charging:  
  - \( V(t) = V_{in} \cdot (1 - e^{-t/τ}) \)  
- For discharging:  
  - \( V(t) = V_{0} \cdot e^{-t/τ} \), with \(V_{0} = V_{in}\)  
- Plot curve with grid, labels, and title:contentReference[oaicite:8]{index=8}

**Units & Conversion**  
- R in ohms (Ω)  
- C in farads (F)  
- V in volts (V)  
- t in seconds (s)  
- τ displayed in seconds (s)  

**Edge Cases & Validation**  
- Non-numeric input → caught in exception → logged as error:contentReference[oaicite:9]{index=9}  
- Very small R or C → τ near zero, results in near-instant transition  
- Negative values accepted mathematically but physically nonsensical  

**Data Sources**  
- Pure exponential capacitor charge/discharge equations:contentReference[oaicite:10]{index=10}  
- Logging via `core.data.functions.log.add_log_entry`  
- Export via `core.data.functions.image_export.export_figure`  

**Logging & Export**  
- Logs under tool = `"RC Circuit Helper"`:  
  - Action = `"Plot"` with `{R, C, Vin, mode, tmax, tau}`  
  - Action = `"Error"` with `{msg}`:contentReference[oaicite:11]{index=11}  

**Chaining**  
- Output curve could be inputs to circuit timing calculators or oscillators  

**Tests**  
- Example 1: R=1000 Ω, C=0.00047 F, Vin=5 V, Charging, tmax=2 → exponential rise, τ≈0.47 s  
- Example 2: Same values, Discharging → exponential decay, τ≈0.47 s  
- Example 3: Negative R → still plots, τ negative → inverted exponential curve  
- Example 4: Invalid input (e.g., “abc”) → error logged  

**Known Limitations / TODO**  
- No interactive parameter sweeping (single plot only)  
- Ignores real-world effects (ESR, leakage, non-idealities)  
- Only single-stage RC circuit modeled  
- Could add marking of 63% and 37% points (τ reference)  

---

### Tool: Half-life Calculator
**Category:** Geology
**Version:** v1.0 (2025-08-22)

**Purpose**  
Simulate radioactive decay using half-life law. Plots the decay curve of a sample over a given time span and reports the final quantity.

**Inputs**  
- **Initial quantity (N₀)**: starting amount of substance:contentReference[oaicite:0]{index=0}  
- **Half-life (t½)**: decay constant in same time units as simulation:contentReference[oaicite:1]{index=1}  
- **Total time span (T)**: duration for simulation:contentReference[oaicite:2]{index=2}

**Outputs**  
- Line plot of N(t) vs. time  
- X-axis: Time (user’s input units)  
- Y-axis: Quantity remaining  
- Label showing `N(T) = …` at the end of simulation:contentReference[oaicite:3]{index=3}

**UI & Interaction**  
- Input fields for N₀, t½, and T  
- Button **Compute** → runs decay calculation and updates plot  
- Embedded Matplotlib plot with navigation toolbar:contentReference[oaicite:4]{index=4}  
- Result QLabel shows computed remaining amount

**Algorithm / Implementation**  
- Uses helper `half_life_decay(N0, t, hl)` from `core.data.functions.geo_utils`:contentReference[oaicite:5]{index=5}  
- Build timeline: `t = np.linspace(0, T, 400)`  
- Compute values: `y = [half_life_decay(N0, ti, hl) for ti in t]`  
- Plot `y` vs. `t` with grid and tight layout  
- Display final value at `t = T`  
- Log success with `{"N0", "hl", "T", "NT"}`  

**Units & Conversion**  
- No explicit unit conversion (inputs interpreted consistently)  
- Time units must be consistent between half-life and total span  
- Quantity is unitless (scales with N₀)

**Edge Cases & Validation**  
- Half-life ≤ 0 or total time ≤ 0 → error raised:contentReference[oaicite:6]{index=6}  
- Non-numeric input → error shown as `"Invalid input."`  
- Handles both large and small values of N₀ correctly  

**Data Sources**  
- Physics: exponential decay law via half-life relation  
- Logging via `core.data.functions.log.add_log_entry`:contentReference[oaicite:7]{index=7}

**Logging & Export**  
- Logs under tool = `"Half-life Calculator (Decay vs Time)"`:  
  - Action = `"Compute"` with `{N0, hl, T, NT}`  
  - Action = `"Error"` with `{msg}`:contentReference[oaicite:8]{index=8}  
- No figure export implemented  

**Chaining**  
- Output curve could feed into radiation dose estimators or activity calculators  

**Tests**  
- Example 1: N₀=100, hl=5, T=20 → curve falls to ~6.25 at t=20  
- Example 2: hl=10, T=10 → final N(T) ≈ N₀/2  
- Example 3: hl ≤ 0 → error `"Invalid input."`  
- Example 4: Non-numeric input → error  

**Known Limitations / TODO**  
- Only single decay process modeled (no chains or branching)  
- No uncertainty or error propagation  
- No export of computed curve data  
- Could add option for multiple half-lives / parallel isotopes  

---

### Tool: Mineral Explorer
**Category:** Geology
**Version:** v1.0 (2025-08-22)

**Purpose**  
Browse, search, and filter a mineral database by name, formula, system, hardness, specific gravity, and type. Supports marking favourites and copying rows.

**Inputs**  
- Search query: free-text filter (matches name, formula, system, notes, type):contentReference[oaicite:0]{index=0}  
- Type filter: dropdown (default “All Types”, populated dynamically from dataset):contentReference[oaicite:1]{index=1}  
- Favourites only: checkbox to restrict to starred minerals:contentReference[oaicite:2]{index=2}

**Outputs**  
- Table of minerals with 6 columns:  
  - ★ (favourite toggle)  
  - Name  
  - Formula  
  - Hardness (numeric, red if ≥7)  
  - SG (specific gravity, blue if ≥4)  
  - System (crystal system):contentReference[oaicite:3]{index=3}  
- Status label showing “X / Y rows”:contentReference[oaicite:4]{index=4}

**UI & Interaction**  
- Top filter bar: search box, type dropdown, favourites checkbox, refresh button:contentReference[oaicite:5]{index=5}  
- Table view: non-editable, row-select, sortable, with coloured hardness/SG cells:contentReference[oaicite:6]{index=6}  
- Bottom bar:  
  - **Toggle Favourite** button  
  - **Copy Row** button (copies selected row to clipboard as tab-separated text)  
  - Status label:contentReference[oaicite:7]{index=7}

**Algorithm / Implementation**  
- Data loaded with `load_minerals()`; favourites loaded via `load_favs()`:contentReference[oaicite:8]{index=8}  
- Debounced rebuild (200 ms) on text change to avoid lag:contentReference[oaicite:9]{index=9}  
- `_match` checks query against multiple fields (name, formula, system, notes, type):contentReference[oaicite:10]{index=10}  
- `_rebuild` applies filters and repopulates table with matching rows:contentReference[oaicite:11]{index=11}  
- Favourites toggled via set + persisted with `save_favs()`:contentReference[oaicite:12]{index=12}  
- Copy row grabs all columns and writes to clipboard:contentReference[oaicite:13]{index=13}

**Units & Conversion**  
- Hardness: Mohs scale (dimensionless)  
- SG: dimensionless ratio (approximate density / water)  
- No unit conversions—values taken directly from dataset:contentReference[oaicite:14]{index=14}

**Edge Cases & Validation**  
- Missing/empty values gracefully shown as blank:contentReference[oaicite:15]{index=15}  
- Invalid floats handled with `_num()` (safe parse with `replace(",", ".")`):contentReference[oaicite:16]{index=16}  
- Case-insensitive substring search  
- If no rows match → table empty, status `0 / N rows`  

**Data Sources**  
- Mineral database via `core.data.functions.geo_utils.load_minerals()`  
- Favourites persisted via `load_favs()` / `save_favs()`:contentReference[oaicite:17]{index=17}

**Logging & Export**  
- No explicit logging in this tool  
- No image export  

**Chaining**  
- Designed as a database browser, not computation output  
- Could feed selected minerals into related chemistry or crystallography tools  

**Tests**  
- Example 1: Search “quartz” → filters to quartz row, shows SG≈2.65, Hardness=7 (red)  
- Example 2: Enable “Favourites only” after starring one mineral → only that mineral remains  
- Example 3: Select a row → Copy Row → tab-separated text in clipboard  
- Example 4: Change Type dropdown to “Silicate” → filters to silicate minerals  

**Known Limitations / TODO**  
- No direct link to external databases (offline only)  
- Favourites stored by name only (case-sensitive match)  
- No sorting persistence across sessions  
- No advanced filters (e.g., numeric ranges for SG/hardness)  

---

### Tool: Mineral Identifier
**Category:** Geology
**Version:** v1.0 (2025-08-22)

**Purpose**  
Assist with identifying unknown minerals by comparing input hardness, specific gravity, and crystal system against a mineral database. Provides a ranked list of candidate minerals and visual scatter plot.

**Inputs**  
- **Hardness (Mohs)**: numeric input (float, optional):contentReference[oaicite:0]{index=0}  
- **Specific Gravity (SG / Density)**: numeric input (float, optional):contentReference[oaicite:1]{index=1}  
- **Crystal system**: text input (partial match, e.g. “hexagonal”):contentReference[oaicite:2]{index=2}  

**Outputs**  
- Table of up to 200 best matches, with columns:  
  - Name  
  - Formula  
  - Hardness (red if ≥7)  
  - SG (blue if ≥4)  
  - Crystal system:contentReference[oaicite:3]{index=3}  
- Scatter plot of Hardness vs. SG for candidate minerals:contentReference[oaicite:4]{index=4}  
- Top ~10% highlighted in the scatter plot (larger markers with outline):contentReference[oaicite:5]{index=5}

**UI & Interaction**  
- Filter row with input fields and “Find matches” button:contentReference[oaicite:6]{index=6}  
- Non-editable, sortable table view with selectable rows:contentReference[oaicite:7]{index=7}  
- Embedded Matplotlib scatter plot with navigation toolbar:contentReference[oaicite:8]{index=8}  
- On launch, shows all minerals with at least one numeric property so interface is never empty:contentReference[oaicite:9]{index=9}

**Algorithm / Implementation**  
- `_parse_float`: safely parse float, handling commas:contentReference[oaicite:10]{index=10}  
- `_score_row`: scoring function combining similarity to input hardness, SG, and partial match of system:contentReference[oaicite:11]{index=11}  
  - Hardness/SG score = 1 / (1 + abs(diff))  
  - System adds +0.5 if prefix matches (case-insensitive)  
- Sort candidates by descending score, keep top 200:contentReference[oaicite:12]{index=12}  
- Highlight mask marks best 10% of matches in plot:contentReference[oaicite:13]{index=13}

**Units & Conversion**  
- Hardness: Mohs scale (dimensionless)  
- SG: dimensionless ratio (relative density)  
- Crystal system: string label  
- No conversions beyond float parsing of numeric values:contentReference[oaicite:14]{index=14}

**Edge Cases & Validation**  
- If no filters → display all minerals with numeric values:contentReference[oaicite:15]{index=15}  
- Non-numeric input ignored (treated as None):contentReference[oaicite:16]{index=16}  
- Missing dataset values shown as blank  
- If no matches → empty table and blank plot message  

**Data Sources**  
- Mineral dataset loaded via `core.data.functions.geo_utils.load_minerals()`:contentReference[oaicite:17]{index=17}  
- Logging via `core.data.functions.log.add_log_entry`:contentReference[oaicite:18]{index=18}

**Logging & Export**  
- Logs under tool = `"Mineral Identifier"`:  
  - Action = `"BrowseAll"` with `{rows}` when showing all minerals  
  - Action = `"Identify"` with `{filters, matched}` when filtering:contentReference[oaicite:19]{index=19}  
- No export feature  

**Chaining**  
- Output candidates could be linked into Mineral Explorer for deeper lookup  
- Not directly chainable to numerical calculators  

**Tests**  
- Example 1: Hardness=7, SG≈2.65, System=“hex” → Quartz among top matches  
- Example 2: Only SG=5 entered → dense minerals like magnetite and galena appear  
- Example 3: No inputs → all rows with hardness or SG shown  
- Example 4: Invalid input “abc” in hardness → ignored  

**Known Limitations / TODO**  
- Scoring is approximate; does not handle compositional ranges well  
- No option to combine multiple crystal systems  
- No direct links to mineral images or external resources  
- Could enhance with probabilistic scoring or error bars  

---

### Tool: Plate Boundary Designer
**Category:** Geology
**Version:** v1.0 (2025-08-22)

**Purpose**  
Provide schematic diagrams of different plate boundary types (convergent, divergent, transform). Intended for quick visualisation and teaching reference.

**Inputs**  
- **Boundary Type**: dropdown selector with options:  
  - Convergent  
  - Divergent  
  - Transform:contentReference[oaicite:0]{index=0}  

**Outputs**  
- Diagram showing two tectonic plates and characteristic features for the selected boundary type:  
  - Convergent: trench and volcanic arc:contentReference[oaicite:1]{index=1}  
  - Divergent: mid-ocean ridge:contentReference[oaicite:2]{index=2}  
  - Transform: fault with opposing arrows:contentReference[oaicite:3]{index=3}  

**UI & Interaction**  
- Dropdown to select boundary type  
- **Draw** button → generates and displays the schematic:contentReference[oaicite:4]{index=4}  
- **Export Diagram…** button → saves current figure via export utility:contentReference[oaicite:5]{index=5}  
- Embedded Matplotlib figure with navigation toolbar  

**Algorithm / Implementation**  
- Base plates represented as coloured rectangles:contentReference[oaicite:6]{index=6}  
- Arrows drawn with `FancyArrow` to indicate motion direction  
- Labels (e.g., “Volcano”, “Ridge”, “Fault”) added with `ax.text`  
- Layout adjusted with `tight_layout()`, then canvas redrawn:contentReference[oaicite:7]{index=7}  
- Export handled by `core.data.functions.image_export.export_figure`  

**Units & Conversion**  
- Not applicable (schematic only, no numeric scale)  

**Edge Cases & Validation**  
- If export fails, error logged via `add_log_entry` with message:contentReference[oaicite:8]{index=8}  
- No input validation required beyond dropdown selection  

**Data Sources**  
- Static schematic templates defined in code  
- Logging via `core.data.functions.log.add_log_entry`:contentReference[oaicite:9]{index=9}  

**Logging & Export**  
- Logs under tool = `"Plate Boundary Designer"`:  
  - Action = `"Draw"` with `{kind}`  
  - Action = `"ExportImage"` with `{path}`  
  - Action = `"ExportError"` with `{msg}`:contentReference[oaicite:10]{index=10}  

**Chaining**  
- None (visual-only reference tool)  

**Tests**  
- Example 1: Select “Convergent” → trench and volcano drawn, “Draw” logged  
- Example 2: Select “Divergent” → ridge drawn, “Draw” logged  
- Example 3: Select “Transform” → fault line drawn, “Draw” logged  
- Example 4: Export → file saved, log entry with path  
- Example 5: Simulated export error → error logged with message  

**Known Limitations / TODO**  
- Schematic only; not to scale and lacks quantitative data  
- No user control over plate size, colour, or annotations  
- Could be expanded with more boundary types (e.g. oblique, triple junctions)  

---

### Tool: Plate Velocity Calculator
**Category:** Geology  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Compute average plate velocity from distance travelled and elapsed geological time. Provides quick conversion into standard unit of mm/yr.

**Inputs**  
- **Distance (km)**: separation or displacement in kilometres:contentReference[oaicite:0]{index=0}  
- **Time (million years)**: geological timescale in Myr:contentReference[oaicite:1]{index=1}

**Outputs**  
- Single result: `Velocity: … mm/yr`:contentReference[oaicite:2]{index=2}  

**UI & Interaction**  
- Two input fields: distance (km) and time (Myr)  
- **Compute** button → calculates and displays velocity:contentReference[oaicite:3]{index=3}  
- Result label shows velocity in mm/yr, 3 significant figures  
- Errors displayed as `"Invalid input."`  

**Algorithm / Implementation**  
- Parse floats from text boxes  
- Formula:  
  - \( v_{mm/yr} = \frac{d_{km}}{t_{Myr}} \)  
  - Conversion: 1 km / 1 Myr = 1 mm/yr:contentReference[oaicite:4]{index=4}  
- Handles division by zero → returns `inf`  
- Logs success with `{d_km, t_ma, v_mm_yr}`  

**Units & Conversion**  
- Distance: kilometres (km)  
- Time: million years (Myr)  
- Output velocity: millimetres per year (mm/yr):contentReference[oaicite:5]{index=5}

**Edge Cases & Validation**  
- Non-numeric input → error message and error logged:contentReference[oaicite:6]{index=6}  
- Time = 0 → velocity = ∞ (infinite)  
- Negative values accepted, though geologically nonsensical  

**Data Sources**  
- Simple unit conversion principle: 1 km / 1 Myr = 1 mm/yr  
- Logging via `core.data.functions.log.add_log_entry`:contentReference[oaicite:7]{index=7}

**Logging & Export**  
- Logs under tool = `"Plate Velocity Calculator"`:  
  - Action = `"Compute"` with `{d_km, t_ma, v_mm_yr}`  
  - Action = `"Error"` with `{msg}`:contentReference[oaicite:8]{index=8}  
- No export or plotting  

**Chaining**  
- Could chain into tectonics visualisation tools or seismic models  

**Tests**  
- Example 1: d=1000 km, t=50 Myr → v=20 mm/yr  
- Example 2: d=4500 km, t=90 Myr → v=50 mm/yr  
- Example 3: t=0 → ∞ mm/yr  
- Example 4: invalid input (“abc”) → “Invalid input.”  

**Known Limitations / TODO**  
- No error bars or uncertainty handling  
- No support for multiple stages of motion  
- No plot of velocity vs. time  
- Could add direct conversion into cm/yr for alternative convention  

---

### Tool: Radioactive Dating
**Category:** Geology  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Estimate the age of rocks or fossils from radioactive isotope data. Provides both direct numerical age estimation and a plotted decay curve for visualisation.

**Inputs**  
- **Half-life (years)**: numeric input, may be entered manually or set via preset button:contentReference[oaicite:0]{index=0}  
- **Remaining (%) [0–100]**: proportion of parent isotope still present:contentReference[oaicite:1]{index=1}  
- **Presets**: quick buttons with standard isotopes:  
  - Carbon-14 (5730 y)  
  - Potassium-40 (1.248×10⁹ y)  
  - Uranium-235 (7.038×10⁸ y)  
  - Uranium-238 (4.468×10⁹ y)  
  - Rubidium-87 (4.88×10¹⁰ y):contentReference[oaicite:2]{index=2}

**Outputs**  
- Estimated age in years, formatted with 3 significant figures and comma separators:contentReference[oaicite:3]{index=3}  
- Decay curve plot showing fractional parent isotope vs. time:contentReference[oaicite:4]{index=4}

**UI & Interaction**  
- Input boxes for half-life and percentage remaining  
- **Estimate Age** button → computes and displays numerical age:contentReference[oaicite:5]{index=5}  
- **Plot Decay Curve** button → generates exponential decay plot:contentReference[oaicite:6]{index=6}  
- Preset isotope buttons insert half-life values into field for quick setup  
- Embedded Matplotlib plot with toolbar  

**Algorithm / Implementation**  
- Age estimation via `estimate_age_from_remaining(fraction, half_life)`:contentReference[oaicite:7]{index=7}  
- Fraction = percentage / 100  
- Decay curve:  
  - `t = np.linspace(0, 10 * half_life, 400)`  
  - `y = (0.5) ** (t / half_life)`:contentReference[oaicite:8]{index=8}  
- Plot: labelled axes, grid, title “Exponential Decay”  

**Units & Conversion**  
- Half-life input and time axis in years  
- Percentage converted to fraction (0–1) internally  
- Output age in years  

**Edge Cases & Validation**  
- Invalid or missing input → “Invalid input.” displayed, error logged:contentReference[oaicite:9]{index=9}  
- Plotting requires valid half-life; otherwise warning shown:contentReference[oaicite:10]{index=10}  
- No handling for uncertainty or multiple decay chains  

**Data Sources**  
- Isotope half-lives: hard-coded presets  
- Age calculation from decay law via `geo_utils.estimate_age_from_remaining`:contentReference[oaicite:11]{index=11}  
- Logging through `core.data.functions.log.add_log_entry`  

**Logging & Export**  
- Logs under tool = `"Radioactive Dating"`:  
  - Action = `"Estimate"` with `{half_life, remaining_pct, age}`  
  - Action = `"Error"` with `{msg}`  
  - Action = `"PlotDecay"` with `{half_life}`:contentReference[oaicite:12]{index=12}  
- No image export  

**Chaining**  
- Estimated age could be used in geological history modelling or cross-referenced with fossil records  

**Tests**  
- Example 1: Half-life=5730 y, Remaining=50% → age ≈ 5730 y  
- Example 2: Half-life=1.248e9 y, Remaining=25% → age ≈ 2.496e9 y  
- Example 3: Invalid input (“abc”) → “Invalid input.” displayed, error logged  
- Example 4: Press Plot without valid half-life → “Enter a valid half-life first.”  

**Known Limitations / TODO**  
- No error propagation or confidence interval handling  
- Only single isotope decay (no decay chains)  
- Presets limited to five isotopes  
- Could add support for inputting daughter/parent ratios directly  

---

### Tool: Algebraic Calculator
**Category:** Mathematics  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Evaluate algebraic functions of a single variable \(x\) at specified numeric values. Built for quick symbolic entry and numerical evaluation.

**Inputs**  
- **Function of x**: text expression, SymPy-compatible (e.g. `x**2 + 3*x - 2`):contentReference[oaicite:0]{index=0}  
- **Value of x**: numeric input (float):contentReference[oaicite:1]{index=1}

**Outputs**  
- Result displayed as formatted string: `f(x) = value`:contentReference[oaicite:2]{index=2}  
- Error message `"Error with the function or x."` if parsing/evaluation fails:contentReference[oaicite:3]{index=3}

**UI & Interaction**  
- Function input box (QLineEdit)  
- Value input box (QLineEdit)  
- **Calculate** button → computes and displays result:contentReference[oaicite:4]{index=4}  
- Result label displays output or error message  

**Algorithm / Implementation**  
- Parse function using `sympy.sympify`:contentReference[oaicite:5]{index=5}  
- Define symbol \(x\) via `sp.Symbol('x')`  
- Substitute given numeric value and evaluate with `.evalf()`  
- On success: display result and log calculation  
- On error: display error message and log exception:contentReference[oaicite:6]{index=6}

**Units & Conversion**  
- Dimensionless numbers (no units)  

**Edge Cases & Validation**  
- Invalid function syntax → error displayed and logged:contentReference[oaicite:7]{index=7}  
- Non-numeric value of \(x\) → error displayed and logged:contentReference[oaicite:8]{index=8}  
- Empty inputs → error displayed  

**Data Sources**  
- Function parsing and evaluation via SymPy  
- Logging via `core.data.functions.log.add_log_entry`:contentReference[oaicite:9]{index=9}

**Logging & Export**  
- Logs under tool = `"Algebraic Calculator"`:  
  - Action = `"Calculate"` with `{expr, x, result}`  
  - Action = `"Error"` with `{expr, x, msg}`:contentReference[oaicite:10]{index=10}  
- No export or plotting  

**Chaining**  
- Outputs can feed into further mathematical tools for function analysis (roots, derivatives, etc.)  

**Tests**  
- Example 1: `f(x)=x**2+3*x-2, x=2` → `f(2.0) = 8.0`  
- Example 2: `f(x)=sin(x), x=3.14` → `f(3.14) ≈ 0.00159`  
- Example 3: `f(x)=invalid, x=2` → error message displayed  
- Example 4: `f(x)=x**2, x=abc` → error message displayed  

**Known Limitations / TODO**  
- Single-variable only (no multivariate input)  
- Limited error handling and syntax guidance  
- No symbolic simplification or step-by-step output  
- Could add support for derivative/integral evaluation  

---

### Tool: Function Plotter
**Category:** Mathematics  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Plot mathematical functions of a single variable \(x\) over a defined interval. Built for quick visualisation of algebraic or trigonometric expressions.

**Inputs**  
- **Function of x**: text expression (SymPy-compatible, e.g. `x**2 + 3*x - 2`):contentReference[oaicite:0]{index=0}  
- **xmin**: lower bound of domain (default −10):contentReference[oaicite:1]{index=1}  
- **xmax**: upper bound of domain (default 10):contentReference[oaicite:2]{index=2}

**Outputs**  
- 2D line plot of \(y=f(x)\) across the interval [xmin, xmax]  
- Axes labelled “x” and “y”  
- Title shows the input expression:contentReference[oaicite:3]{index=3}

**UI & Interaction**  
- Input field for function of x  
- Two fields for xmin and xmax (with placeholder defaults)  
- Buttons:  
  - **Plot** → generates plot  
  - **Export Image…** → saves figure:contentReference[oaicite:4]{index=4}  
- Embedded Matplotlib canvas with navigation toolbar  

**Algorithm / Implementation**  
- Parse expression using `sympy.sympify`  
- Symbolic variable defined as \(x\)  
- Function converted to NumPy lambda via `lambdify`  
- Generate 1000 evenly spaced points with `numpy.linspace(xmin, xmax)`  
- Compute \(y=f(x)\), plot using Matplotlib:contentReference[oaicite:5]{index=5}  
- Logs success or error with inputs and bounds  

**Units & Conversion**  
- Dimensionless (no units handled)  

**Edge Cases & Validation**  
- Non-numeric or missing bounds → defaults to [−10, 10]  
- If xmin ≥ xmax → resets to defaults [−10, 10]:contentReference[oaicite:6]{index=6}  
- Invalid function expression → plot cleared, error logged:contentReference[oaicite:7]{index=7}  

**Data Sources**  
- Expression parsing via SymPy  
- Logging via `core.data.functions.log.add_log_entry`  
- Export via `core.data.functions.image_export.export_figure`:contentReference[oaicite:8]{index=8}

**Logging & Export**  
- Logs under tool = `"Function Plotter"`:  
  - Action = `"Plot"` with `{expr, xmin, xmax}`  
  - Action = `"Error"` with `{expr, msg}`  
  - Action = `"ExportImage"` with `{path}`  
  - Action = `"ExportError"` with `{msg}`:contentReference[oaicite:9]{index=9}  

**Chaining**  
- Output figure is visual-only, no direct chaining  
- Expression text could be reused in analysis tools (e.g., derivative or root solvers)  

**Tests**  
- Example 1: expr=`x**2`, bounds −5 to 5 → parabola plotted  
- Example 2: expr=`sin(x)`, bounds 0 to 6.28 → sine wave plotted  
- Example 3: expr=`invalid`, bounds −10 to 10 → error logged, blank plot  
- Example 4: xmin=10, xmax=−5 → reset to defaults −10 to 10  

**Known Limitations / TODO**  
- Only single-variable functions supported  
- No axis scaling, multiple functions, or styling options  
- No support for discontinuous plots (e.g., asymptotes)  
- Future version planned with advanced error handling and customisation:contentReference[oaicite:10]{index=10}  

---

### Tool: Quadratic Solver
**Category:** Mathematics  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Solve quadratic equations of the form \(ax^2 + bx + c = 0\). Provides symbolic solutions via SymPy.

**Inputs**  
- **a**: coefficient of \(x^2\):contentReference[oaicite:0]{index=0}  
- **b**: coefficient of \(x\):contentReference[oaicite:1]{index=1}  
- **c**: constant term:contentReference[oaicite:2]{index=2}

**Outputs**  
- Solutions displayed as: `Solutions: [sol₁, sol₂]`  
- If invalid input: `"Invalid input."`:contentReference[oaicite:3]{index=3}

**UI & Interaction**  
- Three input fields for coefficients a, b, c  
- **Solve** button → computes solutions:contentReference[oaicite:4]{index=4}  
- Result label shows solutions or error  

**Algorithm / Implementation**  
- Coefficients converted to floats  
- Symbolic variable \(x\) created with SymPy  
- Polynomial constructed as \(A x^2 + B x + C\)  
- `sympy.solve` used to compute solutions:contentReference[oaicite:5]{index=5}  
- Solutions returned as real or complex values depending on discriminant  
- Logs results or errors with coefficients and solutions  

**Units & Conversion**  
- Purely mathematical, no units  

**Edge Cases & Validation**  
- Invalid numeric input → error message logged:contentReference[oaicite:6]{index=6}  
- a=0 → tool still attempts linear solve, handled by SymPy  
- Complex solutions supported automatically  

**Data Sources**  
- Symbolic solving via SymPy:contentReference[oaicite:7]{index=7}  
- Logging via `core.data.functions.log.add_log_entry`  

**Logging & Export**  
- Logs under tool = `"Quadratic Solver"`:  
  - Action = `"Solve"` with `{a, b, c, solutions}`  
  - Action = `"Error"` with `{a, b, c, msg}`:contentReference[oaicite:8]{index=8}  
- No export  

**Chaining**  
- Solutions could be reused in further symbolic or numeric analysis tools  

**Tests**  
- Example 1: a=1, b=−3, c=2 → Solutions: [1, 2]  
- Example 2: a=1, b=0, c=−4 → Solutions: [−2, 2]  
- Example 3: a=1, b=2, c=5 → Solutions: [−1−2i, −1+2i]  
- Example 4: invalid input (“abc”) → “Invalid input.”  

**Known Limitations / TODO**  
- Only one equation at a time  
- No step-by-step derivation or discriminant shown  
- Coefficients must be entered manually (no parsing from equation form)  
- Planned advanced version with complex roots and detailed explanation:contentReference[oaicite:9]{index=9}  

---

### Tool: Triangle Side Solver (Pythagorean)
**Category:** Mathematics  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Solve right-angled triangles using the Pythagorean theorem. Computes the unknown side length when two sides are provided.

**Inputs**  
- **a**: first leg of the triangle:contentReference[oaicite:0]{index=0}  
- **b**: second leg of the triangle:contentReference[oaicite:1]{index=1}  
- **c**: hypotenuse (longest side):contentReference[oaicite:2]{index=2}

**Outputs**  
- Computed missing side, formatted as `side = value`  
- Error message if more or fewer than one side is missing:contentReference[oaicite:3]{index=3}

**UI & Interaction**  
- Three input fields for a, b, c  
- Instruction label: “Leave the unknown side blank. a² + b² = c²”  
- **Solve** button → calculates missing side:contentReference[oaicite:4]{index=4}  
- Result displayed in label  

**Algorithm / Implementation**  
- If c empty → compute \(c = \sqrt{a^2 + b^2}\)  
- If a empty → compute \(a = \sqrt{c^2 - b^2}\)  
- If b empty → compute \(b = \sqrt{c^2 - a^2}\)  
- If none or more than one blank → show error message  
- All computations wrapped in `try/except` → invalid input handled gracefully:contentReference[oaicite:5]{index=5}

**Units & Conversion**  
- Purely numerical, no units enforced  

**Edge Cases & Validation**  
- Non-numeric input → “Invalid input.”  
- Negative or invalid square root → error message  
- Leaving none or more than one blank field → “Leave exactly one field blank.”:contentReference[oaicite:6]{index=6}

**Data Sources**  
- Pythagorean theorem  
- Logging via `core.data.functions.log.add_log_entry`:contentReference[oaicite:7]{index=7}

**Logging & Export**  
- Logs under tool = `"Triangle Side Solver (Pythagorean)"`:  
  - Action = `"Solve"` with `{a, b, c, msg}`  
  - Action = `"Error"` with `{a, b, c, msg}`:contentReference[oaicite:8]{index=8}  
- No export  

**Chaining**  
- Outputs (side lengths) could be reused in geometry tools for further calculations  

**Tests**  
- Example 1: a=3, b=4, c= → c=5  
- Example 2: a=, b=4, c=5 → a=3  
- Example 3: a=3, b=, c=5 → b=4  
- Example 4: a=3, b=4, c=5 → error “Leave exactly one field blank.”  
- Example 5: invalid input (“abc”) → “Invalid input.”  

**Known Limitations / TODO**  
- Only handles right-angled triangles  
- No coordinate geometry, angles, or area calculation (planned for advanced solver):contentReference[oaicite:9]{index=9}  
- No handling of units or scaling  

---

### Tool: Vector Calculator
**Category:** Mathematics  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Perform basic vector operations (dot product, cross product, angle between vectors, magnitude, normalisation) with optional 3D visualisation.

**Inputs**  
- **Vector A**: comma-separated numbers (e.g., `1,2,3`):contentReference[oaicite:0]{index=0}  
- **Vector B**: comma-separated numbers (optional, depending on operation):contentReference[oaicite:1]{index=1}  
- **Operation**: selected from dropdown:  
  - Dot Product  
  - Cross Product (3D)  
  - Angle Between  
  - Magnitude of A  
  - Magnitude of B  
  - Normalise A  
  - Normalise B:contentReference[oaicite:2]{index=2}

**Outputs**  
- Result displayed as formatted string (numeric or vector):contentReference[oaicite:3]{index=3}  
- Optional 3D vector plot (if A, B, or result are 3D vectors):contentReference[oaicite:4]{index=4}  
- Error messages if input invalid  

**UI & Interaction**  
- Dropdown menu for operation  
- Two text fields for A and B  
- **Calculate** button → runs operation  
- Result label for textual output  
- Embedded 3D Matplotlib canvas + toolbar  
- **Export Image…** button → saves current plot:contentReference[oaicite:5]{index=5}

**Algorithm / Implementation**  
- Input parsing via `_parse_vec`, converting comma-separated text into NumPy arrays:contentReference[oaicite:6]{index=6}  
- Operation handling:  
  - Dot Product: `np.dot(A,B)`  
  - Cross Product: `np.cross(A,B)` (3D only)  
  - Angle: \(\arccos(\frac{A·B}{|A||B|})\) in degrees  
  - Magnitude: `np.linalg.norm(A)` or `np.linalg.norm(B)`  
  - Normalisation: `A/|A|` or `B/|B|`:contentReference[oaicite:7]{index=7}  
- Results formatted to 6 significant figures  
- If 3D vectors: plot quivers in 3D axes:contentReference[oaicite:8]{index=8}

**Units & Conversion**  
- Pure numbers, no unit handling  

**Edge Cases & Validation**  
- Empty input → error “Vector A/B required”:contentReference[oaicite:9]{index=9}  
- Different dimensions for dot/angle → error  
- Cross product requires exactly 3D vectors  
- Normalising zero vector → error  
- Angle with zero vector → error  
- Invalid number format → error:contentReference[oaicite:10]{index=10}

**Data Sources**  
- NumPy for linear algebra  
- Matplotlib for plotting  
- Logging via `core.data.functions.log.add_log_entry`  
- Export via `core.data.functions.image_export.export_figure`:contentReference[oaicite:11]{index=11}

**Logging & Export**  
- Logs under tool = `"Vector Calculator"`:  
  - Action = `"Calculate"` with `{op, A, B, result}`  
  - Action = `"Error"` with `{op, A, B, msg}`  
  - Action = `"ExportImage"` with `{path}`  
  - Action = `"ExportError"` with `{msg}`:contentReference[oaicite:12]{index=12}

**Chaining**  
- Outputs (dot product, angle, magnitude, normalised vectors) can feed into other mathematical tools  

**Tests**  
- Example 1: A=`1,0,0`, B=`0,1,0`, op=Dot → Result: 0  
- Example 2: A=`1,0,0`, B=`0,1,0`, op=Cross → Result: [0,0,1]  
- Example 3: A=`1,0,0`, B=`1,0,0`, op=Angle → Result: 0°  
- Example 4: A=`3,4`, op=Magnitude of A → |A|=5  
- Example 5: A=`0,0,0`, op=Normalise A → error  
- Example 6: invalid input “1, a, 3” → error  

**Known Limitations / TODO**  
- Limited to two vectors  
- No advanced operations (projection, scalar triple product, etc.)  
- Visualisation simplistic (basic quiver plot)  
- Planned advanced version with improved 2D/3D visualisation and expanded functionality:contentReference[oaicite:13]{index=13}  

---

### Tool: Acceleration Calculator
**Category:** Mechanics  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Compute average acceleration from change in velocity (Δv) and time (t).

**Inputs**  
- **Δv**: numeric value of velocity change:contentReference[oaicite:0]{index=0}  
- **Δv unit**: selectable → m/s, km/h, mph:contentReference[oaicite:1]{index=1}  
- **t**: numeric value of elapsed time:contentReference[oaicite:2]{index=2}  
- **t unit**: selectable → s, min, hr:contentReference[oaicite:3]{index=3}

**Outputs**  
- Acceleration displayed as `a = value m/s²` with 6 significant figures:contentReference[oaicite:4]{index=4}  
- Error message `"Invalid input."` if input parsing or division fails:contentReference[oaicite:5]{index=5}

**UI & Interaction**  
- Two input rows: Δv with unit dropdown, t with unit dropdown  
- **Compute** button → calculates acceleration:contentReference[oaicite:6]{index=6}  
- Result shown in label  

**Algorithm / Implementation**  
- Convert Δv:  
  - km/h → ÷3.6  
  - mph → ×0.44704:contentReference[oaicite:7]{index=7}  
- Convert t:  
  - min → ×60  
  - hr → ×3600:contentReference[oaicite:8]{index=8}  
- Compute \(a = \frac{Δv}{t}\)  
- If t=0 → raises error  
- Logs both success and error states with input/output data:contentReference[oaicite:9]{index=9}

**Units & Conversion**  
- Standard SI output: m/s²  
- Input supported in m/s, km/h, mph for Δv; s, min, hr for t  

**Edge Cases & Validation**  
- Non-numeric input → error displayed and logged  
- t=0 → division error handled:contentReference[oaicite:10]{index=10}  
- Empty input fields → error  

**Data Sources**  
- Standard conversion factors  
- Logging via `core.data.functions.log.add_log_entry`:contentReference[oaicite:11]{index=11}

**Logging & Export**  
- Logs under tool = `"Acceleration"`:  
  - Action = `"Compute"` with `{dv_ms, t_s, a}`  
  - Action = `"Error"` with `{msg}`:contentReference[oaicite:12]{index=12}  
- No export  

**Chaining**  
- Output acceleration can feed into motion or force calculators (e.g., Newton’s 2nd law)  

**Tests**  
- Example 1: Δv=10 m/s, t=5 s → a=2.0 m/s²  
- Example 2: Δv=36 km/h, t=10 s → Δv=10 m/s, a=1.0 m/s²  
- Example 3: Δv=22.37 mph, t=10 s → Δv≈10 m/s, a≈1.0 m/s²  
- Example 4: Δv=10 m/s, t=0 → error  

**Known Limitations / TODO**  
- Only handles constant acceleration (average)  
- No distance or velocity integration  
- Limited input unit set  
- Future expansion: include full kinematics solver (SUVAT)  

---

### Tool: Drag Force Calculator
**Category:** Mechanics  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Calculate the aerodynamic drag force on an object using the drag equation:  
\[
F_d = \tfrac{1}{2} \, \rho \, v^2 \, C_d \, A
\]  

**Inputs**  
- **ρ (air density)**: numeric value:contentReference[oaicite:0]{index=0}  
  - Units: kg/m³, g/cm³  
- **v (velocity)**: numeric value:contentReference[oaicite:1]{index=1}  
  - Units: m/s, km/h, mph  
- **C_d (drag coefficient)**: dimensionless:contentReference[oaicite:2]{index=2}  
- **A (frontal area)**: numeric value:contentReference[oaicite:3]{index=3}  
  - Units: m², cm², ft²  

**Outputs**  
- Drag force displayed as `F_d = value N` with 6 significant figures:contentReference[oaicite:4]{index=4}  
- Error message `"Invalid input."` if computation fails:contentReference[oaicite:5]{index=5}

**UI & Interaction**  
- Four input rows (ρ, v, C_d, A) with optional unit dropdowns:contentReference[oaicite:6]{index=6}  
- **Compute** button → evaluates drag force  
- Result displayed in label  

**Algorithm / Implementation**  
- Converts units:  
  - ρ: g/cm³ → ×1000 → kg/m³  
  - v: km/h ÷3.6; mph ×0.44704  
  - A: cm² ÷1e4; ft² ×0.09290304:contentReference[oaicite:7]{index=7}  
- Applies drag equation: \(F_d = 0.5 \rho v^2 C_d A\)  
- Logs results and errors via `core.data.functions.log.add_log_entry`:contentReference[oaicite:8]{index=8}

**Units & Conversion**  
- Output in newtons (N)  
- Supported conversions for density, velocity, and area as above  

**Edge Cases & Validation**  
- Non-numeric inputs → error message logged  
- Negative or nonsensical values allowed mathematically, but physically meaningless  
- Missing values → error  

**Data Sources**  
- Physics drag equation  
- Unit conversions embedded in code:contentReference[oaicite:9]{index=9}

**Logging & Export**  
- Logs under tool = `"Drag Force"`:  
  - Action = `"Compute"` with `{rho, v, cd, A, Fd}`  
  - Action = `"Error"` with `{msg}`:contentReference[oaicite:10]{index=10}  
- No export  

**Chaining**  
- Output drag force can be reused in mechanics simulations (e.g., dynamics with resistance)  

**Tests**  
- Example 1: ρ=1.225 kg/m³, v=10 m/s, C_d=1, A=0.5 m² → F_d≈30.625 N  
- Example 2: v=36 km/h → converted to 10 m/s, result same as above  
- Example 3: v=22.37 mph → converted to ~10 m/s, result same  
- Example 4: A=100 cm², other defaults → F_d≈0.306 N  
- Example 5: invalid input (“abc”) → error  

**Known Limitations / TODO**  
- Limited to steady-state, incompressible flow  
- No Reynolds number or Mach effects considered  
- Area assumed flat projection, not shape-dependent  
- No export or plot functionality yet  

---

### Tool: Kinetic Energy Calculator
**Category:** Mechanics  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Compute the kinetic energy of an object using the classical equation:  
\[
E_k = \tfrac{1}{2} m v^2
\]  

**Inputs**  
- **m (mass)**: numeric value:contentReference[oaicite:0]{index=0}  
  - Units: kg, g, lb  
- **v (speed)**: numeric value:contentReference[oaicite:1]{index=1}  
  - Units: m/s, km/h, mph  

**Outputs**  
- Kinetic energy displayed as `E_k = value J` with 6 significant figures:contentReference[oaicite:2]{index=2}  
- Error message `"Invalid input."` if computation fails:contentReference[oaicite:3]{index=3}

**UI & Interaction**  
- Two input rows: mass with unit dropdown, velocity with unit dropdown  
- **Compute** button → evaluates kinetic energy  
- Result displayed in label  

**Algorithm / Implementation**  
- Mass conversions:  
  - g → ÷1000  
  - lb → ×0.45359237  
- Velocity conversions:  
  - km/h → ÷3.6  
  - mph → ×0.44704:contentReference[oaicite:4]{index=4}  
- Applies formula \(E_k = 0.5 m v^2\)  
- Logs results and errors with input/output data  

**Units & Conversion**  
- Output always in joules (J)  
- Inputs converted internally to SI units  

**Edge Cases & Validation**  
- Non-numeric inputs → error message logged  
- Negative mass or velocity accepted mathematically, though non-physical  
- Empty fields → error:contentReference[oaicite:5]{index=5}  

**Data Sources**  
- Classical kinetic energy formula  
- Logging via `core.data.functions.log.add_log_entry`:contentReference[oaicite:6]{index=6}

**Logging & Export**  
- Logs under tool = `"Kinetic Energy"`:  
  - Action = `"Compute"` with `{m, v, KE}`  
  - Action = `"Error"` with `{msg}`:contentReference[oaicite:7]{index=7}  
- No export  

**Chaining**  
- Kinetic energy results can feed into work-energy or mechanical energy balance tools  

**Tests**  
- Example 1: m=1 kg, v=10 m/s → E_k=50 J  
- Example 2: m=1000 g, v=10 m/s → E_k=50 J  
- Example 3: m=1 lb, v=10 mph → m≈0.454 kg, v≈4.4704 m/s, E_k≈4.54 J  
- Example 4: invalid input (“abc”) → error  

**Known Limitations / TODO**  
- Only handles scalar kinetic energy (no rotational KE)  
- No relativistic correction for very high speeds  
- Limited to one object at a time  

---

### Tool: Lens & Mirror Equation
**Category:** Mechanics  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Solve the thin lens/mirror equation and display ray diagrams. Computes the missing focal length, object distance, or image distance, and provides magnification and system type (lens or mirror).

**Inputs**  
- **f (focal length)**: numeric value with unit dropdown (m, cm, mm, in, ft):contentReference[oaicite:0]{index=0}  
- **d₀ (object distance)**: numeric value with unit dropdown (m, cm, mm, in, ft):contentReference[oaicite:1]{index=1}  
- **dᵢ (image distance)**: numeric value with unit dropdown (m, cm, mm, in, ft):contentReference[oaicite:2]{index=2}  
- **Mirror mode**: checkbox, if ticked uses mirror conventions (f negative for converging mirror):contentReference[oaicite:3]{index=3}

**Outputs**  
- Computed missing quantity (f, d₀, or dᵢ) with selected unit  
- Magnification = \(-dᵢ/d₀\)  
- Type string: “Lens (Converging/Diverging)” or “Mirror (Converging/Diverging)”  
- Ray diagram plotted with object, image, and focal points:contentReference[oaicite:4]{index=4}

**UI & Interaction**  
- Three input rows with unit selectors  
- Checkbox toggle for mirror vs lens  
- **Calculate** button → performs computation  
- **Export Diagram…** button → saves ray diagram via `export_figure`:contentReference[oaicite:5]{index=5}  
- Result shown in label with multiple lines  

**Algorithm / Implementation**  
- Requires exactly two fields filled; otherwise shows `"Fill exactly two fields."`  
- Cases:  
  - f missing → \(f = 1 / (1/d₀ + 1/dᵢ)\)  
  - d₀ missing → \(d₀ = 1 / (1/f - 1/dᵢ)\)  
  - dᵢ missing → \(dᵢ = 1 / (1/f - 1/d₀)\)  
- Magnification = \(-dᵢ/d₀\) if valid  
- Mirror mode → focal length negative if converging  
- Units converted to/from metres for calculations:contentReference[oaicite:6]{index=6}  
- Ray diagram plotted: object at -d₀, image at +dᵢ, focal points ±f, principal rays drawn:contentReference[oaicite:7]{index=7}

**Units & Conversion**  
- Supported: m, cm, mm, in, ft  
- Inputs converted to metres internally; output converted back to user-selected unit  

**Edge Cases & Validation**  
- If fewer or more than two values given → error message  
- Division by zero → caught in exception block  
- Non-numeric input → `"Invalid input."`:contentReference[oaicite:8]{index=8}

**Data Sources**  
- Thin lens/mirror equation  
- Magnification relation  
- Logging via `core.data.functions.log.add_log_entry`:contentReference[oaicite:9]{index=9}

**Logging & Export**  
- Logs under tool = `"Lens & Mirror Equation"`:  
  - Action = `"Calculate"` with `{f, d0, di, magn, type}`  
  - Action = `"Error"` with `{msg}`:contentReference[oaicite:10]{index=10}  
- Export available for ray diagram  

**Chaining**  
- Magnification or computed distances could feed into optics or wave tools  

**Tests**  
- Example 1: f=0.1 m, d₀=0.5 m → computes dᵢ and magnification  
- Example 2: f=10 cm, dᵢ=20 cm → computes d₀  
- Example 3: d₀=50 cm, dᵢ=100 cm → computes f  
- Example 4: all three filled → “Fill exactly two fields.”  
- Example 5: invalid input (“abc”) → “Invalid input.”  

**Known Limitations / TODO**  
- Simplified ray diagram (no scale correctness)  
- No handling of sign conventions beyond simple mirror toggle  
- Does not calculate image type (real/virtual, upright/inverted) explicitly  

---

### Tool: Projectile Motion
**Category:** Mechanics  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Simulate projectile trajectories under uniform gravity, compute flight characteristics, and plot the motion curve.

**Inputs**  
- **Initial speed (v₀)**: numeric value:contentReference[oaicite:0]{index=0}  
  - Units: m/s, km/h, mph  
- **Launch angle (θ)**: numeric value:contentReference[oaicite:1]{index=1}  
  - Units: degrees, radians  
- **Initial height (h₀)**: numeric value:contentReference[oaicite:2]{index=2}  
  - Units: m, ft  

**Outputs**  
- Range (m)  
- Flight time (s)  
- Maximum height (m)  
- Impact speed (m/s) with horizontal and vertical components:contentReference[oaicite:3]{index=3}  
- Trajectory plot with x–y axes in metres  

**UI & Interaction**  
- Three input rows: v₀ with unit dropdown, θ with unit dropdown, h₀ with unit dropdown  
- **Calculate** button → evaluates trajectory and displays results:contentReference[oaicite:4]{index=4}  
- **Export Image…** button → saves trajectory plot via `export_figure`:contentReference[oaicite:5]{index=5}  
- Result label shows computed values on two lines  
- Embedded matplotlib figure with navigation toolbar  

**Algorithm / Implementation**  
- Converts units:  
  - v₀: km/h ÷3.6, mph ×0.44704  
  - θ: degrees → radians  
  - h₀: ft ×0.3048:contentReference[oaicite:6]{index=6}  
- Gravity constant g = 9.81 m/s²  
- Solve quadratic for flight time:  
  \[
  y(t) = h₀ + v₀ \sinθ \cdot t - \tfrac{1}{2} g t^2
  \]  
  → discriminant used to find positive root  
- Range: \(R = v₀ \cosθ \cdot T\)  
- Max height: \(h₀ + \frac{(v₀ \sinθ)^2}{2g}\)  
- Impact speed: \(\sqrt{v_x^2 + v_y^2}\)  
- Generates trajectory with 600 points for smooth curve:contentReference[oaicite:7]{index=7}  

**Units & Conversion**  
- Input accepted in m/s, km/h, mph; degrees/radians; m/ft  
- Output always in SI units (m, s, m/s)  

**Edge Cases & Validation**  
- Negative discriminant → `"No real impact (check inputs)."`  
- Non-numeric input → `"Invalid input."`  
- Initial height = 0 accepted (flat ground)  

**Data Sources**  
- Classical projectile motion equations  
- Logging via `core.data.functions.log.add_log_entry`:contentReference[oaicite:8]{index=8}

**Logging & Export**  
- Logs under tool = `"Projectile Motion"`:  
  - Action = `"Calculate"` with `{v, θ, h, R, T, Hmax, vimp}`  
  - Action = `"Error"` with `{msg}`:contentReference[oaicite:9]{index=9}  
- Export available for trajectory plot  

**Chaining**  
- Results can feed into mechanics energy or impact-related tools  

**Tests**  
- Example 1: v₀=20 m/s, θ=45°, h₀=0 m → R≈40.77 m, T≈2.88 s, Hmax≈10.20 m  
- Example 2: v₀=72 km/h, θ=30°, h₀=0 m → R≈35.3 m  
- Example 3: h₀=10 ft (~3.048 m), v₀=20 m/s, θ=45° → longer flight time and range  
- Example 4: invalid angle input (“abc”) → error  

**Known Limitations / TODO**  
- Ignores air resistance and wind drag  
- Flat ground only (no terrain modelling)  
- No unit selection for outputs  
- Does not compute landing angle explicitly  

---

### Tool: Average Speed
**Category:** Mechanics  
**Version:** v1.0 (2025-08-22)

**Purpose**  
Calculate the average speed from a given distance and travel time, with flexible unit support for input and output.

**Inputs**  
- **Distance (d)**: numeric value:contentReference[oaicite:0]{index=0}  
  - Units: m, km, mile, ft  
- **Time (t)**: numeric value:contentReference[oaicite:1]{index=1}  
  - Units: s, min, hr  
- **Output unit**: dropdown selection:contentReference[oaicite:2]{index=2}  
  - Options: m/s, km/h, mph  

**Outputs**  
- Average speed displayed as `Speed = value unit` with 6 significant figures:contentReference[oaicite:3]{index=3}  
- Error message `"Invalid input."` if computation fails:contentReference[oaicite:4]{index=4}

**UI & Interaction**  
- Input row for distance with value + unit selector  
- Input row for time with value + unit selector  
- Dropdown for output speed unit  
- **Compute** button → evaluates average speed:contentReference[oaicite:5]{index=5}  
- Result displayed in label  

**Algorithm / Implementation**  
- Converts distance to metres:  
  - km ×1000, mile ×1609.344, ft ×0.3048  
- Converts time to seconds:  
  - min ×60, hr ×3600  
- Computes speed = d/t (in m/s)  
- Converts result to chosen unit:  
  - km/h ÷(1/3.6), mph ÷(1/2.23693629)  
- Logs result or error via `core.data.functions.log.add_log_entry`:contentReference[oaicite:6]{index=6}  

**Units & Conversion**  
- Distance input: m, km, mile, ft  
- Time input: s, min, hr  
- Output selectable: m/s, km/h, mph  

**Edge Cases & Validation**  
- Time = 0 → error (`"t=0"`)  
- Non-numeric inputs → `"Invalid input."`  
- Negative values accepted mathematically but physically nonsensical  

**Data Sources**  
- Classical definition of average speed (d/t)  
- Unit conversion constants embedded in code:contentReference[oaicite:7]{index=7}

**Logging & Export**  
- Logs under tool = `"Average Speed"`:  
  - Action = `"Compute"` with `{d_m, t_s, v_out, unit}`  
  - Action = `"Error"` with `{msg}`:contentReference[oaicite:8]{index=8}  
- No export  

**Chaining**  
- Output average speed usable in mechanics energy or motion-related tools  

**Tests**  
- Example 1: d=100 m, t=10 s, output m/s → 10 m/s  
- Example 2: d=1 km, t=2 min, output km/h → 30 km/h  
- Example 3: d=1 mile, t=1 min, output mph → ~60 mph  
- Example 4: d=100 ft, t=10 s, output m/s → ~3.048 m/s  
- Example 5: invalid input (“abc”) → error  

**Known Limitations / TODO**  
- Only constant average speed, no instantaneous velocity  
- No graphical or tabular output  
- Limited unit set  

---

### Tool: Terminal Velocity Calculator

**Category:** Mechanics
**Version:** v2.0 (2025-08-23)

**Purpose**
Simulate the motion of a falling object under gravity and air resistance. The tool provides both 2D plots and interactive 3D visualizations of free fall until terminal velocity is reached. It is designed for teaching mechanics concepts such as drag force, acceleration, and velocity-time relationships.

**Inputs**

* **Mass (kg)**: numeric input
* **Cross-sectional Area (m²)**: numeric input
* **Drag Coefficient (dimensionless)**: numeric input
* **Air Density (kg/m³)**: numeric input (default ≈ 1.225)
* **Initial Height (m)**: numeric input

**Outputs**

* **2D Mode**: velocity vs time, displacement vs time plots
* **3D Mode**: interactive simulation of the falling body
* **HUD Overlay**: live display of time, velocity, and position in corner of simulation view
* **Terminal Velocity Value**: displayed numerically

**UI & Interaction**

* Input fields for parameters (mass, area, Cd, density, height)
* Mode toggle: **2D plots / 3D simulation**
* **Run Simulation** button → starts/resets simulation
* **Export Data**: option to save simulation results (CSV, PNG of plots)
* **HUD** in 3D view shows:

  * Time elapsed (s)
  * Velocity (m/s)
  * Height (m)

**Algorithm / Implementation**

* Governing equation:

  $$
  m \frac{dv}{dt} = mg - \frac{1}{2}\rho C_d A v^2
  $$
* Numerical integration (Euler/Runge-Kutta) for velocity and displacement updates
* In **2D mode**: matplotlib plots of velocity-time and position-time
* In **3D mode**: PyQtGraph OpenGL visualization with animated sphere

  * Sphere moves downward with simulated acceleration
  * Camera controls allow rotation and zoom
  * HUD text rendered in scene (no background box)

**Units & Conversion**

* SI units enforced (kg, m, s)
* Input validation ensures numeric fields are > 0

**Edge Cases & Validation**

* Invalid or missing parameters → warning message
* Very high drag or zero mass → capped with safety checks
* Object constrained to stop at ground level (y ≥ 0)

**Data Sources**

* Constants: g = 9.81 m/s²
* Default air density: 1.225 kg/m³ (sea level, 15°C)

**Logging & Export**

* Results (parameters, terminal velocity, simulation data) stored in log system
* Optional CSV export with (t, v, y)
* Image export (plots and/or 3D snapshots)

**Chaining**

* Outputs (terminal velocity value, time series data) can be chained into other mechanics tools (e.g., kinetic energy calculator, drag force visualizer)

**Tests**

* Example 1: Mass = 80 kg, Area = 0.7 m², Cd = 1.0 → vₜ ≈ 47 m/s
* Example 2: Steel ball (m = 5 kg, A = 0.01 m², Cd = 0.47) → vₜ ≈ 32 m/s
* Example 3: Feather-like body (Cd = 1.3, A = 0.05, m = 0.02) → very low vₜ

**Known Limitations / TODO**

* Currently assumes vertical fall only (no horizontal wind component)
* No deformation modeling (e.g., parachutes opening mid-flight)
* HUD shows only t, v, y — could expand to include acceleration a(t)
* Could add particle trails or velocity vectors in 3D for enhanced visualization