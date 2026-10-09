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
C {devices/vsource.sym} 0 0 0 0 {name=VIN value="dc 0.2 ac 1"}
C {devices/res.sym} 100 0 0 0 {name=RL value=1k}
