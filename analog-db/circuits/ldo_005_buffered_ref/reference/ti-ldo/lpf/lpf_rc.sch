v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {Simple RC Low-pass Filter} 310 -570 0 0 0.5 0.5 {}
N 343.75 -341.25 448.75 -341.25 {lab=VIN}
N 117.5 -457.5 117.5 -437.5 {lab=vdd}
N 77.5 -457.5 77.5 -437.5 {lab=vss}
N 580 -257.5 580 -237.5 {lab=vss}
N 508.75 -341.25 586.25 -343.75 {lab=VOUT}
N 585 -365 586.25 -343.75 {lab=VOUT}
N 580 -317.5 586.25 -343.75 {lab=VOUT}
N 478.75 -385 478.75 -361.25 {lab=vdd}
C {devices/ipin.sym} 343.75 -341.25 0 0 {name=p2 lab=VIN}
C {devices/title.sym} 172.5 -35 0 0 {name=l1 author="Danial Noori Zadeh"}
C {symbols/ppolyf_u_3k.sym} 478.75 -341.25 1 0 {name=R1
W=\{R_lpf_r1_w\}
L=\{R_lpf_r1_l\}
model=ppolyf_u_3k
spiceprefix=X
m=1}
C {devices/lab_pin.sym} 478.75 -385 1 0 {name=p6 sig_type=std_logic lab=vdd}
C {devices/iopin.sym} 117.5 -457.5 1 1 {name=p3 lab=vdd}
C {devices/iopin.sym} 77.5 -457.5 3 0 {name=vss lab=vss}
C {devices/lab_pin.sym} 117.5 -437.5 3 0 {name=p7 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 77.5 -437.5 3 0 {name=p11 sig_type=std_logic lab=vss}
C {devices/capa.sym} 580 -287.5 0 0 {name=C1
m=1
value=\{C_lpf_c1\}
footprint=1206
device="ceramic capacitor"}
C {devices/lab_pin.sym} 580 -237.5 3 0 {name=p1 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 382.5 -340 3 0 {name=p4 sig_type=std_logic lab=VIN}
C {devices/opin.sym} 586.25 -343.75 2 1 {name=p5 lab=VOUT}
C {devices/lab_pin.sym} 585 -365 0 0 {name=p8 sig_type=std_logic lab=VOUT}
C {devices/code_shown.sym} 725 -550 0 0 {name=params only_toplevel=true
format="tcleval( @value )"
value="
** LPF Network Parameters
.param C_lpf_c1 	= 100p
.param R_lpf_r1_w	= 1e-6
.param R_lpf_r1_l	= 1e-6

"}
