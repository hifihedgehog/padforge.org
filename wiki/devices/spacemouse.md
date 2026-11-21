# 3Dconnexion SpaceMouse

*Use a 6DoF puck as a mapping source: three translation axes and three rotation axes, all moving at once, plus the device's buttons.*

A SpaceMouse announces itself to Windows as a multi-axis controller, a device class that game input APIs ignore. Games never see it, and neither do most mappers. PadForge reads the puck directly and presents it as a joystick with six axes and 32 buttons, so every part of the app that works on a joystick axis works on it: mapping rows, curves, deadzones, macros, per-app profiles, and virtual controller output.

No setup. Plug it in (or connect its receiver) and it appears on the [Devices](../features/devices.md) page under the product name the device reports, or as **SpaceMouse** when it reports none. PadForge looks for new pucks every two seconds.

---

## The axes

Six bipolar axes, one per degree of freedom. Push, pull, twist, and tilt read simultaneously, which is the point of the device: a flight sim can take translation and rotation from one hand in one motion.

| Source | Motion |
|---|---|
| **Axis 0** | Translation X: slide left / right |
| **Axis 1** | Translation Y: slide toward / away |
| **Axis 2** | Translation Z: pull up / press down |
| **Axis 3** | Rotation X (pitch): tilt forward / back |
| **Axis 4** | Rotation Y (roll): tilt left / right |
| **Axis 5** | Rotation Z (yaw): twist |

The puck is spring-centered, so each axis rests at exactly zero and returns there when released. It behaves like a self-centering analog stick, not like a gyro: map the axes in the **Mappings** section of the controller page ([Mappings](../features/mappings.md)) like any stick or trigger, and shape them with the usual [deadzone and curve](../features/stick-deadzones.md) controls. PadForge passes the puck's raw axis values through with no sign correction, so each direction is whatever the hardware reports. If a motion feels backwards for your game, invert that row's axis.

Buttons map as ordinary buttons. PadForge gives the puck 32 buttons, which covers every model from the SpaceNavigator's two up to the SpaceMouse Enterprise's 31.

---

## Supported models

Both 3Dconnexion vendor IDs are covered. Under the current one, PadForge takes any device that describes itself to Windows as a multi-axis controller, so a model missing from the list below works too. Under the Logitech-era ID it takes only the twelve products listed.

| Generation | Models |
|---|---|
| Current (VID 256F) | Every 6DoF model, among them the SpaceMouse Compact, SpaceMouse Wireless, SpaceMouse Pro Wireless, SpaceMouse Enterprise and the Universal Receiver |
| Logitech era (VID 046D) | SpaceNavigator, SpaceNavigator for Notebooks, SpaceMouse Pro, SpaceMouse Classic, SpaceMouse Plus XT, SpaceExplorer, SpaceTraveler, SpacePilot, SpacePilot Pro, Spaceball 5000, CadMan, NuLOOQ |

The CadMouse and Keyboard Pro families share 3Dconnexion's vendor ID but are pointing and typing devices, not 6DoF pucks. They describe themselves to Windows as a mouse or a keyboard, not as a multi-axis controller, so PadForge leaves them alone.

---

## Alongside 3DxWare

3Dconnexion's own driver can stay installed. PadForge opens the puck shared, and Windows delivers every report to each program that has it open, so PadForge and 3DxWare read the same motion side by side. CAD keeps working while a game takes the mapped output.

*Last updated for PadForge 6.0.0.*
