# PlayStation Move

*The Move wand and the Navigation controller as mapping sources, over USB and Bluetooth.*

Both PlayStation Move devices report to PadForge without a driver install. The wand carries a gyroscope, an accelerometer, its trigger and face buttons, and the illuminated sphere on its head. The Navigation controller is the one-handed companion pad: a stick, a D-pad, and its own set of buttons.

Plug either in over USB, or pair it over Bluetooth, and it appears on the [Devices](../features/devices.md) page under its own name.

![A PS Move Motion Controller on the Devices page, with its live motion readout](../images/devices-move.png)

---

## What reports

| Source | Notes |
|---|---|
| **Gyroscope** | Three axes, feeding the whole [Gyro](../guides/gyro.md) pipeline: gyro-to-stick, gyro-to-mouse, Aim Engage, and the DSU motion server. |
| **Accelerometer** | Three axes, for tilt and gesture work. |
| **Buttons** | The face buttons, Start and Select, the PS button, and the Move button. |
| **Trigger** | Analog, so it maps to a trigger axis rather than collapsing to a press. |
| **Sphere** | The wand's lamp. |

The Navigation controller reports its stick, its D-pad, and its buttons. It has no motion sensors.

---

## Using the motion

The Move's gyro is an ordinary motion source once it is mapped, so everything the [Gyro guide](../guides/gyro.md) describes applies: reference frames, real-world calibration, Aim Engage, and Gyro Tilt.

Because the wand is held rather than gripped in two hands, Aim Engage is usually the right pairing. Motion that is always live is disorienting when the device is also being waved.

---

## Limitations, stated plainly

- PadForge reads the Move's sensors. It does **not** do camera tracking, so there is no positional data, only rotation and acceleration.
- The sphere is an output PadForge can drive, not a tracking input.

---

## Related pages

- [Devices](../features/devices.md)
- [Gyro](../guides/gyro.md)
- [DualShock 3](dualshock-3.md)

---

*Last updated for PadForge 4.3.0.*
