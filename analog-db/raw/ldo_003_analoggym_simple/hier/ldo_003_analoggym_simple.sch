v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_003_analoggym_simple} -590 -540 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -220 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/dp_nmos_simple_1.sym} 220 0 0 0 {name=xdp_nmos_simple_1}
C {devices/capa_np.sym} -330 340 0 0 {name=CC value='c_comp'}
C {devices/res_np.sym} -110 340 0 0 {name=RZ value='r_z'}
C {devices/res_np.sym} 110 340 0 0 {name=R_BLEED value='r_bleed'}
C {devices/vsource_np.sym} -550 340 0 0 {name=VB value="dc {vb_val}"}
C {devices/vsource_np.sym} -550 120 0 0 {name=VLP value="dc 0"}
C {devices/vsource_np.sym} -550 -100 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_nmos_np.sym} 330 340 0 0 {name=M5 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 0 -340 0 0 {name=MP model=sg13_hv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -110 -20 -70 -20 {}
C {devices/lab_wire.sym} -70 -20 0 1 {name=l0 lab=ndiode}
N -110 20 -70 20 {}
C {devices/lab_wire.sym} -70 20 0 1 {name=l1 lab=ngate}
N -220 -80 -220 -120 {}
C {devices/lab_wire.sym} -220 -120 0 1 {name=l2 lab=vdd}
N 110 -20 70 -20 {}
C {devices/lab_wire.sym} 70 -20 0 0 {name=l3 lab=lp_brk}
N 110 20 70 20 {}
C {devices/lab_wire.sym} 70 20 0 0 {name=l4 lab=vref}
N 330 -40 370 -40 {}
C {devices/lab_wire.sym} 370 -40 0 1 {name=l5 lab=ndiode}
N 330 0 370 0 {}
C {devices/lab_wire.sym} 370 0 0 1 {name=l6 lab=ngate}
N 330 40 370 40 {}
C {devices/lab_wire.sym} 370 40 0 1 {name=l7 lab=ntail}
N 220 100 220 140 {}
C {devices/lab_wire.sym} 220 140 2 0 {name=l8 lab=vss}
N -330 310 -330 270 {}
C {devices/lab_wire.sym} -330 270 0 1 {name=l9 lab=ncz}
N -330 370 -330 410 {}
C {devices/lab_wire.sym} -330 410 2 0 {name=l10 lab=vout}
N -110 310 -110 270 {}
C {devices/lab_wire.sym} -110 270 0 1 {name=l11 lab=ncz}
N -110 370 -110 410 {}
C {devices/lab_wire.sym} -110 410 2 0 {name=l12 lab=ngate}
N 110 310 110 270 {}
C {devices/lab_wire.sym} 110 270 0 1 {name=l13 lab=vout}
N 110 370 110 410 {}
C {devices/lab_wire.sym} 110 410 2 0 {name=l14 lab=vss}
N -550 310 -550 270 {}
C {devices/lab_wire.sym} -550 270 0 1 {name=l15 lab=vb}
N -550 370 -550 410 {}
C {devices/lab_wire.sym} -550 410 2 0 {name=l16 lab=vss}
N -550 90 -550 50 {}
C {devices/lab_wire.sym} -550 50 0 1 {name=l17 lab=lp_brk}
N -550 150 -550 190 {}
C {devices/lab_wire.sym} -550 190 2 0 {name=l18 lab=vout}
N -550 -130 -550 -170 {}
C {devices/lab_wire.sym} -550 -170 0 1 {name=l19 lab=vref}
N -550 -70 -550 -30 {}
C {devices/lab_wire.sym} -550 -30 2 0 {name=l20 lab=vss}
N 350 310 350 270 {}
C {devices/lab_wire.sym} 350 270 0 1 {name=l21 lab=ntail}
N 310 340 270 340 {}
C {devices/lab_wire.sym} 270 340 0 0 {name=l22 lab=vb}
N 350 370 350 410 {}
C {devices/lab_wire.sym} 350 410 2 0 {name=l23 lab=vss}
N 350 340 390 340 {}
C {devices/lab_wire.sym} 390 340 0 1 {name=l24 lab=vss}
N 20 -310 20 -270 {}
C {devices/lab_wire.sym} 20 -270 2 0 {name=l25 lab=vout}
N -20 -340 -60 -340 {}
C {devices/lab_wire.sym} -60 -340 0 0 {name=l26 lab=ngate}
N 20 -370 20 -410 {}
C {devices/lab_wire.sym} 20 -410 0 1 {name=l27 lab=vdd}
N 20 -340 60 -340 {}
C {devices/lab_wire.sym} 60 -340 0 1 {name=l28 lab=vdd}
