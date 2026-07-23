v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {smp_001_nmos_th} -150 100 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -110 300 0 0 {name=C0 value=x_dut_c0_value}
C {devices/sg13_lv_nmos_np.sym} 110 300 0 0 {name=M0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
N -110 270 -110 230 {}
C {devices/lab_wire.sym} -110 230 0 1 {name=l0 lab=vout}
N -110 330 -110 370 {}
C {devices/lab_wire.sym} -110 370 2 0 {name=l1 lab=vss}
N 130 270 130 230 {}
C {devices/lab_wire.sym} 130 230 0 1 {name=l2 lab=vin}
N 90 300 50 300 {}
C {devices/lab_wire.sym} 50 300 0 0 {name=l3 lab=clk}
N 130 330 130 370 {}
C {devices/lab_wire.sym} 130 370 2 0 {name=l4 lab=vout}
N 130 300 170 300 {}
C {devices/lab_wire.sym} 170 300 0 1 {name=l5 lab=vss}
