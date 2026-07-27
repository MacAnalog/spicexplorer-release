v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 1080 -220 1080 -160 {
lab=vinp}
N 1260 -220 1260 -160 {
lab=vinn}
N 190 -660 190 -620 {
lab=VDD}
N 140 -660 190 -660 {
lab=VDD}
N 220 -680 220 -620 {
lab=VSS}
N 140 -680 220 -680 {
lab=VSS}
N 1170 -550 1170 -440 {
lab=vcmfb}
N 220 -300 220 -220 {
lab=vcm}
N 220 -220 315 -220 {
lab=vcm}
N 470 -220 660 -220 {
lab=#net1}
N 660 -300 660 -220 {
lab=#net1}
N 220 -440 220 -360 {
lab=vbias}
N 220 -440 315 -440 {
lab=vbias}
N 470 -440 660 -440 {
lab=#net2}
N 660 -440 660 -360 {
lab=#net2}
N 360 -375 360 -360 {
lab=VSS}
N 390 -375 390 -360 {
lab=clk_PHI_not}
N 390 -300 390 -285 {
lab=clk_PHI}
N 360 -300 360 -285 {
lab=VDD}
N 360 -155 360 -140 {
lab=VSS}
N 390 -155 390 -140 {
lab=clk_PHI_not}
N 360 -520 360 -505 {
lab=VDD}
N 390 -520 390 -505 {
lab=clk_PHI}
N 460 -660 460 -620 {
lab=clk_PHI}
N 410 -660 460 -660 {
lab=clk_PHI}
N 490 -680 490 -620 {
lab=clk_PHI_not}
N 410 -680 490 -680 {
lab=clk_PHI_not}
N 120 -440 220 -440 {
lab=vbias}
N 120 -220 220 -220 {
lab=vcm}
N 660 -220 755 -220 {
lab=#net1}
N 660 -440 755 -440 {
lab=#net2}
N 800 -375 800 -360 {
lab=VSS}
N 830 -375 830 -360 {
lab=clk_PHI}
N 830 -300 830 -285 {
lab=clk_PHI_not}
N 800 -300 800 -285 {
lab=VDD}
N 800 -155 800 -140 {
lab=VSS}
N 830 -155 830 -140 {
lab=clk_PHI}
N 800 -520 800 -505 {
lab=VDD}
N 830 -520 830 -505 {
lab=clk_PHI_not}
N 910 -220 1080 -220 {
lab=vinp}
N 2120 -300 2120 -220 {
lab=vcm}
N 2025 -220 2120 -220 {
lab=vcm}
N 1680 -220 1870 -220 {
lab=#net3}
N 1680 -300 1680 -220 {
lab=#net3}
N 2120 -440 2120 -360 {
lab=vbias}
N 2025 -440 2120 -440 {
lab=vbias}
N 1680 -440 1870 -440 {
lab=#net4}
N 1680 -440 1680 -360 {
lab=#net4}
N 1980 -375 1980 -360 {
lab=VSS}
N 1950 -375 1950 -360 {
lab=clk_PHI_not}
N 1950 -300 1950 -285 {
lab=clk_PHI}
N 1980 -300 1980 -285 {
lab=VDD}
N 1980 -155 1980 -140 {
lab=VSS}
N 1950 -155 1950 -140 {
lab=clk_PHI_not}
N 1980 -520 1980 -505 {
lab=VDD}
N 1950 -520 1950 -505 {
lab=clk_PHI}
N 2120 -440 2220 -440 {
lab=vbias}
N 2120 -220 2220 -220 {
lab=vcm}
N 1585 -220 1680 -220 {
lab=#net3}
N 1585 -440 1680 -440 {
lab=#net4}
N 1540 -375 1540 -360 {
lab=VSS}
N 1510 -375 1510 -360 {
lab=clk_PHI}
N 1510 -300 1510 -285 {
lab=clk_PHI_not}
N 1540 -300 1540 -285 {
lab=VDD}
N 1540 -155 1540 -140 {
lab=VSS}
N 1510 -155 1510 -140 {
lab=clk_PHI}
N 1540 -520 1540 -505 {
lab=VDD}
N 1510 -520 1510 -505 {
lab=clk_PHI_not}
N 1260 -220 1430 -220 {
lab=vinn}
N 910 -440 1170 -440 {
lab=vcmfb}
N 1170 -440 1430 -440 {
lab=vcmfb}
C {devices/title.sym} 190 -50 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {iopin.sym} 140 -680 0 1 {name=p1 lab=VSS}
C {iopin.sym} 140 -660 0 1 {name=p2 lab=VDD}
C {ipin.sym} 1080 -160 3 0 {name=p3 lab=vinp}
C {ipin.sym} 1260 -160 3 0 {name=p4 lab=vinn}
C {opin.sym} 1170 -550 3 0 {name=p5 lab=vcmfb}
C {ipin.sym} 120 -440 0 0 {name=p8 lab=vbias}
C {capa.sym} 220 -330 0 0 {name=C1
m=1
value=cmfb_cm2
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 660 -330 0 0 {name=C2
m=1
value=cmfb_cm1
footprint=1206
device="ceramic capacitor"}
C {shared/transmission_gate_pair.sym} 350 -190 0 0 {name=x1}
C {lab_pin.sym} 190 -620 0 0 {name=p6 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 220 -620 0 1 {name=p7 sig_type=std_logic lab=VSS}
C {shared/transmission_gate_pair.sym} 350 -410 0 0 {name=x2}
C {iopin.sym} 410 -680 0 1 {name=p9 lab=clk_PHI_not}
C {iopin.sym} 410 -660 0 1 {name=p10 lab=clk_PHI}
C {lab_pin.sym} 460 -620 0 0 {name=p11 sig_type=std_logic lab=clk_PHI}
C {lab_pin.sym} 490 -620 0 1 {name=p12 sig_type=std_logic lab=clk_PHI_not}
C {lab_pin.sym} 360 -520 0 0 {name=p13 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 360 -300 0 0 {name=p14 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 360 -140 0 0 {name=p15 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 360 -360 0 0 {name=p16 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 390 -360 0 1 {name=p17 sig_type=std_logic lab=clk_PHI_not}
C {lab_pin.sym} 390 -140 0 1 {name=p18 sig_type=std_logic lab=clk_PHI_not}
C {lab_pin.sym} 390 -520 0 1 {name=p19 sig_type=std_logic lab=clk_PHI}
C {lab_pin.sym} 390 -300 0 1 {name=p20 sig_type=std_logic lab=clk_PHI}
C {ipin.sym} 120 -220 0 0 {name=p21 lab=vcm}
C {shared/transmission_gate_pair.sym} 790 -190 0 0 {name=x3}
C {shared/transmission_gate_pair.sym} 790 -410 0 0 {name=x4}
C {lab_pin.sym} 800 -520 0 0 {name=p22 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 800 -300 0 0 {name=p23 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 800 -140 0 0 {name=p24 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 800 -360 0 0 {name=p25 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 830 -520 0 1 {name=p26 sig_type=std_logic lab=clk_PHI_not}
C {lab_pin.sym} 830 -300 0 1 {name=p27 sig_type=std_logic lab=clk_PHI_not}
C {lab_pin.sym} 830 -360 0 1 {name=p28 sig_type=std_logic lab=clk_PHI}
C {lab_pin.sym} 830 -140 0 1 {name=p29 sig_type=std_logic lab=clk_PHI}
C {capa.sym} 2120 -330 0 1 {name=C3
m=1
value=cmfb_cm2
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 1680 -330 0 1 {name=C4
m=1
value=cmfb_cm1
footprint=1206
device="ceramic capacitor"}
C {shared/transmission_gate_pair.sym} 1990 -190 0 1 {name=x5}
C {shared/transmission_gate_pair.sym} 1990 -410 0 1 {name=x6}
C {lab_pin.sym} 1980 -520 0 1 {name=p33 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1980 -300 0 1 {name=p34 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1980 -140 0 1 {name=p35 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1980 -360 0 1 {name=p36 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1950 -360 0 0 {name=p37 sig_type=std_logic lab=clk_PHI_not}
C {lab_pin.sym} 1950 -140 0 0 {name=p38 sig_type=std_logic lab=clk_PHI_not}
C {lab_pin.sym} 1950 -520 0 0 {name=p39 sig_type=std_logic lab=clk_PHI}
C {lab_pin.sym} 1950 -300 0 0 {name=p40 sig_type=std_logic lab=clk_PHI}
C {shared/transmission_gate_pair.sym} 1550 -190 0 1 {name=x7}
C {shared/transmission_gate_pair.sym} 1550 -410 0 1 {name=x8}
C {lab_pin.sym} 1540 -520 0 1 {name=p42 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1540 -300 0 1 {name=p43 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1540 -140 0 1 {name=p44 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1540 -360 0 1 {name=p45 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1510 -520 0 0 {name=p46 sig_type=std_logic lab=clk_PHI_not}
C {lab_pin.sym} 1510 -300 0 0 {name=p47 sig_type=std_logic lab=clk_PHI_not}
C {lab_pin.sym} 1510 -360 0 0 {name=p48 sig_type=std_logic lab=clk_PHI}
C {lab_pin.sym} 1510 -140 0 0 {name=p49 sig_type=std_logic lab=clk_PHI}
C {lab_pin.sym} 2220 -220 0 1 {name=p30 sig_type=std_logic lab=vcm}
C {lab_pin.sym} 2220 -440 0 1 {name=p32 sig_type=std_logic lab=vbias}
