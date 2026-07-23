v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {ia/dc_op -- PGA-ideal standalone bench (ia_005_hsu_pga_ideal)} 52.5 -1402.5 0 0 0.4 0.4 {}
C {bio-afe-01-YuPinHsu-reconfigable-SRMC/PGA-ideal.sym} 1015 -725 0 0 {name=XDUT}
C {devices/lab_wire.sym} 995 -985 0 0 {name=l1 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 995 -855 0 0 {name=l2 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 1395 -985 0 0 {name=l3 sig_type=std_logic lab=voutp}
C {devices/lab_wire.sym} 1395 -855 0 0 {name=l4 sig_type=std_logic lab=voutn}
C {devices/lab_wire.sym} 1395 -765 0 0 {name=l5 sig_type=std_logic lab=vdd}
C {devices/lab_wire.sym} 1395 -745 0 0 {name=l6 sig_type=std_logic lab=vss}
C {devices/lab_wire.sym} 995 -817.5 0 0 {name=l7 sig_type=std_logic lab=vcm}
C {devices/lab_wire.sym} 1055 -705 0 0 {name=l8 sig_type=std_logic lab=v_d0}
C {devices/lab_wire.sym} 1035 -705 0 0 {name=l9 sig_type=std_logic lab=v_d0_not}
C {devices/lab_wire.sym} 1095 -705 0 0 {name=l10 sig_type=std_logic lab=v_d1}
C {devices/lab_wire.sym} 1075 -705 0 0 {name=l11 sig_type=std_logic lab=v_d1_not}
C {devices/lab_wire.sym} 1135 -705 0 0 {name=l12 sig_type=std_logic lab=v_d2}
C {devices/lab_wire.sym} 1115 -705 0 0 {name=l13 sig_type=std_logic lab=v_d2_not}
C {devices/vsource.sym} 965 -1290 0 0 {name=Vdd value="dc \{VDD\}" savecurrent=true}
C {devices/lab_wire.sym} 965 -1320 0 0 {name=l14 sig_type=std_logic lab=vdd}
C {devices/gnd.sym} 965 -1260 0 0 {name=g15 lab=0}
C {devices/vsource.sym} 1065 -1290 0 0 {name=Vss value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 1065 -1320 0 0 {name=l16 sig_type=std_logic lab=vss}
C {devices/gnd.sym} 1065 -1260 0 0 {name=g17 lab=0}
C {devices/vsource.sym} 350 -540 0 0 {name=Vfx0 value="dc \{VDD\}" savecurrent=true}
C {devices/lab_wire.sym} 350 -570 0 0 {name=l18 sig_type=std_logic lab=v_d0}
C {devices/gnd.sym} 350 -510 0 0 {name=g19 lab=0}
C {devices/vsource.sym} 350 -580 0 0 {name=Vfx1 value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 350 -610 0 0 {name=l20 sig_type=std_logic lab=v_d0_not}
C {devices/gnd.sym} 350 -550 0 0 {name=g21 lab=0}
C {devices/vsource.sym} 350 -620 0 0 {name=Vfx2 value="dc \{VDD\}" savecurrent=true}
C {devices/lab_wire.sym} 350 -650 0 0 {name=l22 sig_type=std_logic lab=v_d1}
C {devices/gnd.sym} 350 -590 0 0 {name=g23 lab=0}
C {devices/vsource.sym} 350 -660 0 0 {name=Vfx3 value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 350 -690 0 0 {name=l24 sig_type=std_logic lab=v_d1_not}
C {devices/gnd.sym} 350 -630 0 0 {name=g25 lab=0}
C {devices/vsource.sym} 350 -700 0 0 {name=Vfx4 value="dc \{VDD\}" savecurrent=true}
C {devices/lab_wire.sym} 350 -730 0 0 {name=l26 sig_type=std_logic lab=v_d2}
C {devices/gnd.sym} 350 -670 0 0 {name=g27 lab=0}
C {devices/vsource.sym} 350 -740 0 0 {name=Vfx5 value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 350 -770 0 0 {name=l28 sig_type=std_logic lab=v_d2_not}
C {devices/gnd.sym} 350 -710 0 0 {name=g29 lab=0}
C {devices/vsource.sym} 535 -825 0 0 {name=Vcm value="dc \{VCM\}" savecurrent=true}
C {devices/lab_wire.sym} 535 -855 0 0 {name=l30 sig_type=std_logic lab=vcm}
C {devices/gnd.sym} 535 -795 0 0 {name=g31 lab=0}
C {devices/vsource.sym} 805 -825 0 0 {name=Vinp value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 805 -855 0 0 {name=l32 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 805 -795 0 0 {name=l33 sig_type=std_logic lab=vcm}
C {devices/vsource.sym} 665 -905 0 0 {name=Vinn value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 665 -935 0 0 {name=l34 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 665 -875 0 0 {name=l35 sig_type=std_logic lab=vcm}
C {devices/capa.sym} 1580 -860 0 0 {name=CLoadp m=1 value=\{CL\}}
C {devices/lab_wire.sym} 1580 -890 0 0 {name=l36 sig_type=std_logic lab=voutp}
C {devices/gnd.sym} 1580 -830 0 0 {name=g37 lab=0}
C {devices/capa.sym} 1680 -890 0 0 {name=CLoadn m=1 value=\{CL\}}
C {devices/lab_wire.sym} 1680 -920 0 0 {name=l38 sig_type=std_logic lab=voutn}
C {devices/gnd.sym} 1680 -860 0 0 {name=g39 lab=0}
C {devices/code.sym} 50 -1315 0 0 {name=PARAMS_BENCH
only_toplevel=true
value="
* TESTBENCH dc_op -- DUT PGA-ideal (ia_005_hsu_pga_ideal)
* template amplifier/dc_op_diff ; produces: i_supply, vos, vocm
* 3-bit binary-capbank PGA (ia_005), gain code = 111 (max). CONTINUOUS -> AC valid. Min-size as drawn; ia_005 declares no analyses so this bench set is chosen.
* bench conditions:
.param VDD=1.2
.param VCM=0.6
.param CL=50f
* DUT global params (drawing cap/res + ideal-CMFB macromodel knobs):
.param Cc=1p Rz=10k Cin=16p Cf=0.8p Cu=1p gm_val=100u rout_val=10Meg rin_val=1T cin_val=10f cout_val=100f Rm=1Meg tg_n_w=0.18u tg_p_w=0.18u tg_n_l=0.13u tg_p_l=0.13u
"}
C {devices/code.sym} 565 -1140 0 0 {name=MODELS
only_toplevel=true
value="
.lib cornerMOSlv.lib mos_tt
.lib cornerRES.lib res_typ
.lib cornerCAP.lib cap_typ
.temp 27
"}
C {devices/code.sym} 1812 -527 0 0 {name=COMMANDS
only_toplevel=true
value="
.control
  save all
  set filetype=ascii
  op
  let i_supply = abs(i(Vdd))
  let vos  = v(voutp) - v(voutn)
  let vocm = (v(voutp) + v(voutn))/2
  print i_supply vos vocm
  print v(voutp) v(voutn)
  write dc_op.raw
.endc
"}
C {devices/launcher.sym} 1895 -240 0 0 {name=h_run
descr="Simulate + load waves"
tclcommand="xschem netlist; simulate [list xschem raw_read $netlist_dir/[file tail [file rootname [xschem get current_name]]].raw op]"
}
C {devices/launcher.sym} 1895 -300 0 0 {name=h_load
descr="Load waves"
tclcommand="xschem raw_read $netlist_dir/[file tail [file rootname [xschem get current_name]]].raw op"
}
C {devices/title.sym} 190 -80 0 0 {name=l6 author="Copyright 2026 MacAnalog Research Group"}
