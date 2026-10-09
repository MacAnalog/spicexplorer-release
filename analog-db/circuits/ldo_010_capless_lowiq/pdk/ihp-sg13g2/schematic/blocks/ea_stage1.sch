v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ea_stage1} -975 -200 0 0 0.4 0.4 {}
C {sg13g2_pr/sg13_lv_pmos.sym} -115 0 0 1 {name=MT model=sg13_lv_pmos spiceprefix=X w=x_dut_xmt_w l=x_dut_xmbp_l}
C {sg13g2_pr/sg13_lv_pmos.sym} -95 260 0 1 {name=M1A model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {sg13g2_pr/sg13_lv_pmos.sym} -370 260 0 1 {name=M1B model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 415 260 0 0 {name=M2A model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 200 260 0 0 {name=M2B model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xm1_w/2\}" l=x_dut_xm1_l}
C {sg13g2_pr/sg13_lv_nmos.sym} -710 520 0 1 {name=M3A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {sg13g2_pr/sg13_lv_nmos.sym} -935 520 0 1 {name=M3B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 925 520 0 0 {name=M4A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 650 520 0 0 {name=M4B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {devices/lab_wire.sym} -135 30 0 0 {name=l0 lab=ea_tail}
C {devices/lab_wire.sym} -95 0 0 0 {name=l1 lab=pbias}
C {devices/lab_wire.sym} -135 -30 0 0 {name=l2 lab=vdd}
C {devices/lab_wire.sym} -135 0 0 0 {name=l3 lab=vdd}
C {devices/lab_wire.sym} -115 290 0 0 {name=l4 lab=ea_n}
C {devices/lab_wire.sym} -75 260 0 0 {name=l5 lab=fb}
C {devices/lab_wire.sym} -115 230 0 0 {name=l6 lab=ea_tail}
C {devices/lab_wire.sym} -115 260 0 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} -390 290 0 0 {name=l8 lab=ea_n}
C {devices/lab_wire.sym} -350 260 0 0 {name=l9 lab=fb}
C {devices/lab_wire.sym} -390 230 0 0 {name=l10 lab=ea_tail}
C {devices/lab_wire.sym} -390 260 0 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} 435 290 0 0 {name=l12 lab=ea_o1}
C {devices/lab_wire.sym} 395 260 0 0 {name=l13 lab=vref}
C {devices/lab_wire.sym} 435 230 0 0 {name=l14 lab=ea_tail}
C {devices/lab_wire.sym} 435 260 0 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} 220 290 0 0 {name=l16 lab=ea_o1}
C {devices/lab_wire.sym} 180 260 0 0 {name=l17 lab=vref}
C {devices/lab_wire.sym} 220 230 0 0 {name=l18 lab=ea_tail}
C {devices/lab_wire.sym} 220 260 0 0 {name=l19 lab=vdd}
C {devices/lab_wire.sym} -730 490 0 0 {name=l20 lab=ea_n}
C {devices/lab_wire.sym} -690 520 0 0 {name=l21 lab=ea_n}
C {devices/lab_wire.sym} -730 550 0 0 {name=l22 lab=vss}
C {devices/lab_wire.sym} -730 520 0 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} -955 490 0 0 {name=l24 lab=ea_n}
C {devices/lab_wire.sym} -915 520 0 0 {name=l25 lab=ea_n}
C {devices/lab_wire.sym} -955 550 0 0 {name=l26 lab=vss}
C {devices/lab_wire.sym} -955 520 0 0 {name=l27 lab=vss}
C {devices/lab_wire.sym} 945 490 0 0 {name=l28 lab=ea_o1}
C {devices/lab_wire.sym} 905 520 0 0 {name=l29 lab=ea_n}
C {devices/lab_wire.sym} 945 550 0 0 {name=l30 lab=vss}
C {devices/lab_wire.sym} 945 520 0 0 {name=l31 lab=vss}
C {devices/lab_wire.sym} 670 490 0 0 {name=l32 lab=ea_o1}
C {devices/lab_wire.sym} 630 520 0 0 {name=l33 lab=ea_n}
C {devices/lab_wire.sym} 670 550 0 0 {name=l34 lab=vss}
C {devices/lab_wire.sym} 670 520 0 0 {name=l35 lab=vss}
C {devices/ipin.sym} -955 710 0 0 {name=p_fb lab=fb}
C {devices/ipin.sym} -735 710 0 0 {name=p_pbias lab=pbias}
C {devices/ipin.sym} -515 710 0 0 {name=p_vref lab=vref}
C {devices/opin.sym} -295 710 0 0 {name=p_ea_o1 lab=ea_o1}
C {devices/iopin.sym} -75 710 0 0 {name=p_vdd lab=vdd}
C {devices/iopin.sym} 145 710 0 0 {name=p_vss lab=vss}
