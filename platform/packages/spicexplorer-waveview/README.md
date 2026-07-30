# spicexplorer-waveview

**Universal simulation-result (waveform) viewer — backend.** Load any ngspice `.raw`
file or Cadence Spectre psfascii raw directory into one engine-neutral dataset, run
**every Tier-1 registry measurement** against it, parse/tail the simulator log, and
build interactive Plotly figures — the notebook/API backend the Studio UI's **Analyze**
view sits on.

## Purpose & layering

A **leaf tool**: depends on `spicexplorer-core` only (the `SimResult` protocol and the
measurement registry), plus `spicelib`/`psf-utils`/`numpy`/`plotly`/`pydantic` from
PyPI. It never imports a peer tool. The Spectre PSF-dir reading is a deliberate
*sibling* of the optimizer's `backends/spectre.py` readers (peer packages can't import
each other) — parity between the two is pinned by `tests/test_loaders.py::
test_spectre_parity_with_backend_reader`, not by imports.

The REST adapter (`spicexplorer-api`) mounts this as the `/api/waveview/*` routes.

## Public API

```python
from spicexplorer_waveview import (
    load_result,            # path → WaveDataset (sniffs ngspice vs spectre)
    load_ngspice_raw,       # .raw file → WaveDataset (all plots, incl. multi-plot)
    load_spectre_raw_dir,   # psfascii -raw dir → WaveDataset (ac/dc/tran/noise/pss/pnoise/pac/stb + op + .info)
    merge_datasets,         # N datasets → ONE (a run's testbenches as one tree; dup analyses suffixed #2…)
    WaveDataset, DatasetResult,   # dataset model + its SimResult-protocol adapter
    measure_dataset, measure_many, measurement_catalog,  # Tier-1 recipes on loaded data
    parse_sim_log, discover_log, classify_line,          # log viewer backend
    downsample_indices,     # minmax | lttb | stride display downsampling
    # Plotly builders (figures carry registry-measured annotations):
    waveform_figure, bode_figure, tran_figure, dc_figure,
    noise_figure, pss_spectrum_figure, fft_spectrum_figure, log_view_html,
    # trace snapshots + static PNG / interactive HTML export (visual verification):
    snapshot, save_traces, load_traces, export_pngs, export_htmls,
    PlotTemplate, PLOT_TEMPLATES,
)

ds = load_result("runs/tb_ac/run_1/netlist.raw")       # or a Spectre "…-raw" dir
measure_dataset(ds, {"meas": "ugf", "out": "v(vout)"})  # identical math to the optimizer
bode_figure(ds, "v(vout)").show()                       # UGF/PM/f3dB drawn on the plot

# store the KEY traces + auto-export PNGs and interactive HTMLs per analysis:
snap = snapshot(run.artifact_path(), "verify/", label="amp022_ac",
                annotations={"ac": {"dcgain [dB]": 48.0, "pm [deg]": 81.3}})
snap["traces"]   # one compressed .npz (JSON manifest + arrays; complex survives)
snap["pngs"]     # per-analysis PNGs: combined + one autoscaled breakout per trace
snap["htmls"]    # interactive Plotly companions (one shared plotly.min.js rides along)
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

- [notebooks/waveform_viewer_ngspice.ipynb](notebooks/waveform_viewer_ngspice.ipynb) —
  live-ngspice tour: load `.raw` artifacts, every analysis plotted interactively,
  measurements + log viewer.
- [notebooks/waveform_viewer_spectre.ipynb](notebooks/waveform_viewer_spectre.ipynb) —
  Spectre PSF tour (real raw dirs incl. PSS/stb), same API.
- [notebooks/waveview_api_tour.ipynb](notebooks/waveview_api_tour.ipynb) — the REST
  routes end-to-end against a live server, including the SSE log tail.

## Testing

`uv run pytest packages/spicexplorer-waveview/tests` — fast, no simulator needed:
`spicexplorer_waveview.testing` synthesizes real-format artifacts (ngspice ASCII raw,
Spectre psfascii incl. STRUCT `.info` and an NDA-decoy `modelParameter.info` that must
be skipped) with analytic ground truth. Live-SPICE checks ride the usual `-m slow`
marker in the API/optimizer suites.
