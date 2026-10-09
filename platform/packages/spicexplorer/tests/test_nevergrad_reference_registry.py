"""examples/nevergrad_reference_registry.yaml lists only names the platform can build.

The file is the reference a user copies ``optimizer_config.name`` from. A name nevergrad does not
hold, or one whose package is not in ``uv.lock``, fails the run at start-up with the platform's
"not found" error, so every listed name is built here through ``create_optimizer`` and asked for
one point. A name whose package comes from a platform extra (``EXTRA_BACKED``) is built where that
extra is installed, and skipped with the reason where it is not.
"""

from __future__ import annotations

import importlib.util
import re
import warnings
from pathlib import Path

import pytest

ng = pytest.importorskip("nevergrad")
yaml = pytest.importorskip("yaml")

from spicexplorer.optimization.stochastic.nevergrad import create_optimizer  # noqa: E402

REFERENCE = Path(__file__).resolve().parents[3] / "examples" / "nevergrad_reference_registry.yaml"
PYPROJECT = Path(__file__).resolve().parents[1] / "pyproject.toml"

#: listed name -> (the module it imports, the platform extra that installs it, that extra's package)
EXTRA_BACKED = {"AXP": ("ax", "ax", "ax-platform")}


def _missing_extra(name: str) -> str | None:
    """The skip reason when ``name`` needs an extra that is not installed here, else None."""
    if name not in EXTRA_BACKED:
        return None
    module, extra, _package = EXTRA_BACKED[name]
    if importlib.util.find_spec(module) is not None:
        return None
    return f"{name} needs the `{extra}` extra (`uv sync --extra {extra}`); `{module}` is not installed here"


def _space():
    return ng.p.Dict(x=ng.p.Scalar(lower=0.0, upper=1.0), y=ng.p.Scalar(lower=0.0, upper=1.0))


def _listed_names() -> list[str]:
    names: list[str] = []

    def walk(node: object) -> None:
        if isinstance(node, dict):
            for value in node.values():
                walk(value)
        elif isinstance(node, list):
            for value in node:
                walk(value)
        elif isinstance(node, str):
            names.extend(n for n in re.split(r"\s*,\s*", node.strip()) if n)

    walk(yaml.safe_load(REFERENCE.read_text()))
    return names


NAMES = _listed_names()


def test_the_reference_lists_names():
    assert len(NAMES) > 50, NAMES


@pytest.mark.parametrize("name", NAMES)
def test_every_listed_name_builds_and_asks_one_point(name):
    reason = _missing_extra(name)
    if reason:
        pytest.skip(reason)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        opt = create_optimizer(name, _space(), budget=8, random_seed=0)
        candidate = opt.ask()
    assert set(candidate.value) == {"x", "y"}


UV_LOCK = REFERENCE.parents[1] / "uv.lock"


def _locked() -> dict[str, str]:
    """Package name -> version, as ``uv.lock`` records them."""
    if not UV_LOCK.is_file():  # the public tree ships no lock file
        pytest.skip("no uv.lock in this tree")
    pairs = re.findall(
        r'^\[\[package\]\]\nname = "([^"]+)"\nversion = "([^"]+)"', UV_LOCK.read_text(), re.M
    )
    return dict(pairs)


def test_every_extra_backed_name_is_listed_and_marked_with_its_extra():
    """Each ``EXTRA_BACKED`` name is listed, its YAML line says which extra it needs, that extra is
    declared in ``pyproject.toml`` with the package, and ``uv.lock`` holds the package. No other
    line carries the mark, so a newly marked name cannot skip without an entry here."""
    lines = REFERENCE.read_text().splitlines()
    rows = {m.group(1): ln for ln in lines if (m := re.match(r"\s*-\s*(\w+)\s", ln))}
    marked = {name for name, ln in rows.items() if "needs the `" in ln}
    assert marked == set(EXTRA_BACKED), marked
    tomllib = pytest.importorskip("tomllib")  # Python 3.11+; the package supports 3.10
    extras = tomllib.loads(PYPROJECT.read_text())["project"]["optional-dependencies"]
    locked = _locked()
    for name, (_module, extra, package) in EXTRA_BACKED.items():
        assert name in NAMES, name
        assert f"needs the `{extra}` extra" in rows[name], rows[name]
        assert any(dep.startswith(package) for dep in extras.get(extra, [])), (extra, package)
        assert package in locked, package


def test_the_header_gives_the_real_reason_each_left_out_name_is_left_out():
    """FCMA / BayesOptim / PCABO need a package ``uv.lock`` does not hold. AX fails although
    ax-platform IS locked, because nevergrad's AX imports ``ax.optimize`` and that version has none.
    The header must say which, and name the locked version, so a relock shows up here."""
    comment = [ln.lstrip("#") for ln in REFERENCE.read_text().splitlines() if ln.startswith("#")]
    header = " ".join(" ".join(comment).split())
    locked = _locked()
    assert "nevergrad" in locked  # the lock parses

    unlocked = re.search(r"package is not in uv\.lock \(([^)]*)\)", header)
    assert unlocked, header
    packages = re.findall(r":\s*([\w-]+)", unlocked.group(1))
    assert packages == ["fcmaes", "bayes_optim"]
    for pkg in packages:
        assert pkg.replace("_", "-").lower() not in locked, pkg

    ax = re.search(
        r"AX \(nevergrad's AX imports ax\.optimize, which the locked ax-platform ([\w.]+) does not have",
        header,
    )
    assert ax, header
    assert locked.get("ax-platform") == ax.group(1)


def test_ax_still_fails_with_the_ax_extra_installed():
    """The header's reason for leaving AX out, checked where it can be: with the ``ax`` extra
    installed, building AX and asking it for a point fails on the ``ax.optimize`` import. nevergrad
    runs AX in a thread and may re-raise that ImportError as the cause of a RuntimeError, so the
    whole cause chain is read. If a relock provides ``ax.optimize``, this fails and AX can be listed
    again."""
    if importlib.util.find_spec("ax") is None:
        pytest.skip(
            "AX is checked only where the `ax` extra is installed (`uv sync --extra ax`); "
            "`ax` is not installed here"
        )
    with warnings.catch_warnings(), pytest.raises((ImportError, RuntimeError)) as caught:
        warnings.simplefilter("ignore")
        create_optimizer("AX", _space(), budget=8, random_seed=0).ask()
    chain: list[BaseException] = []
    exc: BaseException | None = caught.value
    while exc is not None:
        chain.append(exc)
        exc = exc.__cause__
    assert any(isinstance(e, ImportError) and "optimize" in str(e) for e in chain), chain
