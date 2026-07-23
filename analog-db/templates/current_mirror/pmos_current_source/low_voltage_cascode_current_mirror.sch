v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 890 -520 890 -426 {
lab=VDD}
N 890 -260 890 -166 {
lab=VDD}
N 830 -660 830 -550 {
lab=VDD}
N 830 -490 830 -290 {
lab=net1}
N 830 -230 830 -100 {
lab=iout}
N 450 -660 450 -550 {
lab=VDD}
N 450 -490 450 -290 {
lab=net2}
N 450 -190 450 -100 {
lab=iin}
N 390 -520 390 -426 {
lab=VDD}
N 390 -260 390 -166 {
lab=VDD}
N 270 -660 450 -660 {
lab=VDD}
N 830 -520 890 -520 {
lab=VDD}
N 490 -520 610 -520 {
lab=iin}
N 390 -520 450 -520 {
lab=VDD}
N 830 -260 890 -260 {
lab=VDD}
N 760 -260 790 -260 {
lab=VBIAS}
N 390 -260 450 -260 {
lab=VDD}
N 830 -660 1010 -660 {
lab=VDD}
N 450 -660 830 -660 {
lab=VDD}
N 610 -520 610 -190 {
lab=iin}
N 610 -520 790 -520 {
lab=iin}
N 450 -190 610 -190 {
lab=iin}
N 450 -230 450 -190 {
lab=iin}
N 760 -340 760 -260 {
lab=VBIAS}
N 490 -260 760 -260 {
lab=VBIAS}
N 200 -340 760 -340 {
lab=VBIAS}
C {sg13g2_pr/sg13_lv_pmos.sym} 470 -520 0 1 {name=M1 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 810 -520 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 810 -260 0 0 {name=M3 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {sg13g2_pr/sg13_lv_pmos.sym} 470 -260 0 1 {name=M4 model=sg13_lv_pmos spiceprefix=X w=0.15u l=0.13u}
C {devices/lab_wire.sym} 730 -260 0 0 {name=l1 lab=VBIAS}
C {devices/lab_wire.sym} 830 -430 2 1 {name=l5 lab=net1}
C {devices/lab_wire.sym} 450 -430 2 1 {name=l6 lab=net2}
C {devices/lab_wire.sym} 390 -426 2 1 {name=l7 lab=VDD}
C {devices/lab_wire.sym} 890 -426 2 1 {name=l8 lab=VDD}
C {devices/lab_wire.sym} 890 -166 2 1 {name=l9 lab=VDD}
C {devices/lab_wire.sym} 390 -166 2 1 {name=l10 lab=VDD}
C {devices/title.sym} 160 -50 0 0 {name=l11 author="Copyright 2026 MacAnalog Research Group"}
C {iopin.sym} 1010 -660 0 0 {name=p1 lab=VDD}
C {iopin.sym} 450 -100 0 1 {name=p2 lab=iin}
C {iopin.sym} 200 -340 0 1 {name=p3 lab=VBIAS}
C {iopin.sym} 830 -100 0 1 {name=p4 lab=iout}
