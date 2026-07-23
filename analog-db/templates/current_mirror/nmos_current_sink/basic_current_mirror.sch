v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 545 -340 670 -340 {
lab=iin}
N 480 -270 480 -240 {
lab=VSS}
N 480 -240 710 -240 {
lab=VSS}
N 710 -280 710 -240 {
lab=VSS}
N 480 -240 480 -180 {
lab=VSS}
N 400 -340 480 -340 {
lab=VSS}
N 400 -340 400 -270 {
lab=VSS}
N 400 -270 480 -270 {
lab=VSS}
N 480 -310 480 -270 {
lab=VSS}
N 710 -340 790 -340 {
lab=VSS}
N 790 -340 790 -280 {
lab=VSS}
N 710 -280 790 -280 {
lab=VSS}
N 710 -310 710 -280 {
lab=VSS}
N 480 -400 480 -370 {
lab=iin}
N 710 -440 710 -370 {
lab=iout}
N 480 -400 545 -400 {
lab=iin}
N 480 -440 480 -400 {
lab=iin}
N 545 -400 545 -340 {
lab=iin}
N 520 -340 545 -340 {
lab=iin}
C {devices/title.sym} 160 -40 0 0 {name=l1 author="Copyright 2026 MacAnalog Research Group"}
C {sg13g2_pr/sg13_lv_nmos.sym} 500 -340 0 1 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 690 -340 0 0 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {iopin.sym} 480 -180 0 0 {name=p1 lab=VSS}
C {iopin.sym} 480 -440 0 0 {name=p2 lab=iin}
C {iopin.sym} 710 -440 0 0 {name=p3 lab=iout}
