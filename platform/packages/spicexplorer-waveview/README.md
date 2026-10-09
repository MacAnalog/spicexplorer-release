# spicexplorer-waveview

**Universal simulation-result (waveform) viewer — backend.** Load any ngspice `.raw`
file or Cadence Spectre psfascii raw directory into one engine-neutral dataset, run
**every Tier-1 registry measurement** against it, parse/tail the simulator log, and
build interactive Plotly figures — the notebook/API backend the Studio UI's **Analyze**
view sits on.

## Purpose & layering

A **leaf tool**: depends on `spicexplorer-core` only (the `SimResult` protocol, the
measurement registry and the PSF parser), plus `spicelib`/`psf-utils`/`numpy`/`plotly`/
`pydantic` from PyPI. It never imports a peer tool.

The Spectre PSF-dir reading is **not** a duplicated parser. `spectre_loader.py` and the
optimizer's `backends/spectre.py` both import the one reader in
`spicexplorer_core.spice_engine.psfascii`; what differs is only the shaping of the result
into this package's `WaveDataset`. An earlier version of this paragraph called the two
"deliberate siblings" because peer packages cannot import each other — true of the peers,
but the parsing moved into `core` (which both may depend on) and the justification went
stale with it (Codex review, item WV-01). `tests/test_loaders.py::
test_spectre_parity_with_backend_reader` still pins that the two agree, now as a guard on
the shaping rather than on two independent parsers.

The REST adapter (`spicexplorer-api`) mounts this as the `/api/waveview/*` routes.

## Public API

```python
from spicexplorer_waveview import (
    # path → WaveDataset (sniffs ngspice vs spectre)
    load_result,
    # .raw file → WaveDataset (all plots, incl. multi-plot)
    load_ngspice_raw,
    # psfascii -raw dir → WaveDataset (ac/dc/tran/noise/pss/pnoise/pac/stb + op + .info)
    load_spectre_raw_dir,
    # N datasets → ONE (a run's testbenches as one tree; dup analyses suffixed #2…)
    merge_datasets,
    # dataset model + its SimResult-protocol adapter
    WaveDataset,
    DatasetResult,
    # Tier-1 recipes on loaded data
    measure_dataset,
    measure_many,
    measurement_catalog,
    # log viewer backend
    parse_sim_log,
    discover_log,
    classify_line,
    # ngspice scalars / fatal lines (core's sim_log)
    parse_measures,
    fatal_lines,
    # data stimulus (PRBS, NRZ/PAM4, PWL taps)
    Data,
    prbs,
    symbols,
    pwl,
    ideal_waveform,
    # symbol-aware eye behind a BT4 receiver
    eye_metrics,
    fold,
    rx_bandwidth,
    # minmax | lttb | stride display downsampling
    downsample_indices,
    # Plotly builders (figures carry registry-measured annotations):
    waveform_figure,
    bode_figure,
    tran_figure,
    dc_figure,
    noise_figure,
    pss_spectrum_figure,
    fft_spectrum_figure,
    log_view_html,
    # trace snapshots + static PNG / interactive HTML export (visual verification):
    snapshot,
    save_traces,
    load_traces,
    export_pngs,
    export_htmls,
    PlotTemplate,
    PLOT_TEMPLATES,
)

ds = load_result("runs/tb_ac/run_1/netlist.raw")  # or a Spectre "…-raw" dir
measure_dataset(ds, {"meas": "ugf", "out": "v(vout)"})  # identical math to the optimizer
bode_figure(ds, "v(vout)").show()  # UGF/PM/f3dB drawn on the plot

# store the KEY traces + auto-export PNGs and interactive HTMLs per analysis:
snap = snapshot(
    run.artifact_path(),
    "verify/",
    label="amp022_ac",
    annotations={"ac": {"dcgain [dB]": 48.0, "pm [deg]": 81.3}},
)
snap["traces"]  # one compressed .npz (JSON manifest + arrays; complex survives)
snap["pngs"]  # per-analysis PNGs: combined + one autoscaled breakout per trace
snap["htmls"]  # interactive Plotly companions (one shared plotly.min.js rides along)
load_traces(snap["traces"])  # round-trips to a WaveDataset — recipes/figures work on it
```

The **per-analysis plot templates** (`PLOT_TEMPLATES`) pick the presentation by kind —
Bode panels for `ac`/`stb`/`pac`, time-domain for `tran`/`pss_td`, transfer for `dc`,
log-log density for `noise`/`pnoise`, a harmonic stem for `pss` (color-cycled; the
HTML twin uses grouped bars); unknown swept kinds fall back to plain x-y, point data
(`op`) is skipped, and pac *sidebands* (`pac_sb*`, one PSF per sideband on a real run)
stay out of a default snapshot (`include_sidebands=True` opts in). Override per call:
`export_pngs(ds, out, templates={"ac": PlotTemplate("xy", "my view")})`.

