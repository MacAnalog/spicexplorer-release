v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {adc_001_inv1b} -40 -200 0 0 0.4 0.4 {}
C {blocks/inv_cmos_stack_1.sym} 0 0 0 0 {name=xinv_cmos_stack_1}
N -110 0 -150 0 {}
C {devices/lab_wire.sym} -150 0 0 0 {name=l0 lab=vin}
N 110 0 150 0 {}
C {devices/lab_wire.sym} 150 0 0 1 {name=l1 lab=vout}
N 0 -80 0 -120 {}
C {devices/lab_wire.sym} 0 -120 0 1 {name=l2 lab=vdd}
N 0 80 0 120 {}
C {devices/lab_wire.sym} 0 120 2 0 {name=l3 lab=vss}
