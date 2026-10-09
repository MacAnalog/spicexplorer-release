v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 0 -30 100 -30 {
lab=vin}
N 0 30 100 30 {
lab=0}
N 200 -30 300 -30 {
lab=vout}
C {devices/vsource.sym} 0 0 0 0 {name=VIN value="dc 0.2"}
C {devices/res.sym} 100 0 0 0 {name=RL value=1k}
C {sar_cmp.sym} 250 0 0 0 {name=XCMP}
C {nowhere/title.sym} 0 -260 0 0 {name=TITLE author="MacAnalog"}
