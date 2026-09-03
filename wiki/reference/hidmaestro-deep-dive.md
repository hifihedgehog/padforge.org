# HIDMaestro Deep Dive

PadForge routes every virtual gamepad except the MIDI and Keyboard+Mouse targets through [HIDMaestro](https://github.com/hifihedgehog/HIDMaestro), a single user-mode UMDF2 driver. This page documents the contract between PadForge and HIDMaestro, the OpenXInput shim that keeps PadForge's own slots out of its own enumeration, and the lifecycle invariants every Step 5 / Input Manager edit must uphold.

> If you are reading this looking for the legacy `vJoy-Deep-Dive.md`, that page is gone. v2 used vJoy + ViGEmBus as two separate drivers and inherited a long list of phantom-controller / N²-slot / DLL-cache bugs that came with vJoy's kernel-mode HID stack. v3 replaces both with HIDMaestro and the headaches with them. The seven virtual controller categories (Xbox, PlayStation, Extended, MIDI, KB+M, Nintendo, VR) live in [Virtual Controllers](../features/virtual-controllers.md).

---

## What HIDMaestro is

HIDMaestro (HM) is a UMDF2 (User-Mode Driver Framework 2) bus driver that publishes virtual HID controllers from user-mode. Each PadForge slot that is not MIDI or Keyboard+Mouse asks HM to instantiate a virtual device matching one of HM's **device profiles**. A profile bundles:

- A USB VID/PID pair
- A product string and OEM name
- A pre-recorded HID report descriptor (input + output + feature reports)
- Optional FFB PID descriptor pages

PadForge ships with HM 1.7.2 (`HIDMaestro.Core.dll`, FileVersion 1.7.2.0), which covers 231 profiles spanning Xbox 360 / Xbox One / Xbox Series / Elite / Adaptive, DualShock 3/4, DualSense / DualSense Edge, Switch Pro, the Steam Deck and both Steam Controllers, Logitech G-series wheels, Thrustmaster / Fanatec wheels, HOTAS / flight sticks, third-party gamepads (Hori, 8BitDo, PowerA, PXN, etc.), and a "Custom" profile that lets the Extended slot type build a HID descriptor from scratch.

The interim milestones a successor should know, each one PadForge's own call sites still cite by version:

| HM version | What landed | Where PadForge depends on it |
|---|---|---|
| v1.3.18 (HM#33) | Virtual Switch Pro profile and the IMU submission channel | `HMaestroVirtualController.cs:72` and `:935` |
| v1.3.21 (HM#37) | Switch Pro Bluetooth descriptor corrected to the real pad's wire shape | The Nintendo category's BT report shape |
| v1.3.22 (HM#38) | Input worker survives foreign stop signals, the structural fix for the frozen-output bug | `App.xaml.cs:274` (the startup orphan sweep's ordering barrier) |
| v1.4.0 (HM#39) | Composite USB personas with audio surfaces (speaker and haptic PCM out, mic in) | `AudioPassthroughService.cs:1405`, `HMaestroVirtualController.cs:87` |
| v1.4.1 (HM#41) | Ring-side audio truncation fixed | `AudioPassthroughService.cs:2332` |
| v1.4.3 (HM#42) | The usbip-vhci node HM owns is stamped, so the persona guard can identify it | `InputManager.Step1.UsbipVhciGuard.cs:18` |
| v1.5.1 (HM#48) | Second DS5 Edge paddle/Fn pair | `HMaestroVirtualController.cs:1458` |
| v1.6.0 (HM#32) | Native OpenVR driver behind `HMVRController` | `HMaestroVRController.cs:9` |
| v1.7.0 (HM#56) | Per-instance usbip serials and the three Valve composite persona profiles (`steam-deck-composite`, `steam-controller-composite`, `steam-controller-2`). They were withheld from the pickers until their art landed; `WithheldProfileIds` is empty at 4.4.0 | `HMaestroProfileCatalog.cs:297` (`WithheldProfileIds`), `ValveReportPackers.cs` |
| v1.7.1 (HM#58) | The Triton raw path: a profile that declares an input report id and is always armed emits a raw frame verbatim, and `SubmitRawExtendedReport` is the explicit form of that. Also corrects the 2026 pad's rear-button pairing to SDL's and throws at profile load on a button name that resolves to nothing | `HMaestroVirtualController.cs:449` (`SubmitRawReport`), `PadForge.App.csproj:173`. See [Raw frames](#raw-frames-submitrawreport-versus-submitrawextendedreport) |
| v1.7.2 (HM#59) | One Windows.Gaming.Input gamepad per Xbox 360 virtual instead of two | No PadForge code. Commit `6e9a9780` bumps the DLL. See [One WGI gamepad](#one-wgi-gamepad-per-xbox-360-virtual-hm59) |

### One driver, seven categories

The seven `VirtualControllerType` values map to HM as follows:

| Category | Backend | Description |
|---|---|---|
| Xbox (`Xbox = 0`) | HM | Xbox 360 / One / Series / Elite / Adaptive profiles. Acts as XInput device 1–4 when allocated a slot. |
| PlayStation (`PlayStation = 1`) | HM | DualShock 3/4, DualSense, DualSense Edge profiles. Reports as HID + DirectInput, plus the DualShock 4 extended report (touchpad, gyro/accel, battery) when supported. |
| Extended (`Extended = 2`) | HM | Any of the remaining HM profiles plus user-defined custom HID descriptors. Up to 8 axes, 128 buttons, 4 POV hats. The five Valve profiles live here: `steam-deck`, `steam-deck-composite`, `steam-controller`, `steam-controller-composite`, `steam-controller-2`. Four of them submit the pad's native input frame through `ValveReportPackers` instead of the field-encoded raw surface (see [Virtual Controllers](../features/virtual-controllers.md#valve-personas-issues-337-338)). |
| MIDI (`Midi = 3`) | Windows MIDI Services | NOT HM. Virtual MIDI endpoint via the Windows MIDI Services SDK. |
| KeyboardMouse (`KeyboardMouse = 4`) | Win32 SendInput | NOT HM. No driver. Pumps `INPUT` structures into the OS input queue. |
| Nintendo (`Nintendo = 5`) | HM | A virtual Switch Pro Controller (VID 057E, PID 2009, the Bluetooth wire shape) on a fixed catalog profile, no Customize. Rides the same raw-HID data path as Extended, with gyro passthrough over the HM v1.3.18 IMU channel and HOME LED control. |
| VR (`Vr = 6`) | HM | A SteamVR left plus right hand pair (issue #49) served by HIDMaestro's native OpenVR driver, one `HMVRController` pipe per slot. `HMaestroVRController` wraps it: `SubmitVrState(in VrRawState)` packs the pipeline state into `HMVRState`, and inbound `HapticReceived` pulses fan into the slot's `Vibration` lanes (left hand to left motor, right to right) with a 50 ms minimum pulse and a one-shot expiry timer. Slot creation refuses early when `HMVR.IsSteamVRInstalled` is false. |

Numeric values are preserved across the rename so legacy PadForge.xml files keep loading. `Xbox` carries `[XmlEnum("Microsoft")]` and `PlayStation` carries `[XmlEnum("Sony")]` purely as a back-compat accept-list for older settings files. This is the exception path, not the canonical naming.

---

## SDK surface PadForge talks to

The relevant assembly is `HIDMaestro.Core` (bundled at `PadForge.App/Resources/HIDMaestro/HIDMaestro.Core.dll`). Three primary types:

```csharp
// HMContext: process-wide entry point. One instance.
var context = new HMContext();
context.LoadDefaultProfiles();    // load the 231 embedded profile JSONs
context.InstallDriver();          // register HM with Windows (idempotent)

// HMProfile: handle to a profile (Xbox 360 wired, DualSense Edge, etc.).
// Returns HMProfile? (null when the id is not in the catalog).
HMProfile profile = context.GetProfile("xbox-series-xs-bt");
//   profile.Id, .Name, .ProductString, .VendorId, .ProductId
//   profile.AxisCount, .StickCount, .TriggerCount, .ButtonCount, .HasHat
//   profile.InputReportSize, .ExtendedReport (.AlwaysArmed, .ReportIdByte,
//   .Fields), .GetDescriptorBytes()
// HMProfile lives inside the HIDMaestro.Core binary. The members above are
// the ones PadForge's call sites read. PadPage reads AxisCount and splits it
// by the gamepad convention (first four axes pair into two sticks, the rest
// are triggers). Step 5 and PadViewModel read StickCount / TriggerCount
// directly off the SDK's simple-view properties (v1.3.9). ExtendedReport is
// the spec of a persona's native frame; the Valve wire test reads its
// Fields by reflection and asserts every named bit against the packer.

// HMController: a live virtual device instance. Construct via the context.
HMController controller = context.CreateController(profile);
//   controller.Profile               // HMProfile this device was built from
//   controller.SubmitState(in state) // ~1000 Hz hot path; HMGamepadState
//   controller.SubmitRawReport(rs)   // ReadOnlySpan<byte>; DS4 extended / custom HID
//   controller.SubmitRawExtendedReport(rs) // v1.7.1: the frame goes out verbatim, id included
//   controller.OutputReceived  += handler   // FFB / rumble feedback packets
//   controller.OutputDecoded   += handler   // decoded FFB events
//   controller.Dispose()             // tears down the live device
```

The VR category does not use those three. It talks to a separate trio in the same assembly: the static `HMVR` (`IsSteamVRInstalled`, `EnsureDriverRegistered`), `HMVRController` (the named-pipe device pair, `SubmitState`, `HapticReceived`), and the `HMVRState` / `HMVRButton` wire types. Because the transport is a named pipe inside `HIDMaestro.Core` rather than an RPC to a service, `HMaestroVRController.Connect` and `Disconnect` carry none of the bounded-call ceremony the MIDI wrapper needs for midisrv.

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
2. **`XboxImpulseHidWriter` XUSB interface enumeration**, in `PadForge.App/Common/Input/XboxImpulseHidWriter.cs`. When PadForge writes rumble + impulse-trigger reports directly to a physical Xbox One+ pad, it enumerates the XUSB interface class (`XUSB_INTERFACE_CLASS_GUID` + `DIGCF_PRESENT | DIGCF_DEVICEINTERFACE`) in SetupAPI order, skips any interface whose path contains `hidmaestro` (case-insensitive, the same fast path OpenXInput uses), and takes the Nth survivor where N is the slot parsed from SDL's `XInput#N` device path.
3. **`HidHideController`** also classifies HM devices through a hardware-ID PnP walk (`IsHidMaestroDevice`), so the HidHide cloak whitelist treatment is consistent with the joystick-enumeration filters.

Step 1's `UpdateDevices` carries a fourth, narrower check of its own: the **self-readback guard** (`InputManager.Step1.UpdateDevices.cs:160`). It is a backstop, not a replacement for the fork filter. A driver upgrade recreates the virtual devnodes with fresh instance paths and can slip past both the fork enumeration filter and the cloak, and when it does, SDL's Switch driver fights the virtual Switch Pro's protocol responder, cyclically resetting its inputs and interleaving rumble. The guard suppresses a wrapper when any of three markers hits:

- The serial starts with `HM-CTL-`.
- The device path contains `HIDMAESTRO`.
- The VID is Sony's `0x054C` and the path sits on a usbip-vhci node (`IsOnUsbipVhci`), which is the only discriminator a v1.4.0 composite persona carries, since a persona rides the real USB stack and has neither of the other two markers.

Its coverage is genuinely narrow. SDL's HIDAPI drivers overwrite the hid-level `HM-CTL-<n>` serial with a fabricated MAC during their identity handshake, and non-Xbox virtuals' interface paths carry no `HIDMAESTRO` marker (which is exactly why the fork filter reads DEVPKEY hardware IDs instead). So the guard catches failed-handshake and serial-preserving cases only. The fork enumeration filter remains the primary defense.

If you change HM's enumerator name, hardware ID, or ContainerID, all five surfaces (OpenXInput fork, SDL3 fork, `XboxImpulseHidWriter`, `HidHideController`, and Step 1's self-readback guard) need to be kept in sync. See `hidmaestro-fork-resync-recipe.md` in project memory.

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

Pass 2's create kickoff is fire-and-forget, and it claims the slot with an interlocked compare-exchange rather than a plain assignment:

```csharp
_pendingConnectTask[padIndex] = Task.Run(() =>
{
    try {
        var vcAsync = CreateVirtualController(capturedIndex);
        if (vcAsync != null && vcAsync.IsConnected)
        {
            // Claim only if the slot is still empty. HM bring-up takes
            // seconds, and a UI-thread reorder can install a reused VC at
            // this index meanwhile. A blind assign overwrote that pointer
            // and leaked the live kernel controller, unreachable from the
            // array that was its only handle.
            var prior = System.Threading.Interlocked.CompareExchange(
                ref _virtualControllers[capturedIndex], vcAsync, null);
            if (prior != null) { vcAsync.Dispose(); /* + re-attach prior's config */ }
            else if (vcAsync is HMaestroVirtualController) _hmaestroContext?.FinalizeNames();
        }
        // null => abort or driver failure; connected==false => dispose + latch
    }
    finally { _slotInitializing[capturedIndex] = false; }
});
```

Losing that race means this task built the spare, so it disposes itself. When the loser had already registered its `UserEffectsDispatcher` under the pad's key, disposing it removes the key, so the winner is re-attached (`AttachDeviceConfig`) to reclaim it. Only one HM connect is kicked off per polling cycle, which is what preserves the ascending-kernel-slot allocation guarantee.

`InputManager.Stop()` calls `AwaitPendingLifecycleTasks()` (30 s timeout via `Task.WaitAll`) before `DestroyAllVirtualControllers()` to make sure no orphan HM controllers leak past engine shutdown.

### Invariant 2: Inactivity destroy timeout

A user whose mapped device goes offline (laptop sleeps, USB hub unplugged, controller battery dies) will have the slot showing 0 online devices for as long as the device stays gone. Holding the HM controller open while no device feeds it wastes a kernel slot.

`HmInactivityTimeoutSeconds` (default 60, 0 disables) drives a per-slot grace period in Pass 1. The engine property mirrors the `HmInactivityDestroyTimeoutSeconds` setting. The grace only runs when the slot has at least one mapped device that's currently offline. A slot with no mappings at all destroys its VC immediately, not on a timer.

The elapsed time is wall clock, not polling cycles. `_slotInactiveSinceMs[padIndex]` is stamped on the grace's first tick and the threshold compares milliseconds. The older shape converted seconds into cycles using the live `PollingIntervalMs`, so changing the polling rate mid-grace rescaled a pending timeout (60 s at 1 ms became roughly 4 s after a switch to 16 ms, and the reverse stretched it). `_slotInactiveCounter` survives only for the trace and for Pass 2's zero versus non-zero eligibility test, and it saturates at `int.MaxValue` rather than wrapping.

```csharp
long inactiveMs = Environment.TickCount64 - _slotInactiveSinceMs[padIndex];
bool isHMaestro = vc is HMaestroVirtualController;

if (!isHMaestro && vc != null && HmInactivityTimeoutSeconds > 0
    && inactiveMs >= HmInactivityTimeoutSeconds * 1000L)
{
    // MIDI / KeyboardMouse: teardown is cheap and has no kernel-slot
    // ordering concern, so destroy inline.
    DestroyVirtualController(padIndex);
    _virtualControllers[padIndex] = null;
    VibrationStates[padIndex].LeftMotorSpeed = 0;
    VibrationStates[padIndex].RightMotorSpeed = 0;
}
else if (isHMaestro && vc != null && HmInactivityTimeoutSeconds > 0
         && !_hmInactivityFired[padIndex])
{
    if (inactiveMs >= HmInactivityTimeoutSeconds * 1000L)
    {
        System.Threading.Volatile.Write(ref _hmInactivityFired[padIndex], true);
        VibrationStates[padIndex].LeftMotorSpeed = 0;
        VibrationStates[padIndex].RightMotorSpeed = 0;
        HmVcInactivityDestroyed?.Invoke(this, padIndex);
    }
}
```

The dropout grace is one user-facing contract across every slot type: MIDI and Keyboard+Mouse ride the same `HmInactivityTimeoutSeconds` as the HM-backed categories. They differ only in what happens at the end, because a non-HM slot has no kernel-slot ordering to repair and tears down inline instead of raising the cascade event.

The event hops to the UI thread, which calls `InputService.OnSlotInactivityTimedOut(padIndex)`. That method tears down the live HM controller (freeing its kernel slot) via `DestroyVirtualControllerAsync`, then runs the bubble-down cascade (`RunBubbleDownCascadeFromPosition`) across surviving HM VCs at higher visual positions in the same subgroup. This runs for every HM-backed subgroup (Xbox / PlayStation / Nintendo / Extended), not Xbox alone. Slot configuration is preserved end-to-end: `SlotCreated`, `SlotEnabled`, the `PadSetting`, the device mappings, the per-group slot order, and every other piece of slot state stays intact. `PadForge.xml` is not touched by the timeout firing.

Once the slot's mapped devices return online, `IsSlotActive(padIndex)` flips back to true, the latch clears, and Pass 2 recreates the same VC automatically at the correct visual-position kernel slot. The user's slot, mappings, profile, and per-group order all persist across the timeout cycle. The sidebar power dot stays green during the grace window (VC alive, devices offline) and turns yellow only after the timeout fires and the VC is torn down.

### Invariant 3: Bubble-down cascade on mid-stack destroy

Kernel-slot allocation hands out the lowest free index when a controller connects. Take an Xbox subgroup: positions 1, 2, 3 are all HM virtuals and the user destroys position 2. The kernel's user-index for positions 1 and 3 stays at 0 and 2. Position 3 does NOT drop to index 1. That contradicts the visual layout (positions renumber 1, 2 in the UI). The same order sensitivity applies to PlayStation and Extended: DirectInput, the SDL fork, and the raw-HID writers all observe HM device creation order, not only xinputhid. So the cascade runs for all three HM subgroups, not Xbox alone.

The fix is a destroy-and-recreate cascade, split across two engine calls on the delete path (`InputService.OnSlotDeleted`):

1. `RunBubbleDownCascadeAfterDelete(deletedType, oldPosition)` async-destroys (`DestroyVirtualControllerAsync`) every surviving HM VC at a position at or above the deleted slot's old position in the same subgroup. This is the step that tears the survivors' VCs down.
2. `CompactSlotsForGaps()` then compacts the pad indices so the controllers list stays contiguous from 0, driving a `PadViewModel` rebuild through `ApplyProfile`. It handles pad-index bookkeeping, not VC teardown.

Pass 2 of Step 5 recreates the destroyed VCs in ascending position order, so each lands one kernel slot lower than before. An external observer sees a natural disconnect/reconnect, exactly what happens when you unplug a real controller.

The engine gates each survivor on `IsHmVcAt`, which is a plain `is HMaestroVirtualController` type check, so it covers Nintendo alongside Xbox / PlayStation / Extended. The older Xbox-only `IsXboxHmVcAt` is kept only for Xbox-specific diagnostics. MIDI, KeyboardMouse, and VR fail that type check (`MidiVirtualController`, `KeyboardMouseVirtualController`, and `HMaestroVRController` are separate types), and none of the three has a kernel-slot ordering to repair, so they are no-ops.

The same bubble-down cascade fires on the non-delete transitions, through `RunBubbleDownCascadeFromPosition`, which finds the slot's still-present position in its order list and destroys survivors above it. The inactivity-timeout path is Invariant 2. The sidebar-disable and all-devices-unassigned paths arrive via the engine's `HmVcWentNonActive` event.

This cascade fires on *destroy* transitions. Intra-group *reorder* is a separate flow that does not go through it. A drag-reorder within Xbox / PlayStation / Extended calls `InputManager.RerouteVirtualControllersForReorder`, which keeps the kernel VC at each visual position in place and just moves pad-index pointers. Same-profile positions reuse via pointer swap (zero teardown). Different-profile positions destroy and recreate. See [Services Layer](services-layer.md#slot-reordering) for the full per-position decision.

---

## Raw frames: SubmitRawReport versus SubmitRawExtendedReport

Two raw submit paths exist on `HMController`, and which one a frame takes decides which report id it leaves on.

`SubmitRawReport` takes data bytes. The driver prepends a report id, and the id it prepends is the descriptor's first input report id. That is the right answer for every Sony USB profile, whose descriptor leads with Report 0x01. It is the wrong answer for Valve's 2026 Steam Controller (`steam-controller-2`): that pad carries its lizard-mode mouse (report 0x40) and keyboard (0x41) on the same interface as its controller state (0x42), and the mouse comes first. PadForge's packer builds the full 54-byte on-wire frame with 0x42 at byte 0. Treated as data, the frame shifted one byte and went out re-headed as 0x40, so byte 1, the rolling sequence number, landed on the mouse's relative X at 250 Hz and creating the virtual controller sent the cursor tearing sideways until the slot was deleted (owner report, 2026-08-28).

HM v1.7.1 (HM#58) fixed it on the driver side. A profile that declares an `extendedReport.reportId` and is `alwaysArmed` now emits a raw frame verbatim through the same extended path `SubmitState` uses. The driver infers the caller's convention from length: a frame the size of the declared input report already carries its id, one byte shorter is the data-only form and gets the id prepended. `SubmitRawExtendedReport` is the explicit form: the frame goes out verbatim whatever the profile declares.

PadForge calls the explicit one. `HMaestroVirtualController.SubmitRawReport` (`HMaestroVirtualController.cs:449`) forwards to `SubmitRawExtendedReport` when `_extendedFrameCarriesItsOwnId` is set, and to `SubmitRawReport` otherwise. The flag is computed once in the constructor (`:216`): `ExtendedReport != null && ExtendedReport.AlwaysArmed && ExtendedReport.ReportIdByte != 0`. Saying it outright means the pairing cannot flip the day a packer size or a declared size moves by one, which HM's length inference would let happen in silence.

What stays on the PadForge side is a tripwire, never a gate. `HMaestroProfileCatalog.LeadsWithAPointingReport` (`HMaestroProfileCatalog.cs:334`) parses a descriptor and returns true when its first input report sits in a Generic Desktop Mouse or Keyboard collection. `PadForge.Tests/PointingReportProfileGuardTests.cs` uses it two ways: `PackerFramesCarryTheirOwnReportId` asserts every Valve packer's frame size equals its profile's `InputReportSize`, and `APointingLedPackerProfileTakesTheVerbatimPath` asserts that any pointing-led profile with a packer declares the always-armed report id that puts it on the verbatim path. Commit `581264e9` had dropped such profiles from the pickers and refused to build them on the Extended creation path. Commit `662e174a` reversed that the same day: withdrawing a working profile over a driver defect was not a call to make on the owner's behalf. At 4.4.0 the 2026 Steam Controller is in the picker, `WithheldProfileIds` is empty, and no creation path refuses a profile.

HM#58 also corrected the 2026 profile's rear-button pairing to SDL's. PadForge's packer already had it right (R4 on bit 7, R5 on bit 8, L4 and L5 on 17 and 18), so the packer did not change. The profile now names all four (`RightPaddle`, `RightPaddle2`, `LeftPaddle`, `LeftPaddle2`).

---

## One WGI gamepad per Xbox 360 virtual (HM#59)

A Virtual Xbox 360 Controller registered as two gamepads on Windows.Gaming.Input surfaces while XInput saw one, so the Start menu double-stepped and games on WGI read every input twice (discussion #378, issue #380). Xbox One, Elite, and Series virtuals never doubled: they run in HM's single-device `xinputhid` mode.

The cause was in the driver. HM's Xbox 360 architecture builds an XUSB companion beside the main HID parent and stamps `UpperFilters="xinputhid"` on that parent so WGI's PnP-added handler skips the HID-backed duplicate. `DeviceOrchestrator` started the main devnode in step 3 and stamped the marker in step 5, after creating the companion, and WGI never re-evaluates a devnode on a registry-only change. Measured on a Windows 11 26200 bench: the marker was absent at devnode arrival on 5 of 5 fresh creates and 4 of 5 doubled. Toggling the property by hand and restarting the devnode moved the count between 2 and 1 reversibly, which is the 30-second test that settled the mechanism.

HM v1.7.2 writes the marker before devnode registration and restarts the main devnode once after the companion exists. The restart is the operative leg: WGI's first arrival is not gated on the property even when it is pre-set, only a re-arrival is. Verified against the v1.7.2 harness: five fresh `xbox-360-wired` creates each enumerate exactly one WGI Gamepad with XInput intact, and the Series and One-S controls hold at one. No PadForge code is involved. The harness reproduced the double without PadForge, and the fix arrived with the vendored SDK bump in commit `6e9a9780` (full suite 5,202 green with the new DLL).

---

## FFB through HM PID descriptors

For Extended (and Custom HID) slots that expose force feedback, PadForge wires a HID PID (Physical Interface Device) descriptor inside the HM profile's HID report descriptor. Games using DirectInput discover the FFB device and write PID effect reports. `HMController.OutputReceived` delivers those raw output packets to PadForge, which feeds them into `HMaestroFfbDecoder` for parsing.

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

*Last updated for PadForge 4.4.0.*