Each analysis exports one **combined** image plus (default `per_signal=True`) one
**autoscaled breakout per trace** — a mV chopping ripple next to a rail-to-rail clock
is invisible on shared axes but obvious alone; in the HTML pages, clicking a legend
entry isolates a trace instead. Default trace selection keeps the plots honest: node
voltages only (branch-current `INST:p` signals squash the axis), numerically-zero
traces dropped (an AC-grounded rail is a −6000 dB floor line), noise-family plots
show **density signals only** (Spectre's `gain` input-referral transfer stays out),
and top-level nets rank before subcircuit-internal (`XDUT.*`) nodes. Pin exact traces
via a template's `signals=`.

### Stimulus and the data eye

`stimulus.Data(fmt, rate_gbd, order=7, n_warm=8, seed=1, t0=8e-9, tr_ui=0.2)` describes one
PRBS-driven stream (NRZ `{-1,+1}` or Gray-coded PAM4); `pwl(name, node, ref, data, vcm=,
swing=, delay_ui=, invert=)` emits the source line, and an FFE tap is the same `Data` delayed
`k` UI, exact by construction. `eye.eye_metrics(t, x, data, filtered=True, full_scale=1.0)`
groups samples by the *transmitted* symbol (FFT latency search, sampling phase swept over one
UI) behind a 4th-order Bessel-Thomson receiver (0.75 x baud NRZ, 0.5 x baud PAM4) and returns
`eye_h_norm`, **two** eye widths, `vecp_db` (capped at 40 dB), `er_db` (unipolar inputs only, `nan`
otherwise), `oma_db`/`oma_norm`, and for PAM4 `rlm` + `pam4_eye_heights`; a closed eye gives
finite numbers, an inverting stage is detected (`polarity`). `fold()` gives eye-diagram
coordinates for a plot.

**The two eye widths, unambiguously named.** Both count the fraction of the swept sampling phases
at which every adjacent level pair is strictly open, but over different windows: `eye_w_ui_1s`
uses a **±one-sample** window (UI/`OVERSAMPLE`), `eye_w_ui_sample_window` the
**±`SAMPLE_HALF_UI`** (0.1 UI) window the eye HEIGHT statistic is taken over. The second is the
stricter, self-consistent one — an eye counts as open at a phase under the same window its height
was measured with — and on an ideal eye it runs ~0.19 UI narrower. They are two measurements of
one eye: a design scored on one and compared against the other looks like it changed when it did
not, so both are reported under explicit names and neither is ever spelled bare `eye_w_ui` — that
name has meant BOTH metrics at different points in this module's design lineage, silently
disagreeing by ≈0.19 UI. The sampling-phase count is a parameter (`n_phases=`, default `PHASES`,
the certified value) whose value rides in the result as `sample_phases`, alongside
`sample_half_ui` (= `SAMPLE_HALF_UI`) — a re-run at a different phase count is visible in the row.

The eye is a **registered measurement kind** (`register_measurements` in the core registry):
`{meas: eye_h_norm | eye_w_ui_1s | eye_w_ui_sample_window | vecp_db | ecp_db | er_db | oma_db | oma_norm | rlm |
eye_latency_ps, out, fmt, rate_gbd, order?, n_warm?, seed?, t0?, tr_ui?, full_scale?,
filtered?, ref?, time?}` runs through `measure_dataset` / `measure_many` / the API's measure
route and shows in `measurement_catalog()` like every built-in. The math lives here (scipy),
the name in the shared catalog — importing `spicexplorer_waveview` registers it.

The log helpers `parse_measures(text) -> (measures, failed)` and `fatal_lines(text)` are
core's `spice_engine.sim_log`, re-exported beside `parse_log_text` (the same rules
`run_deck` applies to its own log).

