v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 300 -340 300 -310 {
lab=net1}
N 300 -490 300 -460 {
lab=IIN}
N 580 -400 580 -310 {
lab=net2}
N 820 -400 820 -310 {
lab=net3}
N 510 -430 540 -430 {
lab=IIN}
N 500 -280 540 -280 {
lab=net1}
N 680 -280 780 -280 {
lab=net1}
N 680 -340 680 -280 {
lab=net1}
N 500 -340 680 -340 {
lab=net1}
N 500 -340 500 -280 {
lab=net1}
N 380 -280 500 -280 {
lab=net1}
N 660 -430 780 -430 {
lab=IIN}
N 660 -490 660 -430 {
lab=IIN}
N 510 -490 660 -490 {
lab=IIN}
N 510 -490 510 -430 {
lab=IIN}
N 390 -430 510 -430 {
lab=IIN}
N 820 -430 910 -430 {
lab=VSS}
N 820 -280 920 -280 {
lab=VSS}
N 220 -280 300 -280 {
lab=VSS}
N 220 -430 300 -430 {
lab=VSS}
N 580 -280 640 -280 {
lab=VSS}
N 640 -280 640 -230 {
lab=VSS}
N 580 -430 640 -430 {
lab=VSS}
N 640 -430 640 -380 {
lab=VSS}
N 580 -250 580 -150 {
lab=VSS}
N 820 -250 820 -150 {
lab=VSS}
N 300 -250 300 -150 {
lab=VSS}
N 820 -150 880 -150 {
lab=VSS}
N 300 -150 580 -150 {
lab=VSS}
N 110 -150 300 -150 {
lab=VSS}
N 580 -150 820 -150 {
lab=VSS}
N 580 -650 580 -460 {
lab=net4}
N 490 -730 580 -730 {
lab=VDD}
N 580 -900 580 -760 {
lab=VDD}
N 240 -900 580 -900 {
lab=VDD}
N 640 -730 640 -650 {
lab=net4}
N 580 -700 580 -650 {
lab=net4}
N 730 -840 820 -840 {
lab=VDD}
N 730 -730 820 -730 {
lab=VDD}
N 820 -810 820 -760 {
lab=net6}
N 620 -730 640 -730 {
lab=net4}
N 580 -650 640 -650 {
lab=net4}
N 820 -600 820 -460 {
lab=net5}
N 820 -900 820 -870 {
lab=VDD}
N 580 -900 820 -900 {
lab=VDD}
N 1170 -840 1260 -840 {
lab=VDD}
N 1170 -730 1260 -730 {
lab=VDD}
N 1170 -810 1170 -760 {
lab=net7}
N 1170 -900 1170 -870 {
lab=VDD}
N 1170 -700 1170 -580 {
lab=IOUT}
N 820 -900 1170 -900 {
lab=VDD}
N 1170 -900 1340 -900 {
lab=VDD}
N 880 -730 1130 -730 {
lab=net4}
N 930 -840 1130 -840 {
lab=net5}
N 930 -840 930 -600 {
lab=net5}
N 860 -840 930 -840 {
lab=net5}
N 820 -600 930 -600 {
lab=net5}
N 820 -700 820 -600 {
lab=net5}
N 640 -650 880 -650 {
lab=net4}
N 880 -730 880 -650 {
lab=net4}
N 860 -730 880 -730 {
lab=net4}
N 300 -340 380 -340 {
lab=net1}
N 300 -400 300 -340 {
lab=net1}
N 380 -340 380 -280 {
lab=net1}
N 340 -280 380 -280 {
lab=net1}
N 300 -490 390 -490 {
lab=IIN}
N 300 -540 300 -490 {
lab=IIN}
N 390 -490 390 -430 {
lab=IIN}
N 340 -430 390 -430 {
lab=IIN}
C {devices/title.sym} 170 -40 0 0 {name=l1 author="Copyright 2026 MacAnalog Research Group"}
C {sg13g2_pr/sg13_lv_nmos.sym} 320 -430 0 1 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 320 -280 0 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 560 -430 0 0 {name=M3
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 560 -280 0 0 {name=M4
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 800 -430 0 0 {name=M5
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_nmos.sym} 800 -280 0 0 {name=M6
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_nmos
spiceprefix=X
}
C {iopin.sym} 110 -150 0 1 {name=p1 lab=VSS}
C {lab_pin.sym} 220 -280 0 0 {name=p2 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 220 -430 0 0 {name=p3 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 640 -380 0 0 {name=p4 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 640 -230 0 0 {name=p5 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 920 -280 0 1 {name=p6 sig_type=std_logic lab=VSS}
C {lab_pin.sym} 910 -430 0 1 {name=p7 sig_type=std_logic lab=VSS}
C {iopin.sym} 300 -540 1 1 {name=p8 lab=IIN}
C {sg13g2_pr/sg13_lv_pmos.sym} 600 -730 0 1 {name=M7
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 490 -730 0 0 {name=p9 sig_type=std_logic lab=VDD}
C {iopin.sym} 240 -900 0 1 {name=p10 lab=VDD}
C {sg13g2_pr/sg13_lv_pmos.sym} 840 -840 0 1 {name=M8
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 730 -840 0 0 {name=p11 sig_type=std_logic lab=VDD}
C {sg13g2_pr/sg13_lv_pmos.sym} 840 -730 0 1 {name=M9
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 730 -730 0 0 {name=p12 sig_type=std_logic lab=VDD}
C {sg13g2_pr/sg13_lv_pmos.sym} 1150 -840 0 0 {name=M10
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 1260 -840 0 1 {name=p13 sig_type=std_logic lab=VDD}
C {sg13g2_pr/sg13_lv_pmos.sym} 1150 -730 0 0 {name=M11
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {lab_pin.sym} 1260 -730 0 1 {name=p14 sig_type=std_logic lab=VDD}
C {iopin.sym} 1170 -580 3 1 {name=p15 lab=IOUT}
C {lab_pin.sym} 450 -280 1 0 {name=p16 sig_type=std_logic lab=net1}
C {lab_pin.sym} 580 -370 0 0 {name=p17 sig_type=std_logic lab=net2}
C {lab_pin.sym} 820 -370 0 0 {name=p18 sig_type=std_logic lab=net3}
C {lab_pin.sym} 580 -580 0 0 {name=p19 sig_type=std_logic lab=net4}
C {lab_pin.sym} 820 -580 0 0 {name=p20 sig_type=std_logic lab=net5}
C {lab_pin.sym} 820 -790 0 0 {name=p21 sig_type=std_logic lab=net6}
C {lab_pin.sym} 1170 -790 0 0 {name=p22 sig_type=std_logic lab=net7}
