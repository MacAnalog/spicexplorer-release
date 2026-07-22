v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 430 -330 430 -236 {
lab=VDD}
N 670 -730 670 -620 {
lab=VDD}
N 670 -560 670 -360 {
lab=#net1}
N 730 -590 730 -496 {
lab=VDD}
N 730 -330 730 -236 {
lab=VDD}
N 335 -730 335 -620 {
lab=VDD}
N 335 -560 335 -520 {
lab=iin2}
N 275 -590 275 -496 {
lab=VDD}
N 560 -330 630 -330 {
lab=iin}
N 670 -590 730 -590 {
lab=VDD}
N 275 -590 335 -590 {
lab=VDD}
N 490 -260 560 -260 {
lab=iin}
N 335 -520 410 -520 {
lab=iin2}
N 670 -330 730 -330 {
lab=VDD}
N 670 -730 1025 -730 {
lab=VDD}
N 490 -300 490 -260 {
lab=iin}
N 490 -260 490 -140 {
lab=iin}
N 490 -730 670 -730 {
lab=VDD}
N 190 -730 335 -730 {
lab=VDD}
N 670 -300 670 -130 {
lab=#net2}
N 430 -330 490 -330 {
lab=VDD}
N 410 -590 630 -590 {
lab=iin2}
N 410 -590 410 -520 {
lab=iin2}
N 375 -590 410 -590 {
lab=iin2}
N 490 -730 490 -360 {
lab=VDD}
N 335 -730 490 -730 {
lab=VDD}
N 560 -330 560 -260 {
lab=iin}
N 530 -330 560 -330 {
lab=iin}
N 330 -140 335 -520 {
lab=iin2}
N 670 -130 675 -130 {}
C {sg13g2_pr/sg13_lv_pmos.sym} 355 -590 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 650 -590 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 650 -330 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 510 -330 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {devices/lab_wire.sym} 275 -496 2 1 {name=l6 lab=VDD}
C {devices/lab_wire.sym} 730 -496 2 0 {name=l7 lab=VDD}
C {devices/lab_wire.sym} 730 -236 2 0 {name=l8 lab=VDD}
C {devices/lab_wire.sym} 430 -236 2 1 {name=l9 lab=VDD}
C {devices/iopin.sym} 675 -130 0 0 {name=p0 lab=iout}
C {title.sym} 200 -80 0 0 {name=l10 author="Stefan Schippers"}
C {devices/iopin.sym} 490 -140 0 0 {name=p1 lab=iin}
C {iopin.sym} 1020 -730 0 0 {name=p2 lab=VDD}
C {devices/iopin.sym} 330 -140 0 0 {name=p3 lab=iin2}
