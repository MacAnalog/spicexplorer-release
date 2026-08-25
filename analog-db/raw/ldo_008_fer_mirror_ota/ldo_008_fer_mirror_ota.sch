v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_008_fer_mirror_ota} -890 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 345 260 1 0 {name=CC value=x_ccomp}
C {devices/isource_np.sym} -850 520 0 0 {name=IBI value="dc {x_ibias_val}"}
C {devices/res_np.sym} -510 520 0 0 {name=RB value=x_dut_rb_value}
C {devices/res_np.sym} 170 260 1 0 {name=RC value=x_rcomp}
C {devices/res_np.sym} -210 260 1 0 {name=RT value=x_dut_rt_value}
C {devices/vsource_np.sym} -850 260 0 0 {name=VLP value="dc 0"}
C {devices/vsource_np.sym} -850 0 0 0 {name=VREF value="dc {x_vref_val}"}
C {devices/sg13_lv_nmos_np.sym} -510 260 0 1 {name=MDF model=sg13_lv_nmos spiceprefix=X w=x_dut_xmdf_w l=x_dut_xmdf_l m=x_dut_xmdf_m}
C {devices/sg13_lv_nmos_np.sym} -20 260 0 0 {name=MDR model=sg13_lv_nmos spiceprefix=X w=x_dut_xmdr_w l=x_dut_xmdr_l m=x_dut_xmdr_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=MLD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmld_w l=x_dut_xmld_l m=x_dut_xmld_m}
C {devices/sg13_lv_pmos_np.sym} -20 0 0 0 {name=MLM model=sg13_lv_pmos spiceprefix=X w=x_dut_xmlm_w l=x_dut_xmlm_l m=x_dut_xmlm_m}
C {devices/sg13_lv_nmos_np.sym} 335 520 0 0 {name=MNB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb_w l=x_dut_xmnb_l m=x_dut_xmnb_m}
C {devices/sg13_lv_nmos_np.sym} -220 520 0 1 {name=MNT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnt_w l=x_dut_xmnt_l m=x_dut_xmnt_m}
C {devices/sg13_lv_pmos_np.sym} 675 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -850 -90 -850 -30 {}
N -850 30 -850 90 {}
N -850 170 -850 230 {}
N -850 290 -850 350 {}
N -850 430 -850 490 {}
N -850 550 -850 610 {}
N -590 0 -590 94 {}
N -590 260 -590 354 {}
N -530 -140 -530 -30 {}
N -530 30 -530 230 {}
N -530 290 -530 350 {}
N -510 460 -510 490 {}
N -510 550 -510 660 {}
N -490 0 -490 70 {}
N -460 260 -460 460 {}
N -300 520 -300 614 {}
N -240 320 -240 490 {}
N -240 550 -240 660 {}
N -70 0 -70 60 {}
N -40 200 -40 260 {}
N 0 -140 0 -30 {}
N 0 30 0 230 {}
N 0 290 0 320 {}
N 60 0 60 94 {}
N 60 260 60 354 {}
N 230 200 230 260 {}
N 315 200 315 260 {}
N 315 450 315 520 {}
N 355 430 355 490 {}
N 355 550 355 660 {}
N 375 260 375 320 {}
N 415 520 415 614 {}
N 625 0 625 260 {}
N 695 -140 695 -30 {}
N 695 30 695 260 {}
N 755 0 755 94 {}
N -910 -140 885 -140 {}
N -590 0 -530 0 {}
N -490 0 -430 0 {}
N -70 0 -40 0 {}
N 0 0 60 0 {}
N 595 0 655 0 {}
N 695 0 755 0 {}
N -530 60 -70 60 {}
N -530 70 -490 70 {}
N 0 200 230 200 {}
N -590 260 -530 260 {}
N -490 260 -240 260 {}
N -180 260 -150 260 {}
N -70 260 -40 260 {}
N 0 260 60 260 {}
N 80 260 140 260 {}
N 200 260 230 260 {}
N 285 260 315 260 {}
N 375 260 405 260 {}
N -530 320 0 320 {}
N 315 450 355 450 {}
N -510 460 -460 460 {}
N -300 520 -240 520 {}
N -200 520 -140 520 {}
N 355 520 415 520 {}
N -910 660 885 660 {}
C {devices/lab_wire.sym} -910 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -910 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 80 260 0 0 {name=l2 lab=czero}
C {devices/lab_wire.sym} 375 320 2 0 {name=l3 lab=czero}
C {devices/lab_wire.sym} 0 90 2 0 {name=l4 lab=egate}
C {devices/lab_wire.sym} 595 0 0 0 {name=l5 lab=egate}
C {devices/lab_wire.sym} -430 260 0 1 {name=l6 lab=fb}
C {devices/lab_wire.sym} -430 0 0 1 {name=l7 lab=ldiode}
C {devices/lab_wire.sym} -180 260 0 0 {name=l8 lab=lp_brk}
C {devices/lab_wire.sym} -140 520 0 1 {name=l9 lab=nbias}
C {devices/lab_wire.sym} 355 430 0 1 {name=l10 lab=nbias}
C {devices/lab_wire.sym} -530 350 2 0 {name=l11 lab=tail}
C {devices/lab_wire.sym} 315 200 0 1 {name=l12 lab=vout}
C {devices/lab_wire.sym} 695 90 2 0 {name=l13 lab=vout}
C {devices/lab_wire.sym} -40 200 0 1 {name=l14 lab=vref}
C {devices/lab_wire.sym} -590 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} 60 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 755 94 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} -590 354 2 0 {name=l18 lab=vss}
C {devices/lab_wire.sym} 60 354 2 0 {name=l19 lab=vss}
C {devices/lab_wire.sym} 415 614 2 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} -300 614 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} -850 350 2 0 {name=l22 lab=vout}
C {devices/lab_wire.sym} -850 430 0 1 {name=l23 lab=vdd}
C {devices/lab_wire.sym} -850 610 2 0 {name=l24 lab=nbias}
C {devices/lab_wire.sym} -850 90 2 0 {name=l25 lab=vss}
C {devices/lab_wire.sym} -850 170 0 1 {name=l26 lab=lp_brk}
C {devices/lab_wire.sym} -850 -90 0 1 {name=l27 lab=vref}
C {devices/opin.sym} 1025 30 0 0 {name=p0 lab=vout}
