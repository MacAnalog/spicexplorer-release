v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 590 -500 590 -400 {
lab=#net1}
N 840 -400 1070 -400 {
lab=#net1}
N 1070 -500 1070 -400 {
lab=#net1}
N 590 -530 660 -530 {
lab=VSS}
N 980 -530 1070 -530 {
lab=VSS}
N 800 -800 1030 -800 {
lab=#net2}
N 1070 -800 1150 -800 {
lab=VDD}
N 1070 -920 1070 -830 {
lab=VDD}
N 590 -920 1070 -920 {
lab=VDD}
N 590 -920 590 -830 {
lab=VDD}
N 480 -530 550 -530 {
lab=vinp}
N 1110 -530 1180 -530 {
lab=vinn}
N 530 -800 590 -800 {
lab=VDD}
N 590 -680 590 -560 {
lab=#net2}
N 840 -270 910 -270 {
lab=VSS}
N 1070 -660 1070 -560 {
lab=#net3}
N 1070 -920 1630 -920 {
lab=VDD}
N 840 -400 840 -300 {
lab=#net1}
N 590 -400 840 -400 {
lab=#net1}
N 840 -240 840 -140 {
lab=VSS}
N 800 -800 800 -680 {
lab=#net2}
N 630 -800 800 -800 {
lab=#net2}
N 590 -680 800 -680 {
lab=#net2}
N 590 -770 590 -680 {
lab=#net2}
N 240 -140 840 -140 {
lab=VSS}
N 170 -270 240 -270 {
lab=VSS}
N 350 -270 800 -270 {
lab=#net4}
N 240 -240 240 -140 {
lab=VSS}
N 180 -140 240 -140 {
lab=VSS}
N 240 -920 590 -920 {
lab=VDD}
N 240 -920 240 -830 {
lab=VDD}
N 180 -800 240 -800 {
lab=VDD}
N 240 -360 240 -300 {
lab=#net4}
N 120 -920 240 -920 {
lab=VDD}
N 280 -800 320 -800 {
lab=#net4}
N 320 -800 320 -740 {
lab=#net4}
N 240 -740 320 -740 {
lab=#net4}
N 240 -770 240 -740 {
lab=#net4}
N 240 -360 350 -360 {
lab=#net4}
N 240 -740 240 -360 {
lab=#net4}
N 350 -360 350 -270 {
lab=#net4}
N 280 -270 350 -270 {
lab=#net4}
N 1070 -660 1310 -660 {
lab=#net3}
N 1070 -770 1070 -660 {
lab=#net3}
C {devices/title.sym} 170 -40 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {sg13g2_pr/sg13_lv_nmos.sym} 570 -530 0 0 {name=M1
l=0.834u
w=0.349u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 1090 -530 0 1 {name=M2
l=0.834u
w=0.349u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 610 -800 0 1 {name=M3
l=1.19u
w=0.218u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1050 -800 0 0 {name=M4
l=1.19u
w=0.218u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 980 -530 0 0 {name=p1 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 660 -530 0 1 {name=p2 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1150 -800 0 1 {name=p3 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 530 -800 0 0 {name=p4 sig_type=std_logic lab=VDD}
C {ipin.sym} 480 -530 0 0 {name=p6 lab=vinp}
C {ipin.sym} 1180 -530 0 1 {name=p7 lab=vinn}
C {iopin.sym} 120 -920 0 1 {name=p10 lab=VDD}
C {sg13g2_pr/sg13_lv_nmos.sym} 820 -270 0 0 {name=M8
l=0.484u
w=18u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} 910 -270 0 1 {name=p13 sig_type=std_logic lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 260 -270 0 1 {name=M5
l=0.276u
w=1.57u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} 170 -270 0 0 {name=p5 sig_type=std_logic lab=VSS}
C {iopin.sym} 180 -140 0 1 {name=p8 lab=VSS}
C {sg13g2_pr/sg13_lv_pmos.sym} 260 -800 0 1 {name=M6
l=1.07u
w=0.178u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 180 -800 0 0 {name=p9 sig_type=std_logic lab=VDD}
C {opin.sym} 1310 -660 0 0 {name=p11 lab=vout}
