v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_033_ti_ldo_ref_selfbias} -720 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -680 260 0 0 {name=CC value='c_comp'}
C {devices/res_np.sym} 75 260 0 0 {name=RZ value='r_z'}
C {devices/sg13_lv_nmos_np.sym} -445 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} -105 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -445 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} -105 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} 295 0 0 1 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_nmos_np.sym} 635 260 0 0 {name=MB0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} -275 520 0 1 {name=MBC model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbc_w l=x_dut_xmbc_l m=x_dut_xmbc_m}
C {devices/sg13_lv_nmos_np.sym} 295 260 0 1 {name=MBO model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbo_w l=x_dut_xmbo_l m=x_dut_xmbo_m}
C {devices/sg13_lv_pmos_np.sym} 635 0 0 0 {name=MBP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmbp_w l=x_dut_xmbp_l}
N -680 170 -680 230 {}
N -680 290 -680 350 {}
N -525 0 -525 94 {}
N -525 260 -525 354 {}
N -465 -140 -465 -30 {}
N -465 30 -465 70 {}
N -465 170 -465 230 {}
N -465 290 -465 350 {}
N -425 0 -425 70 {}
N -355 520 -355 614 {}
N -295 430 -295 490 {}
N -295 550 -295 660 {}
N -155 0 -155 60 {}
N -85 -140 -85 -30 {}
N -85 30 -85 90 {}
N -85 170 -85 230 {}
N -85 290 -85 350 {}
N -25 0 -25 94 {}
N -25 260 -25 354 {}
N 75 170 75 230 {}
N 75 290 75 350 {}
N 215 0 215 94 {}
N 215 260 215 354 {}
N 275 -140 275 -30 {}
N 275 30 275 90 {}
N 275 170 275 230 {}
N 275 290 275 350 {}
N 345 0 345 200 {}
N 345 260 345 520 {}
N 615 0 615 70 {}
N 615 190 615 260 {}
N 655 -140 655 -30 {}
N 655 30 655 230 {}
N 655 290 655 660 {}
N 715 0 715 94 {}
N 715 260 715 354 {}
N -740 -140 850 -140 {}
N -525 0 -465 0 {}
N -425 0 -365 0 {}
N -155 0 -125 0 {}
N -85 0 -25 0 {}
N 215 0 275 0 {}
N 315 0 375 0 {}
N 555 0 615 0 {}
N 655 0 715 0 {}
N -465 60 -155 60 {}
N -465 70 -425 70 {}
N 615 70 655 70 {}
N 615 190 655 190 {}
N -525 260 -465 260 {}
N -425 260 -365 260 {}
N -185 260 -125 260 {}
N -85 260 -25 260 {}
N 215 260 275 260 {}
N 315 260 375 260 {}
N 655 260 715 260 {}
N -355 520 -295 520 {}
N -255 520 345 520 {}
N -740 660 850 660 {}
C {devices/lab_wire.sym} -740 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -740 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 375 260 0 1 {name=l2 lab=ibias}
C {devices/lab_wire.sym} 555 0 0 0 {name=l3 lab=ibias}
C {devices/lab_wire.sym} -365 0 0 1 {name=l4 lab=na}
C {devices/lab_wire.sym} -465 170 0 1 {name=l5 lab=na}
C {devices/lab_wire.sym} -85 90 2 0 {name=l6 lab=nb}
C {devices/lab_wire.sym} -85 170 0 1 {name=l7 lab=nb}
C {devices/lab_wire.sym} 75 170 0 1 {name=l8 lab=nb}
C {devices/lab_wire.sym} 375 0 0 1 {name=l9 lab=nb}
C {devices/lab_wire.sym} -680 170 0 1 {name=l10 lab=ncz}
C {devices/lab_wire.sym} 75 350 2 0 {name=l11 lab=ncz}
C {devices/lab_wire.sym} -465 350 2 0 {name=l12 lab=tail}
C {devices/lab_wire.sym} -295 430 0 1 {name=l13 lab=tail}
C {devices/lab_wire.sym} -85 350 2 0 {name=l14 lab=tail}
C {devices/lab_wire.sym} -365 260 0 1 {name=l15 lab=vinn}
C {devices/lab_wire.sym} -185 260 0 0 {name=l16 lab=vinp}
C {devices/lab_wire.sym} -680 350 2 0 {name=l17 lab=vout}
C {devices/lab_wire.sym} 275 90 2 0 {name=l18 lab=vout}
C {devices/lab_wire.sym} 275 170 0 1 {name=l19 lab=vout}
C {devices/lab_wire.sym} -525 94 2 0 {name=l20 lab=vdd}
C {devices/lab_wire.sym} -25 94 2 0 {name=l21 lab=vdd}
C {devices/lab_wire.sym} 215 94 2 0 {name=l22 lab=vdd}
C {devices/lab_wire.sym} 715 94 2 0 {name=l23 lab=vdd}
C {devices/lab_wire.sym} -525 354 2 0 {name=l24 lab=vss}
C {devices/lab_wire.sym} -25 354 2 0 {name=l25 lab=vss}
C {devices/lab_wire.sym} 715 354 2 0 {name=l26 lab=vss}
C {devices/lab_wire.sym} -355 614 2 0 {name=l27 lab=vss}
C {devices/lab_wire.sym} 215 354 2 0 {name=l28 lab=vss}
C {devices/lab_wire.sym} 275 350 2 0 {name=l29 lab=vss}
C {devices/ipin.sym} -880 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -880 380 0 0 {name=p1 lab=vinp}
C {devices/opin.sym} 990 30 0 0 {name=p2 lab=vout}
B 8 -633 -78 83 78 {fill=0}
T {PMOS Simple Current Mirror} -633 -96 0 0 0.3 0.3 {layer=8}
B 10 -471 182 831 598 {fill=0}
T {NMOS Simple Current Mirror (2 outputs)} -471 164 0 0 0.3 0.3 {layer=10}
B 12 -633 182 83 338 {fill=0}
T {NMOS Differential Pair} -633 164 0 0 0.3 0.3 {layer=12}
