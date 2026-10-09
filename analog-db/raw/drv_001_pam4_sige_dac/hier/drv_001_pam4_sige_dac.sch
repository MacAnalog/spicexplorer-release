v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {drv_001_pam4_sige_dac} -3010 -500 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -2970 300 0 0 {name=CDEGL0 value="\{x_dut_cdeg_ff*1f\}"}
C {devices/capa_np.sym} -2750 300 0 0 {name=CDEGM0 value="\{x_dut_cdeg_ff*1f\}"}
C {devices/capa_np.sym} -2530 300 0 0 {name=CDEGM1 value="\{x_dut_cdeg_ff*1f\}"}
C {devices/vccs.sym} -2310 300 0 0 {name=GTAILL0 value=1m}
C {devices/vccs.sym} -2090 300 0 0 {name=GTAILM0 value=1m}
C {devices/vccs.sym} -1870 300 0 0 {name=GTAILM1 value=1m}
C {devices/res_np.sym} -1650 300 0 0 {name=RBLSBN value="\{x_dut_rb\}"}
C {devices/res_np.sym} -1430 300 0 0 {name=RBLSBP value="\{x_dut_rb\}"}
C {devices/res_np.sym} -1210 300 0 0 {name=RBMSBN value="\{x_dut_rb\}"}
C {devices/res_np.sym} -990 300 0 0 {name=RBMSBP value="\{x_dut_rb\}"}
C {devices/res_np.sym} -110 -300 0 0 {name=RCN value="\{x_dut_rc\}"}
C {devices/res_np.sym} 110 -300 0 0 {name=RCP value="\{x_dut_rc\}"}
C {devices/res_np.sym} -770 300 0 0 {name=RE1L0 value="\{x_dut_re\}"}
C {devices/res_np.sym} -550 300 0 0 {name=RE1M0 value="\{x_dut_re\}"}
C {devices/res_np.sym} -330 300 0 0 {name=RE1M1 value="\{x_dut_re\}"}
C {devices/res_np.sym} -110 300 0 0 {name=RE2L0 value="\{x_dut_re\}"}
C {devices/res_np.sym} 110 300 0 0 {name=RE2M0 value="\{x_dut_re\}"}
C {devices/res_np.sym} 330 300 0 0 {name=RE2M1 value="\{x_dut_re\}"}
C {sg13g2_pr/npn13G2.sym} 550 300 0 0 {name=Q1L0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 770 300 0 0 {name=Q1M0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 990 300 0 0 {name=Q1M1 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 1210 300 0 0 {name=Q2L0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 1430 300 0 0 {name=Q2M0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 1650 300 0 0 {name=Q2M1 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 1870 300 0 0 {name=Q3L0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 2090 300 0 0 {name=Q3M0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 2310 300 0 0 {name=Q3M1 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 2530 300 0 0 {name=Q4L0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 2750 300 0 0 {name=Q4M0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 2970 300 0 0 {name=Q4M1 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
N -2970 270 -2970 230 {}
C {devices/lab_wire.sym} -2970 230 0 1 {name=l0 lab=e1L0}
N -2970 330 -2970 370 {}
C {devices/lab_wire.sym} -2970 370 2 0 {name=l1 lab=e2L0}
N -2750 270 -2750 230 {}
C {devices/lab_wire.sym} -2750 230 0 1 {name=l2 lab=e1M0}
N -2750 330 -2750 370 {}
C {devices/lab_wire.sym} -2750 370 2 0 {name=l3 lab=e2M0}
N -2530 270 -2530 230 {}
C {devices/lab_wire.sym} -2530 230 0 1 {name=l4 lab=e1M1}
N -2530 330 -2530 370 {}
C {devices/lab_wire.sym} -2530 370 2 0 {name=l5 lab=e2M1}
N -2310 270 -2310 230 {}
C {devices/lab_wire.sym} -2310 230 0 1 {name=l6 lab=tlsb0}
N -2310 330 -2310 370 {}
C {devices/lab_wire.sym} -2310 370 2 0 {name=l7 lab=0}
N -2350 280 -2390 280 {}
C {devices/lab_wire.sym} -2390 280 0 0 {name=l8 lab=blsb}
N -2350 320 -2390 320 {}
C {devices/lab_wire.sym} -2390 320 0 0 {name=l9 lab=0}
N -2090 270 -2090 230 {}
C {devices/lab_wire.sym} -2090 230 0 1 {name=l10 lab=tmsb0}
N -2090 330 -2090 370 {}
C {devices/lab_wire.sym} -2090 370 2 0 {name=l11 lab=0}
N -2130 280 -2170 280 {}
C {devices/lab_wire.sym} -2170 280 0 0 {name=l12 lab=bmsb}
N -2130 320 -2170 320 {}
C {devices/lab_wire.sym} -2170 320 0 0 {name=l13 lab=0}
N -1870 270 -1870 230 {}
C {devices/lab_wire.sym} -1870 230 0 1 {name=l14 lab=tmsb1}
N -1870 330 -1870 370 {}
C {devices/lab_wire.sym} -1870 370 2 0 {name=l15 lab=0}
N -1910 280 -1950 280 {}
C {devices/lab_wire.sym} -1950 280 0 0 {name=l16 lab=bmsb}
N -1910 320 -1950 320 {}
C {devices/lab_wire.sym} -1950 320 0 0 {name=l17 lab=0}
N -1650 270 -1650 230 {}
C {devices/lab_wire.sym} -1650 230 0 1 {name=l18 lab=lsbn}
N -1650 330 -1650 370 {}
C {devices/lab_wire.sym} -1650 370 2 0 {name=l19 lab=vcmb}
N -1430 270 -1430 230 {}
C {devices/lab_wire.sym} -1430 230 0 1 {name=l20 lab=lsbp}
N -1430 330 -1430 370 {}
C {devices/lab_wire.sym} -1430 370 2 0 {name=l21 lab=vcmb}
N -1210 270 -1210 230 {}
C {devices/lab_wire.sym} -1210 230 0 1 {name=l22 lab=msbn}
N -1210 330 -1210 370 {}
C {devices/lab_wire.sym} -1210 370 2 0 {name=l23 lab=vcmb}
N -990 270 -990 230 {}
C {devices/lab_wire.sym} -990 230 0 1 {name=l24 lab=msbp}
N -990 330 -990 370 {}
C {devices/lab_wire.sym} -990 370 2 0 {name=l25 lab=vcmb}
N -110 -330 -110 -370 {}
C {devices/lab_wire.sym} -110 -370 0 1 {name=l26 lab=outn}
N -110 -270 -110 -230 {}
C {devices/lab_wire.sym} -110 -230 2 0 {name=l27 lab=vcc}
N 110 -330 110 -370 {}
C {devices/lab_wire.sym} 110 -370 0 1 {name=l28 lab=outp}
N 110 -270 110 -230 {}
C {devices/lab_wire.sym} 110 -230 2 0 {name=l29 lab=vcc}
N -770 270 -770 230 {}
C {devices/lab_wire.sym} -770 230 0 1 {name=l30 lab=e1L0}
N -770 330 -770 370 {}
C {devices/lab_wire.sym} -770 370 2 0 {name=l31 lab=tlsb0}
N -550 270 -550 230 {}
C {devices/lab_wire.sym} -550 230 0 1 {name=l32 lab=e1M0}
N -550 330 -550 370 {}
C {devices/lab_wire.sym} -550 370 2 0 {name=l33 lab=tmsb0}
N -330 270 -330 230 {}
C {devices/lab_wire.sym} -330 230 0 1 {name=l34 lab=e1M1}
N -330 330 -330 370 {}
C {devices/lab_wire.sym} -330 370 2 0 {name=l35 lab=tmsb1}
N -110 270 -110 230 {}
C {devices/lab_wire.sym} -110 230 0 1 {name=l36 lab=e2L0}
N -110 330 -110 370 {}
C {devices/lab_wire.sym} -110 370 2 0 {name=l37 lab=tlsb0}
N 110 270 110 230 {}
C {devices/lab_wire.sym} 110 230 0 1 {name=l38 lab=e2M0}
N 110 330 110 370 {}
C {devices/lab_wire.sym} 110 370 2 0 {name=l39 lab=tmsb0}
N 330 270 330 230 {}
C {devices/lab_wire.sym} 330 230 0 1 {name=l40 lab=e2M1}
N 330 330 330 370 {}
C {devices/lab_wire.sym} 330 370 2 0 {name=l41 lab=tmsb1}
N 570 270 570 230 {}
C {devices/lab_wire.sym} 570 230 0 1 {name=l42 lab=c1L0}
N 530 300 490 300 {}
C {devices/lab_wire.sym} 490 300 0 0 {name=l43 lab=lsbp}
N 570 330 570 370 {}
C {devices/lab_wire.sym} 570 370 2 0 {name=l44 lab=e1L0}
N 570 300 610 300 {}
C {devices/lab_wire.sym} 610 300 0 1 {name=l45 lab=0}
N 790 270 790 230 {}
C {devices/lab_wire.sym} 790 230 0 1 {name=l46 lab=c1M0}
N 750 300 710 300 {}
C {devices/lab_wire.sym} 710 300 0 0 {name=l47 lab=msbp}
N 790 330 790 370 {}
C {devices/lab_wire.sym} 790 370 2 0 {name=l48 lab=e1M0}
N 790 300 830 300 {}
C {devices/lab_wire.sym} 830 300 0 1 {name=l49 lab=0}
N 1010 270 1010 230 {}
C {devices/lab_wire.sym} 1010 230 0 1 {name=l50 lab=c1M1}
N 970 300 930 300 {}
C {devices/lab_wire.sym} 930 300 0 0 {name=l51 lab=msbp}
N 1010 330 1010 370 {}
C {devices/lab_wire.sym} 1010 370 2 0 {name=l52 lab=e1M1}
N 1010 300 1050 300 {}
C {devices/lab_wire.sym} 1050 300 0 1 {name=l53 lab=0}
N 1230 270 1230 230 {}
C {devices/lab_wire.sym} 1230 230 0 1 {name=l54 lab=c2L0}
N 1190 300 1150 300 {}
C {devices/lab_wire.sym} 1150 300 0 0 {name=l55 lab=lsbn}
N 1230 330 1230 370 {}
C {devices/lab_wire.sym} 1230 370 2 0 {name=l56 lab=e2L0}
N 1230 300 1270 300 {}
C {devices/lab_wire.sym} 1270 300 0 1 {name=l57 lab=0}
N 1450 270 1450 230 {}
C {devices/lab_wire.sym} 1450 230 0 1 {name=l58 lab=c2M0}
N 1410 300 1370 300 {}
C {devices/lab_wire.sym} 1370 300 0 0 {name=l59 lab=msbn}
N 1450 330 1450 370 {}
C {devices/lab_wire.sym} 1450 370 2 0 {name=l60 lab=e2M0}
N 1450 300 1490 300 {}
C {devices/lab_wire.sym} 1490 300 0 1 {name=l61 lab=0}
N 1670 270 1670 230 {}
C {devices/lab_wire.sym} 1670 230 0 1 {name=l62 lab=c2M1}
N 1630 300 1590 300 {}
C {devices/lab_wire.sym} 1590 300 0 0 {name=l63 lab=msbn}
N 1670 330 1670 370 {}
C {devices/lab_wire.sym} 1670 370 2 0 {name=l64 lab=e2M1}
N 1670 300 1710 300 {}
C {devices/lab_wire.sym} 1710 300 0 1 {name=l65 lab=0}
N 1890 270 1890 230 {}
C {devices/lab_wire.sym} 1890 230 0 1 {name=l66 lab=outp}
N 1850 300 1810 300 {}
C {devices/lab_wire.sym} 1810 300 0 0 {name=l67 lab=vcasc}
N 1890 330 1890 370 {}
C {devices/lab_wire.sym} 1890 370 2 0 {name=l68 lab=c1L0}
N 1890 300 1930 300 {}
C {devices/lab_wire.sym} 1930 300 0 1 {name=l69 lab=0}
N 2110 270 2110 230 {}
C {devices/lab_wire.sym} 2110 230 0 1 {name=l70 lab=outp}
N 2070 300 2030 300 {}
C {devices/lab_wire.sym} 2030 300 0 0 {name=l71 lab=vcasc}
N 2110 330 2110 370 {}
C {devices/lab_wire.sym} 2110 370 2 0 {name=l72 lab=c1M0}
N 2110 300 2150 300 {}
C {devices/lab_wire.sym} 2150 300 0 1 {name=l73 lab=0}
N 2330 270 2330 230 {}
C {devices/lab_wire.sym} 2330 230 0 1 {name=l74 lab=outp}
N 2290 300 2250 300 {}
C {devices/lab_wire.sym} 2250 300 0 0 {name=l75 lab=vcasc}
N 2330 330 2330 370 {}
C {devices/lab_wire.sym} 2330 370 2 0 {name=l76 lab=c1M1}
N 2330 300 2370 300 {}
C {devices/lab_wire.sym} 2370 300 0 1 {name=l77 lab=0}
N 2550 270 2550 230 {}
C {devices/lab_wire.sym} 2550 230 0 1 {name=l78 lab=outn}
N 2510 300 2470 300 {}
C {devices/lab_wire.sym} 2470 300 0 0 {name=l79 lab=vcasc}
N 2550 330 2550 370 {}
C {devices/lab_wire.sym} 2550 370 2 0 {name=l80 lab=c2L0}
N 2550 300 2590 300 {}
C {devices/lab_wire.sym} 2590 300 0 1 {name=l81 lab=0}
N 2770 270 2770 230 {}
C {devices/lab_wire.sym} 2770 230 0 1 {name=l82 lab=outn}
N 2730 300 2690 300 {}
C {devices/lab_wire.sym} 2690 300 0 0 {name=l83 lab=vcasc}
N 2770 330 2770 370 {}
C {devices/lab_wire.sym} 2770 370 2 0 {name=l84 lab=c2M0}
N 2770 300 2810 300 {}
C {devices/lab_wire.sym} 2810 300 0 1 {name=l85 lab=0}
N 2990 270 2990 230 {}
C {devices/lab_wire.sym} 2990 230 0 1 {name=l86 lab=outn}
N 2950 300 2910 300 {}
C {devices/lab_wire.sym} 2910 300 0 0 {name=l87 lab=vcasc}
N 2990 330 2990 370 {}
C {devices/lab_wire.sym} 2990 370 2 0 {name=l88 lab=c2M1}
N 2990 300 3030 300 {}
C {devices/lab_wire.sym} 3030 300 0 1 {name=l89 lab=0}
