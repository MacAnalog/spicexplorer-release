v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_004_basic_pmos} -590 -520 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} 0 0 0 0 {name=xcm_pmos_simple_1}
C {devices/isource_np.sym} -550 320 0 0 {name=ITAIL value="dc {i_tail}"}
C {devices/res_np.sym} -330 320 0 0 {name=R1 value='r_top'}
C {devices/res_np.sym} -110 320 0 0 {name=R2 value='r_bot'}
C {devices/vsource_np.sym} -550 100 0 0 {name=VLP value="dc 0"}
C {devices/vsource_np.sym} -550 -120 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_nmos_np.sym} 110 320 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} 330 320 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} 0 -320 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N 110 -20 150 -20 {}
C {devices/lab_wire.sym} 150 -20 0 1 {name=l0 lab=egate}
N 110 20 150 20 {}
C {devices/lab_wire.sym} 150 20 0 1 {name=l1 lab=noutm}
N 0 -80 0 -120 {}
C {devices/lab_wire.sym} 0 -120 0 1 {name=l2 lab=vdd}
N -550 290 -550 250 {}
C {devices/lab_wire.sym} -550 250 0 1 {name=l3 lab=etail}
N -550 350 -550 390 {}
C {devices/lab_wire.sym} -550 390 2 0 {name=l4 lab=vss}
N -330 290 -330 250 {}
C {devices/lab_wire.sym} -330 250 0 1 {name=l5 lab=lp_brk}
N -330 350 -330 390 {}
C {devices/lab_wire.sym} -330 390 2 0 {name=l6 lab=fb}
N -110 290 -110 250 {}
C {devices/lab_wire.sym} -110 250 0 1 {name=l7 lab=fb}
N -110 350 -110 390 {}
C {devices/lab_wire.sym} -110 390 2 0 {name=l8 lab=vss}
N -550 70 -550 30 {}
C {devices/lab_wire.sym} -550 30 0 1 {name=l9 lab=lp_brk}
N -550 130 -550 170 {}
C {devices/lab_wire.sym} -550 170 2 0 {name=l10 lab=vout}
N -550 -150 -550 -190 {}
C {devices/lab_wire.sym} -550 -190 0 1 {name=l11 lab=vref}
N -550 -90 -550 -50 {}
C {devices/lab_wire.sym} -550 -50 2 0 {name=l12 lab=vss}
N 130 290 130 250 {}
C {devices/lab_wire.sym} 130 250 0 1 {name=l13 lab=noutm}
N 90 320 50 320 {}
C {devices/lab_wire.sym} 50 320 0 0 {name=l14 lab=fb}
N 130 350 130 390 {}
C {devices/lab_wire.sym} 130 390 2 0 {name=l15 lab=etail}
N 130 320 170 320 {}
C {devices/lab_wire.sym} 170 320 0 1 {name=l16 lab=vss}
N 350 290 350 250 {}
C {devices/lab_wire.sym} 350 250 0 1 {name=l17 lab=egate}
N 310 320 270 320 {}
C {devices/lab_wire.sym} 270 320 0 0 {name=l18 lab=vref}
N 350 350 350 390 {}
C {devices/lab_wire.sym} 350 390 2 0 {name=l19 lab=etail}
N 350 320 390 320 {}
C {devices/lab_wire.sym} 390 320 0 1 {name=l20 lab=vss}
N 20 -290 20 -250 {}
C {devices/lab_wire.sym} 20 -250 2 0 {name=l21 lab=vout}
N -20 -320 -60 -320 {}
C {devices/lab_wire.sym} -60 -320 0 0 {name=l22 lab=egate}
N 20 -350 20 -390 {}
C {devices/lab_wire.sym} 20 -390 0 1 {name=l23 lab=vdd}
N 20 -320 60 -320 {}
C {devices/lab_wire.sym} 60 -320 0 1 {name=l24 lab=vdd}
