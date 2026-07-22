v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 470 -320 470 -290 {
lab=CM_tail}
N 470 -320 590 -320 {
lab=CM_tail}
N 710 -320 710 -290 {
lab=CM_tail}
N 510 -260 560 -260 {
lab=vinp}
N 590 -360 590 -320 {
lab=CM_tail}
N 590 -320 710 -320 {
lab=CM_tail}
N 710 -180 710 -150 {
lab=vinp}
N 560 -260 710 -180 {
lab=vinp}
N 710 -230 710 -180 {
lab=vinp}
N 470 -180 470 -150 {
lab=vinn}
N 610 -260 670 -260 {
lab=vinn}
N 470 -180 610 -260 {
lab=vinn}
N 470 -230 470 -180 {
lab=vinn}
N 710 -260 820 -260 {
lab=VDD}
N 820 -260 820 -250 {
lab=VDD}
N 370 -260 470 -260 {
lab=VDD}
C {title.sym} 190 -40 0 0 {name=l1 author="Stefan Schippers"}
C {ipin.sym} 710 -150 2 0 {name=p1 lab=vinp}
C {ipin.sym} 470 -150 2 1 {name=p2 lab=vinn}
C {ipin.sym} 590 -360 3 1 {name=p3 lab=CM_tail}
C {sg13g2_pr/sg13_lv_pmos.sym} 490 -260 0 1 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 690 -260 0 0 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {ipin.sym} 820 -250 3 0 {name=p6 lab=VDD}
C {lab_pin.sym} 370 -260 2 1 {name=p4 sig_type=std_logic lab=VDD}
