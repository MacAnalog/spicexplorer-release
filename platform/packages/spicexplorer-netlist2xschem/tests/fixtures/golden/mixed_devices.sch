v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {mixed_devices} -40 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 240 240 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=1u l=0.13u}
C {devices/sg13_lv_pmos_np.sym} 480 240 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=2u l=0.13u}
C {devices/res_np.sym} 480 0 0 0 {name=R1 value=10k}
C {devices/capa_np.sym} 0 0 0 0 {name=C1 value=1p}
C {devices/vsource_np.sym} 0 240 0 0 {name=V1 value=1.8}
C {devices/isource_np.sym} 240 0 0 0 {name=I1 value=10u}
C {devices/lab_wire.sym} 260 210 0 0 {name=l0 lab=out}
C {devices/lab_wire.sym} 220 240 0 0 {name=l1 lab=in}
C {devices/lab_wire.sym} 260 270 0 0 {name=l2 lab=0}
C {devices/lab_wire.sym} 260 240 0 0 {name=l3 lab=0}
C {devices/lab_wire.sym} 500 270 0 0 {name=l4 lab=vdd}
C {devices/lab_wire.sym} 460 240 0 0 {name=l5 lab=in}
C {devices/lab_wire.sym} 500 210 0 0 {name=l6 lab=out}
C {devices/lab_wire.sym} 500 240 0 0 {name=l7 lab=vdd}
C {devices/lab_wire.sym} 480 -30 0 0 {name=l8 lab=out}
C {devices/lab_wire.sym} 480 30 0 0 {name=l9 lab=vdd}
C {devices/lab_wire.sym} 0 -30 0 0 {name=l10 lab=out}
C {devices/lab_wire.sym} 0 30 0 0 {name=l11 lab=0}
C {devices/lab_wire.sym} 0 210 0 0 {name=l12 lab=vdd}
C {devices/lab_wire.sym} 0 270 0 0 {name=l13 lab=0}
C {devices/lab_wire.sym} 240 -30 0 0 {name=l14 lab=vdd}
C {devices/lab_wire.sym} 240 30 0 0 {name=l15 lab=in}
