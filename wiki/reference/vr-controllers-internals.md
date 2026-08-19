# Virtual VR Controllers: Internals

*How one slot becomes a SteamVR hand pair: the state struct, the mapping targets, the pack, and the haptic return path.*

The user-facing page is [Virtual VR Controllers](../features/vr-controllers.md). This one is for whoever has to change the code.

Two VR lanes ship, and they run in opposite directions. Most of this page covers the **output** lane (#49): a PadForge slot emits a pair of virtual SteamVR hands through HIDMaestro's OpenVR driver. 4.3.0 added the **input** lane (#287): real VR hardware already tracked by SteamVR becomes a PadForge device you can map from. They share no code beyond a self-emission filter that keeps one from eating the other. The input lane has its own section at the end.

---

## Shape of the thing

One VR slot drives **both** hands. There is no left slot and right slot, and there is no second VR slot: `SettingsManager.MaxVrSlots` is `1`, and the add-slot gate reads `count < MaxVrSlots`.

The slot's output is `VrRawState` (`PadForge.Engine/Common/VrRawState.cs`), a pair of `VrHandRaw`:

```csharp
public struct VrHandRaw
{
    public byte  Buttons;
    public short Trigger;
    public short Grip;
    public short StickX;
    public short StickY;
}
```

Everything is a value field on purpose. A struct assign copies the whole thing, which is the same discipline `KbmRawState` follows, and it means the array-aliasing trap that bit the MIDI lane cannot apply here.

`Merge` follows the gamepad convention when more than one device feeds the slot: buttons OR together, axes keep the larger deflection.

---

## Button bits are a cast, not a table

`VrHandRaw.Buttons` mirrors HIDMaestro's `HMVRButton` flags **exactly**:

| Bit | Value | Meaning |
|---|---|---|
| 0 | 1 | System |
| 1 | 2 | A |
| 2 | 4 | A touch |
| 3 | 8 | B |
| 4 | 16 | B touch |
| 5 | 32 | Trigger click |
| 6 | 64 | Grip click |
| 7 | 128 | Stick click |

Because the layouts match, `PackHand` casts (`(HMVRButton)hand.Buttons`) instead of translating. **If you add a bit, add it at the same index on both sides or the cast silently misroutes every button above it.**

The mapping-target keys are ordered to match those bits, left hand then right:

```
VrLSystem VrLA VrLATouch VrLB VrLBTouch VrLTriggerClick VrLGripClick VrLStickClick
VrRSystem VrRA VrRATouch VrRB VrRBTouch VrRTriggerClick VrRGripClick VrRStickClick
```

`EvalVrButtons` (`InputManager.Step3.UpdateOutputStates.cs`) walks that key array and sets `bits |= (byte)(1 << i)`, so **the array order IS the bit order**. Reordering the keys reorders the wire format.

### Two thresholds, not one

Inside `EvalVrButtons`:

```csharp
int tgt = i == 5 ? TriggerClickActivationPercent : vgt;
```

Index 5 is trigger click, and `TriggerClickActivationPercent` is `0`, documented as strictly-positive detection: any nonzero pull asserts it. That mirrors real hardware, where DualSense and DS4 assert the digital trigger follower on any nonzero analog value.

Every other button, grip click included, uses `vgt`, the slot's ordinary axis-to-button threshold, 50% by default. Grip click is **not** a full-squeeze gesture.

The four touch bits are real mapping targets but carry `includeInMapAll: false` (`PadViewModel.cs`), so Map All skips them. They only ever get bound by hand.

---

## Pack: domains and the single Y flip

`HMaestroVRController.PackHand` converts the pipeline's native short domains to the driver's floats:

- Trigger and grip are one-sided `0..32767`, so they divide by `32767f`.
- Stick axes are bipolar, so positive divides by `32767f` and negative by `32768f`. Doing both with one divisor loses a bit of range at one end.
- **`StickY` is negated.** That is the only frame flip in this lane: SDL is Y-down, OpenVR is Y-up. If a stick ever feels inverted in VR only, this line is the first place to look, and it is also the place a second well-meaning flip elsewhere would cancel out.

`PoseValid` is set `false`. There is no pose source, so the driver holds the hands at its own default rather than being handed a fabricated one.

---

## Poses come from the headset, not from us

PadForge does not fabricate positional tracking. The OpenVR driver anchors both controllers to the live HMD pose plus a fixed offset (`HIDMaestro/driver/openvr/src/controller_device.cpp`), so the hands sit a fixed distance in front of the headset and follow wherever the user looks.

Stated plainly because it shapes what the feature is for: this gives games the **controls**, not room-scale hands.

---

## Haptics return on the Vibration lane

The return path is an event, not a poll. `HMVRController.HapticReceived` fires with `(hand, amplitude, durationSeconds)` and `OnHapticReceived` fans it into the slot's `Vibration` entry, the same lane ordinary game rumble rides, so whatever physical device drives the slot buzzes with no VR-specific plumbing downstream.

Left hand drives `LeftMotorSpeed`, right drives `RightMotorSpeed`. Amplitude clamps to `0..1` and scales to `ushort`. Duration has a floor of `MinPulseMs`, because a pulse shorter than one poll would otherwise be set and cleared without ever reaching the device.

Overlapping pulses on one hand keep the **later** end tick rather than restarting the timer, so a rapid burst holds the motor for the union of its pulses instead of chopping.

### The lock is load-bearing

`OnHapticReceived` re-checks `_connected` **inside** `_hapticLock`, and the comment there is worth preserving:

> Disconnect flips `_connected` and only then takes this lock to zero the lanes and dispose the timer, so a check outside it can pass, block here, and resume after teardown.

Without the inner re-check, a haptic event arriving during teardown re-latches a motor on a slot the virtual controller no longer drives, and `ScheduleExpiryLocked` builds a fresh timer nothing will ever dispose. Both symptoms are a stuck rumble that outlives the slot.

---

## Availability and install

`HMaestroVRController.IsAvailable()` caches `HMVR.IsSteamVRInstalled` for 5 seconds (`AvailabilityTtlMs`), because the probe walks Steam's library metadata on disk and the sidebar rail rebuild queries once per slot. `ResetAvailability()` drops the cache so the gates lift right after an install instead of waiting out the TTL.

The cache's "has a value" flag is an explicit `bool`, not a sentinel timestamp. Seeding the tick with `long.MinValue` made `now - s_availCheckedTick` overflow negative, which always reads as inside the TTL, so the first call returned the default `false` and SteamVR read as absent forever.

`Connect()` refuses twice, once on `IsSteamVRInstalled` and once on `EnsureDriverRegistered()`, before constructing the pipe.

Install lives in `DriverInstaller`:

- `SteamVrInstallDir` is `C:\SteamVR`, the default only. The card accepts any full path.
- A drive root on its own is refused, because uninstall would then be aimed at an entire drive.
- `GetOwnedSteamVrDir()` resolves what PadForge considers its own copy, and `HMVR.SetSteamVRPathHint` is both how the driver finds the runtime and how a hand-placed install becomes discoverable.
- Uninstall refuses while `vrserver` is running.

---

## The other direction: consuming real VR devices (#287)

*New in 4.3.0. This is the input lane, and it shares no code with everything above.*

`OpenVrConsumerService` (`PadForge.App/Common/Input/OpenVrConsumerService.cs`, `public sealed class`) turns the headset and every tracked VR controller into ordinary PadForge devices. `InitializeSdl` constructs it and calls `Start()`, wrapped in its own try/catch so a failure never takes the rest of input initialization down. It logs into the SDL diagnostics ring with a `VRCONSUME` prefix.

### One background client that never launches SteamVR

The service runs a single background thread (`OpenVrConsumer`, `IsBackground = true`) polling at about 90 Hz (`Thread.Sleep(11)`). It initializes OpenVR as `VRApplication_Background`, which by contract does not start SteamVR and instead returns `VRInitError_Init_NoServerForBackgroundApp` while the server is down. That error is the quiet retry signal, logged once rather than once per 5-second retry pass.

The native `openvr_api.dll` is **not shipped**. It comes from the user's own SteamVR runtime, found through OpenVR's own path registry at `%LOCALAPPDATA%\openvr\openvrpaths.vrpath` (with `VR_PATHREG_OVERRIDE` honored first, as the reference does). `DiscoverRuntimeDll` file-checks the result, so a registry entry pointing at a deleted install reads as absent rather than as a load failure. A `NativeLibrary.SetDllImportResolver` hook redirects the vendored binding's `openvr_api` module name to that path. The binding itself is Valve's own C# file, vendored at `PadForge.App/ThirdParty/OpenVR/openvr_api.cs`.

`VREvent_Quit` is answered with `AcknowledgeQuit_Exiting`, or vrserver waits out its force-quit timeout on the PadForge process.

### Each device becomes an SDL virtual joystick

Consumed devices enter the pipeline as SDL virtual joysticks, so they need no new `InputDeviceType` and reach mapping through the normal path. They carry the pid.codes open VID `0x1209`:

| PID | Name |
|---|---|
| `0x2870` | VR Headset |
| `0x2871` | VR Controller (Left Hand) |
| `0x2872` | VR Controller (Right Hand) |
| `0x2873` | VR Controller *n* (role unassigned) |

Both shapes declare 8 axes plus accel and gyro sensors at 90 Hz.

**Headset** (`axis_mask 0x0F`, `button_mask 0x01`): LX is lean right, LY is lean forward or back, RX is yaw, RY is pitch, generic Axis 6 is vertical lean, Axis 7 is roll. Button 0 (South) is pose validity, usable as an activator. Full scales are `LeanFullScaleMeters = 0.35`, `YawFullScaleDeg = 60`, `PitchFullScaleDeg = 45`, `RollFullScaleDeg = 45`. Position and yaw are relative to a baseline captured at the first valid pose and re-captured after 5 seconds of invalidity, so taking the headset off and putting it back on does not leave a stale lean.

**Controller** (`axis_mask 0x33`, `button_mask 0x06D1`): joystick to LX/LY, analog grip to LT, trigger to RT, trackpad to generic Axes 6 and 7. Buttons walk sequentially: South is A, Back is System, Start is ApplicationMenu, LeftStick is joystick click, LeftShoulder is grip click, RightShoulder is trackpad click.

The raw values sit at indices 6 and 7 on purpose. The generic-axis surface (`HasExtraGenericAxes`) only exposes axes past the standardized six, so at index 4 or 5 they would exist on the joystick with no PadForge surface able to read them.

### Axis roles, and why the fallback carries the load

`ClassifyAxes` reads the five `Prop_AxisNType_Int32` properties: `1` is trackpad, `2` is joystick, `3` is trigger. The first trigger-typed axis is the trigger, the second is the analog grip.

**Drivers on the modern input system never set those properties, and vrserver's legacy emulation does not synthesize them either.** All five read `0` on a real bench. So an all-`None` read falls back to the legacy-binding convention every shipped binding follows: axis 0 is the stick or pad, axis 1 is the trigger pull, axis 2 is the grip pull. That fallback is the path most hardware actually takes.

### Sensors come from the runtime's velocity fields

`PushSensors` does not finite-difference position. Gyro is the pose's `vAngularVelocity` rotated into the device frame by `WorldToDevice`. Accel is the derivative of `vVelocity` plus a gravity reaction of `9.80665` up, also rotated into the device frame, so a still device reads +1 g up like a real IMU.

### The self-emission filter

A slot emitting virtual hands must never read them back as input. `IsSelfEmitted` refuses any device whose `Prop_ManufacturerName_String` is `HIDMaestro`, which is exactly what `controller_device.cpp` sets on the driver's own devices. `PADFORGE_VR_CONSUME_SELF=1` lifts the filter, which is the hardware-free validation loop: PadForge's own virtual hands, tracked by SteamVR, read back through this lane.

A transient property-read failure returns an empty manufacturer string, and empty is **not** "not self". That case retries in 1 second rather than deciding. A self-filtered index caches its verdict until the index disconnects, and a failed attach backs off 5 seconds, because both paths used to re-run property reads and allocations at 90 Hz.

### Failure handling worth keeping

- A failed `GetControllerState` **neutralizes once** rather than latching: sticks to 0, triggers to `short.MinValue + 1`, buttons released. Without it a controller that sleeps mid-hold kept its stick deflected indefinitely.
- The shared `VRControllerState_t` is zeroed before every read, because one struct serves every controller in a tick and the runtime does not clear it on failure.
- `RunLoop` wraps everything in a top-level catch. An unhandled exception on a managed background thread is process-fatal, and this loop calls into two native stacks.
- `Start()` does everything that can throw **before** setting `_running`, or a resolver throw leaves the instance latched running with no thread and permanently unstartable.

### Status tiering

Two statics feed the UI, which previously could only ever say SteamVR was installed:

- `OpenVrConsumerService.ServerConnected`: whether the background client is attached to a running SteamVR.
- `HMaestroVRController.GlobalDriverStatus()`: whether any live VR slot's OpenVR driver is connected and whether its hands are live. Both reads happen under `s_liveLock`, and `Disconnect` disposes under the same lock, because the SDK's status getters dereference mapped shared memory with no disposed guard. A read racing `UnmapViewOfFile` is an access violation no catch survives.

---

## Things that will bite you

- **Adding a button** means touching the bit table, the key array order, and HIDMaestro's `HMVRButton` together. The cast hides a mismatch until runtime.
- **A second Y flip** anywhere in the VR lane cancels the one in `PackHand`.
- **SteamVR's own Test Controller is not a diagnostic.** Switching it from left to right often shows nothing until you switch back and forth again. Trust the app's Preview tab or the game.
- **There is no per-slot VR configuration.** The driver ships one identity, so there is no VR equivalent of the PlayStation or Extended profile pickers.
- **The two lanes can eat each other.** If you touch the manufacturer string on either side, the #287 self-emission filter stops matching and a VR slot starts consuming its own hands.

---

## Related

- [Virtual VR Controllers](../features/vr-controllers.md) for the user-facing page
- [Input Pipeline](input-pipeline.md) for where Step 3 evaluation and Step 5 submission sit
- [HIDMaestro Deep Dive](hidmaestro-deep-dive.md) for the driver side
- [Driver Installation Internals](driver-installation-internals.md) for the installer

---

*Last updated for PadForge 4.3.0.*
