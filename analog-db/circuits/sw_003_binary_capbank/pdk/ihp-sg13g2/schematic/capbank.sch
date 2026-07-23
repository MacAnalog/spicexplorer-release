v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 1270 -1570 1270 -1040 {
lab=vout}
N 650 -1570 650 -1040 {
lab=vinp}
N 810 -1660 810 -1635 {
lab=VDD}
N 810 -1505 810 -1480 {
lab=VSS}
N 840 -1660 840 -1635 {
lab=V_D0}
N 840 -1505 840 -1480 {
lab=V_D0_NOT}
N 1070 -1570 1110 -1570 {
lab=#net1}
N 650 -1570 765 -1570 {
lab=vinp}
N 650 -1730 1090 -1730 {
lab=vinp}
N 1070 -1570 1070 -1300 {
lab=#net1}
N 920 -1570 1070 -1570 {
lab=#net1}
N 810 -1390 810 -1365 {
lab=VDD}
N 810 -1235 810 -1210 {
lab=VSS}
N 840 -1390 840 -1365 {
lab=V_D0_NOT}
N 840 -1235 840 -1210 {
lab=V_D0}
N 920 -1300 1070 -1300 {
lab=#net1}
N 560 -1300 765 -1300 {
lab=VCM}
N 100 -160 140 -160 {
lab=VDD}
N 100 -120 140 -120 {
lab=VSS}
N 100 -200 140 -200 {
lab=V_D0_NOT}
N 100 -230 140 -230 {
lab=V_D0}
N 100 -280 140 -280 {
lab=V_D1_NOT}
N 100 -310 140 -310 {
lab=V_D1}
N 100 -360 140 -360 {
lab=V_D2_NOT}
N 100 -390 140 -390 {
lab=V_D2}
N 650 -1730 650 -1570 {
lab=vinp}
N 480 -1730 650 -1730 {
lab=vinp}
N 1270 -1730 1270 -1570 {
lab=vout}
N 1270 -1730 1480 -1730 {
lab=vout}
N 560 -1300 560 -770 {
lab=VCM}
N 510 -1300 560 -1300 {
lab=VCM}
N 1270 -1040 1270 -510 {
lab=vout}
N 650 -1040 650 -510 {
lab=vinp}
N 820 -1130 820 -1105 {
lab=VDD}
N 820 -975 820 -950 {
lab=VSS}
N 850 -1130 850 -1105 {
lab=V_D1}
N 850 -975 850 -950 {
lab=V_D1_NOT}
N 1080 -1040 1120 -1040 {
lab=#net2}
N 650 -1040 775 -1040 {
lab=vinp}
N 1080 -1040 1080 -770 {
lab=#net2}
N 930 -1040 1080 -1040 {
lab=#net2}
N 820 -860 820 -835 {
lab=VDD}
N 820 -705 820 -680 {
lab=VSS}
N 850 -860 850 -835 {
lab=V_D1_NOT}
N 850 -705 850 -680 {
lab=V_D1}
N 930 -770 1080 -770 {
lab=#net2}
N 560 -770 775 -770 {
lab=VCM}
N 1170 -1570 1270 -1570 {
lab=vout}
N 1150 -1730 1270 -1730 {
lab=vout}
N 1180 -1040 1270 -1040 {
lab=vout}
N 820 -600 820 -575 {
lab=VDD}
N 820 -445 820 -420 {
lab=VSS}
N 850 -600 850 -575 {
lab=V_D2}
N 850 -445 850 -420 {
lab=V_D2_NOT}
N 1080 -510 1120 -510 {
lab=#net3}
N 650 -510 775 -510 {
lab=vinp}
N 1080 -510 1080 -240 {
lab=#net3}
N 930 -510 1080 -510 {
lab=#net3}
N 820 -330 820 -305 {
lab=VDD}
N 820 -175 820 -150 {
lab=VSS}
N 850 -330 850 -305 {
lab=V_D2_NOT}
N 850 -175 850 -150 {
lab=V_D2}
N 930 -240 1080 -240 {
lab=#net3}
N 560 -240 775 -240 {
lab=VCM}
N 1180 -510 1270 -510 {
lab=vout}
N 560 -770 560 -240 {
lab=VCM}
C {devices/title.sym} 170 -40 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {iopin.sym} 100 -160 0 1 {name=p4 lab=VDD}
C {iopin.sym} 100 -120 0 1 {name=p1 lab=VSS}
C {capa.sym} 1120 -1730 1 0 {name=C1
m=1
value=Cu
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 1140 -1570 1 0 {name=C2
m=1
value=Cu
footprint=1206
device="ceramic capacitor"}
C {ipin.sym} 100 -230 0 0 {name=p2 lab=V_D0}
C {ipin.sym} 100 -200 0 0 {name=p3 lab=V_D0_NOT}
C {ipin.sym} 100 -310 0 0 {name=p5 lab=V_D1}
C {ipin.sym} 100 -280 0 0 {name=p6 lab=V_D1_NOT}
C {ipin.sym} 100 -390 0 0 {name=p7 lab=V_D2}
C {ipin.sym} 100 -360 0 0 {name=p8 lab=V_D2_NOT}
C {shared/transmission_gate_pair.sym} 800 -1540 0 0 {name=x1}
C {lab_pin.sym} 810 -1480 0 0 {name=p9 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 810 -1660 0 0 {name=p10 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 840 -1660 0 1 {name=p11 sig_type=std_logic lab=V_D0}
C {lab_pin.sym} 840 -1480 0 1 {name=p12 sig_type=std_logic lab=V_D0_NOT}
C {shared/transmission_gate_pair.sym} 800 -1270 0 0 {name=x2}
C {lab_pin.sym} 810 -1210 0 0 {name=p13 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 810 -1390 0 0 {name=p14 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 840 -1210 0 1 {name=p15 sig_type=std_logic lab=V_D0}
C {lab_pin.sym} 840 -1390 0 1 {name=p16 sig_type=std_logic lab=V_D0_NOT}
C {ipin.sym} 480 -1730 0 0 {name=p17 lab=vinp}
C {opin.sym} 1480 -1730 0 1 {name=p18 lab=vout}
C {ipin.sym} 510 -1300 0 0 {name=p19 lab=VCM}
C {capa.sym} 1150 -1040 1 0 {name=C3
m=2
value=Cu
footprint=1206
device="ceramic capacitor"}
C {shared/transmission_gate_pair.sym} 810 -1010 0 0 {name=x3}
C {lab_pin.sym} 820 -950 0 0 {name=p20 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 820 -1130 0 0 {name=p21 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 850 -1130 0 1 {name=p22 sig_type=std_logic lab=V_D1}
C {lab_pin.sym} 850 -950 0 1 {name=p23 sig_type=std_logic lab=V_D1_NOT}
C {shared/transmission_gate_pair.sym} 810 -740 0 0 {name=x4}
C {lab_pin.sym} 820 -680 0 0 {name=p24 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 820 -860 0 0 {name=p25 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 850 -680 0 1 {name=p26 sig_type=std_logic lab=V_D1}
C {lab_pin.sym} 850 -860 0 1 {name=p27 sig_type=std_logic lab=V_D1_NOT}
C {capa.sym} 1150 -510 1 0 {name=C4
m=4
value=Cu
footprint=1206
device="ceramic capacitor"}
C {shared/transmission_gate_pair.sym} 810 -480 0 0 {name=x5}
C {lab_pin.sym} 820 -420 0 0 {name=p28 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 820 -600 0 0 {name=p29 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 850 -600 0 1 {name=p30 sig_type=std_logic lab=V_D2}
C {lab_pin.sym} 850 -420 0 1 {name=p31 sig_type=std_logic lab=V_D2_NOT}
C {shared/transmission_gate_pair.sym} 810 -210 0 0 {name=x6}
C {lab_pin.sym} 820 -150 0 0 {name=p32 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 820 -330 0 0 {name=p33 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 850 -150 0 1 {name=p34 sig_type=std_logic lab=V_D2}
C {lab_pin.sym} 850 -330 0 1 {name=p35 sig_type=std_logic lab=V_D2_NOT}
