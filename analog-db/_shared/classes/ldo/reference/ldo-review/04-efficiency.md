# 4. Efficiency

[← LDO Topologies](03-ldo-topologies.md) | [Index](README.md) | [Next: Load Regulation →](05-load-regulation.md)

---

The efficiency of a LDO regulator is limited by the quiescent current and input/output voltage as follows:

$$\text{Efficiency} = \frac{I_O V_O}{(I_O + I_q) V_I} \times 100 \tag{13}$$

To have a high efficiency LDO regulator, drop out voltage and quiescent current must be minimized. In addition, the voltage difference between input and output must be minimized since the power dissipation of LDO regulators accounts for the efficiency ($\text{Power Dissipation} = (V_I - V_O) I_O$). The input/output voltage difference is an intrinsic factor in determining the efficiency regardless of the load condition.

## 4.1 Application Implications—An Example

What is the efficiency of the TPS76333 3.3-V LDO regulator with the following operating conditions?

- Input voltage range is 3.8 V to 4.5 V.
- Output current range is 100 mA to 150 mA.
- Maximum quiescent current is 140 µA.

$$\text{Efficiency} = \frac{150\ mA \times 3.3}{(150\ mA + 140\ \mu A)\, 4.5\ V} \times 100 = 73.2\% \tag{14}$$

---

[← LDO Topologies](03-ldo-topologies.md) | [Index](README.md) | [Next: Load Regulation →](05-load-regulation.md)
