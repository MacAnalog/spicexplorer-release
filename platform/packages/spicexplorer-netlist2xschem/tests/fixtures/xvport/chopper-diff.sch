v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 830 -960 980 -960 {
lab=VB_p}
N 190 -960 385 -960 {
lab=VA_p}
N 540 -635 540 -590 {
lab=VSS}
N 570 -635 570 -590 {
lab=Vctl}
N 930 -120 1000 -120 {
lab=Vctl_not}
N 1090 -120 1170 -120 {
lab=VSS}
N 460 -1070 460 -1025 {
lab=Vctl}
N 930 -140 1000 -140 {
lab=Vctl}
N 570 -800 570 -765 {
lab=Vctl_not}
N 430 -1060 430 -1025 {
lab=VDD}
N 540 -800 540 -765 {
lab=VDD}
N 430 -895 430 -870 {
lab=VSS}
N 460 -895 460 -870 {
lab=#net2}
N 590 -550 590 -505 {
lab=Vctl_not}
N 560 -540 560 -505 {
lab=VDD}
N 560 -375 560 -350 {
lab=VSS}
N 590 -375 590 -350 {
lab=Vctl}
N 920 -700 980 -700 {
lab=VB_n}
N 190 -700 495 -700 {
lab=VA_p}
N 190 -960 190 -700 {
lab=VA_p}
N 120 -960 190 -960 {
lab=VA_p}
N 350 -390 350 -345 {
lab=Vctl}
N 320 -380 320 -345 {
lab=VDD}
N 320 -215 320 -190 {
lab=VSS}
N 350 -215 350 -190 {
lab=Vctl_not}
N 200 -280 275 -280 {
lab=VA_n}
N 200 -440 200 -280 {
lab=VA_n}
N 140 -280 200 -280 {
lab=VA_n}
N 200 -440 515 -440 {
lab=VA_n}
N 670 -440 830 -440 {
lab=VB_p}
N 430 -280 920 -280 {
lab=VB_n}
N 830 -960 830 -440 {
lab=VB_p}
N 540 -960 830 -960 {
lab=VB_p}
N 920 -700 920 -280 {
lab=VB_n}
N 650 -700 920 -700 {
lab=VB_n}
N 1090 -140 1170 -140 {
lab=VDD}
C {devices/title.sym} 180 -50 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {ccia-02-QinwenFan-chopper-ripple-reduction/transmission_gate_pair.sym} 420 -930 0 0 {name=x1}
C {ccia-02-QinwenFan-chopper-ripple-reduction/transmission_gate_pair.sym} 530 -670 0 0 {name=x2}
C {lab_pin.sym} 540 -800 2 1 {name=p1 sig_type=std_logic lab=VDD}
C {iopin.sym} 120 -960 0 1 {name=p3 lab=VA_p}
C {iopin.sym} 140 -280 0 1 {name=p4 lab=VA_n}
C {iopin.sym} 980 -960 0 0 {name=p5 lab=VB_p}
C {iopin.sym} 930 -140 0 1 {name=p7 lab=Vctl}
C {iopin.sym} 930 -120 0 1 {name=p8 lab=Vctl_not}
C {iopin.sym} 1090 -120 0 1 {name=p9 lab=VSS}
C {iopin.sym} 1090 -140 0 1 {name=p10 lab=VDD}
C {lab_pin.sym} 430 -870 0 0 {name=p2 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 540 -590 2 1 {name=p11 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 430 -1060 0 0 {name=p12 sig_type=std_logic lab=VDD}
C {ccia-02-QinwenFan-chopper-ripple-reduction/transmission_gate_pair.sym} 550 -410 0 0 {name=x3}
C {lab_pin.sym} 560 -350 0 0 {name=p13 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 560 -540 0 0 {name=p14 sig_type=std_logic lab=VDD}
C {iopin.sym} 980 -700 0 0 {name=p15 lab=VB_n}
C {ccia-02-QinwenFan-chopper-ripple-reduction/transmission_gate_pair.sym} 310 -250 0 0 {name=x4}
C {lab_pin.sym} 320 -190 0 0 {name=p6 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 320 -380 0 0 {name=p16 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 460 -1070 0 1 {name=p17 sig_type=std_logic lab=Vctl}
C {lab_pin.sym} 570 -800 0 1 {name=p18 sig_type=std_logic lab=Vctl_not}
C {lab_pin.sym} 590 -550 0 1 {name=p19 sig_type=std_logic lab=Vctl_not}
C {lab_pin.sym} 350 -390 0 1 {name=p20 sig_type=std_logic lab=Vctl}
C {lab_pin.sym} 460 -870 0 1 {name=p21 sig_type=std_logic lab=Vctl_not}
C {lab_pin.sym} 570 -590 0 1 {name=p22 sig_type=std_logic lab=Vctl}
C {lab_pin.sym} 590 -350 0 1 {name=p23 sig_type=std_logic lab=Vctl}
C {lab_pin.sym} 350 -190 0 1 {name=p24 sig_type=std_logic lab=Vctl_not}
