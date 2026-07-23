v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 100 -165 140 -165 {
lab=VDD}
N 100 -125 140 -125 {
lab=VSS}
N 1785 -522.5 2325 -522.5 {
lab=#net1}
N 1785 -392.5 2305 -392.5 {
lab=#net2}
N 1135 -522.5 1385 -522.5 {
lab=#net3}
N 1135 -522.5 1135 -477.5 {
lab=#net3}
N 1110 -477.5 1135 -477.5 {
lab=#net3}
N 1135 -392.5 1385 -392.5 {
lab=#net4}
N 1135 -457.5 1135 -392.5 {
lab=#net4}
N 1110 -457.5 1135 -457.5 {
lab=#net4}
N 2305 -480 2305 -392.5 {
lab=#net2}
N 2305 -480 2325 -480 {
lab=#net2}
N 2625 -522.5 2727.5 -522.5 {
lab=voutp}
N 2625 -477.5 2645 -477.5 {
lab=voutn}
N 2645 -477.5 2645 -442.5 {
lab=voutn}
N 2645 -442.5 2730 -442.5 {
lab=voutn}
N 2625 -382.5 2700 -382.5 {
lab=VDD}
N 2625 -352.5 2700 -352.5 {
lab=VSS}
N 2365 -322.5 2365 -242.5 {
lab=V_PHI}
N 2395 -322.5 2395 -242.5 {
lab=V_PHI_NOT}
N 1525 -242.5 1525 -212.5 {
lab=V_D2}
N 1505 -242.5 1505 -212.5 {
lab=V_D2_NOT}
N 1485 -242.5 1485 -212.5 {
lab=V_D1}
N 1465 -242.5 1465 -212.5 {
lab=V_D1_NOT}
N 1445 -242.5 1445 -212.5 {
lab=V_D0}
N 1425 -242.5 1425 -212.5 {
lab=V_D0_NOT}
N 650 -477.5 705 -477.5 {
lab=vinp}
N 650 -522.5 650 -477.5 {
lab=vinp}
N 650 -457.5 705 -457.5 {
lab=vinn}
N 650 -457.5 650 -382.5 {
lab=vinn}
N 1785 -302.5 1825 -302.5 {
lab=VDD}
N 1785 -282.5 1825 -282.5 {
lab=VSS}
N 780 -602.5 780 -562.5 {
lab=VSS}
N 760 -602.5 760 -562.5 {
lab=VDD}
N 582.5 -522.5 650 -522.5 {
lab=vinp}
N 565 -382.5 650 -382.5 {
lab=vinn}
N 97.5 -260 137.5 -260 {
lab=V_D0_NOT}
N 97.5 -290 137.5 -290 {
lab=V_D0}
N 97.5 -340 137.5 -340 {
lab=V_D1_NOT}
N 97.5 -370 137.5 -370 {
lab=V_D1}
N 97.5 -420 137.5 -420 {
lab=V_D2_NOT}
N 97.5 -450 137.5 -450 {
lab=V_D2}
N 1312.5 -355 1385 -355 {
lab=VCM}
C {devices/title.sym} 180 -45 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {iopin.sym} 100 -165 0 1 {name=p4 lab=VDD}
C {iopin.sym} 100 -125 0 1 {name=p1 lab=VSS}
C {bio-afe-01-YuPinHsu-reconfigable-SRMC/ccia-ideal.sym} 725 -282.5 0 0 {name=x_ia}
C {bio-afe-01-YuPinHsu-reconfigable-SRMC/PGA-ideal.sym} 1405 -262.5 0 0 {name=x_pga}
C {bio-afe-01-YuPinHsu-reconfigable-SRMC/SRMC-ideal.sym} 2345 -342.5 0 0 {name=x_srmc_filter}
C {ipin.sym} 565 -382.5 0 0 {name=p29 lab=vinn}
C {ipin.sym} 582.5 -522.5 0 0 {name=p30 lab=vinp}
C {opin.sym} 2727.5 -522.5 0 0 {name=p31 lab=voutp}
C {opin.sym} 2730 -442.5 0 0 {name=p32 lab=voutn}
C {lab_pin.sym} 1825 -302.5 0 1 {name=p2 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1825 -282.5 0 1 {name=p3 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 2700 -382.5 0 1 {name=p5 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 2700 -352.5 0 1 {name=p6 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 760 -602.5 3 1 {name=p7 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 780 -602.5 3 1 {name=p8 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1425 -212.5 3 0 {name=p16 sig_type=std_logic lab=V_D0_NOT}
C {lab_pin.sym} 1445 -212.5 3 0 {name=p17 sig_type=std_logic lab=V_D0}
C {lab_pin.sym} 1465 -212.5 3 0 {name=p18 sig_type=std_logic lab=V_D1_NOT}
C {lab_pin.sym} 1485 -212.5 3 0 {name=p19 sig_type=std_logic lab=V_D1}
C {lab_pin.sym} 1505 -212.5 3 0 {name=p20 sig_type=std_logic lab=V_D2_NOT}
C {lab_pin.sym} 1525 -212.5 3 0 {name=p21 sig_type=std_logic lab=V_D2}
C {ipin.sym} 97.5 -290 0 0 {name=p22 lab=V_D0}
C {ipin.sym} 97.5 -260 0 0 {name=p23 lab=V_D0_NOT}
C {ipin.sym} 97.5 -370 0 0 {name=p24 lab=V_D1}
C {ipin.sym} 97.5 -340 0 0 {name=p25 lab=V_D1_NOT}
C {ipin.sym} 97.5 -450 0 0 {name=p26 lab=V_D2}
C {ipin.sym} 97.5 -420 0 0 {name=p27 lab=V_D2_NOT}
C {iopin.sym} 1312.5 -355 0 1 {name=p33 lab=VCM}
C {ipin.sym} 2365 -242.5 0 0 {name=p9 lab=V_PHI}
C {ipin.sym} 2395 -242.5 0 1 {name=p10 lab=V_PHI_NOT}
