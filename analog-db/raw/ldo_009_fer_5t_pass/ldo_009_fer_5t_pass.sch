v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_009_fer_5t_pass} -890 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 335 260 1 0 {name=CMIL value=x_cmil}
C {devices/capa_np.sym} 360 520 0 0 {name=COUT value=x_cout}
C {devices/isource_np.sym} -850 520 0 0 {name=IBI value="dc {x_ibias_val}"}
C {devices/res_np.sym} 520 520 0 0 {name=RBLD value=x_rbleed}
C {devices/res_np.sym} 20 260 0 0 {name=RREF value=x_rref}
C {devices/vsource_np.sym} -850 260 0 0 {name=VREF value="dc {x_vref_val}"}
C {devices/sg13_lv_nmos_np.sym} -170 260 0 0 {name=MIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmin_w l=x_dut_xmin_l m=x_dut_xmin_m}
C {devices/sg13_lv_nmos_np.sym} -510 260 0 1 {name=MIP model=sg13_lv_nmos spiceprefix=X w=x_dut_xmip_w l=x_dut_xmip_l m=x_dut_xmip_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=MLD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmld_w l=x_dut_xmld_l m=x_dut_xmld_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 0 {name=MLM model=sg13_lv_pmos spiceprefix=X w=x_dut_xmlm_w l=x_dut_xmlm_l m=x_dut_xmlm_m}
C {devices/sg13_lv_nmos_np.sym} 175 520 0 0 {name=MNB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb_w l=x_dut_xmnb_l m=x_dut_xmnb_m}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 1 {name=MNT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnt_w l=x_dut_xmnt_l m=x_dut_xmnt_m}
C {devices/sg13_lv_pmos_np.sym} 530 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -850 170 -850 230 {}
N -850 290 -850 350 {}
N -850 430 -850 490 {}
N -850 550 -850 610 {}
N -590 0 -590 94 {}
N -590 260 -590 354 {}
N -530 -140 -530 -30 {}
N -530 30 -530 230 {}
N -530 290 -530 350 {}
N -490 0 -490 70 {}
N -420 520 -420 614 {}
N -360 320 -360 490 {}
N -360 550 -360 660 {}
N -220 0 -220 60 {}
N -150 -140 -150 -30 {}
N -150 30 -150 230 {}
N -150 290 -150 320 {}
N -90 0 -90 94 {}
N -90 260 -90 354 {}
N 20 170 20 230 {}
N 20 260 20 350 {}
N 155 450 155 520 {}
N 195 430 195 490 {}
N 195 550 195 660 {}
N 255 520 255 614 {}
N 360 260 360 490 {}
N 360 550 360 660 {}
N 395 200 395 260 {}
N 480 0 480 260 {}
N 520 460 520 490 {}
N 520 550 520 660 {}
N 550 -140 550 -30 {}
N 550 30 550 460 {}
N 610 0 610 94 {}
N -910 -140 740 -140 {}
N -590 0 -530 0 {}
N -490 0 -430 0 {}
N -220 0 -190 0 {}
N -150 0 -90 0 {}
N 450 0 510 0 {}
N 550 0 610 0 {}
N -530 60 -220 60 {}
N -530 70 -490 70 {}
N -590 260 -530 260 {}
N -490 260 -430 260 {}
N -250 260 -190 260 {}
N -150 260 -90 260 {}
N 275 260 360 260 {}
N 365 260 480 260 {}
N -530 320 -150 320 {}
N 155 450 195 450 {}
N 360 460 550 460 {}
N -420 520 -360 520 {}
N -320 520 -260 520 {}
N 195 520 255 520 {}
N -910 660 740 660 {}
C {devices/lab_wire.sym} -910 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -910 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -260 520 0 1 {name=l2 lab=nbias}
C {devices/lab_wire.sym} 195 430 0 1 {name=l3 lab=nbias}
C {devices/lab_wire.sym} -150 90 2 0 {name=l4 lab=otao}
C {devices/lab_wire.sym} 450 0 0 0 {name=l5 lab=otao}
C {devices/lab_wire.sym} -430 0 0 1 {name=l6 lab=otax}
C {devices/lab_wire.sym} 20 170 0 1 {name=l7 lab=ref0}
C {devices/lab_wire.sym} -530 350 2 0 {name=l8 lab=tail}
C {devices/lab_wire.sym} -430 260 0 1 {name=l9 lab=vout}
C {devices/lab_wire.sym} 550 90 2 0 {name=l10 lab=vout}
C {devices/lab_wire.sym} -250 260 0 0 {name=l11 lab=vref}
C {devices/lab_wire.sym} 20 350 2 0 {name=l12 lab=vref}
C {devices/lab_wire.sym} -590 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} -90 94 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} 610 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} -90 354 2 0 {name=l16 lab=vss}
C {devices/lab_wire.sym} -590 354 2 0 {name=l17 lab=vss}
C {devices/lab_wire.sym} 255 614 2 0 {name=l18 lab=vss}
C {devices/lab_wire.sym} -420 614 2 0 {name=l19 lab=vss}
C {devices/lab_wire.sym} -850 350 2 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} -850 430 0 1 {name=l21 lab=vdd}
C {devices/lab_wire.sym} -850 610 2 0 {name=l22 lab=nbias}
C {devices/lab_wire.sym} -850 170 0 1 {name=l23 lab=ref0}
C {devices/opin.sym} 880 30 0 0 {name=p0 lab=vout}
