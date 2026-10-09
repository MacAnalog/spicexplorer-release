v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_001_resistive_load} -200 -200 0 0 0.4 0.4 {}
C {devices/res_np.sym} 60 0 0 0 {name=RN value=x_dut_rn_value}
C {devices/res_np.sym} 285 0 0 0 {name=RP value=x_dut_rp_value}
C {devices/sg13_lv_nmos_np.sym} -160 0 0 0 {name=MN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmn_w l=x_dut_xmn_l m=x_dut_xmn_m}
C {devices/sg13_lv_nmos_np.sym} 510 0 0 0 {name=MP model=sg13_lv_nmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
C {devices/sg13_lv_nmos_np.sym} 60 260 0 0 {name=MR model=sg13_lv_nmos spiceprefix=X w=x_dut_xmr_w l=x_dut_xmr_l m=x_dut_xmr_m}
C {devices/sg13_lv_nmos_np.sym} 285 260 0 0 {name=MT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmt_w l=x_dut_xmt_l m=x_dut_xmt_m}
N -140 -60 -140 -30 {}
N -140 30 -140 90 {}
N -80 0 -80 94 {}
N 40 190 40 260 {}
N 60 -140 60 -30 {}
N 80 190 80 230 {}
N 80 290 80 400 {}
N 120 -60 120 30 {}
N 140 260 140 354 {}
N 235 200 235 260 {}
N 285 -140 285 -30 {}
N 285 30 285 90 {}
N 305 60 305 230 {}
N 305 290 305 400 {}
N 365 60 365 200 {}
N 365 260 365 354 {}
N 530 -60 530 -30 {}
N 530 30 530 60 {}
N 590 0 590 94 {}
N -270 -140 985 -140 {}
N -140 -60 120 -60 {}
N -270 0 -180 0 {}
N -140 0 -80 0 {}
N 400 0 490 0 {}
N 530 0 590 0 {}
N 60 30 120 30 {}
N -140 60 530 60 {}
N 40 190 80 190 {}
N 80 200 235 200 {}
N 305 200 365 200 {}
N 80 260 140 260 {}
N 235 260 265 260 {}
N 305 260 365 260 {}
N -270 400 985 400 {}
C {devices/lab_wire.sym} -140 90 2 0 {name=l0 lab=tail}
C {devices/lab_wire.sym} 285 90 2 0 {name=l1 lab=voutp}
C {devices/lab_wire.sym} -80 94 2 0 {name=l2 lab=vss}
C {devices/lab_wire.sym} 590 94 2 0 {name=l3 lab=vss}
C {devices/lab_wire.sym} 140 354 2 0 {name=l4 lab=vss}
C {devices/lab_wire.sym} 365 354 2 0 {name=l5 lab=vss}
C {devices/ipin.sym} -270 0 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} 400 0 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -270 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -270 400 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 120 -60 0 0 {name=p4 lab=voutn}
C {devices/opin.sym} 530 -60 0 0 {name=p5 lab=voutp}
C {devices/opin.sym} 235 200 0 0 {name=p6 lab=ibias}
