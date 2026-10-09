v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_2} -200 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 90 0 0 0 {name=M3B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {devices/sg13_lv_nmos_np.sym} 340 0 0 0 {name=M4A model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
C {devices/sg13_lv_nmos_np.sym} -160 0 0 0 {name=M4B model=sg13_lv_nmos spiceprefix=X w="\{x_dut_xm3_w/2\}" l=x_dut_xm3_l}
N -210 0 -210 60 {}
N -140 -60 -140 -30 {}
N -140 30 -140 140 {}
N -80 0 -80 94 {}
N 70 -70 70 60 {}
N 110 -90 110 -30 {}
N 110 30 110 140 {}
N 170 0 170 94 {}
N 360 -60 360 -30 {}
N 360 30 360 140 {}
N 420 0 420 94 {}
N 70 -70 110 -70 {}
N -200 -60 360 -60 {}
N -210 0 -180 0 {}
N -140 0 -80 0 {}
N 110 0 170 0 {}
N 290 0 320 0 {}
N 360 0 420 0 {}
N -210 60 70 60 {}
N -270 140 770 140 {}
C {devices/lab_wire.sym} 110 -90 0 1 {name=l0 lab=ea_n}
C {devices/lab_wire.sym} 170 94 2 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 420 94 2 0 {name=l2 lab=vss}
C {devices/lab_wire.sym} -80 94 2 0 {name=l3 lab=vss}
C {devices/iopin.sym} -270 140 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 360 -60 0 0 {name=p1 lab=ea_o1}
C {devices/opin.sym} 290 0 0 0 {name=p2 lab=ea_n}
