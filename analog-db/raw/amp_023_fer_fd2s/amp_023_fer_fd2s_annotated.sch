v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_023_fer_fd2s} -1790 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 180 390 1 0 {name=CCA value=x_dut_cca_value}
C {devices/capa_np.sym} 415 390 1 0 {name=CCB value=x_dut_ccb_value}
C {devices/capa_np.sym} -875 390 1 0 {name=CMA value=x_dut_cma_value}
C {devices/capa_np.sym} -330 390 1 0 {name=CMB value=x_dut_cmb_value}
C {devices/isource_np.sym} -1750 780 0 0 {name=IB value="dc \{x_ibias_val\}"}
C {devices/res_np.sym} -565 390 0 0 {name=RCA value=x_dut_rca_value}
C {devices/res_np.sym} -100 390 1 0 {name=RCB value=x_dut_rcb_value}
C {devices/res_np.sym} 560 520 1 0 {name=RZA value=x_dut_rza_value}
C {devices/res_np.sym} 815 520 1 0 {name=RZB value=x_dut_rzb_value}
C {devices/vsource_np.sym} -1750 520 0 0 {name=VCR value="dc \{x_vcmr_val\}" savecurrent=false}
C {devices/sg13_lv_nmos_np.sym} -605 260 0 1 {name=M2A model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2a_w l=x_dut_xm2a_l m=x_dut_xm2a_m}
C {devices/sg13_lv_nmos_np.sym} -225 260 0 1 {name=M2B model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2b_w l=x_dut_xm2b_l m=x_dut_xm2b_m}
C {devices/sg13_lv_nmos_np.sym} 115 260 0 0 {name=MB1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb1_w l=x_dut_xmb1_l m=x_dut_xmb1_m}
C {devices/sg13_lv_nmos_np.sym} 520 260 0 0 {name=MB2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmb2_w l=x_dut_xmb2_l m=x_dut_xmb2_m}
C {devices/sg13_lv_nmos_np.sym} -945 780 0 1 {name=MBD model=sg13_lv_nmos spiceprefix=X w=x_dut_xmbd_w l=x_dut_xmbd_l m=x_dut_xmbd_m}
C {devices/sg13_lv_pmos_np.sym} 1330 260 0 0 {name=MCA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmca_w l=x_dut_xmca_l m=x_dut_xmca_m}
C {devices/sg13_lv_pmos_np.sym} 1780 260 0 0 {name=MCB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcb_w l=x_dut_xmcb_l m=x_dut_xmcb_m}
C {devices/sg13_lv_nmos_np.sym} -1360 260 0 1 {name=MEA1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmea1_w l=x_dut_xmea1_l m=x_dut_xmea1_m}
C {devices/sg13_lv_nmos_np.sym} -1125 260 0 1 {name=MEA2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmea2_w l=x_dut_xmea2_l m=x_dut_xmea2_m}
C {devices/sg13_lv_nmos_np.sym} -1360 520 0 1 {name=MEAT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmeat_w l=x_dut_xmeat_l m=x_dut_xmeat_m}
C {devices/sg13_lv_pmos_np.sym} -1360 0 0 1 {name=MEPD model=sg13_lv_pmos spiceprefix=X w=x_dut_xmepd_w l=x_dut_xmepd_l m=x_dut_xmepd_m}
C {devices/sg13_lv_pmos_np.sym} -1125 0 0 1 {name=MEPM model=sg13_lv_pmos spiceprefix=X w=x_dut_xmepm_w l=x_dut_xmepm_l m=x_dut_xmepm_m}
C {devices/sg13_lv_nmos_np.sym} 1555 260 0 0 {name=MI1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmi1_w l=x_dut_xmi1_l m=x_dut_xmi1_m}
C {devices/sg13_lv_nmos_np.sym} 2005 260 0 0 {name=MI2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmi2_w l=x_dut_xmi2_l m=x_dut_xmi2_m}
C {devices/sg13_lv_nmos_np.sym} 1330 780 0 0 {name=MKA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmka_w l=x_dut_xmka_l m=x_dut_xmka_m}
C {devices/sg13_lv_nmos_np.sym} 1780 780 0 0 {name=MKB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmkb_w l=x_dut_xmkb_l m=x_dut_xmkb_m}
C {devices/sg13_lv_pmos_np.sym} -605 0 0 1 {name=MLA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmla_w l=x_dut_xmla_l m=x_dut_xmla_m}
C {devices/sg13_lv_pmos_np.sym} -225 0 0 1 {name=MLB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmlb_w l=x_dut_xmlb_l m=x_dut_xmlb_m}
C {devices/sg13_lv_nmos_np.sym} 1330 520 0 0 {name=MNA model=sg13_lv_nmos spiceprefix=X w=x_dut_xmna_w l=x_dut_xmna_l m=x_dut_xmna_m}
C {devices/sg13_lv_nmos_np.sym} 1780 520 0 0 {name=MNB model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnb_w l=x_dut_xmnb_l m=x_dut_xmnb_m}
C {devices/sg13_lv_nmos_np.sym} 1095 260 0 0 {name=MNCD model=sg13_lv_nmos spiceprefix=X w=x_dut_xmncd_w l=x_dut_xmncd_l m=x_dut_xmncd_m}
C {devices/sg13_lv_nmos_np.sym} 860 260 0 0 {name=MND1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xmnd1_w l=x_dut_xmnd1_l m=x_dut_xmnd1_m}
C {devices/sg13_lv_pmos_np.sym} 115 0 0 0 {name=MPD1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpd1_w l=x_dut_xmpd1_l m=x_dut_xmpd1_m}
C {devices/sg13_lv_pmos_np.sym} 520 0 0 0 {name=MPD2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpd2_w l=x_dut_xmpd2_l m=x_dut_xmpd2_m}
C {devices/sg13_lv_pmos_np.sym} 860 0 0 0 {name=MPM1 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpm1_w l=x_dut_xmpm1_l m=x_dut_xmpm1_m}
C {devices/sg13_lv_pmos_np.sym} 1330 0 0 0 {name=MSA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmsa_w l=x_dut_xmsa_l m=x_dut_xmsa_m}
C {devices/sg13_lv_pmos_np.sym} 1780 0 0 0 {name=MSB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmsb_w l=x_dut_xmsb_l m=x_dut_xmsb_m}
C {devices/sg13_lv_nmos_np.sym} -110 520 0 0 {name=MT model=sg13_lv_nmos spiceprefix=X w=x_dut_xmt_w l=x_dut_xmt_l m=x_dut_xmt_m}
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
N -1340 -60 -1340 70 {}
N -1205 30 -1205 200 {}
N -1205 260 -1205 354 {}
N -1145 -140 -1145 -30 {}
N -1145 30 -1145 90 {}
N -1145 200 -1145 230 {}
N -1145 290 -1145 320 {}
N -1105 260 -1105 320 {}
N -1075 -60 -1075 0 {}
N -1025 780 -1025 874 {}
N -995 390 -995 450 {}
N -965 520 -965 750 {}
N -965 810 -965 920 {}
N -935 260 -935 390 {}
N -925 710 -925 780 {}
N -685 0 -685 94 {}
N -685 260 -685 354 {}
N -625 -140 -625 -30 {}
N -625 30 -625 90 {}
N -625 170 -625 230 {}
N -625 290 -625 920 {}
N -565 300 -565 360 {}
N -565 390 -565 450 {}
N -555 -60 -555 0 {}
N -305 60 -305 230 {}
N -305 260 -305 354 {}
N -245 -140 -245 -30 {}
N -245 30 -245 60 {}
N -245 60 -245 90 {}
N -245 290 -245 920 {}
N -185 60 -185 390 {}
N -175 -60 -175 0 {}
N -90 460 -90 490 {}
N -90 550 -90 920 {}
N -30 520 -30 614 {}
N 20 230 20 390 {}
N 65 200 65 260 {}
N 65 260 65 720 {}
N 75 60 75 230 {}
N 95 0 95 70 {}
N 135 -140 135 -30 {}
N 135 30 135 70 {}
N 135 290 135 920 {}
N 195 0 195 94 {}
N 195 260 195 354 {}
N 210 390 210 450 {}
N 445 390 445 450 {}
N 470 200 470 260 {}
N 500 0 500 70 {}
N 540 -140 540 -30 {}
N 540 30 540 70 {}
N 540 170 540 230 {}
N 540 290 540 920 {}
N 590 520 590 580 {}
N 600 0 600 94 {}
N 600 260 600 354 {}
N 755 390 755 520 {}
N 840 190 840 260 {}
N 845 520 845 580 {}
N 880 -140 880 -30 {}
N 880 30 880 90 {}
N 880 170 880 230 {}
N 880 290 880 920 {}
N 940 0 940 94 {}
N 940 260 940 354 {}
N 1075 190 1075 260 {}
N 1115 170 1115 230 {}
N 1115 290 1115 920 {}
N 1175 260 1175 354 {}
N 1280 780 1280 840 {}
N 1290 320 1290 490 {}
N 1310 400 1310 520 {}
N 1350 -140 1350 -30 {}
N 1350 30 1350 230 {}
N 1350 290 1350 350 {}
N 1350 550 1350 750 {}
N 1350 810 1350 920 {}
N 1410 0 1410 94 {}
N 1410 260 1410 354 {}
N 1410 520 1410 614 {}
N 1410 780 1410 874 {}
N 1575 200 1575 230 {}
N 1575 290 1575 320 {}
N 1575 320 1575 350 {}
N 1635 320 1635 460 {}
N 1730 400 1730 520 {}
N 1730 780 1730 840 {}
N 1800 -140 1800 -30 {}
N 1800 30 1800 230 {}
N 1800 290 1800 350 {}
N 1800 430 1800 490 {}
N 1800 550 1800 750 {}
N 1800 810 1800 920 {}
N 1860 0 1860 94 {}
N 1860 260 1860 354 {}
N 1860 520 1860 614 {}
N 1860 780 1860 874 {}
N 2025 200 2025 230 {}
N 2025 290 2025 320 {}
N 2085 260 2085 354 {}
N -1885 -140 2505 -140 {}
N -1340 -60 -1075 -60 {}
N -555 -60 -175 -60 {}
N -1440 0 -1380 0 {}
N -1340 0 -1280 0 {}
N -1105 0 -1075 0 {}
N -685 0 -625 0 {}
N -585 0 -525 0 {}
N -235 0 95 0 {}
N 135 0 195 0 {}
N 440 0 500 0 {}
N 540 0 600 0 {}
N 780 0 840 0 {}
N 880 0 940 0 {}
N 1250 0 1310 0 {}
N 1350 0 1410 0 {}
N 1700 0 1760 0 {}
N 1800 0 1860 0 {}
N -1205 30 -1145 30 {}
N -305 60 -185 60 {}
N 75 60 135 60 {}
N -1380 70 -1340 70 {}
N 95 70 135 70 {}
N 500 70 540 70 {}
N 840 190 880 190 {}
N 1075 190 1115 190 {}
N -1205 200 -1145 200 {}
N 65 200 470 200 {}
N 1350 200 1575 200 {}
N 1800 200 2025 200 {}
N -305 230 20 230 {}
N 75 230 135 230 {}
N -1440 260 -1380 260 {}
N -1340 260 -1280 260 {}
N -1205 260 -1145 260 {}
N -1105 260 -935 260 {}
N -685 260 -625 260 {}
N -585 260 -525 260 {}
N -305 260 -245 260 {}
N -205 260 -145 260 {}
N 35 260 95 260 {}
N 135 260 195 260 {}
N 470 260 500 260 {}
N 540 260 600 260 {}
N 880 260 940 260 {}
N 1115 260 1175 260 {}
N 1250 260 1310 260 {}
N 1350 260 1410 260 {}
N 1445 260 1535 260 {}
N 1700 260 1760 260 {}
N 1800 260 1860 260 {}
N 1895 260 1985 260 {}
N 2025 260 2085 260 {}
N -1380 320 -1145 320 {}
N 1290 320 1350 320 {}
N 1515 320 2025 320 {}
N -995 390 -905 390 {}
N -845 390 -815 390 {}
N -565 390 -360 390 {}
N -300 390 -185 390 {}
N -160 390 -130 390 {}
N -70 390 20 390 {}
N 120 390 150 390 {}
N 210 390 240 390 {}
N 355 390 385 390 {}
N 445 390 755 390 {}
N 1310 400 1730 400 {}
N -995 450 -565 450 {}
N -90 460 1635 460 {}
N 1290 490 1350 490 {}
N -1440 520 -1380 520 {}
N -1340 520 -130 520 {}
N -90 520 -30 520 {}
N 470 520 530 520 {}
N 590 520 620 520 {}
N 755 520 785 520 {}
N 845 520 875 520 {}
N 1250 520 1310 520 {}
N 1350 520 1410 520 {}
N 1730 520 1760 520 {}
N 1800 520 1860 520 {}
N -965 710 -925 710 {}
N -965 720 65 720 {}
N -1025 780 -965 780 {}
N 1250 780 1310 780 {}
N 1350 780 1410 780 {}
N 1730 780 1760 780 {}
N 1800 780 1860 780 {}
N 1280 840 1730 840 {}
N -1885 920 2505 920 {}
C {devices/lab_wire.sym} -1280 0 0 1 {name=l0 lab=ead}
C {devices/lab_wire.sym} -1380 350 2 0 {name=l1 lab=eatail}
C {devices/lab_wire.sym} 1800 90 2 0 {name=l2 lab=fn}
C {devices/lab_wire.sym} 1350 90 2 0 {name=l3 lab=fp}
C {devices/lab_wire.sym} 35 260 0 0 {name=l4 lab=ibias}
C {devices/lab_wire.sym} -525 260 0 1 {name=l5 lab=o1a}
C {devices/lab_wire.sym} 590 580 2 0 {name=l6 lab=o1a}
C {devices/lab_wire.sym} 1350 350 2 0 {name=l7 lab=o1a}
C {devices/lab_wire.sym} -145 260 0 1 {name=l8 lab=o1b}
C {devices/lab_wire.sym} 845 580 2 0 {name=l9 lab=o1b}
C {devices/lab_wire.sym} 1800 350 2 0 {name=l10 lab=o1b}
C {devices/lab_wire.sym} 1800 430 0 1 {name=l11 lab=o1b}
C {devices/lab_wire.sym} 1575 350 2 0 {name=l12 lab=tail}
C {devices/lab_wire.sym} -525 0 0 1 {name=l13 lab=vbp}
C {devices/lab_wire.sym} 780 0 0 0 {name=l14 lab=vbp}
C {devices/lab_wire.sym} 1250 0 0 0 {name=l15 lab=vbp}
C {devices/lab_wire.sym} 1700 0 0 0 {name=l16 lab=vbp}
C {devices/lab_wire.sym} -1145 90 2 0 {name=l17 lab=vcmfb}
C {devices/lab_wire.sym} 1115 170 0 1 {name=l18 lab=vcmfb}
C {devices/lab_wire.sym} 1250 780 0 0 {name=l19 lab=vcmfb}
C {devices/lab_wire.sym} -1280 260 0 1 {name=l20 lab=vcmr}
C {devices/lab_wire.sym} 880 170 0 1 {name=l21 lab=vcn}
C {devices/lab_wire.sym} 880 90 2 0 {name=l22 lab=vcn}
C {devices/lab_wire.sym} 1250 520 0 0 {name=l23 lab=vcn}
C {devices/lab_wire.sym} 440 0 0 0 {name=l24 lab=vcp}
C {devices/lab_wire.sym} 540 170 0 1 {name=l25 lab=vcp}
C {devices/lab_wire.sym} 1250 260 0 0 {name=l26 lab=vcp}
C {devices/lab_wire.sym} 1700 260 0 0 {name=l27 lab=vcp}
C {devices/lab_wire.sym} -245 90 2 0 {name=l28 lab=voutn}
C {devices/lab_wire.sym} -845 390 0 0 {name=l29 lab=voutp}
C {devices/lab_wire.sym} -625 90 2 0 {name=l30 lab=voutp}
C {devices/lab_wire.sym} -625 170 0 1 {name=l31 lab=voutp}
C {devices/lab_wire.sym} -565 300 0 1 {name=l32 lab=voutp}
C {devices/lab_wire.sym} -1105 320 2 0 {name=l33 lab=vsen}
C {devices/lab_wire.sym} -130 390 0 0 {name=l34 lab=vsen}
C {devices/lab_wire.sym} 1350 610 2 0 {name=l35 lab=x1a}
C {devices/lab_wire.sym} 1800 610 2 0 {name=l36 lab=x1b}
C {devices/lab_wire.sym} 210 450 2 0 {name=l37 lab=za}
C {devices/lab_wire.sym} 470 520 0 0 {name=l38 lab=za}
C {devices/lab_wire.sym} 445 450 2 0 {name=l39 lab=zb}
C {devices/lab_wire.sym} 1410 354 2 0 {name=l40 lab=vdd}
C {devices/lab_wire.sym} 1860 354 2 0 {name=l41 lab=vdd}
C {devices/lab_wire.sym} -1440 94 2 0 {name=l42 lab=vdd}
C {devices/lab_wire.sym} -1145 0 0 0 {name=l43 lab=vdd}
C {devices/lab_wire.sym} -685 94 2 0 {name=l44 lab=vdd}
C {devices/lab_wire.sym} -245 0 0 0 {name=l45 lab=vdd}
C {devices/lab_wire.sym} 195 94 2 0 {name=l46 lab=vdd}
C {devices/lab_wire.sym} 600 94 2 0 {name=l47 lab=vdd}
C {devices/lab_wire.sym} 940 94 2 0 {name=l48 lab=vdd}
C {devices/lab_wire.sym} 1410 94 2 0 {name=l49 lab=vdd}
C {devices/lab_wire.sym} 1860 94 2 0 {name=l50 lab=vdd}
C {devices/lab_wire.sym} -685 354 2 0 {name=l51 lab=vss}
C {devices/lab_wire.sym} -305 354 2 0 {name=l52 lab=vss}
C {devices/lab_wire.sym} 195 354 2 0 {name=l53 lab=vss}
C {devices/lab_wire.sym} 600 354 2 0 {name=l54 lab=vss}
C {devices/lab_wire.sym} -1025 874 2 0 {name=l55 lab=vss}
C {devices/lab_wire.sym} -1440 354 2 0 {name=l56 lab=vss}
C {devices/lab_wire.sym} -1205 354 2 0 {name=l57 lab=vss}
C {devices/lab_wire.sym} -1440 614 2 0 {name=l58 lab=vss}
C {devices/lab_wire.sym} 1575 260 0 0 {name=l59 lab=vss}
C {devices/lab_wire.sym} 2085 354 2 0 {name=l60 lab=vss}
C {devices/lab_wire.sym} 1410 874 2 0 {name=l61 lab=vss}
C {devices/lab_wire.sym} 1860 874 2 0 {name=l62 lab=vss}
C {devices/lab_wire.sym} 1410 614 2 0 {name=l63 lab=vss}
C {devices/lab_wire.sym} 1860 614 2 0 {name=l64 lab=vss}
C {devices/lab_wire.sym} 1175 354 2 0 {name=l65 lab=vss}
C {devices/lab_wire.sym} 940 354 2 0 {name=l66 lab=vss}
C {devices/lab_wire.sym} -30 614 2 0 {name=l67 lab=vss}
C {devices/lab_wire.sym} -1750 690 0 1 {name=l68 lab=vdd}
C {devices/lab_wire.sym} -1750 870 2 0 {name=l69 lab=ibias}
C {devices/lab_wire.sym} -1750 430 0 1 {name=l70 lab=vcmr}
C {devices/lab_wire.sym} -1750 610 2 0 {name=l71 lab=vss}
C {devices/ipin.sym} 1445 260 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} 1895 260 0 0 {name=p1 lab=vinn}
C {devices/iopin.sym} -1885 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1885 920 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 120 390 0 0 {name=p4 lab=voutp}
C {devices/opin.sym} 355 390 0 0 {name=p5 lab=voutn}
B 8 -1864 182 1000 858 {fill=0}
T {NMOS Simple Current Mirror (4 outputs)} -1864 164 0 0 0.3 0.3 {layer=8}
B 10 -1864 -78 -1055 78 {fill=0}
T {PMOS Simple Current Mirror} -1864 -96 0 0 0.3 0.3 {layer=10}
B 12 790 182 2260 858 {fill=0}
T {NMOS High Swing Cascode Current Mirror (2 outputs)} 790 164 0 0 0.3 0.3 {layer=12}
B 21 -1085 -78 2260 78 {fill=0}
T {PMOS Simple Current Mirror (5 outputs)} -1085 -96 0 0 0.3 0.3 {layer=21}
B 15 -1864 182 -1055 338 {fill=0}
T {NMOS Differential Pair} -1864 140 0 0 0.3 0.3 {layer=15}
B 13 1485 182 2485 338 {fill=0}
T {NMOS Differential Pair} 1485 164 0 0 0.3 0.3 {layer=13}
B 18 1047 204 1788 836 {fill=0 dash=4}
T {NMOS Simple Current Mirror} 1047 186 0 0 0.3 0.3 {layer=18}
B 20 1047 204 2238 836 {fill=0 dash=4}
T {NMOS Simple Current Mirror} 1047 162 0 0 0.3 0.3 {layer=20}
