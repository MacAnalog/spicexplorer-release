v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 640 -690 640 -520 {lab=vc}
N 340 -690 340 -520 {lab=vb}
N 380 -720 600 -720 {lab=vb}
N 640 -600 980 -600 {lab=vc}
N 640 -460 640 -420 {lab=va}
N 340 -420 640 -420 {lab=va}
N 340 -460 340 -420 {lab=va}
N 340 -780 340 -750 {lab=vdd}
N 640 -780 640 -750 {lab=vdd}
N 1020 -780 1020 -630 {lab=vdd}
N 1020 -600 1100 -600 {lab=vdd}
N 1100 -660 1100 -600 {lab=vdd}
N 1020 -660 1100 -660 {lab=vdd}
N 250 -490 300 -490 {lab=vinn}
N 680 -490 720 -490 {lab=vinp}
N 840 -520 870 -520 {lab=vc}
N 840 -600 840 -520 {lab=vc}
N 930 -520 960 -520 {lab=#net1}
N 960 -520 960 -480 {lab=#net1}
N 1020 -570 1020 -380 {lab=vout}
N 960 -380 1020 -380 {lab=vout}
N 960 -420 960 -380 {lab=vout}
N 640 -720 720 -720 {lab=vdd}
N 720 -760 720 -720 {lab=vdd}
N 640 -760 720 -760 {lab=vdd}
N 260 -720 340 -720 {lab=vdd}
N 260 -760 260 -720 {lab=vdd}
N 260 -760 340 -760 {lab=vdd}
N 1020 -380 1020 -360 {lab=vout}
N 1020 -300 1020 -260 {lab=vss}
N 340 -490 480 -490 {lab=vss}
N 480 -490 640 -490 {lab=vss}
N 100 -800 100 -780 {lab=vdd}
N 60 -800 60 -780 {lab=vss}
N 1020 -540 1160 -540 {lab=vout}
N 460 -720 460 -660 {lab=vb}
N 340 -660 460 -660 {lab=vb}
N 900 -580 900 -540 {lab=vdd}
N 1020 -330 1140 -330 {lab=vss}
N 160 -310 440 -310 {lab=#net2}
N 20 -310 120 -310 {lab=vss}
N 480 -310 540 -310 {lab=vss}
N 480 -420 480 -340 {lab=va}
N 480 -280 480 -220 {lab=vss}
N 120 -280 120 -220 {lab=vss}
N 300 -350 300 -310 {lab=#net2}
N 300 -350 950 -350 {lab=#net2}
N 950 -350 950 -330 {lab=#net2}
N 950 -330 980 -330 {lab=#net2}
N 220 -370 220 -310 {lab=#net2}
N 120 -370 220 -370 {lab=#net2}
N 120 -610 220 -610 {lab=vdd}
N 120 -690 120 -640 {lab=vdd}
N 120 -580 120 -370 {lab=#net2}
N 120 -370 120 -340 {lab=#net2}
N 40 -610 80 -610 {lab=#net2}
N 40 -610 40 -550 {lab=#net2}
N 40 -550 120 -550 {lab=#net2}
C {devices/title.sym} 160 -40 0 0 {name=l1 author="Danial Noori Zadeh"}
C {sg13g2_pr/sg13_hv_nmos.sym} 320 -490 0 0 {name=M1
l=0.70u
w=0.30u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 660 -490 0 1 {name=M2
l=0.70u
w=0.30u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 360 -720 0 1 {name=M3
l=0.50u
w=0.30u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 620 -720 0 0 {name=M4
l=0.50u
w=0.30u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 1000 -600 0 0 {name=M5
l=0.50u
w=0.30u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {devices/ipin.sym} 250 -490 0 0 {name=p1 lab=vinn}
C {devices/ipin.sym} 720 -490 0 1 {name=p2 lab=vinp}
C {devices/iopin.sym} 100 -800 1 1 {name=p3 lab=vdd}
C {devices/capa.sym} 960 -450 0 1 {name=C1
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {devices/iopin.sym} 60 -800 3 0 {name=vss lab=vss}
C {devices/lab_pin.sym} 340 -780 0 0 {name=p4 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 640 -780 0 0 {name=p5 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 1020 -780 0 0 {name=p6 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 100 -780 3 0 {name=p7 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 480 -220 0 0 {name=p8 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 1020 -260 0 0 {name=p9 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 480 -490 1 0 {name=p10 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 60 -780 3 0 {name=p11 sig_type=std_logic lab=vss}
C {devices/opin.sym} 1160 -540 2 1 {name=p12 lab=vout}
C {sg13g2_pr/rhigh.sym} 900 -520 1 0 {name=R1
w=1e-6
l=1.9802u
model=rhigh
spiceprefix=X
m=1
body=sub!
b=0
}
C {devices/lab_pin.sym} 900 -580 0 0 {name=p13 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 480 -420 1 0 {name=p14 sig_type=std_logic lab=va}
C {devices/lab_pin.sym} 340 -610 2 1 {name=p15 sig_type=std_logic lab=vb}
C {devices/lab_pin.sym} 640 -620 2 1 {name=p16 sig_type=std_logic lab=vc}
C {sg13g2_pr/sg13_hv_nmos.sym} 1000 -330 0 0 {name=M6
l=0.70u
w=0.30u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 1140 -330 1 0 {name=p17 sig_type=std_logic lab=vss}
C {sg13g2_pr/sg13_hv_nmos.sym} 460 -310 0 0 {name=M7
l=0.70u
w=0.30u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 140 -310 0 1 {name=M8
l=0.70u
w=0.30u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 20 -310 0 0 {name=p18 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 540 -310 0 1 {name=p19 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 120 -220 0 0 {name=p20 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 120 -690 1 0 {name=p21 sig_type=std_logic lab=vdd}
C {sg13g2_pr/sg13_hv_pmos.sym} 100 -610 0 0 {name=M9
l=0.50u
w=0.30u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 220 -610 2 0 {name=p22 sig_type=std_logic lab=vdd}
