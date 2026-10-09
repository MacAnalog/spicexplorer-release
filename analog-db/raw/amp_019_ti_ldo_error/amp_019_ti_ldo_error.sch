v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_019_ti_ldo_error} -720 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1010 260 1 0 {name=CC value='c_comp'}
C {devices/res_np.sym} -75 260 1 0 {name=RND value='r_nd'}
C {devices/res_np.sym} 195 260 1 0 {name=RZ value='r_z'}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=M1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} -460 260 0 1 {name=M2 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} 435 260 0 0 {name=M4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} -245 0 0 1 {name=M5 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 775 0 0 0 {name=M6 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
C {devices/sg13_lv_pmos_np.sym} -245 260 0 1 {name=M7 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l}
C {devices/sg13_lv_nmos_np.sym} 95 520 0 0 {name=MB0 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} -680 520 0 1 {name=MBC model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbc_w l=x_dut_xmbc_l m=x_dut_xmbc_m}
C {devices/sg13_lv_nmos_np.sym} -245 520 0 1 {name=MBE model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbe_w l=x_dut_xmbe_l}
C {devices/sg13_lv_nmos_np.sym} 435 520 0 0 {name=MBF model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbf_w l=x_dut_xmbf_l}
C {devices/sg13_lv_nmos_np.sym} 775 260 0 0 {name=MBO model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbo_w l=x_dut_xmbo_l m=x_dut_xmbo_m}
N -760 0 -760 94 {}
N -760 260 -760 354 {}
N -760 520 -760 614 {}
N -700 -140 -700 -30 {}
N -700 30 -700 230 {}
N -700 290 -700 490 {}
N -700 550 -700 660 {}
N -660 0 -660 60 {}
N -630 -60 -630 0 {}
N -630 520 -630 580 {}
N -540 260 -540 354 {}
N -480 170 -480 230 {}
N -480 290 -480 320 {}
N -325 60 -325 230 {}
N -325 260 -325 354 {}
N -325 520 -325 614 {}
N -265 -140 -265 -30 {}
N -265 30 -265 90 {}
N -265 170 -265 230 {}
N -265 290 -265 490 {}
N -265 550 -265 660 {}
N -225 260 -225 330 {}
N -195 -60 -195 0 {}
N -195 520 -195 580 {}
N -135 0 -135 260 {}
N -15 200 -15 260 {}
N 45 200 45 260 {}
N 75 450 75 520 {}
N 115 450 115 460 {}
N 115 460 115 490 {}
N 115 550 115 660 {}
N 175 520 175 614 {}
N 255 170 255 260 {}
N 385 200 385 260 {}
N 385 460 385 520 {}
N 455 140 455 230 {}
N 455 290 455 350 {}
N 455 550 455 660 {}
N 515 290 515 490 {}
N 515 520 515 614 {}
N 795 -140 795 -30 {}
N 795 30 795 230 {}
N 795 290 795 660 {}
N 855 0 855 94 {}
N 855 260 855 354 {}
N 950 200 950 260 {}
N 1040 260 1040 320 {}
N -1180 -140 1275 -140 {}
N -630 -60 -195 -60 {}
N -760 0 -700 0 {}
N -660 0 -630 0 {}
N -225 0 -135 0 {}
N 695 0 755 0 {}
N 795 0 855 0 {}
N -325 60 -265 60 {}
N -135 140 455 140 {}
N -265 170 255 170 {}
N -700 200 385 200 {}
N 795 200 950 200 {}
N -325 230 -265 230 {}
N -760 260 -700 260 {}
N -660 260 -630 260 {}
N -540 260 -480 260 {}
N -440 260 -410 260 {}
N -325 260 -265 260 {}
N -135 260 -105 260 {}
N -45 260 45 260 {}
N 135 260 165 260 {}
N 225 260 255 260 {}
N 385 260 415 260 {}
N 695 260 755 260 {}
N 795 260 855 260 {}
N 950 260 980 260 {}
N 1040 260 1070 260 {}
N 455 290 515 290 {}
N -700 320 -480 320 {}
N -265 330 -225 330 {}
N 75 450 115 450 {}
N 75 460 385 460 {}
N 455 490 515 490 {}
N -760 520 -700 520 {}
N -660 520 -630 520 {}
N -325 520 -265 520 {}
N -255 520 75 520 {}
N 115 520 175 520 {}
N 385 520 415 520 {}
N 455 520 515 520 {}
N -630 580 -195 580 {}
N -1180 660 1275 660 {}
C {devices/lab_wire.sym} 695 260 0 0 {name=l0 lab=ibias}
C {devices/lab_wire.sym} -700 90 2 0 {name=l1 lab=na}
C {devices/lab_wire.sym} -480 170 0 1 {name=l2 lab=nb}
C {devices/lab_wire.sym} -265 90 2 0 {name=l3 lab=nb}
C {devices/lab_wire.sym} 165 260 0 0 {name=l4 lab=ncz}
C {devices/lab_wire.sym} 1040 320 2 0 {name=l5 lab=ncz}
C {devices/lab_wire.sym} -660 60 2 0 {name=l6 lab=nd}
C {devices/lab_wire.sym} -225 320 2 0 {name=l7 lab=ne}
C {devices/lab_wire.sym} 695 0 0 0 {name=l8 lab=ne}
C {devices/lab_wire.sym} 455 350 2 0 {name=l9 lab=nlev}
C {devices/lab_wire.sym} -700 350 2 0 {name=l10 lab=tail}
C {devices/lab_wire.sym} -760 94 2 0 {name=l11 lab=vdd}
C {devices/lab_wire.sym} 455 260 0 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -265 0 0 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} 855 94 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} -325 354 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} -760 354 2 0 {name=l16 lab=vss}
C {devices/lab_wire.sym} -540 354 2 0 {name=l17 lab=vss}
C {devices/lab_wire.sym} 175 614 2 0 {name=l18 lab=vss}
C {devices/lab_wire.sym} -760 614 2 0 {name=l19 lab=vss}
C {devices/lab_wire.sym} -325 614 2 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} 515 614 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} 855 354 2 0 {name=l22 lab=vss}
C {devices/ipin.sym} -630 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -410 260 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -1180 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1180 660 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 950 200 0 0 {name=p4 lab=vout}
C {devices/opin.sym} 385 460 0 0 {name=p5 lab=ibias}
