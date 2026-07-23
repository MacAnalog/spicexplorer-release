v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 130 -470 220 -470 {lab=VREF}
N 95 -175 95 -155 {lab=vdd}
N 55 -175 55 -155 {lab=vss}
N 308.75 -379.375 308.75 -365 {lab=vss}
N 310 -556.25 310 -540 {lab=vdd}
N 187.5 -297.5 460 -297.5 {lab=v_ref_fb}
N 187.5 -445 187.5 -297.5 {lab=v_ref_fb}
N 187.5 -445 220 -445 {lab=v_ref_fb}
N 460 -208.75 460 -188.75 {lab=vss}
N 947.5 -547.5 947.5 -531.25 {lab=vdd}
N 1043.75 -620 1181.25 -620 {lab=VIN}
N 1241.25 -620 1290 -620 {lab=VOUT}
N 1290 -620 1290 -280 {lab=VOUT}
N 800 -280 1290 -280 {lab=VOUT}
N 800 -435 800 -280 {lab=VOUT}
N 800 -435 842.5 -436.25 {lab=VOUT}
N 1401.25 -539.375 1401.25 -525 {lab=vss}
N 1434.6875 -620.3125 1502.1875 -620.3125 {lab=VOUT}
N 1290 -620 1434.6875 -620.3125 {lab=VOUT}
N 1211.25 -632.5 1211.25 -618.125 {lab=vss}
N 416.25 -238.75 440 -238.75 {lab=vdd}
N 416.25 -367.5 440 -366.25 {lab=vdd}
N 460 -297.5 460 -268.75 {lab=v_ref_fb}
N 460 -336.25 460 -297.5 {lab=v_ref_fb}
N 947.5 -371.25 947.5 -356.25 {lab=vss}
N 1022.5 -451.25 1208.75 -451.25 {lab=ea_out}
N 1208.75 -451.25 1211.25 -580 {lab=ea_out}
N 1474.6875 -523.75 1475 -537.5 {lab=vss}
N 1401.25 -610 1401.25 -598.75 {lab=VOUT}
N 1401.25 -610 1475 -610 {lab=VOUT}
N 1475 -610 1475 -597.5 {lab=VOUT}
N 1433.75 -610 1434.6875 -620.3125 {lab=VOUT}
N 672.5 -550 672.5 -531.25 {lab=vdd}
N 676.25 -381.25 676.25 -363.75 {lab=vss}
N 400 -460 420 -460 {lab=v_ref_out}
N 420 -460 420 -440 {lab=v_ref_out}
N 420 -440 512.5 -440 {lab=v_ref_out}
N 512.5 -461.25 512.5 -440 {lab=v_ref_out}
N 460 -440 460 -396.25 {lab=v_ref_out}
N 460 -486.25 460 -440 {lab=v_ref_out}
N 453.75 -485 460 -486.25 {lab=v_ref_out}
N 772.5 -460 842.5 -461.25 {lab=v_lpf_out}
N 806.25 -478.75 842.5 -461.25 {lab=v_lpf_out}
C {ldo-005-ti-ldo-buffer-ref/ihp130/ref_amp/ref_amp.sym} 240 -520 0 0 {name=x_ref_amp}
C {devices/title.sym} 168.75 -40 0 0 {name=l1 author="Danial Noori Zadeh"}
C {devices/ipin.sym} 130 -470 0 0 {name=p1 lab=VREF}
C {devices/iopin.sym} 95 -175 1 1 {name=p3 lab=vdd}
C {devices/iopin.sym} 55 -175 3 0 {name=vss lab=vss}
C {devices/lab_pin.sym} 95 -155 3 0 {name=p7 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 55 -155 3 0 {name=p11 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 308.75 -365 3 0 {name=p2 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 310 -556.25 1 0 {name=p4 sig_type=std_logic lab=vdd}
C {sg13g2_pr/rhigh.sym} 460 -366.25 0 0 {name=R1
w=1e-6
l=1.9802u
model=rhigh
spiceprefix=X
m=1
body=sub!
b=0
}
C {devices/lab_pin.sym} 416.25 -367.5 0 0 {name=p5 sig_type=std_logic lab=vdd}
C {sg13g2_pr/rhigh.sym} 460 -238.75 0 0 {name=R2
w=1e-6
l=1.9802u
model=rhigh
spiceprefix=X
m=1
body=sub!
b=0
}
C {devices/lab_pin.sym} 416.25 -238.75 0 0 {name=p6 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 460 -188.75 3 0 {name=p8 sig_type=std_logic lab=vss}
C {ldo-005-ti-ldo-buffer-ref/ihp130/error_amp/error_amp.sym} 842.5 -511.25 0 0 {name=x_error_amp}
C {devices/lab_pin.sym} 947.5 -547.5 1 0 {name=p9 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 947.5 -356.25 3 0 {name=p10 sig_type=std_logic lab=vss}
C {ldo-005-ti-ldo-buffer-ref/ihp130/lpf/lpf_rc.sym} 532.5 -510 0 0 {name=x_lpf}
C {devices/lab_pin.sym} 672.5 -550 1 0 {name=p12 sig_type=std_logic lab=vdd}
C {devices/lab_pin.sym} 676.25 -363.75 3 0 {name=p13 sig_type=std_logic lab=vss}
C {sg13g2_pr/sg13_hv_pmos.sym} 1211.25 -600 3 0 {name=MP
l=0.50u
w=0.30u
ng=1
m=1
model=sg13_hv_pmos
spiceprefix=X
}
C {devices/ipin.sym} 1043.75 -620 0 0 {name=p14 lab=VIN}
C {devices/res.sym} 1401.25 -568.75 0 0 {name=R3
value=1k
footprint=1206
device=resistor
m=1}
C {devices/opin.sym} 1502.1875 -620.3125 0 0 {name=p15 lab=VOUT}
C {devices/lab_pin.sym} 1401.25 -525 3 0 {name=p16 sig_type=std_logic lab=vss}
C {devices/capa.sym} 1475 -567.5 0 0 {name=C1
m=1
value=1p
footprint=1206
device="ceramic capacitor"}
C {devices/lab_pin.sym} 1474.6875 -523.75 3 0 {name=p17 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 1211.25 -632.5 1 0 {name=p18 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 188.75 -297.5 3 0 {name=p19 sig_type=std_logic lab=v_ref_fb}
C {devices/lab_pin.sym} 453.75 -485 1 0 {name=p20 sig_type=std_logic lab=v_ref_out}
C {devices/lab_pin.sym} 806.25 -478.75 1 0 {name=p21 sig_type=std_logic lab=v_lpf_out}
C {devices/lab_pin.sym} 1098.75 -451.25 1 0 {name=p22 sig_type=std_logic lab=ea_out}
