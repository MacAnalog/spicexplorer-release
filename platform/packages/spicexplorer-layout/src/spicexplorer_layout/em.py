"""Full-wave EM verification of extracted layouts (openEMS lane).

The signoff flow's PEX (kpex 2.5D) charges wiring with capacitance only; this
module is the *verification* counterpart that re-derives a net's multiport
S-parameters from FDTD and turns them into a SPICE subcircuit the block's own
benches can splice in. It is a lane for checking a claim (reflection at a band
edge, a balance figure), **never a stage inside an optimizer loop** — one
excitation per port at sub-µm mesh costs minutes to hours.

The module is PDK-agnostic: every process-specific number (metal/via GDS
layers, the via stack order, the substrate-contact layer, the openEMS
workflow location) lives in an :class:`EmTech` config — loaded from a YAML
file the caller owns (``EmTech.from_yaml``) or from the configs packaged
under ``spicexplorer_layout/techs/`` (``EmTech.builtin("ihp-sg13g2")``;
``builtin_techs()`` lists them). The platform carries only the logic.

Three seams, all optional-import so the package stays light:

* :func:`extract_net_gds` — cut named nets out of a signed-off GDS
  (KLayout ``LayoutToNetlist``, metal-only connectivity, labels name the
  nets) into an EM-ready GDS + port rectangles.  Needs ``klayout``
  (the ``gds`` extra).
* :func:`em_sparams` — run the PDK's own openEMS workflow on such a GDS →
  touchstone.  Needs the openEMS python bindings (see :data:`OPENEMS_RECIPE`
  — there is no wheel, it is a from-source build) and a PDK that ships an
  openEMS workflow (``EmTech.workflow``).
* :func:`em_to_subckt` — touchstone → passivity-enforced vector fit →
  ngspice ``.subckt`` with per-port reference pins.  Needs ``scikit-rf``.
  ``dc_r`` anchors the fit at f≈0 with the net's DC resistances: benches
  push bias current through these nets, and a fit that is wrong at DC
  shifts every operating point while producing plausible S-curves — after
  splicing, always compare ``.op`` against the PEX deck first.

Port spec — a list of dicts (the schema a caller's ``ports.yaml``
serializes)::

    {num: 1, kind: "via",     rect: [x1,y1,x2,y2], from_layer: "Metal1",
     to_layer: "TopMetal1", direction: "z", z0: 50, subgnd: False}
    {num: 2, kind: "inplane", rect: [...], layer: "Metal1", direction: "x"}

``rect`` is µm; the port polygon lands on GDS layer
``tech.port_layer_base + num`` (which must stay clear of every stackup
layer — the workflow treats a polygon as a port only when its layer is
absent from the stackup); ``subgnd`` additionally draws the rect on
``tech.subgnd_layer`` (an idealized substrate contact) for short vertical
device-tap ports.
"""
from __future__ import annotations

import dataclasses
import logging
import os
from typing import Any, Sequence

log = logging.getLogger(__name__)

#: How to get the solver. openEMS has no wheel; either build it from source
#: or use the platform's container image (``docker/Dockerfile.em``, compose
#: profile ``em``), which bakes the same toolchain plus the PDK workflow.
OPENEMS_RECIPE = """openEMS must be built from source (no wheel exists):

  conda create -p <env> -c conda-forge python=3.11 cmake compilers \\
      boost-cpp hdf5 vtk 'cgal-cpp=5.6' tinyxml cython numpy h5py \\
      matplotlib gdspy pyyaml scikit-rf          # CGAL 6 breaks CSXCAD
  git clone --recursive https://github.com/thliebig/openEMS-Project.git
  cd openEMS-Project
  CMAKE_PREFIX_PATH=<env> CXXFLAGS=-fpermissive \\
      ./update_openEMS.sh <prefix> --python      # QCSXCAD/Qt failure is OK
  CSXCAD_INSTALL_PATH=<prefix> <env>/bin/pip install --no-build-isolation \\
      ./CSXCAD/python ./openEMS/python
  export LD_LIBRARY_PATH=<prefix>/lib:<env>/lib  # at run time

Or use the container: docker compose --profile em build em."""


