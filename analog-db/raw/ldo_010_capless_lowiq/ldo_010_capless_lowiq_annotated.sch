v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_010_capless_lowiq} -1675 -200 0 0 0.4 0.4 {}
C {devices/vsource_np.sym} -1635 605 0 0 {name=VLP value="dc 0" savecurrent=false}
C {devices/vsource_np.sym} -1635 345 0 0 {name=VREF value="dc \{vref_val\}" savecurrent=false}
C {sg13g2_pr/cap_cmim.sym} -55 390 0 0 {name=CC model=cap_cmim spiceprefix=X w=c_comp_w l=c_comp_w}
C {sg13g2_pr/cap_cmim.sym} 200 260 0 0 {name=CFF model=cap_cmim spiceprefix=X w=c_ff_w l=c_ff_w}
C {sg13g2_pr/cap_cmim.sym} 1675 520 0 0 {name=COUT model=cap_cmim spiceprefix=X w=c_out_w l=c_out_w m=c_out_m}
C {devices/sg13_lv_pmos_np.sym} 605 260 0 0 {name=M1A model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {devices/sg13_lv_pmos_np.sym} 1155 260 0 0 {name=M1B model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {devices/sg13_lv_pmos_np.sym} -450 260 0 0 {name=M2A model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {devices/sg13_lv_pmos_np.sym} 1405 260 0 0 {name=M2B model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} 605 520 0 0 {name=M3A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {devices/sg13_lv_nmos_np.sym} 55 520 0 0 {name=M3B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {devices/sg13_lv_nmos_np.sym} -195 520 0 0 {name=M4A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {devices/sg13_lv_nmos_np.sym} 1155 520 0 0 {name=M4B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {devices/sg13_lv_nmos_np.sym} -55 260 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} -55 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xmbp_l}
C {devices/sg13_lv_nmos_np.sym} 855 520 0 0 {name=MA model=sg13_lv_nmos spiceprefix=X w=x_dut_xma_w l=x_dut_xma_l}
C {devices/sg13_lv_nmos_np.sym} 380 260 0 0 {name=MB model=sg13_lv_nmos spiceprefix=X w=x_dut_xma_w l=x_dut_xma_l}
C {devices/sg13_lv_nmos_np.sym} -450 520 0 0 {name=MB0A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb0_w/2\}" l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} 1405 520 0 0 {name=MB0B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb0_w/2\}" l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} -710 260 0 0 {name=MB1A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb1_w/2\}" l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} 1655 260 0 0 {name=MB1B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb1_w/2\}" l=x_dut_xmb0_l}
C {devices/sg13_lv_pmos_np.sym} 195 0 0 1 {name=MBP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmbp_w l=x_dut_xmbp_l}
C {devices/sg13_lv_pmos_np.sym} 855 260 0 0 {name=MC model=sg13_lv_pmos spiceprefix=X w=x_dut_xmc_w l=x_dut_xmc_l}
C {devices/sg13_lv_pmos_np.sym} 380 0 0 0 {name=MCP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcp_w l=x_dut_xmcp_l}
C {devices/sg13_lv_pmos_np.sym} 605 0 0 0 {name=MD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcp_w l=x_dut_xmcp_l}
C {devices/sg13_lv_pmos_np.sym} 855 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xmp_w/x_dut_xmp_nf_mult\}" l=x_dut_xmp_l m="\{x_dut_xmp_m*x_dut_xmp_nf_mult\}"}
C {devices/sg13_lv_nmos_np.sym} -960 260 0 0 {name=MSA model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xms_w/2\}" l=x_dut_xms_l}
C {devices/sg13_lv_nmos_np.sym} 1915 260 0 0 {name=MSB model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xms_w/2\}" l=x_dut_xms_l}
C {devices/sg13_lv_pmos_np.sym} -310 0 0 1 {name=MT model=sg13_lv_pmos spiceprefix=X w=x_dut_xmt_w l=x_dut_xmbp_l}
C {sg13g2_pr/rhigh.sym} 360 435 0 0 {name=R1_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 525 435 0 0 {name=R1_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 200 435 0 0 {name=R1_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 750 435 0 0 {name=R1_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -50 435 0 0 {name=R1_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 980 435 0 0 {name=R1_6 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -305 435 0 0 {name=R1_7 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1140 435 0 0 {name=R1_8 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -565 435 0 0 {name=R2_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1300 435 0 0 {name=R2_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -815 435 0 0 {name=R2_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1550 435 0 0 {name=R2_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -975 435 0 0 {name=R2_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 1800 435 0 0 {name=R2_6 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} -1135 435 0 0 {name=R2_7 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 360 605 0 0 {name=R2_8 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 360 345 0 0 {name=RB_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 2060 435 0 0 {name=RB_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} -1295 435 0 0 {name=RB_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 2220 435 0 0 {name=RB_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 360 520 0 0 {name=RB_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
N -1635 255 -1635 315 {}
N -1635 375 -1635 435 {}
N -1635 515 -1635 575 {}
N -1635 635 -1635 695 {}
N -1295 345 -1295 405 {}
N -1295 465 -1295 525 {}
N -1255 375 -1255 665 {}
N -1135 345 -1135 405 {}
N -1135 465 -1135 525 {}
N -1010 260 -1010 320 {}
N -975 345 -975 405 {}
N -975 465 -975 525 {}
N -940 200 -940 230 {}
N -940 290 -940 745 {}
N -880 260 -880 354 {}
N -815 345 -815 405 {}
N -815 465 -815 525 {}
N -760 260 -760 320 {}
N -690 170 -690 230 {}
N -690 290 -690 745 {}
N -630 260 -630 354 {}
N -565 345 -565 405 {}
N -565 465 -565 525 {}
N -470 450 -470 520 {}
N -430 170 -430 230 {}
N -430 290 -430 350 {}
N -430 430 -430 490 {}
N -430 550 -430 745 {}
N -390 0 -390 94 {}
N -370 260 -370 354 {}
N -370 520 -370 614 {}
N -330 -140 -330 -30 {}
N -330 30 -330 90 {}
N -305 345 -305 405 {}
N -305 465 -305 525 {}
N -175 430 -175 490 {}
N -175 550 -175 745 {}
N -135 0 -135 94 {}
N -135 260 -135 354 {}
N -115 520 -115 614 {}
N -75 -140 -75 -30 {}
N -75 30 -75 90 {}
N -75 290 -75 745 {}
N -55 330 -55 360 {}
N -55 420 -55 450 {}
N -50 345 -50 405 {}
N -50 465 -50 525 {}
N -15 60 -15 230 {}
N -5 -60 -5 0 {}
N -5 260 -5 450 {}
N 5 230 5 330 {}
N 35 450 35 520 {}
N 75 430 75 490 {}
N 75 550 75 745 {}
N 115 0 115 94 {}
N 135 520 135 614 {}
N 175 -140 175 -30 {}
N 175 30 175 70 {}
N 200 170 200 230 {}
N 200 375 200 405 {}
N 200 465 200 525 {}
N 215 -60 215 70 {}
N 360 -60 360 70 {}
N 360 285 360 315 {}
N 360 635 360 665 {}
N 400 -140 400 -30 {}
N 400 30 400 70 {}
N 400 290 400 745 {}
N 460 60 460 230 {}
N 460 260 460 354 {}
N 525 345 525 405 {}
N 525 465 525 525 {}
N 555 0 555 60 {}
N 585 450 585 520 {}
N 625 -140 625 -30 {}
N 625 30 625 60 {}
N 625 170 625 230 {}
N 625 290 625 350 {}
N 625 430 625 490 {}
N 625 550 625 745 {}
N 685 60 685 200 {}
N 685 260 685 354 {}
N 685 520 685 614 {}
N 750 345 750 405 {}
N 750 465 750 525 {}
N 805 0 805 60 {}
N 805 260 805 330 {}
N 835 450 835 520 {}
N 875 -140 875 -30 {}
N 875 30 875 90 {}
N 875 170 875 230 {}
N 875 290 875 350 {}
N 875 430 875 490 {}
N 875 550 875 745 {}
N 935 0 935 94 {}
N 935 260 935 354 {}
N 935 520 935 614 {}
N 980 345 980 405 {}
N 980 465 980 525 {}
N 1140 260 1140 405 {}
N 1140 465 1140 525 {}
N 1175 170 1175 230 {}
N 1175 290 1175 350 {}
N 1175 430 1175 490 {}
N 1175 550 1175 745 {}
N 1235 260 1235 354 {}
N 1235 520 1235 614 {}
N 1300 345 1300 405 {}
N 1300 465 1300 525 {}
N 1385 450 1385 520 {}
N 1425 170 1425 230 {}
N 1425 290 1425 350 {}
N 1425 430 1425 490 {}
N 1425 550 1425 745 {}
N 1485 260 1485 354 {}
N 1485 520 1485 614 {}
N 1550 345 1550 405 {}
N 1550 465 1550 525 {}
N 1675 170 1675 230 {}
N 1675 290 1675 350 {}
N 1675 460 1675 490 {}
N 1675 550 1675 745 {}
N 1735 260 1735 354 {}
N 1800 345 1800 405 {}
N 1800 465 1800 525 {}
N 1935 170 1935 230 {}
N 1935 290 1935 745 {}
N 1995 260 1995 354 {}
N 2060 345 2060 405 {}
N 2060 465 2060 525 {}
N 2220 345 2220 405 {}
N 2220 465 2220 525 {}
N -1695 -140 2545 -140 {}
N -5 -60 215 -60 {}
N -390 0 -330 0 {}
N -290 0 -230 0 {}
N -135 0 -75 0 {}
N -35 0 25 0 {}
N 115 0 175 0 {}
N 555 0 585 0 {}
N 775 0 835 0 {}
N 875 0 935 0 {}
N -75 60 -15 60 {}
N 400 60 555 60 {}
N 625 60 805 60 {}
N 175 70 215 70 {}
N 360 70 400 70 {}
N -940 200 685 200 {}
N -75 230 5 230 {}
N 400 230 460 230 {}
N -1040 260 -980 260 {}
N -940 260 -880 260 {}
N -760 260 -730 260 {}
N -690 260 -630 260 {}
N -530 260 -470 260 {}
N -430 260 -370 260 {}
N -135 260 -75 260 {}
N -35 260 25 260 {}
N 300 260 360 260 {}
N 400 260 460 260 {}
N 525 260 585 260 {}
N 625 260 685 260 {}
N 805 260 835 260 {}
N 875 260 935 260 {}
N 1075 260 1140 260 {}
N 1175 260 1235 260 {}
N 1325 260 1385 260 {}
N 1425 260 1485 260 {}
N 1575 260 1635 260 {}
N 1675 260 1735 260 {}
N 1835 260 1895 260 {}
N 1935 260 1995 260 {}
N -1010 320 -760 320 {}
N -55 330 805 330 {}
N -1255 375 -1135 375 {}
N 300 375 360 375 {}
N -470 450 -430 450 {}
N -55 450 -5 450 {}
N 35 450 75 450 {}
N 585 450 625 450 {}
N 835 450 875 450 {}
N 1385 450 1425 450 {}
N -430 520 -370 520 {}
N -275 520 -215 520 {}
N -175 520 -115 520 {}
N 75 520 135 520 {}
N 625 520 685 520 {}
N 875 520 935 520 {}
N 1075 520 1135 520 {}
N 1175 520 1235 520 {}
N 1425 520 1485 520 {}
N -1255 665 360 665 {}
N -1695 745 2545 745 {}
C {devices/lab_wire.sym} -275 520 0 0 {name=l0 lab=ea_n}
C {devices/lab_wire.sym} 75 430 0 1 {name=l1 lab=ea_n}
C {devices/lab_wire.sym} 625 430 0 1 {name=l2 lab=ea_n}
C {devices/lab_wire.sym} 625 350 2 0 {name=l3 lab=ea_n}
C {devices/lab_wire.sym} 1075 520 0 0 {name=l4 lab=ea_n}
C {devices/lab_wire.sym} 1175 350 2 0 {name=l5 lab=ea_n}
C {devices/lab_wire.sym} -430 350 2 0 {name=l6 lab=ea_o1}
C {devices/lab_wire.sym} -175 430 0 1 {name=l7 lab=ea_o1}
C {devices/lab_wire.sym} 25 260 0 1 {name=l8 lab=ea_o1}
C {devices/lab_wire.sym} 1175 430 0 1 {name=l9 lab=ea_o1}
C {devices/lab_wire.sym} 1425 350 2 0 {name=l10 lab=ea_o1}
C {devices/lab_wire.sym} -75 90 2 0 {name=l11 lab=ea_out}
C {devices/lab_wire.sym} -430 170 0 1 {name=l12 lab=ea_tail}
C {devices/lab_wire.sym} -330 90 2 0 {name=l13 lab=ea_tail}
C {devices/lab_wire.sym} 625 170 0 1 {name=l14 lab=ea_tail}
C {devices/lab_wire.sym} 1175 170 0 1 {name=l15 lab=ea_tail}
C {devices/lab_wire.sym} 1425 170 0 1 {name=l16 lab=ea_tail}
C {devices/lab_wire.sym} -565 525 2 0 {name=l17 lab=fb}
C {devices/lab_wire.sym} 200 290 0 0 {name=l18 lab=fb}
C {devices/lab_wire.sym} 525 260 0 0 {name=l19 lab=fb}
C {devices/lab_wire.sym} 1075 260 0 0 {name=l20 lab=fb}
C {devices/lab_wire.sym} 775 0 0 0 {name=l21 lab=gate}
C {devices/lab_wire.sym} 1935 170 0 1 {name=l22 lab=gate}
C {devices/lab_wire.sym} 200 170 0 1 {name=l23 lab=lp_brk}
C {devices/lab_wire.sym} 360 465 0 0 {name=l24 lab=lp_brk}
C {devices/lab_wire.sym} 360 405 0 0 {name=l25 lab=n_r1_1}
C {devices/lab_wire.sym} 525 525 2 0 {name=l26 lab=n_r1_1}
C {devices/lab_wire.sym} 200 525 2 0 {name=l27 lab=n_r1_2}
C {devices/lab_wire.sym} 525 345 0 1 {name=l28 lab=n_r1_2}
C {devices/lab_wire.sym} 200 405 0 0 {name=l29 lab=n_r1_3}
C {devices/lab_wire.sym} 750 525 2 0 {name=l30 lab=n_r1_3}
C {devices/lab_wire.sym} -50 525 2 0 {name=l31 lab=n_r1_4}
C {devices/lab_wire.sym} 750 345 0 1 {name=l32 lab=n_r1_4}
C {devices/lab_wire.sym} -50 345 0 1 {name=l33 lab=n_r1_5}
C {devices/lab_wire.sym} 980 525 2 0 {name=l34 lab=n_r1_5}
C {devices/lab_wire.sym} -305 525 2 0 {name=l35 lab=n_r1_6}
C {devices/lab_wire.sym} 980 345 0 1 {name=l36 lab=n_r1_6}
C {devices/lab_wire.sym} -305 345 0 1 {name=l37 lab=n_r1_7}
C {devices/lab_wire.sym} 1140 525 2 0 {name=l38 lab=n_r1_7}
C {devices/lab_wire.sym} -565 345 0 1 {name=l39 lab=n_r2_1}
C {devices/lab_wire.sym} 1300 525 2 0 {name=l40 lab=n_r2_1}
C {devices/lab_wire.sym} -815 525 2 0 {name=l41 lab=n_r2_2}
C {devices/lab_wire.sym} 1300 345 0 1 {name=l42 lab=n_r2_2}
C {devices/lab_wire.sym} -815 345 0 1 {name=l43 lab=n_r2_3}
C {devices/lab_wire.sym} 1550 525 2 0 {name=l44 lab=n_r2_3}
C {devices/lab_wire.sym} -975 525 2 0 {name=l45 lab=n_r2_4}
C {devices/lab_wire.sym} 1550 345 0 1 {name=l46 lab=n_r2_4}
C {devices/lab_wire.sym} -975 345 0 1 {name=l47 lab=n_r2_5}
C {devices/lab_wire.sym} 1800 525 2 0 {name=l48 lab=n_r2_5}
C {devices/lab_wire.sym} -1135 525 2 0 {name=l49 lab=n_r2_6}
C {devices/lab_wire.sym} 1800 345 0 1 {name=l50 lab=n_r2_6}
C {devices/lab_wire.sym} -1135 345 0 1 {name=l51 lab=n_r2_7}
C {devices/lab_wire.sym} 360 315 0 0 {name=l52 lab=n_rb_1}
C {devices/lab_wire.sym} 2060 525 2 0 {name=l53 lab=n_rb_1}
C {devices/lab_wire.sym} -1295 525 2 0 {name=l54 lab=n_rb_2}
C {devices/lab_wire.sym} 2060 345 0 1 {name=l55 lab=n_rb_2}
C {devices/lab_wire.sym} -1295 345 0 1 {name=l56 lab=n_rb_3}
C {devices/lab_wire.sym} 2220 525 2 0 {name=l57 lab=n_rb_3}
C {devices/lab_wire.sym} 360 550 0 0 {name=l58 lab=n_rb_4}
C {devices/lab_wire.sym} 2220 345 0 1 {name=l59 lab=n_rb_4}
C {devices/lab_wire.sym} -1040 260 0 0 {name=l60 lab=nbias}
C {devices/lab_wire.sym} -430 430 0 1 {name=l61 lab=nbias}
C {devices/lab_wire.sym} 360 490 0 0 {name=l62 lab=nbias}
C {devices/lab_wire.sym} 1425 430 0 1 {name=l63 lab=nbias}
C {devices/lab_wire.sym} 1575 260 0 0 {name=l64 lab=nbias}
C {devices/lab_wire.sym} 1835 260 0 0 {name=l65 lab=nbias}
C {devices/lab_wire.sym} -690 170 0 1 {name=l66 lab=pbias}
C {devices/lab_wire.sym} -230 0 0 1 {name=l67 lab=pbias}
C {devices/lab_wire.sym} 25 0 0 1 {name=l68 lab=pbias}
C {devices/lab_wire.sym} 1675 170 0 1 {name=l69 lab=pbias}
C {devices/lab_wire.sym} 875 90 2 0 {name=l70 lab=vout}
C {devices/lab_wire.sym} 875 170 0 1 {name=l71 lab=vout}
C {devices/lab_wire.sym} -530 260 0 0 {name=l72 lab=vref}
C {devices/lab_wire.sym} 1325 260 0 0 {name=l73 lab=vref}
C {devices/lab_wire.sym} 300 260 0 0 {name=l74 lab=x1}
C {devices/lab_wire.sym} 875 430 0 1 {name=l75 lab=x1}
C {devices/lab_wire.sym} 875 350 2 0 {name=l76 lab=x1}
C {devices/lab_wire.sym} 360 -60 0 1 {name=l77 lab=y}
C {devices/lab_wire.sym} 685 354 2 0 {name=l78 lab=vdd}
C {devices/lab_wire.sym} 1235 354 2 0 {name=l79 lab=vdd}
C {devices/lab_wire.sym} -370 354 2 0 {name=l80 lab=vdd}
C {devices/lab_wire.sym} 1485 354 2 0 {name=l81 lab=vdd}
C {devices/lab_wire.sym} -135 94 2 0 {name=l82 lab=vdd}
C {devices/lab_wire.sym} 115 94 2 0 {name=l83 lab=vdd}
C {devices/lab_wire.sym} 935 354 2 0 {name=l84 lab=vdd}
C {devices/lab_wire.sym} 400 0 0 0 {name=l85 lab=vdd}
C {devices/lab_wire.sym} 625 0 0 0 {name=l86 lab=vdd}
C {devices/lab_wire.sym} 935 94 2 0 {name=l87 lab=vdd}
C {devices/lab_wire.sym} -390 94 2 0 {name=l88 lab=vdd}
C {devices/lab_wire.sym} 685 614 2 0 {name=l89 lab=vss}
C {devices/lab_wire.sym} 135 614 2 0 {name=l90 lab=vss}
C {devices/lab_wire.sym} -115 614 2 0 {name=l91 lab=vss}
C {devices/lab_wire.sym} 1235 614 2 0 {name=l92 lab=vss}
C {devices/lab_wire.sym} -135 354 2 0 {name=l93 lab=vss}
C {devices/lab_wire.sym} 935 614 2 0 {name=l94 lab=vss}
C {devices/lab_wire.sym} 460 354 2 0 {name=l95 lab=vss}
C {devices/lab_wire.sym} -370 614 2 0 {name=l96 lab=vss}
C {devices/lab_wire.sym} 1485 614 2 0 {name=l97 lab=vss}
C {devices/lab_wire.sym} -630 354 2 0 {name=l98 lab=vss}
C {devices/lab_wire.sym} 1735 354 2 0 {name=l99 lab=vss}
C {devices/lab_wire.sym} -880 354 2 0 {name=l100 lab=vss}
C {devices/lab_wire.sym} 1995 354 2 0 {name=l101 lab=vss}
C {devices/lab_wire.sym} -1635 515 0 1 {name=l102 lab=lp_brk}
C {devices/lab_wire.sym} -1635 695 2 0 {name=l103 lab=vout}
C {devices/lab_wire.sym} -1635 255 0 1 {name=l104 lab=vref}
C {devices/lab_wire.sym} -1635 435 2 0 {name=l105 lab=vss}
C {devices/lab_wire.sym} 300 375 0 0 {name=l106 lab=vdd}
C {devices/lab_wire.sym} 1675 350 2 0 {name=l107 lab=vss}
C {devices/lab_wire.sym} 360 575 0 0 {name=l108 lab=vss}
C {devices/iopin.sym} -1695 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -1695 745 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 1675 460 0 0 {name=p2 lab=vout}
B 8 -265 442 1563 598 {fill=0}
T {NMOS Simple Current Mirror (2 outputs)} -265 424 0 0 0.3 0.3 {layer=8}
B 10 -265 442 1563 598 {fill=0}
T {NMOS Simple Current Mirror (2 outputs)} -265 400 0 0 0.3 0.3 {layer=10}
B 12 310 182 1231 598 {fill=0}
T {NMOS Simple Current Mirror} 310 164 0 0 0.3 0.3 {layer=12}
B 21 -1030 182 2323 598 {fill=0}
T {NMOS Simple Current Mirror (4 outputs)} -1030 164 0 0 0.3 0.3 {layer=21}
B 15 -1030 182 2323 598 {fill=0}
T {NMOS Simple Current Mirror (4 outputs)} -1030 140 0 0 0.3 0.3 {layer=15}
B 13 -694 -78 265 78 {fill=0}
T {PMOS Simple Current Mirror (2 outputs)} -694 -96 0 0 0.3 0.3 {layer=13}
B 18 310 -78 997 78 {fill=0}
T {PMOS Simple Current Mirror} 310 -96 0 0 0.3 0.3 {layer=18}
B 20 -520 182 1013 338 {fill=0}
T {PMOS Differential Pair} -520 164 0 0 0.3 0.3 {layer=20}
B 8 535 182 1813 338 {fill=0}
T {PMOS Differential Pair} 535 164 0 0 0.3 0.3 {layer=8}
B 10 -520 182 1563 338 {fill=0}
T {PMOS Differential Pair} -520 140 0 0 0.3 0.3 {layer=10}
B 12 1085 182 1813 338 {fill=0}
T {PMOS Differential Pair} 1085 164 0 0 0.3 0.3 {layer=12}
