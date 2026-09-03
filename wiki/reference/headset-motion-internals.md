# Headset Head Tracking: Internals

*How a pair of headphones becomes a motion source: the descriptor probe, the marker, the rotation-to-rate synthesis, and the frame remap.*

The user-facing page is [Headset Head Tracking](../features/headset-motion.md). This one is for whoever has to change the code.

Six files carry it:

| File | Role |
|---|---|
| `PadForge.App/Common/Input/HeadTrackerHid.cs` | The HID usage constants and the pure descriptor decode |
| `PadForge.App/Common/Input/HeadTrackerMath.cs` | `AngularRateFromRotationVectors`, the rotation-to-rate math |
| `PadForge.App/Common/Input/SonyHeadsetHid.cs` | Descriptor probe, marker check, feature-report setup, and `SonyHeadsetMotionRuntime`, the enumerator and its per-path verdict cache |
| `PadForge.App/Common/Input/SonyHeadsetMotionDevice.cs` | The device itself: parse, synthesize, publish |
| `PadForge.App/Services/HeadsetTrackerRepair.cs` | The two unattended repairs: the HID-service re-request and the failed-start driver rebind |
| `PadForge.App/Common/Input/InputManager.Step1.UpdateDevices.cs` | Phase 1g: the background sweep, poll-thread registration, teardown |

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

**Note what the probe does NOT do: it applies no transport filter.** Nothing in `SonyHeadsetHid` checks for Bluetooth. These headsets happen to expose the tracker over Bluetooth and that is where the feature was validated, but the code would open the collection over any transport that presented it. Do not write "Bluetooth only" into the docs as though the code enforced it. The two repairs below are Bluetooth-specific because they act on a paired device's address, and a candidate whose address does not resolve still qualifies as a tracker with that lane simply unavailable to it.

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

## The sweep, and the two repairs

Registration is Phase 1g of `UpdateDevices`. Every blocking call lives on a worker: `HeadsetMotionSweep` runs at most once every 3 seconds (`_headsetSweepIntervalMs`), enumerates, opens and configures the new trackers, and queues them, while the poll thread only registers finished devices and retires vanished ones. An open that fails backs off 60 seconds (`_headsetOpenRetryMs`), and the entry is dropped when the path vanishes so a re-created node starts fresh. `SonyHeadsetMotionRuntime.Enumerate` returning null is not the same as returning an empty list: null is a SetupAPI failure and keeps the previous snapshot, an empty list means the headset is off and retires every open device.

Two repairs run unattended from that worker, both ported from NicholasSlattery/sony-head-tracker (MIT) and both possible in-process only because PadForge always runs with administrator rights.

**Failed-start rebind.** Windows routinely parks the head-tracker child at `CM_PROB_FAILED_START` under a sensor-class driver, and a failed node never qualifies, so no device row exists exactly when the repair is needed. `FindFailedStartNode` runs every sweep, one SetupAPI pass over present nodes, matching a `CM_PROB_FAILED_START` node under a BTHENUM parent whose hardware ID carries `UP:0020_U:00E1`. `RebindNode` then binds the inbox `%WINDIR%\INF\input.inf` generic HID driver through `UpdateDriverForPlugAndPlayDevices`. It acts only when exactly one node matches, with a per-node retry backoff of 60 seconds (`_headsetRebindRetryMs`).

**HID-service re-request.** The XM5 closes the sensor channel on its own, Windows removes the HID child, and nothing recreates it while the headset stays connected for audio. For every known tracker address with no present candidate, `RequestHidServiceByAddress` calls `BluetoothSetServiceState` with the HID service GUID `0x1124` on the paired device. A device reporting not connected is left alone rather than paged on a loop, and a live HID child is never toggled. `ERROR_INVALID_PARAMETER` or `E_INVALIDARG` means the Bluetooth database claims the service is enabled while no node exists, and that stale state is cycled: disable, sleep 1.5 seconds, enable. Only an issued request carries a cooldown, 20 seconds per address (`_headsetServiceRequestIntervalMs`), so a headset that reconnects right after an attempt is caught on the next sweep.

Addresses reach that lane three ways: resolved from the BTHENUM ancestor of a qualified node, loaded from `AppSettingsData.HeadsetTrackerAddresses` (12-hex-digit tokens, comma-joined), and mined once per process out of the PnP tree by `FindKnownTrackerAddresses`, which runs only when there are no candidates and no remembered addresses at all. That last pass recovers past identity from the phantom node a channel drop leaves behind.

---

## Rotation is the signal, not the gyro field

This is the part that surprises people, and it is hardware-validated on the XM5: **the raw gyro channel streams zeros while the rotation vector carries the real motion.**

So the device decides at parse time. `SonyHeadsetMotionDevice` scans the parsed fields for a gyro usage:

```csharp
bool hasGyroUsage = false;
// ... f.Kind == GyroVector || f.Kind == GyroScalar  =>  hasGyroUsage = true
_synthesizeGyro = !hasGyroUsage;
```

When the descriptor exposes no gyro usage, the rate is **synthesized from consecutive rotation vectors** using `_prevRotation` and `_prevRotationTicks` (`SynthesizeGyroFromRotation`, which calls `HeadTrackerMath.AngularRateFromRotationVectors`). Mappings downstream receive an ordinary gyro rate and need no headset-specific handling anywhere in the pipeline.

Parse time is not the only decision point. A descriptor that does expose a gyro usage but streams an all-zero word falls back to synthesis at runtime, and that fallback is **revocable in both directions**: one nonzero sample marks the field live (`_gyroFieldLive`), and a sustained zero run of `GyroZeroRunToRevoke` (50) samples hands the lane back to rotation. A one-way latch here meant a single startup artifact disabled synthesis for the life of the device object.

A descriptor carrying neither a gyro usage nor a rotation vector has nothing this source can serve, so `Open` fails it outright rather than attaching a device that would publish silence.

Accelerometer is advertised **only when the descriptor exposes it**. Some firmware reports orientation without it, and claiming otherwise would put a dead source in the picker.

---

## The frame is remapped once, at ingest

The tracker's axes are swapped and signed into the frame SDL uses for controllers, and that happens exactly once, on the way in, as the reader publishes: `MapIndex = { 1, 0, 2 }` with `MapSign = { -1, 1, -1 }`, applied to the gyro triple and the accel triple alike. Downstream, a headset and a gamepad drive a mapping identically.

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

*Last updated for PadForge 4.4.0.*
