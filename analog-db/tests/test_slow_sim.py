"""The ``slow`` SIMULATION test pyramid (plan §6 T3/T4 + integration), bottom-to-top.

Each level gates the next; the bottom is the most critical:
  L0  syntax     — the assembled ngspice netlist PARSES, no syntax/library error (no sim).
  L1  feature    — each enabled analysis SIMULATES (ngspice + the real PDK), finite numbers.
  L1b PDK-swap   — one abstract topology simulates on BOTH PDKs (ihp-sg13g2 AND sky130).
  L1c crosscheck — netlist2tf symbolic DC gain agrees with the sim (the in-repo OTAs; plan D-5).
  L2  wrapper    — the platform spicelib NGSpice_Wrapper imports + drives a netlist (integration).
  L3  project    — a project_setup.yaml runs one real optimizer step (full integration).

Docker/PDK-gated. L0/L1/L1b/L1c drive ngspice via the EDA base image (`docker run`), so they run
from the host with no api container. L2/L3 need ngspice + PDK + the platform packages together →
the api container; they skip cleanly when it is absent.
"""

from __future__ import annotations

import math
import re
import shutil
import subprocess

import pytest
import yaml

from spicexplorer_analog_db import export, model, paths
from spicexplorer_analog_db import runner as runmod

pytestmark = pytest.mark.slow

_BASE_IMAGE = "spicexplorer-spice-base:local"

# A deck that trips one of these did NOT run — it's structurally broken or its PDK *library* doesn't
# resolve (a real artifact failure → hard fail). DELIBERATELY narrow to UNAMBIGUOUS structural signals.
# A degenerate *baseline sizing* (the IHP-tuned cascodes on sky130/gf180; the `incomplete` tan_clia)
# trips "could not find a valid modelname" (W out of the model bin) → "Error on line N" → "incomplete
# or empty netlist" — that means the device fell out of its bin, NOT that the deck is malformed, so it
# is a recorded-floor SKIP (ngspice still loaded + ran the deck). Likewise singular-matrix / no-
# convergence / "Dsub<0" / a generic "fatal error" are sizing/bias degeneracies, not load failures.
# (Genuinely malformed decks are already caught upstream: Tier-2 re-parses every assembly, and the
# byte-drift guard pins committed == freshly rendered.)
_LOAD_ERR = re.compile(r"(could not find library|unknown subckt|syntax error)", re.IGNORECASE)


def _have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def _base_image_available() -> bool:
    if not _have("docker"):
        return False
    # probe with a real `docker run` — `docker image inspect <tag>` can false-negative under
    # the containerd image store even when the image runs fine
    return subprocess.run(["docker", "run", "--rm", _BASE_IMAGE, "true"],
                          capture_output=True, text=True, timeout=120).returncode == 0


def _api_container_runs() -> bool:
    if not _have("docker"):
        return False
    return bool(subprocess.run(["docker", "compose", "ps", "-q", "api"],
                               capture_output=True, text=True).stdout.strip())


def _base_image_has_gf180() -> bool:
    """The base image carries the gf180mcu PDK (it is vendored + on the sourcepath after the
    gf180 rebuild). Lets the gf180 sim tier skip cleanly on an older image without it."""
    if not _base_image_available():
        return False
    return subprocess.run(
        ["docker", "run", "--rm", _BASE_IMAGE, "bash", "-lc",
         "test -f /opt/pdk/gf180mcu/libs.tech/ngspice/sm141064.ngspice"],
        capture_output=True, text=True).returncode == 0


needs_base = pytest.mark.skipif(
    not _base_image_available(),
    reason=f"{_BASE_IMAGE} not built (docker compose --profile base build spice-base)",
)
needs_api = pytest.mark.skipif(
    not _api_container_runs(),
    reason="api container not running (docker compose up -d api) — needs ngspice+PDK+packages",
)
needs_gf180 = pytest.mark.skipif(
    not _base_image_has_gf180(),
    reason="base image lacks the gf180mcu PDK (rebuild spice-base after the gf180 vendoring)",
)


_shared_container: str | None = None


def _ensure_shared_container() -> str | None:
    """Lazily start ONE long-lived base-image container for the whole test session, reused by
    every `_runner()` call via `docker exec` (cheap) instead of a fresh `docker run --rm` per
    call (expensive — container create/teardown dominates the T3 sweep's ~200+ decks). Falls
    back to per-call `docker run` (returns None here) if the container can't be started."""
    global _shared_container
    if _shared_container is None and _base_image_available():
        _shared_container = runmod.start_detached_base_image(_BASE_IMAGE) or ""
    return _shared_container or None


