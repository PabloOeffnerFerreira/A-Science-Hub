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
**Version:** v1.0 (2025-08-22)

**Purpose**  
Visualize the electron shell structure of an element. Draws concentric shells with electrons placed evenly around them. Useful for teaching atomic structure or quickly checking shell configurations.

**Inputs**  
- **Element Symbol**: text input (e.g., `H`, `He`, `Fe`)  

**Outputs**  
- Visual plot of electron shells with electrons marked as dots  
- Nucleus labeled with element symbol  
- Status message showing save path of exported image  

**UI & Interaction**:contentReference[oaicite:2]{index=2}  
- Text entry for element symbol  
- “Draw & Save” button → generates plot and saves image  
- Canvas area shows the drawn structure  
- Status label displays saved file path or error message  

**Algorithm / Implementation**  
- Uses `load_element_data()` to load periodic table data (with `shells` list for each element):contentReference[oaicite:3]{index=3}  
- Radii calculation: scaled by `sqrt(n)` to fit higher-Z atoms  
- Each shell drawn as a circle (`matplotlib.patches.Circle`)  
- Electrons placed evenly around shell circumference  
- Nucleus labeled with symbol at center  
- Figure auto-scaled to fit shells (up to ~8.0 units radius)  
- Colours assigned per shell (cycled from predefined palette)  

**Units & Conversion**  
- Purely illustrative (not to physical scale)  

**Edge Cases & Validation**  
- Unknown element symbol or no `shells` data → warning popup (“No shell data for element…”)  
- Large-Z elements auto-scaled to fit figure  
- Minimum 1 electron drawn even if count = 0 (ensures shell visible)  

**Data Sources**  
- Periodic table JSON via `chemistry_utils.load_element_data()`:contentReference[oaicite:4]{index=4}  
- Keys: `shells` (list of electron counts per shell)  

**Logging & Export**  
- Image exported as PNG via `export_figure()`  
- Log entry added:  
  - Tool = `"Shell Visualiser"`  
  - Action = `"Draw"`  
  - Data = `{symbol, shells, image path}`  

**Chaining**  
- Output image and shell data could be reused by teaching tools or chain mode  

**Tests**  
- Example 1: `H` → 1 electron on first shell  
- Example 2: `He` → 2 electrons on first shell  
- Example 3: `Ne` → 2 electrons (K shell), 8 electrons (L shell)  
- Example 4: `Fe` → shells from periodic table JSON (2, 8, 14, 2)  

**Known Limitations / TODO**  
- Requires JSON file with `shells` data present  
- Strict text match (case-sensitive correction applied with `.capitalize()`)  
- No 3D orbital visualization (2D shells only)  
- Could add option to export SVG or higher-resolution images  

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

