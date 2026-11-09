# On-Screen Keyboard Internals

*How a keyboard menu is stored, how the poll thread opens the keyboard, holds its controllers at rest, reads its controls and routes its keys, and how the window draws it.*

For the user-facing side see [On-Screen Keyboard](../features/on-screen-keyboard.md).

| File | Responsibility |
| --- | --- |
| `PadForge.Engine/Menus/KeyboardMenu.cs` | The keyboard menu's types: `KeyboardLayout`, `KeyboardOpenPress`, `KeyboardControlAction`, `KeyboardInput`, `KeyboardControlEntry`, and `KeyboardMenuDefaults` with each layout's controls and defaults. |
| `PadForge.Engine/Menus/MenuDefinitionEntry.cs` | `MenuKind.Keyboard` (2) and the keyboard attributes of a `<Menu>`. |
| `PadForge.App/Common/Input/InputManager.OnScreenKeyboard.cs` | The runtime: Step 2's filter, the menu records, the tick, Opens With and the layer, opening, closing and holding controllers at rest. |
| `InputManager.OnScreenKeyboard.Output.cs` | Types Through: Windows Input, a Keyboard + Mouse slot's keyboard, or the menu's own HIDMaestro keyboard. |
| `InputManager.OnScreenKeyboard.TextFocus.cs` | Open When a Text Box Is Selected: the watcher's reports, read by the tick. |
| `PadForge.App/Common/Input/OnScreenKeyboard/OskModel.cs` | `OskStyle`, `OskSettings`, `IOskLayout`, `IOskOutput`, `OskKey`, and `OskLayoutFrame`: the physical key frame, the symbols page and the wheel's sets. |
| `OskEngine.cs` | `OskControlState`, `OskBoard` and `OskEngine`: selection, typing, modifiers, pages, the wheel and suggestions. No Windows state. |
| `OskWindows.cs` | `OskWindowsLayout` (the layout read with `ToUnicodeEx`), `OskWindowsKeyboard` (foreground layout and repeat timing), `OskWindowsOutput` (key events for `SendInput`). |
| `OskPredictor.cs` | Word suggestions from `Windows.Data.Text.TextPredictionGenerator`. |
| `OskTextFocusWatcher.cs` | UI Automation focus, and whether the focused element takes text. |
| `OskView.cs` | The immutable snapshot the window draws. |
| `PadForge.App/Views/OnScreenKeyboardWindow.xaml(.cs)` | The window: keys, hint bar, close button, top-bar drag and corner grip. |
| `PadForge.App/Services/InputService.OnScreenKeyboard.cs` | The UI-timer leg: hands the poll thread the layout and repeat timing, draws the snapshot, saves what the window and the keyboard's own keys changed. |
| `PadForge.App/ViewModels/MenuEditorItem.Keyboard.cs` | The Menus tab's keyboard rows, the Keyboard Controls card and the Keyboard card. |

---

## The stored menu

A keyboard menu is a `MenuDefinitionEntry` with `Kind` `Keyboard` on the slot's `MappingSet.Menus`. It has no cells. Its keyboard attributes carry `ShouldSerialize*` methods that return false for every other `Kind`, so a ring, a grid or a hotbar saves as it did before 5.3.0 (`KeyboardMenuSchemaTests.AMenuOfAnotherStyle_WritesNoKeyboardSetting`). The attributes are listed under [Settings and Serialization](settings-and-serialization.md#mappingset-v32). `Clone` copies every one and deep-copies `KeyboardControls`.

`KeyboardMenuDefaults.Create(menuId, name)` makes a new keyboard: `PosYPercent` `KeyboardMenuDefaults.PosYPercent` (100, the bottom of the work area) and `EngageDeadzonePercent` `SteerDeadzonePercent` (50). The editor applies the same two values when a menu turns into a keyboard, only where the radial defaults (50, 25) still stand, and reverses them on the way back (`MenuEditorItem.ApplyKeyboardDefaults`, `LeaveKeyboardDefaults`).

### Controls

`KeyboardControlAction` has 48 members, saved by name and append-only. `KeyboardMenuDefaults` holds a table per layout, in the editor's order: steering first, then the keys, then the pointers.

