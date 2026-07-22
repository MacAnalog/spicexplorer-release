v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {ldo_005_buffered_ref} -1400 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 1010 260 1 0 {name=CC value='c_comp'}
C {devices/capa_np.sym} 360 520 0 0 {name=C_LPF value='c_lpf'}
C {devices/isource_np.sym} -1360 520 0 0 {name=IBIAS_ERR value="dc {i_tail_err}"}
C {devices/isource_np.sym} -1360 260 0 0 {name=IBIAS_REF value="dc {i_tail_ref}"}
C {devices/res_np.sym} -160 260 0 0 {name=R1 value='r_ref_top'}
C {devices/res_np.sym} -340 520 0 0 {name=R2 value='r_ref_bot'}
C {devices/res_np.sym} 785 520 0 0 {name=R3 value='r_bleed'}
C {devices/res_np.sym} 520 260 0 0 {name=RZ value='r_z'}
C {devices/res_np.sym} 20 260 1 0 {name=R_LPF value='r_lpf'}
C {devices/vsource_np.sym} -1360 0 0 0 {name=VREF value="dc {vref_val}"}
C {devices/sg13_lv_nmos_np.sym} -680 260 0 1 {name=M1 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm1_w l=x_dut_xm1_l}
C {devices/sg13_lv_pmos_np.sym} 360 0 0 1 {name=M10 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm10_w l=x_dut_xm10_l}
C {devices/sg13_lv_nmos_np.sym} 530 520 0 0 {name=M11 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm11_w l=x_dut_xm11_l}
C {devices/sg13_lv_nmos_np.sym} -1020 520 0 1 {name=M12 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm12_w l=x_dut_xm12_l}
C {devices/sg13_lv_nmos_np.sym} -340 260 0 0 {name=M2 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm2_w l=x_dut_xm2_l}
C {devices/sg13_lv_pmos_np.sym} -680 0 0 1 {name=M3 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm3_w l=x_dut_xm3_l}
C {devices/sg13_lv_pmos_np.sym} -340 0 0 0 {name=M4 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm4_w l=x_dut_xm4_l}
C {devices/sg13_lv_nmos_np.sym} -510 520 0 1 {name=M5 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm5_w l=x_dut_xm5_l}
C {devices/sg13_lv_nmos_np.sym} 20 520 0 0 {name=M6 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm6_w l=x_dut_xm6_l}
C {devices/sg13_lv_nmos_np.sym} 700 260 0 0 {name=M7 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm7_w l=x_dut_xm7_l}
C {devices/sg13_lv_nmos_np.sym} 360 260 0 1 {name=M8 model=sg13_lv_nmos spiceprefix=X w=x_dut_xm8_w l=x_dut_xm8_l}
C {devices/sg13_lv_pmos_np.sym} 700 0 0 0 {name=M9 model=sg13_lv_pmos spiceprefix=X w=x_dut_xm9_w l=x_dut_xm9_l}
C {devices/sg13_lv_pmos_np.sym} 1040 0 0 0 {name=MP model=sg13_lv_pmos spiceprefix=X w=x_dut_xmp_w l=x_dut_xmp_l m=x_dut_xmp_m}
N -1360 -90 -1360 -30 {}
N -1360 30 -1360 90 {}
N -1360 170 -1360 230 {}
N -1360 290 -1360 350 {}
N -1360 430 -1360 490 {}
N -1360 550 -1360 610 {}
N -1100 520 -1100 614 {}
N -1040 430 -1040 490 {}
N -1040 550 -1040 660 {}
N -1000 450 -1000 520 {}
N -760 0 -760 94 {}
N -760 260 -760 354 {}
N -700 -140 -700 -30 {}
N -700 30 -700 230 {}
N -700 290 -700 350 {}
N -660 0 -660 70 {}
N -590 520 -590 614 {}
N -530 430 -530 490 {}
N -530 550 -530 660 {}
N -490 520 -490 580 {}
N -390 0 -390 60 {}
N -340 430 -340 490 {}
N -340 550 -340 660 {}
N -320 -140 -320 -30 {}
N -320 30 -320 230 {}
N -320 290 -320 320 {}
N -260 0 -260 94 {}
N -260 260 -260 354 {}
N -160 200 -160 230 {}
N -160 290 -160 350 {}
N -40 200 -40 260 {}
N 0 450 0 520 {}
N 40 430 40 490 {}
N 40 550 40 660 {}
N 50 260 50 320 {}
N 100 520 100 614 {}
N 280 0 280 94 {}
N 280 260 280 354 {}
N 340 -140 340 -30 {}
N 340 30 340 230 {}
N 340 290 340 350 {}
N 360 430 360 490 {}
N 360 550 360 660 {}
N 380 260 380 320 {}
N 480 460 480 520 {}
N 510 460 510 520 {}
N 520 200 520 230 {}
N 520 290 520 350 {}
N 550 430 550 490 {}
N 550 550 550 660 {}
N 610 520 610 614 {}
N 680 0 680 70 {}
N 680 200 680 260 {}
N 720 -140 720 -30 {}
N 720 30 720 70 {}
N 720 170 720 230 {}
N 720 290 720 350 {}
N 780 0 780 94 {}
N 780 260 780 354 {}
N 785 260 785 490 {}
N 785 550 785 660 {}
N 950 260 950 320 {}
N 980 200 980 260 {}
N 990 0 990 200 {}
N 1040 260 1040 320 {}
N 1060 -140 1060 -30 {}
N 1060 30 1060 460 {}
N 1120 0 1120 94 {}
N -1420 -140 1250 -140 {}
N -760 0 -700 0 {}
N -660 0 -600 0 {}
N -390 0 -360 0 {}
N -320 0 -260 0 {}
N 280 0 340 0 {}
N 380 0 440 0 {}
N 620 0 680 0 {}
N 720 0 780 0 {}
N 960 0 1020 0 {}
N 1060 0 1120 0 {}
N -700 60 -390 60 {}
N -700 70 -660 70 {}
N 680 70 720 70 {}
N -320 200 -40 200 {}
N 340 200 520 200 {}
N -760 260 -700 260 {}
N -660 260 -600 260 {}
N -420 260 -340 260 {}
N -320 260 -260 260 {}
N -40 260 -10 260 {}
N 50 260 80 260 {}
N 280 260 340 260 {}
N 360 260 410 260 {}
N 650 260 680 260 {}
N 720 260 780 260 {}
N 950 260 980 260 {}
N 1040 260 1070 260 {}
N -700 320 -320 320 {}
N -1040 450 -1000 450 {}
N 0 450 40 450 {}
N 785 460 1060 460 {}
N -1100 520 -1040 520 {}
N -590 520 -530 520 {}
N -490 520 -460 520 {}
N 40 520 100 520 {}
N 480 520 510 520 {}
N 550 520 610 520 {}
N -1420 660 1250 660 {}
C {devices/lab_wire.sym} -1420 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -1420 660 0 0 {name=l1 lab=vss}
C {devices/lab_wire.sym} -1040 430 0 1 {name=l2 lab=ebias_err}
C {devices/lab_wire.sym} 510 460 0 1 {name=l3 lab=ebias_err}
C {devices/lab_wire.sym} -490 580 2 0 {name=l4 lab=ebias_ref}
C {devices/lab_wire.sym} 40 430 0 1 {name=l5 lab=ebias_ref}
C {devices/lab_wire.sym} 340 90 2 0 {name=l6 lab=egate}
C {devices/lab_wire.sym} 960 0 0 0 {name=l7 lab=egate}
C {devices/lab_wire.sym} 340 350 2 0 {name=l8 lab=etail}
C {devices/lab_wire.sym} 550 430 0 1 {name=l9 lab=etail}
C {devices/lab_wire.sym} 720 350 2 0 {name=l10 lab=etail}
C {devices/lab_wire.sym} 520 350 2 0 {name=l11 lab=ncz}
C {devices/lab_wire.sym} 980 200 0 1 {name=l12 lab=ncz}
C {devices/lab_wire.sym} 440 0 0 1 {name=l13 lab=noutm}
C {devices/lab_wire.sym} 620 0 0 0 {name=l14 lab=noutm}
C {devices/lab_wire.sym} 720 170 0 1 {name=l15 lab=noutm}
C {devices/lab_wire.sym} -600 0 0 1 {name=l16 lab=rd1}
C {devices/lab_wire.sym} -700 350 2 0 {name=l17 lab=retail}
C {devices/lab_wire.sym} -530 430 0 1 {name=l18 lab=retail}
C {devices/lab_wire.sym} 50 320 2 0 {name=l19 lab=v_lpf_out}
C {devices/lab_wire.sym} 360 430 0 1 {name=l20 lab=v_lpf_out}
C {devices/lab_wire.sym} 380 320 2 0 {name=l21 lab=v_lpf_out}
C {devices/lab_wire.sym} -420 260 0 0 {name=l22 lab=v_ref_fb}
C {devices/lab_wire.sym} -340 430 0 1 {name=l23 lab=v_ref_fb}
C {devices/lab_wire.sym} -160 350 2 0 {name=l24 lab=v_ref_fb}
C {devices/lab_wire.sym} -320 90 2 0 {name=l25 lab=v_ref_out}
C {devices/lab_wire.sym} 680 200 0 1 {name=l26 lab=vout}
C {devices/lab_wire.sym} 1060 90 2 0 {name=l27 lab=vout}
C {devices/lab_wire.sym} 1040 320 2 0 {name=l28 lab=vout}
C {devices/lab_wire.sym} -600 260 0 1 {name=l29 lab=vref}
C {devices/lab_wire.sym} 280 94 2 0 {name=l30 lab=vdd}
C {devices/lab_wire.sym} -760 94 2 0 {name=l31 lab=vdd}
C {devices/lab_wire.sym} -260 94 2 0 {name=l32 lab=vdd}
C {devices/lab_wire.sym} 780 94 2 0 {name=l33 lab=vdd}
C {devices/lab_wire.sym} 1120 94 2 0 {name=l34 lab=vdd}
C {devices/lab_wire.sym} -760 354 2 0 {name=l35 lab=vss}
C {devices/lab_wire.sym} 610 614 2 0 {name=l36 lab=vss}
C {devices/lab_wire.sym} -1100 614 2 0 {name=l37 lab=vss}
C {devices/lab_wire.sym} -260 354 2 0 {name=l38 lab=vss}
C {devices/lab_wire.sym} -590 614 2 0 {name=l39 lab=vss}
C {devices/lab_wire.sym} 100 614 2 0 {name=l40 lab=vss}
C {devices/lab_wire.sym} 780 354 2 0 {name=l41 lab=vss}
C {devices/lab_wire.sym} 280 354 2 0 {name=l42 lab=vss}
C {devices/lab_wire.sym} -1360 90 2 0 {name=l43 lab=vss}
C {devices/lab_wire.sym} -1360 430 0 1 {name=l44 lab=vdd}
C {devices/lab_wire.sym} -1360 170 0 1 {name=l45 lab=vdd}
C {devices/lab_wire.sym} -1360 610 2 0 {name=l46 lab=ebias_err}
C {devices/lab_wire.sym} -1360 350 2 0 {name=l47 lab=ebias_ref}
C {devices/lab_wire.sym} -1360 -90 0 1 {name=l48 lab=vref}
C {devices/opin.sym} 1390 30 0 0 {name=p0 lab=vout}
