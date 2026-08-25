v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_001_analoggym_basic} -1220 -620 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -960 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_improved_high_swing_cascode_1.sym} -440 0 0 0 {name=xcm_nmos_improved_high_swing_cascode_1}
C {blocks/cm_nmos_simple_1.sym} 80 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_2.sym} 520 0 0 0 {name=xcm_pmos_simple_2}
C {blocks/dp_pmos_simple_1.sym} 960 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -770 420 0 0 {name=C0 value='c_comp'}
C {devices/isource_np.sym} -1180 420 0 0 {name=IBIAS value="dc {i_bias}"}
C {devices/res_np.sym} -550 420 0 0 {name=R1 value='r_top'}
C {devices/res_np.sym} -330 420 0 0 {name=R2 value='r_bot'}
C {devices/vsource_np.sym} -1180 200 0 0 {name=VLP value="dc 0"}
C {devices/vsource_np.sym} -1180 -20 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_pmos_np.sym} -110 420 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 0 -420 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} 110 420 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 330 420 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} 550 420 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_nmos_np.sym} 770 420 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
N -850 -120 -850 -160 {}
C {devices/lab_wire.sym} -850 -160 0 1 {name=l0 lab=dm_1}
N -850 -80 -810 -80 {}
C {devices/lab_wire.sym} -810 -80 0 1 {name=l1 lab=ib}
N -850 -40 -810 -40 {}
C {devices/lab_wire.sym} -810 -40 0 1 {name=l2 lab=net1}
N -850 0 -810 0 {}
C {devices/lab_wire.sym} -810 0 0 1 {name=l3 lab=net20}
N -850 40 -810 40 {}
C {devices/lab_wire.sym} -810 40 0 1 {name=l4 lab=net7}
N -850 80 -810 80 {}
C {devices/lab_wire.sym} -810 80 0 1 {name=l5 lab=vb3}
N -850 120 -850 160 {}
C {devices/lab_wire.sym} -850 160 2 0 {name=l6 lab=vb4}
N -960 -180 -960 -220 {}
C {devices/lab_wire.sym} -960 -220 0 1 {name=l7 lab=vdd}
N -250 -40 -210 -40 {}
C {devices/lab_wire.sym} -210 -40 0 1 {name=l8 lab=dm_1}
N -250 0 -210 0 {}
C {devices/lab_wire.sym} -210 0 0 1 {name=l9 lab=vb3}
N -250 40 -210 40 {}
C {devices/lab_wire.sym} -210 40 0 1 {name=l10 lab=vb4}
N -440 100 -440 140 {}
C {devices/lab_wire.sym} -440 140 2 0 {name=l11 lab=vss}
N 190 -20 230 -20 {}
C {devices/lab_wire.sym} 230 -20 0 1 {name=l12 lab=net12}
N 190 20 230 20 {}
C {devices/lab_wire.sym} 230 20 0 1 {name=l13 lab=net7}
N 80 80 80 120 {}
C {devices/lab_wire.sym} 80 120 2 0 {name=l14 lab=vss}
N 630 -20 670 -20 {}
C {devices/lab_wire.sym} 670 -20 0 1 {name=l15 lab=net10}
N 630 20 670 20 {}
C {devices/lab_wire.sym} 670 20 0 1 {name=l16 lab=voutn}
N 520 -80 520 -120 {}
C {devices/lab_wire.sym} 520 -120 0 1 {name=l17 lab=vdd}
N 850 -20 810 -20 {}
C {devices/lab_wire.sym} 810 -20 0 0 {name=l18 lab=vfb}
N 850 20 810 20 {}
C {devices/lab_wire.sym} 810 20 0 0 {name=l19 lab=vref}
N 1070 -40 1110 -40 {}
C {devices/lab_wire.sym} 1110 -40 0 1 {name=l20 lab=dm_2}
N 1070 0 1110 0 {}
C {devices/lab_wire.sym} 1110 0 0 1 {name=l21 lab=net106}
N 1070 40 1110 40 {}
C {devices/lab_wire.sym} 1110 40 0 1 {name=l22 lab=net20}
N -770 390 -770 350 {}
C {devices/lab_wire.sym} -770 350 0 1 {name=l23 lab=net106}
N -770 450 -770 490 {}
C {devices/lab_wire.sym} -770 490 2 0 {name=l24 lab=vout}
N -1180 390 -1180 350 {}
C {devices/lab_wire.sym} -1180 350 0 1 {name=l25 lab=ib}
N -1180 450 -1180 490 {}
C {devices/lab_wire.sym} -1180 490 2 0 {name=l26 lab=vss}
N -550 390 -550 350 {}
C {devices/lab_wire.sym} -550 350 0 1 {name=l27 lab=lp_brk}
N -550 450 -550 490 {}
C {devices/lab_wire.sym} -550 490 2 0 {name=l28 lab=vfb}
N -330 390 -330 350 {}
C {devices/lab_wire.sym} -330 350 0 1 {name=l29 lab=vfb}
N -330 450 -330 490 {}
C {devices/lab_wire.sym} -330 490 2 0 {name=l30 lab=vss}
N -1180 170 -1180 130 {}
C {devices/lab_wire.sym} -1180 130 0 1 {name=l31 lab=lp_brk}
N -1180 230 -1180 270 {}
C {devices/lab_wire.sym} -1180 270 2 0 {name=l32 lab=vout}
N -1180 -50 -1180 -90 {}
C {devices/lab_wire.sym} -1180 -90 0 1 {name=l33 lab=vref}
N -1180 10 -1180 50 {}
C {devices/lab_wire.sym} -1180 50 2 0 {name=l34 lab=vss}
N -90 450 -90 490 {}
C {devices/lab_wire.sym} -90 490 2 0 {name=l35 lab=net12}
N -130 420 -170 420 {}
C {devices/lab_wire.sym} -170 420 0 0 {name=l36 lab=net10}
N -90 390 -90 350 {}
C {devices/lab_wire.sym} -90 350 0 1 {name=l37 lab=net1}
N -90 420 -50 420 {}
C {devices/lab_wire.sym} -50 420 0 1 {name=l38 lab=net1}
N 20 -390 20 -350 {}
C {devices/lab_wire.sym} 20 -350 2 0 {name=l39 lab=vout}
N -20 -420 -60 -420 {}
C {devices/lab_wire.sym} -60 -420 0 0 {name=l40 lab=net1}
N 20 -450 20 -490 {}
C {devices/lab_wire.sym} 20 -490 0 1 {name=l41 lab=vdd}
N 20 -420 60 -420 {}
C {devices/lab_wire.sym} 60 -420 0 1 {name=l42 lab=vdd}
N 130 390 130 350 {}
C {devices/lab_wire.sym} 130 350 0 1 {name=l43 lab=voutn}
N 90 420 50 420 {}
C {devices/lab_wire.sym} 50 420 0 0 {name=l44 lab=vb3}
N 130 450 130 490 {}
C {devices/lab_wire.sym} 130 490 2 0 {name=l45 lab=dm_2}
N 130 420 170 420 {}
C {devices/lab_wire.sym} 170 420 0 1 {name=l46 lab=vss}
N 350 390 350 350 {}
C {devices/lab_wire.sym} 350 350 0 1 {name=l47 lab=net10}
N 310 420 270 420 {}
C {devices/lab_wire.sym} 270 420 0 0 {name=l48 lab=vb3}
N 350 450 350 490 {}
C {devices/lab_wire.sym} 350 490 2 0 {name=l49 lab=net106}
N 350 420 390 420 {}
C {devices/lab_wire.sym} 390 420 0 1 {name=l50 lab=vss}
N 570 390 570 350 {}
C {devices/lab_wire.sym} 570 350 0 1 {name=l51 lab=dm_2}
N 530 420 490 420 {}
C {devices/lab_wire.sym} 490 420 0 0 {name=l52 lab=vb4}
N 570 450 570 490 {}
C {devices/lab_wire.sym} 570 490 2 0 {name=l53 lab=vss}
N 570 420 610 420 {}
C {devices/lab_wire.sym} 610 420 0 1 {name=l54 lab=vss}
N 790 390 790 350 {}
C {devices/lab_wire.sym} 790 350 0 1 {name=l55 lab=net106}
N 750 420 710 420 {}
C {devices/lab_wire.sym} 710 420 0 0 {name=l56 lab=vb4}
N 790 450 790 490 {}
C {devices/lab_wire.sym} 790 490 2 0 {name=l57 lab=vss}
N 790 420 830 420 {}
C {devices/lab_wire.sym} 830 420 0 1 {name=l58 lab=vss}
