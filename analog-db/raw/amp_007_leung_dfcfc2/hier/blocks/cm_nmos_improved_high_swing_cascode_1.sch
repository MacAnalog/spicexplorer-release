v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_improved_high_swing_cascode_1} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 0 0 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 340 0 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 1 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 340 260 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
N -420 260 -420 354 {}
N -360 190 -360 230 {}
N -360 290 -360 400 {}
N -320 190 -320 260 {}
N -80 60 -80 230 {}
N -80 260 -80 354 {}
N -20 -60 -20 -30 {}
N -20 30 -20 90 {}
N -20 290 -20 400 {}
N 80 0 80 200 {}
N 110 -60 110 260 {}
N 360 -60 360 -30 {}
N 360 30 360 230 {}
N 360 290 360 400 {}
N 420 0 420 94 {}
N 420 260 420 354 {}
N -20 -60 110 -60 {}
N 20 0 350 0 {}
N 360 0 420 0 {}
N -80 60 -20 60 {}
N -360 190 -320 190 {}
N -360 200 80 200 {}
N -80 230 -20 230 {}
N -420 260 -360 260 {}
N -80 260 -20 260 {}
N 20 260 320 260 {}
N 360 260 420 260 {}
N -840 400 840 400 {}
C {devices/lab_wire.sym} -20 90 2 0 {name=l0 lab=net54}
C {devices/lab_wire.sym} 360 90 2 0 {name=l1 lab=net56}
C {devices/lab_wire.sym} -20 0 0 0 {name=l2 lab=vss}
C {devices/lab_wire.sym} 420 94 2 0 {name=l3 lab=vss}
C {devices/lab_wire.sym} -420 354 2 0 {name=l4 lab=vss}
C {devices/lab_wire.sym} -80 354 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} 420 354 2 0 {name=l6 lab=vss}
C {devices/iopin.sym} -840 400 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 290 260 0 0 {name=p1 lab=VB4}
C {devices/opin.sym} 360 -60 0 0 {name=p2 lab=DM_1}
C {devices/opin.sym} 350 0 0 0 {name=p3 lab=VB3}
