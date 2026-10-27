# Game Telemetry Internals

*How PadForge reads the telemetry driving games send, turns each packet into one frame, shows the frame as the Game Telemetry row, hands it to Custom Expression triggers and the wheel RPM lights, and how the Adaptive Trigger Effect macro action reaches a DualSense.*

For the user-facing side see [Game Telemetry](../features/game-telemetry.md).

| File | Responsibility |
| --- | --- |
| `PadForge.App/Common/Input/Telemetry/TelemetryFrame.cs` | `GameTelemetryFormat` (the Game list, saved), `TelemetrySource` (who sent the frame) and `TelemetryFrame`, one decoded packet in common units. |
| `PadForge.App/Common/Input/Telemetry/TelemetryDecoders.cs` | One pure decoder per game family. No socket, no clock. |
| `PadForge.App/Common/Input/Telemetry/TelemetryReader.cs` | The format choice: a picked game, or Auto-Detect with its hold. The max RPM fallback. |
| `PadForge.App/Common/Input/Telemetry/KunosSharedMemory.cs` | Assetto Corsa's three shared memory pages, opened read-only. |
| `PadForge.App/Common/Input/Telemetry/CustomTelemetryFormat.cs` | The user's formats as saved, and `CompiledTelemetryFormat`, which reads them. |
| `PadForge.App/Common/Input/Telemetry/GameTelemetryRuntime.cs` | The Dashboard mirror the engine reads, the values Custom Expression variables read, and the engine values the wheel lights read. `TelemetryChannel` lives here. |
| `PadForge.App/Common/Input/Telemetry/GameTelemetryDevice.cs` | The row: the socket, the forward socket, the shared memory poll, the axes and buttons, silence, the status. |
| `PadForge.App/Common/Input/InputManager.GameTelemetry.cs` | Step 1 phase 1i2: open, retire, recreate and reopen the row. |
| `PadForge.App/Common/Telemetry/GameTelemetryRowSource.cs` | The row as the first source of the wheel lights' `TelemetryHub`. |
| `PadForge.App/Services/InputService.GameTelemetry.cs` | The Dashboard status line and flame, and the Devices panel line. |
| `PadForge.App/ViewModels/CustomTelemetryFormatEditor.cs`, `Views/CustomTelemetryFormatsDialog.xaml(.cs)` | The custom format window, which edits copies and writes the list back on Save. |
| `PadForge.App/ViewModels/TelemetryChannelOptions.cs` | The channel picker of a Custom Expression variable. |
| `PadForge.App/ViewModels/TriggerEffectCatalog.cs` | The Adaptive Trigger Effect action's effects, their parameters and ranges. |
| `PadForge.App/Common/Input/MacroTriggerEffects.cs` | `MacroTriggerEffectState`, the effects macros hold, one store per slot. |

The layouts come from the projects credited on the About page under Racing telemetry references, each cloned and read at a pinned commit. Where they disagree, the decoder's comment names its choice.

---

## The frame

Every decoder fills one `TelemetryFrame`:

| Field | Unit |
|---|---|
| `SpeedMs` | Meters per second, never negative |
| `Rpm`, `MaxRpm` | Revolutions per minute |
| `Gear` | -1 reverse, 0 neutral, 1 and up |
| `Throttle`, `Brake`, `Clutch`, `Handbrake` | 0 to 1 |
| `Steering` | -1 full left to 1 full right |
| `Driving`, `DrivingReported` | Whether the game says it is driving, and whether it says anything |
| `Variables` | The custom variables, by their index in the global list |

`Clamp` holds the pedals to 0 to 1 and the steering to -1 to 1, and turns a NaN or an infinity into 0, so a game that overshoots cannot push an axis past its end.

## The decoders

Little-endian throughout, offsets in bytes.

