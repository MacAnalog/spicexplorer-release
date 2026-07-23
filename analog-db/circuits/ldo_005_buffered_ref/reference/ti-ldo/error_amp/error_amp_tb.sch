v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 1365 -800 1365 -780 {lab=VDD}
N 1250 -500 1250 -480 {lab=VDD}
N 1440 -700 1480 -700 {lab=vout}
N 1480 -700 1480 -680 {lab=vout}
N 1480 -620 1480 -600 {lab=GND}
N 1350 -500 1350 -480 {lab=vin_p}
N 1350 -420 1350 -400 {lab=GND}
N 1430 -420 1430 -400 {lab=GND}
N 1250 -420 1250 -400 {lab=GND}
N 1430 -500 1430 -480 {lab=vin_n}
N 1365 -620 1365 -600 {lab=GND}
N 1210 -730 1235 -730 {lab=vin_p}
N 1235 -730 1235 -710 {lab=vin_p}
N 1235 -710 1260 -710 {lab=vin_p}
N 1210 -660 1240 -660 {lab=vin_n}
N 1240 -685 1240 -660 {lab=vin_n}
N 1240 -685 1260 -685 {lab=vin_n}
C {devices/title.sym} 180 -50 0 0 {name=l1 author="Danial Noori Zadeh"}
C {devices/vsource.sym} 1250 -450 0 0 {name=VDD value=6 savecurrent=false}
C {devices/vsource.sym} 1350 -450 0 0 {name=VIN_P value=3 savecurrent=false}
C {devices/vsource.sym} 1430 -450 0 0 {name=VIN_N value=3 savecurrent=false}
C {devices/vdd.sym} 1250 -500 0 0 {name=l2 lab=VDD}
C {devices/vdd.sym} 1365 -800 0 0 {name=l3 lab=VDD}
C {devices/gnd.sym} 1250 -400 0 0 {name=l4 lab=GND}
C {devices/gnd.sym} 1350 -400 0 0 {name=l5 lab=GND}
C {devices/gnd.sym} 1430 -400 0 0 {name=l6 lab=GND}
C {devices/gnd.sym} 1365 -600 0 0 {name=l7 lab=GND}
C {devices/capa.sym} 1480 -650 0 0 {name=CL
m=1
value=50p
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 1480 -600 0 0 {name=l8 lab=GND}
C {devices/lab_pin.sym} 1350 -500 0 0 {name=p5 sig_type=std_logic lab=vin_p}
C {devices/lab_pin.sym} 1480 -700 0 1 {name=p1 sig_type=std_logic lab=vout}
C {devices/lab_pin.sym} 1430 -500 0 1 {name=p2 sig_type=std_logic lab=vin_n}
C {devices/lab_pin.sym} 1210 -730 0 0 {name=p3 sig_type=std_logic lab=vin_p}
C {devices/lab_pin.sym} 1210 -660 2 1 {name=p4 sig_type=std_logic lab=vin_n}
C {devices/code_shown.sym} 1130 -970 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical

.lib $::180MCU_MODELS/sm141064.ngspice res_typical
* .lib $::180MCU_MODELS/sm141064.ngspice res_statistical
"}
C {devices/code_shown.sym} 20 -990 0 0 {name=NGSPICE only_toplevel=true
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
alter @VIN_P[DC] = 3.0
alter @VIN_P[PULSE] = [ 0 6 0 $&tfr $&tfr $&ton $&tper 0 ]
** $& is to convert the variables defined by "let" to string variables defined by "set" command

** Simulation 
op
dc vin_p 0 3.3 0.01
tran $&tstep $&tstop

** Plots 
setplot dc1
let vout = v(vout)
plot vout

setplot tran1
let vout = v(vout)
let vin_p = v(vin_p)
let ivdd = -1 * vdd#branch * 1e4
plot vout vin_p ivdd

** Reset plot so the save command uses the operating points
setplot op1
write error_amp_tb.raw
.endc
"}
C {devices/launcher.sym} 1260 -270 0 0 {name=h1
descr="Annotate OP"
tclcommand="set show_hidden_texts 1; xschem annotate_op"}
C {error_amp/error_amp.sym} 1260 -760 0 0 {name=x1}
C {devices/code_shown.sym} 1730 -960 0 0 {name=NGSPICE-AC-Response only_toplevel=true
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
alter @VIN_P[DC] = 3.0
alter @VIN_P[PULSE] = [ 0 6 0 $&tfr $&tfr $&ton $&tper 0 ]
** $& is to convert the variables defined by "let" to string variables defined by "set" command

** Simulation 
op
dc vin_p 0 3.3 0.01
tran $&tstep $&tstop

** Plots 
setplot dc1
let vout = v(vout)
plot vout

setplot tran1
let vout = v(vout)
let vin_p = v(vin_p)
let ivdd = -1 * vdd#branch * 1e4
plot vout vin_p ivdd

** Reset plot so the save command uses the operating points
setplot op1
write error_amp_tb.raw
.endc
"}
