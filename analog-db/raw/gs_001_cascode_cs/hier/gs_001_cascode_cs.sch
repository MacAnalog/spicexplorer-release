v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {gs_001_cascode_cs} -370 -520 0 0 0.4 0.4 {}
C {blocks/cm_pmos_cascode_1.sym} 0 0 0 0 {name=xcm_pmos_cascode_1}
C {devices/sg13_lv_nmos_np.sym} -330 320 0 0 {name=MNB1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb1_w l=x_dut_xmnb1_l m=x_dut_xmnb1_m}
C {devices/sg13_lv_nmos_np.sym} -110 320 0 0 {name=MNB2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb2_w l=x_dut_xmnb2_l m=x_dut_xmnb2_m}
C {devices/sg13_lv_nmos_np.sym} 110 320 0 0 {name=MNCA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnca_w l=x_dut_xmnca_l m=x_dut_xmnca_m}
C {devices/sg13_lv_nmos_np.sym} 330 320 0 0 {name=MNIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnin_w l=x_dut_xmnin_l m=x_dut_xmnin_m}
C {devices/sg13_lv_pmos_np.sym} 0 -320 0 0 {name=MPNR model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpnr_w l=x_dut_xmpnr_l m=x_dut_xmpnr_m}
N 110 -20 150 -20 {}
C {devices/lab_wire.sym} 150 -20 0 1 {name=l0 lab=ibias}
N 110 20 150 20 {}
C {devices/lab_wire.sym} 150 20 0 1 {name=l1 lab=vout}
N 0 -80 0 -120 {}
C {devices/lab_wire.sym} 0 -120 0 1 {name=l2 lab=vdd}
N -310 290 -310 250 {}
C {devices/lab_wire.sym} -310 250 0 1 {name=l3 lab=nbias1}
N -350 320 -390 320 {}
C {devices/lab_wire.sym} -390 320 0 0 {name=l4 lab=nbias1}
N -310 350 -310 390 {}
C {devices/lab_wire.sym} -310 390 2 0 {name=l5 lab=vss}
N -310 320 -270 320 {}
C {devices/lab_wire.sym} -270 320 0 1 {name=l6 lab=vss}
N -90 290 -90 250 {}
C {devices/lab_wire.sym} -90 250 0 1 {name=l7 lab=nbias2}
N -130 320 -170 320 {}
C {devices/lab_wire.sym} -170 320 0 0 {name=l8 lab=nbias2}
N -90 350 -90 390 {}
C {devices/lab_wire.sym} -90 390 2 0 {name=l9 lab=nbias1}
N -90 320 -50 320 {}
C {devices/lab_wire.sym} -50 320 0 1 {name=l10 lab=vss}
N 130 290 130 250 {}
C {devices/lab_wire.sym} 130 250 0 1 {name=l11 lab=vout}
N 90 320 50 320 {}
C {devices/lab_wire.sym} 50 320 0 0 {name=l12 lab=nbias2}
N 130 350 130 390 {}
C {devices/lab_wire.sym} 130 390 2 0 {name=l13 lab=nint}
N 130 320 170 320 {}
C {devices/lab_wire.sym} 170 320 0 1 {name=l14 lab=vss}
N 350 290 350 250 {}
C {devices/lab_wire.sym} 350 250 0 1 {name=l15 lab=nint}
N 310 320 270 320 {}
C {devices/lab_wire.sym} 270 320 0 0 {name=l16 lab=vin}
N 350 350 350 390 {}
C {devices/lab_wire.sym} 350 390 2 0 {name=l17 lab=vss}
N 350 320 390 320 {}
C {devices/lab_wire.sym} 390 320 0 1 {name=l18 lab=vss}
N 20 -290 20 -250 {}
C {devices/lab_wire.sym} 20 -250 2 0 {name=l19 lab=nbias2}
N -20 -320 -60 -320 {}
C {devices/lab_wire.sym} -60 -320 0 0 {name=l20 lab=ibias}
N 20 -350 20 -390 {}
C {devices/lab_wire.sym} 20 -390 0 1 {name=l21 lab=vdd}
N 20 -320 60 -320 {}
C {devices/lab_wire.sym} 60 -320 0 1 {name=l22 lab=vdd}
