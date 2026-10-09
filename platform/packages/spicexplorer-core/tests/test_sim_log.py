"""Log-text rules: ngspice-45 `.meas`/`print` forms, the failed-measure form, fatal lines."""

from __future__ import annotations

from spicexplorer_core.spice_engine import classify_line, fatal_lines, parse_measures

# Real ngspice-45 batch log excerpts (probe decks), verbatim.
LOG_INVALID_LINE = (
    "Warning: 'r1 a 0' is not a valid resistor instance line, ignored!\ni_ma = -0.000000e+00\n"
)
LOG_FAILED_MEAS = (
    "Error: measure  bad  when(WHEN) : out of interval\n"
    " meas tran bad when v(a)=5 failed!\n\ngood                =  1.500000e-09\n"
)
LOG_BAD_LET = (
    "Warning from checkvalid: vector nowhere is not available or has zero length.\n"
    'Error: RHS "v(nowhere)*2" invalid\n'
)


def test_parse_measures_real_forms():
    m, failed = parse_measures(LOG_FAILED_MEAS)
    assert m == {"good": 1.5e-09} and failed == ["bad"]
    m, failed = parse_measures(
        "i_ma = 1.000000e+00\nugf = 1.2345e+06 at=  3.2\n"
        "Total analysis time (seconds) = 0.001\nDoing analysis at TEMP = 27.0\n"
    )
    assert m == {"i_ma": 1.0, "ugf": 1.2345e6} and failed == []


def test_parse_measures_legacy_failed_form_and_dedup():
    m, failed = parse_measures("tsettle = failed\n meas tran tsettle when v(a)=5 failed!\n")
    assert m == {} and failed == ["tsettle"]


def test_fatal_lines_classification():
    assert fatal_lines(LOG_INVALID_LINE), "an ignored device line is the silent-zero class"
    assert fatal_lines(LOG_BAD_LET)
    assert fatal_lines("doAnalyses: iteration limit reached")
    assert fatal_lines("Transient solution failed")
    assert fatal_lines("doAnalyses: TRAN:  Timestep too small; time = 1e-9")
    assert fatal_lines("Error on line 12 : xm1 ... Unknown model type xyz")
    assert fatal_lines("could not find a valid modelname")
    assert fatal_lines("simulation interrupted")
    assert not fatal_lines(LOG_FAILED_MEAS), "a failed .meas is a NaN metric, not a fatal run"
    assert not fatal_lines(
        "Warning: singular matrix:  check nodes a and b\n"
        "Note: Starting dynamic gmin stepping\nWarning: vd: no DC value\n"
    ), "warning-level lines are never fatal"
    assert fatal_lines("singular matrix: check nodes a and b"), (
        "the bare form is the analysis giving up"
    )


def test_classify_levels():
    assert classify_line("Warning: singular matrix:  check nodes a and b") == "warning"
    assert (
        classify_line("Warning: 'r1 a 0' is not a valid resistor instance line, ignored!")
        == "error"
    )
    assert classify_line("Note: Starting dynamic gmin stepping") == "note"
    assert classify_line("No. of Data Rows : 601") == "info"
    assert classify_line("Error: measure  bad  when(WHEN) : out of interval") == "error"


# More real ngspice-45 forms (probe decks under $SX_SCRATCH, verbatim).
LOG_TRAILER = (
    "Total analysis time (seconds) = 0.0171455\nTotal elapsed time (seconds) = 0.026 \n"
    "Total DRAM available = 257516.355 MB.\nDRAM currently available = 16794.793 MB.\n"
    "Maximum ngspice program size =   30.121 MB.\nStack = 0 bytes.\nLibrary pages =    2.051 MB.\n"
)


