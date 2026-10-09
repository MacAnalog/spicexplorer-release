"""The RL optimizer backend and the NEWCAS demo runner are RETIRED (owner ruling 2026-09-25).

`spicexplorer.optimization.rl` was unused and not runnable as shipped: `agent_trainer` imported a
package that exists nowhere (`rl_framework`), `rl_factory`/`rl_optimizer` hard-imported
`stable-baselines3` and `circuit_env` imported `gymnasium`, neither declared in any extra or the lock,
and `custom_agents/td3.py` was a one-line TODO. `spicexplorer.demo.newcas_demo_runner` was a parallel
reimplementation of the API's data flow whose only consumer was its own test. Both were deleted with
their tests (platform `doc/TODO.md` §16).

This file is the proof the removal is complete and stays complete:

* the modules are not importable. A checkout that had compiled the RL tree keeps an untracked
  `__pycache__`-only `rl/` after `git pull`, and Python imports that directory — and each of its
  sourceless sub-package directories (`custom_agents`, `models`, `utils`) — as an empty namespace
  package. Such a leftover counts as removed, because it holds no importable code; every former
  leaf module must still be missing. `rm -rf packages/spicexplorer/src/spicexplorer/optimization/rl`
  tidies it up;
* no Python module or notebook in the platform — nor in the orchestration repo when its checkout is
  beside this one — imports them, statically or through `importlib.import_module`/`__import__`;
* the RL-only DSL names are gone from `core.domains` (`OptimizerType.RL`, `NoiseType`, `AgentType`,
  the `*Config` agent dataclasses), and a stale `type: reinforcement_learning` raises a ValueError
  naming the retirement instead of a bare "unknown engine", while such a YAML still LOADS (the DSL
  keeps `type` a free string), a typo is still "not a known engine", and no shipped YAML names it;
* the live reference docs describe the retired code only as retired.
"""

from __future__ import annotations

import ast
import importlib
import importlib.util
import json
import os
import py_compile
import re
import sys
import uuid
from collections.abc import Iterable, Iterator
from importlib.machinery import ModuleSpec, all_suffixes
from pathlib import Path

import pytest
from _spicexplorer_fixtures import EXAMPLE_YAML, REPO_ROOT

RL_PACKAGE = "spicexplorer.optimization.rl"
DEMO_RUNNER = "spicexplorer.demo.newcas_demo_runner"
RETIRED_MODULES = (RL_PACKAGE, DEMO_RUNNER)

# Every module the deleted RL tree shipped. Each must be gone even when a stale bytecode-only `rl/`
# directory lingers: a leaf module (`rl_factory`, `custom_agents.ddpg`, …) must fail to import (a
# `__pycache__/*.pyc` without its source is never imported), and a sub-package directory
# (`custom_agents`, `models`, `utils`) may at most import as an empty namespace package.
RL_SUBMODULES = tuple(
    f"{RL_PACKAGE}.{name}"
    for name in (
        "rl_optimizer",
        "rl_factory",
        "circuit_env",
        "agent_trainer",
        "custom_agents",
        "custom_agents.base",
        "custom_agents.ddpg",
        "custom_agents.sac",
        "custom_agents.td3",
        "models",
        "models.actor",
        "models.base",
        "models.critic",
        "utils",
        "utils.enums",
        "utils.hyperparameters",
        "utils.replay_buffer",
        "utils.typing",
        "utils.utils",
    )
)

# The RL-only names `core.domains` used to export (enums + agent config dataclasses).
RL_DOMAIN_NAMES = (
    "NoiseType",
    "AgentType",
    "NoiseConfig",
    "ReplayBufferConfig",
    "RLTrainingConfig",
    "NetworkConfig",
    "SACAlphaConfig",
    "AgentConfig",
    "DDPGConfig",
    "SACConfig",
)

SPICEXPLORER_SRC = REPO_ROOT / "packages" / "spicexplorer" / "src" / "spicexplorer"
RL_DIR = SPICEXPLORER_SRC / "optimization" / "rl"
DEMO_RUNNER_FILE = SPICEXPLORER_SRC / "demo" / "newcas_demo_runner.py"

