v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_005_buffered_ref} -1910 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 390 520 0 0 {name=C1 value='c_out_int'}
C {devices/capa_np.sym} 990 260 1 0 {name=CEAC value='c_ea_comp'}
C {devices/capa_np.sym} 2175 260 1 0 {name=CRAC value='c_ra_comp'}
C {devices/capa_np.sym} -1530 520 0 0 {name=C_LPF value='c_lpf'}
C {devices/res_np.sym} 2345 260 1 0 {name=R1 value='r_ref_top'}
C {devices/res_np.sym} 1210 520 0 0 {name=R2 value='r_ref_bot'}
C {devices/res_np.sym} 555 520 0 0 {name=R3 value='r_bleed'}
C {devices/res_np.sym} -895 260 1 0 {name=REAND value='r_ea_nd'}
C {devices/res_np.sym} 285 260 1 0 {name=REAZ value='r_ea_z'}
C {devices/res_np.sym} 1355 260 0 0 {name=RRAZ value='r_ra_z'}
C {devices/res_np.sym} 560 260 1 0 {name=R_LPF value='r_lpf'}
C {devices/vsource_np.sym} -1870 520 0 0 {name=VLP value="dc 0"}
C {devices/vsource_np.sym} -1870 260 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_nmos_np.sym} -1530 260 0 1 {name=MEA_1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_1_w l=x_dut_xmea_1_l}
C {devices/sg13_lv_nmos_np.sym} -1100 260 0 0 {name=MEA_2 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_2_w l=x_dut_xmea_2_l}
C {devices/sg13_lv_pmos_np.sym} -1530 0 0 1 {name=MEA_3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_3_w l=x_dut_xmea_3_l}
C {devices/sg13_lv_pmos_np.sym} -630 260 0 1 {name=MEA_4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_4_w l=x_dut_xmea_4_l}
C {devices/sg13_lv_pmos_np.sym} -1100 0 0 0 {name=MEA_5 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_5_w l=x_dut_xmea_5_l}
C {devices/sg13_lv_pmos_np.sym} -290 0 0 0 {name=MEA_6 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_6_w l=x_dut_xmea_6_l}
C {devices/sg13_lv_nmos_np.sym} 50 260 0 0 {name=MEA_B0 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_b0_w l=x_dut_xmea_b0_l}
C {devices/sg13_lv_nmos_np.sym} -1270 520 0 1 {name=MEA_BC model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_bc_w l=x_dut_xmea_bc_l}
C {devices/sg13_lv_nmos_np.sym} -630 520 0 1 {name=MEA_BF model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_bf_w l=x_dut_xmea_bf_l}
C {devices/sg13_lv_nmos_np.sym} -290 260 0 0 {name=MEA_BO model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_bo_w l=x_dut_xmea_bo_l}
C {devices/sg13_lv_pmos_np.sym} 50 0 0 0 {name=MEA_BP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_bp_w l=x_dut_xmea_bp_l}
C {devices/sg13_lv_pmos_np.sym} 390 0 0 0 {name=MP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
C {devices/sg13_lv_nmos_np.sym} 815 260 0 1 {name=MRA_1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_1_w l=x_dut_xmra_1_l}
C {devices/sg13_lv_nmos_np.sym} 1155 260 0 0 {name=MRA_2 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_2_w l=x_dut_xmra_2_l}
C {devices/sg13_lv_pmos_np.sym} 815 0 0 1 {name=MRA_3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmra_3_w l=x_dut_xmra_3_l}
C {devices/sg13_lv_pmos_np.sym} 1155 0 0 0 {name=MRA_4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmra_4_w l=x_dut_xmra_4_l}
C {devices/sg13_lv_pmos_np.sym} 1625 0 0 1 {name=MRA_5 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmra_5_w l=x_dut_xmra_5_l}
C {devices/sg13_lv_nmos_np.sym} 1965 260 0 0 {name=MRA_B0 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_b0_w l=x_dut_xmra_b0_l}
C {devices/sg13_lv_nmos_np.sym} 985 520 0 1 {name=MRA_BC model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_bc_w l=x_dut_xmra_bc_l}
C {devices/sg13_lv_nmos_np.sym} 1625 260 0 1 {name=MRA_BO model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_bo_w l=x_dut_xmra_bo_l}
C {devices/sg13_lv_pmos_np.sym} 1965 0 0 0 {name=MRA_BP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmra_bp_w l=x_dut_xmra_bp_l}
N -1870 170 -1870 230 {}
N -1870 290 -1870 350 {}
N -1870 430 -1870 490 {}
N -1870 550 -1870 610 {}
N -1610 0 -1610 94 {}
N -1610 260 -1610 354 {}
N -1550 -140 -1550 -30 {}
N -1550 30 -1550 230 {}
N -1550 290 -1550 350 {}
N -1530 460 -1530 490 {}
N -1530 550 -1530 660 {}
N -1480 260 -1480 460 {}
N -1350 520 -1350 614 {}
N -1290 320 -1290 490 {}
N -1290 550 -1290 660 {}
N -1080 -140 -1080 -30 {}
N -1080 30 -1080 60 {}
N -1080 170 -1080 230 {}
N -1080 290 -1080 320 {}
N -1020 0 -1020 94 {}
N -1020 260 -1020 354 {}
N -955 0 -955 260 {}
N -865 260 -865 320 {}
N -835 200 -835 260 {}
N -710 260 -710 354 {}
N -710 520 -710 614 {}
N -650 170 -650 230 {}
N -650 290 -650 490 {}
N -650 550 -650 660 {}
N -340 0 -340 60 {}
N -340 260 -340 520 {}
N -270 -140 -270 -30 {}
N -270 30 -270 230 {}
N -270 290 -270 660 {}
N -210 0 -210 94 {}
N -210 260 -210 354 {}
N 30 0 30 70 {}
N 30 190 30 260 {}
N 70 -140 70 -30 {}
N 70 30 70 70 {}
N 70 170 70 230 {}
N 70 290 70 660 {}
N 130 0 130 94 {}
N 130 260 130 354 {}
N 255 200 255 260 {}
N 315 260 315 320 {}
N 340 0 340 60 {}
N 370 -60 370 0 {}
N 390 460 390 490 {}
N 390 550 390 660 {}
N 410 -140 410 -30 {}
N 410 30 410 460 {}
N 470 0 470 94 {}
N 530 200 530 260 {}
N 555 460 555 490 {}
N 555 550 555 660 {}
N 590 260 590 320 {}
N 735 0 735 94 {}
N 735 260 735 354 {}
N 795 -140 795 -30 {}
N 795 30 795 230 {}
N 795 290 795 350 {}
N 835 0 835 70 {}
N 905 520 905 614 {}
N 930 0 930 260 {}
N 960 200 960 260 {}
N 965 320 965 490 {}
N 965 550 965 660 {}
N 1105 0 1105 60 {}
N 1135 200 1135 260 {}
N 1175 -140 1175 -30 {}
N 1175 30 1175 230 {}
N 1175 290 1175 320 {}
N 1210 260 1210 490 {}
N 1210 550 1210 660 {}
N 1235 0 1235 94 {}
N 1355 200 1355 230 {}
N 1355 290 1355 320 {}
N 1545 0 1545 94 {}
N 1545 260 1545 354 {}
N 1605 -140 1605 -30 {}
N 1605 30 1605 90 {}
N 1605 170 1605 230 {}
N 1605 290 1605 660 {}
N 1675 0 1675 200 {}
N 1675 260 1675 520 {}
N 1945 0 1945 70 {}
N 1945 190 1945 260 {}
N 1985 -140 1985 -30 {}
N 1985 30 1985 230 {}
N 1985 290 1985 660 {}
N 2045 0 2045 94 {}
N 2045 260 2045 354 {}
N 2205 260 2205 320 {}
N 2235 260 2235 320 {}
N 2315 200 2315 260 {}
N 2375 260 2375 320 {}
N -1930 -140 2535 -140 {}
N -1610 0 -1550 0 {}
N -1510 0 -1120 0 {}
N -1080 0 -1020 0 {}
N -370 0 -310 0 {}
N -270 0 -210 0 {}
N -30 0 30 0 {}
N 70 0 130 0 {}
N 410 0 470 0 {}
N 735 0 795 0 {}
N 835 0 895 0 {}
N 1105 0 1135 0 {}
N 1175 0 1235 0 {}
N 1545 0 1605 0 {}
N 1645 0 1705 0 {}
N 1885 0 1945 0 {}
N 1985 0 2045 0 {}
N -1080 60 -340 60 {}
N 795 60 1105 60 {}
N 30 70 70 70 {}
N 795 70 835 70 {}
N 1945 70 1985 70 {}
N 30 190 70 190 {}
N 1945 190 1985 190 {}
N 1175 200 1355 200 {}
N -1610 260 -1550 260 {}
N -1510 260 -1450 260 {}
N -1180 260 -1120 260 {}
N -1080 260 -1020 260 {}
N -985 260 -925 260 {}
N -865 260 -835 260 {}
N -710 260 -650 260 {}
N -610 260 -550 260 {}
N -370 260 -310 260 {}
N -270 260 -210 260 {}
N 70 260 130 260 {}
N 225 260 255 260 {}
N 315 260 345 260 {}
N 500 260 530 260 {}
N 590 260 620 260 {}
N 735 260 795 260 {}
N 835 260 865 260 {}
N 930 260 960 260 {}
N 1020 260 1050 260 {}
N 1105 260 1135 260 {}
N 1545 260 1605 260 {}
N 1645 260 1705 260 {}
N 1985 260 2045 260 {}
N 2085 260 2145 260 {}
N 2205 260 2235 260 {}
N 2285 260 2315 260 {}
N 2375 260 2405 260 {}
N -1550 320 -1080 320 {}
N 795 320 1175 320 {}
N 1355 320 2235 320 {}
N -1530 460 -1480 460 {}
N 390 460 555 460 {}
N -1350 520 -1290 520 {}
N -1250 520 -1190 520 {}
N -710 520 -650 520 {}
N -610 520 -340 520 {}
N 905 520 965 520 {}
N 1005 520 1675 520 {}
N -1930 660 2535 660 {}
C {devices/lab_wire.sym} -1930 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1930 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -1190 520 0 1 {name=l2 lab=ea_ibias}
C {devices/lab_wire.sym} -370 260 0 0 {name=l3 lab=ea_ibias}
C {devices/lab_wire.sym} -30 0 0 0 {name=l4 lab=ea_ibias}
C {devices/lab_wire.sym} 70 170 0 1 {name=l5 lab=ea_ibias}
C {devices/lab_wire.sym} -1550 90 2 0 {name=l6 lab=ea_na}
C {devices/lab_wire.sym} -865 320 2 0 {name=l7 lab=ea_na}
C {devices/lab_wire.sym} -550 260 0 1 {name=l8 lab=ea_na}
C {devices/lab_wire.sym} -370 0 0 0 {name=l9 lab=ea_nb}
C {devices/lab_wire.sym} -1080 170 0 1 {name=l10 lab=ea_nb}
C {devices/lab_wire.sym} 315 320 2 0 {name=l11 lab=ea_nb}
C {devices/lab_wire.sym} 255 200 0 1 {name=l12 lab=ea_ncz}
C {devices/lab_wire.sym} 1020 260 0 0 {name=l13 lab=ea_ncz}
C {devices/lab_wire.sym} -1450 0 0 1 {name=l14 lab=ea_nd}
C {devices/lab_wire.sym} -985 260 0 0 {name=l15 lab=ea_nd}
C {devices/lab_wire.sym} -650 170 0 1 {name=l16 lab=ea_nd}
C {devices/lab_wire.sym} -650 350 2 0 {name=l17 lab=ea_nlev}
C {devices/lab_wire.sym} -270 90 2 0 {name=l18 lab=ea_out}
C {devices/lab_wire.sym} 370 -60 0 1 {name=l19 lab=ea_out}
C {devices/lab_wire.sym} 960 200 0 1 {name=l20 lab=ea_out}
C {devices/lab_wire.sym} -1550 350 2 0 {name=l21 lab=ea_tail}
C {devices/lab_wire.sym} -1180 260 0 0 {name=l22 lab=lp_brk}
C {devices/lab_wire.sym} 1705 260 0 1 {name=l23 lab=ra_ibias}
C {devices/lab_wire.sym} 1885 0 0 0 {name=l24 lab=ra_ibias}
C {devices/lab_wire.sym} 895 0 0 1 {name=l25 lab=ra_na}
C {devices/lab_wire.sym} 1175 90 2 0 {name=l26 lab=ra_nb}
C {devices/lab_wire.sym} 1705 0 0 1 {name=l27 lab=ra_nb}
C {devices/lab_wire.sym} 2205 320 2 0 {name=l28 lab=ra_ncz}
C {devices/lab_wire.sym} 795 350 2 0 {name=l29 lab=ra_tail}
C {devices/lab_wire.sym} -1450 260 0 1 {name=l30 lab=v_lpf_out}
C {devices/lab_wire.sym} 530 200 0 1 {name=l31 lab=v_lpf_out}
C {devices/lab_wire.sym} 835 260 0 0 {name=l32 lab=v_ref_fb}
C {devices/lab_wire.sym} 1210 430 0 1 {name=l33 lab=v_ref_fb}
C {devices/lab_wire.sym} 2315 200 0 1 {name=l34 lab=v_ref_fb}
C {devices/lab_wire.sym} 590 320 2 0 {name=l35 lab=v_ref_out}
C {devices/lab_wire.sym} 1605 90 2 0 {name=l36 lab=v_ref_out}
C {devices/lab_wire.sym} 1605 170 0 1 {name=l37 lab=v_ref_out}
C {devices/lab_wire.sym} 2085 260 0 0 {name=l38 lab=v_ref_out}
C {devices/lab_wire.sym} 2375 320 2 0 {name=l39 lab=v_ref_out}
C {devices/lab_wire.sym} 410 90 2 0 {name=l40 lab=vout}
C {devices/lab_wire.sym} 1135 200 0 1 {name=l41 lab=vref}
C {devices/lab_wire.sym} -1610 94 2 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} -710 354 2 0 {name=l43 lab=vdd}
C {devices/lab_wire.sym} -1020 94 2 0 {name=l44 lab=vdd}
C {devices/lab_wire.sym} -210 94 2 0 {name=l45 lab=vdd}
C {devices/lab_wire.sym} 130 94 2 0 {name=l46 lab=vdd}
C {devices/lab_wire.sym} 470 94 2 0 {name=l47 lab=vdd}
C {devices/lab_wire.sym} 735 94 2 0 {name=l48 lab=vdd}
C {devices/lab_wire.sym} 1235 94 2 0 {name=l49 lab=vdd}
C {devices/lab_wire.sym} 1545 94 2 0 {name=l50 lab=vdd}
C {devices/lab_wire.sym} 2045 94 2 0 {name=l51 lab=vdd}
C {devices/lab_wire.sym} -1610 354 2 0 {name=l52 lab=vss}
C {devices/lab_wire.sym} -1020 354 2 0 {name=l53 lab=vss}
C {devices/lab_wire.sym} 130 354 2 0 {name=l54 lab=vss}
C {devices/lab_wire.sym} -1350 614 2 0 {name=l55 lab=vss}
C {devices/lab_wire.sym} -710 614 2 0 {name=l56 lab=vss}
C {devices/lab_wire.sym} -210 354 2 0 {name=l57 lab=vss}
C {devices/lab_wire.sym} 735 354 2 0 {name=l58 lab=vss}
C {devices/lab_wire.sym} 1175 260 0 0 {name=l59 lab=vss}
C {devices/lab_wire.sym} 2045 354 2 0 {name=l60 lab=vss}
C {devices/lab_wire.sym} 905 614 2 0 {name=l61 lab=vss}
C {devices/lab_wire.sym} 1545 354 2 0 {name=l62 lab=vss}
C {devices/lab_wire.sym} -1870 610 2 0 {name=l63 lab=vout}
C {devices/lab_wire.sym} -1870 350 2 0 {name=l64 lab=vss}
C {devices/lab_wire.sym} -1870 430 0 1 {name=l65 lab=lp_brk}
C {devices/lab_wire.sym} -1870 170 0 1 {name=l66 lab=vref}
C {devices/opin.sym} 2675 30 0 0 {name=p0 lab=vout}
B 8 -1490 182 270 598 {fill=0}
T {NMOS Simple Current Mirror (3 outputs)} -1490 164 0 0 0.3 0.3 {layer=8}
B 10 603 -78 1367 78 {fill=0}
T {PMOS Simple Current Mirror} 603 -96 0 0 0.3 0.3 {layer=10}
B 12 765 182 2185 598 {fill=0}
T {NMOS Simple Current Mirror (2 outputs)} 765 164 0 0 0.3 0.3 {layer=12}
B 21 -1742 182 -888 338 {fill=0}
T {NMOS Differential Pair} -1742 164 0 0 0.3 0.3 {layer=21}
B 15 603 182 1367 338 {fill=0}
T {NMOS Differential Pair} 603 164 0 0 0.3 0.3 {layer=15}
