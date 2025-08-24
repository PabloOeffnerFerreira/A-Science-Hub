# conftest.py
#
# One-file setup + tests for ASH tools.
# - Headless Qt (qapp fixture)
# - sys.path injection for all /tools subfolders
# - Helper parsers
# - Compact test coverage across Astronomy, Biology, Chemistry,
#   Electricity, Math, Mechanics, Microbiology, Optics, Waves
#
# NOTE:
# - AlphaFold is excluded (requires network & 3D viewer).
# - These are “UI-path” tests: they create each Tool, set inputs,
#   call the private _go()/compute button handler, and parse result labels.
#
# Run:  pytest -q
#
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
import math
import re
import types
import importlib
import pytest

# --- sys.path setup so bare module names like "nernst_equation" import ---
from pathlib import Path

# Headless Qt (in case it isn't set elsewhere)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# This file is at: <repo_root>/misc/tests/test_all.py
REPO_ROOT = Path(__file__).resolve().parents[2]   # parents: [tests, misc, <root>]
TOOLS_DIR = REPO_ROOT / "tools"

if not TOOLS_DIR.is_dir():
    raise RuntimeError(f"Couldn't find tools/ at: {TOOLS_DIR}")

# Add each category folder (astronomy, biology, chemistry, ...) to sys.path
for sub in TOOLS_DIR.iterdir():
    if sub.is_dir():
        sys.path.insert(0, str(sub))

# ---------- Test environment & paths ----------------------------------------

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TOOLS_DIR = os.path.join(PROJECT_ROOT, "tools")

# Add each first-level subfolder of /tools to import path (astronomy, biology, ...)
if os.path.isdir(TOOLS_DIR):
    for name in os.listdir(TOOLS_DIR):
        p = os.path.join(TOOLS_DIR, name)
        if os.path.isdir(p):
            if p not in sys.path:
                sys.path.insert(0, p)

# Headless Qt (PyQt/PySide agnostic import)
qt_api = None
for api in ("PyQt6", "PyQt5", "PySide6", "PySide2"):
    try:
        qt_api = api
        QtWidgets = importlib.import_module(f"{api}.QtWidgets")
        QtCore = importlib.import_module(f"{api}.QtCore")
        break
    except Exception:
        continue
if qt_api is None:
    raise RuntimeError("No Qt binding (PyQt5/6 or PySide2/6) available for tests.")

@pytest.fixture(scope="session")
def qapp():
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    return app

# ---------- Helpers ---------------------------------------------------------

_num_re = re.compile(r"([\-+]?(\d+(\.\d*)?|\.\d+)([eE][\-+]?\d+)?)")

def num_from_text(text, key=None):
    """
    Extract the first number after optional 'key' token in a label string.
    """
    if key:
        # find key, then parse a number that follows
        m = re.search(rf"{re.escape(key)}[^0-9\-+]*({_num_re.pattern})", text)
        if not m:
            raise AssertionError(f"Could not find number for key {key!r} in: {text!r}")
        return float(m.group(1))
    # else: first number in string
    m = _num_re.search(text)
    if not m:
        raise AssertionError(f"No number in: {text!r}")
    return float(m.group(1))

def make_tool(modname):
    """
    Import module and create Tool() instance.
    Many tools expose a class `Tool` with ._go() writing into a QLabel result.
    """
    mod = importlib.import_module(modname)
    assert hasattr(mod, "Tool"), f"{modname} missing Tool class"
    return mod.Tool()

def set_text(widget, value):
    # Convenience wrapper for QLineEdit-like
    try:
        widget.setText(str(value))
    except Exception as e:
        raise AssertionError(f"set_text failed on {widget} with {value}: {e}")

# Some tools label keys used in result labels:
# We'll parse with these keys where applicable
KEYS = {
    "observed_fprime": "Observed f'",
    "lambda": "λ",
    "freq": "f",
    "speed": "v",
    "accel_c": "a_c",
    "omega": "ω",
}

# ---------- ASTRONOMY -------------------------------------------------------

