v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_pmos_cascode_1} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 230 0 0 0 {name=M10_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_opamp_w l=x_dut_xm10_opamp_l m=x_dut_xm10_opamp_m}
C {devices/sg13_lv_pmos_np.sym} 465 0 0 0 {name=M2_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_opamp_w l=x_dut_xm2_opamp_l m=x_dut_xm2_opamp_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_opamp_w l=x_dut_xm3_opamp_l m=x_dut_xm3_opamp_m}
C {devices/sg13_lv_pmos_np.sym} -110 0 0 1 {name=M9_OPAMP model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_opamp_w l=x_dut_xm9_opamp_l m=x_dut_xm9_opamp_m}
N -420 0 -420 94 {}
N -360 -90 -360 -30 {}
N -360 30 -360 90 {}
N -320 0 -320 60 {}
N -190 0 -190 94 {}
N -130 -90 -130 -30 {}
N -130 30 -130 90 {}
N 250 -90 250 -30 {}
N 250 30 250 90 {}
N 310 0 310 94 {}
N 445 -60 445 0 {}
N 485 -90 485 -30 {}
N 485 30 485 90 {}
N 545 0 545 94 {}
N -420 0 -360 0 {}
N -320 0 -290 0 {}
N -190 0 -130 0 {}
N -90 0 210 0 {}
N 250 0 310 0 {}
N 415 0 445 0 {}
N 485 0 545 0 {}
C {devices/lab_wire.sym} -130 -90 0 1 {name=l0 lab=oa_d1n}
C {devices/lab_wire.sym} 485 90 2 0 {name=l1 lab=oa_d1n}
C {devices/lab_wire.sym} -360 90 2 0 {name=l2 lab=oa_d1p}
C {devices/lab_wire.sym} 250 -90 0 1 {name=l3 lab=oa_d1p}
C {devices/lab_wire.sym} -320 60 2 0 {name=l4 lab=oa_inn}
C {devices/lab_wire.sym} 445 -60 0 1 {name=l5 lab=oa_inp}
C {devices/lab_wire.sym} -130 90 2 0 {name=l6 lab=oa_outn}
C {devices/lab_wire.sym} 250 90 2 0 {name=l7 lab=oa_outp}
C {devices/lab_wire.sym} -360 -90 0 1 {name=l8 lab=oa_tail}
C {devices/lab_wire.sym} 485 -90 0 1 {name=l9 lab=oa_tail}
C {devices/lab_wire.sym} -30 0 0 1 {name=l10 lab=vb1}
C {devices/lab_wire.sym} 310 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} 545 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} -190 94 2 0 {name=l14 lab=vdd}
C {devices/ipin.sym} -735 0 0 0 {name=p0 lab=oa_inn}
C {devices/ipin.sym} -735 120 0 0 {name=p1 lab=vb1}
C {devices/ipin.sym} -735 240 0 0 {name=p2 lab=oa_inp}
C {devices/iopin.sym} -360 280 0 0 {name=p3 lab=oa_tail}
C {devices/opin.sym} 860 30 0 0 {name=p4 lab=oa_outn}
C {devices/opin.sym} 860 150 0 0 {name=p5 lab=oa_outp}
