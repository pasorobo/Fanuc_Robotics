# Documentation Handbook Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a comprehensive, beginner-friendly handbook for the Fanuc CRX-10iA/L workcell project that consolidates concepts, architecture, references, decision records, and operational checklists across all milestones (M0-M3 completed, M4-M7 planned).

**Architecture:** Add 19 Markdown documents organized into five tiers (Tier 0 concepts / Tier 1 onboarding / Tier 2 reference / Tier 3 ADRs / Tier 4 operations) plus an updated top-level README. Each tier sits under a topical subdirectory of `docs/`. SVG diagrams live under `docs/diagrams/` and are referenced from Markdown by relative path. ADRs use Michael Nygard format with `0001-...`-style filenames so adr-tools can be adopted later without rename.

**Tech Stack:** Markdown (CommonMark), inline SVG XML, Python 3 (for documentation quality script), git, GitHub-flavored Markdown features (tables, fenced code blocks). No ROS 2 build dependency for documentation itself.

---

## Scope

This plan implements project-wide documentation across five tiers:

- Tier 0 (Concepts): hardware overview, software overview, glossary, system block diagram.
- Tier 1 (Immediate Value): quickstart, architecture overview, troubleshooting from M0-M3 history.
- Tier 2 (Reference): frame conventions, services/launches catalog, YAML schemas.
- Tier 3 (ADR): five decision records plus an index.
- Tier 4 (Operations): hardware inputs intake, ROBOGUIDE setup checklist, hardware bringup checklist.
- README integration making the new docs discoverable from the project root.

This plan does not implement M4-M7 features. The Tier 4 operational documents prepare for M6/M7 by structuring the inputs needed, but they do not perform any controller, network, or hardware action.

## Design Decisions

- File layout under `docs/`:
  - `docs/concepts/` for Tier 0
  - `docs/diagrams/` for SVG assets
  - `docs/decisions/` for Tier 3 ADRs
  - `docs/operations/` for Tier 4 procedures
  - `docs/quickstart.md`, `docs/architecture.md`, `docs/troubleshooting.md`, `docs/frames.md`, `docs/services_and_launches.md`, `docs/yaml_schemas.md` directly under `docs/`.
- Markdown style: ATX headings, fenced code blocks with language hints, tables for matrices, hyperlinks via `[text](relative/path)`.
- ADR template: Michael Nygard four-section structure (Status, Context, Decision, Consequences) with one `Date` line under Status.
- ADR filenames: `0001-<kebab-title>.md` so adr-tools can be adopted later.
- ADR index: a `docs/decisions/README.md` maintained manually now; the structure mirrors `adr generate toc` output for easy migration.
- SVG: hand-authored SVG XML, embedded by relative-path reference (`![alt](../diagrams/<file>.svg)`), not inlined in Markdown.
- Existing files preserved without rewrites:
  - `docs/setup/ubuntu22_humble.md` is referenced from new docs but its content is not duplicated.
  - `docs/gripper_frames.md` is superseded by `docs/frames.md`. The older file is kept and gains a single-line redirect comment that points to the new file. No git move; preserve history with a normal edit.
- Documentation quality discipline: a Python script `scripts/check_docs.py` runs after each Task and verifies (a) Markdown fenced-block balance, (b) all referenced internal links resolve, (c) all referenced SVG files exist. This is the "test" layer for documentation, mirroring the source-contract pytests used in M2/M3.
- Commit granularity: one commit per document. `scripts/check_docs.py` itself is added in Task 0 with its own commit.
- Branch: `docs/handbook` from `m3-fixed-pick-place` HEAD. Push remote: `origin/docs/handbook`.

## File Structure

Create these files:

```text
scripts/check_docs.py
docs/diagrams/system_block_diagram.svg
docs/diagrams/hardware_axes.svg
docs/diagrams/software_layers.svg
docs/diagrams/architecture_layers.svg
docs/diagrams/package_dependencies.svg
docs/diagrams/frame_tree.svg
docs/diagrams/grasp_axes.svg
docs/diagrams/c1_contract.svg
docs/concepts/hardware_overview.md
docs/concepts/software_overview.md
docs/concepts/glossary.md
docs/concepts/system_block_diagram.md
docs/quickstart.md
docs/architecture.md
docs/troubleshooting.md
docs/frames.md
docs/services_and_launches.md
docs/yaml_schemas.md
docs/decisions/README.md
docs/decisions/0001-adopt-ubuntu22-humble.md
docs/decisions/0002-use-fanuc-official-driver.md
docs/decisions/0003-fake-gripper-as-runtime-scene-owner.md
docs/decisions/0004-mtc-without-task-execute.md
docs/decisions/0005-cell-xacro-as-single-robot-description.md
docs/operations/hardware_inputs.md
docs/operations/roboguide_setup_checklist.md
docs/operations/hardware_bringup_checklist.md
```

Modify these files:

```text
README.md
docs/gripper_frames.md
```

Total new documentation files: 19 Markdown + 8 SVG + 1 quality script = 28. Plus 2 modifications.

## SVG Diagram Catalog

The plan produces 8 hand-authored SVGs. Each is referenced from one or more Markdown docs.

| File | Used in | Content |
|---|---|---|
| `system_block_diagram.svg` | concepts/system_block_diagram.md | Linux PC, R-30iB controller, CRX-10iA/L robot, gripper, camera, Ethernet links between PC and controller, controller to robot cable, controller to camera, gripper IO line |
| `hardware_axes.svg` | concepts/hardware_overview.md | CRX-10iA/L outline with J1-J6 joint indicators and base/tool0/flange labels |
| `software_layers.svg` | concepts/software_overview.md | Stack from FANUC controller -> FANUC ROS 2 driver -> ros2_control -> MoveIt 2 -> MTC -> task layer; side branch to Gazebo Fortress -> gz_ros2_control |
| `architecture_layers.svg` | architecture.md | Four layers from design §8: Task / Planning / Control adapter / Execution; arrows showing dataflow |
| `package_dependencies.svg` | architecture.md | Boxes for each `crx10ial_*` package + relevant FANUC upstream package, with depend arrows |
| `frame_tree.svg` | frames.md, concepts/hardware_overview.md | Tree from world down to grasp_link, including mock_scene world objects (table, work_object, camera_stand) |
| `grasp_axes.svg` | frames.md, decisions/0003 | grasp_link with +X approach / +Y jaw / +Z up colour-coded |
| `c1_contract.svg` | decisions/0003, architecture.md, troubleshooting.md | Two PlanningScene entities (MTC internal vs runtime), with fake_gripper as the only writer to runtime; MTC stages writing only to internal |

Each Task that produces an SVG includes the full SVG XML in a fenced block. SVGs are intentionally small (<= 100 lines each) and stylistically consistent: white background, `viewBox="0 0 800 500"` baseline, sans-serif text via `font-family="sans-serif"`, stroke widths 1.5-2px, colour palette from `#1f3a93`, `#27ae60`, `#c0392b`, `#7f8c8d`, `#000`.

## Documentation Quality Check Script

`scripts/check_docs.py` is the gate for every documentation commit. It runs offline (no ROS) and exits non-zero on failure. Capabilities:

1. Walk `docs/**/*.md` and the top-level `README.md`.
2. For each Markdown file, balance fenced code blocks using the same CommonMark rule used for plan-fence checks: an opener of length N is closed only by a line that is exactly N or more backticks with no info string.
3. Resolve `[text](relative/path)` links that point into the repository (paths starting with `./`, `../`, or no scheme). Verify the target file exists. Report unresolved.
4. Resolve `![alt](path.svg)` image references the same way.
5. For each ADR file under `docs/decisions/0*.md`, require the four section headings: `## Status`, `## Context`, `## Decision`, `## Consequences`.
6. Print a summary and exit with `0` on success or `1` on any failure.

Each Task that creates or modifies documentation invokes `python3 scripts/check_docs.py` immediately before commit.

## Task 0: Branch Baseline and Documentation Quality Script

**Files:**
- Create: `scripts/check_docs.py`

- [ ] **Step 1: Confirm branch and baseline**

Run:

```bash
git status --short --branch
git branch --show-current
git rev-parse HEAD
```

Expected:

```text
## docs/handbook
docs/handbook
95ec8153e512d3bec5a5dd43a151cc3a47da9724
```

If the branch is missing, run:

```bash
git switch m3-fixed-pick-place
git switch -c docs/handbook
```

- [ ] **Step 2: Create `scripts/check_docs.py`**

Create `scripts/check_docs.py`:

```python
#!/usr/bin/env python3
"""Documentation handbook quality gate.

Verifies fenced-block balance, internal link resolution, SVG references,
and ADR section headings. Run before every docs commit.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
DOCS_ROOT = REPO_ROOT / "docs"
ADR_DIR = DOCS_ROOT / "decisions"

LINK_RE = re.compile(r"(?<!\!)\[[^\]]+\]\(([^)]+)\)")
IMAGE_RE = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")
FENCE_RE = re.compile(r"^(`{3,})(.*)$")
ADR_REQUIRED_SECTIONS = ("## Status", "## Context", "## Decision", "## Consequences")


def iter_markdown_files() -> List[Path]:
    paths = sorted(DOCS_ROOT.rglob("*.md"))
    paths.append(REPO_ROOT / "README.md")
    return [p for p in paths if p.exists()]


