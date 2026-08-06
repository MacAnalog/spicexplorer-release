v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_pmos_simple_2} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=M4_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_cmfb_w l=x_dut_xm4_cmfb_l m=x_dut_xm4_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M5_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_cmfb_w l=x_dut_xm5_cmfb_l m=x_dut_xm5_cmfb_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 190 -60 190 -30 {}
N 190 30 190 90 {}
N 250 0 250 94 {}
N -190 -60 190 -60 {}
N -250 0 -190 0 {}
N -150 0 -90 0 {}
N 90 0 150 0 {}
N 190 0 250 0 {}
C {devices/lab_wire.sym} 90 0 0 0 {name=l0 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 190 90 2 0 {name=l1 lab=cmfb__mirr}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l2 lab=cmfb__ptail}
C {devices/lab_wire.sym} -190 90 2 0 {name=l3 lab=vb4o}
C {devices/lab_wire.sym} -90 0 0 1 {name=l4 lab=vref_cm}
C {devices/lab_wire.sym} 250 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l6 lab=vdd}
C {devices/ipin.sym} -560 0 0 0 {name=p0 lab=vref_cm}
C {devices/ipin.sym} -560 120 0 0 {name=p1 lab=cmfb__cm_sense}
C {devices/iopin.sym} -190 280 0 0 {name=p2 lab=cmfb__ptail}
C {devices/opin.sym} 560 30 0 0 {name=p3 lab=vb4o}
C {devices/opin.sym} 560 150 0 0 {name=p4 lab=cmfb__mirr}
