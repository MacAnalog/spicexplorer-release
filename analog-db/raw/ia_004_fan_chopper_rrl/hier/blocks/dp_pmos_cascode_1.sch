v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_pmos_cascode_1} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 300 0 0 0 {name=M10_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_opamp_rrl_w l=x_dut_xm10_opamp_rrl_l m=x_dut_xm10_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} 605 0 0 0 {name=M2_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_opamp_rrl_w l=x_dut_xm2_opamp_rrl_l m=x_dut_xm2_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_opamp_rrl_w l=x_dut_xm3_opamp_rrl_l m=x_dut_xm3_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -40 0 0 1 {name=M9_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_opamp_rrl_w l=x_dut_xm9_opamp_rrl_l m=x_dut_xm9_opamp_rrl_m}
N -420 0 -420 94 {}
N -360 -60 -360 -30 {}
N -360 30 -360 90 {}
N -120 0 -120 94 {}
N -60 -90 -60 -30 {}
N -60 30 -60 60 {}
N 320 -90 320 -30 {}
N 320 30 320 60 {}
N 380 0 380 94 {}
N 625 -60 625 -30 {}
N 625 30 625 90 {}
N 685 0 685 94 {}
N -1055 -140 1320 -140 {}
N -420 -60 625 -60 {}
N -420 0 -360 0 {}
N -320 0 -290 0 {}
N -120 0 -60 0 {}
N -20 0 280 0 {}
N 320 0 380 0 {}
N 495 0 585 0 {}
N 625 0 685 0 {}
C {devices/lab_wire.sym} -1055 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -60 -90 0 1 {name=l1 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} 625 90 2 0 {name=l2 lab=rrl__oa_d1n}
C {devices/lab_wire.sym} -360 90 2 0 {name=l3 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} 320 -90 0 1 {name=l4 lab=rrl__oa_d1p}
C {devices/lab_wire.sym} 380 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} 685 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} -120 94 2 0 {name=l8 lab=vdd}
C {devices/ipin.sym} -290 0 0 0 {name=p0 lab=rrl__oa_inn}
C {devices/ipin.sym} 10 0 0 0 {name=p1 lab=rrl__vb1}
C {devices/ipin.sym} 495 0 0 0 {name=p2 lab=rrl__oa_inp}
C {devices/iopin.sym} -420 -60 0 0 {name=p3 lab=rrl__oa_tail}
C {devices/opin.sym} -60 60 0 0 {name=p4 lab=rrl__oa_outn}
C {devices/opin.sym} 320 60 0 0 {name=p5 lab=rrl__oa_outp}
