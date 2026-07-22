v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 480 -240 710 -240 {
lab=VSS}
N 480 -240 480 -180 {
lab=VSS}
N 400 -340 480 -340 {
lab=VSS}
N 480 -310 480 -240 {
lab=VSS}
N 710 -340 790 -340 {
lab=#net1}
N 710 -310 710 -240 {
lab=VSS}
N 710 -400 710 -370 {
lab=#net2}
N 595 -340 670 -340 {
lab=iin}
N 710 -620 710 -500 {
lab=iout}
N 480 -470 480 -370 {
lab=iin}
N 480 -470 670 -470 {
lab=iin}
N 480 -560 480 -470 {
lab=iin}
N 710 -470 785 -470 {
lab=#net3}
N 595 -400 595 -340 {}
N 520 -340 595 -340 {
lab=iin}
N 595 -400 710 -400 {}
N 710 -440 710 -400 {
lab=#net2}
C {title.sym} 160 -40 0 0 {name=l1 author="Stefan Schippers"}
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
C {iopin.sym} 480 -560 0 0 {name=p2 lab=iin}
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
