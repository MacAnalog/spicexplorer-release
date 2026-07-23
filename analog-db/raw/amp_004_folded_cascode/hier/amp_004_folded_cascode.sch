v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_004_folded_cascode} -970 -200 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -710 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_simple_1.sym} -270 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_pmos_simple_1.sym} 170 0 0 0 {name=xdp_pmos_simple_1}
C {blocks/cm_pmos_low_voltage_cascode_1.sym} 660 0 0 0 {name=xcm_pmos_low_voltage_cascode_1}
C {devices/vsource_np.sym} -930 340 0 0 {name=V1 value=x_dut_vb1}
C {devices/vsource_np.sym} -930 120 0 0 {name=V2 value=x_dut_vb2}
C {devices/sg13_lv_nmos_np.sym} -110 340 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l ng=x_dut_xm5_ng m=x_dut_xm5_m}
C {devices/sg13_lv_nmos_np.sym} 110 340 0 0 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l ng=x_dut_xm6_ng m=x_dut_xm6_m}
N -600 -40 -560 -40 {}
C {devices/lab_wire.sym} -560 -40 0 1 {name=l0 lab=ibias}
N -600 0 -560 0 {}
C {devices/lab_wire.sym} -560 0 0 1 {name=l1 lab=nbias}
N -600 40 -560 40 {}
C {devices/lab_wire.sym} -560 40 0 1 {name=l2 lab=tail}
N -710 -100 -710 -140 {}
C {devices/lab_wire.sym} -710 -140 0 1 {name=l3 lab=vdd}
N -160 -40 -120 -40 {}
C {devices/lab_wire.sym} -120 -40 0 1 {name=l4 lab=foldn}
N -160 0 -120 0 {}
C {devices/lab_wire.sym} -120 0 0 1 {name=l5 lab=foldp}
N -160 40 -120 40 {}
C {devices/lab_wire.sym} -120 40 0 1 {name=l6 lab=nbias}
N -270 100 -270 140 {}
C {devices/lab_wire.sym} -270 140 2 0 {name=l7 lab=vss}
N 60 -20 20 -20 {}
C {devices/lab_wire.sym} 20 -20 0 0 {name=l8 lab=vinn}
N 60 20 20 20 {}
C {devices/lab_wire.sym} 20 20 0 0 {name=l9 lab=vinp}
N 280 -40 320 -40 {}
C {devices/lab_wire.sym} 320 -40 0 1 {name=l10 lab=foldn}
N 280 0 320 0 {}
C {devices/lab_wire.sym} 320 0 0 1 {name=l11 lab=foldp}
N 280 40 320 40 {}
C {devices/lab_wire.sym} 320 40 0 1 {name=l12 lab=tail}
N 170 -100 170 -140 {}
C {devices/lab_wire.sym} 170 -140 0 1 {name=l13 lab=vdd}
N 500 0 460 0 {}
C {devices/lab_wire.sym} 460 0 0 0 {name=l14 lab=vb2}
N 820 -20 860 -20 {}
C {devices/lab_wire.sym} 860 -20 0 1 {name=l15 lab=cascp}
N 820 20 860 20 {}
C {devices/lab_wire.sym} 860 20 0 1 {name=l16 lab=vout}
N 660 -80 660 -120 {}
C {devices/lab_wire.sym} 660 -120 0 1 {name=l17 lab=vdd}
N -930 310 -930 270 {}
C {devices/lab_wire.sym} -930 270 0 1 {name=l18 lab=vb1}
N -930 370 -930 410 {}
C {devices/lab_wire.sym} -930 410 2 0 {name=l19 lab=vss}
N -930 90 -930 50 {}
C {devices/lab_wire.sym} -930 50 0 1 {name=l20 lab=vb2}
N -930 150 -930 190 {}
C {devices/lab_wire.sym} -930 190 2 0 {name=l21 lab=vss}
N -90 310 -90 270 {}
C {devices/lab_wire.sym} -90 270 0 1 {name=l22 lab=cascp}
N -130 340 -170 340 {}
C {devices/lab_wire.sym} -170 340 0 0 {name=l23 lab=vb1}
N -90 370 -90 410 {}
C {devices/lab_wire.sym} -90 410 2 0 {name=l24 lab=foldp}
N -90 340 -50 340 {}
C {devices/lab_wire.sym} -50 340 0 1 {name=l25 lab=vss}
N 130 310 130 270 {}
C {devices/lab_wire.sym} 130 270 0 1 {name=l26 lab=vout}
N 90 340 50 340 {}
C {devices/lab_wire.sym} 50 340 0 0 {name=l27 lab=vb1}
N 130 370 130 410 {}
C {devices/lab_wire.sym} 130 410 2 0 {name=l28 lab=foldn}
N 130 340 170 340 {}
C {devices/lab_wire.sym} 170 340 0 1 {name=l29 lab=vss}
