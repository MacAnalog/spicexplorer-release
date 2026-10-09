v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_improved_high_swing_cascode_1} -550 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -510 0 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} -170 260 0 1 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} -510 260 0 1 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 170 260 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_nmos_np.sym} 510 0 0 0 {name=M60 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm60_w l=x_dut_xm60_l m=x_dut_xm60_m}
C {devices/sg13_lv_nmos_np.sym} 510 260 0 0 {name=M61 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm61_w l=x_dut_xm61_l m=x_dut_xm61_m}
N -590 0 -590 94 {}
N -590 260 -590 354 {}
N -530 -90 -530 -30 {}
N -530 30 -530 230 {}
N -530 290 -530 400 {}
N -250 0 -250 200 {}
N -250 260 -250 354 {}
N -190 190 -190 200 {}
N -190 200 -190 230 {}
N -190 290 -190 400 {}
N -150 190 -150 260 {}
N -130 0 -130 200 {}
N 120 -120 120 0 {}
N 120 260 120 320 {}
N 190 -60 190 -30 {}
N 190 30 190 230 {}
N 190 290 190 400 {}
N 250 0 250 94 {}
N 250 260 250 354 {}
N 460 -120 460 0 {}
N 460 260 460 320 {}
N 530 -60 530 -30 {}
N 530 30 530 230 {}
N 530 290 530 400 {}
N 590 0 590 94 {}
N 590 260 590 354 {}
N 120 -120 460 -120 {}
N -590 0 -530 0 {}
N -490 0 150 0 {}
N 190 0 250 0 {}
N 460 0 490 0 {}
N 530 0 590 0 {}
N -190 190 -150 190 {}
N -250 200 -130 200 {}
N -590 260 -530 260 {}
N -490 260 -400 260 {}
N -250 260 -190 260 {}
N 90 260 150 260 {}
N 190 260 250 260 {}
N 460 260 490 260 {}
N 530 260 590 260 {}
N 120 320 460 320 {}
N -1010 400 1010 400 {}
C {devices/lab_wire.sym} -530 -90 0 1 {name=l0 lab=VB4}
C {devices/lab_wire.sym} 90 260 0 0 {name=l1 lab=VB4}
C {devices/lab_wire.sym} 530 90 2 0 {name=l2 lab=net3}
C {devices/lab_wire.sym} -530 90 2 0 {name=l3 lab=net54}
C {devices/lab_wire.sym} 190 90 2 0 {name=l4 lab=net56}
C {devices/lab_wire.sym} -590 94 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} 250 94 2 0 {name=l6 lab=vss}
C {devices/lab_wire.sym} -250 354 2 0 {name=l7 lab=vss}
C {devices/lab_wire.sym} -590 354 2 0 {name=l8 lab=vss}
C {devices/lab_wire.sym} 250 354 2 0 {name=l9 lab=vss}
C {devices/lab_wire.sym} 590 94 2 0 {name=l10 lab=vss}
C {devices/lab_wire.sym} 590 354 2 0 {name=l11 lab=vss}
C {devices/iopin.sym} -1010 400 0 0 {name=p0 lab=vss}
C {devices/opin.sym} -400 260 0 0 {name=p1 lab=VB4}
C {devices/opin.sym} 190 -60 0 0 {name=p2 lab=DM_1}
C {devices/opin.sym} 530 -60 0 0 {name=p3 lab=net2}
C {devices/opin.sym} 460 -120 0 0 {name=p4 lab=VB3}