def test_astronomy_blackbody_peak_wien(qapp):
    t = make_tool("blackbody_peak_wien")
    # Mode likely default T→λ_peak. Use Sun's ~5778 K
    set_text(t.input_value, "5778")  # if UI uses .input_value
    t._go()
    txt = t.result.text()
    # Expect ~ 501.5 nm
    lam = num_from_text(txt)
    assert 4.9e-7 < lam < 5.2e-7 or 495 < lam < 520  # accept meters or nm

def test_astronomy_exoplanet_transit_depth(qapp):
    t = make_tool("exoplanet_transit_depth")
    set_text(t.Rp, "6371")     # km
    set_text(t.Rs, "696340")   # km
    t._go()
    depth_txt = t.result.text()
    val = num_from_text(depth_txt)
    assert 0.008 < val < 0.0095  # ~0.00837 %

def test_astronomy_habitable_zone_scaling(qapp):
    t = make_tool("habitable_zone_estimator")
    set_text(t.L, "1.0")
    t._go()
    txt = t.result.text()
    assert "AU" in txt

def test_astronomy_distance_modulus(qapp):
    t = make_tool("magnitude_distance_modulus")
    # mode m,M -> distance
    t.mode.setCurrentIndex(0)
    set_text(t.m, "10")
    set_text(t.M, "5")
    t._go()
    txt = t.result.text()
    d = num_from_text(txt, "d")
    assert 95 <= d <= 105

def test_astronomy_kepler3(qapp):
    t = make_tool("orbital_period_kepler3")
    set_text(t.a, "1.496e11")
    set_text(t.M, "1.989e30")
    t._go()
    txt = t.result.text()
    T = num_from_text(txt, "T")
    assert 3.0e7 < T < 3.5e7  # ~1 year

def test_astronomy_parallax(qapp):
    t = make_tool("parallax_distance")
    set_text(t.p, "0.1")
    t._go()
    txt = t.result.text()
    d = num_from_text(txt, "d")
    assert 9.0 <= d <= 11.0

def test_astronomy_redshift_relativistic(qapp):
    t = make_tool("redshift_calculator")
    t.mode.setCurrentText("z → v (relativistic)")
    set_text(t.input_value, "0.01")
    t._go()
    txt = t.result.text()
    v = num_from_text(txt, "v")
    assert 2.0e6 < v < 3.5e6  # around 0.01c

def test_astronomy_rocket_eq(qapp):
    t = make_tool("rocket_equation_tsiolkovsky")
    set_text(t.isp, "300")
    set_text(t.m0, "50000")
    set_text(t.mf, "15000")
    t._go()
    txt = t.result.text()
    dv = num_from_text(txt, "Δv")
    assert 3000 < dv < 4000

def test_astronomy_stellar_luminosity(qapp):
    t = make_tool("stellar_luminosity_sb")
    set_text(t.R, "6.96e8")
    set_text(t.T, "5778")
    t._go()
    txt = t.result.text()
    L = num_from_text(txt, "L")
    assert 3e26 < L < 5e26

def test_astronomy_surface_gravity(qapp):
    t = make_tool("surface_gravity")
    set_text(t.M, "5.972e24")
    set_text(t.R, "6.371e6")
    t._go()
    gtxt = t.result.text()
    g = num_from_text(gtxt, "g")
    assert 9.7 < g < 10.0

# ---------- BIOLOGY ---------------------------------------------------------

def test_bio_amino_acid_composition(qapp):
    t = make_tool("amino_acid_composition")
    set_text(t.seq, "MGLSDGEWQLVNVWGK")
    t._go()
    assert "Length" in t.result.text()

def test_bio_dna_melting_temp(qapp):
    t = make_tool("dna_melting_temp")
    set_text(t.seq, "ATGCCGGGATATATGC")
    set_text(t.na, "50")
    t.meth.setCurrentIndex(0)  # Wallace
    t._go()
    txt = t.result.text()
    tm = num_from_text(txt, "Tm")
    assert 30 <= tm <= 80

