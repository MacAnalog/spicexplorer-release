v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 280 -360 470 -360 {}
N 610 -360 720 -360 {}
N 750 -360 900 -360 {}
N 470 -320 470 -260 {}
N 610 -260 750 -260 {}
N 750 -320 750 -260 {}
N 610 -360 610 -260 {}
N 500 -360 610 -360 {}
N 470 -260 610 -260 {}
C {title.sym} 200 -40 0 0 {name=l1 author="Stefan Schippers"}
C {ipin.sym} 280 -360 0 0 {name=p1 lab=port_A}
C {ipin.sym} 900 -360 0 1 {name=p2 lab=port_B}
C {sg13g2_pr/sg13_lv_pmos.sym} 750 -340 1 1 {name=M1
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_lv_pmos.sym} 470 -340 3 0 {name=M2
l=0.13u
w=0.15u
ng=1
m=1
model=sg13_lv_pmos
spiceprefix=X
}
