v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {drv_001_pam4_sige_dac} -40 -200 0 0 0.4 0.4 {}
C {devices/capa_np.sym} 0 0 0 0 {name=CDEGL0 value="\{x_dut_cdeg_ff*1f\}"}
C {devices/capa_np.sym} 260 0 0 0 {name=CDEGM0 value="\{x_dut_cdeg_ff*1f\}"}
C {devices/capa_np.sym} 515 0 0 0 {name=CDEGM1 value="\{x_dut_cdeg_ff*1f\}"}
C {devices/vccs.sym} 775 0 0 0 {name=GTAILL0 value=1m}
C {devices/vccs.sym} 1015 0 0 0 {name=GTAILM0 value=1m}
C {devices/vccs.sym} 1255 0 0 0 {name=GTAILM1 value=1m}
C {devices/res_np.sym} 0 240 0 0 {name=RBLSBN value="\{x_dut_rb\}"}
C {devices/res_np.sym} 260 240 0 0 {name=RBLSBP value="\{x_dut_rb\}"}
C {devices/res_np.sym} 515 240 0 0 {name=RBMSBN value="\{x_dut_rb\}"}
C {devices/res_np.sym} 775 240 0 0 {name=RBMSBP value="\{x_dut_rb\}"}
C {devices/res_np.sym} 1015 240 0 0 {name=RCN value="\{x_dut_rc\}"}
C {devices/res_np.sym} 1255 240 0 0 {name=RCP value="\{x_dut_rc\}"}
C {devices/res_np.sym} 0 480 0 0 {name=RE1L0 value="\{x_dut_re\}"}
C {devices/res_np.sym} 260 480 0 0 {name=RE1M0 value="\{x_dut_re\}"}
C {devices/res_np.sym} 515 480 0 0 {name=RE1M1 value="\{x_dut_re\}"}
C {devices/res_np.sym} 775 480 0 0 {name=RE2L0 value="\{x_dut_re\}"}
C {devices/res_np.sym} 1015 480 0 0 {name=RE2M0 value="\{x_dut_re\}"}
C {devices/res_np.sym} 1255 480 0 0 {name=RE2M1 value="\{x_dut_re\}"}
C {sg13g2_pr/npn13G2.sym} 0 720 0 0 {name=Q1L0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 260 720 0 0 {name=Q1M0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 515 720 0 0 {name=Q1M1 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 775 720 0 0 {name=Q2L0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 1015 720 0 0 {name=Q2M0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 1255 720 0 0 {name=Q2M1 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 0 960 0 0 {name=Q3L0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 260 960 0 0 {name=Q3M0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 515 960 0 0 {name=Q3M1 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 775 960 0 0 {name=Q4L0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 1015 960 0 0 {name=Q4M0 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
C {sg13g2_pr/npn13G2.sym} 1255 960 0 0 {name=Q4M1 model=npn13G2 spiceprefix=X Nx=x_dut_nx}
N -60 -60 -60 780 {}
N -50 150 -50 720 {}
N -50 840 -50 960 {}
N -40 660 -40 1020 {}
N 0 -90 0 -30 {}
N 0 30 0 90 {}
N 0 120 0 210 {}
N 0 270 0 300 {}
N 0 420 0 450 {}
N 0 510 0 570 {}
N 20 630 20 690 {}
N 20 750 20 780 {}
N 20 870 20 930 {}
N 20 990 20 1020 {}
N 210 600 210 720 {}
N 210 840 210 960 {}
N 220 660 220 1020 {}
N 260 -90 260 -30 {}
N 260 30 260 90 {}
N 260 150 260 210 {}
N 260 270 260 300 {}
N 260 390 260 450 {}
N 260 510 260 570 {}
N 280 630 280 690 {}
N 280 750 280 780 {}
N 280 900 280 930 {}
N 280 990 280 1020 {}
N 340 420 340 780 {}
N 465 150 465 720 {}
N 465 840 465 960 {}
N 475 660 475 1020 {}
N 515 -90 515 -30 {}
N 515 30 515 90 {}
N 515 270 515 300 {}
N 515 390 515 450 {}
N 515 510 515 570 {}
N 535 630 535 690 {}
N 535 750 535 780 {}
N 535 900 535 930 {}
N 535 990 535 1020 {}
N 595 420 595 780 {}
N 725 120 725 720 {}
N 725 840 725 960 {}
N 735 20 735 1100 {}
N 775 -90 775 -30 {}
N 775 30 775 90 {}
N 775 150 775 210 {}
N 775 270 775 300 {}
N 775 390 775 450 {}
N 775 510 775 570 {}
N 795 630 795 690 {}
N 795 750 795 780 {}
N 795 900 795 930 {}
N 795 990 795 1020 {}
N 815 180 815 900 {}
N 855 660 855 1020 {}
N 915 420 915 780 {}
N 965 600 965 720 {}
N 965 840 965 960 {}
N 975 20 975 1100 {}
N 1015 -90 1015 -30 {}
N 1015 30 1015 90 {}
N 1015 180 1015 210 {}
N 1015 270 1015 330 {}
N 1015 390 1015 450 {}
N 1015 510 1015 570 {}
N 1035 630 1035 690 {}
N 1035 750 1035 780 {}
N 1035 900 1035 930 {}
N 1035 990 1035 1020 {}
N 1055 -60 1055 540 {}
N 1095 660 1095 1020 {}
N 1155 420 1155 780 {}
N 1205 600 1205 720 {}
N 1205 840 1205 960 {}
N 1215 20 1215 1100 {}
N 1255 -90 1255 -30 {}
N 1255 30 1255 90 {}
N 1255 180 1255 210 {}
N 1255 270 1255 330 {}
N 1255 420 1255 450 {}
N 1255 510 1255 540 {}
N 1275 630 1275 690 {}
N 1275 750 1275 780 {}
N 1275 900 1275 930 {}
N 1275 990 1275 1020 {}
N 1335 660 1335 1020 {}
N 1395 420 1395 780 {}
N 1575 60 1575 420 {}
N -110 -140 1515 -140 {}
N -60 -60 0 -60 {}
N 1055 -60 1255 -60 {}
N 705 -20 735 -20 {}
N 945 -20 1215 -20 {}
N 515 60 1575 60 {}
N 0 120 725 120 {}
N -50 150 260 150 {}
N 465 150 775 150 {}
N 815 180 1015 180 {}
N 0 300 775 300 {}
N -60 420 0 420 {}
N 260 420 340 420 {}
N 515 420 595 420 {}
N 775 420 915 420 {}
N 1015 420 1155 420 {}
N 1255 420 1575 420 {}
N 1055 540 1255 540 {}
N 210 600 465 600 {}
N 965 600 1205 600 {}
N -40 660 20 660 {}
N 220 660 280 660 {}
N 475 660 535 660 {}
N 795 660 855 660 {}
N 1035 660 1095 660 {}
N 1275 660 1335 660 {}
N -50 720 -20 720 {}
N 210 720 240 720 {}
N 465 720 495 720 {}
N 725 720 755 720 {}
N 965 720 995 720 {}
N 1205 720 1235 720 {}
N -60 780 20 780 {}
N 280 780 340 780 {}
N 535 780 595 780 {}
N 795 780 915 780 {}
N 1035 780 1155 780 {}
N 1275 780 1395 780 {}
N -50 840 1205 840 {}
N 20 900 535 900 {}
N 795 900 1275 900 {}
N -50 960 -20 960 {}
N 210 960 240 960 {}
N 465 960 495 960 {}
N 725 960 755 960 {}
N 965 960 995 960 {}
N 1205 960 1235 960 {}
N -40 1020 20 1020 {}
N 220 1020 280 1020 {}
N 475 1020 535 1020 {}
N 795 1020 855 1020 {}
N 1035 1020 1095 1020 {}
N 1275 1020 1335 1020 {}
N -110 1100 1515 1100 {}
C {devices/lab_wire.sym} -110 1100 0 0 {name=l0 lab=0}
C {devices/lab_wire.sym} 20 630 0 1 {name=l1 lab=c1L0}
C {devices/lab_wire.sym} 280 630 0 1 {name=l2 lab=c1M0}
C {devices/lab_wire.sym} 535 630 0 1 {name=l3 lab=c1M1}
C {devices/lab_wire.sym} 795 630 0 1 {name=l4 lab=c2L0}
C {devices/lab_wire.sym} 1035 630 0 1 {name=l5 lab=c2M0}
C {devices/lab_wire.sym} 1275 630 0 1 {name=l6 lab=c2M1}
C {devices/lab_wire.sym} 0 -90 0 1 {name=l7 lab=e1L0}
C {devices/lab_wire.sym} 260 -90 0 1 {name=l8 lab=e1M0}
C {devices/lab_wire.sym} 260 390 0 1 {name=l9 lab=e1M0}
C {devices/lab_wire.sym} 515 -90 0 1 {name=l10 lab=e1M1}
C {devices/lab_wire.sym} 515 390 0 1 {name=l11 lab=e1M1}
C {devices/lab_wire.sym} 0 90 2 0 {name=l12 lab=e2L0}
C {devices/lab_wire.sym} 775 390 0 1 {name=l13 lab=e2L0}
C {devices/lab_wire.sym} 260 90 2 0 {name=l14 lab=e2M0}
C {devices/lab_wire.sym} 1015 390 0 1 {name=l15 lab=e2M0}
C {devices/lab_wire.sym} 515 90 2 0 {name=l16 lab=e2M1}
C {devices/lab_wire.sym} 515 210 0 0 {name=l17 lab=msbn}
C {devices/lab_wire.sym} 20 870 0 1 {name=l18 lab=outp}
C {devices/lab_wire.sym} 0 570 2 0 {name=l19 lab=tlsb0}
C {devices/lab_wire.sym} 775 -90 0 1 {name=l20 lab=tlsb0}
C {devices/lab_wire.sym} 775 570 2 0 {name=l21 lab=tlsb0}
C {devices/lab_wire.sym} 260 570 2 0 {name=l22 lab=tmsb0}
C {devices/lab_wire.sym} 1015 -90 0 1 {name=l23 lab=tmsb0}
C {devices/lab_wire.sym} 1015 570 2 0 {name=l24 lab=tmsb0}
C {devices/lab_wire.sym} 515 570 2 0 {name=l25 lab=tmsb1}
C {devices/lab_wire.sym} 1255 -90 0 1 {name=l26 lab=tmsb1}
C {devices/lab_wire.sym} 775 90 2 0 {name=l27 lab=0}
C {devices/lab_wire.sym} 1015 90 2 0 {name=l28 lab=0}
C {devices/lab_wire.sym} 1255 90 2 0 {name=l29 lab=0}
C {devices/lab_wire.sym} 20 720 0 0 {name=l30 lab=0}
C {devices/lab_wire.sym} 280 720 0 0 {name=l31 lab=0}
C {devices/lab_wire.sym} 535 720 0 0 {name=l32 lab=0}
C {devices/lab_wire.sym} 795 720 0 0 {name=l33 lab=0}
C {devices/lab_wire.sym} 1035 720 0 0 {name=l34 lab=0}
C {devices/lab_wire.sym} 1275 720 0 0 {name=l35 lab=0}
C {devices/lab_wire.sym} 20 960 0 0 {name=l36 lab=0}
C {devices/lab_wire.sym} 280 960 0 0 {name=l37 lab=0}
C {devices/lab_wire.sym} 535 960 0 0 {name=l38 lab=0}
C {devices/lab_wire.sym} 795 960 0 0 {name=l39 lab=0}
C {devices/lab_wire.sym} 1035 960 0 0 {name=l40 lab=0}
C {devices/lab_wire.sym} 1275 960 0 0 {name=l41 lab=0}
C {devices/lab_wire.sym} 1015 330 2 0 {name=l42 lab=vcc}
C {devices/lab_wire.sym} 1255 330 2 0 {name=l43 lab=vcc}
C {devices/iopin.sym} 705 -20 0 0 {name=p0 lab=blsb}
C {devices/iopin.sym} 945 -20 0 0 {name=p1 lab=bmsb}
C {devices/iopin.sym} 725 720 0 0 {name=p2 lab=lsbn}
C {devices/iopin.sym} -50 720 0 0 {name=p3 lab=lsbp}
C {devices/iopin.sym} 965 720 0 0 {name=p4 lab=msbn}
C {devices/iopin.sym} 210 720 0 0 {name=p5 lab=msbp}
C {devices/iopin.sym} 795 900 0 0 {name=p6 lab=outn}
C {devices/iopin.sym} 1255 180 0 0 {name=p7 lab=outp}
C {devices/iopin.sym} 0 300 0 0 {name=p8 lab=vcmb}
C {devices/iopin.sym} -110 -140 0 0 {name=p9 lab=vcc}
C {devices/iopin.sym} -50 960 0 0 {name=p10 lab=vcasc}
