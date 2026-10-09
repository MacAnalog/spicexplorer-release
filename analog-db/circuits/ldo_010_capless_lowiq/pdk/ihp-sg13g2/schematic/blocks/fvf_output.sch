v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {fvf_output} -210 -200 0 0 0.4 0.4 {}
C {sg13g2_pr/sg13_lv_pmos.sym} 210 260 0 0 {name=MC model=sg13_lv_pmos spiceprefix=X w=x_dut_xmc_w l=x_dut_xmc_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 210 520 0 0 {name=MA model=sg13_lv_nmos spiceprefix=X w=x_dut_xma_w l=x_dut_xma_l}
C {sg13g2_pr/sg13_lv_nmos.sym} -170 260 0 1 {name=MB model=sg13_lv_nmos spiceprefix=X w=x_dut_xma_w l=x_dut_xma_l}
C {sg13g2_pr/sg13_lv_pmos.sym} -170 0 0 1 {name=MCP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcp_w l=x_dut_xmcp_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 0 0 0 0 {name=MD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcp_w l=x_dut_xmcp_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 0 260 0 0 {name=MSA model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xms_w/2\}" l=x_dut_xms_l}
C {sg13g2_pr/sg13_lv_nmos.sym} 520 260 0 0 {name=MSB model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xms_w/2\}" l=x_dut_xms_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 210 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w="\{x_dut_xmp_w/x_dut_xmp_nf_mult\}" l=x_dut_xmp_l m="\{x_dut_xmp_m*x_dut_xmp_nf_mult\}"}
N -250 0 -250 94 {}
N -250 260 -250 354 {}
N -190 -140 -190 -30 {}
N -190 30 -190 230 {}
N -190 290 -190 660 {}
N -150 0 -150 70 {}
N -150 260 -150 320 {}
N -50 0 -50 60 {}
N -20 200 -20 260 {}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 660 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 160 0 160 60 {}
N 190 -60 190 0 {}
N 190 200 190 260 {}
N 190 450 190 520 {}
N 230 -140 230 -30 {}
N 230 30 230 90 {}
N 230 170 230 230 {}
N 230 290 230 490 {}
N 230 550 230 660 {}
N 290 0 290 94 {}
N 290 260 290 354 {}
N 290 520 290 614 {}
N 540 170 540 230 {}
N 540 290 540 660 {}
N 600 260 600 354 {}
N -385 -140 760 -140 {}
N -250 0 -190 0 {}
N -50 0 -20 0 {}
N 20 0 80 0 {}
N 160 0 190 0 {}
N 230 0 290 0 {}
N -190 60 -50 60 {}
N 20 60 160 60 {}
N -190 70 -150 70 {}
N -250 260 -190 260 {}
N -150 260 -120 260 {}
N -50 260 -20 260 {}
N 20 260 80 260 {}
N 160 260 190 260 {}
N 230 260 290 260 {}
N 440 260 500 260 {}
N 540 260 600 260 {}
N 190 450 230 450 {}
N 230 520 290 520 {}
N -385 660 760 660 {}
C {devices/lab_wire.sym} -385 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -385 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 190 200 0 1 {name=l2 lab=ea_out}
C {devices/lab_wire.sym} 190 -60 0 1 {name=l3 lab=gate}
C {devices/lab_wire.sym} 540 170 0 1 {name=l4 lab=gate}
C {devices/lab_wire.sym} -20 200 0 1 {name=l5 lab=nbias}
C {devices/lab_wire.sym} 440 260 0 0 {name=l6 lab=nbias}
C {devices/lab_wire.sym} 230 90 2 0 {name=l7 lab=vout}
C {devices/lab_wire.sym} 230 170 0 1 {name=l8 lab=vout}
C {devices/lab_wire.sym} -150 320 2 0 {name=l9 lab=x1}
C {devices/lab_wire.sym} 230 350 2 0 {name=l10 lab=x1}
C {devices/lab_wire.sym} -150 60 2 0 {name=l11 lab=y}
C {devices/lab_wire.sym} 290 354 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} 290 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} 290 614 2 0 {name=l16 lab=vss}
C {devices/lab_wire.sym} -250 354 2 0 {name=l17 lab=vss}
C {devices/lab_wire.sym} 80 354 2 0 {name=l18 lab=vss}
C {devices/lab_wire.sym} 600 354 2 0 {name=l19 lab=vss}
C {devices/ipin.sym} -525 260 0 0 {name=p0 lab=nbias}
C {devices/ipin.sym} -525 380 0 0 {name=p1 lab=ea_out}
C {devices/iopin.sym} -190 800 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -70 800 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 900 30 0 0 {name=p4 lab=vout}
