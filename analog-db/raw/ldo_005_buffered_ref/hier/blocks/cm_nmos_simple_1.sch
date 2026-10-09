v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_1} -550 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} -510 0 0 1 {name=MEA_B0 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_b0_w l=x_dut_xmea_b0_l}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=MEA_BC model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_bc_w l=x_dut_xmea_bc_l}
C {devices/sg13_lv_nmos_np.sym} 170 0 0 0 {name=MEA_BF model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_bf_w l=x_dut_xmea_bf_l}
C {devices/sg13_lv_nmos_np.sym} 510 0 0 0 {name=MEA_BO model=sg13_hv_nmos spiceprefix=X w=x_dut_xmea_bo_w l=x_dut_xmea_bo_l}
N -590 0 -590 94 {}
N -530 -70 -530 -30 {}
N -530 30 -530 140 {}
N -490 -70 -490 0 {}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 140 {}
N -120 -60 -120 0 {}
N 120 0 120 60 {}
N 190 -60 190 -30 {}
N 190 30 190 140 {}
N 250 0 250 94 {}
N 460 0 460 60 {}
N 530 -60 530 -30 {}
N 530 30 530 140 {}
N 590 0 590 94 {}
N -530 -70 -490 -70 {}
N -490 -60 -120 -60 {}
N -590 0 -530 0 {}
N -250 0 -190 0 {}
N -150 0 150 0 {}
N 190 0 250 0 {}
N 460 0 490 0 {}
N 530 0 590 0 {}
N 120 60 460 60 {}
N -970 140 970 140 {}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l0 lab=ea_tail}
C {devices/lab_wire.sym} -590 94 2 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l2 lab=vss}
C {devices/lab_wire.sym} 250 94 2 0 {name=l3 lab=vss}
C {devices/lab_wire.sym} 590 94 2 0 {name=l4 lab=vss}
C {devices/iopin.sym} -970 140 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 460 0 0 0 {name=p1 lab=ea_ibias}
C {devices/opin.sym} 190 -60 0 0 {name=p2 lab=ea_nlev}
C {devices/opin.sym} 530 -60 0 0 {name=p3 lab=ea_out}
C {devices/opin.sym} 1110 -30 0 0 {name=p4 lab=ea_tail}
