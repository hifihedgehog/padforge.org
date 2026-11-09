# Profile Import Internals

*How PadForge reads a reWASD `.rewasd` or a DS4Windows profile `.xml` as data, translates it into a `ProfileData`, and reports every binding before the user accepts it.*

This is the developer-side companion to [Import from reWASD and DS4Windows](../guides/profile-import.md) and issue #561.

---

## Files

| File | Role |
|---|---|
| `PadForge.App/Common/ConfigImport/ForeignConfigReader.cs` | Size cap, kind detection, the safe JSON and XML parsers, sibling-file reads. |
| `PadForge.App/Common/ConfigImport/ForeignConfigImporter.cs` | Entry point (`Translate`, `TranslateCore`), `ForeignImportResult`, the `ImportReasons` keys, the file dialog's places. |
| `PadForge.App/Common/ConfigImport/ImportBuilder.cs` | `ImportInput`, `ImportOutput`, `ImportMacro`, and `ImportBuilder`, which both translators feed and which writes the profile. |
| `PadForge.App/Common/ConfigImport/RewasdTranslator.cs` | reWASD schema 3 to builder calls. |
| `PadForge.App/Common/ConfigImport/Ds4WindowsTranslator.cs` | DS4Windows profile XML to builder calls. |
| `PadForge.App/Common/ConfigImport/DirectInputKeys.cs` | DirectInput scan code to virtual key, through the active keyboard layout. |
| `PadForge.Engine/Common/Mapping/BoundedReads.cs` | The bounded source descriptors (`Between`, `Sector`, `Stage`) the importers write and the engine reads. |
| `PadForge.App/Views/ImportConfigDialog.xaml(.cs)` | The preview. |
| `PadForge.App/MainWindow.xaml.cs` | `OnImportProfile`, `ImportProfileFromFile`, `ImportForeignConfig`, and the sink `AddWorkshopProfile`. |
| `PadForge.App/Views/ProfilesPage.xaml.cs` | The drop zone (`IsImportableFile`, `ProfileList_Drop`). |

The report type is the Workshop importer's: `TranslationReport` and `TranslationStatus` (`PadForge.SteamWorkshop/Translation`). The reason vocabulary is separate. `ImportReasons` holds `Import_Tr_*` resource keys, and Steam's list stays locked to what its translator emits.

---

## Entry points

`OnImportProfile` opens a `Microsoft.Win32.OpenFileDialog` whose first filter is `Profiles_ImportFilterAll` over `*.pfprofile;*.rewasd;*.xml`, followed by the `.pfprofile` filter, `FileDialog_ForeignProfileFilter` and all files. `ForeignConfigImporter.ProfileFolders` yields `CommonDocuments\reWASD\Profiles` and `ApplicationData\DS4Windows\Profiles` when each exists, and each becomes a `FileDialogCustomPlace`.

`ProfilesPage.IsImportableFile` accepts a `.pfprofile` or anything `ForeignConfigImporter.HandlesFile` accepts (`.rewasd` or `.xml`, case-insensitive). The drop handler calls `ImportProfileFile` once per accepted file.

`ImportProfileFromFile` sends anything that is not a `.pfprofile` to `ImportForeignConfig`, which calls `ForeignConfigImporter.Translate(path)`. A refused result puts `Strings.Get(result.RefusedKey)` on the status bar (`SetStatus(..., persist: true)`) and stops. Otherwise it shows `ImportConfigDialog` with `ImportSink = AddWorkshopProfile`, the sink the Workshop and starter profiles land through. The dialog calls the sink with `applyAfter: false`, so the active profile is untouched. `AddWorkshopProfile` dedupes the name with `SettingsManager.UniqueProfileName`, adds the profile and its list item, and marks settings dirty. The status line is `Status_WorkshopImported_Format` with the report's three counts.

---

## Reading the file

`ForeignConfigReader` treats the file as hostile.

| Guard | Value |
|---|---|
| `MaxFileBytes` | 16 MB. `ReadCapped` checks `FileInfo.Length` before reading a byte. |
| Kind | `Detect` skips a UTF-8 BOM and whitespace. `{` is reWASD. Otherwise the bytes must parse as XML whose root local name is `DS4Windows`. The extension never decides. |
| JSON | `JsonDocument.Parse` with `MaxDepth = 64`, trailing commas allowed, comments skipped. |
| XML | `DtdProcessing.Prohibit`, `XmlResolver = null`, `MaxCharactersFromEntities = 1024`, `MaxCharactersInDocument = MaxFileBytes`. A DTD refusal is reported as `FileHasDtd`, so a hostile file is not called merely unrecognized. |
| Siblings | `TryReadSibling` reads a file one folder above the profile's folder (`Actions.xml`, `Auto Profiles.xml`) through the same cap and parser. Absent or malformed means the extra data is not there. |

