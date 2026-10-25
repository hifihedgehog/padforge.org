# Game Mods Internals

*How PadForge takes the UDP packets DSX game mods send, turns them into trigger programs, lights and thresholds, decides which virtual controller each reaches, and ends them when the mod's program does.*

For the user-facing side see [Game Mods](../features/game-mods.md).

| File | Responsibility |
| --- | --- |
| `PadForge.App/Common/Input/GameModProtocol.cs` | The packet parser, the trigger encoder, the light mappings and the reply. Pure, with no socket or controller. |
| `PadForge.App/Common/Input/GameModEffects.cs` | What the mods hold by controller index, each value with its sender, the controller order and the release paths. |
| `PadForge.App/Common/Input/GameModSender.cs` | One sending program, found by the UDP port it sends from, and its exit watch. |
| `PadForge.App/Services/GameModServer.cs` | The socket, the receive thread, the reply, the sender watch and the status line, with the reply's device list (`GameModStatusDevices`). |
| `PadForge.App/Services/GameModPortFiles.cs` | The two files mods read their port from. |
| `PadForge.App/Services/DsxStandIn.cs` | The DSX.exe stand-in: extracting it, starting it and the job object that ends it. |
| `PadForge.DsxStandIn/Program.cs` | The stand-in itself, a .NET Framework program that waits for PadForge to exit. |
| `PadForge.App/Services/InputService.GameMods.cs` | Start and stop with the engine and the Dashboard switches, the status line, the pad page lines and the Devices line. |
| `PadForge.App/Common/Input/UserEffectsDispatcher.cs` | Where a mod's hold meets the Sony effects pass: `FillFromModHold`, `ModHoldEnded`, `NotifyModEffectsChanged` and the `TryGetInboundTriggerEffects` fallback. |
| `PadForge.App/Common/Input/InputManager.Step5.VirtualDevices.cs` | The trigger threshold, on the hand-off to the virtual controller, for the gamepad state and the raw surface. |

DSX is closed source. The protocol comes from the official DSX v3.1+ mod example (Paliverse/DSX, `Mod System (DSX v3)/Mod System (DSX v3.1+)/DSX_UDP_Example`), the v2 example in Paliverse/DualSenseX, and the open servers that speak it: DualSenseY in both versions, DSZ and the hbashton fork of DS4Windows. Where they disagree, the code names its choice and its source.

---

## The packet

A packet is JSON: `{"instructions":[{"type":1,"parameters":[0,2,13,0,8]}]}`. Each instruction has a type and a parameter list whose first entry is the controller index.

| Type | Name | Parameters after the index |
|---|---|---|
| 0 | GetDSXStatus | none. The reply goes out for every packet anyway. |
| 1 | TriggerUpdate | side (1 left, 2 right), mode, the mode's parameters |
| 2 | RGBUpdate | red, green, blue, and from v3 a brightness |
| 3 | PlayerLED | five lights on or off |
| 4 | TriggerThreshold | side, point 0 to 255 |
| 5 | MicLED | 0 on, 1 pulse, 2 off |
| 6 | PlayerLEDNewRevision | 0 to 4 for players 1 to 5, 5 for all off |
| 7 | ResetToUserSettings | none |

`GameModProtocol.Parse` reads packets as leniently as DSZ does, because mods built from different examples send different shapes. Keys match without regard to case, and a type may be a number or a name. A null or missing parameter list is empty: the v2 example's fixed-size instruction array sends `{"type":0,"parameters":null}` for every slot it leaves unused. A parameter may be a number (decimals truncate), a numeric string, or a boolean, which the PlayerLED instruction uses. Anything else reads as 0, which is also what DSX's own conversion gives a null. The v3.1 example's helper for custom trigger values writes its values one place early and leaves a null at the end, so a mod built on it sends that shape to DSX as well, and PadForge reads it the way DSX does. An instruction without a readable type is skipped and the rest of the packet applies.

## Trigger encodings

`GameModProtocol.TryEncodeTrigger` turns a mode and its parameters into the 11-byte block the DualSense takes per trigger: a mode byte and ten parameters. Out-of-range parameters, missing ones or an unknown mode return false and change nothing, the way Nielk1's generator leaves its buffer alone, so a mod's bad instruction keeps what it set before.

