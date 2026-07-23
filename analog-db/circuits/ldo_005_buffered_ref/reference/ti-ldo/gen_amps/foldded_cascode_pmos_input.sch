v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Error Amplifier Implementation - TI LDO Paper} 480 -1080 0 0 0.4 0.4 {}
N 270 -920 270 -900 {lab=vdd}
N 230 -920 230 -900 {lab=vss}
N 710 -290 710 -270 {lab=vss}
N 1080 -360 1080 -340 {lab=vss}
N 1300 -360 1300 -340 {lab=vss}
N 600 -780 600 -760 {lab=vdd}
N 600 -700 600 -600 {lab=#net1}
N 480 -600 600 -600 {lab=#net1}
N 480 -600 480 -590 {lab=#net1}
N 600 -600 740 -600 {lab=#net1}
N 740 -600 740 -590 {lab=#net1}
N 480 -560 610 -560 {lab=vdd}
N 610 -560 740 -560 {lab=vdd}
N 780 -560 840 -560 {lab=vin_p}
N 380 -560 440 -560 {lab=vin_n}
N 1080 -720 1080 -420 {lab=#net2}
N 1300 -720 1300 -420 {lab=#net3}
N 1080 -960 1080 -940 {lab=vdd}
N 1080 -880 1080 -780 {lab=vout_n}
N 1300 -950 1300 -930 {lab=vdd}
N 1300 -870 1300 -770 {lab=vout_p}
N 1190 -780 1190 -750 {lab=vss}
N 1080 -750 1190 -750 {lab=vss}
N 1190 -750 1300 -750 {lab=vss}
N 920 -850 1010 -850 {lab=vb1}
N 1010 -850 1010 -750 {lab=vb1}
N 1010 -750 1040 -750 {lab=vb1}
N 1010 -850 1360 -850 {lab=vb1}
N 1360 -850 1360 -750 {lab=vb1}
N 1340 -750 1360 -750 {lab=vb1}
N 740 -530 740 -480 {lab=#net2}
N 740 -480 1080 -480 {lab=#net2}
N 480 -530 480 -440 {lab=#net3}
N 480 -440 1300 -440 {lab=#net3}
N 1080 -830 1110 -830 {lab=vout_n}
N 1280 -830 1300 -830 {lab=vout_p}
C {devices/isource.sym} 600 -730 0 0 {name=Iss value=1m}
C {devices/isource.sym} 1080 -390 0 0 {name=Iss1 value=1m}
C {devices/isource.sym} 1300 -390 0 0 {name=Iss2 value=1m}
C {symbols/pfet_06v0.sym} 460 -560 0 0 {name=M3
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
C {devices/lab_pin.sym} 600 -780 1 0 {name=p1 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 710 -270 3 0 {name=p14 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 1080 -340 3 0 {name=p15 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 1300 -340 3 0 {name=p16 sig_type=std_logic lab=vss}
C {devices/title.sym} 180 -50 0 0 {name=l1 author="Danial Noori Zadeh"}
C {symbols/nfet_06v0.sym} 1060 -750 0 0 {name=M1
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
C {symbols/pfet_06v0.sym} 760 -560 0 1 {name=M2
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
C {devices/lab_pin.sym} 610 -560 3 0 {name=p5 sig_type=std_logic lab=vdd}
C {devices/ipin.sym} 380 -560 0 0 {name=p6 lab=vin_n}
C {devices/ipin.sym} 840 -560 0 1 {name=p8 lab=vin_p}
C {symbols/nfet_06v0.sym} 1320 -750 0 1 {name=M4
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
C {devices/isource.sym} 1080 -910 0 0 {name=I1 value=1m}
C {devices/lab_pin.sym} 1080 -960 1 0 {name=p9 sig_type=std_logic lab=vdd}
C {devices/isource.sym} 1300 -900 0 0 {name=I2 value=1m}
C {devices/lab_pin.sym} 1300 -950 1 0 {name=p2 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 1190 -780 1 0 {name=p4 sig_type=std_logic lab=vss}
C {devices/ipin.sym} 920 -850 2 1 {name=p10 lab=vb1}
C {devices/opin.sym} 1110 -830 0 0 {name=p12 lab=vout_n}
C {devices/opin.sym} 1280 -830 0 1 {name=p13 lab=vout_p}
