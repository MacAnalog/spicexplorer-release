v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_pmos_cascode_1} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 265 0 0 0 {name=M10_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_opamp_w l=x_dut_xm10_opamp_l m=x_dut_xm10_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 540 0 0 0 {name=M2_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_opamp_w l=x_dut_xm2_opamp_l m=x_dut_xm2_opamp_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_opamp_w l=x_dut_xm3_opamp_l m=x_dut_xm3_opamp_m}
C {devices/sg13_lv_pmos_np.sym} -75 0 0 1 {name=M9_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_opamp_w l=x_dut_xm9_opamp_l m=x_dut_xm9_opamp_m}
N -420 0 -420 94 {}
N -360 -60 -360 -30 {}
N -360 30 -360 90 {}
N -155 0 -155 94 {}
N -95 -90 -95 -30 {}
N -95 30 -95 60 {}
N 285 -90 285 -30 {}
N 285 30 285 60 {}
N 345 0 345 94 {}
N 560 -60 560 -30 {}
N 560 30 560 90 {}
N 620 0 620 94 {}
N -960 -140 1160 -140 {}
N -420 -60 560 -60 {}
N -420 0 -360 0 {}
N -320 0 -290 0 {}
N -155 0 -95 0 {}
N -55 0 245 0 {}
N 285 0 345 0 {}
N 430 0 520 0 {}
N 560 0 620 0 {}
C {devices/lab_wire.sym} -960 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -95 -90 0 1 {name=l1 lab=oa_d1n}
C {devices/lab_wire.sym} 560 90 2 0 {name=l2 lab=oa_d1n}
C {devices/lab_wire.sym} -360 90 2 0 {name=l3 lab=oa_d1p}
C {devices/lab_wire.sym} 285 -90 0 1 {name=l4 lab=oa_d1p}
C {devices/lab_wire.sym} 345 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} 620 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} -155 94 2 0 {name=l8 lab=vdd}
C {devices/ipin.sym} -290 0 0 0 {name=p0 lab=oa_inn}
C {devices/ipin.sym} -25 0 0 0 {name=p1 lab=vb1}
C {devices/ipin.sym} 430 0 0 0 {name=p2 lab=oa_inp}
C {devices/iopin.sym} -420 -60 0 0 {name=p3 lab=oa_tail}
C {devices/opin.sym} -95 60 0 0 {name=p4 lab=oa_outn}
C {devices/opin.sym} 285 60 0 0 {name=p5 lab=oa_outp}
