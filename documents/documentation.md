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

## Element Lab

**Name:** Element Lab
**Category:** Chemistry
**Version:** v1.0 (2025-08-23)

### Purpose

The Element Lab provides a unified environment to interactively explore atomic and elemental data. It integrates multiple sub-tools into one cohesive module, allowing both quick lookups and in-depth analysis. The target audience includes students (for learning and visualization), educators (for demonstrations), and developers (for extending with custom data and export features).

It replaces earlier standalone modules (element viewer, shell visualiser, isotopic notation, comparator, property grapher, phase predictor) by embedding them into one consolidated UI with shared navigation and search.

---

### Inputs

* **Element Identifier:** symbol (e.g. "Fe"), name ("Iron"), or atomic number (26).
* **Charge (integer):** optional, for ion visualisation in Shell Visualiser.
* **Mass Number (integer):** required for Isotopic Notation.
* **Temperature (float, string with unit):** accepts plain numbers or suffixed with K, °C, °F (e.g. "25", "77F", "300K").
* **Pressure (float):** optional, defaults to 1 atm, for Phase Predictor.
* **Property Selection:** choice of atomic/physical/chemical properties for Grapher and Comparator.

---

### Outputs

* **Element Viewer:** complete descriptive metadata, atomic parameters, electron configuration, densities, phase points, and textual summary.
* **Shell Visualiser:** 2D orbital diagrams, optional 3D GL-based electron orbit simulations with animated rotation.
* **Isotopic Notation:** full isotope decomposition, neutron counts, nucleon pie charts, natural abundance if available.
* **Property Grapher:** scatterplots of chosen X vs Y property, with category-based coloring and interactive hover tooltips.
* **Element Comparator:** tabulated side-by-side property comparison across up to three elements, automatic highlighting of max/min values.
* **Phase Predictor:** state classification (solid/liquid/gas) under user-defined T/P conditions with formatted summary.

All sub-tools provide options for exporting charts/images or saving to project directories.

---

### UI & Interaction

* Left sidebar: searchable list of all elements, with filters and quick navigation.
* Toolbar: direct buttons for each sub-tool (Viewer, Shells, Isotopes, Properties, Compare, Phase).
* Embedded stacked layout: each tool runs as a child dialog but behaves like a single integrated window.
* Viewer supports "Favorites" with persistent storage in JSON (`ELEMENT_FAVS_PATH`).
* Shell Visualiser provides tabs for 2D (matplotlib) and 3D (pyqtgraph OpenGL) renderings.
* Property Grapher supports category filtering (e.g., transition metals only).
* Comparator uses tabbed property groups and checkboxes to control which values to compare.

---

### Algorithms / Equations

* **Shell Visualiser:**

  * Adjusts shell counts for ionisation states (electron removal/addition).
  * Electrons placed evenly on circular orbits (2D) or distributed on rings with animated rotation (3D).
  * Neutron estimation via rounded atomic mass – Z.
* **Isotopic Notation:**

  * N = A – Z (mass number minus atomic number).
  * Abundance % if available, else shown as unknown.
  * Pie chart: protons vs neutrons.
* **Property Grapher:**

  * Data points drawn from periodic table JSON.
  * X and Y properties numeric only; tooltip shows values.
  * Category coloring scheme applied consistently (alkali = red, halogens = blue, etc.).
* **Comparator:**

  * Auto-highlights largest values in blue, smallest in red italics.
  * Non-numeric differing values italicised.
* **Phase Predictor:**

  * Simple three-way classification:

    * `T < melt` → solid
    * `melt <= T < boil` → liquid
    * `T >= boil` → gas

---

### Units & Conversion

* Temperatures converted internally to Kelvin.
* Atomic masses in unified atomic mass units (u).
* Densities in g/cm³.
* Boiling/melting points in Kelvin.
* Consistent conversion functions from `chemistry_utils`.

---

### Edge Cases & Validation

* Handles missing or incomplete JSON values gracefully (error messages shown instead of crashes).
* Viewer: skips fields not present in dataset.
* Shell Visualiser: warns if element has no shell data or atomic number.
* Isotope Notation: validates integer inputs, warns on negative neutron count.
* Phase Predictor: displays "No Data" if melting/boiling points unavailable.
* Comparator: disallows duplicate element selections.
* Grapher: skips elements missing selected X/Y properties.

---

### Tests

Unit and manual tests cover:

