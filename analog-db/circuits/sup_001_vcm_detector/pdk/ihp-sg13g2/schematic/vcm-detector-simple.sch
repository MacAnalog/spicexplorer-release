v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 370 -280 430 -280 {
lab=vcm}
N 370 -390 370 -280 {
lab=vcm}
N 320 -280 370 -280 {
lab=vcm}
N 230 -280 260 -280 {
lab=vinp}
N 490 -280 560 -280 {
lab=vinn}
N 560 -280 560 -200 {
lab=vinn}
N 230 -200 560 -200 {
lab=vinn}
C {res.sym} 290 -280 1 0 {name=Rmp
value=Rm
footprint=1206
device=resistor
m=1}
C {res.sym} 460 -280 1 0 {name=Rmn
value=Rm
footprint=1206
device=resistor
m=1}
C {ipin.sym} 230 -280 0 0 {name=p1 lab=vinp}
C {ipin.sym} 230 -200 0 0 {name=p2 lab=vinn}
C {opin.sym} 370 -390 0 0 {name=p3 lab=vcm}
C {devices/title.sym} 180 -50 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
