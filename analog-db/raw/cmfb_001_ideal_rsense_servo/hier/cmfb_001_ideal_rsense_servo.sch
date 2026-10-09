v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cmfb_001_ideal_rsense_servo} -700 100 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -660 300 0 0 {name=CIN_SERVO value='cin_val'}
C {devices/capa_np.sym} -440 300 0 0 {name=COUT_SERVO value='cout_val'}
C {devices/vccs.sym} -220 300 0 0 {name=GM_SERVO value="\{gm_val\}"}
C {devices/res_np.sym} 0 300 0 0 {name=RIN_SERVO value='rin_val'}
C {devices/res_np.sym} 220 300 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 440 300 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} 660 300 0 0 {name=ROUT_SERVO value='rout_val'}
N -660 270 -660 230 {}
C {devices/lab_wire.sym} -660 230 0 1 {name=l0 lab=cm_sense}
N -660 330 -660 370 {}
C {devices/lab_wire.sym} -660 370 2 0 {name=l1 lab=vref}
N -440 270 -440 230 {}
C {devices/lab_wire.sym} -440 230 0 1 {name=l2 lab=vss}
N -440 330 -440 370 {}
C {devices/lab_wire.sym} -440 370 2 0 {name=l3 lab=vcmfb}
N -220 270 -220 230 {}
C {devices/lab_wire.sym} -220 230 0 1 {name=l4 lab=vss}
N -220 330 -220 370 {}
C {devices/lab_wire.sym} -220 370 2 0 {name=l5 lab=vcmfb}
N -260 280 -300 280 {}
C {devices/lab_wire.sym} -300 280 0 0 {name=l6 lab=vref}
N -260 320 -300 320 {}
C {devices/lab_wire.sym} -300 320 0 0 {name=l7 lab=cm_sense}
N 0 270 0 230 {}
C {devices/lab_wire.sym} 0 230 0 1 {name=l8 lab=cm_sense}
N 0 330 0 370 {}
C {devices/lab_wire.sym} 0 370 2 0 {name=l9 lab=vref}
N 220 270 220 230 {}
C {devices/lab_wire.sym} 220 230 0 1 {name=l10 lab=vinn}
N 220 330 220 370 {}
C {devices/lab_wire.sym} 220 370 2 0 {name=l11 lab=cm_sense}
N 440 270 440 230 {}
C {devices/lab_wire.sym} 440 230 0 1 {name=l12 lab=cm_sense}
N 440 330 440 370 {}
C {devices/lab_wire.sym} 440 370 2 0 {name=l13 lab=vinp}
N 660 270 660 230 {}
C {devices/lab_wire.sym} 660 230 0 1 {name=l14 lab=vss}
N 660 330 660 370 {}
C {devices/lab_wire.sym} 660 370 2 0 {name=l15 lab=vcmfb}
