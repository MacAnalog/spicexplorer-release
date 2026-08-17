# IHP sg13g2 layout toolchain — setup & installation

How the open-source IHP `sg13g2` layout toolchain was stood up on **srv-elamien** (RHEL 8.10,
glibc 2.28, **no root**). This is a record + reproduction guide; the exact build recipes with
every host-specific fix live in two on-machine notes referenced below.

None of the prebuilt EDA binaries from the shared OSIC bundle run here (they need glibc ≥2.34),
so each tool is either a conda-forge package, a no-root rpm-extraction, or a from-source build,
all under `~/local`.

## What gets installed, and why two KLayouts

| Tool | Purpose | How | Lives in |
|---|---|---|---|
| IHP **PDK** | devices, DRC/LVS decks, PyCells, layer map | git clone / unpack | `~/local/pdks/ihp-sg13g2` |
| Python env **`ai_env`** | `klayout` module, `gdsfactory`, drives PyCells | conda (py3.11) | `~/miniconda3/envs/ai_env` |
| **KLayout (batch)** | run the Ruby DRC/LVS decks headless | rpm-extraction shim around the portable 0.30.5 (py3.6) | `~/local/klayout-runtime` |
| **KLayout (GUI)** | interactive editing **with live PyCells** | built from source vs py3.11 | `~/local/klayout-py311` |
| **magic** | Magic DRC + layout extraction | conda-forge `magic` 8.3.486 (env `eda`) | `~/miniconda3/envs/eda` |
| **netgen** | LVS netlist comparison | built from source 1.5.99 | `~/local/netgen` |
| GL shim | OpenGL libs+headers for the KLayout build/GUI | rpm-extraction + symlinks | `~/local/gl-link` |
| **ihp-gdsfactory** | gdsfactory IHP PDK (device cells with ports) | pip 0.2.7 into `ai_env` | `~/miniconda3/envs/ai_env` |
| Python env **`pex`** | `klayout-pex` (kpex) parasitic extraction | conda (py3.12) + pip | `~/miniconda3/envs/pex` |

**Why two KLayouts:** the portable KLayout embeds **Python 3.6**, but the IHP PyCells need
**≥3.11** (`StrEnum`, `from __future__ import annotations`). The batch shim (py3.6) is fine for
the Ruby DRC/LVS decks; the source build (py3.11) is what makes PyCells work in the GUI.

## Prerequisites

- RHEL8 with `dnf` reachable as non-root (BaseOS/AppStream/EPEL) — used to *download* rpms
  (`dnf download`), which are then extracted with `rpm2cpio | cpio` (no install, no root).
- Miniconda/conda.
- Network access to github + opencircuitdesign.com (for source tarballs).
- `~/local/bin` on `PATH` (holds the `klayout`, `magic`, `netgen` wrappers).

## 1. IHP PDK

Place the IHP `ihp-sg13g2` PDK at `$PDK_ROOT/ihp-sg13g2` (here `PDK_ROOT=~/local/pdks`). It
ships everything under `libs.tech/`: `klayout/` (DRC+LVS decks, PyCells, `sg13g2.lyp`),
`magic/`, `netgen/`, `ngspice/`.

## 2. Python env (`ai_env`, conda, Python 3.11)

```bash
pip install klayout gdsfactory graphviz      # klayout module 0.30.5, gdsfactory 9.25.2
```
The IHP PyCells are imported by adding two dirs to `sys.path` (done automatically by
`5t_ota/pdk.py`): `libs.tech/klayout/python` and `.../python/pycell4klayout-api/source/python`.
`ai_env` also carries the **Qt 5.15 / Python 3.11 / Ruby 2.7** used to build KLayout and netgen.

## 3. KLayout — batch DRC/LVS shim (`~/local/klayout-runtime`)

The portable KLayout 0.30.5 wouldn't start (`libgit2.so.26` missing). Fix: `dnf download` the
stock RHEL8 rpms (Qt5, libgit2, ruby-libs, rubygems, rubygem-json, …), extract into
`~/local/klayout-runtime/root`, and wrap the binary with the right `LD_LIBRARY_PATH` /
`RUBYLIB` / `GEM_PATH` / `QT_PLUGIN_PATH`. `~/local/bin/klayout` → that wrapper.
**Full package list + wrapper: `~/local/klayout-runtime/SETUP.md`.**

