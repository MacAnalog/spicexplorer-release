v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {vref_001_vgs} -150 100 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -110 300 0 0 {name=M0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_nmos_np.sym} 110 300 0 0 {name=M1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
N -90 270 -90 230 {}
C {devices/lab_wire.sym} -90 230 0 1 {name=l0 lab=vdd}
N -130 300 -170 300 {}
C {devices/lab_wire.sym} -170 300 0 0 {name=l1 lab=vref}
N -90 330 -90 370 {}
C {devices/lab_wire.sym} -90 370 2 0 {name=l2 lab=vref}
N -90 300 -50 300 {}
C {devices/lab_wire.sym} -50 300 0 1 {name=l3 lab=vss}
N 130 270 130 230 {}
C {devices/lab_wire.sym} 130 230 0 1 {name=l4 lab=vref}
N 90 300 50 300 {}
C {devices/lab_wire.sym} 50 300 0 0 {name=l5 lab=vref}
N 130 330 130 370 {}
C {devices/lab_wire.sym} 130 370 2 0 {name=l6 lab=vss}
N 130 300 170 300 {}
C {devices/lab_wire.sym} 170 300 0 1 {name=l7 lab=vss}
