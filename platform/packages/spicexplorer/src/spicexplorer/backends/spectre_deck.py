"""Spectre deck composition + parameter injection.

Composes **DUT × stimulus × params (+ corner)** into a runnable `.scs`. Measurements are
NOT composed here — they emit separately (`.ocn`) and never into the deck. This is
pure string work: no circuitgraph import at module level (leaf-tool layering — peer
tools never hard-import each other); the optional ngspice→Spectre translation binds
lazily inside :func:`deck_spec_from_ngspice`, mirroring the lazy ``virtuoso_bridge``
import in ``backends.spectre``.

Deck-side analysis contract (live-validated): the bridge's PSF parser
keys result prefixes off the PSF *file names*, i.e. the analysis *statement names* —
``ac … ``→``ac_*`` keys, ``dc``/``dcOp``→``dc_*`` (op node voltages land there); per-MOS
op scalars additionally need an ``info what=oppoint`` dump (post-parsed by
``backends.spectre.parse_psfascii_oppoint``). :func:`render_spectre_deck` warns when an
analysis statement's name breaks that contract.

Corner-include landmine: ``.lib`` → ``include … section=`` must target the
self-contained *corner* sections, never the raw device-model sections (which fail
with a wall of undefined-parameter errors).
Corner includes arrive via ``apply_corner`` → ``render_spectre_deck(corner_includes=…)``.

Case rule: the composed deck's **parameter namespace is lowercase** (SPICE is
case-insensitive, Spectre is not — the translator folds every parameter symbol to
lowercase), so injection keys are folded to lowercase on merge.

Composition-layer mapping (``Project_Setup``): one :class:`SpectreDeckSpec` per
testbench (its stimulus + DUT blocks); ``dut_params``/testbench params inject through
``Simulator.update_params`` → ``parameters=``; corners through ``apply_corner``;
``target_specs`` → analyses selection stays declarative at the call site.
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping, Sequence

__all__ = [
    "SpectreDeckSpec",
    "render_spectre_deck",
    "render_native_scs",
    "deck_spec_from_ngspice",
    "deck_spec_from_native",
    "ac_analysis",
    "dc_sweep_analysis",
    "noise_analysis",
    "transient_analysis",
    "pss_analysis",
    "pac_analysis",
    "pnoise_analysis",
    "stb_analysis",
    "sine_source",
    "dc_oppoint_analysis",
    "DEFAULT_SIMULATOR_OPTIONS",
    "OPPOINT_INFO_LINE",
    "SAVE_OPTIONS_LINE",
]

logger = logging.getLogger(__name__)

DEFAULT_SIMULATOR_OPTIONS = (
    "simulatorOptions options gmin=1e-13 reltol=1e-4 vabstol=1e-6 iabstol=1e-12"
)
OPPOINT_INFO_LINE = "finalTimeOP info what=oppoint where=rawfile"
SAVE_OPTIONS_LINE = "saveOptions options save=allpub"

# PSF prefixes are keyed by analysis *names*: these types must carry these names.
_CONTRACT_NAMES: dict[str, tuple[str, ...]] = {
    "ac": ("ac",),
    "dc": ("dc", "dcOp"),
    "pss": ("pss",),
    "pac": ("pac",),
    "stb": ("stb",),
}


def dc_oppoint_analysis() -> str:
    """The op-point analysis statement, named per the PSF key contract (``dc_*`` keys)."""
    return "dcOp dc"


def ac_analysis(start: float = 1e3, stop: float = 1e8, dec: int = 101) -> str:
    """An AC sweep named ``ac`` per the PSF key contract (``ac_*`` keys).

    Numeric start/stop only — SPICE eng-suffix case is a Spectre landmine (``100MEG``
    is SPICE mega; Spectre reads ``M`` as mega but ``m`` as milli), so no suffix at all.
    """
    return f"ac ac start={_fmt(float(start))} stop={_fmt(float(stop))} dec={int(dec)}"


def dc_sweep_analysis(dev: str, start: float, stop: float, step: float, *, param: str = "dc") -> str:
    """A Spectre DC *sweep* named ``dc`` (→ a ``dc.dc`` swept PSF), sweeping a source.

    Emits ``dc dc dev=<instance> param=dc start=… stop=… step=…`` — the Spectre analogue of
    the ngspice ``dc <src> <start> <stop> <step>`` card (the analog-db ``linearity``
    template's ICMR sweep). The swept transfer lands in its own psfascii PSF (``dc.dc``)
    read by :func:`backends.spectre.read_swept_psf`, so the ``{meas: icmr_*}`` recipes pull
    the ``(vin, vout)`` traces uniformly for ngspice and Spectre. NOTE the sibling op-point
    analysis (``dcOp dc``) also leaves a ``.dc`` PSF (``dcOp.dc``) — the reader prefers the
    exact ``dc.dc`` file, but avoid composing both when the sweep is the payload. Numeric
    start/stop/step only (the eng-suffix-case landmine, matching :func:`ac_analysis`).
    """
    return (
        f"dc dc dev={dev} param={param} "
        f"start={_fmt(float(start))} stop={_fmt(float(stop))} step={_fmt(float(step))}"
    )


def noise_analysis(
    output: str,
    ref: str = "0",
    *,
    iprobe: str | None = None,
    start: float = 1e3,
    stop: float = 1e8,
    dec: int = 50,
) -> str:
    """A Spectre small-signal noise analysis named ``noise`` (→ a ``noise.noise`` PSF).

    Emits ``noise ( <output> <ref> ) noise start=… stop=… dec=… [iprobe=…]``: the *output*
    noise voltage spectral density is taken across the ``(output, ref)`` port (the
    ``onoise`` spectrum). Passing ``iprobe`` — the input source *instance* carrying the AC
    stimulus (e.g. the translated ``VINP`` ``vsource`` with ``mag=1``) — additionally makes
    Spectre report the *input-referred* spectrum (``inoise``) and the noise gain.

    Like the swept AC/tran results, this lands in its OWN psfascii PSF (``noise.noise``) in
    the run's ``-raw`` dir — read by :func:`backends.spectre.read_swept_psf`, not the
    bridge's flat op-point dict — so the engine-neutral registry's ``inoise_total`` /
    ``onoise_total`` recipes integrate the density uniformly for ngspice and Spectre.

    Numeric start/stop only — SPICE eng-suffix case is a Spectre landmine (``100MEG`` is
    SPICE mega; Spectre reads ``M`` as mega but ``m`` as milli), matching :func:`ac_analysis`.
    """
    parts = [
        "noise",
        f"( {output} {ref} )",
        "noise",
        f"start={_fmt(float(start))}",
        f"stop={_fmt(float(stop))}",
        f"dec={int(dec)}",
    ]
    if iprobe:
        parts.append(f"iprobe={iprobe}")
    return " ".join(parts)


def transient_analysis(
    stop: float,
    *,
    step: float | None = None,
    start: float = 0.0,
    errpreset: str | None = "conservative",
) -> str:
    """A Spectre transient analysis named ``tran`` (→ a ``tran.tran`` PSF).

    Emits ``tran tran stop=… [step=…] [start=…] [errpreset=…]``. Like the AC/noise swept
    analyses this lands in its own psfascii PSF (``tran.tran``) read by
    :func:`backends.spectre.read_swept_psf`, so the transient recipes (``{meas: slew}`` /
    ``{meas: t_settle}`` / ``{meas: thd}``) pull the ``time`` + output waves uniformly for
    ngspice and Spectre. Pair with a large-signal :func:`sine_source` for a THD
    (SPICE ``.four``-equivalent) measurement; ``errpreset=conservative`` keeps the harmonic
    content clean (a loose tolerance manufactures numerical distortion).

    Numeric stop/step/start only — SPICE eng-suffix case is a Spectre landmine (matching
    :func:`ac_analysis`).
    """
    parts = ["tran", "tran", f"stop={_fmt(float(stop))}"]
    if step is not None:
        parts.append(f"step={_fmt(float(step))}")
    if start:
        parts.append(f"start={_fmt(float(start))}")
    if errpreset:
        parts.append(f"errpreset={errpreset}")
    return " ".join(parts)


def pss_analysis(
    fund: float,
    *,
    harms: int = 7,
    tstab: float | None = None,
    errpreset: str | None = "conservative",
) -> str:
    """A Spectre periodic-steady-state analysis named ``pss`` (→ a ``pss.fd.pss`` fd-PSF).

    Emits ``pss pss fund=… harms=… [tstab=…] [errpreset=…]``. Drive the DUT with a periodic
    large-signal :func:`sine_source` at ``fund``; PSS solves the steady state and lands the
    per-harmonic COMPLEX phasors in the frequency-domain PSF ``pss.fd.pss`` (sweep ``freq`` =
    [0, fund, 2·fund, …]), read by :func:`backends.spectre.read_swept_psf`. The native-harmonic
    distortion recipes (``{meas: thd_pss|hd2|hd3|sfdr}``) then read the output's harmonics
    directly — no resample/window, unlike the transient ``.four``-style ``{meas: thd}``.
    ``harms`` is the number of harmonics past DC to resolve; ``tstab`` is the pre-PSS
    stabilisation interval (default: the solver's own). Numeric only (eng-suffix-case landmine).
    """
    parts = ["pss", "pss", f"fund={_fmt(float(fund))}", f"harms={int(harms)}"]
    if tstab is not None:
        parts.append(f"tstab={_fmt(float(tstab))}")
    if errpreset:
        parts.append(f"errpreset={errpreset}")
    return " ".join(parts)


def pnoise_analysis(
    output: str,
    ref: str = "0",
    *,
    iprobe: str | None = None,
    refsideband: int = 0,
    maxsideband: int = 7,
    start: float = 1e3,
    stop: float = 1e8,
    dec: int = 20,
) -> str:
    """A Spectre periodic noise analysis named ``pnoise`` (→ a ``pnoise.pnoise`` PSF).

    Emits ``pnoise ( <output> <ref> ) pnoise start=… stop=… dec=… maxsideband=…
    [iprobe=… refsideband=…]`` — the cyclostationary companion of :func:`noise_analysis`:
    it rides a **preceding** :func:`pss_analysis` steady state (compose both, pss first)
    and sums noise folded in from ``maxsideband`` sidebands of the periodic operating
    point, so it captures what a small-signal ``noise`` cannot (noise modulated by the
    large-signal drive; mixers/switched circuits). ``iprobe`` names the input source
    *instance* to refer noise to; Spectre then **requires** ``refsideband`` — which
    conversion gain refers input to output — and ``0`` (input and output in the same
    band, no frequency translation) is the driven-amplifier case, so it is the default
    here whenever ``iprobe`` is set.

    Like ``noise``/``pss``, the result is a plain swept PSF in the run's ``-raw`` dir
    (``pnoise.pnoise``: sweep ``freq``, top-level ``out``/``in`` V/√Hz densities +
    ``gain``, per-device ``INST:src`` V²/Hz contributions — discovered live on TSMC-65,
    2026-07-11) read by :func:`backends.spectre.read_swept_psf`, so the registry recipes
    ``{meas: onoise_pnoise_total | inoise_pnoise_total | pnoise_spot | phase_noise_dbc}``
    pull the densities exactly as the small-signal noise ones do. Spectre may clip the
    top of the requested band (observed live: ``stop=1e8`` swept to ≈44.7 MHz); the
    trapezoid integral simply covers the band actually swept. Numeric start/stop only
    (the eng-suffix-case landmine, matching :func:`ac_analysis`).
    """
    parts = [
        "pnoise",
        f"( {output} {ref} )",
        "pnoise",
        f"start={_fmt(float(start))}",
        f"stop={_fmt(float(stop))}",
        f"dec={int(dec)}",
        f"maxsideband={int(maxsideband)}",
    ]
    if iprobe:
        parts.append(f"iprobe={iprobe}")
        parts.append(f"refsideband={int(refsideband)}")
    return " ".join(parts)


def pac_analysis(
    *,
    start: float = 1.0,
    stop: float = 1e5,
    dec: int = 20,
    maxsideband: int = 7,
) -> str:
    """A Spectre periodic AC analysis named ``pac`` (→ a ``pac.pac`` PSF).

    The cyclostationary companion of :func:`ac_analysis`: it rides a **preceding**
    :func:`pss_analysis` steady state (compose both, pss first) and computes the
    periodic small-signal transfer, folding in the sidebands of the periodic operating
    point. Drive the small signal by setting ``pacmag=1`` on the input source (the
    periodic analogue of ``ac``'s ``mag=1`` — on a current source it makes the analysis
    read out an impedance); the node responses land in the swept ``pac.pac`` PSF (sweep
    ``freq``, per-node complex voltages at each output sideband), read by
    :func:`backends.spectre.read_swept_psf`.

    This is the CORRECT gain/impedance analysis for CHOPPER / switched-cap circuits,
    where a static ``ac`` on the frozen network is meaningless: the operating point is
    periodic (the chop clock), not DC, and the signal-band response is what survives the
    modulate→amplify→demodulate round-trip. ``maxsideband`` is how many sidebands of the
    periodic OP fold into the response (the driven baseband is sideband 0). Numeric
    start/stop only (the eng-suffix-case landmine, matching :func:`ac_analysis`).

    ngspice has no PSS/PAC; the analog-db ``ia`` chopper benches
    (``tran_chopper_ripple`` gain, ``tran_zin_chopped``) are the transient-domain
    open-PDK approximation of this — the golden PSS+PAC form runs on the Spectre lane
    (virtuoso-bridge-lite) against a 65 nm binding.
    """
    return " ".join(
        [
            "pac",
            "pac",
            f"start={_fmt(float(start))}",
            f"stop={_fmt(float(stop))}",
            f"dec={int(dec)}",
            f"maxsideband={int(maxsideband)}",
        ]
    )


def stb_analysis(probe: str, start: float = 1e3, stop: float = 1e9, dec: int = 101) -> str:
    """A Spectre stability (loop-gain) analysis named ``stb`` (→ an ``stb.stb`` PSF).

    Emits ``stb stb probe=… start=… stop=… dec=…``. ``probe`` names an ``iprobe``
    *instance* inside the feedback loop — the analog-db class templates mark it with a
    0 V source named ``VIPRB*`` that the Spectre emitter translates to an iprobe. The
    result's ``loopGain`` wave (complex vs freq) is the one OCEAN's ``phaseMargin`` is
    actually defined for (it refuses a closed-loop AC wave) and feeds the registry's
    ``{meas: pm_loop|gain_margin_db|loopgain_db}`` recipes via ``read_swept_psf``.
    Numeric start/stop only (the eng-suffix-case landmine, matching :func:`ac_analysis`).
    """
    return (
        f"stb stb probe={probe} "
        f"start={_fmt(float(start))} stop={_fmt(float(stop))} dec={int(dec)}"
    )


def sine_source(
    name: str,
    node_p: str,
    node_n: str = "0",
    *,
    dc: float = 0.0,
    ampl: float,
    freq: float,
) -> str:
    """A large-signal sinusoidal ``vsource`` (Spectre): ``<name> ( p n ) vsource type=sine …``.

    The stimulus for a transient THD measurement — ``ampl`` (amplitude, V) and ``freq`` (Hz)
    set the fundamental that the FFT-based ``{meas: thd, f0: …}`` recipe analyses. ``dc``
    biases the source (e.g. an input common-mode). Numeric only, matching the analyses'
    eng-suffix-case landmine.
    """
    return (
        f"{name} ( {node_p} {node_n} ) vsource type=sine "
        f"dc={_fmt(float(dc))} ampl={_fmt(float(ampl))} freq={_fmt(float(freq))}"
    )


def _fmt(value: Any) -> str:
    if isinstance(value, float):
        return f"{value:.10g}"
    return str(value)


def _check_analysis_contract(line: str) -> None:
    tokens = line.split()
    if len(tokens) < 2:
        return
    name, kind = tokens[0], tokens[1]
    expected = _CONTRACT_NAMES.get(kind)
    if expected and name not in expected:
        logger.warning(
            "analysis %r: a %s analysis must be NAMED %s for its PSF result keys to "
            "carry the %s_ prefix the adapter looks up (P0 contract; keys are keyed "
            "by PSF file names)",
            line,
            kind,
            " or ".join(expected),
            kind if kind != "dc" else "dc",
        )


def _check_pss_riders(analyses: Sequence[str]) -> None:
    """``pac``/``pnoise`` ride a periodic steady state: a ``pss`` (or ``hb``) analysis
    must be composed BEFORE them in the deck. Composing a rider without its base is a
    composition bug — fail it here with an actionable message rather than letting
    Spectre die cryptically at run time."""
    seen_base = False
    for line in analyses:
        tokens = line.split()
        if not tokens:
            continue
        name = tokens[0].lower()  # P0 contract: the analysis NAME equals its kind
        if name in ("pss", "hb"):
            seen_base = True
        elif name in ("pac", "pnoise") and not seen_base:
            raise ValueError(
                f"analysis {name!r} rides a periodic steady state: compose "
                f"pss_analysis(...) BEFORE {name}_analysis(...) in `analyses` "
                f"(got {list(analyses)!r})."
            )


_SECTION_INCLUDE_RE = re.compile(r'^\s*(?:include|ahdl_include)\s+"[^"]+"\s+section\s*=', re.IGNORECASE)
_PARAMS_RE = re.compile(r"^\s*parameters\b(.*)$", re.IGNORECASE)


def _logical_lines(text: str) -> list[str]:
    """Split into logical lines, joining Spectre `\\`-continuations."""
    out: list[str] = []
    buf = ""
    for raw in text.splitlines():
        if raw.rstrip().endswith("\\"):
            buf += raw.rstrip()[:-1] + " "
            continue
        out.append(buf + raw)
        buf = ""
    if buf:
        out.append(buf)
    return out


def _parse_param_tokens(body: str) -> "dict[str, str]":
    """Parse `k=v` pairs from the body of a `parameters` statement (order-preserving).

    Whitespace-separated `name=value`; a token with no `=` is treated as a continuation
    of the previous value (a spaced expression like `p = a + b`)."""
    params: dict[str, str] = {}
    last: str | None = None
    for tok in body.split():
        if "=" in tok:
            key, _, val = tok.partition("=")
            key = key.strip()
            params[key] = val.strip()
            last = key
        elif last is not None:
            params[last] = (params[last] + " " + tok).strip()
    return params


def render_native_scs(
    text: str,
    *,
    parameters: Mapping[str, Any] | None = None,
    corner_includes: Sequence[str] | None = None,
    temp: float | None = None,
) -> str:
    """Inject per-candidate overrides into a **native** Spectre `.scs` deck, in place.

    The native-first counterpart to composing a deck from parts: the caller's hand-written
    `.scs` (the testbench `netlist:`, exactly like an ngspice `.spice`) runs almost
    verbatim — only the two things the optimizer/PVT must control are rewritten, so the
    engineer keeps full native control of stimulus, analyses and saves:

    * ``parameters`` — the deck's ``parameters`` statement(s) have `parameters` (design
      vars, lowercased — SPICE folds case, Spectre doesn't) merged over their defaults;
      an injected key the deck doesn't declare is appended (inert if unused). This is how
      design variables are swept: the bridge runs a fixed file per run, and in local mode
      ignores its ``params`` arg, so injection must happen here.
    * ``corner_includes`` — when given (a PVT corner), model ``include "…" section=…``
      lines are replaced wholesale (mirroring ngspice ``apply_corner`` strip+inject); a
      DUT ``include "dut.scs"`` (no ``section=``) is left untouched.
    * ``temp`` — appends a ``tempOptions options temp=…`` statement.

    If the deck declares no ``parameters`` statement, one is inserted after the
    ``global 0`` / header when there is something to inject.
    """
    inject = {str(k).lower(): v for k, v in (parameters or {}).items()}
    includes = list(corner_includes) if corner_includes is not None else None

    out: list[str] = []
    params_written = False
    includes_written = includes is None  # only touch includes when a corner is given
    header_idx = -1  # last index of a `simulator lang`/`global` header line, for insertion

    for line in _logical_lines(text):
        m = _PARAMS_RE.match(line)
        if m is not None:
            merged = _parse_param_tokens(m.group(1))
            merged.update({k: _fmt(v) for k, v in inject.items()})
            out.append("parameters " + " ".join(f"{k}={v}" for k, v in merged.items()))
            params_written = True
            continue
        if includes is not None and _SECTION_INCLUDE_RE.match(line):
            if not includes_written:
                out.extend(includes)
                includes_written = True
            continue  # drop the deck's own corner include(s)
        low = line.strip().lower()
        if low.startswith("global") or low.startswith("simulator lang"):
            header_idx = len(out)
        out.append(line)

    insert_at = header_idx + 1 if header_idx >= 0 else 0
    if inject and not params_written:
        out.insert(insert_at, "parameters " + " ".join(f"{k}={_fmt(v)}" for k, v in inject.items()))
        insert_at += 1
    if includes is not None and not includes_written:
        for inc in reversed(includes):
            out.insert(insert_at, inc)
    if temp is not None:
        out.append(f"tempOptions options temp={_fmt(float(temp))}")
    return "\n".join(out) + "\n"


@dataclass(frozen=True)
class SpectreDeckSpec:
    """One composable Spectre deck: structural blocks + defaults, analyses, options.

    ``subckt_blocks``/``stimulus`` are plain Spectre text (e.g. from
    ``spicexplorer_circuitgraph.translate_ngspice_to_spectre``, or hand-written).
    ``includes`` are the deck's *default* model includes — replaced wholesale by a
    corner's includes at render time (mirroring the ngspice ``apply_corner`` strip +
    inject semantics).
    """

    title: str
    stimulus: str
    subckt_blocks: tuple[str, ...] = ()
    analyses: tuple[str, ...] = (("dcOp dc"),)
    parameters: Mapping[str, Any] = field(default_factory=dict)
    includes: tuple[str, ...] = ()
    simulator_options: str | None = DEFAULT_SIMULATOR_OPTIONS
    include_oppoint_info: bool = True
    extra_lines: tuple[str, ...] = ()


def render_spectre_deck(
    spec: SpectreDeckSpec,
    *,
    parameters: Mapping[str, Any] | None = None,
    corner_includes: Sequence[str] | None = None,
    temp: float | None = None,
) -> str:
    """Render the spec to `.scs` text; per-run injection wins over spec defaults.

    ``parameters`` overrides the spec's defaults (keys folded to lowercase — the deck's
    parameter namespace is lowercase). ``corner_includes`` *replaces* the spec's default
    includes when given (corner selection). ``temp`` emits a dedicated options statement.
    """
    merged: dict[str, Any] = {str(k).lower(): v for k, v in spec.parameters.items()}
    for key, value in (parameters or {}).items():
        merged[str(key).lower()] = value

    includes = tuple(corner_includes) if corner_includes else spec.includes
    for line in spec.analyses:
        _check_analysis_contract(line)
    _check_pss_riders(spec.analyses)

    lines: list[str] = [
        f"// {spec.title}",
        "simulator lang=spectre",
        "global 0",
        *includes,
    ]
    if merged:
        lines.append("parameters " + " ".join(f"{k}={_fmt(v)}" for k, v in sorted(merged.items())))
    for block in spec.subckt_blocks:
        lines += ["", block.rstrip()]
    if spec.stimulus:
        lines += ["", spec.stimulus.rstrip()]
    lines.append("")
    if spec.simulator_options:
        lines.append(spec.simulator_options)
    if temp is not None:
        lines.append(f"tempOptions options temp={_fmt(float(temp))}")
    lines.extend(spec.analyses)
    if spec.include_oppoint_info:
        lines.append(OPPOINT_INFO_LINE)
    lines.append(SAVE_OPTIONS_LINE)
    lines.extend(spec.extra_lines)
    return "\n".join(lines) + "\n"


def deck_spec_from_native(
    title: str,
    stimulus: str,
    *,
    subckt_blocks: Sequence[str] = (),
    parameters: Mapping[str, Any] | None = None,
    analyses: Sequence[str] | None = None,
    includes: Sequence[str] = (),
    simulator_options: str | None = DEFAULT_SIMULATOR_OPTIONS,
    extra_lines: Sequence[str] = (),
) -> SpectreDeckSpec:
    """Assemble a :class:`SpectreDeckSpec` from **native Spectre** deck parts.

    The native-first counterpart of :func:`deck_spec_from_ngspice`: no translation, no
    circuitgraph import — the caller supplies verbatim Spectre text (the
    ``SpectreTestbench`` YAML block maps straight onto these arguments). Design params
    still inject per candidate via composed-deck mode (``render_spectre_deck``'s
    ``parameters`` merge), which is what makes an *optimization loop* possible on a
    native Spectre bench — the bridge itself runs a fixed file per run (and in local
    mode ignores its ``params`` argument entirely), so param injection must happen here,
    on our side of the seam. An empty ``analyses`` defaults to a DC op-point.
    """
    return SpectreDeckSpec(
        title=title,
        stimulus=stimulus,
        subckt_blocks=tuple(subckt_blocks),
        analyses=tuple(analyses) if analyses else (dc_oppoint_analysis(),),
        parameters=dict(parameters or {}),
        includes=tuple(includes),
        simulator_options=simulator_options,
        extra_lines=tuple(extra_lines),
    )


def deck_spec_from_ngspice(
    netlist: Path | str,
    *,
    pdk: str | Any = "tsmc-n65",
    source_pdk: str | Any | None = None,
    analyses: Sequence[str] | None = None,
    parameters: Mapping[str, Any] | None = None,
    title: str | None = None,
    ground_nets: Sequence[str] = ("GND",),
) -> SpectreDeckSpec:
    """Translate an ngspice deck into a composable :class:`SpectreDeckSpec`.

    The syntax half runs in ``spicexplorer-circuitgraph`` (dialect emitters); imported
    lazily so this module stays importable without it. ``pdk`` names the target device
    table (device-model mapping, e.g. ``"tsmc-n65"``); ``source_pdk`` aids device
    classification of the source deck (e.g. ``"ihp-sg13g2"`` for X-prefixed MOS).
    """
    try:
        from spicexplorer_circuitgraph import translate_ngspice_to_spectre
    except ImportError as exc:  # pragma: no cover - all workspace syncs install it
        raise ImportError(
            "Translating an ngspice deck for the Spectre backend requires "
            "'spicexplorer-circuitgraph' (a workspace member; `uv sync` installs it). "
            "Alternatively pass a hand-written .scs to create_spectre_simulator."
        ) from exc

    design = translate_ngspice_to_spectre(
        netlist, pdk=pdk, source_pdk=source_pdk, ground_nets=ground_nets
    )
    merged: dict[str, Any] = dict(design.parameters)
    for key, value in (parameters or {}).items():
        merged[str(key).lower()] = value
    stimulus = "\n".join(s for s in (design.stimulus, *design.ground_ties) if s)
    return SpectreDeckSpec(
        title=title or f"{Path(netlist).stem} (translated ngspice -> spectre)",
        stimulus=stimulus,
        subckt_blocks=design.subckt_blocks,
        analyses=tuple(analyses) if analyses is not None else (dc_oppoint_analysis(),),
        parameters=merged,
    )