`ForeignConfigImporter.Translate(bytes, path)` wraps `TranslateCore` and turns `InvalidOperationException`, `FormatException`, `ArgumentException`, `KeyNotFoundException`, `IndexOutOfRangeException`, `NullReferenceException` and `OverflowException` into a `FileNotConfig` refusal. The wrong-kind sweep tests call `TranslateCore` directly, so the guard cannot hide a throw.

`RewasdTranslator.Translate` refuses a root that is not an object or whose `schemaVersion` major is not 3 (`RewasdOtherVersion`). `TooManyEntries` refuses (`FileTooLarge`) more than `MaxShifts` = 64 shifts, more than `MaxTableEntries` = 5000 masks, mappings, commands, radial circles, radial sectors or unheritable masks in one shift, or a mask or shift `set` of more than `MaxSetInputs` = 4 inputs. Radial sub-menus are walked with a visited set and a depth limit of 8, because a sector can point at its own circle.

---

## ForeignImportResult

| Member | Meaning |
|---|---|
| `Kind` | `Rewasd` or `Ds4Windows`. `ToolName` spells it as each project does. |
| `Profile`, `Report` | The `ProfileData` and its `TranslationReport`. |
| `ReadsKeyboard`, `ReadsMouse`, `ReadsController` | Drive the preview's notes. |
| `Runs`, `Starts` | Programs the buttons run and programs the profile starts on load, collected by `ImportBuilder.Run`. |
| `RefusedKey`, `Refused` | An `Import_Tr_*` key for a refused file. |
| `HasSlots` | At least one `SlotCreated`. The dialog disables **Import** without it. |

---

## The builder

Both translators describe bindings per layer and per physical input, and `ImportBuilder.Finish(name, executables)` turns the description into a `ProfileData`. The slot assembly follows `WorkshopProfileMaterializer` and `StarterProfileCatalog.Wrap`.

### Inputs and outputs

`ImportInput` is one physical input in PadForge's source grammar. `Control` is the identity a layer overrides: the same physical input carries the same string on every layer (`kb:<vk>`, `ms:<id>`, `ds:<control>`). `Gate` is a second read on the same device, `Band` a bounded read of the same input (below), and `EdgeOnly` marks a moment such as a touch start that only a macro can carry. `ToSource` gives a `MappingSource`, and `ToTriggerEntry` a `MacroItem.TriggerInputEntry`: a named keyboard or mouse button rides the raw-button form the macro editor records, everything else the descriptor form.

`ImportOutput` is one thing the file sends. `HasRow` is false for a key outside the keyboard row engine's closed list (`SteamInputVkTable.IsRowKey`) and for a stick or trigger value below full scale or relative, because a press reads full scale on a stick row whatever its `Sensitivity`. Those ride macros. It lowers to actions with `Tap`, `Down`/`Up`/`Flip` (`ToggleKey`, `ToggleMouseButton`, `ToggleVcButton` with `LatchDirection`, or `AxisSetLatched`/`AxisLatchRelease`/`ToggleVcAxis`), `Pulse` (the repeat-while-held actions), and `Add` (`AxisAdd`). `AxisPayload` uses the Workshop materializer's frames: triggers on 0..32767, stick Y negated.

### Slots

Pads come first in file order, one per `DeclarePad`, each with `MappingSet.Authoritative = true`. A Keyboard + Mouse slot follows when a binding targets keyboard or mouse output (pad id 0), or when there are macros or blocks and no pad. A file of pad bindings with no declared pad gets an Xbox slot. Unclaimed slots get a plain `MappingSet`, so a slot the user adds later automaps normally. Activators, menus, the gyro engage stamp and the `Workshop*` stamps (curves, rumble percent, idle disconnect, battery colors, gyro dead zone, touchpad glide) ride every claimed slot, because the layer and menu runtimes are per slot. `WorkshopTuningApplier` folds the stamps onto the assigned device later, only over its defaults.

### Merged keyboard and mouse rows

