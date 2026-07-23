v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sw_003_binary_capbank} -1170 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 660 0 1 0 {name=C1 value='Cu' m=x_dut_c1_m}
C {devices/capa_np.sym} -970 0 0 0 {name=C2 value='Cu' m=x_dut_c2_m}
C {devices/capa_np.sym} 820 0 0 0 {name=C3 value='Cu' m=x_dut_c3_m}
C {devices/capa_np.sym} -1130 0 0 0 {name=C4 value='Cu' m=x_dut_c4_m}
C {devices/sg13_lv_nmos_np.sym} 195 0 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -270 0 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_nmos_np.sym} 1500 0 0 0 {name=M11 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} 2100 0 0 0 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_pmos_np.sym} -65 0 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1245 0 0 0 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 985 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 450 0 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} -765 0 0 1 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} 1895 0 0 0 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 1685 0 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_nmos_np.sym} -575 0 0 1 {name=M9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1130 -90 -1130 -30 {}
N -1130 30 -1130 90 {}
N -970 -60 -970 -30 {}
N -970 30 -970 90 {}
N -845 0 -845 94 {}
N -785 -90 -785 -30 {}
N -785 30 -785 90 {}
N -745 0 -745 60 {}
N -655 0 -655 94 {}
N -595 -90 -595 -30 {}
N -595 30 -595 90 {}
N -555 0 -555 60 {}
N -350 0 -350 94 {}
N -290 -90 -290 -30 {}
N -290 30 -290 90 {}
N -250 0 -250 60 {}
N -145 0 -145 94 {}
N -85 -90 -85 -30 {}
N -85 30 -85 90 {}
N -45 0 -45 60 {}
N 115 0 115 94 {}
N 175 -90 175 -30 {}
N 175 30 175 90 {}
N 215 0 215 60 {}
N 370 0 370 94 {}
N 430 -90 430 -30 {}
N 430 30 430 90 {}
N 720 -60 720 0 {}
N 820 -90 820 -30 {}
N 820 30 820 90 {}
N 965 -60 965 0 {}
N 1005 -90 1005 -30 {}
N 1005 30 1005 90 {}
N 1065 0 1065 94 {}
N 1265 -60 1265 -30 {}
N 1265 30 1265 90 {}
N 1325 0 1325 94 {}
N 1520 -60 1520 -30 {}
N 1520 30 1520 90 {}
N 1580 0 1580 94 {}
N 1705 -60 1705 -30 {}
N 1705 30 1705 90 {}
N 1765 0 1765 94 {}
N 1915 -60 1915 -30 {}
N 1915 30 1915 90 {}
N 1975 0 1975 94 {}
N 2120 -60 2120 -30 {}
N 2120 30 2120 90 {}
N 2180 0 2180 94 {}
N -1130 -60 -970 -60 {}
N 720 -60 820 -60 {}
N 1005 -60 2120 -60 {}
N -845 0 -785 0 {}
N -745 0 -715 0 {}
N -655 0 -595 0 {}
N -555 0 -525 0 {}
N -350 0 -290 0 {}
N -250 0 -220 0 {}
N -145 0 -85 0 {}
N -45 0 -15 0 {}
N 115 0 175 0 {}
N 215 0 245 0 {}
N 370 0 430 0 {}
N 470 0 530 0 {}
N 570 0 630 0 {}
N 690 0 720 0 {}
N 935 0 965 0 {}
N 1005 0 1065 0 {}
N 1195 0 1225 0 {}
N 1265 0 1325 0 {}
N 1450 0 1480 0 {}
N 1520 0 1580 0 {}
N 1635 0 1665 0 {}
N 1705 0 1765 0 {}
N 1845 0 1875 0 {}
N 1915 0 1975 0 {}
N 2050 0 2080 0 {}
N 2120 0 2180 0 {}
C {devices/lab_wire.sym} 1005 -90 0 1 {name=l0 lab=VCM}
C {devices/lab_wire.sym} 215 60 2 0 {name=l1 lab=V_D0}
C {devices/lab_wire.sym} 965 -60 0 1 {name=l2 lab=V_D0}
C {devices/lab_wire.sym} -45 60 2 0 {name=l3 lab=V_D0_NOT}
C {devices/lab_wire.sym} 1225 0 0 0 {name=l4 lab=V_D0_NOT}
C {devices/lab_wire.sym} 530 0 0 1 {name=l5 lab=V_D1}
C {devices/lab_wire.sym} 1665 0 0 0 {name=l6 lab=V_D1}
C {devices/lab_wire.sym} -745 60 2 0 {name=l7 lab=V_D1_NOT}
C {devices/lab_wire.sym} 1875 0 0 0 {name=l8 lab=V_D1_NOT}
C {devices/lab_wire.sym} -555 60 2 0 {name=l9 lab=V_D2}
C {devices/lab_wire.sym} 2080 0 0 0 {name=l10 lab=V_D2}
C {devices/lab_wire.sym} -250 60 2 0 {name=l11 lab=V_D2_NOT}
C {devices/lab_wire.sym} 1480 0 0 0 {name=l12 lab=V_D2_NOT}
C {devices/lab_wire.sym} -970 90 2 0 {name=l13 lab=bot0}
C {devices/lab_wire.sym} -85 90 2 0 {name=l14 lab=bot0}
C {devices/lab_wire.sym} 175 90 2 0 {name=l15 lab=bot0}
C {devices/lab_wire.sym} 1005 90 2 0 {name=l16 lab=bot0}
C {devices/lab_wire.sym} 1265 90 2 0 {name=l17 lab=bot0}
C {devices/lab_wire.sym} -785 90 2 0 {name=l18 lab=bot1}
C {devices/lab_wire.sym} 430 90 2 0 {name=l19 lab=bot1}
C {devices/lab_wire.sym} 820 90 2 0 {name=l20 lab=bot1}
C {devices/lab_wire.sym} 1705 90 2 0 {name=l21 lab=bot1}
C {devices/lab_wire.sym} 1915 90 2 0 {name=l22 lab=bot1}
C {devices/lab_wire.sym} -1130 90 2 0 {name=l23 lab=bot2}
C {devices/lab_wire.sym} -595 90 2 0 {name=l24 lab=bot2}
C {devices/lab_wire.sym} -290 90 2 0 {name=l25 lab=bot2}
C {devices/lab_wire.sym} 1520 90 2 0 {name=l26 lab=bot2}
C {devices/lab_wire.sym} 2120 90 2 0 {name=l27 lab=bot2}
C {devices/lab_wire.sym} -785 -90 0 1 {name=l28 lab=vinp}
C {devices/lab_wire.sym} -595 -90 0 1 {name=l29 lab=vinp}
C {devices/lab_wire.sym} -290 -90 0 1 {name=l30 lab=vinp}
C {devices/lab_wire.sym} -85 -90 0 1 {name=l31 lab=vinp}
C {devices/lab_wire.sym} 175 -90 0 1 {name=l32 lab=vinp}
C {devices/lab_wire.sym} 430 -90 0 1 {name=l33 lab=vinp}
C {devices/lab_wire.sym} 570 0 0 0 {name=l34 lab=vinp}
C {devices/lab_wire.sym} -1130 -90 0 1 {name=l35 lab=vout}
C {devices/lab_wire.sym} 820 -90 0 1 {name=l36 lab=vout}
C {devices/lab_wire.sym} -350 94 2 0 {name=l37 lab=VDD}
C {devices/lab_wire.sym} 2180 94 2 0 {name=l38 lab=VDD}
C {devices/lab_wire.sym} -145 94 2 0 {name=l39 lab=VDD}
C {devices/lab_wire.sym} 1065 94 2 0 {name=l40 lab=VDD}
C {devices/lab_wire.sym} -845 94 2 0 {name=l41 lab=VDD}
C {devices/lab_wire.sym} 1765 94 2 0 {name=l42 lab=VDD}
C {devices/lab_wire.sym} 115 94 2 0 {name=l43 lab=VSS}
C {devices/lab_wire.sym} 1580 94 2 0 {name=l44 lab=VSS}
C {devices/lab_wire.sym} 1325 94 2 0 {name=l45 lab=VSS}
C {devices/lab_wire.sym} 370 94 2 0 {name=l46 lab=VSS}
C {devices/lab_wire.sym} 1975 94 2 0 {name=l47 lab=VSS}
C {devices/lab_wire.sym} -655 94 2 0 {name=l48 lab=VSS}
C {devices/ipin.sym} -1330 0 0 0 {name=p0 lab=V_D1_NOT}
C {devices/ipin.sym} -1330 120 0 0 {name=p1 lab=V_D2}
C {devices/ipin.sym} -1330 240 0 0 {name=p2 lab=V_D2_NOT}
C {devices/ipin.sym} -1330 360 0 0 {name=p3 lab=V_D0_NOT}
C {devices/ipin.sym} -1330 480 0 0 {name=p4 lab=V_D0}
C {devices/ipin.sym} -1330 600 0 0 {name=p5 lab=V_D1}
C {devices/iopin.sym} -1130 280 0 0 {name=p6 lab=vout}
C {devices/opin.sym} 2455 -30 0 0 {name=p7 lab=vinp}
C {devices/opin.sym} 2455 90 0 0 {name=p8 lab=VCM}
