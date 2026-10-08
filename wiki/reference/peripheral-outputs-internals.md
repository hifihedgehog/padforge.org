# Peripheral Outputs Internals

*How a mouse, keyboard or vendor row assigned to a virtual controller takes that controller's lighting and rumble: the link table, the claims and their ruling, the four lighting backends, the haptic paths, Set Chroma Color, the route line, and the migration of the retired Dashboard switches.*

The user-facing page is [Mice, Keyboards and Vendor Rows](../features/peripherals.md). This one is for whoever has to change the code. The Razer Sensa worker has its own page, [Sensa Haptics Internals](sensa-haptics-internals.md).

| File | Role |
|---|---|
| `PadForge.App/Common/Input/Peripherals/PeripheralOutputs.cs` | The hub: the link table, haptic levels, lighting claims and their ruling, Set Chroma Color, backend states |
| `PadForge.App/Common/Input/Peripherals/PeripheralLinker.cs` | Vendor software presence, and the pure rules that link rows to output paths |
| `PadForge.App/Common/Input/Peripherals/PeripheralOutputHost.cs` | The link pass, claim pruning, the backends' lifetimes, the Sensa worker's lifecycle |
| `PadForge.App/Common/Input/Peripherals/PeripheralOutputRow.cs` | The four vendor rows |
| `PadForge.App/Common/Input/Peripherals/PeripheralProductIds.cs` | Product IDs that name a Razer or SteelSeries device's kind |
| `PadForge.App/Common/Input/Peripherals/PeripheralLightingColor.cs` | One device's color for one slot |
| `PadForge.App/Common/Input/Peripherals/GameLightbarCapture.cs` | The game's lightbar, per virtual controller |
| `PadForge.App/Common/Input/Peripherals/PeripheralRouteText.cs` | The route line on the Lighting and Force Feedback tabs |
| `PadForge.App/Common/Input/Peripherals/HidppBackend.cs`, `HidppUnits.cs` | The HID++ worker, unit discovery, receiver pairing tables, the 0x8070 frames, the battery decode |
| `PadForge.App/Common/Input/Peripherals/LedSdkBackend.cs` | The Logitech LED SDK worker |
| `PadForge.App/Common/Input/Peripherals/ChromaBackend.cs` | The Razer Chroma REST worker |
| `PadForge.App/Common/Input/Peripherals/GameSenseBackend.cs` | The SteelSeries GameSense worker |
| `PadForge.App/Common/Input/HidppHaptics.cs` | The HID++ 0x19B0 frames, the HID++ channel, the per-path probe state |
| `PadForge.App/Common/Input/HapticRumbleShaper.cs` | Rumble strength to a waveform level and a repeat interval |
| `PadForge.App/Common/Input/UserEffectsDispatcher.cs` | The peripheral lane: each slot's claims on its lit devices |
| `PadForge.App/Common/Input/InputManager.PeripheralRows.cs` | Step 1 phase 1m: the vendor rows open and retire |
| `PadForge.App/Common/Input/InputManager.Step2.UpdateInputStates.cs` | `ApplyForceFeedback`'s haptic-peripheral branch |
| `PadForge.App/Common/Input/InputManager.Step4b.EvaluateMacros.cs` | Set Chroma Color in both macro loops |
| `PadForge.App/Services/GameSenseClient.cs` | The GameSense HTTP calls |
| `PadForge.App/Services/LogiLedEngineNative.cs` | The LED SDK engine loader |
| `PadForge.App/Services/SensaHapticsService.cs` | The Interhaptics worker |
| `PadForge.App/Services/PeripheralSwitchMigration.cs` | The retired Dashboard switches become assignments |
| `PadForge.App/Services/InputService.cs` | The host's start and stop, the crash path, the Remote Link legs |
| `PadForge.App/ViewModels/DeviceSlotConfig.cs` | `PeripheralLightingEnabled` |
| `PadForge.App/Views/PadPage.xaml`, `PadPage.xaml.cs` | The tabs and their route lines |
| `PadForge.Tests/PeripheralOutputsTests.cs`, `PeripheralLightingTests.cs`, `LedSdkBackendTests.cs`, `ChromaBackendTests.cs`, `SetChromaColorMacroTests.cs`, `HidppHapticsTests.cs` | The benches |

---

## The model

A peripheral is a device row that shows a virtual controller's output on top of whatever input it has. Two kinds exist.

Device rows are the online mice, keyboards and analog keyboard rows (`PeripheralLinker.IsLinkable` (`PeripheralLinker.cs` line 264)) of three vendors: Logitech `0x046D`, Razer `0x1532` and SteelSeries `0x1038`. A row another PC forwards over Remote Link is left out, since that PC plays its outputs.

Vendor rows stand for a vendor's software: they reach every device it lights or rumbles, the ones PadForge does not read included.

### Vendor rows

`PeripheralOutputRow` (`PeripheralOutputRow.cs` line 44) is a synthetic `ISdlInputDevice` with no inputs, in the shape of `LogitechGKeysDevice`: a fixed path, an id hashed from a fixed string, vendor ID `0x5046` ("PF"), and a two-letter product ID per kind.

| `PeripheralRowKind` | Name | Path | Product ID | Device type | Opens while |
|---|---|---|---|---|---|
| `RazerChroma` | Razer Chroma | `razerchroma://local` | `0x4348` ("CH") | `PeripheralLighting` (40) | Synapse's Chroma runtime is installed |
| `LogitechLightsync` | Logitech LIGHTSYNC | `logilightsync://local` | `0x4C53` ("LS") | `PeripheralLighting` | A Logitech LED engine is registered |
| `RazerSensa` | Razer Sensa | `razersensa://local` | `0x5345` ("SE") | `PeripheralHaptics` (41) | Synapse's Chroma runtime is installed and the process is x64 |
| `SteelSeriesGG` | SteelSeries GG | `steelseriesgg://local` | `0x5347` ("SG") | `PeripheralLighting` | GG is installed |

The enum (`PeripheralRowKind` (`PeripheralOutputRow.cs` line 12)) is append-only. Its values are never saved, but `PeripheralOutputRow.IdentityFor` (`PeripheralOutputRow.cs` line 91) hashes `pfrazerchroma`, `pflogilightsync`, `pfrazersensa` and `pfsteelseriesgg` into the rows' `InstanceGuid`s, which assignments and profiles store. The migration can assign a row that has never opened, so the id comes from the kind alone. Neither device type answers an any-device mapping source (`InputDeviceType.AnswersAnyDeviceSources` (`InputTypes.cs` line 160)), and the Devices page names them Lighting and Haptics.

`InputManager.UpdatePeripheralRows` (`InputManager.PeripheralRows.cs` line 34) is Step 1's phase 1m. It opens a row while `InputManager.PeripheralRowWanted` (`InputManager.PeripheralRows.cs` line 20) finds its software, retires it when the software goes, and opens it again on the next pass after the user removes it from the Devices page, the G-keys row's recreate pattern. The row does no I/O, so the poll thread runs all of this. `InputManager.RetirePeripheralRow` (`InputManager.PeripheralRows.cs` line 77) stops the row's haptic level and releases its lighting claims by id, since its record may already be gone.

### Output paths and the link table

`OutputPath` (`PeripheralOutputs.cs` line 50) is a family and a key. Only a `HidppUnit` path reaches a single device. Every other family addresses a device class the vendor's software resolves, so `OutputPath.Shared` (`PeripheralOutputs.cs` line 54) is true for it.

| `OutputFamily` | Keys | Reaches |
|---|---|---|
| `HidppUnit` | The HID++ collection's path and the device index | One Logitech device |
| `ChromaCategory` | `keyboard`, `mouse`, `headset`, `mousepad`, `keypad`, `chromalink` | Every Razer device of the category |
| `LedSdkType` | `device`, `keyboard`, `mouse`, `mousemat`, `headset`, `speaker` | Every Logitech device of the type that G HUB or LGS lights |
| `GameSenseColor` | `mouse`, `keyboard`, `headset` | Every SteelSeries device of the type |
| `GameSenseTactile` | `tactile` | Every tactile Rival |
| `Interhaptics` | `sensa` | Every Sensa HD device |

`DeviceLinks` (`PeripheralOutputs.cs` line 58) holds one row's paths: `Lighting`, `Haptics`, the keys of the HID++ units it matched, and `CatchAll`, true for a vendor row. `DeviceLinks.HidppUnits` (`PeripheralOutputs.cs` line 67) lists the matched units whatever path lights the row, so Battery mode reads a Logitech device's charge while G HUB lights it.

`LinkTable` (`PeripheralOutputs.cs` line 82) is an immutable snapshot of every row's paths, indexed `ByDevice` and `ByPath`. The link pass swaps it whole through `PeripheralOutputs.PublishLinks` (`PeripheralOutputs.cs` line 171), which bumps `LinkVersion` and raises `LinksChanged`, so a reader never sees half a pass. `LinkTable.SameAs` (`PeripheralOutputs.cs` line 116) compares two tables row by row, paths, `CatchAll` and units included, so a pass publishes only a change.

### The recorded outputs

`UserDevice.PeripheralOutputs` (`UserDevice.cs` line 489) saves the bits of `PeripheralOutputKinds` (`PeripheralOutputs.cs` line 12) on the device record: 1 for haptics, 2 for lighting. The record keeps a row's Force Feedback and Lighting tabs up while the device sleeps or is unplugged, as a gamepad's tabs stay. Every haptic writer keys on `PeripheralOutputs.TakesHaptics` (`PeripheralOutputs.cs` line 186), the record's bit or a haptic path now, so a sleeping device keeps taking its level and plays the current one when it wakes.

---

## Presence and linking

### Presence

`PeripheralPresence.Read` (`PeripheralLinker.cs` line 29) finds which vendor software is there from the registry, files and process names, and never by opening an SDK, so an unassigned device costs nothing.

| Field | True when |
|---|---|
| `LogitechLedSdk` | The default value of `HKLM\SOFTWARE\Classes\CLSID\{a6519e67-7632-4375-afdf-caa889744403}\ServerBinary` names a file that exists |
| `LogitechGHubRunning` | A process named `lghub_agent`, `lgs` or `LCore` runs (`LogiLedEngineNative.RunningHost` (`LogiLedEngineNative.cs` line 86)). The last two are Logitech Gaming Software's hosts |
| `LogitechGamingSoftware` | An init-only member beside the positional ones (`PeripheralLinker.cs` line 22): the host found is `lgs` or `LCore`, not `lghub_agent`. The Lighting tab then names Logitech Gaming Software as the program lighting Logitech devices |
| `RazerSynapse` | `RzChromaSDK64.dll` is in the system directory, or `HKLM\SOFTWARE\Razer Chroma SDK` exists |
| `SteelSeriesGG` | GG's `coreProps.json` exists, or `Program Files\SteelSeries\GG` does |
| `SensaPlatform` | `PlatformSupport.SensaAvailable`: the process is x64 |

