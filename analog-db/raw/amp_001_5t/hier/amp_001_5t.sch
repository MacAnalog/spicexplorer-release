v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_001_5t} -480 -200 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -440 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_simple_1.sym} 0 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_nmos_simple_1.sym} 440 0 0 0 {name=xdp_nmos_simple_1}
N -330 -20 -290 -20 {}
C {devices/lab_wire.sym} -290 -20 0 1 {name=l0 lab=outm}
N -330 20 -290 20 {}
C {devices/lab_wire.sym} -290 20 0 1 {name=l1 lab=vout}
N -440 -80 -440 -120 {}
C {devices/lab_wire.sym} -440 -120 0 1 {name=l2 lab=vdd}
N 110 -20 150 -20 {}
C {devices/lab_wire.sym} 150 -20 0 1 {name=l3 lab=ibias}
N 110 20 150 20 {}
C {devices/lab_wire.sym} 150 20 0 1 {name=l4 lab=tail}
N 0 80 0 120 {}
C {devices/lab_wire.sym} 0 120 2 0 {name=l5 lab=vss}
N 330 -20 290 -20 {}
C {devices/lab_wire.sym} 290 -20 0 0 {name=l6 lab=vinn}
N 330 20 290 20 {}
C {devices/lab_wire.sym} 290 20 0 0 {name=l7 lab=vinp}
N 550 -40 590 -40 {}
C {devices/lab_wire.sym} 590 -40 0 1 {name=l8 lab=outm}
N 550 0 590 0 {}
C {devices/lab_wire.sym} 590 0 0 1 {name=l9 lab=tail}
N 550 40 590 40 {}
C {devices/lab_wire.sym} 590 40 0 1 {name=l10 lab=vout}
N 440 100 440 140 {}
C {devices/lab_wire.sym} 440 140 2 0 {name=l11 lab=vss}
