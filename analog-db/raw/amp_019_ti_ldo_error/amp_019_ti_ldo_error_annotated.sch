v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_019_ti_ldo_error} -720 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1115 260 1 0 {name=CC value='c_comp'}
C {devices/res_np.sym} -170 260 1 0 {name=RND value='r_nd'}
C {devices/res_np.sym} 905 260 1 0 {name=RZ value='r_z'}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=M1 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M2 model=sg13_hv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} 340 260 0 0 {name=M4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=M5 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 680 0 0 0 {name=M6 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
C {devices/sg13_lv_pmos_np.sym} 0 260 0 0 {name=M7 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 1 {name=MB0 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmb0_w l=x_dut_xmb0_l}
C {devices/sg13_lv_nmos_np.sym} -680 520 0 1 {name=MBC model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbc_w l=x_dut_xmbc_l m=x_dut_xmbc_m}
C {devices/sg13_lv_nmos_np.sym} 0 520 0 0 {name=MBE model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbe_w l=x_dut_xmbe_l}
C {devices/sg13_lv_nmos_np.sym} 340 520 0 0 {name=MBF model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbf_w l=x_dut_xmbf_l}
C {devices/sg13_lv_nmos_np.sym} 680 260 0 0 {name=MBO model=sg13_hv_nmos spiceprefix=X w=x_dut_xmbo_w l=x_dut_xmbo_l m=x_dut_xmbo_m}
N -760 0 -760 94 {}
N -760 260 -760 354 {}
N -760 520 -760 614 {}
N -700 -140 -700 -30 {}
N -700 30 -700 230 {}
N -700 290 -700 490 {}
N -700 550 -700 660 {}
N -630 460 -630 520 {}
N -420 260 -420 354 {}
N -420 520 -420 614 {}
N -360 140 -360 230 {}
N -360 290 -360 320 {}
N -360 450 -360 460 {}
N -360 460 -360 490 {}
N -360 550 -360 660 {}
N -320 450 -320 520 {}
N -230 0 -230 260 {}
N -50 200 -50 260 {}
N -50 460 -50 520 {}
N -40 320 -40 490 {}
N -20 260 -20 330 {}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 330 {}
N 20 550 20 660 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 80 520 80 614 {}
N 290 460 290 520 {}
N 360 170 360 230 {}
N 360 290 360 350 {}
N 360 550 360 660 {}
N 420 290 420 490 {}
N 420 520 420 614 {}
N 700 -140 700 -30 {}
N 700 30 700 90 {}
N 700 290 700 660 {}
N 760 60 760 230 {}
N 760 260 760 354 {}
N 935 260 935 320 {}
N 1145 260 1145 320 {}
N -1180 -140 1360 -140 {}
N -760 0 -700 0 {}
N -660 0 -20 0 {}
N 20 0 80 0 {}
N 600 0 660 0 {}
N 700 60 760 60 {}
N -360 140 20 140 {}
N -230 170 360 170 {}
N -700 200 -50 200 {}
N 700 230 760 230 {}
N -760 260 -700 260 {}
N -660 260 -630 260 {}
N -420 260 -360 260 {}
N -320 260 -290 260 {}
N -230 260 -200 260 {}
N -140 260 -50 260 {}
N 20 260 80 260 {}
N 260 260 320 260 {}
N 600 260 660 260 {}
N 700 260 760 260 {}
N 815 260 875 260 {}
N 935 260 965 260 {}
N 1055 260 1085 260 {}
N 1145 260 1175 260 {}
N 360 290 420 290 {}
N -700 320 -360 320 {}
N -40 320 20 320 {}
N -20 330 20 330 {}
N -360 450 -320 450 {}
N -630 460 -320 460 {}
N -50 460 290 460 {}
N -40 490 20 490 {}
N 360 490 420 490 {}
N -760 520 -700 520 {}
N -660 520 -630 520 {}
N -420 520 -360 520 {}
N -320 520 10 520 {}
N 20 520 80 520 {}
N 290 520 320 520 {}
N 360 520 420 520 {}
N -1180 660 1360 660 {}
C {devices/lab_wire.sym} 600 260 0 0 {name=l0 lab=ibias}
C {devices/lab_wire.sym} -700 90 2 0 {name=l1 lab=na}
C {devices/lab_wire.sym} 260 260 0 0 {name=l2 lab=na}
C {devices/lab_wire.sym} 20 90 2 0 {name=l3 lab=nb}
C {devices/lab_wire.sym} 935 320 2 0 {name=l4 lab=nb}
C {devices/lab_wire.sym} 815 260 0 0 {name=l5 lab=ncz}
C {devices/lab_wire.sym} 1145 320 2 0 {name=l6 lab=ncz}
C {devices/lab_wire.sym} -600 0 0 1 {name=l7 lab=nd}
C {devices/lab_wire.sym} -20 260 0 0 {name=l8 lab=ne}
C {devices/lab_wire.sym} 600 0 0 0 {name=l9 lab=ne}
C {devices/lab_wire.sym} 360 350 2 0 {name=l10 lab=nlev}
C {devices/lab_wire.sym} -700 350 2 0 {name=l11 lab=tail}
C {devices/lab_wire.sym} 700 90 2 0 {name=l12 lab=vout}
C {devices/lab_wire.sym} -760 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} 360 260 0 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} 700 0 0 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} 80 354 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} -760 354 2 0 {name=l18 lab=vss}
C {devices/lab_wire.sym} -420 354 2 0 {name=l19 lab=vss}
C {devices/lab_wire.sym} -420 614 2 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} -760 614 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} 80 614 2 0 {name=l22 lab=vss}
C {devices/lab_wire.sym} 420 614 2 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} 760 354 2 0 {name=l24 lab=vss}
C {devices/ipin.sym} -630 260 0 0 {name=p0 lab=vinn}
C {devices/ipin.sym} -290 260 0 0 {name=p1 lab=vinp}
C {devices/iopin.sym} -1180 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1180 660 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 1055 260 0 0 {name=p4 lab=vout}
C {devices/opin.sym} 290 460 0 0 {name=p5 lab=ibias}
B 8 -1160 182 1160 598 {fill=0}
T {NMOS Simple Current Mirror (4 outputs)} -1160 164 0 0 0.3 0.3 {layer=8}
B 10 -1056 182 -270 338 {fill=0}
T {NMOS Differential Pair} -1056 164 0 0 0.3 0.3 {layer=10}