* **Viewer:** searching by symbol, name, number. Verification of details panel formatting.
* **Shell Visualiser:** correct electron distribution for known configurations (H = 1, He = 2, O = 2,6). Charge adjustment tested (Na⁺ → 2,8 vs Na → 2,8,1). 3D renderer tested with mock GL.
* **Isotopic Notation:** isotope data for C-12, C-14, U-238. Validates neutron calculation and pie chart output.
* **Property Grapher:** X = mass, Y = boiling point: verifies correct scatter size, tooltips, and category filter (transition metals only).
* **Comparator:** H, O, Fe: checks table formatting, highlight rules, and tooltip descriptions.
* **Phase Predictor:** tested with known data points (H₂O \~273K melting, \~373K boiling). Handles inputs like "100C", "32F", "373K".

---

### Integration & Logging

* Uses central `chemistry_utils.load_element_data()` for all property data.
* Logs every action (draw, compute, compare, predict) with `add_log_entry`.
* Exports images via `image_export.export_figure`.
* Persistent favorites stored as JSON.

---

### Known Limitations

* 3D visualiser requires PyQtGraph with OpenGL; gracefully disables otherwise.
* No error estimation for phase prediction (sharp thresholds).
* Isotopic abundances incomplete for many elements.
* Grapher currently limited to two properties; no trendline fitting.

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

## DNA Lab

**Name:** DNA Lab
**Category:** Biology
**Version:** v1.0 (2025-08-23)

### Purpose

The DNA Lab is a bioinformatics-oriented module within ASH designed to explore nucleic acid and protein sequences. It provides utilities for codon translation, sequence statistics, alignments, and data parsing. The goal is to give students and researchers an integrated environment to analyze DNA/RNA and their protein products without requiring external software.

It complements the chemistry-focused labs (Element, Molecule) and expands ASH into molecular biology, offering a pipeline from sequence input → translation → protein statistics and eventually 3D structure prediction (future roadmap).

---

### Inputs

* **Nucleotide sequences:** DNA (ATGC) or RNA (AUGC). Supports direct paste or file import (FASTA, GenBank).
* **Codons:** single 3-base RNA codons for lookup.
* **Frames:** translation supports all six reading frames (+1,+2,+3,-1,-2,-3).
* **Scoring parameters:** for sequence alignments (match, mismatch, gap penalties).
* **File formats:** FASTA, GenBank text for parsing and storage.

---

### Outputs

* **Codon Lookup:** amino acid, group classification (hydrophobic, polar, charged, stop), visualized as pie charts.
* **Frame Translation:** amino acid sequences across all reading frames with color-coded codons and stop markers.
* **Transcription:** DNA → RNA → protein, with codon usage histograms and statistics.
* **GC Content:** numerical GC% with optional sliding window graphs.
* **Molecular Weight:** approximate weights for DNA, RNA, and proteins.
* **Reverse Complement:** strand inversion and complement base replacement.
* **Alignment:** pairwise sequence alignment string with score, gap penalties applied.
* **Seq Parser:** parsed records from FASTA/GenBank, stored in internal libraries with metadata (ID, length, type).

---

### UI & Interaction

* Codon lookup panel: single-input field, immediate result with amino acid and classification.
* Frame translation panel: textarea for sequence input, displays six reading frames with aligned codons and stop symbols.
* Transcription panel: input DNA → outputs mRNA + protein sequence + codon frequency bar chart.
* GC content panel: returns % and optional sliding window analysis.
* Alignment tool: dual input with scoring parameter fields, outputs aligned sequences with highlights.
* Sequence parser: file import dialog, displays parsed sequence list with ID, length, and sequence data.

---

### Algorithms / Equations

* **Codon Table:** Standard genetic code mapping codons to amino acids.
* **GC Content:** $\text{GC\%} = \frac{G+C}{A+T+G+C} \times 100$.
* **Transcription:** Replace T → U, group codons in triplets, map to amino acids.
* **Frames:** 6 possible reading frames by shifting index and reverse complementing.
* **Alignment:** Needleman–Wunsch or Smith–Waterman style scoring (depending on mode), using user-defined match/mismatch/gap penalties.
* **Molecular Weight:** sum of average monomer masses minus water molecules for bonds.

---

### Units & Conversion

* Sequence inputs are case-insensitive, whitespace ignored.
* Protein weights in Daltons (Da).
* Sequence lengths reported in base pairs (bp) or amino acids (aa).
* Codon frequencies normalized to counts per 1000 codons.

---

### Edge Cases & Validation

* Rejects invalid nucleotide characters (anything outside A, T, G, C, U).
* Warns if sequence length not divisible by 3 when translating.
* Reverse complement only valid for DNA (RNA U’s converted automatically if present).
* Alignment requires sequences of length ≥ 2.
* Parser gracefully handles malformed FASTA/GenBank headers, skips invalid entries.
* Empty input fields trigger error dialogs instead of crashes.

---

### Tests

Unit and integration tests include:

