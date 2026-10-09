v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {smp_001_nmos_th} -40 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 0 0 0 0 {name=C0 value=x_dut_c0_value}
C {devices/sg13_lv_nmos_np.sym} 225 0 0 0 {name=M0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
N -60 -60 -60 60 {}
N 0 -60 0 -30 {}
N 0 30 0 140 {}
N 245 -60 245 -30 {}
N 245 30 245 60 {}
N 305 0 305 94 {}
N -60 -60 0 -60 {}
N 115 0 205 0 {}
N 245 0 305 0 {}
N -60 60 245 60 {}
N -60 140 700 140 {}
C {devices/lab_wire.sym} 305 94 2 0 {name=l0 lab=vss}
C {devices/ipin.sym} 115 0 0 0 {name=p0 lab=clk}
C {devices/iopin.sym} -60 60 0 0 {name=p1 lab=vout}
C {devices/iopin.sym} -60 140 0 0 {name=p2 lab=vss}
C {devices/opin.sym} 245 -60 0 0 {name=p3 lab=vin}