| Layout | Tables | Controls |
| --- | --- | --- |
| `Grid` | `LeftStickSteer`, `GridKeys`, `Pointers` | 29 |
| `Split` | `LeftStickSteer`, `RightStickSteer2`, `SplitKeys`, `Pointers` | 32 |
| `Wheel` | `LeftStickSteer`, `WheelKeys` | 22 |

Defaults are device-free `"Gamepad ..."` names, and stick directions use the legacy half-axis prefix: `"HGamepad LeftStickX"` is the stick pushed right, `"IHGamepad LeftStickY"` pushed up (SDL frame, +Y down). `SourceCoercion.StripLegacyPrefix` turns the prefix into `MappingSource.Invert` and `HalfAxis`. The pointers default to `"Touchpad 0 Finger 0 X"`, `"... Y"`, `"... Down"` and `"Touchpad 0 Click"`, and the same on touchpad 1.

A control's input is a `KeyboardInput` record struct: `Descriptor`, `DeviceGuid` (empty reads every device that drives the menu), an optional `AndDescriptor` / `AndDeviceGuid` held with it, and `Threshold`, the press point in percent. 0 takes `KeyboardInput.DefaultThreshold`, 50, a mapping row's `MappingSource.DeadZone` default. `ThresholdPercent` clamps a set value to 1 to 99.

`KeyboardMenuDefaults.Effective(menu, layout, action)` returns the saved `KeyboardControlEntry` for that layout and action, else the default. `Set` builds a new list and swaps it in, dropping the entry when the input equals the default, so an untouched keyboard saves no `<KeyboardControl>` and the poll thread never reads a half-edited list. A cleared control keeps an entry with an empty descriptor. `SetOpenInput` writes Opens With's fields with the descriptor last, since the poll thread reads each field on its own.

`KeyboardOpenPress` holds the macro trigger's press modes: `Press` (0), `Hold` (1), `DoublePress` (2), `Release` (3), `WhileHeld` (4), `ShortPress` (5), `TriplePress` (6), `SinglePress` (7). `KeyboardMenuDefaults.OpenPressMs` returns the saved time, or `DefaultHoldMs` (500) for `Hold` and `ShortPress` and `DefaultDoublePressMs` (442) for the three window modes, the macro trigger's `TriggerHoldMs` and `TriggerDoublePressMs` defaults. `MaxOpenPressMs` is 10,000.

---

## The poll thread

### Step 2

`UpdateInputStates` passes each device's new state through `OnScreenKeyboardFilter(ud, raw)` when any device is masked, and stores the result in `ud.InputState`. A masked device's state is a pooled copy with everything at rest. Everything downstream reads `ud.InputState`: mapping rows, macros, other menus, gestures, layer activators, in every slot the device feeds, with no gate of its own.

`UpdateMenuContexts` (`InputManager.MenuRuntime.cs`) calls `NoteKeyboardMenu(slot, def, ud, raw)` for each device on a slot with an enabled keyboard menu, with the real state. The device becomes a driver of the menu's `OskMenuRecord` for this poll when the menu names it (`DeviceGuid`) or, for a device-free menu, when `InputDeviceType.AnswersAnyDeviceSources(ud.CapType)` holds. A device that only a control names drives that control alone. A keyboard menu gets no `MenuContexts` entry and draws no menu overlay.

### The tick

`TickOnScreenKeyboard(step5Runs)` runs once per poll after `EvaluateMacros`, which can switch the layer that holds the keyboard open, and before Step 5, which sends a slot's keyboard the keys typed. The idle path calls it with `step5Runs: false`, where no slot's keyboard is fed. It returns at once when the keyboard is closed and nothing is pending. Otherwise, in order:

1. `RefreshKeyboardMenus` (every 250 ms): the enabled keyboard menus of every created slot, in slot and list order, and whether any asks for text focus.
2. `ReconcileMenuKeyboards` (every 250 ms): makes and retires the menus' own HIDMaestro keyboards.
3. The window's commands (`OskCommand`: `ClickKey`, `ClickWheel`, `Close`). A click carries the `OskView.ShapeOf` shape of the keys it landed on and types nothing when the shape has changed since.
4. `ApplyOwnerSettings`: the owner menu's layout, function row, suggestions, symbols and steering deadzone as a new `OskSettings` when one changed.
5. `ReadControls` for the owner menu. A key control that rose this poll and whose input holds every input of Opens With (`OskSources.HoldsOpen`) takes Opens With's press.
6. `ReadMenuInputs`: each menu's Opens With and layer, queued as open or close requests.
7. `ReadTextFocus`, then the requests.
8. `DropStaleMasks` (a masked device Step 2 has not read for `OskStaleMs`, 300 ms, went offline), `TrackOwned`, and the restricted-slot check.
9. `OskEngine.Tick`, the hold-to-move delta, and a close the engine asked for.
10. Suggestions, the `OskView` snapshot (on a version change or every 100 ms), `ApplyOutput`, and `ForgetIdleMenus` (a non-owner menu no device drove for `OskMenuForgetMs`, 2,000 ms, is forgotten, and an owner menu that is gone, off or no longer a keyboard closes the keyboard).

