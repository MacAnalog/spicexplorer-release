# 2. Quiescent Current or Ground Current

[← Dropout Voltage](01-dropout-voltage.md) | [Index](README.md) | [Next: LDO Topologies →](03-ldo-topologies.md)

---

Quiescent current, or ground current, is the difference between input and output currents. Minimum quiescent current is necessary for maximum current efficiency. Quiescent current is defined by

$$I_q = I_I - I_O \tag{4}$$

Quiescent current consists of bias current (such as band-gap reference, sampling resistor and error amplifier) and drive current of the series pass element, which do not contribute to output power. The value of quiescent current is mostly determined by the series pass element, topologies, ambient temperature, etc.

Linear voltage regulators usually employ bipolar or MOS transistors as the series pass element. The collector current of bipolar transistors is given by

$$I_c = \beta I_b \tag{5}$$

where $\beta$ is forward current gain and typically ranges from 20-500, $I_c$ is the collector current, and $I_b$ is the base current. Figure 7 shows the I-V characteristic of bipolar transistors.

> **Figure 7. I-V Characteristic of Bipolar Transistors**
> Plots collector current $I_c$ versus collector-emitter voltage $V_{ce}$ for several base currents ($I_{b1}$ through $I_{b4}$), with the transfer relationship ($\beta$, $I_c$ vs $I_b$) mirrored on the left axis. Collector-current levels $I_{c1}$, $I_{c2}$, $I_{c3}$ correspond to base currents $I_{b1}$, $I_{b2}$, $I_{b3}$, showing base current proportional to collector current.

Equation (5) and Figure 7 show that the base current of bipolar transistors is proportional to the collector current. As load current increases, base current also increases. Since base current contributes to quiescent current, bipolar transistors intrinsically have high quiescent currents. In addition, during the drop out region the quiescent current can increase due to the additional parasitic current path between the emitter and the base of the bipolar transistor, which is caused by a lower base voltage than that of the output voltage.

The drain-source current of MOS transistors is given by

$$I_{ds} = \beta_1 (V_{gs} - V_t)^2 \tag{6}$$

where $\beta_1$ is a MOS transistor gain factor, $V_{gs}$ is the gate-to-source voltage, and $V_t$ is the device threshold. Figure 8 shows the I-V characteristic of MOS transistors.

> **Figure 8. I-V Characteristic of MOS Transistors**
> Plots drain-source current $I_{ds}$ versus $V_{ds}$ for several gate-source voltages ($V_{gs1}$ through $V_{gs4}$), with the transfer curve ($\beta_1$, $I_{ds}$ vs $V_{gs}$) mirrored on the left axis. Current levels $I_{ds2}$, $I_{ds3}$, $I_{ds4}$ correspond to $V_{gs2}$, $V_{gs3}$, $V_{gs4}$.

The drain-to-source current is a function of the gate-to-source voltage, not the gate current. Thus, MOS transistors maintain a near constant gate current regardless of the load condition.

## 2.1 Application Implications

Figure 9 shows the quiescent current of both transistors with respect to the load current.

> **Figure 9. Quiescent Current and Output Current**
> Plots quiescent current $I_q$ versus output current $I_O$. The **Bipolar Transistor** curve rises linearly with output current. The **MOS Transistor** curve stays nearly flat (near constant). Both start from a small **Standby Current** at zero output current.

For bipolar transistors, the quiescent current increases proportionally with the output current because the series pass element is a current-driven device. For MOS transistors, the quiescent current has a near constant value with respect to the load current since the device is voltage-driven. The only things that contribute to the quiescent current for MOS transistors are the biasing currents of band-gap, sampling resistor, and error amplifier. In applications where power consumption is critical or where small bias current is needed in comparison with the output current, an LDO voltage regulator employing MOS transistors is essential.

---

[← Dropout Voltage](01-dropout-voltage.md) | [Index](README.md) | [Next: LDO Topologies →](03-ldo-topologies.md)