Keyboard sources name `AllKeyboardsGuid` and mouse sources `AllMiceGuid`: `SdlKeyboardWrapper.BuildGuid("aggregate://keyboards")` and `"aggregate://mice"`, hashes of fixed paths and so the same on every PC. A source with no device would be wrong here: an (Any Device) `Button 9` also fires on a gamepad's right stick click, and `Button 0` on its A. `AssignMergedDevices` adds a `ProfileEntry` for each slot whose rows, activators or macro triggers read either guid, with `ProductGuid = Guid.Empty`. A product guid would let the profile apply's same-product fallback rebind those rows to one physical keyboard. The controller is left for the user to assign.

### Layers

In reWASD and DS4Windows a layer overrides by input: while it is on, a control it maps loses its Base mapping and every other control keeps its own. PadForge's rows override by output: a layer row replaces the Base row of its target. Writing the file's rows as they stand would double-fire one way and silence the physical button behind an output the other way.

`Finish` works out each layer's own controls (`OwnControls`): the controls it binds, the controls a macro on it reads, the ones it blocks (`Remove`, reWASD's Do Not Inherit), and for an unlock layer every Base control that reads the keyboard or mouse it hands back, chords included. Then, per layer, it collects the targets the layer touches and writes one layer row per target from Base's kept bindings plus the layer's own. A target left with no source becomes a sourceless `NoInherit` row, the resolver's rule for blocking Base fallthrough.

A macro has one layer mask, and `MacroLayerGateOpen` (`InputManager.Step4b.EvaluateMacros.cs`) leaves "Base" open on an inheriting layer. So a layer that owns a control driving a Base macro sets `Expand`. So does a layer that owns a control Base unmaps, and one whose own macro shares a control with a Base macro, such as a lightbar pattern over Base's. An expanded layer does not inherit: its activators get `InheritUnmapped = false`, it gets rows for every Base target, and it takes its own copy of every Base macro and block for a control it does not own, with fresh pair keys. A macro marked `RunsBesideLayers` (a solid lightbar color) never forces this, since Base writes first and the layer's write ends the frame. Only the layers that need it pay for the copies.

A layer with no activator gets a `Passive` (No Button) one, because an activator owns the layer's tab. A layer that no input or `SwitchLayer` action opens is reported Partial (`LayerNoInput`). Duplicate activators collapse.

### Macros

`AddMacro` gives a macro that repeats until release and latches something an `OnRelease` twin that runs `ReleaseOf` its actions, so a stop between a down and its up leaves nothing held. A `Toggle` macro's twin is an `OnPress` that runs first. `AddHoldPair` writes a press macro and an `OnRelease` release on one `PairId`. Clearing an unset latch is a no-op, so a tap below a long-press threshold stays harmless. `ToMacroData` drops a macro whose trigger is missing a leg, clamps `TriggerHoldMs` to 50..10000 and `TriggerDoublePressMs` to 50..5000, and sets `ConsumeTriggerButtons` only for blocks.

The engine changes that carry this: `ToggleVcButton` honors `LatchDirection`, an Off clears matching On latches (inside its own macro for a hold pair, across the slot otherwise), and a Single Press yields to a Hold For macro on the same trigger and layer, found at the press (`FindHoldForBeside`, `MacroItem.HasSameTrigger`).

A profile color is `ProfileColor`: `LightbarColor`, `Reactive`, held 250 ms and rewritten every frame, so it ends by itself on a profile switch where a `Sticky` override would stay on the bar. Patterns (`LightStep`, `RainbowPattern` in 36 steps) play on `Always` macros. A DS4Windows trigger effect is `TriggerEffect` with `Duration` 500 and a 250 ms `Delay`, so it is rewritten four times a second.

### Blocks

`Block` records a key or button the file stops reaching Windows on a layer. A key that a running row reads is already held back by **Consume Mapped Inputs (Hooks)**, which the import asks for with `AdviseConsume` (`ConsumeKeys`). A key no row reads where the block runs gets an empty macro that consumes its trigger (`InputService.MacroTriggerConsumesKey`). `ReportKeysTheSwitchHoldsBack` adds a `MappedKeyHeldBack` line for each key the switch would hold back that the file left reaching Windows, except hardware remaps, which replace the native key in reWASD.

### Stick ranges and curves

