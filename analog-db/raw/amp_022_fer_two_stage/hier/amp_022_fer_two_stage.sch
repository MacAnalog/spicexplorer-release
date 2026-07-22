v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_022_fer_two_stage} -700 -200 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -660 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_1.sym} -220 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_simple_2.sym} 220 0 0 0 {name=xcm_nmos_simple_2}
C {blocks/dp_pmos_simple_1.sym} 660 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -110 340 0 0 {name=CC value=x_dut_cc_value}
C {devices/sg13_lv_nmos_np.sym} 110 340 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
N -550 -20 -510 -20 {}
C {devices/lab_wire.sym} -510 -20 0 1 {name=l0 lab=a}
N -550 20 -510 20 {}
C {devices/lab_wire.sym} -510 20 0 1 {name=l1 lab=b}
N -660 80 -660 120 {}
C {devices/lab_wire.sym} -660 120 2 0 {name=l2 lab=vss}
N -110 -40 -70 -40 {}
C {devices/lab_wire.sym} -70 -40 0 1 {name=l3 lab=c}
N -110 0 -70 0 {}
C {devices/lab_wire.sym} -70 0 0 1 {name=l4 lab=pbias}
N -110 40 -70 40 {}
C {devices/lab_wire.sym} -70 40 0 1 {name=l5 lab=vout}
N -220 -100 -220 -140 {}
C {devices/lab_wire.sym} -220 -140 0 1 {name=l6 lab=vdd}
N 330 -20 370 -20 {}
C {devices/lab_wire.sym} 370 -20 0 1 {name=l7 lab=ibias}
N 330 20 370 20 {}
C {devices/lab_wire.sym} 370 20 0 1 {name=l8 lab=pbias}
N 220 80 220 120 {}
C {devices/lab_wire.sym} 220 120 2 0 {name=l9 lab=vss}
N 550 -20 510 -20 {}
C {devices/lab_wire.sym} 510 -20 0 0 {name=l10 lab=vinn}
N 550 20 510 20 {}
C {devices/lab_wire.sym} 510 20 0 0 {name=l11 lab=vinp}
N 770 -40 810 -40 {}
C {devices/lab_wire.sym} 810 -40 0 1 {name=l12 lab=a}
N 770 0 810 0 {}
C {devices/lab_wire.sym} 810 0 0 1 {name=l13 lab=b}
N 770 40 810 40 {}
C {devices/lab_wire.sym} 810 40 0 1 {name=l14 lab=c}
N 660 -100 660 -140 {}
C {devices/lab_wire.sym} 660 -140 0 1 {name=l15 lab=vdd}
N -110 310 -110 270 {}
C {devices/lab_wire.sym} -110 270 0 1 {name=l16 lab=b}
N -110 370 -110 410 {}
C {devices/lab_wire.sym} -110 410 2 0 {name=l17 lab=vout}
N 130 310 130 270 {}
C {devices/lab_wire.sym} 130 270 0 1 {name=l18 lab=vout}
N 90 340 50 340 {}
C {devices/lab_wire.sym} 50 340 0 0 {name=l19 lab=b}
N 130 370 130 410 {}
C {devices/lab_wire.sym} 130 410 2 0 {name=l20 lab=vss}
N 130 340 170 340 {}
C {devices/lab_wire.sym} 170 340 0 1 {name=l21 lab=vss}
