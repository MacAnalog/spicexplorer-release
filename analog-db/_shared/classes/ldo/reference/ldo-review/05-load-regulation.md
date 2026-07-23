# 5. Load Regulation

[← Efficiency](04-efficiency.md) | [Index](README.md) | [Next: Line Regulation →](06-line-regulation.md)

---

Load regulation is a measure of the circuit's ability to maintain the specified output voltage under varying load conditions. Load regulation is defined as

$$\text{Load regulation};\quad \frac{\Delta V_o}{\Delta I_o} \tag{15}$$

Figure 12 shows a PMOS voltage regulator. The output voltage change for a given load change ($\Delta V_O / \Delta I_O$) under constant input voltage $V_I$ can be calculated as follows:

$Q_1$ is the series pass element, and $\beta$ is the current gain of $Q_1$. $g_a$ is the transconductance of the error amplifier at its operating point.

> **Figure 12. PMOS Voltage Regulator**
> Schematic: PMOS pass element $Q_1$ (gain $\beta$) between input $V_I$ and output node $P_1$, delivering $I_O$. The output feeds a divider $R_1$ (top) and $R_2$ (bottom) and load $R_L$. An error amplifier (transconductance $g_a$) compares the sensed voltage $V_s$ against reference $V_r$ ($V_{ref}$) and drives $Q_1$'s gate. Output voltage is $V_O \pm \Delta V_O$.

Assume that there is a small output current change ($\Delta I_O$). The change of output current causes the output voltage change. Thus,

$$\Delta V_o = \Delta I_o R_{eq} \tag{16}$$

Where $R_{eq}$ is the equivalent output resistor at $P_1$ ($R_{eq} = (R_1 + R_2) \| R_L \approx R_L$).

The change of sensed voltage multiplied by $g_a$ of the error amplifier input difference and $\beta$ of the PMOS current gain (Figure 12) must be enough to achieve the specified change of output current. Thus,

$$\Delta I_o = \beta\, g_a \Delta V_s = \beta\, g_a \left( \frac{R_2}{R_1 + R_2} \right) \Delta V_o \tag{17}$$

Then, the load regulation is obtained from equation (17).

$$\frac{\Delta V_o}{\Delta I_o} = \frac{1}{\beta g_a} \left( \frac{R_1 + R_2}{R_2} \right) \tag{18}$$

Since load regulation is a steady-state parameter, all frequency components are neglected. The load regulation is limited by the open loop current gain of the system. As noted from the above equation, increasing dc open-loop current gain improves load regulation.

## 5.1 Application Implications

The worst case of the output voltage variations occurs as the load current transitions from zero to its maximum rated value or vice versa. Figure 13 shows that the load regulation is determined by the $\Delta V_{LDR}$. Figure 14 shows the output voltage variation with respect to the output current with the TPS76350 5-V LDO regulator.

> **Figure 13. Load Transient Response of TPS76350**
> Two stacked time-domain traces versus time $t$ (µs). Top: output current $I_O$ (mA) steps from 0 up to ~150 mA and back to 0. Bottom: output voltage change (mV) shows a transient with a settled offset labeled $V_{LDR}$ during the loaded interval.

> **Figure 14. TPS76350 Output Voltage With Respect to Output Current**
> Plots output voltage variation (mV) versus output current $I_O$ (mA, 0 to ~180 mA). The variation stays near 0 at low current and increases (curve bending downward to roughly 50 mV) as output current approaches 150 mA.

---

[← Efficiency](04-efficiency.md) | [Index](README.md) | [Next: Line Regulation →](06-line-regulation.md)
