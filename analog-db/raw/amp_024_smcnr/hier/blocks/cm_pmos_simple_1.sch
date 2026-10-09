v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_1} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 340 0 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -420 0 -420 94 {}
N -360 -140 -360 -30 {}
N -360 30 -360 60 {}
N -50 -60 -50 0 {}
N 20 -140 20 -30 {}
N 20 30 20 60 {}
N 80 0 80 94 {}
N 320 -60 320 70 {}
N 360 -140 360 -30 {}
N 360 30 360 70 {}
N 420 0 420 94 {}
N -815 -140 815 -140 {}
N -50 -60 320 -60 {}
N -420 0 -360 0 {}
N -320 0 -20 0 {}
N 20 0 80 0 {}
N 360 0 420 0 {}
N 320 70 360 70 {}
C {devices/lab_wire.sym} -420 94 2 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l1 lab=vdd}
C {devices/lab_wire.sym} 420 94 2 0 {name=l2 lab=vdd}
C {devices/iopin.sym} -815 -140 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 360 60 0 0 {name=p1 lab=ibias}
C {devices/opin.sym} -360 60 0 0 {name=p2 lab=vout}
C {devices/opin.sym} 20 60 0 0 {name=p3 lab=tailp}
