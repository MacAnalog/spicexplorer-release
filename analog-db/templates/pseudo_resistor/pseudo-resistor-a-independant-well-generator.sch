v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 840 -380 880 -380 {
lab=#net1}
N 400 -380 510 -380 {}
N 510 -340 510 -290 {}
N 400 -290 510 -290 {}
N 400 -380 400 -290 {}
N 270 -380 400 -380 {}
N 750 -340 750 -290 {}
N 750 -290 840 -290 {}
N 840 -380 840 -290 {}
N 750 -380 840 -380 {
lab=#net1}
N 540 -380 720 -380 {}
C {devices/title.sym} 190 -50 0 0 {name=l1 author="Copyright 2026 MacAnalog Research Group"}
C {ipin.sym} 270 -380 0 0 {name=p1 lab=port_A}
C {ipin.sym} 880 -380 0 1 {name=p2 lab=port_B}
C {sg13g2_pr/sg13_lv_pmos.sym} 750 -360 1 1 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 510 -360 3 0 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
