v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cmp_001_hyst_diffpair} -1060 -200 0 0 0.4 0.4 {}
C {devices/res_np.sym} 510 260 1 0 {name=RHN value=x_dut_rhn_value}
C {devices/res_np.sym} 275 260 1 0 {name=RHP value=x_dut_rhp_value}
C {devices/res_np.sym} 1055 520 0 0 {name=RT value=x_rtail}
C {devices/sg13_lv_nmos_np.sym} -1020 260 0 1 {name=MB1N model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb1n_w l=x_dut_xmb1n_l m=x_dut_xmb1n_m}
C {devices/sg13_lv_pmos_np.sym} -1020 0 0 1 {name=MB1P model=sg13_lv_pmos spiceprefix=X w=x_dut_xmb1p_w l=x_dut_xmb1p_l m=x_dut_xmb1p_m}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=MB2N model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb2n_w l=x_dut_xmb2n_l m=x_dut_xmb2n_m}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=MB2P model=sg13_lv_pmos spiceprefix=X w=x_dut_xmb2p_w l=x_dut_xmb2p_l m=x_dut_xmb2p_m}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=MB3N model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb3n_w l=x_dut_xmb3n_l m=x_dut_xmb3n_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=MB3P model=sg13_lv_pmos spiceprefix=X w=x_dut_xmb3p_w l=x_dut_xmb3p_l m=x_dut_xmb3p_m}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 1 {name=MHN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmhn_w l=x_dut_xmhn_l m=x_dut_xmhn_m}
C {devices/sg13_lv_pmos_np.sym} 340 0 0 0 {name=MHP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmhp_w l=x_dut_xmhp_l m=x_dut_xmhp_m}
C {devices/sg13_lv_nmos_np.sym} 885 260 0 1 {name=MIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmin_w l=x_dut_xmin_l m=x_dut_xmin_m}
C {devices/sg13_lv_nmos_np.sym} 1225 260 0 0 {name=MIP model=sg13_lv_nmos spiceprefix=X w=x_dut_xmip_w l=x_dut_xmip_l m=x_dut_xmip_m}
C {devices/sg13_lv_pmos_np.sym} 885 0 0 1 {name=MPLD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpld_w l=x_dut_xmpld_l m=x_dut_xmpld_m}
C {devices/sg13_lv_pmos_np.sym} 1225 0 0 0 {name=MPLM model=sg13_lv_pmos spiceprefix=X w=x_dut_xmplm_w l=x_dut_xmplm_l m=x_dut_xmplm_m}
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
N -420 30 -420 200 {}
N -420 260 -420 354 {}
N -360 -140 -360 -30 {}
N -360 200 -360 230 {}
N -360 290 -360 660 {}
N -290 0 -290 260 {}
N -80 260 -80 354 {}
N -20 170 -20 230 {}
N -20 290 -20 660 {}
N -10 0 -10 260 {}
N 110 200 110 260 {}
N 155 60 155 260 {}
N 305 260 305 320 {}
N 360 -140 360 -30 {}
N 360 30 360 90 {}
N 420 0 420 94 {}
N 540 260 540 320 {}
N 805 0 805 94 {}
N 805 260 805 354 {}
N 865 -140 865 -30 {}
N 865 30 865 230 {}
N 865 290 865 350 {}
N 905 0 905 70 {}
N 1055 320 1055 490 {}
N 1055 550 1055 660 {}
N 1175 0 1175 60 {}
N 1245 -140 1245 -30 {}
N 1245 30 1245 230 {}
N 1245 290 1245 320 {}
N 1305 0 1305 94 {}
N 1305 260 1305 354 {}
N -1545 -140 1750 -140 {}
N -1100 0 -1040 0 {}
N -1000 0 -940 0 {}
N -760 0 -700 0 {}
N -660 0 -600 0 {}
N -320 0 -260 0 {}
N -10 0 320 0 {}
N 360 0 420 0 {}
N 805 0 865 0 {}
N 905 0 965 0 {}
N 1175 0 1205 0 {}
N 1245 0 1305 0 {}
N -420 30 -360 30 {}
N 155 60 360 60 {}
N 865 60 1175 60 {}
N 865 70 905 70 {}
N -420 200 110 200 {}
N -1100 260 -1040 260 {}
N -1000 260 -970 260 {}
N -760 260 -700 260 {}
N -660 260 -630 260 {}
N -420 260 -360 260 {}
N -320 260 -290 260 {}
N -80 260 -20 260 {}
N -10 260 110 260 {}
N 155 260 245 260 {}
N 305 260 335 260 {}
N 420 260 480 260 {}
N 540 260 570 260 {}
N 805 260 865 260 {}
N 905 260 935 260 {}
N 1115 260 1205 260 {}
N 1245 260 1305 260 {}
N 865 320 1245 320 {}
N -1545 660 1750 660 {}
C {devices/lab_wire.sym} -1040 90 2 0 {name=l0 lab=b1}
C {devices/lab_wire.sym} -600 0 0 1 {name=l1 lab=b1}
C {devices/lab_wire.sym} -700 90 2 0 {name=l2 lab=b2}
C {devices/lab_wire.sym} -700 170 0 1 {name=l3 lab=b2}
C {devices/lab_wire.sym} -260 0 0 1 {name=l4 lab=b2}
C {devices/lab_wire.sym} -20 170 0 1 {name=l5 lab=hn}
C {devices/lab_wire.sym} 420 260 0 0 {name=l6 lab=hn}
C {devices/lab_wire.sym} 360 90 2 0 {name=l7 lab=hp}
C {devices/lab_wire.sym} -940 0 0 1 {name=l8 lab=n1}
C {devices/lab_wire.sym} 305 320 2 0 {name=l9 lab=n1}
C {devices/lab_wire.sym} 540 320 2 0 {name=l10 lab=n1}
C {devices/lab_wire.sym} 1245 90 2 0 {name=l11 lab=n1}
C {devices/lab_wire.sym} 965 0 0 1 {name=l12 lab=n2}
C {devices/lab_wire.sym} 865 350 2 0 {name=l13 lab=tail}
C {devices/lab_wire.sym} -1100 94 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} -760 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} -360 0 0 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 420 94 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} 805 94 2 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} 1305 94 2 0 {name=l19 lab=vdd}
C {devices/lab_wire.sym} -1100 354 2 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} -760 354 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} -420 354 2 0 {name=l22 lab=vss}
C {devices/lab_wire.sym} -80 354 2 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} 805 354 2 0 {name=l24 lab=vss}
C {devices/lab_wire.sym} 1305 354 2 0 {name=l25 lab=vss}
C {devices/ipin.sym} 935 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} 1115 260 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -1545 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1545 660 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 290 0 0 0 {name=p4 lab=vout}
B 8 381 -78 1729 78 {fill=0}
T {PMOS Simple Current Mirror} 381 -96 0 0 0.3 0.3 {layer=8}
B 10 -1524 -78 -950 338 {fill=0}
T {COMPLEMENTARY Inverter (2 outputs)} -1524 -96 0 0 0.3 0.3 {layer=10}
B 12 -1184 -78 -610 338 {fill=0}
T {COMPLEMENTARY Inverter (2 outputs)} -1184 -96 0 0 0.3 0.3 {layer=12}
B 21 -844 -78 -270 338 {fill=0}
T {COMPLEMENTARY Inverter (2 outputs)} -844 -96 0 0 0.3 0.3 {layer=21}