* **Codon Lookup:** verifies all 64 codons map to correct amino acids. Includes edge codons (AUG → Start, UAA/UAG/UGA → Stop).
* **Frame Translation:** tested with example sequences; checks consistency across forward and reverse frames.
* **GC Content:** verifies against known sequences (E. coli \~51% GC).
* **Transcription:** validates DNA → RNA substitution and protein translation for known genes.
* **Molecular Weight:** checked against benchmark proteins (e.g. insulin).
* **Reverse Complement:** input DNA "ATGC" → "GCAT".
* **Alignment:** regression-tested with small sequences where optimal alignment known.
* **Seq Parser:** runs with mixed FASTA/GenBank files; checks that IDs, lengths, and sequences match expected values.

---

### Integration & Logging

* Logging of all operations with `add_log_entry`, recording sequence lengths, codon usage, GC%, alignment scores, etc.
* Sequence imports stored in internal library for reuse across sessions.
* Export options: charts saved as PNG, sequence outputs exported as FASTA.

---

### Known Limitations

* Currently supports only the standard genetic code (no mitochondrial/alternative codes).
* Pairwise alignment only; no multiple sequence alignment yet.
* No protein structural prediction yet (future extension with Alphafold/ESMFold).
* Parser does not yet support EMBL or PDB formats.
* Charts limited to 2D bar/pie, no interactive zooming.

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

## Electricity Lab

**Name:** Electricity Lab
**Category:** Physics
**Version:** v1.0 (2025-08-23)

### Purpose

The Electricity Lab is an integrated suite for studying classical electromagnetism, circuit theory, and material properties. It consolidates calculators, visualisers, and simulators into one consistent environment. Each tool runs as an embeddable widget inside the lab framework (`_Embedded` wrapper), ensuring a unified UI and shared resources (logging, notes, constants).

The lab covers basics (Ohm’s law, resistors, capacitors) through intermediate circuits (RC charging/discharging) and into advanced electromagnetism (fields, induction, ferromagnetism). It is designed for both education and exploratory use.

---

### Inputs

* **Electrical quantities:** voltage, current, resistance, capacitance, inductance (with unit scaling).
* **Charge and geometry parameters:** charge values (C), distances (m), coil turns, areas, lengths.
* **Material constants:** relative permittivity (εr), permeability (μr), Curie temperature, etc.
* **Waveform properties:** RMS/peak values for AC, dB/dt or sinusoidal B-field parameters.
* **Simulation ranges:** time intervals for RC and induction plots, spatial ranges for field plots.
* **User notes:** free text saved to persistent file.

---

### Outputs

* **Coulomb Force Calculator** – numeric force magnitude with classification (attractive/repulsive).
* **Electric Field Visualiser** – interactive streamplot of field lines for two point charges; overlay of log|E| magnitude.
* **Mini Tools** – resistor color code decoder, capacitance/inductance calculators, RC time constant, power/energy costs, AC RMS↔peak conversions.
* **Ohm’s Law** – solver that computes V, I, or R from any two inputs with unit conversions.
* **RC Circuit Helper** – charging/discharging exponential plots with computed τ = RC.
* **Magnetic Field Calculator** – plots B-field for infinite wire, circular loop, or solenoid with on-axis formulas.
* **Magnetic Flux & Induction** – EMF vs. time plots from Faraday’s law under linear or sinusoidal B(t).
* **Magnoline** – magnet placement tool with interactive field line plotting from dipole-like sources.
* **Ferromagnetism Helper** – M(T) vs. temperature plots using critical exponent β ≈ 0.33 with Curie temperature cutoff.
* **Notes system** – user notes appended to a persistent file with timestamp.
* **Reference constants** – embedded values for ε₀, μ₀, and c.

---

### UI & Interaction

* **Sidebar:** quick tool list, double-click navigation, notes panel, constants display.
* **Toolbar:** navigation buttons with grouped categories (Basics, Fields, Circuits, Materials).
* **Logging:** all computations and plots call `add_log_entry`.
* **Image export:** visual tools integrate with `export_figure` for PNG export.
* **Notes:** free-form text pad with “Save Notes” button, storing entries under `electricity_lab_notes.txt`.

---

### Algorithms / Equations

