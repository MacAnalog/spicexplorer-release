v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_012_peng_tcfc} -1220 -580 0 0 0.4 0.4 {}
C {blocks/cm_nmos_improved_high_swing_cascode_1.sym} -960 0 0 0 {name=xcm_nmos_improved_high_swing_cascode_1}
C {blocks/cm_pmos_simple_1.sym} -440 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_pmos_improved_high_swing_cascode_1.sym} 80 0 0 0 {name=xcm_pmos_improved_high_swing_cascode_1}
C {blocks/cm_nmos_simple_1.sym} 600 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_pmos_simple_1.sym} 1040 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -660 380 0 0 {name=C0 value='CAPACITOR_0'}
C {devices/capa_np.sym} -440 380 0 0 {name=C1 value='CAPACITOR_1'}
C {devices/isource_np.sym} -1180 380 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/sg13_lv_pmos_np.sym} -440 -380 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} -220 -380 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} -220 380 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 0 380 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} 220 380 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_nmos_np.sym} 440 380 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 660 380 0 0 {name=M23 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_pmos_np.sym} 0 -380 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 220 -380 0 0 {name=M66 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm66_w l=x_dut_xm66_l m=x_dut_xm66_m}
C {devices/sg13_lv_pmos_np.sym} 440 -380 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -770 -60 -730 -60 {}
C {devices/lab_wire.sym} -730 -60 0 1 {name=l0 lab=VB2}
N -770 -20 -730 -20 {}
C {devices/lab_wire.sym} -730 -20 0 1 {name=l1 lab=VB3}
N -770 20 -730 20 {}
C {devices/lab_wire.sym} -730 20 0 1 {name=l2 lab=VB4}
N -770 60 -730 60 {}
C {devices/lab_wire.sym} -730 60 0 1 {name=l3 lab=net7}
N -960 120 -960 160 {}
C {devices/lab_wire.sym} -960 160 2 0 {name=l4 lab=vss}
N -330 -20 -290 -20 {}
C {devices/lab_wire.sym} -290 -20 0 1 {name=l5 lab=VOUTN}
N -330 20 -290 20 {}
C {devices/lab_wire.sym} -290 20 0 1 {name=l6 lab=VOUTP}
N -440 -80 -440 -120 {}
C {devices/lab_wire.sym} -440 -120 0 1 {name=l7 lab=vdd}
N 270 -80 310 -80 {}
C {devices/lab_wire.sym} 310 -80 0 1 {name=l8 lab=VB1}
N 270 -40 310 -40 {}
C {devices/lab_wire.sym} 310 -40 0 1 {name=l9 lab=VB2}
N 270 0 310 0 {}
C {devices/lab_wire.sym} 310 0 0 1 {name=l10 lab=VB3}
N 270 40 310 40 {}
C {devices/lab_wire.sym} 310 40 0 1 {name=l11 lab=VB4}
N 270 80 310 80 {}
C {devices/lab_wire.sym} 310 80 0 1 {name=l12 lab=net7}
N 80 -140 80 -180 {}
C {devices/lab_wire.sym} 80 -180 0 1 {name=l13 lab=vdd}
N 710 -20 750 -20 {}
C {devices/lab_wire.sym} 750 -20 0 1 {name=l14 lab=net043}
N 710 20 750 20 {}
C {devices/lab_wire.sym} 750 20 0 1 {name=l15 lab=net10}
N 600 80 600 120 {}
C {devices/lab_wire.sym} 600 120 2 0 {name=l16 lab=vss}
N 930 -20 890 -20 {}
C {devices/lab_wire.sym} 890 -20 0 0 {name=l17 lab=VINN}
N 930 20 890 20 {}
C {devices/lab_wire.sym} 890 20 0 0 {name=l18 lab=VINP}
N 1150 -40 1190 -40 {}
C {devices/lab_wire.sym} 1190 -40 0 1 {name=l19 lab=DM_2}
N 1150 0 1190 0 {}
C {devices/lab_wire.sym} 1190 0 0 1 {name=l20 lab=net063}
N 1150 40 1190 40 {}
C {devices/lab_wire.sym} 1190 40 0 1 {name=l21 lab=net31}
N -660 350 -660 310 {}
C {devices/lab_wire.sym} -660 310 0 1 {name=l22 lab=VOUTP}
N -660 410 -660 450 {}
C {devices/lab_wire.sym} -660 450 2 0 {name=l23 lab=VOUT}
N -440 350 -440 310 {}
C {devices/lab_wire.sym} -440 310 0 1 {name=l24 lab=net049}
N -440 410 -440 450 {}
C {devices/lab_wire.sym} -440 450 2 0 {name=l25 lab=VOUT}
N -1180 350 -1180 310 {}
C {devices/lab_wire.sym} -1180 310 0 1 {name=l26 lab=VB1}
N -1180 410 -1180 450 {}
C {devices/lab_wire.sym} -1180 450 2 0 {name=l27 lab=vss}
N -420 -350 -420 -310 {}
C {devices/lab_wire.sym} -420 -310 2 0 {name=l28 lab=net043}
N -460 -380 -500 -380 {}
C {devices/lab_wire.sym} -500 -380 0 0 {name=l29 lab=VOUTP}
N -420 -410 -420 -450 {}
C {devices/lab_wire.sym} -420 -450 0 1 {name=l30 lab=vdd}
N -420 -380 -380 -380 {}
C {devices/lab_wire.sym} -380 -380 0 1 {name=l31 lab=vdd}
N -200 -350 -200 -310 {}
C {devices/lab_wire.sym} -200 -310 2 0 {name=l32 lab=VOUT}
N -240 -380 -280 -380 {}
C {devices/lab_wire.sym} -280 -380 0 0 {name=l33 lab=VOUTP}
N -200 -410 -200 -450 {}
C {devices/lab_wire.sym} -200 -450 0 1 {name=l34 lab=vdd}
N -200 -380 -160 -380 {}
C {devices/lab_wire.sym} -160 -380 0 1 {name=l35 lab=vdd}
N -200 350 -200 310 {}
C {devices/lab_wire.sym} -200 310 0 1 {name=l36 lab=VOUTN}
N -240 380 -280 380 {}
C {devices/lab_wire.sym} -280 380 0 0 {name=l37 lab=VB3}
N -200 410 -200 450 {}
C {devices/lab_wire.sym} -200 450 2 0 {name=l38 lab=DM_2}
N -200 380 -160 380 {}
C {devices/lab_wire.sym} -160 380 0 1 {name=l39 lab=vss}
N 20 350 20 310 {}
C {devices/lab_wire.sym} 20 310 0 1 {name=l40 lab=VOUTP}
N -20 380 -60 380 {}
C {devices/lab_wire.sym} -60 380 0 0 {name=l41 lab=VB3}
N 20 410 20 450 {}
C {devices/lab_wire.sym} 20 450 2 0 {name=l42 lab=net063}
N 20 380 60 380 {}
C {devices/lab_wire.sym} 60 380 0 1 {name=l43 lab=vss}
N 240 350 240 310 {}
C {devices/lab_wire.sym} 240 310 0 1 {name=l44 lab=DM_2}
N 200 380 160 380 {}
C {devices/lab_wire.sym} 160 380 0 0 {name=l45 lab=VB4}
N 240 410 240 450 {}
C {devices/lab_wire.sym} 240 450 2 0 {name=l46 lab=vss}
N 240 380 280 380 {}
C {devices/lab_wire.sym} 280 380 0 1 {name=l47 lab=vss}
N 460 350 460 310 {}
C {devices/lab_wire.sym} 460 310 0 1 {name=l48 lab=net063}
N 420 380 380 380 {}
C {devices/lab_wire.sym} 380 380 0 0 {name=l49 lab=VB4}
N 460 410 460 450 {}
C {devices/lab_wire.sym} 460 450 2 0 {name=l50 lab=vss}
N 460 380 500 380 {}
C {devices/lab_wire.sym} 500 380 0 1 {name=l51 lab=vss}
N 680 350 680 310 {}
C {devices/lab_wire.sym} 680 310 0 1 {name=l52 lab=VOUT}
N 640 380 600 380 {}
C {devices/lab_wire.sym} 600 380 0 0 {name=l53 lab=net10}
N 680 410 680 450 {}
C {devices/lab_wire.sym} 680 450 2 0 {name=l54 lab=vss}
N 680 380 720 380 {}
C {devices/lab_wire.sym} 720 380 0 1 {name=l55 lab=vss}
N 20 -350 20 -310 {}
C {devices/lab_wire.sym} 20 -310 2 0 {name=l56 lab=net31}
N -20 -380 -60 -380 {}
C {devices/lab_wire.sym} -60 -380 0 0 {name=l57 lab=VB1}
N 20 -410 20 -450 {}
C {devices/lab_wire.sym} 20 -450 0 1 {name=l58 lab=vdd}
N 20 -380 60 -380 {}
C {devices/lab_wire.sym} 60 -380 0 1 {name=l59 lab=vdd}
N 240 -350 240 -310 {}
C {devices/lab_wire.sym} 240 -310 2 0 {name=l60 lab=net10}
N 200 -380 160 -380 {}
C {devices/lab_wire.sym} 160 -380 0 0 {name=l61 lab=VB2}
N 240 -410 240 -450 {}
C {devices/lab_wire.sym} 240 -450 0 1 {name=l62 lab=net049}
N 240 -380 280 -380 {}
C {devices/lab_wire.sym} 280 -380 0 1 {name=l63 lab=vdd}
N 460 -350 460 -310 {}
C {devices/lab_wire.sym} 460 -310 2 0 {name=l64 lab=net049}
N 420 -380 380 -380 {}
C {devices/lab_wire.sym} 380 -380 0 0 {name=l65 lab=VB1}
N 460 -410 460 -450 {}
C {devices/lab_wire.sym} 460 -450 0 1 {name=l66 lab=vdd}
N 460 -380 500 -380 {}
C {devices/lab_wire.sym} 500 -380 0 1 {name=l67 lab=vdd}
