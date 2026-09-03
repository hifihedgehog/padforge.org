# Handheld PC Buttons: Internals

*How a paddle nobody can see becomes a button: the three delivery paths, the learners, the firmware gate, and the row that carries them.*

The user-facing page is [Handheld PC Buttons](../features/handheld-buttons.md). This one is for whoever has to change the code.

There is no per-model table anywhere in this feature. A learned button is data, and a wrong layout is a data fix.

| File | Role |
|---|---|
| `PadForge.App/Common/Input/HandheldButtonsDevice.cs` | The Hidden Buttons row: state, readers, WMI matching, learn hand-off |
| `PadForge.App/Common/Input/HandheldButtonRegistry.cs` | Persisted entries, stable indices, the feature and capture flags |
| `PadForge.App/Common/Input/HandheldLearnSession.cs` | One learn pass: three phases, buckets, `Finish` |
| `PadForge.Engine/Common/HandheldChords.cs` | `HandheldChordEngine`, the pure key-combination state machine |
| `PadForge.App/Common/Input/HandheldChordRuntime.cs` | Hosts the engine, runs the replay worker |
| `PadForge.Engine/Common/InputHookManager.cs` | The low-level hooks, `ChordSwallows`, `InjectReplay`, `InjectWinMask` |
| `PadForge.Engine/Common/VendorReportLearner.cs` | `NoiseMask`, `FindBits`, `FindValues`, `Learn`, and `VendorButtonDefinition` |
| `PadForge.App/Common/Input/VendorHidRuntime.cs` | Vendor collection enumeration and `VendorHidReader` |
| `PadForge.App/Common/Input/WmiEventRuntime.cs` | WMI event subscriptions behind the firmware gate |
| `PadForge.App/Common/Input/AcpiWmi.cs` | `_WDG` parser over the DSDT and SSDT |
| `PadForge.App/Common/Input/SystemMotionDevice.cs` | The Motion row over `Windows.Devices.Sensors` |
| `PadForge.App/Common/Input/HandheldDaemonWatch.cs` | The vendor daemon scan |
| `PadForge.App/Common/Input/HandheldKeyNames.cs` | Source descriptions for the preview and the dialog |
| `PadForge.Engine/Common/MachineIdentity.cs` | The DMI identity |
| `PadForge.App/Views/LearnHandheldButtonDialog.xaml.cs` | The dialog, export, import |
| `PadForge.App/Common/Input/InputManager.Step1.UpdateDevices.cs` | Phase 1h: `UpdateHandheldDevices`, `HandheldSweep`, `RetireHandheldRows`, `ShutdownHandheldInputs` |
| `tools/WdgProbe/Program.cs` | Runs the WMI learner path outside the app |

---

## Lifecycle: Phase 1h

`UpdateHandheldDevices` runs on the poll thread inside Step 1. With `HandheldButtonRegistry.FeatureEnabled` false and nothing to retire, it returns after two volatile reads. Turning the feature off retires both rows, neutralizes their mapped outputs, and stops the chord worker (`HandheldChordRuntime.Stop`) outside the handheld lock, since `Stop` joins its worker and the poll thread must not block on a join under a nested lock.

The button row opens on the poll thread with no I/O (`HandheldButtonsDevice.Open` only wires events and pushes the registry). Everything that blocks lives in `HandheldSweep`, a worker task every `_handheldSweepIntervalMs` = 4000 ms:

1. `HandheldDaemonWatch.Refresh` scans the process list (3 ms measured across 335 processes).
2. `VendorHidRuntime.Enumerate` lists vendor collections and `SyncReaders` opens or closes readers.
3. `SyncWmi` subscribes the wanted WMI classes.
4. Once, `SystemMotionDevice.IsAvailable` probes for a gyrometer and opens the Motion row, which the next poll registers from `_systemMotionPending`.

A row the user removes from the Devices page is recreated on the next poll (the NFC recreate pattern). `ShutdownHandheldInputs` runs in the same teardown window as the NFC, microphone, and headset shutdowns.

---

## Identity

`MachineIdentity.Read` reads `HKLM\HARDWARE\DESCRIPTION\System\BIOS`: `SystemManufacturer`, `SystemProductName`, `SystemFamily`, `BaseBoardProduct`, `SystemSKU`. No WMI, so the poll side never pays a COM round trip.

