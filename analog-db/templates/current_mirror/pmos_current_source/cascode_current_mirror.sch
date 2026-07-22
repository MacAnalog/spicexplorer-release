v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 840 -600 840 -506 {
lab=VDD}
N 840 -340 840 -246 {
lab=VDD}
N 780 -740 780 -630 {
lab=VDD}
N 780 -570 780 -370 {
lab=net2}
N 780 -310 780 -140 {
lab=iout}
N 440 -600 440 -530 {
lab=#net1}
N 440 -340 440 -270 {
lab=iin}
N 400 -740 400 -630 {
lab=VDD}
N 400 -530 400 -370 {
lab=#net1}
N 400 -310 400 -270 {
lab=iin}
N 340 -600 340 -506 {
lab=VDD}
N 340 -340 340 -246 {
lab=VDD}
N 220 -740 400 -740 {
lab=VDD}
N 780 -600 840 -600 {
lab=VDD}
N 440 -600 740 -600 {
lab=#net1}
N 340 -600 400 -600 {
lab=VDD}
N 400 -530 440 -530 {
lab=#net1}
N 780 -340 840 -340 {
lab=VDD}
N 440 -340 740 -340 {
lab=iin}
N 340 -340 400 -340 {
lab=VDD}
N 400 -270 440 -270 {
lab=iin}
N 780 -740 960 -740 {
lab=VDD}
N 400 -740 780 -740 {
lab=VDD}
N 400 -570 400 -530 {
lab=#net1}
N 400 -270 400 -140 {
lab=iin}
C {sg13g2_pr/sg13_lv_pmos.sym} 420 -600 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 760 -600 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 760 -340 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 420 -340 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {devices/lab_wire.sym} 780 -510 2 1 {name=l6 lab=net2}
C {devices/lab_wire.sym} 340 -506 2 1 {name=l7 lab=VDD}
C {devices/lab_wire.sym} 840 -506 2 1 {name=l8 lab=VDD}
C {devices/lab_wire.sym} 840 -246 2 1 {name=l9 lab=VDD}
C {devices/lab_wire.sym} 340 -246 2 1 {name=l10 lab=VDD}
C {devices/iopin.sym} 780 -140 0 0 {name=p0 lab=iout}
C {iopin.sym} 960 -740 2 1 {name=p1 lab=VDD}
C {iopin.sym} 400 -140 2 0 {name=p2 lab=iin}
C {title.sym} 180 -60 0 0 {name=l1 author="Stefan Schippers"}
