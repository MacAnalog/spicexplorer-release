"""OCEAN canonical metrics on headless Spectre raw dirs.

With the native-first direction, Cadence's own OCEAN calculators
(`dB20`/`bandwidth`/`gainBwProd`/`phaseMargin`/`OP` …) are the *primary* metric path for
Spectre results; the Tier-1 Python parse stays as the ngspice path and cross-check. This
module runs them **without** a Virtuoso session, ADE, or the bridge daemon: one persistent
`ocean -nograph` process (one `.cxt` load + license checkout) is fed SKILL blocks over
stdin, and each evaluation hands its scalars back through a per-candidate file — robust to
stdout buffering, and exactly the shape the optimizer loop needs.

Measured live: **~6.3 s one-time startup, then
~30 ms per candidate** for a full op+ac metric set on *distinct* raw dirs — vs 7.4 s per
one-shot `ocean` and 0.7 s for the Spectre simulation itself. The live bridge daemon (CIW)
evaluates the same blocks at ~22 ms, so this transport gives up nothing while needing no
Virtuoso. `measure_batch` rides N candidates on ONE submission — 18.6 → 10.1 ms per
candidate live — and every submission persists its exact SKILL beside the metrics file
(`<stem>.il`, replayable via `ocean -nograph < file.il`).

Naming truths this module encodes (live-verified):

* **Signals are BARE names** on a headless raw: `v("v_out")`, never `v("/v_out")`
  (OCN-6054). Hierarchy keeps dots: `v("XOTA.tail")`.
* **Result names ≠ analysis names**: `results()` → `ac` / `dc` / `dcOpInfo`. A `dcOp dc`
  analysis registers as ``dc``; the `finalTimeOP info what=oppoint` file as ``dcOpInfo``
  (`selectResults("dcOp")` fails, OCN-6038).
* `OP("<inst>" "<param>")` / `pv()` read the per-device `.info` STRUCTs natively — the
  values the bridge's psfascii parser drops.
* `phaseMargin()` refuses a closed-loop wave whose gain never crosses one — it wants a
  loop-gain (`stb`) wave. Expect NaN for it on a plain closed-loop `ac`.

No `virtuoso_bridge` import anywhere here (blast-radius rule): the only requirements are
`tcsh`, the Cadence cshrc, and an OCEAN license while the session is open — `close()`
promptly (or use the context manager) so the token is returned.
"""

from __future__ import annotations

import math
import os
import re
import shlex
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from typing import IO, Any

__all__ = [
    "OceanMeasurement",
    "OceanMetricsError",
    "OceanMetricsSession",
    "ac_gain_db_at",
    "ac_bandwidth_3db",
    "ac_gain_bw_product",
    "ac_peak_mag",
    "op_node_voltage",
    "device_op_param",
    "render_measure_block",
    "parse_metrics_text",
]

_SENTINEL = "__spicexplorer_ocean_done__"
_NAME_RE = re.compile(r"^[A-Za-z0-9_.:\-]+$")
_METRIC_LINE_RE = re.compile(r"^([A-Za-z0-9_.:\-]+)=(.+)$")


class OceanMetricsError(RuntimeError):
    """A session-level failure (spawn, timeout, dead process) — never a NaN metric."""


@dataclass(frozen=True)
class OceanMeasurement:
    """One named scalar to evaluate with an OCEAN result selected.

    ``result`` is the OCEAN *result* name (``ac`` / ``dc`` / ``dcOpInfo`` / ``tran`` — see
    the module docstring: these are not the deck's analysis names). ``expr`` is a SKILL
    expression evaluated after ``selectResults("<result>")``; it must reduce to a number
    (a complex value is taken as its magnitude; anything else — e.g. a whole wave —
    degrades to NaN, never an exception).
    """

    name: str
    result: str
    expr: str

    def __post_init__(self) -> None:
        if not _NAME_RE.match(self.name):
            raise ValueError(f"measurement name {self.name!r} must match {_NAME_RE.pattern}")
        if not _NAME_RE.match(self.result):
            raise ValueError(f"result name {self.result!r} must match {_NAME_RE.pattern}")
        if "\n" in self.expr or not self.expr.strip():
            raise ValueError(f"expr for {self.name!r} must be one non-empty SKILL line")


def _bare(signal: str) -> str:
    """Strip a leading ``/`` — headless-raw signals are bare names."""
    return signal.lstrip("/")


def ac_gain_db_at(name: str, signal: str, freq_hz: float) -> OceanMeasurement:
    """``dB20`` of an ac signal at one frequency, e.g. the passband gain probe."""
    return OceanMeasurement(name, "ac", f'value(dB20(v("{_bare(signal)}")) {freq_hz:g})')


