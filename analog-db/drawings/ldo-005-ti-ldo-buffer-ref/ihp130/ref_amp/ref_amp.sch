v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 640 -600 640 -520 {lab=vc}
N 340 -660 340 -520 {lab=vb}
N 460 -720 600 -720 {lab=vb}
N 840 -600 980 -600 {lab=vc}
N 640 -460 640 -420 {lab=va}
N 480 -420 640 -420 {lab=va}
N 340 -460 340 -420 {lab=va}
N 340 -760 340 -750 {lab=vdd}
N 640 -760 640 -750 {lab=vdd}
N 1020 -660 1020 -630 {lab=vdd}
N 1020 -600 1100 -600 {lab=vdd}
N 1100 -660 1100 -600 {lab=vdd}
N 1020 -660 1100 -660 {lab=vdd}
N 250 -490 300 -490 {lab=vinn}
N 680 -490 720 -490 {lab=vinp}
N 840 -520 870 -520 {lab=vc}
N 840 -600 840 -520 {lab=vc}
N 930 -520 960 -520 {lab=#net1}
N 960 -520 960 -480 {lab=#net1}
N 1020 -540 1020 -380 {lab=vout}
N 960 -380 1020 -380 {lab=vout}
N 960 -420 960 -380 {lab=vout}
N 640 -720 720 -720 {lab=vdd}
N 720 -760 720 -720 {lab=vdd}
N 640 -760 720 -760 {lab=vdd}
N 260 -720 340 -720 {lab=vdd}
N 260 -760 260 -720 {lab=vdd}
N 260 -760 340 -760 {lab=vdd}
N 1020 -380 1020 -360 {lab=vout}
N 480 -420 480 -360 {lab=va}
N 340 -490 640 -490 {lab=vss}
N 100 -800 100 -780 {lab=vdd}
N 60 -800 60 -780 {lab=vss}
N 1020 -540 1160 -540 {lab=vout}
N 460 -720 460 -660 {lab=vb}
N 340 -660 460 -660 {lab=vb}
N 900 -580 900 -540 {lab=vdd}
N 60 -410 60 -360 {lab=#net2}
N 60 -410 150 -410 {lab=#net2}
N 150 -380 150 -330 {lab=#net2}
N 100 -330 150 -330 {lab=#net2}
N 150 -330 440 -330 {lab=#net2}
N 480 -280 480 -260 {lab=vss}
N 1020 -280 1020 -260 {lab=vss}
N 60 -280 60 -260 {lab=vss}
N -30 -330 60 -330 {lab=vss}
N -30 -330 -30 -280 {lab=vss}
N -30 -280 60 -280 {lab=vss}
N 480 -330 580 -330 {lab=vss}
N 580 -330 580 -280 {lab=vss}
N 480 -280 580 -280 {lab=vss}
N 760 -330 980 -330 {lab=#net2}
N 760 -380 760 -330 {lab=#net2}
N 150 -380 760 -380 {lab=#net2}
N 1020 -330 1120 -330 {lab=vss}
N 1120 -330 1120 -280 {lab=vss}
N 1020 -280 1120 -280 {lab=vss}
N 60 -660 60 -620 {lab=vdd}
N 640 -690 640 -600 {lab=vc}
N 1020 -780 1020 -660 {lab=vdd}
N 640 -600 840 -600 {lab=vc}
N 640 -780 640 -760 {lab=vdd}
N 340 -780 340 -760 {lab=vdd}
N 340 -420 480 -420 {lab=va}
N 1020 -570 1020 -540 {lab=vout}
N 380 -720 460 -720 {lab=vb}
N 340 -690 340 -660 {lab=vb}
N 60 -560 60 -410 {lab=#net2}
N 60 -300 60 -280 {lab=vss}
N 480 -300 480 -280 {lab=vss}
N 150 -410 150 -380 {lab=#net2}
N 1020 -300 1020 -280 {lab=vss}
N 100 -590 170 -590 {lab=#net2}
N -10 -590 60 -590 {lab=vdd}
N 170 -590 170 -530 {
lab=#net2}
N 60 -530 170 -530 {
lab=#net2}
C {devices/title.sym} 160 -40 0 0 {name=l1 author="Danial Noori Zadeh"}
C {sg13g2_pr/sg13_hv_nmos.sym} 320 -490 0 0 {name=M1
l=0.7u
w=86.42u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 660 -490 0 1 {name=M2
l=0.7u
w=86.42u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 360 -720 0 1 {name=M3
l=1u
w=20u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 620 -720 0 0 {name=M4
l=1u
w=20u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_pmos.sym} 1000 -600 0 0 {name=M5
l=2.646u
w=37.76u
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
value=4.508p
footprint=1206
device="ceramic capacitor"}
C {devices/iopin.sym} 60 -800 3 0 {name=vss lab=vss}
C {devices/lab_pin.sym} 340 -780 0 0 {name=p4 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 640 -780 0 0 {name=p5 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 1020 -780 0 0 {name=p6 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 100 -780 3 0 {name=p7 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 480 -260 0 0 {name=p8 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 1020 -260 0 0 {name=p9 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 480 -490 1 0 {name=p10 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 60 -780 3 0 {name=p11 sig_type=std_logic lab=vss}
C {devices/opin.sym} 1160 -540 2 1 {name=p12 lab=vout}
C {sg13g2_pr/rhigh.sym} 900 -520 1 0 {name=R1
w=1u
l=20.3644u
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
C {devices/lab_pin.sym} 60 -260 0 0 {name=p17 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 60 -660 3 1 {name=p18 sig_type=std_logic lab=vdd}
C {sg13g2_pr/sg13_hv_nmos.sym} 460 -330 0 0 {name=M_mirror_a
l=2u
w=8.316u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 1000 -330 0 0 {name=M_mirror_out
l=2u
w=4u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {sg13g2_pr/sg13_hv_nmos.sym} 80 -330 0 1 {name=M_mirror_ref
l=2u
w=12u
ng=1
m=1
model=sg13_hv_nmos
spiceprefix=X
}
C {devices/ngspice_get_expr.sym} 660 -160 2 0 {name=r2 
node="[format %.2g [expr [ngspice::get_node \{@m.x_ref_amp.xm2.m0[gm]\}] / [ngspice::get_node \{i(@m.x_ref_amp.xm2.m0[id])\}]]]"
descr="gm2/id2="}
C {devices/ngspice_get_expr.sym} 720 -160 2 0 {name=r3 
node="[format %.2g [expr 1e3*[ngspice::get_node \{@m.x_ref_amp.xm2.m0[gm]\}]]]"
descr="gm="}
C {devices/ngspice_get_expr.sym} 780 -160 2 0 {name=r4 
node="[format %.2g [expr 1e6*[ngspice::get_node \{i(@m.x_ref_amp.xm2.m0[id])\}]]]"
descr="id2="}
C {devices/ngspice_get_expr.sym} 990 -240 2 0 {name=r11 
node="[format %.2g [expr [ngspice::get_node \{@m.x_ref_amp.xm_mirror_out.m0[gm]\}] / [ngspice::get_node \{i(@m.x_ref_amp.xm_mirror_out.m0[id])\}]]]"
descr="gm/id="}
C {devices/ngspice_get_expr.sym} 1050 -240 2 0 {name=r12 
node="[format %.2g [expr 1e3*[ngspice::get_node \{@m.x_ref_amp.xm_mirror_out.m0[gm]\}]]]"
descr="gm="}
C {devices/ngspice_get_expr.sym} 1110 -240 2 0 {name=r13 
node="[format %.2g [expr 1e6*[ngspice::get_node \{i(@m.x_ref_amp.xm_mirror_out.m0[id])\}]]]"
descr="id_out="}
C {devices/ngspice_get_expr.sym} 660 -120 2 0 {name=r14 
node="[format %.2g [expr [ngspice::get_node \{@m.x_ref_amp.xm1.m0[gm]\}] / [ngspice::get_node \{i(@m.x_ref_amp.xm1.m0[id])\}]]]"
descr="gm1/id1="}
C {devices/ngspice_get_expr.sym} 720 -120 2 0 {name=r15 
node="[format %.2g [expr 1e3*[ngspice::get_node \{@m.x_ref_amp.xm1.m0[gm]\}]]]"
descr="gm="}
C {devices/ngspice_get_expr.sym} 780 -120 2 0 {name=r16 
node="[format %.2g [expr 1e6*[ngspice::get_node \{i(@m.x_ref_amp.xm1.m0[id])\}]]]"
descr="id1="}
C {devices/ngspice_get_expr.sym} 660 -220 2 0 {name=r17 
node="[format %.2g [expr [ngspice::get_node \{@m.x_ref_amp.xm3.m0[gm]\}] / [ngspice::get_node \{i(@m.x_ref_amp.xm3.m0[id])\}]]]"
descr="gm3/id3="}
C {devices/ngspice_get_expr.sym} 720 -220 2 0 {name=r18 
node="[format %.2g [expr 1e3*[ngspice::get_node \{@m.x_ref_amp.xm3.m0[gm]\}]]]"
descr="gm="}
C {devices/ngspice_get_expr.sym} 780 -220 2 0 {name=r19 
node="[format %.2g [expr 1e6*[ngspice::get_node \{i(@m.x_ref_amp.xm3.m0[id])\}]]]"
descr="id3="}
C {devices/ngspice_get_expr.sym} 980 -180 2 0 {name=r20 
node="[format %.2g [expr [ngspice::get_node \{@m.x_ref_amp.xm5.m0[gm]\}] / [ngspice::get_node \{i(@m.x_ref_amp.xm5.m0[id])\}]]]"
descr="gm5/id5="}
C {devices/ngspice_get_expr.sym} 1040 -180 2 0 {name=r21 
node="[format %.2g [expr 1e3*[ngspice::get_node \{@m.x_ref_amp.xm5.m0[gm]\}]]]"
descr="gm="}
C {devices/ngspice_get_expr.sym} 1100 -180 2 0 {name=r22 
node="[format %.2g [expr 1e6*[ngspice::get_node \{i(@m.x_ref_amp.xm5.m0[id])\}]]]"
descr="id5="}
C {devices/ngspice_get_expr.sym} 660 -260 2 0 {name=r23 
node="[format %.2g [expr [ngspice::get_node \{@m.x_ref_amp.xm4.m0[gm]\}] / [ngspice::get_node \{i(@m.x_ref_amp.xm4.m0[id])\}]]]"
descr="gm4/id4="}
C {devices/ngspice_get_expr.sym} 720 -260 2 0 {name=r24 
node="[format %.2g [expr 1e3*[ngspice::get_node \{@m.x_ref_amp.xm4.m0[gm]\}]]]"
descr="gm="}
C {devices/ngspice_get_expr.sym} 780 -260 2 0 {name=r25 
node="[format %.2g [expr 1e6*[ngspice::get_node \{i(@m.x_ref_amp.xm4.m0[id])\}]]]"
descr="id4="}
C {devices/ngspice_get_expr.sym} 440 -240 2 0 {name=r5 
node="[format %.2g [expr [ngspice::get_node \{@m.x_ref_amp.xm_mirror_a.m0[gm]\}] / [ngspice::get_node \{i(@m.x_ref_amp.xm_mirror_a.m0[id])\}]]]"
descr="gm/id="}
C {devices/ngspice_get_expr.sym} 500 -240 2 0 {name=r6 
node="[format %.2g [expr 1e3*[ngspice::get_node \{@m.x_ref_amp.xm_mirror_a.m0[gm]\}]]]"
descr="gm="}
C {devices/ngspice_get_expr.sym} 560 -240 2 0 {name=r7 
node="[format %.2g [expr 1e6*[ngspice::get_node \{i(@m.x_ref_amp.xm_mirror_a.m0[id])\}]]]"
descr="id="}
C {devices/ngspice_get_expr.sym} 60 -240 2 0 {name=r8 
node="[format %.2g [expr [ngspice::get_node \{@m.x_ref_amp.xm_mirror_a.m0[gm]\}] / [ngspice::get_node \{i(@m.x_ref_amp.xm_mirror_ref.m0[id])\}]]]"
descr="gm/id="}
C {devices/ngspice_get_expr.sym} 100 -240 2 0 {name=r9 
node="[format %.2g [expr 1e3*[ngspice::get_node \{@m.x_ref_amp.xm_mirror_ref.m0[gm]\}]]]"
descr="gm="}
C {devices/ngspice_get_expr.sym} 160 -240 2 0 {name=r10 
node="[format %.2g [expr 1e6*[ngspice::get_node \{i(@m.x_ref_amp.xm_mirror_ref.m0[id])\}]]]"
descr="id="}
C {sg13g2_pr/sg13_hv_pmos.sym} 80 -590 0 1 {name=M_bias
l=2u
w=10.844u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} -10 -590 0 0 {name=p31 sig_type=std_logic lab=vdd}
