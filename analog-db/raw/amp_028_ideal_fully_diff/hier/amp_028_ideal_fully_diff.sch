v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_028_ideal_fully_diff} -480 100 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -440 300 0 0 {name=CIN value='cin_val'}
C {devices/capa_np.sym} -220 300 0 0 {name=COUT value='cout_val'}
C {devices/vccs.sym} 0 300 0 0 {name=GM value="\{gm_val\}"}
C {devices/res_np.sym} 220 300 0 0 {name=RIN value='rin_val'}
C {devices/res_np.sym} 440 300 0 0 {name=ROUT value='rout_val'}
N -440 270 -440 230 {}
C {devices/lab_wire.sym} -440 230 0 1 {name=l0 lab=vinp}
N -440 330 -440 370 {}
C {devices/lab_wire.sym} -440 370 2 0 {name=l1 lab=vinn}
N -220 270 -220 230 {}
C {devices/lab_wire.sym} -220 230 0 1 {name=l2 lab=voutn}
N -220 330 -220 370 {}
C {devices/lab_wire.sym} -220 370 2 0 {name=l3 lab=voutp}
N 0 270 0 230 {}
C {devices/lab_wire.sym} 0 230 0 1 {name=l4 lab=voutn}
N 0 330 0 370 {}
C {devices/lab_wire.sym} 0 370 2 0 {name=l5 lab=voutp}
N -40 280 -80 280 {}
C {devices/lab_wire.sym} -80 280 0 0 {name=l6 lab=vinp}
N -40 320 -80 320 {}
C {devices/lab_wire.sym} -80 320 0 0 {name=l7 lab=vinn}
N 220 270 220 230 {}
C {devices/lab_wire.sym} 220 230 0 1 {name=l8 lab=vinp}
N 220 330 220 370 {}
C {devices/lab_wire.sym} 220 370 2 0 {name=l9 lab=vinn}
N 440 270 440 230 {}
C {devices/lab_wire.sym} 440 230 0 1 {name=l10 lab=voutn}
N 440 330 440 370 {}
C {devices/lab_wire.sym} 440 370 2 0 {name=l11 lab=voutp}
