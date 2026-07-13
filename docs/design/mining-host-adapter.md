# Mining HOST adapter — scoping (rung 3)

> **Status:** `plan` · lane: game-mining · 2026-07-12
>
> Scoping doc for **rung 3** of the mining ladder — the HOST adapter (the
> superbot-next `SubsystemManifest` plugin binding). It captures the **binding**
> plugin contract's minimum export shape (studied read-only from the
> `menno420/superbot-next` clone), states plainly what is and is not required,
> renders a **verdict** on buildability, and raises a **⚑ owner/lab decision**
> (the packaging + hermeticity build-model change) that must be signed off before
> ANY host-adapter code lands. This doc contains **no code** and invents **no
> balance numbers**.

---

## ⚑ OWNER / LAB DECISION REQUIRED (read this first)

Building a rung-3 host-adapter — even a decorative panel-only skeleton — forces
a **substantive change to superbot-games' build model**, not a rename:

- **⚑ PACKAGING + HERMETICITY.** To be a conforming plugin, superbot-games must
  become an **installable Python distribution** declaring
  `[project.entry-points."sb.plugins"]` (it ships **no** `pyproject.toml` /
  `setup.py` / `setup.cfg` today, §4), AND its MANIFEST module must import
  `sb.spec.*` from **superbot-next** — pulling a second repo into sbg's currently
  **stdlib-only hermetic CI** (§6). Turning sbg into a package and importing the
  host kernel into its hermetic test baseline is a build-model decision that
  needs **owner/lab sign-off before any host-adapter code (skeleton or full)**.

Everything below §5 (the verdict and next slice) is **blocked on this decision.**
Until it is ratified, rung 3 is *scoped-and-flagged, not built.*

---

## 1. Status / provenance

This is a scoping doc for **rung 3 (the HOST adapter)** of the mining ladder. The
ladder is three rungs, per `games/mining/__init__.py` and
`docs/design/mining-plugin-layout.md`:

```
PURE CORE  →  WORKFLOW (audited seam)  →  HOST adapter
(shipped)     (rung 2, scoped + ⚑)        (this doc scopes it, rung 3)
```

- **PURE CORE** — shipped: `games/mining/core/`, 19 stdlib-only modules.
- **WORKFLOW (audited seam)** — rung 2, scoped in `docs/design/mining-workflow-seam.md`,
  intended at `services/mining_workflow.py`; **parked** on the `⚑ D1 / D2`
  audit-schema owner/lab decision.
- **HOST adapter** — rung 3 (this doc), the superbot-next `SubsystemManifest`
  plugin binding against the plugin contract now **defined and binding**.

The plugin contract below was studied from the **read-only** clone of
`menno420/superbot-next` on **2026-07-12**, from `docs/game-plugin-contract.md`
(status **`binding`**, owner decision 2026-07-09). The file
was read at superbot-next **HEAD `60c01574`**; the coordinator cited pin
`d3dba9b` (not reachable in a depth-1 clone), so the content read here is
**authoritative-current** — cited by file (`superbot-next docs/game-plugin-contract.md`) as read at `60c01574`.
`menno420/superbot-next` is never written to.

## 2. The binding contract — minimum export shape (verbatim copy-source)

A conforming plugin (contract §1) is an **installable Python distribution** that
exports **pure declarations + ref registrations** — the same discipline as an
in-tree `sb/manifest/<key>.py` module, just packaged out of tree. The minimum
export shape:

```toml
# pyproject.toml (plugin repo)
[project.entry-points."sb.plugins"]
<name> = "<package>.manifest"        # the module the host imports
```

- The entry-point value points at a **module** that declares
  `MANIFEST = SubsystemManifest(...)` (or a `MANIFESTS` tuple).
- The module registers every callable its specs reference through the
  `sb.spec.refs` decorators — `@handler` / `@panel` / `@workflow` / `@provider`.
- It exposes an **idempotent `ENSURE_REFS`** hook (the in-tree P1 re-arm
  contract: decorators run at first import only; the compiler's test seam may
  clear the ref table without evicting module caches).
- **"Importing the module IS reserving"** — the host performs the import and
  never executes anything else from the plugin.

### KEY FINDING — `@workflow` is NOT required