def test_bio_michaelis_menten(qapp):
    t = make_tool("enzyme_kinetics_michaelis_menten")
    set_text(t.vmax, "1.0")
    set_text(t.km, "0.5")
    set_text(t.S, "0.25")
    t._go()
    txt = t.result.text()
    v = num_from_text(txt, "v")
    assert math.isclose(v, 0.333333, rel_tol=1e-3, abs_tol=1e-6)

def test_bio_hardy_weinberg(qapp):
    t = make_tool("hardy_weinberg")
    set_text(t.p, "0.6")
    t._go()
    txt = t.result.text()
    assert "f(AA)=0.360" in txt and "f(aa)=0.160" in txt

def test_bio_osmosis_tonicity(qapp):
    t = make_tool("osmosis_tonicity")
    set_text(t.int_e, "30")
    set_text(t.ext_e, "50")
    t._assess()
    assert "Hypotonic" in t.result.text()

def test_bio_ph_calculator(qapp):
    t = make_tool("ph_calculator")
    set_text(t.h, "1e-3")
    set_text(t.oh, "")
    t._calc()
    pH = num_from_text(t.out.text(), "pH")
    assert 2.9 < pH < 3.2

def test_bio_population_growth(qapp):
    t = make_tool("population_growth_calculator")
    set_text(t.n0, "800")
    set_text(t.r, "0.546")
    set_text(t.t, "2")
    t._calc()
    assert "Population after" in t.out.text()

def test_bio_crispr_guides(qapp):
    t = make_tool("crispr_guide_finder")
    set_text(t.seq, "ACGTACGTACGTGGTTACCGG")
    set_text(t.glen, "20")
    t._go()
    # may be zero depending on PAM logic; at least should not crash
    assert "guide" in t.result.text().lower()

# ---------- CHEMISTRY -------------------------------------------------------

def test_chem_buffer_henderson(qapp):
    t = make_tool("buffer_ph_henderson")
    set_text(t.pKa, "4.76")
    set_text(t.Am, "0.1")
    set_text(t.HA, "0.1")
    t._go()
    pH = num_from_text(t.result.text(), "pH")
    assert 4.7 < pH < 4.8

def test_chem_equillibrium_from_dG(qapp):
    t = make_tool("equillibbrium_from_dG")
    set_text(t.dG, "-5.0")
    set_text(t.T, "298")
    t._go()
    K = num_from_text(t.result.text(), "K")
    assert 6.0 < K < 10.0

def test_chem_ideal_gas_P(qapp):
    t = make_tool("ideal_gas_solver")
    t.target.setCurrentText("P (Pa)")
    set_text(t.P, "101325")
    set_text(t.V, "0.024")
    set_text(t.n, "1.0")
    set_text(t.T, "298")
    t._go()
    P = num_from_text(t.result.text(), "P")
    assert 1.0e5 * 0.9 < P < 1.1e5

def test_chem_molar_mass(qapp):
    t = make_tool("molar_mass")
    set_text(t.formula_entry, "CuSO4·5H2O")
    t._calculate()
    assert "Total Molecular Weight" in t.result.toPlainText()

def test_chem_nernst(qapp):
    t = make_tool("nernst_equation")
    set_text(t.E0, "1.10")
    set_text(t.n, "2")
    set_text(t.T, "298")
    set_text(t.Q, "1.0")
    t._go()
    E = num_from_text(t.result.text(), "E")
    assert 1.09 < E < 1.11

def test_chem_reaction_balancer(qapp):
    t = make_tool("reaction_balancer")
    t.input.setPlainText("H2 + O2 -> H2O")
    t._balance_all()
    items = [t.list.item(i).text() for i in range(t.list.count())]
    assert any("2 H2 + O2 -> 2 H2O" in text for text in items)

def test_chem_arrhenius(qapp):
    t = make_tool("reaction_rate_arrhenius")
    set_text(t.A, "1e7")
    set_text(t.Ea, "50")
    set_text(t.T, "298")
    t._go()
    k = num_from_text(t.result.text(), "k")
    assert 1e-3 < k < 1e0

