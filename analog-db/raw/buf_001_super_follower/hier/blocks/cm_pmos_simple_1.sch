v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=MPB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpb_w l=x_dut_xmpb_l m=x_dut_xmpb_m}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=MPD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpd_w l=x_dut_xmpd_l m=x_dut_xmpd_m}
N -250 0 -250 94 {}
N -190 -140 -190 -30 {}
N -190 30 -190 60 {}
N 150 0 150 70 {}
N 190 -140 190 -30 {}
N 190 30 190 70 {}
N 250 0 250 94 {}
N -670 -140 670 -140 {}
N -250 0 -190 0 {}
N -180 0 150 0 {}
N 190 0 250 0 {}
N 150 70 190 70 {}
C {devices/lab_wire.sym} -250 94 2 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l1 lab=vdd}
C {devices/iopin.sym} -670 -140 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 190 60 0 0 {name=p1 lab=pd}
C {devices/opin.sym} -190 60 0 0 {name=p2 lab=na}
