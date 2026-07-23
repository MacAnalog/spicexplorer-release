v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 670 -460 670 -360 {
lab=tail}
N 920 -360 1150 -360 {
lab=tail}
N 1150 -460 1150 -360 {
lab=tail}
N 670 -490 740 -490 {
lab=VSS}
N 1060 -490 1150 -490 {
lab=VSS}
N 710 -760 1110 -760 {
lab=X}
N 1150 -760 1230 -760 {
lab=VDD}
N 1150 -880 1150 -790 {
lab=VDD}
N 670 -880 1150 -880 {
lab=VDD}
N 670 -880 670 -790 {
lab=VDD}
N 560 -490 630 -490 {
lab=vinp}
N 1190 -490 1260 -490 {
lab=vinn}
N 420 -700 670 -700 {
lab=B}
N 380 -880 380 -730 {
lab=VDD}
N 380 -880 670 -880 {
lab=VDD}
N 670 -620 670 -520 {
lab=B}
N 380 -550 380 -270 {
lab=voutp}
N 610 -760 670 -760 {
lab=VDD}
N 300 -700 380 -700 {
lab=VDD}
N 670 -730 670 -700 {
lab=B}
N 270 -570 380 -570 {
lab=voutp}
N 380 -670 380 -570 {
lab=voutp}
N 160 -240 230 -240 {
lab=VSS}
N 380 -240 450 -240 {
lab=VSS}
N 920 -230 990 -230 {
lab=VSS}
N 1440 -880 1440 -730 {
lab=VDD}
N 1440 -550 1440 -270 {
lab=voutn}
N 1440 -700 1520 -700 {
lab=VDD}
N 1440 -600 1550 -600 {
lab=voutn}
N 1440 -600 1440 -550 {
lab=voutn}
N 1440 -240 1510 -240 {
lab=VSS}
N 1150 -620 1150 -520 {
lab=C}
N 1440 -880 1710 -880 {
lab=VDD}
N 920 -360 920 -260 {
lab=tail}
N 670 -360 920 -360 {
lab=tail}
N 920 -200 920 -100 {
lab=VSS}
N 380 -100 920 -100 {
lab=VSS}
N 1440 -210 1440 -100 {
lab=VSS}
N 1440 -100 1660 -100 {
lab=VSS}
N 380 -210 380 -100 {
lab=VSS}
N 160 -210 160 -100 {
lab=VSS}
N 160 -100 380 -100 {
lab=VSS}
N 160 -880 380 -880 {
lab=VDD}
N 160 -300 160 -270 {
lab=REF}
N 160 -880 160 -660 {
lab=VDD}
N 60 -880 160 -880 {
lab=VDD}
N 70 -240 120 -240 {
lab=REF}
N 70 -320 70 -240 {
lab=REF}
N 70 -320 160 -320 {
lab=REF}
N 160 -600 160 -320 {
lab=REF}
N 160 -300 300 -300 {
lab=REF}
N 160 -320 160 -300 {
lab=REF}
N 300 -300 300 -240 {
lab=REF}
N 300 -240 340 -240 {
lab=REF}
N 860 -300 860 -230 {
lab=REF}
N 860 -230 880 -230 {
lab=REF}
N 1360 -300 1360 -240 {
lab=REF}
N 1360 -240 1400 -240 {
lab=REF}
N 1150 -700 1400 -700 {
lab=C}
N 1150 -730 1150 -700 {
lab=C}
N 860 -300 1360 -300 {
lab=REF}
N 380 -550 440 -550 {
lab=voutp}
N 380 -570 380 -550 {
lab=voutp}
N 500 -550 550 -550 {
lab=#net1}
N 550 -620 550 -550 {
lab=#net1}
N 550 -620 580 -620 {
lab=#net1}
N 640 -620 670 -620 {
lab=B}
N 670 -700 670 -620 {
lab=B}
N 1380 -550 1440 -550 {
lab=voutn}
N 1270 -550 1320 -550 {
lab=#net2}
N 1270 -620 1270 -550 {
lab=#net2}
N 1240 -620 1270 -620 {
lab=#net2}
N 1150 -620 1180 -620 {
lab=C}
N 1150 -700 1150 -620 {
lab=C}
N 1150 -880 1440 -880 {
lab=VDD}
N 300 -300 860 -300 {
lab=REF}
N 920 -100 1440 -100 {
lab=VSS}
N 1440 -670 1440 -600 {
lab=voutn}
N 100 -100 160 -100 {
lab=VSS}
C {devices/title.sym} 170 -40 0 0 {name=l1 author="Copyright 2026 MacAnalog Research Group"}
C {sg13g2_pr/sg13_lv_nmos.sym} 650 -490 0 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 1170 -490 0 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 690 -760 0 1 {name=M3
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1130 -760 0 0 {name=M4
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 400 -700 0 1 {name=M5
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 1060 -490 0 0 {name=p1 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 740 -490 0 1 {name=p2 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1230 -760 0 1 {name=p3 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 610 -760 0 0 {name=p4 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 300 -700 0 0 {name=p5 sig_type=std_logic lab=VDD}
C {ipin.sym} 560 -490 0 0 {name=p6 lab=vinp}
C {ipin.sym} 1260 -490 0 1 {name=p7 lab=vinn}
C {opin.sym} 270 -570 0 1 {name=p8 lab=voutp}
C {opin.sym} 1550 -600 0 0 {name=p9 lab=voutn}
C {iopin.sym} 60 -880 0 1 {name=p10 lab=VDD}
C {sg13g2_pr/sg13_lv_nmos.sym} 140 -240 0 0 {name=M6
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 360 -240 0 0 {name=M7
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} 230 -240 0 1 {name=p11 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 450 -240 0 1 {name=p12 sig_type=std_logic lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 900 -230 0 0 {name=M8
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} 990 -230 0 1 {name=p13 sig_type=std_logic lab=VSS}
C {sg13g2_pr/sg13_lv_pmos.sym} 1420 -700 0 0 {name=M9
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 1520 -700 0 1 {name=p14 sig_type=std_logic lab=VDD}
C {sg13g2_pr/sg13_lv_nmos.sym} 1420 -240 0 0 {name=M10
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} 1510 -240 0 1 {name=p15 sig_type=std_logic lab=VSS}
C {isource.sym} 160 -630 0 0 {name=I0 value=1m}
C {res.sym} 610 -620 1 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1}
C {capa.sym} 470 -550 1 0 {name=C1
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {res.sym} 1210 -620 3 1 {name=R2
value=1k
footprint=1206
device=resistor
m=1}
C {capa.sym} 1350 -550 3 1 {name=C2
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {iopin.sym} 100 -100 0 1 {name=p16 lab=VSS}
C {lab_pin.sym} 990 -360 3 1 {name=p17 sig_type=std_logic lab=tail}
C {lab_pin.sym} 940 -760 3 1 {name=p18 sig_type=std_logic lab=X}
C {lab_pin.sym} 670 -650 0 1 {name=p19 sig_type=std_logic lab=B}
C {lab_pin.sym} 1150 -660 0 1 {name=p20 sig_type=std_logic lab=C}
C {lab_pin.sym} 160 -370 0 1 {name=p21 sig_type=std_logic lab=REF}
