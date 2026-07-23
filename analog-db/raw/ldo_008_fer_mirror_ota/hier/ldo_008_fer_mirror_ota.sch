v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_008_fer_mirror_ota} -700 -540 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -440 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_simple_1.sym} 0 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_nmos_simple_1.sym} 440 0 0 0 {name=xdp_nmos_simple_1}
C {devices/capa_np.sym} -330 340 0 0 {name=CC value=x_ccomp}
C {devices/isource_np.sym} -660 340 0 0 {name=IBI value="dc {x_ibias_val}"}
C {devices/res_np.sym} -110 340 0 0 {name=RB value=x_dut_rb_value}
C {devices/res_np.sym} 110 340 0 0 {name=RC value=x_rcomp}
C {devices/res_np.sym} 330 340 0 0 {name=RT value=x_dut_rt_value}
C {devices/vsource_np.sym} -660 120 0 0 {name=VREF value="dc {x_vref_val}"}
C {devices/sg13_lv_pmos_np.sym} 0 -340 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -330 -20 -290 -20 {}
C {devices/lab_wire.sym} -290 -20 0 1 {name=l0 lab=egate}
N -330 20 -290 20 {}
C {devices/lab_wire.sym} -290 20 0 1 {name=l1 lab=ldiode}
N -440 -80 -440 -120 {}
C {devices/lab_wire.sym} -440 -120 0 1 {name=l2 lab=vdd}
N 110 -20 150 -20 {}
C {devices/lab_wire.sym} 150 -20 0 1 {name=l3 lab=nbias}
N 110 20 150 20 {}
C {devices/lab_wire.sym} 150 20 0 1 {name=l4 lab=tail}
N 0 80 0 120 {}
C {devices/lab_wire.sym} 0 120 2 0 {name=l5 lab=vss}
N 330 -20 290 -20 {}
C {devices/lab_wire.sym} 290 -20 0 0 {name=l6 lab=fb}
N 330 20 290 20 {}
C {devices/lab_wire.sym} 290 20 0 0 {name=l7 lab=vref}
N 550 -40 590 -40 {}
C {devices/lab_wire.sym} 590 -40 0 1 {name=l8 lab=egate}
N 550 0 590 0 {}
C {devices/lab_wire.sym} 590 0 0 1 {name=l9 lab=ldiode}
N 550 40 590 40 {}
C {devices/lab_wire.sym} 590 40 0 1 {name=l10 lab=tail}
N 440 100 440 140 {}
C {devices/lab_wire.sym} 440 140 2 0 {name=l11 lab=vss}
N -330 310 -330 270 {}
C {devices/lab_wire.sym} -330 270 0 1 {name=l12 lab=czero}
N -330 370 -330 410 {}
C {devices/lab_wire.sym} -330 410 2 0 {name=l13 lab=vout}
N -660 310 -660 270 {}
C {devices/lab_wire.sym} -660 270 0 1 {name=l14 lab=vdd}
N -660 370 -660 410 {}
C {devices/lab_wire.sym} -660 410 2 0 {name=l15 lab=nbias}
N -110 310 -110 270 {}
C {devices/lab_wire.sym} -110 270 0 1 {name=l16 lab=fb}
N -110 370 -110 410 {}
C {devices/lab_wire.sym} -110 410 2 0 {name=l17 lab=vss}
N 110 310 110 270 {}
C {devices/lab_wire.sym} 110 270 0 1 {name=l18 lab=egate}
N 110 370 110 410 {}
C {devices/lab_wire.sym} 110 410 2 0 {name=l19 lab=czero}
N 330 310 330 270 {}
C {devices/lab_wire.sym} 330 270 0 1 {name=l20 lab=vout}
N 330 370 330 410 {}
C {devices/lab_wire.sym} 330 410 2 0 {name=l21 lab=fb}
N -660 90 -660 50 {}
C {devices/lab_wire.sym} -660 50 0 1 {name=l22 lab=vref}
N -660 150 -660 190 {}
C {devices/lab_wire.sym} -660 190 2 0 {name=l23 lab=vss}
N 20 -310 20 -270 {}
C {devices/lab_wire.sym} 20 -270 2 0 {name=l24 lab=vout}
N -20 -340 -60 -340 {}
C {devices/lab_wire.sym} -60 -340 0 0 {name=l25 lab=egate}
N 20 -370 20 -410 {}
C {devices/lab_wire.sym} 20 -410 0 1 {name=l26 lab=vdd}
N 20 -340 60 -340 {}
C {devices/lab_wire.sym} 60 -340 0 1 {name=l27 lab=vdd}
