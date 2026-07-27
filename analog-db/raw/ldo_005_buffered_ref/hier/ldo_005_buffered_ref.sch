v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_005_buffered_ref} -1360 -560 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -880 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_1.sym} -440 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_simple_2.sym} 0 0 0 0 {name=xcm_nmos_simple_2}
C {blocks/dp_nmos_simple_1.sym} 440 0 0 0 {name=xdp_nmos_simple_1}
C {blocks/dp_nmos_simple_2.sym} 880 0 0 0 {name=xdp_nmos_simple_2}
C {devices/capa_np.sym} -1100 360 0 0 {name=C1 value='c_out_int'}
C {devices/capa_np.sym} -880 360 0 0 {name=CEAC value='c_ea_comp'}
C {devices/capa_np.sym} -660 360 0 0 {name=CRAC value='c_ra_comp'}
C {devices/capa_np.sym} -440 360 0 0 {name=C_LPF value='c_lpf'}
C {devices/res_np.sym} -220 360 0 0 {name=R1 value='r_ref_top'}
C {devices/res_np.sym} 0 360 0 0 {name=R2 value='r_ref_bot'}
C {devices/res_np.sym} 220 360 0 0 {name=R3 value='r_bleed'}
C {devices/res_np.sym} 440 360 0 0 {name=REAND value='r_ea_nd'}
C {devices/res_np.sym} 660 360 0 0 {name=REAZ value='r_ea_z'}
C {devices/res_np.sym} 880 360 0 0 {name=RRAZ value='r_ra_z'}
C {devices/res_np.sym} 1100 360 0 0 {name=R_LPF value='r_lpf'}
C {devices/vsource_np.sym} -1320 360 0 0 {name=VLP value="dc 0"}
C {devices/vsource_np.sym} -1320 140 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_pmos_np.sym} -770 -360 0 0 {name=MEA_3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_3_w l=x_dut_xmea_3_l}
C {devices/sg13_lv_pmos_np.sym} -550 -360 0 0 {name=MEA_4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_4_w l=x_dut_xmea_4_l}
C {devices/sg13_lv_pmos_np.sym} -330 -360 0 0 {name=MEA_5 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_5_w l=x_dut_xmea_5_l}
C {devices/sg13_lv_pmos_np.sym} -110 -360 0 0 {name=MEA_6 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_6_w l=x_dut_xmea_6_l}
C {devices/sg13_lv_pmos_np.sym} 110 -360 0 0 {name=MEA_BP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmea_bp_w l=x_dut_xmea_bp_l}
C {devices/sg13_lv_pmos_np.sym} 330 -360 0 0 {name=MP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
C {devices/sg13_lv_pmos_np.sym} 550 -360 0 0 {name=MRA_5 model=sg13_hv_pmos spiceprefix=X w=x_dut_xmra_5_w l=x_dut_xmra_5_l}
C {devices/sg13_lv_pmos_np.sym} 770 -360 0 0 {name=MRA_BP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmra_bp_w l=x_dut_xmra_bp_l}
N -770 -60 -730 -60 {}
C {devices/lab_wire.sym} -730 -60 0 1 {name=l0 lab=ea_ibias}
N -770 -20 -730 -20 {}
C {devices/lab_wire.sym} -730 -20 0 1 {name=l1 lab=ea_nlev}
N -770 20 -730 20 {}
C {devices/lab_wire.sym} -730 20 0 1 {name=l2 lab=ea_out}
N -770 60 -730 60 {}
C {devices/lab_wire.sym} -730 60 0 1 {name=l3 lab=ea_tail}
N -880 120 -880 160 {}
C {devices/lab_wire.sym} -880 160 2 0 {name=l4 lab=vss}
N -330 -20 -290 -20 {}
C {devices/lab_wire.sym} -290 -20 0 1 {name=l5 lab=ra_na}
N -330 20 -290 20 {}
C {devices/lab_wire.sym} -290 20 0 1 {name=l6 lab=ra_nb}
N -440 -80 -440 -120 {}
C {devices/lab_wire.sym} -440 -120 0 1 {name=l7 lab=vdd}
N 110 -40 150 -40 {}
C {devices/lab_wire.sym} 150 -40 0 1 {name=l8 lab=ra_ibias}
N 110 0 150 0 {}
C {devices/lab_wire.sym} 150 0 0 1 {name=l9 lab=ra_tail}
N 110 40 150 40 {}
C {devices/lab_wire.sym} 150 40 0 1 {name=l10 lab=v_ref_out}
N 0 100 0 140 {}
C {devices/lab_wire.sym} 0 140 2 0 {name=l11 lab=vss}
N 330 -20 290 -20 {}
C {devices/lab_wire.sym} 290 -20 0 0 {name=l12 lab=lp_brk}
N 330 20 290 20 {}
C {devices/lab_wire.sym} 290 20 0 0 {name=l13 lab=v_lpf_out}
N 550 -40 590 -40 {}
C {devices/lab_wire.sym} 590 -40 0 1 {name=l14 lab=ea_na}
N 550 0 590 0 {}
C {devices/lab_wire.sym} 590 0 0 1 {name=l15 lab=ea_nb}
N 550 40 590 40 {}
C {devices/lab_wire.sym} 590 40 0 1 {name=l16 lab=ea_tail}
N 440 100 440 140 {}
C {devices/lab_wire.sym} 440 140 2 0 {name=l17 lab=vss}
N 770 -20 730 -20 {}
C {devices/lab_wire.sym} 730 -20 0 0 {name=l18 lab=v_ref_fb}
N 770 20 730 20 {}
C {devices/lab_wire.sym} 730 20 0 0 {name=l19 lab=vref}
N 990 -40 1030 -40 {}
C {devices/lab_wire.sym} 1030 -40 0 1 {name=l20 lab=ra_na}
N 990 0 1030 0 {}
C {devices/lab_wire.sym} 1030 0 0 1 {name=l21 lab=ra_nb}
N 990 40 1030 40 {}
C {devices/lab_wire.sym} 1030 40 0 1 {name=l22 lab=ra_tail}
N 880 100 880 140 {}
C {devices/lab_wire.sym} 880 140 2 0 {name=l23 lab=vss}
N -1100 330 -1100 290 {}
C {devices/lab_wire.sym} -1100 290 0 1 {name=l24 lab=vout}
N -1100 390 -1100 430 {}
C {devices/lab_wire.sym} -1100 430 2 0 {name=l25 lab=vss}
N -880 330 -880 290 {}
C {devices/lab_wire.sym} -880 290 0 1 {name=l26 lab=ea_ncz}
N -880 390 -880 430 {}
C {devices/lab_wire.sym} -880 430 2 0 {name=l27 lab=ea_out}
N -660 330 -660 290 {}
C {devices/lab_wire.sym} -660 290 0 1 {name=l28 lab=ra_ncz}
N -660 390 -660 430 {}
C {devices/lab_wire.sym} -660 430 2 0 {name=l29 lab=v_ref_out}
N -440 330 -440 290 {}
C {devices/lab_wire.sym} -440 290 0 1 {name=l30 lab=v_lpf_out}
N -440 390 -440 430 {}
C {devices/lab_wire.sym} -440 430 2 0 {name=l31 lab=vss}
N -220 330 -220 290 {}
C {devices/lab_wire.sym} -220 290 0 1 {name=l32 lab=v_ref_out}
N -220 390 -220 430 {}
C {devices/lab_wire.sym} -220 430 2 0 {name=l33 lab=v_ref_fb}
N 0 330 0 290 {}
C {devices/lab_wire.sym} 0 290 0 1 {name=l34 lab=v_ref_fb}
N 0 390 0 430 {}
C {devices/lab_wire.sym} 0 430 2 0 {name=l35 lab=vss}
N 220 330 220 290 {}
C {devices/lab_wire.sym} 220 290 0 1 {name=l36 lab=vout}
N 220 390 220 430 {}
C {devices/lab_wire.sym} 220 430 2 0 {name=l37 lab=vss}
N 440 330 440 290 {}
C {devices/lab_wire.sym} 440 290 0 1 {name=l38 lab=ea_na}
N 440 390 440 430 {}
C {devices/lab_wire.sym} 440 430 2 0 {name=l39 lab=ea_nd}
N 660 330 660 290 {}
C {devices/lab_wire.sym} 660 290 0 1 {name=l40 lab=ea_nb}
N 660 390 660 430 {}
C {devices/lab_wire.sym} 660 430 2 0 {name=l41 lab=ea_ncz}
N 880 330 880 290 {}
C {devices/lab_wire.sym} 880 290 0 1 {name=l42 lab=ra_nb}
N 880 390 880 430 {}
C {devices/lab_wire.sym} 880 430 2 0 {name=l43 lab=ra_ncz}
N 1100 330 1100 290 {}
C {devices/lab_wire.sym} 1100 290 0 1 {name=l44 lab=v_ref_out}
N 1100 390 1100 430 {}
C {devices/lab_wire.sym} 1100 430 2 0 {name=l45 lab=v_lpf_out}
N -1320 330 -1320 290 {}
C {devices/lab_wire.sym} -1320 290 0 1 {name=l46 lab=lp_brk}
N -1320 390 -1320 430 {}
C {devices/lab_wire.sym} -1320 430 2 0 {name=l47 lab=vout}
N -1320 110 -1320 70 {}
C {devices/lab_wire.sym} -1320 70 0 1 {name=l48 lab=vref}
N -1320 170 -1320 210 {}
C {devices/lab_wire.sym} -1320 210 2 0 {name=l49 lab=vss}
N -750 -330 -750 -290 {}
C {devices/lab_wire.sym} -750 -290 2 0 {name=l50 lab=ea_na}
N -790 -360 -830 -360 {}
C {devices/lab_wire.sym} -830 -360 0 0 {name=l51 lab=ea_nd}
N -750 -390 -750 -430 {}
C {devices/lab_wire.sym} -750 -430 0 1 {name=l52 lab=vdd}
N -750 -360 -710 -360 {}
C {devices/lab_wire.sym} -710 -360 0 1 {name=l53 lab=vdd}
N -530 -330 -530 -290 {}
C {devices/lab_wire.sym} -530 -290 2 0 {name=l54 lab=ea_nlev}
N -570 -360 -610 -360 {}
C {devices/lab_wire.sym} -610 -360 0 0 {name=l55 lab=ea_na}
N -530 -390 -530 -430 {}
C {devices/lab_wire.sym} -530 -430 0 1 {name=l56 lab=ea_nd}
N -530 -360 -490 -360 {}
C {devices/lab_wire.sym} -490 -360 0 1 {name=l57 lab=vdd}
N -310 -330 -310 -290 {}
C {devices/lab_wire.sym} -310 -290 2 0 {name=l58 lab=ea_nb}
N -350 -360 -390 -360 {}
C {devices/lab_wire.sym} -390 -360 0 0 {name=l59 lab=ea_nd}
N -310 -390 -310 -430 {}
C {devices/lab_wire.sym} -310 -430 0 1 {name=l60 lab=vdd}
N -310 -360 -270 -360 {}
C {devices/lab_wire.sym} -270 -360 0 1 {name=l61 lab=vdd}
N -90 -330 -90 -290 {}
C {devices/lab_wire.sym} -90 -290 2 0 {name=l62 lab=ea_out}
N -130 -360 -170 -360 {}
C {devices/lab_wire.sym} -170 -360 0 0 {name=l63 lab=ea_nb}
N -90 -390 -90 -430 {}
C {devices/lab_wire.sym} -90 -430 0 1 {name=l64 lab=vdd}
N -90 -360 -50 -360 {}
C {devices/lab_wire.sym} -50 -360 0 1 {name=l65 lab=vdd}
N 130 -330 130 -290 {}
C {devices/lab_wire.sym} 130 -290 2 0 {name=l66 lab=ea_ibias}
N 90 -360 50 -360 {}
C {devices/lab_wire.sym} 50 -360 0 0 {name=l67 lab=ea_ibias}
N 130 -390 130 -430 {}
C {devices/lab_wire.sym} 130 -430 0 1 {name=l68 lab=vdd}
N 130 -360 170 -360 {}
C {devices/lab_wire.sym} 170 -360 0 1 {name=l69 lab=vdd}
N 350 -330 350 -290 {}
C {devices/lab_wire.sym} 350 -290 2 0 {name=l70 lab=vout}
N 310 -360 270 -360 {}
C {devices/lab_wire.sym} 270 -360 0 0 {name=l71 lab=ea_out}
N 350 -390 350 -430 {}
C {devices/lab_wire.sym} 350 -430 0 1 {name=l72 lab=vdd}
N 350 -360 390 -360 {}
C {devices/lab_wire.sym} 390 -360 0 1 {name=l73 lab=vdd}
N 570 -330 570 -290 {}
C {devices/lab_wire.sym} 570 -290 2 0 {name=l74 lab=v_ref_out}
N 530 -360 490 -360 {}
C {devices/lab_wire.sym} 490 -360 0 0 {name=l75 lab=ra_nb}
N 570 -390 570 -430 {}
C {devices/lab_wire.sym} 570 -430 0 1 {name=l76 lab=vdd}
N 570 -360 610 -360 {}
C {devices/lab_wire.sym} 610 -360 0 1 {name=l77 lab=vdd}
N 790 -330 790 -290 {}
C {devices/lab_wire.sym} 790 -290 2 0 {name=l78 lab=ra_ibias}
N 750 -360 710 -360 {}
C {devices/lab_wire.sym} 710 -360 0 0 {name=l79 lab=ra_ibias}
N 790 -390 790 -430 {}
C {devices/lab_wire.sym} 790 -430 0 1 {name=l80 lab=vdd}
N 790 -360 830 -360 {}
C {devices/lab_wire.sym} 830 -360 0 1 {name=l81 lab=vdd}
