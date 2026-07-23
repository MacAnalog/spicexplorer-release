v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_pmos_cascode_1} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 260 0 0 0 {name=M10_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_opamp_rrl_w l=x_dut_xm10_opamp_rrl_l m=x_dut_xm10_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 530 0 0 0 {name=M2_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_opamp_rrl_w l=x_dut_xm2_opamp_rrl_l m=x_dut_xm2_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_opamp_rrl_w l=x_dut_xm3_opamp_rrl_l m=x_dut_xm3_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -80 0 0 1 {name=M9_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_opamp_rrl_w l=x_dut_xm9_opamp_rrl_l m=x_dut_xm9_opamp_rrl_m}
N -420 0 -420 94 {}
N -360 -90 -360 -30 {}
N -360 30 -360 90 {}
N -320 0 -320 60 {}
N -160 0 -160 94 {}
N -100 -90 -100 -30 {}
N -100 30 -100 90 {}
N 280 -90 280 -30 {}
N 280 30 280 90 {}
N 340 0 340 94 {}
N 510 -60 510 0 {}
N 550 -90 550 -30 {}
N 550 30 550 90 {}
N 610 0 610 94 {}
N -420 0 -360 0 {}
N -320 0 -290 0 {}
N -160 0 -100 0 {}
N -60 0 240 0 {}
N 280 0 340 0 {}
N 480 0 510 0 {}
N 550 0 610 0 {}
C {devices/lab_wire.sym} -100 -90 0 1 {name=l0 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} 550 90 2 0 {name=l1 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} -360 90 2 0 {name=l2 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} 280 -90 0 1 {name=l3 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} -320 60 2 0 {name=l4 lab=rrl__oa_inn}
C {devices/lab_wire.sym} 510 -60 0 1 {name=l5 lab=rrl__oa_inp}
C {devices/lab_wire.sym} -100 90 2 0 {name=l6 lab=rrl__oa_outn}
C {devices/lab_wire.sym} 280 90 2 0 {name=l7 lab=rrl__oa_outp}
C {devices/lab_wire.sym} -360 -90 0 1 {name=l8 lab=rrl__oa_tail}
C {devices/lab_wire.sym} 550 -90 0 1 {name=l9 lab=rrl__oa_tail}
C {devices/lab_wire.sym} 0 0 0 1 {name=l10 lab=rrl__vb1}
C {devices/lab_wire.sym} 340 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} 610 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} -160 94 2 0 {name=l14 lab=vdd}
C {devices/ipin.sym} -770 0 0 0 {name=p0 lab=rrl__oa_inn}
C {devices/ipin.sym} -770 120 0 0 {name=p1 lab=rrl__vb1}
C {devices/ipin.sym} -770 240 0 0 {name=p2 lab=rrl__oa_inp}
C {devices/iopin.sym} -360 280 0 0 {name=p3 lab=rrl__oa_tail}
C {devices/opin.sym} 960 30 0 0 {name=p4 lab=rrl__oa_outn}
C {devices/opin.sym} 960 150 0 0 {name=p5 lab=rrl__oa_outp}
