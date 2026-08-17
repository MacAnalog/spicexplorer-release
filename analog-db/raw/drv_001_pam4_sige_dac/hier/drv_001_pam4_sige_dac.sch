v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {drv_001_pam4_sige_dac} -2680 -500 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -2640 300 0 0 {name=CDEGL0 value={x_dut_cdeg_ff*1f}}
C {devices/capa_np.sym} -2420 300 0 0 {name=CDEGM0 value={x_dut_cdeg_ff*1f}}
C {devices/capa_np.sym} -2200 300 0 0 {name=CDEGM1 value={x_dut_cdeg_ff*1f}}
C {devices/res_np.sym} -1980 300 0 0 {name=RBLSBN value={x_dut_rb}}
C {devices/res_np.sym} -1760 300 0 0 {name=RBLSBP value={x_dut_rb}}
C {devices/res_np.sym} -1540 300 0 0 {name=RBMSBN value={x_dut_rb}}
C {devices/res_np.sym} -1320 300 0 0 {name=RBMSBP value={x_dut_rb}}
C {devices/res_np.sym} -110 -300 0 0 {name=RCN value={x_dut_rc}}
C {devices/res_np.sym} 110 -300 0 0 {name=RCP value={x_dut_rc}}
C {devices/res_np.sym} -1100 300 0 0 {name=RE1L0 value={x_dut_re}}
C {devices/res_np.sym} -880 300 0 0 {name=RE1M0 value={x_dut_re}}
C {devices/res_np.sym} -660 300 0 0 {name=RE1M1 value={x_dut_re}}
C {devices/res_np.sym} -440 300 0 0 {name=RE2L0 value={x_dut_re}}
C {devices/res_np.sym} -220 300 0 0 {name=RE2M0 value={x_dut_re}}
C {devices/res_np.sym} 0 300 0 0 {name=RE2M1 value={x_dut_re}}
C {sg13g2_pr/npn13G2.sym} 220 300 0 0 {name=Q1L0 value=npn13G2}
C {sg13g2_pr/npn13G2.sym} 440 300 0 0 {name=Q1M0 value=npn13G2}
C {sg13g2_pr/npn13G2.sym} 660 300 0 0 {name=Q1M1 value=npn13G2}
C {sg13g2_pr/npn13G2.sym} 880 300 0 0 {name=Q2L0 value=npn13G2}
C {sg13g2_pr/npn13G2.sym} 1100 300 0 0 {name=Q2M0 value=npn13G2}
C {sg13g2_pr/npn13G2.sym} 1320 300 0 0 {name=Q2M1 value=npn13G2}
C {sg13g2_pr/npn13G2.sym} 1540 300 0 0 {name=Q3L0 value=npn13G2}
C {sg13g2_pr/npn13G2.sym} 1760 300 0 0 {name=Q3M0 value=npn13G2}
C {sg13g2_pr/npn13G2.sym} 1980 300 0 0 {name=Q3M1 value=npn13G2}
C {sg13g2_pr/npn13G2.sym} 2200 300 0 0 {name=Q4L0 value=npn13G2}
C {sg13g2_pr/npn13G2.sym} 2420 300 0 0 {name=Q4M0 value=npn13G2}
C {sg13g2_pr/npn13G2.sym} 2640 300 0 0 {name=Q4M1 value=npn13G2}
N -2640 270 -2640 230 {}
C {devices/lab_wire.sym} -2640 230 0 1 {name=l0 lab=e1L0}
N -2640 330 -2640 370 {}
C {devices/lab_wire.sym} -2640 370 2 0 {name=l1 lab=e2L0}
N -2420 270 -2420 230 {}
C {devices/lab_wire.sym} -2420 230 0 1 {name=l2 lab=e1M0}
N -2420 330 -2420 370 {}
C {devices/lab_wire.sym} -2420 370 2 0 {name=l3 lab=e2M0}
N -2200 270 -2200 230 {}
C {devices/lab_wire.sym} -2200 230 0 1 {name=l4 lab=e1M1}
N -2200 330 -2200 370 {}
C {devices/lab_wire.sym} -2200 370 2 0 {name=l5 lab=e2M1}
N -1980 270 -1980 230 {}
C {devices/lab_wire.sym} -1980 230 0 1 {name=l6 lab=lsbn}
N -1980 330 -1980 370 {}
C {devices/lab_wire.sym} -1980 370 2 0 {name=l7 lab=vcmb}
N -1760 270 -1760 230 {}
C {devices/lab_wire.sym} -1760 230 0 1 {name=l8 lab=lsbp}
N -1760 330 -1760 370 {}
C {devices/lab_wire.sym} -1760 370 2 0 {name=l9 lab=vcmb}
N -1540 270 -1540 230 {}
C {devices/lab_wire.sym} -1540 230 0 1 {name=l10 lab=msbn}
N -1540 330 -1540 370 {}
C {devices/lab_wire.sym} -1540 370 2 0 {name=l11 lab=vcmb}
N -1320 270 -1320 230 {}
C {devices/lab_wire.sym} -1320 230 0 1 {name=l12 lab=msbp}
N -1320 330 -1320 370 {}
C {devices/lab_wire.sym} -1320 370 2 0 {name=l13 lab=vcmb}
N -110 -330 -110 -370 {}
C {devices/lab_wire.sym} -110 -370 0 1 {name=l14 lab=outn}
N -110 -270 -110 -230 {}
C {devices/lab_wire.sym} -110 -230 2 0 {name=l15 lab=vcc}
N 110 -330 110 -370 {}
C {devices/lab_wire.sym} 110 -370 0 1 {name=l16 lab=outp}
N 110 -270 110 -230 {}
C {devices/lab_wire.sym} 110 -230 2 0 {name=l17 lab=vcc}
N -1100 270 -1100 230 {}
C {devices/lab_wire.sym} -1100 230 0 1 {name=l18 lab=e1L0}
N -1100 330 -1100 370 {}
C {devices/lab_wire.sym} -1100 370 2 0 {name=l19 lab=tlsb0}
N -880 270 -880 230 {}
C {devices/lab_wire.sym} -880 230 0 1 {name=l20 lab=e1M0}
N -880 330 -880 370 {}
C {devices/lab_wire.sym} -880 370 2 0 {name=l21 lab=tmsb0}
N -660 270 -660 230 {}
C {devices/lab_wire.sym} -660 230 0 1 {name=l22 lab=e1M1}
N -660 330 -660 370 {}
C {devices/lab_wire.sym} -660 370 2 0 {name=l23 lab=tmsb1}
N -440 270 -440 230 {}
C {devices/lab_wire.sym} -440 230 0 1 {name=l24 lab=e2L0}
N -440 330 -440 370 {}
C {devices/lab_wire.sym} -440 370 2 0 {name=l25 lab=tlsb0}
N -220 270 -220 230 {}
C {devices/lab_wire.sym} -220 230 0 1 {name=l26 lab=e2M0}
N -220 330 -220 370 {}
C {devices/lab_wire.sym} -220 370 2 0 {name=l27 lab=tmsb0}
N 0 270 0 230 {}
C {devices/lab_wire.sym} 0 230 0 1 {name=l28 lab=e2M1}
N 0 330 0 370 {}
C {devices/lab_wire.sym} 0 370 2 0 {name=l29 lab=tmsb1}
N 240 270 240 230 {}
C {devices/lab_wire.sym} 240 230 0 1 {name=l30 lab=c1L0}
N 200 300 160 300 {}
C {devices/lab_wire.sym} 160 300 0 0 {name=l31 lab=lsbp}
N 240 330 240 370 {}
C {devices/lab_wire.sym} 240 370 2 0 {name=l32 lab=e1L0}
N 240 300 280 300 {}
C {devices/lab_wire.sym} 280 300 0 1 {name=l33 lab=0}
N 460 270 460 230 {}
C {devices/lab_wire.sym} 460 230 0 1 {name=l34 lab=c1M0}
N 420 300 380 300 {}
C {devices/lab_wire.sym} 380 300 0 0 {name=l35 lab=msbp}
N 460 330 460 370 {}
C {devices/lab_wire.sym} 460 370 2 0 {name=l36 lab=e1M0}
N 460 300 500 300 {}
C {devices/lab_wire.sym} 500 300 0 1 {name=l37 lab=0}
N 680 270 680 230 {}
C {devices/lab_wire.sym} 680 230 0 1 {name=l38 lab=c1M1}
N 640 300 600 300 {}
C {devices/lab_wire.sym} 600 300 0 0 {name=l39 lab=msbp}
N 680 330 680 370 {}
C {devices/lab_wire.sym} 680 370 2 0 {name=l40 lab=e1M1}
N 680 300 720 300 {}
C {devices/lab_wire.sym} 720 300 0 1 {name=l41 lab=0}
N 900 270 900 230 {}
C {devices/lab_wire.sym} 900 230 0 1 {name=l42 lab=c2L0}
N 860 300 820 300 {}
C {devices/lab_wire.sym} 820 300 0 0 {name=l43 lab=lsbn}
N 900 330 900 370 {}
C {devices/lab_wire.sym} 900 370 2 0 {name=l44 lab=e2L0}
N 900 300 940 300 {}
C {devices/lab_wire.sym} 940 300 0 1 {name=l45 lab=0}
N 1120 270 1120 230 {}
C {devices/lab_wire.sym} 1120 230 0 1 {name=l46 lab=c2M0}
N 1080 300 1040 300 {}
C {devices/lab_wire.sym} 1040 300 0 0 {name=l47 lab=msbn}
N 1120 330 1120 370 {}
C {devices/lab_wire.sym} 1120 370 2 0 {name=l48 lab=e2M0}
N 1120 300 1160 300 {}
C {devices/lab_wire.sym} 1160 300 0 1 {name=l49 lab=0}
N 1340 270 1340 230 {}
C {devices/lab_wire.sym} 1340 230 0 1 {name=l50 lab=c2M1}
N 1300 300 1260 300 {}
C {devices/lab_wire.sym} 1260 300 0 0 {name=l51 lab=msbn}
N 1340 330 1340 370 {}
C {devices/lab_wire.sym} 1340 370 2 0 {name=l52 lab=e2M1}
N 1340 300 1380 300 {}
C {devices/lab_wire.sym} 1380 300 0 1 {name=l53 lab=0}
N 1560 270 1560 230 {}
C {devices/lab_wire.sym} 1560 230 0 1 {name=l54 lab=outp}
N 1520 300 1480 300 {}
C {devices/lab_wire.sym} 1480 300 0 0 {name=l55 lab=vcasc}
N 1560 330 1560 370 {}
C {devices/lab_wire.sym} 1560 370 2 0 {name=l56 lab=c1L0}
N 1560 300 1600 300 {}
C {devices/lab_wire.sym} 1600 300 0 1 {name=l57 lab=0}
N 1780 270 1780 230 {}
C {devices/lab_wire.sym} 1780 230 0 1 {name=l58 lab=outp}
N 1740 300 1700 300 {}
C {devices/lab_wire.sym} 1700 300 0 0 {name=l59 lab=vcasc}
N 1780 330 1780 370 {}
C {devices/lab_wire.sym} 1780 370 2 0 {name=l60 lab=c1M0}
N 1780 300 1820 300 {}
C {devices/lab_wire.sym} 1820 300 0 1 {name=l61 lab=0}
N 2000 270 2000 230 {}
C {devices/lab_wire.sym} 2000 230 0 1 {name=l62 lab=outp}
N 1960 300 1920 300 {}
C {devices/lab_wire.sym} 1920 300 0 0 {name=l63 lab=vcasc}
N 2000 330 2000 370 {}
C {devices/lab_wire.sym} 2000 370 2 0 {name=l64 lab=c1M1}
N 2000 300 2040 300 {}
C {devices/lab_wire.sym} 2040 300 0 1 {name=l65 lab=0}
N 2220 270 2220 230 {}
C {devices/lab_wire.sym} 2220 230 0 1 {name=l66 lab=outn}
N 2180 300 2140 300 {}
C {devices/lab_wire.sym} 2140 300 0 0 {name=l67 lab=vcasc}
N 2220 330 2220 370 {}
C {devices/lab_wire.sym} 2220 370 2 0 {name=l68 lab=c2L0}
N 2220 300 2260 300 {}
C {devices/lab_wire.sym} 2260 300 0 1 {name=l69 lab=0}
N 2440 270 2440 230 {}
C {devices/lab_wire.sym} 2440 230 0 1 {name=l70 lab=outn}
N 2400 300 2360 300 {}
C {devices/lab_wire.sym} 2360 300 0 0 {name=l71 lab=vcasc}
N 2440 330 2440 370 {}
C {devices/lab_wire.sym} 2440 370 2 0 {name=l72 lab=c2M0}
N 2440 300 2480 300 {}
C {devices/lab_wire.sym} 2480 300 0 1 {name=l73 lab=0}
N 2660 270 2660 230 {}
C {devices/lab_wire.sym} 2660 230 0 1 {name=l74 lab=outn}
N 2620 300 2580 300 {}
C {devices/lab_wire.sym} 2580 300 0 0 {name=l75 lab=vcasc}
N 2660 330 2660 370 {}
C {devices/lab_wire.sym} 2660 370 2 0 {name=l76 lab=c2M1}
N 2660 300 2700 300 {}
C {devices/lab_wire.sym} 2700 300 0 1 {name=l77 lab=0}