Every time here is on `MenuClock`.

### Opening and closing

`ReadMenuInputs` reads Opens With with `InputHeld` and acts once per press by the mode's rule, cited against the macro trigger's evaluators in `InputManager.Step4b.EvaluateMacros.cs` (`EvaluateHoldForMsTrigger`, `EvaluateShortPressTrigger`, `EvaluateDoublePressTrigger`, `EvaluateTriplePressTrigger`, `EvaluateSinglePressTrigger`). A single press acts up to `OskSinglePressGraceMs` (250 ms) past its window. An input held when the record is first seen waits for its release. An act on the owner menu closes the keyboard unless a control took the press, and an act on another menu opens it for that menu, when `IsMenuLayerOpen` passes.

With `LayerHoldsOpen` on a named layer, the layer's rise opens and its fall closes. A fall within `OskLayerSettleMs` (100 ms) of the open sets `_oskLayerIgnored`: the keyboard held the activator at rest, so the layer ended because of the keyboard and the keyboard stays open.

`OpenKeyboard(slot, menuId, reason, now)` refuses a slot `IsSlotRestricted` names, lets go of the last owner's controllers (`ReleaseToGuard`), takes the menu's drivers with `Own`, records the reason (`Input`, `Layer` or `TextFocus`), picks the hint family, and opens the engine with the controls read now, so the opening press types nothing until it is let go. `CloseKeyboard` releases every owned controller.

### Holding a controller at rest

`Own` creates an `OskMask` and `TakeRest` records what each axis holds at. A device in SDL's gamepad layout (`ReadsAsGamepad`: an SDL device opened as a gamepad and not forced raw, or a non-SDL device of type Gamepad) holds sticks at 32768 and triggers at 0. A mouse holds its motion lanes at `SdlMouseWrapper.AxisCenter`. Any other axis, slider, MIDI controller value, Ring-Con strain and Joy-Con IR intensity holds the value it had when the keyboard took the device. `HoldAtRest` clears buttons, hats, MIDI notes, analog keys, gyro, touch, capacitive sense, NFC, IR and mouse deltas, and keeps the accelerometer as it was.

At the close, `ReleaseToGuard` records what is held, and `KeepHeldSilent` keeps each such input at rest until it is let go: buttons, hats, MIDI notes and pitch bend, analog keys, touch, a gamepad stick pushed past a quarter of its travel, a trigger past a tenth (`OskTriggerRest`, 6554), and another axis with a named rest more than a quarter from it (`OskCenteredRest`, 8192). An axis whose rest was taken at the open, such as a throttle, cannot be told held from resting, so it is let go at the close. The mask is removed once nothing is held.

`TrackOwned` takes a device that starts driving the owner menu while it is open and closes the keyboard when the last owned controller went offline.

### Reading controls

`OskSources.Build(def, layout)` turns each control's `Effective` input into an `OskInputReader` of one or two `OskLeg`s. A leg's `Src` is `SourceOf(descriptor, press)` with the press point as `MappingSource.DeadZone`, and `HeldSrc` the same source at `ReleasePercent(press)`, 70% of it (`OskEngine.SteerReleaseShare`), at least 1. Key controls on the same input share a number in `Shared`. The record rebuilds when any field it was built from is a different reference.

`LegHeld` is `SourceCoercion.EvaluateForButtonTarget`, the read a Mappings row with a button target takes, across the drivers the leg reads, at `Src` and at `HeldSrc` while held. `LegLevel` is `EvaluateForTriggerTarget` for depth, falling back to 1 where only the button read holds (a zone, a sector, a two-stage pull, IR Offscreen). `LegReads` applies the #431 rule: a named device reads that device, a device-free leg reads a driver that answers device-free inputs and has the axes the source reads (`HasAxesFor`), so a mouse's empty stick axes never read as a push.

