# 8. Frequency Response

[← Transient Response](07-transient-response.md) | [Index](README.md) | [Next: Range of Stable ESR →](09-range-of-stable-esr.md)

---

Figure 19 shows the essential elements of a linear regulator. [2] The error amplifier is modeled by a transconductor ($g_a$) with a load comprised of capacitor $C_{par}$ and resistor $R_{par}$. The series pass element (MOS transistor) is modeled by a small signal model with transconductance $g_p$. An output capacitor $C_O$ with an equivalent series resistor ($R_{ESR}$) and a bypass capacitor $C_b$ is added.

> **Figure 19. AC Model of a Linear Regulator**
> Small-signal AC model. The series pass element is a MOS small-signal model: gate-source voltage $V_{gs}$ across gate capacitance, a controlled current source $V_{gs} g_p$, and output resistance $R_{ds}$ between drain and source. In the LDO block, $g_p$ drives the output; the error amplifier ($g_a$) is loaded by $R_{par}$ and $C_{par}$ and referenced to $V_{ref}$, sensing through divider $R_1$/$R_2$. The output $V_O$ drives the network $R_{ESR}$ + $C_O$ and bypass $C_b$, with load current source $I_L$. Output impedance $Z_o$ is measured looking into the output node.

From Figure 19, the output impedance is given by

$$
Z_o = R_{12p} \left\| \left( R_{ESR} + \frac{1}{S C_o} \right) \right\| \frac{1}{S C_b}
= \frac{R_{12p}(1 + S R_{ESR} C_o)}{S^2 R_{12p} R_{ESR} C_o C_b + S\left[ (R_{12p} + R_{ESR}) C_o + R_{12p} C_b \right] + 1}
\tag{30}
$$

Where

$$R_{12p} = R_{ds} \| (R_1 + R_2) \approx R_{ds} \tag{31}$$

Typically, the output capacitor value $C_O$ is considerably larger than the bypass capacitor $C_b$. Thus, the output impedance $Z_o$ approximates to

$$
Z_o \approx \frac{R_{ds}(1 + S R_{ESR} C_o)}{\left[ 1 + S(R_{ds} + R_{ESR}) C_o \right] \times \left[ 1 + S(R_{ds} \| R_{ESR}) C_b \right]}
\tag{32}
$$

From equation (32), a part of the overall open-loop transfer function for the regulator is obtained, and the zero and poles can be found. The first pole is

$$
P_o;\quad S(R_{ds} + R_{ESR}) C_o = -1
$$
$$
\text{Therefore,}\quad f_{po} = \frac{-1}{2\pi (R_{ds} + R_{ESR}) C_o} \approx \frac{-1}{2\pi R_{ds} C_o} \quad (\text{Because } R_{ds} \gg R_{ESR})
\tag{33}
$$

The second pole is obtained from equation (32) again,

$$P_b;\quad S(R_{ds} \| R_{ESR}) C_b = -1 \tag{34}$$
$$\text{Therefore,}\quad f_{pb} = \frac{-1}{2\pi (R_{ds} \| R_{ESR}) C_b} \approx \frac{-1}{2\pi R_{ESR} C_b} \tag{35}$$

The zero is

$$Z_{ESR};\quad S R_{ESR} C_o = -1 \tag{36}$$
$$\text{Therefore,}\quad f_{Z(ESR)} = \frac{-1}{2\pi R_{ESR} C_o} \tag{37}$$

In addition, another pole exists from the input impedance of the pass element (i.e. the output impedance of the amplifier, $R_{par}$, $C_{par}$). The approximated poles and the zero are then given by

$$P_o \approx \frac{1}{2\pi R_{ds} C_o} \approx \frac{I_L}{2\pi V_A C_o} \tag{38}$$

$$P_b \approx \frac{1}{2\pi R_{ESR} C_b} \tag{39}$$

$$P_a \approx \frac{1}{2\pi R_{par} C_{par}} \tag{40}$$

$$\text{and}\quad Z_{ESR} \approx \frac{1}{2\pi R_{ESR} C_o} \tag{41}$$

Where $R_{ds} \approx \dfrac{V_A}{I_L}$, $V_A = \dfrac{1}{\lambda}$ for MOS device, $\lambda$ is the channel-length modulation parameter. Pole $P_a$ is the only one introduced at the input of the pass device, not at the output of the device. Figure 20 illustrates the typical frequency response of the LDO voltage regulator.

> **Figure 20. Frequency Response of the LDO Voltage Regulator**
> Bode-style gain (dB) versus frequency (Hz) plot. Starting flat, the response rolls off at $-1$ slope after pole $P_o$, steepens to $-2$ after pole $P_a$, flattens back to $-1$ after zero $Z_{esr}$, then steepens to $-2$ after pole $P_b$. The $0$ dB axis (unity gain) is crossed on the descending slope.

---

[← Transient Response](07-transient-response.md) | [Index](README.md) | [Next: Range of Stable ESR →](09-range-of-stable-esr.md)
