v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_016_song_dacfc} -1520 -580 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -1260 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_improved_high_swing_cascode_1.sym} -740 0 0 0 {name=xcm_nmos_improved_high_swing_cascode_1}
C {blocks/cm_pmos_improved_high_swing_cascode_1.sym} -140 0 0 0 {name=xcm_pmos_improved_high_swing_cascode_1}
C {blocks/cm_nmos_simple_1.sym} 380 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_pmos_simple_1.sym} 820 0 0 0 {name=xdp_pmos_simple_1}
C {blocks/dp_pmos_simple_2.sym} 1260 0 0 0 {name=xdp_pmos_simple_2}
C {devices/capa_np.sym} -660 380 0 0 {name=C0 value='CAPACITOR_0'}
C {devices/capa_np.sym} -440 380 0 0 {name=C2 value='CAPACITOR_1'}
C {devices/isource_np.sym} -1480 380 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/sg13_lv_pmos_np.sym} -220 -380 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 0 -380 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} -220 380 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 0 380 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} 220 380 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_nmos_np.sym} 440 380 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 660 380 0 0 {name=M23 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_pmos_np.sym} 220 -380 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -1150 -80 -1110 -80 {}
C {devices/lab_wire.sym} -1110 -80 0 1 {name=l0 lab=VB3}
N -1150 -40 -1110 -40 {}
C {devices/lab_wire.sym} -1110 -40 0 1 {name=l1 lab=VB4}
N -1150 0 -1110 0 {}
C {devices/lab_wire.sym} -1110 0 0 1 {name=l2 lab=net013}
N -1150 40 -1110 40 {}
C {devices/lab_wire.sym} -1110 40 0 1 {name=l3 lab=net1}
N -1150 80 -1110 80 {}
C {devices/lab_wire.sym} -1110 80 0 1 {name=l4 lab=net31}
N -1260 -140 -1260 -180 {}
C {devices/lab_wire.sym} -1260 -180 0 1 {name=l5 lab=vdd}
N -550 -80 -510 -80 {}
C {devices/lab_wire.sym} -510 -80 0 1 {name=l6 lab=DM_1}
N -550 -40 -510 -40 {}
C {devices/lab_wire.sym} -510 -40 0 1 {name=l7 lab=VB3}
N -550 0 -510 0 {}
C {devices/lab_wire.sym} -510 0 0 1 {name=l8 lab=VB4}
N -550 40 -510 40 {}
C {devices/lab_wire.sym} -510 40 0 1 {name=l9 lab=VOUTN}
N -550 80 -510 80 {}
C {devices/lab_wire.sym} -510 80 0 1 {name=l10 lab=net70}
N -740 140 -740 180 {}
C {devices/lab_wire.sym} -740 180 2 0 {name=l11 lab=vss}
N 50 -60 90 -60 {}
C {devices/lab_wire.sym} 90 -60 0 1 {name=l12 lab=DM_1}
N 50 -20 90 -20 {}
C {devices/lab_wire.sym} 90 -20 0 1 {name=l13 lab=VOUTN}
N 50 20 90 20 {}
C {devices/lab_wire.sym} 90 20 0 1 {name=l14 lab=net4}
N 50 60 90 60 {}
C {devices/lab_wire.sym} 90 60 0 1 {name=l15 lab=net70}
N -140 -120 -140 -160 {}
C {devices/lab_wire.sym} -140 -160 0 1 {name=l16 lab=vdd}
N 490 -20 530 -20 {}
C {devices/lab_wire.sym} 530 -20 0 1 {name=l17 lab=net043}
N 490 20 530 20 {}
C {devices/lab_wire.sym} 530 20 0 1 {name=l18 lab=net049}
N 380 80 380 120 {}
C {devices/lab_wire.sym} 380 120 2 0 {name=l19 lab=vss}
N 710 -20 670 -20 {}
C {devices/lab_wire.sym} 670 -20 0 0 {name=l20 lab=VINN}
N 710 20 670 20 {}
C {devices/lab_wire.sym} 670 20 0 0 {name=l21 lab=VINP}
N 930 -40 970 -40 {}
C {devices/lab_wire.sym} 970 -40 0 1 {name=l22 lab=net043}
N 930 0 970 0 {}
C {devices/lab_wire.sym} 970 0 0 1 {name=l23 lab=net049}
N 930 40 970 40 {}
C {devices/lab_wire.sym} 970 40 0 1 {name=l24 lab=net1}
N 1150 -20 1110 -20 {}
C {devices/lab_wire.sym} 1110 -20 0 0 {name=l25 lab=VINN}
N 1150 20 1110 20 {}
C {devices/lab_wire.sym} 1110 20 0 0 {name=l26 lab=VINP}
N 1370 -40 1410 -40 {}
C {devices/lab_wire.sym} 1410 -40 0 1 {name=l27 lab=DM_2}
N 1370 0 1410 0 {}
C {devices/lab_wire.sym} 1410 0 0 1 {name=l28 lab=net063}
N 1370 40 1410 40 {}
C {devices/lab_wire.sym} 1410 40 0 1 {name=l29 lab=net31}
N -660 350 -660 310 {}
C {devices/lab_wire.sym} -660 310 0 1 {name=l30 lab=VOUT}
N -660 410 -660 450 {}
C {devices/lab_wire.sym} -660 450 2 0 {name=l31 lab=net70}
N -440 350 -440 310 {}
C {devices/lab_wire.sym} -440 310 0 1 {name=l32 lab=net4}
N -440 410 -440 450 {}
C {devices/lab_wire.sym} -440 450 2 0 {name=l33 lab=vss}
N -1480 350 -1480 310 {}
C {devices/lab_wire.sym} -1480 310 0 1 {name=l34 lab=net013}
N -1480 410 -1480 450 {}
C {devices/lab_wire.sym} -1480 450 2 0 {name=l35 lab=vss}
N -200 -350 -200 -310 {}
C {devices/lab_wire.sym} -200 -310 2 0 {name=l36 lab=net043}
N -240 -380 -280 -380 {}
C {devices/lab_wire.sym} -280 -380 0 0 {name=l37 lab=net4}
N -200 -410 -200 -450 {}
C {devices/lab_wire.sym} -200 -450 0 1 {name=l38 lab=vdd}
N -200 -380 -160 -380 {}
C {devices/lab_wire.sym} -160 -380 0 1 {name=l39 lab=vdd}
N 20 -350 20 -310 {}
C {devices/lab_wire.sym} 20 -310 2 0 {name=l40 lab=VOUT}
N -20 -380 -60 -380 {}
C {devices/lab_wire.sym} -60 -380 0 0 {name=l41 lab=net4}
N 20 -410 20 -450 {}
C {devices/lab_wire.sym} 20 -450 0 1 {name=l42 lab=vdd}
N 20 -380 60 -380 {}
C {devices/lab_wire.sym} 60 -380 0 1 {name=l43 lab=vdd}
N -200 350 -200 310 {}
C {devices/lab_wire.sym} -200 310 0 1 {name=l44 lab=VOUTN}
N -240 380 -280 380 {}
C {devices/lab_wire.sym} -280 380 0 0 {name=l45 lab=VB3}
N -200 410 -200 450 {}
C {devices/lab_wire.sym} -200 450 2 0 {name=l46 lab=DM_2}
N -200 380 -160 380 {}
C {devices/lab_wire.sym} -160 380 0 1 {name=l47 lab=vss}
N 20 350 20 310 {}
C {devices/lab_wire.sym} 20 310 0 1 {name=l48 lab=net4}
N -20 380 -60 380 {}
C {devices/lab_wire.sym} -60 380 0 0 {name=l49 lab=VB3}
N 20 410 20 450 {}
C {devices/lab_wire.sym} 20 450 2 0 {name=l50 lab=net063}
N 20 380 60 380 {}
C {devices/lab_wire.sym} 60 380 0 1 {name=l51 lab=vss}
N 240 350 240 310 {}
C {devices/lab_wire.sym} 240 310 0 1 {name=l52 lab=DM_2}
N 200 380 160 380 {}
C {devices/lab_wire.sym} 160 380 0 0 {name=l53 lab=VB4}
N 240 410 240 450 {}
C {devices/lab_wire.sym} 240 450 2 0 {name=l54 lab=vss}
N 240 380 280 380 {}
C {devices/lab_wire.sym} 280 380 0 1 {name=l55 lab=vss}
N 460 350 460 310 {}
C {devices/lab_wire.sym} 460 310 0 1 {name=l56 lab=net063}
N 420 380 380 380 {}
C {devices/lab_wire.sym} 380 380 0 0 {name=l57 lab=VB4}
N 460 410 460 450 {}
C {devices/lab_wire.sym} 460 450 2 0 {name=l58 lab=vss}
N 460 380 500 380 {}
C {devices/lab_wire.sym} 500 380 0 1 {name=l59 lab=vss}
N 680 350 680 310 {}
C {devices/lab_wire.sym} 680 310 0 1 {name=l60 lab=VOUT}
N 640 380 600 380 {}
C {devices/lab_wire.sym} 600 380 0 0 {name=l61 lab=net049}
N 680 410 680 450 {}
C {devices/lab_wire.sym} 680 450 2 0 {name=l62 lab=vss}
N 680 380 720 380 {}
C {devices/lab_wire.sym} 720 380 0 1 {name=l63 lab=vss}
N 240 -350 240 -310 {}
C {devices/lab_wire.sym} 240 -310 2 0 {name=l64 lab=net049}
N 200 -380 160 -380 {}
C {devices/lab_wire.sym} 160 -380 0 0 {name=l65 lab=VOUTN}
N 240 -410 240 -450 {}
C {devices/lab_wire.sym} 240 -450 0 1 {name=l66 lab=vdd}
N 240 -380 280 -380 {}
C {devices/lab_wire.sym} 280 -380 0 1 {name=l67 lab=vdd}
