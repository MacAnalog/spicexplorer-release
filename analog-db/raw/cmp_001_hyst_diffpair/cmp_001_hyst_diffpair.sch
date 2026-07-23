v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cmp_001_hyst_diffpair} -1060 -200 0 0 0.4 0.4 {}
C {devices/res_np.sym} 510 260 1 0 {name=RHN value=x_dut_rhn_value}
C {devices/res_np.sym} 275 260 1 0 {name=RHP value=x_dut_rhp_value}
C {devices/res_np.sym} 980 520 0 0 {name=RT value=x_rtail}
C {devices/sg13_lv_nmos_np.sym} -1020 260 0 1 {name=MB1N model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb1n_w l=x_dut_xmb1n_l m=x_dut_xmb1n_m}
C {devices/sg13_lv_pmos_np.sym} -1020 0 0 1 {name=MB1P model=sg13_lv_pmos spiceprefix=X w=x_dut_xmb1p_w l=x_dut_xmb1p_l m=x_dut_xmb1p_m}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=MB2N model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb2n_w l=x_dut_xmb2n_l m=x_dut_xmb2n_m}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=MB2P model=sg13_lv_pmos spiceprefix=X w=x_dut_xmb2p_w l=x_dut_xmb2p_l m=x_dut_xmb2p_m}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=MB3N model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb3n_w l=x_dut_xmb3n_l m=x_dut_xmb3n_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=MB3P model=sg13_lv_pmos spiceprefix=X w=x_dut_xmb3p_w l=x_dut_xmb3p_l m=x_dut_xmb3p_m}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 1 {name=MHN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmhn_w l=x_dut_xmhn_l m=x_dut_xmhn_m}
C {devices/sg13_lv_pmos_np.sym} 340 0 0 0 {name=MHP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmhp_w l=x_dut_xmhp_l m=x_dut_xmhp_m}
C {devices/sg13_lv_nmos_np.sym} 810 260 0 1 {name=MIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmin_w l=x_dut_xmin_l m=x_dut_xmin_m}
C {devices/sg13_lv_nmos_np.sym} 1150 260 0 0 {name=MIP model=sg13_lv_nmos spiceprefix=X w=x_dut_xmip_w l=x_dut_xmip_l m=x_dut_xmip_m}
C {devices/sg13_lv_pmos_np.sym} 810 0 0 1 {name=MPLD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpld_w l=x_dut_xmpld_l m=x_dut_xmpld_m}
C {devices/sg13_lv_pmos_np.sym} 1150 0 0 0 {name=MPLM model=sg13_lv_pmos spiceprefix=X w=x_dut_xmplm_w l=x_dut_xmplm_l m=x_dut_xmplm_m}
N -1100 0 -1100 94 {}
N -1100 260 -1100 354 {}
N -1040 -140 -1040 -30 {}
N -1040 30 -1040 230 {}
N -1040 290 -1040 660 {}
N -970 0 -970 260 {}
N -760 0 -760 94 {}
N -760 260 -760 354 {}
N -700 -140 -700 -30 {}
N -700 30 -700 90 {}
N -700 170 -700 230 {}
N -700 290 -700 660 {}
N -630 0 -630 260 {}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -360 -140 -360 -30 {}
N -360 30 -360 90 {}
N -360 170 -360 230 {}
N -360 290 -360 660 {}
N -290 0 -290 260 {}
N -80 260 -80 354 {}
N -20 170 -20 230 {}
N -20 290 -20 660 {}
N 290 0 290 260 {}
N 305 260 305 320 {}
N 360 -140 360 -30 {}
N 360 30 360 260 {}
N 420 0 420 94 {}
N 450 200 450 260 {}
N 480 200 480 260 {}
N 540 260 540 320 {}
N 730 0 730 94 {}
N 730 260 730 354 {}
N 790 -140 790 -30 {}
N 790 30 790 230 {}
N 790 290 790 350 {}
N 830 0 830 70 {}
N 980 320 980 490 {}
N 980 550 980 660 {}
N 1100 0 1100 60 {}
N 1170 -140 1170 -30 {}
N 1170 30 1170 230 {}
N 1170 290 1170 320 {}
N 1230 0 1230 94 {}
N 1230 260 1230 354 {}
N -1245 -140 1375 -140 {}
N -1100 0 -1040 0 {}
N -1000 0 -940 0 {}
N -760 0 -700 0 {}
N -660 0 -600 0 {}
N -420 0 -360 0 {}
N -320 0 -260 0 {}
N 260 0 320 0 {}
N 360 0 420 0 {}
N 730 0 790 0 {}
N 830 0 890 0 {}
N 1100 0 1130 0 {}
N 1170 0 1230 0 {}
N 790 60 1100 60 {}
N 790 70 830 70 {}
N -1100 260 -1040 260 {}
N -1000 260 -970 260 {}
N -760 260 -700 260 {}
N -660 260 -630 260 {}
N -420 260 -360 260 {}
N -320 260 -290 260 {}
N -80 260 -20 260 {}
N 20 260 80 260 {}
N 185 260 245 260 {}
N 305 260 335 260 {}
N 450 260 480 260 {}
N 540 260 570 260 {}
N 730 260 790 260 {}
N 830 260 890 260 {}
N 1070 260 1130 260 {}
N 1170 260 1230 260 {}
N 790 320 1170 320 {}
N -1245 660 1375 660 {}
C {devices/lab_wire.sym} -1245 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1245 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -1040 90 2 0 {name=l2 lab=b1}
C {devices/lab_wire.sym} -600 0 0 1 {name=l3 lab=b1}
C {devices/lab_wire.sym} -700 90 2 0 {name=l4 lab=b2}
C {devices/lab_wire.sym} -700 170 0 1 {name=l5 lab=b2}
C {devices/lab_wire.sym} -260 0 0 1 {name=l6 lab=b2}
C {devices/lab_wire.sym} -20 170 0 1 {name=l7 lab=hn}
C {devices/lab_wire.sym} 480 200 0 1 {name=l8 lab=hn}
C {devices/lab_wire.sym} 185 260 0 0 {name=l9 lab=hp}
C {devices/lab_wire.sym} 360 90 2 0 {name=l10 lab=hp}
C {devices/lab_wire.sym} -940 0 0 1 {name=l11 lab=n1}
C {devices/lab_wire.sym} 305 320 2 0 {name=l12 lab=n1}
C {devices/lab_wire.sym} 540 320 2 0 {name=l13 lab=n1}
C {devices/lab_wire.sym} 1170 90 2 0 {name=l14 lab=n1}
C {devices/lab_wire.sym} 890 0 0 1 {name=l15 lab=n2}
C {devices/lab_wire.sym} 790 350 2 0 {name=l16 lab=tail}
C {devices/lab_wire.sym} 890 260 0 1 {name=l17 lab=vinn}
C {devices/lab_wire.sym} 1070 260 0 0 {name=l18 lab=vinp}
C {devices/lab_wire.sym} -360 90 2 0 {name=l19 lab=vout}
C {devices/lab_wire.sym} -360 170 0 1 {name=l20 lab=vout}
C {devices/lab_wire.sym} 80 260 0 1 {name=l21 lab=vout}
C {devices/lab_wire.sym} 260 0 0 0 {name=l22 lab=vout}
C {devices/lab_wire.sym} -1100 94 2 0 {name=l23 lab=vdd}
C {devices/lab_wire.sym} -760 94 2 0 {name=l24 lab=vdd}
C {devices/lab_wire.sym} -420 94 2 0 {name=l25 lab=vdd}
C {devices/lab_wire.sym} 420 94 2 0 {name=l26 lab=vdd}
C {devices/lab_wire.sym} 730 94 2 0 {name=l27 lab=vdd}
C {devices/lab_wire.sym} 1230 94 2 0 {name=l28 lab=vdd}
C {devices/lab_wire.sym} -1100 354 2 0 {name=l29 lab=vss}
C {devices/lab_wire.sym} -760 354 2 0 {name=l30 lab=vss}
C {devices/lab_wire.sym} -420 354 2 0 {name=l31 lab=vss}
C {devices/lab_wire.sym} -80 354 2 0 {name=l32 lab=vss}
C {devices/lab_wire.sym} 730 354 2 0 {name=l33 lab=vss}
C {devices/lab_wire.sym} 1230 354 2 0 {name=l34 lab=vss}
C {devices/ipin.sym} -1385 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -1385 380 0 0 {name=p1 lab=vinp}
C {devices/opin.sym} 1515 0 0 0 {name=p2 lab=vout}
