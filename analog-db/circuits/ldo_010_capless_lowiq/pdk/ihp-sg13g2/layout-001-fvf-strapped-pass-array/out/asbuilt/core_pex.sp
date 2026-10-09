*********************************************************
*** NGSPICE file created by KLayout-PEX 0.3.12
*** -----------------------------------------------------
***     Extraction Engine: KPEX/2.5D
***     Technology: ihp_sg13g2
***     Date: 2026-09-05 03:46:19
*********************************************************

.subckt ldo_ihp_capless vdd vout vss
VREF vref vss dc {vref_val}
* kpex hangs every extracted ground capacitance on a substrate node VSUBS that is NOT in the
* subckt pin list; the p-substrate is at vss through the layout's own ptap ring, so tie it (a 0 V
* source rather than a rename, so the substrate branch stays visible to a reviewer). Without this
* the operating point is singular at `xdut.vsubs`.
VSUBSTIE VSUBS vss dc 0
VLP lp_brk vout dc 0
XCFF lp_brk fb cap_cmim w=c_ff_w l=c_ff_w
XCC ea_out ea_o1 cap_cmim w=c_comp_w l=c_comp_w
XCOUT vout vss cap_cmim w=c_out_w l=c_out_w m=c_out_m
XMn_1 y x1 vss vss sg13_lv_nmos L=0.5U W=5.79U AS=1.9686P AD=1.9686P PS=12.26U
+ PD=12.26U rfmode=0
XMn_2 x1 x1 vss vss sg13_lv_nmos L=0.5U W=5.79U AS=1.9686P AD=1.9686P PS=12.26U
+ PD=12.26U rfmode=0
XMn_3 ea_out ea_o1 vss vss sg13_lv_nmos L=0.5U W=2.42U AS=0.8228P AD=0.8228P
+ PS=5.52U PD=5.52U rfmode=0
XMn_4 gate nbias vss vss sg13_lv_nmos L=0.95U W=1.1U AS=0.374P AD=0.374P PS=2.88U
+ PD=2.88U rfmode=0
XMn_5 nbias nbias vss vss sg13_lv_nmos L=1U W=0.5U AS=0.17P AD=0.17P PS=1.68U
+ PD=1.68U rfmode=0
XMn_6 ea_o1 ea_n vss vss sg13_lv_nmos L=1U W=1.475U AS=0.5015P AD=0.5015P
+ PS=3.63U PD=3.63U rfmode=0
XMn_7 ea_n ea_n vss vss sg13_lv_nmos L=1U W=1.475U AS=0.5015P AD=0.5015P PS=3.63U
+ PD=3.63U rfmode=0
XMn_8 pbias nbias vss vss sg13_lv_nmos L=1U W=0.695U AS=0.2363P AD=0.2363P
+ PS=2.07U PD=2.07U rfmode=0
XMn_9 ea_n ea_n vss vss sg13_lv_nmos L=1U W=1.475U AS=0.5015P AD=0.5015P PS=3.63U
+ PD=3.63U rfmode=0
XMn_10 pbias nbias vss vss sg13_lv_nmos L=1U W=0.695U AS=0.2363P AD=0.2363P
+ PS=2.07U PD=2.07U rfmode=0
XMn_11 nbias nbias vss vss sg13_lv_nmos L=1U W=0.5U AS=0.17P AD=0.17P PS=1.68U
+ PD=1.68U rfmode=0
XMn_12 gate nbias vss vss sg13_lv_nmos L=0.95U W=1.1U AS=0.374P AD=0.374P
+ PS=2.88U PD=2.88U rfmode=0
XMn_13 ea_o1 ea_n vss vss sg13_lv_nmos L=1U W=1.475U AS=0.5015P AD=0.5015P
+ PS=3.63U PD=3.63U rfmode=0
XMn_14 ea_n fb ea_tail vdd sg13_lv_pmos L=0.5U W=4.765U AS=1.6201P AD=1.6201P
+ PS=10.21U PD=10.21U rfmode=0
XMn_15 ea_o1 vref ea_tail vdd sg13_lv_pmos L=0.5U W=4.765U AS=1.6201P AD=1.6201P
+ PS=10.21U PD=10.21U rfmode=0
XMn_16 ea_o1 vref ea_tail vdd sg13_lv_pmos L=0.5U W=4.765U AS=1.6201P AD=1.6201P
+ PS=10.21U PD=10.21U rfmode=0
XMn_17 ea_n fb ea_tail vdd sg13_lv_pmos L=0.5U W=4.765U AS=1.6201P AD=1.6201P
+ PS=10.21U PD=10.21U rfmode=0
XMn_18 pbias pbias vdd vdd sg13_lv_pmos L=1U W=10U AS=3.4P AD=3.4P PS=20.68U
+ PD=20.68U rfmode=0
XMn_19 ea_tail pbias vdd vdd sg13_lv_pmos L=1U W=10U AS=3.4P AD=3.4P PS=20.68U
+ PD=20.68U rfmode=0
XMn_20 ea_out pbias vdd vdd sg13_lv_pmos L=1U W=5.53U AS=1.8802P AD=1.8802P
+ PS=11.74U PD=11.74U rfmode=0
XMn_21 x1 ea_out vout vdd sg13_lv_pmos L=0.36U W=15.76U AS=5.3584P AD=5.3584P
+ PS=32.2U PD=32.2U rfmode=0
XMn_22 y y vdd vdd sg13_lv_pmos L=0.5U W=9.02U AS=3.0668P AD=3.0668P PS=18.72U
+ PD=18.72U rfmode=0
XMn_23 gate y vdd vdd sg13_lv_pmos L=0.5U W=9.02U AS=3.0668P AD=3.0668P PS=18.72U
+ PD=18.72U rfmode=0
XMn_24 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.85P AD=0.475P PS=5.68U
+ PD=2.88U rfmode=0
XMn_25 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_26 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_27 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_28 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_29 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_30 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_31 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_32 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_33 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_34 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_35 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_36 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_37 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_38 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_39 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_40 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_41 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_42 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_43 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_44 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_45 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_46 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_47 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_48 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_49 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_50 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_51 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_52 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_53 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_54 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_55 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_56 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_57 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_58 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_59 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_60 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_61 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_62 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_63 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_64 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_65 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_66 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_67 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_68 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_69 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_70 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_71 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_72 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_73 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_74 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_75 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_76 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_77 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_78 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_79 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_80 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_81 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_82 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_83 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_84 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_85 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_86 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_87 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_88 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_89 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_90 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_91 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_92 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_93 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_94 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_95 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_96 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_97 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_98 vout gate vdd vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.475P PS=2.88U
+ PD=2.88U rfmode=0
XMn_99 vdd gate vout vdd sg13_lv_pmos L=0.13U W=2.5U AS=0.475P AD=0.85P PS=2.88U
+ PD=5.68U rfmode=0
XRn_100 n_19 lp_brk vss rhigh w=0.5u l=42.5u m=1
XRn_101 n_30 fb vss rhigh w=0.5u l=42.5u m=1
XRn_102 n_30 n_34 vss rhigh w=0.5u l=42.5u m=1
XRn_103 n_19 n_35 vss rhigh w=0.5u l=42.5u m=1
XRn_104 n_20 n_35 vss rhigh w=0.5u l=42.5u m=1
XRn_105 n_31 n_34 vss rhigh w=0.5u l=42.5u m=1
XRn_106 n_31 n_36 vss rhigh w=0.5u l=42.5u m=1
XRn_107 n_20 n_37 vss rhigh w=0.5u l=42.5u m=1
XRn_108 n_21 n_37 vss rhigh w=0.5u l=42.5u m=1
XRn_109 n_32 n_36 vss rhigh w=0.5u l=42.5u m=1
XRn_110 n_32 n_38 vss rhigh w=0.5u l=42.5u m=1
XRn_111 n_21 n_39 vss rhigh w=0.5u l=42.5u m=1
XRn_112 n_22 n_39 vss rhigh w=0.5u l=42.5u m=1
XRn_113 n_33 n_38 vss rhigh w=0.5u l=42.5u m=1
XRn_114 n_33 vss vss rhigh w=0.5u l=42.5u m=1
XRn_115 n_22 fb vss rhigh w=0.5u l=42.5u m=1
XRn_116 vdd n_40 vss rhigh w=0.5u l=27.7u m=1
XRn_117 n_28 n_40 vss rhigh w=0.5u l=27.7u m=1
XRn_118 n_28 n_41 vss rhigh w=0.5u l=27.7u m=1
XRn_119 n_29 n_41 vss rhigh w=0.5u l=27.7u m=1
XRn_120 n_29 nbias vss rhigh w=0.5u l=27.7u m=1
Cext_1 n_19 n_20 29.1208a
Cext_2 n_19 n_30 84.7091a
Cext_3 n_19 n_31 0.382346a
Cext_4 n_19 ea_o1 46.5979a
Cext_5 n_19 fb 50.6922a
Cext_6 n_19 lp_brk 3.71789a
Cext_7 n_19 vss 16.0676a
Cext_8 n_19 VSUBS 895.995a
Cext_9 n_20 n_21 29.1208a
Cext_10 n_20 n_30 0.580868a
Cext_11 n_20 n_31 84.7091a
Cext_12 n_20 n_32 0.580868a
Cext_13 n_20 ea_o1 29.4074a
Cext_14 n_20 fb 0.10108a
Cext_15 n_20 lp_brk 54.5808a
Cext_16 n_20 VSUBS 884.846a
Cext_17 n_21 n_22 29.1208a
Cext_18 n_21 n_31 0.580868a
Cext_19 n_21 n_32 85.6526a
Cext_20 n_21 n_33 0.580868a
Cext_21 n_21 ea_o1 30.2717a
Cext_22 n_21 lp_brk 0.103114a
Cext_23 n_21 VSUBS 884.846a
Cext_24 n_22 n_32 0.580868a
Cext_25 n_22 n_33 85.6526a
Cext_26 n_22 ea_o1 30.2717a
Cext_27 n_22 vss 11.5305a
Cext_28 n_22 VSUBS 899.063a
Cext_29 n_28 n_29 9.15004a
Cext_30 n_28 ea_o1 8.77427a
Cext_31 n_28 vdd 12.4696a
Cext_32 n_28 vss 0.347102a
Cext_33 n_28 VSUBS 409.836a
Cext_34 n_29 ea_o1 8.77427a
Cext_35 n_29 vdd 0.347102a
Cext_36 n_29 vss 12.7206a
Cext_37 n_29 VSUBS 409.836a
Cext_38 n_30 n_31 3.1728a
Cext_39 n_30 ea_o1 11.3256a
Cext_40 n_30 fb 24.5464a
Cext_41 n_30 lp_brk 3.78971a
Cext_42 n_30 vss 0.822662a
Cext_43 n_30 VSUBS 508.909a
Cext_44 n_31 n_32 5.96012a
Cext_45 n_31 ea_o1 11.1554a
Cext_46 n_31 lp_brk 15.728a
Cext_47 n_31 VSUBS 511.398a
Cext_48 n_32 n_33 5.96012a
Cext_49 n_32 ea_o1 11.1554a
Cext_50 n_32 VSUBS 517.566a
Cext_51 n_33 ea_o1 11.1554a
Cext_52 n_33 vss 4.95894a
Cext_53 n_33 VSUBS 517.65a
Cext_54 n_34 n_35 63.2751a
Cext_55 n_34 n_36 29.9581a
Cext_56 n_34 fb 21.6148a
Cext_57 n_34 lp_brk 60.7243a
Cext_58 n_34 vss 13.4273a
Cext_59 n_34 VSUBS 766.356a
Cext_60 n_35 n_37 7.36983a
Cext_61 n_35 fb 1.50969a
Cext_62 n_35 lp_brk 28.7125a
Cext_63 n_35 vss 15.9257a
Cext_64 n_35 VSUBS 552.606a
Cext_65 n_36 n_37 65.0349a
Cext_66 n_36 n_38 29.9581a
Cext_67 n_36 lp_brk 0.165868a
Cext_68 n_36 vss 13.7644a
Cext_69 n_36 VSUBS 781.407a
Cext_70 n_37 n_39 7.36983a
Cext_71 n_37 lp_brk 0.603941a
Cext_72 n_37 vss 15.9257a
Cext_73 n_37 VSUBS 550.728a
Cext_74 n_38 n_39 65.0349a
Cext_75 n_38 fb 0.163803a
Cext_76 n_38 vss 35.0313a
Cext_77 n_38 VSUBS 787.047a
Cext_78 n_39 vss 17.3131a
Cext_79 n_39 VSUBS 552.606a
Cext_80 n_40 n_41 9.15004a
Cext_81 n_40 nbias 0.316697a
Cext_82 n_40 vdd 37.8484a
Cext_83 n_40 vss 9.90782a
Cext_84 n_40 VSUBS 409.836a
Cext_85 n_41 nbias 12.003a
Cext_86 n_41 vdd 0.8214a
Cext_87 n_41 vss 0.131092a
Cext_88 n_41 VSUBS 409.836a
Cext_89 ea_n ea_o1 2.97933f
Cext_90 ea_n ea_out 423.674a
Cext_91 ea_n ea_tail 1.37462f
Cext_92 ea_n fb 763.857a
Cext_93 ea_n lp_brk 2.29882f
Cext_94 ea_n nbias 54.4536a
Cext_95 ea_n pbias 0.65902a
Cext_96 ea_n vdd 188.49a
Cext_97 ea_n vref 58.6267a
Cext_98 ea_n vss 988.583a
Cext_99 ea_o1 ea_out 3.94649f
Cext_100 ea_o1 ea_tail 2.78235f
Cext_101 ea_o1 fb 4.085f
Cext_102 ea_o1 lp_brk 5.21605f
Cext_103 ea_o1 nbias 228.182a
Cext_104 ea_o1 vdd 165.553a
Cext_105 ea_o1 vref 757.059a
Cext_106 ea_o1 vss 3.71251f
Cext_107 ea_out ea_tail 2.28435f
Cext_108 ea_out fb 112.871a
Cext_109 ea_out gate 97.8497a
Cext_110 ea_out lp_brk 449.728a
Cext_111 ea_out nbias 1.02255f
Cext_112 ea_out pbias 378.943a
Cext_113 ea_out vdd 495.219a
Cext_114 ea_out vout 383.084a
Cext_115 ea_out vref 118.68a
Cext_116 ea_out vss 698.71a
Cext_117 ea_out x1 600.541a
Cext_118 ea_out y 90.8631a
Cext_119 ea_tail fb 898.24a
Cext_120 ea_tail gate 2.40167a
Cext_121 ea_tail lp_brk 1.28779a
Cext_122 ea_tail nbias 2.36915f
Cext_123 ea_tail pbias 668.179a
Cext_124 ea_tail vdd 743.102a
Cext_125 ea_tail vref 966.022a
Cext_126 ea_tail vss 0.893003a
Cext_127 fb lp_brk 4.23462f
Cext_128 fb nbias 88.3695a
Cext_129 fb vdd 352.791a
Cext_130 fb vref 417.865a
Cext_131 fb vss 1.32951f
Cext_132 gate lp_brk 57.1068a
Cext_133 gate nbias 276.102a
Cext_134 gate pbias 145.728a
Cext_135 gate vdd 5.13329f
Cext_136 gate vout 8.91105f
Cext_137 gate vss 317.513a
Cext_138 gate x1 69.616a
Cext_139 gate y 480.692a
Cext_140 lp_brk nbias 569.582a
Cext_141 lp_brk pbias 61.3904a
Cext_142 lp_brk vdd 31.0335a
Cext_143 lp_brk vout 109.119a
Cext_144 lp_brk vref 386.983a
Cext_145 lp_brk vss 1.18596f
Cext_146 lp_brk x1 90.1098a
Cext_147 lp_brk y 31.2899a
Cext_148 nbias pbias 5.30401f
Cext_149 nbias vdd 443.008a
Cext_150 nbias vout 26.0896a
Cext_151 nbias vref 52.7318a
Cext_152 nbias vss 1.72649f
Cext_153 nbias x1 80.8895a
Cext_154 nbias y 30.1141a
Cext_155 pbias vdd 1.81826f
Cext_156 pbias vout 177.124a
Cext_157 pbias vss 230.602a
Cext_158 pbias x1 1.03958f
Cext_159 pbias y 463.191a
Cext_160 vdd vout 24.8004f
Cext_161 vdd vref 183.919a
Cext_162 vdd vss 4.78508f
Cext_163 vdd x1 255.692a
Cext_164 vdd y 1.37935f
Cext_165 vout vss 19.1557f
Cext_166 vout x1 1.61853f
Cext_167 vout y 1.22001f
Cext_168 vref vss 2.32628a
Cext_169 vss x1 949.688a
Cext_170 vss y 395.588a
Cext_171 VSUBS ea_n 8.85551f
Cext_172 VSUBS ea_o1 40.0411f
Cext_173 VSUBS ea_out 15.5245f
Cext_174 VSUBS ea_tail 5.93314f
Cext_175 VSUBS fb 19.522f
Cext_176 VSUBS gate 29.0038f
Cext_177 VSUBS lp_brk 23.0437f
Cext_178 VSUBS nbias 18.07f
Cext_179 VSUBS pbias 11.901f
Cext_180 VSUBS vdd 122.433f
Cext_181 VSUBS vout 52.7724f
Cext_182 VSUBS vref 3.03809f
Cext_183 VSUBS vss 305.951f
Cext_184 VSUBS x1 5.70387f
Cext_185 VSUBS y 6.56155f
Cext_186 x1 y 968.723a
.ENDS ldo_ihp_capless
