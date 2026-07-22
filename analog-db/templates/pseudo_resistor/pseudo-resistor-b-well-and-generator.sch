v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 580 -380 730 -380 {}
N 440 -340 440 -290 {}
N 730 -340 730 -290 {}
N 270 -380 410 -380 {}
N 580 -290 730 -290 {}
N 580 -380 580 -290 {}
N 440 -380 580 -380 {}
N 440 -290 580 -290 {}
N 760 -380 880 -380 {}
C {title.sym} 190 -50 0 0 {name=l1 author="Stefan Schippers"}
C {ipin.sym} 270 -380 0 0 {name=p1 lab=port_A}
C {ipin.sym} 880 -380 0 1 {name=p2 lab=port_B}
C {sg13g2_pr/sg13_lv_pmos.sym} 730 -360 3 0 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 440 -360 1 1 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
