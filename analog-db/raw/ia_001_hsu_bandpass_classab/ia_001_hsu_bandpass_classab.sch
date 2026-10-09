v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_001_hsu_bandpass_classab} -1980 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -1065 520 1 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} -1375 520 1 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} 495 390 0 0 {name=CF1 value='x_dut_cf1_value'}
C {devices/capa_np.sym} 745 390 0 0 {name=CF2 value='x_dut_cf2_value'}
C {devices/capa_np.sym} 495 520 0 0 {name=CIN1 value='x_dut_cin1_value'}
C {devices/capa_np.sym} 2075 520 0 0 {name=CIN2 value='x_dut_cin2_value'}
C {devices/capa_np.sym} 2330 520 0 0 {name=CISRV value='cin_val'}
C {devices/capa_np.sym} 1550 780 0 0 {name=COSRV value='cout_val'}
C {devices/vccs.sym} 1065 650 1 0 {name=GSRV value="\{gm_val\}"}
C {devices/res_np.sym} 1560 520 1 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} -500 520 1 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} 1055 520 0 0 {name=RISRV value='rin_val'}
C {devices/res_np.sym} 245 390 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 1175 390 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} 3170 520 0 0 {name=ROSRV value='rout_val'}
C {devices/vsource_np.sym} -1940 780 0 0 {name=VB1 value="dc \{vb1\}" savecurrent=false}
C {devices/vsource_np.sym} -1940 520 0 0 {name=VB2 value="dc \{vb2\}" savecurrent=false}
C {devices/vsource_np.sym} -1940 260 0 0 {name=VB3 value="dc \{vb3\}" savecurrent=false}
C {devices/vsource_np.sym} -1940 0 0 0 {name=VCMREF value="dc \{vcmfb_ref\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 2520 520 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 2735 520 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -1600 520 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 2955 520 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 495 0 0 0 {name=MO1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo1_w l=x_dut_xmo1_l m=x_dut_xmo1_m}
C {devices/sg13_lv_pmos_np.sym} 1380 260 0 1 {name=MO10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo10_w l=x_dut_xmo10_l m=x_dut_xmo10_m}
C {devices/sg13_lv_pmos_np.sym} 1805 260 0 0 {name=MO11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo11_w l=x_dut_xmo11_l m=x_dut_xmo11_m}
C {devices/sg13_lv_pmos_np.sym} 1380 0 0 1 {name=MO12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo12_w l=x_dut_xmo12_l m=x_dut_xmo12_m}
C {devices/sg13_lv_pmos_np.sym} 1805 0 0 0 {name=MO13 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo13_w l=x_dut_xmo13_l m=x_dut_xmo13_m}
C {devices/sg13_lv_pmos_np.sym} -675 0 0 1 {name=MO14 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo14_w l=x_dut_xmo14_l m=x_dut_xmo14_m}
C {devices/sg13_lv_nmos_np.sym} -675 260 0 1 {name=MO15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo15_w l=x_dut_xmo15_l m=x_dut_xmo15_m}
C {devices/sg13_lv_nmos_np.sym} 745 0 0 0 {name=MO16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo16_w l=x_dut_xmo16_l m=x_dut_xmo16_m}
C {devices/sg13_lv_pmos_np.sym} -675 520 0 1 {name=MO17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo17_w l=x_dut_xmo17_l m=x_dut_xmo17_m}
C {devices/sg13_lv_pmos_np.sym} 495 260 0 0 {name=MO18 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo18_w l=x_dut_xmo18_l m=x_dut_xmo18_m}
C {devices/sg13_lv_nmos_np.sym} -675 780 0 1 {name=MO19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo19_w l=x_dut_xmo19_l m=x_dut_xmo19_m}
C {devices/sg13_lv_pmos_np.sym} 235 260 0 1 {name=MO2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo2_w l=x_dut_xmo2_l m=x_dut_xmo2_m}
C {devices/sg13_lv_pmos_np.sym} -105 0 0 1 {name=MO20 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo20_w l=x_dut_xmo20_l m=x_dut_xmo20_m}
C {devices/sg13_lv_nmos_np.sym} -105 260 0 1 {name=MO21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo21_w l=x_dut_xmo21_l m=x_dut_xmo21_m}
C {devices/sg13_lv_nmos_np.sym} 245 0 0 0 {name=MO22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo22_w l=x_dut_xmo22_l m=x_dut_xmo22_m}
C {devices/sg13_lv_pmos_np.sym} -105 520 0 1 {name=MO23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo23_w l=x_dut_xmo23_l m=x_dut_xmo23_m}
C {devices/sg13_lv_pmos_np.sym} 2075 260 0 0 {name=MO24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo24_w l=x_dut_xmo24_l m=x_dut_xmo24_m}
C {devices/sg13_lv_nmos_np.sym} -105 780 0 1 {name=MO25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo25_w l=x_dut_xmo25_l m=x_dut_xmo25_m}
C {devices/sg13_lv_pmos_np.sym} 895 260 0 1 {name=MO3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo3_w l=x_dut_xmo3_l m=x_dut_xmo3_m}
C {devices/sg13_lv_nmos_np.sym} 235 520 0 1 {name=MO4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo4_w l=x_dut_xmo4_l m=x_dut_xmo4_m}
C {devices/sg13_lv_nmos_np.sym} 895 520 0 1 {name=MO5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo5_w l=x_dut_xmo5_l m=x_dut_xmo5_m}
C {devices/sg13_lv_nmos_np.sym} 1380 780 0 1 {name=MO6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo6_w l=x_dut_xmo6_l m=x_dut_xmo6_m}
C {devices/sg13_lv_nmos_np.sym} 1380 520 0 1 {name=MO7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo7_w l=x_dut_xmo7_l m=x_dut_xmo7_m}
C {devices/sg13_lv_nmos_np.sym} 1805 780 0 0 {name=MO8 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo8_w l=x_dut_xmo8_l m=x_dut_xmo8_m}
C {devices/sg13_lv_nmos_np.sym} 1805 520 0 0 {name=MO9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmo9_w l=x_dut_xmo9_l m=x_dut_xmo9_m}
N -1940 -90 -1940 -30 {}
N -1940 30 -1940 90 {}
N -1940 170 -1940 230 {}
N -1940 290 -1940 350 {}
N -1940 430 -1940 490 {}
N -1940 550 -1940 610 {}
N -1940 690 -1940 750 {}
N -1940 810 -1940 870 {}
N -1680 330 -1680 520 {}
N -1620 520 -1620 590 {}
N -1580 340 -1580 490 {}
N -1580 550 -1580 590 {}
N -1520 520 -1520 614 {}
N -1345 520 -1345 580 {}
N -1035 520 -1035 580 {}
N -755 0 -755 94 {}
N -755 320 -755 490 {}
N -755 520 -755 614 {}
N -755 780 -755 874 {}
N -695 -140 -695 -30 {}
N -695 30 -695 230 {}
N -695 290 -695 350 {}
N -695 550 -695 750 {}
N -695 810 -695 920 {}
N -655 0 -655 60 {}
N -655 190 -655 260 {}
N -655 520 -655 590 {}
N -625 -60 -625 0 {}
N -625 780 -625 840 {}
N -470 520 -470 580 {}
N -185 30 -185 200 {}
N -185 260 -185 354 {}
N -185 520 -185 614 {}
N -185 780 -185 874 {}
N -125 -140 -125 -30 {}
N -125 30 -125 90 {}
N -125 190 -125 230 {}
N -125 290 -125 350 {}
N -125 430 -125 490 {}
N -125 550 -125 590 {}
N -125 690 -125 750 {}
N -125 810 -125 920 {}
N -85 190 -85 260 {}
N -85 520 -85 590 {}
N -55 -60 -55 0 {}
N 155 320 155 490 {}
N 155 520 155 614 {}
N 185 30 185 330 {}
N 185 420 185 610 {}
N 215 170 215 230 {}
N 215 290 215 350 {}
N 215 550 215 920 {}
N 245 330 245 360 {}
N 255 520 255 900 {}
N 265 -140 265 -30 {}
N 265 30 265 90 {}
N 315 490 315 520 {}
N 325 0 325 94 {}
N 495 300 495 360 {}
N 515 -140 515 -30 {}
N 515 30 515 90 {}
N 515 170 515 230 {}
N 515 290 515 920 {}
N 575 0 575 94 {}
N 575 260 575 354 {}
N 745 300 745 360 {}
N 745 420 745 480 {}
N 765 -140 765 -30 {}
N 765 30 765 90 {}
N 815 260 815 354 {}
N 815 520 815 614 {}
N 825 0 825 94 {}
N 875 170 875 230 {}
N 875 290 875 350 {}
N 875 430 875 490 {}
N 875 550 875 920 {}
N 915 430 915 520 {}
N 1055 430 1055 490 {}
N 1055 550 1055 610 {}
N 1085 550 1085 610 {}
N 1095 650 1095 920 {}
N 1175 330 1175 360 {}
N 1175 420 1175 450 {}
N 1300 30 1300 200 {}
N 1300 260 1300 354 {}
N 1300 550 1300 720 {}
N 1300 780 1300 874 {}
N 1360 -140 1360 -30 {}
N 1360 30 1360 90 {}
N 1360 200 1360 230 {}
N 1360 290 1360 350 {}
N 1360 550 1360 610 {}
N 1360 720 1360 750 {}
N 1360 810 1360 920 {}
N 1400 520 1400 580 {}
N 1430 460 1430 780 {}
N 1480 320 1480 490 {}
N 1500 520 1500 840 {}
N 1530 460 1530 520 {}
N 1550 690 1550 750 {}
N 1550 810 1550 840 {}
N 1590 520 1590 580 {}
N 1610 0 1610 840 {}
N 1755 780 1755 900 {}
N 1765 30 1765 200 {}
N 1825 -140 1825 -30 {}
N 1825 30 1825 90 {}
N 1825 200 1825 230 {}
N 1825 290 1825 350 {}
N 1825 550 1825 610 {}
N 1825 720 1825 750 {}
N 1825 810 1825 920 {}
N 1885 0 1885 94 {}
N 1885 320 1885 490 {}
N 1885 550 1885 720 {}
N 1885 780 1885 874 {}
N 2075 430 2075 490 {}
N 2075 550 2075 610 {}
N 2095 200 2095 230 {}
N 2095 290 2095 920 {}
N 2155 260 2155 354 {}
N 2330 430 2330 490 {}
N 2330 550 2330 610 {}
N 2500 520 2500 590 {}
N 2540 430 2540 490 {}
N 2540 550 2540 590 {}
N 2600 520 2600 614 {}
N 2715 520 2715 590 {}
N 2755 550 2755 590 {}
N 2815 520 2815 614 {}
N 2935 520 2935 590 {}
N 2975 340 2975 490 {}
N 2975 550 2975 590 {}
N 3035 520 3035 614 {}
N 3170 430 3170 490 {}
N 3170 550 3170 840 {}
N -2000 -140 3430 -140 {}
N -625 -60 -55 -60 {}
N -755 0 -695 0 {}
N -655 0 -625 0 {}
N -85 0 -55 0 {}
N 165 0 225 0 {}
N 265 0 325 0 {}
N 415 0 475 0 {}
N 515 0 575 0 {}
N 665 0 725 0 {}
N 765 0 825 0 {}
N 1400 0 1785 0 {}
N 1825 0 1885 0 {}
N -185 30 -125 30 {}
N 185 30 265 30 {}
N 1300 30 1360 30 {}
N 1765 30 1825 30 {}
N -695 190 -655 190 {}
N -125 190 -85 190 {}
N -185 200 -125 200 {}
N 1300 200 1360 200 {}
N 1765 200 1825 200 {}
N -185 260 -125 260 {}
N 255 260 315 260 {}
N 415 260 475 260 {}
N 515 260 575 260 {}
N 815 260 875 260 {}
N 915 260 975 260 {}
N 1300 260 1360 260 {}
N 1400 260 1785 260 {}
N 1995 260 2055 260 {}
N 2095 260 2155 260 {}
N -755 320 -695 320 {}
N 155 320 215 320 {}
N 1360 320 1480 320 {}
N 1825 320 1885 320 {}
N -1680 330 245 330 {}
N -1580 340 2975 340 {}
N 1115 360 1175 360 {}
N 185 420 245 420 {}
N 875 430 915 430 {}
N 915 460 1430 460 {}
N -755 490 -695 490 {}
N 155 490 315 490 {}
N 1360 490 1480 490 {}
N 1825 490 1885 490 {}
N 2540 490 2815 490 {}
N -1680 520 -1620 520 {}
N -1580 520 -1520 520 {}
N -1465 520 -1405 520 {}
N -1345 520 -1315 520 {}
N -1155 520 -1095 520 {}
N -1035 520 -1005 520 {}
N -755 520 -695 520 {}
N -590 520 -530 520 {}
N -470 520 -440 520 {}
N -185 520 -125 520 {}
N -85 520 -25 520 {}
N 155 520 215 520 {}
N 255 520 315 520 {}
N 815 520 875 520 {}
N 1500 520 1530 520 {}
N 1590 520 1620 520 {}
N 1725 520 1785 520 {}
N 2440 520 2500 520 {}
N 2540 520 2600 520 {}
N 2655 520 2715 520 {}
N 2755 520 2815 520 {}
N 2875 520 2935 520 {}
N 2975 520 3035 520 {}
N 1300 550 1360 550 {}
N 1825 550 1885 550 {}
N -1620 590 -1580 590 {}
N -695 590 -655 590 {}
N -125 590 -85 590 {}
N 2500 590 2540 590 {}
N 2715 590 2755 590 {}
N 2935 590 2975 590 {}
N 185 610 1045 610 {}
N 975 650 1035 650 {}
N 1300 720 1360 720 {}
N 1825 720 1885 720 {}
N -755 780 -695 780 {}
N -655 780 -625 780 {}
N -185 780 -125 780 {}
N -85 780 -25 780 {}
N 1300 780 1360 780 {}
N 1400 780 1430 780 {}
N 1755 780 1785 780 {}
N 1825 780 1885 780 {}
N -625 840 1500 840 {}
N 1550 840 3170 840 {}
N 255 900 1755 900 {}
N -2000 920 3430 920 {}
C {devices/lab_wire.sym} 1360 90 2 0 {name=l0 lab=csrc_n}
C {devices/lab_wire.sym} 1825 90 2 0 {name=l1 lab=csrc_p}
C {devices/lab_wire.sym} 875 350 2 0 {name=l2 lab=dio_n}
C {devices/lab_wire.sym} 875 430 0 1 {name=l3 lab=dio_n}
C {devices/lab_wire.sym} 215 350 2 0 {name=l4 lab=dio_p}
C {devices/lab_wire.sym} -1345 580 2 0 {name=l5 lab=flt_n}
C {devices/lab_wire.sym} -125 350 2 0 {name=l6 lab=flt_n}
C {devices/lab_wire.sym} -125 430 0 1 {name=l7 lab=flt_n}
C {devices/lab_wire.sym} -1035 580 2 0 {name=l8 lab=flt_p}
C {devices/lab_wire.sym} -695 350 2 0 {name=l9 lab=flt_p}
C {devices/lab_wire.sym} -25 520 0 1 {name=l10 lab=gdn_n}
C {devices/lab_wire.sym} -125 690 0 1 {name=l11 lab=gdn_n}
C {devices/lab_wire.sym} 1995 260 0 0 {name=l12 lab=gdn_n}
C {devices/lab_wire.sym} -655 580 2 0 {name=l13 lab=gdn_p}
C {devices/lab_wire.sym} 415 260 0 0 {name=l14 lab=gdn_p}
C {devices/lab_wire.sym} -125 90 2 0 {name=l15 lab=gup_n}
C {devices/lab_wire.sym} 165 0 0 0 {name=l16 lab=gup_n}
C {devices/lab_wire.sym} -695 90 2 0 {name=l17 lab=gup_p}
C {devices/lab_wire.sym} 665 0 0 0 {name=l18 lab=gup_p}
C {devices/lab_wire.sym} 1360 610 2 0 {name=l19 lab=msrc_n}
C {devices/lab_wire.sym} 1825 610 2 0 {name=l20 lab=msrc_p}
C {devices/lab_wire.sym} -470 580 2 0 {name=l21 lab=out1n}
C {devices/lab_wire.sym} -25 780 0 1 {name=l22 lab=out1n}
C {devices/lab_wire.sym} 1360 350 2 0 {name=l23 lab=out1n}
C {devices/lab_wire.sym} 1530 460 0 1 {name=l24 lab=out1p}
C {devices/lab_wire.sym} 1825 350 2 0 {name=l25 lab=out1p}
C {devices/lab_wire.sym} -1580 430 0 1 {name=l26 lab=pr_mid_n}
C {devices/lab_wire.sym} 2540 430 0 1 {name=l27 lab=pr_mid_p}
C {devices/lab_wire.sym} 745 480 2 0 {name=l28 lab=sum_n}
C {devices/lab_wire.sym} 975 260 0 1 {name=l29 lab=sum_n}
C {devices/lab_wire.sym} 2075 610 2 0 {name=l30 lab=sum_n}
C {devices/lab_wire.sym} 2875 520 0 0 {name=l31 lab=sum_n}
C {devices/lab_wire.sym} 315 260 0 1 {name=l32 lab=sum_p}
C {devices/lab_wire.sym} 495 300 0 1 {name=l33 lab=sum_p}
C {devices/lab_wire.sym} 495 550 0 0 {name=l34 lab=sum_p}
C {devices/lab_wire.sym} 2440 520 0 0 {name=l35 lab=sum_p}
C {devices/lab_wire.sym} 215 170 0 1 {name=l36 lab=tail}
C {devices/lab_wire.sym} 515 90 2 0 {name=l37 lab=tail}
C {devices/lab_wire.sym} 875 170 0 1 {name=l38 lab=tail}
C {devices/lab_wire.sym} -655 60 2 0 {name=l39 lab=vb1}
C {devices/lab_wire.sym} 415 0 0 0 {name=l40 lab=vb1}
C {devices/lab_wire.sym} 1460 260 0 1 {name=l41 lab=vb2}
C {devices/lab_wire.sym} 1400 580 2 0 {name=l42 lab=vb3}
C {devices/lab_wire.sym} 1725 520 0 0 {name=l43 lab=vb3}
C {devices/lab_wire.sym} 185 420 0 0 {name=l44 lab=vcm_sense}
C {devices/lab_wire.sym} 1055 430 0 1 {name=l45 lab=vcm_sense}
C {devices/lab_wire.sym} 1115 360 0 0 {name=l46 lab=vcm_sense}
C {devices/lab_wire.sym} 2330 430 0 1 {name=l47 lab=vcm_sense}
C {devices/lab_wire.sym} 975 650 0 0 {name=l48 lab=vcmfb}
C {devices/lab_wire.sym} 1460 0 0 1 {name=l49 lab=vcmfb}
C {devices/lab_wire.sym} 1055 610 2 0 {name=l50 lab=vcmfb_ref}
C {devices/lab_wire.sym} 1085 550 0 1 {name=l51 lab=vcmfb_ref}
C {devices/lab_wire.sym} 2330 610 2 0 {name=l52 lab=vcmfb_ref}
C {devices/lab_wire.sym} 3170 430 0 1 {name=l53 lab=vcmfb_ref}
C {devices/lab_wire.sym} 495 490 0 0 {name=l54 lab=vinn}
C {devices/lab_wire.sym} 2075 430 0 1 {name=l55 lab=vinp}
C {devices/lab_wire.sym} 265 90 2 0 {name=l56 lab=voutn}
C {devices/lab_wire.sym} 745 300 0 1 {name=l57 lab=voutn}
C {devices/lab_wire.sym} 495 420 0 0 {name=l58 lab=voutp}
C {devices/lab_wire.sym} 515 170 0 1 {name=l59 lab=voutp}
C {devices/lab_wire.sym} 765 90 2 0 {name=l60 lab=voutp}
C {devices/lab_wire.sym} 2655 520 0 0 {name=l61 lab=voutp}
C {devices/lab_wire.sym} -1465 520 0 0 {name=l62 lab=zc_n}
C {devices/lab_wire.sym} -590 520 0 0 {name=l63 lab=zc_n}
C {devices/lab_wire.sym} -1155 520 0 0 {name=l64 lab=zc_p}
C {devices/lab_wire.sym} 1590 580 2 0 {name=l65 lab=zc_p}
C {devices/lab_wire.sym} -1520 614 2 0 {name=l66 lab=pr_mid_n}
C {devices/lab_wire.sym} 3035 614 2 0 {name=l67 lab=pr_mid_n}
C {devices/lab_wire.sym} 2600 614 2 0 {name=l68 lab=pr_mid_p}
C {devices/lab_wire.sym} 2815 614 2 0 {name=l69 lab=pr_mid_p}
C {devices/lab_wire.sym} 575 94 2 0 {name=l70 lab=vdd}
C {devices/lab_wire.sym} 1300 354 2 0 {name=l71 lab=vdd}
C {devices/lab_wire.sym} 1825 260 0 0 {name=l72 lab=vdd}
C {devices/lab_wire.sym} 1360 0 0 0 {name=l73 lab=vdd}
C {devices/lab_wire.sym} 1885 94 2 0 {name=l74 lab=vdd}
C {devices/lab_wire.sym} -755 94 2 0 {name=l75 lab=vdd}
C {devices/lab_wire.sym} -755 614 2 0 {name=l76 lab=vdd}
C {devices/lab_wire.sym} 575 354 2 0 {name=l77 lab=vdd}
C {devices/lab_wire.sym} 215 260 0 0 {name=l78 lab=vdd}
C {devices/lab_wire.sym} -125 0 0 0 {name=l79 lab=vdd}
C {devices/lab_wire.sym} -185 614 2 0 {name=l80 lab=vdd}
C {devices/lab_wire.sym} 2155 354 2 0 {name=l81 lab=vdd}
C {devices/lab_wire.sym} 815 354 2 0 {name=l82 lab=vdd}
C {devices/lab_wire.sym} -695 260 0 0 {name=l83 lab=vss}
C {devices/lab_wire.sym} 825 94 2 0 {name=l84 lab=vss}
C {devices/lab_wire.sym} -755 874 2 0 {name=l85 lab=vss}
C {devices/lab_wire.sym} -185 354 2 0 {name=l86 lab=vss}
C {devices/lab_wire.sym} 325 94 2 0 {name=l87 lab=vss}
C {devices/lab_wire.sym} -185 874 2 0 {name=l88 lab=vss}
C {devices/lab_wire.sym} 155 614 2 0 {name=l89 lab=vss}
C {devices/lab_wire.sym} 815 614 2 0 {name=l90 lab=vss}
C {devices/lab_wire.sym} 1300 874 2 0 {name=l91 lab=vss}
C {devices/lab_wire.sym} 1360 520 0 0 {name=l92 lab=vss}
C {devices/lab_wire.sym} 1885 874 2 0 {name=l93 lab=vss}
C {devices/lab_wire.sym} 1825 520 0 0 {name=l94 lab=vss}
C {devices/lab_wire.sym} -1940 -90 0 1 {name=l95 lab=vcmfb_ref}
C {devices/lab_wire.sym} -1940 870 2 0 {name=l96 lab=vss}
C {devices/lab_wire.sym} -1940 610 2 0 {name=l97 lab=vss}
C {devices/lab_wire.sym} -1940 350 2 0 {name=l98 lab=vss}
C {devices/lab_wire.sym} -1940 90 2 0 {name=l99 lab=vss}
C {devices/lab_wire.sym} -1940 690 0 1 {name=l100 lab=vb1}
C {devices/lab_wire.sym} -1940 430 0 1 {name=l101 lab=vb2}
C {devices/lab_wire.sym} -1940 170 0 1 {name=l102 lab=vb3}
C {devices/lab_wire.sym} 1550 690 0 1 {name=l103 lab=vss}
C {devices/iopin.sym} -2000 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -2000 920 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 2095 200 0 0 {name=p2 lab=voutn}
C {devices/opin.sym} 1175 450 0 0 {name=p3 lab=voutp}
C {devices/iopin.sym} 495 1060 0 0 {name=p4 lab=vinn}
C {devices/iopin.sym} 2075 1060 0 0 {name=p5 lab=vinp}
