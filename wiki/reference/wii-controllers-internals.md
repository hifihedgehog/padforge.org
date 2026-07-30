# Wii Controllers Internals

*How a Bluetooth Wii controller becomes a mappable pad: the Win32 pairing ceremony in `WiiPairingService`, the SDL `hidapi_wii` read path, and the post-pair hint-toggle recovery in `InputManager`.*

This is the developer-side companion to [Wii Controllers](../devices/wii-controllers.md) (the user guide) and issue #116.

---

## Division of labor

*What PadForge owns versus what SDL owns once a controller is paired.*

PadForge owns one thing: the OS-level Bluetooth pairing handshake. Windows cannot drive that handshake from its own pairing UI, because a Wii controller's PIN is six raw bytes that depend on which sync button was pressed, not a typed string. `WiiPairingService` runs the handshake with the deprecated `bthprops.cpl` API.

After the controller is bonded, SDL reads the standard pad state. SDL's `hidapi_wii` driver enumerates the paired device, parses its reports, and surfaces it as an ordinary SDL gamepad. It then flows through `SdlDeviceWrapper` and the normal six-step pipeline (see [Input Pipeline](input-pipeline.md)) exactly like an Xbox or DualSense pad. There is no Wii-specific `InputDeviceType`, no synthetic identity, and no custom sub-state. This is unlike [MIDI input](midi-input-internals.md) (a bespoke `MidiInputDevice` with `InputDeviceType.Midi`) and unlike a [Remote Link](remote-link-internals.md) peer (`RemotePeerDevice` on a `peer://` path). The earlier direct-HID read path (`WiiControllerHidDevice`) was removed once SDL could drive the controller.

