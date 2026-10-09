v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_023_fer_fd2s} -1790 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} -70 390 1 0 {name=CCA value=x_dut_cca_value}
C {devices/capa_np.sym} 165 390 1 0 {name=CCB value=x_dut_ccb_value}
C {devices/capa_np.sym} -1020 390 1 0 {name=CMA value=x_dut_cma_value}
C {devices/capa_np.sym} -535 390 1 0 {name=CMB value=x_dut_cmb_value}
C {devices/isource_np.sym} -1750 780 0 0 {name=IB value="dc \{x_ibias_val\}"}
C {devices/res_np.sym} -770 390 0 0 {name=RCA value=x_dut_rca_value}
C {devices/res_np.sym} -300 390 0 0 {name=RCB value=x_dut_rcb_value}
C {devices/res_np.sym} 635 520 1 0 {name=RZA value=x_dut_rza_value}
C {devices/res_np.sym} 890 520 1 0 {name=RZB value=x_dut_rzb_value}
C {devices/vsource_np.sym} -1750 520 0 0 {name=VCR value="dc \{x_vcmr_val\}" savecurrent=false}
C {devices/sg13_lv_nmos_np.sym} -900 260 0 1 {name=M2A model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2a_w l=x_dut_xm2a_l m=x_dut_xm2a_m}
C {devices/sg13_lv_nmos_np.sym} -560 260 0 1 {name=M2B model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2b_w l=x_dut_xm2b_l m=x_dut_xm2b_m}
C {devices/sg13_lv_nmos_np.sym} -190 260 0 1 {name=MB1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb1_w l=x_dut_xmb1_l m=x_dut_xmb1_m}
C {devices/sg13_lv_nmos_np.sym} 1025 260 0 0 {name=MB2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb2_w l=x_dut_xmb2_l m=x_dut_xmb2_m}
C {devices/sg13_lv_nmos_np.sym} 685 780 0 0 {name=MBD model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbd_w l=x_dut_xmbd_l m=x_dut_xmbd_m}
C {devices/sg13_lv_pmos_np.sym} 1365 260 0 0 {name=MCA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmca_w l=x_dut_xmca_l m=x_dut_xmca_m}
C {devices/sg13_lv_pmos_np.sym} 1815 260 0 0 {name=MCB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcb_w l=x_dut_xmcb_l m=x_dut_xmcb_m}
C {devices/sg13_lv_nmos_np.sym} -1360 260 0 1 {name=MEA1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmea1_w l=x_dut_xmea1_l m=x_dut_xmea1_m}
C {devices/sg13_lv_nmos_np.sym} -1125 260 0 1 {name=MEA2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmea2_w l=x_dut_xmea2_l m=x_dut_xmea2_m}
C {devices/sg13_lv_nmos_np.sym} -1360 520 0 1 {name=MEAT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmeat_w l=x_dut_xmeat_l m=x_dut_xmeat_m}
C {devices/sg13_lv_pmos_np.sym} -1360 0 0 1 {name=MEPD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmepd_w l=x_dut_xmepd_l m=x_dut_xmepd_m}
C {devices/sg13_lv_pmos_np.sym} 505 0 0 1 {name=MEPM model=sg13_lv_pmos spiceprefix=X w=x_dut_xmepm_w l=x_dut_xmepm_l m=x_dut_xmepm_m}
C {devices/sg13_lv_nmos_np.sym} 1590 260 0 0 {name=MI1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmi1_w l=x_dut_xmi1_l m=x_dut_xmi1_m}
C {devices/sg13_lv_nmos_np.sym} 2045 260 0 0 {name=MI2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmi2_w l=x_dut_xmi2_l m=x_dut_xmi2_m}
C {devices/sg13_lv_nmos_np.sym} 1365 780 0 0 {name=MKA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmka_w l=x_dut_xmka_l m=x_dut_xmka_m}
C {devices/sg13_lv_nmos_np.sym} 1815 780 0 0 {name=MKB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmkb_w l=x_dut_xmkb_l m=x_dut_xmkb_m}
C {devices/sg13_lv_pmos_np.sym} -900 0 0 1 {name=MLA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmla_w l=x_dut_xmla_l m=x_dut_xmla_m}
C {devices/sg13_lv_pmos_np.sym} -560 0 0 1 {name=MLB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmlb_w l=x_dut_xmlb_l m=x_dut_xmlb_m}
C {devices/sg13_lv_nmos_np.sym} 1365 520 0 0 {name=MNA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmna_w l=x_dut_xmna_l m=x_dut_xmna_m}
C {devices/sg13_lv_nmos_np.sym} 1815 520 0 0 {name=MNB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb_w l=x_dut_xmnb_l m=x_dut_xmnb_m}
C {devices/sg13_lv_nmos_np.sym} 505 260 0 1 {name=MNCD model=sg13_lv_nmos spiceprefix=X w=x_dut_xmncd_w l=x_dut_xmncd_l m=x_dut_xmncd_m}
C {devices/sg13_lv_nmos_np.sym} 270 260 0 1 {name=MND1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnd1_w l=x_dut_xmnd1_l m=x_dut_xmnd1_m}
C {devices/sg13_lv_pmos_np.sym} -190 0 0 1 {name=MPD1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpd1_w l=x_dut_xmpd1_l m=x_dut_xmpd1_m}
C {devices/sg13_lv_pmos_np.sym} 1025 0 0 0 {name=MPD2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpd2_w l=x_dut_xmpd2_l m=x_dut_xmpd2_m}
C {devices/sg13_lv_pmos_np.sym} 270 0 0 1 {name=MPM1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpm1_w l=x_dut_xmpm1_l m=x_dut_xmpm1_m}
C {devices/sg13_lv_pmos_np.sym} 1365 0 0 0 {name=MSA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmsa_w l=x_dut_xmsa_l m=x_dut_xmsa_m}
C {devices/sg13_lv_pmos_np.sym} 1815 0 0 0 {name=MSB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmsb_w l=x_dut_xmsb_l m=x_dut_xmsb_m}
C {devices/sg13_lv_nmos_np.sym} 270 520 0 1 {name=MT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmt_w l=x_dut_xmt_l m=x_dut_xmt_m}
N -1750 430 -1750 490 {}
N -1750 550 -1750 610 {}
N -1750 690 -1750 750 {}
N -1750 810 -1750 870 {}
N -1440 0 -1440 94 {}
N -1440 260 -1440 354 {}
N -1440 520 -1440 614 {}
N -1380 -140 -1380 -30 {}
N -1380 30 -1380 230 {}
N -1380 290 -1380 490 {}
N -1380 550 -1380 920 {}
N -1340 0 -1340 70 {}
N -1205 260 -1205 354 {}
N -1145 200 -1145 230 {}
N -1145 290 -1145 320 {}
N -1140 390 -1140 450 {}
N -1075 260 -1075 390 {}
N -980 0 -980 94 {}
N -980 260 -980 354 {}
N -920 -140 -920 -30 {}
N -920 30 -920 90 {}
N -920 170 -920 230 {}
N -920 290 -920 920 {}
N -770 300 -770 360 {}
N -770 420 -770 450 {}
N -640 0 -640 94 {}
N -640 260 -640 354 {}
N -580 -140 -580 -30 {}
N -580 30 -580 90 {}
N -580 170 -580 230 {}
N -580 290 -580 920 {}
N -570 0 -570 30 {}
N -535 390 -535 450 {}
N -300 300 -300 390 {}
N -300 420 -300 450 {}
N -270 30 -270 230 {}
N -270 260 -270 354 {}
N -210 -140 -210 -30 {}
N -210 30 -210 70 {}
N -210 290 -210 920 {}
N -170 0 -170 70 {}
N -40 390 -40 450 {}
N -10 330 -10 390 {}
N 190 0 190 94 {}
N 190 260 190 354 {}
N 190 520 190 614 {}
N 195 390 195 450 {}
N 250 -140 250 -30 {}
N 250 30 250 90 {}
N 250 170 250 230 {}
N 250 290 250 350 {}
N 250 460 250 490 {}
N 250 550 250 920 {}
N 260 520 260 720 {}
N 290 190 290 260 {}
N 425 30 425 230 {}
N 425 260 425 354 {}
N 485 -140 485 -30 {}
N 485 30 485 90 {}
N 485 190 485 230 {}
N 485 290 485 920 {}
N 525 190 525 840 {}
N 545 30 545 200 {}
N 575 330 575 520 {}
N 635 320 635 520 {}
N 665 710 665 780 {}
N 705 260 705 750 {}
N 705 810 705 920 {}
N 765 780 765 874 {}
N 830 390 830 520 {}
N 920 520 920 580 {}
N 985 60 985 230 {}
N 1005 0 1005 70 {}
N 1045 -140 1045 -30 {}
N 1045 30 1045 70 {}
N 1045 170 1045 230 {}
N 1045 290 1045 920 {}
N 1105 0 1105 94 {}
N 1105 260 1105 354 {}
N 1315 780 1315 840 {}
N 1325 320 1325 490 {}
N 1345 170 1345 260 {}
N 1345 400 1345 520 {}
N 1385 -140 1385 -30 {}
N 1385 30 1385 230 {}
N 1385 290 1385 350 {}
N 1385 550 1385 750 {}
N 1385 810 1385 920 {}
N 1445 0 1445 94 {}
N 1445 260 1445 354 {}
N 1445 520 1445 614 {}
N 1445 780 1445 874 {}
N 1610 200 1610 230 {}
N 1610 290 1610 320 {}
N 1610 320 1610 350 {}
N 1670 320 1670 460 {}
N 1765 400 1765 520 {}
N 1765 780 1765 840 {}
N 1835 -140 1835 -30 {}
N 1835 30 1835 230 {}
N 1835 290 1835 350 {}
N 1835 430 1835 490 {}
N 1835 550 1835 750 {}
N 1835 810 1835 920 {}
N 1895 0 1895 94 {}
N 1895 260 1895 354 {}
N 1895 520 1895 614 {}
N 1895 780 1895 874 {}
N 2065 200 2065 230 {}
N 2065 290 2065 320 {}
N 2125 260 2125 354 {}
N -1885 -140 2545 -140 {}
N -1440 0 -1380 0 {}
N -1340 0 -1280 0 {}
N -980 0 -920 0 {}
N -880 0 -820 0 {}
N -640 0 -580 0 {}
N -570 0 -480 0 {}
N 190 0 250 0 {}
N 290 0 350 0 {}
N 525 0 585 0 {}
N 945 0 1005 0 {}
N 1045 0 1105 0 {}
N 1285 0 1345 0 {}
N 1385 0 1445 0 {}
N 1735 0 1795 0 {}
N 1835 0 1895 0 {}
N -570 30 -210 30 {}
N 425 30 545 30 {}
N 985 60 1045 60 {}
N -1380 70 -1340 70 {}
N -210 70 -170 70 {}
N 1005 70 1045 70 {}
N 1045 170 1345 170 {}
N 250 190 290 190 {}
N 485 190 525 190 {}
N -1145 200 545 200 {}
N 1385 200 1610 200 {}
N 1835 200 2065 200 {}
N -270 230 -210 230 {}
N 425 230 485 230 {}
N 985 230 1045 230 {}
N -1440 260 -1380 260 {}
N -1340 260 -1280 260 {}
N -1205 260 -1145 260 {}
N -1105 260 -1045 260 {}
N -980 260 -920 260 {}
N -880 260 -820 260 {}
N -640 260 -580 260 {}
N -540 260 -480 260 {}
N -270 260 -210 260 {}
N -170 260 -110 260 {}
N 190 260 250 260 {}
N 425 260 485 260 {}
N 705 260 1005 260 {}
N 1045 260 1105 260 {}
N 1385 260 1445 260 {}
N 1480 260 1570 260 {}
N 1735 260 1795 260 {}
N 1835 260 1895 260 {}
N 1935 260 2025 260 {}
N 2065 260 2125 260 {}
N -1380 320 -1145 320 {}
N 635 320 1385 320 {}
N 1550 320 2065 320 {}
N -10 330 575 330 {}
N -1140 390 -1050 390 {}
N -990 390 -960 390 {}
N -595 390 -535 390 {}
N -505 390 -300 390 {}
N -130 390 -100 390 {}
N -40 390 -10 390 {}
N 105 390 135 390 {}
N 195 390 830 390 {}
N 1345 400 1765 400 {}
N -1140 450 -300 450 {}
N 250 460 1670 460 {}
N 1325 490 1385 490 {}
N -1440 520 -1380 520 {}
N -1340 520 -1280 520 {}
N 190 520 250 520 {}
N 260 520 320 520 {}
N 575 520 605 520 {}
N 635 520 695 520 {}
N 830 520 860 520 {}
N 920 520 950 520 {}
N 1285 520 1345 520 {}
N 1385 520 1445 520 {}
N 1765 520 1795 520 {}
N 1835 520 1895 520 {}
N 665 710 705 710 {}
N 260 720 705 720 {}
N 705 780 765 780 {}
N 1315 780 1345 780 {}
N 1385 780 1445 780 {}
N 1765 780 1795 780 {}
N 1835 780 1895 780 {}
N 525 840 1765 840 {}
N -1885 920 2545 920 {}
C {devices/lab_wire.sym} -1280 0 0 1 {name=l0 lab=ead}
C {devices/lab_wire.sym} 585 0 0 1 {name=l1 lab=ead}
C {devices/lab_wire.sym} -1380 350 2 0 {name=l2 lab=eatail}
C {devices/lab_wire.sym} 1835 90 2 0 {name=l3 lab=fn}
C {devices/lab_wire.sym} 1385 90 2 0 {name=l4 lab=fp}
C {devices/lab_wire.sym} -1280 520 0 1 {name=l5 lab=ibias}
C {devices/lab_wire.sym} -110 260 0 1 {name=l6 lab=ibias}
C {devices/lab_wire.sym} 945 260 0 0 {name=l7 lab=ibias}
C {devices/lab_wire.sym} -820 260 0 1 {name=l8 lab=o1a}
C {devices/lab_wire.sym} 1385 350 2 0 {name=l9 lab=o1a}
C {devices/lab_wire.sym} -480 260 0 1 {name=l10 lab=o1b}
C {devices/lab_wire.sym} 920 580 2 0 {name=l11 lab=o1b}
C {devices/lab_wire.sym} 1835 350 2 0 {name=l12 lab=o1b}
C {devices/lab_wire.sym} 1835 430 0 1 {name=l13 lab=o1b}
C {devices/lab_wire.sym} 1610 350 2 0 {name=l14 lab=tail}
C {devices/lab_wire.sym} -820 0 0 1 {name=l15 lab=vbp}
C {devices/lab_wire.sym} -480 0 0 1 {name=l16 lab=vbp}
C {devices/lab_wire.sym} 350 0 0 1 {name=l17 lab=vbp}
C {devices/lab_wire.sym} 1285 0 0 0 {name=l18 lab=vbp}
C {devices/lab_wire.sym} 1735 0 0 0 {name=l19 lab=vbp}
C {devices/lab_wire.sym} 485 90 2 0 {name=l20 lab=vcmfb}
C {devices/lab_wire.sym} -1280 260 0 1 {name=l21 lab=vcmr}
C {devices/lab_wire.sym} 250 90 2 0 {name=l22 lab=vcn}
C {devices/lab_wire.sym} 250 170 0 1 {name=l23 lab=vcn}
C {devices/lab_wire.sym} 1285 520 0 0 {name=l24 lab=vcn}
C {devices/lab_wire.sym} 945 0 0 0 {name=l25 lab=vcp}
C {devices/lab_wire.sym} 1735 260 0 0 {name=l26 lab=vcp}
C {devices/lab_wire.sym} -580 90 2 0 {name=l27 lab=voutn}
C {devices/lab_wire.sym} -580 170 0 1 {name=l28 lab=voutn}
C {devices/lab_wire.sym} -300 300 0 1 {name=l29 lab=voutn}
C {devices/lab_wire.sym} -990 390 0 0 {name=l30 lab=voutp}
C {devices/lab_wire.sym} -920 90 2 0 {name=l31 lab=voutp}
C {devices/lab_wire.sym} -920 170 0 1 {name=l32 lab=voutp}
C {devices/lab_wire.sym} -770 300 0 1 {name=l33 lab=voutp}
C {devices/lab_wire.sym} -1045 260 0 1 {name=l34 lab=vsen}
C {devices/lab_wire.sym} 1385 610 2 0 {name=l35 lab=x1a}
C {devices/lab_wire.sym} 1835 610 2 0 {name=l36 lab=x1b}
C {devices/lab_wire.sym} -40 450 2 0 {name=l37 lab=za}
C {devices/lab_wire.sym} 195 450 2 0 {name=l38 lab=zb}
C {devices/lab_wire.sym} 1445 354 2 0 {name=l39 lab=vdd}
C {devices/lab_wire.sym} 1895 354 2 0 {name=l40 lab=vdd}
C {devices/lab_wire.sym} -1440 94 2 0 {name=l41 lab=vdd}
C {devices/lab_wire.sym} 485 0 0 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} -980 94 2 0 {name=l43 lab=vdd}
C {devices/lab_wire.sym} -640 94 2 0 {name=l44 lab=vdd}
C {devices/lab_wire.sym} -210 0 0 0 {name=l45 lab=vdd}
C {devices/lab_wire.sym} 1105 94 2 0 {name=l46 lab=vdd}
C {devices/lab_wire.sym} 190 94 2 0 {name=l47 lab=vdd}
C {devices/lab_wire.sym} 1445 94 2 0 {name=l48 lab=vdd}
C {devices/lab_wire.sym} 1895 94 2 0 {name=l49 lab=vdd}
C {devices/lab_wire.sym} -980 354 2 0 {name=l50 lab=vss}
C {devices/lab_wire.sym} -640 354 2 0 {name=l51 lab=vss}
C {devices/lab_wire.sym} -270 354 2 0 {name=l52 lab=vss}
C {devices/lab_wire.sym} 1105 354 2 0 {name=l53 lab=vss}
C {devices/lab_wire.sym} 765 874 2 0 {name=l54 lab=vss}
C {devices/lab_wire.sym} -1440 354 2 0 {name=l55 lab=vss}
C {devices/lab_wire.sym} -1205 354 2 0 {name=l56 lab=vss}
C {devices/lab_wire.sym} -1440 614 2 0 {name=l57 lab=vss}
C {devices/lab_wire.sym} 1610 260 0 0 {name=l58 lab=vss}
C {devices/lab_wire.sym} 2125 354 2 0 {name=l59 lab=vss}
C {devices/lab_wire.sym} 1445 874 2 0 {name=l60 lab=vss}
C {devices/lab_wire.sym} 1895 874 2 0 {name=l61 lab=vss}
C {devices/lab_wire.sym} 1445 614 2 0 {name=l62 lab=vss}
C {devices/lab_wire.sym} 1895 614 2 0 {name=l63 lab=vss}
C {devices/lab_wire.sym} 425 354 2 0 {name=l64 lab=vss}
C {devices/lab_wire.sym} 190 354 2 0 {name=l65 lab=vss}
C {devices/lab_wire.sym} 190 614 2 0 {name=l66 lab=vss}
C {devices/lab_wire.sym} -1750 690 0 1 {name=l67 lab=vdd}
C {devices/lab_wire.sym} -1750 870 2 0 {name=l68 lab=ibias}
C {devices/lab_wire.sym} -1750 430 0 1 {name=l69 lab=vcmr}
C {devices/lab_wire.sym} -1750 610 2 0 {name=l70 lab=vss}
C {devices/lab_wire.sym} 250 350 2 0 {name=l71 lab=vss}
C {devices/ipin.sym} 1480 260 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} 1935 260 0 0 {name=p1 lab=vinn}
C {devices/iopin.sym} -1885 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1885 920 0 0 {name=p3 lab=vss}
C {devices/opin.sym} -130 390 0 0 {name=p4 lab=voutp}
C {devices/opin.sym} 105 390 0 0 {name=p5 lab=voutn}
