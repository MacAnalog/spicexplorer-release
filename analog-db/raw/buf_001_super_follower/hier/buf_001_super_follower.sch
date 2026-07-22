v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {buf_001_super_follower} -260 -200 0 0 0.4 0.4 {}
C {blocks/cm_pmos_simple_1.sym} -220 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_simple_1.sym} 220 0 0 0 {name=xcm_nmos_simple_1}
C {devices/capa_np.sym} -220 320 0 0 {name=CC value=x_cc}
C {devices/sg13_lv_nmos_np.sym} 0 320 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} 220 320 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
N -110 -20 -70 -20 {}
C {devices/lab_wire.sym} -70 -20 0 1 {name=l0 lab=na}
N -110 20 -70 20 {}
C {devices/lab_wire.sym} -70 20 0 1 {name=l1 lab=pd}
N -220 -80 -220 -120 {}
C {devices/lab_wire.sym} -220 -120 0 1 {name=l2 lab=vdd}
N 330 -20 370 -20 {}
C {devices/lab_wire.sym} 370 -20 0 1 {name=l3 lab=ibias}
N 330 20 370 20 {}
C {devices/lab_wire.sym} 370 20 0 1 {name=l4 lab=pd}
N 220 80 220 120 {}
C {devices/lab_wire.sym} 220 120 2 0 {name=l5 lab=vss}
N -220 290 -220 250 {}
C {devices/lab_wire.sym} -220 250 0 1 {name=l6 lab=na}
N -220 350 -220 390 {}
C {devices/lab_wire.sym} -220 390 2 0 {name=l7 lab=vss}
N 20 290 20 250 {}
C {devices/lab_wire.sym} 20 250 0 1 {name=l8 lab=na}
N -20 320 -60 320 {}
C {devices/lab_wire.sym} -60 320 0 0 {name=l9 lab=vin}
N 20 350 20 390 {}
C {devices/lab_wire.sym} 20 390 2 0 {name=l10 lab=vout}
N 20 320 60 320 {}
C {devices/lab_wire.sym} 60 320 0 1 {name=l11 lab=vss}
N 240 290 240 250 {}
C {devices/lab_wire.sym} 240 250 0 1 {name=l12 lab=vout}
N 200 320 160 320 {}
C {devices/lab_wire.sym} 160 320 0 0 {name=l13 lab=na}
N 240 350 240 390 {}
C {devices/lab_wire.sym} 240 390 2 0 {name=l14 lab=vss}
N 240 320 280 320 {}
C {devices/lab_wire.sym} 280 320 0 1 {name=l15 lab=vss}
