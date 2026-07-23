v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {tsn_002_ptat_classic} -260 -200 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} 0 0 0 0 {name=xcm_pmos_simple_1}
C {devices/res_np.sym} -220 320 0 0 {name=R0 value=x_r0}
C {devices/sg13_lv_nmos_np.sym} 0 320 0 0 {name=M0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_nmos_np.sym} 220 320 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
N 110 -20 150 -20 {}
C {devices/lab_wire.sym} 150 -20 0 1 {name=l0 lab=net1}
N 110 20 150 20 {}
C {devices/lab_wire.sym} 150 20 0 1 {name=l1 lab=vmir}
N 0 -80 0 -120 {}
C {devices/lab_wire.sym} 0 -120 0 1 {name=l2 lab=vdd}
N -220 290 -220 250 {}
C {devices/lab_wire.sym} -220 250 0 1 {name=l3 lab=vout}
N -220 350 -220 390 {}
C {devices/lab_wire.sym} -220 390 2 0 {name=l4 lab=vss}
N 20 290 20 250 {}
C {devices/lab_wire.sym} 20 250 0 1 {name=l5 lab=vmir}
N -20 320 -60 320 {}
C {devices/lab_wire.sym} -60 320 0 0 {name=l6 lab=net1}
N 20 350 20 390 {}
C {devices/lab_wire.sym} 20 390 2 0 {name=l7 lab=vout}
N 20 320 60 320 {}
C {devices/lab_wire.sym} 60 320 0 1 {name=l8 lab=vout}
N 240 290 240 250 {}
C {devices/lab_wire.sym} 240 250 0 1 {name=l9 lab=net1}
N 200 320 160 320 {}
C {devices/lab_wire.sym} 160 320 0 0 {name=l10 lab=net1}
N 240 350 240 390 {}
C {devices/lab_wire.sym} 240 390 2 0 {name=l11 lab=vss}
N 240 320 280 320 {}
C {devices/lab_wire.sym} 280 320 0 1 {name=l12 lab=vss}
