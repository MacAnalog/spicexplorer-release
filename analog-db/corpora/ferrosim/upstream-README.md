# ferrosim netlist import

Source: https://github.com/Arcadia-1/ferrosim

Curated Spectre netlist examples imported from ferrosim test decks.

Sensitive absolute include paths were replaced with placeholders such as
`${PDK_ROOT}`, `${CADENCE_ROOT}`, and `${PROJECT_VA_ROOT}` so the examples
preserve their include intent without exposing local filesystem layouts.

Included:

- Real test decks under `tests/`, including ported analog blocks, SAR ADC blocks, opamps, comparators, sampling switches, and small Verilog-A demos.
- One compact transistor-characterization set under `tests/decks/transistor_char/` (`gm/Id`, DIBL, and Ron sweeps).
- The SAR ADC `with_mos` variant; the duplicate `stripped` variant was omitted to avoid repeated shared blocks.

Excluded:

- `output/char_netlists/` characterization sweep decks; they are mostly one-template-per-corner/length/temperature expansions.

Total netlist files: 122

## Directory counts

| Directory | Files |
|---|---:|
| `tests/decks/amp5t` | 5 |
| `tests/decks/biquad` | 16 |
| `tests/decks/bsimbulk` | 3 |
| `tests/decks/cap_meas.scs` | 1 |
| `tests/decks/comparator` | 14 |
| `tests/decks/inbuf` | 7 |
| `tests/decks/ldo.scs` | 1 |
| `tests/decks/opamp` | 8 |
| `tests/decks/ported` | 17 |
| `tests/decks/refbuf` | 3 |
| `tests/decks/restrim` | 3 |
| `tests/decks/ring5.scs` | 1 |
| `tests/decks/sampling_bts` | 7 |
| `tests/decks/sar` | 18 |
| `tests/decks/sc_counter` | 3 |
| `tests/decks/sc_integrator.scs` | 1 |
| `tests/decks/sc_ring` | 2 |
| `tests/decks/transistor_char` | 3 |
| `tests/decks/va_decl_init.scs` | 1 |
| `tests/sc_sample/sc_sample.scs` | 1 |
| `tests/va_demo/tb_chain.scs` | 1 |
| `tests/va_demo/tb_cswitch_res.scs` | 1 |
| `tests/va_demo/tb_cswitch_short.scs` | 1 |
| `tests/va_demo/tb_degsh.scs` | 1 |
| `tests/va_demo/tb_diode.scs` | 1 |
| `tests/va_demo/tb_sqlaw.scs` | 1 |
| `tests/va_demo/tb_tee.scs` | 1 |

## Manifest