def test_chem_titration_curve(qapp):
    t = make_tool("titration_curve")
    set_text(t.ca, "0.1")
    set_text(t.cb, "0.1")
    set_text(t.va, "0.025")
    set_text(t.vb, "0.020")
    t._go()
    assert "pH" in t.result.text()

# ---------- ELECTRICITY -----------------------------------------------------

def test_elec_biot_savart_straight_wire(qapp):
    t = make_tool("biot_savart_straight_wire")
    set_text(t.I, "10")
    set_text(t.r, "0.05")
    t._go()
    B = num_from_text(t.result.text(), "B")
    assert B > 0

def test_elec_lorentz_force(qapp):
    t = make_tool("lorentz_force")
    set_text(t.q, "1e-6")
    set_text(t.vx, "1000")
    set_text(t.Bx, "0.2")
    set_text(t.Ex, "90")
    t._go()
    F = num_from_text(t.result.text(), "F")
    assert F > 0

def test_elec_rlc_resonance(qapp):
    t = make_tool("rlc_resonance")
    set_text(t.L, "0.1")
    set_text(t.C, "1e-6")
    t._go()
    f0 = num_from_text(t.result.text(), "f₀")
    assert 400 < f0 < 600  # expected ~503 Hz

def test_elec_skin_depth(qapp):
    t = make_tool("skin_depth_calculator")
    set_text(t.f, "1e6")
    set_text(t.mu_r, "1")
    set_text(t.sigma, "5.8e7")
    t._go()
    d = num_from_text(t.result.text(), "δ")
    assert d > 0

def test_elec_tline(qapp):
    t = make_tool("transmission_line_calculator")
    set_text(t.Lp, "2e-7")
    set_text(t.Cp, "8e-11")
    t._go()
    txt = t.result.text()
    assert "Z0" in txt and "v" in txt


# ---------- MATH ------------------------------------------------------------

def test_math_algebraic_calculator(qapp):
    t = make_tool("algebraic_calculator")
    set_text(t.func_input, "x**2 + 3*x - 2")
    set_text(t.x_input, "4.7264")
    t._calculate()
    txt = t.result.text()
    y = num_from_text(txt.split("=", 1)[1])
    # f(4.7264) ≈ 34.518
    assert math.isclose(y, 34.51805696, rel_tol=1e-9)

def test_math_quadratic_solver(qapp):
    t = make_tool("quadratic_solver")
    set_text(t.a_edit, "1")
    set_text(t.b_edit, "0")
    set_text(t.c_edit, "0")
    t._solve_and_plot()
    out = t.out.text()
    assert "Roots x₁, x₂ = -0, 0" in out or "Roots x₁, x₂ = 0, 0" in out

def test_math_triangle_solver(qapp):
    t = make_tool("triangle_solver")
    set_text(t.in_a, "40")
    set_text(t.in_b, "73.55")
    set_text(t.in_c, "68.58")
    t.on_solve()
    out = t.out_label.text()
    assert "Area (Heron)" in out

def test_math_vector_projection(qapp):
    t = make_tool("vector_calculator")
    t.operation.setCurrentText("Projection of A onto B")
    set_text(t.a_in, "1, 3, 4")
    set_text(t.b_in, "6, 2, 9")
    t._calc()
    assert "proj_B(A)" in t.result.text()

# ---------- MECHANICS -------------------------------------------------------

def test_mech_uniform_circular_motion(qapp):
    t = make_tool("uniform_circular_motion")
    set_text(t.r, "1.0")
    set_text(t.T, "2.0")
    t._go()
    txt = t.result.text()
    v = num_from_text(txt, KEYS["speed"])
    ac = num_from_text(txt, KEYS["accel_c"])
    assert 3.0 < v < 3.2
    assert 9.0 < ac < 10.5

def test_mech_work_power(qapp):
    t = make_tool("work_power")
    set_text(t.F, "10")
    set_text(t.s, "3")
    set_text(t.theta, "0")
    set_text(t.t, "")
    t._go()
    W = num_from_text(t.result.text(), "W")
    assert math.isclose(W, 30.0, rel_tol=1e-6)

