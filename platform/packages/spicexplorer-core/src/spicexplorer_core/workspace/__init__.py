"""WORK_ROOT storage kernel — the project-filesystem contract (layout v2).

The single home for "what lives where under WORK_ROOT": the v2 project layout
(:mod:`~spicexplorer_core.workspace.layout`), the ``manifest.json`` identity
schema (:mod:`~spicexplorer_core.workspace.manifest`), the additive v1→v2
migrator (:mod:`~spicexplorer_core.workspace.migrate`, CLI:
``python -m spicexplorer_core.workspace``), the generalized run envelope
(:mod:`~spicexplorer_core.workspace.runs` — sortable dir==run_id minting, owner
liveness/heartbeats, input provenance into ``.objects/``), and the run store's GC
(:mod:`~spicexplorer_core.workspace.retention` — artifact-tier pruning by age,
CLI ``python -m spicexplorer_core.workspace.retention``).

Adapters (the FastAPI ``project_service``) and orchestration agents both build
on this module so every process speaks ONE storage contract.

Invariants this package enforces:

- the filesystem is canonical; anything derived (index, ``state.json``) is
  rebuildable from it;
- every manifest write is atomic (:mod:`~spicexplorer_core.atomic_io`) and
  bumps a monotonic ``rev`` — a torn ``manifest.json`` must never equal a
  vanished project;
- migration is **additive + idempotent**: the migrator creates missing
  structure and upgrades manifests in place, and never moves, renames, or
  deletes anything a v1 reader depends on (``project.yaml`` stays at the
  project root).
"""

from spicexplorer_core.workspace.annotations import (
    merge_curated,
    merge_proposal,
    read_curated,
    write_curated,
)
from spicexplorer_core.workspace.layout import (
    PROJECT_DIRS_V2,
    SHARED_DIRS,
    scaffold_project,
    scaffold_shared,
    shared_root,
    work_root,
)
from spicexplorer_core.workspace.library import (
    import_cell,
    lib_root,
    list_library,
    publish_cell,
)
from spicexplorer_core.workspace.manifest import (
    MANIFEST_NAME,
    SCHEMA_VERSION,
    new_manifest,
    read_manifest,
    upgrade_manifest,
    write_manifest,
)
from spicexplorer_core.workspace.migrate import (
    is_project_dir,
    migrate_project,
    migrate_workspace,
)
from spicexplorer_core.workspace.project_md import (
    append_decision,
    read_decisions,
    render_project_md,
)
from spicexplorer_core.workspace.promote import (
    current_promotion,
    list_promotions,
    promote,
)
from spicexplorer_core.workspace.retention import (
    DEFAULT_GRACE_S,
    RETENTION_TIERS,
    iter_candidates,
    prune_run,
    prune_workspace,
)
from spicexplorer_core.workspace.runs import (
    ENVELOPE_VERSION,
    envelope_fields,
    mint_run_dir,
    new_run_id,
    owner_is_dead,
    project_objects_dir,
    read_run_record,
    snapshot_inputs,
    touch_heartbeat,
    write_run_record,
)
from spicexplorer_core.workspace.state import (
    STATE_NAME,
    build_state,
    read_state,
    rebuild_state,
    write_state,
)
from spicexplorer_core.workspace.verify import (
    AGGREGATES,
    Spec,
    Target,
    VerifyPlan,
    load_targets,
    load_verify_plan,
    parse_target,
)

__all__ = [
    "PROJECT_DIRS_V2",
    "SHARED_DIRS",
    "scaffold_project",
    "scaffold_shared",
    "shared_root",
    "work_root",
    "MANIFEST_NAME",
    "SCHEMA_VERSION",
    "new_manifest",
    "read_manifest",
    "upgrade_manifest",
    "write_manifest",
    "is_project_dir",
    "migrate_project",
    "migrate_workspace",
    "ENVELOPE_VERSION",
    "envelope_fields",
    "mint_run_dir",
    "new_run_id",
    "owner_is_dead",
    "project_objects_dir",
    "read_run_record",
    "snapshot_inputs",
    "touch_heartbeat",
    "write_run_record",
    "RETENTION_TIERS",
    "DEFAULT_GRACE_S",
    "prune_run",
    "prune_workspace",
    "iter_candidates",
    "AGGREGATES",
    "Spec",
    "Target",
    "VerifyPlan",
    "load_targets",
    "load_verify_plan",
    "parse_target",
    "STATE_NAME",
    "build_state",
    "read_state",
    "write_state",
    "rebuild_state",
    "promote",
    "current_promotion",
    "list_promotions",
    "read_curated",
    "write_curated",
    "merge_proposal",
    "merge_curated",
    "publish_cell",
    "import_cell",
    "list_library",
    "lib_root",
    "append_decision",
    "read_decisions",
    "render_project_md",
]