The host reads it at start and every `PresenceMs` (5000) on its link thread, and stores it in `PeripheralOutputs.Presence` (`PeripheralOutputs.cs` line 213), which raises `StatusChanged` on a change.

### The linker

`PeripheralLinker.Build` (`PeripheralLinker.cs` line 149) is pure: rows, the HID++ snapshot and presence in, a `LinkTable` out. A row that gets no path is left out of the table.

| Row | Haptic paths | Lighting paths |
|---|---|---|
| Razer Sensa row | `sensa`, with `SensaPlatform` | none |
| Razer Chroma row | none | All six Chroma categories, with `RazerSynapse` |
| Logitech LIGHTSYNC row | none | All six LED SDK paths, with `LogitechLedSdk` |
| SteelSeries GG row | none | The three GameSense color types, with `SteelSeriesGG` |
| Logitech device | Each matched unit that has haptics | Each matched unit with an RGB feature: while G HUB or LGS runs, its LED SDK type when the LED SDK is registered. Otherwise the unit itself, when it is lit directly |
| Razer device | none | Its Chroma category, with `RazerSynapse` |
| SteelSeries device | `tactile` for a tactile Rival, with `SteelSeriesGG` | Its GameSense type, `keyboard` or `mouse`, with `SteelSeriesGG` |

The direct path is feature 0x8070 alone: `HidppUnit.DirectRgb` (`HidppUnits.cs` line 62) needs that feature and at least one static zone. A Logitech device that lists 0x8071, 0x8081 or 0x8080, with or without 0x8070, takes a lighting path through the LED SDK only.

A mouse reports a keyboard collection for keys bound to keystrokes, and a keyboard reports a mouse collection for keys bound to clicks, so Windows can list two rows for one device, and a row's own kind can name the wrong category. `PeripheralProductIds.LightsAsKeyboard` (`PeripheralProductIds.cs` line 78) decides by product ID where a list holds it: every `USB_PID` in openrazer's `mouse.py` and `keyboards.py`, the Aerox, Rival and Sensei detectors in OpenRGB's `SteelSeriesControllerDetect.cpp` with every `product_id` in rivalcfg's devices, and that file's Apex detectors. A device the lists lack goes by its row's kind. `PeripheralLinker.RazerCategory` (`PeripheralLinker.cs` line 236) sends the keypads (the Nostromo and the Tartarus and Orbweaver families, openrazer `keyboards.py:74-273`) to `keypad`, and the Huntsman V3 boards openrazer does not list yet to `keyboard` through `AnalogKeyboardCatalog.IsRazerHuntsmanV3`. Every row of one device therefore lights as that device.

The tactile Rivals are the Rival 500, 700 and 710 (gamesense-sdk `standard-zones.md:49-52`), by rivalcfg's product IDs `0x170E`, `0x1700` and `0x1730` (`rival500.py:22`, `rival700.py:21` and `27`), which the linker keeps in `PeripheralLinker.RivalTactilePids` (`PeripheralLinker.cs` line 114). A Rival's keyboard collection is the Rival as well, so it takes the mouse color type and the tactile path.

A mouse or keyboard row is one Raw Input interface, and the device's HID++ channel is another collection of the same physical device. `PeripheralLinker.Matches` (`PeripheralLinker.cs` line 275) pairs them by container ID: on the bench's LIGHTSPEED receiver the mouse (`MI_00`), keyboard and consumer (`MI_01`) and HID++ (`MI_02`) collections all report one. A receiver gives one mouse row and one keyboard row however many devices are paired to it, so a receiver's unit goes to the row of its own kind, from feature 0x0005's device type. A unit on device index `0xFF`, wired or Bluetooth, is the device itself and alone in its container, so it goes to every row of the device when it is a mouse or keyboard kind, and a remote or presenter there stays out. A unit that gave no type goes to every row in its container. `PeripheralLinker.LedSdkTypeOf` (`PeripheralLinker.cs` line 249) names a unit's LED SDK type by its own kind, else by its row's.

`PeripheralLinker.Capabilities` (`PeripheralLinker.cs` line 288) is what a row records: the kinds its links found, plus the kinds it had while it is still being looked for. A Logitech device row is still being looked for before the HID++ worker's first scan and while its container has a slot left to ask, so a mouse asleep at launch keeps its tabs.

---

## The link pass