@pytest.fixture(scope="session", autouse=True)
def _stop_shared_container():
    yield
    if _shared_container:
        runmod.stop_container(_shared_container)


def _runner():
    container = _ensure_shared_container()
    if container:
        return runmod.docker_exec_runner(container)
    return runmod.base_image_runner(_BASE_IMAGE)


def _analoggym_ids() -> list[str]:
    """AnalogGym circuits that are sim-able (status != incomplete)."""
    out = []
    for c in model.list_circuit_ids():
        m = model.load_circuit(c).manifest
        if m.get("provenance", {}).get("source") == "AnalogGym" and m.get("status") != "incomplete":
            out.append(c)
    return out


# ───────────────────── L0: syntax (the critical first gate) ─────────────────────

@needs_base
@pytest.mark.parametrize("cid", _analoggym_ids() or ["amp_003_fan_smc"])
def test_L0_analoggym_netlist_parses(cid):
    c = model.load_circuit(cid)
    errs = runmod.parse_errors(c, "ac_open_loop", "sky130", "tt", _runner())
    assert not errs, f"{cid} sky130 parse errors:\n" + "\n".join(errs[:8])


@needs_base
@pytest.mark.parametrize("cid,pdk", [("amp_001_5t", "ihp-sg13g2"), ("amp_001_5t", "sky130"),
                                     ("amp_018_telescopic_cascode", "ihp-sg13g2")])
def test_L0_in_repo_ota_parses(cid, pdk):
    c = model.load_circuit(cid)
    errs = runmod.parse_errors(c, "ac_open_loop", pdk, "tt", _runner())
    assert not errs, f"{cid}@{pdk} parse errors:\n" + "\n".join(errs[:8])


# ───────────────────── L1: feature sim ─────────────────────

@needs_base
def test_L1_analoggym_simulates_on_sky130():
    c = model.load_circuit("amp_003_fan_smc")
    ac = runmod.run_circuit(c, "sky130", "tt", _runner())["analyses"]["ac_open_loop"]
    assert ac["status"] == "ok", ac.get("error", "")
    m = ac["measures"]
    assert 0 < m["dcgain"] < 200 and m["ugf"] > 0 and 0 <= m["pm"] <= 180


# ───────────────────── L1b: PDK swap (the full cross-PDK transfer matrix) ─────────────────────


def _pdk_transfer_pairs() -> list[tuple[str, str]]:
    """(circuit, pdk) cells the cross-PDK transfer must SIMULATE: every AnalogGym amp on BOTH PDKs
    (sky130 ← native, ihp-sg13g2 ← transferred) + amp_001_5t on both.

    The in-repo cascodes (folded/telescopic) sim on ihp only: their sky130 lowering is now
    finger-correct (ng→nf, per-finger width), but the IHP-tuned device geometries fall outside
    sky130's reliable binned-model envelope (single-finger caps at ~100µm; nf>1 needs per-finger
    W ≲ 5µm) — meaningful sky130 baselines need device re-sizing (Phase 6 / gm-ID). See
    `_shared/PDK_SIM.md`."""
    pairs = [("amp_001_5t", "ihp-sg13g2"), ("amp_001_5t", "sky130")]
    for cid in _analoggym_ids():
        pairs += [(cid, "sky130"), (cid, "ihp-sg13g2")]
    return pairs


@needs_base
@pytest.mark.parametrize("cid,pdk", _pdk_transfer_pairs() or [("amp_001_5t", "sky130")])
def test_L1b_pdk_transfer_simulates(cid, pdk):
    """One abstract topology, two PDKs: the open-loop AC simulates with a finite, positive gain on
    each. (PM is not asserted — an unoptimized cross-PDK transfer is a recorded floor, not a
    spec-passing design, so a low/negative PM at default sizing is a valid baseline.)"""
    ac = runmod.run_circuit(model.load_circuit(cid), pdk, "tt", _runner())["analyses"]["ac_open_loop"]
    assert ac["status"] == "ok", f"{cid}@{pdk}: {ac.get('error', '')[:300]}"
    m = ac["measures"]
    assert 0 < m["dcgain"] < 200 and m["ugf"] > 0, (cid, pdk, m)


# ───────────────────── L1b-gf180: the third PDK (cross-PDK benchmarking) ─────────────────────


