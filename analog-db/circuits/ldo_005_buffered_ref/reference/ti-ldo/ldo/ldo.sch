v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 130 -633.75 220 -633.75 {lab=VREF}
N 90 -807.5 90 -787.5 {lab=vdd}
N 50 -807.5 50 -787.5 {lab=vss}
N 308.75 -543.125 308.75 -528.75 {lab=vss}
N 310 -720 310 -703.75 {lab=vdd}
N 187.5 -461.25 460 -461.25 {lab=v_ref_fb}
N 187.5 -608.75 187.5 -461.25 {lab=v_ref_fb}
N 187.5 -608.75 220 -608.75 {lab=v_ref_fb}
N 460 -372.5 460 -352.5 {lab=vss}
N 947.5 -711.25 947.5 -695 {lab=vdd}
N 1290 -783.75 1290 -443.75 {lab=VOUT}
N 800 -443.75 1290 -443.75 {lab=VOUT}
N 800 -598.75 800 -443.75 {lab=VOUT}
N 800 -598.75 842.5 -600 {lab=VOUT}
N 1401.25 -703.125 1401.25 -688.75 {lab=vss}
N 1434.6875 -784.0625 1502.1875 -784.0625 {lab=VOUT}
N 1290 -783.75 1434.6875 -784.0625 {lab=VOUT}
N 416.25 -402.5 440 -402.5 {lab=vdd}
N 416.25 -531.25 440 -530 {lab=vdd}
N 460 -461.25 460 -432.5 {lab=v_ref_fb}
N 460 -500 460 -461.25 {lab=v_ref_fb}
N 947.5 -535 947.5 -520 {lab=vss}
N 1022.5 -615 1208.75 -615 {lab=ea_out}
N 1474.6875 -687.5 1475 -701.25 {lab=vss}
N 1401.25 -773.75 1401.25 -762.5 {lab=VOUT}
N 1401.25 -773.75 1475 -773.75 {lab=VOUT}
N 1475 -773.75 1475 -761.25 {lab=VOUT}
N 1433.75 -773.75 1434.6875 -784.0625 {lab=VOUT}
N 672.5 -713.75 672.5 -695 {lab=vdd}
N 676.25 -545 676.25 -527.5 {lab=vss}
N 400 -623.75 420 -623.75 {lab=v_ref_out}
N 420 -623.75 420 -603.75 {lab=v_ref_out}
N 420 -603.75 512.5 -603.75 {lab=v_ref_out}
N 512.5 -625 512.5 -603.75 {lab=v_ref_out}
N 460 -603.75 460 -560 {lab=v_ref_out}
N 460 -650 460 -603.75 {lab=v_ref_out}
N 453.75 -648.75 460 -650 {lab=v_ref_out}
N 772.5 -623.75 842.5 -625 {lab=v_lpf_out}
N 806.25 -642.5 842.5 -625 {lab=v_lpf_out}
N 1038.75 -778.75 1180 -780 {lab=VIN}
N 1240 -780 1290 -783.75 {lab=VOUT}
N 1208.75 -615 1210 -740 {lab=ea_out}
N 1210 -780 1211.25 -846.25 {lab=vss}
C {ref_amp/ref_amp.sym} 240 -683.75 0 0 {name=x_ref_amp}
C {devices/title.sym} 168.75 -40 0 0 {name=l1 author="Danial Noori Zadeh"}
C {devices/ipin.sym} 130 -633.75 0 0 {name=p1 lab=VREF}
C {devices/iopin.sym} 90 -807.5 1 1 {name=p3 lab=vdd}
C {devices/iopin.sym} 50 -807.5 3 0 {name=vss lab=vss}
C {devices/lab_pin.sym} 90 -787.5 3 0 {name=p7 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 50 -787.5 3 0 {name=p11 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 308.75 -528.75 3 0 {name=p2 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 310 -720 1 0 {name=p4 sig_type=std_logic lab=vdd}
C {symbols/ppolyf_u_3k.sym} 460 -530 0 0 {name=R1
W=\{R_ldo_top_r1_w\}
L=\{R_ldo_top_r1_l\}
model=ppolyf_u_3k
spiceprefix=X
m=1}
C {devices/lab_pin.sym} 416.25 -531.25 0 0 {name=p5 sig_type=std_logic lab=vdd}
C {symbols/ppolyf_u_3k.sym} 460 -402.5 0 0 {name=R2
W=\{R_ldo_top_r2_w\}
L=\{R_ldo_top_r2_l\}
model=ppolyf_u_3k
spiceprefix=X
m=1}
C {devices/lab_pin.sym} 416.25 -402.5 0 0 {name=p6 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 460 -352.5 3 0 {name=p8 sig_type=std_logic lab=vss}
C {error_amp/error_amp.sym} 842.5 -675 0 0 {name=x_error_amp}
C {devices/lab_pin.sym} 947.5 -711.25 1 0 {name=p9 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 947.5 -520 3 0 {name=p10 sig_type=std_logic lab=vss}
C {lpf/lpf_rc.sym} 532.5 -673.75 0 0 {name=x_lpf}
C {devices/lab_pin.sym} 672.5 -713.75 1 0 {name=p12 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 676.25 -527.5 3 0 {name=p13 sig_type=std_logic lab=vss}
C {devices/ipin.sym} 1038.75 -778.75 0 0 {name=p14 lab=VIN}
C {devices/res.sym} 1401.25 -732.5 0 0 {name=R3
value=\{R_ldo_top_r3\}
footprint=1206
device=resistor
m=1}
C {devices/opin.sym} 1502.1875 -784.0625 0 0 {name=p15 lab=VOUT}
C {devices/lab_pin.sym} 1401.25 -688.75 3 0 {name=p16 sig_type=std_logic lab=vss}
C {devices/capa.sym} 1475 -731.25 0 0 {name=C1
m=1
value=\{C_ldo_top_c1\}
footprint=1206
device="ceramic capacitor"}
C {devices/lab_pin.sym} 1474.6875 -687.5 3 0 {name=p17 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 1211.25 -846.25 1 0 {name=p18 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 188.75 -461.25 3 0 {name=p19 sig_type=std_logic lab=v_ref_fb}
C {devices/lab_pin.sym} 453.75 -648.75 1 0 {name=p20 sig_type=std_logic lab=v_ref_out}
C {devices/lab_pin.sym} 806.25 -642.5 1 0 {name=p21 sig_type=std_logic lab=v_lpf_out}
C {devices/lab_pin.sym} 1098.75 -615 1 0 {name=p22 sig_type=std_logic lab=ea_out}
C {symbols/pfet_06v0.sym} 1210 -760 1 1 {name=Mp
L=\{XMP_ldo_top_pfet_l\}
W=\{XMP_ldo_top_pfet_w\}
nf=1
m=1
ad="'int((nf+1)/2) * W/nf * 0.18u'"
pd="'2*int((nf+1)/2) * (W/nf + 0.18u)'"
as="'int((nf+2)/2) * W/nf * 0.18u'"
ps="'2*int((nf+2)/2) * (W/nf + 0.18u)'"
nrd="'0.18u / W'" nrs="'0.18u / W'"
sa=0 sb=0 sd=0
model=pfet_06v0
spiceprefix=X
}
