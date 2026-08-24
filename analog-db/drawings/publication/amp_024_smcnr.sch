v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_024_smcnr} 60 -1075 0 0 0.5 0.5 {}
N 60 -1000 200 -1000 {}
N 200 -1000 520 -1000 {}
N 520 -1000 1520 -1000 {}
N 200 -950 200 -1000 {}
N 520 -950 520 -1000 {}
N 1520 -950 1520 -1000 {}
N 200 -920 380 -920 {}
N 520 -920 700 -920 {}
N 1520 -920 1700 -920 {}
N 100 -840 100 -590 {}
N 100 -530 100 -160 {}
N 100 -840 160 -840 {}
N 160 -840 480 -840 {}
N 480 -840 520 -840 {}
N 520 -840 800 -840 {}
N 800 -840 1480 -840 {}
N 160 -920 160 -840 {}
N 480 -920 480 -840 {}
N 520 -890 520 -840 {}
N 1480 -920 1480 -840 {}
N 200 -890 200 -720 {}
N 200 -720 620 -720 {}
N 620 -720 720 -720 {}
N 720 -720 1160 -720 {}
N 720 -690 720 -720 {}
N 1160 -690 1160 -720 {}
N 300 -660 680 -660 {}
N 300 -780 1280 -780 {}
N 1280 -780 1280 -660 {}
N 1200 -660 1280 -660 {}
N 720 -660 860 -660 {}
N 1020 -660 1160 -660 {}
N 720 -630 720 -580 {}
N 680 -580 720 -580 {}
N 680 -580 680 -480 {}
N 680 -480 680 -400 {}
N 680 -400 680 -350 {}
N 680 -400 780 -400 {}
N 780 -400 1100 -400 {}
N 780 -400 780 -320 {}
N 720 -320 780 -320 {}
N 1100 -400 1100 -320 {}
N 1100 -320 1160 -320 {}
N 520 -320 680 -320 {}
N 1200 -320 1360 -320 {}
N 1520 -320 1700 -320 {}
N 680 -290 680 -160 {}
N 1200 -290 1200 -160 {}
N 1520 -290 1520 -160 {}
N 1160 -630 1160 -580 {}
N 1160 -580 1200 -580 {}
N 1200 -580 1200 -520 {}
N 1200 -520 1200 -480 {}
N 1200 -480 1200 -440 {}
N 1200 -440 1200 -350 {}
N 1200 -520 1250 -520 {}
N 1310 -520 1340 -520 {}
N 1340 -520 1410 -520 {}
N 1470 -520 1520 -520 {}
N 1200 -440 1480 -440 {}
N 1480 -440 1480 -320 {}
N 1520 -890 1520 -660 {}
N 1520 -660 1520 -520 {}
N 1520 -520 1520 -350 {}
N 1520 -660 1700 -660 {}
N 60 -160 100 -160 {}
N 100 -160 680 -160 {}
N 680 -160 1200 -160 {}
N 1200 -160 1520 -160 {}
C {sg13g2_pr/sg13_lv_pmos.sym} 180 -920 0 0 {name=M6
l=x_dut_xm6_l
w=x_dut_xm6_w
ng=1
m=x_dut_xm6_m
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 500 -920 0 0 {name=M7
l=x_dut_xm7_l
w=x_dut_xm7_w
ng=1
m=x_dut_xm7_m
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1500 -920 0 0 {name=M5
l=x_dut_xm5_l
w=x_dut_xm5_w
ng=1
m=x_dut_xm5_m
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 700 -660 0 0 {name=M0
l=x_dut_xm0_l
w=x_dut_xm0_w
ng=1
m=x_dut_xm0_m
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1180 -660 0 1 {name=M2
l=x_dut_xm2_l
w=x_dut_xm2_w
ng=1
m=x_dut_xm2_m
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 700 -320 0 1 {name=M1
l=x_dut_xm1_l
w=x_dut_xm1_w
ng=1
m=x_dut_xm1_m
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 1180 -320 0 0 {name=M3
l=x_dut_xm3_l
w=x_dut_xm3_w
ng=1
m=x_dut_xm3_m
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 1500 -320 0 0 {name=M4
l=x_dut_xm4_l
w=x_dut_xm4_w
ng=1
m=x_dut_xm4_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/isource.sym} 100 -560 0 0 {name=IBS
value="dc \{x_ibias_val\}"
}
C {devices/capa.sym} 1280 -520 3 0 {name=C0
m=1
value=x_c0
footprint=1206
device="ceramic capacitor"}
C {devices/res.sym} 1440 -520 3 0 {name=R0
value=x_rz
footprint=1206
device=resistor
m=1}
C {devices/iopin.sym} 60 -160 0 1 {name=p0 lab=vss}
C {devices/iopin.sym} 60 -1000 0 1 {name=p1 lab=vdd}
C {devices/ipin.sym} 300 -660 0 0 {name=p2 lab=vinn}
C {devices/ipin.sym} 300 -780 0 0 {name=p3 lab=vinp}
C {devices/opin.sym} 1700 -660 0 0 {name=p4 lab=vout}
C {devices/lab_pin.sym} 380 -920 0 1 {name=l0 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 700 -920 0 1 {name=l1 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 1700 -920 0 1 {name=l2 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 860 -660 0 1 {name=l3 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 1020 -660 0 0 {name=l4 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 520 -320 0 0 {name=l5 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 1360 -320 0 1 {name=l6 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 1700 -320 0 1 {name=l7 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 800 -840 0 1 {name=l8 sig_type=std_logic lab=ibias}
C {devices/lab_pin.sym} 620 -720 0 1 {name=l9 sig_type=std_logic lab=tailp}
C {devices/lab_pin.sym} 680 -480 0 0 {name=l10 sig_type=std_logic lab=outp}
C {devices/lab_pin.sym} 1200 -480 0 1 {name=l11 sig_type=std_logic lab=outn}
C {devices/lab_pin.sym} 1340 -520 0 1 {name=l12 sig_type=std_logic lab=nzo}
