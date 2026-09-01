# Source map: Jespers & Murmann, "Systematic Design of Analog CMOS Circuits
# Using Pre-Computed Lookup Tables" (Cambridge University Press)

This skill distills the book; it does not replace it. When a distilled
reference is insufficient (derivations, second-order effects, worked numeric
examples), consult the source chapter. The PDFs are NOT bundled here for
copyright reasons. They live in the project's private knowledge base as
chapter files; agents with project-knowledge search should query them by the
topic keywords below. If your runtime instead mounts the PDFs on disk, set
GMID_BOOK_DIR and use the filenames below.

| Topic in this skill                      | Book location | Project file |
|------------------------------------------|---------------|--------------|
| Methodology motivation, FDH vs FDA, 5-step flow | Ch 1 (Introduction) | 08_0_..._Introduction.pdf |
| Transistor modeling, gm/ID vs VGS/JD, fT, EKV basics | Ch 2 (pp 1-20) | 09_0_..._Basic_Transistor_Modeling.pdf |
| Core sizing flows: IGS, given (L, gm/ID), JD flow, self-loading iteration, weak inversion | Ch 3 (pp 21-61) | 10_0_..._Basic_Sizing_Using_the_gmID_Methodology.pdf |
| Noise (STH/SFL), distortion (HD2/HD3 vs gm/ID), mismatch sizing | Ch 4 (pp 62-113) | 11_0_..._Noise_Distortion_and_Mismatch.pdf |
| Worked designs I: bias gen, high-swing mirror, LDO, LNA, charge amp, PVT corners | Ch 5 | 12_0_..._Practical_Circuit_Examples_I.pdf |
| Worked designs II: basic / folded-cascode / two-stage OTAs, SC switches | Ch 6 | 13_0_..._Practical_Circuit_Examples_II.pdf |

NOTE: the `pp_..._...` page ranges in the file 12 / file 13 names are MISLABELED
(off by ~50). file 12 holds book Ch 5 (bias/LDO/LNA/charge-amp/PVT), file 13 holds
book Ch 6 (OTAs/switches). Cite the example number (Ex 5.x / Ex 6.x), not a page.
The numeric reference designs from both chapters are distilled in
`worked-examples.md`; read it alongside `ota-recipes.md` / `biasing-and-pvt.md`.
| EKV parameter extraction (XTRACT, corners) | Appendix 1 | 14_1_..._EKV_Parameter_Extraction_Algorithm.pdf |
| LUT generation flow, lookup.m / lookupVGS.m semantics, non-monotonicity | Appendix 2 | 14_2_..._Lookup_Table_Generation_and_Usage.pdf |
| Layout-dependent effects, finger partitioning, width dependence of ratios | Appendix 3 | 14_3_..._Layout_Dependence.pdf |

Rules for agents:
- Cite chapter/section when a design decision leans on the book.
- Quote nothing beyond short fragments; paraphrase into the design rationale.
- Distillation coverage is strongest for Ch 1, Ch 3, Ch 5 (biasing + PVT, see
  biasing-and-pvt.md), and Ch 6 (OTA flows, see ota-recipes.md), all with their
  worked examples now extracted into worked-examples.md (Ex 5.1-5.11, 6.2-6.8),
  plus App 2. Ch 4 (noise/distortion/mismatch derivations) and App 1/3 are
  summarized lightly; prefer consulting the source for those. The LDO
  high-frequency (load-cap) analysis and the LNA HD2 third-order distortion
  derivations are the one thin spot — the sized results are captured but consult
  the source for the full small-signal/distortion algebra.
