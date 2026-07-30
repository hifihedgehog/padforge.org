# HIDMaestro Deep Dive

PadForge routes every virtual gamepad except the MIDI and Keyboard+Mouse targets through [HIDMaestro](https://github.com/hifihedgehog/HIDMaestro), a single user-mode UMDF2 driver. This page documents the contract between PadForge and HIDMaestro, the OpenXInput shim that keeps PadForge's own slots out of its own enumeration, and the lifecycle invariants every Step 5 / Input Manager edit must uphold.

> If you are reading this looking for the legacy `vJoy-Deep-Dive.md`, that page is gone. v2 used vJoy + ViGEmBus as two separate drivers and inherited a long list of phantom-controller / N²-slot / DLL-cache bugs that came with vJoy's kernel-mode HID stack. v3 replaces both with HIDMaestro and the headaches with them. The "five virtual controller categories" Xbox / PlayStation / Extended / MIDI / KB+M live in [Virtual Controllers](../features/virtual-controllers.md).

---

## What HIDMaestro is

HIDMaestro (HM) is a UMDF2 (User-Mode Driver Framework 2) bus driver that publishes virtual HID controllers from user-mode. Each PadForge slot that is not MIDI or Keyboard+Mouse asks HM to instantiate a virtual device matching one of HM's **device profiles**. A profile bundles:

- A USB VID/PID pair
- A product string and OEM name
- A pre-recorded HID report descriptor (input + output + feature reports)
- Optional FFB PID descriptor pages

PadForge ships with HM 1.3.22, which covers 225 profiles spanning Xbox 360 / Xbox One / Xbox Series / Elite / Adaptive, DualShock 3/4, DualSense / DualSense Edge, Switch Pro, Logitech G-series wheels, Thrustmaster / Fanatec wheels, HOTAS / flight sticks, third-party gamepads (Hori, 8BitDo, PowerA, PXN, etc.), and a "Custom" profile that lets the Extended slot type build a HID descriptor from scratch. The interim milestones a successor should know: v1.3.18 added the virtual Switch Pro profile and the IMU submission channel (HM#33), v1.3.21 corrected the Switch Pro Bluetooth descriptor to the real pad's wire shape (HM#37), and v1.3.22 made the input worker survive foreign stop signals, the structural fix for the frozen-output bug (HM#38).

### One driver, six categories

The six `VirtualControllerType` values map to HM as follows:

| Category | Backend | Description |
|---|---|---|
| Xbox (`Xbox = 0`) | HM | Xbox 360 / One / Series / Elite / Adaptive profiles. Acts as XInput device 1–4 when allocated a slot. |
| PlayStation (`PlayStation = 1`) | HM | DualShock 3/4, DualSense, DualSense Edge profiles. Reports as HID + DirectInput, plus the DualShock 4 extended report (touchpad, gyro/accel, battery) when supported. |
| Extended (`Extended = 2`) | HM | Any of the remaining HM profiles plus user-defined custom HID descriptors. Up to 8 axes, 128 buttons, 4 POV hats. |
| MIDI (`Midi = 3`) | Windows MIDI Services | NOT HM. Virtual MIDI endpoint via the Windows MIDI Services SDK. |
| KeyboardMouse (`KeyboardMouse = 4`) | Win32 SendInput | NOT HM. No driver. Pumps `INPUT` structures into the OS input queue. |
| Nintendo (`Nintendo = 5`) | HM | A virtual Switch Pro Controller (VID 057E, PID 2009, the Bluetooth wire shape) on a fixed catalog profile, no Customize. Rides the same raw-HID data path as Extended, with gyro passthrough over the HM v1.3.18 IMU channel and HOME LED control. |

Numeric values are preserved across the rename so legacy PadForge.xml files keep loading. `Xbox` carries `[XmlEnum("Microsoft")]` and `PlayStation` carries `[XmlEnum("Sony")]` purely as a back-compat accept-list for older settings files. This is the exception path, not the canonical naming.

---

## SDK surface PadForge talks to

The relevant assembly is `HIDMaestro.Core` (bundled at `PadForge.App/Resources/HIDMaestro/HIDMaestro.Core.dll`). Three primary types:

```csharp
// HMContext: process-wide entry point. One instance.
var context = new HMContext();
context.LoadDefaultProfiles();    // load the 225 embedded profile JSONs
context.InstallDriver();          // register HM with Windows (idempotent)

// HMProfile: handle to a profile (Xbox 360 wired, DualSense Edge, etc.).
// Returns HMProfile? (null when the id is not in the catalog).
HMProfile profile = context.GetProfile("xbox-series-xs-bt");
//   profile.Id, .Name, .ProductString, .VendorId, .ProductId
//   profile.AxisCount, .StickCount, .TriggerCount, .ButtonCount, .HasHat
// HMProfile lives inside the HIDMaestro.Core binary. The members above are
// the ones PadForge's call sites read. PadPage reads AxisCount and splits it
// by the gamepad convention (first four axes pair into two sticks, the rest
// are triggers). Step 5 and PadViewModel read StickCount / TriggerCount
// directly off the SDK's simple-view properties (v1.3.9).

// HMController: a live virtual device instance. Construct via the context.
HMController controller = context.CreateController(profile);
//   controller.Profile               // HMProfile this device was built from
//   controller.SubmitState(in state) // ~1000 Hz hot path; HMGamepadState
//   controller.SubmitRawReport(rs)   // ReadOnlySpan<byte>; DS4 extended / custom HID
//   controller.OutputReceived  += handler   // FFB / rumble feedback packets
//   controller.OutputDecoded   += handler   // decoded FFB events
//   controller.Dispose()             // tears down the live device
```

For Extended slots that build a custom HID descriptor, PadForge starts from the catalog profile with `new HMProfileBuilder().FromProfile(baseProfile)`, feeds a `HidDescriptorBuilder` (sticks, triggers, buttons, hats, plus `AddPidFfbBlock()` when FFB is on) through `FromDescriptorBuilder`, and calls `builder.Build()`. That returns an `HMProfile` handed straight to `CreateController`, the same as any catalog profile. There is no separate register step.

### Property availability gating

Every HM SDK call is annotated `[SupportedOSPlatform("windows10.0.26100.0")]`. The main project targets `net10.0-windows10.0.26100.0`, which satisfies that platform requirement, so the main build's calls are reachable without a CA1416 warning. CA1416 still fires from the auto-generated WPF temp project (`*_wpftmp.csproj`), which does not inherit `TargetPlatformVersion` from the main csproj. That is the reason the csproj comment gives for suppressing it via `<NoWarn>$(NoWarn);CA1416;WFO0003</NoWarn>`. `WFO0003` in the same line is the WinForms HighDPI-migration recommendation, left in the manifest because the app is WPF-primary.

---

## OpenXInput: filtering PadForge's own slots out of its own view

PadForge enumerates physical gamepads through SDL3, which in turn uses XInput. When PadForge owns an Xbox-category virtual slot, that slot also reports as XInput device 1–4. Without filtering, SDL would re-enumerate the virtual slot as an input device, PadForge would map it to itself, and you'd get a feedback loop.

The fix is a fork of [OpenXInput](https://github.com/hifihedgehog/OpenXinput) (branch `OpenXinput1_4`) that ships as `xinput1_4.dll` under `PadForge.App/Resources/OpenXInput/x64/`, bundled into the single-file `PadForge.exe`. At launch, `App.xaml.cs` calls `SetDllDirectory` on the single-file extract directory so the OS resolves the local copy ahead of `C:\Windows\System32\xinput1_4.dll`. The fork's `IsHidMaestroInterface` classifier (`src/OpenXinput.cpp`) drops any device whose interface symlink contains the literal `HIDMAESTRO` substring (fast path) or whose PnP parent chain holds an ancestor with `HIDMAESTRO` in its hardware-ID list (depth-4 walk, covers the HID child that spoofs the real gamepad's hardware IDs).

`devobj.dll` is deliberately **not** bundled. OpenXInput's source tree contains a stub `devobj.dll` that exists only to satisfy `xinput1_4.dll`'s static-link import at compile time. Shipping that stub would hijack `setupapi.dll`'s own `DevObj*` imports and crash HID class enumeration. See [PadForge #69](https://github.com/hifihedgehog/PadForge/issues/69). The system `devobj.dll` resolves from `System32` unaided.

This filter is **PadForge-only**. Other applications (games, Steam, etc.) load the system XInput and see PadForge's virtuals normally. That's the entire point of having virtual controllers.

The same filter logic exists in three other places PadForge owns:

1. **SDL3 fork**, branch `feat/hidmaestro-filter` of `hifihedgehog/SDL`. Stops SDL from opening the HM virtuals as joysticks during `SDL_OpenJoystick`. The classifier (`hid_internal_is_hidmaestro_device` + a 256-entry path cache) lives in `src/hidapi/windows/hid.c`. The DirectInput and Raw Input enumeration paths each carry one `SDL_HidmaestroIsAnsiHidPathHm` call site in `src/joystick/windows/SDL_dinputjoystick.c` and `SDL_rawinputjoystick.c`. The XInput backend is pristine upstream. XInput-side filtering happens through the OpenXInput fork PadForge ships next to SDL3.
2. **`XboxImpulseHidWriter` raw-HID enumeration**, in `PadForge.App/Common/Input/XboxImpulseHidWriter.cs`. When PadForge writes rumble + impulse-trigger reports directly to a physical Xbox One+ pad, it walks `HidD_GetHidGuid` + `DIGCF_DEVICEINTERFACE` and rejects any interface whose path contains `HIDMAESTRO` or whose `StableXInputInstance.FindAll` lookup misses (substring + 16-level PnP parent walk against hardware IDs).
3. **`HidHideController`** also classifies HM devices through a hardware-ID PnP walk (`IsHidMaestroDevice`), so the HidHide cloak whitelist treatment is consistent with the joystick-enumeration filters.

Step 1's `UpdateDevices` does **not** filter HM separately. It trusts the SDL3 fork's pre-filtered `SDL_GetJoysticks` result and opens every instance ID returned.

If you change HM's enumerator name, hardware ID, or ContainerID, all four surfaces (OpenXInput fork, SDL3 fork, `XboxImpulseHidWriter`, `HidHideController`) need to be kept in sync. See `hidmaestro-fork-resync-recipe.md` in project memory.

---

## Lifecycle: Step 5 invariants

`InputManager.Step5.VirtualDevices.cs` runs once per polling cycle and is responsible for matching the desired controller set (driven by user actions in the UI) against the live `_virtualControllers[]` array. Three invariants govern it:

### Invariant 1: HM lifecycle does NOT block the polling thread

Creating an HM controller can take 100 ms to several seconds depending on driver state and Windows PnP queues. Destroying one is similar. Doing either on the polling thread would freeze every other slot's input.

The fix (committed `aee6811`) routes both `CreateVirtualController` and `Destroy` through `Task.Run`. Per-slot state lives in two parallel arrays:

```csharp
private System.Threading.Tasks.Task[] _pendingConnectTask;
private System.Threading.Tasks.Task[] _pendingDisposeTask;
```

Pass 1 of Step 5 short-circuits if either task is in flight for that slot:

```csharp
{
    var inFlight = _pendingConnectTask[padIndex];
    if (inFlight != null && !inFlight.IsCompleted) continue;
}
```

Pass 2's create kickoff is fire-and-forget:

```csharp
_pendingConnectTask[capturedIndex] = Task.Run(() =>
{
    try {
        var vc = CreateVirtualController(capturedIndex);
        if (vc != null && vc.IsConnected) _virtualControllers[capturedIndex] = vc;
    }
    finally { _slotInitializing[capturedIndex] = false; }
});
```

`InputManager.Stop()` calls `AwaitPendingLifecycleTasks()` (30 s timeout via `Task.WaitAll`) before `DestroyAllVirtualControllers()` to make sure no orphan HM controllers leak past engine shutdown.

### Invariant 2: Inactivity destroy timeout

A user whose mapped device goes offline (laptop sleeps, USB hub unplugged, controller battery dies) will have the slot showing 0 online devices for as long as the device stays gone. Holding the HM controller open while no device feeds it wastes a kernel slot.

`HmInactivityTimeoutSeconds` (default 60, 0 disables) drives a per-slot countdown in Pass 1. The engine property mirrors the `HmInactivityDestroyTimeoutSeconds` setting. The grace counter only ticks when the slot has at least one mapped device that's currently offline. A slot with no mappings at all destroys its VC immediately, not on a timer:

```csharp
else if (isHMaestro && vc != null && HmInactivityTimeoutSeconds > 0 && !_hmInactivityFired[padIndex])
{
    int hmThresholdCycles = (HmInactivityTimeoutSeconds * 1000) / Math.Max(1, PollingIntervalMs);
    if (_slotInactiveCounter[padIndex] >= hmThresholdCycles)
    {
        _hmInactivityFired[padIndex] = true;
        VibrationStates[padIndex].LeftMotorSpeed = 0;
        VibrationStates[padIndex].RightMotorSpeed = 0;
        HmVcInactivityDestroyed?.Invoke(this, padIndex);
    }
}
```

The event hops to the UI thread, which calls `InputService.OnSlotInactivityTimedOut(padIndex)`. That method tears down the live HM controller (freeing its kernel slot) via `DestroyVirtualControllerAsync`, then runs the bubble-down cascade (`RunBubbleDownCascadeFromPosition`) across surviving HM VCs at higher visual positions in the same subgroup. This runs for every HM-backed subgroup (Xbox / PlayStation / Extended), not Xbox alone. Slot configuration is preserved end-to-end: `SlotCreated`, `SlotEnabled`, the `PadSetting`, the device mappings, the per-group slot order, and every other piece of slot state stays intact. `PadForge.xml` is not touched by the timeout firing.

Once the slot's mapped devices return online, `IsSlotActive(padIndex)` flips back to true, the latch clears, and Pass 2 recreates the same VC automatically at the correct visual-position kernel slot. The user's slot, mappings, profile, and per-group order all persist across the timeout cycle. The sidebar power dot stays green during the grace window (VC alive, devices offline) and turns yellow only after the timeout fires and the VC is torn down.

### Invariant 3: Bubble-down cascade on mid-stack destroy

Kernel-slot allocation hands out the lowest free index when a controller connects. Take an Xbox subgroup: positions 1, 2, 3 are all HM virtuals and the user destroys position 2. The kernel's user-index for positions 1 and 3 stays at 0 and 2. Position 3 does NOT drop to index 1. That contradicts the visual layout (positions renumber 1, 2 in the UI). The same order sensitivity applies to PlayStation and Extended: DirectInput, the SDL fork, and the raw-HID writers all observe HM device creation order, not only xinputhid. So the cascade runs for all three HM subgroups, not Xbox alone.

The fix is a destroy-and-recreate cascade, split across two engine calls on the delete path (`InputService.OnSlotDeleted`):

1. `RunBubbleDownCascadeAfterDelete(deletedType, oldPosition)` async-destroys (`DestroyVirtualControllerAsync`) every surviving HM VC at a position at or above the deleted slot's old position in the same subgroup. This is the step that tears the survivors' VCs down.
2. `CompactSlotsForGaps()` then compacts the pad indices so the controllers list stays contiguous from 0, driving a `PadViewModel` rebuild through `ApplyProfile`. It handles pad-index bookkeeping, not VC teardown.

Pass 2 of Step 5 recreates the destroyed VCs in ascending position order, so each lands one kernel slot lower than before. An external observer sees a natural disconnect/reconnect, exactly what happens when you unplug a real controller.

The engine gates each survivor on `IsHmVcAt` (any HM VC in the subgroup). The older Xbox-only `IsXboxHmVcAt` is kept only for Xbox-specific diagnostics. MIDI and KeyboardMouse have no kernel-slot ordering and are no-ops.

The same bubble-down cascade fires on the non-delete transitions, through `RunBubbleDownCascadeFromPosition`, which finds the slot's still-present position in its order list and destroys survivors above it. The inactivity-timeout path is Invariant 2. The sidebar-disable and all-devices-unassigned paths arrive via the engine's `HmVcWentNonActive` event.

This cascade fires on *destroy* transitions. Intra-group *reorder* is a separate flow that does not go through it. A drag-reorder within Xbox / PlayStation / Extended calls `InputManager.RerouteVirtualControllersForReorder`, which keeps the kernel VC at each visual position in place and just moves pad-index pointers. Same-profile positions reuse via pointer swap (zero teardown). Different-profile positions destroy and recreate. See [Services Layer](services-layer.md#slot-reordering) for the full per-position decision.

---

## FFB through HM PID descriptors

For Extended (and Custom HID) slots that expose force feedback, PadForge wires a HID PID (Physical Interface Device) descriptor inside the HM profile's HID report descriptor. Games using DirectInput discover the FFB device and write PID effect reports; `HMController.OutputReceived` delivers those raw output packets to PadForge, which feeds them into `HMaestroFfbDecoder` for parsing.

Decoder internals (all in `PadForge.App/Common/Input/HMaestroFfbDecoder.cs`):

```csharp
internal sealed class HMaestroFfbDecoder
{
    // Per-effect state, keyed by EffectBlockIndex.
    private sealed class EffectState     { ... }   // type, magnitude, direction, duration, started/stopped
    private struct ConditionAxis         { ... }   // per-axis Spring/Damper/Friction/Inertia coefficients
}
```

The decoder's `Apply(Vibration vib)` step collapses every active effect into a `Vibration` (a class in `PadForge.Engine/Common/ForceFeedbackState.cs`, null-checked on entry with `if (vib == null) return;`) carrying `LeftMotorSpeed` / `RightMotorSpeed` plus a directional / condition payload. Step 2's `ApplyForceFeedback` reads that `Vibration` through `VibrationStates[padIndex]` and hands it off to the per-pad-family writer (UserEffectsDispatcher for Sony, XboxImpulseHidWriter for Xbox One+, `ForceFeedbackState.SetDeviceForces` for SDL-rumble devices). Mirrors the v2 `ApplyMotorOutput` polar-split + dominant-effect-passthrough semantics but lives inside the decoder now.

---

## What's gone from the v2 vJoy story

Anything you remember from the old `vJoy-Deep-Dive.md` that does not appear above is **gone**. Specifically:

- **Phantom controller doubling (N nodes × N registry keys = N² controllers).** Gone. HM uses a single bus driver. There is no per-instance registry to manage.
- **DLL namespace cache (`StatNS_global`).** Gone. HM SDK is managed. No per-process caching DLL.
- **VJOYRAWPDO vs HID collection accounting.** Gone. HM exposes one HID device per controller, no sideband IOCTL PDO.
- **Single-node architecture rules / DICS_PROPCHANGE rebuild rules.** Gone. HM doesn't use SetupAPI device-node creation. It's WDF.
- **Generation-based re-acquire for `vJoyInterface.dll` handles.** Gone. HM SDK handles are GC-managed and don't go stale across device restarts.
- **HID descriptor written to registry, parsed only at EvtDeviceAdd.** Gone. HM profiles bundle the descriptor. Changing button/axis counts is a profile swap.
- **Auto-elevation for vJoy SetupAPI calls.** Gone. PadForge declares `requireAdministrator` in its app.manifest, so the whole process starts elevated. HM's `InstallDriver()` runs inside that already-elevated session to register the INF. No v2-style mid-session relaunch via `Verb = "runas"`.

The legacy v2 driver cleanup dialog (offered on the first launch that detects ViGEmBus or vJoy from a prior v2 install) handles uninstalling them. After that dialog runs, the user's machine has only HIDMaestro, HidHide, and (optionally) Windows MIDI Services. See [Driver Installation Internals](driver-installation-internals.md).

---

## See also

- [Virtual Controllers](../features/virtual-controllers.md): IVirtualController surface, per-category implementations.
- [Input Pipeline](input-pipeline.md): Step 5 in the broader 6-step polling loop context.
- [Driver Management](../features/driver-management.md): install + status flow for HIDMaestro plus install / uninstall flow for HidHide and Windows MIDI Services.
- [Driver Installation Internals](driver-installation-internals.md): the embedded installer and INF / pnputil mechanics.
- [Force Feedback](../features/force-feedback.md): user-facing rumble/FFB tuning controls.

---

Last updated for PadForge 4.0.0
