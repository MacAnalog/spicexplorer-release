v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {buf_001_super_follower} -380 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -180 520 0 0 {name=CC value=x_cc}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 1 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 0 {name=MNS model=sg13_lv_nmos spiceprefix=X w=x_dut_xmns_w l=x_dut_xmns_l m=x_dut_xmns_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=MPB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpb_w l=x_dut_xmpb_l m=x_dut_xmpb_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=MPD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpd_w l=x_dut_xmpd_l m=x_dut_xmpd_m}
C {devices/sg13_lv_nmos_np.sym} 340 520 0 0 {name=MRN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmrn_w l=x_dut_xmrn_l m=x_dut_xmrn_m}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -420 520 -420 614 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -360 290 -360 490 {}
N -360 550 -360 660 {}
N -180 430 -180 520 {}
N -180 550 -180 660 {}
N -20 0 -20 70 {}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 660 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 320 450 320 520 {}
N 360 260 360 490 {}
N 360 550 360 660 {}
N 420 520 420 614 {}
N -555 -140 555 -140 {}
N -420 0 -360 0 {}
N -320 0 -260 0 {}
N -80 0 -20 0 {}
N 20 0 80 0 {}
N -20 70 20 70 {}
N -360 200 -290 200 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N -80 260 -20 260 {}
N 20 260 80 260 {}
N 320 450 360 450 {}
N -420 520 -360 520 {}
N -320 520 -180 520 {}
N 360 520 420 520 {}
N -555 660 555 660 {}
C {devices/lab_wire.sym} -555 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -555 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -80 260 0 0 {name=l2 lab=ibias}
C {devices/lab_wire.sym} 360 430 0 1 {name=l3 lab=ibias}
C {devices/lab_wire.sym} -360 90 2 0 {name=l4 lab=na}
C {devices/lab_wire.sym} -180 430 0 1 {name=l5 lab=na}
C {devices/lab_wire.sym} -260 0 0 1 {name=l6 lab=pd}
C {devices/lab_wire.sym} -80 0 0 0 {name=l7 lab=pd}
C {devices/lab_wire.sym} -260 260 0 1 {name=l8 lab=vin}
C {devices/lab_wire.sym} -360 350 2 0 {name=l9 lab=vout}
C {devices/lab_wire.sym} -420 94 2 0 {name=l10 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} -420 354 2 0 {name=l12 lab=vss}
C {devices/lab_wire.sym} -420 614 2 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} 80 354 2 0 {name=l14 lab=vss}
C {devices/lab_wire.sym} 420 614 2 0 {name=l15 lab=vss}
C {devices/ipin.sym} -695 260 0 0 {name=p0 lab=vin}
C {devices/opin.sym} 695 260 0 0 {name=p1 lab=ibias}
C {devices/opin.sym} 695 380 0 0 {name=p2 lab=vout}
