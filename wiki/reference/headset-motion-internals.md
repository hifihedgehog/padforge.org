# Headset Head Tracking: Internals

*How a pair of headphones becomes a motion source: the descriptor probe, the marker, the rotation-to-rate synthesis, and the frame remap.*

The user-facing page is [Headset Head Tracking](../features/headset-motion.md). This one is for whoever has to change the code.

Two files carry it:

| File | Role |
|---|---|
| `PadForge.App/Common/Input/HeadTrackerHid.cs` | The HID usage constants |
| `PadForge.App/Common/Input/SonyHeadsetHid.cs` | Descriptor probe, marker check, feature-report setup |
| `PadForge.App/Common/Input/SonyHeadsetMotionDevice.cs` | The device itself: parse, synthesize, publish |

---

## Discovery is by capability, never by model list

There is no VID/PID table. A candidate is any HID device exposing a collection on the **Sensor page** with the **Other: Custom** usage, whose sensor-description feature report begins with a marker string:

```csharp
internal const ushort SensorPage        = 0x20;
internal const ushort OtherCustom       = 0xE1;
internal const ushort SensorDescription = 0x0308;
internal const string Marker            = "#AndroidHeadTracker#";
```

Confirmed working on the WH-1000XM5 family. Any headset presenting the same collection is a candidate, whatever its name, which is the point of probing by capability.

**Note what the probe does NOT do: it applies no transport filter.** Nothing in `SonyHeadsetHid` checks for Bluetooth. These headsets happen to expose the tracker over Bluetooth and that is where the feature was validated, but the code would open the collection over any transport that presented it. Do not write "Bluetooth only" into the docs as though the code enforced it.

The remaining usages the probe cares about:

| Constant | Usage | Meaning |
|---|---|---|
| `ReportInterval` | `0x030E` | Sampling interval, written during setup |
| `ReportingAllEvents` | `0x0841` | Reporting-state selector |
| `PowerFull` | `0x0851` | Power-state selector |
| `Rotation` | `0x0544` | Orientation rotation vector |
| `AngularVelocity` | `0x0545` | Gyroscope, rad/s, vector form |
| `AccelerationVector` | `0x0452` | Accelerometer, vector form |

Some Sensor stacks omit constant fields from value caps, which the probe accounts for rather than treating as a missing feature.

---

## Rotation is the signal, not the gyro field

This is the part that surprises people, and it is hardware-validated on the XM5: **the raw gyro channel streams zeros while the rotation vector carries the real motion.**

So the device decides at parse time. `SonyHeadsetMotionDevice` scans the parsed fields for a gyro usage:

```csharp
bool hasGyroUsage = false;
// ... f.Kind == GyroVector || f.Kind == GyroScalar  =>  hasGyroUsage = true
_synthesizeGyro = !hasGyroUsage;
```

When the descriptor exposes no gyro usage, the rate is **synthesized from consecutive rotation vectors** using `_prevRotation` and `_prevRotationTicks`. Mappings downstream receive an ordinary gyro rate and need no headset-specific handling anywhere in the pipeline.

If a firmware exposes the rotation vector but no gyro and the synthesis path is disabled, there is nothing to fall back to. That combination is guarded rather than left to produce silence.

Accelerometer is advertised **only when the descriptor exposes it**. Some firmware reports orientation without it, and claiming otherwise would put a dead source in the picker.

---

## The frame is remapped once, at ingest

The tracker's axes are swapped and signed into the frame SDL uses for controllers, and that happens exactly once, on the way in. Downstream, a headset and a gamepad drive a mapping identically.

Two consequences worth stating plainly:

- **A second remap anywhere downstream cancels this one.** If head tracking feels mirrored on one axis only, suspect a duplicate transform before suspecting the device.
- It is a swap plus signs, not a rotation. Describing it as "rotated into the SDL frame" is imprecise enough to mislead someone reimplementing it.

The DSU motion server does its own flip separately, in `DsuMotionServer`, and that stays there. `MotionSnapshot` remains in the SDL native frame.

---

## What the user sees

The headset appears on the **Devices** page as its own device, and carries a headphone glyph in the slot's device roster on the **Pad** page (`DeviceTypeGlyph.For`, one call site in `InputService`).

Because it is motion-only, it reports no buttons, no sticks, and no triggers. Its whole contribution is rotation, which is why it is worth pairing with Aim Engage: head tracking that is always live is disorienting in most games.

The picker label is **Gyro Horizontal (Yaw + Roll)**, verbatim from `Strings.resx`. Not "Gyro Horizontal".

---

## Limitations, stated as facts

- **Rotation, not position.** Leaning physically closer to the screen changes nothing.
- **The tracker runs off the headphone battery** like everything else the headset does.
- **Validated over Bluetooth.** That is how these headsets expose it and how it was tested. The code imposes no transport restriction, so do not document one.

---

## Related

- [Headset Head Tracking](../features/headset-motion.md) for the user-facing page
- [Motion aiming (Gyro)](../guides/gyro.md) for the pipeline the headset feeds
- [DSU Motion Server](dsu-motion-server.md) for the separate flip that lives there
- [Input Pipeline](input-pipeline.md) for where external devices register

---

*Last updated for PadForge 4.2.0.*
