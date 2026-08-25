v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_007_pmos} -890 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 360 260 1 0 {name=CC value='c_comp'}
C {devices/capa_np.sym} -330 260 1 0 {name=CFF value='c_ff'}
C {devices/isource_np.sym} -850 520 0 0 {name=IBIAS value="dc {i_tail}"}
C {devices/res_np.sym} 10 260 0 0 {name=R1 value='r_top'}
C {devices/res_np.sym} -170 520 0 0 {name=R2 value='r_bot'}
C {devices/res_np.sym} 185 260 1 0 {name=RZ value='r_z'}
C {devices/vsource_np.sym} -850 260 0 0 {name=VLP value="dc 0"}
C {devices/vsource_np.sym} -850 0 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_nmos_np.sym} -510 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} -170 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_nmos_np.sym} 190 520 0 0 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
C {devices/sg13_lv_pmos_np.sym} 530 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -850 -90 -850 -30 {}
N -850 30 -850 90 {}
N -850 170 -850 230 {}
N -850 290 -850 350 {}
N -850 430 -850 490 {}
N -850 550 -850 610 {}
N -590 0 -590 94 {}
N -590 260 -590 354 {}
N -530 -140 -530 -30 {}
N -530 30 -530 230 {}
N -530 290 -530 350 {}
N -490 0 -490 70 {}
N -420 520 -420 614 {}
N -360 320 -360 490 {}
N -360 550 -360 660 {}
N -320 520 -320 580 {}
N -220 0 -220 60 {}
N -190 200 -190 260 {}
N -170 260 -170 490 {}
N -170 550 -170 660 {}
N -150 -140 -150 -30 {}
N -150 30 -150 230 {}
N -150 290 -150 320 {}
N -90 0 -90 94 {}
N -90 260 -90 354 {}
N 10 170 10 230 {}
N 10 290 10 460 {}
N 155 200 155 260 {}
N 170 450 170 520 {}
N 210 430 210 490 {}
N 210 550 210 660 {}
N 215 260 215 320 {}
N 245 200 245 260 {}
N 270 520 270 614 {}
N 330 200 330 260 {}
N 390 260 390 320 {}
N 480 0 480 260 {}
N 550 -140 550 -30 {}
N 550 30 550 260 {}
N 610 0 610 94 {}
N -910 -140 740 -140 {}
N -590 0 -530 0 {}
N -490 0 -430 0 {}
N -220 0 -190 0 {}
N -150 0 -90 0 {}
N 450 0 510 0 {}
N 550 0 610 0 {}
N -530 60 -220 60 {}
N -530 70 -490 70 {}
N -590 260 -530 260 {}
N -490 260 -360 260 {}
N -300 260 -270 260 {}
N -220 260 -190 260 {}
N -150 260 -90 260 {}
N 125 260 155 260 {}
N 215 260 245 260 {}
N 300 260 330 260 {}
N 390 260 420 260 {}
N -530 320 -150 320 {}
N 170 450 210 450 {}
N -170 460 10 460 {}
N -420 520 -360 520 {}
N -320 520 -290 520 {}
N 210 520 270 520 {}
N -910 660 740 660 {}
C {devices/lab_wire.sym} -910 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -910 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -320 580 2 0 {name=l2 lab=ebias}
C {devices/lab_wire.sym} 210 430 0 1 {name=l3 lab=ebias}
C {devices/lab_wire.sym} -150 90 2 0 {name=l4 lab=egate}
C {devices/lab_wire.sym} 215 320 2 0 {name=l5 lab=egate}
C {devices/lab_wire.sym} 450 0 0 0 {name=l6 lab=egate}
C {devices/lab_wire.sym} -530 350 2 0 {name=l7 lab=etail}
C {devices/lab_wire.sym} -490 260 0 0 {name=l8 lab=fb}
C {devices/lab_wire.sym} 10 350 2 0 {name=l9 lab=fb}
C {devices/lab_wire.sym} -300 260 0 0 {name=l10 lab=lp_brk}
C {devices/lab_wire.sym} 10 170 0 1 {name=l11 lab=lp_brk}
C {devices/lab_wire.sym} 155 200 0 1 {name=l12 lab=ncz}
C {devices/lab_wire.sym} 390 320 2 0 {name=l13 lab=ncz}
C {devices/lab_wire.sym} -430 0 0 1 {name=l14 lab=noutm}
C {devices/lab_wire.sym} 330 200 0 1 {name=l15 lab=vout}
C {devices/lab_wire.sym} 550 90 2 0 {name=l16 lab=vout}
C {devices/lab_wire.sym} -190 200 0 1 {name=l17 lab=vref}
C {devices/lab_wire.sym} -590 94 2 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} -90 94 2 0 {name=l19 lab=vdd}
C {devices/lab_wire.sym} 610 94 2 0 {name=l20 lab=vdd}
C {devices/lab_wire.sym} -590 354 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} -90 354 2 0 {name=l22 lab=vss}
C {devices/lab_wire.sym} -420 614 2 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} 270 614 2 0 {name=l24 lab=vss}
C {devices/lab_wire.sym} -850 350 2 0 {name=l25 lab=vout}
C {devices/lab_wire.sym} -850 170 0 1 {name=l26 lab=lp_brk}
C {devices/lab_wire.sym} -850 430 0 1 {name=l27 lab=vdd}
C {devices/lab_wire.sym} -850 610 2 0 {name=l28 lab=ebias}
C {devices/lab_wire.sym} -850 90 2 0 {name=l29 lab=vss}
C {devices/lab_wire.sym} -850 -90 0 1 {name=l30 lab=vref}
C {devices/opin.sym} 880 30 0 0 {name=p0 lab=vout}
B 8 -698 -78 18 78 {fill=0}
T {PMOS Simple Current Mirror} -698 -96 0 0 0.3 0.3 {layer=8}
B 10 -528 442 378 598 {fill=0}
T {NMOS Simple Current Mirror} -528 424 0 0 0.3 0.3 {layer=10}
B 12 -698 182 18 338 {fill=0}
T {NMOS Differential Pair} -698 164 0 0 0.3 0.3 {layer=12}
