v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 280 -120 320 -120 {
lab=VSS}
N 620 -450 620 -410 {
lab=#net1}
N 800 -410 960 -410 {
lab=#net1}
N 960 -450 960 -410 {
lab=#net1}
N 800 -410 800 -270 {
lab=#net1}
N 620 -410 800 -410 {
lab=#net1}
N 800 -210 800 -120 {
lab=VSS}
N 320 -210 320 -120 {
lab=VSS}
N 320 -120 800 -120 {
lab=VSS}
N 320 -480 320 -270 {
lab=vo2p}
N 540 -480 580 -480 {
lab=vinp}
N 540 -650 540 -480 {
lab=vinp}
N 540 -650 580 -650 {
lab=vinp}
N 620 -560 620 -510 {
lab=vo1n}
N 960 -560 960 -510 {
lab=vo1p}
N 940 -650 960 -650 {
lab=VDD}
N 620 -650 650 -650 {
lab=VDD}
N 620 -480 650 -480 {
lab=VSS}
N 920 -480 960 -480 {
lab=VSS}
N 260 -730 320 -730 {
lab=VDD}
N 280 -240 320 -240 {
lab=VSS}
N 800 -240 850 -240 {
lab=VSS}
N 520 -560 620 -560 {
lab=vo1n}
N 620 -580 620 -560 {
lab=vo1n}
N 410 -560 440 -560 {
lab=#net2}
N 320 -560 350 -560 {
lab=vo2p}
N 320 -700 320 -560 {
lab=vo2p}
N 520 -560 520 -240 {
lab=vo1n}
N 500 -560 520 -560 {
lab=vo1n}
N 360 -240 520 -240 {
lab=vo1n}
N 490 -650 540 -650 {
lab=vinp}
N 1000 -650 1060 -650 {
lab=vinn}
N 1060 -650 1060 -480 {
lab=vinn}
N 1000 -480 1060 -480 {
lab=vinn}
N 1060 -650 1110 -650 {
lab=vinn}
N 620 -740 620 -680 {
lab=#net3}
N 780 -740 960 -740 {
lab=#net3}
N 960 -740 960 -680 {
lab=#net3}
N 780 -810 840 -810 {
lab=VDD}
N 780 -940 780 -840 {
lab=VDD}
N 320 -940 780 -940 {
lab=VDD}
N 320 -940 320 -760 {
lab=VDD}
N 217.5 -940 320 -940 {
lab=VDD}
N 780 -780 780 -740 {
lab=#net3}
N 620 -740 780 -740 {
lab=#net3}
N 1280 -210 1280 -120 {
lab=VSS}
N 1280 -730 1340 -730 {
lab=VDD}
N 1280 -240 1320 -240 {
lab=VSS}
N 1160 -560 1190 -560 {
lab=#net4}
N 1250 -560 1280 -560 {
lab=vo2n}
N 1280 -700 1280 -560 {
lab=vo2n}
N 1080 -560 1080 -240 {
lab=vo1p}
N 1080 -560 1100 -560 {
lab=vo1p}
N 1080 -240 1240 -240 {
lab=vo1p}
N 1280 -940 1280 -760 {
lab=VDD}
N 800 -120 1280 -120 {
lab=VSS}
N 960 -560 1080 -560 {
lab=vo1p}
N 960 -580 960 -560 {
lab=vo1p}
N 780 -940 1280 -940 {
lab=VDD}
N 1190 -730 1240 -730 {
lab=vcmfb2}
N 690 -810 740 -810 {
lab=vcmfb1}
N 360 -730 410 -730 {
lab=vcmfb2}
N 1280 -480 1280 -270 {
lab=vo2n}
N 1280 -480 1342.5 -480 {
lab=vo2n}
N 1280 -560 1280 -480 {
lab=vo2n}
N 240 -480 320 -480 {
lab=vo2p}
N 320 -560 320 -480 {
lab=vo2p}
N 722.5 -240 760 -240 {
lab=vb2}
N 620 -580 682.5 -580 {
lab=vo1n}
N 620 -620 620 -580 {
lab=vo1n}
N 887.5 -580 960 -580 {
lab=vo1p}
N 960 -620 960 -580 {
lab=vo1p}
C {devices/title.sym} 172.5 -47.5 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {iopin.sym} 217.5 -940 0 1 {name=p4 lab=VDD}
C {iopin.sym} 280 -120 0 1 {name=p1 lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 340 -240 0 1 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 340 -730 0 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {capa.sym} 470 -560 1 0 {name=C1
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {res.sym} 380 -560 1 0 {name=R1
value=1k
footprint=1206
device=resistor
m=1}
C {sg13g2_pr/sg13_lv_nmos.sym} 600 -480 0 0 {name=M3
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 980 -480 0 1 {name=M4
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 780 -240 0 0 {name=M5
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 980 -650 0 1 {name=M6
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 600 -650 0 0 {name=M7
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 280 -240 0 0 {name=p2 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 850 -240 0 1 {name=p3 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 650 -480 0 1 {name=p5 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 920 -480 0 0 {name=p6 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 940 -650 0 0 {name=p7 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 650 -650 0 1 {name=p8 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 260 -730 0 0 {name=p9 sig_type=std_logic lab=VDD}
C {sg13g2_pr/sg13_lv_pmos.sym} 760 -810 0 0 {name=M8
l=0.13u
w=0.5u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 840 -810 0 1 {name=p10 sig_type=std_logic lab=VDD}
C {sg13g2_pr/sg13_lv_nmos.sym} 1260 -240 0 0 {name=M9
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1260 -730 0 0 {name=M10
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {capa.sym} 1130 -560 3 1 {name=C2
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {res.sym} 1220 -560 3 1 {name=R2
value=1k
footprint=1206
device=resistor
m=1}
C {lab_pin.sym} 1320 -240 0 1 {name=p12 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1340 -730 0 1 {name=p13 sig_type=std_logic lab=VDD}
C {ipin.sym} 1105 -650 0 1 {name=p29 lab=vinn}
C {ipin.sym} 492.5 -650 0 0 {name=p30 lab=vinp}
C {opin.sym} 240 -480 0 1 {name=p31 lab=vo2p}
C {opin.sym} 1342.5 -480 0 0 {name=p32 lab=vo2n}
C {ipin.sym} 407.5 -730 0 1 {name=p15 lab=vcmfb2}
C {ipin.sym} 692.5 -810 0 0 {name=p16 lab=vcmfb1}
C {lab_pin.sym} 1190 -730 0 0 {name=p17 sig_type=std_logic lab=vcmfb2}
C {ipin.sym} 722.5 -240 0 0 {name=p18 lab=vb2}
C {opin.sym} 682.5 -580 0 0 {name=p19 lab=vo1n}
C {opin.sym} 887.5 -580 0 1 {name=p20 lab=vo1p}
