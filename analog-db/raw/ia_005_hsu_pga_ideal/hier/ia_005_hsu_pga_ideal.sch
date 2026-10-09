v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ia_005_hsu_pga_ideal} -3300 -200 0 0 0.4 0.4 {}
C {blocks/pr_series_shared_well_1.sym} -3260 0 0 0 {name=xpr_series_shared_well_1}
C {blocks/pr_series_shared_well_2.sym} -2770 0 0 0 {name=xpr_series_shared_well_2}
C {blocks/tg_pair_cmos_rail_bulk_1.sym} -2275 0 0 0 {name=xtg_pair_cmos_rail_bulk_1}
C {blocks/tg_pair_cmos_rail_bulk_2.sym} -1775 0 0 0 {name=xtg_pair_cmos_rail_bulk_2}
C {blocks/tg_pair_cmos_rail_bulk_3.sym} -1275 0 0 0 {name=xtg_pair_cmos_rail_bulk_3}
C {blocks/tg_pair_cmos_rail_bulk_4.sym} -775 0 0 0 {name=xtg_pair_cmos_rail_bulk_4}
C {blocks/tg_pair_cmos_rail_bulk_5.sym} -275 0 0 0 {name=xtg_pair_cmos_rail_bulk_5}
C {blocks/tg_pair_cmos_rail_bulk_6.sym} 225 0 0 0 {name=xtg_pair_cmos_rail_bulk_6}
C {blocks/tg_pair_cmos_rail_bulk_7.sym} 725 0 0 0 {name=xtg_pair_cmos_rail_bulk_7}
C {blocks/tg_pair_cmos_rail_bulk_8.sym} 1225 0 0 0 {name=xtg_pair_cmos_rail_bulk_8}
C {blocks/tg_pair_cmos_rail_bulk_9.sym} 1725 0 0 0 {name=xtg_pair_cmos_rail_bulk_9}
C {blocks/tg_pair_cmos_rail_bulk_10.sym} 2230 0 0 0 {name=xtg_pair_cmos_rail_bulk_10}
C {blocks/tg_pair_cmos_rail_bulk_11.sym} 2740 0 0 0 {name=xtg_pair_cmos_rail_bulk_11}
C {blocks/tg_pair_cmos_rail_bulk_12.sym} 3250 0 0 0 {name=xtg_pair_cmos_rail_bulk_12}
C {devices/capa_np.sym} -1540 320 0 0 {name=CA1 value='Cu' m=x_dut_ca1_m}
C {devices/capa_np.sym} -1320 320 0 0 {name=CA2 value='Cu' m=x_dut_ca2_m}
C {devices/capa_np.sym} -1100 320 0 0 {name=CA3 value='Cu' m=x_dut_ca3_m}
C {devices/capa_np.sym} -880 320 0 0 {name=CA4 value='Cu' m=x_dut_ca4_m}
C {devices/capa_np.sym} -660 320 0 0 {name=CB1 value='Cu' m=x_dut_cb1_m}
C {devices/capa_np.sym} -440 320 0 0 {name=CB2 value='Cu' m=x_dut_cb2_m}
C {devices/capa_np.sym} -220 320 0 0 {name=CB3 value='Cu' m=x_dut_cb3_m}
C {devices/capa_np.sym} 0 320 0 0 {name=CB4 value='Cu' m=x_dut_cb4_m}
C {devices/capa_np.sym} 220 320 0 0 {name=CF1 value='x_dut_cf1_value'}
C {devices/capa_np.sym} 440 320 0 0 {name=CF2 value='x_dut_cf2_value'}
C {devices/capa_np.sym} 660 320 0 0 {name=CIN value='cin_val'}
C {devices/capa_np.sym} 880 320 0 0 {name=COUT value='cout_val'}
C {devices/vccs.sym} 1100 320 0 0 {name=GM value="\{gm_val\}"}
C {devices/res_np.sym} 1320 320 0 0 {name=RIN value='rin_val'}
C {devices/res_np.sym} 1540 320 0 0 {name=ROUT value='rout_val'}
N -3125 -20 -3085 -20 {}
C {devices/lab_wire.sym} -3085 -20 0 1 {name=l0 lab=sum_p}
N -3125 20 -3085 20 {}
C {devices/lab_wire.sym} -3085 20 0 1 {name=l1 lab=voutp}
N -2635 -20 -2595 -20 {}
C {devices/lab_wire.sym} -2595 -20 0 1 {name=l2 lab=sum_n}
N -2635 20 -2595 20 {}
C {devices/lab_wire.sym} -2595 20 0 1 {name=l3 lab=voutn}
N -2415 -20 -2455 -20 {}
C {devices/lab_wire.sym} -2455 -20 0 0 {name=l4 lab=V_D0}
N -2415 20 -2455 20 {}
C {devices/lab_wire.sym} -2455 20 0 0 {name=l5 lab=V_D0_NOT}
N -2135 -20 -2095 -20 {}
C {devices/lab_wire.sym} -2095 -20 0 1 {name=l6 lab=bota0}
N -2135 20 -2095 20 {}
C {devices/lab_wire.sym} -2095 20 0 1 {name=l7 lab=vinp}
N -2275 -80 -2275 -120 {}
C {devices/lab_wire.sym} -2275 -120 0 1 {name=l8 lab=VDD}
N -2275 80 -2275 120 {}
C {devices/lab_wire.sym} -2275 120 2 0 {name=l9 lab=VSS}
N -1915 -20 -1955 -20 {}
C {devices/lab_wire.sym} -1955 -20 0 0 {name=l10 lab=V_D2}
N -1915 20 -1955 20 {}
C {devices/lab_wire.sym} -1955 20 0 0 {name=l11 lab=V_D2_NOT}
N -1635 -20 -1595 -20 {}
C {devices/lab_wire.sym} -1595 -20 0 1 {name=l12 lab=bota2}
N -1635 20 -1595 20 {}
C {devices/lab_wire.sym} -1595 20 0 1 {name=l13 lab=vinp}
N -1775 -80 -1775 -120 {}
C {devices/lab_wire.sym} -1775 -120 0 1 {name=l14 lab=VDD}
N -1775 80 -1775 120 {}
C {devices/lab_wire.sym} -1775 120 2 0 {name=l15 lab=VSS}
N -1415 -20 -1455 -20 {}
C {devices/lab_wire.sym} -1455 -20 0 0 {name=l16 lab=V_D2}
N -1415 20 -1455 20 {}
C {devices/lab_wire.sym} -1455 20 0 0 {name=l17 lab=V_D2_NOT}
N -1135 -20 -1095 -20 {}
C {devices/lab_wire.sym} -1095 -20 0 1 {name=l18 lab=VCM}
N -1135 20 -1095 20 {}
C {devices/lab_wire.sym} -1095 20 0 1 {name=l19 lab=bota2}
N -1275 -80 -1275 -120 {}
C {devices/lab_wire.sym} -1275 -120 0 1 {name=l20 lab=VDD}
N -1275 80 -1275 120 {}
C {devices/lab_wire.sym} -1275 120 2 0 {name=l21 lab=VSS}
N -915 -20 -955 -20 {}
C {devices/lab_wire.sym} -955 -20 0 0 {name=l22 lab=V_D0}
N -915 20 -955 20 {}
C {devices/lab_wire.sym} -955 20 0 0 {name=l23 lab=V_D0_NOT}
N -635 -20 -595 -20 {}
C {devices/lab_wire.sym} -595 -20 0 1 {name=l24 lab=VCM}
N -635 20 -595 20 {}
C {devices/lab_wire.sym} -595 20 0 1 {name=l25 lab=bota0}
N -775 -80 -775 -120 {}
C {devices/lab_wire.sym} -775 -120 0 1 {name=l26 lab=VDD}
N -775 80 -775 120 {}
C {devices/lab_wire.sym} -775 120 2 0 {name=l27 lab=VSS}
N -415 -20 -455 -20 {}
C {devices/lab_wire.sym} -455 -20 0 0 {name=l28 lab=V_D1}
N -415 20 -455 20 {}
C {devices/lab_wire.sym} -455 20 0 0 {name=l29 lab=V_D1_NOT}
N -135 -20 -95 -20 {}
C {devices/lab_wire.sym} -95 -20 0 1 {name=l30 lab=bota1}
N -135 20 -95 20 {}
C {devices/lab_wire.sym} -95 20 0 1 {name=l31 lab=vinp}
N -275 -80 -275 -120 {}
C {devices/lab_wire.sym} -275 -120 0 1 {name=l32 lab=VDD}
N -275 80 -275 120 {}
C {devices/lab_wire.sym} -275 120 2 0 {name=l33 lab=VSS}
N 85 -20 45 -20 {}
C {devices/lab_wire.sym} 45 -20 0 0 {name=l34 lab=V_D1}
N 85 20 45 20 {}
C {devices/lab_wire.sym} 45 20 0 0 {name=l35 lab=V_D1_NOT}
N 365 -20 405 -20 {}
C {devices/lab_wire.sym} 405 -20 0 1 {name=l36 lab=VCM}
N 365 20 405 20 {}
C {devices/lab_wire.sym} 405 20 0 1 {name=l37 lab=bota1}
N 225 -80 225 -120 {}
C {devices/lab_wire.sym} 225 -120 0 1 {name=l38 lab=VDD}
N 225 80 225 120 {}
C {devices/lab_wire.sym} 225 120 2 0 {name=l39 lab=VSS}
N 585 -20 545 -20 {}
C {devices/lab_wire.sym} 545 -20 0 0 {name=l40 lab=V_D0}
N 585 20 545 20 {}
C {devices/lab_wire.sym} 545 20 0 0 {name=l41 lab=V_D0_NOT}
N 865 -20 905 -20 {}
C {devices/lab_wire.sym} 905 -20 0 1 {name=l42 lab=botb0}
N 865 20 905 20 {}
C {devices/lab_wire.sym} 905 20 0 1 {name=l43 lab=vinn}
N 725 -80 725 -120 {}
C {devices/lab_wire.sym} 725 -120 0 1 {name=l44 lab=VDD}
N 725 80 725 120 {}
C {devices/lab_wire.sym} 725 120 2 0 {name=l45 lab=VSS}
N 1085 -20 1045 -20 {}
C {devices/lab_wire.sym} 1045 -20 0 0 {name=l46 lab=V_D2}
N 1085 20 1045 20 {}
C {devices/lab_wire.sym} 1045 20 0 0 {name=l47 lab=V_D2_NOT}
N 1365 -20 1405 -20 {}
C {devices/lab_wire.sym} 1405 -20 0 1 {name=l48 lab=botb2}
N 1365 20 1405 20 {}
C {devices/lab_wire.sym} 1405 20 0 1 {name=l49 lab=vinn}
N 1225 -80 1225 -120 {}
C {devices/lab_wire.sym} 1225 -120 0 1 {name=l50 lab=VDD}
N 1225 80 1225 120 {}
C {devices/lab_wire.sym} 1225 120 2 0 {name=l51 lab=VSS}
N 1585 -20 1545 -20 {}
C {devices/lab_wire.sym} 1545 -20 0 0 {name=l52 lab=V_D2}
N 1585 20 1545 20 {}
C {devices/lab_wire.sym} 1545 20 0 0 {name=l53 lab=V_D2_NOT}
N 1865 -20 1905 -20 {}
C {devices/lab_wire.sym} 1905 -20 0 1 {name=l54 lab=VCM}
N 1865 20 1905 20 {}
C {devices/lab_wire.sym} 1905 20 0 1 {name=l55 lab=botb2}
N 1725 -80 1725 -120 {}
C {devices/lab_wire.sym} 1725 -120 0 1 {name=l56 lab=VDD}
N 1725 80 1725 120 {}
C {devices/lab_wire.sym} 1725 120 2 0 {name=l57 lab=VSS}
N 2085 -20 2045 -20 {}
C {devices/lab_wire.sym} 2045 -20 0 0 {name=l58 lab=V_D0}
N 2085 20 2045 20 {}
C {devices/lab_wire.sym} 2045 20 0 0 {name=l59 lab=V_D0_NOT}
N 2375 -20 2415 -20 {}
C {devices/lab_wire.sym} 2415 -20 0 1 {name=l60 lab=VCM}
N 2375 20 2415 20 {}
C {devices/lab_wire.sym} 2415 20 0 1 {name=l61 lab=botb0}
N 2230 -80 2230 -120 {}
C {devices/lab_wire.sym} 2230 -120 0 1 {name=l62 lab=VDD}
N 2230 80 2230 120 {}
C {devices/lab_wire.sym} 2230 120 2 0 {name=l63 lab=VSS}
N 2595 -20 2555 -20 {}
C {devices/lab_wire.sym} 2555 -20 0 0 {name=l64 lab=V_D1}
N 2595 20 2555 20 {}
C {devices/lab_wire.sym} 2555 20 0 0 {name=l65 lab=V_D1_NOT}
N 2885 -20 2925 -20 {}
C {devices/lab_wire.sym} 2925 -20 0 1 {name=l66 lab=botb1}
N 2885 20 2925 20 {}
C {devices/lab_wire.sym} 2925 20 0 1 {name=l67 lab=vinn}
N 2740 -80 2740 -120 {}
C {devices/lab_wire.sym} 2740 -120 0 1 {name=l68 lab=VDD}
N 2740 80 2740 120 {}
C {devices/lab_wire.sym} 2740 120 2 0 {name=l69 lab=VSS}
N 3105 -20 3065 -20 {}
C {devices/lab_wire.sym} 3065 -20 0 0 {name=l70 lab=V_D1}
N 3105 20 3065 20 {}
C {devices/lab_wire.sym} 3065 20 0 0 {name=l71 lab=V_D1_NOT}
N 3395 -20 3435 -20 {}
C {devices/lab_wire.sym} 3435 -20 0 1 {name=l72 lab=VCM}
N 3395 20 3435 20 {}
C {devices/lab_wire.sym} 3435 20 0 1 {name=l73 lab=botb1}
N 3250 -80 3250 -120 {}
C {devices/lab_wire.sym} 3250 -120 0 1 {name=l74 lab=VDD}
N 3250 80 3250 120 {}
C {devices/lab_wire.sym} 3250 120 2 0 {name=l75 lab=VSS}
N -1540 290 -1540 250 {}
C {devices/lab_wire.sym} -1540 250 0 1 {name=l76 lab=sum_p}
N -1540 350 -1540 390 {}
C {devices/lab_wire.sym} -1540 390 2 0 {name=l77 lab=vinp}
N -1320 290 -1320 250 {}
C {devices/lab_wire.sym} -1320 250 0 1 {name=l78 lab=sum_p}
N -1320 350 -1320 390 {}
C {devices/lab_wire.sym} -1320 390 2 0 {name=l79 lab=bota0}
N -1100 290 -1100 250 {}
C {devices/lab_wire.sym} -1100 250 0 1 {name=l80 lab=sum_p}
N -1100 350 -1100 390 {}
C {devices/lab_wire.sym} -1100 390 2 0 {name=l81 lab=bota1}
N -880 290 -880 250 {}
C {devices/lab_wire.sym} -880 250 0 1 {name=l82 lab=sum_p}
N -880 350 -880 390 {}
C {devices/lab_wire.sym} -880 390 2 0 {name=l83 lab=bota2}
N -660 290 -660 250 {}
C {devices/lab_wire.sym} -660 250 0 1 {name=l84 lab=sum_n}
N -660 350 -660 390 {}
C {devices/lab_wire.sym} -660 390 2 0 {name=l85 lab=vinn}
N -440 290 -440 250 {}
C {devices/lab_wire.sym} -440 250 0 1 {name=l86 lab=sum_n}
N -440 350 -440 390 {}
C {devices/lab_wire.sym} -440 390 2 0 {name=l87 lab=botb0}
N -220 290 -220 250 {}
C {devices/lab_wire.sym} -220 250 0 1 {name=l88 lab=sum_n}
N -220 350 -220 390 {}
C {devices/lab_wire.sym} -220 390 2 0 {name=l89 lab=botb1}
N 0 290 0 250 {}
C {devices/lab_wire.sym} 0 250 0 1 {name=l90 lab=sum_n}
N 0 350 0 390 {}
C {devices/lab_wire.sym} 0 390 2 0 {name=l91 lab=botb2}
N 220 290 220 250 {}
C {devices/lab_wire.sym} 220 250 0 1 {name=l92 lab=voutp}
N 220 350 220 390 {}
C {devices/lab_wire.sym} 220 390 2 0 {name=l93 lab=sum_p}
N 440 290 440 250 {}
C {devices/lab_wire.sym} 440 250 0 1 {name=l94 lab=voutn}
N 440 350 440 390 {}
C {devices/lab_wire.sym} 440 390 2 0 {name=l95 lab=sum_n}
N 660 290 660 250 {}
C {devices/lab_wire.sym} 660 250 0 1 {name=l96 lab=sum_p}
N 660 350 660 390 {}
C {devices/lab_wire.sym} 660 390 2 0 {name=l97 lab=sum_n}
N 880 290 880 250 {}
C {devices/lab_wire.sym} 880 250 0 1 {name=l98 lab=voutp}
N 880 350 880 390 {}
C {devices/lab_wire.sym} 880 390 2 0 {name=l99 lab=voutn}
N 1100 290 1100 250 {}
C {devices/lab_wire.sym} 1100 250 0 1 {name=l100 lab=voutp}
N 1100 350 1100 390 {}
C {devices/lab_wire.sym} 1100 390 2 0 {name=l101 lab=voutn}
N 1060 300 1020 300 {}
C {devices/lab_wire.sym} 1020 300 0 0 {name=l102 lab=sum_p}
N 1060 340 1020 340 {}
C {devices/lab_wire.sym} 1020 340 0 0 {name=l103 lab=sum_n}
N 1320 290 1320 250 {}
C {devices/lab_wire.sym} 1320 250 0 1 {name=l104 lab=sum_p}
N 1320 350 1320 390 {}
C {devices/lab_wire.sym} 1320 390 2 0 {name=l105 lab=sum_n}
N 1540 290 1540 250 {}
C {devices/lab_wire.sym} 1540 250 0 1 {name=l106 lab=voutp}
N 1540 350 1540 390 {}
C {devices/lab_wire.sym} 1540 390 2 0 {name=l107 lab=voutn}