@needs_base
@needs_gf180
@pytest.mark.parametrize("cid", [*( _analoggym_ids() or ["amp_003_fan_smc"]), "amp_001_5t"])
def test_L0_gf180_netlist_parses(cid):
    """Every (sim-able) circuit's gf180 deck PARSES + resolves the gf180 libs (no model/lib error)."""
    errs = runmod.parse_errors(model.load_circuit(cid), "ac_open_loop", "gf180mcu", "tt", _runner())
    assert not errs, f"{cid} gf180 parse errors:\n" + "\n".join(errs[:8])


@needs_base
@needs_gf180
@pytest.mark.parametrize("cid", ["amp_001_5t", "amp_009_leung_nmcnr", "amp_014_ramos_pfc"])
def test_L1_gf180_simulates(cid):
    """Representative circuits simulate on gf180mcu with a finite, positive open-loop gain. (Not all
    transfers bias at default sizing on the 3.3V rail — degenerates are recorded floors, not tested;
    folded/telescopic need re-sizing as on sky130. See `_shared/PDK_SIM.md`.)"""
    ac = runmod.run_circuit(model.load_circuit(cid), "gf180mcu", "tt", _runner())["analyses"]["ac_open_loop"]
    assert ac["status"] == "ok", f"{cid}@gf180mcu: {ac.get('error', '')[:300]}"
    m = ac["measures"]
    assert 0 < m["dcgain"] < 200 and m["ugf"] > 0, (cid, m)


# ───────────────────── L1c: symbolic cross-check (the in-repo OTAs; D-5) ─────────────────────

@needs_base
@pytest.mark.parametrize("cid", ["amp_001_5t", "amp_018_telescopic_cascode", "amp_004_folded_cascode"])
def test_L1c_symbolic_crosscheck_agrees(cid):
    from spicexplorer_analog_db.symbolic import crosscheck

    c = model.load_circuit(cid)
    r = _runner()
    res = runmod.run_circuit(c, "ihp-sg13g2", "tt", r)
    bad = {a: r2 for a, r2 in res["analyses"].items() if r2["status"] not in ("ok", "disabled")}
    assert not bad, f"{cid} sim errors: { {a: r2.get('error','')[:160] for a, r2 in bad.items()} }"
    # rel_tol=10%: this is a STRUCTURAL check (does the symbolic TF match the topology + measured
    # bias?), not a precision gate. The IHP PSP OSDI is numerically build-dependent (compiled-for-arch
    # vs the vendored x86-64 prebuilt), which shifts gm/gds a few % — most on the sensitive cascode.
    # 10% still catches gross structural errors (e.g. a d/s swap → 50%+ off) while surviving that.
    report = crosscheck(c, "ihp-sg13g2", "tt", res["analyses"], r, rel_tol=0.10)
    checked = {m: e for m, e in report["metrics"].items() if "agrees" in e}
    assert checked and all(e["agrees"] for e in checked.values()), report["metrics"]


# ───────── raw/ committed decks: the ON-DISK artifact loads + simulates (plan_raw_export §5) ─────────
#
# T3 sim-smoke realized over the materialized tree (todo_examples_db Phase 7): EVERY committed deck is
# run through ngspice. The contract has two levels —
#   HARD (fail): the deck RUNS — ngspice loads it and the PDK libs/models/subckts resolve (`_LOAD_ERR`).
#   SOFT (skip): the metrics of interest EXTRACT (finite measures). A baseline whose default sizing
#                doesn't bias into a working circuit (no convergence / W out of bin / no finite measure)
#                is a *recorded floor* → skipped, but the SPICE run was still exercised.


def _load_ci_skip() -> list[dict]:
    """Load static T3 exclusion rules from ``_shared/ci_skip.yaml``.

    Each rule is a dict with optional keys ``pdk``, ``circuit``, ``testbench``
    (omitted = wildcard) and a required ``reason`` string.  A deck matches a
    rule when every key present in the rule equals the corresponding component
    of the deck's path.  Consumed by :func:`_deck_is_skipped`.
    """
    p = paths.shared_root() / "ci_skip.yaml"
    if not p.is_file():
        return []
    with p.open() as fh:
        data = yaml.safe_load(fh)
    return data.get("exclude", []) if data else []


def _deck_is_skipped(deck, rules: list[dict]) -> bool:
    """Return True if *deck* matches any rule in *rules* from ``ci_skip.yaml``."""
    circuit, pdk, stem = deck.parts[-3], deck.parts[-2], deck.stem
    for rule in rules:
        if "pdk" in rule and rule["pdk"] != pdk:
            continue
        if "circuit" in rule and rule["circuit"] != circuit:
            continue
        if "testbench" in rule and rule["testbench"] != stem:
            continue
        return True
    return False


