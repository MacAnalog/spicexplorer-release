v {xschem version=3.4.4 file_version=1.2}
N -800 -1920 1240 -1920 {}
N -800 -540 1240 -540 {}
N -520 -1720 -460 -1720 {}
N -460 -1720 -460 -1760 {}
N -520 -1750 -520 -1920 {}
N -560 -1720 -560 -1520 {}
N -320 -1720 -260 -1720 {}
N -260 -1720 -260 -1760 {}
N -320 -1750 -320 -1920 {}
N -360 -1720 -360 -1520 {}
N -100 -1720 -40 -1720 {}
N -40 -1720 -40 -1760 {}
N -100 -1750 -100 -1920 {}
N -140 -1720 -140 -1520 {}
N -640 -1520 -140 -1520 {}
N -520 -1690 -520 -1520 {}
N -320 -1690 -320 -1620 {}
N -100 -1690 -100 -1340 {}
N -220 -1340 20 -1340 {}
N -220 -1250 -160 -1250 {}
N -160 -1250 -160 -1290 {}
N -220 -1280 -220 -1340 {}
N 20 -1250 80 -1250 {}
N 80 -1250 80 -1290 {}
N 20 -1280 20 -1340 {}
N -640 -1250 -260 -1250 {}
N -640 -930 -20 -930 {}
N -20 -930 -20 -1250 {}
N 20 -1220 20 -1050 {}
N 20 -1050 320 -1050 {}
N -220 -1220 -220 -960 {}
N -220 -960 820 -960 {}
N 320 -1720 260 -1720 {}
N 260 -1720 260 -1760 {}
N 320 -1750 320 -1920 {}
N 320 -1430 260 -1430 {}
N 260 -1430 260 -1470 {}
N 320 -1690 320 -1460 {}
N 320 -1140 260 -1140 {}
N 260 -1140 260 -1100 {}
N 320 -1400 320 -1170 {}
N 320 -800 260 -800 {}
N 260 -800 260 -760 {}
N 320 -1110 320 -830 {}
N 320 -770 320 -540 {}
N 360 -800 360 -880 {}
N 820 -1720 880 -1720 {}
N 880 -1720 880 -1760 {}
N 820 -1750 820 -1920 {}
N 820 -1430 880 -1430 {}
N 880 -1430 880 -1470 {}
N 820 -1690 820 -1460 {}
N 820 -1140 880 -1140 {}
N 880 -1140 880 -1100 {}
N 820 -1400 820 -1170 {}
N 820 -800 880 -800 {}
N 880 -800 880 -760 {}
N 820 -1110 820 -830 {}
N 820 -770 820 -540 {}
N 780 -800 780 -880 {}
N 360 -1720 780 -1720 {}
N 360 -1430 780 -1430 {}
N 360 -1140 780 -1140 {}
N 360 -880 780 -880 {}
N 820 -1300 1120 -1300 {}
N 570 -1370 570 -1340 {}
N 570 -1080 570 -1050 {}
N 590 -800 650 -800 {}
N 650 -800 650 -760 {}
N 590 -830 590 -880 {}
N 550 -800 550 -880 {}
N 590 -770 590 -540 {}
C {devices/iopin.sym} -640 -1920 0 1 {name=P1 lab=vdd}
C {devices/iopin.sym} -640 -540 0 1 {name=P2 lab=vss}
C {devices/sg13_lv_pmos_np.sym} -540 -1720 0 0 {name=M11
w=x_dut_xm11_w
l=x_dut_xm11_l
ng=x_dut_xm11_ng
m=x_dut_xm11_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} -460 -1760 0 1 {name=l3 sig_type=std_logic lab=vdd}
C {devices/sg13_lv_pmos_np.sym} -340 -1720 0 0 {name=M12
w=x_dut_xm12_w
l=x_dut_xm12_l
ng=x_dut_xm12_ng
m=x_dut_xm12_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} -260 -1760 0 1 {name=l5 sig_type=std_logic lab=vdd}
C {devices/sg13_lv_pmos_np.sym} -120 -1720 0 0 {name=M0
w=x_dut_xm0_w
l=x_dut_xm0_l
ng=x_dut_xm0_ng
m=x_dut_xm0_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} -40 -1760 0 1 {name=l7 sig_type=std_logic lab=vdd}
C {devices/ipin.sym} -640 -1520 0 0 {name=P3 lab=ibias}
C {devices/lab_pin.sym} -320 -1620 0 1 {name=l9 sig_type=std_logic lab=nbias}
C {devices/lab_pin.sym} -220 -1340 0 0 {name=l10 sig_type=std_logic lab=tail}
C {devices/sg13_lv_pmos_np.sym} -240 -1250 0 0 {name=M2
w=x_dut_xm2_w
l=x_dut_xm2_l
ng=x_dut_xm2_ng
m=x_dut_xm2_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} -160 -1290 0 1 {name=l12 sig_type=std_logic lab=vdd}
C {devices/sg13_lv_pmos_np.sym} 0 -1250 0 0 {name=M1
w=x_dut_xm1_w
l=x_dut_xm1_l
ng=x_dut_xm1_ng
m=x_dut_xm1_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 80 -1290 0 1 {name=l14 sig_type=std_logic lab=vdd}
C {devices/ipin.sym} -640 -1250 0 0 {name=P4 lab=vinn}
C {devices/ipin.sym} -640 -930 0 0 {name=P5 lab=vinp}
C {devices/lab_pin.sym} 170 -1050 0 1 {name=l17 sig_type=std_logic lab=foldp}
C {devices/lab_pin.sym} 60 -960 0 1 {name=l18 sig_type=std_logic lab=foldn}
C {devices/sg13_lv_pmos_np.sym} 340 -1720 0 1 {name=M9
w=x_dut_xm9_w
l=x_dut_xm9_l
ng=x_dut_xm9_ng
m=x_dut_xm9_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 260 -1760 0 0 {name=l20 sig_type=std_logic lab=vdd}
C {devices/sg13_lv_pmos_np.sym} 340 -1430 0 1 {name=M7
w=x_dut_xm7_w
l=x_dut_xm7_l
ng=x_dut_xm7_ng
m=x_dut_xm7_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 260 -1470 0 0 {name=l22 sig_type=std_logic lab=vdd}
C {devices/sg13_lv_nmos_np.sym} 340 -1140 0 1 {name=M5
w=x_dut_xm5_w
l=x_dut_xm5_l
ng=x_dut_xm5_ng
m=x_dut_xm5_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 260 -1100 0 0 {name=l24 sig_type=std_logic lab=vss}
C {devices/sg13_lv_nmos_np.sym} 340 -800 0 1 {name=M3
w=x_dut_xm3_w
l=x_dut_xm3_l
ng=x_dut_xm3_ng
m=x_dut_xm3_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 260 -760 0 0 {name=l26 sig_type=std_logic lab=vss}
C {devices/sg13_lv_pmos_np.sym} 800 -1720 0 0 {name=M10
w=x_dut_xm10_w
l=x_dut_xm10_l
ng=x_dut_xm10_ng
m=x_dut_xm10_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 880 -1760 0 1 {name=l28 sig_type=std_logic lab=vdd}
C {devices/sg13_lv_pmos_np.sym} 800 -1430 0 0 {name=M8
w=x_dut_xm8_w
l=x_dut_xm8_l
ng=x_dut_xm8_ng
m=x_dut_xm8_m
model=sg13_lv_pmos
spiceprefix=X
}
C {devices/lab_pin.sym} 880 -1470 0 1 {name=l30 sig_type=std_logic lab=vdd}
C {devices/sg13_lv_nmos_np.sym} 800 -1140 0 0 {name=M6
w=x_dut_xm6_w
l=x_dut_xm6_l
ng=x_dut_xm6_ng
m=x_dut_xm6_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 880 -1100 0 1 {name=l32 sig_type=std_logic lab=vss}
C {devices/sg13_lv_nmos_np.sym} 800 -800 0 0 {name=M4
w=x_dut_xm4_w
l=x_dut_xm4_l
ng=x_dut_xm4_ng
m=x_dut_xm4_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 880 -760 0 1 {name=l34 sig_type=std_logic lab=vss}
C {devices/lab_pin.sym} 320 -1600 0 0 {name=l35 sig_type=std_logic lab=s9}
C {devices/lab_pin.sym} 820 -1600 0 1 {name=l36 sig_type=std_logic lab=s10}
C {devices/lab_pin.sym} 320 -1250 0 0 {name=l37 sig_type=std_logic lab=cascp}
C {devices/lab_pin.sym} 420 -1720 0 1 {name=l38 sig_type=std_logic lab=cascp}
C {devices/lab_pin.sym} 400 -1430 0 1 {name=l39 sig_type=std_logic lab=vb2}
C {devices/lab_pin.sym} 400 -1140 0 1 {name=l40 sig_type=std_logic lab=vb1}
C {devices/lab_pin.sym} 400 -880 0 1 {name=l41 sig_type=std_logic lab=nbias}
C {devices/opin.sym} 1120 -1300 0 0 {name=P6 lab=vout}
C {devices/vsource.sym} 570 -1400 0 0 {name=V2
value=x_dut_vb2
savecurrent=false
}
C {devices/lab_pin.sym} 570 -1340 0 1 {name=l44 sig_type=std_logic lab=vss}
C {devices/vsource.sym} 570 -1110 0 0 {name=V1
value=x_dut_vb1
savecurrent=false
}
C {devices/lab_pin.sym} 570 -1050 0 1 {name=l46 sig_type=std_logic lab=vss}
C {devices/sg13_lv_nmos_np.sym} 570 -800 0 0 {name=M13
w=x_dut_xm13_w
l=x_dut_xm13_l
ng=x_dut_xm13_ng
m=x_dut_xm13_m
model=sg13_lv_nmos
spiceprefix=X
}
C {devices/lab_pin.sym} 650 -760 0 1 {name=l48 sig_type=std_logic lab=vss}
T {amp_004_folded_cascode} -780 -780 0 0 0.8 0.8 {}
T {folded-cascode OTA, IHP SG13G2} -780 -710 0 0 0.45 0.45 {}
T {sizing knobs: x_dut_<dev>_<w|l|ng|m>} -780 -650 0 0 0.35 0.35 {}