* **Coulomb:** $F = k \frac{|q_1 q_2|}{r^2}$, sign determines nature.
* **Electric field:** vector superposition from point charges, $\vec{E} = k q \vec{r}/|\vec{r}|^3$.
* **Ohm’s law:** $V = IR$ with flexible unit scaling.
* **RC circuit:** charging $V(t) = V_{in}(1-e^{-t/\tau})$, discharging $V(t) = V_0 e^{-t/\tau}$, τ = RC.
* **Capacitance:** $C = ε₀ ε_r A/d$.
* **Inductance (solenoid):** $L = μ₀ μ_r N^2 A / \ell$.
* **Power/Energy:** $P=VI, V^2/R, I^2R$; $E = P·t$; cost = kWh·price.
* **AC wave:** conversions via $V_{peak} = V_{rms}\sqrt{2}$.
* **Magnetic field:**

  * Wire: $B(r) = μ₀ I / (2πr)$
  * Loop (axis): $B(x) = μ₀ I R^2 / (2(R^2+x^2)^{3/2})$
  * Solenoid: $B ≈ μ₀ (N/L) I$.
* **Induction:** EMF = $-N \cdot dΦ/dt$, computed via gradients of B(t).
* **Ferromagnetism:** $M(T) = M₀ (1-T/T_c)^β$ for T\<Tc, else 0.
* **Magnoline:** field lines from superposition of dipole-like sources, normalized and streamplotted.

---

### Units & Conversion

* Extensive unit support: V/mV/kV, A/mA/kA, Ω/mΩ/kΩ/MΩ.
* Outputs formatted with engineering prefixes (m, µ, n, k, M, G).
* Constants embedded in SI units: ε₀ (F/m), μ₀ (H/m), c (m/s).

---

### Edge Cases & Validation

* Coulomb tool enforces r>0.
* Field visualiser clamps near-zero r to avoid division errors.
* Mini tools validate inputs and warn for invalid/empty entries.
* Ohm’s law solver requires exactly two fields filled.
* RC helper validates τ>0; disallows negative R or C.
* Magnoline warns if no magnets are defined.
* Ferromagnetism helper enforces Tc, M₀, Tmax > 0.
* Sidebar notes check for empty text before saving.

---

### Tests

* Coulomb: q1=+1µC, q2=-2µC, r=0.05 m → |F| ≈ 7.19 N attractive.
* Ohm’s law: V=12 V, R=6 Ω → I=2 A; I=0.5 A, R=10 Ω → V=5 V.
* RC helper: R=1kΩ, C=470 µF, Vin=5 V → τ ≈ 0.47 s, charging/discharging plots match expected exponentials.
* Electric field: symmetric charges ±q at ±x produce dipole field pattern with symmetry about origin.
* Magnetic field calculator: infinite wire, I=5 A, r=0.05 m → B ≈ 2.0e-5 T.
* Induction: sinusoidal B, ΔB=0.2, ω=50 rad/s → EMF matches numerical derivative.
* Magnoline: two opposite magnets produce standard dipole field lines.
* Ferromagnetism: Tc=770 K, M0=1 → curve decays to zero smoothly at Tc.
* Mini tools: resistor bands (red-violet-orange-gold) → 27kΩ ±5%.

---

### Integration & Logging

* All tools log actions with `add_log_entry` (inputs, outputs, errors).
* Image plots exportable via `export_figure`.
* Notes system appends to persistent file with timestamps.
* Shared constants panel avoids repeated entry and enforces SI values.

---

### Known Limitations

* Ferromagnetism helper currently uses only mean-field β=0.33; no hysteresis curves.
* Electric field visualiser limited to two charges.
* Magnoline is qualitative (dipole-like approximation).
* Induction plots rely on numerical differentiation of B(t), may be noisy for stiff parameters.
* Mini tools cover only common components; no transformers or AC phasor analysis yet.
* Circuit analysis limited to single RC; no multi-component networks.

---

### Tool: Geo Lab

**Category:** Geology
**Version:** v1.0 (2025-08-23)

**Purpose**
Geo Lab is a comprehensive geology supertool that merges the functionality of several smaller calculators into one unified interface. It replaces the Mineral Explorer, Mineral Identifier, Half-life Calculator, Radioactive Dating, Plate Boundary Designer, and Plate Velocity Calculator. By consolidating overlapping tools, it reduces redundancy, ensures shared datasets, and provides a consistent interface for geoscientific exploration. The tool is designed for both educational and exploratory use, with emphasis on visualization and intuitive interaction.

---

**Inputs**

* *Minerals Tab*

  * **Explorer Subtab:**

    * Search query (text, matches name, formula, notes, system, type).
    * Filter by mineral type (dropdown).
    * Filter by favourites (checkbox).
  * **Identifier Subtab:**

    * Mohs hardness (numeric).
    * Specific gravity (numeric).
    * Crystal system (text).

* *Radioactivity Tab*

  * Initial quantity N₀ (numeric).
  * Half-life t½ (numeric, years).
  * Time span T for decay curve plotting (numeric, years).
  * Remaining % for age estimation (0–100).
  * Presets for common isotopes (Carbon-14, Potassium-40, Uranium-235/238, Rubidium-87).

