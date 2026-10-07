# Haptic Mice: Internals

*How controller rumble reaches an MX Master 4 over HID++ and a Rival mouse through GameSense: the feed and its silence edges, the strength shaper, the HID++ 0x19B0 frames, discovery, the GameSense client, the worker, and why TouchSense mice stay out.*

The user-facing page is [Haptic Mice](../features/haptic-mice.md). This one is for whoever has to change the code.

| File | Role |
|---|---|
| `PadForge.App/Services/MouseHapticsService.cs` | The worker, the publish surface, `MouseRumbleShaper` |
| `PadForge.App/Common/Input/HidppHaptics.cs` | `HidppHapticProtocol`, `HidppChannel`, `HidppHapticProbe` |
| `PadForge.App/Services/GameSenseTactile.cs` | The GameSense client |
| `PadForge.App/Common/Input/InputManager.Step5.VirtualDevices.cs` | `UpdateMouseHapticsLane`, the per-tick feed |
| `PadForge.App/Common/Input/InputManager.cs` | The call site after `UpdateSensaLane`, and the three silence edges |
| `PadForge.App/Services/InputService.cs` | `StartMouseHapticsIfEnabled`, `StopMouseHapticsService`, `MouseHapticsStatusText` |
| `PadForge.Tests/MouseHapticsTests.cs` | A scripted HID++ mouse, a local GameSense server, and an opt-in live probe |

---

## The feed

`UpdateMouseHapticsLane` is a declared sibling of `UpdateSensaLane` and runs right after it in the poll loop. Behind `MouseHapticsService.PublisherArmed` (one volatile read while the feature is off) it max-merges each slot's VC inbound pack with the live `VibrationStates` through `LfeOutputState.MaxMerge`, takes the loudest of the four voices across every slot with `PackToAmplitude`, and publishes it with one volatile write. A fix to one lane's rumble authority belongs in both.

The lane runs only inside the non-idle loop, so the engine silences it on the three paths that skip it, each beside the rumble-audio lane's `SilenceAll`: engine stop, every idle iteration, and focus suspend. `MouseHapticsService.Silence()` zeroes the published amplitude, so a mouse never keeps buzzing on the last value.

---

## Strength shaping

`MouseRumbleShaper` turns the amplitude into a level with hysteresis, shared by both transports.

| Level | Rises at | Falls below | MX Master 4 waveform, then fallbacks |
|---|---|---|---|
| 1, light | 0.05 | 0.03 | subtle collision (4), damp (3), sharp (2) |
| 2, medium | 0.33 | 0.30 | damp collision (3), subtle (4), sharp (2) |
| 3, strong | 0.66 | 0.63 | sharp collision (2), damp (3), subtle (4) |

The first waveform the mouse's mask lists wins. A mouse that lists none of the three is dropped at discovery, with a diag line. The MX Master 4's repeat interval is `250 - 170 * t` ms, where `t` runs from 0 at an amplitude of 0.05 to 1 at full strength. The 80 ms floor is the cooldown mxhaptics (an MX Master 4 Minecraft mod, cloned) ships for its impact events, and LiveHaptics plays one waveform per scroll notch with no cooldown.

---

## HID++ 0x19B0

Logitech has not published the feature. Three implementations agree on it: Solaar (`hidpp20_constants.py` HapticWaveForms, `settings_templates.py` HapticLevel and PlayHapticWaveForm), OpenLogi's x19b0 reference, cross-checked against an MX Master 4, and LiveHaptics (`HidppDevice.cpp`).

| Function | Request | Answer |
|---|---|---|
| 0, getCapabilities | none | Payload bytes 4 to 7: the supported-waveform mask, big-endian, bit N for waveform N |
| 1, getConfiguration | none | Byte 0 bit 0: enabled. Byte 1: intensity, 0 to 100 |
| 2, setConfiguration | enabled, intensity | Never sent. The user's setting in Options+ stays theirs |
| 4, play | waveform, 0, 0 | An empty acknowledgment, not read |

LiveHaptics sends 100 after the waveform byte. Solaar and OpenLogi send zero, and this follows them. The waveform IDs are Solaar's table, which runs in the same order as the list in Logitech's Actions SDK documentation: sharp state change 0, damp state change 1, sharp collision 2, damp collision 3, subtle collision 4, and on to ringing at 14.

