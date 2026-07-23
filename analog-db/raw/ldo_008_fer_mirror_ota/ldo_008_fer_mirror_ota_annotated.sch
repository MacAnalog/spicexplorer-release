v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_008_fer_mirror_ota} -890 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 620 260 1 0 {name=CC value=x_ccomp}
C {devices/isource_np.sym} -850 520 0 0 {name=IBI value="dc {x_ibias_val}"}
C {devices/res_np.sym} -510 520 0 0 {name=RB value=x_dut_rb_value}
C {devices/res_np.sym} 445 260 1 0 {name=RC value=x_rcomp}
C {devices/res_np.sym} 195 260 1 0 {name=RT value=x_dut_rt_value}
C {devices/vsource_np.sym} -850 260 0 0 {name=VREF value="dc {x_vref_val}"}
C {devices/sg13_lv_nmos_np.sym} -510 260 0 1 {name=MDF model=sg13_lv_nmos spiceprefix=X w=x_dut_xmdf_w l=x_dut_xmdf_l m=x_dut_xmdf_m}
C {devices/sg13_lv_nmos_np.sym} -50 260 0 0 {name=MDR model=sg13_lv_nmos spiceprefix=X w=x_dut_xmdr_w l=x_dut_xmdr_l m=x_dut_xmdr_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=MLD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmld_w l=x_dut_xmld_l m=x_dut_xmld_m}
C {devices/sg13_lv_pmos_np.sym} -50 0 0 0 {name=MLM model=sg13_lv_pmos spiceprefix=X w=x_dut_xmlm_w l=x_dut_xmlm_l m=x_dut_xmlm_m}
C {devices/sg13_lv_nmos_np.sym} 290 520 0 0 {name=MNB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb_w l=x_dut_xmnb_l m=x_dut_xmnb_m}
C {devices/sg13_lv_nmos_np.sym} -220 520 0 1 {name=MNT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnt_w l=x_dut_xmnt_l m=x_dut_xmnt_m}
C {devices/sg13_lv_pmos_np.sym} 630 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
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
N -100 0 -100 60 {}
N -30 -140 -30 -30 {}
N -30 30 -30 230 {}
N -30 290 -30 320 {}
N 30 0 30 94 {}
N 30 260 30 354 {}
N 225 260 225 320 {}
N 270 450 270 520 {}
N 310 430 310 490 {}
N 310 550 310 660 {}
N 370 520 370 614 {}
N 505 200 505 260 {}
N 590 200 590 260 {}
N 650 -140 650 -30 {}
N 650 30 650 90 {}
N 650 260 650 320 {}
N 710 0 710 94 {}
N -910 -140 840 -140 {}
N -590 0 -530 0 {}
N -490 0 -430 0 {}
N -100 0 -70 0 {}
N -30 0 30 0 {}
N 550 0 610 0 {}
N 650 0 710 0 {}
N -530 60 -100 60 {}
N -530 70 -490 70 {}
N -30 200 505 200 {}
N -590 260 -530 260 {}
N -490 260 -430 260 {}
N -130 260 -70 260 {}
N -30 260 30 260 {}
N 135 260 165 260 {}
N 225 260 255 260 {}
N 385 260 415 260 {}
N 475 260 505 260 {}
N 650 260 680 260 {}
N -530 320 -30 320 {}
N 270 450 310 450 {}
N -510 460 -460 460 {}
N -300 520 -240 520 {}
N -200 520 -140 520 {}
N 310 520 370 520 {}
N -910 660 840 660 {}
C {devices/lab_wire.sym} -910 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -910 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} 415 260 0 0 {name=l2 lab=czero}
C {devices/lab_wire.sym} 650 320 2 0 {name=l3 lab=czero}
C {devices/lab_wire.sym} -30 90 2 0 {name=l4 lab=egate}
C {devices/lab_wire.sym} 550 0 0 0 {name=l5 lab=egate}
C {devices/lab_wire.sym} -430 260 0 1 {name=l6 lab=fb}
C {devices/lab_wire.sym} 165 260 0 0 {name=l7 lab=fb}
C {devices/lab_wire.sym} -430 0 0 1 {name=l8 lab=ldiode}
C {devices/lab_wire.sym} -140 520 0 1 {name=l9 lab=nbias}
C {devices/lab_wire.sym} 310 430 0 1 {name=l10 lab=nbias}
C {devices/lab_wire.sym} -530 350 2 0 {name=l11 lab=tail}
C {devices/lab_wire.sym} 225 320 2 0 {name=l12 lab=vout}
C {devices/lab_wire.sym} 590 200 0 1 {name=l13 lab=vout}
C {devices/lab_wire.sym} 650 90 2 0 {name=l14 lab=vout}
C {devices/lab_wire.sym} -130 260 0 0 {name=l15 lab=vref}
C {devices/lab_wire.sym} -590 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 30 94 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} 710 94 2 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} -590 354 2 0 {name=l19 lab=vss}
C {devices/lab_wire.sym} 30 354 2 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} 370 614 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} -300 614 2 0 {name=l22 lab=vss}
C {devices/lab_wire.sym} -850 430 0 1 {name=l23 lab=vdd}
C {devices/lab_wire.sym} -850 610 2 0 {name=l24 lab=nbias}
C {devices/lab_wire.sym} -850 350 2 0 {name=l25 lab=vss}
C {devices/lab_wire.sym} -850 170 0 1 {name=l26 lab=vref}
C {devices/opin.sym} 980 30 0 0 {name=p0 lab=vout}
B 8 -706 -78 146 78 {fill=0}
T {PMOS Simple Current Mirror} -706 -96 0 0 0.3 0.3 {layer=8}
B 10 -416 442 486 598 {fill=0}
T {NMOS Simple Current Mirror} -416 424 0 0 0.3 0.3 {layer=10}
B 12 -706 182 146 338 {fill=0}
T {NMOS Differential Pair} -706 164 0 0 0.3 0.3 {layer=12}
