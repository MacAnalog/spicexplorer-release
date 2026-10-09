v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_031_srmc_core_cmfb} -1020 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1390 520 0 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} 110 520 0 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} 715 520 0 0 {name=CIN1 value='cin_val'}
C {devices/capa_np.sym} -455 520 0 0 {name=CIN2 value='cin_val'}
C {devices/capa_np.sym} 120 780 0 0 {name=COUT1 value='cout_val'}
C {devices/capa_np.sym} 315 780 0 0 {name=COUT2 value='cout_val'}
C {devices/vccs.sym} 120 650 0 0 {name=GM1 value="\{gm_val\}"}
C {devices/vccs.sym} 315 650 0 0 {name=GM2 value="\{gm_val\}"}
C {devices/res_np.sym} 110 390 1 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} 350 390 1 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} 900 520 0 0 {name=RIN1 value='rin_val'}
C {devices/res_np.sym} -640 520 0 0 {name=RIN2 value='rin_val'}
C {devices/res_np.sym} 1630 520 0 0 {name=RM1N value='x_dut_rm1n_value'}
C {devices/res_np.sym} 1100 520 0 0 {name=RM1P value='x_dut_rm1p_value'}
C {devices/res_np.sym} 595 390 1 0 {name=RM2N value='x_dut_rm2n_value'}
C {devices/res_np.sym} -150 390 1 0 {name=RM2P value='x_dut_rm2p_value'}
C {devices/res_np.sym} -75 780 0 0 {name=ROUT1 value='rout_val'}
C {devices/res_np.sym} 505 780 0 0 {name=ROUT2 value='rout_val'}
C {devices/vsource_np.sym} -980 780 0 0 {name=VB2 value="dc \{vb2\}" savecurrent=false}
C {devices/vsource_np.sym} -980 520 0 0 {name=VREF1 value="dc \{vref_cm\}" savecurrent=false}
C {devices/vsource_np.sym} -980 260 0 0 {name=VREF2 value="dc \{vref_cm\}" savecurrent=false}
C {devices/sg13_lv_nmos_np.sym} -510 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 745 0 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 350 520 0 0 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} -135 520 0 1 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} -295 780 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} -135 260 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 350 260 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 120 0 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_nmos_np.sym} 745 260 0 0 {name=M9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -980 170 -980 230 {}
N -980 290 -980 350 {}
N -980 430 -980 490 {}
N -980 550 -980 610 {}
N -980 690 -980 750 {}
N -980 810 -980 870 {}
N -640 460 -640 490 {}
N -640 550 -640 610 {}
N -590 0 -590 94 {}
N -590 260 -590 354 {}
N -530 -140 -530 -30 {}
N -530 30 -530 230 {}
N -530 290 -530 920 {}
N -455 460 -455 490 {}
N -455 550 -455 580 {}
N -275 720 -275 750 {}
N -275 810 -275 920 {}
N -215 320 -215 490 {}
N -215 520 -215 614 {}
N -215 780 -215 874 {}
N -210 200 -210 390 {}
N -155 200 -155 230 {}
N -155 290 -155 350 {}
N -155 550 -155 610 {}
N -120 390 -120 450 {}
N -95 550 -95 720 {}
N -85 260 -85 520 {}
N -75 690 -75 750 {}
N -75 810 -75 840 {}
N -30 390 -30 460 {}
N -10 580 -10 670 {}
N 50 330 50 390 {}
N 70 0 70 710 {}
N 110 460 110 490 {}
N 120 680 120 710 {}
N 120 810 120 840 {}
N 140 -140 140 -30 {}
N 140 30 140 200 {}
N 140 330 140 390 {}
N 170 460 170 490 {}
N 180 710 180 840 {}
N 200 0 200 94 {}
N 300 260 300 520 {}
N 315 560 315 620 {}
N 315 680 315 710 {}
N 315 810 315 840 {}
N 370 200 370 230 {}
N 370 290 370 350 {}
N 370 430 370 490 {}
N 370 550 370 610 {}
N 375 710 375 840 {}
N 380 390 380 450 {}
N 430 260 430 354 {}
N 430 520 430 614 {}
N 505 690 505 750 {}
N 505 810 505 840 {}
N 715 430 715 490 {}
N 715 550 715 580 {}
N 715 580 715 610 {}
N 765 -140 765 -30 {}
N 765 30 765 230 {}
N 765 290 765 920 {}
N 825 0 825 94 {}
N 825 200 825 390 {}
N 900 430 900 490 {}
N 900 550 900 580 {}
N 1100 430 1100 490 {}
N 1100 550 1100 610 {}
N 1390 430 1390 490 {}
N 1390 550 1390 610 {}
N 1630 460 1630 490 {}
N 1630 550 1630 610 {}
N -1040 -140 1955 -140 {}
N -590 0 -530 0 {}
N -490 0 -430 0 {}
N 40 0 100 0 {}
N 140 0 200 0 {}
N 665 0 725 0 {}
N 765 0 825 0 {}
N -530 200 -210 200 {}
N -155 200 370 200 {}
N 765 200 825 200 {}
N -590 260 -530 260 {}
N -490 260 -430 260 {}
N -115 260 -85 260 {}
N 300 260 330 260 {}
N 370 260 430 260 {}
N 665 260 725 260 {}
N -215 320 -155 320 {}
N -210 330 50 330 {}
N -210 390 -180 390 {}
N -120 390 -30 390 {}
N 50 390 80 390 {}
N 140 390 170 390 {}
N 290 390 320 390 {}
N 380 390 410 390 {}
N 505 390 565 390 {}
N 625 390 825 390 {}
N -640 460 -30 460 {}
N 110 460 170 460 {}
N 1390 460 1630 460 {}
N -215 490 170 490 {}
N -215 520 -155 520 {}
N -115 520 -85 520 {}
N 300 520 330 520 {}
N 370 520 430 520 {}
N -155 550 -95 550 {}
N 50 550 110 550 {}
N -640 580 -455 580 {}
N -10 580 900 580 {}
N 60 620 120 620 {}
N 20 630 80 630 {}
N 215 630 275 630 {}
N -10 670 80 670 {}
N 215 670 275 670 {}
N 70 710 180 710 {}
N 315 710 375 710 {}
N -275 720 -95 720 {}
N -375 780 -315 780 {}
N -275 780 -215 780 {}
N -75 840 180 840 {}
N 315 840 505 840 {}
N -1040 920 1955 920 {}
C {devices/lab_wire.sym} 20 630 0 0 {name=l0 lab=cm1_det}
C {devices/lab_wire.sym} 715 430 0 1 {name=l1 lab=cm1_det}
C {devices/lab_wire.sym} 900 430 0 1 {name=l2 lab=cm1_det}
C {devices/lab_wire.sym} 1100 430 0 1 {name=l3 lab=cm1_det}
C {devices/lab_wire.sym} 1630 610 2 0 {name=l4 lab=cm1_det}
C {devices/lab_wire.sym} -120 450 2 0 {name=l5 lab=cm2_det}
C {devices/lab_wire.sym} 215 630 0 0 {name=l6 lab=cm2_det}
C {devices/lab_wire.sym} 505 390 0 0 {name=l7 lab=cm2_det}
C {devices/lab_wire.sym} -155 610 2 0 {name=l8 lab=ntail}
C {devices/lab_wire.sym} 370 610 2 0 {name=l9 lab=ntail}
C {devices/lab_wire.sym} 140 90 2 0 {name=l10 lab=ptail}
C {devices/lab_wire.sym} -375 780 0 0 {name=l11 lab=vb2}
C {devices/lab_wire.sym} 40 0 0 0 {name=l12 lab=vcmfb1}
C {devices/lab_wire.sym} -430 0 0 1 {name=l13 lab=vcmfb2}
C {devices/lab_wire.sym} 315 680 0 0 {name=l14 lab=vcmfb2}
C {devices/lab_wire.sym} 665 0 0 0 {name=l15 lab=vcmfb2}
C {devices/lab_wire.sym} -430 260 0 1 {name=l16 lab=vo1n}
C {devices/lab_wire.sym} 370 350 2 0 {name=l17 lab=vo1n}
C {devices/lab_wire.sym} 370 430 0 1 {name=l18 lab=vo1n}
C {devices/lab_wire.sym} 1390 430 0 1 {name=l19 lab=vo1n}
C {devices/lab_wire.sym} -155 350 2 0 {name=l20 lab=vo1p}
C {devices/lab_wire.sym} 665 260 0 0 {name=l21 lab=vo1p}
C {devices/lab_wire.sym} 1100 610 2 0 {name=l22 lab=vo1p}
C {devices/lab_wire.sym} 765 90 2 0 {name=l23 lab=voutn}
C {devices/lab_wire.sym} 715 610 2 0 {name=l24 lab=vref_cm1}
C {devices/lab_wire.sym} -640 610 2 0 {name=l25 lab=vref_cm2}
C {devices/lab_wire.sym} 215 670 0 0 {name=l26 lab=vref_cm2}
C {devices/lab_wire.sym} 50 550 0 0 {name=l27 lab=zc_n}
C {devices/lab_wire.sym} 380 450 2 0 {name=l28 lab=zc_n}
C {devices/lab_wire.sym} 140 330 0 1 {name=l29 lab=zc_p}
C {devices/lab_wire.sym} 1390 610 2 0 {name=l30 lab=zc_p}
C {devices/lab_wire.sym} 825 94 2 0 {name=l31 lab=vdd}
C {devices/lab_wire.sym} -590 94 2 0 {name=l32 lab=vdd}
C {devices/lab_wire.sym} -155 260 0 0 {name=l33 lab=vdd}
C {devices/lab_wire.sym} 430 354 2 0 {name=l34 lab=vdd}
C {devices/lab_wire.sym} 200 94 2 0 {name=l35 lab=vdd}
C {devices/lab_wire.sym} -590 354 2 0 {name=l36 lab=vss}
C {devices/lab_wire.sym} 430 614 2 0 {name=l37 lab=vss}
C {devices/lab_wire.sym} -215 614 2 0 {name=l38 lab=vss}
C {devices/lab_wire.sym} -215 874 2 0 {name=l39 lab=vss}
C {devices/lab_wire.sym} 765 260 0 0 {name=l40 lab=vss}
C {devices/lab_wire.sym} -980 430 0 1 {name=l41 lab=vref_cm1}
C {devices/lab_wire.sym} -980 170 0 1 {name=l42 lab=vref_cm2}
C {devices/lab_wire.sym} -980 870 2 0 {name=l43 lab=vss}
C {devices/lab_wire.sym} -980 610 2 0 {name=l44 lab=vss}
C {devices/lab_wire.sym} -980 350 2 0 {name=l45 lab=vss}
C {devices/lab_wire.sym} -980 690 0 1 {name=l46 lab=vb2}
C {devices/lab_wire.sym} 120 750 0 0 {name=l47 lab=vss}
C {devices/lab_wire.sym} 315 750 0 0 {name=l48 lab=vss}
C {devices/lab_wire.sym} 60 620 0 0 {name=l49 lab=vss}
C {devices/lab_wire.sym} 315 560 0 1 {name=l50 lab=vss}
C {devices/lab_wire.sym} -75 690 0 1 {name=l51 lab=vss}
C {devices/lab_wire.sym} 505 690 0 1 {name=l52 lab=vss}
C {devices/ipin.sym} -85 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} 300 260 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -1040 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1040 920 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 50 330 0 0 {name=p4 lab=voutp}
C {devices/opin.sym} 290 390 0 0 {name=p5 lab=voutn}