def ac_bandwidth_3db(name: str, signal: str) -> OceanMeasurement:
    """Low-pass −3 dB bandwidth of an ac signal."""
    return OceanMeasurement(name, "ac", f'bandwidth(v("{_bare(signal)}") 3 "low")')


def ac_gain_bw_product(name: str, signal: str) -> OceanMeasurement:
    """OCEAN ``gainBwProd`` of an ac signal."""
    return OceanMeasurement(name, "ac", f'gainBwProd(v("{_bare(signal)}"))')


def ac_peak_mag(name: str, signal: str) -> OceanMeasurement:
    """Peak magnitude of an ac signal (``ymax(mag(...))``)."""
    return OceanMeasurement(name, "ac", f'ymax(mag(v("{_bare(signal)}")))')


def op_node_voltage(name: str, node: str) -> OceanMeasurement:
    """An operating-point node voltage (result ``dc`` — where a `dcOp dc` run lands)."""
    return OceanMeasurement(name, "dc", f'v("{_bare(node)}")')


def device_op_param(name: str, instance: str, param: str) -> OceanMeasurement:
    """A per-device op scalar (``gm``, ``vdsat``, ``region`` …) from the `.info` STRUCTs."""
    return OceanMeasurement(name, "dcOpInfo", f'OP("{_bare(instance)}" "{param}")')


def _skill_path(path: Path | str, what: str) -> str:
    """A filesystem path as a SKILL string literal (reject characters we won't escape)."""
    text = str(path)
    if any(ch in text for ch in ('"', "\\", "\n")):
        raise ValueError(f"{what} {text!r} contains characters unsafe in a SKILL string")
    return f'"{text}"'


def render_measure_block(
    raw_dir: Path | str,
    measurements: list[OceanMeasurement] | tuple[OceanMeasurement, ...],
    out_path: Path | str,
) -> str:
    """The SKILL block for one candidate: open the raw dir, evaluate, fprintf scalars.

    Every statement is a *top-level* form and every fallible step is `errset`-guarded or
    followed by a NaN fallback, so one bad measurement (missing signal, wave-valued expr,
    absent result) degrades to ``<name>=NaN`` while the rest still evaluate — and the
    sentinel line always lands, so the caller never times out on a merely-bad metric.
    """
    if not measurements:
        raise ValueError("at least one OceanMeasurement is required")
    names = [m.name for m in measurements]
    if len(set(names)) != len(names):
        raise ValueError(f"duplicate measurement names: {sorted(names)}")

    lines: list[str] = [
        f"setq(__sxq_port outfile({_skill_path(out_path, 'out_path')}))",
        f"setq(__sxq_open errset(openResults({_skill_path(raw_dir, 'raw_dir')})))",
    ]
    current_result: str | None = None
    for m in measurements:
        if m.result != current_result:
            lines.append(
                f'setq(__sxq_sel and(__sxq_open errset(selectResults("{m.result}"))))'
            )
            current_result = m.result
        lines += [
            "setq(__sxq_val nil)",
            f"when(__sxq_sel setq(__sxq_r errset({m.expr})))",
            "when(and(__sxq_sel __sxq_r) setq(__sxq_x car(__sxq_r))"
            " when(complexp(__sxq_x) setq(__sxq_x mag(__sxq_x)))"
            " setq(__sxq_val errset(float(__sxq_x))))",
            f'if(__sxq_val fprintf(__sxq_port "{m.name}=%.10e\\n" car(__sxq_val))'
            f' fprintf(__sxq_port "{m.name}=NaN\\n"))',
        ]
    lines += [
        f'fprintf(__sxq_port "{_SENTINEL}=1\\n")',
        "close(__sxq_port)",
    ]
    return "\n".join(lines) + "\n"


def parse_metrics_text(text: str) -> dict[str, float]:
    """``name=value`` lines → floats (``NaN`` literal included); junk lines are ignored."""
    out: dict[str, float] = {}
    for line in text.splitlines():
        m = _METRIC_LINE_RE.match(line.strip())
        if not m or m.group(1) == _SENTINEL:
            continue
        try:
            out[m.group(1)] = float(m.group(2))
        except ValueError:
            out[m.group(1)] = math.nan
    return out


def _read_vb_env_value(env_file: Path, key: str) -> str | None:
    """One ``KEY=VALUE`` from a bridge-style env file (quotes and ``export`` tolerated)."""
    try:
        lines = env_file.read_text().splitlines()
    except OSError:
        return None
    for raw in lines:
        line = raw.strip()
        if line.startswith("export "):
            line = line[len("export ") :]
        if line.startswith(f"{key}="):
            return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


