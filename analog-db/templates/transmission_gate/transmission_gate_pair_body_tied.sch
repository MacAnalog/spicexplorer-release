v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 650 -370 650 -250 {
lab=port_B}
N 650 -370 710 -370 {
lab=port_B}
N 450 -250 530 -250 {
lab=port_A}
N 450 -370 450 -250 {
lab=port_A}
N 350 -370 450 -370 {
lab=port_A}
N 490 -150 560 -150 {
lab=vctl}
N 560 -210 560 -150 {
lab=vctl}
N 450 -510 560 -510 {
lab=port_A}
N 450 -510 450 -370 {
lab=port_A}
N 590 -510 650 -510 {
lab=port_B}
N 650 -510 650 -370 {
lab=port_B}
N 560 -590 560 -550 {
lab=vctl_not}
N 380 -590 560 -590 {
lab=vctl_not}
N 560 -250 650 -250 {
lab=port_B}
C {title.sym} 180 -40 0 0 {name=l1 author="Stefan Schippers"}
C {ipin.sym} 350 -370 0 0 {name=p1 lab=port_A}
C {ipin.sym} 710 -370 0 1 {name=p2 lab=port_B}
C {ipin.sym} 490 -150 2 1 {name=p6 lab=vctl}
C {sg13g2_pr/sg13_lv_nmos.sym} 560 -230 3 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 560 -530 3 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {ipin.sym} 380 -590 2 1 {name=p5 lab=vctl_not}