| Path | Bytes | SHA256 |
|---|---:|---|
| `tests/decks/amp5t/netlist/dut/amp_5t_d2s.scs` | 461 | `5ca6e86bce133ac92d93520f0a240e733bd3b4cd7ace2ba36407551db3cb20df` |
| `tests/decks/amp5t/netlist/runs/common_setup.scs` | 1742 | `5669b3b50b8b33913db3b38f3de6e05907842abe9511b99e397eaf504e6a1262` |
| `tests/decks/amp5t/netlist/runs/vdd_0p9.scs` | 74 | `4e3f70f41af98c38ec3e4bd3577dc94553541ecb56aa61b983cce2a5424ec038` |
| `tests/decks/amp5t/netlist/runs/vdd_1p0.scs` | 74 | `54d43f9a41c6f796a59b0a08f1fffc212a6605ecb7072f0715b9ec2803746c3f` |
| `tests/decks/amp5t/netlist/tb/tb_amp_5t_d2s_dc_ac.scs` | 438 | `8f1d0bb2df59b70fecd3d86ae033b95103885154be32d2e585446cd30273412f` |
| `tests/decks/biquad/netlist/dut/hs_biquad_ota.scs` | 13857 | `df6f6b108539a6df0a92ef197639d73e9e836d5aba4b36704d911934ee1c8b6b` |
| `tests/decks/biquad/netlist/dut/hs_biquad_ota_geometry.scs` | 100660 | `adbaf0dc56479284cb31e1f52cad3c8b2777d7e4fd3966a3f402c9a1a70c6f96` |
| `tests/decks/biquad/netlist/runs/common_ac_noise.scs` | 1332 | `22789868af33cab09ccfc2cac9862a1baaa9628d38134dc8350e0287cea9075e` |
| `tests/decks/biquad/netlist/runs/common_ac_noise_geometry.scs` | 1350 | `c788f6086359cfb8eee1f58393b062d8b5b42e28deb484da23d06db67c1ba7e3` |
| `tests/decks/biquad/netlist/runs/common_setup.scs` | 1629 | `002bb30c04aff992851535816d99a13c5cc2969e5e82b46614e0ab6cdcca5632` |
| `tests/decks/biquad/netlist/runs/common_setup_geometry.scs` | 1647 | `37f3f2fe3ac65b57011cfc63789b1965a1349ae2929a8fc740b1cd810ae7ac81` |
| `tests/decks/biquad/netlist/runs/vdd_1p1.scs` | 74 | `42415cfd1bb8e2edb8e7b27d9d76766f5596ae5a7926b2fdd03371c4b0d260f9` |
| `tests/decks/biquad/netlist/runs/vdd_1p1_geometry.scs` | 83 | `df1264c4edbdb2e41a7249621f010d516cd54c1a78ed827b02ad494ffa0110a3` |
| `tests/decks/biquad/netlist/runs/vdd_1p2.scs` | 74 | `dd5fa2f29211542eac15614342c8b7aa4a8887a4ff8b8adb54daee7d12c3ddd0` |
| `tests/decks/biquad/netlist/runs/vdd_1p2_ac_noise.scs` | 77 | `bd94e42870445625b065c19bd6ef13160e49f31487c39357c0da2bab799f009f` |
| `tests/decks/biquad/netlist/runs/vdd_1p2_ac_noise_geometry.scs` | 86 | `04a1b2e201bda8919fd93a197a94ee82765a574cc94d712bbfeb00d76c1c2d61` |
| `tests/decks/biquad/netlist/runs/vdd_1p2_geometry.scs` | 83 | `670fca9417e6f8246cc2422c3c166b917c78120e62c77b99eedaf44ccbf977e6` |
| `tests/decks/biquad/netlist/runs/vdd_1p3.scs` | 74 | `d42cdbf8ae2cd29df8fce2661e449126da0fed42423ab2f14261a3e6ef675601` |
| `tests/decks/biquad/netlist/runs/vdd_1p3_geometry.scs` | 83 | `b7e83d671d0046cf3f89cb75b2a85bcb9284add2146e46e5dcdf63a38e1bf695` |
| `tests/decks/biquad/netlist/tb/tb_biquad_exp.scs` | 1135 | `bf03866eb36a9c3110b0c61dd8f25a0693fa3cc5a0eba4c1e70478881fefe8ff` |
| `tests/decks/biquad/netlist/tb/tb_biquad_exp_geometry.scs` | 2038 | `4a59a3d031866119493371857ef298a67eb9aebea0b73096b66bc0865afa7a91` |
| `tests/decks/bsimbulk/bench_nmos.scs` | 518 | `51bc01b6e66793a6cc5737c478c7c58cee12618b856b1a7aaae62b7c6161e12a` |
| `tests/decks/bsimbulk/nmos_iv.scs` | 573 | `714fedec43125ec29ecc404078ead10b1c5949fd32f9957954b00b08c7ab21f8` |
| `tests/decks/bsimbulk/pmos_iv.scs` | 527 | `ba02ad7fb33904637adb8302f38de57f7cafde1a25ea3bd96da4cf0e1a2f5c32` |
| `tests/decks/cap_meas.scs` | 1118 | `cec6650d0663506db5f0ad18e1841638d5f2a7cb21b546696d6374286c1e6e43` |
| `tests/decks/comparator/netlist/dut/cmp_strongarm.scs` | 1281 | `bf70e886fe8be2d565b7c4a8f20bc03710c7a4d7e03fc94fd4e9e61ec40b8b6c` |
| `tests/decks/comparator/netlist/dut/cmp_strongarm_offset_trim.scs` | 3583 | `c5770a8d11823688fb63603281d273ce9f0cfa0867537464f88a1642fce6e226` |
| `tests/decks/comparator/netlist/dut/cmp_under_test_offset_trim.scs` | 316 | `c6d2b3a87fd6491da6dbf4381fd1edd8800f88b1bed2344fa6b2f2c54e28908a` |
| `tests/decks/comparator/netlist/dut/cmp_under_test_plain.scs` | 236 | `c022555c306dc9f473baf67d0087df30bed63d3be3bf130708b0c07cf3cd684c` |
| `tests/decks/comparator/netlist/runs/mc_offset_offset_trim.scs` | 1432 | `4f8cea01714b283e75b295b35bcf34ca0c68f69e5e2bef9b63fa24c7e8ecb7e7` |
| `tests/decks/comparator/netlist/runs/mc_offset_plain.scs` | 1413 | `6f8b447aef5c5d1d381485d03fdf96d530bbf9b0ef9c0167f277d6c80e9be45a` |
| `tests/decks/comparator/netlist/runs/offset_offset_trim.scs` | 1152 | `8eb3f612be4c1dd04b25c65474a6e87d7f8cc304b361e792ec6b4f6aa76272f5` |
| `tests/decks/comparator/netlist/runs/offset_plain.scs` | 1133 | `5a8a375c1bbc7fce6d608a64997ec5143fd31305c69555f7b90e01e035c427f8` |
| `tests/decks/comparator/netlist/runs/pss_pnoise_offset_trim.scs` | 1301 | `4ca523ed93df421b60fee86664f24370f4c809b75af50d303585d2fa0077395e` |
| `tests/decks/comparator/netlist/runs/pss_pnoise_plain.scs` | 1282 | `a1fc6189a14a904a3f4e57e2c6da8390f417cd6e9a792bbf7c93d9d7a4089f1a` |
| `tests/decks/comparator/netlist/runs/pvt_pss_pnoise_offset_trim.scs` | 1617 | `79108ffb29e78e484a468590b23f40d4640b376cc9e4f30869ac520960f6ecbf` |
| `tests/decks/comparator/netlist/runs/pvt_pss_pnoise_plain.scs` | 1616 | `cf885f4335ab08444ae01ea54caad3aad06f1bf0e129ed0def408b7b1b4a03bb` |
| `tests/decks/comparator/netlist/tb/tb_cmp_offset_search.scs` | 530 | `9ef03c60d0c9e860bfeb463caba38f12f6010299659b10421f5b3a2b5441979e` |
| `tests/decks/comparator/netlist/tb/tb_cmp_pss_pnoise.scs` | 537 | `fc03fc73184e4956bff4539353b6e4bed879e962ca4914a6d5b478e45dbbf012` |
| `tests/decks/inbuf/netlist/dut/l1_input_buffer_cascode.scs` | 15981 | `3b223abfd9f402e68061338ffb5e1d67afdb4fd12d110be5b4b65b7832a6cfe4` |
| `tests/decks/inbuf/netlist/runs/pss_100M.scs` | 824 | `01434b6b63242483cacf031a36a31079311a89f331fb2387cebc9ef2a730401d` |
| `tests/decks/inbuf/netlist/runs/pss_1G.scs` | 822 | `89d316a74974187765bc59b1d47e4c96288a8b738c764b50dc4338b70ccef1e3` |
| `tests/decks/inbuf/netlist/runs/pss_2G.scs` | 822 | `f4c935ba42d34b57a9c95c40ce475b81e12ca421514238f98675fbced8901c7f` |
| `tests/decks/inbuf/netlist/runs/pss_4G.scs` | 822 | `4cc177a6288de66a23cda5d69543d3a8e4e44a63f2c9bbc8a85e9f3d8f1a8617` |
| `tests/decks/inbuf/netlist/runs/pss_8G.scs` | 822 | `94b3d9ef66e7a6dedc898cbca6d11bafdc99db6b676dd712b8f53fbdd7e6997c` |
| `tests/decks/inbuf/netlist/tb/tb_input_buffer_cascode_pss.scs` | 564 | `d1d0126176e4f6f5e0da00a87667cb038a0b28e2c110c1ef844b167438c6f3a5` |
| `tests/decks/ldo.scs` | 1869 | `c5f9458654bf209b01ad2c10fdcb2736079d324e55dd71a99f3b621fb161ccef` |
| `tests/decks/opamp/netlist/dut/ota_fd2s.scs` | 4306 | `4a4558925b8bf72a1e40e0dfa5b989244f5a7dcd3ab24eca6c8a34dc65be1c34` |
| `tests/decks/opamp/netlist/runs/cl_tran.scs` | 752 | `79e902a569b46071d5b08ab773a3efb6cd7e745c1d965bfc4a30f708f0015a5b` |
| `tests/decks/opamp/netlist/runs/mc_offset.scs` | 787 | `ebec76b5f512a4cbeec974424e7b397736336d8d4d55bd127b097a9aef5116a2` |
| `tests/decks/opamp/netlist/runs/ol_cmrr.scs` | 696 | `cfc8533a20b6b173f455cdc15cd220fed21ff9d19bdb8042bcbe24ce8bda38ca` |
| `tests/decks/opamp/netlist/runs/ol_main.scs` | 1156 | `b45891638ea7940713d80d1a0b27a8b9ed2bfc851fc28bb11730d7eb665da8a2` |
| `tests/decks/opamp/netlist/runs/ol_psrr.scs` | 725 | `781e7fe3000b9cfdef9bf11bcc52f7bc5c7701c5679740fa121f7870054e505b` |
| `tests/decks/opamp/netlist/tb/tb_closedloop.scs` | 1397 | `b7923e2241b1acf624878335b05f3ba425b9e104c8667f6d13c0accd8462bf70` |
| `tests/decks/opamp/netlist/tb/tb_openloop.scs` | 976 | `e6203272e77ac6cf38d5a89392ab6a538f1578d2430bd5b9ff5aa47677b4d298` |
| `tests/decks/ported/bandgap_core_28.scs` | 1348 | `6df671f491632b5f4e3963a0dc714e617f2147c055e46430c182645b498e591f` |
| `tests/decks/ported/bandgap_core_65.scs` | 1323 | `d04e6c8aa87346517a9280ed3ea24765c4e5062181e144a82e0b3a1768ee8a69` |
| `tests/decks/ported/bjt_cal_28.scs` | 412 | `e871ecb0ce9941b12129a4aa1cc6a9db11b38b2c88fbdd0ba28453d750c1ce18` |
| `tests/decks/ported/common_source_28.scs` | 1036 | `21bca650cb49d43c34c9c294ea58e42ff6deafb885e2aaff503a096c8da44e07` |
| `tests/decks/ported/common_source_65.scs` | 1033 | `2fba08455078e75733e6665ddce0ed2e7b7d1eda89ffba7ea4d4f13ec1c8f46d` |
| `tests/decks/ported/differential_pair_28.scs` | 696 | `a19bf5af1be7cc8e01918ebda88229245f6c4197f8b849605fc5c97c6da99981` |
| `tests/decks/ported/differential_pair_65.scs` | 725 | `74aa9bf2e4be8a6fbda9d060f852103fc14ecb33c0e7394b9956046f3ec74cbb` |
| `tests/decks/ported/hyst_comparator_28.scs` | 1109 | `0b25fc36d54d12239c761ee9ee2ec794a4cb0a8f84ab3ae1cf612b1b247ba8fa` |
| `tests/decks/ported/hyst_comparator_65.scs` | 1094 | `30dc88feaf31d6c5635187b93e316f3c4de9cc510045ad43b8940cdb0503670c` |
| `tests/decks/ported/ldo_28.scs` | 1076 | `1c1bee7c89a1a6f2a73e9996a336b0dfe87702d66c0d6d5b6bc638351f683431` |
| `tests/decks/ported/ldo_65.scs` | 1081 | `81b7478620eb9a1c222c516dcb6e6355681ac780ab5965f1892dd1a89f3819a7` |
| `tests/decks/ported/lfsr8_28.scs` | 1836 | `4d45bc396e41fb896bc561ba1325e5b62be5fad4c16897dfe7008b48b85c5850` |
| `tests/decks/ported/pga_16step_28.scs` | 2304 | `d7340934b2cab9ba5153a4508f4a44a09f36ea99b9dcd168e265ec8099f15e43` |
| `tests/decks/ported/source_follower_28.scs` | 776 | `0bc5635db5573a8033e03f63b23880da99244b8a5c6e77b9287e4c4c6037ac34` |
| `tests/decks/ported/source_follower_65.scs` | 786 | `c6bb31dd0131d0a83c31b7024f1ff14ab3070786bcf681640266431ca285cb87` |
| `tests/decks/ported/two_stage_opamp_28.scs` | 948 | `dd5b696fad0e1f7a45ff534f2d850c60d6398c70bea2933db3667391bf8df2e0` |
| `tests/decks/ported/two_stage_opamp_65.scs` | 949 | `36b5ca458ba79642667746ba5ec27b217f2865a291a0eaf3396ff8f258e29ee4` |
| `tests/decks/refbuf/netlist/dut/ref_buffer_blocks.scs` | 2895 | `9f07578fca987c9a6169330f74e36a4a0931066455ce388426608a77f57ac9a2` |
| `tests/decks/refbuf/netlist/runs/dc_ac_tran_noise.scs` | 2033 | `280f5807b74e5596654c770739df586fddbeb1c1b718383da0907767010d7f65` |
| `tests/decks/refbuf/netlist/tb/tb_ref_buffer_characterization.scs` | 1103 | `4ceb30c44256c258a3842021cc61a37fe006a80ca2571ebcd5c8fea4e4456bce` |
| `tests/decks/restrim/netlist/dut/res_trim_thermo_16.scs` | 2578 | `087324f5d9b90a6d33862dbb7219e6a618faef83503bfd717adf4a2653ed4504` |
| `tests/decks/restrim/netlist/runs/dc_trim_resistance.scs` | 1318 | `2dbb9f6426f81c9fc06f26508d4cc807566fe0d6342a19744023d206f1059c6d` |
| `tests/decks/restrim/netlist/tb/tb_resistance_dc.scs` | 856 | `11c7b2e68d5b2c55a8967acf8aa383fca32c6b2cdda3c87d62eca7580d164fc2` |
| `tests/decks/ring5.scs` | 1164 | `510bb0ee2821e36ebacba8b82a160b21cf39d76143c7fa05afc5003508b05915` |
| `tests/decks/sampling_bts/netlists/bootstrap.scs` | 8367 | `77cde6f2ed79e6da2306f7491382b987576a12643793f33fe53e5d2325d72d64` |
| `tests/decks/sampling_bts/netlists/bottom_plate_dut.scs` | 2921 | `5407fbef2e0d8c18865aecf508c7a89ab62615b7a4f68b7c9aac6b8d89f82238` |
| `tests/decks/sampling_bts/netlists/bottom_plate_ideal_bts.scs` | 2648 | `1f232521bb8b506517bf1666c68e9e25ceadb83e32127833a64674f01189c557` |
| `tests/decks/sampling_bts/netlists/bottom_plate_real_bts.scs` | 2625 | `ee61620b270617c558c237b73253548300ab7910283d1e1f3ba2ec36c75fc670` |
| `tests/decks/sampling_bts/netlists/top_plate_dut.scs` | 1336 | `20b7f7818d73bfa8ba4f46e68d9c4e468ec807512944c6264bba2946ddf06df6` |
| `tests/decks/sampling_bts/netlists/top_plate_ideal_bts.scs` | 1686 | `c38693c6163c5e325ede9fb02bc2fd5d628dd253c160f67bceb8a3a7bab05d4e` |
| `tests/decks/sampling_bts/netlists/top_plate_real_bts.scs` | 1701 | `b1cb8ba4e33f10a701ffececa75c3b2513826a1d56f03b11e946feb586b3600f` |
| `tests/decks/sar/netlists/sampling_bootstrap_l4_bts_x2.scs` | 396 | `d188efcb1353ca3e13890da9cd785942299061f3579fc3fb87c2d1b01f5978f6` |
| `tests/decks/sar/netlists/sar_adc_11b_sampling_bts_with_mos.scs` | 923 | `0e28dc1a92f8d1e72f75846f8299076847a1b53ff563f471020482fe6359891e` |
| `tests/decks/sar/netlists/sar_adc_11b_with_mos.scs` | 929 | `389d571300e4bcbc778f53d5bc3735ec88c5fb6dc05bf5c506d4aa922bc66a31` |
| `tests/decks/sar/netlists/variants/with_mos/00_corner_and_models.scs` | 1282 | `ecd1fb66e9a48bb61d83f656ab73a09536bf3d1c1b72e9893bc5f51568839721` |
| `tests/decks/sar/netlists/variants/with_mos/10_refgen_ideal.scs` | 394 | `837d32f814d2acc4dc923fb69398087504df5da847aa5db888e2075cbd49b51b` |
| `tests/decks/sar/netlists/variants/with_mos/20_comparator_dynamic_l4.scs` | 19380 | `b34e6dfe544c33a46595ec4ec610b107dd8b06f6add3ff8c06611ee5a3e0a8e0` |
| `tests/decks/sar/netlists/variants/with_mos/30_bottom_plate_switch_l5.scs` | 11641 | `1b211d9c9b7eb579587946d9763dccda6a7dc8fc87be99df6e30112eeafdbf6c` |
| `tests/decks/sar/netlists/variants/with_mos/40_sar_latch_cell_l5.scs` | 7413 | `e4b37ff0fa74de483a9e56bdc7d70cfaa48870db0ddce72425035d6ecfe19497` |
| `tests/decks/sar/netlists/variants/with_mos/41_sar_latch_lsb_l5.scs` | 7350 | `4114a76bf3534b24400ef17d086cea2de3446c00db736f4c32c50f64c8ef4346` |
| `tests/decks/sar/netlists/variants/with_mos/42_sar_logic_switch_l4.scs` | 7193 | `514950cc7c12bbaa54709dc3132be5bcd0cd3db50a74bc9ead243dbdb0bd86f1` |
| `tests/decks/sar/netlists/variants/with_mos/50_cap_unit_x1.scs` | 282 | `3ffcf0c349332eae2752e8808fe49b069116f227462b735c4ac735552621bf56` |
| `tests/decks/sar/netlists/variants/with_mos/51_cap_unit_x3.scs` | 354 | `818bc1493f4a42a090bcaaf78931cf6e9d4944de8998a5c0359c191f876a44c6` |
| `tests/decks/sar/netlists/variants/with_mos/52_cap_array_l5.scs` | 16508 | `54cd1a338e90d1b8ea0caf16638cd70e0c5659d4c24dbe5f644282f0270e27cd` |
| `tests/decks/sar/netlists/variants/with_mos/53_cdac_sampler_l4.scs` | 2565 | `e2aa6f2136241bf48373efc3bcfcac6a0fce791a511e23637c7c48ad9e0e1316` |
| `tests/decks/sar/netlists/variants/with_mos/60_bootstrap_core_lb.scs` | 6337 | `1ef6323ea0b16d13f3ad961fbfa2e5bb880c84e8e98bdb1e65a1af1deeeaee1c` |
| `tests/decks/sar/netlists/variants/with_mos/61_bootstrap_diff_l4.scs` | 351 | `0890636ea0aa2eabe18dee6008490d704c090e2d1f6d8e4f2eddc70364d91900` |
| `tests/decks/sar/netlists/variants/with_mos/90_sar_adc_11b_l3.scs` | 1924 | `fc155a9f59886385fafa807e305416095674055b79dff279abfd31e9c9719c00` |
| `tests/decks/sar/netlists/variants/with_mos/99_tb_sar_adc_11b_interactive13.scs` | 2284 | `b2ad42fd9b296270c3386e5c3403ec32e8896069a36f0d050fa557aecb8631a4` |
| `tests/decks/sc_counter/netlist/dut/counter_prog_4b.scs` | 1990 | `42a973b738f8d4af4355c657df4d12e4a30121c292340ad989f97f5bf9e36b08` |
| `tests/decks/sc_counter/netlist/runs/tran_counter_prog_4b.scs` | 1512 | `5e01fb4bad37e08ae68c795eb19f8593dae69c2b02fb09df3d9b5f7d3345c8bb` |
| `tests/decks/sc_counter/netlist/tb/tb_counter_prog_4b.scs` | 597 | `8570a20237fbc4f610cb46c2a992dae6a863ad47941a9232121f409af715a53d` |
| `tests/decks/sc_integrator.scs` | 1930 | `361e6d7a0245aff02e6be6b5a61db3c555291303abb92745faf20acf2c786477` |
| `tests/decks/sc_ring/netlists/ring_osc_lvt.scs` | 750 | `eaf418ea477a630089cb21acb18b961050d75997decc4e114de029944bfad846` |
| `tests/decks/sc_ring/netlists/ring_osc_svt.scs` | 738 | `5a687fffe37c73446589d34ea59da2f1482ee25cccb3f1276f947e06f3af4464` |
| `tests/decks/transistor_char/dc_vds_dibl_ulvt.scs` | 819 | `c9a482957031695f63c5b6a84394300828d0bb10cd303b1459258faf8bb8c37b` |
| `tests/decks/transistor_char/dc_vds_ron_ulvt.scs` | 879 | `58171b32e80accf3b4903435fef916a8f1f692dee4132e6c6f6a70d2e4969bdb` |
| `tests/decks/transistor_char/dc_vgs_gmid_ulvt.scs` | 851 | `c8c5ee09e35c01eb2a84d4c3f93561ed94c5f52e06e7170eb3964024ed58131c` |
| `tests/decks/va_decl_init.scs` | 1110 | `47b9ef3536d93ff8d9faf5141c6f47f4449f24b06cd6b71586023339daa3943a` |
| `tests/sc_sample/sc_sample.scs` | 870 | `6e4ecf50bb9ba52107f148ed305bcd05109490f2baa1eb29747cb6cb047071c3` |
| `tests/va_demo/tb_chain.scs` | 231 | `49b89a4296c78ec6b2aed4fd51fcb17927cec5ae2f91d5e87aa3e1b6e939d82e` |
| `tests/va_demo/tb_cswitch_res.scs` | 245 | `7653ff5e9306111a3f09c45ebb28ebc73a80ce7ef7c3b9d62f8f34e44673ace8` |
| `tests/va_demo/tb_cswitch_short.scs` | 246 | `d34fefef35d2e4d54a8d99de67550191ad1f3a66f45b65c2171bf0dc467f56a0` |
| `tests/va_demo/tb_degsh.scs` | 235 | `9b3a36b5590ad8ea570d9bf2fde86f82bd22a72157c76b54a2b5528fcd9f5b32` |
| `tests/va_demo/tb_diode.scs` | 496 | `883997c6ea9e6270bfcc2414a1991c7f4981c37bf2d9882c7c4edeb6bbda9f7a` |
| `tests/va_demo/tb_sqlaw.scs` | 239 | `098e50f28ad8870fdb59e748bdfe7c566145a60b02aea5538f3e72c0276cffba` |
| `tests/va_demo/tb_tee.scs` | 216 | `11ff0b334f55a209a03c4e7b56ff90dff4d0d07800e01f90e7a550f05000256e` |
