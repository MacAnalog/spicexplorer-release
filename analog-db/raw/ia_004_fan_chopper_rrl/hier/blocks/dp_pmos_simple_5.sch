v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dp_pmos_simple_5} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=M7_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_opamp_rrl_w l=x_dut_xm7_opamp_rrl_l m=x_dut_xm7_opamp_rrl_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M8_OPAMP_RRL model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_opamp_rrl_w l=x_dut_xm8_opamp_rrl_l m=x_dut_xm8_opamp_rrl_m}
N -250 0 -250 94 {}
N -190 -60 -190 -30 {}
N -190 30 -190 60 {}
N 190 -60 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N -885 -140 885 -140 {}
N -190 -60 190 -60 {}
N -250 0 -190 0 {}
N -150 0 -120 0 {}
N 60 0 150 0 {}
N 190 0 250 0 {}
C {devices/lab_wire.sym} -885 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l1 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l2 lab=vdd}
C {devices/ipin.sym} -120 0 0 0 {name=p0 lab=rrl__vb4}
C {devices/ipin.sym} 60 0 0 0 {name=p1 lab=rrl__oa_outp}
C {devices/iopin.sym} -190 -60 0 0 {name=p2 lab=rrl__oa_cm_tail}
C {devices/opin.sym} -190 60 0 0 {name=p3 lab=rrl__oa_cm_bias}
C {devices/opin.sym} 190 60 0 0 {name=p4 lab=rrl__oa_cm_sense}