def _all_committed_decks() -> list:
    """Every committed runnable deck (`raw/**/*.spice` minus the standalone `_dut.spice`).

    gf180mcu decks drop out when the base image lacks that PDK (a runtime probe —
    the PDK *can* be present, just not always built in).  All other static exclusions
    are driven by ``_shared/ci_skip.yaml`` so new NDA-protected PDKs, broken circuits,
    or flaky testbenches can be excluded without touching this code.
    """
    rd = export.raw_root()
    if not rd.is_dir():
        return [export.deck_path(model.load_circuit("amp_001_5t"), "ac_open_loop", "sky130")]
    decks = sorted(p for p in rd.rglob("*.spice") if p.name != "_dut.spice")
    if not _base_image_has_gf180():
        decks = [p for p in decks if "gf180mcu" not in p.parts]
    rules = _load_ci_skip()
    if rules:
        skipped = {str(p) for p in decks if _deck_is_skipped(p, rules)}
        if skipped:
            reasons = {
                r["reason"] for r in rules
                if any(_deck_is_skipped(p, [r]) for p in decks if str(p) in skipped)
            }
            print(f"\n[ci_skip] excluding {len(skipped)} deck(s): {'; '.join(sorted(reasons))}")
        decks = [p for p in decks if str(p) not in skipped]
    return decks


@needs_base
@pytest.mark.parametrize(
    "deck", _all_committed_decks(),
    ids=lambda p: "/".join(p.parts[-3:])[:-6],   # <circuit>/<pdk>/<testbench>
)
def test_T3_every_raw_deck_runs_and_extracts_or_floors(deck):
    """Tier 3 over the WHOLE raw/ tree: ngspice must RUN every committed deck (hard), and the
    testbench metrics must extract (soft → skip as a recorded floor if the baseline sizing doesn't
    bias into a working circuit). Runs the on-disk bytes, not a fresh assemble()."""
    output = _runner()(deck.read_text())
    load_errs = [ln.strip() for ln in output.splitlines() if _LOAD_ERR.search(ln)]
    rel = "/".join(deck.parts[-4:])
    assert not load_errs, f"{rel}: deck did not run (load/lib/model error):\n" + "\n".join(load_errs[:8])
    measures, failed = runmod.parse_measures(output)
    finite = {k: v for k, v in measures.items() if math.isfinite(v)}
    if not finite:
        pytest.skip(f"{rel}: ran but baseline sizing extracts no finite metrics "
                    f"(recorded floor; failed meas={failed or 'none'})")


def _committed_raw_sim_cells() -> list[tuple[str, str, str]]:
    """(circuit, pdk, testbench) cells whose COMMITTED ``raw/`` deck must SIMULATE on the base image:
    every amp_001_5t testbench on each available PDK (all its analyses sim — L1c already drives them) +
    one AnalogGym amp's open-loop on sky130. These run the bytes on disk, not a fresh assemble() —
    proving the persisted, designer-pullable artifact is genuinely ready-to-run."""
    cells: list[tuple[str, str, str]] = []
    ota = model.load_circuit("amp_001_5t")
    pdks = ["ihp-sg13g2", "sky130"] + (["gf180mcu"] if _base_image_has_gf180() else [])
    for pdk in pdks:
        for tb in ota.analyses:
            cells.append(("amp_001_5t", pdk, tb))
    cells.append(("amp_003_fan_smc", "sky130", "ac_open_loop"))
    return cells


@needs_base
@pytest.mark.parametrize("cid,pdk,tb", _committed_raw_sim_cells(),
                         ids=lambda t: f"{t[0]}@{t[1]}/{t[2]}" if isinstance(t, tuple) else str(t))
def test_L1_committed_raw_deck_simulates(cid, pdk, tb):
    """The COMMITTED ``raw/<circuit>/<pdk>/<tb>.spice`` (the on-disk artifact, NOT a fresh
    assemble) runs through ngspice on the base image and yields finite measures. ``run_text`` raises
    on a fatal error / no parseable measures / NaN, so a non-empty return == the deck ran clean."""
    deck = export.deck_path(model.load_circuit(cid), tb, pdk, "tt")
    assert deck.is_file(), f"missing committed deck {deck} — run `analog-db export-raw`"
    measures = runmod.run_text(deck.read_text(), f"raw:{cid}@{pdk}/{tb}", _runner())
    assert measures, (cid, pdk, tb)


