v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cmfb_002_5t_pmos_input} -480 -200 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -440 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_simple_1.sym} 0 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_pmos_simple_1.sym} 440 0 0 0 {name=xdp_pmos_simple_1}
C {devices/res_np.sym} -220 340 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 0 340 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/sg13_lv_nmos_np.sym} 220 340 0 0 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -330 -20 -290 -20 {}
C {devices/lab_wire.sym} -290 -20 0 1 {name=l0 lab=bias}
N -330 20 -290 20 {}
C {devices/lab_wire.sym} -290 20 0 1 {name=l1 lab=ptail}
N -440 -80 -440 -120 {}
C {devices/lab_wire.sym} -440 -120 0 1 {name=l2 lab=vdd}
N 110 -20 150 -20 {}
C {devices/lab_wire.sym} 150 -20 0 1 {name=l3 lab=mirr}
N 110 20 150 20 {}
C {devices/lab_wire.sym} 150 20 0 1 {name=l4 lab=vcmfb}
N 0 80 0 120 {}
C {devices/lab_wire.sym} 0 120 2 0 {name=l5 lab=vss}
N 330 -20 290 -20 {}
C {devices/lab_wire.sym} 290 -20 0 0 {name=l6 lab=cm_sense}
N 330 20 290 20 {}
C {devices/lab_wire.sym} 290 20 0 0 {name=l7 lab=vref}
N 550 -40 590 -40 {}
C {devices/lab_wire.sym} 590 -40 0 1 {name=l8 lab=mirr}
N 550 0 590 0 {}
C {devices/lab_wire.sym} 590 0 0 1 {name=l9 lab=ptail}
N 550 40 590 40 {}
C {devices/lab_wire.sym} 590 40 0 1 {name=l10 lab=vcmfb}
N 440 -100 440 -140 {}
C {devices/lab_wire.sym} 440 -140 0 1 {name=l11 lab=vdd}
N -220 310 -220 270 {}
C {devices/lab_wire.sym} -220 270 0 1 {name=l12 lab=vinn}
N -220 370 -220 410 {}
C {devices/lab_wire.sym} -220 410 2 0 {name=l13 lab=cm_sense}
N 0 310 0 270 {}
C {devices/lab_wire.sym} 0 270 0 1 {name=l14 lab=cm_sense}
N 0 370 0 410 {}
C {devices/lab_wire.sym} 0 410 2 0 {name=l15 lab=vinp}
N 240 310 240 270 {}
C {devices/lab_wire.sym} 240 270 0 1 {name=l16 lab=bias}
N 200 340 160 340 {}
C {devices/lab_wire.sym} 160 340 0 0 {name=l17 lab=bias}
N 240 370 240 410 {}
C {devices/lab_wire.sym} 240 410 2 0 {name=l18 lab=vss}
N 240 340 280 340 {}
C {devices/lab_wire.sym} 280 340 0 1 {name=l19 lab=vss}
