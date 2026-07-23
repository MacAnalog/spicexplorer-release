v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_024_smcnr} -700 -200 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -440 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_1.sym} 0 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/dp_pmos_simple_1.sym} 440 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -220 340 0 0 {name=C0 value=x_c0}
C {devices/isource_np.sym} -660 340 0 0 {name=IBS value="dc {x_ibias_val}"}
C {devices/res_np.sym} 0 340 0 0 {name=R0 value=x_rz}
C {devices/sg13_lv_nmos_np.sym} 220 340 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
N -330 -20 -290 -20 {}
C {devices/lab_wire.sym} -290 -20 0 1 {name=l0 lab=outn}
N -330 20 -290 20 {}
C {devices/lab_wire.sym} -290 20 0 1 {name=l1 lab=outp}
N -440 80 -440 120 {}
C {devices/lab_wire.sym} -440 120 2 0 {name=l2 lab=vss}
N 110 -40 150 -40 {}
C {devices/lab_wire.sym} 150 -40 0 1 {name=l3 lab=ibias}
N 110 0 150 0 {}
C {devices/lab_wire.sym} 150 0 0 1 {name=l4 lab=tailp}
N 110 40 150 40 {}
C {devices/lab_wire.sym} 150 40 0 1 {name=l5 lab=vout}
N 0 -100 0 -140 {}
C {devices/lab_wire.sym} 0 -140 0 1 {name=l6 lab=vdd}
N 330 -20 290 -20 {}
C {devices/lab_wire.sym} 290 -20 0 0 {name=l7 lab=vinn}
N 330 20 290 20 {}
C {devices/lab_wire.sym} 290 20 0 0 {name=l8 lab=vinp}
N 550 -40 590 -40 {}
C {devices/lab_wire.sym} 590 -40 0 1 {name=l9 lab=outn}
N 550 0 590 0 {}
C {devices/lab_wire.sym} 590 0 0 1 {name=l10 lab=outp}
N 550 40 590 40 {}
C {devices/lab_wire.sym} 590 40 0 1 {name=l11 lab=tailp}
N 440 -100 440 -140 {}
C {devices/lab_wire.sym} 440 -140 0 1 {name=l12 lab=vdd}
N -220 310 -220 270 {}
C {devices/lab_wire.sym} -220 270 0 1 {name=l13 lab=outn}
N -220 370 -220 410 {}
C {devices/lab_wire.sym} -220 410 2 0 {name=l14 lab=nzo}
N -660 310 -660 270 {}
C {devices/lab_wire.sym} -660 270 0 1 {name=l15 lab=ibias}
N -660 370 -660 410 {}
C {devices/lab_wire.sym} -660 410 2 0 {name=l16 lab=vss}
N 0 310 0 270 {}
C {devices/lab_wire.sym} 0 270 0 1 {name=l17 lab=nzo}
N 0 370 0 410 {}
C {devices/lab_wire.sym} 0 410 2 0 {name=l18 lab=vout}
N 240 310 240 270 {}
C {devices/lab_wire.sym} 240 270 0 1 {name=l19 lab=vout}
N 200 340 160 340 {}
C {devices/lab_wire.sym} 160 340 0 0 {name=l20 lab=outn}
N 240 370 240 410 {}
C {devices/lab_wire.sym} 240 410 2 0 {name=l21 lab=vss}
N 240 340 280 340 {}
C {devices/lab_wire.sym} 280 340 0 1 {name=l22 lab=vss}