def test_mech_work_energy_theorem(qapp):
    t = make_tool("work_energy_theorem")
    set_text(t.m, "1")
    set_text(t.v0, "0")
    set_text(t.vf, "2")
    t._go()
    W = num_from_text(t.result.text(), "W")
    assert math.isclose(W, 2.0, rel_tol=1e-6)

def test_mech_terminal_velocity_numbers(qapp):
    t = make_tool("terminal_velocity")
    set_text(t.mass_edit, "1.0")
    set_text(t.area_edit, "0.5")
    set_text(t.height_edit, "100")
    t.air_mode.setCurrentText("Air Density")
    set_text(t.air_value, "1.225")
    t.cd_preset.setCurrentText("Sphere (0.47)")
    set_text(t.cd_edit, "0.47")
    t.calculate()
    txt = t.result_label.text()
    assert "Terminal Velocity" in txt
    # Extract terminal velocity from label
    vt = num_from_text(txt, "Terminal Velocity")
    assert 7.5 < vt < 9.5

# ---------- MICROBIOLOGY ----------------------------------------------------

def test_micro_agar_diffusion_demo(qapp):
    t = make_tool("agar_diffusion_demo")
    set_text(t.D, "1.0")
    set_text(t.t, "4")
    t._go()
    RMS = num_from_text(t.result.text())
    assert 2.0 < RMS < 3.0

def test_micro_bacterial_growth_logistic(qapp):
    t = make_tool("bacterial_growth_logistic")
    set_text(t.N0, "1e6")
    set_text(t.K, "1e9")
    set_text(t.r, "0.8")
    set_text(t.t, "5")
    t._go()
    assert "N(t)" in t.result.text()

def test_micro_chemostat_steady_state(qapp):
    t = make_tool("chemostat_steady_state")
    set_text(t.D, "0.4")
    set_text(t.umax, "1.0")
    set_text(t.Ks, "0.5")
    set_text(t.Sin, "10")
    t._go()
    txt = t.result.text()
    assert "μ*" in txt and "S*" in txt

def test_micro_monod_kinetics(qapp):
    t = make_tool("monod_kinetics")
    set_text(t.umax, "1.0")
    set_text(t.Ks, "0.5")
    set_text(t.S, "0.8")
    t._go()
    mu = num_from_text(t.result.text(), "μ")
    assert 0.5 < mu < 0.7

def test_micro_phylo_hamming(qapp):
    t = make_tool("phylo_distance_hamming")
    set_text(t.a, "ATGCCGTA")
    set_text(t.b, "ATGACGTT")
    t._go()
    d = num_from_text(t.result.text())
    assert d == pytest.approx(2, rel=0, abs=1e-9)

def test_micro_quorum_sensing(qapp):
    t = make_tool("quorum_sensing_threshold")
    set_text(t.A, "1.0")
    set_text(t.K, "1.0")
    set_text(t.n, "2")
    set_text(t.Rmax, "1.0")
    t._go()
    resp = num_from_text(t.result.text(), "Response")
    assert 0.45 < resp < 0.55

def test_micro_shannon_simpson(qapp):
    t = make_tool("shannon_simpson_diversity")
    set_text(t.abunds, "0.4,0.3,0.2,0.1")
    t._go()
    txt = t.result.text()
    assert "Shannon H" in txt and "Simpson D" in txt

def test_micro_sir_epidemic(qapp):
    t = make_tool("sir_epidemic_model")
    set_text(t.S0, "990")
    set_text(t.I0, "10")
    set_text(t.R0, "0")
    set_text(t.beta, "0.3")
    set_text(t.gamma, "0.1")
    set_text(t.t, "30")
    t._go()
    assert "R0 ≈ 3.000" in t.result.text()

def test_micro_wright_fisher(qapp):
    t = make_tool("wright_fisher_drift")
    set_text(t.N, "100")
    set_text(t.p0, "0.5")
    set_text(t.gens, "5")
    set_text(t.trials, "1")
    t._go()
    assert "Mean allele frequency" in t.result.text()

# ---------- OPTICS ----------------------------------------------------------

