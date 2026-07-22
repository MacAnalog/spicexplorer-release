v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {tsn_001_ptat_2t} -40 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 0 0 0 0 {name=M0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
N -20 190 -20 260 {}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 400 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N -110 -140 210 -140 {}
N -80 0 -20 0 {}
N 20 0 80 0 {}
N -20 190 20 190 {}
N 20 260 80 260 {}
N -110 400 210 400 {}
C {devices/lab_wire.sym} -110 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -110 400 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -80 0 0 0 {name=l2 lab=vout}
C {devices/lab_wire.sym} 20 90 2 0 {name=l3 lab=vout}
C {devices/lab_wire.sym} 80 94 2 0 {name=l4 lab=vss}
C {devices/lab_wire.sym} 80 354 2 0 {name=l5 lab=vss}
C {devices/opin.sym} 350 0 0 0 {name=p0 lab=vout}
