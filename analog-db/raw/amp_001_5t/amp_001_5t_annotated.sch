v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_001_5t} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} -170 520 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_nmos_np.sym} 340 520 0 0 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -360 290 -360 350 {}
N -320 0 -320 70 {}
N -250 520 -250 614 {}
N -190 320 -190 490 {}
N -190 550 -190 660 {}
N -50 0 -50 60 {}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 320 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 320 450 320 520 {}
N 360 450 360 490 {}
N 360 550 360 660 {}
N 420 520 420 614 {}
N -815 -140 815 -140 {}
N -420 0 -360 0 {}
N -320 0 -260 0 {}
N -50 0 -20 0 {}
N 20 0 80 0 {}
N -360 60 -50 60 {}
N -360 70 -320 70 {}
N -420 260 -360 260 {}
N -320 260 -290 260 {}
N -110 260 -20 260 {}
N 20 260 80 260 {}
N -360 320 20 320 {}
N 320 450 360 450 {}
N -250 520 -190 520 {}
N -180 520 320 520 {}
N 360 520 420 520 {}
N -815 660 815 660 {}
C {devices/lab_wire.sym} -260 0 0 1 {name=l0 lab=outm}
C {devices/lab_wire.sym} -360 350 2 0 {name=l1 lab=tail}
C {devices/lab_wire.sym} -420 94 2 0 {name=l2 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l3 lab=vdd}
C {devices/lab_wire.sym} -420 354 2 0 {name=l4 lab=vss}
C {devices/lab_wire.sym} 80 354 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} -250 614 2 0 {name=l6 lab=vss}
C {devices/lab_wire.sym} 420 614 2 0 {name=l7 lab=vss}
C {devices/ipin.sym} -290 260 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} -110 260 0 0 {name=p1 lab=vinn}
C {devices/iopin.sym} -815 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -815 660 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 20 60 0 0 {name=p4 lab=vout}
C {devices/opin.sym} 360 450 0 0 {name=p5 lab=ibias}
B 8 -796 -78 456 78 {fill=0}
T {PMOS Simple Current Mirror} -796 -96 0 0 0.3 0.3 {layer=8}
B 10 -626 442 796 598 {fill=0}
T {NMOS Simple Current Mirror} -626 424 0 0 0.3 0.3 {layer=10}
B 12 -796 182 456 338 {fill=0}
T {NMOS Differential Pair} -796 164 0 0 0.3 0.3 {layer=12}
