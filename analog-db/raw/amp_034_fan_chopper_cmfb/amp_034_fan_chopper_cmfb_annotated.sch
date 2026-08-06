v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_034_fan_chopper_cmfb} -1740 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -1020 780 0 0 {name=CCM value='c_cm'}
C {devices/capa_np.sym} 835 520 1 0 {name=CM1_CORE value='x_dut_cm1_core_value'}
C {devices/capa_np.sym} 2230 520 1 0 {name=CM2_CORE value='x_dut_cm2_core_value'}
C {devices/res_np.sym} 475 390 1 0 {name=RMN_CMFB value='x_dut_rmn_cmfb_value'}
C {devices/res_np.sym} 780 390 1 0 {name=RMP_CMFB value='x_dut_rmp_cmfb_value'}
C {devices/vsource_np.sym} -1360 780 0 0 {name=VB1_CORE value="dc {vb1_core}"}
C {devices/vsource_np.sym} -1360 520 0 0 {name=VB2_CORE value="dc {vb2_core}"}
C {devices/vsource_np.sym} -1360 260 0 0 {name=VB3_CORE value="dc {vb3_core}"}
C {devices/vsource_np.sym} -1360 0 0 0 {name=VB4_CORE value="dc {vb4_core}"}
C {devices/vsource_np.sym} -1700 780 0 0 {name=VREFCM value="dc {vcm_ref}"}
C {devices/sg13_lv_pmos_np.sym} -90 260 0 1 {name=M10_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_core_w l=x_dut_xm10_core_l m=x_dut_xm10_core_m}
C {devices/sg13_lv_pmos_np.sym} 835 260 0 0 {name=M11_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_core_w l=x_dut_xm11_core_l m=x_dut_xm11_core_m}
C {devices/sg13_lv_nmos_np.sym} 1090 520 0 0 {name=M12_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_core_w l=x_dut_xm12_core_l m=x_dut_xm12_core_m}
C {devices/sg13_lv_nmos_np.sym} -90 520 0 1 {name=M13_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_core_w l=x_dut_xm13_core_l m=x_dut_xm13_core_m}
C {devices/sg13_lv_nmos_np.sym} 1335 260 0 1 {name=M14_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm14_core_w l=x_dut_xm14_core_l m=x_dut_xm14_core_m}
C {devices/sg13_lv_nmos_np.sym} 1810 260 0 0 {name=M15_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_core_w l=x_dut_xm15_core_l m=x_dut_xm15_core_m}
C {devices/sg13_lv_nmos_np.sym} 140 520 0 1 {name=M16_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_core_w l=x_dut_xm16_core_l m=x_dut_xm16_core_m}
C {devices/sg13_lv_pmos_np.sym} -315 520 0 1 {name=M17_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_core_w l=x_dut_xm17_core_l m=x_dut_xm17_core_m}
C {devices/sg13_lv_nmos_np.sym} 1315 520 0 0 {name=M18_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm18_core_w l=x_dut_xm18_core_l m=x_dut_xm18_core_m}
C {devices/sg13_lv_pmos_np.sym} 1545 520 0 0 {name=M19_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm19_core_w l=x_dut_xm19_core_l m=x_dut_xm19_core_m}
C {devices/sg13_lv_pmos_np.sym} -850 0 0 1 {name=M1_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_cmfb_w l=x_dut_xm1_cmfb_l m=x_dut_xm1_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 615 0 0 0 {name=M1_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_core_w l=x_dut_xm1_core_l m=x_dut_xm1_core_m}
C {devices/sg13_lv_nmos_np.sym} 1770 520 0 0 {name=M20_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm20_core_w l=x_dut_xm20_core_l m=x_dut_xm20_core_m}
C {devices/sg13_lv_pmos_np.sym} 2000 520 0 0 {name=M21_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm21_core_w l=x_dut_xm21_core_l m=x_dut_xm21_core_m}
C {devices/sg13_lv_nmos_np.sym} 370 520 0 1 {name=M22_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_core_w l=x_dut_xm22_core_l m=x_dut_xm22_core_m}
C {devices/sg13_lv_pmos_np.sym} 595 520 0 1 {name=M23_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_core_w l=x_dut_xm23_core_l m=x_dut_xm23_core_m}
C {devices/sg13_lv_nmos_np.sym} -1020 520 0 1 {name=M2_CMFB model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_cmfb_w l=x_dut_xm2_cmfb_l m=x_dut_xm2_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 615 260 0 0 {name=M2_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_core_w l=x_dut_xm2_core_l m=x_dut_xm2_core_m}
C {devices/sg13_lv_pmos_np.sym} 390 0 0 0 {name=M3_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_cmfb_w l=x_dut_xm3_cmfb_l m=x_dut_xm3_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 160 260 0 0 {name=M3_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_core_w l=x_dut_xm3_core_l m=x_dut_xm3_core_m}
C {devices/sg13_lv_pmos_np.sym} -680 260 0 0 {name=M4_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_cmfb_w l=x_dut_xm4_cmfb_l m=x_dut_xm4_cmfb_m}
C {devices/sg13_lv_nmos_np.sym} 390 780 0 0 {name=M4_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_core_w l=x_dut_xm4_core_l m=x_dut_xm4_core_m}
C {devices/sg13_lv_pmos_np.sym} -1020 260 0 1 {name=M5_CMFB model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_cmfb_w l=x_dut_xm5_cmfb_l m=x_dut_xm5_cmfb_m}
C {devices/sg13_lv_nmos_np.sym} 615 780 0 0 {name=M5_CORE model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_core_w l=x_dut_xm5_core_l m=x_dut_xm5_core_m}
C {devices/sg13_lv_nmos_np.sym} -680 520 0 0 {name=M6_CMFB model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_cmfb_w l=x_dut_xm6_cmfb_l m=x_dut_xm6_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} -90 0 0 1 {name=M6_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm6_core_w l=x_dut_xm6_core_l m=x_dut_xm6_core_m}
C {devices/sg13_lv_nmos_np.sym} 390 260 0 0 {name=M7_CMFB model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_cmfb_w l=x_dut_xm7_cmfb_l m=x_dut_xm7_cmfb_m}
C {devices/sg13_lv_pmos_np.sym} 835 0 0 0 {name=M7_CORE model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_core_w l=x_dut_xm7_core_l m=x_dut_xm7_core_m}
C {devices/sg13_lv_pmos_np.sym} 1335 0 0 1 {name=M8O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8o_w l=x_dut_xm8o_l m=x_dut_xm8o_m}
C {devices/sg13_lv_pmos_np.sym} 1810 0 0 0 {name=M9O model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9o_w l=x_dut_xm9o_l m=x_dut_xm9o_m}
N -1700 690 -1700 750 {}
N -1700 810 -1700 870 {}
N -1360 -90 -1360 -30 {}
N -1360 30 -1360 90 {}
N -1360 170 -1360 230 {}
N -1360 290 -1360 350 {}
N -1360 430 -1360 490 {}
N -1360 550 -1360 610 {}
N -1360 690 -1360 750 {}
N -1360 810 -1360 870 {}
N -1100 260 -1100 354 {}
N -1100 520 -1100 614 {}
N -1040 200 -1040 230 {}
N -1040 290 -1040 490 {}
N -1040 550 -1040 920 {}
N -1020 460 -1020 750 {}
N -1020 810 -1020 920 {}
N -930 0 -930 94 {}
N -870 -140 -870 -30 {}
N -870 30 -870 200 {}
N -700 450 -700 520 {}
N -660 200 -660 230 {}
N -660 290 -660 490 {}
N -660 550 -660 920 {}
N -600 260 -600 354 {}
N -600 520 -600 614 {}
N -395 520 -395 614 {}
N -335 460 -335 490 {}
N -335 550 -335 610 {}
N -295 520 -295 920 {}
N -170 0 -170 94 {}
N -170 260 -170 354 {}
N -170 520 -170 614 {}
N -110 -140 -110 -30 {}
N -110 30 -110 230 {}
N -110 290 -110 490 {}
N -110 550 -110 610 {}
N -70 520 -70 580 {}
N 60 520 60 614 {}
N 120 460 120 490 {}
N 120 550 120 610 {}
N 160 -140 160 520 {}
N 180 170 180 230 {}
N 180 290 180 350 {}
N 240 260 240 354 {}
N 290 520 290 614 {}
N 350 460 350 490 {}
N 350 550 350 610 {}
N 370 0 370 70 {}
N 370 190 370 260 {}
N 390 520 390 920 {}
N 410 -140 410 -30 {}
N 410 30 410 70 {}
N 410 170 410 230 {}
N 410 290 410 350 {}
N 410 690 410 750 {}
N 410 810 410 920 {}
N 415 260 415 390 {}
N 470 0 470 94 {}
N 470 780 470 874 {}
N 505 390 505 450 {}
N 515 520 515 614 {}
N 575 460 575 490 {}
N 575 550 575 610 {}
N 595 -60 595 0 {}
N 595 200 595 260 {}
N 595 720 595 780 {}
N 615 -140 615 520 {}
N 635 -140 635 -30 {}
N 635 30 635 230 {}
N 635 290 635 350 {}
N 635 690 635 750 {}
N 635 810 635 920 {}
N 695 0 695 94 {}
N 695 260 695 354 {}
N 695 780 695 874 {}
N 775 390 775 520 {}
N 810 390 810 450 {}
N 815 -60 815 0 {}
N 815 200 815 260 {}
N 855 -140 855 -30 {}
N 855 30 855 230 {}
N 855 290 855 350 {}
N 865 520 865 580 {}
N 915 0 915 94 {}
N 915 260 915 354 {}
N 1070 460 1070 520 {}
N 1110 430 1110 490 {}
N 1110 550 1110 610 {}
N 1170 520 1170 614 {}
N 1255 0 1255 94 {}
N 1255 260 1255 354 {}
N 1295 -140 1295 520 {}
N 1315 -140 1315 -30 {}
N 1315 30 1315 230 {}
N 1315 290 1315 920 {}
N 1335 460 1335 490 {}
N 1335 550 1335 610 {}
N 1395 520 1395 614 {}
N 1525 520 1525 920 {}
N 1565 460 1565 490 {}
N 1565 550 1565 610 {}
N 1625 520 1625 614 {}
N 1750 520 1750 920 {}
N 1760 260 1760 580 {}
N 1790 460 1790 490 {}
N 1790 550 1790 580 {}
N 1830 -140 1830 -30 {}
N 1830 30 1830 230 {}
N 1830 290 1830 920 {}
N 1850 520 1850 614 {}
N 1890 0 1890 94 {}
N 1890 260 1890 354 {}
N 1980 -140 1980 520 {}
N 2020 460 2020 490 {}
N 2020 550 2020 580 {}
N 2080 520 2080 614 {}
N 2170 200 2170 520 {}
N 2260 520 2260 580 {}
N 2290 260 2290 520 {}
N -1760 -140 2510 -140 {}
N -930 0 -870 0 {}
N -830 0 -770 0 {}
N -170 0 -110 0 {}
N -70 0 -10 0 {}
N 310 0 370 0 {}
N 410 0 470 0 {}
N 565 0 595 0 {}
N 635 0 695 0 {}
N 785 0 815 0 {}
N 855 0 915 0 {}
N 1255 0 1315 0 {}
N 1355 0 1790 0 {}
N 1830 0 1890 0 {}
N 370 70 410 70 {}
N 370 190 410 190 {}
N -1040 200 -660 200 {}
N 1830 200 2170 200 {}
N -1100 260 -1040 260 {}
N -1000 260 -940 260 {}
N -760 260 -700 260 {}
N -660 260 -600 260 {}
N -170 260 -110 260 {}
N -70 260 -10 260 {}
N 80 260 140 260 {}
N 180 260 240 260 {}
N 565 260 595 260 {}
N 635 260 695 260 {}
N 785 260 815 260 {}
N 855 260 915 260 {}
N 1255 260 1315 260 {}
N 1355 260 1415 260 {}
N 1730 260 1790 260 {}
N 1830 260 1890 260 {}
N 385 390 445 390 {}
N 505 390 535 390 {}
N 690 390 775 390 {}
N 810 390 840 390 {}
N -700 450 -660 450 {}
N -1040 460 -1020 460 {}
N -335 460 575 460 {}
N 1110 460 2020 460 {}
N -1100 520 -1040 520 {}
N -1000 520 -940 520 {}
N -660 520 -600 520 {}
N -395 520 -335 520 {}
N -170 520 -110 520 {}
N -70 520 -40 520 {}
N 60 520 120 520 {}
N 290 520 350 520 {}
N 515 520 575 520 {}
N 775 520 805 520 {}
N 865 520 895 520 {}
N 1040 520 1070 520 {}
N 1110 520 1170 520 {}
N 1335 520 1395 520 {}
N 1565 520 1625 520 {}
N 1790 520 1850 520 {}
N 2020 520 2080 520 {}
N 2170 520 2200 520 {}
N 2260 520 2290 520 {}
N 1760 580 2020 580 {}
N 310 780 370 780 {}
N 410 780 470 780 {}
N 565 780 595 780 {}
N 635 780 695 780 {}
N -1760 920 2510 920 {}
C {devices/lab_wire.sym} -1760 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1760 920 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -770 0 0 1 {name=l2 lab=cmfb__bias}
C {devices/lab_wire.sym} 310 0 0 0 {name=l3 lab=cmfb__bias}
C {devices/lab_wire.sym} 410 170 0 1 {name=l4 lab=cmfb__bias}
C {devices/lab_wire.sym} -760 260 0 0 {name=l5 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 385 390 0 0 {name=l6 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} 810 450 2 0 {name=l7 lab=cmfb__cm_sense}
C {devices/lab_wire.sym} -940 520 0 1 {name=l8 lab=cmfb__mirr}
C {devices/lab_wire.sym} -660 350 2 0 {name=l9 lab=cmfb__mirr}
C {devices/lab_wire.sym} -870 90 2 0 {name=l10 lab=cmfb__ptail}
C {devices/lab_wire.sym} -110 90 2 0 {name=l11 lab=core__casc_src_n}
C {devices/lab_wire.sym} 855 90 2 0 {name=l12 lab=core__casc_src_p}
C {devices/lab_wire.sym} -110 610 2 0 {name=l13 lab=core__fold_n}
C {devices/lab_wire.sym} 180 350 2 0 {name=l14 lab=core__fold_n}
C {devices/lab_wire.sym} 635 690 0 1 {name=l15 lab=core__fold_n}
C {devices/lab_wire.sym} 410 690 0 1 {name=l16 lab=core__fold_p}
C {devices/lab_wire.sym} 635 350 2 0 {name=l17 lab=core__fold_p}
C {devices/lab_wire.sym} 1110 610 2 0 {name=l18 lab=core__fold_p}
C {devices/lab_wire.sym} -335 610 2 0 {name=l19 lab=core__g2_n}
C {devices/lab_wire.sym} 120 610 2 0 {name=l20 lab=core__g2_n}
C {devices/lab_wire.sym} 1730 260 0 0 {name=l21 lab=core__g2_n}
C {devices/lab_wire.sym} 2260 580 2 0 {name=l22 lab=core__g2_n}
C {devices/lab_wire.sym} 350 610 2 0 {name=l23 lab=core__g2_p}
C {devices/lab_wire.sym} 575 610 2 0 {name=l24 lab=core__g2_p}
C {devices/lab_wire.sym} 865 580 2 0 {name=l25 lab=core__g2_p}
C {devices/lab_wire.sym} 1335 610 2 0 {name=l26 lab=core__g2_p}
C {devices/lab_wire.sym} 1415 260 0 1 {name=l27 lab=core__g2_p}
C {devices/lab_wire.sym} 1565 610 2 0 {name=l28 lab=core__g2_p}
C {devices/lab_wire.sym} -110 350 2 0 {name=l29 lab=core__out1_n}
C {devices/lab_wire.sym} 855 350 2 0 {name=l30 lab=core__out1_p}
C {devices/lab_wire.sym} 1110 430 0 1 {name=l31 lab=core__out1_p}
C {devices/lab_wire.sym} 180 170 0 1 {name=l32 lab=core__tail}
C {devices/lab_wire.sym} 635 90 2 0 {name=l33 lab=core__tail}
C {devices/lab_wire.sym} 310 780 0 0 {name=l34 lab=core__vb1}
C {devices/lab_wire.sym} 595 720 0 1 {name=l35 lab=core__vb1}
C {devices/lab_wire.sym} -70 580 2 0 {name=l36 lab=core__vb2}
C {devices/lab_wire.sym} 1070 460 0 1 {name=l37 lab=core__vb2}
C {devices/lab_wire.sym} -10 260 0 1 {name=l38 lab=core__vb3}
C {devices/lab_wire.sym} 815 200 0 1 {name=l39 lab=core__vb3}
C {devices/lab_wire.sym} -10 0 0 1 {name=l40 lab=core__vb4}
C {devices/lab_wire.sym} 595 -60 0 1 {name=l41 lab=core__vb4}
C {devices/lab_wire.sym} 815 -60 0 1 {name=l42 lab=core__vb4}
C {devices/lab_wire.sym} -1040 350 2 0 {name=l43 lab=vb4o}
C {devices/lab_wire.sym} 1415 0 0 1 {name=l44 lab=vb4o}
C {devices/lab_wire.sym} 80 260 0 0 {name=l45 lab=vinn}
C {devices/lab_wire.sym} 595 200 0 1 {name=l46 lab=vinp}
C {devices/lab_wire.sym} 505 450 2 0 {name=l47 lab=voutn}
C {devices/lab_wire.sym} 1830 90 2 0 {name=l48 lab=voutn}
C {devices/lab_wire.sym} 690 390 0 0 {name=l49 lab=voutp}
C {devices/lab_wire.sym} 1315 90 2 0 {name=l50 lab=voutp}
C {devices/lab_wire.sym} -940 260 0 1 {name=l51 lab=vref_cm}
C {devices/lab_wire.sym} -170 354 2 0 {name=l52 lab=vdd}
C {devices/lab_wire.sym} 915 354 2 0 {name=l53 lab=vdd}
C {devices/lab_wire.sym} -395 614 2 0 {name=l54 lab=vdd}
C {devices/lab_wire.sym} 1625 614 2 0 {name=l55 lab=vdd}
C {devices/lab_wire.sym} -930 94 2 0 {name=l56 lab=vdd}
C {devices/lab_wire.sym} 695 94 2 0 {name=l57 lab=vdd}
C {devices/lab_wire.sym} 2080 614 2 0 {name=l58 lab=vdd}
C {devices/lab_wire.sym} 515 614 2 0 {name=l59 lab=vdd}
C {devices/lab_wire.sym} 695 354 2 0 {name=l60 lab=vdd}
C {devices/lab_wire.sym} 470 94 2 0 {name=l61 lab=vdd}
C {devices/lab_wire.sym} 240 354 2 0 {name=l62 lab=vdd}
C {devices/lab_wire.sym} -600 354 2 0 {name=l63 lab=vdd}
C {devices/lab_wire.sym} -1100 354 2 0 {name=l64 lab=vdd}
C {devices/lab_wire.sym} -170 94 2 0 {name=l65 lab=vdd}
C {devices/lab_wire.sym} 915 94 2 0 {name=l66 lab=vdd}
C {devices/lab_wire.sym} 1255 94 2 0 {name=l67 lab=vdd}
C {devices/lab_wire.sym} 1890 94 2 0 {name=l68 lab=vdd}
C {devices/lab_wire.sym} 1170 614 2 0 {name=l69 lab=vss}
C {devices/lab_wire.sym} -170 614 2 0 {name=l70 lab=vss}
C {devices/lab_wire.sym} 1255 354 2 0 {name=l71 lab=vss}
C {devices/lab_wire.sym} 1890 354 2 0 {name=l72 lab=vss}
C {devices/lab_wire.sym} 60 614 2 0 {name=l73 lab=vss}
C {devices/lab_wire.sym} 1395 614 2 0 {name=l74 lab=vss}
C {devices/lab_wire.sym} 1850 614 2 0 {name=l75 lab=vss}
C {devices/lab_wire.sym} 290 614 2 0 {name=l76 lab=vss}
C {devices/lab_wire.sym} -1100 614 2 0 {name=l77 lab=vss}
C {devices/lab_wire.sym} 470 874 2 0 {name=l78 lab=vss}
C {devices/lab_wire.sym} 695 874 2 0 {name=l79 lab=vss}
C {devices/lab_wire.sym} -600 614 2 0 {name=l80 lab=vss}
C {devices/lab_wire.sym} 410 260 0 0 {name=l81 lab=vss}
C {devices/lab_wire.sym} -1360 870 2 0 {name=l82 lab=vss}
C {devices/lab_wire.sym} -1360 610 2 0 {name=l83 lab=vss}
C {devices/lab_wire.sym} -1360 350 2 0 {name=l84 lab=vss}
C {devices/lab_wire.sym} -1360 90 2 0 {name=l85 lab=vss}
C {devices/lab_wire.sym} -1700 870 2 0 {name=l86 lab=vss}
C {devices/lab_wire.sym} -1360 690 0 1 {name=l87 lab=core__vb1}
C {devices/lab_wire.sym} -1360 430 0 1 {name=l88 lab=core__vb2}
C {devices/lab_wire.sym} -1360 170 0 1 {name=l89 lab=core__vb3}
C {devices/lab_wire.sym} -1360 -90 0 1 {name=l90 lab=core__vb4}
C {devices/lab_wire.sym} -1700 690 0 1 {name=l91 lab=vref_cm}
C {devices/lab_wire.sym} 410 350 2 0 {name=l92 lab=vss}
C {devices/ipin.sym} -1900 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -1900 380 0 0 {name=p1 lab=vinp}
C {devices/opin.sym} 2650 30 0 0 {name=p2 lab=voutp}
C {devices/opin.sym} 2650 150 0 0 {name=p3 lab=voutn}
B 8 -1078 -78 618 78 {fill=0}
T {PMOS Simple Current Mirror} -1078 -96 0 0 0.3 0.3 {layer=8}
B 10 -1248 442 -452 598 {fill=0}
T {NMOS Simple Current Mirror} -1248 424 0 0 0.3 0.3 {layer=10}
B 12 90 182 843 338 {fill=0}
T {PMOS Differential Pair} 90 164 0 0 0.3 0.3 {layer=12}
B 21 -1248 182 -452 338 {fill=0}
T {PMOS Differential Pair} -1248 164 0 0 0.3 0.3 {layer=21}
