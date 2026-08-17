v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {2-bit current-mode DAC PAM-4 driver — top view (paper Fig. 1)} 150 -420 0 0 0.4 0.4 {}
T {MSB = 2 gain cells, LSB = 1 gain cell (see dut_msb.sch / dut_lsb.sch); flat netlist: ../dut/dut_pam4.spice} 150 -380 0 0 0.28 0.28 {}
T {4 V} 620 -318 0 0 0.3 0.3 {layer=7}
C {devices/iopin.sym} 600 -320 1 0 {name=p_vcc lab=vcc}
C {devices/res.sym} 300 -260 0 0 {name=RCP value=50}
C {devices/res.sym} 900 -260 0 0 {name=RCN value=50}
C {devices/opin.sym} 1050 -200 0 0 {name=p_outp lab=outp}
C {devices/opin.sym} 1050 -180 0 0 {name=p_outn lab=outn}
C {gain_cell_amp.sym} 450 -40 0 0 {name=AMSB}
C {gain_cell_amp.sym} 750 -40 0 1 {name=ALSB}
C {devices/ipin.sym} 100 20 0 0 {name=p_msbp lab=msbp}
C {devices/ipin.sym} 100 60 0 0 {name=p_msbn lab=msbn}
C {devices/ipin.sym} 100 100 0 0 {name=p_lsbp lab=lsbp}
C {devices/ipin.sym} 100 140 0 0 {name=p_lsbn lab=lsbn}
C {devices/iopin.sym} 200 -40 0 1 {name=p_bmsb lab=bmsb}
C {devices/iopin.sym} 950 -40 0 0 {name=p_blsb lab=blsb}
C {devices/res.sym} 140 200 0 0 {name=RBmsbp value=50}
C {devices/res.sym} 240 200 0 0 {name=RBmsbn value=50}
C {devices/res.sym} 340 200 0 0 {name=RBlsbp value=50}
C {devices/res.sym} 440 200 0 0 {name=RBlsbn value=50}
C {devices/iopin.sym} 80 280 0 1 {name=p_vcmb lab=vcmb}
N 300 -320 900 -320 {}
N 300 -320 300 -290 {}
N 900 -320 900 -290 {}
N 300 -230 300 -200 {}
N 900 -230 900 -180 {}
N 300 -200 1050 -200 {}
N 470 -180 1050 -180 {}
N 430 -200 430 -100 {}
N 470 -180 470 -100 {}
N 770 -200 770 -100 {}
N 730 -180 730 -100 {}
N 100 20 410 20 {}
N 100 60 490 60 {}
N 490 20 490 60 {}
N 100 100 790 100 {}
N 790 20 790 100 {}
N 100 140 710 140 {}
N 710 20 710 140 {}
N 200 -40 395 -40 {}
N 805 -40 950 -40 {}
N 140 20 140 170 {}
N 240 60 240 170 {}
N 340 100 340 170 {}
N 440 140 440 170 {}
N 140 230 140 280 {}
N 240 230 240 280 {}
N 340 230 340 280 {}
N 440 230 440 280 {}
N 80 280 440 280 {}