| Format | Packets | Fields |
|---|---|---|
| Forza | 232 (Sled), 311 (Motorsport 7 Dash), 331 (Motorsport 2023 Dash), 323 or 324 (Horizon) | IsRaceOn s32 at 0, max RPM f32 at 8, RPM at 16. From the Dash on, with a shift of 12 for Horizon: speed f32 at 244, throttle, brake, clutch, handbrake u8 at 303 to 306, gear u8 at 307 (0 reverse, 11 neutral), steer s8 at 308. A Sled packet takes its speed from the velocity vector at 32, 36 and 40. |
| F1 22 to F1 25 | The packet format u16 at 0, 2022 to 2025, and one of that format's sizes for the packet id: twelve for 2022, fourteen for 2023, fifteen for 2024 and sixteen for 2025, from vAzhure F12022.cs to F12025.cs. Format 2022: a 24-byte header, packet id at 5, player car at 22. Format 2023 on: a 29-byte header with the game's year less 2000 at 2, packet id at 6, player car at 27. The layout follows the format alone, so F1 24 or F1 25 on an older format reads too. The status line names the game by the year at 2 when it is not 0, and by the format otherwise. | Car Telemetry (id 6), 60-byte entries: speed u16 km/h, throttle +2, steer +6, brake +10, clutch u8 +14 (0 to 100), gear s8 +15, RPM u16 +16. Car Status (id 7), 47-byte entries in F1 22 and 55 later: max RPM u16 +17. |
| Codemasters | 264 or 280 | Speed f32 at 28, throttle 116, steer 120, brake 124, clutch 128, gear 132 (-1 and 10 reverse), RPM 148 and max RPM 252 in tenths. |
| EA SPORTS WRC | 237, 240 with a 3-byte pad after byte 36, 241 or 244 with a 4-byte `packet_4cc` header | Gear index at 37 with the neutral and reverse indexes at 38 and 39, speed 41, max RPM 185, RPM 193, throttle 197, brake 201, clutch 205, steering 209, handbrake 213. |
| OutGauge | 92, or 96 with an OutGauge ID | Car name at 4 (`beam` is BeamNG.drive), gear u8 at 10 (0 reverse, 1 neutral), speed 12, RPM 16, the dash lights u32 at 44 (mask 4 is the handbrake), throttle 48, brake 52, clutch 56. |
| Project CARS 2 | Telemetry (type 0 at byte 10), 559 bytes. Game State (type 4), 24 bytes. | Brake, throttle, clutch u8 at 29 to 31, speed f32 at 36, RPM u16 40, max RPM u16 42, steering s8 44, gear in the low nibble of 45 (15 reverse), handbrake u8 at 370. Game State: byte 14 and 7, 2 while playing. |
| Assetto Corsa | Shared memory | Physics: gas 4, brake 8, gear s32 16 (0 reverse, 1 neutral), RPM 20, steer 24, speed km/h 28, clutch as 1 less the value at 364. Static: `smVersion` UTF-16 at 0, 1.8 or later is ACC, max RPM s32 at 412. Graphics: status at 4, 2 while live. |
| ETS2 and ATS | One JSON object per change from MrHokss's plugin | `speed` (absolute), `rpm`, `gear` (negative is reverse), `steer` (counterclockwise, so negated), `throttle`, `brake`, `clutch`. |

F1 claims every packet with its format, a known id and that id's size, read or not, so format 2024's 237-byte Motion Ex packet never reaches the EA SPORTS WRC rule.

## Auto-Detect

`TelemetryReader` tries, in order: the custom formats that name a length or a key, JSON (the truck plugin), F1, Project CARS 2, OutGauge, EA SPORTS WRC, Codemasters, Forza. Formats with a signature come ahead of formats known only by their length.

Once a format sends a frame it holds. Another format takes over after `ChallengerFrames` (3) frames in a row, or after `HoldReleaseMs` (1000) with no frame from the held one. A game with no max RPM gets the highest RPM seen since that format started sending, tm-bt-led's `detectedMaxRpm`, and the frame sets `MaxRpmLearned`. tm-bt-led starts its peak at 5000, which would hold a truck governed near 2,500 RPM to half scale, so this one starts at 0.

## Assetto Corsa's shared memory

