v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_025_hsu_classab_ota} -1600 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -1070 520 1 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} 955 520 0 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} 765 520 0 0 {name=CIN value='cin_val'}
C {devices/capa_np.sym} 620 780 0 0 {name=COUT value='cout_val'}
C {devices/vccs.sym} 395 650 0 0 {name=GM value="\{gm_val\}"}
C {devices/res_np.sym} 1465 520 1 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} 155 520 1 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} 1925 520 0 0 {name=RIN value='rin_val'}
C {devices/res_np.sym} 520 390 1 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} -365 390 1 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} 175 780 0 0 {name=ROUT value='rout_val'}
C {devices/vsource_np.sym} -1560 780 0 0 {name=VB1 value="dc \{vb1\}" savecurrent=false}
C {devices/vsource_np.sym} -1560 520 0 0 {name=VB2 value="dc \{vb2\}" savecurrent=false}
C {devices/vsource_np.sym} -1560 260 0 0 {name=VB3 value="dc \{vb3\}" savecurrent=false}
C {devices/vsource_np.sym} -1560 0 0 0 {name=VCMFB_REF value="dc \{vcmfb_ref\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 1030 0 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -345 260 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 1245 260 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} -345 0 0 1 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_pmos_np.sym} 1245 0 0 0 {name=M13 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_pmos_np.sym} -685 0 0 1 {name=M14 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} -685 260 0 1 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} -1190 0 0 1 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} -685 520 0 1 {name=M17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_pmos_np.sym} -1190 260 0 1 {name=M18 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} -685 780 0 1 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} -5 260 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} 395 0 0 0 {name=M20 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 395 260 0 0 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 800 0 0 0 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} 395 520 0 0 {name=M23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_pmos_np.sym} 800 260 0 0 {name=M24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_nmos_np.sym} 395 780 0 0 {name=M25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm25_w l=x_dut_xm25_l m=x_dut_xm25_m}
C {devices/sg13_lv_pmos_np.sym} 1705 260 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} -5 520 0 1 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 1705 520 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_nmos_np.sym} -345 780 0 1 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} -345 520 0 1 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_nmos_np.sym} 1245 780 0 0 {name=M8 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_nmos_np.sym} 1245 520 0 0 {name=M9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1560 -90 -1560 -30 {}
N -1560 30 -1560 90 {}
N -1560 170 -1560 230 {}
N -1560 290 -1560 350 {}
N -1560 430 -1560 490 {}
N -1560 550 -1560 610 {}
N -1560 690 -1560 750 {}
N -1560 810 -1560 870 {}
N -1270 0 -1270 94 {}
N -1270 200 -1270 390 {}
N -1210 -140 -1210 -30 {}
N -1210 30 -1210 230 {}
N -1210 290 -1210 920 {}
N -1200 0 -1200 60 {}
N -1170 0 -1170 60 {}
N -1170 260 -1170 320 {}
N -1070 460 -1070 520 {}
N -765 0 -765 94 {}
N -765 260 -765 354 {}
N -765 520 -765 614 {}
N -765 780 -765 874 {}
N -705 -140 -705 -30 {}
N -705 30 -705 60 {}
N -705 170 -705 230 {}
N -705 290 -705 490 {}
N -705 550 -705 750 {}
N -705 810 -705 920 {}
N -665 190 -665 260 {}
N -665 520 -665 590 {}
N -425 0 -425 94 {}
N -425 260 -425 354 {}
N -425 520 -425 614 {}
N -425 780 -425 874 {}
N -365 -140 -365 -30 {}
N -365 30 -365 230 {}
N -365 290 -365 490 {}
N -365 550 -365 750 {}
N -365 810 -365 920 {}
N -335 390 -335 450 {}
N -85 320 -85 490 {}
N -85 520 -85 614 {}
N -25 200 -25 230 {}
N -25 290 -25 350 {}
N -25 450 -25 490 {}
N -25 550 -25 920 {}
N 15 450 15 900 {}
N 175 690 175 750 {}
N 175 810 175 840 {}
N 205 390 205 670 {}
N 275 460 275 520 {}
N 345 520 345 780 {}
N 355 60 355 230 {}
N 375 190 375 260 {}
N 375 520 375 590 {}
N 395 680 395 840 {}
N 415 -140 415 -30 {}
N 415 30 415 60 {}
N 415 190 415 230 {}
N 415 290 415 350 {}
N 415 550 415 750 {}
N 415 810 415 920 {}
N 475 0 475 94 {}
N 475 320 475 490 {}
N 475 520 475 614 {}
N 475 780 475 874 {}
N 620 690 620 750 {}
N 620 810 620 840 {}
N 750 0 750 60 {}
N 750 260 750 580 {}
N 765 430 765 490 {}
N 765 550 765 610 {}
N 820 -140 820 -30 {}
N 820 30 820 90 {}
N 820 170 820 230 {}
N 820 290 820 920 {}
N 825 580 825 630 {}
N 880 0 880 94 {}
N 880 260 880 354 {}
N 955 430 955 490 {}
N 955 550 955 610 {}
N 990 60 990 200 {}
N 1050 -140 1050 -30 {}
N 1050 30 1050 60 {}
N 1050 60 1050 90 {}
N 1110 60 1110 200 {}
N 1195 780 1195 900 {}
N 1225 460 1225 520 {}
N 1265 -140 1265 -30 {}
N 1265 30 1265 90 {}
N 1265 290 1265 350 {}
N 1265 550 1265 610 {}
N 1265 720 1265 750 {}
N 1265 810 1265 920 {}
N 1325 60 1325 230 {}
N 1325 320 1325 490 {}
N 1325 550 1325 720 {}
N 1325 780 1325 874 {}
N 1465 490 1465 520 {}
N 1685 450 1685 520 {}
N 1725 200 1725 230 {}
N 1725 290 1725 350 {}
N 1725 450 1725 490 {}
N 1725 550 1725 920 {}
N 1785 320 1785 490 {}
N 1785 520 1785 614 {}
N 1925 430 1925 490 {}
N 1925 550 1925 580 {}
N -1690 -140 2180 -140 {}
N -1270 0 -1210 0 {}
N -1200 0 -1140 0 {}
N -765 0 -705 0 {}
N -665 0 -605 0 {}
N -425 0 -365 0 {}
N -325 0 -265 0 {}
N 315 0 375 0 {}
N 415 0 475 0 {}
N 720 0 780 0 {}
N 820 0 880 0 {}
N 950 0 1010 0 {}
N 1165 0 1225 0 {}
N -1200 60 -705 60 {}
N 355 60 750 60 {}
N 990 60 1110 60 {}
N 1265 60 1325 60 {}
N -705 190 -665 190 {}
N 375 190 415 190 {}
N -1270 200 -1210 200 {}
N -25 200 1725 200 {}
N 355 230 415 230 {}
N 1265 230 1325 230 {}
N -1170 260 -1140 260 {}
N -765 260 -705 260 {}
N -425 260 -365 260 {}
N -325 260 -265 260 {}
N 15 260 45 260 {}
N 720 260 780 260 {}
N 820 260 880 260 {}
N 1165 260 1225 260 {}
N 1595 260 1685 260 {}
N -85 320 -25 320 {}
N 415 320 475 320 {}
N 1265 320 1325 320 {}
N 1725 320 1785 320 {}
N -1270 390 -395 390 {}
N -335 390 490 390 {}
N 550 390 580 390 {}
N -25 450 15 450 {}
N 1685 450 1725 450 {}
N -1070 460 -705 460 {}
N -365 460 275 460 {}
N -85 490 -25 490 {}
N 415 490 475 490 {}
N 1265 490 1465 490 {}
N 1725 490 1785 490 {}
N -1160 520 -1100 520 {}
N -1070 520 -1010 520 {}
N -765 520 -705 520 {}
N -665 520 -605 520 {}
N -425 520 -365 520 {}
N -325 520 -265 520 {}
N -85 520 -25 520 {}
N 95 520 125 520 {}
N 185 520 345 520 {}
N 415 520 475 520 {}
N 1405 520 1465 520 {}
N 1495 520 1525 520 {}
N 1725 520 1785 520 {}
N 1265 550 1325 550 {}
N 415 580 750 580 {}
N 765 580 1985 580 {}
N -705 590 -665 590 {}
N 375 590 415 590 {}
N 335 620 395 620 {}
N 355 630 825 630 {}
N 205 670 355 670 {}
N 335 680 395 680 {}
N 1265 720 1325 720 {}
N -765 780 -705 780 {}
N -665 780 -605 780 {}
N -425 780 -365 780 {}
N -325 780 -265 780 {}
N 345 780 375 780 {}
N 415 780 475 780 {}
N 1195 780 1225 780 {}
N 1265 780 1325 780 {}
N 175 840 620 840 {}
N 15 900 1195 900 {}
N -1690 920 2180 920 {}
C {devices/lab_wire.sym} 415 350 2 0 {name=l0 lab=abm_n}
C {devices/lab_wire.sym} 955 430 0 1 {name=l1 lab=abm_n}
C {devices/lab_wire.sym} -705 350 2 0 {name=l2 lab=abm_p}
C {devices/lab_wire.sym} -335 450 2 0 {name=l3 lab=cm_det}
C {devices/lab_wire.sym} 765 430 0 1 {name=l4 lab=cm_det}
C {devices/lab_wire.sym} 1925 430 0 1 {name=l5 lab=cm_det}
C {devices/lab_wire.sym} -365 610 2 0 {name=l6 lab=csrc_n}
C {devices/lab_wire.sym} 1265 610 2 0 {name=l7 lab=csrc_p}
C {devices/lab_wire.sym} -365 350 2 0 {name=l8 lab=drv_n}
C {devices/lab_wire.sym} -605 780 0 1 {name=l9 lab=drv_p}
C {devices/lab_wire.sym} 1265 350 2 0 {name=l10 lab=drv_p}
C {devices/lab_wire.sym} 720 0 0 0 {name=l11 lab=gnf_n}
C {devices/lab_wire.sym} -1170 60 2 0 {name=l12 lab=gnf_p}
C {devices/lab_wire.sym} -705 170 0 1 {name=l13 lab=gnf_p}
C {devices/lab_wire.sym} 720 260 0 0 {name=l14 lab=gpf_n}
C {devices/lab_wire.sym} -1170 320 2 0 {name=l15 lab=gpf_p}
C {devices/lab_wire.sym} -605 520 0 1 {name=l16 lab=gpf_p}
C {devices/lab_wire.sym} -265 780 0 1 {name=l17 lab=mir_n}
C {devices/lab_wire.sym} 1725 350 2 0 {name=l18 lab=mir_n}
C {devices/lab_wire.sym} -25 350 2 0 {name=l19 lab=mir_p}
C {devices/lab_wire.sym} -365 90 2 0 {name=l20 lab=psrc_n}
C {devices/lab_wire.sym} 1265 90 2 0 {name=l21 lab=psrc_p}
C {devices/lab_wire.sym} 1050 90 2 0 {name=l22 lab=tail}
C {devices/lab_wire.sym} -605 0 0 1 {name=l23 lab=vb1}
C {devices/lab_wire.sym} 315 0 0 0 {name=l24 lab=vb1}
C {devices/lab_wire.sym} 950 0 0 0 {name=l25 lab=vb1}
C {devices/lab_wire.sym} -265 260 0 1 {name=l26 lab=vb2}
C {devices/lab_wire.sym} 1165 260 0 0 {name=l27 lab=vb2}
C {devices/lab_wire.sym} -265 520 0 1 {name=l28 lab=vb3}
C {devices/lab_wire.sym} 1225 460 0 1 {name=l29 lab=vb3}
C {devices/lab_wire.sym} -265 0 0 1 {name=l30 lab=vcmfb}
C {devices/lab_wire.sym} 335 680 0 0 {name=l31 lab=vcmfb}
C {devices/lab_wire.sym} 1165 0 0 0 {name=l32 lab=vcmfb}
C {devices/lab_wire.sym} 765 610 2 0 {name=l33 lab=vcmfb_ref}
C {devices/lab_wire.sym} 820 90 2 0 {name=l34 lab=voutn}
C {devices/lab_wire.sym} 820 170 0 1 {name=l35 lab=voutn}
C {devices/lab_wire.sym} 125 520 0 0 {name=l36 lab=zc_n}
C {devices/lab_wire.sym} 955 610 2 0 {name=l37 lab=zc_n}
C {devices/lab_wire.sym} -1160 520 0 0 {name=l38 lab=zc_p}
C {devices/lab_wire.sym} 1495 520 0 0 {name=l39 lab=zc_p}
C {devices/lab_wire.sym} 1050 0 0 0 {name=l40 lab=vdd}
C {devices/lab_wire.sym} -425 354 2 0 {name=l41 lab=vdd}
C {devices/lab_wire.sym} 1265 260 0 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} -425 94 2 0 {name=l43 lab=vdd}
C {devices/lab_wire.sym} 1265 0 0 0 {name=l44 lab=vdd}
C {devices/lab_wire.sym} -765 94 2 0 {name=l45 lab=vdd}
C {devices/lab_wire.sym} -765 614 2 0 {name=l46 lab=vdd}
C {devices/lab_wire.sym} -1210 260 0 0 {name=l47 lab=vdd}
C {devices/lab_wire.sym} -25 260 0 0 {name=l48 lab=vdd}
C {devices/lab_wire.sym} 475 94 2 0 {name=l49 lab=vdd}
C {devices/lab_wire.sym} 475 614 2 0 {name=l50 lab=vdd}
C {devices/lab_wire.sym} 880 354 2 0 {name=l51 lab=vdd}
C {devices/lab_wire.sym} 1725 260 0 0 {name=l52 lab=vdd}
C {devices/lab_wire.sym} -765 354 2 0 {name=l53 lab=vss}
C {devices/lab_wire.sym} -1270 94 2 0 {name=l54 lab=vss}
C {devices/lab_wire.sym} -765 874 2 0 {name=l55 lab=vss}
C {devices/lab_wire.sym} 415 260 0 0 {name=l56 lab=vss}
C {devices/lab_wire.sym} 880 94 2 0 {name=l57 lab=vss}
C {devices/lab_wire.sym} 475 874 2 0 {name=l58 lab=vss}
C {devices/lab_wire.sym} -85 614 2 0 {name=l59 lab=vss}
C {devices/lab_wire.sym} 1785 614 2 0 {name=l60 lab=vss}
C {devices/lab_wire.sym} -425 874 2 0 {name=l61 lab=vss}
C {devices/lab_wire.sym} -425 614 2 0 {name=l62 lab=vss}
C {devices/lab_wire.sym} 1325 874 2 0 {name=l63 lab=vss}
C {devices/lab_wire.sym} 1265 520 0 0 {name=l64 lab=vss}
C {devices/lab_wire.sym} -1560 -90 0 1 {name=l65 lab=vcmfb_ref}
C {devices/lab_wire.sym} -1560 870 2 0 {name=l66 lab=vss}
C {devices/lab_wire.sym} -1560 610 2 0 {name=l67 lab=vss}
C {devices/lab_wire.sym} -1560 350 2 0 {name=l68 lab=vss}
C {devices/lab_wire.sym} -1560 90 2 0 {name=l69 lab=vss}
C {devices/lab_wire.sym} -1560 690 0 1 {name=l70 lab=vb1}
C {devices/lab_wire.sym} -1560 430 0 1 {name=l71 lab=vb2}
C {devices/lab_wire.sym} -1560 170 0 1 {name=l72 lab=vb3}
C {devices/lab_wire.sym} 620 690 0 1 {name=l73 lab=vss}
C {devices/lab_wire.sym} 335 620 0 0 {name=l74 lab=vss}
C {devices/lab_wire.sym} 175 690 0 1 {name=l75 lab=vss}
C {devices/ipin.sym} 45 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} 1595 260 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -1690 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1690 920 0 0 {name=p3 lab=vss}
C {devices/iopin.sym} -1270 390 0 0 {name=p4 lab=voutp}
C {devices/iopin.sym} 580 390 0 0 {name=p5 lab=voutn}
B 8 -461 442 1701 858 {fill=0}
T {NMOS Simple Current Mirror} -461 424 0 0 0.3 0.3 {layer=8}
B 10 -801 442 2161 858 {fill=0}
T {NMOS Simple Current Mirror} -801 424 0 0 0.3 0.3 {layer=10}
B 12 -461 182 2161 338 {fill=0}
T {PMOS Differential Pair} -461 164 0 0 0.3 0.3 {layer=12}
