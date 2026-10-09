v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {bias_ref} -635 -200 0 0 0.4 0.4 {}
C {sg13g2_pr/rhigh.sym} 85 260 0 0 {name=RB_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 85 345 0 0 {name=RB_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 245 345 0 0 {name=RB_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} 405 345 0 0 {name=RB_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/rhigh.sym} -170 345 1 0 {name=RB_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_bias_l/5\}"}
C {sg13g2_pr/sg13_lv_nmos.sym} -255 260 0 1 {name=MB0A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb0_w/2\}" l=x_dut_xmb0_l}
C {sg13g2_pr/sg13_lv_nmos.sym} -595 260 0 1 {name=MB0B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb0_w/2\}" l=x_dut_xmb0_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 645 260 0 0 {name=MB1A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb1_w/2\}" l=x_dut_xmb0_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 425 260 0 0 {name=MB1B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb1_w/2\}" l=x_dut_xmb0_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 255 0 0 0 {name=MBP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmbp_w l=x_dut_xmbp_l}
C {devices/lab_wire.sym} 85 290 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} 85 230 0 0 {name=l1 lab=n_rb_1}
C {devices/lab_wire.sym} 85 375 0 0 {name=l2 lab=n_rb_1}
C {devices/lab_wire.sym} 85 315 0 0 {name=l3 lab=n_rb_2}
C {devices/lab_wire.sym} 245 375 0 0 {name=l4 lab=n_rb_2}
C {devices/lab_wire.sym} 245 315 0 0 {name=l5 lab=n_rb_3}
C {devices/lab_wire.sym} 405 375 0 0 {name=l6 lab=n_rb_3}
C {devices/lab_wire.sym} 405 315 0 0 {name=l7 lab=n_rb_4}
C {devices/lab_wire.sym} -200 345 0 0 {name=l8 lab=n_rb_4}
C {devices/lab_wire.sym} -140 345 0 0 {name=l9 lab=nbias}
C {devices/lab_wire.sym} -275 230 0 0 {name=l10 lab=nbias}
C {devices/lab_wire.sym} -235 260 0 0 {name=l11 lab=nbias}
C {devices/lab_wire.sym} -275 290 0 0 {name=l12 lab=vss}
C {devices/lab_wire.sym} -275 260 0 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} -615 230 0 0 {name=l14 lab=nbias}
C {devices/lab_wire.sym} -575 260 0 0 {name=l15 lab=nbias}
C {devices/lab_wire.sym} -615 290 0 0 {name=l16 lab=vss}
C {devices/lab_wire.sym} -615 260 0 0 {name=l17 lab=vss}
C {devices/lab_wire.sym} 665 230 0 0 {name=l18 lab=pbias}
C {devices/lab_wire.sym} 625 260 0 0 {name=l19 lab=nbias}
C {devices/lab_wire.sym} 665 290 0 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} 665 260 0 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} 445 230 0 0 {name=l22 lab=pbias}
C {devices/lab_wire.sym} 405 260 0 0 {name=l23 lab=nbias}
C {devices/lab_wire.sym} 445 290 0 0 {name=l24 lab=vss}
C {devices/lab_wire.sym} 445 260 0 0 {name=l25 lab=vss}
C {devices/lab_wire.sym} 275 30 0 0 {name=l26 lab=pbias}
C {devices/lab_wire.sym} 235 0 0 0 {name=l27 lab=pbias}
C {devices/lab_wire.sym} 275 -30 0 0 {name=l28 lab=vdd}
C {devices/lab_wire.sym} 275 0 0 0 {name=l29 lab=vdd}
C {devices/opin.sym} -615 535 0 0 {name=p_nbias lab=nbias}
C {devices/opin.sym} -395 535 0 0 {name=p_pbias lab=pbias}
C {devices/iopin.sym} -175 535 0 0 {name=p_vdd lab=vdd}
C {devices/iopin.sym} 45 535 0 0 {name=p_vss lab=vss}
