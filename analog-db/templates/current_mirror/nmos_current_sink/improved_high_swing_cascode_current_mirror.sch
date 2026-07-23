v {xschem version=3.4.8RC file_version=1.3}
G {}
K {}
V {}
S {}
F {}
E {}
N 480 -240 710 -240 {
lab=VSS}
N 400 -340 480 -340 {
lab=VSS}
N 480 -310 480 -240 {
lab=VSS}
N 710 -340 790 -340 {
lab=VSS}
N 710 -310 710 -240 {
lab=VSS}
N 710 -620 710 -500 {
lab=iout}
N 710 -470 785 -470 {
lab=VSS}
N 710 -440 710 -370 {
lab=#net1}
N 480 -220 480 -180 {
lab=VSS}
N 630 -340 670 -340 {
lab=iin}
N 480 -680 480 -550 {
lab=iin}
N 280 -530 280 -500 {
lab=iin2}
N 280 -440 280 -220 {
lab=VSS}
N 280 -220 480 -220 {
lab=VSS}
N 480 -240 480 -220 {
lab=VSS}
N 480 -550 480 -500 {
lab=iin}
N 600 -470 670 -470 {
lab=iin2}
N 480 -440 480 -370 {
lab=#net2}
N 340 -470 375 -470 {
lab=iin2}
N 375 -525 375 -470 {
lab=iin2}
N 375 -525 600 -525 {
lab=iin2}
N 600 -525 600 -470 {
lab=iin2}
N 520 -470 600 -470 {
lab=iin2}
N 425 -470 480 -470 {
lab=VSS}
N 215 -470 280 -470 {
lab=VSS}
N 480 -550 630 -550 {
lab=iin}
N 630 -550 630 -340 {
lab=iin}
N 520 -340 630 -340 {
lab=iin}
N 280 -530 340 -530 {
lab=iin2}
N 340 -530 340 -470 {
lab=iin2}
N 320 -470 340 -470 {
lab=iin2}
N 280 -680 280 -530 {lab=iin2}
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
C {iopin.sym} 480 -680 0 0 {name=p2 lab=iin}
C {iopin.sym} 710 -620 0 0 {name=p3 lab=iout}
C {sg13g2_pr/sg13_lv_nmos.sym} 690 -470 0 0 {name=M3
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} 400 -340 0 0 {name=p4 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 790 -340 2 0 {name=p5 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 785 -470 2 0 {name=p6 sig_type=std_logic lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 300 -470 0 1 {name=M4
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 500 -470 0 1 {name=M5
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} 425 -470 0 0 {name=p7 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 215 -470 0 0 {name=p8 sig_type=std_logic lab=VSS}
C {iopin.sym} 280 -680 0 0 {name=p9 lab=iin2}
