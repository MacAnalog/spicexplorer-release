v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_001_hsu_bandpass_classab} -1980 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -1075 520 1 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} -1385 520 1 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} 580 390 0 0 {name=CF1 value='x_dut_cf1_value'}
C {devices/capa_np.sym} 875 390 0 0 {name=CF2 value='x_dut_cf2_value'}
C {devices/capa_np.sym} -115 520 0 0 {name=CIN1 value='x_dut_cin1_value'}
C {devices/capa_np.sym} 1735 520 0 0 {name=CIN2 value='x_dut_cin2_value'}
C {devices/capa_np.sym} 1955 520 0 0 {name=CISRV value='cin_val'}
C {devices/capa_np.sym} 1095 780 0 0 {name=COSRV value='cout_val'}
C {devices/res_np.sym} 1280 520 1 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} -600 520 1 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} 2115 520 0 0 {name=RISRV value='rin_val'}
C {devices/res_np.sym} -95 390 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 365 390 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} 2720 520 1 0 {name=ROSRV value='rout_val'}
C {devices/vsource_np.sym} -1940 780 0 0 {name=VB1 value="dc {vb1}"}
C {devices/vsource_np.sym} -1940 520 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -1940 260 0 0 {name=VB3 value="dc {vb3}"}
C {devices/vsource_np.sym} -1940 0 0 0 {name=VCMREF value="dc {vcmfb_ref}"}
C {devices/sg13_lv_pmos_np.sym} 415 520 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 2295 520 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -1600 520 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 2475 520 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 915 0 0 1 {name=MO1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo1_w l=x_dut_xmo1_l m=x_dut_xmo1_m}
C {devices/sg13_lv_pmos_np.sym} 725 260 0 1 {name=MO10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo10_w l=x_dut_xmo10_l m=x_dut_xmo10_m}
C {devices/sg13_lv_pmos_np.sym} 1485 260 0 0 {name=MO11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo11_w l=x_dut_xmo11_l m=x_dut_xmo11_m}
C {devices/sg13_lv_pmos_np.sym} 725 0 0 1 {name=MO12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo12_w l=x_dut_xmo12_l m=x_dut_xmo12_m}
C {devices/sg13_lv_pmos_np.sym} 1485 0 0 0 {name=MO13 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo13_w l=x_dut_xmo13_l m=x_dut_xmo13_m}
C {devices/sg13_lv_pmos_np.sym} -760 0 0 1 {name=MO14 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo14_w l=x_dut_xmo14_l m=x_dut_xmo14_m}
C {devices/sg13_lv_nmos_np.sym} -760 260 0 1 {name=MO15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo15_w l=x_dut_xmo15_l m=x_dut_xmo15_m}
C {devices/sg13_lv_nmos_np.sym} 415 0 0 0 {name=MO16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo16_w l=x_dut_xmo16_l m=x_dut_xmo16_m}
C {devices/sg13_lv_pmos_np.sym} -760 520 0 1 {name=MO17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo17_w l=x_dut_xmo17_l m=x_dut_xmo17_m}
C {devices/sg13_lv_pmos_np.sym} 415 260 0 0 {name=MO18 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo18_w l=x_dut_xmo18_l m=x_dut_xmo18_m}
C {devices/sg13_lv_nmos_np.sym} -760 780 0 1 {name=MO19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo19_w l=x_dut_xmo19_l m=x_dut_xmo19_m}
C {devices/sg13_lv_pmos_np.sym} 210 260 0 1 {name=MO2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo2_w l=x_dut_xmo2_l m=x_dut_xmo2_m}
C {devices/sg13_lv_pmos_np.sym} -285 0 0 1 {name=MO20 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo20_w l=x_dut_xmo20_l m=x_dut_xmo20_m}
C {devices/sg13_lv_nmos_np.sym} -285 260 0 1 {name=MO21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo21_w l=x_dut_xmo21_l m=x_dut_xmo21_m}
C {devices/sg13_lv_nmos_np.sym} 220 0 0 0 {name=MO22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo22_w l=x_dut_xmo22_l m=x_dut_xmo22_m}
C {devices/sg13_lv_pmos_np.sym} -285 520 0 1 {name=MO23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo23_w l=x_dut_xmo23_l m=x_dut_xmo23_m}
C {devices/sg13_lv_pmos_np.sym} 1755 260 0 0 {name=MO24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo24_w l=x_dut_xmo24_l m=x_dut_xmo24_m}
C {devices/sg13_lv_nmos_np.sym} -285 780 0 1 {name=MO25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo25_w l=x_dut_xmo25_l m=x_dut_xmo25_m}
C {devices/sg13_lv_pmos_np.sym} 1095 260 0 0 {name=MO3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo3_w l=x_dut_xmo3_l m=x_dut_xmo3_m}
C {devices/sg13_lv_nmos_np.sym} 210 520 0 1 {name=MO4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo4_w l=x_dut_xmo4_l m=x_dut_xmo4_m}
C {devices/sg13_lv_nmos_np.sym} 1095 520 0 0 {name=MO5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo5_w l=x_dut_xmo5_l m=x_dut_xmo5_m}
C {devices/sg13_lv_nmos_np.sym} 725 780 0 1 {name=MO6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo6_w l=x_dut_xmo6_l m=x_dut_xmo6_m}
C {devices/sg13_lv_nmos_np.sym} 725 520 0 1 {name=MO7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo7_w l=x_dut_xmo7_l m=x_dut_xmo7_m}
C {devices/sg13_lv_nmos_np.sym} 1485 780 0 0 {name=MO8 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo8_w l=x_dut_xmo8_l m=x_dut_xmo8_m}
C {devices/sg13_lv_nmos_np.sym} 1485 520 0 0 {name=MO9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo9_w l=x_dut_xmo9_l m=x_dut_xmo9_m}
N -1940 -90 -1940 -30 {}
N -1940 30 -1940 90 {}
N -1940 170 -1940 230 {}
N -1940 290 -1940 350 {}
N -1940 430 -1940 490 {}
N -1940 550 -1940 610 {}
N -1940 690 -1940 750 {}
N -1940 810 -1940 870 {}
N -1620 520 -1620 590 {}
N -1580 430 -1580 490 {}
N -1580 550 -1580 590 {}
N -1520 520 -1520 614 {}
N -1415 460 -1415 520 {}
N -1355 520 -1355 580 {}
N -1105 460 -1105 520 {}
N -1045 520 -1045 580 {}
N -840 0 -840 94 {}
N -840 260 -840 354 {}
N -840 520 -840 614 {}
N -840 780 -840 874 {}
N -780 -140 -780 -30 {}
N -780 30 -780 230 {}
N -780 290 -780 350 {}
N -780 430 -780 490 {}
N -780 550 -780 590 {}
N -780 690 -780 750 {}
N -780 810 -780 920 {}
N -740 190 -740 260 {}
N -740 520 -740 590 {}
N -630 460 -630 520 {}
N -570 520 -570 580 {}
N -365 0 -365 94 {}
N -365 260 -365 354 {}
N -365 520 -365 614 {}
N -365 780 -365 874 {}
N -305 -140 -305 -30 {}
N -305 30 -305 90 {}
N -305 170 -305 230 {}
N -305 290 -305 350 {}
N -305 430 -305 490 {}
N -305 550 -305 590 {}
N -305 690 -305 750 {}
N -305 810 -305 920 {}
N -265 190 -265 260 {}
N -265 520 -265 590 {}
N -235 520 -235 780 {}
N -115 430 -115 490 {}
N -115 550 -115 610 {}
N -95 300 -95 360 {}
N -95 420 -95 450 {}
N 130 260 130 354 {}
N 130 520 130 614 {}
N 190 170 190 230 {}
N 190 290 190 350 {}
N 190 430 190 490 {}
N 190 550 190 920 {}
N 240 -140 240 -30 {}
N 240 30 240 90 {}
N 300 0 300 94 {}
N 395 -60 395 0 {}
N 395 520 395 590 {}
N 435 -140 435 -30 {}
N 435 30 435 90 {}
N 435 170 435 230 {}
N 435 290 435 350 {}
N 435 430 435 490 {}
N 435 550 435 590 {}
N 495 0 495 94 {}
N 495 260 495 354 {}
N 495 520 495 614 {}
N 580 300 580 360 {}
N 580 420 580 480 {}
N 645 0 645 94 {}
N 645 260 645 354 {}
N 645 520 645 614 {}
N 645 780 645 874 {}
N 705 -140 705 -30 {}
N 705 30 705 90 {}
N 705 170 705 230 {}
N 705 290 705 350 {}
N 705 430 705 490 {}
N 705 550 705 610 {}
N 705 690 705 750 {}
N 705 810 705 920 {}
N 745 0 745 60 {}
N 835 0 835 94 {}
N 875 300 875 360 {}
N 875 420 875 450 {}
N 895 -140 895 -30 {}
N 895 30 895 90 {}
N 1045 260 1045 450 {}
N 1075 450 1075 520 {}
N 1095 690 1095 750 {}
N 1095 810 1095 840 {}
N 1115 170 1115 230 {}
N 1115 290 1115 350 {}
N 1115 430 1115 490 {}
N 1115 550 1115 610 {}
N 1175 260 1175 354 {}
N 1175 520 1175 614 {}
N 1220 520 1220 780 {}
N 1310 520 1310 580 {}
N 1465 460 1465 520 {}
N 1505 -140 1505 -30 {}
N 1505 30 1505 90 {}
N 1505 170 1505 230 {}
N 1505 290 1505 350 {}
N 1505 430 1505 490 {}
N 1505 550 1505 610 {}
N 1505 690 1505 750 {}
N 1505 810 1505 920 {}
N 1565 0 1565 94 {}
N 1565 260 1565 354 {}
N 1565 520 1565 614 {}
N 1565 780 1565 874 {}
N 1705 260 1705 580 {}
N 1735 200 1735 260 {}
N 1735 430 1735 490 {}
N 1735 550 1735 610 {}
N 1775 170 1775 230 {}
N 1775 290 1775 920 {}
N 1835 260 1835 354 {}
N 1955 430 1955 490 {}
N 1955 550 1955 610 {}
N 2115 430 2115 490 {}
N 2115 550 2115 610 {}
N 2275 460 2275 590 {}
N 2315 430 2315 490 {}
N 2315 550 2315 590 {}
N 2375 520 2375 614 {}
N 2455 460 2455 590 {}
N 2495 430 2495 490 {}
N 2495 550 2495 590 {}
N 2555 520 2555 614 {}
N 2660 520 2660 840 {}
N 2690 460 2690 520 {}
N 2750 520 2750 580 {}
N 2780 520 2780 580 {}
N -2000 -140 2905 -140 {}
N -840 0 -780 0 {}
N -740 0 -680 0 {}
N -365 0 -305 0 {}
N -265 0 -205 0 {}
N 140 0 200 0 {}
N 240 0 300 0 {}
N 365 0 395 0 {}
N 435 0 495 0 {}
N 645 0 705 0 {}
N 745 0 775 0 {}
N 835 0 895 0 {}
N 935 0 995 0 {}
N 1405 0 1465 0 {}
N 1505 0 1565 0 {}
N -780 190 -740 190 {}
N -305 190 -265 190 {}
N -840 260 -780 260 {}
N -365 260 -305 260 {}
N 130 260 190 260 {}
N 230 260 290 260 {}
N 335 260 395 260 {}
N 435 260 495 260 {}
N 645 260 705 260 {}
N 745 260 805 260 {}
N 1015 260 1075 260 {}
N 1115 260 1175 260 {}
N 1405 260 1465 260 {}
N 1505 260 1565 260 {}
N 1705 260 1735 260 {}
N 1775 260 1835 260 {}
N -95 330 240 330 {}
N 305 360 365 360 {}
N -155 420 -95 420 {}
N 305 420 365 420 {}
N 875 450 1045 450 {}
N 1075 450 1115 450 {}
N -1680 520 -1620 520 {}
N -1580 520 -1520 520 {}
N -1445 520 -1415 520 {}
N -1355 520 -1325 520 {}
N -1135 520 -1105 520 {}
N -1045 520 -1015 520 {}
N -840 520 -780 520 {}
N -660 520 -630 520 {}
N -570 520 -540 520 {}
N -365 520 -305 520 {}
N 130 520 190 520 {}
N 230 520 290 520 {}
N 335 520 395 520 {}
N 435 520 495 520 {}
N 645 520 705 520 {}
N 745 520 805 520 {}
N 1115 520 1175 520 {}
N 1190 520 1250 520 {}
N 1310 520 1340 520 {}
N 1505 520 1565 520 {}
N 2315 520 2375 520 {}
N 2495 520 2555 520 {}
N 2660 520 2690 520 {}
N 2750 520 2780 520 {}
N -1620 590 -1580 590 {}
N -780 590 -740 590 {}
N -305 590 -265 590 {}
N 395 590 435 590 {}
N 2275 590 2315 590 {}
N 2455 590 2495 590 {}
N -840 780 -780 780 {}
N -740 780 -680 780 {}
N -365 780 -305 780 {}
N -265 780 -205 780 {}
N 645 780 705 780 {}
N 745 780 805 780 {}
N 1405 780 1465 780 {}
N 1505 780 1565 780 {}
N 1095 840 2660 840 {}
N -2000 920 2905 920 {}
C {devices/lab_wire.sym} -2000 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -2000 920 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 705 90 2 0 {name=l2 lab=csrc_n}
C {devices/lab_wire.sym} 705 170 0 1 {name=l3 lab=csrc_n}
C {devices/lab_wire.sym} 1505 90 2 0 {name=l4 lab=csrc_p}
C {devices/lab_wire.sym} 1505 170 0 1 {name=l5 lab=csrc_p}
C {devices/lab_wire.sym} 805 780 0 1 {name=l6 lab=dio_n}
C {devices/lab_wire.sym} 1115 430 0 1 {name=l7 lab=dio_n}
C {devices/lab_wire.sym} 1115 350 2 0 {name=l8 lab=dio_n}
C {devices/lab_wire.sym} 190 350 2 0 {name=l9 lab=dio_p}
C {devices/lab_wire.sym} 190 430 0 1 {name=l10 lab=dio_p}
C {devices/lab_wire.sym} 290 520 0 1 {name=l11 lab=dio_p}
C {devices/lab_wire.sym} 1405 780 0 0 {name=l12 lab=dio_p}
C {devices/lab_wire.sym} -1355 580 2 0 {name=l13 lab=flt_n}
C {devices/lab_wire.sym} -305 350 2 0 {name=l14 lab=flt_n}
C {devices/lab_wire.sym} -305 430 0 1 {name=l15 lab=flt_n}
C {devices/lab_wire.sym} -1045 580 2 0 {name=l16 lab=flt_p}
C {devices/lab_wire.sym} -780 350 2 0 {name=l17 lab=flt_p}
C {devices/lab_wire.sym} -780 430 0 1 {name=l18 lab=flt_p}
C {devices/lab_wire.sym} -265 580 2 0 {name=l19 lab=gdn_n}
C {devices/lab_wire.sym} -305 690 0 1 {name=l20 lab=gdn_n}
C {devices/lab_wire.sym} 1735 200 0 1 {name=l21 lab=gdn_n}
C {devices/lab_wire.sym} -740 580 2 0 {name=l22 lab=gdn_p}
C {devices/lab_wire.sym} -780 690 0 1 {name=l23 lab=gdn_p}
C {devices/lab_wire.sym} 335 260 0 0 {name=l24 lab=gdn_p}
C {devices/lab_wire.sym} -305 90 2 0 {name=l25 lab=gup_n}
C {devices/lab_wire.sym} -305 170 0 1 {name=l26 lab=gup_n}
C {devices/lab_wire.sym} 140 0 0 0 {name=l27 lab=gup_n}
C {devices/lab_wire.sym} -780 90 2 0 {name=l28 lab=gup_p}
C {devices/lab_wire.sym} 395 -60 0 1 {name=l29 lab=gup_p}
C {devices/lab_wire.sym} 705 610 2 0 {name=l30 lab=msrc_n}
C {devices/lab_wire.sym} 705 690 0 1 {name=l31 lab=msrc_n}
C {devices/lab_wire.sym} 1505 610 2 0 {name=l32 lab=msrc_p}
C {devices/lab_wire.sym} 1505 690 0 1 {name=l33 lab=msrc_p}
C {devices/lab_wire.sym} -570 580 2 0 {name=l34 lab=out1n}
C {devices/lab_wire.sym} -205 780 0 1 {name=l35 lab=out1n}
C {devices/lab_wire.sym} 705 350 2 0 {name=l36 lab=out1n}
C {devices/lab_wire.sym} 705 430 0 1 {name=l37 lab=out1n}
C {devices/lab_wire.sym} -680 780 0 1 {name=l38 lab=out1p}
C {devices/lab_wire.sym} 1190 520 0 0 {name=l39 lab=out1p}
C {devices/lab_wire.sym} 1505 350 2 0 {name=l40 lab=out1p}
C {devices/lab_wire.sym} 1505 430 0 1 {name=l41 lab=out1p}
C {devices/lab_wire.sym} -1580 430 0 1 {name=l42 lab=pr_mid_n}
C {devices/lab_wire.sym} 2495 430 0 1 {name=l43 lab=pr_mid_n}
C {devices/lab_wire.sym} 435 430 0 1 {name=l44 lab=pr_mid_p}
C {devices/lab_wire.sym} 2315 430 0 1 {name=l45 lab=pr_mid_p}
C {devices/lab_wire.sym} 1015 260 0 0 {name=l46 lab=sum_n}
C {devices/lab_wire.sym} 1735 610 2 0 {name=l47 lab=sum_n}
C {devices/lab_wire.sym} 2455 460 0 1 {name=l48 lab=sum_n}
C {devices/lab_wire.sym} -115 610 2 0 {name=l49 lab=sum_p}
C {devices/lab_wire.sym} 290 260 0 1 {name=l50 lab=sum_p}
C {devices/lab_wire.sym} 335 520 0 0 {name=l51 lab=sum_p}
C {devices/lab_wire.sym} 580 300 0 1 {name=l52 lab=sum_p}
C {devices/lab_wire.sym} 190 170 0 1 {name=l53 lab=tail}
C {devices/lab_wire.sym} 895 90 2 0 {name=l54 lab=tail}
C {devices/lab_wire.sym} 1115 170 0 1 {name=l55 lab=tail}
C {devices/lab_wire.sym} -680 0 0 1 {name=l56 lab=vb1}
C {devices/lab_wire.sym} -205 0 0 1 {name=l57 lab=vb1}
C {devices/lab_wire.sym} 995 0 0 1 {name=l58 lab=vb1}
C {devices/lab_wire.sym} 805 260 0 1 {name=l59 lab=vb2}
C {devices/lab_wire.sym} 1405 260 0 0 {name=l60 lab=vb2}
C {devices/lab_wire.sym} 805 520 0 1 {name=l61 lab=vb3}
C {devices/lab_wire.sym} 1465 460 0 1 {name=l62 lab=vb3}
C {devices/lab_wire.sym} -155 420 0 0 {name=l63 lab=vcm_sense}
C {devices/lab_wire.sym} 305 360 0 0 {name=l64 lab=vcm_sense}
C {devices/lab_wire.sym} 1955 430 0 1 {name=l65 lab=vcm_sense}
C {devices/lab_wire.sym} 2115 430 0 1 {name=l66 lab=vcm_sense}
C {devices/lab_wire.sym} 745 60 2 0 {name=l67 lab=vcmfb}
C {devices/lab_wire.sym} 2690 460 0 1 {name=l68 lab=vcmfb}
C {devices/lab_wire.sym} 1405 0 0 0 {name=l69 lab=vcmfb}
C {devices/lab_wire.sym} 1955 610 2 0 {name=l70 lab=vcmfb_ref}
C {devices/lab_wire.sym} 2115 610 2 0 {name=l71 lab=vcmfb_ref}
C {devices/lab_wire.sym} 2750 580 2 0 {name=l72 lab=vcmfb_ref}
C {devices/lab_wire.sym} -115 430 0 1 {name=l73 lab=vinn}
C {devices/lab_wire.sym} 1735 430 0 1 {name=l74 lab=vinp}
C {devices/lab_wire.sym} -1680 520 0 0 {name=l75 lab=voutn}
C {devices/lab_wire.sym} -95 300 0 1 {name=l76 lab=voutn}
C {devices/lab_wire.sym} 240 90 2 0 {name=l77 lab=voutn}
C {devices/lab_wire.sym} 875 300 0 1 {name=l78 lab=voutn}
C {devices/lab_wire.sym} 1775 170 0 1 {name=l79 lab=voutn}
C {devices/lab_wire.sym} 305 420 0 0 {name=l80 lab=voutp}
C {devices/lab_wire.sym} 435 90 2 0 {name=l81 lab=voutp}
C {devices/lab_wire.sym} 435 170 0 1 {name=l82 lab=voutp}
C {devices/lab_wire.sym} 580 480 2 0 {name=l83 lab=voutp}
C {devices/lab_wire.sym} 2275 460 0 1 {name=l84 lab=voutp}
C {devices/lab_wire.sym} -1415 460 0 1 {name=l85 lab=zc_n}
C {devices/lab_wire.sym} -630 460 0 1 {name=l86 lab=zc_n}
C {devices/lab_wire.sym} -1105 460 0 1 {name=l87 lab=zc_p}
C {devices/lab_wire.sym} 1310 580 2 0 {name=l88 lab=zc_p}
C {devices/lab_wire.sym} -1520 614 2 0 {name=l89 lab=pr_mid_n}
C {devices/lab_wire.sym} 2555 614 2 0 {name=l90 lab=pr_mid_n}
C {devices/lab_wire.sym} 495 614 2 0 {name=l91 lab=pr_mid_p}
C {devices/lab_wire.sym} 2375 614 2 0 {name=l92 lab=pr_mid_p}
C {devices/lab_wire.sym} 835 94 2 0 {name=l93 lab=vdd}
C {devices/lab_wire.sym} 645 354 2 0 {name=l94 lab=vdd}
C {devices/lab_wire.sym} 1565 354 2 0 {name=l95 lab=vdd}
C {devices/lab_wire.sym} 645 94 2 0 {name=l96 lab=vdd}
C {devices/lab_wire.sym} 1565 94 2 0 {name=l97 lab=vdd}
C {devices/lab_wire.sym} -840 94 2 0 {name=l98 lab=vdd}
C {devices/lab_wire.sym} -840 614 2 0 {name=l99 lab=vdd}
C {devices/lab_wire.sym} 495 354 2 0 {name=l100 lab=vdd}
C {devices/lab_wire.sym} 130 354 2 0 {name=l101 lab=vdd}
C {devices/lab_wire.sym} -365 94 2 0 {name=l102 lab=vdd}
C {devices/lab_wire.sym} -365 614 2 0 {name=l103 lab=vdd}
C {devices/lab_wire.sym} 1835 354 2 0 {name=l104 lab=vdd}
C {devices/lab_wire.sym} 1175 354 2 0 {name=l105 lab=vdd}
C {devices/lab_wire.sym} -840 354 2 0 {name=l106 lab=vss}
C {devices/lab_wire.sym} 495 94 2 0 {name=l107 lab=vss}
C {devices/lab_wire.sym} -840 874 2 0 {name=l108 lab=vss}
C {devices/lab_wire.sym} -365 354 2 0 {name=l109 lab=vss}
C {devices/lab_wire.sym} 300 94 2 0 {name=l110 lab=vss}
C {devices/lab_wire.sym} -365 874 2 0 {name=l111 lab=vss}
C {devices/lab_wire.sym} 130 614 2 0 {name=l112 lab=vss}
C {devices/lab_wire.sym} 1175 614 2 0 {name=l113 lab=vss}
C {devices/lab_wire.sym} 645 874 2 0 {name=l114 lab=vss}
C {devices/lab_wire.sym} 645 614 2 0 {name=l115 lab=vss}
C {devices/lab_wire.sym} 1565 874 2 0 {name=l116 lab=vss}
C {devices/lab_wire.sym} 1565 614 2 0 {name=l117 lab=vss}
C {devices/lab_wire.sym} -1940 -90 0 1 {name=l118 lab=vcmfb_ref}
C {devices/lab_wire.sym} -1940 870 2 0 {name=l119 lab=vss}
C {devices/lab_wire.sym} -1940 610 2 0 {name=l120 lab=vss}
C {devices/lab_wire.sym} -1940 350 2 0 {name=l121 lab=vss}
C {devices/lab_wire.sym} -1940 90 2 0 {name=l122 lab=vss}
C {devices/lab_wire.sym} -1940 690 0 1 {name=l123 lab=vb1}
C {devices/lab_wire.sym} -1940 430 0 1 {name=l124 lab=vb2}
C {devices/lab_wire.sym} -1940 170 0 1 {name=l125 lab=vb3}
C {devices/lab_wire.sym} 1095 690 0 1 {name=l126 lab=vss}
C {devices/lab_wire.sym} 435 350 2 0 {name=l127 lab=vss}
C {devices/lab_wire.sym} 1115 610 2 0 {name=l128 lab=vss}
C {devices/iopin.sym} -115 1060 0 0 {name=p0 lab=vinn}
C {devices/iopin.sym} 1735 1060 0 0 {name=p1 lab=vinp}
C {devices/opin.sym} 3045 30 0 0 {name=p2 lab=voutn}
C {devices/opin.sym} 3045 150 0 0 {name=p3 lab=voutp}
B 8 14 442 1681 858 {fill=0}
T {NMOS Simple Current Mirror} 14 424 0 0 0.3 0.3 {layer=8}
B 10 529 442 1291 858 {fill=0}
T {NMOS Simple Current Mirror} 529 424 0 0 0.3 0.3 {layer=10}
B 12 345 442 2483 598 {fill=0}
T {PMOS Series Shared Well Pseudo Resistor} 345 424 0 0 0.3 0.3 {layer=12}
B 21 -1670 442 2663 598 {fill=0}
T {PMOS Series Shared Well Pseudo Resistor} -1670 424 0 0 0.3 0.3 {layer=21}
B 15 14 182 1291 338 {fill=0}
T {PMOS Differential Pair} 14 164 0 0 0.3 0.3 {layer=15}
