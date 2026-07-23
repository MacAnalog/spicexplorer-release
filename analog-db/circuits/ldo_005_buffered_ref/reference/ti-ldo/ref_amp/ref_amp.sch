v {xschem version=3.4.7 file_version=1.2}
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
N 250 -490 300 -490 {lab=vin_n}
N 680 -490 720 -490 {lab=vin_p}
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
N 480 -420 480 -360 {lab=va}
N 340 -490 480 -490 {lab=vss}
N 480 -490 640 -490 {lab=vss}
N 100 -800 100 -780 {lab=vdd}
N 60 -800 60 -780 {lab=vss}
N 1020 -540 1160 -540 {lab=vout}
N 460 -720 460 -660 {lab=vb}
N 340 -660 460 -660 {lab=vb}
N 900 -580 900 -540 {lab=vdd}
N 60 -560 60 -360 {lab=#net2}
N 60 -410 150 -410 {lab=#net2}
N 150 -410 150 -330 {lab=#net2}
N 100 -330 150 -330 {lab=#net2}
N 150 -330 440 -330 {lab=#net2}
N 480 -300 480 -260 {lab=vss}
N 1020 -300 1020 -260 {lab=vss}
N 60 -300 60 -260 {lab=vss}
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
C {devices/title.sym} 160 -40 0 0 {name=l1 author="Danial Noori Zadeh"}
C {symbols/nfet_06v0.sym} 320 -490 0 0 {name=M1

L=\{M1_ref_amp_nfet_l\}
W=\{M1_ref_amp_nfet_w\}
nf=1
m=\{M1_ref_amp_nfet_m\}

ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_06v0
spiceprefix=X
}
C {symbols/nfet_06v0.sym} 660 -490 0 1 {name=M2
L=\{M2_ref_amp_nfet_l\}
W=\{M2_ref_amp_nfet_w\}
nf=1
m=\{M2_ref_amp_nfet_m\}
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_06v0
spiceprefix=X
}
C {symbols/pfet_06v0.sym} 360 -720 0 1 {name=M3

L=\{M3_ref_amp_pfet_l\}
W=\{M3_ref_amp_pfet_w\}
nf=1
m=\{M3_ref_amp_pfet_m\}

ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_06v0
spiceprefix=X
}
C {symbols/pfet_06v0.sym} 620 -720 0 0 {name=M4

L=\{M4_ref_amp_pfet_l\}
W=\{M4_ref_amp_pfet_w\}
nf=1
m=\{M4_ref_amp_pfet_m\}

ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_06v0
spiceprefix=X
}
C {symbols/pfet_06v0.sym} 1000 -600 0 0 {name=M5

L=\{M5_ref_amp_pfet_l\}
W=\{M5_ref_amp_pfet_w\}
nf=1
m=\{M5_ref_amp_pfet_m\}

ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_06v0
spiceprefix=X
}
C {devices/ipin.sym} 250 -490 0 0 {name=p1 lab=vin_n}
C {devices/ipin.sym} 720 -490 0 1 {name=p2 lab=vin_p}
C {devices/iopin.sym} 100 -800 1 1 {name=p3 lab=vdd}
C {devices/capa.sym} 960 -450 0 1 {name=C1
m=1
value=\{C_ref_amp_c1\}
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
C {symbols/ppolyf_u_3k.sym} 900 -520 1 0 {name=R1
W=\{R_ref_amp_r1_w\}
L=\{R_ref_amp_r1_l\}
model=ppolyf_u_3k
spiceprefix=X
m=1}
C {devices/lab_pin.sym} 900 -580 0 0 {name=p13 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 480 -420 1 0 {name=p14 sig_type=std_logic lab=va}
C {devices/lab_pin.sym} 340 -610 2 1 {name=p15 sig_type=std_logic lab=vb}
C {devices/lab_pin.sym} 640 -620 2 1 {name=p16 sig_type=std_logic lab=vc}
C {devices/isource.sym} 60 -590 0 0 {name=I_ref_amp_ref value=1u}
C {devices/lab_pin.sym} 60 -260 0 0 {name=p17 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 60 -660 3 1 {name=p18 sig_type=std_logic lab=vdd}
C {symbols/nfet_06v0.sym} 460 -330 0 0 {name=M_mirror_a

L=\{M_mirror_a_ref_amp_nfet_l\}
W=\{M_mirror_a_ref_amp_nfet_w\}
nf=2
m=\{M_mirror_a_ref_amp_nfet_m\}

ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_06v0
spiceprefix=X
}
C {symbols/nfet_06v0.sym} 1000 -330 0 0 {name=M_mirror_out

L=\{M_mirror_out_ref_amp_nfet_l\}
W=\{M_mirror_out_ref_amp_nfet_w\}
nf=1
m=\{M_mirror_out_ref_amp_nfet_m\}

ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_06v0
spiceprefix=X
}
C {symbols/nfet_06v0.sym} 80 -330 0 1 {name=M_mirror_ref
L=\{M_mirror_ref_ref_amp_nfet_l\}
W=\{M_mirror_ref_ref_amp_nfet_w\}
nf=1
m=\{M_mirror_ref_ref_amp_nfet_m\}
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=nfet_06v0
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