`SteerOf` combines four direction levels into -1 to 1 per axis. `PointerOf` reads a pointer's X and Y across their whole range from the first driver whose touch input holds. `ReadControls` fills `OskControlState`: `Down` and `Shared` for key controls, `SX`/`SY` and `S2X`/`S2Y`, and up to two `OskTouch` values.

---

## OskEngine

`OskEngine` owns no Windows state. It takes an `IOskLayout` and an `IOskOutput`, so `OnScreenKeyboardEngineTests` drive it with a fake US layout and a recording output.

| Constant | Value | Use |
| --- | --- | --- |
| `NavDelayMs`, `NavIntervalMs` | 380, 90 | Moving the selection repeats after the delay, every interval. |
| `ChordWindowMs` | 90 | Split's two type controls within it type a space (Wilson and Agrawala, CHI 2006). |
| `SteerReleaseShare` | 0.7 | Steering counts as let go under this share of the deadzone. |
| `MovePercentPerSecond` | 60 | Hold-to-move speed at a full push, in percent of the work area. |

`Tick(pad, now)` releases guards (an input held at the open, or at a layout switch, reads nothing until let go), moves the keyboard while **Move the Keyboard (Hold)** is held past the steering release point, then runs `TickGrid`, `TickSplit` or `TickWheel`, and `TickTouch` outside the wheel. A key control that shares its input with Move the Keyboard fires on release when the keyboard did not move (`Fire`, `SharesMove`). Typing controls repeat at `RepeatDelayMs` and `RepeatIntervalMs`, which `InputService` fills from `OskWindowsKeyboard.RepeatTiming` (Windows' `SPI_GETKEYBOARDDELAY` and `SPI_GETKEYBOARDSPEED`, read every 5 seconds).

`MoveFocus` wraps around a row and between rows and keeps the column (`Focus.Col`). Shift, Ctrl, Alt, Win and AltGr cycle off, latched for one key, locked (`Cycle`). `TogglePage` switches the letters and symbols pages. `PetalOf` maps the steering vector to one of eight groups, 0 north and clockwise, past the deadzone and held down to its release share. `TypeCharacter` types a character with the layout's key and level that produces it, base level first, else as Unicode text. A dead level's character goes out as text, so no accent waits for the next key.

`SuggestionQuery` carries the word being typed, the previous word and a version. `SetSuggestions` keeps up to three answers to the current version that start with the typed word, are longer than it and contain no space, shaped to its case.

### The layout

`OskWindowsLayout(hkl)` reads every key's four levels (base, Shift, AltGr, Shift+AltGr) once with `ToUnicodeEx` and flag 4, which leaves Windows' keyboard state alone, so reading a dead key leaves no pending accent behind. Only Caps Lock changes afterward (`SetCaps`). `InputService` asks `OskWindowsKeyboard.ForegroundLayout` (the keyboard layout of the thread that owns the foreground window) every 250 ms while the keyboard is open and hands a new `OskWindowsLayout` to the poll thread when the HKL changes.

`OskLayoutFrame` is the physical frame: the main block by set 1 scan code, 0xE000 added for an extended key, rows aligned in columns so up and down move straight. `CharRows` holds the character keys of the four main rows (13, 13, 11 and 10). The ISO key (0x56) is drawn only when it types something no other key does. `SplitAfter` gives each row's last left-hand scan code. `DefaultSymbols` is the 47-character default symbols page, in the character keys' places. `WheelSets(layout)` returns four sets of 32: on a US Latin layout, daisywheeljs's `abcdefghijklmnopqrstuvwxyz?!;\&-`, `ABCDEFGHIJKLMNOPQRSTUVWXYZ+.@#$%` and `0123456789*,_="'()[]{}:~^<>|`, and on another layout its own letters sorted by the layout language's `CompareInfo`, letters past 32 spilling into the numbers set. The fourth set is `KeysSet`: modifiers, navigation, Esc, Tab, Delete, Caps Lock, F1 to F12, Insert, Print Screen, the layout key and Backspace.

---

## Output

The engine's `IOskOutput` is `OskRouter`. `TapKey` first tries `QueueDeviceTap`, and otherwise sends through `OskWindowsOutput`, queued behind any device report still waiting so nothing types out of order. Text always goes through Windows Input.

`OskWindowsOutput.TapKey` maps the scan code to the virtual key the foreground layout gives it (`MapVirtualKeyExW`, `MAPVK_VSC_TO_VK_EX`), builds the modifiers down, the key down and up, and the modifiers up in reverse (AltGr is left Ctrl with right Alt), and queues the batch with `InputManager.QueueKeyboardOutputs`. The injector thread sends it with `SendInput`, in order with the macros' and the mapped keys, tagged with `InputHookManager.OutputTag` so PadForge's own hooks and Raw Input reader pass it by. `TypeText` sends `KEYEVENTF_UNICODE` pairs, with Enter and Tab as keys.

`OskDestination` reads the owner's `TypesThrough`: `""` Windows Input, `"slot:N"` a Keyboard + Mouse slot (`TryParseSlotTarget`), anything else a HIDMaestro keyboard profile id (`MenuKeyboardProfileOf`). `QueueDeviceTap` falls back to Windows Input when the layout gives the key no virtual key, when the slot is not Keyboard + Mouse with its keyboard half on and Step 5 running (`SlotKeyboardSends`), when the menu's own keyboard is not made yet, or when the model's report cannot carry the key (`CapsSend` through `KbmHidKeyMap.Resolve` and `KbmDeviceCaps`). It queues four reports, one per poll: modifiers, modifiers with the key, modifiers, nothing. `ApplyOutput` sends one per tick: a slot's into `CombinedKbmRawStates[slot]`, which lasts that poll, and a menu keyboard's straight to `SubmitKbmState`.

A menu's own keyboard (`OskMenuKeyboard`) exists while its menu is enabled and names a profile `KbmDeviceCatalog.HasKeyboard` knows. `ReconcileMenuKeyboards` makes at most one at a time, and only while no slot's create or dispose runs, since Step 5 waits on `MenuKeyboardLifecyclePending` the same way. `CreateMenuKeyboard` builds a keyboard-only `KeyboardMouseVirtualController` on a worker under `MenuKeyboardIdentityKey(slot, menuId)`, `"padforge:pad{slot}:KeyboardMenu{menuId}:keyboard"`, so it returns at the same device path after a restart and never meets a slot's own identity. A failed create is not retried until the menu asks for another keyboard or is turned off and on. `DestroyMenuKeyboardsLocked` removes them at engine stop under the lifecycle lock.

---

## Suggestions

`OskPredictor.Request(language, word, previous, version)` runs one question at a time on a task, a newer one replacing any still waiting. It asks `TextPredictionGenerator(language).GetCandidatesAsync(word, 10)`, or `GetNextWordCandidatesAsync(10, [previous])` when no word is started, unless `LanguageAvailableButNotInstalled`. A failure drops the generator and answers nothing. The language is the layout's `LanguageTag`. `TryTake` hands the newest answer to the tick, which passes it to `SetSuggestions` with its version.

---

## Text focus

`OskTextFocusWatcher` runs on its own MTA thread for the engine's life (`StartTextFocusWatcher`) and subscribes to `Automation.AddAutomationFocusChangedEventHandler` only while `_oskWantsTextFocus` is set, checked twice a second. Every program that answers UI Automation pays a query per focus change while it listens, and Firefox answers through a slow proxy (Mozilla bug 1777875). Each focus change asks the element's control type, then its Value pattern's read-only flag, else its Text pattern's read-only attribute, so an edit control or a writable document counts. Focus that stays in one element is reported once, by runtime id. Each pass has its own try, so a `TimeoutException` from a hung window leaves the watcher running.

`NoteTextFocus` bumps a sequence number. `ReadTextFocus` opens the keyboard for the first enabled menu in `_oskMenuScan` with `OpenOnTextFocus`, an open layer and an unrestricted slot, when the keyboard is closed. A report that focus left text boxes closes a keyboard opened with `OskOpenReason.TextFocus` and no other.

---

## The window

`InputService.UpdateOnScreenKeyboard` runs on the UI timer. It reads `InputManager.OnScreenKeyboardView`, hides the window when the view is closed, older than 500 ms, or names a menu no longer on its slot, and saves to the menu what changed: the layout key's style and the Fn key's function row (`EditKeyboardMenu`, through the menu's editor when one exists), and the hold-to-move delta in whole percents of `PosXPercent` and `PosYPercent`.

`OskView.Build` makes the snapshot on the poll thread: keys with their texts and latch states, the focus per board, the wheel's labels, the owner slot and menu, each control's input for the hint bar, and a `Shape` that changes only when the keys' places change, so the window rebuilds only then. `OnScreenKeyboardWindow` sets `WS_EX_NOACTIVATE` and `WS_EX_TOOLWINDOW` and `ShowActivated="False"`, so the window being typed into keeps focus. It places its center at the menu's Screen Position in the work area, as `MenuOverlayWindow` places a menu, shrinks a keyboard larger than the work area, takes `OpacityPercent` (5 to 100) and `ScalePercent` (10 to 400), and writes the top-bar drag and the corner grip back to the menu. The hint bar names a device-free input by the controller family's own label (`OskFamily`: Xbox, PlayStation, Nintendo, GameCube, from SDL's face labels, else the vendor id), and any other input by the name the slot's input lists give it.

---

## Import and starter profile

`WorkshopProfileMaterializer.KeyboardMenuFor(TranslatedMacro, menuId)` turns a Steam Show Keyboard binding (`TranslatedMacroAction.ShowOnScreenKeyboard`) into a keyboard menu named after the binding, or "Keyboard". Its first trigger input is Opens With, its second the input held with it, each with the hosting read's half-axis prefix, and a half-axis host's `TriggerDescriptorDeadZonePercent` as the press point. `OnRelease`, `HoldForMs` and `DoublePress` become `Release`, `Hold` and `DoublePress`, the times clamped to 50 through 10,000 ms. The binding's layer becomes `LayerMask`. The menu goes on the Xbox slot when the import made one, else the Keyboard + Mouse slot, after that slot's other menus. A binding with no input makes no menu.

`StarterProfileCatalog.BuildDesktop` adds `KeyboardMenuDefaults.Create(1, "Keyboard")` with Opens With `"Gamepad ButtonX"` and no text-box opening (`StarterProfileCatalogTests.Desktop_ReachesShowKeyboardAndTheWindowsKey`).

---

## Tests

| Test class | Holds |
| --- | --- |
| `KeyboardMenuSchemaTests` | Saved enum numbers, the settings-file round trip, no keyboard attribute on another style, defaults per layout, the press point's save rule, `Set` and `SetOpenInput`, Opens On's default times. |
| `OnScreenKeyboardEngineTests` | The engine on a fake US layout: Grid, Split and Wheel controls, wrap, Shift latch and lock, symbols page, repeat at Windows' timing, hold-to-move and its tap rule, the layout and Fn keys, pointers, suggestions, dead keys and the ISO key. |
| `OnScreenKeyboardMenuTests` | The runtime: Opens With and every Opens On mode, controls that take Opens With's press, the controller at rest and silent after the close, devices going offline or joining, takeover by another menu, restricted peers, layers and the settle window, text focus, Types Through to a slot and to the menu's own keyboard, its identity key, non-gamepad devices at rest, the watcher's timeout and once-per-element reports, and Step 2's two states. |
| `OnScreenKeyboardWindowsLayoutTests` | Every installed layout read through `ToUnicodeEx`, the US layout as Windows types it, ABNT2's /? key on a keyboard device, and each family's hint labels. |
| `MenuEditorKeyboardTests` | The Menus tab: the style and its defaults, each layout's rows and names, recording (gestures and menu cells only for Opens With), pointer rows, press points, resets, Types Through, Opens On, the symbols box, and the D-pad and face-button openers. |
| `KeyboardMenuSlotDeviceTests` | Input lists per device, Copy From Slot and paste moving inputs to the target slot's controller, and the Types Through list after the slots renumber. |
| `WorkshopKeyboardMenuImportTests` | The Show Keyboard import: the menu, its slot, its press modes, a stick half with a second input, its layer, and a binding with no input. |
| `StarterProfileCatalogTests` | The Desktop starter's keyboard menu. |

---

## Related pages

- [On-Screen Keyboard](../features/on-screen-keyboard.md)
- [Engine Library](engine-library.md#menudefinitionentry): the menu model the keyboard extends.
- [Settings and Serialization](settings-and-serialization.md#mappingset-v32): the `<Menu>` element's keyboard attributes.
- [Input Pipeline](input-pipeline.md)

---

*Last updated for PadForge 5.3.0.*