@needs_base
def test_committed_raw_deck_byte_identical_to_render():
    """The on-disk deck is byte-for-byte what the generator produces (the Tier-1 drift guard's
    invariant, re-asserted here so the slow tier runs the SAME bytes the fast suite guards)."""
    c = model.load_circuit("amp_001_5t")
    deck = export.deck_path(c, "ac_open_loop", "sky130", "tt")
    assert deck.read_text() == export.render_deck(c, "ac_open_loop", "sky130", "tt")


# ───────────────────── gm/ID LUT extraction (Phase 6) ─────────────────────


@needs_base
def test_L1_gmid_extract_is_physical_and_pygmid_loads():
    """A small gm/ID LUT extracts on the base image, is physically sane, and loads in pygmid."""
    import os
    import pickle
    import tempfile

    import numpy as np

    pytest.importorskip("pygmid")
    from pygmid import Lookup

    from spicexplorer_analog_db import gmid

    cfg = gmid.GmidConfig.from_registry(
        "sky130", vgs=(0, 0.2, 1.8), vds=(0, 0.4, 1.8), vsb=(0, -0.4, -0.4), length_um=[0.15, 0.5]
    )
    lut = gmid.extract(cfg, gmid.base_image_deck_runner(_BASE_IMAGE))
    assert {"GM", "ID", "CGG", "VGS", "VDS", "VSB", "L"} <= set(lut)
    assert lut["GM"].shape == (2, len(lut["VGS"]), len(lut["VDS"]), len(lut["VSB"]))
    # the L sweep must actually take effect — distinct slices with less current at longer L
    assert not np.allclose(lut["ID"][0], lut["ID"][1]), "L slices identical — alterparam not applied"
    mid = lut["GM"].shape[1] // 2
    assert lut["ID"][1, mid, 2, 0] < lut["ID"][0, mid, 2, 0]

    gm, idd = lut["GM"], lut["ID"]
    mid = gm.shape[2] // 2                                   # a mid-range VDS
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(idd[0, :, mid, 0] > 0, gm[0, :, mid, 0] / idd[0, :, mid, 0], np.nan)
    assert 15 < np.nanmax(ratio) < 45, ratio                 # physical weak-inversion gm/ID peak

    d = tempfile.mkdtemp()
    p = os.path.join(d, "nch.pkl")
    with open(p, "wb") as fh:
        pickle.dump(lut, fh)
    nch = Lookup(p)                                          # the pygmid contract: loads our .pkl
    vgs = float(nch.look_upVGS(GM_ID=10, VDS=0.9, VSB=0, L=0.15))
    assert 0.4 < vgs < 1.2, vgs                              # gm/ID=10 sits around mid-VGS


@needs_base
def test_L1_gmid_vsb_axis_and_pmos_extract():
    """Theme: validate across the WHOLE grid, not slice 0 (the L-sweep bug's lesson).
    (a) VSB slices must differ — body effect raises VT, so ID at fixed VGS drops with |VSB|.
    (b) pmos extracts end-to-end (mirrored-bias deck) with a physical gm/ID peak — pmos was
    config-tested but never simulated before this."""
    import numpy as np

    from spicexplorer_analog_db import gmid

    run = gmid.base_image_deck_runner(_BASE_IMAGE)
    nch = gmid.extract(gmid.GmidConfig.from_registry(
        "sky130", vgs=(0, 0.3, 1.8), vds=(0, 0.6, 1.8), vsb=(0, -0.6, -0.6), length_um=[0.5]
    ), run)
    assert not np.allclose(nch["ID"][:, :, :, 0], nch["ID"][:, :, :, 1]), "VSB slices identical"
    mid = nch["ID"].shape[1] // 2
    assert nch["ID"][0, mid, 2, 1] < nch["ID"][0, mid, 2, 0]   # body effect: less ID at |VSB|>0

    pch = gmid.extract(gmid.GmidConfig.from_registry(
        "sky130", device="sky130_fd_pr__pfet_01v8",
        vgs=(0, 0.3, 1.8), vds=(0, 0.6, 1.8), vsb=(0, -0.6, -0.6), length_um=[0.5]
    ), run)
    gm, idd = pch["GM"], pch["ID"]
    with np.errstate(divide="ignore", invalid="ignore"):
        eff = np.where(np.abs(idd[0, :, 2, 0]) > 0, np.abs(gm[0, :, 2, 0] / idd[0, :, 2, 0]), np.nan)
    assert 15 < np.nanmax(eff) < 45, "pmos gm/ID peak not physical"


