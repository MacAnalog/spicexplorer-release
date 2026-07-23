# 3. LDO Topologies

[← Quiescent Current](02-quiescent-current.md) | [Index](README.md) | [Next: Efficiency →](04-efficiency.md)

---

The regulator circuit can be partitioned into four functional blocks: the reference, the pass element, the sampling resistor, and the error amplifier as shown in Figure 10.

> **Figure 10. Linear Regulator**
> Block schematic of a linear regulator. The input rail ($V_I$, current $I_I$) feeds a **Pass Element** with dropout voltage $V_{DO}$ across it and drive current $I_{drv}$, delivering output current $I_O$ at $V_O$. A reference $V_{ref}$ and an error amplifier compare against the output through a sampling resistor divider. Bias/reference current $I_a$, feedback current $I_r$, and sampling current $I_s$ return to ground.

Figure 11 shows that linear voltage regulators can be classified based on pass element structures: NPN-Darlington, NPN, PNP, PMOS, and NMOS regulators. The bipolar devices can deliver the highest output currents for a given supply voltage. The MOS-based circuits offer limited drive performance with a strong dependence on aspect ratio (width to length ratio) and to voltage-gate drive. On the positive side, however, the voltage-driven MOS devices minimize quiescent current flow.

> **Figure 11. Pass Element Structures**
> Five pass-element configurations, each shown with its dropout voltage $V_{DO}$:
> - **(a) Darlington:** two stacked NPN transistors; dropout includes $V_{sat}$ plus $2V_{BE}$.
> - **(b) NPN:** NPN pass transistor driven so that dropout includes $V_{sat}$ plus $V_{BE}$; base current $I_b$ shown.
> - **(c) PNP:** PNP pass transistor with drive current $I_{drv}$.
> - **(d) PMOS:** PMOS pass transistor.
> - **(e) NMOS:** NMOS pass transistor with gate-source voltage $V_{GS}$ and $V_{sat}$ shown.

The Darlington requires at least 1.6 V of dropout voltage to regulate, while the LDO will typically work with less than 500 mV of input-to-output voltage differential. The dropout voltage of NPN-Darlington is given by

$$V_{(dropout)} = V_{CE}(sat) + 2V_{BE} \cong 1.6 \sim 2.5\ V \quad \text{for Darlington} \tag{7}$$

The NPN regulator is comprised of an NPN and a PNP transistor. The base potential of the NPN transistor should always be higher than the emitter potential to ensure proper operation of the pass element. When the input-output differential voltage is high, there is no problem. When the input voltage approaches the output voltage, the control circuit pushes the pass element toward saturation to ensure proper operation of the regulator, and the value of the transistor equivalent variable resistor decreases. However, the equivalent variable resistor can not decrease to zero because the transistor NPN needs to maintain a necessary $V_{be}$ level. Below a certain level of input voltage, the regulator cannot maintain the regulation.

The minimum voltage difference between the input and output required to maintain regulation (dropout voltage) is given by

$$V_{(dropout)} = V_{CE}(sat) + V_{BE} \geq 0.9\ V \quad \text{for NPN regulator} \tag{8}$$

The NPN transistor receives its drive current from the input rail through the PNP transistor. The base drive circuit contributes its emitter current ($I_{drv}$) to output current ($I_O$). Therefore, the quiescent current of the NPN regulator is small. The quiescent current for the NPN regulator is defined as follows:

$$I_q = I_{bias} \quad \text{for NPN regulator} \tag{9}$$

Where:
- $I_q$ = quiescent current
- $I_{bias}$ = total bias current ($I_{bias} = I_a + I_r + I_s$)

The PNP regulator shown in Figure 11 (c) operates the same as the NPN with the exception that the NPN pass transistor has been replaced by a single PNP transistor. The big advantage of the PNP regulator is that the PNP pass transistor can maintain output regulation with very little voltage drop across it.

$$V_{(dropout)} = V_{CE}(sat) \cong 0.15 \sim 0.4\ V \quad \text{for PNP regulator} \tag{10}$$

By selecting a high-gain series transistor, dropout voltages as low as 150 mV at 100 mA are possible. However, the base drive current flows to ground and no longer contributes to the output current. The value of this ground current directly depends on the pass element transistor's gain. Thus, the quiescent current of the PNP regulator is higher than the NPN regulator. The quiescent current is defined as follows:

$$I_q = I_{drv} + I_{bias} \cong 0.8 \sim 2.6\ mA \quad \text{for PNP regulator} \tag{11}$$

Where:
- $I_{drv}$ = base drive current of PNP

Figures 11(d) and 11(e) show the P-MOS and N-MOS voltage regulators respectively, which employ MOSFETs as the pass element. The PMOS devices have very low dropout voltages. The NMOS can have a low dropout voltage with a charge pump. The dropout voltage is determined by saturation voltage across the pass element, and the dropout voltage is proportional to the current flowing through the pass element.

$$V_{(dropout)} = I_O R_{on} \cong 35 \sim 350\ mV \quad \text{for PMOS regulator} \tag{12}$$

where $R_{on}$ is the on-resistance of the pass element

At light load, the dropout voltage is only a few millivolts. At full load, the typical dropout voltage is 300 mV for most of the families. The MOSFET pass element is a voltage controlled device and, unlike a PNP transistor, does not require increased drive current as output current increases. Thus, very low quiescent current is obtained (less than 1 mA).

## 3.1 Application Implications

Table 1 summarizes the differences of these pass element devices. [2]

**Table 1. Comparison of Pass Element Structures**

| PARAMETER | DARLINGTON | NPN | PNP | NMOS | PMOS |
|-----------|-----------|-----|-----|------|------|
| $I_{O,max}$ | High | High | High | Medium | Medium |
| $I_q$ | Medium | Medium | Large | Low | Low |
| $V_{dropout}$ | $V_{sat} + 2V_{be}$ | $V_{sat} + V_{be}$ | $V_{ce(sat)}$ | $V_{sat} + V_{gs}$ | $V_{SD(sat)}$ |
| Speed | Fast | Fast | Slow | Medium | Medium |

Traditionally, the PNP bipolar transistor has been applied to low dropout applications, primarily because it easily enables a low drop out voltage. However, it has a high quiescent current and low efficiency, which are not ideal in applications where maximizing efficiency is a priority. The NMOS pass element is most advantageous due to its low on resistance. Unfortunately, the gate drive difficulties make it less than ideal in applications and as a result there are few NMOS LDOs available. PMOS devices have been highly developed and now have performance levels exceeding most bipolar devices.

---

[← Quiescent Current](02-quiescent-current.md) | [Index](README.md) | [Next: Efficiency →](04-efficiency.md)
