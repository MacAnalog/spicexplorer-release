v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 770 -320 770 -290 {
lab=CM_tail}
N 650 -290 770 -290 {
lab=CM_tail}
N 530 -320 530 -290 {
lab=CM_tail}
N 680 -350 730 -350 {
lab=vinp}
N 650 -290 650 -250 {
lab=CM_tail}
N 530 -290 650 -290 {
lab=CM_tail}
N 530 -460 530 -430 {
lab=vinp}
N 530 -430 680 -350 {
lab=vinp}
N 530 -430 530 -380 {
lab=vinp}
N 770 -460 770 -430 {
lab=vinn}
N 570 -350 630 -350 {
lab=vinn}
N 630 -350 770 -430 {
lab=vinn}
N 770 -430 770 -380 {
lab=vinn}
N 420 -350 530 -350 {
lab=VSS}
N 420 -360 420 -350 {
lab=VSS}
N 770 -350 870 -350 {
lab=VSS}
C {title.sym} 210 -70 0 0 {name=l1 author="Stefan Schippers"}
C {ipin.sym} 530 -460 0 0 {name=p1 lab=vinp}
C {ipin.sym} 770 -460 0 1 {name=p2 lab=vinn}
C {ipin.sym} 650 -250 1 1 {name=p3 lab=CM_tail}
C {ipin.sym} 420 -360 1 0 {name=p6 lab=VSS}
C {lab_pin.sym} 870 -350 0 1 {name=p4 sig_type=std_logic lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 750 -350 0 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 550 -350 0 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
