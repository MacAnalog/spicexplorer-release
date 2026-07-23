v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 510 -480 510 -380 {
lab=#net1}
N 760 -380 990 -380 {
lab=#net1}
N 990 -480 990 -380 {
lab=#net1}
N 510 -510 580 -510 {
lab=VSS}
N 900 -510 990 -510 {
lab=VSS}
N 550 -780 950 -780 {
lab=#net2}
N 990 -720 990 -540 {
lab=#net3}
N 990 -780 1070 -780 {
lab=VDD}
N 1280 -900 1550 -900 {
lab=xxx}
N 990 -900 990 -810 {
lab=xxx}
N 510 -900 990 -900 {
lab=xxx}
N 510 -900 510 -810 {
lab=xxx}
N 400 -510 470 -510 {
lab=vinp}
N 1030 -510 1100 -510 {
lab=vinn}
N 260 -720 510 -720 {
lab=#net4}
N 220 -900 220 -750 {
lab=xxx}
N 220 -900 510 -900 {
lab=xxx}
N 510 -720 510 -540 {
lab=#net4}
N 220 -590 220 -290 {
lab=#net5}
N 450 -780 510 -780 {
lab=VDD}
N 140 -720 220 -720 {
lab=VDD}
N 510 -750 510 -720 {
lab=#net4}
N 110 -590 220 -590 {
lab=#net5}
N 220 -690 220 -590 {
lab=#net5}
N 0 -260 70 -260 {
lab=VSS}
N 220 -260 290 -260 {
lab=VSS}
N 760 -250 830 -250 {
lab=VSS}
N 990 -720 1240 -720 {
lab=#net3}
N 1280 -900 1280 -750 {
lab=xxx}
N 1280 -590 1280 -290 {
lab=#net6}
N 1280 -720 1360 -720 {
lab=VDD}
N 1280 -590 1390 -590 {
lab=#net6}
N 1280 -690 1280 -590 {
lab=#net6}
N 1280 -260 1350 -260 {
lab=VSS}
N 990 -750 990 -720 {
lab=#net3}
N 990 -900 1280 -900 {
lab=xxx}
N 1280 -120 1500 -120 {
lab=#net7}
N 760 -380 760 -280 {
lab=#net1}
N 510 -380 760 -380 {
lab=#net1}
N 760 -220 760 -120 {
lab=#net7}
N 220 -120 760 -120 {
lab=#net7}
N 1280 -230 1280 -120 {
lab=#net7}
N 760 -120 1280 -120 {
lab=#net7}
N 220 -230 220 -120 {
lab=#net7}
N 0 -230 0 -120 {
lab=#net7}
N 0 -120 220 -120 {
lab=#net7}
N -100 -900 220 -900 {}
C {devices/title.sym} 170 -40 0 0 {name=l1 author="Copyright 2026 MacAnalog Research Group"}
C {sg13g2_pr/sg13_lv_nmos.sym} 490 -510 0 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 1010 -510 0 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 530 -780 0 1 {name=M3
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 970 -780 0 0 {name=M4
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 240 -720 0 1 {name=M5
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 900 -510 0 0 {name=p1 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 580 -510 0 1 {name=p2 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1070 -780 0 1 {name=p3 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 450 -780 0 0 {name=p4 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 140 -720 0 0 {name=p5 sig_type=std_logic lab=VDD}
C {ipin.sym} 400 -510 0 0 {name=p6 lab=vinp}
C {ipin.sym} 1100 -510 0 1 {name=p7 lab=vinn}
C {opin.sym} 640 -940 0 0 {name=p8 lab=xxx}
C {opin.sym} 500 -940 0 0 {name=p9 lab=xxx}
C {iopin.sym} -100 -900 0 1 {name=p10 lab=xxx}
C {sg13g2_pr/sg13_lv_nmos.sym} -20 -260 0 0 {name=M6
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 200 -260 0 0 {name=M7
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} 70 -260 0 1 {name=p11 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 290 -260 0 1 {name=p12 sig_type=std_logic lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 740 -250 0 0 {name=M8
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} 830 -250 0 1 {name=p13 sig_type=std_logic lab=VSS}
C {sg13g2_pr/sg13_lv_pmos.sym} 1260 -720 0 0 {name=M9
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 1360 -720 0 1 {name=p14 sig_type=std_logic lab=VDD}
C {sg13g2_pr/sg13_lv_nmos.sym} 1260 -260 0 0 {name=M10
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} 1350 -260 0 1 {name=p15 sig_type=std_logic lab=VSS}
