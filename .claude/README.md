<!-- Managed by the private release infra (scripts/release/repo/.claude/) —
     edit there, not here; the next release port overwrites this file. -->
# Agent kit

Agent definitions and skills for driving this repo with [Claude
Code](https://claude.com/claude-code). Clone the repo and they are picked up
automatically: agents appear as subagent types, skills trigger off their own
`description` metadata. They are ordinary Markdown — read them directly if you
use a different agent runtime, or copy the folders into another repo's
`.claude/`.

Every one of them is *block- and PDK-agnostic*: they encode the method, and
take the circuit, the benches and the PDK as inputs.

## Agents — the layout lane

A signed-off schematic becomes a layout in four hand-offs. Each agent has one
job and refuses the others; the reviewer never writes layout, the designer
never self-certifies.

| Agent | Job | Reads | Writes |
|---|---|---|---|
| [`layout-brief-author`](agents/layout-brief-author.md) | Measures the design intent before anything is drawn — ranked net sensitivities with parasitic budgets, matching classes with tolerated mismatch, hi-Z/leakage nodes, wells, symmetry, and the explicit don't-cares | the certified cell + its own frozen benches | `BRIEF.md` + `brief.json` |
| [`layout-designer`](agents/layout-designer.md) | Turns the certified cell into a **parameterized generator** (gdsfactory Python whose parameters are an optimizer's knobs), then proves it DRC-clean, LVS-identical, and re-measures the benches on the extracted netlist | the brief + the certified netlist | `gen_<cell>.py`, GDS, `PLAN.md`, `REPORT.md` |
| [`layout-reviewer`](agents/layout-reviewer.md) | Independent, report-only review: rebuilds the GDS from the committed generator and re-runs DRC/LVS/PEX itself, then reviews per-net parasitics against the brief's budgets | the generator + the brief | `REVIEW.md`, `REVIEW.yaml` (the `layout-review/1` DSL), `REVIEW.png` |
| [`layout-schematic-codesign`](agents/layout-schematic-codesign.md) | Runs the layout-in-the-loop co-design loop: expresses sizing + layout knobs as one `sim_engine: layout` project, runs `spicexplorer-optimize` (build → DRC → LVS → PEX → benches, every trial), and either accepts the winner or repairs the generator and goes again | the generator + the block's specs | the search projects, per-round records and figures |

Worked example, end to end: [`agentic-design-example/`](../agentic-design-example/)
— the PAM-4 driver DAC in IHP SG13G2, with every co-design round on the record.

## Skills — gm/ID sizing

The Jespers & Murmann lookup-table methodology, wired to this repo's
`spicexplorer-gmid` tool and the analog-db extraction pipeline.

| Skill | Use it when |
|---|---|
| [`gmid-sizing`](skills/gmid-sizing/) | Sizing or verifying a circuit — W/L and bias current from gm/ID, inversion level, intrinsic gain, fT; verifying a sized design against ngspice operating points. `references/` holds the recipes (OTAs, biasing, noise/mismatch, worked designs from the book) |
| [`gmid-lut-generation`](skills/gmid-lut-generation/) | No lookup table exists yet for a PDK, device flavor, corner or temperature. Drives `analog-db gmid-extract`; needs live ngspice + a PDK (`make up-live`) |

The lookup tables themselves are **not** committed — they are regenerable
artifacts and land in an out-of-repo store (`~/.spicexplorer/gmid/`).