def _build(cls, d: dict, source: str, overrides: dict):
    """Shared loud constructor: unknown keys are errors, ``overrides`` (from
    the caller, e.g. CLI flags) beat the file, and every field that silently
    falls back to its dataclass default is reported."""
    names = {f.name for f in dataclasses.fields(cls)}
    unknown = set(d) - names
    if unknown:
        raise ValueError(f"{cls.__name__}({source}): unknown keys {sorted(unknown)}; "
                         f"valid: {sorted(names)}")
    if overrides:
        bad = set(overrides) - names
        if bad:
            raise ValueError(f"{cls.__name__} overrides: unknown keys {sorted(bad)}")
        log.info("%s(%s): caller overrides %s", cls.__name__, source,
                 {k: overrides[k] for k in sorted(overrides)})
        d = {**d, **overrides}
    inst = cls(**d)
    defaulted = sorted(names - set(d))
    if defaulted:
        log.warning("%s(%s): using DEFAULTS for %s", cls.__name__, source,
                    {k: getattr(inst, k) for k in defaulted})
    return inst


@dataclasses.dataclass(frozen=True)
class EmTech:
    """Process description for the EM lane — all PDK specifics live here.

    ``metals``/``vias`` map layer name → GDS layer number (the numbers the
    PDK's openEMS stackup XML uses); ``via_stack`` maps each via layer to
    the (metal below, metal above) it connects. ``workflow`` is the PDK's
    openEMS workflow directory (absolute, or relative to ``$PDK_ROOT``);
    ``stackup_xml`` the stackup file (absolute, or relative to workflow)."""

    metals: dict[str, int]
    vias: dict[str, int]
    via_stack: dict[str, tuple[str, str]]
    subgnd_layer: int | None = None
    gnd_contact_layers: tuple[int, ...] = ()
    port_layer_base: int = 300
    text_datatype: int = 25
    workflow: str | None = None
    stackup_xml: str | None = None

    @classmethod
    def from_yaml(cls, path: str, **overrides: Any) -> "EmTech":
        """Load from YAML; ``overrides`` (field=value) beat the file. Fields
        neither in the file nor overridden fall back to the dataclass
        defaults — LOUDLY (logged at WARNING)."""
        import yaml

        d = yaml.safe_load(open(path))
        d = d.get("tech", d)        # combined {tech:, sim:} files work too
        if "via_stack" in d:
            d["via_stack"] = {k: tuple(v) for k, v in d["via_stack"].items()}
        return _build(cls, d, path, overrides)

    @classmethod
    def builtin(cls, name: str, **overrides: Any) -> "EmTech":
        """Load a tech config packaged with this module (``techs/<name>.yaml``);
        ``overrides`` behave as in :meth:`from_yaml`."""
        from importlib.resources import files

        p = files("spicexplorer_layout") / "techs" / f"{name}.yaml"
        if not p.is_file():
            raise ValueError(f"no builtin EM tech {name!r}; "
                             f"available: {builtin_techs()}")
        return cls.from_yaml(str(p), **overrides)

    def workflow_dir(self, pdk_root: str | None = None) -> str:
        if not self.workflow:
            raise ValueError("EmTech.workflow not set — this tech config has "
                             "no openEMS workflow location")
        wf = self.workflow
        if not os.path.isabs(wf):
            root = pdk_root or os.environ.get("PDK_ROOT",
                                              os.path.expanduser("~/local/pdks"))
            wf = os.path.join(root, wf)
        if not os.path.isdir(wf):
            raise FileNotFoundError(
                f"PDK openEMS workflow not found at {wf} (set PDK_ROOT or use "
                f"an absolute EmTech.workflow)")
        return wf

    def stackup_path(self, pdk_root: str | None = None) -> str:
        if not self.stackup_xml:
            raise ValueError("EmTech.stackup_xml not set")
        if os.path.isabs(self.stackup_xml):
            return self.stackup_xml
        return os.path.join(self.workflow_dir(pdk_root), self.stackup_xml)