| Mode | Name | Encoding |
|---|---|---|
| 0, 20 | Normal, OFF | Nielk1's Off: 0x05 and zeros |
| 1-7, 9-11 | GameCube, VerySoft, Soft, Hard, VeryHard, Hardest, Rigid, Choppy, Medium, VibrateTriggerPulse | DualSenseY's bytes (`scePadCustomTriggers.cpp`) |
| 8 | VibrateTrigger | Nielk1's Vibration over the whole pull at amplitude 8, its parameter as the frequency, 10 when absent |
| 12 | CustomTriggerValue | the custom mode's byte, values 1 to 6 in bytes 1 to 6 and value 7 in byte 9 |
| 13, 21 | Resistance, FEEDBACK | Nielk1's Feedback (0x21): start 0-9, strength 0-8 |
| 14 | Bow | Nielk1's Bow (0x22) |
| 15 | Galloping | Nielk1's Galloping (0x23) |
| 16, 22 | SemiAutomaticGun, WEAPON | Nielk1's Weapon (0x25): start 2-7 |
| 17, 23 | AutomaticGun, VIBRATION | Nielk1's Vibration (0x26) |
| 18 | Machine | Nielk1's Machine (0x27) |
| 19 | VIBRATE_TRIGGER_10Hz | the VibrateTrigger encoding at 10 Hz |
| 24 | SLOPE_FEEDBACK | Nielk1's SlopeFeedback, rounded to even as C#'s `Math.Round` rounds |
| 25 | MULTIPLE_POSITION_FEEDBACK | Nielk1's MultiplePositionFeedback |
| 26 | MULTIPLE_POSITION_VIBRATION | Nielk1's MultiplePositionVibration, the frequency first |

Three choices rest on more than one source:

- **VibrateTrigger's parameter is a frequency.** The v3.1 example says so ("Frequency: 0-255") and DSZ reads it so. DualSenseY ignores it.
- **The named presets are DualSenseY's bytes.** DSX never published them. DualSenseY's first, C# version carries them as packed 64-bit constants in `MainWindow.xaml.cs` beside a reply class with decompiler tokens, so they came from DSX's own code, and its current bytes keep their patterns. DSZ substitutes effects of its own and the DS4Windows fork refuses these modes.
- **The custom value's seventh number goes to byte 9.** The Wujek Dualsense API writes its seventh force at report byte 20 on USB, trigger byte 9 (`Controller.cs`), and the DS4Windows fork does the same. DualSense4Rockstar names that value `ab_actuationFrequency`, and byte 9 is where mode 0x26 reads its frequency. DualSenseY's current version and DSZ write it to byte 7, where the GTA IV mod's wheel speed would land in an unused byte.

The custom mode bytes are Off 0x00, Rigid 0x01, RigidA 0x21, RigidB 0x05, RigidAB 0x25, Pulse 0x02, PulseA 0x22, PulseB 0x06 and PulseAB 0x26, the A (0x20) and B (0x04) flags of the Wujek API, pydualsense and the DS4Windows fork. DualSenseY alone encodes the VibrateResistance and VibratePulse modes: 0x06, 0x26, 0x06, 0x26, then 0x27 for the four VibratePulse modes.

## Lights and thresholds

- RGBUpdate scales each color by the brightness over 255, as DSZ does.
- PlayerLED sets bits 0 to 4 from the five lights, left to right. PlayerLEDNewRevision maps to the patterns 0x04, 0x0A, 0x15, 0x1B and 0x1F, PadForge's own `PlayerLedBits`, and 0 for all off. PadForge adds the no-fade bit 0x20 to both, as it does for its own pips.
- MicLED's on, pulse and off are the report's 1, 2 and 0.
- TriggerThreshold holds a point on one trigger. `GameModEffects.ApplyThreshold` reports the trigger as 0 below the point and unchanged at or past it, DualSenseY's rule, with the point on the mods' 0-255 scale and the trigger on PadForge's 0-65535 one (point × 257). A point of 0 holds nothing.

## Holds

