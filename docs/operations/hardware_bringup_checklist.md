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
