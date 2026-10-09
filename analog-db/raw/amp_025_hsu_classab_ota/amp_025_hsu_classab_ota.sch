v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_025_hsu_classab_ota} -1600 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 895 520 1 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} 2065 520 1 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} 1380 520 0 0 {name=CIN value='cin_val'}
C {devices/capa_np.sym} -505 780 0 0 {name=COUT value='cout_val'}
C {devices/vccs.sym} -35 650 1 0 {name=GM value="\{gm_val\}"}
C {devices/res_np.sym} 1140 520 0 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} 435 520 1 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} -1020 520 0 0 {name=RIN value='rin_val'}
C {devices/res_np.sym} 575 390 1 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 905 390 1 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} -700 780 0 0 {name=ROUT value='rout_val'}
C {devices/vsource_np.sym} -1560 780 0 0 {name=VB1 value="dc \{vb1\}" savecurrent=false}
C {devices/vsource_np.sym} -1560 520 0 0 {name=VB2 value="dc \{vb2\}" savecurrent=false}
C {devices/vsource_np.sym} -1560 260 0 0 {name=VB3 value="dc \{vb3\}" savecurrent=false}
C {devices/vsource_np.sym} -1560 0 0 0 {name=VCMFB_REF value="dc \{vcmfb_ref\}" savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 50 0 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -1190 260 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 220 260 0 0 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} -1190 0 0 1 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l m=x_dut_xm12_m}
C {devices/sg13_lv_pmos_np.sym} 220 0 0 0 {name=M13 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l m=x_dut_xm13_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M14 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm14_w l=x_dut_xm14_l m=x_dut_xm14_m}
C {devices/sg13_lv_nmos_np.sym} -170 260 0 1 {name=M15 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm15_w l=x_dut_xm15_l m=x_dut_xm15_m}
C {devices/sg13_lv_nmos_np.sym} 1500 0 0 0 {name=M16 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm16_w l=x_dut_xm16_l m=x_dut_xm16_m}
C {devices/sg13_lv_pmos_np.sym} -170 520 0 1 {name=M17 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm17_w l=x_dut_xm17_l m=x_dut_xm17_m}
C {devices/sg13_lv_pmos_np.sym} 1500 260 0 0 {name=M18 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm18_w l=x_dut_xm18_l m=x_dut_xm18_m}
C {devices/sg13_lv_nmos_np.sym} -170 780 0 1 {name=M19 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm19_w l=x_dut_xm19_l m=x_dut_xm19_m}
C {devices/sg13_lv_pmos_np.sym} -700 260 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} 1840 0 0 0 {name=M20 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm20_w l=x_dut_xm20_l m=x_dut_xm20_m}
C {devices/sg13_lv_nmos_np.sym} 1840 260 0 0 {name=M21 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm21_w l=x_dut_xm21_l m=x_dut_xm21_m}
C {devices/sg13_lv_nmos_np.sym} 1140 0 0 1 {name=M22 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm22_w l=x_dut_xm22_l m=x_dut_xm22_m}
C {devices/sg13_lv_pmos_np.sym} 1840 520 0 0 {name=M23 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm23_w l=x_dut_xm23_l m=x_dut_xm23_m}
C {devices/sg13_lv_pmos_np.sym} 1140 260 0 1 {name=M24 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm24_w l=x_dut_xm24_l m=x_dut_xm24_m}
C {devices/sg13_lv_nmos_np.sym} 1840 780 0 0 {name=M25 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm25_w l=x_dut_xm25_l m=x_dut_xm25_m}
C {devices/sg13_lv_pmos_np.sym} 680 260 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} -700 520 0 1 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 680 520 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_nmos_np.sym} -1190 780 0 1 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} -1190 520 0 1 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_nmos_np.sym} 220 780 0 0 {name=M8 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_nmos_np.sym} 220 520 0 0 {name=M9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1560 -90 -1560 -30 {}
N -1560 30 -1560 90 {}
N -1560 170 -1560 230 {}
N -1560 290 -1560 350 {}
N -1560 430 -1560 490 {}
N -1560 550 -1560 610 {}
N -1560 690 -1560 750 {}
N -1560 810 -1560 870 {}
N -1270 0 -1270 94 {}
N -1270 260 -1270 354 {}
N -1270 520 -1270 614 {}
N -1270 780 -1270 874 {}
N -1210 -140 -1210 -30 {}
N -1210 30 -1210 230 {}
N -1210 290 -1210 490 {}
N -1210 550 -1210 750 {}
N -1210 810 -1210 920 {}
N -1170 260 -1170 320 {}
N -1170 520 -1170 580 {}
N -1140 140 -1140 260 {}
N -1140 400 -1140 520 {}
N -1020 430 -1020 490 {}
N -1020 550 -1020 610 {}
N -780 320 -780 490 {}
N -780 520 -780 614 {}
N -720 200 -720 230 {}
N -720 290 -720 350 {}
N -720 450 -720 490 {}
N -720 550 -720 920 {}
N -700 690 -700 750 {}
N -700 810 -700 840 {}
N -680 450 -680 520 {}
N -640 0 -640 840 {}
N -505 690 -505 750 {}
N -505 810 -505 840 {}
N -250 60 -250 230 {}
N -250 320 -250 490 {}
N -250 550 -250 720 {}
N -250 780 -250 874 {}
N -190 -140 -190 -30 {}
N -190 30 -190 90 {}
N -190 190 -190 230 {}
N -190 290 -190 350 {}
N -190 550 -190 590 {}
N -190 720 -190 750 {}
N -190 810 -190 920 {}
N -150 190 -150 260 {}
N -150 520 -150 590 {}
N -120 -60 -120 0 {}
N -115 390 -115 610 {}
N -95 650 -95 840 {}
N -30 30 -30 200 {}
N -5 650 -5 920 {}
N 30 -140 30 -30 {}
N 30 30 30 90 {}
N 45 580 45 610 {}
N 90 30 90 200 {}
N 100 -60 100 0 {}
N 170 140 170 260 {}
N 170 460 170 780 {}
N 180 30 180 230 {}
N 180 320 180 490 {}
N 180 550 180 720 {}
N 200 -60 200 0 {}
N 200 400 200 520 {}
N 240 -140 240 -30 {}
N 240 30 240 90 {}
N 240 290 240 350 {}
N 240 550 240 610 {}
N 240 720 240 750 {}
N 240 810 240 920 {}
N 300 0 300 94 {}
N 300 260 300 354 {}
N 300 520 300 614 {}
N 300 780 300 874 {}
N 465 520 465 580 {}
N 515 330 515 390 {}
N 660 450 660 520 {}
N 700 200 700 230 {}
N 700 290 700 350 {}
N 700 430 700 490 {}
N 700 550 700 920 {}
N 760 260 760 354 {}
N 760 520 760 614 {}
N 905 390 905 460 {}
N 925 520 925 580 {}
N 965 330 965 390 {}
N 1060 30 1060 200 {}
N 1060 260 1060 354 {}
N 1120 -140 1120 -30 {}
N 1120 30 1120 90 {}
N 1120 200 1120 230 {}
N 1120 290 1120 920 {}
N 1140 430 1140 490 {}
N 1140 550 1140 610 {}
N 1190 0 1190 120 {}
N 1190 260 1190 580 {}
N 1380 460 1380 490 {}
N 1380 550 1380 610 {}
N 1520 -140 1520 -30 {}
N 1520 30 1520 230 {}
N 1520 290 1520 920 {}
N 1580 0 1580 94 {}
N 1580 260 1580 354 {}
N 1820 190 1820 260 {}
N 1820 520 1820 590 {}
N 1860 -140 1860 -30 {}
N 1860 30 1860 230 {}
N 1860 290 1860 490 {}
N 1860 550 1860 750 {}
N 1860 810 1860 920 {}
N 1920 0 1920 94 {}
N 1920 260 1920 354 {}
N 1920 520 1920 614 {}
N 1920 780 1920 874 {}
N 2125 460 2125 520 {}
N -1690 -140 2375 -140 {}
N -120 -60 100 -60 {}
N -1270 0 -1210 0 {}
N -1170 0 -640 0 {}
N -150 0 -90 0 {}
N 70 0 100 0 {}
N 170 0 200 0 {}
N 240 0 300 0 {}
N 1160 0 1220 0 {}
N 1420 0 1480 0 {}
N 1520 0 1580 0 {}
N 1760 0 1820 0 {}
N 1860 0 1920 0 {}
N -30 30 90 30 {}
N 180 30 240 30 {}
N 1060 30 1120 30 {}
N -250 60 -190 60 {}
N 1190 120 1860 120 {}
N -1140 140 170 140 {}
N -190 190 -150 190 {}
N 1820 190 1860 190 {}
N -720 200 700 200 {}
N 1060 200 1120 200 {}
N -250 230 -190 230 {}
N 180 230 240 230 {}
N -1270 260 -1210 260 {}
N -1170 260 -1140 260 {}
N -680 260 -650 260 {}
N 170 260 200 260 {}
N 240 260 300 260 {}
N 570 260 660 260 {}
N 700 260 760 260 {}
N 1060 260 1120 260 {}
N 1160 260 1220 260 {}
N 1420 260 1480 260 {}
N 1520 260 1580 260 {}
N 1860 260 1920 260 {}
N -780 320 -720 320 {}
N -250 320 -190 320 {}
N 180 320 240 320 {}
N 515 330 965 330 {}
N -115 390 545 390 {}
N 605 390 635 390 {}
N 845 390 875 390 {}
N 905 390 965 390 {}
N -1140 400 200 400 {}
N -720 450 -680 450 {}
N 660 450 700 450 {}
N -680 460 170 460 {}
N 905 460 1380 460 {}
N 1860 460 2125 460 {}
N -780 490 -720 490 {}
N -250 490 -190 490 {}
N 180 490 240 490 {}
N -1270 520 -1210 520 {}
N -1170 520 -1140 520 {}
N -780 520 -720 520 {}
N -150 520 -90 520 {}
N 240 520 300 520 {}
N 345 520 405 520 {}
N 465 520 495 520 {}
N 700 520 760 520 {}
N 805 520 865 520 {}
N 925 520 955 520 {}
N 1860 520 1920 520 {}
N 1975 520 2035 520 {}
N 2095 520 2125 520 {}
N -250 550 -190 550 {}
N 180 550 240 550 {}
N -1020 580 45 580 {}
N 1190 580 1820 580 {}
N -190 590 -150 590 {}
N 1820 590 1860 590 {}
N -115 610 -55 610 {}
N -15 610 45 610 {}
N -95 650 -65 650 {}
N -250 720 -190 720 {}
N 180 720 240 720 {}
N -1270 780 -1210 780 {}
N -1170 780 -1110 780 {}
N -250 780 -190 780 {}
N -150 780 -90 780 {}
N 170 780 200 780 {}
N 240 780 300 780 {}
N 1760 780 1820 780 {}
N 1860 780 1920 780 {}
N -700 840 -95 840 {}
N -1690 920 2375 920 {}
C {devices/lab_wire.sym} 1860 350 2 0 {name=l0 lab=abm_n}
C {devices/lab_wire.sym} -190 350 2 0 {name=l1 lab=abm_p}
C {devices/lab_wire.sym} 925 580 2 0 {name=l2 lab=abm_p}
C {devices/lab_wire.sym} -1020 430 0 1 {name=l3 lab=cm_det}
C {devices/lab_wire.sym} 485 390 0 0 {name=l4 lab=cm_det}
C {devices/lab_wire.sym} -1210 610 2 0 {name=l5 lab=csrc_n}
C {devices/lab_wire.sym} 240 610 2 0 {name=l6 lab=csrc_p}
C {devices/lab_wire.sym} -1210 350 2 0 {name=l7 lab=drv_n}
C {devices/lab_wire.sym} 465 580 2 0 {name=l8 lab=drv_n}
C {devices/lab_wire.sym} 1760 780 0 0 {name=l9 lab=drv_n}
C {devices/lab_wire.sym} -90 780 0 1 {name=l10 lab=drv_p}
C {devices/lab_wire.sym} 240 350 2 0 {name=l11 lab=drv_p}
C {devices/lab_wire.sym} 1140 610 2 0 {name=l12 lab=drv_p}
C {devices/lab_wire.sym} 1220 0 0 1 {name=l13 lab=gnf_n}
C {devices/lab_wire.sym} -190 90 2 0 {name=l14 lab=gnf_p}
C {devices/lab_wire.sym} 1420 0 0 0 {name=l15 lab=gnf_p}
C {devices/lab_wire.sym} 1220 260 0 1 {name=l16 lab=gpf_n}
C {devices/lab_wire.sym} -90 520 0 1 {name=l17 lab=gpf_p}
C {devices/lab_wire.sym} 1420 260 0 0 {name=l18 lab=gpf_p}
C {devices/lab_wire.sym} -1110 780 0 1 {name=l19 lab=mir_n}
C {devices/lab_wire.sym} 700 430 0 1 {name=l20 lab=mir_n}
C {devices/lab_wire.sym} 700 350 2 0 {name=l21 lab=mir_n}
C {devices/lab_wire.sym} -720 350 2 0 {name=l22 lab=mir_p}
C {devices/lab_wire.sym} -1210 90 2 0 {name=l23 lab=psrc_n}
C {devices/lab_wire.sym} 240 90 2 0 {name=l24 lab=psrc_p}
C {devices/lab_wire.sym} 30 90 2 0 {name=l25 lab=tail}
C {devices/lab_wire.sym} -90 0 0 1 {name=l26 lab=vb1}
C {devices/lab_wire.sym} 1760 0 0 0 {name=l27 lab=vb1}
C {devices/lab_wire.sym} -1170 320 2 0 {name=l28 lab=vb2}
C {devices/lab_wire.sym} -1170 580 2 0 {name=l29 lab=vb3}
C {devices/lab_wire.sym} -1110 0 0 1 {name=l30 lab=vcmfb}
C {devices/lab_wire.sym} 200 -60 0 1 {name=l31 lab=vcmfb}
C {devices/lab_wire.sym} -1020 610 2 0 {name=l32 lab=vcmfb_ref}
C {devices/lab_wire.sym} 1380 610 2 0 {name=l33 lab=vcmfb_ref}
C {devices/lab_wire.sym} 1120 90 2 0 {name=l34 lab=voutn}
C {devices/lab_wire.sym} 1520 90 2 0 {name=l35 lab=voutp}
C {devices/lab_wire.sym} 345 520 0 0 {name=l36 lab=zc_n}
C {devices/lab_wire.sym} 1975 520 0 0 {name=l37 lab=zc_n}
C {devices/lab_wire.sym} 805 520 0 0 {name=l38 lab=zc_p}
C {devices/lab_wire.sym} 1140 430 0 1 {name=l39 lab=zc_p}
C {devices/lab_wire.sym} 30 0 0 0 {name=l40 lab=vdd}
C {devices/lab_wire.sym} -1270 354 2 0 {name=l41 lab=vdd}
C {devices/lab_wire.sym} 300 354 2 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} -1270 94 2 0 {name=l43 lab=vdd}
C {devices/lab_wire.sym} 300 94 2 0 {name=l44 lab=vdd}
C {devices/lab_wire.sym} -190 0 0 0 {name=l45 lab=vdd}
C {devices/lab_wire.sym} -190 520 0 0 {name=l46 lab=vdd}
C {devices/lab_wire.sym} 1580 354 2 0 {name=l47 lab=vdd}
C {devices/lab_wire.sym} -720 260 0 0 {name=l48 lab=vdd}
C {devices/lab_wire.sym} 1920 94 2 0 {name=l49 lab=vdd}
C {devices/lab_wire.sym} 1920 614 2 0 {name=l50 lab=vdd}
C {devices/lab_wire.sym} 1060 354 2 0 {name=l51 lab=vdd}
C {devices/lab_wire.sym} 760 354 2 0 {name=l52 lab=vdd}
C {devices/lab_wire.sym} -190 260 0 0 {name=l53 lab=vss}
C {devices/lab_wire.sym} 1580 94 2 0 {name=l54 lab=vss}
C {devices/lab_wire.sym} -250 874 2 0 {name=l55 lab=vss}
C {devices/lab_wire.sym} 1920 354 2 0 {name=l56 lab=vss}
C {devices/lab_wire.sym} 1120 0 0 0 {name=l57 lab=vss}
C {devices/lab_wire.sym} 1920 874 2 0 {name=l58 lab=vss}
C {devices/lab_wire.sym} -780 614 2 0 {name=l59 lab=vss}
C {devices/lab_wire.sym} 760 614 2 0 {name=l60 lab=vss}
C {devices/lab_wire.sym} -1270 874 2 0 {name=l61 lab=vss}
C {devices/lab_wire.sym} -1270 614 2 0 {name=l62 lab=vss}
C {devices/lab_wire.sym} 300 874 2 0 {name=l63 lab=vss}
C {devices/lab_wire.sym} 300 614 2 0 {name=l64 lab=vss}
C {devices/lab_wire.sym} -1560 -90 0 1 {name=l65 lab=vcmfb_ref}
C {devices/lab_wire.sym} -1560 870 2 0 {name=l66 lab=vss}
C {devices/lab_wire.sym} -1560 610 2 0 {name=l67 lab=vss}
C {devices/lab_wire.sym} -1560 350 2 0 {name=l68 lab=vss}
C {devices/lab_wire.sym} -1560 90 2 0 {name=l69 lab=vss}
C {devices/lab_wire.sym} -1560 690 0 1 {name=l70 lab=vb1}
C {devices/lab_wire.sym} -1560 430 0 1 {name=l71 lab=vb2}
C {devices/lab_wire.sym} -1560 170 0 1 {name=l72 lab=vb3}
C {devices/lab_wire.sym} -505 690 0 1 {name=l73 lab=vss}
C {devices/lab_wire.sym} -700 690 0 1 {name=l74 lab=vss}
C {devices/ipin.sym} -650 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} 570 260 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -1690 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1690 920 0 0 {name=p3 lab=vss}
C {devices/iopin.sym} 635 390 0 0 {name=p4 lab=voutn}
C {devices/iopin.sym} 845 390 0 0 {name=p5 lab=voutp}
