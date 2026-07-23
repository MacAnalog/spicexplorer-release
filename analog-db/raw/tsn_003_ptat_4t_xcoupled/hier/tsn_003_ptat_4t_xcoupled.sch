v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {tsn_003_ptat_4t_xcoupled} -260 -200 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -220 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_1.sym} 220 0 0 0 {name=xcm_pmos_simple_1}
N -110 -20 -70 -20 {}
C {devices/lab_wire.sym} -70 -20 0 1 {name=l0 lab=na}
N -110 20 -70 20 {}
C {devices/lab_wire.sym} -70 20 0 1 {name=l1 lab=vout}
N -220 80 -220 120 {}
C {devices/lab_wire.sym} -220 120 2 0 {name=l2 lab=vss}
N 330 -20 370 -20 {}
C {devices/lab_wire.sym} 370 -20 0 1 {name=l3 lab=na}
N 330 20 370 20 {}
C {devices/lab_wire.sym} 370 20 0 1 {name=l4 lab=vout}
N 220 -80 220 -120 {}
C {devices/lab_wire.sym} 220 -120 0 1 {name=l5 lab=vdd}
