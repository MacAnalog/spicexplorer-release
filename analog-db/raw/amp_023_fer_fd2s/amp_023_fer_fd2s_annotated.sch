v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_023_fer_fd2s} -1740 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 100 390 1 0 {name=CCA value=x_dut_cca_value}
C {devices/capa_np.sym} 300 390 1 0 {name=CCB value=x_dut_ccb_value}
C {devices/capa_np.sym} -915 390 1 0 {name=CMA value=x_dut_cma_value}
C {devices/capa_np.sym} -410 390 1 0 {name=CMB value=x_dut_cmb_value}
C {devices/isource_np.sym} -1700 780 0 0 {name=IB value="dc {x_ibias_val}"}
C {devices/res_np.sym} -605 390 0 0 {name=RCA value=x_dut_rca_value}
C {devices/res_np.sym} -180 390 1 0 {name=RCB value=x_dut_rcb_value}
C {devices/res_np.sym} 445 520 1 0 {name=RZA value=x_dut_rza_value}
C {devices/res_np.sym} 700 520 1 0 {name=RZB value=x_dut_rzb_value}
C {devices/vsource_np.sym} -1700 520 0 0 {name=VCR value="dc {x_vcmr_val}"}
C {devices/sg13_lv_nmos_np.sym} -645 260 0 1 {name=M2A model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2a_w l=x_dut_xm2a_l m=x_dut_xm2a_m}
C {devices/sg13_lv_nmos_np.sym} -305 260 0 1 {name=M2B model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2b_w l=x_dut_xm2b_l m=x_dut_xm2b_m}
C {devices/sg13_lv_nmos_np.sym} 35 260 0 0 {name=MB1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb1_w l=x_dut_xmb1_l m=x_dut_xmb1_m}
C {devices/sg13_lv_nmos_np.sym} 405 260 0 0 {name=MB2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb2_w l=x_dut_xmb2_l m=x_dut_xmb2_m}
C {devices/sg13_lv_nmos_np.sym} -985 780 0 1 {name=MBD model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbd_w l=x_dut_xmbd_l m=x_dut_xmbd_m}
C {devices/sg13_lv_pmos_np.sym} 1135 260 0 0 {name=MCA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmca_w l=x_dut_xmca_l m=x_dut_xmca_m}
C {devices/sg13_lv_pmos_np.sym} 1510 260 0 0 {name=MCB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcb_w l=x_dut_xmcb_l m=x_dut_xmcb_m}
C {devices/sg13_lv_nmos_np.sym} -1360 260 0 1 {name=MEA1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmea1_w l=x_dut_xmea1_l m=x_dut_xmea1_m}
C {devices/sg13_lv_nmos_np.sym} -1165 260 0 1 {name=MEA2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmea2_w l=x_dut_xmea2_l m=x_dut_xmea2_m}
C {devices/sg13_lv_nmos_np.sym} -1360 520 0 1 {name=MEAT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmeat_w l=x_dut_xmeat_l m=x_dut_xmeat_m}
C {devices/sg13_lv_pmos_np.sym} -1360 0 0 1 {name=MEPD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmepd_w l=x_dut_xmepd_l m=x_dut_xmepd_m}
C {devices/sg13_lv_pmos_np.sym} -1165 0 0 1 {name=MEPM model=sg13_lv_pmos spiceprefix=X w=x_dut_xmepm_w l=x_dut_xmepm_l m=x_dut_xmepm_m}
C {devices/sg13_lv_nmos_np.sym} 1325 260 0 0 {name=MI1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmi1_w l=x_dut_xmi1_l m=x_dut_xmi1_m}
C {devices/sg13_lv_nmos_np.sym} 1700 260 0 0 {name=MI2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmi2_w l=x_dut_xmi2_l m=x_dut_xmi2_m}
C {devices/sg13_lv_nmos_np.sym} 1135 780 0 0 {name=MKA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmka_w l=x_dut_xmka_l m=x_dut_xmka_m}
C {devices/sg13_lv_nmos_np.sym} 1510 780 0 0 {name=MKB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmkb_w l=x_dut_xmkb_l m=x_dut_xmkb_m}
C {devices/sg13_lv_pmos_np.sym} -645 0 0 1 {name=MLA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmla_w l=x_dut_xmla_l m=x_dut_xmla_m}
C {devices/sg13_lv_pmos_np.sym} -305 0 0 1 {name=MLB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmlb_w l=x_dut_xmlb_l m=x_dut_xmlb_m}
C {devices/sg13_lv_nmos_np.sym} 1135 520 0 0 {name=MNA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmna_w l=x_dut_xmna_l m=x_dut_xmna_m}
C {devices/sg13_lv_nmos_np.sym} 1510 520 0 0 {name=MNB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb_w l=x_dut_xmnb_l m=x_dut_xmnb_m}
C {devices/sg13_lv_nmos_np.sym} 940 260 0 0 {name=MNCD model=sg13_lv_nmos spiceprefix=X w=x_dut_xmncd_w l=x_dut_xmncd_l m=x_dut_xmncd_m}
C {devices/sg13_lv_nmos_np.sym} 745 260 0 0 {name=MND1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnd1_w l=x_dut_xmnd1_l m=x_dut_xmnd1_m}
C {devices/sg13_lv_pmos_np.sym} 35 0 0 0 {name=MPD1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpd1_w l=x_dut_xmpd1_l m=x_dut_xmpd1_m}
C {devices/sg13_lv_pmos_np.sym} 405 0 0 0 {name=MPD2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpd2_w l=x_dut_xmpd2_l m=x_dut_xmpd2_m}
C {devices/sg13_lv_pmos_np.sym} 745 0 0 0 {name=MPM1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpm1_w l=x_dut_xmpm1_l m=x_dut_xmpm1_m}
C {devices/sg13_lv_pmos_np.sym} 1135 0 0 0 {name=MSA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmsa_w l=x_dut_xmsa_l m=x_dut_xmsa_m}
C {devices/sg13_lv_pmos_np.sym} 1510 0 0 0 {name=MSB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmsb_w l=x_dut_xmsb_l m=x_dut_xmsb_m}
C {devices/sg13_lv_nmos_np.sym} -190 520 0 0 {name=MT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmt_w l=x_dut_xmt_l m=x_dut_xmt_m}
N -1700 430 -1700 490 {}
N -1700 550 -1700 610 {}
N -1700 690 -1700 750 {}
N -1700 810 -1700 870 {}
N -1440 0 -1440 94 {}
N -1440 260 -1440 354 {}
N -1440 520 -1440 614 {}
N -1380 -140 -1380 -30 {}
N -1380 30 -1380 230 {}
N -1380 290 -1380 490 {}
N -1380 550 -1380 920 {}
N -1340 0 -1340 70 {}
N -1245 0 -1245 94 {}
N -1245 260 -1245 354 {}
N -1185 -140 -1185 -30 {}
N -1185 30 -1185 90 {}
N -1185 170 -1185 230 {}
N -1185 290 -1185 320 {}
N -1115 0 -1115 60 {}
N -1065 780 -1065 874 {}
N -1005 520 -1005 750 {}
N -1005 810 -1005 920 {}
N -965 710 -965 780 {}
N -855 260 -855 390 {}
N -725 0 -725 94 {}
N -725 260 -725 354 {}
N -665 -140 -665 -30 {}
N -665 30 -665 90 {}
N -665 170 -665 230 {}
N -665 290 -665 920 {}
N -605 330 -605 360 {}
N -605 390 -605 450 {}
N -385 0 -385 94 {}
N -385 260 -385 354 {}
N -380 390 -380 450 {}
N -325 -140 -325 -30 {}
N -325 30 -325 90 {}
N -325 170 -325 230 {}
N -325 290 -325 350 {}
N -210 330 -210 390 {}
N -170 430 -170 490 {}
N -170 550 -170 920 {}
N -150 330 -150 390 {}
N -110 520 -110 614 {}
N -15 260 -15 720 {}
N 15 0 15 70 {}
N 55 -140 55 -30 {}
N 55 30 55 70 {}
N 55 170 55 230 {}
N 55 290 55 920 {}
N 70 390 70 450 {}
N 115 0 115 94 {}
N 115 260 115 354 {}
N 130 390 130 450 {}
N 270 330 270 390 {}
N 330 390 330 450 {}
N 385 0 385 70 {}
N 425 -140 425 -30 {}
N 425 30 425 70 {}
N 425 170 425 230 {}
N 425 290 425 920 {}
N 475 520 475 580 {}
N 485 0 485 94 {}
N 485 260 485 354 {}
N 505 390 505 520 {}
N 640 260 640 520 {}
N 670 460 670 520 {}
N 725 190 725 260 {}
N 730 520 730 580 {}
N 760 390 760 520 {}
N 765 -140 765 -30 {}
N 765 30 765 90 {}
N 765 170 765 230 {}
N 765 290 765 920 {}
N 825 0 825 94 {}
N 825 260 825 354 {}
N 920 190 920 260 {}
N 960 170 960 230 {}
N 960 290 960 920 {}
N 1020 260 1020 354 {}
N 1115 200 1115 260 {}
N 1155 -140 1155 -30 {}
N 1155 30 1155 230 {}
N 1155 290 1155 350 {}
N 1155 430 1155 490 {}
N 1155 550 1155 750 {}
N 1155 810 1155 920 {}
N 1215 0 1215 94 {}
N 1215 260 1215 354 {}
N 1215 520 1215 614 {}
N 1215 780 1215 874 {}
N 1345 200 1345 230 {}
N 1345 290 1345 460 {}
N 1405 260 1405 354 {}
N 1490 200 1490 260 {}
N 1530 -140 1530 -30 {}
N 1530 30 1530 230 {}
N 1530 290 1530 350 {}
N 1530 430 1530 490 {}
N 1530 550 1530 750 {}
N 1530 810 1530 920 {}
N 1590 0 1590 94 {}
N 1590 260 1590 354 {}
N 1590 520 1590 614 {}
N 1590 780 1590 874 {}
N 1720 200 1720 230 {}
N 1720 290 1720 350 {}
N 1780 260 1780 354 {}
N -1760 -140 1915 -140 {}
N -1440 0 -1380 0 {}
N -1245 0 -1185 0 {}
N -1145 0 -1085 0 {}
N -725 0 -665 0 {}
N -625 0 -565 0 {}
N -385 0 -325 0 {}
N -285 0 -225 0 {}
N -45 0 15 0 {}
N 55 0 115 0 {}
N 325 0 385 0 {}
N 425 0 485 0 {}
N 665 0 725 0 {}
N 765 0 825 0 {}
N 1055 0 1115 0 {}
N 1155 0 1215 0 {}
N 1430 0 1490 0 {}
N 1530 0 1590 0 {}
N -1380 70 -1340 70 {}
N 15 70 55 70 {}
N 385 70 425 70 {}
N 725 190 765 190 {}
N 920 190 960 190 {}
N 1155 200 1345 200 {}
N 1530 200 1720 200 {}
N -1440 260 -1380 260 {}
N -1340 260 -1310 260 {}
N -1245 260 -1185 260 {}
N -1145 260 -855 260 {}
N -725 260 -665 260 {}
N -625 260 -565 260 {}
N -385 260 -325 260 {}
N -285 260 -225 260 {}
N -45 260 15 260 {}
N 55 260 115 260 {}
N 325 260 385 260 {}
N 425 260 485 260 {}
N 765 260 825 260 {}
N 960 260 1020 260 {}
N 1155 260 1215 260 {}
N 1275 260 1305 260 {}
N 1345 260 1405 260 {}
N 1460 260 1490 260 {}
N 1530 260 1590 260 {}
N 1650 260 1680 260 {}
N 1720 260 1780 260 {}
N -1380 320 -1185 320 {}
N -1005 390 -945 390 {}
N -885 390 -605 390 {}
N -500 390 -440 390 {}
N -380 390 -350 390 {}
N -240 390 -210 390 {}
N -150 390 -120 390 {}
N 40 390 70 390 {}
N 130 390 160 390 {}
N 240 390 270 390 {}
N 330 390 360 390 {}
N -1440 520 -1380 520 {}
N -1340 520 -210 520 {}
N -170 520 -110 520 {}
N 355 520 415 520 {}
N 475 520 505 520 {}
N 640 520 670 520 {}
N 730 520 760 520 {}
N 1055 520 1115 520 {}
N 1155 520 1215 520 {}
N 1430 520 1490 520 {}
N 1530 520 1590 520 {}
N -1005 710 -965 710 {}
N -1005 720 -15 720 {}
N -1065 780 -1005 780 {}
N 1055 780 1115 780 {}
N 1155 780 1215 780 {}
N 1430 780 1490 780 {}
N 1530 780 1590 780 {}
N -1760 920 1915 920 {}
C {devices/lab_wire.sym} -1760 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1760 920 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -1340 60 2 0 {name=l2 lab=ead}
C {devices/lab_wire.sym} -1085 0 0 1 {name=l3 lab=ead}
C {devices/lab_wire.sym} -1380 350 2 0 {name=l4 lab=eatail}
C {devices/lab_wire.sym} 1530 90 2 0 {name=l5 lab=fn}
C {devices/lab_wire.sym} 1155 90 2 0 {name=l6 lab=fp}
C {devices/lab_wire.sym} -45 260 0 0 {name=l7 lab=ibias}
C {devices/lab_wire.sym} 325 260 0 0 {name=l8 lab=ibias}
C {devices/lab_wire.sym} -565 260 0 1 {name=l9 lab=o1a}
C {devices/lab_wire.sym} 355 520 0 0 {name=l10 lab=o1a}
C {devices/lab_wire.sym} 1155 350 2 0 {name=l11 lab=o1a}
C {devices/lab_wire.sym} 1155 430 0 1 {name=l12 lab=o1a}
C {devices/lab_wire.sym} -225 260 0 1 {name=l13 lab=o1b}
C {devices/lab_wire.sym} 670 460 0 1 {name=l14 lab=o1b}
C {devices/lab_wire.sym} 1530 350 2 0 {name=l15 lab=o1b}
C {devices/lab_wire.sym} 1530 430 0 1 {name=l16 lab=o1b}
C {devices/lab_wire.sym} -170 430 0 1 {name=l17 lab=tail}
C {devices/lab_wire.sym} 1345 350 2 0 {name=l18 lab=tail}
C {devices/lab_wire.sym} 1720 350 2 0 {name=l19 lab=tail}
C {devices/lab_wire.sym} -565 0 0 1 {name=l20 lab=vbp}
C {devices/lab_wire.sym} -225 0 0 1 {name=l21 lab=vbp}
C {devices/lab_wire.sym} -45 0 0 0 {name=l22 lab=vbp}
C {devices/lab_wire.sym} 55 170 0 1 {name=l23 lab=vbp}
C {devices/lab_wire.sym} 665 0 0 0 {name=l24 lab=vbp}
C {devices/lab_wire.sym} 1055 0 0 0 {name=l25 lab=vbp}
C {devices/lab_wire.sym} 1430 0 0 0 {name=l26 lab=vbp}
C {devices/lab_wire.sym} -1185 90 2 0 {name=l27 lab=vcmfb}
C {devices/lab_wire.sym} -1185 170 0 1 {name=l28 lab=vcmfb}
C {devices/lab_wire.sym} 960 170 0 1 {name=l29 lab=vcmfb}
C {devices/lab_wire.sym} 1055 780 0 0 {name=l30 lab=vcmfb}
C {devices/lab_wire.sym} 1430 780 0 0 {name=l31 lab=vcmfb}
C {devices/lab_wire.sym} -1340 260 0 0 {name=l32 lab=vcmr}
C {devices/lab_wire.sym} 765 170 0 1 {name=l33 lab=vcn}
C {devices/lab_wire.sym} 765 90 2 0 {name=l34 lab=vcn}
C {devices/lab_wire.sym} 1055 520 0 0 {name=l35 lab=vcn}
C {devices/lab_wire.sym} 1430 520 0 0 {name=l36 lab=vcn}
C {devices/lab_wire.sym} 325 0 0 0 {name=l37 lab=vcp}
C {devices/lab_wire.sym} 425 170 0 1 {name=l38 lab=vcp}
C {devices/lab_wire.sym} 1115 200 0 1 {name=l39 lab=vcp}
C {devices/lab_wire.sym} 1490 200 0 1 {name=l40 lab=vcp}
C {devices/lab_wire.sym} 1680 260 0 0 {name=l41 lab=vinn}
C {devices/lab_wire.sym} 1305 260 0 0 {name=l42 lab=vinp}
C {devices/lab_wire.sym} -500 390 0 0 {name=l43 lab=voutn}
C {devices/lab_wire.sym} -325 90 2 0 {name=l44 lab=voutn}
C {devices/lab_wire.sym} -325 170 0 1 {name=l45 lab=voutn}
C {devices/lab_wire.sym} -210 330 0 1 {name=l46 lab=voutn}
C {devices/lab_wire.sym} 330 450 2 0 {name=l47 lab=voutn}
C {devices/lab_wire.sym} -1005 390 0 0 {name=l48 lab=voutp}
C {devices/lab_wire.sym} -665 90 2 0 {name=l49 lab=voutp}
C {devices/lab_wire.sym} -665 170 0 1 {name=l50 lab=voutp}
C {devices/lab_wire.sym} -605 360 0 0 {name=l51 lab=voutp}
C {devices/lab_wire.sym} 130 450 2 0 {name=l52 lab=voutp}
C {devices/lab_wire.sym} -1085 260 0 1 {name=l53 lab=vsen}
C {devices/lab_wire.sym} -380 450 2 0 {name=l54 lab=vsen}
C {devices/lab_wire.sym} -150 330 0 1 {name=l55 lab=vsen}
C {devices/lab_wire.sym} 1155 610 2 0 {name=l56 lab=x1a}
C {devices/lab_wire.sym} 1530 610 2 0 {name=l57 lab=x1b}
C {devices/lab_wire.sym} 70 450 2 0 {name=l58 lab=za}
C {devices/lab_wire.sym} 475 580 2 0 {name=l59 lab=za}
C {devices/lab_wire.sym} 270 330 0 1 {name=l60 lab=zb}
C {devices/lab_wire.sym} 730 580 2 0 {name=l61 lab=zb}
C {devices/lab_wire.sym} 1215 354 2 0 {name=l62 lab=vdd}
C {devices/lab_wire.sym} 1590 354 2 0 {name=l63 lab=vdd}
C {devices/lab_wire.sym} -1440 94 2 0 {name=l64 lab=vdd}
C {devices/lab_wire.sym} -1245 94 2 0 {name=l65 lab=vdd}
C {devices/lab_wire.sym} -725 94 2 0 {name=l66 lab=vdd}
C {devices/lab_wire.sym} -385 94 2 0 {name=l67 lab=vdd}
C {devices/lab_wire.sym} 115 94 2 0 {name=l68 lab=vdd}
C {devices/lab_wire.sym} 485 94 2 0 {name=l69 lab=vdd}
C {devices/lab_wire.sym} 825 94 2 0 {name=l70 lab=vdd}
C {devices/lab_wire.sym} 1215 94 2 0 {name=l71 lab=vdd}
C {devices/lab_wire.sym} 1590 94 2 0 {name=l72 lab=vdd}
C {devices/lab_wire.sym} -725 354 2 0 {name=l73 lab=vss}
C {devices/lab_wire.sym} -385 354 2 0 {name=l74 lab=vss}
C {devices/lab_wire.sym} 115 354 2 0 {name=l75 lab=vss}
C {devices/lab_wire.sym} 485 354 2 0 {name=l76 lab=vss}
C {devices/lab_wire.sym} -1065 874 2 0 {name=l77 lab=vss}
C {devices/lab_wire.sym} -1440 354 2 0 {name=l78 lab=vss}
C {devices/lab_wire.sym} -1245 354 2 0 {name=l79 lab=vss}
C {devices/lab_wire.sym} -1440 614 2 0 {name=l80 lab=vss}
C {devices/lab_wire.sym} 1405 354 2 0 {name=l81 lab=vss}
C {devices/lab_wire.sym} 1780 354 2 0 {name=l82 lab=vss}
C {devices/lab_wire.sym} 1215 874 2 0 {name=l83 lab=vss}
C {devices/lab_wire.sym} 1590 874 2 0 {name=l84 lab=vss}
C {devices/lab_wire.sym} 1215 614 2 0 {name=l85 lab=vss}
C {devices/lab_wire.sym} 1590 614 2 0 {name=l86 lab=vss}
C {devices/lab_wire.sym} 1020 354 2 0 {name=l87 lab=vss}
C {devices/lab_wire.sym} 825 354 2 0 {name=l88 lab=vss}
C {devices/lab_wire.sym} -110 614 2 0 {name=l89 lab=vss}
C {devices/lab_wire.sym} -1700 690 0 1 {name=l90 lab=vdd}
C {devices/lab_wire.sym} -1700 870 2 0 {name=l91 lab=ibias}
C {devices/lab_wire.sym} -1700 430 0 1 {name=l92 lab=vcmr}
C {devices/lab_wire.sym} -1700 610 2 0 {name=l93 lab=vss}
C {devices/lab_wire.sym} -325 350 2 0 {name=l94 lab=vss}
C {devices/ipin.sym} -1900 260 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} -1900 380 0 0 {name=p1 lab=vinn}
C {devices/opin.sym} 2055 30 0 0 {name=p2 lab=voutp}
C {devices/opin.sym} 2055 150 0 0 {name=p3 lab=voutn}
B 8 -1564 182 601 858 {fill=0}
T {NMOS Simple Current Mirror (4 outputs)} -1564 164 0 0 0.3 0.3 {layer=8}
B 10 -1564 -78 -1095 78 {fill=0}
T {PMOS Simple Current Mirror} -1564 -96 0 0 0.3 0.3 {layer=10}
B 12 675 182 1706 858 {fill=0}
T {NMOS High Swing Cascode Current Mirror (2 outputs)} 675 164 0 0 0.3 0.3 {layer=12}
B 21 -841 -78 1706 78 {fill=0}
T {PMOS Simple Current Mirror (5 outputs)} -841 -96 0 0 0.3 0.3 {layer=21}
B 15 -1564 182 -1095 338 {fill=0}
T {NMOS Differential Pair} -1564 140 0 0 0.3 0.3 {layer=15}
B 13 1255 182 1896 338 {fill=0}
T {NMOS Differential Pair} 1255 164 0 0 0.3 0.3 {layer=13}
B 18 892 204 1309 836 {fill=0 dash=4}
T {NMOS Simple Current Mirror} 892 186 0 0 0.3 0.3 {layer=18}
B 20 892 204 1684 836 {fill=0 dash=4}
T {NMOS Simple Current Mirror} 892 162 0 0 0.3 0.3 {layer=20}
