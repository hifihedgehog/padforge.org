# Steering

*Two per-stick steering modes make a thumbstick act like a steering wheel, plus a Motion Lean input that steers from controller tilt.*

Winding and Angle to Axis live on the **Sticks** tab, one mode per stick, and write to the stick's virtual axis. Motion Lean is a separate input you map like a gyro source, tuned on the **Gyro** tab. The math follows JoyShockMapper's steering stick modes. The at-lock haptic feedback is PadForge's addition.

Every mode is off by default. With the mode set to **Off**, the stick is a normal stick. Pick a mode to make it act like a steering wheel.

## Modes

### Winding

Rotating the stick winds a virtual wheel. Turn clockwise and the wheel turns right. **Wind Range** is the total lock-to-lock travel. The default 900 is 2.5 turns from one lock to the other, so full lock lands at 450 degrees (1.25 turns) each way from center. The accumulator tracks total angular travel, not the stick's current position, so you can keep winding past lock and then unwind back through the overshoot.

Below full deflection the wind leaks back toward center at **Unwind Rate** degrees per second (default 1800), scaled by how far you've released, so a partial release bleeds slowly and a full release snaps back. **Wind Power** (default 1) curves the output: above 1 makes the approach to lock gentler, below 1 sharper.

| Setting | Default | Range |
| --- | --- | --- |
| Wind Range | 900° | 90–2520 |
| Wind Power | 1 | 0–4 |
| Unwind Rate | 1800°/s | 0–10000 |

### Angle to Axis

Positional, no accumulator. The stick's angle relative to one axis maps straight to that axis. Before deadzones, holding the stick at 45° gives half output and pushing to 90° saturates. Magnitude scales with how far the stick is deflected, and releasing the stick drops the output immediately.

It projects onto a half-plane, so up-and-right and down-and-right read the same angle. Pick **Angle to Axis (X)** to drive the X axis or **Angle to Axis (Y)** for Y. A common driving layout pairs one stick's X variant with steering and leaves the other axis for throttle.

| Setting | Default | Range |
| --- | --- | --- |
| Angle Inner Deadzone | 0° | 0–89 |
| Angle Outer Deadzone | 10° | 0–89 |

The outer deadzone is measured from 90°, so the default reaches full lock at 80° instead of forcing an exact 90°.

### Motion Lean

Motion Lean is not a stick mode. It's an input you pick from the input dropdown, like any gyro source, and map to a steering axis. Its tuning lives on the **Gyro** tab's Motion Steering card, not the Sticks tab. Gravity, read through the same source the Gyro tab uses, drives the axis. **Controller Orientation** tells PadForge which way the controller is held (Forward, Left, Right, Backward) so the lean axis is correct.

With the default deadzones, lock lands near 45° of tilt from neutral. The inner deadzone covers small neutral wobble.

| Setting | Default | Range |
| --- | --- | --- |
| Lean Inner Deadzone | 15° | 0–179 |
| Lean Outer Deadzone | 135° | 0–179 |
| Controller Orientation | Forward | Forward / Left / Right / Backward |

A Wii Nunchuk or a left Joy-Con exposes its own lean source in the input dropdown, **Nunchuk Lean** or **Left Joy-Con Lean**. It steers from that second sensor's tilt, using the same math and the same Motion Steering card tuning.

Motion Lean needs a controller with a motion sensor. Without one it produces no output.

## At-lock feedback

When a steering source saturates at full lock, PadForge can make the wheel feel like it hit a wall. The **Steering Lock Feedback** card sits at the bottom of the **Sticks** tab. Every channel is per-slot and off by default, and rows the selected device can't play are hidden.

| Toggle | What it does | Hardware |
| --- | --- | --- |
| **Rumble Pulse on Lock** | Grip-motor pulse on lock entry | Any pad with rumble |
| **Trigger Vibration on Lock** | The same pulse on the trigger actuators | Xbox One and later impulse triggers, DualSense adaptive triggers |
| **Lightbar Pulse on Lock** | Lightbar flashes a color on lock entry | DualSense / DualShock 4 |
| **Trigger Resistance near Lock** | DualSense trigger resistance ramps up as the wheel approaches lock, so you feel it coming | DualSense |

**Trigger Resistance near Lock** only engages on triggers you haven't already configured on the Adaptive Triggers tab, so it never overrides your own trigger effects.

**Pulse Length** sets how long the rumble and trigger pulses last. The lightbar pulse has its own timing: it jumps to the chosen color on lock entry, holds at full strength for **Hold**, then fades back out over **Decay**.

| Setting | Default | Range |
| --- | --- | --- |
| Pulse Length | 80 ms | 0–2000 |
| Hold | 80 ms | 0–2000 |
| Decay | 250 ms | 0–5000 |

The **Color** dropdown picks where the lightbar color comes from:

- **Fixed**: one color, chosen in a full picker under **Lightbar Color** with an HSV field, swatch, **HEX** box, and RGB sliders. The default is red.
- **Random Hue**: a random full-brightness hue on every lock entry.
- **Palette Step**: a dedicated palette editor. Add colors to step through, one per lock. The palette belongs to this card alone. Leave it empty and the pulse goes dark instead of borrowing colors from another feature, and the step position restarts at the first color when PadForge restarts.

At-lock feedback fires for every steering source on the slot, including a **Nunchuk Lean** or **Left Joy-Con Lean** row. Steer from the second sensor and all four channels still work.

A controller-speaker tone on lock entry is still planned. The speaker output it will ride on shipped with [Controller Audio](../features/controller-audio.md), but the tone itself is not implemented yet.

Physical feedback honors the per-slot test target: when you're testing one assigned device, only it reacts.

## Notes

- The steering mode is per stick. Both sticks can run different modes at once, and each keeps its own winding state.
- Switching profiles clears a stick's winding state. Setting a stick back to Off makes it a normal stick again.
- The mode and its tunables save with the profile.

---

*Last updated for PadForge 4.2.0.*
