v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_002_analoggym_folded_cascode} -1070 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 555 260 1 0 {name=CC value='c_comp'}
C {devices/res_np.sym} 180 390 0 0 {name=RZ value='r_z'}
C {devices/res_np.sym} 505 520 0 0 {name=R_BLEED value='r_bleed'}
C {devices/vsource_np.sym} -690 520 0 0 {name=VB1 value="dc \{vb1_val\}" savecurrent=false}
C {devices/vsource_np.sym} -690 260 0 0 {name=VB2 value="dc \{vb2_val\}" savecurrent=false}
C {devices/vsource_np.sym} -690 0 0 0 {name=VLP value="dc 0" savecurrent=false}
C {devices/vsource_np.sym} -1030 520 0 0 {name=VREF value="dc \{vref_val\}" savecurrent=false}
C {devices/sg13_lv_nmos_np.sym} -120 260 0 1 {name=M1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} 275 260 0 0 {name=M2 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} 60 0 0 0 {name=M4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} -340 260 0 1 {name=M5 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 60 260 0 0 {name=M6 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 1 {name=M7 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l}
C {devices/sg13_lv_nmos_np.sym} 60 520 0 0 {name=M8 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l}
C {devices/sg13_lv_nmos_np.sym} 275 520 0 0 {name=M9 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l}
C {devices/sg13_lv_pmos_np.sym} 455 0 0 0 {name=MP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -1030 430 -1030 490 {}
N -1030 550 -1030 610 {}
N -690 -90 -690 -30 {}
N -690 30 -690 90 {}
N -690 170 -690 230 {}
N -690 290 -690 350 {}
N -690 430 -690 490 {}
N -690 550 -690 610 {}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -420 520 -420 614 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -360 290 -360 490 {}
N -360 550 -360 660 {}
N -140 200 -140 230 {}
N -140 290 -140 320 {}
N -140 320 -140 350 {}
N 10 520 10 580 {}
N 20 290 20 460 {}
N 40 200 40 260 {}
N 80 -140 80 -30 {}
N 80 30 80 230 {}
N 80 460 80 490 {}
N 80 550 80 660 {}
N 140 0 140 94 {}
N 140 260 140 354 {}
N 140 520 140 614 {}
N 180 330 180 360 {}
N 180 420 180 460 {}
N 225 520 225 580 {}
N 295 200 295 230 {}
N 295 290 295 490 {}
N 295 550 295 660 {}
N 355 260 355 354 {}
N 355 520 355 614 {}
N 405 0 405 450 {}
N 435 -60 435 0 {}
N 475 -140 475 -30 {}
N 475 30 475 60 {}
N 495 60 495 260 {}
N 505 260 505 490 {}
N 505 550 505 660 {}
N 535 0 535 94 {}
N 585 260 585 320 {}
N 615 260 615 330 {}
N -1090 -140 930 -140 {}
N -420 0 -360 0 {}
N -320 0 40 0 {}
N 80 0 140 0 {}
N 405 0 435 0 {}
N 475 0 535 0 {}
N 475 60 495 60 {}
N -360 200 -140 200 {}
N 80 200 295 200 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N -100 260 -70 260 {}
N 10 260 40 260 {}
N 80 260 140 260 {}
N 195 260 255 260 {}
N 295 260 355 260 {}
N 495 260 525 260 {}
N 585 260 615 260 {}
N 20 290 80 290 {}
N -200 320 295 320 {}
N 180 330 615 330 {}
N 180 450 405 450 {}
N 20 460 180 460 {}
N -420 520 -360 520 {}
N -320 520 40 520 {}
N 80 520 140 520 {}
N 225 520 255 520 {}
N 295 520 355 520 {}
N 10 580 225 580 {}
N -1090 660 930 660 {}
C {devices/lab_wire.sym} -100 260 0 0 {name=l0 lab=lp_brk}
C {devices/lab_wire.sym} -360 90 2 0 {name=l1 lab=n2}
C {devices/lab_wire.sym} 80 90 2 0 {name=l2 lab=n3}
C {devices/lab_wire.sym} -140 350 2 0 {name=l3 lab=n4}
C {devices/lab_wire.sym} 585 320 2 0 {name=l4 lab=ncz}
C {devices/lab_wire.sym} 435 -60 0 1 {name=l5 lab=ngate}
C {devices/lab_wire.sym} -360 350 2 0 {name=l6 lab=nmir}
C {devices/lab_wire.sym} -260 0 0 1 {name=l7 lab=nmir}
C {devices/lab_wire.sym} -260 520 0 1 {name=l8 lab=vb1}
C {devices/lab_wire.sym} -260 260 0 1 {name=l9 lab=vb2}
C {devices/lab_wire.sym} 40 200 0 1 {name=l10 lab=vb2}
C {devices/lab_wire.sym} 195 260 0 0 {name=l11 lab=vref}
C {devices/lab_wire.sym} -420 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} 140 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} -420 354 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} 140 354 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} 535 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} -140 260 0 0 {name=l17 lab=vss}
C {devices/lab_wire.sym} 355 354 2 0 {name=l18 lab=vss}
C {devices/lab_wire.sym} -420 614 2 0 {name=l19 lab=vss}
C {devices/lab_wire.sym} 140 614 2 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} 355 614 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} -690 90 2 0 {name=l22 lab=vout}
C {devices/lab_wire.sym} -690 610 2 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} -690 350 2 0 {name=l24 lab=vss}
C {devices/lab_wire.sym} -1030 610 2 0 {name=l25 lab=vss}
C {devices/lab_wire.sym} -690 430 0 1 {name=l26 lab=vb1}
C {devices/lab_wire.sym} -690 170 0 1 {name=l27 lab=vb2}
C {devices/lab_wire.sym} -690 -90 0 1 {name=l28 lab=lp_brk}
C {devices/lab_wire.sym} -1030 430 0 1 {name=l29 lab=vref}
C {devices/iopin.sym} -1090 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -1090 660 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 505 260 0 0 {name=p2 lab=vout}
B 8 -496 182 651 338 {fill=0}
T {NMOS Differential Pair} -496 164 0 0 0.3 0.3 {layer=8}
