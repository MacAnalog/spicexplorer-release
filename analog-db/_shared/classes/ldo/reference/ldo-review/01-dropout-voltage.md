# 1. Dropout Voltage

[← Index](README.md) | [Next: Quiescent Current →](02-quiescent-current.md)

---

Dropout voltage is the input-to-output differential voltage at which the circuit ceases to regulate against further reductions in input voltage; this point occurs when the input voltage approaches the output voltage. Figure 1 shows an example of a simple NMOS low dropout (LDO) voltage regulator.

> **Figure 1. LDO Voltage Regulator**
> Schematic of a simple NMOS LDO regulator. An NMOS series pass element (source S, drain D, gate G) sits between the input ($V_I$, with input current $I_d$ flowing to the drain) and the output ($V_O$ across output resistance $R_O$). The drain-to-source voltage of the pass element is labeled $V_{ds}$. A Control Circuit drives the gate.

LDO operation can be explained using the NMOS series pass element I-V characteristics shown in Figure 2. NMOS devices are not widely used in LDO designs, but they simplify the explanation of LDO performance. Figure 2 (a) shows the two regions of operation—linear and saturation. In the linear region, the series pass element acts like a series resistor. In the saturation region, the device becomes a voltage-controlled current source. Voltage regulators usually operate in the saturation region.

> **Figure 2. Series Pass Element I-V Characteristic and LDO Equivalent Circuits**
> - **(a) I-V Characteristic of n-channel MOSFET:** Plots drain current $I_d$ versus $V_{ds} = V_I - V_O$ for several gate-source voltages ($V_{gs1}$ through $V_{gs5}$). The **Linear Region** (operation like a resistor, slope = $R_i$) lies to the left of $V_{ds(sat)}$; the **Saturation Region** (operation like a current source) lies to the right.
> - **(b) LDO Equivalent Circuit in The Linear Region:** The series pass element is modeled as a resistor $R_i$ between source and drain; $V_I$ drives current $I_d$ into $R_O$ to produce $V_O$.
> - **(c) LDO Equivalent Circuit in The Saturation Region:** The series pass element is modeled as a controlled current source $\beta V_{gs}^2$ in parallel with $R_{ds}$, controlled by gate-source voltage $V_{gs}$.

Figures 2 (b) and (c) show the LDO equivalent circuits for the two operating regions. The control circuit is not shown. Figure 2 (c) shows the LDO equivalent circuit in the saturation region (assume threshold voltage is zero). There is a constant current source between the drain and source, which is a function of gate-to-source voltage, $V_{gs}$. The drain current (load current) is given by

$$I_d = \beta V_{gs}^2 \tag{1}$$

Where $\beta$ is a current gain.

From equation (1), the series pass element acts like a constant current source in the saturation region in terms of gate-to-source voltage. Under varying load conditions, $V_{gs}$ controls the LDO regulator to supply the demand output load. Figure 3 illustrates the LDO operation in the saturation region. When load current increases from $I_{d2}$ to $I_{d3}$, the operating point moves from $P_0$ to $P_2$, and the input-to-output voltage differential, $V_{ds}$, is given by

$$V_{ds} = V_I - V_O \tag{2}$$

> **Figure 3. NMOS Operation With LDO in Saturation Region**
> Plots $I_{ds}$ versus $V_{ds} = V_I - V_O$ with the transfer curve ($\beta$, $I_{ds}$ vs $V_{gs}$) mirrored on the left. Curves for $V_{gs1}$ through $V_{gs4}$ are shown. A shaded "Operation Within Regulation" band is marked. Operating points $P_0$, $P_1$, and $P_2$ correspond to currents $I_{d1}$, $I_{d2}$, $I_{d3}$ and dropout/operating voltages $V_{ds1}$, $V_{ds0}$, $V_{ds2}$. The dropout point $V_{(Dropout)}$ is at the left edge of regulation.

From equation (2) and Figure 3, as the input voltage decreases, the voltage regulator pushes the operating point toward $P_1$ (toward the dropout region). As the input voltage nears the output voltage, a critical point exists at which the voltage regulator can not maintain a regulated output. The point at which the LDO circuit begins to lose loop control is called the dropout voltage. Below the dropout voltage, the LDO regulator can no longer regulate the output.

> **Figure 4. NMOS Operation With LDO in Dropout Region**
> Plots output current $I_O$ versus $V_{ds} = V_I - V_O$ for the pass element operating in the dropout/linear region as input voltage decreases. Curves for $V_{gs1}$ through $V_{gs7}$ are shown, bounded by the linear-region equivalent resistances $R_{i(min)}$ and $R_{i(max)}$. An "Operation Within Regulation" band is shaded. Operating points $P_1$, $P_2$, $P_3$ and the turnoff point $P_{to}$ are shown at output current $I_{O1}$ across $V_{ds}$ values $V_1$, $V_2$, $V_3$.

In the dropout region, the series pass element limits the load current like a resistor—as shown in Figure 2 (b). Figure 4 shows NMOS operation with the LDO regulator in the dropout region and decreasing input voltage. The equivalent resistors $R_{i(max)}$ and $R_{i(min)}$ are the maximum and minimum values respectively of the series pass element in the linear region. When the input voltage decreases to near the output voltage, the operating point $P_1$ moves to the operating point $P_2$ that is the minimum regulating point at the specific load condition ($I_{O1}$) (i.e., dropout voltage). Within the dropout region, $V_{gs}$ is not a function of the control loop, but of the input voltage. In other words, the regulator control loop cut off and $V_{gs}$ begins to depend on the decreasing input voltage. Thus when the input voltage decreases further, the control voltage ($V_{gs}$) also decreases in proportion to the decreasing input voltage. The operating point moves down to $P_3$ from $P_2$. Finally, the regulator reaches the turnoff point, $P_{to}$.

> **Figure 5. Typical Input/Output Voltage Characteristics of a Linear Regulator**
> Plots voltage versus $V_{(dropout)}$ showing input voltage $V_I$ (a straight rising line), output voltage $V_O$, and the pass-element drop $V_{ds}$. Three regions are delineated: the **Off Region**, the **Dropout Region**, and the **Regulation Region**. Below $V_{(dropout)}$ the output voltage drops with decreasing input voltage.

Figure 5 shows the dropout region in relation to the off and regulation regions. Below $V_{(dropout)}$, the output voltage drops with decreasing input voltage.

## 1.1 Application Implications

In dropout region, the magnitude of the dropout voltage depends on the load current and the on resistance ($R_{on}$) of the series pass element. It is given by

$$V_{do} = I_{Load} R_{on} \tag{3}$$

Throughout the dropout region, the output voltage is not maintained any more by the control loop since the control loop is electrically disconnected at the output of the controller (Figure 1) and then the pass device acts like a resistor. Therefore, the output voltage can be pulled down to ground by the load.

Figure 6 shows the input-output characteristics of the TPS76333 3.3-V LDO regulator. The dropout voltage of the TPS76333 is typically 300 mV at 150 mA. The LDO regulator begins dropping out at 3.6-V input voltage; the range of the dropout region is between 3.6 V and 2.0 V input voltage.

> **Figure 6. Dropout Region of TI TPS76333 (3.3-V LDO)**
> Plots output voltage $V_O$ (V) versus input voltage $V_I$ (V) for the TPS76333. Output holds at 3.3 V in the **Regulation Region** (above 3.6 V input, shown out to 10 V). The **Dropout Region** spans roughly 2.0 V to 3.6 V input, where output rises with input. Below 2.0 V is the **Off Region**.

---

[← Index](README.md) | [Next: Quiescent Current →](02-quiescent-current.md)
