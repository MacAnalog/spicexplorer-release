v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_pmos_simple_2} -890 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_pmos_np.sym} -850 0 0 1 {name=MLA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmla_w l=x_dut_xmla_l m=x_dut_xmla_m}
C {devices/sg13_lv_pmos_np.sym} -510 0 0 1 {name=MLB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmlb_w l=x_dut_xmlb_l m=x_dut_xmlb_m}
C {devices/sg13_lv_pmos_np.sym} -170 0 0 1 {name=MPD1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpd1_w l=x_dut_xmpd1_l m=x_dut_xmpd1_m}
C {devices/sg13_lv_pmos_np.sym} 170 0 0 0 {name=MPM1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpm1_w l=x_dut_xmpm1_l m=x_dut_xmpm1_m}
C {devices/sg13_lv_pmos_np.sym} 510 0 0 0 {name=MSA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmsa_w l=x_dut_xmsa_l m=x_dut_xmsa_m}
C {devices/sg13_lv_pmos_np.sym} 850 0 0 0 {name=MSB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmsb_w l=x_dut_xmsb_l m=x_dut_xmsb_m}
N -930 0 -930 94 {}
N -870 -140 -870 -30 {}
N -870 30 -870 60 {}
N -590 0 -590 94 {}
N -530 -140 -530 -30 {}
N -530 30 -530 60 {}
N -460 -60 -460 0 {}
N -250 0 -250 94 {}
N -190 -140 -190 -30 {}
N -190 30 -190 70 {}
N -150 -60 -150 70 {}
N 120 -60 120 0 {}
N 190 -140 190 -30 {}
N 190 30 190 60 {}
N 250 0 250 94 {}
N 460 -60 460 0 {}
N 530 -140 530 -30 {}
N 530 30 530 60 {}
N 590 0 590 94 {}
N 870 -140 870 -30 {}
N 870 30 870 60 {}
N 930 0 930 94 {}
N -1350 -140 1350 -140 {}
N -460 -60 -150 -60 {}
N 120 -60 460 -60 {}
N -930 0 -870 0 {}
N -830 0 -770 0 {}
N -590 0 -530 0 {}
N -490 0 -430 0 {}
N -250 0 -190 0 {}
N -150 0 180 0 {}
N 190 0 250 0 {}
N 460 0 490 0 {}
N 530 0 590 0 {}
N 800 0 830 0 {}
N 870 0 930 0 {}
N -190 70 -150 70 {}
C {devices/lab_wire.sym} -770 0 0 1 {name=l0 lab=vbp}
C {devices/lab_wire.sym} -430 0 0 1 {name=l1 lab=vbp}
C {devices/lab_wire.sym} -930 94 2 0 {name=l2 lab=vdd}
C {devices/lab_wire.sym} -590 94 2 0 {name=l3 lab=vdd}
C {devices/lab_wire.sym} -250 94 2 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} 250 94 2 0 {name=l5 lab=vdd}
C {devices/lab_wire.sym} 590 94 2 0 {name=l6 lab=vdd}
C {devices/lab_wire.sym} 930 94 2 0 {name=l7 lab=vdd}
C {devices/iopin.sym} -1350 -140 0 0 {name=p0 lab=vdd}
C {devices/opin.sym} 800 0 0 0 {name=p1 lab=vbp}
C {devices/opin.sym} -870 60 0 0 {name=p2 lab=voutp}
C {devices/opin.sym} -530 60 0 0 {name=p3 lab=voutn}
C {devices/opin.sym} 190 60 0 0 {name=p4 lab=vcn}
C {devices/opin.sym} 530 60 0 0 {name=p5 lab=fp}
C {devices/opin.sym} 870 60 0 0 {name=p6 lab=fn}
