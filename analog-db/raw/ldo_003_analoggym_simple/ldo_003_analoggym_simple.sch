v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_003_analoggym_simple} -720 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 445 260 1 0 {name=CC value='c_comp'}
C {devices/res_np.sym} 210 260 1 0 {name=RZ value='r_z'}
C {devices/res_np.sym} 230 520 0 0 {name=R_BLEED value='r_bleed'}
C {devices/vsource_np.sym} -680 520 0 0 {name=VB value="dc {vb_val}"}
C {devices/vsource_np.sym} -680 260 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 0 {name=M1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M2 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=M3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_nmos_np.sym} -170 520 0 1 {name=M5 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 340 0 0 0 {name=MP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -680 170 -680 230 {}
N -680 290 -680 350 {}
N -680 430 -680 490 {}
N -680 550 -680 610 {}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -360 290 -360 350 {}
N -250 520 -250 614 {}
N -190 320 -190 490 {}
N -190 550 -190 660 {}
N -20 0 -20 70 {}
N 20 -140 20 -30 {}
N 20 30 20 70 {}
N 20 170 20 230 {}
N 20 290 20 320 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 150 200 150 260 {}
N 180 200 180 260 {}
N 230 260 230 490 {}
N 230 550 230 660 {}
N 240 260 240 320 {}
N 290 0 290 260 {}
N 360 -140 360 -30 {}
N 360 30 360 460 {}
N 415 200 415 260 {}
N 420 0 420 94 {}
N 475 260 475 320 {}
N -740 -140 615 -140 {}
N -420 0 -360 0 {}
N -320 0 -260 0 {}
N -80 0 -20 0 {}
N 20 0 80 0 {}
N 260 0 320 0 {}
N 360 0 420 0 {}
N -20 70 20 70 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N -80 260 -20 260 {}
N 20 260 80 260 {}
N 150 260 180 260 {}
N 240 260 270 260 {}
N 385 260 415 260 {}
N 475 260 505 260 {}
N -360 320 20 320 {}
N 230 460 360 460 {}
N -250 520 -190 520 {}
N -150 520 -90 520 {}
N -740 660 615 660 {}
C {devices/lab_wire.sym} -740 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -740 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 240 320 2 0 {name=l2 lab=ncz}
C {devices/lab_wire.sym} 475 320 2 0 {name=l3 lab=ncz}
C {devices/lab_wire.sym} -260 0 0 1 {name=l4 lab=ndiode}
C {devices/lab_wire.sym} -80 0 0 0 {name=l5 lab=ndiode}
C {devices/lab_wire.sym} 20 170 0 1 {name=l6 lab=ndiode}
C {devices/lab_wire.sym} -360 90 2 0 {name=l7 lab=ngate}
C {devices/lab_wire.sym} 180 200 0 1 {name=l8 lab=ngate}
C {devices/lab_wire.sym} 260 0 0 0 {name=l9 lab=ngate}
C {devices/lab_wire.sym} -360 350 2 0 {name=l10 lab=ntail}
C {devices/lab_wire.sym} -90 520 0 1 {name=l11 lab=vb}
C {devices/lab_wire.sym} -80 260 0 0 {name=l12 lab=vout}
C {devices/lab_wire.sym} 360 90 2 0 {name=l13 lab=vout}
C {devices/lab_wire.sym} 415 200 0 1 {name=l14 lab=vout}
C {devices/lab_wire.sym} -260 260 0 1 {name=l15 lab=vref}
C {devices/lab_wire.sym} -420 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} 420 94 2 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} 80 354 2 0 {name=l19 lab=vss}
C {devices/lab_wire.sym} -420 354 2 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} -250 614 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} -680 610 2 0 {name=l22 lab=vss}
C {devices/lab_wire.sym} -680 350 2 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} -680 430 0 1 {name=l24 lab=vb}
C {devices/lab_wire.sym} -680 170 0 1 {name=l25 lab=vref}
C {devices/opin.sym} 755 30 0 0 {name=p0 lab=vout}
