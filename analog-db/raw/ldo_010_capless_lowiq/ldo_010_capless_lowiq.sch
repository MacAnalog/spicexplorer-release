v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_010_capless_lowiq} -1645 -200 0 0 0.4 0.4 {}
C {devices/vsource_np.sym} -1605 605 0 0 {name=VLP value="dc 0" savecurrent=false}
C {devices/vsource_np.sym} -1605 345 0 0 {name=VREF value="dc \{vref_val\}" savecurrent=false}
C {sg13g2_pr/cap_cmim.sym} -70 390 0 0 {name=CC model=cap_cmim spiceprefix=X w=c_comp_w l=c_comp_w}
C {sg13g2_pr/cap_cmim.sym} 2100 260 0 0 {name=CFF model=cap_cmim spiceprefix=X w=c_ff_w l=c_ff_w}
C {sg13g2_pr/cap_cmim.sym} 1870 520 0 0 {name=COUT model=cap_cmim spiceprefix=X w=c_out_w l=c_out_w m=c_out_m}
C {devices/sg13_lv_pmos_np.sym} 715 260 0 0 {name=M1A model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {devices/sg13_lv_pmos_np.sym} 215 260 0 0 {name=M1B model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {devices/sg13_lv_pmos_np.sym} 1345 260 0 0 {name=M2A model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {devices/sg13_lv_pmos_np.sym} -450 260 0 0 {name=M2B model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} 465 520 0 0 {name=M3A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {devices/sg13_lv_nmos_np.sym} 715 520 0 0 {name=M3B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {devices/sg13_lv_nmos_np.sym} 215 520 0 0 {name=M4A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {devices/sg13_lv_nmos_np.sym} -35 520 0 0 {name=M4B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {devices/sg13_lv_nmos_np.sym} -70 260 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} -70 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xmbp_l}
C {devices/sg13_lv_nmos_np.sym} 965 520 0 0 {name=MA model=sg13_lv_nmos spiceprefix=X w=x_dut_xma_w l=x_dut_xma_l}
C {devices/sg13_lv_nmos_np.sym} 465 260 0 0 {name=MB model=sg13_lv_nmos spiceprefix=X w=x_dut_xma_w l=x_dut_xma_l}
C {devices/sg13_lv_nmos_np.sym} -290 520 0 0 {name=MB0A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb0_w/2\}" l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} 1345 520 0 0 {name=MB0B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb0_w/2\}" l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} 1595 260 0 0 {name=MB1A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb1_w/2\}" l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} -710 260 0 0 {name=MB1B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb1_w/2\}" l=x_dut_xmb0_l}
C {devices/sg13_lv_pmos_np.sym} 715 0 0 0 {name=MBP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmbp_w l=x_dut_xmbp_l}
C {devices/sg13_lv_pmos_np.sym} 965 260 0 0 {name=MC model=sg13_lv_pmos spiceprefix=X w=x_dut_xmc_w l=x_dut_xmc_l}
C {devices/sg13_lv_pmos_np.sym} 465 0 0 0 {name=MCP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcp_w l=x_dut_xmcp_l}
C {devices/sg13_lv_pmos_np.sym} 215 0 0 0 {name=MD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcp_w l=x_dut_xmcp_l}
C {devices/sg13_lv_pmos_np.sym} 965 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xmp_w/x_dut_xmp_nf_mult\}" l=x_dut_xmp_l m="\{x_dut_xmp_m*x_dut_xmp_nf_mult\}"}
C {devices/sg13_lv_nmos_np.sym} 1850 260 0 0 {name=MSA model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xms_w/2\}" l=x_dut_xms_l}
C {devices/sg13_lv_nmos_np.sym} -960 260 0 0 {name=MSB model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xms_w/2\}" l=x_dut_xms_l}
C {devices/sg13_lv_pmos_np.sym} 1345 0 0 0 {name=MT model=sg13_lv_pmos spiceprefix=X w=x_dut_xmt_w l=x_dut_xmbp_l}
C {sg13g2_pr/rhigh.sym} 480 435 0 0 {name=R1_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 730 435 0 0 {name=R1_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 230 435 0 0 {name=R1_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 890 435 0 0 {name=R1_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -20 435 0 0 {name=R1_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1120 435 0 0 {name=R1_6 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -275 435 0 0 {name=R1_7 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1360 435 0 0 {name=R1_8 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -435 435 0 0 {name=R2_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1610 435 0 0 {name=R2_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -695 435 0 0 {name=R2_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1865 435 0 0 {name=R2_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -945 435 0 0 {name=R2_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 2100 435 0 0 {name=R2_6 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -1105 435 0 0 {name=R2_7 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 480 605 0 0 {name=R2_8 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 480 345 0 0 {name=RB_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 2260 435 0 0 {name=RB_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} -1265 435 0 0 {name=RB_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 2420 435 0 0 {name=RB_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 1610 520 0 0 {name=RB_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
N -1605 255 -1605 315 {}
N -1605 375 -1605 435 {}
N -1605 515 -1605 575 {}
N -1605 635 -1605 695 {}
N -1265 345 -1265 405 {}
N -1265 465 -1265 525 {}
N -1225 375 -1225 665 {}
N -1105 345 -1105 405 {}
N -1105 465 -1105 525 {}
N -1010 260 -1010 320 {}
N -945 345 -945 405 {}
N -945 465 -945 525 {}
N -940 200 -940 230 {}
N -940 290 -940 745 {}
N -880 260 -880 354 {}
N -760 260 -760 320 {}
N -695 345 -695 405 {}
N -695 465 -695 525 {}
N -690 170 -690 230 {}
N -690 290 -690 745 {}
N -630 260 -630 354 {}
N -435 345 -435 405 {}
N -435 465 -435 525 {}
N -430 170 -430 230 {}
N -430 290 -430 350 {}
N -370 260 -370 354 {}
N -310 450 -310 720 {}
N -275 345 -275 405 {}
N -275 465 -275 525 {}
N -270 430 -270 490 {}
N -270 550 -270 745 {}
N -210 520 -210 614 {}
N -150 0 -150 94 {}
N -150 260 -150 354 {}
N -90 -140 -90 -30 {}
N -90 30 -90 90 {}
N -90 170 -90 230 {}
N -90 290 -90 745 {}
N -70 330 -70 360 {}
N -70 420 -70 480 {}
N -20 345 -20 405 {}
N -20 465 -20 525 {}
N -15 430 -15 490 {}
N -15 550 -15 745 {}
N 45 520 45 614 {}
N 165 -60 165 0 {}
N 230 345 230 405 {}
N 230 465 230 525 {}
N 235 -140 235 -30 {}
N 235 30 235 90 {}
N 235 170 235 230 {}
N 235 290 235 350 {}
N 235 430 235 490 {}
N 235 550 235 745 {}
N 295 60 295 200 {}
N 295 260 295 354 {}
N 295 520 295 614 {}
N 445 -60 445 70 {}
N 445 450 445 520 {}
N 480 255 480 315 {}
N 480 465 480 495 {}
N 480 635 480 665 {}
N 485 -140 485 -30 {}
N 485 30 485 70 {}
N 485 170 485 230 {}
N 485 290 485 350 {}
N 485 430 485 490 {}
N 485 550 485 745 {}
N 545 0 545 94 {}
N 545 260 545 354 {}
N 545 520 545 614 {}
N 695 0 695 70 {}
N 695 450 695 520 {}
N 730 345 730 405 {}
N 730 465 730 525 {}
N 735 -140 735 -30 {}
N 735 30 735 70 {}
N 735 170 735 230 {}
N 735 290 735 350 {}
N 735 430 735 490 {}
N 735 550 735 745 {}
N 795 0 795 94 {}
N 795 260 795 354 {}
N 795 520 795 614 {}
N 890 345 890 405 {}
N 890 465 890 525 {}
N 915 260 915 330 {}
N 945 450 945 520 {}
N 985 -140 985 -30 {}
N 985 30 985 90 {}
N 985 170 985 230 {}
N 985 290 985 350 {}
N 985 430 985 490 {}
N 985 550 985 745 {}
N 1045 0 1045 94 {}
N 1045 260 1045 354 {}
N 1045 520 1045 614 {}
N 1120 345 1120 405 {}
N 1120 465 1120 525 {}
N 1325 200 1325 260 {}
N 1325 450 1325 720 {}
N 1360 375 1360 405 {}
N 1360 465 1360 525 {}
N 1365 -140 1365 -30 {}
N 1365 30 1365 90 {}
N 1365 290 1365 350 {}
N 1365 450 1365 490 {}
N 1365 550 1365 745 {}
N 1425 60 1425 230 {}
N 1425 260 1425 354 {}
N 1425 520 1425 614 {}
N 1610 345 1610 405 {}
N 1610 550 1610 580 {}
N 1615 170 1615 230 {}
N 1615 290 1615 745 {}
N 1675 260 1675 354 {}
N 1865 345 1865 405 {}
N 1865 465 1865 525 {}
N 1870 170 1870 230 {}
N 1870 290 1870 350 {}
N 1870 460 1870 490 {}
N 1870 550 1870 745 {}
N 1930 260 1930 354 {}
N 2100 170 2100 230 {}
N 2100 290 2100 320 {}
N 2100 465 2100 525 {}
N 2160 320 2160 375 {}
N 2260 345 2260 405 {}
N 2260 465 2260 525 {}
N 2420 345 2420 405 {}
N 2420 465 2420 525 {}
N 2540 375 2540 580 {}
N -1665 -140 2745 -140 {}
N 165 -60 445 -60 {}
N -150 0 -90 0 {}
N -50 0 10 0 {}
N 135 0 195 0 {}
N 485 0 545 0 {}
N 635 0 695 0 {}
N 735 0 795 0 {}
N 885 0 945 0 {}
N 985 0 1045 0 {}
N 1265 0 1325 0 {}
N 235 60 295 60 {}
N 1365 60 1425 60 {}
N 445 70 485 70 {}
N 695 70 735 70 {}
N -940 200 295 200 {}
N 1365 230 1425 230 {}
N -1040 260 -980 260 {}
N -940 260 -880 260 {}
N -760 260 -730 260 {}
N -690 260 -630 260 {}
N -530 260 -470 260 {}
N -430 260 -370 260 {}
N -150 260 -90 260 {}
N -50 260 10 260 {}
N 135 260 195 260 {}
N 235 260 295 260 {}
N 385 260 445 260 {}
N 485 260 545 260 {}
N 635 260 695 260 {}
N 735 260 795 260 {}
N 885 260 945 260 {}
N 985 260 1045 260 {}
N 1295 260 1325 260 {}
N 1365 260 1425 260 {}
N 1515 260 1575 260 {}
N 1615 260 1675 260 {}
N 1770 260 1830 260 {}
N 1870 260 1930 260 {}
N -1010 320 -760 320 {}
N 2100 320 2160 320 {}
N -70 330 915 330 {}
N -1225 375 -1105 375 {}
N 420 375 480 375 {}
N 1360 375 2160 375 {}
N 2420 375 2540 375 {}
N -310 450 -270 450 {}
N 445 450 485 450 {}
N 695 450 735 450 {}
N 945 450 985 450 {}
N 1325 450 1365 450 {}
N -270 520 -210 520 {}
N -115 520 -55 520 {}
N -15 520 45 520 {}
N 135 520 195 520 {}
N 235 520 295 520 {}
N 485 520 545 520 {}
N 735 520 795 520 {}
N 985 520 1045 520 {}
N 1365 520 1425 520 {}
N 1610 580 2540 580 {}
N -1225 665 480 665 {}
N -310 720 1325 720 {}
N -1665 745 2745 745 {}
C {devices/lab_wire.sym} -115 520 0 0 {name=l0 lab=ea_n}
C {devices/lab_wire.sym} 135 520 0 0 {name=l1 lab=ea_n}
C {devices/lab_wire.sym} 235 350 2 0 {name=l2 lab=ea_n}
C {devices/lab_wire.sym} 485 430 0 1 {name=l3 lab=ea_n}
C {devices/lab_wire.sym} 735 430 0 1 {name=l4 lab=ea_n}
C {devices/lab_wire.sym} 735 350 2 0 {name=l5 lab=ea_n}
C {devices/lab_wire.sym} -430 350 2 0 {name=l6 lab=ea_o1}
C {devices/lab_wire.sym} -70 480 2 0 {name=l7 lab=ea_o1}
C {devices/lab_wire.sym} 10 260 0 1 {name=l8 lab=ea_o1}
C {devices/lab_wire.sym} -15 430 0 1 {name=l9 lab=ea_o1}
C {devices/lab_wire.sym} 235 430 0 1 {name=l10 lab=ea_o1}
C {devices/lab_wire.sym} 1365 350 2 0 {name=l11 lab=ea_o1}
C {devices/lab_wire.sym} -90 90 2 0 {name=l12 lab=ea_out}
C {devices/lab_wire.sym} -90 170 0 1 {name=l13 lab=ea_out}
C {devices/lab_wire.sym} 885 260 0 0 {name=l14 lab=ea_out}
C {devices/lab_wire.sym} -430 170 0 1 {name=l15 lab=ea_tail}
C {devices/lab_wire.sym} 235 170 0 1 {name=l16 lab=ea_tail}
C {devices/lab_wire.sym} 735 170 0 1 {name=l17 lab=ea_tail}
C {devices/lab_wire.sym} 1365 90 2 0 {name=l18 lab=ea_tail}
C {devices/lab_wire.sym} -435 525 2 0 {name=l19 lab=fb}
C {devices/lab_wire.sym} 135 260 0 0 {name=l20 lab=fb}
C {devices/lab_wire.sym} 635 260 0 0 {name=l21 lab=fb}
C {devices/lab_wire.sym} 2100 290 0 0 {name=l22 lab=fb}
C {devices/lab_wire.sym} 235 90 2 0 {name=l23 lab=gate}
C {devices/lab_wire.sym} 885 0 0 0 {name=l24 lab=gate}
C {devices/lab_wire.sym} 1870 170 0 1 {name=l25 lab=gate}
C {devices/lab_wire.sym} 480 465 0 0 {name=l26 lab=lp_brk}
C {devices/lab_wire.sym} 2100 170 0 1 {name=l27 lab=lp_brk}
C {devices/lab_wire.sym} 480 405 0 0 {name=l28 lab=n_r1_1}
C {devices/lab_wire.sym} 730 525 2 0 {name=l29 lab=n_r1_1}
C {devices/lab_wire.sym} 230 525 2 0 {name=l30 lab=n_r1_2}
C {devices/lab_wire.sym} 730 345 0 1 {name=l31 lab=n_r1_2}
C {devices/lab_wire.sym} 230 345 0 1 {name=l32 lab=n_r1_3}
C {devices/lab_wire.sym} 890 525 2 0 {name=l33 lab=n_r1_3}
C {devices/lab_wire.sym} -20 525 2 0 {name=l34 lab=n_r1_4}
C {devices/lab_wire.sym} 890 345 0 1 {name=l35 lab=n_r1_4}
C {devices/lab_wire.sym} -20 345 0 1 {name=l36 lab=n_r1_5}
C {devices/lab_wire.sym} 1120 525 2 0 {name=l37 lab=n_r1_5}
C {devices/lab_wire.sym} -275 525 2 0 {name=l38 lab=n_r1_6}
C {devices/lab_wire.sym} 1120 345 0 1 {name=l39 lab=n_r1_6}
C {devices/lab_wire.sym} -275 345 0 1 {name=l40 lab=n_r1_7}
C {devices/lab_wire.sym} 1360 525 2 0 {name=l41 lab=n_r1_7}
C {devices/lab_wire.sym} -435 345 0 1 {name=l42 lab=n_r2_1}
C {devices/lab_wire.sym} 1610 465 0 0 {name=l43 lab=n_r2_1}
C {devices/lab_wire.sym} -695 525 2 0 {name=l44 lab=n_r2_2}
C {devices/lab_wire.sym} 1610 345 0 1 {name=l45 lab=n_r2_2}
C {devices/lab_wire.sym} -695 345 0 1 {name=l46 lab=n_r2_3}
C {devices/lab_wire.sym} 1865 525 2 0 {name=l47 lab=n_r2_3}
C {devices/lab_wire.sym} -945 525 2 0 {name=l48 lab=n_r2_4}
C {devices/lab_wire.sym} 1865 345 0 1 {name=l49 lab=n_r2_4}
C {devices/lab_wire.sym} -945 345 0 1 {name=l50 lab=n_r2_5}
C {devices/lab_wire.sym} 2100 525 2 0 {name=l51 lab=n_r2_5}
C {devices/lab_wire.sym} -1105 525 2 0 {name=l52 lab=n_r2_6}
C {devices/lab_wire.sym} 2100 405 0 0 {name=l53 lab=n_r2_6}
C {devices/lab_wire.sym} -1105 345 0 1 {name=l54 lab=n_r2_7}
C {devices/lab_wire.sym} 480 255 0 1 {name=l55 lab=n_rb_1}
C {devices/lab_wire.sym} 2260 525 2 0 {name=l56 lab=n_rb_1}
C {devices/lab_wire.sym} -1265 525 2 0 {name=l57 lab=n_rb_2}
C {devices/lab_wire.sym} 2260 345 0 1 {name=l58 lab=n_rb_2}
C {devices/lab_wire.sym} -1265 345 0 1 {name=l59 lab=n_rb_3}
C {devices/lab_wire.sym} 2420 525 2 0 {name=l60 lab=n_rb_3}
C {devices/lab_wire.sym} 2420 345 0 1 {name=l61 lab=n_rb_4}
C {devices/lab_wire.sym} -1040 260 0 0 {name=l62 lab=nbias}
C {devices/lab_wire.sym} -270 430 0 1 {name=l63 lab=nbias}
C {devices/lab_wire.sym} 1515 260 0 0 {name=l64 lab=nbias}
C {devices/lab_wire.sym} 1610 490 0 0 {name=l65 lab=nbias}
C {devices/lab_wire.sym} 1770 260 0 0 {name=l66 lab=nbias}
C {devices/lab_wire.sym} -690 170 0 1 {name=l67 lab=pbias}
C {devices/lab_wire.sym} 10 0 0 1 {name=l68 lab=pbias}
C {devices/lab_wire.sym} 635 0 0 0 {name=l69 lab=pbias}
C {devices/lab_wire.sym} 1265 0 0 0 {name=l70 lab=pbias}
C {devices/lab_wire.sym} 1615 170 0 1 {name=l71 lab=pbias}
C {devices/lab_wire.sym} 985 90 2 0 {name=l72 lab=vout}
C {devices/lab_wire.sym} 985 170 0 1 {name=l73 lab=vout}
C {devices/lab_wire.sym} -530 260 0 0 {name=l74 lab=vref}
C {devices/lab_wire.sym} 1325 200 0 1 {name=l75 lab=vref}
C {devices/lab_wire.sym} 385 260 0 0 {name=l76 lab=x1}
C {devices/lab_wire.sym} 985 430 0 1 {name=l77 lab=x1}
C {devices/lab_wire.sym} 985 350 2 0 {name=l78 lab=x1}
C {devices/lab_wire.sym} 135 0 0 0 {name=l79 lab=y}
C {devices/lab_wire.sym} 485 170 0 1 {name=l80 lab=y}
C {devices/lab_wire.sym} 795 354 2 0 {name=l81 lab=vdd}
C {devices/lab_wire.sym} 295 354 2 0 {name=l82 lab=vdd}
C {devices/lab_wire.sym} 1425 354 2 0 {name=l83 lab=vdd}
C {devices/lab_wire.sym} -370 354 2 0 {name=l84 lab=vdd}
C {devices/lab_wire.sym} -150 94 2 0 {name=l85 lab=vdd}
C {devices/lab_wire.sym} 795 94 2 0 {name=l86 lab=vdd}
C {devices/lab_wire.sym} 1045 354 2 0 {name=l87 lab=vdd}
C {devices/lab_wire.sym} 545 94 2 0 {name=l88 lab=vdd}
C {devices/lab_wire.sym} 235 0 0 0 {name=l89 lab=vdd}
C {devices/lab_wire.sym} 1045 94 2 0 {name=l90 lab=vdd}
C {devices/lab_wire.sym} 1365 0 0 0 {name=l91 lab=vdd}
C {devices/lab_wire.sym} 545 614 2 0 {name=l92 lab=vss}
C {devices/lab_wire.sym} 795 614 2 0 {name=l93 lab=vss}
C {devices/lab_wire.sym} 295 614 2 0 {name=l94 lab=vss}
C {devices/lab_wire.sym} 45 614 2 0 {name=l95 lab=vss}
C {devices/lab_wire.sym} -150 354 2 0 {name=l96 lab=vss}
C {devices/lab_wire.sym} 1045 614 2 0 {name=l97 lab=vss}
C {devices/lab_wire.sym} 545 354 2 0 {name=l98 lab=vss}
C {devices/lab_wire.sym} -210 614 2 0 {name=l99 lab=vss}
C {devices/lab_wire.sym} 1425 614 2 0 {name=l100 lab=vss}
C {devices/lab_wire.sym} 1675 354 2 0 {name=l101 lab=vss}
C {devices/lab_wire.sym} -630 354 2 0 {name=l102 lab=vss}
C {devices/lab_wire.sym} 1930 354 2 0 {name=l103 lab=vss}
C {devices/lab_wire.sym} -880 354 2 0 {name=l104 lab=vss}
C {devices/lab_wire.sym} -1605 515 0 1 {name=l105 lab=lp_brk}
C {devices/lab_wire.sym} -1605 695 2 0 {name=l106 lab=vout}
C {devices/lab_wire.sym} -1605 255 0 1 {name=l107 lab=vref}
C {devices/lab_wire.sym} -1605 435 2 0 {name=l108 lab=vss}
C {devices/lab_wire.sym} 420 375 0 0 {name=l109 lab=vdd}
C {devices/lab_wire.sym} 485 350 2 0 {name=l110 lab=vss}
C {devices/lab_wire.sym} 1870 350 2 0 {name=l111 lab=vss}
C {devices/lab_wire.sym} 480 575 0 0 {name=l112 lab=vss}
C {devices/iopin.sym} -1665 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -1665 745 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 1870 460 0 0 {name=p2 lab=vout}
