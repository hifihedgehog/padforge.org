# Peripheral Outputs Internals

*How a mouse, keyboard, lit unit or vendor row assigned to a virtual controller takes that controller's lighting and rumble: the link table, the claims and their ruling, the backends that reach a vendor's software, the backends that write to one device at a time, the haptic paths, Set Chroma Color, the route line, and the migration of the retired Dashboard switches.*

The user-facing page is [Mice, Keyboards and Vendor Rows](../features/peripherals.md). This one is for whoever has to change the code. The Razer Sensa worker has its own page, [Sensa Haptics Internals](sensa-haptics-internals.md).

| File | Role |
|---|---|
| `PadForge.App/Common/Input/Peripherals/PeripheralOutputs.cs` | The hub: the link table, haptic levels, lighting claims and their ruling, Set Chroma Color, backend states |
| `PadForge.App/Common/Input/Peripherals/PeripheralLinker.cs` | Vendor software presence, the watch on running vendor programs, and the pure rules that link rows to output paths |
| `PadForge.App/Common/Input/Peripherals/PeripheralOutputHost.cs` | The link pass, the walk of the present HID collections, claim pruning, the backends' lifetimes, the crash path, the Sensa worker's lifecycle |
| `PadForge.App/Common/Input/Peripherals/PeripheralOutputRow.cs` | The four vendor rows, and `IOutputOnlyRow` |
| `PadForge.App/Common/Input/Peripherals/PeripheralUnitRow.cs` | The row of a lit unit no mouse or keyboard row reaches |
| `PadForge.App/Common/Input/Peripherals/PeripheralProductIds.cs` | Product IDs that name a Razer or SteelSeries device's kind |
| `PadForge.App/Common/Input/Peripherals/PeripheralLightingColor.cs` | One device's color for one slot |
| `PadForge.App/Common/Input/Peripherals/GameLightbarCapture.cs` | The game's lightbar, per virtual controller |
| `PadForge.App/Common/Input/Peripherals/PeripheralRouteText.cs` | The route line on the Lighting and Force Feedback tabs |
| `PadForge.App/Common/Input/Peripherals/HidppBackend.cs`, `HidppUnits.cs` | The HID++ worker, unit discovery, receiver pairing tables, the lighting probe, the battery decode |
| `PadForge.App/Common/Input/Peripherals/HidppLightPlan.cs` | The frames that claim, paint, hold and hand back each class of HID++ device |
| `PadForge.App/Common/Input/Peripherals/IDirectUnitBackend.cs`, `DirectBackends.cs` | The contract every direct backend keeps, its snapshots, and the one place the backends are made |
| `PadForge.App/Common/Input/Peripherals/LampArrayBackend.cs`, `LampArrayProtocol.cs`, `WindowsLightingState.cs` | The HID LampArray worker, its reports and descriptor checks, and whether Windows Dynamic Lighting lights a collection |
| `PadForge.App/Common/Input/Peripherals/RazerDirectBackend.cs`, `RazerDirectProtocol.cs`, `RazerDirectTable.cs`, `RazerGuard.cs` | The Razer worker, the 90-byte report, the product table, and the lock third-party Razer tools share |
| `PadForge.App/Common/Input/Peripherals/SteelSeriesDirectBackend.cs`, `SteelSeriesDirectProtocol.cs` | The SteelSeries worker, and the frames of each command family |
| `PadForge.App/Common/Input/Peripherals/TouchSenseBackend.cs`, `TouchSenseProtocol.cs`, `TouchSenseChannel.cs`, `TouchSenseWinUsb.cs`, `TouchSenseMouseDevice.cs`, `RealTouchSenseAccess.cs` | The iFeel rumble worker, its frames, the one WinUSB handle per mouse, the row that reads a bound mouse, and the test host's refusal |
| `PadForge.App/Common/Input/Peripherals/LedSdkBackend.cs` | The Logitech LED SDK worker |
| `PadForge.App/Common/Input/Peripherals/ChromaBackend.cs` | The Razer Chroma REST worker |
| `PadForge.App/Common/Input/Peripherals/GameSenseBackend.cs` | The SteelSeries GameSense worker |
| `PadForge.App/Common/Input/HidCollectionRuntime.cs`, `HidReportChannel.cs`, `RealHidAccess.cs` | The walk of every present HID collection, the bounded report channel, and the test host's refusal |
| `PadForge.App/Common/Input/HidppHaptics.cs` | The HID++ 0x19B0 frames, the HID++ channel, the per-path probe state |
| `PadForge.App/Common/Input/HapticRumbleShaper.cs` | Rumble strength to a waveform level and a repeat interval |
| `PadForge.App/Common/Input/UserEffectsDispatcher.cs` | The peripheral lane: each slot's claims on its lit devices |
| `PadForge.App/Common/Input/InputManager.PeripheralRows.cs` | Step 1 phase 1m: the vendor rows and the unit rows open and retire |
| `PadForge.App/Common/Input/InputManager.TouchSenseMice.cs` | Step 1 phase 1n: the rows of bound TouchSense mice |
| `PadForge.App/Common/Input/InputManager.Step2.UpdateInputStates.cs` | `ApplyForceFeedback`'s haptic-peripheral branch |
| `PadForge.App/Common/Input/InputManager.Step4b.EvaluateMacros.cs` | Set Chroma Color in both macro loops |
| `PadForge.App/Services/GameSenseClient.cs` | The GameSense HTTP calls |
| `PadForge.App/Services/LogiLedEngineNative.cs` | The LED SDK engine loader |
| `PadForge.App/Services/SensaHapticsService.cs` | The Interhaptics worker |
| `PadForge.App/Services/TouchSenseBinding.cs` | Which TouchSense mice are bound to WinUSB, and whether one declares the buzz report |
| `PadForge.App/Services/PeripheralSwitchMigration.cs` | The retired Dashboard switches become assignments |
| `PadForge.App/Services/InputService.cs` | The host's start and stop, the crash path, the Remote Link legs |
| `PadForge.App/ViewModels/DeviceSlotConfig.cs` | `PeripheralLightingEnabled`, `PeripheralClaimLevel` |
| `PadForge.App/Views/PadPage.xaml`, `PadPage.xaml.cs` | The tabs and their route lines |
| `PadForge.Tests/PeripheralOutputsTests.cs`, `PeripheralLightingTests.cs`, `DirectPathSeamTests.cs`, `DirectPathHostTests.cs`, `HidppLightPlanTests.cs`, `LampArrayBackendTests.cs`, `LampArrayProtocolTests.cs`, `RazerDirectBackendTests.cs`, `RazerDirectProtocolTests.cs`, `SteelSeriesDirectBackendTests.cs`, `SteelSeriesDirectProtocolTests.cs`, `TouchSenseBackendTests.cs`, `TouchSenseProtocolTests.cs`, `TouchSenseChannelTests.cs`, `TouchSenseMouseTests.cs`, `TouchSenseBindingTests.cs`, `LedSdkBackendTests.cs`, `ChromaBackendTests.cs`, `SetChromaColorMacroTests.cs`, `HidppHapticsTests.cs` | The benches |

---

## The model

A peripheral is a device row that shows a virtual controller's output on top of whatever input it has. Three kinds exist.

Device rows are the online mice, keyboards and analog keyboard rows (`PeripheralLinker.IsLinkable` (`PeripheralLinker.cs` line 1055)). The host always runs direct backends (`DirectBackends.Create`), so the link pass reads such a row of any vendor: a keyboard or mouse of any make can carry a HID LampArray collection. A Logitech `0x046D`, Razer `0x1532` or SteelSeries `0x1038` row can also be lit or rumbled through its vendor's own protocol or software. A row another PC forwards over Remote Link is left out, since that PC plays its outputs. A TouchSense mouse bound to WinUSB is no mouse to Windows any more, so PadForge reads it itself and gives it a mouse row (`TouchSenseMouseDevice`, under [TouchSense](#touchsense)).

Vendor rows stand for a vendor's software: they reach every device it lights or rumbles, the ones PadForge does not read included.

Unit rows stand for one lit device that no mouse or keyboard row reaches: a headset, a mousepad, a light strip, a monitor or a chassis light that Windows lists as a HID LampArray.

### Vendor rows

`PeripheralOutputRow` (`PeripheralOutputRow.cs` line 58) is a synthetic `ISdlInputDevice` with no inputs, in the shape of `LogitechGKeysDevice`: a fixed path, an id hashed from a fixed string, vendor ID `0x5046` ("PF"), and a two-letter product ID per kind.

| `PeripheralRowKind` | Name | Path | Product ID | Device type | Opens while |
|---|---|---|---|---|---|
| `RazerChroma` | Razer Chroma | `razerchroma://local` | `0x4348` ("CH") | `PeripheralLighting` (40) | Synapse's Chroma runtime is installed |
| `LogitechLightsync` | Logitech LIGHTSYNC | `logilightsync://local` | `0x4C53` ("LS") | `PeripheralLighting` | A Logitech LED engine is registered |
| `RazerSensa` | Razer Sensa | `razersensa://local` | `0x5345` ("SE") | `PeripheralHaptics` (41) | Synapse's Chroma runtime is installed and the process is x64 |
| `SteelSeriesGG` | SteelSeries GG | `steelseriesgg://local` | `0x5347` ("SG") | `PeripheralLighting` | GG is installed |

The enum (`PeripheralRowKind` (`PeripheralOutputRow.cs` line 12)) is append-only. Its values are never saved, but `PeripheralOutputRow.IdentityFor` (`PeripheralOutputRow.cs` line 124) hashes `pfrazerchroma`, `pflogilightsync`, `pfrazersensa` and `pfsteelseriesgg` into the rows' `InstanceGuid`s, which assignments and profiles store. The migration can assign a row that has never opened, so the id comes from the kind alone. Neither device type answers an any-device mapping source (`InputDeviceType.AnswersAnyDeviceSources` (`InputTypes.cs` line 170)), and the Devices page names them Lighting and Haptics.

`InputManager.UpdatePeripheralRows` (`InputManager.PeripheralRows.cs` line 41) is Step 1's phase 1m. It opens a row while `InputManager.PeripheralRowWanted` (`InputManager.PeripheralRows.cs` line 27) finds its software, retires it when the software goes, and opens it again on the next pass after the user removes it from the Devices page, the G-keys row's recreate pattern. The row does no I/O, so the poll thread runs all of this. `InputManager.RetirePeripheralRow` (`InputManager.PeripheralRows.cs` line 127) stops the row's haptic level and releases its lighting claims by id, since its record may already be gone.

### Unit rows

`PeripheralUnitRow` (`PeripheralUnitRow.cs`) has the vendor row's shape: a synthetic device with no inputs, vendor ID `0x5046` and device type `PeripheralLighting`. Where a vendor row takes every path of its family, a unit row holds the path of its one unit, and in the ruling it ranks as a device, never as a vendor row. Every unit row has product ID `0x4C55` ("LU"). `PeripheralUnitRow.IdentityFor` hashes `pfunit:`, the family's number and the unit's key in upper case into the row's `InstanceGuid`, so the same device on the same port is the same row in every session and keeps its assignment. Windows compares interface paths without regard to case, which is why the key is folded. The row's `ProductGuid` is hashed from the same identity and never from the model: `InputManager.FindOrCreateUserDevice` adopts a record found by product alone, and two lit units of one model would then trade assignments. The name is the unit's product string, or `LampArray VVVV:PPPP` where it gave none (`PeripheralUnitRow.NameFor`), and the path is `lightunit://` plus the id.

