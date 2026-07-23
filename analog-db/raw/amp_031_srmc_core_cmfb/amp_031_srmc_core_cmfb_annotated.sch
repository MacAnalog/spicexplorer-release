v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_031_srmc_core_cmfb} -1020 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1230 520 0 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} 10 520 0 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} 580 520 0 0 {name=CIN1 value='cin_val'}
C {devices/capa_np.sym} -480 520 0 0 {name=CIN2 value='cin_val'}
C {devices/capa_np.sym} 40 780 0 0 {name=COUT1 value='cout_val'}
C {devices/capa_np.sym} 200 780 0 0 {name=COUT2 value='cout_val'}
C {devices/res_np.sym} -170 390 1 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} 255 390 1 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} 740 520 0 0 {name=RIN1 value='rin_val'}
C {devices/res_np.sym} -640 520 0 0 {name=RIN2 value='rin_val'}
C {devices/res_np.sym} 1430 520 0 0 {name=RM1N value='x_dut_rm1n_value'}
C {devices/res_np.sym} 955 520 0 0 {name=RM1P value='x_dut_rm1p_value'}
C {devices/res_np.sym} 460 390 1 0 {name=RM2N value='x_dut_rm2n_value'}
C {devices/res_np.sym} 35 390 1 0 {name=RM2P value='x_dut_rm2p_value'}
C {devices/res_np.sym} -140 780 0 0 {name=ROUT1 value='rout_val'}
C {devices/res_np.sym} 405 780 0 0 {name=ROUT2 value='rout_val'}
C {devices/vsource_np.sym} -980 780 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -980 520 0 0 {name=VREF1 value="dc {vref_cm}"}
C {devices/vsource_np.sym} -980 260 0 0 {name=VREF2 value="dc {vref_cm}"}
C {devices/sg13_lv_nmos_np.sym} -510 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 610 0 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 255 520 0 0 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} -170 520 0 1 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} -320 780 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} -170 260 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 255 260 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 40 0 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_nmos_np.sym} 610 260 0 0 {name=M9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -980 170 -980 230 {}
N -980 290 -980 350 {}
N -980 430 -980 490 {}
N -980 550 -980 610 {}
N -980 690 -980 750 {}
N -980 810 -980 870 {}
N -640 430 -640 490 {}
N -640 550 -640 610 {}
N -590 0 -590 94 {}
N -590 260 -590 354 {}
N -530 -140 -530 -30 {}
N -530 30 -530 230 {}
N -530 290 -530 920 {}
N -480 460 -480 490 {}
N -480 550 -480 580 {}
N -300 720 -300 750 {}
N -300 810 -300 920 {}
N -250 260 -250 354 {}
N -250 520 -250 614 {}
N -240 780 -240 874 {}
N -230 200 -230 390 {}
N -190 200 -190 230 {}
N -190 290 -190 350 {}
N -190 430 -190 490 {}
N -190 550 -190 720 {}
N -140 390 -140 450 {}
N -140 690 -140 750 {}
N -140 810 -140 840 {}
N -120 260 -120 520 {}
N -10 0 -10 840 {}
N 10 550 10 610 {}
N 40 690 40 750 {}
N 40 810 40 840 {}
N 60 -140 60 -30 {}
N 60 30 60 200 {}
N 65 330 65 390 {}
N 120 0 120 94 {}
N 200 690 200 750 {}
N 200 810 200 870 {}
N 205 260 205 520 {}
N 275 200 275 230 {}
N 275 290 275 350 {}
N 275 430 275 490 {}
N 275 550 275 610 {}
N 285 390 285 450 {}
N 315 390 315 580 {}
N 335 260 335 354 {}
N 335 520 335 614 {}
N 405 690 405 750 {}
N 405 810 405 840 {}
N 490 330 490 390 {}
N 580 550 580 610 {}
N 630 -140 630 -30 {}
N 630 30 630 230 {}
N 630 290 630 350 {}
N 690 0 690 94 {}
N 690 260 690 354 {}
N 740 430 740 490 {}
N 740 550 740 580 {}
N 955 430 955 490 {}
N 955 550 955 610 {}
N 1230 430 1230 490 {}
N 1230 550 1230 610 {}
N 1430 430 1430 490 {}
N 1430 550 1430 610 {}
N -1040 -140 1680 -140 {}
N -590 0 -530 0 {}
N -490 0 -430 0 {}
N -40 0 20 0 {}
N 60 0 120 0 {}
N 405 0 590 0 {}
N 630 0 690 0 {}
N -530 200 -230 200 {}
N -190 200 275 200 {}
N -590 260 -530 260 {}
N -490 260 -430 260 {}
N -250 260 -190 260 {}
N -150 260 -90 260 {}
N 175 260 235 260 {}
N 275 260 335 260 {}
N 530 260 590 260 {}
N 630 260 690 260 {}
N -230 390 -200 390 {}
N -140 390 -110 390 {}
N -55 390 5 390 {}
N 65 390 95 390 {}
N 165 390 225 390 {}
N 285 390 315 390 {}
N 370 390 430 390 {}
N 490 390 520 390 {}
N -640 460 -480 460 {}
N -50 490 10 490 {}
N 520 490 580 490 {}
N -250 520 -190 520 {}
N -150 520 -120 520 {}
N 205 520 235 520 {}
N 275 520 335 520 {}
N -640 580 -480 580 {}
N 580 580 740 580 {}
N -300 720 -190 720 {}
N -400 780 -340 780 {}
N -300 780 -240 780 {}
N -140 840 40 840 {}
N 200 840 405 840 {}
N -1040 920 1680 920 {}
C {devices/lab_wire.sym} -1040 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1040 920 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 520 490 0 0 {name=l2 lab=cm1_det}
C {devices/lab_wire.sym} 740 430 0 1 {name=l3 lab=cm1_det}
C {devices/lab_wire.sym} 955 430 0 1 {name=l4 lab=cm1_det}
C {devices/lab_wire.sym} 1430 610 2 0 {name=l5 lab=cm1_det}
C {devices/lab_wire.sym} -640 430 0 1 {name=l6 lab=cm2_det}
C {devices/lab_wire.sym} 65 330 0 1 {name=l7 lab=cm2_det}
C {devices/lab_wire.sym} 370 390 0 0 {name=l8 lab=cm2_det}
C {devices/lab_wire.sym} -190 610 2 0 {name=l9 lab=ntail}
C {devices/lab_wire.sym} 275 610 2 0 {name=l10 lab=ntail}
C {devices/lab_wire.sym} 60 90 2 0 {name=l11 lab=ptail}
C {devices/lab_wire.sym} -400 780 0 0 {name=l12 lab=vb2}
C {devices/lab_wire.sym} -40 0 0 0 {name=l13 lab=vcmfb1}
C {devices/lab_wire.sym} -430 0 0 1 {name=l14 lab=vcmfb2}
C {devices/lab_wire.sym} 200 870 2 0 {name=l15 lab=vcmfb2}
C {devices/lab_wire.sym} 530 0 0 0 {name=l16 lab=vcmfb2}
C {devices/lab_wire.sym} -90 260 0 1 {name=l17 lab=vinn}
C {devices/lab_wire.sym} 175 260 0 0 {name=l18 lab=vinp}
C {devices/lab_wire.sym} -430 260 0 1 {name=l19 lab=vo1n}
C {devices/lab_wire.sym} 275 350 2 0 {name=l20 lab=vo1n}
C {devices/lab_wire.sym} 275 430 0 1 {name=l21 lab=vo1n}
C {devices/lab_wire.sym} 1230 430 0 1 {name=l22 lab=vo1n}
C {devices/lab_wire.sym} 1430 430 0 1 {name=l23 lab=vo1n}
C {devices/lab_wire.sym} -190 350 2 0 {name=l24 lab=vo1p}
C {devices/lab_wire.sym} -190 430 0 1 {name=l25 lab=vo1p}
C {devices/lab_wire.sym} -50 490 0 0 {name=l26 lab=vo1p}
C {devices/lab_wire.sym} 530 260 0 0 {name=l27 lab=vo1p}
C {devices/lab_wire.sym} 955 610 2 0 {name=l28 lab=vo1p}
C {devices/lab_wire.sym} 165 390 0 0 {name=l29 lab=voutn}
C {devices/lab_wire.sym} 490 330 0 1 {name=l30 lab=voutn}
C {devices/lab_wire.sym} 630 90 2 0 {name=l31 lab=voutn}
C {devices/lab_wire.sym} -530 90 2 0 {name=l32 lab=voutp}
C {devices/lab_wire.sym} -55 390 0 0 {name=l33 lab=voutp}
C {devices/lab_wire.sym} 580 610 2 0 {name=l34 lab=vref_cm1}
C {devices/lab_wire.sym} -640 610 2 0 {name=l35 lab=vref_cm2}
C {devices/lab_wire.sym} 10 610 2 0 {name=l36 lab=zc_n}
C {devices/lab_wire.sym} 285 450 2 0 {name=l37 lab=zc_n}
C {devices/lab_wire.sym} -140 450 2 0 {name=l38 lab=zc_p}
C {devices/lab_wire.sym} 1230 610 2 0 {name=l39 lab=zc_p}
C {devices/lab_wire.sym} 690 94 2 0 {name=l40 lab=vdd}
C {devices/lab_wire.sym} -590 94 2 0 {name=l41 lab=vdd}
C {devices/lab_wire.sym} -250 354 2 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} 335 354 2 0 {name=l43 lab=vdd}
C {devices/lab_wire.sym} 120 94 2 0 {name=l44 lab=vdd}
C {devices/lab_wire.sym} -590 354 2 0 {name=l45 lab=vss}
C {devices/lab_wire.sym} 335 614 2 0 {name=l46 lab=vss}
C {devices/lab_wire.sym} -250 614 2 0 {name=l47 lab=vss}
C {devices/lab_wire.sym} -240 874 2 0 {name=l48 lab=vss}
C {devices/lab_wire.sym} 690 354 2 0 {name=l49 lab=vss}
C {devices/lab_wire.sym} -980 430 0 1 {name=l50 lab=vref_cm1}
C {devices/lab_wire.sym} -980 170 0 1 {name=l51 lab=vref_cm2}
C {devices/lab_wire.sym} -980 870 2 0 {name=l52 lab=vss}
C {devices/lab_wire.sym} -980 610 2 0 {name=l53 lab=vss}
C {devices/lab_wire.sym} -980 350 2 0 {name=l54 lab=vss}
C {devices/lab_wire.sym} -980 690 0 1 {name=l55 lab=vb2}
C {devices/lab_wire.sym} 40 690 0 1 {name=l56 lab=vss}
C {devices/lab_wire.sym} 200 690 0 1 {name=l57 lab=vss}
C {devices/lab_wire.sym} -140 690 0 1 {name=l58 lab=vss}
C {devices/lab_wire.sym} 405 690 0 1 {name=l59 lab=vss}
C {devices/lab_wire.sym} 630 350 2 0 {name=l60 lab=vss}
C {devices/ipin.sym} -1180 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -1180 380 0 0 {name=p1 lab=vinp}
C {devices/opin.sym} 1820 30 0 0 {name=p2 lab=voutp}
C {devices/opin.sym} 1820 150 0 0 {name=p3 lab=voutn}
B 8 -358 442 443 598 {fill=0}
T {NMOS Differential Pair} -358 424 0 0 0.3 0.3 {layer=8}
B 10 -358 182 443 338 {fill=0}
T {PMOS Differential Pair} -358 164 0 0 0.3 0.3 {layer=10}
