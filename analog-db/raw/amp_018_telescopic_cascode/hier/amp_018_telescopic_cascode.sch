v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_018_telescopic_cascode} -750 -420 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -490 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/dp_nmos_cascode_1.sym} -50 0 0 0 {name=xdp_nmos_cascode_1}
C {blocks/cm_pmos_low_voltage_cascode_1.sym} 440 0 0 0 {name=xcm_pmos_low_voltage_cascode_1}
C {devices/vsource_np.sym} -710 0 0 0 {name=V1 value=x_dut_v_bias_2}
C {devices/vsource_np.sym} -710 -220 0 0 {name=V2 value=x_dut_v_bias_1}
N -380 -20 -340 -20 {}
C {devices/lab_wire.sym} -340 -20 0 1 {name=l0 lab=ibias}
N -380 20 -340 20 {}
C {devices/lab_wire.sym} -340 20 0 1 {name=l1 lab=tail}
N -490 80 -490 120 {}
C {devices/lab_wire.sym} -490 120 2 0 {name=l2 lab=vss}
N -160 -40 -200 -40 {}
C {devices/lab_wire.sym} -200 -40 0 0 {name=l3 lab=casc_n}
N -160 0 -200 0 {}
C {devices/lab_wire.sym} -200 0 0 0 {name=l4 lab=vinn}
N -160 40 -200 40 {}
C {devices/lab_wire.sym} -200 40 0 0 {name=l5 lab=vinp}
N 60 -40 100 -40 {}
C {devices/lab_wire.sym} 100 -40 0 1 {name=l6 lab=gate_p}
N 60 0 100 0 {}
C {devices/lab_wire.sym} 100 0 0 1 {name=l7 lab=tail}
N 60 40 100 40 {}
C {devices/lab_wire.sym} 100 40 0 1 {name=l8 lab=vout}
N -50 100 -50 140 {}
C {devices/lab_wire.sym} -50 140 2 0 {name=l9 lab=vss}
N 280 0 240 0 {}
C {devices/lab_wire.sym} 240 0 0 0 {name=l10 lab=gate_pc}
N 600 -20 640 -20 {}
C {devices/lab_wire.sym} 640 -20 0 1 {name=l11 lab=gate_p}
N 600 20 640 20 {}
C {devices/lab_wire.sym} 640 20 0 1 {name=l12 lab=vout}
N 440 -80 440 -120 {}
C {devices/lab_wire.sym} 440 -120 0 1 {name=l13 lab=vdd}
N -710 -30 -710 -70 {}
C {devices/lab_wire.sym} -710 -70 0 1 {name=l14 lab=vdd}
N -710 30 -710 70 {}
C {devices/lab_wire.sym} -710 70 2 0 {name=l15 lab=gate_pc}
N -710 -250 -710 -290 {}
C {devices/lab_wire.sym} -710 -290 0 1 {name=l16 lab=casc_n}
N -710 -190 -710 -150 {}
C {devices/lab_wire.sym} -710 -150 2 0 {name=l17 lab=tail}
