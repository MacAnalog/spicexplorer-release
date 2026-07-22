v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 590 -340 590 -280 {
lab=VSS}
N 620 -280 680 -280 {
lab=port_B}
N 680 -400 680 -280 {
lab=port_B}
N 680 -400 740 -400 {
lab=port_B}
N 480 -280 560 -280 {
lab=port_A}
N 480 -400 480 -280 {
lab=port_A}
N 380 -400 480 -400 {
lab=port_A}
N 520 -180 590 -180 {
lab=vctl}
N 590 -240 590 -180 {
lab=vctl}
N 480 -540 560 -540 {
lab=port_A}
N 480 -540 480 -400 {
lab=port_A}
N 620 -540 680 -540 {
lab=port_B}
N 680 -540 680 -400 {
lab=port_B}
N 590 -540 590 -460 {
lab=VDD}
N 590 -620 590 -580 {
lab=vctl_not}
N 410 -620 590 -620 {
lab=vctl_not}
C {title.sym} 210 -70 0 0 {name=l1 author="Stefan Schippers"}
C {ipin.sym} 380 -400 0 0 {name=p1 lab=port_A}
C {ipin.sym} 740 -400 0 1 {name=p2 lab=port_B}
C {ipin.sym} 520 -180 2 1 {name=p6 lab=vctl}
C {ipin.sym} 590 -340 3 1 {name=p3 lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 590 -260 3 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 590 -560 3 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {ipin.sym} 590 -460 1 1 {name=p4 lab=VDD}
C {ipin.sym} 410 -620 2 1 {name=p5 lab=vctl_not}