The minimum shape lists four ref decorators, but **none of them is mandatory**;
which appear depends on the facets declared. Contract §2 allows these
`SubsystemManifest` facets in v1: **commands, panels, settings (+ bindings),
events, capabilities.** The working exemplar `examples/superbot-plugin-hello/` is
**panel-only** — it declares **one `@panel`** (`hello.home`) and **one
`CommandSpec`** whose `route` is a `PanelRef(PANEL_ID)`, with **no `@workflow`**
and **no `@handler`**. Its `pyproject.toml` declares
`hello = "superbot_plugin_hello.manifest"` under `[project.entry-points."sb.plugins"]`,
and its `MANIFEST` carries `commands=(CommandSpec(..., route=PanelRef(PANEL_ID)))`
plus `panels=(hello_home_spec(),)`. A plugin can therefore be conforming while
routing a command straight at a panel.

The one constraint that *does* bind mining: contract §3 says **route mutating
commands at a `WorkflowRef` the plugin registers** — the audited K7 engine
(audit rows, outbox, confirm gates) is inherited, never reimplemented. So a
*read-only / decorative* plugin can be panel-only, but any **state-changing**
command (mining's `mine` / `harvest` / `explore`) must route through a
`WorkflowRef`, i.e. through the rung-2 workflow op.

## 3. Host discovery + pin lifecycle

The host side is `sb/app/plugin_host.py` + `tools/plugin_pin.py` + the committed
`plugins.lock.json` (contract §5; host code confirmed at superbot-next
`60c01574`):

- **Discovery** — `discover_plugins()` scans entry points via
  `importlib.metadata.entry_points(group="sb.plugins")` and imports each module.
  The import IS ref registration — no other plugin code runs.
- **Hash** — `manifest_stable_hash(manifests)` returns
  `sha256:<digest>`, a sha256 over the **canonical JSON** of the serialized
  manifest (the same P8 `serialize_manifest` + `canonical_json` mechanics the
  in-tree snapshot uses, scoped to the plugin).
- **Verdicts** — `load_plugins()`: installed-but-**unpinned** or pin/installed
  **hash drift** ⇒ `FAILED_STARTUP (plugin_gate)` (the plugin twin of boot-gate
  leg-A DRIFT). **Pinned-but-not-installed** ⇒ warning + **skip**, never fatal —
  the registry is an allowlist ceiling, so hermetic CI and plugin-free containers
  boot unchanged.
- **Lock ownership** — `plugins.lock.json` lives in the **HOST repo**
  (superbot-next root — the plugin twin of `manifest.snapshot.json`), written by
  `python3 tools/plugin_pin.py --write` against the **installed** plugin set
  (facet fence + one joint `compile_manifests` pass over host+plugins). Contract
  §5: **"the pin diff is the reviewable artifact"** — committed via a **HOST PR**.

**The exemplar template.** `examples/superbot-plugin-hello/` is the complete
package the contract points sbg at: a `pyproject.toml` with the `sb.plugins`
entry-point and no runtime deps (the host process provides `sb`), a **panel-only**
`SubsystemManifest`, and a host-side pin in `plugins.lock.json`. It is the shape a
mining adapter would mirror.

## 4. superbot-games readiness gaps

Measured at sbg HEAD `fbf5202`:

- **Not an installable package.** There is **no** `pyproject.toml` /
  `setup.py` / `setup.cfg` anywhere in the repo — sbg cannot currently declare an
  `sb.plugins` entry-point at all.
- **No `sb` surface.** No `import sb`, no `sb.plugins` reference, no MANIFEST
  module, no `SubsystemManifest` — the only host-adapter mention is the
  `games/mining/__init__.py` docstring naming it **"(named-next)"**.
- **No workflow layer.** No `services/mining_workflow.py` and no `services/`
  directory; mining's shipped surface is **PURE CORE ONLY** (`games/mining/core/`,
  19 stdlib-only modules, purity-guarded).
- **The seam is the workflow op, not the core.** `docs/design/mining-plugin-layout.md`
  §3: a handler wraps a workflow op run via `engine.run(WorkflowRef("mining.mine"), ctx)`
  and **"the pure core is never imported by the host directly — the workflow op
  is the seam."** A host adapter therefore has **nothing to wrap** until rung 2
  exists.

## 5. Verdict — PARTIALLY buildable, with a split

Buildability splits cleanly in two:

