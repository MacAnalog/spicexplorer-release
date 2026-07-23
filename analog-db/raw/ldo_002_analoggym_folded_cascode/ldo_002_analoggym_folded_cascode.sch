v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_002_analoggym_folded_cascode} -720 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 480 260 1 0 {name=CC value='c_comp'}
C {devices/res_np.sym} 140 390 0 0 {name=RZ value='r_z'}
C {devices/res_np.sym} 430 520 0 0 {name=R_BLEED value='r_bleed'}
C {devices/vsource_np.sym} -680 520 0 0 {name=VB1 value="dc {vb1_val}"}
C {devices/vsource_np.sym} -680 260 0 0 {name=VB2 value="dc {vb2_val}"}
C {devices/vsource_np.sym} -680 0 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_nmos_np.sym} -160 260 0 1 {name=M1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} 200 260 0 0 {name=M2 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} 20 0 0 0 {name=M4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} -340 260 0 1 {name=M5 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 20 260 0 0 {name=M6 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 1 {name=M7 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l}
C {devices/sg13_lv_nmos_np.sym} 20 520 0 0 {name=M8 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l}
C {devices/sg13_lv_nmos_np.sym} 200 520 0 0 {name=M9 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l}
C {devices/sg13_lv_pmos_np.sym} 380 0 0 0 {name=MP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -680 -90 -680 -30 {}
N -680 30 -680 90 {}
N -680 170 -680 230 {}
N -680 290 -680 350 {}
N -680 430 -680 490 {}
N -680 550 -680 610 {}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -420 520 -420 614 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -360 290 -360 490 {}
N -360 550 -360 660 {}
N -240 260 -240 354 {}
N -180 200 -180 230 {}
N -180 290 -180 350 {}
N -140 260 -140 320 {}
N 0 200 0 260 {}
N 40 -140 40 -30 {}
N 40 30 40 230 {}
N 40 290 40 350 {}
N 40 460 40 490 {}
N 40 550 40 660 {}
N 100 0 100 94 {}
N 100 260 100 354 {}
N 100 520 100 614 {}
N 140 330 140 360 {}
N 140 420 140 460 {}
N 180 520 180 580 {}
N 220 200 220 230 {}
N 220 290 220 490 {}
N 220 550 220 660 {}
N 280 260 280 354 {}
N 280 520 280 614 {}
N 330 0 330 450 {}
N 400 -140 400 -30 {}
N 400 30 400 260 {}
N 430 60 430 490 {}
N 430 550 430 660 {}
N 460 0 460 94 {}
N 510 260 510 320 {}
N 540 260 540 330 {}
N -740 -140 650 -140 {}
N -420 0 -360 0 {}
N -320 0 0 0 {}
N 40 0 100 0 {}
N 300 0 360 0 {}
N 400 0 460 0 {}
N 400 60 430 60 {}
N -360 200 -180 200 {}
N 40 200 220 200 {}
N -420 260 -360 260 {}
N -240 260 -180 260 {}
N -140 260 -110 260 {}
N -30 260 0 260 {}
N 40 260 100 260 {}
N 150 260 180 260 {}
N 220 260 280 260 {}
N 400 260 450 260 {}
N 510 260 540 260 {}
N -360 320 -290 320 {}
N 140 330 540 330 {}
N 140 450 330 450 {}
N 40 460 140 460 {}
N -420 520 -360 520 {}
N -320 520 0 520 {}
N 40 520 100 520 {}
N 150 520 180 520 {}
N 220 520 280 520 {}
N -740 660 650 660 {}
C {devices/lab_wire.sym} -740 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -740 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -360 90 2 0 {name=l2 lab=n2}
C {devices/lab_wire.sym} 40 90 2 0 {name=l3 lab=n3}
C {devices/lab_wire.sym} -180 350 2 0 {name=l4 lab=n4}
C {devices/lab_wire.sym} 220 350 2 0 {name=l5 lab=n4}
C {devices/lab_wire.sym} 510 320 2 0 {name=l6 lab=ncz}
C {devices/lab_wire.sym} 40 350 2 0 {name=l7 lab=ngate}
C {devices/lab_wire.sym} 300 0 0 0 {name=l8 lab=ngate}
C {devices/lab_wire.sym} -360 350 2 0 {name=l9 lab=nmir}
C {devices/lab_wire.sym} -260 0 0 1 {name=l10 lab=nmir}
C {devices/lab_wire.sym} -260 520 0 1 {name=l11 lab=vb1}
C {devices/lab_wire.sym} 180 580 2 0 {name=l12 lab=vb1}
C {devices/lab_wire.sym} -320 260 0 0 {name=l13 lab=vb2}
C {devices/lab_wire.sym} 0 200 0 1 {name=l14 lab=vb2}
C {devices/lab_wire.sym} -140 320 2 0 {name=l15 lab=vout}
C {devices/lab_wire.sym} 400 90 2 0 {name=l16 lab=vout}
C {devices/lab_wire.sym} 180 260 0 0 {name=l17 lab=vref}
C {devices/lab_wire.sym} -420 94 2 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} 100 94 2 0 {name=l19 lab=vdd}
C {devices/lab_wire.sym} -420 354 2 0 {name=l20 lab=vdd}
C {devices/lab_wire.sym} 100 354 2 0 {name=l21 lab=vdd}
C {devices/lab_wire.sym} 460 94 2 0 {name=l22 lab=vdd}
C {devices/lab_wire.sym} -240 354 2 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} 280 354 2 0 {name=l24 lab=vss}
C {devices/lab_wire.sym} -420 614 2 0 {name=l25 lab=vss}
C {devices/lab_wire.sym} 100 614 2 0 {name=l26 lab=vss}
C {devices/lab_wire.sym} 280 614 2 0 {name=l27 lab=vss}
C {devices/lab_wire.sym} -680 610 2 0 {name=l28 lab=vss}
C {devices/lab_wire.sym} -680 350 2 0 {name=l29 lab=vss}
C {devices/lab_wire.sym} -680 90 2 0 {name=l30 lab=vss}
C {devices/lab_wire.sym} -680 430 0 1 {name=l31 lab=vb1}
C {devices/lab_wire.sym} -680 170 0 1 {name=l32 lab=vb2}
C {devices/lab_wire.sym} -680 -90 0 1 {name=l33 lab=vref}
C {devices/opin.sym} 790 30 0 0 {name=p0 lab=vout}
