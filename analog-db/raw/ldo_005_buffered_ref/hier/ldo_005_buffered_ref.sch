v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_005_buffered_ref} -1360 -540 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -1100 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_1.sym} -660 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_simple_2.sym} -220 0 0 0 {name=xcm_nmos_simple_2}
C {blocks/cm_pmos_simple_2.sym} 220 0 0 0 {name=xcm_pmos_simple_2}
C {blocks/dp_nmos_simple_1.sym} 660 0 0 0 {name=xdp_nmos_simple_1}
C {blocks/dp_nmos_simple_2.sym} 1100 0 0 0 {name=xdp_nmos_simple_2}
C {devices/capa_np.sym} -660 340 0 0 {name=CC value='c_comp'}
C {devices/capa_np.sym} -440 340 0 0 {name=C_LPF value='c_lpf'}
C {devices/isource_np.sym} -1320 340 0 0 {name=IBIAS_ERR value="dc {i_tail_err}"}
C {devices/isource_np.sym} -1320 120 0 0 {name=IBIAS_REF value="dc {i_tail_ref}"}
C {devices/res_np.sym} -220 340 0 0 {name=R1 value='r_ref_top'}
C {devices/res_np.sym} 0 340 0 0 {name=R2 value='r_ref_bot'}
C {devices/res_np.sym} 220 340 0 0 {name=R3 value='r_bleed'}
C {devices/res_np.sym} 440 340 0 0 {name=RZ value='r_z'}
C {devices/res_np.sym} 660 340 0 0 {name=R_LPF value='r_lpf'}
C {devices/vsource_np.sym} -1320 -100 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_pmos_np.sym} 0 -340 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -990 -20 -950 -20 {}
C {devices/lab_wire.sym} -950 -20 0 1 {name=l0 lab=ebias_err}
N -990 20 -950 20 {}
C {devices/lab_wire.sym} -950 20 0 1 {name=l1 lab=etail}
N -1100 80 -1100 120 {}
C {devices/lab_wire.sym} -1100 120 2 0 {name=l2 lab=vss}
N -550 -20 -510 -20 {}
C {devices/lab_wire.sym} -510 -20 0 1 {name=l3 lab=rd1}
N -550 20 -510 20 {}
C {devices/lab_wire.sym} -510 20 0 1 {name=l4 lab=v_ref_out}
N -660 -80 -660 -120 {}
C {devices/lab_wire.sym} -660 -120 0 1 {name=l5 lab=vdd}
N -110 -20 -70 -20 {}
C {devices/lab_wire.sym} -70 -20 0 1 {name=l6 lab=ebias_ref}
N -110 20 -70 20 {}
C {devices/lab_wire.sym} -70 20 0 1 {name=l7 lab=retail}
N -220 80 -220 120 {}
C {devices/lab_wire.sym} -220 120 2 0 {name=l8 lab=vss}
N 330 -20 370 -20 {}
C {devices/lab_wire.sym} 370 -20 0 1 {name=l9 lab=egate}
N 330 20 370 20 {}
C {devices/lab_wire.sym} 370 20 0 1 {name=l10 lab=noutm}
N 220 -80 220 -120 {}
C {devices/lab_wire.sym} 220 -120 0 1 {name=l11 lab=vdd}
N 550 -20 510 -20 {}
C {devices/lab_wire.sym} 510 -20 0 0 {name=l12 lab=v_ref_fb}
N 550 20 510 20 {}
C {devices/lab_wire.sym} 510 20 0 0 {name=l13 lab=vref}
N 770 -40 810 -40 {}
C {devices/lab_wire.sym} 810 -40 0 1 {name=l14 lab=rd1}
N 770 0 810 0 {}
C {devices/lab_wire.sym} 810 0 0 1 {name=l15 lab=retail}
N 770 40 810 40 {}
C {devices/lab_wire.sym} 810 40 0 1 {name=l16 lab=v_ref_out}
N 660 100 660 140 {}
C {devices/lab_wire.sym} 660 140 2 0 {name=l17 lab=vss}
N 990 -20 950 -20 {}
C {devices/lab_wire.sym} 950 -20 0 0 {name=l18 lab=v_lpf_out}
N 990 20 950 20 {}
C {devices/lab_wire.sym} 950 20 0 0 {name=l19 lab=vout}
N 1210 -40 1250 -40 {}
C {devices/lab_wire.sym} 1250 -40 0 1 {name=l20 lab=egate}
N 1210 0 1250 0 {}
C {devices/lab_wire.sym} 1250 0 0 1 {name=l21 lab=etail}
N 1210 40 1250 40 {}
C {devices/lab_wire.sym} 1250 40 0 1 {name=l22 lab=noutm}
N 1100 100 1100 140 {}
C {devices/lab_wire.sym} 1100 140 2 0 {name=l23 lab=vss}
N -660 310 -660 270 {}
C {devices/lab_wire.sym} -660 270 0 1 {name=l24 lab=ncz}
N -660 370 -660 410 {}
C {devices/lab_wire.sym} -660 410 2 0 {name=l25 lab=vout}
N -440 310 -440 270 {}
C {devices/lab_wire.sym} -440 270 0 1 {name=l26 lab=v_lpf_out}
N -440 370 -440 410 {}
C {devices/lab_wire.sym} -440 410 2 0 {name=l27 lab=vss}
N -1320 310 -1320 270 {}
C {devices/lab_wire.sym} -1320 270 0 1 {name=l28 lab=vdd}
N -1320 370 -1320 410 {}
C {devices/lab_wire.sym} -1320 410 2 0 {name=l29 lab=ebias_err}
N -1320 90 -1320 50 {}
C {devices/lab_wire.sym} -1320 50 0 1 {name=l30 lab=vdd}
N -1320 150 -1320 190 {}
C {devices/lab_wire.sym} -1320 190 2 0 {name=l31 lab=ebias_ref}
N -220 310 -220 270 {}
C {devices/lab_wire.sym} -220 270 0 1 {name=l32 lab=v_ref_out}
N -220 370 -220 410 {}
C {devices/lab_wire.sym} -220 410 2 0 {name=l33 lab=v_ref_fb}
N 0 310 0 270 {}
C {devices/lab_wire.sym} 0 270 0 1 {name=l34 lab=v_ref_fb}
N 0 370 0 410 {}
C {devices/lab_wire.sym} 0 410 2 0 {name=l35 lab=vss}
N 220 310 220 270 {}
C {devices/lab_wire.sym} 220 270 0 1 {name=l36 lab=vout}
N 220 370 220 410 {}
C {devices/lab_wire.sym} 220 410 2 0 {name=l37 lab=vss}
N 440 310 440 270 {}
C {devices/lab_wire.sym} 440 270 0 1 {name=l38 lab=egate}
N 440 370 440 410 {}
C {devices/lab_wire.sym} 440 410 2 0 {name=l39 lab=ncz}
N 660 310 660 270 {}
C {devices/lab_wire.sym} 660 270 0 1 {name=l40 lab=v_ref_out}
N 660 370 660 410 {}
C {devices/lab_wire.sym} 660 410 2 0 {name=l41 lab=v_lpf_out}
N -1320 -130 -1320 -170 {}
C {devices/lab_wire.sym} -1320 -170 0 1 {name=l42 lab=vref}
N -1320 -70 -1320 -30 {}
C {devices/lab_wire.sym} -1320 -30 2 0 {name=l43 lab=vss}
N 20 -310 20 -270 {}
C {devices/lab_wire.sym} 20 -270 2 0 {name=l44 lab=vout}
N -20 -340 -60 -340 {}
C {devices/lab_wire.sym} -60 -340 0 0 {name=l45 lab=egate}
N 20 -370 20 -410 {}
C {devices/lab_wire.sym} 20 -410 0 1 {name=l46 lab=vdd}
N 20 -340 60 -340 {}
C {devices/lab_wire.sym} 60 -340 0 1 {name=l47 lab=vdd}
