v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_pmos_cascode_1} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 220 0 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 445 0 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -120 0 0 1 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -420 0 -420 94 {}
N -360 -60 -360 -30 {}
N -360 30 -360 90 {}
N -200 0 -200 94 {}
N -140 -90 -140 -30 {}
N -140 30 -140 60 {}
N 240 -90 240 -30 {}
N 240 30 240 60 {}
N 300 0 300 94 {}
N 465 -60 465 -30 {}
N 465 30 465 90 {}
N 525 0 525 94 {}
N -815 -140 920 -140 {}
N -420 -60 465 -60 {}
N -420 0 -360 0 {}
N -320 0 -290 0 {}
N -200 0 -140 0 {}
N -100 0 200 0 {}
N 240 0 300 0 {}
N 335 0 425 0 {}
N 465 0 525 0 {}
C {devices/lab_wire.sym} -815 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -140 -90 0 1 {name=l1 lab=d1n}
C {devices/lab_wire.sym} 465 90 2 0 {name=l2 lab=d1n}
C {devices/lab_wire.sym} -360 90 2 0 {name=l3 lab=d1p}
C {devices/lab_wire.sym} 240 -90 0 1 {name=l4 lab=d1p}
C {devices/lab_wire.sym} 300 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} 525 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} -200 94 2 0 {name=l8 lab=vdd}
C {devices/ipin.sym} -290 0 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -70 0 0 0 {name=p1 lab=vb1}
C {devices/ipin.sym} 335 0 0 0 {name=p2 lab=vinp}
C {devices/iopin.sym} -420 -60 0 0 {name=p3 lab=tail}
C {devices/opin.sym} -140 60 0 0 {name=p4 lab=voutn}
C {devices/opin.sym} 240 60 0 0 {name=p5 lab=voutp}
