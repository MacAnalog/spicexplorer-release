v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_009_fer_5t_pass} -935 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 370 260 1 0 {name=CMIL value=x_cmil}
C {devices/capa_np.sym} 435 520 0 0 {name=COUT value=x_cout}
C {devices/isource_np.sym} -895 520 0 0 {name=IBI value="dc \{x_ibias_val\}"}
C {devices/res_np.sym} 600 520 0 0 {name=RBLD value=x_rbleed}
C {devices/res_np.sym} 55 260 0 0 {name=RREF value=x_rref}
C {devices/vsource_np.sym} -895 260 0 0 {name=VLP value="dc 0" savecurrent=false}
C {devices/vsource_np.sym} -895 0 0 0 {name=VREF value="dc \{x_vref_val\}" savecurrent=false}
C {devices/sg13_lv_nmos_np.sym} -170 260 0 0 {name=MIN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmin_w l=x_dut_xmin_l m=x_dut_xmin_m}
C {devices/sg13_lv_nmos_np.sym} -510 260 0 1 {name=MIP model=sg13_lv_nmos spiceprefix=X w=x_dut_xmip_w l=x_dut_xmip_l m=x_dut_xmip_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=MLD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmld_w l=x_dut_xmld_l m=x_dut_xmld_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 0 {name=MLM model=sg13_lv_pmos spiceprefix=X w=x_dut_xmlm_w l=x_dut_xmlm_l m=x_dut_xmlm_m}
C {devices/sg13_lv_nmos_np.sym} 210 520 0 0 {name=MNB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb_w l=x_dut_xmnb_l m=x_dut_xmnb_m}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 1 {name=MNT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnt_w l=x_dut_xmnt_l m=x_dut_xmnt_m}
C {devices/sg13_lv_pmos_np.sym} 610 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -895 -90 -895 -30 {}
N -895 30 -895 90 {}
N -895 170 -895 230 {}
N -895 290 -895 350 {}
N -895 430 -895 490 {}
N -895 550 -895 610 {}
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
N -220 260 -220 380 {}
N -150 -140 -150 -30 {}
N -150 30 -150 230 {}
N -150 290 -150 320 {}
N -90 0 -90 94 {}
N -90 260 -90 354 {}
N 55 170 55 230 {}
N 55 290 55 380 {}
N 190 450 190 520 {}
N 230 430 230 490 {}
N 230 550 230 660 {}
N 290 520 290 614 {}
N 310 -60 310 260 {}
N 370 200 370 260 {}
N 435 260 435 490 {}
N 435 550 435 660 {}
N 560 -60 560 0 {}
N 600 460 600 490 {}
N 600 550 600 660 {}
N 630 -140 630 -30 {}
N 630 30 630 460 {}
N 690 0 690 94 {}
N -1010 -140 1085 -140 {}
N 310 -60 560 -60 {}
N -590 0 -530 0 {}
N -490 0 -430 0 {}
N -220 0 -190 0 {}
N -150 0 -90 0 {}
N 530 0 590 0 {}
N 630 0 690 0 {}
N -530 60 -220 60 {}
N -530 70 -490 70 {}
N -150 200 370 200 {}
N -590 260 -530 260 {}
N -490 260 -430 260 {}
N -250 260 -190 260 {}
N -150 260 -90 260 {}
N 310 260 370 260 {}
N 400 260 435 260 {}
N -530 320 -150 320 {}
N -220 380 55 380 {}
N 190 450 230 450 {}
N 435 460 630 460 {}
N -420 520 -360 520 {}
N -350 520 190 520 {}
N 230 520 290 520 {}
N -1010 660 1085 660 {}
C {devices/lab_wire.sym} -430 260 0 1 {name=l0 lab=lp_brk}
C {devices/lab_wire.sym} 230 430 0 1 {name=l1 lab=nbias}
C {devices/lab_wire.sym} 530 0 0 0 {name=l2 lab=otao}
C {devices/lab_wire.sym} -430 0 0 1 {name=l3 lab=otax}
C {devices/lab_wire.sym} 55 170 0 1 {name=l4 lab=ref0}
C {devices/lab_wire.sym} -530 350 2 0 {name=l5 lab=tail}
C {devices/lab_wire.sym} -250 260 0 0 {name=l6 lab=vref}
C {devices/lab_wire.sym} -590 94 2 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} -90 94 2 0 {name=l8 lab=vdd}
C {devices/lab_wire.sym} 690 94 2 0 {name=l9 lab=vdd}
C {devices/lab_wire.sym} -90 354 2 0 {name=l10 lab=vss}
C {devices/lab_wire.sym} -590 354 2 0 {name=l11 lab=vss}
C {devices/lab_wire.sym} 290 614 2 0 {name=l12 lab=vss}
C {devices/lab_wire.sym} -420 614 2 0 {name=l13 lab=vss}
C {devices/lab_wire.sym} -895 350 2 0 {name=l14 lab=vout}
C {devices/lab_wire.sym} -895 90 2 0 {name=l15 lab=vss}
C {devices/lab_wire.sym} -895 430 0 1 {name=l16 lab=vdd}
C {devices/lab_wire.sym} -895 610 2 0 {name=l17 lab=nbias}
C {devices/lab_wire.sym} -895 -90 0 1 {name=l18 lab=ref0}
C {devices/lab_wire.sym} -895 170 0 1 {name=l19 lab=lp_brk}
C {devices/iopin.sym} -1010 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -1010 660 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 630 60 0 0 {name=p2 lab=vout}
