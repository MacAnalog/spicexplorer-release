v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 80 -230 120 -230 {
lab=vinp}
N 80 -190 120 -190 {
lab=vinn}
N 80 -160 120 -160 {
lab=vref}
N 360 -310 360 -280 {
lab=VSS}
N 380 -310 380 -280 {
lab=VDD}
N 420 -180 460 -180 {
lab=#net1}
N 290 -100 380 -100 {
lab=#net2}
N 380 -40 380 -20 {
lab=VSS}
C {shared/cmfb-output-diff-pair-sense.sym} 140 -120 0 0 {name=x1}
C {vsource.sym} 380 -70 0 0 {name=V1 value=3 savecurrent=false}
C {lab_pin.sym} 380 -20 0 0 {name=p1 sig_type=std_logic lab=VSS}
C {iopin.sym} 380 -310 0 0 {name=p2 lab=VDD}
C {ipin.sym} 80 -190 0 0 {name=p4 lab=vinn}
C {iopin.sym} 360 -310 0 1 {name=p3 lab=VSS}
C {ipin.sym} 80 -230 0 0 {name=p5 lab=vinp}
C {ipin.sym} 80 -160 0 0 {name=p6 lab=vref}
C {opin.sym} 460 -180 0 0 {name=p7 lab=vcmfb}