def builtin_techs() -> list[str]:
    """Names accepted by :meth:`EmTech.builtin`."""
    from importlib.resources import files

    d = files("spicexplorer_layout") / "techs"
    return sorted(f.name[:-5] for f in d.iterdir() if f.name.endswith(".yaml"))


@dataclasses.dataclass(frozen=True)
class EmSim:
    """Solver hyperparameters for one :func:`em_sparams` run — everything a
    rerun needs to reproduce the sim, YAML-loadable so the setup can be
    committed next to its results. ``cellsize_um`` is the refined mesh cell
    in conductor regions (never coarser than the thinnest trace);
    ``energy_limit_db`` the FDTD end criterion; ``boundary`` the six openEMS
    boundary conditions (xmin,xmax,ymin,ymax,zmin,zmax); ``excite_ports``
    restricts the excitation loop (default: every port)."""

    fstart: float = 0.0
    fstop: float = 60e9
    numfreq: int = 241
    cellsize_um: float = 0.5
    margin_um: float = 50.0
    energy_limit_db: float = -40.0
    boundary: tuple[str, ...] = ("PEC",) * 6
    excite_ports: tuple[int, ...] | None = None

    @classmethod
    def from_yaml(cls, path: str, **overrides: Any) -> "EmSim":
        """Load from YAML; ``overrides`` (field=value, e.g. from CLI flags)
        beat the file. Fields neither in the file nor overridden fall back
        to the dataclass defaults — LOUDLY (logged at WARNING)."""
        import yaml

        d = yaml.safe_load(open(path))
        d = d.get("sim", d)         # combined {tech:, sim:} files work too
        if overrides:
            log.info("EmSim(%s): caller overrides %s", path, overrides)
            d = {**d, **overrides}
        for k in ("boundary", "excite_ports"):
            if d.get(k) is not None:
                d[k] = tuple(d[k])
        for k in ("fstart", "fstop", "cellsize_um", "margin_um",
                  "energy_limit_db"):
            if k in d:
                d[k] = float(d[k])
        return _build(cls, d, path, {})


