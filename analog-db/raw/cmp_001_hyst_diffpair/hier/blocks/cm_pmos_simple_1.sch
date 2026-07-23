v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=MPLD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpld_w l=x_dut_xmpld_l m=x_dut_xmpld_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=MPLM model=sg13_lv_pmos spiceprefix=X w=x_dut_xmplm_w l=x_dut_xmplm_l m=x_dut_xmplm_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 150 0 150 70 {}
N 190 -60 190 -30 {}
N 190 30 190 70 {}
N 250 0 250 94 {}
N -190 -60 190 -60 {}
N -250 0 -190 0 {}
N -150 0 -90 0 {}
N 90 0 150 0 {}
N 190 0 250 0 {}
N 150 70 190 70 {}
C {devices/lab_wire.sym} -190 90 2 0 {name=l0 lab=n1}
C {devices/lab_wire.sym} -90 0 0 1 {name=l1 lab=n2}
C {devices/lab_wire.sym} 90 0 0 0 {name=l2 lab=n2}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l3 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l5 lab=vdd}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 535 0 0 0 {name=p1 lab=n2}
C {devices/opin.sym} 535 120 0 0 {name=p2 lab=n1}
