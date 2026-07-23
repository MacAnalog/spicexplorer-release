v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_028_ideal_fully_diff} -370 100 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -330 300 0 0 {name=CIN value='cin_val'}
C {devices/capa_np.sym} -110 300 0 0 {name=COUT value='cout_val'}
C {devices/res_np.sym} 110 300 0 0 {name=RIN value='rin_val'}
C {devices/res_np.sym} 330 300 0 0 {name=ROUT value='rout_val'}
N -330 270 -330 230 {}
C {devices/lab_wire.sym} -330 230 0 1 {name=l0 lab=vinp}
N -330 330 -330 370 {}
C {devices/lab_wire.sym} -330 370 2 0 {name=l1 lab=vinn}
N -110 270 -110 230 {}
C {devices/lab_wire.sym} -110 230 0 1 {name=l2 lab=voutn}
N -110 330 -110 370 {}
C {devices/lab_wire.sym} -110 370 2 0 {name=l3 lab=voutp}
N 110 270 110 230 {}
C {devices/lab_wire.sym} 110 230 0 1 {name=l4 lab=vinp}
N 110 330 110 370 {}
C {devices/lab_wire.sym} 110 370 2 0 {name=l5 lab=vinn}
N 330 270 330 230 {}
C {devices/lab_wire.sym} 330 230 0 1 {name=l6 lab=voutn}
N 330 330 330 370 {}
C {devices/lab_wire.sym} 330 370 2 0 {name=l7 lab=voutp}
