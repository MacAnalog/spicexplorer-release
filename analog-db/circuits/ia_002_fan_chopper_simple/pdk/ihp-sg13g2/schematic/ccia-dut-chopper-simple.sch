v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
L 4 1637.5 -1035 1702.5 -1035 {}
L 4 1637.5 -1035 1647.5 -1040 {}
L 4 1637.5 -1035 1647.5 -1030 {}
L 4 1640 -967.5 1705 -967.5 {}
L 4 1695 -972.5 1705 -967.5 {}
L 4 1695 -962.5 1705 -967.5 {}
T {Ifb1} 1652.5 -1060 0 0 0.4 0.4 {}
T {Ifb2} 1690 -960 0 1 0.4 0.4 {}
T {Feedback Path} 1480 -902.5 0 0 0.4 0.4 {}
N 1425 -630 1640 -630 {
lab=#net1}
N 1460 -590 1640 -590 {
lab=#net2}
N 1610 -545 1640 -545 {
lab=vb4}
N 1610 -530 1640 -530 {
lab=vb3}
N 1610 -515 1640 -515 {
lab=vb2}
N 1610 -500 1640 -500 {
lab=vb1}
N 1680 -390 1680 -355 {
lab=clk_CHout}
N 1700 -390 1700 -335 {
lab=clk_CHout_not}
N 1640 -335 1700 -335 {
lab=clk_CHout_not}
N 1640 -355 1680 -355 {
lab=clk_CHout}
N 1750 -720 1750 -690 {
lab=VDD}
N 1770 -720 1770 -690 {
lab=VSS}
N 330 -130 330 -100 {
lab=VSS}
N 230 -130 230 -100 {
lab=VSS}
N 130 -130 130 -100 {
lab=VSS}
N 130 -100 230 -100 {
lab=VSS}
N 130 -230 130 -190 {
lab=vb1}
N 230 -230 230 -190 {
lab=vb2}
N 330 -230 330 -190 {
lab=vb3}
N 185 -360 465 -360 {
lab=VDD}
N 230 -100 330 -100 {
lab=VSS}
N 2085 -630 2205 -630 {
lab=voutn}
N 2160 -585 2205 -585 {
lab=voutp}
N 2050 -980 2085 -980 {
lab=voutn}
N 2085 -980 2085 -630 {
lab=voutn}
N 1940 -630 2085 -630 {
lab=voutn}
N 2050 -1020 2160 -1020 {
lab=voutp}
N 2160 -1020 2160 -585 {
lab=voutp}
N 1940 -585 2160 -585 {
lab=voutp}
N 1600 -1020 1745 -1020 {
lab=#net3}
N 1600 -1030 1600 -1020 {
lab=#net3}
N 1600 -980 1745 -980 {
lab=#net4}
N 1460 -980 1540 -980 {
lab=#net2}
N 1905 -880 1905 -845 {
lab=clk_CHfb}
N 1850 -845 1905 -845 {
lab=clk_CHfb}
N 1945 -880 1945 -825 {
lab=clk_CHfb_not}
N 1850 -825 1945 -825 {
lab=clk_CHfb_not}
N 1460 -980 1460 -590 {
lab=#net2}
N 1425 -1030 1540 -1030 {
lab=#net1}
N 1425 -1030 1425 -630 {
lab=#net1}
N 1240 -650 1270 -650 {
lab=#net1}
N 1270 -650 1270 -630 {
lab=#net1}
N 1320 -630 1425 -630 {
lab=#net1}
N 1320 -590 1460 -590 {
lab=#net2}
N 1270 -590 1270 -570 {
lab=#net2}
N 1240 -570 1270 -570 {
lab=#net2}
N 1985 -1110 1985 -1080 {
lab=VDD}
N 2005 -1110 2005 -1080 {
lab=VSS}
N 955 -485 955 -450 {
lab=clk_CHin}
N 900 -450 955 -450 {
lab=clk_CHin}
N 995 -485 995 -430 {
lab=clk_CHin_not}
N 900 -430 995 -430 {
lab=clk_CHin_not}
N 1035 -715 1035 -685 {
lab=VDD}
N 1055 -715 1055 -685 {
lab=VSS}
N 1135 -650 1180 -650 {
lab=#net5}
N 1135 -650 1135 -625 {
lab=#net5}
N 1100 -625 1135 -625 {
lab=#net5}
N 1100 -585 1135 -585 {
lab=#net6}
N 1135 -585 1135 -570 {
lab=#net6}
N 1135 -570 1180 -570 {
lab=#net6}
N 675 -585 795 -585 {
lab=vinp}
N 675 -625 795 -625 {
lab=vinn}
N 1320 -640 1320 -630 {
lab=#net1}
N 1270 -630 1320 -630 {
lab=#net1}
N 1320 -590 1320 -580 {
lab=#net2}
N 1270 -590 1320 -590 {
lab=#net2}
N 1320 -520 1320 -505 {
lab=Vref}
N 1320 -740 1320 -700 {
lab=Vref}
N 415 -100 520 -100 {
lab=VSS}
N 415 -130 415 -100 {
lab=VSS}
N 415 -230 415 -190 {
lab=vb4}
N 330 -100 415 -100 {
lab=VSS}
C {devices/title.sym} 172.5 -37.5 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {ccia-02-QinwenFan-chopper-ripple-reduction/two-stage-opamp-core.sym} 1660 -410 0 0 {name=x_CCIA_opamp}
C {lab_pin.sym} 1610 -545 0 0 {name=p1 sig_type=std_logic lab=vb4}
C {lab_pin.sym} 1610 -530 0 0 {name=p2 sig_type=std_logic lab=vb3}
C {lab_pin.sym} 1610 -515 0 0 {name=p3 sig_type=std_logic lab=vb2}
C {lab_pin.sym} 1610 -500 0 0 {name=p4 sig_type=std_logic lab=vb1}
C {vsource.sym} 130 -160 0 0 {name=Vb1 value=0.5 savecurrent=false}
C {vsource.sym} 230 -160 0 0 {name=Vb2 value=0.5 savecurrent=false}
C {vsource.sym} 330 -160 0 0 {name=Vb3 value=0.5 savecurrent=false}
C {iopin.sym} 520 -100 0 0 {name=p5 lab=VSS}
C {iopin.sym} 465 -360 0 0 {name=p6 lab=VDD}
C {lab_pin.sym} 130 -230 0 0 {name=p7 sig_type=std_logic lab=vb1}
C {lab_pin.sym} 230 -230 0 0 {name=p8 sig_type=std_logic lab=vb2}
C {lab_pin.sym} 330 -230 0 0 {name=p9 sig_type=std_logic lab=vb3}
C {opin.sym} 2205 -630 0 0 {name=p10 lab=voutn}
C {opin.sym} 2205 -585 0 0 {name=p11 lab=voutp}
C {shared/chopper-diff.sym} 1765 -900 0 0 {name=x_CH_fb}
C {capa.sym} 1570 -1030 1 0 {name=Cfb_1
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 1570 -980 1 0 {name=Cfb_2
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {lab_pin.sym} 1750 -720 0 0 {name=p12 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1770 -720 0 1 {name=p14 sig_type=std_logic lab=VSS}
C {capa.sym} 1210 -650 1 0 {name=C3
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 1210 -570 1 0 {name=C4
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {iopin.sym} 1640 -355 0 1 {name=p15 lab=clk_CHout}
C {iopin.sym} 1640 -335 0 1 {name=p16 lab=clk_CHout_not}
C {iopin.sym} 1850 -845 0 1 {name=p17 lab=clk_CHfb}
C {iopin.sym} 1850 -825 0 1 {name=p18 lab=clk_CHfb_not}
C {lab_pin.sym} 1985 -1110 0 0 {name=p19 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 2005 -1110 0 1 {name=p20 sig_type=std_logic lab=VSS}
C {shared/chopper-diff.sym} 815 -505 0 0 {name=x_CH_in}
C {iopin.sym} 900 -450 0 1 {name=p21 lab=clk_CHin}
C {iopin.sym} 900 -430 0 1 {name=p22 lab=clk_CHin_not}
C {lab_pin.sym} 1035 -715 0 0 {name=p23 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1055 -715 0 1 {name=p24 sig_type=std_logic lab=VSS}
C {ipin.sym} 675 -625 0 0 {name=p25 lab=vinn}
C {ipin.sym} 675 -585 0 0 {name=p26 lab=vinp}
C {res.sym} 1320 -670 2 0 {name=Rb1
value=1k
footprint=1206
device=resistor
m=1}
C {res.sym} 1320 -550 0 1 {name=Rb2
value=1k
footprint=1206
device=resistor
m=1}
C {iopin.sym} 1320 -740 0 1 {name=p27 lab=Vref}
C {lab_pin.sym} 1320 -505 0 0 {name=p28 sig_type=std_logic lab=Vref}
C {vsource.sym} 415 -160 0 0 {name=Vb4 value=0.5 savecurrent=false}
C {lab_pin.sym} 415 -230 0 0 {name=p13 sig_type=std_logic lab=vb4}
