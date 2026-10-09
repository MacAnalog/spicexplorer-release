v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ea_stage2} -40 -200 0 0 0.4 0.4 {}
C {sg13g2_pr/sg13_lv_nmos.sym} 0 260 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {sg13g2_pr/sg13_lv_pmos.sym} 0 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xmbp_l}
C {sg13g2_pr/cap_cmim.sym} 180 260 0 0 {name=CC model=cap_cmim spiceprefix=X w=c_comp_w l=c_comp_w}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 400 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 180 200 180 230 {}
N 180 260 180 350 {}
N -110 -140 350 -140 {}
N -80 0 -20 0 {}
N 20 0 80 0 {}
N 20 200 180 200 {}
N -80 260 -20 260 {}
N 20 260 80 260 {}
N -110 400 350 400 {}
C {devices/lab_wire.sym} -110 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -110 400 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -80 260 0 0 {name=l2 lab=ea_o1}
C {devices/lab_wire.sym} 180 350 2 0 {name=l3 lab=ea_o1}
C {devices/lab_wire.sym} 20 90 2 0 {name=l4 lab=ea_out}
C {devices/lab_wire.sym} -80 0 0 0 {name=l5 lab=pbias}
C {devices/lab_wire.sym} 80 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} 80 354 2 0 {name=l7 lab=vss}
C {devices/ipin.sym} -250 0 0 0 {name=p0 lab=pbias}
C {devices/iopin.sym} -20 540 0 0 {name=p1 lab=vdd}
C {devices/iopin.sym} 100 540 0 0 {name=p2 lab=ea_o1}
C {devices/iopin.sym} 220 540 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 490 30 0 0 {name=p4 lab=ea_out}
