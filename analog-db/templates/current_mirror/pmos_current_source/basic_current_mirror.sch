v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 545 -300 670 -300 {
lab=iin}
N 480 -400 480 -330 {
lab=VSS}
N 480 -400 710 -400 {
lab=VSS}
N 710 -400 710 -330 {
lab=VSS}
N 480 -460 480 -400 {
lab=VSS}
N 400 -300 480 -300 {
lab=VDD}
N 710 -300 790 -300 {
lab=VDD}
N 480 -270 480 -240 {
lab=iin}
N 710 -270 710 -200 {
lab=iout}
N 480 -240 545 -240 {
lab=iin}
N 480 -240 480 -200 {
lab=iin}
N 545 -300 545 -240 {
lab=iin}
N 520 -300 545 -300 {
lab=iin}
C {title.sym} 160 -40 0 0 {name=l1 author="Stefan Schippers"}
C {iopin.sym} 480 -460 2 1 {name=p1 lab=VDD}
C {iopin.sym} 480 -200 2 1 {name=p2 lab=iin}
C {iopin.sym} 710 -200 2 1 {name=p3 lab=iout}
C {sg13g2_pr/sg13_lv_pmos.sym} 690 -300 0 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 500 -300 0 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 400 -300 0 0 {name=p4 sig_type=std_logic lab=VDD
}
C {lab_pin.sym} 790 -300 0 1 {name=p5 sig_type=std_logic lab=VDD
}