The buttons, sticks, and D-pad reach the pipeline through the generic SDL gamepad mapping with no Wii-aware code. The Wii-specific reads sit on top of that path in `SdlDeviceWrapper`: the IR-pointer axes for a Wii Remote (#146), the four load-cell corners for a Balance Board (#146), and the enable of SDL's `hidapi_wii` driver via one hint. The Wii Remote speaker (#146) is a separate output path in `WiiSpeakerService`, not part of the read side.

So the data flow is: PadForge pairs over Bluetooth, the Microsoft Bluetooth stack writes the link key, SDL opens the now-stable HID device, and PadForge maps it through the generic SDL path with a Wii-specific overlay for IR, the Balance Board, and the speaker.

---

## Files

| File | Role |
|---|---|
| `PadForge.App/Services/WiiPairingService.cs` | The pairing ceremony. `public sealed class`, P/Invoke over `bthprops.cpl`. Original C# over the Win32 Bluetooth API, following the sequence Dolphin's `Source/Core/Core/HW/WiimoteReal/IOWin.cpp` documents (no Dolphin GPL code). |
| `PadForge.App/Views/PairDeviceDialog.xaml.cs` | The Fluent dialog, family-selectable via a Controller Family combo (Nintendo Wii / Sony DualShock 3). The Wii branch loops `RunPairingPass` on a background thread until a controller pairs or the user cancels. Picking DualShock 3 hides the temporary-pairing checkbox and routes `Pair_Click` to `PairDs3` / `Ds3PairingService` instead (out of scope here). |
| `PadForge.App/Common/Input/InputManager.cs` | The SDL Wii hint at `InitializeSdl` (line 601) and `RescanWiiControllers` (line 906). |
| `PadForge.App/MainWindow.xaml.cs` | The `PairRequested` handler (~712) that opens the dialog then runs the rescan, and the 100 ms `_sdlPumpTimer`. |
| `PadForge.App/Services/InputService.cs` | `RescanWiiControllers` passthrough to the input manager (line 8703). |
| `PadForge.Engine/Common/SdlDeviceWrapper.cs` | The capability gate that stops a stickless Wii Remote from advertising phantom stick axes, the `HasIrCamera` / `IsBalanceBoard` detection, and the IR-pointer read (`ReadIrPointer`). |
| `PadForge.Engine/Common/Mapping/SourceCoercion.cs` | `ReadTunedBalanceBoard`: the Lean X / Lean Y / Total Weight coercions from the four corner load cells. |
| `PadForge.App/Common/Input/WiiSpeakerService.cs` | The Wii Remote speaker output sink. `internal static class`, 8-bit PCM at 2 kHz over the raw HID handle. |
| `PadForge.Engine/Haptics/WiiSpeakerAdpcm.cs` | Yamaha 4-bit ADPCM codec. Compiled and unit-tested, off the live speaker path. |

The pairing service depends only on `bthprops.cpl` and `kernel32.dll`. No managed Bluetooth library is involved.

---

## WiiPairingService: one inquiry-and-pair pass

*The `RunPairingPass` flow, the inquiry parameters, and why a pass returns every device state.*

`RunPairingPass(bool temporary, CancellationToken ct)` runs a single Bluetooth inquiry and tries to bond every Wii controller it finds in pairing mode. The sequence is `BluetoothFindFirstRadio` to get the host radio handle, `BluetoothGetRadioInfo` to read the host address and name, then `BluetoothFindFirstDevice` and `BluetoothFindNextDevice` to walk the inquiry results. The inquiry uses `cTimeoutMultiplier = 2`, about 2.5 seconds per pass. The call blocks for that duration, so the dialog runs it on a background thread through `Task.Run`.

The search parameters set every return flag, not just unknown devices:

| `BLUETOOTH_DEVICE_SEARCH_PARAMS` field | Value | Reason |
|---|---|---|
| `fReturnAuthenticated` | 1 | See an already-bonded controller. |
| `fReturnRemembered` | 1 | See a stale half-paired record so it can be reset. |
| `fReturnUnknown` | 1 | See a fresh, never-paired controller. |
| `fReturnConnected` | 1 | See a controller that is already live. |
| `fIssueInquiry` | 1 | Actually scan the air, not just read cached state. |
| `cTimeoutMultiplier` | 2 | About 2.5 s of inquiry. |

Filtering out the remembered state would hide a controller left half-paired by an earlier attempt, so it could never be reset and re-paired. Returning all four states is what makes that record visible to the cleanup step.

`RunPairingPass` returns a `PairPassResult` carrying the Wii controllers seen this pass (`Found`), the ones it bonded (`Paired`), the total device count from the inquiry (`DiscoveredCount`), and an `Error` string (`no-radio`, `radio-info`, `no-bluetooth-stack`, or `exception`, null on success). `PairDeviceDialog` loops passes, accumulating found controllers in a `HashSet`, and stops on the first pass that bonds one or when the user cancels. Dolphin runs a fixed three iterations per click. PadForge instead loops until success or cancel.

One cross-cutting side effect matters when a DualShock 3 is in play. If BthPS3 is installed (`Ds3DriverInstaller.IsBthPs3Installed()`), the pass forces its PSM patching off for the whole inquiry-and-pair pass (issue #199) and restores it to policy in the outer `finally` on every exit path (`Ds3PairingService.ReconcilePsmPatchForCrashSafety("wii-pass-end")`). A Wii Remote's incoming HID connection must not enter BthPS3's identify/deny/destroy path, where the upstream use-after-free lives, so with patching off the Wii's standard HID PSMs pass through to the inbox Bluetooth stack, which is where a Wii Remote belongs anyway. See [Driver Management](../features/driver-management.md) for the BthPS3 crash-safety detail.

---

## Discovery match

*How a pass decides a discovered device is a Wii controller and not a stray keyboard.*

A device matches if its advertised name starts with `Nintendo` (case-insensitive). Every Wii peripheral advertises a `Nintendo RVL-CNT-01` style name. A fresh inquiry of a never-seen device often returns an empty name, so there is a fallback: when the name is empty, the device matches only on an exact Class-of-Device value.

| Class of Device | Controller |
|---|---|
| `0x002504` | Wii Remote |
| `0x000508` | Wii Remote Plus / -TR |

`IsWiiClassOfDevice` matches those two exact values rather than the broad Peripheral major class. A broad match would try to pair a stray Bluetooth keyboard or mouse that happens to be in discovery range. The Class-of-Device fallback only fires when the name is empty, so a named device is never matched by class.

---

## The two PIN modes

*How the SYNC button and the 1+2 hold map to two different PINs, and how the PIN bytes are derived.*

A Wii controller has two sync methods, and each one expects a different six-byte PIN.

| Mode | Trigger | `temporary` | PIN source | Bonding |
|---|---|---|---|---|
| SYNC | Red SYNC button under the battery cover | `false` | The host radio's own address (`radioInfo.address`) | Persistent. Reconnects on any button press afterward. |
| 1+2 | Hold the **1** and **2** buttons | `true` | The controller's own address (`deviceInfo.Address`) | Session only. Not bonded, so it re-pairs next time. |

The PIN derivation is the same shape in both modes. The six Bluetooth-address bytes are taken low byte first, each widened into one `WCHAR`, and the passkey length is 6:

```csharp
char[] passkey = new char[6];
for (int i = 0; i < 6; i++)
    passkey[i] = (char)((pinSource >> (8 * i)) & 0xFF);
```

This exact shape is what the deprecated authentication API expects and what Dolphin passes.

---

## The deprecated authentication sequence

*The three-call bonding sequence Dolphin proved, and why the callback path is not used.*

`TryPairDevice` runs the bonding for one discovered controller. The important detail from Dolphin: do not use the `BluetoothRegisterForAuthenticationEx` callback path. Use the deprecated `BluetoothAuthenticateDevice` with the PIN passed directly. The sequence, when the device is not already authenticated:

1. **`BluetoothAuthenticateDevice(IntPtr.Zero, hRadio, ref device, passkey, 6)`.** The PIN is the wide-char array above, length 6. A non-zero return aborts the pair.
2. **`BluetoothEnumerateInstalledServices(hRadio, ref device, ref pcServices, IntPtr.Zero)`.** A count-only query with a null service array. Dolphin notes this "must be done to make the remote remember the pairing." `ERROR_MORE_DATA` (234) is tolerated as success because the count query is expected to report that more data exists.
3. **`BluetoothSetServiceState(hRadio, ref device, HumanInterfaceDeviceServiceClass_UUID, BLUETOOTH_SERVICE_ENABLE)`.** Enables the HID service so the controller appears as a HID device. The UUID is `{00001124-0000-1000-8000-00805F9B34FB}`.

When the device is already authenticated (a re-pair of a remembered controller), steps 1 and 2 are skipped and only the HID-service enable runs.

Every step is written to the in-memory diagnostics ring (crash context) with its return code, so a failed bond is diagnosable from the real handshake trace rather than a generic error. The dialog itself sees only the pass result (the found and paired controller names and any error), not the per-step trace.

---

## Cleanup of unusable records

*How a stale half-paired record is forgotten so the next pass can rediscover it.*

This is Dolphin's `RemoveUnusableWiimoteBluetoothDevices`, inlined into the pass loop. For each discovered Wii controller:

- **Already connected** (`fConnected != 0`): leave it alone. It is working. The pass counts it as found and paired and moves on.
- **Remembered but not authenticated and not connected** (`fRemembered != 0 && fAuthenticated == 0`): this record cannot reconnect and it blocks re-pairing. `BluetoothRemoveDevice(ref deviceInfo.Address)` forgets it, and the next pass rediscovers it fresh.
- **Otherwise**: proceed to `TryPairDevice`.

So a controller stuck in a remembered-but-dead state is reset automatically across passes, which is why the search returns the remembered state in the first place.

---

## Struct marshaling

*Why the interop structs use default packing, and the failure mode when they do not.*

Default packing is required on every Bluetooth struct. `Pack = 1` would undersize them and the API rejects the `dwSize` field with `ERROR_REVISION_MISMATCH` (1306). The cause is `BLUETOOTH_ADDRESS`, an 8-byte (`ULONGLONG`) union that is 8-byte aligned, so the native layout has pad bytes the packed layout drops.

| Struct | Natural size | Note |
|---|---|---|
| `BLUETOOTH_RADIO_INFO` | 520 bytes | 4 pad bytes after `dwSize` before the 8-byte-aligned address. |
| `BLUETOOTH_DEVICE_INFO` | 560 bytes | Same alignment requirement. |
| `BLUETOOTH_DEVICE_SEARCH_PARAMS` | default | The trailing `IntPtr hRadio` must land on its 8-byte slot. |

Each struct sets its `dwSize` from `Marshal.SizeOf<T>()` before the call, so the managed size and the native size must agree, which only holds under natural alignment. String fields are `ByValTStr` with `SizeConst = 248` and `CharSet.Unicode`.

---

## Elevation

*Why the process must be elevated and how the failure surfaces.*

`BluetoothAuthenticateDevice` and `BluetoothSetServiceState` return `ERROR_ACCESS_DENIED` (5) from a non-elevated process. PadForge always runs elevated (HIDMaestro requires it), so this is satisfied in normal use. The service maps the common return codes for the log through `DescribeError`:

| Code | Meaning |
|---|---|
| 5 | `ACCESS_DENIED` (need elevation) |
| 31 | `GEN_FAILURE` |
| 87 | `INVALID_PARAMETER` |
| 170 | `BUSY` |
| 234 | `MORE_DATA` |
| 259 | `NO_MORE_ITEMS` |
| 1167 | `DEVICE_NOT_CONNECTED` |

---

## IsWiiConnected and pairing narration

*An uncalled public helper, and where the pairing narration actually goes.*

`IsWiiConnected()` is a fast state read with `fIssueInquiry = 0`, so it returns the radio's current connection state without paying the 2.5-second inquiry. Its intent, stated in the doc comment, is to time the SDL re-enumeration to the moment the controller actually connects (which happens on a button press, possibly seconds after the pair completes) rather than a fixed delay. It has no caller today. The shipped post-pair recovery uses the fixed-cadence `RescanWiiControllers` instead, which the `MainWindow` `PairRequested` handler runs unconditionally after the dialog closes.

PadForge writes no pairing log file. The private `Log` helper is a one-line delegate to the in-memory diagnostics ring: `SdlDiagLog.WriteLine("WIIPAIR " + message)`, the same crash-context buffer the rest of the app narrates into. That ring is the only narration sink. The dialog shows only the pass result (found and paired names from `PairPassResult`), not the per-step handshake trace. There is no `LogPath`, no `LogLine`, and no lock or `try/catch` around logging, because a ring write does not throw the way a file write can. `RescanWiiControllers` does not narrate.

---

## The reading side: the SDL Wii hint

*The single hint that turns on SDL's Wii driver and what it does at enumeration time.*

`InitializeSdl` sets `SDL_SetHint(SDL_HINT_JOYSTICK_HIDAPI_WII, "1")` at line 601, before `SDL_Init`. That enables SDL's `hidapi_wii` driver. It surfaces the Bluetooth-paired controller, parses all four forms (Wii Remote / Plus, Remote plus Nunchuk, Classic / Pro, Wii U Pro), and lights the player LED, which stops the idle flashing the controller does while unassigned. From there the standard buttons, sticks, and D-pad are an ordinary SDL gamepad. The only Wii-aware reads on top of that are the IR pointer and the Balance Board corners, both covered below.

One enumeration detail matters for the stickless Wii Remote. `SdlDeviceWrapper.GetDeviceObjects` gates each standard axis on `SDL_GamepadHasAxis` (the axis path mirrors the existing button gate on `SDL_GamepadHasButton`). A Wii Remote with no Nunchuk has no sticks, so it must not advertise phantom Left or Right Stick axes. A phantom axis reads as a dead center, and `CreateDefaultPadSetting`'s auto-map trusts the `DeviceObjects` capability list, so without the gate it would pin both virtual sticks to a corner. See [SDL3 Integration](sdl3-integration.md) for the wrapper detail.

---

## Wii Remote IR pointer (#146)

*The two sensor-bar dots, where SDL posts them, and how `ReadIrPointer` turns them into an aim point.*

The IR camera path rides the same `SdlDeviceWrapper` read that surfaces the pad. It is gated by `HasIrCamera`, set at enumeration (`~377`): the device is the Wii VID `0x057E`, it is not a Balance Board, and its raw joystick axis count is 10 or more. Reading the raw axis count (`SDL_GetNumJoystickAxes`), not the gamepad-pinned `NumAxes` of 6, is the stable signal, and it is the same idiom the right Joy-Con NIR and Joy-Con 2 mouse detections use.

The SDL fork's `hidapi_wii` driver posts the two IR dots on dedicated joystick axes 6-9 (SDL#6 follow-up `41909fdc4e`), separate from the gamepad sticks so a Nunchuk or Classic extension keeps axes 0-3. Axis 6 is dot 0 X (`0..1023`), axis 7 is dot 0 Y (`0..767`), axis 8 and 9 are dot 1. A value of `-1` means the dot is not detected.

`ReadIrPointer` (`SdlDeviceWrapper.cs`, `~662-685`) runs after the standard state read, joystick-direct, because the gamepad mapping does not surface these axes. It reads the four values through `ComputeIrAim` into `CustomInputState.Ir` (a `WiiIrState` with `X`, `Y`, `Detected`):

- All four at exactly 0 means no report has arrived yet (two dots on one pixel is physically impossible), so `Detected` is set false rather than yanking the pointer to a corner on connect.
- The aim exists only when BOTH sensor-bar dots are visible. `ComputeIrAim` returns `Detected = false` if any of the four dot slots reads negative (fewer than two dots: out of reach). There is no single-dot fallback. Snapping the midpoint to the surviving dot would sit half a dot-separation away, and a steady sweep would re-walk that span of the screen (the #203 bench "double walk"). Every proven reference (Touchmote, Ryochan7-lightgun, Suegrini-4IR, WiimoteLib) computes the aim as a dot-pair midpoint and treats fewer than two dots as out of reach.
- The `1024x768` camera frame is normalized to the `[-1..+1]` stick range with X mirrored and Y direct, grounded against Touchmote and WiimoteLib.

The wrapper stores only the raw screen-aligned aim. All tuning is applied later at the slot-scoped read in `SourceCoercion.ReadTunedIrPointer`, because one remote can feed several virtual controllers, each with its own settings. That read applies four stages in order:

1. **Lineage margin stretch** (base aim map, #203 pointer modes): `IrMarginStretchX = 1.8`, `IrMarginStretchY = 2.0`, applied first. A tracked pair midpoint physically cannot reach +/-1, because both LEDs must stay in the camera view. Without this stretch the cursor walls off inside the screen in every pointer mode. This is the base map, not an optional extra.
2. **Sensor-bar offset** (Y only): the Pointer-tab vertical bar offset, in post-stretch screen space, matching Touchmote's `offsetY`.
3. **EMA smoothing**: a per-(device, slot, axis) exponential moving average, clamped to `[0..0.95]`, dropped on sight loss so a re-acquire snaps instead of sliding in from stale.
4. **Per-source sensitivity**: `MappingSource.IrPointerSensitivity` (default `1.0`), a mapping-row Slider with a reset button on the "IR Pointer X/Y" rows, then a final clamp to `[-1..+1]`.

---

## Wii Balance Board (#146)

*How the board is told apart, how the corner loads reach the mapping grid, and the calibration source.*

`IsBalanceBoard` is set at enumeration (`~370`): the Wii VID plus an SDL name that contains "Balance Board". The board enumerates as a Wii Remote (PID `0x0306`), so the name is the only reliable discriminator, and it is what keeps the board out of the `HasIrCamera` gate.

The four corner load cells ride the gamepad stick axes: `ReadTunedBalanceBoard` (`SourceCoercion.cs`, `~1050-1101`) reads `Axis[0]`, `Axis[1]`, `Axis[3]`, `Axis[4]` as top-left, bottom-left, top-right, bottom-right, undoing the unsigned `+32768` shift and clamping negatives to 0. It coerces three sources by descriptor suffix:

- **Lean X**: `(right - left) / total`, clamped to `[-1..+1]`.
- **Lean Y**: `(top - bottom) / total`.
- **Total Weight**: each corner converted to kilograms and summed, minus the tare, scaled against `BalanceMaxKg`.

Calibration is auto-parsed, not user-entered. The SDL fork exposes the board's 24-byte calibration block as the hex property `SDL.joystick.wii.balance_board_calibration`, which `InputService.ParseBalanceCalibrationHex` reads once and re-lays into the 12-float `[corner × {Kg0, Kg17, Kg34}]` shape the coercion interpolates. Without calibration, Total Weight falls back to a coarse raw-sum approximation so the source stays monotonic.

`SetBalanceTare` (`InputService.cs`, `~9109`) captures the current total weight as the zero-point so Total Weight reads 0 with whatever is on the board. It is code-reachable only. No UI element calls it today.

---

## Wii Remote speaker (#146)

*The output side: macro sounds through the Wii Remote's built-in speaker, and why the live path is PCM, not ADPCM.*

`WiiSpeakerService` (`PadForge.App/Common/Input/WiiSpeakerService.cs`) is the Nintendo analogue of the Sony speaker path in `AudioPassthroughService`. A Wii Remote assigned to a slot becomes an output sink whose `MacroMixer` is returned to `SoundMacroService` alongside the Sony sinks, so a macro Play Sound fans out to it with no macro-layer change. It gates on the Wii Remote PIDs `0x0306` (RVL-CNT-01) and `0x0330` (Wii Remote Plus / -TR).

The live path streams signed 8-bit PCM at 2000 Hz, the WiiBrew-recommended config for slow Bluetooth stacks. The 48 kHz macro mix is resampled to 2000 Hz mono, quantized to 8-bit, and written as one `0x18` speaker report of 20 PCM samples per 10 ms tick (100 reports/s), never in bursts. The 20 is the sample count, not the wire frame size: the on-the-wire report is a report id, a control byte (`(len<<3)`), and the 20 payload bytes, zero-padded to the device's `OutputReportByteLength` (`ReportLen = 22` floor). The init sequence (`0x14` enable, `0x19` mute, the `0xa20001` register config for format `0x40` / rate `0x1770` / volume `0xFF`, then `0x19` unmute) is the WiiBrew sequence with register offsets grounded in Dolphin's `Speaker.h`. Output writes go through overlapped `WriteFile` when the BT stack accepts it, falling back to `HidD_SetOutputReport`.

PCM is memoryless, which is the point. A dropped or late report on the SDL-shared BT link is a single click, not the cascading garble that differential ADPCM produces. `WiiSpeakerAdpcm.cs` (Yamaha 4-bit ADPCM) is compiled and unit-tested as the verified reference codec but stays off the live streaming path. The service also supports a system-audio loopback mirror, the same option the DualSense path offers.

---

## RescanWiiControllers: post-pair recovery

*Why a freshly-paired controller needs a forced re-open, and the hint-toggle that delivers it.*

During the pairing ceremony SDL grabs the Wii Remote mid-pairing. Then `BluetoothSetServiceState` and the rest of the pairing churn invalidate that handle, so the SDL joystick drops and SDL keeps a stale device that only a full app restart clears. `RescanWiiControllers` (line 906) replicates the restart for just that one driver:

```csharp
for (int i = 0; i < 8 && !_disposed; i++)
{
    SDL_SetHint(SDL_HINT_JOYSTICK_HIDAPI_WII, "0");
    Thread.Sleep(200);
    SDL_SetHint(SDL_HINT_JOYSTICK_HIDAPI_WII, "1");
    Thread.Sleep(1200);
}
```

Setting the hint to `0` runs `SDL_HIDAPIDriverHintChanged`, which disables the driver. SDL cleans up the stale device, closes the dead handle, and resets its hidapi change count to force a re-enumerate. Setting the hint back to `1` re-opens and re-inits the now-stable device. The toggle repeats eight times over about 11 seconds (`(200 + 1200) * 8`) to cover the post-pair settling window, because the controller only connects on a button press that can come several seconds late.

The work runs on a background thread through `Task.Run` and checks `_disposed` each iteration. It is safe to call from any thread because `SDL_SetHint` is thread-safe. The actual driver re-scan happens on the UI thread: `MainWindow`'s `_sdlPumpTimer` fires `PumpSdlEvents` every 100 ms, and `PumpSdlEvents` runs `SDL_PumpEvents` then `SDL_UpdateJoysticks` on the `SDL_Init` thread, which is where SDL's hidapi posts its device-change messages and where a re-enumerate actually produces joysticks. So the background toggle changes the hint and the UI pump processes each change.

---

## SDL3-fork hidapi_wii fixes

*The `hidapi_wii` fixes the bundled `SDL3.dll` carries beyond the upstream driver. Non-exhaustive: the MotionPlus and D-pad fixes are catalogued elsewhere.*

Driving a Bluetooth Wii controller on Windows 8 and later relies on several fixes in PadForge's SDL3 fork, all shipped in the bundled `SDL3.dll`. These three cover pairing and connect stability:

1. **Bluetooth `hid_write` fallback.** A Wii Remote's output reports must go through `HidD_SetOutputReport`, because the Microsoft Bluetooth stack rejects `WriteFile` for an output length at or under 512 bytes (a Wiimote report is 22). The fork keeps the `WriteFile` path and adds a `HidD_SetOutputReport` fallback when `WriteFile` returns error 87 (`ERROR_INVALID_PARAMETER`). This is `hifihedgehog/SDL#2`, referenced in the `InitializeSdl` comment.
2. **Connect-timeout seed.** `m_ulLastInput` is seeded with `SDL_GetTicks()` in the device's `InitDevice`. Without it, a freshly-paired remote is disconnected after the app's first three-second input timeout before it has sent anything.
3. **Extension hot-plug.** `UpdateDevice` re-identifies the controller when a Nunchuk or other extension is attached or detached, so the form change is picked up and the device re-added without a restart.

A fourth fix feeds the IR pointer above: the driver posts the two IR dots on dedicated joystick axes 6-9 (`hifihedgehog/SDL#6` follow-up `41909fdc4e`), separate from the gamepad sticks so an extension keeps axes 0-3. Further fork fixes handle MotionPlus and D-pad mapping (the MotionPlus identify dead-window, the ~8s MotionPlus presence-churn loop, bare-D-pad POV-hat mapping, IR + MotionPlus coexistence). Those bear on gyro and hat mapping rather than the read path here, so their detail lives on [Gyro](../guides/gyro.md) and in the read-only SDL3 fork.

These live in the SDL3 fork and are read-only from PadForge's side. See [SDL3 Integration](sdl3-integration.md).

---

## Related pages

- [Wii Controllers](../devices/wii-controllers.md): the user guide for this feature.
- [Input Pipeline](input-pipeline.md): the six-step pipeline that maps the controller once SDL surfaces it.
- [SDL3 Integration](sdl3-integration.md): the `hidapi_wii` driver, the fork fixes, and the axis capability gate.
- [Devices](../features/devices.md): the Pair button and the paired controller's device card.
- [Gyro](../guides/gyro.md): the Wii Remote's accelerometer and Motion Plus path.
- [Controller Audio Internals](controller-audio-internals.md): the shared sink model the Wii Remote speaker follows, and the HD-haptic tone path.
- [Driver Management](../features/driver-management.md): HIDMaestro and HidHide setup.

---

*Last updated for PadForge 4.0.0.*
