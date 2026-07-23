# 6. Line Regulation

[← Load Regulation](05-load-regulation.md) | [Index](README.md) | [Next: Transient Response →](07-transient-response.md)

---

Line regulation is a measure of the circuit's ability to maintain the specified output voltage with varying input voltage. Line regulation is defined as

$$\text{Line regulation};\quad \frac{\Delta V_o}{\Delta V_I} \tag{19}$$

The output voltage change for a given input voltage change ($\Delta V_O / \Delta V_I$) can be calculated from Figure 12 as follows;

$$
V_o = \frac{V_I R_{eq}}{R_{ds} + R_{eq}} - \Delta V_o = \frac{V_I R_{eq}}{R_{ds} + R_{eq}} - \Delta I_o R_{eq}
= \frac{V_I R_{eq}}{R_{ds} + R_{eq}} - G(V_s - V_r) R_{eq}
\tag{20}
$$

where the open loop current gain $G = \beta \times g_a$, and $R_{ds}$ is the equivalent resistor between drain and source of the series pass element. $R_{eq}$ is the equivalent output resistor at the point $P_1$ ($R_{eq} = (R_1 + R_2) \| R_L \approx R_L$). The sensed voltage $V_s$ is given by

$$V_s = \frac{R_2}{R_1 + R_2} V_o \tag{21}$$

Substituting (21) into equation (20),

$$
V_o = \frac{\dfrac{R_{eq}(R_1 + R_2)}{R_{ds} + R_{eq}} V_I + (R_1 + R_2) G V_r R_{eq}}{R_1 + R_2 + G R_2 R_{eq}}
\tag{22}
$$

Now in the usual case,

$$G V_s \gg 1 \tag{23}$$

From equations (22) and (23), the output voltage is

$$
V_o = \frac{(R_1 + R_2)}{G R_2 (R_{ds} + R_{eq})} V_I + \frac{(R_1 + R_2)}{R_2} V_r
\tag{24}
$$

Now, the right hand side of the equation can be split into two parts. One is the steady state average output voltage and the another is the function of input voltage. The average steady state output voltage is then given by

$$V_o = \frac{(R_1 + R_2)}{R_2} V_r \tag{25}$$

Thus, the line regulation is obtained from equation (24).

$$\frac{\Delta V_o}{\Delta V_I} = \frac{1}{(R_{ds} + R_L)} \frac{(R_1 + R_2)}{G R_2} \tag{26}$$

Or substituting the open loop current gain $G$ into equation (26), the line regulation can be

$$\frac{\Delta V_o}{\Delta V_I} = \left[ \frac{1}{(R_{ds} + R_L)\beta g_a} \right] \left( \frac{R_1 + R_2}{R_2} \right) \tag{27}$$

Like load regulation, line regulation is a steady state parameter—all frequency components are neglected. Increasing dc open loop current gain improves the line regulation.

## 6.1 Application Implications

Figure 15 shows the input voltage transient response; the line regulation is determined by $\Delta V_{LR}$.

> **Figure 15. Line Transient Response of TPS76333**
> Two stacked time-domain traces versus time $t$ (µs). Top: input voltage $V_I$ (V) steps from 5 V up to ~6 V and back to 5 V. Bottom: output voltage change (mV) shows transient spikes at each edge and a settled offset labeled $V_{LR}$ during the raised-input interval.

Figure 16 shows the circuit performance of the TPS76333 3.3-V LDO regulator with respect to the input voltages. The broken line shows the range of output voltage variation resulting from the input voltage change (1.244 mV to 18.81 mV).

> **Figure 16. TPS76333 Output Voltage With Respect to Input Voltage**
> Plots output voltage $V_O$ (V) versus input voltage $V_I$ (V). Output rises steeply from ~2.0 V input, reaching regulation at 3.6 V and holding near 3.3 V out to 10 V. The **Output Voltage Variation** over the regulation range spans from 1.244 mV to 18.81 mV (indicated by broken lines).

---

[← Load Regulation](05-load-regulation.md) | [Index](README.md) | [Next: Transient Response →](07-transient-response.md)
