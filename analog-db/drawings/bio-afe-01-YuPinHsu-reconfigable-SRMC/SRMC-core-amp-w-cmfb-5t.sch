v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 730 -710 730 -680 {
lab=VDD}
N 750 -710 750 -680 {
lab=VSS}
N 610 -510 660 -510 {
lab=vcmfb1}
N 610 -490 660 -490 {
lab=vcmfb2}
N 610 -460 660 -460 {
lab=VB2}
N 510 -560 660 -560 {
lab=vinp}
N 510 -540 660 -540 {
lab=vinn}
N 1050 -610 1200 -610 {
lab=#net1}
N 1490 -710 1490 -680 {
lab=VDD}
N 1470 -710 1470 -680 {
lab=VSS}
N 1530 -580 1580 -580 {
lab=vcmfb1}
N 1500 -470 1500 -440 {
lab=VDD}
N 1480 -470 1480 -440 {
lab=VSS}
N 1540 -340 1590 -340 {
lab=vcmfb2}
N 1120 -390 1240 -390 {
lab=voutp}
N 1120 -480 1120 -390 {
lab=voutp}
N 1050 -560 1120 -560 {
lab=voutp}
N 1080 -350 1240 -350 {
lab=voutn}
N 1050 -540 1080 -540 {
lab=voutn}
N 1080 -380 1080 -350 {
lab=voutn}
N 1150 -320 1240 -320 {
lab=V_REF_CMFB2}
N 1180 -560 1230 -560 {
lab=V_REF_CMFB1}
N 1037.5 -380 1080 -380 {
lab=voutn}
N 1080 -540 1080 -380 {
lab=voutn}
N 1120 -480 1142.5 -480 {
lab=voutp}
N 1120 -560 1120 -480 {
lab=voutp}
N 1160 -580 1180 -580 {
lab=V_REF_CMFB1}
N 1180 -580 1180 -560 {
lab=V_REF_CMFB1}
N 57.5 -440 410 -440 {
lab=VDD}
N 400 -120 730 -120 {
lab=VSS}
N 400 -160 400 -120 {
lab=VSS}
N 300 -120 400 -120 {
lab=VSS}
N 300 -160 300 -120 {
lab=VSS}
N 220 -120 300 -120 {
lab=VSS}
N 220 -160 220 -120 {
lab=VSS}
N 70 -120 220 -120 {
lab=VSS}
N 220 -260 220 -220 {
lab=V_REF_CMFB1}
N 300 -260 300 -220 {
lab=V_REF_CMFB2}
N 400 -260 400 -220 {
lab=VB2}
N 1200 -630 1200 -610 {
lab=#net1}
N 1200 -630 1230 -630 {
lab=#net1}
N 1050 -630 1180 -630 {
lab=#net2}
N 1180 -630 1180 -590 {
lab=#net2}
N 1180 -590 1230 -590 {
lab=#net2}
C {devices/title.sym} 192.5 -47.5 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {bio-afe-01-YuPinHsu-reconfigable-SRMC/SRMC-core-amp.sym} 680 -410 0 0 {name=x_amp_1}
C {shared/cmfb-output-amp-5t-pmos-input.sym} 1250 -520 0 0 {name=x1}
C {lab_pin.sym} 730 -710 0 0 {name=p2 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1490 -710 0 1 {name=p3 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 750 -710 0 1 {name=p5 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1470 -710 0 0 {name=p6 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 610 -510 0 0 {name=p7 sig_type=std_logic lab=vcmfb1}
C {lab_pin.sym} 1580 -580 0 1 {name=p8 sig_type=std_logic lab=vcmfb1}
C {shared/cmfb-output-amp-5t-pmos-input.sym} 1260 -280 0 0 {name=x2}
C {lab_pin.sym} 1500 -470 0 1 {name=p9 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1480 -470 0 0 {name=p10 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1590 -340 0 1 {name=p11 sig_type=std_logic lab=vcmfb2}
C {lab_pin.sym} 610 -490 0 0 {name=p12 sig_type=std_logic lab=vcmfb2}
C {lab_pin.sym} 1160 -580 0 0 {name=p15 sig_type=std_logic lab=V_REF_CMFB1}
C {lab_pin.sym} 1150 -320 0 0 {name=p16 sig_type=std_logic lab=V_REF_CMFB2}
C {vsource.sym} 400 -190 0 0 {name=V1 value=0.7 savecurrent=false}
C {vsource.sym} 300 -190 0 0 {name=V2 value=0.5 savecurrent=false}
C {vsource.sym} 220 -190 0 0 {name=V3 value=0.5 savecurrent=false}
C {lab_pin.sym} 220 -260 1 0 {name=p17 sig_type=std_logic lab=V_REF_CMFB1}
C {lab_pin.sym} 300 -260 1 0 {name=p18 sig_type=std_logic lab=V_REF_CMFB2}
C {lab_pin.sym} 400 -260 1 0 {name=p19 sig_type=std_logic lab=VB2}
C {lab_pin.sym} 610 -460 0 0 {name=p20 sig_type=std_logic lab=VB2}
C {ipin.sym} 512.5 -560 0 0 {name=p30 lab=vinp}
C {ipin.sym} 512.5 -540 0 0 {name=p13 lab=vinn}
C {opin.sym} 1142.5 -480 0 0 {name=p32 lab=voutp}
C {opin.sym} 1037.5 -380 0 1 {name=p14 lab=voutn}
C {iopin.sym} 57.5 -440 0 1 {name=p4 lab=VDD}
C {iopin.sym} 70 -120 0 1 {name=p1 lab=VSS}
