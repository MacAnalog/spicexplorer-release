v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cmfb_001_ideal_rsense_servo} -40 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 0 0 0 0 {name=CIN_SERVO value='cin_val'}
C {devices/capa_np.sym} 240 0 0 0 {name=COUT_SERVO value='cout_val'}
C {devices/res_np.sym} 480 0 0 0 {name=RIN_SERVO value='rin_val'}
C {devices/res_np.sym} 0 240 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 240 240 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} 480 240 0 0 {name=ROUT_SERVO value='rout_val'}
N 0 -90 0 -30 {}
N 0 30 0 90 {}
N 0 150 0 210 {}
N 0 270 0 330 {}
N 240 -90 240 -30 {}
N 240 30 240 90 {}
N 240 150 240 210 {}
N 240 270 240 330 {}
N 480 -60 480 -30 {}
N 480 30 480 90 {}
N 480 150 480 210 {}
N 480 270 480 330 {}
N 0 -60 480 -60 {}
N -60 380 665 380 {}
C {devices/lab_wire.sym} -60 380 0 0 {name=l0 lab=vss}
C {devices/lab_wire.sym} 0 -90 0 1 {name=l1 lab=cm_sense}
C {devices/lab_wire.sym} 0 330 2 0 {name=l2 lab=cm_sense}
C {devices/lab_wire.sym} 240 150 0 1 {name=l3 lab=cm_sense}
C {devices/lab_wire.sym} 240 90 2 0 {name=l4 lab=vcmfb}
C {devices/lab_wire.sym} 480 330 2 0 {name=l5 lab=vcmfb}
C {devices/lab_wire.sym} 0 150 0 1 {name=l6 lab=vinn}
C {devices/lab_wire.sym} 240 330 2 0 {name=l7 lab=vinp}
C {devices/lab_wire.sym} 0 90 2 0 {name=l8 lab=vref}
C {devices/lab_wire.sym} 480 90 2 0 {name=l9 lab=vref}
C {devices/lab_wire.sym} 240 -90 0 1 {name=l10 lab=vss}
C {devices/lab_wire.sym} 480 150 0 1 {name=l11 lab=vss}
C {devices/iopin.sym} 0 520 0 0 {name=p0 lab=vref}
C {devices/iopin.sym} 120 520 0 0 {name=p1 lab=vcmfb}
C {devices/iopin.sym} 240 520 0 0 {name=p2 lab=vinn}
C {devices/iopin.sym} 360 520 0 0 {name=p3 lab=vinp}
