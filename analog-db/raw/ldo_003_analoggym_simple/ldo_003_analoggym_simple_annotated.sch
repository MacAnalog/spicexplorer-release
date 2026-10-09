v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_003_analoggym_simple} -730 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 455 260 1 0 {name=CC value='c_comp'}
C {devices/res_np.sym} 220 260 1 0 {name=RZ value='r_z'}
C {devices/res_np.sym} 240 520 0 0 {name=R_BLEED value='r_bleed'}
C {devices/vsource_np.sym} -690 520 0 0 {name=VB value="dc \{vb_val\}" savecurrent=false}
C {devices/vsource_np.sym} -690 260 0 0 {name=VLP value="dc 0" savecurrent=false}
C {devices/vsource_np.sym} -690 0 0 0 {name=VREF value="dc \{vref_val\}" savecurrent=false}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 0 {name=M1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M2 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_nmos_np.sym} -170 520 0 1 {name=M5 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 350 0 0 0 {name=MP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -690 -90 -690 -30 {}
N -690 30 -690 90 {}
N -690 170 -690 230 {}
N -690 290 -690 350 {}
N -690 430 -690 490 {}
N -690 550 -690 610 {}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -360 290 -360 350 {}
N -250 520 -250 614 {}
N -190 320 -190 490 {}
N -190 550 -190 660 {}
N -40 60 -40 230 {}
N -20 0 -20 70 {}
N 20 -140 20 -30 {}
N 20 30 20 70 {}
N 20 290 20 320 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 240 460 240 490 {}
N 240 550 240 660 {}
N 250 260 250 320 {}
N 370 -140 370 -30 {}
N 370 30 370 460 {}
N 395 60 395 260 {}
N 430 0 430 94 {}
N 485 260 485 320 {}
N -750 -140 825 -140 {}
N -420 0 -360 0 {}
N -350 0 -20 0 {}
N 20 0 80 0 {}
N 270 0 330 0 {}
N 370 0 430 0 {}
N -40 60 20 60 {}
N 370 60 395 60 {}
N -20 70 20 70 {}
N -40 230 20 230 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N -80 260 -20 260 {}
N 20 260 80 260 {}
N 130 260 190 260 {}
N 250 260 280 260 {}
N 395 260 425 260 {}
N 485 260 515 260 {}
N -360 320 20 320 {}
N 240 460 370 460 {}
N -250 520 -190 520 {}
N -150 520 -90 520 {}
N -750 660 825 660 {}
C {devices/lab_wire.sym} -80 260 0 0 {name=l0 lab=lp_brk}
C {devices/lab_wire.sym} 250 320 2 0 {name=l1 lab=ncz}
C {devices/lab_wire.sym} 485 320 2 0 {name=l2 lab=ncz}
C {devices/lab_wire.sym} -260 0 0 1 {name=l3 lab=ndiode}
C {devices/lab_wire.sym} -360 90 2 0 {name=l4 lab=ngate}
C {devices/lab_wire.sym} 130 260 0 0 {name=l5 lab=ngate}
C {devices/lab_wire.sym} 270 0 0 0 {name=l6 lab=ngate}
C {devices/lab_wire.sym} -360 350 2 0 {name=l7 lab=ntail}
C {devices/lab_wire.sym} -90 520 0 1 {name=l8 lab=vb}
C {devices/lab_wire.sym} -260 260 0 1 {name=l9 lab=vref}
C {devices/lab_wire.sym} -420 94 2 0 {name=l10 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} 430 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} 80 354 2 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} -420 354 2 0 {name=l14 lab=vss}
C {devices/lab_wire.sym} -250 614 2 0 {name=l15 lab=vss}
C {devices/lab_wire.sym} -690 350 2 0 {name=l16 lab=vout}
C {devices/lab_wire.sym} -690 610 2 0 {name=l17 lab=vss}
C {devices/lab_wire.sym} -690 90 2 0 {name=l18 lab=vss}
C {devices/lab_wire.sym} -690 430 0 1 {name=l19 lab=vb}
C {devices/lab_wire.sym} -690 170 0 1 {name=l20 lab=lp_brk}
C {devices/lab_wire.sym} -690 -90 0 1 {name=l21 lab=vref}
C {devices/iopin.sym} -750 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -750 660 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 395 60 0 0 {name=p2 lab=vout}
B 8 -716 -78 376 78 {fill=0}
T {PMOS Simple Current Mirror} -716 -96 0 0 0.3 0.3 {layer=8}
B 10 -716 182 376 338 {fill=0}
T {NMOS Differential Pair} -716 164 0 0 0.3 0.3 {layer=10}