`KunosSharedMemory` opens `Local\acpmf_physics`, `Local\acpmf_static` and `Local\acpmf_graphics` with `OpenExisting` and read access, vAzhure's `GameListener` pattern, so PadForge never creates a game's mapping. A failed open retries after `RetryMs` (2000). The first read is a baseline, the FreeTrack reader's rule, and a frame counts only while the physics `packetId` moves. A page that stops moving for `StaleMs` (5000) is closed, so a game that exits lets its mapping go. The pages are read on the poll thread in the row's `GetCurrentState`, while Auto-Detect or Assetto Corsa is picked.

---

## The row

`GameTelemetryDevice` follows `HeadTrackerDevice`: one socket on every address at the configured port, behind `NetworkListenerGate`, with `ExclusiveAddressUse` so a second listener shows as a conflict rather than taking half the packets, `SIO_UDP_CONNRESET` off, one receive thread, the frame under a lock, and a pooled clone on every read. Outside loopback it adds the inbound firewall rule **PadForge Game Telemetry** for the port.

Every packet that arrives, read or not, is copied to 127.0.0.1 at the forward port, from a second socket bound to loopback. A forward port of 0, or equal to the listening port, forwards nothing.

| Item | Value |
|---|---|
| Device type | `InputDeviceType.GameTelemetry` = 44 |
| Path, identity | `telemetry://game`, instance GUID MD5 of `pftelemetry:game`, VID 0x4754, PID 0x5544. The identity never changes, so mappings survive a change of game, port or format. |
| Axes 0 to 6 | Speed (0 at rest to Full Speed), RPM (share of max RPM), Throttle, Brake, Clutch, Handbrake, Steering (32768 at rest) |
| Axes 7 on | Each custom variable at 7 plus the slot it keeps, from its Min to its Max, up to the state's 24 axes. A slot a deleted variable gave up stays empty until a new variable takes it. |
| Buttons | Driving 0, Reverse 1, Neutral 2, Gear 1 to Gear 18 at 3 to 20 |

Speed to Handbrake carry the X, Y, Z, Rx, Ry and Rz axis GUIDs, and Steering and every variable the Z axis GUID. A Slider GUID would make the mapping picker offer *Slider N*, which reads the state's slider array, and the row writes only its axis array, the rule `SdlDeviceWrapper.GetDeviceObjects` keeps for its extra axes.

Driving reads `!DrivingReported || Driving`. After `SilenceMs` (1000) with no frame everything rests. The truck plugin sends only on a change, so its frames hold for `TruckSimulatorHoldMs` (10,000).

Step 1 phase 1i2 (`UpdateGameTelemetryDevice`) opens the row while the switch is on. It retires the row with `NeutralizeMappedOutputsFor` when the switch goes off, recreates it when the user removes it, and reopens it when `GameTelemetryRuntime.Version` moves. The switch, the port, the game, the custom format and the format list move it. The forward port and Full Speed are read live. While another program holds the port, each sweep tries it again (`RetryBind`, every 2 seconds), so the row listens once the port is free, with no toggle. The failure is logged once per run of failures.

The row joins the lists that name synthetic rows: out of `InputDeviceType.AnswersAnyDeviceSources`, internal in `DeviceRowViewModel.IsInternalVirtual`, no Submit Mapping, the type key and label `GameTelemetry`, the glyph U+EC4A, named axes in `MappingDisplayResolver`, and the Remote Link list of rows that send their names. No slot maps it on its own.

## The wheel RPM lights

`TelemetryHub` drives the wheel RPM lights. It runs only while a wheel asks for them, and its UDP sources listen on 5300 (Forza), 20777 (Codemasters) and 4444 (OutGauge). Two sockets cannot share a port, so the row and the hub share them this way:

