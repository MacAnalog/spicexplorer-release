v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 80 -170 120 -170 {
lab=VDD}
N 80 -130 120 -130 {
lab=VSS}
N 1060 -730 1060 -700 {
lab=VDD}
N 1090 -730 1090 -700 {
lab=VSS}
N 1120 -570 1225 -570 {
lab=voutn}
N 1120 -590 1222.5 -590 {
lab=voutp}
N 1222.5 -667.5 1222.5 -590 {
lab=voutp}
N 1232.5 -667.5 1392.5 -667.5 {
lab=voutp}
N 1225 -570 1225 -502.5 {
lab=voutn}
N 1225 -502.5 1387.5 -502.5 {
lab=voutn}
N 1045 -870 1232.5 -870 {
lab=voutp}
N 1042.5 -440 1222.5 -440 {
lab=voutn}
N 842.5 -1005 875 -1005 {
lab=#net1}
N 1047.5 -1070 1047.5 -1045 {
lab=voutp}
N 1047.5 -1070 1127.5 -1070 {
lab=voutp}
N 1127.5 -1070 1127.5 -1005 {
lab=voutp}
N 1077.5 -1005 1127.5 -1005 {
lab=voutp}
N 902.5 -1080 902.5 -1045 {
lab=#net1}
N 842.5 -1080 902.5 -1080 {
lab=#net1}
N 842.5 -1080 842.5 -1005 {
lab=#net1}
N 870 -305 902.5 -305 {
lab=#net2}
N 1075 -265 1075 -240 {
lab=voutn}
N 1075 -240 1155 -240 {
lab=voutn}
N 1155 -305 1155 -240 {
lab=voutn}
N 1105 -305 1155 -305 {
lab=voutn}
N 930 -265 930 -230 {
lab=#net2}
N 870 -230 930 -230 {
lab=#net2}
N 870 -305 870 -230 {
lab=#net2}
N 695 -305 870 -305 {
lab=#net2}
N 672.5 -720 672.5 -670 {
lab=#net1}
N 512.5 -720 672.5 -720 {
lab=#net1}
N 672.5 -650 672.5 -600 {
lab=#net2}
N 510 -600 672.5 -600 {
lab=#net2}
N 332.5 -720 455 -720 {
lab=vinp}
N 335 -600 450 -600 {
lab=vinn}
N 692.5 -670 820 -670 {
lab=#net1}
N 692.5 -870 985 -870 {
lab=#net1}
N 692.5 -1005 692.5 -870 {
lab=#net1}
N 692.5 -1005 842.5 -1005 {
lab=#net1}
N 692.5 -870 692.5 -670 {
lab=#net1}
N 672.5 -670 692.5 -670 {
lab=#net1}
N 1232.5 -870 1232.5 -667.5 {
lab=voutp}
N 1222.5 -667.5 1232.5 -667.5 {
lab=voutp}
N 1232.5 -1005 1232.5 -870 {
lab=voutp}
N 1127.5 -1005 1232.5 -1005 {
lab=voutp}
N 695 -440 695 -305 {
lab=#net2}
N 695 -650 820 -650 {
lab=#net2}
N 695 -440 982.5 -440 {
lab=#net2}
N 1222.5 -440 1222.5 -305 {
lab=voutn}
N 1155 -305 1222.5 -305 {
lab=voutn}
N 1222.5 -440 1225 -502.5 {
lab=voutn}
N 695 -650 695 -440 {
lab=#net2}
N 672.5 -650 695 -650 {
lab=#net2}
N 980 -1005 1017.5 -1005 {
lab=#net3}
N 1047.5 -1005 1047.5 -937.5 {
lab=#net3}
N 980 -937.5 1047.5 -937.5 {
lab=#net3}
N 980 -1005 980 -937.5 {
lab=#net3}
N 940 -1005 980 -1005 {
lab=#net3}
N 902.5 -1005 902.5 -937.5 {
lab=#net3}
N 902.5 -937.5 940 -937.5 {
lab=#net3}
N 940 -1005 940 -937.5 {
lab=#net3}
N 932.5 -1005 940 -1005 {
lab=#net3}
N 930 -372.5 930 -305 {
lab=#net4}
N 930 -372.5 960 -372.5 {
lab=#net4}
N 960 -372.5 960 -305 {
lab=#net4}
N 960 -305 1045 -305 {
lab=#net4}
N 1075 -370 1075 -305 {
lab=#net4}
N 1042.5 -370 1075 -370 {
lab=#net4}
N 1042.5 -370 1045 -305 {
lab=#net4}
C {devices/title.sym} 160 -50 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {iopin.sym} 80 -170 0 1 {name=p4 lab=VDD}
C {iopin.sym} 80 -130 0 1 {name=p1 lab=VSS}
C {shared/ideal/ideal-amp-fully-diff.sym} 840 -540 0 0 {name=x_amp_1}
C {lab_pin.sym} 1060 -730 0 0 {name=p2 sig_type=std_logic lab=VDD}
C {lab_pin.sym} 1090 -730 0 1 {name=p3 sig_type=std_logic lab=VSS}
C {capa.sym} 1015 -870 1 0 {name=Cf1
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 1012.5 -440 1 0 {name=Cf2
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {sg13g2_pr/sg13_lv_pmos.sym} 1047.5 -1025 3 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 902.5 -1025 1 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 1075 -285 3 0 {name=M3
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 930 -285 1 1 {name=M4
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {ipin.sym} 335 -600 0 0 {name=p29 lab=vinn}
C {ipin.sym} 332.5 -720 0 0 {name=p30 lab=vinp}
C {opin.sym} 1392.5 -667.5 0 0 {name=p31 lab=voutp}
C {opin.sym} 1387.5 -502.5 0 0 {name=p32 lab=voutn}
C {capa.sym} 485 -720 1 0 {name=Cf3
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {capa.sym} 480 -600 1 0 {name=Cf4
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
