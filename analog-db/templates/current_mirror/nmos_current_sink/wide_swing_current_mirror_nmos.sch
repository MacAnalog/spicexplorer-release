v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 450 -880 450 -850 {
lab=net1}
N 450 -730 450 -700 {
lab=IIN}
N 730 -880 730 -790 {
lab=net2}
N 970 -880 970 -790 {
lab=net3}
N 660 -760 690 -760 {
lab=IIN}
N 650 -910 690 -910 {
lab=net1}
N 830 -910 930 -910 {
lab=net1}
N 830 -910 830 -850 {
lab=net1}
N 650 -850 830 -850 {
lab=net1}
N 650 -910 650 -850 {
lab=net1}
N 530 -910 650 -910 {
lab=net1}
N 810 -760 930 -760 {
lab=IIN}
N 810 -760 810 -700 {
lab=IIN}
N 660 -700 810 -700 {
lab=IIN}
N 660 -760 660 -700 {
lab=IIN}
N 540 -760 660 -760 {
lab=IIN}
N 970 -760 1060 -760 {
lab=VDD}
N 970 -910 1070 -910 {
lab=VDD}
N 370 -910 450 -910 {
lab=VDD}
N 370 -760 450 -760 {
lab=VDD}
N 730 -910 790 -910 {
lab=VDD}
N 790 -960 790 -910 {
lab=VDD}
N 730 -760 790 -760 {
lab=VDD}
N 790 -810 790 -760 {
lab=VDD}
N 730 -1040 730 -940 {
lab=VDD}
N 970 -1040 970 -940 {
lab=VDD}
N 450 -1040 450 -940 {
lab=VDD}
N 970 -1040 1030 -1040 {
lab=VDD}
N 450 -1040 730 -1040 {
lab=VDD}
N 260 -1040 450 -1040 {
lab=VDD}
N 730 -1040 970 -1040 {
lab=VDD}
N 730 -730 730 -540 {
lab=net4}
N 640 -460 730 -460 {
lab=VSS}
N 730 -430 730 -290 {
lab=VSS}
N 390 -290 730 -290 {
lab=VSS}
N 790 -540 790 -460 {
lab=net4}
N 730 -540 730 -490 {
lab=net4}
N 880 -350 970 -350 {
lab=VSS}
N 880 -460 970 -460 {
lab=VSS}
N 970 -430 970 -380 {
lab=net6}
N 770 -460 790 -460 {
lab=net4}
N 730 -540 790 -540 {
lab=net4}
N 970 -730 970 -590 {
lab=net5}
N 970 -320 970 -290 {
lab=VSS}
N 730 -290 970 -290 {
lab=VSS}
N 1320 -350 1410 -350 {
lab=VSS}
N 1320 -460 1410 -460 {
lab=VSS}
N 1320 -430 1320 -380 {
lab=net7}
N 1320 -320 1320 -290 {
lab=VSS}
N 1320 -610 1320 -490 {
lab=IOUT}
N 970 -290 1320 -290 {
lab=VSS}
N 1320 -290 1490 -290 {
lab=VSS}
N 1030 -460 1280 -460 {
lab=net4}
N 1080 -350 1280 -350 {
lab=net5}
N 1080 -590 1080 -350 {
lab=net5}
N 1010 -350 1080 -350 {
lab=net5}
N 970 -590 1080 -590 {
lab=net5}
N 970 -590 970 -490 {
lab=net5}
N 790 -540 1030 -540 {
lab=net4}
N 1030 -540 1030 -460 {
lab=net4}
N 1010 -460 1030 -460 {
lab=net4}
N 450 -850 530 -850 {
lab=net1}
N 450 -850 450 -790 {
lab=net1}
N 530 -910 530 -850 {
lab=net1}
N 490 -910 530 -910 {
lab=net1}
N 450 -700 540 -700 {
lab=IIN}
N 450 -700 450 -650 {
lab=IIN}
N 540 -760 540 -700 {
lab=IIN}
N 490 -760 540 -760 {
lab=IIN}
C {devices/title.sym} 280 -160 0 0 {name=l1 author="Copyright 2026 MacAnalog Research Group"}
C {iopin.sym} 260 -1040 2 0 {name=p1 lab=VDD}
C {lab_pin.sym} 370 -910 2 1 {name=p2 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 370 -760 2 1 {name=p3 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 790 -810 2 1 {name=p4 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 790 -960 2 1 {name=p5 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1070 -910 2 0 {name=p6 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1060 -760 2 0 {name=p7 sig_type=std_logic lab=VDD}
C {iopin.sym} 450 -650 1 0 {name=p8 lab=IIN}
C {lab_pin.sym} 640 -460 2 1 {name=p9 sig_type=std_logic lab=VSS}
C {iopin.sym} 390 -290 2 0 {name=p10 lab=VSS}
C {lab_pin.sym} 880 -350 2 1 {name=p11 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 880 -460 2 1 {name=p12 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1410 -350 2 0 {name=p13 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 1410 -460 2 0 {name=p14 sig_type=std_logic lab=VSS}
C {iopin.sym} 1320 -610 3 0 {name=p15 lab=IOUT}
C {lab_pin.sym} 600 -910 1 1 {name=p16 sig_type=std_logic lab=net1}
C {lab_pin.sym} 730 -820 2 1 {name=p17 sig_type=std_logic lab=net2}
C {lab_pin.sym} 970 -820 2 1 {name=p18 sig_type=std_logic lab=net3}
C {lab_pin.sym} 730 -610 2 1 {name=p19 sig_type=std_logic lab=net4}
C {lab_pin.sym} 970 -610 2 1 {name=p20 sig_type=std_logic lab=net5}
C {lab_pin.sym} 970 -400 2 1 {name=p21 sig_type=std_logic lab=net6}
C {lab_pin.sym} 1320 -400 2 1 {name=p22 sig_type=std_logic lab=net7}
C {sg13g2_pr/sg13_lv_nmos.sym} 1300 -460 0 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 1300 -350 0 0 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 750 -460 0 1 {name=M3
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 990 -350 0 1 {name=M4
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 990 -460 0 1 {name=M5
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 950 -910 0 0 {name=M6
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 950 -760 0 0 {name=M7
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 710 -760 0 0 {name=M8
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 710 -910 0 0 {name=M9
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 470 -910 0 1 {name=M10
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 470 -760 0 1 {name=M11
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
