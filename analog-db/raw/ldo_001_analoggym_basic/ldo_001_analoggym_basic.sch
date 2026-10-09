v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_001_analoggym_basic} -1760 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 145 390 1 0 {name=C0 value='c_comp'}
C {devices/isource_np.sym} -1720 520 0 0 {name=IBIAS value="dc \{i_bias\}"}
C {devices/res_np.sym} -165 260 1 0 {name=R1 value='r_top'}
C {devices/res_np.sym} 840 520 0 0 {name=R2 value='r_bot'}
C {devices/vsource_np.sym} -1720 260 0 0 {name=VLP value="dc 0" savecurrent=false}
C {devices/vsource_np.sym} -1720 0 0 0 {name=VREF value="dc \{vref_val\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} 145 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -1020 260 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} -1360 0 0 1 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_nmos_np.sym} 145 260 0 1 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} 545 260 0 0 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_nmos_np.sym} 885 260 0 0 {name=M14 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} 1225 260 0 0 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 1670 260 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_nmos_np.sym} 145 520 0 1 {name=M17 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_nmos_np.sym} 545 520 0 0 {name=M18 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} 1225 520 0 0 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} 545 0 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1670 520 0 0 {name=M20 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} -1020 520 0 1 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} -1020 0 0 1 {name=M24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_pmos_np.sym} 885 0 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} 365 0 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 1225 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 1670 0 0 0 {name=M6 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 1450 260 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 1895 260 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1720 -90 -1720 -30 {}
N -1720 30 -1720 90 {}
N -1720 170 -1720 230 {}
N -1720 290 -1720 350 {}
N -1720 430 -1720 490 {}
N -1720 550 -1720 610 {}
N -1500 60 -1500 390 {}
N -1440 0 -1440 94 {}
N -1380 -140 -1380 -30 {}
N -1380 30 -1380 60 {}
N -1100 0 -1100 94 {}
N -1100 260 -1100 354 {}
N -1100 520 -1100 614 {}
N -1040 -140 -1040 -30 {}
N -1040 30 -1040 90 {}
N -1040 170 -1040 230 {}
N -1040 290 -1040 490 {}
N -1040 550 -1040 660 {}
N -760 0 -760 94 {}
N -700 -140 -700 -30 {}
N -700 30 -700 70 {}
N -660 -60 -660 70 {}
N -420 30 -420 200 {}
N -420 260 -420 354 {}
N -360 -140 -360 -30 {}
N -360 30 -360 90 {}
N -360 190 -360 230 {}
N -360 290 -360 660 {}
N -320 190 -320 260 {}
N -300 30 -300 520 {}
N -290 -60 -290 0 {}
N -135 260 -135 320 {}
N 65 0 65 94 {}
N 65 260 65 354 {}
N 65 520 65 614 {}
N 125 -140 125 -30 {}
N 125 30 125 230 {}
N 125 290 125 490 {}
N 125 550 125 660 {}
N 195 -60 195 0 {}
N 195 140 195 520 {}
N 285 0 285 94 {}
N 345 -140 345 -30 {}
N 345 30 345 90 {}
N 415 -60 415 0 {}
N 495 -60 495 0 {}
N 495 140 495 260 {}
N 495 520 495 580 {}
N 505 30 505 200 {}
N 565 -140 565 -30 {}
N 565 30 565 90 {}
N 565 200 565 230 {}
N 565 290 565 490 {}
N 565 550 565 660 {}
N 625 0 625 94 {}
N 625 260 625 354 {}
N 625 520 625 614 {}
N 835 -60 835 0 {}
N 840 430 840 490 {}
N 840 550 840 660 {}
N 865 140 865 260 {}
N 905 -140 905 -30 {}
N 905 30 905 90 {}
N 905 170 905 230 {}
N 905 290 905 660 {}
N 965 0 965 94 {}
N 965 260 965 354 {}
N 1175 520 1175 580 {}
N 1205 0 1205 70 {}
N 1245 -140 1245 -30 {}
N 1245 30 1245 70 {}
N 1245 170 1245 230 {}
N 1245 290 1245 490 {}
N 1245 550 1245 660 {}
N 1305 0 1305 94 {}
N 1305 260 1305 354 {}
N 1305 520 1305 614 {}
N 1470 200 1470 230 {}
N 1470 290 1470 320 {}
N 1530 60 1530 200 {}
N 1530 260 1530 354 {}
N 1620 520 1620 580 {}
N 1650 -60 1650 0 {}
N 1690 -140 1690 -30 {}
N 1690 30 1690 90 {}
N 1690 170 1690 230 {}
N 1690 290 1690 490 {}
N 1690 550 1690 660 {}
N 1750 0 1750 94 {}
N 1750 260 1750 354 {}
N 1750 520 1750 614 {}
N 1915 200 1915 230 {}
N 1915 290 1915 320 {}
N 1975 260 1975 354 {}
N -1860 -140 2370 -140 {}
N -660 -60 -290 -60 {}
N 195 -60 415 -60 {}
N 495 -60 835 -60 {}
N -1440 0 -1380 0 {}
N -1340 0 -1280 0 {}
N -1100 0 -1040 0 {}
N -1000 0 -940 0 {}
N -760 0 -700 0 {}
N -660 0 -600 0 {}
N -320 0 -290 0 {}
N 65 0 125 0 {}
N 165 0 225 0 {}
N 285 0 345 0 {}
N 385 0 525 0 {}
N 565 0 625 0 {}
N 835 0 865 0 {}
N 905 0 965 0 {}
N 1145 0 1205 0 {}
N 1245 0 1305 0 {}
N 1620 0 1650 0 {}
N 1690 0 1750 0 {}
N -420 30 -300 30 {}
N 505 30 565 30 {}
N -1500 60 -1380 60 {}
N 345 60 1530 60 {}
N -700 70 -660 70 {}
N 1205 70 1245 70 {}
N 125 140 195 140 {}
N 495 140 865 140 {}
N -360 190 -320 190 {}
N 865 190 905 190 {}
N -420 200 -360 200 {}
N 505 200 565 200 {}
N 1410 200 1915 200 {}
N -1100 260 -1040 260 {}
N -1000 260 -940 260 {}
N -420 260 -360 260 {}
N -255 260 -195 260 {}
N -135 260 -105 260 {}
N 65 260 125 260 {}
N 165 260 555 260 {}
N 565 260 625 260 {}
N 905 260 965 260 {}
N 1145 260 1205 260 {}
N 1245 260 1305 260 {}
N 1370 260 1430 260 {}
N 1470 260 1530 260 {}
N 1590 260 1650 260 {}
N 1690 260 1750 260 {}
N 1815 260 1875 260 {}
N 1915 260 1975 260 {}
N 1245 320 1470 320 {}
N 1690 320 1915 320 {}
N -1500 390 115 390 {}
N 175 390 1690 390 {}
N -1100 520 -1040 520 {}
N -1000 520 -300 520 {}
N 65 520 125 520 {}
N 165 520 525 520 {}
N 565 520 625 520 {}
N 1175 520 1205 520 {}
N 1245 520 1305 520 {}
N 1620 520 1650 520 {}
N 1690 520 1750 520 {}
N 495 580 1620 580 {}
N -1860 660 2370 660 {}
C {devices/lab_wire.sym} 565 90 2 0 {name=l0 lab=dm_1}
C {devices/lab_wire.sym} 1245 350 2 0 {name=l1 lab=dm_2}
C {devices/lab_wire.sym} -940 0 0 1 {name=l2 lab=ib}
C {devices/lab_wire.sym} -600 0 0 1 {name=l3 lab=ib}
C {devices/lab_wire.sym} 225 0 0 1 {name=l4 lab=ib}
C {devices/lab_wire.sym} -135 320 2 0 {name=l5 lab=lp_brk}
C {devices/lab_wire.sym} -1280 0 0 1 {name=l6 lab=net1}
C {devices/lab_wire.sym} -1040 90 2 0 {name=l7 lab=net1}
C {devices/lab_wire.sym} -1040 170 0 1 {name=l8 lab=net1}
C {devices/lab_wire.sym} -940 260 0 1 {name=l9 lab=net10}
C {devices/lab_wire.sym} 1690 90 2 0 {name=l10 lab=net10}
C {devices/lab_wire.sym} 1690 170 0 1 {name=l11 lab=net10}
C {devices/lab_wire.sym} 1690 350 2 0 {name=l12 lab=net106}
C {devices/lab_wire.sym} -1040 350 2 0 {name=l13 lab=net12}
C {devices/lab_wire.sym} 345 90 2 0 {name=l14 lab=net20}
C {devices/lab_wire.sym} 125 350 2 0 {name=l15 lab=net28}
C {devices/lab_wire.sym} 565 350 2 0 {name=l16 lab=net31}
C {devices/lab_wire.sym} -360 90 2 0 {name=l17 lab=net7}
C {devices/lab_wire.sym} 905 170 0 1 {name=l18 lab=vb3}
C {devices/lab_wire.sym} 905 90 2 0 {name=l19 lab=vb3}
C {devices/lab_wire.sym} 1145 260 0 0 {name=l20 lab=vb3}
C {devices/lab_wire.sym} 1590 260 0 0 {name=l21 lab=vb3}
C {devices/lab_wire.sym} 125 90 2 0 {name=l22 lab=vb4}
C {devices/lab_wire.sym} -255 260 0 0 {name=l23 lab=vfb}
C {devices/lab_wire.sym} 840 430 0 1 {name=l24 lab=vfb}
C {devices/lab_wire.sym} 1370 260 0 0 {name=l25 lab=vfb}
C {devices/lab_wire.sym} 1145 0 0 0 {name=l26 lab=voutn}
C {devices/lab_wire.sym} 1245 170 0 1 {name=l27 lab=voutn}
C {devices/lab_wire.sym} 1650 -60 0 1 {name=l28 lab=voutn}
C {devices/lab_wire.sym} 1815 260 0 0 {name=l29 lab=vref}
C {devices/lab_wire.sym} -1100 354 2 0 {name=l30 lab=net1}
C {devices/lab_wire.sym} 1530 354 2 0 {name=l31 lab=net20}
C {devices/lab_wire.sym} 1975 354 2 0 {name=l32 lab=net20}
C {devices/lab_wire.sym} -760 94 2 0 {name=l33 lab=vdd}
C {devices/lab_wire.sym} 65 94 2 0 {name=l34 lab=vdd}
C {devices/lab_wire.sym} -1440 94 2 0 {name=l35 lab=vdd}
C {devices/lab_wire.sym} 625 94 2 0 {name=l36 lab=vdd}
C {devices/lab_wire.sym} -1100 94 2 0 {name=l37 lab=vdd}
C {devices/lab_wire.sym} 965 94 2 0 {name=l38 lab=vdd}
C {devices/lab_wire.sym} 285 94 2 0 {name=l39 lab=vdd}
C {devices/lab_wire.sym} 1305 94 2 0 {name=l40 lab=vdd}
C {devices/lab_wire.sym} 1750 94 2 0 {name=l41 lab=vdd}
C {devices/lab_wire.sym} -360 0 0 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} 65 354 2 0 {name=l43 lab=vss}
C {devices/lab_wire.sym} 625 354 2 0 {name=l44 lab=vss}
C {devices/lab_wire.sym} 965 354 2 0 {name=l45 lab=vss}
C {devices/lab_wire.sym} 1305 354 2 0 {name=l46 lab=vss}
C {devices/lab_wire.sym} 1750 354 2 0 {name=l47 lab=vss}
C {devices/lab_wire.sym} 65 614 2 0 {name=l48 lab=vss}
C {devices/lab_wire.sym} 625 614 2 0 {name=l49 lab=vss}
C {devices/lab_wire.sym} 1305 614 2 0 {name=l50 lab=vss}
C {devices/lab_wire.sym} 1750 614 2 0 {name=l51 lab=vss}
C {devices/lab_wire.sym} -1100 614 2 0 {name=l52 lab=vss}
C {devices/lab_wire.sym} -420 354 2 0 {name=l53 lab=vss}
C {devices/lab_wire.sym} -1720 350 2 0 {name=l54 lab=vout}
C {devices/lab_wire.sym} -1720 430 0 1 {name=l55 lab=ib}
C {devices/lab_wire.sym} -1720 610 2 0 {name=l56 lab=vss}
C {devices/lab_wire.sym} -1720 90 2 0 {name=l57 lab=vss}
C {devices/lab_wire.sym} -1720 170 0 1 {name=l58 lab=lp_brk}
C {devices/lab_wire.sym} -1720 -90 0 1 {name=l59 lab=vref}
C {devices/iopin.sym} -1860 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -1860 660 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 85 390 0 0 {name=p2 lab=vout}
