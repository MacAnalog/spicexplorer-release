# 9. Range of Stable ESR (Tunnel of Death)

[← Frequency Response](08-frequency-response.md) | [Index](README.md) | [Next: Accuracy →](10-accuracy.md)

---

An LDO regulator would require an output capacitor with an output equivalent series resistor (ESR) to stabilize the control loop. An LDO has two poles that can cause oscillations as shown in Figure 21 if it is not compensated. It is obvious that the linear regulator is unstable because the phase shift at unity gain frequency (UGF) is −180° due to the effects of two poles ($P_O$, $P_a$) at low frequencies. To make the regulator stable, a zero must be added, which will cancel out the phase effect of one of two poles.

> **Figure 21. LDO Frequency Response Without Compensation**
> Gain (dB) versus frequency (Hz). The response rolls off at $-1$ after pole $P_o$, then $-2$ after pole $P_a$, crossing unity gain (UGF) on the $-2$ slope — indicating instability (−180° phase shift at UGF).

The equivalent series resistance of the output capacitor (ESR) or a compensated series resistor (CSR) is used for the zero. Figure 22 shows how the ESR (or CSR) zero stabilizes the control loop. The zero produced by the ESR locates before the UGF so that the phase shift at $UGF_1$ will be around −90° (i.e., two poles −zero = -180°+90° = -90°). Thus, the linear regulator becomes stable. The phase shift of the control loop at UGF should always be less than −180° for system stability.

> **Figure 22. LDO Frequency Response With External Compensation**
> Gain (dB) versus frequency (Hz). The response rolls off at $-1$ after $P_o$, $-2$ after $P_a$, then the ESR zero $Z_{esr}$ returns the slope to $-1$ before unity gain, moving the crossing to $UGF_1$ on a $-1$ slope; pole $P_b$ (slope $-2$) occurs after. This stabilizes the loop by canceling one pole's phase effect.

The ESR value should be maintained in the range that determines the loop stability. For most LDO regulators, minimum and maximum ESR values exist. Figures 23 and 24 show the unstable loop responses of an LDO regulator even though a zero is added. From equation (39) and (41), the zero $Z_{esr}$ and the pole $P_b$ are determined by the equivalent series resistor (ESR). When the ESR changes, $Z_{esr}$ and $P_b$ are shifted upward/downward and the loop stability is affected.

> **Figure 23. Unstable Frequency Response of LDO With too High ESR**
> Gain (dB) versus frequency. With too high an ESR, the zero $Z_{esr}$ moves to low frequency (right after $P_a$), so the response goes $-1$ ($P_o$), $-2$ ($P_a$), $-1$ ($Z_{esr}$), then $-2$ ($P_b$). The broken line marks the **Stable Region of ESR**; the actual crossing gives −180° phase shift at unity gain — unstable.

Figure 23 illustrates the unstable frequency response of an LDO when too high an ESR is added, and Figure 24 illustrates the LDO frequency response when too low an ESR is used. For both cases, the total phase shift at unity gain frequency is −180°, resulting in system instability. The broken line in Figures 23 and 24 shows the stable range of $Z_{esr}$.

> **Figure 24. Unstable Frequency Response of LDO With too Low ESR**
> Gain (dB) versus frequency. With too low an ESR, the zero $Z_{esr}$ moves to high frequency (past unity gain): the response goes $-1$ ($P_o$), $-2$ ($P_a$), crossing unity gain on the $-2$ slope, with $Z_{esr}$ and $P_b$ occurring below 0 dB. The broken line marks the **Stable Region of ESR**; the crossing gives −180° phase shift — unstable.

## 9.1 Application Implications

Since ESR can cause instability, LDO manufacturers typically provide a graph showing the stable range of ESR values. Figure 25 shows a typical range of ESR values with respect to the output currents. This curve is called tunnel of death. The curve shows that the ESR must be between 0.2 Ω and 9 Ω. Solid tantalum electrolytic, aluminum electrolytic, and multilayer ceramic capacitors are all suitable, provided they meet the ESR requirements.

> **Figure 25. Range of Stable ESR Values**
> Log-scale plot of output capacitor ESR (Ω, 0.01 to 100) versus output current $I_O$ (mA, 0 to 250) for $C_O = 4.7\ \mu F$. A central **Stable Region** (roughly 0.2 Ω to 9 Ω, narrowing at low current) is bounded above and below by **Region of Instability** — the "tunnel of death."

---

[← Frequency Response](08-frequency-response.md) | [Index](README.md) | [Next: Accuracy →](10-accuracy.md)
