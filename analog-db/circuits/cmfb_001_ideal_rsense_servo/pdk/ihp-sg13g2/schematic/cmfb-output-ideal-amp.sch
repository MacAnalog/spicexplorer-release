v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 220 -330 280 -330 {
lab=vinp}
N 220 -300 280 -300 {
lab=vinn}
N 910 -410 910 -370 {
lab=VDD}
N 860 -410 910 -410 {
lab=VDD}
N 940 -430 940 -370 {
lab=VSS}
N 860 -430 940 -430 {
lab=VSS}
N 970 -260 1000 -260 {
lab=VSS}
N 1000 -290 1000 -260 {
lab=VSS}
N 970 -240 1080 -240 {
lab=vcmfb}
N 210 -400 630 -400 {}
N 630 -400 630 -340 {}
N 630 -340 670 -340 {}
N 520 -310 630 -310 {}
N 630 -320 630 -310 {}
N 630 -320 670 -320 {}
C {devices/title.sym} 190 -50 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {shared/ideal/ideal-amp-fully-diff.sym} 690 -210 0 0 {name=x1}
C {shared/vcm-detector-simple.sym} 300 -280 0 0 {name=x2}
C {iopin.sym} 860 -430 0 1 {name=p1 lab=VSS}
C {iopin.sym} 860 -410 0 1 {name=p2 lab=VDD}
C {ipin.sym} 220 -330 0 0 {name=p3 lab=vinp}
C {ipin.sym} 220 -300 0 0 {name=p4 lab=vinn}
C {opin.sym} 1080 -240 0 0 {name=p5 lab=vcmfb}
C {lab_pin.sym} 1000 -290 0 1 {name=p6 sig_type=std_logic lab=VSS}
C {ipin.sym} 210 -400 0 0 {name=p8 lab=vref}
