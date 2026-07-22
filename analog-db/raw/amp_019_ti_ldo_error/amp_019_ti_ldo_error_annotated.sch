v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_019_ti_ldo_error} -720 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -170 260 1 0 {name=CC value='c_comp'}
C {devices/res_np.sym} 900 260 1 0 {name=RZ value='r_z'}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=M1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M2 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} 340 260 0 0 {name=M4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M5 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 680 0 0 0 {name=M6 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
C {devices/sg13_lv_pmos_np.sym} 0 260 0 0 {name=M7 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 1 {name=MB0 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} -680 520 0 1 {name=MBC model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbc_w l=x_dut_xmbc_l m=x_dut_xmbc_m}
C {devices/sg13_lv_nmos_np.sym} 0 520 0 0 {name=MBE model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbe_w l=x_dut_xmbe_l}
C {devices/sg13_lv_nmos_np.sym} 340 520 0 0 {name=MBF model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbf_w l=x_dut_xmbf_l}
C {devices/sg13_lv_nmos_np.sym} 680 260 0 0 {name=MBO model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbo_w l=x_dut_xmbo_l m=x_dut_xmbo_m}
N -760 0 -760 94 {}
N -760 260 -760 354 {}
N -760 520 -760 614 {}
N -700 -140 -700 -30 {}
N -700 30 -700 230 {}
N -700 290 -700 490 {}
N -700 550 -700 660 {}
N -420 260 -420 354 {}
N -420 520 -420 614 {}
N -360 170 -360 230 {}
N -360 290 -360 320 {}
N -360 430 -360 490 {}
N -360 550 -360 660 {}
N -320 260 -320 320 {}
N -320 450 -320 520 {}
N -200 200 -200 260 {}
N -140 260 -140 320 {}
N -20 200 -20 330 {}
N 20 -140 20 -30 {}
N 20 30 20 90 {}
N 20 170 20 230 {}
N 20 290 20 330 {}
N 20 430 20 490 {}
N 20 550 20 660 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 80 520 80 614 {}
N 360 170 360 230 {}
N 360 290 360 350 {}
N 360 430 360 490 {}
N 360 550 360 660 {}
N 420 260 420 354 {}
N 420 520 420 614 {}
N 700 -140 700 -30 {}
N 700 30 700 90 {}
N 700 170 700 230 {}
N 700 290 700 660 {}
N 760 0 760 94 {}
N 760 260 760 354 {}
N 840 200 840 260 {}
N 870 200 870 260 {}
N 930 260 930 320 {}
N -895 -140 1045 -140 {}
N -760 0 -700 0 {}
N -660 0 -20 0 {}
N 20 0 80 0 {}
N 600 0 660 0 {}
N 700 0 760 0 {}
N -760 260 -700 260 {}
N -660 260 -600 260 {}
N -420 260 -360 260 {}
N -320 260 -290 260 {}
N -230 260 -200 260 {}
N -140 260 -110 260 {}
N 20 260 80 260 {}
N 260 260 320 260 {}
N 360 260 420 260 {}
N 600 260 660 260 {}
N 700 260 760 260 {}
N 840 260 870 260 {}
N 930 260 960 260 {}
N -700 320 -360 320 {}
N -20 330 20 330 {}
N -360 450 -320 450 {}
N -760 520 -700 520 {}
N -660 520 -600 520 {}
N -420 520 -360 520 {}
N -80 520 -20 520 {}
N 20 520 80 520 {}
N 260 520 320 520 {}
N 360 520 420 520 {}
N -895 660 1045 660 {}
C {devices/lab_wire.sym} -895 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -895 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -600 520 0 1 {name=l2 lab=ibias}
C {devices/lab_wire.sym} -360 430 0 1 {name=l3 lab=ibias}
C {devices/lab_wire.sym} -80 520 0 0 {name=l4 lab=ibias}
C {devices/lab_wire.sym} 260 520 0 0 {name=l5 lab=ibias}
C {devices/lab_wire.sym} 600 260 0 0 {name=l6 lab=ibias}
C {devices/lab_wire.sym} -700 90 2 0 {name=l7 lab=na}
C {devices/lab_wire.sym} 260 260 0 0 {name=l8 lab=na}
C {devices/lab_wire.sym} -360 170 0 1 {name=l9 lab=nb}
C {devices/lab_wire.sym} 20 90 2 0 {name=l10 lab=nb}
C {devices/lab_wire.sym} 20 170 0 1 {name=l11 lab=nb}
C {devices/lab_wire.sym} 870 200 0 1 {name=l12 lab=nb}
C {devices/lab_wire.sym} -200 200 0 1 {name=l13 lab=ncz}
C {devices/lab_wire.sym} 930 320 2 0 {name=l14 lab=ncz}
C {devices/lab_wire.sym} -600 0 0 1 {name=l15 lab=nd}
C {devices/lab_wire.sym} 360 170 0 1 {name=l16 lab=nd}
C {devices/lab_wire.sym} -20 200 0 1 {name=l17 lab=ne}
C {devices/lab_wire.sym} 20 430 0 1 {name=l18 lab=ne}
C {devices/lab_wire.sym} 600 0 0 0 {name=l19 lab=ne}
C {devices/lab_wire.sym} 360 350 2 0 {name=l20 lab=nlev}
C {devices/lab_wire.sym} 360 430 0 1 {name=l21 lab=nlev}
C {devices/lab_wire.sym} -700 350 2 0 {name=l22 lab=tail}
C {devices/lab_wire.sym} -600 260 0 1 {name=l23 lab=vinn}
C {devices/lab_wire.sym} -320 320 2 0 {name=l24 lab=vinp}
C {devices/lab_wire.sym} -140 320 2 0 {name=l25 lab=vout}
C {devices/lab_wire.sym} 700 90 2 0 {name=l26 lab=vout}
C {devices/lab_wire.sym} 700 170 0 1 {name=l27 lab=vout}
C {devices/lab_wire.sym} -760 94 2 0 {name=l28 lab=vdd}
C {devices/lab_wire.sym} 420 354 2 0 {name=l29 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l30 lab=vdd}
C {devices/lab_wire.sym} 760 94 2 0 {name=l31 lab=vdd}
C {devices/lab_wire.sym} 80 354 2 0 {name=l32 lab=vdd}
C {devices/lab_wire.sym} -760 354 2 0 {name=l33 lab=vss}
C {devices/lab_wire.sym} -420 354 2 0 {name=l34 lab=vss}
C {devices/lab_wire.sym} -420 614 2 0 {name=l35 lab=vss}
C {devices/lab_wire.sym} -760 614 2 0 {name=l36 lab=vss}
C {devices/lab_wire.sym} 80 614 2 0 {name=l37 lab=vss}
C {devices/lab_wire.sym} 420 614 2 0 {name=l38 lab=vss}
C {devices/lab_wire.sym} 760 354 2 0 {name=l39 lab=vss}
C {devices/ipin.sym} -1035 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -1035 380 0 0 {name=p1 lab=vinp}
C {devices/opin.sym} 1185 30 0 0 {name=p2 lab=vout}
C {devices/opin.sym} 1185 260 0 0 {name=p3 lab=ibias}
B 8 -876 182 876 598 {fill=0}
T {NMOS Simple Current Mirror (4 outputs)} -876 164 0 0 0.3 0.3 {layer=8}
B 10 -868 182 -270 338 {fill=0}
T {NMOS Differential Pair} -868 164 0 0 0.3 0.3 {layer=10}
