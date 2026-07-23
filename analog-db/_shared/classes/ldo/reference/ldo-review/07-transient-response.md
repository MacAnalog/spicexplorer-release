# 7. Transient Response

[← Line Regulation](06-line-regulation.md) | [Index](README.md) | [Next: Frequency Response →](08-frequency-response.md)

---

The transient response is an important specification, which is the maximum allowable output voltage variation for a load current step change. The transient response is a function of the output capacitor value ($C_O$), the equivalent series resistance (ESR) of the output capacitor, the bypass capacitor ($C_b$), and the maximum load-current ($I_{O,max}$). The application determines how low this value should be. The maximum transient voltage variation is defined as follows [2].

$$\Delta V_{tr,max} = \frac{I_{o,max}}{C_o + C_b} \Delta t_1 + \Delta V_{ESR} \tag{28}$$

Where $\Delta t_1$ corresponds to the closed loop bandwidth. $\Delta V_{ESR}$ is the voltage variation resulting from the presence of the ESR ($R_{ESR}$) of the output capacitor. $\Delta V_{ESR}$ is proportional to $R_{ESR}$.

## 7.1 Application Implications

A LDO voltage regulator with output capacitor of 4.7 µF is shown in Figure 17.

> **Figure 17. 1.2-V, 100-mA LDO Voltage Regulator With Output Capacitor of 4.7 µF**
> Schematic of an LDO regulator (PMOS pass element, error amplifier, reference $V_{ref}$) driving an output network: output capacitor $C_O = 4.7\ \mu F$ in series with its ESR $R_{ESR}$, a bypass capacitor $C_b$, and load $R_L$, all across the output $V_O$.

Figure 18 illustrates the transient response of a 1.2 V, 100 mA LDO regulator with an output capacitor of 4.7 µF shown in Figure 17. A step change of load current (near 90 mA) was applied to the regulator which is shown in the upper trace of the figure. It is noted that in the lower trace the output voltage drops approximately 120 mV and then the voltage control loop begins to respond to the step load change in 1 µs ($\Delta t_1 = 1\ \mu s$). Finally, the output voltage reaches to a stble state within 17 µs. From equation 28, the calculated maximum voltage variation is given by:

$$\Delta V_{tr,max} = \frac{90\ mA}{4.7\ \mu F + 0} \times 1\ \mu s + \Delta V_{ESR} = 19\ mV + \Delta V_{ESR} = 120\ mV \tag{29}$$

Therefore, the output voltage variation of 101 mV is caused by the $\Delta V_{ESR}$. The effects of $\Delta V_{ESR}$ can be reduced by adding bypass capacitors shown in Figure 17, which normally exhibit low ESR value.

To decrease the voltage variation resulting from the load transient, a big value of output capacitor and the low ESR of the capacitor are recommended. However, the *Tunnel of Death* (discussed in section 9) limits the values of output capacitor and its ESR value.

> **Figure 18. Transient Response of Step Load Change of 1.2-V, 100-mA LDO Voltage Regulator With an Output Capacitor Co=4.7 µF**
> Oscilloscope capture (Tek, 10.0 MS/s, 22 Acqs). Upper trace: output current stepping up (50 mA/div). Lower trace: 1.2 V output, AC coupled (50 mV/div), showing the transient dip $V_{tr,max}$ and the response time $t_1$, with subsequent ringing settling to steady state. Horizontal scale M 5.00 µs.

---

[← Line Regulation](06-line-regulation.md) | [Index](README.md) | [Next: Frequency Response →](08-frequency-response.md)
