v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sup_001_vcm_detector} -40 -200 0 0 0.4 0.4 {}
C {devices/res_np.sym} 0 0 0 0 {name=RMN value='x_dut_rmn_value'}
C {devices/res_np.sym} 240 0 0 0 {name=RMP value='x_dut_rmp_value'}
N 0 -90 0 -30 {}
N 0 30 0 90 {}
N 240 -90 240 -30 {}
N 240 30 240 90 {}
C {devices/lab_wire.sym} 0 90 2 0 {name=l0 lab=vcm_out}
C {devices/lab_wire.sym} 240 -90 0 1 {name=l1 lab=vcm_out}
C {devices/lab_wire.sym} 0 -90 0 1 {name=l2 lab=vinn}
C {devices/lab_wire.sym} 240 90 2 0 {name=l3 lab=vinp}
C {devices/iopin.sym} 0 280 0 0 {name=p0 lab=vinn}
C {devices/iopin.sym} 240 280 0 0 {name=p1 lab=vcm_out}
C {devices/iopin.sym} 360 280 0 0 {name=p2 lab=vinp}
