# VR Controller Input

*Your VR motion controllers as two ordinary device rows. Their pose, sticks, triggers, grips and buttons map like any gamepad's.*

When [OpenXR Headset Input](head-tracking.md) is on, PadForge reads the hand controllers from the same runtime and presents each one as its own device row. Waving a Touch controller can drive a stick, its trigger can drive a trigger, and its buttons bind like any other buttons.

This page is about reading real VR controllers *into* PadForge. For the opposite direction, presenting a virtual left and right hand *to* SteamVR, see [Virtual VR Controllers](vr-controllers.md).

---

## Turning it on

There is no separate switch. Enable **OpenXR Headset Input** on the [Dashboard](dashboard.md)'s Head Tracking section and both controller rows appear. They are there whether or not a runtime ever answers, so mappings can be made before a headset is plugged in. A row that never goes live simply holds its axes at rest.

Two rows show up on the [Devices](devices.md) page, typed **VR Controller**:

- **VR Controller (Left)**
- **VR Controller (Right)**

They are separate devices with separate identities, so a mapping on one survives the other going to sleep, and losing one hand does not disturb the other.

---

## What each row exposes

Ten axes and four buttons.

| Axis | Raw view | What it reads |
| --- | --- | --- |
| Controller Yaw | Axis 0 | turning the controller left and right |
| Controller Pitch | Axis 1 | tipping it up and down |
| Controller Roll | Axis 2 | rolling it toward a thumb |
| Controller X | Axis 3 | moving it left and right |
| Controller Y | Axis 4 | raising and lowering it |
| Controller Z | Axis 5 | pushing it away and pulling it back |
| Thumbstick X | Axis 6 | the stick left and right |
| Thumbstick Y | Axis 7 | the stick up and down |
| Trigger | Axis 8 | the index trigger, resting at zero |
| Grip | Axis 9 | the squeeze, resting at zero |

| Button | Raw view |
| --- | --- |
| Thumbstick Click | Button 0 |
| Primary Button | Button 1 |
| Secondary Button | Button 2 |
| Menu Button | Button 3 |

The six pose axes come first, in the same order as the [Head Tracker](head-tracking.md) row's, so an axis you already know how to map sits where you expect. The names say Controller rather than Head, because the two rows are different devices. They rest at center and take the same shared and per-axis ranges the headset pose uses.

Trigger and Grip rest at zero rather than center, the way a gamepad's triggers do. An Axis Past Threshold activator on either knows that, so it sits disengaged at rest instead of firing the moment you save it.

---

## Which controllers work

PadForge suggests bindings for three interaction profiles and the runtime picks whichever matches your hardware:

- Oculus Touch controllers
- Valve Index controllers
- The Khronos simple controller, the fallback profile every conformant runtime supports

A controller the runtime maps to the simple profile reports far fewer controls, because that profile defines only a pose and two buttons. There is no stick, no trigger and no grip in it, so those axes stay at rest and Primary and Menu are the only buttons that move.

---

## Mapping it

The rows bind anywhere a gamepad does. An **Any Device** source never reads them, so pick the controller by name. That is deliberate: these rows speak their own vocabulary, and an Any Device row asking for "Button 1" should not suddenly answer from a headset controller.

Auto-map covers gamepads only, so each control is bound by hand.

---

## When a controller goes quiet

Set a controller down, or let it sleep, and after one second without a sample every axis returns to rest and every button releases. A stick is never left held by a controller lying on a desk.

The row stays online while the session is up, so mappings can be made before you pick the controller back up.

---

## Related pages

- [Head Tracking](head-tracking.md): the OpenXR headset input these rows come with, and the ranges they share.
- [Virtual VR Controllers](vr-controllers.md): the other direction, PadForge presenting hands to SteamVR.
- [Devices](devices.md): the device rows.
- [OpenXR Input Internals](../reference/openxr-input-internals.md): the runtime negotiation, session and action set, for whoever has to change the code.

---

*Last updated for PadForge 4.5.0.*
