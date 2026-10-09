v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_1} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l ng=x_dut_xm0_ng m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l ng=x_dut_xm11_ng m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} 340 0 0 0 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l ng=x_dut_xm12_ng m=x_dut_xm12_m}
N -420 0 -420 94 {}
N -360 -140 -360 -30 {}
N -360 30 -360 60 {}
N -20 -60 -20 70 {}
N 20 -140 20 -30 {}
N 20 30 20 70 {}
N 80 0 80 94 {}
N 290 -60 290 0 {}
N 360 -140 360 -30 {}
N 360 30 360 60 {}
N 420 0 420 94 {}
N -905 -140 935 -140 {}
N -20 -60 290 -60 {}
N -420 0 -360 0 {}
N -350 0 -20 0 {}
N 20 0 80 0 {}
N 290 0 320 0 {}
N 360 0 420 0 {}
N -20 70 20 70 {}
C {devices/lab_wire.sym} -420 94 2 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l1 lab=vdd}
C {devices/lab_wire.sym} 420 94 2 0 {name=l2 lab=vdd}
C {devices/iopin.sym} -905 -140 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 290 -60 0 0 {name=p1 lab=ibias}
C {devices/opin.sym} -360 60 0 0 {name=p2 lab=tail}
C {devices/opin.sym} 360 60 0 0 {name=p3 lab=nbias}
