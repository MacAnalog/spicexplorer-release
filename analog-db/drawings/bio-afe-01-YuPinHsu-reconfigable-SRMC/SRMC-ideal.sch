v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 1430 -670 1480 -670 {
lab=voutp}
N 1480 -740 1480 -670 {
lab=voutp}
N 1580 -740 1710 -740 {
lab=voutp}
N 1430 -650 1480 -650 {
lab=voutn}
N 1480 -650 1480 -580 {
lab=voutn}
N 1580 -580 1720 -580 {
lab=voutn}
N 1370 -810 1370 -780 {
lab=VDD}
N 1400 -810 1400 -780 {
lab=VSS}
N 980 -730 980 -420 {
lab=#net1}
N 980 -750 1130 -750 {
lab=#net2}
N 100 -170 170 -170 {
lab=V_PHI}
N 100 -150 170 -150 {
lab=V_PHI_NOT}
N 1580 -860 1580 -740 {
lab=voutp}
N 1480 -740 1580 -740 {
lab=voutp}
N 1280 -980 1580 -980 {
lab=voutp}
N 1280 -860 1580 -860 {
lab=voutp}
N 1580 -980 1580 -860 {
lab=voutp}
N 370 -980 370 -750 {
lab=#net3}
N 980 -860 1220 -860 {
lab=#net2}
N 980 -860 980 -750 {
lab=#net2}
N 780 -750 980 -750 {
lab=#net2}
N 1580 -580 1580 -360 {
lab=voutn}
N 1280 -240 1580 -240 {
lab=voutn}
N 1280 -360 1580 -360 {
lab=voutn}
N 1580 -360 1580 -240 {
lab=voutn}
N 980 -360 1220 -360 {
lab=#net1}
N 1480 -580 1580 -580 {
lab=voutn}
N 980 -420 980 -360 {
lab=#net1}
N 780 -420 980 -420 {
lab=#net1}
N 300 -750 370 -750 {
lab=#net3}
N 60 -750 130 -750 {
lab=vinp}
N 360 -420 625 -420 {
lab=#net4}
N 60 -420 130 -420 {
lab=vinn}
N 100 -120 170 -120 {
lab=VDD}
N 100 -100 170 -100 {
lab=VSS}
N 670 -840 670 -815 {
lab=VDD}
N 670 -685 670 -660 {
lab=VSS}
N 700 -840 700 -815 {
lab=V_PHI}
N 700 -685 700 -660 {
lab=V_PHI_NOT}
N 370 -750 625 -750 {
lab=#net3}
N 370 -980 1220 -980 {
lab=#net3}
N 980 -730 1130 -730 {
lab=#net1}
N 670 -510 670 -485 {
lab=VDD}
N 670 -355 670 -330 {
lab=VSS}
N 700 -510 700 -485 {
lab=V_PHI}
N 700 -355 700 -330 {
lab=V_PHI_NOT}
N 300 -420 360 -420 {
lab=#net4}
N 360 -240 1220 -240 {
lab=#net4}
N 360 -420 360 -240 {
lab=#net4}
N 365 -670 390 -670 {
lab=VSS}
N 210 -640 235 -640 {
lab=V_PHI_NOT}
N 365 -640 390 -640 {
lab=V_PHI}
N 300 -750 300 -715 {
lab=#net3}
N 190 -750 300 -750 {
lab=#net3}
N 300 -560 300 -420 {
lab=#net4}
N 190 -420 300 -420 {
lab=#net4}
N 200 -670 235 -670 {
lab=VDD}
C {shared/ideal/ideal-amp-fully-diff.sym} 1150 -620 0 0 {name=x1}
C {iopin.sym} 100 -170 0 1 {name=p4 lab=V_PHI}
C {iopin.sym} 100 -150 0 1 {name=p1 lab=V_PHI_NOT}
C {res.sym} 1250 -980 1 0 {name=Rf1
value=1k
footprint=1206
device=resistor
m=1}
C {capa.sym} 1250 -860 1 0 {name=Cf1
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {res.sym} 1250 -240 1 1 {name=Rf2
value=1k
footprint=1206
device=resistor
m=1}
C {capa.sym} 1250 -360 1 1 {name=Cf2
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {res.sym} 160 -750 1 0 {name=R2
value=1k
footprint=1206
device=resistor
m=1}
C {res.sym} 160 -420 1 0 {name=R4
value=1k
footprint=1206
device=resistor
m=1}
C {lab_pin.sym} 1370 -810 0 0 {name=p2 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1400 -810 0 1 {name=p3 sig_type=std_logic lab=VSS}
C {ipin.sym} 60 -750 0 0 {name=p11 lab=vinp}
C {ipin.sym} 60 -420 0 0 {name=p12 lab=vinn}
C {opin.sym} 1720 -580 0 0 {name=p15 lab=voutn}
C {opin.sym} 1710 -740 0 0 {name=p16 lab=voutp}
C {iopin.sym} 100 -120 0 1 {name=p8 lab=VDD}
C {iopin.sym} 100 -100 0 1 {name=p9 lab=VSS}
C {devices/title.sym} 162.5 -37.5 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {shared/transmission_gate_pair.sym} 660 -720 0 0 {name=x_sw_1}
C {lab_pin.sym} 670 -660 0 0 {name=p28 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 670 -840 0 0 {name=p29 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 700 -660 0 1 {name=p31 sig_type=std_logic lab=V_PHI_NOT}
C {lab_pin.sym} 700 -840 1 0 {name=p10 sig_type=std_logic lab=V_PHI}
C {shared/transmission_gate_pair.sym} 660 -390 0 0 {name=x_sw_2}
C {lab_pin.sym} 670 -330 0 0 {name=p13 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 670 -510 0 0 {name=p14 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 700 -330 0 1 {name=p17 sig_type=std_logic lab=V_PHI_NOT}
C {lab_pin.sym} 700 -510 1 0 {name=p18 sig_type=std_logic lab=V_PHI}
C {shared/transmission_gate_pair.sym} 330 -680 3 1 {name=x_sw_3}
C {lab_pin.sym} 390 -670 0 1 {name=p7 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 200 -670 2 1 {name=p19 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 210 -640 0 0 {name=p20 sig_type=std_logic lab=V_PHI_NOT}
C {lab_pin.sym} 390 -640 2 0 {name=p21 sig_type=std_logic lab=V_PHI}
