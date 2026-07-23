v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {smp_001_nmos_th} -40 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 0 0 0 0 {name=C0 value=x_dut_c0_value}
C {devices/sg13_lv_nmos_np.sym} 190 0 0 0 {name=M0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
N 0 -90 0 -30 {}
N 0 30 0 140 {}
N 170 -60 170 0 {}
N 210 -90 210 -30 {}
N 210 30 210 90 {}
N 270 0 270 94 {}
N 140 0 170 0 {}
N 210 0 270 0 {}
N -60 140 400 140 {}
C {devices/lab_wire.sym} -60 140 0 0 {name=l0 lab=vss}
C {devices/lab_wire.sym} 170 -60 0 1 {name=l1 lab=clk}
C {devices/lab_wire.sym} 210 -90 0 1 {name=l2 lab=vin}
C {devices/lab_wire.sym} 0 -90 0 1 {name=l3 lab=vout}
C {devices/lab_wire.sym} 210 90 2 0 {name=l4 lab=vout}
C {devices/lab_wire.sym} 270 94 2 0 {name=l5 lab=vss}
C {devices/ipin.sym} -200 0 0 0 {name=p0 lab=clk}
C {devices/iopin.sym} 0 280 0 0 {name=p1 lab=vout}
C {devices/opin.sym} 540 -30 0 0 {name=p2 lab=vin}
