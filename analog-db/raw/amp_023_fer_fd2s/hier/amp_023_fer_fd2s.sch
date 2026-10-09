v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_023_fer_fd2s} -1455 -600 0 0 0.4 0.4 {}
C {blocks/cm_nmos_simple_1.sym} -1195 0 0 0 {name=xcm_nmos_simple_1}
C {blocks/cm_pmos_simple_1.sym} -725 0 0 0 {name=xcm_pmos_simple_1}
C {blocks/cm_nmos_high_swing_cascode_1.sym} -240 0 0 0 {name=xcm_nmos_high_swing_cascode_1}
C {blocks/cm_pmos_simple_2.sym} 295 0 0 0 {name=xcm_pmos_simple_2}
C {blocks/dp_nmos_simple_1.sym} 785 0 0 0 {name=xdp_nmos_simple_1}
C {blocks/dp_nmos_simple_2.sym} 1225 0 0 0 {name=xdp_nmos_simple_2}
C {devices/capa_np.sym} -990 400 0 0 {name=CCA value=x_dut_cca_value}
C {devices/capa_np.sym} -770 400 0 0 {name=CCB value=x_dut_ccb_value}
C {devices/capa_np.sym} -550 400 0 0 {name=CMA value=x_dut_cma_value}
C {devices/capa_np.sym} -330 400 0 0 {name=CMB value=x_dut_cmb_value}
C {devices/isource_np.sym} -1415 400 0 0 {name=IB value="dc \{x_ibias_val\}"}
C {devices/res_np.sym} -110 400 0 0 {name=RCA value=x_dut_rca_value}
C {devices/res_np.sym} 110 400 0 0 {name=RCB value=x_dut_rcb_value}
C {devices/res_np.sym} 330 400 0 0 {name=RZA value=x_dut_rza_value}
C {devices/res_np.sym} 550 400 0 0 {name=RZB value=x_dut_rzb_value}
C {devices/vsource_np.sym} -1415 180 0 0 {name=VCR value="dc \{x_vcmr_val\}" savecurrent=false}
C {devices/sg13_lv_nmos_np.sym} 770 400 0 0 {name=M2A model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2a_w l=x_dut_xm2a_l m=x_dut_xm2a_m}
C {devices/sg13_lv_nmos_np.sym} 990 400 0 0 {name=M2B model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2b_w l=x_dut_xm2b_l m=x_dut_xm2b_m}
C {devices/sg13_lv_pmos_np.sym} -220 -400 0 0 {name=MCA model=sg13_lv_pmos spiceprefix=X w=x_dut_xmca_w l=x_dut_xmca_l m=x_dut_xmca_m}
C {devices/sg13_lv_pmos_np.sym} 0 -400 0 0 {name=MCB model=sg13_lv_pmos spiceprefix=X w=x_dut_xmcb_w l=x_dut_xmcb_l m=x_dut_xmcb_m}
C {devices/sg13_lv_pmos_np.sym} 220 -400 0 0 {name=MPD2 model=sg13_lv_pmos spiceprefix=X w=x_dut_xmpd2_w l=x_dut_xmpd2_l m=x_dut_xmpd2_m}
N -1055 -80 -1015 -80 {}
C {devices/lab_wire.sym} -1015 -80 0 1 {name=l0 lab=eatail}
N -1055 -40 -1015 -40 {}
C {devices/lab_wire.sym} -1015 -40 0 1 {name=l1 lab=ibias}
N -1055 0 -1015 0 {}
C {devices/lab_wire.sym} -1015 0 0 1 {name=l2 lab=tail}
N -1055 40 -1015 40 {}
C {devices/lab_wire.sym} -1015 40 0 1 {name=l3 lab=vbp}
N -1055 80 -1015 80 {}
C {devices/lab_wire.sym} -1015 80 0 1 {name=l4 lab=vcp}
N -1195 140 -1195 180 {}
C {devices/lab_wire.sym} -1195 180 2 0 {name=l5 lab=vss}
N -615 -20 -575 -20 {}
C {devices/lab_wire.sym} -575 -20 0 1 {name=l6 lab=ead}
N -615 20 -575 20 {}
C {devices/lab_wire.sym} -575 20 0 1 {name=l7 lab=vcmfb}
N -725 -80 -725 -120 {}
C {devices/lab_wire.sym} -725 -120 0 1 {name=l8 lab=vdd}
N -85 -60 -45 -60 {}
C {devices/lab_wire.sym} -45 -60 0 1 {name=l9 lab=o1a}
N -85 -20 -45 -20 {}
C {devices/lab_wire.sym} -45 -20 0 1 {name=l10 lab=o1b}
N -85 20 -45 20 {}
C {devices/lab_wire.sym} -45 20 0 1 {name=l11 lab=vcmfb}
N -85 60 -45 60 {}
C {devices/lab_wire.sym} -45 60 0 1 {name=l12 lab=vcn}
N -240 120 -240 160 {}
C {devices/lab_wire.sym} -240 160 2 0 {name=l13 lab=vss}
N 455 -100 495 -100 {}
C {devices/lab_wire.sym} 495 -100 0 1 {name=l14 lab=fn}
N 455 -60 495 -60 {}
C {devices/lab_wire.sym} 495 -60 0 1 {name=l15 lab=fp}
N 455 -20 495 -20 {}
C {devices/lab_wire.sym} 495 -20 0 1 {name=l16 lab=vbp}
N 455 20 495 20 {}
C {devices/lab_wire.sym} 495 20 0 1 {name=l17 lab=vcn}
N 455 60 495 60 {}
C {devices/lab_wire.sym} 495 60 0 1 {name=l18 lab=voutn}
N 455 100 495 100 {}
C {devices/lab_wire.sym} 495 100 0 1 {name=l19 lab=voutp}
N 295 -160 295 -200 {}
C {devices/lab_wire.sym} 295 -200 0 1 {name=l20 lab=vdd}
N 675 -20 635 -20 {}
C {devices/lab_wire.sym} 635 -20 0 0 {name=l21 lab=vcmr}
N 675 20 635 20 {}
C {devices/lab_wire.sym} 635 20 0 0 {name=l22 lab=vsen}
N 895 -40 935 -40 {}
C {devices/lab_wire.sym} 935 -40 0 1 {name=l23 lab=ead}
N 895 0 935 0 {}
C {devices/lab_wire.sym} 935 0 0 1 {name=l24 lab=eatail}
N 895 40 935 40 {}
C {devices/lab_wire.sym} 935 40 0 1 {name=l25 lab=vcmfb}
N 785 100 785 140 {}
C {devices/lab_wire.sym} 785 140 2 0 {name=l26 lab=vss}
N 1115 -20 1075 -20 {}
C {devices/lab_wire.sym} 1075 -20 0 0 {name=l27 lab=vinn}
N 1115 20 1075 20 {}
C {devices/lab_wire.sym} 1075 20 0 0 {name=l28 lab=vinp}
N 1335 -40 1375 -40 {}
C {devices/lab_wire.sym} 1375 -40 0 1 {name=l29 lab=fn}
N 1335 0 1375 0 {}
C {devices/lab_wire.sym} 1375 0 0 1 {name=l30 lab=fp}
N 1335 40 1375 40 {}
C {devices/lab_wire.sym} 1375 40 0 1 {name=l31 lab=tail}
N 1225 100 1225 140 {}
C {devices/lab_wire.sym} 1225 140 2 0 {name=l32 lab=vss}
N -990 370 -990 330 {}
C {devices/lab_wire.sym} -990 330 0 1 {name=l33 lab=za}
N -990 430 -990 470 {}
C {devices/lab_wire.sym} -990 470 2 0 {name=l34 lab=voutp}
N -770 370 -770 330 {}
C {devices/lab_wire.sym} -770 330 0 1 {name=l35 lab=zb}
N -770 430 -770 470 {}
C {devices/lab_wire.sym} -770 470 2 0 {name=l36 lab=voutn}
N -550 370 -550 330 {}
C {devices/lab_wire.sym} -550 330 0 1 {name=l37 lab=voutp}
N -550 430 -550 470 {}
C {devices/lab_wire.sym} -550 470 2 0 {name=l38 lab=vsen}
N -330 370 -330 330 {}
C {devices/lab_wire.sym} -330 330 0 1 {name=l39 lab=voutn}
N -330 430 -330 470 {}
C {devices/lab_wire.sym} -330 470 2 0 {name=l40 lab=vsen}
N -1415 370 -1415 330 {}
C {devices/lab_wire.sym} -1415 330 0 1 {name=l41 lab=vdd}
N -1415 430 -1415 470 {}
C {devices/lab_wire.sym} -1415 470 2 0 {name=l42 lab=ibias}
N -110 370 -110 330 {}
C {devices/lab_wire.sym} -110 330 0 1 {name=l43 lab=voutp}
N -110 430 -110 470 {}
C {devices/lab_wire.sym} -110 470 2 0 {name=l44 lab=vsen}
N 110 370 110 330 {}
C {devices/lab_wire.sym} 110 330 0 1 {name=l45 lab=voutn}
N 110 430 110 470 {}
C {devices/lab_wire.sym} 110 470 2 0 {name=l46 lab=vsen}
N 330 370 330 330 {}
C {devices/lab_wire.sym} 330 330 0 1 {name=l47 lab=o1a}
N 330 430 330 470 {}
C {devices/lab_wire.sym} 330 470 2 0 {name=l48 lab=za}
N 550 370 550 330 {}
C {devices/lab_wire.sym} 550 330 0 1 {name=l49 lab=o1b}
N 550 430 550 470 {}
C {devices/lab_wire.sym} 550 470 2 0 {name=l50 lab=zb}
N -1415 150 -1415 110 {}
C {devices/lab_wire.sym} -1415 110 0 1 {name=l51 lab=vcmr}
N -1415 210 -1415 250 {}
C {devices/lab_wire.sym} -1415 250 2 0 {name=l52 lab=vss}
N 790 370 790 330 {}
C {devices/lab_wire.sym} 790 330 0 1 {name=l53 lab=voutp}
N 750 400 710 400 {}
C {devices/lab_wire.sym} 710 400 0 0 {name=l54 lab=o1a}
N 790 430 790 470 {}
C {devices/lab_wire.sym} 790 470 2 0 {name=l55 lab=vss}
N 790 400 830 400 {}
C {devices/lab_wire.sym} 830 400 0 1 {name=l56 lab=vss}
N 1010 370 1010 330 {}
C {devices/lab_wire.sym} 1010 330 0 1 {name=l57 lab=voutn}
N 970 400 930 400 {}
C {devices/lab_wire.sym} 930 400 0 0 {name=l58 lab=o1b}
N 1010 430 1010 470 {}
C {devices/lab_wire.sym} 1010 470 2 0 {name=l59 lab=vss}
N 1010 400 1050 400 {}
C {devices/lab_wire.sym} 1050 400 0 1 {name=l60 lab=vss}
N -200 -370 -200 -330 {}
C {devices/lab_wire.sym} -200 -330 2 0 {name=l61 lab=o1a}
N -240 -400 -280 -400 {}
C {devices/lab_wire.sym} -280 -400 0 0 {name=l62 lab=vcp}
N -200 -430 -200 -470 {}
C {devices/lab_wire.sym} -200 -470 0 1 {name=l63 lab=fp}
N -200 -400 -160 -400 {}
C {devices/lab_wire.sym} -160 -400 0 1 {name=l64 lab=vdd}
N 20 -370 20 -330 {}
C {devices/lab_wire.sym} 20 -330 2 0 {name=l65 lab=o1b}
N -20 -400 -60 -400 {}
C {devices/lab_wire.sym} -60 -400 0 0 {name=l66 lab=vcp}
N 20 -430 20 -470 {}
C {devices/lab_wire.sym} 20 -470 0 1 {name=l67 lab=fn}
N 20 -400 60 -400 {}
C {devices/lab_wire.sym} 60 -400 0 1 {name=l68 lab=vdd}
N 240 -370 240 -330 {}
C {devices/lab_wire.sym} 240 -330 2 0 {name=l69 lab=vcp}
N 200 -400 160 -400 {}
C {devices/lab_wire.sym} 160 -400 0 0 {name=l70 lab=vcp}
N 240 -430 240 -470 {}
C {devices/lab_wire.sym} 240 -470 0 1 {name=l71 lab=vdd}
N 240 -400 280 -400 {}
C {devices/lab_wire.sym} 280 -400 0 1 {name=l72 lab=vdd}
