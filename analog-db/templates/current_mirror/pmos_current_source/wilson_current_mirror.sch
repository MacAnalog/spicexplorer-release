v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 500 -570 730 -570 {
lab=VDD}
N 420 -470 500 -470 {
lab=VDD}
N 500 -570 500 -500 {
lab=VDD}
N 730 -470 810 -470 {
lab=VDD}
N 730 -570 730 -500 {
lab=VDD}
N 730 -440 730 -410 {
lab=net1}
N 615 -470 690 -470 {
lab=net1}
N 730 -310 730 -190 {
lab=iout}
N 500 -440 500 -340 {
lab=iin}
N 500 -340 690 -340 {
lab=iin}
N 500 -340 500 -190 {
lab=iin}
N 730 -340 805 -340 {
lab=VDD}
N 615 -470 615 -410 {
lab=net1}
N 540 -470 615 -470 {
lab=net1}
N 615 -410 730 -410 {
lab=net1}
N 730 -410 730 -370 {
lab=net1}
N 430 -570 500 -570 {
lab=VDD}
N 730 -570 820 -570 {
lab=VDD}
C {devices/title.sym} 160 -40 0 0 {name=l1 author="Copyright 2026 MacAnalog Research Group"}
C {iopin.sym} 820 -570 2 1 {name=p1 lab=VDD}
C {iopin.sym} 500 -190 2 1 {name=p2 lab=iin}
C {iopin.sym} 730 -190 2 1 {name=p3 lab=iout}
C {lab_pin.sym} 420 -470 2 1 {name=p4 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 810 -470 0 1 {name=p5 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 805 -340 0 1 {name=p6 sig_type=std_logic lab=VDD}
C {sg13g2_pr/sg13_lv_pmos.sym} 710 -470 0 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 710 -340 0 0 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 520 -470 0 1 {name=M3
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 630 -470 1 0 {name=p7 sig_type=std_logic lab=net1}