| Member | Value |
|---|---|
| `Key` | `MANUFACTURER|PRODUCTNAME`, trimmed and upper-cased |
| `DisplayName` | Family when the product name is empty or a bare model code (12 characters or fewer, no spaces, letters and digits mixed, such as `83RU`), product name otherwise, `This PC` when both are empty |

The row identity follows from the key:

| Row | `DevicePath` | `InstanceGuid` | VID:PID | `InputDeviceType` |
|---|---|---|---|---|
| Hidden Buttons | `handheld://<key lower-cased>` | MD5 of `pfhandheld:<key>` | `4850:4842` ("HP", "HB") | `HandheldButtons` = 32 |
| Motion | `sensor://motion` | MD5 of `pfsysmotion:<key>` | `5359:4D4F` ("SY", "MO") | `SystemMotion` = 33 |

The registry stamps `MachineKey` when the first button is learned. Definitions still apply on a different machine of the same model, which is what export and import rely on.

---

## The registry and the stable index

`HandheldButtonRegistry.Entry` carries whichever paths the press produced, and one entry can carry more than one:

| Field | Path |
|---|---|
| `Keys` | Chord: VK codes 0 to 255, or `0x1000` + button id for mouse buttons (0 left, 1 middle, 2 right, 3 X1, 4 X2). Modifiers are stored as the left and right specific codes the hook reports (`0xA0` to `0xA5`, `0x5B`, `0x5C`), never the generic `0x10`, `0x11`, `0x12`. |
| `Collection`, `ReportId`, `ByteIndex`, `Mask`, `Value`, `ValueKind` | Report field. `Collection` is `VID:PID:PAGE:USAGE`. `ByteIndex` counts the report id byte at index 0. |
| `WmiClass`, `WmiProperty`, `WmiValue` | WMI event, value as invariant text |

`Register` assigns the lowest free button index (from 0, there is no "any" button on this row) unless the entry already carries a free one, which is how import keeps indices. `Remove` never renumbers survivors. `LoadRegistry` honors stored indices and reassigns collisions. Names are deduplicated with ` (2)`, ` (3)` suffixes.

Persistence is `AppSettingsData.HandheldButtons`, an array of `HandheldButtonData` with every field as an XML attribute (`Keys` is comma-joined), plus `HandheldMachineKey` and `HandheldButtonsEnabled`. The registry loads before the toggle. The export file is the same DTO under `{"padforgeHandheldButtons": 1, "machine": "...", "buttons": [...]}`.

Two flags on the registry drive the hooks: `FeatureEnabled` (the Settings toggle) and `LearnCaptureActive` (the dialog is open). Either flipping raises `ActivityChanged`, which sends `InputService.ApplyDeviceHiding` back through `ApplyInputHooks`, where `HandheldChordRuntime.NeedsHooks` is the one extra term beside the suppression sets. The hooks stay installed with nothing to suppress while a chord is defined or a capture is armed, and come down when neither holds.

---

## Path one: key combinations

`HandheldChordEngine` is pure. Both low-level hooks feed every key and mouse-button event through `InputHookManager.ChordSwallows`, which calls `engine.OnEvent(code, down, now)` and swallows or passes on its answer. The rules, each locked by a test in `HandheldChordEngineTests`:

| Rule | Constant |
|---|---|
| A key in no chord passes untouched and ends any prefix in flight (the held keys replay first) | |
| Modifiers are never held back on the way down | |
| A non-modifier key that is a strict prefix of a chord is swallowed and held. If the chord completes, the held keys are consumed. If not, they replay in order. | `HoldMs` = 100 |
| A prefix is judged in the learned order, so D alone is typing for a Win+D chord | |
| Completion swallows the completing key and asserts the button. The longest completing chord wins when two complete at once. | |
| The button releases when any key of the chord goes up. Ups of consumed keys are swallowed. | |
| A completed chord containing Win or Alt sets `WinMaskRequested` | mask key VK `0xFF` |
| Auto-repeat of a key keeps the first decision | |
| Capture mode swallows everything and reports the set of codes pressed once all are released. An up whose down it never saw passes (the Enter that clicked Start). Idle capture ends empty. | `CaptureIdleTimeoutMs` = 10000 |
| `SetChords` releases a button whose definition vanished or changed, with the event. `Reset` (hooks detached) releases everything and forgets held prefixes. | |

