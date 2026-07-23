v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_pmos_cascode_1} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 180 0 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 370 0 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -160 0 0 1 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -420 0 -420 94 {}
N -360 -90 -360 -30 {}
N -360 30 -360 90 {}
N -320 0 -320 60 {}
N -240 0 -240 94 {}
N -180 -90 -180 -30 {}
N -180 30 -180 90 {}
N 200 -90 200 -30 {}
N 200 30 200 90 {}
N 260 0 260 94 {}
N 350 -60 350 0 {}
N 390 -90 390 -30 {}
N 390 30 390 90 {}
N 450 0 450 94 {}
N -420 0 -360 0 {}
N -320 0 -290 0 {}
N -240 0 -180 0 {}
N -140 0 160 0 {}
N 200 0 260 0 {}
N 320 0 350 0 {}
N 390 0 450 0 {}
C {devices/lab_wire.sym} -180 -90 0 1 {name=l0 lab=d1n}
C {devices/lab_wire.sym} 390 90 2 0 {name=l1 lab=d1n}
C {devices/lab_wire.sym} -360 90 2 0 {name=l2 lab=d1p}
C {devices/lab_wire.sym} 200 -90 0 1 {name=l3 lab=d1p}
C {devices/lab_wire.sym} -360 -90 0 1 {name=l4 lab=tail}
C {devices/lab_wire.sym} 390 -90 0 1 {name=l5 lab=tail}
C {devices/lab_wire.sym} -80 0 0 1 {name=l6 lab=vb1}
C {devices/lab_wire.sym} -320 60 2 0 {name=l7 lab=vinn}
C {devices/lab_wire.sym} 350 -60 0 1 {name=l8 lab=vinp}
C {devices/lab_wire.sym} -180 90 2 0 {name=l9 lab=voutn}
C {devices/lab_wire.sym} 200 90 2 0 {name=l10 lab=voutp}
C {devices/lab_wire.sym} 260 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} 450 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} -240 94 2 0 {name=l14 lab=vdd}
C {devices/ipin.sym} -690 0 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -690 120 0 0 {name=p1 lab=vb1}
C {devices/ipin.sym} -690 240 0 0 {name=p2 lab=vinp}
C {devices/iopin.sym} -360 280 0 0 {name=p3 lab=tail}
C {devices/opin.sym} 720 30 0 0 {name=p4 lab=voutn}
C {devices/opin.sym} 720 150 0 0 {name=p5 lab=voutp}
