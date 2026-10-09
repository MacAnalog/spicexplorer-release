v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_031_srmc_core_cmfb} -2460 -540 0 0 0.4 0.4 {}
C {blocks/dp_nmos_simple_1.sym} -220 0 0 0 {name=xdp_nmos_simple_1}
C {blocks/dp_pmos_simple_1.sym} 220 0 0 0 {name=xdp_pmos_simple_1}
C {devices/capa_np.sym} -2200 340 0 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} -1980 340 0 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} -1760 340 0 0 {name=CIN1 value='cin_val'}
C {devices/capa_np.sym} -1540 340 0 0 {name=CIN2 value='cin_val'}
C {devices/capa_np.sym} -1320 340 0 0 {name=COUT1 value='cout_val'}
C {devices/capa_np.sym} -1100 340 0 0 {name=COUT2 value='cout_val'}
C {devices/vccs.sym} -880 340 0 0 {name=GM1 value="\{gm_val\}"}
C {devices/vccs.sym} -660 340 0 0 {name=GM2 value="\{gm_val\}"}
C {devices/res_np.sym} -440 340 0 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} -220 340 0 0 {name=R2 value='x_dut_r2_value'}
C {devices/res_np.sym} 0 340 0 0 {name=RIN1 value='rin_val'}
C {devices/res_np.sym} 220 340 0 0 {name=RIN2 value='rin_val'}
C {devices/res_np.sym} 440 340 0 0 {name=RM1N value='x_dut_rm1n_value'}
C {devices/res_np.sym} 660 340 0 0 {name=RM1P value='x_dut_rm1p_value'}
C {devices/res_np.sym} 880 340 0 0 {name=RM2N value='x_dut_rm2n_value'}
C {devices/res_np.sym} 1100 340 0 0 {name=RM2P value='x_dut_rm2p_value'}
C {devices/res_np.sym} 1320 340 0 0 {name=ROUT1 value='rout_val'}
C {devices/res_np.sym} 1540 340 0 0 {name=ROUT2 value='rout_val'}
C {devices/vsource_np.sym} -2420 340 0 0 {name=VB2 value="dc \{vb2\}" savecurrent=false}
C {devices/vsource_np.sym} -2420 120 0 0 {name=VREF1 value="dc \{vref_cm\}" savecurrent=false}
C {devices/vsource_np.sym} -2420 -100 0 0 {name=VREF2 value="dc \{vref_cm\}" savecurrent=false}
C {devices/sg13_lv_nmos_np.sym} 1760 340 0 0 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_pmos_np.sym} -220 -340 0 0 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_pmos_np.sym} 0 -340 0 0 {name=M2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_nmos_np.sym} 1980 340 0 0 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_pmos_np.sym} 220 -340 0 0 {name=M8 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_nmos_np.sym} 2200 340 0 0 {name=M9 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -330 -20 -370 -20 {}
C {devices/lab_wire.sym} -370 -20 0 0 {name=l0 lab=vinn}
N -330 20 -370 20 {}
C {devices/lab_wire.sym} -370 20 0 0 {name=l1 lab=vinp}
N -110 -40 -70 -40 {}
C {devices/lab_wire.sym} -70 -40 0 1 {name=l2 lab=ntail}
N -110 0 -70 0 {}
C {devices/lab_wire.sym} -70 0 0 1 {name=l3 lab=vo1n}
N -110 40 -70 40 {}
C {devices/lab_wire.sym} -70 40 0 1 {name=l4 lab=vo1p}
N -220 100 -220 140 {}
C {devices/lab_wire.sym} -220 140 2 0 {name=l5 lab=vss}
N 110 -20 70 -20 {}
C {devices/lab_wire.sym} 70 -20 0 0 {name=l6 lab=vinn}
N 110 20 70 20 {}
C {devices/lab_wire.sym} 70 20 0 0 {name=l7 lab=vinp}
N 330 -40 370 -40 {}
C {devices/lab_wire.sym} 370 -40 0 1 {name=l8 lab=ptail}
N 330 0 370 0 {}
C {devices/lab_wire.sym} 370 0 0 1 {name=l9 lab=vo1n}
N 330 40 370 40 {}
C {devices/lab_wire.sym} 370 40 0 1 {name=l10 lab=vo1p}
N 220 -100 220 -140 {}
C {devices/lab_wire.sym} 220 -140 0 1 {name=l11 lab=vdd}
N -2200 310 -2200 270 {}
C {devices/lab_wire.sym} -2200 270 0 1 {name=l12 lab=vo1n}
N -2200 370 -2200 410 {}
C {devices/lab_wire.sym} -2200 410 2 0 {name=l13 lab=zc_p}
N -1980 310 -1980 270 {}
C {devices/lab_wire.sym} -1980 270 0 1 {name=l14 lab=vo1p}
N -1980 370 -1980 410 {}
C {devices/lab_wire.sym} -1980 410 2 0 {name=l15 lab=zc_n}
N -1760 310 -1760 270 {}
C {devices/lab_wire.sym} -1760 270 0 1 {name=l16 lab=cm1_det}
N -1760 370 -1760 410 {}
C {devices/lab_wire.sym} -1760 410 2 0 {name=l17 lab=vref_cm1}
N -1540 310 -1540 270 {}
C {devices/lab_wire.sym} -1540 270 0 1 {name=l18 lab=cm2_det}
N -1540 370 -1540 410 {}
C {devices/lab_wire.sym} -1540 410 2 0 {name=l19 lab=vref_cm2}
N -1320 310 -1320 270 {}
C {devices/lab_wire.sym} -1320 270 0 1 {name=l20 lab=vss}
N -1320 370 -1320 410 {}
C {devices/lab_wire.sym} -1320 410 2 0 {name=l21 lab=vcmfb1}
N -1100 310 -1100 270 {}
C {devices/lab_wire.sym} -1100 270 0 1 {name=l22 lab=vss}
N -1100 370 -1100 410 {}
C {devices/lab_wire.sym} -1100 410 2 0 {name=l23 lab=vcmfb2}
N -880 310 -880 270 {}
C {devices/lab_wire.sym} -880 270 0 1 {name=l24 lab=vss}
N -880 370 -880 410 {}
C {devices/lab_wire.sym} -880 410 2 0 {name=l25 lab=vcmfb1}
N -920 320 -960 320 {}
C {devices/lab_wire.sym} -960 320 0 0 {name=l26 lab=cm1_det}
N -920 360 -960 360 {}
C {devices/lab_wire.sym} -960 360 0 0 {name=l27 lab=vref_cm1}
N -660 310 -660 270 {}
C {devices/lab_wire.sym} -660 270 0 1 {name=l28 lab=vss}
N -660 370 -660 410 {}
C {devices/lab_wire.sym} -660 410 2 0 {name=l29 lab=vcmfb2}
N -700 320 -740 320 {}
C {devices/lab_wire.sym} -740 320 0 0 {name=l30 lab=cm2_det}
N -700 360 -740 360 {}
C {devices/lab_wire.sym} -740 360 0 0 {name=l31 lab=vref_cm2}
N -440 310 -440 270 {}
C {devices/lab_wire.sym} -440 270 0 1 {name=l32 lab=zc_p}
N -440 370 -440 410 {}
C {devices/lab_wire.sym} -440 410 2 0 {name=l33 lab=voutp}
N -220 310 -220 270 {}
C {devices/lab_wire.sym} -220 270 0 1 {name=l34 lab=zc_n}
N -220 370 -220 410 {}
C {devices/lab_wire.sym} -220 410 2 0 {name=l35 lab=voutn}
N 0 310 0 270 {}
C {devices/lab_wire.sym} 0 270 0 1 {name=l36 lab=cm1_det}
N 0 370 0 410 {}
C {devices/lab_wire.sym} 0 410 2 0 {name=l37 lab=vref_cm1}
N 220 310 220 270 {}
C {devices/lab_wire.sym} 220 270 0 1 {name=l38 lab=cm2_det}
N 220 370 220 410 {}
C {devices/lab_wire.sym} 220 410 2 0 {name=l39 lab=vref_cm2}
N 440 310 440 270 {}
C {devices/lab_wire.sym} 440 270 0 1 {name=l40 lab=vo1n}
N 440 370 440 410 {}
C {devices/lab_wire.sym} 440 410 2 0 {name=l41 lab=cm1_det}
N 660 310 660 270 {}
C {devices/lab_wire.sym} 660 270 0 1 {name=l42 lab=cm1_det}
N 660 370 660 410 {}
C {devices/lab_wire.sym} 660 410 2 0 {name=l43 lab=vo1p}
N 880 310 880 270 {}
C {devices/lab_wire.sym} 880 270 0 1 {name=l44 lab=voutn}
N 880 370 880 410 {}
C {devices/lab_wire.sym} 880 410 2 0 {name=l45 lab=cm2_det}
N 1100 310 1100 270 {}
C {devices/lab_wire.sym} 1100 270 0 1 {name=l46 lab=cm2_det}
N 1100 370 1100 410 {}
C {devices/lab_wire.sym} 1100 410 2 0 {name=l47 lab=voutp}
N 1320 310 1320 270 {}
C {devices/lab_wire.sym} 1320 270 0 1 {name=l48 lab=vss}
N 1320 370 1320 410 {}
C {devices/lab_wire.sym} 1320 410 2 0 {name=l49 lab=vcmfb1}
N 1540 310 1540 270 {}
C {devices/lab_wire.sym} 1540 270 0 1 {name=l50 lab=vss}
N 1540 370 1540 410 {}
C {devices/lab_wire.sym} 1540 410 2 0 {name=l51 lab=vcmfb2}
N -2420 310 -2420 270 {}
C {devices/lab_wire.sym} -2420 270 0 1 {name=l52 lab=vb2}
N -2420 370 -2420 410 {}
C {devices/lab_wire.sym} -2420 410 2 0 {name=l53 lab=vss}
N -2420 90 -2420 50 {}
C {devices/lab_wire.sym} -2420 50 0 1 {name=l54 lab=vref_cm1}
N -2420 150 -2420 190 {}
C {devices/lab_wire.sym} -2420 190 2 0 {name=l55 lab=vss}
N -2420 -130 -2420 -170 {}
C {devices/lab_wire.sym} -2420 -170 0 1 {name=l56 lab=vref_cm2}
N -2420 -70 -2420 -30 {}
C {devices/lab_wire.sym} -2420 -30 2 0 {name=l57 lab=vss}
N 1780 310 1780 270 {}
C {devices/lab_wire.sym} 1780 270 0 1 {name=l58 lab=voutp}
N 1740 340 1700 340 {}
C {devices/lab_wire.sym} 1700 340 0 0 {name=l59 lab=vo1n}
N 1780 370 1780 410 {}
C {devices/lab_wire.sym} 1780 410 2 0 {name=l60 lab=vss}
N 1780 340 1820 340 {}
C {devices/lab_wire.sym} 1820 340 0 1 {name=l61 lab=vss}
N -200 -310 -200 -270 {}
C {devices/lab_wire.sym} -200 -270 2 0 {name=l62 lab=voutn}
N -240 -340 -280 -340 {}
C {devices/lab_wire.sym} -280 -340 0 0 {name=l63 lab=vcmfb2}
N -200 -370 -200 -410 {}
C {devices/lab_wire.sym} -200 -410 0 1 {name=l64 lab=vdd}
N -200 -340 -160 -340 {}
C {devices/lab_wire.sym} -160 -340 0 1 {name=l65 lab=vdd}
N 20 -310 20 -270 {}
C {devices/lab_wire.sym} 20 -270 2 0 {name=l66 lab=voutp}
N -20 -340 -60 -340 {}
C {devices/lab_wire.sym} -60 -340 0 0 {name=l67 lab=vcmfb2}
N 20 -370 20 -410 {}
C {devices/lab_wire.sym} 20 -410 0 1 {name=l68 lab=vdd}
N 20 -340 60 -340 {}
C {devices/lab_wire.sym} 60 -340 0 1 {name=l69 lab=vdd}
N 2000 310 2000 270 {}
C {devices/lab_wire.sym} 2000 270 0 1 {name=l70 lab=ntail}
N 1960 340 1920 340 {}
C {devices/lab_wire.sym} 1920 340 0 0 {name=l71 lab=vb2}
N 2000 370 2000 410 {}
C {devices/lab_wire.sym} 2000 410 2 0 {name=l72 lab=vss}
N 2000 340 2040 340 {}
C {devices/lab_wire.sym} 2040 340 0 1 {name=l73 lab=vss}
N 240 -310 240 -270 {}
C {devices/lab_wire.sym} 240 -270 2 0 {name=l74 lab=ptail}
N 200 -340 160 -340 {}
C {devices/lab_wire.sym} 160 -340 0 0 {name=l75 lab=vcmfb1}
N 240 -370 240 -410 {}
C {devices/lab_wire.sym} 240 -410 0 1 {name=l76 lab=vdd}
N 240 -340 280 -340 {}
C {devices/lab_wire.sym} 280 -340 0 1 {name=l77 lab=vdd}
N 2220 310 2220 270 {}
C {devices/lab_wire.sym} 2220 270 0 1 {name=l78 lab=voutn}
N 2180 340 2140 340 {}
C {devices/lab_wire.sym} 2140 340 0 0 {name=l79 lab=vo1p}
N 2220 370 2220 410 {}
C {devices/lab_wire.sym} 2220 410 2 0 {name=l80 lab=vss}
N 2220 340 2260 340 {}
C {devices/lab_wire.sym} 2260 340 0 1 {name=l81 lab=vss}