Injection happens in two places. Event-driven replays and the mask key are injected inside the hook callback, before it returns, so a replayed prefix precedes the foreign key that ended it and the mask lands while Win is still physically down. `HandheldChordRuntime`'s worker handles only timed work, ticking every 10 ms while `HasPendingWork` (hold expiry, capture idle). Every injected event carries `ReplayTag` = `0x50464843` ("PFHC") in `dwExtraInfo`, AutoHotkey's KEY_IGNORE technique, and re-enters the hook without reaching the engine. Events from other software carrying `LLKHF_INJECTED` or `LLMHF_INJECTED` bypass the engine too.

The device turns `ButtonChanged` into `_chordDown[button]` plus a pulse.

---

## Path two: vendor HID reports

`VendorHidRuntime.Enumerate` walks every present HID interface and keeps the ones whose top-level usage page is `0xFF00` or higher with a nonzero input report length. The probe opens with no access rights, so a collection another program holds exclusively is still listed and named. Verdicts are cached per interface path until the path disappears. The collection key is `VID:PID:PAGE:USAGE`, stable across reboots and between two machines of one model, unlike the interface path.

`VendorHidReader` opens `GENERIC_READ` with both share flags and reads overlapped on its own thread (`PadForge.VendorHid`), the headset reader's shape: bounded 100 ms waits, `CancelIoEx` on teardown, a 2 s join, and a leaked handle rather than a free under a stuck native call.

`HandheldButtonsDevice.SyncReaders` keeps open exactly `RequiredCollections` (the collections learned entries name), or every present collection while `LearnCaptureActive`. A collection that fails to open logs once, not once per sweep. The dialog calls `SyncReadersNow` so it does not wait out the sweep cadence.

`OnReport` evaluates each definition for the report's collection. A definition for another report id says nothing about this report and leaves its state alone.

| Kind | Evaluate | Release |
|---|---|---|
| `Bit` | `(byte & Mask) == (Value & Mask)`, so an active-low bit learns its pressed pattern and evaluates pressed when clear | The report reads the idle pattern again |
| `Value` | `byte == Value` | `ValueHoldMs` = 150 after the last matching report |

---

## Path three: WMI events

`WmiEventRuntime` subscribes `SELECT * FROM <class>` in `root\WMI` through `ManagementEventWatcher`. `Sync(wanted)` drops watchers no longer wanted and starts the rest. Outside a capture the wanted set is `RequiredWmiClasses`. During one it is every class `EnumerateEventClasses` returns. An event's data properties arrive as invariant strings with `SECURITY_DESCRIPTOR`, `TIME_CREATED`, `InstanceName`, and `Active` stripped, and `OnWmiEvent` on the device pulses the button whose `(class, property, value)` matches.

### The firmware gate

Subscribing every `WmiEvent` subclass on the bench machine bug-checked it (0x44, `MULTIPLE_IRP_COMPLETE_REQUESTS`, a miniport double-completing the enable IRP). A user-mode subscription to a kernel driver's WMI class can crash the kernel, and the culprit class was unrecoverable from the dump. The gate is therefore the mechanism, never a vendor allowlist: firmware hotkeys reach Windows through the ACPI-WMI mapper (`ACPI\PNP0C14`), and the firmware's `_WDG` object lists every GUID it serves.

`AcpiWmi.ReadBlocks` reads the DSDT and the first SSDT through `GetSystemFirmwareTable` and scans for `_WDG` followed by `BufferOp` (`0x11`). Each 20-byte block (Linux `drivers/platform/x86/wmi.c`, `struct guid_block`) is a 16-byte GUID, a notify id, a reserved byte, an instance count, and flags, where `0x08` marks an event. `EnumerateEventClasses` keeps only `WmiEvent` subclasses whose `guid` qualifier appears in that set, caches a non-empty answer for 60 s, and `Sync` applies the gate to every class it is about to start, so a class named by a hand-edited `PadForge.xml` or an imported set is refused the same way. Refusals are remembered until `StopAll`.

