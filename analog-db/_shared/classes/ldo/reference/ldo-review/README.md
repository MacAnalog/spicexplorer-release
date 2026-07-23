# Technical Review of Low Dropout Voltage Regulator Operation and Performance

**Author:** Bang S. Lee
**Publisher:** Texas Instruments, Mixed Signal Products
**Document number:** SLVA072
**Date:** August 1999

## Abstract

This application report provides a technical review of low dropout (LDO) voltage regulators, and describes fundamental concepts including dropout voltage, quiescent current, and topologies. The report also includes detailed discussions of load/line regulation, efficiency, frequency response, range of stable ESR, and accuracy of LDO voltage regulators.

## About this conversion

This is a faithful Markdown transcription of the original PDF, split into one file per top-level section and organized through this index. Equations are reproduced in LaTeX notation. Figures from the original are images and cannot be reproduced as text; each figure appears as a captioned placeholder with a short description of what the original figure shows (no content has been invented). Page numbers refer to the original document.

## Contents

| # | Section | File |
|---|---------|------|
| 1 | Dropout Voltage | [01-dropout-voltage.md](01-dropout-voltage.md) |
| 2 | Quiescent Current or Ground Current | [02-quiescent-current.md](02-quiescent-current.md) |
| 3 | LDO Topologies | [03-ldo-topologies.md](03-ldo-topologies.md) |
| 4 | Efficiency | [04-efficiency.md](04-efficiency.md) |
| 5 | Load Regulation | [05-load-regulation.md](05-load-regulation.md) |
| 6 | Line Regulation | [06-line-regulation.md](06-line-regulation.md) |
| 7 | Transient Response | [07-transient-response.md](07-transient-response.md) |
| 8 | Frequency Response | [08-frequency-response.md](08-frequency-response.md) |
| 9 | Range of Stable ESR (Tunnel of Death) | [09-range-of-stable-esr.md](09-range-of-stable-esr.md) |
| 10 | Accuracy | [10-accuracy.md](10-accuracy.md) |
| 11 | References | [11-references.md](11-references.md) |

## List of Figures

1. LDO Voltage Regulator — §1
2. Series Pass Element I-V Characteristic and LDO Equivalent Circuits — §1
3. NMOS Operation With LDO in Saturation Region — §1
4. NMOS Operation With LDO in Dropout Region — §1
5. Typical Input/Output Voltage Characteristics of a Linear Regulator — §1
6. Dropout Region of TI TPS76333 (3.3-V LDO) — §1.1
7. I-V Characteristic of Bipolar Transistors — §2
8. I-V Characteristic of MOS Transistors — §2
9. Quiescent Current and Output Current — §2.1
10. Linear Regulator — §3
11. Pass Element Structures — §3
12. PMOS Voltage Regulator — §5
13. Load Transient Response of TPS76350 — §5.1
14. TPS76350 Output Voltage With Respect to Output Current — §5.1
15. Line Transient Response of TPS76333 — §6.1
16. TPS76333 Output Voltage With Respect to Input Voltage — §6.1
17. 1.2-V, 100-mA LDO Voltage Regulator With Output Capacitor of 4.7 µF — §7.1
18. Transient Response of Step Load Change of 1.2-V, 100-mA LDO Voltage Regulator With an Output Capacitor Co=4.7 µF — §7.1
19. AC Model of a Linear Regulator — §8
20. Frequency Response of the LDO Voltage Regulator — §8
21. LDO Frequency Response Without Compensation — §9
22. LDO Frequency Response With External Compensation — §9
23. Unstable Frequency Response of LDO With too High ESR — §9
24. Unstable Frequency Response of LDO With too Low ESR — §9
25. Range of Stable ESR Values — §9.1
26. LDO With Reference Voltage Drift — §10.1
27. LDO With Error Amplifier Voltage Drift — §10.2
28. LDO With Sampling Resistors — §10.3
29. LDO Regulator — §10.4

## List of Tables

1. Comparison of Pass Element Structures — §3.1

---

*Original copyright © 1999, Texas Instruments Incorporated. This transcription reproduces the technical content of TI application report SLVA072 for reference purposes.*
