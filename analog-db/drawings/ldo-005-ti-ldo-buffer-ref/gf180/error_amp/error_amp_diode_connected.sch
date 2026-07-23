v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Error Amplifier Implementation - TI LDO Paper} 480 -1080 0 0 0.4 0.4 {}
N 570 -430 870 -430 {lab=net_c}
N 870 -480 870 -430 {lab=net_c}
N 710 -430 710 -350 {lab=net_c}
N 270 -920 270 -900 {lab=vdd}
N 230 -920 230 -900 {lab=vss}
N 550 -950 550 -880 {lab=vdd}
N 590 -850 830 -850 {lab=net_a}
N 870 -950 870 -880 {lab=vdd}
N 550 -430 551.0461742708455 -480 {lab=net_c}
N 550 -430 570 -430 {lab=net_c}
N 870 -820 870 -540 {lab=net_b}
N 790 -510 870 -510 {lab=vss}
N 910 -510 1050 -510 {lab=vinp}
N 990 -710 990 -350 {lab=net_e}
N 1230 -780 1230 -350 {lab=vout}
N 990 -810 990 -770 {lab=net_b}
N 870 -810 990 -810 {lab=net_b}
N 990 -810 1090 -810 {lab=net_b}
N 1090 -810 1090 -740 {lab=net_b}
N 1090 -740 1110 -740 {lab=net_b}
N 1140 -780 1140 -760 {lab=vdd}
N 1170 -740 1190 -740 {lab=#net1}
N 1190 -740 1190 -680 {lab=#net1}
N 1190 -620 1190 -560 {lab=vout}
N 1190 -560 1230 -560 {lab=vout}
N 1230 -950 1230 -840 {lab=vdd}
N 1230 -720 1370 -720 {lab=vout}
N 930 -740 950 -740 {lab=net_e}
N 930 -740 930 -670 {lab=net_e}
N 930 -670 990 -670 {lab=net_e}
N 930 -790 930 -740 {lab=net_e}
N 930 -790 1110 -790 {lab=net_e}
N 1110 -810 1110 -790 {lab=net_e}
N 1110 -810 1190 -810 {lab=net_e}
N 470 -850 550 -850 {lab=vdd}
N 870 -850 980 -850 {lab=vdd}
N 1230 -810 1310 -810 {lab=vdd}
N 990 -740 1030 -740 {lab=vdd}
N 710 -290 710 -270 {lab=vss}
N 990 -290 990 -270 {lab=vss}
N 1230 -290 1230 -270 {lab=vss}
N 550 -820 550 -710 {lab=net_a}
N 550 -710 551.0461742708455 -540 {lab=net_a}
N 551.0461742708455 -480 560 -480 {lab=net_c}
N 551.0461742708455 -540 560 -540 {lab=net_a}
N 560 -510 790 -510 {lab=vss}
N 500 -510 520 -510 {lab=vinn}
N 680 -850 680 -760 {lab=net_a}
N 550 -760 680 -760 {lab=net_a}
C {symbols/nfet_06v0.sym} 890 -510 0 1 {name=M2
L=0.70u
W=0.30u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_06v0
spiceprefix=X
}
C {devices/isource.sym} 710 -320 0 0 {name=I1 value=1m}
C {devices/isource.sym} 990 -320 0 0 {name=I2 value=1m}
C {devices/isource.sym} 1230 -320 0 0 {name=I3 value=1m}
C {symbols/pfet_06v0.sym} 570 -850 0 1 {name=M3
L=0.50u
W=0.30u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_06v0
spiceprefix=X
}
C {symbols/pfet_06v0.sym} 850 -850 0 0 {name=M5
L=0.50u
W=0.30u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_06v0
spiceprefix=X
}
C {symbols/pfet_06v0.sym} 1210 -810 0 0 {name=M6
L=0.50u
W=0.30u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_06v0
spiceprefix=X
}
C {symbols/pfet_06v0.sym} 970 -740 0 0 {name=M7
L=0.50u
W=0.30u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_06v0
spiceprefix=X
}
C {devices/iopin.sym} 270 -920 1 1 {name=p3 lab=vdd}
C {devices/iopin.sym} 230 -920 3 0 {name=vss lab=vss}
C {devices/lab_pin.sym} 270 -900 3 0 {name=p7 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 230 -900 3 0 {name=p11 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 550 -950 1 0 {name=p1 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 870 -950 1 0 {name=p2 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 1230 -950 1 0 {name=p4 sig_type=std_logic lab=vdd}
C {devices/capa.sym} 1190 -650 0 1 {name=Cc
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {symbols/ppolyf_u_3k.sym} 1140 -740 1 0 {name=RZ
W=1e-6
L=1e-6
model=ppolyf_u_3k
spiceprefix=X
m=1}
C {devices/lab_pin.sym} 1140 -770 1 0 {name=p5 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 1030 -740 2 0 {name=p6 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 1310 -810 2 0 {name=p8 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 980 -850 2 0 {name=p9 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 470 -850 0 0 {name=p10 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 710 -270 3 0 {name=p14 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 990 -270 3 0 {name=p15 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 1230 -270 3 0 {name=p16 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 790 -510 0 0 {name=p18 sig_type=std_logic lab=vss}
C {devices/ipin.sym} 1050 -510 2 0 {name=p20 lab=vinp}
C {devices/opin.sym} 1370 -720 2 1 {name=p21 lab=vout}
C {devices/title.sym} 180 -50 0 0 {name=l1 author="Danial Noori Zadeh"}
C {devices/lab_pin.sym} 550 -710 2 0 {name=p22 sig_type=std_logic lab=net_a}
C {devices/lab_pin.sym} 870 -710 0 0 {name=p23 sig_type=std_logic lab=net_b}
C {devices/lab_pin.sym} 710 -430 1 0 {name=p24 sig_type=std_logic lab=net_c}
C {devices/lab_pin.sym} 990 -670 2 0 {name=p26 sig_type=std_logic lab=net_e}
C {devices/lab_pin.sym} 940 -510 3 0 {name=p29 sig_type=std_logic lab=vinp}
C {devices/lab_pin.sym} 1310 -720 3 0 {name=p30 sig_type=std_logic lab=vout}
C {symbols/nfet_06v0.sym} 540 -510 0 0 {name=M1
L=0.70u
W=0.30u
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_06v0
spiceprefix=X
}
C {devices/ipin.sym} 500 -510 0 0 {name=p17 lab=vinn}
