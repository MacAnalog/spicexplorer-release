v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {sw_003_binary_capbank} -1290 -200 0 0 0.4 0.4 {}
C {blocks/tg_pair_cmos_rail_bulk_1.sym} -1250 0 0 0 {name=xtg_pair_cmos_rail_bulk_1}
C {blocks/tg_pair_cmos_rail_bulk_2.sym} -750 0 0 0 {name=xtg_pair_cmos_rail_bulk_2}
C {blocks/tg_pair_cmos_rail_bulk_3.sym} -250 0 0 0 {name=xtg_pair_cmos_rail_bulk_3}
C {blocks/tg_pair_cmos_rail_bulk_4.sym} 250 0 0 0 {name=xtg_pair_cmos_rail_bulk_4}
C {blocks/tg_pair_cmos_rail_bulk_5.sym} 750 0 0 0 {name=xtg_pair_cmos_rail_bulk_5}
C {blocks/tg_pair_cmos_rail_bulk_6.sym} 1250 0 0 0 {name=xtg_pair_cmos_rail_bulk_6}
C {devices/capa_np.sym} -330 320 0 0 {name=C1 value='Cu' m=x_dut_c1_m}
C {devices/capa_np.sym} -110 320 0 0 {name=C2 value='Cu' m=x_dut_c2_m}
C {devices/capa_np.sym} 110 320 0 0 {name=C3 value='Cu' m=x_dut_c3_m}
C {devices/capa_np.sym} 330 320 0 0 {name=C4 value='Cu' m=x_dut_c4_m}
N -1390 -20 -1430 -20 {}
C {devices/lab_wire.sym} -1430 -20 0 0 {name=l0 lab=V_D0}
N -1390 20 -1430 20 {}
C {devices/lab_wire.sym} -1430 20 0 0 {name=l1 lab=V_D0_NOT}
N -1110 -20 -1070 -20 {}
C {devices/lab_wire.sym} -1070 -20 0 1 {name=l2 lab=bot0}
N -1110 20 -1070 20 {}
C {devices/lab_wire.sym} -1070 20 0 1 {name=l3 lab=vinp}
N -1250 -80 -1250 -120 {}
C {devices/lab_wire.sym} -1250 -120 0 1 {name=l4 lab=VDD}
N -1250 80 -1250 120 {}
C {devices/lab_wire.sym} -1250 120 2 0 {name=l5 lab=VSS}
N -890 -20 -930 -20 {}
C {devices/lab_wire.sym} -930 -20 0 0 {name=l6 lab=V_D2}
N -890 20 -930 20 {}
C {devices/lab_wire.sym} -930 20 0 0 {name=l7 lab=V_D2_NOT}
N -610 -20 -570 -20 {}
C {devices/lab_wire.sym} -570 -20 0 1 {name=l8 lab=bot2}
N -610 20 -570 20 {}
C {devices/lab_wire.sym} -570 20 0 1 {name=l9 lab=vinp}
N -750 -80 -750 -120 {}
C {devices/lab_wire.sym} -750 -120 0 1 {name=l10 lab=VDD}
N -750 80 -750 120 {}
C {devices/lab_wire.sym} -750 120 2 0 {name=l11 lab=VSS}
N -390 -20 -430 -20 {}
C {devices/lab_wire.sym} -430 -20 0 0 {name=l12 lab=V_D2}
N -390 20 -430 20 {}
C {devices/lab_wire.sym} -430 20 0 0 {name=l13 lab=V_D2_NOT}
N -110 -20 -70 -20 {}
C {devices/lab_wire.sym} -70 -20 0 1 {name=l14 lab=VCM}
N -110 20 -70 20 {}
C {devices/lab_wire.sym} -70 20 0 1 {name=l15 lab=bot2}
N -250 -80 -250 -120 {}
C {devices/lab_wire.sym} -250 -120 0 1 {name=l16 lab=VDD}
N -250 80 -250 120 {}
C {devices/lab_wire.sym} -250 120 2 0 {name=l17 lab=VSS}
N 110 -20 70 -20 {}
C {devices/lab_wire.sym} 70 -20 0 0 {name=l18 lab=V_D0}
N 110 20 70 20 {}
C {devices/lab_wire.sym} 70 20 0 0 {name=l19 lab=V_D0_NOT}
N 390 -20 430 -20 {}
C {devices/lab_wire.sym} 430 -20 0 1 {name=l20 lab=VCM}
N 390 20 430 20 {}
C {devices/lab_wire.sym} 430 20 0 1 {name=l21 lab=bot0}
N 250 -80 250 -120 {}
C {devices/lab_wire.sym} 250 -120 0 1 {name=l22 lab=VDD}
N 250 80 250 120 {}
C {devices/lab_wire.sym} 250 120 2 0 {name=l23 lab=VSS}
N 610 -20 570 -20 {}
C {devices/lab_wire.sym} 570 -20 0 0 {name=l24 lab=V_D1}
N 610 20 570 20 {}
C {devices/lab_wire.sym} 570 20 0 0 {name=l25 lab=V_D1_NOT}
N 890 -20 930 -20 {}
C {devices/lab_wire.sym} 930 -20 0 1 {name=l26 lab=bot1}
N 890 20 930 20 {}
C {devices/lab_wire.sym} 930 20 0 1 {name=l27 lab=vinp}
N 750 -80 750 -120 {}
C {devices/lab_wire.sym} 750 -120 0 1 {name=l28 lab=VDD}
N 750 80 750 120 {}
C {devices/lab_wire.sym} 750 120 2 0 {name=l29 lab=VSS}
N 1110 -20 1070 -20 {}
C {devices/lab_wire.sym} 1070 -20 0 0 {name=l30 lab=V_D1}
N 1110 20 1070 20 {}
C {devices/lab_wire.sym} 1070 20 0 0 {name=l31 lab=V_D1_NOT}
N 1390 -20 1430 -20 {}
C {devices/lab_wire.sym} 1430 -20 0 1 {name=l32 lab=VCM}
N 1390 20 1430 20 {}
C {devices/lab_wire.sym} 1430 20 0 1 {name=l33 lab=bot1}
N 1250 -80 1250 -120 {}
C {devices/lab_wire.sym} 1250 -120 0 1 {name=l34 lab=VDD}
N 1250 80 1250 120 {}
C {devices/lab_wire.sym} 1250 120 2 0 {name=l35 lab=VSS}
N -330 290 -330 250 {}
C {devices/lab_wire.sym} -330 250 0 1 {name=l36 lab=vout}
N -330 350 -330 390 {}
C {devices/lab_wire.sym} -330 390 2 0 {name=l37 lab=vinp}
N -110 290 -110 250 {}
C {devices/lab_wire.sym} -110 250 0 1 {name=l38 lab=vout}
N -110 350 -110 390 {}
C {devices/lab_wire.sym} -110 390 2 0 {name=l39 lab=bot0}
N 110 290 110 250 {}
C {devices/lab_wire.sym} 110 250 0 1 {name=l40 lab=vout}
N 110 350 110 390 {}
C {devices/lab_wire.sym} 110 390 2 0 {name=l41 lab=bot1}
N 330 290 330 250 {}
C {devices/lab_wire.sym} 330 250 0 1 {name=l42 lab=vout}
N 330 350 330 390 {}
C {devices/lab_wire.sym} 330 390 2 0 {name=l43 lab=bot2}
