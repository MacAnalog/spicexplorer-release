v {xschem version=3.4.7 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 1360 -815 1360 -795 {lab=VDD}
N 1080 -335 1080 -315 {lab=VDD}
N 1500 -735 1540 -735 {lab=vout}
N 1540 -735 1540 -715 {lab=vout}
N 1540 -655 1540 -635 {lab=GND}
N 1180 -335 1180 -315 {lab=vin}
N 1180 -255 1180 -235 {lab=GND}
N 1260 -255 1260 -235 {lab=GND}
N 1080 -255 1080 -235 {lab=GND}
N 1260 -335 1260 -315 {lab=vref}
N 1360 -515 1360 -495 {lab=GND}
N 1170 -625 1220 -625 {lab=vref}
N 1165 -715 1220 -715 {lab=vin}
C {devices/title.sym} 180 -50 0 0 {name=l1 author="Danial Noori Zadeh"}
C {devices/vsource.sym} 1080 -285 0 0 {name=VDD value=6 savecurrent=false}
C {devices/vsource.sym} 1180 -285 0 0 {name=VIN value=3 savecurrent=false}
C {devices/vsource.sym} 1260 -285 0 0 {name=VREF value=3 savecurrent=false}
C {devices/vdd.sym} 1080 -335 0 0 {name=l2 lab=VDD}
C {devices/vdd.sym} 1360 -815 0 0 {name=l3 lab=VDD}
C {devices/gnd.sym} 1080 -235 0 0 {name=l4 lab=GND}
C {devices/gnd.sym} 1180 -235 0 0 {name=l5 lab=GND}
C {devices/gnd.sym} 1260 -235 0 0 {name=l6 lab=GND}
C {devices/gnd.sym} 1360 -495 0 0 {name=l7 lab=GND}
C {devices/capa.sym} 1540 -685 0 0 {name=Cout
m=1
value=\{Cout\}
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 1540 -635 0 0 {name=l8 lab=GND}
C {devices/lab_pin.sym} 1180 -335 0 0 {name=p5 sig_type=std_logic lab=vin}
C {devices/lab_pin.sym} 1540 -735 0 1 {name=p1 sig_type=std_logic lab=vout}
C {devices/lab_pin.sym} 1260 -335 0 1 {name=p2 sig_type=std_logic lab=vref}
C {devices/code_shown.sym} 1675 -1570 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical

.lib $::180MCU_MODELS/sm141064.ngspice res_typical
* .lib $::180MCU_MODELS/sm141064.ngspice res_statistical
"}
C {devices/code_shown.sym} 10 -1580 0 0 {name=NGSPICE only_toplevel=true
place=end
value="

.control
save all

** VARIABLE DEFINITION
**   let allows defining vars that can be used in mathematicall expressions
**   set is only string variables

** Input Signal
let fsig = 1k
let tper = 1/fsig
** rise fall/time
let tfr  = 0.01*tper
let ton  = 0.5*tper-2*tfr

** Transient Params
let tstop = 2*tper
let tstep = 0.001*tper

** Set Sources
alter @VIN[DC] = 3.0
alter @VIN[PULSE] = [ 0 6 0 $&tfr $&tfr $&ton $&tper 0 ]
** $& is to convert the variables defined by \"let\" to string variables defined by \"set\" command

** Simulation 
op
dc vin_p 0 3.3 0.01
tran $&tstep $&tstop

** Plots 
let vout = v(vout)
let vea_out = v(x_ldo.ea_out)
plot vout vea_out

setplot tran1
let vout = v(vout)
let vin = v(vin)
let vref = v(vref)
let ivdd = -1 * vdd#branch * 1e4
let vea_out = v(x_ldo.ea_out)
plot vout vin vref vea_out
write tran.raw


** Reset plot so the save command uses the operating points
setplot op1
write op.raw
.endc
"}
C {devices/launcher.sym} 1570 -235 0 0 {name=h1
descr="Annotate OP"
tclcommand="set show_hidden_texts 1; xschem annotate_op"}
C {ldo/ldo.sym} 1240 -775 0 0 {name=x_ldo}
C {devices/lab_pin.sym} 1170 -625 0 0 {name=p3 sig_type=std_logic lab=vref}
C {devices/lab_pin.sym} 1165 -715 0 0 {name=p4 sig_type=std_logic lab=vin}
C {devices/code_shown.sym} 1685 -1240 0 0 {name=params_tb only_toplevel=true
format="tcleval( @value )"
value="
** Load Parameters
.param Cout 	= 1n
.param Iout 	= 20m
.param ESR 	= 10e-3
.param ESL	= .1e-9

** Source Paramters
.param Cin  	= 1u
.param Vin	= 3.6
.param Vref	= 1.25

"}
C {devices/code_shown.sym} 1680 -965 0 0 {name=params_lfp only_toplevel=true
format="tcleval( @value )"
value="
** LPF Network Parameters
.param C_lpf_c1 	= 100p
.param R_lpf_r1_w	= 1e-6
.param R_lpf_r1_l	= 1e-6

"}
C {devices/code_shown.sym} 1670 -785 0 0 {name=params_ldo_top only_toplevel=true
format="tcleval( @value )"
value="
** LDO Top Level Parameters **

** Output node passive devices
.param C_ldo_top_c1 	= 100p
.param R_ldo_top_r3 	= 100p

** Voltage divider network
.param R_ldo_top_r1_w	= 1e-6
.param R_ldo_top_r1_l	= 1e-6
.param R_ldo_top_r2_w	= 1e-6
.param R_ldo_top_r2_l	= 1e-6

** CG Transistor
.param XMP_ldo_top_pfet_w  = 0.50u
.param XMP_ldo_top_pfet_l  = 0.70u
.param XMP_ldo_top_pfet_nf = 1
.param XMP_ldo_top_pfet_m  = 1


"}
C {devices/code_shown.sym} 2055 -1260 0 0 {name=params_ref_amp only_toplevel=true
format="tcleval( @value )"
value="
** Ref Amp Parameters **

.param I_ref_ref_amp = 1m


** Passive Devices
.param C_ref_amp_c1 	= 100p

.param R_ref_amp_r1_w	= 1e-6
.param R_ref_amp_r1_l	= 1e-6

** NMOS
** ref_amp.M1 Transistor
.param M1_ref_amp_nfet_w  = 0.50u
.param M1_ref_amp_nfet_l  = 0.30u
.param M1_ref_amp_nfet_nf = 1
.param M1_ref_amp_nfet_m  = 1

** ref_amp.M2 Transistor
.param M2_ref_amp_nfet_w  = 0.50u
.param M2_ref_amp_nfet_l  = 0.30u
.param M2_ref_amp_nfet_nf = 1
.param M2_ref_amp_nfet_m  = 1

** ref_amp.M_mirror_out Transistor
.param M_mirror_out_ref_amp_nfet_w  = 0.50u
.param M_mirror_out_ref_amp_nfet_l  = 0.30u
.param M_mirror_out_ref_amp_nfet_nf = 1
.param M_mirror_out_ref_amp_nfet_m  = 1

** ref_amp.M_mirror_a Transistor
.param M_mirror_a_ref_amp_nfet_w  = 0.50u
.param M_mirror_a_ref_amp_nfet_l  = 0.30u
.param M_mirror_a_ref_amp_nfet_nf = 1
.param M_mirror_a_ref_amp_nfet_m  = 1


** ref_amp.M_mirror_ref Transistor
.param M_mirror_ref_ref_amp_nfet_w  = 0.50u
.param M_mirror_ref_ref_amp_nfet_l  = 0.30u
.param M_mirror_ref_ref_amp_nfet_nf = 1
.param M_mirror_ref_ref_amp_nfet_m  = 1


** PMOS
** ref_amp.M3 Transistor
.param M3_ref_amp_pfet_w  = 0.50u
.param M3_ref_amp_pfet_l  = 0.30u
.param M3_ref_amp_pfet_nf = 1
.param M3_ref_amp_pfet_m  = 1


** ref_amp.M4 Transistor
.param M4_ref_amp_pfet_w  = 0.50u
.param M4_ref_amp_pfet_l  = 0.30u
.param M4_ref_amp_pfet_nf = 1
.param M4_ref_amp_pfet_m  = 1


** ref_amp.M5 Transistor
.param M5_ref_amp_pfet_w  = 0.50u
.param M5_ref_amp_pfet_l  = 0.30u
.param M5_ref_amp_pfet_nf = 1
.param M5_ref_amp_pfet_m  = 1

"}
C {devices/code_shown.sym} 2500 -1550 0 0 {name=params_ref_amp1 only_toplevel=true
format="tcleval( @value )"
value="
** Error Amp Parameters **

.param I_error_amp_ref = 1m


** Passive Devices
.param C_error_amp_cc 	= 100p

.param R_error_amp_rz_w	= 1e-6
.param R_error_amp_rz_l	= 1e-6

** NMOS
** error_amp.M1 Transistor
.param M1_error_amp_nfet_w  = 0.50u
.param M1_error_amp_nfet_l  = 0.30u
.param M1_error_amp_nfet_nf = 1
.param M1_error_amp_nfet_m  = 1

** error_amp.M2 Transistor
.param M2_error_amp_nfet_w  = 0.50u
.param M2_error_amp_nfet_l  = 0.30u
.param M2_error_amp_nfet_nf = 1
.param M2_error_amp_nfet_m  = 1

** error_amp.M_mirror_ea_out Transistor
.param M_mirror_ea_out_error_amp_nfet_w  = 0.50u
.param M_mirror_ea_out_error_amp_nfet_l  = 0.30u
.param M_mirror_ea_out_error_amp_nfet_nf = 1
.param M_mirror_ea_out_error_amp_nfet_m  = 1

** error_amp.M_mirror_e Transistor
.param M_mirror_e_error_amp_nfet_w  = 0.50u
.param M_mirror_e_error_amp_nfet_l  = 0.30u
.param M_mirror_e_error_amp_nfet_nf = 1
.param M_mirror_e_error_amp_nfet_m  = 1

** error_amp.M_mirror_c Transistor
.param M_mirror_c_error_amp_nfet_w  = 0.50u
.param M_mirror_c_error_amp_nfet_l  = 0.30u
.param M_mirror_c_error_amp_nfet_nf = 1
.param M_mirror_c_error_amp_nfet_m  = 1

** error_amp.M_mirror_f Transistor
.param M_mirror_f_error_amp_nfet_w  = 0.50u
.param M_mirror_f_error_amp_nfet_l  = 0.30u
.param M_mirror_f_error_amp_nfet_nf = 1
.param M_mirror_f_error_amp_nfet_m  = 1

** error_amp.M_mirror_error_amp_ref Transistor
.param M_mirror_error_amp_ref_error_amp_nfet_w  = 0.50u
.param M_mirror_error_amp_ref_error_amp_nfet_l  = 0.30u
.param M_mirror_error_amp_ref_error_amp_nfet_nf = 1
.param M_mirror_error_amp_ref_error_amp_nfet_m  = 1

** PMOS
** error_amp.M3 Transistor
.param M3_error_amp_pfet_w  = 0.50u
.param M3_error_amp_pfet_l  = 0.30u
.param M3_error_amp_pfet_nf = 1
.param M3_error_amp_pfet_m  = 1

** error_amp.M4 Transistor
.param M4_error_amp_pfet_w  = 0.50u
.param M4_error_amp_pfet_l  = 0.30u
.param M4_error_amp_pfet_nf = 1
.param M4_error_amp_pfet_m  = 1

** error_amp.M5 Transistor
.param M5_error_amp_pfet_w  = 0.50u
.param M5_error_amp_pfet_l  = 0.30u
.param M5_error_amp_pfet_nf = 1
.param M5_error_amp_pfet_m  = 1

** error_amp.M6 Transistor
.param M6_error_amp_pfet_w  = 0.50u
.param M6_error_amp_pfet_l  = 0.30u
.param M6_error_amp_pfet_nf = 1
.param M6_error_amp_pfet_m  = 1

** error_amp.M7 Transistor
.param M7_error_amp_pfet_w  = 0.50u
.param M7_error_amp_pfet_l  = 0.30u
.param M7_error_amp_pfet_nf = 1
.param M7_error_amp_pfet_m  = 1

"}
