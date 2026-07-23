v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_001_hsu_bandpass_classab} -2140 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -1045 520 1 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} -1355 520 1 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} 325 390 0 0 {name=CF1 value='x_dut_cf1_value'}
C {devices/capa_np.sym} 535 390 0 0 {name=CF2 value='x_dut_cf2_value'}
C {devices/capa_np.sym} 325 520 0 0 {name=CIN1 value='x_dut_cin1_value'}
C {devices/capa_np.sym} 1730 520 0 0 {name=CIN2 value='x_dut_cin2_value'}
C {devices/capa_np.sym} 1950 520 0 0 {name=CISRV value='cin_val'}
C {devices/capa_np.sym} 1250 780 0 0 {name=COSRV value='cout_val'}
C {devices/res_np.sym} 1260 520 1 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} -555 520 1 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} 2110 520 0 0 {name=RISRV value='rin_val'}
C {devices/res_np.sym} 110 390 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 800 390 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} 820 520 1 0 {name=ROSRV value='rout_val'}
C {devices/vsource_np.sym} -2100 780 0 0 {name=VB1 value="dc {vb1}"}
C {devices/vsource_np.sym} -2100 520 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -2100 260 0 0 {name=VB3 value="dc {vb3}"}
C {devices/vsource_np.sym} -2100 0 0 0 {name=VCMREF value="dc {vcmfb_ref}"}
C {devices/sg13_lv_pmos_np.sym} 2270 520 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -1580 520 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} 2450 520 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -1760 520 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 325 0 0 0 {name=MO1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo1_w l=x_dut_xmo1_l m=x_dut_xmo1_m}
C {devices/sg13_lv_pmos_np.sym} 1080 260 0 1 {name=MO10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo10_w l=x_dut_xmo10_l m=x_dut_xmo10_m}
C {devices/sg13_lv_pmos_np.sym} 1460 260 0 0 {name=MO11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo11_w l=x_dut_xmo11_l m=x_dut_xmo11_m}
C {devices/sg13_lv_pmos_np.sym} 1080 0 0 1 {name=MO12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo12_w l=x_dut_xmo12_l m=x_dut_xmo12_m}
C {devices/sg13_lv_pmos_np.sym} 1460 0 0 0 {name=MO13 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo13_w l=x_dut_xmo13_l m=x_dut_xmo13_m}
C {devices/sg13_lv_pmos_np.sym} -730 0 0 1 {name=MO14 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo14_w l=x_dut_xmo14_l m=x_dut_xmo14_m}
C {devices/sg13_lv_nmos_np.sym} -730 260 0 1 {name=MO15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo15_w l=x_dut_xmo15_l m=x_dut_xmo15_m}
C {devices/sg13_lv_nmos_np.sym} 535 0 0 0 {name=MO16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo16_w l=x_dut_xmo16_l m=x_dut_xmo16_m}
C {devices/sg13_lv_pmos_np.sym} -730 520 0 1 {name=MO17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo17_w l=x_dut_xmo17_l m=x_dut_xmo17_m}
C {devices/sg13_lv_pmos_np.sym} 325 260 0 0 {name=MO18 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo18_w l=x_dut_xmo18_l m=x_dut_xmo18_m}
C {devices/sg13_lv_nmos_np.sym} -730 780 0 1 {name=MO19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo19_w l=x_dut_xmo19_l m=x_dut_xmo19_m}
C {devices/sg13_lv_pmos_np.sym} 100 260 0 1 {name=MO2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo2_w l=x_dut_xmo2_l m=x_dut_xmo2_m}
C {devices/sg13_lv_pmos_np.sym} -240 0 0 1 {name=MO20 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo20_w l=x_dut_xmo20_l m=x_dut_xmo20_m}
C {devices/sg13_lv_nmos_np.sym} -240 260 0 1 {name=MO21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo21_w l=x_dut_xmo21_l m=x_dut_xmo21_m}
C {devices/sg13_lv_nmos_np.sym} 110 0 0 0 {name=MO22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo22_w l=x_dut_xmo22_l m=x_dut_xmo22_m}
C {devices/sg13_lv_pmos_np.sym} -240 520 0 1 {name=MO23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo23_w l=x_dut_xmo23_l m=x_dut_xmo23_m}
C {devices/sg13_lv_pmos_np.sym} 1730 260 0 0 {name=MO24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo24_w l=x_dut_xmo24_l m=x_dut_xmo24_m}
C {devices/sg13_lv_nmos_np.sym} -240 780 0 1 {name=MO25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo25_w l=x_dut_xmo25_l m=x_dut_xmo25_m}
C {devices/sg13_lv_pmos_np.sym} 650 260 0 1 {name=MO3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo3_w l=x_dut_xmo3_l m=x_dut_xmo3_m}
C {devices/sg13_lv_nmos_np.sym} 100 520 0 1 {name=MO4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo4_w l=x_dut_xmo4_l m=x_dut_xmo4_m}
C {devices/sg13_lv_nmos_np.sym} 650 520 0 1 {name=MO5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo5_w l=x_dut_xmo5_l m=x_dut_xmo5_m}
C {devices/sg13_lv_nmos_np.sym} 1080 780 0 1 {name=MO6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo6_w l=x_dut_xmo6_l m=x_dut_xmo6_m}
C {devices/sg13_lv_nmos_np.sym} 1080 520 0 1 {name=MO7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo7_w l=x_dut_xmo7_l m=x_dut_xmo7_m}
C {devices/sg13_lv_nmos_np.sym} 1460 780 0 0 {name=MO8 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo8_w l=x_dut_xmo8_l m=x_dut_xmo8_m}
C {devices/sg13_lv_nmos_np.sym} 1460 520 0 0 {name=MO9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo9_w l=x_dut_xmo9_l m=x_dut_xmo9_m}
N -2100 -90 -2100 -30 {}
N -2100 30 -2100 90 {}
N -2100 170 -2100 230 {}
N -2100 290 -2100 350 {}
N -2100 430 -2100 490 {}
N -2100 550 -2100 610 {}
N -2100 690 -2100 750 {}
N -2100 810 -2100 870 {}
N -1780 520 -1780 590 {}
N -1740 430 -1740 490 {}
N -1740 550 -1740 590 {}
N -1680 520 -1680 614 {}
N -1600 460 -1600 590 {}
N -1560 430 -1560 490 {}
N -1560 550 -1560 590 {}
N -1500 520 -1500 614 {}
N -1385 460 -1385 520 {}
N -1325 520 -1325 580 {}
N -1075 460 -1075 520 {}
N -1015 520 -1015 580 {}
N -810 0 -810 94 {}
N -810 260 -810 354 {}
N -810 520 -810 614 {}
N -810 780 -810 874 {}
N -750 -140 -750 -30 {}
N -750 30 -750 230 {}
N -750 290 -750 350 {}
N -750 430 -750 490 {}
N -750 550 -750 590 {}
N -750 690 -750 750 {}
N -750 810 -750 920 {}
N -710 190 -710 260 {}
N -710 520 -710 590 {}
N -585 460 -585 520 {}
N -525 520 -525 580 {}
N -320 0 -320 94 {}
N -320 260 -320 354 {}
N -320 520 -320 614 {}
N -320 780 -320 874 {}
N -260 -140 -260 -30 {}
N -260 30 -260 90 {}
N -260 170 -260 230 {}
N -260 290 -260 350 {}
N -260 430 -260 490 {}
N -260 550 -260 590 {}
N -260 690 -260 750 {}
N -260 810 -260 920 {}
N -220 190 -220 260 {}
N -220 520 -220 590 {}
N -190 520 -190 780 {}
N 20 260 20 354 {}
N 20 520 20 614 {}
N 80 170 80 230 {}
N 80 290 80 350 {}
N 80 430 80 490 {}
N 80 550 80 920 {}
N 110 330 110 360 {}
N 130 -140 130 -30 {}
N 130 30 130 90 {}
N 190 0 190 94 {}
N 305 -60 305 0 {}
N 325 300 325 360 {}
N 325 420 325 480 {}
N 325 550 325 610 {}
N 345 -140 345 -30 {}
N 345 30 345 90 {}
N 345 170 345 230 {}
N 345 290 345 350 {}
N 405 0 405 94 {}
N 405 260 405 354 {}
N 515 -60 515 0 {}
N 535 300 535 360 {}
N 535 420 535 480 {}
N 555 -140 555 -30 {}
N 555 30 555 90 {}
N 570 260 570 354 {}
N 570 520 570 614 {}
N 615 0 615 94 {}
N 630 170 630 230 {}
N 630 290 630 350 {}
N 630 430 630 490 {}
N 630 550 630 920 {}
N 670 520 670 580 {}
N 790 520 790 580 {}
N 800 300 800 360 {}
N 800 420 800 480 {}
N 850 520 850 580 {}
N 1000 0 1000 94 {}
N 1000 260 1000 354 {}
N 1000 520 1000 614 {}
N 1000 780 1000 874 {}
N 1060 -140 1060 -30 {}
N 1060 30 1060 90 {}
N 1060 170 1060 230 {}
N 1060 290 1060 350 {}
N 1060 430 1060 490 {}
N 1060 550 1060 610 {}
N 1060 690 1060 750 {}
N 1060 810 1060 920 {}
N 1100 520 1100 580 {}
N 1100 780 1100 840 {}
N 1200 520 1200 780 {}
N 1230 460 1230 520 {}
N 1250 690 1250 750 {}
N 1250 810 1250 870 {}
N 1290 520 1290 580 {}
N 1440 460 1440 520 {}
N 1440 720 1440 780 {}
N 1480 -140 1480 -30 {}
N 1480 30 1480 90 {}
N 1480 170 1480 230 {}
N 1480 290 1480 350 {}
N 1480 430 1480 490 {}
N 1480 550 1480 610 {}
N 1480 690 1480 750 {}
N 1480 810 1480 920 {}
N 1540 0 1540 94 {}
N 1540 260 1540 354 {}
N 1540 520 1540 614 {}
N 1540 780 1540 874 {}
N 1710 200 1710 260 {}
N 1730 430 1730 490 {}
N 1730 550 1730 610 {}
N 1750 60 1750 230 {}
N 1750 290 1750 920 {}
N 1810 260 1810 354 {}
N 1950 430 1950 490 {}
N 1950 550 1950 610 {}
N 2110 430 2110 490 {}
N 2110 550 2110 610 {}
N 2250 460 2250 590 {}
N 2290 430 2290 490 {}
N 2290 550 2290 590 {}
N 2350 520 2350 614 {}
N 2430 460 2430 590 {}
N 2470 430 2470 490 {}
N 2470 550 2470 590 {}
N 2530 520 2530 614 {}
N -2160 -140 2660 -140 {}
N -810 0 -750 0 {}
N -710 0 -650 0 {}
N -320 0 -260 0 {}
N -220 0 -160 0 {}
N 30 0 90 0 {}
N 130 0 190 0 {}
N 275 0 305 0 {}
N 345 0 405 0 {}
N 485 0 515 0 {}
N 555 0 615 0 {}
N 1000 0 1060 0 {}
N 1100 0 1440 0 {}
N 1480 0 1540 0 {}
N -750 190 -710 190 {}
N -260 190 -220 190 {}
N 1750 200 2470 200 {}
N -810 260 -750 260 {}
N -320 260 -260 260 {}
N 20 260 80 260 {}
N 120 260 180 260 {}
N 245 260 305 260 {}
N 345 260 405 260 {}
N 570 260 630 260 {}
N 670 260 730 260 {}
N 1000 260 1060 260 {}
N 1100 260 1160 260 {}
N 1380 260 1440 260 {}
N 1480 260 1540 260 {}
N 1680 260 1710 260 {}
N 1750 260 1810 260 {}
N 110 330 130 330 {}
N 800 330 1950 330 {}
N 50 360 110 360 {}
N 50 420 110 420 {}
N 265 490 325 490 {}
N -1840 520 -1780 520 {}
N -1740 520 -1680 520 {}
N -1560 520 -1500 520 {}
N -1415 520 -1385 520 {}
N -1325 520 -1295 520 {}
N -1105 520 -1075 520 {}
N -1015 520 -985 520 {}
N -810 520 -750 520 {}
N -615 520 -585 520 {}
N -525 520 -495 520 {}
N -320 520 -260 520 {}
N 20 520 80 520 {}
N 120 520 180 520 {}
N 570 520 630 520 {}
N 760 520 790 520 {}
N 850 520 880 520 {}
N 1000 520 1060 520 {}
N 1200 520 1230 520 {}
N 1290 520 1320 520 {}
N 1480 520 1540 520 {}
N 2290 520 2350 520 {}
N 2470 520 2530 520 {}
N -1780 590 -1740 590 {}
N -1600 590 -1560 590 {}
N -750 590 -710 590 {}
N -260 590 -220 590 {}
N 2250 590 2290 590 {}
N 2430 590 2470 590 {}
N -810 780 -750 780 {}
N -710 780 -650 780 {}
N -320 780 -260 780 {}
N -220 780 -160 780 {}
N 1000 780 1060 780 {}
N 1100 780 1130 780 {}
N 1410 780 1440 780 {}
N 1480 780 1540 780 {}
N -2160 920 2660 920 {}
C {devices/lab_wire.sym} -2160 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -2160 920 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 1060 90 2 0 {name=l2 lab=csrc_n}
C {devices/lab_wire.sym} 1060 170 0 1 {name=l3 lab=csrc_n}
C {devices/lab_wire.sym} 1480 90 2 0 {name=l4 lab=csrc_p}
C {devices/lab_wire.sym} 1480 170 0 1 {name=l5 lab=csrc_p}
C {devices/lab_wire.sym} 630 350 2 0 {name=l6 lab=dio_n}
C {devices/lab_wire.sym} 630 430 0 1 {name=l7 lab=dio_n}
C {devices/lab_wire.sym} 670 580 2 0 {name=l8 lab=dio_n}
C {devices/lab_wire.sym} 1100 840 2 0 {name=l9 lab=dio_n}
C {devices/lab_wire.sym} 80 350 2 0 {name=l10 lab=dio_p}
C {devices/lab_wire.sym} 80 430 0 1 {name=l11 lab=dio_p}
C {devices/lab_wire.sym} 180 520 0 1 {name=l12 lab=dio_p}
C {devices/lab_wire.sym} 1440 720 0 1 {name=l13 lab=dio_p}
C {devices/lab_wire.sym} -1325 580 2 0 {name=l14 lab=flt_n}
C {devices/lab_wire.sym} -260 350 2 0 {name=l15 lab=flt_n}
C {devices/lab_wire.sym} -260 430 0 1 {name=l16 lab=flt_n}
C {devices/lab_wire.sym} -1015 580 2 0 {name=l17 lab=flt_p}
C {devices/lab_wire.sym} -750 350 2 0 {name=l18 lab=flt_p}
C {devices/lab_wire.sym} -750 430 0 1 {name=l19 lab=flt_p}
C {devices/lab_wire.sym} -220 520 0 0 {name=l20 lab=gdn_n}
C {devices/lab_wire.sym} -260 690 0 1 {name=l21 lab=gdn_n}
C {devices/lab_wire.sym} 1710 200 0 1 {name=l22 lab=gdn_n}
C {devices/lab_wire.sym} -710 580 2 0 {name=l23 lab=gdn_p}
C {devices/lab_wire.sym} -750 690 0 1 {name=l24 lab=gdn_p}
C {devices/lab_wire.sym} 245 260 0 0 {name=l25 lab=gdn_p}
C {devices/lab_wire.sym} -260 90 2 0 {name=l26 lab=gup_n}
C {devices/lab_wire.sym} -260 170 0 1 {name=l27 lab=gup_n}
C {devices/lab_wire.sym} 30 0 0 0 {name=l28 lab=gup_n}
C {devices/lab_wire.sym} -750 90 2 0 {name=l29 lab=gup_p}
C {devices/lab_wire.sym} 515 -60 0 1 {name=l30 lab=gup_p}
C {devices/lab_wire.sym} 1060 610 2 0 {name=l31 lab=msrc_n}
C {devices/lab_wire.sym} 1060 690 0 1 {name=l32 lab=msrc_n}
C {devices/lab_wire.sym} 1480 610 2 0 {name=l33 lab=msrc_p}
C {devices/lab_wire.sym} 1480 690 0 1 {name=l34 lab=msrc_p}
C {devices/lab_wire.sym} -525 580 2 0 {name=l35 lab=out1n}
C {devices/lab_wire.sym} -160 780 0 1 {name=l36 lab=out1n}
C {devices/lab_wire.sym} 1060 350 2 0 {name=l37 lab=out1n}
C {devices/lab_wire.sym} 1060 430 0 1 {name=l38 lab=out1n}
C {devices/lab_wire.sym} -650 780 0 1 {name=l39 lab=out1p}
C {devices/lab_wire.sym} 1230 460 0 1 {name=l40 lab=out1p}
C {devices/lab_wire.sym} 1480 350 2 0 {name=l41 lab=out1p}
C {devices/lab_wire.sym} 1480 430 0 1 {name=l42 lab=out1p}
C {devices/lab_wire.sym} -1740 430 0 1 {name=l43 lab=pr_mid_n}
C {devices/lab_wire.sym} 2470 430 0 1 {name=l44 lab=pr_mid_n}
C {devices/lab_wire.sym} -1560 430 0 1 {name=l45 lab=pr_mid_p}
C {devices/lab_wire.sym} 2290 430 0 1 {name=l46 lab=pr_mid_p}
C {devices/lab_wire.sym} -1840 520 0 0 {name=l47 lab=sum_n}
C {devices/lab_wire.sym} 535 480 2 0 {name=l48 lab=sum_n}
C {devices/lab_wire.sym} 730 260 0 1 {name=l49 lab=sum_n}
C {devices/lab_wire.sym} 1730 610 2 0 {name=l50 lab=sum_n}
C {devices/lab_wire.sym} 180 260 0 1 {name=l51 lab=sum_p}
C {devices/lab_wire.sym} 325 300 0 1 {name=l52 lab=sum_p}
C {devices/lab_wire.sym} 325 610 2 0 {name=l53 lab=sum_p}
C {devices/lab_wire.sym} 2250 460 0 1 {name=l54 lab=sum_p}
C {devices/lab_wire.sym} 80 170 0 1 {name=l55 lab=tail}
C {devices/lab_wire.sym} 345 90 2 0 {name=l56 lab=tail}
C {devices/lab_wire.sym} 630 170 0 1 {name=l57 lab=tail}
C {devices/lab_wire.sym} -650 0 0 1 {name=l58 lab=vb1}
C {devices/lab_wire.sym} -160 0 0 1 {name=l59 lab=vb1}
C {devices/lab_wire.sym} 305 -60 0 1 {name=l60 lab=vb1}
C {devices/lab_wire.sym} 1160 260 0 1 {name=l61 lab=vb2}
C {devices/lab_wire.sym} 1380 260 0 0 {name=l62 lab=vb2}
C {devices/lab_wire.sym} 1100 580 2 0 {name=l63 lab=vb3}
C {devices/lab_wire.sym} 1440 460 0 1 {name=l64 lab=vb3}
C {devices/lab_wire.sym} 50 420 0 0 {name=l65 lab=vcm_sense}
C {devices/lab_wire.sym} 800 300 0 1 {name=l66 lab=vcm_sense}
C {devices/lab_wire.sym} 1950 430 0 1 {name=l67 lab=vcm_sense}
C {devices/lab_wire.sym} 2110 430 0 1 {name=l68 lab=vcm_sense}
C {devices/lab_wire.sym} 790 580 2 0 {name=l69 lab=vcmfb}
C {devices/lab_wire.sym} 1160 0 0 1 {name=l70 lab=vcmfb}
C {devices/lab_wire.sym} 1250 870 2 0 {name=l71 lab=vcmfb}
C {devices/lab_wire.sym} 850 580 2 0 {name=l72 lab=vcmfb_ref}
C {devices/lab_wire.sym} 1950 610 2 0 {name=l73 lab=vcmfb_ref}
C {devices/lab_wire.sym} 2110 610 2 0 {name=l74 lab=vcmfb_ref}
C {devices/lab_wire.sym} 265 490 0 0 {name=l75 lab=vinn}
C {devices/lab_wire.sym} 1730 430 0 1 {name=l76 lab=vinp}
C {devices/lab_wire.sym} 50 360 0 0 {name=l77 lab=voutn}
C {devices/lab_wire.sym} 130 90 2 0 {name=l78 lab=voutn}
C {devices/lab_wire.sym} 535 300 0 1 {name=l79 lab=voutn}
C {devices/lab_wire.sym} 1750 170 0 1 {name=l80 lab=voutn}
C {devices/lab_wire.sym} 2430 460 0 1 {name=l81 lab=voutn}
C {devices/lab_wire.sym} -1600 460 0 1 {name=l82 lab=voutp}
C {devices/lab_wire.sym} 325 480 2 0 {name=l83 lab=voutp}
C {devices/lab_wire.sym} 345 170 0 1 {name=l84 lab=voutp}
C {devices/lab_wire.sym} 555 90 2 0 {name=l85 lab=voutp}
C {devices/lab_wire.sym} 800 480 2 0 {name=l86 lab=voutp}
C {devices/lab_wire.sym} -1385 460 0 1 {name=l87 lab=zc_n}
C {devices/lab_wire.sym} -585 460 0 1 {name=l88 lab=zc_n}
C {devices/lab_wire.sym} -1075 460 0 1 {name=l89 lab=zc_p}
C {devices/lab_wire.sym} 1290 580 2 0 {name=l90 lab=zc_p}
C {devices/lab_wire.sym} 2530 614 2 0 {name=l91 lab=pr_mid_n}
C {devices/lab_wire.sym} -1680 614 2 0 {name=l92 lab=pr_mid_n}
C {devices/lab_wire.sym} 2350 614 2 0 {name=l93 lab=pr_mid_p}
C {devices/lab_wire.sym} -1500 614 2 0 {name=l94 lab=pr_mid_p}
C {devices/lab_wire.sym} 405 94 2 0 {name=l95 lab=vdd}
C {devices/lab_wire.sym} 1000 354 2 0 {name=l96 lab=vdd}
C {devices/lab_wire.sym} 1540 354 2 0 {name=l97 lab=vdd}
C {devices/lab_wire.sym} 1000 94 2 0 {name=l98 lab=vdd}
C {devices/lab_wire.sym} 1540 94 2 0 {name=l99 lab=vdd}
C {devices/lab_wire.sym} -810 94 2 0 {name=l100 lab=vdd}
C {devices/lab_wire.sym} -810 614 2 0 {name=l101 lab=vdd}
C {devices/lab_wire.sym} 405 354 2 0 {name=l102 lab=vdd}
C {devices/lab_wire.sym} 20 354 2 0 {name=l103 lab=vdd}
C {devices/lab_wire.sym} -320 94 2 0 {name=l104 lab=vdd}
C {devices/lab_wire.sym} -320 614 2 0 {name=l105 lab=vdd}
C {devices/lab_wire.sym} 1810 354 2 0 {name=l106 lab=vdd}
C {devices/lab_wire.sym} 570 354 2 0 {name=l107 lab=vdd}
C {devices/lab_wire.sym} -810 354 2 0 {name=l108 lab=vss}
C {devices/lab_wire.sym} 615 94 2 0 {name=l109 lab=vss}
C {devices/lab_wire.sym} -810 874 2 0 {name=l110 lab=vss}
C {devices/lab_wire.sym} -320 354 2 0 {name=l111 lab=vss}
C {devices/lab_wire.sym} 190 94 2 0 {name=l112 lab=vss}
C {devices/lab_wire.sym} -320 874 2 0 {name=l113 lab=vss}
C {devices/lab_wire.sym} 20 614 2 0 {name=l114 lab=vss}
C {devices/lab_wire.sym} 570 614 2 0 {name=l115 lab=vss}
C {devices/lab_wire.sym} 1000 874 2 0 {name=l116 lab=vss}
C {devices/lab_wire.sym} 1000 614 2 0 {name=l117 lab=vss}
C {devices/lab_wire.sym} 1540 874 2 0 {name=l118 lab=vss}
C {devices/lab_wire.sym} 1540 614 2 0 {name=l119 lab=vss}
C {devices/lab_wire.sym} -2100 -90 0 1 {name=l120 lab=vcmfb_ref}
C {devices/lab_wire.sym} -2100 870 2 0 {name=l121 lab=vss}
C {devices/lab_wire.sym} -2100 610 2 0 {name=l122 lab=vss}
C {devices/lab_wire.sym} -2100 350 2 0 {name=l123 lab=vss}
C {devices/lab_wire.sym} -2100 90 2 0 {name=l124 lab=vss}
C {devices/lab_wire.sym} -2100 690 0 1 {name=l125 lab=vb1}
C {devices/lab_wire.sym} -2100 430 0 1 {name=l126 lab=vb2}
C {devices/lab_wire.sym} -2100 170 0 1 {name=l127 lab=vb3}
C {devices/lab_wire.sym} 1250 690 0 1 {name=l128 lab=vss}
C {devices/lab_wire.sym} 345 350 2 0 {name=l129 lab=vss}
C {devices/iopin.sym} 325 1060 0 0 {name=p0 lab=vinn}
C {devices/iopin.sym} 1730 1060 0 0 {name=p1 lab=vinp}
C {devices/opin.sym} 2800 30 0 0 {name=p2 lab=voutn}
C {devices/opin.sym} 2800 150 0 0 {name=p3 lab=voutp}
