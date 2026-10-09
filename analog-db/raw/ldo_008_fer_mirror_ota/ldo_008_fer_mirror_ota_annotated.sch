v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_008_fer_mirror_ota} -935 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 495 260 1 0 {name=CC value=x_ccomp}
C {devices/isource_np.sym} -895 520 0 0 {name=IBI value="dc \{x_ibias_val\}"}
C {devices/res_np.sym} -510 520 0 0 {name=RB value=x_dut_rb_value}
C {devices/res_np.sym} 320 260 1 0 {name=RC value=x_rcomp}
C {devices/res_np.sym} -130 260 1 0 {name=RT value=x_dut_rt_value}
C {devices/vsource_np.sym} -895 260 0 0 {name=VLP value="dc 0" savecurrent=false}
C {devices/vsource_np.sym} -895 0 0 0 {name=VREF value="dc \{x_vref_val\}" savecurrent=false}
C {devices/sg13_lv_nmos_np.sym} -510 260 0 1 {name=MDF model=sg13_lv_nmos spiceprefix=X w=x_dut_xmdf_w l=x_dut_xmdf_l m=x_dut_xmdf_m}
C {devices/sg13_lv_nmos_np.sym} 95 260 0 0 {name=MDR model=sg13_lv_nmos spiceprefix=X w=x_dut_xmdr_w l=x_dut_xmdr_l m=x_dut_xmdr_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=MLD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmld_w l=x_dut_xmld_l m=x_dut_xmld_m}
C {devices/sg13_lv_pmos_np.sym} 95 0 0 0 {name=MLM model=sg13_lv_pmos spiceprefix=X w=x_dut_xmlm_w l=x_dut_xmlm_l m=x_dut_xmlm_m}
C {devices/sg13_lv_nmos_np.sym} 485 520 0 0 {name=MNB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb_w l=x_dut_xmnb_l m=x_dut_xmnb_m}
C {devices/sg13_lv_nmos_np.sym} -140 520 0 1 {name=MNT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnt_w l=x_dut_xmnt_l m=x_dut_xmnt_m}
C {devices/sg13_lv_pmos_np.sym} 825 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
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
N -510 460 -510 490 {}
N -510 550 -510 660 {}
N -490 0 -490 70 {}
N -460 260 -460 460 {}
N -220 520 -220 614 {}
N -160 320 -160 490 {}
N -160 550 -160 660 {}
N 45 0 45 60 {}
N 115 -140 115 -30 {}
N 115 30 115 230 {}
N 115 290 115 320 {}
N 175 0 175 94 {}
N 175 260 175 354 {}
N 380 200 380 260 {}
N 465 450 465 520 {}
N 505 430 505 490 {}
N 505 550 505 660 {}
N 525 260 525 320 {}
N 565 520 565 614 {}
N 845 -140 845 -30 {}
N 845 30 845 60 {}
N 905 0 905 94 {}
N -1010 -140 1300 -140 {}
N -590 0 -530 0 {}
N -490 0 -430 0 {}
N 45 0 75 0 {}
N 115 0 175 0 {}
N 745 0 805 0 {}
N 845 0 905 0 {}
N -530 60 45 60 {}
N -530 70 -490 70 {}
N 115 200 380 200 {}
N -590 260 -530 260 {}
N -490 260 -160 260 {}
N -100 260 -70 260 {}
N 15 260 75 260 {}
N 115 260 175 260 {}
N 230 260 290 260 {}
N 350 260 380 260 {}
N 405 260 465 260 {}
N 525 260 555 260 {}
N -530 320 115 320 {}
N 465 450 505 450 {}
N -510 460 -460 460 {}
N -220 520 -160 520 {}
N -150 520 465 520 {}
N 505 520 565 520 {}
N -1010 660 1300 660 {}
C {devices/lab_wire.sym} 230 260 0 0 {name=l0 lab=czero}
C {devices/lab_wire.sym} 525 320 2 0 {name=l1 lab=czero}
C {devices/lab_wire.sym} 115 90 2 0 {name=l2 lab=egate}
C {devices/lab_wire.sym} 745 0 0 0 {name=l3 lab=egate}
C {devices/lab_wire.sym} -430 260 0 1 {name=l4 lab=fb}
C {devices/lab_wire.sym} -430 0 0 1 {name=l5 lab=ldiode}
C {devices/lab_wire.sym} -100 260 0 0 {name=l6 lab=lp_brk}
C {devices/lab_wire.sym} 505 430 0 1 {name=l7 lab=nbias}
C {devices/lab_wire.sym} -530 350 2 0 {name=l8 lab=tail}
C {devices/lab_wire.sym} 405 260 0 0 {name=l9 lab=vout}
C {devices/lab_wire.sym} 15 260 0 0 {name=l10 lab=vref}
C {devices/lab_wire.sym} -590 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} 175 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} 905 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} -590 354 2 0 {name=l14 lab=vss}
C {devices/lab_wire.sym} 175 354 2 0 {name=l15 lab=vss}
C {devices/lab_wire.sym} 565 614 2 0 {name=l16 lab=vss}
C {devices/lab_wire.sym} -220 614 2 0 {name=l17 lab=vss}
C {devices/lab_wire.sym} -895 350 2 0 {name=l18 lab=vout}
C {devices/lab_wire.sym} -895 430 0 1 {name=l19 lab=vdd}
C {devices/lab_wire.sym} -895 610 2 0 {name=l20 lab=nbias}
C {devices/lab_wire.sym} -895 90 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} -895 170 0 1 {name=l22 lab=lp_brk}
C {devices/lab_wire.sym} -895 -90 0 1 {name=l23 lab=vref}
C {devices/iopin.sym} -1010 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -1010 660 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 845 60 0 0 {name=p2 lab=vout}
B 8 -990 -78 575 78 {fill=0}
T {PMOS Simple Current Mirror} -990 -96 0 0 0.3 0.3 {layer=8}
B 10 -620 442 965 598 {fill=0}
T {NMOS Simple Current Mirror} -620 424 0 0 0.3 0.3 {layer=10}
B 12 -990 182 575 338 {fill=0}
T {NMOS Differential Pair} -990 164 0 0 0.3 0.3 {layer=12}
