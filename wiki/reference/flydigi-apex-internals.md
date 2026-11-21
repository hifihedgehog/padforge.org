# Flydigi Apex Internals

*How PadForge identifies a Flydigi Apex 4, Apex 5 or Apex 6 Pro, the three vendor dialects it speaks, the session that writes every packet, the three lighting models and the two screen upload paths.*

For the user-facing side see [Flydigi Apex Controllers](../features/flydigi-apex.md). The feature is issue #586, from discussion #570.

No Flydigi pad ran this code. Every byte layout and timing below is copied from a tool whose author ran it on the pad, and the tests drive the code against scripted pads.

---

## Files

| File | Role |
|---|---|
| `PadForge.Engine/Flydigi/FlydigiApexProtocol.cs` | The IDs, the device types, and every report of the three dialects as bytes. Pure. |
| `PadForge.Engine/Flydigi/FlydigiTriggerTranslator.cs` | An 11-byte DualSense trigger block to one of the Apex 4 and 5's modes, and the bow, zone and rhythm descriptions. Pure. |
| `PadForge.Engine/Flydigi/FlydigiTriggerEngine.cs` | Plays blocks on an Apex 4 or 5's force triggers: the translation, the bow, zone and rhythm emulation, and the de-duplication. |
| `PadForge.Engine/Flydigi/Apex6TriggerEffect.cs` | `Apex6TriggerRenderer` and `Apex6TriggerMixer`: DualSense effects as 1 kHz waveforms for the Apex 6 Pro's trigger voice coils, and the one trigger column both triggers share. |
| `PadForge.Engine/Flydigi/FlydigiScreenFormat.cs` | `FlydigiScreenFormat` (the 160 by 80 frame), `FlydigiScreenOta` (the serial bootloader) and `FlydigiApex4XinputScreen` (the Apex 4's Xbox-mode upload). |
| `PadForge.App/Common/Input/Flydigi/FlydigiApexSession.cs` | One pad's connection: two handles on its vendor collection, its identity, and the one thread that writes to it. |
| `PadForge.App/Common/Input/Flydigi/FlydigiApexService.cs` | The sessions, keyed by device and by collection path: when a pad is asked, kept, retried and let go. |
| `PadForge.App/Common/Input/Flydigi/FlydigiScreenSender.cs` | Both screen uploads, the serial port and the Apex 4's WinUSB pipes. |
| `PadForge.App/Common/Input/Flydigi/FlydigiScreenPictures.cs` | Pictures, GIFs and text drawn as screen frames, on the UI thread. |
| `PadForge.App/Common/Input/UserEffectsDispatcher.Flydigi.cs` | The dispatcher's Flydigi lane: which block each trigger shows. |
| `PadForge.App/Common/Input/Peripherals/HidFamilies/FlydigiApexLighting.cs` | The lighting family, one model per pad. |
| `PadForge.App/Views/FlydigiScreenDialog.xaml.cs` and `PadForge.App/MainWindow.FlydigiScreen.cs` | The Controller Screen dialog, and its wiring to the settings and the SDL hint. |

The app also touches the pads in `InputManager.Step2.UpdateInputStates.cs` (the poll hook and the rumble hand-off), `HapticToneService.cs` (the Apex 6 Pro's grip samples), `PadPage.xaml.cs` (`SyncTabVisibility`) and `InputService.cs` (the Devices page button).

---

## Identity

All three pads answer on a HID collection with usage page `0xFFA0`, which SDL's Flydigi driver opens too. `FlydigiApexProtocol.CandidateModel` maps the IDs to the model they allow: `04B4:2412` to the Apex 4, `37D7:2501` to the Apex 5 and `37D7:2502` to the Apex 6 Pro. The IDs decide nothing on their own. The Vader 3 and Vader 4 share the Apex 4's, and the plain Apex 6 shares the Pro's, so `ParseIdentity` reads the device type in the pad's answer:

| Model | Request | Reply | Device types | Cable |
|---|---|---|---|---|
| Apex 5 | command `0x01` | `04 5A A5 01`, the type at byte 6, the connection at 7 | 128, 129, 133, 134, 135, 136 | connection 1 |
| Apex 4 | `05 EC` | 32 bytes with `EC` at byte 15, the type at 3, the connection at 13 | 84, 86, 87, 92, 93, 102, 103, 104 | connection 1 |
| Apex 6 Pro | command `0x01` | a checksummed frame, the type at payload 0, the connection at 1, the features at 24 | `0x96`, `0x98` | connection 0 |

`0x95` is the plain Apex 6, which `IsApex6ProDeviceType` refuses, as ApexSenseBridge's `isProDeviceType` does. The Apex 6 Pro's feature byte carries `0x80` for the grip voice coils, `0x10` for the trigger voice coils and `0x08` for the screen. `FlydigiApexSession.Open` drops an Apex 6 Pro that lacks either voice-coil bit, since it takes no stream (`FlydigiApexIdentity.HasVoiceCoils`). `HasScreen` is true for every Apex 4 and Apex 5 and for an Apex 6 Pro with the screen bit.

`Open` asks as ApexSenseBridge's `verifyIdentity` asks: an Apex 5 three times with 600 ms each, since another program's reader can take the first answer, an Apex 4 three times 1.5 s apart with 100 ms each, an Apex 6 once with 600 ms. Input that arrived before each request is drained first, at most 128 reports, since a pad that streams motion never runs dry.

---

## The three dialects

Every layout is in `FlydigiApexProtocol`.

**Apex 5.** Output report `0x03`, input report `0x04`, 32 bytes: `03 5A A5 cmd len payload`. A checksummed command's length byte is the payload plus 2, and the 8-bit sum from the command byte through the payload follows the payload (`Apex5Checksummed`). Commands 81 (trigger) and 18 (rumble) carry no checksum.

- Trigger, command 81: length 10, the apply flag 1, the side (1 left, 2 right), the mode and five parameters. A Race that starts at 0 with match on goes out with match off, the rewrite Flydigi's own live path makes (`Apex5Trigger`).
- Rumble, command 18 (`0x12`): length 6, the low motor, then the high.
- Lights, commands `0xA7` read, `0xA8` write start, `0xA9` packet: a 380-byte block in nineteen 20-byte packets.
- Screen, command 31 with the chip module 4: the screen chip goes to its serial bootloader.

**Apex 4.** Output report `0x05`, no magic and no checksum, zero padded to 12 bytes at least, since a shorter command is ignored. Replies arrive in the input stream.

- Rumble `05 0F low high`.
- Trigger, 15 bytes: `05 A0 01 apply side mode p1..p5`. The apply flag stays 0: set, the pad also writes the effect into its stored profile and stalls for about a second (flydigi-apex4-linux docs/TRIGGERS.md).
- The active profile slot: `05 EB A0`, answered with `EB A0` and the slot. A pad that gives no usable answer within a second is taken to be on slot 0, as flydigi-space-station-mac takes it.
- Lights: read `05 E5 slot`, write start `05 E7 slot 50` (14 bytes), and fifty 14-byte parcels `05 33 <10 bytes> A0 index`. Each write is acknowledged with `E7` or `33` at byte 15 and the index at byte 3, from 1 for a parcel and `FF` for the start.

**Apex 6 Pro.** Unnumbered 32-byte frames written behind a zero report ID: `5A A5 cmd len payload`, with the sum of bytes 2 to 30 in byte 31 (`Apex6Command`).

- Motor route, command `0x53`: triggers on the stream `01 target 03 00 40` (target 0 left, 1 right, 2 both), triggers off `01 target 00`, grips on the stream `01 12 02 40 00`, grips back to the pad `01 12 00`.
- Stream, command `0x57`: a control byte, `0x80` for interpolation, `0x18` for both grips, `0x04` for the trigger and the route in the low bits (0 left, 1 right, 2 both, 3 mute), then eight triples of trigger, left grip and right grip, each sample plus 128 (`Apex6Stream`).
- Lights, RAM block 4: `0xA3` reads (`01 04` for the length and CRC-32, `00 04 index 16` for a chunk), `0xA4` writes (`00 04 length crc32` begins, `01 offset count data` writes up to 16 bytes, `02 length crc32` commits, `03` aborts).
- Screen: command 31 with the chip module 4, in this framing.

---

## The session

`FlydigiApexSession` opens the pad's collection twice beside SDL's handle, one handle to write and one to read, and runs one thread per pad. Every command and the replies it waits for hold the session's `_io` lock, so the lighting family's exchanges and the thread's writes never interleave inside one command (`Exclusive`, `Request`, `Await`). Ten writes refused in a row mark the session failed, and the service lets it go.

### Apex 4 and Apex 5: the writer

`WriterLoop` keeps one wanted value for each trigger and one for the rumble, and the newest value wins, so a value replaced before it could go out is never sent (ApexSenseBridge `Apex5Device.cpp` `writerLoop`). `Pick` takes the slots in turn. The pacing is a `Policy` per model:

| Pad | Spacing | Rumble |
|---|---|---|
| Apex 4 | a trigger write 25 ms after any write, two rumbles 10 ms apart (`Apex4WritePacing.h`) | a stop goes first |
| Apex 5 on its receiver | 10 ms | 30 ms after a trigger write |
| Apex 5 by cable | none | none |

Rumble waits no more than 100 ms behind trigger writes (`RumbleMaximumWaitMs`). A refused write is owed again unless a newer value came meanwhile.

The Apex 4 acknowledges no trigger command, so each change is queued again 100 and 500 ms after it goes out. Each change stops its sticks for about 50 ms, so `Apex4ChangeAllowedIn` rations changes, after flydigi-apex4-linux `triggers.py` `_change_allowed`: no two changes closer than 100 ms, a change of mode at once, and a change of parameters 150 ms after the trigger's last change when one moved by more than a quarter (and by more than 4), 500 ms otherwise. Repeats are not rationed.

### Apex 6 Pro: the stream

`StreamLoop` runs at above-normal priority on a high-resolution waitable timer and sends one stream report every 8 ms, eight 1 ms samples for the trigger column and each grip, the shape of ApexSenseBridge `Apex6HapticBridge.cpp`. It starts with the first work: a trigger effect, a pending clear, or grip samples wanted or queued. The start puts both triggers and both grips on the stream, waits 94 ms and marks the stream up.

Each frame renders both triggers' effects (`Apex6TriggerRenderer.Render`) on one sample clock, takes the newest grip block no older than 24 ms from a queue of three, and has `Apex6TriggerMixer` pick the route. One trigger's effect goes to that trigger, and the pad is told which with a route command. Two at once are summed and sent to both, and that holds for half a second after one falls quiet, ApexSenseBridge's `Apex6DualArbiter` under its Mix policy. A grip with no samples plays the rumble as a carrier: 65 Hz at the low motor's level on the left grip and 150 Hz at the high motor's on the right, a level of 255 being a sine of 112.

After eight silent frames the loop sends one neutral report every 50 ms and wakes at once on new work. After three quiet seconds (`HandBackAfterQuietMs`) it sends three neutral reports, takes the triggers and grips off the stream and hands the motors back to the pad, whose own rumble then drives them.

A game's off on an Apex 6 Pro trigger waits 100 ms before it clears the effect, so a game that sets and clears an effect many times a second does not cut a burst. A vibration within half a second of a resistance on the same trigger is that resistance's click (`DetentFeedbackWindowMs`).

### Stops

`Quiet` releases both triggers and stops the rumble through the session's own thread. `QuietNow`, for a crash or a stop, writes the release on the calling thread: an Apex 5 gets both releases and a zero rumble, an Apex 4 gets both releases three times 25 ms apart, as flydigi-apex4-linux's reset sends each release once per entry of its schedule, and an Apex 6 Pro is given no work, marked handed back so the stream does not start again, and has its motors handed back. `Dispose` runs both, then closes the handles.

---

## The service

`FlydigiApexService.OnPolled` runs on the poll thread for every read of a candidate pad (`InputManager.Step2.UpdateInputStates.cs`). It costs a compare for any other device. For a pad with a session it hands the triggers' positions, axes 2 and 5, to the session. For a pad without one it queues `FlydigiApexSession.Open` on a pool thread, and a pad that did not answer is asked again after 5 s, then every 30 s.

`Keep` stores a session that has just opened and then checks that the pad is still listed at the path it was opened on and that the engine still runs, so a session that opened as the pad left is closed. A pad read at another path gets a new session there. A pad that has gone unread for 3 s (`StaleAfterMs`) counts as gone, whichever path took it offline, and a sweep once a second closes its session. `Shutdown` closes every session on the pool and waits up to 2 s for the stop frames.

The model a pad answered with goes on its device record (`UserDevice.FlydigiApexModel`), trusted only for the IDs it belongs to (`KeptModel`), so the controller page keeps the pad's cards while it sleeps. A record that takes a model raises `ModelRecorded`, which saves the settings. `Changed` tells the controller page, the Devices page and the lighting worker to look again.

A pad assigned to no slot has its triggers released and its rumble stopped once (`Unassigned`), since no dispatcher drives it.

---

## Triggers

### Which block

The dispatcher's Flydigi lane (`UserEffectsDispatcher.DriveFlydigiTriggers`) resolves the 11-byte DualSense block each trigger should show, in the DualSense lane's order: a game's effect on the slot's virtual DualSense, a game mod's hold, a macro's effect (the three latched from `TryGetInboundTriggerEffects`), the Impulse Triggers levels as a vibration block with the DualSense lane's 100 ms linger, the steering lock's pulse and resistance on a trigger the Adaptive Triggers card leaves off, and the card's own effect (`Ds5EffectSynthesizer.EncodeUserTrigger`). The lowest live slot the pad is assigned to drives it. An inbound off stands for 100 ms (`FlydigiOffHoldMs`) before PadForge's own layers show through, after ApexSenseBridge `AdaptiveTriggerBridge.cpp` `apply`.

### Apex 4 and Apex 5

`FlydigiTriggerTranslator` is a port of ApexSenseBridge's `AdaptiveTriggerTranslation.cpp`, function for function, whose table came from openflydigi's transcription of Space Station's own DualSense mode. The modes are `FlydigiTriggerMode`: 0 off, 1 constant resistance (start, force, match), 2 a vibration (start, pressure, strength, frequency, match), 3 a band that gives way (start, length, force, 0, match), 4 a hard stop (start, 255, match). Start is 0 to 192 of the pull. Space Station's labels for 2 and 3 are crossed against its enum's names, and the pad follows the labels, so the names here say what the trigger does.

`FlydigiTriggerEngine` sends one command per block and skips a command equal to the last one sent to that trigger. A block the table has no entry for, and a game's block of type 0, leave the trigger as it is: games interleave empty blocks with live effects. PadForge's own off releases the trigger. On an Apex 5 three kinds of block are played from the PC as the trigger moves: a bow whose draw spans four zones or more swaps its draw for a break past the end zone and back again (`FlydigiBow`), effects whose zones differ in strength swap the command as the trigger crosses a zone with a margin (`FlydigiZones`, `FlydigiZoneTracker`), and Galloping and Machine are stepped as a rhythm every 2 ms, no two commands closer than 10 ms (`FlydigiRhythm`, `StepRhythm`). The Apex 4 keeps the plain table, as ApexSenseBridge keeps it there.

### Apex 6 Pro

`Apex6TriggerRenderer` is a port of ApexSenseBridge's `Apex6TriggerEffect.cpp` (`decodeApex6TriggerEffect`, `renderApex6TriggerEffect`) with the constants of `Apex6TriggerEffect.h`. Zone resistance becomes a carrier whose level follows the zone strengths, a weapon's break point one burst as the trigger crosses it, a bow a draw that builds and a burst at the release, and Galloping and Machine a rhythm. The carrier runs at 85 Hz and a burst at 95 Hz (`CarrierFrequency`, `BurstFrequency`). ApexSenseBridge's twelve weapon presets and its test effects belong to its own trigger test and are left out.

### The controller page

`PadPage.SyncTabVisibility` shows the Adaptive Triggers and Impulse Triggers cards for a pad with a model, live or kept. Their tooltips name the pad's triggers (`Pad_AdaptiveTriggers_Subtitle_Flydigi`, `Pad_AdaptiveTriggers_Subtitle_FlydigiVibration` for the Apex 6 Pro, `Pad_ImpulseTriggers_Subtitle_Flydigi`), and the Translate Adaptive Trigger Vibrations row is hidden, since the pad takes the whole effect.

---

## Rumble and haptics

Step 2's force feedback (`InputManager.Step2.UpdateInputStates.cs`) gives a candidate pad's rumble to `FlydigiApexService.TakeRumble`. While the session takes it, SDL's rumble call is not made, so one writer paces every packet, and on the pass the writer changes SDL's level is stopped (`StopDeviceForces`). The trigger levels are not folded into the grips: the Flydigi lane plays them on the triggers. An Apex 6 Pro's session takes the rumble only while its stream runs.

`HapticToneService` gives an Apex 6 Pro with voice coils the family `FlydigiApex6`. Its mix, macro sounds and the persona haptic track, is low-passed at 400 Hz (`FlydigiLowPassHz`), resampled to 8 kHz, and each millisecond's eight frames are averaged into one grip sample, as ApexSenseBridge averages each millisecond of the 48 kHz haptic track. The samples go to the session (`SubmitGripPcm`), never through the sink's own handle. The Test button and a linked pad's tone play as a sine held under 400 Hz. The tone filter is hidden for this pad (`PadViewModel.SelectedDeviceHasToneFilter`). The Play DualSense Haptics on This Controller switch and its Haptics Gain show, in a panel gated on `SelectedDeviceHasHapticTones`.

---

## Lighting

`FlydigiApexLighting` is a family of the shared HID lighting worker. It matches a collection on usage page `0xFFA0` only for a pad `FlydigiApexService.ModelAt` names, its session's model or its kept one, so a Vader or a plain Apex 6 lists no lights. Every exchange goes through the pad's session, and the channel the worker opens stands for the claim. Flydigi Space Station is the family's vendor program (`VendorPrograms.FlydigiSpaceStation`), so the worker stands back while it runs. The lights belong on the pad's own device row (`PeripheralOutputHost`).

| Model | Lights | Repaint | Source |
|---|---|---|---|
| Apex 4 | 4 groups | 1000 ms | flydigi-space-station-mac `DeviceSession.swift`, `LEDConfig.swift` |
| Apex 5 | 12 lights | 80 ms | ApexSenseBridge `LightbarBridge.cpp`, openflydigi `flydigi/lighting.py`, `blobs.py` |
| Apex 6 Pro | 1 zone | 1500 ms hold | ApexSenseBridge `Apex6Lighting.cpp`, `LightbarBridge.cpp` |

**Apex 5.** The pad plays ten frames of twelve lights from a 380-byte block it keeps per profile slot. A session asks the active slot twice, 50 ms apart, and takes no pad whose two answers differ or whose Switch bank (slots 4 to 7) is active, as ApexSenseBridge's `BridgeCommand.cpp` does, then reads the block. A picture is that block with every frame the same color per light: the latch as given, loop 0 to 9, time 1, the brightness the pad stored (100 at most), twelve lights, mode 4 and no grip sync (`Apex5RgbBlock`). It goes out latched in nineteen acknowledged packets, then its first packet again with the latch clear, which shows the whole picture at once (openflydigi `docs/device-settings.md`). A write changes the pad's working copy, which the pad drops at its next sleep. The hand-back sends the block that was read the same way and applies the profile (`0xA2`), the one command a crash can send blind.

**Apex 4.** The pad keeps a 500-byte block per slot: a header, then sixteen groups of ten units of RGB in percent, four groups in use. A session reads the active slot's block. A picture is that block with the steady mode 5, the loop at 0 to 0, and every unit of each lit group its color, rounded down to percent (`Apex4SteadyLed`). flydigi-space-station-mac gives every group one color, and here each group takes its own. It goes out as a start and fifty parcels, each acknowledged, and a parcel not acknowledged within a second fails the picture, where the reference sends on. In DInput mode a write shows at once and is gone at power-off, since nothing here sends the save command.

**Apex 6 Pro.** The lighting lives in RAM block 4: a length and a CRC-16-CCITT of the body, then `LGHT`, version 2, the payload's length, the header's sum, the payload and its sum. A steady color is mode 1, red, green, blue, the brightness and the vibration flag (`Apex6SolidLighting`). The pad stores every write, so a color goes out once it has held for 1.5 s, a color within 12 a channel of the one the pad holds is not written, and no more than 300 go out in one run, ApexSenseBridge's three bounds (`Apex6HoldMs`, `Apex6ColorTolerance`, `Apex6MaximumWrites`). A session reads the block, takes no pad whose block does not parse, and saves it in the settings file before its first write (`KeyboardProfileBackups`). The hand-back writes it back and reads it back, three tries 300 ms apart. A run that ends without one leaves the copy, and the next run writes it back if the pad still shows PadForge's color (`Repair`). Two RAM exchanges are kept 220 ms apart, since the pad does not answer a request that follows the one before too closely (`RamSpacingMs`), and the stream's reports go out between them.

---

## The screen

A frame is an LVGL v8 image of 25,604 bytes: the header `04 80 02 0A`, then 160 by 80 RGB565 pixels, high byte first, row by row (`FlydigiScreenFormat`, openflydigi `PROTOCOL.md` section 8a, flydigi-space-station-mac `docs/protocol.md` section 6). A picture of several frames is the frames one after another. `FlydigiScreenPictures` draws a picture, a GIF or text into frames on the UI thread. A GIF's frames are drawn over one another on a canvas of the file's own size, cleared to black where a frame asks for the background back (disposal method 2), and the first frame's delay times them all, 100 ms when it gives none. A frame with disposal method 3 is drawn as one with disposal 0.

`FlydigiScreenSender.Send` refuses a pad on its receiver (`NotWired`), a picture with too many frames, and a second send to the same pad (`Busy`). The dialog takes `FlydigiApexService.SessionOf` at each Send, since a send makes the pad leave and come back with a new session.

### Apex 5 and Apex 6 Pro: the serial bootloader

1. A bootloader port already present is a send that stopped partway, and the send goes to it, openflydigi's recovery path. More than one fails as `SeveralPorts`.
2. Otherwise command 31 for the screen chip goes out through the session. The pad's answer says nothing either way, so a write that did not go fails as `SwitchNotSent`, and the port is what counts. After 5 s the port, `FFAA:5555`, is looked for every 250 ms for up to 30 s.
3. The port opens at 921600 baud, 8N1, no flow control, DTR and RTS raised, as Space Station's updater opens it (`SerialOtaLink`).
4. The upload runs openflydigi's `screen_ota.upload`: the base address (opcode 11) with the frame count and rate, the version (10), an erase (3) of each 4096-byte sector under the picture, writes (5) of 55 bytes at a time, and a reset (12) with the total length and a checksum, which is not retried, since a second could land after the chip restarted.
5. The chip syncs for about 15 s and the pad restarts on its own.

Every address comes from the chip, so nothing here can reach the program region. The Apex 6 Pro's exchanges are strict: each step waits up to 3 s for the reply to its own packet and is retried three times, and a base address that is not sector-aligned or whose erase would run past 4 GB fails as `BadAddress`. An Apex 5 takes 255 frames and an Apex 6 Pro 150. The frame time is 10 ms to 2.55 s on an Apex 5 and 1 ms to 2.5 s on an Apex 6 Pro (`ClampInterval`).

### Apex 4: Xbox mode over WinUSB

The Apex 4's screen is reachable only in Xbox mode, over interface 0's interrupt endpoints. In DInput mode the start is acknowledged and every later write refused until a power cycle (flydigi-space-station-mac `docs/protocol.md` section 6).

1. No `045E:028E` device may be present, since the binding moves every device of those IDs (`OtherXboxPads`).
2. `05 ED` switches the pad to Xbox mode. It must come back within 10 s as the one new `045E:028E` device (`NoXboxPad`, `OtherXboxPads`), with a USB product string that names Flydigi (`NotApex4`).
3. The node goes on the record in the settings file (`FlydigiScreenBindings`) before its driver moves, and SDL's HIDAPI Xbox 360 driver is held off (`InputManager.HoldXbox360HidapiDriver`), since WinUSB gives a device one handle and that driver opens such a pad on sight.
4. `VendorUsbDriverInstaller.Bind` moves the node from `xusb22` to WinUSB, and the pad must answer the device-info command `A5 10` as an Apex 4 within 2 s. Every command here is 15 bytes, `A5`, the command and its arguments, with the sum of the bytes before it at the end (`FlydigiApex4XinputScreen.Command`).
5. Each frame goes as a start `A5 D0`, data packets `A5 D1` of 26 bytes and an end `A5 D2`, each acknowledged and sent again on any result but 0, five times at most, then the picture's end `A5 D3`. The replies sit at byte 14 of the 64-byte input report, `5A A5` and the command, with the result at byte 18.
6. In a `finally` with the pipe still open, `A5 17` switches the pad back to DInput mode, whether the upload finished, was canceled or got no answer. A refused switch fails the send as `NotSwitchedBack`.
7. In an outer `finally`, SDL's driver is let go and the node goes back to Windows' Xbox driver (`VendorUsbDriverInstaller.Restore`). A hand-back that fails stays on the record, and `MainWindow.GiveBackFlydigiScreenBindings` tries it at the next start.

The Apex 4 takes 35 frames, about 4.5 s each.

### The dialog's lines

`FlydigiScreenDialog.FailureText` gives every `FlydigiScreenFailure` its own string. `PortDidNotOpen` names Flydigi Space Station only while `FlydigiServiceWatch.Running` names a Flydigi process, and says to switch the pad off and on otherwise (`FlydigiScreen_Fail_PortDidNotOpenPlain`). Closing the dialog while a send runs asks first, then cancels it, and the send hands the pad back on its own thread.

---

## Flydigi Space Station

Space Station's service talks to the pad over the same vendor collection and holds the pad's replies while it runs, so PadForge's identity request can go unanswered, which is one reason `FlydigiApexService` asks again every 30 s. Whether PadForge's second handle gets its own copy of each reply on Windows, as hidapi readers do on Linux, was not measured. `FlydigiServiceWatch` names the running Flydigi processes (`SpaceStationService`, `GameControllerService`, `Flydigi Space Station`) for the Devices page's warning, the lighting family stands back for the program, and the dialog's port line names it.

---

## References

Cloned beside PadForge:

| Clone | Commit | What PadForge takes from it |
|---|---|---|
| ApexSenseBridge (ReynArts) | cf52214 | The identity and its retries, the Apex 5 and Apex 6 dialects, the writer and its pacing, the trigger translation and the Apex 5's bow, zone and rhythm emulation, the Apex 6 Pro's trigger rendering, mixer, stream and hand-back, the Apex 5 light writes, the Apex 6 lighting block and its bounds. |
| openflydigi (Mikalai Kaliaha) | 9ab15b4 | The Apex 5 and Apex 6 protocol notes, the light block transfer and latch, the screen frame and the serial upload. |
| flydigi-space-station-mac (Uilton Lopes) | 649b9f3 | The Apex 4's light block, profile slot and parcels, the Xbox-mode screen upload and the DInput refusal, and the serial port's settings. |
| flydigi-apex4-linux (Jackwmtr) | afd2e43 | The Apex 4 trigger command, the apply flag, the repeats and the change rationing measured on the pad. |

SDL's own Flydigi driver (`SDL_hidapi_flydigi.c` in the SDL fork) reads the pads' input and is the rumble path without a session.

---

## Tests

`FlydigiApexProtocolTests` builds the reports byte for byte against the references. `FlydigiApexRuntimeTests` drives the session, the service, the trigger engine, the dispatcher lane and the lighting family against scripted pads. `FlydigiAuditFixTests` holds the 2026-11-20 audit's fixes: the Apex 6 Pro's motors staying handed back after a crash stop, the Apex 4's three releases, the switch back after a send that stops midway, a send to a closed session, each failure's own line, and the dialog's Send following the pad's session. `FlydigiScreenDialogTests` opens the dialog. No test runs against a pad.

---

## Related pages

- [Flydigi Apex Controllers](../features/flydigi-apex.md): the user guide.
- [Peripheral Outputs Internals](peripheral-outputs-internals.md): the shared HID lighting worker.
- [Controller Audio Internals](controller-audio-internals.md): the haptic sink model.
- [SDL3 Integration](sdl3-integration.md): SDL's Flydigi driver.

---

*Last updated for PadForge 6.0.0.*