_SKIP_DIRS = {
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
}
_IMPORT_CALLS = {"import_module", "__import__"}
# Line-scan fallback for a file that is not valid Python 3: every spelling the AST path catches.
_RETIRED_IMPORT_LINE = re.compile(
    r"^\s*(?:from|import)\s+(?:"
    r"spicexplorer\.optimization\.rl\b|spicexplorer\.demo\.newcas_demo_runner\b"
    r"|spicexplorer\.optimization\s+import\s+.*\brl\b"
    r"|spicexplorer\.demo\s+import\s+.*\bnewcas_demo_runner\b)"
)


# ── helpers ───────────────────────────────────────────────────────────────────


def _is_retired(dotted: str, retired: tuple[str, ...] = RETIRED_MODULES) -> bool:
    """True if `dotted` names one of the retired modules or anything beneath them."""
    return any(dotted == m or dotted.startswith(m + ".") for m in retired)


def _has_importable_code(spec: ModuleSpec) -> bool:
    """Whether a found spec is a real module, or a namespace package with code somewhere below it.

    A namespace package whose directories hold nothing but `__pycache__/` (bytecode the import
    system never loads without its source) is the harmless leftover of a deleted package."""
    if spec.origin not in (None, "namespace"):
        return True
    suffixes = tuple(all_suffixes())  # .py, legacy .pyc beside the source, extension modules
    for loc in spec.submodule_search_locations or []:
        for path in Path(loc).rglob("*"):
            if (
                path.is_file()
                and path.name.endswith(suffixes)
                and "__pycache__" not in path.relative_to(loc).parts
            ):
                return True
    return False


def _still_importable(name: str, retired: tuple[str, ...] = RETIRED_MODULES) -> str | None:
    """Why module `name` is NOT gone, or None when it is.

    Gone means: `name` (or a package above it inside `retired`) is missing, or `name` resolves only
    to a code-free namespace package. A ModuleNotFoundError for anything else — before the
    retirement, several RL modules already failed on `stable_baselines3`, `gymnasium` or
    `rl_framework` — means the retired code is still there, merely broken."""
    try:
        spec = importlib.util.find_spec(name)  # imports the parent packages first
    except ImportError as exc:
        if isinstance(exc, ModuleNotFoundError) and exc.name and _is_retired(exc.name, retired):
            return None
        return f"{name}: a parent package still exists and fails with {exc!r}"
    if spec is not None:
        if _has_importable_code(spec):
            where = spec.origin or list(spec.submodule_search_locations or [])
            return f"{name} is still importable from {where}"
        return None  # a bytecode-only directory left behind by `git pull`
    try:
        importlib.import_module(name)
    except ModuleNotFoundError as exc:
        if exc.name and _is_retired(exc.name, retired):
            return None
        return f"{name}: import fails on {exc.name!r}, not on the module itself: {exc!r}"
    return f"{name} imports although find_spec found no spec for it"


