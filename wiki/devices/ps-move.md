# PlayStation Move

*The Move wand and the Navigation controller as mapping sources, over Bluetooth.*

The wand carries a gyroscope, an accelerometer, its trigger and face buttons, and the illuminated sphere on its head. The Navigation controller is the one-handed companion pad: a stick, a D-pad, and its own set of buttons.

Both connect over Bluetooth through the same signed PlayStation Bluetooth driver the [DualShock 3](dualshock-3.md) uses, which PadForge installs at pairing time. They appear on the [Devices](../features/devices.md) page as **PS Move Motion Controller** and **PS Move Navigation Controller**.

![A PS Move Motion Controller on the Devices page, with its live motion readout](../images/devices-move.png)

---

## Pairing

1. Open the [Devices](../features/devices.md) page and click **Pair**.
2. Set **Controller Family** to **PlayStation Move / Navigation**.
3. Connect the controller with a USB cable and click **Pair**. PadForge writes this PC's address into the controller and, on a wand, reads out its motion calibration.
4. Unplug and press the controller's **PS** button. It connects over Bluetooth.

Docking an original Move over USB also runs this on its own, so a wand that has never been paired pairs the first time you plug it in to charge.

---

## USB

USB is a pairing and charging dock, not an input path, for the original Move (ZCM1) and for the Navigation controller. Neither streams input over the cable. The PS4-era Move (ZCM2) does stream over USB.

---

## What reports

| Source | Notes |
|---|---|
| **Gyroscope** | Three axes, feeding the whole [Gyro](../guides/gyro.md) pipeline: gyro-to-stick, gyro-to-mouse, Aim Engage, and the DSU motion server. |
| **Accelerometer** | Three axes, for tilt and gesture work. |
| **Buttons** | Eight: Cross, Circle, Square, Triangle, Select, Start, PS, and the big Move button. Move sits on the right shoulder, beside the trigger. |
| **Trigger** | Analog, on the right-trigger axis, so it maps to a trigger rather than collapsing to a press. |

The wand's sphere is an output, not a source. PadForge drives it from the [Lighting](../features/lighting.md) tab, and it idles at the slot's player color.

The Navigation controller reports its left stick, its D-pad, Cross, Circle, L1, L3, PS, and its analog L2. It has no motion sensors. L2 is its only analog trigger, and it maps like any other trigger, pressure and all.

Before 4.3.0 that trigger read at rest no matter how hard it was pulled. The pressure was being written to an axis nothing reads: PadForge was numbering the pad's axes by their position in the standard gamepad layout, and the Navigation controller does not carry the axes in between, so every index past its sticks was off by the ones it skips.

---

## Using the motion

The Move's gyro is an ordinary motion source once it is mapped, so everything the [Gyro guide](../guides/gyro.md) describes applies: reference frames, real-world calibration, Aim Engage, and Gyro Tilt.

Because the wand is held rather than gripped in two hands, Aim Engage is usually the right pairing. Motion that is always live is disorienting when the device is also being waved.

---

## Limitations, stated plainly

- PadForge reads the Move's sensors. It does **not** do camera tracking, so there is no positional data, only rotation and acceleration.
- The sphere is an output PadForge can drive, not a tracking input.
- Motion depends on the per-wand calibration captured over USB. A wand that has never been docked reports its buttons and trigger normally, but its gyroscope and accelerometer stay muted. Plug it in once to fix that.

---

## Related pages

- [Devices](../features/devices.md)
- [Gyro](../guides/gyro.md)
- [Lighting](../features/lighting.md)
- [DualShock 3](dualshock-3.md)

---

*Last updated for PadForge 4.3.0.*
