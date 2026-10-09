v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_1} -550 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 510 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
N -590 0 -590 94 {}
N -530 -140 -530 -30 {}
N -530 30 -530 70 {}
N -490 -60 -490 70 {}
N -250 0 -250 94 {}
N -190 -140 -190 -30 {}
N -190 30 -190 90 {}
N -120 -60 -120 0 {}
N 120 -60 120 0 {}
N 190 -140 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N 460 -60 460 0 {}
N 530 -140 530 -30 {}
N 530 30 530 60 {}
N 590 0 590 94 {}
N -985 -140 985 -140 {}
N -490 -60 -120 -60 {}
N 120 -60 460 -60 {}
N -590 0 -530 0 {}
N -250 0 -190 0 {}
N -150 0 150 0 {}
N 190 0 250 0 {}
N 460 0 490 0 {}
N 530 0 590 0 {}
N -530 70 -490 70 {}
C {devices/lab_wire.sym} -190 90 2 0 {name=l0 lab=VB4}
C {devices/lab_wire.sym} -590 94 2 0 {name=l1 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l2 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l3 lab=vdd}
C {devices/lab_wire.sym} 590 94 2 0 {name=l4 lab=vdd}
C {devices/iopin.sym} -985 -140 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 460 -60 0 0 {name=p1 lab=net1}
C {devices/opin.sym} 190 60 0 0 {name=p2 lab=VB3}
C {devices/opin.sym} 530 60 0 0 {name=p3 lab=net31}
C {devices/opin.sym} 1125 30 0 0 {name=p4 lab=VB4}
