v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {gs_001_cascode_cs} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 340 520 0 0 {name=MNB1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb1_w l=x_dut_xmnb1_l m=x_dut_xmnb1_m}
C {devices/sg13_lv_nmos_np.sym} 340 260 0 0 {name=MNB2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb2_w l=x_dut_xmnb2_l m=x_dut_xmnb2_m}
C {devices/sg13_lv_nmos_np.sym} 0 520 0 0 {name=MNCA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnca_w l=x_dut_xmnca_l m=x_dut_xmnca_m}
C {devices/sg13_lv_nmos_np.sym} 0 780 0 0 {name=MNIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnin_w l=x_dut_xmnin_l m=x_dut_xmnin_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=MPB1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpb1_w l=x_dut_xmpb1_l m=x_dut_xmpb1_m}
C {devices/sg13_lv_pmos_np.sym} -340 260 0 1 {name=MPB2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpb2_w l=x_dut_xmpb2_l m=x_dut_xmpb2_m}
C {devices/sg13_lv_pmos_np.sym} 0 260 0 0 {name=MPCA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpca_w l=x_dut_xmpca_l m=x_dut_xmpca_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=MPLD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpld_w l=x_dut_xmpld_l m=x_dut_xmpld_m}
C {devices/sg13_lv_pmos_np.sym} 340 0 0 0 {name=MPNR model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpnr_w l=x_dut_xmpnr_l m=x_dut_xmpnr_m}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -360 290 -360 330 {}
N -320 0 -320 70 {}
N -320 260 -320 330 {}
N -50 0 -50 60 {}
N -50 260 -50 320 {}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 490 {}
N 20 550 20 750 {}
N 20 810 20 920 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 80 520 80 614 {}
N 80 780 80 874 {}
N 290 0 290 260 {}
N 320 190 320 260 {}
N 320 450 320 520 {}
N 360 -140 360 -30 {}
N 360 30 360 230 {}
N 360 290 360 490 {}
N 360 550 360 920 {}
N 420 0 420 94 {}
N 420 260 420 354 {}
N 420 520 420 614 {}
N -565 -140 565 -140 {}
N -420 0 -360 0 {}
N -320 0 -260 0 {}
N -50 0 -20 0 {}
N 20 0 80 0 {}
N 260 0 320 0 {}
N 360 0 420 0 {}
N -360 60 -50 60 {}
N -360 70 -320 70 {}
N 320 190 360 190 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N -50 260 -20 260 {}
N 20 260 80 260 {}
N 360 260 420 260 {}
N -360 320 -50 320 {}
N -360 330 -320 330 {}
N 320 450 360 450 {}
N -80 520 -20 520 {}
N 20 520 80 520 {}
N 360 520 420 520 {}
N -80 780 -20 780 {}
N 20 780 80 780 {}
N -565 920 565 920 {}
C {devices/lab_wire.sym} -565 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -565 920 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -260 260 0 1 {name=l2 lab=ibias}
C {devices/lab_wire.sym} 260 0 0 0 {name=l3 lab=ibias}
C {devices/lab_wire.sym} 360 350 2 0 {name=l4 lab=nbias1}
C {devices/lab_wire.sym} -80 520 0 0 {name=l5 lab=nbias2}
C {devices/lab_wire.sym} 360 90 2 0 {name=l6 lab=nbias2}
C {devices/lab_wire.sym} 20 610 2 0 {name=l7 lab=nint}
C {devices/lab_wire.sym} -260 0 0 1 {name=l8 lab=pbias1}
C {devices/lab_wire.sym} 20 90 2 0 {name=l9 lab=pint}
C {devices/lab_wire.sym} -80 780 0 0 {name=l10 lab=vin}
C {devices/lab_wire.sym} 20 350 2 0 {name=l11 lab=vout}
C {devices/lab_wire.sym} -420 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -420 354 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} 80 354 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} 420 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 420 614 2 0 {name=l17 lab=vss}
C {devices/lab_wire.sym} 420 354 2 0 {name=l18 lab=vss}
C {devices/lab_wire.sym} 80 614 2 0 {name=l19 lab=vss}
C {devices/lab_wire.sym} 80 874 2 0 {name=l20 lab=vss}
C {devices/ipin.sym} -705 780 0 0 {name=p0 lab=vin}
C {devices/opin.sym} 705 0 0 0 {name=p1 lab=ibias}
C {devices/opin.sym} 705 290 0 0 {name=p2 lab=vout}