Every frame is a 20-byte long report: `11`, the device index, the feature index, the function in the high nibble with software ID `0C` in the low one, then up to 16 parameter bytes. Windows splits HID++ short and long reports into separate collections, and OpenRGB (`LogitechHIDPP20Controller.cpp` SendStandard) opens only the long one on Windows and sends every frame long. Its detector table puts a receiver's and a Bluetooth mouse's HID++ collection on usage page `FF00` usage 2. PadForge enumerates exactly those: vendor `046D`, page `FF00`, usage 2, a 20-byte input report, through `VendorHidRuntime.Enumerate`.

Software ID `0C` is claimed by no tool in Solaar's table (OpenRGB `07`, LGSTrayEx `0A`, Solaar `0B`, G HUB `0D`, firmware `0F`) and not used by LiveHaptics (`01`), so an answer meant for Logi Options+ never reads as PadForge's.

`HidppChannel` opens the collection shared through `VendorHidReader` and writes through `RawHidOutput.Write`. One request is in flight at a time. A report answers it when it echoes the device index, the feature index and the function byte. A HID++ 2.0 error carries `FF` where the feature index goes, then the request's feature index, function byte and error code. A busy error (`08`) is retried once after 50 ms, as OpenRGB's retry policy does. The answer window is 300 ms, or 700 ms on a Bluetooth path (one that carries the HID service UUID `00001812-...`), OpenRGB's first-contact and Bluetooth budgets.

---

## Discovery

`HidppHapticProbe.Probe` asks each collection Root.getFeature(0x19B0):

1. Device index `FF` first. An answer means the collection is the device itself, on Bluetooth or a cable, and slots 1 to 6 are never asked. A Bluetooth path is always the device itself.
2. Otherwise slots 1 to 6, a receiver's paired devices. Once a slot answers, `FF` is never asked again.
3. A slot that answers without the feature, or with a HID++ 2.0 error, is settled for as long as the path is present. A slot with the feature is described: the mask, the configuration, and the name through feature 0x0005, read the way Solaar's `get_name` does (function 0 for the length, function 1 at each offset for the next 16 bytes, UTF-8). Without a mask nothing can be chosen, so a failed capabilities read counts as a miss.
4. A slot that does not answer is asked again after 5, then 10, then 15 seconds.

