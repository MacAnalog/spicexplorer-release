v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {buf_001_super_follower} -380 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -180 520 0 0 {name=CC value=x_cc}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} -340 520 0 1 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 0 260 0 0 {name=MNS model=sg13_lv_nmos spiceprefix=X w=x_dut_xmns_w l=x_dut_xmns_l m=x_dut_xmns_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 1 {name=MPB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpb_w l=x_dut_xmpb_l m=x_dut_xmpb_m}
C {devices/sg13_lv_pmos_np.sym} 0 0 0 0 {name=MPD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpd_w l=x_dut_xmpd_l m=x_dut_xmpd_m}
C {devices/sg13_lv_nmos_np.sym} 340 520 0 0 {name=MRN model=sg13_lv_nmos spiceprefix=X w=x_dut_xmrn_w l=x_dut_xmrn_l m=x_dut_xmrn_m}
N -420 0 -420 94 {}
N -420 260 -420 354 {}
N -420 520 -420 614 {}
N -360 -140 -360 -30 {}
N -360 30 -360 230 {}
N -360 290 -360 490 {}
N -360 550 -360 660 {}
N -230 200 -230 520 {}
N -180 460 -180 520 {}
N -180 550 -180 660 {}
N -110 260 -110 460 {}
N -20 0 -20 70 {}
N 20 -140 20 -30 {}
N 20 30 20 230 {}
N 20 290 20 660 {}
N 80 0 80 94 {}
N 80 260 80 354 {}
N 320 450 320 520 {}
N 360 450 360 490 {}
N 360 550 360 660 {}
N 420 520 420 614 {}
N -840 -140 840 -140 {}
N -420 0 -360 0 {}
N -350 0 -20 0 {}
N 20 0 80 0 {}
N -20 70 20 70 {}
N -360 200 -230 200 {}
N -420 260 -360 260 {}
N -320 260 -260 260 {}
N -110 260 -20 260 {}
N 20 260 80 260 {}
N 320 450 360 450 {}
N -110 460 360 460 {}
N -420 520 -360 520 {}
N -320 520 -180 520 {}
N 360 520 420 520 {}
N -840 660 840 660 {}
C {devices/lab_wire.sym} -360 90 2 0 {name=l0 lab=na}
C {devices/lab_wire.sym} -260 0 0 1 {name=l1 lab=pd}
C {devices/lab_wire.sym} -260 260 0 1 {name=l2 lab=vin}
C {devices/lab_wire.sym} -420 94 2 0 {name=l3 lab=vdd}
C {devices/lab_wire.sym} 80 94 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} -420 354 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} -420 614 2 0 {name=l6 lab=vss}
C {devices/lab_wire.sym} 80 354 2 0 {name=l7 lab=vss}
C {devices/lab_wire.sym} 420 614 2 0 {name=l8 lab=vss}
C {devices/iopin.sym} -840 -140 0 0 {name=p0 lab=vdd}
C {devices/iopin.sym} -840 660 0 0 {name=p1 lab=vss}
C {devices/opin.sym} 360 450 0 0 {name=p2 lab=ibias}
C {devices/opin.sym} -360 320 0 0 {name=p3 lab=vout}
C {devices/ipin.sym} -980 260 0 0 {name=p4 lab=vin}
B 8 -820 -78 480 78 {fill=0}
T {PMOS Simple Current Mirror} -820 -96 0 0 0.3 0.3 {layer=8}
B 10 -70 182 820 598 {fill=0}
T {NMOS Simple Current Mirror} -70 164 0 0 0.3 0.3 {layer=10}
