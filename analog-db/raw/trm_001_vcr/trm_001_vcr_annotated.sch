v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {trm_001_vcr} -40 -200 0 0 0.4 0.4 {}
C {devices/res_np.sym} 0 0 0 0 {name=R0 value=x_dut_r0_value}
C {devices/sg13_lv_nmos_np.sym} 190 0 0 0 {name=M0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
N 0 -140 0 -30 {}
N 0 30 0 90 {}
N 170 -60 170 0 {}
N 210 -90 210 -30 {}
N 210 30 210 90 {}
N 270 0 270 94 {}
N -60 -140 400 -140 {}
N 140 0 170 0 {}
N 210 0 270 0 {}
N -60 140 400 140 {}
C {devices/lab_wire.sym} -60 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -60 140 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 170 -60 0 1 {name=l2 lab=vcode}
C {devices/lab_wire.sym} 0 90 2 0 {name=l3 lab=vout}
C {devices/lab_wire.sym} 210 -90 0 1 {name=l4 lab=vout}
C {devices/lab_wire.sym} 270 94 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} 210 90 2 0 {name=l6 lab=vss}
C {devices/ipin.sym} -200 0 0 0 {name=p0 lab=vcode}
C {devices/opin.sym} 540 -30 0 0 {name=p1 lab=vout}