`StickShape` records reWASD's initial and maximum deflection per layer and target. The floor rides each source as `ParamAntiDeadzone`. A scale below 1 becomes an `Always` `AxisScale` macro with value `(scale - 1) * 32767`. `Curves` are stamped as `WorkshopCurves`, except for a target whose rows tune it differently on different layers (`WorkshopTuningApplier.TargetsKeepingTheirRows`). There `PowerFit` finds the least-squares exponent on 0.05..20 by ternary search and writes it to each stick or trigger source's `ParamCurveExponent`, reported Partial (`CurveOnRows`).

---

## Bounded reads

`BoundedReads` (`PadForge.Engine`) parses descriptors that read an input inside a range, and `SourceCoercion` evaluates any source for which `BoundedReads.IsBounded` holds through `BoundedReads.Read`.

| Builder | Descriptor | Used for |
|---|---|---|
| `Between(low, high, halfAxis, invert, input)` | `Between <low> <high> <half><invert> <input>` | A reWASD zone below the next zone's edge (`ImportInput.Below`). |
| `Sector(center, halfWidth, innerX, innerY, outerX, outerY, ring)` | `Sector <center> <halfWidth> <radius>[~<outer>] <ring>` | A stick direction or zone by angle, with an elliptic dead zone and an optional outer edge. Degrees run counterclockwise from right. |
| `Stage(mode, full, waitMs, pull, press, input)` | `Stage <mode> Soft\|Full <wait> <pull> <press> <input>` | One stage of a DS4Windows two-stage trigger. |

`TwoStageMode` names `HairTrigger`, `HipFire` and `HipFireExclusive`, the DS4Windows modes that need memory of the pull. `Normal` needs none, and `ExclusiveButtons` is a `Between` read. Each pull is a `TwoStagePull` state machine, after `Mapping.ProcessTwoStageTrigger`, shared by every reader of one trigger and stepped once per device per poll by `BoundedReads.StepPulls` from `InputManager.Step2.UpdateInputStates.cs`. A gap over `GapMs` = 250 ms resets it. `FullPullPercent` = 99 stands in for DS4Windows' raw 255.

---

## reWASD

`RewasdTranslator.Translate` runs `ReadTables`, `ReadDevices`, `ReadShifts`, `ReadDeviceTuning`, `ReadShiftActivators`, `ReadVirtualSticks`, `BuildPassThrough`, `ReadHardwareMappings`, `ReadMaskMappings`, `ReadRadialMenus`, `ReadLed` and `ReportLeftovers`, then `Finish`.

- **Tables.** Masks (the inputs), mappings (an activator on a mask and what it sends), commands, shifts and per-device tuning. A preset's single layer that nothing opens reads as Base. A `radialMenu` shift nothing jumps to reads as -1 and imports nothing.
- **Devices.** Hardware class by `name`, else by description prefix (`DIK_` keyboard, `MOUSE` mouse), else by id. The file always lists a virtual gamepad, so a pad slot exists only when a mapping sends to it or unmaps or moves a physical pad's button (`FileUsesVirtualPad`) or the pad converts to virtual. `VirtualFor` maps `xboxonebt` to `xbox-one-s-bt`, `ds4` to `dualshock-4-v2`, `ds3` to `dualshock-3`, `nintendoswitchpro` to `switch-pro`, anything else to `xbox-360-wired`. `udp` sets `EnableDsuMotionServer`.
- **Keys.** A keyboard `buttonId` is a DirectInput scan code (DIK_A = 30). `DirectInputKeys.TryGetVirtualKey` asks the active layout (`MapVirtualKeyEx` with `MAPVK_VSC_TO_VK_EX` on `GetKeyboardLayout(0)`) for character keys, so the key at a place types what it types on this PC, and reads its US table for the rest: sided modifiers, the numpad, every E0 key. Numpad Enter lands at 0x88, `RawInputListener`'s index for it. `OffLimitsForTest` makes the test host read the US table.
- **Mouse.** reWASD's ids run Left, Right, Middle, X1, X2. PadForge's mouse state order is Left, Middle, Right, X1, X2, so id 2 reads `Button 2` and id 3 `Button 1`. Movement and the wheel are half-axis reads of axes 0, 1 and 2.
- **Gamepad.** Button ids follow reWASD-Powertools' `gamepad-buttons.md` and each file's own `description`, never the index in shunt's `rewasd_all_buttons_and_keys.json`. `GamepadSkipReason` names a third stick (213..235), a gyro tilt zone (74..76, 145..162) and a lean in Tilt mode (72, 73).
- **Activators.** `TriggerFor` maps `long` to `HoldForMs`, `double` to `DoublePress`, `triple` to `TriplePress`, `release` to `OnRelease`, `start` to `OnPress`. `single` is `SinglePress` beside a double or triple, `ShortPress` beside a long press (sharing that sibling's `longwaittime`), and `OnPress` alone. Defaults: `longwaittime` 300, `doublewaittime` 442. `LowerMacros` writes held plain outputs under `hold_until_release` on single or start as rows when `CanRow` allows (up to three inputs, gates on the source's device), `repeat` as a repeating `WhileHeld`, `turbo` as `Turbo`, and `toggle` through `LowerToggle`.
- **Jumps.** `LowerJump` makes a held or toggled jump a layer activator carrying `DelayMs`, `PostponeMapping`, `HostLayerMask`, the long-press delay, the double-press window and `FireOnRelease`. A jump back to Base on release from the layer the same control engaged is the file's own Hold and writes nothing more. Every other jump is a `SwitchLayer` macro.
- **Commands.** `CommandAction` maps command types: 1 Toggle Virtual Controllers Disabled, 2 Disconnect Controller, 3 Toggle Window, 4 and 6 gyro toggle, 15 and 16 gyro on and off, 5 and 18 Gyro Recenter, 7 log off, 8 shut down, 9 sleep, 13 hibernate, 17 restart (each a `RunProgram` of `shutdown.exe` or, for sleep, `powershell.exe`), 11 Win + Print Screen, 12 Alt + F4, 101..108 and 120 Toggle Screen Overlay (109 and 110 skipped, `NinthCrosshair`), 130..137 radial navigation, and 1000..1999 a program.
- **Radial menus.** One `MenuDefinitionEntry` per top circle, `MenuKind.Radial`, `FireType = TouchRelease`, on the layer its sectors' mappings sit on, hosted on the stick the navigation commands name (right stick by default).
- **Mouse regions.** `LowerRegion` writes a `MouseLimitRegion` hold pair, the file's rectangle as insets and offsets against `GetSystemMetrics`.
- **Lightbar.** `ReadLed` lowers `config.led.default` and each shift's entry: solid, `rainbow` (6000 ms), `breath`, `heartbeat`, `stroboscope`, `shimmer`.

