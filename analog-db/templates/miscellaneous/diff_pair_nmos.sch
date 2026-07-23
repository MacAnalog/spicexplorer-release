v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 700 -310 700 -280 {
lab=CM_tail}
N 580 -280 700 -280 {
lab=CM_tail}
N 460 -310 460 -280 {
lab=CM_tail}
N 360 -340 420 -340 {
lab=vinp}
N 740 -340 790 -340 {
lab=vinn}
N 700 -450 700 -370 {
lab=drain_n}
N 460 -460 460 -370 {
lab=drain_p}
N 580 -280 580 -240 {
lab=CM_tail}
N 460 -280 580 -280 {
lab=CM_tail}
N 580 -360 580 -340 {
lab=VSS}
N 580 -340 700 -340 {
lab=VSS}
N 460 -340 580 -340 {
lab=VSS}
C {devices/title.sym} 170 -30 0 0 {name=l1 author="Copyright 2026 MacAnalog Research Group"}
C {sg13g2_pr/sg13_lv_nmos.sym} 440 -340 0 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 720 -340 0 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {ipin.sym} 360 -340 0 0 {name=p1 lab=vinp}
C {ipin.sym} 790 -340 0 1 {name=p2 lab=vinn}
C {ipin.sym} 580 -240 1 1 {name=p3 lab=CM_tail}
C {ipin.sym} 700 -450 1 0 {name=p4 lab=drain_n}
C {ipin.sym} 460 -460 1 0 {name=p5 lab=drain_p}
C {ipin.sym} 580 -360 3 1 {name=p6 lab=VSS}
