v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_004_basic_pmos} -720 -200 0 0 0.4 0.4 {}
C {devices/isource_np.sym} -680 390 0 0 {name=ITAIL value="dc {i_tail}"}
C {devices/res_np.sym} 180 260 1 0 {name=R1 value='r_top'}
C {devices/res_np.sym} 0 390 0 0 {name=R2 value='r_bot'}
C {devices/vsource_np.sym} -680 130 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} 360 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -680 40 -680 100 {}
N -680 160 -680 220 {}
N -680 300 -680 360 {}
N -680 420 -680 480 {}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -360 290 -360 350 {}
N -320 0 -320 70 {}
N -50 0 -50 60 {}
N 0 260 0 360 {}
N 0 420 0 530 {}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 320 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 310 0 310 60 {}
N 380 -140 380 -30 {}
N 380 30 380 260 {}
N 440 0 440 94 {}
N -740 -140 570 -140 {}
N -420 0 -360 0 {}
N -320 0 -260 0 {}
N -50 0 -20 0 {}
N 20 0 80 0 {}
N 280 0 340 0 {}
N 380 0 440 0 {}
N -360 60 -50 60 {}
N 20 60 310 60 {}
N -360 70 -320 70 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N -80 260 -20 260 {}
N 20 260 80 260 {}
N 90 260 150 260 {}
N 210 260 380 260 {}
N -360 320 20 320 {}
N -60 360 0 360 {}
N -740 530 570 530 {}
C {devices/lab_wire.sym} -740 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -740 530 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 280 0 0 0 {name=l2 lab=egate}
C {devices/lab_wire.sym} -360 350 2 0 {name=l3 lab=etail}
C {devices/lab_wire.sym} -260 260 0 1 {name=l4 lab=fb}
C {devices/lab_wire.sym} -60 360 0 0 {name=l5 lab=fb}
C {devices/lab_wire.sym} 90 260 0 0 {name=l6 lab=fb}
C {devices/lab_wire.sym} -260 0 0 1 {name=l7 lab=noutm}
C {devices/lab_wire.sym} 380 90 2 0 {name=l8 lab=vout}
C {devices/lab_wire.sym} -80 260 0 0 {name=l9 lab=vref}
C {devices/lab_wire.sym} -420 94 2 0 {name=l10 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} 440 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -420 354 2 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} 80 354 2 0 {name=l14 lab=vss}
C {devices/lab_wire.sym} -680 300 0 1 {name=l15 lab=etail}
C {devices/lab_wire.sym} -680 480 2 0 {name=l16 lab=vss}
C {devices/lab_wire.sym} -680 220 2 0 {name=l17 lab=vss}
C {devices/lab_wire.sym} -680 40 0 1 {name=l18 lab=vref}
C {devices/opin.sym} 710 30 0 0 {name=p0 lab=vout}
