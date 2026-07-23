v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {adc_001_inv1b} -40 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 0 {name=MN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmn_w l=x_dut_xmn_l m=x_dut_xmn_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -50 0 -50 260 {}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 400 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N -110 -140 210 -140 {}
N -80 0 -20 0 {}
N 20 0 80 0 {}
N -50 260 -20 260 {}
N 20 260 80 260 {}
N -110 400 210 400 {}
C {devices/lab_wire.sym} -110 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -110 400 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -80 0 0 0 {name=l2 lab=vin}
C {devices/lab_wire.sym} 20 90 2 0 {name=l3 lab=vout}
C {devices/lab_wire.sym} 80 94 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} 80 354 2 0 {name=l5 lab=vss}
C {devices/ipin.sym} -250 0 0 0 {name=p0 lab=vin}
C {devices/opin.sym} 350 30 0 0 {name=p1 lab=vout}
B 8 -70 -78 188 338 {fill=0}
T {COMPLEMENTARY Inverter (2 outputs)} -70 -96 0 0 0.3 0.3 {layer=8}
