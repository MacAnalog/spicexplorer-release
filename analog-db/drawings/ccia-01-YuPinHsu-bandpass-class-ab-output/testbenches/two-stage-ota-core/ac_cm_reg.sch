v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {amplifier/ac_cm_reg -- two-stage-ota-core standalone bench (amp_025_hsu_classab_ota)} 52.5 -1402.5 0 0 0.4 0.4 {}
B 2 1820 -925 2780 -765 {flags=graph
y1=0
y2=120
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=2
x2=9
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
dataset=-1
unitx=1
logx=1
logy=0
color="4"
node="zcmdb"
rainbow=0}
C {ccia-01-YuPinHsu-bandpass-class-ab-output/two-stage-ota-core.sym} 1015 -725 0 0 {name=XDUT}
C {devices/lab_wire.sym} 995 -785 0 0 {name=l1 sig_type=std_logic lab=vb1}
C {devices/lab_wire.sym} 995 -855 0 0 {name=l2 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 995 -765 0 0 {name=l3 sig_type=std_logic lab=vb2}
C {devices/lab_wire.sym} 995 -835 0 0 {name=l4 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 995 -745 0 0 {name=l5 sig_type=std_logic lab=vb3}
C {devices/lab_wire.sym} 1295 -775 0 0 {name=l6 sig_type=std_logic lab=voutn}
C {devices/lab_wire.sym} 1295 -755 0 0 {name=l7 sig_type=std_logic lab=voutp}
C {devices/lab_wire.sym} 1265 -885 0 0 {name=l8 sig_type=std_logic lab=vss}
C {devices/lab_wire.sym} 1235 -885 0 0 {name=l9 sig_type=std_logic lab=vdd}
C {devices/lab_wire.sym} 1295 -735 0 0 {name=l10 sig_type=std_logic lab=vcmfb}
C {devices/vsource.sym} 965 -1290 0 0 {name=Vdd value="dc \{VDD\}" savecurrent=true}
C {devices/lab_wire.sym} 965 -1320 0 0 {name=l11 sig_type=std_logic lab=vdd}
C {devices/gnd.sym} 965 -1260 0 0 {name=g12 lab=0}
C {devices/vsource.sym} 1065 -1290 0 0 {name=Vss value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 1065 -1320 0 0 {name=l13 sig_type=std_logic lab=vss}
C {devices/gnd.sym} 1065 -1260 0 0 {name=g14 lab=0}
C {devices/vsource.sym} 150 -540 0 0 {name=Vb1 value="dc \{vb1\}" savecurrent=true}
C {devices/lab_wire.sym} 150 -570 0 0 {name=l15 sig_type=std_logic lab=vb1}
C {devices/gnd.sym} 150 -510 0 0 {name=g16 lab=0}
C {devices/vsource.sym} 150 -660 0 0 {name=Vb2 value="dc \{vb2\}" savecurrent=true}
C {devices/lab_wire.sym} 150 -690 0 0 {name=l17 sig_type=std_logic lab=vb2}
C {devices/gnd.sym} 150 -630 0 0 {name=g18 lab=0}
C {devices/vsource.sym} 150 -780 0 0 {name=Vb3 value="dc \{vb3\}" savecurrent=true}
C {devices/lab_wire.sym} 150 -810 0 0 {name=l19 sig_type=std_logic lab=vb3}
C {devices/gnd.sym} 150 -750 0 0 {name=g20 lab=0}
C {devices/vsource.sym} 150 -900 0 0 {name=Vcmfb value="dc \{vcmfb\}" savecurrent=true}
C {devices/lab_wire.sym} 150 -930 0 0 {name=l21 sig_type=std_logic lab=vcmfb}
C {devices/gnd.sym} 150 -870 0 0 {name=g22 lab=0}
C {devices/vsource.sym} 535 -825 0 0 {name=Vcm value="dc \{VCM\}" savecurrent=true}
C {devices/lab_wire.sym} 535 -855 0 0 {name=l23 sig_type=std_logic lab=vcm}
C {devices/gnd.sym} 535 -795 0 0 {name=g24 lab=0}
C {devices/vsource.sym} 805 -825 0 0 {name=Vinp value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 805 -855 0 0 {name=l25 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 805 -795 0 0 {name=l26 sig_type=std_logic lab=vcm}
C {devices/vsource.sym} 665 -905 0 0 {name=Vinn value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 665 -935 0 0 {name=l27 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 665 -875 0 0 {name=l28 sig_type=std_logic lab=vcm}
C {devices/capa.sym} 1580 -860 0 0 {name=CLoadp m=1 value=\{CL\}}
C {devices/lab_wire.sym} 1580 -890 0 0 {name=l29 sig_type=std_logic lab=voutp}
C {devices/gnd.sym} 1580 -830 0 0 {name=g30 lab=0}
C {devices/capa.sym} 1680 -890 0 0 {name=CLoadn m=1 value=\{CL\}}
C {devices/lab_wire.sym} 1680 -920 0 0 {name=l31 sig_type=std_logic lab=voutn}
C {devices/gnd.sym} 1680 -860 0 0 {name=g32 lab=0}
C {devices/isource.sym} 1500 -660 0 0 {name=Icmp value="dc 0 ac 0.5"}
C {devices/lab_wire.sym} 1500 -690 0 0 {name=l33 sig_type=std_logic lab=voutp}
C {devices/gnd.sym} 1500 -630 0 0 {name=g34 lab=0}
C {devices/isource.sym} 1620 -660 0 0 {name=Icmn value="dc 0 ac 0.5"}
C {devices/lab_wire.sym} 1620 -690 0 0 {name=l35 sig_type=std_logic lab=voutn}
C {devices/gnd.sym} 1620 -630 0 0 {name=g36 lab=0}
C {devices/code.sym} 50 -1315 0 0 {name=PARAMS_BENCH
only_toplevel=true
value="
* TESTBENCH ac_cm_reg -- DUT two-stage-ota-core (amp_025_hsu_classab_ota)
* template amplifier/ac_cm_reg ; produces: zcm_lf_ohm, zcm_peak_ohm, cm_peaking_db
* class-AB two-stage OTA (min-size as drawn). External ports Vb1/Vb2/Vb3 + vcmfb_ref (output-CM reference into the CMFB servo).
* bench conditions:
.param VDD=1.2
.param VCM=0.6
.param CL=50f
* DUT global params (drawing cap/res + ideal-CMFB macromodel knobs):
.param Cc=1p Rz=10k Cin=16p Cf=0.8p gm_val=100u rout_val=10Meg rin_val=1T cin_val=10f cout_val=100f Rm=1Meg
* external bias ports (amp_025 sizing.yaml defaults):
.param vb1=0.55
.param vb2=0.45
.param vb3=0.75
.param vcmfb=0.6
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
  set hcopydevtype=svg
  set filetype=ascii
  ac dec 41 100 1G
  let zcm = mag((v(voutp)+v(voutn))/2)
  let zcmdb = db(zcm)
  meas ac zcm_lf_ohm FIND zcm AT=100
  meas ac zcm_pk MAX zcm
  let zcm_peak_ohm = zcm_pk
  let cm_peaking_db = 20*log10(zcm_pk/zcm_lf_ohm)
  print zcm_lf_ohm zcm_peak_ohm cm_peaking_db
  write ac_cm_reg.raw
  hardcopy ac_cm_reg_zcm.svg zcmdb
.endc
"}
C {devices/launcher.sym} 1895 -240 0 0 {name=h_run
descr="Simulate + load waves"
tclcommand="xschem netlist; simulate [list xschem raw_read $netlist_dir/[file tail [file rootname [xschem get current_name]]].raw ac]"
}
C {devices/launcher.sym} 1895 -300 0 0 {name=h_load
descr="Load waves"
tclcommand="xschem raw_read $netlist_dir/[file tail [file rootname [xschem get current_name]]].raw ac"
}
C {devices/title.sym} 190 -80 0 0 {name=l6 author="Copyright 2026 MacAnalog Research Group"}
