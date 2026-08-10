# Virtual VR Controllers: Internals

*How one slot becomes a SteamVR hand pair: the state struct, the mapping targets, the pack, and the haptic return path.*

The user-facing page is [Virtual VR Controllers](../features/vr-controllers.md). This one is for whoever has to change the code.

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

`HMaestroVRController.IsAvailable()` caches `HMVR.IsSteamVRInstalled`, which is why `ResetAvailability()` exists: after an install the cached answer is stale and the Add Controller tile would stay disabled.

`Connect()` refuses twice, once on `IsSteamVRInstalled` and once on `EnsureDriverRegistered()`, before constructing the pipe.

Install lives in `DriverInstaller`:

- `SteamVrInstallDir` is `C:\SteamVR`, the default only. The card accepts any full path.
- A drive root on its own is refused, because uninstall would then be aimed at an entire drive.
- `GetOwnedSteamVrDir()` resolves what PadForge considers its own copy, and `HMVR.SetSteamVRPathHint` is both how the driver finds the runtime and how a hand-placed install becomes discoverable.
- Uninstall refuses while `vrserver` is running.

---

## Things that will bite you

- **Adding a button** means touching the bit table, the key array order, and HIDMaestro's `HMVRButton` together. The cast hides a mismatch until runtime.
- **A second Y flip** anywhere in the VR lane cancels the one in `PackHand`.
- **SteamVR's own Test Controller is not a diagnostic.** Switching it from left to right often shows nothing until you switch back and forth again. Trust the app's Preview tab or the game.
- **There is no per-slot VR configuration.** The driver ships one identity, so there is no VR equivalent of the PlayStation or Extended profile pickers.

---

## Related

- [Virtual VR Controllers](../features/vr-controllers.md) for the user-facing page
- [Input Pipeline](input-pipeline.md) for where Step 3 evaluation and Step 5 submission sit
- [HIDMaestro Deep Dive](hidmaestro-deep-dive.md) for the driver side
- [Driver Installation Internals](driver-installation-internals.md) for the installer

---

*Last updated for PadForge 4.2.0.*
