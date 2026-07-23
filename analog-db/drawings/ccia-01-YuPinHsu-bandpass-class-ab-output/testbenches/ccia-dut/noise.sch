v {xschem version=3.4.5 file_version=1.2
}
G {}
K {}
V {}
S {}
E {}
T {ia/noise -- ccia-dut standalone bench (ia_001_hsu_bandpass_classab)} 52.5 -1402.5 0 0 0.4 0.4 {}
B 2 1820 -925 2780 -765 {flags=graph
y1=0
y2=500
ypos1=0
ypos2=2
divy=5
subdivy=1
unity=1
x1=0
x2=7
divx=5
subdivx=1
xlabmag=1.0
ylabmag=1.0
dataset=-1
unitx=1
logx=1
logy=0
color="4"
node="vn_in_nv"
rainbow=0}
C {ccia-01-YuPinHsu-bandpass-class-ab-output/ccia-dut.sym} 1015 -725 0 0 {name=XDUT}
C {devices/lab_wire.sym} 995 -935 0 0 {name=l1 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 995 -815 0 0 {name=l2 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 1435 -935 0 0 {name=l3 sig_type=std_logic lab=voutn}
C {devices/lab_wire.sym} 1435 -815 0 0 {name=l4 sig_type=std_logic lab=voutp}
C {devices/lab_wire.sym} 1345 -1005 0 0 {name=l5 sig_type=std_logic lab=vss}
C {devices/lab_wire.sym} 1315 -1005 0 0 {name=l6 sig_type=std_logic lab=vdd}
C {devices/vsource.sym} 965 -1290 0 0 {name=Vdd value="dc \{VDD\}" savecurrent=true}
C {devices/lab_wire.sym} 965 -1320 0 0 {name=l7 sig_type=std_logic lab=vdd}
C {devices/gnd.sym} 965 -1260 0 0 {name=g8 lab=0}
C {devices/vsource.sym} 1065 -1290 0 0 {name=Vss value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 1065 -1320 0 0 {name=l9 sig_type=std_logic lab=vss}
C {devices/gnd.sym} 1065 -1260 0 0 {name=g10 lab=0}
C {devices/vsource.sym} 535 -825 0 0 {name=Vcm value="dc \{VCM\}" savecurrent=true}
C {devices/lab_wire.sym} 535 -855 0 0 {name=l11 sig_type=std_logic lab=vcm}
C {devices/gnd.sym} 535 -795 0 0 {name=g12 lab=0}
C {devices/vsource.sym} 805 -825 0 0 {name=Vinp value="dc 0 ac 1" savecurrent=true}
C {devices/lab_wire.sym} 805 -855 0 0 {name=l13 sig_type=std_logic lab=vinp}
C {devices/lab_wire.sym} 805 -795 0 0 {name=l14 sig_type=std_logic lab=vcm}
C {devices/vsource.sym} 665 -905 0 0 {name=Vinn value="dc 0" savecurrent=true}
C {devices/lab_wire.sym} 665 -935 0 0 {name=l15 sig_type=std_logic lab=vinn}
C {devices/lab_wire.sym} 665 -875 0 0 {name=l16 sig_type=std_logic lab=vcm}
C {devices/capa.sym} 1580 -860 0 0 {name=CLoadp m=1 value=\{CL\}}
C {devices/lab_wire.sym} 1580 -890 0 0 {name=l17 sig_type=std_logic lab=voutp}
C {devices/gnd.sym} 1580 -830 0 0 {name=g18 lab=0}
C {devices/capa.sym} 1680 -890 0 0 {name=CLoadn m=1 value=\{CL\}}
C {devices/lab_wire.sym} 1680 -920 0 0 {name=l19 sig_type=std_logic lab=voutn}
C {devices/gnd.sym} 1680 -860 0 0 {name=g20 lab=0}
C {devices/code.sym} 50 -1315 0 0 {name=PARAMS_BENCH
only_toplevel=true
value="
* TESTBENCH noise -- DUT ccia-dut (ia_001_hsu_bandpass_classab)
* template amplifier/noise_diff ; produces: inoise_total, onoise_total (vn_in density over the band)
* self-contained cap-coupled bandpass CCIA (Cin/Cf ratio gain + pseudo-R DC servo + internal biases). CONTINUOUS -> AC valid. Min-size as drawn.
* bench conditions:
.param CL=50f
.param VCM=0.6
.param VDD=1.2
* DUT global params (drawing cap/res + ideal-CMFB macromodel knobs):
.param Cc=1p Rz=10k Cin=16p Cf=0.8p gm_val=100u rout_val=10Meg rin_val=1T cin_val=10f cout_val=100f Rm=1Meg
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
  noise v(voutp,voutn) Vinp dec 21 1 10MEG
  print inoise_total onoise_total
  setplot noise1
  let vn_in = sqrt(inoise_spectrum)
  let vn_in_nv = vn_in*1e9
  write noise.raw vn_in vn_in_nv inoise_spectrum onoise_spectrum
  hardcopy noise_vnin.svg vn_in_nv
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
