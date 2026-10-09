v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cmfb_001_ideal_rsense_servo} -40 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 0 0 0 0 {name=CIN_SERVO value='cin_val'}
C {devices/capa_np.sym} 240 0 0 0 {name=COUT_SERVO value='cout_val'}
C {devices/vccs.sym} 490 0 0 0 {name=GM_SERVO value="\{gm_val\}"}
C {devices/res_np.sym} 0 240 0 0 {name=RIN_SERVO value='rin_val'}
C {devices/res_np.sym} 240 240 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 490 240 0 0 {name=RMP value='x_dut_rmp_value'}
C {devices/res_np.sym} 0 480 0 0 {name=ROUT_SERVO value='rout_val'}
N -60 -60 -60 180 {}
N 0 -90 0 -30 {}
N 0 30 0 90 {}
N 0 180 0 210 {}
N 0 270 0 300 {}
N 0 390 0 450 {}
N 0 510 0 600 {}
N 60 60 60 300 {}
N 240 -90 240 -30 {}
N 240 30 240 120 {}
N 240 150 240 210 {}
N 240 270 240 360 {}
N 300 180 300 300 {}
N 450 20 450 360 {}
N 490 -90 490 -30 {}
N 490 30 490 120 {}
N 490 180 490 210 {}
N 490 270 490 360 {}
N 550 20 550 180 {}
N -60 -60 0 -60 {}
N 420 -20 450 -20 {}
N 450 20 550 20 {}
N 0 60 60 60 {}
N 240 120 490 120 {}
N -60 180 300 180 {}
N 490 180 550 180 {}
N 0 300 60 300 {}
N 240 300 300 300 {}
N 240 360 450 360 {}
N -60 620 805 620 {}
C {devices/lab_wire.sym} 0 -90 0 1 {name=l0 lab=cm_sense}
C {devices/lab_wire.sym} 240 90 2 0 {name=l1 lab=vcmfb}
C {devices/lab_wire.sym} 240 150 0 1 {name=l2 lab=vinn}
C {devices/lab_wire.sym} 0 90 2 0 {name=l3 lab=vref}
C {devices/lab_wire.sym} 240 -90 0 1 {name=l4 lab=vss}
C {devices/lab_wire.sym} 490 -90 0 1 {name=l5 lab=vss}
C {devices/lab_wire.sym} 0 390 0 1 {name=l6 lab=vss}
C {devices/iopin.sym} -60 620 0 0 {name=p0 lab=vss}
C {devices/iopin.sym} 420 -20 0 0 {name=p1 lab=vref}
C {devices/iopin.sym} 0 600 0 0 {name=p2 lab=vcmfb}
C {devices/iopin.sym} 490 360 0 0 {name=p3 lab=vinp}
C {devices/iopin.sym} 240 760 0 0 {name=p4 lab=vinn}
