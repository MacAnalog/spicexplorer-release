* schematic subckt of record
.subckt lpf_core vinp vinn vout_1 vout_2 vdd vss ibias
xm1a n1 vinp vdd vdd sg13_hv_pmos w=16u l=10u ng=2 m=1
xm1b n2 vinn vdd vdd sg13_hv_pmos w=16u l=10u ng=2 m=1
xc1 vout_1 vout_2 cap_cmim w=40u l=40u m=2
xr1 n1 n1 vss vss sg13_hv_nmos w=4u l=15u
.ends lpf_core
