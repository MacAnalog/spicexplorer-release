v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_004_basic_pmos} -1070 -200 0 0 0.4 0.4 {}
C {devices/isource_np.sym} -690 390 0 0 {name=ITAIL value="dc \{i_tail\}"}
C {devices/res_np.sym} 250 260 0 0 {name=R1 value='r_top'}
C {devices/res_np.sym} -70 390 0 0 {name=R2 value='r_bot'}
C {devices/vsource_np.sym} -690 130 0 0 {name=VLP value="dc 0" savecurrent=false}
C {devices/vsource_np.sym} -1030 390 0 0 {name=VREF value="dc \{vref_val\}" savecurrent=false}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} 340 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -1030 300 -1030 360 {}
N -1030 420 -1030 480 {}
N -690 300 -690 360 {}
N -690 420 -690 480 {}
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
N 360 30 360 60 {}
N 420 0 420 94 {}
N -1090 -140 815 -140 {}
N -420 0 -360 0 {}
N -320 0 -260 0 {}
N -50 0 -20 0 {}
N 20 0 80 0 {}
N 260 0 320 0 {}
N 360 0 420 0 {}
N -360 60 -50 60 {}
N 20 60 290 60 {}
N -360 70 -320 70 {}
N -750 100 -690 100 {}
N -750 160 -690 160 {}
N -420 260 -360 260 {}
N -320 260 -70 260 {}
N -50 260 -20 260 {}
N 20 260 80 260 {}
N -360 320 20 320 {}
N -70 330 250 330 {}
N -1090 530 815 530 {}
C {devices/lab_wire.sym} 260 0 0 0 {name=l0 lab=egate}
C {devices/lab_wire.sym} -360 350 2 0 {name=l1 lab=etail}
C {devices/lab_wire.sym} -260 260 0 1 {name=l2 lab=fb}
C {devices/lab_wire.sym} 250 170 0 1 {name=l3 lab=lp_brk}
C {devices/lab_wire.sym} -260 0 0 1 {name=l4 lab=noutm}
C {devices/lab_wire.sym} -20 260 0 0 {name=l5 lab=vref}
C {devices/lab_wire.sym} -420 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} 420 94 2 0 {name=l8 lab=vdd}
C {devices/lab_wire.sym} -420 354 2 0 {name=l9 lab=vss}
C {devices/lab_wire.sym} 80 354 2 0 {name=l10 lab=vss}
C {devices/lab_wire.sym} -690 300 0 1 {name=l11 lab=etail}
C {devices/lab_wire.sym} -690 480 2 0 {name=l12 lab=vss}
C {devices/lab_wire.sym} -1030 480 2 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} -750 100 0 0 {name=l14 lab=lp_brk}
C {devices/lab_wire.sym} -750 160 0 0 {name=l15 lab=vout}
C {devices/lab_wire.sym} -1030 300 0 1 {name=l16 lab=vref}
C {devices/iopin.sym} -1090 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -1090 530 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 360 60 0 0 {name=p2 lab=vout}
