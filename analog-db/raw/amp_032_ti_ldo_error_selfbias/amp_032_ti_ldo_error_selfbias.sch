v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_032_ti_ldo_error_selfbias} -940 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1185 260 1 0 {name=CC value='c_comp'}
C {devices/res_np.sym} -55 260 1 0 {name=RND value='r_nd'}
C {devices/res_np.sym} -900 260 1 0 {name=RZ value='r_z'}
C {devices/sg13_lv_nmos_np.sym} -610 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} -270 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -610 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} 240 260 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} -270 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 580 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
C {devices/sg13_lv_nmos_np.sym} 920 260 0 0 {name=MB0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} -440 520 0 1 {name=MBC model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbc_w l=x_dut_xmbc_l m=x_dut_xmbc_m}
C {devices/sg13_lv_nmos_np.sym} 240 520 0 1 {name=MBF model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbf_w l=x_dut_xmbf_l}
C {devices/sg13_lv_nmos_np.sym} 580 260 0 0 {name=MBO model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbo_w l=x_dut_xmbo_l m=x_dut_xmbo_m}
C {devices/sg13_lv_pmos_np.sym} 920 0 0 0 {name=MBP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmbp_w l=x_dut_xmbp_l}
N -870 260 -870 320 {}
N -690 0 -690 94 {}
N -690 260 -690 354 {}
N -630 -140 -630 -30 {}
N -630 30 -630 230 {}
N -630 290 -630 350 {}
N -520 520 -520 614 {}
N -460 320 -460 490 {}
N -460 550 -460 660 {}
N -390 520 -390 580 {}
N -310 60 -310 230 {}
N -250 -140 -250 -30 {}
N -250 30 -250 60 {}
N -250 290 -250 320 {}
N -190 0 -190 94 {}
N -190 260 -190 354 {}
N -25 260 -25 320 {}
N 160 260 160 354 {}
N 160 520 160 614 {}
N 220 170 220 230 {}
N 220 290 220 490 {}
N 220 550 220 660 {}
N 290 520 290 580 {}
N 530 0 530 60 {}
N 530 260 530 520 {}
N 600 -140 600 -30 {}
N 600 30 600 230 {}
N 600 290 600 660 {}
N 660 0 660 94 {}
N 660 260 660 354 {}
N 900 0 900 70 {}
N 900 190 900 260 {}
N 940 -140 940 -30 {}
N 940 30 940 70 {}
N 940 170 940 230 {}
N 940 290 940 660 {}
N 1000 0 1000 94 {}
N 1000 260 1000 354 {}
N 1215 260 1215 320 {}
N -1020 -140 1430 -140 {}
N -690 0 -630 0 {}
N -590 0 -290 0 {}
N -250 0 -190 0 {}
N 500 0 560 0 {}
N 600 0 660 0 {}
N 840 0 900 0 {}
N 940 0 1000 0 {}
N -310 60 530 60 {}
N 900 70 940 70 {}
N 900 190 940 190 {}
N -310 230 -250 230 {}
N -990 260 -930 260 {}
N -870 260 -840 260 {}
N -690 260 -630 260 {}
N -590 260 -560 260 {}
N -380 260 -290 260 {}
N -250 260 -190 260 {}
N -145 260 -85 260 {}
N -25 260 5 260 {}
N 160 260 220 260 {}
N 260 260 320 260 {}
N 500 260 560 260 {}
N 600 260 660 260 {}
N 940 260 1000 260 {}
N 1125 260 1155 260 {}
N 1215 260 1245 260 {}
N -630 320 -250 320 {}
N -520 520 -460 520 {}
N -420 520 -390 520 {}
N 160 520 220 520 {}
N 260 520 530 520 {}
N -390 580 290 580 {}
N -1020 660 1430 660 {}
C {devices/lab_wire.sym} 500 260 0 0 {name=l0 lab=ibias}
C {devices/lab_wire.sym} 840 0 0 0 {name=l1 lab=ibias}
C {devices/lab_wire.sym} 940 170 0 1 {name=l2 lab=ibias}
C {devices/lab_wire.sym} -630 90 2 0 {name=l3 lab=na}
C {devices/lab_wire.sym} -25 320 2 0 {name=l4 lab=na}
C {devices/lab_wire.sym} 320 260 0 1 {name=l5 lab=na}
C {devices/lab_wire.sym} -870 320 2 0 {name=l6 lab=nb}
C {devices/lab_wire.sym} 500 0 0 0 {name=l7 lab=nb}
C {devices/lab_wire.sym} -990 260 0 0 {name=l8 lab=ncz}
C {devices/lab_wire.sym} 1215 320 2 0 {name=l9 lab=ncz}
C {devices/lab_wire.sym} -530 0 0 1 {name=l10 lab=nd}
C {devices/lab_wire.sym} -145 260 0 0 {name=l11 lab=nd}
C {devices/lab_wire.sym} 220 170 0 1 {name=l12 lab=nd}
C {devices/lab_wire.sym} 220 350 2 0 {name=l13 lab=nlev}
C {devices/lab_wire.sym} -630 350 2 0 {name=l14 lab=tail}
C {devices/lab_wire.sym} 600 90 2 0 {name=l15 lab=vout}
C {devices/lab_wire.sym} -690 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 160 354 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} -190 94 2 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} 660 94 2 0 {name=l19 lab=vdd}
C {devices/lab_wire.sym} 1000 94 2 0 {name=l20 lab=vdd}
C {devices/lab_wire.sym} -690 354 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} -190 354 2 0 {name=l22 lab=vss}
C {devices/lab_wire.sym} 1000 354 2 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} -520 614 2 0 {name=l24 lab=vss}
C {devices/lab_wire.sym} 160 614 2 0 {name=l25 lab=vss}
C {devices/lab_wire.sym} 660 354 2 0 {name=l26 lab=vss}
C {devices/ipin.sym} -560 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -380 260 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -1020 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1020 660 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 1125 260 0 0 {name=p4 lab=vout}
