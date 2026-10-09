v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_001_hsu_bandpass_classab} -1980 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -1070 520 1 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} -1380 520 1 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} 700 390 0 0 {name=CF1 value='x_dut_cf1_value'}
C {devices/capa_np.sym} 950 390 0 0 {name=CF2 value='x_dut_cf2_value'}
C {devices/capa_np.sym} 40 520 0 0 {name=CIN1 value='x_dut_cin1_value'}
C {devices/capa_np.sym} 2210 520 0 0 {name=CIN2 value='x_dut_cin2_value'}
C {devices/capa_np.sym} 2470 520 0 0 {name=CISRV value='cin_val'}
C {devices/capa_np.sym} 1490 780 0 0 {name=COSRV value='cout_val'}
C {devices/vccs.sym} 1160 650 1 0 {name=GSRV value="\{gm_val\}"}
C {devices/res_np.sym} 1720 520 1 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} -520 520 1 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} 3140 520 0 0 {name=RISRV value='rin_val'}
C {devices/res_np.sym} 450 390 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 1385 390 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} 3330 520 0 0 {name=ROSRV value='rout_val'}
C {devices/vsource_np.sym} -1940 780 0 0 {name=VB1 value="dc \{vb1\}" savecurrent=false}
C {devices/vsource_np.sym} -1940 520 0 0 {name=VB2 value="dc \{vb2\}" savecurrent=false}
C {devices/vsource_np.sym} -1940 260 0 0 {name=VB3 value="dc \{vb3\}" savecurrent=false}
C {devices/vsource_np.sym} -1940 0 0 0 {name=VCMREF value="dc \{vcmfb_ref\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 700 520 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 2655 520 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} 2870 520 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -1600 520 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 1310 0 0 1 {name=MO1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo1_w l=x_dut_xmo1_l m=x_dut_xmo1_m}
C {devices/sg13_lv_pmos_np.sym} 1085 260 0 1 {name=MO10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo10_w l=x_dut_xmo10_l m=x_dut_xmo10_m}
C {devices/sg13_lv_pmos_np.sym} 1960 260 0 0 {name=MO11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo11_w l=x_dut_xmo11_l m=x_dut_xmo11_m}
C {devices/sg13_lv_pmos_np.sym} 1085 0 0 1 {name=MO12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo12_w l=x_dut_xmo12_l m=x_dut_xmo12_m}
C {devices/sg13_lv_pmos_np.sym} 1960 0 0 0 {name=MO13 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo13_w l=x_dut_xmo13_l m=x_dut_xmo13_m}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=MO14 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo14_w l=x_dut_xmo14_l m=x_dut_xmo14_m}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=MO15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo15_w l=x_dut_xmo15_l m=x_dut_xmo15_m}
C {devices/sg13_lv_nmos_np.sym} 700 0 0 0 {name=MO16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo16_w l=x_dut_xmo16_l m=x_dut_xmo16_m}
C {devices/sg13_lv_pmos_np.sym} -680 520 0 1 {name=MO17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo17_w l=x_dut_xmo17_l m=x_dut_xmo17_m}
C {devices/sg13_lv_pmos_np.sym} 700 260 0 0 {name=MO18 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo18_w l=x_dut_xmo18_l m=x_dut_xmo18_m}
C {devices/sg13_lv_nmos_np.sym} -680 780 0 1 {name=MO19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo19_w l=x_dut_xmo19_l m=x_dut_xmo19_m}
C {devices/sg13_lv_pmos_np.sym} 440 260 0 1 {name=MO2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo2_w l=x_dut_xmo2_l m=x_dut_xmo2_m}
C {devices/sg13_lv_pmos_np.sym} -130 0 0 1 {name=MO20 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo20_w l=x_dut_xmo20_l m=x_dut_xmo20_m}
C {devices/sg13_lv_nmos_np.sym} -130 260 0 1 {name=MO21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo21_w l=x_dut_xmo21_l m=x_dut_xmo21_m}
C {devices/sg13_lv_nmos_np.sym} 450 0 0 0 {name=MO22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo22_w l=x_dut_xmo22_l m=x_dut_xmo22_m}
C {devices/sg13_lv_pmos_np.sym} -130 520 0 1 {name=MO23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo23_w l=x_dut_xmo23_l m=x_dut_xmo23_m}
C {devices/sg13_lv_pmos_np.sym} 2230 260 0 0 {name=MO24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo24_w l=x_dut_xmo24_l m=x_dut_xmo24_m}
C {devices/sg13_lv_nmos_np.sym} -130 780 0 1 {name=MO25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo25_w l=x_dut_xmo25_l m=x_dut_xmo25_m}
C {devices/sg13_lv_pmos_np.sym} 1490 260 0 0 {name=MO3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo3_w l=x_dut_xmo3_l m=x_dut_xmo3_m}
C {devices/sg13_lv_nmos_np.sym} 440 520 0 1 {name=MO4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo4_w l=x_dut_xmo4_l m=x_dut_xmo4_m}
C {devices/sg13_lv_nmos_np.sym} 1490 520 0 0 {name=MO5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo5_w l=x_dut_xmo5_l m=x_dut_xmo5_m}
C {devices/sg13_lv_nmos_np.sym} 1085 780 0 1 {name=MO6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo6_w l=x_dut_xmo6_l m=x_dut_xmo6_m}
C {devices/sg13_lv_nmos_np.sym} 1085 520 0 1 {name=MO7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo7_w l=x_dut_xmo7_l m=x_dut_xmo7_m}
C {devices/sg13_lv_nmos_np.sym} 1960 780 0 0 {name=MO8 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo8_w l=x_dut_xmo8_l m=x_dut_xmo8_m}
C {devices/sg13_lv_nmos_np.sym} 1960 520 0 0 {name=MO9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo9_w l=x_dut_xmo9_l m=x_dut_xmo9_m}
N -1940 -90 -1940 -30 {}
N -1940 30 -1940 90 {}
N -1940 170 -1940 230 {}
N -1940 290 -1940 350 {}
N -1940 430 -1940 490 {}
N -1940 550 -1940 610 {}
N -1940 690 -1940 750 {}
N -1940 810 -1940 870 {}
N -1620 460 -1620 590 {}
N -1580 430 -1580 490 {}
N -1580 550 -1580 590 {}
N -1520 520 -1520 614 {}
N -1350 520 -1350 580 {}
N -1040 520 -1040 580 {}
N -760 0 -760 94 {}
N -760 320 -760 490 {}
N -760 550 -760 720 {}
N -760 780 -760 874 {}
N -700 -140 -700 -30 {}
N -700 30 -700 230 {}
N -700 290 -700 350 {}
N -700 550 -700 590 {}
N -700 720 -700 750 {}
N -700 810 -700 920 {}
N -660 0 -660 60 {}
N -660 190 -660 260 {}
N -660 520 -660 590 {}
N -660 780 -660 840 {}
N -630 -60 -630 0 {}
N -490 520 -490 580 {}
N -210 30 -210 200 {}
N -210 320 -210 490 {}
N -210 550 -210 720 {}
N -210 780 -210 874 {}
N -150 -140 -150 -30 {}
N -150 30 -150 90 {}
N -150 190 -150 230 {}
N -150 290 -150 350 {}
N -150 550 -150 590 {}
N -150 720 -150 750 {}
N -150 810 -150 920 {}
N -110 190 -110 260 {}
N -110 520 -110 590 {}
N -80 -60 -80 0 {}
N 40 430 40 490 {}
N 40 550 40 610 {}
N 360 320 360 490 {}
N 360 520 360 614 {}
N 390 30 390 330 {}
N 390 420 390 610 {}
N 420 200 420 230 {}
N 420 290 420 350 {}
N 420 550 420 920 {}
N 450 330 450 360 {}
N 460 520 460 900 {}
N 470 -140 470 -30 {}
N 470 30 470 90 {}
N 520 490 520 520 {}
N 530 0 530 94 {}
N 680 520 680 590 {}
N 700 300 700 360 {}
N 700 420 700 480 {}
N 720 -140 720 -30 {}
N 720 30 720 90 {}
N 720 170 720 230 {}
N 720 290 720 350 {}
N 720 430 720 490 {}
N 720 550 720 590 {}
N 780 0 780 94 {}
N 780 260 780 354 {}
N 780 520 780 614 {}
N 950 300 950 360 {}
N 950 420 950 480 {}
N 1005 0 1005 94 {}
N 1005 260 1005 354 {}
N 1005 520 1005 614 {}
N 1005 780 1005 874 {}
N 1040 650 1040 840 {}
N 1065 -140 1065 -30 {}
N 1065 30 1065 90 {}
N 1065 170 1065 230 {}
N 1065 290 1065 350 {}
N 1065 430 1065 490 {}
N 1065 690 1065 750 {}
N 1065 810 1065 920 {}
N 1190 650 1190 920 {}
N 1230 30 1230 200 {}
N 1290 -140 1290 -30 {}
N 1290 30 1290 90 {}
N 1310 320 1310 490 {}
N 1350 30 1350 200 {}
N 1360 -60 1360 0 {}
N 1385 330 1385 360 {}
N 1430 0 1430 840 {}
N 1470 450 1470 520 {}
N 1490 690 1490 750 {}
N 1490 810 1490 840 {}
N 1510 200 1510 230 {}
N 1510 290 1510 350 {}
N 1510 450 1510 490 {}
N 1510 550 1510 920 {}
N 1570 260 1570 354 {}
N 1570 520 1570 614 {}
N 1750 520 1750 580 {}
N 1910 780 1910 900 {}
N 1920 30 1920 200 {}
N 1980 -140 1980 -30 {}
N 1980 30 1980 90 {}
N 1980 200 1980 230 {}
N 1980 290 1980 350 {}
N 1980 720 1980 750 {}
N 1980 810 1980 920 {}
N 2040 0 2040 94 {}
N 2040 320 2040 490 {}
N 2040 550 2040 720 {}
N 2040 780 2040 874 {}
N 2210 430 2210 490 {}
N 2250 200 2250 230 {}
N 2250 290 2250 920 {}
N 2310 260 2310 354 {}
N 2470 430 2470 490 {}
N 2470 550 2470 580 {}
N 2470 580 2470 610 {}
N 2530 580 2530 610 {}
N 2635 520 2635 590 {}
N 2675 430 2675 490 {}
N 2675 550 2675 590 {}
N 2735 520 2735 614 {}
N 2850 520 2850 590 {}
N 2890 430 2890 490 {}
N 2890 550 2890 590 {}
N 2950 520 2950 614 {}
N 3140 430 3140 490 {}
N 3140 550 3140 580 {}
N 3330 430 3330 490 {}
N 3330 550 3330 840 {}
N -2000 -140 3590 -140 {}
N -630 -60 1360 -60 {}
N -760 0 -700 0 {}
N -660 0 -630 0 {}
N -110 0 -80 0 {}
N 370 0 430 0 {}
N 470 0 530 0 {}
N 620 0 680 0 {}
N 720 0 780 0 {}
N 1005 0 1065 0 {}
N 1105 0 1165 0 {}
N 1330 0 1360 0 {}
N 1430 0 1940 0 {}
N 1980 0 2040 0 {}
N -210 30 -150 30 {}
N 390 30 470 30 {}
N 1230 30 1350 30 {}
N 1920 30 1980 30 {}
N -700 190 -660 190 {}
N -150 190 -110 190 {}
N -210 200 -150 200 {}
N 420 200 1510 200 {}
N 1920 200 1980 200 {}
N 460 260 520 260 {}
N 620 260 680 260 {}
N 720 260 780 260 {}
N 1005 260 1065 260 {}
N 1105 260 1165 260 {}
N 1410 260 1470 260 {}
N 1510 260 1570 260 {}
N 1910 260 1940 260 {}
N 2150 260 2210 260 {}
N 2250 260 2310 260 {}
N -760 320 -700 320 {}
N -210 320 -150 320 {}
N 360 320 420 320 {}
N 1310 320 1510 320 {}
N 1980 320 2040 320 {}
N 390 330 450 330 {}
N 1325 360 1385 360 {}
N 390 420 450 420 {}
N 1325 420 1385 420 {}
N 1470 450 1510 450 {}
N -760 490 -700 490 {}
N -210 490 -150 490 {}
N 360 490 520 490 {}
N 1310 490 1510 490 {}
N 1980 490 2040 490 {}
N -1580 520 -1520 520 {}
N -1470 520 -1410 520 {}
N -1350 520 -1320 520 {}
N -1160 520 -1100 520 {}
N -1040 520 -1010 520 {}
N -610 520 -550 520 {}
N -490 520 -460 520 {}
N 360 520 420 520 {}
N 460 520 520 520 {}
N 620 520 680 520 {}
N 720 520 780 520 {}
N 1005 520 1065 520 {}
N 1105 520 1165 520 {}
N 1510 520 1570 520 {}
N 1630 520 1690 520 {}
N 1750 520 1780 520 {}
N 1880 520 1940 520 {}
N 2675 520 2735 520 {}
N 2790 520 2850 520 {}
N 2890 520 2950 520 {}
N -760 550 -700 550 {}
N -210 550 -150 550 {}
N 1980 550 2040 550 {}
N 2410 580 3140 580 {}
N -1620 590 -1580 590 {}
N -700 590 -660 590 {}
N -150 590 -110 590 {}
N 680 590 720 590 {}
N 2635 590 2675 590 {}
N 2850 590 2890 590 {}
N 390 610 1140 610 {}
N 1180 610 2530 610 {}
N 1040 650 1130 650 {}
N -760 720 -700 720 {}
N -210 720 -150 720 {}
N 1980 720 2040 720 {}
N -760 780 -700 780 {}
N -660 780 -630 780 {}
N -210 780 -150 780 {}
N -110 780 -50 780 {}
N 1005 780 1065 780 {}
N 1105 780 1165 780 {}
N 1910 780 1940 780 {}
N 1980 780 2040 780 {}
N 1040 840 3330 840 {}
N 460 900 1910 900 {}
N -2000 920 3590 920 {}
C {devices/lab_wire.sym} 1065 90 2 0 {name=l0 lab=csrc_n}
C {devices/lab_wire.sym} 1065 170 0 1 {name=l1 lab=csrc_n}
C {devices/lab_wire.sym} 1980 90 2 0 {name=l2 lab=csrc_p}
C {devices/lab_wire.sym} 1165 780 0 1 {name=l3 lab=dio_n}
C {devices/lab_wire.sym} 1510 350 2 0 {name=l4 lab=dio_n}
C {devices/lab_wire.sym} 420 350 2 0 {name=l5 lab=dio_p}
C {devices/lab_wire.sym} -1350 580 2 0 {name=l6 lab=flt_n}
C {devices/lab_wire.sym} -150 350 2 0 {name=l7 lab=flt_n}
C {devices/lab_wire.sym} -1040 580 2 0 {name=l8 lab=flt_p}
C {devices/lab_wire.sym} -700 350 2 0 {name=l9 lab=flt_p}
C {devices/lab_wire.sym} -110 580 2 0 {name=l10 lab=gdn_n}
C {devices/lab_wire.sym} 2150 260 0 0 {name=l11 lab=gdn_n}
C {devices/lab_wire.sym} -660 580 2 0 {name=l12 lab=gdn_p}
C {devices/lab_wire.sym} 620 260 0 0 {name=l13 lab=gdn_p}
C {devices/lab_wire.sym} -150 90 2 0 {name=l14 lab=gup_n}
C {devices/lab_wire.sym} 370 0 0 0 {name=l15 lab=gup_n}
C {devices/lab_wire.sym} -700 90 2 0 {name=l16 lab=gup_p}
C {devices/lab_wire.sym} 620 0 0 0 {name=l17 lab=gup_p}
C {devices/lab_wire.sym} 1065 550 0 0 {name=l18 lab=msrc_n}
C {devices/lab_wire.sym} 1065 690 0 1 {name=l19 lab=msrc_n}
C {devices/lab_wire.sym} 1980 550 0 0 {name=l20 lab=msrc_p}
C {devices/lab_wire.sym} -490 580 2 0 {name=l21 lab=out1n}
C {devices/lab_wire.sym} -50 780 0 1 {name=l22 lab=out1n}
C {devices/lab_wire.sym} 1065 350 2 0 {name=l23 lab=out1n}
C {devices/lab_wire.sym} 1065 430 0 1 {name=l24 lab=out1n}
C {devices/lab_wire.sym} -660 840 2 0 {name=l25 lab=out1p}
C {devices/lab_wire.sym} 1630 520 0 0 {name=l26 lab=out1p}
C {devices/lab_wire.sym} 1980 350 2 0 {name=l27 lab=out1p}
C {devices/lab_wire.sym} -1580 430 0 1 {name=l28 lab=pr_mid_n}
C {devices/lab_wire.sym} 2890 430 0 1 {name=l29 lab=pr_mid_n}
C {devices/lab_wire.sym} 720 430 0 1 {name=l30 lab=pr_mid_p}
C {devices/lab_wire.sym} 2675 430 0 1 {name=l31 lab=pr_mid_p}
C {devices/lab_wire.sym} -1620 460 0 1 {name=l32 lab=sum_n}
C {devices/lab_wire.sym} 950 480 2 0 {name=l33 lab=sum_n}
C {devices/lab_wire.sym} 1410 260 0 0 {name=l34 lab=sum_n}
C {devices/lab_wire.sym} 2210 550 0 0 {name=l35 lab=sum_n}
C {devices/lab_wire.sym} 40 610 2 0 {name=l36 lab=sum_p}
C {devices/lab_wire.sym} 520 260 0 1 {name=l37 lab=sum_p}
C {devices/lab_wire.sym} 620 520 0 0 {name=l38 lab=sum_p}
C {devices/lab_wire.sym} 700 300 0 1 {name=l39 lab=sum_p}
C {devices/lab_wire.sym} 1290 90 2 0 {name=l40 lab=tail}
C {devices/lab_wire.sym} -660 60 2 0 {name=l41 lab=vb1}
C {devices/lab_wire.sym} 1165 260 0 1 {name=l42 lab=vb2}
C {devices/lab_wire.sym} 1940 260 0 0 {name=l43 lab=vb2}
C {devices/lab_wire.sym} 1165 520 0 1 {name=l44 lab=vb3}
C {devices/lab_wire.sym} 1880 520 0 0 {name=l45 lab=vb3}
C {devices/lab_wire.sym} 390 420 0 0 {name=l46 lab=vcm_sense}
C {devices/lab_wire.sym} 1325 360 0 0 {name=l47 lab=vcm_sense}
C {devices/lab_wire.sym} 2470 430 0 1 {name=l48 lab=vcm_sense}
C {devices/lab_wire.sym} 3140 430 0 1 {name=l49 lab=vcm_sense}
C {devices/lab_wire.sym} 1165 0 0 1 {name=l50 lab=vcmfb}
C {devices/lab_wire.sym} 1880 0 0 0 {name=l51 lab=vcmfb}
C {devices/lab_wire.sym} 2470 610 2 0 {name=l52 lab=vcmfb_ref}
C {devices/lab_wire.sym} 3330 430 0 1 {name=l53 lab=vcmfb_ref}
C {devices/lab_wire.sym} 40 430 0 1 {name=l54 lab=vinn}
C {devices/lab_wire.sym} 2210 430 0 1 {name=l55 lab=vinp}
C {devices/lab_wire.sym} 470 90 2 0 {name=l56 lab=voutn}
C {devices/lab_wire.sym} 950 300 0 1 {name=l57 lab=voutn}
C {devices/lab_wire.sym} 2790 520 0 0 {name=l58 lab=voutn}
C {devices/lab_wire.sym} 700 480 2 0 {name=l59 lab=voutp}
C {devices/lab_wire.sym} 720 90 2 0 {name=l60 lab=voutp}
C {devices/lab_wire.sym} 720 170 0 1 {name=l61 lab=voutp}
C {devices/lab_wire.sym} 1325 420 0 0 {name=l62 lab=voutp}
C {devices/lab_wire.sym} -1470 520 0 0 {name=l63 lab=zc_n}
C {devices/lab_wire.sym} -610 520 0 0 {name=l64 lab=zc_n}
C {devices/lab_wire.sym} -1160 520 0 0 {name=l65 lab=zc_p}
C {devices/lab_wire.sym} 1750 580 2 0 {name=l66 lab=zc_p}
C {devices/lab_wire.sym} 2950 614 2 0 {name=l67 lab=pr_mid_n}
C {devices/lab_wire.sym} -1520 614 2 0 {name=l68 lab=pr_mid_n}
C {devices/lab_wire.sym} 780 614 2 0 {name=l69 lab=pr_mid_p}
C {devices/lab_wire.sym} 2735 614 2 0 {name=l70 lab=pr_mid_p}
C {devices/lab_wire.sym} 1290 0 0 0 {name=l71 lab=vdd}
C {devices/lab_wire.sym} 1005 354 2 0 {name=l72 lab=vdd}
C {devices/lab_wire.sym} 1980 260 0 0 {name=l73 lab=vdd}
C {devices/lab_wire.sym} 1005 94 2 0 {name=l74 lab=vdd}
C {devices/lab_wire.sym} 2040 94 2 0 {name=l75 lab=vdd}
C {devices/lab_wire.sym} -760 94 2 0 {name=l76 lab=vdd}
C {devices/lab_wire.sym} -700 520 0 0 {name=l77 lab=vdd}
C {devices/lab_wire.sym} 780 354 2 0 {name=l78 lab=vdd}
C {devices/lab_wire.sym} 420 260 0 0 {name=l79 lab=vdd}
C {devices/lab_wire.sym} -150 0 0 0 {name=l80 lab=vdd}
C {devices/lab_wire.sym} -150 520 0 0 {name=l81 lab=vdd}
C {devices/lab_wire.sym} 2310 354 2 0 {name=l82 lab=vdd}
C {devices/lab_wire.sym} 1570 354 2 0 {name=l83 lab=vdd}
C {devices/lab_wire.sym} -700 260 0 0 {name=l84 lab=vss}
C {devices/lab_wire.sym} 780 94 2 0 {name=l85 lab=vss}
C {devices/lab_wire.sym} -760 874 2 0 {name=l86 lab=vss}
C {devices/lab_wire.sym} -150 260 0 0 {name=l87 lab=vss}
C {devices/lab_wire.sym} 530 94 2 0 {name=l88 lab=vss}
C {devices/lab_wire.sym} -210 874 2 0 {name=l89 lab=vss}
C {devices/lab_wire.sym} 360 614 2 0 {name=l90 lab=vss}
C {devices/lab_wire.sym} 1570 614 2 0 {name=l91 lab=vss}
C {devices/lab_wire.sym} 1005 874 2 0 {name=l92 lab=vss}
C {devices/lab_wire.sym} 1005 614 2 0 {name=l93 lab=vss}
C {devices/lab_wire.sym} 2040 874 2 0 {name=l94 lab=vss}
C {devices/lab_wire.sym} 1980 520 0 0 {name=l95 lab=vss}
C {devices/lab_wire.sym} -1940 -90 0 1 {name=l96 lab=vcmfb_ref}
C {devices/lab_wire.sym} -1940 870 2 0 {name=l97 lab=vss}
C {devices/lab_wire.sym} -1940 610 2 0 {name=l98 lab=vss}
C {devices/lab_wire.sym} -1940 350 2 0 {name=l99 lab=vss}
C {devices/lab_wire.sym} -1940 90 2 0 {name=l100 lab=vss}
C {devices/lab_wire.sym} -1940 690 0 1 {name=l101 lab=vb1}
C {devices/lab_wire.sym} -1940 430 0 1 {name=l102 lab=vb2}
C {devices/lab_wire.sym} -1940 170 0 1 {name=l103 lab=vb3}
C {devices/lab_wire.sym} 1490 690 0 1 {name=l104 lab=vss}
C {devices/lab_wire.sym} 720 350 2 0 {name=l105 lab=vss}
C {devices/iopin.sym} -2000 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -2000 920 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 2250 200 0 0 {name=p2 lab=voutn}
C {devices/opin.sym} 2675 590 0 0 {name=p3 lab=voutp}
C {devices/iopin.sym} 40 1060 0 0 {name=p4 lab=vinn}
C {devices/iopin.sym} 2210 1060 0 0 {name=p5 lab=vinp}
B 8 -40 442 2440 858 {fill=0}
T {NMOS Simple Current Mirror} -40 424 0 0 0.3 0.3 {layer=8}
B 10 605 442 1970 858 {fill=0}
T {NMOS Simple Current Mirror} 605 424 0 0 0.3 0.3 {layer=10}
B 12 630 442 3111 598 {fill=0}
T {PMOS Series Shared Well Pseudo Resistor} 630 400 0 0 0.3 0.3 {layer=12}
B 21 -1670 442 3326 598 {fill=0}
T {PMOS Series Shared Well Pseudo Resistor} -1670 424 0 0 0.3 0.3 {layer=21}
B 15 -40 182 1970 338 {fill=0}
T {PMOS Differential Pair} -40 164 0 0 0.3 0.3 {layer=15}
