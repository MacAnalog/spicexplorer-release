v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 1075 -650 1075 -630 {lab=VDD}
N 960 -350 960 -330 {lab=VDD}
N 1150 -550 1190 -550 {lab=v_out}
N 1190 -550 1190 -530 {lab=v_out}
N 1190 -470 1190 -450 {lab=GND}
N 1060 -350 1060 -330 {lab=v_in}
N 1060 -270 1060 -250 {lab=GND}
N 960 -270 960 -250 {lab=GND}
N 1075 -470 1075 -450 {lab=GND}
N 920 -580 945 -580 {lab=v_in}
N 945 -580 945 -560 {lab=v_in}
N 945 -560 970 -535 {lab=v_in}
N 940 -520 970 -560 {lab=v_out}
N 940 -520 940 -420 {lab=v_out}
N 940 -420 1160 -420 {lab=v_out}
N 1160 -550 1160 -420 {lab=v_out}
C {devices/title.sym} 180 -50 0 0 {name=l1 author="Danial Noori Zadeh"}
C {devices/vsource.sym} 960 -300 0 0 {name=VDD value=6 savecurrent=false}
C {devices/vsource.sym} 1060 -300 0 0 {name=Vin value="dc 0 pwl(0 0 1u 0 1.1u 6)" savecurrent=false}
C {devices/vdd.sym} 960 -350 0 0 {name=l2 lab=VDD}
C {devices/vdd.sym} 1075 -650 0 0 {name=l3 lab=VDD}
C {devices/gnd.sym} 960 -250 0 0 {name=l4 lab=GND}
C {devices/gnd.sym} 1060 -250 0 0 {name=l5 lab=GND}
C {devices/gnd.sym} 1075 -450 0 0 {name=l7 lab=GND}
C {devices/capa.sym} 1190 -500 0 0 {name=CL
m=1
value=50p
footprint=1206
device="ceramic capacitor"}
C {devices/gnd.sym} 1190 -450 0 0 {name=l8 lab=GND}
C {devices/lab_pin.sym} 1190 -550 0 1 {name=p1 sig_type=std_logic lab=v_out}
C {devices/lab_pin.sym} 920 -580 0 0 {name=p3 sig_type=std_logic lab=v_in}
C {devices/code_shown.sym} 60 -930 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
*----------------------
* PDK Models
*----------------------

.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical

.lib $::180MCU_MODELS/sm141064.ngspice res_typical
* .lib $::180MCU_MODELS/sm141064.ngspice res_statistical
"}
C {devices/code_shown.sym} 90 -630 0 0 {name=NGSPICE only_toplevel=true 
value="
.temp 27

.ic v(v_out)=0
.option method=gear

.control
tran 0.005u 15u uic
plot v_in v_out

let vout_limit=11*0.99
meas tran tcross WHEN v(v_out)=vout_limit
let vin_limit=0.5*1.5
meas tran tstart WHEN v(v_in)=vin_limit
let tsettle=tcross-tstart
print tsettle

.endc"}
C {devices/launcher.sym} 970 -120 0 0 {name=h1
descr="Annotate OP"
tclcommand="set show_hidden_texts 1; xschem annotate_op"}
C {ldo-005-ti-ldo-buffer-ref/gf180/error_amp/error_amp.sym} 970 -610 0 0 {name=x1}
C {devices/launcher.sym} 670 -120 0 0 {name=h2
descr="simulate" 
tclcommand="xschem save; xschem netlist; xschem simulate"}
C {devices/lab_pin.sym} 1060 -350 0 0 {name=p2 sig_type=std_logic lab=v_in}
