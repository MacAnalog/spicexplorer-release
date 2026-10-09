v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {amp_029_two_stage_miller_comp} -1060 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 990 260 1 0 {name=C1 value='x_dut_c1_value'}
C {devices/capa_np.sym} 1235 260 1 0 {name=C2 value='x_dut_c2_value'}
C {devices/isource_np.sym} -1020 520 0 0 {name=IBIAS value="dc \{i_bias\}"}
C {devices/res_np.sym} -110 260 1 0 {name=R1 value='x_dut_r1_value'}
C {devices/res_np.sym} 145 260 1 0 {name=R2 value='x_dut_r2_value'}
C {devices/vsource_np.sym} -1020 260 0 0 {name=VBL value="dc \{vbl\}" savecurrent=false}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l m=x_dut_xm1_m}
C {devices/sg13_lv_nmos_np.sym} 725 260 0 0 {name=M10 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l m=x_dut_xm10_m}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l m=x_dut_xm2_m}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l m=x_dut_xm3_m}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l m=x_dut_xm4_m}
C {devices/sg13_lv_pmos_np.sym} 385 0 0 0 {name=M5 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l m=x_dut_xm5_m}
C {devices/sg13_lv_nmos_np.sym} 0 520 0 1 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l m=x_dut_xm6_m}
C {devices/sg13_lv_nmos_np.sym} 385 260 0 0 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l m=x_dut_xm7_m}
C {devices/sg13_lv_nmos_np.sym} -510 520 0 1 {name=M8 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l m=x_dut_xm8_m}
C {devices/sg13_lv_pmos_np.sym} 725 0 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l m=x_dut_xm9_m}
N -1020 170 -1020 230 {}
N -1020 290 -1020 350 {}
N -1020 430 -1020 490 {}
N -1020 550 -1020 610 {}
N -760 0 -760 94 {}
N -760 260 -760 354 {}
N -700 -140 -700 -30 {}
N -700 30 -700 230 {}
N -700 290 -700 350 {}
N -590 520 -590 614 {}
N -530 320 -530 490 {}
N -530 550 -530 660 {}
N -460 460 -460 520 {}
N -380 60 -380 230 {}
N -320 -140 -320 -30 {}
N -320 30 -320 90 {}
N -320 170 -320 230 {}
N -320 290 -320 320 {}
N -260 0 -260 94 {}
N -260 260 -260 354 {}
N -80 260 -80 320 {}
N -80 520 -80 614 {}
N -20 450 -20 460 {}
N -20 460 -20 490 {}
N -20 550 -20 660 {}
N 20 450 20 460 {}
N 20 460 20 520 {}
N 205 170 205 260 {}
N 335 260 335 460 {}
N 405 -140 405 -30 {}
N 405 30 405 230 {}
N 405 290 405 660 {}
N 465 0 465 94 {}
N 465 260 465 354 {}
N 745 -140 745 -30 {}
N 745 30 745 90 {}
N 745 170 745 230 {}
N 745 290 745 660 {}
N 805 0 805 94 {}
N 805 260 805 354 {}
N 1020 260 1020 320 {}
N 1265 260 1265 320 {}
N -1155 -140 1545 -140 {}
N -760 0 -700 0 {}
N -660 0 -360 0 {}
N -320 0 -260 0 {}
N 305 0 365 0 {}
N 405 0 465 0 {}
N 645 0 705 0 {}
N 745 0 805 0 {}
N -380 60 -320 60 {}
N -320 170 205 170 {}
N -380 230 -320 230 {}
N -760 260 -700 260 {}
N -660 260 -630 260 {}
N -450 260 -360 260 {}
N -320 260 -260 260 {}
N -200 260 -140 260 {}
N -80 260 -50 260 {}
N 55 260 115 260 {}
N 175 260 205 260 {}
N 305 260 365 260 {}
N 405 260 465 260 {}
N 645 260 705 260 {}
N 745 260 805 260 {}
N 930 260 960 260 {}
N 1020 260 1050 260 {}
N 1175 260 1205 260 {}
N 1265 260 1295 260 {}
N -700 320 -320 320 {}
N -20 450 20 450 {}
N -460 460 335 460 {}
N -590 520 -530 520 {}
N -490 520 -460 520 {}
N -80 520 -20 520 {}
N -1155 660 1545 660 {}
C {devices/lab_wire.sym} 55 260 0 0 {name=l0 lab=mill_n}
C {devices/lab_wire.sym} 1265 320 2 0 {name=l1 lab=mill_n}
C {devices/lab_wire.sym} -200 260 0 0 {name=l2 lab=mill_p}
C {devices/lab_wire.sym} 1020 320 2 0 {name=l3 lab=mill_p}
C {devices/lab_wire.sym} 305 260 0 0 {name=l4 lab=ref}
C {devices/lab_wire.sym} 645 260 0 0 {name=l5 lab=ref}
C {devices/lab_wire.sym} -320 90 2 0 {name=l6 lab=stg1n}
C {devices/lab_wire.sym} 645 0 0 0 {name=l7 lab=stg1n}
C {devices/lab_wire.sym} -700 90 2 0 {name=l8 lab=stg1p}
C {devices/lab_wire.sym} -80 320 2 0 {name=l9 lab=stg1p}
C {devices/lab_wire.sym} 305 0 0 0 {name=l10 lab=stg1p}
C {devices/lab_wire.sym} -700 350 2 0 {name=l11 lab=tail}
C {devices/lab_wire.sym} -600 0 0 1 {name=l12 lab=vbl}
C {devices/lab_wire.sym} 745 90 2 0 {name=l13 lab=voutn}
C {devices/lab_wire.sym} 745 170 0 1 {name=l14 lab=voutn}
C {devices/lab_wire.sym} 405 90 2 0 {name=l15 lab=voutp}
C {devices/lab_wire.sym} -760 94 2 0 {name=l16 lab=vdd}
C {devices/lab_wire.sym} -260 94 2 0 {name=l17 lab=vdd}
C {devices/lab_wire.sym} 465 94 2 0 {name=l18 lab=vdd}
C {devices/lab_wire.sym} 805 94 2 0 {name=l19 lab=vdd}
C {devices/lab_wire.sym} -760 354 2 0 {name=l20 lab=vss}
C {devices/lab_wire.sym} 805 354 2 0 {name=l21 lab=vss}
C {devices/lab_wire.sym} -260 354 2 0 {name=l22 lab=vss}
C {devices/lab_wire.sym} -80 614 2 0 {name=l23 lab=vss}
C {devices/lab_wire.sym} 465 354 2 0 {name=l24 lab=vss}
C {devices/lab_wire.sym} -590 614 2 0 {name=l25 lab=vss}
C {devices/lab_wire.sym} -1020 430 0 1 {name=l26 lab=vdd}
C {devices/lab_wire.sym} -1020 610 2 0 {name=l27 lab=ref}
C {devices/lab_wire.sym} -1020 170 0 1 {name=l28 lab=vbl}
C {devices/lab_wire.sym} -1020 350 2 0 {name=l29 lab=vss}
C {devices/ipin.sym} -630 260 0 0 {name=p0 lab=vinp}
C {devices/ipin.sym} -450 260 0 0 {name=p1 lab=vinn}
C {devices/iopin.sym} -1155 -140 0 0 {name=p2 lab=vdd}
C {devices/iopin.sym} -1155 660 0 0 {name=p3 lab=vss}
C {devices/opin.sym} 930 260 0 0 {name=p4 lab=voutp}
C {devices/opin.sym} 1175 260 0 0 {name=p5 lab=voutn}
