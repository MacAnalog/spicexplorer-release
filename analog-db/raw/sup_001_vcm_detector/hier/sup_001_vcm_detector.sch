v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sup_001_vcm_detector} -150 100 0 0 0.4 0.4 {}
C {devices/res_np.sym} -110 300 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 110 300 0 0 {name=RMP value='x_dut_rmp_value'}
N -110 270 -110 230 {}
C {devices/lab_wire.sym} -110 230 0 1 {name=l0 lab=vinn}
N -110 330 -110 370 {}
C {devices/lab_wire.sym} -110 370 2 0 {name=l1 lab=vcm_out}
N 110 270 110 230 {}
C {devices/lab_wire.sym} 110 230 0 1 {name=l2 lab=vcm_out}
N 110 330 110 370 {}
C {devices/lab_wire.sym} 110 370 2 0 {name=l3 lab=vinp}
