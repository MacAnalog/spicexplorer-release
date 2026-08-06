v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_032_ti_ldo_error_selfbias} -940 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1005 260 1 0 {name=CC value='c_comp'}
C {devices/res_np.sym} -160 260 1 0 {name=RND value='r_nd'}
C {devices/res_np.sym} -900 260 1 0 {name=RZ value='r_z'}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} 60 260 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 400 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
C {devices/sg13_lv_nmos_np.sym} 740 260 0 0 {name=MB0 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} -510 520 0 1 {name=MBC model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbc_w l=x_dut_xmbc_l m=x_dut_xmbc_m}
C {devices/sg13_lv_nmos_np.sym} 60 520 0 1 {name=MBF model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbf_w l=x_dut_xmbf_l}
C {devices/sg13_lv_nmos_np.sym} 400 260 0 0 {name=MBO model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbo_w l=x_dut_xmbo_l m=x_dut_xmbo_m}
C {devices/sg13_lv_pmos_np.sym} 740 0 0 0 {name=MBP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmbp_w l=x_dut_xmbp_l}
N -870 260 -870 320 {}
N -760 0 -760 94 {}
N -760 260 -760 354 {}
N -700 -140 -700 -30 {}
N -700 30 -700 230 {}
N -700 290 -700 350 {}
N -590 520 -590 614 {}
N -530 320 -530 490 {}
N -530 550 -530 660 {}
N -320 -140 -320 -30 {}
N -320 30 -320 60 {}
N -320 170 -320 230 {}
N -320 290 -320 320 {}
N -260 0 -260 94 {}
N -260 260 -260 354 {}
N -220 0 -220 260 {}
N -130 260 -130 320 {}
N -100 200 -100 260 {}
N -20 260 -20 354 {}
N -20 520 -20 614 {}
N 40 170 40 230 {}
N 40 290 40 490 {}
N 40 550 40 660 {}
N 350 0 350 60 {}
N 350 260 350 520 {}
N 420 -140 420 -30 {}
N 420 30 420 230 {}
N 420 290 420 660 {}
N 480 0 480 94 {}
N 480 260 480 354 {}
N 720 0 720 70 {}
N 720 190 720 260 {}
N 760 -140 760 -30 {}
N 760 30 760 70 {}
N 760 170 760 230 {}
N 760 290 760 660 {}
N 820 0 820 94 {}
N 820 260 820 354 {}
N 945 200 945 260 {}
N 975 200 975 260 {}
N 1035 260 1035 320 {}
N -1020 -140 1175 -140 {}
N -760 0 -700 0 {}
N -660 0 -360 0 {}
N -320 0 -260 0 {}
N 320 0 380 0 {}
N 420 0 480 0 {}
N 660 0 720 0 {}
N 760 0 820 0 {}
N -320 60 350 60 {}
N 720 70 760 70 {}
N 720 190 760 190 {}
N -990 260 -930 260 {}
N -870 260 -840 260 {}
N -760 260 -700 260 {}
N -660 260 -600 260 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N -250 260 -190 260 {}
N -130 260 -100 260 {}
N -20 260 40 260 {}
N 80 260 140 260 {}
N 320 260 380 260 {}
N 420 260 480 260 {}
N 760 260 820 260 {}
N 945 260 975 260 {}
N 1035 260 1065 260 {}
N -700 320 -320 320 {}
N -590 520 -530 520 {}
N -490 520 -430 520 {}
N -20 520 40 520 {}
N 80 520 350 520 {}
N -1020 660 1175 660 {}
C {devices/lab_wire.sym} -1020 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1020 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -430 520 0 1 {name=l2 lab=ibias}
C {devices/lab_wire.sym} 320 260 0 0 {name=l3 lab=ibias}
C {devices/lab_wire.sym} 660 0 0 0 {name=l4 lab=ibias}
C {devices/lab_wire.sym} 760 170 0 1 {name=l5 lab=ibias}
C {devices/lab_wire.sym} -700 90 2 0 {name=l6 lab=na}
C {devices/lab_wire.sym} -130 320 2 0 {name=l7 lab=na}
C {devices/lab_wire.sym} 140 260 0 1 {name=l8 lab=na}
C {devices/lab_wire.sym} -870 320 2 0 {name=l9 lab=nb}
C {devices/lab_wire.sym} 320 0 0 0 {name=l10 lab=nb}
C {devices/lab_wire.sym} -320 170 0 1 {name=l11 lab=nb}
C {devices/lab_wire.sym} -990 260 0 0 {name=l12 lab=ncz}
C {devices/lab_wire.sym} 1035 320 2 0 {name=l13 lab=ncz}
C {devices/lab_wire.sym} -600 0 0 1 {name=l14 lab=nd}
C {devices/lab_wire.sym} -250 260 0 0 {name=l15 lab=nd}
C {devices/lab_wire.sym} 40 170 0 1 {name=l16 lab=nd}
C {devices/lab_wire.sym} 40 350 2 0 {name=l17 lab=nlev}
C {devices/lab_wire.sym} -700 350 2 0 {name=l18 lab=tail}
C {devices/lab_wire.sym} -600 260 0 1 {name=l19 lab=vinn}
C {devices/lab_wire.sym} -420 260 0 0 {name=l20 lab=vinp}
C {devices/lab_wire.sym} 420 90 2 0 {name=l21 lab=vout}
C {devices/lab_wire.sym} 975 200 0 1 {name=l22 lab=vout}
C {devices/lab_wire.sym} -760 94 2 0 {name=l23 lab=vdd}
C {devices/lab_wire.sym} -20 354 2 0 {name=l24 lab=vdd}
C {devices/lab_wire.sym} -260 94 2 0 {name=l25 lab=vdd}
C {devices/lab_wire.sym} 480 94 2 0 {name=l26 lab=vdd}
C {devices/lab_wire.sym} 820 94 2 0 {name=l27 lab=vdd}
C {devices/lab_wire.sym} -760 354 2 0 {name=l28 lab=vss}
C {devices/lab_wire.sym} -260 354 2 0 {name=l29 lab=vss}
C {devices/lab_wire.sym} 820 354 2 0 {name=l30 lab=vss}
C {devices/lab_wire.sym} -590 614 2 0 {name=l31 lab=vss}
C {devices/lab_wire.sym} -20 614 2 0 {name=l32 lab=vss}
C {devices/lab_wire.sym} 480 354 2 0 {name=l33 lab=vss}
C {devices/ipin.sym} -1160 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -1160 380 0 0 {name=p1 lab=vinp}
C {devices/opin.sym} 1315 30 0 0 {name=p2 lab=vout}
B 8 -706 182 936 598 {fill=0}
T {NMOS Simple Current Mirror (3 outputs)} -706 164 0 0 0.3 0.3 {layer=8}
B 10 -868 182 -152 338 {fill=0}
T {NMOS Differential Pair} -868 164 0 0 0.3 0.3 {layer=10}
