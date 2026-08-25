v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_004_basic_pmos} -1060 -200 0 0 0.4 0.4 {}
C {devices/isource_np.sym} -680 390 0 0 {name=ITAIL value="dc {i_tail}"}
C {devices/res_np.sym} 250 260 0 0 {name=R1 value='r_top'}
C {devices/res_np.sym} -70 390 0 0 {name=R2 value='r_bot'}
C {devices/vsource_np.sym} -680 130 0 0 {name=VLP value="dc 0"}
C {devices/vsource_np.sym} -1020 390 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} 340 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -1020 300 -1020 360 {}
N -1020 420 -1020 480 {}
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
N -70 260 -70 360 {}
N -70 420 -70 530 {}
N -50 0 -50 60 {}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 320 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 250 170 250 230 {}
N 250 290 250 330 {}
N 290 0 290 60 {}
N 360 -140 360 -30 {}
N 360 30 360 90 {}
N 420 0 420 94 {}
N -1080 -140 550 -140 {}
N -420 0 -360 0 {}
N -320 0 -260 0 {}
N -50 0 -20 0 {}
N 20 0 80 0 {}
N 260 0 320 0 {}
N 360 0 420 0 {}
N -360 60 -50 60 {}
N 20 60 290 60 {}
N -360 70 -320 70 {}
N -420 260 -360 260 {}
N -320 260 -70 260 {}
N -50 260 -20 260 {}
N 20 260 80 260 {}
N -360 320 20 320 {}
N -70 330 250 330 {}
N -1080 530 550 530 {}
C {devices/lab_wire.sym} -1080 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1080 530 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 260 0 0 0 {name=l2 lab=egate}
C {devices/lab_wire.sym} -360 350 2 0 {name=l3 lab=etail}
C {devices/lab_wire.sym} -260 260 0 1 {name=l4 lab=fb}
C {devices/lab_wire.sym} 250 170 0 1 {name=l5 lab=lp_brk}
C {devices/lab_wire.sym} -260 0 0 1 {name=l6 lab=noutm}
C {devices/lab_wire.sym} 360 90 2 0 {name=l7 lab=vout}
C {devices/lab_wire.sym} -20 260 0 0 {name=l8 lab=vref}
C {devices/lab_wire.sym} -420 94 2 0 {name=l9 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l10 lab=vdd}
C {devices/lab_wire.sym} 420 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} -420 354 2 0 {name=l12 lab=vss}
C {devices/lab_wire.sym} 80 354 2 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} -680 300 0 1 {name=l14 lab=etail}
C {devices/lab_wire.sym} -680 480 2 0 {name=l15 lab=vss}
C {devices/lab_wire.sym} -1020 480 2 0 {name=l16 lab=vss}
C {devices/lab_wire.sym} -680 40 0 1 {name=l17 lab=lp_brk}
C {devices/lab_wire.sym} -680 220 2 0 {name=l18 lab=vout}
C {devices/lab_wire.sym} -1020 300 0 1 {name=l19 lab=vref}
C {devices/opin.sym} 690 30 0 0 {name=p0 lab=vout}
B 8 -528 -78 188 78 {fill=0}
T {PMOS Simple Current Mirror} -528 -96 0 0 0.3 0.3 {layer=8}