The link pass decides which units get a row and publishes them as `PeripheralOutputs.UnitRows` ([The linker](#the-linker)). `InputManager.UpdatePeripheralUnitRows`, the second half of phase 1m, opens a row for each listed unit and retires a row whose unit left the list: the device went, or a mouse or keyboard row reaches it now. A row the user removed from the Devices page comes back on the same pass while its unit is still listed, as a vendor row does. `InputManager.RetirePeripheralUnitRow` releases the row's lighting claims by id, so its backend hands the device back to its own effect.

A vendor row and a unit row both implement `IOutputOnlyRow` (`PeripheralOutputRow.cs`). Such a row is assigned for its output alone, so it lights with no Control This Device’s Lighting switch.

### Output paths and the link table

`OutputPath` (`PeripheralOutputs.cs` line 79) is a family and a key. A unit family reaches a single device. Every other family addresses a device class the vendor's software resolves, so `OutputPath.Shared` (`PeripheralOutputs.cs` line 85) is true for it. `Shared` names every family and throws for one it does not know, so a family appended later is refused until it is sorted. `OutputFamily` is append-only, because the backend states are an array indexed by its value.

| `OutputFamily` | Keys | Reaches |
|---|---|---|
| `HidppUnit` | The HID++ collection's path and the device index | One Logitech device |
| `ChromaCategory` | `keyboard`, `mouse`, `headset`, `mousepad`, `keypad`, `chromalink` | Every Razer device of the category |
| `LedSdkType` | `device`, `keyboard`, `mouse`, `mousemat`, `headset`, `speaker` | Every Logitech device of the type that G HUB or LGS lights |
| `GameSenseColor` | `mouse`, `keyboard`, `headset` | Every SteelSeries device of the type |
| `GameSenseTactile` | `tactile` | Every tactile Rival |
| `Interhaptics` | `sensa` | Every Sensa HD device |
| `RazerUnit` | The interface path of the device's control collection, the one the product table ranks first where a device shows several | One Razer device |
| `SteelSeriesUnit` | The interface path of the device's control collection | One SteelSeries device |
| `LampArrayUnit` | The interface path of the LampArray collection | One HID LampArray device |
| `TouchSenseUnit` | The mouse's WinUSB interface path | One TouchSense mouse, rumble only |

Each key has one producer and the linker copies it, so two paths to one unit are equal without any case folding.

`DeviceLinks` (`PeripheralOutputs.cs` line 96) holds one row's paths: `Lighting`, `Haptics`, the keys of the HID++ units it matched, and `CatchAll`, true for a vendor row. `DeviceLinks.HidppUnits` (`PeripheralOutputs.cs` line 105) lists the matched units whatever path lights the row, so Battery mode reads a Logitech device's charge while G HUB lights it. The direct paths added these members:

| Member | Says |
|---|---|
| `UnitRow`, `OutputOnly` | The row is a unit row, or either synthetic kind |
| `MaxClaimLevel` | The highest lighting hold any of the row's lit units offers: 0, 1 or 2 |
| `DirectWhenClosed` | The row is lit through its vendor's software now, and has a path of its own waiting for that program to stop |
| `Shadows` | The shared paths the row's own path stands in for. A shared backend leaves one of them unpainted while this row is painted on its own, so a directly lit Razer mouse is never painted by the Chroma session too |
| `HasVendorProgram` | The row is a Logitech, Razer or SteelSeries device, or the row of a unit of one. A path that lights it on its own is withdrawn when that vendor's program starts |

`LinkTable` (`PeripheralOutputs.cs` line 155) is an immutable snapshot of every row's paths, indexed `ByDevice` and `ByPath`. The link pass swaps it whole through `PeripheralOutputs.PublishLinks` (`PeripheralOutputs.cs` line 254), which bumps `LinkVersion` and raises `LinksChanged`, so a reader never sees half a pass. `LinkTable.SameAs` (`PeripheralOutputs.cs` line 192) compares two tables row by row, every member above included, so a pass publishes only a change, and a control that should appear or a shadow that should lift republishes the table.

### The recorded outputs

`UserDevice.PeripheralOutputs` (`UserDevice.cs` line 507) saves the bits of `PeripheralOutputKinds` (`PeripheralOutputs.cs` line 12) on the device record: 1 for haptics, 2 for lighting, 4 for a device that offers the first lighting hold above colors alone and 8 for one that offers the second, so the Lighting tab keeps its Lighting Hold choice while the device sleeps. The record keeps a row's Force Feedback and Lighting tabs up while the device sleeps or is unplugged, as a gamepad's tabs stay. Every haptic writer keys on `PeripheralOutputs.TakesHaptics` (`PeripheralOutputs.cs` line 269), the record's bit or a haptic path now, so a sleeping device keeps taking its level and plays the current one when it wakes.

---

## Presence and linking

### Presence

`PeripheralPresence` (`PeripheralLinker.cs`) says which vendor software is installed and which of it runs. It is read from the registry, files and process names, and never by opening an SDK, so an unassigned device costs nothing. `PeripheralPresence.ReadInstalled` reads what is installed, and the running flags come from one read of the running processes' image names (`PeripheralPresence.WithRunning`).

| Field | True when |
|---|---|
| `LogitechLedSdk` | The default value of `HKLM\SOFTWARE\Classes\CLSID\{a6519e67-7632-4375-afdf-caa889744403}\ServerBinary` names a file that exists |
| `LogitechGHubRunning` | A process named `lghub_agent`, `lgs` or `LCore` runs (`LogiLedEngineNative.HostProcesses`). The last two are Logitech Gaming Software's hosts |
| `LogitechGamingSoftware` | The host found is `lgs` or `LCore`, not `lghub_agent`. The Lighting tab then names Logitech Gaming Software as the program lighting Logitech devices |
| `RazerSynapse` | `RzChromaSDK64.dll` is in the system directory, or `HKLM\SOFTWARE\Razer Chroma SDK` exists |
| `RazerSoftwareRunning` | A process named `RazerAppEngine`, `Razer Synapse 3`, `Razer Synapse Service`, `Razer Synapse Service Process` or `RazerCentralService` runs (`PeripheralPresence.RazerHostProcesses`, from uncoil `apps/uncoild/src/conflicts.rs:20-24`). The Chroma SDK services of that table stay out: they keep running after Synapse is quit, and with them in the list a PC with Synapse installed would never light a Razer device on its own |
| `SteelSeriesGG` | GG's `coreProps.json` exists, or `Program Files\SteelSeries\GG` does |
| `SteelSeriesGGRunning` | A process whose name starts with `SteelSeriesGG`, `SteelSeriesEngine` or `SteelSeriesPrism` runs, in any case (`PeripheralPresence.SteelSeriesHostPrefixes`). No source lists every process of GG, so the match is by prefix. A name it takes in by mistake only closes the direct path |
| `SensaPlatform` | `PlatformSupport.SensaAvailable`: the process is x64 |

`VendorProgramWatch` (`PeripheralLinker.cs`) is the host's look at the running programs, and it has two reads.

- The full read, `VendorProgramWatch.Read`, runs at start and every `PresenceMs` (5000) on the link thread. It reads what is installed and the name of every running process (`RunningProcesses.ImageNames`).
- The fast read, `VendorProgramWatch.ReadRunning`, reads the running flags alone on every link pass while `PeripheralOutputs.WatchesVendorPrograms` holds: a claim resolves on a HID++, Razer or SteelSeries unit, or on a LampArray unit that a row with `HasVendorProgram` holds and Windows does not light, or a Set Chroma Color is live on a controller that holds a row lit through a Razer unit. A vendor program that starts is then seen within one link pass. At the presence interval the device's worker would keep writing, a re-asserted claim included, on top of the claim the program just made.

The fast read asks for the list of process IDs first (`RunningProcesses.ProcessIds`, one `K32EnumProcesses` call) and takes a snapshot only when that list differs from the one seen at the last snapshot. The names come from the list of process IDs and one limited query per process (`RunningProcessList`, `ProcessImage.PathOf`): 7 ms on a PC with 404 processes and 8,884 threads, where a Toolhelp snapshot took 358 ms of CPU and, taken every 5 s, held the link thread at 7 percent of a core. The list of IDs alone takes 0.02 to 0.05 ms. The IDs are read before the snapshot they go with, so a process that starts between the two shows as a list that moved on the next pass. A snapshot that fails leaves the running flags as they were (`PeripheralPresence.WithSnapshot`): read as nothing running, it would hand a running program's devices to a direct worker.

The host stores each read in `PeripheralOutputs.Presence` (`PeripheralOutputs.cs` line 298), which raises `StatusChanged` on a change. `PeripheralOutputHost.PublishPresence` stores it under the host's gate and only while the pass's run is not stopped, so a read that outlived a stop never replaces the next start's own.

### The linker

`PeripheralLinker.Build` (`PeripheralLinker.cs` line 500) is pure: rows and `LinkInputs` in, a `LinkTable` out. `LinkInputs` carries the HID++ snapshot, the presence, the units every direct backend found (`DirectUnit`: family, key, container, vendor and product ID, name, LampArray kind, `WindowsLit`, `MaxClaimLevel` and `Asleep`) and whether every direct backend has scanned once. A row that gets no path is left out of the table.

| Row | Haptic paths | Lighting paths |
|---|---|---|
| Razer Sensa row | `sensa`, with `SensaPlatform` | none |
| Razer Chroma row | none | All six Chroma categories, with `RazerSynapse` |
| Logitech LIGHTSYNC row | none | All six LED SDK paths, with `LogitechLedSdk` |
| SteelSeries GG row | none | The three GameSense color types, with `SteelSeriesGG` |
| Unit row | none | Its own unit, while the unit is listed awake, is not one that ignores a raw host, and its vendor's program does not run |
| Logitech device | Each matched HID++ unit that has haptics | One family, chosen below |
| Razer device | none | One family, chosen below |
| SteelSeries device | `tactile` for a tactile Rival, with `SteelSeriesGG` | One family, chosen below |
| A mouse or keyboard of any other vendor | none | The LampArray units that match it |
| The row of a bound TouchSense mouse | Its own TouchSense unit, while it is listed awake | none |

A device row takes one lighting family at a time, because two families would paint one device from two rulings. `Build` gathers what each family offers the row:

- `shared`, the path its vendor's software lights it through: the LED SDK type of each matched HID++ unit with an RGB feature when the LED SDK is registered, a Razer row's Chroma category with `RazerSynapse`, a SteelSeries row's GameSense type with `SteelSeriesGG`.
- `native`, the units of the device's own protocol: a matched HID++ unit with a light plan, or the Razer or SteelSeries unit of the same device.
- `lamps`, the LampArray units that match the row.

`PeripheralLinker.ChooseLighting` then picks, in the same order for every vendor:

1. The vendor's program runs: its shared path when its SDK is installed, and nothing else. The program drives every device of its vendor, and two programs driving one device fight over it (uncoil `apps/uncoild/src/conflicts.rs:34-37`, which tells its user to quit Synapse). `DirectWhenClosed` is set when the row would be lit on its own without the program, unless Windows lights it.
2. Windows Dynamic Lighting lights a LampArray unit of the device: the LampArray paths, which their backend leaves unpainted, and no native path. A device Windows lights has a second writer whichever door a color comes in by. Logitech's LampArray driver, which Windows Update installs, repaints a mouse over HID++ about twice a second, and a 0x8070 write beside it lasts one sample (OpenLogi issue 1129). The row keeps its tab, whose line names Windows and its switch.
3. The device's own protocol. For a Logitech device that is HID++ ahead of any LampArray unit: every reference that lights a 0x8071 or per-key Logitech device speaks HID++ to it, and OpenRGB keeps its LampArray detector off Logitech nodes (`LogitechControllerDetect.cpp:1771-1774`).
4. A LampArray unit of the device.
5. The shared path again for a Razer or SteelSeries row, so a model with no unit of its own keeps its tab and its waiting line. A Logitech row has no such step, since its LED SDK path is given only while G HUB or LGS runs.

The family is chosen as if every unit answered, and only the units that answer are linked. A unit listed asleep (`DirectUnit.Asleep`) counts toward the choice and gets no path, so a row whose own unit sleeps holds no path. Falling through to the shared path there would name the wrong wait on its tab. A Razer row lit through its own unit lists its Chroma category in `Shadows`.

A HID++ unit has a light plan when `HidppUnit.HasLightPlan` holds: feature 0x8070 with at least one static zone, feature 0x8071 with at least one cluster that lists the Fixed effect, or a per-key board whose 0x8070 the probe found behind its 0x8080 or 0x8081 (`HidppUnitProbe.DescribeLighting`). A unit with an RGB feature and no plan takes a lighting path through the LED SDK only.

A Razer, SteelSeries or TouchSense unit belongs to the rows of its own device: the same container, and the same vendor and product ID, which every collection of one USB device reports (`PeripheralLinker.MatchesDevice`). The pair also tells the built-in devices of a laptop apart, which share one container.

A LampArray unit and a row meet by container (`PeripheralLinker.MatchesLampArray`):

- The only LampArray unit in its container is that device's lighting, so it goes to every mouse and keyboard row of the device.
- In the PC's own container, `00000000-0000-0000-ffff-ffffffffffff`, which every built-in device reports, the only unit goes to the keyboard rows whatever kind it declares. The lit built-in device is the keyboard, and built-in arrays declare kinds their own tools call misleading (keybackcon `docs/architecture/protocol.md:24`).
- With several LampArray units in one container, a receiver or a device with several lit parts, kind 1 goes to the keyboard rows, kind 2 to the mouse rows, and any other kind to no row, since nothing else tells the units apart (LampArrayKind, HID Usage Tables 1.6, 26.2.1).
- A unit on `PeripheralLinker.LampArrayIgnoresRawHost` lights no row and gets none of its own. Its firmware takes a host's frames and keeps painting its own effect over them. The one entry is the keyboard of the Lenovo Legion Pro 5 16IAX10, 048D:C195 (hid-rgb-ctl issue 10).

`PeripheralLinker.Orphans` lists the LampArray units no mouse, keyboard or analog keyboard row reaches. A unit whose container is not known yet is not one, since its row may be a lookup away. Neither is a Logitech, Razer or SteelSeries unit while that vendor's program runs: the program drives such a device then, and the vendor's own row is how it is lit through it. `PeripheralLinker.HeldOrphans` passes on the units that have been orphans for `UnitRowHoldMs` (5000) without a break, and those get a row. A keyboard's row can come online a moment after its LampArray collection, and without the wait that keyboard would get a second row for the moment between.

A mouse reports a keyboard collection for keys bound to keystrokes, and a keyboard reports a mouse collection for keys bound to clicks, so Windows can list two rows for one device, and a row's own kind can name the wrong category. `PeripheralProductIds.LightsAsKeyboard` (`PeripheralProductIds.cs` line 78) decides by product ID where a list holds it: every `USB_PID` in openrazer's `mouse.py` and `keyboards.py`, the Aerox, Rival and Sensei detectors in OpenRGB's `SteelSeriesControllerDetect.cpp` with every `product_id` in rivalcfg's devices, and that file's Apex detectors. A device the lists lack goes by its row's kind. `PeripheralLinker.RazerCategory` (`PeripheralLinker.cs` line 1027) sends the keypads (the Nostromo and the Tartarus and Orbweaver families, openrazer `keyboards.py:74-273`) to `keypad`, and the Huntsman V3 boards openrazer does not list yet to `keyboard` through `AnalogKeyboardCatalog.IsRazerHuntsmanV3`. Every row of one device therefore lights as that device.

The tactile Rivals are the Rival 500, 700 and 710 (gamesense-sdk `standard-zones.md:49-52`), by rivalcfg's product IDs `0x170E`, `0x1700` and `0x1730` (`rival500.py:22`, `rival700.py:21` and `27`), which the linker keeps in `PeripheralLinker.RivalTactilePids` (`PeripheralLinker.cs` line 422). A Rival's keyboard collection is the Rival as well, so it takes the mouse color type and the tactile path.

A mouse or keyboard row is one Raw Input interface, and the device's HID++ channel is another collection of the same physical device. `PeripheralLinker.Matches` (`PeripheralLinker.cs` line 1066) pairs them by container ID: on the bench's LIGHTSPEED receiver the mouse (`MI_00`), keyboard and consumer (`MI_01`) and HID++ (`MI_02`) collections all report one. A receiver gives one mouse row and one keyboard row however many devices are paired to it, so a receiver's unit goes to the row of its own kind, from feature 0x0005's device type. A unit on device index `0xFF`, wired or Bluetooth, is the device itself and alone in its container, so it goes to every row of the device when it is a mouse or keyboard kind, and a remote or presenter there stays out. A unit that gave no type goes to every row in its container. `PeripheralLinker.LedSdkTypeOf` (`PeripheralLinker.cs` line 1040) names a unit's LED SDK type by its own kind, else by its row's.

`PeripheralLinker.Capabilities` (`PeripheralLinker.cs` line 1101) is what a row records: the kinds its links found, plus the kinds it had while its device may still be found. `PeripheralLinker.StillLooking` says when that is: a Logitech row before the HID++ worker's first scan or while its container has a slot left to ask, any device row until every direct backend has scanned once, and a row one of whose units is listed asleep. So a mouse asleep at launch keeps its tabs, and so does one a write just failed on. A vendor row is found by no scan and is never waited for.

`PeripheralLinker.HeldRows` adds the rows whose last unit left every backend's list less than `UnitGoneHoldMs` (5000) ago. A device that is unplugged loses its unit at the next walk of the present collections and its row at the input manager's next device scan, and either can come first. The link pass does not read an offline row, so a row held until that scan has come keeps its record and its tabs, as an unplugged gamepad's row does. The scan runs every 2000 ms (`InputManager.EnumerationIntervalMs`).

---

## The link pass

`PeripheralOutputHost` (`PeripheralOutputHost.cs` line 23) runs while the engine runs. `InputService.StartPeripheralOutputs` (`InputService.cs` line 10853) creates it at engine start, hands it `SlotHasController` (the input manager's `HasVirtualControllerAt`), subscribes to `CapabilitiesChanged`, and starts it. `InputService.StopPeripheralOutputs` (`InputService.cs` line 10864) disposes it at engine stop. There is no global switch. Every output follows assignment, the way a gamepad's does. Identify is the one exception: for the length of its train, the row it buzzes takes its shared haptic path (`PeripheralOutputs.BeginIdentify`).

`PeripheralOutputHost.Start` (`PeripheralOutputHost.cs` line 212) publishes `SlotHasController` as `PeripheralOutputs.SlotHasController`, sets `PeripheralOutputs.Running`, starts the HID++, GameSense, Chroma and LED SDK workers and each direct backend, reads presence, and starts the `PeripheralLink` thread. One direct family that cannot start keeps neither the others nor the link pass from running. The HID++ worker scans Logitech's HID++ collections from the start, since the linker needs its units, and each direct backend scans the list of present collections the host hands it, with nothing written to any device. Every backend reaches its vendor or its device only while an assigned device or row uses a path it serves, or while Identify buzzes a row on one.

`PeripheralOutputHost.Loop` (`PeripheralOutputHost.cs` line 334) reads presence every `PresenceMs`, and on the passes between reads the running programs alone while a vendor's program could take a device PadForge lights on its own ([Presence](#presence)). It then walks the present HID collections when a walk is due, runs one link pass and one Sensa lifecycle check, and waits `LinkMs` (500) on an event that `PeripheralOutputHost.Nudge` (`PeripheralOutputHost.cs` line 261) sets. The HID++ worker's `SnapshotChanged`, each direct backend's `SnapshotChanged` and `PeripheralOutputs.IdentifyChanged` nudge it, and so does `InputService.OnDevicesUpdated` (`InputService.cs` line 10228) through `PeripheralOutputHost.DevicesChanged`, so a device that comes or goes is linked at once, and Identify on the Razer Sensa row starts its worker inside the train.

### The walk

`HidCollectionRuntime.Enumerate` (`HidCollectionRuntime.cs`) lists every present HID top-level collection as a `HidCollectionInfo`: its path, vendor and product ID, usage page and usage, USB interface number and report lengths. It opens each path with no access right, which Windows grants on a mouse or keyboard collection too, and reads only what the HID class driver already holds, so no report and no string request goes to a device. `VendorHidRuntime.Enumerate` makes the same walk and cannot serve the direct backends: it drops every collection below usage page `0xFF00` and every collection with no input report, and nearly every Razer control collection sits on usage page `0x01` or `0x0C`.

`PeripheralOutputHost.RescanDirect` makes one walk and hands the list to every direct backend (`IDirectUnitBackend.Rescan`): on the first pass, every `RescanMs` (30000), and sooner when a walk was asked for, though never within `RescanFloorMs` (1000) of the walk before. Three things ask:

- A device row came or went (`PeripheralOutputHost.DevicesChanged`).
- Windows reported a HID interface arriving. `MainWindow.OnDeviceChangeMessage` passes the arrival on through `InputService.RequestPeripheralRescan`, which is how a lit device with no row of its own, a light strip or a headset, is found when it is plugged in.
- A backend's write to a unit failed (`IDirectUnitBackend.RescanRequested`), since the device may have left with no mouse or keyboard row to say so.

A device with several collections raises one arrival for each, a few milliseconds apart, and several backends can ask about one device. An ask inside the floor is kept and answered by the first pass after it, so one walk answers all of them. A walk that fails hands over nothing and is made again on the next pass, so a failed SetupAPI call never reads as every device unplugged.

### One pass

`PeripheralOutputHost.Link` (`PeripheralOutputHost.cs` line 501), one pass:

1. Read presence and the HID++ snapshot, and note whether any unit's charge changed (`PeripheralOutputHost.ChargesChanged` (`PeripheralOutputHost.cs` line 692)). Read each direct backend's snapshot once (`PeripheralOutputHost.ReadSnapshot`), so its units and its scan state are of one scan. A read that throws or gives none counts as not scanned with no units for that pass, which keeps every device row's recorded outputs, and is logged once per backend.
2. Under the device list's lock, take each online vendor row, each online unit row and each linkable device row. A forwarded row is skipped.
3. Outside that lock, look up each device row's container ID (`PeripheralOutputHost.ResolveContainer`, through `AudioPassthroughService.DevicePathContainerId`), cached per path once it answers, since each lookup is a kernel round trip. A failed lookup is asked again on the next pass, and a path no row used this pass is forgotten (`PeripheralOutputHost.ForgetContainers`). The path was taken under the lock by `PeripheralOutputHost.ContainerPath` (`PeripheralOutputHost.cs` line 441): the row's device path, or for an analog keyboard row, whose device path is a synthetic `analogkb://` key, the HID collection the row reads, so a Logitech analog keyboard reaches its HID++ unit.
4. Build the table, and list the LampArray units no row reaches (`PeripheralLinker.Orphans`).
5. Prune the lighting claims (below), reading the assignments under the settings lock, never nested inside the device lock.
6. Take the host's gate for the rest of the pass. A pass that finds its run stopped, which `Stop` marks under the same gate, ends here and publishes nothing. Otherwise publish the HID++ snapshot as `PeripheralOutputs.Hidpp`, the direct units as `PeripheralOutputs.Direct` (a `DirectSnapshot`: the units, the families served in this engine run, and whether every backend has scanned once), and the held orphans as `PeripheralOutputs.UnitRows`. Then write each row's recorded outputs. They land before the table, so a tab that refreshes on the new table reads the record that goes with it. The orphans' clock and the rows' hold are kept under the gate, past the stop check, so a pass `Stop` gave up on never moves either under its successor.
7. Publish the table when it changed, with a `PERIPHERAL links:` diag line, or raise `StatusChanged` when only a record moved or a slot started or stopped being live, which changes what the tabs' route lines say.
8. Raise `CapabilitiesChanged` when a record moved. `InputService.OnPeripheralCapabilitiesChanged` (`InputService.cs` line 10884) marks the settings dirty and resyncs the Devices page, whose rumble chip reads the record.
9. Ask the dispatchers for a peripheral refresh: every slot, lit or not, after a relink, so a new path reaches a slot whose last pass lit nothing, or the lit slots after a charge changed, for Battery mode.

`PeripheralOutputs.PruneClaims` (`PeripheralOutputs.cs` line 686) drops every claim whose (device, slot) is no longer an assignment, and every claim on a slot that is not live. A slot is live while it has a live effects dispatcher (`UserEffectsDispatcher.HasLiveDispatcher` (`UserEffectsDispatcher.cs` line 1212)) or still holds a virtual controller (`SlotHasController`). `PeripheralOutputs.SlotLive` is that rule, and the prune and the tabs' route lines both read it. The prune runs under the settings lock its assignment snapshot was read under, so an assignment made during the pass keeps its claim. Unassigning a device runs no pass on its old slot's dispatcher, and a slot whose controller went away has no dispatcher at all, so without the prune a claim would hold its device on a color nobody sets. A reorder moves the controllers first and rebuilds the slots' dispatchers one at a time afterward. The controller test keeps a slot's claims through that rebuild, so its devices are never handed back and taken again. The dispatcher's own disposal releases nothing for the same reason.

`PeripheralOutputHost.Stop` (`PeripheralOutputHost.cs` line 296) marks the link pass's run stopped under the host's gate and waits `StopJoinMs` (3000) for the pass, so a pass that outlives the wait publishes nothing, starts no Sensa worker, and makes no further call on a backend. It then stops the Sensa worker, the direct backends in the reverse of their start order, and the LED SDK, Chroma, GameSense and HID++ workers, each of which hands its devices back before it closes them. It clears `PeripheralOutputs.Running` and `PeripheralOutputs.SlotHasController`, clears every claim, and publishes an empty table, an empty HID++ snapshot, an empty direct snapshot and no unit rows, so nothing claimed carries into the next engine start.

---

## Claims and the ruling

Lighting is claimed per (device, slot). One dictionary, `PeripheralOutputs.s_claims` (`PeripheralOutputs.cs` line 598), maps each pair to the slot's displayed player number, the color and the lighting hold. A mouse on two virtual controllers holds one claim from each, and the ruling picks between them the way it picks between two devices on a shared path, so two dispatchers never take turns repainting it.

| Call | Does |
|---|---|
| `PeripheralOutputs.SetLighting` (`PeripheralOutputs.cs` line 625) | Adds or updates the claim. Any change bumps `LightingVersion` and raises `LightingChanged`, which wakes every lighting worker. `ClaimsChanged` fires only when a claim starts or its player number or hold changes |
| `PeripheralOutputs.ReleaseLighting` (`PeripheralOutputs.cs` line 660) | Drops one slot's claim. The same device's claim from another slot stays |
| `PeripheralOutputs.ReleaseDevice` (`PeripheralOutputs.cs` line 669) | Drops every claim on a device that went offline, retired or was removed |
| `PeripheralOutputs.PruneClaims` (`PeripheralOutputs.cs` line 686) | The link pass's prune |
| `PeripheralOutputs.ClearClaims` (`PeripheralOutputs.cs` line 703) | The host's stop |

`ClaimsChanged` never fires for a color alone, so a tab naming the controller that rules a shared path follows it without redrawing at animation speed.

`PeripheralOutputs.Rules` (`PeripheralOutputs.cs` line 743) is the ruling, pure so it is testable. Claimant `a` rules claimant `b` by the first of these that differs:

1. A device's own claim beats a vendor row's, whatever the numbers.
2. The smaller displayed player number. A claim with none (0 or less) reads as `int.MaxValue`, so it never beats a numbered one.
3. The lower slot index.
4. The lower device id, so the answer never flips between two equal claims, such as two rows of one device on one slot.

`PeripheralOutputs.TryResolveColor` (`PeripheralOutputs.cs` line 758) returns false when the path is not in the table or nothing claims it, which is a backend's cue to hand the device back to its own software. It counts only a claim whose row links that path, and it returns the ruling claim with the color, for a tab that names the controller whose color shows. The smallest displayed player number is the precedence `InputService.ApplyGuideLeds` gives the Steam Controller's process-wide home LED.

The ruling claim also carries its lighting hold, `Claimant.Level`: 0 for colors alone, 1 for the device's lighting power too, 2 for its on-board memory mode off as well. The hold never ranks a claim. It travels with the claim because a claim outlives a change of path and a backend reads the link table on its own tick: looked up anywhere else, an old claim could meet a new path at a hold its slot never chose. A backend holds a unit at the smaller of the ruling claim's hold and what the unit offers.

The haptic backends have no claims to read a player number from. `PeripheralOutputs.TryResolveHapticRuler` (`PeripheralOutputs.cs` line 1027) runs the same `Rules` over the devices linked to a shared haptic path, ranked by `PeripheralOutputs.HapticRulingPlayer` (`PeripheralOutputs.cs` line 1011): the device's smallest displayed player number among its assignments (`SettingsManager.SlotOrders.GetIdentityPlayerNumber`), else `PeerDrivenPlayer` (1000) when a Remote Link peer wrote its rumble last, else 0, which never rules by rank. A Rival a linked PC drives therefore ranks after every controller on this PC. A row Identify buzzes (`PeripheralOutputs.BeginIdentify`) rules the path for its train ahead of every rank, and of two such rows the one whose claim lapses later rules.

---

## Lighting from the slot

The slot's effects dispatcher, which already lights a DualSense, lights the slot's mice, keyboards and vendor rows too. `UserEffectsDispatcher.DispatchSnapshot` (`UserEffectsDispatcher.cs` line 1851) walks the slot's assigned devices under the device list's lock. A device that is not a DualSense or DualShock 4 and that `UserEffectsDispatcher.IsLitPeripheral` (`UserEffectsDispatcher.cs` line 1783) accepts, by its record or a lighting path now, goes to `UserEffectsDispatcher.LightPeripheral` (`UserEffectsDispatcher.cs` line 1808) instead of an effect report. An offline one releases this slot's claim.

`LightPeripheral` takes the device's own config for the slot and never the slot's anchor config, whose switch and mode are another device's. With no config of its own yet, or for a device row whose `PeripheralLightingEnabled` is off, it releases this slot's claim, and this controller no longer lights the device. A vendor row or a unit row ignores the switch (`IOutputOnlyRow`), since lighting is all it carries. Otherwise the color comes from `PeripheralLightingColor.Resolve` (`PeripheralLightingColor.cs` line 21) with the slot's game lightbar, the audio peak scaled by the device's own sensitivity, the input-reactive pulse, and the charge from `PeripheralOutputs.BatteryOf` (`PeripheralOutputs.cs` line 989), or 100 when it is unknown, which holds Battery mode at its full-charge color. The color goes to `SetLighting`, ranked by the slot's displayed player number (`GetGlobalSlotNumber`, or the slot index plus one for a slot in no order list), with the device's Lighting Hold as the claim's hold. The switch and the hold are read together (`DeviceSlotConfig.PeripheralLightingClaim`, one field with the switch in bit 8 and the hold in the low byte), because a load writes them one after the other on the UI thread and this pass can run on the timer's. A vendor row or a unit row asks for colors alone whatever its config holds. Every call there is a leaf. The I/O belongs to the backends, because the poll thread needs this lock every cycle.

### The color

`PeripheralLightingColor.Resolve` keeps the DualSense's order (`Ds5EffectSynthesizer.BuildFields`):

1. A lightbar the game wrote within the grace window wins over every setting, a macro color included.
2. Past the window, a device left at the defaults keeps the game's last color: Player Number, no input-reactive overlay, no live macro lightbar override. That is the stand-down the DualSense makes so a game that sets the bar once is not overwritten 1.5 seconds later (#191).
3. Anything else goes through `Ds4EffectSynthesizer.ResolveLightbarRgb`, the color core every lit device shares, so the whole mode set works: Player Number, Static, Breathing, Strobe, Rainbow, Color Cycle, Battery, the six audio modes, the input-reactive overlay and the macro lightbar override.

Player Number shows this slot's own player color, since each slot holds its own claim and the ruling picks the claim from the smallest displayed number. The Sony lane's lowest-raw-index owner rule is not used here, because it can disagree with the displayed numbers.

`UserEffectsDispatcher.OnAssignmentSetObserved` (`UserEffectsDispatcher.cs` line 535) releases the claim of a device that left the slot and, except on a new dispatcher's first look, forgets the slot's game color, the DualSense mirror's rule for an assignment change. A reorder rebuilds a slot's dispatcher after moving its controller's game color there, which is why the first look keeps it.

`UserEffectsDispatcher.LightingDriven` (`UserEffectsDispatcher.cs` line 1314) decides whether a device's config keeps the slot's animation timer running. A device with a lighting path drives it when it is a vendor row or a unit row (`DeviceLinks.OutputOnly`) or its switch is on. A peripheral with no path now, asleep or offline or with its vendor's software closed, follows what the slot's last pass saw: an online mouse or keyboard follows its switch, and a vendor row, a unit row or an offline device drives nothing. Every other device keeps the old rule. `UserEffectsDispatcher.OnConfigChanged` (`UserEffectsDispatcher.cs` line 1215) checks the timer again when the switch flips.

### The peripheral lane

Some of what a peripheral shows changes outside its slot: the game's lightbar, a charge, a new path. `UserEffectsDispatcher.RequestPeripheralRefresh` (`UserEffectsDispatcher.cs` line 1117) asks the slot's dispatcher for a pass over its lit peripherals alone. A slot that lit nothing last pass costs nothing, unless the request says `evenUnlit`. One refresh runs at a time on the thread pool, at most once per animation tick (33 ms), and requests that arrive while it runs fold into one more. `UserEffectsDispatcher.RunPeripheralRefresh` (`UserEffectsDispatcher.cs` line 1138) calls `DispatchSnapshot(peripheralsOnly: true)`, which writes no Sony effect report and no web pad or PS Move color. A game that animates its lightbar every frame reaches the peripherals at the dispatcher's own cadence, and the HIDMaestro output reader that reports the color never waits. `UserEffectsDispatcher.RequestPeripheralRefreshAll` (`UserEffectsDispatcher.cs` line 1169) asks every slot.

---

## The game's lightbar

`GameLightbar` (`GameLightbarCapture.cs` line 22) is the color a game writes to one virtual PlayStation controller. Each `HMaestroVirtualController` owns one, so the color moves with the controller when a reorder retargets it, the way its inbound rumble pack does.

The `OutputDecoded` handler that `HMaestroVirtualController.RegisterFeedbackCallback` (`HMaestroVirtualController.cs` line 1417) installs feeds it from the controller's output reader thread. Only a frame the trust gate accepts counts: the declared report length and a valid checksum (`HMaestroVirtualController.SonyFrameValid` (`HMaestroVirtualController.cs` line 2031)). The profile codec decodes a `lightbar` rgb24 field for the DualSense and the DualShock 4 alike, and the family's validity bit says whether this write carries it: `validFlag1 & 0x04` on a DualSense or DualSense Edge, `validFlag0 & 0x02` on a DualShock 4 (SDL's `k_EPS4EffectLED`). A valid write goes to `GameLightbar.Capture` (`GameLightbarCapture.cs` line 38). Any other trusted frame goes to `GameLightbar.NoteFrame` (`GameLightbarCapture.cs` line 53), which says the game is still there. The Chroma and LIGHTSYNC mirrors this replaced read the field before the gate, so a corrupt Bluetooth frame could paint a keyboard.

| Phase | When | What a lit device shows |
|---|---|---|
| `Fresh` | Within `GraceMs` (1500) of the last write | The game's color, over every setting |
| `Held` | Past the grace window while the game still sends trusted frames | The game's last color on a device left at the defaults, its own mode otherwise |
| `None` | No write yet, cleared, or `LapseMs` (15000) after the later of the last write and the last trusted frame | Its own mode |

`GraceMs` is the DualSense mirror's `ExternalSubsystemGraceMs` and `LapseMs` its `ExternalClaimLapseMs`. The next `NoteFrame` clears a lapsed record rather than reviving it, so a second game that never writes the bar does not bring back the first game's color. `Capture` returns true on a new color or on a write after the grace window closed, and the reader thread then queues the slot's refresh (`GameLightbarCapture.NotifyChanged` (`GameLightbarCapture.cs` line 208)).

`GameLightbarCapture` (`GameLightbarCapture.cs` line 137) maps slots to sources. `HMaestroVirtualController.PrepareDeviceEffectsForPublication` (`HMaestroVirtualController.cs` line 576) publishes a Sony controller's source once it wins its slot, `HMaestroVirtualController.RetargetToPad` (`HMaestroVirtualController.cs` line 654) moves it, and `HMaestroVirtualController.UnregisterFeedback` (`HMaestroVirtualController.cs` line 1409) and `HMaestroVirtualController.Disconnect` (`HMaestroVirtualController.cs` line 516) withdraw it. `GameLightbarCapture.Withdraw` (`GameLightbarCapture.cs` line 167) clears a slot only while it still holds that source, so in a two-pad swap the controller that already took the other's place keeps it. A dispatcher computes colors only when it runs, and a slot whose devices are not animated may not run again for a long time, so a timer every `WatchMs` (250) runs while any controller is registered and asks for a refresh when a slot's phase moves to `Held` or `None`. The capture reports `Fresh` itself.

---

## The HID++ backend

`HidppBackend` (`HidppBackend.cs` line 114) is one `PeripheralHidpp` thread that owns every HID++ collection, so a probe, a haptic pulse and a color never interleave on one channel.

### Collections and the channel

`HidppBackend.IsHidppLong` (`HidppBackend.cs` line 339) takes Logitech's vendor ID, a 20-byte input report, and usage page `0xFF00` usage 2 (mice and receivers), or `0xFF43` usage `0x0602` (keyboards, OpenRGB `LogitechControllerDetect.cpp:162-166` and `1530`) or `0x0202`: the headsets OpenRGB registers over USB (`1553` and `1763-1768`) and the devices paired over Bluetooth LE, which OpenLogi lists on that usage (`crates/openlogi-hid/src/transport.rs:181-183` and `198-202`, HIDPP_LONG_COLLECTIONS). OpenRGB's HID++ 2.0 detector takes page `0xFF43` over Bluetooth with any usage (`1783-1784` and `1795`). The 64-byte usage `0x0604` and the Centurion page `0xFFA0` stay out. `HidppChannel` (`HidppHaptics.cs` line 309) opens that collection shared and reads it on a `VendorHidReader` thread, so Logi Options+ and other HID++ clients keep their own reports, and writes through `RawHidOutput.Write`. Every frame on the long collection is a long report, because Windows splits HID++ short and long reports into two collections and the long one rejects 7-byte writes, which is why OpenRGB forces long frames on Windows (`LogitechHIDPP20Controller.cpp` SendStandard).

One request is in flight at a time, the worker's. `HidppChannel.Request` (`HidppHaptics.cs` line 458) retries a HID++ 2.0 busy answer (`0x08`) once after 50 ms, OpenRGB's retry on busy. HID++ 1.0's `0x08` is `UNKNOWN_DEVICE` and is never retried. The answer window is 300 ms, or 700 ms on a Bluetooth path, one whose interface path carries the HID service UUID `00001812-0000-1000-8000-00805f9b34fb`, OpenRGB's first-contact and Bluetooth budgets.

### The loop

`HidppBackend.Worker` (`HidppBackend.cs` line 373) first waits up to `PredecessorJoinMs` (5000) for a worker that a timed-out `Stop` left inside a probe, since that worker still holds the collections, and starts anyway when the wait runs out. Each pass plays haptics, paints lighting, then scans when a scan is due and, while a unit is linked for rumble, nothing has played for `QuietMs` (1000), so a probe does not hold up rumble that comes in bursts. A check runs every `CheckMs` (30000) once nothing has played for `QuietMs` (1000). Neither a scan nor a check starts while a claim or a paint is still going out. The wait between passes is `ActiveTickMs` (10) while a row linked to a unit holds a level above zero and `IdleTickMs` (100) otherwise, `FrameTickMs` (8) at most while a lighting frame waits to go out, and `HapticsChanged` and `LightingChanged` cut it short. A request that waits for its answer lets the pulses that came due go out beside it (`HidppWaiter`), so a slot that never answers costs rumble one tick and not its timeout.

### Discovery

`HidppBackend.Scan` (`HidppBackend.cs` line 1231) enumerates the vendor collections, drops paths that vanished, and keeps a `HidppPathState` per path, so a scan asks again only what is still open. It looks up each present path's container ID once. A lookup that fails is asked again at the next scan, and the units already found on the path take the container once it answers. A receiver known by its product ID (`HidppReceiverProtocol.KindOf` (`HidppUnits.cs` line 517): Bolt `0xC548`, and the Unifying and LIGHTSPEED receivers from Solaar's `base_usb.py:149-178`) has its pairing table read at every scan, so a device paired since the last scan is found. The table is HID++ 1.0 long register `0x2B5` (request `0x83B5`, Solaar `hidpp10.py:56-60`), one record per slot, at sub-register `0x20` plus the slot minus one on Unifying and LIGHTSPEED and `0x50` plus the slot on Bolt (Solaar `receiver.py:266-276` and `502-503`). The request goes out short on the receiver's short collection (usage 1), found by OpenRGB's path key (`HidppReceiverProtocol.ShortSibling` (`HidppUnits.cs` line 563)), and the record comes back long on the collection the worker already reads. `HidppUnitProbe.ReadPairing` (`HidppUnits.cs` line 688) takes a record as a paired device, asleep or not, and an error as an empty slot only when the same read errs twice, since another program reading the register at that moment could hand this read its error. An unanswered read stops the pass, and after `PairingGiveUp` (3) such passes in a row the table is not read again. A read that never went out, on a channel without the receiver's short collection or one whose short write failed, stops the pass and counts toward nothing.

`HidppUnitProbe.Probe` (`HidppUnits.cs` line 609) then asks the slots: device index `0xFF` first on a path that is not a known receiver, then receiver slots 1 to 6 unless `0xFF` answered. A Bluetooth path is the device itself and has no slots. A slot is alive once Root answers for feature 0x0005. A receiver's HID++ 1.0 `INVALID_SUB_ID` for a slot means its device speaks only HID++ 1.0, and the slot settles. Any other HID++ 1.0 error, a busy answer, or no answer at all backs off 5, then 10, then 15 seconds. `HidppUnitProbe.Describe` (`HidppUnits.cs` line 819) reads the rest of a live unit:

- The device type, feature 0x0005 function 2, by Solaar's table (`hidpp20_constants.py:251-260`): 0 keyboard, 1 remote, 2 numpad, 3 mouse, 4 touchpad, 5 trackball, 6 presenter, 7 receiver. Then the name, read the way Solaar's `get_name` reads it.
- The 0x19B0 capabilities and configuration (below).
- The RGB feature: the first of 0x8071, 0x8081, 0x8080 and 0x8070, in that order, that the device has. For 0x8070, `HidppUnitProbe.StaticZones` (`HidppUnits.cs` line 1193) walks the zones and keeps those that list the static effect, found by scanning for effect ID `0x0001`, never by a fixed index, which differs between models.
- The battery feature, 0x1004 before 0x1000.
- For a unit whose first RGB feature is not 0x8070, `HidppUnitProbe.DescribeLighting` reads the rest of its lighting after everything above, so the first pass and its order stay what they were. On a 0x8071 device it looks up 0x8081, walks the clusters for the Fixed effect, reads the zone bounds of a 0x8081 found, and on a keyboard with both walks the multi-cluster effects for Host streaming (effect ID `0x0013`). It then looks up the feature that switches the on-board memory mode, 0x8101 before 0x8100, the order OpenRGB and Solaar test them in (`LogitechHIDPP20Controller.cpp:3978-3998`, `settings_templates.py:3334-3337`). On a board whose first RGB feature is a per-key one it looks up 0x8070 and walks its zones, since every known board with 0x8080 lists 0x8070 too (g810-led `Keyboard.cpp:911-937`). The unit ends with its effect feature and its per-key feature as separate pairs, each with its own index.

A request that decides an output and goes unanswered marks the unit incomplete. Its slot backs off and is asked again in full, rather than keeping a device whose zones or type are missing. A unit with neither haptics nor an RGB feature is not kept, since a charge alone feeds only a lit device.

After a scan, the next one comes in `FirstScanMs` (5000) while some slot still waits for its device, or when the scan dropped a path with a unit that is owed its hand-back, else in `RescanMs` (30000). `HidppBackend.Check` (`HidppBackend.cs` line 1386) asks each found unit something cheap: its 0x19B0 configuration, or Root's lookup of 0x0005 for a unit without haptics. A unit that answers refreshes its feedback flag and its charge. One that does not went to sleep or away: it leaves the list, its slot reopens, and the next scan comes within 5 seconds. A failed write drops the whole path.

`HidppSnapshot` (`HidppBackend.cs` line 11) publishes the units, the containers with a slot still open (`PendingContainers`), and `Scanned`, false until the first scan ran, so nothing the worker has not looked for reads as missing.

### Direct lighting

`HidppBackend.PaintLighting` (`HidppBackend.cs` line 488) lights each unit that has a light plan, while a row links its path and a claim resolves on it. The linker gives these paths only while neither G HUB nor LGS runs and Windows Dynamic Lighting does not light the device.

`HidppLightPlan` (`HidppLightPlan.cs`) holds the frames for one unit as pure lists: what takes the lighting from the device's own effect, what paints a color, what holds the claim, and what hands the device back. `HidppLightPlan.For` picks one of four by the features the device lights through. No plan builds a frame that writes the device's memory.

| Plan | Features | Claim | Paint |
|---|---|---|---|
| `ZonePlan` | 0x8070 alone | SetSWControl `[01 01]` (function 8, `HidppUnitProtocol.SetSwControl` (`HidppUnits.cs` line 241)) | The static effect on each zone (function 3, `HidppUnitProtocol.SetStaticColor` (`HidppUnits.cs` line 231)): the zone, the static effect's index, R, G, B, and `0x02`, OpenRGB's fixed-color marker, or `0x00` for black (`LogitechHIDPP20Controller.cpp:5647-5663`) |
| `ZonePerKeyPlan` | 0x8070 with 0x8080, the G810 class | The same | The zone effects, then fills of the indicators and the media keys through 0x8080 and its commit, the frames Logitech Gaming Software sends for a fixed color (g810-led-resources `dumps/g810-spectrum/set_fx_color_00ff00.pcapng`). Black also fills the keys, the G-keys and the logo, since the static effect with no color marker leaves the buffer as it stands |
| `ClusterPlan` | 0x8071 alone | manageSwControl, by the hold | The Fixed effect on each cluster |
| `ClusterStreamPlan` | 0x8071 with 0x8081, on a keyboard | The same | The cluster effect lights the main board only (g915x-heatmap `PROTOCOL.md:97`), so the color also goes to every zone through 0x8081. A first paint sets each cluster, chooses the Host streaming effect when the keyboard lists one, then sends one range over every zone and the frame end, twice, since the first per-key frame after a claim can land before the firmware has let go (Solaar `settings_templates.py:4089-4093`). A later paint is the range and the frame end alone |

A mouse with 0x8071 and 0x8081 stays on `ClusterPlan`. The one such mouse known, the G502 X PLUS, answers with a single cluster.

#### The hold

The lighting hold is how firmly a 0x8071 device is held while it is lit. Only that class has holds above 0. The tab's Lighting Hold picker chooses it (`PeripheralClaimLevel`), and the claim carries it to the worker.

| Hold | Claim frames | What it adds |
|---|---|---|
| 0, colors alone | manageSwControl `[01 01 00]`, the cluster flag alone | The device keeps its power saving, and its on-board profile keeps running (Logitech's x8071 document pp. 26-27, and OpenLogi pull request 523, where a G903 took five colors under it) |
| 1, lighting power too | `[01 03 07]`, power mode Full, `[01 03 05]`, as Logitech's own program claims (g810-led-resources `dumps/g815/G815-Hotplug-to-start.pcapng`, rigdeck `lighting.py:27-30`) | The power flag stops the device from dimming its lights by itself |
| 2, on-board memory mode off as well | The switch to host mode first, the order that program and Solaar keep (`settings_templates.py:3332-3339`), then hold 1's frames | The profile saved on the device does not apply while it is lit |

The bytes are fixed at every hold. They are never the flags read back and widened, so a power flag a program that died left behind does not outlive a claim at hold 0.

`HidppUnit.MaxClaimLevel` is what a unit offers, set by `DescribeLighting`: 1 for a 0x8071 device with a cluster to paint, and 2 where it also has the mode feature and is not a keyboard that must stay in its on-board memory mode (`HidppUnitProtocol.KeepsOnBoardMode`, the G915 TKL, known on any transport by the model ID feature 0x0003 reports). A device that lists 0x0003 and refuses the read stays at 1, since it cannot be told from that keyboard. `PaintLighting` holds a unit at the smaller of the ruling claim's hold and what the unit offers. A claim whose hold changes is handed back at the hold it was made at, and the same pass claims it at the new one (`HidppBackend.Drive`).

At hold 2, `HidppBackend.Claim` reads the mode before it changes it, as libratbag does (`hidpp20.c:2260-2271`). Only a device read in its on-board memory mode is switched, so a device its owner keeps in host mode stays there, and the hand-back writes back exactly what was read. A read that goes unanswered makes no claim: with no mode on record nothing could be put back. A device that refuses the read is claimed as hold 1 claims it.

#### Pacing and answers

A zone plan sends its frames back to back and repaints at most every `HidppBackend.PaintMs` (33). A cluster plan keeps `ClusterPlan.ClusterGapMs` (8) between two frames to one device, OpenLogi's wait, kept because "the controller can drop closely-spaced reports" (`openlogi-device write/lighting.rs:61-62`), and repaints at most every `ClusterPlan.ClusterPaintMs` (50), the 20 frames a second OpenGHub streams to these devices. Each unit has a queue of the frames still to go out. `HidppBackend.Send` puts out one frame per turn for a plan that spaces them, and the worker waits `FrameTickMs` (8) while any queue holds a frame. A scan or a check waits for the queues to empty, so a claim never stands half sent for as long as a probe takes.

`HidppStepKind` says how a frame goes out. A `Write` is written and not awaited. A `Commit`, the frame that shows what the frames before it staged, a `Stream`, a frame of the per-key stream, and a `Select`, the choice of the Host streaming effect, each go out as a request with `HidppLightPlan.AckTimeoutMs` (60), OpenRGB's wait for a per-key answer. An awaited frame that goes unanswered ends the paint, and the color is not taken as shown. A refused `Select` is logged and the paint goes on. Any other refused frame drops a cluster stream plan to `ClusterPlan` for as long as the unit stays found (`HidppLightPlan.WithoutPerKey`), with its clusters painted again, and ends the paint of a plan with no fallback.

A paint that failed is made again at once. After `HidppLightPlan.FailedPaintLimit` (5) failed paints in a row the unit is left alone until its next keep-alive, since OpenRGB reads five as a sleeping device. Over Bluetooth every frame is written and none is awaited: an idle Bluetooth LE link loses answers (OpenLogi issue 1000), and a wait there would stall the paint without confirming it.

#### Holding the claim

The claim and the color go out again every `ReassertMs` (5000) on their own clock, whatever the colors are doing, because a device back from sleep boots its on-board profile and drops the claim without a word (OpenRGB ReclaimSWControl, `LogitechHIDPP20Controller.cpp:6102-6110`). `HidppBackend.KeepAlive` does it by plan:

- A zone plan repeats the claim and the colors.
- A cluster plan repeats `[01 01 00]` at hold 0, or `[01 03 05]` and power mode Full above it, then the colors. It never repeats `[01 03 07]` or the mode frame. The mode is switched once per claim, because on a G515 the mode call resets the keyboard's state and drops held modifiers, under Logitech's own program too (Solaar issue 3310). At hold 2, where the claim switched the mode, the keep-alive reads it, and a device found back in its on-board memory mode is claimed again as it was first claimed, switch included.
- A cluster stream plan reads the claim first (`HidppLightPlan.ClaimRead`), since a cluster frame sent while per-key frames show takes the display back and blanks them (g915x-heatmap `PROTOCOL.md:90-92`). While the cluster flag stands it repaints through the per-key frames alone. When the read shows the flag gone, which is how a keyboard that slept and woke behind its receiver reads, the worker claims and paints in full again. A read that goes unanswered sends nothing, and the next keep-alive asks again.

#### Letting go

When nothing claims the path any more, the plan's hand-back goes out (`HidppBackend.HandBack`):

- A zone plan sends SetSWControl `[00 00]` (OpenRGB `LogitechHIDPP20Controller.cpp:3935-3946` and `4058-4078`, Solaar `settings_templates.py:3204-3293`). On a per-key board it first fills the indicators and the media keys white and commits, since the release returns the keys to the board's own effect and the indicators would keep the last fill, dark after black. White is what Logitech Gaming Software gives both when it starts a board.
- A cluster plan sends manageSwControl `[01 00 00]`, then at hold 2 the mode the claim switched away from, release first as OpenRGB and Solaar order it (`LogitechHIDPP20Controller.cpp:3837-3877`, `settings_templates.py:3374-3388`). Each frame goes out as a request, and one whose answer is missing is written once more, which changes nothing a second time.

When G HUB or LGS starts, the linker withdraws the unit's path and the worker lets go without a frame (`HidppBackend.LeftToLogitechProgram`). The program lights the device from there on, and a hand-back that landed after its claim would clear that claim, and at hold 2 undo the mode it just set. A path that is still linked and merely unclaimed, a switch turned off or a device unassigned, is handed back as ever.

The worker's `finally` hands every claimed unit back before it closes the channel, so stopping the engine leaves no mouse frozen on the last color.

### The owed hand-back

A claimed unit the worker lets go of with no frame, because it stopped answering a check or a write to its path failed, is owed its hand-back (`HidppBackend.Owe`). A write that fails while the scan asks a slot owes it as a failed color write does (`HidppBackend.Drop`). A device that slept restarts on its own effect and is owed nothing in fact. One that missed a single answer still holds the claim, and at hold 2 is still in host mode. The worker cannot tell the two apart, so the claim stays on the crash path's record as it stood, with its plan, its hold and the mode read before it.

- When the unit is found again, the debt is paid before anything else goes to it, a new claim included, which then starts from the device's own mode (`HidppBackend.PayBack`). The release goes out as any hand-back's does. The mode is read first and written back only to a device that is not in the mode the claim found, because the mode call is the one that costs a keyboard its held modifiers. A read that goes unanswered leaves the write in, since a device still in host mode is the worse of the two to leave.
- When the unit found at the slot is another device, one with another name or with its lighting features at other indexes (`HidppBackend.SameDevice`), the debt is dropped unsent. Its frames name the features of the device that left, at that device's indexes, and a receiver's slot can be given to another device meanwhile.
- A stop sends what is still owed through one-shot writes on a handle of its own (`HidppBackend.PayOwedNow`), as the crash path does.
- A Logitech program that starts ends every debt with no frame, and so does a collection that leaves.

The same rule holds in the three direct lighting workers ([The direct backends](#the-direct-backends)).

### The crash path

A crash dialog keeps the process alive, and the workers with it, and a worker left running would claim its device again on its next re-assert. `HidppBackend.NoteClaimed` (`HidppBackend.cs` line 1083) records a unit and the frames of its hand-back before its claim goes out, so no moment exists in which a device is claimed and the hand-back does not know it. The record holds the frames themselves and never an index to build one from: a 0x8070 release sent to a 0x8071 index sets the power mode and releases nothing.

`InputService.PanicQuiesceOutputs` (`InputService.cs` line 13812) first waits up to 250 ms in all for silence (`PeripheralOutputHost.WaitForSilence`): the GameSense worker, the Razer Sensa worker, then each direct backend that rumbles a device. It then calls `PeripheralOutputHost.ReleaseLightingNow` (`PeripheralOutputHost.cs` line 799), which sets one deadline `PanicBudgetMs` (750) ahead for the direct backends together:

1. `SignalStop` on every direct backend, before any is waited for, so none claims anything more.
2. `HidppBackend.ReleaseClaimedNow` (`HidppBackend.cs` line 1126). The HID++ units go first, because only they can leave a device in host mode. The worker is stopped and given `PanicJoinMs` (250) to hand back on its own channel, OpenRGB's teardown order (its sender stops before SetSWControl(0, 0), `LogitechHIDPP20Controller.cpp:3843-3856`). Each unit still on the record then gets its frames in order through `RawHidOutput.WriteOnce`, which opens its own handle with a 200 ms timeout. A unit whose write fails is left there, since the frames behind it would wait out the same timeout on the same path.
3. `ReleaseClaimedNow` on each direct backend in the order `DirectBackends.Create` lists them: LampArray first, whose hand-back is one short report, then SteelSeries, then Razer, whose hand-back can wait on a lock other tools share. Each waits at most 250 ms for its worker and never past the deadline, then hands back what is still on its record through bounded calls on handles of its own (`HidReportChannel.RunBounded`).

Chroma and GameSense end their sessions on their own timeouts, and the LED SDK goes with the process.

### Battery

`HidppUnitProtocol.BatteryPercent` (`HidppUnits.cs` line 450) decodes as Solaar does (`hidpp20.py:2191-2265`). 0x1004 function 1 gives a percent, or when that is 0 a level: 8 full at 90, 4 good at 50, 2 low at 20, 1 critical at 5, anything else 0 (`common.py:652-657`). 0x1000 function 0 gives a percent, and 0 means unknown. The charge is read at discovery and with each check. `PeripheralOutputs.BatteryOf` reads the first unit in the row's `HidppUnits` that reports one, whatever path lights the row. Razer and SteelSeries software report no charge here, so those rows read as unknown.

---

## The direct backends

`IDirectUnitBackend` (`IDirectUnitBackend.cs`) is one family of devices lit or rumbled one at a time, each through its own collection, with no vendor software running. `DirectBackends.Create` (`DirectBackends.cs`) makes the four the host starts with the engine. Each is made inside a guard (`DirectBackends.Add`), so a constructor that throws costs that family alone. `HidppBackend` is their model and keeps its own shape.

| Family | Backend | Thread | Finds its devices by |
|---|---|---|---|
| `LampArrayUnit` | `LampArrayBackend` | `PeripheralLampArray` | A collection on usage page `0x59`, usage `0x01` |
| `SteelSeriesUnit` | `SteelSeriesDirectBackend` | `PeripheralSteelSeries` | Product ID, and the control collection on usage page `0xFFC0`, usage `0x0001` |
| `RazerUnit` | `RazerDirectBackend` | `PeripheralRazer` | Product ID, and a 91-byte feature report |
| `TouchSenseUnit` | `TouchSenseBackend` | `PeripheralTouchSense` | The interfaces PadForge's WinUSB package registers |

### The contract

Each backend has one worker thread that owns every channel of its family, so a scan, a claim and a color never interleave on one collection. A lighting worker wakes on `PeripheralOutputs.LightingChanged`, a haptic one on `HapticsChanged`, and each waits on its idle tick with no I/O while no row links one of its paths.

| Step | Rule |
|---|---|
| Scan | From the list `Rescan` hands over, by descriptor and table, with no write to any device. The result goes out as one new `DirectBackendSnapshot`, swapped whole, and `SnapshotChanged`. Until a backend's first scan its snapshot is `DirectBackendSnapshot.NotScanned`, and every device row keeps the outputs it had on record until every backend has scanned |
| Rows | A unit reaches the rows of its own device by container. The host looks each row's container up from the row's device path, and the linker compares it with `DirectUnit.ContainerId`. A unit whose container is not known yet carries `Guid.Empty`, matches no row and gets no row of its own |
| Open | Only a unit whose path a row links and on which a claim resolves, so a device nobody assigned costs nothing |
| Record, claim, paint | The unit's hand-back goes into the crash record before its first claim frame goes out, and a worker whose stop is set claims nothing more. The first color follows the claim in the same pass. The claim and the color go out again on the family's interval, on a clock apart from the color's, so a color that changes faster than the interval never holds the claim back |
| Hand back | When the path leaves the link table or no claim resolves on it: the family's hand-back, then the handle closes. Nothing is sent to a Razer or SteelSeries unit whose path was withdrawn because Synapse or GG started, since the program has taken the device and a hand-back that lands after its claim undoes it. Nothing is sent to a LampArray unit Windows Dynamic Lighting started to light, whose hand-back would switch Windows' own effect off |
| Fail | A failed write closes the unit's channel and lists the unit asleep (`DirectUnit.Asleep`). It never takes the unit off the list. The backend tries the unit again on its own interval and asks the host for a walk (`RescanRequested`). A unit stays listed while its collection is in the last walk and leaves the list when its collection leaves it |
| Stop | The worker's `finally` hands back every unit it holds before it closes its handles, and sends what it still owes through a bounded write on a handle of its own. A backend takes calls after its stop, and after `Dispose`, and does nothing: the host's link pass can outlive the wait `Stop` makes for it, so a `Rescan` or a read of `Snapshot` can arrive beside the stop or after it |

While a unit is asleep the linker links no path to it, and the rows that match it keep the outputs they had on record, so their tabs stay up with the line for a device that has not answered yet. A unit with a row of its own keeps that row. The claim stays where the dispatcher put it, and paints again once the unit answers and is listed awake.

The owed hand-back is the HID++ worker's rule ([above](#the-owed-hand-back)) in each lighting family. A lit unit the worker lets go of while its device may still show the claim, after a failed write, a missed answer or a hand-back that did not go out, is owed its hand-back. The hand-back keeps its place on the crash record until it is settled. It is sent once the unit answers again, whether or not anything lights it by then, ahead of whatever else the unit is sent. A unit that does not take it stays owed. A stop sends it through a bounded write on a handle of its own. It ends with nothing sent where a hand-back would send nothing, and when the unit leaves the list.

For the crash path each backend has `SignalStop`, which must not block, and `ReleaseClaimedNow(deadline)` ([The crash path](#the-crash-path)). `WaitForSilence(waitMs)` is for a haptic family, which sends its stop inside the wait.

### LampArray

`LampArrayBackend` (`LampArrayBackend.cs`) lights the devices Windows Dynamic Lighting drives, each on its own. `LampArrayProtocol` builds and reads the reports of the HID Lighting and Illumination page (HID Usage Tables 1.6, section 26).

The scan keeps the collections on usage page `0x59`, usage `0x01`, and describes each once.

1. `LampArrayDescriptors.Read` reads the descriptor through Windows' HID parser, with no report sent. It finds each report by the usage of its logical collection, the attributes report `0x02`, the request `0x20`, the response `0x22`, the range update `0x60` and the control report `0x70`, and checks the fields it uses (`LampArrayProtocol.CheckShape`). The attributes, the request, the response and the range update must be there. The control report is taken when it is. Only feature reports are driven.
2. It has the parser build each report PadForge sends or reads from known values and compares the bytes with its own frames (`LampArrayProtocol.CrossCheck`). The descriptor is the device's, so its reports are not taken on faith: a device whose range update, control, request or response report is laid out any other way would take PadForge's frames for something else, and is rejected.
3. One read of the attributes report gives the lamp count, the kind and the minimum update interval, and the parser must read the same values from it (`LampArrayDescriptors.AttributesAgree`). A count above `LampArrayProtocol.MaxLamps` (4096) is taken for a misread report.

A device whose reports are not the ones PadForge drives is named once in the diagnostics log and left alone. A unit that has never answered its attributes read is not listed.

`LampArrayContainers.For` gives the container a unit is matched to its rows by: the collection's own, the lookup the host makes for a row. One device needs more. Logitech's LampArray driver puts a slot node under a LIGHTSPEED receiver for each paired device, a USB node of vendor 046D whose device ID ends in `LAMPARRAY`, and the collection Windows lights is a virtual HID device under that slot. When such a collection reports no container or the PC's own, the container is taken from the first USB device above the slot, the receiver, whose rows the unit belongs to.

| Step | What happens |
|---|---|
| Claim | The unit is opened for reading and writing. Its lamps are read first, once per arrival: the request for lamp 0, then one response per lamp, each checked for the lamp it names (26.8.2), `LampsPerPass` (32) to a pass. A read that fails is tried `ReadAttempts` (8) times in all, with a pause of `ReadRetryStepMs` (50) times the tries made so far, the rule of the host that found one firmware refusing reads for a short window after a write (acer-predator-helios-rgb `protocol/PROTOCOL.md:212-214`). Then AutonomousMode off, the wait the page promises the device (26.10.1), and the color |
| Paint | One range update report per run. A run is a longest span of neighboring lamps with the same level counts (`LampArrayProtocol.BuildRuns`), because a device ignores a whole report in which any channel is above the count of any lamp in its range (26.11.2). Each channel is scaled to the run's counts. An array cut into more runs than the device promises to take back to back, or than `MaxRuns` (8), is painted as one run at the smallest counts. A fixed-color lamp takes the color's brightest channel as its intensity. A unit whose lamps could not be read is painted blind, one report over every lamp at intensity 255 |
| Hold | A new color goes out no sooner than the device's minimum update interval after the last one, and never sooner than `LampArrayProtocol.PaintFloorMs` (33). The newest color is the one sent. The claim and the color go out again every `ReassertMs` (4000), the one interval a reference names: a host for a Lenovo ITE 8258 keyboard re-takes control every four seconds to keep the firmware from timing out to its own default (aura-loq `aura/cycle.py:173-176`) |
| Hand back | AutonomousMode on, which returns the device to its own effect (OpenRGB `RGBController_HIDLampArray.cpp:434-444`). A device with no control report has no effect to return to, so its lamps are turned off, their default state (26.11). A unit whose path was withdrawn because its vendor's program started is handed back like any other: while AutonomousMode is off no source other than the host can change a lamp, and the program is such a source |
| Fail | The channel closes, the unit is listed asleep, a walk is asked for once, and the unit is described again after 5, then 10, then 15 seconds (`FirstRetryMs`, `MaxRetryMs`), the HID++ worker's backoff |

The control report is never read back. Microsoft's firmware samples answer a GET for the attributes and the response alone, and real firmware stalls one for the control report (hp-omen-35l-rgb `README.md:43`).

`WindowsLightingState` (`WindowsLightingState.cs`) says whether Windows Dynamic Lighting lights a collection, from the registry of the signed-in user under `Software\Microsoft\Lighting`: the value `AmbientLightingEnabled` under `Devices\<interface path>` where the user set the device on its own, else the value of the same name for every device, else on, since Windows turns Dynamic Lighting on by itself. Each doubt is settled toward lit: standing down for nothing costs a color, and writing beside Windows makes two writers fight over the device. On a Windows before build 22621, or with no `SettingsHandlers_Lighting.dll`, nothing lights devices in the background and the answer is no. PadForge runs elevated, and when a standard user elevates with another account's credentials `HKEY_CURRENT_USER` is that account's hive. So the user is taken from the token of the shell's process, and the key is opened under that user's SID in `HKEY_USERS`. The values are read and never written.

A unit Windows lights is listed with `DirectUnit.WindowsLit` and never written to. One that turns Windows-lit while claimed is let go without a frame. The state is read again every `LitReadMs` (1000), and once more right before each hand-back. A collection the scan cannot describe is not listed, so the linker's rule that closes a device's own protocol while Windows lights it does not see such a collection.

A unit that was claimed when its write failed is owed its hand-back from then on: a device that missed one report and stayed on the bus still has AutonomousMode off and keeps the last color until it loses power. The hand-back goes out when the unit answers again with nothing claiming it, or at stop. A claim that takes the unit anew ends the debt, since its own hand-back is the same report, and so does Windows lighting it.

No step of a pass sleeps. Every wait there is a time the worker comes back at: the pause between two tries of a failed read, the wait between the claim and the first color, the update interval. So a device that is slow to answer holds up no other unit's colors for longer than one such step takes. `HidD_SetFeature` and `HidD_GetFeature` take no timeout, which is why this family has a thread of its own and the crash path writes through a bounded call (`HidReportChannel.RunBounded`).

### Razer

`RazerDirectBackend` (`RazerDirectBackend.cs`) lights one Razer mouse or keyboard at a time through the device's own feature reports. `RazerDirectProtocol` builds the reports, and `RazerDirectTable` says which a product takes: 232 product IDs, 180 of them with a color path. The table was read from openrazer 477f4d6d and OpenRGB 01bd77c.

One report carries every command: 90 bytes, sent and read back as a HID feature report with report ID 0. Windows wants the ID in front, so the buffer is 91 bytes. After the ID come the status, the transaction ID, two bytes of remaining packets, the protocol type, the data size, the command class, the command ID, 80 argument bytes, the checksum and a reserved byte. The checksum is the XOR of buffer bytes 3 to 88. Every write that has a storage byte carries `00`, which shows the color and writes nothing to the device's memory. No device-mode report (class `00`, command `04`) is built or sent: mode `03` hands a device's special keys to a program that must then handle them, and one that dies leaves the device there.

| `RazerFamily` | Paint | Product IDs |
|---|---|---|
| `Classic` | Class `03`, commands `00`, `01` and `02`: state, color and effect per LED | 11 |
| `Extended` | `0F/02`, the extended matrix effect, one report per LED | 98 |
| `ExtendedFrame` | `0F/03`, the extended matrix frame of one row, which paints the whole mouse after a mode report | 7 |
| `Standard` | Frame rows `03/0B` or `03/0C` shown by `03/0A`, or the `03/0A` static effect alone | 62, of which 2 by the effect alone |
| `MouseExtended` | `03/0D`, one report per LED | 2 |

A unit is a listed product with a color path whose collection has a 91-byte feature report, the one fact every Windows reference goes by. A device can show more than one such collection. They are one unit, keyed by the collection the table ranks first (`RazerDirectProtocol.CollectionRank`) and written through the first of them that answers.

A claim opens the unit and goes in this order:

1. A read that changes nothing (`RazerProbe`). Its reply settles the transaction ID. The two projects disagree on it for 64 of the products, a device answers some IDs and stays silent on others, and the IDs the table lists are tried one claim attempt at a time, so a mouse asleep behind its receiver never gets a burst of them. A receiver's status `04` settles none.
2. The device's own regions are read where the family has the list, at most `RazerDirectProtocol.MaxRegions` (16).
3. What the device shows on its own is read where the family can say, which becomes the hand-back.
4. With the hand-back on the crash record, the claim reports and the first color go out.

Every request is followed by a read of its reply, under `RazerGuard` (`RazerGuard.cs`): the named mutex `Global\RazerLinkReadWriteGuardMutex`, which OpenRGB holds around every report it sends and uncoil around each request and its reply. PadForge takes it the same way, so neither tool reads a reply to PadForge's request, nor PadForge theirs. The mutex is created with a rule that gives everyone full control, because PadForge runs elevated and a mutex made with an elevated process's default security would shut out an unelevated OpenRGB. The waits are bounded: `PaintWaitMs` (25) for a paint, after which that paint is skipped and the next one carries the newest color, and `CommandWaitMs` (250) for a claim or a hand-back. A hand-back goes out even where the lock stayed busy. Nothing shows Razer's own software taking the lock, so it is no way to write beside Synapse.

The wait between a request and its reply is the product's (`RazerDirectRow.ReplyWaitUs`). A wired device's 600 microseconds are waited for in place. A wireless mouse takes 31 ms or 59.9 ms, and the worker does not sleep on those: it notes when the read is due and serves the other devices meanwhile (`RazerDirectRow.SlowReply`). A request is tried `Attempts` (5) times, `AttemptGapMs` (10) apart.

No color is queued. A pass paints the color that resolves then, at most every `PaintMs` (33), and never starts a paint while one is in flight. The claim and the color go out again every `ReassertMs` (5000), since a device that lost power shows its stored effect again and says nothing, and once when Windows resumes from sleep. Three kinds of product differ:

- A laptop keyboard goes back to its own lighting when the host goes quiet, so its claim read is sent whenever `KeepAliveMs` (2500) pass with nothing else.
- A product painted by the standard matrix effect report, which has no storage byte, takes a color only once it has held for `RazerDirectProtocol.EffectHoldMs` (1000), the first color of a claim included. A claim that comes and goes inside the hold opens nothing and writes nothing, and the product is not painted again on the clock.
- A product that refuses its own paint is tried on the fallbacks the table lists for it (`RazerFallback`). One that refuses every paint is left to its own lighting until its collection leaves the walk. A region a device names itself and then takes no color for is left to the device.

Set Chroma Color paints the Razer devices on its virtual controller whether or not their Lighting tabs take control. For a unit that is the live macro of the controller with the smallest displayed number among the ones that hold a row of it, ahead of the unit's ruling claim (`RazerDirectBackend.MacroOn`), the precedence the Chroma worker keeps for a category. A macro with no claim behind it claims the unit for its window and hands it back after.

When no color resolves on a unit any more, each LED is given what the device showed for it where that could be read, or its spectrum effect, and a product painted by frame is sent nothing. No report in any reference returns a device to its stored effect, so this is as far as a hand-back goes.

Synapse and Razer Central drive every Razer device, and nothing keeps their reports and PadForge's apart. From the pass that sees one running, nothing more is sent to any unit: no color, no hand-back, no read of a reply in flight. The claim is forgotten and the handle closed. The worker reads the link table before the presence on every pass, because the link pass publishes the presence first, so a table that shows a path withdrawn is never read beside a presence older than it.

A unit that stops answering, or whose write fails, a hand-back's included, is listed asleep with its handle closed. It is asked again every `RetryMs` (5000) while a row that held it is still lit, and once after each walk the host hands over, so a device whose row was replaced while it slept is found awake again. A unit that falls asleep painted is owed its hand-back (`Unit.Owed`). It is then asked every `RetryMs` whether or not anybody lights it, and `RazerDirectBackend.Probe` pays the debt on the handle its question went out on, before the unit is listed awake.

### SteelSeries

`SteelSeriesDirectBackend` (`SteelSeriesDirectBackend.cs`) lights each SteelSeries mouse and keyboard through the device's own control collection. `SteelSeriesDirectProtocol.Models` lists 96 product IDs, 82 of them with a color path, each under one of 29 command families (`SteelSeriesFamily`).

Every lit product keeps its control channel on a vendor collection of its own: usage page `0xFFC0`, usage `0x0001`, no report IDs, alone on one USB interface. A frame is chosen by product ID and never from a descriptor, because the families reuse command numbers. `0x08` is the color on a Rival 300 and erases a flash page on the Rival 3 Gen 2 firmware, and `0x09` saves on the older mice and on a Rival 310 "will break the LEDs" (rival310-re `README.md:27`). No builder produces a command that saves to the device's memory, and the brightness commands stay out as well, since they are the user's setting.

A family's row (`SteelSeriesFamilyInfo`) carries:

| Member | Says |
|---|---|
| `Interface` | The USB interface the control collection is alone on |
| `Report`, `AltReport` | The report type the color travels as, output or feature, and the other type where shipped references differ. The alternate is used for a collection that lacks the first at the length the frames need |
| `GapMs` | The least time between two reports of one paint, up to 66 ms |
| `RepaintMs` | The least time between the first reports of two colors |
| `ReassertMs` | How long the claim and an unchanged color stand before they go out again: 5000, or `SlowReassertMs` (30000) for the Rival 3 Wireless and the Rival 650, whose color is an LED program in several reports |
| `Echoes` | A 2.4 GHz dongle, which answers each report on its input report |
| `Gated` | An Apex board whose claim, packet and hand-back depend on its firmware version |
| `Claim`, `Color`, `HandBack` | The frames |

The pacing comes from what the vendor's own program does where a USB capture of it exists, then from a program that streams to that product on Windows, and from the reference tools' waits where neither exists.

A unit a row links and a claim resolves on is opened for read and write. A collection that opens with no access right only is one Windows keeps for itself or another program holds, and such a unit is not written to. No color is queued. Each pass reads the color that rules the unit now and sends it when the family's next allowed time has come, one report per pass, so a slow device shows the newest color and skips the ones between. Every paint sets every LED, so a paint is its own re-assert. The claim frames go out in front of the first color of an open, again in front of the first color that starts once the interval has passed since they last went, and once more when Windows resumes from sleep.

A dongle answers each report on its input report, and the worker reads that answer before the next report goes. The dongle stays on the bus while its mouse is switched off or asleep, and then answers anything with `40 FF`. So the write succeeds whatever the mouse does, and only the answer tells. On `40 FF`, or with no answer in `EchoTimeoutMs` (250), the color in flight is dropped and the unit is left alone for `QuietMs` (1000), then the whole color is sent again from its first report. The handle stays open and the unit stays listed awake through this: a unit listed asleep has no path and so no color, and the color's first report is the only question in the lighting protocol that a mouse which woke up answers.

A gated board is asked its firmware version once after the open (`SteelSeriesDirectProtocol.VersionQuery`, command `0x90`), and the reply is waited for `QueryTimeoutMs` (100). Firmware 1.19.7 or newer is the third generation (OpenRGB `SteelSeriesApexController.cpp:219-253`), which is claimed with the feature report `4B` and handed back with the output report `41 00`. An older board takes no claim and is handed back with `3B`.

When no claim resolves on the unit or its path leaves the link table, the family's hand-back frame goes out and the handle closes. A family no reference has such a frame for keeps the last color until the device loses power, and gets no parting color: black would leave a dark device, and any other color is a guess at what its owner stored. That is 47 of the 82 product IDs. Nothing is sent when GG has taken the device (`SteelSeriesDirectBackend.LeftToVendorProgram`), and nothing to a dongle whose mouse is off, which wakes into its own lighting.

A write that fails, a hand-back included, closes the unit's channel, lists the unit asleep and asks the host for a walk. The unit is tried again every `RetryMs` (5000) by opening it, which sends nothing. A unit that fails while it may show a color of PadForge's is owed its hand-back (`Unit.Owed`), and the try that finds the unit open again sends it before the unit is listed awake (`SteelSeriesDirectBackend.PayBack`). A unit that failed before any claim or color report of its was tried, a family with no hand-back frame, and a dongle that had said its mouse is off are owed nothing.

### TouchSense

`TouchSenseBackend` (`TouchSenseBackend.cs`) plays the buzz motor of a TouchSense mouse bound to WinUSB: the Logitech iFeel Mouse, 046D:C030 and 046D:C031, and the iFeel MouseMan, 046D:C032 (`TouchSenseProtocol.Mice`).

The mouse declares one output report, seven bytes with no report ID, inside its mouse collection. Windows' mouse class driver passes no output report down, so the frames reach the mouse only once it is bound to WinUSB, which the Devices page offers as Play Rumble on This Mouse ([Driver Installation Internals](driver-installation-internals.md#opt-in-bindings)). Bound, the mouse is no mouse to Windows any more: it has no Raw Input row and moves no pointer.

`InputManager.SyncTouchSenseMice` (`InputManager.TouchSenseMice.cs`) is Step 1's phase 1n, and the one place a bound mouse is opened. A worker task looks for the bound mice (`TouchSenseBinding.FindBound`: the active interfaces of PadForge's WinUSB package whose path names a TouchSense mouse) at most every `TouchSenseSweepMs` (1000) and opens each one (`TouchSenseChannel.Open`), since both are blocking calls. The poll thread registers the rows a sweep finished, takes a row whose channel closed offline, and puts back a row the user removed from the Devices page while its mouse is still there. A mouse whose open failed or whose channel closed is opened again after `TouchSenseReopenMs` (5000), and only once the channel it had before has closed.

`TouchSenseMouseDevice` (`TouchSenseMouseDevice.cs`) is the row. It reads the mouse's four-byte input report from the interrupt IN pipe on a `TouchSenseMouse` thread and presents it as any mouse row does, the two motion axes, the wheel and five buttons, so mappings and a Keyboard + Mouse virtual controller treat it as a mouse. It carries the mouse's vendor and product ID, so the Devices page finds the offer that gives Windows its driver back, and the mouse's WinUSB interface path as its device path, so the host's container lookup matches the row to the mouse's unit. A mouse whose report descriptor is not the iFeel Mouse's is read as no pointer at all (`TouchSenseProtocol.DeclaresPointerReport`), never through a layout that was guessed.

WinUSB lets one handle open a device, so the row and the backend share one `ITouchSenseChannel` per mouse, listed in `TouchSenseChannels`. `TouchSenseChannel` keeps the rules of that handle:

- At open, the interface must be HID class with an interrupt IN pipe, and the report descriptor the mouse itself returns must declare the buzz report (`TouchSenseProtocol.DeclaresBuzzReport`), so no frame ever goes to a device that does not declare it. SET_IDLE goes out once.
- A frame goes out as a control SET_REPORT, the transfer the vendor's own stack used. When that fails and the interrupt OUT pipe takes the same seven bytes, as the Linux driver sends them, the channel stays on the pipe for the rest of its life.
- Any thread may close it, once, and a close returns only after the handle is gone, so a mouse is never opened while a handle to it is still held.

A bound mouse is no HID collection, so it is in no walk the host hands over. Each `Rescan` is the backend's cue to look for the bound mice again, and a mouse is a unit, keyed by its WinUSB interface path, for as long as that look finds it. The backend opens nothing: it takes the channel the row opened, and only when a frame has to go out.

| Frame | Bytes |
|---|---|
| Buzz, a train of pulses | `11 0A`, the strength, the delay between pulses in milliseconds as 16 bits with the low byte first, the number of pulses, `00` |
| Stop | `13` and six zeros |
| The vendor driver's last frame | `F3` and six zeros |

Four sources give the same bytes: the 2001 capture of the vendor's driver stack, Dan Moore's write-up and BeOS program, Joshua Bobruk's Linux driver, and the LibUsbDotNet program in Logitech-iFeel-Vibration-POC. The vendor's 2003 driver, `LMouFrc.dll` of MouseWare 9.80, builds the same frames and shows the strength scale. `TouchSenseProtocol.StrengthFor` follows its two steps: nothing under a level of `OffBelow` (0.02), else `0x50` plus the level times `0xAF`, then that times the model's factor for the delay between pulses, out of `0xFF` (`TouchSenseProtocol.DelayFactor`). At this build's delay of 10 ms, full strength is `F0` on an iFeel Mouse and `E3` on an iFeel MouseMan.

A mouse buzzes at the strongest level among the rows linked to it. A level that rises from silence goes out at once. One that changes while the motor buzzes goes out once `MinGapMs` (33) have passed since the last frame, with no stop frame between two buzz frames. One that holds goes out again every `ResendMs` (100), so the motor never reaches the end of its count. Each frame asks for `HoldMs` (300) of pulses, so a PadForge that is gone leaves a third of a second of buzz at most. A level that falls silent, a row that leaves the link table and a level the engine zeroed at a silence edge each get the stop frame on the worker's next pass, which comes within `ActiveTickMs` (10) while anything plays.

A frame that fails closes the channel, lists the unit asleep and asks the host for a walk once. A mouse with no channel open when a frame is due is listed asleep too. The mouse is tried again every `ReopenMs` (5000), and at once when a channel opens. At stop the worker sends every mouse it wrote to the stop frame and then `F3`. On the crash path `WaitForSilence` sends the stop inside the wait, and the lighting pass asks nothing of this family.

### Limits

No device was written to while these paths were built: no Razer, SteelSeries, LampArray or TouchSense device, and no Logitech device for the HID++ plans beyond the zone-only class. Each frame rests on the references its source cites, and what a device shows after a frame is stated here from those references. The test host cannot reach a device either. It refuses every real HID open and write (`RealHidAccess`), the look for bound TouchSense mice with every WinUSB open and transfer on one (`RealTouchSenseAccess`), and the shared Razer mutex (`RazerGuard.KeepOffTheSharedMutexForTest`). A test hands its code a scripted channel, which keeps it off the hardware while the code is right. The refusals are for the build in which the code is wrong, one with a guard taken out to see whether a test notices.

---

## The LED SDK backend

### The loader

`LogiLedEngineNative` (`LogiLedEngineNative.cs` line 34) replicates the `LogitechLedEnginesWrapper.dll` shim from managed code, so PadForge redistributes nothing of Logitech's. `LogiLedEngineNative.TryLoad` (`LogiLedEngineNative.cs` line 103) reads the default value of `ServerBinaryKey`, the wrapper's only embedded wide string and the key Aurora and Artemis read from HKLM's 64-bit view. It checks that the file's description is `Logitech Gaming LED SDK` (Aurora `LgsInstallationUtils.cs:48-64`), loads it with `LoadLibraryExW` and `LOAD_WITH_ALTERED_SEARCH_PATH` so the engine's own directory joins its dependency resolution, and resolves the undecorated cdecl `LogiLed*` exports:

| Export | Required |
|---|---|
| `LogiLedInit`, `LogiLedSetLighting`, `LogiLedShutdown` | yes |
| `LogiLedInitWithName` | no. Called with the ANSI string `"PadForge"`, `LogiLedInit` otherwise |
| `LogiLedSetTargetDevice` | no |
| `LogiLedSaveCurrentLighting`, `LogiLedRestoreLighting` | no |
| `LogiLedSetLightingForTargetZone` | no. The 9.00 header's zone call (logitech-led-sdk-rs `bindings-x86_64.rs:354`, RGB.NET `_LogitechGSDK.cs:146`) |

Old engines carry 13 exports, so each optional one degrades on its own. Returns are one-byte C++ `bool`, marshaled as `byte`. `LogiLedEngineNative.Unload` (`LogiLedEngineNative.cs` line 233) nulls every delegate before `FreeLibrary`, so a stray call lands on a null check instead of a freed code page. `ILogiLedNative` (`LedSdkBackend.cs` line 16) is the seam the bench scripts.

### Types and zones

`LedSdkBackend.TypeOf` (`LedSdkBackend.cs` line 142) maps a path key to `LogiLed::DeviceType` (logitech-led-sdk-rs `bindings-x86_64.rs:136-142`) and the zones written for it:

| Key | Device type | Zones | Reference |
|---|---|---|---|
| `keyboard` | 0 | 5, and the per-key call | RGB.NET's G213, `LogitechDeviceProvider.cs:99` |
| `mouse` | 3 | 3 | Aurora `LogitechDevice.cs:104-123` |
| `mousemat` | 4 | 1 | Aurora |
| `headset` | 8 | 4 | Aurora |
| `speaker` | 14 | 4 | Aurora |
| `device` | none | One `LogiLedSetLighting` on the RGB and monochrome targets | `LogitechGamingLEDSDK.pdf` p. 23, RGB.NET `LogitechPerDeviceUpdateQueue.cs:34-37` |

The `device` path lights the Logitech devices with no zones, the manual's G710+, G600, G510, G110, G19, G105, G300, G11, G13 and G15 (`LogitechGamingLEDSDK.pdf` pp. 9-18). Only the LIGHTSYNC row takes it, as the lightbar mirror lit them. `PeripheralLinker.LedSdkTypes` (`PeripheralLinker.cs` line 443) puts it first in paint order.

### Painting

`LedSdkBackend.Paint` (`LedSdkBackend.cs` line 375) sends whole percent per channel, rounded (`LedSdkBackend.ToPercent` (`LedSdkBackend.cs` line 201)). The target mask is sticky process-global state, so each call that narrows it puts it back:

- `device`: `SetTarget(3)` (`MONOCHROME` and `RGB`), `SetLighting`, `SetTarget(7)`. Per-key boards ignore that mask.
- `keyboard`, when the engine has the target call: `SetTarget(4)` (`PERKEY_RGB`) and `SetLighting`, since a per-key board answers only the whole-board call on its own target. Without the target call `SetLighting` would reach every device (`LogitechGamingLEDSDK.pdf` p. 23), so it is never sent that way.
- Every zoned type: `SetTarget(7)`, then one `LogiLedSetLightingForTargetZone` per zone, as RGB.NET sets the mask before every zone batch (`LogitechZoneUpdateQueue.cs`).

The whole-device call reaches zonal devices too. As in Aurora, which sends it before the zone calls on every update (`LogitechDevice.cs:94-124`), every claimed type after it in a pass goes out again.

`LedSdkBackend.CanPaint` (`LedSdkBackend.cs` line 280): the whole devices need the target call, a keyboard either call, and every other type the zone call. A session for types the engine cannot paint would paint nothing and fail every liveness round, so the engine goes back unopened until the claimed types change or the retry interval (30000) passes, when it is loaded again in case Logitech's software was updated or replaced. `LedSdkBackend.PublishPaintable` (`LedSdkBackend.cs` line 295) stores the paths the loaded engine can paint in `PeripheralOutputs.LedSdkPaintable` (`PeripheralOutputs.cs` line 359). A load that fails while the software runs stores an empty list (`LedSdkBackend.PublishNone` (`LedSdkBackend.cs` line 304)), an x64 engine in the ARM64 build among the causes. The list is null before any load, while no Logitech software runs and once nothing is claimed, and the Lighting tab names a type outside it instead of a route.

### The session

`LedSdkBackend.LoopAsync` (`LedSdkBackend.cs` line 409) runs on a thread-pool task and makes every native call itself. Every reference serializes SDK calls, and the Rust binding wraps the whole API in a process mutex.

| Step | What happens | Timing |
|---|---|---|
| Orphan wait | A previous worker still inside the SDK is waited for | up to `DefaultOrphanWaitMs`, 15000 |
| Nothing claimed | No engine is loaded. `Idle`, no paintable list | polled every 100 ms |
| Presence | `SoftwarePresent`, else `Waiting` and no paintable list | retried every 30000 |
| Presence settle | The first time it finds the host, and after an absence or a reinitialization, wait before touching the engine. Init right after G HUB starts succeeds and does nothing (Aurora waits 5 s) | 5000 |
| Load | `TryLoad`, then `PublishPaintable`. A failed load publishes an empty list and reports `Waiting`. When no claimed type is paintable: unload, `Waiting`, and wait for the claimed types to change or for the retry interval | retry 30000 on failure |
| Init | `InitWithName("PadForge")`, else `Init`. A refusal unloads and retries | retry 30000 |
| Open | Wait, `SetTarget(7)`, `SaveCurrent`, `Connected` | 100 (Aurora's settle) |
| Stream | Each poll: a type nobody claims any more gets the saved lighting back (`Restore`), and every remaining type is painted again over it. Between liveness rounds only a changed color goes out. Every `LivenessMs` (5000) every claimed type goes out | polled every 100 ms |
| Fail streak | Three liveness rounds in a row in which no call took end the session, which reinitializes after the retry | |
| Teardown | `Teardown`: `RestoreAndShutdown` (restore first, the RGB.NET dispose shape) unless a newer worker already loaded the engine, then `Unload` | |

A set color needs no keep-alive, but a dead G HUB shows only as failing calls, which the liveness round surfaces while the colors hold still. The manual gives two reasons a call answers false, a session never initialized and a lost connection to Logitech's software (`LogitechGamingLEDSDK.pdf`, `LogiLedSetLightingForTargetZone`). It says nothing about a type with no device behind it, so a type that fails alone is recorded as sent, waits for its next color or round, and never ends the session.

### Generations and orphans

`LedSdkBackend.Start` (`LedSdkBackend.cs` line 204) increments `s_generation`, and a worker whose generation is no longer the newest (`LedSdkBackend.Superseded` (`LedSdkBackend.cs` line 239)) drops its state reports and loads nothing more. `LedSdkBackend.Stop` (`LedSdkBackend.cs` line 214) cancels and waits 3000 ms. A worker still inside a native call is parked in `s_orphan`, and the next worker waits for it before loading the engine, for up to `DefaultOrphanWaitMs`, past the 14 seconds an Artemis-launched G HUB cold start takes, so two workers never overlap inside the SDK. `LedSdkBackend.MarkLoader` (`LedSdkBackend.cs` line 331) and `LedSdkBackend.Teardown` (`LedSdkBackend.cs` line 346) both take `s_sdkGate`, bounded by `GateWaitMs` (3000). An orphan that finishes before a newer worker loads the engine still restores and shuts down its own session. One that finishes after leaves the SDK to the newer session and only frees its module handle.

---

## The Chroma backend

`ChromaBackend` (`ChromaBackend.cs` line 54) talks to the Chroma REST server Synapse hosts at `ChromaBackend.DefaultEndpoint` (`ChromaBackend.cs` line 58), `http://localhost:54235`. The official Chroma REST docs and chroma-sdk/Colore (`RestApi.cs`) agree on every field. The endpoint is injectable because the production port is machine-global, and a test that talked to it would reach a real Synapse.

`ChromaBackend.Wanted` (`ChromaBackend.cs` line 221) gives each category's color in the order the init lists them (Colore `Rest/RestApi.cs`, the official REST docs): a live Set Chroma Color first (below), else `TryResolveColor` on the category. A Razer device claims its own category while Control This Device’s Lighting is on for its controller, the Razer Chroma row claims all six and rules the ones no device claims, and the smallest displayed player number rules a category two controllers claim.

A category that a directly lit Razer device stands in for is left out (`ChromaBackend.Shadowed`, from `DeviceLinks.Shadows`). With Synapse closed the Razer direct worker paints such a device through its own reports, and the Chroma SDK's services can still be answering on the REST port. A session that listed the device's category would then paint the same device through the SDK, from another ruling. The category counts as shadowed while a claim resolves on the row's own path, or while a Set Chroma Color is live on a controller that holds a row of the device.

| Step | Call | Notes |
|---|---|---|
| Open | `POST {endpoint}/razer/chromasdk` with `ChromaBackend.InitBody` (`ChromaBackend.cs` line 160) | The app-info JSON Synapse shows in its Connect tab: title `PadForge`, a description, an author, `device_supported` listing only the categories wanted now, and category `application`. The answer's `uri` names the session |
| Heartbeat | `PUT {uri}/heartbeat`, no body | Every second, Colore's interval and its no-data overload (`RestClient.cs:107`). A session dies after 15 seconds without a command. A non-success status ends the session |
| Effect | `PUT {uri}/{category}` with `{"effect":"CHROMA_STATIC","param":{"color":N}}` | Applies at once. Only a changed color goes out per category. `N` is BGR, `R + (G << 8) + (B << 16)` (`ChromaBackend.ToBgr` (`ChromaBackend.cs` line 154)) |
| Close | `DELETE {uri}` | Bounded to a second. Ends the session, which hands the lighting back to Synapse |

The session lists only the categories something wants, and it is opened again when that set changes, so a category nothing claims stays Synapse's. The docs do not say whether Synapse leaves alone a category a session lists and never paints. With nothing wanted, the worker holds no session and reports `Idle`.

The server answers HTTP 200 with a `result` integer even when it rejects an effect, so `ChromaBackend.SendStaticAsync` (`ChromaBackend.cs` line 459) reads the body, as Colore checks that field after every effect call (`Rest/RestApi.cs` SetEffectAsync). `ChromaBackend.TryReadResult` (`ChromaBackend.cs` line 493) needs a JSON object with a numeric `result`. 0 and 1167 are accepted, 1167 being `ResultDeviceNotConnected`, a category with no device behind it (Colore `Data/Result.cs`). Anything else leaves the category's last color unrecorded, so the next poll retries it, and a rejection is logged once per category and code, until that category is accepted or a new session opens.

URIs are joined by string concatenation, because the session URI has no trailing slash and `new Uri(base, relative)` would replace its last segment. `HttpClient` reports its own 5000 ms timeout as a `TaskCanceledException`. The init's catch for a cancellation takes only a stop (`when (ct.IsCancellationRequested)`), so a slow Synapse stays on the 30-second retry path as `Waiting`. `LightingChanged` and `ChromaMacroChanged` wake the 100 ms poll. While a Set Chroma Color is live the wait ends at its lapse (`PeripheralOutputs.NextChromaMacroLapse`), so the macro lets go then and not at the next poll. `ChromaBackend.Stop` (`ChromaBackend.cs` line 131) cancels, waits 3 seconds, and then lets a worker parked in a REST call finish on its own, since the session it ends is its own.

---

## The GameSense backend

`GameSenseBackend` (`GameSenseBackend.cs` line 31) is one `PeripheralGameSense` thread on a 20 ms tick, or `IdleTickMs` (100) while GG is let go and nothing is claimed. `HapticsChanged`, `IdentifyChanged` and `LightingChanged` wake it. `GameSenseClient` (`GameSenseClient.cs` line 47) makes its HTTP calls, synchronous with a 500 ms timeout, since a local engine answers in milliseconds. Every rule in the client is from SteelSeries/gamesense-sdk. Rumble and colors share one game, `PADFORGE`, displayed as PadForge.

| Call | When | What |
|---|---|---|
| Read `coreProps.json` | Each connect | The `address` key of `%PROGRAMDATA%\SteelSeries\SteelSeries Engine 3\coreProps.json`. No file means GG is not running |
| `POST /game_metadata`, `POST /bind_game_event` | Connect | The game, then `RUMBLE` (0 to 100) with one `tactile` handler on zone `one`, mode `vibrate` |
| `POST /remove_game_event` | Connect | Every color event a dropped session or a dead process left bound, so a type nobody claims stays GG's |
| `POST /game_event` | A rumble level change | `RUMBLE` at 0, 17, 50 or 84, one value inside each range (`GameSenseClient.LevelValue` (`GameSenseClient.cs` line 145)) |
| `POST /bind_game_event`, `POST /game_event` | A color type newly claimed, or its color changed | `COLOR_MOUSE`, `COLOR_KEYBOARD` or `COLOR_HEADSET` with `value_optional` and one `context-color` handler per zone reading the frame key `color`, then the color in the event's frame |
| `POST /remove_game_event` | A type stops being claimed | GG lights that type again |
| `POST /game_heartbeat` | Every 10 seconds while rumble or a color holds | GameSense deactivates a game after 15 seconds without events |
| `POST /game_event` 0, `POST /remove_game_event`, `POST /stop_game` | `GameSenseClient.Close` (`GameSenseClient.cs` line 273) | Silences the motor, drops the color events, and hands the devices back to GG |

The `RUMBLE` binding, `GameSenseClient.BindBody` (`GameSenseClient.cs` line 72), gives each value range a custom pulse, 30 ms for 1 to 33, 55 ms for 34 to 66 and 80 ms for 67 to 100, and a rate that repeats it 5, 7 or 10 times a second until the value changes. Each pulse ends before its next repeat starts, which answers the tactile doc's warning that vibrations take time and can queue up. Value 0 plays nothing and repeats nothing. `GameSenseClient.ColorZones` (`GameSenseClient.cs` line 94) follows `standard-zones.md:86-110` and `208-238`: the mouse's `wheel`, `logo` and `base`, the keyboard's `main-keyboard`, `function-keys`, `keypad`, `number-keys` and `macro-keys` plus `rgb-per-key-zones` `all` for a per-key board, and the headset's `earcups`. GameSense has no mousepad type: the QcK Prism pads answer only its zone-count types (`standard-zones.md:29` and `37`), which no row binds. The fourth general type, `indicator`, is a single status light and stays out.

`GameSenseBackend.Worker` (`GameSenseBackend.cs` line 180), each tick:

1. Every `RulerMs` (250), and at once when a level starts or Identify begins or ends on a row, work out the ruling Rival on the tactile path through `TryResolveHapticRuler`. The tactile handler drives every tactile Rival at once (`standard-zones.md:3`, "a device category"), so the Rival on the virtual controller with the smallest displayed player number sets the level for all of them, or the Rival Identify buzzes for the length of its train.
2. Resolve each claimed color type (`GameSenseBackend.Colors` (`GameSenseBackend.cs` line 157)).
3. With no ruling Rival and no color, post level 0 and remove every color event at once, since GG repeats a level's pulse until the value changes and a Rival that just left its controller would buzz on. After `ReleaseMs` (2000) of nothing claimed, `Close`, so a reassignment does not churn the registration.
4. Otherwise, shape the ruler's level (`HapticRumbleShaper.Level`), connect when due, render the level, and set the colors at most every `ColorMs` (50), or at once when the claimed types change. A refused or failed connect, or a call that stops answering, disconnects, and the next try comes after `RetryMs` (15000).

The crash path calls `GameSenseBackend.WaitForSilence` (`GameSenseBackend.cs` line 312) after the engine's quiesce zeroed every level. GG repeats a pulse at its rate until the value changes (`json-handlers-tactile.md:187-195`) or the game goes 15 seconds without an event (`sending-game-events.md:83`), so a process that died first would leave a Rival buzzing that long. `PanicQuiesceOutputs` waits up to 250 ms, through `PeripheralOutputHost.WaitForSilence`, for the GameSense worker to post the zero and then for the Razer Sensa worker to render it (`SensaHapticsService.WaitForSilence`), the way the Bliss-Box stop waits in `InputManager.QuiesceOutputs`. A look or a tick that read its level before the quiesce still puts it out, so each wait holds while such a pass is in flight: the GameSense worker marks a look before it reads the ruling Rival's level, and the Sensa worker marks a tick before it reads its level. A wait ends once its worker has put out a zero with no such pass in flight, at once when its worker does not run, or when the 250 ms run out. A GameSense look that reads no level, one that only paints colors, never holds the wait.

---

## Haptics

### The level

`PeripheralOutputs.SetMotors` (`PeripheralOutputs.cs` line 463) stores a row's combined level as float bits: the stronger motor over 65535, since every backend plays one waveform or one intensity. A zero goes through `PeripheralOutputs.StopHaptics` (`PeripheralOutputs.cs` line 484). The first nonzero level after silence raises `HapticsChanged`, which wakes the HID++, GameSense and TouchSense workers so the first pulse of new rumble plays at once. The level is kept whether or not a path is linked now. A backend plays only a linked path, so a device that wakes plays the level the game holds, and a stop sent while it slept is never lost. `PeripheralOutputs.AmplitudeOf` (`PeripheralOutputs.cs` line 495) reads it.

`PeripheralOutputs.IsHapticPeripheral` (`PeripheralOutputs.cs` line 276) adds to `TakesHaptics` a mouse or keyboard a linked PC forwards with rumble. It opens the Force Feedback tab and the Devices page's rumble chip (`InputService.PopulateDeviceRow` (`InputService.cs` line 15382)), and the chip is Identify's button.

### Step 2

`InputManager.ApplyForceFeedback` (`InputManager.Step2.UpdateInputStates.cs` line 671) treats a haptic peripheral the way it treats a Bliss-Box port: a sole writer that records a level and hands it to a worker.

- A haptic mouse or keyboard, or the Sensa row, reports no SDL rumble, so loading it made no `ForceFeedbackState`. The poll thread makes one on first use, after `StopHaptics`, since a new cache starts from zero and a level kept from before the row was removed and found again would otherwise play on.
- `isPeripheralHaptic` joins the Xbox impulse, Padix and Bliss-Box paths past the SDL rumble gate, and like them it needs `ud.Device`.
- On every slot the row is on, the level goes through the chain a gamepad's does: game rumble, macro rumble, constant force, and the row's own Force Feedback settings for that slot. The slots combine by maximum.
- The `isPeripheralHaptic` branch (`InputManager.Step2.UpdateInputStates.cs` line 1234) folds trigger rumble into the motors (`ForceFeedbackState.FoldTriggersForDirectWriter`), since no peripheral has trigger motors. When `PeripheralOutputs.ConsumeResend` (`PeripheralOutputs.cs` line 527) says a silence edge owes the row a resend, the branch marks the snapshot failed. It calls `SetMotors` only when `TryRecordMotorSnapshot` reports a change.
- When the row's last slot goes, it sends a zero once through `SetMotors` (`InputManager.Step2.UpdateInputStates.cs` line 850), under the row's output gate and the Remote Link guards.

### Silence edges and the other writers

`PeripheralOutputs.SilenceHaptics` (`PeripheralOutputs.cs` line 512) zeroes every level and marks each row that was playing as owed one resend, so a level a game still asks for comes back the moment Step 2 runs again instead of reading as unchanged. It runs where Step 2 does not:

| Edge | Site |
|---|---|
| Engine stop | `InputManager.Stop` (`InputManager.cs` line 1885) |
| Crash quiesce | `InputManager.StopAllForceFeedback` (`InputManager.cs` line 2396), which also stops each row's level under its output gate, so a level the poll thread or Identify decided under the gate cannot land after the sweep |
| Focus suspend | `InputManager.ApplyFocusSuspension` (`InputManager.cs` line 3911), with `keepRelayed: true`: a level a Remote Link peer drives keeps playing, as a peer-driven SDL rumble does, since the relay still writes while the engine is suspended and a peer sends a steady level only once |

Idle is no edge. Step 2 runs there and writes the level itself.

The other writers: `InputManager.MarkDeviceOffline` (`InputManager.Step1.UpdateDevices.cs` line 1248) and `SettingsManager.RemoveDevice` (`SettingsManager.cs` line 487) stop a row's level and release its claims. Identify's pulse train (`InputService.IdentifyDevice` (`InputService.cs` line 17204)) sets the level under the row's gate with the quiesce checked again, and ends at the level the snapshot holds. For the train, a row on a controller or on none also holds its shared haptic path (`PeripheralOutputs.BeginIdentify`, ended in the train's `finally`, lapsing 1000 ms past the train's length), so GameSense plays that Rival and the host runs the Sensa worker for a row no controller holds. Steering-angle rumble accepts a haptic peripheral (`InputManager.SupportsSteeringAngleRumble` (`InputManager.SteeringAngleRumble.cs` line 51)).

### HID++ 0x19B0

Logitech has not published the haptic feature. Three implementations agree on it: Solaar (`hidpp20_constants.py` HapticWaveForms, `settings_templates.py` HapticLevel and PlayHapticWaveForm), OpenLogi (`crates/openlogi-hidpp/src/feature/haptic_feedback.rs` HapticFeedbackFeature) and LiveHaptics (`HidppDevice.cpp`). `HidppHapticProtocol` (`HidppHaptics.cs` line 31) follows them.

| Function | Request | Answer |
|---|---|---|
| 0, getCapabilities | none | Payload bytes 4 to 7: the supported-waveform mask, big-endian, bit N for waveform N |
| 1, getConfiguration | none | Byte 0 bit 0: feedback enabled. Byte 1: intensity, 0 to 100 |
| 4, play | waveform, 0, 0 | Not read |

LiveHaptics sends 100 after the waveform byte. Solaar and OpenLogi send zero, and so does PadForge. No setConfiguration is ever sent, so the intensity and the on/off switch in Logi Options+ stay the user's. A frame (`HidppHapticProtocol.Frame` (`HidppHaptics.cs` line 80)) is report ID `0x11`, the device index, the feature index, the function in the high nibble with software ID `0x0C` in the low one, and up to 16 parameter bytes. `0x0C` is none of the IDs Solaar's table lists for other tools (OpenRGB `0x07`, LGSTrayEx `0x0A`, Solaar `0x0B`, G HUB `0x0D`, the firmware `0x0F`) and not LiveHaptics' `0x01`, so an answer meant for Logi Options+ never reads as PadForge's.

`HidppBackend.PlayHaptics` (`HidppBackend.cs` line 1175) plays each haptic unit a linked row asks for, at the strongest level when two rows link it. `HapticRumbleShaper` (`HapticRumbleShaper.cs` line 14) turns the amplitude into pulses:

| Level | Rises at | Falls below | Waveform, then fallbacks |
|---|---|---|---|
| 1 | 0.05 | 0.03 | subtle collision (4), damp collision (3), sharp collision (2) |
| 2 | 0.33 | 0.30 | damp collision (3), subtle collision (4), sharp collision (2) |
| 3 | 0.66 | 0.63 | sharp collision (2), damp collision (3), subtle collision (4) |

The hysteresis keeps rumble that hovers on a boundary from flipping the level every tick. `HapticRumbleShaper.Waveform` (`HapticRumbleShaper.cs` line 54) takes the first of the level's waveforms the unit's mask lists, and `HidppUnit.HasHaptics` (`HidppUnits.cs` line 97) requires at least one of the three. `HapticRumbleShaper.IntervalMs` (`HapticRumbleShaper.cs` line 35) runs linearly from 250 ms at an amplitude of 0.05 to 80 ms at full strength, the cooldown mxhaptics ships for its impact events. Silence resets a unit's interval, so the first pulse of new rumble plays at once. Logitech's Actions SDK describes the sharp collision as a "High-intensity impact simulation", the damp collision as a "Medium-intensity impact with gradual decay" and the subtle collision as "Low-intensity feedback for light contact events". No model list gates the path. Any Logitech device that lists 0x19B0 and one of the three waveforms takes it, the MX Master 4 among them.

The configuration's enable bit, read at discovery and with each check, feeds the Force Feedback tab's line for a unit whose feedback is off in Logi Options+.

### The GameSense tactile path

A tactile Rival's level reaches GG through the GameSense worker above. Every tactile Rival plays the ruling Rival's level. The motor stops at the first ruler check (`RulerMs`, 250) that finds no Rival assigned or buzzed by Identify, and GG gets the mice back `ReleaseMs` (2000) after nothing at all is claimed, colors included.

### Razer Sensa

The Sensa row's level reaches the Interhaptics engine through `SensaHapticsService`, which reads `PeripheralOutputs.AmplitudeOf` for the row's id. `PeripheralOutputHost.SensaLifecycle` (`PeripheralOutputHost.cs` line 716) runs the worker only while the row is linked and either assigned to a virtual controller or buzzed by Identify, and starts a worker that ended on its own again after `SensaRestartMs` (30000), so a missing `HAR.dll` does not spin. [Sensa Haptics Internals](sensa-haptics-internals.md) covers the engine, the worker and the row.

### Remote Link

- The owner advertises rumble for a haptic mouse or keyboard. `InputService.BuildExposedDevices` (`InputService.cs` line 12189) sets `HasRumble` from the device or the row's recorded haptics bit, so the capability does not flap while the device sleeps. A consumer registers a device again when its rumble flag changes (`LinkServer.ReconcileRemoteDevices` (`LinkServer.cs` line 2176)).
- On the consumer, the forwarded mouse shows its Force Feedback tab through `IsHapticPeripheral`, and Step 2 ships its level back to the owner as it does for any forwarded device. The host never links a forwarded device to this PC's vendor channels.
- On the owner, `InputService.ApplyRemoteOutput` (`InputService.cs` line 12608) pays a resend a silence edge owed, records the relayed motors, and calls `SetMotors` with `relayed: true`.
- Vendor rows are not shared. `InputService.IsShareableDevice` (`InputService.cs` line 12387) refuses a `PeripheralOutputRow`, since it stands for this PC's vendor software and has no input.

### TouchSense mice

A Logitech iFeel mouse rumbles once it is bound to WinUSB. Its buzz command is a 7-byte output report with no report ID, which the mouse declares inside its own mouse collection, and Windows opens mouse collections for exclusive system use (Microsoft's table of top-level collections opened by Windows for system use), so a user-mode program cannot write that report to a mouse on Windows' HID driver. The Devices page offers the switch to PadForge's WinUSB package for the three listed models. The bound mouse then gets a row PadForge reads itself and a `TouchSenseUnit` path, and `TouchSenseBackend` plays its level ([TouchSense](#touchsense)). A mouse outside `TouchSenseProtocol.Mice` has no path.

---

## Set Chroma Color

The macro action (#468), `MacroActionType.SetChromaColor` (`MacroItem.cs` line 6881), paints while it is current, the AxisHold duration shape.

1. `InputManager.ExecuteSequentialAction` (`InputManager.Step4b.EvaluateMacros.cs` line 2872) and its extended twin `InputManager.ExecuteSequentialActionRaw` (`InputManager.Step4b.EvaluateMacros.cs` line 5226) call `InputManager.NoteChromaColor` (`InputManager.Step4b.EvaluateMacros.cs` line 2831) with the macro's slot and color on every frame the action is current. Several macros current in one frame leave the last one evaluated, which is how a full-press macro listed below its soft-press twin wins at the bottom of the press.
2. `InputManager.EvaluateSlotMacros` (`InputManager.Step4b.EvaluateMacros.cs` line 466) and `InputManager.EvaluateSlotMacrosExtended` (`InputManager.Step4b.EvaluateMacros.cs` line 4536) end with `InputManager.FlushChromaColors` (`InputManager.Step4b.EvaluateMacros.cs` line 2840), which hands each slot's color for the frame to `MacroChromaSink` once, so a reader never sees the color flip between two macros within a frame. Each macro pass sends one color per controller.
3. The sink is `PeripheralOutputs.AssertChromaMacro` (`PeripheralOutputs.cs` line 895). It packs the tick shifted left 24 bits with the color into one `long` per slot, so one atomic read gives a matching pair. A first assertion, a new color, or one after the window lapsed raises `PeripheralOutputs.ChromaMacroChanged` (`PeripheralOutputs.cs` line 888), which wakes the Chroma worker and the Razer direct worker and no other. A held color asserted every frame raises nothing.
4. `PeripheralOutputs.TryGetChromaMacro` (`PeripheralOutputs.cs` line 920) reads a slot's color while its latest assertion is within `PeripheralOutputs.MacroAssertWindowMs` (`PeripheralOutputs.cs` line 879), 120 ms. The action asserts on every poll, a millisecond apart, so the window measures only the gap after the action ends.

`ChromaBackend.Wanted` (`ChromaBackend.cs` line 221) applies it. For each slot with a live macro, `PeripheralOutputs.DevicesOnSlot` (`PeripheralOutputs.cs` line 951) lists the devices assigned there, and every Chroma category linked to one of them takes the macro's color: the categories of the slot's Razer devices, which reaches every other Razer device of those kinds, or all six when the Razer Chroma row is on the slot. Links do not depend on the Lighting tab's switch, so the macro paints whether or not those tabs control the devices, over every claim on the category. Between two controllers' macros on one category, the smaller `PeripheralOutputs.DisplayedSlotNumber` (`PeripheralOutputs.cs` line 967) wins. A macro on a slot with no Razer device of a category leaves that category alone.

With Synapse closed, a Razer device lit through its own unit takes the macro there. `RazerDirectBackend.MacroOn` gives a unit the live macro of the controller with the smallest displayed number among the ones that hold a row lit through it, ahead of the unit's ruling claim, and the Chroma worker leaves that device's category out of its session (`ChromaBackend.Shadowed`). The unit is then written to for the macro's window with no claim behind it, so the link pass reads the running vendor programs on every pass while such a macro is live (`PeripheralOutputs.AnyChromaMacroOnARazerUnit`).

---

## The route line

`PeripheralRouteText` (`PeripheralRouteText.cs` line 20) builds the ember line on the Force Feedback and Lighting tabs, on the UI thread, from the link table, the backend states, the HID++ units and the direct units. It replaced the Dashboard status lines the global switches carried. `PadPage.SyncTabVisibility` (`PadPage.xaml.cs` line 438) fills both lines and reads `PeripheralOutputs.SlotLive` for the tab's slot. The page runs it again on `LinksChanged`, `StatusChanged` and `ClaimsChanged`, one sync per burst (`PadPage.OnPeripheralOutputsChanged` (`PadPage.xaml.cs` line 138)). While the engine is stopped (`PeripheralOutputs.Running`) nothing reaches any device and both lines are empty, except the Razer Sensa row's `Common_NotAvailableOnArm64`.

`PeripheralRouteText.Haptics` (`PeripheralRouteText.cs` line 30), for the Force Feedback tab, takes `slotLive`: on a slot that is not live the line is empty, since a controller that is gone sends the row no rumble. Only the ARM64 row shows whatever the engine or the slot does.

| Condition | String |
|---|---|
| No haptic path, the Sensa row whose record has haptics, an x64 process | `Pad_ForceFeedback_RouteSensaWaiting` |
| No haptic path, the Sensa row whose record has haptics, an ARM64 process | `Common_NotAvailableOnArm64` |
| No haptic path, any other row whose record has haptics: a Logitech row, or any row while the TouchSense backend runs | `Pad_ForceFeedback_RouteHidppAsleep` |
| A HID++ unit whose feedback is off | `Pad_ForceFeedback_RouteHidppFeedbackOff`, with the unit's name |
| A HID++ unit | `Pad_ForceFeedback_RouteHidpp`, with the unit's name |
| A TouchSense unit | `Pad_ForceFeedback_RouteTouchSense`, with the unit's name, or the row's where the backend read none |
| The tactile path while GG does not answer | `Pad_ForceFeedback_RouteGameSenseWaiting` |
| The tactile path, ruled by another Rival on a controller of this PC | `Pad_ForceFeedback_RouteGameSenseShared`, with that controller's number |
| The tactile path otherwise | `Pad_ForceFeedback_RouteGameSense` |
| The Sensa path while the backend state is `Waiting` | `Pad_ForceFeedback_RouteSensaWaiting` |
| The Sensa path otherwise | `Pad_ForceFeedback_RouteSensa` |

`PeripheralRouteText.Lighting` (`PeripheralRouteText.cs` line 155), for the Lighting tab, takes the slot, `lightsHere` and `claimLevel`. `lightsHere` is, on a live slot, true for a vendor row or a unit row, else the device's Control This Device’s Lighting switch on this slot, and false on a slot that is not live. `claimLevel` is the Lighting Hold this controller's claim carries. A device or a vendor row this controller does not light shows only who else lights it, never a route of its own. The path is the row's first lighting path, and the app is the vendor software behind a shared family (`PeripheralRouteText.LightingApp` (`PeripheralRouteText.cs` line 113)): Razer Synapse, Logitech G HUB (Logitech Gaming Software while `PeripheralPresence.LogitechGamingSoftware` holds) or SteelSeries GG. The first condition that holds picks the line. `PeripheralRouteText.CannotLight` (`PeripheralRouteText.cs` line 296) gives `Common_NotAvailableOnArm64` for an empty paintable list in the ARM64 build, and `Pad_Lighting_RouteCannotLight` otherwise.

| # | Condition | String |
|---|---|---|
| 1 | No lighting path, and this controller lights a row whose record has lighting: a Logitech row, or any row but a vendor row while a direct backend runs | `Pad_Lighting_RouteAsleep` |
| 2 | The Logitech LIGHTSYNC row while `LedSdkPaintable` is an empty list, on every controller it is on, one that is gone included | `CannotLight` |
| 3 | A vendor row on a slot that is not live | `Pad_Lighting_RouteOtherControllerOnly`, with the number of the controller where the same row rules one of its paths, while its software answers. Otherwise no line |
| 4 | A vendor row whose software does not answer | `Pad_Lighting_RouteVendorRowWaiting`, with the app and the row's examples |
| 5 | A vendor row that rules none of its paths here while the same row on another controller rules one | `Pad_Lighting_RouteOtherController`, with that controller's number |
| 6 | Any other vendor row | `Pad_Lighting_RouteVendorRow`, with the app and the row's examples |
| 7 | An LED SDK type outside `LedSdkPaintable` | `CannotLight` when this controller lights it, else no line |
| 8 | Windows Dynamic Lighting lights a LampArray unit the row is linked to | When this controller lights it: `Pad_Lighting_RouteWindowsLightingBuiltIn` for a keyboard row whose unit is built into the PC, which adds what turning Windows' switch off costs on some laptops, else `Pad_Lighting_RouteWindowsLighting`. Otherwise no line |
| 9 | The app does not answer | `Pad_Lighting_RouteWaiting` when this controller lights it, else no line |
| 10 | A vendor row rules the path | `Pad_Lighting_RouteSharedVendorRow`, with the app, the row's name and its controller's number |
| 11 | The same device on another controller rules it, or another row of the device on another controller rules its direct path | `Pad_Lighting_RouteOtherController` when this controller lights it, else `Pad_Lighting_RouteOtherControllerOnly`, with that controller's number |
| 12 | Another row of the same directly lit device on this controller rules it | `Pad_Lighting_RouteOtherRow` when this controller lights it, else `Pad_Lighting_RouteOtherRowOnly` |
| 13 | Another device on a shared path rules it | `Pad_Lighting_RouteShared`, with the app and that device's controller number |
| 14 | This controller does not light it | no line |
| 15 | A unit this controller lights on its own, of any unit family | With the unit's name as its backend read it, or the row's: `Pad_Lighting_RouteDirectHostMode` at hold 2, `Pad_Lighting_RouteDirectPower` at hold 1, else `Pad_Lighting_RouteDirect`. The hold is the smaller of `claimLevel` and `DeviceLinks.MaxClaimLevel` |
| 16 | A shared path | With the app: `Pad_Lighting_RouteThroughOrDirect` when the row has a path of its own waiting for the program to stop (`DeviceLinks.DirectWhenClosed`), else `Pad_Lighting_RouteThrough` |

Rows 10 to 13 apply only to a ruling claim with a player number. The examples a vendor row names (`PeripheralRouteText.VendorRowExamples` (`PeripheralRouteText.cs` line 126)) are what its software lights that PadForge does not read: `Pad_Lighting_VendorRowExamples_Chroma`, `_LedSdk` and `_GameSense`. SteelSeries GG binds no mousepad type, so its row names headsets alone.

---

## The tabs and the switch

`PadPage.SyncTabVisibility` (`PadPage.xaml.cs` line 438) gives a device that `IsHapticPeripheral` accepts the Force Feedback tab and its route line (`PeripheralHapticsRoute`). A device with lighting by record or path and no Sony lightbar of its own gets the Lighting tab with the lightbar's mode card and `PeripheralLightingPanel`, without the DualShock 4 or DualSense art. The panel's Control This Device’s Lighting check box binds `DeviceConfig.PeripheralLightingEnabled` and hides for a vendor row or a unit row, whose device type is `PeripheralLighting`.

`DeviceSlotConfig.PeripheralLightingEnabled` (`DeviceSlotConfig.cs` line 1003) is per (virtual controller, device) and off by default, so assigning a keyboard for its keys never repaints it. It is saved with the device's slot config, counts as a configuration on its own (`SettingsService.IsDeviceConfigConfigured` (`SettingsService.cs` line 2889)), and has a reset button.

`DeviceSlotConfig.PeripheralClaimLevel` is the Lighting Hold under that switch, per (virtual controller, device) too: `Colors` (0, the default), `Power` (1) and `HostMode` (2). The number is the hold a claim carries and the place of the option in the picker, so a member is appended and never renumbered. The saved form is the name, and a value the enum does not name leaves the property as it was. The switch and the hold live in one field (`PeripheralLightingClaim`), so a reader on another thread never pairs the switch of one moment with the hold of the next. A load writes them in the order that never claims a device at a hold neither the outgoing nor the incoming settings asked for: the hold first for a device being taken, the switch first for one being let go.

The Lighting Hold row shows only for a mouse or keyboard that offers a hold. `PadPage.OfferedLightingHold` reads the row's `DeviceLinks.MaxClaimLevel` while a path of its own lights it, and the record's bits 4 and 8 while it sleeps or is unplugged. `PadPage.ShowLightingHold` takes the last option out of the list for a device that does not offer hold 2. The option stays in the list, collapsed and disabled, so a choice of it saved earlier still shows as the selection, and the picker's tooltip and the options' set size follow the shorter list.

A Copy From or a Paste whose source slot did not hold the device applies another device's settings to it, all but the switch and the hold, which stay the device's own (`SettingsService.ApplyStandInDeviceSlotConfigData`). A copy that carried a mouse's switch onto a keyboard would start the controller lighting it, and a hold carried to another device would switch that device's on-board memory mode off on a choice nobody made for it.

---

## Migration of the Dashboard switches

The Dashboard's Lightbar Mirrors section, with its Razer Chroma (#373) and Logitech LIGHTSYNC (#382) toggles, and its Razer Sensa section (#374) are gone, along with `ChromaLightbarService` and `LightsyncLightbarService`. `PeripheralSwitchMigration` (`PeripheralSwitchMigration.cs` line 38) turns each switch that was on into an assignment of the row that replaced it.

Each switch had a global value and a nullable per-profile opinion, and profiles own their device assignments. `AppSettingsData.EnableChromaLightbar` (`SettingsService.cs` line 6904), `EnableSensaHaptics` (`SettingsService.cs` line 6912) and `EnableLightsyncLightbar` (`SettingsService.cs` line 6920), and their `bool?` twins `ProfileData.EnableChromaLightbar` (`SettingsService.cs` line 7896), `EnableLightsyncLightbar` (`SettingsService.cs` line 7902) and `EnableSensaHaptics` (`SettingsService.cs` line 7909), are read once and never written: each `ShouldSerialize` method returns false. `PeripheralSwitchMigration.Switches` (`PeripheralSwitchMigration.cs` line 49) lists them. The Sensa switch is `Available` only where `PlatformSupport.SensaAvailable` holds, so on ARM64 it assigns nothing and only clears.

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

`SettingsService.LoadFromFile` (`SettingsService.cs` line 244) runs the migration after `LoadProfiles`, the ghost-mapping guard and the motion backfill, since only from there on is the live topology the active profile's. A change sets `_peripheralSwitchesMigratedOnLoad`. `SettingsService.Initialize` (`SettingsService.cs` line 177) and `SettingsService.Reload` (`SettingsService.cs` line 5942) clear the dirty flag after a load and then mark the settings dirty again for it, so the migrated file is saved. `ProfileTransfer.Import` (`ProfileTransfer.cs` line 131) runs `PeripheralSwitchMigration.MigrateImported` (`PeripheralSwitchMigration.cs` line 63) on a profile file exported before #494, which carries opinions and no global value. Each assignment writes a `CFG #494 migrated ...` diag line.

---

## Threads

| Thread | Does |
|---|---|
| Poll thread | Phase 1m's rows, Step 2's `SetMotors`, Set Chroma Color's assertions |
| The effects dispatchers (their timer, config changes, the peripheral refresh) | `SetLighting` and the releases, under the device lock |
| HIDMaestro output reader | `GameLightbar.Capture` and `NoteFrame` |
| `PeripheralLink` | Presence, the walk of the present HID collections, the link pass, the prune, the Sensa lifecycle |
| `PeripheralHidpp` | Every HID++ request and write but the crash path's hand-back. Answers arrive on each collection's `VendorHidReader` thread |
| `PeripheralLampArray`, `PeripheralSteelSeries`, `PeripheralRazer` | Every report to a device of the family but the crash path's hand-back |
| `PeripheralTouchSense` | Every buzz frame |
| `TouchSenseMouse`, one per bound mouse | The mouse's input reports, and the close of its channel when the reader leaves |
| `PeripheralGameSense` | Every GameSense call |
| Thread-pool tasks | Every Chroma REST call, every LED SDK native call, and the look for bound TouchSense mice with each open of one |
| `SensaHaptics` | Every Interhaptics call |
| The thread the crash path runs on | The one-shot hand-backs of whatever is still on a backend's crash record, each bounded |
| UI thread | The route lines, marshaled from `LinksChanged`, `StatusChanged` and `ClaimsChanged`, and the HID arrival notice that asks the host for a walk |

Every setter on `PeripheralOutputs` is lock-free or takes only that class's own leaf state, so the poll thread and the dispatchers never wait on a backend's I/O. `PeripheralOutputs.SetBackendState` (`PeripheralOutputs.cs` line 372) raises `StatusChanged` only on a change. The events fire on any thread, and their owners marshal.

---

## ARM64

The Sensa row never opens in an ARM64 process: phase 1m and the linker both need `SensaPlatform`, and the migration only clears the Sensa switch. The LED SDK path loads whatever engine `ServerBinary` names, and an ARM64 process loads ARM64 libraries only, so that path works only where Logitech installs an ARM64 engine. The HID++, Chroma and GameSense paths are HID reports and local HTTP, with nothing native to load. The LampArray, Razer and SteelSeries workers send HID reports and the TouchSense worker WinUSB transfers, both through libraries Windows ships for every architecture.

---

## Diag lines

| Line | When |
|---|---|
| `PERIPHERAL links: {rows} row(s), {paths} path(s)` | A link pass published a new table |
| `PERIPHERAL link pass fault: {type}` | A link pass threw |
| `PERIPHERAL Sensa worker started (row assigned)` | The Sensa row was assigned |
| `PERIPHERAL Sensa worker started (Identify)` | Identify buzzes the Sensa row while no controller holds it |
| `PERIPHERAL Sensa worker stopped (row unassigned)` | It left its last controller, or its Identify train ended |
| `PERIPHERAL Sensa worker ended on its own, starting again later` | The worker ended while the row stayed assigned or buzzed by Identify |
| `PERIPHERAL {family} backend not made: {type}` | A direct backend's constructor threw, and the host runs without that family |
| `PERIPHERAL {backend} left out, its family fault: {type}` | A direct backend could not name its family |
| `PERIPHERAL {family} start fault: {type}`, `rescan fault: {type}` | A direct backend threw from `Start` or `Rescan` |
| `PERIPHERAL {family} snapshot fault: {type}`, `gave no snapshot` | A direct backend's snapshot could not be read. Written once per backend |
| `PERIPHERAL HID++ found '{name}' index=... type=... haptic=... mask=... rgb=... zones=... battery=... charge=... effect=... perkey=...` | A unit was found |
| `PERIPHERAL HID++ '{name}' index=... has no haptics or RGB` | A unit has nothing to offer |
| `PERIPHERAL HID++ '{name}' lighting claimed at level {n}` | A unit's claim and its first paint went out, at that hold |
| `PERIPHERAL HID++ '{name}' refused the read of its on-board memory mode (error 0x..), claiming without the switch` | A claim at hold 2 on a device that refuses the mode read |
| `PERIPHERAL HID++ '{name}' was back in its on-board memory mode, claiming again` | A keep-alive at hold 2 found the mode the claim had switched away from |
| `PERIPHERAL HID++ '{name}' lighting claim was gone, claiming again` | A keep-alive's claim read showed the cluster flag gone |
| `PERIPHERAL HID++ '{name}' refused the Host streaming effect, painting on` | A refused `Select` frame |
| `PERIPHERAL HID++ '{name}' refused a per-key frame, lighting its clusters alone` | The unit fell back to `ClusterPlan` |
| `PERIPHERAL HID++ '{name}' lighting handed back` | The plan's hand-back went out |
| `PERIPHERAL HID++ '{name}' lighting handed back, owed since the unit was let go` | An owed hand-back was paid when the unit was found again |
| `PERIPHERAL HID++ '{name}' is another device than the one owed a hand-back at its slot, which is dropped` | Another device answered at the slot of a unit that was owed |
| `PERIPHERAL HID++ '{name}' lighting left to the Logitech program that started` | G HUB or LGS started while the unit was claimed |
| `PERIPHERAL HID++ '{name}' stopped answering` | A check found it asleep or gone |
| `PERIPHERAL HID++ write failed, dropping {path}` | A collection went away |
| `PERIPHERAL HID++ worker fault: {type}` | The worker threw |
| `PERIPHERAL HID++ previous worker still running after {n} ms, starting anyway` | A new worker's bounded wait for a predecessor held in a probe ran out. The LampArray, Razer, SteelSeries and TouchSense workers write the same line under their own names |
| `PERIPHERAL LampArray found {label} VVVV:PPPP lamps={n}` | A unit was described |
| `PERIPHERAL LampArray VVVV:PPPP not used: {why}` | A collection's reports are not the ones PadForge drives |
| `PERIPHERAL LampArray {label} is asked again later: {why}` | The collection did not answer. Written once until it answers |
| `PERIPHERAL LampArray {label} lamps read: {n}, painted as {runs}` | The first claim read the lamps |
| `PERIPHERAL LampArray {label} lamps could not be read ({why}), painting without their level counts` | The unit is painted blind |
| `PERIPHERAL LampArray {label} lighting claimed`, `lighting handed back` | AutonomousMode off, and on |
| `PERIPHERAL LampArray {label} is lit by Windows Dynamic Lighting`, `is no longer lit by Windows Dynamic Lighting` | The switch moved |
| `PERIPHERAL LampArray {label} lighting left to Windows Dynamic Lighting` | A claimed unit turned Windows-lit, and nothing was sent |
| `PERIPHERAL LampArray {label} is asleep: {why}`, `answers again`, `left` | A failed write, the describe that follows, and a collection that left the walk |
| `PERIPHERAL Razer found '{name}' pid=... family=... collections={n}` | A unit was listed |
| `PERIPHERAL Razer '{name}' lighting claimed (id {id})`, with `, fallback {n}` on a fallback paint | The claim and its first color went out under that transaction ID |
| `PERIPHERAL Razer '{name}' answers reads under {id} and took no report of its claim, writing under {id} next` | A device answered the claim read and then took no report of the claim, so its writes move to the row's next transaction ID and its reads stay under the one that answered |
| `PERIPHERAL Razer '{name}' has its brightness at 0, so no color shows on it` | The claim read showed the device's own brightness at 0. It is left that way and named once |
| `PERIPHERAL Razer '{name}' refused its paint, trying fallback {n}`, `refuses every paint known for it, leaving it to its own lighting` | The fallbacks |
| `PERIPHERAL Razer '{name}' takes no color on its region {led}, leaving that region to the device` | A region the device named and then refused |
| `PERIPHERAL Razer '{name}' lighting handed back`, `did not take its hand-back`, `lighting let go, with nothing to hand back` | The end of a claim |
| `PERIPHERAL Razer '{name}' lighting handed back, owed since it stopped answering` | An owed hand-back was paid |
| `PERIPHERAL Razer '{name}' lighting left to the Razer program that started` | Synapse or Razer Central started |
| `PERIPHERAL Razer '{name}' does not answer, asking again later`, `handle failed, closing it and asking again later`, `answers again`, `left` | Asleep, awake, gone |
| `PERIPHERAL Razer lock not available (...), going on without it` | The shared mutex could neither be created nor opened. Written once |
| `PERIPHERAL SteelSeries found {pid} {family} interface={n}` | A unit was listed |
| `PERIPHERAL SteelSeries {pid} {family} lit gen3={bool}` | The first color of an open went out |
| `PERIPHERAL SteelSeries {pid} lighting handed back` | The family's hand-back went out |
| `PERIPHERAL SteelSeries {pid} lighting handed back, owed since it failed` | An owed hand-back was paid |
| `PERIPHERAL SteelSeries {pid} left to SteelSeries GG, which started` | GG started while the unit was lit |
| `PERIPHERAL SteelSeries {pid} {why}, listed asleep`, `answers again` | Asleep, awake |
| `TouchSense: opened VVVV:PPPP at {path} (pointer={bool})` | Phase 1n opened a bound mouse, and whether its input report is read as a pointer |
| `TouchSense: open failed for VVVV:PPPP at {path}, trying again every {n} s` | The open failed. Written once until the mouse opens |
| `PERIPHERAL TouchSense found VVVV:PPPP at {path}`, `gone {path}` | A bound mouse was found, or the look no longer finds it |
| `PERIPHERAL TouchSense write failed, closing {path}`, `has no open channel for {path}`, `answers again {path}` | Asleep, awake |
| `PERIPHERAL {name} worker fault: {type}` | A direct worker threw, under `LampArray`, `Razer`, `SteelSeries` or `TouchSense` |
| `PERIPHERAL LED SDK session open` | A session opened |
| `PERIPHERAL LED SDK handed back` | A session ended |
| `PERIPHERAL LED SDK load failed: {detail}` | `TryLoad` failed. Written once per detail until a load works, the software leaves or nothing is claimed |
| `PERIPHERAL LED SDK engine cannot paint any claimed type` | The engine lacks the calls the claimed types need. Written once per set of claimed types until a session opens, the software leaves or nothing is claimed |
| `PERIPHERAL LED SDK calls failing, reinitializing` | The third failed liveness round |
| `PERIPHERAL LED SDK stop timed out after {n} ms, worker orphaned inside the SDK` | `Stop` timed out |
| `PERIPHERAL LED SDK waiting for the orphaned worker of the previous session to leave the SDK` | A new worker found a live orphan |
| `PERIPHERAL LED SDK worker fault: {type}` | The worker threw |
| `PERIPHERAL Chroma session for {categories}` | A session opened |
| `PERIPHERAL Chroma waiting for Synapse` | The init failed. Written once until a session opens or nothing is claimed |
| `PERIPHERAL Chroma session lost` | A heartbeat or a call failed |
| `PERIPHERAL Chroma handed back` | Nothing is wanted any more |
| `PERIPHERAL Chroma effect rejected: {category ...}, retrying on the next poll` | A rejection, once per category and code until that category is accepted or a new session opens |
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
| `PeripheralOutputsTests.cs` | `HidppBackendTests` | The worker plays only a linked unit, stops, drops a failed path, reads a Bolt pairing table and asks only paired slots, the idle and fast ticks and the quiet second (read from what the worker recorded), a restart after a timed-out stop, the bounded wait for a wedged predecessor, a failed container lookup asked again, a Bluetooth LE device on page `0xFF43` |
| `PeripheralOutputsTests.cs` | `GameSenseBackendTests` | The ruling Rival's level plays, the motor stops at once, GG gets the mice back after the release delay, the crash wait sees the zero, the crash wait holds for a look that read its level before the quiesce and never for a look that reads none, Identify on an unassigned Rival, the idle and fast ticks, a restart after a timed-out stop |
| `PeripheralOutputsTests.cs` | `PeripheralOutputHostTests` | The host against scripted backends, waiting on link passes (`PeripheralOutputHost.PassCount`): the host's gate against a stop that outlives a pass, the container cache, the Sensa worker under Identify, a restart after a timed-out stop, the refresh when a slot comes or goes |
| `PeripheralOutputsTests.cs` | `PeripheralSwitchMigrationTests` | The ruling slot, one entry per profile, each profile's own value, the live settings, the default topology, a row this PC cannot open, imported profiles, the lightbar slot, rebuilt orders |
| `PeripheralOutputsTests.cs` | `PeripheralWiringTests` | Source pins: Step 2's branch, every silence edge, the other writers, the Remote Link legs, the records before the table, the crash path's GameSense and Sensa waits, the save after a migration on load |
| `PeripheralLightingTests.cs` | `PeripheralLightingTests` | Claims and the ruling, pruning, `ClaimsChanged`, the macro window and its wake, the charge, the linker's lighting rules, the route line, the game's lightbar phases and its trust gate, the DualSense order, the dispatcher lane and its timer, the HID++ claim, reassert and crash hand-back, GameSense colors, the switch's persistence, the mirror switches' migration |
| `DirectPathSeamTests.cs` | `DirectPathLinkingTests` | The append-only family numbers, the order of `ChooseLighting` for each vendor, shadows, the LampArray matching rules inside and outside the PC's own container, orphans and their hold, a unit row's one path, asleep units, the hold after a unit left. Two tests run generated inputs: no row ever holds two lighting families, and with no direct units every row links as it did before |
| `DirectPathSeamTests.cs` | `DirectPathPlumbingTests` | The running flags from image names, the fast and the full read of the running programs, the walk's verdict per path, the open ladder, the padded write, the bounded call, the unit row's identity, the TouchSense binding's texts in every locale, the recorded holds |
| `DirectPathHostTests.cs` | `DirectPathFacadeTests` | A claim's hold and the ruling claim's, what counts as a claim a vendor program would take, the status change of the direct units, every new route line, the direct strings in every locale, a unit row lit with no switch, the HID arrival that asks for a walk |
| `DirectPathHostTests.cs` | `DirectPathHostTests` | The host against scripted direct backends on a clock the bench sets: a backend that cannot be made, start or name its family, a snapshot read that throws, when the collections are walked and the floor between two walks, a pass that outlives `Stop`, the records held after a unit left, the read of the running programs on every pass while a device is lit on its own, the crash path's order and its one deadline, the unit rows opening and retiring |
| `HidppLightPlanTests.cs` | `HidppLightFrameTests`, `HidppLightPlanTests`, `HidppLightProbeTests` | The frames byte for byte, each plan's claim, paint, keep-alive and hand-back at each hold, and the lighting probe |
| `HidppLightPlanTests.cs` | `HidppLightWorkerTests`, `HidppOffLimitsTests` | The worker against scripted channels: the claim recorded before it goes out, pacing, awaited frames, the fallback from per-key frames, the mode read and its write-back, a Logitech program that starts, the owed hand-back, and the test host's refusal of a real HID++ collection |
| `LampArrayProtocolTests.cs` | `LampArrayProtocolTests` | The reports byte for byte, the descriptor's shape check and its cross-check against the parser's layout, runs and level scaling |
| `LampArrayBackendTests.cs` | `LampArrayRulesTests`, `LampArrayBackendTests`, `LampArrayUnitRowTests`, `LampArrayOffLimitsTests` | The container rule and Windows' lighting switches, the worker against scripted channels (the lamp read, the claim, the hold, the hand-back, a unit Windows starts to light, the owed hand-back, the crash path), the unit rows end to end, and the test host's refusal |
| `LampArrayBackendTests.cs` | `LampArrayLiveTests` | `Live_DescribesTheRealLampArrayCollections`, which runs only with `PADFORGE_LIVE_LAMPARRAY=1` and reads this PC's own collections without writing a report |
| `RazerDirectProtocolTests.cs` | `RazerDirectProtocolTests` | The report layout and checksum, each family's reports, and the product table |
| `RazerDirectBackendTests.cs` | `RazerDirectBackendTests`, `RazerGuardTests` | The worker against scripted channels: the transaction ID settled one attempt at a time, slow replies, the effect hold, fallbacks, Set Chroma Color, a Razer program that starts, the owed hand-back, the crash path. The guard on a mutex of its own |
| `SteelSeriesDirectProtocolTests.cs` | `SteelSeriesDirectProtocolTests` | Each family's frames, the model table, and that no builder makes a command that saves |
| `SteelSeriesDirectBackendTests.cs` | `SteelSeriesDirectBackendTests` | The worker against scripted channels: pacing, the claim's re-assert, the dongle's answer and its `40 FF`, the gated boards, GG starting, the owed hand-back, the crash path |
| `TouchSenseProtocolTests.cs`, `TouchSenseChannelTests.cs` | `TouchSenseProtocolTests`, `TouchSenseChannelTests` | The frames and the strength scale, the descriptor checks, and the channel's open, send and close over a scripted WinUSB interface |
| `TouchSenseBackendTests.cs`, `TouchSenseMouseTests.cs` | `TouchSenseBackendTests`, `TouchSenseMouseDeviceTests`, `TouchSenseMiceLaneTests` | The worker's frames and their timing, the row a bound mouse gets, and phase 1n's sweep, registration and reopen |
| `TouchSenseBindingTests.cs` | `TouchSenseBindingTests` | The bound paths, the buzz report read from a node, the opt-in offer and its one-at-a-time refusal, and a live test that runs only with `PADFORGE_LIVE_TOUCHSENSE=1` |
| `HidDevicesOffLimitsTests.cs`, `RazerMutexOffLimitsTests.cs`, `TouchSenseOffLimitsTests.cs` | The classes of the same names | The test host's refusals hold: no real HID open or write, no shared Razer mutex, no look for or open of a bound mouse |
| `LedSdkBackendTests.cs` | `LedSdkBackendTests` | A scripted `ILogiLedNative`: no load with nothing claimed, the session's call order, the whole-device call first and every type over it, engines without the target or zone call, the restore when a type leaves, the fail streak, a type that fails alone, a refused init, orphans, an engine loaded again after the retry interval, a failing load logged once |
| `ChromaBackendTests.cs` | `ChromaBackendTests` | The BGR integer and the init body, the result codes, the wanted categories, the Chroma row filling the rest, Set Chroma Color's precedence and window and its release at the lapse, a rejection logged once per category and code, the waiting line logged once |
| `SetChromaColorMacroTests.cs` | `SetChromaColorMacroTests` | The assertion's slot, both macro loops asserting every frame, the last macro of a frame heard once, the duration, persistence, the editor |
| `HidppHapticsTests.cs` | `HidppHapticsTests` | The shaper's thresholds, interval and fallbacks, the frames and reply matching, the probe against scripted channels, the GameSense client against a local server, and `Live_ProbesTheRealHidppCollections`, which runs only with `PADFORGE_LIVE_HIDPP=1` |
| `SensaHapticsTests.cs` | `SensaHapticsTests` | The real Interhaptics engine, on [Sensa Haptics Internals](sensa-haptics-internals.md) |

---

## Related pages

- [Sensa Haptics Internals](sensa-haptics-internals.md): the Interhaptics engine behind the Razer Sensa row.
- [Logitech G-Keys Internals](logitech-g-keys-internals.md): the other Logitech library PadForge loads.
- [Driver Installation Internals](driver-installation-internals.md#opt-in-bindings): the switch that binds a TouchSense mouse to WinUSB and gives it back.
- [Remote Link Internals](remote-link-internals.md)
- [Input Pipeline](input-pipeline.md)
- [Lighting](../features/lighting.md) and [Force Feedback](../features/force-feedback.md): the tabs a lit or haptic peripheral shares with a gamepad.

---

*Last updated for PadForge 5.1.0.*
