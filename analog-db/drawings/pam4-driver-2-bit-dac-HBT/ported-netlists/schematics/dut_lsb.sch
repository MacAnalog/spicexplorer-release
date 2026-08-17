v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {LSB amplifier — one differential cascode gain cell (paper Fig. 2a)} 60 -260 0 0 0.4 0.4 {}
T {npn13G2 Nx=3, R_E=2.5 Ohm, C_deg=20 fF, R_C=R_B=50 Ohm, tail VCCS 1 mA/V} 60 -220 0 0 0.28 0.28 {}
C {devices/iopin.sym} 380 -160 0 0 {name=p_vcc lab=vcc}
C {devices/res.sym} 140 -100 0 0 {name=RCP value=50}
C {devices/res.sym} 620 -100 0 0 {name=RCN value=50}
C {devices/opin.sym} 100 -20 0 1 {name=p_outp lab=outp}
C {devices/opin.sym} 660 -20 0 0 {name=p_outn lab=outn}
C {sg13g2_pr/npn13G2.sym} 200 80 0 0 {name=Q3L0 model=npn13G2 Nx=3 spiceprefix=X}
C {sg13g2_pr/npn13G2.sym} 560 80 0 1 {name=Q4L0 model=npn13G2 Nx=3 spiceprefix=X}
C {sg13g2_pr/npn13G2.sym} 200 240 0 0 {name=Q1L0 model=npn13G2 Nx=3 spiceprefix=X}
C {sg13g2_pr/npn13G2.sym} 560 240 0 1 {name=Q2L0 model=npn13G2 Nx=3 spiceprefix=X}
C {devices/lab_pin.sym} 640 80 0 1 {name=lVB2 lab=vcasc}
C {devices/ipin.sym} 100 240 0 0 {name=p_inp lab=inp}
C {devices/ipin.sym} 660 240 0 1 {name=p_inn lab=inn}
C {devices/lab_pin.sym} 250 80 0 1 {name=lS3 lab=0}
C {devices/lab_pin.sym} 510 80 0 0 {name=lS4 lab=0}
C {devices/lab_pin.sym} 250 240 0 1 {name=lS1 lab=0}
C {devices/lab_pin.sym} 510 240 0 0 {name=lS2 lab=0}
C {devices/capa.sym} 380 270 1 0 {name=CdegL0 value=20f}
C {devices/res.sym} 220 340 0 0 {name=RE1L0 value=2.5}
C {devices/res.sym} 540 340 0 0 {name=RE2L0 value=2.5}
C {devices/vccs.sym} 380 440 0 0 {name=GtailL0 value=1m}
C {devices/lab_pin.sym} 300 460 0 0 {name=lcm lab=0}
C {devices/gnd.sym} 380 490 0 0 {name=lgnd lab=GND}
C {devices/res.sym} 140 300 0 0 {name=RBinp value=50}
C {devices/res.sym} 620 300 0 0 {name=RBinn value=50}
C {devices/iopin.sym} 140 400 3 0 {name=p_vcmb lab=vcmb}
C {devices/lab_pin.sym} 620 400 3 0 {name=lvcmb lab=vcmb}
C {devices/iopin.sym} 300 420 0 0 {name=p_bias lab=bias}
C {devices/ipin.sym} 120 80 0 0 {name=p_vcasc lab=vcasc}
N 140 -160 620 -160 {}
N 140 -160 140 -130 {}
N 620 -160 620 -130 {}
N 140 -70 140 -20 {}
N 620 -70 620 -20 {}
N 100 -20 140 -20 {}
N 620 -20 660 -20 {}
N 140 -20 140 20 {}
N 620 -20 620 20 {}
N 140 20 220 20 {}
N 540 20 620 20 {}
N 220 20 220 50 {}
N 540 20 540 50 {}
N 120 80 180 80 {}
N 580 80 640 80 {}
N 220 80 250 80 {}
N 510 80 540 80 {}
N 220 110 220 210 {}
N 540 110 540 210 {}
N 100 240 180 240 {}
N 580 240 660 240 {}
N 220 240 250 240 {}
N 510 240 540 240 {}
N 220 270 220 310 {}
N 540 270 540 310 {}
N 220 270 350 270 {}
N 410 270 540 270 {}
N 220 370 540 370 {}
N 380 370 380 410 {}
N 380 470 380 490 {}
N 340 420 300 420 {}
N 340 460 300 460 {}
N 140 240 140 270 {}
N 620 240 620 270 {}
N 140 330 140 400 {}
N 620 330 620 400 {}