def extract_net_gds(gds: str, nets: Sequence[str], out_gds: str,
                    ports: Sequence[dict[str, Any]] | None = None, *,
                    tech: EmTech, via_bar_min_um: float | None = 0.55,
                    gnd_nets: Sequence[str] = (),
                    gnd_plane: bool | None = None) -> dict[str, Any]:
    """Trace metal-only connectivity, select ``nets`` by label, write their
    polygons (native layer numbers) + port rectangles to ``out_gds``.
    Returns a manifest ``{nets: {name: [layers]}, ports: [...]}``.

    Ground scheme (``gnd_plane``, default on when ``tech.subgnd_layer`` is
    set): ONE common substrate-contact plane under the whole cut — the same
    single-ground idealization a lumped bench makes — plus contact columns
    (``tech.gnd_contact_layers``, e.g. Activ+Cont) tying each ``gnd_nets``
    net's lowest metal down to it. Without a common reference the ports
    couple only through the lossy substrate and the S-matrix goes open
    below a few GHz, which no DC anchor can reconcile.

    ``via_bar_min_um``: merge each via-cut array into its solid envelope
    bar with at least this side length (None disables). PDK via cuts are
    typically smaller than the FDTD mesh cell, and a via column with no
    interior grid line simply does not conduct — solid bars are the
    standard EM idealization of via arrays and are mesh-robust."""
    import klayout.db as kdb

    def via_bars(region, dbu: float) -> "kdb.Region":
        grow = int(0.35 / dbu)          # joins cuts across the array pitch
        r = region.sized(grow)
        r.merge()
        out = kdb.Region()
        half = int(via_bar_min_um / 2 / dbu)
        for poly in r.each_merged():
            b = poly.bbox()
            bb = kdb.Box(b.left + grow, b.bottom + grow,
                         b.right - grow, b.top - grow)
            cx, cy = bb.center().x, bb.center().y
            w2 = max((bb.right - bb.left) // 2, half)
            h2 = max((bb.top - bb.bottom) // 2, half)
            out.insert(kdb.Box(cx - w2, cy - h2, cx + w2, cy + h2))
        return out

    ly = kdb.Layout()
    ly.read(gds)
    top = ly.top_cell()
    l2n = kdb.LayoutToNetlist(kdb.RecursiveShapeIterator(ly, top, []))
    regions: dict[str, Any] = {}
    for name, ln in {**tech.metals, **tech.vias}.items():
        regions[name] = l2n.make_polygon_layer(ly.layer(ln, 0), name)
    for name, ln in tech.metals.items():
        t = l2n.make_text_layer(ly.layer(ln, tech.text_datatype), name + "_txt")
        l2n.connect(regions[name])
        l2n.connect(regions[name], t)
    for via, (below, above) in tech.via_stack.items():
        l2n.connect(regions[via])
        l2n.connect(regions[below], regions[via])
        l2n.connect(regions[via], regions[above])
    l2n.extract_netlist()

    circuit = l2n.netlist().circuit_by_name(top.name)
    out_ly = kdb.Layout()
    out_ly.dbu = ly.dbu
    out_top = out_ly.create_cell("em_cut")
    manifest: dict[str, Any] = {"source_gds": os.path.abspath(gds),
                                "nets": {}, "ports": list(ports or [])}
    for netname in nets:
        net = circuit.net_by_name(netname)
        if net is None:
            names = sorted(n.name for n in circuit.each_net() if n.name)
            raise ValueError(f"net {netname!r} not found; labelled nets: {names}")
        found = []
        for lname in list(tech.metals) + list(tech.vias):
            r = l2n.shapes_of_net(net, regions[lname], True)
            if not r.is_empty():
                found.append(lname)
                if lname in tech.vias and via_bar_min_um:
                    r = via_bars(r, ly.dbu)
                out_top.shapes(
                    out_ly.layer((tech.metals | tech.vias)[lname], 0)).insert(r)
        manifest["nets"][netname] = found
    if gnd_plane is None:
        gnd_plane = tech.subgnd_layer is not None
    if gnd_nets:
        low_metal = min(tech.metals, key=tech.metals.get)
        for netname in gnd_nets:
            net = circuit.net_by_name(netname)
            if net is None:
                raise ValueError(f"gnd net {netname!r} not found")
            r = l2n.shapes_of_net(net, regions[low_metal], True)
            for layer_num in tech.gnd_contact_layers:
                out_top.shapes(out_ly.layer(layer_num, 0)).insert(r)
    if gnd_plane:
        if tech.subgnd_layer is None:
            raise ValueError("gnd_plane requires tech.subgnd_layer")
        bb = out_top.dbbox()
        plane = kdb.DBox(bb.left - 5, bb.bottom - 5, bb.right + 5, bb.top + 5)
        out_top.shapes(out_ly.layer(tech.subgnd_layer, 0)).insert(plane)
    for p in ports or []:
        x1, y1, x2, y2 = p["rect"]
        box = kdb.DBox(x1, y1, x2, y2)
        out_top.shapes(
            out_ly.layer(tech.port_layer_base + p["num"], 0)).insert(box)
    out_ly.write(out_gds)
    return manifest


def em_sparams(gds: str, ports: Sequence[dict[str, Any]], out_dir: str, *,
               tech: EmTech, sim: EmSim | None = None,
               pdk_root: str | None = None,
               stackup_xml: str | None = None) -> str:
    """FDTD multiport S-parameters of an EM-cut GDS through the PDK's own
    openEMS workflow. One excitation per port; returns the touchstone path.
    ``sim`` carries every solver hyperparameter (:class:`EmSim`; default
    constructed, or load a committed setup with ``EmSim.from_yaml``).

    Raises ImportError with the build recipe pointer when the openEMS python
    bindings are absent (they are a from-source install, never a wheel)."""
    import sys

    import numpy as np

    if sim is None:
        sim = EmSim()
        log.warning("em_sparams: no EmSim given — running with ALL defaults: %s",
                    dataclasses.asdict(sim))

    wf = tech.workflow_dir(pdk_root)
    sys.path.insert(0, wf)
    sys.path.insert(0, os.path.join(wf, "modules"))
    try:
        from openEMS import openEMS
    except ImportError as e:
        raise ImportError(
            "openEMS python bindings not importable.\n" + OPENEMS_RECIPE) from e
    import modules.util_gds_reader as gds_reader
    import modules.util_meshlines as util_meshlines
    import modules.util_simulation_setup as simulation_setup
    import modules.util_stackup_reader as stackup_reader
    import modules.util_utilities as utilities

    simulation_setup.AppCSXCAD_BIN = "true"     # headless: no GUI viewer
    simulation_setup.sys = sys

    os.makedirs(out_dir, exist_ok=True)
    sim_ports = simulation_setup.all_simulation_ports()
    for p in ports:
        ln = tech.port_layer_base + p["num"]
        if p["kind"] == "via":
            sp = simulation_setup.simulation_port(
                portnumber=p["num"], voltage=1, port_Z0=p.get("z0", 50),
                source_layernum=ln, from_layername=p["from_layer"],
                to_layername=p["to_layer"], direction=p.get("direction", "z"))
        else:
            sp = simulation_setup.simulation_port(
                portnumber=p["num"], voltage=1, port_Z0=p.get("z0", 50),
                source_layernum=ln, target_layername=p["layer"],
                direction=p["direction"])
        sim_ports.add_port(sp)

    xml = stackup_xml or tech.stackup_path(pdk_root)
    materials, dielectrics, metals_l = stackup_reader.read_substrate(xml)
    # the workflow treats a polygon as a port ONLY if its layer is absent from
    # the stackup; a collision silently swallows the port rect as metal and
    # that port's excitation run never injects any energy
    for sp_ in sim_ports.ports:
        clash = metals_l.getbylayernumber(sp_.source_layernum)
        if clash is not None:
            raise ValueError(
                f"port {sp_.portnumber}: source layer {sp_.source_layernum} is "
                f"stackup layer {getattr(clash, 'name', clash)} — ports must "
                "not share a GDS layer with the stackup")
    layernumbers = metals_l.getlayernumbers()
    layernumbers.extend(sim_ports.portlayers)
    polys = gds_reader.read_gds(gds, layernumbers, purposelist=[0],
                                metals_list=metals_l, preprocess=False,
                                merge_polygon_size=0)
    unit = 1e-6
    max_cell = (3e8 / sim.fstop / unit) / (np.sqrt(materials.eps_max) * 20)
    basename = os.path.splitext(os.path.basename(gds))[0]
    for pnum in (sim.excite_ports or [p.portnumber for p in sim_ports.ports]):
        fdtd = openEMS(EndCriteria=np.exp(sim.energy_limit_db / 10 * np.log(10)))
        fdtd.SetGaussExcite((sim.fstart + sim.fstop) / 2,
                            (sim.fstop - sim.fstart) / 2)
        fdtd.SetBoundaryCond(list(sim.boundary))
        simulation_setup.setupSimulation(
            [pnum], sim_ports, fdtd, materials, dielectrics, metals_l, polys,
            max_cell, sim.cellsize_um, sim.margin_um, unit,
            xy_mesh_function=util_meshlines.create_xy_mesh_from_polygons)
        simulation_setup.runSimulation([pnum], fdtd, os.path.abspath(out_dir),
                                       basename, False, False)
    n = sim_ports.portcount
    f = np.linspace(sim.fstart, sim.fstop, sim.numfreq)
    s = np.empty((n, n, sim.numfreq), dtype=object)
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            s[i - 1, j - 1] = utilities.calculate_Sij(i, j, f, os.path.abspath(out_dir), sim_ports)
    snp = os.path.join(out_dir, f"{basename}.s{n}p")
    utilities.write_snp(s, f, snp)
    return snp


def em_to_subckt(touchstone: str, out_path: str, *, name: str = "em_net",
                 n_poles: int = 12, f_dc: float = 1e6,
                 dc_r: dict[tuple[int, int], float] | None = None,
                 dc_from_data: bool = False) -> str:
    """Touchstone → passivity-enforced vector fit → ngspice subckt (with
    per-port reference pins). ``dc_r`` = {(port_i, port_j) 1-based: ohms}
    anchors the fit at f≈0 with that resistive graph (ports in no pair are
    DC-open): raw points below ``f_dc`` are dropped — a Gauss excitation has
    ~no DC energy, so the FDTD's own f→0 samples are numerically meaningless
    — and replaced by one exact sample at ``f_dc``. ``dc_from_data``
    instead anchors with the conductance graph Re(Y) at the lowest kept
    frequency — valid once the EM cut has a common ground plane so its
    low-f limit is resistive; a spliced-deck ``.op`` vs the PEX deck stays
    the independent gate either way."""
    import numpy as np
    import skrf
    from skrf.vectorFitting import VectorFitting

    nw = skrf.Network(touchstone)
    # FDTD numerical noise leaves ~1e-4 passivity violations scattered over
    # the band; renormalize onto a small margin INSIDE the unit sphere so
    # the (tiny) fit error has headroom to stay passive — enforcement alone
    # cannot always absorb boundary-hugging data
    margin = 2e-4
    sv = np.linalg.svd(nw.s, compute_uv=False).max(axis=1)
    hot = sv > 1.0 - margin
    if hot.any():
        nw.s[hot] *= ((1.0 - margin) / sv[hot])[:, None, None]
    if dc_from_data:
        keep = nw.f > f_dc
        k = int(np.argmax(keep))
        # strictly-PSD conductance graph: symmetrize and clip the (numerical
        # noise) negative eigenvalues, so the anchor itself is passive
        g = nw.y[k].real
        g = 0.5 * (g + g.T)
        w, v = np.linalg.eigh(g)
        g = (v * np.clip(w, 0.0, None)) @ v.T
        eye = np.eye(nw.nports)
        z0 = nw.z0[0, 0].real
        s0 = (1.0 - margin) * np.linalg.solve(eye + z0 * g, eye - z0 * g)
        # several anchor samples across the gap up to the first real data
        # point: the network's measured low-f limit is frequency-flat, and
        # an unconstrained two-decade gap lets the fit drift non-passive
        f0 = nw.f[keep][0]
        fa = [f_dc / 1000, f_dc / 100, f_dc / 10, f_dc]
        while fa[-1] * 3 < f0:
            fa.append(fa[-1] * 3)
        nw = skrf.Network(f=np.concatenate([fa, nw.f[keep]]),
                          s=np.concatenate([np.repeat(s0[None], len(fa), 0),
                                            nw.s[keep]], axis=0),
                          z0=z0, f_unit="hz")
    elif dc_r:
        n = nw.nports
        z0 = nw.z0[0, 0].real
        g = np.zeros((n, n))
        for (i, j), r in dc_r.items():
            gij = 1.0 / max(r, 1e-3)
            i, j = i - 1, j - 1
            g[i, i] += gij
            g[j, j] += gij
            g[i, j] -= gij
            g[j, i] -= gij
        eye = np.eye(n)
        s0 = np.linalg.solve(eye + z0 * g, eye - z0 * g)
        keep = nw.f > f_dc
        nw = skrf.Network(f=np.concatenate([[f_dc], nw.f[keep]]),
                          s=np.concatenate([s0[None], nw.s[keep]], axis=0),
                          z0=z0, f_unit="hz")
    # near-noise fits flip in and out of (microscopic) passivity violations
    # depending on the pole split — walk a small ladder and keep the first
    # passive (or enforceable) fit
    vf = None
    tried = []
    for nr, ncx in ((2, n_poles), (1, n_poles), (2, n_poles + 2), (1, max(1, n_poles - 1))):
        import copy

        cand = VectorFitting(nw)
        cand.vector_fit(n_poles_real=nr, n_poles_cmplx=ncx)
        rms = cand.get_rms_error()
        pristine = copy.deepcopy(cand)   # a failed enforce corrupts the model
        if not cand.is_passive():
            try:
                cand.passivity_enforce()
            except Exception as e:
                log.info("em_to_subckt (%d,%d): rms %.3e, enforce failed: %s",
                         nr, ncx, rms, e)
                tried.append((rms, nr, ncx, pristine))
                continue
        if cand.is_passive():
            vf = cand
            log.info("em_to_subckt: %d real + %d cplx poles, passive, rms %.3e",
                     nr, ncx, cand.get_rms_error())
            break
        tried.append((rms, nr, ncx, pristine))
        log.info("em_to_subckt (%d,%d): rms %.3e, still non-passive", nr, ncx, rms)
    if vf is None and tried:
        # tolerance fallback: a fit whose worst sampled singular value is
        # within sv_tol of the boundary is numerically indistinguishable
        # from passive for AC/OP use — accept the best one, LOUDLY, rather
        # than dead-ending on a 1e-4 excursion in a data-free band
        sv_tol = 1e-3
        fgrid = np.linspace(0, 1.2 * nw.f[-1], 400)
        rms, nr, ncx, cand = sorted(tried, key=lambda t: t[0])[0]
        n = nw.nports
        sm = np.empty((len(fgrid), n, n), dtype=complex)
        for i in range(n):
            for j in range(n):
                sm[:, i, j] = cand.get_model_response(i, j, fgrid)
        worst = float(np.linalg.svd(sm, compute_uv=False).max())
        if worst < 1.0 + sv_tol:
            log.warning("em_to_subckt: accepting NEAR-passive fit (%d,%d): "
                        "rms %.3e, worst sampled sv %.6f (tol %g) — validate "
                        "the spliced deck's .op against the PEX deck", nr, ncx,
                        rms, worst, sv_tol)
            vf = cand
        else:
            raise RuntimeError(
                f"vector fit not passive at any pole count (best worst-sv {worst:.4f})")
    if vf is None:
        raise RuntimeError("vector fit could not be made passive at any tried pole count")
    vf.write_spice_subcircuit_s(out_path, fitted_model_name=name,
                                create_reference_pins=True)
    _rescale_states(out_path)
    return out_path


def _rescale_states(path: str, k: float = 1e9) -> None:
    """Rescale the exported state-space realization for SPICE robustness.

    skrf's export integrates each state on a 1 F cap with a pole resistor
    R = 1/|pole| — sub-picoohm for the fast poles — and output gains up to
    ~1e12. ngspice clamps R below 1e-12 (silently moving those poles) and
    the resulting conductance spread makes even the DC solve singular.
    Scaling every state by ``k`` (R*k, C/k, and any source CONTROLLED BY a
    state /k) leaves all poles and port responses identical while bringing
    the element values into SPICE-friendly ranges."""
    out = []
    for ln in open(path):
        t = ln.split()
        if t and t[0][0] in "CRGF" and len(t) >= 4:
            if t[0].startswith("C") and t[1].startswith("x"):
                t[-1] = repr(float(t[-1]) / k)
                ln = " ".join(t) + "\n"
            elif t[0].startswith("R") and t[2].startswith("x"):
                t[-1] = repr(float(t[-1]) * k)
                ln = " ".join(t) + "\n"
            elif t[0].startswith("G") and t[3].startswith("x"):
                t[-1] = repr(float(t[-1]) / k)
                ln = " ".join(t) + "\n"
        out.append(ln)
    with open(path, "w") as f:
        f.write("".join(out))
