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
