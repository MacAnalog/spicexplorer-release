v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_ihp_capless} -1100 -200 0 0 0.4 0.4 {}
C {blocks/bias_ref.sym} -840 0 0 0 {name=xbias_ref}
C {blocks/ea_stage1.sym} -420 0 0 0 {name=xea_stage1}
C {blocks/ea_stage2.sym} 0 0 0 0 {name=xea_stage2}
C {blocks/fvf_output.sym} 420 0 0 0 {name=xfvf_output}
C {blocks/fb_divider.sym} 840 0 0 0 {name=xfb_divider}
C {devices/vsource.sym} -1060 120 0 0 {name=VREF value="dc \{vref_val\}"}
C {devices/vsource.sym} -1060 340 0 0 {name=VLP value="dc 0"}
C {sg13g2_pr/cap_cmim.sym} 0 340 0 0 {name=COUT model=cap_cmim spiceprefix=X w=c_out_w l=c_out_w m=c_out_m}
N -740 -20 -700 -20 {}
C {devices/lab_wire.sym} -700 -20 0 1 {name=l0 lab=nbias}
N -740 20 -700 20 {}
C {devices/lab_wire.sym} -700 20 0 1 {name=l1 lab=pbias}
N -840 -80 -840 -120 {}
C {devices/lab_wire.sym} -840 -120 0 1 {name=l2 lab=vdd}
N -840 80 -840 120 {}
C {devices/lab_wire.sym} -840 120 2 0 {name=l3 lab=vss}
N -520 -40 -560 -40 {}
C {devices/lab_wire.sym} -560 -40 0 0 {name=l4 lab=fb}
N -520 0 -560 0 {}
C {devices/lab_wire.sym} -560 0 0 0 {name=l5 lab=pbias}
N -520 40 -560 40 {}
C {devices/lab_wire.sym} -560 40 0 0 {name=l6 lab=vref}
N -320 0 -280 0 {}
C {devices/lab_wire.sym} -280 0 0 1 {name=l7 lab=ea_o1}
N -420 -100 -420 -140 {}
C {devices/lab_wire.sym} -420 -140 0 1 {name=l8 lab=vdd}
N -420 100 -420 140 {}
C {devices/lab_wire.sym} -420 140 2 0 {name=l9 lab=vss}
N -100 0 -140 0 {}
C {devices/lab_wire.sym} -140 0 0 0 {name=l10 lab=pbias}
N 100 -20 140 -20 {}
C {devices/lab_wire.sym} 140 -20 0 1 {name=l11 lab=ea_o1}
N 100 20 140 20 {}
C {devices/lab_wire.sym} 140 20 0 1 {name=l12 lab=ea_out}
N 0 -80 0 -120 {}
C {devices/lab_wire.sym} 0 -120 0 1 {name=l13 lab=vdd}
N 0 80 0 120 {}
C {devices/lab_wire.sym} 0 120 2 0 {name=l14 lab=vss}
N 320 -20 280 -20 {}
C {devices/lab_wire.sym} 280 -20 0 0 {name=l15 lab=ea_out}
N 320 20 280 20 {}
C {devices/lab_wire.sym} 280 20 0 0 {name=l16 lab=nbias}
N 520 0 560 0 {}
C {devices/lab_wire.sym} 560 0 0 1 {name=l17 lab=vout}
N 420 -80 420 -120 {}
C {devices/lab_wire.sym} 420 -120 0 1 {name=l18 lab=vdd}
N 420 80 420 120 {}
C {devices/lab_wire.sym} 420 120 2 0 {name=l19 lab=vss}
N 940 -20 980 -20 {}
C {devices/lab_wire.sym} 980 -20 0 1 {name=l20 lab=fb}
N 940 20 980 20 {}
C {devices/lab_wire.sym} 980 20 0 1 {name=l21 lab=lp_brk}
N 840 80 840 120 {}
C {devices/lab_wire.sym} 840 120 2 0 {name=l22 lab=vss}
N -1060 90 -1060 50 {}
C {devices/lab_wire.sym} -1060 50 0 1 {name=l23 lab=vref}
N -1060 150 -1060 190 {}
C {devices/lab_wire.sym} -1060 190 2 0 {name=l24 lab=vss}
N -1060 310 -1060 270 {}
C {devices/lab_wire.sym} -1060 270 0 1 {name=l25 lab=lp_brk}
N -1060 370 -1060 410 {}
C {devices/lab_wire.sym} -1060 410 2 0 {name=l26 lab=vout}
N 0 310 0 270 {}
C {devices/lab_wire.sym} 0 270 0 1 {name=l27 lab=vout}
N 0 370 0 410 {}
C {devices/lab_wire.sym} 0 410 2 0 {name=l28 lab=vss}
C {devices/iopin.sym} -1060 570 0 0 {name=p_vdd lab=vdd}
C {devices/opin.sym} -840 570 0 0 {name=p_vout lab=vout}
C {devices/iopin.sym} -620 570 0 0 {name=p_vss lab=vss}