## DS4Windows

`Ds4WindowsTranslator.Translate` runs `ReadOutput`, `BuildDefaultRows`, `ReadControlBlock` for `Control` and `ShiftControl`, `ReadTwoStage` for L2 and R2, `ReadGyro`, `ReadTouchpad`, `ReadLightbar`, `ReadSafetyAndLeftovers` and `ReadSpecialActions`, drops the pads for `DinputOnly`, and calls `Finish` with the file name and `ExecutablesFor`.

- **Default rows.** A profile lists only what differs from `defaultButtonMapping`, so `BuildDefaultRows` binds every control to its own output first and a listed control replaces its own (`ReplaceDefault`). Elements the translator does not know are ignored, which is how a fork's profile still imports.
- **Control blocks.** `Button`, `Key`, `Macro`, `Extras`, `KeyType` (`Toggle`, `Unbound`, `HoldMacro`, `RepeatMacro`) and `LightbarMacro` per control. A `ShiftControl` entry's `Trigger` attribute indexes `ShiftTriggers`, `Mapping.cs`'s `shiftTriggerMapping`, and `EnsureShiftLayer` makes one held, inheriting layer per trigger with `PostponeMapping`. Index 26 is a touch.
- **Macros.** `DecodeMacro` follows `PlayMacroCodeValue`: at or past a billion is a lightbar color, at or past a million a rumble, at or past 300 a wait of the value less 300, below that a key or button that alternates down and up.
- **Special actions.** `ReadSpecialActions` reads the names in `ProfileActions` from the sibling `Actions.xml` and always knows DS4Windows' stock `Disconnect Controller`. `LowerAction` handles `Program`, `Profile`, `Macro`, `Key`, `DisconnectBT`, `MultiAction`, `XboxGameDVR` (`ExpandGameDvr`), `GyroCalibration` and `SASteeringWheelEmulationCalibrate`. `LowerMultiAction` uses a 500 ms hold and a 300 ms window, spanning `Mapping.cs`'s two 150 ms tap limits.
- **Gyro.** `Mouse`, `MouseJoystick`, `Passthru` (DS4 output only), `Controls` and `DirectionalSwipe`. Gyro zones convert at `GyroCountsPerDegree` = 16 against PadForge's `GyroFullScaleDegrees` = 500. `ApplyGyroEngage` takes the first trigger of the list.
- **Touchpad.** `Passthru`, `Mouse` with its click regions, `AbsoluteMouse` and `MouseJoystick`. `ApplyTouchToggle` makes PS + touch a Toggle layer (mask `"Shift" + (ShiftTriggers.Length + 0)`), and `ApplyTouchDisInvert` a Hold layer that carries the movement uninverted.
- **Leftovers.** `LaunchProgram` becomes an `Always` macro on every layer (`Layer = ""`) that runs it once and waits. `RumbleBoost` and `idleDisconnectTimeout` become stamps. Settings with nothing to land on are reported Skipped (`NoSuchSetting` or `ControllerSetting`).
- **Executables.** `ExecutablesFor` reads the sibling `Auto Profiles.xml` and keeps each `Program` whose `Controller1` to `Controller8` names this profile.

