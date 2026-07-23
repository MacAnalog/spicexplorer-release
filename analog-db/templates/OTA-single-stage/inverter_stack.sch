v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 700 -390 700 -350 {
lab=vout}
N 600 -470 660 -470 {
lab=vinp}
N 600 -390 600 -320 {
lab=vinp}
N 600 -320 660 -320 {
lab=vinp}
N 700 -390 850 -390 {
lab=vout}
N 700 -440 700 -390 {
lab=vout}
N 700 -580 700 -500 {
lab=VDD}
N 700 -290 700 -200 {
lab=VSS}
N 520 -390 600 -390 {
lab=vinp}
N 600 -470 600 -390 {
lab=vinp}
N 700 -320 780 -320 {
lab=VSS}
N 700 -470 770 -470 {
lab=VDD}
C {devices/title.sym} 180 -40 0 0 {name=l1 author="Copyright 2026 MacAnalog Research Group"}
C {sg13g2_pr/sg13_lv_nmos.sym} 680 -320 0 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 680 -470 0 0 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {iopin.sym} 700 -580 0 0 {name=p1 lab=VDD}
C {iopin.sym} 700 -200 0 0 {name=p2 lab=VSS}
C {lab_pin.sym} 770 -470 0 1 {name=p3 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 780 -320 0 1 {name=p4 sig_type=std_logic lab=VSS}
C {iopin.sym} 850 -390 0 0 {name=p5 lab=vout}
C {iopin.sym} 520 -390 0 1 {name=p6 lab=vin}
