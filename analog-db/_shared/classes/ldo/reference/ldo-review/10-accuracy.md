# 10. Accuracy

[← Range of Stable ESR](09-range-of-stable-esr.md) | [Index](README.md) | [Next: References →](11-references.md)

---

Accuracy specifies all effects of line regulation ($\Delta V_{LR}$), load regulation ($\Delta V_{LDR}$), reference voltage drift ($\Delta V_{o,ref}$), error amplifier voltage drift ($\Delta V_{o,a}$), external sampling resistor tolerance ($\Delta V_{o,r}$), and temperature coefficient ($\Delta V_{TC}$). It can be defined by

$$
\text{Accuracy} \approx \frac{|\Delta V_{LR}| + |\Delta V_{LDR}| + \sqrt{\Delta V_{o,ref}^2 + \Delta V_{o,a}^2 + \Delta V_{o,r}^2 + \Delta V_{TC}^2}}{V_o} \times 100
\tag{42}
$$

Output voltage variation in a regulated power supply is due primarily to temperature variation of the constant voltage reference source and temperature variation of the difference amplifier characteristics as well as the sampling resistor tolerance. Load regulation, line regulation, gain error, and offsets normally account for 1% to 3% of the overall accuracy.

Output voltage variations resulting from the reference voltage drift, error amplifier voltage drift, and sampling resistor tolerance that are due to inter-lot and process variations are detailed in this section.

## 10.1 Reference Voltage Drift

Assume the LDO regulator exhibits the reference voltage drift ($V_d$) as shown in Figure 26. The reference voltage drift directly causes the output voltage change ($\Delta V_{o,ref}$).

> **Figure 26. LDO With Reference Voltage Drift**
> Schematic: PMOS pass element $Q_1$ (gain $\beta$) from $V_I$ to output, with divider $R_1$/$R_2$ and load $R_L$. Error amplifier ($g_a$) senses $V_s$ against a reference whose value includes drift, shown as $V_r \pm V_d$. Output is $V_O + \Delta V_{o,ref}$.

Thus, the resultant output voltage is

$$V_o + \Delta V_{o,ref} = \left[ V_s - (V_r \pm V_d) \right] g_a \beta R_L \tag{43}$$

The sensed voltage $V_s$ is given by

$$V_s = \frac{R_2}{R_1 + R_2} (V_o + \Delta V_{o,ref}) \tag{44}$$

Substituting equation (44) into equation (43),

$$
V_o + \Delta V_{o,ref} = \left[ \frac{R_2}{R_1 + R_2}(V_o + \Delta V_{o,ref}) - (V_r \pm V_d) \right] g_a \beta R_L
= \frac{(R_1 + R_2)(-V_r \mp V_d) g_a \beta R_L}{R_1 + R_2 - R_2 g_a \beta R_L}
\tag{45}
$$

Now in the usual case,

$$g_a \beta V_s \gg 1 \tag{46}$$

From equation (45) and (46), the output voltage is obtained.

$$V_o + \Delta V_{o,ref} = \frac{R_1 + R_2}{R_2}(V_r \pm V_d) \tag{47}$$

Now, the right hand side of the equation can be split into two parts. One is the average output voltage and the other is the function of the reference voltage drift. The average output voltage is then given by

$$V_o = \frac{(R_1 + R_2)}{R_2} V_r \tag{48}$$

Thus, the output voltage variation resulting from reference voltage drift is obtained from equation (47).

$$\Delta V_{o,ref} = \frac{R_1 + R_2}{R_2}(\pm V_d) \tag{49}$$

From equations (48) and (49), the following equation is obtained.

$$\frac{\Delta V_{o,ref}}{V_O} = \pm \frac{V_d}{V_r} \tag{50}$$

Equation (50) shows that the output voltage variation is directly affected by the accuracy of the reference voltage. If the reference voltage accuracy is 1%, then the output voltage of the regulator will exhibit the same percentage of variation.

## 10.2 Error Amplifier Voltage Drift

The error amplifiers exhibit drift characteristics with temperature. Assume that an error (or drift) voltage $V_d$ appears at the output of the amplifier as shown in Figure 27.

> **Figure 27. LDO With Error Amplifier Voltage Drift**
> Schematic: PMOS pass element $Q_1$ (gain $\beta$) from $V_I$ to output, divider $R_1$/$R_2$, load $R_L$, reference $V_{ref}$. A drift voltage $\pm V_d$ is injected at the error amplifier ($g_a$) output. Output is $V_O \pm V_{o,a}$.

The output change $\Delta V_{o,a}$ resulting from the drift voltage $V_d$ is obtained from Figure 27.

$$\Delta V_{o,a} = \beta V_d R_L \pm g_a \beta \Delta V_s R_L \tag{51}$$

The sensed voltage $\Delta V_s$ is given by

$$\Delta V_s = \frac{R_2}{R_1 + R_2} \Delta V_{o,a} \tag{52}$$

Substituting equation (52) into equation (51)

$$\Delta V_{o,a} = \frac{\beta V_d (R_1 + R_2) R_L}{R_1 + R_2 \pm g_a \beta R_2 R_L} \tag{53}$$

