v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_019_ti_ldo_error} -480 -580 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -220 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_nmos_simple_1.sym} 220 0 0 0 {name=xdp_nmos_simple_1}
C {devices/capa_np.sym} -220 380 0 0 {name=CC value='c_comp'}
C {devices/res_np.sym} 0 380 0 0 {name=RND value='r_nd'}
C {devices/res_np.sym} 220 380 0 0 {name=RZ value='r_z'}
C {devices/sg13_lv_pmos_np.sym} -440 -380 0 0 {name=M3 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} -220 -380 0 0 {name=M4 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_pmos_np.sym} 0 -380 0 0 {name=M5 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_pmos_np.sym} 220 -380 0 0 {name=M6 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
C {devices/sg13_lv_pmos_np.sym} 440 -380 0 0 {name=M7 model=sg13_hv_pmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l}
N -110 -80 -70 -80 {}
C {devices/lab_wire.sym} -70 -80 0 1 {name=l0 lab=ibias}
N -110 -40 -70 -40 {}
C {devices/lab_wire.sym} -70 -40 0 1 {name=l1 lab=ne}
N -110 0 -70 0 {}
C {devices/lab_wire.sym} -70 0 0 1 {name=l2 lab=nlev}
N -110 40 -70 40 {}
C {devices/lab_wire.sym} -70 40 0 1 {name=l3 lab=tail}
N -110 80 -70 80 {}
C {devices/lab_wire.sym} -70 80 0 1 {name=l4 lab=vout}
N -220 140 -220 180 {}
C {devices/lab_wire.sym} -220 180 2 0 {name=l5 lab=vss}
N 110 -20 70 -20 {}
C {devices/lab_wire.sym} 70 -20 0 0 {name=l6 lab=vinn}
N 110 20 70 20 {}
C {devices/lab_wire.sym} 70 20 0 0 {name=l7 lab=vinp}
N 330 -40 370 -40 {}
C {devices/lab_wire.sym} 370 -40 0 1 {name=l8 lab=na}
N 330 0 370 0 {}
C {devices/lab_wire.sym} 370 0 0 1 {name=l9 lab=nb}
N 330 40 370 40 {}
C {devices/lab_wire.sym} 370 40 0 1 {name=l10 lab=tail}
N 220 100 220 140 {}
C {devices/lab_wire.sym} 220 140 2 0 {name=l11 lab=vss}
N -220 350 -220 310 {}
C {devices/lab_wire.sym} -220 310 0 1 {name=l12 lab=ncz}
N -220 410 -220 450 {}
C {devices/lab_wire.sym} -220 450 2 0 {name=l13 lab=vout}
N 0 350 0 310 {}
C {devices/lab_wire.sym} 0 310 0 1 {name=l14 lab=na}
N 0 410 0 450 {}
C {devices/lab_wire.sym} 0 450 2 0 {name=l15 lab=nd}
N 220 350 220 310 {}
C {devices/lab_wire.sym} 220 310 0 1 {name=l16 lab=nb}
N 220 410 220 450 {}
C {devices/lab_wire.sym} 220 450 2 0 {name=l17 lab=ncz}
N -420 -350 -420 -310 {}
C {devices/lab_wire.sym} -420 -310 2 0 {name=l18 lab=na}
N -460 -380 -500 -380 {}
C {devices/lab_wire.sym} -500 -380 0 0 {name=l19 lab=nd}
N -420 -410 -420 -450 {}
C {devices/lab_wire.sym} -420 -450 0 1 {name=l20 lab=vdd}
N -420 -380 -380 -380 {}
C {devices/lab_wire.sym} -380 -380 0 1 {name=l21 lab=vdd}
N -200 -350 -200 -310 {}
C {devices/lab_wire.sym} -200 -310 2 0 {name=l22 lab=nlev}
N -240 -380 -280 -380 {}
C {devices/lab_wire.sym} -280 -380 0 0 {name=l23 lab=na}
N -200 -410 -200 -450 {}
C {devices/lab_wire.sym} -200 -450 0 1 {name=l24 lab=nd}
N -200 -380 -160 -380 {}
C {devices/lab_wire.sym} -160 -380 0 1 {name=l25 lab=vdd}
N 20 -350 20 -310 {}
C {devices/lab_wire.sym} 20 -310 2 0 {name=l26 lab=nb}
N -20 -380 -60 -380 {}
C {devices/lab_wire.sym} -60 -380 0 0 {name=l27 lab=nd}
N 20 -410 20 -450 {}
C {devices/lab_wire.sym} 20 -450 0 1 {name=l28 lab=vdd}
N 20 -380 60 -380 {}
C {devices/lab_wire.sym} 60 -380 0 1 {name=l29 lab=vdd}
N 240 -350 240 -310 {}
C {devices/lab_wire.sym} 240 -310 2 0 {name=l30 lab=vout}
N 200 -380 160 -380 {}
C {devices/lab_wire.sym} 160 -380 0 0 {name=l31 lab=ne}
N 240 -410 240 -450 {}
C {devices/lab_wire.sym} 240 -450 0 1 {name=l32 lab=vdd}
N 240 -380 280 -380 {}
C {devices/lab_wire.sym} 280 -380 0 1 {name=l33 lab=vdd}
N 460 -350 460 -310 {}
C {devices/lab_wire.sym} 460 -310 2 0 {name=l34 lab=ne}
N 420 -380 380 -380 {}
C {devices/lab_wire.sym} 380 -380 0 0 {name=l35 lab=ne}
N 460 -410 460 -450 {}
C {devices/lab_wire.sym} 460 -450 0 1 {name=l36 lab=nb}
N 460 -380 500 -380 {}
C {devices/lab_wire.sym} 500 -380 0 1 {name=l37 lab=vdd}
