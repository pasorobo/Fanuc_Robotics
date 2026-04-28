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