class OceanMetricsSession:
    """A persistent headless ``ocean -nograph`` evaluator (spawn lazily, reuse warm).

    One session = one subprocess = one OCEAN license token held while open. ``measure()``
    respawns transparently if the process died (the respawn re-pays the ~6 s startup);
    a *timeout* kills the process and raises :class:`OceanMetricsError` — a hung ocean
    must never stall an optimizer loop silently.
    """

    def __init__(
        self,
        cshrc: Path | str | None = None,
        *,
        work_dir: Path | str | None = None,
        startup_timeout: float = 180.0,
        eval_timeout: float = 60.0,
        _argv: list[str] | None = None,
    ) -> None:
        if _argv is None:
            if cshrc is None:
                raise ValueError("cshrc is required (or use OceanMetricsSession.from_vb_env)")
            cshrc_path = Path(cshrc).expanduser()
            if not cshrc_path.is_file():
                raise FileNotFoundError(f"Cadence cshrc not found: {cshrc_path}")
            _argv = [
                "tcsh",
                "-f",
                "-c",
                f"source {shlex.quote(str(cshrc_path))}; exec ocean -nograph",
            ]
        self._argv = _argv
        self._startup_timeout = float(startup_timeout)
        self._eval_timeout = float(eval_timeout)
        if work_dir is None:
            self._tmp = tempfile.TemporaryDirectory(prefix="spicexplorer-ocean-")
            self._work_dir = Path(self._tmp.name)
        else:
            self._tmp = None
            self._work_dir = Path(work_dir)
            self._work_dir.mkdir(parents=True, exist_ok=True)
        self._proc: subprocess.Popen[str] | None = None
        self._log: IO[Any] | None = None
        self._seq = 0
        self._just_spawned = False
        self.last_eval_seconds: float | None = None

    @classmethod
    def from_vb_env(
        cls, env_file: Path | str | None = None, **kwargs: Any
    ) -> "OceanMetricsSession":
        """Resolve the cshrc from ``VB_CADENCE_CSHRC`` — the process env first, then a
        bridge-style env file (default ``~/.virtuoso-bridge/local.env``)."""
        cshrc = os.environ.get("VB_CADENCE_CSHRC", "").strip() or None
        if cshrc is None:
            candidate = Path(env_file).expanduser() if env_file is not None else (
                Path.home() / ".virtuoso-bridge" / "local.env"
            )
            cshrc = _read_vb_env_value(candidate, "VB_CADENCE_CSHRC")
        if not cshrc:
            raise OceanMetricsError(
                "VB_CADENCE_CSHRC not set and not found in the bridge env file — "
                "pass cshrc= explicitly."
            )
        return cls(cshrc, **kwargs)

    # -- process management ---------------------------------------------------
    @property
    def is_alive(self) -> bool:
        return self._proc is not None and self._proc.poll() is None

    def _spawn(self) -> None:
        if self._log is None:
            self._log = (self._work_dir / "ocean.log").open("a", encoding="utf-8")
        self._proc = subprocess.Popen(
            self._argv,
            stdin=subprocess.PIPE,
            stdout=self._log,
            stderr=subprocess.STDOUT,
            text=True,
            # ocean drops `.cadence/` perf litter in its cwd — keep that inside the
            # session's own work dir, never the caller's checkout
            cwd=self._work_dir,
        )
        self._just_spawned = True

    def _log_tail(self, n: int = 12) -> str:
        log_path = self._work_dir / "ocean.log"
        try:
            return "\n".join(log_path.read_text(errors="replace").splitlines()[-n:])
        except OSError:
            return "<no ocean.log>"

    def _kill(self) -> None:
        if self._proc is not None and self._proc.poll() is None:
            self._proc.kill()
            self._proc.wait(timeout=10)
        self._proc = None

    def close(self) -> None:
        """Quit ocean (releasing its license token) and clean the temp work dir."""
        if self._proc is not None and self._proc.poll() is None:
            try:
                assert self._proc.stdin is not None
                self._proc.stdin.write("exit\n")
                self._proc.stdin.flush()
                self._proc.wait(timeout=15)
            except (OSError, subprocess.TimeoutExpired):
                self._kill()
        self._proc = None
        if self._log is not None:
            self._log.close()
            self._log = None
        if self._tmp is not None:
            self._tmp.cleanup()

    def __enter__(self) -> "OceanMetricsSession":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # -- evaluation -----------------------------------------------------------
    def measure(
        self,
        raw_dir: Path | str,
        measurements: list[OceanMeasurement] | tuple[OceanMeasurement, ...],
        *,
        label: str | None = None,
    ) -> dict[str, float]:
        """Evaluate ``measurements`` on one raw dir → ``{name: float}`` (NaN = that metric
        failed; an :class:`OceanMetricsError` = the session itself failed)."""
        raw = Path(raw_dir)
        if not raw.is_dir():
            raise OceanMetricsError(f"raw dir does not exist: {raw}")
        self._seq += 1
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", label) if label else "eval"
        out_path = self._work_dir / f"{self._seq:04d}_{safe}.metrics"
        block = render_measure_block(raw, measurements, out_path)
        self._persist_block(out_path, block)
        self._write_block(block)
        text = self._await_sentinel(out_path, n_evals=1)
        parsed = parse_metrics_text(text)
        return {m.name: parsed.get(m.name, math.nan) for m in measurements}

    def measure_batch(
        self,
        raw_dirs: "list[Path | str] | tuple[Path | str, ...]",
        measurements: list[OceanMeasurement] | tuple[OceanMeasurement, ...],
        *,
        label: str | None = None,
    ) -> list[dict[str, float]]:
        """Evaluate the same measurement set on MANY raw dirs in **one** ocean submission.

        The warm per-eval cost of :meth:`measure` is round-trip-dominated (a pipe write +
        an output-file poll per candidate), not SKILL-evaluation-dominated — batching N
        candidates into a single stdin submission pays that round trip once. ocean executes
        the concatenated blocks sequentially and each candidate writes its own metrics
        file, so waiting for the LAST file's sentinel guarantees all are complete; per-
        candidate failures still degrade to NaN lines (never abort the batch). Returns one
        ``{name: float}`` dict per raw dir, in order.
        """
        raws = [Path(r) for r in raw_dirs]
        if not raws:
            return []
        for raw in raws:
            if not raw.is_dir():
                raise OceanMetricsError(f"raw dir does not exist: {raw}")
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", label) if label else "batch"
        blocks: list[str] = []
        out_paths: list[Path] = []
        for i, raw in enumerate(raws):
            self._seq += 1
            out_path = self._work_dir / f"{self._seq:04d}_{safe}_{i:03d}.metrics"
            out_paths.append(out_path)
            block = render_measure_block(raw, measurements, out_path)
            self._persist_block(out_path, block)
            blocks.append(block)
        self._write_block("".join(blocks))
        self._await_sentinel(out_paths[-1], n_evals=len(raws))
        results: list[dict[str, float]] = []
        for out_path in out_paths:
            text = out_path.read_text(errors="replace") if out_path.exists() else ""
            parsed = parse_metrics_text(text)
            results.append({m.name: parsed.get(m.name, math.nan) for m in measurements})
        return results

    # -- transport (shared by measure / measure_batch) --------------------------
    @staticmethod
    def _persist_block(out_path: Path, block: str) -> None:
        """Persist the submitted SKILL beside its metrics file (``<same-stem>.il``).

        The audit trail: like the per-candidate `.scs` decks the simulator leaves in
        `deck_dir`, every OCEAN evaluation leaves exactly what was piped to the session —
        so a surprising metric can be replayed by hand (`ocean -nograph < file.il`).
        """
        try:
            out_path.with_suffix(".il").write_text(block)
        except OSError:  # auditing must never break an evaluation
            pass

    def _write_block(self, block: str) -> None:
        """Write one SKILL submission to the live ocean stdin (one transparent respawn)."""
        if not self.is_alive:
            self._spawn()
        assert self._proc is not None and self._proc.stdin is not None
        try:
            self._proc.stdin.write(block)
            self._proc.stdin.flush()
        except (BrokenPipeError, OSError):
            # died between evals (crash, license drop) — one transparent respawn+retry
            self._kill()
            self._spawn()
            assert self._proc is not None and self._proc.stdin is not None
            try:
                self._proc.stdin.write(block)
                self._proc.stdin.flush()
            except (BrokenPipeError, OSError) as exc:
                self._kill()
                raise OceanMetricsError(
                    f"ocean died immediately on respawn; log tail:\n{self._log_tail()}"
                ) from exc

    def _await_sentinel(self, out_path: Path, *, n_evals: int) -> str:
        """Poll ``out_path`` until its sentinel lands (timeout scales with ``n_evals``)."""
        assert self._proc is not None
        timeout = self._eval_timeout * max(1, n_evals) + (
            self._startup_timeout if self._just_spawned else 0.0
        )
        t0 = time.perf_counter()
        deadline = t0 + timeout
        text = ""
        while time.perf_counter() < deadline:
            if out_path.exists():
                text = out_path.read_text(errors="replace")
                if f"{_SENTINEL}=1" in text:
                    break
            if self._proc.poll() is not None and not out_path.exists():
                # process exited without producing the file — respawn happens next call
                raise OceanMetricsError(
                    f"ocean exited (rc={self._proc.returncode}) before producing metrics; "
                    f"log tail:\n{self._log_tail()}"
                )
            time.sleep(0.01)
        else:
            self._kill()
            raise OceanMetricsError(
                f"ocean metrics timed out after {timeout:.0f}s for {out_path.name}; "
                f"log tail:\n{self._log_tail()}"
            )
        self.last_eval_seconds = time.perf_counter() - t0
        self._just_spawned = False
        return text
