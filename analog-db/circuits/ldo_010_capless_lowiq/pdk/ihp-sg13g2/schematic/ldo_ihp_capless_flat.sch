v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_ihp_capless} -1645 -200 0 0 0.4 0.4 {}
C {devices/vsource.sym} -1605 345 0 0 {name=VREF value="dc \{vref_val\}"}
C {devices/vsource.sym} -1605 605 0 0 {name=VLP value="dc 0"}
C {sg13g2_pr/rhigh.sym} 290 435 0 0 {name=R1_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 505 435 0 0 {name=R1_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 80 435 0 0 {name=R1_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 665 435 0 0 {name=R1_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -135 435 0 0 {name=R1_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 855 435 0 0 {name=R1_6 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -355 435 0 0 {name=R1_7 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1055 435 0 0 {name=R1_8 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/cap_cmim.sym} 1685 260 0 0 {name=CFF model=cap_cmim spiceprefix=X w=c_ff_w l=c_ff_w}
C {sg13g2_pr/rhigh.sym} -515 435 0 0 {name=R2_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1265 435 0 0 {name=R2_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -735 435 0 0 {name=R2_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1485 435 0 0 {name=R2_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -945 435 0 0 {name=R2_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1685 435 0 0 {name=R2_6 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -1105 435 0 0 {name=R2_7 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 290 605 0 0 {name=R2_8 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 290 345 0 0 {name=RB_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 1845 435 0 0 {name=RB_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} -1265 435 0 0 {name=RB_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 2005 435 0 0 {name=RB_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 1265 520 0 0 {name=RB_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/sg13_lv_nmos.sym} -370 520 0 0 {name=MB0A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb0_w/2\}" l=x_dut_xmb0_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 1040 520 0 0 {name=MB0B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb0_w/2\}" l=x_dut_xmb0_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 1250 260 0 0 {name=MB1A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb1_w/2\}" l=x_dut_xmb0_l}
C {sg13g2_pr/sg13_lv_nmos.sym} -750 260 0 0 {name=MB1B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb1_w/2\}" l=x_dut_xmb0_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 490 0 0 0 {name=MBP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmbp_w l=x_dut_xmbp_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 1040 0 0 0 {name=MT model=sg13_lv_pmos spiceprefix=X w=x_dut_xmt_w l=x_dut_xmbp_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 490 260 0 0 {name=M1A model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 65 260 0 0 {name=M1B model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 1040 260 0 0 {name=M2A model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {sg13g2_pr/sg13_lv_pmos.sym} -530 260 0 0 {name=M2B model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 275 520 0 0 {name=M3A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 490 520 0 0 {name=M3B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 65 520 0 0 {name=M4A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {sg13g2_pr/sg13_lv_nmos.sym} -150 520 0 0 {name=M4B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {sg13g2_pr/sg13_lv_nmos.sym} -220 260 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {sg13g2_pr/sg13_lv_pmos.sym} -220 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xmbp_l}
C {sg13g2_pr/cap_cmim.sym} -220 390 0 0 {name=CC model=cap_cmim spiceprefix=X w=c_comp_w l=c_comp_w}
C {sg13g2_pr/sg13_lv_pmos.sym} 700 260 0 0 {name=MC model=sg13_lv_pmos spiceprefix=X w=x_dut_xmc_w l=x_dut_xmc_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 700 520 0 0 {name=MA model=sg13_lv_nmos spiceprefix=X w=x_dut_xma_w l=x_dut_xma_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 275 260 0 0 {name=MB model=sg13_lv_nmos spiceprefix=X w=x_dut_xma_w l=x_dut_xma_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 275 0 0 0 {name=MCP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcp_w l=x_dut_xmcp_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 65 0 0 0 {name=MD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcp_w l=x_dut_xmcp_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 1470 260 0 0 {name=MSA model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xms_w/2\}" l=x_dut_xms_l}
C {sg13g2_pr/sg13_lv_nmos.sym} -960 260 0 0 {name=MSB model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xms_w/2\}" l=x_dut_xms_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 700 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xmp_w/x_dut_xmp_nf_mult\}" l=x_dut_xmp_l m="\{x_dut_xmp_m*x_dut_xmp_nf_mult\}"}
C {sg13g2_pr/cap_cmim.sym} 1490 520 0 0 {name=COUT model=cap_cmim spiceprefix=X w=c_out_w l=c_out_w m=c_out_m}
N -1605 255 -1605 315 {}
N -1605 375 -1605 435 {}
N -1605 515 -1605 575 {}
N -1605 635 -1605 695 {}
N -1265 345 -1265 405 {}
N -1265 465 -1265 525 {}
N -1105 345 -1105 405 {}
N -1105 465 -1105 525 {}
N -945 345 -945 405 {}
N -945 465 -945 525 {}
N -940 170 -940 230 {}
N -940 290 -940 745 {}
N -880 260 -880 354 {}
N -770 200 -770 260 {}
N -735 345 -735 405 {}
N -735 465 -735 525 {}
N -730 170 -730 230 {}
N -730 290 -730 745 {}
N -670 260 -670 354 {}
N -550 200 -550 260 {}
N -515 345 -515 405 {}
N -515 465 -515 525 {}
N -510 170 -510 230 {}
N -510 290 -510 350 {}
N -450 260 -450 354 {}
N -390 450 -390 520 {}
N -355 345 -355 405 {}
N -355 465 -355 525 {}
N -350 430 -350 490 {}
N -350 550 -350 745 {}
N -300 0 -300 94 {}
N -300 260 -300 354 {}
N -290 520 -290 614 {}
N -240 -140 -240 -30 {}
N -240 30 -240 90 {}
N -240 170 -240 230 {}
N -240 290 -240 745 {}
N -220 330 -220 360 {}
N -220 420 -220 450 {}
N -170 260 -170 450 {}
N -170 520 -170 580 {}
N -135 345 -135 405 {}
N -135 465 -135 525 {}
N -130 430 -130 490 {}
N -130 550 -130 745 {}
N -70 520 -70 614 {}
N 45 520 45 580 {}
N 80 345 80 405 {}
N 80 465 80 525 {}
N 85 -140 85 -30 {}
N 85 30 85 90 {}
N 85 170 85 230 {}
N 85 290 85 350 {}
N 85 430 85 490 {}
N 85 550 85 745 {}
N 145 0 145 94 {}
N 145 260 145 354 {}
N 145 520 145 614 {}
N 255 -60 255 70 {}
N 255 200 255 260 {}
N 255 450 255 520 {}
N 290 255 290 315 {}
N 290 635 290 695 {}
N 295 -140 295 -30 {}
N 295 30 295 70 {}
N 295 170 295 230 {}
N 295 290 295 350 {}
N 295 430 295 490 {}
N 295 550 295 745 {}
N 355 0 355 94 {}
N 355 260 355 354 {}
N 355 520 355 614 {}
N 470 -60 470 70 {}
N 470 200 470 260 {}
N 470 450 470 520 {}
N 505 345 505 405 {}
N 505 465 505 525 {}
N 510 -140 510 -30 {}
N 510 30 510 70 {}
N 510 170 510 230 {}
N 510 290 510 350 {}
N 510 430 510 490 {}
N 510 550 510 745 {}
N 570 0 570 94 {}
N 570 260 570 354 {}
N 570 520 570 614 {}
N 650 0 650 60 {}
N 650 260 650 330 {}
N 665 345 665 405 {}
N 665 465 665 525 {}
N 680 -60 680 0 {}
N 680 200 680 260 {}
N 680 450 680 520 {}
N 720 -140 720 -30 {}
N 720 30 720 90 {}
N 720 170 720 230 {}
N 720 290 720 350 {}
N 720 430 720 490 {}
N 720 550 720 745 {}
N 780 0 780 94 {}
N 780 260 780 354 {}
N 780 520 780 614 {}
N 855 345 855 405 {}
N 855 465 855 525 {}
N 1020 -60 1020 0 {}
N 1020 450 1020 520 {}
N 1055 260 1055 405 {}
N 1055 465 1055 525 {}
N 1060 -140 1060 -30 {}
N 1060 30 1060 90 {}
N 1060 170 1060 230 {}
N 1060 290 1060 350 {}
N 1060 430 1060 490 {}
N 1060 550 1060 745 {}
N 1120 0 1120 94 {}
N 1120 260 1120 354 {}
N 1120 520 1120 614 {}
N 1230 200 1230 260 {}
N 1265 345 1265 405 {}
N 1265 550 1265 610 {}
N 1270 170 1270 230 {}
N 1270 290 1270 745 {}
N 1330 260 1330 354 {}
N 1450 200 1450 260 {}
N 1485 345 1485 405 {}
N 1485 465 1485 525 {}
N 1490 170 1490 230 {}
N 1490 290 1490 350 {}
N 1490 430 1490 490 {}
N 1490 550 1490 745 {}
N 1550 260 1550 354 {}
N 1685 170 1685 230 {}
N 1685 290 1685 320 {}
N 1685 465 1685 525 {}
N 1845 345 1845 405 {}
N 1845 465 1845 525 {}
N 2005 345 2005 405 {}
N 2005 465 2005 525 {}
N -1665 -140 2220 -140 {}
N -300 0 -240 0 {}
N -200 0 -140 0 {}
N -15 0 45 0 {}
N 85 0 145 0 {}
N 295 0 355 0 {}
N 510 0 570 0 {}
N 650 0 680 0 {}
N 720 0 780 0 {}
N 990 0 1020 0 {}
N 1060 0 1120 0 {}
N 255 70 295 70 {}
N 470 70 510 70 {}
N -1040 260 -980 260 {}
N -940 260 -880 260 {}
N -800 260 -770 260 {}
N -730 260 -670 260 {}
N -580 260 -550 260 {}
N -510 260 -450 260 {}
N -300 260 -240 260 {}
N -200 260 -130 260 {}
N -15 260 45 260 {}
N 85 260 145 260 {}
N 225 260 255 260 {}
N 295 260 355 260 {}
N 440 260 470 260 {}
N 510 260 570 260 {}
N 650 260 680 260 {}
N 720 260 780 260 {}
N 960 260 1020 260 {}
N 1060 260 1120 260 {}
N 1200 260 1265 260 {}
N 1270 260 1330 260 {}
N 1420 260 1450 260 {}
N 1490 260 1550 260 {}
N 290 285 1845 285 {}
N -220 330 650 330 {}
N 230 375 290 375 {}
N -390 450 -350 450 {}
N -220 450 -170 450 {}
N 255 450 295 450 {}
N 470 450 510 450 {}
N 680 450 720 450 {}
N 1020 450 1060 450 {}
N 1060 460 1265 460 {}
N -350 520 -290 520 {}
N -200 520 -170 520 {}
N -130 520 -70 520 {}
N 15 520 45 520 {}
N 85 520 145 520 {}
N 295 520 355 520 {}
N 510 520 570 520 {}
N 720 520 780 520 {}
N 1060 520 1120 520 {}
N 1265 580 2005 580 {}
N -1665 745 2220 745 {}
C {devices/lab_wire.sym} -1665 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1665 745 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -170 580 2 0 {name=l2 lab=ea_n}
C {devices/lab_wire.sym} 45 580 2 0 {name=l3 lab=ea_n}
C {devices/lab_wire.sym} 85 350 2 0 {name=l4 lab=ea_n}
C {devices/lab_wire.sym} 295 430 0 1 {name=l5 lab=ea_n}
C {devices/lab_wire.sym} 510 430 0 1 {name=l6 lab=ea_n}
C {devices/lab_wire.sym} 510 350 2 0 {name=l7 lab=ea_n}
C {devices/lab_wire.sym} -510 350 2 0 {name=l8 lab=ea_o1}
C {devices/lab_wire.sym} -140 260 0 1 {name=l9 lab=ea_o1}
C {devices/lab_wire.sym} -130 430 0 1 {name=l10 lab=ea_o1}
C {devices/lab_wire.sym} 85 430 0 1 {name=l11 lab=ea_o1}
C {devices/lab_wire.sym} 1060 350 2 0 {name=l12 lab=ea_o1}
C {devices/lab_wire.sym} -240 90 2 0 {name=l13 lab=ea_out}
C {devices/lab_wire.sym} -240 170 0 1 {name=l14 lab=ea_out}
C {devices/lab_wire.sym} 680 200 0 1 {name=l15 lab=ea_out}
C {devices/lab_wire.sym} -510 170 0 1 {name=l16 lab=ea_tail}
C {devices/lab_wire.sym} 85 170 0 1 {name=l17 lab=ea_tail}
C {devices/lab_wire.sym} 510 170 0 1 {name=l18 lab=ea_tail}
C {devices/lab_wire.sym} 1060 90 2 0 {name=l19 lab=ea_tail}
C {devices/lab_wire.sym} 1060 170 0 1 {name=l20 lab=ea_tail}
C {devices/lab_wire.sym} -515 525 2 0 {name=l21 lab=fb}
C {devices/lab_wire.sym} -15 260 0 0 {name=l22 lab=fb}
C {devices/lab_wire.sym} 470 200 0 1 {name=l23 lab=fb}
C {devices/lab_wire.sym} 1055 345 0 1 {name=l24 lab=fb}
C {devices/lab_wire.sym} 1685 290 0 0 {name=l25 lab=fb}
C {devices/lab_wire.sym} -940 170 0 1 {name=l26 lab=gate}
C {devices/lab_wire.sym} 85 90 2 0 {name=l27 lab=gate}
C {devices/lab_wire.sym} 680 -60 0 1 {name=l28 lab=gate}
C {devices/lab_wire.sym} 1490 170 0 1 {name=l29 lab=gate}
C {devices/lab_wire.sym} 290 465 0 0 {name=l30 lab=lp_brk}
C {devices/lab_wire.sym} 1685 170 0 1 {name=l31 lab=lp_brk}
C {devices/lab_wire.sym} 290 405 0 0 {name=l32 lab=n_r1_1}
C {devices/lab_wire.sym} 505 525 2 0 {name=l33 lab=n_r1_1}
C {devices/lab_wire.sym} 80 525 2 0 {name=l34 lab=n_r1_2}
C {devices/lab_wire.sym} 505 345 0 1 {name=l35 lab=n_r1_2}
C {devices/lab_wire.sym} 80 345 0 1 {name=l36 lab=n_r1_3}
C {devices/lab_wire.sym} 665 525 2 0 {name=l37 lab=n_r1_3}
C {devices/lab_wire.sym} -135 525 2 0 {name=l38 lab=n_r1_4}
C {devices/lab_wire.sym} 665 345 0 1 {name=l39 lab=n_r1_4}
C {devices/lab_wire.sym} -135 345 0 1 {name=l40 lab=n_r1_5}
C {devices/lab_wire.sym} 855 525 2 0 {name=l41 lab=n_r1_5}
C {devices/lab_wire.sym} -355 525 2 0 {name=l42 lab=n_r1_6}
C {devices/lab_wire.sym} 855 345 0 1 {name=l43 lab=n_r1_6}
C {devices/lab_wire.sym} -355 345 0 1 {name=l44 lab=n_r1_7}
C {devices/lab_wire.sym} 1055 525 2 0 {name=l45 lab=n_r1_7}
C {devices/lab_wire.sym} -515 345 0 1 {name=l46 lab=n_r2_1}
C {devices/lab_wire.sym} 1265 465 0 0 {name=l47 lab=n_r2_1}
C {devices/lab_wire.sym} -735 525 2 0 {name=l48 lab=n_r2_2}
C {devices/lab_wire.sym} 1265 345 0 1 {name=l49 lab=n_r2_2}
C {devices/lab_wire.sym} -735 345 0 1 {name=l50 lab=n_r2_3}
C {devices/lab_wire.sym} 1485 525 2 0 {name=l51 lab=n_r2_3}
C {devices/lab_wire.sym} -945 525 2 0 {name=l52 lab=n_r2_4}
C {devices/lab_wire.sym} 1485 345 0 1 {name=l53 lab=n_r2_4}
C {devices/lab_wire.sym} -945 345 0 1 {name=l54 lab=n_r2_5}
C {devices/lab_wire.sym} 1685 525 2 0 {name=l55 lab=n_r2_5}
C {devices/lab_wire.sym} -1105 525 2 0 {name=l56 lab=n_r2_6}
C {devices/lab_wire.sym} 1685 405 0 0 {name=l57 lab=n_r2_6}
C {devices/lab_wire.sym} -1105 345 0 1 {name=l58 lab=n_r2_7}
C {devices/lab_wire.sym} 290 695 2 0 {name=l59 lab=n_r2_7}
C {devices/lab_wire.sym} 290 255 0 1 {name=l60 lab=n_rb_1}
C {devices/lab_wire.sym} 1845 525 2 0 {name=l61 lab=n_rb_1}
C {devices/lab_wire.sym} -1265 525 2 0 {name=l62 lab=n_rb_2}
C {devices/lab_wire.sym} 1845 345 0 1 {name=l63 lab=n_rb_2}
C {devices/lab_wire.sym} -1265 345 0 1 {name=l64 lab=n_rb_3}
C {devices/lab_wire.sym} 2005 525 2 0 {name=l65 lab=n_rb_3}
C {devices/lab_wire.sym} 1265 610 2 0 {name=l66 lab=n_rb_4}
C {devices/lab_wire.sym} 2005 345 0 1 {name=l67 lab=n_rb_4}
C {devices/lab_wire.sym} -1040 260 0 0 {name=l68 lab=nbias}
C {devices/lab_wire.sym} -770 200 0 1 {name=l69 lab=nbias}
C {devices/lab_wire.sym} -350 430 0 1 {name=l70 lab=nbias}
C {devices/lab_wire.sym} 1060 430 0 1 {name=l71 lab=nbias}
C {devices/lab_wire.sym} 1230 200 0 1 {name=l72 lab=nbias}
C {devices/lab_wire.sym} 1265 490 0 0 {name=l73 lab=nbias}
C {devices/lab_wire.sym} 1450 200 0 1 {name=l74 lab=nbias}
C {devices/lab_wire.sym} -730 170 0 1 {name=l75 lab=pbias}
C {devices/lab_wire.sym} -140 0 0 1 {name=l76 lab=pbias}
C {devices/lab_wire.sym} 470 -60 0 1 {name=l77 lab=pbias}
C {devices/lab_wire.sym} 1020 -60 0 1 {name=l78 lab=pbias}
C {devices/lab_wire.sym} 1270 170 0 1 {name=l79 lab=pbias}
C {devices/lab_wire.sym} 720 90 2 0 {name=l80 lab=vout}
C {devices/lab_wire.sym} 720 170 0 1 {name=l81 lab=vout}
C {devices/lab_wire.sym} 1490 430 0 1 {name=l82 lab=vout}
C {devices/lab_wire.sym} -550 200 0 1 {name=l83 lab=vref}
C {devices/lab_wire.sym} 960 260 0 0 {name=l84 lab=vref}
C {devices/lab_wire.sym} 255 200 0 1 {name=l85 lab=x1}
C {devices/lab_wire.sym} 720 430 0 1 {name=l86 lab=x1}
C {devices/lab_wire.sym} 720 350 2 0 {name=l87 lab=x1}
C {devices/lab_wire.sym} -15 0 0 0 {name=l88 lab=y}
C {devices/lab_wire.sym} 255 -60 0 1 {name=l89 lab=y}
C {devices/lab_wire.sym} 295 170 0 1 {name=l90 lab=y}
C {devices/lab_wire.sym} 570 94 2 0 {name=l91 lab=vdd}
C {devices/lab_wire.sym} 1120 94 2 0 {name=l92 lab=vdd}
C {devices/lab_wire.sym} 570 354 2 0 {name=l93 lab=vdd}
C {devices/lab_wire.sym} 145 354 2 0 {name=l94 lab=vdd}
C {devices/lab_wire.sym} 1120 354 2 0 {name=l95 lab=vdd}
C {devices/lab_wire.sym} -450 354 2 0 {name=l96 lab=vdd}
C {devices/lab_wire.sym} -300 94 2 0 {name=l97 lab=vdd}
C {devices/lab_wire.sym} 780 354 2 0 {name=l98 lab=vdd}
C {devices/lab_wire.sym} 355 94 2 0 {name=l99 lab=vdd}
C {devices/lab_wire.sym} 145 94 2 0 {name=l100 lab=vdd}
C {devices/lab_wire.sym} 780 94 2 0 {name=l101 lab=vdd}
C {devices/lab_wire.sym} -290 614 2 0 {name=l102 lab=vss}
C {devices/lab_wire.sym} 1120 614 2 0 {name=l103 lab=vss}
C {devices/lab_wire.sym} 1330 354 2 0 {name=l104 lab=vss}
C {devices/lab_wire.sym} -670 354 2 0 {name=l105 lab=vss}
C {devices/lab_wire.sym} 355 614 2 0 {name=l106 lab=vss}
C {devices/lab_wire.sym} 570 614 2 0 {name=l107 lab=vss}
C {devices/lab_wire.sym} 145 614 2 0 {name=l108 lab=vss}
C {devices/lab_wire.sym} -70 614 2 0 {name=l109 lab=vss}
C {devices/lab_wire.sym} -300 354 2 0 {name=l110 lab=vss}
C {devices/lab_wire.sym} 780 614 2 0 {name=l111 lab=vss}
C {devices/lab_wire.sym} 355 354 2 0 {name=l112 lab=vss}
C {devices/lab_wire.sym} 1550 354 2 0 {name=l113 lab=vss}
C {devices/lab_wire.sym} -880 354 2 0 {name=l114 lab=vss}
C {devices/lab_wire.sym} -1605 255 0 1 {name=l115 lab=vref}
C {devices/lab_wire.sym} -1605 435 2 0 {name=l116 lab=vss}
C {devices/lab_wire.sym} -1605 515 0 1 {name=l117 lab=lp_brk}
C {devices/lab_wire.sym} -1605 695 2 0 {name=l118 lab=vout}
C {devices/lab_wire.sym} 230 375 0 0 {name=l119 lab=vdd}
C {devices/lab_wire.sym} 290 575 0 0 {name=l120 lab=vss}
C {devices/lab_wire.sym} 295 350 2 0 {name=l121 lab=vss}
C {devices/lab_wire.sym} 1490 350 2 0 {name=l122 lab=vss}
C {devices/iopin.sym} -940 885 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -240 885 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 2360 30 0 0 {name=p2 lab=vout}