- Before the row binds, `TelemetryHub.YieldPort(port)` closes the hub's source on that port, if one is open, and keeps it closed. A failed bind and the row's close give the port back (`ReclaimPort`), and a running hub opens its source again.
- `GameTelemetryRowSource` reads the row's engine values from `GameTelemetryRuntime.TryGetEngine`. The row publishes them on every poll under a lock, since the hub polls on its own thread. They count while the row is live, the game says it is driving, a max RPM is known, and the last publish is under a second old.
- The hub holds two row sources. `GameTelemetryRowSource(learnedMax: false)`, first in its order, answers when the game sent its max RPM. `GameTelemetryRowSource(learnedMax: true)`, last, answers when the max was learned, so a hub source with the game's own max answers first: scs-sdk-plugin's for Euro Truck Simulator 2. It raises a learned max to 1.05 times the RPM (`LearnedHeadroom`), the headroom `OutGaugeTelemetrySource` keeps, so a strip on a fresh engine or a new peak does not blink the shift cue.

While the row is live, the lights therefore read the game the user set the row up for, including EA SPORTS WRC and the custom formats, which the hub's own sources do not read. Shared memory games the row does not read (iRacing, rFactor, RaceRoom and the rest) still reach the lights through the hub.

---

## Custom Expression variables

`MacroTriggerSource.GameTelemetry` (2) is the third source of a Custom Expression variable. The variable names a `TelemetryChannel`:

| Channel | Value | Spec |
|---|---|---|
| SpeedKmh, SpeedMph | Speed in that unit | `tel:SpeedKmh` |
| Rpm, MaxRpm | RPM | `tel:Rpm` |
| RpmPercent | 0 to 100 | `tel:RpmPercent` |
| Gear | -1, 0, 1 and up | `tel:Gear` |
| ThrottlePercent, BrakePercent, ClutchPercent, HandbrakePercent | 0 to 100 | `tel:ThrottlePercent` |
| SteeringPercent | -100 to 100 | `tel:SteeringPercent` |
| Driving | 0 or 1 | `tel:Driving` |
| Variable | The custom variable's value after its scale | `tel:var:Boost` |

`TelemetryChannel` is append-only and saved by name. A spec with an unknown channel, or `Variable` without a name, is unbound. Both expression readers, `ReadExpressionVariable` for the gamepad lane and `ReadExpressionVariableRaw` for Extended and Nintendo slots, read `GameTelemetryRuntime.Read`, which returns 0 while nothing is live. The row publishes each frame with the variable list it opened with (`Publish`), and `Read` looks a name up in that list, so a format list saved in the window cannot pair a name with another variable's value before the row reopens. The values are published by the row on the poll thread and read later in the same pass, so they take no lock.

## Custom formats

`CustomTelemetryFormat` is saved in `PadForge.xml` under `GameTelemetryFormats`, one `Format` element per format with `Field` children. A format has a name (no `:` or `|`, the characters the spec splits on), a kind, a length or a key for Auto-Detect, a byte order and an optional pair of gear values. A field has a target, a name for a variable, an offset and type or a dotted JSON key, a scale, and a Min and Max. A hand-edited NaN or infinity in the file leaves the number as it was, the `MappingSource` rule, and a scaled value past a double's range leaves its target alone.

`GameTelemetryRuntime.Formats` drops a format whose name cannot be read or repeats an earlier one's name, ignoring case, since the picker, the profiles and the reader name a format by it. It builds the global variable list (each name once, in the order first used, with its first span) and gives each variable the axis slot it keeps (`AssignAxes`, the rule the voice phrase and NFC tag registries keep for their buttons). A name in use keeps its slot. A new name takes the slot its fields carry when no name in use holds it, and otherwise the lowest free slot, in first-use order, so a file from before the slots were saved keeps its old order. A name past the 17th slot reads as an expression channel alone, and a name no format uses gives its slot up. The slot is saved as the field's `Axis` attribute (`WriteAxes`), and the window carries it through an edit, so a renamed variable keeps its old name's slot. Then it compiles one `CompiledTelemetryFormat` per format. A binary field whose offset lies past the end of the packet, however large the offset, is skipped. JSON reads numbers, booleans as 1 or 0, and numeric strings.

---

## The Adaptive Trigger Effect action

