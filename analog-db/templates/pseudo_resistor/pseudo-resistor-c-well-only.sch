v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 450 -320 450 -270 {
lab=port_A}
N 730 -320 730 -270 {
lab=port_B}
N 340 -360 420 -360 {
lab=port_A}
N 830 -360 880 -360 {
lab=port_B}
N 450 -360 730 -360 {
lab=#net1}
N 730 -270 830 -270 {
lab=port_B}
N 830 -360 830 -270 {
lab=port_B}
N 760 -360 830 -360 {
lab=port_B}
N 340 -270 450 -270 {
lab=port_A}
N 340 -360 340 -270 {
lab=port_A}
N 260 -360 340 -360 {
lab=port_A}
C {title.sym} 180 -40 0 0 {name=l1 author="Stefan Schippers"}
C {ipin.sym} 260 -360 0 0 {name=p1 lab=port_A}
C {ipin.sym} 880 -360 0 1 {name=p2 lab=port_B}
C {sg13g2_pr/sg13_lv_pmos.sym} 730 -340 3 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 450 -340 1 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
