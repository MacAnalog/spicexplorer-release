v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 560 -290 560 -260 {
lab=CM_tail}
N 440 -260 560 -260 {
lab=CM_tail}
N 320 -290 320 -260 {
lab=CM_tail}
N 220 -320 280 -320 {
lab=vinp}
N 600 -320 650 -320 {
lab=vinn}
N 560 -430 560 -350 {
lab=net1}
N 440 -260 440 -220 {
lab=CM_tail}
N 320 -260 440 -260 {
lab=CM_tail}
N 440 -340 440 -320 {
lab=VSS}
N 440 -320 560 -320 {
lab=VSS}
N 320 -320 440 -320 {
lab=VSS}
N 360 -460 520 -460 {
lab=VBIAS}
N 320 -430 320 -350 {
lab=net2}
N 320 -610 320 -490 {
lab=drain_p}
N 560 -620 560 -490 {
lab=drain_n}
N 560 -460 640 -460 {
lab=VSS}
N 230 -460 320 -460 {
lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 300 -320 0 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 580 -320 0 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {ipin.sym} 220 -320 0 0 {name=p1 lab=vinp}
C {ipin.sym} 650 -320 0 1 {name=p2 lab=vinn}
C {ipin.sym} 440 -220 1 1 {name=p3 lab=CM_tail}
C {ipin.sym} 560 -620 1 0 {name=p4 lab=drain_n}
C {ipin.sym} 320 -610 1 0 {name=p5 lab=drain_p}
C {ipin.sym} 440 -340 3 1 {name=p6 lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 540 -460 0 0 {name=M3
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 340 -460 0 1 {name=M4
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} 230 -460 0 0 {name=p7 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 640 -460 0 1 {name=p8 sig_type=std_logic lab=VSS}
C {ipin.sym} 430 -460 3 1 {name=p9 lab=VBIAS}
C {devices/title.sym} 190 -60 0 0 {name=l2 author="Copyright 2026 MacAnalog Research Group"}
C {lab_pin.sym} 560 -400 0 0 {name=p10 sig_type=std_logic lab=net1
}
C {lab_pin.sym} 320 -390 0 0 {name=p11 sig_type=std_logic lab=net2
}