def _iter_sources(root: Path) -> Iterator[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for name in filenames:
            if name.endswith((".py", ".ipynb")):
                yield Path(dirpath) / name


def _source_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix != ".ipynb":
        return text
    try:
        cells = json.loads(text).get("cells", [])
    except (ValueError, AttributeError):
        return ""
    lines: list[str] = []
    for cell in cells:
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", "")
        src = "".join(src) if isinstance(src, list) else str(src)
        # IPython magics / shell escapes are not Python; blank them so the cell still parses.
        lines.extend("" if ln.lstrip().startswith(("%", "!")) else ln for ln in src.splitlines())
    return "\n".join(lines)


def _relative_target(path: Path, level: int, module: str | None) -> Path:
    """Filesystem location a relative `from <dots><module> import …` in `path` resolves to."""
    base = path.parent
    for _ in range(level - 1):
        base = base.parent
    return base.joinpath(*module.split(".")) if module else base


def _points_at_retired_file(target: Path) -> bool:
    target = target.resolve()
    rl_dir, runner = RL_DIR.resolve(), DEMO_RUNNER_FILE.resolve()
    return (
        target == rl_dir
        or rl_dir in target.parents
        or target == runner.with_suffix("")
        or target == runner
    )


def retired_imports(path: Path) -> list[tuple[int, str]]:
    """Every import of a retired module in one file, as `(line, what)`.

    Covers `import X`, `from X import Y` (incl. `from spicexplorer.optimization import rl`),
    relative imports that resolve into the deleted files, and dynamic
    `importlib.import_module("…")` / `__import__("…")` calls with a literal name. A file that is
    not valid Python 3 (a reference script copied in verbatim) falls back to a line scan so it cannot
    hide an import behind a SyntaxError."""
    text = _source_text(path)
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return [
            (no, line.strip())
            for no, line in enumerate(text.splitlines(), 1)
            if _RETIRED_IMPORT_LINE.match(line)
        ]

    hits: list[tuple[int, str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            hits += [(node.lineno, a.name) for a in node.names if _is_retired(a.name)]
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                target = _relative_target(path, node.level, node.module)
                candidates = [target] + [target / a.name for a in node.names]
                if any(_points_at_retired_file(c) for c in candidates):
                    hits.append((node.lineno, "." * node.level + (node.module or "")))
            elif node.module:
                names = [node.module] + [f"{node.module}.{a.name}" for a in node.names]
                hits += [(node.lineno, n) for n in names if _is_retired(n)][:1]
        elif isinstance(node, ast.Call):
            func = node.func
            fname = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", None)
            if fname in _IMPORT_CALLS and node.args:
                arg = node.args[0]
                if (
                    isinstance(arg, ast.Constant)
                    and isinstance(arg.value, str)
                    and _is_retired(arg.value)
                ):
                    hits.append((node.lineno, arg.value))
    return hits


def _scan(roots: Iterable[Path], exclude: Iterable[Path] = ()) -> list[str]:
    excluded = {p.resolve() for p in exclude}
    found = []
    for root in roots:
        for path in _iter_sources(root):
            if path.resolve() in excluded:
                continue
            found += [f"{path}:{line}: {what}" for line, what in retired_imports(path)]
    return found


def _orchestration_root() -> Path | None:
    """The orchestration checkout, when one is beside this platform checkout."""
    candidates = [
        os.environ.get("SPICEXPLORER_ORCHESTRATION_ROOT"),
        str(REPO_ROOT.parent / "spicexplorer-orchestration"),
    ]
    if os.environ.get("SX_ROOT"):
        candidates.append(str(Path(os.environ["SX_ROOT"]) / "spicexplorer-orchestration"))
    for cand in candidates:
        if cand and (Path(cand) / "packages").is_dir():
            return Path(cand)
    return None


def _setup_with_type(value: object):
    """The example project with `optimizer_config.type` set to `value` (any object, even None)."""
    from spicexplorer.core.domains import Project_Setup

    setup = Project_Setup.from_yaml(EXAMPLE_YAML)
    setattr(setup.optimizer_config, "type", value)
    return setup


def _retired_engine_line() -> re.Pattern[str]:
    """A YAML line selecting a retired engine: `type: reinforcement_learning`, any case/quoting."""
    from spicexplorer.optimization.orchestrator import _RETIRED_ENGINES

    names = "|".join(map(re.escape, _RETIRED_ENGINES))
    return re.compile(
        rf"^[ \t]*type[ \t]*:[ \t]*['\"]?(?:{names})['\"]?[ \t]*(?:#.*)?$", re.M | re.I
    )


# Live reference docs this retirement corrected (plus the explanatory header comment of
# `core/__init__.py`); each paragraph, list item or table row in them that names the retired code
# must say it is retired. History records keep describing the old tree on purpose: `doc/archive/`
# is not scanned, and a history row is exempt by its exact line prefix.
LIVE_DOCS = (
    "README.md",
    "CLAUDE.md",
    "packages/spicexplorer/README.md",
    "packages/spicexplorer/pyproject.toml",
    "doc/TODO.md",
    "doc/root_anchoring.md",
    "packages/spicexplorer/src/spicexplorer/core/__init__.py",
)
_HISTORY_ROWS = {
    # "What it replaced": the four parent walks the monolith had, before the runner was deleted.
    "doc/root_anchoring.md": ("| `src/spicexplorer/demo/newcas_demo_runner.py:22` |",),
}
_RETIRED_DOC_MENTION = re.compile(
    r"optimization[/.]rl\b|`rl/`|newcas_demo_runner|reinforcement_learning|rl_framework"
    r"|stable-baselines3|\b(?:NoiseType|AgentType|DDPGConfig|SACConfig|NetworkConfig|RLTrainingConfig"
    r"|ReplayBufferConfig|SACAlphaConfig)\b|\bRL\s+(?:backends?|optimizers?|agents?|path)\b"
    r"|\bRL\s+is\s+dormant\b"
)
_DOC_BLOCK_START = re.compile(r"^\s*(?:\||[-*+]\s|\d+[.)]\s)")  # table row or list item


def _doc_blocks(text: str) -> list[list[tuple[int, str]]]:
    """A Markdown/TOML text as blocks: blank-line paragraphs, each list item (with its indented
    continuation lines) and each table row on its own."""
    blocks: list[list[tuple[int, str]]] = []
    cur: list[tuple[int, str]] = []
    for no, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            if cur:
                blocks.append(cur)
            cur = []
            continue
        if _DOC_BLOCK_START.match(line) and cur:
            blocks.append(cur)
            cur = []
        cur.append((no, line))
        if line.lstrip().startswith("|"):
            blocks.append(cur)
            cur = []
    if cur:
        blocks.append(cur)
    return blocks


def stale_doc_mentions(rel: str, text: str) -> list[str]:
    """Blocks of `text` that name retired code without saying it is retired."""
    history = _HISTORY_ROWS.get(rel, ())
    stale = []
    for block in _doc_blocks(text):
        if history and block[0][1].lstrip().startswith(history):
            continue
        body = "\n".join(line for _, line in block)
        if _RETIRED_DOC_MENTION.search(body) and "retire" not in body.lower():
            stale.append(f"{rel}:{block[0][0]}: {block[0][1].strip()[:100]}")
    return stale


# ── the modules are gone ──────────────────────────────────────────────────────


def test_retired_source_files_are_deleted():
    assert not DEMO_RUNNER_FILE.exists()
    leftovers = (
        sorted(str(p.relative_to(RL_DIR)) for p in RL_DIR.rglob("*.py")) if RL_DIR.exists() else []
    )
    assert leftovers == [], f"optimization/rl/ still ships Python sources: {leftovers}"


@pytest.mark.parametrize("name", RETIRED_MODULES)
def test_retired_module_is_not_importable(name):
    assert _still_importable(name) is None


@pytest.mark.parametrize("name", RL_SUBMODULES)
def test_retired_rl_submodule_is_not_importable(name):
    # The module ITSELF must be missing. Before the retirement several of these already raised
    # ModuleNotFoundError — for `stable_baselines3` / `gymnasium` / `rl_framework`, their
    # undeclared dependencies — which a bare `pytest.raises` would have read as "gone".
    assert _still_importable(name) is None


def test_bytecode_only_leftover_counts_as_removed(tmp_path, monkeypatch):
    """Control for the two tests above, independent of this checkout's own `rl/` state.

    Builds a package, compiles it and deletes the sources: the state `git pull` leaves behind in a
    checkout that had imported the RL tree. Its directories must read as removed, its leaf modules
    as missing — and a source file put back anywhere, or a live parent failing on a missing
    dependency, must not."""
    top = f"retired_ctl_{uuid.uuid4().hex[:12]}"
    pkg = tmp_path / top
    for rel in (
        "__init__.py",
        "gone/__init__.py",
        "gone/leaf.py",
        "gone/sub/__init__.py",
        "gone/sub/deep.py",
    ):
        (pkg / rel).parent.mkdir(parents=True, exist_ok=True)
        (pkg / rel).write_text("X = 1\n")
    for src in sorted((pkg / "gone").rglob("*.py")):
        py_compile.compile(str(src), doraise=True)  # -> __pycache__/<name>.cpython-XY.pyc
        src.unlink()
    (pkg / "live").mkdir()
    (pkg / "live" / "__init__.py").write_text(f"import {top}_missing_dependency\n")
    assert list((pkg / "gone" / "sub" / "__pycache__").glob("deep.*.pyc"))
    monkeypatch.syspath_prepend(str(tmp_path))
    gone = (f"{top}.gone",)
    try:
        for name in ("gone", "gone.sub", "gone.leaf", "gone.sub.deep", "gone.never_existed"):
            assert _still_importable(f"{top}.{name}", gone) is None, name
        # The whole tree deleted (a clean checkout): the missing parent is the retired module.
        assert _still_importable(f"{top}.absent.leaf", (f"{top}.absent",)) is None
        # A live parent that fails on an undeclared dependency is broken, not gone.
        assert _still_importable(f"{top}.live.leaf", (f"{top}.live",)) is not None
        # A source file back anywhere below makes the leftover code again.
        (pkg / "gone" / "sub" / "deep.py").write_text("X = 2\n")
        importlib.invalidate_caches()
        for name in ("gone", "gone.sub", "gone.sub.deep"):
            assert _still_importable(f"{top}.{name}", gone) is not None, name
    finally:
        for mod in [m for m in sys.modules if m == top or m.startswith(top + ".")]:
            del sys.modules[mod]


# ── nothing imports them ──────────────────────────────────────────────────────


def test_scanner_detects_every_import_form(tmp_path):
    """Positive control: the scan below is only proof if it can see each import shape."""
    forms = {
        "abs.py": f"import {RL_PACKAGE}.rl_factory\n",
        "alias.py": f"import {DEMO_RUNNER} as d\n",
        "from_mod.py": f"from {RL_PACKAGE}.utils.hyperparameters import DDPGConfig\n",
        "from_pkg.py": "from spicexplorer.optimization import rl\n",
        "from_demo.py": "from spicexplorer.demo import newcas_demo_runner\n",
        "dyn.py": f"import importlib\nimportlib.import_module({RL_PACKAGE!r})\n",
        "dunder.py": f"__import__({DEMO_RUNNER!r})\n",
        "lazy.py": f"def f():\n    from {RL_PACKAGE} import DDPGAgent\n",
        "py2.py": f"print 'x'\nfrom {RL_PACKAGE} import x\n",
        "py2_pkg.py": "print 'x'\nfrom spicexplorer.optimization import rl\n",
    }
    for name, body in forms.items():
        (tmp_path / name).write_text(body)
    nb = {
        "cells": [
            {
                "cell_type": "code",
                "source": ["%matplotlib inline\n", f"from {DEMO_RUNNER} import load_trace\n"],
            }
        ]
    }
    (tmp_path / "nb.ipynb").write_text(json.dumps(nb))
    # Negative controls: live neighbours and prose mentions are not imports.
    (tmp_path / "ok.py").write_text(
        f'"""Docs may mention {RL_PACKAGE}."""\nfrom spicexplorer.optimization import orchestrator\n'
        "import spicexplorer.optimization.rlx\n"
    )
    flagged = {Path(hit.split(":", 1)[0]).name for hit in _scan([tmp_path])}
    assert flagged == set(forms) | {"nb.ipynb"}


def test_scanner_resolves_relative_imports_into_the_deleted_tree():
    opt = SPICEXPLORER_SRC / "optimization"
    assert _points_at_retired_file(_relative_target(opt / "orchestrator.py", 1, "rl"))
    assert _points_at_retired_file(
        _relative_target(opt / "stochastic" / "x.py", 2, "rl.rl_factory")
    )
    assert _points_at_retired_file(
        _relative_target(SPICEXPLORER_SRC / "demo" / "x.py", 1, "newcas_demo_runner")
    )
    assert not _points_at_retired_file(_relative_target(opt / "orchestrator.py", 1, "base"))


def test_scanner_flags_relative_imports_into_the_retired_tree(tmp_path, monkeypatch):
    """Positive control for the relative-import branch of the scan itself, on a stand-in tree (the
    real one is deleted, so nothing under `src/` can exercise it)."""
    opt, demo = tmp_path / "spicexplorer" / "optimization", tmp_path / "spicexplorer" / "demo"
    (opt / "stochastic").mkdir(parents=True)
    demo.mkdir(parents=True)
    this = sys.modules[__name__]
    monkeypatch.setattr(this, "RL_DIR", opt / "rl")
    monkeypatch.setattr(this, "DEMO_RUNNER_FILE", demo / "newcas_demo_runner.py")
    imports = {
        opt / "a.py": "from .rl import rl_factory\n",
        opt / "b.py": "from . import orchestrator, rl\n",
        opt / "stochastic" / "c.py": "def f():\n    from ..rl.utils import enums\n",
        demo / "d.py": "from .newcas_demo_runner import load_trace\n",
        demo / "e.py": "from . import newcas_demo_runner\n",
    }
    neighbours = {  # same directories, live names that merely START like the retired ones
        opt / "ok_a.py": "from . import orchestrator\nfrom .rl_utils import x\n",
        opt / "stochastic" / "ok_b.py": "from ..rlx import y\nfrom . import rl\n",
        demo / "ok_c.py": "from .newcas_demo_runner_v2 import z\n",
    }
    for path, body in {**imports, **neighbours}.items():
        path.write_text(body)
    flagged = {Path(hit.split(":", 1)[0]) for hit in _scan([tmp_path])}
    assert flagged == set(imports)


def test_no_platform_module_imports_the_retired_code():
    roots = [REPO_ROOT / d for d in ("packages", "tests", "scripts", "examples")]
    roots = [r for r in roots if r.is_dir()]
    hits = _scan(roots, exclude=[Path(__file__)])
    assert hits == [], "retired modules are still imported:\n" + "\n".join(hits)


def test_no_orchestration_module_imports_the_retired_code():
    root = _orchestration_root()
    if root is None:
        pytest.skip(
            "no spicexplorer-orchestration checkout beside this platform checkout "
            "(set SPICEXPLORER_ORCHESTRATION_ROOT to point at one)"
        )
    hits = _scan([root])
    assert hits == [], "orchestration still imports retired modules:\n" + "\n".join(hits)


# ── the RL-only DSL names are gone ────────────────────────────────────────────


def test_domains_exports_no_rl_config():
    from spicexplorer.core import domains

    still_there = [n for n in RL_DOMAIN_NAMES if hasattr(domains, n)]
    assert still_there == []
    assert {t.value for t in domains.OptimizerType} == {"nevergrad", "bayesian_ax"}


def test_retired_engine_type_fails_loud_naming_the_retirement():
    from spicexplorer.core.domains import Project_Setup
    from spicexplorer.optimization.orchestrator import optimizer_type_from_config

    setup = Project_Setup.from_yaml(EXAMPLE_YAML)
    setup.optimizer_config.type = "Reinforcement_Learning "
    with pytest.raises(ValueError, match="retired"):
        optimizer_type_from_config(setup)


@pytest.mark.parametrize(
    "spelled",
    [
        "reinforcement_learning",
        "REINFORCEMENT_LEARNING",
        " reinforcement_learning\n",
        "\tReinforcement_Learning ",
    ],
)
def test_retired_engine_message_names_the_value_the_reason_and_the_live_engines(spelled):
    from spicexplorer.core.domains import OptimizerType
    from spicexplorer.optimization.orchestrator import optimizer_type_from_config

    with pytest.raises(ValueError) as info:
        optimizer_type_from_config(_setup_with_type(spelled))
    msg = str(info.value)
    assert "optimizer_config.type='reinforcement_learning' is no longer supported: " in msg
    assert "the RL optimizer backend was retired (owner ruling 2026-09-25)" in msg
    # the message lists every live engine to choose from, never the retired one
    assert msg.endswith(f"choose one of {[t.value for t in OptimizerType]}.")
    assert {"nevergrad", "bayesian_ax"} <= {t.value for t in OptimizerType}
    assert msg.count("reinforcement_learning") == 1
    assert "not a known engine" not in msg


@pytest.mark.parametrize(
    "bad",
    [
        "nope",
        "",
        "   ",
        None,
        "rl",
        "ppo",
        "reinforcement-learning",
        "reinforcement_learning_v2",
        "reinforcement",
    ],
)
def test_an_unknown_engine_is_not_reported_as_retired(bad):
    """Only the exact retired name gets the retirement message; a typo, a near-miss or an empty
    `type:` is still a plain unknown engine (and still a ValueError, never a KeyError)."""
    from spicexplorer.optimization.orchestrator import optimizer_type_from_config

    with pytest.raises(ValueError, match="is not a known engine; choose one of") as info:
        optimizer_type_from_config(_setup_with_type(bad))
    assert "retired" not in str(info.value)
    assert "no longer supported" not in str(info.value)


@pytest.mark.parametrize(
    "spelled, backend", [(" NeverGrad ", "NEVERGRAD_SINGLE"), ("BAYESIAN_AX\n", "AX_SINGLE")]
)
def test_the_live_engines_still_resolve_after_the_retirement(spelled, backend):
    from spicexplorer.optimization.orchestrator import (
        Optimizer_Type_Enum,
        optimizer_type_from_config,
    )

    assert optimizer_type_from_config(_setup_with_type(spelled)) is Optimizer_Type_Enum[backend]


def test_engine_tables_agree():
    """Every live engine has a backend (so no live engine reaches the resolver's "no backend
    wired" branch), no retired name is also a live engine, and the retired table is keyed
    the way the resolver normalizes `type:` (stripped, lower-case)."""
    from spicexplorer.core.domains import OptimizerType
    from spicexplorer.optimization.orchestrator import _ENGINE_TO_OPTIMIZER, _RETIRED_ENGINES

    assert set(_ENGINE_TO_OPTIMIZER) == set(OptimizerType)
    assert "reinforcement_learning" in _RETIRED_ENGINES
    assert not set(_RETIRED_ENGINES) & {t.value for t in OptimizerType}
    assert all(k == k.strip().lower() and _RETIRED_ENGINES[k] for k in _RETIRED_ENGINES)


def test_an_engine_without_a_backend_names_only_the_wired_engines(monkeypatch):
    """The check for an engine added to the DSL before it has a backend. No live engine reaches
    it, so remove one's backend: the message offers only what can run, and no longer blames the
    (now retired) RL backend."""
    from spicexplorer.core.domains import OptimizerType
    from spicexplorer.optimization import orchestrator

    monkeypatch.delitem(orchestrator._ENGINE_TO_OPTIMIZER, OptimizerType.BAYESIAN_AX)
    with pytest.raises(ValueError, match="'bayesian_ax' has no optimizer backend wired; ") as info:
        orchestrator.optimizer_type_from_config(_setup_with_type("bayesian_ax"))
    msg = str(info.value)
    assert msg.endswith("choose one of ['nevergrad'].")
    assert "dormant" not in msg and "RL" not in msg


def test_a_stale_rl_yaml_still_loads_but_the_orchestrator_will_not_run_it(tmp_path):
    """Backwards compatibility of an old project file: it opens (the UI can still show it) and
    raises only where an engine is resolved: at the orchestrator's construction in a script run.
    An explicit `optimizer_type=` still wins over the YAML, as it always did."""
    from spicexplorer.core.domains import Project_Setup
    from spicexplorer.optimization.orchestrator import (
        Circuit_Optimizer_Orchestrator_with_SPICE,
        Optimizer_Type_Enum,
    )

    text = EXAMPLE_YAML.read_text()
    # ws_root set to an absolute path: the example's `..` is relative to the YAML's own directory
    text, n_root = re.subn(
        r"(?m)^([ \t]*ws_root[ \t]*:).*$",
        lambda m: f"{m.group(1)} {EXAMPLE_YAML.parent.parent}",
        text,
        count=1,
    )
    text, n_type = re.subn(
        r"(?m)^([ \t]*type:[ \t]*)nevergrad[ \t]*$", r"\1reinforcement_learning", text
    )
    assert (n_root, n_type) == (1, 1)
    stale = tmp_path / "stale_rl_project.yaml"
    stale.write_text(text)

    setup = Project_Setup.from_yaml(stale)
    assert setup.optimizer_config.type == "reinforcement_learning"
    with pytest.raises(
        ValueError, match="no longer supported: the RL optimizer backend was retired"
    ):
        Circuit_Optimizer_Orchestrator_with_SPICE(stale, auto_load=False)
    explicit = Circuit_Optimizer_Orchestrator_with_SPICE(
        stale, optimizer_type=Optimizer_Type_Enum.NEVERGRAD_SINGLE, auto_load=False
    )
    assert explicit.optimizer_type is Optimizer_Type_Enum.NEVERGRAD_SINGLE


def test_no_shipped_yaml_names_a_retired_engine():
    """Every project YAML the platform ships (examples incl. analog-db, packages, tests) — and the
    orchestration checkout's, when one is beside this one — still names a runnable engine."""
    line = _retired_engine_line()
    roots = [REPO_ROOT / d for d in ("examples", "packages", "tests")]
    orch = _orchestration_root()
    roots += [orch] if orch is not None else []
    hits = []
    for root in (r for r in roots if r.is_dir()):
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
            for name in filenames:
                if name.endswith((".yaml", ".yml")):
                    path = Path(dirpath) / name
                    text = path.read_text(encoding="utf-8", errors="replace")
                    hits += [
                        f"{path}:{text.count(chr(10), 0, m.start()) + 1}"
                        for m in line.finditer(text)
                    ]
    assert hits == [], "shipped YAML still selects a retired engine:\n" + "\n".join(hits)


def test_the_yaml_scan_sees_a_retired_engine_line():
    """Positive control for the scan above (its pattern, not its walk)."""
    line = _retired_engine_line()
    assert line.search("  optimizer_config:\n    type: reinforcement_learning\n")
    assert line.search("    type : 'Reinforcement_Learning'  # old\n")
    assert not line.search("    type: nevergrad\n")
    assert not line.search("    # type: reinforcement_learning was retired\n")


# ── the docs describe it as retired ───────────────────────────────────────────


def test_live_docs_describe_the_retired_code_only_as_retired():
    stale = []
    for rel in LIVE_DOCS:
        path = REPO_ROOT / rel
        if not path.is_file():  # the public tree ships only some of these docs
            continue
        stale += stale_doc_mentions(rel, path.read_text(encoding="utf-8"))
    assert stale == [], "docs still describe retired code as present:\n" + "\n".join(stale)


def test_the_doc_guard_flags_a_stale_mention_and_passes_a_retired_one():
    """Positive + negative control for the doc guard: one block per paragraph, list item and table
    row, so a retired mention elsewhere in the file cannot cover for a stale one."""
    text = (
        "| `rl/` | Dormant RL backend. |\n"
        "| `stochastic/` | Nevergrad; the RL backend was retired. |\n"
        "\n"
        "- the dormant RL\n  optimizer inherits the corner loop\n"
        "- `demo/newcas_demo_runner.py` was deleted and RETIRED\n"
        "\n"
        "> **RL is dormant.** It needs `stable-baselines3`.\n"
        "\n"
        "# The dormant RL agents (optimization/rl) ride on this extra.\n"
        'ax = ["ax-platform"]\n'
        "\n"
        "Enums: `OptimizerType`, `NoiseType`.\n"
        "\n"
        "The netlist has a load resistor RL and a `reinforcement_learning` engine, since retired.\n"
        "| `src/spicexplorer/demo/newcas_demo_runner.py:22` | parents[3] |\n"
    )
    flagged = [s.split(":")[1] for s in stale_doc_mentions("doc/root_anchoring.md", text)]
    assert flagged == ["1", "4", "8", "10", "13"]
    # the history-row exemption is per document
    assert [s.split(":")[1] for s in stale_doc_mentions("README.md", text)][-1] == "16"
