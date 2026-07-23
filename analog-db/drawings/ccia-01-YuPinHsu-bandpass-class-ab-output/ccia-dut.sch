v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 490 -160 490 -130 {
lab=VSS}
N 390 -160 390 -130 {
lab=VSS}
N 290 -160 290 -130 {
lab=VSS}
N 490 -130 540 -130 {
lab=VSS}
N 390 -130 490 -130 {
lab=VSS}
N 290 -130 390 -130 {
lab=VSS}
N 1450 -630 1450 -600 {
lab=VSS}
N 1420 -630 1420 -600 {
lab=VDD}
N 1130 -500 1180 -500 {
lab=vb1}
N 1130 -480 1180 -480 {
lab=vb2}
N 1130 -460 1180 -460 {
lab=vb3}
N 290 -260 290 -220 {
lab=vb1}
N 390 -260 390 -220 {
lab=vb2}
N 490 -260 490 -220 {
lab=vb3}
N 130 -340 410 -340 {
lab=VDD}
N 920 -570 1180 -570 {
lab=#net1}
N 1020 -550 1180 -550 {
lab=#net2}
N 1020 -550 1020 -500 {
lab=#net2}
N 980 -500 1020 -500 {
lab=#net2}
N 150 -160 150 -130 {
lab=VSS}
N 110 -130 150 -130 {
lab=VSS}
N 150 -260 150 -220 {
lab=vcmfb_ref}
N 150 -130 290 -130 {
lab=VSS}
N 1480 -450 1530 -450 {
lab=vcmfb_ref}
N 1530 -450 1530 -390 {
lab=vcmfb_ref}
N 1610 -470 1750 -470 {
lab=voutp}
N 1480 -490 1560 -490 {
lab=voutn}
N 1560 -540 1560 -490 {
lab=voutn}
N 1560 -540 1750 -540 {
lab=voutn}
N 1180 -210 1210 -210 {
lab=#net2}
N 1240 -210 1420 -210 {
lab=#net3}
N 1240 -170 1240 -150 {
lab=#net2}
N 1180 -150 1240 -150 {
lab=#net2}
N 1180 -210 1180 -150 {
lab=#net2}
N 1420 -170 1420 -150 {
lab=voutp}
N 1420 -150 1490 -150 {
lab=voutp}
N 1490 -210 1490 -150 {
lab=voutp}
N 1450 -210 1490 -210 {
lab=voutp}
N 660 -570 780 -570 {
lab=vinp}
N 660 -500 780 -500 {
lab=vinn}
N 1490 -310 1610 -310 {
lab=voutp}
N 1490 -310 1490 -210 {
lab=voutp}
N 1180 -310 1290 -310 {
lab=#net2}
N 1180 -310 1180 -210 {
lab=#net2}
N 1350 -310 1490 -310 {
lab=voutp}
N 980 -310 1180 -310 {
lab=#net2}
N 980 -500 980 -310 {
lab=#net2}
N 840 -500 980 -500 {
lab=#net2}
N 1610 -470 1610 -310 {
lab=voutp}
N 1480 -470 1610 -470 {
lab=voutp}
N 1370 -860 1400 -860 {
lab=voutn}
N 1160 -860 1340 -860 {
lab=#net4}
N 1340 -920 1340 -900 {
lab=voutn}
N 1340 -920 1400 -920 {
lab=voutn}
N 1400 -920 1400 -860 {
lab=voutn}
N 1160 -920 1160 -900 {
lab=#net1}
N 1090 -920 1160 -920 {
lab=#net1}
N 1090 -920 1090 -860 {
lab=#net1}
N 1090 -860 1130 -860 {
lab=#net1}
N 1090 -800 1090 -760 {
lab=#net1}
N 1290 -760 1400 -760 {
lab=voutn}
N 1400 -800 1400 -760 {
lab=voutn}
N 1090 -760 1230 -760 {
lab=#net1}
N 920 -800 920 -570 {
lab=#net1}
N 840 -570 920 -570 {
lab=#net1}
N 920 -800 1090 -800 {
lab=#net1}
N 1090 -860 1090 -800 {
lab=#net1}
N 1400 -800 1560 -800 {
lab=voutn}
N 1400 -860 1400 -800 {
lab=voutn}
N 1560 -800 1560 -540 {
lab=voutn}
C {devices/title.sym} 180 -40 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {ccia-01-YuPinHsu-bandpass-class-ab-output/two-stage-ota-core.sym} 1200 -440 0 0 {name=x1}
C {vsource.sym} 290 -190 0 0 {name=Vb1 value=0.5 savecurrent=false}
C {vsource.sym} 390 -190 0 0 {name=Vb2 value=0.5 savecurrent=false}
C {vsource.sym} 490 -190 0 0 {name=Vb3 value=0.5 savecurrent=false}
C {iopin.sym} 540 -130 0 0 {name=p1 lab=VSS}
C {lab_pin.sym} 1450 -630 0 1 {name=p2 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1420 -630 0 0 {name=p3 sig_type=std_logic lab=VDD}
C {iopin.sym} 410 -340 0 0 {name=p4 lab=VDD}
C {lab_pin.sym} 290 -260 0 0 {name=p5 sig_type=std_logic lab=vb1}
C {lab_pin.sym} 390 -260 0 0 {name=p6 sig_type=std_logic lab=vb2}
C {lab_pin.sym} 490 -260 0 0 {name=p7 sig_type=std_logic lab=vb3}
C {lab_pin.sym} 1130 -500 0 0 {name=p8 sig_type=std_logic lab=vb1}
C {lab_pin.sym} 1130 -480 0 0 {name=p9 sig_type=std_logic lab=vb2}
C {lab_pin.sym} 1130 -460 0 0 {name=p10 sig_type=std_logic lab=vb3}
C {ipin.sym} 660 -570 0 0 {name=p11 lab=vinp}
C {ipin.sym} 660 -500 0 0 {name=p12 lab=vinn}
C {vsource.sym} 150 -190 0 0 {name=Vcmfb_ref value=0.5 savecurrent=false}
C {lab_pin.sym} 150 -260 0 0 {name=p13 sig_type=std_logic lab=vcmfb_ref}
C {lab_pin.sym} 1530 -390 0 0 {name=p14 sig_type=std_logic lab=vcmfb_ref}
C {opin.sym} 1750 -540 0 0 {name=p15 lab=voutn}
C {opin.sym} 1750 -470 0 0 {name=p16 lab=voutp}
C {capa.sym} 810 -570 3 0 {name=Cin_2
m=1
value=Cin
footprint=1206
device="ceramic capacitor"}
C {sg13g2_pr/sg13_lv_pmos.sym} 1240 -190 1 1 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1420 -190 3 0 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {capa.sym} 810 -500 3 0 {name=Cin_1
m=1
value=Cin
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 1320 -310 3 0 {name=Cf_1
m=1
value=Cf
footprint=1206
device="ceramic capacitor"}
C {sg13g2_pr/sg13_lv_pmos.sym} 1340 -880 3 1 {name=M3
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1160 -880 1 0 {name=M4
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {capa.sym} 1260 -760 1 0 {name=Cf_2
m=1
value=Cf
footprint=1206
device="ceramic capacitor"}
