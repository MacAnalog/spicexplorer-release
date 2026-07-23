v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_001_resistive_load} -200 -200 0 0 0.4 0.4 {}
C {devices/res_np.sym} 20 0 0 0 {name=RN value=x_dut_rn_value}
C {devices/res_np.sym} 210 0 0 0 {name=RP value=x_dut_rp_value}
C {devices/sg13_lv_nmos_np.sym} -160 0 0 0 {name=MN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmn_w l=x_dut_xmn_l m=x_dut_xmn_m}
C {devices/sg13_lv_nmos_np.sym} 395 0 0 0 {name=MP model=sg13_lv_nmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
C {devices/sg13_lv_nmos_np.sym} 20 260 0 0 {name=MR model=sg13_lv_nmos spiceprefix=X w=x_dut_xmr_w l=x_dut_xmr_l m=x_dut_xmr_m}
C {devices/sg13_lv_nmos_np.sym} 210 260 0 0 {name=MT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmt_w l=x_dut_xmt_l m=x_dut_xmt_m}
N -140 -90 -140 -30 {}
N -140 30 -140 90 {}
N -80 0 -80 94 {}
N 0 190 0 260 {}
N 20 -90 20 -30 {}
N 20 30 20 90 {}
N 40 170 40 230 {}
N 40 290 40 400 {}
N 100 260 100 354 {}
N 160 200 160 260 {}
N 210 -140 210 -30 {}
N 210 30 210 90 {}
N 230 170 230 230 {}
N 230 290 230 400 {}
N 290 260 290 354 {}
N 375 -60 375 0 {}
N 415 -90 415 -30 {}
N 415 30 415 90 {}
N 475 0 475 94 {}
N -270 -140 605 -140 {}
N -240 0 -180 0 {}
N -140 0 -80 0 {}
N 345 0 375 0 {}
N 415 0 475 0 {}
N 0 190 40 190 {}
N 40 200 160 200 {}
N 40 260 100 260 {}
N 160 260 190 260 {}
N 230 260 290 260 {}
N -270 400 605 400 {}
C {devices/lab_wire.sym} -270 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -270 400 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 40 170 0 1 {name=l2 lab=ibias}
C {devices/lab_wire.sym} -140 90 2 0 {name=l3 lab=tail}
C {devices/lab_wire.sym} 230 170 0 1 {name=l4 lab=tail}
C {devices/lab_wire.sym} 415 90 2 0 {name=l5 lab=tail}
C {devices/lab_wire.sym} -240 0 0 0 {name=l6 lab=vinn}
C {devices/lab_wire.sym} 375 -60 0 1 {name=l7 lab=vinp}
C {devices/lab_wire.sym} -140 -90 0 1 {name=l8 lab=voutn}
C {devices/lab_wire.sym} 20 90 2 0 {name=l9 lab=voutn}
C {devices/lab_wire.sym} 210 90 2 0 {name=l10 lab=voutp}
C {devices/lab_wire.sym} 415 -90 0 1 {name=l11 lab=voutp}
C {devices/lab_wire.sym} -80 94 2 0 {name=l12 lab=vss}
C {devices/lab_wire.sym} 475 94 2 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} 100 354 2 0 {name=l14 lab=vss}
C {devices/lab_wire.sym} 290 354 2 0 {name=l15 lab=vss}
C {devices/lab_wire.sym} 20 -90 0 1 {name=l16 lab=vdd}
C {devices/ipin.sym} -410 0 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -410 120 0 0 {name=p1 lab=vinp}
C {devices/opin.sym} 745 -30 0 0 {name=p2 lab=voutn}
C {devices/opin.sym} 745 90 0 0 {name=p3 lab=voutp}
C {devices/opin.sym} 745 230 0 0 {name=p4 lab=ibias}
B 8 -50 182 398 338 {fill=0}
T {NMOS Simple Current Mirror} -50 164 0 0 0.3 0.3 {layer=8}
B 10 -230 -78 583 78 {fill=0}
T {NMOS Differential Pair} -230 -96 0 0 0.3 0.3 {layer=10}
