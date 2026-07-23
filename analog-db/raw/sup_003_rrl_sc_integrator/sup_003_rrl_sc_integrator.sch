v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sup_003_rrl_sc_integrator} -1815 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 400 650 0 0 {name=CAZ1 value='x_dut_caz1_value'}
C {devices/capa_np.sym} 640 650 0 0 {name=CAZ2 value='x_dut_caz2_value'}
C {devices/capa_np.sym} 400 910 0 0 {name=CINT1 value='x_dut_cint1_value'}
C {devices/capa_np.sym} 640 910 0 0 {name=CINT2 value='x_dut_cint2_value'}
C {devices/capa_np.sym} 400 1040 0 0 {name=CIN_1 value='cin_val'}
C {devices/capa_np.sym} 1690 520 0 0 {name=COUT_1 value='cout_val'}
C {devices/capa_np.sym} 2380 780 0 0 {name=CS1 value='x_dut_cs1_value'}
C {devices/capa_np.sym} -1435 780 0 0 {name=CS2 value='x_dut_cs2_value'}
C {devices/res_np.sym} 160 1040 0 0 {name=RIN_1 value='rin_val'}
C {devices/res_np.sym} -910 520 0 0 {name=ROUT_1 value='rout_val'}
C {devices/vsource_np.sym} -1775 1040 0 0 {name=VB1 value="dc {vb1}"}
C {devices/vsource_np.sym} -1775 780 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -1775 520 0 0 {name=VB3 value="dc {vb3}"}
C {devices/vsource_np.sym} -1775 260 0 0 {name=VB4 value="dc {vb4}"}
C {devices/sg13_lv_pmos_np.sym} 125 520 0 1 {name=M10_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_opamp_w l=x_dut_xm10_opamp_l m=x_dut_xm10_opamp_m}
C {devices/sg13_lv_nmos_np.sym} -275 780 0 1 {name=M11_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_opamp_w l=x_dut_xm11_opamp_l m=x_dut_xm11_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 650 780 0 0 {name=M12_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_opamp_w l=x_dut_xm12_opamp_l m=x_dut_xm12_opamp_m}
C {devices/sg13_lv_nmos_np.sym} -275 1040 0 1 {name=M13_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_opamp_w l=x_dut_xm13_opamp_l m=x_dut_xm13_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 650 1040 0 0 {name=M14_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_opamp_w l=x_dut_xm14_opamp_l m=x_dut_xm14_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 400 520 0 0 {name=M15_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_opamp_w l=x_dut_xm15_opamp_l m=x_dut_xm15_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 640 520 0 0 {name=M16_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_opamp_w l=x_dut_xm16_opamp_l m=x_dut_xm16_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 400 780 0 0 {name=M1_CHRRL_1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_1_w l=x_dut_xm1_chrrl_1_l m=x_dut_xm1_chrrl_1_m}
C {devices/sg13_lv_nmos_np.sym} 160 780 0 0 {name=M1_CHRRL_2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_2_w l=x_dut_xm1_chrrl_2_l m=x_dut_xm1_chrrl_2_m}
C {devices/sg13_lv_nmos_np.sym} -85 780 0 0 {name=M1_CHRRL_3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_3_w l=x_dut_xm1_chrrl_3_l m=x_dut_xm1_chrrl_3_m}
C {devices/sg13_lv_nmos_np.sym} 1035 780 0 0 {name=M1_CHRRL_4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_chrrl_4_w l=x_dut_xm1_chrrl_4_l m=x_dut_xm1_chrrl_4_m}
C {devices/sg13_lv_pmos_np.sym} 650 0 0 0 {name=M1_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_opamp_w l=x_dut_xm1_opamp_l m=x_dut_xm1_opamp_m}
C {devices/sg13_lv_nmos_np.sym} -85 1040 0 0 {name=M1_S1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s1_w l=x_dut_xm1_s1_l m=x_dut_xm1_s1_m}
C {devices/sg13_lv_nmos_np.sym} 1035 1040 0 0 {name=M1_S2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s2_w l=x_dut_xm1_s2_l m=x_dut_xm1_s2_m}
C {devices/sg13_lv_nmos_np.sym} 875 520 0 0 {name=M1_S3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s3_w l=x_dut_xm1_s3_l m=x_dut_xm1_s3_m}
C {devices/sg13_lv_nmos_np.sym} -245 520 0 0 {name=M1_S4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s4_w l=x_dut_xm1_s4_l m=x_dut_xm1_s4_m}
C {devices/sg13_lv_nmos_np.sym} 1280 780 0 0 {name=M1_S5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s5_w l=x_dut_xm1_s5_l m=x_dut_xm1_s5_m}
C {devices/sg13_lv_nmos_np.sym} 1480 780 0 0 {name=M1_S6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_s6_w l=x_dut_xm1_s6_l m=x_dut_xm1_s6_m}
C {devices/sg13_lv_pmos_np.sym} -670 780 0 0 {name=M2_CHRRL_1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_1_w l=x_dut_xm2_chrrl_1_l m=x_dut_xm2_chrrl_1_m}
C {devices/sg13_lv_pmos_np.sym} 1685 780 0 0 {name=M2_CHRRL_2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_2_w l=x_dut_xm2_chrrl_2_l m=x_dut_xm2_chrrl_2_m}
C {devices/sg13_lv_pmos_np.sym} -915 780 0 0 {name=M2_CHRRL_3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_3_w l=x_dut_xm2_chrrl_3_l m=x_dut_xm2_chrrl_3_m}
C {devices/sg13_lv_pmos_np.sym} 1930 780 0 0 {name=M2_CHRRL_4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_chrrl_4_w l=x_dut_xm2_chrrl_4_l m=x_dut_xm2_chrrl_4_m}
C {devices/sg13_lv_pmos_np.sym} 1100 260 0 0 {name=M2_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_opamp_w l=x_dut_xm2_opamp_l m=x_dut_xm2_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 1280 1040 0 0 {name=M2_S1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s1_w l=x_dut_xm2_s1_l m=x_dut_xm2_s1_m}
C {devices/sg13_lv_pmos_np.sym} 1480 1040 0 0 {name=M2_S2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s2_w l=x_dut_xm2_s2_l m=x_dut_xm2_s2_m}
C {devices/sg13_lv_pmos_np.sym} -510 520 0 0 {name=M2_S3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s3_w l=x_dut_xm2_s3_l m=x_dut_xm2_s3_m}
C {devices/sg13_lv_pmos_np.sym} 1480 520 0 0 {name=M2_S4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s4_w l=x_dut_xm2_s4_l m=x_dut_xm2_s4_m}
C {devices/sg13_lv_pmos_np.sym} -1120 780 0 0 {name=M2_S5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s5_w l=x_dut_xm2_s5_l m=x_dut_xm2_s5_m}
C {devices/sg13_lv_pmos_np.sym} 2175 780 0 0 {name=M2_S6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_s6_w l=x_dut_xm2_s6_l m=x_dut_xm2_s6_m}
C {devices/sg13_lv_pmos_np.sym} 125 260 0 1 {name=M3_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_opamp_w l=x_dut_xm3_opamp_l m=x_dut_xm3_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 400 0 0 0 {name=M4_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_opamp_w l=x_dut_xm4_opamp_l m=x_dut_xm4_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 400 260 0 0 {name=M5_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_opamp_w l=x_dut_xm5_opamp_l m=x_dut_xm5_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 640 260 0 0 {name=M6_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_opamp_w l=x_dut_xm6_opamp_l m=x_dut_xm6_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 875 260 0 0 {name=M7_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_opamp_w l=x_dut_xm7_opamp_l m=x_dut_xm7_opamp_m}
C {devices/sg13_lv_pmos_np.sym} -245 260 0 0 {name=M8_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_opamp_w l=x_dut_xm8_opamp_l m=x_dut_xm8_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 1100 520 0 0 {name=M9_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_opamp_w l=x_dut_xm9_opamp_l m=x_dut_xm9_opamp_m}
N -1775 170 -1775 230 {}
N -1775 290 -1775 350 {}
N -1775 430 -1775 490 {}
N -1775 550 -1775 610 {}
N -1775 690 -1775 750 {}
N -1775 810 -1775 870 {}
N -1775 950 -1775 1010 {}
N -1775 1070 -1775 1130 {}
N -1435 690 -1435 750 {}
N -1435 810 -1435 870 {}
N -1140 720 -1140 780 {}
N -1100 690 -1100 750 {}
N -1100 810 -1100 870 {}
N -1040 780 -1040 874 {}
N -935 720 -935 780 {}
N -910 430 -910 490 {}
N -910 550 -910 610 {}
N -895 690 -895 750 {}
N -895 810 -895 870 {}
N -835 780 -835 874 {}
N -690 720 -690 780 {}
N -650 690 -650 750 {}
N -650 810 -650 870 {}
N -590 780 -590 874 {}
N -490 430 -490 490 {}
N -490 550 -490 610 {}
N -430 520 -430 614 {}
N -355 780 -355 874 {}
N -355 1040 -355 1134 {}
N -295 690 -295 750 {}
N -295 810 -295 870 {}
N -295 950 -295 1010 {}
N -295 1070 -295 1180 {}
N -265 460 -265 520 {}
N -255 780 -255 840 {}
N -255 1040 -255 1100 {}
N -225 170 -225 230 {}
N -225 290 -225 350 {}
N -225 430 -225 490 {}
N -225 550 -225 610 {}
N -165 260 -165 354 {}
N -165 520 -165 614 {}
N -105 720 -105 780 {}
N -105 980 -105 1040 {}
N -65 690 -65 750 {}
N -65 810 -65 870 {}
N -65 950 -65 1010 {}
N -65 1070 -65 1180 {}
N -5 780 -5 874 {}
N -5 1040 -5 1134 {}
N 45 260 45 354 {}
N 45 520 45 614 {}
N 105 170 105 230 {}
N 105 290 105 350 {}
N 105 430 105 490 {}
N 105 550 105 610 {}
N 140 720 140 780 {}
N 160 950 160 1010 {}
N 160 1070 160 1100 {}
N 180 690 180 750 {}
N 180 810 180 870 {}
N 240 780 240 874 {}
N 380 450 380 520 {}
N 400 590 400 620 {}
N 400 680 400 710 {}
N 400 850 400 880 {}
N 400 940 400 1010 {}
N 400 1070 400 1100 {}
N 420 -140 420 -30 {}
N 420 30 420 90 {}
N 420 170 420 230 {}
N 420 290 420 350 {}
N 420 430 420 490 {}
N 420 550 420 610 {}
N 420 690 420 750 {}
N 420 810 420 870 {}
N 480 0 480 94 {}
N 480 260 480 354 {}
N 480 520 480 614 {}
N 480 780 480 874 {}
N 620 200 620 260 {}
N 620 450 620 520 {}
N 630 -60 630 0 {}
N 640 560 640 620 {}
N 640 680 640 740 {}
N 640 820 640 880 {}
N 640 940 640 1100 {}
N 660 170 660 230 {}
N 660 290 660 350 {}
N 660 430 660 490 {}
N 660 550 660 1180 {}
N 670 -140 670 -30 {}
N 670 30 670 90 {}
N 670 690 670 750 {}
N 670 810 670 870 {}
N 670 950 670 1010 {}
N 670 1070 670 1180 {}
N 720 260 720 354 {}
N 720 520 720 614 {}
N 730 0 730 94 {}
N 730 780 730 874 {}
N 730 1040 730 1134 {}
N 855 200 855 260 {}
N 855 460 855 520 {}
N 895 170 895 230 {}
N 895 290 895 350 {}
N 895 430 895 490 {}
N 895 550 895 610 {}
N 955 260 955 354 {}
N 955 520 955 614 {}
N 1015 720 1015 780 {}
N 1055 690 1055 750 {}
N 1055 810 1055 870 {}
N 1055 950 1055 1010 {}
N 1055 1070 1055 1180 {}
N 1080 200 1080 260 {}
N 1080 460 1080 520 {}
N 1115 780 1115 874 {}
N 1115 1040 1115 1134 {}
N 1120 170 1120 230 {}
N 1120 290 1120 350 {}
N 1120 430 1120 490 {}
N 1120 550 1120 610 {}
N 1180 260 1180 354 {}
N 1180 520 1180 614 {}
N 1230 780 1230 1040 {}
N 1260 720 1260 780 {}
N 1300 690 1300 750 {}
N 1300 810 1300 870 {}
N 1300 950 1300 1010 {}
N 1300 1070 1300 1180 {}
N 1360 780 1360 874 {}
N 1360 1040 1360 1134 {}
N 1430 520 1430 1040 {}
N 1500 430 1500 490 {}
N 1500 550 1500 610 {}
N 1500 690 1500 750 {}
N 1500 810 1500 870 {}
N 1500 980 1500 1010 {}
N 1500 1070 1500 1180 {}
N 1560 520 1560 614 {}
N 1560 780 1560 874 {}
N 1560 1040 1560 1134 {}
N 1665 720 1665 780 {}
N 1690 430 1690 490 {}
N 1690 550 1690 610 {}
N 1705 690 1705 750 {}
N 1705 810 1705 870 {}
N 1765 780 1765 874 {}
N 1910 720 1910 780 {}
N 1950 690 1950 750 {}
N 1950 810 1950 870 {}
N 2010 780 2010 874 {}
N 2155 720 2155 780 {}
N 2195 690 2195 750 {}
N 2195 810 2195 870 {}
N 2255 780 2255 874 {}
N 2380 690 2380 750 {}
N 2380 810 2380 870 {}
N -1835 -140 2620 -140 {}
N 320 0 380 0 {}
N 420 0 480 0 {}
N 600 0 630 0 {}
N 670 0 730 0 {}
N -325 260 -265 260 {}
N -225 260 -165 260 {}
N 45 260 105 260 {}
N 145 260 205 260 {}
N 320 260 380 260 {}
N 420 260 480 260 {}
N 590 260 620 260 {}
N 660 260 720 260 {}
N 825 260 855 260 {}
N 895 260 955 260 {}
N 1050 260 1080 260 {}
N 1120 260 1180 260 {}
N 380 450 420 450 {}
N 620 450 660 450 {}
N -590 520 -530 520 {}
N -490 520 -430 520 {}
N -295 520 -265 520 {}
N -225 520 -165 520 {}
N 45 520 105 520 {}
N 145 520 205 520 {}
N 420 520 480 520 {}
N 660 520 720 520 {}
N 895 520 955 520 {}
N 1120 520 1180 520 {}
N 1400 520 1460 520 {}
N 1500 520 1560 520 {}
N 340 620 400 620 {}
N 340 680 400 680 {}
N -1170 780 -1140 780 {}
N -1100 780 -1040 780 {}
N -965 780 -935 780 {}
N -895 780 -835 780 {}
N -720 780 -690 780 {}
N -650 780 -590 780 {}
N -355 780 -295 780 {}
N -255 780 -225 780 {}
N -65 780 -5 780 {}
N 110 780 140 780 {}
N 180 780 240 780 {}
N 320 780 380 780 {}
N 420 780 480 780 {}
N 570 780 630 780 {}
N 670 780 730 780 {}
N 985 780 1015 780 {}
N 1055 780 1115 780 {}
N 1230 780 1260 780 {}
N 1300 780 1360 780 {}
N 1430 780 1460 780 {}
N 1500 780 1560 780 {}
N 1635 780 1665 780 {}
N 1705 780 1765 780 {}
N 1880 780 1910 780 {}
N 1950 780 2010 780 {}
N 2125 780 2155 780 {}
N 2195 780 2255 780 {}
N 340 880 400 880 {}
N 340 940 400 940 {}
N 640 970 1500 970 {}
N -355 1040 -295 1040 {}
N -255 1040 -225 1040 {}
N -135 1040 -105 1040 {}
N -65 1040 -5 1040 {}
N 600 1040 630 1040 {}
N 670 1040 730 1040 {}
N 955 1040 1015 1040 {}
N 1055 1040 1115 1040 {}
N 1230 1040 1260 1040 {}
N 1300 1040 1360 1040 {}
N 1430 1040 1460 1040 {}
N 1500 1040 1560 1040 {}
N 160 1100 640 1100 {}
N -1835 1180 2620 1180 {}
C {devices/lab_wire.sym} -1835 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1835 1180 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -935 720 0 1 {name=l2 lab=clk_ch_rrl}
C {devices/lab_wire.sym} 140 720 0 1 {name=l3 lab=clk_ch_rrl}
C {devices/lab_wire.sym} 320 780 0 0 {name=l4 lab=clk_ch_rrl}
C {devices/lab_wire.sym} 1910 720 0 1 {name=l5 lab=clk_ch_rrl}
C {devices/lab_wire.sym} -690 720 0 1 {name=l6 lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} -105 720 0 1 {name=l7 lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} 1015 720 0 1 {name=l8 lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} 1665 720 0 1 {name=l9 lab=clk_ch_rrl_not}
C {devices/lab_wire.sym} -590 520 0 0 {name=l10 lab=clk_phi_1}
C {devices/lab_wire.sym} 1260 720 0 1 {name=l11 lab=clk_phi_1}
C {devices/lab_wire.sym} 1400 520 0 0 {name=l12 lab=clk_phi_1}
C {devices/lab_wire.sym} -1140 720 0 1 {name=l13 lab=clk_phi_2}
C {devices/lab_wire.sym} -265 460 0 1 {name=l14 lab=clk_phi_2}
C {devices/lab_wire.sym} -105 980 0 1 {name=l15 lab=clk_phi_2}
C {devices/lab_wire.sym} 855 460 0 1 {name=l16 lab=clk_phi_2}
C {devices/lab_wire.sym} 955 1040 0 0 {name=l17 lab=clk_phi_2}
C {devices/lab_wire.sym} 2155 720 0 1 {name=l18 lab=clk_phi_2}
C {devices/lab_wire.sym} 640 1000 2 0 {name=l19 lab=int_n}
C {devices/lab_wire.sym} 1500 870 2 0 {name=l20 lab=int_n}
C {devices/lab_wire.sym} 2195 870 2 0 {name=l21 lab=int_n}
C {devices/lab_wire.sym} -1100 870 2 0 {name=l22 lab=int_p}
C {devices/lab_wire.sym} 160 950 0 1 {name=l23 lab=int_p}
C {devices/lab_wire.sym} 340 940 0 0 {name=l24 lab=int_p}
C {devices/lab_wire.sym} 400 950 0 1 {name=l25 lab=int_p}
C {devices/lab_wire.sym} 1300 870 2 0 {name=l26 lab=int_p}
C {devices/lab_wire.sym} -255 1100 2 0 {name=l27 lab=oa_cm_bias}
C {devices/lab_wire.sym} -225 350 2 0 {name=l28 lab=oa_cm_bias}
C {devices/lab_wire.sym} 420 430 0 1 {name=l29 lab=oa_cm_bias}
C {devices/lab_wire.sym} 630 1040 0 0 {name=l30 lab=oa_cm_bias}
C {devices/lab_wire.sym} 660 350 2 0 {name=l31 lab=oa_cm_bias}
C {devices/lab_wire.sym} 420 350 2 0 {name=l32 lab=oa_cm_sense}
C {devices/lab_wire.sym} 660 430 0 1 {name=l33 lab=oa_cm_sense}
C {devices/lab_wire.sym} 895 350 2 0 {name=l34 lab=oa_cm_sense}
C {devices/lab_wire.sym} -225 170 0 1 {name=l35 lab=oa_cm_tail}
C {devices/lab_wire.sym} 420 90 2 0 {name=l36 lab=oa_cm_tail}
C {devices/lab_wire.sym} 420 170 0 1 {name=l37 lab=oa_cm_tail}
C {devices/lab_wire.sym} 660 170 0 1 {name=l38 lab=oa_cm_tail}
C {devices/lab_wire.sym} 895 170 0 1 {name=l39 lab=oa_cm_tail}
C {devices/lab_wire.sym} -295 870 2 0 {name=l40 lab=oa_csrc_n}
C {devices/lab_wire.sym} -295 950 0 1 {name=l41 lab=oa_csrc_n}
C {devices/lab_wire.sym} 670 870 2 0 {name=l42 lab=oa_csrc_p}
C {devices/lab_wire.sym} 670 950 0 1 {name=l43 lab=oa_csrc_p}
C {devices/lab_wire.sym} 1120 350 2 0 {name=l44 lab=oa_d1n}
C {devices/lab_wire.sym} 1120 430 0 1 {name=l45 lab=oa_d1n}
C {devices/lab_wire.sym} 105 350 2 0 {name=l46 lab=oa_d1p}
C {devices/lab_wire.sym} 105 430 0 1 {name=l47 lab=oa_d1p}
C {devices/lab_wire.sym} -225 430 0 1 {name=l48 lab=oa_inn}
C {devices/lab_wire.sym} 205 260 0 1 {name=l49 lab=oa_inn}
C {devices/lab_wire.sym} 640 740 2 0 {name=l50 lab=oa_inn}
C {devices/lab_wire.sym} 1500 430 0 1 {name=l51 lab=oa_inn}
C {devices/lab_wire.sym} -490 430 0 1 {name=l52 lab=oa_inp}
C {devices/lab_wire.sym} 340 680 0 0 {name=l53 lab=oa_inp}
C {devices/lab_wire.sym} 895 430 0 1 {name=l54 lab=oa_inp}
C {devices/lab_wire.sym} 1080 200 0 1 {name=l55 lab=oa_inp}
C {devices/lab_wire.sym} -1100 690 0 1 {name=l56 lab=oa_outn}
C {devices/lab_wire.sym} -490 610 2 0 {name=l57 lab=oa_outn}
C {devices/lab_wire.sym} -295 690 0 1 {name=l58 lab=oa_outn}
C {devices/lab_wire.sym} 320 260 0 0 {name=l59 lab=oa_outn}
C {devices/lab_wire.sym} 895 610 2 0 {name=l60 lab=oa_outn}
C {devices/lab_wire.sym} 1120 610 2 0 {name=l61 lab=oa_outn}
C {devices/lab_wire.sym} 1300 690 0 1 {name=l62 lab=oa_outn}
C {devices/lab_wire.sym} -225 610 2 0 {name=l63 lab=oa_outp}
C {devices/lab_wire.sym} 105 610 2 0 {name=l64 lab=oa_outp}
C {devices/lab_wire.sym} 670 690 0 1 {name=l65 lab=oa_outp}
C {devices/lab_wire.sym} 855 200 0 1 {name=l66 lab=oa_outp}
C {devices/lab_wire.sym} 1500 610 2 0 {name=l67 lab=oa_outp}
C {devices/lab_wire.sym} 1500 690 0 1 {name=l68 lab=oa_outp}
C {devices/lab_wire.sym} 2195 690 0 1 {name=l69 lab=oa_outp}
C {devices/lab_wire.sym} 105 170 0 1 {name=l70 lab=oa_tail}
C {devices/lab_wire.sym} 670 90 2 0 {name=l71 lab=oa_tail}
C {devices/lab_wire.sym} 1120 170 0 1 {name=l72 lab=oa_tail}
C {devices/lab_wire.sym} -1435 870 2 0 {name=l73 lab=sc_n}
C {devices/lab_wire.sym} -895 870 2 0 {name=l74 lab=sc_n}
C {devices/lab_wire.sym} -65 870 2 0 {name=l75 lab=sc_n}
C {devices/lab_wire.sym} -65 950 0 1 {name=l76 lab=sc_n}
C {devices/lab_wire.sym} 180 870 2 0 {name=l77 lab=sc_n}
C {devices/lab_wire.sym} 1300 950 0 1 {name=l78 lab=sc_n}
C {devices/lab_wire.sym} 1705 870 2 0 {name=l79 lab=sc_n}
C {devices/lab_wire.sym} -650 870 2 0 {name=l80 lab=sc_p}
C {devices/lab_wire.sym} 420 870 2 0 {name=l81 lab=sc_p}
C {devices/lab_wire.sym} 1055 870 2 0 {name=l82 lab=sc_p}
C {devices/lab_wire.sym} 1055 950 0 1 {name=l83 lab=sc_p}
C {devices/lab_wire.sym} 1500 1010 0 0 {name=l84 lab=sc_p}
C {devices/lab_wire.sym} 1950 870 2 0 {name=l85 lab=sc_p}
C {devices/lab_wire.sym} 2380 870 2 0 {name=l86 lab=sc_p}
C {devices/lab_wire.sym} 180 690 0 1 {name=l87 lab=sum_n}
C {devices/lab_wire.sym} 640 560 0 1 {name=l88 lab=sum_n}
C {devices/lab_wire.sym} 640 820 0 1 {name=l89 lab=sum_n}
C {devices/lab_wire.sym} 1055 690 0 1 {name=l90 lab=sum_n}
C {devices/lab_wire.sym} 1705 690 0 1 {name=l91 lab=sum_n}
C {devices/lab_wire.sym} 1950 690 0 1 {name=l92 lab=sum_n}
C {devices/lab_wire.sym} -895 690 0 1 {name=l93 lab=sum_p}
C {devices/lab_wire.sym} -650 690 0 1 {name=l94 lab=sum_p}
C {devices/lab_wire.sym} -65 690 0 1 {name=l95 lab=sum_p}
C {devices/lab_wire.sym} 340 620 0 0 {name=l96 lab=sum_p}
C {devices/lab_wire.sym} 340 880 0 0 {name=l97 lab=sum_p}
C {devices/lab_wire.sym} 420 690 0 1 {name=l98 lab=sum_p}
C {devices/lab_wire.sym} 205 520 0 1 {name=l99 lab=vb1}
C {devices/lab_wire.sym} 1080 460 0 1 {name=l100 lab=vb1}
C {devices/lab_wire.sym} -255 840 2 0 {name=l101 lab=vb2}
C {devices/lab_wire.sym} 570 780 0 0 {name=l102 lab=vb2}
C {devices/lab_wire.sym} 320 0 0 0 {name=l103 lab=vb3}
C {devices/lab_wire.sym} 630 -60 0 1 {name=l104 lab=vb3}
C {devices/lab_wire.sym} -325 260 0 0 {name=l105 lab=vb4}
C {devices/lab_wire.sym} 620 200 0 1 {name=l106 lab=vb4}
C {devices/lab_wire.sym} -1435 690 0 1 {name=l107 lab=vinn}
C {devices/lab_wire.sym} 2380 690 0 1 {name=l108 lab=vinp}
C {devices/lab_wire.sym} -910 430 0 1 {name=l109 lab=voutn}
C {devices/lab_wire.sym} 1690 430 0 1 {name=l110 lab=voutn}
C {devices/lab_wire.sym} -910 610 2 0 {name=l111 lab=voutp}
C {devices/lab_wire.sym} 1690 610 2 0 {name=l112 lab=voutp}
C {devices/lab_wire.sym} 45 614 2 0 {name=l113 lab=vdd}
C {devices/lab_wire.sym} 730 94 2 0 {name=l114 lab=vdd}
C {devices/lab_wire.sym} -590 874 2 0 {name=l115 lab=vdd}
C {devices/lab_wire.sym} 1765 874 2 0 {name=l116 lab=vdd}
C {devices/lab_wire.sym} -835 874 2 0 {name=l117 lab=vdd}
C {devices/lab_wire.sym} 2010 874 2 0 {name=l118 lab=vdd}
C {devices/lab_wire.sym} 1180 354 2 0 {name=l119 lab=vdd}
C {devices/lab_wire.sym} 1360 1134 2 0 {name=l120 lab=vdd}
C {devices/lab_wire.sym} 1560 1134 2 0 {name=l121 lab=vdd}
C {devices/lab_wire.sym} -430 614 2 0 {name=l122 lab=vdd}
C {devices/lab_wire.sym} 1560 614 2 0 {name=l123 lab=vdd}
C {devices/lab_wire.sym} -1040 874 2 0 {name=l124 lab=vdd}
C {devices/lab_wire.sym} 2255 874 2 0 {name=l125 lab=vdd}
C {devices/lab_wire.sym} 45 354 2 0 {name=l126 lab=vdd}
C {devices/lab_wire.sym} 480 94 2 0 {name=l127 lab=vdd}
C {devices/lab_wire.sym} 480 354 2 0 {name=l128 lab=vdd}
C {devices/lab_wire.sym} 720 354 2 0 {name=l129 lab=vdd}
C {devices/lab_wire.sym} 955 354 2 0 {name=l130 lab=vdd}
C {devices/lab_wire.sym} -165 354 2 0 {name=l131 lab=vdd}
C {devices/lab_wire.sym} 1180 614 2 0 {name=l132 lab=vdd}
C {devices/lab_wire.sym} -355 874 2 0 {name=l133 lab=vss}
C {devices/lab_wire.sym} 730 874 2 0 {name=l134 lab=vss}
C {devices/lab_wire.sym} -355 1134 2 0 {name=l135 lab=vss}
C {devices/lab_wire.sym} 730 1134 2 0 {name=l136 lab=vss}
C {devices/lab_wire.sym} 480 614 2 0 {name=l137 lab=vss}
C {devices/lab_wire.sym} 720 614 2 0 {name=l138 lab=vss}
C {devices/lab_wire.sym} 480 874 2 0 {name=l139 lab=vss}
C {devices/lab_wire.sym} 240 874 2 0 {name=l140 lab=vss}
C {devices/lab_wire.sym} -5 874 2 0 {name=l141 lab=vss}
C {devices/lab_wire.sym} 1115 874 2 0 {name=l142 lab=vss}
C {devices/lab_wire.sym} -5 1134 2 0 {name=l143 lab=vss}
C {devices/lab_wire.sym} 1115 1134 2 0 {name=l144 lab=vss}
C {devices/lab_wire.sym} 955 614 2 0 {name=l145 lab=vss}
C {devices/lab_wire.sym} -165 614 2 0 {name=l146 lab=vss}
C {devices/lab_wire.sym} 1360 874 2 0 {name=l147 lab=vss}
C {devices/lab_wire.sym} 1560 874 2 0 {name=l148 lab=vss}
C {devices/lab_wire.sym} -1775 950 0 1 {name=l149 lab=vb1}
C {devices/lab_wire.sym} -1775 1130 2 0 {name=l150 lab=vss}
C {devices/lab_wire.sym} -1775 870 2 0 {name=l151 lab=vss}
C {devices/lab_wire.sym} -1775 610 2 0 {name=l152 lab=vss}
C {devices/lab_wire.sym} -1775 350 2 0 {name=l153 lab=vss}
C {devices/lab_wire.sym} -1775 690 0 1 {name=l154 lab=vb2}
C {devices/lab_wire.sym} -1775 430 0 1 {name=l155 lab=vb3}
C {devices/lab_wire.sym} -1775 170 0 1 {name=l156 lab=vb4}
C {devices/lab_wire.sym} 420 610 2 0 {name=l157 lab=vss}
C {devices/ipin.sym} -1975 520 0 0 {name=p0 lab=clk_phi_1}
C {devices/ipin.sym} -1975 640 0 0 {name=p1 lab=clk_phi_2}
C {devices/ipin.sym} -1975 780 0 0 {name=p2 lab=clk_ch_rrl}
C {devices/ipin.sym} -1975 900 0 0 {name=p3 lab=clk_ch_rrl_not}
C {devices/iopin.sym} -1435 1320 0 0 {name=p4 lab=voutn}
C {devices/iopin.sym} -910 1320 0 0 {name=p5 lab=voutp}
C {devices/iopin.sym} -790 1320 0 0 {name=p6 lab=vinn}
C {devices/iopin.sym} 2380 1320 0 0 {name=p7 lab=vinp}