By equation (46), the output voltage variation resulting from the error amplifier voltage drift is obtained as follows.

$$\Delta V_{o,a} = \pm \frac{V_d (R_1 + R_2)}{g_a R_2} \tag{54}$$

## 10.3 Tolerance of External Sampling Resistors

For adjustable regulators, the output depends on the accuracy of two sampling resistors. Suppose that the sampling resistors of an LDO regulator have tolerances such as $\pm R_1$ and $\pm R_2$ as shown in Figure 28.

> **Figure 28. LDO With Sampling Resistors**
> Schematic: PMOS pass element $Q_1$ (gain $\beta$) from $V_I$ to output, load $R_L$, reference $V_{ref}$, error amplifier ($g_a$) sensing $V_s$ against $V_r$. The divider resistors carry tolerances: $R_1 \pm \Delta R_1$ (top) and $R_2 \pm \Delta R_2$ (bottom). Output is $V_O \pm V_{o,r}$.

The output voltage change resulting from the sampling resistor tolerance is

$$V_o + \Delta V_{o,r} = g_a \beta (V_s - V_r) R_L \tag{55}$$

The sensed voltage $V_s$ is given by

$$V_s = \frac{(R_2 \pm \Delta R_2)}{(R_1 \pm \Delta R_1) + (R_2 \pm \Delta R_2)} (V_o + \Delta V_{o,r}) \tag{56}$$

Substituting $V_s$ into equation (55)

$$
V_o + \Delta V_{o,r} = \frac{-g_a \beta V_r \left[ (R_1 \pm \Delta R_1) + (R_2 \pm \Delta R_2) \right] R_L}{(R_1 \pm \Delta R_1) + (R_2 \pm \Delta R_2) - g_a \beta (R_2 \pm \Delta R_2) R_L}
\tag{57}
$$

By equation (46), the output voltage resulting from the tolerance of the sampling resistors is obtained as follows.

$$V_o + \Delta V_{o,r} = \frac{(R_1 \pm \Delta R_1) + (R_2 \pm \Delta R_2)}{(R_2 \pm \Delta R_2)} V_r \tag{58}$$

Thus, the average output voltage is given by

$$V_o = \frac{R_1 + R_2}{R_2 \pm \Delta R_2} V_r \tag{59}$$

The average output voltage is a function of the resistor accuracy. Specifically, the bottom side of the resistor dominates the overall LDO accuracy. The output voltage variation due to the resistor tolerance is given by.

$$\Delta V_{o,r} = \pm \frac{\Delta R_1 + \Delta R_2}{R_2 \pm \Delta R_2} V_r \tag{60}$$

## 10.4 Application Implications—an Example

What is the total accuracy of the 3.3-V LDO regulator shown in Figure 29 over the temperature span from 0° to 125° with the following operating characteristics?

- Temperature coefficient is 100 ppm/°C.
- Sampling resistor tolerance is 0.25%.
- Output voltage change resulting from load regulation, and line regulation are ±5 mV, and ±10 mV, respectively.
- Accuracy of the reference is 1%.

> **Figure 29. LDO Regulator**
> Schematic: PMOS pass element $Q_1$ (gain $\beta$) from $V_I$ to output $V_O$, load $R_L$. A symmetric divider with two equal resistors $R$ (top and bottom) sets the output; the error amplifier ($g_a$) senses the midpoint $V_s$ against reference $V_{ref}$ ($V_{ref}$ shown at the amplifier input and as the reference block). Because both divider resistors are equal ($R$), $V_O = 2V_{ref}$.

The output voltage is given by

$$V_o = \frac{R + R}{R} V_{ref} = 2 V_{ref} \tag{61}$$

Therefore, the reference voltage $V_{ref}$ is half of the output voltage (i.e. $V_{ref} = 3.3/2$ [V]), and

$$
\begin{aligned}
\Delta V_{TC} &= \text{Temperature Coefficient} \times (T_{max} - T_{min}) \times V_o \\
&= (100\ ppm/°C)(125°C)(3.3\ V) = 41.2\ mV
\end{aligned}
\tag{62}
$$

$$
\begin{aligned}
\Delta V_{o,r} &= (0.25\%\ of\ V_o + 0.25\%\ of\ V_o) V_{ref} \\
&= (0.005)(3.3)\frac{3.3}{2} = 27\ mV
\end{aligned}
$$

From equation (49), the output voltage variation resulting from the reference voltage is obtained as follows.

$$\Delta V_{o,ref} = 2\left(\frac{3.3}{2}\right) 0.01 = 33\ mV \tag{63}$$

Where

$$V_d = V_{ref} \times 0.01 = \left(\frac{3.3}{2}\right) \times 0.01$$

Therefore, the overall accuracy of the LDO is obtained as follows,

$$
\text{Accuracy} \approx \frac{10\ mV + 5\ mV + \sqrt{(33\ mV)^2 + (27\ mV)^2 + (41.2\ mV)^2}}{3.3\ V} \times 100 \approx 2.25\%
\tag{64}
$$

---

[← Range of Stable ESR](09-range-of-stable-esr.md) | [Index](README.md) | [Next: References →](11-references.md)
