v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cmfb_004_output_switched_cap} -1790 -200 0 0 0.4 0.4 {}
C {blocks/tg_pair_cmos_rail_bulk_1.sym} -1750 0 0 0 {name=xtg_pair_cmos_rail_bulk_1}
C {blocks/tg_pair_cmos_rail_bulk_2.sym} -1250 0 0 0 {name=xtg_pair_cmos_rail_bulk_2}
C {blocks/tg_pair_cmos_rail_bulk_3.sym} -750 0 0 0 {name=xtg_pair_cmos_rail_bulk_3}
C {blocks/tg_pair_cmos_rail_bulk_4.sym} -250 0 0 0 {name=xtg_pair_cmos_rail_bulk_4}
C {blocks/tg_pair_cmos_rail_bulk_5.sym} 250 0 0 0 {name=xtg_pair_cmos_rail_bulk_5}
C {blocks/tg_pair_cmos_rail_bulk_6.sym} 750 0 0 0 {name=xtg_pair_cmos_rail_bulk_6}
C {blocks/tg_pair_cmos_rail_bulk_7.sym} 1250 0 0 0 {name=xtg_pair_cmos_rail_bulk_7}
C {blocks/tg_pair_cmos_rail_bulk_8.sym} 1750 0 0 0 {name=xtg_pair_cmos_rail_bulk_8}
C {devices/capa_np.sym} -330 320 0 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} -110 320 0 0 {name=C2 value='x_dut_c2_value'}
C {devices/capa_np.sym} 110 320 0 0 {name=C3 value='x_dut_c3_value'}
C {devices/capa_np.sym} 330 320 0 0 {name=C4 value='x_dut_c4_value'}
N -1890 -20 -1930 -20 {}
C {devices/lab_wire.sym} -1930 -20 0 0 {name=l0 lab=clk_phi}
N -1890 20 -1930 20 {}
C {devices/lab_wire.sym} -1930 20 0 0 {name=l1 lab=clk_phi_not}
N -1610 -20 -1570 -20 {}
C {devices/lab_wire.sym} -1570 -20 0 1 {name=l2 lab=sense_p}
N -1610 20 -1570 20 {}
C {devices/lab_wire.sym} -1570 20 0 1 {name=l3 lab=vcm}
N -1750 -80 -1750 -120 {}
C {devices/lab_wire.sym} -1750 -120 0 1 {name=l4 lab=vdd}
N -1750 80 -1750 120 {}
C {devices/lab_wire.sym} -1750 120 2 0 {name=l5 lab=vss}
N -1390 -20 -1430 -20 {}
C {devices/lab_wire.sym} -1430 -20 0 0 {name=l6 lab=clk_phi}
N -1390 20 -1430 20 {}
C {devices/lab_wire.sym} -1430 20 0 0 {name=l7 lab=clk_phi_not}
N -1110 -20 -1070 -20 {}
C {devices/lab_wire.sym} -1070 -20 0 1 {name=l8 lab=sense_n}
N -1110 20 -1070 20 {}
C {devices/lab_wire.sym} -1070 20 0 1 {name=l9 lab=vcm}
N -1250 -80 -1250 -120 {}
C {devices/lab_wire.sym} -1250 -120 0 1 {name=l10 lab=vdd}
N -1250 80 -1250 120 {}
C {devices/lab_wire.sym} -1250 120 2 0 {name=l11 lab=vss}
N -890 -20 -930 -20 {}
C {devices/lab_wire.sym} -930 -20 0 0 {name=l12 lab=clk_phi}
N -890 20 -930 20 {}
C {devices/lab_wire.sym} -930 20 0 0 {name=l13 lab=clk_phi_not}
N -610 -20 -570 -20 {}
C {devices/lab_wire.sym} -570 -20 0 1 {name=l14 lab=ctl_n}
N -610 20 -570 20 {}
C {devices/lab_wire.sym} -570 20 0 1 {name=l15 lab=vbias}
N -750 -80 -750 -120 {}
C {devices/lab_wire.sym} -750 -120 0 1 {name=l16 lab=vdd}
N -750 80 -750 120 {}
C {devices/lab_wire.sym} -750 120 2 0 {name=l17 lab=vss}
N -390 -20 -430 -20 {}
C {devices/lab_wire.sym} -430 -20 0 0 {name=l18 lab=clk_phi}
N -390 20 -430 20 {}
C {devices/lab_wire.sym} -430 20 0 0 {name=l19 lab=clk_phi_not}
N -110 -20 -70 -20 {}
C {devices/lab_wire.sym} -70 -20 0 1 {name=l20 lab=sense_n}
N -110 20 -70 20 {}
C {devices/lab_wire.sym} -70 20 0 1 {name=l21 lab=vinn}
N -250 -80 -250 -120 {}
C {devices/lab_wire.sym} -250 -120 0 1 {name=l22 lab=vdd}
N -250 80 -250 120 {}
C {devices/lab_wire.sym} -250 120 2 0 {name=l23 lab=vss}
N 110 -20 70 -20 {}
C {devices/lab_wire.sym} 70 -20 0 0 {name=l24 lab=clk_phi}
N 110 20 70 20 {}
C {devices/lab_wire.sym} 70 20 0 0 {name=l25 lab=clk_phi_not}
N 390 -20 430 -20 {}
C {devices/lab_wire.sym} 430 -20 0 1 {name=l26 lab=ctl_n}
N 390 20 430 20 {}
C {devices/lab_wire.sym} 430 20 0 1 {name=l27 lab=vcmfb}
N 250 -80 250 -120 {}
C {devices/lab_wire.sym} 250 -120 0 1 {name=l28 lab=vdd}
N 250 80 250 120 {}
C {devices/lab_wire.sym} 250 120 2 0 {name=l29 lab=vss}
N 610 -20 570 -20 {}
C {devices/lab_wire.sym} 570 -20 0 0 {name=l30 lab=clk_phi}
N 610 20 570 20 {}
C {devices/lab_wire.sym} 570 20 0 0 {name=l31 lab=clk_phi_not}
N 890 -20 930 -20 {}
C {devices/lab_wire.sym} 930 -20 0 1 {name=l32 lab=ctl_p}
N 890 20 930 20 {}
C {devices/lab_wire.sym} 930 20 0 1 {name=l33 lab=vbias}
N 750 -80 750 -120 {}
C {devices/lab_wire.sym} 750 -120 0 1 {name=l34 lab=vdd}
N 750 80 750 120 {}
C {devices/lab_wire.sym} 750 120 2 0 {name=l35 lab=vss}
N 1110 -20 1070 -20 {}
C {devices/lab_wire.sym} 1070 -20 0 0 {name=l36 lab=clk_phi}
N 1110 20 1070 20 {}
C {devices/lab_wire.sym} 1070 20 0 0 {name=l37 lab=clk_phi_not}
N 1390 -20 1430 -20 {}
C {devices/lab_wire.sym} 1430 -20 0 1 {name=l38 lab=sense_p}
N 1390 20 1430 20 {}
C {devices/lab_wire.sym} 1430 20 0 1 {name=l39 lab=vinp}
N 1250 -80 1250 -120 {}
C {devices/lab_wire.sym} 1250 -120 0 1 {name=l40 lab=vdd}
N 1250 80 1250 120 {}
C {devices/lab_wire.sym} 1250 120 2 0 {name=l41 lab=vss}
N 1610 -20 1570 -20 {}
C {devices/lab_wire.sym} 1570 -20 0 0 {name=l42 lab=clk_phi}
N 1610 20 1570 20 {}
C {devices/lab_wire.sym} 1570 20 0 0 {name=l43 lab=clk_phi_not}
N 1890 -20 1930 -20 {}
C {devices/lab_wire.sym} 1930 -20 0 1 {name=l44 lab=ctl_p}
N 1890 20 1930 20 {}
C {devices/lab_wire.sym} 1930 20 0 1 {name=l45 lab=vcmfb}
N 1750 -80 1750 -120 {}
C {devices/lab_wire.sym} 1750 -120 0 1 {name=l46 lab=vdd}
N 1750 80 1750 120 {}
C {devices/lab_wire.sym} 1750 120 2 0 {name=l47 lab=vss}
N -330 290 -330 250 {}
C {devices/lab_wire.sym} -330 250 0 1 {name=l48 lab=vbias}
N -330 350 -330 390 {}
C {devices/lab_wire.sym} -330 390 2 0 {name=l49 lab=vcm}
N -110 290 -110 250 {}
C {devices/lab_wire.sym} -110 250 0 1 {name=l50 lab=ctl_p}
N -110 350 -110 390 {}
C {devices/lab_wire.sym} -110 390 2 0 {name=l51 lab=sense_p}
N 110 290 110 250 {}
C {devices/lab_wire.sym} 110 250 0 1 {name=l52 lab=vbias}
N 110 350 110 390 {}
C {devices/lab_wire.sym} 110 390 2 0 {name=l53 lab=vcm}
N 330 290 330 250 {}
C {devices/lab_wire.sym} 330 250 0 1 {name=l54 lab=ctl_n}
N 330 350 330 390 {}
C {devices/lab_wire.sym} 330 390 2 0 {name=l55 lab=sense_n}
