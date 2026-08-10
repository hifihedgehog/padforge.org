# Wheel Force Feedback Internals

*How a game's force feedback reaches a real wheel: the HID PID decode chain, the three clean-room vendor writers, the host-sampled and software paths in `ForceFeedbackState`, and the RPM-LED telemetry system.*

This is the developer-side companion to [Wheel](../features/wheel.md) (the user guide). See [Force Feedback](../features/force-feedback.md) for the rumble and generic-haptic side.

---

## Two pipelines, one set of writers

Two force pipelines converge on the same vendor writers:

- **Game PID force feedback** (DirectInput games): the game writes HID PID output reports to an Extended virtual controller. `HMaestroFfbDecoder` parses them into a `Vibration` carrying direction and condition data.
- **XInput rumble** (Xbox-target games): the two motor bytes become scalar `Vibration` fields, which wheels translate into an oscillating constant force.

Both write the single aggregation buffer `_combinedVibration` in `InputManager.Step2.UpdateInputStates.cs`. Everything downstream reads from it.

A third destination joined in 4.1.0: the Bass Shakers lane (#236) turns the same game force into low-frequency audio. It bypasses `_combinedVibration` and the writers:

- `HMaestroFfbDecoder.Apply` stores the game-authored motor pair in `LastComputedMotors`, computed purely from the uploaded PID effect set. Test and macro rumble stay out by construction.
- `TickFfb` packs the pair into the virtual controller's inbound rumble pack via `LfeOutputState.Pack`.
- `UpdateRumbleAudioLane` in `InputManager.Step5.VirtualDevices.cs` publishes each slot's pack once per poll tick through `RumbleAudioService.PublishIfCurrent`.

So game force feedback reaches vendor wheels, scalar rumble devices, and bass-shaker audio endpoints. The slot's **Bass Shakers** tab configures the endpoint. See [Force Feedback](../features/force-feedback.md#bass-shakers) for the user-facing side.

---

## Files

| File | Role |
|---|---|
| `PadForge.App/Common/Input/HMaestroVirtualController.cs` | Forwards HM HID-output and XInput packets into the decoder. |
| `PadForge.App/Common/Input/HMaestroFfbDecoder.cs` | Parses HID PID reports into a `Vibration`. |
| `PadForge.App/Common/Input/InputManager.Step2.UpdateInputStates.cs` | `ApplyForceFeedback` aggregates per slot and dispatches to a vendor writer. |
| `PadForge.App/Common/Input/LogitechRawHidWriter.cs` | Logitech native HID (from `new-lg4ff`, clean-room). |
| `PadForge.App/Common/Input/FanatecRawHidWriter.cs` | Fanatec native HID (from `hid-fanatecff`, clean-room). |
| `PadForge.App/Common/Input/ThrustmasterRawHidWriter.cs` | Thrustmaster native HID (from `hid-tmff2`, clean-room). |
| `PadForge.Engine/Common/ForceFeedbackState.cs` | The `Vibration` carrier, the host-sampled and software paths, the SDL writer for generic devices. |
| `PadForge.App/Common/Telemetry/` | The RPM-LED telemetry sources, hub, and LED map. |

---

## Decode chain

`HMaestroVirtualController` holds an `HMaestroFfbDecoder`, constructed when the controller's HID descriptor carries the PID force-feedback block (the gate is descriptor presence, not VID, so catalog profiles keep their identity). The HM output callback routes by packet source: a HID-output report goes to `_ffbDecoder.OnHidOutput` then immediately `Apply`, a HID feature report (the Create-New-Effect path) goes to `OnHidFeature`, and an XInput packet writes the scalar motor and impulse-trigger bytes directly. A per-tick `TickFfb` calls `Apply` again so duration-bounded effects expire even without new packets.

`HMaestroFfbDecoder.OnHidOutput` dispatches per report ID: Set Effect (0x11), Set Condition (0x13, the bit-packed per-axis condition coefficients for spring, damper, inertia, and friction), Set Periodic (0x14), Set Constant (0x15), Set Ramp (0x16), Effect Operation (0x1A, start and stop), Block Free (0x1B), Device Control (0x1C), and Device Gain (0x1D). It also handles the pre-allocation flow where the OS writes parameters before the SetFeature allocates the real effect block. `ParseFfbScales` walks the report descriptor once at construction to normalize hand-authored descriptors (the SideWinder ranges) into canonical units.

`Apply(Vibration vib)` finds the dominant effect, writes its type, signed magnitude, direction, period, and gain, splits the polar direction into left and right motor scalars so rumble-only devices still feel directional force, and copies the spring, damper, inertia, and friction coefficients into the vibration's condition axes.

The `Vibration` carrier lives in `PadForge.Engine/Common/ForceFeedbackState.cs` with scalar motor fields, directional fields (`EffectType`, `SignedMagnitude`, `Direction`, `Period`, `DeviceGain`), and condition fields.

---

## Aggregation and dispatch

`ApplyForceFeedback(UserDevice ud)` in Step 2 combines every slot the device is mapped to (motors max-combined, the first slot with directional or condition data becomes the directional source) into `_combinedVibration`, then dispatches by device identity:

- Sony pads (DualSense, DualShock 4) return early. They are written by `UserEffectsDispatcher` and `PlayStationEffectWriter`.
- Xbox One and later take the `XboxImpulseHidWriter` path.
- Logitech, Fanatec, and Thrustmaster wheels and pedals (gated by `IsLogitechWheel` / `IsFanatecWheel` / `IsThrustmasterWheel` / `IsFanatecPedal`) take the vendor-writer block.
- Everything else falls to `ForceFeedbackState.SetDeviceForces` (the SDL path).

Per-frame force is throttled by a change-detection struct cached in `_appliedWheelFfb`, because re-sending an unchanged force every poll is a blocking HID write that halves the poll rate with a wheel attached.

---

## The three vendor writers

All three are `internal static class`, frame a vendor-shaped command padded to the device's output-report length, and are clean-room C# from the open Linux drivers.

### Logitech (`LogitechRawHidWriter`, VID 0x046D)

`IsLogitechWheel` gates G29, G923 (PlayStation variant), G27, G25, Driving Force GT, Driving Force Pro, Driving Force, MOMO Racing, MOMO Force, and WingMan Formula Force GP. The G920 and the Xbox G923 speak HID++ 2.0 and are excluded. Effects: `WriteConstantForce` (with a per-slot download then refresh state), `WriteCondition` (spring command 0x0b, friction command 0x0e only on the G27, G25, DFGT, and DFP, else the damper command for damper and inertia), `WriteAutocenter` (a firmware spring), `WriteRange` (`f8 81` for most, a coarse-plus-fine path for the DFP), and `WriteRpmLeds` (`f8 12`, five LEDs). No firmware periodic, so periodic effects arrive host-sampled.

### Fanatec (`FanatecRawHidWriter`, VID 0x0EB7)

`IsFanatecWheel` gates the CSL Elite, CSL DD, DD Pro, ClubSport DD, ClubSport V2 and V2.5, Podium DD1 and DD2, CSR Elite, and Porsche 911 bases. `IsFanatecPedal` gates the ClubSport V3 and CSL pedals (rumble only). High-resolution bases write 16-bit force. `WriteAutocenter` is a software centering spring routed through a slot-1 condition and re-asserted every frame, because Fanatec bases expose no firmware auto-center and the range command disables the stock spring. `WriteRange` sends three reports. `WriteRpmLeds` writes the base strip and the rim strip separately, nine LEDs. No firmware periodic.

### Thrustmaster (`ThrustmasterRawHidWriter`, VID 0x044F)

`IsThrustmasterWheel` gates the T300RS variants, T-GT II, T248, TX, TS-XW, and TS-PC. The T150 uses a separate driver and is excluded. This writer is stateful and multi-packet (upload, play, update, stop), with a per-device armed-kind cache so switching effect kind re-uploads while the same kind updates live. It is the only writer with `WritePeriodic`, a firmware-native periodic generator (`WaveformCode` maps square, triangle, sine, and the two sawtooths). It takes the un-sampled peak, not the host-sampled level. `WriteAutocenter` and `WriteRange` are firmware-native. `WriteRpmLeds` writes fifteen LEDs.

---

## Host-sampled and software paths

`ForceFeedbackState` holds the static math used by the dispatch plus the SDL writer for generic devices:

- `ComputeWheelSteeringPeak` gain-scales the signed magnitude and projects the polar direction onto the steering axis. This is the steady amplitude Thrustmaster uploads as a firmware periodic.
- `ComputeWheelSteeringLevel` multiplies that peak by `PeriodicWaveform`, the instantaneous waveform multiplier. For Logitech and Fanatec, which have no firmware periodic generator, a periodic effect becomes this oscillating constant force, sampled each frame.
- `ComputeWheelRumbleLevel` turns rumble-only motor values into an oscillating constant force (heavy motor on a 120 ms period, light on 40 ms). This is what wheels get from XInput games.
- `TryApplyAutoCenterSpring` is the software auto-center for generic SDL wheels. Gated to single-axis spring-capable haptics, it reads `AutoCenterStrength` and builds a symmetric `SDL_HAPTIC_SPRING` on the steering axis. Vendor wheels never reach here.

---

## Wheel-tab settings

`PadSetting.RotationRange` (default 900), `AutoCenterStrength` (default 0), and `WheelRpmLeds` (default 0) all participate in the settings checksum. The `PadViewModel` bridges them through `InputService`. In `ApplyForceFeedback`, range and auto-center are one-shot, re-sent only when the cached `_appliedWheelSettings` changes, with each writer clamping range to its own hardware maximum.

The tab-visibility gate is `PadPage.SyncTabVisibility`. `hasWheel` is the OR of the three `IsXxxWheel` gates on the selected device's VID and PID. `hasGenericWheel` covers a non-vendor SDL wheel that can only self-center. The Wheel tab shows when either is true, but the rotation-range and RPM-LED rows show only for `hasWheel`. See [Wheel](../features/wheel.md) for the user-facing behavior.

---

## RPM-LED telemetry

When `WheelRpmLeds` is on and the device is a vendor wheel, Step 2 requests telemetry, computes the rev fraction, and writes the matching `WriteRpmLeds` mask only when it changes.

`TelemetryHub` is demand-driven. `RequestActive` (called each frame a wheel wants LEDs) starts a 60 Hz background poll and auto-stops three seconds after the last request. It polls the registered sources in order and publishes the first with a non-zero max RPM. `RpmLedMap` turns the rev fraction into a bit-0-first LED mask, with a redline blink, and holds the LED counts (5 Logitech, 9 Fanatec, 15 Thrustmaster).

Each per-game source implements `ITelemetrySource` (`Start`, `Stop`, `TryGetSnapshot`) and reads RPM and max RPM from a shared-memory map or a UDP feed:

| Source | Game | Channel |
|---|---|---|
| `ForzaUdpTelemetrySource` | Forza Horizon and Motorsport | UDP |
| `AssettoCorsaTelemetrySource` | Assetto Corsa and Competizione | shared memory |
| `IRacingTelemetrySource` | iRacing | shared memory |
| `RFactor2TelemetrySource` | rFactor 2 and Le Mans Ultimate | shared memory |
| `RaceRoomTelemetrySource` | RaceRoom | shared memory |
| `ScsTruckTelemetrySource` | Euro Truck Simulator 2 and American Truck Simulator | shared memory |
| `MadnessTelemetrySource` | Automobilista 2 and Project CARS 2 and 3 | shared memory |
| `RFactor1TelemetrySource` | rFactor 1 and Automobilista 1 | shared memory |
| `CodemastersUdpTelemetrySource` | F1, DiRT, GRID | UDP |
| `OutGaugeTelemetrySource` | BeamNG and Live for Speed | UDP |

The telemetry readers are original. Where a game's memory layout came from a published SDK or community header, only field offsets and wire facts were used, with no source carried across.

---

## Remote Link wheel relay

A shared wheel works over [Remote Link](remote-link-internals.md) through a parallel dispatch in `InputService`. The consumer ships a semantic wheel frame, and `ApplyRemoteWheel` re-encodes it on the owner with the owner's own vendor writer, calling the same condition, constant-force, periodic, range, auto-center, and RPM-LED entry points Step 2 uses (`WriteCondition` / `WriteConstantForce` on Logitech and Thrustmaster, `WriteWheelCondition` / `WriteWheelConstantForce` on Fanatec, `WritePeriodic` on Thrustmaster only, then `WriteRange`, `WriteAutocenter`, and `WriteRpmLeds` on all three). This is why the writers are referenced from both Step 2 and `InputService`.

---

## Related pages

- [Wheel](../features/wheel.md): the user guide for this feature.
- [Force Feedback](../features/force-feedback.md): rumble passthrough, the generic-haptic path, and the `Vibration` carrier.
- [Input Pipeline](input-pipeline.md): where `ApplyForceFeedback` runs in Step 2.
- [Engine Library](engine-library.md): `ForceFeedbackState` and the `Vibration` struct.
- [Remote Link Internals](remote-link-internals.md): relaying a shared wheel's force feedback.

---

*Last updated for PadForge 4.2.0.*
