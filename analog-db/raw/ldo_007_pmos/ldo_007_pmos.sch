v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_007_pmos} -900 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 400 260 1 0 {name=CC value='c_comp'}
C {devices/capa_np.sym} -330 260 1 0 {name=CFF value='c_ff'}
C {devices/isource_np.sym} -860 520 0 0 {name=IBIAS value="dc \{i_tail\}"}
C {devices/res_np.sym} 50 260 0 0 {name=R1 value='r_top'}
C {devices/res_np.sym} -170 520 0 0 {name=R2 value='r_bot'}
C {devices/res_np.sym} 225 260 1 0 {name=RZ value='r_z'}
C {devices/vsource_np.sym} -860 260 0 0 {name=VLP value="dc 0" savecurrent=false}
C {devices/vsource_np.sym} -860 0 0 0 {name=VREF value="dc \{vref_val\}" savecurrent=false}
C {devices/sg13_lv_nmos_np.sym} -510 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} -170 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_nmos_np.sym} 230 520 0 0 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
C {devices/sg13_lv_pmos_np.sym} 570 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -860 -90 -860 -30 {}
N -860 30 -860 90 {}
N -860 170 -860 230 {}
N -860 290 -860 350 {}
N -860 430 -860 490 {}
N -860 550 -860 610 {}
N -590 0 -590 94 {}
N -590 260 -590 354 {}
N -530 -140 -530 -30 {}
N -530 30 -530 230 {}
N -530 290 -530 350 {}
N -490 0 -490 70 {}
N -420 520 -420 614 {}
N -360 320 -360 490 {}
N -360 550 -360 660 {}
N -290 520 -290 580 {}
N -220 0 -220 60 {}
N -170 460 -170 490 {}
N -170 550 -170 660 {}
N -150 -140 -150 -30 {}
N -150 30 -150 230 {}
N -150 290 -150 320 {}
N -90 0 -90 94 {}
N -90 260 -90 354 {}
N 50 170 50 230 {}
N 50 290 50 460 {}
N 210 450 210 580 {}
N 250 430 250 490 {}
N 250 550 250 660 {}
N 285 -60 285 260 {}
N 310 520 310 614 {}
N 430 260 430 320 {}
N 520 -60 520 0 {}
N 590 -140 590 -30 {}
N 590 30 590 60 {}
N 650 0 650 94 {}
N -920 -140 1045 -140 {}
N 285 -60 520 -60 {}
N -590 0 -530 0 {}
N -490 0 -430 0 {}
N -220 0 -190 0 {}
N -150 0 -90 0 {}
N 490 0 550 0 {}
N 590 0 650 0 {}
N -530 60 -220 60 {}
N -530 70 -490 70 {}
N -150 140 285 140 {}
N -590 260 -530 260 {}
N -490 260 -360 260 {}
N -300 260 -270 260 {}
N -250 260 -190 260 {}
N -150 260 -90 260 {}
N 135 260 195 260 {}
N 255 260 285 260 {}
N 310 260 370 260 {}
N 430 260 460 260 {}
N -530 320 -150 320 {}
N 210 450 250 450 {}
N -170 460 50 460 {}
N -420 520 -360 520 {}
N -320 520 -290 520 {}
N 250 520 310 520 {}
N -290 580 210 580 {}
N -920 660 1045 660 {}
C {devices/lab_wire.sym} 250 430 0 1 {name=l0 lab=ebias}
C {devices/lab_wire.sym} 490 0 0 0 {name=l1 lab=egate}
C {devices/lab_wire.sym} -530 350 2 0 {name=l2 lab=etail}
C {devices/lab_wire.sym} -490 260 0 0 {name=l3 lab=fb}
C {devices/lab_wire.sym} 50 350 2 0 {name=l4 lab=fb}
C {devices/lab_wire.sym} -300 260 0 0 {name=l5 lab=lp_brk}
C {devices/lab_wire.sym} 50 170 0 1 {name=l6 lab=lp_brk}
C {devices/lab_wire.sym} 135 260 0 0 {name=l7 lab=ncz}
C {devices/lab_wire.sym} 430 320 2 0 {name=l8 lab=ncz}
C {devices/lab_wire.sym} -430 0 0 1 {name=l9 lab=noutm}
C {devices/lab_wire.sym} 310 260 0 0 {name=l10 lab=vout}
C {devices/lab_wire.sym} -250 260 0 0 {name=l11 lab=vref}
C {devices/lab_wire.sym} -590 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -90 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} 650 94 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} -590 354 2 0 {name=l15 lab=vss}
C {devices/lab_wire.sym} -90 354 2 0 {name=l16 lab=vss}
C {devices/lab_wire.sym} -420 614 2 0 {name=l17 lab=vss}
C {devices/lab_wire.sym} 310 614 2 0 {name=l18 lab=vss}
C {devices/lab_wire.sym} -860 350 2 0 {name=l19 lab=vout}
C {devices/lab_wire.sym} -860 170 0 1 {name=l20 lab=lp_brk}
C {devices/lab_wire.sym} -860 430 0 1 {name=l21 lab=vdd}
C {devices/lab_wire.sym} -860 610 2 0 {name=l22 lab=ebias}
C {devices/lab_wire.sym} -860 90 2 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} -860 -90 0 1 {name=l24 lab=vref}
C {devices/iopin.sym} -920 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -920 660 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 590 60 0 0 {name=p2 lab=vout}
