v {xschem version=3.4.6 file_version=1.2}
G {}
K {}
V {}
S {}
E {}
T {cm_nmos_simple_2} -210 -200 0 0 0.4 0.4 {}
C {devices/sg13_lv_nmos_np.sym} 210 0 0 0 {name=MRA_B0 model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_b0_w l=x_dut_xmra_b0_l}
C {devices/sg13_lv_nmos_np.sym} 0 0 0 0 {name=MRA_BC model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_bc_w l=x_dut_xmra_bc_l}
C {devices/sg13_lv_nmos_np.sym} -170 0 0 1 {name=MRA_BO model=sg13_hv_nmos spiceprefix=X w=x_dut_xmra_bo_w l=x_dut_xmra_bo_l}
N -250 0 -250 94 {}
N -190 -90 -190 -30 {}
N -190 30 -190 90 {}
N 20 -90 20 -30 {}
N 20 30 20 60 {}
N 80 0 80 94 {}
N 190 -70 190 0 {}
N 230 -90 230 -30 {}
N 230 30 230 60 {}
N 290 0 290 94 {}
N 190 -70 230 -70 {}
N -250 0 -190 0 {}
N -150 0 -20 0 {}
N 20 0 80 0 {}
N 230 0 290 0 {}
N -190 60 230 60 {}
C {devices/lab_wire.sym} -150 0 0 0 {name=l0 lab=ra_ibias}
C {devices/lab_wire.sym} 230 -90 0 1 {name=l1 lab=ra_ibias}
C {devices/lab_wire.sym} 20 -90 0 1 {name=l2 lab=ra_tail}
C {devices/lab_wire.sym} -190 -90 0 1 {name=l3 lab=v_ref_out}
C {devices/lab_wire.sym} -190 90 2 0 {name=l4 lab=vss}
C {devices/lab_wire.sym} 290 94 2 0 {name=l5 lab=vss}
C {devices/lab_wire.sym} 80 94 2 0 {name=l6 lab=vss}
C {devices/lab_wire.sym} -250 94 2 0 {name=l7 lab=vss}
C {devices/iopin.sym} -190 280 0 0 {name=p0 lab=vss}
C {devices/opin.sym} 590 -30 0 0 {name=p1 lab=v_ref_out}
C {devices/opin.sym} 590 90 0 0 {name=p2 lab=ra_tail}
C {devices/opin.sym} 590 210 0 0 {name=p3 lab=ra_ibias}