Two facts about the read. `GetSystemFirmwareTable` returns the first table with a given signature, so every SSDT collapses to one read and a `_WDG` in a later SSDT is unreachable. That fails closed: no event GUIDs, no class watched. And the buffer contents are bounded by the enclosing `PkgLength`, or a declared `BufferSize` larger than its package would read adjacent AML as blocks.

`tools/WdgProbe <seconds>` prints the `_WDG` table, the classes that pass the gate, and every event for the given number of seconds, using the app's own code.

---

## The learners

`HandheldLearnSession` runs three timed phases (`IdleMs` = 1000, `PressMs` = 3000, `ReleaseMs` = 1000) driven by the dialog's timer. Reports from every open reader are bucketed by `(collection, report id)` per phase, up to 256 samples per bucket, and WMI events per phase in arrival order. The chord engine's capture runs alongside and lands in `ChordKeys`. `Finish` produces candidates:

**WMI first.** A `(class, property, value)` seen during the press or the release is a candidate unless it appeared two or more times while idle. One idle copy is an early press. Press-window events list before release-window ones, and arrival order is candidate order (on the Legion Pro 7 the utility event that names the key lands 3 ms before the lighting side event both keys share).

**Reports next**, per bucket that received a press sample, with the baseline chosen in this order: the first idle sample with `NoiseMask` over all idle samples, else the last report seen before the press (an event-style collection that is silent while idle), else all zeros. A candidate at byte 0 is the report id flipping between layouts and is dropped.

`VendorReportLearner` is pure over byte arrays:

| Function | Rule |
|---|---|
| `NoiseMask(idle)` | Bit set wherever any idle sample disagreed with the first. Unequal lengths compare over the shorter prefix, tail volatile. |
| `MinPressRun(n)` | `max(min(2, n), n / 40)`: a run of 2.5% of the press samples, never fewer than two when two exist, a single sample its own run |
| `FindBits` | Outside the mask, a bit that reads the opposite of idle for a run of at least `MinPressRun` press samples and is back at idle in the last sample seen (last release sample, else last press sample). A hold and a tap both qualify. One candidate per byte, `Value` = the pressed pattern (idle inverted under the mask). |
| `FindValues` | Outside the mask, a byte whose first differing press sample carries a value no release sample carries. A single-bit difference is left to `FindBits`. |
| `Learn` | `FindBits` first. A bit candidate whose mask has more than one bit set is a code, not a flag (the ROG Ally writes 166 for one button and 167 for its neighbor, and a mask match on `0xA6` would fire on both), so it becomes a `Value` candidate with the exact byte. `FindValues` only when no bit was found. |

More than one candidate means the press changed several things (two buttons, or a byte plus its mirror). The dialog lists them and the user picks, or presses again.

---

## The row's state

`HandheldButtonsDevice.GetCurrentState` runs on the poll thread under the state lock and writes every button every poll, true or false, so a released button produces its falling edge. A button reads pressed while any of these holds:

| Source | Held while |
|---|---|
| `_chordDown[b]` | The chord is active in the engine |
| `_reportDown[b]` | The last matching report read the pressed pattern (Bit kind) |
| `_pulseUntil[b]` | `PulseMs` = 175 after a chord down, a Bit rising edge, or a WMI match |
| `_valueUntil[b]` | `ValueHoldMs` = 150 after the last matching Value report |

`NumButtons` spans the range of indices in use, `1 + MaxButtonInUse`, not the count, so a removed middle entry leaves a gap instead of renumbering. `GetDeviceObjects` lists each entry as a `PushButton` at its stable `InputIndex`, which is what the picker shows. `ApplyRegistry` on every registry change rebuilds the frozen definition maps and clears the state of any index no longer defined.

---

## The Motion row

`SystemMotionDevice` subscribes `Gyrometer.GetDefault()` and `Accelerometer.GetDefault()` at their minimum report interval and publishes under a lock, the headset motion device's shape without its stale window.

| Sensor | Conversion |
|---|---|
| Gyrometer, degrees per second | × π/180, identity axes |
| Accelerometer, g | negated and × 9.80665. Windows reports the gravity direction (a face-up device at rest reads −1 g on Z), SDL reports the reaction (+9.8 on the up axis). |

