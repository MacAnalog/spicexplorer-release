v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_006_stub} -150 -500 0 0 0.4 0.4 {}
C {devices/res_np.sym} 0 -300 0 0 {name=R1 value=r_top}
C {devices/res_np.sym} -110 300 0 0 {name=R2 value=r_bot}
C {devices/sg13_lv_nmos_np.sym} 110 300 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
N 0 -330 0 -370 {}
C {devices/lab_wire.sym} 0 -370 0 1 {name=l0 lab=vdd}
N 0 -270 0 -230 {}
C {devices/lab_wire.sym} 0 -230 2 0 {name=l1 lab=vref}
N -110 270 -110 230 {}
C {devices/lab_wire.sym} -110 230 0 1 {name=l2 lab=vref}
N -110 330 -110 370 {}
C {devices/lab_wire.sym} -110 370 2 0 {name=l3 lab=vss}
N 130 270 130 230 {}
C {devices/lab_wire.sym} 130 230 0 1 {name=l4 lab=vdd}
N 90 300 50 300 {}
C {devices/lab_wire.sym} 50 300 0 0 {name=l5 lab=vref}
N 130 330 130 370 {}
C {devices/lab_wire.sym} 130 370 2 0 {name=l6 lab=vout}
N 130 300 170 300 {}
C {devices/lab_wire.sym} 170 300 0 1 {name=l7 lab=vss}
