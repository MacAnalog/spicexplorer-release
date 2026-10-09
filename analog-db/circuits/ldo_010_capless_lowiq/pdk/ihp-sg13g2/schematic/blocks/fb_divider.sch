v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {fb_divider} -40 -200 0 0 0.4 0.4 {}
C {sg13g2_pr/rhigh.sym} 240 0 0 0 {name=R1_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 480 0 0 0 {name=R1_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 720 0 0 0 {name=R1_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 960 0 0 0 {name=R1_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 0 240 0 0 {name=R1_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 240 240 0 0 {name=R1_6 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 480 240 0 0 {name=R1_7 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 720 240 0 0 {name=R1_8 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 960 240 0 0 {name=R2_1 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 0 480 0 0 {name=R2_2 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 240 480 0 0 {name=R2_3 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 480 480 0 0 {name=R2_4 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 720 480 0 0 {name=R2_5 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 960 480 0 0 {name=R2_6 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 0 720 0 0 {name=R2_7 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/rhigh.sym} 240 720 0 0 {name=R2_8 model=rhigh spiceprefix=X body=vss w=r_w l="\{r_fb_l/8\}"}
C {sg13g2_pr/cap_cmim.sym} 0 0 0 0 {name=CFF model=cap_cmim spiceprefix=X w=c_ff_w l=c_ff_w}
N 0 -90 0 -30 {}
N 0 30 0 90 {}
N 0 150 0 210 {}
N 0 270 0 330 {}
N 0 390 0 450 {}
N 0 510 0 570 {}
N 0 630 0 690 {}
N 0 750 0 810 {}
N 240 -90 240 -30 {}
N 240 30 240 90 {}
N 240 150 240 210 {}
N 240 270 240 330 {}
N 240 390 240 450 {}
N 240 510 240 570 {}
N 240 750 240 810 {}
N 480 -90 480 -30 {}
N 480 30 480 90 {}
N 480 150 480 210 {}
N 480 270 480 330 {}
N 480 390 480 450 {}
N 480 510 480 570 {}
N 720 -90 720 -30 {}
N 720 30 720 90 {}
N 720 150 720 210 {}
N 720 270 720 330 {}
N 720 390 720 450 {}
N 720 510 720 570 {}
N 960 -90 960 -30 {}
N 960 30 960 90 {}
N 960 150 960 210 {}
N 960 270 960 330 {}
N 960 390 960 450 {}
N 960 510 960 570 {}
N 0 660 240 660 {}
N -60 860 1160 860 {}
C {devices/lab_wire.sym} -60 860 0 0 {name=l0 lab=vss}
C {devices/lab_wire.sym} 0 90 2 0 {name=l1 lab=fb}
C {devices/lab_wire.sym} 720 150 0 1 {name=l2 lab=fb}
C {devices/lab_wire.sym} 960 330 2 0 {name=l3 lab=fb}
C {devices/lab_wire.sym} 0 -90 0 1 {name=l4 lab=lp_brk}
C {devices/lab_wire.sym} 240 90 2 0 {name=l5 lab=lp_brk}
C {devices/lab_wire.sym} 240 -90 0 1 {name=l6 lab=n_r1_1}
C {devices/lab_wire.sym} 480 90 2 0 {name=l7 lab=n_r1_1}
C {devices/lab_wire.sym} 480 -90 0 1 {name=l8 lab=n_r1_2}
C {devices/lab_wire.sym} 720 90 2 0 {name=l9 lab=n_r1_2}
C {devices/lab_wire.sym} 720 -90 0 1 {name=l10 lab=n_r1_3}
C {devices/lab_wire.sym} 960 90 2 0 {name=l11 lab=n_r1_3}
C {devices/lab_wire.sym} 0 330 2 0 {name=l12 lab=n_r1_4}
C {devices/lab_wire.sym} 960 -90 0 1 {name=l13 lab=n_r1_4}
C {devices/lab_wire.sym} 0 150 0 1 {name=l14 lab=n_r1_5}
C {devices/lab_wire.sym} 240 330 2 0 {name=l15 lab=n_r1_5}
C {devices/lab_wire.sym} 240 150 0 1 {name=l16 lab=n_r1_6}
C {devices/lab_wire.sym} 480 330 2 0 {name=l17 lab=n_r1_6}
C {devices/lab_wire.sym} 480 150 0 1 {name=l18 lab=n_r1_7}
C {devices/lab_wire.sym} 720 330 2 0 {name=l19 lab=n_r1_7}
C {devices/lab_wire.sym} 0 570 2 0 {name=l20 lab=n_r2_1}
C {devices/lab_wire.sym} 960 150 0 1 {name=l21 lab=n_r2_1}
C {devices/lab_wire.sym} 0 390 0 1 {name=l22 lab=n_r2_2}
C {devices/lab_wire.sym} 240 570 2 0 {name=l23 lab=n_r2_2}
C {devices/lab_wire.sym} 240 390 0 1 {name=l24 lab=n_r2_3}
C {devices/lab_wire.sym} 480 570 2 0 {name=l25 lab=n_r2_3}
C {devices/lab_wire.sym} 480 390 0 1 {name=l26 lab=n_r2_4}
C {devices/lab_wire.sym} 720 570 2 0 {name=l27 lab=n_r2_4}
C {devices/lab_wire.sym} 720 390 0 1 {name=l28 lab=n_r2_5}
C {devices/lab_wire.sym} 960 570 2 0 {name=l29 lab=n_r2_5}
C {devices/lab_wire.sym} 0 810 2 0 {name=l30 lab=n_r2_6}
C {devices/lab_wire.sym} 960 390 0 1 {name=l31 lab=n_r2_6}
C {devices/lab_wire.sym} 0 630 0 1 {name=l32 lab=n_r2_7}
C {devices/lab_wire.sym} 240 810 2 0 {name=l33 lab=n_r2_7}
C {devices/lab_wire.sym} 240 690 0 0 {name=l34 lab=vss}
C {devices/iopin.sym} 0 1000 0 0 {name=p0 lab=lp_brk}
C {devices/iopin.sym} 120 1000 0 0 {name=p1 lab=fb}
C {devices/iopin.sym} 240 1000 0 0 {name=p2 lab=vss}
