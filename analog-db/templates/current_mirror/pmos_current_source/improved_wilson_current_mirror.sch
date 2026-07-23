v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 1050 -600 1050 -506 {
lab=VDD}
N 1050 -340 1050 -246 {
lab=VDD}
N 990 -740 990 -630 {
lab=VDD}
N 990 -530 990 -370 {
lab=net1}
N 990 -310 990 -150 {
lab=iout}
N 950 -600 950 -530 {
lab=net1}
N 610 -740 610 -630 {
lab=VDD}
N 610 -570 610 -370 {
lab=net2}
N 610 -310 610 -270 {
lab=iin}
N 550 -600 550 -506 {
lab=VDD}
N 550 -340 550 -246 {
lab=VDD}
N 430 -740 610 -740 {
lab=VDD}
N 990 -600 1050 -600 {
lab=VDD}
N 650 -600 950 -600 {
lab=net1}
N 550 -600 610 -600 {
lab=VDD}
N 950 -530 990 -530 {
lab=net1}
N 990 -340 1050 -340 {
lab=VDD}
N 700 -340 950 -340 {
lab=iin}
N 550 -340 610 -340 {
lab=VDD}
N 610 -270 700 -270 {
lab=iin}
N 990 -740 1170 -740 {
lab=VDD}
N 610 -740 990 -740 {
lab=VDD}
N 990 -570 990 -530 {
lab=net1}
N 610 -270 610 -150 {
lab=iin}
N 700 -340 700 -270 {
lab=iin}
N 650 -340 700 -340 {
lab=iin}
C {sg13g2_pr/sg13_lv_pmos.sym} 630 -600 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 970 -600 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 970 -340 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 630 -340 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {devices/lab_wire.sym} 890 -600 0 0 {name=l4 lab=net1}
C {devices/lab_wire.sym} 610 -510 2 1 {name=l5 lab=net2}
C {devices/lab_wire.sym} 550 -506 2 1 {name=l6 lab=VDD}
C {devices/lab_wire.sym} 1050 -506 2 1 {name=l7 lab=VDD}
C {devices/lab_wire.sym} 1050 -246 2 1 {name=l8 lab=VDD}
C {devices/lab_wire.sym} 550 -246 2 1 {name=l9 lab=VDD}
C {devices/title.sym} 210 -60 0 0 {name=l10 author="Copyright 2026 MacAnalog Research Group"}
C {iopin.sym} 1170 -740 0 0 {name=p1 lab=VDD}
C {iopin.sym} 990 -150 0 0 {name=p2 lab=iout}
C {iopin.sym} 610 -150 0 0 {name=p3 lab=iin}