* *Tectonics Tab*

  * Distance between points (km).
  * Time interval (Myr).
  * Boundary type (Convergent, Divergent, Transform).

---

**Outputs**

* *Minerals Explorer:* searchable table with mineral name, formula, hardness, SG, system, and favourite marker.
* *Minerals Identifier:* table of likely matches with scores; scatter plot of hardness vs. SG with highlighted best candidates.
* *Radioactivity:* decay curve plot of N(t); text outputs for N(T), half-life used, and estimated age from remaining %.
* *Tectonics:* computed plate velocity (mm/yr); schematic boundary diagrams showing ridges, trenches, arrows, volcanoes, or faults depending on type.

---

**Algorithms & Implementation**

* *Minerals:*

  * Data loaded from local JSON/CSV.
  * Explorer uses substring match with debounce for performance.
  * Identifier scores rows with weighted similarity on hardness, SG, and system. Top results shown and plotted.

* *Radioactivity:*

  * Decay curve computed with $N(t) = N₀ \times 0.5^{t/t_{½}}$.
  * Age from remaining %: $t = \frac{\ln(r)}{\ln(0.5)} \times t_{½}$.

* *Tectonics:*

  * Plate velocity: $v = \frac{d\,[km]}{t\,[Myr]}$ in mm/yr.
  * Boundary diagrams drawn using Matplotlib patches (rectangles, arrows, text labels).

---

**UI & Interaction**

* Top-level tabs for **Minerals**, **Radioactivity**, and **Tectonics**.
* Minerals tab has **Explorer** and **Identifier** subtabs.
* Toolbar integration for all figures, allowing zoom/pan.
* Export buttons for saving figures/diagrams as PNG.
* Prefill button provides debug/demo values.

---

**Logging & Export**

* Log entries include:

  * Mineral Explorer queries and matches count.
  * Identifier inputs and number of results.
  * Radioactivity: N₀, t½, T, and final N(T).
  * Tectonics: distance, time, velocity, boundary type.
* Figures exported using `export_figure()`.

---

**Testing**

* *Minerals:*

  * Example 1: Search “Quartz” → returns SiO₂ with hardness \~7.
  * Example 2: Identifier hardness=3, SG=2.7, sys=“hexagonal” → matches Calcite, Dolomite.

* *Radioactivity:*

  * Example 1: N₀=100, t½=5730, T=50000 → curve decays correctly, final N≈0.76.
  * Example 2: rem=25%, hl=5730 → estimated age ≈11460 years.

* *Tectonics:*

  * Example 1: d=100 km, t=2 Myr → v=50 mm/yr.
  * Example 2: Boundary=Convergent → diagram shows trench + volcano arc.

---

**Edge Cases & Validation**

* Mineral filters with empty inputs → return all numeric rows.
* Radioactivity: negative or zero half-life/time → error message.
* Tectonics: zero time → velocity set to ∞.
* Identifier: gracefully handles missing hardness/SG in dataset.

---

**Known Limitations / TODO**

* Mineral identification uses heuristic matching, not full statistical inference.
* Radioactivity assumes closed system, no contamination corrections.
* Plate diagrams are schematic, not scaled to geological reality.
* No 3D mineral crystal visualization yet.
* Future: integration with external mineral DBs (e.g., Mindat API), isotope libraries, and GIS map overlays for tectonics.

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

### Tool: Mechanics Lab

**Category:** Mechanics
**Version:** v1.0 (2025-08-23)

**Purpose**
Mechanics Lab is a consolidated mechanics supertool that unifies separate calculators for average speed, acceleration, kinetic energy, drag force, and projectile motion. It replaces multiple small, redundant tools by centralizing all inputs and providing tabbed analysis. This ensures consistency across computations, avoids re-entering the same values, and provides immediate visualizations that connect different mechanics concepts together. It is designed for students, educators, and self-learners who need both quick calculations and intuitive graphical representations.

---

**Inputs**

All core quantities are defined once in a centralized *Inputs Tab*.

* Distance with unit selector (`m`, `km`, `mile`, `ft`)
* Time with unit selector (`s`, `min`, `hr`)
* Initial velocity $v₀$ with unit selector (`m/s`, `km/h`, `mph`)
* Change in velocity Δv with unit selector (`m/s`, `km/h`, `mph`)
* Mass with unit selector (`kg`, `g`, `lb`)
* Fluid density ρ with unit selector (`kg/m³`, `g/cm³`)
* Drag coefficient $C_d$
* Reference area A with unit selector (`m²`, `cm²`, `ft²`)
* Initial height h₀ with unit selector (`m`, `ft`)
* Launch angle θ with unit selector (`degrees`, `radians`)

