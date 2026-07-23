v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 440 -630 440 -600 {
lab=CM_tail}
N 440 -630 560 -630 {
lab=CM_tail}
N 680 -630 680 -600 {
lab=CM_tail}
N 720 -570 780 -570 {
lab=vinp}
N 350 -570 400 -570 {
lab=vinn}
N 440 -540 440 -330 {
lab=net1}
N 680 -540 680 -330 {
lab=net2}
N 560 -670 560 -630 {
lab=CM_tail}
N 560 -630 680 -630 {
lab=CM_tail}
N 440 -570 560 -570 {
lab=VDD}
N 560 -570 560 -550 {
lab=VDD}
N 560 -570 680 -570 {
lab=VDD}
N 440 -270 440 -200 {
lab=drain_n}
N 680 -270 680 -200 {
lab=drain_p}
N 560 -300 640 -300 {
lab=VBIAS}
N 560 -360 560 -300 {
lab=VBIAS}
N 480 -300 560 -300 {
lab=VBIAS}
N 340 -300 440 -300 {
lab=VDD}
N 680 -300 790 -300 {
lab=VDD}
C {devices/title.sym} 180 -60 0 0 {name=l1 author="Copyright 2026 MacAnalog Research Group"}
C {ipin.sym} 780 -570 2 0 {name=p1 lab=vinp}
C {ipin.sym} 350 -570 2 1 {name=p2 lab=vinn}
C {ipin.sym} 560 -670 3 1 {name=p3 lab=CM_tail}
C {ipin.sym} 440 -200 3 0 {name=p4 lab=drain_n}
C {ipin.sym} 680 -200 3 0 {name=p5 lab=drain_p}
C {sg13g2_pr/sg13_lv_pmos.sym} 420 -570 0 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 700 -570 0 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {ipin.sym} 560 -550 3 0 {name=p6 lab=VDD}
C {sg13g2_pr/sg13_lv_pmos.sym} 460 -300 0 1 {name=M3
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 660 -300 0 0 {name=M4
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {ipin.sym} 560 -360 0 0 {name=p7 lab=VBIAS}
C {lab_pin.sym} 340 -300 0 0 {name=p8 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 790 -300 0 1 {name=p9 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 680 -430 0 1 {name=p10 sig_type=std_logic lab=net2}
C {lab_pin.sym} 440 -420 0 1 {name=p11 sig_type=std_logic lab=net1}
