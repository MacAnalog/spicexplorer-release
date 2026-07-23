v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 900 -770 900 -676 {
lab=VDD}
N 900 -510 900 -416 {
lab=VDD}
N 840 -910 840 -800 {
lab=VDD}
N 840 -740 840 -540 {
lab=net1}
N 840 -480 840 -180 {
lab=iout}
N 650 -510 650 -220 {
lab=iin}
N 460 -910 460 -800 {
lab=VDD}
N 460 -740 460 -540 {
lab=net3}
N 460 -400 460 -320 {
lab=net2}
N 400 -770 400 -676 {
lab=VDD}
N 400 -510 400 -416 {
lab=VDD}
N 280 -910 460 -910 {
lab=VDD}
N 840 -770 900 -770 {
lab=VDD}
N 500 -770 570 -770 {
lab=net2}
N 400 -770 460 -770 {
lab=VDD}
N 840 -510 900 -510 {
lab=VDD}
N 500 -510 650 -510 {
lab=iin}
N 400 -510 460 -510 {
lab=VDD}
N 840 -910 1020 -910 {
lab=VDD}
N 650 -510 800 -510 {
lab=iin}
N 460 -910 840 -910 {
lab=VDD}
N 570 -770 570 -400 {
lab=net2}
N 570 -770 800 -770 {
lab=net2}
N 460 -400 570 -400 {
lab=net2}
N 460 -480 460 -400 {
lab=net2}
N 460 -220 460 -180 {
lab=iin}
N 460 -220 650 -220 {
lab=iin}
N 460 -260 460 -220 {
lab=iin}
C {sg13g2_pr/sg13_lv_pmos.sym} 480 -770 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 820 -770 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 820 -510 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 480 -510 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {devices/res.sym} 460 -290 0 1 {name=R1 value=1k}
C {devices/lab_wire.sym} 840 -680 2 1 {name=l3 lab=net1}
C {devices/lab_wire.sym} 740 -770 0 0 {name=l4 lab=net2}
C {devices/lab_wire.sym} 460 -680 2 1 {name=l6 lab=net3}
C {devices/lab_wire.sym} 400 -676 2 1 {name=l7 lab=VDD}
C {devices/lab_wire.sym} 900 -676 2 1 {name=l8 lab=VDD}
C {devices/lab_wire.sym} 900 -416 2 1 {name=l9 lab=VDD}
C {devices/lab_wire.sym} 400 -416 2 1 {name=l10 lab=VDD}
C {devices/title.sym} 190 -50 0 0 {name=l11 author="Copyright 2026 MacAnalog Research Group"}
C {iopin.sym} 1020 -910 0 0 {name=p1 lab=VDD}
C {iopin.sym} 840 -180 0 0 {name=p2 lab=iout}
C {iopin.sym} 460 -180 0 0 {name=p3 lab=iin}
