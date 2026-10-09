v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sup_001_vcm_detector} -40 -200 0 0 0.4 0.4 {}
C {devices/res_np.sym} 0 0 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 250 0 0 0 {name=RMP value='x_dut_rmp_value'}
N 0 -60 0 -30 {}
N 0 30 0 120 {}
N 250 -90 250 -30 {}
N 250 30 250 120 {}
C {devices/lab_wire.sym} 250 -90 0 1 {name=l0 lab=vcm_out}
C {devices/iopin.sym} 0 -60 0 0 {name=p0 lab=vinn}
C {devices/iopin.sym} 0 120 0 0 {name=p1 lab=vcm_out}
C {devices/iopin.sym} 250 120 0 0 {name=p2 lab=vinp}