- **(A) A panel-only contract-proving skeleton is technically buildable
  INDEPENDENT of rung 2.** The contract allows panel-only plugins (§2, KEY
  FINDING); a mining adapter could declare one `@panel` + a `CommandSpec`
  routing to it via `PanelRef`, mirroring the hello exemplar, with **no
  `@workflow`**. This wraps **no mining core** — it is a decorative proof of the
  entry-point → pin → boot path.
- **(B) A MEANINGFUL mining adapter wrapping mutating ops
  (`mine` / `harvest` / `explore`) is BLOCKED behind rung 2's workflow seam.**
  The contract requires mutating commands to route at a `WorkflowRef` (§3); that
  ref *is* the rung-2 workflow op (`services/mining_workflow.py`), which does not
  exist and is itself **parked on the `⚑ D1 / D2` audit-schema decision**
  (`docs/design/mining-workflow-seam.md`).

**The two-repo dependency chain** the meaningful adapter must clear:

```
rung 2 workflow op (parked ⚑ D1/D2, sbg)
      →  rung 3 mutating adapter (sbg: manifest routes command → WorkflowRef)
      →  HOST PR to pin (superbot-next: plugins.lock.json via tools/plugin_pin.py --write)
```

## 6. Three preconditions even skeleton (A) must clear

This is *why* the verdict is only "partial" — even the decorative skeleton is not
free:

- **(i) PACKAGING.** sbg must add a `pyproject.toml` declaring
  `[project.entry-points."sb.plugins"] mining = "<package>.manifest"`. This is a
  **real build-model change** — sbg becomes an installable distribution — not a
  file rename.
- **(ii) HERMETICITY.** Importing the MANIFEST module pulls `sb.spec.*` (manifest
  grammar, panel specs, refs decorators) from **superbot-next** into sbg's
  **currently stdlib-only hermetic CI**. Either sbg adds a `superbot-next`
  dev-dependency plus a skip-if-not-installed guard on the manifest test, or the
  hermetic test baseline breaks. (The contract's pinned-not-installed → warn+skip
  verdict, §3, is the host-side analogue; sbg's CI needs its own skip discipline.)
- **(iii) HOST-OWNED PIN.** `plugins.lock.json` closes in **superbot-next** via a
  **host PR** — **sbg-the-plugin cannot pin itself.** The full
  pin → lock → boot-verify binding therefore spans **two repos**, so even the
  skeleton's contract proof is not completable inside superbot-games alone.

## 7. Recommendation

**Build order:**

1. **Ratify the rung-2 `⚑ D1 / D2` audit-schema decision** (owner/lab).
2. **Build the rung-2 workflow seam** (`services/mining_workflow.py`) — the
   `WorkflowRef` mutating commands route at.
3. **Then build the rung-3 adapter** wrapping the workflow op, **plus a
   superbot-next host PR** to pin it in `plugins.lock.json`.

**Defer the panel-only skeleton (A).** It wraps no core, forces packaging +
hermeticity (preconditions i + ii) for a **decorative** panel, and **cannot close
the pin in-repo** (precondition iii). There is no honest reason to change sbg's
build model for a panel that proves plumbing but routes to nothing — build the
adapter when there is a **real workflow op to wrap**.

## 8. Why this is a scoping doc, not a skeleton

A born-red host-adapter skeleton would either (a) wrap the rung-2 workflow op —
which **does not exist and is parked** on `⚑ D1 / D2` — or (b) ship a
panel-only decorative plugin that wraps nothing yet still forces superbot-games
to become an installable package and to import superbot-next into its hermetic
stdlib-only CI. Both paths make a **build-model commitment** (packaging +
hermeticity) that is an owner/lab call, not a self-initiated default — and the
pin that would *prove* either can only close in the host repo. So this session
scopes the rung and raises the `⚑` packaging/hermeticity decision; the build
follows ratification of both that decision and rung-2's `⚑ D1 / D2`.

---

_Ladder / provenance references: `games/mining/__init__.py`;
`docs/design/mining-plugin-layout.md`; `docs/design/mining-workflow-seam.md`
(rung-2 scoping, parked ⚑ D1/D2); superbot-next
`docs/game-plugin-contract.md` (status `binding`, owner decision
2026-07-09; read at superbot-next HEAD `60c01574`; coordinator cited pin
`d3dba9b`), host `sb/app/plugin_host.py`, `tools/plugin_pin.py`,
`plugins.lock.json`, and exemplar `examples/superbot-plugin-hello/` (read-only
clone of `menno420/superbot-next`)._
