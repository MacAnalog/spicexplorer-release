v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_024_smcnr} -925 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -170 390 0 0 {name=C0 value=x_c0}
C {devices/isource_np.sym} -885 520 0 0 {name=IBS value="dc \{x_ibias_val\}"}
C {devices/res_np.sym} 50 260 0 0 {name=R0 value=x_rz}
C {devices/sg13_lv_pmos_np.sym} -510 260 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_nmos_np.sym} -510 520 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -170 260 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} -170 520 0 0 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} 230 260 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 230 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 570 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -885 430 -885 490 {}
N -885 550 -885 610 {}
N -590 260 -590 354 {}
N -590 520 -590 614 {}
N -530 200 -530 230 {}
N -530 290 -530 490 {}
N -530 550 -530 660 {}
N -490 450 -490 520 {}
N -420 0 -420 94 {}
N -360 -140 -360 -30 {}
N -360 30 -360 200 {}
N -220 460 -220 520 {}
N -170 330 -170 360 {}
N -170 420 -170 450 {}
N -150 200 -150 230 {}
N -150 290 -150 490 {}
N -150 550 -150 660 {}
N -90 260 -90 354 {}
N -90 520 -90 614 {}
N 50 170 50 230 {}
N 50 290 50 350 {}
N 180 -60 180 0 {}
N 250 -140 250 -30 {}
N 250 30 250 230 {}
N 250 290 250 660 {}
N 310 0 310 94 {}
N 310 260 310 354 {}
N 550 -60 550 70 {}
N 590 -140 590 -30 {}
N 590 30 590 70 {}
N 650 0 650 94 {}
N -985 -140 1045 -140 {}
N 180 -60 550 -60 {}
N -420 0 -360 0 {}
N -320 0 210 0 {}
N 250 0 310 0 {}
N 590 0 650 0 {}
N 550 70 590 70 {}
N -530 200 -150 200 {}
N -590 260 -530 260 {}
N -490 260 -460 260 {}
N -280 260 -190 260 {}
N -150 260 -90 260 {}
N 150 260 210 260 {}
N 250 260 310 260 {}
N -170 330 -150 330 {}
N -230 420 -170 420 {}
N -530 450 -490 450 {}
N -530 460 -220 460 {}
N -590 520 -530 520 {}
N -220 520 -190 520 {}
N -150 520 -90 520 {}
N -985 660 1045 660 {}
C {devices/lab_wire.sym} -260 0 0 1 {name=l0 lab=ibias}
C {devices/lab_wire.sym} -230 420 0 0 {name=l1 lab=nzo}
C {devices/lab_wire.sym} 50 170 0 1 {name=l2 lab=nzo}
C {devices/lab_wire.sym} -150 350 2 0 {name=l3 lab=outn}
C {devices/lab_wire.sym} 150 260 0 0 {name=l4 lab=outn}
C {devices/lab_wire.sym} -530 350 2 0 {name=l5 lab=outp}
C {devices/lab_wire.sym} -360 90 2 0 {name=l6 lab=tailp}
C {devices/lab_wire.sym} 50 350 2 0 {name=l7 lab=vout}
C {devices/lab_wire.sym} -590 354 2 0 {name=l8 lab=vdd}
C {devices/lab_wire.sym} -90 354 2 0 {name=l9 lab=vdd}
C {devices/lab_wire.sym} 310 94 2 0 {name=l10 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} 650 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -590 614 2 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} -90 614 2 0 {name=l14 lab=vss}
C {devices/lab_wire.sym} 310 354 2 0 {name=l15 lab=vss}
C {devices/lab_wire.sym} -885 430 0 1 {name=l16 lab=ibias}
C {devices/lab_wire.sym} -885 610 2 0 {name=l17 lab=vss}
C {devices/ipin.sym} -460 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -280 260 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -985 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -985 660 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 250 60 0 0 {name=p4 lab=vout}
B 8 -966 442 286 598 {fill=0}
T {NMOS Simple Current Mirror} -966 424 0 0 0.3 0.3 {layer=8}
B 10 -796 -78 1026 78 {fill=0}
T {PMOS Simple Current Mirror (2 outputs)} -796 -96 0 0 0.3 0.3 {layer=10}
B 12 -966 182 286 338 {fill=0}
T {PMOS Differential Pair} -966 164 0 0 0.3 0.3 {layer=12}