---

## Format sources

PadForge reads users' own files from published facts. It ships no copy of either tool's schema or code, and no third-party sample file is committed as a fixture.

| Tool | Source |
|---|---|
| reWASD | The schema 3.0 dump `ConfigJSONSchema_3.0.json` and the enum dumps in hcn1z1's [shunt](https://github.com/hcn1z1/shunt) (MIT). DatMoshu's reWASD-Powertools docs: `schema-reference.md`, `gamepad-buttons.md`, `activators-and-modes.md`, `dik-keycodes.md`. reWASD's own help pages, cited in the translator's comments. |
| DS4Windows | [Schmaldeo's fork](https://github.com/schmaldeo/DS4Windows): `DS4Windows/DS4Control/DTOXml/ProfileDTO.cs` (element names and defaults), `DS4Windows/DS4Control/Mapping.cs` (`shiftTriggerMapping`, the macro player, two-stage triggers, multi-action timing), `DS4Windows/DS4Control/ScpUtil.cs` (special actions and their default names). |

---

## Tests

| Test class | Holds |
|---|---|
| `RewasdImportTests` | Every row of the reWASD table against hand-written files in the schema's shape, plus the refusals: `JsonThatIsNotSchema3_IsRefused`, `MalformedJson_IsRefused`, `OversizedFile_IsRefusedUnread`, `MissingFile_IsRefused`, `TooManyShifts_AreRefused`, `AMaskOfFiveInputs_IsRefused`, `ACircleThatNamesItself_EndsAndKeepsTheOtherSectors`, `AChainOfCirclesDeeperThanAnyMenu_Ends`, and `AnyValueOfTheWrongKind_NeverThrows`, which swaps every value of a file that uses the whole format for each JSON kind through `TranslateCore`. |
| `Ds4WindowsImportTests` | Every row of the DS4Windows table against profiles in the shape `ProfileDTO.cs` writes, plus `ADtd_IsRefusedAndSaysWhy`, `ExpandingEntities_AreRefused`, `OtherFiles_AreRefused`, `BytesThatAreNoFile_AreRefused`, `AnyElementWithTheWrongText_NeverThrows`, and the `Actions.xml` sibling cases. |
| `Ds4WindowsDefaultsTests` | A profile that leaves an element out imports as one that writes the `ProfileDTO` default. |
| `ForeignConfigCorpusTests` | `EveryPublicRewasdFileImports` and `EveryPublicDs4WindowsProfileImports` read the public sample clones beside the repository when they are on disk (reWASD: `rewasd-profiles-supersmo`, `rewasd-profiles-yungcheeze`, `shunt-hcn1z1`, `reWASD-Powertools-DatMoshu`, `reWASDMappings-ShashankaNataraj`, and for DS4Windows four `ds4w-profiles-*` clones). At most one reWASD file may be refused, at least 46 DS4Windows profiles must import, and the trigger and stick tuning are checked against `Mapping.cs`'s math. A machine without the clones runs nothing here. |
| `ImportedMacroRuntimeTests` | Runs what the importers write through the macro engine: single, double and long on one button, latch direction, hold pairs on one key, axis latches, Until Next Press, Profile Shortcut by name, and the stamps folding onto the assigned device only over its defaults. |

---

## Related pages

- [Import from reWASD and DS4Windows](../guides/profile-import.md): the user guide.
- [Steam Workshop Config Import Internals](steam-workshop-import-internals.md): the materializer, tuning applier and report this importer shares.
- [Settings and Serialization](settings-and-serialization.md): `ProfileData` and how it persists.

---

*Last updated for PadForge 5.3.0.*