`GameModEffects` keeps one `Hold` per controller index: the two trigger blocks, the lightbar, the player lights, the mute light and the two thresholds, each with the `GameModSender` that set it. Holds never change once published. A change copies the array under a lock and publishes it, and readers take the published copy without a lock, since the polling thread reads the thresholds every cycle.

An instruction that sets a value already held changes nothing, so a mod that resends its state every frame, as the GTA V mods do, costs no writes. If a different sender sends the same value, it becomes the value's owner and nothing is written. An index below 0 means every controller, as in DSZ. A threshold of 0 holds nothing and has no owner.

### Which virtual controller an index reaches

`GameModEffects.OrderedSlots` lists the virtual controllers mods can reach: created and enabled, with an online DualSense, DualSense Edge or DualShock 4 assigned, in the order `SettingsManager.SlotOrders.GetGlobalSlotNumber` numbers them on the Dashboard. Index 0 is the first. It takes the devices lock and then the settings lock, never both at once, then the leaf slot-order lock, so the effects pass may call it under the devices lock in the documented order. The polling thread's readers, the threshold and the impulse translation, use `ForSlotCached`, which resolves the order at most every 250 ms.

### Releases

A hold's values end when:

- **The sender's process exits.** `GameModSender.Identify` finds the process that owns the sender's UDP port in the owner-PID UDP tables (`GetExtendedUdpTable`, IPv4 then IPv6, for a dual-mode socket), opens it with `SYNCHRONIZE` and keeps the handle, so the process id cannot pass to another program while it is watched. The receive loop wakes every 500 ms and `WatchSenders` releases every sender whose process has signaled. A sender whose process cannot be found lapses 15 seconds after its last packet, DualSenseY's `IsActive` window and the dispatcher's `ExternalClaimLapseMs`.
- **The mod sends ResetToUserSettings** for its index, which ends everything on that index whoever set it.
- **The user clicks Clear Mod Effects** on a controller's Devices panel, which resets every index that reaches a virtual controller the controller feeds.
- **The server stops**, with the switch, the port, the engine or PadForge.

A packet from a port whose sender has exited is identified anew, so a new program that reuses the port does not inherit the old one's values.

## The effects pass

`UserEffectsDispatcher.DispatchSnapshot` reads the slot's hold under the devices lock, beside `GetActiveOverrides`, so a release and a pass are ordered like everything else it writes. For each Sony pad, `FillFromModHold` places the hold into the per-device overrides wherever a game is not writing within its 1.5-second grace window: both triggers, the mute light and the player row on a DualSense, the lightbar on every Sony pad. The order is a game's own write, then the mod's hold, then PadForge's injected effects (the impulse-to-adaptive-trigger route and the steering cues, which fill only an empty slot), then the pad page's settings.

Two placements are deliberate:

- The fill runs after `ShouldAssertLightbar`. A mod's color counted as a game's would stand the pass down on a pass-through target and nothing would light, while a game driving the bar through the pass-through still owns it.
- `LightbarEverExternal` is left as the game left it, so when the hold ends PadForge's own color returns rather than the stand-down a game's write triggers.

The pad keeps a trigger program, a mute light or a player row until something overwrites it, and the pass leaves an idle subsystem unasserted (`GateMirroredSubsystem`), so a game's last program persists after the game stops writing. A mod's hold ends on purpose, so `ModHoldEnded` asserts each of those subsystems once more on the pass after a hold ends, carrying PadForge's own value: Off for a trigger or a mute light the pad page leaves unset.

A change to a hold calls `NotifyModEffectsChanged` for the slot it reaches. It queues one pass on the thread pool, since the caller is the receive thread and must answer the next packet without waiting on a HID write, and it keeps the slot's 30 Hz writer alive for two seconds (`ModChangeTimerMs`, a `HasTimerDemand` term), so a mod that changes its effects every frame is written at the pass's own rate. The lighting rows a slot lights take the hold's color through `LightPeripheral` where no game color is live, and a change requests their refresh through `GameLightbarCapture.NotifyChanged`.

`TryGetInboundTriggerEffects` hands `AtToImpulseTranslator` the mod's block for a trigger the game never wrote, so an Xbox controller with Translate Adaptive Trigger Vibrations plays a mod's vibrations on its impulse triggers.

