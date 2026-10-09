v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_033_ti_ldo_ref_selfbias} -720 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -680 260 0 0 {name=CC value='c_comp'}
C {devices/res_np.sym} 190 260 0 0 {name=RZ value='r_z'}
C {devices/sg13_lv_nmos_np.sym} -370 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} -30 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -370 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} -30 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} 485 0 0 1 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_nmos_np.sym} 825 260 0 0 {name=MB0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} -200 520 0 1 {name=MBC model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbc_w l=x_dut_xmbc_l m=x_dut_xmbc_m}
C {devices/sg13_lv_nmos_np.sym} 485 260 0 1 {name=MBO model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbo_w l=x_dut_xmbo_l m=x_dut_xmbo_m}
C {devices/sg13_lv_pmos_np.sym} 825 0 0 0 {name=MBP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmbp_w l=x_dut_xmbp_l}
N -680 170 -680 230 {}
N -680 290 -680 320 {}
N -450 0 -450 94 {}
N -450 260 -450 354 {}
N -390 -140 -390 -30 {}
N -390 30 -390 230 {}
N -390 290 -390 350 {}
N -350 0 -350 70 {}
N -280 520 -280 614 {}
N -220 320 -220 490 {}
N -220 550 -220 660 {}
N -80 0 -80 60 {}
N -10 -140 -10 -30 {}
N -10 30 -10 230 {}
N -10 290 -10 320 {}
N 50 0 50 94 {}
N 50 260 50 354 {}
N 190 200 190 230 {}
N 190 290 190 350 {}
N 405 60 405 230 {}
N 405 260 405 354 {}
N 465 -140 465 -30 {}
N 465 30 465 90 {}
N 465 290 465 660 {}
N 535 260 535 520 {}
N 595 0 595 200 {}
N 805 0 805 70 {}
N 805 190 805 260 {}
N 845 -140 845 -30 {}
N 845 30 845 230 {}
N 845 290 845 660 {}
N 905 0 905 94 {}
N 905 260 905 354 {}
N -765 -140 1235 -140 {}
N -450 0 -390 0 {}
N -350 0 -290 0 {}
N -80 0 -50 0 {}
N -10 0 50 0 {}
N 505 0 595 0 {}
N 745 0 805 0 {}
N 845 0 905 0 {}
N -390 60 -80 60 {}
N 405 60 465 60 {}
N -390 70 -350 70 {}
N 805 70 845 70 {}
N 805 190 845 190 {}
N -10 200 595 200 {}
N 405 230 465 230 {}
N -450 260 -390 260 {}
N -350 260 -320 260 {}
N -140 260 -50 260 {}
N -10 260 50 260 {}
N 405 260 465 260 {}
N 475 260 805 260 {}
N 845 260 905 260 {}
N -390 320 -10 320 {}
N -280 520 -220 520 {}
N -180 520 535 520 {}
N -765 660 1235 660 {}
C {devices/lab_wire.sym} 745 0 0 0 {name=l0 lab=ibias}
C {devices/lab_wire.sym} -290 0 0 1 {name=l1 lab=na}
C {devices/lab_wire.sym} 565 0 0 1 {name=l2 lab=nb}
C {devices/lab_wire.sym} -680 170 0 1 {name=l3 lab=ncz}
C {devices/lab_wire.sym} 190 350 2 0 {name=l4 lab=ncz}
C {devices/lab_wire.sym} -390 350 2 0 {name=l5 lab=tail}
C {devices/lab_wire.sym} 465 90 2 0 {name=l6 lab=vout}
C {devices/lab_wire.sym} -450 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} 50 94 2 0 {name=l8 lab=vdd}
C {devices/lab_wire.sym} 465 0 0 0 {name=l9 lab=vdd}
C {devices/lab_wire.sym} 905 94 2 0 {name=l10 lab=vdd}
C {devices/lab_wire.sym} -450 354 2 0 {name=l11 lab=vss}
C {devices/lab_wire.sym} 50 354 2 0 {name=l12 lab=vss}
C {devices/lab_wire.sym} 905 354 2 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} -280 614 2 0 {name=l14 lab=vss}
C {devices/lab_wire.sym} 405 354 2 0 {name=l15 lab=vss}
C {devices/ipin.sym} -320 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -140 260 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -765 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -765 660 0 0 {name=p3 lab=vss}
C {devices/opin.sym} -680 320 0 0 {name=p4 lab=vout}
B 8 -746 -78 346 78 {fill=0}
T {PMOS Simple Current Mirror} -746 -96 0 0 0.3 0.3 {layer=8}
B 10 -680 182 1217 598 {fill=0}
T {NMOS Simple Current Mirror (2 outputs)} -680 164 0 0 0.3 0.3 {layer=10}
B 12 -746 182 346 338 {fill=0}
T {NMOS Differential Pair} -746 164 0 0 0.3 0.3 {layer=12}
