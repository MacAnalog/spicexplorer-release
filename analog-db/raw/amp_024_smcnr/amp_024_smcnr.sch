v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_024_smcnr} -890 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -170 390 0 0 {name=C0 value=x_c0}
C {devices/isource_np.sym} -850 520 0 0 {name=IBS value="dc {x_ibias_val}"}
C {devices/res_np.sym} 10 260 0 0 {name=R0 value=x_rz}
C {devices/sg13_lv_pmos_np.sym} -510 260 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_nmos_np.sym} -510 520 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -170 260 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} -170 520 0 0 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} 190 260 0 0 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 190 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 530 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -850 430 -850 490 {}
N -850 550 -850 610 {}
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
N 10 170 10 230 {}
N 10 290 10 350 {}
N 170 200 170 260 {}
N 210 -140 210 -30 {}
N 210 30 210 230 {}
N 210 290 210 350 {}
N 270 0 270 94 {}
N 270 260 270 354 {}
N 510 0 510 70 {}
N 550 -140 550 -30 {}
N 550 30 550 70 {}
N 610 0 610 94 {}
N -910 -140 740 -140 {}
N -420 0 -360 0 {}
N -320 0 170 0 {}
N 210 0 270 0 {}
N 450 0 510 0 {}
N 550 0 610 0 {}
N 510 70 550 70 {}
N -530 200 -150 200 {}
N -590 260 -530 260 {}
N -490 260 -430 260 {}
N -250 260 -190 260 {}
N -150 260 -90 260 {}
N 140 260 170 260 {}
N 210 260 270 260 {}
N -170 330 -150 330 {}
N -230 420 -170 420 {}
N -530 450 -490 450 {}
N -170 450 10 450 {}
N -530 460 -220 460 {}
N -590 520 -530 520 {}
N -220 520 -190 520 {}
N -150 520 -90 520 {}
N -910 660 740 660 {}
C {devices/lab_wire.sym} -910 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -910 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -260 0 0 1 {name=l2 lab=ibias}
C {devices/lab_wire.sym} 450 0 0 0 {name=l3 lab=ibias}
C {devices/lab_wire.sym} -230 420 0 0 {name=l4 lab=nzo}
C {devices/lab_wire.sym} 10 170 0 1 {name=l5 lab=nzo}
C {devices/lab_wire.sym} -150 350 2 0 {name=l6 lab=outn}
C {devices/lab_wire.sym} 170 200 0 1 {name=l7 lab=outn}
C {devices/lab_wire.sym} -530 350 2 0 {name=l8 lab=outp}
C {devices/lab_wire.sym} -360 90 2 0 {name=l9 lab=tailp}
C {devices/lab_wire.sym} -430 260 0 1 {name=l10 lab=vinn}
C {devices/lab_wire.sym} -250 260 0 0 {name=l11 lab=vinp}
C {devices/lab_wire.sym} 10 350 2 0 {name=l12 lab=vout}
C {devices/lab_wire.sym} 210 90 2 0 {name=l13 lab=vout}
C {devices/lab_wire.sym} -590 354 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} -90 354 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} 270 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} 610 94 2 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} -590 614 2 0 {name=l19 lab=vss}
C {devices/lab_wire.sym} -90 614 2 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} 270 354 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} -850 430 0 1 {name=l22 lab=ibias}
C {devices/lab_wire.sym} -850 610 2 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} 210 350 2 0 {name=l24 lab=vss}
C {devices/ipin.sym} -1050 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -1050 380 0 0 {name=p1 lab=vinp}
C {devices/opin.sym} 880 30 0 0 {name=p2 lab=vout}
