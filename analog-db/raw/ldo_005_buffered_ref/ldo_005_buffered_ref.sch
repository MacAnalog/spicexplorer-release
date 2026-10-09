v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_005_buffered_ref} -1945 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 595 520 0 0 {name=C1 value='c_out_int'}
C {devices/capa_np.sym} 1305 260 1 0 {name=CEAC value='c_ea_comp'}
C {devices/capa_np.sym} 2685 260 1 0 {name=CRAC value='c_ra_comp'}
C {devices/capa_np.sym} -1530 520 0 0 {name=C_LPF value='c_lpf'}
C {devices/res_np.sym} 2885 260 1 0 {name=R1 value='r_ref_top'}
C {devices/res_np.sym} 1565 520 0 0 {name=R2 value='r_ref_bot'}
C {devices/res_np.sym} 800 520 0 0 {name=R3 value='r_bleed'}
C {devices/res_np.sym} -780 260 1 0 {name=REAND value='r_ea_nd'}
C {devices/res_np.sym} 490 260 1 0 {name=REAZ value='r_ea_z'}
C {devices/res_np.sym} 1750 260 0 0 {name=RRAZ value='r_ra_z'}
C {devices/res_np.sym} 805 260 1 0 {name=R_LPF value='r_lpf'}
C {devices/vsource_np.sym} -1905 520 0 0 {name=VLP value="dc 0" savecurrent=false}
C {devices/vsource_np.sym} -1905 260 0 0 {name=VREF value="dc \{vref_val\}" savecurrent=false}
C {devices/sg13_lv_nmos_np.sym} -1530 260 0 1 {name=MEA_1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_1_w l=x_dut_xmea_1_l}
C {devices/sg13_lv_nmos_np.sym} -1025 260 0 0 {name=MEA_2 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_2_w l=x_dut_xmea_2_l}
C {devices/sg13_lv_pmos_np.sym} -1530 0 0 1 {name=MEA_3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_3_w l=x_dut_xmea_3_l}
C {devices/sg13_lv_pmos_np.sym} -440 260 0 1 {name=MEA_4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_4_w l=x_dut_xmea_4_l}
C {devices/sg13_lv_pmos_np.sym} -1025 0 0 0 {name=MEA_5 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_5_w l=x_dut_xmea_5_l}
C {devices/sg13_lv_pmos_np.sym} -100 0 0 0 {name=MEA_6 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_6_w l=x_dut_xmea_6_l}
C {devices/sg13_lv_nmos_np.sym} 240 260 0 0 {name=MEA_B0 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_b0_w l=x_dut_xmea_b0_l}
C {devices/sg13_lv_nmos_np.sym} -1195 520 0 1 {name=MEA_BC model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_bc_w l=x_dut_xmea_bc_l}
C {devices/sg13_lv_nmos_np.sym} -440 520 0 1 {name=MEA_BF model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_bf_w l=x_dut_xmea_bf_l}
C {devices/sg13_lv_nmos_np.sym} -100 260 0 0 {name=MEA_BO model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_bo_w l=x_dut_xmea_bo_l}
C {devices/sg13_lv_pmos_np.sym} 240 0 0 0 {name=MEA_BP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_bp_w l=x_dut_xmea_bp_l}
C {devices/sg13_lv_pmos_np.sym} 595 0 0 0 {name=MP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
C {devices/sg13_lv_nmos_np.sym} 1130 260 0 1 {name=MRA_1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_1_w l=x_dut_xmra_1_l}
C {devices/sg13_lv_nmos_np.sym} 1510 260 0 0 {name=MRA_2 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_2_w l=x_dut_xmra_2_l}
C {devices/sg13_lv_pmos_np.sym} 1130 0 0 1 {name=MRA_3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmra_3_w l=x_dut_xmra_3_l}
C {devices/sg13_lv_pmos_np.sym} 1510 0 0 0 {name=MRA_4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmra_4_w l=x_dut_xmra_4_l}
C {devices/sg13_lv_pmos_np.sym} 2095 0 0 1 {name=MRA_5 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmra_5_w l=x_dut_xmra_5_l}
C {devices/sg13_lv_nmos_np.sym} 2435 260 0 0 {name=MRA_B0 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_b0_w l=x_dut_xmra_b0_l}
C {devices/sg13_lv_nmos_np.sym} 1300 520 0 1 {name=MRA_BC model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_bc_w l=x_dut_xmra_bc_l}
C {devices/sg13_lv_nmos_np.sym} 2095 260 0 1 {name=MRA_BO model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_bo_w l=x_dut_xmra_bo_l}
C {devices/sg13_lv_pmos_np.sym} 2435 0 0 0 {name=MRA_BP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmra_bp_w l=x_dut_xmra_bp_l}
N -1905 170 -1905 230 {}
N -1905 290 -1905 350 {}
N -1905 430 -1905 490 {}
N -1905 550 -1905 610 {}
N -1610 0 -1610 94 {}
N -1610 260 -1610 354 {}
N -1550 -140 -1550 -30 {}
N -1550 30 -1550 230 {}
N -1550 290 -1550 350 {}
N -1530 460 -1530 490 {}
N -1530 550 -1530 660 {}
N -1480 260 -1480 460 {}
N -1275 520 -1275 614 {}
N -1215 320 -1215 490 {}
N -1215 550 -1215 660 {}
N -1145 520 -1145 580 {}
N -1065 60 -1065 230 {}
N -1005 -140 -1005 -30 {}
N -1005 30 -1005 60 {}
N -1005 290 -1005 320 {}
N -945 0 -945 94 {}
N -945 260 -945 354 {}
N -750 260 -750 320 {}
N -520 260 -520 354 {}
N -520 520 -520 614 {}
N -460 170 -460 230 {}
N -460 290 -460 490 {}
N -460 550 -460 660 {}
N -390 520 -390 580 {}
N -150 0 -150 60 {}
N -150 260 -150 520 {}
N -80 -140 -80 -30 {}
N -80 30 -80 230 {}
N -80 290 -80 660 {}
N -20 0 -20 94 {}
N -20 260 -20 354 {}
N 220 0 220 70 {}
N 220 190 220 260 {}
N 260 -140 260 -30 {}
N 260 30 260 70 {}
N 260 170 260 230 {}
N 260 290 260 660 {}
N 320 0 320 94 {}
N 320 260 320 354 {}
N 520 260 520 320 {}
N 595 460 595 490 {}
N 595 550 595 660 {}
N 615 -140 615 -30 {}
N 615 30 615 460 {}
N 675 0 675 94 {}
N 800 460 800 490 {}
N 800 550 800 660 {}
N 835 260 835 320 {}
N 1050 0 1050 94 {}
N 1050 260 1050 354 {}
N 1110 -140 1110 -30 {}
N 1110 30 1110 230 {}
N 1110 290 1110 350 {}
N 1150 0 1150 70 {}
N 1180 140 1180 260 {}
N 1220 520 1220 614 {}
N 1275 200 1275 260 {}
N 1280 320 1280 490 {}
N 1280 550 1280 660 {}
N 1460 0 1460 60 {}
N 1530 -140 1530 -30 {}
N 1530 30 1530 230 {}
N 1530 290 1530 320 {}
N 1565 140 1565 490 {}
N 1565 550 1565 660 {}
N 1590 0 1590 94 {}
N 1590 260 1590 354 {}
N 1750 200 1750 230 {}
N 1750 290 1750 320 {}
N 2015 60 2015 230 {}
N 2015 260 2015 354 {}
N 2075 -140 2075 -30 {}
N 2075 30 2075 90 {}
N 2075 290 2075 660 {}
N 2145 260 2145 520 {}
N 2205 0 2205 200 {}
N 2415 0 2415 70 {}
N 2415 190 2415 260 {}
N 2455 -140 2455 -30 {}
N 2455 30 2455 230 {}
N 2455 290 2455 660 {}
N 2515 0 2515 94 {}
N 2515 260 2515 354 {}
N 2715 260 2715 320 {}
N 2745 260 2745 320 {}
N 2915 260 2915 320 {}
N -1975 -140 3155 -140 {}
N -1610 0 -1550 0 {}
N -1510 0 -1045 0 {}
N -1005 0 -945 0 {}
N -180 0 -120 0 {}
N -80 0 -20 0 {}
N 160 0 220 0 {}
N 260 0 320 0 {}
N 515 0 575 0 {}
N 615 0 675 0 {}
N 1050 0 1110 0 {}
N 1150 0 1210 0 {}
N 1460 0 1490 0 {}
N 1530 0 1590 0 {}
N 2115 0 2205 0 {}
N 2355 0 2415 0 {}
N 2455 0 2515 0 {}
N -1065 60 -150 60 {}
N 1110 60 1460 60 {}
N 2015 60 2075 60 {}
N 220 70 260 70 {}
N 1110 70 1150 70 {}
N 2415 70 2455 70 {}
N 1180 140 1565 140 {}
N 220 190 260 190 {}
N 2415 190 2455 190 {}
N 1530 200 2205 200 {}
N -1065 230 -1005 230 {}
N 2015 230 2075 230 {}
N -1610 260 -1550 260 {}
N -1510 260 -1450 260 {}
N -1105 260 -1045 260 {}
N -1005 260 -945 260 {}
N -870 260 -810 260 {}
N -750 260 -720 260 {}
N -520 260 -460 260 {}
N -420 260 -360 260 {}
N -180 260 -120 260 {}
N -80 260 -20 260 {}
N 260 260 320 260 {}
N 400 260 460 260 {}
N 520 260 550 260 {}
N 715 260 775 260 {}
N 835 260 865 260 {}
N 1050 260 1110 260 {}
N 1150 260 1180 260 {}
N 1245 260 1275 260 {}
N 1335 260 1365 260 {}
N 1430 260 1490 260 {}
N 1530 260 1590 260 {}
N 2015 260 2075 260 {}
N 2085 260 2415 260 {}
N 2455 260 2515 260 {}
N 2595 260 2655 260 {}
N 2715 260 2745 260 {}
N 2795 260 2855 260 {}
N 2915 260 2945 260 {}
N -1550 320 -1005 320 {}
N 1110 320 1530 320 {}
N 1750 320 2745 320 {}
N -1530 460 -1480 460 {}
N 595 460 800 460 {}
N -1275 520 -1215 520 {}
N -1175 520 -1145 520 {}
N -520 520 -460 520 {}
N -420 520 -150 520 {}
N 1220 520 1280 520 {}
N 1320 520 2145 520 {}
N -1145 580 -390 580 {}
N -1975 660 3155 660 {}
C {devices/lab_wire.sym} -180 260 0 0 {name=l0 lab=ea_ibias}
C {devices/lab_wire.sym} 160 0 0 0 {name=l1 lab=ea_ibias}
C {devices/lab_wire.sym} 260 170 0 1 {name=l2 lab=ea_ibias}
C {devices/lab_wire.sym} -1550 90 2 0 {name=l3 lab=ea_na}
C {devices/lab_wire.sym} -750 320 2 0 {name=l4 lab=ea_na}
C {devices/lab_wire.sym} -360 260 0 1 {name=l5 lab=ea_na}
C {devices/lab_wire.sym} -180 0 0 0 {name=l6 lab=ea_nb}
C {devices/lab_wire.sym} 520 320 2 0 {name=l7 lab=ea_nb}
C {devices/lab_wire.sym} 400 260 0 0 {name=l8 lab=ea_ncz}
C {devices/lab_wire.sym} 1335 260 0 0 {name=l9 lab=ea_ncz}
C {devices/lab_wire.sym} -1450 0 0 1 {name=l10 lab=ea_nd}
C {devices/lab_wire.sym} -870 260 0 0 {name=l11 lab=ea_nd}
C {devices/lab_wire.sym} -460 170 0 1 {name=l12 lab=ea_nd}
C {devices/lab_wire.sym} -460 350 2 0 {name=l13 lab=ea_nlev}
C {devices/lab_wire.sym} -80 90 2 0 {name=l14 lab=ea_out}
C {devices/lab_wire.sym} 515 0 0 0 {name=l15 lab=ea_out}
C {devices/lab_wire.sym} 1275 200 0 1 {name=l16 lab=ea_out}
C {devices/lab_wire.sym} -1550 350 2 0 {name=l17 lab=ea_tail}
C {devices/lab_wire.sym} -1105 260 0 0 {name=l18 lab=lp_brk}
C {devices/lab_wire.sym} 2355 0 0 0 {name=l19 lab=ra_ibias}
C {devices/lab_wire.sym} 1210 0 0 1 {name=l20 lab=ra_na}
C {devices/lab_wire.sym} 2175 0 0 1 {name=l21 lab=ra_nb}
C {devices/lab_wire.sym} 2715 320 2 0 {name=l22 lab=ra_ncz}
C {devices/lab_wire.sym} 1110 350 2 0 {name=l23 lab=ra_tail}
C {devices/lab_wire.sym} -1450 260 0 1 {name=l24 lab=v_lpf_out}
C {devices/lab_wire.sym} 715 260 0 0 {name=l25 lab=v_lpf_out}
C {devices/lab_wire.sym} 1150 260 0 0 {name=l26 lab=v_ref_fb}
C {devices/lab_wire.sym} 2795 260 0 0 {name=l27 lab=v_ref_fb}
C {devices/lab_wire.sym} 835 320 2 0 {name=l28 lab=v_ref_out}
C {devices/lab_wire.sym} 2075 90 2 0 {name=l29 lab=v_ref_out}
C {devices/lab_wire.sym} 2595 260 0 0 {name=l30 lab=v_ref_out}
C {devices/lab_wire.sym} 2915 320 2 0 {name=l31 lab=v_ref_out}
C {devices/lab_wire.sym} 1430 260 0 0 {name=l32 lab=vref}
C {devices/lab_wire.sym} -1610 94 2 0 {name=l33 lab=vdd}
C {devices/lab_wire.sym} -520 354 2 0 {name=l34 lab=vdd}
C {devices/lab_wire.sym} -945 94 2 0 {name=l35 lab=vdd}
C {devices/lab_wire.sym} -20 94 2 0 {name=l36 lab=vdd}
C {devices/lab_wire.sym} 320 94 2 0 {name=l37 lab=vdd}
C {devices/lab_wire.sym} 675 94 2 0 {name=l38 lab=vdd}
C {devices/lab_wire.sym} 1050 94 2 0 {name=l39 lab=vdd}
C {devices/lab_wire.sym} 1590 94 2 0 {name=l40 lab=vdd}
C {devices/lab_wire.sym} 2075 0 0 0 {name=l41 lab=vdd}
C {devices/lab_wire.sym} 2515 94 2 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} -1610 354 2 0 {name=l43 lab=vss}
C {devices/lab_wire.sym} -945 354 2 0 {name=l44 lab=vss}
C {devices/lab_wire.sym} 320 354 2 0 {name=l45 lab=vss}
C {devices/lab_wire.sym} -1275 614 2 0 {name=l46 lab=vss}
C {devices/lab_wire.sym} -520 614 2 0 {name=l47 lab=vss}
C {devices/lab_wire.sym} -20 354 2 0 {name=l48 lab=vss}
C {devices/lab_wire.sym} 1050 354 2 0 {name=l49 lab=vss}
C {devices/lab_wire.sym} 1590 354 2 0 {name=l50 lab=vss}
C {devices/lab_wire.sym} 2515 354 2 0 {name=l51 lab=vss}
C {devices/lab_wire.sym} 1220 614 2 0 {name=l52 lab=vss}
C {devices/lab_wire.sym} 2015 354 2 0 {name=l53 lab=vss}
C {devices/lab_wire.sym} -1905 610 2 0 {name=l54 lab=vout}
C {devices/lab_wire.sym} -1905 350 2 0 {name=l55 lab=vss}
C {devices/lab_wire.sym} -1905 430 0 1 {name=l56 lab=lp_brk}
C {devices/lab_wire.sym} -1905 170 0 1 {name=l57 lab=vref}
C {devices/iopin.sym} -1975 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -1975 660 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 800 460 0 0 {name=p2 lab=vout}