## The threshold

Step 5 applies the held thresholds right before submit, after button SOCD, on a copy, so the pad page's preview and the impulse translation still read the real pull. Two paths carry it:

- **The gamepad state** of an Xbox or PlayStation slot. `ApplyThreshold` sets `LeftTrigger` or `RightTrigger` to 0 in Step 5's local `gpOut`, after Keep Controller Awake. The Sony packers derive the digital L2 and R2 bits from the analog value, so those follow.
- **The raw surface** of an Extended or Nintendo slot. `ApplyRawThresholds` copies the combined frame's axes into `_modRawAxesScratch` and rests the layout's first and second trigger axes (`CustomControllerLayout.IsTriggerSlot`, the pair `BuildRawHidState` hands HIDMaestro as the profile's named left and right triggers) at `short.MinValue` below their points. The Valve packer, `ExtendedReportPacker` and `SubmitRawHidState` all take that copy. A Valve persona's digital trigger bits derive from the analog value too. A Nintendo controller's ZL and ZR are buttons set in Step 3, which no threshold touches.

## The server

`GameModServer` follows `DsuMotionServer`: a UDP socket bound to 127.0.0.1, `SIO_UDP_CONNRESET` turned off so a mod that closes its socket cannot end the receive loop, a background receive thread with a 500 ms timeout for the sender watch, and an `OffLimitsForTest` fence on the default port. Datagrams from any address but loopback are dropped.

Every packet gets a reply at once, sent before the packet is applied, because the mods that wait for one block on `Receive` with no timeout. The reply carries DSX's fields and casing: `Status` ("DSX Received UDP Instructions", DSX's own text), `TimeReceived`, `isControllerConnected`, `BatteryLevel`, and the v3 `Devices` list. `GameModStatusDevices` builds that list at most every 250 ms: one entry per controller index, describing the first online Sony pad on that virtual controller, with DSX's `DeviceType` (0 DualSense, 1 Edge, 2 and 3 DualShock 4 v1 and v2, 4 the wireless adapter) and `ConnectionType` (0 USB, 1 Bluetooth, 2 the adapter).

The Dashboard line comes from `GameModServer.FormatStatus`: why the server is not listening, or the last sender's program and the Dashboard number of the virtual controller its index reaches.

### Port files

`GameModPortFiles.Write` runs on a worker after each successful bind and leaves both files alone while a process named DSX runs that is not the stand-in (`RunningProcessList`, the app's one process walk):

- `C:\Temp\DualSenseX\DualSenseX_PortNumber.txt`, which v2 mods read, is created when missing and rewritten when it names another port. Some of those mods stop without it.
- `%LOCALAPPDATA%\DSX\DSX_UDP_PortNumber.txt`, which v3.1 mods read and fall back to 6969 without, is rewritten when it names another port and created only for a port other than 6969.

### The stand-in

`DsxStandIn` writes the embedded `PadForge.DsxStandIn.exe` resource to `%TEMP%\PadForge_DSX\DSX.exe` unless the same bytes are already there, and starts it with PadForge's process id. The stand-in is a separate .NET Framework 4.6.2 project of a few kilobytes, since a renamed copy of PadForge's single-file executable would extract its whole native bundle again under the new name. It waits on its parent and exits, and PadForge also places it in a job object with kill-on-close, so it ends however PadForge ends. It starts after the bind and stops before the socket closes, so a mod that sees a DSX process always gets its reply. The start goes through `ShellLaunch.Start`, the fenced `Process.Start`.

---

## Tests

`GameModTests` replays the packets of the mods DSZ's tests capture, checks every encoding against Nielk1's formulas and the chosen tables, the lights, the holds and their owners, the releases, the controller order, the dispatcher's fill and its order in the pass, the threshold, the server over a real loopback socket, sender identification against the test's own socket, the port-file rule on temporary paths, and the stand-in, which the test extracts and runs. The default port and the real port files are fenced in the test host (`GameModPortOffLimits`, `GameModPortFilesOffLimits`).

---

*Last updated for PadForge 5.1.0.*
