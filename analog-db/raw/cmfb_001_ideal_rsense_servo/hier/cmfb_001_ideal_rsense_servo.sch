v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cmfb_001_ideal_rsense_servo} -590 100 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -550 300 0 0 {name=CIN_SERVO value='cin_val'}
C {devices/capa_np.sym} -330 300 0 0 {name=COUT_SERVO value='cout_val'}
C {devices/res_np.sym} -110 300 0 0 {name=RIN_SERVO value='rin_val'}
C {devices/res_np.sym} 110 300 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 330 300 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} 550 300 0 0 {name=ROUT_SERVO value='rout_val'}
N -550 270 -550 230 {}
C {devices/lab_wire.sym} -550 230 0 1 {name=l0 lab=cm_sense}
N -550 330 -550 370 {}
C {devices/lab_wire.sym} -550 370 2 0 {name=l1 lab=vref}
N -330 270 -330 230 {}
C {devices/lab_wire.sym} -330 230 0 1 {name=l2 lab=vss}
N -330 330 -330 370 {}
C {devices/lab_wire.sym} -330 370 2 0 {name=l3 lab=vcmfb}
N -110 270 -110 230 {}
C {devices/lab_wire.sym} -110 230 0 1 {name=l4 lab=cm_sense}
N -110 330 -110 370 {}
C {devices/lab_wire.sym} -110 370 2 0 {name=l5 lab=vref}
N 110 270 110 230 {}
C {devices/lab_wire.sym} 110 230 0 1 {name=l6 lab=vinn}
N 110 330 110 370 {}
C {devices/lab_wire.sym} 110 370 2 0 {name=l7 lab=cm_sense}
N 330 270 330 230 {}
C {devices/lab_wire.sym} 330 230 0 1 {name=l8 lab=cm_sense}
N 330 330 330 370 {}
C {devices/lab_wire.sym} 330 370 2 0 {name=l9 lab=vinp}
N 550 270 550 230 {}
C {devices/lab_wire.sym} 550 230 0 1 {name=l10 lab=vss}
N 550 330 550 370 {}
C {devices/lab_wire.sym} 550 370 2 0 {name=l11 lab=vcmfb}