def check_fences(path: Path) -> List[str]:
    errors: List[str] = []
    stack: List[Tuple[int, int]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        match = FENCE_RE.match(line.rstrip("\n"))
        if not match:
            continue
        flen = len(match.group(1))
        info = match.group(2).strip()
        if stack:
            top_line, top_len = stack[-1]
            if info == "" and flen >= top_len:
                stack.pop()
        else:
            stack.append((lineno, flen))
    for opened_line, length in stack:
        errors.append(f"{path}:{opened_line}: unclosed fence (length {length})")
    return errors


def check_internal_link(path: Path, target: str) -> List[str]:
    if target.startswith(("http://", "https://", "mailto:", "#")):
        return []
    bare = target.split("#", 1)[0].split("?", 1)[0]
    if not bare:
        return []
    resolved = (path.parent / bare).resolve()
    if not resolved.exists():
        return [f"{path}: link target does not exist: {target}"]
    return []


def check_links_and_images(path: Path) -> List[str]:
    errors: List[str] = []
    text = path.read_text(encoding="utf-8")
    for match in LINK_RE.finditer(text):
        errors.extend(check_internal_link(path, match.group(1)))
    for match in IMAGE_RE.finditer(text):
        errors.extend(check_internal_link(path, match.group(1)))
    return errors


def check_adr_sections(path: Path) -> List[str]:
    if path.parent != ADR_DIR or not path.name[0].isdigit():
        return []
    text = path.read_text(encoding="utf-8")
    missing = [section for section in ADR_REQUIRED_SECTIONS if section not in text]
    return [f"{path}: ADR missing section: {section}" for section in missing]


def main() -> int:
    failures: List[str] = []
    files = iter_markdown_files()
    for path in files:
        failures.extend(check_fences(path))
        failures.extend(check_links_and_images(path))
        failures.extend(check_adr_sections(path))

    if failures:
        for failure in failures:
            print(f"FAIL {failure}", file=sys.stderr)
        print(f"\n{len(failures)} documentation issue(s) found", file=sys.stderr)
        return 1

    print(f"check_docs ok ({len(files)} markdown files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

Make it executable:

```bash
chmod +x scripts/check_docs.py
```

- [ ] **Step 3: Run the script against the existing repo**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0` and prints a count of files scanned. Any failures here indicate pre-existing doc issues that must be fixed before continuing.

- [ ] **Step 4: Commit the quality script**

Run:

```bash
git add scripts/check_docs.py
git commit -m "tooling: add documentation quality gate"
```

Expected: commit succeeds.

## Task 1: Concepts - Hardware Overview

**Files:**
- Create: `docs/diagrams/hardware_axes.svg`
- Create: `docs/diagrams/system_block_diagram.svg`
- Create: `docs/concepts/hardware_overview.md`

- [ ] **Step 1: Create `docs/diagrams/hardware_axes.svg`**

Create `docs/diagrams/hardware_axes.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" font-family="sans-serif" font-size="14">
  <rect width="800" height="500" fill="white"/>
  <text x="400" y="30" text-anchor="middle" font-size="18" font-weight="bold">FANUC CRX-10iA/L Joint Layout</text>
  <g stroke="#1f3a93" stroke-width="2" fill="none">
    <rect x="320" y="380" width="160" height="40" rx="4"/>
    <line x1="400" y1="380" x2="400" y2="320"/>
    <circle cx="400" cy="320" r="14" fill="#27ae60"/>
    <line x1="400" y1="320" x2="400" y2="240"/>
    <circle cx="400" cy="240" r="14" fill="#27ae60"/>
    <line x1="400" y1="240" x2="500" y2="200"/>
    <circle cx="500" cy="200" r="14" fill="#27ae60"/>
    <line x1="500" y1="200" x2="600" y2="180"/>
    <circle cx="600" cy="180" r="14" fill="#27ae60"/>
    <line x1="600" y1="180" x2="660" y2="160"/>
    <circle cx="660" cy="160" r="14" fill="#27ae60"/>
    <line x1="660" y1="160" x2="700" y2="150"/>
    <circle cx="700" cy="150" r="14" fill="#27ae60"/>
    <line x1="700" y1="150" x2="730" y2="145"/>
  </g>
  <g fill="#000">
    <text x="400" y="445" text-anchor="middle">base_link</text>
    <text x="412" y="324">J1</text>
    <text x="412" y="244">J2</text>
    <text x="512" y="204">J3</text>
    <text x="612" y="184">J4</text>
    <text x="672" y="164">J5</text>
    <text x="712" y="154">J6</text>
    <text x="745" y="148">flange / tool0</text>
  </g>
  <g stroke="#c0392b" stroke-width="1.5" fill="#c0392b">
    <line x1="730" y1="145" x2="780" y2="145" marker-end="url(#arrow)"/>
    <line x1="730" y1="145" x2="730" y2="95" marker-end="url(#arrow)"/>
    <text x="785" y="148" font-size="12">+X tool</text>
    <text x="700" y="92" font-size="12">+Z tool</text>
  </g>
  <defs>
    <marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 z" fill="#c0392b"/>
    </marker>
  </defs>
  <text x="60" y="470" font-size="12" fill="#7f8c8d">Reach 1.249 m. Payload 10 kg. Repeatability +/-0.04 mm.</text>
</svg>
```

- [ ] **Step 2: Create `docs/diagrams/system_block_diagram.svg`**

Create `docs/diagrams/system_block_diagram.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 520" font-family="sans-serif" font-size="14">
  <rect width="900" height="520" fill="white"/>
  <text x="450" y="32" text-anchor="middle" font-size="18" font-weight="bold">CRX-10iA/L Workcell System Block Diagram</text>
  <g stroke="#1f3a93" stroke-width="2" fill="#eaf0ff">
    <rect x="40" y="80" width="220" height="120" rx="6"/>
    <rect x="340" y="80" width="220" height="120" rx="6"/>
    <rect x="640" y="80" width="220" height="120" rx="6"/>
    <rect x="340" y="280" width="220" height="80" rx="6"/>
    <rect x="40" y="280" width="220" height="80" rx="6"/>
    <rect x="640" y="280" width="220" height="80" rx="6"/>
  </g>
  <g fill="#000">
    <text x="150" y="110" text-anchor="middle" font-weight="bold">Linux PC</text>
    <text x="150" y="135" text-anchor="middle" font-size="12">Ubuntu 22.04</text>
    <text x="150" y="153" text-anchor="middle" font-size="12">ROS 2 Humble</text>
    <text x="150" y="171" text-anchor="middle" font-size="12">MoveIt 2 / MTC</text>
    <text x="150" y="189" text-anchor="middle" font-size="12">crx10ial_* packages</text>

    <text x="450" y="110" text-anchor="middle" font-weight="bold">FANUC Controller</text>
    <text x="450" y="135" text-anchor="middle" font-size="12">R-30iB Mini Plus</text>
    <text x="450" y="153" text-anchor="middle" font-size="12">J519 Stream Motion</text>
    <text x="450" y="171" text-anchor="middle" font-size="12">R912 Remote Motion</text>
    <text x="450" y="189" text-anchor="middle" font-size="12">iRVision (optional)</text>

    <text x="750" y="110" text-anchor="middle" font-weight="bold">CRX-10iA/L Robot</text>
    <text x="750" y="135" text-anchor="middle" font-size="12">6 axes</text>
    <text x="750" y="153" text-anchor="middle" font-size="12">Reach 1.249 m</text>
    <text x="750" y="171" text-anchor="middle" font-size="12">Payload 10 kg</text>
    <text x="750" y="189" text-anchor="middle" font-size="12">Tool flange</text>

    <text x="150" y="305" text-anchor="middle" font-weight="bold">Teach Pendant</text>
    <text x="150" y="328" text-anchor="middle" font-size="12">DCS, Safety, Operator UI</text>

    <text x="450" y="305" text-anchor="middle" font-weight="bold">Gripper</text>
    <text x="450" y="328" text-anchor="middle" font-size="12">Parallel jaw / vacuum</text>
    <text x="450" y="346" text-anchor="middle" font-size="12">Driven by DO/DI</text>

    <text x="750" y="305" text-anchor="middle" font-weight="bold">Camera</text>
    <text x="750" y="328" text-anchor="middle" font-size="12">iRVision target</text>
    <text x="750" y="346" text-anchor="middle" font-size="12">External RGB-D (future)</text>
  </g>
  <g stroke="#27ae60" stroke-width="2" fill="none" marker-end="url(#arrow2)">
    <line x1="260" y1="140" x2="340" y2="140"/>
    <line x1="560" y1="140" x2="640" y2="140"/>
    <line x1="450" y1="200" x2="450" y2="280"/>
    <line x1="450" y1="200" x2="150" y2="280"/>
    <line x1="450" y1="200" x2="750" y2="280"/>
  </g>
  <g fill="#27ae60" font-size="12">
    <text x="300" y="135">Ethernet</text>
    <text x="600" y="135">cable</text>
    <text x="465" y="245">DI/DO + iRVision</text>
  </g>
  <defs>
    <marker id="arrow2" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 z" fill="#27ae60"/>
    </marker>
  </defs>
  <text x="450" y="490" text-anchor="middle" font-size="12" fill="#7f8c8d">ROS 2 is not safety-rated. Safety is owned by FANUC controller, DCS, and pendant.</text>
</svg>
```

- [ ] **Step 3: Create `docs/concepts/hardware_overview.md`**

Create `docs/concepts/hardware_overview.md`. Required sections and key facts to include:

````markdown
# Hardware Overview

This document describes the physical hardware that the project targets.

## Robot

The target robot is the FANUC CRX-10iA/L collaborative robot.

- 6 articulated axes (J1, J2, J3, J4, J5, J6).
- Reach: 1.249 m.
- Payload: 10 kg.
- Repeatability: +/-0.04 mm.
- Mass: ~40 kg.
- Cooperative speed limit at force-sensitive operation.

![CRX-10iA/L joint layout](../diagrams/hardware_axes.svg)

The robot exposes several frames that ROS 2 cares about:

- `world` - workspace root, attached to the cell base.
- `base_link` - robot base.
- `J1`..`J6` link frames.
- `flange` - mechanical interface for tool attachment.
- `tool0` - FANUC default tool frame at flange.
- Project-specific extensions: `end_effector`, `tool_link`, `grasp_link` (see [frames.md](../frames.md)).

## Controller

The controller is the FANUC R-30iB Mini Plus or equivalent.

Relevant software options for ROS 2 integration:

- **J519 Stream Motion** - high-rate joint streaming. Required by the FANUC ROS 2 driver for trajectory execution.
- **R912 Remote Motion Interface (RMI)** - command and status path used by the driver.
- **S636 External Control Package** - alternative external command path.
- **iRVision** - FANUC built-in vision system. Used in the project as a controller-side feature; see [decisions/0003](../decisions/0003-fake-gripper-as-runtime-scene-owner.md) for ownership boundary.

The Teach Pendant is the operator interface and is the source of authority for safety. Dual Check Safety (DCS) and reduced-speed mode are configured here, not in ROS 2.

## I/O and Registers

FANUC controllers expose several data spaces:

- **Digital I/O** - DI[] (input), DO[] (output). Used for triggers and status.
- **Analog I/O** - AI[], AO[].
- **Group I/O** - GI[], GO[]. Bundles of digital lines.
- **Robot I/O** - RI[], RO[]. Robot-specific lines (handshake bits).
- **Numeric registers** - R[]. Integer or real values for program control.
- **Position registers** - PR[]. Stored Cartesian or joint poses.

iRVision results are typically published into R[] and PR[] by a TP program after image processing.

## Network

The Linux ROS 2 host and the controller communicate over Ethernet. Required:

- A static IP for the robot, reachable from the ROS 2 PC.
- Subnet that does not collide with other engineering networks.
- Firewall openings for J519 / RMI ports as documented by FANUC.

See [system block diagram](system_block_diagram.md) for the high-level layout.

## Safety

ROS 2 is not safety-rated in this project. Authority for stopping the robot, enforcing speed limits, and validating payload remains with:

- The FANUC controller and its DCS configuration.
- The Teach Pendant operator.
- An external emergency stop integrated into the cell.

ROS 2 application code may add convenience guards (workspace limits, recovery flows) but those are not safety functions. See [decisions/0001](../decisions/0001-adopt-ubuntu22-humble.md) and the project safety section in operations docs.
````

- [ ] **Step 4: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`. Internal links to `frames.md`, `decisions/0001-...md`, `decisions/0003-...md`, `system_block_diagram.md` will fail at this point because those files do not exist yet.

If the script fails on those expected-missing links, comment them out or remove the link wrapper temporarily and add them back in the Task that creates the target. Alternative: tolerate the failure during this task and re-run the script after Task 16. Decide on tolerance policy:

- Adopt strict mode: only commit when `check_docs.py` returns `0`. To achieve this in Task 1, replace not-yet-created link targets with plain bracketed text (e.g. `[frames.md](../frames.md)` -> `frames.md`) and convert them back to links in the final integration Task.

- Adopt lenient mode for Tier 0: accept link failures pointing only to filenames listed in this plan's File Structure section.

This plan adopts the strict mode. Therefore in Step 3 above, write the Markdown without the `[name](path)` wrappers for files that do not yet exist; use plain text. The wrappers are restored in Task 20 (README integration) where every target file exists.

- [ ] **Step 5: Commit**

Run:

```bash
git add docs/diagrams/hardware_axes.svg docs/diagrams/system_block_diagram.svg docs/concepts/hardware_overview.md
git commit -m "docs: add hardware overview"
```

Expected: commit succeeds.

## Task 2: Concepts - Software Overview

**Files:**
- Create: `docs/diagrams/software_layers.svg`
- Create: `docs/concepts/software_overview.md`

- [ ] **Step 1: Create `docs/diagrams/software_layers.svg`**

Create `docs/diagrams/software_layers.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 540" font-family="sans-serif" font-size="14">
  <rect width="800" height="540" fill="white"/>
  <text x="400" y="32" text-anchor="middle" font-size="18" font-weight="bold">Software Stack Overview</text>
  <g stroke="#1f3a93" stroke-width="2" fill="#eaf0ff">
    <rect x="80" y="60" width="640" height="60" rx="6"/>
    <rect x="80" y="140" width="640" height="60" rx="6"/>
    <rect x="80" y="220" width="640" height="60" rx="6"/>
    <rect x="80" y="300" width="640" height="60" rx="6"/>
    <rect x="80" y="380" width="640" height="60" rx="6"/>
    <rect x="80" y="460" width="300" height="50" rx="6"/>
    <rect x="420" y="460" width="300" height="50" rx="6" fill="#fff5e6"/>
  </g>
  <g fill="#000" font-size="14">
    <text x="400" y="95" text-anchor="middle" font-weight="bold">Task layer</text>
    <text x="400" y="115" text-anchor="middle" font-size="12">crx10ial_tasks - MoveIt Task Constructor pipelines</text>
    <text x="400" y="175" text-anchor="middle" font-weight="bold">Planning layer</text>
    <text x="400" y="195" text-anchor="middle" font-size="12">MoveIt 2 - planning scene, kinematics, collision, OMPL</text>
    <text x="400" y="255" text-anchor="middle" font-weight="bold">Control adapter layer</text>
    <text x="400" y="275" text-anchor="middle" font-size="12">crx10ial_bringup launch, crx10ial_gripper, crx10ial_vision_bridge, crx10ial_safety</text>
    <text x="400" y="335" text-anchor="middle" font-weight="bold">ros2_control + Hardware abstraction</text>
    <text x="400" y="355" text-anchor="middle" font-size="12">controller_manager, joint_state_broadcaster, joint_trajectory_controller</text>
    <text x="400" y="415" text-anchor="middle" font-weight="bold">Execution backend</text>
    <text x="400" y="435" text-anchor="middle" font-size="12">FANUC ROS 2 driver / mock / Gazebo (future)</text>
    <text x="230" y="490" text-anchor="middle" font-weight="bold">URDF / xacro / SRDF</text>
    <text x="230" y="505" text-anchor="middle" font-size="12">crx10ial_cell_description</text>
    <text x="570" y="490" text-anchor="middle" font-weight="bold">Sim / Vision (future)</text>
    <text x="570" y="505" text-anchor="middle" font-size="12">Gazebo Fortress, gz_ros2_control, iRVision</text>
  </g>
</svg>
```

- [ ] **Step 2: Create `docs/concepts/software_overview.md`**

Create `docs/concepts/software_overview.md`:

````markdown
# Software Overview

This project runs on Ubuntu 22.04 with ROS 2 Humble. The software is layered to keep concerns separable: planning logic stays independent of which simulator or controller is on the other end.

![Software stack](../diagrams/software_layers.svg)

## ROS 2 Humble

ROS 2 Humble Hawksbill is the LTS distribution targeted at Ubuntu 22.04. Core concepts the rest of this document assumes the reader knows:

- **Node** - a process publishing/subscribing/serving ROS interfaces.
- **Topic** - typed asynchronous publish/subscribe channel.
- **Service** - synchronous request/response.
- **Action** - long-running goal/feedback/result.
- **Parameter** - per-node typed configuration.
- **Launch** - Python file that composes nodes, parameters, and includes.

The project uses `colcon` for building and `vcstool` for fetching upstream source dependencies. Both come from the standard ROS 2 install.

## URDF / xacro / SRDF

`crx10ial_cell_description` owns the workcell description.

- **URDF** is the rigid-body model: links, joints, meshes, masses, collision geometry.
- **xacro** is a templating layer over URDF; the cell composition uses `<xacro:macro>` and `<xacro:include>` to compose the FANUC robot description, the workcell environment (table, work object, camera stand), and the gripper.
- **SRDF** is MoveIt's semantic description: planning groups, named states, end-effector names, allowed-collision matrix overrides.

The cell xacro is the single source of truth for `robot_description`. It serves both MoveIt and ros2_control. See [decisions/0005](../decisions/0005-cell-xacro-as-single-robot-description.md).

## ros2_control

`ros2_control` is the standard hardware abstraction layer. Concepts:

- **Hardware Interface** - C++ plugin that exposes joints, sensors, and command interfaces. The FANUC driver provides one for the real and mock controllers.
- **Controller Manager** - `controller_manager` node that runs controllers.
- **Controllers** - `joint_state_broadcaster`, `joint_trajectory_controller`, `fanuc_gpio_controller`, `force_torque_sensor_broadcaster`, etc.

The mock launch starts the FANUC mock hardware interface plus all controllers needed for trajectory execution and status broadcasting.

## MoveIt 2

MoveIt 2 plans collision-free trajectories.

- **Planning scene** - the world MoveIt sees (robot state + collision objects).
- **Planning pipeline** - sampling-based (OMPL) or other.
- **`MoveGroupInterface`** - the C++/Python entry point for "plan and execute".
- **Kinematics solver** - IK plugin; FANUC ships a default solver.

The `move_group` node hosts the planner and exposes `/plan_kinematic_path`, `/execute_trajectory`, `/apply_planning_scene`, `/get_planning_scene`.

## MoveIt Task Constructor (MTC)

MTC orchestrates multi-stage tasks (pick, place, transit) on top of MoveIt 2. Concepts:

- **Stage** - one named planning step (`MoveTo`, `MoveRelative`, `Connect`, `ModifyPlanningScene`).
- **Container** - groups stages (`SerialContainer`, `Alternatives`, `Fallbacks`).
- **Solution** - one valid composition of stage results.

The project uses MTC apt binaries (`ros-humble-moveit-task-constructor-*`) for fixed pick/place planning. MTC's internal scene transitions (e.g., `ModifyPlanningScene::attachObject()`) update the planner's view but never the runtime planning scene; runtime scene writes are owned by `crx10ial_gripper` per [decisions/0003](../decisions/0003-fake-gripper-as-runtime-scene-owner.md).

## FANUC ROS 2 Driver

The FANUC ROS 2 driver provides:

- `fanuc_description` - URDF/xacro for FANUC robots including CRX-10iA/L.
- `fanuc_hardware_interface` - ros2_control hardware interface for both mock and real controllers.
- `fanuc_moveit_config` - MoveIt configuration package (SRDF, kinematics, planning).
- `fanuc_msgs` - shared messages.
- `fanuc_controllers` - FANUC-specific controllers (gpio, force sensor, scaled trajectory).

The driver is fetched via `vcs import` from `third_party.humble.repos`.

## Gazebo Fortress (planned for M4)

Gazebo Fortress is the LTS Ignition release supported on Ubuntu 22.04. The bridge to ROS 2 is `gz_ros2_control` plus `ros_gz_sim`. M4 introduces a Gazebo backend behind the same control adapter layer; nothing in the task or planning layer changes.

## iRVision (planned for M5/M6/M7)

iRVision is a FANUC controller feature, not a ROS 2 package. Integration uses controller-visible state: a TP program triggers the vision job, writes results to R[]/PR[], and `crx10ial_vision_bridge` reads them through the FANUC driver. Three backends share one `DetectObject` interface: `fake`, `sim` (Gazebo ground truth), `fanuc_irvision`.
````

- [ ] **Step 3: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0` if internal link targets that don't exist yet have been written as plain text instead of links. Apply strict mode: replace `[decisions/0003](../decisions/0003-...md)` with `decisions/0003` (plain text) until Task 20 reconnects the links.

- [ ] **Step 4: Commit**

Run:

```bash
git add docs/diagrams/software_layers.svg docs/concepts/software_overview.md
git commit -m "docs: add software overview"
```

Expected: commit succeeds.

## Task 3: Concepts - Glossary

**Files:**
- Create: `docs/concepts/glossary.md`

- [ ] **Step 1: Create `docs/concepts/glossary.md`**

Create `docs/concepts/glossary.md`. Use a flat alphabetical structure with short definitions. Include at minimum the following terms (one paragraph each):

````markdown
# Glossary

Short definitions for terms used across the project.

## A

**ACM (Allowed Collision Matrix)**
MoveIt's per-pair toggle of which links and objects are allowed to be in contact. Used during grasping to allow the gripper to touch the object.

**ament_cmake / ament_python**
ROS 2 package build types. `ament_cmake` is for C++ packages and packages that ship configuration files. `ament_python` is for pure-Python ROS 2 nodes. Each top-level project package picks one.

**ADR (Architecture Decision Record)**
A short Markdown document recording a single technical decision: why it was made, what was decided, and the trade-offs accepted. See `docs/decisions/`.

## C

**colcon**
The ROS 2 build tool. Builds the workspace from `src/` into `install/`.

**CommonMark**
The Markdown specification used by this repository's docs.

**Controller (ros2_control)**
A plugin that uses the hardware interface to drive a joint or sensor. Examples: `joint_trajectory_controller`, `joint_state_broadcaster`.

**CRX-10iA/L**
The FANUC collaborative robot the project targets. 6 axes, 1.249 m reach, 10 kg payload.

## D

**DCS (Dual Check Safety)**
FANUC's safety-rated subsystem on the controller. Independent of ROS 2.

**DI / DO / GI / GO / RI / RO**
FANUC controller I/O families. Digital In/Out, Group In/Out, Robot In/Out.

## E

**end_effector**
The link in this project's cell xacro that anchors gripper geometry. Sits between `flange` (FANUC) and `tool_link` (project).

## F

**fake_gripper**
The mock backend that owns runtime planning-scene attach/detach. See `docs/decisions/0003`.

**flange**
FANUC's mechanical tool mounting frame. Tools attach here.

## G

**Gazebo Fortress**
Ignition Fortress, the LTS simulator targeted by M4. Supports `gz_ros2_control`.

**grasp_link**
Project frame at which objects are attached during grasping. Convention: +X approach, +Y jaw opening, +Z up. See `docs/frames.md`.

**gz_ros2_control**
The Gazebo Fortress bridge to ros2_control.

## H

**Humble (Hawksbill)**
ROS 2 LTS release for Ubuntu 22.04. The project's primary target.

## I

**iRVision**
FANUC's built-in vision system. Runs on the controller. Results are exposed through I/O and registers.

## J

**J1..J6**
The six joints of the CRX-10iA/L, numbered from base to wrist.

**J519 Stream Motion**
FANUC software option that exposes high-rate joint streaming. Required by the FANUC ROS 2 driver.

## M

**MoveIt 2**
The motion-planning framework. Hosts the `move_group` node.

**MoveIt Task Constructor (MTC)**
Stage-based task orchestration on top of MoveIt 2. The project uses it for fixed pick/place.

**Mock mode**
Project run mode with no Gazebo, no ROBOGUIDE, and no physical robot. Uses FANUC's mock hardware interface.

## O

**OMPL**
The default motion-planning library MoveIt 2 uses for sampling-based planning.

## P

**PR[]**
Position register on the FANUC controller. Stores Cartesian or joint poses. Used by iRVision result readback when supported.

**Planning scene**
MoveIt's view of the world: robot state, world collision objects, attached collision objects, ACM.

## R

**R[]**
Numeric register on the FANUC controller. Used to pass scalar values such as iRVision result codes.

**R-30iB Mini Plus**
FANUC controller used with the CRX series.

**R912 Remote Motion Interface (RMI)**
FANUC software option for command/status remote control.

**ROBOGUIDE**
FANUC's Windows-only virtual controller and cell simulator. Used in M6 to validate the driver before real hardware.

**ros2_control**
ROS 2's standard hardware abstraction framework.

**rosdep**
ROS 2's dependency installer. Reads `package.xml` and installs system packages.

## S

**S636 External Control Package**
FANUC software option, alternative to J519/R912 for external command.

**SRDF**
MoveIt's Semantic Robot Description Format. Adds groups, end-effectors, named states on top of URDF.

## T

**Task (MTC)**
A MoveIt Task Constructor task: a tree of stages plus a planner. `Task::plan()` finds solutions; `Task::execute()` is intentionally not used in this project.

**Teach Pendant**
The handheld operator interface for FANUC controllers. Also where DCS and safety are configured.

**tool0 / tool_link**
`tool0` is FANUC's default tool frame at flange. `tool_link` is this project's extension where the gripper geometry attaches.

## U

**URDF**
Unified Robot Description Format. The rigid-body model of the robot.

## V

**vcs (vcstool)**
Tool that fetches multiple git repositories listed in a `.repos` YAML file. Used for FANUC source dependencies.

## W

**world**
Top frame of the planning scene. Static.
````

- [ ] **Step 2: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/concepts/glossary.md
git commit -m "docs: add glossary"
```

Expected: commit succeeds.

## Task 4: Concepts - System Block Diagram Page

**Files:**
- Create: `docs/concepts/system_block_diagram.md`

(`docs/diagrams/system_block_diagram.svg` was created in Task 1.)

- [ ] **Step 1: Create `docs/concepts/system_block_diagram.md`**

Create `docs/concepts/system_block_diagram.md`:

````markdown
# System Block Diagram

The diagram below shows the physical and logical components in a CRX-10iA/L workcell as the project targets it.

![System block diagram](../diagrams/system_block_diagram.svg)

## Roles

- **Linux PC** runs Ubuntu 22.04 with ROS 2 Humble. It hosts MoveIt 2, MoveIt Task Constructor, the FANUC ROS 2 driver, and the project's `crx10ial_*` packages.
- **FANUC Controller (R-30iB Mini Plus)** runs the safety-rated motion control. It exposes ROS 2 access via J519 Stream Motion and the Remote Motion Interface (R912). iRVision runs here when the option is installed.
- **CRX-10iA/L Robot** is the 6-axis collaborative arm.
- **Teach Pendant** is the operator UI and source of authority for safety configuration (DCS).
- **Gripper** is end-effector hardware. The first project iteration treats it as a fake/mock element with optional digital I/O. Real grippers (parallel jaw, vacuum) are added behind the gripper service abstraction.
- **Camera** is the iRVision-targeted device or a future external RGB-D sensor.

## Connections

- Linux PC <-> Controller: Ethernet. Carries Stream Motion, RMI, and ROS 2 to driver traffic.
- Controller <-> Robot: cable.
- Controller <-> Gripper: digital I/O.
- Controller <-> Camera: iRVision interface (controller-side image processing).

## What is and is not safety-rated

The FANUC controller and its DCS configuration are safety-rated. ROS 2 application code is not. Any feature that affects the robot's motion safety must be implemented and reviewed on the controller side (Teach Pendant, DCS, payload schedule).

For the layered software stack that runs on the Linux PC, see [software_overview.md](software_overview.md). For frame conventions used inside the cell description, see `docs/frames.md`.
````

- [ ] **Step 2: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/concepts/system_block_diagram.md
git commit -m "docs: add system block diagram page"
```

Expected: commit succeeds.

## Task 5: Onboarding - Quickstart

**Files:**
- Create: `docs/quickstart.md`

- [ ] **Step 1: Create `docs/quickstart.md`**

Create `docs/quickstart.md`:

````markdown
# Quickstart

This page takes a contributor from a fresh Ubuntu 22.04 machine to a running mock pick/place demo. It does not cover Gazebo, ROBOGUIDE, hardware, or iRVision; those are separate milestones.

## Prerequisites

- Ubuntu 22.04 LTS, x86-64.
- ROS 2 Humble desktop install. See `docs/setup/ubuntu22_humble.md` for the long form.
- Network access for git clones and apt installs.
- A user account with `sudo`.

If you do not yet have ROS 2 Humble:

```bash
sudo apt update
sudo apt install -y software-properties-common curl gnupg lsb-release
# Follow https://docs.ros.org/en/humble/Installation/Ubuntu-Install-Debs.html
sudo apt install -y ros-humble-desktop python3-colcon-common-extensions \
  python3-rosdep python3-vcstool git git-lfs
sudo rosdep init || true
rosdep update
```

## Clone and build

```bash
mkdir -p ~/Develop/Fanuc
cd ~/Develop/Fanuc
git clone <this-repo-url> Fanuc_Robotics
cd Fanuc_Robotics

source /opt/ros/humble/setup.bash
./scripts/import_dependencies.sh third_party.humble.lock.repos
sudo apt install -y ros-humble-moveit ros-humble-moveit-task-constructor-core \
  ros-humble-moveit-task-constructor-msgs \
  ros-humble-moveit-task-constructor-capabilities \
  ros-humble-moveit-task-constructor-visualization
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble \
  --skip-keys ament_python
colcon build --symlink-install
source install/setup.bash
```

## Mock launch

```bash
ros2 launch crx10ial_bringup mock.launch.py \
  launch_rviz:=true publish_scene:=true launch_gripper:=true
```

You should see RViz open with the CRX-10iA/L, table, work object, camera stand, and gripper. The fake gripper services are available under `/crx10ial_gripper/`.

For headless verification (no display):

```bash
timeout 45s ros2 launch crx10ial_bringup mock.launch.py \
  launch_rviz:=false publish_scene:=true launch_gripper:=true
```

The command exits with status 124 after 45 s. That is expected; it means the launch reached steady state.

## Run the fixed pick/place demo (M3)

In one terminal, start the mock cell:

```bash
ros2 launch crx10ial_bringup mock.launch.py \
  launch_rviz:=false publish_scene:=true launch_gripper:=true
```

In a second terminal:

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch crx10ial_tasks fixed_pick_place.launch.py run_mode:=execute_mock
```

Expected log lines:

- `M3 fixed pick/place planning succeeded with 1 solution(s)`
- `M3 single attached object verified`
- `M3 mock pick/place execution succeeded`

To see actionable failure diagnostics for a deliberately unreachable goal:

```bash
ros2 launch crx10ial_tasks fixed_pick_place.launch.py run_mode:=negative_plan
```

Expected: the task reports `M3 negative planning produced diagnostics` plus a Failing stage breakdown.

## Where to go next

- Concepts: `docs/concepts/software_overview.md`, `docs/concepts/hardware_overview.md`.
- Architecture: `docs/architecture.md`.
- Frame conventions: `docs/frames.md`.
- When something does not work: `docs/troubleshooting.md`.
- Decision rationale: `docs/decisions/`.
````

- [ ] **Step 2: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/quickstart.md
git commit -m "docs: add quickstart"
```

Expected: commit succeeds.

## Task 6: Onboarding - Architecture Overview

**Files:**
- Create: `docs/diagrams/architecture_layers.svg`
- Create: `docs/diagrams/package_dependencies.svg`
- Create: `docs/architecture.md`

- [ ] **Step 1: Create `docs/diagrams/architecture_layers.svg`**

Create `docs/diagrams/architecture_layers.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 480" font-family="sans-serif" font-size="14">
  <rect width="800" height="480" fill="white"/>
  <text x="400" y="32" text-anchor="middle" font-size="18" font-weight="bold">Project Architecture - Four Layers</text>
  <g stroke="#1f3a93" stroke-width="2" fill="#eaf0ff">
    <rect x="100" y="60" width="600" height="80" rx="6"/>
    <rect x="100" y="160" width="600" height="80" rx="6"/>
    <rect x="100" y="260" width="600" height="80" rx="6"/>
    <rect x="100" y="360" width="600" height="80" rx="6"/>
  </g>
  <g fill="#000">
    <text x="400" y="90" text-anchor="middle" font-weight="bold">Task layer</text>
    <text x="400" y="115" text-anchor="middle" font-size="12">crx10ial_tasks (MTC stages, grasp/place state machines, recovery)</text>
    <text x="400" y="190" text-anchor="middle" font-weight="bold">Planning layer</text>
    <text x="400" y="215" text-anchor="middle" font-size="12">MoveIt 2 (planning scene, kinematics, OMPL trajectories)</text>
    <text x="400" y="290" text-anchor="middle" font-weight="bold">Control adapter layer</text>
    <text x="400" y="315" text-anchor="middle" font-size="12">crx10ial_bringup, crx10ial_gripper, crx10ial_vision_bridge, crx10ial_safety</text>
    <text x="400" y="390" text-anchor="middle" font-weight="bold">Execution layer</text>
    <text x="400" y="415" text-anchor="middle" font-size="12">mock / Gazebo / ROBOGUIDE / hardware via FANUC driver</text>
  </g>
  <g stroke="#27ae60" stroke-width="2" fill="none" marker-end="url(#a3)">
    <line x1="400" y1="140" x2="400" y2="160"/>
    <line x1="400" y1="240" x2="400" y2="260"/>
    <line x1="400" y1="340" x2="400" y2="360"/>
  </g>
  <defs>
    <marker id="a3" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 z" fill="#27ae60"/>
    </marker>
  </defs>
</svg>
```

- [ ] **Step 2: Create `docs/diagrams/package_dependencies.svg`**

Create `docs/diagrams/package_dependencies.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 900 560" font-family="sans-serif" font-size="13">
  <rect width="900" height="560" fill="white"/>
  <text x="450" y="32" text-anchor="middle" font-size="18" font-weight="bold">Project Package Dependencies</text>
  <g stroke="#1f3a93" stroke-width="1.8" fill="#eaf0ff">
    <rect x="370" y="70" width="160" height="46" rx="6"/>
    <rect x="170" y="160" width="180" height="46" rx="6"/>
    <rect x="370" y="160" width="160" height="46" rx="6"/>
    <rect x="560" y="160" width="180" height="46" rx="6"/>
    <rect x="60" y="260" width="180" height="46" rx="6"/>
    <rect x="270" y="260" width="160" height="46" rx="6"/>
    <rect x="450" y="260" width="200" height="46" rx="6"/>
    <rect x="670" y="260" width="180" height="46" rx="6"/>
    <rect x="170" y="360" width="200" height="46" rx="6"/>
    <rect x="400" y="360" width="200" height="46" rx="6"/>
    <rect x="630" y="360" width="180" height="46" rx="6"/>
    <rect x="320" y="460" width="260" height="46" rx="6" fill="#fff5e6"/>
  </g>
  <g fill="#000" font-weight="bold">
    <text x="450" y="98" text-anchor="middle">crx10ial_tasks</text>
    <text x="260" y="188" text-anchor="middle">crx10ial_bringup</text>
    <text x="450" y="188" text-anchor="middle">crx10ial_gripper</text>
    <text x="650" y="188" text-anchor="middle">crx10ial_vision_bridge</text>
    <text x="150" y="288" text-anchor="middle">crx10ial_cell_description</text>
    <text x="350" y="288" text-anchor="middle">crx10ial_safety</text>
    <text x="550" y="288" text-anchor="middle">crx10ial_interfaces</text>
    <text x="760" y="288" text-anchor="middle">crx10ial_sim</text>
    <text x="270" y="388" text-anchor="middle">fanuc_crx_description</text>
    <text x="500" y="388" text-anchor="middle">fanuc_hardware_interface</text>
    <text x="720" y="388" text-anchor="middle">fanuc_moveit_config</text>
    <text x="450" y="488" text-anchor="middle">MoveIt 2 / ros2_control / MTC apt</text>
  </g>
  <g stroke="#27ae60" stroke-width="1.5" fill="none" marker-end="url(#a4)">
    <line x1="450" y1="116" x2="260" y2="160"/>
    <line x1="450" y1="116" x2="450" y2="160"/>
    <line x1="450" y1="116" x2="650" y2="160"/>
    <line x1="260" y1="206" x2="150" y2="260"/>
    <line x1="260" y1="206" x2="350" y2="260"/>
    <line x1="260" y1="206" x2="550" y2="260"/>
    <line x1="450" y1="206" x2="550" y2="260"/>
    <line x1="650" y1="206" x2="550" y2="260"/>
    <line x1="150" y1="306" x2="270" y2="360"/>
    <line x1="260" y1="206" x2="500" y2="360"/>
    <line x1="260" y1="206" x2="720" y2="360"/>
    <line x1="450" y1="488" x2="450" y2="408" stroke-dasharray="4,3"/>
  </g>
  <defs>
    <marker id="a4" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 z" fill="#27ae60"/>
    </marker>
  </defs>
  <text x="60" y="540" font-size="12" fill="#7f8c8d">Solid arrows: package depends on. Dashed: external apt dependencies.</text>
</svg>
```

- [ ] **Step 3: Create `docs/architecture.md`**

Create `docs/architecture.md`:

````markdown
# Architecture

This document explains how the project is organized into layers and packages, and how data flows between them. For background on individual technologies, see `docs/concepts/software_overview.md`.

## Four-layer architecture

The architecture (from the design document, section 8) has four layers:

![Architecture layers](diagrams/architecture_layers.svg)

- **Task layer** owns higher-level intent. In M3 this is the fixed pick/place pipeline built with MoveIt Task Constructor. Recovery and grasp/place state machines live here. The task layer never calls FANUC register services directly.
- **Planning layer** is MoveIt 2. It owns the planning scene, kinematics, collision checking, and trajectory generation. It exposes services like `/plan_kinematic_path` and `/apply_planning_scene`.
- **Control adapter layer** is where this project's mode-specific composition lives: `crx10ial_bringup` chooses launch mode, `crx10ial_gripper` abstracts end-effector commands, `crx10ial_vision_bridge` adapts vision sources, `crx10ial_safety` adds non-safety-rated runtime guards.
- **Execution layer** is the underlying engine: mock hardware, Gazebo (M4), ROBOGUIDE (M6), or the real controller (M7). The FANUC ROS 2 driver bridges this layer to ros2_control.

This boundary keeps the task layer stable while the simulator, controller, gripper hardware, or vision source change underneath.

## Package responsibilities

| Package | Build type | Role |
|---|---|---|
| `crx10ial_interfaces` | ament_cmake | Shared `.srv` definitions: `CommandGripper`, `AttachObject`, `DetachObject`, `GetGripperState`. |
| `crx10ial_cell_description` | ament_cmake | Workcell xacro composing FANUC robot, table, work object, camera stand, gripper, frames. Single source of truth for `robot_description`. |
| `crx10ial_bringup` | ament_python | Mode launches: mock today, gazebo/roboguide/hardware in later milestones. Owns the static planning-scene publisher (`mock_scene`). |
| `crx10ial_gripper` | ament_python | Fake gripper backend and ROS 2 services. Sole owner of runtime attach/detach planning-scene writes. |
| `crx10ial_tasks` | ament_cmake | M3 fixed pick/place using MTC plus mock execution orchestration. |
| `crx10ial_vision_bridge` | ament_cmake | Vision adapter boundary for fake/sim/iRVision detection backends (M5+). |
| `crx10ial_safety` | ament_cmake | Non-safety-rated runtime guard package (workspace limits, recovery helpers). |
| `crx10ial_sim` | ament_cmake | Gazebo Fortress integration boundary (M4). |
| `crx10ial_tests` | ament_cmake | Cross-package launch and integration tests (deferred). |

## Package dependency graph

![Package dependencies](diagrams/package_dependencies.svg)

Arrows mean "depends on". The dashed line at the bottom marks external apt dependencies (MoveIt, MTC, ros2_control) that all upper packages share through ROS 2 build infrastructure.

## Data flow in mock mode

The mock launch wires this graph:

1. `crx10ial_bringup/mock.launch.py` expands the cell xacro from `crx10ial_cell_description`. The expanded URDF includes both the robot and the FANUC `crx_mock_ros2_control` macro.
2. `robot_state_publisher` publishes `/tf` from the URDF and joint states.
3. `controller_manager` (`ros2_control_node`) consumes the same URDF and starts the FANUC mock hardware interface plus controllers (joint_state_broadcaster, joint_trajectory_controller, fanuc_gpio_controller, fanuc_force_sensor_broadcaster, force_torque_sensor_broadcaster).
4. `move_group` loads the cell URDF and the FANUC SRDF, exposing `/plan_kinematic_path`, `/apply_planning_scene`, etc.
5. `crx10ial_bringup/mock_scene_node.py` publishes static workcell collision objects (table, work_object, camera_stand) to `/collision_object`.
6. `crx10ial_gripper/fake_gripper_node.py` exposes `command`, `attach_object`, `detach_object`, `get_state` and applies attach/detach diffs to the runtime planning scene through `/apply_planning_scene`.

The cell xacro is the single robot_description source; see `docs/decisions/0005`. The mock launch composes the same FANUC mock controllers as the upstream FANUC mock launch, but starts them locally so the URDF is not expanded twice.

## C1 contract

The C1 contract is the rule that runtime planning-scene writes for attached objects flow through `crx10ial_gripper` only.

![C1 contract](diagrams/c1_contract.svg)

- MTC stages (`ModifyPlanningScene::attachObject`, `detachObject`) update the planner's internal scene during `Task::plan()`.
- The project never calls `Task::execute()`. Doing so would also write the runtime scene through MTC's executor.
- Runtime attach/detach goes through `crx10ial_gripper`'s services. The gripper service applies the scene diff via `/apply_planning_scene`.

This contract is enforced by source-contract pytests in `crx10ial_tasks` and by a runtime check (`/get_planning_scene` after attach asserts exactly one attached `work_object` and zero world duplicates). See `docs/decisions/0003` for the full rationale.

## Where new code goes

- New planning logic: `crx10ial_tasks`.
- New gripper hardware support: a new backend module under `crx10ial_gripper`, sharing the existing service interface.
- New vision source: a new backend under `crx10ial_vision_bridge`, sharing a future `DetectObject` interface.
- New simulator mode: `crx10ial_sim` plus a new launch in `crx10ial_bringup`.
- A new workcell element (table, sensor, fixture): cell xacro in `crx10ial_cell_description` plus the matching collision in `mock_scene` (or a new publisher if it must move).
````

- [ ] **Step 4: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 5: Commit**

Run:

```bash
git add docs/diagrams/architecture_layers.svg docs/diagrams/package_dependencies.svg docs/architecture.md
git commit -m "docs: add architecture overview"
```

Expected: commit succeeds.

## Task 7: Onboarding - Troubleshooting

**Files:**
- Create: `docs/troubleshooting.md`

- [ ] **Step 1: Create `docs/troubleshooting.md`**

Create `docs/troubleshooting.md`. Distil real fixes from M0-M3 history. Each entry has Symptom / Cause / Fix / Reference (commit) format:

````markdown
# Troubleshooting

This page collects problems observed during M0-M3 execution and their fixes. New entries should follow the same `Symptom / Cause / Fix / Reference` template.

## Build and dependency

### `vcs: command not found`

**Symptom:** `./scripts/import_dependencies.sh` aborts with `vcs is not installed`.

**Cause:** `python3-vcstool` not installed on the host. Some CI/build environments lack it by default.

**Fix:** With sudo, `sudo apt install -y python3-vcstool`. Without sudo, `python3 -m pip install --user vcstool` then ensure `${HOME}/.local/bin` is on `PATH`.

**Reference:** Documented in `third_party.humble.repos` setup notes and Task 0 of the M0/M1 plan (commit 9c6bf7f added the fallback).

### `git lfs: command not found` during dependency import

**Symptom:** `import_dependencies.sh` fails on `git -C src/fanuc_description lfs install --local`.

**Cause:** `git-lfs` not installed. FANUC mesh files are LFS-stored.

**Fix:** Install `git-lfs` via apt. The import script tolerates the missing tool by skipping the LFS pull when `git lfs version` fails (commit 5f9ad26). Meshes can be fetched manually later if visualization needs them.

### `rosdep` cannot resolve `ament_python`

**Symptom:** `rosdep install ...` fails with "Cannot locate rosdep definition for [ament_python]".

**Cause:** Humble's `rosdep` distro index does not include the `ament_python` buildtool key. The package is provided by the ROS 2 install itself.

**Fix:** Add `--skip-keys ament_python` to the `rosdep install` invocation. Documented in M2 plan Task 0.

## Launch and runtime

### MoveIt complains "Semantic description is not specified"

**Symptom:** `move_group` warns about semantic description; planning fails.

**Cause:** SRDF cannot be loaded. Most often the robot name in the URDF does not match the SRDF root robot name.

**Fix:** Ensure the cell xacro's `<robot name="...">` matches the FANUC SRDF expected name. Commit 6180cfe aligned the cell robot name with `fanuc_moveit_config`'s SRDF.

### Mock gripper self-collision blocks planning

**Symptom:** Plans to plausible poses fail with collision errors involving gripper internal links.

**Cause:** Gripper geometry overlapping the robot wrist or itself.

**Fix:** Separate gripper collision geometry from visual geometry; tighten boxes so adjacent links do not overlap. Commit bb90a39 split gripper collision shapes from visual ones.

### `/apply_planning_scene` returns failure

**Symptom:** `crx10ial_gripper` service responds with success=false; runtime scene not updated.

**Cause:** Race during service call: the future's `add_done_callback` resolves before the threaded executor sees the response, so the response is empty.

**Fix:** Use a wait pattern that does not depend on `add_done_callback` racing the executor. Commit 4197c66 stabilized the apply_planning_scene call by waiting on the future via `Event` only after the call completed.

### MTC plans pass but trajectory ends past the object

**Symptom:** MTC `Task::plan()` returns SUCCESS, but the resulting end pose is 5-10 cm beyond the object.

**Cause:** "Move to grasp pose" stage targeted the object center directly. The subsequent `MoveRelative` approach added another approach distance, overshooting.

**Fix:** Target a pre-grasp pose in the MoveTo stage (`pregrasp_pose = grasp_pose - approach_direction * approach_distance`). The Cartesian approach then ends at the grasp pose. Commit a32a3ef applied this and other MTC structure adjustments in M3.

### Runtime collision when moving to grasp pose

**Symptom:** During mock execution, `MoveGroupInterface::move()` to the grasp pose fails with `INVALID_GOAL_STATE` even though the MTC plan succeeded.

**Cause:** MTC has its own `ModifyPlanningScene allow collision` stage that allows the gripper to overlap the object during planning. The runtime planning scene has no such allowance, so the same goal pose is rejected.

**Fix:** In mock execution, attach the object before moving to the grasp pose. The fake gripper's attach removes the world `work_object` and re-anchors it as an attached collision on `grasp_link`, so the goal becomes valid. Order: pregrasp -> close -> attach -> move-to-grasp -> retreat. Commit 631bf07 implements this for execute_mock; the source-contract pytest enforces the order statically.

### `slider_gui_node` warnings on headless launch

**Symptom:** Headless launch logs Qt or X11 errors from `slider_gui_node`.

**Cause:** The slider helper requires a display and is started by both the upstream FANUC mock and this project's mock launch.

**Fix:** Acceptable. The smoke checks grep for `Traceback|Exception|ModuleNotFoundError|PackageNotFoundError`, which excludes Qt/X11 connection messages. If needed, suppress slider's start in custom launches.

## MTC and planning

### Negative pick/place planning is "too" successful

**Symptom:** A negative test case meant to fail at the place stage still finds a plan.

**Cause:** The "unreachable" pose is actually within reach.

**Fix:** Use a target with X-coordinate well beyond the robot's 1.249 m reach (the project uses x=2.0 m). The planner reliably reports `GOAL_STATE_INVALID` at "move to place pose". The negative smoke deliberately does not pin a specific failing-stage name; non-empty diagnostics is the assertion.

### Planning succeeds but trajectory has zero points

**Symptom:** `Task::plan()` returns SUCCESS but `solutions().empty()`.

**Cause:** Edge case in MTC; sometimes a non-failure error code does not imply a usable trajectory.

**Fix:** Always check `task.solutions().empty()` in addition to the error code. The project's `plan_fixed_pick_place` does this.

## Reading commit history for fixes

The fastest way to find a fix for an unfamiliar symptom is to grep the project's commit messages:

```bash
git log --oneline | grep -iE 'fix|stabilize|align'
```

M0-M3 fix commits are short and scoped to one concern. Their commit messages describe the symptom and the fix in one line.
````

- [ ] **Step 2: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/troubleshooting.md
git commit -m "docs: add troubleshooting from M0-M3 history"
```

Expected: commit succeeds.

## Task 8: Reference - Frame Conventions

**Files:**
- Create: `docs/diagrams/frame_tree.svg`
- Create: `docs/diagrams/grasp_axes.svg`
- Create: `docs/frames.md`
- Modify: `docs/gripper_frames.md`

- [ ] **Step 1: Create `docs/diagrams/frame_tree.svg`**

Create `docs/diagrams/frame_tree.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 540" font-family="sans-serif" font-size="13">
  <rect width="800" height="540" fill="white"/>
  <text x="400" y="32" text-anchor="middle" font-size="18" font-weight="bold">Cell Frame Tree</text>
  <g stroke="#1f3a93" stroke-width="1.6" fill="#eaf0ff">
    <rect x="340" y="60" width="120" height="34" rx="4"/>
    <rect x="100" y="140" width="160" height="34" rx="4"/>
    <rect x="320" y="140" width="160" height="34" rx="4"/>
    <rect x="540" y="140" width="160" height="34" rx="4"/>
    <rect x="60" y="220" width="160" height="34" rx="4"/>
    <rect x="320" y="220" width="160" height="34" rx="4"/>
    <rect x="320" y="300" width="160" height="34" rx="4"/>
    <rect x="180" y="380" width="120" height="34" rx="4"/>
    <rect x="320" y="380" width="120" height="34" rx="4"/>
    <rect x="460" y="380" width="120" height="34" rx="4"/>
    <rect x="320" y="460" width="160" height="34" rx="4" fill="#fff5e6"/>
  </g>
  <g fill="#000">
    <text x="400" y="83" text-anchor="middle">world</text>
    <text x="180" y="163" text-anchor="middle">work_table</text>
    <text x="400" y="163" text-anchor="middle">base_link</text>
    <text x="620" y="163" text-anchor="middle">camera_stand</text>
    <text x="140" y="243" text-anchor="middle">work_object</text>
    <text x="400" y="243" text-anchor="middle">flange</text>
    <text x="400" y="323" text-anchor="middle">end_effector</text>
    <text x="240" y="403" text-anchor="middle">gripper_palm</text>
    <text x="380" y="403" text-anchor="middle">left_finger</text>
    <text x="520" y="403" text-anchor="middle">right_finger</text>
    <text x="400" y="483" text-anchor="middle">grasp_link</text>
  </g>
  <g stroke="#27ae60" stroke-width="1.4" fill="none">
    <line x1="400" y1="94" x2="180" y2="140"/>
    <line x1="400" y1="94" x2="400" y2="140"/>
    <line x1="400" y1="94" x2="620" y2="140"/>
    <line x1="180" y1="174" x2="140" y2="220"/>
    <line x1="400" y1="174" x2="400" y2="220"/>
    <line x1="400" y1="254" x2="400" y2="300"/>
    <line x1="400" y1="334" x2="240" y2="380"/>
    <line x1="400" y1="334" x2="380" y2="380"/>
    <line x1="400" y1="334" x2="520" y2="380"/>
    <line x1="400" y1="334" x2="400" y2="460"/>
  </g>
  <text x="60" y="525" font-size="12" fill="#7f8c8d">Yellow box: object attach target during grasp.</text>
</svg>
```

- [ ] **Step 2: Create `docs/diagrams/grasp_axes.svg`**

Create `docs/diagrams/grasp_axes.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 420" font-family="sans-serif" font-size="14">
  <rect width="600" height="420" fill="white"/>
  <text x="300" y="32" text-anchor="middle" font-size="18" font-weight="bold">grasp_link Axis Convention</text>
  <g stroke="#1f3a93" stroke-width="2" fill="#eaf0ff">
    <rect x="200" y="180" width="60" height="60" rx="4"/>
    <text x="230" y="217" text-anchor="middle" font-size="12" fill="#000">grasp_link</text>
  </g>
  <g stroke="#c0392b" stroke-width="2" fill="#c0392b">
    <line x1="260" y1="210" x2="450" y2="210" marker-end="url(#aX)"/>
    <text x="460" y="214">+X (approach)</text>
  </g>
  <g stroke="#27ae60" stroke-width="2" fill="#27ae60">
    <line x1="230" y1="180" x2="230" y2="60" marker-end="url(#aY)"/>
    <text x="170" y="80">+Y (jaw)</text>
  </g>
  <g stroke="#1f3a93" stroke-width="2" fill="#1f3a93">
    <line x1="230" y1="240" x2="170" y2="320" marker-end="url(#aZ)"/>
    <text x="80" y="345">+Z (up from palm)</text>
  </g>
  <defs>
    <marker id="aX" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#c0392b"/></marker>
    <marker id="aY" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#27ae60"/></marker>
    <marker id="aZ" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#1f3a93"/></marker>
  </defs>
  <text x="60" y="395" font-size="12" fill="#7f8c8d">Pre-grasp: move along -X. Approach: +X. Retreat after grasp: -X.</text>
</svg>
```

- [ ] **Step 3: Create `docs/frames.md`**

Create `docs/frames.md`:

````markdown
# Frame Conventions

This document is the canonical reference for the frames used by the CRX-10iA/L workcell. It supersedes `docs/gripper_frames.md`, which now points here.

![Cell frame tree](diagrams/frame_tree.svg)

## Frame catalog

| Frame | Owner | Purpose |
|---|---|---|
| `world` | cell xacro | Fixed root of the workspace. All static cell objects ultimately attach here. |
| `base_link` | FANUC URDF | Robot base. Origin at the bolt-down face. |
| `flange` | FANUC URDF | Tool mounting interface. |
| `end_effector` | cell xacro | Project-side anchor for tooling, parented to `flange`. Used as the MTC IK frame's parent in mock. |
| `tool_link` | cell xacro | Project tool root. Gripper geometry parents here. |
| `gripper_palm` | cell xacro | Gripper body collision. |
| `left_finger` / `right_finger` | cell xacro | Parallel-jaw fingers. Collision geometry only; not actuated. |
| `grasp_link` | cell xacro | Frame at which objects attach during grasp. Origin offset 0.18 m in `+X` from `tool_link`. |
| `work_table` | mock_scene runtime publisher | Static collision: 1.0 x 0.7 x 0.04 box at world (0.75, 0, 0.70). |
| `work_object` | mock_scene + fake_gripper | Static collision when on the table; attached collision when grasped. |
| `camera_stand` | mock_scene | Static collision representing the camera fixture. |

## grasp_link convention

`grasp_link` defines orientation as well as position.

![grasp_link axes](diagrams/grasp_axes.svg)

- **+X** is the approach direction from wrist toward the object.
- **+Y** is the parallel-jaw opening direction.
- **+Z** completes the right-handed frame and points up from the palm.

This is consistent with FANUC's tool0 convention (X forward) and is the reason approach directions are encoded as `[1.0, 0.0, 0.0]` in `fixed_pick_place.yaml`.

Pre-grasp poses sit at `grasp_pose - approach_max * +X`. Approach proceeds `+X` to `grasp_pose`. Retreat is `-X`.

## Workcell coordinates

The mock workcell uses these world-frame coordinates by convention. Both the cell xacro and `mock_scene` reference them; values must stay in sync.

| Object | Center (x, y, z) m | Size (x, y, z) m |
|---|---|---|
| `work_table` | (0.75, 0.0, 0.70) | (1.0, 0.7, 0.04) |
| `work_object` (free) | (0.55, 0.0, 0.745) | (0.08, 0.08, 0.05) |
| `camera_stand` | (0.35, -0.55, 0.35) | (0.05, 0.05, 0.70) |

These come from M2 (`crx10ial_cell.urdf.xacro`) and `crx10ial_bringup/mock_scene.py`. When changing them, update both files; a mismatch breaks planning-scene consistency.

## Frame ownership policy

- **Static world geometry** is published by `mock_scene_publisher` (in `crx10ial_bringup`) as MoveIt collision objects. The cell xacro contains the same geometry as URDF for visualization, but MoveIt's planning view comes from the publisher, not the URDF.
- **Robot links** come from the FANUC URDF.
- **Project tool links** come from the cell xacro.
- **Attached objects** are owned by `crx10ial_gripper` at runtime (see [decisions/0003](decisions/0003-fake-gripper-as-runtime-scene-owner.md)).
````

- [ ] **Step 4: Modify `docs/gripper_frames.md`**

Replace the existing content of `docs/gripper_frames.md` with a single-line redirect:

````markdown
# Superseded

This document has been replaced by [`docs/frames.md`](frames.md), which covers the entire workcell frame tree. Update bookmarks accordingly.
````

- [ ] **Step 5: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 6: Commit**

Run:

```bash
git add docs/diagrams/frame_tree.svg docs/diagrams/grasp_axes.svg docs/frames.md docs/gripper_frames.md
git commit -m "docs: consolidate frame conventions"
```

Expected: commit succeeds.

## Task 9: Reference - Services and Launches

**Files:**
- Create: `docs/services_and_launches.md`

- [ ] **Step 1: Create `docs/services_and_launches.md`**

Create `docs/services_and_launches.md`:

````markdown
# Services and Launches

Reference catalog of every project-defined service and launch file. For schemas of YAML configuration files, see [`yaml_schemas.md`](yaml_schemas.md).

## Services

All project services live in `crx10ial_interfaces/srv/`.

### `CommandGripper` (`crx10ial_gripper/command`)

Commands the fake gripper.

Constants in `Request`:

- `OPEN = 1` - command opens the gripper.
- `CLOSE = 2` - command closes the gripper.
- `VACUUM_ON = 3` - sets the fake vacuum state to enabled.
- `VACUUM_OFF = 4` - clears the fake vacuum state.

Request fields:

- `uint8 command` - one of the constants above.
- `float64 width_m` - target jaw width in metres (0.0 to 0.12).
- `float64 force_n` - target force in newtons (>= 0.0).

Response fields:

- `bool success`, `string message`.
- `uint8 state` - state machine value (`IDLE=0, OPEN=1, CLOSED=2, HOLDING=3`).
- `float64 width_m`, `float64 force_n`.
- `string attached_object_id` - empty unless an object is attached.
- `bool vacuum_enabled`.

### `AttachObject` (`crx10ial_gripper/attach_object`)

Attaches a known world collision object to `grasp_link`.

Request: `string object_id` (must be a known mock object; `work_object` is the default).

Response: `bool success`, `string message`, `string attached_object_id`.

The implementation removes the object from the world and adds it as an attached collision via `/apply_planning_scene`.

### `DetachObject` (`crx10ial_gripper/detach_object`)

Detaches the currently attached object and restores it as a world collision at its configured pose.

Request: empty.

Response: `bool success`, `string message`, `string detached_object_id`.

### `GetGripperState` (`crx10ial_gripper/get_state`)

Reads the current fake gripper state.

Request: empty.

Response: `uint8 state`, `float64 width_m`, `float64 force_n`, `string attached_object_id`, `bool vacuum_enabled`.

## Launches

All launches live under `src/<package>/launch/`.

### `crx10ial_cell_description/view_cell.launch.py`

Visualizes the workcell in RViz with `joint_state_publisher_gui`. Useful for inspecting frame placement and collision geometry without running MoveIt or controllers.

Arguments:

- `launch_rviz` (`true`/`false`, default `true`).

### `crx10ial_bringup/mock.launch.py`

Brings up the full mock workcell: FANUC mock control, MoveIt 2, RViz (optional), the static planning-scene publisher, and the fake gripper.

Arguments:

- `robot_model` (default `crx10ia_l`).
- `robot_ip` (default `1.1.1.1`; unused in mock).
- `launch_rviz` (`true`/`false`, default `true`).
- `publish_scene` (`true`/`false`, default `true`).
- `launch_gripper` (`true`/`false`, default `true`).
- `ros2_control_config` (default: FANUC's `ros2_controllers.yaml`).
- `gpio_configuration` (default: FANUC's `example_gpio_config.yaml`).

Notable nodes started:

- `controller_manager` (`ros2_control_node`).
- `robot_state_publisher`.
- 5 controller spawners: `joint_state_broadcaster`, `joint_trajectory_controller`, `fanuc_gpio_controller`, `fanuc_force_sensor_broadcaster`, `force_torque_sensor_broadcaster`.
- `move_group`.
- `rviz2` (conditional).
- `mock_scene_publisher` (conditional).
- `fake_gripper` (conditional).
- `slider_gui_node` (FANUC upstream helper).

### `crx10ial_tasks/fixed_pick_place.launch.py`

Starts the M3 fixed pick/place node alongside the mock cell. Use after `mock.launch.py` is up.

Arguments:

- `robot_model` (default `crx10ia_l`).
- `run_mode` - one of `plan`, `negative_plan`, `execute_mock` (default `plan`).
- `config_file` - YAML path; defaults to the installed `fixed_pick_place.yaml`.

Behaviours:

- `plan` - builds the MTC task and calls `Task::plan(max_solutions)`. Logs diagnostics and exits.
- `negative_plan` - same, but uses the failure place pose. Expects diagnostics.
- `execute_mock` - plans, then orchestrates motion through `MoveGroupInterface` and the fake gripper. Asserts a single attached object via `/get_planning_scene` after attach.

The launch always injects the MoveIt configuration (`robot_description`, `robot_description_semantic`, kinematics, joint limits, planning pipelines) so the node can build the MTC task without the move_group monitor topics.

## Common topics and services touched at runtime

These are not project-owned but are consumed by project code in mock mode.

- `/joint_states` - joint state publisher feeds MoveIt and `tf`.
- `/tf`, `/tf_static` - frame transforms.
- `/collision_object` - latched topic published by `mock_scene_publisher`.
- `/apply_planning_scene` - service exposed by `move_group`; called by `fake_gripper`.
- `/get_planning_scene` - service exposed by `move_group`; called by execute_mock and the M3 duplicate-attach check.
- `/plan_kinematic_path` - MoveIt motion-planning service.
- `/execute_trajectory` - MoveIt trajectory execution action.
````

- [ ] **Step 2: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/services_and_launches.md
git commit -m "docs: add services and launches reference"
```

Expected: commit succeeds.

## Task 10: Reference - YAML Schemas

**Files:**
- Create: `docs/yaml_schemas.md`

- [ ] **Step 1: Create `docs/yaml_schemas.md`**

Create `docs/yaml_schemas.md`:

````markdown
# YAML Schemas

The project uses YAML for two configurations today. This page documents both. Schemas are descriptive, not enforced by a JSON-Schema validator; the consuming code (Python or C++) raises when expectations are violated.

## `mock_scene` (in code, not user-facing YAML)

Static workcell collision objects published by `crx10ial_bringup/mock_scene.py`. Defined as a Python tuple `SCENE_BOXES`, not as user YAML. Documented here for reference because changing it requires changing the cell xacro to match.

```python
SCENE_BOXES = (
    BoxSpec("work_table",   (1.00, 0.70, 0.04), (0.75,  0.00, 0.70)),
    BoxSpec("work_object",  (0.08, 0.08, 0.05), (0.55,  0.00, 0.745)),
    BoxSpec("camera_stand", (0.05, 0.05, 0.70), (0.35, -0.55, 0.35)),
)
```

Fields:

- `object_id` - identifier published as `CollisionObject.id`.
- `dimensions` - `(x, y, z)` size of the box in metres.
- `xyz` - `(x, y, z)` centre position in `world`.

The publisher uses TRANSIENT_LOCAL durability so `move_group`'s planning-scene monitor picks up the latest state on subscribe.

## `crx10ial_tasks/config/fixed_pick_place.yaml`

Drives the M3 fixed pick/place task. Single ROS parameter file under the node namespace `fixed_pick_place`.

```yaml
fixed_pick_place:
  ros__parameters:
    arm_group_name: manipulator        # MoveIt planning group
    eef_name: tool_link                # MoveIt end-effector identifier
    hand_frame: grasp_link             # Frame at which objects attach
    world_frame: world

    object.id: work_object             # Attached object id
    object.frame_id: world             # Pose frame for object
    object.dimensions: [0.08, 0.08, 0.05]
    object.pose.xyz: [0.55, 0.0, 0.745]
    object.pose.rpy: [0.0, 0.0, 0.0]

    grasp.frame_id: grasp_link
    grasp.pose.xyz: [0.0, 0.0, 0.0]    # Offset from object frame to grasp pose
    grasp.pose.rpy: [0.0, 0.0, 0.0]
    grasp.approach.direction: [1.0, 0.0, 0.0]   # Unit vector in hand_frame
    grasp.approach.min: 0.05                    # Metres
    grasp.approach.max: 0.10
    grasp.retreat.direction: [-1.0, 0.0, 0.0]
    grasp.retreat.min: 0.05
    grasp.retreat.max: 0.10

    place.frame_id: world
    place.pose.xyz: [0.55, 0.20, 0.745]
    place.pose.rpy: [0.0, 0.0, 0.0]

    failure.place.pose.xyz: [2.00, 0.00, 0.745] # For negative_plan run mode
    failure.place.pose.rpy: [0.0, 0.0, 0.0]

    gripper.open_width_m: 0.08
    gripper.close_width_m: 0.02
    gripper.close_force_n: 30.0

    planning.max_solutions: 1
    planning.timeout_sec: 10.0
    execution.enabled: false           # Reserved for future modes
```

Validation rules implemented in `crx10ial_tasks/src/fixed_pick_place_config.cpp`:

- All `*.xyz` and `*.rpy` arrays must have length 3.
- `grasp.approach.min` must be > 0 and <= `grasp.approach.max`. Same for retreat.
- `gripper.open_width_m`, `gripper.close_width_m`, `gripper.close_force_n` must be > 0.
- `planning.max_solutions` must be > 0 and is cast to `size_t`.
- `planning.timeout_sec` must be > 0.

Notes on conventions:

- `grasp.approach.direction` is expressed in `hand_frame` (`grasp_link`). The default `[1, 0, 0]` matches the `+X approach` convention from `docs/frames.md`.
- `grasp.pose.xyz: [0, 0, 0]` means the grasp pose equals the object pose. The MTC stage moves first to a *pre-grasp* pose computed as `grasp_world_pose - approach.max * approach.direction`.
- `failure.place.pose.xyz: [2.0, ...]` is intentionally outside the robot's reach (1.249 m). It produces deterministic IK failure for the `negative_plan` run mode.

## Future YAMLs (not yet implemented)

- `crx10ial_vision_bridge/config/vision_jobs.yaml` - declared in the design (section 9). Maps each vision job to trigger DO, busy/complete DI, result register, found-pose register, frames. Will be added in M5.
- `crx10ial_bringup/config/safety.yaml` - workspace limits and reduced-speed thresholds for `crx10ial_safety` (M7 prep).
````

- [ ] **Step 2: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/yaml_schemas.md
git commit -m "docs: add YAML schema reference"
```

Expected: commit succeeds.

## Task 11: ADR 0001 - Adopt Ubuntu 22.04 / ROS 2 Humble

**Files:**
- Create: `docs/decisions/0001-adopt-ubuntu22-humble.md`

- [ ] **Step 1: Create `docs/decisions/0001-adopt-ubuntu22-humble.md`**

Create `docs/decisions/0001-adopt-ubuntu22-humble.md`:

````markdown
# 1. Adopt Ubuntu 22.04 / ROS 2 Humble

## Status

Accepted (2026-04-27)

## Context

The project targets a FANUC CRX-10iA/L workcell that must support staged validation in mock, simulation, ROBOGUIDE, and physical-hardware modes. The choice of OS and ROS 2 distribution shapes every downstream dependency: simulator (Gazebo Fortress vs Garden vs Harmonic), MoveIt branch, FANUC driver compatibility, available apt binaries.

Three credible options were considered:

- Ubuntu 22.04 + ROS 2 Humble Hawksbill (LTS, supported through May 2027 per REP 2000).
- Ubuntu 24.04 + ROS 2 Jazzy Jalisco (newer LTS, supported through May 2029).
- Ubuntu 22.04 + ROS 2 Iron (interim, EOL November 2024).

External constraints affecting the choice:

- The FANUC official ROS 2 driver (`FANUC-CORPORATION/fanuc_driver`) ships a `humble` branch. A `jazzy` branch is not yet stable as of project start.
- MoveIt Task Constructor apt binaries (`ros-humble-moveit-task-constructor-*`) are stable on Humble. Jazzy availability is uneven.
- Gazebo Fortress is the LTS Ignition release that pairs with Humble. Gazebo Harmonic pairs with Jazzy.
- The user's existing engineering hosts run Ubuntu 22.04.

## Decision

Adopt **Ubuntu 22.04 LTS + ROS 2 Humble Hawksbill** as the primary target for M0-M7.

A future migration to Ubuntu 24.04 / ROS 2 Jazzy / Gazebo Harmonic is acknowledged as a follow-on track but is explicitly outside the initial milestones. Code is kept "migration aware" by isolating simulator-specific assets in `crx10ial_sim` (see [decisions/0005](0005-cell-xacro-as-single-robot-description.md)) and by avoiding Humble-only API surfaces where Jazzy equivalents are well-known.

## Consequences

Positive:

- All upstream dependencies (FANUC driver, MoveIt 2, MTC, Gazebo Fortress, gz_ros2_control) are available as supported binaries or first-class source builds.
- Humble's two-year LTS window covers the project's planned M0-M7 timeline.
- Onboarding documentation can assume the standard ROS 2 Humble setup procedure.

Negative:

- Gazebo Fortress reaches end of life in September 2026, before Humble's own EOL. The project must plan a Fortress-to-Harmonic transition during the Humble window or carry an unsupported simulator briefly.
- Some packages and ecosystem trends move ahead on Jazzy first; back-porting fixes occasionally slows.

Mitigations:

- Track REP 2000 and the Gazebo release lifecycle from `docs/concepts/software_overview.md`.
- Keep simulator-specific code in `crx10ial_sim` so a Fortress-to-Harmonic swap is a contained change, not a workspace-wide rewrite.
- Re-evaluate the Jazzy migration after M7 lands and the Humble path is fully validated.
````

- [ ] **Step 2: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/decisions/0001-adopt-ubuntu22-humble.md
git commit -m "docs: add ADR-0001 adopt Humble"
```

Expected: commit succeeds.

## Task 12: ADR 0002 - Use FANUC Official ROS 2 Driver

**Files:**
- Create: `docs/decisions/0002-use-fanuc-official-driver.md`

- [ ] **Step 1: Create `docs/decisions/0002-use-fanuc-official-driver.md`**

Create `docs/decisions/0002-use-fanuc-official-driver.md`:

````markdown
# 2. Use FANUC Official ROS 2 Driver

## Status

Accepted (2026-04-27)

## Context

Multiple options exist for ROS-driving a FANUC controller from Linux:

- **FANUC official ROS 2 driver** (`FANUC-CORPORATION/fanuc_driver`). Vendor-maintained. Includes `fanuc_description`, `fanuc_hardware_interface`, `fanuc_moveit_config`, and FANUC-specific controllers. Targets J519 Stream Motion + R912 RMI. Has a `humble` branch.
- **ROS-Industrial Fanuc** (`ros-industrial/fanuc`). Original, ROS 1 era driver. ROS 2 port is partial and community-maintained.
- **Unofficial ROS 2 Fanuc interface** (`paolofrance/ros2_fanuc_interface`). Single-author, smaller scope, no vendor backing.
- Custom driver development.

Scoring criteria the project cares about:

- Long-term support and bug-fix flow.
- Feature coverage: trajectory streaming, I/O, registers, payload, recovery.
- URDF and MoveIt config quality for the CRX series.
- Compatibility with iRVision integration via R[]/PR[].

## Decision

Use the **FANUC official ROS 2 driver** as the primary upstream for description, hardware interface, MoveIt configuration, and message types.

Specifically:

- Pin `fanuc_description` and `fanuc_driver` in `third_party.humble.repos` and `third_party.humble.lock.repos` to specific commits. Reproduce in M0 Task 1.
- Treat `ros-industrial/fanuc` and `paolofrance/ros2_fanuc_interface` as references only. Do not ship code that depends on them.
- Do not write a custom driver in M0-M7.

## Consequences

Positive:

- The robot model (`crx10ia_l`), MoveIt configuration, and SRDF are vendor-quality. The project trusts these, freeing engineering effort for cell, gripper, and task work.
- Future driver updates (new controller versions, fixes) flow from FANUC. The project follows by bumping the lock file.
- iRVision integration paths are aligned with what FANUC officially documents.

Negative:

- The project is dependent on FANUC's release cadence for upstream fixes. Some niche features may lag.
- The driver assumes specific software options (J519, R912). Hosts without those options cannot run the hardware path. M7 explicitly checks the option inventory.

Mitigations:

- Maintain a pinned-commit lock file so accidental upstream regressions are caught at the next intentional bump.
- Document required FANUC controller options in M7 prep and in `docs/concepts/hardware_overview.md`.
- Keep the project's gripper, vision, and task layers behind their own interfaces so a future driver change does not cascade through application code.
````

- [ ] **Step 2: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/decisions/0002-use-fanuc-official-driver.md
git commit -m "docs: add ADR-0002 FANUC official driver"
```

Expected: commit succeeds.

## Task 13: ADR 0003 - fake_gripper as Runtime Scene Owner (C1 Contract)

**Files:**
- Create: `docs/diagrams/c1_contract.svg`
- Create: `docs/decisions/0003-fake-gripper-as-runtime-scene-owner.md`

- [ ] **Step 1: Create `docs/diagrams/c1_contract.svg`**

Create `docs/diagrams/c1_contract.svg`:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 460" font-family="sans-serif" font-size="13">
  <rect width="800" height="460" fill="white"/>
  <text x="400" y="32" text-anchor="middle" font-size="18" font-weight="bold">C1 Contract: Runtime Planning Scene Ownership</text>

  <g stroke="#1f3a93" stroke-width="2" fill="#eaf0ff">
    <rect x="50" y="80" width="220" height="120" rx="6"/>
    <rect x="290" y="80" width="220" height="120" rx="6"/>
    <rect x="530" y="80" width="220" height="120" rx="6"/>
    <rect x="290" y="280" width="220" height="120" rx="6"/>
  </g>
  <g fill="#000">
    <text x="160" y="110" text-anchor="middle" font-weight="bold">crx10ial_tasks</text>
    <text x="160" y="135" text-anchor="middle" font-size="12">MTC Task::plan()</text>
    <text x="160" y="155" text-anchor="middle" font-size="12">No Task::execute()</text>
    <text x="160" y="175" text-anchor="middle" font-size="12">Mock orchestration</text>

    <text x="400" y="110" text-anchor="middle" font-weight="bold">MTC internal scene</text>
    <text x="400" y="135" text-anchor="middle" font-size="12">ModifyPlanningScene</text>
    <text x="400" y="155" text-anchor="middle" font-size="12">attachObject /</text>
    <text x="400" y="175" text-anchor="middle" font-size="12">detachObject (planning only)</text>

    <text x="640" y="110" text-anchor="middle" font-weight="bold">crx10ial_gripper</text>
    <text x="640" y="135" text-anchor="middle" font-size="12">attach_object</text>
    <text x="640" y="155" text-anchor="middle" font-size="12">detach_object</text>
    <text x="640" y="175" text-anchor="middle" font-size="12">command / get_state</text>

    <text x="400" y="310" text-anchor="middle" font-weight="bold">Runtime planning scene</text>
    <text x="400" y="335" text-anchor="middle" font-size="12">/apply_planning_scene</text>
    <text x="400" y="355" text-anchor="middle" font-size="12">/get_planning_scene</text>
    <text x="400" y="375" text-anchor="middle" font-size="12">(MoveIt 2)</text>
  </g>
  <g stroke="#27ae60" stroke-width="2" fill="none" marker-end="url(#a5)">
    <line x1="270" y1="140" x2="290" y2="140"/>
    <line x1="640" y1="200" x2="510" y2="280"/>
  </g>
  <g stroke="#c0392b" stroke-width="2" fill="none" stroke-dasharray="6,4">
    <line x1="510" y1="140" x2="530" y2="140"/>
    <text x="525" y="135" font-size="11" fill="#c0392b">forbidden</text>
    <line x1="400" y1="200" x2="400" y2="280"/>
    <text x="410" y="245" font-size="11" fill="#c0392b">never</text>
  </g>
  <defs>
    <marker id="a5" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 z" fill="#27ae60"/></marker>
  </defs>
  <text x="60" y="430" font-size="12" fill="#7f8c8d">Solid green: allowed dataflow. Red dashed: explicitly forbidden by source-contract test.</text>
</svg>
```

- [ ] **Step 2: Create `docs/decisions/0003-fake-gripper-as-runtime-scene-owner.md`**

Create `docs/decisions/0003-fake-gripper-as-runtime-scene-owner.md`:

````markdown
# 3. fake_gripper as Runtime Scene Owner (C1 Contract)

## Status

Accepted (2026-04-28)

## Context

In MoveIt 2, attached collision objects are usually written to the runtime planning scene by whichever component grabs an object: a MoveIt Task Constructor stage, a MoveGroupInterface client, or a custom node. The standard MTC pick/place tutorial uses MTC's `ModifyPlanningScene::attachObject()` and `Task::execute()` to drive both planning and runtime scene transitions.

This project has a different runtime story:

- The gripper has multiple future backends: a fake one for mock and Gazebo work, a controller-side iRVision-aware backend for ROBOGUIDE (M6), and a physical gripper backend (M7).
- Each backend updates the same runtime planning scene from a different physical pathway (Python service for fake, FANUC I/O for real).
- The planning task should not change shape when the underlying backend changes.

If MTC owns runtime attach/detach via `Task::execute()`, every backend swap requires changes to MTC stages and to the executor configuration. If MTC and the gripper service both write to `/apply_planning_scene`, ordering issues and double attachments are possible.

![C1 contract diagram](../diagrams/c1_contract.svg)

## Decision

Make `crx10ial_gripper` the sole writer to the runtime planning scene for attached collision objects.

Concretely:

- MTC stages may use `ModifyPlanningScene::attachObject()` and `detachObject()` only to update MTC's internal stage scene during planning.
- The project never calls `moveit::task_constructor::Task::execute()`. A pytest source-contract test in `crx10ial_tasks/test/test_task_source_contract.py` greps for `.execute(` and `execute_task_solution` in task and node sources and fails on either match.
- Mock execution drives motion through `MoveGroupInterface` and triggers attach/detach via the `crx10ial_gripper` services. The gripper service is the only ROS client of `/apply_planning_scene` for attach/detach diffs.
- A runtime check (`/get_planning_scene` after attach) asserts exactly one attached `work_object` and zero world `work_object` duplicates. This is part of the M3 execute_mock smoke.

## Consequences

Positive:

- Planning logic in `crx10ial_tasks` is independent of backend. Switching from fake to real iRVision-driven gripper does not change MTC stages.
- One named place to debug runtime scene corruption: any duplicate or missing attached object is by definition a `crx10ial_gripper` issue.
- Static enforcement (source-contract test) catches accidental violations during code review or auto-generated changes.

Negative:

- Mock execution must reorder operations relative to the textbook MTC flow. Specifically: pregrasp -> close -> attach -> move-to-grasp, instead of pregrasp -> move-to-grasp -> close -> attach. Without the reorder, the runtime scene still has the world `work_object` when the arm tries to reach the grasp pose, and goal collision rejects the plan.
- New contributors are unfamiliar with this convention because it differs from the MoveIt MTC tutorial. Mitigated by this ADR plus the documentation in `docs/architecture.md`.

## Enforcement

- `crx10ial_tasks/test/test_task_source_contract.py` greps for forbidden symbols and required structural patterns (pregrasp stage, attach-before-grasp ordering).
- M3 execute_mock smoke calls `/get_planning_scene` after attach and after detach; the C++ helper `verify_single_runtime_attachment` enforces the single-attached invariant.
- An external pytest, `check_single_attached_object.py`, verifies post-run state (`attached=0`, `world=1`).
````

- [ ] **Step 3: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 4: Commit**

Run:

```bash
git add docs/diagrams/c1_contract.svg docs/decisions/0003-fake-gripper-as-runtime-scene-owner.md
git commit -m "docs: add ADR-0003 C1 contract"
```

Expected: commit succeeds.

## Task 14: ADR 0004 - MTC Without Task::execute()

**Files:**
- Create: `docs/decisions/0004-mtc-without-task-execute.md`

- [ ] **Step 1: Create `docs/decisions/0004-mtc-without-task-execute.md`**

Create `docs/decisions/0004-mtc-without-task-execute.md`:

````markdown
# 4. MoveIt Task Constructor Without Task::execute()

## Status

Accepted (2026-04-28)

## Context

MoveIt Task Constructor (MTC) is a natural fit for fixed pick-and-place planning: stages compose into a graph, failures localize to the offending stage, and diagnostics are built in. For M3 the project chose MTC for the planning side.

A separate question is whether to call `moveit::task_constructor::Task::execute()` to drive the actual robot motion. `Task::execute()` sends an `ExecuteTaskSolution` action that, in addition to executing the trajectory, applies the same scene diffs MTC used during planning. That side effect collides with the C1 contract from [0003](0003-fake-gripper-as-runtime-scene-owner.md).

Three execution paths were considered:

- **Use `Task::execute()`**. Most concise. Implicitly violates C1.
- **Use `Task::execute()` and rewrite the gripper service to noop on attach/detach**. Possible but inverts ownership. The gripper backend would still need to track state machine transitions for hardware support; the runtime scene write would now live in MTC, breaking the "one place to debug" property.
- **Drive motion separately via `MoveGroupInterface` and call gripper services for attach/detach**. Slightly more code but preserves C1.

## Decision

Use MTC for planning only. Drive runtime motion through `MoveGroupInterface`. Trigger attach/detach through `crx10ial_gripper` services. The project does not call `Task::execute()` in M3 or any later milestone.

Implementation specifics:

- The MTC task in `crx10ial_tasks/src/fixed_pick_place_task.cpp` builds the full pick/place graph including `ModifyPlanningScene` stages for internal attach and detach.
- `plan_fixed_pick_place()` calls `task.plan(max_solutions)` and reports diagnostics. It does not return solutions for execution.
- `run_execute_mock()` re-derives waypoints (pregrasp, grasp, retreat, place, post-place) from configuration and the cell xacro, then sequences `MoveGroupInterface` moves with `crx10ial_gripper` service calls.
- A pytest source-contract check fails on any occurrence of `.execute(` or `execute_task_solution` in task or node sources.

## Consequences

Positive:

- Backend switching (fake -> Gazebo -> ROBOGUIDE -> hardware) never requires removing or rewriting MTC executor wiring.
- Runtime planning-scene state is single-sourced through `crx10ial_gripper`.
- Failure diagnostics from `Task::plan()` (`task.printState`, `task.explainFailure`) remain available for negative cases.

Negative:

- The mock execution path duplicates some logic that MTC already encodes (waypoint derivation, frame composition). The duplication is small (`translated_pose`, `compose_pose`) and lives in one file.
- Future contributors familiar with the MTC tutorial may try to call `Task::execute()`. The source-contract test catches this.

## Enforcement

- `crx10ial_tasks/test/test_task_source_contract.py` includes:
  - `assert ".execute(" not in combined`
  - `assert "execute_task_solution" not in combined`
- `check_docs.py` does not enforce this; it is a code-level invariant.
````

- [ ] **Step 2: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/decisions/0004-mtc-without-task-execute.md
git commit -m "docs: add ADR-0004 no Task::execute()"
```

Expected: commit succeeds.

## Task 15: ADR 0005 - Cell xacro as Single robot_description Source

**Files:**
- Create: `docs/decisions/0005-cell-xacro-as-single-robot-description.md`

- [ ] **Step 1: Create `docs/decisions/0005-cell-xacro-as-single-robot-description.md`**

Create `docs/decisions/0005-cell-xacro-as-single-robot-description.md`:

````markdown
# 5. Cell xacro as Single robot_description Source

## Status

Accepted (2026-04-27)

## Context

In M0/M1 the mock launch used `IncludeLaunchDescription(fanuc_mock_control.launch.py)` and let the FANUC mock launch expand its own URDF. MoveIt was given a separate `robot_description` derived from the FANUC `crx10ia_l.urdf.xacro`. There were effectively two URDFs: one for ros2_control (FANUC's view), one for MoveIt (FANUC's same xacro, separately expanded).

In M2 the workcell description grew. The cell xacro started including the FANUC ros2_control macro (`crx_mock_ros2_control_macro.xacro`) so that planning, controllers, and visualization shared a single URDF. With this change, including the upstream FANUC mock launch as-is would expand the FANUC URDF a second time, producing inconsistent state.

Three paths were considered:

- Keep `IncludeLaunchDescription(fanuc_mock_control.launch.py)` and override its `robot_description` parameter from outside.
- Stop including the FANUC mock launch and start the same controllers and nodes directly from the project launch.
- Continue with two URDFs and accept the duplication.

## Decision

Make the **cell xacro the single source of truth** for `robot_description`. The project's mock launch:

- Expands the cell xacro once.
- Feeds the expanded URDF to `controller_manager` (ros2_control), `robot_state_publisher`, and the MoveIt configuration via `MoveItConfigsBuilder.robot_description(file_path=cell_xacro_path, ...)`.
- Starts the FANUC controllers (`joint_state_broadcaster`, `joint_trajectory_controller`, `fanuc_gpio_controller`, `fanuc_force_sensor_broadcaster`, `force_torque_sensor_broadcaster`) directly via 5 spawner `ExecuteProcess` actions, mirroring the upstream FANUC mock launch.
- Starts `slider_gui_node` for parity with the upstream helper.

The launch file documents this choice with an inline comment near `control_node`.

## Consequences

Positive:

- One URDF: changes to the cell (frames, gripper, collision) propagate to MoveIt and ros2_control consistently.
- Project-defined frames (`tool_link`, `grasp_link`, gripper geometry) are visible to MoveIt for planning.
- The mock launch is self-contained; no upstream launch is included, so behaviour is reproducible without reading FANUC's launch file.

Negative:

- The project must track the FANUC controller list and timeouts. If FANUC adds or renames a controller in `fanuc_mock_control.launch.py`, the project's mock launch needs an explicit edit to follow.
- Future controllers introduced for hardware (M7) need similar mirroring rather than launch inclusion.

Mitigations:

- The project's launch file is short and easy to read. Diff it against `fanuc_mock_control.launch.py` periodically when bumping the FANUC lock pin.
- Keep an explicit comment block in `mock.launch.py` linking to this ADR so the rationale is local to the code.

## Related decisions

- [0003](0003-fake-gripper-as-runtime-scene-owner.md) - C1 contract. Also depends on a single planning scene source.
````

- [ ] **Step 2: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/decisions/0005-cell-xacro-as-single-robot-description.md
git commit -m "docs: add ADR-0005 single robot_description"
```

Expected: commit succeeds.

## Task 16: ADR Index

**Files:**
- Create: `docs/decisions/README.md`

- [ ] **Step 1: Create `docs/decisions/README.md`**

Create `docs/decisions/README.md`:

````markdown
# Architecture Decision Records

This directory holds the project's Architecture Decision Records (ADRs).

ADRs use the [Michael Nygard](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) format with four sections: Status, Context, Decision, Consequences. Filenames follow the `0001-<kebab-title>.md` convention so [adr-tools](https://github.com/npryce/adr-tools) can be adopted later without renaming.

## How to add a new ADR

1. Pick the next available number.
2. Create `docs/decisions/NNNN-<kebab-title>.md` with the four required sections.
3. Add an entry to the table below.
4. If the new ADR supersedes an older one, set the older ADR's `## Status` line to `Superseded by ADR-NNNN (<date>)`.
5. If the project later switches to `adr-tools`, run `adr generate toc > README.md` and the existing files require no changes.

## Index

| ID | Title | Status |
|---|---|---|
| 0001 | [Adopt Ubuntu 22.04 / ROS 2 Humble](0001-adopt-ubuntu22-humble.md) | Accepted |
| 0002 | [Use FANUC Official ROS 2 Driver](0002-use-fanuc-official-driver.md) | Accepted |
| 0003 | [fake_gripper as Runtime Scene Owner (C1 Contract)](0003-fake-gripper-as-runtime-scene-owner.md) | Accepted |
| 0004 | [MoveIt Task Constructor Without Task::execute()](0004-mtc-without-task-execute.md) | Accepted |
| 0005 | [Cell xacro as Single robot_description Source](0005-cell-xacro-as-single-robot-description.md) | Accepted |
````

- [ ] **Step 2: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/decisions/README.md
git commit -m "docs: add ADR index"
```

Expected: commit succeeds.

## Task 17: Operations - Hardware Inputs Intake

**Files:**
- Create: `docs/operations/hardware_inputs.md`

- [ ] **Step 1: Create `docs/operations/hardware_inputs.md`**

Create `docs/operations/hardware_inputs.md`:

````markdown
# Hardware Inputs Intake

This document is a structured questionnaire. M6 (ROBOGUIDE) and M7 (physical hardware) require these inputs to be filled in before plans can be drafted. The data lives in this file so it stays under version control and reviewable.

Fill in the answers in place. Use `TBD` only as a temporary placeholder; track open questions explicitly.

## Section 1 - Controller

- **Controller model**: ___ (e.g. R-30iB Mini Plus)
- **Controller software version**: ___ (e.g. V9.30P/16)
- **Boot ROM / OS variant**: ___
- **Authority of safety configuration (DCS/CSS)**: ___ (who manages these settings)

## Section 2 - FANUC software options

Tick installed options. Add date verified.

- [ ] **J519 Stream Motion** (verified ___)
- [ ] **R912 Remote Motion Interface (RMI)** (verified ___)
- [ ] **S636 External Control Package** (verified ___)
- [ ] **iRVision** (verified ___)
- [ ] **KAREL** (verified ___) - needed for any custom TP/socket bridge fallback
- [ ] **Other**: ___

If iRVision is installed, also record:

- **iRVision license type** (TBD: 2D, 2DV, 3DL, etc.): ___
- **Available cameras**: ___

## Section 3 - Robot

- **Robot model**: CRX-10iA/L (assumed)
- **Serial number**: ___
- **Mounting orientation**: floor / inverted / wall (circle one)
- **Reach in current cell layout**: ___ m
- **DCS zones configured** (Cartesian/joint, count, owner): ___

## Section 4 - End effector and payload

- **Gripper make/model**: ___ (e.g. Robotiq 2F-85, OnRobot RG2, custom vacuum)
- **Gripper interface**: digital I/O / RS-485 / Ethernet / other: ___
- **DI lines used**: ___
- **DO lines used**: ___
- **Tool weight**: ___ kg
- **Tool centre of mass offset**: (x, y, z) ___ m
- **Tool inertia (if known)**: ___
- **Payload schedule index** in controller: ___ (P[___])
- **Maximum payload during operation**: ___ kg

## Section 5 - Workcell environment

- **Table dimensions** (x, y, z): ___ m, ___ m, ___ m
- **Table position** (world frame): ___
- **Camera mounting**: type ___, position ___, orientation ___
- **Other fixtures, conveyors, sensors**: ___
- **Workspace soft limits planned for `crx10ial_safety`**: ___

## Section 6 - iRVision

If iRVision is in scope:

- **Calibration plate / fiducial**: ___
- **Camera calibration done? date / RMS error**: ___
- **Job names planned**: ___
- **Per-job result code register (R[N])**: ___
- **Per-job found-pose register (PR[N])**: ___ (if PR[] supported, else encoding scheme)
- **Trigger DO line**: ___
- **Busy DI line**: ___
- **Complete DI line**: ___
- **Coordinate frame the job reports in**: ___ (e.g. user frame UF[2])
- **Mapping from user frame to ROS `world`**: ___

## Section 7 - Network

- **Robot controller IP**: ___
- **Subnet mask**: ___
- **Default gateway**: ___
- **ROS PC IP** on the same subnet: ___
- **Network isolation**: dedicated switch / shared LAN / VPN: ___
- **FANUC ports opened** (J519 default, RMI default, FTP, etc.): ___

## Section 8 - ROBOGUIDE (for M6)

- **ROBOGUIDE version**: ___
- **Windows host OS**: ___
- **Connection method between ROS PC and ROBOGUIDE**: bridged VM / external host / other: ___
- **Available virtual controller image and FANUC software version**: ___

## Section 9 - Operations and roles

- **Owner of safety review for M7 hardware bringup**: ___
- **Owner of E-stop integration**: ___
- **Operator(s) trained on Teach Pendant**: ___
- **Reduced-speed mode policy during ROS commanding**: ___ (e.g. T1 only, T2 with supervision, etc.)

## Section 10 - Open questions

Use this section for items that cannot be resolved at intake time.

- ___

## Change log

| Date | Editor | Change |
|---|---|---|
| 2026-04-28 | Codex | Created intake form |
````

- [ ] **Step 2: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/operations/hardware_inputs.md
git commit -m "docs: add hardware inputs intake form"
```

Expected: commit succeeds.

## Task 18: Operations - ROBOGUIDE Setup Checklist

**Files:**
- Create: `docs/operations/roboguide_setup_checklist.md`

- [ ] **Step 1: Create `docs/operations/roboguide_setup_checklist.md`**

Create `docs/operations/roboguide_setup_checklist.md`:

````markdown
# ROBOGUIDE Setup Checklist

Pre-flight checks before starting M6 (ROBOGUIDE integration). Complete top-to-bottom; each section gates the next.

Source of truth for the inputs referenced here: [`hardware_inputs.md`](hardware_inputs.md).

## A. Inputs and authority

- [ ] `hardware_inputs.md` Section 1 (Controller) is filled in.
- [ ] `hardware_inputs.md` Section 2 (Options) confirms J519 + R912 (or S636) installed in the virtual controller.
- [ ] `hardware_inputs.md` Section 7 (Network) defines reachable IPs between Linux PC and Windows ROBOGUIDE host.
- [ ] `hardware_inputs.md` Section 8 (ROBOGUIDE) records the ROBOGUIDE version and Windows host details.

## B. Windows ROBOGUIDE host

- [ ] ROBOGUIDE installed and licensed.
- [ ] Virtual controller image matches the FANUC software version recorded in `hardware_inputs.md`.
- [ ] Cell project loaded with the CRX-10iA/L robot.
- [ ] DCS profile in the virtual controller mirrors the planned physical DCS settings (close approximation acceptable).
- [ ] Required FANUC options enabled in the virtual controller (J519, R912, iRVision if applicable).
- [ ] Static IP assigned to the virtual controller; reachable from the Linux ROS PC by `ping`.
- [ ] FTP enabled if needed for TP program upload.

## C. Linux ROS PC

- [ ] Workspace built and tested in mock mode (`docs/quickstart.md`).
- [ ] `third_party.humble.lock.repos` pinned commits are sufficient (no driver bump pending).
- [ ] FANUC driver supports the FANUC controller version of the virtual image (verify `fanuc_driver_doc/quick_start`).
- [ ] Project bringup launch supports a `roboguide` mode argument (M6 plan deliverable; not present yet).

## D. Network and connectivity

- [ ] Robot IP / subnet documented in `hardware_inputs.md`.
- [ ] FANUC default ports reachable from the Linux PC (J519, RMI, FTP). If running across hosts/VMs, confirm bridged networking or port forwarding.
- [ ] Linux firewall (`ufw`, etc.) allows outbound and inbound on the relevant ports.
- [ ] Time sync between Linux and Windows acceptable (within 1-2 s); adjust if commands appear to "lag".

## E. iRVision readiness (only if iRVision is in scope for M6)

- [ ] Camera calibrated inside ROBOGUIDE; calibration error within acceptable bounds.
- [ ] User frame and tool frame defined in the virtual controller.
- [ ] Vision job created with deterministic result.
- [ ] Trigger DO and busy/complete DI mapping documented in `hardware_inputs.md` Section 6.
- [ ] Result register (`R[N]`) and found-pose register (`PR[N]`) chosen and reserved.
- [ ] PR[] read access from ROS verified or a fallback scheme decided (numeric register encoding or KAREL/socket bridge).

## F. Test plan in ROBOGUIDE

Once A-E are checked:

- [ ] Read-only checks: `/joint_states` reflects ROBOGUIDE robot pose changes.
- [ ] DI/DO read works.
- [ ] Numeric register read works.
- [ ] Position register read works (or fallback documented).
- [ ] Single small Cartesian motion executes safely in the virtual controller via the project bringup launch.
- [ ] iRVision trigger / readback path completes one round trip (only when iRVision is in scope).

## Failure modes and their first checks

- **Cannot ping virtual controller**: confirm bridged networking, virtual controller's IP assignment, Windows firewall.
- **`/plan_kinematic_path` plans but execution stalls**: check J519 Stream Motion enabled, controller is in remote mode, RMI session open.
- **Trajectory rejected with payload error**: payload schedule mismatch; align payload P[] index in virtual controller with what the project's launch sends.
- **PR[] read returns empty**: PR access depends on driver+controller version. Check `fanuc_driver` documentation and, if unsupported, switch the iRVision bridge to numeric-register encoding fallback.

## Exit criteria

ROBOGUIDE phase is complete when section F's items are all green and the M6 plan's acceptance checks pass.
````

- [ ] **Step 2: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/operations/roboguide_setup_checklist.md
git commit -m "docs: add ROBOGUIDE setup checklist"
```

Expected: commit succeeds.

## Task 19: Operations - Hardware Bringup Checklist

**Files:**
- Create: `docs/operations/hardware_bringup_checklist.md`

- [ ] **Step 1: Create `docs/operations/hardware_bringup_checklist.md`**

Create `docs/operations/hardware_bringup_checklist.md`:

````markdown
# Hardware Bringup Checklist

Pre-flight checks before starting M7 (physical CRX-10iA/L bringup). M7 is gated by safety review and by ROBOGUIDE validation in M6. Do not skip sections.

Source of truth for inputs: [`hardware_inputs.md`](hardware_inputs.md).

## A. Authority and authorization

- [ ] Safety review completed and signed off (owner: `hardware_inputs.md` Section 9).
- [ ] Operator trained on Teach Pendant and on this project's launch syntax.
- [ ] E-stop integration verified by a trained operator (button on robot, button at workstation, controller integration).
- [ ] DCS zones configured to match `hardware_inputs.md` Section 3.
- [ ] Reduced-speed mode policy documented and posted at the cell.

## B. M6 prerequisites

- [ ] M6 ROBOGUIDE integration completed and PR[] (or fallback) path validated.
- [ ] `crx10ial_vision_bridge` (if iRVision is in scope) tested in ROBOGUIDE.
- [ ] Project bringup launch's `mode:=roboguide` profile passes its smoke checks.

## C. Physical environment

- [ ] Workcell physically matches the dimensions in `crx10ial_cell_description` and `mock_scene` within tolerance.
- [ ] Table is fixed; no slip during operation.
- [ ] Camera mounted, focused, and at the documented pose.
- [ ] Gripper installed; mechanical and electrical connections confirmed.
- [ ] No personnel in DCS zones during commissioning.
- [ ] Lighting adequate for iRVision (only if applicable).

## D. Controller settings on the real robot

- [ ] Controller software version matches `hardware_inputs.md` Section 1.
- [ ] FANUC options match Section 2.
- [ ] Payload schedule P[N] reflects the actual gripper plus expected work_object weight.
- [ ] Tool frame UT[N] matches `tool_link` offset in the cell xacro.
- [ ] User frame UF[N] for the cell aligns with ROS `world`.
- [ ] iRVision job names and registers match `hardware_inputs.md` Section 6 (only if applicable).
- [ ] J519 Stream Motion enabled and tested in T1 mode.
- [ ] RMI session can be opened from the Linux PC (verify with FANUC's `quick_start` instructions).

## E. Linux ROS PC

- [ ] Workspace builds clean.
- [ ] M3 mock smoke passes immediately before M7 bringup.
- [ ] Hardware launch file requires explicit `mode:=hardware` and `robot_ip:=...` (no defaults that would let mock-style command lines accidentally drive hardware).
- [ ] Hardware launch file requires `allow_motion:=true` for any motion command. Status reads remain available without it.
- [ ] Logs configured (file + stdout); commands are recorded.

## F. Bringup sequence (in this order)

Each step is gated by the previous one passing. Do not skip ahead.

- [ ] **F1 - Status only.** Run hardware launch with `allow_motion:=false`. Verify `/joint_states` matches the Teach Pendant's reported joint values within tolerance. Read DI/DO. No motion commanded.
- [ ] **F2 - I/O write.** With operator confirmation, write a single non-actuating DO. Verify reflected in Teach Pendant.
- [ ] **F3 - Single small joint motion.** With T1 mode, reduced speed (<= 25 percent), and `allow_motion:=true`, command a small (<= 5 deg) joint move via `MoveGroupInterface`. Operator hand on E-stop. Confirm motion magnitude matches command.
- [ ] **F4 - Small Cartesian motion.** Same posture as F3, command a small (<= 50 mm) Cartesian move from `flange`. Operator hand on E-stop.
- [ ] **F5 - Static planning scene + gripper.** Bring up the same workcell collision scene as mock. Open / close gripper at a safe pose. Confirm gripper hardware responds.
- [ ] **F6 - iRVision round trip** (only if applicable). Trigger the vision job, read R[]/PR[], log the detected pose. Do not act on it yet.
- [ ] **F7 - Pick attempt.** Only after F1-F6 are green and a second safety review confirms readiness. Use M3 fixed pick/place at the lowest configured speed scaling and with the operator at the E-stop.

## G. Recovery procedures

Document in this section how the team will recover from each named failure. Do not skip; this is the difference between a controlled stop and an incident.

- [ ] **Connection loss to controller**: ___
- [ ] **RMI session timeout**: ___
- [ ] **Robot fault on controller**: ___
- [ ] **E-stop pressed during motion**: ___
- [ ] **Planning failure during execution**: ___
- [ ] **Unexpected attached-object state at exit (object stuck in gripper)**: ___
- [ ] **iRVision returns invalid result**: ___

## H. Exit criteria

The hardware phase is provisionally complete when:

- F1-F5 are green.
- The team has demonstrated a clean recovery for at least one of the failure modes in section G.
- A reviewer signs off on the controller and ROS logs from F1-F5.

A successful F7 pick attempt is **not** required to mark M7 done; the deliverable is repeatable, reviewed status/I/O/motion plus iRVision trigger validation. Full pick-and-place execution remains gated by additional safety review.
````

- [ ] **Step 2: Run quality check**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`.

- [ ] **Step 3: Commit**

Run:

```bash
git add docs/operations/hardware_bringup_checklist.md
git commit -m "docs: add hardware bringup checklist"
```

Expected: commit succeeds.

## Task 20: README Integration

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Read the existing top-level README**

Run:

```bash
cat README.md
```

Note the existing structure. The existing M0 README has a project overview, target environment, bootstrap, and mock launch.

- [ ] **Step 2: Replace `README.md`**

Replace `README.md` with the content below. Preserve the existing project overview paragraph; add navigation to the new docs.

````markdown
# Fanuc_Robotics

ROS 2 Humble workspace for validating FANUC CRX-10iA/L visualization, MoveIt mock planning, fixed pick-and-place, and later staged integration with simulation, ROBOGUIDE, hardware, and iRVision.

## Target Environment

- Ubuntu 22.04 LTS
- ROS 2 Humble Hawksbill
- Robot model: FANUC CRX-10iA/L (`crx10ia_l`)
- Primary upstream stack: FANUC official ROS 2 driver and description packages

For background, see [docs/concepts/software_overview.md](docs/concepts/software_overview.md) and [docs/concepts/hardware_overview.md](docs/concepts/hardware_overview.md).

## New here?

- [docs/quickstart.md](docs/quickstart.md) takes you from clone to running the M3 mock pick/place demo.
- [docs/concepts/](docs/concepts/) holds beginner-friendly overviews of the hardware, software stack, and a project glossary.
- [docs/architecture.md](docs/architecture.md) explains the four-layer architecture and the package responsibilities.

## Reference

- [docs/frames.md](docs/frames.md) - canonical frame conventions for the workcell.
- [docs/services_and_launches.md](docs/services_and_launches.md) - every project-defined service and launch file.
- [docs/yaml_schemas.md](docs/yaml_schemas.md) - configuration YAML reference.
- [docs/troubleshooting.md](docs/troubleshooting.md) - symptoms and fixes from M0-M3.

## Decisions

- [docs/decisions/](docs/decisions/) - architecture decision records (ADRs).

## Operations

- [docs/operations/hardware_inputs.md](docs/operations/hardware_inputs.md) - intake form for M6/M7 inputs.
- [docs/operations/roboguide_setup_checklist.md](docs/operations/roboguide_setup_checklist.md) - pre-flight for M6.
- [docs/operations/hardware_bringup_checklist.md](docs/operations/hardware_bringup_checklist.md) - pre-flight for M7.

## Bootstrap

```bash
source /opt/ros/humble/setup.bash
sudo apt update
sudo apt install -y git git-lfs python3-vcstool python3-colcon-common-extensions python3-rosdep
./scripts/import_dependencies.sh third_party.humble.lock.repos
sudo apt install -y ros-humble-moveit-task-constructor-core ros-humble-moveit-task-constructor-msgs ros-humble-moveit-task-constructor-capabilities ros-humble-moveit-task-constructor-visualization
rosdep install --from-paths src --ignore-src -r -y --rosdistro humble --skip-keys ament_python
colcon build --symlink-install
source install/setup.bash
```

## Mock Launch

```bash
source /opt/ros/humble/setup.bash
source install/setup.bash
ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=true publish_scene:=true launch_gripper:=true
```

For headless smoke checks:

```bash
timeout 45s ros2 launch crx10ial_bringup mock.launch.py launch_rviz:=false publish_scene:=true launch_gripper:=true
```

The timeout command exits with code `124` after the launch reaches steady state.

## Status

| Milestone | Status |
|---|---|
| M0 Workspace Foundation | Done |
| M1 RViz and MoveIt Mock | Done |
| M2 Workcell and Gripper Model | Done |
| M3 Fixed Pick-and-Place | Done |
| M4 Gazebo Fortress Simulation | Planned |
| M5 Vision Interface (fake/sim) | Planned |
| M6 ROBOGUIDE Integration | Planned |
| M7 Physical Hardware Bringup | Planned |

See `docs/superpowers/specs/2026-04-27-ubuntu22-humble-crx10ial-design.md` for the full design.
````

- [ ] **Step 3: Restore link wrappers in earlier docs**

The earlier Tier 0/1/2/3 tasks may have stripped some `[text](path)` links to plain text when their targets did not yet exist. Re-link them now. Search for known forward-reference candidates and convert:

```bash
grep -rn 'docs/decisions/0003' docs/concepts/ docs/quickstart.md docs/frames.md docs/architecture.md docs/troubleshooting.md docs/services_and_launches.md docs/yaml_schemas.md 2>/dev/null
grep -rn 'docs/decisions/0005' docs/concepts/ docs/quickstart.md docs/frames.md docs/architecture.md docs/troubleshooting.md docs/services_and_launches.md docs/yaml_schemas.md 2>/dev/null
grep -rn 'docs/frames.md' docs/concepts/ 2>/dev/null
grep -rn 'docs/architecture.md' docs/concepts/ 2>/dev/null
```

For each plain-text reference to a now-existing target, edit the file to use a Markdown link with a relative path. Examples:

- `decisions/0003` -> `[decisions/0003](../decisions/0003-fake-gripper-as-runtime-scene-owner.md)` (when reading from a doc inside `docs/concepts/`).
- Inside `docs/architecture.md`: `docs/decisions/0003` -> `[decisions/0003](decisions/0003-fake-gripper-as-runtime-scene-owner.md)`.

- [ ] **Step 4: Run quality check on the entire docs tree**

Run:

```bash
python3 scripts/check_docs.py
```

Expected: exits `0`. All links must resolve. All ADRs must contain the four required sections. All fences must balance.

- [ ] **Step 5: Run a final fence and link audit manually**

Run:

```bash
ls docs/diagrams/*.svg | sort
ls docs/concepts/*.md | sort
ls docs/decisions/*.md | sort
ls docs/operations/*.md | sort
ls docs/*.md | sort
```

Expected: 8 SVGs, 4 concepts, 6 decisions (5 ADRs + README), 3 operations, and at least 4 top-level (`quickstart.md`, `architecture.md`, `troubleshooting.md`, `frames.md`, `services_and_launches.md`, `yaml_schemas.md`, plus existing ones).

- [ ] **Step 6: Commit README update**

Run:

```bash
git add README.md
git diff --cached --stat
git commit -m "docs: integrate handbook into top-level README"
```

Expected: commit succeeds.

- [ ] **Step 7: Push the branch**

Run:

```bash
git push -u origin docs/handbook
git rev-parse HEAD
git ls-remote origin refs/heads/docs/handbook
```

Expected: local HEAD matches the remote branch SHA. Branch `docs/handbook` exists on `origin`.

## Self-Review Checklist

- [x] All Tier 0 documents (4) are produced by Tasks 1-4.
- [x] All Tier 1 documents (3) are produced by Tasks 5-7.
- [x] All Tier 2 documents (3) are produced by Tasks 8-10.
- [x] All Tier 3 ADR documents (5) are produced by Tasks 11-15, plus the index in Task 16.
- [x] All Tier 4 operations documents (3) are produced by Tasks 17-19.
- [x] Top-level `README.md` is integrated in Task 20.
- [x] `scripts/check_docs.py` is committed in Task 0 and runs at every Task before commit.
- [x] Each Markdown document is committed by itself (one document, one commit), per the agreed granularity.
- [x] Diagrams (8 SVGs) are produced inline in the tasks that introduce them.
- [x] ADR file names follow the `0001-<kebab-title>.md` convention so adr-tools can be adopted later without rename.
- [x] ADRs use the Michael Nygard four-section template (Status / Context / Decision / Consequences).
- [x] Forward-referenced links in early Tier 0/1 docs are reconnected in Task 20 once all targets exist.
- [x] M4-M7 milestones are not implemented; only their preparatory documents are.
- [x] No code changes outside `docs/` and `scripts/check_docs.py`.
- [x] Branch `docs/handbook` is pushed to `origin/docs/handbook`.
