v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_013_qu2017_azc} -1910 -580 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -880 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_simple_1.sym} -440 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_2.sym} 0 0 0 0 {name=xcm_pmos_simple_2}
C {blocks/cm_pmos_simple_3.sym} 440 0 0 0 {name=xcm_pmos_simple_3}
C {blocks/dp_pmos_simple_1.sym} 880 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -1650 380 0 0 {name=C0 value='CAPACITOR_0'}
C {devices/capa_np.sym} -1430 380 0 0 {name=C1 value='CAPACITOR_1'}
C {devices/capa_np.sym} -1210 380 0 0 {name=C2 value='CAPACITOR_2'}
C {devices/isource_np.sym} -1870 380 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/res_np.sym} -990 380 0 0 {name=R0 value='RESISTOR_0'}
C {devices/res_np.sym} -770 380 0 0 {name=R1 value='RESISTOR_1'}
C {devices/res_np.sym} -550 380 0 0 {name=R2 value='RESISTOR_2'}
C {devices/res_np.sym} -330 380 0 0 {name=R3 value='RESISTOR_3'}
C {devices/sg13_lv_pmos_np.sym} -110 -380 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} -110 380 0 0 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_pmos_np.sym} 110 -380 0 0 {name=M13 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 110 380 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 330 380 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 550 380 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} 770 380 0 0 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 990 380 0 0 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 1210 380 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_nmos_np.sym} 1430 380 0 0 {name=M23 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_nmos_np.sym} 1650 380 0 0 {name=M24 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
N -770 -80 -730 -80 {}
C {devices/lab_wire.sym} -730 -80 0 1 {name=l0 lab=VB1}
N -770 -40 -730 -40 {}
C {devices/lab_wire.sym} -730 -40 0 1 {name=l1 lab=VB4}
N -770 0 -730 0 {}
C {devices/lab_wire.sym} -730 0 0 1 {name=l2 lab=net019}
N -770 40 -730 40 {}
C {devices/lab_wire.sym} -730 40 0 1 {name=l3 lab=net049}
N -770 80 -730 80 {}
C {devices/lab_wire.sym} -730 80 0 1 {name=l4 lab=net078}
N -880 -140 -880 -180 {}
C {devices/lab_wire.sym} -880 -180 0 1 {name=l5 lab=vdd}
N -330 -40 -290 -40 {}
C {devices/lab_wire.sym} -290 -40 0 1 {name=l6 lab=DM_2}
N -330 0 -290 0 {}
C {devices/lab_wire.sym} -290 0 0 1 {name=l7 lab=VB4}
N -330 40 -290 40 {}
C {devices/lab_wire.sym} -290 40 0 1 {name=l8 lab=net063}
N -440 100 -440 140 {}
C {devices/lab_wire.sym} -440 140 2 0 {name=l9 lab=vss}
N 110 -20 150 -20 {}
C {devices/lab_wire.sym} 150 -20 0 1 {name=l10 lab=VOUTN}
N 110 20 150 20 {}
C {devices/lab_wire.sym} 150 20 0 1 {name=l11 lab=net050}
N 0 -80 0 -120 {}
C {devices/lab_wire.sym} 0 -120 0 1 {name=l12 lab=vdd}
N 550 -20 590 -20 {}
C {devices/lab_wire.sym} 590 -20 0 1 {name=l13 lab=net055}
N 550 20 590 20 {}
C {devices/lab_wire.sym} 590 20 0 1 {name=l14 lab=net057}
N 440 -80 440 -120 {}
C {devices/lab_wire.sym} 440 -120 0 1 {name=l15 lab=vdd}
N 770 -20 730 -20 {}
C {devices/lab_wire.sym} 730 -20 0 0 {name=l16 lab=VINN}
N 770 20 730 20 {}
C {devices/lab_wire.sym} 730 20 0 0 {name=l17 lab=VINP}
N 990 -40 1030 -40 {}
C {devices/lab_wire.sym} 1030 -40 0 1 {name=l18 lab=DM_2}
N 990 0 1030 0 {}
C {devices/lab_wire.sym} 1030 0 0 1 {name=l19 lab=net019}
N 990 40 1030 40 {}
C {devices/lab_wire.sym} 1030 40 0 1 {name=l20 lab=net063}
N -1650 350 -1650 310 {}
C {devices/lab_wire.sym} -1650 310 0 1 {name=l21 lab=net063}
N -1650 410 -1650 450 {}
C {devices/lab_wire.sym} -1650 450 2 0 {name=l22 lab=VOUT}
N -1430 350 -1430 310 {}
C {devices/lab_wire.sym} -1430 310 0 1 {name=l23 lab=net051}
N -1430 410 -1430 450 {}
C {devices/lab_wire.sym} -1430 450 2 0 {name=l24 lab=vss}
N -1210 350 -1210 310 {}
C {devices/lab_wire.sym} -1210 310 0 1 {name=l25 lab=net043}
N -1210 410 -1210 450 {}
C {devices/lab_wire.sym} -1210 450 2 0 {name=l26 lab=vss}
N -1870 350 -1870 310 {}
C {devices/lab_wire.sym} -1870 310 0 1 {name=l27 lab=VB1}
N -1870 410 -1870 450 {}
C {devices/lab_wire.sym} -1870 450 2 0 {name=l28 lab=vss}
N -990 350 -990 310 {}
C {devices/lab_wire.sym} -990 310 0 1 {name=l29 lab=net078}
N -990 410 -990 450 {}
C {devices/lab_wire.sym} -990 450 2 0 {name=l30 lab=net077}
N -770 350 -770 310 {}
C {devices/lab_wire.sym} -770 310 0 1 {name=l31 lab=net078}
N -770 410 -770 450 {}
C {devices/lab_wire.sym} -770 450 2 0 {name=l32 lab=net082}
N -550 350 -550 310 {}
C {devices/lab_wire.sym} -550 310 0 1 {name=l33 lab=net057}
N -550 410 -550 450 {}
C {devices/lab_wire.sym} -550 450 2 0 {name=l34 lab=net051}
N -330 350 -330 310 {}
C {devices/lab_wire.sym} -330 310 0 1 {name=l35 lab=net057}
N -330 410 -330 450 {}
C {devices/lab_wire.sym} -330 450 2 0 {name=l36 lab=net043}
N -90 -350 -90 -310 {}
C {devices/lab_wire.sym} -90 -310 2 0 {name=l37 lab=net094}
N -130 -380 -170 -380 {}
C {devices/lab_wire.sym} -170 -380 0 0 {name=l38 lab=net050}
N -90 -410 -90 -450 {}
C {devices/lab_wire.sym} -90 -450 0 1 {name=l39 lab=vdd}
N -90 -380 -50 -380 {}
C {devices/lab_wire.sym} -50 -380 0 1 {name=l40 lab=vdd}
N -90 350 -90 310 {}
C {devices/lab_wire.sym} -90 310 0 1 {name=l41 lab=net055}
N -130 380 -170 380 {}
C {devices/lab_wire.sym} -170 380 0 0 {name=l42 lab=net094}
N -90 410 -90 450 {}
C {devices/lab_wire.sym} -90 450 2 0 {name=l43 lab=vss}
N -90 380 -50 380 {}
C {devices/lab_wire.sym} -50 380 0 1 {name=l44 lab=vss}
N 130 -350 130 -310 {}
C {devices/lab_wire.sym} 130 -310 2 0 {name=l45 lab=VOUT}
N 90 -380 50 -380 {}
C {devices/lab_wire.sym} 50 -380 0 0 {name=l46 lab=net050}
N 130 -410 130 -450 {}
C {devices/lab_wire.sym} 130 -450 0 1 {name=l47 lab=vdd}
N 130 -380 170 -380 {}
C {devices/lab_wire.sym} 170 -380 0 1 {name=l48 lab=vdd}
N 130 350 130 310 {}
C {devices/lab_wire.sym} 130 310 0 1 {name=l49 lab=VOUTN}
N 90 380 50 380 {}
C {devices/lab_wire.sym} 50 380 0 0 {name=l50 lab=net077}
N 130 410 130 450 {}
C {devices/lab_wire.sym} 130 450 2 0 {name=l51 lab=DM_2}
N 130 380 170 380 {}
C {devices/lab_wire.sym} 170 380 0 1 {name=l52 lab=vss}
N 350 350 350 310 {}
C {devices/lab_wire.sym} 350 310 0 1 {name=l53 lab=net050}
N 310 380 270 380 {}
C {devices/lab_wire.sym} 270 380 0 0 {name=l54 lab=net082}
N 350 410 350 450 {}
C {devices/lab_wire.sym} 350 450 2 0 {name=l55 lab=net063}
N 350 380 390 380 {}
C {devices/lab_wire.sym} 390 380 0 1 {name=l56 lab=vss}
N 570 350 570 310 {}
C {devices/lab_wire.sym} 570 310 0 1 {name=l57 lab=net077}
N 530 380 490 380 {}
C {devices/lab_wire.sym} 490 380 0 0 {name=l58 lab=DM_2}
N 570 410 570 450 {}
C {devices/lab_wire.sym} 570 450 2 0 {name=l59 lab=vss}
N 570 380 610 380 {}
C {devices/lab_wire.sym} 610 380 0 1 {name=l60 lab=vss}
N 790 350 790 310 {}
C {devices/lab_wire.sym} 790 310 0 1 {name=l61 lab=net082}
N 750 380 710 380 {}
C {devices/lab_wire.sym} 710 380 0 0 {name=l62 lab=net063}
N 790 410 790 450 {}
C {devices/lab_wire.sym} 790 450 2 0 {name=l63 lab=vss}
N 790 380 830 380 {}
C {devices/lab_wire.sym} 830 380 0 1 {name=l64 lab=vss}
N 1010 350 1010 310 {}
C {devices/lab_wire.sym} 1010 310 0 1 {name=l65 lab=VOUT}
N 970 380 930 380 {}
C {devices/lab_wire.sym} 930 380 0 0 {name=l66 lab=net049}
N 1010 410 1010 450 {}
C {devices/lab_wire.sym} 1010 450 2 0 {name=l67 lab=vss}
N 1010 380 1050 380 {}
C {devices/lab_wire.sym} 1050 380 0 1 {name=l68 lab=vss}
N 1230 350 1230 310 {}
C {devices/lab_wire.sym} 1230 310 0 1 {name=l69 lab=net094}
N 1190 380 1150 380 {}
C {devices/lab_wire.sym} 1150 380 0 0 {name=l70 lab=net051}
N 1230 410 1230 450 {}
C {devices/lab_wire.sym} 1230 450 2 0 {name=l71 lab=vss}
N 1230 380 1270 380 {}
C {devices/lab_wire.sym} 1270 380 0 1 {name=l72 lab=vss}
N 1450 350 1450 310 {}
C {devices/lab_wire.sym} 1450 310 0 1 {name=l73 lab=net057}
N 1410 380 1370 380 {}
C {devices/lab_wire.sym} 1370 380 0 0 {name=l74 lab=net043}
N 1450 410 1450 450 {}
C {devices/lab_wire.sym} 1450 450 2 0 {name=l75 lab=vss}
N 1450 380 1490 380 {}
C {devices/lab_wire.sym} 1490 380 0 1 {name=l76 lab=vss}
N 1670 350 1670 310 {}
C {devices/lab_wire.sym} 1670 310 0 1 {name=l77 lab=net049}
N 1630 380 1590 380 {}
C {devices/lab_wire.sym} 1590 380 0 0 {name=l78 lab=net057}
N 1670 410 1670 450 {}
C {devices/lab_wire.sym} 1670 450 2 0 {name=l79 lab=vss}
N 1670 380 1710 380 {}
C {devices/lab_wire.sym} 1710 380 0 1 {name=l80 lab=vss}
