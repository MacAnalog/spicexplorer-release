v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {gs_001_cascode_cs} -380 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 0 520 0 1 {name=MNB1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb1_w l=x_dut_xmnb1_l m=x_dut_xmnb1_m}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 1 {name=MNB2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb2_w l=x_dut_xmnb2_l m=x_dut_xmnb2_m}
C {devices/sg13_lv_nmos_np.sym} 340 520 0 0 {name=MNCA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnca_w l=x_dut_xmnca_l m=x_dut_xmnca_m}
C {devices/sg13_lv_nmos_np.sym} 340 780 0 0 {name=MNIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnin_w l=x_dut_xmnin_l m=x_dut_xmnin_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=MPB1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpb1_w l=x_dut_xmpb1_l m=x_dut_xmpb1_m}
C {devices/sg13_lv_pmos_np.sym} -340 260 0 1 {name=MPB2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpb2_w l=x_dut_xmpb2_l m=x_dut_xmpb2_m}
C {devices/sg13_lv_pmos_np.sym} 340 260 0 0 {name=MPCA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpca_w l=x_dut_xmpca_l m=x_dut_xmpca_m}
C {devices/sg13_lv_pmos_np.sym} 340 0 0 0 {name=MPLD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpld_w l=x_dut_xmpld_l m=x_dut_xmpld_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 1 {name=MPNR model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpnr_w l=x_dut_xmpnr_l m=x_dut_xmpnr_m}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -360 290 -360 330 {}
N -320 0 -320 70 {}
N -320 260 -320 330 {}
N -80 30 -80 200 {}
N -80 290 -80 460 {}
N -80 520 -80 614 {}
N -20 -140 -20 -30 {}
N -20 30 -20 90 {}
N -20 190 -20 230 {}
N -20 290 -20 350 {}
N -20 450 -20 490 {}
N -20 550 -20 920 {}
N 20 190 20 260 {}
N 20 450 20 520 {}
N 50 0 50 320 {}
N 290 200 290 520 {}
N 320 260 320 320 {}
N 360 -140 360 -30 {}
N 360 30 360 230 {}
N 360 290 360 490 {}
N 360 550 360 750 {}
N 360 810 360 920 {}
N 420 0 420 94 {}
N 420 260 420 354 {}
N 420 520 420 614 {}
N 420 780 420 874 {}
N -865 -140 865 -140 {}
N -420 0 -360 0 {}
N -320 0 -260 0 {}
N 20 0 50 0 {}
N 260 0 320 0 {}
N 360 0 420 0 {}
N -80 30 -20 30 {}
N -360 70 -320 70 {}
N -20 190 20 190 {}
N -80 200 -20 200 {}
N 20 200 290 200 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N 360 260 420 260 {}
N -80 290 -20 290 {}
N 50 320 320 320 {}
N -360 330 -320 330 {}
N -20 450 20 450 {}
N -80 460 -20 460 {}
N -80 520 -20 520 {}
N 290 520 320 520 {}
N 360 520 420 520 {}
N 230 780 320 780 {}
N 360 780 420 780 {}
N -865 920 865 920 {}
C {devices/lab_wire.sym} -260 260 0 1 {name=l0 lab=ibias}
C {devices/lab_wire.sym} -20 350 2 0 {name=l1 lab=nbias1}
C {devices/lab_wire.sym} -20 90 2 0 {name=l2 lab=nbias2}
C {devices/lab_wire.sym} 360 610 2 0 {name=l3 lab=nint}
C {devices/lab_wire.sym} -260 0 0 1 {name=l4 lab=pbias1}
C {devices/lab_wire.sym} 260 0 0 0 {name=l5 lab=pbias1}
C {devices/lab_wire.sym} 360 90 2 0 {name=l6 lab=pint}
C {devices/lab_wire.sym} -420 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} -420 354 2 0 {name=l8 lab=vdd}
C {devices/lab_wire.sym} 420 354 2 0 {name=l9 lab=vdd}
C {devices/lab_wire.sym} 420 94 2 0 {name=l10 lab=vdd}
C {devices/lab_wire.sym} -20 0 0 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} -80 614 2 0 {name=l12 lab=vss}
C {devices/lab_wire.sym} -20 260 0 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} 420 614 2 0 {name=l14 lab=vss}
C {devices/lab_wire.sym} 420 874 2 0 {name=l15 lab=vss}
C {devices/ipin.sym} 230 780 0 0 {name=p0 lab=vin}
C {devices/iopin.sym} -865 -140 0 0 {name=p1 lab=vdd}
C {devices/iopin.sym} -865 920 0 0 {name=p2 lab=vss}
C {devices/opin.sym} 320 320 0 0 {name=p3 lab=ibias}
C {devices/opin.sym} 360 320 0 0 {name=p4 lab=vout}
B 8 -844 -78 844 338 {fill=0}
T {PMOS Cascode Current Mirror} -844 -96 0 0 0.3 0.3 {layer=8}
B 10 -822 -56 822 56 {fill=0 dash=4}
T {PMOS Simple Current Mirror} -822 -122 0 0 0.3 0.3 {layer=10}
