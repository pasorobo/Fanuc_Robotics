# crx10ial_interfaces

Shared ROS 2 interfaces for the CRX-10iA/L workcell.

## Gripper services

- `CommandGripper`: command the fake gripper to open, close, enable vacuum state, or disable vacuum state.
- `AttachObject`: attach a known world collision object to the configured gripper link.
- `DetachObject`: detach the currently held object and restore it as a world collision object.
- `GetGripperState`: read the fake gripper state.
