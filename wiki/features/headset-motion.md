# Headset Head Tracking

*Sony headphones with a head tracker become a motion source. Turn your head to aim, lean, or drive any mapping that takes gyro.*

Some Sony headphones carry a head-tracking IMU for spatial audio. PadForge reads it and treats the headset as a motion-only input device, so your head becomes another source you can map. The whole [gyro](../guides/gyro.md) pipeline works with it: gyro-to-stick, gyro-to-mouse, aim engage, calibration, and the DSU motion server.

Confirmed working on the **WH-1000XM5** family over Bluetooth.

---

## How PadForge finds it

Discovery is by capability, not by a hardcoded model list. PadForge looks for a HID device exposing a **Sensor page (0x20), usage 0xE1** collection whose sensor-description feature report begins with the marker `#AndroidHeadTracker#`. Any headset presenting that collection is a candidate, whatever its name.

Pair the headphones to Windows as you normally would. When PadForge recognises the tracker, it appears on the **Devices** page as its own device alongside your controllers, and it carries a headphone icon in the slot's device roster on the Pad page.

Because it is motion-only, it reports no buttons, no sticks, and no triggers. Its whole contribution is rotation.

---

## Mapping it

Assign the headset to a slot on the **Devices** page, then map it like any gyro source:

| Source | Typical use |
|---|---|
| Gyro Yaw | Turn the camera as you turn your head |
| Gyro Pitch | Look up and down |
| Gyro Roll | Lean |
| Gyro Horizontal (Yaw + Roll) | Yaw and roll blended, for a grip-agnostic turn |

Pair it with **Aim Engage** so head tracking only steers while you hold or toggle a button. Head tracking that is always live is disorienting in most games, and an engage gate is the difference between a novelty and something you keep switched on.

---

## What the device actually reports

Worth knowing, because it explains the behaviour you will see:

- **Rotation is the signal.** On the XM5 the raw gyro channel streams zeros while the rotation vector carries the real motion. PadForge synthesises an angular rate from consecutive rotation samples, so mappings receive an ordinary gyro rate and need no headset-specific handling.
- **Accelerometer is advertised only when the descriptor exposes it.** Some firmware reports orientation without it.
- **The frame is remapped once, at ingest.** The tracker's axes are swapped and signed into the same frame SDL uses for controllers, so a headset and a gamepad both drive a mapping the same way.

---

## Limitations

- **Validated over Bluetooth.** That is how these headsets expose the tracker and how this was tested. PadForge itself applies no transport filter, so it would open the collection over any transport that presented it.
- **Rotation, not position.** Leaning physically closer to the screen changes nothing. Only orientation is reported.
- **Battery.** The tracker runs off the headphone battery like anything else it does.

---

## Related

- [Motion aiming (Gyro)](../guides/gyro.md) for the whole gyro pipeline, curves, and engage modes
- [Devices](devices.md) for assigning it to a slot
- [Mappings](mappings.md) for binding its axes
- [Headset Head Tracking: Internals](../reference/headset-motion-internals.md) for the descriptor probe and the rotation-to-rate synthesis

---

*Last updated for PadForge 4.2.0.*
