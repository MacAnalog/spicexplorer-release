v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_5} -360 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 190 0 0 0 {name=MB0B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb0_w/2\}" l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} 445 0 0 0 {name=MB1A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb1_w/2\}" l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} -70 0 0 0 {name=MB1B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xmb1_w/2\}" l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} 705 0 0 0 {name=MSA model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xms_w/2\}" l=x_dut_xms_l}
C {devices/sg13_lv_nmos_np.sym} -320 0 0 0 {name=MSB model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xms_w/2\}" l=x_dut_xms_l}
N -370 0 -370 60 {}
N -300 -60 -300 -30 {}
N -300 30 -300 140 {}
N -240 0 -240 94 {}
N -120 0 -120 60 {}
N -50 -90 -50 -30 {}
N -50 30 -50 140 {}
N 10 0 10 94 {}
N 170 -70 170 0 {}
N 210 -90 210 -30 {}
N 210 30 210 140 {}
N 270 0 270 94 {}
N 465 -90 465 -30 {}
N 465 30 465 140 {}
N 525 0 525 94 {}
N 725 -60 725 -30 {}
N 725 30 725 140 {}
N 785 0 785 94 {}
N 170 -70 210 -70 {}
N -360 -60 725 -60 {}
N -400 0 -340 0 {}
N -300 0 -240 0 {}
N -120 0 -90 0 {}
N -50 0 10 0 {}
N 210 0 270 0 {}
N 365 0 425 0 {}
N 465 0 525 0 {}
N 655 0 685 0 {}
N 725 0 785 0 {}
N -370 60 -120 60 {}
N -430 140 1135 140 {}
C {devices/lab_wire.sym} -400 0 0 0 {name=l0 lab=nbias}
C {devices/lab_wire.sym} 210 -90 0 1 {name=l1 lab=nbias}
C {devices/lab_wire.sym} 365 0 0 0 {name=l2 lab=nbias}
C {devices/lab_wire.sym} -50 -90 0 1 {name=l3 lab=pbias}
C {devices/lab_wire.sym} 465 -90 0 1 {name=l4 lab=pbias}
C {devices/lab_wire.sym} 270 94 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} 525 94 2 0 {name=l6 lab=vss}
C {devices/lab_wire.sym} 10 94 2 0 {name=l7 lab=vss}
C {devices/lab_wire.sym} 785 94 2 0 {name=l8 lab=vss}
C {devices/lab_wire.sym} -240 94 2 0 {name=l9 lab=vss}
C {devices/iopin.sym} -430 140 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 725 -60 0 0 {name=p1 lab=gate}
C {devices/opin.sym} 655 0 0 0 {name=p2 lab=nbias}
C {devices/opin.sym} 1275 -30 0 0 {name=p3 lab=pbias}
