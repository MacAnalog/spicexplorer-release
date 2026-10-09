v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {dropout_tb} -40 -200 0 0 0.4 0.4 {}
C {devices/vsource.sym} 240 0 0 0 {name=VDD value="dc 0.9"}
C {devices/vsource.sym} 0 240 0 0 {name=VSS value="dc 0"}
C {devices/isource.sym} 0 0 0 0 {name=ILOAD value="dc 10m"}
C {ldo_ihp_capless.sym} 240 240 0 0 {name=XDUT value=ldo_ihp_capless}
N 0 -90 0 -30 {}
N 0 30 0 90 {}
N 0 150 0 210 {}
N 0 270 0 330 {}
N 240 -90 240 -30 {}
N 240 30 240 90 {}
N 240 100 240 160 {}
N 240 320 240 380 {}
N 345 240 345 300 {}
N -60 -110 465 -110 {}
N 345 240 375 240 {}
N -60 430 465 430 {}
C {devices/lab_wire.sym} -60 -110 0 0 {name=l0 lab=vdd}
C {devices/lab_wire.sym} -60 430 0 0 {name=l1 lab=0}
C {devices/lab_wire.sym} 345 300 2 0 {name=l2 lab=vout}
C {devices/lab_wire.sym} 240 380 2 0 {name=l3 lab=vss}
C {devices/lab_wire.sym} 240 -90 0 1 {name=l4 lab=vdd}
C {devices/lab_wire.sym} 240 90 2 0 {name=l5 lab=0}
C {devices/lab_wire.sym} 0 330 2 0 {name=l6 lab=0}
C {devices/lab_wire.sym} 0 90 2 0 {name=l7 lab=0}
C {devices/lab_wire.sym} 0 150 0 1 {name=l8 lab=vss}
C {devices/lab_wire.sym} 0 -90 0 1 {name=l9 lab=vout}
C {devices/lab_wire.sym} 240 100 0 1 {name=l10 lab=vdd}
T {dropout_tb -- dropout} -60 470 0 0 0.5 0.5 {}
T {drawn from decks/candidate/dropout.spice; directives and .control lifted verbatim} -60 510 0 0 0.3 0.3 {}
C {devices/code_shown.sym} -60 570 0 0 {name=DIRECTIVES only_toplevel=false value=".lib cornerMOSlv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.temp 27
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
  dc Vdd 0.9 1.6 0.002
  let vo    = v(vout)
  let vsw   = v(vdd)
  let dvo   = deriv(vo)
  let dvi   = deriv(vsw)
  let slope = dvo / dvi
  let inreg = (abs(vo - 1.2) <= 0.05) & (abs(slope) <= 0.1)
  let npts  = length(inreg)
  let k     = 0
  let found = 0
  let vin_at = 0
  let vout_at = 0
  while k < npts
    if found < 0.5
      if inreg[k] > 0.5
        let vin_at  = vsw[k]
        let vout_at = vo[k]
        let found   = 1
      end
    end
    let k = k + 1
  end
  if found < 0.5
    let v_dropout = 0*log(0)
  else
    let v_dropout = vin_at - vout_at
  end
  print vin_at vout_at v_dropout
  write
  quit
.endc"}
