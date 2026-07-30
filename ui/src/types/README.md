# API types — codegen pipeline + adoption

Two files describe the api contract:

- **`api.ts`** — hand-written interfaces, **plus** a large set of `type` aliases
  ADOPTED from the codegen (the app imports everything from here, so adoption is a
  one-line swap with zero call-site churn).
- **`api.gen.ts`** (generated) — produced from the api's OpenAPI by `npm run gen:types`
  (`openapi-typescript ./openapi.json -o src/types/api.gen.ts`). Excluded from eslint.

## Adopted from codegen (the backend route carries a `response_model=`, the UI type is a one-line alias)

| UI type(s) | generated schema | api route |
|---|---|---|
| `EnvInfo` | `EnvResponse` | `GET /api/env` |
| `AppConfig` | `ConfigResponse` (+ `PresetCheckpoint`) | `GET /api/config` |
| `ParamSensitivity`, `SensitivityResponse` | same | `GET /api/spec/{name}/sensitivity` |
| `SanityCheckResponse` | `SanityResponse` | `POST /api/sanity-check` |
| `SimulateOnceResponse` | same | `POST /api/simulate/once` |
| `ScoreResponse`, `SpecScore`, `ScoreCurve` | same | `POST /api/score` |
| `ProjectSummary` tree (`DutParam`, `TbParam`, `Testbench`, `TargetSpec`, `ModelInclude`, `SupplyOverride`, `PVTCornerDef`, `PVTConfig`) | same | `POST /api/project/load`, `GET /api/projects/{id}` |
| `LoadProjectResponse`, `ValidateResponse`, `GenerateProjectResponse` | same | `POST /api/project/{load,validate,generate}` |
| `CheckpointMeta`, `CheckpointData`, `EnvelopeEntry`, `ScatterPoint` | same | `GET /api/checkpoint*` |
| `ProjectMeta`, `ProjectDetail`→`ProjectDetailResponse`, `ProjectRun`, `ExampleMeta`, `TrashItem` | same | `GET /api/projects`, `/examples`, `/trash`, `…/runs` |
| `NetlistParseResponse` | same | `POST /api/netlist/parse` |
| `RunStartResponse` | same | `POST /api/optimize/start` |

> `TargetSpec.goal` is now `string` (the wire value), not the old narrowed
> `"exceed" | "minimize" | "exact"` — the editable union lives in `WizardTargetSpec`.

## Coverage

Most routes carry a `response_model` and emit a typed `$ref` 200 in `openapi.json`;
the committed (drift-guarded) `openapi.json` is the source of truth for exact counts
(see the **Regenerate** section below for the CI drift check that keeps it honest). The
deliberately-untyped routes are the non-JSON ones: PlainText (`GET /api/yaml-text`),
FileResponse (`GET /api/schematic` and `GET /api/library/circuits/{id}/schematic` SVG,
`GET /api/library/templates/{id}/image` PNG, `GET /api/library/circuits/{id}/reference-image`,
`GET /api/waveview/runs/{id}/artifacts/file`, `GET /api/checkpoint/{id}/report` zip), SSE
streams (`GET /api/optimize/stream/{run_id}`, `GET /api/waveview/log/stream`), plus
`GET /health`. The SSE per-event shapes (`SSEEvent`/`CheckpointEvent`) stay
hand-written — they describe stream frames, not a single response body.

The library routes (`/api/library/*`) and the waveview routes (`/api/waveview/*`) are
fully typed in `api.gen.ts` (bar the file/SSE ones above); the Library's view-model
types live in `src/lib/library/types.ts` and `adapt.ts` (not `api.ts` aliases)
because they go through an adaptation layer.

## Still hand-written (by design)

- **The wizard-editing tree** — `WizardForm` and its members (`WizardProjectInfo`,
  `WizardPVTCorner`, `WizardDutParam`, `WizardTargetSpec`, …) plus `ParseProjectResponse`.
  These are constructed/mutated in `wizardStore`, and the hand-written shapes are
  deliberately stricter (optional/union fields) than the generated all-required schema.
  The backend `/project/parse-to-form` DOES carry a `WizardForm` response_model now, so a
  future pass can reconcile the two if the editing types are relaxed to match.
- `NetlistParam` / `MeasCandidate` / `SpecLibraryEntry` — small wizard-editing helpers
  still referenced directly by wizard components.

## Regenerate (must stay in sync — see the CI drift check)

```bash
# 1) dump the api OpenAPI (from the platform repo, offline — no running server):
uv run python -c "import json; from spicexplorer_api.main import app; print(json.dumps(app.openapi(), indent=2))" > openapi.json
# 2) generate the TS types:
npm run gen:types
```

`openapi.json` is a committed snapshot; CI fails if it (or `api.gen.ts`) drifts from the
backend — see `scripts/check_openapi_drift.sh` and `.github/workflows/openapi-drift.yml`
in the **meta-repo** (`spicexplorer-workspace`), not the platform `ci.yml`. Regenerate
both whenever a route's request/response model changes.

The end state: every JSON route typed, `api.gen.ts` the single source of truth, the
remaining hand-written wizard interfaces retired once the editing types are reconciled.
