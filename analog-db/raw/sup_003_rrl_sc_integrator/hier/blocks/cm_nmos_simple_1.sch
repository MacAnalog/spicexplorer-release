v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 235 0 0 0 {name=M13_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_opamp_w l=x_dut_xm13_opamp_l m=x_dut_xm13_opamp_m}
C {devices/sg13_lv_nmos_np.sym} 0 0 0 0 {name=M14_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_opamp_w l=x_dut_xm14_opamp_l m=x_dut_xm14_opamp_m}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=M15_OPAMP model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_opamp_w l=x_dut_xm15_opamp_l m=x_dut_xm15_opamp_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N -150 -70 -150 0 {}
N -50 -60 -50 0 {}
N 20 -90 20 -30 {}
N 20 30 20 60 {}
N 80 0 80 94 {}
N 215 -60 215 0 {}
N 255 -90 255 -30 {}
N 255 30 255 60 {}
N 315 0 315 94 {}
N -190 -70 -150 -70 {}
N -190 -60 -50 -60 {}
N -250 0 -190 0 {}
N -50 0 -20 0 {}
N 20 0 80 0 {}
N 185 0 215 0 {}
N 255 0 315 0 {}
N -190 60 255 60 {}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l0 lab=oa_cm_bias}
C {devices/lab_wire.sym} 215 -60 0 1 {name=l1 lab=oa_cm_bias}
C {devices/lab_wire.sym} 255 -90 0 1 {name=l2 lab=oa_csrc_n}
C {devices/lab_wire.sym} 20 -90 0 1 {name=l3 lab=oa_csrc_p}
C {devices/lab_wire.sym} -190 90 2 0 {name=l4 lab=vss}
C {devices/lab_wire.sym} 315 94 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} 80 94 2 0 {name=l6 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l7 lab=vss}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 640 -30 0 0 {name=p1 lab=oa_cm_bias}
C {devices/opin.sym} 640 90 0 0 {name=p2 lab=oa_csrc_p}
C {devices/opin.sym} 640 210 0 0 {name=p3 lab=oa_csrc_n}
