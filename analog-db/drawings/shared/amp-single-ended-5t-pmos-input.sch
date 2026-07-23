v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 540 -620 540 -520 {
lab=#net1}
N 790 -620 1020 -620 {
lab=#net1}
N 1020 -620 1020 -520 {
lab=#net1}
N 540 -490 610 -490 {
lab=VDD}
N 930 -490 1020 -490 {
lab=VDD}
N 750 -220 980 -220 {
lab=#net2}
N 1020 -220 1100 -220 {
lab=VSS}
N 1020 -190 1020 -100 {
lab=VSS}
N 540 -100 1020 -100 {
lab=VSS}
N 540 -190 540 -100 {
lab=VSS}
N 430 -490 500 -490 {
lab=vinp}
N 1060 -490 1130 -490 {
lab=vinn}
N 480 -220 540 -220 {
lab=VSS}
N 540 -460 540 -340 {
lab=#net2}
N 790 -750 860 -750 {
lab=VDD}
N 1020 -460 1020 -360 {
lab=vout}
N 790 -720 790 -620 {
lab=#net1}
N 540 -620 790 -620 {
lab=#net1}
N 790 -880 790 -780 {
lab=VDD}
N 750 -340 750 -220 {
lab=#net2}
N 580 -220 750 -220 {
lab=#net2}
N 540 -340 750 -340 {
lab=#net2}
N 540 -340 540 -250 {
lab=#net2}
N 190 -880 790 -880 {
lab=VDD}
N 120 -750 190 -750 {
lab=VDD}
N 300 -750 750 -750 {
lab=#net3}
N 190 -880 190 -780 {
lab=VDD}
N 130 -880 190 -880 {
lab=VDD}
N 190 -100 540 -100 {
lab=VSS}
N 190 -190 190 -100 {
lab=VSS}
N 130 -220 190 -220 {
lab=VSS}
N 190 -720 190 -660 {
lab=#net3}
N 70 -100 190 -100 {
lab=VSS}
N 230 -220 270 -220 {
lab=#net3}
N 270 -280 270 -220 {
lab=#net3}
N 190 -280 270 -280 {
lab=#net3}
N 190 -280 190 -250 {
lab=#net3}
N 190 -660 300 -660 {
lab=#net3}
N 190 -660 190 -280 {
lab=#net3}
N 300 -750 300 -660 {
lab=#net3}
N 230 -750 300 -750 {
lab=#net3}
N 1020 -360 1260 -360 {
lab=vout}
N 1020 -360 1020 -250 {
lab=vout}
N 790 -880 1300 -880 {
lab=VDD}
N 1020 -100 1320 -100 {
lab=VSS}
C {devices/title.sym} 170 -40 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {lab_pin.sym} 930 -490 2 1 {name=p1 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 610 -490 2 0 {name=p2 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1100 -220 2 0 {name=p3 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 480 -220 2 1 {name=p4 sig_type=std_logic lab=VSS}
C {ipin.sym} 430 -490 2 1 {name=p6 lab=vinp}
C {ipin.sym} 1130 -490 2 0 {name=p7 lab=vinn}
C {iopin.sym} 70 -100 2 0 {name=p10 lab=VSS}
C {lab_pin.sym} 860 -750 2 0 {name=p13 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 120 -750 2 1 {name=p5 sig_type=std_logic lab=VDD}
C {iopin.sym} 130 -880 2 0 {name=p8 lab=VDD}
C {lab_pin.sym} 130 -220 2 1 {name=p9 sig_type=std_logic lab=VSS}
C {opin.sym} 1260 -360 2 1 {name=p11 lab=vout}
C {sg13g2_pr/sg13_lv_pmos.sym} 770 -750 0 0 {name=M1
l=0.267u
w=0.329u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 1000 -220 0 0 {name=M2
l=1.31u
w=2.32u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 210 -750 0 1 {name=M3
l=0.259u
w=0.881u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 520 -490 0 0 {name=M4
l=0.27u
w=1.42u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1040 -490 0 1 {name=M5
l=0.27u
w=1.42u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 560 -220 0 1 {name=M6
l=1.31u
w=2.32u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 210 -220 0 1 {name=M7
l=0.22u
w=0.293u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
