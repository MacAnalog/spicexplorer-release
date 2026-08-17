v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {MSB amplifier — two identical gain cells in parallel (paper Fig. 2b)} 60 -260 0 0 0.4 0.4 {}
T {npn13G2 Nx=3 per device, shared R_C/R_B, tails VCCS 1 mA/V each} 60 -220 0 0 0.28 0.28 {}
C {devices/iopin.sym} 700 -160 0 0 {name=p_vcc lab=vcc}
C {devices/res.sym} 140 -100 0 0 {name=RCP value=50}
C {devices/res.sym} 1260 -100 0 0 {name=RCN value=50}
C {devices/opin.sym} 100 -20 0 1 {name=p_outp lab=outp}
C {devices/opin.sym} 1300 20 0 0 {name=p_outn lab=outn}
C {sg13g2_pr/npn13G2.sym} 200 80 0 0 {name=Q3M0 model=npn13G2 Nx=3 spiceprefix=X}
C {sg13g2_pr/npn13G2.sym} 560 80 0 1 {name=Q4M0 model=npn13G2 Nx=3 spiceprefix=X}
C {sg13g2_pr/npn13G2.sym} 200 240 0 0 {name=Q1M0 model=npn13G2 Nx=3 spiceprefix=X}
C {sg13g2_pr/npn13G2.sym} 560 240 0 1 {name=Q2M0 model=npn13G2 Nx=3 spiceprefix=X}
C {sg13g2_pr/npn13G2.sym} 840 80 0 0 {name=Q3M1 model=npn13G2 Nx=3 spiceprefix=X}
C {sg13g2_pr/npn13G2.sym} 1200 80 0 1 {name=Q4M1 model=npn13G2 Nx=3 spiceprefix=X}
C {sg13g2_pr/npn13G2.sym} 840 240 0 0 {name=Q1M1 model=npn13G2 Nx=3 spiceprefix=X}
C {sg13g2_pr/npn13G2.sym} 1200 240 0 1 {name=Q2M1 model=npn13G2 Nx=3 spiceprefix=X}
C {devices/ipin.sym} 120 80 0 0 {name=p_vcasc lab=vcasc}
C {devices/lab_pin.sym} 640 80 0 1 {name=lVB2 lab=vcasc}
C {devices/lab_pin.sym} 820 40 3 0 {name=lVB3 lab=vcasc}
C {devices/lab_pin.sym} 1280 80 0 1 {name=lVB4 lab=vcasc}
C {devices/ipin.sym} 100 240 0 0 {name=p_inp lab=inp}
C {devices/lab_pin.sym} 640 240 0 1 {name=lin2 lab=inn}
C {devices/lab_pin.sym} 820 200 3 0 {name=lin3 lab=inp}
C {devices/ipin.sym} 1300 240 0 1 {name=p_inn lab=inn}
C {devices/lab_pin.sym} 250 80 0 1 {name=lS3 lab=0}
C {devices/lab_pin.sym} 510 80 0 0 {name=lS4 lab=0}
C {devices/lab_pin.sym} 250 240 0 1 {name=lS1 lab=0}
C {devices/lab_pin.sym} 510 240 0 0 {name=lS2 lab=0}
C {devices/lab_pin.sym} 890 80 0 1 {name=lS7 lab=0}
C {devices/lab_pin.sym} 1150 80 0 0 {name=lS8 lab=0}
C {devices/lab_pin.sym} 890 240 0 1 {name=lS5 lab=0}
C {devices/lab_pin.sym} 1150 240 0 0 {name=lS6 lab=0}
C {devices/capa.sym} 380 270 1 0 {name=CdegM0 value=20f}
C {devices/res.sym} 220 340 0 0 {name=RE1M0 value=2.5}
C {devices/res.sym} 540 340 0 0 {name=RE2M0 value=2.5}
C {devices/vccs.sym} 380 440 0 0 {name=GtailM0 value=1m}
C {devices/iopin.sym} 300 420 0 0 {name=p_bias lab=bias}
C {devices/lab_pin.sym} 300 460 0 0 {name=lcm0 lab=0}
C {devices/gnd.sym} 380 490 0 0 {name=lgnd0 lab=GND}
C {devices/capa.sym} 1020 270 1 0 {name=CdegM1 value=20f}
C {devices/res.sym} 860 340 0 0 {name=RE1M1 value=2.5}
C {devices/res.sym} 1180 340 0 0 {name=RE2M1 value=2.5}
C {devices/vccs.sym} 1020 440 0 0 {name=GtailM1 value=1m}
C {devices/lab_pin.sym} 940 420 0 0 {name=lbias1 lab=bias}
C {devices/lab_pin.sym} 940 460 0 0 {name=lcm1 lab=0}
C {devices/gnd.sym} 1020 490 0 0 {name=lgnd1 lab=GND}
C {devices/res.sym} 140 300 0 0 {name=RBinp value=50}
C {devices/res.sym} 1260 300 0 0 {name=RBinn value=50}
C {devices/iopin.sym} 140 400 3 0 {name=p_vcmb lab=vcmb}
C {devices/lab_pin.sym} 1260 400 3 0 {name=lvcmb lab=vcmb}
N 140 -160 1260 -160 {}
N 140 -160 140 -130 {}
N 1260 -160 1260 -130 {}
N 140 -70 140 -20 {}
N 1260 -70 1260 20 {}
N 100 -20 860 -20 {}
N 540 20 1300 20 {}
N 220 -20 220 50 {}
N 860 -20 860 50 {}
N 540 20 540 50 {}
N 1180 20 1180 50 {}
N 120 80 180 80 {}
N 580 80 640 80 {}
N 820 40 820 80 {}
N 1220 80 1280 80 {}
N 220 80 250 80 {}
N 510 80 540 80 {}
N 860 80 890 80 {}
N 1150 80 1180 80 {}
N 220 110 220 210 {}
N 540 110 540 210 {}
N 860 110 860 210 {}
N 1180 110 1180 210 {}
N 100 240 180 240 {}
N 580 240 640 240 {}
N 820 200 820 240 {}
N 1220 240 1300 240 {}
N 220 240 250 240 {}
N 510 240 540 240 {}
N 860 240 890 240 {}
N 1150 240 1180 240 {}
N 220 270 220 310 {}
N 540 270 540 310 {}
N 220 270 350 270 {}
N 410 270 540 270 {}
N 220 370 540 370 {}
N 380 370 380 410 {}
N 380 470 380 490 {}
N 340 420 300 420 {}
N 340 460 300 460 {}
N 860 270 860 310 {}
N 1180 270 1180 310 {}
N 860 270 990 270 {}
N 1050 270 1180 270 {}
N 860 370 1180 370 {}
N 1020 370 1020 410 {}
N 1020 470 1020 490 {}
N 980 420 940 420 {}
N 980 460 940 460 {}
N 140 240 140 270 {}
N 1260 240 1260 270 {}
N 140 330 140 400 {}
N 1260 330 1260 400 {}
