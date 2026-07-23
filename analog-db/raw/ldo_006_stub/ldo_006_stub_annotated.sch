v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_006_stub} -40 -200 0 0 0.4 0.4 {}
C {devices/res_np.sym} 0 0 0 0 {name=R1 value=r_top}
C {devices/res_np.sym} 0 130 0 0 {name=R2 value=r_bot}
C {devices/sg13_lv_nmos_np.sym} 160 0 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
N 0 -140 0 -30 {}
N 0 30 0 100 {}
N 0 160 0 270 {}
N 110 0 110 60 {}
N 140 -60 140 0 {}
N 180 -140 180 -30 {}
N 180 30 180 90 {}
N 240 0 240 94 {}
N -60 -140 370 -140 {}
N 110 0 140 0 {}
N 180 0 240 0 {}
N 0 60 110 60 {}
N -60 270 370 270 {}
C {devices/lab_wire.sym} -60 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -60 270 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 180 90 2 0 {name=l2 lab=vout}
C {devices/lab_wire.sym} 140 -60 0 1 {name=l3 lab=vref}
C {devices/lab_wire.sym} 240 94 2 0 {name=l4 lab=vss}
C {devices/iopin.sym} 180 410 0 0 {name=p0 lab=vout}
