v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {psrr_tb} -40 -200 0 0 0.4 0.4 {}
C {devices/vsource.sym} 480 0 0 0 {name=VDD value="dc \{VDD\} ac 1"}
C {devices/vsource.sym} 0 240 0 0 {name=VSS value="dc 0"}
C {devices/isource.sym} 240 0 0 0 {name=ILOAD value="dc 1m"}
C {devices/capa.sym} 0 0 0 0 {name=CLOAD value=1p}
C {ldo_ihp_capless.sym} 240 240 0 0 {name=XDUT value=ldo_ihp_capless}
N 0 -90 0 -30 {}
N 0 30 0 90 {}
N 0 150 0 210 {}
N 0 270 0 330 {}
N 240 -90 240 -30 {}
N 240 30 240 90 {}
N 240 100 240 160 {}
N 240 320 240 380 {}
N 375 -60 375 240 {}
N 480 -90 480 -30 {}
N 480 30 480 90 {}
N -60 -140 690 -140 {}
N 0 -60 375 -60 {}
N 345 240 375 240 {}
N -60 430 690 430 {}
C {devices/lab_wire.sym} -60 -140 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -60 430 0 0 {name=l1 lab=0}
C {devices/lab_wire.sym} 0 -90 0 1 {name=l2 lab=vout}
C {devices/lab_wire.sym} 240 380 2 0 {name=l3 lab=vss}
C {devices/lab_wire.sym} 480 -90 0 1 {name=l4 lab=vdd}
C {devices/lab_wire.sym} 480 90 2 0 {name=l5 lab=0}
C {devices/lab_wire.sym} 0 330 2 0 {name=l6 lab=0}
C {devices/lab_wire.sym} 240 90 2 0 {name=l7 lab=0}
C {devices/lab_wire.sym} 0 150 0 1 {name=l8 lab=vss}
C {devices/lab_wire.sym} 240 -90 0 1 {name=l9 lab=vout}
C {devices/lab_wire.sym} 0 90 2 0 {name=l10 lab=0}
C {devices/lab_wire.sym} 240 100 0 1 {name=l11 lab=vdd}
T {psrr_tb -- PSRR} -60 470 0 0 0.5 0.5 {}
T {drawn from decks/candidate/psrr.spice; directives and .control lifted verbatim} -60 510 0 0 0.3 0.3 {}
C {devices/code_shown.sym} -60 570 0 0 {name=DIRECTIVES only_toplevel=false value=".lib cornerMOSlv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.temp 27
.param VDD=1.5
.param vref_val=0.6
.param r_w=0.5u
.param r_fb_l=340u
.param c_ff_w=8u
.param r_bias_l=138.5u
.param x_dut_xmb0_w=1u
.param x_dut_xmb0_l=1u
.param x_dut_xmb1_w=1.39u
.param x_dut_xmbp_w=10u
.param x_dut_xmbp_l=1u
.param x_dut_xmt_w=10u
.param x_dut_xm1_w=9.53u
.param x_dut_xm1_l=0.5u
.param x_dut_xm3_w=2.95u
.param x_dut_xm3_l=1u
.param x_dut_xm5_w=2.42u
.param x_dut_xm5_l=0.5u
.param x_dut_xm6_w=5.53u
.param c_comp_w=54u
.param x_dut_xmc_w=15.76u
.param x_dut_xmc_l=0.36u
.param x_dut_xma_w=5.79u
.param x_dut_xma_l=0.5u
.param x_dut_xmcp_w=9.02u
.param x_dut_xmcp_l=0.5u
.param x_dut_xms_w=2.2u
.param x_dut_xms_l=0.95u
.param x_dut_xmp_w=10u
.param x_dut_xmp_l=0.13u
.param x_dut_xmp_m=19
.param x_dut_xmp_nf_mult=4
.param c_out_w=58u
.param c_out_m=4"}
C {devices/code_shown.sym} 316 570 0 0 {name=CONTROL only_toplevel=false value=".control
  set filetype=ascii
  ac dec 20 10 100meg
  meas ac vout_db FIND vdb(vout) AT=1k
  let psrr_vdd_db = 0 - vout_db
  print psrr_vdd_db
  write
  quit
.endc"}