Additional interface options:

* Output speed unit for results (`m/s`, `km/h`, `mph`)
* Time unit for acceleration denominator (`s`, `min`, `hr`)
* Prefill button with debug/demo values.
* Apply to Tabs button (updates all calculations simultaneously).

---

**Outputs**

Each tab provides both text results and a plot:

* **Speed & Acceleration**

  * Average speed from distance/time.
  * Acceleration from Δv/time.
  * Velocity–time graph using v₀, Δv, and t.

* **Kinetic Energy**

  * Kinetic energy at given m and v.
  * Plot of $E_k(v) = 0.5mv²$.

* **Drag Force**

  * Drag force at v₀.
  * Plot of $F_d(v) = 0.5ρC_dAv²$.

* **Projectile Motion**

  * Full kinematic analysis with gravity g = 9.81 m/s².
  * Outputs: range, flight time, max height, impact velocity (with vx, vy).
  * 2D trajectory plot.

---

**Algorithms & Implementation**

* Average speed: $v = d/t$ after unit conversion.
* Acceleration: $a = Δv / t$.
* Kinetic energy: $E_k = 0.5mv²$.
* Drag force: $F_d = 0.5ρC_dAv²$.
* Projectile motion:

  * Solve quadratic equation for flight time.
  * Compute range R, flight time T, Hmax, and impact speed.
  * Trajectory drawn as $y(x) = h₀ + x\tanθ - \frac{gx²}{2v²\cos²θ}$.

---

**UI & Interaction**

* Centralized Inputs tab ensures consistency.
* Prefill button auto-fills sensible defaults (e.g., d=100 m, t=10 s, v₀=20 m/s).
* Apply to Tabs instantly updates every tab.
* Export buttons available per-plot.
* Velocity-time, energy, drag, and trajectory plots all interactive via Matplotlib toolbar.

---

**Logging & Export**

* Logs include all inputs/outputs: speed, acceleration, energies, drag forces, projectile parameters.
* Export system saves plots as PNG.
* Each export and computation recorded in log for reproducibility.

---

**Testing**

* *Speed & Acceleration*

  * Example 1: d=100 m, t=10 s → v=10 m/s.
  * Example 2: Δv=10 m/s, t=5 s → a=2 m/s².

* *Kinetic Energy*

  * Example: m=2 kg, v=10 m/s → Eₖ=100 J.
  * Curve doubles quadratically with v.

* *Drag Force*

  * Example: ρ=1.225, Cd=1.0, A=0.5 m², v=10 m/s → F=30.6 N.
  * Plot matches quadratic increase.

* *Projectile Motion*

  * Example: v=20 m/s, θ=45°, h₀=0 → range≈40.8 m, T≈2.88 s, Hmax≈10.2 m.
  * Matches textbook equations.

---

**Edge Cases & Validation**

* Division by zero (t=0) handled → “undefined” message.
* Missing values → tab shows instructions instead of crash.
* Projectile with θ=90° → vertical trajectory, zero range.
* Projectile with h₀<0 → clamps to ground level.

---

**Known Limitations / TODO**

* No air resistance in projectile motion.
* Drag force assumes steady flow, no turbulence modeling.
* Energy and drag plots use simple range scaling, not adaptive to extreme values.
* Could add 3D projectile visualization (future extension).
* Could add real-time recomputation on input change (currently manual Apply).

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

---

## AlphaFold Tool

**Category:** Microbiology  

**Purpose:**  
The AlphaFold tool integrates protein structure prediction results from the official AlphaFold Protein Structure Database into ASH. It allows the user to fetch predicted 3D structures from a UniProt accession ID, inspect confidence metrics (pLDDT, PAE), and visualize the structure in an interactive 3D viewer.  

**Core Features:**  
- **UniProt accession input:** User provides an accession ID (e.g. A9VLF6).  
- **Format selection:** Download models in PDB or mmCIF formats.  
- **Confidence data:** Option to fetch supporting JSON files with per-residue confidence scores (pLDDT) and predicted aligned error (PAE).  
- **Caching:** Downloaded models and metadata are stored locally under `~/.ash_cache/alphafold`.  
- **Interactive 3D Viewer:** Structures are displayed via NGL.js embedded in a PyQt6 WebEngine widget. Users can choose different representations (cartoon, licorice, ball+stick, spacefill, backbone) and toggle coloring by pLDDT.  

**Inputs:**  
- UniProt accession code (string).  
- Desired file format (PDB or mmCIF).  
- Checkbox to include pLDDT/PAE confidence data.  

**Outputs:**  
- Downloaded structure file (.pdb or .cif).  
- Optional JSON files with pLDDT and PAE confidence metrics.  
- Display of coverage, creation date, and model identifier metadata.  
- 3D interactive visualization of the protein structure.  