## 4. KLayout — GUI build with live PyCells (`~/local/klayout-py311`)

Built KLayout 0.30.5 from source (github tag `v0.30.5`) against `ai_env`'s Qt5.15 + Python 3.11
+ Ruby 2.7, so the embedded interpreter is 3.11 and the PyCells load. Host-specific fixes
(missing OpenGL dev bits on RHEL8) go through `~/local/gl-link`. GUI launcher:
`~/local/klayout-py311/klayout-gui.sh` (sets `QT_QPA_PLATFORM=xcb`, needs `$DISPLAY`).
**Full build recipe + every fix: `~/local/klayout-py311/SETUP.md`.** Summary:
```bash
# in ~/local/src/klayout-0.30.5, with ai_env on PATH:
./build.sh -qt5 -qmake $EDA/bin/qmake \
  -python $EDA/bin/python3.11 -pylib $EDA/lib/libpython3.11.so -pyinc $EDA/include/python3.11 \
  -ruby $EDA/bin/ruby -build ~/local/src/klayout-build -bin ~/local/klayout-py311 -option -j16
# plus in build.sh's qmake_options: QMAKE_LFLAGS+="-Wl,--allow-shlib-undefined -L~/local/gl-link"
#                                    QMAKE_CXXFLAGS+="-I~/local/gl-link/usr/include"
```

## 5. GL shim (`~/local/gl-link`) — needed by the KLayout build/GUI

RHEL8 lacks the OpenGL dev files conda-Qt5 wants:
```bash
# runtime + link symlinks from the system glvnd libs
ln -s /usr/lib64/libGL.so.1        ~/local/gl-link/libGL.so
ln -s /usr/lib64/libGL.so.1        ~/local/gl-link/libGL.so.1
ln -s /usr/lib64/libGLU.so.1       ~/local/gl-link/libGLU.so   # + .so.1
ln -s /usr/lib64/libGLdispatch.so.0 ~/local/gl-link/libGLdispatch.so   # + .so.0
ln -s /usr/lib64/libGLX.so.0       ~/local/gl-link/libGLX.so    # + .so.0
# GL headers (GL/gl.h …) — extract, don't install:
dnf download --destdir /tmp mesa-libGL-devel mesa-libGLU-devel libglvnd-devel
cd ~/local/gl-link && rpm2cpio /tmp/mesa-libGL-devel-*.x86_64.rpm | cpio -idmu   # etc.
```

## 6. magic (conda-forge, env `eda`)

The OSIC magic prebuilt needs glibc 2.34; conda-forge's does not:
```bash
conda create -n eda -c conda-forge magic          # 8.3.486 (+ tcl/tk/cairo)
```
Wrapper `~/local/bin/magic` sets `PDK_ROOT` and execs `~/miniconda3/envs/eda/bin/magic`.
Batch gotcha: run with `-rcfile /dev/null -T $PDK/libs.tech/magic/ihp-sg13g2-GDS.tech` and feed
the script via **stdin** (a trailing file arg is treated as a cell to load).

## 7. netgen (from source, `~/local/netgen`)

Not on conda-forge (that `netgen` is the mesh tool). Build 1.5.99 against `eda`'s tcl/tk:
```bash
curl -sO http://opencircuitdesign.com/netgen/archive/netgen-1.5.99.tgz && tar xzf netgen-1.5.99.tgz
cd netgen-1.5.99
CC=/usr/bin/gcc CPPFLAGS="-I$EDA/include" LDFLAGS="-L$EDA/lib" \
  ./configure --prefix=~/local/netgen --with-tcl=$EDA/lib --with-tk=$EDA/lib \
  --x-includes=$EDA/include --x-libraries=$EDA/lib      # needs system gcc + X11 headers
make && make install
```
Wrapper `~/local/bin/netgen` sets `LD_LIBRARY_PATH=$EDA/lib`.

## 8. ihp-gdsfactory (gdsfactory lane, in `ai_env`)

