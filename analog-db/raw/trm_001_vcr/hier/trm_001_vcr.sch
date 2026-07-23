v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {trm_001_vcr} -40 -500 0 0 0.4 0.4 {}
C {devices/res_np.sym} 0 -300 0 0 {name=R0 value=x_dut_r0_value}
C {devices/sg13_lv_nmos_np.sym} 0 300 0 0 {name=M0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
N 0 -330 0 -370 {}
C {devices/lab_wire.sym} 0 -370 0 1 {name=l0 lab=vdd}
N 0 -270 0 -230 {}
C {devices/lab_wire.sym} 0 -230 2 0 {name=l1 lab=vout}
N 20 270 20 230 {}
C {devices/lab_wire.sym} 20 230 0 1 {name=l2 lab=vout}
N -20 300 -60 300 {}
C {devices/lab_wire.sym} -60 300 0 0 {name=l3 lab=vcode}
N 20 330 20 370 {}
C {devices/lab_wire.sym} 20 370 2 0 {name=l4 lab=vss}
N 20 300 60 300 {}
C {devices/lab_wire.sym} 60 300 0 1 {name=l5 lab=vss}
