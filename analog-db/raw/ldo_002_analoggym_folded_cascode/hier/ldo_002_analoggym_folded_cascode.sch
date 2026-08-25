v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_002_analoggym_folded_cascode} -810 -540 0 0 0.4 0.4 {}
C {blocks/dp_nmos_simple_1.sym} 0 0 0 0 {name=xdp_nmos_simple_1}
C {devices/capa_np.sym} -550 340 0 0 {name=CC value='c_comp'}
C {devices/res_np.sym} -330 340 0 0 {name=RZ value='r_z'}
C {devices/res_np.sym} -110 340 0 0 {name=R_BLEED value='r_bleed'}
C {devices/vsource_np.sym} -770 340 0 0 {name=VB1 value="dc {vb1_val}"}
C {devices/vsource_np.sym} -770 120 0 0 {name=VB2 value="dc {vb2_val}"}
C {devices/vsource_np.sym} -770 -100 0 0 {name=VLP value="dc 0"}
C {devices/vsource_np.sym} -770 -320 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_pmos_np.sym} -440 -340 0 0 {name=M3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} -220 -340 0 0 {name=M4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} 0 -340 0 0 {name=M5 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 220 -340 0 0 {name=M6 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
C {devices/sg13_lv_nmos_np.sym} 110 340 0 0 {name=M7 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l}
C {devices/sg13_lv_nmos_np.sym} 330 340 0 0 {name=M8 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l}
C {devices/sg13_lv_nmos_np.sym} 550 340 0 0 {name=M9 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l}
C {devices/sg13_lv_pmos_np.sym} 440 -340 0 0 {name=MP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -110 -20 -150 -20 {}
C {devices/lab_wire.sym} -150 -20 0 0 {name=l0 lab=lp_brk}
N -110 20 -150 20 {}
C {devices/lab_wire.sym} -150 20 0 0 {name=l1 lab=vref}
N 110 -40 150 -40 {}
C {devices/lab_wire.sym} 150 -40 0 1 {name=l2 lab=n2}
N 110 0 150 0 {}
C {devices/lab_wire.sym} 150 0 0 1 {name=l3 lab=n3}
N 110 40 150 40 {}
C {devices/lab_wire.sym} 150 40 0 1 {name=l4 lab=n4}
N 0 100 0 140 {}
C {devices/lab_wire.sym} 0 140 2 0 {name=l5 lab=vss}
N -550 310 -550 270 {}
C {devices/lab_wire.sym} -550 270 0 1 {name=l6 lab=ncz}
N -550 370 -550 410 {}
C {devices/lab_wire.sym} -550 410 2 0 {name=l7 lab=vout}
N -330 310 -330 270 {}
C {devices/lab_wire.sym} -330 270 0 1 {name=l8 lab=ncz}
N -330 370 -330 410 {}
C {devices/lab_wire.sym} -330 410 2 0 {name=l9 lab=ngate}
N -110 310 -110 270 {}
C {devices/lab_wire.sym} -110 270 0 1 {name=l10 lab=vout}
N -110 370 -110 410 {}
C {devices/lab_wire.sym} -110 410 2 0 {name=l11 lab=vss}
N -770 310 -770 270 {}
C {devices/lab_wire.sym} -770 270 0 1 {name=l12 lab=vb1}
N -770 370 -770 410 {}
C {devices/lab_wire.sym} -770 410 2 0 {name=l13 lab=vss}
N -770 90 -770 50 {}
C {devices/lab_wire.sym} -770 50 0 1 {name=l14 lab=vb2}
N -770 150 -770 190 {}
C {devices/lab_wire.sym} -770 190 2 0 {name=l15 lab=vss}
N -770 -130 -770 -170 {}
C {devices/lab_wire.sym} -770 -170 0 1 {name=l16 lab=lp_brk}
N -770 -70 -770 -30 {}
C {devices/lab_wire.sym} -770 -30 2 0 {name=l17 lab=vout}
N -770 -350 -770 -390 {}
C {devices/lab_wire.sym} -770 -390 0 1 {name=l18 lab=vref}
N -770 -290 -770 -250 {}
C {devices/lab_wire.sym} -770 -250 2 0 {name=l19 lab=vss}
N -420 -310 -420 -270 {}
C {devices/lab_wire.sym} -420 -270 2 0 {name=l20 lab=n2}
N -460 -340 -500 -340 {}
C {devices/lab_wire.sym} -500 -340 0 0 {name=l21 lab=nmir}
N -420 -370 -420 -410 {}
C {devices/lab_wire.sym} -420 -410 0 1 {name=l22 lab=vdd}
N -420 -340 -380 -340 {}
C {devices/lab_wire.sym} -380 -340 0 1 {name=l23 lab=vdd}
N -200 -310 -200 -270 {}
C {devices/lab_wire.sym} -200 -270 2 0 {name=l24 lab=n3}
N -240 -340 -280 -340 {}
C {devices/lab_wire.sym} -280 -340 0 0 {name=l25 lab=nmir}
N -200 -370 -200 -410 {}
C {devices/lab_wire.sym} -200 -410 0 1 {name=l26 lab=vdd}
N -200 -340 -160 -340 {}
C {devices/lab_wire.sym} -160 -340 0 1 {name=l27 lab=vdd}
N 20 -310 20 -270 {}
C {devices/lab_wire.sym} 20 -270 2 0 {name=l28 lab=nmir}
N -20 -340 -60 -340 {}
C {devices/lab_wire.sym} -60 -340 0 0 {name=l29 lab=vb2}
N 20 -370 20 -410 {}
C {devices/lab_wire.sym} 20 -410 0 1 {name=l30 lab=n2}
N 20 -340 60 -340 {}
C {devices/lab_wire.sym} 60 -340 0 1 {name=l31 lab=vdd}
N 240 -310 240 -270 {}
C {devices/lab_wire.sym} 240 -270 2 0 {name=l32 lab=ngate}
N 200 -340 160 -340 {}
C {devices/lab_wire.sym} 160 -340 0 0 {name=l33 lab=vb2}
N 240 -370 240 -410 {}
C {devices/lab_wire.sym} 240 -410 0 1 {name=l34 lab=n3}
N 240 -340 280 -340 {}
C {devices/lab_wire.sym} 280 -340 0 1 {name=l35 lab=vdd}
N 130 310 130 270 {}
C {devices/lab_wire.sym} 130 270 0 1 {name=l36 lab=nmir}
N 90 340 50 340 {}
C {devices/lab_wire.sym} 50 340 0 0 {name=l37 lab=vb1}
N 130 370 130 410 {}
C {devices/lab_wire.sym} 130 410 2 0 {name=l38 lab=vss}
N 130 340 170 340 {}
C {devices/lab_wire.sym} 170 340 0 1 {name=l39 lab=vss}
N 350 310 350 270 {}
C {devices/lab_wire.sym} 350 270 0 1 {name=l40 lab=ngate}
N 310 340 270 340 {}
C {devices/lab_wire.sym} 270 340 0 0 {name=l41 lab=vb1}
N 350 370 350 410 {}
C {devices/lab_wire.sym} 350 410 2 0 {name=l42 lab=vss}
N 350 340 390 340 {}
C {devices/lab_wire.sym} 390 340 0 1 {name=l43 lab=vss}
N 570 310 570 270 {}
C {devices/lab_wire.sym} 570 270 0 1 {name=l44 lab=n4}
N 530 340 490 340 {}
C {devices/lab_wire.sym} 490 340 0 0 {name=l45 lab=vb1}
N 570 370 570 410 {}
C {devices/lab_wire.sym} 570 410 2 0 {name=l46 lab=vss}
N 570 340 610 340 {}
C {devices/lab_wire.sym} 610 340 0 1 {name=l47 lab=vss}
N 460 -310 460 -270 {}
C {devices/lab_wire.sym} 460 -270 2 0 {name=l48 lab=vout}
N 420 -340 380 -340 {}
C {devices/lab_wire.sym} 380 -340 0 0 {name=l49 lab=ngate}
N 460 -370 460 -410 {}
C {devices/lab_wire.sym} 460 -410 0 1 {name=l50 lab=vdd}
N 460 -340 500 -340 {}
C {devices/lab_wire.sym} 500 -340 0 1 {name=l51 lab=vdd}
