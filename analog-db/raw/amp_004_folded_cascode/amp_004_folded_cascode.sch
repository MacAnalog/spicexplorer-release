v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_004_folded_cascode} -895 -200 0 0 0.4 0.4 {}
C {devices/vsource_np.sym} -855 780 0 0 {name=V1 value=x_dut_vb1 savecurrent=false}
C {devices/vsource_np.sym} -855 520 0 0 {name=V2 value=x_dut_vb2 savecurrent=false}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M0 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm0_w l=x_dut_xm0_l ng=x_dut_xm0_ng m=x_dut_xm0_m}
C {devices/sg13_lv_pmos_np.sym} 1040 260 0 0 {name=M1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l ng=x_dut_xm1_ng m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} 390 0 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l ng=x_dut_xm10_ng m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=M11 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l ng=x_dut_xm11_ng m=x_dut_xm11_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=M12 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l ng=x_dut_xm12_ng m=x_dut_xm12_m}
C {devices/sg13_lv_nmos_np.sym} -170 260 0 1 {name=M13 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm13_w l=x_dut_xm13_l ng=x_dut_xm13_ng m=x_dut_xm13_m}
C {devices/sg13_lv_pmos_np.sym} 625 260 0 1 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l ng=x_dut_xm2_ng m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 805 780 0 0 {name=M3 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l ng=x_dut_xm3_ng m=x_dut_xm3_m}
C {devices/sg13_lv_nmos_np.sym} 390 780 0 1 {name=M4 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l ng=x_dut_xm4_ng m=x_dut_xm4_m}
C {devices/sg13_lv_nmos_np.sym} 805 520 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l ng=x_dut_xm5_ng m=x_dut_xm5_m}
C {devices/sg13_lv_nmos_np.sym} 390 520 0 1 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l ng=x_dut_xm6_ng m=x_dut_xm6_m}
C {devices/sg13_lv_pmos_np.sym} 805 260 0 0 {name=M7 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l ng=x_dut_xm7_ng m=x_dut_xm7_m}
C {devices/sg13_lv_pmos_np.sym} 390 260 0 1 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l ng=x_dut_xm8_ng m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 805 0 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l ng=x_dut_xm9_ng m=x_dut_xm9_m}
N -855 430 -855 490 {}
N -855 550 -855 610 {}
N -855 690 -855 750 {}
N -855 810 -855 870 {}
N -590 0 -590 94 {}
N -530 -140 -530 -30 {}
N -530 30 -530 70 {}
N -490 0 -490 70 {}
N -250 30 -250 200 {}
N -250 260 -250 354 {}
N -190 -140 -190 -30 {}
N -190 30 -190 90 {}
N -190 190 -190 230 {}
N -190 290 -190 920 {}
N -150 190 -150 840 {}
N -40 60 -40 200 {}
N 20 -140 20 -30 {}
N 20 30 20 90 {}
N 80 0 80 94 {}
N 310 0 310 94 {}
N 310 260 310 354 {}
N 310 520 310 614 {}
N 310 780 310 874 {}
N 370 -140 370 -30 {}
N 370 30 370 90 {}
N 370 170 370 230 {}
N 370 290 370 490 {}
N 370 550 370 750 {}
N 370 810 370 920 {}
N 440 780 440 840 {}
N 545 260 545 354 {}
N 605 200 605 230 {}
N 605 290 605 580 {}
N 695 0 695 320 {}
N 765 60 765 230 {}
N 825 -140 825 -30 {}
N 825 30 825 90 {}
N 825 290 825 490 {}
N 825 550 825 750 {}
N 825 810 825 920 {}
N 885 0 885 94 {}
N 885 260 885 354 {}
N 885 520 885 614 {}
N 885 780 885 874 {}
N 1060 200 1060 230 {}
N 1060 290 1060 580 {}
N 1120 260 1120 354 {}
N -1105 -140 1605 -140 {}
N -590 0 -530 0 {}
N -490 0 -430 0 {}
N -150 0 -20 0 {}
N 20 0 80 0 {}
N 310 0 370 0 {}
N 410 0 785 0 {}
N 825 0 885 0 {}
N -250 30 -190 30 {}
N -40 60 20 60 {}
N 765 60 825 60 {}
N -530 70 -490 70 {}
N -190 190 -150 190 {}
N -250 200 -190 200 {}
N -40 200 1060 200 {}
N 765 230 825 230 {}
N -250 260 -190 260 {}
N 310 260 370 260 {}
N 410 260 470 260 {}
N 545 260 605 260 {}
N 645 260 675 260 {}
N 755 260 785 260 {}
N 825 260 885 260 {}
N 930 260 1020 260 {}
N 1060 260 1120 260 {}
N 695 320 825 320 {}
N 310 520 370 520 {}
N 410 520 815 520 {}
N 825 520 885 520 {}
N 370 580 605 580 {}
N 825 580 1060 580 {}
N 310 780 370 780 {}
N 410 780 785 780 {}
N 825 780 885 780 {}
N -150 840 440 840 {}
N -1105 920 1605 920 {}
C {devices/lab_wire.sym} 470 0 0 1 {name=l0 lab=cascp}
C {devices/lab_wire.sym} 605 350 2 0 {name=l1 lab=foldn}
C {devices/lab_wire.sym} 1060 350 2 0 {name=l2 lab=foldp}
C {devices/lab_wire.sym} -430 0 0 1 {name=l3 lab=ibias}
C {devices/lab_wire.sym} -190 90 2 0 {name=l4 lab=nbias}
C {devices/lab_wire.sym} 370 90 2 0 {name=l5 lab=s10}
C {devices/lab_wire.sym} 370 170 0 1 {name=l6 lab=s10}
C {devices/lab_wire.sym} 825 90 2 0 {name=l7 lab=s9}
C {devices/lab_wire.sym} 20 90 2 0 {name=l8 lab=tail}
C {devices/lab_wire.sym} 470 520 0 1 {name=l9 lab=vb1}
C {devices/lab_wire.sym} 470 260 0 1 {name=l10 lab=vb2}
C {devices/lab_wire.sym} 785 260 0 0 {name=l11 lab=vb2}
C {devices/lab_wire.sym} 80 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} 1120 354 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} 310 94 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} -590 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} -190 0 0 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 545 354 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} 885 354 2 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} 310 354 2 0 {name=l19 lab=vdd}
C {devices/lab_wire.sym} 885 94 2 0 {name=l20 lab=vdd}
C {devices/lab_wire.sym} -250 354 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} 885 874 2 0 {name=l22 lab=vss}
C {devices/lab_wire.sym} 310 874 2 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} 885 614 2 0 {name=l24 lab=vss}
C {devices/lab_wire.sym} 310 614 2 0 {name=l25 lab=vss}
C {devices/lab_wire.sym} -855 690 0 1 {name=l26 lab=vb1}
C {devices/lab_wire.sym} -855 870 2 0 {name=l27 lab=vss}
C {devices/lab_wire.sym} -855 610 2 0 {name=l28 lab=vss}
C {devices/lab_wire.sym} -855 430 0 1 {name=l29 lab=vb2}
C {devices/ipin.sym} 675 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} 930 260 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -1105 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1105 920 0 0 {name=p3 lab=vss}
C {devices/opin.sym} -50 0 0 0 {name=p4 lab=ibias}
C {devices/opin.sym} 370 320 0 0 {name=p5 lab=vout}
