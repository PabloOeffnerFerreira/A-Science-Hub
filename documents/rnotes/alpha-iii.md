# Release Notes (since alpha-ii.i)

## New Features
- Introduced the **ASH Assistant** (initial version, improvements, and now fully functional).
- Added **40+ small tools** across categories, including **Alphafold integration**.
- Added **Element Lab** and **DNA Lab**.
- Added **Electricity Lab**.
- Added **Mechanics Lab**, consolidating five tools into one.
- Enhanced *Shell Visualiser* and *Terminal Velocity* with 3D simulations and HUD displays.

## Bug Fixes
- Corrected Alphafold tool classification (moved out of *Microbiology*).
- Fixed *Equilibrium from ΔG* tool showing outputs from the *Arrhenius* tool.
- Fixed crash in *DNA Melting Temperature Tool* caused by duplicate code.
- Fixed crash when typing `"kg'"` with an apostrophe.
- Fixed *Temperature Conversion* bug.
- Silenced irrelevant ThreeJS console warning (caused by NGL dependency, not project code).

## Documentation
- Added comprehensive project documentation (several updates).
- Expanded and finalized `documentation.md`.
- Updated multiple README files.
- Documented all tools within `documentation.md`.
- added alpha-iii.md release notes

## Maintenance and Refactoring
- Standardized naming:
  - Renamed *momentum conversation* → *momentum conservation* tool.
  - Corrected filename typo: `equilibbrium_from_dG.py` → `equillibbrium_from_dG.py`.
- Reorganized categories:
  - Moved *Lens Mirror Tool* to **Optics** (previously in **Mechanics**).
  - Replaced all geology tools with the new **GeoLab**.
- Improved `.gitignore` and stopped tracking runtime JSON files.
- Added `test_all.py` for small tools.
- General project structure and cleanup.