@needs_base
def test_L1_non_tt_corner_simulates():
    """Every sim assertion in CI was tt-only — the composed ss corner bundles were never
    executed. One ss cell per BSIM4 PDK pins that the corner libs actually load + bias."""
    from spicexplorer_analog_db import model
    from spicexplorer_analog_db import runner as runmod

    ckt = model.load_circuit("amp_001_5t")
    r = runmod.base_image_runner(_BASE_IMAGE)
    for pdk in ["sky130"] + (["gf180mcu"] if _base_image_has_gf180() else []):
        measures = runmod.run_cell(ckt, "ac_open_loop", pdk, "ss", r)
        assert measures.get("dcgain", 0) > 10, f"{pdk}@ss: implausible gain {measures}"


@needs_base
def test_L1_gmid_hv_variant_swaps_corner_lib():
    """An HV variant (ihp `sg13_hv_nmos`) extracts via the `variants` corner-lib swap (cornerMOShv.lib)
    — proving HV/LV is configurable, not just the LV core device."""
    import numpy as np

    from spicexplorer_analog_db import gmid

    cfg = gmid.GmidConfig.from_registry(
        "ihp-sg13g2", device="sg13_hv_nmos",
        vgs=(0, 0.5, 3.0), vds=(0, 1.0, 3.0), vsb=(0, -0.4, -0.4), length_um=[0.45, 1.0],
    )
    assert cfg.corner_override == {"lib_file": "cornerMOShv.lib"}     # the variant override took effect
    lut = gmid.extract(cfg, gmid.base_image_deck_runner(_BASE_IMAGE))
    gm, idd = lut["GM"], lut["ID"]
    mid = gm.shape[2] // 2
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(idd[0, :, mid, 0] > 0, gm[0, :, mid, 0] / idd[0, :, mid, 0], np.nan)
    assert 15 < np.nanmax(ratio) < 45, ratio                         # physical HV-device gm/ID peak


# ───────────────────── L2: spicelib wrapper (integration) ─────────────────────

@needs_api
def test_L2_spicelib_wrapper_path_in_container():
    """The platform spicelib engine imports + an assembled netlist runs through ngspice inside the
    api container (ngspice + PDK + spicexplorer_core together)."""
    from spicexplorer_analog_db.assemble import assemble

    netlist = assemble(model.load_circuit("amp_001_5t"), "ac_open_loop", "ihp-sg13g2", "tt")
    driver = (
        "import sys, tempfile, os, subprocess\n"
        "from spicexplorer_core.spice_engine import NGSpice_Wrapper  # import must succeed\n"
        "nl = sys.stdin.read(); d = tempfile.mkdtemp(); p = os.path.join(d, 'cell.spice')\n"
        "open(p, 'w').write(nl)\n"
        "r = subprocess.run(['ngspice','-b','cell.spice'], cwd=d, capture_output=True, text=True)\n"
        "print('OK' if 'dcgain' in (r.stdout + r.stderr).lower() else 'FAIL')\n"
    )
    proc = subprocess.run(
        ["docker", "compose", "exec", "-T", "-w", "/app", "api", "python", "-c", driver],
        input=netlist, capture_output=True, text=True, timeout=300,
    )
    assert "OK" in proc.stdout, f"wrapper path failed:\n{proc.stdout}\n{proc.stderr[-1500:]}"


# ───────────────────── L3: project_setup run (top integration) ─────────────────────

@needs_api
def test_L3_project_setup_runs_one_optimizer_step():
    driver = (
        "from spicexplorer.optimization.orchestrator import "
        "Circuit_Optimizer_Orchestrator_with_SPICE as O, Optimizer_Type_Enum as T\n"
        "o = O(project_setup_path='examples/circuits/amp_018_telescopic_cascode/project_setup.yaml',"
        " optimizer_type=T.NEVERGRAD_SINGLE, auto_load=True)\n"
        "opt = o.get_optimizer(); opt.parameterize(); assert opt._create_optimizer_obj()\n"
        "params, score, meta = opt.optimization_step()\n"
        "print('STEP_OK' if params and score is not None else 'STEP_FAIL')\n"
    )
    proc = subprocess.run(
        ["docker", "compose", "exec", "-T", "-w", "/app", "api", "python", "-c", driver],
        capture_output=True, text=True, timeout=600,
    )
    assert "STEP_OK" in proc.stdout, f"project_setup run failed:\n{proc.stdout[-500:]}\n{proc.stderr[-1500:]}"
