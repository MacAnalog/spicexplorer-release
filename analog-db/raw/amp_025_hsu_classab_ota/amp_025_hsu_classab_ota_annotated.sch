v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_025_hsu_classab_ota} -1570 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -1070 520 1 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} 1660 520 0 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} 615 520 0 0 {name=CIN value='cin_val'}
C {devices/capa_np.sym} 470 780 0 0 {name=COUT value='cout_val'}
C {devices/res_np.sym} 1200 520 1 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} 80 520 1 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} 775 520 0 0 {name=RIN value='rin_val'}
C {devices/res_np.sym} 360 390 1 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} -465 390 1 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} 100 780 0 0 {name=ROUT value='rout_val'}
C {devices/vsource_np.sym} -1530 780 0 0 {name=VB1 value="dc {vb1}"}
C {devices/vsource_np.sym} -1530 520 0 0 {name=VB2 value="dc {vb2}"}
C {devices/vsource_np.sym} -1530 260 0 0 {name=VB3 value="dc {vb3}"}
C {devices/vsource_np.sym} -1530 0 0 0 {name=VCMFB_REF value="dc {vcmfb_ref}"}
C {devices/sg13_lv_pmos_np.sym} 840 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -420 260 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 1020 260 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} -420 0 0 1 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_pmos_np.sym} 1020 0 0 0 {name=M13 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_pmos_np.sym} -760 0 0 1 {name=M14 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} -760 260 0 1 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} -1190 0 0 1 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} -760 520 0 1 {name=M17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_pmos_np.sym} -1190 260 0 1 {name=M18 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} -760 780 0 1 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} -80 260 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} 280 0 0 0 {name=M20 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 280 260 0 0 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 650 0 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} 280 520 0 0 {name=M23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_pmos_np.sym} 650 260 0 0 {name=M24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_nmos_np.sym} 280 780 0 0 {name=M25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm25_w l=x_dut_xm25_l m=x_dut_xm25_m}
C {devices/sg13_lv_pmos_np.sym} 1400 260 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} -80 520 0 1 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 1400 520 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_nmos_np.sym} -420 780 0 1 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} -420 520 0 1 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_nmos_np.sym} 1020 780 0 0 {name=M8 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_nmos_np.sym} 1020 520 0 0 {name=M9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1530 -90 -1530 -30 {}
N -1530 30 -1530 90 {}
N -1530 170 -1530 230 {}
N -1530 290 -1530 350 {}
N -1530 430 -1530 490 {}
N -1530 550 -1530 610 {}
N -1530 690 -1530 750 {}
N -1530 810 -1530 870 {}
N -1270 0 -1270 94 {}
N -1270 260 -1270 354 {}
N -1210 -140 -1210 -30 {}
N -1210 30 -1210 230 {}
N -1210 290 -1210 920 {}
N -1040 520 -1040 580 {}
N -840 0 -840 94 {}
N -840 260 -840 354 {}
N -840 520 -840 614 {}
N -840 780 -840 874 {}
N -780 -140 -780 -30 {}
N -780 30 -780 90 {}
N -780 170 -780 230 {}
N -780 290 -780 490 {}
N -780 550 -780 750 {}
N -780 810 -780 920 {}
N -740 190 -740 260 {}
N -740 520 -740 590 {}
N -525 200 -525 390 {}
N -500 0 -500 94 {}
N -500 260 -500 354 {}
N -500 520 -500 614 {}
N -500 780 -500 874 {}
N -440 -140 -440 -30 {}
N -440 30 -440 230 {}
N -440 290 -440 490 {}
N -440 550 -440 750 {}
N -440 810 -440 920 {}
N -435 390 -435 450 {}
N -160 260 -160 354 {}
N -160 520 -160 614 {}
N -100 170 -100 230 {}
N -100 290 -100 350 {}
N -100 430 -100 490 {}
N -100 550 -100 920 {}
N -60 450 -60 520 {}
N 50 460 50 520 {}
N 100 690 100 750 {}
N 100 810 100 870 {}
N 110 520 110 580 {}
N 230 520 230 780 {}
N 260 190 260 260 {}
N 260 520 260 590 {}
N 300 -140 300 -30 {}
N 300 30 300 60 {}
N 300 170 300 230 {}
N 300 290 300 350 {}
N 300 430 300 490 {}
N 300 550 300 750 {}
N 300 810 300 920 {}
N 360 0 360 94 {}
N 360 260 360 354 {}
N 360 520 360 614 {}
N 360 780 360 874 {}
N 390 390 390 450 {}
N 470 690 470 750 {}
N 470 810 470 840 {}
N 600 0 600 60 {}
N 600 260 600 580 {}
N 615 430 615 490 {}
N 615 550 615 610 {}
N 670 -140 670 -30 {}
N 670 30 670 90 {}
N 670 170 670 230 {}
N 670 290 670 350 {}
N 730 0 730 94 {}
N 730 260 730 354 {}
N 775 430 775 490 {}
N 775 550 775 580 {}
N 820 -60 820 0 {}
N 860 -140 860 -30 {}
N 860 30 860 200 {}
N 920 0 920 94 {}
N 1000 -60 1000 0 {}
N 1000 460 1000 520 {}
N 1040 -140 1040 -30 {}
N 1040 30 1040 90 {}
N 1040 170 1040 230 {}
N 1040 290 1040 350 {}
N 1040 430 1040 490 {}
N 1040 550 1040 750 {}
N 1040 810 1040 920 {}
N 1100 0 1100 94 {}
N 1100 260 1100 354 {}
N 1100 520 1100 614 {}
N 1100 780 1100 874 {}
N 1230 520 1230 580 {}
N 1380 450 1380 520 {}
N 1420 170 1420 230 {}
N 1420 290 1420 350 {}
N 1420 430 1420 490 {}
N 1420 550 1420 920 {}
N 1480 260 1480 354 {}
N 1480 520 1480 614 {}
N 1660 430 1660 490 {}
N 1660 520 1660 610 {}
N -1590 -140 1890 -140 {}
N -1270 0 -1210 0 {}
N -1170 0 -1110 0 {}
N -840 0 -780 0 {}
N -740 0 -680 0 {}
N -500 0 -440 0 {}
N -400 0 100 0 {}
N 200 0 260 0 {}
N 300 0 360 0 {}
N 570 0 630 0 {}
N 670 0 730 0 {}
N 790 0 820 0 {}
N 860 0 920 0 {}
N 970 0 1000 0 {}
N 1040 0 1100 0 {}
N 300 60 600 60 {}
N -780 190 -740 190 {}
N 260 190 300 190 {}
N -1270 260 -1210 260 {}
N -1170 260 -1110 260 {}
N -840 260 -780 260 {}
N -500 260 -440 260 {}
N -400 260 -340 260 {}
N -160 260 -100 260 {}
N -60 260 0 260 {}
N 300 260 360 260 {}
N 570 260 630 260 {}
N 670 260 730 260 {}
N 940 260 1000 260 {}
N 1040 260 1100 260 {}
N 1320 260 1380 260 {}
N 1420 260 1480 260 {}
N -555 390 -495 390 {}
N -435 390 -405 390 {}
N 270 390 330 390 {}
N 390 390 420 390 {}
N -100 450 -60 450 {}
N 1380 450 1420 450 {}
N -1160 520 -1100 520 {}
N -1040 520 -1010 520 {}
N -840 520 -780 520 {}
N -740 520 -680 520 {}
N -500 520 -440 520 {}
N -400 520 -340 520 {}
N -160 520 -100 520 {}
N 20 520 50 520 {}
N 110 520 230 520 {}
N 300 520 360 520 {}
N 1040 520 1100 520 {}
N 1110 520 1170 520 {}
N 1230 520 1260 520 {}
N 1420 520 1480 520 {}
N 300 580 600 580 {}
N 615 580 775 580 {}
N -780 590 -740 590 {}
N 260 590 300 590 {}
N -840 780 -780 780 {}
N -740 780 -680 780 {}
N -500 780 -440 780 {}
N -400 780 -340 780 {}
N 230 780 260 780 {}
N 300 780 360 780 {}
N 940 780 1000 780 {}
N 1040 780 1100 780 {}
N 100 840 470 840 {}
N -1590 920 1890 920 {}
C {devices/lab_wire.sym} -1590 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1590 920 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 300 350 2 0 {name=l2 lab=abm_n}
C {devices/lab_wire.sym} 300 430 0 1 {name=l3 lab=abm_n}
C {devices/lab_wire.sym} 1660 430 0 1 {name=l4 lab=abm_n}
C {devices/lab_wire.sym} -1040 580 2 0 {name=l5 lab=abm_p}
C {devices/lab_wire.sym} -780 350 2 0 {name=l6 lab=abm_p}
C {devices/lab_wire.sym} -435 450 2 0 {name=l7 lab=cm_det}
C {devices/lab_wire.sym} 270 390 0 0 {name=l8 lab=cm_det}
C {devices/lab_wire.sym} 615 430 0 1 {name=l9 lab=cm_det}
C {devices/lab_wire.sym} 775 430 0 1 {name=l10 lab=cm_det}
C {devices/lab_wire.sym} -440 610 2 0 {name=l11 lab=csrc_n}
C {devices/lab_wire.sym} 1040 610 2 0 {name=l12 lab=csrc_p}
C {devices/lab_wire.sym} -440 350 2 0 {name=l13 lab=drv_n}
C {devices/lab_wire.sym} 110 580 2 0 {name=l14 lab=drv_n}
C {devices/lab_wire.sym} -680 780 0 1 {name=l15 lab=drv_p}
C {devices/lab_wire.sym} 1040 350 2 0 {name=l16 lab=drv_p}
C {devices/lab_wire.sym} 1040 430 0 1 {name=l17 lab=drv_p}
C {devices/lab_wire.sym} 1110 520 0 0 {name=l18 lab=drv_p}
C {devices/lab_wire.sym} 300 170 0 1 {name=l19 lab=gnf_n}
C {devices/lab_wire.sym} 570 0 0 0 {name=l20 lab=gnf_n}
C {devices/lab_wire.sym} -1110 0 0 1 {name=l21 lab=gnf_p}
C {devices/lab_wire.sym} -780 90 2 0 {name=l22 lab=gnf_p}
C {devices/lab_wire.sym} -780 170 0 1 {name=l23 lab=gnf_p}
C {devices/lab_wire.sym} 570 260 0 0 {name=l24 lab=gpf_n}
C {devices/lab_wire.sym} -1110 260 0 1 {name=l25 lab=gpf_p}
C {devices/lab_wire.sym} -680 520 0 1 {name=l26 lab=gpf_p}
C {devices/lab_wire.sym} -340 780 0 1 {name=l27 lab=mir_n}
C {devices/lab_wire.sym} 1420 430 0 1 {name=l28 lab=mir_n}
C {devices/lab_wire.sym} 1420 350 2 0 {name=l29 lab=mir_n}
C {devices/lab_wire.sym} -100 350 2 0 {name=l30 lab=mir_p}
C {devices/lab_wire.sym} -100 430 0 1 {name=l31 lab=mir_p}
C {devices/lab_wire.sym} 940 780 0 0 {name=l32 lab=mir_p}
C {devices/lab_wire.sym} -440 90 2 0 {name=l33 lab=psrc_n}
C {devices/lab_wire.sym} 1040 90 2 0 {name=l34 lab=psrc_p}
C {devices/lab_wire.sym} 1040 170 0 1 {name=l35 lab=psrc_p}
C {devices/lab_wire.sym} -100 170 0 1 {name=l36 lab=tail}
C {devices/lab_wire.sym} 860 90 2 0 {name=l37 lab=tail}
C {devices/lab_wire.sym} 1420 170 0 1 {name=l38 lab=tail}
C {devices/lab_wire.sym} -680 0 0 1 {name=l39 lab=vb1}
C {devices/lab_wire.sym} 200 0 0 0 {name=l40 lab=vb1}
C {devices/lab_wire.sym} 820 -60 0 1 {name=l41 lab=vb1}
C {devices/lab_wire.sym} -340 260 0 1 {name=l42 lab=vb2}
C {devices/lab_wire.sym} 940 260 0 0 {name=l43 lab=vb2}
C {devices/lab_wire.sym} -340 520 0 1 {name=l44 lab=vb3}
C {devices/lab_wire.sym} 1000 460 0 1 {name=l45 lab=vb3}
C {devices/lab_wire.sym} -340 0 0 1 {name=l46 lab=vcmfb}
C {devices/lab_wire.sym} 100 870 2 0 {name=l47 lab=vcmfb}
C {devices/lab_wire.sym} 1000 -60 0 1 {name=l48 lab=vcmfb}
C {devices/lab_wire.sym} 615 610 2 0 {name=l49 lab=vcmfb_ref}
C {devices/lab_wire.sym} 0 260 0 1 {name=l50 lab=vinn}
C {devices/lab_wire.sym} 1320 260 0 0 {name=l51 lab=vinp}
C {devices/lab_wire.sym} 390 450 2 0 {name=l52 lab=voutn}
C {devices/lab_wire.sym} 670 90 2 0 {name=l53 lab=voutn}
C {devices/lab_wire.sym} 670 170 0 1 {name=l54 lab=voutn}
C {devices/lab_wire.sym} -1210 90 2 0 {name=l55 lab=voutp}
C {devices/lab_wire.sym} -555 390 0 0 {name=l56 lab=voutp}
C {devices/lab_wire.sym} 50 460 0 1 {name=l57 lab=zc_n}
C {devices/lab_wire.sym} 1660 610 2 0 {name=l58 lab=zc_n}
C {devices/lab_wire.sym} -1160 520 0 0 {name=l59 lab=zc_p}
C {devices/lab_wire.sym} 1230 580 2 0 {name=l60 lab=zc_p}
C {devices/lab_wire.sym} 920 94 2 0 {name=l61 lab=vdd}
C {devices/lab_wire.sym} -500 354 2 0 {name=l62 lab=vdd}
C {devices/lab_wire.sym} 1100 354 2 0 {name=l63 lab=vdd}
C {devices/lab_wire.sym} -500 94 2 0 {name=l64 lab=vdd}
C {devices/lab_wire.sym} 1100 94 2 0 {name=l65 lab=vdd}
C {devices/lab_wire.sym} -840 94 2 0 {name=l66 lab=vdd}
C {devices/lab_wire.sym} -840 614 2 0 {name=l67 lab=vdd}
C {devices/lab_wire.sym} -1270 354 2 0 {name=l68 lab=vdd}
C {devices/lab_wire.sym} -160 354 2 0 {name=l69 lab=vdd}
C {devices/lab_wire.sym} 360 94 2 0 {name=l70 lab=vdd}
C {devices/lab_wire.sym} 360 614 2 0 {name=l71 lab=vdd}
C {devices/lab_wire.sym} 730 354 2 0 {name=l72 lab=vdd}
C {devices/lab_wire.sym} 1480 354 2 0 {name=l73 lab=vdd}
C {devices/lab_wire.sym} -840 354 2 0 {name=l74 lab=vss}
C {devices/lab_wire.sym} -1270 94 2 0 {name=l75 lab=vss}
C {devices/lab_wire.sym} -840 874 2 0 {name=l76 lab=vss}
C {devices/lab_wire.sym} 360 354 2 0 {name=l77 lab=vss}
C {devices/lab_wire.sym} 730 94 2 0 {name=l78 lab=vss}
C {devices/lab_wire.sym} 360 874 2 0 {name=l79 lab=vss}
C {devices/lab_wire.sym} -160 614 2 0 {name=l80 lab=vss}
C {devices/lab_wire.sym} 1480 614 2 0 {name=l81 lab=vss}
C {devices/lab_wire.sym} -500 874 2 0 {name=l82 lab=vss}
C {devices/lab_wire.sym} -500 614 2 0 {name=l83 lab=vss}
C {devices/lab_wire.sym} 1100 874 2 0 {name=l84 lab=vss}
C {devices/lab_wire.sym} 1100 614 2 0 {name=l85 lab=vss}
C {devices/lab_wire.sym} -1530 -90 0 1 {name=l86 lab=vcmfb_ref}
C {devices/lab_wire.sym} -1530 870 2 0 {name=l87 lab=vss}
C {devices/lab_wire.sym} -1530 610 2 0 {name=l88 lab=vss}
C {devices/lab_wire.sym} -1530 350 2 0 {name=l89 lab=vss}
C {devices/lab_wire.sym} -1530 90 2 0 {name=l90 lab=vss}
C {devices/lab_wire.sym} -1530 690 0 1 {name=l91 lab=vb1}
C {devices/lab_wire.sym} -1530 430 0 1 {name=l92 lab=vb2}
C {devices/lab_wire.sym} -1530 170 0 1 {name=l93 lab=vb3}
C {devices/lab_wire.sym} 470 690 0 1 {name=l94 lab=vss}
C {devices/lab_wire.sym} 100 690 0 1 {name=l95 lab=vss}
C {devices/lab_wire.sym} 670 350 2 0 {name=l96 lab=vss}
C {devices/ipin.sym} -1730 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -1730 380 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -1210 1060 0 0 {name=p2 lab=voutp}
C {devices/iopin.sym} 670 1060 0 0 {name=p3 lab=voutn}
B 8 -268 442 1208 858 {fill=0}
T {NMOS Simple Current Mirror} -268 424 0 0 0.3 0.3 {layer=8}
B 10 -608 442 1588 858 {fill=0}
T {NMOS Simple Current Mirror} -608 424 0 0 0.3 0.3 {layer=10}
B 12 -268 182 1588 338 {fill=0}
T {PMOS Differential Pair} -268 164 0 0 0.3 0.3 {layer=12}