The frame is the identity map: Windows X toward the screen's right edge, Y toward its top, Z out of the screen, which for a handheld held facing the player is SDL's X right, Y up, Z toward the player. `Unsubscribe` hands the report interval back (0 = the driver's default) off the caller's thread, since Dispose reaches it from the poll thread and the property write is a WinRT call.

---

## The daemon scan

`HandheldDaemonWatch.Names` lists process image names as the vendors ship them: `LegionSpace`, `LSDaemon`, `LegionGoQuickSettings`, `ArmouryCrate` and its service, socket server, and session helper, `MSI_Center_M_Server`, `MSI Center M`, `MCMOSDInfo`, `MSI Center OSD Info`, `ZotacHandheldQuickSetting`, `AYASpace`. `Running` is the comma-joined sorted set, refreshed on the sweep cadence, shown on the Devices row and in the dialog.

---

## Diagnostics lines

All through `SdlDiagLog`, so they ride the diagnostics mirror.

| Line | When |
|---|---|
| `Handheld: reading vendor collection <key> (<name>), <n>-byte reports` | A reader opened |
| `Handheld: could not open vendor collection <key> (<name>)` | Open failed, once per collection |
| `Handheld: firmware declares <n> ACPI-WMI event GUIDs, <m> event classes match` | The gate enumerated |
| `Handheld: firmware declares no ACPI-WMI event GUIDs; no WMI class is watched` | Empty `_WDG` read |
| `Handheld: refusing to watch WMI class <cls>, the firmware does not declare its GUID as an ACPI-WMI event` | A named class failed the gate |
| `Handheld: watching WMI event class <cls>` | A watcher started |
| `Handheld: cannot watch WMI class <cls>: <message>` | Subscription threw |
| `Handheld: stopped watching <n> WMI event classes; still watching <list>` | Watchers dropped |
| `Handheld: WMI event <cls> <prop>=<value> ...` | Every event received |
| `Handheld: WMI event <cls> pulses button <n> (span <s>, attached <bool>)` | A match |
| `Handheld: WMI event <cls> matched no value on its <n> learned button(s)` | Class known, value not |
| `Handheld: WMI event <cls> matches no learned button` | Class unknown |
| `Handheld learn: watched <c> collections, <w> WMI classes; reports idle/press/release a/b/c, events d/e/f, chord <keys>, candidates <n>` | A learn pass finished |
| `Handheld chords: worker error <message>` | SendInput failed in the worker |
| `System motion: gyrometer at <n> ms, accelerometer present/absent` | The Motion row opened |
| `System motion: sample #<n> gyro=(...) accel=(...)` | Samples 1, 2, 4, ... 64, then every 4096th |

---

## Tests

`HandheldChordEngineTests` (36) replays the engine rules with a fake clock. `HandheldButtonsTests` (33) covers the registry, the device state (minimum press, value hold, other report ids, two bits in one byte, span growth), the WMI pulse and the pinned Step 3 path, the learners over Legion-style, active-low, Ally-style, and GPD Win 5 fixtures, the WMI candidate rules, the motion conversions, and the `_WDG` parser over a synthetic table.

---

## Evidence status

The WMI path has run on real hardware: a Lenovo Legion Pro 7 learned its Vantage (`LENOVO_UTILITY_EVENT`, `PressTypeDataVal` = 72, fires on press) and Smart Connect (value 1, fires only on a short tap) keys and triggered their mapped outputs. The chord and report paths have no handheld bench yet. Their contracts are the replay tests, built from byte-for-byte agreements between Handheld Companion and InputPlumber on the same hardware (Legion Go byte 20 paddle bits, the Ally `0x5A` key-code byte, the OneXPlayer frame). Where those two references disagreed on a layout, which happened fifteen times, a table would have shipped one of them wrong, and that is why there is no table.

---

## Related

- [Handheld PC Buttons](../features/handheld-buttons.md) for the user-facing page
- [Input Pipeline](input-pipeline.md) for where Phase 1h sits
- [Settings and Serialization](settings-and-serialization.md) for `AppSettingsData`

---

*Last updated for PadForge 4.4.0.*
