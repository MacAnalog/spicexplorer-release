v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_005_hsu_pga_ideal} -3975 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -1875 0 1 0 {name=CA1 value='Cu' m=x_dut_ca1_m}
C {devices/capa_np.sym} -1375 0 1 0 {name=CA2 value='Cu' m=x_dut_ca2_m}
C {devices/capa_np.sym} -375 0 1 0 {name=CA3 value='Cu' m=x_dut_ca3_m}
C {devices/capa_np.sym} 335 0 1 0 {name=CA4 value='Cu' m=x_dut_ca4_m}
C {devices/capa_np.sym} 1480 0 1 0 {name=CB1 value='Cu' m=x_dut_cb1_m}
C {devices/capa_np.sym} 1670 0 1 0 {name=CB2 value='Cu' m=x_dut_cb2_m}
C {devices/capa_np.sym} 3285 0 1 0 {name=CB3 value='Cu' m=x_dut_cb3_m}
C {devices/capa_np.sym} 3450 0 1 0 {name=CB4 value='Cu' m=x_dut_cb4_m}
C {devices/capa_np.sym} -2965 0 1 0 {name=CF1 value='x_dut_cf1_value'}
C {devices/capa_np.sym} -1135 0 1 0 {name=CF2 value='x_dut_cf2_value'}
C {devices/capa_np.sym} 140 0 1 0 {name=CIN value='cin_val'}
C {devices/capa_np.sym} -2325 0 1 0 {name=COUT value='cout_val'}
C {devices/vccs.sym} -1645 0 1 0 {name=GM value="\{gm_val\}"}
C {devices/res_np.sym} -560 0 1 0 {name=RIN value='rin_val'}
C {devices/res_np.sym} -2075 0 1 0 {name=ROUT value='rout_val'}
C {devices/sg13_lv_pmos_np.sym} -3595 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -3935 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -2580 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -3255 0 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 845 0 0 1 {name=MA1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xma1_w l=x_dut_xma1_l m=x_dut_xma1_m}
C {devices/sg13_lv_pmos_np.sym} -75 0 0 1 {name=MA10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xma10_w l=x_dut_xma10_l m=x_dut_xma10_m}
C {devices/sg13_lv_nmos_np.sym} 2420 0 0 1 {name=MA11 model=sg13_lv_nmos spiceprefix=X w=x_dut_xma11_w l=x_dut_xma11_l m=x_dut_xma11_m}
C {devices/sg13_lv_pmos_np.sym} 2880 0 0 1 {name=MA12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xma12_w l=x_dut_xma12_l m=x_dut_xma12_m}
C {devices/sg13_lv_pmos_np.sym} 620 0 0 1 {name=MA2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xma2_w l=x_dut_xma2_l m=x_dut_xma2_m}
C {devices/sg13_lv_nmos_np.sym} 2185 0 0 1 {name=MA3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xma3_w l=x_dut_xma3_l m=x_dut_xma3_m}
C {devices/sg13_lv_pmos_np.sym} 1955 0 0 1 {name=MA4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xma4_w l=x_dut_xma4_l m=x_dut_xma4_m}
C {devices/sg13_lv_nmos_np.sym} 1300 0 0 1 {name=MA5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xma5_w l=x_dut_xma5_l m=x_dut_xma5_m}
C {devices/sg13_lv_pmos_np.sym} 1075 0 0 1 {name=MA6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xma6_w l=x_dut_xma6_l m=x_dut_xma6_m}
C {devices/sg13_lv_nmos_np.sym} 3105 0 0 1 {name=MA7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xma7_w l=x_dut_xma7_l m=x_dut_xma7_m}
C {devices/sg13_lv_pmos_np.sym} 2645 0 0 1 {name=MA8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xma8_w l=x_dut_xma8_l m=x_dut_xma8_m}
C {devices/sg13_lv_nmos_np.sym} -745 0 0 1 {name=MA9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xma9_w l=x_dut_xma9_l m=x_dut_xma9_m}
C {devices/sg13_lv_nmos_np.sym} 5865 0 0 0 {name=MB1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb1_w l=x_dut_xmb1_l m=x_dut_xmb1_m}
C {devices/sg13_lv_pmos_np.sym} 5335 0 0 0 {name=MB10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmb10_w l=x_dut_xmb10_l m=x_dut_xmb10_m}
C {devices/sg13_lv_nmos_np.sym} 4165 0 0 0 {name=MB11 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb11_w l=x_dut_xmb11_l m=x_dut_xmb11_m}
C {devices/sg13_lv_pmos_np.sym} 4625 0 0 0 {name=MB12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmb12_w l=x_dut_xmb12_l m=x_dut_xmb12_m}
C {devices/sg13_lv_pmos_np.sym} 5640 0 0 0 {name=MB2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmb2_w l=x_dut_xmb2_l m=x_dut_xmb2_m}
C {devices/sg13_lv_nmos_np.sym} 3930 0 0 0 {name=MB3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb3_w l=x_dut_xmb3_l m=x_dut_xmb3_m}
C {devices/sg13_lv_pmos_np.sym} 3705 0 0 0 {name=MB4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmb4_w l=x_dut_xmb4_l m=x_dut_xmb4_m}
C {devices/sg13_lv_nmos_np.sym} 6320 0 0 0 {name=MB5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb5_w l=x_dut_xmb5_l m=x_dut_xmb5_m}
C {devices/sg13_lv_pmos_np.sym} 6090 0 0 0 {name=MB6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmb6_w l=x_dut_xmb6_l m=x_dut_xmb6_m}
C {devices/sg13_lv_nmos_np.sym} 4860 0 0 0 {name=MB7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb7_w l=x_dut_xmb7_l m=x_dut_xmb7_m}
C {devices/sg13_lv_pmos_np.sym} 4400 0 0 0 {name=MB8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmb8_w l=x_dut_xmb8_l m=x_dut_xmb8_m}
C {devices/sg13_lv_nmos_np.sym} 5110 0 0 0 {name=MB9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb9_w l=x_dut_xmb9_l m=x_dut_xmb9_m}
N -4015 0 -4015 94 {}
N -3955 -90 -3955 -30 {}
N -3955 30 -3955 70 {}
N -3915 0 -3915 70 {}
N -3675 0 -3675 94 {}
N -3615 -60 -3615 -30 {}
N -3615 30 -3615 70 {}
N -3575 0 -3575 70 {}
N -3335 0 -3335 94 {}
N -3275 -90 -3275 -30 {}
N -3275 30 -3275 70 {}
N -3235 0 -3235 70 {}
N -2660 0 -2660 94 {}
N -2600 -60 -2600 -30 {}
N -2600 30 -2600 70 {}
N -2560 0 -2560 70 {}
N -2385 -60 -2385 0 {}
N -2295 0 -2295 60 {}
N -2265 0 -2265 60 {}
N -2135 -60 -2135 0 {}
N -2015 -60 -2015 60 {}
N -1845 0 -1845 60 {}
N -1665 -100 -1665 -40 {}
N -1625 -100 -1625 -40 {}
N -1585 -60 -1585 0 {}
N -1405 -60 -1405 0 {}
N -1345 0 -1345 60 {}
N -825 0 -825 94 {}
N -765 -90 -765 -30 {}
N -765 30 -765 60 {}
N -155 0 -155 94 {}
N -95 -60 -95 -30 {}
N -95 30 -95 60 {}
N 275 0 275 60 {}
N 365 0 365 60 {}
N 540 0 540 94 {}
N 600 -60 600 -30 {}
N 600 30 600 90 {}
N 765 0 765 94 {}
N 825 -60 825 -30 {}
N 825 30 825 90 {}
N 1055 -60 1055 -30 {}
N 1055 30 1055 90 {}
N 1220 0 1220 94 {}
N 1280 -60 1280 -30 {}
N 1420 -120 1420 0 {}
N 1510 0 1510 60 {}
N 1700 0 1700 60 {}
N 1875 0 1875 94 {}
N 1935 -60 1935 -30 {}
N 1935 30 1935 90 {}
N 2105 0 2105 94 {}
N 2165 -60 2165 -30 {}
N 2165 30 2165 90 {}
N 2340 0 2340 94 {}
N 2400 -60 2400 -30 {}
N 2400 30 2400 90 {}
N 2565 0 2565 94 {}
N 2625 -60 2625 -30 {}
N 2625 30 2625 90 {}
N 2800 0 2800 94 {}
N 2860 -60 2860 -30 {}
N 2860 30 2860 90 {}
N 3025 0 3025 94 {}
N 3085 -60 3085 -30 {}
N 3085 30 3085 90 {}
N 3125 0 3125 60 {}
N 3315 0 3315 60 {}
N 3480 0 3480 60 {}
N 3725 -60 3725 -30 {}
N 3725 30 3725 90 {}
N 3785 0 3785 94 {}
N 3950 -60 3950 -30 {}
N 3950 30 3950 60 {}
N 4010 0 4010 94 {}
N 4185 -60 4185 -30 {}
N 4185 30 4185 90 {}
N 4245 0 4245 94 {}
N 4420 -60 4420 -30 {}
N 4420 30 4420 90 {}
N 4480 0 4480 94 {}
N 4645 -60 4645 -30 {}
N 4645 30 4645 90 {}
N 4705 0 4705 94 {}
N 4880 -60 4880 -30 {}
N 4880 30 4880 90 {}
N 4940 0 4940 94 {}
N 5130 -120 5130 -30 {}
N 5130 30 5130 90 {}
N 5190 0 5190 94 {}
N 5355 -60 5355 -30 {}
N 5355 30 5355 90 {}
N 5415 0 5415 94 {}
N 5660 -60 5660 -30 {}
N 5660 30 5660 90 {}
N 5720 0 5720 94 {}
N 5885 -60 5885 -30 {}
N 5885 30 5885 90 {}
N 5945 0 5945 94 {}
N 6110 -60 6110 -30 {}
N 6110 30 6110 90 {}
N 6170 0 6170 94 {}
N 6340 -60 6340 -30 {}
N 6340 30 6340 60 {}
N 6400 0 6400 94 {}
N -4410 -150 6820 -150 {}
N 1420 -120 5130 -120 {}
N -3955 -60 -3615 -60 {}
N -3275 -60 -2600 -60 {}
N -2385 -60 -2135 -60 {}
N -2015 -60 -1585 -60 {}
N -765 -60 1280 -60 {}
N 1935 -60 4880 -60 {}
N 5130 -60 6340 -60 {}
N -4015 0 -3955 0 {}
N -3915 0 -3855 0 {}
N -3675 0 -3615 0 {}
N -3575 0 -3515 0 {}
N -3335 0 -3275 0 {}
N -3235 0 -3175 0 {}
N -3055 0 -2995 0 {}
N -2935 0 -2845 0 {}
N -2660 0 -2600 0 {}
N -2560 0 -2325 0 {}
N -2295 0 -2265 0 {}
N -2135 0 -2105 0 {}
N -2045 0 -2015 0 {}
N -1935 0 -1905 0 {}
N -1845 0 -1815 0 {}
N -1705 0 -1675 0 {}
N -1615 0 -1585 0 {}
N -1435 0 -1405 0 {}
N -1345 0 -1315 0 {}
N -1225 0 -1165 0 {}
N -1105 0 -1015 0 {}
N -825 0 -765 0 {}
N -725 0 -695 0 {}
N -620 0 -590 0 {}
N -530 0 -500 0 {}
N -465 0 -405 0 {}
N -345 0 -315 0 {}
N -155 0 -95 0 {}
N -55 0 -25 0 {}
N 50 0 110 0 {}
N 170 0 200 0 {}
N 245 0 305 0 {}
N 365 0 395 0 {}
N 540 0 600 0 {}
N 640 0 670 0 {}
N 765 0 825 0 {}
N 865 0 895 0 {}
N 1095 0 1125 0 {}
N 1220 0 1280 0 {}
N 1320 0 1350 0 {}
N 1420 0 1450 0 {}
N 1510 0 1540 0 {}
N 1580 0 1640 0 {}
N 1700 0 1730 0 {}
N 1875 0 1935 0 {}
N 1975 0 2035 0 {}
N 2105 0 2165 0 {}
N 2205 0 2265 0 {}
N 2340 0 2400 0 {}
N 2440 0 2500 0 {}
N 2565 0 2625 0 {}
N 2665 0 2725 0 {}
N 2800 0 2860 0 {}
N 2900 0 2960 0 {}
N 3025 0 3085 0 {}
N 3125 0 3155 0 {}
N 3225 0 3255 0 {}
N 3315 0 3345 0 {}
N 3360 0 3420 0 {}
N 3480 0 3510 0 {}
N 3655 0 3685 0 {}
N 3725 0 3785 0 {}
N 3850 0 3910 0 {}
N 3950 0 4010 0 {}
N 4085 0 4145 0 {}
N 4185 0 4245 0 {}
N 4320 0 4380 0 {}
N 4420 0 4480 0 {}
N 4545 0 4605 0 {}
N 4645 0 4705 0 {}
N 4780 0 4840 0 {}
N 4880 0 4940 0 {}
N 5030 0 5090 0 {}
N 5130 0 5190 0 {}
N 5255 0 5315 0 {}
N 5355 0 5415 0 {}
N 5560 0 5620 0 {}
N 5660 0 5720 0 {}
N 5785 0 5845 0 {}
N 5885 0 5945 0 {}
N 6010 0 6070 0 {}
N 6110 0 6170 0 {}
N 6240 0 6300 0 {}
N 6340 0 6400 0 {}
N 995 30 1280 30 {}
N -2265 60 -2015 60 {}
N -765 60 275 60 {}
N 3725 60 3950 60 {}
N 6110 60 6340 60 {}
N -3955 70 -3915 70 {}
N -3615 70 -3575 70 {}
N -3275 70 -3235 70 {}
N -2600 70 -2560 70 {}
N -4410 140 6820 140 {}
C {devices/lab_wire.sym} -4410 -150 0 0 {name=l0 lab=VDD}
C {devices/lab_wire.sym} -4410 140 0 0 {name=l1 lab=VSS}
C {devices/lab_wire.sym} 2035 0 0 1 {name=l2 lab=V_D0}
C {devices/lab_wire.sym} 3685 0 0 0 {name=l3 lab=V_D0}
C {devices/lab_wire.sym} 5785 0 0 0 {name=l4 lab=V_D0}
C {devices/lab_wire.sym} 2265 0 0 1 {name=l5 lab=V_D0_NOT}
C {devices/lab_wire.sym} 3850 0 0 0 {name=l6 lab=V_D0_NOT}
C {devices/lab_wire.sym} 5560 0 0 0 {name=l7 lab=V_D0_NOT}
C {devices/lab_wire.sym} 2725 0 0 1 {name=l8 lab=V_D1}
C {devices/lab_wire.sym} 4320 0 0 0 {name=l9 lab=V_D1}
C {devices/lab_wire.sym} 6240 0 0 0 {name=l10 lab=V_D1}
C {devices/lab_wire.sym} 3125 60 2 0 {name=l11 lab=V_D1_NOT}
C {devices/lab_wire.sym} 4780 0 0 0 {name=l12 lab=V_D1_NOT}
C {devices/lab_wire.sym} 6010 0 0 0 {name=l13 lab=V_D1_NOT}
C {devices/lab_wire.sym} 2960 0 0 1 {name=l14 lab=V_D2}
C {devices/lab_wire.sym} 4545 0 0 0 {name=l15 lab=V_D2}
C {devices/lab_wire.sym} 5030 0 0 0 {name=l16 lab=V_D2}
C {devices/lab_wire.sym} 2500 0 0 1 {name=l17 lab=V_D2_NOT}
C {devices/lab_wire.sym} 4085 0 0 0 {name=l18 lab=V_D2_NOT}
C {devices/lab_wire.sym} 5255 0 0 0 {name=l19 lab=V_D2_NOT}
C {devices/lab_wire.sym} -1405 -60 0 1 {name=l20 lab=bota0}
C {devices/lab_wire.sym} 600 90 2 0 {name=l21 lab=bota0}
C {devices/lab_wire.sym} 825 90 2 0 {name=l22 lab=bota0}
C {devices/lab_wire.sym} 1935 90 2 0 {name=l23 lab=bota0}
C {devices/lab_wire.sym} 2165 90 2 0 {name=l24 lab=bota0}
C {devices/lab_wire.sym} -465 0 0 0 {name=l25 lab=bota1}
C {devices/lab_wire.sym} 1055 90 2 0 {name=l26 lab=bota1}
C {devices/lab_wire.sym} 2625 90 2 0 {name=l27 lab=bota1}
C {devices/lab_wire.sym} 3085 90 2 0 {name=l28 lab=bota1}
C {devices/lab_wire.sym} 245 0 0 0 {name=l29 lab=bota2}
C {devices/lab_wire.sym} 2400 90 2 0 {name=l30 lab=bota2}
C {devices/lab_wire.sym} 2860 90 2 0 {name=l31 lab=bota2}
C {devices/lab_wire.sym} 1580 0 0 0 {name=l32 lab=botb0}
C {devices/lab_wire.sym} 3725 90 2 0 {name=l33 lab=botb0}
C {devices/lab_wire.sym} 5660 90 2 0 {name=l34 lab=botb0}
C {devices/lab_wire.sym} 5885 90 2 0 {name=l35 lab=botb0}
C {devices/lab_wire.sym} 3255 0 0 0 {name=l36 lab=botb1}
C {devices/lab_wire.sym} 4420 90 2 0 {name=l37 lab=botb1}
C {devices/lab_wire.sym} 4880 90 2 0 {name=l38 lab=botb1}
C {devices/lab_wire.sym} 6110 90 2 0 {name=l39 lab=botb1}
C {devices/lab_wire.sym} 3360 0 0 0 {name=l40 lab=botb2}
C {devices/lab_wire.sym} 4185 90 2 0 {name=l41 lab=botb2}
C {devices/lab_wire.sym} 4645 90 2 0 {name=l42 lab=botb2}
C {devices/lab_wire.sym} 5130 90 2 0 {name=l43 lab=botb2}
C {devices/lab_wire.sym} 5355 90 2 0 {name=l44 lab=botb2}
C {devices/lab_wire.sym} -3275 -90 0 1 {name=l45 lab=pr_mid_n}
C {devices/lab_wire.sym} -3955 -90 0 1 {name=l46 lab=pr_mid_p}
C {devices/lab_wire.sym} -3175 0 0 1 {name=l47 lab=sum_n}
C {devices/lab_wire.sym} -1665 -100 0 1 {name=l48 lab=sum_n}
C {devices/lab_wire.sym} -1225 0 0 0 {name=l49 lab=sum_n}
C {devices/lab_wire.sym} -590 0 0 0 {name=l50 lab=sum_n}
C {devices/lab_wire.sym} 50 0 0 0 {name=l51 lab=sum_n}
C {devices/lab_wire.sym} 1510 60 2 0 {name=l52 lab=sum_n}
C {devices/lab_wire.sym} 1700 60 2 0 {name=l53 lab=sum_n}
C {devices/lab_wire.sym} 3315 60 2 0 {name=l54 lab=sum_n}
C {devices/lab_wire.sym} 3480 60 2 0 {name=l55 lab=sum_n}
C {devices/lab_wire.sym} -3515 0 0 1 {name=l56 lab=sum_p}
C {devices/lab_wire.sym} -3055 0 0 0 {name=l57 lab=sum_p}
C {devices/lab_wire.sym} -1845 60 2 0 {name=l58 lab=sum_p}
C {devices/lab_wire.sym} -1625 -100 0 1 {name=l59 lab=sum_p}
C {devices/lab_wire.sym} -1345 60 2 0 {name=l60 lab=sum_p}
C {devices/lab_wire.sym} -530 0 0 0 {name=l61 lab=sum_p}
C {devices/lab_wire.sym} -345 0 0 0 {name=l62 lab=sum_p}
C {devices/lab_wire.sym} 170 0 0 0 {name=l63 lab=sum_p}
C {devices/lab_wire.sym} 365 60 2 0 {name=l64 lab=sum_p}
C {devices/lab_wire.sym} -765 -90 0 1 {name=l65 lab=vinp}
C {devices/lab_wire.sym} -2500 0 0 1 {name=l66 lab=voutn}
C {devices/lab_wire.sym} -1675 0 0 0 {name=l67 lab=voutn}
C {devices/lab_wire.sym} -3855 0 0 1 {name=l68 lab=voutp}
C {devices/lab_wire.sym} -2295 60 2 0 {name=l69 lab=voutp}
C {devices/lab_wire.sym} -155 94 2 0 {name=l70 lab=VDD}
C {devices/lab_wire.sym} 2800 94 2 0 {name=l71 lab=VDD}
C {devices/lab_wire.sym} 540 94 2 0 {name=l72 lab=VDD}
C {devices/lab_wire.sym} 1875 94 2 0 {name=l73 lab=VDD}
C {devices/lab_wire.sym} 1055 0 0 0 {name=l74 lab=VDD}
C {devices/lab_wire.sym} 2565 94 2 0 {name=l75 lab=VDD}
C {devices/lab_wire.sym} 5415 94 2 0 {name=l76 lab=VDD}
C {devices/lab_wire.sym} 4705 94 2 0 {name=l77 lab=VDD}
C {devices/lab_wire.sym} 5720 94 2 0 {name=l78 lab=VDD}
C {devices/lab_wire.sym} 3785 94 2 0 {name=l79 lab=VDD}
C {devices/lab_wire.sym} 6170 94 2 0 {name=l80 lab=VDD}
C {devices/lab_wire.sym} 4480 94 2 0 {name=l81 lab=VDD}
C {devices/lab_wire.sym} 765 94 2 0 {name=l82 lab=VSS}
C {devices/lab_wire.sym} 2340 94 2 0 {name=l83 lab=VSS}
C {devices/lab_wire.sym} 2105 94 2 0 {name=l84 lab=VSS}
C {devices/lab_wire.sym} 1220 94 2 0 {name=l85 lab=VSS}
C {devices/lab_wire.sym} 3025 94 2 0 {name=l86 lab=VSS}
C {devices/lab_wire.sym} -825 94 2 0 {name=l87 lab=VSS}
C {devices/lab_wire.sym} 5945 94 2 0 {name=l88 lab=VSS}
C {devices/lab_wire.sym} 4245 94 2 0 {name=l89 lab=VSS}
C {devices/lab_wire.sym} 4010 94 2 0 {name=l90 lab=VSS}
C {devices/lab_wire.sym} 6400 94 2 0 {name=l91 lab=VSS}
C {devices/lab_wire.sym} 4940 94 2 0 {name=l92 lab=VSS}
C {devices/lab_wire.sym} 5190 94 2 0 {name=l93 lab=VSS}
C {devices/lab_wire.sym} -2660 94 2 0 {name=l94 lab=pr_mid_n}
C {devices/lab_wire.sym} -3335 94 2 0 {name=l95 lab=pr_mid_n}
C {devices/lab_wire.sym} -3675 94 2 0 {name=l96 lab=pr_mid_p}
C {devices/lab_wire.sym} -4015 94 2 0 {name=l97 lab=pr_mid_p}
C {devices/ipin.sym} -695 0 0 0 {name=p0 lab=V_D2}
C {devices/ipin.sym} -25 0 0 0 {name=p1 lab=V_D2_NOT}
C {devices/ipin.sym} 670 0 0 0 {name=p2 lab=V_D0_NOT}
C {devices/ipin.sym} 895 0 0 0 {name=p3 lab=V_D0}
C {devices/ipin.sym} 1125 0 0 0 {name=p4 lab=V_D1_NOT}
C {devices/ipin.sym} 1350 0 0 0 {name=p5 lab=V_D1}
C {devices/opin.sym} -1935 0 0 0 {name=p6 lab=vinp}
C {devices/opin.sym} 4880 -60 0 0 {name=p7 lab=VCM}
C {devices/opin.sym} 6340 -60 0 0 {name=p8 lab=vinn}
C {devices/opin.sym} -2845 0 0 0 {name=p9 lab=voutp}
C {devices/opin.sym} -1015 0 0 0 {name=p10 lab=voutn}