`MacroActionType.TriggerEffect` (62) and `TriggerEffectStop` (63) sit in the Rumble category. `TriggerEffectCatalog` lists the DSX trigger modes the #529 encoder takes: Off (0), Feedback (13), Weapon (16), Vibration (17), Bow (14), Galloping (15), Machine (18), Slope Feedback (24), Multiple-Position Feedback (25), Multiple-Position Vibration (26), and the presets 1, 2, 3, 10, 4, 5, 6, 7, 9 and 11. DSX's duplicates of other modes (19 to 23) and VibrateTrigger (8) are left out. Each kind's parameters carry the ranges `GameModProtocol.TryEncodeTrigger` accepts, after Nielk1's TriggerEffectGenerator, and the action encodes through it, so a macro plays exactly what a mod can.

| Field | Saved as |
|---|---|
| `TriggerEffectSide` | Right, Left, Both (append-only) |
| `TriggerEffectMode` | The DSX mode number |
| `TriggerEffectParameters` | The values in the encoder's order, comma-separated. A short list takes the effect's starting values for the rest. |
| `TriggerEffectHold` | Duration, UntilRelease, UntilStopped (append-only) |
| `TriggerEffectMs` | 1 to 60,000 |

Both slot evaluators play the action into `InputManager.MacroTriggerEffects[slot]` and advance at once, the Rumble action's shape. An until-release effect is owned by its macro: the frame its trigger goes inactive, `ReleaseHeldTriggerEffects` ends it, whatever the run is doing. The pass also ends the effects of a macro that left the slot or was turned off (`ReleaseOwnersNotIn`), since neither reaches the release hook again. A timed effect ends at its time when the store is read. The store wakes the effects dispatcher only when a side's program changes, so a macro that repeats while held does not flood it.

The effects dispatcher reads the store once per pass, beside a mod's hold. `FillFromMacroEffects` puts a macro's block on each DualSense trigger that neither the game nor a mod holds, after `FillFromModHold` and before the impulse and steering effects. The order in the Sony pass is: the game, a game mod, a macro, the impulse and steering effects, then the pad page. When a macro's hold ends, PadForge's own value is written once more (`ModHoldEnded` on `_prevMacroRightTrig` and `_prevMacroLeftTrig`). `TryGetInboundTriggerEffects` falls back to the store after the game and the mods, so Xbox pads with Translate Adaptive Trigger Vibrations feel a macro's vibrating effects.

---

## Settings

`AppSettings` and `ProfileData` both carry `EnableGameTelemetry`, `GameTelemetryPort` (20777), `GameTelemetryFormat`, `GameTelemetryCustomFormat`, `GameTelemetryForwardPort` (0) and `GameTelemetryFullSpeed` (300), so they follow profiles like the Game Mods settings. `GameTelemetryFormats` is in `AppSettings` alone. On load the formats go first, then the game, port, forward port and Full Speed, and the switch last, so the row opens once with the whole configuration. A saved custom game whose format is gone reads as Auto-Detect, and a number out of range keeps the current value.

## Tests

- `GameTelemetryTests`: each decoder against packets built from the references' layouts, Auto-Detect and its hold, custom binary formats in both byte orders and JSON, the XML round trips, the row's axes, buttons, silence and truck hold, the port fence, a loopback receive with forwarding, the Assetto Corsa reader on maps of its own, the expression values and specs, a Custom Expression macro firing on telemetry, the wheel lights' hand-off (`YieldPort`, `ReclaimPort`, `TryGetEngine`, both `GameTelemetryRowSource`s and their places in the hub's order, a learned max's headroom against every wheel's shift cue), the Dashboard picker and the custom format window's checks.
- `MacroTriggerEffectTests` and `MacroTriggerEffectDispatchTests`: each effect against the encoder, the editor's values, the settings round trip, the store, both evaluators with the release hook and the pass's sweep, the fill order and the inbound copy.
- The test host binds no real telemetry port and opens no `acpmf` mapping: `GameTelemetryPortOffLimits` and `KunosOffLimits` in `TestHostFences.cs`, both pinned in `TestHostFenceTests`, and the row in the listener census of `TestHostListenerTests`.

---

*Last updated for PadForge 5.1.0.*
