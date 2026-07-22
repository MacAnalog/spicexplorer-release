v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 480 -240 710 -240 {
lab=VSS}
N 480 -235 480 -180 {
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
N 560 -340 670 -340 {
lab=iin2}
N 710 -440 710 -370 {
lab=#net1}
N 480 -410 480 -370 {
lab=iin2}
N 480 -500 480 -410 {
lab=iin2}
N 480 -410 560 -410 {
lab=iin2}
N 560 -410 560 -340 {
lab=iin2}
N 520 -340 560 -340 {
lab=iin2}
N 340 -640 480 -640 {
lab=iin}
N 480 -680 480 -640 {
lab=iin}
N 340 -550 340 -500 {
lab=iin}
N 420 -470 670 -470 {
lab=iin}
N 340 -440 340 -235 {
lab=VSS}
N 340 -235 480 -235 {
lab=VSS}
N 480 -240 480 -235 {
lab=VSS}
N 260 -470 340 -470 {
lab=VSS}
N 340 -550 420 -550 {
lab=iin}
N 340 -640 340 -550 {
lab=iin}
N 420 -550 420 -470 {
lab=iin}
N 380 -470 420 -470 {
lab=iin}
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
C {iopin.sym} 480 -680 0 0 {name=p2 lab=iin}
C {iopin.sym} 710 -620 0 0 {name=p3 lab=iout}
C {iopin.sym} 480 -500 0 0 {name=p8 lab=iin2}
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
C {sg13g2_pr/sg13_lv_nmos.sym} 360 -470 0 1 {name=M4
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} 260 -470 0 0 {name=p7 sig_type=std_logic lab=VSS}
