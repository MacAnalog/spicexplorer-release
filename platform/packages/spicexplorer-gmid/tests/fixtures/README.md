# gm/ID test fixtures

Copies of committed analog-db LUTs so the package tests are **self-contained and depend on no DB
import** — the leaf-tool rule.  If a source LUT is regenerated, refresh the copy with the
`cp` command shown below.

| File | Source LUT | Purpose |
|---|---|---|
| `sky130_fd_pr__nfet_01v8__tt.pkl` | `_shared/gmid/sky130/sky130_fd_pr__nfet_01v8__tt.pkl` | sky130 NMOS @ tt — fast sizing tests |
| `sky130_fd_pr__nfet_01v8__tt.manifest.json` | `_shared/gmid/sky130/sky130_fd_pr__nfet_01v8__tt.manifest.json` | manifest sidecar — typed `LUTManifest` / `LUTRegistry` tests |
| `sg13_lv_nmos__tt.pkl` | `_shared/gmid/ihp-sg13g2/sg13_lv_nmos__tt.pkl` | IHP nmos @ tt — P4 SPICE back-annotation slow test |

Refresh commands (run from this directory):

```bash
cp ../../../examples/analog-db/_shared/gmid/sky130/sky130_fd_pr__nfet_01v8__tt.pkl .
cp ../../../examples/analog-db/_shared/gmid/sky130/sky130_fd_pr__nfet_01v8__tt.manifest.json .
cp ../../../examples/analog-db/_shared/gmid/ihp-sg13g2/sg13_lv_nmos__tt.pkl .
```