`PeripheralOutputHost` (`PeripheralOutputHost.cs` line 21) runs while the engine runs. `InputService.StartPeripheralOutputs` (`InputService.cs` line 10212) creates it at engine start, hands it `SlotHasController` (the input manager's `HasVirtualControllerAt`), subscribes to `CapabilitiesChanged`, and starts it. `InputService.StopPeripheralOutputs` (`InputService.cs` line 10223) disposes it at engine stop. There is no global switch. Every output follows assignment, the way a gamepad's does.

`PeripheralOutputHost.Start` (`PeripheralOutputHost.cs` line 72) starts the HID++, GameSense, Chroma and LED SDK workers, reads presence, and starts the `PeripheralLink` thread. The HID++ worker scans Logitech's HID++ collections from the start, since the linker needs its units. The other backends reach their vendor only while an assigned device or row uses a path they serve. `PeripheralOutputHost.Loop` (`PeripheralOutputHost.cs` line 112) reads presence every `PresenceMs`, runs one link pass and one Sensa lifecycle check, and waits `LinkMs` (500) on an event that `PeripheralOutputHost.Nudge` (`PeripheralOutputHost.cs` line 87) sets. The HID++ worker's `SnapshotChanged` and `InputService.OnDevicesUpdated` (`InputService.cs` line 9609) nudge it, so a device that comes or goes is linked at once.

`PeripheralOutputHost.Link` (`PeripheralOutputHost.cs` line 147), one pass:

1. Read presence and the HID++ snapshot, note whether any unit's charge changed (`PeripheralOutputHost.ChargesChanged` (`PeripheralOutputHost.cs` line 266)), and publish the snapshot as `PeripheralOutputs.Hidpp`.
2. Under the device list's lock, take each online vendor row and each linkable device row of the three vendors. A forwarded row is skipped.
3. Outside that lock, look up each device row's container ID (`AudioPassthroughService.DevicePathContainerId`), cached per path, since each lookup is a kernel round trip. The path was taken under the lock by `PeripheralOutputHost.ContainerPath` (`PeripheralOutputHost.cs` line 142): the row's device path, or for an analog keyboard row, whose device path is a synthetic `analogkb://` key, the HID collection the row reads, so a Logitech analog keyboard reaches its HID++ unit.
4. Build the table.
5. Prune the lighting claims (below), reading the assignments under the settings lock, never nested inside the device lock.
6. Write each row's recorded outputs. They land before the table, so a tab that refreshes on the new table reads the record that goes with it.
7. Publish the table when it changed, with a `PERIPHERAL links:` diag line, or raise `StatusChanged` when only a record moved.
8. Raise `CapabilitiesChanged` when a record moved. `InputService.OnPeripheralCapabilitiesChanged` (`InputService.cs` line 10235) marks the settings dirty and resyncs the Devices page, whose rumble chip reads the record.
9. Ask the dispatchers for a peripheral refresh: every slot, lit or not, after a relink, so a new path reaches a slot whose last pass lit nothing, or the lit slots after a charge changed, for Battery mode.

`PeripheralOutputs.PruneClaims` (`PeripheralOutputs.cs` line 480) drops every claim whose (device, slot) is no longer an assignment, and every claim on a slot that is not live. A slot is live while it has a live effects dispatcher (`UserEffectsDispatcher.HasLiveDispatcher` (`UserEffectsDispatcher.cs` line 1206)) or still holds a virtual controller (`SlotHasController`). Unassigning a device runs no pass on its old slot's dispatcher, and a slot whose controller went away has no dispatcher at all, so without the prune a claim would hold its device on a color nobody sets. A reorder moves the controllers first and rebuilds the slots' dispatchers one at a time afterward. The controller test keeps a slot's claims through that rebuild, so its devices are never handed back and taken again. The dispatcher's own disposal releases nothing for the same reason.

`PeripheralOutputHost.Stop` (`PeripheralOutputHost.cs` line 92) stops the Sensa worker and every backend, clears every claim, and publishes an empty table and an empty HID++ snapshot, so nothing claimed carries into the next engine start.

---

## Claims and the ruling

Lighting is claimed per (device, slot). One dictionary, `PeripheralOutputs.s_claims` (`PeripheralOutputs.cs` line 390), maps each pair to the slot's displayed player number and the color. A mouse on two virtual controllers holds one claim from each, and the ruling picks between them the way it picks between two devices on a shared path, so two dispatchers never take turns repainting it.

| Call | Does |
|---|---|
| `PeripheralOutputs.SetLighting` (`PeripheralOutputs.cs` line 411) | Adds or updates the claim. Any change bumps `LightingVersion` and raises `LightingChanged`, which wakes the HID++, LED SDK and Chroma workers. `ClaimsChanged` fires only when a claim starts or its player number changes |
| `PeripheralOutputs.ReleaseLighting` (`PeripheralOutputs.cs` line 443) | Drops one slot's claim. The same device's claim from another slot stays |
| `PeripheralOutputs.ReleaseSlot` (`PeripheralOutputs.cs` line 452) | Drops every claim a slot holds |
| `PeripheralOutputs.ReleaseDevice` (`PeripheralOutputs.cs` line 464) | Drops every claim on a device that went offline, retired or was removed |
| `PeripheralOutputs.PruneClaims` (`PeripheralOutputs.cs` line 480) | The link pass's prune |
| `PeripheralOutputs.ClearClaims` (`PeripheralOutputs.cs` line 497) | The host's stop |

`ClaimsChanged` never fires for a color alone, so a tab naming the controller that rules a shared path follows it without redrawing at animation speed.

`PeripheralOutputs.Rules` (`PeripheralOutputs.cs` line 531) is the ruling, pure so it is testable. Claimant `a` rules claimant `b` by the first of these that differs:

1. A device's own claim beats a vendor row's, whatever the numbers.
2. The smaller displayed player number. A claim with none (0 or less) reads as `int.MaxValue`, so it never beats a numbered one.
3. The lower slot index.
4. The lower device id, so the answer never flips between two equal claims, such as two rows of one device on one slot.

`PeripheralOutputs.TryResolveColor` (`PeripheralOutputs.cs` line 545) returns false when the path is not in the table or nothing claims it, which is a backend's cue to hand the device back to its own software. It counts only a claim whose row links that path, and it returns the ruling claim with the color, for a tab that names the controller whose color shows. The smallest displayed player number is the precedence `InputService.ApplyGuideLeds` gives the Steam Controller's process-wide home LED.

The haptic backends have no claims to read a player number from. `PeripheralOutputs.TryResolveHapticRuler` (`PeripheralOutputs.cs` line 704) runs the same `Rules` over the devices linked to a shared haptic path, ranked by `PeripheralOutputs.HapticRulingPlayer` (`PeripheralOutputs.cs` line 691): the device's smallest displayed player number among its assignments (`SettingsManager.SlotOrders.GetIdentityPlayerNumber`), else `PeerDrivenPlayer` (1000) when a Remote Link peer wrote its rumble last, else 0, which never rules. A Rival a linked PC drives therefore ranks after every controller on this PC.

---

## Lighting from the slot

The slot's effects dispatcher, which already lights a DualSense, lights the slot's mice, keyboards and vendor rows too. `UserEffectsDispatcher.DispatchSnapshot` (`UserEffectsDispatcher.cs` line 1819) walks the slot's assigned devices under the device list's lock. A device that is not a DualSense or DualShock 4 and that `UserEffectsDispatcher.IsLitPeripheral` (`UserEffectsDispatcher.cs` line 1770) accepts, by its record or a lighting path now, goes to `UserEffectsDispatcher.LightPeripheral` (`UserEffectsDispatcher.cs` line 1786) instead of an effect report. An offline one releases this slot's claim.

`LightPeripheral` takes the device's own config for the slot, else the slot's anchor config. With no config at all, or for a device row whose `PeripheralLightingEnabled` is off, it releases this slot's claim, and this controller no longer lights the device. A vendor row ignores the switch, since lighting is all it carries. Otherwise the color comes from `PeripheralLightingColor.Resolve` (`PeripheralLightingColor.cs` line 21) with the slot's game lightbar, the audio peak scaled by the device's own sensitivity, the input-reactive pulse, and the charge from `PeripheralOutputs.BatteryOf` (`PeripheralOutputs.cs` line 669), or 100 when it is unknown, which holds Battery mode at its full-charge color. The color goes to `SetLighting`, ranked by the slot's displayed player number (`GetGlobalSlotNumber`, or the slot index plus one for a slot in no order list). Every call there is a leaf. The I/O belongs to the backends, because the poll thread needs this lock every cycle.

### The color

`PeripheralLightingColor.Resolve` keeps the DualSense's order (`Ds5EffectSynthesizer.BuildFields`):

1. A lightbar the game wrote within the grace window wins over every setting, a macro color included.
2. Past the window, a device left at the defaults keeps the game's last color: Player Number, no input-reactive overlay, no live macro lightbar override. That is the stand-down the DualSense makes so a game that sets the bar once is not overwritten 1.5 seconds later (#191).
3. Anything else goes through `Ds4EffectSynthesizer.ResolveLightbarRgb`, the color core every lit device shares, so the whole mode set works: Player Number, Static, Breathing, Strobe, Rainbow, Color Cycle, Battery, the six audio modes, the input-reactive overlay and the macro lightbar override.

Player Number shows this slot's own player color, since each slot holds its own claim and the ruling picks the claim from the smallest displayed number. The Sony lane's lowest-raw-index owner rule is not used here, because it can disagree with the displayed numbers.

`UserEffectsDispatcher.OnAssignmentSetObserved` (`UserEffectsDispatcher.cs` line 530) releases the claim of a device that left the slot and, except on a new dispatcher's first look, forgets the slot's game color, the DualSense mirror's rule for an assignment change. A reorder rebuilds a slot's dispatcher after moving its controller's game color there, which is why the first look keeps it.

`UserEffectsDispatcher.LightingDriven` (`UserEffectsDispatcher.cs` line 1305) decides whether a device's config keeps the slot's animation timer running. A device with a lighting path drives it when it is a vendor row or its switch is on. A peripheral with no path now, asleep or offline or with its vendor's software closed, follows what the slot's last pass saw: an online mouse or keyboard follows its switch, and a vendor row or an offline device drives nothing. Every other device keeps the old rule. `UserEffectsDispatcher.OnConfigChanged` (`UserEffectsDispatcher.cs` line 1209) checks the timer again when the switch flips.

### The peripheral lane

Some of what a peripheral shows changes outside its slot: the game's lightbar, a charge, a new path. `UserEffectsDispatcher.RequestPeripheralRefresh` (`UserEffectsDispatcher.cs` line 1111) asks the slot's dispatcher for a pass over its lit peripherals alone. A slot that lit nothing last pass costs nothing, unless the request says `evenUnlit`. One refresh runs at a time on the thread pool, at most once per animation tick (33 ms), and requests that arrive while it runs fold into one more. `UserEffectsDispatcher.RunPeripheralRefresh` (`UserEffectsDispatcher.cs` line 1132) calls `DispatchSnapshot(peripheralsOnly: true)`, which writes no Sony effect report and no web pad or PS Move color. A game that animates its lightbar every frame reaches the peripherals at the dispatcher's own cadence, and the HIDMaestro output reader that reports the color never waits. `UserEffectsDispatcher.RequestPeripheralRefreshAll` (`UserEffectsDispatcher.cs` line 1163) asks every slot.

---

## The game's lightbar

`GameLightbar` (`GameLightbarCapture.cs` line 22) is the color a game writes to one virtual PlayStation controller. Each `HMaestroVirtualController` owns one, so the color moves with the controller when a reorder retargets it, the way its inbound rumble pack does.

The `OutputDecoded` handler that `HMaestroVirtualController.RegisterFeedbackCallback` (`HMaestroVirtualController.cs` line 1297) installs feeds it from the controller's output reader thread. Only a frame the trust gate accepts counts: the declared report length and a valid checksum (`HMaestroVirtualController.SonyFrameValid` (`HMaestroVirtualController.cs` line 1911)). The profile codec decodes a `lightbar` rgb24 field for the DualSense and the DualShock 4 alike, and the family's validity bit says whether this write carries it: `validFlag1 & 0x04` on a DualSense or DualSense Edge, `validFlag0 & 0x02` on a DualShock 4 (SDL's `k_EPS4EffectLED`). A valid write goes to `GameLightbar.Capture` (`GameLightbarCapture.cs` line 38). Any other trusted frame goes to `GameLightbar.NoteFrame` (`GameLightbarCapture.cs` line 53), which says the game is still there. The Chroma and LIGHTSYNC mirrors this replaced read the field before the gate, so a corrupt Bluetooth frame could paint a keyboard.

| Phase | When | What a lit device shows |
|---|---|---|
| `Fresh` | Within `GraceMs` (1500) of the last write | The game's color, over every setting |
| `Held` | Past the grace window while the game still sends trusted frames | The game's last color on a device left at the defaults, its own mode otherwise |
| `None` | No write yet, cleared, or `LapseMs` (15000) after the later of the last write and the last trusted frame | Its own mode |

`GraceMs` is the DualSense mirror's `ExternalSubsystemGraceMs` and `LapseMs` its `ExternalClaimLapseMs`. The next `NoteFrame` clears a lapsed record rather than reviving it, so a second game that never writes the bar does not bring back the first game's color. `Capture` returns true on a new color or on a write after the grace window closed, and the reader thread then queues the slot's refresh (`GameLightbarCapture.NotifyChanged` (`GameLightbarCapture.cs` line 208)).

`GameLightbarCapture` (`GameLightbarCapture.cs` line 137) maps slots to sources. `HMaestroVirtualController.PrepareDeviceEffectsForPublication` (`HMaestroVirtualController.cs` line 456) publishes a Sony controller's source once it wins its slot, `HMaestroVirtualController.RetargetToPad` (`HMaestroVirtualController.cs` line 534) moves it, and `HMaestroVirtualController.UnregisterFeedback` (`HMaestroVirtualController.cs` line 1289) and `HMaestroVirtualController.Disconnect` (`HMaestroVirtualController.cs` line 398) withdraw it. `GameLightbarCapture.Withdraw` (`GameLightbarCapture.cs` line 167) clears a slot only while it still holds that source, so in a two-pad swap the controller that already took the other's place keeps it. A dispatcher computes colors only when it runs, and a slot whose devices are not animated may not run again for a long time, so a timer every `WatchMs` (250) runs while any controller is registered and asks for a refresh when a slot's phase moves to `Held` or `None`. The capture reports `Fresh` itself.

---

## The HID++ backend

`HidppBackend` (`HidppBackend.cs` line 67) is one `PeripheralHidpp` thread that owns every HID++ collection, so a probe, a haptic pulse and a color never interleave on one channel.

### Collections and the channel

`HidppBackend.IsHidppLong` (`HidppBackend.cs` line 169) takes Logitech's vendor ID, a 20-byte input report, and usage page `0xFF00` usage 2 (mice and receivers) or `0xFF43` usage `0x0602` (keyboards), from OpenRGB `LogitechControllerDetect.cpp:162-166` and `574-587`. `HidppChannel` (`HidppHaptics.cs` line 231) opens that collection shared and reads it on a `VendorHidReader` thread, so Logi Options+ and other HID++ clients keep their own reports, and writes through `RawHidOutput.Write`. Every frame on the long collection is a long report, because Windows splits HID++ short and long reports into two collections and the long one rejects 7-byte writes, which is why OpenRGB forces long frames on Windows (`LogitechHIDPP20Controller.cpp` SendStandard).

One request is in flight at a time, the worker's. `HidppChannel.Request` (`HidppHaptics.cs` line 345) retries a HID++ 2.0 busy answer (`0x08`) once after 50 ms, OpenRGB's retry on busy. HID++ 1.0's `0x08` is `UNKNOWN_DEVICE` and is never retried. The answer window is 300 ms, or 700 ms on a Bluetooth path, one whose interface path carries the HID service UUID `00001812-0000-1000-8000-00805f9b34fb`, OpenRGB's first-contact and Bluetooth budgets.

### The loop

`HidppBackend.Worker` (`HidppBackend.cs` line 201) plays haptics, paints lighting, then scans when a scan is due and no unit is playing rumble, so a probe never delays a pulse. A check runs every `CheckMs` (30000) once nothing has played for `QuietMs` (1000). The wait between passes is `ActiveTickMs` (10) while any unit is linked for rumble and `IdleTickMs` (100) otherwise, and `HapticsChanged` and `LightingChanged` cut it short.

### Discovery

`HidppBackend.Scan` (`HidppBackend.cs` line 475) enumerates the vendor collections, drops paths that vanished, and keeps a `HidppPathState` per path, so a scan asks again only what is still open. A receiver known by its product ID (`HidppReceiverProtocol.KindOf` (`HidppUnits.cs` line 203): Bolt `0xC548`, and the Unifying and LIGHTSPEED receivers from Solaar's `base_usb.py:149-178`) has its pairing table read at every scan, so a device paired since the last scan is found. The table is HID++ 1.0 long register `0x2B5` (request `0x83B5`, Solaar `hidpp10.py:56-60`), one record per slot, at sub-register `0x20` plus the slot minus one on Unifying and LIGHTSPEED and `0x50` plus the slot on Bolt (Solaar `receiver.py:266-276` and `502-503`). The request goes out short on the receiver's short collection (usage 1), found by OpenRGB's path key (`HidppReceiverProtocol.ShortSibling` (`HidppUnits.cs` line 241)), and the record comes back long on the collection the worker already reads. `HidppUnitProbe.ReadPairing` (`HidppUnits.cs` line 363) takes a record as a paired device, asleep or not, and an error as an empty slot only when the same read errs twice, since another program reading the register at that moment could hand this read its error. An unanswered read stops the pass, and after `PairingGiveUp` (3) such passes in a row the table is not read again.

`HidppUnitProbe.Probe` (`HidppUnits.cs` line 287) then asks the slots: device index `0xFF` first on a path that is not a known receiver, then receiver slots 1 to 6 unless `0xFF` answered. A Bluetooth path is the device itself and has no slots. A slot is alive once Root answers for feature 0x0005. A receiver's HID++ 1.0 `INVALID_SUB_ID` for a slot means its device speaks only HID++ 1.0, and the slot settles. Any other HID++ 1.0 error, a busy answer, or no answer at all backs off 5, then 10, then 15 seconds. `HidppUnitProbe.Describe` (`HidppUnits.cs` line 492) reads the rest of a live unit:

- The device type, feature 0x0005 function 2, by Solaar's table (`hidpp20_constants.py:251-260`): 0 keyboard, 1 remote, 2 numpad, 3 mouse, 4 touchpad, 5 trackball, 6 presenter, 7 receiver. Then the name, read the way Solaar's `get_name` reads it.
- The 0x19B0 capabilities and configuration (below).
- The RGB feature: the first of 0x8071, 0x8081, 0x8080 and 0x8070, in that order, that the device has. For 0x8070, `HidppUnitProbe.StaticZones` (`HidppUnits.cs` line 582) walks the zones and keeps those that list the static effect, found by scanning for effect ID `0x0001`, never by a fixed index, which differs between models.
- The battery feature, 0x1004 before 0x1000.

A request that decides an output and goes unanswered marks the unit incomplete. Its slot backs off and is asked again in full, rather than keeping a device whose zones or type are missing. A unit with neither haptics nor an RGB feature is not kept, since a charge alone feeds only a lit device.

After a scan, the next one comes in `FirstScanMs` (5000) while some slot still waits for its device, else in `RescanMs` (30000). `HidppBackend.Check` (`HidppBackend.cs` line 585) asks each found unit something cheap: its 0x19B0 configuration, or Root's lookup of 0x0005 for a unit without haptics. A unit that answers refreshes its feedback flag and its charge. One that does not went to sleep or away: it leaves the list, its slot reopens, and the next scan comes within 5 seconds. A failed write drops the whole path.

`HidppSnapshot` (`HidppBackend.cs` line 10) publishes the units, the containers with a slot still open (`PendingContainers`), and `Scanned`, false until the first scan ran, so nothing the worker has not looked for reads as missing.

### Direct lighting

`HidppBackend.PaintLighting` (`HidppBackend.cs` line 260) paints each unit lit directly, a zone-only 0x8070 device whose claim is a single SetSWControl (OpenRGB `LogitechHIDPP20Controller.cpp:4038-4065`). The linker gives these paths only while neither G HUB nor LGS runs, since either software drives the same devices through the LED SDK.

- When the path is linked and `TryResolveColor` finds a color, the first color takes the lighting from the device's own effect with SetSWControl `[01 01]` (function 8, `HidppUnitProtocol.SetSwControl` (`HidppUnits.cs` line 126)). Each zone then gets the static effect in that color (function 3, `HidppUnitProtocol.SetStaticColor` (`HidppUnits.cs` line 116)): the zone, the static effect's index, R, G, B, and `0x02`, OpenRGB's fixed-color marker, or `0x00` for black (`LogitechHIDPP20Controller.cpp:5647-5663`). The persist byte stays 0, so nothing is saved to the device's memory.
- The claim and the color go out again every `ReassertMs` (5000) on their own clock, whatever the colors are doing, because a device back from sleep boots its onboard profile and drops the claim without a word (OpenRGB ReclaimSWControl, `LogitechHIDPP20Controller.cpp:6102-6110`). A changed color repaints at most every `PaintMs` (33).
- When nothing claims the path any more, SetSWControl `[00 00]` hands the lighting back (OpenRGB `LogitechHIDPP20Controller.cpp:3935-3946` and `4058-4078`, Solaar `settings_templates.py:3204-3293`).

The worker's `finally` hands every claimed unit back before it closes the channel, so stopping the engine leaves no mouse frozen on the last color.

### The crash path

A crash dialog keeps the process alive, and the worker with it, and a worker left running would claim the device again on its next reassert. `HidppBackend.NoteClaimed` (`HidppBackend.cs` line 350) records a unit before its claim goes out, so no moment exists in which a device is claimed and the hand-back does not know it. `HidppBackend.ReleaseClaimedNow` (`HidppBackend.cs` line 386) stops the worker first and waits `PanicJoinMs` (250) for it to hand back on its own channel, OpenRGB's teardown order (its sender stops before SetSWControl(0, 0), `LogitechHIDPP20Controller.cpp:3843-3856`). A stopping worker claims nothing more. Each unit still recorded goes back through `RawHidOutput.WriteOnce`, which opens its own handle with a 200 ms timeout. `InputService.PanicQuiesceOutputs` (`InputService.cs` line 12975) calls it through `PeripheralOutputHost.ReleaseLightingNow` (`PeripheralOutputHost.cs` line 339), after the GameSense wait. Chroma and GameSense end their sessions on their own timeouts, and the LED SDK goes with the process.

### Battery

`HidppUnitProtocol.BatteryPercent` (`HidppUnits.cs` line 136) decodes as Solaar does (`hidpp20.py:2191-2265`). 0x1004 function 1 gives a percent, or when that is 0 a level: 8 full at 90, 4 good at 50, 2 low at 20, 1 critical at 5, anything else 0 (`common.py:652-657`). 0x1000 function 0 gives a percent, and 0 means unknown. The charge is read at discovery and with each check. `PeripheralOutputs.BatteryOf` reads the first unit in the row's `HidppUnits` that reports one, whatever path lights the row. Razer and SteelSeries software report no charge here, so those rows read as unknown.

---

## The LED SDK backend

### The loader

`LogiLedEngineNative` (`LogiLedEngineNative.cs` line 33) replicates the `LogitechLedEnginesWrapper.dll` shim from managed code, so PadForge redistributes nothing of Logitech's. `LogiLedEngineNative.TryLoad` (`LogiLedEngineNative.cs` line 100) reads the default value of `ServerBinaryKey`, the wrapper's only embedded wide string and the key Aurora and Artemis read from HKLM's 64-bit view. It checks that the file's description is `Logitech Gaming LED SDK` (Aurora `LgsInstallationUtils.cs:48-64`), loads it with `LoadLibraryExW` and `LOAD_WITH_ALTERED_SEARCH_PATH` so the engine's own directory joins its dependency resolution, and resolves the undecorated cdecl `LogiLed*` exports:

| Export | Required |
|---|---|
| `LogiLedInit`, `LogiLedSetLighting`, `LogiLedShutdown` | yes |
| `LogiLedInitWithName` | no. Called with the ANSI string `"PadForge"`, `LogiLedInit` otherwise |
| `LogiLedSetTargetDevice` | no |
| `LogiLedSaveCurrentLighting`, `LogiLedRestoreLighting` | no |
| `LogiLedSetLightingForTargetZone` | no. The 9.00 header's zone call (logitech-led-sdk-rs `bindings-x86_64.rs:354`, RGB.NET `_LogitechGSDK.cs:146`) |

Old engines carry 13 exports, so each optional one degrades on its own. Returns are one-byte C++ `bool`, marshaled as `byte`. `LogiLedEngineNative.Unload` (`LogiLedEngineNative.cs` line 225) nulls every delegate before `FreeLibrary`, so a stray call lands on a null check instead of a freed code page. `ILogiLedNative` (`LedSdkBackend.cs` line 16) is the seam the bench scripts.

### Types and zones

`LedSdkBackend.TypeOf` (`LedSdkBackend.cs` line 139) maps a path key to `LogiLed::DeviceType` (logitech-led-sdk-rs `bindings-x86_64.rs:136-142`) and the zones written for it:

| Key | Device type | Zones | Reference |
|---|---|---|---|
| `keyboard` | 0 | 5, and the per-key call | RGB.NET's G213, `LogitechDeviceProvider.cs:99` |
| `mouse` | 3 | 3 | Aurora `LogitechDevice.cs:104-123` |
| `mousemat` | 4 | 1 | Aurora |
| `headset` | 8 | 4 | Aurora |
| `speaker` | 14 | 4 | Aurora |
| `device` | none | One `LogiLedSetLighting` on the RGB and monochrome targets | `LogitechGamingLEDSDK.pdf` p. 23, RGB.NET `LogitechPerDeviceUpdateQueue.cs:34-37` |

The `device` path lights the Logitech devices with no zones, the manual's G710+, G600, G510, G110, G19, G105, G300, G11, G13 and G15 (`LogitechGamingLEDSDK.pdf` pp. 9-18). Only the LIGHTSYNC row takes it, as the lightbar mirror lit them. `PeripheralLinker.LedSdkTypes` (`PeripheralLinker.cs` line 135) puts it first in paint order.

### Painting

`LedSdkBackend.Paint` (`LedSdkBackend.cs` line 370) sends whole percent per channel, rounded (`LedSdkBackend.ToPercent` (`LedSdkBackend.cs` line 198)). The target mask is sticky process-global state, so each call that narrows it puts it back:

- `device`: `SetTarget(3)` (`MONOCHROME` and `RGB`), `SetLighting`, `SetTarget(7)`. Per-key boards ignore that mask.
- `keyboard`, when the engine has the target call: `SetTarget(4)` (`PERKEY_RGB`) and `SetLighting`, since a per-key board answers only the whole-board call on its own target. Without the target call `SetLighting` would reach every device (`LogitechGamingLEDSDK.pdf` p. 23), so it is never sent that way.
- Every zoned type: `SetTarget(7)`, then one `LogiLedSetLightingForTargetZone` per zone, as RGB.NET sets the mask before every zone batch (`LogitechZoneUpdateQueue.cs`).

The whole-device call reaches zonal devices too. As in Aurora, which sends it before the zone calls on every update (`LogitechDevice.cs:94-124`), every claimed type after it in a pass goes out again.

`LedSdkBackend.CanPaint` (`LedSdkBackend.cs` line 277): the whole devices need the target call, a keyboard either call, and every other type the zone call. A session for types the engine cannot paint would paint nothing and fail every liveness round, so the engine goes back unopened until the claimed types change. `LedSdkBackend.PublishPaintable` (`LedSdkBackend.cs` line 292) stores the paths the loaded engine can paint in `PeripheralOutputs.LedSdkPaintable` (`PeripheralOutputs.cs` line 241). A load that fails while the software runs stores an empty list (`LedSdkBackend.PublishNone` (`LedSdkBackend.cs` line 301)), an x64 engine in the ARM64 build among the causes. The list is null before any load, while no Logitech software runs and once nothing is claimed, and the Lighting tab names a type outside it instead of a route.

### The session

`LedSdkBackend.LoopAsync` (`LedSdkBackend.cs` line 404) runs on a thread-pool task and makes every native call itself. Every reference serializes SDK calls, and the Rust binding wraps the whole API in a process mutex.

| Step | What happens | Timing |
|---|---|---|
| Orphan wait | A previous worker still inside the SDK is waited for | up to `DefaultOrphanWaitMs`, 15000 |
| Nothing claimed | No engine is loaded. `Idle`, no paintable list | polled every 100 ms |
| Presence | `SoftwarePresent`, else `Waiting` and no paintable list | retried every 30000 |
| Presence settle | The first time it finds the host, and after an absence or a reinitialization, wait before touching the engine. Init right after G HUB starts succeeds and does nothing (Aurora waits 5 s) | 5000 |
| Load | `TryLoad`, then `PublishPaintable`. A failed load publishes an empty list and reports `Waiting`. When no claimed type is paintable: unload, `Waiting`, and wait for the claimed types to change | retry 30000 on failure |
| Init | `InitWithName("PadForge")`, else `Init`. A refusal unloads and retries | retry 30000 |
| Open | Wait, `SetTarget(7)`, `SaveCurrent`, `Connected` | 100 (Aurora's settle) |
| Stream | Each poll: a type nobody claims any more gets the saved lighting back (`Restore`), and every remaining type is painted again over it. Between liveness rounds only a changed color goes out. Every `LivenessMs` (5000) every claimed type goes out | polled every 100 ms |
| Fail streak | Three liveness rounds in a row in which no call took end the session, which reinitializes after the retry | |
| Teardown | `Teardown`: `RestoreAndShutdown` (restore first, the RGB.NET dispose shape) unless a newer worker already loaded the engine, then `Unload` | |

A set color needs no keep-alive, but a dead G HUB shows only as failing calls, which the liveness round surfaces while the colors hold still. The manual gives two reasons a call answers false, a session never initialized and a lost connection to Logitech's software (`LogitechGamingLEDSDK.pdf`, `LogiLedSetLightingForTargetZone`). It says nothing about a type with no device behind it, so a type that fails alone is recorded as sent, waits for its next color or round, and never ends the session.

### Generations and orphans

`LedSdkBackend.Start` (`LedSdkBackend.cs` line 201) increments `s_generation`, and a worker whose generation is no longer the newest (`LedSdkBackend.Superseded` (`LedSdkBackend.cs` line 236)) drops its state reports and loads nothing more. `LedSdkBackend.Stop` (`LedSdkBackend.cs` line 211) cancels and waits 3000 ms. A worker still inside a native call is parked in `s_orphan`, and the next worker waits for it before loading the engine, for up to `DefaultOrphanWaitMs`, past the 14 seconds an Artemis-launched G HUB cold start takes, so two workers never overlap inside the SDK. `LedSdkBackend.MarkLoader` (`LedSdkBackend.cs` line 326) and `LedSdkBackend.Teardown` (`LedSdkBackend.cs` line 341) both take `s_sdkGate`, bounded by `GateWaitMs` (3000). An orphan that finishes before a newer worker loads the engine still restores and shuts down its own session. One that finishes after leaves the SDK to the newer session and only frees its module handle.

---

## The Chroma backend

`ChromaBackend` (`ChromaBackend.cs` line 49) talks to the Chroma REST server Synapse hosts at `ChromaBackend.DefaultEndpoint` (`ChromaBackend.cs` line 53), `http://localhost:54235`. The official Chroma REST docs and chroma-sdk/Colore (`RestApi.cs`) agree on every field. The endpoint is injectable because the production port is machine-global, and a test that talked to it would reach a real Synapse.

`ChromaBackend.Wanted` (`ChromaBackend.cs` line 157) gives each category's color in the order the init lists them (Colore `Rest/RestApi.cs`, the official REST docs): a live Set Chroma Color first (below), else `TryResolveColor` on the category. A Razer device claims its own category while Control This Device’s Lighting is on for its controller, the Razer Chroma row claims all six and rules the ones no device claims, and the smallest displayed player number rules a category two controllers claim.

| Step | Call | Notes |
|---|---|---|
| Open | `POST {endpoint}/razer/chromasdk` with `ChromaBackend.InitBody` (`ChromaBackend.cs` line 137) | The app-info JSON Synapse shows in its Connect tab: title `PadForge`, a description, an author, `device_supported` listing only the categories wanted now, and category `application`. The answer's `uri` names the session |
| Heartbeat | `PUT {uri}/heartbeat`, no body | Every second, Colore's interval and its no-data overload (`RestClient.cs:107`). A session dies after 15 seconds without a command. A non-success status ends the session |
| Effect | `PUT {uri}/{category}` with `{"effect":"CHROMA_STATIC","param":{"color":N}}` | Applies at once. Only a changed color goes out per category. `N` is BGR, `R + (G << 8) + (B << 16)` (`ChromaBackend.ToBgr` (`ChromaBackend.cs` line 131)) |
| Close | `DELETE {uri}` | Bounded to a second. Ends the session, which hands the lighting back to Synapse |

The session lists only the categories something wants, and it is opened again when that set changes, so a category nothing claims stays Synapse's. The docs do not say whether Synapse leaves alone a category a session lists and never paints. With nothing wanted, the worker holds no session and reports `Idle`.

The server answers HTTP 200 with a `result` integer even when it rejects an effect, so `ChromaBackend.SendStaticAsync` (`ChromaBackend.cs` line 356) reads the body, as Colore checks that field after every effect call (`Rest/RestApi.cs` SetEffectAsync). `ChromaBackend.TryReadResult` (`ChromaBackend.cs` line 385) needs a JSON object with a numeric `result`. 0 and 1167 are accepted, 1167 being `ResultDeviceNotConnected`, a category with no device behind it (Colore `Data/Result.cs`). Anything else leaves the category's last color unrecorded, so the next poll retries it, and a rejection is logged when it differs from the last one logged.

URIs are joined by string concatenation, because the session URI has no trailing slash and `new Uri(base, relative)` would replace its last segment. `HttpClient` reports its own 5000 ms timeout as a `TaskCanceledException`. The init's catch for a cancellation takes only a stop (`when (ct.IsCancellationRequested)`), so a slow Synapse stays on the 30-second retry path as `Waiting`. `LightingChanged` and `ChromaMacroChanged` wake the 100 ms poll. `ChromaBackend.Stop` (`ChromaBackend.cs` line 108) cancels, waits 3 seconds, and then lets a worker parked in a REST call finish on its own, since the session it ends is its own.

---

## The GameSense backend

`GameSenseBackend` (`GameSenseBackend.cs` line 28) is one `PeripheralGameSense` thread on a 20 ms tick. `GameSenseClient` (`GameSenseClient.cs` line 47) makes its HTTP calls, synchronous with a 500 ms timeout, since a local engine answers in milliseconds. Every rule in the client is from SteelSeries/gamesense-sdk. Rumble and colors share one game, `PADFORGE`, displayed as PadForge.

| Call | When | What |
|---|---|---|
| Read `coreProps.json` | Each connect | The `address` key of `%PROGRAMDATA%\SteelSeries\SteelSeries Engine 3\coreProps.json`. No file means GG is not running |
| `POST /game_metadata`, `POST /bind_game_event` | Connect | The game, then `RUMBLE` (0 to 100) with one `tactile` handler on zone `one`, mode `vibrate` |
| `POST /remove_game_event` | Connect | Every color event a dropped session or a dead process left bound, so a type nobody claims stays GG's |
| `POST /game_event` | A rumble level change | `RUMBLE` at 0, 17, 50 or 84, one value inside each range (`GameSenseClient.LevelValue` (`GameSenseClient.cs` line 142)) |
| `POST /bind_game_event`, `POST /game_event` | A color type newly claimed, or its color changed | `COLOR_MOUSE`, `COLOR_KEYBOARD` or `COLOR_HEADSET` with `value_optional` and one `context-color` handler per zone reading the frame key `color`, then the color in the event's frame |
| `POST /remove_game_event` | A type stops being claimed | GG lights that type again |
| `POST /game_heartbeat` | Every 10 seconds while rumble or a color holds | GameSense deactivates a game after 15 seconds without events |
| `POST /game_event` 0, `POST /remove_game_event`, `POST /stop_game` | `GameSenseClient.Close` (`GameSenseClient.cs` line 261) | Silences the motor, drops the color events, and hands the devices back to GG |

The `RUMBLE` binding, `GameSenseClient.BindBody` (`GameSenseClient.cs` line 69), gives each value range a custom pulse, 30 ms for 1 to 33, 55 ms for 34 to 66 and 80 ms for 67 to 100, and a rate that repeats it 5, 7 or 10 times a second until the value changes. Each pulse ends before its next repeat starts, which answers the tactile doc's warning that vibrations take time and can queue up. Value 0 plays nothing and repeats nothing. `GameSenseClient.ColorZones` (`GameSenseClient.cs` line 91) follows `standard-zones.md:86-110` and `208-238`: the mouse's `wheel`, `logo` and `base`, the keyboard's `main-keyboard`, `function-keys`, `keypad`, `number-keys` and `macro-keys` plus `rgb-per-key-zones` `all` for a per-key board, and the headset's `earcups`. GameSense has no mousepad type: the QcK Prism pads answer only its zone-count types (`standard-zones.md:29` and `37`), which no row binds. The fourth general type, `indicator`, is a single status light and stays out.

`GameSenseBackend.Worker` (`GameSenseBackend.cs` line 113), each tick:

1. Every `RulerMs` (250), work out the ruling Rival on the tactile path through `TryResolveHapticRuler`. The tactile handler drives every tactile Rival at once (`standard-zones.md:3`, "a device category"), so the Rival on the virtual controller with the smallest displayed player number sets the level for all of them.
2. Resolve each claimed color type (`GameSenseBackend.Colors` (`GameSenseBackend.cs` line 90)).
3. With no ruling Rival and no color, post level 0 and remove every color event at once, since GG repeats a level's pulse until the value changes and a Rival that just left its controller would buzz on. After `ReleaseMs` (2000) of nothing claimed, `Close`, so a reassignment does not churn the registration.
4. Otherwise, shape the ruler's level (`HapticRumbleShaper.Level`), connect when due, render the level, and set the colors at most every `ColorMs` (50), or at once when the claimed types change. A refused or failed connect, or a call that stops answering, disconnects, and the next try comes after `RetryMs` (15000).

The crash path calls `GameSenseBackend.WaitForSilence` (`GameSenseBackend.cs` line 224) after the engine's quiesce zeroed every level. GG repeats a pulse at its rate until the value changes (`json-handlers-tactile.md:187-195`) or the game goes 15 seconds without an event (`sending-game-events.md:83`), so a process that died first would leave a Rival buzzing that long. `PanicQuiesceOutputs` waits up to 250 ms for the worker to post the zero, the way the Bliss-Box stop waits in `InputManager.QuiesceOutputs`.

---

## Haptics

### The level

`PeripheralOutputs.SetMotors` (`PeripheralOutputs.cs` line 303) stores a row's combined level as float bits: the stronger motor over 65535, since every backend plays one waveform or one intensity. A zero goes through `PeripheralOutputs.StopHaptics` (`PeripheralOutputs.cs` line 324). The first nonzero level after silence raises `HapticsChanged`, which wakes the HID++ worker so the first pulse of new rumble plays at once. The level is kept whether or not a path is linked now. A backend plays only a linked path, so a device that wakes plays the level the game holds, and a stop sent while it slept is never lost. `PeripheralOutputs.AmplitudeOf` (`PeripheralOutputs.cs` line 335) reads it.

`PeripheralOutputs.IsHapticPeripheral` (`PeripheralOutputs.cs` line 193) adds to `TakesHaptics` a mouse or keyboard a linked PC forwards with rumble. It opens the Force Feedback tab and the Devices page's rumble chip (`InputService.PopulateDeviceRow` (`InputService.cs` line 14159)), and the chip is Identify's button.

### Step 2

`InputManager.ApplyForceFeedback` (`InputManager.Step2.UpdateInputStates.cs` line 671) treats a haptic peripheral the way it treats a Bliss-Box port: a sole writer that records a level and hands it to a worker.

- A haptic mouse or keyboard, or the Sensa row, reports no SDL rumble, so loading it made no `ForceFeedbackState`. The poll thread makes one on first use, after `StopHaptics`, since a new cache starts from zero and a level kept from before the row was removed and found again would otherwise play on.
- `isPeripheralHaptic` joins the Xbox impulse, Padix and Bliss-Box paths past the SDL rumble gate, and like them it needs `ud.Device`.
- On every slot the row is on, the level goes through the chain a gamepad's does: game rumble, macro rumble, constant force, and the row's own Force Feedback settings for that slot. The slots combine by maximum.
- The `isPeripheralHaptic` branch (`InputManager.Step2.UpdateInputStates.cs` line 1234) folds trigger rumble into the motors (`ForceFeedbackState.FoldTriggersForDirectWriter`), since no peripheral has trigger motors. When `PeripheralOutputs.ConsumeResend` (`PeripheralOutputs.cs` line 367) says a silence edge owes the row a resend, the branch marks the snapshot failed. It calls `SetMotors` only when `TryRecordMotorSnapshot` reports a change.
- When the row's last slot goes, it sends a zero once through `SetMotors` (`InputManager.Step2.UpdateInputStates.cs` line 850), under the row's output gate and the Remote Link guards.

### Silence edges and the other writers

`PeripheralOutputs.SilenceHaptics` (`PeripheralOutputs.cs` line 352) zeroes every level and marks each row that was playing as owed one resend, so a level a game still asks for comes back the moment Step 2 runs again instead of reading as unchanged. It runs where Step 2 does not:

| Edge | Site |
|---|---|
| Engine stop | `InputManager.Stop` (`InputManager.cs` line 1810) |
| Crash quiesce | `InputManager.StopAllForceFeedback` (`InputManager.cs` line 2325), which also stops each row's level under its output gate, so a level the poll thread or Identify decided under the gate cannot land after the sweep |
| Focus suspend | `InputManager.ApplyFocusSuspension` (`InputManager.cs` line 3838), with `keepRelayed: true`: a level a Remote Link peer drives keeps playing, as a peer-driven SDL rumble does, since the relay still writes while the engine is suspended and a peer sends a steady level only once |

Idle is no edge. Step 2 runs there and writes the level itself.

The other writers: `InputManager.MarkDeviceOffline` (`InputManager.Step1.UpdateDevices.cs` line 1167) and `SettingsManager.RemoveDevice` (`SettingsManager.cs` line 487) stop a row's level and release its claims. Identify's pulse train (`InputService.IdentifyDevice` (`InputService.cs` line 15962)) sets the level under the row's gate with the quiesce checked again, and ends at the level the snapshot holds. Steering-angle rumble accepts a haptic peripheral (`InputManager.SupportsSteeringAngleRumble` (`InputManager.SteeringAngleRumble.cs` line 51)).

### HID++ 0x19B0

Logitech has not published the haptic feature. Three implementations agree on it: Solaar (`hidpp20_constants.py` HapticWaveForms, `settings_templates.py` HapticLevel and PlayHapticWaveForm), OpenLogi's x19b0 reference, and LiveHaptics (`HidppDevice.cpp`). `HidppHapticProtocol` (`HidppHaptics.cs` line 28) follows them.

| Function | Request | Answer |
|---|---|---|
| 0, getCapabilities | none | Payload bytes 4 to 7: the supported-waveform mask, big-endian, bit N for waveform N |
| 1, getConfiguration | none | Byte 0 bit 0: feedback enabled. Byte 1: intensity, 0 to 100 |
| 4, play | waveform, 0, 0 | Not read |

LiveHaptics sends 100 after the waveform byte. Solaar and OpenLogi send zero, and so does PadForge. No setConfiguration is ever sent, so the intensity and the on/off switch in Logi Options+ stay the user's. A frame (`HidppHapticProtocol.Frame` (`HidppHaptics.cs` line 77)) is report ID `0x11`, the device index, the feature index, the function in the high nibble with software ID `0x0C` in the low one, and up to 16 parameter bytes. `0x0C` is none of the IDs Solaar's table lists for other tools (OpenRGB `0x07`, LGSTrayEx `0x0A`, Solaar `0x0B`, G HUB `0x0D`, the firmware `0x0F`) and not LiveHaptics' `0x01`, so an answer meant for Logi Options+ never reads as PadForge's.

`HidppBackend.PlayHaptics` (`HidppBackend.cs` line 416) plays each haptic unit a linked row asks for, at the strongest level when two rows link it. `HapticRumbleShaper` (`HapticRumbleShaper.cs` line 14) turns the amplitude into pulses:

| Level | Rises at | Falls below | Waveform, then fallbacks |
|---|---|---|---|
| 1 | 0.05 | 0.03 | subtle collision (4), damp collision (3), sharp collision (2) |
| 2 | 0.33 | 0.30 | damp collision (3), subtle collision (4), sharp collision (2) |
| 3 | 0.66 | 0.63 | sharp collision (2), damp collision (3), subtle collision (4) |

The hysteresis keeps rumble that hovers on a boundary from flipping the level every tick. `HapticRumbleShaper.Waveform` (`HapticRumbleShaper.cs` line 45) takes the first of the level's waveforms the unit's mask lists, and `HidppUnit.HasHaptics` (`HidppUnits.cs` line 55) requires at least one of the three. `HapticRumbleShaper.IntervalMs` (`HapticRumbleShaper.cs` line 35) runs linearly from 250 ms at an amplitude of 0.05 to 80 ms at full strength, the cooldown mxhaptics ships for its impact events. Silence resets a unit's interval, so the first pulse of new rumble plays at once. Logitech's Actions SDK describes the sharp collision as a "High-intensity impact simulation", the damp collision as a "Medium-intensity impact with gradual decay" and the subtle collision as "Low-intensity feedback for light contact events". No model list gates the path. Any Logitech device that lists 0x19B0 and one of the three waveforms takes it, the MX Master 4 among them.

The configuration's enable bit, read at discovery and with each check, feeds the Force Feedback tab's line for a unit whose feedback is off in Logi Options+.

### The GameSense tactile path

A tactile Rival's level reaches GG through the GameSense worker above. Every tactile Rival plays the ruling Rival's level. The motor stops at the first ruler check (`RulerMs`, 250) that finds no Rival assigned, and GG gets the mice back `ReleaseMs` (2000) after nothing at all is claimed, colors included.

### Razer Sensa

The Sensa row's level reaches the Interhaptics engine through `SensaHapticsService`, which reads `PeripheralOutputs.AmplitudeOf` for the row's id. `PeripheralOutputHost.SensaLifecycle` (`PeripheralOutputHost.cs` line 289) runs the worker only while the row is linked and assigned to a virtual controller, and starts a worker that ended on its own again after `SensaRestartMs` (30000), so a missing `HAR.dll` does not spin. [Sensa Haptics Internals](sensa-haptics-internals.md) covers the engine, the worker and the row.

### Remote Link

- The owner advertises rumble for a haptic mouse or keyboard. `InputService.BuildExposedDevices` (`InputService.cs` line 11518) sets `HasRumble` from the device or the row's recorded haptics bit, so the capability does not flap while the device sleeps. A consumer registers a device again when its rumble flag changes (`LinkServer.ReconcileRemoteDevices` (`LinkServer.cs` line 2162)).
- On the consumer, the forwarded mouse shows its Force Feedback tab through `IsHapticPeripheral`, and Step 2 ships its level back to the owner as it does for any forwarded device. The host never links a forwarded device to this PC's vendor channels.
- On the owner, `InputService.ApplyRemoteOutput` (`InputService.cs` line 11903) pays a resend a silence edge owed, records the relayed motors, and calls `SetMotors` with `relayed: true`.
- Vendor rows are not shared. `InputService.IsShareableDevice` (`InputService.cs` line 11706) refuses a `PeripheralOutputRow`, since it stands for this PC's vendor software and has no input.

### TouchSense mice

Logitech iFeel mice and other mice built on Immersion TouchSense have no path. Their vibration command is a 7-byte output report, `11 0A <strength> <delay> 00 <count> 00` in a BeOS iFeel tool (`ifeel-beos.cpp:25`) and the same bytes in the Linux ifeel driver (`ifeel.c:73`), with no report ID, so it belongs to the mouse's own top-level collection. Windows opens mouse collections for exclusive system use (Microsoft's table of top-level collections opened by Windows for system use), so a user-mode program cannot open one to write that report.

---

## Set Chroma Color

The macro action (#468), `MacroActionType.SetChromaColor` (`MacroItem.cs` line 6634), paints while it is current, the AxisHold duration shape.

1. `InputManager.ExecuteSequentialAction` (`InputManager.Step4b.EvaluateMacros.cs` line 2857) and its extended twin `InputManager.ExecuteSequentialActionRaw` (`InputManager.Step4b.EvaluateMacros.cs` line 5189) call `InputManager.NoteChromaColor` (`InputManager.Step4b.EvaluateMacros.cs` line 2828) with the macro's slot and color on every frame the action is current. Several macros current in one frame leave the last one evaluated, which is how a full-press macro listed below its soft-press twin wins at the bottom of the press.
2. `InputManager.EvaluateSlotMacros` (`InputManager.Step4b.EvaluateMacros.cs` line 463) and `InputManager.EvaluateSlotMacrosExtended` (`InputManager.Step4b.EvaluateMacros.cs` line 4499) end with `InputManager.FlushChromaColors` (`InputManager.Step4b.EvaluateMacros.cs` line 2837), which hands each slot's color for the frame to `MacroChromaSink` once, so a reader never sees the color flip between two macros within a frame. Each macro pass sends one color per controller.
3. The sink is `PeripheralOutputs.AssertChromaMacro` (`PeripheralOutputs.cs` line 596). It packs the tick shifted left 24 bits with the color into one `long` per slot, so one atomic read gives a matching pair. A first assertion, a new color, or one after the window lapsed raises `PeripheralOutputs.ChromaMacroChanged` (`PeripheralOutputs.cs` line 589), which wakes the Chroma worker alone. A held color asserted every frame raises nothing.
4. `PeripheralOutputs.TryGetChromaMacro` (`PeripheralOutputs.cs` line 619) reads a slot's color while its latest assertion is within `PeripheralOutputs.MacroAssertWindowMs` (`PeripheralOutputs.cs` line 580), 120 ms. The action asserts on every poll, a millisecond apart, so the window measures only the gap after the action ends.

`ChromaBackend.Wanted` (`ChromaBackend.cs` line 157) applies it. For each slot with a live macro, `PeripheralOutputs.DevicesOnSlot` (`PeripheralOutputs.cs` line 631) lists the devices assigned there, and every Chroma category linked to one of them takes the macro's color: the categories of the slot's Razer devices, which reaches every other Razer device of those kinds, or all six when the Razer Chroma row is on the slot. Links do not depend on the Lighting tab's switch, so the macro paints whether or not those tabs control the devices, over every claim on the category. Between two controllers' macros on one category, the smaller `PeripheralOutputs.DisplayedSlotNumber` (`PeripheralOutputs.cs` line 647) wins. A macro on a slot with no Razer device of a category leaves that category alone.

---

## The route line

`PeripheralRouteText` (`PeripheralRouteText.cs` line 16) builds the ember line on the Force Feedback and Lighting tabs, on the UI thread, from the link table, the backend states and the HID++ units. It replaced the Dashboard status lines the global switches carried. `PadPage.SyncTabVisibility` (`PadPage.xaml.cs` line 374) fills both lines. The page runs it again on `LinksChanged`, `StatusChanged` and `ClaimsChanged`, one sync per burst (`PadPage.OnPeripheralOutputsChanged` (`PadPage.xaml.cs` line 138)).

`PeripheralRouteText.Haptics` (`PeripheralRouteText.cs` line 20), for the Force Feedback tab:

| Condition | String |
|---|---|
| No haptic path, the Sensa row whose record has haptics, an x64 process | `Pad_ForceFeedback_RouteSensaWaiting` |
| No haptic path, the Sensa row whose record has haptics, an ARM64 process | `Common_NotAvailableOnArm64` |
| No haptic path, a Logitech row whose record has haptics | `Pad_ForceFeedback_RouteHidppAsleep` |
| A HID++ unit whose feedback is off | `Pad_ForceFeedback_RouteHidppFeedbackOff`, with the unit's name |
| A HID++ unit | `Pad_ForceFeedback_RouteHidpp`, with the unit's name |
| The tactile path while GG does not answer | `Pad_ForceFeedback_RouteGameSenseWaiting` |
| The tactile path, ruled by another Rival on a controller of this PC | `Pad_ForceFeedback_RouteGameSenseShared`, with that controller's number |
| The tactile path otherwise | `Pad_ForceFeedback_RouteGameSense` |
| The Sensa path while the backend state is `Waiting` | `Pad_ForceFeedback_RouteSensaWaiting` |
| The Sensa path otherwise | `Pad_ForceFeedback_RouteSensa` |

`PeripheralRouteText.Lighting` (`PeripheralRouteText.cs` line 108), for the Lighting tab, takes the slot and `lightsHere`: true for a vendor row, else the device's Control This Device’s Lighting switch on this slot. A device this controller leaves alone shows only who else lights it, never a route of its own. The path is the row's first lighting path, and the app is the vendor software behind a shared family (`PeripheralRouteText.LightingApp` (`PeripheralRouteText.cs` line 74)): Razer Synapse, Logitech G HUB (Logitech Gaming Software while `PeripheralPresence.LogitechGamingSoftware` holds) or SteelSeries GG. The first condition that holds picks the line. `PeripheralRouteText.CannotLight` (`PeripheralRouteText.cs` line 185) gives `Common_NotAvailableOnArm64` for an empty paintable list in the ARM64 build, and `Pad_Lighting_RouteCannotLight` otherwise.

| # | Condition | String |
|---|---|---|
| 1 | No lighting path, and this controller lights a Logitech row whose record has lighting | `Pad_Lighting_RouteAsleep` |
| 2 | The Logitech LIGHTSYNC row while `LedSdkPaintable` is an empty list | `CannotLight` |
| 3 | A vendor row whose software does not answer | `Pad_Lighting_RouteVendorRowWaiting`, with the app and the row's examples |
| 4 | A vendor row that rules none of its paths here while the same row on another controller rules one | `Pad_Lighting_RouteOtherController`, with that controller's number |
| 5 | Any other vendor row | `Pad_Lighting_RouteVendorRow`, with the app and the row's examples |
| 6 | An LED SDK type outside `LedSdkPaintable` | `CannotLight` when this controller lights it, else no line |
| 7 | The app does not answer | `Pad_Lighting_RouteWaiting` when this controller lights it, else no line |
| 8 | A vendor row rules the path | `Pad_Lighting_RouteSharedVendorRow`, with the app, the row's name and its controller's number |
| 9 | The same device on another controller rules it, or another row of the device on another controller rules its direct path | `Pad_Lighting_RouteOtherController` when this controller lights it, else `Pad_Lighting_RouteOtherControllerOnly`, with that controller's number |
| 10 | Another row of the same directly lit device on this controller rules it | `Pad_Lighting_RouteOtherRow` when this controller lights it, else `Pad_Lighting_RouteOtherRowOnly` |
| 11 | Another device on a shared path rules it | `Pad_Lighting_RouteShared`, with the app and that device's controller number |
| 12 | This controller does not light it | no line |
| 13 | A HID++ unit | `Pad_Lighting_RouteDirect`, with the unit's name |
| 14 | A shared path | `Pad_Lighting_RouteThrough`, with the app |

Rows 7 to 10 apply only to a ruling claim with a player number. The examples a vendor row names (`PeripheralRouteText.VendorRowExamples` (`PeripheralRouteText.cs` line 87)) are what its software lights that PadForge does not read: `Pad_Lighting_VendorRowExamples_Chroma`, `_LedSdk` and `_GameSense`. SteelSeries GG binds no mousepad type, so its row names headsets alone.

---

## The tabs and the switch

`PadPage.SyncTabVisibility` (`PadPage.xaml.cs` line 374) gives a device that `IsHapticPeripheral` accepts the Force Feedback tab and its route line (`PeripheralHapticsRoute`). A device with lighting by record or path and no Sony lightbar of its own gets the Lighting tab with the lightbar's mode card and `PeripheralLightingPanel`, without the DualShock 4 or DualSense art. The panel's Control This Device’s Lighting check box binds `DeviceConfig.PeripheralLightingEnabled` and hides for a vendor row, whose device type is `PeripheralLighting`.

`DeviceSlotConfig.PeripheralLightingEnabled` (`DeviceSlotConfig.cs` line 1003) is per (virtual controller, device) and off by default, so assigning a keyboard for its keys never repaints it. It is saved with the device's slot config, counts as a configuration on its own (`SettingsService.IsDeviceConfigConfigured` (`SettingsService.cs` line 2857)), and has a reset button.

---

## Migration of the Dashboard switches

The Dashboard's Lightbar Mirrors section, with its Razer Chroma (#373) and Logitech LIGHTSYNC (#382) toggles, and its Razer Sensa section (#374) are gone, along with `ChromaLightbarService` and `LightsyncLightbarService`. `PeripheralSwitchMigration` (`PeripheralSwitchMigration.cs` line 38) turns each switch that was on into an assignment of the row that replaced it.

Each switch had a global value and a nullable per-profile opinion, and profiles own their device assignments. `AppSettingsData.EnableChromaLightbar` (`SettingsService.cs` line 6696), `EnableSensaHaptics` (`SettingsService.cs` line 6704) and `EnableLightsyncLightbar` (`SettingsService.cs` line 6712), and their `bool?` twins `ProfileData.EnableChromaLightbar` (`SettingsService.cs` line 7662), `EnableLightsyncLightbar` (`SettingsService.cs` line 7668) and `EnableSensaHaptics` (`SettingsService.cs` line 7675), are read once and never written: each `ShouldSerialize` method returns false. `PeripheralSwitchMigration.Switches` (`PeripheralSwitchMigration.cs` line 49) lists them. The Sensa switch is `Available` only where `PlatformSupport.SensaAvailable` holds, so on ARM64 it assigns nothing and only clears.

`PeripheralSwitchMigration.Run` (`PeripheralSwitchMigration.cs` line 193):

- The live settings take the active profile's opinion, else the global value. A switch that was on calls `PeripheralSwitchMigration.AssignLive` (`PeripheralSwitchMigration.cs` line 223), which creates the row's record offline when the file has none (`PeripheralSwitchMigration.NewRowRecord` (`PeripheralSwitchMigration.cs` line 170), outputs bit set), assigns it to the live slot `SettingsService.LiveRulingSlot` (`SettingsService.cs` line 569) names, and gives it the setting a drag onto that slot gives.
- The default profile's stored state, while a named profile is active, and every stored profile take their own opinion, else the global value. A switch that was on adds an entry for the row on that profile's slot (`PeripheralSwitchMigration.AddToProfile` (`PeripheralSwitchMigration.cs` line 261)) with a default setting for the slot's controller type.
- Every opinion is cleared once read, and the switches are never written again, so the migration runs once per file.

The slot comes from `PeripheralSwitchMigration.RulingSlot` (`PeripheralSwitchMigration.cs` line 153):

| Row | Slot |
|---|---|
| Razer Chroma, Logitech LIGHTSYNC | The first created PlayStation slot in display order whose controller is a DualSense or DualShock 4 (`PeripheralSwitchMigration.FirstLightbarSlot` (`PeripheralSwitchMigration.cs` line 140)), since the mirrors showed only a lightbar color a game wrote to one of those. `PeripheralSwitchMigration.DecodesLightbar` (`PeripheralSwitchMigration.cs` line 130) takes a profile id that starts with `dualsense` or `dualshock-4`, or none, the PlayStation default, a DualSense |
| Razer Sensa | The first created slot in the group order the Dashboard walks (`PeripheralSwitchMigration.FirstDisplayedSlot` (`PeripheralSwitchMigration.cs` line 70)), the slot that shows the smallest player number |

A topology without the controller a row needs gets nothing. A stored profile's order is rebuilt the way applying the profile rebuilds the live one (`PeripheralSwitchMigration.DisplayOrder` (`PeripheralSwitchMigration.cs` line 94)): its saved order's created slots of the group, then the group's other created slots in ascending index. A migrated lighting row starts at Player Number, so it shows the game's lightbar as the mirror did, and the controller's player color while no game writes one.

`SettingsService.LoadFromFile` (`SettingsService.cs` line 244) runs the migration after `LoadProfiles`, the ghost-mapping guard and the motion backfill, since only from there on is the live topology the active profile's. A change sets `_peripheralSwitchesMigratedOnLoad`. `SettingsService.Initialize` (`SettingsService.cs` line 177) and `SettingsService.Reload` (`SettingsService.cs` line 5789) clear the dirty flag after a load and then mark the settings dirty again for it, so the migrated file is saved. `ProfileTransfer.Import` (`ProfileTransfer.cs` line 131) runs `PeripheralSwitchMigration.MigrateImported` (`PeripheralSwitchMigration.cs` line 63) on a profile file exported before #494, which carries opinions and no global value. Each assignment writes a `CFG #494 migrated ...` diag line.

---

## Threads

| Thread | Does |
|---|---|
| Poll thread | Phase 1m's rows, Step 2's `SetMotors`, Set Chroma Color's assertions |
| The effects dispatchers (their timer, config changes, the peripheral refresh) | `SetLighting` and the releases, under the device lock |
| HIDMaestro output reader | `GameLightbar.Capture` and `NoteFrame` |
| `PeripheralLink` | Presence, the link pass, the prune, the Sensa lifecycle |
| `PeripheralHidpp` | Every HID++ request and write but the crash path's hand-back. Answers arrive on each collection's `VendorHidReader` thread |
| `PeripheralGameSense` | Every GameSense call |
| Thread-pool tasks | Every Chroma REST call, every LED SDK native call |
| `SensaHaptics` | Every Interhaptics call |
| UI thread | The route lines, marshaled from `LinksChanged`, `StatusChanged` and `ClaimsChanged` |

Every setter on `PeripheralOutputs` is lock-free or takes only that class's own leaf state, so the poll thread and the dispatchers never wait on a backend's I/O. `PeripheralOutputs.SetBackendState` (`PeripheralOutputs.cs` line 254) raises `StatusChanged` only on a change. The events fire on any thread, and their owners marshal.

---

## ARM64

The Sensa row never opens in an ARM64 process: phase 1m and the linker both need `SensaPlatform`, and the migration only clears the Sensa switch. The LED SDK path loads whatever engine `ServerBinary` names, and an ARM64 process loads ARM64 libraries only, so that path works only where Logitech installs an ARM64 engine. The HID++, Chroma and GameSense paths are HID reports and local HTTP, with nothing native to load.

---

## Diag lines

| Line | When |
|---|---|
| `PERIPHERAL links: {rows} row(s), {paths} path(s)` | A link pass published a new table |
| `PERIPHERAL link pass fault: {type}` | A link pass threw |
| `PERIPHERAL Sensa worker started (row assigned)` | The Sensa row was assigned |
| `PERIPHERAL Sensa worker stopped (row unassigned)` | It left its last controller |
| `PERIPHERAL Sensa worker ended on its own, starting again later` | The worker ended while the row stayed assigned |
| `PERIPHERAL HID++ found '{name}' index=... type=... haptic=... mask=... rgb=... zones=... battery=... charge=...` | A unit was found |
| `PERIPHERAL HID++ '{name}' index=... has no haptics or RGB` | A unit has nothing to offer |
| `PERIPHERAL HID++ '{name}' lighting claimed` | A unit's lighting was claimed, the first time or after a hand-back |
| `PERIPHERAL HID++ '{name}' lighting handed back` | `[00 00]` went out |
| `PERIPHERAL HID++ '{name}' stopped answering` | A check found it asleep or gone |
| `PERIPHERAL HID++ write failed, dropping {path}` | A collection went away |
| `PERIPHERAL HID++ worker fault: {type}` | The worker threw |
| `PERIPHERAL LED SDK session open` | A session opened |
| `PERIPHERAL LED SDK handed back` | A session ended |
| `PERIPHERAL LED SDK load failed: {detail}` | `TryLoad` failed |
| `PERIPHERAL LED SDK engine cannot paint any claimed type` | The engine lacks the calls the claimed types need |
| `PERIPHERAL LED SDK calls failing, reinitializing` | The third failed liveness round |
| `PERIPHERAL LED SDK stop timed out after {n} ms, worker orphaned inside the SDK` | `Stop` timed out |
| `PERIPHERAL LED SDK waiting for the orphaned worker of the previous session to leave the SDK` | A new worker found a live orphan |
| `PERIPHERAL LED SDK worker fault: {type}` | The worker threw |
| `PERIPHERAL Chroma session for {categories}` | A session opened |
| `PERIPHERAL Chroma waiting for Synapse` | The init failed |
| `PERIPHERAL Chroma session lost` | A heartbeat or a call failed |
| `PERIPHERAL Chroma handed back` | Nothing is wanted any more |
| `PERIPHERAL Chroma effect rejected: {category ...}, retrying on the next poll` | A rejection that differs from the last one logged |
| `PERIPHERAL Chroma worker fault: {type}` | The worker threw |
| `PERIPHERAL GameSense bound` | A connect succeeded |
| `PERIPHERAL GameSense stopped answering` | A call failed |
| `PERIPHERAL GameSense handed back` | `stop_game` went out |
| `PERIPHERAL GameSense worker fault: {type}` | The worker threw |
| `CFG #494 migrated a global switch: {kind} row assigned to slot {n}` | The live settings took a row |
| `CFG #494 migrated a profile switch: {kind} row assigned to slot {n} in '{profile}'` | A stored or imported profile took a row |

---

## Tests

The facade's levels, claims and links are process-wide, so the classes that touch them share the `PeripheralOutputStatics` collection and run with nothing else.

| File | Test class | What it pins |
|---|---|---|
| `PeripheralOutputsTests.cs` | `PeripheralLinkingTests` | The ruling order, a claim with no player number, the shared-path flag, the table's indexes and comparison, unit-to-row matching, the Rival and Sensa paths, the recorded outputs, the vendor rows' identities and device types, phase 1m's Sensa condition |
| `PeripheralOutputsTests.cs` | `HidppUnitProbeTests` | Zones found by scanning for the static effect, 0x8071 preferred, the battery order and decode, the receiver's pairing table, incomplete units asked again, HID++ 1.0 errors, the long collections the worker opens |
| `PeripheralOutputsTests.cs` | `PeripheralOutputsFacadeTests` | A level kept without a path, the stronger motor, the silence edge and its resend, a relayed level through focus suspend, the haptic ruler, the Force Feedback route line, the Sensa row's level |
| `PeripheralOutputsTests.cs` | `HidppBackendTests` | The worker plays only a linked unit, stops, drops a failed path, reads a Bolt pairing table and asks only paired slots |
| `PeripheralOutputsTests.cs` | `GameSenseBackendTests` | The ruling Rival's level plays, the motor stops at once, GG gets the mice back after the release delay, the crash wait sees the zero |
| `PeripheralOutputsTests.cs` | `PeripheralSwitchMigrationTests` | The ruling slot, one entry per profile, each profile's own value, the live settings, the default topology, a row this PC cannot open, imported profiles, the lightbar slot, rebuilt orders |
| `PeripheralOutputsTests.cs` | `PeripheralWiringTests` | Source pins: Step 2's branch, every silence edge, the other writers, the Remote Link legs, the records before the table, the crash path's GameSense wait, the save after a migration on load |
| `PeripheralLightingTests.cs` | `PeripheralLightingTests` | Claims and the ruling, pruning, `ClaimsChanged`, the macro window and its wake, the charge, the linker's lighting rules, the route line, the game's lightbar phases and its trust gate, the DualSense order, the dispatcher lane and its timer, the HID++ claim, reassert and crash hand-back, GameSense colors, the switch's persistence, the mirror switches' migration |
| `LedSdkBackendTests.cs` | `LedSdkBackendTests` | A scripted `ILogiLedNative`: no load with nothing claimed, the session's call order, the whole-device call first and every type over it, engines without the target or zone call, the restore when a type leaves, the fail streak, a type that fails alone, a refused init, orphans |
| `ChromaBackendTests.cs` | `ChromaBackendTests` | The BGR integer and the init body, the result codes, the wanted categories, the Chroma row filling the rest, Set Chroma Color's precedence and window |
| `SetChromaColorMacroTests.cs` | `SetChromaColorMacroTests` | The assertion's slot, both macro loops asserting every frame, the last macro of a frame heard once, the duration, persistence, the editor |
| `HidppHapticsTests.cs` | `HidppHapticsTests` | The shaper's thresholds, interval and fallbacks, the frames and reply matching, the probe against scripted channels, the GameSense client against a local server, and `Live_ProbesTheRealHidppCollections`, which runs only with `PADFORGE_LIVE_HIDPP=1` |
| `SensaHapticsTests.cs` | `SensaHapticsTests` | The real Interhaptics engine, on [Sensa Haptics Internals](sensa-haptics-internals.md) |

---

## Related pages

- [Sensa Haptics Internals](sensa-haptics-internals.md): the Interhaptics engine behind the Razer Sensa row.
- [Logitech G-Keys Internals](logitech-g-keys-internals.md): the other Logitech library PadForge loads.
- [Remote Link Internals](remote-link-internals.md)
- [Input Pipeline](input-pipeline.md)
- [Lighting](../features/lighting.md) and [Force Feedback](../features/force-feedback.md): the tabs a lit or haptic peripheral shares with a gamepad.

---

*Last updated for PadForge 5.0.0.*
