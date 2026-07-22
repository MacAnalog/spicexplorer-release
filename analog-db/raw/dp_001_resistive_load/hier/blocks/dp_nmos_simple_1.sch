v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_nmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=MN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmn_w l=x_dut_xmn_l m=x_dut_xmn_m}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=MP model=sg13_lv_nmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 190 -90 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N -250 0 -190 0 {}
N -150 0 -90 0 {}
N 90 0 150 0 {}
N 190 0 250 0 {}
N -190 60 190 60 {}
C {devices/lab_wire.sym} -190 90 2 0 {name=l0 lab=tail}
C {devices/lab_wire.sym} 90 0 0 0 {name=l1 lab=vinn}
C {devices/lab_wire.sym} -90 0 0 1 {name=l2 lab=vinp}
C {devices/lab_wire.sym} 190 -90 0 1 {name=l3 lab=voutn}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l4 lab=voutp}
C {devices/lab_wire.sym} 250 94 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l6 lab=vss}
C {devices/ipin.sym} -520 0 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} -520 120 0 0 {name=p1 lab=vinn}
C {devices/iopin.sym} -190 280 0 0 {name=p2 lab=tail}
C {devices/opin.sym} 520 -30 0 0 {name=p3 lab=voutp}
C {devices/opin.sym} 520 90 0 0 {name=p4 lab=voutn}
