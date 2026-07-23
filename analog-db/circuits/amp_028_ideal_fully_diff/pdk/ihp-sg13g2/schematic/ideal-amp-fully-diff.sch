v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
N 330 -290 330 -260 {
lab=vinp}
N 270 -290 330 -290 {
lab=vinp}
N 330 -200 330 -170 {
lab=vinn}
N 270 -170 330 -170 {
lab=vinn}
N 510 -320 510 -260 {
lab=voutn}
N 680 -320 700 -320 {
lab=voutn}
N 610 -320 610 -260 {
lab=voutn}
N 510 -320 610 -320 {
lab=voutn}
N 610 -200 610 -160 {
lab=voutp}
N 510 -160 610 -160 {
lab=voutp}
N 510 -200 510 -160 {
lab=voutp}
N 680 -160 710 -160 {
lab=voutp}
N 680 -320 680 -260 {
lab=voutn}
N 610 -320 680 -320 {
lab=voutn}
N 680 -200 680 -160 {
lab=voutp}
N 610 -160 680 -160 {
lab=voutp}
N 390 -250 470 -250 {
lab=vinp}
N 390 -290 390 -250 {
lab=vinp}
N 330 -290 390 -290 {
lab=vinp}
N 390 -210 470 -210 {
lab=vinn}
N 390 -210 390 -170 {
lab=vinn}
N 330 -170 390 -170 {
lab=vinn}
N 270 -290 270 -260 {
lab=vinp}
N 250 -290 270 -290 {
lab=vinp}
N 270 -200 270 -170 {
lab=vinn}
N 260 -170 270 -170 {
lab=vinn}
N 420 -400 430 -400 {
lab=VDD}
N 420 -400 420 -350 {
lab=VDD}
N 260 -400 280 -400 {
lab=VSS}
N 260 -400 260 -340 {
lab=VSS}
C {vccs.sym} 510 -230 0 0 {name=Gm value=gm_val}
C {res.sym} 610 -230 0 0 {name=Rout
value=rout_val
footprint=1206
device=resistor
m=1}
C {res.sym} 330 -230 0 0 {name=Rin
value=rin_val
footprint=1206
device=resistor
m=1}
C {capa.sym} 680 -230 0 0 {name=Cout
m=1
value=cout_val
footprint=1206
device="ceramic capacitor"}
C {ipin.sym} 250 -290 0 0 {name=p1 lab=vinp}
C {ipin.sym} 260 -170 0 0 {name=p2 lab=vinn}
C {opin.sym} 710 -160 0 0 {name=p3 lab=voutp}
C {opin.sym} 700 -320 0 0 {name=p4 lab=voutn}
C {capa.sym} 270 -230 0 1 {name=Cin
m=1
value=cin_val
footprint=1206
device="ceramic capacitor"}
C {devices/title.sym} 180 -40 0 0 {name=l5 author="Copyright 2026 MacAnalog Research Group"}
C {iopin.sym} 430 -400 0 0 {name=p5 lab=VDD}
C {iopin.sym} 280 -400 0 0 {name=p6 lab=VSS}
C {noconn.sym} 420 -350 0 0 {name=l1}
C {noconn.sym} 260 -340 0 0 {name=l2}
