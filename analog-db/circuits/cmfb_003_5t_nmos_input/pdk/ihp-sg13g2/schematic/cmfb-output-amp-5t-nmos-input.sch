v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 220 -500 280 -500 {
lab=vinp}
N 220 -470 280 -470 {
lab=vinn}
N 910 -410 910 -370 {
lab=VDD}
N 860 -410 910 -410 {
lab=VDD}
N 940 -430 940 -370 {
lab=VSS}
N 860 -430 940 -430 {
lab=VSS}
N 970 -240 1080 -240 {
lab=vcmfb}
N 210 -320 670 -320 {
lab=vref}
N 630 -340 670 -340 {
lab=vcm_detected}
N 520 -480 630 -480 {
lab=vcm_detected}
N 630 -480 630 -340 {
lab=vcm_detected}
C {devices/title.sym} 190 -50 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {shared/vcm-detector-simple.sym} 300 -450 0 0 {name=x2}
C {iopin.sym} 860 -430 0 1 {name=p1 lab=VSS}
C {iopin.sym} 860 -410 0 1 {name=p2 lab=VDD}
C {ipin.sym} 220 -500 0 0 {name=p3 lab=vinp}
C {ipin.sym} 220 -470 0 0 {name=p4 lab=vinn}
C {opin.sym} 1080 -240 0 0 {name=p5 lab=vcmfb}
C {ipin.sym} 210 -320 0 0 {name=p8 lab=vref}
C {shared/amp-single-ended-5t-nmos-input.sym} 690 -210 0 0 {name=x1}
C {lab_pin.sym} 630 -400 0 1 {name=p6 sig_type=std_logic lab=vcm_detected}
