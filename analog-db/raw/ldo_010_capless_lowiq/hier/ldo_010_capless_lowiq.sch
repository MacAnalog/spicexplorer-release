v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_010_capless_lowiq} -2900 -540 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -2200 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_nmos_simple_2.sym} -1760 0 0 0 {name=xcm_nmos_simple_2}
C {blocks/cm_nmos_simple_3.sym} -1320 0 0 0 {name=xcm_nmos_simple_3}
C {blocks/cm_nmos_simple_4.sym} -880 0 0 0 {name=xcm_nmos_simple_4}
C {blocks/cm_nmos_simple_5.sym} -440 0 0 0 {name=xcm_nmos_simple_5}
C {blocks/cm_pmos_simple_1.sym} 0 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_pmos_simple_2.sym} 440 0 0 0 {name=xcm_pmos_simple_2}
C {blocks/dp_pmos_simple_1.sym} 880 0 0 0 {name=xdp_pmos_simple_1}
C {blocks/dp_pmos_simple_2.sym} 1320 0 0 0 {name=xdp_pmos_simple_2}
C {blocks/dp_pmos_simple_3.sym} 1760 0 0 0 {name=xdp_pmos_simple_3}
C {blocks/dp_pmos_simple_4.sym} 2200 0 0 0 {name=xdp_pmos_simple_4}
C {devices/vsource_np.sym} -2860 340 0 0 {name=VLP value="dc 0" savecurrent=false}
C {devices/vsource_np.sym} -2860 120 0 0 {name=VREF value="dc \{vref_val\}" savecurrent=false}
C {sg13g2_pr/cap_cmim.sym} -2640 340 0 0 {name=CC model=cap_cmim spiceprefix=X w=c_comp_w l=c_comp_w}
C {sg13g2_pr/cap_cmim.sym} -2420 340 0 0 {name=CFF model=cap_cmim spiceprefix=X w=c_ff_w l=c_ff_w}
C {sg13g2_pr/cap_cmim.sym} -2200 340 0 0 {name=COUT model=cap_cmim spiceprefix=X w=c_out_w l=c_out_w m=c_out_m}
C {devices/sg13_lv_nmos_np.sym} -1980 340 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} -110 -340 0 0 {name=MC model=sg13_lv_pmos spiceprefix=X w=x_dut_xmc_w l=x_dut_xmc_l}
C {devices/sg13_lv_pmos_np.sym} 110 -340 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xmp_w/x_dut_xmp_nf_mult\}" l=x_dut_xmp_l m="\{x_dut_xmp_m*x_dut_xmp_nf_mult\}"}
C {sg13g2_pr/rhigh.sym} -1760 340 0 0 {name=R1_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -1540 340 0 0 {name=R1_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -1320 340 0 0 {name=R1_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -1100 340 0 0 {name=R1_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -880 340 0 0 {name=R1_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -660 340 0 0 {name=R1_6 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -440 340 0 0 {name=R1_7 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -220 340 0 0 {name=R1_8 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 0 340 0 0 {name=R2_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 220 340 0 0 {name=R2_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 440 340 0 0 {name=R2_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 660 340 0 0 {name=R2_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 880 340 0 0 {name=R2_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1100 340 0 0 {name=R2_6 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1320 340 0 0 {name=R2_7 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1540 340 0 0 {name=R2_8 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1760 340 0 0 {name=RB_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 1980 340 0 0 {name=RB_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 2200 340 0 0 {name=RB_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 2420 340 0 0 {name=RB_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 2640 340 0 0 {name=RB_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
N -2090 -20 -2050 -20 {}
C {devices/lab_wire.sym} -2050 -20 0 1 {name=l0 lab=ea_n}
N -2090 20 -2050 20 {}
C {devices/lab_wire.sym} -2050 20 0 1 {name=l1 lab=ea_o1}
N -2200 80 -2200 120 {}
C {devices/lab_wire.sym} -2200 120 2 0 {name=l2 lab=vss}
N -1650 -20 -1610 -20 {}
C {devices/lab_wire.sym} -1610 -20 0 1 {name=l3 lab=ea_n}
N -1650 20 -1610 20 {}
C {devices/lab_wire.sym} -1610 20 0 1 {name=l4 lab=ea_o1}
N -1760 80 -1760 120 {}
C {devices/lab_wire.sym} -1760 120 2 0 {name=l5 lab=vss}
N -1210 -20 -1170 -20 {}
C {devices/lab_wire.sym} -1170 -20 0 1 {name=l6 lab=x1}
N -1210 20 -1170 20 {}
C {devices/lab_wire.sym} -1170 20 0 1 {name=l7 lab=y}
N -1320 80 -1320 120 {}
C {devices/lab_wire.sym} -1320 120 2 0 {name=l8 lab=vss}
N -770 -40 -730 -40 {}
C {devices/lab_wire.sym} -730 -40 0 1 {name=l9 lab=gate}
N -770 0 -730 0 {}
C {devices/lab_wire.sym} -730 0 0 1 {name=l10 lab=nbias}
N -770 40 -730 40 {}
C {devices/lab_wire.sym} -730 40 0 1 {name=l11 lab=pbias}
N -880 100 -880 140 {}
C {devices/lab_wire.sym} -880 140 2 0 {name=l12 lab=vss}
N -330 -40 -290 -40 {}
C {devices/lab_wire.sym} -290 -40 0 1 {name=l13 lab=gate}
N -330 0 -290 0 {}
C {devices/lab_wire.sym} -290 0 0 1 {name=l14 lab=nbias}
N -330 40 -290 40 {}
C {devices/lab_wire.sym} -290 40 0 1 {name=l15 lab=pbias}
N -440 100 -440 140 {}
C {devices/lab_wire.sym} -440 140 2 0 {name=l16 lab=vss}
N 110 -40 150 -40 {}
C {devices/lab_wire.sym} 150 -40 0 1 {name=l17 lab=ea_out}
N 110 0 150 0 {}
C {devices/lab_wire.sym} 150 0 0 1 {name=l18 lab=ea_tail}
N 110 40 150 40 {}
C {devices/lab_wire.sym} 150 40 0 1 {name=l19 lab=pbias}
N 0 -100 0 -140 {}
C {devices/lab_wire.sym} 0 -140 0 1 {name=l20 lab=vdd}
N 550 -20 590 -20 {}
C {devices/lab_wire.sym} 590 -20 0 1 {name=l21 lab=gate}
N 550 20 590 20 {}
C {devices/lab_wire.sym} 590 20 0 1 {name=l22 lab=y}
N 440 -80 440 -120 {}
C {devices/lab_wire.sym} 440 -120 0 1 {name=l23 lab=vdd}
N 770 -20 730 -20 {}
C {devices/lab_wire.sym} 730 -20 0 0 {name=l24 lab=fb}
N 770 20 730 20 {}
C {devices/lab_wire.sym} 730 20 0 0 {name=l25 lab=vref}
N 990 -40 1030 -40 {}
C {devices/lab_wire.sym} 1030 -40 0 1 {name=l26 lab=ea_n}
N 990 0 1030 0 {}
C {devices/lab_wire.sym} 1030 0 0 1 {name=l27 lab=ea_o1}
N 990 40 1030 40 {}
C {devices/lab_wire.sym} 1030 40 0 1 {name=l28 lab=ea_tail}
N 880 -100 880 -140 {}
C {devices/lab_wire.sym} 880 -140 0 1 {name=l29 lab=vdd}
N 1210 -20 1170 -20 {}
C {devices/lab_wire.sym} 1170 -20 0 0 {name=l30 lab=fb}
N 1210 20 1170 20 {}
C {devices/lab_wire.sym} 1170 20 0 0 {name=l31 lab=vref}
N 1430 -40 1470 -40 {}
C {devices/lab_wire.sym} 1470 -40 0 1 {name=l32 lab=ea_n}
N 1430 0 1470 0 {}
C {devices/lab_wire.sym} 1470 0 0 1 {name=l33 lab=ea_o1}
N 1430 40 1470 40 {}
C {devices/lab_wire.sym} 1470 40 0 1 {name=l34 lab=ea_tail}
N 1320 -100 1320 -140 {}
C {devices/lab_wire.sym} 1320 -140 0 1 {name=l35 lab=vdd}
N 1650 -20 1610 -20 {}
C {devices/lab_wire.sym} 1610 -20 0 0 {name=l36 lab=fb}
N 1650 20 1610 20 {}
C {devices/lab_wire.sym} 1610 20 0 0 {name=l37 lab=vref}
N 1870 -40 1910 -40 {}
C {devices/lab_wire.sym} 1910 -40 0 1 {name=l38 lab=ea_n}
N 1870 0 1910 0 {}
C {devices/lab_wire.sym} 1910 0 0 1 {name=l39 lab=ea_o1}
N 1870 40 1910 40 {}
C {devices/lab_wire.sym} 1910 40 0 1 {name=l40 lab=ea_tail}
N 1760 -100 1760 -140 {}
C {devices/lab_wire.sym} 1760 -140 0 1 {name=l41 lab=vdd}
N 2090 -20 2050 -20 {}
C {devices/lab_wire.sym} 2050 -20 0 0 {name=l42 lab=fb}
N 2090 20 2050 20 {}
C {devices/lab_wire.sym} 2050 20 0 0 {name=l43 lab=vref}
N 2310 -40 2350 -40 {}
C {devices/lab_wire.sym} 2350 -40 0 1 {name=l44 lab=ea_n}
N 2310 0 2350 0 {}
C {devices/lab_wire.sym} 2350 0 0 1 {name=l45 lab=ea_o1}
N 2310 40 2350 40 {}
C {devices/lab_wire.sym} 2350 40 0 1 {name=l46 lab=ea_tail}
N 2200 -100 2200 -140 {}
C {devices/lab_wire.sym} 2200 -140 0 1 {name=l47 lab=vdd}
N -2860 310 -2860 270 {}
C {devices/lab_wire.sym} -2860 270 0 1 {name=l48 lab=lp_brk}
N -2860 370 -2860 410 {}
C {devices/lab_wire.sym} -2860 410 2 0 {name=l49 lab=vout}
N -2860 90 -2860 50 {}
C {devices/lab_wire.sym} -2860 50 0 1 {name=l50 lab=vref}
N -2860 150 -2860 190 {}
C {devices/lab_wire.sym} -2860 190 2 0 {name=l51 lab=vss}
N -2640 310 -2640 270 {}
C {devices/lab_wire.sym} -2640 270 0 1 {name=l52 lab=ea_out}
N -2640 370 -2640 410 {}
C {devices/lab_wire.sym} -2640 410 2 0 {name=l53 lab=ea_o1}
N -2420 310 -2420 270 {}
C {devices/lab_wire.sym} -2420 270 0 1 {name=l54 lab=lp_brk}
N -2420 370 -2420 410 {}
C {devices/lab_wire.sym} -2420 410 2 0 {name=l55 lab=fb}
N -2200 310 -2200 270 {}
C {devices/lab_wire.sym} -2200 270 0 1 {name=l56 lab=vout}
N -2200 370 -2200 410 {}
C {devices/lab_wire.sym} -2200 410 2 0 {name=l57 lab=vss}
N -1960 310 -1960 270 {}
C {devices/lab_wire.sym} -1960 270 0 1 {name=l58 lab=ea_out}
N -2000 340 -2040 340 {}
C {devices/lab_wire.sym} -2040 340 0 0 {name=l59 lab=ea_o1}
N -1960 370 -1960 410 {}
C {devices/lab_wire.sym} -1960 410 2 0 {name=l60 lab=vss}
N -1960 340 -1920 340 {}
C {devices/lab_wire.sym} -1920 340 0 1 {name=l61 lab=vss}
N -90 -310 -90 -270 {}
C {devices/lab_wire.sym} -90 -270 2 0 {name=l62 lab=x1}
N -130 -340 -170 -340 {}
C {devices/lab_wire.sym} -170 -340 0 0 {name=l63 lab=ea_out}
N -90 -370 -90 -410 {}
C {devices/lab_wire.sym} -90 -410 0 1 {name=l64 lab=vout}
N -90 -340 -50 -340 {}
C {devices/lab_wire.sym} -50 -340 0 1 {name=l65 lab=vdd}
N 130 -310 130 -270 {}
C {devices/lab_wire.sym} 130 -270 2 0 {name=l66 lab=vout}
N 90 -340 50 -340 {}
C {devices/lab_wire.sym} 50 -340 0 0 {name=l67 lab=gate}
N 130 -370 130 -410 {}
C {devices/lab_wire.sym} 130 -410 0 1 {name=l68 lab=vdd}
N 130 -340 170 -340 {}
C {devices/lab_wire.sym} 170 -340 0 1 {name=l69 lab=vdd}
N -1760 370 -1760 410 {}
C {devices/lab_wire.sym} -1760 410 2 0 {name=l70 lab=lp_brk}
N -1760 310 -1760 270 {}
C {devices/lab_wire.sym} -1760 270 0 1 {name=l71 lab=n_r1_1}
N -1540 370 -1540 410 {}
C {devices/lab_wire.sym} -1540 410 2 0 {name=l72 lab=n_r1_1}
N -1540 310 -1540 270 {}
C {devices/lab_wire.sym} -1540 270 0 1 {name=l73 lab=n_r1_2}
N -1320 370 -1320 410 {}
C {devices/lab_wire.sym} -1320 410 2 0 {name=l74 lab=n_r1_2}
N -1320 310 -1320 270 {}
C {devices/lab_wire.sym} -1320 270 0 1 {name=l75 lab=n_r1_3}
N -1100 370 -1100 410 {}
C {devices/lab_wire.sym} -1100 410 2 0 {name=l76 lab=n_r1_3}
N -1100 310 -1100 270 {}
C {devices/lab_wire.sym} -1100 270 0 1 {name=l77 lab=n_r1_4}
N -880 370 -880 410 {}
C {devices/lab_wire.sym} -880 410 2 0 {name=l78 lab=n_r1_4}
N -880 310 -880 270 {}
C {devices/lab_wire.sym} -880 270 0 1 {name=l79 lab=n_r1_5}
N -660 370 -660 410 {}
C {devices/lab_wire.sym} -660 410 2 0 {name=l80 lab=n_r1_5}
N -660 310 -660 270 {}
C {devices/lab_wire.sym} -660 270 0 1 {name=l81 lab=n_r1_6}
N -440 370 -440 410 {}
C {devices/lab_wire.sym} -440 410 2 0 {name=l82 lab=n_r1_6}
N -440 310 -440 270 {}
C {devices/lab_wire.sym} -440 270 0 1 {name=l83 lab=n_r1_7}
N -220 370 -220 410 {}
C {devices/lab_wire.sym} -220 410 2 0 {name=l84 lab=n_r1_7}
N -220 310 -220 270 {}
C {devices/lab_wire.sym} -220 270 0 1 {name=l85 lab=fb}
N 0 370 0 410 {}
C {devices/lab_wire.sym} 0 410 2 0 {name=l86 lab=fb}
N 0 310 0 270 {}
C {devices/lab_wire.sym} 0 270 0 1 {name=l87 lab=n_r2_1}
N 220 370 220 410 {}
C {devices/lab_wire.sym} 220 410 2 0 {name=l88 lab=n_r2_1}
N 220 310 220 270 {}
C {devices/lab_wire.sym} 220 270 0 1 {name=l89 lab=n_r2_2}
N 440 370 440 410 {}
C {devices/lab_wire.sym} 440 410 2 0 {name=l90 lab=n_r2_2}
N 440 310 440 270 {}
C {devices/lab_wire.sym} 440 270 0 1 {name=l91 lab=n_r2_3}
N 660 370 660 410 {}
C {devices/lab_wire.sym} 660 410 2 0 {name=l92 lab=n_r2_3}
N 660 310 660 270 {}
C {devices/lab_wire.sym} 660 270 0 1 {name=l93 lab=n_r2_4}
N 880 370 880 410 {}
C {devices/lab_wire.sym} 880 410 2 0 {name=l94 lab=n_r2_4}
N 880 310 880 270 {}
C {devices/lab_wire.sym} 880 270 0 1 {name=l95 lab=n_r2_5}
N 1100 370 1100 410 {}
C {devices/lab_wire.sym} 1100 410 2 0 {name=l96 lab=n_r2_5}
N 1100 310 1100 270 {}
C {devices/lab_wire.sym} 1100 270 0 1 {name=l97 lab=n_r2_6}
N 1320 370 1320 410 {}
C {devices/lab_wire.sym} 1320 410 2 0 {name=l98 lab=n_r2_6}
N 1320 310 1320 270 {}
C {devices/lab_wire.sym} 1320 270 0 1 {name=l99 lab=n_r2_7}
N 1540 370 1540 410 {}
C {devices/lab_wire.sym} 1540 410 2 0 {name=l100 lab=n_r2_7}
N 1540 310 1540 270 {}
C {devices/lab_wire.sym} 1540 270 0 1 {name=l101 lab=vss}
N 1760 370 1760 410 {}
C {devices/lab_wire.sym} 1760 410 2 0 {name=l102 lab=vdd}
N 1760 310 1760 270 {}
C {devices/lab_wire.sym} 1760 270 0 1 {name=l103 lab=n_rb_1}
N 1980 370 1980 410 {}
C {devices/lab_wire.sym} 1980 410 2 0 {name=l104 lab=n_rb_1}
N 1980 310 1980 270 {}
C {devices/lab_wire.sym} 1980 270 0 1 {name=l105 lab=n_rb_2}
N 2200 370 2200 410 {}
C {devices/lab_wire.sym} 2200 410 2 0 {name=l106 lab=n_rb_2}
N 2200 310 2200 270 {}
C {devices/lab_wire.sym} 2200 270 0 1 {name=l107 lab=n_rb_3}
N 2420 370 2420 410 {}
C {devices/lab_wire.sym} 2420 410 2 0 {name=l108 lab=n_rb_3}
N 2420 310 2420 270 {}
C {devices/lab_wire.sym} 2420 270 0 1 {name=l109 lab=n_rb_4}
N 2640 370 2640 410 {}
C {devices/lab_wire.sym} 2640 410 2 0 {name=l110 lab=n_rb_4}
N 2640 310 2640 270 {}
C {devices/lab_wire.sym} 2640 270 0 1 {name=l111 lab=nbias}