**Educational Role:**  
- Provides a bridge between sequence-level biology and 3D structural biology.  
- Allows users to explore how protein structures are predicted, and visually connect sequence → fold → confidence.  
- Encourages exploration of different visualization styles and confidence maps for interpretation.  

**Limitations:**  
- Requires internet access to fetch models from the AlphaFold DB.  
- 3D viewing requires `pyqt6-webengine` installed. Without it, only downloads and text summaries are available.  
- Relies entirely on AlphaFold DB availability; no local prediction is performed.  

**Example Workflow:**  
1. Enter a UniProt accession ID (e.g. A9VLF6).  
2. Select PDB format and enable confidence data.  
3. Click *Fetch* → model and metadata are downloaded and cached.  
4. Open 3D viewer → protein structure appears with default cartoon representation, color-coded by pLDDT.  
5. Switch visualization style or disable confidence coloring for comparison.  

---

# Smaller Tools Documentation

## Astronomy
- **Blackbody Peak (Wien’s Law):** Computes peak emission wavelength for a given temperature. Input: T (K). Output: λ_max.  
- **Escape Velocity:** Calculates minimum speed required to escape gravity. Inputs: mass, radius.  
- **Exoplanet Transit Depth:** Estimates stellar light dip during transit. Inputs: R_star, R_planet.  
- **Habitable Zone Estimator:** Calculates habitable zone boundaries from stellar luminosity.  
- **Magnitude–Distance Modulus:** Relates apparent/absolute magnitudes to distance.  
- **Orbital Period (Kepler’s 3rd Law):** Computes orbital period from semi-major axis and mass.  
- **Parallax Distance:** Calculates distance to stars from parallax angle.  
- **Redshift Calculator:** Computes z from observed vs emitted wavelengths; includes relativistic case.  
- **Rocket Equation (Tsiolkovsky):** Computes Δv given Isp and mass ratio.  
- **Stellar Luminosity (Stefan–Boltzmann):** L = 4πR²σT⁴.  
- **Surface Gravity:** g = GM/R².  

## Biology
- **Amino Acid Composition:** Counts amino acid occurrences in a protein sequence.  
- **CRISPR Guide Finder:** Identifies PAM sites and candidate gRNAs.  
- **DNA Melting Temperature:** Estimates duplex Tm from GC content, length, salt concentration.  
- **Enzyme Kinetics (Michaelis–Menten):** Computes v from substrate concentration.  
- **Hardy–Weinberg Calculator:** Calculates genotype frequencies from allele frequencies.  
- **Osmosis/Tonicity Tool:** Classifies conditions as hypo-, iso-, or hypertonic.  
- **pH Calculator:** Computes pH from hydrogen ion concentration or acid/base concentration.  
- **Population Growth Calculator:** Models exponential or logistic growth of N(t).  
- **Restriction Site Mapper:** Identifies restriction enzyme recognition/cut sites in DNA.  

## Chemistry
- **Buffer pH (Henderson–Hasselbalch):** Calculates buffer pH from pKa and concentration ratio.  
- **Equilibrium from ΔG°:** Computes equilibrium constant K from standard Gibbs free energy.  
- **Ideal Gas Solver:** Solves PV = nRT for any variable.  
- **Molar Mass Calculator:** Computes molecular weight from a chemical formula.  
- **Nernst Equation:** Computes cell potential under non-standard conditions.  
- **Reaction Balancer:** Balances stoichiometric equations.  
- **Reaction Rate (Arrhenius):** k = Ae^(–Ea/RT).  
- **Titration Curve Generator:** Computes pH at titration points (basic form).  

## Electricity
- **Biot–Savart (Straight Wire):** Calculates magnetic field from an infinitely long wire.  
- **Lorentz Force Calculator:** Computes force on a charge in E and B fields.  
- **RLC Resonance Calculator:** Finds resonance frequency of an RLC circuit.  
- **Skin Depth Calculator:** Computes δ = √(2ρ/ωμ).  
- **Transmission Line Calculator:** Computes impedance/reflection coefficients.  

## Mechanics
- **Angular Momentum Calculator:** Computes L = r × p or L = Iω.  
- **Centripetal Force Calculator:** Fc = mv²/r.  
- **Collision Simulator:** Models elastic and inelastic collisions.  
- **Impulse–Momentum Calculator:** Δp = FΔt.  
- **Momentum Conservation Tool:** Calculates before/after momentum of a system.  
- **Oscillator Damping Tool:** Computes amplitude decay for damped oscillators.  
- **Power Calculator:** Computes power from work/time or force × velocity.  
- **Rotational Kinematics Tool:** Relates θ, ω, α, and t.  
- **SHM Tool:** Simple harmonic motion equations for displacement, velocity, acceleration.  
- **Terminal Velocity Simulator:** Computes terminal velocity under drag. Includes 3D interactive view.  
- **Uniform Circular Motion Tool:** Computes velocity and frequency for circular paths.  
- **Work–Energy Theorem Tool:** W = ΔE.  
- **Work–Power Tool:** Computes mechanical power from work or velocity.  

