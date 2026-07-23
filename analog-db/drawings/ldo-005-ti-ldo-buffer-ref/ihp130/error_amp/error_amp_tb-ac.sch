v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 1300 -630 1300 -590 {
lab=v_out}
N 1220 -630 1300 -630 {
lab=v_out}
N 1220 -630 1220 -510 {
lab=v_out}
N 1150 -630 1220 -630 {
lab=v_out}
N 900 -510 1220 -510 {
lab=v_out}
N 900 -620 900 -510 {lab=v_out}
N 900 -620 970 -640 {lab=v_out}
N 600 -420 600 -400 {lab=VDD}
N 700 -420 700 -400 {lab=v_in}
N 700 -340 700 -320 {lab=GND}
N 600 -340 600 -320 {lab=GND}
N 1300 -530 1300 -510 {lab=GND}
N 1075 -550 1075 -530 {lab=GND}
N 880 -640 970 -615 {lab=v_in}
N 1075 -730 1075 -710 {lab=VDD}
C {devices/code_shown.sym} 0 -100 0 0 {name=MODEL only_toplevel=true
format="tcleval( @value )"
value=".include $::SG13G2_MODELS/design.ngspice
.lib $::SG13G2_MODELS/cornerMOShv.lib mos_tt
.lib $::SG13G2_MODELS/cornerRES.lib res_typ
"}
C {devices/code_shown.sym} 0 -750 0 0 {name=NGSPICE only_toplevel=true 
value="
.temp 27
.control
option sparse
save all
op
write ota-5t_tb-ac.raw
set appendwrite

ac dec 101 1k 100MEG
write ota-5t_tb-ac.raw
plot 20*log10(v_out)

meas ac dcgain MAX vmag(v_out) FROM=10 TO=10k
let f3db = dcgain/sqrt(2)
meas ac fbw WHEN vmag(v_out)=f3db FALL=1
let gainerror=(dcgain-1)/1
print dcgain
print fbw
print gainerror

noise v(v_out) Vin dec 101 1k 100MEG
print onoise_total

.endc
"}
C {devices/title.sym} 160 -30 0 0 {name=l5 author="(c) 2024-2025 H. Pretl, Apache-2.0 license"}
C {devices/launcher.sym} 680 -160 0 0 {name=h2
descr="simulate" 
tclcommand="xschem save; xschem netlist; xschem simulate"
}
C {devices/launcher.sym} 920 -160 0 0 {name=h3
descr="annotate OP" 
tclcommand="set show_hidden_texts 1; xschem annotate_op"
}
C {devices/capa.sym} 1300 -560 0 0 {name=CL
value=50f}
C {devices/lab_wire.sym} 1300 -630 0 0 {name=p3 sig_type=std_logic lab=v_out}
C {devices/spice_probe.sym} 1180 -630 0 0 {name=p6 attrs=""}
C {devices/code_shown.sym} 0 -190 0 0 {name=SAVE only_toplevel=true
format="tcleval( @value )"
value=".include [file rootname [xschem get schname]].save
"}
C {ldo-005-ti-ldo-buffer-ref/ihp130/error_amp/error_amp.sym} 970 -690 0 0 {name=x1}
C {devices/vsource.sym} 600 -370 0 0 {name=VDD value=6 savecurrent=false}
C {devices/vsource.sym} 700 -370 0 0 {name=Vin value="dc 0 pwl(0 0 1u 0 1.1u 6)" savecurrent=false}
C {devices/vdd.sym} 600 -420 0 0 {name=l2 lab=VDD}
C {devices/gnd.sym} 600 -320 0 0 {name=l4 lab=GND}
C {devices/gnd.sym} 700 -320 0 0 {name=l1 lab=GND}
C {devices/gnd.sym} 1075 -530 0 0 {name=l7 lab=GND}
C {devices/lab_pin.sym} 880 -640 0 0 {name=p2 sig_type=std_logic lab=v_in}
C {devices/lab_pin.sym} 700 -420 0 0 {name=p4 sig_type=std_logic lab=v_in}
C {devices/gnd.sym} 1300 -510 0 0 {name=l6 lab=GND}
C {devices/vdd.sym} 1075 -730 0 0 {name=l9 lab=VDD}
