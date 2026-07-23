v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cmp_001_hyst_diffpair} -700 -520 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -660 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/inv_cmos_stack_1.sym} -220 0 0 0 {name=xinv_cmos_stack_1}
C {blocks/inv_cmos_stack_2.sym} 220 0 0 0 {name=xinv_cmos_stack_2}
C {blocks/inv_cmos_stack_3.sym} 660 0 0 0 {name=xinv_cmos_stack_3}
C {devices/res_np.sym} -550 320 0 0 {name=RHN value=x_dut_rhn_value}
C {devices/res_np.sym} -330 320 0 0 {name=RHP value=x_dut_rhp_value}
C {devices/res_np.sym} -110 320 0 0 {name=RT value=x_rtail}
C {devices/sg13_lv_nmos_np.sym} 110 320 0 0 {name=MHN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmhn_w l=x_dut_xmhn_l m=x_dut_xmhn_m}
C {devices/sg13_lv_pmos_np.sym} 0 -320 0 0 {name=MHP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmhp_w l=x_dut_xmhp_l m=x_dut_xmhp_m}
C {devices/sg13_lv_nmos_np.sym} 330 320 0 0 {name=MIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmin_w l=x_dut_xmin_l m=x_dut_xmin_m}
C {devices/sg13_lv_nmos_np.sym} 550 320 0 0 {name=MIP model=sg13_lv_nmos spiceprefix=X w=x_dut_xmip_w l=x_dut_xmip_l m=x_dut_xmip_m}
N -550 -20 -510 -20 {}
C {devices/lab_wire.sym} -510 -20 0 1 {name=l0 lab=n1}
N -550 20 -510 20 {}
C {devices/lab_wire.sym} -510 20 0 1 {name=l1 lab=n2}
N -660 -80 -660 -120 {}
C {devices/lab_wire.sym} -660 -120 0 1 {name=l2 lab=vdd}
N -330 0 -370 0 {}
C {devices/lab_wire.sym} -370 0 0 0 {name=l3 lab=n1}
N -110 0 -70 0 {}
C {devices/lab_wire.sym} -70 0 0 1 {name=l4 lab=b1}
N -220 -80 -220 -120 {}
C {devices/lab_wire.sym} -220 -120 0 1 {name=l5 lab=vdd}
N -220 80 -220 120 {}
C {devices/lab_wire.sym} -220 120 2 0 {name=l6 lab=vss}
N 110 0 70 0 {}
C {devices/lab_wire.sym} 70 0 0 0 {name=l7 lab=b1}
N 330 0 370 0 {}
C {devices/lab_wire.sym} 370 0 0 1 {name=l8 lab=b2}
N 220 -80 220 -120 {}
C {devices/lab_wire.sym} 220 -120 0 1 {name=l9 lab=vdd}
N 220 80 220 120 {}
C {devices/lab_wire.sym} 220 120 2 0 {name=l10 lab=vss}
N 550 0 510 0 {}
C {devices/lab_wire.sym} 510 0 0 0 {name=l11 lab=b2}
N 770 0 810 0 {}
C {devices/lab_wire.sym} 810 0 0 1 {name=l12 lab=vout}
N 660 -80 660 -120 {}
C {devices/lab_wire.sym} 660 -120 0 1 {name=l13 lab=vdd}
N 660 80 660 120 {}
C {devices/lab_wire.sym} 660 120 2 0 {name=l14 lab=vss}
N -550 290 -550 250 {}
C {devices/lab_wire.sym} -550 250 0 1 {name=l15 lab=n1}
N -550 350 -550 390 {}
C {devices/lab_wire.sym} -550 390 2 0 {name=l16 lab=hn}
N -330 290 -330 250 {}
C {devices/lab_wire.sym} -330 250 0 1 {name=l17 lab=n1}
N -330 350 -330 390 {}
C {devices/lab_wire.sym} -330 390 2 0 {name=l18 lab=hp}
N -110 290 -110 250 {}
C {devices/lab_wire.sym} -110 250 0 1 {name=l19 lab=tail}
N -110 350 -110 390 {}
C {devices/lab_wire.sym} -110 390 2 0 {name=l20 lab=vss}
N 130 290 130 250 {}
C {devices/lab_wire.sym} 130 250 0 1 {name=l21 lab=hn}
N 90 320 50 320 {}
C {devices/lab_wire.sym} 50 320 0 0 {name=l22 lab=vout}
N 130 350 130 390 {}
C {devices/lab_wire.sym} 130 390 2 0 {name=l23 lab=vss}
N 130 320 170 320 {}
C {devices/lab_wire.sym} 170 320 0 1 {name=l24 lab=vss}
N 20 -290 20 -250 {}
C {devices/lab_wire.sym} 20 -250 2 0 {name=l25 lab=hp}
N -20 -320 -60 -320 {}
C {devices/lab_wire.sym} -60 -320 0 0 {name=l26 lab=vout}
N 20 -350 20 -390 {}
C {devices/lab_wire.sym} 20 -390 0 1 {name=l27 lab=vdd}
N 20 -320 60 -320 {}
C {devices/lab_wire.sym} 60 -320 0 1 {name=l28 lab=vdd}
N 350 290 350 250 {}
C {devices/lab_wire.sym} 350 250 0 1 {name=l29 lab=n2}
N 310 320 270 320 {}
C {devices/lab_wire.sym} 270 320 0 0 {name=l30 lab=vinn}
N 350 350 350 390 {}
C {devices/lab_wire.sym} 350 390 2 0 {name=l31 lab=tail}
N 350 320 390 320 {}
C {devices/lab_wire.sym} 390 320 0 1 {name=l32 lab=vss}
N 570 290 570 250 {}
C {devices/lab_wire.sym} 570 250 0 1 {name=l33 lab=n1}
N 530 320 490 320 {}
C {devices/lab_wire.sym} 490 320 0 0 {name=l34 lab=vinp}
N 570 350 570 390 {}
C {devices/lab_wire.sym} 570 390 2 0 {name=l35 lab=tail}
N 570 320 610 320 {}
C {devices/lab_wire.sym} 610 320 0 1 {name=l36 lab=vss}
