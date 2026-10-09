v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_improved_high_swing_cascode_1} -720 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -680 0 0 1 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 0 0 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 1 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 680 260 0 0 {name=M64 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm64_w l=x_dut_xm64_l m=x_dut_xm64_m}
C {devices/sg13_lv_nmos_np.sym} 340 260 0 0 {name=M65 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm65_w l=x_dut_xm65_l m=x_dut_xm65_m}
C {devices/sg13_lv_nmos_np.sym} 340 0 0 0 {name=M70 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm70_w l=x_dut_xm70_l m=x_dut_xm70_m}
C {devices/sg13_lv_nmos_np.sym} 680 0 0 0 {name=M71 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm71_w l=x_dut_xm71_l m=x_dut_xm71_m}
N -760 0 -760 94 {}
N -760 260 -760 354 {}
N -700 -90 -700 -30 {}
N -700 30 -700 230 {}
N -700 290 -700 400 {}
N -420 260 -420 354 {}
N -360 -120 -360 230 {}
N -360 290 -360 400 {}
N -320 190 -320 260 {}
N -80 0 -80 94 {}
N -80 260 -80 354 {}
N -20 -60 -20 -30 {}
N -20 30 -20 230 {}
N -20 290 -20 400 {}
N 50 -120 50 0 {}
N 290 -120 290 0 {}
N 290 260 290 320 {}
N 360 -60 360 -30 {}
N 360 30 360 230 {}
N 360 290 360 400 {}
N 420 0 420 94 {}
N 420 260 420 354 {}
N 630 -120 630 0 {}
N 630 260 630 320 {}
N 700 -60 700 -30 {}
N 700 30 700 230 {}
N 700 290 700 400 {}
N 760 0 760 94 {}
N 760 260 760 354 {}
N -360 -120 50 -120 {}
N 290 -120 630 -120 {}
N -760 0 -700 0 {}
N -660 0 -600 0 {}
N -80 0 -20 0 {}
N 20 0 320 0 {}
N 360 0 420 0 {}
N 630 0 660 0 {}
N 700 0 760 0 {}
N -360 190 -320 190 {}
N -760 260 -700 260 {}
N -660 260 -570 260 {}
N -420 260 -360 260 {}
N -80 260 -20 260 {}
N 20 260 320 260 {}
N 360 260 420 260 {}
N 630 260 660 260 {}
N 700 260 760 260 {}
N 290 320 630 320 {}
N -1180 400 1180 400 {}
C {devices/lab_wire.sym} -600 0 0 1 {name=l0 lab=VB3}
C {devices/lab_wire.sym} -700 -90 0 1 {name=l1 lab=VB4}
C {devices/lab_wire.sym} 80 260 0 1 {name=l2 lab=VB4}
C {devices/lab_wire.sym} -700 90 2 0 {name=l3 lab=net54}
C {devices/lab_wire.sym} -20 90 2 0 {name=l4 lab=net56}
C {devices/lab_wire.sym} 360 90 2 0 {name=l5 lab=net69}
C {devices/lab_wire.sym} 700 90 2 0 {name=l6 lab=net85}
C {devices/lab_wire.sym} -760 94 2 0 {name=l7 lab=vss}
C {devices/lab_wire.sym} -80 94 2 0 {name=l8 lab=vss}
C {devices/lab_wire.sym} -420 354 2 0 {name=l9 lab=vss}
C {devices/lab_wire.sym} -760 354 2 0 {name=l10 lab=vss}
C {devices/lab_wire.sym} -80 354 2 0 {name=l11 lab=vss}
C {devices/lab_wire.sym} 760 354 2 0 {name=l12 lab=vss}
C {devices/lab_wire.sym} 420 354 2 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} 420 94 2 0 {name=l14 lab=vss}
C {devices/lab_wire.sym} 760 94 2 0 {name=l15 lab=vss}
C {devices/iopin.sym} -1180 400 0 0 {name=p0 lab=vss}
C {devices/opin.sym} -570 260 0 0 {name=p1 lab=VB4}
C {devices/opin.sym} -20 -60 0 0 {name=p2 lab=DM_1}
C {devices/opin.sym} 360 -60 0 0 {name=p3 lab=net70}
C {devices/opin.sym} 700 -60 0 0 {name=p4 lab=VOUTN}
C {devices/opin.sym} 630 -120 0 0 {name=p5 lab=VB3}
