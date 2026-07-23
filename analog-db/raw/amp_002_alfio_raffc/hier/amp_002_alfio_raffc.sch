v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_002_alfio_raffc} -1220 -580 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -960 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_improved_high_swing_cascode_1.sym} -440 0 0 0 {name=xcm_nmos_improved_high_swing_cascode_1}
C {blocks/cm_nmos_simple_1.sym} 80 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_2.sym} 520 0 0 0 {name=xcm_pmos_simple_2}
C {blocks/dp_pmos_simple_1.sym} 960 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -660 380 0 0 {name=C0 value='CAPACITOR_0'}
C {devices/capa_np.sym} -440 380 0 0 {name=C1 value='CAPACITOR_1'}
C {devices/isource_np.sym} -1180 380 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/sg13_lv_pmos_np.sym} -220 -380 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 0 -380 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} -220 380 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 0 380 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} 220 380 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_nmos_np.sym} 440 380 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 660 380 0 0 {name=M59 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm59_w l=x_dut_xm59_l m=x_dut_xm59_m}
C {devices/sg13_lv_pmos_np.sym} 220 -380 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
N -850 -80 -810 -80 {}
C {devices/lab_wire.sym} -810 -80 0 1 {name=l0 lab=DM_1}
N -850 -40 -810 -40 {}
C {devices/lab_wire.sym} -810 -40 0 1 {name=l1 lab=VB3}
N -850 0 -810 0 {}
C {devices/lab_wire.sym} -810 0 0 1 {name=l2 lab=VB4}
N -850 40 -810 40 {}
C {devices/lab_wire.sym} -810 40 0 1 {name=l3 lab=net1}
N -850 80 -810 80 {}
C {devices/lab_wire.sym} -810 80 0 1 {name=l4 lab=net31}
N -960 -140 -960 -180 {}
C {devices/lab_wire.sym} -960 -180 0 1 {name=l5 lab=vdd}
N -250 -40 -210 -40 {}
C {devices/lab_wire.sym} -210 -40 0 1 {name=l6 lab=DM_1}
N -250 0 -210 0 {}
C {devices/lab_wire.sym} -210 0 0 1 {name=l7 lab=VB3}
N -250 40 -210 40 {}
C {devices/lab_wire.sym} -210 40 0 1 {name=l8 lab=VB4}
N -440 100 -440 140 {}
C {devices/lab_wire.sym} -440 140 2 0 {name=l9 lab=vss}
N 190 -20 230 -20 {}
C {devices/lab_wire.sym} 230 -20 0 1 {name=l10 lab=VOUT}
N 190 20 230 20 {}
C {devices/lab_wire.sym} 230 20 0 1 {name=l11 lab=net043}
N 80 80 80 120 {}
C {devices/lab_wire.sym} 80 120 2 0 {name=l12 lab=vss}
N 630 -20 670 -20 {}
C {devices/lab_wire.sym} 670 -20 0 1 {name=l13 lab=VOUTN}
N 630 20 670 20 {}
C {devices/lab_wire.sym} 670 20 0 1 {name=l14 lab=net050}
N 520 -80 520 -120 {}
C {devices/lab_wire.sym} 520 -120 0 1 {name=l15 lab=vdd}
N 850 -20 810 -20 {}
C {devices/lab_wire.sym} 810 -20 0 0 {name=l16 lab=VINN}
N 850 20 810 20 {}
C {devices/lab_wire.sym} 810 20 0 0 {name=l17 lab=VINP}
N 1070 -40 1110 -40 {}
C {devices/lab_wire.sym} 1110 -40 0 1 {name=l18 lab=DM_2}
N 1070 0 1110 0 {}
C {devices/lab_wire.sym} 1110 0 0 1 {name=l19 lab=net063}
N 1070 40 1110 40 {}
C {devices/lab_wire.sym} 1110 40 0 1 {name=l20 lab=net31}
N -660 350 -660 310 {}
C {devices/lab_wire.sym} -660 310 0 1 {name=l21 lab=net063}
N -660 410 -660 450 {}
C {devices/lab_wire.sym} -660 450 2 0 {name=l22 lab=VOUT}
N -440 350 -440 310 {}
C {devices/lab_wire.sym} -440 310 0 1 {name=l23 lab=net050}
N -440 410 -440 450 {}
C {devices/lab_wire.sym} -440 450 2 0 {name=l24 lab=net013}
N -1180 350 -1180 310 {}
C {devices/lab_wire.sym} -1180 310 0 1 {name=l25 lab=net1}
N -1180 410 -1180 450 {}
C {devices/lab_wire.sym} -1180 450 2 0 {name=l26 lab=vss}
N -200 -350 -200 -310 {}
C {devices/lab_wire.sym} -200 -310 2 0 {name=l27 lab=net013}
N -240 -380 -280 -380 {}
C {devices/lab_wire.sym} -280 -380 0 0 {name=l28 lab=net050}
N -200 -410 -200 -450 {}
C {devices/lab_wire.sym} -200 -450 0 1 {name=l29 lab=vdd}
N -200 -380 -160 -380 {}
C {devices/lab_wire.sym} -160 -380 0 1 {name=l30 lab=vdd}
N 20 -350 20 -310 {}
C {devices/lab_wire.sym} 20 -310 2 0 {name=l31 lab=VOUT}
N -20 -380 -60 -380 {}
C {devices/lab_wire.sym} -60 -380 0 0 {name=l32 lab=net050}
N 20 -410 20 -450 {}
C {devices/lab_wire.sym} 20 -450 0 1 {name=l33 lab=vdd}
N 20 -380 60 -380 {}
C {devices/lab_wire.sym} 60 -380 0 1 {name=l34 lab=vdd}
N -200 350 -200 310 {}
C {devices/lab_wire.sym} -200 310 0 1 {name=l35 lab=VOUTN}
N -240 380 -280 380 {}
C {devices/lab_wire.sym} -280 380 0 0 {name=l36 lab=VB3}
N -200 410 -200 450 {}
C {devices/lab_wire.sym} -200 450 2 0 {name=l37 lab=DM_2}
N -200 380 -160 380 {}
C {devices/lab_wire.sym} -160 380 0 1 {name=l38 lab=vss}
N 20 350 20 310 {}
C {devices/lab_wire.sym} 20 310 0 1 {name=l39 lab=net050}
N -20 380 -60 380 {}
C {devices/lab_wire.sym} -60 380 0 0 {name=l40 lab=VB3}
N 20 410 20 450 {}
C {devices/lab_wire.sym} 20 450 2 0 {name=l41 lab=net063}
N 20 380 60 380 {}
C {devices/lab_wire.sym} 60 380 0 1 {name=l42 lab=vss}
N 240 350 240 310 {}
C {devices/lab_wire.sym} 240 310 0 1 {name=l43 lab=DM_2}
N 200 380 160 380 {}
C {devices/lab_wire.sym} 160 380 0 0 {name=l44 lab=VB4}
N 240 410 240 450 {}
C {devices/lab_wire.sym} 240 450 2 0 {name=l45 lab=vss}
N 240 380 280 380 {}
C {devices/lab_wire.sym} 280 380 0 1 {name=l46 lab=vss}
N 460 350 460 310 {}
C {devices/lab_wire.sym} 460 310 0 1 {name=l47 lab=net063}
N 420 380 380 380 {}
C {devices/lab_wire.sym} 380 380 0 0 {name=l48 lab=VB4}
N 460 410 460 450 {}
C {devices/lab_wire.sym} 460 450 2 0 {name=l49 lab=vss}
N 460 380 500 380 {}
C {devices/lab_wire.sym} 500 380 0 1 {name=l50 lab=vss}
N 680 350 680 310 {}
C {devices/lab_wire.sym} 680 310 0 1 {name=l51 lab=net013}
N 640 380 600 380 {}
C {devices/lab_wire.sym} 600 380 0 0 {name=l52 lab=VB4}
N 680 410 680 450 {}
C {devices/lab_wire.sym} 680 450 2 0 {name=l53 lab=vss}
N 680 380 720 380 {}
C {devices/lab_wire.sym} 720 380 0 1 {name=l54 lab=vss}
N 240 -350 240 -310 {}
C {devices/lab_wire.sym} 240 -310 2 0 {name=l55 lab=net043}
N 200 -380 160 -380 {}
C {devices/lab_wire.sym} 160 -380 0 0 {name=l56 lab=net013}
N 240 -410 240 -450 {}
C {devices/lab_wire.sym} 240 -450 0 1 {name=l57 lab=vdd}
N 240 -380 280 -380 {}
C {devices/lab_wire.sym} 280 -380 0 1 {name=l58 lab=vdd}
