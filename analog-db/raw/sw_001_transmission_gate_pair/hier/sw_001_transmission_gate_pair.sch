v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sw_001_transmission_gate_pair} -40 -200 0 0 0.4 0.4 {}
C {blocks/tg_pair_cmos_rail_bulk_1.sym} 0 0 0 0 {name=xtg_pair_cmos_rail_bulk_1}
N -140 -20 -180 -20 {}
C {devices/lab_wire.sym} -180 -20 0 0 {name=l0 lab=vctl}
N -140 20 -180 20 {}
C {devices/lab_wire.sym} -180 20 0 0 {name=l1 lab=vctl_not}
N 140 -20 180 -20 {}
C {devices/lab_wire.sym} 180 -20 0 1 {name=l2 lab=port_a}
N 140 20 180 20 {}
C {devices/lab_wire.sym} 180 20 0 1 {name=l3 lab=port_b}
N 0 -80 0 -120 {}
C {devices/lab_wire.sym} 0 -120 0 1 {name=l4 lab=vdd}
N 0 80 0 120 {}
C {devices/lab_wire.sym} 0 120 2 0 {name=l5 lab=vss}
