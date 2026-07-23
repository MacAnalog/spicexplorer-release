v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_023_fer_fd2s} -1740 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -210 390 1 0 {name=CCA value=x_dut_cca_value}
C {devices/capa_np.sym} -15 390 1 0 {name=CCB value=x_dut_ccb_value}
C {devices/capa_np.sym} -1060 390 1 0 {name=CMA value=x_dut_cma_value}
C {devices/capa_np.sym} -615 390 1 0 {name=CMB value=x_dut_cmb_value}
C {devices/isource_np.sym} -1700 780 0 0 {name=IB value="dc {x_ibias_val}"}
C {devices/res_np.sym} -845 390 0 0 {name=RCA value=x_dut_rca_value}
C {devices/res_np.sym} -405 390 0 0 {name=RCB value=x_dut_rcb_value}
C {devices/res_np.sym} 415 520 1 0 {name=RZA value=x_dut_rza_value}
C {devices/res_np.sym} 670 520 1 0 {name=RZB value=x_dut_rzb_value}
C {devices/vsource_np.sym} -1700 520 0 0 {name=VCR value="dc {x_vcmr_val}"}
C {devices/sg13_lv_nmos_np.sym} -975 260 0 1 {name=M2A model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2a_w l=x_dut_xm2a_l m=x_dut_xm2a_m}
C {devices/sg13_lv_nmos_np.sym} -635 260 0 1 {name=M2B model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2b_w l=x_dut_xm2b_l m=x_dut_xm2b_m}
C {devices/sg13_lv_nmos_np.sym} -295 260 0 1 {name=MB1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb1_w l=x_dut_xmb1_l m=x_dut_xmb1_m}
C {devices/sg13_lv_nmos_np.sym} 805 260 0 0 {name=MB2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb2_w l=x_dut_xmb2_l m=x_dut_xmb2_m}
C {devices/sg13_lv_nmos_np.sym} 465 780 0 0 {name=MBD model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbd_w l=x_dut_xmbd_l m=x_dut_xmbd_m}
C {devices/sg13_lv_pmos_np.sym} 1145 260 0 0 {name=MCA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmca_w l=x_dut_xmca_l m=x_dut_xmca_m}
C {devices/sg13_lv_pmos_np.sym} 1525 260 0 0 {name=MCB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcb_w l=x_dut_xmcb_l m=x_dut_xmcb_m}
C {devices/sg13_lv_nmos_np.sym} -1360 260 0 1 {name=MEA1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmea1_w l=x_dut_xmea1_l m=x_dut_xmea1_m}
C {devices/sg13_lv_nmos_np.sym} -1165 260 0 1 {name=MEA2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmea2_w l=x_dut_xmea2_l m=x_dut_xmea2_m}
C {devices/sg13_lv_nmos_np.sym} -1360 520 0 1 {name=MEAT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmeat_w l=x_dut_xmeat_l m=x_dut_xmeat_m}
C {devices/sg13_lv_pmos_np.sym} -1360 0 0 1 {name=MEPD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmepd_w l=x_dut_xmepd_l m=x_dut_xmepd_m}
C {devices/sg13_lv_pmos_np.sym} 285 0 0 1 {name=MEPM model=sg13_lv_pmos spiceprefix=X w=x_dut_xmepm_w l=x_dut_xmepm_l m=x_dut_xmepm_m}
C {devices/sg13_lv_nmos_np.sym} 1335 260 0 0 {name=MI1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmi1_w l=x_dut_xmi1_l m=x_dut_xmi1_m}
C {devices/sg13_lv_nmos_np.sym} 1710 260 0 0 {name=MI2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmi2_w l=x_dut_xmi2_l m=x_dut_xmi2_m}
C {devices/sg13_lv_nmos_np.sym} 1145 780 0 0 {name=MKA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmka_w l=x_dut_xmka_l m=x_dut_xmka_m}
C {devices/sg13_lv_nmos_np.sym} 1525 780 0 0 {name=MKB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmkb_w l=x_dut_xmkb_l m=x_dut_xmkb_m}
C {devices/sg13_lv_pmos_np.sym} -975 0 0 1 {name=MLA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmla_w l=x_dut_xmla_l m=x_dut_xmla_m}
C {devices/sg13_lv_pmos_np.sym} -635 0 0 1 {name=MLB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmlb_w l=x_dut_xmlb_l m=x_dut_xmlb_m}
C {devices/sg13_lv_nmos_np.sym} 1145 520 0 0 {name=MNA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmna_w l=x_dut_xmna_l m=x_dut_xmna_m}
C {devices/sg13_lv_nmos_np.sym} 1525 520 0 0 {name=MNB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb_w l=x_dut_xmnb_l m=x_dut_xmnb_m}
C {devices/sg13_lv_nmos_np.sym} 285 260 0 1 {name=MNCD model=sg13_lv_nmos spiceprefix=X w=x_dut_xmncd_w l=x_dut_xmncd_l m=x_dut_xmncd_m}
C {devices/sg13_lv_nmos_np.sym} 90 260 0 1 {name=MND1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnd1_w l=x_dut_xmnd1_l m=x_dut_xmnd1_m}
C {devices/sg13_lv_pmos_np.sym} -295 0 0 1 {name=MPD1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpd1_w l=x_dut_xmpd1_l m=x_dut_xmpd1_m}
C {devices/sg13_lv_pmos_np.sym} 805 0 0 0 {name=MPD2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpd2_w l=x_dut_xmpd2_l m=x_dut_xmpd2_m}
C {devices/sg13_lv_pmos_np.sym} 90 0 0 1 {name=MPM1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpm1_w l=x_dut_xmpm1_l m=x_dut_xmpm1_m}
C {devices/sg13_lv_pmos_np.sym} 1145 0 0 0 {name=MSA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmsa_w l=x_dut_xmsa_l m=x_dut_xmsa_m}
C {devices/sg13_lv_pmos_np.sym} 1525 0 0 0 {name=MSB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmsb_w l=x_dut_xmsb_l m=x_dut_xmsb_m}
C {devices/sg13_lv_nmos_np.sym} 90 520 0 1 {name=MT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmt_w l=x_dut_xmt_l m=x_dut_xmt_m}
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
N -1245 260 -1245 354 {}
N -1185 170 -1185 230 {}
N -1185 290 -1185 320 {}
N -1145 200 -1145 260 {}
N -1115 260 -1115 390 {}
N -1055 0 -1055 94 {}
N -1055 260 -1055 354 {}
N -1030 390 -1030 450 {}
N -995 -140 -995 -30 {}
N -995 30 -995 90 {}
N -995 170 -995 230 {}
N -995 290 -995 350 {}
N -845 300 -845 360 {}
N -845 420 -845 480 {}
N -715 0 -715 94 {}
N -715 260 -715 354 {}
N -655 -140 -655 -30 {}
N -655 30 -655 90 {}
N -655 170 -655 230 {}
N -655 290 -655 920 {}
N -645 390 -645 450 {}
N -405 300 -405 390 {}
N -405 420 -405 450 {}
N -375 0 -375 94 {}
N -375 260 -375 354 {}
N -315 -140 -315 -30 {}
N -315 30 -315 70 {}
N -315 170 -315 230 {}
N -315 290 -315 920 {}
N -275 0 -275 70 {}
N -245 260 -245 520 {}
N -180 390 -180 450 {}
N 10 0 10 94 {}
N 10 260 10 354 {}
N 10 520 10 614 {}
N 15 390 15 450 {}
N 70 -140 70 -30 {}
N 70 30 70 90 {}
N 70 170 70 230 {}
N 70 290 70 350 {}
N 70 430 70 490 {}
N 70 550 70 920 {}
N 110 0 110 60 {}
N 110 190 110 260 {}
N 205 0 205 94 {}
N 205 260 205 354 {}
N 265 -140 265 -30 {}
N 265 30 265 90 {}
N 265 170 265 230 {}
N 265 290 265 920 {}
N 305 190 305 260 {}
N 335 0 335 60 {}
N 445 520 445 580 {}
N 445 710 445 780 {}
N 475 260 475 520 {}
N 485 260 485 750 {}
N 485 810 485 920 {}
N 545 780 545 874 {}
N 610 390 610 520 {}
N 640 460 640 520 {}
N 700 520 700 580 {}
N 785 0 785 70 {}
N 825 -140 825 -30 {}
N 825 30 825 70 {}
N 825 170 825 230 {}
N 825 290 825 920 {}
N 885 0 885 94 {}
N 885 260 885 354 {}
N 1165 -140 1165 -30 {}
N 1165 30 1165 230 {}
N 1165 290 1165 350 {}
N 1165 430 1165 490 {}
N 1165 550 1165 750 {}
N 1165 810 1165 920 {}
N 1225 0 1225 94 {}
N 1225 260 1225 354 {}
N 1225 520 1225 614 {}
N 1225 780 1225 874 {}
N 1355 200 1355 230 {}
N 1355 290 1355 460 {}
N 1415 260 1415 354 {}
N 1505 200 1505 260 {}
N 1545 -140 1545 -30 {}
N 1545 30 1545 230 {}
N 1545 290 1545 350 {}
N 1545 430 1545 490 {}
N 1545 550 1545 750 {}
N 1545 810 1545 920 {}
N 1605 0 1605 94 {}
N 1605 260 1605 354 {}
N 1605 520 1605 614 {}
N 1605 780 1605 874 {}
N 1730 200 1730 230 {}
N 1730 290 1730 350 {}
N 1790 260 1790 354 {}
N -1760 -140 1925 -140 {}
N -1440 0 -1380 0 {}
N -1340 0 -1280 0 {}
N -1055 0 -995 0 {}
N -955 0 -895 0 {}
N -715 0 -655 0 {}
N -615 0 -555 0 {}
N -375 0 -315 0 {}
N -275 0 -215 0 {}
N 10 0 70 0 {}
N 110 0 140 0 {}
N 205 0 265 0 {}
N 305 0 365 0 {}
N 725 0 785 0 {}
N 825 0 885 0 {}
N 1065 0 1125 0 {}
N 1165 0 1225 0 {}
N 1445 0 1505 0 {}
N 1545 0 1605 0 {}
N -1380 70 -1340 70 {}
N -315 70 -275 70 {}
N 785 70 825 70 {}
N 70 190 110 190 {}
N 265 190 305 190 {}
N 1165 200 1355 200 {}
N 1545 200 1730 200 {}
N -1440 260 -1380 260 {}
N -1340 260 -1310 260 {}
N -1245 260 -1185 260 {}
N -1145 260 -1115 260 {}
N -1055 260 -995 260 {}
N -955 260 -895 260 {}
N -715 260 -655 260 {}
N -615 260 -555 260 {}
N -375 260 -315 260 {}
N -275 260 -215 260 {}
N 10 260 70 260 {}
N 205 260 265 260 {}
N 725 260 785 260 {}
N 825 260 885 260 {}
N 1065 260 1125 260 {}
N 1165 260 1225 260 {}
N 1285 260 1315 260 {}
N 1355 260 1415 260 {}
N 1475 260 1505 260 {}
N 1545 260 1605 260 {}
N 1660 260 1690 260 {}
N 1730 260 1790 260 {}
N -1380 320 -1185 320 {}
N -1120 390 -1090 390 {}
N -1030 390 -1000 390 {}
N -675 390 -645 390 {}
N -585 390 -405 390 {}
N -300 390 -240 390 {}
N -180 390 -150 390 {}
N -105 390 -45 390 {}
N 15 390 45 390 {}
N -845 450 -405 450 {}
N -1440 520 -1380 520 {}
N -1340 520 -1280 520 {}
N 10 520 70 520 {}
N 110 520 170 520 {}
N 325 520 385 520 {}
N 445 520 475 520 {}
N 610 520 640 520 {}
N 700 520 730 520 {}
N 1065 520 1125 520 {}
N 1165 520 1225 520 {}
N 1445 520 1505 520 {}
N 1545 520 1605 520 {}
N 445 710 485 710 {}
N 485 780 545 780 {}
N 1065 780 1125 780 {}
N 1165 780 1225 780 {}
N 1445 780 1505 780 {}
N 1545 780 1605 780 {}
N -1760 920 1925 920 {}
C {devices/lab_wire.sym} -1760 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1760 920 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -1280 0 0 1 {name=l2 lab=ead}
C {devices/lab_wire.sym} 365 0 0 1 {name=l3 lab=ead}
C {devices/lab_wire.sym} -1380 350 2 0 {name=l4 lab=eatail}
C {devices/lab_wire.sym} 1545 90 2 0 {name=l5 lab=fn}
C {devices/lab_wire.sym} 1165 90 2 0 {name=l6 lab=fp}
C {devices/lab_wire.sym} -1280 520 0 1 {name=l7 lab=ibias}
C {devices/lab_wire.sym} -215 260 0 1 {name=l8 lab=ibias}
C {devices/lab_wire.sym} 170 520 0 1 {name=l9 lab=ibias}
C {devices/lab_wire.sym} 485 690 0 1 {name=l10 lab=ibias}
C {devices/lab_wire.sym} 725 260 0 0 {name=l11 lab=ibias}
C {devices/lab_wire.sym} -895 260 0 1 {name=l12 lab=o1a}
C {devices/lab_wire.sym} 445 580 2 0 {name=l13 lab=o1a}
C {devices/lab_wire.sym} 1165 350 2 0 {name=l14 lab=o1a}
C {devices/lab_wire.sym} 1165 430 0 1 {name=l15 lab=o1a}
C {devices/lab_wire.sym} -555 260 0 1 {name=l16 lab=o1b}
C {devices/lab_wire.sym} 700 580 2 0 {name=l17 lab=o1b}
C {devices/lab_wire.sym} 1545 350 2 0 {name=l18 lab=o1b}
C {devices/lab_wire.sym} 1545 430 0 1 {name=l19 lab=o1b}
C {devices/lab_wire.sym} 70 430 0 1 {name=l20 lab=tail}
C {devices/lab_wire.sym} 1355 350 2 0 {name=l21 lab=tail}
C {devices/lab_wire.sym} 1730 350 2 0 {name=l22 lab=tail}
C {devices/lab_wire.sym} -895 0 0 1 {name=l23 lab=vbp}
C {devices/lab_wire.sym} -555 0 0 1 {name=l24 lab=vbp}
C {devices/lab_wire.sym} -215 0 0 1 {name=l25 lab=vbp}
C {devices/lab_wire.sym} -315 170 0 1 {name=l26 lab=vbp}
C {devices/lab_wire.sym} 110 60 2 0 {name=l27 lab=vbp}
C {devices/lab_wire.sym} 1065 0 0 0 {name=l28 lab=vbp}
C {devices/lab_wire.sym} 1445 0 0 0 {name=l29 lab=vbp}
C {devices/lab_wire.sym} -1185 170 0 1 {name=l30 lab=vcmfb}
C {devices/lab_wire.sym} 265 90 2 0 {name=l31 lab=vcmfb}
C {devices/lab_wire.sym} 265 170 0 1 {name=l32 lab=vcmfb}
C {devices/lab_wire.sym} 1065 780 0 0 {name=l33 lab=vcmfb}
C {devices/lab_wire.sym} 1445 780 0 0 {name=l34 lab=vcmfb}
C {devices/lab_wire.sym} -1340 260 0 0 {name=l35 lab=vcmr}
C {devices/lab_wire.sym} 70 90 2 0 {name=l36 lab=vcn}
C {devices/lab_wire.sym} 70 170 0 1 {name=l37 lab=vcn}
C {devices/lab_wire.sym} 1065 520 0 0 {name=l38 lab=vcn}
C {devices/lab_wire.sym} 1445 520 0 0 {name=l39 lab=vcn}
C {devices/lab_wire.sym} 725 0 0 0 {name=l40 lab=vcp}
C {devices/lab_wire.sym} 825 170 0 1 {name=l41 lab=vcp}
C {devices/lab_wire.sym} 1065 260 0 0 {name=l42 lab=vcp}
C {devices/lab_wire.sym} 1505 200 0 1 {name=l43 lab=vcp}
C {devices/lab_wire.sym} 1690 260 0 0 {name=l44 lab=vinn}
C {devices/lab_wire.sym} 1315 260 0 0 {name=l45 lab=vinp}
C {devices/lab_wire.sym} -655 90 2 0 {name=l46 lab=voutn}
C {devices/lab_wire.sym} -655 170 0 1 {name=l47 lab=voutn}
C {devices/lab_wire.sym} -405 300 0 1 {name=l48 lab=voutn}
C {devices/lab_wire.sym} -105 390 0 0 {name=l49 lab=voutn}
C {devices/lab_wire.sym} -1030 450 2 0 {name=l50 lab=voutp}
C {devices/lab_wire.sym} -995 90 2 0 {name=l51 lab=voutp}
C {devices/lab_wire.sym} -995 170 0 1 {name=l52 lab=voutp}
C {devices/lab_wire.sym} -845 300 0 1 {name=l53 lab=voutp}
C {devices/lab_wire.sym} -300 390 0 0 {name=l54 lab=voutp}
C {devices/lab_wire.sym} -1145 200 0 1 {name=l55 lab=vsen}
C {devices/lab_wire.sym} -845 480 2 0 {name=l56 lab=vsen}
C {devices/lab_wire.sym} -645 450 2 0 {name=l57 lab=vsen}
C {devices/lab_wire.sym} 1165 610 2 0 {name=l58 lab=x1a}
C {devices/lab_wire.sym} 1545 610 2 0 {name=l59 lab=x1b}
C {devices/lab_wire.sym} -180 450 2 0 {name=l60 lab=za}
C {devices/lab_wire.sym} 325 520 0 0 {name=l61 lab=za}
C {devices/lab_wire.sym} 15 450 2 0 {name=l62 lab=zb}
C {devices/lab_wire.sym} 640 460 0 1 {name=l63 lab=zb}
C {devices/lab_wire.sym} 1225 354 2 0 {name=l64 lab=vdd}
C {devices/lab_wire.sym} 1605 354 2 0 {name=l65 lab=vdd}
C {devices/lab_wire.sym} -1440 94 2 0 {name=l66 lab=vdd}
C {devices/lab_wire.sym} 205 94 2 0 {name=l67 lab=vdd}
C {devices/lab_wire.sym} -1055 94 2 0 {name=l68 lab=vdd}
C {devices/lab_wire.sym} -715 94 2 0 {name=l69 lab=vdd}
C {devices/lab_wire.sym} -375 94 2 0 {name=l70 lab=vdd}
C {devices/lab_wire.sym} 885 94 2 0 {name=l71 lab=vdd}
C {devices/lab_wire.sym} 10 94 2 0 {name=l72 lab=vdd}
C {devices/lab_wire.sym} 1225 94 2 0 {name=l73 lab=vdd}
C {devices/lab_wire.sym} 1605 94 2 0 {name=l74 lab=vdd}
C {devices/lab_wire.sym} -1055 354 2 0 {name=l75 lab=vss}
C {devices/lab_wire.sym} -715 354 2 0 {name=l76 lab=vss}
C {devices/lab_wire.sym} -375 354 2 0 {name=l77 lab=vss}
C {devices/lab_wire.sym} 885 354 2 0 {name=l78 lab=vss}
C {devices/lab_wire.sym} 545 874 2 0 {name=l79 lab=vss}
C {devices/lab_wire.sym} -1440 354 2 0 {name=l80 lab=vss}
C {devices/lab_wire.sym} -1245 354 2 0 {name=l81 lab=vss}
C {devices/lab_wire.sym} -1440 614 2 0 {name=l82 lab=vss}
C {devices/lab_wire.sym} 1415 354 2 0 {name=l83 lab=vss}
C {devices/lab_wire.sym} 1790 354 2 0 {name=l84 lab=vss}
C {devices/lab_wire.sym} 1225 874 2 0 {name=l85 lab=vss}
C {devices/lab_wire.sym} 1605 874 2 0 {name=l86 lab=vss}
C {devices/lab_wire.sym} 1225 614 2 0 {name=l87 lab=vss}
C {devices/lab_wire.sym} 1605 614 2 0 {name=l88 lab=vss}
C {devices/lab_wire.sym} 205 354 2 0 {name=l89 lab=vss}
C {devices/lab_wire.sym} 10 354 2 0 {name=l90 lab=vss}
C {devices/lab_wire.sym} 10 614 2 0 {name=l91 lab=vss}
C {devices/lab_wire.sym} -1700 690 0 1 {name=l92 lab=vdd}
C {devices/lab_wire.sym} -1700 870 2 0 {name=l93 lab=ibias}
C {devices/lab_wire.sym} -1700 430 0 1 {name=l94 lab=vcmr}
C {devices/lab_wire.sym} -1700 610 2 0 {name=l95 lab=vss}
C {devices/lab_wire.sym} -995 350 2 0 {name=l96 lab=vss}
C {devices/lab_wire.sym} 70 350 2 0 {name=l97 lab=vss}
C {devices/ipin.sym} -1900 260 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} -1900 380 0 0 {name=p1 lab=vinn}
C {devices/opin.sym} 2065 30 0 0 {name=p2 lab=voutp}
C {devices/opin.sym} 2065 150 0 0 {name=p3 lab=voutn}
