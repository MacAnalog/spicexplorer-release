v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 160 -340 220 -340 {
lab=vinp}
N 160 -310 220 -310 {
lab=vinn}
N 890 -410 890 -370 {
lab=VDD}
N 840 -410 890 -410 {
lab=VDD}
N 920 -430 920 -370 {
lab=VSS}
N 840 -430 920 -430 {
lab=VSS}
N 950 -260 980 -260 {
lab=VSS}
N 980 -290 980 -260 {
lab=VSS}
N 950 -240 1060 -240 {
lab=vcmfb}
N 610 -340 650 -340 {
lab=#net1}
N 610 -480 610 -340 {
lab=#net1}
N 460 -320 650 -320 {
lab=#net2}
N 140 -480 610 -480 {}
C {devices/title.sym} 170 -50 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {shared/ideal/ideal-amp-fully-diff.sym} 670 -210 0 0 {name=x1}
C {shared/vcm-detector-simple.sym} 240 -290 0 0 {name=x2}
C {iopin.sym} 840 -430 0 1 {name=p1 lab=VSS}
C {iopin.sym} 840 -410 0 1 {name=p2 lab=VDD}
C {ipin.sym} 160 -340 0 0 {name=p3 lab=vinp}
C {ipin.sym} 160 -310 0 0 {name=p4 lab=vinn}
C {opin.sym} 1060 -240 0 0 {name=p5 lab=vcmfb}
C {lab_pin.sym} 980 -290 0 1 {name=p6 sig_type=std_logic lab=VSS}
C {ipin.sym} 140 -480 0 0 {name=p8 lab=vref}
