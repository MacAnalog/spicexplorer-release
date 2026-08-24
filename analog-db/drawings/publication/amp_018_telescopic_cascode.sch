v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {amp_018_telescopic_cascode} 100 110 0 0 0.4 0.4 {}
N 60 60 600 60 {}
N 600 60 800 60 {}
N 800 60 1000 60 {}
N 600 60 600 150 {}
N 1000 60 1000 150 {}
N 800 60 800 100 {}
N 540 180 600 180 {}
N 540 310 600 310 {}
N 1000 180 1060 180 {}
N 1000 310 1060 310 {}
N 800 160 800 310 {}
N 640 310 800 310 {}
N 800 310 960 310 {}
N 600 210 600 280 {}
N 1000 210 1000 280 {}
N 640 180 720 180 {}
N 720 180 720 360 {}
N 600 360 720 360 {}
N 720 360 880 360 {}
N 880 180 880 360 {}
N 880 180 960 180 {}
N 600 340 600 360 {}
N 600 360 600 440 {}
N 1000 340 1000 420 {}
N 1000 420 1000 440 {}
N 1000 420 1180 420 {}
N 640 470 800 470 {}
N 800 470 960 470 {}
N 800 470 800 525 {}
N 540 470 600 470 {}
N 1000 470 1060 470 {}
N 600 610 660 610 {}
N 940 610 1000 610 {}
N 180 840 240 840 {}
N 460 840 520 840 {}
N 600 500 600 580 {}
N 1000 500 1000 580 {}
N 60 610 560 610 {}
N 60 700 1100 700 {}
N 1100 610 1100 700 {}
N 1040 610 1100 610 {}
N 460 640 600 640 {}
N 600 640 800 640 {}
N 800 640 1000 640 {}
N 460 640 460 810 {}
N 800 585 800 640 {}
N 60 780 240 780 {}
N 240 780 350 780 {}
N 240 780 240 810 {}
N 350 780 350 840 {}
N 280 840 350 840 {}
N 350 840 420 840 {}
N 60 940 240 940 {}
N 240 940 460 940 {}
N 460 940 1000 940 {}
N 240 870 240 940 {}
N 460 870 460 940 {}
C {devices/sg13_lv_pmos_np.sym} 620 180 0 1 {name=M3
model=sg13_lv_pmos
spiceprefix=X
w=x_dut_xm3_w
l=x_dut_xm3_l
ng=1
m=x_dut_xm3_m
}
C {devices/sg13_lv_pmos_np.sym} 620 310 0 1 {name=M3C
model=sg13_lv_pmos
spiceprefix=X
w=x_dut_xm3c_w
l=x_dut_xm3c_l
ng=1
m=x_dut_xm3c_m
}
C {devices/sg13_lv_nmos_np.sym} 620 470 0 1 {name=M1C
model=sg13_lv_nmos
spiceprefix=X
w=x_dut_xm1c_w
l=x_dut_xm1c_l
ng=1
m=x_dut_xm1c_m
}
C {devices/sg13_lv_nmos_np.sym} 580 610 0 0 {name=M1
model=sg13_lv_nmos
spiceprefix=X
w=x_dut_xm1_w
l=x_dut_xm1_l
ng=1
m=x_dut_xm1_m
}
C {devices/sg13_lv_pmos_np.sym} 980 180 0 0 {name=M4
model=sg13_lv_pmos
spiceprefix=X
w=x_dut_xm4_w
l=x_dut_xm4_l
ng=1
m=x_dut_xm4_m
}
C {devices/sg13_lv_pmos_np.sym} 980 310 0 0 {name=M4C
model=sg13_lv_pmos
spiceprefix=X
w=x_dut_xm4c_w
l=x_dut_xm4c_l
ng=1
m=x_dut_xm4c_m
}
C {devices/sg13_lv_nmos_np.sym} 980 470 0 0 {name=M2C
model=sg13_lv_nmos
spiceprefix=X
w=x_dut_xm2c_w
l=x_dut_xm2c_l
ng=1
m=x_dut_xm2c_m
}
C {devices/sg13_lv_nmos_np.sym} 1020 610 0 1 {name=M2
model=sg13_lv_nmos
spiceprefix=X
w=x_dut_xm2_w
l=x_dut_xm2_l
ng=1
m=x_dut_xm2_m
}
C {devices/sg13_lv_nmos_np.sym} 440 840 0 0 {name=M5
model=sg13_lv_nmos
spiceprefix=X
w=x_dut_xm5_w
l=x_dut_xm5_l
ng=x_dut_xm5_ng
m=x_dut_xm5_m
}
C {devices/sg13_lv_nmos_np.sym} 260 840 0 1 {name=M6
model=sg13_lv_nmos
spiceprefix=X
w=x_dut_xm6_w
l=x_dut_xm6_l
ng=1
m=x_dut_xm6_m
}
C {devices/vsource.sym} 800 130 0 0 {name=V1 value=x_dut_v_bias_2}
C {devices/vsource.sym} 800 555 0 0 {name=V2 value=x_dut_v_bias_1}
C {devices/iopin.sym} 60 60 0 1 {name=p1 lab=vdd}
C {devices/iopin.sym} 60 940 0 1 {name=p2 lab=vss}
C {devices/ipin.sym} 60 610 0 0 {name=p3 lab=vinp}
C {devices/ipin.sym} 60 700 0 0 {name=p4 lab=vinn}
C {devices/ipin.sym} 60 780 0 0 {name=p5 lab=ibias}
C {devices/opin.sym} 1180 420 0 0 {name=p6 lab=vout}
C {devices/lab_pin.sym} 540 180 0 0 {name=p7 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 540 310 0 0 {name=p8 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 1060 180 0 1 {name=p9 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 1060 310 0 1 {name=p10 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 540 470 0 0 {name=p11 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 1060 470 0 1 {name=p12 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 660 610 0 1 {name=p13 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 940 610 0 0 {name=p14 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 180 840 0 0 {name=p15 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 520 840 0 1 {name=p16 sig_type=std_logic lab=vss}
C {devices/lab_wire.sym} 600 245 0 0 {name=p17 lab=s3}
C {devices/lab_wire.sym} 1000 245 2 0 {name=p18 lab=s4}
C {devices/lab_wire.sym} 640 360 2 0 {name=p19 lab=gate_p}
C {devices/lab_wire.sym} 780 310 2 0 {name=p20 lab=gate_pc}
C {devices/lab_wire.sym} 680 470 2 0 {name=p21 lab=casc_n}
C {devices/lab_wire.sym} 600 540 0 0 {name=p22 lab=d1}
C {devices/lab_wire.sym} 1000 540 2 0 {name=p23 lab=d2}
C {devices/lab_wire.sym} 520 640 2 0 {name=p24 lab=tail}
