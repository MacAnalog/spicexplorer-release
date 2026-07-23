v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 640 -1010 700 -1010 {
lab=VDD}
N 640 -1090 640 -1040 {
lab=VDD}
N 430 -790 490 -790 {
lab=VDD}
N 430 -850 430 -820 {
lab=#net1}
N 430 -850 520 -850 {
lab=#net1}
N 520 -920 520 -850 {
lab=#net1}
N 590 -790 650 -790 {
lab=VDD}
N 650 -850 650 -820 {
lab=#net1}
N 520 -850 650 -850 {
lab=#net1}
N 990 -760 990 -610 {
lab=#net2}
N 930 -790 990 -790 {
lab=VDD}
N 1030 -790 1080 -790 {
lab=vinp}
N 990 -850 990 -820 {
lab=#net1}
N 900 -850 990 -850 {
lab=#net1}
N 900 -920 900 -850 {
lab=#net1}
N 770 -760 770 -650 {
lab=vcmfb}
N 770 -790 830 -790 {
lab=VDD}
N 770 -850 770 -820 {
lab=#net1}
N 770 -850 900 -850 {
lab=#net1}
N 700 -790 730 -790 {
lab=vref}
N 650 -650 770 -650 {
lab=vcmfb}
N 650 -650 650 -420 {
lab=vcmfb}
N 640 -980 640 -920 {
lab=#net1}
N 640 -920 900 -920 {
lab=#net1}
N 260 -790 390 -790 {
lab=vinn}
N 560 -340 610 -340 {
lab=vcmfb}
N 650 -340 750 -340 {
lab=VSS}
N 650 -420 650 -370 {
lab=vcmfb}
N 560 -420 650 -420 {
lab=vcmfb}
N 560 -420 560 -340 {
lab=vcmfb}
N 940 -610 990 -610 {
lab=#net2}
N 430 -760 430 -610 {
lab=#net2}
N 650 -760 650 -650 {
lab=vcmfb}
N 650 -310 650 -200 {
lab=VSS}
N 850 -340 900 -340 {
lab=#net2}
N 940 -340 1040 -340 {
lab=VSS}
N 940 -420 940 -370 {
lab=#net2}
N 850 -420 940 -420 {
lab=#net2}
N 850 -420 850 -340 {
lab=#net2}
N 940 -310 940 -200 {
lab=VSS}
N 940 -610 940 -420 {
lab=#net2}
N 430 -610 940 -610 {
lab=#net2}
N 690 -790 700 -790 {
lab=vref}
N 400 -340 560 -340 {
lab=vcmfb}
N 510 -1090 640 -1090 {
lab=VDD}
N 640 -1140 640 -1090 {
lab=VDD}
N 510 -1090 510 -1010 {
lab=VDD}
N 510 -1010 600 -1010 {
lab=VDD}
N 640 -1140 1470 -1140 {
lab=VDD}
N 520 -920 640 -920 {
lab=#net1}
N 290 -200 650 -200 {
lab=VSS}
N 650 -200 940 -200 {
lab=VSS}
N 320 -1140 640 -1140 {
lab=VDD}
N 700 -880 720 -880 {
lab=vref}
N 700 -880 700 -790 {
lab=vref}
N 290 -1010 510 -1010 {
lab=VDD}
N 940 -200 1390 -200 {
lab=VSS}
C {devices/title.sym} 182.5 -82.5 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {iopin.sym} 320 -1140 0 1 {name=p1 lab=VDD}
C {ipin.sym} 1080 -790 0 1 {name=p3 lab=vinp}
C {ipin.sym} 260 -790 0 0 {name=p4 lab=vinn}
C {sg13g2_pr/sg13_lv_pmos.sym} 620 -1010 0 0 {name=M4
l=x_dut_xm4_opamp_rrl_l
w=x_dut_xm4_opamp_rrl_w
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 700 -1010 0 1 {name=p2 sig_type=std_logic lab=VDD}
C {sg13g2_pr/sg13_lv_pmos.sym} 410 -790 0 0 {name=M5
l=x_dut_xm5_opamp_rrl_l
w=x_dut_xm5_opamp_rrl_w
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 490 -790 0 1 {name=p5 sig_type=std_logic lab=VDD}
C {sg13g2_pr/sg13_lv_pmos.sym} 670 -790 0 1 {name=M6
l=x_dut_xm6_opamp_rrl_l
w=x_dut_xm6_opamp_rrl_w
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 590 -790 0 0 {name=p6 sig_type=std_logic lab=VDD}
C {sg13g2_pr/sg13_lv_pmos.sym} 1010 -790 0 1 {name=M7
l=x_dut_xm7_opamp_rrl_l
w=x_dut_xm7_opamp_rrl_w
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 930 -790 0 0 {name=p7 sig_type=std_logic lab=VDD}
C {sg13g2_pr/sg13_lv_pmos.sym} 750 -790 0 0 {name=M8
l=x_dut_xm8_opamp_rrl_l
w=x_dut_xm8_opamp_rrl_w
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 830 -790 0 1 {name=p11 sig_type=std_logic lab=VDD}
C {ipin.sym} 290 -1010 0 0 {name=p12 lab=vbias}
C {opin.sym} 400 -340 0 1 {name=p15 lab=vcmfb}
C {iopin.sym} 290 -200 0 1 {name=p16 lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 630 -340 0 0 {name=M15
l=x_dut_xm15_opamp_rrl_l
w=x_dut_xm15_opamp_rrl_w
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} 750 -340 0 1 {name=p24 sig_type=std_logic lab=VSS}
C {sg13g2_pr/sg13_lv_nmos.sym} 920 -340 0 0 {name=M16
l=x_dut_xm16_opamp_rrl_l
w=x_dut_xm16_opamp_rrl_w
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {lab_pin.sym} 1040 -340 0 1 {name=p25 sig_type=std_logic lab=VSS}
C {iopin.sym} 720 -880 0 0 {name=p26 lab=vref}
