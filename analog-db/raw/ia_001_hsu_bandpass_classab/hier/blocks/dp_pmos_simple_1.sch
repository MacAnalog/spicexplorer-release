v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_pmos_simple_1} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=MO2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo2_w l=x_dut_xmo2_l m=x_dut_xmo2_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=MO3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmo3_w l=x_dut_xmo3_l m=x_dut_xmo3_m}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 190 -60 190 -30 {}
N 190 30 190 90 {}
N 250 0 250 94 {}
N -190 -60 190 -60 {}
N -250 0 -190 0 {}
N -150 0 -90 0 {}
N 90 0 150 0 {}
N 190 0 250 0 {}
C {devices/lab_wire.sym} -190 90 2 0 {name=l0 lab=dio_n}
C {devices/lab_wire.sym} 190 90 2 0 {name=l1 lab=dio_p}
C {devices/lab_wire.sym} -90 0 0 1 {name=l2 lab=sum_n}
C {devices/lab_wire.sym} 90 0 0 0 {name=l3 lab=sum_p}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l4 lab=tail}
C {devices/lab_wire.sym} 250 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l6 lab=vdd}
C {devices/ipin.sym} -525 0 0 0 {name=p0 lab=sum_n}
C {devices/ipin.sym} -525 120 0 0 {name=p1 lab=sum_p}
C {devices/iopin.sym} -190 280 0 0 {name=p2 lab=tail}
C {devices/opin.sym} 525 30 0 0 {name=p3 lab=dio_n}
C {devices/opin.sym} 525 150 0 0 {name=p4 lab=dio_p}
