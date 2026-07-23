v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_2} -420 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} 890 0 0 0 {name=MLA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmla_w l=x_dut_xmla_l m=x_dut_xmla_m}
C {devices/sg13_lv_pmos_np.sym} -380 0 0 0 {name=MLB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmlb_w l=x_dut_xmlb_l m=x_dut_xmlb_m}
C {devices/sg13_lv_pmos_np.sym} 595 0 0 0 {name=MPD1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpd1_w l=x_dut_xmpd1_l m=x_dut_xmpd1_m}
C {devices/sg13_lv_pmos_np.sym} 365 0 0 1 {name=MPM1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpm1_w l=x_dut_xmpm1_l m=x_dut_xmpm1_m}
C {devices/sg13_lv_pmos_np.sym} 140 0 0 1 {name=MSA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmsa_w l=x_dut_xmsa_l m=x_dut_xmsa_m}
C {devices/sg13_lv_pmos_np.sym} -90 0 0 1 {name=MSB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmsb_w l=x_dut_xmsb_l m=x_dut_xmsb_m}
N -360 -90 -360 -30 {}
N -360 30 -360 90 {}
N -300 0 -300 94 {}
N -170 0 -170 94 {}
N -110 -60 -110 -30 {}
N -110 30 -110 90 {}
N -70 0 -70 60 {}
N 60 0 60 94 {}
N 120 -60 120 -30 {}
N 120 30 120 90 {}
N 160 0 160 60 {}
N 285 0 285 94 {}
N 345 -60 345 -30 {}
N 345 30 345 90 {}
N 575 0 575 70 {}
N 615 -60 615 -30 {}
N 615 30 615 70 {}
N 675 0 675 94 {}
N 910 -60 910 -30 {}
N 910 30 910 90 {}
N 970 0 970 94 {}
N -360 -60 910 -60 {}
N -460 0 -400 0 {}
N -360 0 -300 0 {}
N -170 0 -110 0 {}
N -70 0 -40 0 {}
N 60 0 120 0 {}
N 160 0 190 0 {}
N 285 0 345 0 {}
N 385 0 445 0 {}
N 515 0 575 0 {}
N 615 0 675 0 {}
N 840 0 870 0 {}
N 910 0 970 0 {}
N 575 70 615 70 {}
C {devices/lab_wire.sym} -110 90 2 0 {name=l0 lab=fn}
C {devices/lab_wire.sym} 120 90 2 0 {name=l1 lab=fp}
C {devices/lab_wire.sym} -460 0 0 0 {name=l2 lab=vbp}
C {devices/lab_wire.sym} -70 60 2 0 {name=l3 lab=vbp}
C {devices/lab_wire.sym} 160 60 2 0 {name=l4 lab=vbp}
C {devices/lab_wire.sym} 445 0 0 1 {name=l5 lab=vbp}
C {devices/lab_wire.sym} 515 0 0 0 {name=l6 lab=vbp}
C {devices/lab_wire.sym} 870 0 0 0 {name=l7 lab=vbp}
C {devices/lab_wire.sym} 345 90 2 0 {name=l8 lab=vcn}
C {devices/lab_wire.sym} -360 -90 0 1 {name=l9 lab=vdd}
C {devices/lab_wire.sym} -360 90 2 0 {name=l10 lab=voutn}
C {devices/lab_wire.sym} 910 90 2 0 {name=l11 lab=voutp}
C {devices/lab_wire.sym} 970 94 2 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} -300 94 2 0 {name=l13 lab=vdd}
C {devices/lab_wire.sym} 675 94 2 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} 285 94 2 0 {name=l15 lab=vdd}
C {devices/lab_wire.sym} 60 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} -170 94 2 0 {name=l17 lab=vdd}
C {devices/iopin.sym} -360 280 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 1245 0 0 0 {name=p1 lab=vbp}
C {devices/opin.sym} 1245 120 0 0 {name=p2 lab=voutn}
C {devices/opin.sym} 1245 240 0 0 {name=p3 lab=fn}
C {devices/opin.sym} 1245 360 0 0 {name=p4 lab=fp}
C {devices/opin.sym} 1245 480 0 0 {name=p5 lab=vcn}
C {devices/opin.sym} 1245 600 0 0 {name=p6 lab=voutp}
