# Original design source — amp_019_ti_ldo_error

The source schematic is **not duplicated here**: it lives with the LDO that uses it,
at [`../../ldo_005_buffered_ref/reference/ti-ldo/error_amp/`](../../ldo_005_buffered_ref/reference/ti-ldo/)
(`error_amp.sch` + its own per-block testbenches `error_amp_tb*.sch`), vendored
verbatim from the meta-repo's `external/conceptual_LDO_design/ti-ldo/` tree
(first-party MacAnalog material, gf180mcu-native, TI application-note architecture).

## Connectivity ground truth

gf180's PDK device symbols netlist as `* IS MISSING` placeholders without the PDK's
`.model` cards, so the schematic was decoded by `.sym` pin-geometry resolution
(pin `B`-box centers transformed by each instance's `x y rot flip` placement,
looked up in the schematic's labelled wires). The resolved table:

```
M2                nfet_06v0    D=net_b   G=VFB    S=net_c  B=vss
M1                nfet_06v0    D=net_a   G=VREF   S=net_c  B=vss
M3m               pfet_06v0    D=net_a   G=net_d  S=vdd    B=vdd
M4                pfet_06v0    D=net_f   G=net_a  S=net_d  B=vdd
M5                pfet_06v0    D=net_b   G=net_d  S=vdd    B=vdd
M7                pfet_06v0    D=net_e   G=net_e  S=net_b  B=vdd
M6                pfet_06v0    D=EA_OUT  G=net_e  S=vdd    B=vdd
RZ                ppolyf_u_3k  P=#net1   M=net_b  B=vdd
M_mirror_error_amp_ref  nfet_06v0  D=G=#net2 (diode), S=vss
M_mirror_c/_f/_e/_ea_out nfet_06v0 G=#net2 sinks on net_c / net_f / net_e / EA_OUT
Cc: #net1 -> EA_OUT;  I_error_amp_ref: vdd -> #net2 (1 mA)
```

Net-name mapping into `../abstract/netlist.spice`: `net_a→na, net_b→nb, net_c→tail,
net_d→nd, net_e→ne, net_f→nlev, #net1→ncz, #net2→ibias` (the ideal reference current
is exposed as the amplifier-class `ibias` port).

Note `net_d` has **no DC current path** by design: M4 runs at (near) zero current as a
source-follower level shifter, so `net_d ≈ net_a + |Vgs(M4)|` — M3m/M5 mirror against a
Vth-level-shifted diode (extra Vds headroom; the TI paper's low-voltage mirror trick).
The source `.sch` carries WIP placeholder geometry (`W=0.3u` everywhere); the DB
bindings re-size coarsely for the 1 mA class bias.
