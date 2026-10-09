v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_028_ideal_fully_diff} -40 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 0 0 0 0 {name=CIN value='cin_val'}
C {devices/capa_np.sym} 240 0 0 0 {name=COUT value='cout_val'}
C {devices/vccs.sym} 480 0 0 0 {name=GM value="\{gm_val\}"}
C {devices/res_np.sym} 0 240 0 0 {name=RIN value='rin_val'}
C {devices/res_np.sym} 240 240 0 0 {name=ROUT value='rout_val'}
N -60 60 -60 300 {}
N 0 -90 0 -30 {}
N 0 30 0 90 {}
N 0 180 0 210 {}
N 0 270 0 300 {}
N 60 -60 60 180 {}
N 240 180 240 210 {}
N 240 270 240 360 {}
N 300 -30 300 180 {}
N 360 30 360 300 {}
N 480 -60 480 -30 {}
N 480 30 480 360 {}
N 540 -60 540 180 {}
N 0 -60 60 -60 {}
N 480 -60 540 -60 {}
N 240 -30 300 -30 {}
N 410 -20 440 -20 {}
N 410 20 440 20 {}
N 240 30 360 30 {}
N -60 60 0 60 {}
N 0 180 60 180 {}
N 240 180 540 180 {}
N -60 300 0 300 {}
N 240 300 360 300 {}
N 240 360 480 360 {}
C {devices/lab_wire.sym} 0 90 2 0 {name=l0 lab=vinn}
C {devices/lab_wire.sym} 0 -90 0 1 {name=l1 lab=vinp}
C {devices/iopin.sym} 410 -20 0 0 {name=p0 lab=vinp}
C {devices/iopin.sym} 240 180 0 0 {name=p1 lab=voutn}
C {devices/iopin.sym} 410 20 0 0 {name=p2 lab=vinn}
C {devices/iopin.sym} 240 360 0 0 {name=p3 lab=voutp}
