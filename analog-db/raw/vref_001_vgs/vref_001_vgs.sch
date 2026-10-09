v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {vref_001_vgs} -40 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 0 0 0 0 {name=M0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 0 {name=M1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
N -110 0 -110 60 {}
N -20 190 -20 260 {}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 400 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N -110 -140 475 -140 {}
N -110 0 -20 0 {}
N 20 0 80 0 {}
N -110 60 20 60 {}
N -20 190 20 190 {}
N 20 260 80 260 {}
N -110 400 475 400 {}
C {devices/lab_wire.sym} 80 94 2 0 {name=l0 lab=vss}
C {devices/lab_wire.sym} 80 354 2 0 {name=l1 lab=vss}
C {devices/iopin.sym} -110 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -110 400 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 20 60 0 0 {name=p2 lab=vref}
