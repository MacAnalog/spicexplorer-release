v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_019_ti_ldo_error} -720 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 135 260 1 0 {name=CC value='c_comp'}
C {devices/res_np.sym} -40 260 1 0 {name=RZ value='r_z'}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=M1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} -500 260 0 1 {name=M2 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} 360 260 0 0 {name=M4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} -320 0 0 1 {name=M5 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 700 0 0 0 {name=M6 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
C {devices/sg13_lv_pmos_np.sym} -320 260 0 1 {name=M7 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l}
C {devices/sg13_lv_nmos_np.sym} 20 520 0 0 {name=MB0 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} -680 520 0 1 {name=MBC model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbc_w l=x_dut_xmbc_l m=x_dut_xmbc_m}
C {devices/sg13_lv_nmos_np.sym} -320 520 0 1 {name=MBE model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbe_w l=x_dut_xmbe_l}
C {devices/sg13_lv_nmos_np.sym} 360 520 0 0 {name=MBF model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbf_w l=x_dut_xmbf_l}
C {devices/sg13_lv_nmos_np.sym} 700 260 0 0 {name=MBO model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbo_w l=x_dut_xmbo_l m=x_dut_xmbo_m}
N -760 0 -760 94 {}
N -760 260 -760 354 {}
N -760 520 -760 614 {}
N -700 -140 -700 -30 {}
N -700 30 -700 230 {}
N -700 290 -700 490 {}
N -700 550 -700 660 {}
N -580 260 -580 354 {}
N -520 170 -520 230 {}
N -520 290 -520 320 {}
N -480 260 -480 320 {}
N -400 0 -400 94 {}
N -400 260 -400 354 {}
N -400 520 -400 614 {}
N -340 -140 -340 -30 {}
N -340 30 -340 90 {}
N -340 170 -340 230 {}
N -340 290 -340 490 {}
N -340 550 -340 660 {}
N -300 260 -300 330 {}
N -10 260 -10 320 {}
N 0 450 0 520 {}
N 40 430 40 490 {}
N 40 550 40 660 {}
N 100 520 100 614 {}
N 165 260 165 320 {}
N 310 200 310 260 {}
N 340 200 340 260 {}
N 380 0 380 230 {}
N 380 290 380 350 {}
N 380 430 380 490 {}
N 380 550 380 660 {}
N 440 260 440 354 {}
N 440 520 440 614 {}
N 720 -140 720 -30 {}
N 720 30 720 230 {}
N 720 290 720 660 {}
N 780 0 780 94 {}
N 780 260 780 354 {}
N -895 -140 915 -140 {}
N -760 0 -700 0 {}
N -660 0 -600 0 {}
N -400 0 -340 0 {}
N -300 0 380 0 {}
N 620 0 680 0 {}
N 720 0 780 0 {}
N -760 260 -700 260 {}
N -660 260 -630 260 {}
N -580 260 -520 260 {}
N -480 260 -450 260 {}
N -400 260 -340 260 {}
N -300 260 -240 260 {}
N -130 260 -70 260 {}
N -10 260 105 260 {}
N 165 260 195 260 {}
N 310 260 340 260 {}
N 380 260 440 260 {}
N 620 260 680 260 {}
N 720 260 780 260 {}
N -700 320 -520 320 {}
N -340 330 -300 330 {}
N 0 450 40 450 {}
N -760 520 -700 520 {}
N -660 520 -600 520 {}
N -400 520 -340 520 {}
N -300 520 -240 520 {}
N 40 520 100 520 {}
N 280 520 340 520 {}
N 380 520 440 520 {}
N -895 660 915 660 {}
C {devices/lab_wire.sym} -895 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -895 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -600 520 0 1 {name=l2 lab=ibias}
C {devices/lab_wire.sym} -240 520 0 1 {name=l3 lab=ibias}
C {devices/lab_wire.sym} 40 430 0 1 {name=l4 lab=ibias}
C {devices/lab_wire.sym} 280 520 0 0 {name=l5 lab=ibias}
C {devices/lab_wire.sym} 620 260 0 0 {name=l6 lab=ibias}
C {devices/lab_wire.sym} -700 90 2 0 {name=l7 lab=na}
C {devices/lab_wire.sym} 340 200 0 1 {name=l8 lab=na}
C {devices/lab_wire.sym} -520 170 0 1 {name=l9 lab=nb}
C {devices/lab_wire.sym} -340 90 2 0 {name=l10 lab=nb}
C {devices/lab_wire.sym} -340 170 0 1 {name=l11 lab=nb}
C {devices/lab_wire.sym} -130 260 0 0 {name=l12 lab=nb}
C {devices/lab_wire.sym} -10 320 2 0 {name=l13 lab=ncz}
C {devices/lab_wire.sym} -600 0 0 1 {name=l14 lab=nd}
C {devices/lab_wire.sym} -240 0 0 1 {name=l15 lab=nd}
C {devices/lab_wire.sym} -240 260 0 1 {name=l16 lab=ne}
C {devices/lab_wire.sym} 620 0 0 0 {name=l17 lab=ne}
C {devices/lab_wire.sym} 380 350 2 0 {name=l18 lab=nlev}
C {devices/lab_wire.sym} 380 430 0 1 {name=l19 lab=nlev}
C {devices/lab_wire.sym} -700 350 2 0 {name=l20 lab=tail}
C {devices/lab_wire.sym} -660 260 0 0 {name=l21 lab=vinn}
C {devices/lab_wire.sym} -480 320 2 0 {name=l22 lab=vinp}
C {devices/lab_wire.sym} 165 320 2 0 {name=l23 lab=vout}
C {devices/lab_wire.sym} 720 90 2 0 {name=l24 lab=vout}
C {devices/lab_wire.sym} -760 94 2 0 {name=l25 lab=vdd}
C {devices/lab_wire.sym} 440 354 2 0 {name=l26 lab=vdd}
C {devices/lab_wire.sym} -400 94 2 0 {name=l27 lab=vdd}
C {devices/lab_wire.sym} 780 94 2 0 {name=l28 lab=vdd}
C {devices/lab_wire.sym} -400 354 2 0 {name=l29 lab=vdd}
C {devices/lab_wire.sym} -760 354 2 0 {name=l30 lab=vss}
C {devices/lab_wire.sym} -580 354 2 0 {name=l31 lab=vss}
C {devices/lab_wire.sym} 100 614 2 0 {name=l32 lab=vss}
C {devices/lab_wire.sym} -760 614 2 0 {name=l33 lab=vss}
C {devices/lab_wire.sym} -400 614 2 0 {name=l34 lab=vss}
C {devices/lab_wire.sym} 440 614 2 0 {name=l35 lab=vss}
C {devices/lab_wire.sym} 780 354 2 0 {name=l36 lab=vss}
C {devices/ipin.sym} -1035 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -1035 380 0 0 {name=p1 lab=vinp}
C {devices/opin.sym} 1055 30 0 0 {name=p2 lab=vout}
C {devices/opin.sym} 1055 260 0 0 {name=p3 lab=ibias}