A receiver answers an empty slot, a sleeping device and the `FF` index with HID++ 1.0 errors, and those are short reports that arrive on the other collection, so here they read as timeouts. The opt-in live test showed that shape on a Lightspeed receiver: error `01` (invalid sub-ID) for `FF` and `08` (unknown device) for every slot, all on the short collection, while its answer to the pairing-name register (`83 B5`, sub `40`, slot 1's stored name) arrived on the long one, the positive control for the channel.

The worker scans every 5 seconds while it has no Logitech target, and every 30 seconds otherwise, but only when nothing plays or rumble has been quiet for a second, so a probe never delays a pulse. Every 30 seconds in a quiet second it also reads each found device's configuration: an answer refreshes the feedback flag in the status, and silence takes the device off the list and reopens its slot. A failed play write drops the whole path, closes its channel and forgets its answers.

---

## GameSense

`GameSenseTactile` follows SteelSeries' gamesense-sdk documentation (cloned):

| Step | Call | Detail |
|---|---|---|
| Find the server | `coreProps.json` | The `address` key of `%PROGRAMDATA%\SteelSeries\SteelSeries Engine 3\coreProps.json`. No file means GG is not running |
| Name the game | `POST /game_metadata` | `PADFORGE`, displayed as PadForge |
| Bind the event | `POST /bind_game_event` | `RUMBLE`, 0 to 100, one `tactile` handler on zone `one`, mode `vibrate` |
| Change the level | `POST /game_event` | Only on a level change, since a handler runs on a new value. Values 0, 17, 50 and 84, one inside each range |
| Keep it alive | `POST /game_heartbeat` | Every 10 seconds while rumble holds. GameSense deactivates a game after 15 seconds without events |
| Stop | `POST /game_event` 0, then `POST /stop_game` | When the service stops. `stop_game` hands the devices back to GG at once |

The handler's pattern ranges pick a custom pulse (`length-ms` 30, 55 or 80) and its rate ranges repeat it (5, 7 or 10 times a second) until the value changes. Value 0 has an empty pattern and no rate. Each pulse ends before its next repeat starts, which answers the tactile doc's warning that vibrations take time and can queue up. Every call is synchronous on the worker with a 500 ms timeout. A failed call disconnects, and the worker reads `coreProps.json` again 15 seconds later, so a GG restart on a new port is picked up.

---

## Worker lifecycle

The worker copies `SensaHapticsService`: it swaps itself into `s_lastWorker`, joins a live predecessor for up to 10 seconds (the Sensa lane's F10 rule), and quits without arming on the deadline. Then it arms the publisher and loops every 10 ms:

1. Read the amplitude and update the level and the quiet clock.
2. Scan for Logitech devices and connect GameSense when due and allowed.
3. Check the found devices when due and quiet.
4. Play each Logitech device whose interval is up. Silence resets the interval.
5. Post the GameSense level or heartbeat.
6. Report the target list when it changed, tracked by a version counter so nothing is built per tick.

The `finally` disarms the publisher, zeroes the amplitude, closes every channel, closes GameSense and reports Stopped. `Stop` joins 3 seconds, so a worker inside a long scan can outlive its service, and the next worker's join covers that.

---

## TouchSense

The iFeel protocol is documented by two independent 2002 drivers, both cloned: mgrdcm's BeOS tool sends a 7-byte SET_REPORT (Output, report ID 0) `11 0A <strength> <delay> 00 <count> 00`, and Joshua Bobruk's Linux `ifeel.c` sends the same bytes on the interrupt OUT endpoint. Neither uses a report ID, and HID 1.11 says a device without report IDs has a single report, so the buzz report sits in the mouse's own collection.

Microsoft's table of top-level collections opened for system use lists mice as exclusive. A probe sent an output report through a zero-access handle to two exclusive keyboard collections (an ITE controller and a Logitech receiver): both failed with ERROR_INVALID_FUNCTION, elevated and not, while the same receiver's vendor HID++ collection accepted the same call in the same run. A read/write open of the exclusive collections fails with ERROR_ACCESS_DENIED. Only a kernel driver reaches the report, and iFeelPixel's download page records that "Logitech has discontinued TouchSense Mouse drivers support for 64bits OS".

---

## Ownership and persistence

| Leg | Where | Contract |
|---|---|---|
| Global | `AppSettingsData.EnableMouseHaptics`, `bool` | Default false |
| Profile | `ProfileData.EnableMouseHaptics`, `bool?` | Null is no opinion. Authored on a user change while a named profile is active, applied on a switch, refreshed on save, never snapshotted |

`DashboardViewModel.EnableMouseHaptics` and `MouseHapticsStatus` back the card. `MainWindow` autosaves on the toggle, `CanResetSetting` lists it, and `InputService` starts or stops the service on its `PropertyChanged`.

---

## Diag lines

All prefixed `MOUSEHAPTICS`:

- `start?` with the toggle, the engine and the live service, on every start request.
- `found` with the name, device index, feature index, mask and feedback flag.
- `lists no collision waveform` for a device that cannot play rumble.
- `stopped answering` for a device that missed a check.
- `write failed, dropping` with the path.
- `GameSense bound` and `GameSense stopped answering`.
- `predecessor join timed out` and `worker fault`.

---

## Tests

`MouseHapticsTests` runs alone in its collection, since the amplitude and the armed flag are process statics and an engine test's idle edge silences them.

- The feed: the pack reduction matches Sensa's, and publish clamps.
- The shaper: the level thresholds and hysteresis, the interval's range, the waveform fallbacks.
- HID++: byte-exact frames, reply matching against other software IDs, devices and report sizes, the big-endian mask, the Bluetooth window.
- Discovery against a scripted channel: a mouse behind a receiver, a Bluetooth mouse, a silent path, a device without the feature, a dead write, a missing capabilities answer, the 5, 10 and 15 second backoff, Solaar's name read.
- The service: discovery, waveform by level, pulse spacing, silence, a feedback-off mouse, a mouse with no collision, a failed write and recovery, the predecessor join and its deadline, and GameSense end to end.
- GameSense against a local server: the address read, the handler's JSON, change-only posts, the heartbeat, stop, a refusal and a server that goes away.
- Source pins for the lane, the three silence edges, the settings legs and the card, and every locale's strings.
- `Live_ProbesTheRealHidppCollections`, which runs only with `PADFORGE_LIVE_HIDPP=1` and probes this machine's HID++ collections read-only, with the pairing-name read as its positive control.

---

*Last updated for PadForge 5.0.0.*
