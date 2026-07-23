v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {Error Amplifier Implementation - TI LDO Paper} 480 -1080 0 0 0.4 0.4 {}
N 710 -430 870 -430 {lab=net_c}
N 870 -480 870 -430 {lab=net_c}
N 710 -430 710 -350 {lab=net_c}
N 270 -920 270 -900 {lab=vdd}
N 230 -920 230 -900 {lab=vss}
N 550 -950 550 -880 {lab=vdd}
N 710 -850 830 -850 {lab=net_d}
N 870 -950 870 -880 {lab=vdd}
N 550 -430 551.0461742708455 -480 {lab=net_c}
N 550 -430 710 -430 {lab=net_c}
N 870 -810 870 -540 {lab=net_b}
N 440 -790 440 -740 {lab=net_d}
N 440 -790 710 -790 {lab=net_d}
N 710 -850 710 -790 {lab=net_d}
N 480 -710 550 -710 {lab=net_a}
N 440 -680 440 -350 {lab=net_f}
N 910 -510 1050 -510 {lab=vinp}
N 1230 -560 1230 -350 {lab=vout}
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
N 370 -710 440 -710 {lab=vdd}
N 470 -850 550 -850 {lab=vdd}
N 870 -850 980 -850 {lab=vdd}
N 1230 -810 1310 -810 {lab=vdd}
N 990 -740 1030 -740 {lab=vdd}
N 550 -820 550 -710 {lab=net_a}
N 550 -710 551.0461742708455 -540 {lab=net_a}
N 551.0461742708455 -480 560 -480 {lab=net_c}
N 551.0461742708455 -540 560 -540 {lab=net_a}
N 560 -510 870 -510 {lab=vss}
N 500 -510 520 -510 {lab=vinn}
N 220 -660 220 -540 {lab=vdd}
N 440 -280 440 -270 {lab=vss}
N 220 -270 220 -260 {lab=vss}
N 340 -320 400 -320 {lab=#net2}
N 710 -280 710 -270 {lab=vss}
N 990 -280 990 -270 {lab=vss}
N 1230 -280 1230 -270 {lab=vss}
N 220 -380 220 -350 {lab=#net2}
N 220 -380 280 -380 {lab=#net2}
N 280 -380 280 -320 {lab=#net2}
N 340 -380 340 -320 {lab=#net2}
N 340 -380 620 -380 {lab=#net2}
N 620 -380 620 -320 {lab=#net2}
N 620 -320 670 -320 {lab=#net2}
N 620 -380 900 -380 {lab=#net2}
N 900 -380 900 -320 {lab=#net2}
N 900 -320 950 -320 {lab=#net2}
N 900 -380 1140 -380 {lab=#net2}
N 1140 -380 1140 -320 {lab=#net2}
N 1140 -320 1190 -320 {lab=#net2}
N 710 -320 820 -320 {lab=vss}
N 820 -320 820 -280 {lab=vss}
N 710 -280 820 -280 {lab=vss}
N 440 -320 560 -320 {lab=vss}
N 560 -320 560 -280 {lab=vss}
N 440 -280 560 -280 {lab=vss}
N 990 -320 1100 -320 {lab=vss}
N 1100 -320 1100 -280 {lab=vss}
N 990 -280 1100 -280 {lab=vss}
N 1230 -320 1360 -320 {lab=vss}
N 1360 -320 1360 -280 {lab=vss}
N 1230 -280 1360 -280 {lab=vss}
N 120 -320 220 -320 {lab=vss}
N 120 -320 120 -270 {lab=vss}
N 120 -270 220 -270 {lab=vss}
N 590 -850 710 -850 {lab=net_d}
N 870 -820 870 -810 {lab=net_b}
N 1230 -720 1230 -560 {lab=vout}
N 1230 -780 1230 -720 {lab=vout}
N 220 -480 220 -380 {lab=#net2}
N 260 -320 280 -320 {lab=#net2}
N 280 -320 340 -320 {lab=#net2}
N 710 -290 710 -280 {lab=vss}
N 440 -290 440 -280 {lab=vss}
N 990 -290 990 -280 {lab=vss}
N 1230 -290 1230 -280 {lab=vss}
N 220 -290 220 -270 {lab=vss}
N 260 -510 330 -510 {lab=#net2}
N 150 -510 220 -510 {lab=vdd}
N 330 -510 330 -450 {
lab=#net2}
N 220 -450 330 -450 {
lab=#net2}
C {symbols/nfet_06v0.sym} 890 -510 0 1 {name=M2
L=0.7u
W=68.542u
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
C {symbols/pfet_06v0.sym} 570 -850 0 1 {name=M3m
L=0.5u
W=69.545u
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
C {symbols/pfet_06v0.sym} 460 -710 0 1 {name=M4
L=0.5u
W=10u
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
L=0.5u
W=69.545u
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
L=3.8349u
W=20u
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
value=6.7168p
footprint=1206
device="ceramic capacitor"}
C {symbols/ppolyf_u_3k.sym} 1140 -740 1 0 {name=RZ
W=1u
L=9.476u
model=ppolyf_u_3k
spiceprefix=X
m=1}
C {devices/lab_pin.sym} 1140 -770 1 0 {name=p5 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 1030 -740 2 0 {name=p6 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 1310 -810 2 0 {name=p8 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 980 -850 2 0 {name=p9 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 470 -850 0 0 {name=p10 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 370 -710 0 0 {name=p12 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 440 -270 3 0 {name=p13 sig_type=std_logic lab=vss}
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
C {devices/lab_pin.sym} 710 -850 1 0 {name=p25 sig_type=std_logic lab=net_d}
C {devices/lab_pin.sym} 440 -630 2 1 {name=p27 sig_type=std_logic lab=net_f}
C {devices/lab_pin.sym} 940 -510 3 0 {name=p29 sig_type=std_logic lab=vinp}
C {devices/lab_pin.sym} 1310 -720 3 0 {name=p30 sig_type=std_logic lab=vout}
C {symbols/nfet_06v0.sym} 540 -510 0 0 {name=M1
L=0.7u
W=68.542u
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
C {devices/lab_pin.sym} 220 -660 1 0 {name=p19 sig_type=std_logic lab=vdd}
C {symbols/nfet_06v0.sym} 240 -320 0 1 {name=M_mirror_error_amp_ref
L=2u
W=34.533u
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
C {devices/lab_pin.sym} 220 -260 3 0 {name=p28 sig_type=std_logic lab=vss}
C {symbols/nfet_06v0.sym} 420 -320 0 0 {name=M_mirror_f
L=2u
W=5u
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
C {symbols/nfet_06v0.sym} 690 -320 0 0 {name=M_mirror_c
L=2u
W=34.533u
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
C {symbols/nfet_06v0.sym} 1210 -320 0 0 {name=M_mirror_ea_out
L=2u
W=34.533u
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
C {symbols/pfet_06v0.sym} 240 -510 0 1 {name=M_bias
L=2u
W=6.3111u
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
C {devices/lab_pin.sym} 150 -510 0 0 {name=p31 sig_type=std_logic lab=vdd}
N 1110 -810 1190 -810 {lab=net_b}
C {devices/lab_pin.sym} 1110 -810 2 0 {name=p_m6gate sig_type=std_logic lab=net_b}