## Microbiology
- **Agar Diffusion Demo:** Simplified diffusion distance calculator.  
- **Bacterial Growth (Logistic):** Simulates logistic growth curve.  
- **Biofilm Growth (Gompertz):** Models sigmoidal biofilm development.  
- **Chemostat Steady State:** Calculates washout threshold and steady state.  
- **Monod Kinetics:** Computes μ as function of substrate concentration.  
- **Phylogenetic Distance (Hamming):** Computes dissimilarity between DNA sequences.  
- **Quorum Sensing Threshold:** Hill-function activation threshold model.  
- **Shannon & Simpson Diversity Indices:** Computes ecological diversity metrics.  
- **SIR Epidemic Model:** Compartment model of infectious spread.  
- **Wright–Fisher Drift Simulation:** Models genetic drift of alleles over generations.  

## Optics
- **Diffraction Grating Calculator:** Computes diffraction maxima.  
- **Polarization (Malus’ Law):** I = I₀ cos²θ.  
- **Single Slit Diffraction Tool:** Computes diffraction minima.  
- **Thin Film Interference Calculator:** Identifies constructive/destructive interference.  
- **Thin Lens Combiner:** Computes effective focal length of multiple lenses.  
- **Young’s Double Slit Calculator:** Computes fringe spacing and positions.  

## Waves
- **Doppler Effect (Sound):** Frequency shift for moving source/observer in medium.  
- **Doppler Effect (Light):** Relativistic Doppler calculation.  
- **Standing Wave (Air Column):** Computes harmonics in open/closed air tubes.  
- **Standing Wave (String):** Computes harmonics in a vibrating string.  

## Math
- **Algebraic Calculator:** Evaluates algebraic expressions.  
- **Function Plotter:** Plots functions y=f(x).  
- **Quadratic Solver:** Finds roots, discriminant, and vertex.  
- **Triangle Solver:** Solves sides, angles, and area of triangles.  
- **Vector Calculator:** Performs dot, cross, projections. Includes interactive 3D view.  

---

# AI Assistant

**Category:** Core / Misc  

**Purpose:**  
The AI Assistant is a conversational agent inside ASH. It enables natural language queries, explains science concepts, helps navigate tools, and is designed to eventually orchestrate tool execution automatically.  

**Current Features:**  
- Simple chat interface with input/output log.  
- Backend powered by a local LLM model (`dolphin3:8b`).  
- Adjustable parameters: temperature, top_p, top_k, max_tokens.  
- Pure text generation without tool linkage.  

**Planned Features:**  
- **Tool Knowledge:** Read from an ASH manifest of all tools (name, category, inputs, outputs).  
- **Tool Orchestration:** Accept user queries, map to tool calls (JSON schema), and return results.  
- **Documentation Integration:** Use ASH documentation as knowledge base for explanations.  
- **Visualization Hooks:** Trigger plots or simulations when applicable.  
- **User Profiles:** Allow persistence of preferences and previous queries.  
- **Multi-step Reasoning:** Break down complex queries into sequences of tool calls.  

**Educational Role:**  
- Explains both results and theory behind them.  
- Acts as a tutor by linking formulas to intuitive examples.  
- Connects numerical outputs to visualizations (e.g., “Shall I show you the diffraction pattern?”).  

**Limitations (Now):**  
- No persistent memory.  
- No automatic tool execution.  
- Accuracy relies entirely on the LLM.  
- No built-in error-checking for physical units.  

**Example Interactions:**  
- User: *“How do I calculate escape velocity?”*  
  Assistant: *“Use the Escape Velocity tool. Formula: v = √(2GM/R). Provide the mass and radius of the planet.”*  

- User: *“Simulate logistic bacterial growth with r=0.5 for 10 hours.”*  
  Assistant: *“This maps to the Bacterial Growth Logistic tool. Inputs: N₀, r=0.5 h⁻¹, t=10 h. I can compute and plot N(t).”*  

- User: *“Show me optics tools.”*  
  Assistant: *“There are six smaller tools in Optics: Diffraction Grating, Polarization, Single Slit, Thin Film, Thin Lens, and Young’s Double Slit. Each computes conditions of optical interference or diffraction.”*  
