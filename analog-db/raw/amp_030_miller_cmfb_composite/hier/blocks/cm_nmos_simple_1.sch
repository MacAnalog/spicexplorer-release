v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_1} -550 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -510 0 0 1 {name=M10_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm10_core_w l=x_dut_xm10_core_l m=x_dut_xm10_core_m}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=M6_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_core_w l=x_dut_xm6_core_l m=x_dut_xm6_core_m}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=M7_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_core_w l=x_dut_xm7_core_l m=x_dut_xm7_core_m}
C {devices/sg13_lv_nmos_np.sym} 510 0 0 0 {name=M8_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm8_core_w l=x_dut_xm8_core_l m=x_dut_xm8_core_m}
N -590 0 -590 94 {}
N -530 -60 -530 -30 {}
N -530 30 -530 140 {}
N -460 -60 -460 0 {}
N -250 0 -250 94 {}
N -190 -70 -190 -60 {}
N -190 -60 -190 -30 {}
N -190 30 -190 140 {}
N -150 -70 -150 0 {}
N 120 0 120 60 {}
N 190 -60 190 -30 {}
N 190 30 190 140 {}
N 250 0 250 94 {}
N 460 0 460 60 {}
N 530 -60 530 -30 {}
N 530 30 530 140 {}
N 590 0 590 94 {}
N -190 -70 -150 -70 {}
N -460 -60 -150 -60 {}
N -590 0 -530 0 {}
N -490 0 -460 0 {}
N -250 0 -190 0 {}
N -150 0 180 0 {}
N 190 0 250 0 {}
N 460 0 490 0 {}
N 530 0 590 0 {}
N 120 60 460 60 {}
N -1130 140 1105 140 {}
C {devices/lab_wire.sym} -590 94 2 0 {name=l0 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 250 94 2 0 {name=l2 lab=vss}
C {devices/lab_wire.sym} 590 94 2 0 {name=l3 lab=vss}
C {devices/iopin.sym} -1130 140 0 0 {name=p0 lab=vss}
C {devices/opin.sym} -530 -60 0 0 {name=p1 lab=voutn}
C {devices/opin.sym} 460 0 0 0 {name=p2 lab=core__ref}
C {devices/opin.sym} 190 -60 0 0 {name=p3 lab=voutp}
C {devices/opin.sym} 530 -60 0 0 {name=p4 lab=core__tail}
