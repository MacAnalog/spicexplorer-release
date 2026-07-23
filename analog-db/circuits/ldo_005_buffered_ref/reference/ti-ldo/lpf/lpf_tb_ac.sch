v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
N 1176.25 -323.75 1176.25 -303.75 {lab=VDD}
N 1276.25 -323.75 1276.25 -303.75 {lab=vin}
N 1276.25 -243.75 1276.25 -223.75 {lab=GND}
N 1176.25 -243.75 1176.25 -223.75 {lab=GND}
N 1720 -740 1740 -710 {lab=#net1}
N 1741.25 -538.75 1743.75 -560 {lab=GND}
N 1840 -640 1900 -640 {lab=vout}
N 1521.25 -638.75 1580 -640 {lab=vin}
N 1898.75 -678.75 1900 -640 {lab=vout}
C {lpf/lpf_rc.sym} 1600 -690 0 0 {name=x1}
C {devices/title.sym} 198.75 -51.25 0 0 {name=l1 author="Danial Noori Zadeh"}
C {devices/code_shown.sym} 913.75 -991.25 0 0 {name=MODELS only_toplevel=true
format="tcleval( @value )"
value="
.include $::180MCU_MODELS/design.ngspice
.lib $::180MCU_MODELS/sm141064.ngspice typical

.lib $::180MCU_MODELS/sm141064.ngspice res_typical
* .lib $::180MCU_MODELS/sm141064.ngspice res_statistical
"}
C {devices/code_shown.sym} 38.75 -991.25 0 0 {name=NGSPICE only_toplevel=true
value="
* ====== NGSPICE_AC_Response Control Block ======
.control
save all

* === Sweep Params ===
let f_start = 1
let f_stop  = 1e9
let f_step  = 10

* === Source Setup ===
let vin_ac_mag = 1
let vin_dc_bias = 3.0
alter @VIN[DC] = $&vin_dc_bias
alter @VIN[AC] = $&vin_ac_mag

* === OP + AC Sweep ===
op
ac dec $&f_step $&f_start $&f_stop

* === Signal Processing ===
let vout_mag = abs(v(vout))
let vout_dB  = 20*log10(vout_mag)
*let vout_ph  = phase(v(vout))
let vout_ph  = 180/PI*cph(vout)


* === Plots ===
settype decibel out
plot vout_dB vs frequency xlimit $&f_start $&f_stop ylabel 'signal gain'

plot vout_ph vs frequency

* === Measurements ===
* Max Gain
meas ac gain_max max vout_dB
meas ac f_peak when vout_dB=GAIN_MAX

* 3dB below peak gain
let gain_3dB = gain_max - 3

* Lower and Upper 3dB Frequencies
*meas ac f_lo when vout_dB=gain_3dB fall=1
*meas ac f_hi when vout_dB=gain_3dB rise=1

* Post-Processing for BW and Q (use let)
* If previous failed, fallback values will be undefined or skipped
*let bw = f_hi - f_lo
*let q  = f_peak / bw

* Print Results
*print gain_max
*print f_peak
*print f_lo
*print f_hi
*print bw
*print q

* Save Raw
write NGSPICE_AC_Response.raw
.endc


"
}
C {devices/vsource.sym} 1176.25 -273.75 0 0 {name=VDD value=6 savecurrent=false}
C {devices/vsource.sym} 1276.25 -273.75 0 0 {name=VIN value=3 savecurrent=false}
C {devices/vdd.sym} 1176.25 -323.75 0 0 {name=l2 lab=VDD}
C {devices/gnd.sym} 1176.25 -223.75 0 0 {name=l4 lab=GND}
C {devices/gnd.sym} 1276.25 -223.75 0 0 {name=l5 lab=GND}
C {devices/lab_pin.sym} 1276.25 -323.75 0 0 {name=p5 sig_type=std_logic lab=vin}
C {devices/launcher.sym} 1666.25 -223.75 0 0 {name=h1
descr="Annotate OP"
tclcommand="set show_hidden_texts 1; xschem annotate_op"}
C {devices/vdd.sym} 1721.25 -738.75 0 0 {name=l3 lab=VDD}
C {devices/gnd.sym} 1741.25 -538.75 0 0 {name=l7 lab=GND}
C {devices/noconn.sym} 1900 -640 0 1 {name=l8}
C {devices/lab_pin.sym} 1521.25 -638.75 0 0 {name=p1 sig_type=std_logic lab=vin}
C {devices/lab_pin.sym} 1898.75 -678.75 1 0 {name=p2 sig_type=std_logic lab=vout}
