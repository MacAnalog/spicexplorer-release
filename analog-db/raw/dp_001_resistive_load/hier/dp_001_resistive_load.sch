v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_001_resistive_load} -260 -540 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -220 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_nmos_simple_1.sym} 220 0 0 0 {name=xdp_nmos_simple_1}
C {devices/res_np.sym} -110 -340 0 0 {name=RN value=x_dut_rn_value}
C {devices/res_np.sym} 110 -340 0 0 {name=RP value=x_dut_rp_value}
N -110 -20 -70 -20 {}
C {devices/lab_wire.sym} -70 -20 0 1 {name=l0 lab=ibias}
N -110 20 -70 20 {}
C {devices/lab_wire.sym} -70 20 0 1 {name=l1 lab=tail}
N -220 80 -220 120 {}
C {devices/lab_wire.sym} -220 120 2 0 {name=l2 lab=vss}
N 110 -20 70 -20 {}
C {devices/lab_wire.sym} 70 -20 0 0 {name=l3 lab=vinn}
N 110 20 70 20 {}
C {devices/lab_wire.sym} 70 20 0 0 {name=l4 lab=vinp}
N 330 -40 370 -40 {}
C {devices/lab_wire.sym} 370 -40 0 1 {name=l5 lab=tail}
N 330 0 370 0 {}
C {devices/lab_wire.sym} 370 0 0 1 {name=l6 lab=voutn}
N 330 40 370 40 {}
C {devices/lab_wire.sym} 370 40 0 1 {name=l7 lab=voutp}
N 220 100 220 140 {}
C {devices/lab_wire.sym} 220 140 2 0 {name=l8 lab=vss}
N -110 -370 -110 -410 {}
C {devices/lab_wire.sym} -110 -410 0 1 {name=l9 lab=vdd}
N -110 -310 -110 -270 {}
C {devices/lab_wire.sym} -110 -270 2 0 {name=l10 lab=voutn}
N 110 -370 110 -410 {}
C {devices/lab_wire.sym} 110 -410 0 1 {name=l11 lab=vdd}
N 110 -310 110 -270 {}
C {devices/lab_wire.sym} 110 -270 2 0 {name=l12 lab=voutp}