def test_optics_diffraction_grating(qapp):
    t = make_tool("diffraction_grating")
    set_text(t.lines, "600")
    set_text(t.m, "1")
    set_text(t.lmbd, "532")
    t._go()
    txt = t.result.text()
    assert "θ" in txt and "d =" in txt

def test_optics_polarization_malus(qapp):
    t = make_tool("polarization_malus")
    set_text(t.I0, "1.0")
    set_text(t.theta, "30")
    t._go()
    I = num_from_text(t.result.text(), "I")
    assert 0.7 < I < 0.76  # cos^2(30°)=0.75

def test_optics_single_slit(qapp):
    t = make_tool("single_slit_diffraction")
    set_text(t.lmbd, "632.8")
    set_text(t.a, "1e-4")
    set_text(t.L, "1.0")
    t._go()
    txt = t.result.text()
    assert "θ" in txt and "a =" in txt

def test_optics_thin_film(qapp):
    t = make_tool("thin_film_interference")
    set_text(t.t, "300")
    set_text(t.n, "1.33")
    t.cond.setCurrentText("Constructive")
    set_text(t.m, "0")
    t._go()
    assert "λ ≈" in t.result.text()

def test_optics_thin_lens_combiner(qapp):
    t = make_tool("thin_lens_combiner")
    set_text(t.f1, "50")
    set_text(t.f2, "100")
    set_text(t.d, "10")
    t._go()
    feq = num_from_text(t.result.text(), "f_eq")
    assert 30 < feq < 40

def test_optics_young_double_slit(qapp):
    t = make_tool("young_double_slit")
    set_text(t.lmbd, "532")
    set_text(t.d, "1e-4")
    set_text(t.L, "1.0")
    t._go()
    txt = t.result.text()
    assert "θ" in txt and "d =" in txt

def test_optics_lens_mirror_equation(qapp):
    t = make_tool("lens_mirror_equation")
    set_text(t.f, "0.5")
    set_text(t.do, "2")
    t.kind.setCurrentText("Lens (Converging)")
    t._calc()
    assert "image is real" in t.result.text().lower()

# ---------- WAVES -----------------------------------------------------------

def test_waves_standing_air_both_open(qapp):
    t = make_tool("standing_wave_air")
    set_text(t.L, "0.5")
    set_text(t.n, "1")
    set_text(t.v, "343")
    t.ends.setCurrentText("Both Open")
    t._go()
    lam = num_from_text(t.result.text(), "λ")
    f = num_from_text(t.result.text(), "f")
    assert math.isclose(lam, 1.0, rel_tol=1e-6)
    assert math.isclose(f, 343.0, rel_tol=1e-6)

def test_waves_standing_string_basic(qapp):
    t = make_tool("standing_wave_string")
    set_text(t.L, "1")
    set_text(t.n, "1")
    set_text(t.v, "100")
    t._go()
    lam = num_from_text(t.result.text(), "λ")
    f = num_from_text(t.result.text(), "f")
    assert math.isclose(lam, 2.0, rel_tol=1e-6)
    assert math.isclose(f, 50.0, rel_tol=1e-6)

def test_waves_doppler_sound_identity(qapp):
    t = make_tool("doppler_effect")
    set_text(t.f, "440")
    set_text(t.v, "343")
    set_text(t.vs, "0")
    set_text(t.vo, "0")
    t._go()
    fprime = num_from_text(t.result.text(), "f'")
    assert math.isclose(fprime, 440.0, rel_tol=1e-9)


def test_waves_doppler_sound_observer_towards(qapp):
    t = make_tool("doppler_effect")
    set_text(t.f, "440")
    set_text(t.v, "343")
    set_text(t.vs, "0")
    set_text(t.vo, "10")
    t._go()
    fprime = num_from_text(t.result.text(), "f'")
    assert fprime > 440.0

def test_waves_doppler_light_small_v(qapp):
    t = make_tool("doppler_light")
    set_text(t.f, "6e14")
    set_text(t.v, "1e6")  # + => approaching
    t._go()
    fprime = num_from_text(t.result.text(), "f'")
    assert fprime > 5.95e14