Key semantics (mirroring the engines' own result adapters):

- analyses are keyed by the **engine-neutral analysis vocabulary** (`ac`/`dc`/`op`/
  `tran`/`noise`/`noise_spectrum`/`pss`/`pnoise`/`pac`/`stb`; the pac BASEBAND
  (`pac.0.pac`, the chopper/SC signal-band transfer) claims `pac`, other sidebands
  land under `pac_sb*`, and the metadata-only `pac.pac` parent is skipped — the
  backend reader's sibling rule), with per-engine alias chains
  (Spectre's `noise_spectrum → noise`, ngspice's two separate noise plots) matching
  `NgspiceSimResult`/`SpectreSimResult`;
- signal lookup is cross-engine tolerant: `vout` finds ngspice's `v(vout)` and vice
  versa;
- `DatasetResult.scalar` degrades to NaN, `.wave` raises — exactly the core protocol;
- Spectre `*.info` op-point STRUCTs load as `inst:param` scalars; the ADE
  model/parameter dumps (`modelParameter` …) are **never** read (NDA guard);
- unknown ngspice plot titles are kept (slugified) with a warning — never dropped.

## REST surface (`spicexplorer-api`)

| Route | Purpose |
|---|---|
| `POST /api/waveview/open` | open an artifact by absolute path (whitelisted) → dataset meta |
| `GET /api/waveview/datasets[/{id}]` | list/inspect open datasets |
| `DELETE /api/waveview/datasets/{id}` | close (free) a dataset |
| `GET /api/waveview/datasets/{id}/wave` | waveform data: `fmt=auto\|mag_db\|mag\|phase_deg\|re\|im\|complex`, `max_points` + `method=minmax\|lttb\|stride\|none` downsampling |
| `POST /api/waveview/datasets/{id}/measure` | evaluate Tier-1 `{meas: …}` recipes (per-item degradation) |
| `GET /api/waveview/datasets/{id}/scalars` | op-point / per-device `inst:param` tables |
| `GET /api/waveview/datasets/{id}/log` | parsed, severity-classified simulator log |
| `GET /api/waveview/log/stream` | **SSE live tail** of any whitelisted log (works mid-simulation) |
| `GET /api/waveview/browse` | list result artifacts in a directory |
| `GET /api/waveview/measurements` | the measurement catalog (name → kind/required/analysis) |
| `GET /api/waveview/runs[?project_id=]` | optimizer runs the viewer can open (disk truth: their `run.json`s), newest first |
| `GET /api/waveview/runs/{run_id}/artifacts` | a run's openable artifacts (per-trial raws, Spectre raw dirs, logs incl. `run.log`) |
| `GET /api/waveview/runs/{run_id}/artifacts/file` | fetch ANY run artifact by identity (`?rel=` — traversal-safe) |
| `POST /api/waveview/open_run` | open a run's result artifacts by `run_id` (optional `match` substring; `merge: true` combines the newest testbench raws into one dataset via `merge_datasets`) |
| `POST /api/waveview/runs/{run_id}/prune` | free a `keep_raw` run's sim raws on demand (`metrics_only` retention; idempotent, open datasets evicted) |
| `POST /api/waveview/upload` | upload an artifact from the browser (`.raw` / Spectre-PSF `.zip` / log) → staged + auto-opened |
| `GET /api/waveview/uploads` / `DELETE …/{id}` | staged-upload inventory + delete (open-dataset dirs protected; TTL sweep, `SPICEXPLORER_UPLOAD_TTL_DAYS`) |

Retention: the optimizer deletes per-trial `.raw` files after each evaluate by default —
start a run with `keep_raw: true` (`POST /api/optimize/start`) to retain them for the
viewer (disk grows with budget × testbenches), and reclaim the space later with the
`prune` route. Logs are always retained; the Spectre lane's persisted `-raw` dirs are
unaffected.

Path posture: absolute paths only, resolved under `REPO_ROOT` / `WORK_ROOT`; the
`SPICEXPLORER_WAVEVIEW_ROOTS` env var (`:`-separated) opts in extra roots (e.g. a
Spectre work dir outside the repo).

## Notebooks

Each is a marimo notebook: open it with
`uv run marimo edit packages/spicexplorer-waveview/notebooks/<name>.py`, or run all its cells
from that folder with `uv run python <name>.py`.

- [notebooks/waveform_viewer_ngspice.py](notebooks/waveform_viewer_ngspice.py) —
  live-ngspice tour: load `.raw` artifacts, every analysis plotted interactively,
  measurements + log viewer.
- [notebooks/waveform_viewer_spectre.py](notebooks/waveform_viewer_spectre.py) —
  Spectre PSF tour (real raw dirs incl. PSS/stb), same API. Runs only on the Spectre lane:
  `virtuoso_bridge` importable, `SPICEXPLORER_SPECTRE_MODEL_ROOT` set to the closed-PDK model
  wrapper directory and the bridge env file (`SPICEXPLORER_VB_ENV_FILE`); `tests/test_notebooks.py`
  gates it as `live_spectre`. Its recorded outputs are not published (they hold licensed-lane
  data).
- [notebooks/waveview_api_tour.py](notebooks/waveview_api_tour.py) — the REST
  routes end-to-end against a live server, including the SSE log tail.
- [notebooks/eye_and_stimulus.py](notebooks/eye_and_stimulus.py) — pure Python: a
  PRBS/PAM4 stimulus, a synthetic channel, the BT4 eye metrics, the eye as a registered
  `{meas: …}` recipe on a `WaveDataset`, and the fold plot.

## Testing

`uv run pytest packages/spicexplorer-waveview/tests` — fast, no simulator needed:
`spicexplorer_waveview.testing` synthesizes real-format artifacts (ngspice ASCII raw,
Spectre psfascii incl. STRUCT `.info` and an NDA-decoy `modelParameter.info` that must
be skipped) with analytic ground truth. Live-SPICE checks ride the usual `-m slow`
marker in the API/optimizer suites.
