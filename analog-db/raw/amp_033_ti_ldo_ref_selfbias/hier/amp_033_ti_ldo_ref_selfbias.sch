v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_033_ti_ldo_ref_selfbias} -480 -540 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -440 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_simple_1.sym} 0 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_nmos_simple_1.sym} 440 0 0 0 {name=xdp_nmos_simple_1}
C {devices/capa_np.sym} -110 340 0 0 {name=CC value='c_comp'}
C {devices/res_np.sym} 110 340 0 0 {name=RZ value='r_z'}
C {devices/sg13_lv_pmos_np.sym} -110 -340 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 110 -340 0 0 {name=MBP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmbp_w l=x_dut_xmbp_l}
N -330 -20 -290 -20 {}
C {devices/lab_wire.sym} -290 -20 0 1 {name=l0 lab=na}
N -330 20 -290 20 {}
C {devices/lab_wire.sym} -290 20 0 1 {name=l1 lab=nb}
N -440 -80 -440 -120 {}
C {devices/lab_wire.sym} -440 -120 0 1 {name=l2 lab=vdd}
N 110 -40 150 -40 {}
C {devices/lab_wire.sym} 150 -40 0 1 {name=l3 lab=ibias}
N 110 0 150 0 {}
C {devices/lab_wire.sym} 150 0 0 1 {name=l4 lab=tail}
N 110 40 150 40 {}
C {devices/lab_wire.sym} 150 40 0 1 {name=l5 lab=vout}
N 0 100 0 140 {}
C {devices/lab_wire.sym} 0 140 2 0 {name=l6 lab=vss}
N 330 -20 290 -20 {}
C {devices/lab_wire.sym} 290 -20 0 0 {name=l7 lab=vinn}
N 330 20 290 20 {}
C {devices/lab_wire.sym} 290 20 0 0 {name=l8 lab=vinp}
N 550 -40 590 -40 {}
C {devices/lab_wire.sym} 590 -40 0 1 {name=l9 lab=na}
N 550 0 590 0 {}
C {devices/lab_wire.sym} 590 0 0 1 {name=l10 lab=nb}
N 550 40 590 40 {}
C {devices/lab_wire.sym} 590 40 0 1 {name=l11 lab=tail}
N 440 100 440 140 {}
C {devices/lab_wire.sym} 440 140 2 0 {name=l12 lab=vss}
N -110 310 -110 270 {}
C {devices/lab_wire.sym} -110 270 0 1 {name=l13 lab=ncz}
N -110 370 -110 410 {}
C {devices/lab_wire.sym} -110 410 2 0 {name=l14 lab=vout}
N 110 310 110 270 {}
C {devices/lab_wire.sym} 110 270 0 1 {name=l15 lab=nb}
N 110 370 110 410 {}
C {devices/lab_wire.sym} 110 410 2 0 {name=l16 lab=ncz}
N -90 -310 -90 -270 {}
C {devices/lab_wire.sym} -90 -270 2 0 {name=l17 lab=vout}
N -130 -340 -170 -340 {}
C {devices/lab_wire.sym} -170 -340 0 0 {name=l18 lab=nb}
N -90 -370 -90 -410 {}
C {devices/lab_wire.sym} -90 -410 0 1 {name=l19 lab=vdd}
N -90 -340 -50 -340 {}
C {devices/lab_wire.sym} -50 -340 0 1 {name=l20 lab=vdd}
N 130 -310 130 -270 {}
C {devices/lab_wire.sym} 130 -270 2 0 {name=l21 lab=ibias}
N 90 -340 50 -340 {}
C {devices/lab_wire.sym} 50 -340 0 0 {name=l22 lab=ibias}
N 130 -370 130 -410 {}
C {devices/lab_wire.sym} 130 -410 0 1 {name=l23 lab=vdd}
N 130 -340 170 -340 {}
C {devices/lab_wire.sym} 170 -340 0 1 {name=l24 lab=vdd}
