v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 420 -440 420 -410 {
lab=CM_tail}
N 420 -440 540 -440 {
lab=CM_tail}
N 660 -440 660 -410 {
lab=CM_tail}
N 700 -380 760 -380 {
lab=vinp}
N 330 -380 380 -380 {
lab=vinn}
N 420 -350 420 -270 {
lab=drain_n}
N 660 -350 660 -260 {
lab=drain_p}
N 540 -480 540 -440 {
lab=CM_tail}
N 540 -440 660 -440 {
lab=CM_tail}
N 420 -380 540 -380 {
lab=#net1}
N 540 -380 540 -360 {}
N 540 -380 660 -380 {}
C {title.sym} 170 -30 0 0 {name=l1 author="Stefan Schippers"}
C {ipin.sym} 760 -380 2 0 {name=p1 lab=vinp}
C {ipin.sym} 330 -380 2 1 {name=p2 lab=vinn}
C {ipin.sym} 540 -480 3 1 {name=p3 lab=CM_tail}
C {ipin.sym} 420 -270 3 0 {name=p4 lab=drain_n}
C {ipin.sym} 660 -260 3 0 {name=p5 lab=drain_p}
C {sg13g2_pr/sg13_lv_pmos.sym} 400 -380 0 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 680 -380 0 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {ipin.sym} 540 -360 3 0 {name=p6 lab=VDD}
