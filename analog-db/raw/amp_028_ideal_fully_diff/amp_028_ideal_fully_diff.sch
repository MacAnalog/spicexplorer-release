v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_028_ideal_fully_diff} -40 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 0 0 0 0 {name=CIN value='cin_val'}
C {devices/capa_np.sym} 240 0 0 0 {name=COUT value='cout_val'}
C {devices/res_np.sym} 0 240 0 0 {name=RIN value='rin_val'}
C {devices/res_np.sym} 240 240 0 0 {name=ROUT value='rout_val'}
N 0 -90 0 -30 {}
N 0 30 0 90 {}
N 0 150 0 210 {}
N 0 270 0 330 {}
N 240 -90 240 -30 {}
N 240 30 240 90 {}
N 240 150 240 210 {}
N 240 270 240 330 {}
C {devices/lab_wire.sym} 0 90 2 0 {name=l0 lab=vinn}
C {devices/lab_wire.sym} 0 330 2 0 {name=l1 lab=vinn}
C {devices/lab_wire.sym} 0 -90 0 1 {name=l2 lab=vinp}
C {devices/lab_wire.sym} 0 150 0 1 {name=l3 lab=vinp}
C {devices/lab_wire.sym} 240 -90 0 1 {name=l4 lab=voutn}
C {devices/lab_wire.sym} 240 150 0 1 {name=l5 lab=voutn}
C {devices/lab_wire.sym} 240 90 2 0 {name=l6 lab=voutp}
C {devices/lab_wire.sym} 240 330 2 0 {name=l7 lab=voutp}
C {devices/iopin.sym} 0 520 0 0 {name=p0 lab=vinp}
C {devices/iopin.sym} 120 520 0 0 {name=p1 lab=voutn}
C {devices/iopin.sym} 240 520 0 0 {name=p2 lab=vinn}
C {devices/iopin.sym} 360 520 0 0 {name=p3 lab=voutp}