```bash
conda activate ai_env
pip install ihp-gdsfactory            # 0.2.7 — the last version that supports py3.11
pip install "protobuf>=6.32,<7"       # restore: vlsir (unused) downgraded it
```
PyPI name is `ihp-gdsfactory` (the PDK-vendored README's `ihp-gdfactory` is a typo);
2.0.0 needs py>=3.12. The install also bumps `gdsfactory` (9.34 works fine).

## 9. klayout-pex / kpex (PEX, own env `pex`)

```bash
conda create -n pex -y python=3.12    # kpex requires python >= 3.12
conda activate pex && pip install klayout-pex
```
kpex shells out to a KLayout **executable** whose LVS engine needs **Ruby >= 2.6**. The
rpm-shim batch klayout (Ruby 2.5) fails parsing the kpex deck; use the py3.11 source
build via its headless wrapper `~/local/klayout-py311/klayout-batch.sh` (Ruby 2.7 from
`ai_env`) — `pex_kpex.py` sets `KPEX_KLAYOUT_EXE` to it by default.

## Environment variables

```bash
export PDK_ROOT=~/local/pdks
export PDK=ihp-sg13g2
export KLAYOUT_PATH="$PDK_ROOT/ihp-sg13g2/libs.tech/klayout:$PDK_ROOT/ihp-sg13g2/libs.tech/klayout/tech"
export PATH="$HOME/local/bin:$PATH"     # klayout(batch), magic, netgen wrappers
```
`KLAYOUT_PATH` makes the sg13g2 technology + PyCell library auto-load in the GUI build.

## Verify everything

```bash
klayout -b -v                                   # -> KLayout 0.30.5 (batch shim)
magic --version                                 # -> 8.3.486
echo quit | netgen -batch                       # -> Netgen 1.5.99
python -c "import klayout, gdsfactory"          # ai_env modules import
~/local/klayout-py311/klayout-gui.sh -b -v      # -> 0.30.5, embedded Python 3.11

# end-to-end on the example (from 5t_ota/):
python gen_5t_ota.py                             # -> ota_5t.gds
python signoff.py                                # KLayout DRC + LVS   -> PASS / PASS
python signoff_magic_netgen.py                   # Magic DRC + netgen  -> PASS / PASS

# gdsfactory lane + PEX (from the parent ihp-sg13g2/ dir):
python 5t_ota_gf/gen_5t_ota_gf.py                # -> ota_5t_gf.gds (ai_env)
python 5t_ota_gf/signoff.py                      # PASS / PASS
conda run -n pex python pex_kpex.py --gds 5t_ota_gf/ota_5t_gf.gds \
    --cell ota_5t_gf --schematic 5t_ota_gf/ota_5t_gf_lvs.spice     # PEX OK
python sim_pex_compare.py --schematic 5t_ota_gf/ota_5t_gf_lvs.spice \
    --pex 5t_ota_gf/pex_out/kpex/ota_5t_gf__ota_5t_gf/ota_5t_gf_k25d_pex_netlist.spice \
    --cell ota_5t_gf                             # pre vs post-layout AC
```

## Path quick-reference

| Path | What |
|---|---|
| `~/local/pdks/ihp-sg13g2` | the PDK |
| `~/local/bin/{klayout,magic,netgen}` | tool wrappers (on `PATH`) |
| `~/local/klayout-runtime/` | batch KLayout (py3.6) + `SETUP.md` |
| `~/local/klayout-py311/` | GUI KLayout (py3.11) + `klayout-gui.sh` + `SETUP.md` |
| `~/local/netgen/` | netgen 1.5.99 |
| `~/local/gl-link/` | OpenGL libs + headers for the build |
| `~/miniconda3/envs/ai_env` | Python 3.11 env (klayout module, gdsfactory, ihp-gdsfactory) |
| `~/miniconda3/envs/eda` | magic 8.3.486 (+ tcl/tk for netgen) |
| `~/miniconda3/envs/pex` | Python 3.12 env (klayout-pex / kpex) |
| `~/local/klayout-py311/klayout-batch.sh` | headless py311/ruby2.7 KLayout (for kpex) |