def test_parse_measures_delay_dotted_and_range_forms():
    m, failed = parse_measures(
        "dly                 =  6.935673e-10 targ=  1.743567e-09 trig=  1.050000e-09\n"
        "m.dot               =  1.000000e+00 at=  1.609500e-08\n"
        "vavg                =  8.429713e-01 from=  2.000000e-09 to=  6.050000e-09\n"
        "integ_x             =  5.91483e-09 from=  0.00000e+00 to=  1.00000e-08\n"
        "trise               =   1.50000e-09\n" + LOG_TRAILER
    )
    assert m == {
        "dly": 6.935673e-10,
        "m.dot": 1.0,
        "vavg": 0.8429713,
        "integ_x": 5.91483e-09,
        "trise": 1.5e-09,
    }
    assert failed == []


def test_parse_measures_non_finite_scalars_are_floats():
    """`print` of an overflow/indeterminate `let` prints `inf` / `-inf` / `-nan`; they are
    scalars (the statement did not fail), so they land in `measures` as non-finite floats
    for the caller's `isfinite` gate — never in `failed`, which is ngspice's own list."""
    import math

    m, failed = parse_measures("big = inf\nnegbig = -inf\nnn = -nan\ne = inf\n")
    assert failed == [] and set(m) == {"big", "negbig", "nn", "e"}
    assert m["big"] == math.inf and m["negbig"] == -math.inf and math.isnan(m["nn"])


def test_parse_measures_print_contract_is_a_named_let():
    """`print <expression>` echoes the expression as the name (`-i(v1) = …`, `i_ma*2 = …`,
    `v(out)[3] = …`); those are not parsed — the contract is `let x = …; print x`."""
    m, failed = parse_measures(
        "i_ma = 1.000000e+00\n-i(v1) = 1.000000e-03\nneg = -1.00000e+00\n"
        "i_ma*2 = 2.000000e+00\nv(out)[3] = 3.000000e-01\nmn = -1.00000e-15\n"
    )
    assert m == {"i_ma": 1.0, "neg": -1.0, "mn": -1e-15} and failed == []


def test_parse_measures_body_meas_failed_form():
    m, failed = parse_measures(
        "Error: measure  bad  when(WHEN) : out of interval\n .meas tran bad when v(a)=5 failed!\n"
        " meas ac neverf when vdb(out)=vexprint2 failed!\n meas tran bad2 max v(nowhere) failed!\n"
    )
    assert m == {} and failed == ["bad", "neverf", "bad2"]


def test_fatal_lines_matches_a_lowercase_runner_marker():
    """The `Fatal|FATAL` pattern was case-SENSITIVE, so a runner's own injected marker —
    analog-db's `fatal: ngspice timed out after <n>s` (runner.py) — was classified `info` and
    `fatal_lines` came back empty on a timed-out run."""
    log = "some output\nfatal: ngspice timed out after 30s\n"
    assert classify_line("fatal: ngspice timed out after 30s") == "error"
    assert fatal_lines(log) == ["fatal: ngspice timed out after 30s"]
    assert classify_line("FATAL: out of memory") == "error"
    assert classify_line("** Fatal error in ngspice") == "error"


def test_fatal_lines_matches_a_missing_include_or_model_file():
    """ngspice prints `cannot open` bare and then runs on a circuit with no models. There was no
    pattern for it at all, so the run looked clean."""
    assert classify_line('cannot open file "/opt/pdk/foo.lib"') == "error"
    assert classify_line("Can't open /opt/pdk/foo.lib") == "error"
    assert fatal_lines('cannot open file "/opt/pdk/foo.lib"\n') == [
        'cannot open file "/opt/pdk/foo.lib"'
    ]


def test_a_warning_that_mentions_fatal_is_still_only_a_warning():
    """The `fatal` match is case-insensitive but stays LINE-ANCHORED, and `cannot open` /
    `fatal error` sit after the warning patterns — so "warnings are never fatal" still holds."""
    for line in (
        "Warning: a fatal error was avoided by gmin stepping",
        "Warning: cannot open the optional .ic file; continuing",
        "WARNING (SPECTRE-123): fatal error suppressed",
        "Note: fatal errors are logged to ngspice.out",
    ):
        assert classify_line(line) in ("warning", "note"), line
        assert fatal_lines(line + "\n") == [], line
