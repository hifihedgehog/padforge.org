# 3Dconnexion SpaceMouse

*Use a 6DoF puck as a mapping source: three translation axes and three rotation axes, all moving at once, plus the device's buttons.*

A SpaceMouse announces itself to Windows as a multi-axis controller, a device class that game input APIs ignore. Games never see it, and neither do most mappers. PadForge reads the puck directly and presents it as a six-axis controller, so every part of the app that works on a gamepad axis works on it: mapping rows, curves, deadzones, macros, per-app profiles, and virtual controller output.

No setup. Plug it in (or connect its receiver) and it appears on the [Devices](../features/devices.md) page under its own name.

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

The puck is spring-centred, so each axis rests at exactly zero and returns there when released. It behaves like a self-centring analog stick, not like a gyro: map the axes on the [Mappings](../features/mappings.md) tab like any stick or trigger, and shape them with the usual [deadzone and curve](../features/stick-deadzones.md) machinery. Directions follow the device's own right-handed convention. If a motion feels backwards for your game, invert that row's axis.

Buttons map as ordinary buttons. Every model's buttons fit, from the SpaceNavigator's two up through the SpaceMouse Enterprise's full bank.

---

## Supported models

Both 3Dconnexion vendor generations are covered.

| Generation | Models |
|---|---|
| Current (VID 256F) | SpaceMouse Compact, SpaceMouse Wireless, SpaceMouse Pro, SpaceMouse Pro Wireless (USB or Bluetooth), SpaceMouse Enterprise, SpaceMouse Module, the Universal Receiver |
| Logitech era (VID 046D) | SpaceNavigator, SpaceNavigator for Notebooks, SpaceMouse Pro, SpaceMouse Classic, SpaceMouse Plus XT, SpaceExplorer, SpaceTraveller, SpacePilot, SpacePilot Pro, Spaceball 5000, CadMan, NuLOOQ |

The CadMouse and Keyboard Pro families share 3Dconnexion's vendor ID but are pointing and typing devices, not 6DoF pucks. PadForge tells them apart by how the hardware describes itself and leaves them alone.

---

## Alongside 3DxWare

3Dconnexion's own driver can stay installed. Windows delivers the puck's input to every application that opens it, so PadForge and 3DxWare read the same motion side by side. CAD keeps working while a game takes the mapped output.

*Last updated for PadForge 4.3.0.*
