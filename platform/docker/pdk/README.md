# Vendored PDK subsets — ngspice (3 PDKs)

This directory ships the **minimal subset** of three open PDKs that SpiceXplorer's
ngspice flow needs, so the Docker base image is self-contained (no host PDK install,
no multi-GB EDA base). It is **~20 MB** total. A netlist selects its PDK via its own
`.lib`; all three are placed on the ngspice sourcepath, so any one is reachable by a
bare `.lib` name.

| PDK | Vendored here | What is unpacked into the image | OSDI? |
|---|---|---|---|
| **IHP `ihp-sg13g2`** | `ihp-sg13g2/` (~3.2 MB, unpacked tree) | `libs.tech/ngspice/` (`.spiceinit`, `models/*.lib`, prebuilt `osdi/*.osdi`), `verilog-a/` (OSDI sources), `xschem/` (symbols) | yes — PSP103 / r3_cmc / mosvar (compiled or vendored) |
| **SkyWater `sky130`** | `sky130_pdk.zip` (~17 MB) | ngspice corner libs + the `sky130_fd_pr` device models | no (BSIM4, built into ngspice) |
| **GlobalFoundries `gf180mcu`** | `gf180_pdk.zip` (~148 KB) | ngspice model libs only | no (BSIM4) |

The IHP tree is the only one kept unpacked, because its OSDI source must be compiled at
build time; sky130/gf180 are vendored as zips and unzipped during the build to keep the
checked-in subset small.

```
ihp-sg13g2/libs.tech/
  ngspice/
    .spiceinit        # sets sourcepath + loads the OSDI compact models
    models/*.lib      # device model libraries (cornerMOSlv.lib, cornerRES.lib, …)
    osdi/*.osdi       # prebuilt OSDI compact models — x86-64 (used by OSDI_MODE=vendor)
  verilog-a/          # OSDI source (psp103, r3_cmc, mosvar) — compiled per-arch
    {psp103,r3_cmc,mosvar}/*.va    #   by openvaf when OSDI_MODE=compile (default)
  xschem/             # PDK symbol libraries (sg13g2_pr/*.sym) for the in-browser schematic viewer
```

The base image [`docker/Dockerfile.spice-base`](../Dockerfile.spice-base) copies the IHP
tree to `/opt/pdk/ihp-sg13g2/`, unzips sky130 → `/opt/pdk/sky130/` and gf180mcu →
`/opt/pdk/gf180mcu/`, and sets `PDK_ROOT=/opt/pdk`, `PDK=ihp-sg13g2`. The IHP `.spiceinit`
then appends the sky130 + gf180 ngspice dirs to the sourcepath, so a netlist's bare
`.lib sky130.lib.spice <corner>` / `.lib sm141064.ngspice <section>` resolves the same way
IHP's does. The IHP OSDI always loads (it is simply unused by a sky130/gf180 sim).

## License

All three are permissively licensed open PDKs (**Apache License 2.0**), freely
redistributable; every `*.lib` carries its per-file copyright header — do not strip them.

- IHP Open PDK — <https://github.com/IHP-GmbH/IHP-Open-PDK>
- SkyWater sky130 + GF gf180mcu — distributed via the `open_pdks` / `volare` projects.

## Architecture note (the IHP `*.osdi` files)

OSDI compact models are architecture-specific compiled binaries (only IHP uses them;
sky130/gf180 are BSIM4, built into ngspice). The base image handles this with the
`OSDI_MODE` build arg:

- **`compile` (default):** [`docker/Dockerfile.spice-base`](../Dockerfile.spice-base) builds
  openvaf and compiles the `verilog-a/` sources **for the build's own architecture** — so
  the image is native on x86-64 **and** arm64 (incl. Apple silicon), no emulation. This is
  the recipe below, run automatically in a throwaway build stage.
- **`vendor`:** reuse the committed `osdi/*.osdi`, which are **x86-64 ELF** (ABI-matched to
  ngspice 45). Faster (no openvaf toolchain) but x86-64 only.

To regenerate the committed prebuilt `osdi/*.osdi` (e.g. to refresh `vendor` mode or track a
newer PDK), use the same recipe iic-osic-tools uses:

```bash
# 1. Build openvaf-reloaded (needs Rust + LLVM-18):
git clone --filter=blob:none https://github.com/arpadbuermen/OpenVAF.git
cd OpenVAF && git checkout 2e066436d985b05cf8e6563e936daf9ab875775a
cargo build --release --features llvm18 --bin openvaf-r   # -> target/release/openvaf-r

# 2. Compile the models (from <PDK>/libs.tech/verilog-a/, per openvaf-compile-va.sh):
openvaf --target_cpu generic -D__NGSPICE__ -o ../ngspice/osdi/psp103.osdi     psp103/psp103.va
openvaf --target_cpu generic -D__NGSPICE__ -o ../ngspice/osdi/psp103_nqs.osdi psp103/psp103_nqs.va
openvaf --target_cpu generic -D__NGSPICE__ -o ../ngspice/osdi/r3_cmc.osdi     r3_cmc/r3_cmc.va
openvaf --target_cpu generic -D__NGSPICE__ -o ../ngspice/osdi/mosvar.osdi     mosvar/mosvar.va
```

Then replace the `osdi/*.osdi` here. (The default `compile` mode runs exactly this in a
throwaway build stage; the committed `osdi/*.osdi` exist only for the optional `vendor`
fast-path, since the openvaf build needs a ~1 GB LLVM-18 + Rust toolchain.)
