v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_improved_high_swing_cascode_1} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -340 0 0 1 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 370 0 0 0 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 30 0 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 555 0 0 0 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} -150 0 0 1 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
N -420 0 -420 94 {}
N -360 -90 -360 -30 {}
N -360 30 -360 90 {}
N -320 0 -320 60 {}
N -230 0 -230 94 {}
N -170 -90 -170 -30 {}
N -170 30 -170 90 {}
N -130 0 -130 60 {}
N 10 -70 10 0 {}
N 50 -90 50 -30 {}
N 50 30 50 90 {}
N 110 0 110 94 {}
N 390 -90 390 -30 {}
N 390 30 390 90 {}
N 450 0 450 94 {}
N 535 -60 535 0 {}
N 575 -90 575 -30 {}
N 575 30 575 90 {}
N 635 0 635 94 {}
N 10 -70 50 -70 {}
N -420 0 -360 0 {}
N -320 0 -290 0 {}
N -230 0 -170 0 {}
N -130 0 -100 0 {}
N 50 0 110 0 {}
N 290 0 350 0 {}
N 390 0 450 0 {}
N 505 0 535 0 {}
N 575 0 635 0 {}
C {devices/lab_wire.sym} 390 -90 0 1 {name=l0 lab=DM_1}
C {devices/lab_wire.sym} -320 60 2 0 {name=l1 lab=VB3}
C {devices/lab_wire.sym} 50 -90 0 1 {name=l2 lab=VB3}
C {devices/lab_wire.sym} 290 0 0 0 {name=l3 lab=VB3}
C {devices/lab_wire.sym} -360 -90 0 1 {name=l4 lab=VB4}
C {devices/lab_wire.sym} -130 60 2 0 {name=l5 lab=VB4}
C {devices/lab_wire.sym} 535 -60 0 1 {name=l6 lab=VB4}
C {devices/lab_wire.sym} -360 90 2 0 {name=l7 lab=net54}
C {devices/lab_wire.sym} 575 -90 0 1 {name=l8 lab=net54}
C {devices/lab_wire.sym} -170 -90 0 1 {name=l9 lab=net56}
C {devices/lab_wire.sym} 390 90 2 0 {name=l10 lab=net56}
C {devices/lab_wire.sym} -170 90 2 0 {name=l11 lab=vss}
C {devices/lab_wire.sym} 50 90 2 0 {name=l12 lab=vss}
C {devices/lab_wire.sym} 575 90 2 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} -420 94 2 0 {name=l14 lab=vss}
C {devices/lab_wire.sym} 450 94 2 0 {name=l15 lab=vss}
C {devices/lab_wire.sym} 110 94 2 0 {name=l16 lab=vss}
C {devices/lab_wire.sym} 635 94 2 0 {name=l17 lab=vss}
C {devices/lab_wire.sym} -230 94 2 0 {name=l18 lab=vss}
C {devices/iopin.sym} -170 280 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 910 -30 0 0 {name=p1 lab=VB4}
C {devices/opin.sym} 910 90 0 0 {name=p2 lab=VB3}
C {devices/opin.sym} 910 210 0 0 {name=p3 lab=DM_1}
