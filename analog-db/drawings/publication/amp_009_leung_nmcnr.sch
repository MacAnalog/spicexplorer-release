v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 130 120 130 0 {}
N 130 150 130 490 {}
N 90 120 70 120 {}
N 70 120 70 200 {}
N 70 200 130 200 {}
N 130 550 130 1190 {}
N 310 120 310 0 {}
N 310 150 310 990 {}
N 310 1020 310 1190 {}
N 270 1020 250 1020 {}
N 250 1020 250 950 {}
N 250 950 310 950 {}
N 490 120 490 0 {}
N 490 150 490 730 {}
N 490 760 530 760 {}
N 530 760 530 700 {}
N 490 790 490 990 {}
N 490 1020 490 1190 {}
N 670 120 670 0 {}
N 670 150 670 730 {}
N 670 760 710 760 {}
N 710 760 710 700 {}
N 670 790 670 990 {}
N 670 1020 670 1190 {}
N 900 120 900 0 {}
N 900 150 900 730 {}
N 860 120 840 120 {}
N 840 120 840 200 {}
N 840 200 900 200 {}
N 900 760 940 760 {}
N 940 760 940 700 {}
N 900 790 900 990 {}
N 900 1020 900 1190 {}
N 1040 340 1040 230 {}
N 1040 370 1040 890 {}
N 1040 890 900 890 {}
N 1220 340 1220 230 {}
N 1220 370 1220 890 {}
N 1220 890 1360 890 {}
N 1130 120 1130 0 {}
N 1130 150 1130 230 {}
N 1040 230 1220 230 {}
N 780 340 1000 340 {}
N 780 420 1300 420 {}
N 1300 420 1300 340 {}
N 1300 340 1260 340 {}
N 1360 120 1360 0 {}
N 1360 150 1360 730 {}
N 1360 760 1400 760 {}
N 1400 760 1400 700 {}
N 1360 790 1360 990 {}
N 1360 1020 1360 1190 {}
N 1540 120 1540 0 {}
N 1540 150 1540 990 {}
N 1500 120 1460 120 {}
N 1460 120 1460 190 {}
N 1460 190 1360 190 {}
N 1540 1020 1540 1190 {}
N 1500 1020 1480 1020 {}
N 1480 1020 1480 950 {}
N 1480 950 1540 950 {}
N 1720 120 1720 0 {}
N 1720 150 1720 990 {}
N 1720 1020 1720 1190 {}
N 1680 1020 1630 1020 {}
N 1630 1020 1630 950 {}
N 1630 950 1540 950 {}
N 2000 120 2000 0 {}
N 2000 150 2000 990 {}
N 2000 1020 2000 1190 {}
N 1960 1020 1810 1020 {}
N 1810 1020 1810 920 {}
N 1810 920 1720 920 {}
N 2000 340 2120 340 {}
N 1360 480 1580 480 {}
N 1640 480 1860 480 {}
N 1720 620 1760 620 {}
N 1820 620 1860 620 {}
N 1860 480 1860 620 {}
N 1860 550 1900 550 {}
N 1960 550 2000 550 {}
N 60 0 2000 0 {}
N 60 1190 2000 1190 {}
C {devices/sg13_lv_pmos_np.sym} 110 120 0 0 {name=M0
l=x_dut_xm0_l
w=x_dut_xm0_w
ng=1
m=x_dut_xm0_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/isource.sym} 130 520 0 0 {name=I0 value='CURRENT_0_BIAS'}
C {devices/lab_pin.sym} 130 300 0 1 {name=l2 sig_type=std_logic lab=net013}
C {devices/sg13_lv_pmos_np.sym} 290 120 0 0 {name=M3
l=x_dut_xm3_l
w=x_dut_xm3_w
ng=1
m=x_dut_xm3_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 270 120 0 0 {name=l4 sig_type=std_logic lab=net013}
C {devices/sg13_lv_nmos_np.sym} 290 1020 0 0 {name=M14
l=x_dut_xm14_l
w=x_dut_xm14_w
ng=1
m=x_dut_xm14_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 310 480 0 1 {name=l6 sig_type=std_logic lab=VB3}
C {devices/sg13_lv_pmos_np.sym} 470 120 0 0 {name=M1
l=x_dut_xm1_l
w=x_dut_xm1_w
ng=1
m=x_dut_xm1_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 450 120 0 0 {name=l8 sig_type=std_logic lab=net013}
C {devices/sg13_lv_nmos_np.sym} 470 760 0 0 {name=M12
l=x_dut_xm12_l
w=x_dut_xm12_w
ng=1
m=x_dut_xm12_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 450 760 0 0 {name=l10 sig_type=std_logic lab=VB3}
C {devices/lab_pin.sym} 530 700 0 1 {name=l11 sig_type=std_logic lab=vss}
C {devices/sg13_lv_nmos_np.sym} 470 1020 0 0 {name=M17
l=x_dut_xm17_l
w=x_dut_xm17_w
ng=1
m=x_dut_xm17_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 450 1020 0 0 {name=l13 sig_type=std_logic lab=VB4}
C {devices/lab_pin.sym} 490 480 0 1 {name=l14 sig_type=std_logic lab=VB4}
C {devices/sg13_lv_pmos_np.sym} 650 120 0 0 {name=M2
l=x_dut_xm2_l
w=x_dut_xm2_w
ng=1
m=x_dut_xm2_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 630 120 0 0 {name=l16 sig_type=std_logic lab=net013}
C {devices/sg13_lv_nmos_np.sym} 650 760 0 0 {name=M13
l=x_dut_xm13_l
w=x_dut_xm13_w
ng=1
m=x_dut_xm13_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 630 760 0 0 {name=l18 sig_type=std_logic lab=VB3}
C {devices/lab_pin.sym} 710 700 0 1 {name=l19 sig_type=std_logic lab=vss}
C {devices/sg13_lv_nmos_np.sym} 650 1020 0 0 {name=M18
l=x_dut_xm18_l
w=x_dut_xm18_w
ng=1
m=x_dut_xm18_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 630 1020 0 0 {name=l21 sig_type=std_logic lab=VB4}
C {devices/lab_pin.sym} 670 480 0 1 {name=l22 sig_type=std_logic lab=DM_1}
C {devices/sg13_lv_pmos_np.sym} 880 120 0 0 {name=M5
l=x_dut_xm5_l
w=x_dut_xm5_w
ng=1
m=x_dut_xm5_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 900 480 0 1 {name=l24 sig_type=std_logic lab=VOUTN}
C {devices/sg13_lv_nmos_np.sym} 880 760 0 0 {name=M15
l=x_dut_xm15_l
w=x_dut_xm15_w
ng=1
m=x_dut_xm15_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 860 760 0 0 {name=l26 sig_type=std_logic lab=VB3}
C {devices/lab_pin.sym} 940 700 0 1 {name=l27 sig_type=std_logic lab=vss}
C {devices/sg13_lv_nmos_np.sym} 880 1020 0 0 {name=M19
l=x_dut_xm19_l
w=x_dut_xm19_w
ng=1
m=x_dut_xm19_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 860 1020 0 0 {name=l29 sig_type=std_logic lab=VB4}
C {devices/lab_pin.sym} 900 830 0 1 {name=l30 sig_type=std_logic lab=DM_2}
C {devices/sg13_lv_pmos_np.sym} 1020 340 0 0 {name=M8
l=x_dut_xm8_l
w=x_dut_xm8_w
ng=1
m=x_dut_xm8_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/sg13_lv_pmos_np.sym} 1240 340 0 1 {name=M9
l=x_dut_xm9_l
w=x_dut_xm9_w
ng=1
m=x_dut_xm9_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/sg13_lv_pmos_np.sym} 1110 120 0 0 {name=M4
l=x_dut_xm4_l
w=x_dut_xm4_w
ng=1
m=x_dut_xm4_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 1090 120 0 0 {name=l34 sig_type=std_logic lab=net013}
C {devices/ipin.sym} 780 340 0 0 {name=p35 lab=VINN}
C {devices/ipin.sym} 780 420 0 0 {name=p36 lab=VINP}
C {devices/sg13_lv_pmos_np.sym} 1340 120 0 0 {name=M6
l=x_dut_xm6_l
w=x_dut_xm6_w
ng=1
m=x_dut_xm6_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 1320 120 0 0 {name=l38 sig_type=std_logic lab=VOUTN}
C {devices/sg13_lv_nmos_np.sym} 1340 760 0 0 {name=M16
l=x_dut_xm16_l
w=x_dut_xm16_w
ng=1
m=x_dut_xm16_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 1320 760 0 0 {name=l40 sig_type=std_logic lab=VB3}
C {devices/lab_pin.sym} 1400 700 0 1 {name=l41 sig_type=std_logic lab=vss}
C {devices/sg13_lv_nmos_np.sym} 1340 1020 0 0 {name=M20
l=x_dut_xm20_l
w=x_dut_xm20_w
ng=1
m=x_dut_xm20_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 1320 1020 0 0 {name=l43 sig_type=std_logic lab=VB4}
C {devices/sg13_lv_pmos_np.sym} 1520 120 0 0 {name=M10
l=x_dut_xm10_l
w=x_dut_xm10_w
ng=1
m=x_dut_xm10_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/sg13_lv_nmos_np.sym} 1520 1020 0 0 {name=M21
l=x_dut_xm21_l
w=x_dut_xm21_w
ng=1
m=x_dut_xm21_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/sg13_lv_pmos_np.sym} 1700 120 0 0 {name=M7
l=x_dut_xm7_l
w=x_dut_xm7_w
ng=1
m=x_dut_xm7_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 1680 120 0 0 {name=l47 sig_type=std_logic lab=net013}
C {devices/sg13_lv_nmos_np.sym} 1700 1020 0 0 {name=M22
l=x_dut_xm22_l
w=x_dut_xm22_w
ng=1
m=x_dut_xm22_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/sg13_lv_pmos_np.sym} 1980 120 0 0 {name=M11
l=x_dut_xm11_l
w=x_dut_xm11_w
ng=1
m=x_dut_xm11_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 1960 120 0 0 {name=l50 sig_type=std_logic lab=net013}
C {devices/sg13_lv_nmos_np.sym} 1980 1020 0 0 {name=M23
l=x_dut_xm23_l
w=x_dut_xm23_w
ng=1
m=x_dut_xm23_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/opin.sym} 2120 340 0 0 {name=p52 lab=VOUT}
C {devices/capa_np.sym} 1610 480 3 0 {name=C0
m=1
value='CAPACITOR_0'
footprint=1206
device="ceramic capacitor"}
C {devices/capa_np.sym} 1790 620 1 0 {name=C1
m=1
value='CAPACITOR_1'
footprint=1206
device="ceramic capacitor"}
C {devices/res_np.sym} 1930 550 3 0 {name=R0
value='RESISTOR_0'
footprint=1206
device=resistor
m=1}
C {devices/iopin.sym} 60 0 0 1 {name=p56 lab=vdd}
C {devices/iopin.sym} 60 1190 0 1 {name=p57 lab=vss}
