# ViewModels Reference

*Every ViewModel class in PadForge: what it backs, what it exposes, and how state flows between the UI and the services layer.*

> **v4 (2026-07-12):** Refreshed for v4. Remote Link (`DashboardViewModel` + `SettingsViewModel`, and the `RemoteLinkTrustedPeer` / `RemoteLinkNearbyPeer` rows), the per-(slot, device) `DeviceSlotConfig` (renamed from `PlayStationSlotConfig`), `KbmSlotConfig` (SOCD / Snap Tap), multi-source mapping rows (`MappingSourceItem`), the mouse-gesture partial, and the Ember dashboard vocabulary all landed since the v3 rewrite. The HIDMaestro SDK surface, OpenXInput shim, thread-pool lifecycle, and bubble-up cascade live on [HIDMaestro Deep Dive](hidmaestro-deep-dive.md). If anything here drifts from the live source, the live source wins.
>
> **v4.1 (2026-07-30):** The Nintendo output type (#215) joins the family. `PadViewModel` gains the Bass Shakers tab (#236), the slot SOCD card (#240), the flick rotation offset, gyro Acceleration, and the macro Layer dropdown. `MacroItem` carries the #238 / #253 fire-mode wave and per-macro layer scope (#254). Mapping rows and sources gain Flip Output, per-source Acceleration, and the #251 axis-latch macro actions. The Touchpad partial grows the libinput pointer Response, momentum, and pointer-region cards. `DeviceSlotConfig` adds synthetic touch pressure (#239) and the Switch home-LED lane (#226).
>
> **v4.2:** The VR output type (#49) lands as `VirtualControllerType.Vr` (6), with a `VrControllerIcon` sidebar entry, a `VrOutputSnapshot`, and a SteamVR row in both driver-status surfaces (`DashboardViewModel.IsSteamVrInstalled`, plus the install / uninstall pair on `SettingsViewModel`). The pad page grows two slot-tier tabs: Bass Shakers at index 16 and Output at index 17 (SOCD plus Keep Controller Awake). `DeviceSlotConfig` gains headphone-jack volume, the DualSense audio-output path, and persona haptics, with `MacroActionType.HeadphoneVolumeUp` / `HeadphoneVolumeDown` (52 / 53) driving the volume. Sony headset head trackers get their own device class (`HeadsetMotion`, #188). `RawHidState` replaced the old `ExtendedRawState`, so the Extended snapshot is now `RawHidOutputSnapshot`.
>
> **v4.3:** The mapping picker gains one shared per-slot choice list plus a search box and device-visibility filter (#322 / discussion #302), both on `PadViewModel`. Voice macros (#317) add the `"Microphone"` device class, the Voice Macros preview on `DevicesViewModel`, `DeviceRowViewModel.ShowManageVoicePhrases`, and `MacroActionType.VoiceListenWhileHeld` (54). `MacroAction` grows the pressure-scaled turbo block (#290). `StickConfigItem` grows stick trackball momentum (#291), the touchpad partial grows the shared momentum knobs, and `PadViewModel` grows the Gyro Tilt envelope (#292). The Dashboard's web-controller card gains a URL and QR (#296), its SteamVR row goes tiered (#287), and Settings gains the low-battery notification trio (#293).
>
> **v4.4:** Head tracking moves from `SettingsViewModel` to `DashboardViewModel`, which also gains the Razer Chroma (#373), Logitech LIGHTSYNC (#382) and Razer Sensa (#374) enable-plus-status pairs. The Dashboard's driver-status strip is gone, leaving three bare installed flags and the full cards on Settings. `DeviceRowViewModel` gains `ShowQuickCharge` (#372), and `IsInternalVirtual` grows the `handheld://`, `sensor://` and `headtrack://` schemes. `PadViewModel` gains the `ExtendedConfig` reseed on a profile switch, the Grip option list and `IsLoadingPadSetting` (#392), the grouped `MacroTypeCatalog` picker, menu macro cells and `.pficons` icon packages (#390). The Profiles page gains external control (#366) and the per-profile polling override (#365).
>
> **Peripheral outputs (#494):** `DashboardViewModel` loses the Razer Chroma, Logitech LIGHTSYNC and Razer Sensa enable-plus-status pairs. Those outputs are vendor rows on the Devices page now, assigned to a virtual controller like any device, and each row's tab names where its output goes. `DeviceSlotConfig` gains `PeripheralLightingEnabled`, the Lighting tab's Control This Device’s Lighting switch for a mouse or keyboard. `DeviceRowViewModel` gains the `"PeripheralLighting"` and `"PeripheralHaptics"` type keys. `MacroActionType.SetChromaColor` paints the Razer devices assigned to its macro's virtual controller.

> **5.3.0:** `DashboardViewModel` gains the Twitch Chat row (#555) and the Screen Overlay list (`ScreenOverlayItem`, #560), and its slot cards carry the type chip and Preset name (#543). `SettingsViewModel` gains the keyboard takeover list (#549) and the full-charge and repeat battery notices. `DeviceSlotConfig` gains Screen Color (#559), per-key lighting and LED strip counts (#557), with `KeyColorsCardViewModel`, `LedStripsCardViewModel`, `KeyTargetPickerViewModel` and `MapKeyLightsViewModel` behind them. `MenuEditorItem` gains the Keyboard (On-Screen Keyboard, #566) and Hotbar styles. `MacroActionType` gains `SetKeyColors`, `ClearKeyColors`, `ToggleScreenOverlay` and `ProfileShortcut` (64 to 67), and `MacroRepeatMode` gains `UntilNextPress` (#561). `DeviceRowViewModel` gains the firmware and revision lines, the Use Only in PadForge rows (#549) and the Map Key Lights and Manage Chat Commands gates. Mapping and mapping-source `Sensitivity` clamps at 0.001 for the importers (#561).

> **6.0.0:** PadForge 6 (#574) rebuilt the interface, and the view models followed. `DashboardViewModel` keeps its name and now backs Home (`DashboardViewModel.Home.cs`, `.Cards.cs`, `.FirstRun.cs`), the Extras page's twelve extras and their switches (`.Extras.cs`) and the Crosshair and Magnifier extras (#585, `.Crosshairs.cs`, with `CrosshairItem` and `MagnifierItem`). `SlotSummary` is a Home card with its picture, heat and state word, and the controller page's header reads it through `SelectedSlotSummary`. New view models: `AddControllerViewModel` (the Add a Controller panel), `SearchViewModel` (Ctrl+K search) and `WebControllerPhone`. `PadViewModel` gains the six sections and the bar under the picture (`PadViewModel.Sections.cs`), the mapping list's device columns (`PadViewModel.List.cs`, with `ListColumn`, `RowCell` and `RowTag`), the Centering card (#588, `PadViewModel.Centering.cs`) and the Gyro card's activation rows (`PadViewModel.GyroActivation.cs`). Mapping rows and their sources gain a source line with shaping and gates (`MappingItem.Shaping.cs`, `MappingSourceItem.Shaping.cs`, `MappingSourceItem.Line.cs`). `DevicesViewModel` gains the page's lists, segments and search (`.List.cs`), the selected device's picture and cards (`.Board.cs`, `.SettingResets.cs`) and the compact gamepad test (`.Test.cs`). `SettingsViewModel` gains the page's groups and search, Get Profiles, Save Current Setup Here, the polling rate in hertz with this PC's wake rate, and the About page's lines. `StickConfigItem` gains the steering modes' Stick Deadzone. `MacroActionType` gains `ToggleCrosshair`, `ToggleMagnifier` and `MagnifierWhileHeld` (68 to 70). Removed: `MainViewModel`'s engine commands, events, brush and counts, `RefreshCommands` on `MainViewModel`, `DashboardViewModel.TotalDevices`, `IsGameTelemetryRunning`, `IsWebControllerPlainRunning`, `IsHidHideInstalled`, `IsMidiAvailable` and `IsSteamVrInstalled`, the slot vibration argument of `PadViewModel.UpdateFromEngineState`, the Devices page's facet filter and its assign and hide commands, `DeviceRowViewModel`'s divider and capability-strip flags and `NotifyDisplayChanged`, `KeyboardKeyItem.LayoutWidth` / `LayoutHeight`, `PadViewModel.OutputTypeIndex`, `EnumerateDeviceSlotConfigs`, `LeftMotorDisplay` / `RightMotorDisplay` and `StopMapAllCommand`, the per-Param recording flags on `MappingSourceItem`, `MacroItem.RemoveActionCommand` (now `RemoveStepCommand`), and `StickConfigItem.InDisplay` / `RawDisplay`.

---

All ViewModels live in `PadForge.App/ViewModels/` (`PadForge.ViewModels` namespace). Built on [CommunityToolkit.Mvvm](https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/) (`ObservableObject`, `RelayCommand`).

---

## ViewModelBase

**File:** `ViewModelBase.cs`

Abstract base class for all ViewModels. Extends `FiniteObservableObject`, which extends `ObservableObject` (`INotifyPropertyChanged`, `SetProperty`).

```csharp
public abstract class ViewModelBase : FiniteObservableObject
{
    private string _title = string.Empty;

    public string Title
    {
        get => _title;
        set => SetProperty(ref _title, value);
    }
}
```

| Property | Type | Description |
|----------|------|-------------|
| `Title` | `string` | Display title for the view. Used by navigation and page headers. |

### FiniteObservableObject

**File:** `FiniteObservableObject.cs`

An `ObservableObject` whose `SetProperty(ref double, ...)` and `SetProperty(ref float, ...)` overloads leave the property as it was when handed NaN. `Math.Clamp` passes NaN through, so a clamped setter used to store a NaN typed into a numeric box or read from a setting. Infinity passes, so a clamped setter turns it into its bound. `ViewModelBase` derives from it, and so do the rows and settings objects that hold a persisted number (`StickConfigItem`, `ScreenOverlayItem`, `TelemetryFieldEdit`). Those do not take `ViewModelBase` itself: its constructor subscribes each instance to the static culture event and never unsubscribes.

### Culture / Localization

The constructor subscribes to `Strings.CultureChanged` for live language switching. When the UI language changes, every ViewModel's `OnCultureChanged()` runs, letting derived classes refresh culture-dependent text.

`Strings.CultureChanged` uses a **weak event pattern**. Instance-method subscribers are stored as `(WeakReference<Target>, MethodInfo)` pairs, so short-lived ViewModels can be garbage-collected without unsubscribing. Dead entries are pruned on each raise. Static-method subscribers use strong references.

```csharp
protected ViewModelBase()
{
    Strings.CultureChanged += OnCultureChanged;  // weak. No GC leak
}

protected virtual void OnCultureChanged() { }
```

---

## Per-Setting Reset Commands

**File:** `SettingResetCommands.cs`

A partial of sixteen classes that adds one generic `ResetSettingCommand` (`RelayCommand<string>`) to each: `SettingsViewModel`, `DashboardViewModel`, `DeviceRowViewModel`, `PadViewModel`, `DeviceSlotConfig`, `MacroItem`, `MacroItem.TriggerInputEntry`, `MacroAction`, `MacroExpressionVariable`, `MappingItem`, `MappingSourceItem`, `EqBandVm`, `MenuEditorItem`, `MenuCellItem`, `ProfileShortcutViewModel`, and `RemoteLinkTrustedPeer`. The parameter is a property name. `CanResetSetting` accepts only the names its class lists, and `ResetSetting` writes that property's default, then raises the property's change notification even when the value was already the default. The `SettingResetButton` control (`PadForge.App/Controls/`) binds it with `CommandParameter` set to the property name. The dedicated `Reset…Command` members named on this page sit beside it. `DevicesViewModel` (`DevicesViewModel.SettingResets.cs`), `CrosshairItem` and `MagnifierItem` carry a `ResetSettingCommand` of their own on the same pattern.

---

## NavControllerItemViewModel

**File:** `MainViewModel.cs` (defined alongside MainViewModel)

Sidebar entry for one virtual controller. The card is one line: flame, slot number, type chip, `#` instance number, Preset name, remove button.

| Property | Type | Description |
|----------|------|-------------|
| `PadIndex` | `int` | Zero-based pad slot index (0–15). Read-only. |
| `Tag` | `string` | Navigation tag (`"Pad1"`–`"Pad16"`). Computed as `$"Pad{PadIndex + 1}"`. |
| `SlotNumber` | `int` | 1-based controller number among active slots. |
| `InstanceLabel` | `string` | Per-type instance label (e.g., `"1"`, `"2"`). |
| `PresetName` | `string` | The slot's Preset as its controller page's chip names it (`PadViewModel.PresetDisplayName`). The card prints it after the instance number. `MainViewModel.OnPadPresetChanged` carries a change to the entry on the UI thread. |
| `IconKey` | `string` | Resource key for controller type icon (e.g., `"XboxControllerIcon"`, `"DS4ControllerIcon"`, `"NintendoControllerIcon"`, `"ExtendedControllerIcon"`, `"MidiControllerIcon"`, `"KeyboardMouseControllerIcon"`, `"VrControllerIcon"`). |
| `IsEnabled` | `bool` | Virtual controller enabled. |
| `ConnectedDeviceCount` | `int` | Mapped physical devices connected. |
| `MappedDeviceCount` | `int` | Physical devices assigned to this slot in config, connected or not. Lets the mini card split "assigned but awaiting" (idle) from "nothing assigned" (cold), the same split a Home card makes. Added by commit `2006ac6b`. |
| `IsInitializing` | `bool` | Virtual controller initializing. |
| `IsVirtualControllerConnected` | `bool` | Live virtual controller is alive (created + reporting `IsConnected`). Drives the sidebar green-vs-yellow indicator so the slot stays green through the HM-inactivity grace window and only turns yellow once the timeout tears the VC down. |
| `IsCreateFailed` | `bool` | The slot's latest virtual-controller create attempt failed (engine createFailed latch). Distinct from awaiting devices, so the flame tooltip does not blame absent devices for a failed create. |

**Sidebar wiring:** MainWindow code-behind rebuilds one wpf-ui `NavigationViewItem` per `NavControllerItems` entry on `NavControllerItemsRefreshed` (`RebuildControllerSection` / `CreateControllerNavItem`), and subscribes each item's `PropertyChanged` so `SlotNumber`, `InstanceLabel`, `IconKey` (matched as a plain string in `UpdateControllerNavItemContent`), `IsEnabled`, and the flame-state flags update the card in place.

---

## MainViewModel

**File:** `MainViewModel.cs`
**DataContext for:** `MainWindow`

Root ViewModel. Manages navigation state, 16 pad ViewModels, sidebar controller entries, and app-wide status.

### Child ViewModels

| Property | Type | Description |
|----------|------|-------------|
| `Pads` | `ObservableCollection<PadViewModel>` | 16 pad ViewModels (one per slot). Created in constructor. |
| `NavControllerItems` | `ObservableCollection<NavControllerItemViewModel>` | Sidebar items for created slots. Rebuilt by `RefreshNavControllerItems()`. |
| `Dashboard` | `DashboardViewModel` | The view model behind Home, the Extras pages and the sidebar's foot (the class kept its Dashboard name). |
| `Devices` | `DevicesViewModel` | Devices list ViewModel. |
| `Settings` | `SettingsViewModel` | Application settings ViewModel. |

The constructor gives every `PadViewModel` a `KbmSlotChoicesProvider` (`MainViewModel.KeyboardMouseSlots`, the created slots whose type is Keyboard + Mouse, as `KbmSlotChoice` entries) for the keyboard menu's Types Through list (#566). It also subscribes `OnPadPresetChanged` (Preset name to the sidebar entry and the Home controller card at once, because the cards' own refresh rides the engine's display timer, which a stopped engine does not run) and `OnPadOutputTypeChanged` (a slot's `OutputType` or `SlotLabel` change calls `MenuEditorItem.RefreshTypesThrough` on every menu of every pad).

### Navigation Properties

| Property | Type | Description |
|----------|------|-------------|
| `SelectedNavTag` | `string` | Current nav tag: `"Home"` (the default), `"Devices"`, `"Profiles"`, `"Extras"`, `"Pad1"`–`"Pad16"`, `"Settings"`, `"About"`. MainWindow's `NavigateToTag` writes it. The sidebar's Add Controller entry (`"AddController"`) opens the Add a Controller panel and never becomes the tag. Also notifies `IsPadPageSelected` and `SelectedPadIndex`. |
| `IsPadPageSelected` | `bool` | True if a controller page (Pad1–Pad16) is selected. Computed. |
| `SelectedPadIndex` | `int` | Zero-based pad index for the selected controller page, or -1. Computed. |
| `SelectedPad` | `PadViewModel` | PadViewModel for the selected controller page, or null. Computed. |

### App-wide Status Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `StatusText` | `string` | `""` | The message line over the page's lower corner. Empty means no line. Plain writes are info-class and decay after about 5 s (`StatusDecayMs`). Every write restamps the decay window. |
| `IsEngineRunning` | `bool` | `false` | Polling loop active. Calls `RefreshEngineStatus()`. |
| `HasActiveSlots` | `bool` | `false` | Any virtual controller slots exist. Calls `RefreshEngineStatus()`. |
| `EngineStatusText` | `string` | - | Computed localized text: `Engine_Forging` (`"Forging"`, engine running with active slots) / `Common_Idle` (`"Idle"`, running with no created slots) / `Common_Stopped` (`"Stopped"`). Note: this is the localized display text. `DashboardViewModel.EngineStateKey` carries the non-localized `"Running"` / `"Idle"` / `"Stopped"` key for XAML DataTriggers. |
| `IsStatusDecayDue` | `bool` | - | Computed: the message is info-class, not empty, and older than `StatusDecayMs`. |

The polling rate and the connected-device count are on `DashboardViewModel` (`PollingFrequency`, `OnlineDevices`), which Home and the sidebar's foot read. No view-model command starts or stops the engine: Home's engine button (`EngineFlame`, bound to `DashboardViewModel.IsEngineOn`) raises `HomePage.EngineToggleRequested`, which MainWindow handles.

### Events

| Event | Args | Description |
|-------|------|-------------|
| `NavControllerItemsRefreshed` | `EventArgs` | Raised after `RefreshNavControllerItems()` completes. MainWindow uses this instead of `CollectionChanged` to avoid rapid sidebar rebuilds. |

### Key Methods

| Method | Description |
|--------|-------------|
| `RefreshNavControllerItems()` | Rebuilds sidebar entries from `SettingsManager.SlotCreated[]`, in each group's order (`VirtualControllerGroups.InOrder`, `SettingsManager.SlotOrders`). Computes per-type instance numbers and updates each pad's `Title`, `SlotLabel`, `TypeInstanceLabel`. Raises `NavControllerItemsRefreshed` only when the active-slot set changed (add / remove / reorder). Property-only changes (icon, label, enabled) update in place without the event. |
| `RefreshEngineStatus()` | Notifies `EngineStatusText`. Runs when the engine's state, the slot count or the language changes. |
| `SetStatus(string, bool persist = false)` | Writes the message line with an explicit class. `persist: true` (failures, prompts a later write always terminates) exempts the message from the decay sweep until the next write. |
| `ClearMenuRecordings()` | Runs on `RecorderService.RecordingCanceled`. Clears `HostRecording`, `RecordingKeyboardRow` and `KeyboardMapAllActive` on every menu of every pad, because a cancel drops the callback that would have cleared them (#566). |
| `ClearDecayedStatus()` | Clears a decayed info message. Re-checks `IsStatusDecayDue` first, so a write that lands mid-sweep wins. Called from MainWindow's 5 s driver-status timer. |

---

## DashboardViewModel

**Files:** `DashboardViewModel.cs`, `DashboardViewModel.Home.cs`, `DashboardViewModel.Cards.cs`, `DashboardViewModel.FirstRun.cs`, `DashboardViewModel.Extras.cs`, `DashboardViewModel.Crosshairs.cs`
**DataContext for:** Home (`Views/HomePage.xaml`), the Extras page and its twelve extras' pages (`Views/ExtrasPage.xaml`), and the engine block at the sidebar's foot (`MainWindow.xaml`). The controller page's header reads `SelectedSlotSummary`.

The class kept the name of the PadForge 5 Dashboard page that Home replaced (#574). It holds the controller cards, the engine's state, the device counts, and every extra's settings: Web Controller, Head Tracking, Game Telemetry, Twitch Chat, Remote Link, Motion Server (DSU), Game Mods, Overlays, Touchpad Overlay, Screen Overlay, Crosshair and Magnifier, in the catalog order of `ExtrasPage.Keys`.

### Slot Summaries

| Property | Type | Description |
|----------|------|-------------|
| `SlotSummaries` | `ObservableCollection<SlotSummary>` | Home's controller cards, one per created slot. Rebuilt by `RefreshActiveSlots()` only when the slot set or its order changed. |
| `ShowAddController` | `bool` | Home's Add Controller card shows (some type has room for another slot). Default `true`. |
| `SelectedSlotSummary` | `SlotSummary` | The summary of the slot whose controller page is open, null while none is. The controller page's header reads the power button, the state word and the stage chips from it, the values the slot's Home card shows. `SetSelectedPad` and every `RefreshActiveSlots` find it again, so it never holds a summary that left the list. Private setter. |

### Engine Status

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `EngineStatus` | `string` | `Common_Stopped` | Localized engine status. |
| `EngineStateKey` | `string` | `"Stopped"` | Non-localized state key (`"Running"`, `"Idle"`, `"Stopping"`, `"Stopped"`) for XAML DataTriggers. Notifies `IsEngineOn` and tells every slot summary whether the engine is stopped. |
| `IsEngineOn` | `bool` | `false` | Computed: `EngineStateKey != "Stopped"`, so idle and stopping count as on. Home's engine button (`EngineFlame`) binds its on state to it. |
| `HeroLine` | `string` | - | Computed: the sentence under Home's engine state, with no numbers in it: `Home_Hero_Forging`, `Home_Hero_Idle`, `Common_Stopping` or `Home_Hero_Stopped` by `EngineStateKey`. |
| `LiveControllers` / `ControllerCount` | `int` | - | Computed: how many cards have `Heat == SlotSummary.HeatForging`, and how many cards there are. |
| `LiveLine` | `string` | - | Computed: `Shell_Foot_Live_Format` with those two counts, the line under the engine's state at the sidebar's foot. |
| `PollingFrequency` | `double` | `0` | Polling frequency in Hz. Also notifies `PollingFrequencyText` and the three rate parts. |
| `PollingFrequencyText` | `string` | - | Computed: `Dashboard_PollingHz_Format` with the rate, or `Dashboard_PollingDash` when zero. |
| `PollingRateLead` / `PollingRateNumber` / `PollingRateTail` | `string` | - | Computed: the same rate in three parts (`FormatRuns.SplitValue`), so Home can set the number larger than its unit. With no rate the number is the dash and the other two are empty. |

### Device Counts

| Property | Type | Description |
|----------|------|-------------|
| `OnlineDevices` | `int` | The devices connected now, as the Devices page counts them: `InputService.CountConnectedDevices` counts the rows that are online and pass `DeviceRowViewModel.IsCountedDevice`, so it equals that page's `ConnectedTotal`. Written by `InputService` on the display refresh, `0` when the engine stops. Home's engine block shows it (`EngineDevices`). |

### Driver Status

`DashboardViewModel` holds no driver status. The HidHide, HIDMaestro, BthPS3, Windows MIDI Services and SteamVR rows are on Settings' Drivers card, backed by `SettingsViewModel`, and the Add a Controller type tiles read `SettingsViewModel.IsMidiAvailable` and `HMaestroVRController.IsAvailable()` themselves.

Through 5.3.1 this class carried three bare flags, `IsHidHideInstalled`, `IsMidiAvailable` and `IsSteamVrInstalled`. MainWindow's driver status refresh wrote them and nothing read them, and 6.0.0 removed them.

### DSU Motion Server

The Motion Server extra. Each extra's page on the Extras page shows a status flame whose `IsOn` is the extra's switch and whose `IsLive` is its serving flag (`IsDsuServerRunning` here).

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `EnableDsuMotionServer` | `bool` | `false` | DSU (cemuhook) motion server enabled. |
| `DsuMotionServerPort` | `int` | `26760` | UDP port. Clamped to 1024–65535. |
| `DsuServerStatus` | `string` | `"Stopped"` | DSU server status. |
| `IsDsuServerRunning` | `bool` | `false` | Serving truth for the status flame (#175): the actual server lifecycle, not the switch. Set by InputService at the same points that write `DsuServerStatus`. Null writes to `DsuServerStatus` coalesce to `Common_Stopped`. |

| Command | Description |
|---------|-------------|
| `ResetDsuPortCommand` | Resets `DsuMotionServerPort` to 26760. |

### Game Mods (#529)

The Game Mods extra: the server for DSX game mods. All three settings ride profiles. See [Game Mods Internals](game-mods-internals.md).

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `EnableGameModServer` | `bool` | `false` | The server listens while this is on and the engine runs. |
| `GameModServerPort` | `int` | `6969` (`GameModProtocol.DefaultPort`) | UDP port. Clamped to 1024–65535. |
| `GameModDsxStandIn` | `bool` | `false` | Run the DSX.exe stand-in while the server listens. |
| `GameModServerStatus` | `string` | `"Stopped"` | The card's line: listening, who sends to which virtual controller, the port in use, or the bind that failed. Set by `InputService` from `GameModServer.FormatStatus()`. |
| `IsGameModServerRunning` | `bool` | `false` | Serving truth for the status flame: the server listens, whatever the switch says. |

| Command | Description |
|---------|-------------|
| `ResetGameModPortCommand` | Resets `GameModServerPort` to 6969. |

### Game Telemetry (#531)

The Game Telemetry extra: the listener behind the Game Telemetry device row. Each setter mirrors into the static `GameTelemetryRuntime`, the head tracking card's shape, so a write lands whatever its source. The switch, the port, the game, the forward port and Full Speed ride profiles. The custom formats are one list for every profile. See [Game Telemetry Internals](game-telemetry-internals.md).

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `EnableGameTelemetry` | `bool` | `false` | The row listens while this is on and the engine runs. Mirrors to `GameTelemetryRuntime.Enabled`. |
| `GameTelemetryPort` | `int` | `20777` | The UDP port the games send to. Clamped to 1024–65535. Mirrors to `GameTelemetryRuntime.Port`. |
| `GameTelemetryFormat` | `GameTelemetryFormat` | `Auto` | The game picked, or Auto-Detect. Mirrors to `GameTelemetryRuntime.Format`. |
| `GameTelemetryCustomFormat` | `string` | `""` | The custom format read while the game is `Custom`. Null writes empty. Mirrors to `GameTelemetryRuntime.CustomFormatName`. |
| `GameTelemetryOptions` | `ObservableCollection<GameTelemetryOption>` | - | The picker: Auto, each game family, then each custom format with a valid name. A `GameTelemetryOption` is the pair of a `GameTelemetryFormat` and a custom format's name. Its `Display` is renamed in place on a language change. |
| `SelectedGameTelemetryOption` | `GameTelemetryOption` | Auto | The picker's selection, read from the game and the custom name, or the first option. Picking Project CARS 2 moves the port to 5606 and the ETS2 plugin to 49001, the two senders whose port cannot change. Picking another game afterward, or the reset, puts 20777 back while the port is still that sender's (`PickGameTelemetry`). A load or a profile applies its saved port as saved. A null write is ignored. |
| `GameTelemetryReadsUdp` | `bool` | `true` | Whether the picked game is read over UDP (`TelemetryReader.FormatReadsUdp`). False while Assetto Corsa is picked, which grays out Port and Forward to Port. Raised with `GameTelemetryFormat`. |
| `GameTelemetryForwardPort` | `int` | `0` | The port every packet is copied to on 127.0.0.1, 0 for none. Clamped to 0–65535. Mirrors to `GameTelemetryRuntime.ForwardPort`. |
| `GameTelemetryFullSpeed` | `int` | `300` | The speed, in km/h, that moves the Speed axis all the way. Clamped to 10–1000. Mirrors to `GameTelemetryRuntime.FullSpeedKmh`. |
| `GameTelemetryFormats` | `List<CustomTelemetryFormat>` | empty | The custom formats. A set mirrors them to `GameTelemetryRuntime.Formats`, which reopens the row, writes each variable field's axis slot back with `WriteAxes` so the settings file saves it, refreshes the expression variables' `TelemetryChannelOptions` and rebuilds `GameTelemetryOptions`. A picked custom format that is gone sends the picker back to Auto-Detect. The Extras page's Formats button (`ExtrasPage.xaml.cs`) sets it from `CustomTelemetryFormatsDialog.Result`. |
| `GameTelemetryStatus` | `string` | `Common_Stopped` | The page's status line: the game it hears, or why it hears nothing. Set by `InputService.UpdateGameTelemetryStatus`. Null coalesces back to `Common_Stopped`. |
| `IsGameTelemetryReceiving` | `bool` | `false` | A game's telemetry reaches the row. The status flame burns ember while it does, and gold while the row waits for a game. Set with the status line from the row's own status (`InputService.GameTelemetry.cs`), false when the row closes. |

| Command | Description |
|---------|-------------|
| `ResetGameTelemetryPortCommand` | Resets the port to 20777. |
| `ResetGameTelemetryGameCommand` | Back to Auto-Detect, with no custom format. |
| `ResetGameTelemetryForwardPortCommand` | Sets the forward port to 0, forwarding nothing. |
| `ResetGameTelemetryFullSpeedCommand` | Resets Full Speed to 300. |

| Method | Description |
|--------|-------------|
| `ApplyGameTelemetrySettings(GameTelemetryFormat format, string customName, int port, int forwardPort, int fullSpeed)` | Applies a saved game, port, forward port and Full Speed, from the settings file or a profile. The switch is excluded, and its caller sets it last. An undefined format, or a custom one whose format is gone, reads as Auto-Detect. An out-of-range port, forward port or Full Speed keeps the current value. |

### Head Tracking (#355, #403)

Three independent inputs feed the Head Tracker device row: a UDP listener on OpenTrack's port, a FreeTrack 2.0 shared-memory reader, and an OpenXR headset reader (#403) that also adds the two VR controller rows. The row exists while any of the three is on (`HeadTrackingRuntime.AnyEnabled`). Each setter mirrors into the static `PadForge.Common.Input.HeadTrackingRuntime` that the poll thread's device sweep reads, so a write lands whatever its source (global load, profile apply, the user). The UDP and FreeTrack toggles ride profiles as nullable legs (`ProfileData.EnableHeadTracking`, `ProfileData.EnableHeadTrackingFreeTrack`). The port, the OpenXR toggle and runtime, and the ranges are global. These properties moved here from `SettingsViewModel` on 2026-09-02. MainWindow's dirty-gate allowlist for `DashboardViewModel` names them, so a head-tracking edit marks the settings file dirty. See [Head Tracking: Internals](head-tracking-internals.md) and [OpenXR Input Internals](openxr-input-internals.md).

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `HeadTrackingEnabled` | `bool` | `false` | The OpenTrack UDP input. Mirrors to `HeadTrackingRuntime.Enabled`. |
| `HeadTrackingUdpPort` | `int` | `4242` | Port OpenTrack's "UDP over network" output sends to. Clamped to 1–65535. Mirrors to `HeadTrackingRuntime.UdpPort`. |
| `HeadTrackingFreeTrack` | `bool` | `false` | The FreeTrack 2.0 shared-memory input, independent of UDP. Mirrors to `HeadTrackingRuntime.FreeTrackEnabled`. |
| `HeadTrackingOpenXr` | `bool` | `false` | Read the headset through an OpenXR runtime, independent of the other two inputs and of SteamVR. Mirrors to `HeadTrackingRuntime.OpenXrEnabled`. Turning it on calls `RefreshOpenXrRuntimes()`. |
| `OpenXrRuntimes` | `ObservableCollection<OpenXrRuntimeChoice>` | - | Runtime picker items (`ManifestPath`, and `Display`, observable so an entry kept across a refresh takes a new caption): the system default (empty path) first, then each installed runtime `OpenXrRuntimeCatalog.Discover()` finds, read through the internal test seam `DiscoverOpenXrRuntimes`. Built on first read, never rebuilt from the getter. A saved runtime the registry no longer names stays listed under its manifest's file name. `RefreshOpenXrRuntimes()` rebuilds it. |
| `SelectedOpenXrRuntime` | `OpenXrRuntimeChoice` | system default | Reads and writes `HeadTrackingRuntime.OpenXrRuntimeManifest`. It changes the runtime this process uses, never the machine's active runtime. A null, which WPF writes when the box's entry leaves the list, and any write during a refresh are ignored. |
| `HeadTrackingRotationRange` | `int` | `90` | Degrees of head rotation at full deflection for the rotation axes. Clamped to 1–180. |
| `HeadTrackingTranslationRange` | `int` | `30` | Centimeters of head travel at full deflection for the translation axes. Clamped to 1–500. |
| `HeadTrackingRangeYaw` / `Pitch` / `Roll` / `X` / `Y` / `Z` | `int` | `0` | Per-axis range pins (#403) over `HeadTrackingRuntime.SetAxisRange`. `0` follows the axis family's range. Rotation axes clamp to 180, translation axes to 500. |
| `HeadTrackingStatus` | `string` | `Common_Stopped` | The Head Tracker row's source line (which source is live, or why none is). Pushed by `InputService` on the display tick whenever the device's `StatusVersion` moves. Null coalesces back to `Common_Stopped`. |
| `IsHeadTrackingReceiving` | `bool` | `false` | A source delivers a pose to the Head Tracker row. The page's status flame burns ember while one does, and gold while the inputs wait. Set with the status line. |
| `HeadTrackingOpenXrRuntimeChanged` | `object` | `null` | Always null. Raised when the chosen runtime changes, so the settings save picks the change up the way it picks up the toggles. |

| Command | Description |
|---------|-------------|
| `ResetHeadTrackingEnabledCommand` / `ResetHeadTrackingFreeTrackCommand` / `ResetHeadTrackingOpenXrCommand` | Turn the matching input off. |
| `ResetHeadTrackingOpenXrRuntimeCommand` | Back to the system default runtime. |
| `ResetHeadTrackingPortCommand` | Resets the port to 4242. |
| `ResetHeadTrackingRotationRangeCommand` | Resets the rotation range to 90. |
| `ResetHeadTrackingTranslationRangeCommand` | Resets the translation range to 30. |
| `ResetHeadTrackingRangeYawCommand` … `ResetHeadTrackingRangeZCommand` | Set one axis back to `0`, so it follows its family again. |
| `ResetHeadTrackingRangesCommand` | The Range card's Reset All (#574): the rotation and translation ranges back to 90 and 30. The per-axis ranges under More keep their own resets. |
| `HeadTrackingRecenterCommand` | Calls `HeadTrackingRuntime.Recenter()`. Only the OpenXR source has a neutral to move. OpenTrack and FreeTrack keep the zero their own application set. |

| Method | Description |
|--------|-------------|
| `RefreshOpenXrRuntimes()` | Rebuilds the runtime list in place: an entry whose manifest path is still wanted keeps its instance and takes the fresh caption, so the bound selection rides through. The saved runtime stays listed. Runs when `HeadTrackingOpenXr` turns on, from `NotifyHeadTrackingRangesChanged()`, and on a language switch once the list exists. |
| `NotifyHeadTrackingRangesChanged()` | Re-raises the six per-axis ranges and rebuilds the runtime list after a settings load or Reset to Defaults writes the statics they read. The rebuild lists a saved runtime the registry no longer names, which a list built before the load lacks. |

### Web Controller Server

The Web Controller extra.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `EnableWebController` | `bool` | `false` | Web controller server enabled. |
| `WebControllerPort` | `int` | `8080` | HTTP/WebSocket port. Clamped to 1024–65535. |
| `WebControllerStatus` | `string` | `"Stopped"` | Web controller server status. |
| `IsWebControllerRunning` | `bool` | `false` | Serving truth for the page's status flame (#175): actual server lifecycle, not the switch. Set by InputService alongside `WebControllerStatus`. |
| `WebControllerClientCount` | `int` | `0` | Connected web controller clients. |
| `WebControllerPhones` | `ObservableCollection<WebControllerPhone>` | empty | The phones and browsers connected now, for the page's Phones card (#574). `InputService` calls `AddWebControllerPhone` on the UI thread when a session connects (a phone that reconnects under the same id replaces its old entry) and `RemoveWebControllerPhone` when that same session ends, so the end of a session a reconnect replaced leaves the new entry alone. |
| `WebControllerUrl` | `string` | `null` | The live server URL, `https://` when the secure lane bound (#296). Empty when stopped. |
| `WebControllerQr` | `ImageSource` | `null` | QR of `WebControllerUrl` so a phone opens the controller by scanning (#296). Null when stopped, which hides the image. |
| `HasWebControllerQr` | `bool` | `false` | Whether a QR is available. Drives its visibility. |
| `WebControllerHttpsWarning` | `string` | `null` | Why the main address fell back to plain HTTP and phone motion is off. Null while it serves HTTPS. |
| `EnableWebControllerPlainHttp` | `bool` | `false` | Also serve the plain HTTP address. Machine setting, never in a profile. |
| `WebControllerPlainHttpPort` | `int` | `8081` (`WebControllerServer.DefaultPlainPort`) | The plain address's port. Clamped to 1024–65535. |
| `WebControllerPlainHttpLocalOnly` | `bool` | `false` | Admit only this PC on the plain address. |
| `WebControllerAccessCode` | `string` | fresh code | The plain address's access code. Starts as a freshly generated code, and the setter ignores anything that is not a valid code, so it is never empty. |

| `WebControllerPlainStatus` | `string` | `null` | Where the plain address runs, or why it does not. Null while stopped or off. |
| `WebControllerPlainUrl` | `string` | `null` | The plain address with its `?code=`. Null when not served. |
| `WebControllerPlainQr` / `HasWebControllerPlainQr` | `ImageSource` / `bool` | `null` / `false` | QR of the plain address. None in This PC Only mode. |

| Command | Description |
|---------|-------------|
| `ResetWebPortCommand` | Resets `WebControllerPort` to 8080. |
| `CopyWebControllerUrlCommand` | Copies `WebControllerUrl` to the clipboard. No-op when empty. |
| `ResetWebPlainPortCommand` | Resets `WebControllerPlainHttpPort` to 8081. |
| `NewWebAccessCodeCommand` | Replaces `WebControllerAccessCode` with a fresh code. |
| `CopyWebControllerPlainUrlCommand` | Copies `WebControllerPlainUrl` to the clipboard. No-op when empty. |

`ResetSettingCommand` also resets `EnableWebControllerPlainHttp` and `WebControllerPlainHttpLocalOnly` to off.

### Remote Link (#138)

The Remote Link extra: peer-to-peer controller relay over the LAN. Its page hosts the server switch and the outbound-connect box. The paired-peer manager and identity-protection state live on `SettingsViewModel` and are surfaced here through the `RemoteLink` reference below.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `RemoteLink` | `SettingsViewModel` | - | The Settings VM, set once at startup. Holds `TrustedPeers`, `NearbyUnpaired`, and the identity-protection block so the Remote Link page can show paired peers, identity mode, and nearby PCs in one place. |
| `EnableRemoteLink` | `bool` | `false` | Whether the Remote Link server is listening for paired peers. |
| `AutoReconnect` | `bool` | `true` | When a paired PC appears on the LAN, establish the link without a click. |
| `RemoteLinkPort` | `int` | `27500` | TCP control + UDP data port. Clamped to 1024–65535. |
| `RemoteLinkStatus` | `string` | `Common_Stopped` | Remote Link server status text. Null coalesces to `Common_Stopped`. |
| `IsRemoteLinkRunning` | `bool` | `false` | Serving truth for the page's status flame (#175): true only while the link server object is live. The status text can carry identity-unlock errors while the server never started, so the flame keys on this, not the text or the switch. |
| `RemoteLinkConnectHost` | `string` | `""` | Host (or host:port) the user types to initiate an outbound pairing. |
| `RemoteLinkMyCode` | `string` | `""` | This PC's connection code (#294): a self-contained code embedding the public and private endpoints, minted while Remote Link runs. Empty until the STUN probe returns. Set by InputService. Notifies `HasRemoteLinkMyCode`. |
| `HasRemoteLinkMyCode` | `bool` | - | Computed: a shareable code is available to show or copy. |
| `RemoteLinkNatWarning` | `string` | `""` | Network warning (#294): set when the STUN probe found no public address (UDP blocked) or an endpoint-dependent NAT direct connections cannot traverse. Empty when the network looks punchable. Notifies `HasRemoteLinkNatWarning`. |
| `HasRemoteLinkNatWarning` | `bool` | - | Computed: `RemoteLinkNatWarning` is non-empty. |

| Command | Description |
|---------|-------------|
| `ResetRemoteLinkPortCommand` | Resets `RemoteLinkPort` to 27500. |
| `ConnectToPeerCommand` | Raises `ConnectToPeerRequested` with the trimmed `RemoteLinkConnectHost` when non-empty. |
| `CopyRemoteLinkCodeCommand` | Copies `RemoteLinkMyCode` to the clipboard. No-op when empty. |

| Event | Args | Description |
|-------|------|-------------|
| `ConnectToPeerRequested` | `Action<string>` | User asked to connect/pair with a typed host[:port]. |

### Touchpad Overlay (3.2) and Overlays

The Touchpad Overlay extra: an on-screen transparent touchpad window that drives the DS4 / DualSense touchpad on the assigned PlayStation slot. `EnableMenuOverlay`, `EnableShiftLayerFlyout` and `EnableProfileOverlay` are the Overlays extra's three switches.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `EnableTouchpadOverlay` | `bool` | `false` | Overlay visible. |
| `EnableMenuOverlay` | `bool` | `true` | Radial / touch menu overlay (#9): render the `MenuOverlayWindow` HUD while a menu is engaged. When off, menus still hover and commit blind (the runtime never depends on the window). |
| `EnableShiftLayerFlyout` | `bool` | `true` | Show the shift-layer flyout while a slot sits on a non-Base layer. Purely a display of engagement state the poll thread already computes, so turning it off changes nothing about which layer is active. |
| `EnableProfileOverlay` | `bool` | `true` | Show the profile-switch overlay when a profile changes. The switch still happens when off, this only suppresses the announcement. |
| `TouchpadOverlayOpacity` | `double` | `0.25` | Surface opacity 0.0–1.0. Notifies `TouchpadOverlayOpacityPercent`. |
| `TouchpadOverlayOpacityPercent` | `int` | `25` | 0–100 integer view of opacity for NumberBox binding. |
| `TouchpadOverlayMonitor` | `int` | `0` | Monitor index the overlay is pinned to (0 = primary). |
| `TouchpadOverlayLeft` / `Top` | `double` | `-1` | Window position. `-1` = centered on the chosen monitor. |
| `TouchpadOverlayWidth` / `Height` | `double` | `500` / `250` | Window size. Clamped to `>= 150` and `>= 80` respectively. |
| `IsTouchpadOverlayRunning` | `bool` | `false` | Overlay window currently shown. Drives `TouchpadOverlayStatus`. |
| `TouchpadOverlayStatus` | `string` | - | Computed: `Common_Running` or `Common_Stopped`. |

| Command | Description |
|---------|-------------|
| `ResetOpacityCommand` | Resets opacity to default 0.25. |
| `ResetTouchpadOverlayPositionCommand` | Raises `ResetTouchpadOverlayPositionRequested`. `InputService` recenters the live overlay (or seeds defaults if not open) and clears persisted `Left` / `Top`. |
| `ResetTouchpadOverlayCardCommand` | Reset All on the Look and Place card (#574): runs the two commands above. |

| Event | Description |
|-------|-------------|
| `ResetTouchpadOverlayPositionRequested` | Recenter request from the UI. |

### Twitch Chat (#555)

The Twitch Chat extra: its device row reads a channel's chat and presses the slots it is assigned to when viewers type commands. See [Twitch Chat Internals](twitch-chat-internals.md). Each setter mirrors into the static `PadForge.Common.Input.Twitch.TwitchChatRuntime`, the same shape as Game Telemetry. The switch and the channel are machine settings, like the plain web address, and stay out of profiles, so a profile switch never opens or closes the connection.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `EnableTwitchChat` | `bool` | `false` | Mirrors to `TwitchChatRuntime.Enabled`. Turning it off also clears `TwitchChatPaused`, so chat control starts unpaused the next time. |
| `TwitchChatChannel` | `string` | `""` | The channel as typed, the name or the channel's address. Null coalesces to empty. Mirrors to `TwitchChatRuntime.Channel`, which keeps the name Twitch uses. |
| `TwitchChatClaimApprovalIndex` | `int` | `0` | Who approves a viewer's `!claim`, a `TwitchClaimApproval` by number: `0` the streamer alone, `1` with moderators, `2` also any two viewers (`Viewers`). A value below 0 or above `Viewers` (a hand-edited file, or the box's `-1` when it loses its selection) is ignored. Mirrors to `TwitchChatRuntime.ClaimApproval`. |
| `TwitchChatStatus` | `string` | `"Stopped"` | The row's line: the channel it reads, or why it reads nothing. Null coalesces back to `Common_Stopped`. |
| `IsTwitchChatRunning` | `bool` | `false` | The row has joined the channel's chat. Drives the page's status flame. |
| `IsTwitchChatOpen` | `bool` | `false` | The row is open. The streamer's controls act on it. |
| `TwitchChatPaused` | `bool` | `false` | The streamer's Pause. The row ignores every command, pausing stops the command playing and clears the line. Mirrors to `TwitchChatRuntime.Paused`. Not saved. |
| `TwitchChatDisplayUrl` | `string` | `null` | The controller picture page on the plain HTTP address, code included, for an OBS browser source. Null while the plain address is not served. |

| Command | Description |
|---------|-------------|
| `TwitchChatPauseCommand` | Toggles `TwitchChatPaused`. |
| `TwitchChatSkipCommand` | `TwitchChatRuntime.Skip()`. |
| `TwitchChatClearCommand` | `TwitchChatRuntime.ClearLine()`. |
| `TwitchChatEndClaimCommand` | `TwitchChatRuntime.EndClaim()`. |
| `CopyTwitchChatDisplayUrlCommand` | Copies `TwitchChatDisplayUrl` through `ShellLaunch.SetClipboardText`. No-op when empty. |

### Screen Overlays (#560)

The Screen Overlay extra's page lists up to `KeyboardScreenInfo.MaxOverlays` (8) overlay windows, one card each. Each shows what a keyboard screen shows, on any PC. The list is always at least one item, so the page reads like a single extra's until another is added. See [Keyboard Screens Internals](keyboard-screens-internals.md).

| Member | Type | Description |
|--------|------|-------------|
| `ScreenOverlays` | `ObservableCollection<ScreenOverlayItem>` | The overlays, sorted by `Number`. The constructor adds overlay 1. |
| `CanAddScreenOverlay` | `bool` | Computed: fewer than `MaxOverlays`. |
| `AddScreenOverlayCommand` | `RelayCommand` | Calls `AddScreenOverlay()`: the new item takes the lowest free number, so a macro that names a number finds the overlay that took it. |
| `RemoveScreenOverlay(item)` | method | Refuses when only one is left. |
| `FindScreenOverlay(number)` / `ScreenOverlayNumbers()` | methods | Lookup by number, and the numbers on the card for a macro that names every overlay. |
| `SnapshotScreenOverlays()` / `LoadScreenOverlays(data)` | methods | The list for the settings file (`ScreenOverlayData[]`), and back. A file or profile from before overlays existed has none, which loads as one overlay, off. An entry whose number is outside 1-8 or already taken is dropped. `_loadingScreenOverlays` keeps the load from raising `ScreenOverlays` changes. |
| `ScreenOverlayEdited()` | method | A saved value of an overlay changed. Raises `PropertyChanged("ScreenOverlays")`, which marks settings dirty and tells `InputService` to bring the windows into line. |
| `ResetScreenOverlayPositionRequested`, `ChooseScreenOverlayContentRequested` | `EventHandler<ScreenOverlayItem>` | Raised from an item's Reset Position and Choose What It Shows (`RequestScreenOverlayResetPosition`, `RequestScreenOverlayChoose`). `InputService` recenters a live overlay, or clears the saved place when it is not showing. |
| `ResetScreenOverlayChoicesRequested` | `EventHandler<ScreenOverlayItem>` | Raised by an overlay's Reset All (`RequestScreenOverlayResetChoices`): what it shows goes back to the default. MainWindow holds the keyboard screens' choices and makes the change. |
| `ScreenOverlayModeOf` | `Func<int, KeyboardScreenMode>` (internal) | What an overlay shows, by its number, read from the saved choices. Set by MainWindow. Null leaves every overlay at the default mode. |
| `ScreenOverlayChoicesChanged(Guid row)` | internal method | A screen's choices changed: the overlay that is that row says what it shows again. |

`ScreenOverlayItem` (`ScreenOverlayItem.cs`, derives `FiniteObservableObject`) is one overlay's group. `Number` is its identity and survives removing another overlay.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Number` | `int` | - | 1-8. |
| `Title` | `string` | - | The card's title, `Extras_ScreenOverlay_Number_Format` with the number ("Overlay 2"). Macros, the dialog's title and the status line keep `KeyboardScreenService.OverlayName`. |
| `OneOfSeveral` | `bool` | - | Computed: more than one overlay exists. Each card shows its Remove button only then. |
| `Enabled` | `bool` | `false` | Overlay shown. |
| `Opacity` / `OpacityPercent` | `double` / `int` | `0.8` (`DefaultOpacity`) / `80` | Clamped to 0.0-1.0. |
| `Monitor` | `int` | `0` | Monitor index, 0 is primary. |
| `Left` / `Top` | `double` | `OverlayPlacement.NoPlace` (-100000) | Saved window place. |
| `Width` / `Height` | `double` | `320` / `240` (`DefaultWidth`, `DefaultHeight`) | Clamped to at least 80 and 60 (`MinWidth`, `MinHeight`). |
| `IsRunning` | `bool` | `false` | The window is shown. Drives `Status`. |
| `Blank` | `KeyboardScreenService.Blank` (internal) | - | Why the running overlay shows nothing, for `Status`. |
| `Status` | `string` | - | Stopped, Running, or Running with the reason it shows nothing (`KeyboardScreens_Status_NoPicture_Format`, `KeyboardScreens_Status_NoLightbar_Format`). |
| `ShowsText` | `string` | - | Computed: what the overlay shows now, in the keyboard screens' words (`KeyboardScreenService.ModeName` of `ScreenOverlayModeOf(Number)`, or the default mode). `RefreshShows()` raises it. |
| `EnableId`, `OpacityId`, `ChooseId`, `ResetPositionId`, `RemoveId`, `ResetAllId` | `string` | - | `ScreenOverlay_<Control>_<Number>` automation ids. |

Commands: `ResetEnabledCommand` (off), `ResetOpacityCommand` (0.8), `ResetPositionCommand`, `ChooseCommand`, `RemoveCommand`, and `ResetAllCommand`, Reset All on the overlay's card (#574): off, what it shows, its opacity and its place, each to its default. `RefreshText()` and `RefreshOneOfSeveral()` re-raise the culture text and the Remove gate. Every setter of a saved value calls `DashboardViewModel.ScreenOverlayEdited()`. `ToData()` and `Load(ScreenOverlayData)` move the values through the setters' bounds.

### Crosshair and Magnifier (#585)

**File:** `DashboardViewModel.Crosshairs.cs`

| Member | Type | Description |
|--------|------|-------------|
| `Crosshairs` | `ObservableCollection<CrosshairItem>` | The crosshairs on the Crosshair page. There is always at least one, so the page reads like a single extra's until someone adds another. |
| `CanAddCrosshair` | `bool` | Computed: fewer than `CrosshairData.MaxCrosshairs` (10). |
| `AddCrosshairCommand` | `RelayCommand` | Calls `AddCrosshair()` (internal): the new crosshair takes the lowest free number, so a macro that names a number finds the crosshair that took it. |
| `RemoveCrosshair(item)` / `FindCrosshair(number)` | internal methods | Remove one crosshair, and look one up by number. |
| `SnapshotCrosshairs()` / `LoadCrosshairs(data)` | internal methods | The list for the settings file (`CrosshairData[]`), and back. A file or profile from before crosshairs existed has none, which loads as one crosshair, off. An entry whose number is out of range or already taken is dropped. |
| `CrosshairEdited()` | internal method | A saved value of a crosshair changed. The property change marks the settings dirty and tells `InputService` to bring the windows into line. |
| `Magnifier` | `MagnifierItem` | The magnifier's settings, made on first read. |
| `MagnifierEnabled` | `bool` | The Magnifier switch on the Extras page and on Home: the magnifier's own `Enabled`, a property of this view model as every catalog switch is. |
| `SnapshotMagnifier()` / `LoadMagnifier(data)` | internal methods | The settings file's `MagnifierData`, and back. Null, from a file or profile from before the magnifier, is the defaults: off. |
| `MagnifierEdited()` | internal method | A saved value of the magnifier changed: the settings are dirty and `InputService` brings the magnifier into line. |

### Extras Switches

**File:** `DashboardViewModel.Extras.cs`

Each tile on the Extras page and each extra's page head carries one switch. Four extras gather several settings under that switch, so the switch is a computed property that remembers what it turned off. The remembered sets are saved with the program's settings (`SettingsService` reads them back into these properties).

| Member | Type | Description |
|--------|------|-------------|
| `HeadTrackingAnyEnabled` | `bool` | On while any of the three head-tracking inputs is on. Turning it off stores the inputs that were on in `HeadTrackingLastSources`. Turning it on restores that set, or `HeadTrackingStartingSources` (UDP and FreeTrack, never OpenXR, which opens a session) when none is stored. |
| `HeadTrackingLastSources` | `int` | The inputs the switch turned off last, as bits (`HeadTrackingUdpBit` 1, `HeadTrackingFreeTrackBit` 2, `HeadTrackingOpenXrBit` 4, internal constants). Zero until it has turned any off. The setter masks to the three bits. |
| `ResetHeadTrackingSourcesCommand` | `RelayCommand` | The reset beside the Head Tracking switch: each input back to off. |
| `OverlaysAnyEnabled` | `bool` | On while any of the menu overlay, shift-layer flyout and profile overlay is on. Off stores the set in `OverlaysLastShown`. On restores it, or all three (`OverlaysStartingSet`). |
| `OverlaysLastShown` | `int` | The overlays the switch turned off last, as bits (`MenuOverlayBit` 1, `ShiftLayerFlyoutBit` 2, `ProfileOverlayBit` 4). |
| `ResetOverlaysCommand` | `RelayCommand` | The reset beside the Overlays switch: each overlay back to on, through `ResetSettingCommand`. |
| `ScreenOverlaysAnyEnabled` / `ScreenOverlaysLastOn` | `bool` / `int` | The Screen Overlay switch: on while any overlay on the list is on. The remembered set is a bit per overlay number, masked to `MaxOverlays`. Turned on with none remembered, or with every remembered overlay since removed, it turns on the first. |
| `CrosshairsAnyEnabled` / `CrosshairsLastOn` | `bool` / `int` | The Crosshair switch, the same rule over the crosshair numbers, masked to `MaxCrosshairs`. |

### Home

**Files:** `DashboardViewModel.Home.cs`, `DashboardViewModel.Cards.cs`, `DashboardViewModel.FirstRun.cs`

Home shows the engine block, the controller cards, an offer for a new device, and the extras in use. With no controller it shows its first page instead.

| Member | Type | Description |
|--------|------|-------------|
| `HomeCards` | `HomeCardSize` | The size of the controller cards, the Cards choice (`Home_Cards`: Detailed, Compact, Auto). Saved with the program's settings. Notifies `IsCardsCompact`. |
| `DetailedCardsRunPast` | `bool` | Whether detailed cards would run past the window as it is now. The page writes it, since only it knows its size. |
| `IsCardsCompact` | `bool` | Computed: `HomeCardSizes.IsCompact(HomeCards, DetailedCardsRunPast)`, Compact, or Auto while detailed cards would run past the window. |
| `HomeOfferGuid` / `HasHomeOffer` | `Guid` / `bool` | The device Home is offering a virtual controller of its own, or `Guid.Empty`. `InputService` writes it for a device PadForge has just met that is connected and on no virtual controller. Cleared by Not Now, when the device goes offline, when it lands on a virtual controller by any route, and when the prompt's setting is turned off. Never saved: the device's own `HomeOfferPending` is. |
| `HomeOfferText` | `string` | `Home_Offer_Format` ("{0} is connected and not in use.") with the device's name, the localized name the Devices page shows. Private setter. |
| `HomeOfferLead` / `HomeOfferName` / `HomeOfferTail` | `string` | The same sentence in three parts, so the page can set the name apart. A format with no `{0}` is all lead. |
| `SetHomeOffer(Guid, string)` / `ClearHomeOffer()` | methods | Start and end the offer. An empty Guid clears it. |
| `DismissHomeOfferCommand` | `RelayCommand` | Not Now: clears the offer and raises `HomeOfferDismissed` (`EventHandler<Guid>`), and `InputService` ends the offer for that device for good. Use It has no command here: the window opens Add a Controller for the device, and the offer stays until the device is on a virtual controller. |
| `ExtrasCount` | `int` (internal const) | 12, the extras the Extras page lists. A test holds it to `ExtrasPage.Keys`. |
| `ExtrasInUseCount` | `int` | Computed: how many of the twelve extras are on, each read through the switch its tile shows. |
| `HasExtrasInUse` / `ShowsExtrasIntro` / `ShowsExtrasRestLine` | `bool` | Computed: Home's Extras in Use heading and rows show (some extra is on), Home introduces the Extras page in place of the list (none is on), and Home says where the other extras are (some are on and some are not). |
| `ExtrasRestLead` / `ExtrasRestLink` / `ExtrasRestTail` | `string` | The line under the tiles that counts the other extras, in three parts around its bracketed link word (`BracketPart`). |
| `ExtrasOnLead` / `ExtrasOnNumber` / `ExtrasOnTail` / `ExtrasOnSpoken` | `string` | The count at the end of the Extras page's head, `Extras_OnCount_Format` ("{0} of {1} on"), in three parts so the number draws large, and as one sentence for a screen reader. |
| `BracketPart(string, int)` | internal static method | One of the three parts of a text around its first pair of square brackets: 0 before, 1 inside, 2 after. A text with no closed pair is all part 0. |

First page members (`DashboardViewModel.FirstRun.cs`):

| Member | Type | Description |
|--------|------|-------------|
| `IsFirstRun` | `bool` | Computed: no virtual controller exists (`SlotSummaries.Count == 0`). |
| `FirstRunDeviceGuid` / `HasFirstRunDevice` / `FirstRunDeviceName` | `Guid` / `bool` / `string` | The controller the first page names, as the Devices page names it, or none. |
| `SetFirstRunDevice(Guid, string, DeviceRowViewModel)` / `ClearFirstRunDevice()` | methods | `InputService` names the controller on every device walk and the page follows its row for the battery and the link. A null row (a device the Devices page has not listed yet) leaves the line empty. |
| `FirstRunShowsStopped` / `FirstRunShowsDevice` / `FirstRunShowsNoDevice` | `bool` | Computed: the engine is stopped (nothing reads which devices are connected, so the card says so and offers Start), a controller is named, none is connected. |
| `FirstRunCardTitle` | `string` | The card's title: `Main_EngineStopped`, the controller's name, or `Home_FirstRun_NoDevice`. |
| `FirstRunLineLead` / `FirstRunLineBattery` / `FirstRunLineTail` | `string` | The card's line in three parts, so the battery takes tabular figures. |
| `FirstRunLineFacts` / `FirstRunLineGlyph` / `FirstRunLineGap` | `string` | The line as drawn up to the battery, the battery's level glyph and the space before the percentage, read from the row (`BatteryGlyph`, `BatteryGap`). |
| `FirstRunLineText` / `HasFirstRunLine` | `string` / `bool` | The whole line in words for a screen reader, and whether there is a line. |
| `FirstRunBody` | `string` | The words under the heading: `Home_FirstRun_Body` ("this controller") while the card names one, `Home_FirstRun_BodyNoDevice` ("your controller") while it names none. |
| `FirstRunTypes` | `IReadOnlyList<ControllerTypeChoice>` | The three tiles: Xbox, PlayStation and Keyboard + Mouse (`ControllerTypeChoice.FirstRunSet()`). |
| `MoreTypesLead` / `MoreTypesLink` / `MoreTypesTail` | `string` | The line under the tiles in three parts, so the four other types' names make a link that opens Add a Controller. |

### Key Methods

| Method | Description |
|--------|-------------|
| `RefreshActiveSlots(IList<int>, bool)` | Rebuilds `SlotSummaries` when the active-slot list or its order changed, then decides Home's first page once the list is whole. Updates the `Main_VirtualController_Format` labels, finds `SelectedSlotSummary` again, sets `ShowAddController`. Called by InputService and MainWindow. |
| `SetSelectedPad(int)` | Names the slot whose controller page is open, `-1` for none, and sets `SelectedSlotSummary`. The index is remembered, so a later `RefreshActiveSlots` rebuild finds that slot's new summary. |
| `RenderTierChanged()` (internal) | Tells every card the computer's drawing tier changed. Home's page calls it from `RenderCapability.TierChanged`. |
| `CanResetSetting(string)` (internal static) | The names `ResetSettingCommand` accepts on this class (`SettingResetCommands.cs`). |

---

### SlotSummary

**File:** `DashboardViewModel.cs` (nested class)

One controller card on Home, and the state the controller page's header reads through `DashboardViewModel.SelectedSlotSummary`. `ToString()` returns the card's screen-reader name, the "Slot 3" its header shows (`AccessibleNames.SlotTitle`).

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `PadIndex` | `int` | - | Zero-based slot index. Read-only. |
| `SlotLabel` | `string` | - | Display label (`Main_VirtualController_Format`, "Virtual Controller 1"). |
| `MappedDevices` | `ObservableCollection<PadViewModel.MappedDeviceInfo>` | `null` | Live reference to the pad's mapped-device list, so a detailed card lists each device with its battery (#175). Set by InputService. Same-reference sets are no-ops. |
| `IsVirtualControllerConnected` | `bool` | `false` | Virtual controller connected to its backend. |
| `IsInitializing` | `bool` | `false` | Virtual controller initializing. |
| `IsCreateFailed` | `bool` | `false` | The slot's latest create attempt failed (engine createFailed latch). Its own state: a failed slot with online devices is neither forging nor awaiting devices. |
| `MappedDeviceCount` | `int` | `0` | Devices mapped to this slot. Notifies `HasMappedDevices`. |
| `HasMappedDevices` | `bool` | - | Computed: `MappedDeviceCount > 0`. |
| `ConnectedDeviceCount` | `int` | `0` | Mapped devices connected. |
| `EngineStopped` | `bool` | `true` | The engine is stopped. `DashboardViewModel` tells each summary, so a card can say its heat without looking past itself. |
| `Heat` | `string` | `HeatCold` | One word that never changes with the language, for the views to switch on: `HeatForging` (`"Forging"`) while the virtual controller is live or being made, `HeatWaiting` (`"Waiting"`) while the slot is on and has devices but the engine is stopped or the virtual controller is not there, `HeatCold` (`"Cold"`) while it is off or has no device. The sidebar pill's rule (`MainWindow.ComputeFlameHeat`) without the engine's idle state. |
| `StateWord` | `string` | - | Computed: the word on the card's pill, which is the controller's switch. In order: `Common_Disabled` while off, `Main_Initializing`, `Main_VcFailed`, `Dashboard_StatusCold` with nothing mapped, `Main_EngineStopped`, `Main_AwaitingDevices` once the virtual controller is gone, else `Main_Active` ("Forging"). Through the inactivity grace the controller is still live with its devices away, so it reads Forging until it is taken down. |
| `WaitHint` | `string` | - | Computed: what a waiting controller waits for, or empty. `Home_Card_StartsWithEngine` while the engine is stopped, else `Home_Card_StartsWhenThis` or `Home_Card_StartsWhenOne` (one mapped device or several) while none is connected. |
| `FirstDevice` / `FirstDeviceNote` | `PadViewModel.MappedDeviceInfo` / `string` | - | The one device a compact card names, the first connected or else the first, and what follows its name: that it is not connected, or how many more devices there are. `ReadFirstDevice()` reads them, through the static `FirstDeviceOf(devices)`. |
| `Picture` / `PictureGray` / `HasPicture` | `ImageSource` / `ImageSource` / `bool` | `null` / `null` / `false` | The controller's picture on the card's stage, what its own page shows in the finish chosen there, and the same picture with its colors taken out for a card that is not forging. Null for a type with no picture, whose card shows the type's symbol. `HasPicture` is also true while a still of the 3D model is being made. |
| `PictureMarks` / `HeldLevels` | `IReadOnlyList<StillMark>` / `byte[]` | - | Where each control is drawn on the picture, and how far each is held now, in steps (`StillMarks.Steps`), so a held button lights on the card. A new array each time a step changes. |
| `LiveModel` / `ShowsLiveModel` | `LiveModel` / `bool` | `null` / `false` | The 3D model a still was drawn from, which the card shows moving while the controller forges (`LiveStage`), and whether it does: it has one and `LiveStage.DrawsIn3D`. |
| `LiveArt` / `ShowsLiveArt` | `LiveArt` / `bool` | `null` / `false` | The layers the 2D art was made of, which the card shows moving (`LiveArtStage`). |
| `PictureMoves` | `bool` | - | Computed: `ShowsLiveModel` or `ShowsLiveArt`. A picture that does not move lights ember marks over it (`HeldGlow`). |
| `StagePose` | `StagePose` | - | What is held on the controller now as the moving picture shows it, in steps (`PoseOf(pad, buttons)`: sticks in steps of 256, triggers in 64ths, the held buttons and a finger on either stick's top). |
| `IsEnabled` | `bool` | `true` | Slot enabled for output. |
| `SlotNumber` | `int` | `1` | 1-based controller number among active slots. |
| `TypeInstanceLabel` | `string` | `"1"` | Per-type instance label. |
| `OutputType` | `VirtualControllerType` | `Xbox` | Virtual controller output type. (XML on-disk name is `"Microsoft"` via `[XmlEnum]` for v2/early-v3 back-compat. In-code identifier is `Xbox`.) Changing it notifies `TypeGeometry` and `TypeGlyph`. |
| `TypeGeometry` / `TypeGlyph` | `Geometry` / `string` | - | The type chip's branded logo (null for the types drawn as a glyph), and the MDL2 glyph for those. Same `SlotTypeIconMap` as the Devices page slot badges. |
| `PresetName` | `string` | `""` | The slot's Preset as its controller page's chip names it (`PadViewModel.PresetDisplayName`), printed under the card's title (discussion #543). Set by `MainViewModel.OnPadPresetChanged`. |
| `StageLedger` | `ObservableCollection<SlotStageInfo>` | empty | Pipeline stage ledger (#175 item 10): one entry per configuration stage the slot's assigned devices actually have (sticks / triggers / gyro / lighting / touchpad / audio), in that order. Rebuilt per slot by `InputService.RefreshSlotStageLedger` on the display refresh's 1 s slow lane. Entries mutate in place when membership is unchanged so the card doesn't re-template. |

Internal methods: `RefreshWords()` re-raises `StateWord` and `WaitHint` and reads the first device again (a state or the language changed). `PictureIsFor(...)` and `SetPicture(...)` set the picture and what it was made for (Preset, type, finishes, still or 2D art), so `InputService` asks again only when one changed. `ReadHeld(pad)` reads what is held and tells the card only when a step changed. `ForgetPicture()` has the picture asked for again at the next refresh. `RenderTierChanged()` re-raises the moving-picture gates after a drawing-tier change (a remote desktop session started or ended).

### SlotStageInfo

**File:** `DashboardViewModel.cs`

One stage entry in a slot card's pipeline heat ledger (#175 item 10).

| Property | Type | Description |
|----------|------|-------------|
| `Kind` | `string` | Stable stage identity (`"Sticks"`..`"Audio"`). Membership comparisons key on this so in-place updates are possible. Read-only. |
| `Glyph` | `string` | Segoe font glyph for the font stages. Empty for shape stages. Read-only. `ToString()` returns the stage's screen-reader name (`Pad_Sticks`, `Pad_Triggers`, `Pad_Gyro`, `Pad_Lighting`, `Pad_Touchpad`, `Pad_Audio`). |
| `IsStickShape` | `bool` | True for the Sticks entry. Rendered with the Zacksly stick ring + disc geometries instead of a font glyph. Read-only. |
| `IsTriggerShape` | `bool` | True for the Triggers entry. Rendered with the Zacksly trigger body geometry. Read-only. |
| `IsHot` | `bool` | True when the stage carries a non-default configuration on any assigned device. Ember when hot, ashen steel when inert. |
| `Summary` | `string` | Composite change key for the tooltip readout (all lines joined). Empty when inert, which disables the tooltip. Notifies `HasSummary`. |
| `HasSummary` | `bool` | Computed: tooltip gate, no tooltip on inert stages. |
| `SummaryLines` | `ObservableCollection<StageSummaryLine>` | Per-device readout lines for the hover tooltip, in binding order. A device still at its defaults reads `Home_Stage_Defaults` ("Default Settings"). |

### StageSummaryLine

**File:** `DashboardViewModel.cs`

One tooltip line of a stage's readout: device-class glyph, device name, then mono value tokens.

| Property | Type | Description |
|----------|------|-------------|
| `DeviceGlyph` | `string` | Device-class glyph. Empty for slot-level lines. |
| `DeviceShape` | `Geometry` | A wheel's or a joystick's drawing, which stands before the line in place of a glyph, or null. |
| `DeviceName` | `string` | Body-face device name, carrying its trailing `"  ·  "` separator. Empty for slot-level lines like the audio master volume. |
| `Tokens` | `string` | Value tokens joined with `" · "`. |

### HomeCardSize

**File:** `DashboardViewModel.Cards.cs`

The Cards choice on Home: `Auto` (0), `Detailed` (1), `Compact` (2). Auto shows detailed cards while they fit the window and compact ones once they would run past it. The internal static `HomeCardSizes` holds the rules: `FromStored(int)` reads a settings file's value (anything else is Auto), `RunPast(cardsTop, detailedHeight, windowHeight)` says whether a detailed grid runs past the window (a grid that ends on the window's edge fits), and `IsCompact(choice, detailedRunPast)`.

### OpenXrRuntimeChoice and GameTelemetryOption

**Files:** `DashboardViewModel.cs`, `GameTelemetryOption.cs`

`OpenXrRuntimeChoice` is one line of the OpenXR runtime picker: `ManifestPath` (init, empty for the system default) and `Display`, observable so an entry kept across a refresh takes a new caption. `GameTelemetryOption` is one line of the game picker: `Format`, `CustomName`, `Display` (from the internal static `DisplayFor(format, customName)`), `Matches(format, customName)`, and the internal `RaiseDisplayChanged()` that a language change calls. Both return `Display` from `ToString()`.

---

## CrosshairItem

**File:** `CrosshairItem.cs` (derives `FiniteObservableObject`)

One crosshair's card on the Crosshair extra's page (#585): its switch, its style, its display and offset, and how it is drawn. `Number` is its identity and stays through removing another crosshair, so a macro that names crosshair 3 keeps meaning the same one. Sizes are whole pixels. Every value lives in a `CrosshairData`, and each setter writes it, makes a new `Look` and calls `DashboardViewModel.CrosshairEdited()`. Ranges are `CrosshairData`'s constants.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Number` | `int` | - | 1 to `MaxCrosshairs` (10). |
| `Title` | `string` | - | `Extras_Crosshair_Number_Format` ("Crosshair 2"). Macros name it the same way. |
| `OneOfSeveral` | `bool` | - | Computed: more than one crosshair exists. Each card shows its Remove button only then. |
| `Look` | `CrosshairData` | - | A copy of the settings for the card's preview and the window, new after each change. |
| `Enabled` | `bool` | `false` | The crosshair shows. |
| `Style` / `StyleIndex` / `StyleNames` | `CrosshairStyle` / `int` / `IReadOnlyList<string>` | `Cross` | The style (Cross, Circle, Dot, Image), as the style box's index and lines in the enum's order. |
| `IsCross` / `IsCircle` / `IsDot` / `IsImage` | `bool` | - | Computed from `Style`. |
| `IsDrawn` / `HasThickness` | `bool` | - | Computed: a style drawn from shapes, which takes a color and an outline (not Image), and a style with a line thickness and a center dot (Cross and Circle). |
| `Display` / `DisplayChoices` | `string` / `IReadOnlyList<ScreenDisplayChoice>` | `""` | The display's Windows name, empty for the primary. A null write (the box's selection cleared by a new list) changes nothing. The choices are `ScreenDisplayChoice.ListFor(Display)`: the primary display, each display by number, and the saved one while it is not connected. `RefreshDisplays()` (internal) makes a new list when a display comes or goes or the language changes. |
| `OffsetX` / `OffsetY` | `int` | `0` | Pixels from the display's center, -4000 to 4000. |
| `ColorR` / `ColorG` / `ColorB` / `ColorHex` | `byte` / `byte` / `byte` / `string` | `#2EFA2E` | The color. Hex text that is no color changes nothing. |
| `Opacity` / `OpacityPercent` | `double` / `int` | `1.0` / `100` | 0 to 1. |
| `Outline` / `OutlineThickness` | `bool` / `int` | `true` / `1` | The outline and its width, 1 to 10. |
| `OutlineR` / `OutlineG` / `OutlineB` / `OutlineHex` | `byte` / `byte` / `byte` / `string` | - | The outline's color. |
| `Rotation` | `int` | `0` | Degrees clockwise, 0 to 359. |
| `SmoothEdges` | `bool` | - | Antialiased edges. |
| `Length` / `Thickness` / `Gap` | `int` | `10` / `2` / `4` | The cross's arms: length 0 to 200, thickness 1 to 40, gap -20 to 200. |
| `CenterDot` / `TShape` | `bool` | - | A dot in the center, and the T shape with no top arm. |
| `Radius` / `Sides` | `int` | `12` / `64` | The ring's radius, 2 to 400, and its sides, 3 to 64 (64 is round). |
| `DotSize` | `int` | `4` | 1 to 100. |
| `ImagePath` / `ImageName` | `string` | `""` | The picture's path, and its file name or `Extras_Crosshair_NoPictureChosen`. |
| `ImageWidth` / `ImageHeight` / `KeepProportions` | `int` / `int` / `bool` | `64` / `64` / `true` | The drawn size, 1 to 8000, and whether width and height move together in the picture's own proportions. |
| `IsRunning` | `bool` | `false` | The crosshair's window is up. |
| `Problem` | `CrosshairProblem` (internal) | `None` | Why a crosshair that is on shows nothing: `NoPicture` (an Image crosshair whose picture cannot be read) or `OffDisplay` (the offset puts it wholly off its display). |
| `Status` | `string` | - | `Common_Running` while the window is up, `Common_Stopped` while off, else the problem (`Extras_Crosshair_Status_NoPicture`, `Extras_Crosshair_Status_OffDisplay`). |
| `EnableId`, `StyleId`, `DisplayId`, `PictureId`, `RemoveId`, `ResetAllId` | `string` | - | `Crosshair_<Control>_<Number>` automation ids. |

Commands: `OwnSizeCommand` (`UseOwnSize()`, the drawn size back to the picture's own), `RemoveCommand`, `ResetAllCommand` (Reset All on the card: off, and every value back to its default) and `ResetSettingCommand`, whose names `CanResetSetting` lists. Internal: `UsePicture(path)` takes a picture chosen on the page at its own size, `ToData()` and `Load(CrosshairData)` (values held to their ranges), `RefreshText()`, `RefreshOneOfSeveral()`, and the static `Hex` and `TryHex` (`#RRGGBB` or `RRGGBB`, any case).

## MagnifierItem

**File:** `MagnifierItem.cs` (derives `FiniteObservableObject`)

The Magnifier extra's settings (`DashboardViewModel.Magnifier`). Values live in a `MagnifierData`, ranges are its constants, and each setter calls `DashboardViewModel.MagnifierEdited()`.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Enabled` | `bool` | `false` | The magnifier is on. |
| `Mode` / `ModeIndex` / `ModeNames` | `MagnifierMode` / `int` / `IReadOnlyList<string>` | `Lens` | Lens, Full Screen or Spotlight. `IsLens`, `IsSpotlight` and `HasZoom` (Lens and Full Screen zoom, Spotlight only shades) are computed from it. |
| `Follow` / `FollowIndex` / `FollowNames` | `MagnifierFollow` / `int` / `IReadOnlyList<string>` | `ScreenCenter` | What the magnifier centers on: `ScreenCenter`, `Pointer`, or `Crosshair` (the first crosshair that is on, its display's center plus its offset). `FollowsCenter` is computed: the display row counts only while it marks a display's center. |
| `Display` / `DisplayChoices` | `string` / `IReadOnlyList<ScreenDisplayChoice>` | `""` | As on `CrosshairItem`, with `RefreshDisplays()`. |
| `ZoomPercent` | `int` | `200` | The zoom as a whole percentage, 125 to 1600. |
| `LensShape` / `LensShapeIndex` / `LensShapeNames` | `LensShape` / `int` / `IReadOnlyList<string>` | `Circle` | The lens's shape. `IsRound` is computed: a round lens has one size, its width. |
| `LensWidthName` | `string` | - | `Extras_Magnifier_Size` ("Size") for a round lens, `Extras_Magnifier_Width` for a rectangle. The width row's label, slider, box and reset take it. |
| `LensWidth` / `LensHeight` | `int` | `400` / `400` | 80 to 2000. |
| `Border` / `BorderR` / `BorderG` / `BorderB` / `BorderHex` / `BorderThickness` | `bool` / `byte` / `byte` / `byte` / `string` / `int` | `true` | The lens border, its color and its thickness, 1 to 20. |
| `SpotlightSize` | `int` | - | The spotlight circle's width in pixels, 40 to 2000. |
| `SpotlightDimPercent` | `int` | - | How dark the display goes outside the spotlight, 10 to 95 percent. |
| `IsRunning` | `bool` | `false` | The magnifier runs. |
| `Failure` | `string` (internal) | `null` | What Windows refused, in the user's words. |
| `Status` | `string` | - | Computed: `Failure`, else `Common_Running` or `Common_Stopped`. |

Commands: `ResetAllCommand` (off, and every value back to its default) and `ResetSettingCommand` over the names `CanResetSetting` lists. Internal: `ToData()`, `Load(MagnifierData)` (values held to their ranges, null is the defaults) and `RefreshText()`.

## WebControllerPhone

**File:** `WebControllerPhone.cs`

A phone or browser connected to the web controller now, as the Web Controller page's Phones card lists it (#574). `Id` (the session device's `InstanceGuid`) and `Name` are public, and `ToString()` returns `Name` for a screen reader. It keeps the session's `WebControllerDevice` (internal `Device`), so the session that ends is the one that leaves the list.

## AddControllerViewModel

**File:** `AddControllerViewModel.cs`
**DataContext for:** the Add a Controller panel (`Views/AddControllerView.xaml`), which the sidebar's Add Controller entry, Home's Add Controller card and Home's Use It open.

Made fresh each time the panel opens by the internal static `Build(devices, countOf, total, midiAvailable, steamVrAvailable, midiReason)`: `countOf` gives how many of a type exist and `total` how many in all. Its values are fixed once built.

| Property | Type | Description |
|----------|------|-------------|
| `Devices` | `IReadOnlyList<DrivenByChoice>` | Driven By: the devices, then Choose Later. Empty when no device can be offered. |
| `ShowsDrivenBy` | `bool` | Computed: `Devices.Count > 0`. |
| `SelectedDevice` | `Guid` | The device the new controller takes: the checked choice's, `Guid.Empty` for Choose Later or no device. |
| `Common` | `IReadOnlyList<ControllerTypeChoice>` | Xbox, PlayStation and Nintendo. |
| `More` | `IReadOnlyList<ControllerTypeChoice>` | Keyboard + Mouse, Extended, MIDI and VR. |
| `FullNotice` / `IsFull` | `string` / `bool` | Why no tile can be used while every slot is taken, or empty, and whether it is set. |

### ControllerTypeChoice

One type of virtual controller on a tile (#574): Add a Controller's seven and Home's three on its first page. Init-only: `Type`, `AutomationId` (the old popup button's id, `AddXbox360Btn`, `AddDS4Btn`, `AddNintendoBtn`, `AddRawBtn`, `AddKeyboardMouseBtn`, `AddMidiBtn`, `AddVrBtn`, from `AddButtonId(type)`, or `Home_FirstRun_` and the type on Home), `Name` (`ControllerType_*`, from `SlotTypeIconMap.NameFor`), `Line` (what the type is for, or why it cannot be made now, from `LineOf(type)`), `ToolTip` (its name, or why it cannot be made) and `IsAvailable`. `Geometry` and `Glyph` come from `SlotTypeIconMap`. The internal static `For(type, ofType, total, midiAvailable, steamVrAvailable, midiReason)` applies the rules: none past 16 controllers in all or past the type's own cap, no MIDI without a MIDI API, no VR without SteamVR. `FirstRunSet()` returns Home's three (Xbox, PlayStation, Keyboard + Mouse), each available.

### DrivenByChoice and DeviceLine

`DrivenByChoice` is one Driven By line: `Device`, `Name`, `LineLead`, `LineBattery` (tabular figures), `BatteryGlyph` and `BatteryGap`, `LineTail`, `AccessibleName` (the name, then the line after a comma), `AutomationId` (`AddController_Device_` and the device's place in the list, or `AddController_ChooseLater`) and `IsChecked`. The internal static `For(device, name, bluetooth, battery, index, batteryGlyph)` makes a device's line, checked when it is the first, and `ChooseLater()` the last line, which makes the controller with no device. The internal static `DeviceLine.Parts(bluetooth, battery, bothFormat, batteryFormat)` splits a device's line into lead, battery and tail: Bluetooth with a battery takes `bothFormat`, a battery alone `batteryFormat`, Bluetooth alone `Pad_Transport_Bluetooth`, neither nothing.

## SearchViewModel

**File:** `SearchViewModel.cs`
**DataContext for:** the search panel MainWindow opens from the title bar's search box (`TitleSearchBox`) or Ctrl+K.

| Member | Type | Description |
|--------|------|-------------|
| `Query` | `string` | The words typed. Each change runs the query. |
| `Results` / `ResultsView` | `ObservableCollection<SearchResult>` / `ICollectionView` | The results, and the same grouped under their labels in the order the query gave: each group's best, Documentation last. |
| `SelectedResult` | `SearchResult` | The picked result, the first after each query. |
| `HasResults` | `bool` | Computed. |
| `NoResultsText` / `HasNoResultsText` | `string` / `bool` | `Search_NoResults_Format` (Nothing in PadForge matches “{0}”.) while the query finds nothing but the documentation, else empty. |
| `SelectedAnnouncement` | `string` | What a screen reader hears as the pick moves while the focus stays in the query box: the result's `AutomationName`. |
| `ShortcutText` | `string` | The language's `Key_Control` and " K". |
| `Run(bool keepSelection = false)` | method | Runs the query again: on a change of language, when Search opens on the words it had, and when the other controllers' answers come in. With `keepSelection` the picked result stays picked while it is still listed (the same entry, controller and item or place). |
| `MoveSelection(int)` | method | Moves the pick by that many results, stopping at either end. |
| `Open()` / `Close()` | methods | Raise `OpenRequested` (`EventHandler<SearchResult>`, Enter or a click, with the result) and `CloseRequested` (Escape). |

---

## SettingsViewModel

**Files:** `SettingsViewModel.cs`, its part of `SettingResetCommands.cs`
**DataContext for:** the Settings page (`Views/SettingsPage.xaml`), the Profiles page (`Views/ProfilesPage.xaml`) and the About page

Application-level settings: theme, language, drivers, profiles, and engine configuration.

### Settings Page Groups and Resets

The Settings page (#574) shows one group at a time, picked from its list: `SettingsGroup` is `General`, `Input`, `Hardware`, `Drivers`, `Data`, in that order.

| Member | Type | Description |
|--------|------|-------------|
| `SelectedSettingsGroup` | `SettingsGroup` | The group the page shows while its search box is empty. For this run only: the page opens on General. |
| `SettingsSearchText` | `string` | What the page's search box holds. While it holds a word the page shows the matching rows of every group. Not saved, and emptied when the page is left. |
| `ResetCardCommand` | `RelayCommand<string>` | A card's Reset All (#574): every setting the card names in `CardSettings(card)` (internal static, in the card's order) goes back to its default through its own reset. |
| `ResetSettingCommand` / `CanResetSetting(string)` | `RelayCommand<string>` / internal static | The per-row reset described under [Per-Setting Reset Commands](#per-setting-reset-commands). |

### Theme

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `SelectedThemeIndex` | `int` | `0` | 0 = System, 1 = Light, 2 = Dark. Raises `ThemeChanged`. |

| Event | Args | Description |
|-------|------|-------------|
| `ThemeChanged` | `int` | Raised when theme selection changes. Arg = theme index. |

### Language

| Property | Type | Description |
|----------|------|-------------|
| `AvailableLanguages` | `IReadOnlyList<LanguageInfo>` | `LanguageCatalog.All`: one row for each language in `Resources/Strings/Languages.tsv`, sorted by own name. Each `LanguageInfo` carries `Tag`, `EnglishName`, `NativeName`, `IsRightToLeft`, `IsComplete`, `Culture`, and `EnglishNameIfDifferent`, the English name the picker shows beside the own name, empty when the two match. |
| `SelectedLanguage` | `CultureInfo` | Current UI language. Applies immediately via `Strings.ChangeCulture()`. With no explicit selection it reads the row `LanguageCatalog.Resolve` finds for the current UI culture: its own, its nearest parent's or an alias's (de-DE shows `de`, en-AU shows `en-GB`), else American English. |

| Member | Type | Description |
|--------|------|-------------|
| `LanguageCode` | `string` | Persisted language code for serialization. Empty when no language was picked. |
| `SetLanguageFromCode(string)` | method | Sets the language from the persisted code, found through `LanguageCatalog.Find`, so a code saved before American and British English each had a row (`en`) reads `en-US`. When it differs from the current UI culture it goes through `Strings.ChangeCulture()`, which raises `CultureChanged`, so a reload to another saved language updates the live window. An empty or unknown code is a no-op. |
| `ResetLanguageToSystemDefault()` | method | Clears the explicit selection (`LanguageCode` saves `""`) and switches back to the culture the process started under, read through its row of the language table (`LanguageCatalog.InterfaceCulture`) as startup reads it. Used by Reset to Defaults and by the language row's reset button. |

### Driver Status: HIDMaestro

HIDMaestro is shipped as an embedded managed SDK (`HIDMaestro.Core`, bundled at `Resources/HIDMaestro/HIDMaestro.Core.dll`). The user-mode driver still needs to be registered with Windows once. That happens inside the engine via `HMContext.InstallDriver()` (called from `InputManager.Step5.VirtualDevices.cs:EnsureHMaestroContext`), not through `DriverInstaller`. The SettingsViewModel exposes a read-only version string read from the bundled assembly at startup.

| Property | Type | Description |
|----------|------|-------------|
| `HIDMaestroVersion` | `string` | HIDMaestro SDK version, `major.minor.build` with no `v` prefix. Initialized from the embedded `HIDMaestro.Core` assembly via `GetEmbeddedHidMaestroVersion()`. |
| `IsHIDMaestroInstalled` | `bool` | The driver of this PC's HIDMaestro backend is installed: HIDMaestro's package in the driver store on the UMDF2 backend, usbip-win2's host controller on the USB/IP backend. Set by `MainWindow.RefreshHIDMaestroStatus` from `HIDMaestroRemoval.IsDriverInstalled()` at startup, on the driver status timer and after a removal. |
| `HIDMaestroStatusText` | `string` | Computed: `Common_Installed` or `Common_NotInstalled`. Raised again on a language change. |

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `UninstallHIDMaestroCommand` | Always | Raises `UninstallHIDMaestroRequested`, which `MainWindow.UninstallHIDMaestroAsync` handles. Available with the driver gone, since HIDMaestro can leave other things behind. |

### Driver Status: BthPS3

| Property | Type | Description |
|----------|------|-------------|
| `BthPS3Version` | `string` | The BthPS3 version PadForge carries (`major.minor.build`, no `v` prefix), from the `DriverVer` of its embedded `BthPS3.inf` (`Ds3DriverInstaller.BundledBthPs3Version`). |
| `IsBthPS3Installed` | `bool` | Either BthPS3 driver is installed as a service. Set by `MainWindow.RefreshBthPS3Status` from `Ds3DriverInstaller.IsAnyBthPs3DriverInstalled()` at startup, on the driver status timer and after a removal. |
| `BthPS3StatusText` | `string` | Computed: `Common_Installed` or `Common_NotInstalled`. Raised again on a language change. |

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `UninstallBthPS3Command` | Always | Raises `UninstallBthPS3Requested`, which `MainWindow.UninstallBthPS3Async` handles. Available with the drivers gone, since PadForge's WinUSB package and certificate can remain. |

### Driver Status: HidHide

| Property | Type | Description |
|----------|------|-------------|
| `IsHidHideInstalled` | `bool` | HidHide installed. |
| `HidHideStatusText` | `string` | Computed: `Common_Installed` (`"Installed"`) or `Common_NotInstalled` (`"Not Installed"`). On a machine that is neither x64 nor ARM64 (`PlatformSupport.HidHideAvailable` false) it reads `Common_NotAvailableOnArm64` instead. |
| `HidHideVersion` | `string` | HidHide version. |
| `HidHideWhitelistPaths` | `ObservableCollection<string>` | Whitelisted application paths. |
| `ICadePads` | `ObservableCollection<string>` | Pads in iCade mode marked on the Devices page, as `0xVVVV/0xPPPP` pairs (hifihedgehog/SDL#33 Part 16). MainWindow's `SetICadeMode` edits it. |
| `DjiRemoteHosts` | `ObservableCollection<string>` | DJI remotes added by address in the pairing dialog, as `a.b.c.d:port` keys (hifihedgehog/SDL#33 Part 6). `DjiRemoteHostsChanged` fires on each add or remove (`RaiseDjiRemoteHostsChanged`, internal), never on load. |
| `FlydigiScreenBindings` | `ObservableCollection<string>` | The Flydigi Apex 4 nodes a screen send moved to WinUSB and has not yet given back to Windows' Xbox driver (#586). A send adds the node before the move and drops it after the hand-back, so a node a crash cut off is given back at the next start. |
| `UsioLayout` | `string` | The Namco USIO's layout, `"taiko"` or `"tekken"` (hifihedgehog/SDL#33 Part 14). MainWindow's `SetUsioLayout` sets it. |
| `SelectedWhitelistPath` | `string` | Selected whitelist path. Refreshes `RemoveWhitelistPathCommand`. |

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `InstallHidHideCommand` | `!IsHidHideInstalled && PlatformSupport.HidHideAvailable` | Raises `InstallHidHideRequested`. |
| `UninstallHidHideCommand` | `IsHidHideInstalled && !HasAnyHidHideDevices()` | Raises `UninstallHidHideRequested`. |
| `AddWhitelistPathCommand` | `IsHidHideInstalled` | Raises `AddWhitelistPathRequested`. |
| `RemoveWhitelistPathCommand` | `SelectedWhitelistPath != null` | Removes selected path, raises `WhitelistChanged` (`RaiseWhitelistChanged`, internal). |

| Event | Description |
|-------|-------------|
| `InstallHidHideRequested` | Install HidHide. |
| `UninstallHidHideRequested` | Uninstall HidHide. |
| `AddWhitelistPathRequested` | Add whitelist path (opens file dialog). |
| `WhitelistChanged` | Whitelist was modified (add or remove). |

### Driver Status: Windows MIDI Services

The card names the API PadForge drives (`MidiApiSelection`), offers PadForge's build of the App SDK runtime where it would give MIDI slots ports of their own, and removes an installed runtime, Microsoft's or PadForge's. MainWindow's status refresh, on the 5-second driver timer, writes the inputs from `MidiApiSelection.ForCard`, `MidiApiSelection.CanOfferRuntimeInstall` and `DriverInstaller`. See [Driver Installation Internals](driver-installation-internals.md#windows-midi-services).

| Property | Type | Description |
|----------|------|-------------|
| `ActiveMidiApi` | `MidiApiKind` (internal) | `InBox`, `AppSdk`, `Legacy` or `None`. Notifies `IsMidiAvailable` and the card text. |
| `CanInstallMidiRuntime` | `bool` | The card offers the runtime (`MidiApiSelection.CanOfferRuntimeInstall`). Shows the Install button. |
| `IsMidiRuntimeInstalled` | `bool` | The App SDK runtime is installed, Microsoft's or PadForge's (`DriverInstaller.IsMidiRuntimeInstalled`). Shows the Uninstall button. |
| `MidiRuntimeVersion` | `string` | The runtime's version, from its DLL (`DriverInstaller.GetMidiRuntimeVersion`). |
| `MidiApiNotStarted` | `bool` | The probe started no API, the legacy one included, or timed out on a stuck service. Also true while MIDI is held released for the runtime's uninstall. |
| `MidiNotRunningReason` | `MidiNotRunningReason` (internal) | Why nothing runs while `MidiApiNotStarted` holds: `ServiceDidNotRespond`, `DriverDidNotRespond` (a classic MIDI driver, which no service restart reaches) or `Uninstalling`. Written from `MidiVirtualController.NotRunningReason`. Notifies the card text. |
| `MidiInBoxFailure` | `int` (internal) | The HRESULT of an in-box API that Windows registers and that failed to activate, or 0. The legacy API runs in its place. Written from `MidiVirtualController.InBoxActivationFailure`. Notifies the card text. |
| `MidiUninstallerRunning` | `bool` (internal) | A runtime uninstaller PadForge started has not exited (`MidiRuntimeSwitch.UninstallerRunning`). Re-evaluates `UninstallMidiServicesCommand`. |
| `IsMidiAvailable` | `bool` | Computed: `ActiveMidiApi != None`. Lights the card's flame. |
| `MidiServicesStatusText` | `string` | Computed: `Settings_MidiStatusInBox` ("Built into Windows"), `Settings_MidiStatusRuntime` ("App SDK Runtime"), `Settings_MidiStatusLegacy` ("Legacy MIDI API"), `Settings_MidiStatusNotRunning` ("Not Running") or `Settings_MidiStatusUnavailable` ("Not Available"). |
| `MidiServicesDetailText` | `string` | Computed: under the in-box API, empty, or `Settings_MidiOlderRuntime_Format` when a runtime is also installed. Under the runtime, its version. Under the legacy API, `Settings_MidiLegacy`, or `Settings_MidiInBoxFailed_Format` with the HRESULT when `MidiInBoxFailure` is set. Otherwise empty unless `MidiApiNotStarted`, and then by `MidiNotRunningReason`: `Settings_MidiNotRunning`, `Settings_MidiNotRunningDriver` or `Settings_MidiUninstallRunning`. |
| `MidiDetailIsVersion` | `bool` | Computed: the detail line is the runtime's version. |
| `MidiInstallTooltip` | `string` | Computed: the Install button's tooltip, what it installs, or while an uninstaller PadForge started still runs, that Install waits for it. |

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `InstallMidiRuntimeCommand` | `CanInstallMidiRuntime` | Raises `InstallMidiRuntimeRequested`. |
| `UninstallMidiServicesCommand` | `IsMidiRuntimeInstalled && !MidiUninstallerRunning && !(ActiveMidiApi == AppSdk && HasAnyMidiSlots())` | Raises `UninstallMidiServicesRequested`. Under the in-box or the legacy API, MIDI slots do not hold the runtime. Unavailable while an uninstaller PadForge started still runs. |

| Event | Description |
|-------|-------------|
| `InstallMidiRuntimeRequested` | Download and install PadForge's build of the runtime (`DriverInstaller.InstallMidiRuntime`). |
| `UninstallMidiServicesRequested` | Uninstall the installed runtime (`DriverInstaller.UninstallMidiRuntime`). MainWindow asks first when the runtime is Microsoft's bundle. |

### Driver Status: SteamVR (#49)

The VR slot type needs SteamVR present. PadForge can install it Steam-free through steamcmd, and it only offers to remove the copy it created itself.

| Property | Type | Description |
|----------|------|-------------|
| `IsSteamVrInstalled` | `bool` | A SteamVR install of either shape is present (Steam client, or the Steam-free steamcmd one). Notifies `SteamVrStatusText` and `ShowSteamVrUninstall`. |
| `SteamVrStatusText` | `string` | Computed, tiered (#287), deepest true state wins: `"Not Installed"`, then controllers-live / driver-connected / running read off `HMaestroVRController.GlobalDriverStatus()` and `OpenVrConsumerService.ServerConnected`, falling back to `"Installed"`. |
| `SteamVrSentence` | `string` | Computed: the same state as one line in sentence case, as a VR slot's header on the controller page says it after the slot's name (#574), for example "SteamVR running, controllers live". |
| `SteamVrInstallDir` | `string` | Where the Steam-free install will land (seeded from `DriverInstaller.SteamVrInstallDir`). Not persisted by PadForge: after a successful install the HIDMaestro path hint is the durable record. |
| `IsSteamVrOwned` | `bool` | The present install is the Steam-free one PadForge created. A Steam-client install is never PadForge's to remove. |
| `ShowSteamVrUninstall` | `bool` | Computed: `IsSteamVrInstalled && IsSteamVrOwned`. |
| `SteamVrDriverConflictText` / `HasSteamVrDriverConflict` | `string` / `bool` | The warning the row shows when another OpenVR driver is registered under HIDMaestro's driver name, naming its folders one per line (`Vr_DriverNameConflict_Format`). OpenVR requires unique driver names, so SteamVR may load that driver in place of HIDMaestro's and the VR slot's controllers never appear. Empty when there is none or SteamVR is not installed. The internal static `SteamVrDriverConflictLine(folders)` builds the warning from a folder list. `RefreshSteamVrDriverConflict` re-reads at most every 10 seconds (`SteamVrConflictTtlMs`) through `HMVR.FindDriverNameConflicts()`, held in the internal test seam `SteamVrConflictProbe`. |

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `InstallSteamVrCommand` | `!IsSteamVrInstalled` | Raises `InstallSteamVrRequested`. |
| `UninstallSteamVrCommand` | `IsSteamVrInstalled && IsSteamVrOwned && !HasAnyVrSlots()` | Raises `UninstallSteamVrRequested`. |

| Event | Description |
|-------|-------------|
| `InstallSteamVrRequested` | Install SteamVR Steam-free. |
| `UninstallSteamVrRequested` | Remove the PadForge-owned install. |

| Method | Description |
|--------|-------------|
| `RefreshSteamVrStatus()` | Raises the SteamVR row's change notification and re-reads the driver-name conflict. Called by MainWindow's periodic status refresh, since `SteamVrStatusText` reads live statics rather than stored fields. |

### Driver Uninstall Guards

| Member | Type | Description |
|--------|------|-------------|
| `HasAnyMidiSlots` | `Func<bool>` | Set by MainWindow. True if any slot uses MIDI. Blocks `UninstallMidiServicesCommand` while the App SDK runtime is the API in use. |
| `HasAnyVrSlots` | `Func<bool>` | Set by MainWindow. True if any created slot is a VR slot. Blocks `UninstallSteamVrCommand`. |
| `HasAnyHidHideDevices` | `Func<bool>` | Set by MainWindow. True if any device has HidHide enabled. Blocks `UninstallHidHideCommand`. |
| `RefreshDriverGuards()` | method | Re-evaluates uninstall `CanExecute` for HidHide, MIDI Services, and SteamVR. Call after slot creation/deletion/type changes. |

### Engine Settings

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `AutoStartEngine` | `bool` | `true` | Auto-start engine on launch. |
| `MinimizeToTray` | `bool` | `false` | Minimize to system tray instead of taskbar. |
| `CloseToTray` | `bool` | `false` | Closing the window keeps PadForge running in the system tray. Has its own `ResetCloseToTrayCommand`. |
| `AlwaysShowTrayIcon` | `bool` | `false` | Keep the tray icon up while the window is open (#439), so the tray menu's Exit never needs the window closed first. |
| `BatteryNotifyEnabled` | `bool` | `true` | Low-battery notification master toggle (#293). |
| `BatteryNotifyThreshold` | `int` | `15` | Percent at or below which the edge-triggered notification fires. Clamped 5–50. |
| `BatteryNotifyVibrate` | `bool` | `false` | Also buzz the device on the low-battery edge, using the identify pulse train. |
| `BatteryNotifyRepeatMinutes` | `int` | `0` | Shows the low-battery notice again every this many minutes while the pad stays at or below the threshold and is not charging. `0` never repeats. Clamped 0-60. |
| `BatteryNotifyFull` | `bool` | `false` | Notify once when a pad's charge rises to 100%. On a pad that reports no charging state (an Xbox pad) that is the sign a charge finished. Opt-in. |
| `AssignOfferNewDevice` | `bool` | `true` | Assignment Prompts: offer a device PadForge has never seen before to the virtual controller whose page is open when it connects. |
| `AssignOfferEmptySlot` | `bool` | `true` | Assignment Prompts: offer any connecting device, new or already known, to the open virtual controller when that slot has no devices assigned. |
| `AssignOfferHome` | `bool` | `true` | Assignment Prompts: Home offers a device PadForge has just met a virtual controller of its own, once, while no virtual controller uses it (#574, `DashboardViewModel.HomeOfferGuid`). |
| `HandheldButtonsEnabled` | `bool` | `false` | Handheld PC Buttons (#343): adds the per-machine Hidden Buttons row and the System Motion row. The setter mirrors into `HandheldButtonRegistry.FeatureEnabled`, which the engine sweep reads. |
| `StartMinimized` | `bool` | `false` | Start minimized. |
| `DiagnosticsLoggingEnabled` | `bool` | `false` | Diagnostics logging (#303): mirrors the engine's in-memory event ring to `diagnostics.log` continuously. Persisted, so it survives restarts and covers auto-started sessions where a launch flag cannot. |
| `DiagnosticsFolderPath` | `string` | - | Read-only forwarder over `DiagnosticsLogControl.Folder`: where the log and snapshots land. Shown on the Diagnostics card. |
| `StartAtLogin` | `bool` | `false` | Auto-start at login. |
| `EnablePollingOnFocusLoss` | `bool` | `true` | Continue polling on focus loss. |
| `FlydigiEnhancedProtocol` | `bool` | `true` | SDL's Flydigi HIDAPI driver switch (#395), applied through `InputManager.ApplyFlydigiEnhancedProtocol`. On, SDL drives a Flydigi pad's vendor interface (M1 to M4, C, Z, LM, RM, motion). Off leaves the pad on its XInput view so Flydigi Space Station keeps access. |
| `GKeysEnabled` | `bool` | `false` | Read Logitech G-keys through the G-key SDK (#454). The setter mirrors into `LogitechGKeysRuntime.Enabled`. See [Logitech G-Keys Internals](logitech-g-keys-internals.md). |
| `GKeysStatus` | `string` | `""` | Which of seven states the G-key source is in, pushed by `InputService`. Empty while the feature is off, which collapses the line. |
| `GKeysStatusIsWarning` | `bool` | `false` | The G-keys line says something is wrong, which draws it in the warning color (#574). Running with keys arriving does not. |
| `PollingOverrideNote` | `string` | `null` | Why the global polling rate is not in charge (#365 follow-up). While the active profile carries a polling override, this names the profile and the rate it imposes, and the Settings page shows it under the rate. Null or empty collapses the note. Written by `InputService.ApplyEffectivePollingRate`, the same owner that writes the live rate, so note and loop cannot disagree. |
| `PollingRateHz` | `int` | `1000` (`InputManager.DefaultPollingRateHz`) | How many times a second the engine reads the devices and updates the virtual controllers. Clamped to 60–10000 (`MinPollingRateHz`, `MaxPollingRateHz`). The row is `Settings_PollingRate` ("Polling Rate (Unless a Profile Overrides It)"). |
| `PollingWakesPerSecond` | `int` | - | The wakes a second this PC's timer grid gives the engine, `InputManager.WakesPerSecond(InputManager.TimerGrid())`, read once at construction: the grid is the finest period Windows reports and does not change while PadForge runs. The Polling Rate tooltip (`Settings_PollingRateTooltip_Format`) names it: "On this PC, Windows wakes the engine at most {0} times a second, so a higher rate runs several passes at each wake." |
| `HmInactivityDestroyTimeoutSeconds` | `int` | `60` | Seconds the engine waits for any mapped device to return online before tearing down the live HM virtual controller and freeing its kernel slot. Clamped to 0–3600. `0` disables the timeout. The slot's configuration (mappings, profile, position, enabled state) is preserved end-to-end. Only the live VC is destroyed. Once mapped devices come back online, the VC recreates automatically at the same visual position. Surviving Xbox HM VCs at higher visual positions bubble down to keep xinputhid indices contiguous after the teardown. |
| `EnableInputHiding` | `bool` | `true` | Master switch for device hiding (HidHide + input hooks). |
| `KeepHidHideCloaksBetweenLaunches` | `bool` | `false` | When true, HidHide cloaks stay asserted after PadForge exits so other apps still see the physical devices hidden. When false (default), cloaks clear on shutdown. |

### Optional Device Sources

Each switch below is off until asked for, mirrors into a static runtime the engine sweep reads, and has a status line that `InputService` pushes and that is empty while the switch is off or the engine is stopped, which collapses the line. The per-device choices ride the settings file as lists on the view model.

| Property | Type | Description |
|----------|------|-------------|
| `AnalogKeyboardsEnabled` / `AnalogKeyboardsStatus` | `bool` / `string` | Analog keyboards over their vendor HID interface (#468). Mirrors to `AnalogKeyboardRuntime.Enabled`. See [Analog Keyboards Internals](analog-keyboards-internals.md). |
| `BlissBoxEnabled` / `BlissBoxStatus` | `bool` / `string` | Bliss-Box adapters through their API (#469). Mirrors to `BlissBoxRuntime.Enabled`. |
| `BlissBoxPorts` | `List<BlissBoxPortData>` | Each port's own choices: its Dreamcast screen, its native arrow poll. Changed on the UI thread only. |
| `DefaultProfileDreamcastPicture` | `string` | The Default profile's Dreamcast screen picture, base64 in image order, or null. See [Bliss-Box Internals](bliss-box-internals.md). |
| `KeyboardScreensEnabled` / `KeyboardScreensStatus` | `bool` / `string` | The keyboard screens (#519): Logitech GamePanel screens, Arx Control and the S.T.R.I.K.E. 7. Mirrors to `KeyboardScreensRuntime.Enabled`. Off until asked for because it loads other vendors' libraries and can bind WinUSB to a G19's screen interface. |
| `KeyboardScreensStatusIsWarning` | `bool` | The keyboard screens' lines include that no screen was found, which draws them in the warning color (#574). A library's line beside a screen that is present is information. |
| `KeyboardScreens` | `List<KeyboardScreenData>` | Each screen's choices, kept by the screen's row. |
| `DefaultProfileKeyboardScreenPicture` | `string` | The Default profile's keyboard screen picture, a stored path, or null. |
| `Strike7LibraryPath` | `string` | A `Strike7API.dll` the user picked, or null for the copy PadForge downloads. |
| `DownloadStrike7LibraryCommand`, `PickStrike7LibraryCommand`, `InstallVc2008RuntimeCommand` | `RelayCommand` | Raise `DownloadStrike7LibraryRequested`, `PickStrike7LibraryRequested`, `InstallVc2008RuntimeRequested`. The VC++ 2008 runtime is what the S.T.R.I.K.E. 7 library links. See [Keyboard Screens Internals](keyboard-screens-internals.md). |
| `NovintFalconEnabled` / `FalconStatus` | `bool` / `string` | Drive a Novint Falcon (#521). Mirrors to `FalconRuntime.Enabled`. See [Novint Falcon Internals](novint-falcon-internals.md). |
| `FalconStatusIsWarning` | `bool` | The Falcon's lines say something is wrong, which draws them in the warning color (#574): a library that did not load, a picked copy that was not used, or no Falcon open. |
| `FalconCanInstallDriver` | `bool` | A Falcon with no driver is plugged in and Force Dimension's package is at hand, so the Install button shows. |
| `FalconLibraryPath` | `string` | A `dhd64.dll` the user picked, or null. The setter resolves it through `IconPackageManager.ResolvePath` into `FalconRuntime.PickedLibrary`. |
| `PickFalconLibraryCommand`, `InstallFalconDriverCommand`, `OpenFalconDownloadCommand` | `RelayCommand` | Raise `PickFalconLibraryRequested`, `InstallFalconDriverRequested`, `OpenFalconDownloadRequested`. |
| `SerialControllers` | `ObservableCollection<SerialControllerEntry>` | Controllers on COM ports the user added in the pairing dialog (hifihedgehog/SDL#33). SDL opens each named port. `SerialControllersChanged` is raised on each add or remove (`RaiseSerialControllersChanged`, internal), never by the load, so reading the file cannot mark it dirty. |
| `WinUsbOptIns` | `ObservableCollection<string>` | IDs of the devices the user moved to PadForge's WinUSB driver from the Devices page. |
| `KeyboardTakeovers` | `ObservableCollection<KeyboardTakeoverEntry>` | The keyboards the user took from Windows for PadForge alone from the Devices page (#549), each with the row it had as a Raw Input keyboard. |

### Updates (#457)

The Settings > Updates card. `UpdateController` (`Services/UpdateController.cs`) subscribes to the three request events and to the three switches, and writes the status line, the progress and the busy state. The three switches persist as `PadForge.xml` AppSettings elements of the same names. The user-facing behavior is on [Updates](../features/updates.md), the mechanics on [Updates Internals](updates-internals.md).

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `CheckForUpdatesAutomatically` | `bool` | `true` | Check GitHub 20 seconds after launch and every 12 hours after that. |
| `InstallUpdatesAutomatically` | `bool` | `false` | Download what the automatic check finds and install it at the next launch. The card shows it only while `CheckForUpdatesAutomatically` is on. |
| `IncludePreReleaseUpdates` | `bool` | `false` | Offer the rolling dev build instead of releases. A change cancels the running operation, drops the current offer and clears the status line, then checks again when automatic checks are on. |
| `UpdateStatusText` | `string` | `""` | The card's status line, empty until a check has run. Built on every read from the function `SetUpdateStatus(Func<string> text, bool upToDate = false)` (internal) stored, which also sets `IsUpToDate`, so a language change reaches it (`OnCultureChanged` raises it). |
| `IsUpdateAvailable` | `bool` | `false` | A newer build was found. Shows Install and Restart and Release Notes, and turns the status line ember. |
| `IsUpToDate` | `bool` | `false` | The last check found this build the newest (#574). |
| `VersionNumber` | `string` | `""` | The version alone, "6.0.0", which the About page shows beside PadForge's name (#574). `ApplicationVersion` is the full build line. |
| `AboutSubLine` | `string` | - | The About page's line under PadForge's name (#574): the subtitle, then "Up to date." once a check found the newest build, or the Updates card's own sentence while a check runs, has failed or has found an update. Before any check, the subtitle alone. |
| `IsUpdateBusy` | `bool` | `false` | A check or a download is running. Disables Check Now and Install and Restart. |
| `IsUpdateDownloading` | `bool` | `false` | Shows the progress bar. |
| `UpdateProgress` | `int` | `0` | Download progress, 0 to 100. |

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `CheckForUpdatesNowCommand` | `!IsUpdateBusy` | Check Now. Raises `CheckForUpdatesNowRequested`. |
| `InstallUpdateCommand` | `IsUpdateAvailable && !IsUpdateBusy` | Install and Restart. Raises `InstallUpdateRequested`. |
| `OpenReleaseNotesCommand` | always | Release Notes. Raises `OpenReleaseNotesRequested`. |

### Settings File

| Property | Type | Description |
|----------|------|-------------|
| `SettingsFilePath` | `string` | Path to the loaded settings file. |
| `HasUnsavedChanges` | `bool` | Unsaved changes exist. |

| Command | Description |
|---------|-------------|
| `SaveCommand` | Raises `SaveRequested`. |
| `ReloadCommand` | Raises `ReloadRequested`. |
| `ResetCommand` | Raises `ResetRequested`. |
| `OpenSettingsFolderCommand` | Raises `OpenSettingsFolderRequested`. |

| Event | Description |
|-------|-------------|
| `SaveRequested` | Save settings. |
| `ReloadRequested` | Reload from disk. |
| `ResetRequested` | Reset settings. |
| `OpenSettingsFolderRequested` | Open settings folder. |

### Diagnostic Info

| Property | Type | Description |
|----------|------|-------------|
| `SdlVersion` | `string` | SDL3 version from `SDL_Linked_Version()`, the number alone (`"{major}.{minor}.{patch}"`), since its row's label already says SDL. MainWindow sets it on load. While `SdlVersionState` is `NotFound` it reads `Status_SDL3NotFound`, and while `Unknown`, `Common_Unknown`, so a language change reaches a failure. |
| `SdlVersionState` | `SdlVersionKind` | `Number`, `NotFound` or `Unknown` (`SdlVersionKind`, nested enum): what the SDL row shows. |
| `ApplicationVersion` | `string` | `BuildIdentity.Display`, which adds the commit count and short hash to a build made from a git checkout, for example `"4.5.3 (r3682@176208e)"`. Set by MainWindow on load. |
| `RuntimeVersion` | `string` | .NET runtime version (`Environment.Version`). |

### Display Preferences

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Use2DControllerView` | `bool` | `false` | Show 2D controller view instead of 3D. |

### Community Configs (v4.1, #9)

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `EnableCommunityConfigLookup` | `bool` | `false` | Master opt-in for the Steam Workshop clients. Persisted, dirty-gate allowlisted. |
| `ShowLegacyWorkshopConfigs` | `bool` | `false` | Legacy sub-toggle. Persisted, dirty-gate allowlisted. |
| `ClearWorkshopCacheCommand` | `RelayCommand` | | Raises `ClearWorkshopCacheRequested`, handled by MainWindow (empties `SteamWorkshopCache`). |
| `CheckWorkshopUpdatesCommand` | `RelayCommand` | | Raises `CheckWorkshopUpdatesRequested`, handled by MainWindow (batched provenance check). |
| `GetProfilesCommand` | `RelayCommand<string>` | | Opens Get Profiles (`GetProfilesDialog`, #574) on a tab: `"Starters"` (also for anything it does not know), `"Community"` or `"File"`. It raises `GetProfilesRequested` (`EventHandler<GetProfilesTab>`, `Starters` / `Community` / `File`). The Profiles page's button opens Starters and its drop tile opens Import a File. Always enabled: the starters ship in the box, and with the community opt-in off the Community tab opens on its cold state and offers the enable action itself. |

### Remote Link Peer Manager (#138)

The trusted-peer list and identity-protection mode live here. The Remote Link extra's page binds them through `DashboardViewModel.RemoteLink`.

| Property | Type | Description |
|----------|------|-------------|
| `TrustedPeers` | `ObservableCollection<RemoteLinkTrustedPeer>` | Trusted paired PCs, listed under Paired PCs on the Remote Link page. |
| `NearbyUnpaired` | `ObservableCollection<RemoteLinkNearbyPeer>` | PadForge PCs discovered on the LAN that aren't paired yet. |
| `HasNearbyUnpaired` | `bool` | Computed: `NearbyUnpaired.Count > 0`. |
| `IdentityProtectionModes` | `IReadOnlyList<GyroLabeledOption>` | Dropdown options in index order: 0 Secure, 1 password-portable, 2 open-portable. |
| `IdentityProtectionModeIndex` | `int` | Selected protection mode (0/1/2). User changes raise `IdentityProtectionModeChangeRequested`. Programmatic reverts use `SetIdentityProtectionModeSilently` so no event re-fires. Notifies `IdentityProtectionHint`. |
| `IdentityProtectionHint` | `string` | Computed: one-line guidance under the dropdown for the selected mode. |

| Command | Description |
|---------|-------------|
| `RevokeAllPeersCommand` | Raises `PeerRevokeAllRequested`. |

| Event | Args | Description |
|-------|------|-------------|
| `PeerRevokeRequested` | `string` | Revoke one peer by fingerprint. |
| `PeerRevokeAllRequested` | - | Revoke every peer. |
| `PeerRenameRequested` | `string, string` | Rename a peer (fingerprint, new name), persisted. |
| `PeerConnectRequested` | `string` | Connect to a paired-but-offline peer (host:port). |
| `PeerAssignmentPermissionChanged` | `string, bool` | A peer's Allow Remote Assignment Changes switch changed (fingerprint, allowed). `InputService` writes it to the trust store. |
| `PeerAssignmentsRequested` | `string` | Assign Shared Devices was clicked for a peer (fingerprint). `InputService` opens `RemoteAssignmentsDialog` over that peer's assignment channel. |
| `IdentityProtectionModeChangeRequested` | `int` | User picked a different protection mode (new index). |

| Method | Description |
|--------|-------------|
| `RefreshTrustedPeers(IEnumerable<PeerTrust>, IReadOnlyCollection<string> connectedFingerprints = null)` | Rebuilds `TrustedPeers` from the trust store. Called on pair / revoke / rename, not for online refresh. |
| `UpdatePeerOnlineStatus(IReadOnlyCollection<string>)` | Updates each peer's online dot in place from the live connection set. |
| `UpdatePeerReachability(IReadOnlyDictionary<string,string>)` | Updates each paired peer's reachable host:port in place from LAN discovery. |
| `SetNearbyUnpaired(IEnumerable<RemoteLinkNearbyPeer>)` | Replaces the nearby-unpaired list. |
| `SetIdentityProtectionModeSilently(int)` | Sets the mode without raising the change request (init from settings, or revert a canceled switch). |

### Window and Foreground State

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ForegroundExeName` | `string` | `"-"` | Foreground exe filename the auto-switch monitor last saw (#175 item 8). Runtime-only, fed at 1 Hz by InputService's UI timer, never persisted. |
| `IsForegroundMatched` | `bool` | `false` | True while the foreground exe matches a profile. Runtime-only. |
| `ShowsInFront` | `bool` | - | Computed: the Profiles page's In Front Now line shows. Switching by game is on and a program in front has been read. |
| `ForegroundProfileName` | `string` | `""` | The name of the profile the program in front loads, empty when none (#574). Runtime only, fed at 1 Hz with `ForegroundExeName`. |
| `ForegroundLead` / `ForegroundTail` | `string` | `""` | The In Front Now line around the program's name: a match comes first, then no profile with a game, then neither. Split by the internal static `SplitAroundPlace(format, name)`, which cuts a sentence at its `{0}` with `{1}` filled by `name` in both parts, so a language may put `{1}` before `{0}`. A format with no `{0}` is all lead. Private setters. |
| `NoProfileHasExecutables` | `bool` | - | Computed: no profile carries an executable match rule (#175 item 8). |
| `LegacyDriverCleanupOffered` | `bool` | `false` | True after the v3 first-run cleanup wizard has been shown. Persists so the dialog appears once. |
| `MainWindowLeft` / `Top` | `double` | `-1` | Main window position (profile-independent). |
| `MainWindowWidth` / `Height` | `double` | `1100` / `720` | Main window size. |
| `MainWindowState` | `int` | `0` | Persisted window state (normal / maximized). |
| `MainWindowFullScreen` | `bool` | `false` | Full-screen flag. |

### Profiles

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `EnableAutoProfileSwitching` | `bool` | `false` | Auto-profile switching enabled. |
| `EnableExternalControl` | `bool` | `false` | Serve the external-control named pipe (#366) so a launcher or script can activate and deactivate profiles from outside PadForge. `InputService` watches this property and starts or stops the pipe live. The Profiles page carries its switch, because this is a third way a profile activates rather than a global engine service. |
| `ProfileItems` | `ObservableCollection<ProfileListItem>` | empty | The Profiles page's cards. |
| `ProfileShortcuts` | `ObservableCollection<ProfileShortcutViewModel>` | empty | Profile-switch shortcut rows for the Profiles page's Shortcuts card. |
| `SelectedProfile` | `ProfileListItem` | `null` | The profile a card command acts on. Each card command sets it before raising its event, and MainWindow's handlers read it. |
| `ActiveProfileInfo` | `string` | `Common_Default` | Active profile display text. Null writes `Common_Default`. |

Each card's commands take the card's `ProfileListItem` as their parameter (#574). A null parameter does nothing.

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `NewProfileCommand` | always | Raises `NewProfileRequested`. |
| `LoadProfileCommand` | `p != null && !p.IsActive` | Raises `RevertToDefaultRequested` for Default, else `LoadProfileRequested`. The active profile has nothing to load. |
| `SaveAsProfileCommand` | `p.IsActive` | Raises `SaveAsProfileRequested`, from the active card's menu: the active profile is what the live setup holds. |
| `SaveSetupHereCommand` | `p != null && !p.IsDefault && !p.IsActive` | Save Current Setup Here: raises `SaveSetupHereRequested`, and the live setup replaces what the stored profile holds. Default is never overwritten. |
| `EditProfileCommand` | `p != null && !p.IsDefault` | Raises `EditProfileRequested`: the name, games and polling override. |
| `ExportProfileCommand` | `p != null` | Raises `ExportProfileRequested`. Exports the card's profile as a `.pfprofile`. The Default card exports its own stored state. |
| `DeleteProfileCommand` | `p != null && !p.IsDefault` | Raises `DeleteProfileRequested`. |
| `ResetShortcutsCommand` | always | Reset All on the Shortcuts card (#574): each shortcut's action, profile and device go back to their defaults through the row's own resets. The rows and their recorded buttons stay. |

Importing a profile goes through `GetProfilesCommand` with the `"File"` tab, or a file dropped on the Profiles page: a `.pfprofile` imports directly and a reWASD `.rewasd` or DS4Windows `.xml` goes through `ImportConfigDialog` (#561). See [Profile Import Internals](profile-import-internals.md).

| Event | Description |
|-------|-------------|
| `RevertToDefaultRequested` | Revert to default profile. |
| `NewProfileRequested` | Create new empty profile. |
| `SaveAsProfileRequested` | Save current settings as profile. |
| `SaveSetupHereRequested` | Put the current setup into the selected stored profile. |
| `DeleteProfileRequested` | Delete selected profile. |
| `EditProfileRequested` | Edit selected profile metadata. |
| `LoadProfileRequested` | Load selected profile. |
| `ExportProfileRequested` | Export selected profile to a `.pfprofile`. |
| `ProfileControllersChanged` | The profiles' cards have other controllers to show: a profile more or fewer, or other controllers in one. The one that makes the cards' pictures listens. |

---

### ProfileListItem

**File:** `SettingsViewModel.cs` (nested class)

One card on the Profiles page. `ToString()` returns `Name`, the entry's screen-reader name.

| Property | Type | Description |
|----------|------|-------------|
| `Id` | `string` | Profile identifier. Notifies `IsDefault`, `CanEdit` and `ShowsSaveHere`. |
| `IsActive` | `bool` | Whether this profile is the active one. The card shows Active in place of Load. Notifies `ShowsLoad`, `ShowsSaveAs` and `ShowsSaveHere`. |
| `CanEdit` | `bool` | Computed: `!IsDefault`. The card's menu offers Edit and Delete. Default has no name or games of its own and is never deleted. |
| `ShowsLoad` / `ShowsSaveAs` / `ShowsSaveHere` | `bool` | Computed: Load on every card but the active one, Save As on the active card's menu, Save Current Setup Here on every card but Default's and the active one's. |
| `Name` | `string` | Display name. |
| `Executables` | `string` | Comma-separated exe names for auto-switch (display form). Notifies `HasExecutables`. |
| `ExecutablePaths` | `string` | Pipe-separated full executable paths (the ForegroundMonitorService match source). Rebuilds the game line. |
| `HasExecutables` | `bool` | Computed: the profile carries any executable match rule. |
| `SwitchesByGame` | `bool` | Set by the owner from Switch Profiles by Game. The card says Loads For while it is on and Set For while it is off (`Profiles_Card_LoadsFor_Format`, `Profiles_Card_SetFor_Format`), since the game then loads nothing by itself. |
| `GameNames` / `GameExtra` | `string` | The first two games' file names (`"a.exe, b.exe"`), and `"+N"` for the games past two, in a cell of its own so a long name never cuts it off. |
| `GameLead` / `GameTail` | `string` | What the Loads For or Set For sentence puts before and after the names (`SettingsViewModel.SplitAroundPlace`). |
| `Controllers` | `IReadOnlyList<ProfileController>` | The profile's controllers in slot order. The card shows a picture of each. |
| `HasNoSlots` | `bool` | Computed: `Controllers.Count == 0`. |
| `IsDefault` | `bool` | Computed: true if `Id == "__default__"`. |

Internal methods: `SetTopology(slotCreated, slotControllerTypes, slotProfileIds, slotModel3DAppearances)` takes the profile's slots (which exist, each one's type, its preset and the finishes chosen for its picture) and rebuilds `Controllers` only when one of them changed. `RaiseCultureDependentText()` re-raises the game line's words and the controllers' type names after a language switch.

| Constant | Value | Description |
|----------|-------|-------------|
| `DefaultProfileId` | `"__default__"` | Sentinel ID for the Default profile. |

### ProfileController

**File:** `SettingsViewModel.cs`

One controller on a profile's card. Built by the internal static `ProfileController.Build(...)` from the profile's slots, numbered per type in slot order.

| Property | Type | Description |
|----------|------|-------------|
| `Slot` | `int` | The slot index. |
| `Type` | `VirtualControllerType` | The slot's type. An undefined stored value reads as Xbox. |
| `TypeGeometry` / `TypeGlyph` / `TypeName` | `Geometry` / `string` / `string` | From `SlotTypeIconMap`. |
| `Number` | `string` | `"#"` and the type's own count, `"#2"`. |
| `SpokenName` | `string` | `TypeName` and `Number`, which `ToString()` returns for a screen reader. |
| `Picture` / `HasPicture` | `ImageSource` / `bool` | The controller's picture, and whether it has one or one is being made. Set by the internal `SetPicture(picture, coming)`, from the internal `PresetId`, `Finishes` and `FinishOf(family)`. |

---

## DevicesViewModel

**Files:** `DevicesViewModel.cs`, `DevicesViewModel.List.cs`, `DevicesViewModel.Board.cs`, `DevicesViewModel.Test.cs`, `DevicesViewModel.SettingResets.cs`
**DataContext for:** the Devices page (`Views/DevicesPage.xaml`)

All detected input devices (online and offline), the page's lists, and the selected device's panel: its picture, its Details, Settings and Test Inputs cards, and its raw input state.

### Device List

| Property | Type | Description |
|----------|------|-------------|
| `Devices` | `ObservableCollection<DeviceRowViewModel>` | All known devices. Updated by InputService on change. |
| `SelectedDevice` | `DeviceRowViewModel` | Selected device. Notifies `HasSelectedDevice`, refreshes slot buttons, the driver offer and command state. |
| `HasSelectedDevice` | `bool` | Computed: `SelectedDevice != null`. |

### The Page's Lists (#574)

**File:** `DevicesViewModel.List.cs`

The main list shows the devices connected now, or under the Not Connected segment the ones PadForge remembers and cannot see, in parts by kind. The Not Connected fold holds those under the other two segments. Each list passes the Show segment, the connection segment and the search. Every row stands in the part of its kind, the rows PadForge and the extras feed included. Four enums carry the shape: `DeviceListGroup` (`Connected`, `NotConnected`), `DeviceFilter` (`All`, `Gamepad`, `Joystick`, `Wheel`, `Keyboard`, `Mouse`, `Other`, the Show segments and the main list's parts in that order), `DeviceConnection` (`All`, `Connected`, `NotConnected`) and `DevicePageList` (`Main`, `NotConnected`).

| Member | Type | Description |
|--------|------|-------------|
| `Filter` | `DeviceFilter` | The Show segment: which kinds of device the lists show. Default `All`. |
| `Connection` | `DeviceConnection` | The connection segment: every device, the connected ones, or the ones that are not. |
| `MainGroup` | `DeviceListGroup` (internal) | The rows the main list holds: the connected ones, or under the Not Connected segment the ones that are not. |
| `SearchText` | `string` | What the search box holds. It finds a device by its name, its product's name, its type in the language and its VID:PID, ignoring case in the current culture. |
| `MainView` / `NotConnectedView` | `ICollectionView` | The main list's view of `Devices`, in parts by kind, and the Not Connected list's view. `EnsureListViews()` (internal) makes them on the UI thread from the page's `OnDataContextChanged`, since a `ListCollectionView` belongs to the thread that makes it. |
| `Shows(list, row)` / `RowsOf(list, inParts)` / `Matches(row)` | internal methods | Whether a list shows a row, the rows a list shows in order (each part's rows together, the parts in the Show segments' order, through `SectionOrder`), and whether a row passes the segments and the search. |
| `Parts` / `FilterOf(typeKey)` | internal static | The connected list's parts (every segment but All), and the segment a type falls in: gamepads are the gamepad-shaped classes, joysticks take flight sticks with them, a wheel, a keyboard and a mouse each have their own, and every other type is Other. |
| `ConnectedTotal` | `int` | The devices connected now, whatever the segments and the search, the "N connected" under the page's title. It counts rows whose `DeviceRowViewModel.CountsAsDevice` is true, so a merged row, a keyboard's media keys and the rows PadForge feeds stand in the list and are not counted. The rule is the static `IsCountedDevice(devicePath, deviceTypeKey)`, which Home's `OnlineDevices` counts by too. |
| `NotConnectedCount` / `HasNotConnected` / `NotConnectedHint` | `int` / `bool` / `string` | The Not Connected line's count, whether it shows (it has a row to open), and its hint, the names it holds. |
| `ShowNoMatch` | `bool` | The list says no device matches: a segment or the search leaves no row in either list. |
| `CanAddController` | `bool` | A controller can be made for a device (Use It, New Controller): a slot is free. Set by `RefreshSlotButtons`. |
| `RefreshCounts()` | method | Recomputes `ConnectedTotal`, `NotConnectedCount`, `NotConnectedHint` and `ShowNoMatch` (only while a segment or the search narrows the lists), then `RefreshColumns()` and the views. |

### The Selected Device's Board

**Files:** `DevicesViewModel.Board.cs`, `DevicesViewModel.SettingResets.cs`, `DevicesViewModel.Test.cs`

| Member | Type | Description |
|--------|------|-------------|
| `ShowLinkColumn` / `ShowBatteryColumn` | `bool` | Whether any row the lists show names its link, or reports a battery. The table's head drops a column no row fills. `RefreshColumns()` reads them again with the counts and after the battery walk. |
| `SelectedPicture` / `SelectedPictureGray` | `ImageSource` | The selected device's picture at the head of its panel, in its own colors where PadForge has that controller's art, and the same in gray for a device that is not connected. |
| `HasSelectedPicture` / `ShowSelectedKind` | `bool` | Computed: the panel has a picture, and the stage shows the device's kind (no picture and none on its way). |
| `PictureIsFor(...)` / `SetPicture(...)` / `ForgetPicture()` | internal methods | The picture and what it was made for (device, VID, PID, a still of the 3D model or the 2D art), so it is made again only when one changed. |
| `ShowDeviceTools` | `bool` | The Settings card shows the device's tools: a driver switch, or a button its kind offers (the iCade and USIO readings, NFC tags, voice and chat words, hidden buttons, key lights, a Bliss-Box port's actions, a keyboard's screen, the Flydigi screen, the Falcon's reach). |
| `ShowSettingsCard` | `bool` | The Settings card shows at all: the device has a setting of its own or a tool. |
| `SettingsCardResets(row)` / `HasResettableSettings` | internal static / `bool` | The settings the Settings card shows for a device, in the card's order, which its Reset All puts back (Force Raw Joystick Mode is the Details card's and stays), and whether there is one. |
| `ResetSettingsCardCommand` | `RelayCommand` | The Settings card's Reset All: each of the card's settings back to its default through its own reset, and one notification for them all. |
| `ShowTestCard` | `bool` | The Test Inputs card shows: `HasRawData` and the row's `ShowRawInputState`. |
| `ShowGamepadTest` | `bool` | The card shows the compact test: the selected device's state is in the gamepad layout. |
| `TestLeftX` / `TestLeftY` / `TestRightX` / `TestRightY` | `double` | The sticks, 0 to 1, 0.5 at rest, Y down the page. Private setters. |
| `TestLeftTrigger` / `TestRightTrigger` | `double` | The triggers, 0 to 1. |
| `TestPressed` / `TestPressedNames` / `NothingPressed` | `string[]` / `string` / `bool` | The held buttons' names, one per chip on the Pressed line, the same joined with commas or the word None, and whether none is held. |
| `TestPressedLead` / `TestPressedTail` | `string` | What the Pressed line's format holds before and after its `{0}`. |
| `UpdateGamepadTest(state)` | internal method | Reads the gamepad layout's slots (`SdlDeviceWrapper.GetGamepadState`): axis 0 the left stick across and 1 down, 2 the left trigger, 3 and 4 the right stick, 5 the right trigger, each 0 to 65535, and buttons 0 to 21 named by `GamepadObjectNames.Button`. |

### Raw Input State Display (for selected device)

| Property | Type | Description |
|----------|------|-------------|
| `RawAxes` | `ObservableCollection<AxisDisplayItem>` | Axis values (progress bars). |
| `RawButtons` | `ObservableCollection<ButtonDisplayItem>` | Button states (circles). |
| `RawPovs` | `ObservableCollection<PovDisplayItem>` | POV hat values (compass). |
| `KeyboardKeys` | `ObservableCollection<KeyboardKeyItem>` | Keyboard layout items. |
| `IsKeyboardDevice` | `bool` | Selected device is a keyboard. |
| `IsMouseDevice` | `bool` | Selected device is a mouse. |
| `IsTouchpadDevice` | `bool` | Selected device is itself a touchpad (`CapType` Touchpad) or a drawing tablet. |
| `IsMidiDevice` | `bool` | Selected device is a MIDI input (#128). Drives the live piano / CC preview off `LiveMidi`. |
| `IsNfcDevice` | `bool` | Selected device is an NFC reader (#150). Populates `NfcTags`. |
| `IsMicrophoneDevice` | `bool` | Selected device is a standalone microphone (#317). Hides the numbered button grid, since every button it has is a named phrase. |
| `ShowVoicePhrases` | `bool` | Selected device carries voice phrases (a microphone row, or a Bluetooth DualSense whose embedded mic is not a system device). Drives the Voice Macros section, the voice twin of the NFC Tags section. |
| `VoicePhrases` | `ObservableCollection<NfcTagDisplayItem>` | Named phrase rows for the live preview (#317): "Any Phrase" plus each registered phrase. Reuses the NFC row item. Rebuilt by `RebuildVoicePhrases(int)`. |
| `VoiceButtonBase` | `int` | Raw-button base the current device's phrase buttons sit at (0 on a microphone row, the reserved pad range on a DualSense). `-1` when none. Private setter. |
| `IsConsumerDevice` | `bool` | Selected device is a Consumer Control collection (#168). Populates `ConsumerButtons`. |
| `IsHeadsetMotionDevice` | `bool` | Selected device is a Sony headset head tracker (#188). Collapses the raw Axes / Buttons sections, since a motion-only source has neither and the gyro readout is its whole preview. |
| `IsHandheldDevice` | `bool` | Selected device is the handheld hidden-buttons row (#343). Drives the named button list in place of the numbered grid, the same treatment NFC gets. |
| `IsSystemMotionDevice` | `bool` | Selected device is the machine's own motion sensor row (#343). Motion only, so the raw Axes / Buttons sections collapse like the headset tracker's. |
| `IsHeadTrackerDevice` | `bool` | Selected device is the head tracker row (#355): six named axes, no buttons, plus a source line. |
| `HeadTrackerStatus` | `string` | Which head-tracking source is live, for the details pane (#355). Written by `InputService.UpdateDevicePanelLines`, which runs on the Devices page tick, on a selection change while the engine is off, and once after an engine stop, so a retired device's line clears. Null coalesces to empty. |
| `HeadTrackerStatusVersion` | `int` | Internal. The device `StatusVersion` the current `HeadTrackerStatus` was built from, `-1` for none. |
| `HeadTrackerStatusDevice` | `object` | Internal. The device instance that version belongs to. A reopen (port change, FreeTrack toggle) builds a new device whose `StatusVersion` restarts at 0 and collides with the cached 0, so the cache compares instance as well as version. |
| `IsGameTelemetryDevice` | `bool` | Selected device is the Game Telemetry row (#531): named axes, the Driving, Reverse and Neutral buttons, a button per gear, plus the listener's line. |
| `GameTelemetryStatus` | `string` | What the listener hears, for the details pane (#531), the same line as the Game Telemetry page's. Written by `InputService.UpdateDevicePanelLines` like `HeadTrackerStatus`. Null coalesces to empty. |
| `GameTelemetryStatusVersion` / `GameTelemetryStatusDevice` | `int` / `object` | Internal. The cache pair, the head tracker's shape: the row's `StatusVersion` and the row instance it belongs to. |
| `HandheldButtons` | `ObservableCollection<NfcTagDisplayItem>` | Named button chips, each lighting while its button is down. Reuses the NFC row item. For the handheld row (#343) `RebuildHandheldButtons()` fills it from the registry, with `Uid` carrying the delivery description. For a VR controller or Logitech G-Keys row `RebuildNamedButtons(IReadOnlyList<DeviceObjectItem>)` fills it from the device's own button objects. |
| `ShowNamedButtons` | `bool` | The preview shows the named chips instead of the numbered grid: the handheld, VR controller, and Logitech G-Keys rows. |
| `NfcTags` | `ObservableCollection<NfcTagDisplayItem>` | Registered-tag rows for the NFC preview. Rebuilt by `RebuildNfcTags()`. |
| `ConsumerButtons` | `ObservableCollection<ConsumerButtonDisplayItem>` | Named media-key chips for the Consumer Control preview. |
| `LiveMidi` | `MidiInputState` | Latest MIDI input snapshot the piano / CC preview polls. Plain property, no change notification. |
| `HasTouchpadData` | `bool` | The selected device has a touchpad to preview (`UserDevice.HasTouchpad`, or the device is itself a touchpad or tablet). Set when the selection changes. |
| `IsAnalogKeyboardDevice` / `HasAnalogKeys` | `bool` | The selected device is an analog keyboard (#468), which previews key depths in place of axes and buttons, and a key on it has moved, which swaps the "press a key" hint for the key chips. |
| `AnalogKeys` | `ObservableCollection<AnalogKeyDisplayItem>` | One chip per key the selected analog keyboard has reported since it was selected, in keyboard order, each with its live depth. `UpdateAnalogKeys(keys)` (internal) folds one poll's depths in, and `SetAnalogKeyOrder(order)` (internal) moves the chips to a new key order. |
| `HasBlissBoxPressure` / `BlissBoxPressure` | `bool` / `ObservableCollection<AnalogKeyDisplayItem>` | A DualShock 2 is in the selected Bliss-Box port, so its twelve pressures show as chips (#469). `UpdateBlissBoxPressure(pressure)` (internal) folds report 21's twelve bytes in, or clears them, and the static `PressureButton(name)` turns "Triangle Pressure" into "Triangle". |
| `IsFalconDevice` / `FalconDotX` / `FalconDotY` | `bool` / `double` / `double` | The selected device is a Novint Falcon (#521): its handle draws as a dot in a square above the named axes, across and down, 0 to 1, up at 0. `FalconAxisName(slot)` (internal static) gives an axis's name as its mapping picker shows it. |
| `NamedAxis(objects, slot)` | internal static | An axis's name from a row's own objects, or null. |
| `TouchpadX0`–`TouchpadX4` / `TouchpadY0`–`TouchpadY4` | `double` | Per-finger normalized position (0.0–1.0) on the first pad. Five contacts, not two. |
| `TouchpadDown0`–`TouchpadDown4` | `bool` | Per-finger contact state. |
| `HasSecondTouchpadData` | `bool` | The device exposes a second pad (Steam Controller / Steam Deck). Switches the labels to `TouchpadLabel` / `Touchpad2Label`. |
| `TouchpadLabel` / `Touchpad2Label` | `string` | Computed pad captions. `Touchpad2Label` is always the localized touchpad word plus `" 2"`. `TouchpadLabel` picks up its own `" 1"` only when a second pad exists. |
| `Pad2X0`–`Pad2X4` / `Pad2Y0`–`Pad2Y4` / `Pad2Down0`–`Pad2Down4` | `double` / `bool` | Second-pad contacts, same five-finger shape. |
| `MouseMotionX` | `double` | Mouse X motion. |
| `MouseMotionY` | `double` | Mouse Y motion. |
| `MouseScrollIntensity` | `double` | Normalized scroll intensity (−1 to 1). |
| `SelectedButtonTotal` | `int` | Button count on selected device. |
| `HasRawData` | `bool` | Raw state data available. |

### Gyroscope / Accelerometer

| Property | Type | Description |
|----------|------|-------------|
| `HasGyroData` | `bool` | Gyroscope data available. |
| `HasAccelData` | `bool` | Accelerometer data available. |
| `GyroX` | `double` | Gyroscope X value. |
| `GyroY` | `double` | Gyroscope Y value. |
| `GyroZ` | `double` | Gyroscope Z value. |
| `AccelX` | `double` | Accelerometer X value. |
| `AccelY` | `double` | Accelerometer Y value. |
| `AccelZ` | `double` | Accelerometer Z value. |
| `HasAccelAuxData` | `bool` | Aux (left-side) accelerometer data available (#199). True for a Nunchuk behind a MotionPlus or a left Joy-Con, where the device carries a second accelerometer alongside the primary one. |
| `AccelAuxX` | `double` | Aux accelerometer X value. |
| `AccelAuxY` | `double` | Aux accelerometer Y value. |
| `AccelAuxZ` | `double` | Aux accelerometer Z value. |
| `HasGyroAuxData` | `bool` | Aux (left-side) gyro data available (#252): the left Joy-Con of a combined pair. Paired with the aux accel readout so the user can see which half a reading comes from before binding it. Cleared by `ClearRawState()`. |
| `GyroAuxX` | `double` | Aux gyro X value. |
| `GyroAuxY` | `double` | Aux gyro Y value. |
| `GyroAuxZ` | `double` | Aux gyro Z value. |

### Driver Switch (hifihedgehog/SDL#33 Part 15, #549)

`RefreshDriverOffer()` works out what the selected row offers, and `NotifyDriverOffer()` raises the button flags. The offer is one of three shapes:

| Selected row | Offer |
|--------------|-------|
| A precision touchpad's own row, or a mouse row whose collection has a touchpad beside it (`TouchpadOfCollection`, default `TouchpadNodes.TouchpadOf`) | A `TouchpadOffer(TouchpadRow, Name, Taken)`: **Use Only in PadForge**, with a give-back when taken (`Devices_TouchpadGiveBack`). No driver changes: HidHide hides the touchpad's collection and PadForge reads it (`InputService.Touchpads.cs`). A touchpad's mouse row never gets a WinUSB bind, which would take the whole touchpad from Windows' touchpad driver. |
| A row `VendorUsbDriverInstaller.IsOptInRow` lists by VID and PID | `VendorUsbDriverInstaller.QueryOptIn`. A device listed by its IDs keeps its own offer. |
| Any other real keyboard or mouse row (#549) | `WinUsbKeyboardBinding.QueryOffer(devicePath, nodes, kind)`, else `WinUsbKeyboardBinding.RestoreOffer` from the row's `KeyboardTakeovers` entry, for a taken device whose WinUSB row never opened. |

| Member | Description |
|--------|-------------|
| `DriverOffer` | Internal. The `OptInOffer` (`Kind`, `Bind`, `Restore`). |
| `Hides(kind)` | Internal static. True for the Keyboard and Mouse kinds, whose switch hides the device from Windows, so their buttons stand in the Input Hiding section. |
| `ShowDriverBind` / `ShowDriverRestore` | The buttons with the device's other buttons: an offer exists, no switch is running (`DriverBusy`), and the kind does not hide. |
| `ShowHidingDriverBind` / `ShowHidingDriverRestore` | The same two buttons in the Input Hiding section, for a kind that hides and for a touchpad's switch. |
| `DriverBindText` | The bind button's text by kind (`Devices_DriverBind_Xbox360Pad`, `_Xbox360Receiver`, `_IntelBaseStation`, `_Prodikeys`, `_TouchSenseMouse`). A keyboard, a mouse and a touchpad all read **Use Only in PadForge** (`Devices_DriverBind_OnlyInPadForge`). |
| `DriverRestoreText` | `Devices_TouchpadGiveBack` for a touchpad, else `Devices_DriverRestore`. |
| `DriverBusy` | True while a switch runs, which hides every button. |
| `DriverBindRequested` / `DriverRestoreRequested`, `RequestDriverBind()` / `RequestDriverRestore()` | Raised by the page's buttons. `MainWindow` states the cost, runs the switch and persists it. |
| `TouchpadSwitch` | Internal. The `TouchpadOffer` the selected row offers, or null. |
| `ApplyDriverOffer(offer)` | Internal, for a test. |

A keyboard taken from Windows keeps its row and its ID: its path changes to its WinUSB interface once PadForge opens it, and back after a restore. `OnSelectedDevicePropertyChanged` watches the selected row's `DevicePath` and calls `RefreshDriverOffer()`, so the restore shows on the row that was just switched. Changing the selection clears the previous row's `ShowsHidingDriverSwitch` and `IsTouchpadMouse`. `NotifyDriverOffer()` sets the selected row's `ShowsHidingDriverSwitch` and calls its `NotifyTakeoverChanged()`.

### Key Lights Link (#557)

The constructor subscribes `OnKeyLightsChanged` to `PeripheralLightMaps.Changed` and `PeripheralOutputs.LinksChanged`, both raised on a backend's or the link pass's thread. The handler dispatches `SelectedDevice?.RefreshKeyLights()` to the UI thread, so a device's lights becoming known shows its **Map Key Lights** button (`DeviceRowViewModel.ShowMapKeyLights`). The page lives as long as the app, so the subscription is never removed.

### Twitch Chat row (#555)

| Property | Type | Description |
|----------|------|-------------|
| `IsTwitchChatDevice` | `bool` | The selected device is the Twitch Chat row: the command words as named chips, plus the chat's line. Set by `RebuildRawStateCollections(..., isTwitchChat: true)` and cleared by `ClearRawState()`. |
| `TwitchChatStatus` | `string` | The channel the row reads, or why it reads nothing, the Twitch Chat page's line. Written by `InputService`'s panel lines, which clear it once a stopped engine retires the row. Null writes empty. |
| `TwitchChatStatusVersion` / `TwitchChatStatusDevice` | `int` / `object` | Internal. The row's status version and instance the current `TwitchChatStatus` was built from, the Game Telemetry row's cache pair. |

### Dynamic Slot Assignment Buttons

| Property | Type | Description |
|----------|------|-------------|
| `ActiveSlotItems` | `ObservableCollection<SlotButtonItem>` | Slot toggle chips. Only includes created slots, in each group's order (`VirtualControllerGroups.InOrder`). |

### Device Action Requests

Each of these raises an event that `MainWindow` handles, from a button on the selected device's Settings card.

| Method | Event | Description |
|--------|-------|-------------|
| `RequestICadeMode(bool asPad)` | `ICadeModeRequested` (`EventHandler<bool>`) | Read as iCade Controller (true) or Read as Keyboard (false). MainWindow keeps the list and writes the hint (hifihedgehog/SDL#33 Part 16). |
| `RequestUsioLayout(string)` | `UsioLayoutRequested` (`EventHandler<string>`) | A Namco USIO row's layout, `"tekken"` or `"taiko"`. MainWindow keeps the choice and has the board opened again in it (hifihedgehog/SDL#33 Part 14). |
| `RequestBlissBox(BlissBoxAction)` | `BlissBoxActionRequested` | A Bliss-Box port row's actions (#469): `DreamcastScreen`, `PakBackup`, `PakRestore`, `NativeArrows`. MainWindow owns the dialogs and the transfers. |
| `RequestKeyboardScreen()` | `KeyboardScreenRequested` | A keyboard screen row's button (#519). MainWindow opens that screen's dialog. |
| `RequestFlydigiScreen()` | `FlydigiScreenRequested` | A Flydigi Apex pad's screen dialog (#586). |
| `RequestFalconCalibrate()` | `FalconCalibrateRequested` | A Falcon row's Calibrate Reach (#521). MainWindow runs the sweep and keeps the result on the device. |

### Commands

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `RefreshCommand` | always | Raises `RefreshRequested`. Force-refreshes device list. |
| `PairCommand` | always | Raises `PairRequested`. Opens the Bluetooth pairing flow for controllers that need an in-app pairing ceremony (Wii controllers, #116). |
| `ToggleSlotCommand` | `HasSelectedDevice` | `RelayCommand<int>`. Raises `ToggleSlotRequested` with the slot index, then `RefreshSlotButtons()`. |
| `RemoveDeviceCommand` | `HasSelectedDevice` | Runs `RemoveDevice(SelectedDevice)`. |
| `RemoveDevice(DeviceRowViewModel)` | method | Removes one device's row, record and settings: the selected device's from the Details card, or any row's from the X at the row's end. Removes the row from `Devices`, clears `SelectedDevice` only when it was the device removed, raises `RemoveDeviceRequested`, then `RefreshCounts()`. |
| `ClearModEffects()` | method | Ends what DSX game mods hold on every virtual controller the selected device feeds (`GameModEffects.ClearDevice`, #529) and clears its `GameModLine`. Called by **Clear Mod Effects** on the panel. |
| `ResetSelectedDeviceSettingCommand` | `HasSelectedDevice` and a name `DeviceRowViewModel.CanResetSetting` accepts | `RelayCommand<string>` (`DevicesViewModel.SettingResets.cs`). Runs the selected row's `ResetSettingCommand` for the named option, then clears `LastRawStateDeviceGuid` and raises `DeviceHidingChanged` so the option persists. Skips `HidHideEnabled` while HidHide is unavailable. |

### Events

| Event | Args | Description |
|-------|------|-------------|
| `RefreshRequested` | `EventArgs` | Refresh requested. |
| `PairRequested` | `EventArgs` | User opened the Bluetooth pairing flow (#116). |
| `ToggleSlotRequested` | `int` | Slot index. |
| `RemoveDeviceRequested` | `Guid` | Instance GUID. |
| `DeviceHidingChanged` | `Guid` | HidHide or ConsumeInput toggle changed. |

### Key Methods

| Method | Description |
|--------|-------------|
| `RebuildRawStateCollections(IReadOnlyList<int> axisIndices, IReadOnlyList<int> buttonIndices, int povCount, bool isKeyboard, bool isMouse, bool isTouchpad, bool isMidi, bool isNfc, IReadOnlyList<ConsumerButtonDisplayItem> consumerButtons, bool isHeadsetMotion, int voiceButtonBase, bool isMicrophone, bool isHandheld, bool isSystemMotion, bool isHeadTracker, IReadOnlyList<DeviceObjectItem> namedObjects, int[] analogKeyOrder, bool isFalcon, bool isGameTelemetry, bool isTwitchChat, bool gamepadLayout)` | Internal. Rebuilds axis/button/POV collections for a new device, and sets up the Test Inputs card's compact test when `gamepadLayout` says the device's state is in SDL's gamepad layout (#574). `axisIndices` is the sparse list of axis slots the device actually exposes (from `SupportedAxisIndices` / `CapAxisIndices` through `InputService.ResolveAxisIndices`), so each `AxisDisplayItem.Index` is the real `state.Axis[]` slot and its label reads `Axis {slot}`, gaps included. `buttonIndices` is the sparse list of button positions the device actually exposes (each item's value is stored verbatim as both `Index` and `DisplayNumber`). `namedObjects`, passed for VR controller and Logitech G-Keys rows, fills the named chips in place of the numbered grid. The class-flag booleans default to `false`, `consumerButtons` and `namedObjects` to `null`, and `voiceButtonBase` to `-1`. `analogKeyOrder` (non-null for an analog keyboard, #468) gathers key chips as keys move. Handles keyboard, mouse, touchpad, MIDI, NFC, Consumer Control, headset-motion, handheld, system-motion, head-tracker, named-button, voice-phrase, analog-keyboard, Falcon, Game Telemetry and Twitch Chat cases. |
| `ClearRawState()` | Internal. Clears all raw state display data, including every class flag, `ShowGamepadTest`, the head-tracker status cache, and the NFC / voice / handheld / Consumer collections. `ShowNamedButtons` keeps its value until the next rebuild. |
| `RebuildNfcTags()` | Repopulates `NfcTags` from `NfcTagRegistry`: "Any NFC Tag" first at button 0, then each registered tag at its stable button index. |
| `RebuildHandheldButtons()` | Repopulates `HandheldButtons` from `HandheldButtonRegistry.Entries` (#343). Called on selection and whenever the registry changes. |
| `RebuildNamedButtons(IReadOnlyList<DeviceObjectItem>)` | Repopulates `HandheldButtons` from a device's own button objects, one chip per button with the name the device publishes. |
| `RebuildVoicePhrases(int)` | Repopulates `VoicePhrases` from `VoicePhraseRegistry` at the passed button base. A negative base clears the list. |
| `RefreshSlotButtons()` | Rebuilds `ActiveSlotItems` from created slots and selected device assignments. |
| `RefreshAllSlotBadges()` | Re-derives every row's `SlotBadges` after a slot set changes. |
| `FindByGuid(Guid)` | Finds a `DeviceRowViewModel` by instance GUID. |

| `NotifyDeviceHidingChanged(Guid)` | Raises `DeviceHidingChanged`. |

### Internal State

| Member | Type | Description |
|--------|------|-------------|
| `LastRawStateDeviceGuid` | `Guid` | Tracks which device's collections are populated. Prevents unnecessary rebuilds. |
| `HeadTrackerAxisName(int slot)` | `static string` | Localized name of a head-tracker axis slot (#355): Yaw, Pitch, Roll, X, Y, Z for slots 0–5. Null past the six. |

---

### SlotButtonItem

**File:** `DevicesViewModel.cs`

Single slot toggle chip for the selected device on the Devices page.

| Property | Type | Description |
|----------|------|-------------|
| `PadIndex` | `int` | Zero-based slot index (0–15). |
| `SlotNumber` | `int` | 1-based number among active slots. |
| `TypeNumber` | `int` | The slot's number within its type, the sidebar's "#1". |
| `Label` | `string` | Computed: the type's name in the language and the number within the type, "Xbox #1". `RaiseLabel()` re-raises it after a language change. |
| `IsAssigned` | `bool` | Selected device is assigned to this slot. |
| `VcType` | `VirtualControllerType` | The slot's output type. Notifies the two icon properties below. |
| `TypeGeometry` | `Geometry` | Branded type icon path from `SlotTypeIconMap.GeometryFor`. Null for the glyph-drawn types. |
| `TypeGlyph` | `string` | Segoe glyph from `SlotTypeIconMap.GlyphFor` for the types with no path geometry (MIDI `E8D6`, Keyboard+Mouse `E961`, VR `F119`). |

### AxisDisplayItem

**File:** `DevicesViewModel.cs`

Display item for a single axis value.

| Property | Type | Description |
|----------|------|-------------|
| `Index` | `int` | The real `state.Axis[]` slot (sparse, gaps preserved). |
| `Name` | `string` | Display name from that slot (e.g., `"Axis 0"`). |
| `NormalizedValue` | `double` | Value normalized to 0.0–1.0. Bound to ProgressBar. |
| `RawValue` | `int` | Raw value (0–65535). |

### ButtonDisplayItem

**File:** `DevicesViewModel.cs`

Display item for a single button state.

| Property | Type | Description |
|----------|------|-------------|
| `Index` | `int` | Raw button slot (sparse, e.g. 16 for touchpad-click). |
| `DisplayNumber` | `int` | The number shown to the user. Equals `Index`, so the preview agrees with the mapping picker's `Button N` names, gaps included. The XAML binds `DisplayNumber`. |
| `IsPressed` | `bool` | Currently pressed. Bound to circle fill color. |

### ConsumerButtonDisplayItem

**File:** `DevicesViewModel.cs`

One named chip in the Consumer Control live preview (#168): a canonical media key that lights while held.

| Property | Type | Description |
|----------|------|-------------|
| `Index` | `int` | Slot into `state.Buttons[]` (the persistence-stable `ConsumerUsageTable` index). |
| `Name` | `string` | Localized button name. |
| `IsPressed` | `bool` | Currently held. Bound to chip background. |

### NfcTagDisplayItem

**File:** `DevicesViewModel.cs`

One row in the NFC reader's live tag preview (#150): a registered tag (or "Any NFC Tag") that lights while its button pulses.

| Property | Type | Description |
|----------|------|-------------|
| `Name` | `string` | Tag display name. |
| `Uid` | `string` | Tag UID (empty for "Any NFC Tag"). |
| `Button` | `int` | Stable raw-button index (0 = Any NFC Tag). |
| `LastActiveTick` | `long` | `TickCount64` of the last tap. Held past the ~175 ms button pulse so the row does not flicker. |
| `IsActive` | `bool` | Lit while recently tapped. Bound to row background. |

### KeyboardKeyItem

**File:** `DevicesViewModel.cs`

Display item for a keyboard key with position data. Rendered in a Canvas inside a Viewbox for auto-scaling.

| Property | Type | Description |
|----------|------|-------------|
| `VKeyIndex` | `int` | Windows Virtual Key code. |
| `Label` | `string` | Key label. |
| `X` | `double` | Canvas X position (px). |
| `Y` | `double` | Canvas Y position (px). |
| `KeyWidth` | `double` | Key width (px). |
| `KeyHeight` | `double` | Key height (px). |
| `IsPressed` | `bool` | Currently pressed. |

| Static Method | Description |
|---------------|-------------|
| `BuildLayout()` | Builds full ANSI QWERTY layout with numpad. Each key mapped to its VK code. |
| `IsVKeyPressed(bool[], int)` | Checks if a VKey is pressed in a button array. |

### PovDisplayItem

**File:** `DevicesViewModel.cs`

Display item for a single POV hat switch.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Index` | `int` | - | POV hat index. |
| `Centidegrees` | `int` | `-1` | Value in centidegrees (0–35900), or −1 for centered. Notifies `IsCentered` and `AngleDegrees`. |
| `IsCentered` | `bool` | - | Computed: `Centidegrees < 0`. |
| `AngleDegrees` | `double` | - | Computed: direction in degrees (0–359) for RotateTransform. |

### AnalogKeyDisplayItem

**File:** `DevicesViewModel.cs`

One chip of an analog keyboard's key depths (#468), or of a DualShock 2's pressures behind a Bliss-Box (#469).

| Property | Type | Description |
|----------|------|-------------|
| `Code` | `int` | The key's code. |
| `Rank` | `int` | Position in the keyboard's key order, for insertion. |
| `Depth` | `double` | 0 at rest, 1 at the bottom of the press. Notifies `IsPressed` and `DepthText`. |
| `IsPressed` | `bool` | Computed: `Depth > 0`. Lights the chip. |
| `DepthText` | `string` | The depth as the culture writes a whole percent (`"P0"`). |

### BlissBoxAction and SectionOrder

`BlissBoxAction` (`DevicesViewModel.cs`) names a Bliss-Box port row's actions: `DreamcastScreen`, `PakBackup`, `PakRestore`, `NativeArrows`. `SectionOrder` (`DevicesViewModel.Board.cs`, internal) is the `IComparer` that sorts the connected list's parts in the Show segments' order, whichever part a device first turned up in.

---

## DeviceRowViewModel

**Files:** `DeviceRowViewModel.cs`, `DeviceRowViewModel.Board.cs`, its part of `SettingResetCommands.cs`

Single device row on the Devices page, and the selected device's panel. Shows identification, status, capabilities, and input hiding controls. `ToString()` returns the row's screen-reader name.

### The Row's Line and Place (#574)

| Property | Type | Description |
|----------|------|-------------|
| `KindGlyph` / `KindShape` | `string` / `Geometry` | The device's kind as an MDL2 glyph (`DeviceTypeGlyph.For`), and the line drawing a wheel or a joystick shows in place of one (`DeviceTypeGlyph.ShapeFor`) or null. Set by `InputService.PopulateDeviceRow` from the device's `CapType`. The row's square shows them. |
| `Section` | `DeviceFilter` | The part of the connected list the row stands in, `DevicesViewModel.FilterOf(DeviceTypeKey)`. |
| `ListGroup` | `DeviceListGroup` | Whether the row stands with the devices connected now or the ones PadForge remembers (`GroupOf(online)`, internal static). Raised only when it changes. The lists move a row at the next `RefreshCounts` and do not filter live. |
| `CountsAsDevice` | `bool` | Computed: the row counts in the page's "N connected", a device a person plugs in, counted once. A merged row, a keyboard's or a remote's consumer-control collection, and a row PadForge or an extra feeds (`IsInternalVirtual`) do not, except a MIDI device, a Falcon and an analog keyboard, which stand for one. |
| `IsGameControllerType` | `bool` | Computed: `DeviceTypeKey` is Gamepad, Joystick, Wheel, FlightStick, FirstPerson or Supplemental, the six types Home offers a controller for (`InputService.IsHomeOfferEligible`). |
| `IsAssigned` / `OffersUse` | `bool` | Computed: a virtual controller uses the device (`SlotBadges.Count > 0`), and the row offers Use It: a game controller that is connected and that no virtual controller uses. |
| `LineLead` / `LineBattery` / `LineTail` | `string` | The row's line, "Gamepad, Bluetooth, battery 82%", in three parts so the charge draws with tabular figures. A link is named only when it is Bluetooth. |
| `LineFacts` | `string` | The line as it is drawn up to the battery: the type and the link when it is Bluetooth, with one more comma when a battery follows. The battery is then its glyph and the percentage. |
| `RowLine` / `RowStatus` | `string` | The row's whole line, its help text for a screen reader, and the pills' names or Not in Use, its item status. |
| `Link` | `DeviceLink` | How the device reaches the PC where PadForge knows it (`DeviceTransport.LinkOf`): Bluetooth, USB, PS/2 or I2C. `None` for a virtual device and one the device tree does not hold. |
| `LinkText` / `LinkMarkText` / `HasLink` | `string` / `string` / `bool` | The link in words (a wireless receiver is the USB device it is), the Bluetooth mark and a space for the Details row's Link line, and whether there is a link to name. |
| `HasLinkOrBattery` | `bool` | The panel has a Link or a Battery tile to show. |
| `IsSending` | `bool` | The device is sending input now: the light on the row's icon (`InputActivity`). |

### Identity

| Property | Type | Description |
|----------|------|-------------|
| `InstanceGuid` | `Guid` | Unique instance GUID. |
| `SdlGuid` | `string` | SDL device GUID string used by gamecontrollerdb mappings. |
| `DeviceName` | `string` | Display name. |
| `ProductName` | `string` | Product name. |
| `ProductGuid` | `Guid` | Product GUID in PIDVID format. |

### USB Identification

| Property | Type | Description |
|----------|------|-------------|
| `VendorId` | `ushort` | USB Vendor ID. Notifies `VendorIdHex`. |
| `ProductId` | `ushort` | USB Product ID. Notifies `ProductIdHex`. |
| `VendorIdHex` | `string` | Computed: hex (e.g., `"045E"`). |
| `ProductIdHex` | `string` | Computed: hex (e.g., `"028E"`). |

### Status

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `IsOnline` | `bool` | `false` | Device connected. Notifies `StatusText`. |
| `IsEnabled` | `bool` | `true` | Device enabled for mapping. Notifies `StatusText`. |
| `StatusText` | `string` | - | Computed: `"Disabled"`, `"Online"`, or `"Offline"`. |
| `SerialNumber` | `string` | `""` | Device serial, where the transport reports one. |
| `HasVidPid` | `bool` | - | Computed: either `VendorId` or `ProductId` is non-zero. Gates the VID:PID line. |
| `FirmwareVersion` | `string` | `""` | The dossier FIRMWARE line: the firmware version SDL reports. SDL gives one for a DualSense and an Edge, pads on the GIP and Xbox One drivers, Switch pads over Bluetooth, Flydigi pads (hifihedgehog/SDL#42), and Xbox pads on the XInput driver whose device GameInput lists (hifihedgehog/SDL#44), in all four parts when SDL publishes them (hifihedgehog/SDL#46). A Bluetooth LE pad SDL reports none for shows the revision its Device Information service gives, as an Xbox pad on Bluetooth does (`"5.23.6.0"`). Empty hides the line. |
| `ProductRevision` | `string` | `""` | The dossier REV line: the product version the device reports, its USB release number (`bcdDevice`) over USB and its PnP ID product version over Bluetooth LE. Empty hides the line. |
| `GameModLine` | `string` | `""` | (#529) What DSX game mods set on the virtual controllers this device feeds, as this device carries it, from `InputService.GameModDeviceLine`. Empty hides the line and **Clear Mod Effects**. |

`FormatFirmwareVersion(ushort version, ushort vendorId)` (public static) prints a 16-bit firmware value by maker: Sony (`0x054C`) as the high byte and the low byte as hex around a dot (`0x0224` is `2.24`, the version SDL takes as current DualSense firmware, the way dualsense-tester's `formatUpdateVersion` writes it), Microsoft (`0x045E`) and Nintendo (`0x057E`) as the major version in the high byte and the minor in the low byte, in decimal (`0x0505` is `5.5`, `0x0348` is `3.72`), every other maker as raw hex (`0x1234`), and `0` as empty. `FormatProductRevision(ushort version)` prints a release number as `0x{version:X4}`, `0` as empty.

### Battery (#167)

Battery indicator on the device row. Sourced from SDL by InputService's slow lane.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `BatteryPercent` | `int` | `-1` | Battery percentage. `-1` when the device reports none (wired, unknown, or offline). Notifies `HasBattery`, `BatteryText`, `BatteryGlyph`. |
| `BatteryCharging` | `bool` | `false` | True while the device reports charging or charged. Notifies `BatteryGlyph`. |
| `HasBattery` | `bool` | - | Computed: `BatteryPercent >= 0`. Gates whether the indicator renders. |
| `BatteryText` | `string` | - | Computed: `"78%"`, or empty when `BatteryPercent < 0`. |
| `BatteryGlyph` | `string` | - | Computed (`BatteryGlyphs.For`): Segoe MDL2 Assets battery glyph bucketed to the nearest tenth. Discharging: Battery0–Battery9 = U+E850–U+E859, Battery10 = U+E83F. Charging: BatteryCharging0–8 = U+E85A–U+E862, BatteryCharging9 = U+E83E, BatteryCharging10 = U+EA93. |
| `BatteryGap` | `string` | - | Computed: the space between the glyph and the percentage, or nothing with no battery. |
| `BatteryLine` | `string` | - | Computed: the battery as the Details card reads it to a screen reader, the percentage and what the row's line says after it ("82%, charging"), or nothing. |
| `BatteryLowAt` | `int` | - | The level Settings names for a low battery (`BatteryNotifyThreshold`). The battery walk hands it to every row with each reading. |
| `BatteryLow` | `bool` | - | Computed: the charge is at or under that level and not charging. |
| `BatterySpoken` | `string` | - | Computed: the battery for a screen reader, its level, and that it is low or charging when it is. |

### Power: Idle Disconnect (#162) and Quick Charge (#372)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `IdleDisconnectMinutes` | `int` | `0` | Idle countdown in minutes, `0` = off. Clamped `>= 0`. Persisted to UserDevice in seconds through the hiding-toggle channel. |
| `ShowIdleDisconnect` | `bool` | `false` | Whether the idle-disconnect control applies (Bluetooth path detected). Set by the service, not computed on the row. Notifies `ShowPowerSection`. |
| `QuickChargeEnabled` | `bool` | `false` | Quick Charge (#372): drop this pad's Bluetooth link when its USB twin comes online. Persisted on UserDevice through the same channel as the hiding toggles. |
| `ShowQuickCharge` | `bool` | `false` | Whether the Quick Charge checkbox applies. Deliberately wider than `ShowIdleDisconnect`: the USB cable rebinds a Sony record to the USB path (identity keys on the shared MAC serial, so no twin record exists), a path the disconnect predicate rejects, which made the checkbox vanish exactly while the pad was plugged in. Seeded by `ComputeShowQuickCharge`. Notifies `ShowPowerSection`. |
| `ShowPowerSection` | `bool` | - | Computed: `ShowIdleDisconnect \|\| ShowQuickCharge`. The Power section draws when either control in it does. |

### Light gun, iCade and USIO rows (hifihedgehog/SDL#33)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `GunCalibration` | `string` | `""` | A GunCon 2's or a Wii Remote's aim range as `UserDevice.GunCalibration` keeps it. Persisted through the hiding-toggle channel, which also hands it to a connected gun or remote. |
| `ShowGunCalibration` | `bool` | `false` | The row is a GunCon 2 (`UserDevice.IsGunCon2`) or a Wii Remote with an IR camera (`UserDevice.HasIrCamera`, #485), online or offline. A Remote Link peer's row has none, the rule the other owner-only controls follow (#248): `ComputeShowGunCalibration`, which the row fill calls. |
| `GunIsWiiRemote` | `bool` | `false` | The light gun is a Wii Remote, not a GunCon 2 (#485). Notifies `GunCalibrationStatus` and `GunCalibrateTooltip`. |
| `GunConnectedHere` | `bool` | `false` | The gun's or remote's live device is this PC's own `SdlDeviceWrapper`. A relayed one is calibrated on its owner's PC. |
| `CanCalibrateGun` | `bool` | - | Computed: `GunConnectedHere && IsOnline`. Enables **Calibrate**. |

| `GunCalibrationStatus` | `string` | - | Computed: the aim range, formatted with `Devices_GunWindowDefault` or `Devices_GunWindowCalibrated`. A Wii Remote's line says only whether a window is stored (`Devices_WiiAimCalibrated` or `Devices_WiiAimDefault`), since its pointer counts mean nothing to a reader. |
| `GunCalibrateTooltip` | `string` | - | Computed: what **Calibrate** does for this gun, `Devices_WiiCalibrateTooltip` for a Wii Remote, else `Devices_GunCalibrateTooltip`. |
| `ShowReadAsICade` | `bool` | `false` | A Bluetooth keyboard with IDs, not the ION iCade cabinet, whose pair `ICadePads` does not list (`ICadePads.CanMark`). |
| `ShowReadAsKeyboard` | `bool` | `false` | A listed pair's iCade Controller joystick, or its keyboard record while the pad is away. |
| `ShowUsioTekken` / `ShowUsioTaiko` | `bool` | `false` | A Namco USIO drum or stick joystick, by the names the fork gives each layout. Each offers the other layout. |

| Method | Description |
|--------|-------------|
| `ComputeShowQuickCharge(string devicePath, ushort vendorId, ushort productId, string serial)` | Internal static, so tests need no view model. True for a `BluetoothLinkHelper.IsDisconnectTarget` shape, or for a record whose serial parses as a non-zero Bluetooth address. The second leg is exactly the gate the engine's wired path fires on, with no vendor gate: the feature fires for any pad that reports its radio's MAC as the serial on both transports. |

### Vendor Source Lines

Panel lines and gates for the optional device sources. Each line is empty for every other row.

| Property | Type | Description |
|----------|------|-------------|
| `BlissBoxLine` | `string` | A Bliss-Box port's line (#469): its player number, the controller in it and the adapter's firmware. Empty while Read Bliss-Box Adapters is off. See [Bliss-Box Internals](bliss-box-internals.md). |
| `ShowBlissBoxPlayer` | `bool` | The port's API channel is open, so its player number can be set. |
| `ShowDreamcastScreen` | `bool` | A Dreamcast pad is in the port. |
| `ShowControllerPak` | `bool` | An N64 controller is in the port on an adapter with firmware 3.0 or later, whose native channel the pak rides. |
| `ShowNativeArrows` / `BlissBoxNativeArrows` | `bool` | A PlayStation digital pad is in a 3.x adapter's port, whose hat cannot carry opposite directions together, and whether the port polls the four directions through the native channel. |
| `BlissBoxIdle` | `bool` | No player change or Controller Pak transfer holds the port's channel and no player change has replaced the port, so its buttons can act. |
| `KeyboardScreenLine` / `KeyboardScreenButtonText` / `ShowKeyboardScreen` | `string` / `string` / `bool` | A keyboard screen's line (#519): what draws the screen or why nothing does, and whose picture Logitech Gaming Software shows when it shares one. The dialog button is named for the kind of screen, and shows while the screen is present. |
| `FalconLine` / `ShowFalconCalibrate` / `FalconCalibrationStatus` | `string` / `bool` / `string` | An open Novint Falcon's line (#521): a homing prompt for its first seconds, then its rate. The calibrate button shows while the Falcon is open, and the status says the reach in use or how the sweep went. |
| `AnalogKeyboardLine` | `string` | An analog keyboard's line (#468): a Razer keyboard that waits for Razer Synapse says so. |
| `ShowFlydigiScreen` | `bool` | The row is a Flydigi Apex pad with a screen and a session (#586), so the Settings card offers its screen's dialog (`DevicesViewModel.RequestFlydigiScreen`, `FlydigiScreenDialog`). |

### Device-Class Flags

| Property | Type | Description |
|----------|------|-------------|
| `IsMidiDevice` | `bool` | Computed: `DeviceTypeKey == "Midi"`. Drives the live piano / CC preview (#128). |
| `IsHeadsetMotionDevice` | `bool` | Computed: `DeviceTypeKey == "HeadsetMotion"`. True for Sony headset head trackers (#188). Collapses the raw Axes / Buttons preview, which a motion-only source has neither of, and gates the repair action. |
| `IsHandheldDevice` | `bool` | Computed: `DeviceTypeKey == "HandheldButtons"`. The handheld hidden-buttons row (#343). |
| `IsSystemMotionDevice` | `bool` | Computed: `DeviceTypeKey == "SystemMotion"`. The machine's own motion sensor row (#343). |

| `ShowManageChatCommands` | `bool` | Computed: `DeviceTypeKey == "TwitchChat"` and the path is not `peer://` (#555). Shows **Manage Chat Commands** (`ChatCommandsDialog`) on the Twitch Chat row. The words are this PC's list, and a peer's shared copy is managed on its owner. See [Twitch Chat Internals](twitch-chat-internals.md). Raised when `DeviceTypeKey` or `DevicePath` changes. |
| `ShowMapKeyLights` | `bool` | Computed (#557): shows **Map Key Lights** (`MapKeyLightsDialog`) when the row's lighting path knows its lights one by one with keys among them and a product name (`PeripheralLightMaps.ForRow(PeripheralOutputs.Links.For(InstanceGuid), out _)` is `{ HasKeys: true, Product: not null }`) and the path is not `peer://`. `RefreshKeyLights()` raises it when the device's lights became known, changed or went. See [MapKeyLightsViewModel](#mapkeylightsviewmodel-557). |
| `ShowRawInputState` | `bool` | Computed: `DeviceTypeKey` is not `"PeripheralLighting"` or `"PeripheralHaptics"`. A lighting or rumble row (#494) reads no input, so it has no Raw Input State section. |
| `IsTouchpadRow` | `bool` | Computed: `DeviceTypeKey == "Touchpad" && !IsAggregate && !IsInternalVirtual`. A precision touchpad's own row. |
| `IsTouchpadMouse` | `bool` | Set by the Devices page while the row is selected and is a precision touchpad's mouse collection. Its switch is the touchpad's, and Hide from Games leaves it as it leaves the touchpad's own row. |
| `TouchpadOnlyInPadForge` | `bool` | Whether PadForge reads this touchpad alone (`UserDevice.TouchpadOnlyInPadForge`, **Use Only in PadForge**). Hidden with nothing reading it, a touchpad was dead in Windows and in PadForge alike, so Hide from Games leaves the row and this switch takes its place. Notifies `ShowTouchpadCaptureStatus`. |
| `ShowTouchpadCaptureStatus` | `bool` | Computed: `IsTouchpadRow && TouchpadOnlyInPadForge`. Shows the capture line under the switch. |
| `TouchpadCaptureState` / `TouchpadInputStatus` | `TabletCaptureState` / `string` | The capture state (`Shared`, `Switching`, `WaitingForInput`, `Captured`, `Failed`) and its line (`Tablet_InputShared`, `Tablet_InputSwitching`, `Touchpad_InputWaiting`, `Tablet_InputCaptured`, `Touchpad_InputFailed`). |
| `IsPadForgeDriverRow` | `bool` | Computed: the row is read over PadForge's own WinUSB driver, a keyboard or mouse taken from Windows (#549, `KeyboardTakeovers.IsTakenOver`) or a bound TouchSense mouse (#494, `VendorUsbDriverInstaller.IsOwnInterfacePath`). Windows sees neither as a keyboard or mouse, so there is nothing to hide from games and nothing for the hook to consume, and both toggles leave the row. `InputService.ServedByPadForgeDriver` skips such a row in the hiding pass. |
| `ShowLearnHandheldButton` | `bool` | Computed: `IsHandheldDevice` and the path is not `peer://`. A peer row's buttons are learned on the machine that has them. |
| `HandheldDaemonRunning` | `string` | Comma-joined names of vendor daemons the sweep found running (#343), empty when none. Written by the device list sync. Notifies the two below. |
| `HasHandheldDaemonWarning` | `bool` | Computed: `IsHandheldDevice` and `HandheldDaemonRunning` is non-empty. |
| `HandheldDaemonWarning` | `string` | Computed: the localized warning naming the running daemons, empty when there is nothing to warn about. |
| `ShowRegisterNfcTag` | `bool` | Computed: shows the Register / Manage NFC Tags button (#150). True for a standalone PC/SC reader (`DeviceTypeKey == "Nfc"`) and for a Switch right Joy-Con / combined pair / Pro Controller (VID 057E, PID 2007 / 2008 / 2009) on a Bluetooth link, whose own reader registers through the same dialog (#241). Always false on a `peer://` row: the tap event never crosses the link, so registration belongs to the owner. |
| `ShowManageVoicePhrases` | `bool` | Computed: shows the Manage Voice Macros button (#317). True for a `"Microphone"` row, and for a DualSense (VID 054C, PID 0CE6 / 0DF2) on a Bluetooth link, where the embedded mic is not a system device. Same `peer://` exclusion as the NFC button. |
| `HasNfcCapabilityChip` | `bool` | Computed: the device is a Switch controller carrying an NFC reader (VID 057E, PID 2007 / 2008 / 2009). A hardware fact, not the transport-gated arming state, so it reads true over USB too. A standalone PC/SC reader is excluded, its device type already says NFC. |
| `IsBluetoothLink` | `bool` | Computed by `DeviceTransport.IsBluetooth` from the device path and VID:PID. |
| `FlydigiServiceRunning` | `string` | Flydigi Space Station processes the device list sync found running (#395), empty when none. Notifies the two below. |
| `IsFlydigiDevice` | `bool` | Computed: `FlydigiServiceWatch.IsFlydigiDevice(VendorId, ProductId)`. |
| `HasFlydigiServiceWarning` / `FlydigiServiceWarning` | `bool` / `string` | Computed: a Flydigi row while Flydigi software is running, and the localized warning that names it (`Flydigi_ServiceWarning_Format`). |
| `IsTabletDevice` | `bool` | Computed: `DeviceTypeKey == "Tablet"`, a drawing tablet. |
| `ShowTabletCaptureStatus` | `bool` | Computed: `IsTabletDevice && !IsInternalVirtual`. Shows the capture line. |
| `TabletCaptureState` | `TabletCaptureState` | `Shared`, `Switching`, `WaitingForInput`, `Captured`, `Failed`, or `Offline`. Notifies `TabletInputStatus`. |
| `TabletInputStatus` | `string` | Computed: the localized line for `TabletCaptureState` (`"Shared Input"`, `"Switching Input"`, `"Waiting For Tablet Input"`, `"Captured By PadForge"`, `"Tablet Input Unavailable"`), or `StatusText` while offline. |

### Capabilities

| Property | Type | Description |
|----------|------|-------------|
| `AxisCount` | `int` | Number of axes. |
| `ButtonCount` | `int` | Number of buttons. |
| `PovCount` | `int` | Number of POV hat switches. |
| `DeviceTypeKey` | `string` | English type key: `"Gamepad"`, `"Joystick"`, `"Wheel"`, `"FlightStick"`, `"FirstPerson"`, `"Supplemental"`, `"Mouse"`, `"Keyboard"`, `"Touchpad"`, `"Tablet"`, `"Midi"`, `"Nfc"`, `"Microphone"`, `"ConsumerControl"`, `"HeadsetMotion"`, `"HandheldButtons"`, `"SystemMotion"`, `"HeadTracker"`, `"VrController"`, `"LogitechGKeys"`, `"AnalogKeyboard"`, `"WebMenus"`, the vendor rows' `"PeripheralLighting"` and `"PeripheralHaptics"` (#494, labeled "Lighting" and "Haptics"), `"KeyboardScreenKeys"` (#519), `"NovintFalcon"` (#521), `"GameTelemetry"` (#531) and `"TwitchChat"` (#555). Anything else falls back to the generic "Device" label. The setter notifies every derived property that reads the key. A row is constructed before the key is known, so one missing from that list evaluates once against the empty string and its binding never updates (#315). |
| `DeviceType` | `string` | Computed: localized type from `DeviceTypeKey`. |
| `HasRumble` | `bool` | Supports rumble. |
| `HasGyro` | `bool` | Has gyroscope. |
| `HasAccel` | `bool` | Has accelerometer. |
| `HasTouchpad` | `bool` | Exposes a touchpad surface. |

| `CapabilitiesSummary` | `string` | Computed: e.g., `"6 axes, 11 buttons, 1 POV, Rumble, Gyro"`, each count in its singular or plural form (`Devices_Caps_OneAxis` / `Devices_Caps_Axes_Format` and the button and POV pairs). A touchpad-type row skips the counts. |

### Slot Assignment

| Property | Type | Description |
|----------|------|-------------|
| `AssignedSlots` | `List<int>` | Assigned pad slot indices (0–15). Set via `SetAssignedSlots()`. |
| `SlotBadges` | `ObservableCollection<SlotBadge>` | Slot pills for XAML (type name + number). Rebuilt by `SetAssignedSlots()`. No pill means unassigned. |

| Method | Description |
|--------|-------------|
| `SetAssignedSlots(List<int>)` | Replaces assigned slots and rebuilds `SlotBadges`, numbering each pill within its type as the sidebar numbers controllers. |

### Input Hiding Toggles

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `HidHideEnabled` | `bool` | `false` | Hidden via HidHide (driver-level). |
| `ConsumeInputEnabled` | `bool` | `false` | Mapped inputs consumed via low-level hooks. |
| `ForceRawJoystickMode` | `bool` | `false` | Bypass SDL gamepad remapping. Read raw joystick indices. |
| `IsHidHideAvailable` | `bool` | `false` | HidHide installed (controls toggle IsEnabled). |
| `ShowConsumeToggle` | `bool` | - | Computed: real keyboards and mice only (`(Keyboard or Mouse) && !IsInternalVirtual && !IsPadForgeDriverRow`). Consumption suppresses the source at the raw/descriptor layer, which only exists for a real Windows HID device. |
| `IsInternalVirtual` | `bool` | - | Computed: true for PadForge-internal virtual sources, identified by a URI-scheme `DevicePath` instead of a real Windows HID path. Twenty-four schemes: `web://`, `overlay://`, `midi://`, `peer://`, `nfc://`, `mic://`, `handheld://`, `sensor://`, `headtrack://`, `openxr://`, `logigkeys://`, `keyboardscreen://`, `falcon://`, `telemetry://`, `twitch://` (#555), `analogkb://`, `razerchroma://`, `logilightsync://`, `steelseriesgg://`, `razersensa://`, `asusaura://`, `msimysticlight://`, `corsairicue://` (the last three #557), `lightunit://`. Those cover web controllers, the touchpad overlay, MIDI-input devices, Remote Link peers, PC/SC readers, WASAPI microphone endpoints, the handheld hidden-buttons row, the machine's own sensor row, the head tracker, the OpenXR hand-controller rows, the Logitech G-Keys row, the keyboard screen rows (#519), the Novint Falcon rows (#521), the Game Telemetry row (#531), the Twitch Chat row (#555), the analog keyboard rows, the Razer Chroma, Logitech LIGHTSYNC, SteelSeries GG and Razer Sensa rows, and the unit rows of lit devices no mouse or keyboard row reaches (#494). `DeviceRowGateTests.EverySchemeTheSourceAssigns_IsInternalVirtual` reads every scheme the app and the engine assign and checks each one here. HidHide cannot blacklist a non-HID path, so the "Hide from games" toggle hides itself for these. |
| `IsAggregate` | `bool` | - | Computed: an `aggregate://` merged row (All Keyboards, All Mice, All Touchpads, All Consumer Controls). It has no HID instance of its own. |
| `ShowHidHideToggle` | `bool` | - | Computed: `!IsInternalVirtual && !IsAggregate && !IsPadForgeDriverRow && !IsTouchpadRow && !IsTouchpadMouse`. Gates the "Hide from games" checkbox. |
| `ShowsHidingDriverSwitch` | `bool` | `false` | Set by the Devices page while the row is selected and a button of its keyboard's or mouse's switch (#549), or of a precision touchpad's switch, shows. The button stands in the Input Hiding section, which a switched device keeps for it alone, since both toggles leave such a row. |
| `NotifyTakeoverChanged()` | method | - | Internal. The takeover list changed, so `IsPadForgeDriverRow`, both toggles and `ShowInputHidingSection` are raised again. A taken device whose WinUSB row never opened keeps its path, so nothing else raises them. |
| `ShowInputHidingSection` | `bool` | - | Computed: `ShowHidHideToggle \|\| ShowConsumeToggle \|\| ShowsHidingDriverSwitch`. Drives the Input Hiding section visibility, heading included. |
| `ShowInputModeSection` | `bool` | - | Computed: `_forceRawJoystickMode \|\| (IsGamepad && !IsInternalVirtual)`. Drives the Input Mode (Force Raw Joystick) section visibility. A row whose flag is on shows the section whatever its type or path, so the checkbox can turn it off. |


### Device Path

| Property | Type | Description |
|----------|------|-------------|
| `DevicePath` | `string` | Device path (diagnostics). Notifies `DossierConnectionPath` and the `IsInternalVirtual` family. |
| `HidHideInstancePath` | `string` | Resolved HID instance path for HidHide blacklisting. Notifies `DossierConnectionPath`. |
| `DossierConnectionPath` | `string` | Computed: the connection path the dossier shows when no HidHide instance path occupies the PATH row. Covers bridged devices like the DS3, whose real transport path (BthPS3 PDO / WinUSB interface) arrives through `SdlDeviceWrapper.ExternalDevicePathProvider` even though SDL reports no path. Empty for internal virtual sources and when a HidHide path is already shown. |

### Display Helpers

| Property | Type | Description |
|----------|------|-------------|
| `IsGamepad` | `bool` | Computed: true if `DeviceTypeKey == "Gamepad"`. |
| `ShowSubmitMapping` | `bool` | Computed: the device can have a community mapping submitted. True for everything except `"Gamepad"`, `"Mouse"`, `"Keyboard"`, `"Touchpad"`, `"Tablet"`, `"Midi"`, `"Nfc"`, `"HeadsetMotion"`, `"Microphone"`, `"ConsumerControl"`, `"HandheldButtons"`, `"SystemMotion"`, `"HeadTracker"`, `"VrController"`, `"LogitechGKeys"`, `"AnalogKeyboard"`, `"WebMenus"`, `"PeripheralLighting"`, `"PeripheralHaptics"`, `"KeyboardScreenKeys"`, `"NovintFalcon"`, `"GameTelemetry"` and `"TwitchChat"`. |

`ResetSettingCommand` resets the row's own options by name (`CanResetSetting`, internal static), through `DevicesViewModel.ResetSelectedDeviceSettingCommand`.

### SlotBadge

**File:** `DeviceRowViewModel.cs`

Slot assignment pill: the type's name and its number within the type. `ToString()` returns `Label`, so a screen reader reads the name the pill shows.

| Property | Type | Description |
|----------|------|-------------|
| `SlotIndex` | `int` | Zero-based pad slot index. |
| `SlotNumber` | `int` | Sequential global number (1-based among created slots). |
| `VcType` | `VirtualControllerType` | The slot's output type, which picks the badge art below. |
| `TypeGeometry` / `TypeGlyph` | `Geometry` / `string` | Branded icon path, or the Segoe glyph for the types with no path (`SlotTypeIconMap`). |
| `TypeNumber` | `int` | The slot's number within its type: Xbox #1, Xbox #2. |
| `Label` | `string` | Computed: `SlotTypeIconMap.NameFor(VcType)`, `" #"` and `TypeNumber`. `RaiseLabel()` re-raises it after a language change. |

### SlotTypeIconMap

**File:** `DeviceRowViewModel.cs` (static)

The one table of type art and names, which the sidebar pills, Home's cards, the slot pills and chips, the Profiles cards and Add a Controller all read: `GeometryFor(type)` (the branded path, or null for the glyph-only types), `GlyphFor(type)` (the MDL2 glyph for the types without a vector logo, empty otherwise) and `NameFor(type)` (the type's name in the language, as the type bar and the sidebar write it).

---

## PadViewModel

**Files:** `PadViewModel.cs`, `PadViewModel.Sections.cs` (the controller page's six sections, #574), `PadViewModel.List.cs` (the mapping list's columns, #574), `PadViewModel.Centering.cs` (the Centering card, #588), `PadViewModel.GyroActivation.cs` (the Gyro card's activation rows), `PadViewModel.Touchpad.cs` (partial added in v3.3 for the Touchpad group's properties), `PadViewModel.Mouse.cs` (partial added for the #200 mouse gestures), `PadViewModel.AudioDsp.cs` (partial added in 4.3.2 for the #347 Audio DSP chain), `PadViewModel.Keyboard.cs` (partial added for the keyboard menu's slot side, #566), and its part of `SettingResetCommands.cs`
**DataContext for:** the controller page (`Views/PadPage.xaml`, one per virtual controller slot)

The largest ViewModel. One per virtual controller slot (16 total). Handles output type, multi-device selection, the mapping list, deadzone/sensitivity, macros, force feedback, touchpad settings, and live state display.

The controller page is a header and six sections: Buttons (`Section_Buttons`, named Mappings on a controller and Keys & Mouse, Notes & Controls or Hands on the other slot types), Sticks & Triggers, Rumble & Haptics, Motion & Touch, Lights & Sound, and Macros & Menus. The view model still numbers the old tabs (`SelectedConfigTab`, 0 to 17), and each number is now a group of one section: see [Sections and Groups](#sections-and-groups-574). This page names a group by its old tab's name ("the Lighting group").

### Identity and Type

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `PadIndex` | `int` | - | Zero-based slot index (0–15). Read-only. |
| `SlotNumber` | `int` | `PadIndex + 1` | 1-based number among active slots. |
| `SlotLabel` | `string` | - | Display label (e.g., `"Virtual Controller 1"`). |
| `OutputType` | `VirtualControllerType` | `Xbox` | Output type. Resets deadzones, rebuilds mappings/stick/trigger configs, syncs macro button style. A Home card's type chip and a sidebar pill's type chip open the type bar (`MainWindow.ShowTypeBar`), which changes it through `ChangeSlotType`. |
| `TypeInstanceLabel` | `string` | `"1"` | Per-type instance label. Set by `RefreshNavControllerItems`. |

| `OutputTypeDisplayName` | `string` | - | Computed: localized type name for the tier-1 header. Re-raised on `OutputType` and culture changes. |
| `PresetDisplayName` | `string` | - | Computed: the name the slot's Preset chip shows on its controller page. The HIDMaestro profile's name for an Xbox, PlayStation, Nintendo or Extended slot (a null `ProfileId` falls back to `InputManager.GetDefaultProfileId(OutputType)`, as `CreateVirtualController` does), the surface mode's name for a Keyboard + Mouse slot (`KbmConfig.AvailableKbmSurfaces`), and the type name for MIDI and VR, which have no Preset. The sidebar entry and the Home card print it (discussion #543). Raised wherever an input changes: `ProfileId`, `OutputType`, the Keyboard + Mouse halves and the culture. The display lane reads it at 30 Hz, so the lookups are index loops that allocate nothing. `MainViewModel.OnPadPresetChanged` forwards it. |
| `ConfigItemDirtyCallback` | `Action` | `null` | Called on config item change. Wired to `SettingsService.MarkDirty()`. |

### HIDMaestro Profile

The slot's HID descriptor. Picking a different profile rewires the slot, so the setter does the work of a small migration before anything rebinds.

| Property | Type | Description |
|----------|------|-------------|
| `ProfileId` | `string` | HIDMaestro profile slug (`"xbox-360-wired"`, `"dualsense"`, `"logitech-g920"`). Null or empty falls back to the active category's default profile in `CreateVirtualController`. |
| `AvailableProfiles` | `IReadOnlyList<HMProfile>` | Computed: the catalog list for the current category (Xbox / PlayStation / Nintendo / Extended). Empty for MIDI, Keyboard+Mouse, and VR slots, which use no HIDMaestro profile. |
| `PresetChoices` | `IReadOnlyList<PresetChoice>` | The Preset picker's list: `AvailableProfiles` as an id and the name PadForge shows (`HMaestroProfileCatalog.DisplayName`: a profile's product name, and `Pad_Preset_Custom` for the synthetic Custom profile, which keeps "Custom" as the name HIDMaestro reads). Made again when the list or the language changes. Equal by id, so a list made for a new language keeps the pick. |
| `HasHMaestroProfileBar` | `bool` | Computed: the slot's category uses an HIDMaestro profile. Gates the Preset chip on the controller page's header. True for Xbox, PlayStation, Nintendo, and Extended. |

The `ProfileId` setter, in order. Steps 1 and 2 run on a live re-target only: the setter reads `SettingsManager.GetWireStamp` before translating, and restore, apply, and import paths stamp the incoming wire first, so they no-op through both. An unknown stamp adopts the incoming profile and moves nothing, since the data was saved with it, so the next change on the slot reads as the live change it is. The `OutputType` setter stamps the new category's default before it assigns the profile, so a type change never reads the incoming set as a re-target from the outgoing wire.

1. Translates existing raw bindings by role, with the SOCD pairs and each device's per-mapping deadzone and Bidirectional entries, on a Nintendo slot, or on any slot where both the outgoing and incoming wires are lettered (`NintendoPreviewMap.IsLettered`). Every other live re-target only re-stamps the wire (`StampNintendoWire`). Raw targets are wire-relative and the lettered families share almost no indices, so without the translation every binding keeps its index and silently changes meaning.
2. On an Extended or Nintendo slot, fills empty auto-mappings for what the new profile added (`DeviceService.FillEmptyAutoMappingsForSlot`, then `SettingsService.RefreshMappingSetsFromLegacy`), merged into the slot's `MappingSet` before the rebuild, since the grid rebuilds from the set and the save pipeline regenerates settings from the grid. Fill is additive, so a binding the user authored or deliberately cleared survives.
3. Reseeds `ExtendedConfig` from the profile (`SyncExtendedConfigFromProfile`): `ThumbstickCount` and `TriggerCount` from `HMProfile.StickCount` / `TriggerCount`, `PovCount` from `HasHat`, `ButtonCount` from `HMProfile.ButtonCount`, or on a Nintendo lettered profile from its own lettered count. That lettered count is authoritative rather than a `Min` against the SDK-reported one: taking a `Min` let a low reported count truncate the surface, which is how Capture, GR, GL, and C went missing from the Switch 2 Pro grid. A Valve lettered profile takes all four counts from `NintendoPreviewMap` instead, because those descriptors declare almost nothing and the real shape lives in the extended report. Picking the synthetic Custom entry also forces `ExtendedConfig.Customize` on.
4. Rebuilds mappings, stick configs, and trigger configs, re-derives macro and menu button lettering (`SyncMacroButtonStyle`), and re-gates the Bass Shakers group.

Xbox and PlayStation slots have fixed layouts, so they skip the reseed. They rebuild mappings and re-derive the macro and menu lettering (`SyncMacroButtonStyle`, which also stamps each macro's `CarriesPressure`, #530). On a PlayStation slot, a live preset change first fills, from the slot's pads, what the new preset's default maps and the outgoing one's does not (`DeviceService.FillEmptyPresetMappingsForSlot`): the Full preset's pressure rows, and the touchpad, Mic Mute and Edge rows a DualShock 3 preset withheld. A field the outgoing default mapped and the user cleared on that wire stays cleared. Profile-gated rows exist inside those fixed layouts too (Xbox Series adds Share, the DualSense family adds Mic Mute, the Edge adds its paddle and Fn pairs, the Full preset adds the ten pressure rows, and both DualShock 3 presets drop the touchpad rows and label Back and Start as Select and Start), so a profile change within the category still has to rebuild the row list. The lettering follows for the same reason: `MacroButtonNames.DeriveStyle` returns `DualShock3` for a PlayStation slot on either DualShock 3 preset (`HMaestroProfileCatalog.IsDualShock3`).

### Extended Configuration

| Property | Type | Description |
|----------|------|-------------|
| `ExtendedConfig` | `ExtendedSlotConfig` | Per-slot Extended config (preset, axis/button/POV counts). Drives the HID descriptor handed to HIDMaestro for Extended slots. Only meaningful when `OutputType == Extended`. Subscribes to `PropertyChanged` for dynamic rebuilds. |

### MIDI Configuration

| Property | Type | Description |
|----------|------|-------------|
| `MidiConfig` | `MidiSlotConfig` | Per-slot MIDI config (channel, CC/note mappings). Only meaningful when `OutputType == Midi`. |
| `IsLegacyMidi` | `bool` | True while the legacy MIDI API runs MIDI slots. Shows the MIDI bar's Output Port picker. MainWindow sets it on every pad from the Settings card's refresh. |

### Per-(Slot, Device) Lighting / Adaptive Trigger Configuration

Drives the Adaptive Triggers and Lighting groups. Keyed per physical device, so two devices on one slot each carry their own lighting/trigger config. A lit mouse, keyboard, unit row or vendor row (#494) gets its own config here too, whose `PeripheralLightingEnabled` decides whether this slot lights a mouse or keyboard at all and whose `PeripheralClaimLevel` says how firmly. See [DeviceSlotConfig](#deviceslotconfig).

| Property | Type | Description |
|----------|------|-------------|
| `DeviceConfig` | `DeviceSlotConfig` | The Adaptive Triggers and Lighting groups' currently bound config, following `SelectedMappedDevice`. The setter re-attaches its `PropertyChanged` forwarder (`ActiveDeviceConfigPropertyChanged`) on swap. Before the change notice it detaches `KeyColors` and `LedStrips`, so a swap no page sees leaves them detached, never on the old config. |
| `KeyColors` | `KeyColorsCardViewModel` | The Lighting group's Key Colors or Zone Colors card for the selected device (#557). The page attaches it to `DeviceConfig` and the device's lights, and `UpdateLayers(LayerTabs)` keeps its shift-layer chips current. |
| `LedStrips` | `LedStripsCardViewModel` | The Lighting group's LED Strips card (#557), attached the same way. |
| `PerDeviceSlotConfigs` | `IReadOnlyDictionary<Guid, DeviceSlotConfig>` | Per-device configs keyed by InstanceGuid. The empty-Guid key holds a fallback used before any device is mapped. |

| Method | Description |
|--------|-------------|
| `GetOrCreateDeviceConfig(Guid)` | Returns the per-device config, creating a fresh default entry if none exists. Empty Guid returns the anchor config. |

| `EnsureDeviceSlotConfigsForMappedDevices()` | Adds a default config entry for every currently-mapped device. |

Three lines name a DSX game mod (#529) while it holds something on the slot. `InputService.SetGameModPadLines` sets them, and each is empty otherwise:

| Property | Type | Shown on |
|----------|------|----------|
| `GameModTriggersLine` | `string` | The Adaptive Triggers group, while the mod holds a trigger program |
| `GameModImpulseLine` | `string` | The Impulse Triggers group, while the mod holds a trigger program |
| `GameModLightsLine` | `string` | The Lighting group, while the mod holds the lightbar, the player lights or the mute light |

### Keyboard + Mouse Configuration (#205)

| Property | Type | Description |
|----------|------|-------------|
| `KbmConfig` | `KbmSlotConfig` | Per-slot surface mode and SOCD / Snap Tap config. Always present, only meaningful when `OutputType == KeyboardMouse`. See [KbmSlotConfig](#kbmslotconfig). |
| `KbmKeyboardDevice` / `KbmMouseDevice` | `string` | Forwarders over `KbmConfig.KeyboardDevice` / `MouseDevice` for the device bar's pickers, each with a reset button. A null write is ignored, and a change calls `NotifyKbmSurfacesChanged()`, which re-reads the pickers, their visibility, the capability tags and the mapping table's rows. |
| `KbmKeyboardDeviceVisible` / `KbmMouseDeviceVisible` | `bool` | A picker shows while the surface mode drives its half. |
| `KbmKeyboardCapabilities` / `KbmMouseCapabilities` | `IReadOnlyList<string>` | The device bar's tags for the picked model: Keys at Once (or Any), Media Keys and Lock Lights for a keyboard, and Buttons, Wheel and Tilt Wheel for a mouse. Empty on Windows input. |
| `KbmKeyboardLeds` | `int` | The lock lights Windows last set on the slot's virtual keyboard (bit 0 Num Lock, 1 Caps Lock, 2 Scroll Lock), -1 without one. The poll fills it beside `KbmOutputSnapshot`, and the preview reads it per frame. |
| `KbmSurfaces` | `string` | Forwarder over `KbmConfig.Surfaces` for the surface dropdown (#408). A null or empty write is ignored. `NotifyKbmSurfacesChanged()` re-reads it after a load, paste, or profile apply and re-filters the mapping table. |
| `MappingSurfaceScope` | `string` | The mapping table's keyboard / mouse scope: `All`, `Keyboard`, or `Mouse`. Session state. Visible only through `KbmSurfaceScopeVisible` (a Keyboard + Mouse slot in `Both` mode), and reset to `All` when the slot type changes. |

### Multi-Device Selection

| Property | Type | Description |
|----------|------|-------------|
| `MappedDevices` | `ObservableCollection<MappedDeviceInfo>` | Physical devices mapped to this slot. |
| `SelectedMappedDevice` | `MappedDeviceInfo` | Selected device for configuration. Raises `SelectedDeviceChanged`, notifies `HasSelectedDevice`. |
| `HasSelectedDevice` | `bool` | Computed: `SelectedMappedDevice != null`. |
| `MappedDeviceName` | `string` | Mapped device name. Default: `"No device mapped"`. |
| `MappedDeviceGuid` | `Guid` | Mapped device GUID. |
| `IsDeviceOnline` | `bool` | Mapped device is online. |

| Event | Args | Description |
|-------|------|-------------|
| `SelectedDeviceChanged` | `MappedDeviceInfo` | Different device selected. InputService reloads PadSetting. |

#### MappedDeviceInfo (nested class)

One device assigned to the slot: an entry of the controller page's device pills, of the mapping list's columns and of Home's detailed cards.

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `HasBattery` | `bool` | - | Whether the device reports a battery: a charge from 0 up (`SetBattery`). |
| `HasLinkOrBattery` | `bool` | - | Whether anything stands after the device's name on its pill: the mark of a Bluetooth link or a battery. |
| `TransportGlyph` | `string` | `string.Empty` | Segoe MDL2 transport glyph for the device pill (#175): Bluetooth links carry E702, wired stays unmarked (the quiet default). |
| `HasTransportGlyph` | `bool` | - |  |
| `IsBluetooth` | `bool` | - | Whether the device is linked over Bluetooth, the one link that is marked: a wired one stays unmarked. |
| `IsSending` | `bool` | - | Whether the device is sending input now: the small light beside its name (Common.Input.InputActivity). |
| `BatteryPercent` | `int` | - | The charge from 0 to 100, or -1 while the device reports no battery. The meter draws it. |
| `BatteryCharging` | `bool` | - |  |
| `BatteryLow` | `bool` | - | Whether the charge is at or under the level Settings names for a low battery, and not charging. |
| `BatterySpoken` | `string` | - | The battery for a screen reader: its level, and that it is low or charging when it is. |
| `RaiseWords` | method (internal) | - | Has the spoken battery read again: the language changed. |
| `SetBattery` | method | - | Sets every battery fact from one reading: `lowAt` is the level Settings names. |
| `TypeGlyph` | `string` | `"\uE7FC"` | Segoe MDL2 device-class glyph (#175): keyboards read as keyboards, mice as mice. Sourced from DeviceTypeGlyph.For. Defaults to the controller glyph until InputService resolves the device. |
| `TypeShape` | `Geometry` | - | The line drawing a wheel or a joystick shows in place of a glyph (DeviceTypeGlyph.ShapeFor), or null. Its `TypeGlyph` is empty then. |
| `TypeKey` | `string` | `string.Empty` | The kind of device, as the Devices page keys it ("Gamepad", "Wheel"). The list's head names it under the device (`TypeName`). |
| `TypeName` | `string` | - | The kind of device in words: "Gamepad", "Wheel", "Keyboard". |
| `Name` | `string` | `"Unknown"` |  |
| `InstanceGuid` | `Guid` | - |  |
| `IsOnline` | `bool` | - | Per-device connect state, the same ud.IsOnline truth the card's "N connected" count reads (#175 phase 2 item 14). Refreshed every display tick in RefreshSlotSummaryProperties from the same device snapshot as that count, so an offline roster line dims instead of rendering full-brightness cold. |
| `BatteryText` | `string` | `string.Empty` | "78%" while the device reports a battery, empty otherwise (issue #167). Refreshed on the UI timer's slow lane. |

### Assignment Offer (Settings > Assignment Prompts)

The controller page's assign-offer banner. `InputService` writes it when a device connects while this slot's page is open and one of the two Assignment Prompts settings applies. UI-only state, never persisted.

| Member | Type | Description |
|--------|------|-------------|
| `AssignOfferGuid` | `Guid` | The device on offer, or `Guid.Empty`. |
| `HasAssignOffer` | `bool` | Computed: `AssignOfferGuid != Guid.Empty`. |
| `AssignOfferText` | `string` | The banner sentence (`Pad_AssignOffer_Format`: "{0} just connected. Assign it to this virtual controller?"). |
| `SetAssignOffer(Guid, string)` / `ClearAssignOffer()` | methods | Raise or clear the offer. An empty guid clears it. |
| `AcceptAssignOfferCommand` | `RelayCommand` | Clears the offer and raises `AssignOfferAccepted` with the guid. MainWindow routes it to `DeviceService.AssignDeviceToSlot`, the drag-and-drop entry point. |
| `DismissAssignOfferCommand` | `RelayCommand` | Not Now. Clears the offer and raises `AssignOfferDismissed`, so `InputService` skips that device for this slot for the rest of the session. |

### XInput Output State (Controller Visualizer)

Combined slot output values, updated at 30 Hz by `UpdateFromEngineState()`. Bound to the 2D/3D controller visualizer. On a slot whose preview rides the raw surface, `UpdateNintendoPreviewFromRaw` owns the button and stick properties instead, and `UpdateFromEngineState` writes only the selected device's motor bars.

**Buttons (all `bool`):**

`ButtonA`, `ButtonB`, `ButtonX`, `ButtonY`, `LeftShoulder`, `RightShoulder`, `ButtonBack`, `ButtonStart`, `LeftThumbButton`, `RightThumbButton`, `ButtonGuide`, `DPadUp`, `DPadDown`, `DPadLeft`, `DPadRight`

Family extras on the same lane, each driving the 2D overlay and 3D mesh accent for the pads that carry the button: `ButtonShare` (Xbox Series), `ButtonMute` (DualSense mic mute), `LeftFunction` / `RightFunction` (DualSense Edge Fn), `ButtonC` / `LeftPaddle` / `RightPaddle` (Switch 2 Pro C, GL and GR, with `UpdateFromEngineState` writing the paddle pair on PlayStation slots too, so both surfaces share it), and the Valve set `ButtonQuickAccess`, `Paddle1`-`Paddle4` (translator handedness: R4, L4, R5, L5), `LeftGrip` / `RightGrip` (the 2015 pad's rear grips), and `LeftTouchpadClick` / `RightTouchpadClick`.

On a Nintendo or Valve slot these come from `UpdateNintendoPreviewFromRaw`, which walks `Models2D.NintendoPreviewMap.ButtonTable(ProfileId)` and assigns by name. It is table-driven off the same wire table the mapping grid and the click-to-record path use, so the two directions cannot disagree. The hardcoded index list it replaced was the original Pro Controller's, and it lit the wrong art for eleven of the Switch 2 Pro's twenty-one buttons. Two details fall out of the table: on the 2015 Steam Controller the right pad click is also the right stick button, so `RightThumbButton` follows `RightTouchpadClick`, and a profile that spends real buttons on the D-pad (Switch 2 Pro) skips the hat read entirely.

**Axes (combined slot values):**

| Property | Type | Description |
|----------|------|-------------|
| `LeftTrigger` | `double` | Left trigger (0.0–1.0). |
| `RightTrigger` | `double` | Right trigger (0.0–1.0). |
| `ThumbLX` | `double` | Left stick X (0.0–1.0, 0.5 = center). |
| `ThumbLY` | `double` | Left stick Y (0.0–1.0, 0.5 = center, Y inverted). |
| `ThumbRX` | `double` | Right stick X (0.0–1.0, 0.5 = center). |
| `ThumbRY` | `double` | Right stick Y (0.0–1.0, 0.5 = center, Y inverted). |

**Raw values:**

| Property | Type | Description |
|----------|------|-------------|
| `RawThumbLX` | `short` | Raw left stick X (−32768 to 32767). |
| `RawThumbLY` | `short` | Raw left stick Y. |
| `RawThumbRX` | `short` | Raw right stick X. |
| `RawThumbRY` | `short` | Raw right stick Y. |
| `RawLeftTrigger` | `ushort` | Raw left trigger (0–65535). |
| `RawRightTrigger` | `ushort` | Raw right trigger (0–65535). |

**Per-device values (selected device only, for the stick and trigger previews):**

| Property | Type | Description |
|----------|------|-------------|
| `DeviceThumbLX` | `double` | Selected device left stick X (0.0–1.0). |
| `DeviceThumbLY` | `double` | Selected device left stick Y. |
| `DeviceThumbRX` | `double` | Selected device right stick X. |
| `DeviceThumbRY` | `double` | Selected device right stick Y. |
| `DeviceRawThumbLX` | `short` | Selected device raw left stick X. |
| `DeviceRawThumbLY` | `short` | Selected device raw left stick Y. |
| `DeviceRawThumbRX` | `short` | Selected device raw right stick X. |
| `DeviceRawThumbRY` | `short` | Selected device raw right stick Y. |
| `DeviceLeftTrigger` | `double` | Selected device left trigger (0.0–1.0). |
| `DeviceRightTrigger` | `double` | Selected device right trigger. |
| `DeviceRawLeftTrigger` | `ushort` | Selected device raw left trigger. |
| `DeviceRawRightTrigger` | `ushort` | Selected device raw right trigger. |

### Mapping Rows

| Property | Type | Description |
|----------|------|-------------|
| `Mappings` | `ObservableCollection<MappingItem>` | Rows linking physical inputs to output targets. Rebuilt by `RebuildMappings()`. |
| `ActiveLayerMask` | `string` | The layer being authored in the mapping list (the selected layer tab). Defaults to `Base`. A change raises `LayerChanging` first, then `LayerActivated`, so the grid reloads that layer's rows. |
| `LayerTabs` | `ObservableCollection<ShiftLayerInfo>` | Layer tab strip entries above the mapping list, one per layer (Base + each shift layer). Populated by `RebuildLayerTabs` from the slot's `ShiftActivators`. |
| `HasShiftLayers` | `bool` | True when at least one shift activator is authored (i.e. at least one tab beyond Base). |

| Event | Description |
|-------|-------------|
| `MappingsRebuilt` | Raised after `RebuildMappings()` completes so InputService can reload descriptors. |
| `LayerChanging` | Raised before `ActiveLayerMask` changes, while the grid still belongs to the old layer. |
| `LayerActivated` | Raised when `ActiveLayerMask` changes. Subscribers reload per-row source data so the DataGrid reflects the active layer's rows. |

The slot's `MappingSet` (multi-source rows, shift layers and their activators, plus the menus, SOCD, Bass Shakers, and Keep Controller Awake configs) is not a `PadViewModel` property. It lives in `SettingsManager.SlotMappingSets[PadIndex]`, and the view model reads it through a private accessor. See [Button and Axis Mappings](../features/mappings.md) and [Shift Layers](../guides/shift-layers.md).

### Slot-Level Picker Lists and Mapping Picker Filter (#322, discussion #302)

Slot-wide cross-device choice lists, plus the one search box and device-visibility set applied as the filter of the shared views every picker on the slot binds. `ApplyMappingPickerFilter` filters all five lists, and `RebuildPickerDeviceFilterEntries` builds the popup from the device groups of the first three, so a device the Motion rows alone offer still has a checkbox. The key list holds no device the full list lacks. A view filter changes what a dropdown offers, never what a row's binding holds, so saved selections survive filtering.

| Property | Type | Description |
|----------|------|-------------|
| `SlotAvailableInputs` | `ObservableCollection<InputChoice>` | Slot-level cross-device choice list, so the Gyro group's Aim Engage picker and any other slot-wide picker binds without proxy-walking `Mappings`. Populated by `InputService.PopulateAvailableInputs`. Every choice except the four bundled motion sources (#475). |
| `SlotMotionGyroInputs` | `ObservableCollection<InputChoice>` | (#475) The Motion Gyro row's choices: `Motion Gyro` and `Motion Gyro L` per device, the one kind that row reads. |
| `SlotMotionAccelInputs` | `ObservableCollection<InputChoice>` | (#475) The Motion Accelerometer row's choices: `Motion Accel` and `Motion Accel L` per device. |
| `SlotButtonInputs` | `ObservableCollection<InputChoice>` | A button row's list: the entries of `SlotAvailableInputs` a button read can press, as the same instances, less a touchpad finger's place (`MappingItem.ButtonReadPressesNothing`). The rows whose target reads its sources as a press bind it (`InputService.PickerListForRow`). A finger's place saved on such a row before stays stored, and its picker shows no selection. |
| `SlotKeyInputs` | `ObservableCollection<InputChoice>` | The Up and Down pickers' list: the entries of `SlotAvailableInputs` an Incremental or Ramp source reads as a key (`SourceKindRuntime.ReadsAsKey`), as the same instances. A stick, a trigger or another axis is in the full list and not in this one. |
| `SlotAvailableInputsView` | `ICollectionView` | Grouped view over the list, keyed on `InputChoice.DeviceLabel` for the picker's GroupStyle header. |
| `SlotMacroTriggerChoices` | `ObservableCollection<InputChoice>` | The subset of `SlotAvailableInputs` that converts to a `MacroItem.TriggerInputEntry` (raw buttons, POV directions, gamepad-layout axes, the touchpad click and finger reads, gestures, gyro axes, stick rings, and the on/off sources: capsense, NFC tags, voice phrases, analog keys, menu cells, MIDI notes, CCs and encoder detents, and `IR Offscreen`), for the macro trigger dropdown (#177). |
| `SlotMacroTriggerChoicesView` | `ICollectionView` | Grouped view over the macro-trigger list, same `DeviceLabel` grouping. |
| `MappingInputSearch` | `string` | Find-as-you-type over the picker list. Session state, never persisted. Setting it re-applies the filter. |
| `PickerDeviceFilterEntries` | `ObservableCollection<PickerDeviceFilterEntry>` | The device-filter popup's rows, one per device group currently in the picker. |
| `MappingPickerFilterActive` | `bool` | Computed: any hidden device, a non-empty search, or a `MappingSurfaceScope` other than `All`. Lets the funnel button read as engaged. |

| Method / Event | Description |
|----------------|-------------|
| `RebuildPickerDeviceFilterEntries()` | Rebuilds the popup rows from the shared list's current device groups, preserving each group's shown / hidden state. Called after every picker repopulation. |
| `SetHiddenPickerDeviceKeys(IEnumerable<string>)` | Restores the persisted hidden set on settings load. |
| `GetHiddenPickerDeviceKeysJoined()` | The persisted form: hidden keys, semicolon-joined. Stored per slot in the settings root, not in profiles. |
| `PickerDeviceFilterChanged` | Raised when the hidden set changes so the settings service can mark dirty and persist. |

The search filters both sides: the dropdown's offered choices, and the mapping grid's own rows. A row matches when its target label or its selected source's display name carries the text. Rows are outputs, so the device-visibility set never hides them, only typed text does. On a Keyboard + Mouse slot the row filter also drops rows of a half the surface mode turns off, then applies `MappingSurfaceScope` (#408).

`PickerDeviceFilterEntry` is one popup row: `Key` (device guid, or `"any"` for the device-agnostic group), `Label`, and a two-way `IsShown` whose setter toggles the owner's hidden set.

### Per-Device Test Routing (3.2)

Not a ViewModel property. `InputManager.TestRumbleTargetGuid` is a `Guid[MaxPads]` array holding, per slot, the InstanceGuid of the device currently visible in the per-device groups (Impulse Triggers, Force Feedback, Adaptive Triggers, Lighting). InputService's test-send methods (`SendTestImpulseTrigger` and its siblings) set the slot's entry to the device GUID the controller page passed, and clear it back to `Guid.Empty` when the pulse ends. Test / Probe actions in those groups gate on `target == Empty || ud.InstanceGuid == target` so only the selected physical pad fires, and `UserEffectsDispatcher.TestRumbleTargetGuidProvider` carries the same gate into the dispatcher branches that emit physical effects from those groups (for example auto-routed impulse-to-AT vibration).

### Touchpad State (3.2 canonical slot)

| Property | Type | Description |
|----------|------|-------------|
| `TouchpadClickPressed` | `bool` | True while the touchpad-click button is held (`state.Buttons[16]` = `SDL_GAMEPAD_BUTTON_TOUCHPAD` upstream). Drives the 2D/3D model click highlight and the per-press lightbar overlay synth. |
| `TouchpadFinger0X` / `TouchpadFinger0Y` / `TouchpadFinger0Down` | `float` / `float` / `bool` | First finger position (0..1, normalized to pad width / height) and contact state on the source touchpad. |
| `TouchpadFinger1X` / `TouchpadFinger1Y` / `TouchpadFinger1Down` | `float` / `float` / `bool` | Second finger position and contact state. |

All seven are written by `UpdateFromTouchpadState(in TouchpadState)`, which mirrors the per-slot combined touchpad state so the 2D / 3D / web previews can render finger dots and the click highlight. Only meaningful on PlayStation slots, harmless elsewhere.

| Method | Description |
|--------|-------------|
| `RebuildMappings()` | Rebuilds Mappings from `OutputType` and Extended config. Dispatches to type-specific initializers. |

### Touchpad Gestures (v3.3)

**File:** `PadViewModel.Touchpad.cs`

Per-(active device, pad-index) touchpad settings. Same Load / Sync / guard rhythm as the gyro tuning partial: `Load*` reads `PadSetting.TouchpadSettings[]` into VM fields under the `_loadingTouchpadGestures` guard, setters push back through `PushIfNotLoading`, and `InputService` calls the sync method on the live polling rhythm so the gesture engine sees changes at once. Setter clamps in parentheses below.

**Active pad pivot** (devices with two pads, Steam Controller / Deck):

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `SelectedTouchpadIndex` | `int` | `0` | Which pad on the active device the Touchpad group edits (0..`MaxTouchpadIndex`-1). Changing it reloads VM fields from the matching `TouchpadSettings` entry. |
| `MaxTouchpadIndex` | `int` | `1` | Touchpad count on the active device (`0` when none). Private setter. |
| `HasMultipleTouchpads` | `bool` | - | Computed: `MaxTouchpadIndex > 1`. Shows the pad pivot. |
| `TouchpadIndexOptions` | `IEnumerable<int>` | - | `0..MaxTouchpadIndex-1` for the pivot ComboBox. |

**Detection card:**

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TouchpadGesturesEnabled` | `bool` | `false` | Master switch for the touchpad gestures. |
| `TouchpadGestureMode` | `string` | `"Both"` | `"InBoxOnly"` / `"CustomOnly"` / `"Both"`. |
| `TouchpadInBoxSectionEnabled` | `bool` | - | Computed: master on and mode isn't CustomOnly. Grays the In-Box card otherwise (#177/#178). |
| `TouchpadCustomSectionEnabled` | `bool` | - | Computed: master on and mode isn't InBoxOnly. |
| `TouchpadCooldownMs` | `int` | `100` | Minimum gap between recognized gestures (0–5000). |

**In-box gestures card:**

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TouchpadSwipeDistanceThreshold` | `double` | `0.15` | Swipe distance, fraction of pad (0.01–1.0). |
| `TouchpadSwipeTimeWindowMs` | `int` | `500` | Swipe time window (50–5000). |
| `TouchpadEnableFourWaySwipes` | `bool` | `false` | 4-direction swipes. |
| `TouchpadEnableEightWaySwipes` | `bool` | `false` | 8-direction swipes. |
| `TouchpadEnableRadialZones` | `bool` | `false` | Radial-menu zones. |
| `TouchpadRadialZoneCount` | `int` | `8` | Zone count, snapped to one of `4` / `6` / `8` / `12`. |
| `TouchpadRadialZoneCountOptions` | `IReadOnlyList<int>` | `{4,6,8,12}` | Static dropdown choices. |
| `TouchpadRadialCenterDeadzone` | `double` | `0.30` | Center dead radius (0.0–0.9). |
| `TouchpadEnableTouchSpots` | `bool` | `false` | Fixed touch-spot regions. |
| `TouchpadEnableTaps` | `bool` | `false` | Tap / multi-tap recognition. |
| `TouchpadTapTimeWindowMs` | `int` | `350` | Single-tap window (30–1000). |
| `TouchpadMultiTapGapMs` | `int` | `300` | Gap between taps in a multi-tap (50–2000). |
| `TouchpadEnableLongPress` | `bool` | `false` | Long-press recognition. |
| `TouchpadLongPressTimeWindowMs` | `int` | `500` | Long-press hold time (100–5000). |
| `TouchpadEnableTwoFingerSwipes` | `bool` | `false` | Two-finger swipes. |
| `TouchpadEnablePinchSpread` | `bool` | `false` | Pinch / spread. |
| `TouchpadEnableRotate` | `bool` | `false` | Two-finger rotate. |
| `TouchpadEnableThreeFingerGestures` | `bool` | `false` | Three-finger gestures. |
| `TouchpadEnableFourFingerGestures` | `bool` | `false` | Four-finger gestures. |
| `TouchpadEnableFiveFingerGestures` | `bool` | `false` | Five-finger gestures. |
| `TouchpadEnableShapeGestures` | `bool` | `false` | Shape-recognizer gestures. |
| `TouchpadGestureMatchThreshold` | `double` | `3.0` | Shape-recognizer match threshold, lower = stricter (0.1–10.0). $Q scale. |

**Joystick / D-pad output card:**

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TouchpadEnableJoystickOutput` | `bool` | `false` | Drive a stick / D-pad from finger position. |
| `TouchpadJoystickMaxRadius` | `double` | `0.30` | Finger travel mapped to full deflection (0.05–0.5). |
| `TouchpadJoystickInnerDeadzone` | `double` | `0.02` | Center dead radius (0.0–0.10). |
| `TouchpadJoystickDPadMode` | `string` | `"FourWay"` | `"Off"` / `"FourWay"` / `"EightWay"`. |
| `TouchpadJoystickDPadActivationThreshold` | `double` | `0.15` | Travel before a D-pad direction fires (0.05–0.5). |

**Mouse output card (touchpad-as-mouse tuning):**

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TouchpadMouseSensitivityX` | `double` | `1.0` | X sensitivity (0.05–10.0). |
| `TouchpadMouseSensitivityY` | `double` | `1.0` | Y sensitivity (0.05–10.0). |
| `TouchpadMouseInvertX` | `bool` | `false` | Invert X. |
| `TouchpadMouseInvertY` | `bool` | `false` | Invert Y. |
| `TouchpadMouseMomentum` | `bool` | `false` | Keep the cursor gliding after the finger lifts. |
| `TouchpadMouseMomentumDecay` | `double` | `0.90` | Per-tick momentum decay (0.80–1.00). Higher glides longer. |
| `TouchpadMomentumMaxSpeed` | `double` | `0` | Fling launch ceiling in pad widths per second (0–30). `0` = no ceiling. |
| `TouchpadMomentumMinLift` | `double` | `0.286` | Lift-velocity gate below which no fling starts (0–2). The old hardcoded value. |
| `TouchpadMomentumFlingGain` | `double` | `1.0` | Launch-speed multiplier (0.1–5.0). Leaves drag speed alone. |
| `TouchpadMomentumStacking` | `bool` | `false` | Whether a new fling adds to an in-flight coast instead of replacing it. |
| `TouchpadPointerResponse` | `string` | `"Simple"` | `"Simple"` (flat multiplier) or `"Trackpad"` (the libinput pointer-acceleration port). Notifies `TouchpadPointerResponseIsSimple` / `TouchpadPointerResponseIsTrackpad`, which gate the two halves of the card. |
| `TouchpadTrackpadThreshold` | `double` | `130` | Trackpad-curve speed threshold in mm/s (20–600). |
| `TouchpadTrackpadPadWidthMm` | `double` | `69` | Physical pad width in mm the curve normalizes against (20–150). |
| `TouchpadMouseAcceleration` | `double` | `0` | Simple-response acceleration exponent (0.0–5.0). `0` is linear. |
| `TouchpadMouseJitterReduction` | `bool` | `true` | Suppress sub-pixel jitter at rest. |

**Recognizer tolerances:**

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TouchpadTapMaxMotion` | `double` | `0.04` | Travel a contact may drift and still count as a tap, as a fraction of the pad (0.01–0.30). |
| `TouchpadLongPressMaxMotion` | `double` | `0.05` | Same guard for a long press (0.01–0.30). |
| `TouchpadTwoFingerSwipeAngularTolerance` | `double` | `25` | How far apart, in degrees, two fingers may travel and still read as one swipe (5–90). |
| `TouchpadPinchThreshold` | `double` | `0.25` | Spread change that fires a pinch (0.05–1.00). |
| `TouchpadRotateThresholdDegrees` | `double` | `20` | Rotation that fires a two-finger rotate (5–90). |

**Pointer region card (#9):** the screen rectangle the "Touchpad N Pointer X/Y" absolute cursor sources map onto. The four values are authored together: touching any of them latches the region as user-authored, so a later default sweep leaves it alone.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TouchpadPointerRegionSizeX` | `double` | `1.0` | Region width as a fraction of the work area (0.05–3.0). `1.0` is Steam's 1:1 pad-to-screen map. |
| `TouchpadPointerRegionSizeY` | `double` | `1.0` | Region height (0.05–3.0). |
| `TouchpadPointerRegionCenterX` | `double` | `0.5` | Region center X in work-area fractions (0.0–1.0). |
| `TouchpadPointerRegionCenterY` | `double` | `0.5` | Region center Y (0.0–1.0). |

**Swipe haptics card (#219):**

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TouchpadSwipeHapticsEnabled` | `bool` | `false` | Short haptic ticks as the finger travels across this pad. |
| `TouchpadSwipeHapticsIntensity` | `double` | `0.5` | Tick intensity (0.0–1.0). |

**Custom gestures card:**

| Member | Type | Description |
|--------|------|-------------|
| `CustomTouchpadGestures` | `ObservableCollection<TouchpadCustomGestureItem>` | Profile-scoped custom gestures filtered by the active device's class. |
| `HasNoCustomTouchpadGestures` | `bool` | Computed: the collection is empty. Drives the placeholder text. |
| `RecordTouchpadGestureCommand` | `RelayCommand` | Raises `RecordTouchpadGestureRequested` with the active (device, pad) so the recorder dialog mirrors the right pad. |
| `DeleteTouchpadGestureCommand` | `RelayCommand<TouchpadCustomGestureItem>` | Raises `DeleteTouchpadGestureRequested` for the row. |

| Event | Args | Description |
|-------|------|-------------|
| `RecordTouchpadGestureRequested` | `RecordTouchpadGestureArgs` | Open the recorder dialog for (device, pad). |
| `DeleteTouchpadGestureRequested` | `TouchpadCustomGestureItem` | Delete a saved custom gesture. |

**Reset commands:** every setting row carries a `Reset<Property>Command` that restores its default above, plus per-card `ResetTouchpadDetectionCardCommand`, `ResetTouchpadInBoxCardCommand`, `ResetTouchpadJoystickCardCommand`, `ResetTouchpadMouseCardCommand`, `ResetTouchpadPointerCardCommand`, `ResetTouchpadSwipeHapticsCardCommand`, and `ResetTouchpadSyntheticPressureCardCommand`. Defaults mirror `TouchpadGestureSettings.Default()`, so Reset to Defaults round-trips the group by construction.

| Method | Description |
|--------|-------------|
| `LoadTouchpadGestureSettingsForActiveDevice()` | Reads the per-(device, pad) entry into VM fields under the load guard so setters don't ping-pong back. |
| `SyncTouchpadGestureSettingsToActiveDevice()` | Writes VM fields into the entry, creating it on first touch. No-op while loading, which stops an external `PropertyChanged` caller from clobbering not-yet-loaded fields. |
| `RecomputeTouchpadCountForActiveDevice(int)` | Sets `MaxTouchpadIndex` from the active device. `0` hides the Touchpad group. |
| `RefreshCustomTouchpadGestures(IEnumerable<TouchpadCustomGesture>)` | Repopulates `CustomTouchpadGestures` after a profile load / switch. Pass null to clear. |

`RecordTouchpadGestureArgs` (device GUID, name, pad index) and `TouchpadCustomGestureItem` (display wrapper over a `TouchpadCustomGesture` with `Name`, `FingerCount`, `Summary`) are declared alongside the partial.

### Mouse Gestures (#200)

**File:** `PadViewModel.Mouse.cs`

Per-(slot, device) mouse-gesture settings. Twin of the Touchpad partial's Load/Sync/guard pattern. Persistence rides setter-time writes into the live PadSetting plus MainWindow's `PropertyChanged` hook. The 30 Hz VM flush does not carry these fields.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `MouseGesturesEnabled` | `bool` | `false` | Mouse-gesture recognizer armed for the active mouse device. |
| `MouseGestureButtons` | `int` | `8` (`1 << 3`, X1) | Bitmask of buttons arming the recognizer: bit 0 Left, bit 1 Middle, bit 2 Right, bit 3 X1, bit 4 X2, bit 5 Custom (#216, armed by the recorded cross-device input below instead of a mouse button). Masked to `0x3F`. |
| `MouseGestureButtonLeft` / `Middle` / `Right` / `X1` / `X2` / `Custom` | `bool` | - | Per-bit wrappers over `MouseGestureButtons` for the checkboxes. |
| `MouseGestureFlickThreshold` | `int` | `150` | Flick distance threshold in mouse counts. Clamped 10–5000. |
| `MouseGestureCooldownMs` | `int` | `100` | Minimum gap between recognized gestures (ms). Clamped 0–5000. |

**Custom activation input (#216).** The recorded cross-device descriptor + owning device GUID that arm the Custom gesture session while held. Same pair shape, picker projection, and record flow as the Gyro group's Aim Engage cluster, scoped per (slot, mouse device) with the rest of the card.

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `MouseGestureCustomEngageButton` | `string` | `""` | Recorded input descriptor. |
| `MouseGestureCustomEngageDeviceGuid` | `string` | `""` | Owning device GUID for the recorded input. |
| `MouseGestureCustomEngageSelectedInput` | `InputChoice` | `null` | Picker projection over the (descriptor, device) pair. Setting it writes both. `OnMouseGestureCustomEngageSelectedInputRefresh()` re-raises it after the choice list repopulates. |
| `MouseGestureCustomEngageRecording` | `bool` | `false` | Record in progress. Swaps `MouseGestureCustomEngageRecordButtonIcon` / `MouseGestureCustomEngageRecordButtonText`. |
| `MouseGestureCustomEngageRecordCommand` | `RelayCommand` | - | Raises `MouseGestureCustomEngageRecordRequested` so MainWindow runs the freeform recorder. |

**Reset commands:** `ResetMouseGesturesEnabledCommand`, `ResetMouseGestureButtonCommand`, `ResetMouseGestureFlickThresholdCommand`, `ResetMouseGestureCooldownCommand`, `ResetMouseGestureCustomEngageCommand` (clears the recorded pair), `ResetMouseGesturesCardCommand`.

| Method | Description |
|--------|-------------|
| `LoadMouseGestureSettingsForActiveDevice()` | Loads the active mouse device's gesture settings into the VM. Missing settings load as defaults, so Reset to Defaults resets these settings by construction. |
| `SyncMouseGestureSettingsToActiveDevice()` | Writes the VM fields into the active mouse device's entry, creating it on first touch. No-op while loading. |

### Force Feedback / Rumble

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `ForceOverallGain` | `int` | `100` | 0–100 | Overall FFB gain %. |
| `LeftMotorStrength` | `int` | `100` | 0–100 | Left motor strength %. |
| `RightMotorStrength` | `int` | `100` | 0–100 | Right motor strength %. |
| `SwapMotors` | `bool` | `false` | - | Swap left/right motor assignment. |
| `TriggerRumbleFold` | `bool` | `false` | - | Fold the game's trigger-motor channels into the body motors on devices without trigger motors (#271 item 2). |
| `RawLeftMotorDisplay` / `RawRightMotorDisplay` | `double` | `0` | 0–1 | The motor command the game put on the virtual pad, before any device's settings: the Force Feedback group's raw bar. |
| `DeviceLeftMotorDisplay` / `DeviceRightMotorDisplay` | `double` | `0` | 0–1 | The selected device's own motor activity, its gain, motor strengths, audio rumble and constant force applied to the slot's raw vibration: the group's output bar, so the gap between the two bars is the user's settings. |

**Wheel (per-device):**

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `WheelRotationRangeEnabled` | `bool` | `true` | - | Set Rotation Range. False leaves the range to the wheel and its own software, and no range is sent (#512). Persisted in `PadSetting.RotationRangeEnabled`, reset by its row and by the Wheel card's Reset All. |
| `WheelRotationRange` | `int` | `900` | `WheelRangeMinimum`–`WheelRangeMaximum` | Native wheel rotation range in degrees. The setter clamps to the bounds. |
| `WheelRangeMinimum` | `int` | `40` | - | The least range the loaded wheel takes. Read-only, set by `LoadWheelRotationRange`. |
| `WheelRangeMaximum` | `int` | `2520` | - | The greatest range the loaded wheel takes. Read-only, set by `LoadWheelRotationRange`. |
| `WheelAutoCenter` | `int` | `0` | 0–100 | Auto-center strength %. 0 is off. |
| `WheelRpmLeds` | `bool` | `false` | - | Drive the wheel's RPM / shift LEDs from game telemetry. |

`LoadWheelRotationRange(int degrees, (int Min, int Max)? limits)` loads a device's stored range with that device's wheel bounds (`WheelRangeLimits.For`), or 40–2520 when no native writer drives it (#512). The bounds change only here, with the values they belong to. See [Wheel Force Feedback Internals](wheel-ffb-internals.md#wheel-and-centering-card-settings).

**Audio Bass Rumble (per-device):**

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `AudioRumbleEnabled` | `bool` | `false` | - | Audio-driven rumble from system bass frequencies. |
| `AudioRumbleSensitivity` | `double` | `4.0` | 1–60 (`AudioBassDetector.MinSensitivity`, `MaxSensitivity`) | Bass detection sensitivity multiplier. |
| `AudioRumbleCutoffHz` | `double` | `80.0` | 20–2000 (`AudioBassDetector.MinCutoffHz`, `MaxCutoffHz`) | Low-pass cutoff (Hz) for bass extraction. |
| `AudioRumbleLeftMotor` | `int` | `100` | 0–100 | Left motor strength for audio rumble. |
| `AudioRumbleRightMotor` | `int` | `100` | 0–100 | Right motor strength for audio rumble. |
| `AudioRumbleLevelMeter` | `double` | `0` | - | Live audio bass level meter. |

**Reset commands:** `ResetForceAllCommand`, `ResetOverallGainCommand`, `ResetLeftMotorCommand`, `ResetRightMotorCommand`, `ResetAudioRumbleAllCommand`, `ResetAudioSensitivityCommand`, `ResetAudioCutoffCommand`, `ResetAudioLeftMotorCommand`, `ResetAudioRightMotorCommand`.

**Steering Angle Rumble (per-device):**

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `SteeringAngleRumbleEnabled` | `bool` | `false` | - | Turns the selected virtual stick axis into continuous rumble. |
| `SteeringAngleRumbleAxis` | `int` | `0` | 0–3 | Left Stick X, Left Stick Y, Right Stick X, Right Stick Y. |
| `SteeringAngleRumbleMotor` | `int` | `0` | 0–2 | Split by Direction, Left Motor, Right Motor (#510). The setter reads any other value as 0, as the engine does, so the picker shows what plays. |
| `SteeringAngleRumbleStrength` | `int` | `50` | 0–100 | Rumble at full travel, %. |
| `SteeringAngleRumbleDeadzone` | `int` | `2` | 0–25 | Travel around center that adds no rumble, %. |

**Reset commands:** the private `ResetSteeringAngleRumble()` puts the whole card back, run by `ResetForceAllCommand` and `ResetAllSettings`. Each row has its own: `ResetSteeringAngleRumbleEnabledCommand`, `ResetSteeringAngleRumbleAxisCommand`, `ResetSteeringAngleRumbleMotorCommand`, `ResetSteeringAngleRumbleStrengthCommand`, `ResetSteeringAngleRumbleDeadzoneCommand`.

**Constant Force (per-device, FFB-capable + scalar-rumble pads):**

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `ConstantForceEnabled` | `bool` | `false` | - | Apply a continuous force vector until toggled off. Resumes after game/macro forces stop. |
| `ConstantForceX` | `double` | `0` | −1.0–1.0 | X component of the force vector. |
| `ConstantForceY` | `double` | `0` | −1.0–1.0 | Y component (+ = up in the UI grid). |

### Audio Group Gates

| Member | Type | Description |
|--------|------|-------------|
| `SelectedDeviceHasHeadphoneJack` | `bool` | The selected device has a 3.5 mm jack PadForge drives the hardware volume and route of: a DualSense (`0x0CE6`), a DualSense Edge (`0x0DF2`), or a DualShock 4 over Bluetooth (`AudioPassthroughService.IsBluetoothDs4`), which writes its split left and right headphone bytes from the same Headphone Volume (#528). A DualShock 4 on USB plays through its own Windows endpoint, whose volume Windows keeps. |
| `SelectedDeviceHasOutputPath` | `bool` | Shows **Output Path** in the Audio group (#546): every pad with a headphone jack, and a DualShock 4 on USB with audio (a wired second model or a pad on Sony's adapter, `AudioPassthroughService.Ds4HasAudio`, never a peer's copy and never a `{00001124` Bluetooth path), whose Headphone Volume Windows keeps. Replaced `SelectedDeviceIsHeadsetOnly`. |
| `SelectedDeviceHasHeadsetAndSpeakerPath` | `bool` | **Headphones + Speaker** is offered: the DualSense family, and a DualShock 4 on USB through route 2 of feature report `0xE0` (#546). Over Bluetooth a DualShock 4 plays one or the other (target `0x02` or `0x24`), so the item is hidden there and its index stays in place, which keeps the stored enum's meaning (#528). |

### Audio DSP Chain (#347)

Audio group's surface over the per-device crossfeed / EQ / limiter fields on `DeviceSlotConfig` (see the DeviceSlotConfig section below). Lives in `PadViewModel.AudioDsp.cs`. The cards are gated on `SelectedDeviceHasDspChain`.

| Member | Type | Description |
|--------|------|-------------|
| `SelectedDeviceHasDspChain` | `bool` (computed, `PadViewModel.cs`) | True when the selected device is a Sony pad whose audio rides an `AudioPassthroughService` sink, the only place the chain runs: DualSense family, Sony's DS4 USB wireless adapter (PID 0BA0), a second-model DualShock 4 (PID 09CC) on a cable, or any DualShock 4 over Bluetooth (`AudioPassthroughService.Ds4HasAudio`). |
| `EqBands` | `ObservableCollection<EqBandVm>` | Grid rows decoded from `DeviceSlotConfig.AudioEqBands`. Every row edit re-encodes the whole list back into the config (`PushEqBands`). |
| `RefreshEqBands()` | method | Rebuilds the rows from the selected device's config on every device switch and clears the import status. |
| `AddEqBandCommand` / `RemoveEqBandCommand` / `ClearEqBandsCommand` | `RelayCommand` (`RemoveEqBandCommand` takes the `EqBandVm` row) | Add a default band, remove one row, or clear the list. Each pushes the encoded list. |
| `ImportAutoEqFileCommand` | `RelayCommand` | Open-file dialog for an AutoEq `ParametricEQ.txt` / `FixedBandEQ.txt` and apply its Filter lines plus preamp. |
| `ImportAutoEqCommand` | `RelayCommand` | Same parse over the clipboard text. |
| `EqImportStatus` / `HasEqImportStatus` | `string` / `bool` | What the last import did, shown under the buttons. A Graphic EQ file with no Filter lines says so instead of silently doing nothing. |
| `ResetCrossfeedCommand` | `RelayCommand` | `AudioCrossfeedLevel` back to 0. |
| `ResetCrossfeedCutCommand` / `ResetCrossfeedFeedCommand` | `RelayCommand` | Custom knobs back to libbs2b's own defaults, 700 Hz and 4.5 dB. |
| `ResetEqPreampCommand` | `RelayCommand` | `AudioEqPreampDb` back to 0. |
| `ResetEqCommand` | `RelayCommand` | EQ off, preamp 0, bands cleared. |
| `ResetLimiterCommand` / `ResetLimiterCeilingCommand` | `RelayCommand` | Limiter back on, ceiling back to 98. |

**EqBandVm** (one editable row, `ObservableObject`): `Enabled`, `Type` (`EqBandType`: Peaking, LowShelf, HighShelf, HighPass, LowPass, Notch), `FrequencyHz` (clamped 10 to `EqBand.MaxFrequencyHz()`), `GainDb` (clamped −30..30), `Q` (clamped 0.05..20). Clamps match the engine's so the grid never accepts a band the DSP would silently reject.

### Impulse Triggers (3.2)

Per-pad-per-slot per-trigger-motor effects. The group shows only when the selected device reports `HasRumbleTriggers`: SDL's `SDL_PROP_JOYSTICK_CAP_TRIGGER_RUMBLE_BOOLEAN` or a Microsoft impulse-trigger PID (`XboxControllerIdentity.IsImpulseTriggerDevice`). Xbox One and later pads.

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `ImpulseOverallGain` | `int` | `100` | 0–100 | Master scale for the trigger-motor pipeline. |
| `ImpulseLeftStrength` | `int` | `100` | 0–100 | Left trigger motor scale. |
| `ImpulseRightStrength` | `int` | `100` | 0–100 | Right trigger motor scale. |
| `ImpulseSwapTriggers` | `bool` | `false` | - | Swap left/right trigger motor assignment. |
| `AtVibrationToImpulse` | `bool` | `false` | - | Render vibration-class DualSense adaptive-trigger programs on the impulse motors (#271 item 3). Resistance-class programs are ignored. |

**Constant Trigger Force:**

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `ConstantTriggerForceEnabled` | `bool` | `false` | - | Override-with-resume continuous force on the trigger motors. |
| `ConstantTriggerForceLeft` | `double` | `0` | 0.0–1.0 | Left trigger steady force. |
| `ConstantTriggerForceRight` | `double` | `0` | 0.0–1.0 | Right trigger steady force. |

**Audio Bass Trigger Rumble:**

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `AudioRumbleTriggersEnabled` | `bool` | `false` | - | Drive trigger motors from system audio bass. Runs alongside the body-motor audio rumble. |
| `AudioRumbleTriggersSensitivity` | `double` | `4.0` | 1–60 | Bass intensity multiplier (trigger channel). |
| `AudioRumbleTriggersCutoffHz` | `double` | `80.0` | 20–2000 | Low-pass cutoff (trigger channel). |
| `AudioRumbleLeftTrigger` | `int` | `100` | 0–100 | Audio-driven left-trigger motor scale. |
| `AudioRumbleRightTrigger` | `int` | `100` | 0–100 | Audio-driven right-trigger motor scale. |
| `AudioRumbleTriggersLevelMeter` | `double` | `0` | - | Live trigger-channel level. |

| Event | Args | Description |
|-------|------|-------------|
| `TestLeftImpulseTriggerRequested` | `EventArgs` | Per-device test pulse on the left trigger motor. |
| `TestRightImpulseTriggerRequested` | `EventArgs` | Per-device test pulse on the right trigger motor. |

### Gyro Engage Stick Gate (#120)

Per-direction stick gate for Easy-Aim gyro engagement. Both persist per device and reset to their defaults when the value is empty, so old profiles keep their original right-stick-radial behavior.

| Property | Type | Default | Values | Description |
|----------|------|---------|--------|-------------|
| `GyroEngageStickSide` | `string` | `"Right"` | `Right`, `Left`, `Either` | Which stick's deflection drives the Easy-Aim threshold gate. `Either` uses the larger of the two. Empty collapses to `"Right"`. |
| `GyroEngageStickDirection` | `string` | `"Full"` | `Full`, `X`, `Y`, `XNeg`, `XPos`, `YNeg`, `YPos` | Which component of the engage stick(s) drives the gate. `Full` is radial. Empty collapses to `"Full"`. |

| Command | Description |
|---------|-------------|
| `ResetGyroEngageStickSideCommand` | Resets `GyroEngageStickSide` to `"Right"`. |
| `ResetGyroEngageStickDirectionCommand` | Resets `GyroEngageStickDirection` to `"Full"`. |

### Motion Space and Grip (#392)

Both store the canonical English identifier, not the localized label, so `PadForge.xml` round-trips across a language change. Both are per (slot, device).

| Property | Type | Default | Values | Description |
|----------|------|---------|--------|-------------|
| `GyroSpace` | `string` | `"Local"` | `Local`, `Player`, `World` | Gyro reference frame. Empty collapses to `"Local"`. |
| `GyroSpaceOptions` | `IReadOnlyList<GyroLabeledOption>` | - | - | Display-label / stored-value pairs for the space dropdown. |
| `MotionGrip` | `string` | `"Pointing"` | `Pointing`, `Sideways`, `WiiWheel`, `Upright` | How the controller is held. Empty collapses to `"Pointing"`. |
| `MotionGripOptions` | `IReadOnlyList<GyroLabeledOption>` | - | - | Display-label / stored-value pairs for the grip dropdown, in that order. |
| `IsLoadingPadSetting` | `bool` | `false` | - | True while `InputService.LoadPadSettingIntoViewModel` mirrors a `PadSetting` into this VM. A plain field with no change notification: it is a scope marker, not a bound property. |

**Reset commands:** `ResetGyroSpaceCommand` (back to `"Local"`), `ResetMotionGripCommand` (back to `"Pointing"`).

Changing the grip re-references the motion state of the one device the page is editing: its gravity estimate, shake envelope, and lean and tilt neutrals are in the old frame. MainWindow's `MotionGrip` `PropertyChanged` handler gates that on `InputService.ShouldRecenterOnGripChange`, which is `!IsLoadingPadSetting`. A grip write arriving through a `PadSetting` load is a mirror of stored state, not a change of hold, so a device selection or a profile switch must not drop every device's estimate on the slot. The recenter itself is `InputService.RecenterMotionForSelectedDevice`. The Gyro Recenter macro's pad-wide drop is a separate path (`InputManager.GyroRecenterApply`).

### Pitch and Roll Simulation (#474)

Per (slot, device). The card shows only for a DualShock 3 with both sensors.

| Property | Type | Default | Values | Description |
|----------|------|---------|--------|-------------|
| `GyroSimulation` | `bool` | `false` | - | Fills pitch and roll from the accelerometer. |
| `GyroSimulationSmoothingMs` | `double` | `100` | 20 to 250 | The smoothing time constant. The setter clamps, and a value that is not finite (NaN or infinity) becomes 100. |

**Reset commands:** `ResetGyroSimulationCommand` (off), `ResetGyroSimulationSmoothingCommand` (back to 100), `ResetGyroSimulationCardCommand` (both).

### Gyro Tilt Envelope (#292)

Per-(slot, device) lens over the "Gyro Tilt X/Y" sources, the same shape as Flick Stick below. The save pipeline stamps these onto every tilt source (`ApplyGyroTiltParamsToRow`, the Motion Steering push pattern) and persists them in the PadSetting extended-mapping bag under `GyroTilt*` keys.

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `GyroTiltRangeDeg` | `double` | `25` | 1–90 | Physical tilt in degrees that reaches full deflection. 25 is the modal Steam-corpus maximum. The cap is 90 because the angle comes from an arc sine of one gravity component, so a wider range never reaches full deflection. |
| `GyroTiltInnerDz` | `double` | `0` | 0–89 | Inner tilt deadzone in degrees. |

**Reset commands:** `ResetGyroTiltRangeCommand`, `ResetGyroTiltInnerCommand`, and the card-level `ResetGyroTiltAllCommand`.

### Flick Stick (#225)

Per-(slot, device) lens over the "Flick Stick ..." sources in the slot's KBM mapping set. The save pipeline stamps these onto every flick source (`ApplyFlickStickParamsToRow`, the Motion Steering push pattern) and persists them in the PadSetting extended-mapping bag (`FlickStick*` keys). Defaults mirror the `MappingSource` `ParamFlick*` defaults (JSM-grounded).

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `FlickCountsPer360` | `double` | `14400` | 100–100000 | Mouse counts per full 360° camera turn (Steam "Dots Per 360°"). |
| `FlickTime` | `double` | `0.1` | 0.01–2.0 | Flick easing duration in seconds for a full 180° flick. |
| `FlickThreshold` | `double` | `0.9` | 0.1–1.0 | Stick deflection (raw magnitude) at which a flick engages. |
| `FlickSnapMode` | `string` | `"None"` | `None` / `Forward` / `Half` / `Four` / `Sixths` / `Eight` | Snap interval, Tag-backed combo string (the `GyroEngageStickSide` pattern). Value set = `SourceKindRuntime.FlickSnapIntervalRad`'s. |
| `FlickSnapStrength` | `double` | `1.0` | 0.0–1.0 | Snap lerp strength. 1.0 = full snap to the interval. |
| `FlickForwardDeadzone` | `double` | `0` | 0–180 | Forward angle deadzone in degrees: a flick within this of dead-ahead reads as 0°. |
| `FlickSmoothing` | `double` | `-1` | −1.0 to 0.5 | Rotation smoothing threshold in rad/tick. Negative = automatic tiered window, 0 = off, positive = explicit lower threshold. |
| `FlickRotationOffset` | `double` | `0` | −180 to 180 | Steam's flick-stick rotation in degrees: the whole input map turns, so the offset lands on the flick angle before snapping. |
| `FlickOnEngage` | `bool` | `false` | - | Fire a flick immediately when evaluation starts with the stick already past threshold (the shift-layer engage case). Off arms at the current angle and only tracks rotation. |

**Reset commands:** one per row (`ResetFlickCountsPer360Command`, `ResetFlickTimeCommand`, `ResetFlickThresholdCommand`, `ResetFlickSnapModeCommand`, `ResetFlickSnapStrengthCommand`, `ResetFlickForwardDeadzoneCommand`, `ResetFlickSmoothingCommand`, `ResetFlickRotationOffsetCommand`, `ResetFlickOnEngageCommand`) plus the card-level `ResetFlickStickCardCommand`.

### Deadzone Settings

**Left Stick:**

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `LeftDeadZoneShape` | `int` | `2` (ScaledRadial) | 0–5 | Deadzone shape index. |
| `LeftDeadZoneX` | `double` | `0` | 0–100 | X deadzone %. |
| `LeftDeadZoneY` | `double` | `0` | 0–100 | Y deadzone %. |
| `LeftAntiDeadZoneX` | `double` | `0` | 0–100 | X anti-deadzone %. |
| `LeftAntiDeadZoneY` | `double` | `0` | 0–100 | Y anti-deadzone %. |
| `LeftLinear` | `double` | `0` | 0–100 | Linear interpolation factor. |
| `LeftMaxRangeX` | `double` | `100` | 1–100 | X max range (positive). |
| `LeftMaxRangeY` | `double` | `100` | 1–100 | Y max range (positive). |
| `LeftMaxRangeXNeg` | `double` | `100` | 1–100 | X max range (negative). |
| `LeftMaxRangeYNeg` | `double` | `100` | 1–100 | Y max range (negative). |
| `LeftCenterOffsetX` | `double` | `0` | −100 to 100 | X center offset %. |
| `LeftCenterOffsetY` | `double` | `0` | −100 to 100 | Y center offset %. |

**Right Stick:** Same pattern with `Right` prefix: `RightDeadZoneShape`, `RightDeadZoneX`, `RightDeadZoneY`, `RightAntiDeadZoneX`, `RightAntiDeadZoneY`, `RightLinear`, `RightMaxRangeX`, `RightMaxRangeY`, `RightMaxRangeXNeg`, `RightMaxRangeYNeg`, `RightCenterOffsetX`, `RightCenterOffsetY`.

**Backward compat shims:** `LeftDeadZone` (get=`LeftDeadZoneX`, set=both X+Y), `RightDeadZone` (same pattern).

**Speed and momentum mirrors:** `LeftStickSensitivity` / `RightStickSensitivity` (`1.0`, clamped 0.1–5.0) carry the flat speed multiplier the KBM pointer sticks use, and `KbmMouseMomentum` (`false`) / `KbmMouseMomentumGlide` (`0.90`, clamped 0.80–1.00) carry the stick trackball (#291) for the KBM mouse stick. `SyncStickItemFromVm` pushes them into the matching [StickConfigItem](#stickconfigitem).

**Sensitivity Curves (serialized control point strings, `"x,y;x,y;..."` format):**

| Property | Default | Description |
|----------|---------|-------------|
| `LeftSensitivityCurveX` | `"0,0;1,1"` | Left stick X sensitivity curve. |
| `LeftSensitivityCurveY` | `"0,0;1,1"` | Left stick Y sensitivity curve. |
| `RightSensitivityCurveX` | `"0,0;1,1"` | Right stick X sensitivity curve. |
| `RightSensitivityCurveY` | `"0,0;1,1"` | Right stick Y sensitivity curve. |
| `LeftTriggerSensitivityCurve` | `"0,0;1,1"` | Left trigger sensitivity curve. |
| `RightTriggerSensitivityCurve` | `"0,0;1,1"` | Right trigger sensitivity curve. |

**Triggers:**

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `LeftTriggerDeadZone` | `double` | `0` | 0–100 | Left trigger deadzone %. |
| `RightTriggerDeadZone` | `double` | `0` | 0–100 | Right trigger deadzone %. |
| `LeftTriggerAntiDeadZone` | `double` | `0` | 0–100 | Left trigger anti-deadzone %. |
| `RightTriggerAntiDeadZone` | `double` | `0` | 0–100 | Right trigger anti-deadzone %. |
| `LeftTriggerMaxRange` | `double` | `100` | 1–100 | Left trigger max range %. |
| `RightTriggerMaxRange` | `double` | `100` | 1–100 | Right trigger max range %. |

### Dynamic Stick/Trigger Config Items

Drive the `ItemsControl`-based Sticks and Triggers groups. Gamepad presets: 2 sticks, 2 triggers. Custom Extended: N sticks, M triggers. KBM: 2 stick items (Mouse Movement, Scroll Wheel) and no triggers. VR: none of either.

| Property | Type | Description |
|----------|------|-------------|
| `StickConfigs` | `ObservableCollection<StickConfigItem>` | Stick config items. Rebuilt by `RebuildStickConfigs()`. |
| `TriggerConfigs` | `ObservableCollection<TriggerConfigItem>` | Trigger config items. Rebuilt by `RebuildTriggerConfigs()`. |

| Method | Description |
|--------|-------------|
| `RebuildStickConfigs()` | Rebuilds stick configs for current output type. A VR slot gets none. |
| `RebuildTriggerConfigs()` | Rebuilds trigger configs. KBM and VR have none. |
| `SyncStickItemFromVm(StickConfigItem)` | Pushes VM deadzone properties into a stick item. |
| `SyncTriggerItemFromVm(TriggerConfigItem)` | Pushes VM trigger properties into a trigger item. |
| `SyncAllConfigItemsFromVm()` | Syncs all items from VM. Called after settings load/paste. |
| `ResetAllSettings()` | Resets per-slot settings to defaults. Called on slot deletion and by Reset to Defaults. |

### Macros

| Property | Type | Description |
|----------|------|-------------|
| `Macros` | `ObservableCollection<MacroItem>` | Macros for this slot. |
| `SelectedMacro` | `MacroItem` | Selected macro. Notifies `HasSelectedMacro`, refreshes remove command. |
| `HasSelectedMacro` | `bool` | Computed: `SelectedMacro != null`. |

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `AddMacroCommand` | always | Adds a new macro named by `Macro_Default_Format` ("Macro {0}", the next number), with the slot's derived `ButtonStyle`, `RawProfileId` and `CarriesPressure` (#530), selects it and shows the Macros part of Macros & Menus. The other macro and menu commands (`DuplicateMacroCommand`, `PasteMacroCommand`, `CopyMacroFromCommand`, `AddMenuCommand`, `DuplicateMenuCommand`) show their part the same way (`ShowMacrosPart`). |
| `RemoveMacroCommand` | `HasSelectedMacro` | Removes the selected macro, then selects the last remaining one. |
| `DuplicateMacroCommand` | `HasSelectedMacro` | Clones the selected macro within the slot (#112) by round-tripping it through the macro DTO, so it is a deep copy and the runtime-only execution state drops away. A macro mid-fire keeps firing. The clone starts cold. |
| `CopyMacroCommand` | `HasSelectedMacro` | Raises `CopyMacroRequested`. MainWindow owns the clipboard. |
| `PasteMacroCommand` | always | Raises `PasteMacroRequested`. |
| `CopyMacroFromCommand` | always | Raises `CopyMacroFromRequested`: pull macros from another virtual controller, mirroring the mapping list's Copy From. MainWindow shows the picker and does the copy. |

**Action-type picker.** The editor's type dropdown binds `MacroTypeCatalog.View`, a grouped `ICollectionView` over `MacroTypeCatalog.Choices` keyed on `MacroTypeChoice.Category`. Each `MacroTypeChoice` carries the `MacroActionType`, a localized `Label`, the localized `Category` header, and an optional `Tooltip`, and equals another by `Type`, so a box finds its pick in a list made again. The picker was fifty-six flat entries in enum-history order. The catalog orders them by what they act on, under eleven headers: Virtual Buttons, Virtual Axes & Wheel, Keyboard & Text, Mouse, Timing & Flow, Rumble, Lightbar & LEDs, Sound & Volume, Motion & Pointer, Layers & Overlays, and System & Apps. A census test pins that every enum member appears exactly once, so a new action type cannot ship without choosing its shelf. The catalog holds one list instance for its lifetime and refills it in place on `Strings.CultureChanged`, then refreshes the view: a fresh list per culture would strand the `x:Static`-bound view on the old one.

### Bass Shakers (#236)

The per-slot Bass Shakers group's surface, MappingSet-backed like Menus and persisted through the same dirty callback. `RumbleAudioTabVisible` gates the group on slot type: Xbox, PlayStation, and Nintendo always, plus Extended slots whose surface carries force feedback. With Customize on, the ForceFeedbackEnabled checkbox decides. With Customize off, the catalog profile descriptor must carry a PID FFB block, except the `steam-deck-composite` persona, whose vendor feedback PadForge decodes without one. The card binds `RumbleAudioEnabled`, `RumbleAudioEndpointId` (output device picker), `RumbleAudioChannelMode` (Mono / Controller Stereo), `RumbleAudioMasterGain`, and `RumbleAudioVoices`, an `ObservableCollection` of the four per-channel voice rows (Low Motor, High Motor, Left Trigger, Right Trigger: enable, 20–120 Hz frequency, gain, per-voice Test). The frequency sweep and Stop live beside the voices. Everything writes into `MappingSet.RumbleAudio` (`RumbleAudioConfig`), so the routing travels with profiles and Copy / Paste.

### Output Cards: Slot SOCD (#245) and Keep Controller Awake

Both cards stand under the picture in the first section (`FirstSectionName`: Mappings on a gamepad slot) (`OutputTabIndex` 17, `ShowOutputGroup`). `OutputTabVisible` is a slot-type gate: every type except MIDI and VR, the two with no output-behavior surface at all.

Controller-button SOCD is distinct from `KbmSlotConfig`'s key SOCD (#205). `SocdCardVisible` and `KbmSocdCardVisible` are mutually exclusive by slot type. On a Keyboard + Mouse slot, `KbmSocdEditorVisible` also hides the key-pair editor while the slot's keyboard half is off (#408). The card binds `SocdMode` over `MappingSet.SocdMode` (`AvailableSlotSocdModes`, in dropdown order: Off / Last Wins / Neutral / First Wins), and `SocdPairItems` (`SlotSocdPairItem`) edits the opposing button pairs from `SocdButtonOptions`. `SocdUsesRawIndices` says which pair grammar the slot stores: Extended and Nintendo slots write flat raw indices (`"12:13"`), Xbox and PlayStation slots write the `WriteBoolTarget` names, mirroring the engine's own raw-surface gate. The engine applies the cleaning to the combined output right before submit, on both the Gamepad bitmap and the raw-HID button words.

Keep Controller Awake holds a stick off-center so a console-style pad never idles out. Like the Bass Shakers config, it lives on the slot's `MappingSet` and every setter fires `ConfigItemDirtyCallback`.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `KeepAwakeCardVisible` | `bool` | - | Computed: Xbox and PlayStation slots only. |
| `KeepAwakeEnabled` | `bool` | `false` | Card master switch, over `MappingSet.KeepAwakeEnabled`. |
| `KeepAwakeMotion` | `bool` | `false` | Sweep the hold instead of parking it, over `MappingSet.KeepAwakeMotion`. For titles that gate vibration on the stick moving rather than on where it sits. |
| `KeepAwakeAxis` | `string` | `"LX"` | Held axis, locale-stable: `LX`, `LY`, `RX`, `RY`. The default is stored as an empty string, so the getter substitutes `"LX"`. |
| `AvailableKeepAwakeAxes` | `IReadOnlyList<GyroLabeledOption>` | - | Axis picker options, reusing the stick-axis strings the mapping grid already localizes. |
| `KeepAwakeDeflection` | `int` | `25` | Held deflection percent, clamped 1–90. A persisted `0` means unset and reads as the engine default 25, so the card always shows the effective number. |

| Command | Description |
|---------|-------------|
| `ResetKeepAwakeEnabledCommand` | Card switch back off. |
| `ResetKeepAwakeMotionCommand` | Sweep back off. |
| `ResetKeepAwakeAxisCommand` | Back to `"LX"`. |
| `ResetKeepAwakeDeflectionCommand` | Back to 25. |
| `ResetKeepAwakeCardCommand` | Disabled, sweep off, axis and deflection back to their unset defaults, then `ReloadKeepAwake()`. |

| Method | Description |
|--------|-------------|
| `ReloadKeepAwake()` | Re-raises the whole card off the live `MappingSet`. Called on profile apply and output-type change. |

### Menus (#9)

Radial / touch menus for this slot. Slot-level like Macros: the collection wraps the LIVE `MenuDefinitionEntry` list on the slot's `MappingSet` (write-through), and every edit fires `ConfigItemDirtyCallback` so the autosave path persists the set. Rows are [MenuEditorItem](#menueditoritem) instances.

| Property | Type | Description |
|----------|------|-------------|
| `Menus` | `ObservableCollection<MenuEditorItem>` | Menus configured for this pad slot. |
| `SelectedMenu` | `MenuEditorItem` | Selected menu. Notifies `HasSelectedMenu`, refreshes the remove / duplicate commands. |
| `HasSelectedMenu` | `bool` | Computed: `SelectedMenu != null`. |

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `AddMenuCommand` | always | Adds a new entry to the slot set with the next free `MenuId` and an auto-numbered name. |
| `RemoveMenuCommand` | `HasSelectedMenu` | Removes the selected menu from the slot set. |
| `DuplicateMenuCommand` | `HasSelectedMenu` | Clones the selected entry under the next free `MenuId` with a "(Copy)"-suffixed name. |
| `MenuHostRecordCommand` | always | Calls `SelectedMenu.PrepareRecord(Host)`, then raises `MenuHostRecordRequested`. |
| `MenuRecordTargetCommand` | always | `RelayCommand<string>`. The same freeform recorder aimed by parameter, parsed as a `MenuRecordTarget`: `"CustomX"`, `"CustomY"`, `"Click"` for the Custom opener, and `"HotbarShow"`, `"HotbarPrevious"`, `"HotbarNext"`, `"HotbarFire"` for a Hotbar's four controls. |
| `MenuKeyboardRecordCommand` | always | `RelayCommand<KeyboardInputRow>` (`PadViewModel.Keyboard.cs`). Raises `MenuKeyboardRecordRequested` for one Keyboard Controls row. A null row or no `SelectedMenu` does nothing. |
| `MenuKeyboardMapAllCommand` | always | Raises `MenuKeyboardMapAllRequested` when the selected menu is a Keyboard, else does nothing. |

| Callback | Description |
|----------|-------------|
| `MenusStructureChanged` | `Action`, wired by MainWindow to `InputService.RefreshAvailableInputsForSlot`. Fired on a structural edit (add / remove / duplicate, kind, cell count, center cell, enabled) that changes which "Menu N Item K" descriptors exist, so the mapping and macro pickers stop offering stale entries. Label and name typing must not fire it. |

| Event | Description |
|-------|-------------|
| `MenuKeyboardRecordRequested` | `KeyboardInputRow`. A keyboard row's record button: `MainWindow` records a press for it, or stops the recording it has (`MainWindow.RecordKeyboardRow`). |
| `MenuKeyboardMapAllRequested` | Map All on the Keyboard Controls card: `MainWindow` records each control in turn, or stops. |
| `MenuHostRecordRequested` | Record button on the menu host picker. MainWindow runs the freeform recorder and folds the recorded descriptor onto a host choice (`MenuEditorItem.TryApplyRecordedHost`), the Aim Engage record shape. |

| Method | Description |
|--------|-------------|
| `KbmSlotChoicesProvider` / `KbmSlotChoices()` / `IsKeyboardMouseSlot` | Internal. The Keyboard + Mouse slots a keyboard menu can type through, supplied by `MainViewModel.KeyboardMouseSlots` (a pad holds the delegate rather than a static, which would keep a main view model alive), and whether this slot is one. Each menu row's `KbmSlotsProvider` is set to `KbmSlotChoices`. |
| `DescribeSlotInput(descriptor, deviceGuid)` | Internal. The name the slot's input lists give an input on a device: that device's entry, else any entry of the input, else the descriptor. An axis half carries the `I` or `H` prefix, which no entry does, so its base input is looked up and its direction (`+` or `-`) added. |
| `ReloadMenus()` | Rebuilds `Menus` from the slot's live `MappingSet` and selects the first entry. Called from `RebuildMappings()`, so profile applies, Workshop imports, output-type changes, and Reset to Defaults all refresh the group. |

**Slot context stamped onto every row.** `ApplyMenuButtonStyle` runs on each item at reload, add, duplicate, and whenever the slot's macro button style is re-derived. It sets `ButtonStyle` from `MacroButtonNames.DeriveStyle(OutputType)`, `RawButtonCount` (the Extended / Nintendo `ExtendedConfig.ButtonCount`, else 11), `RawProfileId`, and `SupportsControllerButtons`, true on Xbox, PlayStation, Nintendo and Extended only. A MIDI or Keyboard+Mouse output cannot press a controller button, so its cells omit the choice rather than offering it with a warning. It also hands the row five providers: `DescriptorDisplayProvider`, `InputChoicesProvider` (the slot's `SlotAvailableInputs`), `RowBoundProvider`, `LayerChoicesProvider` (the slot's `MacroLayerChoices`, for the #413 layer gate), and, for the #390 macro cells, `MacroNamesProvider`, which lists this slot's macro names live. Two callbacks ride along: `StructureChanged` fires `MenusStructureChanged`, and `RuntimeEdit` routes an edit through `InputService.TryEditMenuConfiguration`.

**Macro renames follow their cells.** `MacroItem.Renamed` is a static hook each pad VM subscribes to once. A rename on this slot retags every menu cell that referenced the old name, matched case-insensitively, which is the comparer the menu runtime itself uses.

### Active Config Tab

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `SelectedConfigTab` | `int` | `0` | The selected group, by its old tab number: 0 Picture (the `TabController` segment, `Pad_View_Picture`), 1 Macros, 2 List (`TabMappings`, `Pad_View_List`), 3 Sticks, 4 Triggers, 5 Force Feedback, 6 Adaptive Triggers, 7 Lighting, 8 Gyro, 9 Impulse Triggers, 10 Touchpad, 11 Wheel, 12 Audio (`AudioTabIndex`), 13 Pointer, 14 Mouse, 15 Menus, 16 Bass Shakers (`BassShakersTabIndex`, gated on `RumbleAudioTabVisible`), 17 Output (`OutputTabIndex`, gated on `OutputTabVisible`). The page shows the section that holds it (`SelectedSection`). The setter remembers the number as its section's last tab, re-filters the rows when Buttons goes from the picture to the list or back, and on entering 12 or 16 runs `RefreshAudioGroup()` or `RefreshBassShakersGroup()`. The groups a selected device cannot use (no gyro, no touchpad, no lights) hide on the page. |

### Commands

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `TestRumbleCommand` | `IsDeviceOnline` | Raises `TestRumbleRequested`. |
| `ClearMappingsCommand` | always | Stops any Map All walk, then clears every row's whole surface: primary and negative descriptors, the option flags, the per-row sensitivities and acceleration, `NoInherit`, the primary kind (back to Direct), the deadzone (back to 50), the device tag, the extra sources, the combine mode and formula, the trim settings, and the first source's shaping and gates (`LoadShapingAndGates(null)`). |
| `CopySettingsCommand` | `HasSelectedDevice`, or the slot is created | Raises `CopySettingsRequested`. |
| `PasteSettingsCommand` | `HasSelectedDevice`, or the slot is created | Raises `PasteSettingsRequested`. |
| `CopyFromCommand` | `HasSelectedDevice`, or the slot is created | Raises `CopyFromRequested`. |
| `MapAllCommand` | `HasSelectedDevice && !IsMapAllActive && SelectedMappedDevice.IsOnline` | Starts sequential "Map All" recording. The page's Map All button (`MapAllToggle_Click`) starts a sweep or stops the one running, and swaps its caption and tooltip through `MapAllButtonText` (`Pad_MapAll`, or `Common_Stop` while a sweep runs) / `MapAllButtonTooltip`. |

### Map All System

| Property | Type | Description |
|----------|------|-------------|
| `IsMapAllActive` | `bool` | Map All recording in progress. |
| `MapAllCurrentIndex` | `int` | Current mapping row index during Map All. |
| `MapAllCurrentTarget` | `string` | Target setting name being recorded. |
| `MapAllPromptText` | `string` | Descriptive text the line under the picture shows during Map All (e.g., `"Map: A  (1/21)"`). |
| `CurrentRecordingTarget` | `string` | `TargetSettingName` being recorded. Drives the preview's flashing. |
| `MapAllRecordingNeg` | `bool` | Internal. Recording negative direction of a bidirectional axis. |

| Event | Args | Description |
|-------|------|-------------|
| `TestRumbleRequested` | `EventArgs` | Test rumble requested. |
| `TestLeftMotorRequested` | `EventArgs` | Test left motor only. Fired via `FireTestLeftMotor()`. |
| `TestRightMotorRequested` | `EventArgs` | Test right motor only. Fired via `FireTestRightMotor()`. |
| `CopySettingsRequested` | `EventArgs` | Copy settings to clipboard. |
| `PasteSettingsRequested` | `EventArgs` | Paste settings from clipboard. |
| `CopyFromRequested` | `EventArgs` | Copy from another slot (MainWindow opens `CopyFromDialog`). |
| `MapAllRecordRequested` | `MappingItem` | Request recording for the current Map All item. |
| `MapAllCancelRequested` | `EventArgs` | Cancel an in-progress Map All recording. |

### State Update Methods

| Method | Description |
|--------|-------------|
| `UpdateFromEngineState(Gamepad, Vibration selectedDeviceVibration = null)` | Updates combined slot output at 30 Hz. The optional second argument drives the selected device's own motor bars (`DeviceLeftMotorDisplay`, `DeviceRightMotorDisplay` and the two trigger-motor bars). The raw bars (`RawLeftMotorDisplay`, `RawRightMotorDisplay`) are written by `InputService` from the game's command. |
| `UpdateDeviceState(Gamepad)` | Updates per-device stick/trigger values for the stick and trigger previews. |
| `UpdateFromTouchpadState(in TouchpadState)` | Mirrors the combined touchpad state onto the `TouchpadFinger*` / `TouchpadClickPressed` preview properties. |
| `UpdateFromRawHidState(RawHidState)` | Publishes the combined raw-HID output for the Extended schematic. Skips the notification when axes, hardware axes, buttons, and POVs all match the last snapshot, so an idle slot does not re-arm a repaint at 30 Hz. On a slot whose preview rides the raw surface (`PreviewRidesRawSurface`: any Nintendo slot, and an Extended slot on a Valve lettered profile) it also projects the raw state onto the Gamepad-shaped preview properties, and `UpdateFromEngineState` skips writing them so the two paths cannot fight. |
| `UpdateFromMidiRawState(MidiRawState)` | Updates the MIDI preview snapshot. Skips the notification when the CC values and notes match the last snapshot. |
| `OnMapAllItemCompleted()` | Advances Map All to next item after 500 ms delay. |
| `StopMapAll()` | Stops Map All, clears state, raises `MapAllCancelRequested`. |
| `RefreshCommands()` | Refreshes `CanExecute` for the device-gated commands: test rumble, sound test, both impulse-trigger tests, remove macro, copy, paste, Copy From and Map All. |

### Sections and Groups (#574)

**File:** `PadViewModel.Sections.cs`

The controller page's six sections, the header's type chip, and the bar under the picture. The old tab numbers live on as groups: `TabsOfSection(section)` lists each section's tabs in page order (Buttons 0, 2, 17. Sticks & Triggers 3, 4, 14. Rumble & Haptics 5, 9, 6, 11, 16. Motion & Touch 8, 10, 13. Lights & Sound 7, 12. Macros & Menus 1, 15), and `SectionOfTab(tab)` goes the other way. The four middle sections stack their groups on one page (`IsStackedSection`). Buttons shows the picture or the list, and Macros & Menus shows the macros or the menus. `BarOrder` (internal) is the comparer that orders the rows of the bar under the picture.

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `SectionCount` | `int` (const) | - | How many sections the page has. |
| `ButtonsSection` | `int` (const) | - | Buttons: the picture, the mapping list and the output options. |
| `SticksSection` | `int` (const) | - | Sticks & Triggers: sticks, triggers and a mouse's gestures. |
| `RumbleSection` | `int` (const) | - | Rumble & Haptics: force feedback, impulse triggers, adaptive triggers, the wheel and bass shakers. |
| `MotionSection` | `int` (const) | - | Motion & Touch: gyro, touchpad and pointer. |
| `LightsSection` | `int` (const) | - | Lights & Sound: lighting and audio. |
| `MacrosSection` | `int` (const) | - | Macros & Menus. |
| `PictureTabIndex` | `int` (const) | - | The tab that is the picture of the controller. |
| `MappingsTabIndex` | `int` (const) | - | The tab that is the list of every mapping row. |
| `TabsOfSection` | method (static) | - | The tabs of a section in page order, empty for a number that names no section. |
| `SectionOfTab` | method (static) | - | The section that holds a tab, or -1 for a number that names no tab. |
| `IsStackedSection` | method (static) | - | True for the four sections that stack their tabs as groups. False for Buttons and Macros & Menus. |
| `TypeGeometry` | `Geometry` | - | The header chip's logo for the slot's type, or null for the types drawn with a glyph. The same drawing as the slot's Home card and its sidebar entry (SlotTypeIconMap). |
| `SelectedSection` | `int` | - | The section that holds the selected tab. The page's content follows it. |
| `ButtonsViewIndex` | `int` | - | Which view of Buttons shows: 0 the picture, with the picked control's rows and the output cards under it, 1 the list of every row. Tab 2 is the list. Tabs 0 and 17 are the picture. It holds while another section is selected. |
| `IsButtonsPictureView` | `bool` | - | Buttons shows the picture. |
| `IsButtonsListView` | `bool` | - | Buttons shows the list. |
| `ShowOutputGroup` | `bool` | - | The output cards show: under the picture, on a slot type that has any. |
| `ShowMidiCard` | `bool` | - | A MIDI slot's card shows under the picture's card, where a controller has its output cards: the port, the channel and the runs of controls and notes. |
| `ShowExtendedCard` | `bool` | - | An Extended slot's card shows under the picture's card, over the output cards: what is done to the slot as a whole, and Customize with what it sets. |
| `ShowSteamVrState` | `bool` | - | The header says SteamVR's state after the slot's name: a VR slot drives nothing without SteamVR, and nothing else on the page says whether it is there. |
| `MacrosPartIndex` | `int` | - | Which part of Macros & Menus shows: 0 the macros, 1 the menus. |
| `MacrosTabIndex` | `int` (const) | - | The Macros tab's number. |
| `MenusTabIndex` | `int` (const) | - | The Menus tab's number. |
| `ListedMacro` | `MacroItem` | - | The macro its list shows as picked: the selected macro while the macros are the part that shows, and none while the menus are, so one item is picked across the two lists. Picking a macro selects it and shows the macros. A list hands back nothing when its pick goes to the other list, which selects nothing. |
| `ListedMenu` | `MenuEditorItem` | - | The menu its list shows as picked, as `ListedMacro` is for the macros. |
| `LastTabOfSection` | method | - | The tab a section was last on, 0 for a number that names no section. |
| `IsTabShown` | method | - | Whether a tab's content is on the page now. A stacked section shows all of its tabs at once, so any of them counts while that section is selected. In Buttons the picture and the output cards show together and the list shows alone. Macros & Menus shows only the selected part. A group the page hides for the selected device still counts here, since only the page knows that. |
| `PickedTarget` | `string` | - | The control the bar under the picture shows: the TargetSettingName of the one last clicked on the picture, last recorded, or last selected in the list. Session only, never saved. A direction's own name ("LeftThumbAxisXNeg") picks its row. |
| `PickedRow` | `MappingItem` | - | The row the bar under the picture is on: the one `PickedTarget` names. Its value, Add Source and options stand at the bar's end. Null with nothing picked. |
| `PickedTargets` | method (internal) | - | The targets of the controls the pick names: the picked row's, and with a row of a D-pad or a stick picked, those of every row of that control, which are the rows the bar under the picture holds. The picture rings what they draw. |
| `PickedName` | `string` | - | The bar's heading: the picked control's name. A stick and a D-pad are named as the list's group is, whichever of their rows was picked: a stick's axes and its click, the D-pad's directions. Where a slot has several controls to a category (a custom Extended slot's sticks and POVs), and on a keyboard and mouse slot, the control is named by the picked row. So is every one-row control, by the picture's name for it where that is not the row's. |
| `PickedKind` | `string` | - | What kind of control the picked one is, under its name in the bar, as the boards have it: "Face button", "Stick", "Keyboard key". Empty with nothing picked, or for a control with no kind to name. |
| `KindOf` | method (internal) | - | The kind of control a row is an output of, in the words of the bar's small line. A row of a stick or a D-pad is that control's kind, a stick's click included. Any other row of a controller goes by its group, and a button by which button it is: a lettered preset's raw rows by the control each one is. A keyboard and mouse slot's rows and a VR slot's go by their target's name, and a VR control says which hand it is in. A MIDI note's line is the row's own name, since the bar heads a note by its pitch. A pressure row has no kind to name. |
| `ShowPictureBar` | `bool` | - | The bar shows: under the picture, with a control picked. |
| `ShowPickedValue` | `bool` | - | The bar shows the picked row's live value: on every slot but a Keyboard + Mouse or a MIDI slot, whose boards draw the bar with none. A key, a mouse button or a note is on or off, and the picture lights it. |
| `ShowKbmFoot` | `bool` | - | A Keyboard + Mouse slot's foot shows at the foot of the picture's card, and under the list: what the slot's keyboard and its mouse type through. |
| `ShowVrFoot` | `bool` | - | The note under a VR slot's card, as its board draws it: Map All skips the A and B touch outputs, and how to bind one. It says to click the ring around A or B, so it shows under the picture, where the rings are, and not under the list. |
| `FirstSectionName` | `string` | - | The first section's name. On a Keyboard + Mouse, a MIDI and a VR slot it says what the slot's picture holds, as each slot's board names it: Keys & Mouse, Notes & Controls, Hands. On a controller it is Mappings: the section maps every control the picture draws, the sticks, the triggers and the D-pad with the buttons, so Buttons named a part of it (owner, 2026-11-14). |
| `PictureHintText` | `string` | - | The hint over the picture, in the words of what the slot's picture holds: keys and mouse buttons, notes and sliders, or a controller's controls. |
| `PictureIsCardFoot` | `bool` | - | The picture is the card's foot, and takes its lower corners: nothing is picked, so no bar follows it, the slot has no foot of its own, and no output lines stand in the card's tray under it (the sections pass). |
| `SameControl` | method (internal, static) | - | Whether two rows are of one control on the picture: both of one family, and of the same control where the slot has several to the category. |
| `FamilyOf` | method (internal, static) | - | The control a row is part of on the picture, by the category of that control's own rows: a D-pad's directions and a stick's two axes by their category, and a stick's click by the stick it is on, as the Buttons board has it. The click is a button in the list and one of its stick's rows under the picture. Null for a row that is a control by itself. |
| `PickedRowsView` | `ICollectionView` | - | The rows the bar under the picture holds: the picked control's, in the bar's order, and only those the slot's surface mode lets it drive. A view of its own over the rows. The bar shared the table's view before, so in the list, hidden, it built a block for every row of the table: 148 on a Keyboard + Mouse slot, about a second on each switch to the list. |
| `RowOfTarget` | method (internal) | - | The row a target names, by its own name or by its opposite direction's, or null. |
| `IsFamilyCategory` | method (internal, static) | - | The categories whose rows are one control on the picture: a stick's two axes and the D-pad's four directions. A pick of one of their rows shows them all, and a stick's click with its axes (`FamilyOf`). |
| `RowMatchesPick` | method (internal, static) | - | Whether a row belongs under the picture for a pick: the picked row itself, or any row of the picked row's control, which is its family and, on a slot with several controls to a category, the one it names. Names and a category are compared, never row objects, so the answer holds after the rows are rebuilt. |
| `HasGamepadRows` | method (internal, static) | - | The types whose rows are the fixed gamepad grid: buttons, the D-pad, the triggers and the two sticks, with the touchpad and motion rows where the type has them. Keyboard + Mouse, MIDI and VR have row sets of their own, and an Extended or Nintendo slot's rows follow its preset. |
| `ListIsGrouped` | `bool` (internal) | - | Whether the table's rows stand under a header for each kind of output. A gamepad's list has them. The rows under the picture never do: they are one control's. |
| `IsListGroupOpen` | method | - | Whether a group of the list shows its rows. The two sticks' groups start folded, as the List board opens (#574), and every other group starts open. The state is kept here by category, since the table builds its groups again whenever its rows change. Session only, never saved. |
| `SetListGroupOpen` | method | - | Records that a group of the list was opened or folded. The page shows it (PadPage.SyncListGroup). |
| `IsListening` | `bool` | - | A recording is waiting for an input on this slot: one started on the picture, by a row's record button or by Map All. |
| `ShowPictureLine` | `bool` | - | The line under the picture shows: in the picture's view, a recording waits for an input, or the last one asked for could not start. The list has no such line: a row shows its own recording state. |
| `PictureLineText` | `string` | - | What the line under the picture says: Map All's prompt while it runs, the control being recorded while one is, then why the last recording could not start, and otherwise how to map a control. |
| `RecordRefusalShown` | `TimeSpan` (internal, static) | - | How long the line under the picture says why a recording could not start, when nothing else clears it. |
| `RecordRefusal` | `string` | - | Why the last recording asked for on this slot could not start, or null. Session only, never saved. |
| `ShowRecordRefusal` | method | - | The recorder refused a recording on this slot: no device of the slot is connected, or none has the motion sensor a motion row records. A click on a control did nothing else, so the line under the picture says why, where the click was, until the next pick, a recording that starts, or `RecordRefusalShown` passes. The status line at the window's foot says it too. |
| `SocdSummary` | `string` | - | The SOCD card's value while folded: the mode's name. |

### Mapping List Columns (#574)

**File:** `PadViewModel.List.cs`

The mapping list draws one column per assigned device, with the devices that are not connected folded into one column at the end when the columns do not fit. See [ListColumn and RowCell](#listcolumn-and-rowcell).

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ListColumns` | `ObservableCollection<ListColumn>` | - | The list's columns, in order. The fold is the last and is always there, shown only while it holds devices. |
| `MarkListDirty` | method (internal) | - | The columns or a row's cells may be others now. The list is built again once, before the next frame, however many changes ask for it: a load changes every row many times. The build is posted only from the app's own thread, which is where the program changes rows and devices. A change made on any other thread leaves the list to its next reader (`Cells` and `FlushList` build it then). Posted from there, the build would read the rows on the app's thread while the other thread still changes them. |
| `MappedDeviceOf` | method (internal) | - | The assigned device a source names, or null: for no device, and for one the controller does not have. |
| `IsAway` | method (internal, static) | - | Whether a source's device is away: not connected, or not one of the controller's. A source that names no device is never away. |
| `ResolveFirstSourceName` | method (internal) | - | Names a row's first source again from its device's own names, after the source changed without a load. |
| `FlushList` | method (internal) | - | Builds the columns and every row's cells, if anything changed since they were built. |
| `SetListCellsWidth` | method (internal) | - | The page tells the list how wide its cells' part is: what a row has between the output's name and the row's end. |
| `IsAwayFolded` | `bool` | - | The devices that are not connected are folded into one column. |
| `ListCellsOffset` | `double` | - | How far the cells are scrolled sideways. |
| `ListCellsScrollMax` | `double` | - | The furthest the cells scroll: what the columns need at their least width, less what the list has. |
| `ListCellsViewport` | `double` | - | The room the list has for its cells, the scroll bar's page. |
| `ShowListCellsScroll` | `bool` | - | The cells do not fit at their least width, so the list shows a scroll bar at its foot. |
| `OpenAwayColumnsCommand` | `RelayCommand` | - | A click on the fold's head: each device that is not connected gets its column back, until the list has room for all of them or the devices change. |
| `ColumnsAreTight` | method (internal, static) | - | Whether the columns need folding, given how many there are and the room: more of them than fit at their least width. |
| `ShowRowValue` | `bool` | - | Whether an open row shows its live value: in the list always, and under the picture where the bar does (`ShowPickedValue`). |

### Centering (#588)

**File:** `PadViewModel.Centering.cs`

The Centering card in the Wheel group (`WheelTabIndex` 11, Rumble & Haptics): wheel centering as a plain spring (Mode `Spring`, with the Auto Centering Strength slider, `Pad_Wheel_Autocenter`) or as a car's steering torque from a tire model (Vehicle). The card's rows are Mode, Vehicle, Speed (From the Game or Fixed Speed), Steering Weight, On-Center Feel, Power Assist, Damping, Friction, Grip, Wheel Torque, Wheel Range and the Release Test. Every value is per (slot, device) and saved with the device's settings (`LoadCentering`, `SaveCentering`). The Friction row hides on a wheel that runs no friction effect (`CenteringFrictionShown`), since the wheel is then sent none. No wheel was run with this build: the card's behavior rests on the wheel references and the tests.

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `WheelTabIndex` | `int` (const) | - | The Wheel group's tab, which holds the Wheel card and the Centering card. |
| `CenteringMode` | `int` | - | 0 Spring, the Auto Centering Strength slider. 1 Vehicle, a car's steering torque from the tire model. |
| `CenteringIsVehicle` | `bool` | - |  |
| `CenteringIsSpring` | `bool` | - |  |
| `CenteringStrengthShown` | `bool` | - | The Auto Centering Strength row shows: Spring mode, on a wheel that has a spring. |
| `CenteringVehicleAvailable` | `bool` | `true` | Whether the selected wheel can run Vehicle mode: a Logitech, a Fanatec or a Thrustmaster wheel, or a wheel routed through SDL that has a constant force. Set with the device. |
| `CenteringSpringAvailable` | `bool` | `true` | Whether the selected wheel has a centering spring for Auto Centering Strength: every Logitech, Fanatec and Thrustmaster wheel, and a wheel routed through SDL whose driver lists a spring. Set with the device. |
| `CenteringModeSpringLabel` | `string` | - | The Mode list's first choice: Spring, or Off on a wheel with no spring, where that choice centers nothing. |
| `CenteringVehicle` | `string` | `SteeringVehicle.All[0].Id` | The car's id (`ById`). |
| `CenteringVehicleOptions` | `IReadOnlyList<GyroLabeledOption>` | - | The cars, in the list's order, each under its name in the interface's language. |
| `CenteringSpeedSource` | `int` | - | 0 From the Game, 1 Fixed. |
| `CenteringFixedSpeed` | `int` | `SpeedUnits.DefaultFixedSpeedKmh` | The fixed speed in km/h, 0 to 320, as it is saved. Clamped to 0 to 320. |
| `SpeedInMiles` | `bool` (static) | - | Whether speeds read in miles an hour on this PC (`Miles`). |
| `CenteringSpeedUnit` | `string` | - | The unit speeds read in: mph or km/h. |
| `CenteringFixedSpeedMost` | `int` | - | The fixed speed's most, in the unit shown. |
| `CenteringFixedSpeedShown` | `int` | - | The fixed speed in the unit shown. |
| `CenteringWeight` | `int` | - | Steering Weight in percent, the tire moment gain. Clamped to 0 to 200. |
| `CenteringOnCenter` | `int` | - | On-Center Feel in percent, the jacking stiffness. Clamped to 0 to 200. |
| `CenteringAssist` | `int` | `100, _centeringDamping = 100` | Power Assist in percent, the weighting's lower limit. Clamped to 0 to 200. |
| `CenteringDamping` | `int` | `100` | Damping in percent of what returns the wheel without swinging past center. Clamped to 0 to 200. |
| `CenteringFriction` | `int` | `30` | Friction in hundredths of a newton meter, 0 to 150, as it is saved. Clamped to 0 to 150. |
| `CenteringFrictionNm` | `double` | - | Friction in N·m. |
| `CenteringGrip` | `int` | - | 0 From the Game, 1 Dry, 2 Wet, 3 Snow, 4 Ice. Clamped to 0 to 4. |
| `CenteringWheelTorque` | `int` | - | The wheel's torque in tenths of a newton meter as it is saved, 0 where none is entered and the listed figure applies. Clamped to 0 to 500. |
| `CenteringListedTorque` | `double` | - | The maker's figure for the selected wheel in N·m, or 0 (`WheelTorqueList`). Set with the device. |
| `CenteringWheelTorqueNm` | `double` | - | The torque in use, in N·m: the entered figure, the listed one, or what an unlisted wheel starts from. Entering one saves it. Clamped to 0 to 50. |
| `CenteringTorqueUnset` | `bool` | - | No figure is entered and none is listed, so the forces are held low. |
| `CenteringWheelRange` | `int` | `900` | How far the wheel turns from lock to lock in degrees, for a wheel whose range PadForge does not set. Clamped to 40 to 2520. |
| `CenteringWheelRangeShown` | `bool` | - | The Wheel Range row shows in Vehicle mode on a wheel whose range PadForge does not set: one routed through SDL, or a native wheel with Set Rotation Range off. |
| `SetCenteringWheel` | method (internal) | - | The facts of the selected device's wheel: its listed torque, whether PadForge sets its range, and which of the two modes it can run. Set when the device's settings load, and again by the page when the wheel connects or leaves. |
| `LoadCentering` | method (internal) | - | Loads the Centering section of a device's settings with the facts of its wheel. |
| `SaveCentering` | method | - | The Centering section back into a device's settings. |
| `CenteringFrictionShown` | `bool` | - | The Friction row shows on a wheel that runs a friction effect. Elsewhere the wheel is sent no friction (`FrictionSent`), so the setting would change nothing. |
| `CenteringMoreHint` | `string` | - | The More row's hint: the rows under it, Friction left out where that row does not show. |
| `CenteringSettingsNow` | method | - | The settings as the engine reads them, from what the card shows now and what the wheel runs itself: the Release Test starts from these. |
| `CenteringPreview` | `CenteringPreview` | - | The chart's curves and the measures, at the speed and the grip in use. |
| `RefreshCenteringPreview` | method | - | Rebuilds what the card draws from the settings. |
| `NoFigure` | `string` (const) | - | What a figure reads while there is none to show. |
| `Signed` | method (internal, static) | - | A figure that can fall under zero, with the minus sign the chart's own labels have, and none on a figure that rounds to zero. |
| `CenteringSpeedLegend` | `string` | - | The chart's two legends: the speed its band is drawn at, and the speed of its second line, each with its unit. |
| `CenteringReferenceLegend` | `string` | - |  |
| `CenteringOnCenterFeelText` | `string` | - |  |
| `CenteringStiffnessText` | `string` | - |  |
| `CenteringLinearityText` | `string` | - |  |
| `CenteringPeakText` | `string` | - |  |
| `CenteringPeakOfText` | `string` | - |  |
| `CenteringPeakOverLimit` | `bool` | - |  |
| `CenteringSpeedText` | `string` | - | The speed the model runs at, in the unit shown. |
| `CenteringSpeedIsLive` | `bool` | - | That speed is a game's, read this moment, and no setting's: the figure is lit as a live reading is. |
| `CenteringAngleText` | `string` | - | The wheel's angle in degrees and the torque at the rim in N·m, as the wheel runs. |
| `CenteringTorqueText` | `string` | - |  |
| `CenteringChartName` | `string` | - | The chart's spoken name: what it plots and where the curve peaks. |
| `CenteringLiveShown` | `bool` | - | The chart's live mark shows: Vehicle mode is running on the wheel. |
| `CenteringLiveAngle` | `double` | - | Where the chart's live mark stands, in degrees and in N·m, while `CenteringLiveShown`. |
| `CenteringLiveTorque` | `double` | - |  |
| `CenteringStatusText` | `string` | - | The line under the card's rows that says what holds the force back, or nothing. |
| `CenteringHasStatus` | `bool` | - |  |
| `CenteringMeasured` | `bool` | - | The Release Test has measured the selected wheel. |
| `CenteringReleaseStatus` | `string` | - | The Release Test row's state. |
| `UpdateCenteringLive` | method | - | Takes the wheel's last frame from the engine: the live mark and readouts, the speed and the grip a game gives, and what holds the force back. Called on the page's timer while the card shows. |
| `ResetCenteringAllCommand` | `RelayCommand` | - | Every setting on the Centering card back to its default: Spring mode, with the slider at nothing. The wheel's measurement is the wheel's, and stays. |

`CenteringPreview` is what the card's chart draws, rebuilt by `RefreshCenteringPreview()`:

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ReferenceSpeed` | `double` (const) | - | The reference speed the chart's second line is drawn at: 25 mph, the lower of the two speeds the paper tests at. |
| `WidestSpanDegrees` | `double` (const) | - | The widest the chart draws either side of center, in degrees. A wheel that turns less draws to its lock. |
| `Curve` | `SteeringCurve` | - |  |
| `Reference` | `SteeringCurve` | - |  |
| `Measures` | `SteeringMeasures` | - |  |
| `Friction` | `double` | - | The friction the wheel is sent in N·m (`FrictionSent`), none on a wheel with no friction effect, and the most torque the wheel gives. |
| `WheelTorque` | `double` | - |  |
| `SpanDegrees` | `double` | - | How far the chart draws either side of center, in degrees. |
| `PeakTorque` | `double` | - | The most torque the car asks inside the chart's span, in N·m, and the angle it asks it at, in degrees. |
| `PeakAngleDegrees` | `double` | - |  |
| `PeakOverLimit` | `bool` | - | The car asks more than the wheel has. |

### Gyro Activation (Steam's Gyro On, Ratchet and Re-Center)

**File:** `PadViewModel.GyroActivation.cs`

The Gyro card's activation rows: Layer (`Pad_GyroActivation_Layer`), Gyro On (`Pad_GyroActivation`: Same as Base, Always On, While Held, While Not Held, Toggle on Each Press), Gyro On Buttons (`Pad_GyroActivation_Buttons`), Needs (`Pad_GyroActivation_Needs`: Any Button or Every Button) and Re-Center When Gyro Turns On (`Pad_GyroRecenterOnEngage`), each with its reset. Activation is stored per device, by shift layer (`PadSetting.GyroActivation`), and covers what Steam Input's gyro activation, ratchet and re-center do. An imported Steam config's activations arrive on the slot's `MappingSet` (`WorkshopGyroActivation`, `WorkshopGyroRecenterOnEngage`), and `WorkshopTuningApplier` moves them onto the assigned device's Gyro card.

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `GyroActivationSameAsBase` | `string` (const) | - | The Gyro On value of a layer with no entry of its own, which follows Base's. |
| `GyroActivationAlways` | `string` (const) | - | The Gyro On value of an entry with no buttons: the gyro stays on in that layer. |
| `GyroActivation` | `string` | `""` | The device's gyro activation by layer (`GyroActivation`), in its text form. The Engage card edits one layer of it at a time. |
| `GyroRecenterOnEngage` | `bool` | - | Re-centers the gyro each time it turns on (`GyroRecenterOnEngage`). |
| `GyroActivationLayer` | `string` | `"Base"` | The layer whose activation the card shows: Base or a shift layer's mask, from `SwitchLayerChoices`. |
| `GyroActivationMode` | `string` | `GyroActivationSameAsBase` | How the shown layer turns the gyro on: Same as Base (no entry), Always, Hold, Release or Toggle. |
| `GyroActivationAll` | `bool` | - | True when the shown layer needs every checked button held, false when any one does. |
| `GyroActivationUsesButtons` | `bool` | - | True while the shown layer's mode reads buttons, which is when the Buttons and Needs rows show. |
| `GyroActivationButtons` | `ObservableCollection<GyroActivationButton>` | - | Every device-free input the activation can use, each checked when the shown layer's entry holds it. |
| `GyroActivationModeChoices` | `IReadOnlyList<GyroActivationChoice>` | - | The Gyro On choices for the shown layer. Base has nothing to follow, so its no-entry choice reads Always On. |
| `GyroActivationNeedsChoices` | `IReadOnlyList<GyroActivationChoice>` | - | The Needs choices: any one checked button, or all of them. |
| `GyroActivationNeeds` | `string` | - | The Needs picker's value, "Any" or "All". |
| `ResetGyroActivationLayerCommand` | `RelayCommand` | - | Clears the shown layer's entry: Base keeps the gyro on, a shift layer follows Base. |
| `ResetGyroActivationNeedsCommand` | `RelayCommand` | - | Resets `GyroActivationNeeds` to `"Any"`. |
| `ResetGyroActivationButtonsCommand` | `RelayCommand` | - | Resets gyro activation buttons to its default. |
| `ResetGyroRecenterOnEngageCommand` | `RelayCommand` | - | Resets `GyroRecenterOnEngage` to `false`. |

`GyroActivationButton` is one checkable input in Gyro On Buttons: `Descriptor`, `DisplayName` and `IsOn`. `GyroActivationChoice` is one entry of the Gyro On and Needs pickers.

### Settings Sync, Device Configs and Appearance

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `SettingsSyncDirty` | `bool` (internal) | - | Set by any PropertyChanged on this VM. Cleared by InputService after SyncViewModelToPadSettings pushes the VM into the selected device's PadSetting. Idle pads (no engine feed changes, no user edits) raise nothing because every VM write is SetProperty equality-guarded, so the 30 Hz sync's ~80 string formats per pad skip entirely. Starts true so the first tick always syncs. UI-thread only. |
| `SuppressSettingsDirty` | `bool` (internal) | - | Set by InputService around its 30 Hz telemetry-mirror block (live sticks/gyro/meters): those writes are display state, not settings, and without this every frame of controller motion re-armed the full ~80-format settings serialization. UI-thread only, always cleared in a finally. |
| `SeedExtendedConfigFromProfile` | method (internal) | - | Fills an `ExtendedSlotConfig` from the slot's selected HIDMaestro profile in `AvailableProfiles`: triggers to zero first, since the stick and trigger setters share an axis budget. No profile, no change. |
| `RekeyDeviceConfig` | method (internal) | - | Moves a per-device slot config to a device's new identity after an adoption re-key. The INSTANCE moves rather than being copied, so effect-dispatcher subscriptions anchored to it stay valid. No-op when the old key is absent. When the new key ALREADY holds a config that entry is the newer truth and the old instance is dropped, so subscriptions anchored to the dropped one do not survive: the destination-wins policy matches the UserSetting migration's, and the loss is bounded to a collision that only an orphaned entry can produce. |
| `PeekDeviceConfig` | method | - | Non-creating read of a device's config. For provider lambdas that run on audio/worker threads: a miss means "not this slot", and materializing a default entry from a reader would race EnsureDeviceSlotConfigsForMappedDevices. |
| `PruneDeviceSlotConfigsToAssigned` | method | - | Drops the per-device config of every device that is no longer assigned to this slot. The dictionary is keyed by device guid and nothing removed entries: unassigning a DualSense left its crossfeed, limiter and EQ in here, and the next assignment of the same pad found them through GetOrAdd and showed them as if the user had set them again (owner report 2026-08-25). An assigned device's config is per-assignment state and leaves with the assignment. Offline is not unassigned: the caller passes the slot's UserSetting guids, never its online set. The anchor (empty guid) is reset only when it was bound to a dropped config, so the page never keeps editing an orphan. |
| `RemoveDeviceConfig` | method | - | Removes one device's per-device config, rebinding the page's per-device groups to the empty sentinel when that config was the bound one. Returns false when there was nothing to remove. |
| `NotifySelectedMappedDeviceIdentityChanged` | method | - | Forces the same notification chain the setter would fire when `SelectedMappedDevice`'s underlying device changes without the object reference itself changing. InputService's SyncMappedDevices mutates existing MappedDeviceInfo entries in place to minimize ObservableCollection churn, so unassigning a device that sat above the previously-selected one (e.g. removing "All Keyboards (Merged)" from a slot that also has a DualSense) rewrites the selected entry's Name + InstanceGuid + IsOnline while keeping the same object: without this nudge, listeners that gate on PropertyChanged (PadPage.SyncTabVisibility, the Force Feedback, Lighting and Adaptive Triggers groups, the HM dispatcher re-attachment) miss the device identity swap and stay pinned to the prior device's capabilities. |
| `ClearPerDeviceConfigsForUncreatedSlot` | method | - | clears the per-device config dictionary for a slot that is NOT created after a profile apply. Compaction shifts data down and the former tail index kept its dictionary, so creating a new slot there later and mapping the same device resurrected the old lighting / adaptive / synthetic-pressure config via GetOrAdd, the exact resurrection the DeleteSlot clear above prevents for the deleted index. DeviceConfig replacement is anchor-safe through the forwarder pattern. |
| `Model3DAppearances` | `string` | `""` | 3D preview colorway per model family, comma-joined "Family=AppearanceId" pairs saved with the slot, so each virtual controller keeps its own appearance per family. Cosmetic only. |
| `GetModelAppearance` | method | - | Selected appearance id for a model family, or null when unset (the model's default applies). |
| `ModelAppearanceIn` | method (internal, static) | - | The finish chosen for a family of art in a controller's stored finishes ("family=finish,family=finish"), or null when they name none for it. A profile's card reads a stored controller's finish with it, as the controller's page reads its own. |
| `SetModelAppearance` | method | - | Stores one model family's appearance id in `Model3DAppearances`. An empty id removes the family's pair. |
| `AnnotationOverlayEnabled` | `bool` | `true` | Controller-preview annotation overlay, shared by the 2D and 3D hosts (#175 roadmap 1). On at first, as the Buttons board opens with the button labels shown (#574). Session-only by design: not written to PadSetting, not in the MarkDirty allowlist. |

### Picker Filter and Mapping Rows

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `PickerFilterKey` | method (internal, static) | - | The key a choice filters under: its device guid, or "any" for the device-agnostic group (empty guid). |
| `MatchesPickerFilter` | method (internal, static) | - | The filter predicate, pure and test-locked: a choice shows unless its device is hidden or the search text misses its display name (case-insensitive substring). |
| `HiddenPickerDeviceKeys` | `HashSet<string>` (internal) | - | Hidden picker device keys (guids, plus "any" for the device-agnostic group). Persisted per slot in the settings root, not in profiles. |
| `RowMatchesSurface` | method (internal, static) | - | Whether a Keyboard + Mouse row survives the slot's surface mode and the table's scope. Non-KBM rows are unaffected, so this is a no-op on every other slot type. |
| `RowMatchesSearch` | method (internal, static) | - | A grid row matches the search when its target label or its selected source's display name carries the text. Rows are OUTPUTS, so the device-visibility set does not hide them. Only typed text does. |
| `MappingsViewLoaded` | `bool` | - | True when `Mappings` currently reflects this slot's authoritative MappingSet: i.e. `RefreshMappingsCore` has run since the MappingSet was last rebuilt. False during the window between a MappingSet rebuild (e.g. a device assignment auto-mapping a new pad) and the ViewModel reload that follows it. Why this exists. `SaveViewModelToPadSetting` (syncMappings) persists the per-VC mappings by CLEARING every slot device's PadSetting descriptors and rewriting them from `Mappings`. That is only lossless when `Mappings` is current. During an assignment the dropdown auto-selects the just-assigned device, which fires `OnSelectedDeviceChanged` → `SaveViewModelToPadSetting` a few milliseconds BEFORE `RefreshMappingsToViewModel` reloads `Mappings` from the freshly auto-mapped MappingSet. With a stale (empty) `Mappings`, the clear+rewrite wiped the new device's entire auto-map: the trace showed a DualSense going from 21 mapped descriptors to 0 in 2 ms ("assigning my DualSense to the wheel's slot only maps the Share button"). When this flag is false, the save skips the mapping clobber (the MappingSet is authoritative and already current). Per-device tuning still saves. |
| `ReloadActiveLayerRows` | method (internal) | - | Re-reads the active layer's rows into the grid without changing which layer is active. Callers that edited the active layer's rows underneath the grid used to fake a change by assigning "Base" and then the mask back. That is a no-op when the active layer IS Base, because the setter returns on equality before raising anything, so a paste or a clear on Base left the grid showing the pre-edit rows and the next save pushed those stale rows back over the edit. |
| `SwitchLayerChoices` | `ObservableCollection<ShiftLayerInfo>` | - | A Switch Layer step's targets: Base and every shift layer, the layer tabs' own set. A collection of its own, reconciled in place beside `MacroLayerChoices` and for the same reason: the step's picker keeps its selected entry through a rebuild of the layer tabs. |
| `IsActiveLayerInheriting` | `bool` | - | True when the currently-active layer is a shift layer AND its activator has `InheritUnmapped=true`. Drives the per-row "Do not inherit" CheckBox visibility: that flag only has meaning on inheritance-enabled layers (in replace mode the Base row is already blocked wholesale). Recomputed by `RebuildLayerTabs` and on `ActiveLayerMask` change. |
| `KbmSurfaceOf` | method (internal, static) | - | Which half of a Keyboard + Mouse slot a mapping row belongs to, or null when the row is not a Keyboard + Mouse row at all. ONE classifier, called by the surface mode and by the table filter, so the two cannot drift apart the way two copies of the POV sector rule did (#408). The descriptor vocabulary is the fact it reads, and it is the same vocabulary the engine dispatches on: keyboard rows are "KbmKey" plus the VK in hex, and every other Kbm row is mouse (KbmMBtn0..4, KbmMouseX/Y, KbmScroll, KbmScrollH). |
| `IsMenuItemRowBound` | method (internal) | - | True when a Mappings row source or a macro trigger on this slot reads "Menu {menuId} Item {itemIndex}". Workshop imports bind cells through rows instead of the cell's direct binding, and the cell editor must not show "None" while those rows fire (audit 2026-07-16 C12). Same unlocked UI-thread read of the slot's MappingSet as SlotMenuSet. |
| `RefreshMenuInputChoices` | method | - | Re-raises every menu editor's Custom steer / Click dropdowns after the slot's picker list repopulates. Called by PopulateAvailableInputs beside the other per-feature selected- input refreshers. |

### More Live Output State

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `Paddle2` | `bool` | - | Live output state of the second and third paddles, beside `Paddle1` / `Paddle4`, for the preview. |
| `Paddle3` | `bool` | - | See `Paddle2`. |
| `LeftStickTouch` | `bool` | - | Live output state of the stick-top and grip touch sensors, for the preview. |
| `RightStickTouch` | `bool` | - | See `LeftStickTouch`. |
| `LeftGripTouch` | `bool` | - | See `LeftStickTouch`. |
| `RightGripTouch` | `bool` | - | See `LeftStickTouch`. |
| `DeviceTouchX0` | `float` | - | The selected device's own touchpad contacts 0 and 1, position 0 to 1 and contact state, for the live touch view. |
| `DeviceTouchY0` | `float` | - | See `DeviceTouchX0`. |
| `DeviceTouchDown0` | `bool` | - | See `DeviceTouchX0`. |
| `DeviceTouchX1` | `float` | - | See `DeviceTouchX0`. |
| `DeviceTouchY1` | `float` | - | See `DeviceTouchX0`. |
| `DeviceTouchDown1` | `bool` | - | See `DeviceTouchX0`. |
| `DeviceTouchTapered` | `bool` | - | Whether the device's pad is a PlayStation pad, whose sides close in toward its foot, so the live view draws that outline. Any other pad is drawn as a rounded rectangle. |

### Pipeline Chips (#175 item 10)

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `PipelineCurveActive` | `bool` | - | Each chip's three faces: `…Active` (some row carries that configuration, from the 1 s config lane), `…Live` (a row of it fired this tick) and `…TipRows` (the tooltip's lines). Shift has a `PipelineShiftSummary` string in place of tip rows. |
| `PipelineCurveLive` | `bool` | - | See `PipelineCurveActive`. |
| `PipelineCurveTipRows` | `IReadOnlyList<PipelineTipRow>` | `Empty<PipelineTipRow>()` | See `PipelineCurveActive`. |
| `PipelineGyroActive` | `bool` | - | See `PipelineCurveActive`. |
| `PipelineGyroLive` | `bool` | - | See `PipelineCurveActive`. |
| `PipelineGyroTipRows` | `IReadOnlyList<PipelineTipRow>` | `Empty<PipelineTipRow>()` | See `PipelineCurveActive`. |
| `PipelineShiftActive` | `bool` | - | See `PipelineCurveActive`. |
| `PipelineShiftLive` | `bool` | - | See `PipelineCurveActive`. |
| `PipelineShiftSummary` | `string` | `""` | The shift chip's tooltip: the non-Base layer names. |
| `PipelineInvertActive` | `bool` | - | See `PipelineCurveActive`. |
| `PipelineInvertLive` | `bool` | - | See `PipelineCurveActive`. |
| `PipelineInvertTipRows` | `IReadOnlyList<PipelineTipRow>` | `Empty<PipelineTipRow>()` | See `PipelineCurveActive`. |
| `PipelineDeadZoneActive` | `bool` | - | See `PipelineCurveActive`. |
| `PipelineDeadZoneLive` | `bool` | - | See `PipelineCurveActive`. |
| `PipelineDeadZoneTipRows` | `IReadOnlyList<PipelineTipRow>` | `Empty<PipelineTipRow>()` | See `PipelineCurveActive`. |
| `HasAnyPipelineChips` | `bool` | - | Chip-row visibility gate: collapse the whole strip when no pipeline carries configuration. |
| `IsInvertPipelineRow` | method (static) | - | Row owns the Inverted pipeline: a mapped primary with the invert transform on. Extra-source Invert is excluded on purpose. On a bipolar pair it encodes the negative direction, not an inversion transform. |
| `IsDeadZonePipelineRow` | method (static) | - | Row owns the Deadzone pipeline: per-mapping deadzone moved off its 50% default (MappingItem initializer + ResetDeadZoneCommand) on a row where it applies. |
| `IsGyroPipelineRow` | method (static) | - | Row owns the Gyro pipeline: primary or any extra source reads a "Gyro *" axis. Motion-passthrough rows use "Motion *" descriptors, so the auto-created Sony passthrough never lights this chip. |
| `IsCurvePipelineRow` | method | - | Row owns the Curve pipeline: its target is one of the six curve-bearing outputs and that output's sensitivity curve is non-linear (defaults `"0"` / `"0,0;1,1"` both parse linear via CurveLut.IsLinear). |
| `RefreshPipelineChips` | method | - | Refreshes chip liveness from the current Mappings rows. Called by InputService.UpdateMappingLiveValues right after the rowfire pass so IsInputActive reflects this tick. The engaged layer mask comes from the same engine poll the shift flyout uses (InputManager.GetEngagedLayerMask). Presence + tooltip listings ride the throttled config recompute, not this per-tick path. |
| `PipelineTipRow` | type | - | One line of a pipeline chip tooltip: a device header (present only when several controllers feed the chip's row set), an "OUTPUT ← source" mapping line, or the "+N" overflow tail. Built on the 1 s config lane. |
| `ClearPipelineLiveness` | method | - | Drops every flame (Live flags) without touching the config-derived Active / Summary state. InputService.Stop calls this after tearing down the UI timer so no chip stays lit on a dead engine. |

| `PipelineTipRow` member | Type | Default | Description |
|--------|------|---------|-------------|
| `IsHeader` | `bool` | - |  |
| `IsTail` | `bool` | - |  |
| `Text` | `string` | `""` | Header / tail lane text: device label or "+N". |
| `Output` | `string` | `""` | Mapping lane: the VC output label. |
| `Detail` | `string` | `""` | Mapping lane: feeding source(s), plus the chip-specific note (curve preset name, DZ percent). |

### Gyro Tuning

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `GyroSensitivityH` | `double` | `1.0` | Horizontal gyro sensitivity. Also raises `GyroSensitivityH_DegPerTurn`. Clamped to 0.1 to 10. |
| `GyroSensitivityV` | `double` | `1.0` | Vertical gyro sensitivity. Also raises `GyroSensitivityV_DegPerTurn`. Clamped to 0.1 to 10. |
| `GyroSensitivityH_DegPerTurn` | `double` | - | Real-world readout: whole degrees of physical rotation per one full screen turn at the current H sensitivity, which its row under Sensitivity's More says (Pad_Gyro_DegPerTurn_Format). Steam-style reference, 360 at multiplier 1.0. |
| `GyroSensitivityV_DegPerTurn` | `double` | - | The same for the V sensitivity. |
| `GyroDeadZoneDegPerSec` | `double` | `3.0` | Gyro deadzone in degrees per second. Clamped to 0 to 30. |
| `GyroSmoothingAlpha` | `double` | - | Gyro smoothing factor. Clamped to 0 to 0.95. |
| `GyroAcceleration` | `double` | - | Gyro acceleration. Clamped to 0 to 5. |
| `GyroOutputCurve` | `string` | `"Linear"` | The output curve's stored value, from `OutputCurveChoices`. Null writes `"Linear"`. |
| `OutputCurveChoices` | `IReadOnlyList<GyroLabeledOption>` (internal, static) | - | The output curve picker's entries, one list for every slot. The Home stage readout names a stored curve from it. |
| `GyroOutputCurveOptions` | `IReadOnlyList<GyroLabeledOption>` | - | The output curve picker's entries (`OutputCurveChoices`). |
| `GyroSensitivityUnits` | `string` | `"Multiplier"` | How the sensitivity is shown: `"Multiplier"` (default) or the other entries of `GyroSensitivityUnitsOptions`. Null writes `"Multiplier"`. |
| `GyroSensitivityUnitsOptions` | `IReadOnlyList<GyroLabeledOption>` | - | The units picker's entries. |
| `GyroEasyAimStickThreshold` | `double` | - | Deflection threshold (0-100%) of the Engage Stick (`GyroEngageStickSide`) below which gyro output is zeroed. 0 = always on (default). Clamped to 0 to 100. |
| `SpaceChoices` | `IReadOnlyList<GyroLabeledOption>` (internal, static) | - | Localized-display + stored-value pairs for the gyro space dropdown, one list for every slot. Stored value stays as the canonical English identifier so PadForge.xml round-trips are stable across locale changes. Display text is read from the strings resx. The Home stage readout names a stored space from it. |
| `GripChoices` | `IReadOnlyList<GyroLabeledOption>` (internal, static) | - | The grip picker's entries, one list for every slot. The Home stage readout names a stored grip from it. |
| `GyroPlayerSpaceYawRelaxFactor` | `double` | `1.41` | Player space's yaw relax factor (`GyroSpace` `"Player"`). Clamped to 1.0 to 2.0. |
| `GyroWorldSpaceSideReductionThreshold` | `double` | `0.125` | World space's side-reduction threshold (`GyroSpace` `"World"`). Clamped to 0.0 to 0.5. |
| `GyroTighteningThresholdDegPerSec` | `double` | `3.0` | Gyro tightening threshold in degrees per second. Clamped to 0 to 30. |
| `GyroSmoothingThresholdDegPerSec` | `double` | `8.0` | Gyro smoothing threshold in degrees per second: slower motion is smoothed. Clamped to 0 to 30. |
| `GyroSmoothingWindowMs` | `double` | `50` | Gyro smoothing window in milliseconds. Clamped to 10 to 200. |
| `GyroRealWorldCalibration` | `double` | - | Real-world calibration factor for the sensitivity. Clamped to 0 to 2. |
| `GyroInvertPitch` | `bool` | - | Inverts the gyro's pitch. |
| `GyroCompassYaw` | `bool` | - | Compass-anchored yaw (#271 item 5, Switch 2 magnetometer devices). Requires a stored magnetometer calibration to take effect. |
| `MagCalibrating` | `bool` | - | True while the figure-8 magnetometer capture runs (drives the Calibrate button's label swap). |
| `MagCalibrationToggle` | `Func<Guid, bool>` (static) | - | Wired by InputService: toggles the magnetometer calibration capture for a device GUID, returns true while capturing. |
| `MagCalibrateCommand` | `RelayCommand` | - | Starts or stops the magnetometer capture for `SelectedMappedDevice` through `MagCalibrationToggle`, and sets `MagCalibrating` from the answer. |
| `GyroInvertYaw` | `bool` | - | Inverts the gyro's yaw. |
| `GyroInvertRoll` | `bool` | - | Inverts the gyro's roll. |
| `GyroApplyTuningToPassthrough` | `bool` | `false` | Motion Passthrough reads the tuned motion (Tuned) instead of the calibrated motion (Raw). See `GyroPassthroughRaw`. |
| `GyroPassthroughRaw` | `bool` | - | Motion Passthrough's other choice, Raw: the game reads the calibrated motion and tunes it itself. It is the inverse of `GyroApplyTuningToPassthrough`, for the Gyro card's two-way switch, Raw or Tuned (the sections pass of #574). Raw chosen turns the tuning off. The switch's other choice going off writes nothing: choosing Tuned is what turns it on. |
| `GyroLiveRatePitch` | `double` | - | The selected device's live gyro rates and accelerometer values, for the Gyro group's readouts. Written by the 30 Hz tick. |
| `GyroLiveRateYaw` | `double` | - | See `GyroLiveRatePitch`. |
| `GyroLiveRateRoll` | `double` | - | See `GyroLiveRatePitch`. |
| `AccelLiveX` | `double` | - | See `GyroLiveRatePitch`. |
| `AccelLiveY` | `double` | - | See `GyroLiveRatePitch`. |
| `AccelLiveZ` | `double` | - | See `GyroLiveRatePitch`. |
| `GyroCalibrationLabel` | `string` | `""` | The calibration status line under Calibrate. |
| `GyroCalibrationLabelHoldUntilUtc` | `DateTime` | - | UTC gate before which the 30 Hz pad tick must not overwrite `GyroCalibrationLabel`. The manual Calibrate flow owns the label while a pass runs and briefly after a rejection: the tick pushes the memoized timestamp label unconditionally, which otherwise clobbers "Calibrating…" within one frame and makes a motion-rejected run pixel-identical to nothing happening. |
| `GyroCalibrationGeneration` | `int` | - | Bumped by Reset Calibration so an in-flight manual run knows its result was voided. Reset ignores the busy flag by design (the user may want to abandon a run), and without this the aborted manual pass pinned "Couldn't calibrate" for five seconds over a profile that had just been reset or re-calibrated. Same idiom as the auto latch's run token and the handler's selection re-validation. |
| `GyroCalibrateRequested` | `EventHandler` | - | Raised by Calibrate Gyro in the Gyro group. MainWindow wires the handler to `InputService.GyroCalibrator.RecalibrateAsync` against the slot's selected mapped device. |
| `FireGyroCalibrate` | method | - | Raises `GyroCalibrateRequested`. |
| `GyroResetCalibrationRequested` | `EventHandler` | - | Raised by Reset Calibration. MainWindow handles it. |
| `FireGyroResetCalibration` | method | - | Raises `GyroResetCalibrationRequested`. |
| `GyroCalibrateCommand` | `RelayCommand` | - | Runs `FireGyroCalibrate()`. |
| `GyroResetCalibrationCommand` | `RelayCommand` | - | Runs `FireGyroResetCalibration()`. |
| `ResetGyroSensitivityHCommand` | `RelayCommand` | - | Resets `GyroSensitivityH` to `1.0`. |
| `ResetGyroSensitivityVCommand` | `RelayCommand` | - | Resets `GyroSensitivityV` to `1.0`. |
| `ResetGyroSensitivityUnitsCommand` | `RelayCommand` | - | Resets `GyroSensitivityUnits` to `"Multiplier"`. |
| `ResetGyroInvertPitchCommand` | `RelayCommand` | - | Resets `GyroInvertPitch` to `false`. |
| `ResetGyroCompassYawCommand` | `RelayCommand` | - | Resets `GyroCompassYaw` to `false`. |
| `ResetGyroInvertYawCommand` | `RelayCommand` | - | Resets `GyroInvertYaw` to `false`. |
| `ResetGyroInvertRollCommand` | `RelayCommand` | - | Resets `GyroInvertRoll` to `false`. |
| `ResetGyroApplyToPassthroughCommand` | `RelayCommand` | - | Resets `GyroApplyTuningToPassthrough` to `false`. |
| `ResetGyroRealWorldCalibrationCommand` | `RelayCommand` | - | Resets `GyroRealWorldCalibration` to `0`. |
| `ResetGyroDeadZoneCommand` | `RelayCommand` | - | Resets `GyroDeadZoneDegPerSec` to `3.0`. |
| `ResetGyroTighteningCommand` | `RelayCommand` | - | Resets `GyroTighteningThresholdDegPerSec` to `3.0`. |
| `ResetGyroSmoothingThresholdCommand` | `RelayCommand` | - | Resets `GyroSmoothingThresholdDegPerSec` to `8.0`. |
| `ResetGyroSmoothingWindowCommand` | `RelayCommand` | - | Resets `GyroSmoothingWindowMs` to `50`. |
| `ResetGyroAccelerationCommand` | `RelayCommand` | - | Resets `GyroAcceleration` to `0`. |
| `ResetGyroOutputCurveCommand` | `RelayCommand` | - | Resets `GyroOutputCurve` to `"Linear"`. |
| `ResetGyroEasyAimStickThresholdCommand` | `RelayCommand` | - | Resets `GyroEasyAimStickThreshold` to `0`. |
| `ResetGyroAimEngageButtonCommand` | `RelayCommand` | - | Resets gyro aim engage button to its default. |
| `ResetGyroAimEngageModeCommand` | `RelayCommand` | - | Resets `GyroAimEngageMode` to `"Hold"`. |
| `FireGyroAimEngageRecord` | method | - | Raises `GyroAimEngageRecordRequested`. |
| `ResetGyroCardCommand` | `RelayCommand` | - | Reset All on its card: every row of the card back to its default. |
| `ResetGyroResponseCardCommand` | `RelayCommand` | - | Reset All on its card: every row of the card back to its default. |

### Gyro Aim Engage

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `GyroAimEngageButton` | `string` | `""` | The Aim Engage input's descriptor and the device it is on. `GyroAimEngageSelectedInput` writes both. |
| `GyroAimEngageDeviceGuid` | `string` | `""` | See `GyroAimEngageButton`. |
| `GyroAimEngageMode` | `string` | `"Hold"` | "Hold" (default): gyro fires while the engage button is held. "Toggle": each rising edge flips a sticky per-slot engaged bit. "ReleaseToEngage" (Release to Aim): gyro fires while the engage button is not held. OR-combined with the SetGyroEngaged macro action's bit at the gyro evaluator. Per-(device, slot) like the rest of the gyro tuning, but the runtime state itself is per-slot volatile and resets on profile switch. |
| `GyroAimEngageSelectedInput` | `InputChoice` | - | `InputChoice` projection over the `GyroAimEngageButton` + `GyroAimEngageDeviceGuid` pair. The getter resolves the matching entry in `SlotAvailableInputs`, the setter writes both strings together, and null collapses the picker to its placeholder. |
| `GyroAimEngageRecording` | `bool` | - | Whether the recorder listens for this input. Drives the record button's icon and tooltip. |
| `GyroAimEngageRecordButtonIcon` | `string` | - | Segoe MDL2 glyph: Stop while recording, Record while idle. |
| `GyroAimEngageRecordButtonText` | `string` | - | Localized tooltip for the record button. Mirrors `RecordButtonText`. |
| `GyroAimEngageRecordRequested` | `EventHandler` | - | Fires when the user clicks the Record button next to the Aim Engage picker. MainWindow listens and either starts a freeform recorder session (if idle) or cancels (if already recording), matching the mapping-table Toggle pattern. |
| `GyroAimEngageRecordCommand` | `RelayCommand` | - | Runs the matching `Fire…Record` method. |

### Motion Steering

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `GetSteerableSticks` | method | - | The stick X axes this slot's output exposes, as (label, X target, Y target). Per-stick steering (Winding / Angle) resolves its target against this one list, so a standard gamepad (Left/Right) and an Extended custom layout (one entry per thumbstick, using the same interleaved axis layout the rest of the Extended pipeline uses) go through the same code. |
| `MotionSteerInnerDz` | `double` | `15` | Motion steering's inner deadzone, in degrees. Clamped to 0 to 179. |
| `MotionSteerOuterDz` | `double` | `135` | Motion steering's outer limit, in degrees. Clamped to 0 to 179. |
| `MotionSteerOrientIndex` | `int` | - | How the controller is held for motion steering, as an index into `"Forward"`, `"Left"`, `"Right"`, `"Backward"`. Notifies `MotionSteerOrient`. Clamped to 0 to 3. |
| `MotionSteerOrient` | `string` | - | Computed: the stored name of `MotionSteerOrientIndex`. Clamped to 0 to 3. |
| `SetMotionSteerOrient` | method | - | Sets `MotionSteerOrientIndex` from a stored name. An unknown name reads as Forward. |
| `ResetMotionSteerInnerCommand` | `RelayCommand` | - | Resets `MotionSteerInnerDz` to `15`. |
| `ResetMotionSteerOuterCommand` | `RelayCommand` | - | Resets `MotionSteerOuterDz` to `135`. |
| `ResetMotionSteerOrientCommand` | `RelayCommand` | - | Resets `MotionSteerOrientIndex` to `0`. |
| `ResetMotionSteerAllCommand` | `RelayCommand` | - | Reset All on its card: every row of the card back to its default. |

### Trigger Rumble Routing (#102)

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `LeftTriggerRouteSource` | `string` | `"None"` | Where the left trigger's rumble comes from: `"None"` or a source name (`"MainLeft"` and so on). |
| `IsTriggerRoutingOn` | `bool` | - | Whether either trigger's rumble is routed from a source, for the fold's summary. The two sources are names ("None", "MainLeft" and so on), which a summary cannot read as on or off. |
| `LeftTriggerRouteMode` | `string` | `"Duplicate"` | How the routed rumble combines with the trigger's own (`"Duplicate"` by default). |
| `LeftTriggerRouteScale` | `int` | `100` | The routed rumble's scale in percent. Clamped to 0 to 200. |
| `LeftTriggerRouteActivator` | `string` | `""` | An optional input that gates the routing, its device, and its mode (`"Hold"` by default, an empty write reads as Hold). |
| `LeftTriggerRouteActivatorDeviceGuid` | `string` | `""` | See `LeftTriggerRouteActivator`. |
| `LeftTriggerRouteActivatorMode` | `string` | `"Hold"` | See `LeftTriggerRouteActivator`. |
| `LeftTriggerRouteActivatorSelectedInput` | `InputChoice` | - | InputChoice projection over the left-trigger activator descriptor + device GUID, mirroring `GyroAimEngageSelectedInput`. A null write-back from the ComboBox's TwoWay binding is ignored so a transient empty list (during device switch) doesn't wipe the binding. |
| `LeftTriggerRouteActivatorRecording` | `bool` | - | Whether the recorder listens for this input. Drives the record button's icon and tooltip. |
| `LeftTriggerRouteActivatorRecordButtonIcon` | `string` | - | Segoe MDL2 glyph: Stop while recording, Record while idle. |
| `LeftTriggerRouteActivatorRecordButtonText` | `string` | - | The record button's localized tooltip, which swaps while recording. |
| `LeftTriggerRouteActivatorRecordRequested` | `EventHandler` | - | Raised for MainWindow, which handles it. |
| `FireLeftTriggerRouteActivatorRecord` | method | - | Raises `LeftTriggerRouteActivatorRecordRequested`. |
| `LeftTriggerRouteActivatorRecordCommand` | `RelayCommand` | - | Runs the matching `Fire…Record` method. |
| `ResetLeftTriggerRouteActivatorCommand` | `RelayCommand` | - | Resets left trigger route activator to its default. |
| `RightTriggerRouteSource` | `string` | `"None"` | The right trigger's twin of `LeftTriggerRouteSource`, with the same `Mode`, `Scale` and activator members. |
| `RightTriggerRouteMode` | `string` | `"Duplicate"` | See `RightTriggerRouteSource`. |
| `RightTriggerRouteScale` | `int` | `100` | See `RightTriggerRouteSource`. Clamped to 0 to 200. |
| `RightTriggerRouteActivator` | `string` | `""` | See `RightTriggerRouteSource`. |
| `RightTriggerRouteActivatorDeviceGuid` | `string` | `""` | See `RightTriggerRouteSource`. |
| `RightTriggerRouteActivatorMode` | `string` | `"Hold"` | See `RightTriggerRouteSource`. |
| `RightTriggerRouteActivatorSelectedInput` | `InputChoice` | - | InputChoice projection over the right-trigger activator descriptor + device GUID. See `LeftTriggerRouteActivatorSelectedInput`. |
| `RightTriggerRouteActivatorRecording` | `bool` | - | Whether the recorder listens for this input. Drives the record button's icon and tooltip. |
| `RightTriggerRouteActivatorRecordButtonIcon` | `string` | - | Segoe MDL2 glyph: Stop while recording, Record while idle. |
| `RightTriggerRouteActivatorRecordButtonText` | `string` | - | The record button's localized tooltip, which swaps while recording. |
| `RightTriggerRouteActivatorRecordRequested` | `EventHandler` | - | Raised for MainWindow, which handles it. |
| `FireRightTriggerRouteActivatorRecord` | method | - | Raises `RightTriggerRouteActivatorRecordRequested`. |
| `RightTriggerRouteActivatorRecordCommand` | `RelayCommand` | - | Runs the matching `Fire…Record` method. |
| `ResetRightTriggerRouteActivatorCommand` | `RelayCommand` | - | Resets right trigger route activator to its default. |
| `ResetTriggerRouteCardCommand` | `RelayCommand` | - | Reset All on its card: every row of the card back to its default. |
| `ResetLeftTriggerRouteSourceCommand` | `RelayCommand` | - | Resets `LeftTriggerRouteSource` to `"None"`. |
| `ResetLeftTriggerRouteModeCommand` | `RelayCommand` | - | Resets `LeftTriggerRouteMode` to `"Duplicate"`. |
| `ResetLeftTriggerRouteScaleCommand` | `RelayCommand` | - | Resets `LeftTriggerRouteScale` to `100`. |
| `ResetLeftTriggerRouteActivatorModeCommand` | `RelayCommand` | - | Resets `LeftTriggerRouteActivatorMode` to `"Hold"`. |
| `ResetRightTriggerRouteSourceCommand` | `RelayCommand` | - | Resets `RightTriggerRouteSource` to `"None"`. |
| `ResetRightTriggerRouteModeCommand` | `RelayCommand` | - | Resets `RightTriggerRouteMode` to `"Duplicate"`. |
| `ResetRightTriggerRouteScaleCommand` | `RelayCommand` | - | Resets `RightTriggerRouteScale` to `100`. |
| `ResetRightTriggerRouteActivatorModeCommand` | `RelayCommand` | - | Resets `RightTriggerRouteActivatorMode` to `"Hold"`. |

### Wheel Resets and Novint Falcon Feel (#521)

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ResetWheelRotationRangeCommand` | `RelayCommand` | - | Resets `WheelRotationRange` to `900`. |
| `ResetWheelAutoCenterCommand` | `RelayCommand` | - | Resets `WheelAutoCenter` to `0`. |
| `ResetWheelRpmLedsCommand` | `RelayCommand` | - | Resets `WheelRpmLeds` to `false`. |
| `ResetWheelAllCommand` | `RelayCommand` | - | Reset All on its card: every row of the card back to its default. |
| `FalconFeel` | `int` | - | 0 Joystick, 1 Aim (`FalconFeel`). Clamped to 0 to 1. |
| `FalconIsJoystick` | `bool` | - | The Spring row shows for the Joystick feel, and the Brace and Preload rows for the Aim feel, the feels that read them. |
| `FalconIsAim` | `bool` | - | Computed: `FalconFeel == 1`. |
| `FalconSpring` | `int` | `100` | The Joystick feel's spring, percent of 3 N. Clamped to 0 to 200. |
| `FalconKickButton` | `int` | `1` | The Kick button, 1 to 4, 0 for none. Clamped to 0 to 4. |
| `FalconKick` | `int` | `100` | The Kick button's strength in percent. Clamped to 0 to 200. |
| `FalconShake` | `int` | `100` | The shake's strength in percent. Clamped to 0 to 200. |
| `FalconBraceButton` | `int` | - | The Aim feel's Brace button, 1 to 4, 0 for none. Clamped to 0 to 4. |
| `FalconPreloadButton` | `int` | - | The Aim feel's Preload button, 1 to 4, 0 for none. Clamped to 0 to 4. |
| `FalconGravity` | `int` | `100` | Gravity compensation, percent of standard gravity. Clamped to 0 to 200. |
| `FalconForceCap` | `int` | `8` | The force cap in newtons. Clamped to 1 to 8. |
| `ResetFalconSpringCommand` | `RelayCommand` | - | Resets `FalconSpring` to `100`. |
| `ResetFalconKickCommand` | `RelayCommand` | - | Resets `FalconKick` to `100`. |
| `ResetFalconShakeCommand` | `RelayCommand` | - | Resets `FalconShake` to `100`. |
| `ResetFalconGravityCommand` | `RelayCommand` | - | Resets `FalconGravity` to `100`. |
| `ResetFalconForceCapCommand` | `RelayCommand` | - | Resets `FalconForceCap` to `8`. |
| `ResetFalconAllCommand` | `RelayCommand` | - | Reset All on its card: every row of the card back to its default. |

### Trigger Motor Displays

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `DeviceLeftTriggerMotorDisplay` | `double` | - | The selected device's own trigger-motor activity, the impulse triggers' twin of `DeviceLeftMotorDisplay`. |
| `DeviceRightTriggerMotorDisplay` | `double` | - | See `DeviceLeftTriggerMotorDisplay`. |
| `RawLeftMotorDisplay` | `double` | - | The motor command the GAME put on the virtual pad, before any device's settings. The Force Feedback group's raw bar reads this and its output bar reads the selected device's scaled value, so the gap between them is the user's settings. It used to read the slot meter, which is already past every device's settings, so both bars showed processed values under different labels. |
| `RawRightMotorDisplay` | `double` | - | See `RawLeftMotorDisplay`. |
| `DeviceLeftMotorDisplay` | `double` | - | Selected device's own motor activity (its PadSetting's gain / motor strengths / audio rumble / constant force applied to the slot's raw vibration). Drives the Force Feedback group's motor bar: that meter MUST be device-specific so users editing one device's FFB settings see what's effectively reaching THAT device, not the slot-wide max. |
| `DeviceRightMotorDisplay` | `double` | - | See `DeviceLeftMotorDisplay`. |

### Impulse and Audio Trigger Resets

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ResetImpulseAllCommand` | `ICommand` | - | Reset All on its card: every row of the card back to its default. |
| `ResetImpulseOverallGainCommand` | `ICommand` | - | Resets `ImpulseOverallGain` to `100`. |
| `ResetImpulseLeftCommand` | `ICommand` | - | Resets `ImpulseLeftStrength` to `100`. |
| `ResetImpulseRightCommand` | `ICommand` | - | Resets `ImpulseRightStrength` to `100`. |
| `ResetConstantTriggerLeftCommand` | `ICommand` | - | Resets `ConstantTriggerForceLeft` to `0`. |
| `ResetConstantTriggerRightCommand` | `ICommand` | - | Resets `ConstantTriggerForceRight` to `0`. |
| `ResetAudioTriggerRumbleAllCommand` | `ICommand` | - | Reset All on its card: every row of the card back to its default. |
| `ResetAudioTriggerSensitivityCommand` | `ICommand` | - | Resets `AudioRumbleTriggersSensitivity` to `4.0`. |
| `ResetAudioTriggerCutoffCommand` | `ICommand` | - | Resets `AudioRumbleTriggersCutoffHz` to `80.0`. |
| `ResetAudioLeftTriggerCommand` | `ICommand` | - | Resets `AudioRumbleLeftTrigger` to `100`. |
| `ResetAudioRightTriggerCommand` | `ICommand` | - | Resets `AudioRumbleRightTrigger` to `100`. |
| `TestLeftImpulseTriggerCommand` | `RelayCommand` | - | Raise `TestLeftImpulseTriggerRequested` / `TestRightImpulseTriggerRequested`. CanExecute: `IsDeviceOnline`. |
| `TestRightImpulseTriggerCommand` | `RelayCommand` | - | See `TestLeftImpulseTriggerCommand`. |

### Steering Lock Feedback

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `SteeringLockRumbleEnabled` | `bool` | - | What fires when a steering stick hits its lock: a rumble pulse, a trigger vibration, a lightbar flash and an adaptive-trigger resistance. |
| `SteeringLockTriggerVibEnabled` | `bool` | - | See `SteeringLockRumbleEnabled`. |
| `SteeringLockLightbarEnabled` | `bool` | - | See `SteeringLockRumbleEnabled`. |
| `SteeringLockATResistanceEnabled` | `bool` | - | See `SteeringLockRumbleEnabled`. |
| `SteeringLockPulseMs` | `double` | `80` | The rumble pulse's length in milliseconds. Clamped to 0 to 2000. |
| `SteeringLockLightbarColor` | `string` | `"#FF0000"` | The flash's fixed color as `#RRGGBB`, which `SteeringLockColorR` / `G` / `B` edit. |
| `SteeringLockColorR` | `byte` | - | See `SteeringLockLightbarColor`. |
| `SteeringLockColorG` | `byte` | - | See `SteeringLockLightbarColor`. |
| `SteeringLockColorB` | `byte` | - | See `SteeringLockLightbarColor`. |
| `SteeringLockLightbarHoldMs` | `double` | `80` | How long the flash holds, in milliseconds. Clamped to 0 to 2000. |
| `SteeringLockLightbarFadeMs` | `double` | `250` | How long the flash fades, in milliseconds. Clamped to 0 to 5000. |
| `SteeringLockLightbarColorSource` | `MacroLightbarColorSource` | `MacroLightbarColorSource.Fixed` | Where the flash's color comes from: `Fixed`, or a palette step. |
| `IsSteeringLockLightbarFixedColorVisible` | `bool` | - | Show the fixed-color picker only for the Fixed source. |
| `IsSteeringLockLightbarPaletteVisible` | `bool` | - | Show the dedicated palette editor only for the PaletteStep source. |
| `SteeringLockLightbarPaletteCsv` | `string` | `string.Empty` | The palette as stored text, which `SteeringLockLightbarPalette` edits. |
| `SteeringLockLightbarPalette` | `ObservableCollection<LightbarPaletteEntry>` | - | Editable view of the steering-lock palette, bound by the card's ItemsControl. Edits write back to `SteeringLockLightbarPaletteCsv`. |
| `AddSteeringLockPaletteColorCommand` | `ICommand` | - | Adds a white entry to `SteeringLockLightbarPalette`. |
| `RemoveSteeringLockPaletteColorCommand` | `ICommand` | - | Removes the entry passed as its parameter from `SteeringLockLightbarPalette`. |
| `ResetSteeringLockColorRCommand` | `ICommand` | - | Resets `SteeringLockColorR` to `0xFF`. |
| `ResetSteeringLockColorGCommand` | `ICommand` | - | Resets `SteeringLockColorG` to `0x00`. |
| `ResetSteeringLockColorBCommand` | `ICommand` | - | Resets `SteeringLockColorB` to `0x00`. |
| `ResetSteeringLockPulseCommand` | `ICommand` | - | Resets `SteeringLockPulseMs` to `80`. |
| `ResetSteeringLockLightbarHoldCommand` | `ICommand` | - | Resets `SteeringLockLightbarHoldMs` to `80`. |
| `ResetSteeringLockFadeCommand` | `ICommand` | - | Resets `SteeringLockLightbarFadeMs` to `250`. |
| `ResetSteeringLockRumbleCommand` | `ICommand` | - | Resets `SteeringLockRumbleEnabled` to `false`. |
| `ResetSteeringLockTriggerVibCommand` | `ICommand` | - | Resets `SteeringLockTriggerVibEnabled` to `false`. |
| `ResetSteeringLockLightbarCommand` | `ICommand` | - | Resets `SteeringLockLightbarEnabled` to `false`. |
| `ResetSteeringLockResistanceCommand` | `ICommand` | - | Resets `SteeringLockATResistanceEnabled` to `false`. |
| `ResetSteeringLockAllCommand` | `ICommand` | - | Reset All on its card: every row of the card back to its default. |
| `ResetConstantForceXCommand` | `ICommand` | - | Resets `ConstantForceX` to `0`. |
| `ResetConstantForceYCommand` | `ICommand` | - | Resets `ConstantForceY` to `0`. |

### Sticks: Steering and Boundary

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `SteeringModeChangedCallback` | `Action` | - | Wired by MainWindow to re-stamp the engine's per-slot MappingSets immediately on a steering-mode change (including Reset all -> Direct), so the stick stops/starts steering at once instead of after the 2s autosave. |
| `ResetBothSticksCommand` | `RelayCommand` | - | Runs `ResetSteeringLockAllCommand` and `ResetFlickStickCardCommand`. |
| `LeftThumbBoundaryMap` | `string` | `""` | The left and right sticks' boundary calibration (#174), as stored text. |
| `RightThumbBoundaryMap` | `string` | `""` | See `LeftThumbBoundaryMap`. |
| `SteeringReloadCallback` | `Action` | - | Invoked at the end of `RebuildStickConfigs` so the host can re-load the selected assigned device's steering into the freshly-rebuilt items (rebuild resets steering to defaults and SyncStickItemFromVm doesn't cover it). |
| `LoadSteeringConfigItems` | method | - | Loads each stick's steering mode + tunables from the SELECTED assigned device's stored values, with the dirty callback suppressed (mirrors the guarded deadzone sync). Steering is per assigned device, so this runs on every device select and after a rebuild. `get` resolves a steering key (e.g. "Stick0SteerKind") for the selected device. Steering has no flat VM mirror property, so it loads straight onto the items. |

### Audio Group: Device Capabilities

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `SelectedDeviceIsDualSenseFamily` | `bool` | - | The selected device is a DualSense or a DualSense Edge. The Output Path tooltip states their firmware's limits, which a DualShock 4 on the same row does not share: it takes the row through its own routes (#528, #546). |
| `SelectedDeviceHasDs5AudioBuffer` | `bool` | - | The selected device takes the DS5 audio buffer-length byte. That byte exists only in the DualSense BLUETOOTH packet 0x11 header (every ResolveAudioBufferLength call site is a BT report builder), so gating its slider on the headphone-jack rule showed a control that does nothing on a USB DualSense: same PID, no packet 0x11. The transport test is the one SelectedDeviceHasDspChain already uses for the DualShock 4. |
| `SelectedDeviceHasSpeaker` | `bool` | - | True when PadForge has a path to a speaker on the SELECTED assigned device over its link (DualSense / Edge, a DualShock 4 on a link that carries audio, and the Wii and haptic-tone devices). It does not say whether the device has a speaker: a first-model DualShock 4 on USB has one and no path from PadForge. The Audio group is per assigned device by convention. This gates the mirror toggle and the routing notes, and the line that says there is no path (Pad_Audio_NoSpeakerRoute). |
| `SelectedDeviceHasNoSpeaker` | `bool` | - | Computed: `!SelectedDeviceHasSpeaker`. |
| `SelectedDeviceHasHapticTones` | `bool` | - | True when the SELECTED assigned device plays haptic TONES (Joy-Con, Switch Pro, Steam family, a Flydigi Apex 6 Pro with voice coils) rather than real speaker audio (`HapticToneService.DeviceHasHaptics`). Gates the mirror engage row (#185): the engage gate exists because a resonant actuator buzzing with music is intrusive in a way a real speaker is not, so Sony / Wii speaker devices do not show it. It also gates the Audio card's panel that holds Play DualSense Haptics on This Controller, Haptics Gain and the Steam Controller (2026)'s Actuator Low-Pass Cutoff. That panel is apart from the high-tone filter's, so an Apex 6 Pro, which hides the filter, shows the switch and its gain. |
| `SelectedDeviceHasToneFilter` | `bool` | - | True when the SELECTED assigned device reduces what it plays to one pitch a tick, which is what the high-tone filter acts on. A Flydigi Apex 6 Pro plays the mix as samples (#586), so the filter has nothing to act on there and is not shown. |
| `SelectedDeviceIsTritonPcm` | `bool` | - | True when the SELECTED assigned device is a Steam Controller 2026 on a PCM-capable transport (wired 0x1302 or a dongle 0x1304/0x1305), the set the #381 native PCM stream drives. Gates the actuator low-pass card: on BLE (0x1303) and every other haptic family the setting has no effect, so it is not shown there. |
| `SelectedDeviceHasTouchpadPulse` | `bool` | - | True when the SELECTED assigned device has a touchpad AND a haptic lane the swipe-tick feature can drive (Steam Controller family actuators, or a dispatcher-driven Sony pad). Gates the Touchpad group's Swipe Haptics card (#219) so devices whose touchpads have no haptics (Precision Touchpads, the overlay, web controllers) don't show a dead toggle. |

### Audio Group: Mirror and Haptic Tones

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `MirrorEngageSelectedInput` | `InputChoice` | - | InputChoice projection over the selected device's AudioMirrorEngageButton + AudioMirrorEngageDeviceGuid pair (#185), mirroring `GyroAimEngageSelectedInput`: the getter resolves the matching entry in `SlotAvailableInputs`, the setter writes both backing strings atomically, and a null write-back from the ComboBox is ignored because the getter returns null any time the list has not been rebuilt yet for the newly selected device. Treating that transient null as a user clear would silently wipe the saved binding on every device switch. |
| `MirrorEngageRecording` | `bool` | - | Whether the engage-input recorder is listening for the next physical input. Drives the record button's icon + tooltip swap, mirroring `GyroAimEngageRecording`. |
| `MirrorEngageRecordButtonIcon` | `string` | - | Segoe MDL2 glyph: Stop while recording, Record while idle. Same literals as the gyro twin. |
| `MirrorEngageRecordButtonText` | `string` | - | Localized tooltip for the record button. |
| `MirrorEngageRecordRequested` | `EventHandler` | - | Fires when the user clicks the Record button next to the engage-input picker. MainWindow starts or cancels a freeform recorder session, matching the Aim Engage pattern. |
| `FireMirrorEngageRecord` | method | - | Raises `MirrorEngageRecordRequested`. |
| `MirrorEngageRecordCommand` | `RelayCommand` | - | Runs the matching `Fire…Record` method. |
| `ResetMirrorEngageModeCommand` | `RelayCommand` | - | Per-row resets of the Sound Output rows on the selected device's config: the mirror engage mode and release time (#185), the tone filter mode and limit (#202), persona haptics and its gain (#271), and the Steam Controller 2026's actuator low-pass (#381). |
| `ResetMirrorEngageInputCommand` | `RelayCommand` | - | The sanctioned clear path for the engage input (the picker's null-writeback guard exists because of it). |
| `ResetMirrorEngageReleaseMsCommand` | `RelayCommand` | - | See `ResetMirrorEngageModeCommand`. |
| `ResetToneFilterModeCommand` | `RelayCommand` | - | See `ResetMirrorEngageModeCommand`. |
| `ResetPersonaHapticsCommand` | `RelayCommand` | - | See `ResetMirrorEngageModeCommand`. |
| `ResetPersonaHapticsGainCommand` | `RelayCommand` | - | See `ResetMirrorEngageModeCommand`. |
| `ResetTritonLowPassCommand` | `RelayCommand` | - | See `ResetMirrorEngageModeCommand`. |
| `ResetToneLimitHzCommand` | `RelayCommand` | - | See `ResetMirrorEngageModeCommand`. |
| `ResetMirrorSourceCommand` | `RelayCommand` | - | Clears the mirror source back to the system default endpoint (Id ""), the same value the Sound Output "Reset All" path writes. |
| `ResetAudioMirrorCommand` | `RelayCommand` | - | Per-row reset for the system-audio mirror toggle. The Audio card's Reset All already covers it. This is the row affordance every setting row carries. |
| `MirrorSourceOption` | type | - | A render endpoint the mirror can capture. Id "" = the system default device. One entry in an audio endpoint picker. Observable because the refresh below RETAINS the instance on purpose (rebuilding the list drops the ComboBox's selected item and WPF clears the selection), so a caption change has to reach the binding through the object rather than through the collection. |
| `MirrorSourceOptions` | `ObservableCollection<MirrorSourceOption>` | - | The mirror source picker's entries, refreshed by `RefreshMirrorSources()`. |
| `RefreshMirrorSources` | method | - | Repopulates `MirrorSourceOptions` from the active render endpoints. Guarded: rebuilding the ItemsSource makes WPF write a transient null through SelectedValue (the Aim Engage picker documents the same hazard), so config writes are suppressed while the list is swapped. |
| `SelectedMirrorSourceId` | `string` | - | ComboBox-facing proxy over DeviceConfig.AudioMirrorSourceId that ignores the transient null write-back during ItemsSource rebuilds. |

`MirrorSourceOption` carries `Id` (`""` for the system default) and `Name` (default `"Unknown"`).

### Audio Group: Sound Macros

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `SoundMasterVolume` | `int` | `100` | Per-pad master volume for macro sounds (0-100), multiplied with each action's own volume. Live sounds retune. Clamped to 0 to 100. |
| `SoundMacros` | `List<MacroItem>` | - | This pad's macros that play a sound, the Sound Macros fold's list. Raised when the Audio group comes on the page, when a macro comes or goes, and when a macro's steps or a step's type change: a profile switch replaces the macros while the section can be showing. |
| `HasNoSoundMacros` | `bool` | - | Computed: `SoundMacros.Count == 0`. |
| `SoundTestCommand` | `RelayCommand` | - | Plays a test on the selected device: a fixed haptic tone on a haptic device, else the audio beep. CanExecute: `HasSelectedDevice`. |
| `SoundStopAllCommand` | `RelayCommand` | - | Stops every sound this slot plays. |
| `ResetSoundMasterVolumeCommand` | `RelayCommand` | - | Resets `SoundMasterVolume` to `100`. |
| `ResetSoundOutputAllCommand` | `RelayCommand` | - | Resets the Sound Output card for the selected device, the WHOLE card: mirror off, mirror source back to system default, master volume to 100%, the #185 engage gate back to Always with its defaults, the #202 tone filter back to Off / 800 Hz, the #271 persona haptics off at 100%, the #314 Bluetooth audio buffer back to its default, headphone volume and output path, and the whole #347 DSP chain (crossfeed off with the custom knobs at bs2b's defaults, EQ off with no bands and no preamp, limiter on at 98%). A reset-all that skips rows it does not know about is the defect the "Clear All resets the ENTIRE row surface" rule exists to forbid. The 4.3.2 docs sweep caught this one skipping eight rows across three features that had each landed after it was written. The EQ rows are cleared through ClearEqBandsCommand so the grid and the config agree. |
| `AddSoundMacroCommand` | `RelayCommand` | - | Creates a macro pre-loaded with a Play Sound action and jumps to the Macros part of Macros & Menus to finish it (trigger + file): the "best of both worlds" flow: the Audio group is the hub, the macro editor is the editor. |
| `OpenSoundMacro` | method | - | Jumps to the Macros part of Macros & Menus with the clicked sound macro selected. |
| `RefreshAudioGroup` | method | - | The Audio group comes on the page: re-derive the sound-macro list, the selected device's speaker capability, and the mirror-source endpoint list. |

### Pointer (#146, #203)

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `IrSensorBarPos` | `int` | - | Sensor-bar position for the IR pointer (issue #146): 0 = centered, 1 = above the screen, 2 = below. Per (device, slot) on PadSetting like every other pad-page tunable, so two virtual controllers sharing one remote keep independent pointer feel. Read at runtime through SourceCoercion.IrTuningProvider. Clamped to 0 to 2. |
| `IrSensorBarCompPercent` | `int` | - | Sensor-bar vertical-offset magnitude, shown as 0..50 percent of the pointer range and stored as 0..0.5 on `IrSensorBarComp` (issue #146). Clamped to 0 to 50. |
| `IrSmoothingPercent` | `int` | - | IR pointer smoothing, shown as 0..100 percent and stored as 0..1 on `IrSmoothing` (issue #146). Clamped to 0 to 100. |
| `PointerMode` | `string` | `"Mouse"` | Wii pointer mode (issue #203): "Mouse", "FpsMouse", "Mouse43", "Mouse169". Per (device, slot) on `PointerMode`. Shapes the cursor drive only. "IR Pointer X/Y" mapping sources stay raw. |
| `PointerFpsSpeed` | `int` | `35` | FPS Mouse speed (issue #203), the lineage's fpsmouse speed knob. 35 default, clamped 5..100. |
| `ResetPointerModeCommand` | `RelayCommand` | - | Resets `PointerMode` to `"Mouse"`. |
| `ResetPointerFpsSpeedCommand` | `RelayCommand` | - | Resets `PointerFpsSpeed` to `35`. |
| `ResetIrSensorBarPosCommand` | `RelayCommand` | - | Resets `IrSensorBarPos` to `0`. |
| `ResetIrSensorBarCompCommand` | `RelayCommand` | - | Resets `IrSensorBarCompPercent` to `0`. |
| `ResetIrSmoothingCommand` | `RelayCommand` | - | Resets `IrSmoothingPercent` to `0`. |
| `ResetIrPointerCardCommand` | `RelayCommand` | - | Reset All on its card: every row of the card back to its default. |

### Bass Shakers Members (#236)

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `RumbleAudioEndpointOptions` | `ObservableCollection<MirrorSourceOption>` | - | Active render endpoints for the output picker. Reuses the mirror-source option shape (Id "" = system default). |
| `RefreshRumbleAudioEndpoints` | method | - | Repopulates `RumbleAudioEndpointOptions` from the active render endpoints. Diff-syncs in place so the ComboBox selection rides through a refresh (never Clear()). A configured endpoint that is currently absent stays listed as unavailable so the fail-closed selection remains visible. |
| `ReloadRumbleAudio` | method | - | Rebuilds the Bass Shakers group's state from the slot's live MappingSet. Called beside `ReloadMenus` from every path that swaps or rewrites the slot set (profile apply, Workshop import, output-type change, Reset to Defaults, paste, Copy From Slot, slot delete). |
| `WriteRumbleAudioVoice` | method (internal) | - | Writes one voice row's edits into the DTO voice, authoring the voice entry when the config predates it. Clamped to 0 to 100. |
| `ResetRumbleAudioEnabledCommand` | `RelayCommand` | - | Per-row reset for the enable toggle. Default is off. |
| `ResetRumbleAudioEndpointCommand` | `RelayCommand` | - | Resets `RumbleAudioEndpointId` to `string.Empty`. |
| `ResetRumbleAudioChannelModeCommand` | `RelayCommand` | - | Resets `RumbleAudioChannelMode` to `string.Empty`. |
| `ResetRumbleAudioMasterGainCommand` | `RelayCommand` | - | Resets `RumbleAudioMasterGain` to `50`. |
| `ResetRumbleAudioAllCommand` | `RelayCommand` | - | Card-level Reset All: endpoint to system default, mono, master gain 50, every voice to enabled / 100 / default carrier. Keeps Enabled as it is (the enable row's own reset covers it). |
| `RumbleAudioSweepCommand` | `RelayCommand` | - | Resonance finder: sweeps 20..120 Hz over eight seconds on the low-voice routing. |
| `RumbleAudioStopTestCommand` | `RelayCommand` | - | Stops a running test or sweep (`RumbleAudioService.StopTest`). |
| `RumbleAudioVoiceItem` | type | - | One Bass Shakers voice row (#236). Keyed by voice index into `SourceOrder`. Edits route through the owner so the row never holds a reference to a DTO the profile-apply path may have replaced. |
| `RefreshBassShakersGroup` | method | - | The Bass Shakers group comes on the page: re-enumerate render endpoints so hot-plugged devices show up, and re-seed the rows from the slot set. |

`RumbleAudioVoiceItem` is one voice row:

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `Label` | `string` | - | Localized row label, live lookup so a language switch re-renders without rebuilding the list. |
| `ResetTooltip` | `string` | - | Per-row reset tooltip, "Reset {Row}" per canon. |
| `RaiseWords` | method (internal) | - | Has the row's label and its reset's tooltip read again: the language changed. |
| `Enabled` | `bool` | `true` | Per-voice enable. Gain and frequency stay authored while muted. |
| `GainPercent` | `int` | `100` | Voice gain percent, 0..100, before master gain. Clamped to 0 to 100. |
| `FrequencyHz` | `int` | - | Sine carrier frequency in Hz, 20..120. Clamped to RumbleAudioConfig.MinFrequencyHz to RumbleAudioConfig.MaxFrequencyHz. |
| `MeterLevel` | `double` | - | Live activity 0..100 for the row meter, written by the page's meter timer. Never persisted. |
| `TestCommand` | `RelayCommand` | - | Plays this voice for 1.5 seconds at authored gain. |
| `ResetCommand` | `RelayCommand` | - | Row reset: enabled, gain 100, default carrier. |
| `ResetToDefault` | method (internal) | - |  |
| `LoadFrom` | method (internal) | - | Re-seeds the row from the DTO voice (null reads as the source's default voice) without writing back. |

### Slot SOCD Members (#245)

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ReloadSocd` | method | - | Re-seeds the SOCD card from the slot's MappingSet. Called on the same paths that reload Menus and RumbleAudio (RebuildMappings, slot delete, Paste, Copy From Slot). |
| `AddSocdPairCommand` | `RelayCommand` | - | Appends a fresh pair for the user to retarget: the D-Pad Left / Right opposites on gamepad slots, raw indices 0 and 1 on Extended slots. |
| `RemoveSocdPairCommand` | `RelayCommand<SlotSocdPairItem>` | - | Removes the pair passed as its parameter. |
| `ResetSocdModeCommand` | `RelayCommand` | - | Per-row reset for the mode combo. Default is off. |
| `ResetSocdCardCommand` | `RelayCommand` | - | Card-level Reset All: mode off, every pair removed. |

### Extended Raw State

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `UpdateFromRawDeviceState` | method | - | Updates per-stick and per-trigger live values for the Extended stick and trigger groups. Caller passes either the selected device's `RawHidOutputState` or, when no device is selected, the combined slot raw state as a fallback so the groups always show something. Does NOT write `RawHidOutputSnapshot`: that field is owned by the schematic preview path. |

### Reset Members

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ResetSettingCommand` | `RelayCommand<string>` | - | The generic per-setting reset (see [Per-Setting Reset Commands](#per-setting-reset-commands)). |
| `CanResetSetting` | method (internal, static) | - | The names `ResetSettingCommand` accepts on this class. |
| `ResetGyroEngageCardCommand` | `RelayCommand` | - | Reset All on its card: every row of the card back to its default. |

### Touchpad Group Resets

One per-row reset for each touchpad setting above, each back to the default its table gives: `ResetTouchpadGesturesEnabledCommand`, `ResetTouchpadGestureModeCommand`, `ResetTouchpadCooldownMsCommand`, `ResetTouchpadEnableFourWaySwipesCommand`, `ResetTouchpadEnableEightWaySwipesCommand`, `ResetTouchpadSwipeDistanceThresholdCommand`, `ResetTouchpadSwipeTimeWindowMsCommand`, `ResetTouchpadEnableRadialZonesCommand`, `ResetTouchpadEnableTouchSpotsCommand`, `ResetTouchpadRadialZoneCountCommand`, `ResetTouchpadRadialCenterDeadzoneCommand`, `ResetTouchpadEnableTapsCommand`, `ResetTouchpadTapTimeWindowMsCommand`, `ResetTouchpadMultiTapGapMsCommand`, `ResetTouchpadEnableLongPressCommand`, `ResetTouchpadLongPressTimeWindowMsCommand`, `ResetTouchpadEnableTwoFingerSwipesCommand`, `ResetTouchpadEnablePinchSpreadCommand`, `ResetTouchpadEnableRotateCommand`, `ResetTouchpadEnableThreeFingerGesturesCommand`, `ResetTouchpadEnableFourFingerGesturesCommand`, `ResetTouchpadEnableFiveFingerGesturesCommand`, `ResetTouchpadEnableShapeGesturesCommand`, `ResetTouchpadGestureMatchThresholdCommand`, `ResetTouchpadEnableJoystickOutputCommand`, `ResetTouchpadJoystickMaxRadiusCommand`, `ResetTouchpadJoystickInnerDeadzoneCommand`, `ResetTouchpadJoystickDPadModeCommand`, `ResetTouchpadJoystickDPadActivationThresholdCommand`, `ResetTouchpadMouseSensitivityXCommand`, `ResetTouchpadMouseSensitivityYCommand`, `ResetTouchpadMouseInvertXCommand`, `ResetTouchpadMouseInvertYCommand`, `ResetTouchpadMouseMomentumCommand`, `ResetTouchpadMouseMomentumDecayCommand`, `ResetTouchpadMomentumMaxSpeedCommand`, `ResetTouchpadMomentumMinLiftCommand`, `ResetTouchpadMomentumFlingGainCommand`, `ResetTouchpadMomentumStackingCommand`, `ResetTouchpadPointerResponseCommand`, `ResetTouchpadTrackpadThresholdCommand`, `ResetTouchpadTrackpadPadWidthCommand`, `ResetTouchpadMouseAccelerationCommand`, `ResetTouchpadMouseJitterReductionCommand`, `ResetTouchpadTapMaxMotionCommand`, `ResetTouchpadLongPressMaxMotionCommand`, `ResetTouchpadTwoFingerSwipeAngularToleranceCommand`, `ResetTouchpadPinchThresholdCommand`, `ResetTouchpadRotateThresholdDegreesCommand`, `ResetTouchpadPointerRegionSizeXCommand`, `ResetTouchpadPointerRegionSizeYCommand`, `ResetTouchpadPointerRegionCenterXCommand`, `ResetTouchpadPointerRegionCenterYCommand`, `ResetTouchpadSwipeHapticsEnabledCommand`, `ResetTouchpadSwipeHapticsIntensityCommand`, `ResetTouchpadSyntheticPressureEnabledCommand`, `ResetTouchpadSyntheticTouchPercentCommand`. `FindPointerRegionAxis` (internal static) searches every slot's mapping set for an imported Steam config's pointer region, one axis at a time. `FireMouseGestureCustomEngageRecord()` raises `MouseGestureCustomEngageRecordRequested`.

### Output Snapshots (for custom previews)

| Property | Type | Description |
|----------|------|-------------|
| `RawHidOutputSnapshot` | `RawHidState` | Latest raw-HID state for the Extended / Nintendo schematic. Updated at 30 Hz by `UpdateFromRawHidState`, which raises `PropertyChanged` for it. Private setter. |
| `KbmOutputSnapshot` | `KbmRawState` | Latest KBM raw state. Updated at 30 Hz. Plain auto-property, no change notification: the view polls it. |
| `VrOutputSnapshot` | `VrRawState` | Latest VR raw state for the VR preview (#49). Same plain auto-property contract as the KBM twin. |
| `MidiOutputSnapshot` | `MidiRawState` | Latest MIDI raw state snapshot. |

---

## MappingItem

**File:** `MappingItem.cs`

Single mapping row linking a physical input to an output target in the controller page's mapping list.

### Target (Output)

| Property | Type | Description |
|----------|------|-------------|
| `TargetLabel` | `string` | Display label (e.g., `"A"`, `"Left Stick X"`, `"CC 1"`). Read-only. |
| `TargetSettingName` | `string` | PadSetting property name (e.g., `"ButtonA"`, `"LeftThumbAxisX"`). Read-only. |
| `Category` | `MappingCategory` | Grouping: `Buttons`, `DPad`, `Triggers`, `LeftStick`, `RightStick`, `Touchpad`, `Motion`. |
| `NegSettingName` | `string` | Negative-direction PadSetting property. Null for non-axis targets. |
| `HasNegDirection` | `bool` | Computed: `NegSettingName != null`. |

### Source (Physical Input)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `SourceDescriptor` | `string` | `""` | Physical input descriptor. Format: `"{MapType} {Index}"`, `"IH{MapType} {Index}"`, or `"POV {Index} {Direction}"`. Empty = unmapped. Notifies `SourceDisplayText` and `IsMapped`. |
| `NegSourceDescriptor` | `string` | `""` | Negative-direction descriptor for stick axes. |
| `SourceDisplayText` | `string` | - | Computed: readable text. Bidirectional axes show `"neg / pos"`. Falls back to `"Not mapped"`. |
| `IsMapped` | `bool` | - | Computed: true if either `SourceDescriptor` or `NegSourceDescriptor` is non-empty. |

| Method | Description |
|--------|-------------|
| `SetResolvedSourceText(string)` | Sets display text (e.g., `"A"` instead of `"Button 65"`). Called by InputService. |
| `SetResolvedNegText(string)` | Sets resolved text for negative direction. |
| `LoadDescriptor(string)` | Sets source descriptor, syncs `IsInverted`/`IsHalfAxis` from prefix flags. |
| `LoadNegDescriptor(string)` | Loads negative-direction descriptor. |
| `SyncSelectedInputFromDescriptor()` | Syncs `SelectedInput` to current `SourceDescriptor` without re-triggering update. |

### Source Input Dropdown

| Property | Type | Description |
|----------|------|-------------|
| `AvailableInputs` | `ObservableCollection<InputChoice>` | Source dropdown choices, spanning every device assigned to the slot. Populated by InputService once per VC slot, not per device-dropdown change. Since #322 every row on a slot points at a shared list (`UseSharedAvailableInputs`), so a keyboard-and-mouse tab switch no longer rebuilds a private copy and a grouped view per row. Since #475 the Motion Gyro and Motion Accelerometer rows point at the slot's motion lists and every other row at `SlotAvailableInputs` (`InputService.PickerListForRow`). |
| `ParamInputs` / `ParamInputsView` | `ObservableCollection<InputChoice>` / `ICollectionView` | (#475) The slot's list, `SlotAvailableInputs`, for the modifier picker and for `MappingSourceItem.ResolveParamChoice`, which resolves the modifier and both keys. It differs from `AvailableInputs` only on the Motion Gyro and Motion Accelerometer rows, where an Invert On Hold modifier still needs a button. Set by `UseSharedParamInputs`, which collapses back to `AvailableInputs` when the two are the same list. |
| `KeyInputs` / `KeyInputsView` | `ObservableCollection<InputChoice>` / `ICollectionView` | The Up and Down pickers' list, `PadViewModel.SlotKeyInputs`, set by `UseSharedKeyInputs`. A row no slot has filled holds an empty list of its own. A key saved before the pickers were narrowed, a stick or a trigger, resolves from `ParamInputs` to an entry this list lacks, so its picker shows no selection. The saved descriptor stays: the picker's null write-back is ignored (#160), and a pick or the reset button replaces it. |
| `AvailableInputsView` | `ICollectionView` | The grouped view the XAML ComboBox binds to. `GroupDescriptions` carries one `PropertyGroupDescription` on `InputChoice.DeviceLabel`, so the picker renders one dropdown with device-name headers. The default view is one object per collection, so on the shared list every row lands on the same view and the grouping is configured once. |
| `SelectedInput` | `InputChoice` | Selected dropdown input. Updates `SourceDescriptor`. Empty sentinel triggers `ClearCommand`. Suppression flag prevents re-entrancy, and is held across the shared-list rebuild (`BeginSharedListRebuild` / `EndSharedListRebuild`) so a live ComboBox cannot write its own selection back through the TwoWay binding. |

| Event | Description |
|-------|-------------|
| `InputSelectedFromDropdown` | Input selected from dropdown (for display text resolution). |

### Recording

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `IsRecording` | `bool` | `false` | Recording mode active. Notifies `RecordButtonText` and `RecordButtonIcon`. |
| `RecordButtonText` | `string` | - | Computed: `"Record"` or `"Recording…"`. |

### Live Value Display

| Property | Type | Description |
|----------|------|-------------|
| `CurrentValueText` | `string` | Source input raw value. Updated at 30 Hz when visible. |

### Per-Mapping Deadzone

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `MappingDeadZone` | `int` | `50` | Axis activation threshold, clamped 1–100%. Input below this percentage is ignored for this mapping row. `0` is disallowed because it used to read as "unset" and silently reverted to 50. |
| `IsDeadZoneApplicable` | `bool` | - | Computed: true for axis-based mappings where a per-mapping deadzone is meaningful, and on a gamepad trigger row whose primary is in Rapid Trigger, where it is the actuation point (#482). |

| Command | Description |
|---------|-------------|
| `ResetDeadZoneCommand` | Resets `MappingDeadZone` to 50. |

`PadViewModel.ClearAllMappings` resets all mapping deadzones to 50.

Two internal static helpers on `MappingItem` hold the button-read rules so other editors share them (#566). `ButtonReadThresholds(desc)` is true when a button read of a source, given as its prefix-stripped body, presses at the source's deadzone: an axis or a slider (the abstract Gamepad sticks and triggers among them) and the engine's continuous families (mouse motion, IR pointer, balance, gyro, mouse position, MIDI CC, touchpad gesture axes, pointer and pressure, and `SourceCoercion.IsThresholdedButtonFamily`). The Mappings grid's `IsDeadZoneApplicable` and the keyboard menu's press point (`KeyboardInputRow.ShowsThreshold`) both ask it. `ButtonReadPressesNothing(descriptor)` is true for a touchpad finger's X or Y, whole or windowed, which the button read has no threshold for (`SourceCoercion.ReadAsBool`'s touchpad branch reads Click, `Finger M Down`, rings, pressure and the absolute pointer only). A list for a button target leaves these out (`PadViewModel.SlotButtonInputs`, a keyboard menu's press rows).

### Options

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `IsInverted` | `bool` | `false` | Axis inverted. Calls `RebuildDescriptor()` to toggle `"I"` prefix. |
| `IsHalfAxis` | `bool` | `false` | Upper half of axis range only. Calls `RebuildDescriptor()` to toggle `"H"` prefix. |
| `IsBidirectional` | `bool` | `false` | With `IsHalfAxis`, fires on absolute deflection past the deadzone, either side of center. Persisted through `PadSetting.MappingBidirectional`, not a descriptor prefix, because the I/H prefixes are already spoken for. |
| `IsInvertApplicable` | `bool` | - | Computed: `IsPrimaryDescriptor && !(IsHalfAxis && IsBidirectional)`. Mirroring around center already covers both directions, and a primary of a key kind (Incremental, Ramp, Invert on Hold) saves its own holder and leaves the row's flag out. |
| `InvertOutput` | `bool` | `false` | Flip Output: invert what the row writes, for the half-axis reads where `Invert` is consumed as the half selector. Round-trips to `MappingSource.InvertOutput`. |
| `IsInvertOutputApplicable` | `bool` | - | Computed by the engine's own `InvertConsumedByHalfAxisRead` predicate against the prefix-stripped primary. Gates the Flip Output checkbox. |
| `ParamAccel` | `double` | `0` | Per-row acceleration exponent, clamped 0.0–5.0. Has `ResetParamAccelCommand`. Gated by `IsParamAccelApplicable`, which excludes the gravity-tilt family: those are position reads whose engine path applies only the curve / range channel (#292). |
| `GyroSensitivity` | `double` | `1.0` | Primary-source gyro multiplier, clamped 0.1–10. Gated by `IsGyroSource`, which excludes the gravity-tilt family. |
| `IsGyroLeanSource` | `bool` | - | Computed: the primary is a gravity-lean read (`"Gyro Lean X"` / `"Gyro Lean Y"`, #292). Gates the lean row's dial, which binds `Sensitivity`. |
| `MouseCursorSensitivity` | `double` | `1.0` | Primary-source cursor sensitivity, clamped 0.1–5. Gated by `IsMouseCursorSource`. |
| `IrPointerSensitivity` | `double` | `1.0` | Primary-source Wii IR-pointer sensitivity, clamped 0.1–5. Gated by `IsIrPointerSource`. |
| `Sensitivity` | `double` | `1.0` | Clamped 0.001–5. The floor is the importers': a rotated stick's row carries the rotation's sine or cosine, which falls under a tenth within about 6 degrees of none or a quarter turn, and the importers drop a leg only under 0.001. Its only mapping-grid surface is the Gyro Lean dial, gated by `IsGyroLeanSource`. The generic per-source slider was removed on 2026-07-27 and the knob moved to the Sticks group as a per-stick multiplier, so `IsGenericSensitivitySource` exists but no XAML binds it. |

### Commands

| Command | Description |
|---------|-------------|
| `ToggleRecordCommand` | Toggles recording. Raises `StartRecordingRequested` or `StopRecordingRequested`. |
| `ClearCommand` | Clears the source and neg descriptor, resets `IsInverted` / `IsHalfAxis` / `IsBidirectional`, puts `MappingDeadZone` back to 50, blanks `PrimarySourceDeviceGuid` and `PrimarySourceDeviceLabel`, wipes the primary kind holder's `ParamUp` / `ParamDown` / `ParamModifier` and forces its `Kind` to `"Direct"` and blanks its `DeviceGuid` and `DeviceLabel`, then re-syncs the selected input from the descriptor. |
| `ResetGyroSensitivityCommand`, `ResetMouseCursorSensitivityCommand`, `ResetIrPointerSensitivityCommand`, `ResetSensitivityCommand`, `ResetParamAccelCommand` | Per-control resets for the primary-source knobs above. |

| Event | Description |
|-------|-------------|
| `StartRecordingRequested` | Start recording. |
| `StopRecordingRequested` | Recording should stop. |

### Multi-Source Extras (#61)

A row's primary source stays on `SourceDescriptor`. Additional sources live in `ExtraSources`, each a `MappingSourceItem`. `CombineMode` applies when the row has more than one source. The engine's `CombineHelper` / `MappingExpression` consumes it in Step 3.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ExtraSources` | `ObservableCollection<MappingSourceItem>` | empty | Sources beyond the primary. |
| `IsPrimaryDirect` / `IsPrimaryDescriptor` | `bool` | - | Computed. `IsPrimaryDirect` is `PrimaryKindSource.Kind == "Direct"`. `IsPrimaryDescriptor` is true for Direct, Toggle and Rapid Trigger (`SourceEvaluator.IsDescriptorKind`), the kinds whose input lives in `SourceDescriptor`. It gates the Source picker, its device label and the kind card in the row, and the Record button's target (#461, #482). |
| `IsGamepadTriggerTarget` / `IsRapidTriggerTarget` / `IsRapidTriggerOffered` | `bool` | - | Computed (#482). `IsGamepadTriggerTarget` is the `LeftTrigger` and `RightTrigger` rows, narrower than `IsTriggerTarget`. `IsRapidTriggerTarget` adds the button-class rows (`IsTargetDiscrete`) apart from the touchpad X/Y rows (`IsTouchpadAxisTarget`), which read every source as a position. `IsRapidTriggerOffered` also needs the primary's input to have press depth (`SourceCoercion.IsRapidTriggerSource`) or to be empty. `PrimaryKindOptions` lists Rapid Trigger only while it holds, and `EnforcePrimaryKindGate`, run from the `SourceDescriptor` setter and `EndLoadRow`, sets a Rapid Trigger primary back to Direct when it stops holding. |
| `IsMultiSource` | `bool` | - | Computed: `ExtraSources.Count > 0 \|\| !IsPrimaryDescriptor`, so a lone Toggle primary shows no Combine picker. Not the same test as `IsTrivialDirect`, which requires `IsPrimaryDirect` and additionally a primary descriptor, no neg descriptor, no extras, no invert / half / bidirectional, and no custom formula. |
| `VariableCount` | `int` | - | Computed: `PositionalSourceCount`, the number of letters a Custom formula may reference. Drives the formula chip palette's visibility. It can run smaller than the primary plus `ExtraSources.Count`: the positional walk skips the bipolar Neg pair and any `InvertOnHold` modifier source. |
| `CombineMode` | `string` | `""` | Per-row combine mode. Empty = per-target-type default (MaxAbs for axes, OR for buttons). Named modes: `MaxAbs`, `Sum`, `Average`, `OR`, `AND`, `XOR`, `StickTrim`, `Custom`. On a Motion target the getter reads `MaxAbs` for any stored mode other than empty, `MaxAbs`, `Sum`, `Average`, or `Custom`. |
| `CombineExpression` | `string` | `""` | Custom formula, only meaningful when `CombineMode == "Custom"`. |
| `IsCustomCombine` | `bool` | - | Computed: `CombineMode == "Custom"`. |
| `ShouldShowCustomExpression` | `bool` | - | Computed: `IsCustomCombine && (IsMultiSource \|\| IsTouchpadAxisTarget)`. A touchpad axis row evaluates a Custom formula at any source count, so its editor shows with one source. |
| `IsBipolarAxisTarget` | `bool` | - | Computed: target is a bipolar stick axis (`LeftThumbAxisX/Y`, `RightThumbAxisX/Y`). Drives per-source direction-badge visibility. |
| `IsTouchpadAxisTarget` | `bool` | - | Computed: target is a touchpad X/Y axis (`TouchpadX1/Y1/X2/Y2`). |
| `PrimarySourceDeviceGuid` | `string` | `""` | DeviceGuid of the primary source on the per-VC MappingSet row. Empty = first available device on this VC. |
| `PrimarySourceDeviceLabel` | `string` | `""` | Friendly device name for the primary source. |
| `NoInherit` | `bool` | `false` | Shift-layer "do not inherit from Base" flag. Round-trips to `MappingRow.NoInherit`. Visible only when authoring a non-Base layer. |
| `ShouldShowEmptyDirectionHint` | `bool` | - | Computed: a bipolar-axis row with exactly one non-inverted button-class primary source, nudging the user to map the opposite direction. |

| Command | Description |
|---------|-------------|
| `AddExtraSourceCommand` | Appends a blank `MappingSourceItem`, seeding `CombineMode` to the per-target default. |
| `RemoveExtraSourceCommand` | `RelayCommand<MappingSourceItem>`. Removes the passed source. |
| `AddOppositeDirectionCommand` | Adds an extra source mirroring the primary descriptor with `Invert=true`, filling a single-button bipolar-axis row's negative direction in one click. |

### Stick Trim (#155)

Trigger-only combine mode that lets a "winding" stick axis trim a trigger output up/down.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `IsStickTrimCombine` | `bool` | - | Computed: `CombineMode == "StickTrim"`. |
| `IsTriggerTarget` | `bool` | - | Computed: target is `LeftTrigger` / `RightTrigger` or an Extended axis created in the Triggers category. The only class the engine's StickTrim combine intercepts. |
| `ShouldShowTrimSettings` | `bool` | - | Computed: `IsMultiSource && IsStickTrimCombine && IsTriggerTarget`. Gates the trim strip. |
| `TrimDeadzone` | `int` | `25` | Trim-axis deflection below this percentage is ignored (steering wobble guard). Clamped 0–95. |
| `TrimRate` | `int` | `100` | Full-deflection adjust speed, percent of the trigger range per second. Clamped 1–1000. |
| `TrimResetOnRelease` | `bool` | `true` | Releasing the gate snaps the stored level back to 100% when true. False keeps it. |

**Reset commands:** `ResetTrimDeadzoneCommand`, `ResetTrimRateCommand`, `ResetTrimResetOnReleaseCommand`.

### Motion Pitch, Yaw and Roll (#475)

File: `MappingItem.MotionRows.cs`. The three rows that turn stick, trigger, button and key input into the virtual controller's motion.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `IsMotionAxisRow` | `bool` | - | Computed: the target is `MotionPitch`, `MotionYaw` or `MotionRoll`. Shows the motion panel. |
| `CanUseMotionAngle` | `bool` | - | Computed: pitch or roll. Yaw has no Angle response, so the Motion Mode dropdown hides on it. |
| `MotionResponse` | `string` | `""` | `""` for Speed, `"Angle"` for Angle. Any other value stores as `""`. |
| `IsMotionAngle` | `bool` | - | Computed: `CanUseMotionAngle` and `MotionResponse == "Angle"`. |
| `ShowMotionSpeedSettings` / `ShowMotionAngleSettings` | `bool` | - | Computed: which half of the panel shows. Raised with `MotionResponse`. |
| `MotionSpeed` | `int` | `360` | Top Speed, degrees per second. Clamped 1 to 1600. |
| `MotionMinSpeed` | `int` | `0` | Start Speed, degrees per second. Clamped 0 to 1600. |
| `MotionAngle` | `int` | `85` | Lean Angle, degrees. Clamped 1 to 90. |
| `MotionDeadzone` | `int` | `20` | Motion Deadzone, percent. Clamped 0 to 90. |
| `MotionResponseOptions` | `IReadOnlyList<CombineModeOption>` | - | Speed and Angle with their descriptions, culture-cached like the combine modes. |
| `PresetCarriesNoMotion` | `bool` (init) | `false` | Set by the grid builder on all five Motion rows of the DualShock 3 (SIXAXIS), plain Switch 2 Pro and plain Steam Deck presets (`HMaestroProfileCatalog.ReportCarriesNoMotion`). |
| `MotionRowNote` / `ShowMotionRowNote` | `string` / `bool` | `null` / `false` | The note under the row. On a Motion Gyro or Motion Accelerometer row, a source whose descriptor is not a `Motion ` one: `Pad_Mapping_MotionRowUnreadNote`. On any other row, a bundled motion source: `Pad_Mapping_MotionSourceElsewhereNote`. Otherwise, on a preset without motion, `Pad_Mapping_MotionPresetNote` on the Motion rows, and on the DualShock 3 (SIXAXIS): Full, whose report carries no pitch or roll rate (`PresetCarriesNoPitchRollRate`), `Pad_Mapping_MotionPitchRollRateNote` on Motion Pitch and Motion Roll in Speed mode. InvertOnHold modifiers are skipped. Raised when the primary, an extra source or `MotionResponse` changes. |

The five settings reset through `ResetSettingCommand` with their property names. The grid builder adds the three rows after Motion Gyro and Motion Accelerometer on the PlayStation, Nintendo and Valve grids (`PadViewModel.AddMotionRows`), each with `NegSettingName` `<Target>Neg` and all five out of Map All. **Clear All** resets the five settings.

### More MappingItem Members

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `RefreshExtraSourceInputs` | method | - | Re-syncs a single extra source's `SelectedInput` to match its stored DeviceGuid+Descriptor pair against this row's cross-device `AvailableInputs` list. Also pushes the parent's discrete-target flag down to the source so the per-source deadzone visibility tracks the row's target. |
| `RefreshAllExtraSourceInputs` | method | - | Bulk-refresh every extra source's selected-input state. Called by InputService after the slot's AvailableInputs list is rebuilt. |
| `PrimaryKindLabel` | `string` | - | Friendly name of the primary's current Kind (e.g. "Ramp"), for any compact display when the primary is non-Direct. |
| `BeginLoadRow` | method (internal) | - | Holds the primary-kind gate while a row loads. `EndLoadRow()` (internal) lets it go, applies it once, and gives a multi-source row the default combine mode. |
| `LoadPrimaryKind` | method | - | Hydrates the reused `PrimaryKindSource` from a stored `MappingSource` on load. Copies into the existing object so its PropertyChanged wiring (recording, dirty, picker refresh) survives. A null or Direct source resets it to a plain Direct holder so the row falls back to its `SourceDescriptor` primary. A Toggle or Rapid Trigger source resets it the same way and keeps the kind, since both read that descriptor too, and the holder keeps the Rapid Trigger distance. A null source (an unmapped row, Clear All) resets the distance with the rest. |
| `IncludeInMapAll` | `bool` | - | Whether this row participates in the "Map All" walk-through. Optional rows (Xbox Series Share, etc.) are visible and individually mappable but skipped during the bulk sequence. |
| `Control` | `string` | - | Which of several like controls the row belongs to, on a slot that has more than one to a category: a custom Extended slot's sticks past the second share the right stick's category, and its POVs the D-pad's. Null where a category is one control, which is every other row. The rows under the picture, and the ring on it, are the picked control's own (#574). |
| `Role` | `string` | - | The control a row is, in a gamepad's names ("LeftThumbButton", "ButtonGuide"), where its target does not say: a lettered preset's raw button rows are laid out by the control each one is. Null for every other row, whose target names it. The bar under the picture reads it for a control's kind, and to put a stick's click with its stick (#574). |
| `PictureName` | `string` | - | The picture's name for the row's control, where that is not the row's own: a MIDI note's pitch ("C4" for Note 60), which is what its key on the picture says. Null for every other row. |
| `BarLabel` | `string` | - | The name the bar under the picture has for the row: the picture's where it has one, else the row's own. |
| `SuppressBipolarPair` | `bool` (internal) | - | Keeps the copied Custom argument positions during edits. |
| `PrimarySourceExists` | `bool` (internal) | - | Retains a loaded primary position when its input is blank. |
| `HasAnySource` | `bool` | - | Whether anything feeds this row: a Direct primary descriptor, a bound stateful primary (Ramp / Incremental / InvertOnHold, whose feeds are the Up/Down/Modifier keys on `PrimaryKindSource`, not a descriptor), or any extra source with a bound feed. The preview annotation layer keys chip presence on this rather than `IsMapped`, so stateful-primary rows stay visible. |
| `CanResetSetting` | method (internal, static) | - | The names `ResetSettingCommand` accepts on this class. |
| `CurrentPercentText` | `string` | `string.Empty` | The row's live value as a share of its full scale, as the bar under the picture reads it (#574): "0 %". A stick's axis reads from -100 to 100, a button or a trigger from 0 to 100. Set by InputService with `CurrentValueText`, from the same value. The two motion rows that list three axes read them as they are, since they are no one number. |
| `IsInputActive` | `bool` | - | True while live input flows on this row (#175 rowfire). Set by InputService from the numeric value with a deadband, so stick rows at rest stay dark. |
| `LiveLevel` | `double` | - | The row's live value as a share of its full scale, 0 to 1: what the value meter beside the row fills to (#574). Set by InputService with the value itself (`InputService.LiveLevelOf`). A row whose value is no one number, as the two motion rows that list three axes, stays at 0. |
| `IsRowSelected` | `bool` | - | Mirror of the row's DataGrid selection state (#175 phase two item 10). Written by the controller page's SelectionChanged handler so the row template can tell the open row, which is the selected one, with a plain DataContext binding (#574). UI-only state, never persisted. |
| `ApplyScrollUpAuthoringDefault` | method | - | E7 authoring default (2026-07-14 audit, closed 2026-07-18), the ONE seam shared by the dropdown pick and the recorder: the wire contract makes an un-inverted press on the vertical scroll target read DOWN (Step 3's documented negation, which the Workshop translator compensates for with SCROLL_UP => Invert). A user attaching a plain press expects scroll UP, so direction-free press-class sources (buttons, POV directions, touchpad clicks / finger downs) get Invert stamped as the authoring default. Hydration and existing rows are untouched (no migration), the user can uncheck for scroll down, and KbmScrollNeg (the explicit down leg) plus horizontal scroll are never stamped. |
| `PromoteNegDescriptorToExtraSource` | method | - | Issue #61: promotes the legacy `NegSourceDescriptor` into a visible `ExtraSources` entry with Invert flipped. Called by the recording pipeline so the user sees both directions immediately after a two-phase recording, instead of having to toggle the Device dropdown to trigger a load- time migration. The new ExtraSource inherits its device origin from `PrimarySourceDeviceGuid`, which `RecorderService.CompleteRecording` reliably stamps with the device that physically fired. Does nothing when the Neg is empty or when an equivalent extra already exists on the row. |
| `IsMouseMotionSource` | `bool` | - | True for a "Mouse Motion X/Y" primary source (#154). Mirrors `IsMouseMotionSource` so the per-source sensitivity slider's visibility binding resolves on the legacy-row template too (a missing property leaves the failed binding at Visibility's default, which is Visible on EVERY row). |
| `IsHalfAxisApplicable` | `bool` | - | True when the Half checkbox (and the dependent Either) is meaningful for this row's source. Half-axis only applies to continuous-range sources: Axis, Slider, Touchpad X/Y/Pressure, and Gyro Pitch/Yaw/Roll. Discrete sources (Button, POV direction, Touchpad Click / Finger Down) have no upper or lower half to pick. |
| `Cleared` | `EventHandler` | - | Raised when Clear empties this row, a row that held nothing included, which changes no property. |
| `CombineModeDisplayName` | `string` | - | The current combine mode's layman label ("Strongest" / "Combined"…) for the collapsed row's chip (#292 discoverability: the chip used to show the raw engine token, "MAXABS" to a user who never opened the detail strip). Falls back to the raw value for a mode the option list doesn't carry. |
| `AvailableCombineModes` | `IReadOnlyList<CombineModeOption>` | - | Motion rows use axis combine modes. StickTrim is available on trigger rows. |
| `CombineExpressionStatus` | `string` | - | Live parse status of `CombineExpression`. "✓ valid" or a parse-error message. Surfaced inline below the Custom expression TextBox so users get immediate feedback. Empty/whitespace expression compiles as 0 (always valid). |
| `IsCombineExpressionValid` | `bool` | - | Computed from `CombineExpressionStatus`: the expression parses, or it does not. |
| `IsCombineExpressionInvalid` | `bool` | - | See `IsCombineExpressionValid`. |
| `VariableALabel` | `string` | - | The labels of the formula chips A to D, each the friendly alias of the row's source at that position. |
| `VariableBLabel` | `string` | - | See `VariableALabel`. |
| `VariableCLabel` | `string` | - | See `VariableALabel`. |
| `VariableDLabel` | `string` | - | See `VariableALabel`. |
| `VariableATooltip` | `string` | - | Composite tooltip strings for the formula chips. Show the chip's positional meaning plus the friendly alias for the row's current source at that position. |
| `VariableBTooltip` | `string` | - | See `VariableATooltip`. |
| `VariableCTooltip` | `string` | - | See `VariableATooltip`. |
| `VariableDTooltip` | `string` | - | See `VariableATooltip`. |
| `IsCombineExpressionWarning` | `bool` | - | True when the expression is valid but references variables beyond the row's actual source count: those silently evaluate to 0 in the engine, which is rarely what the user intended. |
| `IsVrAxisTarget` | method (internal, static) | - | True for the VR axis-class targets (stick axes, trigger and grip pulls). The "...Click" button names end past these suffixes, so they classify as discrete. |

### The Row in the List (#574)

**File:** `MappingItem.List.cs`

The row as the mapping list draws it: its first source's line (the row implements `IMappingSourceLine`, as each added source does), its cells under the list's device columns, and its live bar.

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `Owner` | `PadViewModel` (internal) | - | The controller the row belongs to, which knows the devices and holds the list's columns. Null for a row that is in no list. |
| `Row` | `MappingItem` | - | The row this source line belongs to. |
| `ModeHolder` | `MappingSourceItem` | - | The source that holds the line's mode: the row's `PrimaryKindSource` for the first source, the source itself for an added one. |
| `IsLineKeyMode` | `bool` | - | The source reads keys of its mode's own (Incremental, Ramp, Invert On Hold), so it has no input to pick. |
| `ShowsLineDeadZone` | `bool` | - | The `Line…` members are the first source's line under the row, the same facts an added source's line shows: its device (`LineDeviceGuid`, `LineDeviceLabel`, `LineDevice`, `IsLineAway`, `IsLineUnassigned`), its letter in a Custom formula (`LineLetter`), its switches (`LineInvert`, `LineHalf`, `LineBidirectional`), its deadzone (`LineDeadZone`, shown while `ShowsLineDeadZone`), and its Record, Clear and Remove (`LineRecordCommand`, `LineClearCommand`, `LineRemoveCommand`, `LineRecordIcon`, `LineRecordText`, `CanLineRecord`). |
| `LineDeviceGuid` | `string` | - | See `ShowsLineDeadZone`. |
| `LineDeviceLabel` | `string` | - | See `ShowsLineDeadZone`. |
| `LineDevice` | `PadViewModel.MappedDeviceInfo` | - | See `ShowsLineDeadZone`. |
| `IsLineAway` | `bool` | - | See `ShowsLineDeadZone`. |
| `IsLineUnassigned` | `bool` | - | See `ShowsLineDeadZone`. |
| `LineLetter` | `string` | `string.Empty` | See `ShowsLineDeadZone`. |
| `LineDirection` | `string` | - | Which way the first source pushes a stick's axis: a button, a hat's direction or a touchpad's press on a row with two directions. The same mark an added source carries. |
| `IsTrimStick` | `bool` | - | This source is the trim stick: the last source of a row that trims. |
| `LineInvert` | `bool` | - | See `ShowsLineDeadZone`. |
| `LineHalf` | `bool` | - | See `ShowsLineDeadZone`. |
| `LineBidirectional` | `bool` | - | See `ShowsLineDeadZone`. |
| `LineDeadZone` | `int` | - | See `ShowsLineDeadZone`. |
| `LineRecordCommand` | `RelayCommand` | - | Record beside the first source's input is the row's own Record, which takes a mode's keys in turn. |
| `LineClearCommand` | `RelayCommand` | - | See `ShowsLineDeadZone`. |
| `LineRemoveCommand` | `RelayCommand` | - | See `ShowsLineDeadZone`. |
| `LineRecordIcon` | `string` | - | See `ShowsLineDeadZone`. |
| `LineRecordText` | `string` | - | See `ShowsLineDeadZone`. |
| `CanLineRecord` | `bool` | - | See `ShowsLineDeadZone`. |
| `RaiseLineFacts` | method (internal) | - | What the first source's line shows, read again: its device may be another, or have connected or gone. |
| `RefreshLineMarks` | method (internal) | - | The marks that depend on a source's place among the row's sources: the trim stick, which is the last source of a row that trims, and each source's letter in a Custom formula. |
| `WithFlagPrefix` | method (internal, static) | - | The input with its Invert and Half flags written before it ("IH"), the form the row keeps its first source's input in. |
| `LoadFirstSource` | method (internal) | - | Takes a stored source as the row's first, or empties the first source for none. A source whose mode reads its own input (Direct, Toggle, Rapid Trigger) lands in the row's own fields. One whose mode reads keys lands on `PrimaryKindSource` and leaves the row's own fields empty. A load and the removal of the first source both come through here, so the source that moves up reads exactly as it would after a save and a load. |
| `RemoveFirstSourceCommand` | `RelayCommand` | - | Remove on the first source's line. The next source becomes the first, and with no next source the row is cleared. |
| `Cells` | `IReadOnlyList<RowCell>` | - | The row's cells, one under each column of the list, in the columns' order. |
| `LiveTags` | `IReadOnlyList<RowTag>` (internal) | - | The tags whose level the live refresh reads. |
| `ShowsCombine` | `bool` | - | The closed row's end names how its sources combine: where the open row offers the Combine choice, and one is set. |
| `BuildTags` | method (internal) | - | A tag for each input that drives the row, in the order of its sources: the first source's, then each added source's. A source read through its own input is one tag. A source whose mode reads keys is a tag for each key that is set. |
| `SetCells` | method (internal) | - | Lays the row's tags under the list's columns. Each tag goes under the column of the device it is read on. Under a column, the last tag of a source names the source's mode when it is not Direct. The fold's cell counts the tags on the devices that are not connected. |
| `IsRecordTarget` | `bool` (internal) | - | The controller is recording for this row: its first source, one of its added sources, or a new one. Set by the controller's view model from the target it records. |
| `IsRowRecording` | `bool` | - | Something records for the row. Its line flashes while it does, whichever of its sources the input will land on. |
| `IsCenteredValue` | `bool` | - | The row's value rests in the middle of its range and moves either way: a stick's axis, a motion axis, or a custom Extended slot's stick axis. |
| `LiveSign` | `int` (internal) | - | Which way the row's live value stands from rest: -1, 0 or 1. Set by the live refresh with `LiveLevel`. |
| `LiveBarLevel` | `double` | - | Where the row's live value stands on its bar, 0 to 1. A centered value rests in the middle of the bar and moves either way from it. Any other fills from the start, as `LiveLevel` does. Clamped to 0 to 1. |

### Source Shaping and Gates (#574)

**File:** `MappingItem.Shaping.cs`

The line under a source (#574) carries its shaping and its gates, each with a reset: Only While (`Mapping_Gate`, `GateDescriptor`), And While (`Mapping_Gate2`, `Gate2Descriptor`), Curve (`Mapping_SourceCurve`, `ParamCurveExponent`), Outer Range (`Mapping_SourceOuterRange`, `ParamRangeOuter`), Anti-Deadzone (`Mapping_SourceAntiDeadzone`, `ParamAntiDeadzone`), Deadzone Shape (`Mapping_SourceDeadZoneShape`, `ParamStickDeadZoneShape`) and Inner Deadzone (`Mapping_SourceInnerDeadzone`, `ParamStickDeadZoneInner`). The row's first source keeps them on `MappingItem` (`MappingItem.Shaping.cs`), and each added source on its `MappingSourceItem` (`MappingSourceItem.Shaping.cs`), with the same members. `SourceDeadZoneShapeChoice` is one entry of the Deadzone Shape picker.

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ParamCurveExponent` | `double` | - | The reading raised to this power. 0 and 1 leave it straight. Clamped to 0.0 to 5.0. |
| `ParamRangeOuter` | `double` | - | Full output at this fraction of the travel. 0 is off. Clamped to 0.0 to 1.0. |
| `ParamRangeOuterPercent` | `double` | - | `ParamRangeOuter` in percent, 100 for off. Clamped to 1.0 to 100.0. |
| `ParamAntiDeadzone` | `double` | - | The output starts at this fraction. 0 is off. Clamped to 0.0 to 0.99. |
| `ParamAntiDeadzonePercent` | `double` | - | `ParamAntiDeadzone` in percent. Clamped to 0.0 to 99.0. |
| `ParamStickDeadZoneShape` | `int` | - | 0 off, 1 axial (this axis alone), 2 radial (the stick pair together). |
| `ParamStickDeadZoneShapeChoices` | `IReadOnlyList<SourceDeadZoneShapeChoice>` | - | The Deadzone Shape picker's choices. |
| `ParamStickDeadZoneInner` | `double` | - | The inner deadzone of the shape, as a fraction. Clamped to 0.0 to 0.99. |
| `ParamStickDeadZoneInnerPercent` | `double` | - | `ParamStickDeadZoneInner` in percent. Clamped to 0.0 to 99.0. |
| `HasShaping` | `bool` | - | True when any of the five holds a value the engine applies. |
| `IsShapingShown` | `bool` | - | The five shaping dials show where the source holds a value, and on a continuous source of a row whose output has no device card (a mouse axis, a raw axis), where they are the only shaping there is. A stick or trigger output's shaping lives on the device's own card, which takes an import's at assignment. |
| `GateDescriptor` | `string` | `string.Empty` | The input this source waits on: it counts only while this also reads as pressed on the same controller. Empty for none. |
| `Gate2Descriptor` | `string` | `string.Empty` | A second input the source waits on, beside `GateDescriptor`. Empty for none. |
| `HasGate` | `bool` | - | Computed: `GateDescriptor` is not empty (`HasGate2`: `Gate2Descriptor`). |
| `HasGate2` | `bool` | - | See `HasGate`. |
| `GateText` | `string` | - | The gate in words. An import's zone test (a stick's sector or ring, a trigger's pull band) reads as the range it checks. |
| `Gate2Text` | `string` | - | The second gate in words, as `GateText`. |
| `GatePick` | `InputChoice` | - | The gate's picker: a pick replaces the gate, and the picker itself holds nothing. |
| `Gate2Pick` | `InputChoice` | - | The second gate's picker, as `GatePick`. |
| `ShapingHolder` | `object` | - | The object whose shaping and gates the line under the source shows. |
| `ResetParamCurveExponentCommand` | `RelayCommand` | - | Resets `ParamCurveExponent` to `0.0`. |
| `ResetParamRangeOuterCommand` | `RelayCommand` | - | Resets `ParamRangeOuter` to `0.0`. |
| `ResetParamAntiDeadzoneCommand` | `RelayCommand` | - | Resets `ParamAntiDeadzone` to `0.0`. |
| `ResetParamStickDeadZoneShapeCommand` | `RelayCommand` | - | Resets `ParamStickDeadZoneShape` to `0`. |
| `ResetParamStickDeadZoneInnerCommand` | `RelayCommand` | - | Resets `ParamStickDeadZoneInner` to `0.0`. |
| `ResetGateDescriptorCommand` | `RelayCommand` | - | Resets `GateDescriptor` to `string.Empty`. |
| `ResetGate2DescriptorCommand` | `RelayCommand` | - | Resets `Gate2Descriptor` to `string.Empty`. |
| `LoadShapingAndGates` | method (internal) | - | Takes the five shaping values and the two gates of `src`, or clears them for none. |
| `StoreShapingAndGates` | method (internal) | - | Writes them onto `dst`. |

### InputChoice

**File:** `MappingItem.cs`

Input choice in the source dropdown.

| Property | Type | Description |
|----------|------|-------------|
| `Descriptor` | `string` | Mapping descriptor (e.g., `"Button 0"`, `"Axis 1"`, `"POV 0 Up"`). Empty string = "clear" sentinel. |
| `DisplayName` | `string` | Human-readable display name (e.g., `"A"`, `"Left Stick X"`). `ToString()` returns it. |
| `DeviceGuid` | `string` | Owning device for the cross-device picker. Empty = the "(Any device)" group. |
| `DeviceLabel` | `string` | Friendly device name for that group heading. |

### MappingCategory (enum)

Values: `Buttons`, `DPad`, `Triggers`, `LeftStick`, `RightStick`, `Touchpad`, `Motion`. `Motion` covers the bundled motion-passthrough rows (`MotionGyro` / `MotionAccel` targets) and the Motion Pitch, Yaw and Roll rows (#475). The passthrough rows are auto-created on Sony-class slots for every assigned gyro or accel-capable device and rendered as one combined Motion row when both sub-channels come from the same source. `Touchpad` rows are the one category `IsRecordable` excludes.

---

## MappingSourceItem

**File:** `MappingSourceItem.cs`

One source row within a multi-source `MappingItem` (#61). Represents a single `Engine.Data.MappingSource`, bound by the RowDetailsTemplate inside the Mappings DataGrid.

### Kind

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Kind` | `string` | `"Direct"` | Source kind: `Direct`, `Toggle`, `RapidTrigger`, `Incremental`, `InvertOnHold`, `Ramped`. Notifies the `Is*Kind` computed flags. A change to Incremental or Ramp outside a load drops `Invert`, unless it comes from the other of those two kinds, and puts the source on the controller its Up and Down keys share (`FollowKeysDevice`). A change to InvertOnHold outside a load puts it on the controller its modifier names, and a change to a kind that reads the Descriptor puts it back on the Descriptor's (`RestoreDescriptorController`). |
| `IsIncrementalKind` / `IsInvertOnHoldKind` / `IsRampedKind` / `IsToggleKind` / `IsRapidTriggerKind` | `bool` | - | Computed per-kind flags. |
| `DescriptorKind` | `string` (internal) | - | Computed: the kind a row's primary saves as, `Toggle` or `RapidTrigger` when set, else `Direct`. Every path that rebuilds a primary into a source reads it. |
| `UsesUpDownKeys` | `bool` | - | Computed: Incremental or Ramped (authored via an Up/Down key pair). |
| `IsKindDescriptorless` | `bool` | - | Computed: the kinds that leave the source's `Descriptor`, `HalfAxis` and `DeadZone` unread (Incremental, InvertOnHold, Ramped). The grid collapses those controls and `Invert` with them. `Invert` is not unread: the engine applies it to an Incremental source and to a Ramp source on an axis, so a source that comes to one of those two kinds from any other kind in the editor drops it, while a switch between Incremental and Ramp keeps it, and one saved with it on shows it (`IsKeyInvertShown`). |
| `IsKeyInvertShown` | `bool` | - | Computed: `UsesUpDownKeys && Invert`. An Incremental or Ramp source saved with `Invert` on shows a checkbox for it, the control that turns it off. Unchecked, the checkbox goes with it. A row's primary shows the same checkbox in its own strip, bound to the primary kind holder's `Invert`. |
| `HasAnyBoundFeed` | `bool` | - | Computed: whether any input feeds this source, per kind. Mirrors the engine's SourceEvaluator dispatch. |

`KindOptions` (static) is the culture-cached list of `KindChoice { Value, Name }` for the Kind dropdown, keeping backend identifiers out of the UI. `KindChoices`, the extra-source chip's instance list, drops Rapid Trigger while `IsRapidTriggerOffered` is false: the source's input has no press depth, or its row cannot take the mode (`ParentTargetTakesRapidTrigger`, #482). Picking an input without depth sets a Rapid Trigger source back to Direct, and `EnforceRapidTriggerGate` does the same when the parent row pushes a target that cannot take it.

### Source

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `DeviceGuid` | `string` | `""` | Device this source reads from. Empty = the picker's "(Any device)" group. |
| `DeviceLabel` | `string` | `""` | Friendly device name, shown inline below the per-source picker. |
| `DisplayDeviceLabel` | `string` | - | Computed device label honoring the "(Any device)" contract: a concrete-guid source prefers `SelectedInput.DeviceLabel` (recovers the friendly name when the stored label wasn't hydrated), an empty-guid source keeps its own label and never borrows a concrete device from a descriptor-only picker fallback. Read by the grid subtitle, the annotation overlays, and the pipeline-chip tooltip. |
| `Descriptor` | `string` | `""` | Input descriptor. Notifies the source-class flags below. |
| `DescriptorDeviceGuid` | `string` | - | Computed: what `ToDomain` saves as the controller the kept Descriptor was picked on, the domain field of the same name. The remembered controller while the kind leaves the Descriptor unread and the source sits on another device, `null` otherwise. `FromDomain` takes a saved one back. |
| `SelectedInput` | `InputChoice` | `null` | Cross-device picker selection. Setting it writes `DeviceGuid`, `DeviceLabel`, and `Descriptor` in one shot. |
| `IsGyroSource` / `IsMouseCursorSource` / `IsIrPointerSource` / `IsMouseMotionSource` | `bool` | - | Computed from the descriptor prefix. Gate the matching per-source sensitivity sliders. `IsGyroSource` excludes the gravity-tilt family (#292). |
| `IsGyroLeanSource` | `bool` | - | Computed: the gravity-lean pair (`"Gyro Lean X"` / `"Gyro Lean Y"`, #292). Gates the lean row's dial, which binds `Sensitivity`, the field `ReadGyroLean` scales by. |
| `IsParamAccelApplicable` | `bool` | - | Computed: gates the per-source Acceleration slider. The continuous-source family minus the gravity-tilt pairs, whose engine path never applies `ParamAccel` (#292). |
| `IsButtonClassDescriptor` | `bool` | - | Computed: the descriptor yields a bool. Gamepad aliases resolve first, then button, POV, touchpad-click, NFC tag (#241), and voice phrase (#317). |
| `DirectionBadge` | `string` | - | Computed: `"→ +"` / `"← −"` for button-class sources, per `Invert`. Empty otherwise. |

### Options and per-source deadzone

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Invert` | `bool` | `false` | Axis / direction inverted. |
| `HalfAxis` | `bool` | `false` | Upper half of the range only. |
| `IsHalfAxisApplicable` | `bool` | - | Computed: Half applies to continuous-range sources (Axis, Slider, Touchpad X/Y/Pressure, Gyro, Mouse Motion). |
| `Bidirectional` | `bool` | `false` | With `HalfAxis`, fires on absolute deflection past the deadzone (either side of center). |
| `DeadZone` | `int` | `50` | Per-source axis-to-button threshold. Clamped 1–100 (0 is disallowed because it read as "unset"). |
| `IsDeadZoneApplicable` | `bool` | - | Computed: the source is an axis/slider (or an engine-owned continuous family) AND the parent target is a discrete output, or a gamepad trigger row with this source in Rapid Trigger (#482). |
| `ParentTargetIsDiscrete` / `ParentTargetIsTrigger` | `bool` | `false` | Set by the parent `MappingItem` so `IsDeadZoneApplicable` knows the target class. `ParentTargetIsTrigger` is `MappingItem.IsGamepadTriggerTarget`. |
| `ParentTargetTakesRapidTrigger` | `bool` | `false` | Set by the parent `MappingItem` from `IsRapidTriggerTarget`, so an extra source offers Rapid Trigger on exactly the rows whose primary does (#482). |

### Kind parameters

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ParamUp` / `ParamDown` | `string` | `""` | Up / Down key descriptors for Incremental and Ramped. |
| `ParamRapidTriggerDistance` | `int` | `10` | Rapid Trigger distance in percent of full travel, clamped 1 to 50 (#482). The Distance row in the detail strip and on the extra-source chip, each with a reset button. `LoadPrimaryKind(null)` and the row's Clear reset it. |
| `ParamRate` | `double` | `0.5` | Incremental step rate. |
| `ParamSticky` | `bool` | `true` | Incremental sticky hold. |
| `ParamMin` / `ParamMax` | `double` | `0` / `1` | Incremental output bounds. |
| `ParamModifier` | `string` | `""` | InvertOnHold modifier key descriptor. |
| `ParamUpDeviceGuid` / `ParamDownDeviceGuid` / `ParamModifierDeviceGuid` | `string` | `null` | The controller each key reads, the domain fields of the same names. A pick or a recording sets it with the key (`SetParamKey`), and `ToDomain` saves none for an empty key. `ParamUpReadDevice` and its siblings answer the controller the engine reads, the source's own for a key with none. |
| `ParamAttackTime` | `double` | `0.30` | Ramped attack seconds (#111). Clamped 0–5. |
| `ParamReleaseTime` | `double` | `0.30` | Ramped release seconds (#111). Clamped 0–5. |
| `ParamAutocenter` | `bool` | `true` | Ramped: release ramps back to zero (#111). |
| `ParamReverseMultiplier` | `double` | `4.0` | Ramped reverse speed-up (#111). Clamped 1–10. |
| `GyroSensitivity` | `double` | `1.0` | Per-source gyro multiplier (Gyro descriptors). Clamped 0.1–10. |
| `MouseCursorSensitivity` | `double` | `1.0` | Per-source cursor sensitivity (#107, Mouse Position). Clamped 0.1–5. |
| `IrPointerSensitivity` | `double` | `1.0` | Per-source Wii IR-pointer sensitivity (#146). Clamped 0.1–5. |
| `Sensitivity` | `double` | `1.0` | Per-source multiplier the Gyro Lean dial binds (`ReadGyroLean` scales by it). Clamped 0.001–5, the same importer floor as `MappingItem.Sensitivity`. |
| `ParamAccel` | `double` | `0` | Per-source acceleration exponent, clamped 0.0–5.0. Gated by `IsParamAccelApplicable`. |
| `InvertOutput` | `bool` | `false` | Flip Output: invert what this source writes. Gated by `IsInvertOutputApplicable`, the engine's `InvertConsumedByHalfAxisRead` predicate. |

### Per-source recording

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `IsRecording` | `bool` | `false` | Recording mode active. Notifies the record text and icon. |
| `RecordButtonText` / `RecordButtonIcon` | `string` | - | Computed record-button label / Segoe MDL2 glyph. |

| Command | Description |
|---------|-------------|
| `ToggleRecordCommand` | Toggles primary-source recording (raises `StartRecordingRequested` / `StopRecordingRequested`). |
| `RecordParamUpCommand` / `RecordParamDownCommand` / `RecordParamModifierCommand` | Toggle recording for a specific Param field (raise `StartParamRecordingRequested` with a `ParamRecordTarget`). |
| `ClearCommand` | Clears the descriptor, `DeviceGuid`, `DeviceLabel`, and the backing selected-input field, and resets the flags and deadzone to their defaults, keeping the row in `ExtraSources`. It leaves `Kind`, the `Param*` fields, the sensitivities, `ParamAccel`, and `InvertOutput` alone. |
| `ResetDeadZoneCommand`, `ResetGyroSensitivityCommand`, `ResetMouseCursorSensitivityCommand`, `ResetIrPointerSensitivityCommand`, `ResetParamAccelCommand`, `ResetSensitivityCommand` | Per-control resets. |

| Method | Description |
|--------|-------------|
| `ToDomain()` | Builds a domain `Engine.Data.MappingSource` from the VM. |
| `FromDomain(MappingSource)` | Static: populates a new VM from a domain source. |
| `SyncSelectedInputFromState(IEnumerable<InputChoice>)` | Syncs the picker selection from the current `(DeviceGuid, Descriptor)` pair. |
| `SetParamKey(ParamRecordTarget, string, string)` | Internal: lands a key and its controller together, a cleared key keeping none, then lets the source follow the keys its kind reads (`FollowKeysDevice`: for Incremental or Ramp the controller its Up and Down keys share, or none, for InvertOnHold the controller its modifier names). A key saved without a controller, the modifier included, is first given the source's. The source remembers the controller and name its Descriptor was picked on when it first follows its keys away, and a switch back to a kind that reads the Descriptor restores them (`RestoreDescriptorController`). `FollowKeysDevice` has two more callers: `AdoptLegacyKeyDevices`, and the `Kind` setter when the kind becomes Incremental or Ramp with keys already in. |
| `AdoptLegacyKeyDevices()` | Internal: gives each key saved before keys carried a controller the controller of the entry its picker shows, and only from a list that carries the source's own controller (`ListCarriesOwnController`). The parent row calls it from `RefreshExtraSourceInputs`, outside a row load (`BeginLoadRow` to `EndLoadRow`), so the list rebuilt after the rows decides. `MappingItem.LoadPrimaryKind` holds it off (`LoadingKeys`) until the whole source is in, because the source's device lands before its keys. `LoadingKeys` holds the `Kind` setter's follow off too: `LoadPrimaryKind` sets the kind last, and the source stays on the device it was saved on. |

`ParamRecordTarget` (enum): `Up`, `Down`, `Modifier`.

### More MappingSourceItem Members

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `NameDescriptorController` | method (internal) | - | Names the remembered controller where a load left it unnamed. The loader passes the resolver it names the source's own device with, so a controller the row's list does not carry comes back under its device's name all the same (`RestoreDescriptorController`). |
| `KindOptionsWithoutRapidTrigger` | method (internal, static) | - | `all` without Rapid Trigger, cached against the culture's list it was built from. |
| `RefreshCulture` | method (internal) | - | Called by the owning MappingItem's culture handler. |
| `ParentMappingItem` | `MappingItem` (internal) | - | The row the source is one of. What the source's line reads through the row follows a change of it. |
| `ParamUpInputChoice` | `InputChoice` | - | `InputChoice` projections for the Up, Down and Modifier key pickers, over the stored descriptor and device. `RefreshParamPickerChoices()` re-raises them after the slot's lists change. |
| `ParamDownInputChoice` | `InputChoice` | - | See `ParamUpInputChoice`. |
| `ParamModifierInputChoice` | `InputChoice` | - | See `ParamUpInputChoice`. |
| `RefreshParamPickerChoices` | method | - | See `ParamUpInputChoice`. |
| `ParamUpDeviceLabel` | `string` | - | Device label of the device whose button is currently stored in the corresponding Param field. Resolved against the parent MappingItem's AvailableInputs via the InputChoice picker bridge. Returns empty when no matching InputChoice is found (typical for empty Param fields). |
| `ParamDownDeviceLabel` | `string` | - | See `ParamUpDeviceLabel`. |
| `ParamModifierDeviceLabel` | `string` | - | See `ParamUpDeviceLabel`. |
| `ParamDownReadDevice` | `string` | - | See `ParamUpReadDevice`. |
| `ParamModifierReadDevice` | `string` | - | See `ParamUpReadDevice`. |
| `ResetSettingCommand` | `RelayCommand<string>` | - | Resets setting to its default. |
| `CanResetSetting` | method (internal, static) | - | The names `ResetSettingCommand` accepts on this class. |
| `IsGenericSensitivitySource` | `bool` | - | True when this source carries the generic per-source Sensitivity knob (issue #9): a plain "Axis N" / "Slider N" read, or an abstract Gamepad stick / trigger that canonicalizes to one. Drives that slider's visibility, mutually exclusive with the gyro / mouse / IR predicates above. |
| `IsInvertApplicable` | `bool` | - | Whether the Invert checkbox actually does anything in the current combination: with Half + Either both on, the engine reads absolute deflection and Invert is documented inert. Mirrors MappingItem.IsInvertApplicable on the grid-row twin. |
| `ParamRecordEventArgs` | type | - | The `StartParamRecordingRequested` event's argument: its `Target` (`ParamRecordTarget`) names which key records. |

### The Source's Line (#574)

**File:** `MappingSourceItem.Line.cs`

An added source's line under its row, the same `IMappingSourceLine` members the row carries for its first source.

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `DirectionPositive` | `string` (const) | - | The mark of a button that pushes a stick's axis its positive way, and the opposite way. |
| `DirectionNegative` | `string` (const) | - | The two `LineDirection` marks (`DirectionPositive`, `DirectionNegative`). |
| `IsButtonClass` | method (internal, static) | - | Whether an input is pressed or not, as against moved: a button, a hat's direction, a touchpad's press, an NFC tag or a voice phrase. Such an input pushes a stick's axis one way, so it carries a direction there. The input is given with no flag before it. |
| `Row` | `MappingItem` | - | The row this source line belongs to. |
| `ModeHolder` | `MappingSourceItem` | - | The source that holds the line's mode: the row's `PrimaryKindSource` for the first source, the source itself for an added one. |
| `ModeChoices` | `IReadOnlyList<KindChoice>` | - | The modes the source's picker offers. The first source leaves out Invert On Hold while no other source is there for it to turn around (`PrimaryKindOptions`). Both leave out Rapid Trigger where it cannot act. |
| `RaiseModeChoices` | method (internal) | - | Re-raises `ModeChoices`. |
| `KindLabel` | `string` | - | The mode's name as its picker shows it. |
| `IsLineKeyMode` | `bool` | - | The source reads keys of its mode's own (Incremental, Ramp, Invert On Hold), so it has no input to pick. |
| `ShowsLineDeadZone` | `bool` | - | The `Line…` members are the first source's line under the row, the same facts an added source's line shows: its device (`LineDeviceGuid`, `LineDeviceLabel`, `LineDevice`, `IsLineAway`, `IsLineUnassigned`), its letter in a Custom formula (`LineLetter`), its switches (`LineInvert`, `LineHalf`, `LineBidirectional`), its deadzone (`LineDeadZone`, shown while `ShowsLineDeadZone`), and its Record, Clear and Remove (`LineRecordCommand`, `LineClearCommand`, `LineRemoveCommand`, `LineRecordIcon`, `LineRecordText`, `CanLineRecord`). |
| `LineDeviceGuid` | `string` | - | See `ShowsLineDeadZone`. |
| `LineDeviceLabel` | `string` | - | See `ShowsLineDeadZone`. |
| `LineDevice` | `PadViewModel.MappedDeviceInfo` | - | See `ShowsLineDeadZone`. |
| `IsLineAway` | `bool` | - | See `ShowsLineDeadZone`. |
| `IsLineUnassigned` | `bool` | - | See `ShowsLineDeadZone`. |
| `LineLetter` | `string` | `string.Empty` | See `ShowsLineDeadZone`. |
| `LineDirection` | `string` | - | Which way the source pushes a stick's axis, on a row with two directions. |
| `IsTrimStick` | `bool` | - | This source is the trim stick: the last source of a row that trims. |
| `LineInvert` | `bool` | - | See `ShowsLineDeadZone`. |
| `LineHalf` | `bool` | - | See `ShowsLineDeadZone`. |
| `LineBidirectional` | `bool` | - | See `ShowsLineDeadZone`. |
| `LineDeadZone` | `int` | - | See `ShowsLineDeadZone`. |
| `StartKeysRecordingRequested` | `EventHandler` | - | Raised when Record should take the keys of the source's mode: Up and then Down, or the modifier. |
| `LineRecordCommand` | `RelayCommand` | - | Record on the source's line. A mode that reads its own input records that input. A mode that reads keys records them in turn, as the first source's Record does. A second click stops either. |
| `LineClearCommand` | `RelayCommand` | - | See `ShowsLineDeadZone`. |
| `LineRemoveCommand` | `RelayCommand` | - | See `ShowsLineDeadZone`. |
| `LineRecordIcon` | `string` | - | See `ShowsLineDeadZone`. |
| `LineRecordText` | `string` | - | See `ShowsLineDeadZone`. |
| `CanLineRecord` | `bool` | - | See `ShowsLineDeadZone`. |
| `RaiseLineFacts` | method (internal) | - | What the source's line shows, read again: its device may be another, or have connected or gone. |

### Source Shaping and Gates

**File:** `MappingSourceItem.Shaping.cs`

The same members as [the row's](#source-shaping-and-gates-574), for an added source.

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ParamCurveExponent` | `double` | - | The reading raised to this power. 0 and 1 leave it straight. Clamped to 0.0 to 5.0. |
| `ParamRangeOuter` | `double` | - | Full output at this fraction of the travel. 0 is off. Clamped to 0.0 to 1.0. |
| `ParamRangeOuterPercent` | `double` | - | `ParamRangeOuter` in percent, 100 for off. Clamped to 1.0 to 100.0. |
| `ParamAntiDeadzone` | `double` | - | The output starts at this fraction. 0 is off. Clamped to 0.0 to 0.99. |
| `ParamAntiDeadzonePercent` | `double` | - | `ParamAntiDeadzone` in percent. Clamped to 0.0 to 99.0. |
| `ParamStickDeadZoneShape` | `int` | - | 0 off, 1 axial (this axis alone), 2 radial (the stick pair together). |
| `ParamStickDeadZoneShapeChoices` | `IReadOnlyList<SourceDeadZoneShapeChoice>` | - | The Deadzone Shape picker's choices. |
| `ParamStickDeadZoneInner` | `double` | - | The inner deadzone of the shape, as a fraction. Clamped to 0.0 to 0.99. |
| `ParamStickDeadZoneInnerPercent` | `double` | - | `ParamStickDeadZoneInner` in percent. Clamped to 0.0 to 99.0. |
| `HasShaping` | `bool` | - | True when any of the five holds a value the engine applies. |
| `IsShapingShown` | `bool` | - | The five shaping dials show where the source holds a value, and on a continuous source of a row whose output has no device card (a mouse axis, a raw axis), where they are the only shaping there is. A stick or trigger output's shaping lives on the device's own card, which takes an import's at assignment. |
| `GateDescriptor` | `string` | `string.Empty` | The input this source waits on: it counts only while this also reads as pressed on the same controller. Empty for none. |
| `Gate2Descriptor` | `string` | `string.Empty` | A second input the source waits on, beside `GateDescriptor`. Empty for none. |
| `HasGate` | `bool` | - | Computed: `GateDescriptor` is not empty (`HasGate2`: `Gate2Descriptor`). |
| `HasGate2` | `bool` | - | See `HasGate`. |
| `GateText` | `string` | - | The gate in words. An import's zone test (a stick's sector or ring, a trigger's pull band) reads as the range it checks. |
| `Gate2Text` | `string` | - | The second gate in words, as `GateText`. |
| `GatePick` | `InputChoice` | - | The gate's picker: a pick replaces the gate, and the picker itself holds nothing. |
| `Gate2Pick` | `InputChoice` | - | The second gate's picker, as `GatePick`. |
| `ShapingHolder` | `object` | - | The object whose shaping and gates the line under the source shows. |
| `ResetParamCurveExponentCommand` | `RelayCommand` | - | Resets `ParamCurveExponent` to `0.0`. |
| `ResetParamRangeOuterCommand` | `RelayCommand` | - | Resets `ParamRangeOuter` to `0.0`. |
| `ResetParamAntiDeadzoneCommand` | `RelayCommand` | - | Resets `ParamAntiDeadzone` to `0.0`. |
| `ResetParamStickDeadZoneShapeCommand` | `RelayCommand` | - | Resets `ParamStickDeadZoneShape` to `0`. |
| `ResetParamStickDeadZoneInnerCommand` | `RelayCommand` | - | Resets `ParamStickDeadZoneInner` to `0.0`. |
| `ResetGateDescriptorCommand` | `RelayCommand` | - | Resets `GateDescriptor` to `string.Empty`. |
| `ResetGate2DescriptorCommand` | `RelayCommand` | - | Resets `Gate2Descriptor` to `string.Empty`. |
| `LoadShapingAndGates` | method (internal) | - | Takes the five shaping values and the two gates of `src`, or clears them for none. |
| `StoreShapingAndGates` | method (internal) | - | Writes them onto `dst`. |

---

## ListColumn and RowCell

**File:** `MappingListCells.cs`

The mapping list's columns and cells (#574). `PadViewModel.ListColumns` holds the columns, and each row's `Cells` holds one `RowCell` per column, each with the `RowTag`s of the inputs that drive the row on that column's device.

`ListColumnKind`: `Device` (a device assigned to the controller), `AnyDevice` (sources that name no device), `Gone` (a device a source still names that the controller no longer has), `Fold` (the devices that are not connected, folded into one column while the list has no room for a column each).

### ListColumn

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `MinWidth` | `double` (const) | - | The least width of a device's column. Under it the devices that are not connected fold, and past that the cells scroll sideways. |
| `FoldWidth` | `double` (const) | - | The width of the folded column. |
| `Kind` | `ListColumnKind` | - |  |
| `Guid` | `string` | - | The device's id as sources store it, in lower case. Empty for the any-device column and for the fold. |
| `Device` | `PadViewModel.MappedDeviceInfo` | - | The assigned device, which lights the column's dot while it sends. Null for every other kind of column. |
| `IsFold` | `bool` | - |  |
| `FixedWidth` | `double` | - | The width the column keeps whatever the list's: the fold's. Not a number for a column that shares the room. |
| `Name` | `string` | `string.Empty` | The device's name, "(Any device)", or how many devices the fold holds. |
| `TypeGlyph` | `string` | `string.Empty` |  |
| `TypeShape` | `Geometry` | - | A wheel's or a joystick's drawing in place of the glyph, or null. |
| `TypeName` | `string` | `string.Empty` | The kind of device ("Gamepad", "Wheel"), under its name. |
| `IsAway` | `bool` | - | The device is not connected, or is no longer one of the controller's. Its column is dimmed and shows no live level. |
| `ShowsType` | `bool` | - | The second line names the kind of device. An away device's says it is not connected, and the any-device column and the fold have none. |
| `IsShown` | `bool` | `true` | Whether the column is drawn: an away device's is not while the away devices are folded, and the fold is only then. |

### RowCell

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `Row` | `MappingItem` | - | The row the cell is in. A click on the cell records for it. |
| `Column` | `ListColumn` | - |  |
| `Tags` | `IReadOnlyList<RowTag>` | - |  |
| `Count` | `int` | - | In the fold's cell, how many inputs of the folded devices drive the row. |
| `HasCount` | `bool` | - |  |

### RowTag

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `Word` | `string` | `string.Empty` | "Up", "Down" or "Modifier" for a key of a mode that reads keys. Empty for a source's own input. |
| `Text` | `string` | `string.Empty` | The input's name. |
| `Direction` | `string` | `string.Empty` | Which way a button pushes a stick's axis. Empty where that says nothing. |
| `Mode` | `string` | `string.Empty` | The source's mode, after the last of its tags in the cell, when it is not Direct. |
| `PendingMode` | `string` (internal) | `string.Empty` | The source's mode when it is not Direct, for the tag that turns out to be the source's last under its column. |
| `Line` | `IMappingSourceLine` | - | The source the tag belongs to: the row for its first source, else one of its added sources. A click on the tag records that source again. |
| `Key` | `MappingSourceItem.ParamRecordTarget?` | - | Which key of the source the tag is, or null for the source's own input. |
| `Descriptor` | `string` (internal) | `string.Empty` | The input as the device's state names it, with no flag before it. The live level is read by it. |
| `DeviceGuid` | `string` (internal) | `string.Empty` | The device the input is read on. |
| `HasLevel` | `bool` | - | The input has a level to show: an axis or a slider of a device, as against a button or a key. |
| `ShowsLevel` | `bool` | - | The level is drawn: the input has one and its device is connected. |
| `IsCentered` | `bool` | - | The input rests in the middle of its range, as a stick's axis does, so its level is drawn from the middle. |
| `CenterKnown` | `bool` (internal) | - | Whether `IsCentered` has been worked out from the device, which the first live refresh does. |
| `InputFound` | `bool` (internal) | - | Whether the live refresh has found where the tag's input is in a device's state. It does so once. |
| `Device` | `UserDevice` (internal) | - | The device the level is read on, or null for one the device list did not hold. Found again whenever the device list changed (`DevicesSeen`, `DevicesVersion`). |
| `DevicesSeen` | `DeviceList` (internal) | - | The device list `Device` was found in. |
| `DevicesVersion` | `int` (internal) | - | That list's change count when `Device` was found. |
| `InputIndex` | `int` (internal) | `-1` | The input's index among the state's axes, or among its sliders when `InputIsSlider` is set. -1 reads 0. |
| `InputIsSlider` | `bool` (internal) | - | The input is a slider, as against an axis. |
| `Level` | `double` | - | Where the input stands in its range, 0 to 1. A centered input rests at one half. |
| `LevelText` | `string` | `string.Empty` |  |

---

## ShiftLayerInfo

**File:** `ShiftLayerInfo.cs`

VM wrapper around a single `Engine.Data.ShiftActivator`. Populates the layer tab strip over the mapping list (`PadViewModel.LayerTabs`) and the per-layer context-menu commands.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `LayerMask` | `string` | `"Base"` | Engine-side layer identity (matches `MappingRow.LayerMask`). |
| `LayerName` | `string` | `"Base"` | User-visible display name. |
| `Color` | `string` | `""` | v2 per-layer color hint, `"#AARRGGBB"` or empty. |
| `IsActive` | `bool` | `false` | True when this layer's tab is selected (the one being authored). |
| `IsBase` | `bool` | - | Computed: `LayerMask == "Base"`. Two consumers: the tab chip's color-dot visibility, and the SHIFT pipeline chip's idle summary, which lists only non-Base layer names. It does not gate the tab context menu, whose Base behavior lives in the handlers. Base does show Rename (edits the base appearance), Configure (its flyout and tab appearance), and Delete (the legacy-Base heal path). |

---

## MacroItem

**File:** `MacroItem.cs`

A trigger combination of inputs that produces a sequence of output actions. Evaluated in Step 4b, after Step 4 combines the slot output and before Step 5 writes the virtual devices.

### Identity

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Name` | `string` | `Macro_NewMacro` | User-facing name, seeded from the localized resource (English "New Macro"). The setter is not plain: any post-construction change fires the static `Renamed` event, which is how #390 retags menu cells that referenced the old name. |
| `IsEnabled` | `bool` | `true` | Macro active. |

### Trigger Condition (Button-Based)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TriggerButtons` | `ushort` | `0` | Gamepad button bitmask (e.g., `Gamepad.A \| Gamepad.B`). All must be pressed. |
| `TriggerCustomButtonWords` | `uint[]` | `new uint[4]` | Wide bitmask for custom Extended slots (128 buttons, 4x32-bit). Not serialized. |
| `TriggerCustomButtons` | `string` | `null` | Serializable hex form (e.g., `"00000003,00000000,00000000,00000000"`). |
| `UsesCustomTrigger` | `bool` | - | Computed: any custom trigger button set. |
| `TriggerSource` | `MacroTriggerSource` | `InputDevice` | Record from physical device or virtual controller output. |
| `TriggerDisplayText` | `string` | - | Computed: readable trigger combo with device name. |
| `ButtonStyle` | `MacroButtonStyle` | `Xbox360` | Display name style. Not serialized. |
| `CustomButtonCount` | `int` | `11` | Custom Extended button count. Not serialized. |
| `CarriesPressure` | `bool` | `false` | (#530) True on a PlayStation slot whose preset `HMaestroProfileCatalog.ReportCarriesPressure` names, the DualShock 3 (SIXAXIS): Full. Stamped with `ButtonStyle` (`PadViewModel.SyncMacroButtonStyle`, the add commands, `SettingsService.LoadMacroFromData`) and handed to every action. Not serialized. |

### Trigger Condition (Raw Device Button)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TriggerDeviceGuid` | `Guid` | `Guid.Empty` | Trigger source device. `Empty` = legacy Xbox bitmask. |
| `TriggerRawButtons` | `int[]` | `[]` | Raw button indices. All must be pressed. |
| `UsesRawTrigger` | `bool` | - | Computed: any `TriggerInputs` entry has `RawButton >= 0`, or the legacy pair `TriggerDeviceGuid != Empty && TriggerRawButtons.Length > 0`. The legacy half alone reads false for every entry-list macro. |

### Trigger Condition (POV Hat)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TriggerPovs` | `string[]` | `[]` | POV hat triggers as `"povIndex:centidegrees"` (e.g., `"0:0"` for POV 0 Up). |
| `UsesPovTrigger` | `bool` | - | Computed: any `TriggerInputs` entry carries a non-empty `Pov`, or `TriggerPovs.Length > 0`. |

### Trigger Condition (Axis)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TriggerAxisTargets` | `MacroAxisTarget[]` | `[]` | Axes that must all exceed threshold. Not serialized. |
| `TriggerAxisTargetList` | `string` | `null` | Serializable comma-separated form. |
| `TriggerAxisThreshold` | `int` | `50` | Threshold % (1–100). |
| `UsesAxisTrigger` | `bool` | - | Computed: `TriggerAxisTargets.Length > 0`, or any `TriggerInputs` entry has `AxisTarget != MacroAxisTarget.None`. |
| `TriggerAxisDirections` | `MacroAxisDirection[]` | `[]` | Direction filter per axis. Parallel array. Not serialized. |
| `TriggerAxisDirectionList` | `string` | `null` | Serializable comma-separated form. |
| `TriggerAxisDirectionIndex` | `int` | - | UI index for direction (0=Any, 1=Positive, 2=Negative). Sets all uniformly. |

### Trigger Condition (Descriptor / Device-Free) (#9)

Descriptor entries carry the trigger shapes that have no raw-entry form: engine-read descriptors (`"Gyro Pitch"`, `"Touchpad 0 Finger 0 Down"`, `"Menu {id} Item {k}"`) evaluated through `SourceCoercion`'s button read with the same per-(device, slot) tuning a mapping row gets. Entry-list only, picked from the trigger dropdown, never recorded.

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `TriggerInputEntry.SourceDescriptor` | `string` | `null` | The engine-read descriptor on a trigger-entry row. Serialized through the pipe-joined `TriggerInputs` spec. The plain form is `in:{guid}:sd:{descriptor}` (same tail escaping as gestures). When the entry carries a stamp (`HalfAxis`, `Invert`, `Bidirectional`, or `DescriptorDeadZone > 0`) it writes the extended form instead: `in:{guid}:sdh:{half}:{invert}:{bidi}:{deadzone}:{descriptor}`. |
| `TriggerInputEntry.DescriptorSource` | `MappingSource` | - | Cached wrapper for the descriptor so the 1 kHz trigger evaluation never allocates. Null when the entry isn't a descriptor entry. |
| `UsesDescriptorTrigger` | `bool` | - | Computed: any trigger entry carries a `SourceDescriptor`. |

An entry with `DeviceGuid == Guid.Empty` is device-free: the evaluator resolves it against whatever device sits on the macro's slot, and `TriggerDisplayText` renders it under the localized "(Any device)" sentinel (the same group the mapping picker uses).

### Trigger Options

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TriggerMode` | `MacroTriggerMode` | `OnPress` | Twelve modes, ordinals pinned: `OnPress` (0), `OnRelease` (1), `WhileHeld` (2), `Always` (3), `CustomExpression` (4, v3.2), `HoldForMs` (5, On Long Press), `DoublePress` (6), `TriplePress` (7), `SinglePress` (8), `Toggle` (9), `Turbo` (10), `ShortPress` (11, On Short Press, #253). |
| `TriggerHoldMs` | `int` | `500` | Hold threshold shared by `HoldForMs` and `ShortPress`, the tap-vs-hold pair (#9 wave 1b). Clamped 50-10000. `ResetTriggerHoldMsCommand` puts it back to 500. |
| `TriggerDoublePressMs` | `int` | `442` | Multi-press window for the Single / Double / Triple modes. Clamped 50-5000. The default is the double-tap window Valve's own shipped `controller_base` templates author (`basicui.vdf` / `basicui_neptune.vdf`, `"double_tap_time" "442"`). `ResetTriggerDoublePressMsCommand` puts it back to 442. |
| `LayerMask` | `string` | `""` | Per-macro shift-layer scope (#254). Empty fires on any layer. `"Base"` opens only while Base is effectively engaged, honoring the engaged layer's `InheritUnmapped` exactly like a Base row does. Any other value opens only while that layer is engaged, scoped to the macro's own slot. When the macro's own slot does not declare the mask at all, any slot's engagement still opens it. A null write is ignored: the editor's Layer ComboBox coerces `SelectedValue` to null when the selected choice disappears, which silently downgraded a scoped macro to "any layer". `HasLayerScope` and `ShowsLayerRow` both read `LayerMask` non-empty. |
| `IsNotAlwaysMode` | `bool` | - | Computed: `TriggerMode != Always`. Controls trigger UI visibility. |
| `ConsumeTriggerButtons` | `bool` | `true` | Remove trigger buttons from Gamepad state on fire. |

### Recording

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `IsRecordingTrigger` | `bool` | `false` | Recording trigger combo. Notifies `RecordTriggerButtonText`. |
| `RecordTriggerButtonText` | `string` | - | Computed: `"Stop"` or `"Record Trigger"`. |
| `RecordingLiveText` | `string` | `""` | Live display of buttons pressed during recording. Not serialized. |

### Actions

| Property | Type | Description |
|----------|------|-------------|
| `Actions` | `ObservableCollection<MacroAction>` | Ordered sequence of actions to execute. |
| `SelectedAction` | `MacroAction` | Selected action. Refreshes remove command. |

### Repeat Settings

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `RepeatMode` | `MacroRepeatMode` | `Once` | How actions repeat: `Once`, `FixedCount`, `UntilRelease`, `UntilNextPress`. `UntilNextPress` repeats until the trigger is pressed again. The press that started the run does not count, and releasing it changes nothing. The press that ends the run sets the same re-arm gate as an Until Release stop (the trigger must read inactive once before the macro fires again). Appended, since the clipboard writes the enum as a number. The reWASD translator uses it for gesture triggers (`RewasdTranslator`). |
| `RepeatCount` | `int` | `1` | Repeat count for FixedCount mode. Min 1. |
| `RepeatDelayMs` | `int` | `100` | Delay between repeats (ms). Min 0. |

### Runtime State (not serialized)

| Property | Type | Description |
|----------|------|-------------|
| `IsExecuting` | `bool` | Executing action sequence. |
| `CurrentActionIndex` | `int` | Position in action sequence. |
| `RemainingRepeats` | `int` | Remaining repeat count. |
| `ActionStartTime` | `DateTime` | When current action/delay started. |
| `WasTriggerActive` | `bool` | Trigger active on previous frame. |

### Commands

| Command | Description |
|---------|-------------|
| `RecordTriggerCommand` | Toggles `IsRecordingTrigger` and raises `RecordTriggerRequested`. |
| `ClearTriggerCommand` | Stops a trigger recording in progress, then clears every trigger form: the button masks, the raw buttons and their device, the axis targets and directions, the POVs, and the trigger-entry list. |
| `AddActionCommand` | Adds a new `MacroAction` with default type `ButtonPress` and this macro's button style, count, and profile. |
| `DuplicateActionCommand` | Clones the selected action through the action DTO and inserts the copy right after it (#112). CanExecute: `SelectedAction != null`. |
| `RemoveStepCommand` | `RelayCommand<MacroAction>`: removes the action passed, by the remove at its own step's end (#574). The selected action stays selected unless it is the one removed, and then the last one is. |

| Event | Description |
|-------|-------------|
| `RecordTriggerRequested` | Trigger recording toggled. |

---

### MacroItem: Trigger Inputs

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `OutputChannelOptions` | `IList<MacroOutputChannelOption>` | - | Style- and culture-aware list of channels for the per-variable OutputController dropdown. Labels mirror the mapping table for the same VC family (e.g. PlayStation slot → ✕/○/◻/△ + L1/R1/L2/R2/Share/Options/PS. Extended slot → Button 1 / Button 2 / …. Xbox slot → A/B/X/Y + Left Shoulder / Right Shoulder / etc.). |
| `PairId` | `int` | - | Nonzero links the two legs of a materialized hold pair (audit #2 M4/M6): the press leg SETs the ToggleKey / ToggleMouseButton latch, the OnRelease twin CLEARs it, and the shared id is how they reach each other at runtime. A starting leg cancels its executing twin, so a re-press kills the twin's pending delayed release before the stale Clear can cut the new hold short, and an Off fire clears the twin's latches (each leg's latch state lives on its own action instance). 0 = unpaired, every macro the editor creates. Persisted via `MacroData.PairId`, like `PadIndex`. |
| `ButtonLabel` | method (internal, static) | - | A raw button's label in a trigger's text: the device object's name as the mapping picker shows it (`LocalizeObjectName`), or "Button N" when the device names none. A row that publishes its names in English, a keyboard screen's keys or a Falcon's grip buttons, reads in the current language here too. |
| `FormatPovTrigger` | method (internal, static) | - | Formats a stored POV trigger ("povIndex:centidegrees") to display text ("POV 0 Up"). |
| `ParsePovTrigger` | method (internal, static) | - | Parses a stored POV trigger ("povIndex:centidegrees") into its components. |
| `UsesGestureTrigger` | `bool` | - | True if this macro uses touchpad-gesture trigger entries (#177). Gesture entries only exist in the multi-device `TriggerInputs` spec. There is no legacy form. |
| `TryBuildTriggerEntry` | method (static) | - | Converts a picker `InputChoice` into a `TriggerInputEntry` for the macro trigger dropdown (#177). Returns false for descriptors the trigger engine has no entry shape for (finger position axes, sliders, continuous gesture axes). Buttons, POV directions, gamepad-layout axes 0-5, the touchpad click (raw button 16), bool-valued touchpad gestures, gyro axes, "Finger M Down", MIDI notes, CCs and encoder detents, and IR Offscreen all convert. An empty `DeviceGuid` converts too (#9 B-9): it is the picker's "(Any device)" group and stores `Empty`, the persisted "the device on the macro's slot" form the evaluator resolves per slot device. |
| `GetTriggerInputEntries` | method | - | Returns the current parsed entries. Migrates from legacy single-device fields on first access. Hot path: called every macro evaluation frame via `UsesRawTrigger` / `CheckRawButtonTrigger`. The migrated cache is reused. |
| `TriggerAxisEntries` | `IEnumerable<TriggerInputEntry>` | - | Subset of `GetTriggerInputEntries` containing just the axis-bearing entries: used by the per-entry editor in the macro trigger panel so the user can toggle Invert / HalfAxis and adjust DeadZone the same way the merge-mapping editor exposes them on axis-to-button sources. |
| `HasLegacyAxisTrigger` | `bool` | - | True when the macro has legacy slot-combined axis targets (the OutputController-source path): drives the visibility of the legacy single Threshold + Direction sliders. Mutually exclusive in practice with `HasTriggerAxisEntries` since the recorder writes to one path or the other based on TriggerSource. |
| `HasTriggerAxisEntries` | `bool` | - | True when the macro has at least one per-device axis entry. Drives the visibility of the per-entry axis editor panel. |
| `SetTriggerInputEntries` | method | - | Replaces the entry list, which becomes authoritative. Used by the recorder when finalizing a multi-device combo and by the per-row remove. The legacy single-device raw-button and POV mirrors are dropped here. First access migrates those fields INTO the entry list without clearing them, so both copies then describe the same inputs, and the evaluator falls back to the legacy copy whenever the entry list holds no button. Removing the last visible entry therefore handed control to an invisible duplicate and the removed button kept firing the macro. The entry list is what the editor shows, so it decides. A caller that still wants the back-compat mirror writes it after this returns, which is exactly what the recorder does. |
| `TriggerInputItems` | `IEnumerable<MacroTriggerInputItem>` | - | Every individual input that makes up the trigger, one removable row: the per-device entries plus any legacy slot-combined bitmask buttons and axis targets, mirroring what `TriggerDisplayText` renders. UI-only (the evaluator reads the underlying fields directly and never touches this), and regenerated on each bind like `TriggerAxisEntries`. |
| `HasTriggerInputItems` | `bool` | - | True when the trigger has at least one input to list. Cheap (no item/command allocation) so the empty-state placeholder can bind to it without walking `TriggerInputItems`. |
| `ShowsLegacyAxisRows` | `bool` | - | True when the editor's Threshold and Direction rows show: the trigger-combo panel is up and the macro holds legacy slot-combined axis targets. The More fold's hint names the two rows by this rule. |
| `HasSameTrigger` | method (internal) | - | True when the other macro reads exactly the trigger this one does. |
| `GetAxisDirection` | method | - | Gets the direction for a trigger axis at the given index, defaulting to Any. |

### MacroItem: Custom Trigger Expression

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `TriggerExpression` | `string` | `""` | User-typed formula. Empty / whitespace compiles to literal 0 (trigger never active). Changes invalidate the cached compile. |
| `TriggerExpressionCompiled` | `Compiled` | - | Returns the cached compile, recomputing if dirty. Hot path: called every macro evaluation frame in CustomExpression mode. |
| `TriggerExpressionVariables` | `ObservableCollection<MacroExpressionVariable>` | - | Ordered list of variables for the custom-expression trigger. Variable at index 0 binds to `a`, index 1 to `b`, etc. Also addressable as `s[0]`, `s[1]`, ... in the formula. |
| `VariableCount` | `int` | - | Number of variables defined for the custom-expression trigger. Drives the chip-palette visibility so users only see letters that map to a real variable. |
| `TriggerExpressionVariableSpecs` | `string` | - | Serializable list of the variables' Spec strings, joined with '\|'. Empty entries are preserved so a/b/c/... indexing is stable across a load even if some variables are still unbound. |
| `IsCustomExpressionMode` | `bool` | - | True when this macro's trigger uses the custom-expression path. |
| `CustomExpressionStatus` | `string` | - | Localized "valid" / parse-error string for the editor footer. Mirrors the merge-mapping `CombineExpressionStatus` shape. |
| `IsCustomExpressionInvalid` | `bool` | - | True when the expression failed to parse. |
| `IsCustomExpressionWarning` | `bool` | - | True when the expression parses but references a variable the macro has not defined. Same rule as the footer text. |
| `MaxExpressionVariables` | `int` (const) | - | Variable ceiling for a custom-expression macro. The editor labels each row from the ItemsControl's AlternationIndex, which WPF assigns cyclically, so past this count two rows would carry the SAME letter while the evaluator still binds them positionally: the user would edit one variable and the formula would read the other (round 34). Keep in sync with AlternationCount on the TriggerExpressionVariables ItemsControl in PadPage.xaml. |
| `AddExpressionVariableCommand` | `RelayCommand` | - | Adds a variable to the custom trigger expression, up to `MaxExpressionVariables`. |
| `RemoveExpressionVariableCommand` | `RelayCommand<MacroExpressionVariable>` | - | Removes one variable from the list. Subsequent variables shift letters (b becomes a, etc.): that matches how the merge- mapping editor handles ExtraSources deletion, so the formula's references stay positionally meaningful. |

### MacroItem: Editor Gates

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `PadIndex` | `int` | `-1` | Pad index (0-based) of the slot that owns this macro. Set when the macro is added to a slot's collection or loaded from XML. Used by `LightbarColor` to resolve the target `DeviceSlotConfig` at fire time. Not serialized: the parent `MacroData.PadIndex` is the persisted source of truth and gets reapplied on load. |
| `RecordTriggerIcon` | `string` | - | The trigger record button's glyph, which swaps while the trigger records. |
| `RawProfileId` | `string` | - | The Extended slot's HIDMaestro profile slug, stamped by PadViewModel beside ButtonStyle (#215). Null on non-Extended slots. Re-letters the Numbered labels on Switch Pro profiles. The mask / index value spaces are untouched. |
| `SoundFilesSummary` | `string` | - | Compact "file1, file2" summary of this macro's Play Sound actions, for the Audio group's sound-macro hub list. |
| `ShowsHoldTimeRow` | `bool` | - | True when the shared hold-time ms row shows (#253): HoldForMs fires AT the threshold, ShortPress fires at release UNDER it. One row, one stored value, two directions (the ShowsInlineIntervalRow precedent). |
| `HoldTimeToolTip` | `string` | - | Tooltip for the shared hold-time row, following the active mode (the TriggerPressWindowToolTip idiom). Re-raised on mode and culture changes. |
| `ShowsInlineIntervalRow` | `bool` | - | True when the inline repeat-interval ms row shows beside the Fire picker (#238): Turbo (the interval is the turbo rate) and Toggle (while latched, the sequence re-runs at this interval). Both modes force until-release repeats in the engine, so the interval is their only live repeat setting and it sits where the mode was chosen. |
| `ShowsRepeatSection` | `bool` | - | False when the Repeat section (Mode / Count / Interval) hides (#238): Turbo and Toggle override RepeatMode and RepeatCount in the engine, so showing dead controls would let the user author settings that silently do nothing. Their one live knob, the interval, moves to the inline row beside the Fire picker instead. |
| `SupportsUntilReleaseRepeat` | `bool` | - | False for ShortPress, where Until Release is the one repeat setting the engine ignores. A ShortPress run starts with the trigger ALREADY released, so the deferred-completion flag is set and the until-release branch can never run. That is true of Until Release only. A fixed count works there exactly as it does elsewhere, because the executor arms RemainingRepeats from RepeatCount for every mode and decrements it independently of that flag. Hiding the whole section for ShortPress therefore hid a live setting: a loaded or mode-switched fixed repeat kept running with no way to see or edit it. |
| `InlineIntervalToolTip` | `string` | - | Tooltip for the inline interval row, following the active mode (the TriggerPressWindowToolTip idiom): the turbo rate for Turbo, the while-latched pacing for Toggle. Re-raised on mode and culture changes. |
| `IsDoublePressMode` | `bool` | - | True when TriggerMode is DoublePress (translator v17), TriplePress, or SinglePress (#238, all three consume the same press window: the chains chain through it, the single defers by it). Gates the press-window ms row in the trigger editor. |
| `TriggerPressWindowToolTip` | `string` | - | Tooltip for the shared press-window ms row (#238): the double- or triple-press explanation, following the active trigger mode. Re-raised on mode and culture changes. |
| `ShowsTriggerComboEditor` | `bool` | - | True when the standard trigger-combo recording UI should show (i.e. one of OnPress / OnRelease / WhileHeld / HoldForMs / DoublePress / TriplePress / SinglePress / Toggle / Turbo). Always mode has no trigger. CustomExpression mode uses the formula editor instead. |

### MacroItem: Runtime State (not serialized)

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ReleaseLingerMs` | `int` | - | Release linger for UntilRelease macros (translator v22, Steam's activator `delay_end` on autofire: "wait for this period of time after the button has been released before deactivating"). When nonzero, the trigger's release does not stop the executing macro immediately. The pulse train keeps running this many milliseconds past the release, and a re-press inside the window cancels the pending stop (the M6 cancel-on-re-press shape applied to the pulse stop leg). 0 = stop at release, every macro the editor creates. Persisted via `MacroData.ReleaseLingerMs`, like `PairId`. |
| `ReleaseLingerStartUtc` | `DateTime` | `MinValue` | Runtime deadline of the pending linger stop (UTC). MinValue = no pending stop. Owned by the Step4b evaluators. |
| `LastEvaluatedUtc` | `DateTime` | `DateTime.MinValue` | UTC time of the last evaluator tick that OBSERVED this macro's trigger (audit 2026-07-25 round four, replacing the round-three sticky bool). `WasTriggerActive` is only trustworthy when observation was CONTINUOUS: after any gap (engine stop, the macro disabled, its slot idle-skipped, a profile hot-retain), the previous sample is stale and an apparent edge on the first tick back may have happened entirely unwatched. The sticky bool modeled "sampled sometime", so every one of those gap sources re-created the held-at-start bug it was added to fix. A stamp self-heals them all: a rising edge only arms On Short Press when the previous tick is recent. Poll-thread transient. |
| `TriggerLastPressUtc` | `DateTime` (internal) | `DateTime.MinValue` | Transient timing state for `DoublePress`: the UTC time of the previous rising edge, or `MinValue` when no first press is armed. Never serialized. |
| `TriggerPressStreak` | `int` (internal) | - | TriplePress chain length so far (#238): how many rising edges the current fast-press chain holds. Volatile runtime state, reset when a press lands outside the window and consumed on fire. |
| `TriggerHoldStartUtc` | `DateTime` (internal) | `DateTime.MinValue` | Transient timing state for `HoldForMs`: the UTC time the trigger combo last went active (rising edge). The evaluator arms it on each press and fires once the hold crosses `TriggerHoldMs`. Never serialized. |
| `TriggerHoldFired` | `bool` (internal) | - | True once the current hold has fired, so a single hold never double-fires. Re-armed (cleared) by the evaluator on the next rising edge. Never serialized. |
| `HoldForBeside` | `MacroItem` (internal) | - | The Hold For macro on this Single Press macro's trigger, found at the press (#561). Never serialized. |
| `RunReleasedFireToCompletion` | `bool` (internal) | - | Set when a deferred SinglePress fired with the button already released (audit 2026-07-18): the activation runs its sequence ONE full pass, with the UntilRelease release-stop suppressed until the pass completes (the release already happened before the fire). Cleared on completion, disable, mode switch, and pair-cancel. |
| `MenuTriggerTick` | `long` | `-1` | Menu-cell trigger stamp (#390): the macro pass tick on which a fired menu cell last named this macro. The menu runtime's per-tick walk stamps it BEFORE the evaluators run, and both evaluator twins treat a current stamp as trigger-active alongside the macro's own triggers, so every trigger mode keeps its semantics. A stale stamp is simply false: no clearing pass exists or is needed. Poll thread only. |
| `MenuTriggerExitLayer` | `string` | - | The layer a cell's commit was made in, when leaving that layer made it (DC20), stamped beside `MenuTriggerTick`. The macro's Layer scope reads that commit against this layer, not the one engaged after the exit. Null for every other fire. Poll thread only. |
| `ToggleRawWasActive` | `bool` | - | Raw trigger state on the previous frame for the Toggle mode's edge detector (#238). Separate from `WasTriggerActive`, which stores the LATCH the evaluator presents downstream. Runtime only. |
| `ToggleTriggerLatched` | `bool` | - | The Toggle mode's latch (#238): flipped on each raw rising edge, presented downstream as the trigger state, cleared on disable, mode switch, and layer close. Runtime only. |
| `ComboResumeIndex` | `int` | - | Combo-break park position (discussion #237): the action index the NEXT start resumes from. 0 = start from the top. Set by a `ComboBreak` action, cleared on normal sequence completion, UntilRelease stop, disable, profile switch, engine stop, and app restart (volatile). |
| `AwaitReleaseAfterBreak` | `bool` | - | Set when a combo break parks the sequence while the trigger is still held: hold-shaped trigger modes (WhileHeld, Always) must not auto-resume through the break, so the start gate stays closed until the trigger reads inactive once. The press that ends an Until Next Press run sets it for the same reason. |

### MacroItem: Commands and Resets

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ResetSettingCommand` | `RelayCommand<string>` | - | Resets setting to its default. |
| `CanResetSetting` | method (internal, static) | - | The names `ResetSettingCommand` accepts on this class. |
| `ResetRepeatDelayMsCommand` | `RelayCommand` | - | Resets the repeat interval to the 100 ms default, for the Turbo mode's inline interval row (#238). |
| `RemoveStepCommand` | `RelayCommand<MacroAction>` | - | Removes one action, by the remove at its own step's end (#574). The selected action stays selected unless it is the one removed, and then the last one is, as Remove leaves it. |

### MacroAction

**File:** `MacroItem.cs` (a separate top-level class in the same file, not nested inside `MacroItem`)

Single action in a macro's sequence.

### Core Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Type` | `MacroActionType` | `ButtonPress` | Action type. Notifies all `Is*Type` properties. |
| `DurationMs` | `int` | `50` | Hold/delay duration (ms). Min 0. |
| `DisplayText` | `string` | - | Computed: readable action summary. |

### Type-Check Properties (all computed, not serialized)

One `Is*Type` flag per action family, plus the rolled-up families the editor gates whole panels on (`IsAnyRumbleSetType`, `IsAnyRumbleStopType`, `IsAnyAxisValueType`, `IsAnyVcButtonType`, `IsAnyKeyType`, and the rest). A representative set: `IsButtonType`, `IsKeyType`, `IsDurationType`, `IsAxisType`, `IsSystemVolumeType`, `IsAppVolumeType`, `IsMouseMoveType`, `IsMouseButtonType`, `IsContinuousAxisType`, `IsDeviceAxisSource`, `IsOutputAxisSource`.

### Button Action Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ButtonFlags` | `ushort` | `0` | Xbox bitmask for gamepad presets. |
| `ButtonStyle` | `MacroButtonStyle` | `Xbox360` | Display name style. Not serialized. |
| `CustomButtonCount` | `int` | `11` | Numbered style button count. Not serialized. |
| `CarriesPressure` | `bool` | `false` | (#530) The owning macro's flag, set by Add Action and Duplicate Action too. The axis pickers show the ten pressure targets only while it is true. Not serialized. |
| `CustomButtonWords` | `uint[]` | `new uint[4]` | Wide bitmask for Extended slots (128 buttons). Not serialized. |
| `CustomButtons` | `string` | `null` | Serializable hex form. |
| `ButtonOptions` | `IReadOnlyList<GamepadButtonOption>` | - | Computed: checkbox-bindable list. Lazy-built from style and count. |

| Method | Description |
|--------|-------------|
| `SetCustomButton(int, bool)` | Sets/clears a custom Extended button by 0-based index. |
| `IsCustomButtonPressed(int)` | Returns whether a custom button is pressed. |
| `HasCustomButtons` | Computed: any custom button is set. |

### Key Action Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `KeyCode` | `int` | `0` | Win32 VK_ code. Notifies `SelectedVirtualKey`. |
| `SelectedVirtualKey` | `VirtualKey` | `None` | Enum wrapper for ComboBox. Not serialized. |
| `KeyString` | `string` | `""` | Multi-key combo in x360ce format (`"{Control}{Alt}{Delete}"`). |
| `ParsedKeyCodes` | `int[]` | - | Computed: VK codes from `KeyString`, falling back to `KeyCode`. |
| `SelectedKeyToAdd` | `VirtualKey` | `None` | Key picker binding. Auto-appends to `KeyString` and resets. |

| Command | Description |
|---------|-------------|
| `ClearKeyStringCommand` | Clears the `KeyString`. |

| Static | Description |
|--------|-------------|
| `VirtualKeyValues` | `List<KeyDisplayItem>` with localized display names. Rebuilt on culture change. |
| `ParseKeyString(string)` | Parses `"{Key1}{Key2}..."` into `int[]` of VK codes. |

### Axis Action Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `AxisValue` | `short` | `0` | AxisSet: signed value (−32768 to 32767). |
| `AxisTarget` | `MacroAxisTarget` | `None` | Which axis to set/read. |
| `InvertAxis` | `bool` | `false` | Invert axis value. |

### Volume Action Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ShowVolumeOsd` | `bool` | `true` | Trigger Windows volume OSD. |
| `ProcessName` | `string` | `""` | AppVolume: target process name. |
| `AudioProcessNames` | `ObservableCollection<string>` | empty | Processes with active audio sessions (suggestions). |
| `VolumeLimit` | `int` | `100` | Max volume % (1–100). |

| Command | Description |
|---------|-------------|
| `RefreshAudioProcessesCommand` | Refreshes active audio session process list. |

### Mouse Action Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `MouseSensitivity` | `float` | `10f` | Pixels/scroll units per frame at full deflection (1–100). |
| `MouseButton` | `MacroMouseButton` | `Left` | Mouse button for press/release. |
| `CursorClampOffsetX` / `CursorClampOffsetY` | `int` | `0` | Limit Mouse Region (#110) offset, in pixels, from the screen's center: right and down are positive. Clamped to half the primary monitor's width or height either way. Zero keeps the region centered. `ResetCursorClampOffsetXCommand` and `ResetCursorClampOffsetYCommand` return them to 0. The reWASD translator sets them so a region off center lands where reWASD put it (#561). |
| `MouseAccumulator` | `float` | `0` | Internal `[XmlIgnore]` field, not a property: the fractional pixel accumulator that keeps sub-pixel precision across ticks. |

### Axis Source Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `AxisSource` | `MacroAxisSource` | `OutputController` | Axis value source. |
| `SourceDeviceGuid` | `Guid` | `Guid.Empty` | InputDevice source: physical device GUID. |
| `SourceDeviceAxisIndex` | `int` | `-1` | InputDevice source: axis index in `InputState.Axis[]`. |

### Pressure-Scaled Turbo (#290, #393)

Applies to the repeat-interval action family (`RepeatKeyWhileHeld`, `RepeatVcButtonWhileHeld`, the toggles pulsing under `PulseWhileLatched`, and the rest of the `IsRepeatIntervalType` set). While the gate is on, the repeat rate follows a physical analog source (DualShock 3 button pressure, any trigger) instead of the fixed `IntervalMs`. `IntervalMs` becomes the fast end (full press) and `SlowIntervalMs` the slow end, interpolated in rate space so a light press is a defined slow rate.

**Pressure direction comes from the trigger (#393).** The read used to be the raw axis position, `raw / 65535`, so on a stick's lower half a harder push read as falling pressure and a gentle push repeated faster than a hard one. A macro that fires on a stick half already says which half, so the engine takes the direction from there rather than adding a knob. `InputManager.ResolveTurboPressure01` resolves the 0..1 pressure in three steps:

1. A `TriggerInputs` entry on the pressure source's axis, on the same device or device-free (`Guid.Empty`, the picker's "(Any device)" form). An entry pinned to the source device outranks a device-free one on the same axis. A half-axis entry reads deflection from center into the half it selects: `Invert` takes the lower half, `Bidirectional` takes both sides. A full-axis entry is trigger-style and reads `raw / 65535`, flipped by `Invert`.
2. Otherwise a legacy `TriggerAxisTargets` slot target on the corresponding gamepad axis: `Positive` and `Negative` read deflection from center into that half, `Any` reads `raw / 65535`.
3. Otherwise `raw / 65535`, byte-identical to the #290 read. A pressure source that is not the macro's trigger keeps exactly what it shipped with.

Every direction now ramps 0 at rest to 1 at full push, which is what the ramp endpoints, the curve, and the rate blend were written against. The volume and mouse actions keep `ReadAxisFromDevice`, where absolute position is the meaning.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `PressureScaledRate` | `bool` | `false` | Master gate. Off keeps every existing macro on the legacy fixed-rate path. |
| `SlowIntervalMs` | `int` | `500` | Light-press period in ms. Clamped 10–2000 here, and floored at `IntervalMs` at evaluation time so slow can never outrun fast. |
| `TurboRateCurve` | `string` | `"Linear"` | Curve applied to the 0..1 pressure before the rate interpolation. Same vocabulary as the mapping rows' output curves: `Linear`, `Aggressive`, `Relaxed`, `Wide`, `ExtraWide`. Empty collapses to `Linear`. |
| `TurboRateCurveOptions` | `IReadOnlyList<GyroLabeledOption>` | - | Live-language curve choices for the dropdown. |
| `PressureStartPercent` | `int` | `0` | Pressure at which the ramp leaves the slow rate. Below it the rate stays at `SlowIntervalMs`. Clamped 0–99. The remap runs before the curve. |
| `PressureEndPercent` | `int` | `100` | Pressure at which the ramp reaches the full-press rate. Clamped 1–100. The engine floors the span at one percent. |
| `ShowsPressureTurboRows` | `bool` | - | Computed: `IsRepeatIntervalType && PressureScaledRate`. Gates the card's extra rows. |

**Reset commands:** `ResetIntervalMsCommand` (100 ms), `ResetSlowIntervalMsCommand` (500 ms), `ResetPressureStartCommand` (0), `ResetPressureEndCommand` (100).

### Disconnect Action Properties (#162)

For `MacroActionType.DisconnectController`. The target is set on the action, not the trigger, so a macro can turn off device X from a chord on device Y.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `DisconnectTarget` | `MacroDisconnectTarget` | `TriggeringDevice` | Which device(s) the disconnect targets. Notifies `DisplayText` and `IsDisconnectSpecificDevice`. |
| `DisconnectDeviceGuid` | `Guid` | `Guid.Empty` | Victim device for `SpecificDevice` mode. Notifies `DisplayText`. |
| `IsDisconnectSpecificDevice` | `bool` | - | Computed: `IsDisconnectControllerType && DisconnectTarget == SpecificDevice`. Drives the specific-device picker's visibility. |
| `DisconnectDeviceOptions` | `List<MacroDisconnectDeviceOption>` | - | Computed on read (`[XmlIgnore]`). Every known device on a Bluetooth path (`BluetoothLinkHelper.IsDisconnectTarget`). If the saved `DisconnectDeviceGuid` is offline or forgotten it is appended as a synthetic option, so the selection stays visible in the picker. Populates the Specific-device picker. |

### Key Color Properties (#557)

For `MacroActionType.SetKeyColors` (`IsSetKeyColorsType`) and `MacroActionType.ClearKeyColors` (`IsClearKeyColorsType`). Both share the target list (`IsKeyColorTargetsType`). The color is the `LightbarR` / `LightbarG` / `LightbarB` trio, as Set Chroma Color's is. The slot's key-color store runs the action.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `KeyColorTargets` | `string` | `""` | The lights named, in the order picked: `kUU` for a key by HID usage, `gNAME` for a group of lights, `all` for every light (`KeyColorTarget.Parse` / `Format`). Keys go by usage, so one action lights the same keys on any keyboard. A setter normalizes through parse and format. A Clear Key Colors that names none ends every running action. |
| `KeyColorTargetCount` / `HasNoKeyColorTargets` | `int` / `bool` | - | Computed. A Set Key Colors that names no light lights nothing, and the editor says so. |
| `KeyColorTargetsParsed` | `KeyColorTarget[]` | - | Internal, `[XmlIgnore]`: the parsed list, cached per text, because an action that repeats while held reads it on every poll. |
| `KeyTargetPicker` | `KeyTargetPickerViewModel` | - | `[XmlIgnore]`: the editor's key picker over `KeyColorTargets`. See [KeyTargetPickerViewModel](#keytargetpickerviewmodel-557). |
| `KeyColorStyle` | `MacroKeyColorStyle` | `Steady` | `Steady` (the color until the action ends), `Fade` (dims to off over the time) or `Countdown` (keys go dark one by one, the last one picked first). Fade and Countdown always run for `KeyColorMs`. |
| `KeyColorHold` | `MacroKeyColorHold` | `Duration` | How a steady action holds: `Duration`, `UntilRelease` (until the macro's trigger is let go) or `UntilCleared` (until a Clear Key Colors action). `EffectiveKeyColorHold` is this for Steady and `Duration` otherwise. |
| `KeyColorMs` | `int` | `3000` | Length when the action runs for a time. Clamped to 1-600000 ms. |
| `KeyColorRest` | `MacroKeyColorRest` | `Keep` | What the lights the action leaves out show meanwhile: `Keep` (their own colors from the Lighting group), `Off`, or `Color` (the second color). |
| `KeyRestR` / `KeyRestG` / `KeyRestB` | `byte` | `0` | The second color when `KeyColorRest` is `Color`. |
| `IsKeyColorHoldShown`, `IsKeyColorTimed`, `IsKeyRestColorShown` | `bool` | - | Computed editor gates: the hold picker shows for a steady Set Key Colors, the time row when the effective hold is `Duration`, the second color when the rest is `Color`. |

`MacroKeyColorStyle`, `MacroKeyColorHold` and `MacroKeyColorRest` live in `MacroKeyColorChoices.cs`, saved by name and append-only.

### Screen Overlay and Keyboard Screen Action Properties (#519, #560)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ScreenKind` | `KeyboardScreenKind` | `Monochrome` | For Show Keyboard Screen and Keyboard Screen Mode: the kind of screen the action acts on, including `Overlay`. An undefined value reads as `Monochrome`. `ScreenKindIndex` is the list position. |
| `ScreenOverlayNumber` | `int` | `0` | The Screen Overlay the action acts on, 1-8, or `0` for every overlay. Clamped to 0-`MaxOverlays`. A macro on any slot reaches it. `IsScreenOverlayTargetType` is true for `ToggleScreenOverlay`, `PanKeyboardScreen`, and the two kind-naming types when `ScreenKind` is `Overlay`. |
| `ScreenOverlayChoices` | `IReadOnlyList<ScreenOverlayChoice>` | - | `[XmlIgnore]`: the editor's list, from `KeyboardScreenService.OverlayChoices()`. A new list clears the box's selection, so the number goes back to it by value (`ScreenOverlayNumber` is re-raised after). |
| `ScreenFrames` | `string` | `""` | Show Keyboard Screen: up to `KeyboardScreenService.MaxFrames` (8) pictures, each a base64 PNG at the kind's size (the Screen Overlay's own proportions), comma-joined. |
| `ScreenFrameMs` | `int` | `1000` | How long each picture shows. Clamped to `MinFrameMs` (100) to 600000. |
| `ScreenRepeat` | `int` | `1` | Times the pictures play before the screen returns to its mode. Clamped 0-1000. `0` holds the last picture until another Show Keyboard Screen or a Keyboard Screen Mode macro. |
| `PanDirection` / `PanStep` | `KeyboardScreenPanDirection` / `int` | `Right` / `16` | Pan Keyboard Screen Picture: the window's direction and distance in picture pixels. `PanStep` clamps to 1-`KeyboardScreenRenderer.MaxPictureSide` (2048). |
| `ScreenMode` / `StopwatchAction` | `KeyboardScreenMode` / `KeyboardScreenStopwatchAction` | `KeyboardScreenData.DefaultMode` / `StartPause` | Keyboard Screen Mode and Stopwatch. |

Show Dreamcast Screen (#469) has the same shape: `DreamcastFrames`, `DreamcastFrameMs` (at least `DreamcastScreenService.MinFrameMs`, at most 600000), `DreamcastRepeat` (1-1000).

### Profile Shortcut Action Properties (#561)

For `MacroActionType.ProfileShortcut` (`IsProfileShortcutType`): does what a Profile Shortcut does, so a translated reWASD or DS4Windows profile switch needs no separate shortcut. A shortcut row works in every profile. This action belongs to the macro's own profile and layer and names its profile by name, so that profile can arrive later. See [Profile Import Internals](profile-import-internals.md).

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ProfileShortcutMode` | `SwitchProfileMode` | `Specific` | `Specific`, `Next`, `Previous`, `ToggleWindow` or `ToggleVCsDisabled`. `ProfileShortcutModeIndex` is the list position, and an undefined index reads as `Specific`. |
| `ProfileShortcutName` | `string` | `""` | The profile for `Specific`. `ShowsProfileShortcutName` gates the box. |
| `ProfileShortcutChoices` | `IEnumerable<string>` | - | `[XmlIgnore]`: the profile names `SettingsManager.Profiles` holds. The box also takes a name no profile has yet. |

### Adaptive Trigger Effect Properties (#531)

For `MacroActionType.TriggerEffect` (`IsTriggerEffectType`) and `MacroActionType.TriggerEffectStop` (`IsTriggerEffectStopType`). The effects are the DSX trigger modes, encoded by the game mods' encoder (`GameModProtocol.TryEncodeTrigger`, #529). `TriggerEffectCatalog` (`PadForge.App/ViewModels/TriggerEffectCatalog.cs`) lists the 20 kinds, each with its mode number, label and parameters. How a held effect reaches the triggers is on [Game Telemetry Internals](game-telemetry-internals.md).

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TriggerEffectSide` | `MacroTriggerEffectSide` | `Right` | The trigger the effect plays on, or that Stop ends: `Right`, `Left` or `Both`. |
| `TriggerEffectMode` | `int` | `13` | The DSX trigger mode. 13 is the one the editor calls Feedback. A change of effect starts the values at the new effect's defaults, except while a settings file loads them (`LoadTriggerEffect`). |
| `TriggerEffectKind` | `TriggerEffectKind` | - | Computed (`[XmlIgnore]`): the picker's selection, the catalog entry for `TriggerEffectMode`. |
| `TriggerEffectParameters` | `string` | the effect's defaults | The values in the encoder's order, comma-separated, as the settings file stores them. A list shorter than the effect's takes the effect's defaults for the rest. |
| `TriggerEffectRows` | `ObservableCollection<TriggerEffectParameterValue>` | - | Computed (`[XmlIgnore]`): the editor's rows, one per parameter of the effect, rebuilt when the effect changes. |
| `TriggerEffectIsValid` | `bool` | - | Computed (`[XmlIgnore]`): false when the encoder refuses the values, an end zone not past its start or a second foot not past the first. The action then plays nothing and the editor says why. |
| `TriggerEffectHold` | `MacroTriggerEffectHold` | `UntilRelease` | `Duration` (for `TriggerEffectMs`), `UntilRelease` (until the macro's trigger is let go) or `UntilStopped` (until a Stop Adaptive Trigger Effect action). |
| `IsTriggerEffectTimed` | `bool` | - | Computed (`[XmlIgnore]`): `TriggerEffectHold == Duration`. Shows the time field. |
| `TriggerEffectMs` | `int` | `500` | The effect's length for `Duration`. Clamped to 1–60,000 ms. |

`MacroTriggerEffectSide` and `MacroTriggerEffectHold` live in `TriggerEffectCatalog.cs`. Both are saved by name and append-only.

---

### MacroAction: Type Gates

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `IsMouseWheelTapType` | `bool` | - | True when Type is MouseWheelTap (v15). |
| `IsMouseNudgeType` | `bool` | - | True when Type is MouseNudge (v16). |
| `IsCycleTapListType` | `bool` | - | True when Type is CycleTapList (v16). |
| `IsLightbarType` | `bool` | - | True when Type is LightbarColor (PlayStation slot RGB override). |
| `IsRumbleType` | `bool` | - | True when Type is Rumble. |
| `IsRumbleStopType` | `bool` | - | True when Type is RumbleStop. |
| `IsRumbleTriggerType` | `bool` | - | True when Type is RumbleTrigger (issue #102). |
| `IsRumbleTriggerStopType` | `bool` | - | True when Type is RumbleTriggerStop (issue #102). |
| `IsAnyRumbleSetType` | `bool` | - | True for either rumble-set action (main motors or trigger). Both share the strength / hold-mode / duration param editor. |
| `IsAnyRumbleStopType` | `bool` | - | True for either rumble-stop action (main motors or trigger). |
| `RumbleStopEditorBody` | `string` | - | What stopping the rumble does, under the Type row of a rumble-stop step (#102). |
| `IsPlaySoundType` | `bool` | - | Computed: `Type == PlaySound` (and `IsSoundStopType`: `SoundStop`). |
| `IsSoundStopType` | `bool` | - | See `IsPlaySoundType`. |
| `IsSetGyroEngagedType` | `bool` | - | True when Type is SetGyroEngaged. Surfaces the Mode dropdown editor in the macro action UI. |
| `IsMouseRecenterType` | `bool` | - | True when Type is MouseRecenter (issue #108). Surfaces the Cursor Recenter Mode dropdown in the macro action UI. |
| `IsMouseFixPositionType` | `bool` | - | True when Type is MouseFixPosition (issue #109). Surfaces the Cursor Pin Mode dropdown plus the Pin X / Pin Y spinboxes. |
| `IsMouseLimitRegionType` | `bool` | - | True when Type is MouseLimitRegion (issue #110). Surfaces the Cursor Clamp Mode dropdown plus the Inset X / Inset Y spinboxes. |
| `IsMoveMouseToScreenPositionType` | `bool` | - | True when Type is MoveMouseToScreenPosition (issue #9). Surfaces the Mouse X / Mouse Y spinboxes plus the "Pick on screen" capture button. |
| `IsRepeatKeyWhileHeldType` | `bool` | - | True when Type is RepeatKeyWhileHeld (issue #9). Surfaces the key picker (shared with Key Press) plus the Interval spinbox. |
| `IsRepeatVcButtonWhileHeldType` | `bool` | - | True when Type is RepeatVcButtonWhileHeld (issue #9 wave 1b). Surfaces the button-target grid (shared with Button Press) plus the Interval spinbox. |
| `IsToggleVcButtonType` | `bool` | - | True when Type is ToggleVcButton (issue #9 wave 1b). Surfaces the button-target grid (shared with Button Press). |
| `IsToggleKeyType` | `bool` | - | True when Type is ToggleKey (issue #9 wave 1b). Surfaces the key picker (shared with Key Press). |
| `IsGyroRecenterType` | `bool` | - | True when Type is GyroRecenter (issue #9 wave 1b, B-18). Gates the parameter-less info card in the macro editor. |
| `IsToggleMouseButtonType` | `bool` | - | True when Type is ToggleMouseButton (v19, M1). Surfaces the mouse-button picker (shared with Mouse Button Press) plus the pulse-while-latched row. |
| `IsToggleVcAxisType` | `bool` | - | True when Type is ToggleVcAxis (v19, M1). Surfaces the axis target / value pair (shared with Set Axis) plus the pulse-while-latched row. |
| `IsRepeatVcAxisWhileHeldType` | `bool` | - | True when Type is RepeatVcAxisWhileHeld (v19, M1). Surfaces the axis target / value pair plus the Interval spinbox. |
| `IsToggleWheelType` | `bool` | - | True when Type is ToggleWheel (v19, M1). Surfaces the wheel tick / horizontal pair (shared with Mouse Wheel Tick) plus the Interval spinbox. |
| `IsAxisAddType` | `bool` | - | True when Type is AxisAdd (discussion #237). Surfaces the signed-value hint under the shared axis target / value pair (the value box already accepts the full -32768..32767 range, so the relative add reuses it as is). |
| `IsAxisSetLatchedType` | `bool` | - | True when Type is AxisSetLatched (#251). Gates the ladder hint under the shared axis editor. |
| `IsAxisScaleType` | `bool` | - | True when Type is AxisScale (#251). Surfaces the signed-percent hint under the shared axis target / value pair: the value is the scale delta, -50% halves the current deflection, +50% amplifies half again. |
| `IsAxisLatchReleaseType` | `bool` | - | True when Type is AxisLatchRelease (#251). Surfaces the axis-target-only row (None reads as "all axes"). |
| `IsComboBreakType` | `bool` | - | True when Type is ComboBreak (discussion #237). Gates the parameter-less info card in the macro editor, the GyroRecenter card shape. |
| `IsAxisYieldCapableType` | `bool` | - | True for the axis holds that honor `AxisYieldToPhysical` (discussion #237): AxisHold, ToggleVcAxis, and RepeatVcAxisWhileHeld. Gates the yield checkbox row. |
| `IsAnyMouseButtonType` | `bool` | - | True when the mouse-button picker applies: MouseButtonPress / MouseButtonRelease plus the v18 ToggleMouseButton latch, which addresses its target through the same `MouseButton` knob (the IsAnyKeyType pattern applied to the mouse-button picker, v19 M1). |
| `IsAnyWheelTapType` | `bool` | - | True when the wheel tick / horizontal editor applies: MouseWheelTap plus the v18 ToggleWheel latch, both reading `AxisValue` as the signed tick count and `WheelHorizontal` as the lane (v19, M1). |
| `IsPulseCapableType` | `bool` | - | True for the latch actions whose held contribution can pulse on the turbo square wave (`PulseWhileLatched`): ToggleVcButton / ToggleKey plus the v18 ToggleMouseButton and ToggleVcAxis. Gates the pulse checkbox row (v19, M1). |
| `IsRunProgramType` | `bool` | - | True when Type is RunProgram (user request). Surfaces the program path / arguments / working-folder editor. |
| `IsTextBlockType` | `bool` | - | True when Type is TextBlock (#201). Gates the multiline text editor panel. |
| `IsRumbleReactiveHold` | `bool` | - | True when the Rumble action is in Reactive hold mode: drives visibility of the hold/fade sliders in the editor. |
| `IsRumbleStickyHold` | `bool` | - | True when the Rumble action is in Sticky hold mode. |
| `IsLightbarColorClearType` | `bool` | - | True when Type is LightbarColorClear. |
| `IsLightbarModeSetType` | `bool` | - | True when Type is LightbarModeSet. |
| `IsLightbarModeCycleType` | `bool` | - | True when Type is LightbarModeCycle. |
| `IsPointerModeCycleType` | `bool` | - | True when Type is PointerModeCycle (issue #203). |
| `IsSwitchLayerType` | `bool` | - | True when Type is SwitchLayer (#377). |
| `IsSetChromaColorType` | `bool` | - | True when Type is SetChromaColor (#468). Surfaces the color card. The hold rides the generic duration row. |
| `IsShowDreamcastScreenType` | `bool` | - | True when Type is ShowDreamcastScreen (#469). Surfaces the picture card. |
| `IsShowKeyboardScreenType` | `bool` | - | True when Type is ShowKeyboardScreen (#519). Surfaces the picture card. |
| `IsKeyboardScreenModeType` | `bool` | - | True when Type is KeyboardScreenMode (#519). |
| `IsStopwatchType` | `bool` | - | True when Type is Stopwatch (#519). |
| `IsPanKeyboardScreenType` | `bool` | - | True when Type is PanKeyboardScreen (#519). |
| `IsKeyboardScreenKindType` | `bool` | - | True for the two keyboard screen types that name a kind of screen (#519), which share the kind row. |
| `IsCrosshairTargetType` | `bool` | - | True when the action names a crosshair (#585). |
| `IsPointerModeSetType` | `bool` | - | True when Type is PointerModeSet (issue #203 follow-up). |
| `IsGuideLedBrightnessType` | `bool` | - | True when Type is GuideLedBrightness (discussion #209). |
| `IsAnyLightbarType` | `bool` | - | True when Type is any of the lightbar-related action types: drives the macro editor's grouping into a single CardBorder. |
| `IsLightbarReactiveHold` | `bool` | - | True when the LightbarColor action is in Reactive hold mode: drives the visibility of the ColorSource picker and Decay slider in the editor. |
| `IsLightbarStickyHold` | `bool` | - | True when the LightbarColor action is in Sticky hold mode. |
| `IsLightbarFixedColorVisible` | `bool` | - | True when the color picker should be visible: LightbarColor with ColorSource = Fixed (Reactive or Sticky). Random and Palette sources don't read the action's RGB so the picker is hidden in those cases. |

### MacroAction: Runtime Latches (not serialized)

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `CycleIndex` | `int` | - | CycleTapList runtime position (v16): index of the NEXT step to fire. Per-action volatile like the ToggleVcButton latch: lives with the loaded action, resets on profile switch and app restart, never persisted. |
| `CycleInjectionFired` | `bool` | - | Transient CycleTapList latch (v16): true once the current step's injection parts (key / mouse / wheel) have fired, cleared when the step completes. A latch instead of the executor's usual actionElapsed < 1 convention because a loaded frame can arrive later than 1 ms after the trigger stamp, which would silently swallow the one-shot parts. Never serialized. |
| `TextEmitCursor` | `int` (internal) | - | Runtime emission cursor for TextBlock pacing: how many UTF-16 code units of `TextContent` the current run has typed. The executor re-arms it to 0 when the action completes, and macro start resets it alongside the mouse accumulators, so an interrupted run can't resume mid-string. |
| `ComputeTextEmitTarget` | method (internal, static) | - | Pure pacing math for TextBlock emission: how many UTF-16 code units of `text` should have been typed once `elapsedMs` has passed. Delay 0 (or less) is the whole string at once. Otherwise code unit k emits when elapsed reaches k * delay, so the first character goes out on the action's first tick. Never splits a surrogate pair: a boundary landing between the halves pulls the low half forward into the same emission. |
| `RepeatKeyLastFireUtc` | `DateTime` (internal) | `DateTime.MinValue` | Transient timing state for `RepeatKeyWhileHeld`: the UTC time the last autofire pulse was sent. Reset to `MinValue` so the first held frame fires immediately. Never serialized. |
| `RepeatVcLastToggleUtc` | `DateTime` (internal) | `DateTime.MinValue` | Transient timing state for `RepeatVcButtonWhileHeld` (issue #9 wave 1b): the UTC time the pulse phase last flipped. MinValue makes the first held frame flip to ON immediately, mirroring `RepeatKeyLastFireUtc`. Reset on macro (re)start via InputManager.ResetMouseAccumulators. Never serialized. |
| `RepeatVcPulseOn` | `bool` (internal) | - | Current phase of the RepeatVcButtonWhileHeld square wave: true = the target button is written this half-period. Runtime state beside `RepeatVcLastToggleUtc`. Never serialized. |
| `VcToggleLatched` | `bool` (internal) | - | Volatile latch bit for `ToggleVcButton` (issue #9 wave 1b). While set, the engine ORs the action's target button(s) into the slot's combined output every frame. Cleared when the owning macro is disabled. Fresh instances (profile switch / app restart) start unlatched. Never serialized. |
| `KeyToggleLatched` | `bool` (internal) | - | Volatile latch bit for `ToggleKey` (issue #9 wave 1b). While set, the engine's per-frame key reconcile holds every parsed key logically down. Clearing it (second fire, macro disable, or instance discard) releases the key on the next tick. Never serialized. |
| `MouseToggleLatched` | `bool` (internal) | - | Volatile latch bit for `ToggleMouseButton` (v18). While set, the engine's per-frame mouse-button reconcile holds `MouseButton` logically down. Never serialized. |
| `VcAxisToggleLatched` | `bool` (internal) | - | Volatile latch bit for `ToggleVcAxis` (v18). While set, the engine re-writes the axis assert every frame. Never serialized. |
| `WheelToggleLatched` | `bool` (internal) | - | Volatile latch bit for `ToggleWheel` (v18). While set, the engine sends one wheel detent per interval. Never serialized. |
| `ClearVolatileLatches` | method (internal) | - | Drops every volatile Toggle latch this action holds. Called where an action stops owning its current output: the macro being disabled, and the action being retyped. The bits are runtime-only and a fresh instance starts unlatched, so this is a no-op on load and on copy. |
| `TurboPhase` | `double` (internal) | - | Pressure-turbo phase accumulator (#290): cycles advanced at the pressure-scaled rate. The square-wave family toggles each 0.5, the one-shot family fires each 1.0. Runtime state, never serialized. |
| `TurboLastTickUtc` | `DateTime` (internal) | `DateTime.MinValue` | UTC stamp of the last pressure-turbo accumulator tick, giving the dt the rate integrates over. MinValue marks a fresh activation, which fires/flips ON immediately, mirroring the legacy `RepeatVcLastToggleUtc` contract. Never serialized. |
| `LightbarCycleIndex` | `int` | - | Per-action volatile cycle position. Resets on action edit and on app restart. |
| `PointerCycleIndex` | `int` | - | Per-action volatile cycle position for PointerModeCycle. Resets on action edit and on app restart. |

### MacroAction: Source Recording and Mouse Pick

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `IsRecordingSource` | `bool` | - | True while a record session is capturing the next axis deflection into `SourceDeviceGuid` + `SourceDeviceAxisIndex`. Set by InputService.StartMacroActionAxisRecording / Stop. |
| `SourceRecordIcon` | `string` | - | The source record button's glyph and tooltip, which swap while `IsRecordingSource`. |
| `SourceRecordTooltip` | `string` | - | See `SourceRecordIcon`. |
| `RecordSourceCommand` | `RelayCommand` | - | Toggles a device-axis record session (the MacroExpressionVariable.RecordCommand pattern): the host wires `RecordSourceRequested` to InputService.StartMacroActionAxisRecording / Stop. |
| `ClearSourceCommand` | `RelayCommand` | - | Clears the device-axis source pair so the pickers read empty again. |
| `RecordSourceRequested` | `EventHandler` | - | Raised when the user toggles the source Record button. |
| `IsPickingMousePosition` | `bool` | - | True while a MoveMouseToScreenPosition "Pick on screen" capture countdown is running (issue #9). |
| `MousePickButtonText` | `string` | - | Label for the "Pick on screen" button: the live countdown while capturing, the idle prompt otherwise (issue #9). |
| `PickMousePositionCommand` | `RelayCommand` | - | Starts a 3-second "pick on screen" countdown (issue #9). When it elapses, the current desktop cursor position is captured into `MouseX` / `MouseY`. The delay lets the user move the cursor onto the target after clicking the button. |

### MacroAction: Cycle and Lightbar

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ResetLightbarCycleModesCommand` | `RelayCommand` | - | Resets lightbar cycle modes to its default. |
| `ResetPointerCycleModesCommand` | `RelayCommand` | - | Resets pointer cycle modes to its default. |
| `CycleModeOptions` | `IReadOnlyList<LightbarModeCycleOption>` | - | Checkbox-bindable list of every selectable LightbarMode value for the LightbarModeCycle action's editor. Toggling any option's IsChecked rewrites `LightbarCycleModesCsv`: the CSV is the canonical storage. The option list is a UI-side projection. Each option's `Label` is a live getter that resolves the localized mode name on access, so a culture change reflows the labels without rebuilding the list. |
| `WriteCycleCsv` | method (internal) | - | Sets the cycle CSV from an enumerable of selected modes. Sorts by enum value for stable ordering. |
| `CycleStepsCsv` | `string` | `""` | For CycleTapList (v16): the ordered step list. Steps separated by ','. Parts of one step joined '+' (they fire together). Part = kind ':' value. Kinds: K:{vk} key tap, M:{0..4} mouse-button click, W:{ticks} vertical wheel, H:{ticks} horizontal wheel, B:{mask} VC button flags, A:{axisTarget}:{value} VC axis assert (MacroAxisTarget ordinal, trigger and button pressure targets on the AxisHold pull scale). Example: "K:49,K:50,W:1+M:0". |
| `CycleWrap` | `bool` | `true` | For CycleTapList (v16): wrap past the last step back to the first. Off = further fires produce nothing once the end is reached (Steam's Wrap List - Off). |
| `ParsedCycleSteps` | `CycleStepPart[][]` | - | Parses `CycleStepsCsv` into step parts, memoized against the CSV (the executor reads this per fire on the poll thread). Unparseable parts are dropped, and a step whose parts all drop is dropped whole. |
| `LightbarHoldMode` | `MacroLightbarHoldMode` | `MacroLightbarHoldMode.Reactive` | Reactive (default, decay-fade) or Sticky (held until a `LightbarColorClear` runs). |
| `LightbarColorSource` | `MacroLightbarColorSource` | `MacroLightbarColorSource.Fixed` | For Reactive holds: Fixed RGB (the action's color), RandomHue (rolled per fire), or PaletteStep (advance through the slot's `LightbarPalette`). Ignored for Sticky holds (always Fixed). |
| `LightbarHoldMs` | `int` | `0` | Hold window for Reactive holds (ms). The override stays at full intensity for this many ms before the fade begins. 0 means start fading immediately. Clamped 0..5000. |
| `LightbarFadeMs` | `int` | `600` | Fade window for Reactive holds (ms). After the hold period elapses, the override linearly fades to 0 over this duration. 0 means cut directly to off after the hold. Clamped 0..5000. |
| `LightbarPaletteCsv` | `string` | `string.Empty` | CSV of "R,G,B" hex triplets defining the per-macro palette for `PaletteStep`. Empty falls back to the slot's own `LightbarPalette`. |
| `LightbarPalette` | `ObservableCollection<LightbarPaletteEntry>` | - | Parsed view of `LightbarPaletteCsv` as a list of LightbarPaletteEntry rows. The macro editor binds an ItemsControl to this and writes back via the helper commands. |
| `IsLightbarPaletteVisible` | `bool` | - | True when the palette editor should be visible: LightbarColor + Reactive + ColorSource = PaletteStep. |
| `AddLightbarPaletteColorCommand` | `RelayCommand` | - | Adds an entry to `LightbarPalette`, and `RemoveLightbarPaletteColorCommand` removes the entry passed as its parameter. |
| `RemoveLightbarPaletteColorCommand` | `RelayCommand<LightbarPaletteEntry>` | - | See `AddLightbarPaletteColorCommand`. |
| `LightbarTargetMode` | `LightbarMode` | `LightbarMode.Static` | Target `LightbarMode` for `LightbarModeSet`. |
| `LightbarCycleModesCsv` | `string` | `"1,2,3,4,11,12,13"` | CSV of `LightbarMode` int values to cycle through. Each fire advances to the next listed mode. Editor surfaces this as a 13-item checkbox grid. |
| `PointerCycleModesCsv` | `string` | `"Mouse,FpsMouse,Mouse43,Mouse169"` | CSV of `PadSetting.PointerMode` names to cycle through. Each fire advances to the next listed mode. Editor surfaces this as a four-item checkbox row. |
| `ParsedPointerCycleModes` | method | - | Parses `PointerCycleModesCsv` into the recognized mode names, preserving CSV order. |
| `CountSelectedPointerCycleModes` | method (internal) | - | Counts the pointer modes the cycle list holds, and `WritePointerCycleCsv` writes the list back to `PointerCycleModesCsv`. |
| `WritePointerCycleCsv` | method (internal) | - | See `CountSelectedPointerCycleModes`. |
| `PointerCycleModeOptions` | `IReadOnlyList<PointerModeCycleOption>` | - | Checkbox-bindable projection of the four pointer modes for the PointerModeCycle editor, mirroring `CycleModeOptions`: the CSV is canonical, labels resolve live for culture changes. |
| `CountSelectedCycleModes` | method | - | Counts the modes selected in `LightbarCycleModesCsv`. Used for the cycle action's display string. |
| `ParsedCycleModes` | method | - | Parses `LightbarCycleModesCsv` into an array of `LightbarMode` values (skipping invalid tokens). Empty array if the CSV is empty or unparseable. |
| `LightbarModeDisplayName` | method (internal, static) | - | A lightbar mode's name in the language. |

### MacroAction: Pointer, Layer, Gyro and Guide LED

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `SetGyroEngagedMode` | `MacroSetGyroEngagedMode` | `MacroSetGyroEngagedMode.Toggle` | Write mode for `SetGyroEngaged`. `Toggle` flips the per-slot macro-engaged bit. `On` forces it true. `Off` forces it false. OR-combined with the dedicated engage button's bit at the gyro evaluator. |
| `SwitchLayerMask` | `string` | `"Base"` | The layer mask SwitchLayer engages. |
| `PointerSetMode` | `string` | `"Mouse"` | The `PadSetting.PointerMode` name PointerModeSet applies. Unknown names normalize to Mouse at execution. |
| `NormalizedPointerSetMode` | method (internal) | - | Resolves `PointerSetMode` to a recognized mode name, defaulting to Mouse for anything unknown, so a hand- edited XML value can never write garbage into PadSetting. |
| `GuideLedPercent` | `int` | `100` | The brightness percent (0-100) the GuideLedBrightness action applies. 0 turns the LED off. Clamped to 0 to 100. |
| `PointerModeDisplayName` | method (internal, static) | - | Localized display name for a PointerMode value, shared by the Pointer group's combo and the cycle checkboxes. |

### MacroAction: Rumble

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `RumbleHoldMode` | `MacroRumbleHoldMode` | `MacroRumbleHoldMode.Reactive` | Reactive (decay-fade pulse) or Sticky (held until a `RumbleStop` runs). |
| `RumbleStrengthLeft` | `int` | `100` | Left (heavy / low-frequency) motor strength as a percentage 0..100 of the device's full output. Combined with the Force Feedback group's per-motor gain at injection time. Clamped to 0 to 100. |
| `RumbleStrengthRight` | `int` | `100` | Right (light / high-frequency) motor strength as a percentage 0..100. Set 0 with `RumbleStrengthLeft` > 0 (or vice versa) to fire one motor in isolation. Clamped to 0 to 100. |
| `RumbleHoldMs` | `int` | `100` | Full-strength hold window for Reactive rumble (ms). Default 100: short enough that a button tap feels punchy without bleeding into the next press. Clamped 0..5000. |
| `RumbleFadeMs` | `int` | `200` | Fade-out window for Reactive rumble (ms). After `RumbleHoldMs` elapses, both motors ramp linearly to 0 over this duration. 0 means cut directly to off. Clamped 0..5000. |

### MacroAction: Trigger Effects

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ResetTriggerEffectValues` | method (internal) | - | Puts the effect's own starting values back, whatever the effect, and refreshes every row. |
| `TriggerEffectValue` | method (internal) | - | Reads one parameter of the action's trigger effect by index, 0 past the list, and `SetTriggerEffectValue(index, value)` writes one. |
| `SetTriggerEffectValue` | method (internal) | - | See `TriggerEffectValue`. |
| `TriggerEffectValues` | `int[]` (internal) | - | The values as the encoder takes them. |
| `TriggerEffectSideName` | method (internal, static) | - | A trigger side's name in the language. |

### MacroAction: Sound, Program and Text

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `SoundFilePath` | `string` | `string.Empty` | Absolute path of the sound file to play. Decoded via Media Foundation (wav / mp3 / m4a / aac / wma / flac) and cached after first use so repeat fires start instantly. |
| `SoundFileName` | `string` | - | File name only, for compact display on the action row and the Audio group's sound-macro list. Package references render as "entry: package". |
| `SoundVolume` | `int` | `100` | Per-action volume percentage 0-100, multiplied with the slot's master sound volume (Audio group). Clamped to 0 to 100. |
| `SoundLoop` | `bool` | - | Loop until a SoundStop action (or, for While-Held / Until-Release macros, the trigger's release). Off = play once. |
| `ProgramPath` | `string` | `""` | Path to the program or file to launch. ShellExecute, so a document or URL with a file association works too. |
| `ProgramArgs` | `string` | `""` | Command-line arguments passed to the program (one string). |
| `ProgramWorkingDir` | `string` | `""` | Working folder for the launched program. Empty leaves it to the shell default. |
| `TextContent` | `string` | `""` | The plain text a TextBlock action types out. There is no token grammar (Key Press owns combos). Newlines press Enter, tabs press Tab. The setter normalizes line endings to LF and strips the control characters the settings XML cannot carry, so the stored value round-trips byte-identically on every persistence leg. |
| `SanitizeTextContent` | method (internal, static) | - | Normalizes a Text Block's content for storage: CRLF and lone CR become LF, and C0 control characters other than tab and LF are stripped. Two forcing facts, both verified against XmlSerializer: a C0 character (e.g. ESC pasted from ANSI-colored terminal text) makes the WHOLE settings save throw on every autosave until removed, and a CR survives the save but the XML parser normalizes it to LF on load, so persisting CR would leave the XML and clipboard-JSON legs byte-divergent. The emitter treats \n, \r, and \r\n as one Enter each, so normalizing here changes no typed output and keeps per-character pacing one-slot-per-Enter. |
| `TextPerCharDelayMs` | `int` | - | Milliseconds between typed characters. 0 (default) emits the whole text as one batched SendInput call. Clamped to 0 to 1000. |

### MacroAction: Screens and Crosshairs

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `DreamcastFrameImages` | `IReadOnlyList<ImageSource>` | - | The pictures as the VMU shows them, for the editor. |
| `DreamcastFrameCount` | `int` | - | How many frames the action holds, and whether another can be added. |
| `CanAddDreamcastFrame` | `bool` | - | See `DreamcastFrameCount`. |
| `AddDreamcastFrame` | method (internal) | - | Appends a picture, while fewer than eight are set. |
| `RemoveDreamcastFrame` | method (internal) | - | Removes the picture at `index`. |
| `CrosshairNumber` | `int` | - | The crosshair Toggle Crosshair shows or hides (#585): its number, or 0 for every crosshair. A macro on any slot reaches it. Clamped to 0 to MaxCrosshairs. |
| `CrosshairChoices` | `IReadOnlyList<CrosshairChoice>` | - | The editor's list of crosshairs, by number. |
| `ScreenFrameImages` | `IReadOnlyList<ImageSource>` | - | The pictures as the screen shows them, for the editor. |
| `ScreenFrameCount` | `int` | - | How many frames the action holds, and whether another can be added. |
| `CanAddScreenFrame` | `bool` | - | See `ScreenFrameCount`. |
| `AddScreenFrame` | method (internal) | - | Appends a picture, a PNG in base64, while fewer than eight are set. |
| `RemoveScreenFrame` | method (internal) | - | Removes the picture at `index` in the editor's list. The editor lists only the entries that hold a picture (`ScreenFrameImages`), so the index counts those, and an entry that holds none goes too: it shows nowhere and plays nowhere. |
| `ScreenModeIndex` | `int` | - | The mode as the editor's list index, the modes' own order. |
| `StopwatchActionIndex` | `int` | - | The stopwatch action's picker index over `StopwatchAction`. |
| `PanDirectionIndex` | `int` | - | The pan direction's picker index over `PanDirection`. |
| `DefaultPanStep` | `int` (const) | - | 16: the pan step, in the picture's pixels, a new action takes. |

### MacroAction: Mouse and Cursor

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `CursorRecenterMode` | `CursorRecenterMode` | `CursorRecenterMode.XAndY` | Which axes a `MouseRecenter` action snaps to the primary-monitor center (issue #108). |
| `CursorPinMode` | `CursorPinMode` | `CursorPinMode.XAndY` | Which axes a `MouseFixPosition` action pins while engaged (issue #109). The other axis stays free. |
| `CursorPinX` | `int` | - | Target X coordinate (primary-monitor physical pixels) a pin action holds while engaged (issue #109). Defaults to the monitor center on first type switch. Clamped to the primary monitor's width. |
| `CursorPinY` | `int` | - | Target Y coordinate (primary-monitor physical pixels) a pin action holds while engaged (issue #109). Defaults to the monitor center on first type switch. Clamped to the primary monitor's height. |
| `MouseX` | `int` | - | Target X coordinate (primary-monitor physical pixels) a `MoveMouseToScreenPosition` action warps the cursor to on press (issue #9). Seeded to the primary-monitor center on first type switch and pickable on screen. Clamped to the primary monitor's width, mirroring `CursorPinX`. |
| `MouseY` | `int` | - | Target Y coordinate (primary-monitor physical pixels) a `MoveMouseToScreenPosition` action warps the cursor to on press (issue #9). Seeded to the primary-monitor center on first type switch and pickable on screen. Clamped to the primary monitor's height, mirroring `CursorPinY`. |
| `NudgeDx` | `int` | - | Signed X pixel delta a `MouseNudge` action moves the cursor by per fire (v16). Screen frame: positive = right. Deliberately NOT the clamped `MouseX` warp coordinate: a nudge is a relative offset and negative values are the point. |
| `NudgeDy` | `int` | - | Signed Y pixel delta for `MouseNudge` (v16). Screen frame: positive = down (the SendInput MOUSEEVENTF_MOVE convention). |
| `CursorClampMode` | `CursorClampMode` | `CursorClampMode.XAndY` | Which axes a `MouseLimitRegion` action clamps inside the inset region while engaged (issue #110). |
| `CursorClampInsetX` | `int` | `50` | Pixels held back from each left/right edge for a region clamp (issue #110). The cursor is kept inside [inset, width - inset] on X. Clamped to 0..half the primary monitor's width. |
| `CursorClampInsetY` | `int` | `50` | Pixels held back from each top/bottom edge for a region clamp (issue #110). The cursor is kept inside [inset, height - inset] on Y. Clamped to 0..half the primary monitor's height. |
| `ResetCursorClampInsetXCommand` | `RelayCommand` | - | Resets the region-clamp X inset to the 50 px default (#110). |
| `ResetCursorClampInsetYCommand` | `RelayCommand` | - | Resets the region-clamp Y inset to the 50 px default (#110). |

### MacroAction: Axis and Wheel

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `AxisValuePercent` | `double` | - | The editor-facing form of `AxisValue`: a signed percent of full deflection (-100..100), the unit every summary and tooltip already speaks. The raw -32768..32767 field stays the persisted truth, so profiles and the clipboard are untouched. Typing 75 means 75% of full scale, which is what a human means by 75 (the raw box demanded 24575 for the same thing, which nobody could know). Clamped to -100.0 to 100.0. |
| `WheelHorizontal` | `bool` | - | For MouseWheelTap (v15): tick the horizontal (MOUSEEVENTF_HWHEEL) lane instead of the vertical wheel. |
| `AxisYieldToPhysical` | `bool` | - | Yield-to-physical for the absolute axis holds (discussion #237, reWASD's "Absolute deflection" contract: "once you move your physical stick, the combo will go back to zero, and now your stick will have a higher priority"). While set on an `AxisHold`, `ToggleVcAxis`, or `RepeatVcAxisWhileHeld` action, the engine checks the target's already-mapped value each frame BEFORE overwriting: the first frame the physical input exceeds the yield threshold, the macro write is suppressed and STAYS suppressed for the remainder of that activation (latched, matching reWASD's "goes back to zero"), re-arming when the action re-fires. Off by default so existing macros keep their macro-wins semantics. |
| `LatchDirection` | `MacroLatchDirection` | - | How a ToggleKey / ToggleMouseButton / ToggleVcButton fire writes the volatile latch (audit #2 M4, #561): Toggle flips (the classic behavior and the serialized default), On sets, Off clears. The Workshop materializer lowers HoldKey / HoldMouseButton pairs to On on the press leg and Off on the release leg, so the held key rides the per-frame reconcile and its engine-stop / profile-switch release paths instead of a raw KeyPress Down those paths cannot see. Serialized. |

### MacroAction: Keys

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `VirtualKeyChoices` | `List<KeyDisplayItem>` | - | Instance accessor over `VirtualKeyValues`. x:Static ItemsSource bindings evaluate once and kept the old language after a live switch (owner report 2026-07-16). |
| `RefreshVirtualKeyValues` | method (internal, static) | - | Rebuilds the virtual-key picker's entries. |
| `VirtualKeyDisplayName` | method (internal, static) | - | Returns a user-friendly localized display name for a virtual key. Internal: MappingDisplayResolver reuses this vocabulary for keyboard-device keys the engine's invariant table leaves as "Key 0xNN" hex. |

### MacroAction: Resets and Other

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ResetButtonSelectionCommand` | `RelayCommand` | - | Resets button selection to its default. |
| `ResetSettingCommand` | `RelayCommand<string>` | - | Resets setting to its default. |
| `CanResetSetting` | method (internal, static) | - | The names `ResetSettingCommand` accepts on this class. |
| `RawProfileId` | `string` | - | The Extended slot's HIDMaestro profile slug, cascaded from the owning MacroItem (#215). Re-letters the Numbered button labels on Switch Pro profiles. Display-only. |

### Supporting Enums (MacroItem.cs)

**MacroTriggerMode** (ordinals pinned): `OnPress` (0), `OnRelease` (1), `WhileHeld` (2), `Always` (3), `CustomExpression` (4, v3.2), `HoldForMs` (5, On Long Press), `DoublePress` (6), `TriplePress` (7), `SinglePress` (8, deferred single), `Toggle` (9), `Turbo` (10), `ShortPress` (11, On Short Press, #253. Shares `TriggerHoldMs` with `HoldForMs` to compose tap-vs-hold on one button)

**MacroTriggerSource:** `InputDevice`, `OutputController`, `GameTelemetry` (#531). The last one is offered for Custom Expression variables alone, which then read a game's telemetry in its own units. Appended, since the clipboard writes this enum as a number.

**MacroRepeatMode:** `Once`, `FixedCount`, `UntilRelease`, `UntilNextPress` (appended in 5.3.0, #561)

**MacroActionType** (append-only, since the clipboard serializes these as ints, so members are never reordered): `ButtonPress`, `ButtonRelease`, `KeyPress`, `KeyRelease`, `Delay`, `AxisSet`, `SystemVolume`, `AppVolume`, `MouseMove`, `MouseButtonPress`, `MouseButtonRelease`, `MouseScroll`, `ToggleTouchpadOverlay` (v3.2), `LightbarColor` / `LightbarColorClear` / `LightbarModeSet` / `LightbarModeCycle` (v3.1+), `SetGyroEngaged` (#120), `Rumble` / `RumbleStop` (v3.1+), `RumbleTrigger` / `RumbleTriggerStop` (#102), `PlaySound` / `SoundStop` (#83), `MouseRecenter` (#108), `MouseFixPosition` (#109), `MouseLimitRegion` (#110), `DisconnectController` (#162), `RunProgram` (launch an external program/file), `TextBlock` (#201, Unicode text injection), `PointerModeCycle` / `PointerModeSet` (#203, Wii pointer mode), `GuideLedBrightness` (#209), `MoveMouseToScreenPosition` (33, #9), `RepeatKeyWhileHeld` (34), `RepeatVcButtonWhileHeld` (35), `ToggleVcButton` (36), `ToggleKey` (37), `GyroRecenter` (38), `AxisHold` (39), `MouseWheelTap` (40), `MouseNudge` (41), `CycleTapList` (42), `ToggleMouseButton` (43), `ToggleVcAxis` (44), `RepeatVcAxisWhileHeld` (45), `ToggleWheel` (46), `AxisAdd` (47, #237), `ComboBreak` (48, #237), `AxisSetLatched` (49, #251), `AxisLatchRelease` (50, #251), `AxisScale` (51, #251), `HeadphoneVolumeUp` (52), `HeadphoneVolumeDown` (53), `VoiceListenWhileHeld` (54, #317), `SwitchLayer` (55, #377), `SetChromaColor` (56, #468), `ShowDreamcastScreen` (57, #469), `ShowKeyboardScreen` (58, #519), `KeyboardScreenMode` (59, #519), `Stopwatch` (60, #519), `PanKeyboardScreen` (61, #519), `TriggerEffect` (62, #531), `TriggerEffectStop` (63, #531), `SetKeyColors` (64, #557), `ClearKeyColors` (65, #557), `ToggleScreenOverlay` (66, #560), `ProfileShortcut` (67, #561), `ToggleCrosshair` (68, #585: a crosshair, or every crosshair when it names none), `ToggleMagnifier` (69, #585) and `MagnifierWhileHeld` (70, #585: shows the magnifier while the macro's input is held, for aiming down sights). `TriggerEffect` plays a DSX trigger mode on the slot's DualSense triggers, and `TriggerEffectStop` ends one (see [Adaptive Trigger Effect Properties](#adaptive-trigger-effect-properties-531)). The volume pair steps `DeviceSlotConfig.HeadphoneVolume` by 10% and clamps at the ends, persisting like any other Audio group edit. `SwitchLayer` is one-shot: it writes the shift runtime's `CustomLayer` override under the Latch activator's own lock-and-version discipline, so the layer stays engaged until another switch, a Latch or Cycle transition, or a profile switch. Its parameter is `MacroAction.SwitchLayerMask` (default `"Base"`) and its gate is `IsSwitchLayerType`. `SetChromaColor` has the `AxisHold` duration shape: Step 4b asserts its color (`LightbarR`, `LightbarG`, `LightbarB`) for the macro's slot on every frame the action is current, through `PeripheralOutputs.AssertChromaMacro` (#494). The Chroma worker paints the categories of the Razer devices assigned to that slot, every category when the Razer Chroma row is, over every Lighting group, and lets go within 120 ms of the action ending. Two macros current in one frame resolve to the last one evaluated. Its gate is `IsSetChromaColorType`. The append-only rule is stated in code beside the enum.

The editor's type picker is grouped, not a flat list of these members. See `MacroTypeCatalog` under [PadViewModel's Macros section](#macros).

**MacroDisconnectTarget** (#162): `TriggeringDevice` (0), `SpecificDevice` (1), `SlotDevices` (2), `AllDevices` (3). Picks the disconnect victim: the trigger's device(s), one picked device, every Bluetooth device on the pad's slot, or every Bluetooth device PadForge knows.

**MacroLightbarHoldMode:** `Reactive`, `Sticky` (v3.1)

**MacroLightbarColorSource:** `Fixed`, `RandomHue`, `PaletteStep` (v3.1)

**MacroRumbleHoldMode:** `Reactive`, `Sticky` (v3.1)

**MacroMouseButton:** `Left`, `Right`, `Middle`, `X1`, `X2`

**MacroAxisTarget:** `None`, `LeftStickX`, `LeftStickY`, `RightStickX`, `RightStickY`, `LeftTrigger`, `RightTrigger`, then the virtual DualShock 3's ten button pressures (#530, values 7 to 16, in `ButtonPressureState` order): `PressureButtonA`, `PressureButtonB`, `PressureButtonX`, `PressureButtonY`, `PressureLeftShoulder`, `PressureRightShoulder`, `PressureDPadUp`, `PressureDPadDown`, `PressureDPadLeft`, `PressureDPadRight`. Append-only. `MacroAxisTargetNames.PressureIndex` gives a target's pressure index or -1, and `DisplayName` gives a pressure target the pressure mapping row's label (`PressureName`). `MacroPressureLabels.Instance` serves the same labels to the axis pickers, raised again on a language change.

**MacroAxisDirection:** `Any`, `Positive`, `Negative`

**MacroAxisSource:** `OutputController`, `InputDevice`

**MacroButtonStyle:** `Xbox360`, `DualShock4`, `Numbered`, `DualShock3` (the DualShock 4 lettering with Select and Start on Back and Start, and no Touchpad button)

### MacroExpressionVariable

**File:** `MacroItem.cs`

One variable of a Custom Expression trigger (`MacroItem.TriggerExpressionVariables`), read as a letter in the formula. It binds a device's raw button, POV direction or axis (`Source` `InputDevice`), a virtual controller output (`OutputController`, `OutputChannel`), or a game's telemetry (`GameTelemetry`, #531).

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ResetSettingCommand` | `RelayCommand<string>` | - | Resets setting to its default. |
| `CanResetSetting` | method (internal, static) | - | The names `ResetSettingCommand` accepts on this class. |
| `Source` | `MacroTriggerSource` | `MacroTriggerSource.InputDevice` |  |
| `TelemetryChannel` | `TelemetryChannel` | - | The telemetry channel read when Source is GameTelemetry (issue #531). |
| `TelemetryVariable` | `string` | `string.Empty` | The custom variable's name when the channel is Variable. |
| `TelemetryOption` | `TelemetryChannelOption` | - | The picker's selection: the channel and the variable's name as one entry of `Items`. |
| `DeviceGuid` | `Guid` | - |  |
| `RawButton` | `int` | `-1` | Raw device button index (0-based) when Source=InputDevice. -1 when not used. |
| `Pov` | `string` | - | "povIndex:centidegrees" form when Source=InputDevice and the variable samples a POV direction. Null when not used. |
| `AxisTarget` | `MacroAxisTarget` | `MacroAxisTarget.None` |  |
| `OutputChannel` | `MacroOutputChannel` | `MacroOutputChannel.None` |  |
| `IsBound` | `bool` | - | True if this variable has a usable binding (one of raw-button / POV / axis / output-channel populated). An unbound variable evaluates to 0. |
| `Spec` | `string` | - | Compact tagged form used for XML round-tripping. "in:GUID:btn:N", "in:GUID:pov:idx:cd", "in:GUID:ax:Target", "out:Channel", "tel:Channel", "tel:var:Name" (issue #531). Empty for unbound. A variable's name never holds ':' or '\|', which the custom format editor refuses. |
| `DisplaySummary` | `string` | - | Short human-readable summary for the variable row UI. Resolves device-aware names (e.g. real button label "X" instead of "Button 13") when the device is online. |
| `IsRecording` | `bool` | - | Whether the recorder listens for this input. Drives the record button's icon and tooltip. |
| `LiveText` | `string` | `""` | Live in-progress feedback shown while a record session is running for this variable (e.g. "Press any input…"). |
| `RecordIcon` | `string` | - |  |
| `RecordTooltip` | `string` | - |  |
| `RecordCommand` | `RelayCommand` | - | Runs the matching `Fire…Record` method. |
| `ClearBindingCommand` | `RelayCommand` | - |  |
| `RecordRequested` | `EventHandler` | - | Raised when the user toggles the per-row Record button. The host wires this to `StartExpressionVariableRecording` / Stop, similar to the macro trigger flow. |

### MacroTriggerInputItem

**File:** `MacroItem.cs`

One row of a macro's trigger input list (`MacroItem.TriggerInputItems`).

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `Label` | `string` | - |  |
| `RemoveCommand` | `ICommand` | - |  |
| `AxisEntry` | `MacroItem.TriggerInputEntry` | - | The underlying axis entry when this row is a per-device axis input, else null. Drives the inline axis controls. |
| `IsAxis` | `bool` | - | True when this row carries an axis input and should show the Invert / Half / Either / Deadzone controls. |
| `ThresholdEntry` | `MacroItem.TriggerInputEntry` | - | The underlying descriptor entry when its read takes a threshold (an analog key, a stick ring, a Ring-Con squeeze), else null. Drives the inline Deadzone control (#468). |
| `HasThreshold` | `bool` | - | True when this row should show the Deadzone control. |

### MacroOutputChannel, MacroOutputChannelNames and MacroOutputChannelOption

**File:** `MacroItem.cs`

`MacroOutputChannel` names a virtual controller output a macro or a variable reads: `None`, the buttons `A`, `B`, `X`, `Y`, `LB`, `RB`, `LS`, `RS`, `Back`, `Start`, `Guide`, `DpadUp`, `DpadDown`, `DpadLeft`, `DpadRight`, the triggers `LT`, `RT`, and the axes `LX`, `LY`, `RX`, `RY`. The static `MacroOutputChannelNames.DisplayName(channel, style, profileId)` names one in the slot's lettering (the profile id re-letters Numbered labels on Switch Pro profiles, #215), and `GetOptions(style, profileId)` builds the picker's list in presentation order (face, shoulders, start/back/guide, sticks, D-pad, triggers, axes). `MacroOutputChannelOption` is one picker entry: `Value`, `Name`.

### Smaller Macro Enums and Helpers

**File:** `MacroItem.cs`

**MacroLatchDirection:** `Toggle` (each fire flips the latch), `On`, `Off`. On a hold-pair leg (`PairId` nonzero) the clear also reaches the twin's latches.

**MacroSetGyroEngagedMode:** `Toggle`, `On`, `Off`, over the slot's macro-engaged gyro bit.

**CursorClampMode**, **CursorPinMode**, **CursorRecenterMode:** `XOnly`, `YOnly`, `XAndY`, which coordinates the cursor action clamps, pins or snaps to center.

`CycleStepPart` is one parsed step of a cycle list: `Kind` (a char), `Value`, `Value2`, and the static `TryParse` over the `"K:49"`, `"B:4096"`, `"A:2:32767"` forms. Unknown kinds and junk numbers fail rather than guess.

`LightbarModeCycleOption` (`Mode`, `Label`, `IsChecked`) and `PointerModeCycleOption` (`ModeName`, `Label`, `IsChecked`) are the checkable entries of the lightbar-mode and pointer-mode cycle lists. `Label` reads the language on each access, and the internal `RefreshCheckedState()` re-raises `IsChecked`.

`TriggerEffectParameter` (`TriggerEffectCatalog.cs`) is one parameter of a trigger effect: `Label`, `Min`, `Max`, `Default`.

---

### GamepadButtonOption

**File:** `MacroItem.cs`

Checkbox for a single gamepad button. Reads/writes bits from the parent `MacroAction`'s `ButtonFlags` (or `CustomButtonWords` for Extended slots).

| Property | Type | Description |
|----------|------|-------------|
| `Label` | `string` | Button display name. |
| `Flag` | `ushort` | Xbox/PlayStation bitmask flag (0 for custom). |
| `CustomIndex` | `int` | Extended button index (0-based). −1 = use Flag. |
| `IsChecked` | `bool` | Button selected. Reads/writes parent's flags. |

| Method | Description |
|--------|-------------|
| `Refresh()` | Re-evaluates `IsChecked` after external state change. |

### KeyDisplayItem

**File:** `MacroItem.cs`

Wraps a `VirtualKey` with a localized display name for ComboBox binding.

| Property | Type | Description |
|----------|------|-------------|
| `Key` | `VirtualKey` | The virtual key value. |
| `DisplayName` | `string` | Localized display name. |

### MacroDisconnectDeviceOption

**File:** `MacroItem.cs`

One row in the `DisconnectController` action's Specific-device picker (#162): a known Bluetooth-pathed device by GUID and display name.

| Property | Type | Description |
|----------|------|-------------|
| `Guid` | `Guid` | Device instance GUID. |
| `Name` | `string` | Resolved device name. |

---

## MenuEditorItem

**File:** `MenuEditorItem.cs`

Editor VM for one radial / touch menu (#9), backing a row of `PadViewModel.Menus`. Wraps the LIVE `MenuDefinitionEntry` stored on the slot's `MappingSet` (write-through, like the mapping grid edits its live rows). Every mutation raises `Changed`, which `PadViewModel` forwards to `ConfigItemDirtyCallback` so the settings go dirty. Cells materialize lazily: the editor shows every cell position for the current shape, and a cell's entry exists in `MenuDefinitionEntry.Items` only once it carries a label or a binding.

### Slot Context

Set on every row by `PadViewModel.ApplyMenuButtonStyle`. The five providers and the two callbacks are internal delegates, not bound properties.

| Member | Type | Description |
|--------|------|-------------|
| `ButtonStyle` | `MacroButtonStyle` | Button lettering, derived from the slot's output type and, on a PlayStation slot, its preset. Same derivation the macro editor uses. |
| `RawButtonCount` | `int` | Raw button count for Extended and Nintendo slots, from `ExtendedConfig.ButtonCount`. Defaults to 11. |
| `RawProfileId` | `string` | The slot's HIDMaestro profile slug, so lettered wires label their buttons correctly. |
| `SupportsControllerButtons` | `bool` | Xbox, PlayStation, Nintendo, and Extended only. A MIDI or Keyboard+Mouse output cannot press a controller button, so its cells omit the choice rather than offering it with a warning. |
| `DescriptorDisplayProvider` | `Func<string,string>` | Resolves a descriptor to its display name for the Custom host's subtitles. |
| `InputChoicesProvider` | `Func<IEnumerable<InputChoice>>` | The slot's `SlotAvailableInputs`, for the Custom host's three pickers. |
| `RowBoundProvider` | `Func<int,int,bool>` | Whether a cell is already bound through a mapping row, which is what the read-only `RowBoundKind` binding kind reports. |
| `MacroNamesProvider` | `Func<IReadOnlyList<string>>` | The slot's macro names, live, for the #390 macro cells. |
| `LayerChoicesProvider` | `Func<IEnumerable<ShiftLayerInfo>>` | The slot's layer choices (Any Layer, Base, every named layer, every cycle stop) for the #413 layer picker. |
| `StructureChanged` | `Action` | Raised on a structural edit (enabled, kind, cell count, center cell). The owner forwards it to `MenusStructureChanged`. |
| `RuntimeEdit` | `Func<Action, bool>` | Routes the `Enabled` write through `InputService.TryEditMenuConfiguration`. A refused edit leaves the value unchanged. |

### Identity and shape

| Property | Type | Description |
|----------|------|-------------|
| `Name` | `string` | User-facing name. |
| `Enabled` | `bool` | Menu active. |
| `KindIndex` | `int` | The `MenuKind` by number: `0` Radial Ring, `1` Touch Grid, `2` Keyboard (#566), `3` Hotbar. Appended, since the numbers are saved. Switching to Grid or Hotbar forces `HasCenter = false`. A Keyboard leaves a ring's center cell alone, for when it turns back. Entering or leaving Keyboard or Hotbar swaps the style's default `PosYPercent` and `EngageDeadzonePercent` only while they still hold the other style's default (Keyboard: `PosYPercent` 100 and deadzone 50, Hotbar: deadzone 61 from `MenuHotbar.SteamDeadzonePercent`, ring and grid: `PosYPercent` 50 and deadzone 25), so a value the user set stays. Every switch rebuilds `Cells` and raises `StructureChanged`. |
| `IsRadial` | `bool` | Computed: `Kind == MenuKind.Radial`. Gates the Center Cell checkbox. |
| `IsKeyboard` / `IsHotbar` | `bool` | Computed: `Kind` is `Keyboard` or `Hotbar`. Raised from `RaiseKeyboardDependents` and `RaiseHotbarDependents` on a style change. |
| `IsCellMenu` | `bool` | Computed: not a Keyboard. The rows a ring or grid uses (Cells, Fire Mode, Show Labels, the cell bindings, the opener rows) hide on a Keyboard. |
| `ShowsClickRow` / `ShowsHostHalfRow` / `ShowsCustomAxesRows` | `bool` | Computed. The Click Input row hides on a Keyboard (it types with its own controls) and a Hotbar (it fires with its Fire control). Pad Half hides on a Keyboard (it points with its own pointer rows). The Custom Axes rows hide on a Keyboard and a Hotbar, which read no axes of a Custom opener. |
| `IsGrid` | `bool` | Computed: `Kind == MenuKind.Grid` (#471). Raised with `IsRadial` when `KindIndex` changes. |
| `ShowWebControllerRow` | `bool` | Computed: `IsGrid || ShowOnWebController` (#471). Shows the Show on Web Controller row on a Touch Grid, and on any menu while the flag is set, so a menu switched to Radial Ring can still clear it, the layer-hold row's rule. |
| `ShowOnWebController` | `bool` | (#471) Offer this Touch Grid menu to Web Menus phones on the slot. Write-through to the definition, reset to off through `ResetSettingCommand`. |
| `KindOptions` | `IReadOnlyList<MenuIntOption>` | Style combo items (`Menu_Style_*` resx): **Radial Ring**, **Touch Grid**, **Keyboard**, **Hotbar**. Instance accessor over a static backing field on purpose: WPF `{Binding}` resolves against the DataContext instance and never finds static properties. |
| `CellCount` | `int` | Cell count, clamped 1–20. Rebuilds `Cells`. |
| `HasCenter` | `bool` | Radial only: adds the center cell (index 0, Steam's "Radial Menu Center Button"), selected while inside the deadzone. Rebuilds `Cells`. |
| `FireTypeIndex` | `int` | Fire mode, clamped 0–3 over `FireOptions` (`Menu_Fire_*` resx): 0 On Click, 1 On Click Release, 2 On Touch Release, 3 While Hovered. A negative write (a Selector losing its items) is ignored. `FireOptions` swaps to the stay-open explanations while `EffectiveLayerHoldsOpen` is true. `SelectedFireDescription` is the selected option's longer explanation, or the note that a button-pair grid (`IsButtonPairGrid`: a grid on the `Gamepad DPad` or `Gamepad Diamond` host) ignores Fire Mode. |
| `EngageDeadzonePercent` | `int` | Engage deadzone, clamped 1–95. |

### Layer gate and stay-open (#413)

| Member | Type | Description |
|--------|------|-------------|
| `LayerMask` | `string` | The shift layer the menu is gated to. Empty and `"Base"` behave alike at runtime and both spellings are kept as written. A null write is ignored. Setting it to empty or `"Base"` also clears `LayerHoldsOpen`. |
| `LayerChoices` | `ObservableCollection<ShiftLayerInfo>` | The Layer picker items from `LayerChoicesProvider`, plus a marked "(not listed on this slot)" entry for an authored mask the slot lacks. Reconciled in place by mask. `LayerChoicesVersion` bumps after each reconcile. |
| `HasLayerScope` / `HasNamedLayer` | `bool` | Computed: any mask at all, and a mask that names a real layer (not `"Base"`). |
| `ShowsLayerRow` / `ShowLayerHold` | `bool` | Computed visibility of the Layer row and the stay-open checkbox. Each also shows while `LayerHoldsOpen` is set, so a malformed loaded file stays visible and clearable. |
| `LayerHoldsOpen` | `bool` | Layer Holds the Menu Open: the named layer keeps the menu open and the host surface only steers. A true write is refused without a named layer. `EffectiveLayerHoldsOpen` is what the runtime applies. |
| `HostInputLabel` / `HostInputTip` / `HostInputCaption` | `string` | The host row's text: "Opens With" normally, "Steer With" in stay-open mode. |
| `ResetLayerCommand` / `ResetLayerHoldsOpenCommand` | `RelayCommand` | Clear the gate (and the stay-open flag), or only the flag. |

### Host surface

| Property | Type | Description |
|----------|------|-------------|
| `HostOptions` | `IReadOnlyList<MenuHostOption>` | The five built-in host surfaces: `Gamepad LeftStick`, `Gamepad RightStick`, `Touchpad 0`, `Touchpad 1` (labels from `Menu_Host_*` resx, touchpads displayed 1-based as "Touchpad 1" / "Touchpad 2"), and `Custom` for the devices the named surfaces cannot describe (joysticks, wheels, anything not detected as a gamepad). An authored descriptor outside that grammar is appended as its own entry so the selection never silently lies. Never gated on assignment or online state, because imported profiles land on slots with nothing assigned yet. |
| `SelectedHost` | `MenuHostOption` | Selected host. A new menu starts on the right stick (the `MenuDefinitionEntry.HostDescriptor` default). An empty stored descriptor reads as the first option, the left stick. Selecting a non-touchpad host resets `HostHalf` to 0. |
| `HostIsTouchpad` | `bool` | Computed from `SelectedHost`. Shows the Pad Half row. |
| `IsCustomHost` | `bool` | Computed: the Custom host is selected, which swaps in the `CustomX` / `CustomY` / `Click` pickers (`CustomXChoices`, `CustomXSelected`, `CustomXSubtitle`, and their Y and click twins) and their own record buttons. |
| `HostHalfOptions` / `HostHalfIndex` | list / `int` | Pad Half picker for touchpad hosts: 0 Whole Pad, 1 Left Half, 2 Right Half. Clamped 0–2. |
| `HostRecording` | `bool` | Freeform-recorder state. |
| `HostRecordIcon` / `CustomXRecordIcon` / `CustomYRecordIcon` / `ClickRecordIcon` | `string` | Record-button glyphs: Stop (`E71A`) on the target currently recording, Record (`E7C8`) otherwise, mirroring the Aim Engage record button. |
| `PendingRecordTarget` | `MenuRecordTarget` | Which of `Host`, `CustomX`, `CustomY`, `Click` the next recorded descriptor lands on. Private setter. `PrepareRecord(MenuRecordTarget)` sets it. |

| Method | Description |
|--------|-------------|
| `TryApplyRecordedHost(string)` | Folds a freeform-recorded descriptor onto a host choice: stick axis and click reads pick the stick, touchpad-family reads pick the pad. Returns false when the recorded input has no host surface (buttons, gyro, keys). |
| `TryApplyRecorded(MenuRecordTarget, string)` | The same fold aimed at any of the four record targets. |
| `PrepareRecord(MenuRecordTarget)` | Aims the next recording at one target. |

### Overlay geometry

| Property | Type | Description |
|----------|------|-------------|
| `ShowLabels` | `bool` | Draw cell labels on the overlay. |
| `PosXPercent` / `PosYPercent` | `int` | Overlay center as work-area percents, clamped 0–100 (50/50 = centered). |
| `ScalePercent` | `int` | Overlay scale, clamped 10–400. |
| `OpacityPercent` | `int` | Overlay opacity, clamped 5–100. |

### Cells

| Member | Type | Description |
|--------|------|-------------|
| `Cells` | `ObservableCollection<MenuCellItem>` | One row per visible cell position: grid 0..N−1, radial (optional center 0 +) ring 1..N. |
| `RebuildCells()` | internal | Rebuilds the rows for the current shape. Existing item entries keep their data. Out-of-range entries (a shrunken ring's tail, a removed center) are pruned from the definition so exports and the overlay agree with the editor. |
| `EnsureItem(int)` / `DropItemIfEmpty(...)` | internal | Write-through for a cell edit: materializes the `MenuItemDefinition` on first use, drops it again when the label and both bindings are cleared. |

**Per-row resets** (canon: every setting row has one): `ResetHostCommand` (right stick, whole pad, custom descriptors cleared), `ResetHostHalfCommand` (whole pad), `ResetStyleCommand` (Radial), `ResetFireCommand` (On Click), `ResetCellsCommand` (4 cells, no center), `ResetGeometryCommand` (50/50, scale 100%, opacity 90%, labels on), `ResetDeadzoneCommand` (the style's `DefaultEngageDeadzonePercent`: 25, 50 for a Keyboard, 61 for a Hotbar), plus `ResetCustomXCommand` / `ResetCustomYCommand` / `ResetClickCommand` for the Custom host's three inputs.

### Keyboard style (#566)

**File:** `MenuEditorItem.Keyboard.cs` (a partial of `MenuEditorItem`). See [On-Screen Keyboard Internals](on-screen-keyboard-internals.md).

The On-Screen Keyboard as a menu. It has no cells (`RebuildCells` returns early, and items a ring or grid left keep their data for a flip back) and steers with its own controls. Every control writes through `KeyboardMenuDefaults.Set`, which keeps only what differs from the layout's default.

| Member | Description |
|--------|-------------|
| `KeyboardLayoutOptions` / `KeyboardLayoutIndex` / `KeyboardLayoutDescription` | The `KeyboardLayout`: **Grid** (0, one selection moved across the whole keyboard), **Split** (1, two halves, a steering input and a type input each) and **Wheel** (2, a daisy wheel of groups of four characters). Clamped 0-2. A change rebuilds the controls. `ResetKeyboardLayoutCommand` returns to Grid. |
| `OpenOnTextFocus` | **Open When a Text Box Is Selected**. |
| `OpenPressOptions` / `OpenPressIndex` / `OpenPressMs` / `ShowsOpenPressMs` / `OpenPressMsLabel` | The macro trigger's press modes that open and close the keyboard, by the trigger's own names: Press, Release, While Held, Hold, Short Press, Double Press, Triple Press, Single Press (`KeyboardOpenPress`). A change resets `OpenPressMs` to 0, so the new mode starts at its own default. The time (clamped 50-`KeyboardMenuDefaults.MaxOpenPressMs`, 10000) shows for the Hold-time and press-window modes, labeled with the trigger's Hold Time or Press Window. `ResetOpenPressCommand` returns to Press. |
| `FunctionRow`, `Suggestions`, `Symbols` | The Keyboard card. `Symbols` reads the default set (`OskLayoutFrame.DefaultSymbols`) until the user writes another, and writing the default set back stores nothing, so the default keeps following PadForge's. `ResetSymbolsCommand`. |
| `TypesThroughOptions` / `TypesThrough` | **Types Through**: **Windows Input**, **Same Keyboard as** each Keyboard + Mouse slot (`slot:<pad index>`, from `KbmSlotsProvider`, supplied by `MainViewModel.KeyboardMouseSlots`) and the HIDMaestro keyboards from `KbmDeviceCatalog.KeyboardOptions`. A stored value no entry carries (a slot no longer Keyboard + Mouse, a profile not on this PC) gets a marked entry, so the selection never lies. `RefreshTypesThrough()` re-reads the list when a slot changes type or label. `ResetTypesThroughCommand`. |
| `OpenRow` | The **Opens With** row, a `KeyboardInputRow` with no action. Its default is none. |
| `KeyboardControlRows` / `KeyboardControlsSummary` | One `KeyboardInputRow` per control of the layout, in `KeyboardMenuDefaults.Actions(layout)` order (`KeyboardControlAction`: typing, editing, shift and symbol pages, cursor moves, suggestions, steering, picks and pointer X, Y, touch and click, by layout). `ControlName(layout, action)` gives the row's label from the `Osk_Control_*` strings, with the left-hand and right-hand wrappers on the Split layout. The summary is `Menu_Keyboard_Controls_Summary_Format`. `ResetKeyboardControlsCommand` clears the saved controls of the current layout only. |
| `SetKeyboardInput(row, input)` | Writes one control, or Opens With, and refreshes the row. A write that changes nothing raises nothing. |
| `TryApplyKeyboardPress(row, press)` / `TryApplyKeyboardAxis(row, descriptor, deviceGuid)` | Fold a recorded press, combination (an AND leg), or axis onto a row. Both refuse an input the row does not `Accept`. |
| `RecordingKeyboardRow`, `KeyboardMapAllActive`, `MapAllText` | The row that is recording, and the Map All run that steps through every row. `MainViewModel.ClearMenuRecordings` clears them on a recording cancel. |

`KeyboardInputRow` (`MenuEditorItem.Keyboard.cs`) is one input row: `Action` (null for Opens With), `Layout`, `Label`, `Input` (`KeyboardMenuDefaults.Effective`), `Default`, `ChoicesView` (inputs on the slot's devices that the row accepts, grouped by device, with half-axis entries for a centered axis), `SelectedKey`, `Subtitle`, `ResetTip`, `RecordIcon` / `RecordText`, `ResetInputCommand`, and `AutomationId` (`MenuKeyboard_<Action>` or `MenuKeyboard_OpensWith`). `Accepts(descriptor)` encodes what each row reads: a pointer's X and Y take an input with a place (`IsPositionDescriptor`), a steering row takes any input and reads its depth, and every other row presses through the button read, so none takes a touchpad finger's place (`MappingItem.ButtonReadPressesNothing`). Controls other than Opens With refuse slot events and `Menu` cells. The press point (`ShowsThreshold`, `ThresholdPercent`, 1-99, default `KeyboardInput.DefaultThreshold` 50, `ResetThresholdCommand`) shows where `MappingItem.ButtonReadThresholds` says a Mappings row with a button target would show its deadzone. A pointer's X and Y have none, and a steering row has one only on a combination's second input.

### Hotbar style

**File:** `MenuEditorItem.Hotbar.cs` (a partial of `MenuEditorItem`).

A bar of cells run by four inputs, Steam Input's hotbar mode: Show or Hide opens and closes the bar, Previous and Next step the selection, Fire fires the selected cell. Cells are built like a grid's. A control left empty takes the Opens With direction (`MenuHotbar.DefaultControl`).

| Member | Description |
|--------|-------------|
| `HotbarShowSelected`, `HotbarPreviousSelected`, `HotbarNextSelected`, `HotbarFireSelected` | The descriptor of each control, written through `SetCustomInput` with the `MenuRecordTarget` values `HotbarShow`, `HotbarPrevious`, `HotbarNext`, `HotbarFire`. |
| `Hotbar<Control>ChoicesView`, `...Subtitle`, `...RecordIcon`, `...RecordText`, `Reset<Control>Command` | Per control: the pickable inputs (non-analog), the subtitle (`Menu_ClickDefault` when the opener supplies a default, else `Menu_NotRecorded`), the Record button's state and the reset, which writes an empty descriptor. |
| `HotbarWrap` | **Wrap Around**. Default off. |
| `HotbarDismissOnFire` | **Hide After Firing**. Default on. |
| `HotbarRecenter` | **Re-Center Each Time**. Default on. |

`FireOptions` for a Hotbar are the four fire modes as Steam's hotbar runs them (**On Click**, **On Click Release**, **On Touch Release**, **While Hovered**, with `Menu_Fire_*_Hotbar_Desc` descriptions). A Hotbar shows no layer-hold box (`ShowLayerHold` excludes it).

### Hotbar Controls

**File:** `MenuEditorItem.Hotbar.cs`

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `HotbarShowChoicesView` | `ICollectionView` | - | The Hotbar's four controls (Show, Previous, Next, Fire) each have a grouped input list (`Hotbar…ChoicesView`), a subtitle naming the device the input is read on (`Hotbar…Subtitle`), a record button's glyph and screen-reader text (`Hotbar…RecordIcon`, `Hotbar…RecordText`) and a reset (`ResetHotbar…Command`) that clears the control's input. |
| `HotbarPreviousChoicesView` | `ICollectionView` | - | See `HotbarShowChoicesView`. |
| `HotbarNextChoicesView` | `ICollectionView` | - | See `HotbarShowChoicesView`. |
| `HotbarFireChoicesView` | `ICollectionView` | - | See `HotbarShowChoicesView`. |
| `HotbarShowSubtitle` | `string` | - | See `HotbarShowChoicesView`. |
| `HotbarPreviousSubtitle` | `string` | - | See `HotbarShowChoicesView`. |
| `HotbarNextSubtitle` | `string` | - | See `HotbarShowChoicesView`. |
| `HotbarFireSubtitle` | `string` | - | See `HotbarShowChoicesView`. |
| `HotbarShowRecordIcon` | `string` | - | See `HotbarShowChoicesView`. |
| `HotbarPreviousRecordIcon` | `string` | - | See `HotbarShowChoicesView`. |
| `HotbarNextRecordIcon` | `string` | - | See `HotbarShowChoicesView`. |
| `HotbarFireRecordIcon` | `string` | - | See `HotbarShowChoicesView`. |
| `HotbarShowRecordText` | `string` | - | See `HotbarShowChoicesView`. |
| `HotbarPreviousRecordText` | `string` | - | See `HotbarShowChoicesView`. |
| `HotbarNextRecordText` | `string` | - | See `HotbarShowChoicesView`. |
| `HotbarFireRecordText` | `string` | - | See `HotbarShowChoicesView`. |
| `ResetHotbarShowCommand` | `RelayCommand` | - | See `HotbarShowChoicesView`. |
| `ResetHotbarPreviousCommand` | `RelayCommand` | - | See `HotbarShowChoicesView`. |
| `ResetHotbarNextCommand` | `RelayCommand` | - | See `HotbarShowChoicesView`. |
| `ResetHotbarFireCommand` | `RelayCommand` | - | See `HotbarShowChoicesView`. |

### Keyboard Controls Rows (#566)

**File:** `MenuEditorItem.Keyboard.cs`

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `RebuildKeyboardControls` | method (internal) | - | Rebuilds the Keyboard Controls rows from the layout's actions (`KeyboardMenuDefaults.Actions`). Empty for a menu that is not a Keyboard. |
| `IsSlotEvent` | method (internal, static) | - | A touchpad or mouse gesture or a menu cell: inputs the keyboard's own controls cannot read, since the keyboard holds the controller at rest while it is open and they come from that state. Opens With reads them, since the keyboard is closed when it opens. |
| `HasHalves` | method (internal, static) | - | Whether an input has two halves to list: a plain axis, the abstract Gamepad sticks among them, with no direction of its own yet, on `deviceGuid`. A stick rests at the middle of its range, so a press or a steering direction reads one half of it. An axis that rests at zero and moves one way (a gamepad's trigger, by its Gamepad name or on the controller, a VR controller's trigger or grip, a Bliss-Box pressure axis) is listed whole, by the rule the press recorder records it by (InputManager.AxisRestsAtZero): its lower half would read pressed at rest. |
| `KeyOf` | method (internal, static) | - | The key a list entry is found by: the device and the input, and the second input of a combination. |
| `KeyboardChoicesView` | method (internal) | - | A row's input list: the slot's inputs, grouped by device as the mapping picker shows them, less those the row cannot read (`Accepts`). An axis that rests at the middle is followed by its two halves, the directions a recorded push gives (`HasHalves`), on every row but a pointer's X and Y, which read the whole axis. The device-free "Gamepad ..." names sit under (Any Device). The row's own input, when no entry is it (a combination), gets an entry of its own so the selection never lies. |
| `KeyboardInputText` | method (internal) | - | An input's text: its name in the slot's lists, an axis half's direction, and a combination's two parts. |
| `KeyboardSubtitle` | method (internal) | - | A row's subtitle: the device its input is read on, both devices for a combination across two, or that it has none. |
| `RaisingKeyboardChoices` | `bool` (internal) | - | True while a row's list is being replaced: the selector clears its selection during the swap, which is no edit (`_raisingInputChoices`'s reason). |

#### KeyboardInputRow

One row of the Keyboard Controls card, the Opens With row or one control.

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `Action` | `KeyboardControlAction?` | - | The control, or null for Opens With. |
| `Layout` | `KeyboardLayout` | - |  |
| `Label` | `string` | - |  |
| `IsOpensWith` | `bool` | - |  |
| `RecordsAnAxis` | `bool` | - | A pointer's X or Y row, which takes a place across a range and records an axis. |
| `Accepts` | method (internal) | - | Whether the row reads an input. A pointer's X and Y take an input with a place (`IsPositionDescriptor`). A key, a pointer's touch and click, and Opens With press through the button read, which never presses on a touchpad finger's place (`ButtonReadPressesNothing`), so none of them takes one. A steering row reads its input's depth and keeps it. Opens With takes every other input, gestures and menu cells too. The controls take all but those two, which stop while the keyboard holds the controller at rest. |
| `AutomationId` | `string` | - | The row's id for UI Automation, stable across languages. |
| `Input` | `KeyboardInput` | - |  |
| `Default` | `KeyboardInput` | - |  |
| `ChoicesView` | `ICollectionView` | - |  |
| `SelectedKey` | `string` | - |  |
| `Subtitle` | `string` | - | The device the input is read on, or, while the row records, what to do. |
| `ResetTip` | `string` | - | The reset button's name: what the default is. |
| `IsRecording` | `bool` | - | Whether the recorder listens for this input. Drives the record button's icon and tooltip. |
| `RecordIcon` | `string` | - |  |
| `RecordText` | `string` | - |  |
| `ResetInputCommand` | `RelayCommand` | - | Resets input to its default. |
| `ShowsThreshold` | `bool` | - | Whether the row's press point acts, so its Axis-to-Button Deadzone shows. A key, a pointer's touch or click and Opens With press at it where a Mappings row with a button target would, for either input of a combination (`ButtonReadThresholds`). A steering row reads its input's depth, so only a combination's second input, which holds the steering as a press, has one. A pointer's X and Y read a place, and have none. |
| `ThresholdPercent` | `int` | - | The press point, 1 to 99 percent of the input's travel, 50 unless set. A held press lets go at 70% of it. Clamped to 1 to 99. |
| `ThresholdName` | `string` | - | The press point's name for screen readers, with the row's. |
| `ThresholdAutomationId` | `string` | - | The press point's id for UI Automation. |
| `ResetThresholdCommand` | `RelayCommand` | - | Resets `ThresholdPercent` to `KeyboardInput.DefaultThreshold`. |
| `RaiseRecording` | method (internal) | - | Whether the recorder listens for this input. Drives the record button's icon and tooltip. |
| `Refresh` | method (internal) | - | Re-reads the row after its input changed or the slot's lists did: the list first, then the selection against it. |

`KeyboardChoice` is one entry of a row's input list (`Key`, `DisplayName`, `DeviceLabel`, `Input`). `MenuStringOption` is a value-and-label picker entry (`Value`, `Label`).

### More MenuEditorItem Members

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `Entry` | `MenuDefinitionEntry` (internal) | - | The `MenuDefinitionEntry` on the slot's `MappingSet` that the editor writes through to. |
| `EnsureOptionsCultureCurrent` | method (internal, static) | - | Rebuilds the static option lists' labels after a language change. |
| `KindLabel` | `string` | - | The menu's style in words, which the slot's list of menus shows at the end of its item. |
| `RefreshLayerChoices` | method (internal) | - | Re-raises the layer gate's choices. |
| `HostOptionsFor` | method (internal) | - | The opener list with `current` listed: the two sticks, the D-pad and the face buttons (the button-pair hosts the runtime has run since translator v25, #566), two touchpads and Custom Axes. |
| `RefreshHostOptions` | method (internal) | - | Re-raises the opener list and selection after a direct Entry.HostDescriptor mutation (record fold, reset) or a culture change rebuilds the labels. |
| `CustomYChoices` | `IReadOnlyList<InputChoice>` | - | The Custom opener's three input lists (`CustomXChoices`, `CustomYChoices`, `ClickChoices`), their grouped views (`…ChoicesView`), their subtitles naming the device (`CustomXSubtitle`, `CustomYSubtitle`, `ClickSubtitle`) and their selections (`CustomXSelected`, `CustomYSelected`, `ClickSelected`). |
| `ClickChoices` | `IReadOnlyList<InputChoice>` | - | See `CustomYChoices`. |
| `CustomXChoicesView` | `ICollectionView` | - | See `CustomYChoices`. |
| `CustomYChoicesView` | `ICollectionView` | - | See `CustomYChoices`. |
| `ClickChoicesView` | `ICollectionView` | - | See `CustomYChoices`. |
| `CustomYSubtitle` | `string` | - | See `CustomYChoices`. |
| `ClickSubtitle` | `string` | - | See `CustomYChoices`. |
| `CustomYSelected` | `string` | - | See `CustomYChoices`. |
| `ClickSelected` | `string` | - | See `CustomYChoices`. |
| `CanResetSetting` | method (internal, static) | - | The names `ResetSettingCommand` accepts on this class. |
| `RefreshInputChoices` | method (internal) | - | Re-raises the three input dropdowns after the slot's picker list repopulates (device assignment changes) or the culture moves. Labels come from the live picker, so both events can relabel every entry. |
| `BeginRecord` | method (internal) | - | Arms a record target (`PendingRecordTarget`, `RecordingTarget`). `BeginRecordAfterStart` is the guarded form the record buttons use. |
| `BeginRecordAfterStart` | method (internal) | - | Runs `start`, which starts the recorder and says whether it runs, and arms `target` only then. The start cancels any recording another record button left running, and that cancel clears every menu's Recording state (MainViewModel.ClearMenuRecordings), so the state is set after it. With no device to record from, nothing is armed. |
| `StopGlyph` | `string` (internal, static) | - | Segoe MDL2's Stop and Record glyphs, which every record button in the Menus part shows (#566's rows share them). |
| `RecordGlyph` | `string` (internal, static) | - | See `StopGlyph`. |
| `HostRecordText` | `string` | - | The record buttons' names for screen readers, "Record" or "Recording" as the glyph shows, the text the Aim Engage record button's tooltip gives. |
| `CustomXRecordText` | `string` | - | See `HostRecordText`. |
| `CustomYRecordText` | `string` | - | See `HostRecordText`. |
| `ClickRecordText` | `string` | - | See `HostRecordText`. |
| `DefaultEngageDeadzonePercent` | `int` (internal) | - | The engage deadzone a menu of this style starts with, the value a switch to the style sets. |
| `MaxCells` | `int` (internal, const) | - | The most cells a ring, a grid or a hotbar has. |
| `SelectedCell` | `MenuCellItem` | - | The cell open in the editor's list, or none. It is not saved: a menu opens with its cells closed. |
| `EditCellCommand` | `RelayCommand<MenuCellItem>` | - | A cell's pencil: opens that cell, and closes it when it is the open one. |
| `AddCellCommand` | `RelayCommand` | - | Add Cell: one more cell at the end, open. Cells come and go at the end alone: a cell's number is what a mapping or a macro names it by ("Menu 1 Item 3"), so no cell changes its number. |
| `RemoveLastCellCommand` | `RelayCommand` | - | Remove: the last cell leaves the menu. What it held stays with the menu out of reach, as a cell past a smaller shape's reach does (RebuildCells), and comes back with the cell. |
| `RaiseChanged` | method (internal) | - | Marks the menu edited (`OnEdited`), from outside the item. |
| `RefreshCellsAfterExternalEdit` | method (internal) | - | Re-raises every cell row's bindings after an external mutation of the underlying items (#390: the macro-rename retag). The cell refresh raises the same property set a culture change does, which covers every picker. |

### MenuCellItem

**File:** `MenuEditorItem.cs`

One cell row in the menu editor: a label, an optional icon, and one direct binding. The backing `MenuItemDefinition` reference is null until the cell has content.

| Property | Type | Description |
|----------|------|-------------|
| `Index` / `IsCenter` | `int` / `bool` | Cell position. `Header` renders "Center" or the localized "Cell {n}". |
| `Label` | `string` | Cell label. Setting it materializes the item entry, clearing it drops an otherwise-empty entry. |
| `HasIcon` / `IconName` / `IconImage` / `ShowIconGlyph` / `IsGlyphIcon` | `bool` / `string` / `ImageSource` / `bool` / `bool` | Cell icon: the stored reference, the resolved image, the picture-glyph fallback used when a picture reference resolves to nothing, and (#471) whether the icon is an emoji, which the row shows as itself and never resolves as an image. Written through the internal `SetIcon(string)`, which the shared icon picker calls. An empty reference clears the icon and prunes an otherwise-empty item. |
| `IconScalePercent` | `int` | Per-cell icon size as a percent of the menu's normal icon box (#413), clamped 25–200. Reads 100 and ignores writes while the cell has no icon. Reset through `ResetSettingCommand`. |
| `BindingKind` | `int` | Derived from which field is set: `0` none, `1` keyboard key, `2` VC button (Xbox mask on Xbox and PlayStation slots, 1-based raw button number on Extended slots, per the owner's button style), `3` `RowBoundKind` (no direct binding but bound through mapping rows, a read-only sentinel, and the cell still fires as a menu-item source), `4` `MacroKind` (#390). Selecting a kind seeds a default and zeroes the others. |
| `BindingKindOptions` | `IReadOnlyList<MenuIntOption>` | Built per read, dynamic per slot type. None and Keyboard Key everywhere. Controller Button only where the slot's output can press one, or as a marked "unsupported" entry when a slot-type switch left a stale button binding, so the selection never lies. Macro only while the slot has macros, or when the cell already carries a name. `RowBoundKind` appears only while that is the current kind. |
| `ShowKeyPicker` / `ShowButtonPicker` / `ShowMacroPicker` | `bool` | Computed from `BindingKind` (1 / 2 / 4). |
| `SelectedKeyVk` | `int` | Virtual-key code. `KeyOptions` offers the full `VirtualKey` vocabulary the macro editor's Key Press offers, with the same localized labels. `VirtualKey.None` is dropped: a cell with no key is an empty cell, cleared by its reset button, never by a "None" pick. |
| `SelectedButtonFlag` | `int` | The Xbox button mask on Xbox and PlayStation slots, or the 1-based raw button number on a numbered-style slot. Labels come from the macro editor's `MacroButtonNames` tables. After a slot-type switch the stored value in the other space is shown through the shared mask-to-number mapping. |
| `SelectedMacroName` | `string` | The macro this cell fires, by name (#390). |
| `MacroOptions` | `IReadOnlyList<MenuHostOption>` | The slot's macro names from `MacroNamesProvider`. A name the slot no longer declares stays in the list under a "missing" label rather than vanishing, and the runtime treats the stale name as an inert no-op. |
| `ResetCellCommand` | `RelayCommand` | Clears the icon (and its size), the label, and the binding, which drops the item entry. |

**More MenuCellItem members:**

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `CanResetSetting` | method (internal, static) | - | The names `ResetSettingCommand` accepts on this class. |
| `HasLabel` | `bool` | - | Whether the cell has a label of its own. |
| `RowName` | `string` | - | The cell's name in the editor's list, as the Macros board names a cell (#574): its label, else what it runs ("Quick Combo", "R"), else its place ("Cell 3", a ring's "Center"). |
| `IsPlaceName` | `bool` | - | The list names the cell by its place: it has no label and runs nothing with a name. The list draws a place in the quiet color. |
| `Summary` | `string` | - | What the cell does, in the editor's list: the kind of its binding and, where the kind has one, what it presses or runs ("Keyboard Key, R"). |
| `RefreshCulture` | method (internal) | - | Re-raises the cell's culture-dependent text. |
| `ButtonOptions` | `IReadOnlyList<MenuIntOption>` | - | Button choices in the SLOT'S lettering, mirrored from the macro editor's tables (MacroButtonNames.DeriveStyle): Xbox letters on Xbox slots, DualShock symbols on PlayStation slots, numbered raw buttons (1..layout count) on Extended slots. Built fresh per read: the lists are tiny, and both a language switch and a slot-type switch re-raise this property. Clamped to 0 to 128. |
| `RefreshButtonStyle` | method (internal) | - | Re-raises the button options after the slot's lettering changed. |

### Cell Icons and Icon Packages (#390)

A cell's `Icon` is one reference string, resolved by `PadForge.Common.MenuIconResolver.Resolve` into a frozen `ImageSource`. Three shapes, tried in that order, with misses cached as null so a menu rebuild never re-probes the disk for a known-absent file:

1. `pficon://Package/entry`, an entry inside a registered icon package.
2. A loose image path, exe-relative or absolute. The shape test wants a directory separator or a drive colon plus one of the pack image extensions. Existence is the loader's problem.
3. A bare Steam binding-icon name, resolved under the Steam install.

`PadForge.Common.IconPackageManager` owns the packages. A package is a `.pficons` file: a zip carrying the images and an optional `manifest.json` display name. Recognized image formats are `.png`, `.jpg`, `.jpeg`, `.bmp`, `.gif`, one list shared by the pack probe, the entry lister, and the editor's loose-file gate, so every surface agrees on what an icon is.

| Member | Description |
|--------|-------------|
| `Scheme` / `FileExtension` | `"pficon://"` and `".pficons"`. |
| `Packages` | The registry: `PackageRef` rows of `Name` and `Path`. The stored path is relative to the exe directory when the pack lives under it, absolute otherwise. |
| `RegistryChanged` | Raised on any registry change. `MenuIconResolver` subscribes and drops its whole cache, since a registration, rename, or removal changes what `pficon://` references resolve to and misses are cached. |
| `Register(string filePath)` / `Register(string, out string probedName)` | Adds a pack, returning its registered name. |
| `Unregister(string name)` | Removes a pack. |
| `LoadRegistry(...)` / `SaveRegistry()` | Settings round-trip. |
| `IsPackageRef` / `MakeRef` / `TryParseRef` / `DisplayName` | Reference-string grammar. |
| `ResolvePackageFile` / `ResolvePath` / `MakeStoredPath` | Path resolution against the exe directory. |
| `TryReadIcon(string iconRef)` | The bytes behind one reference. |
| `ListIcons(string packageName)` / `ListIconsInFile(string filePath)` | Entry names, for the picker. |
| `ExportPackage(string destFilePath, string displayName, IEnumerable<string> imageFiles)` | Builds a pack from loose images. Entry names are the source file names, with a `" (2)"` suffix on same-named files from different folders. It writes to a temp file and moves it into place, so a mid-write failure never leaves a truncated pack at the destination. |

### MenuHostOption / MenuIntOption

**File:** `MenuEditorItem.cs`

`MenuHostOption` is one pickable host surface (`Descriptor`, `Label`, `IsTouchpad`), and it is also reused for the macro picker's rows. `MenuIntOption` is a generic labeled int option used by the style, half, fire, binding-kind, and button combos (`Value`, `Label`, `Description`). The key picker reuses `SocdKeyOption` from `KbmSlotConfig` instead. Both option types override `ToString()` with the label.

---

## ProfileShortcutViewModel

**File:** `ProfileShortcutViewModel.cs`

Wraps a `GlobalMacroData` instance for data binding in the ProfilesPage shortcuts card. One ViewModel per shortcut row.

### Constructor

```csharp
public ProfileShortcutViewModel(
    GlobalMacroData data,
    Action<ProfileShortcutViewModel> deleteCallback,
    Action<ProfileShortcutViewModel> saveCallback)
```

`deleteCallback` removes the row. `saveCallback` triggers a settings save via `SettingsService.MarkDirty()`.

### Switch Mode

| Property | Type | Description |
|----------|------|-------------|
| `SwitchMode` | `SwitchProfileMode` | Two-way bound to mode ComboBox. Setter writes through to `Data.SwitchMode` and raises `IsSpecificMode`. |
| `IsSpecificMode` | `bool` (computed) | `true` when `SwitchMode == Specific`. Controls visibility of the target profile dropdown. |
| `SwitchModes` | `ObservableCollection<SwitchProfileModeItem>` | Dropdown items: Next, Previous, Specific, ToggleWindow, ToggleVCsDisabled (v3.2). |

`SwitchProfileModeItem` is a class extending `ObservableObject` with a read-only `Mode` and a mutable `DisplayName` that updates in place on culture change. `ToString()` returns `DisplayName` so ComboBox display refreshes on language switch without rebuilding the list.

### Target Profile (Specific mode)

Selection binds to a stable ID, not a display name. The previous name-keyed properties were removed: rebuilding a fresh `ObservableCollection<string>` on every culture refresh replaced the ComboBox `ItemsSource` instance, which cleared `SelectedItem` and wrote null back through the binding, wiping `Data.TargetProfileId` / `TriggerDeviceGuid` / `SwitchMode`. The persistent-collection + stable-ID-selection shape fixes that.

| Member | Type | Description |
|--------|------|-------------|
| `TargetProfileId` | `string` | Two-way selection target. Empty string is the localized "Default" sentinel. Any other value is a `ProfileEntry.Id`. Getter reads `Data.TargetProfileId ?? ""`. Setter writes through (empty maps to `null`) and invokes the save callback. |
| `ProfileChoices` | `ObservableCollection<ProfileChoice>` | Persistent dropdown items: the "Default" sentinel plus one per `SettingsManager.Profiles` entry. |
| `RebuildProfileChoices()` | method | Rebuilds `ProfileChoices` in place from `SettingsManager.Profiles`. The page's DropDownOpened handler calls it so newly-saved / deleted profiles surface without tearing down the shortcut row. |

### Trigger Device

| Member | Type | Description |
|--------|------|-------------|
| `TriggerDeviceGuid` | `Guid` | Two-way selection target. `Guid.Empty` is the localized "Any Connected Device" sentinel (`Profiles_ShortcutDevice_Any`). Getter/setter proxy `Data.TriggerDeviceGuid` and invoke the save callback on change. |
| `DeviceChoices` | `ObservableCollection<DeviceChoice>` | Persistent dropdown items: the "Any Connected Device" sentinel plus one per online, named `SettingsManager.UserDevices` entry. |
| `RebuildDeviceChoices()` | method | Rebuilds `DeviceChoices` in place from `SettingsManager.UserDevices`. Called from the page's DropDownOpened handler so newly-connected / disconnected devices surface without a row teardown. |

`ProfileChoice` and `DeviceChoice` are the same mutable-wrapper pattern as `SwitchProfileModeItem`: a stable key (`ProfileId` / `DeviceGuid`) plus a `DisplayName` that updates in place on culture change, with `ToString()` returning `DisplayName`. Selection is unaffected by a language switch because no item is added or removed.

### Button Combo Display

| Property | Type | Description |
|----------|------|-------------|
| `ButtonComboDisplay` | `string` (computed) | Human-readable trigger combo. Joins entries with " + ", resolving each to a friendly name (e.g., "A (Xbox Controller) + LT+ (Xbox Controller)"). During recording, appends countdown. |

Name resolution helpers:
- `ResolveButtonName(int index, Guid deviceGuid)`. Gamepad-type devices use A, B, X, Y, then the localized Left Shoulder, Right Shoulder, Back, Start, Left Stick Button, Right Stick Button, and Guide for indices 0–10. Keyboard devices resolve via the `VirtualKey` enum. Others fall back to `Macro_Btn_Format`, "Btn N" with N one-based.
- `ResolveAxisName(int index, Guid deviceGuid, AxisTriggerDirection direction)`. Gamepad axes use LX/LY/LT/RX/RY/RT names with +/– suffix. Others use "Axis N+/–".
- `ResolveDeviceName(Guid deviceGuid)`. Returns `ResolvedName` from `UserDevices`, or `null` for `Guid.Empty`.

### Recording State

| Property | Type | Description |
|----------|------|-------------|
| `IsRecording` | `bool` | `true` during Learn mode. Raises `LearnButtonText` and `LearnButtonIcon`. |
| `RecordingCountdown` | `int` | Seconds remaining. Raises `ButtonComboDisplay` on change. |
| `LearnButtonText` | `string` (computed) | `Common_Stop` while recording, else `Common_Record`. |
| `LearnButtonIcon` | `string` (computed) | `\uE71A` (Stop) or `\uE7C8` (Record) |

| Method | Description |
|--------|-------------|
| `SetLearnedButtons(TriggerButtonEntry[] entries)` | Saves captured entries to `Data.TriggerEntries`, clears recording state, invokes save callback. |
| `CancelRecording()` | Clears `IsRecording` without saving. |
| `NotifyComboChanged()` | Raises `ButtonComboDisplay` for live display during recording. |

**More ProfileShortcutViewModel members:**

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `ComboParts` | `IReadOnlyList<ShortcutKeyPart>` | - | The recorded button combination in parts, whether there is one, and the note beside it. |
| `HasCombo` | `bool` | - | See `ComboParts`. |
| `ComboNote` | `string` | - | See `ComboParts`. |
| `ResetSettingCommand` | `RelayCommand<string>` | - | The generic per-setting reset (see [Per-Setting Reset Commands](#per-setting-reset-commands)). |
| `CanResetSetting` | method (internal, static) | - | The names `ResetSettingCommand` accepts on this class. |

`ShortcutKeyPart` is one key of the combination as the row draws it: `Name` (Guide, Right Shoulder, LT+), `Device` and `DeviceTail` (the device after the name, two spaces in, or nothing). `DeviceChoice` (`DeviceGuid`, `DisplayName`), `ProfileChoice` (`ProfileId`, `DisplayName`) and `SwitchProfileModeItem` (`Mode`, `DisplayName`) are the row's picker entries.

### Commands

| Command | Action |
|---------|--------|
| `DeleteCommand` | Invokes `_deleteCallback`. Removes this shortcut from the list. |
| `ClearCommand` | Sets `Data.TriggerEntries = null`, updates display, saves. |

---

## StickConfigItem

**File:** `StickConfigItem.cs`

One thumbstick card in the Sticks group. Gamepad presets: 0 = Left, 1 = Right. Custom Extended: 0..N per `ThumbstickCount`.

### Identity

| Property | Type | Description |
|----------|------|-------------|
| `Title` | `string` | Display title (e.g., `"Left Thumbstick"`, `"Stick 1"`). Read-only. |
| `Index` | `int` | Stick index (0-based). Read-only. |
| `AxisXIndex` | `int` | Raw axis index for X in `RawHidState.Axes` (custom Extended only, -1 for gamepad). Read-only. |
| `AxisYIndex` | `int` | Raw axis index for Y in `RawHidState.Axes` (custom Extended only, -1 for gamepad). Read-only. |
| `IsPointerStick` | `bool` | Set at construction. True on a KBM slot, where stick 0 is mouse movement and stick 1 the scroll wheel. Those are rate outputs, so the speed multiplier row applies there and only there. |
| `IsMouseStick` | `bool` | Set at construction. True only for the KBM slot's stick 0. Gates the Momentum rows, since a coasting scroll wheel is kinetic scrolling and out of #291's scope. |

### Speed and Momentum

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `Sensitivity` | `double` | `1.0` | 0.1–5.0 | Flat speed multiplier. Live for the pointer sticks above only. On a gamepad stick the per-axis response curves own the shaping. Reset: `ResetStickSensitivityCommand`. |
| `MomentumEnabled` | `bool` | `false` | - | Stick trackball (#291): flick the mouse stick and release, and the cursor keeps traveling, coasting to a stop on the same constant-deceleration physics the touchpad's Momentum uses. |
| `MomentumGlide` | `double` | `0.90` | 0.80–1.00 | The coast's friction band, identical to the touchpad's Momentum Glide. 0.80 full friction, 1.00 frictionless. |

**Reset commands:** `ResetMomentumCommand`, `ResetMomentumGlideCommand`.

### Deadzone Configuration

All percentage properties clamped to 0–100. Each has a `*Digit` companion for digit-based binding (signed 16-bit: +/−32768).

| Property (%) | Digit Property | Default | Description |
|--------------|----------------|---------|-------------|
| `DeadZoneX` | `DeadZoneXDigit` | `0` | X deadzone percentage. |
| `DeadZoneY` | `DeadZoneYDigit` | `0` | Y deadzone percentage. |
| `AntiDeadZoneX` | `AntiDeadZoneXDigit` | `0` | X anti-deadzone percentage. |
| `AntiDeadZoneY` | `AntiDeadZoneYDigit` | `0` | Y anti-deadzone percentage. |
| `MaxRangeX` | `MaxRangeXDigit` | `100` | X max range (positive), 1–100. |
| `MaxRangeY` | `MaxRangeYDigit` | `100` | Y max range (positive), 1–100. |
| `MaxRangeXNeg` | `MaxRangeXNegDigit` | `100` | X max range (negative), 1–100. |
| `MaxRangeYNeg` | `MaxRangeYNegDigit` | `100` | Y max range (negative), 1–100. |
| `CenterOffsetX` | `CenterOffsetXDigit` | `0` | X center offset, −100 to 100. |
| `CenterOffsetY` | `CenterOffsetYDigit` | `0` | Y center offset, −100 to 100. |
| `Linear` | - | `0` | Linear interpolation factor (0–100). |

### Deadzone Shape

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `DeadZoneShape` | `DeadZoneShape` | `ScaledRadial` | Shape enum. Notifies `DeadZoneShapeIndex` and `Is*Shape` properties. |
| `DeadZoneShapeIndex` | `int` | `0` | ComboBox SelectedIndex. Maps display order to enum. |
| `IsAxialShape` | `bool` | - | Computed. |
| `IsRadialShape` | `bool` | - | Computed: Radial or ScaledRadial. |
| `IsSlopedShape` | `bool` | - | Computed: SlopedAxial or SlopedScaledAxial. |
| `IsHybridShape` | `bool` | - | Computed. |
| `HasSlopedWedges` | `bool` | - | Computed: SlopedAxial, SlopedScaledAxial, or Hybrid. |

**Display order:** ScaledRadial(0), Radial(1), Axial(2), Hybrid(3), SlopedScaledAxial(4), SlopedAxial(5).

### Sensitivity Curves

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `SensitivityCurveX` | `string` | `"0,0;1,1"` | X-axis sensitivity curve (control point string). |
| `SensitivityCurveY` | `string` | `"0,0;1,1"` | Y-axis sensitivity curve. |
| `PresetNameX` | `string` | - | Computed: matched preset name for X curve. |
| `PresetNameY` | `string` | - | Computed: matched preset name for Y curve. |

| Static | Description |
|--------|-------------|
| `CurvePresetNames` | `string[]` of available curve preset display names. Rebuilt on culture change. `CurvePresetChoices` is its instance accessor for XAML. |

### Calibration

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `IsCalibrating` | `bool` | `false` | Center calibration in progress. |
| `HardwareRawX` | `short` | - | Unprocessed hardware X value (not affected by offset/deadzone). |
| `HardwareRawY` | `short` | - | Unprocessed hardware Y value. |

| Method | Description |
|--------|-------------|
| `StartCalibration()` | Samples RawX/RawY over ~0.5 s (15 frames at 33 ms). Sets CenterOffsetX/Y to negate drift. |

### Boundary Calibration (#174)

Measures the stick's real physical boundary by sweeping the rim, then reshapes it toward a circle at runtime (Step 3 warp). Offered only for the two primary physical thumbsticks the warp covers.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `BoundaryMap` | `string` | `""` | Serialized measured boundary (StickBoundary format). Empty = uncalibrated, no reshaping. The setter rebuilds the radar overlay and circularity readout. |
| `HasBoundaryCalibration` | `bool` | - | Computed: `BoundaryMap` is non-empty. |
| `SupportsBoundaryCalibration` | `bool` | - | Set at construction. True for the Xbox/PlayStation two-stick grid and Extended primary sticks 0/1. False for KBM pseudo-sticks and Extended custom sticks 2+. |
| `IsCalibratingBoundary` | `bool` | `false` | A boundary sweep is in progress. Notifies `BoundaryButtonText`. |
| `BoundarySectorsRemaining` | `int` | `0` | Live count of rim sectors still uncovered during a sweep. Notifies `BoundaryButtonText`. |
| `BoundaryButtonText` | `string` | - | Computed button caption: Calibrate / Recalibrate idle prompt, the `"N sectors left"` countdown, or the second-lap prompt. |
| `BoundaryPolygonPoints` | `PointCollection` | empty | Measured boundary as a convex polygon in the 200×200 radar plot. |
| `BoundaryCircularityText` | `string` | `""` | Computed circularity readout for the plot. |

| Command | Description |
|---------|-------------|
| `CalibrateBoundaryCommand` | Starts (or, if sweeping, commits) a boundary sweep. |
| `ResetBoundaryCommand` | Cancels any sweep and clears `BoundaryMap`. |

| Method | Description |
|--------|-------------|
| `StartBoundaryCalibration()` | Runs a coverage-driven ~60 Hz rim sweep off `HardwareRawX/Y`, auto-completing once every sector is covered and at least two full rotations have swept (30 s cap). Clicking again while sweeping commits early. |

### Live Preview

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `LiveX` | `double` | `0.5` | Live X (0.0–1.0 for Canvas). |
| `LiveY` | `double` | `0.5` | Live Y. |
| `RawX` | `short` | `0` | Processed raw X. Notifies `OutDisplayX` (and `RawY`, `OutDisplayY`). |
| `RawY` | `short` | `0` | Processed raw Y. |
| `LiveInputX` | `double` | `0` | CurveEditor X input (0–1). |
| `LiveInputY` | `double` | `0` | CurveEditor Y input. |
| `RawPosX` / `RawPosY` | `double` | `0.5` | Raw-stage dot position (0–1, before the pipeline) for the two-stage plot (#175). `LiveX` / `LiveY` hold the processed stage. Notifies `InDisplayX` / `InDisplayY`. |

### Steering Mode (#94)

Per-stick steering source kind and its tunables. The kind feeds the matching `Param*` fields on the stick's `MappingSet` rows at build time.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `SteeringModeIndex` | `int` | `0` | 0 Linear (`Direct`), 1 `WindingStick`, 2 `AngleToAxisX`, 3 `AngleToAxisY`. Clamped 0–3. `SteeringKind` is the matching `MappingSource.Kind`, and `SetSteeringKind(string)` sets the index from one on load (an unknown kind falls back to Linear). |
| `IsSteeringActive` / `IsWindingMode` / `IsAngleMode` | `bool` | - | Computed from the index. |
| `WindRangeDeg` | `double` | `900` | Winding range in degrees, clamped 90–2520. |
| `WindPower` | `double` | `1` | Winding power, clamped 0–4. |
| `WindUnwindRate` | `double` | `1800` | Unwind rate, clamped 0–10000. |
| `AngleInnerDz` / `AngleOuterDz` | `double` | `0` / `10` | Angle-mode inner and outer deadzones in degrees, clamped 0–89. |
| `SteerStickDeadZone` | `double` | `15` | Stick Deadzone (`Pad_Steering_StickDeadZone`), the stick's radial deadzone for both steering modes, in percent of full deflection, clamped 0–90. Below it the stick reads as centered, so no wind accrues and no angle is output. The steering source reads it as `MappingSource.ParamStickDeadzone`, since the raw-axis read under the steering math applies none. `ResetSteerStickDeadZoneCommand` puts back 15. |

### More StickConfigItem Members

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `EnsurePresetsCultureCurrent` | method (internal, static) | - | Rebuilds the static preset lists' labels after a language change. |
| `IconLabel` | `string` | - | The label the card's icon carries. Set at construction. |
| `ResetAllToolTip` | `string` | - | The card's Reset All tooltip, `Pad_ResetSection_Format` with the card's title. |
| `DeadZoneBoth` | `double` | - | Both axes at once, for the card's single rows: `DeadZoneBoth` reads the larger deadzone and writes both (0 to 100), `SensitivityCurveBoth` the curve, and `PresetNameBoth` the curve's preset name, or `Curve_Custom` while the two axes differ. Their resets are `ResetDeadZoneBothCommand` and `ResetSensitivityBothCommand`. Clamped to 0 to 100. |
| `SensitivityCurveBoth` | `string` | `"0,0;1,1"` | See `DeadZoneBoth`. |
| `PresetNameBoth` | `string` | - | See `DeadZoneBoth`. |
| `MoreStateKey` | `string` | - | The key the card's More fold remembers its open state under (`"Pad.Sticks.Stick{Index}.More"`). |
| `DeadZoneSteelGeometry` | `Geometry` | - | The deadzone's outline on the stick plot, from the X and Y deadzones. |
| `InDisplayX` | `string` | - | Computed: the raw stage (`RawPosX`, `RawPosY`) and the processed stage (`RawX`, `RawY`) as axis units and percent, through `AxisText(units, percent)` (internal static, `"-1234 (48.1%)"`). |
| `InDisplayY` | `string` | - | See `InDisplayX`. |
| `OutDisplayX` | `string` | - | See `InDisplayX`. |
| `OutDisplayY` | `string` | - | See `InDisplayX`. |
| `AxisText` | method (internal, static) | - | See `InDisplayX`. |
| `RebuildCurvePoints` | method | - | Rebuilds the curve editor's points from the stored curve. |
| `ResetDeadZoneBothCommand` | `ICommand` | - | See `DeadZoneBoth`. |
| `ResetSensitivityBothCommand` | `ICommand` | - | See `DeadZoneBoth`. |
| `StopCalibration` | method | - | Stops a running center or boundary calibration. |

### Reset Commands

`ResetAllCommand` (shape, offsets, deadzones, anti-deadzones, linear, speed, curves, ranges, and steering back to their defaults, the boundary map cleared, and any running center or boundary calibration stopped. Momentum keeps its values), `ResetDeadZoneShapeCommand`, `ResetCenterOffsetXCommand`, `ResetCenterOffsetYCommand`, `ResetDeadZoneXCommand`, `ResetDeadZoneYCommand`, `ResetAntiDeadZoneXCommand`, `ResetAntiDeadZoneYCommand`, `ResetLinearCommand`, `ResetStickSensitivityCommand`, `ResetSensitivityXCommand`, `ResetSensitivityYCommand`, `ResetMaxRangeXCommand`, `ResetMaxRangeYCommand`, `ResetMaxRangeXNegCommand`, `ResetMaxRangeYNegCommand`, `ResetSteeringModeCommand`, `ResetWindRangeCommand`, `ResetWindPowerCommand`, `ResetWindUnwindRateCommand`, `ResetAngleInnerDzCommand`, `ResetAngleOuterDzCommand`

### Static Methods

| Method | Description |
|--------|-------------|
| `ApplyCurve(double, string)` | Internal. Applies the spline LUT curve to a magnitude. Used by the preview and Extended processing. |

---

## TriggerConfigItem

**File:** `TriggerConfigItem.cs`

One trigger card in the Triggers group. Gamepad presets: 0 = Left, 1 = Right. Custom Extended: 0..N per `TriggerCount`.

### Identity

| Property | Type | Description |
|----------|------|-------------|
| `Title` | `string` | Display title (e.g., `"Left Trigger"`, `"Trigger 1"`). Read-only. |
| `Index` | `int` | Trigger index (0-based). Read-only. |
| `AxisIndex` | `int` | Raw axis index in `RawHidState.Axes` (custom Extended only, -1 for gamepad). Read-only. |

### Configuration

All percentage properties clamped to 0–100 (except `MaxRange`: 1–100). Each has a `*Digit` companion for digit-based binding (unsigned 16-bit: 0–65535).

| Property (%) | Digit Property | Default | Description |
|--------------|----------------|---------|-------------|
| `DeadZone` | `DeadZoneDigit` | `0` | Deadzone %. |
| `MaxRange` | `MaxRangeDigit` | `100` | Max range % (1–100). |
| `AntiDeadZone` | `AntiDeadZoneDigit` | `0` | Anti-deadzone %. |

### Sensitivity Curve

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `SensitivityCurve` | `string` | `"0,0;1,1"` | Sensitivity curve (control point string). |
| `PresetName` | `string` | - | Computed: matched preset name for the curve. |

| Static | Description |
|--------|-------------|
| `CurvePresetNames` | `string[]` of available curve preset display names. Rebuilt on culture change. `CurvePresetChoices` is its instance accessor for XAML. |

### Live Preview

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `LiveValue` | `double` | `0` | Processed trigger value (0.0–1.0). |
| `RawValue` | `ushort` | `0` | Processed raw value. Notifies `RawDisplay`. |
| `RawDisplay` | `string` | - | Computed: formatted display `"32768 (50.0%)"`. |
| `LiveInputForCurve` | `double` | `0` | Live input for CurveEditor binding. |
| `RawNorm` | `double` | `0` | Raw-stage value (0–1, before the pipeline) for the two-stage bars (#175). |
| `OutDisplay` | `string` | - | Computed: `LiveValue` in the `RawDisplay` format, for the OUT readout. |

### More TriggerConfigItem Members

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `EnsurePresetsCultureCurrent` | method (internal, static) | - | Rebuilds the static preset lists' labels after a language change. |
| `IconLabel` | `string` | - | The label the card's icon carries. Set at construction. |
| `IconRightSide` | `bool` | - | Whether the card's icon is the right trigger's. Set at construction. |
| `ResetAllToolTip` | `string` | - | The card's Reset All tooltip, `Pad_ResetSection_Format` with the card's title. |
| `MoreStateKey` | `string` | - | The key the card's More fold remembers its open state under (`"Pad.Triggers.Trigger{Index}.More"`). |
| `RebuildCurvePoints` | method | - | Rebuilds the curve editor's points from the stored curve. |

### Reset Commands

`ResetAllCommand`, `ResetRangeCommand` (resets DeadZone+MaxRange), `ResetAntiDeadZoneCommand`, `ResetSensitivityCommand`

---

## ExtendedSlotConfig

**File:** `ExtendedSlotConfig.cs`

Per-slot Extended-controller configuration. Drives stick/trigger/POV/button counts, the HID descriptor handed to HIDMaestro for Extended slots, and mapping generation.

| Constant | Value | Description |
|----------|-------|-------------|
| `MaxAxes` | `8` | DirectInput max axis count (shared between sticks and triggers). |

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `Customize` | `bool` | `false` | - | Master toggle for the override fields. When `false`, the VC is built from the catalog HM profile with no customizations (Product String, layout counts, OEM-name override are ignored even if they hold values). When `true`, each sub-field is applied on top of the catalog profile via `HMProfileBuilder`. |
| `ThumbstickCount` | `int` | `2` | 0–`(MaxAxes - TriggerCount) / 2` | Thumbsticks (2 axes each). Applied only when `Customize` is true. |
| `TriggerCount` | `int` | `2` | 0–`MaxAxes - ThumbstickCount * 2` | Triggers (1 axis each). Applied only when `Customize` is true. |
| `PovCount` | `int` | `1` | 0–4 | POV hat switches. Applied only when `Customize` is true. |
| `ButtonCount` | `int` | `11` | 0–128 | Buttons. Applied only when `Customize` is true. |
| `TotalAxes` | `int` | - | - | Computed: `ThumbstickCount * 2 + TriggerCount` (max 8). |
| `MaxThumbsticks` | `int` | - | - | Computed: max sticks given current triggers. |
| `MaxTriggers` | `int` | - | - | Computed: max triggers given current sticks. |
| `OemNameOverride` | `bool` | `false` | - | Whether this slot claims the Windows DirectInput OEM-name table entry for its profile's VID:PID at create time, using `ProductString` as the label. Customize-gated. |
| `ProductString` | `string` | `""` | - | Custom product string applied to the HID descriptor when `Customize` is true. |
| `VendorId` | `int` | `0` | - | VID override. `0` means "use the active profile's VID" (the box then shows the profile value). Customize-gated. Applied at profile-build time via `HMProfileBuilder.Vid`. |
| `ProductId` | `int` | `0` | - | PID override. `0` means "use the active profile's PID". Customize-gated. Applied via `HMProfileBuilder.Pid`. |
| `ForceFeedbackEnabled` | `bool` | `true` | - | Whether the HID PID 1.0 force-feedback block is appended to the descriptor. Customize-gated. Toggling on a live VC forces a destroy + recreate because HIDMaestro bakes the descriptor at create time. |

| Method | Description |
|--------|-------------|
| `ComputeAxisLayout(out int[], out int[], out int[])` | Computes interleaved axis indices per group. |
| `ResetToDefaults()` | Resets every field to its fresh-install default in place. Never replaces the instance (MainWindow's autosave hook binds to this object's `PropertyChanged`). Triggers drop to `0` first so the stick default isn't clamped away by the shared-axis budget. |

The v2 `ExtendedPreset` enum (`Xbox360` / `DualShock4` / `Custom`) and the `ApplyPresetDefaults()` method that paired with it were dropped in v3 (commit `824b4224`). v3 picks layouts from HIDMaestro.Core's embedded catalog instead. HIDMaestro 2.3.0 ships 344 profiles in 60 vendor folders, and PadForge's pickers offer 246 of the 247 that can be deployed (`HMaestroProfileCatalog` keeps only `IsDeployable` profiles and withholds the GameCube adapter's Full persona). `Customize` is the single boolean that gates user overrides on top of the catalog profile.

### ExtendedSlotConfigData

Serializable DTO for persisting in PadForge.xml. All properties have `[XmlAttribute]`.

| Property | Type | Default |
|----------|------|---------|
| `SlotIndex` | `int` | `0` |
| `Customize` | `bool` | `false` |
| `ThumbstickCount` | `int` | `2` |
| `TriggerCount` | `int` | `2` |
| `PovCount` | `int` | `1` |
| `ButtonCount` | `int` | `11` |
| `OemNameOverride` | `bool` | `false` |
| `ProductString` | `string` | `""` |
| `VendorId` | `int` | `0` |
| `ProductId` | `int` | `0` |
| `ForceFeedbackEnabled` | `bool` | `true` |

`VendorId` / `ProductId` default to `0`, meaning "use the active profile's VID/PID" (no override).

`ForceFeedbackEnabled` defaults to `true` so v3.0.0/v3.0.1/v3.0.2 PadForge.xml files (which never wrote this attribute) deserialize with FFB enabled. Customize-gated like the layout overrides: only honored when `Customize == true`.

Older PadForge.xml files written by v2 contained a `Preset` attribute (`Xbox360` / `DualShock4` / `Custom`). v3 ignores it on read since the `ExtendedPreset` enum was removed in commit `d57a725`. Equivalent layouts in v3 come from the active HIDMaestro profile.

---

## MidiSlotConfig

**File:** `MidiSlotConfig.cs`

Per-slot MIDI output configuration: CC/note counts, starting numbers, channel, velocity, and the legacy API's output port.

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `Channel` | `int` | `1` | 1–16 | MIDI channel (1-based). |
| `CcCount` | `int` | `6` | 0–`128 - StartCc` | CC output count. |
| `StartCc` | `int` | `1` | 0–127 | Starting CC number. Re-clamps `CcCount`. |
| `NoteCount` | `int` | `11` | 0–`128 - StartNote` | Note output count. |
| `StartNote` | `int` | `60` | 0–127 | Starting note number. Re-clamps `NoteCount`. |
| `Velocity` | `byte` | `127` | 1–127 | Note velocity for button presses. A 0 reads as 1, because a Note On with velocity 0 is a Note Off. |
| `OutputPort` | `string` | `""` | A port name | The output port the slot sends to under the legacy MIDI API, by the name the slot's port picker shows. Empty for **None**, and until the user picks one. The Windows MIDI Services APIs create the slot's own port and ignore it. |
| `OutputPortChosen` | `bool` | `false` | - | Whether `OutputPort`, **None** included, is a choice for the profile in use: picked or reset in the slot's port picker, or applied from a snapshot that carries one. |
| `OutputPortSnapshot` | `string` | - | - | Computed: the port as a snapshot records it. `OutputPort` while `OutputPortChosen`, else `null`. |

| Method | Description |
|--------|-------------|
| `GetCcNumbers()` | Returns `int[]` of sequential CC numbers from `StartCc`. |
| `GetNoteNumbers()` | Returns `int[]` of sequential note numbers from `StartNote`. |
| `ChooseOutputPort(string)` | Makes a port the slot's port as the user's choice: sets `OutputPort`, empty for **None**, and `OutputPortChosen`. |
| `ResetToDefaults()` | Resets every field in place, starts before counts so the count clamps see the default starts. Clears `OutputPort` and `OutputPortChosen`. |

`PitchName(int)` (static) names a note's pitch as the picture's keys and the bar under the picture do: 60 is C4. Null for a number that is no MIDI note.

### MidiSlotConfigData

Serializable DTO. All properties have `[XmlAttribute]`.

| Property | Type | Default |
|----------|------|---------|
| `SlotIndex` | `int` | `0` |
| `Channel` | `int` | `1` |
| `CcCount` | `int` | `6` |
| `StartCc` | `int` | `1` |
| `NoteCount` | `int` | `11` |
| `StartNote` | `int` | `60` |
| `Velocity` | `byte` | `127` |
| `OutputPort` | `string` | `null` |

`OutputPort` is written whenever the snapshot records a choice, **None** as an empty attribute, and left out when it records none (`ShouldSerializeOutputPort`). `ApplyOutputPortTo(MidiSlotConfig)` applies a recorded choice through `ChooseOutputPort`. A snapshot with no choice keeps the slot's current port and clears `OutputPortChosen`, so a snapshot saved before a port was picked keeps the slot's port.

---

## DeviceSlotConfig

**File:** `DeviceSlotConfig.cs`

Per-(slot, device) output configuration. Renamed from `PlayStationSlotConfig` in commit `3fd97c89`. It is not PlayStation-only. Drives the Adaptive Triggers and Lighting groups, the Lighting group of a lit mouse, keyboard or vendor row included (#494). Held per physical device on a slot (`PadViewModel.PerDeviceSlotConfigs`), so two devices on one slot each carry their own config. Parallel to `ExtendedSlotConfig` and `MidiSlotConfig`: `ObservableObject` with a paired `[XmlAttribute]` data record.

### Adaptive Triggers (per trigger)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `LeftTriggerMode` / `RightTriggerMode` | `AdaptiveTriggerMode` | `Off` | Effect mode. Off reverts to the standard linear response. |
| `LeftStartPosition` / `RightStartPosition` | `byte` | `0` | Start of the pull range the effect targets. |
| `LeftEndPosition` / `RightEndPosition` | `byte` | `255` | End of the pull range (full travel). |
| `LeftStrength` / `RightStrength` | `byte` | `200` | Effect force (0–255). |
| `LeftFrequency` / `RightFrequency` | `byte` | `10` | Vibration frequency for the Vibration modes. |

### Lightbar base color

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `LightbarRed` / `LightbarGreen` | `byte` | `0` | Base RGB red / green channel. |
| `LightbarBlue` | `byte` | `0xFF` | Base blue channel. Fresh slot lights blue (Sony player-1 color). |
| `LightbarEnabled` | `bool` | `false` | Legacy toggle kept for XML round-trip. Nothing reads it at runtime. On a save with `LightingRev` 0 whose `LightbarMode` is Off and whose `AudioLightbarEnabled` is false, true migrates to `LightbarMode.Static` on load. |

### Audio mirror / speaker passthrough (#83)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `AudioPassthroughEnabled` | `bool` | `false` | Mirror the system audio to this pad's built-in speaker (per device). |
| `AudioMirrorSourceId` | `string` | `""` | MMDevice ID of the render endpoint to capture. Empty = the system default. |

### Synthetic touchpad pressure (#239)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TouchpadSyntheticPressure` | `bool` | `false` | Synthesize a pressure reading on pads whose hardware reports none (DualShock 4, DualSense, Steam Controller 2015). No touch reads 0, a resting touch reads `TouchpadSyntheticTouchPercent`, a pad click reads 100%. Valve pads with true analog pressure keep their raw readings while this is off. |
| `TouchpadSyntheticTouchPercent` | `int` | `50` | The touch stop of that curve, percent of full pressure a resting unclicked touch reads. Clamped 0-100. |

### Haptic mirror engage gate (#185)

Applies to haptic-tone sinks only (Joy-Con, Switch Pro, Steam family). Sony/Wii speaker mirrors stay ungated.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `AudioMirrorEngageMode` | `string` | `"Always"` | `Always`, `Input` (while an input is held), or `Rumble` (while game vibration is active). |
| `AudioMirrorEngageDeviceGuid` | `string` | `""` | Device carrying the engage input for Input mode. |
| `AudioMirrorEngageButton` | `string` | `""` | Input descriptor held to engage in Input mode. |
| `AudioMirrorEngageReleaseMs` | `int` | `500` | How long the mirror keeps playing after the engage source drops (ms). |

### High-tone filter (#202)

Filters the single (pitch, amplitude) pair the haptic-tone sinks reduce everything to, upstream of every family encoder.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `AudioToneFilterMode` | `string` | `"Off"` | `Off`, `Cut` (silence above the limit), or `Fold` (octave-halve into the pass band). |
| `AudioToneLimitHz` | `int` | `800` | Ceiling for Cut / Fold in Hz. |

### Persona haptics (#271 item 1)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `AudioPersonaHapticsEnabled` | `bool` | `false` | Render the virtual DualSense's authored haptic audio (persona UAC channels 3/4) on this device's actuators through the haptic-tone chain. Off by default because the derived tones only approximate the designer's track. While it is off the device takes the track as rumble instead (`PersonaHapticRumble`, #522). |
| `AudioPersonaHapticsGain` | `int` | `100` | Input gain percent (25–300) applied before the tone reducer, so a quiet authored track can still reach the actuators. |

Reset commands: `ResetPersonaHapticsCommand`, `ResetPersonaHapticsGainCommand` (both on `PadViewModel`, alongside the Audio group's other row resets).

### Steam Controller 2026 PCM haptics (#381)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `AudioTritonLowPassHz` | `int` | `250` | Low-pass cutoff in Hz for the Steam Controller 2026 PCM haptic stream, clamped 60-1000. Past roughly 250 Hz the pad's actuators start behaving like small speakers. 250 is one requester's hardware-measured threshold on their own unit, not a device specification, which is why it stays tunable. |

### Audio DSP chain (#347)

Per (slot, device) like the rest of the bag, never gated on OutputType. The chain runs on the `AudioPassthroughService` sink only, upstream of the Opus encoder. Edited from the `PadViewModel.AudioDsp.cs` cards.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `AudioCrossfeedLevel` | `int` | `0` | bs2b crossfeed level, clamped 0–9: 0 off, 1–3 crossfeed, 4–6 easy crossfeed, 7 Jan Meier, 8 the bs2b default, 9 custom. Skipped on the speaker paths, which carry a mono downmix. |
| `AudioCrossfeedIsCustom` | `bool` | - | Computed: level 9. Shows the two custom knobs. |
| `AudioCrossfeedCutHz` | `int` | `700` | Custom crossover cutoff, clamped 300–2000 (libbs2b's BS2B_MINFCUT / BS2B_MAXFCUT). |
| `AudioCrossfeedFeedDb` | `double` | `4.5` | Custom feed level in dB, clamped 1.0–15.0 (libbs2b's BS2B_MINFEED / BS2B_MAXFEED in tenths). |
| `AudioEqEnabled` | `bool` | `false` | Master switch for the parametric EQ, separate from an empty band list so a tuned EQ can be muted without being lost. |
| `AudioEqBands` | `string` | `""` | The band list as one attribute encoded by `EqBandCodec`, bridged to grid rows by `PadViewModel.AudioDsp.cs`. |
| `AudioEqPreampDb` | `double` | `0` | Preamp in dB applied before the EQ, clamped −30..12. AutoEq imports carry their negative preamp through here. |
| `AudioLimiterEnabled` | `bool` | `true` | On by default, since a positive EQ band without a limiter clips the Opus encoder. |
| `AudioLimiterCeiling` | `int` | `98` | Ceiling as a percent of full scale, clamped 5–100. |

### Headphone jack and audio path

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `HeadphoneVolume` | `int` | `100` | Headphone-jack hardware volume percent, clamped 0–100. Maps onto the DS5 output report's VolumeHeadphones byte over Sony's own scePad window. `0%` writes `0x00`. Owned by the Audio group's card and the `HeadphoneVolumeUp` / `HeadphoneVolumeDown` macro actions. On a Bluetooth DualShock 4 (#528) the same percent maps onto 0x00 to 0x4F for its left and right headphone bytes. |
| `AudioOutputPath` | `AudioOutputPath` | `Automatic` | Where the DualSense plays its audio (output report byte 7 bits 4–5). On a Bluetooth DualShock 4 (#528) it picks the stream's target, 0x24 for the two headphone routes and 0x02 otherwise, and which output's volume the route mutes. |
| `Ds5AudioBufferLength` | `int` | `48` | DualSense Bluetooth audio buffer length (#314): the packet 0x11 header byte governing the transport that carries speaker audio, haptics, and microphone capture together. Clamped 16–255, defaulting to `AudioPassthroughService.Ds5AudioBufferLengthDefault`. Lower is less delay and more dropout risk. |

| Command | Description |
|---------|-------------|
| `ResetHeadphoneVolumeCommand` | Back to 100. |
| `ResetDs5AudioBufferLengthCommand` | Back to the 48 default. |
| `ResetAudioOutputPathCommand` | Back to `Automatic`. |

### Macro lightbar override (#63)

Transient runtime state set by `MacroActionType.LightbarColor`. Not persisted (`[XmlIgnore]`).

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `MacroOverrideR` / `MacroOverrideG` / `MacroOverrideB` | `byte` | `0` | Override RGB. |
| `MacroOverrideStartUtc` / `MacroOverrideHoldEndUtc` / `MacroOverrideExpiresAtUtc` | `DateTime` | `MinValue` | Hold window bounds. Full intensity over [Start, HoldEnd], linear fade to 0 over [HoldEnd, Expires]. |
| `MacroOverrideHoldMode` | `MacroLightbarHoldMode` | `Reactive` | Reactive (decay-fade) or Sticky (held until cleared). |
| `HasActiveMacroLightbarOverride` | `bool` | - | Computed: `UtcNow < ExpiresAtUtc`. |
| `ComputeMacroOverrideIntensity()` | method | - | 0..1 scalar for the override RGB. 1.0 for Sticky. Ramps for Reactive. |
| `ClearMacroOverride()` | method | - | Releases the active override, Sticky or Reactive. Drives the `LightbarColorClear` macro action. |

### Mic LED

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `MicLedMode` | `MicLedMode` | `Off` | Mic-mute LED state. Notifies `IsMicLedFollowDevice`. |
| `MicLedFollowDeviceId` | `string` | `""` | CoreAudio endpoint id polled by `FollowDeviceMute`. The only name the class's `ResetSettingCommand` accepts. |
| `IsMicLedFollowDevice` | `bool` | - | Computed: mode is `FollowDeviceMute`. |
| `MicLightOn` | `bool` | - | Legacy XML shim over `MicLedMode` (true = Solid, false = Off). |
| `MicLedAvailableDevices` | `List<MicLedDeviceItem>` | - | Endpoints for the follow-device dropdown. `RefreshMicLedDevices()` re-enumerates. |

### Player LEDs (#191)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `PlayerLedMode` | `PlayerLedMode` | `PlayerNumber` | Bottom-row player pips. PlayerNumber idles on the virtual controller's number. |
| `PlayerLedBrightness` | `PlayerLedBrightness` | `High` | Pip brightness (byte 42). |

### Guide LED (#209)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `GuideLedMode` | `GuideLedMode` | `DeviceDefault` | DeviceDefault never writes, Fixed holds `GuideLedBrightness`, Battery re-maps battery percent to brightness on a slow cadence with a floor of 10 so a low battery stays visible. Xbox One and later pads take the GIP LED command over `\\.\XboxGIP` (USB only, `XboxGipGuideLedWriter`). The 2015 Steam Controller takes SDL's process-global home-LED hint (`SteamHomeLedSetter`). Switch Pro Controllers, right Joy-Cons, the combined pair, and the charging grip take per-device `SDL_SetJoystickLED` (`SwitchHomeLedSetter`, #226). Notifies `IsGuideLedFixed`. |
| `IsGuideLedFixed` | `bool` | - | Computed: mode is `Fixed`. Gates the brightness slider. |
| `GuideLedBrightness` | `int` | `100` | Fixed-mode brightness percent. Clamped 0–100. Writers scale it onto each device's own range: 0-47 for GIP per MS-GIPUSB, 0..1 for the SDL hint, and a 4-bit subcommand 0x38 intensity for the Switch home LED. |

### Lightbar mode and animation

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `LightbarMode` | `LightbarMode` | `PlayerNumber` | Base lightbar effect. Off, Static, PlayerNumber, and Battery leave the dispatcher's 33 ms animation timer parked, and Battery repaints when the battery percent changes. The animated modes (Breathing, Strobe, Rainbow, Color Cycle, Screen Color and the audio modes) run the timer, as does any input-reactive overlay or Reactive macro override. |
| `InputReactiveMode` | `InputReactiveMode` | `Off` | Per-press flash overlay on top of the base mode. Notifies `IsInputReactiveActive`, `ShowPaletteForBase`, `ShowPaletteForOverlay`, `IsInputReactiveFixed`. |
| `InputReactiveR` / `G` / `B` | `byte` | `0xFF` | Per-press flash color for the Fixed overlay variant. |
| `LightbarPeriodMs` | `int` | `3000` | Animation period for time-based modes. Clamped 250–10000. |
| `LightbarColorCycleSmooth` | `bool` | `true` | ColorCycle blends between palette entries when true. |
| `LightbarRainbowBrightness` | `int` | `100` | Rainbow output scale. Clamped 0–100. |
| `LightbarBatteryLowR/G/B` | `byte` | red | Battery-mode 0% endpoint color (default red). |
| `LightbarBatteryHighR/G/B` | `byte` | green | Battery-mode 100% endpoint color (default green). |
| `LightbarInputHoldMs` | `int` | `0` | Input-reactive full-intensity hold before decay. |
| `LightbarInputDecayMs` | `int` | `600` | Input-reactive decay length. |
| `LightbarPalette` | `ObservableCollection<LightbarPaletteEntry>` | - | ColorCycle palette. Add / Remove / Reset commands. |
| `LightbarInputReactivePalette` | `ObservableCollection<LightbarPaletteEntry>` | - | Dedicated palette for the InputReactive = Cycle overlay. |

### Peripheral lighting (#494)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `PeripheralLightingEnabled` | `bool` | `false` | The Lighting group's Control This Device’s Lighting switch (`DeviceSlotConfig.cs` line 1003). On, this virtual controller lights a mouse or keyboard with the modes above, and the slot's effects dispatcher holds a lighting claim on the device. Off, the dispatcher releases this slot's claim, so the color comes from another virtual controller that lights the device, a vendor row, another device of its kind on a shared path, or the device's own software. A Set Chroma Color macro on this virtual controller still paints a Razer device. Off by default, so assigning a keyboard for its keys never repaints it. The vendor lighting rows and the unit rows ignore it, since lighting is all they carry. A change re-checks the dispatcher's animation timer. |
| `PeripheralClaimLevel` | `PeripheralClaimLevel` | `Colors` | The Lighting group's Lighting Hold under that switch, for the same (virtual controller, device) pair: how firmly this controller may hold the device while it lights it. `Colors` (0) takes the colors alone, `Power` (1) the device's lighting power too, so it stops dimming its lights by itself, and `HostMode` (2) its on-board memory mode as well, so the profile saved on the device does not apply while it is lit. The number is the hold a lighting claim carries (`PeripheralOutputs.SetLighting`) and the option's place in the picker, so a member is appended and never renumbered. The saved form is the name. A value the enum does not name leaves the property as it was. Only a device that offers a hold shows the picker, and a worker holds a device at no more than it offers. A vendor row and a unit row ask for colors alone |

`ResetPeripheralLightingEnabledCommand` turns the switch back off, and `ResetPeripheralClaimLevelCommand` puts the hold back at `Colors`. `PeripheralLightingClaim(out level)` reads the switch and the hold together from one field, for the dispatcher, whose pass can run on its timer's thread while a load writes the two one after the other.

### Screen Color (#559)

The settings of `LightbarMode.ScreenColor`, per (slot, device) like the rest of the Lighting group. See [Screen Color Internals](screen-color-internals.md). `UserEffectsDispatcher` reads them through `ScreenColorSource.PictureFor(devCfg)`. The dispatcher treats the mode as animated, so its timer runs while the mode is the base mode. With `ScreenColorSpread` on and nothing covering the base mode (no game lightbar, game mod color, macro color or overlay), the picture reaches `PeripheralOutputs.SetLighting` as a `KeyFrame` picture so each light takes its own color.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ScreenColorDisplay` | `string` | `""` | The display to read, by device name. Empty is the primary display. Null writes empty. |
| `ScreenColorArea` | `ScreenColorArea` | `WholeScreen` | The part of the display read. |
| `ScreenColorLeft` / `ScreenColorTop` | `int` | `25` / `25` | Custom area's left and top edge, percent of the display. Clamped 0-99. |
| `ScreenColorWidth` / `ScreenColorHeight` | `int` | `50` / `50` | Custom area's size, percent. Clamped 1-100. |
| `ScreenColorMethod` | `ScreenColorMethod` | `MostCommon` | How the area reduces to a color. |
| `ScreenColorSaturation` | `int` | `100` | Percent. Clamped 0-200. |
| `ScreenColorBrightness` | `int` | `100` | Percent. Clamped 0-100. |
| `ScreenColorSmoothing` | `int` | `30` | Percent. Clamped 0-100. |
| `ScreenColorSpread` | `bool` | `true` | On a per-light device, each light takes the color of its place in a picture of the chosen area (`ScreenColorSource.PictureFor`), in place of one color for the whole device. |

Every property has a `ResetScreenColor<Name>Command`, and the reset-all path writes the defaults above. All ride `DeviceSlotConfigData` as `[XmlAttribute]`s.

### Key lighting and LED strips (#557)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `KeyLighting` | `string` | `""` | The Lighting group's Key Colors for this device on this controller, one block per shift layer (`KeyLightingSettings`). The setter parses and re-formats the text, so equal settings compare equal, publishes the parsed copy with `Volatile.Write`, and only then raises the change. `ResetKeyLightingCommand` clears it. |
| `KeyLightingParsed` | `KeyLightingSettings` | `Empty` | Internal. The parsed copy, read with `Volatile.Read` by the dispatcher thread. |
| `LedStripCounts` | `string` | `""` | How many LEDs each strip of the device has, for devices that drive strips of a length only the user knows (`LightMap.Strips`). Parsed and formatted through `StripCounts`, with the same publish order. `ResetLedStripCountsCommand` clears it. |
| `LedStripCountsParsed` / `SetLedStripCount(number, count)` | `IReadOnlyList<int>` / method | `StripCounts.None` | Internal. The parsed counts, and a write of one strip's count back through the formatted text. |

The dispatcher passes `LedStripCountsParsed` and the key frame to `PeripheralOutputs.SetLighting`. `KeyColorsCardViewModel` and `LedStripsCardViewModel` edit these two properties.

### Audio-to-lightbar (#55)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `AudioLightbarEnabled` | `bool` | `false` | Legacy toggle (migrated into `LightbarMode` on load). |
| `AudioLightbarSensitivity` | `double` | `4.0` | Pre-clamp gain on the audio peak. Clamped 1–20. |
| `AudioLightbarMode` | `AudioLightbarMode` | `Pulse` | Pulse / Thresholds / Gradient / CrossFade behavior. |
| `AudioLowR/G/B` | `byte` | green | Quiet-band color. |
| `AudioMidR/G/B` | `byte` | yellow | Mid-band color. |
| `AudioHighR/G/B` | `byte` | red | Loud-band color. |
| `AudioLowToMidPercent` | `double` | `33` | Low→Mid threshold. Clamped 0–100. |
| `AudioMidToHighPercent` | `double` | `66` | Mid→High threshold. Clamped 0–100. |
| `AudioCrossFadePercent` | `double` | `5.0` | Half-width of the crossfade window around each threshold. Clamped 0–50. |

Each control has a matching `Reset…Command` (mirroring the Sticks / Triggers per-row reset pattern), plus the palette add/remove commands `AddPaletteColorCommand`, `RemovePaletteColorCommand`, `AddInputReactivePaletteColorCommand`, `RemoveInputReactivePaletteColorCommand`, `ResetInputReactivePaletteCommand`, `ResetPaletteCommand`.

### Palette Snapshots and Reset Commands

`SnapshotLightbarPalette()` returns a copy of the palette's colors under the palette's lock, so a timer-thread reader cannot tear a read while the UI thread adds or removes an entry, and `ReplaceLightbarPalette(entries)` swaps the contents under the same lock when a saved config loads. `SnapshotLightbarInputReactivePalette()` and `ReplaceLightbarInputReactivePalette(entries)` do the same for the input-reactive palette.

Each row of the Lighting, Adaptive Triggers and Screen Color cards has a reset that puts its default back, and each card has a Reset All: `ResetLeftTriggerCommand`, `ResetRightTriggerCommand`, `ResetAdaptiveTriggersCommand`, `ResetLeftRangeCommand`, `ResetRightRangeCommand`, `ResetLeftStrengthCommand`, `ResetRightStrengthCommand`, `ResetLeftFrequencyCommand`, `ResetRightFrequencyCommand`, `ApplyLeftGameCubePresetCommand`, `ApplyRightGameCubePresetCommand`, `ResetLightbarAllCommand`, `ResetIndicatorLedsAllCommand`, `ResetLightbarRedCommand`, `ResetLightbarGreenCommand`, `ResetLightbarBlueCommand`, `ResetAudioLowRCommand`, `ResetAudioLowGCommand`, `ResetAudioLowBCommand`, `ResetAudioMidRCommand`, `ResetAudioMidGCommand`, `ResetAudioMidBCommand`, `ResetAudioHighRCommand`, `ResetAudioHighGCommand`, `ResetAudioHighBCommand`, `ResetLightbarModeCommand`, `ResetInputReactiveModeCommand`, `ResetInputReactiveRCommand`, `ResetInputReactiveGCommand`, `ResetInputReactiveBCommand`, `ResetPlayerLedBrightnessCommand`, `ResetPlayerLedModeCommand`, `ResetMicLedModeCommand`, `ResetGuideLedAllCommand`, `ResetGuideLedModeCommand`, `ResetGuideLedBrightnessCommand`, `ResetLightbarPeriodCommand`, `ResetLightbarRainbowBrightnessCommand`, `ResetScreenColorDisplayCommand`, `ResetScreenColorAreaCommand`, `ResetScreenColorLeftCommand`, `ResetScreenColorTopCommand`, `ResetScreenColorWidthCommand`, `ResetScreenColorHeightCommand`, `ResetScreenColorSpreadCommand`, `ResetScreenColorMethodCommand`, `ResetScreenColorSaturationCommand`, `ResetScreenColorBrightnessCommand`, `ResetScreenColorSmoothingCommand`, `ResetLightbarBatteryLowRCommand`, `ResetLightbarBatteryLowGCommand`, `ResetLightbarBatteryLowBCommand`, `ResetLightbarBatteryHighRCommand`, `ResetLightbarBatteryHighGCommand`, `ResetLightbarBatteryHighBCommand`, `ResetLightbarInputHoldCommand`, `ResetLightbarInputDecayCommand`, `ResetLightbarColorCycleSmoothCommand`, `ResetAudioLightbarSensitivityCommand`, `ResetAudioLowToMidPercentCommand`, `ResetAudioMidToHighPercentCommand`, `ResetAudioCrossFadePercentCommand`. `ApplyLeftGameCubePresetCommand` and `ApplyRightGameCubePresetCommand` set a trigger's start and end positions to the GameCube preset's (`0x90` and `0xA0`, among its values). `ResetSettingCommand` and `CanResetSetting` are the generic per-setting reset.

### Enums and helper classes (DeviceSlotConfig.cs)

**AdaptiveTriggerMode:** `Off`(0), `Feedback`(1), `Weapon`(2), `Vibration`(3), `MultiplePositionFeedback`(4), `SlopeFeedback`(5), `MultiplePositionVibration`(6). Sony's seven PS5 SDK effect modes.

**AudioOutputPath:** `Automatic`(0), `StereoHeadset`(1), `MonoHeadset`(2), `HeadsetAndSpeaker`(3), `SpeakerOnly`(4), `FollowHeadphoneJack`(5). Values 1–4 map to firmware paths 0–3, the four names in duaLib's scePad surface. `Automatic` writes nothing and keeps the #83 behavior: firmware routing, with PadForge forcing the speaker only while it plays sounds there. `FollowHeadphoneJack` tracks the pad's own jack detect. The jack bit is read by `AudioPassthroughService`'s sink-owned `JackWatch` on either transport (USB input report 0x01 or Bluetooth 0x31, the duaLib PluggedHeadphones status bit), and on a Bluetooth DualShock 4 from bit 5 of the status byte at offset 32 (#528), independent of any persona lane. Plugged resolves to `StereoHeadset`, unplugged to `SpeakerOnly`, and no reading to the default. Persisted numerically, so the members are append-only.

**MicLedMode:** `Off`(0), `Solid`(1), `Pulse`(2), `FollowDeviceMute`(3).

**PlayerLedMode:** `Off`(0), `Player1`(1), `Player2`(2), `Player3`(3), `Player4`(4), `All`(5), `PlayerNumber`(6, default). Sequential to map 1:1 with the dropdown.

**PlayerLedBrightness:** `High`(0), `Medium`(1), `Low`(2).

**GuideLedMode** (#209): `DeviceDefault`(0), `Fixed`(1), `Battery`(2).

**LightbarMode:** `Off`(0), `Static`(1), `Breathing`(2), `Rainbow`(3), `ColorCycle`(4), `AudioPulse`(5), `AudioPulseRandom`(6), `AudioPulseRainbow`(7), `AudioThresholds`(8), `AudioGradient`(9), `AudioCrossFade`(10), `InputReactive`(11, legacy), `InputReactiveCycle`(12, legacy), `InputReactiveFixed`(13, legacy), `Battery`(14), `Strobe`(15), `PlayerNumber`(16, default), `ScreenColor`(17, #559). Legacy 11–13 stay in the enum for XML round-trip and are migrated to `InputReactiveMode` on load.

**ScreenColorArea** (#559): `WholeScreen`(0), `TopLeft`(1), `Top`(2), `TopRight`(3), `Left`(4), `Center`(5), `Right`(6), `BottomLeft`(7), `Bottom`(8), `BottomRight`(9), `Custom`(10).

**ScreenColorMethod** (#559): `MostCommon`(0), `Average`(1).

**ScreenDisplayChoice** (#559): a record of `Id` (the display's device name, such as `\\.\DISPLAY2`, empty for the primary display) and `Label`. `ListFor(saved)` builds the picker: the primary entry first, then each display from `System.Windows.Forms.Screen.AllScreens` ordered by display number (the `DisplaysSeam` test seam replaces the source), then a saved display that is no longer present, labeled with `Pad_Lighting_ScreenDisplayGone`.

**InputReactiveMode:** `Off`(0), `Random`(1), `Cycle`(2), `Fixed`(3).

**AudioLightbarMode:** `Pulse`(0), `Thresholds`(1), `Gradient`(2), `CrossFade`(3).

**MicLedDeviceItem:** `Id` (CoreAudio endpoint string), `Display` (label, prefixed `[In]` / `[Out]`).

**LightbarPaletteEntry** (`ObservableObject`): `R`, `G`, `B` (byte), `Hex` (two-way `"RRGGBB"` shim, `[XmlIgnore]`).

### DeviceSlotConfigData

Serializable DTO. All scalar properties are `[XmlAttribute]`. The two palettes are `[XmlArray]`. Key defaults: `LeftEndPosition`/`RightEndPosition` = 255, `LeftStrength`/`RightStrength` = 200, `LeftFrequency`/`RightFrequency` = 10, `LightbarBlue` = 0xFF, `AudioMirrorEngageMode` = "Always", `AudioMirrorEngageReleaseMs` = 500, `AudioToneFilterMode` = "Off", `AudioToneLimitHz` = 800, `TouchpadSyntheticPressure` = false, `TouchpadSyntheticTouchPercent` = 50, `AudioPersonaHapticsEnabled` = false, `AudioPersonaHapticsGain` = 100, `AudioTritonLowPassHz` = 250, `HeadphoneVolume` = 100 (a missing attribute on legacy XML keeps the initializer, so old configs load at full volume, the pre-feature effective behavior), `Ds5AudioBufferLength` = 48, `AudioOutputPath` = Automatic, `AudioCrossfeedLevel` = 0, `AudioCrossfeedCutHz` = 700, `AudioCrossfeedFeedDb` = 4.5, `AudioEqEnabled` = false, `AudioEqBands` = "", `AudioEqPreampDb` = 0, `AudioLimiterEnabled` = true, `AudioLimiterCeiling` = 98, `GuideLedMode` = DeviceDefault, `GuideLedBrightness` = 100, `PeripheralLightingEnabled` = false (#494: a config saved before the switch leaves every mouse and keyboard to its own software), `LightbarMode` = Off (the DTO default, migrated to PlayerNumber via `LightingRev`), `PlayerLedMode` = Off (likewise). It also carries a `DeviceGuid` (per-device key, empty = a legacy slot-level entry the loader fans out) and `LightingRev` (schema revision: 0 predates the PlayerNumber default and triggers the Off→PlayerNumber lift on load). `LightbarPaletteEntryData` is the palette element (`R`, `G`, `B` byte attributes).

---

## KbmSlotConfig

**File:** `KbmSlotConfig.cs`

Per-slot keyboard + mouse output config (discussion #205, SOCD / Snap Tap, plus the #408 surface mode). Same per-slot lane as `MidiSlotConfig`: lives on `PadViewModel.KbmConfig`, referenced into the engine by InputService, persisted as `KbmSlotConfigData`.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Surfaces` | `string` | `"Both"` | Which halves of the slot are live (#408): `Both`, `KeyboardOnly`, or `MouseOnly`. Any other value coerces to `Both`. Turning a half off hides its mapping rows and stops the slot's own keyboard or mouse output for them. The mappings stay on the PadSetting. Macros are not gated. Notifies `KeyboardEnabled` and `MouseEnabled`. |
| `KeyboardEnabled` / `MouseEnabled` | `bool` | - | Computed: the half is live (`Surfaces != "MouseOnly"` / `Surfaces != "KeyboardOnly"`). `Allows(KbmSurfaceKind)` answers the same question for a row's half. |
| `KeyboardDevice` / `MouseDevice` | `string` | `""` (`WindowsInput`) | The HIDMaestro keyboard or mouse profile each half sends through, or the empty string for Windows input. When one changes, a half that rode the old shared device follows to the new one if it carries that half, and goes back to Windows input if it does not. A null write is a picker artifact and is ignored. `SetDevices(keyboard, mouse)` sets both as one change, as a load, a paste or a profile apply does, and `ResetToDefaults()` puts both back on Windows input. See [Virtual keyboards and mice](../features/virtual-controllers.md#virtual-keyboards-and-mice). |
| `AvailableKeyboardDevices` / `AvailableMouseDevices` | `IReadOnlyList<KbmDeviceOption>` | - | The two dropdowns: Windows Input, then the other half's device when it carries this half (Same Device as the Mouse / Keyboard), then every keyboard or mouse profile by name. `KbmDeviceOption` compares by value, so a rebuilt list keeps its selection. |
| `UsesDevices` | `bool` | - | True when either half has a model. `DeviceCanSend(settingName)` answers whether the picked model can send a row's target, and the mapping table hides a row it cannot and keeps the binding. |
| `AvailableKbmSurfaces` | `IReadOnlyList<KbmSurfaceOption>` | - | Culture-cached surface dropdown items, in order: "Keyboard + Mouse" (`Both`), "Mouse Only", "Keyboard Only". |
| `SocdMode` | `string` | `"Off"` | Resolution mode: `Off`, `LastWins`, `Neutral`, `FirstWins`. Stored locale-stable. |
| `SocdPairs` | `string` | `"87:83\|65:68\|38:40\|37:39"` | Pipe-separated `"vkA:vkB"` decimal pairs (the `DefaultSocdPairs` constant: W/S, A/D, Up/Down, Left/Right). |
| `SocdPairItems` | `ObservableCollection<SocdPairItem>` | - | Editable projection of `SocdPairs` for the pair editor. |
| `AvailableSocdModes` | `IReadOnlyList<SocdModeOption>` | - | Culture-cached dropdown items. |

| Constant | Value |
|----------|-------|
| `DefaultSocdPairs` | `"87:83\|65:68\|38:40\|37:39"` |
| `DefaultSurfaces` | `"Both"` |

| Command | Description |
|---------|-------------|
| `AddSocdPairCommand` | Appends a fresh W/S pair. |
| `RemoveSocdPairCommand` | `RelayCommand<SocdPairItem>`. Removes the passed pair. |
| `ResetSocdCommand` | The SOCD card's Reset All (`ResetSocdToDefaults()`): `SocdMode` back to Off and `SocdPairs` to `DefaultSocdPairs` in place. It leaves `Surfaces` alone. |
| `ResetSocdModeCommand` | `SocdMode` back to Off, pairs untouched. |

| Method | Description |
|--------|-------------|
| `ResetToDefaults()` | The whole-slot reset: `Surfaces` back to `Both`, then the SOCD reset. Keeps the instance. |

| Static Method | Description |
|---------------|-------------|
| `GetKeyOptions()` | Culture-cached `SocdKeyOption` list, the same key set and labels as the KBM mapping targets. |

**Companion classes:**
- `SocdModeOption` carries `Value` (engine-stable), `Name`, and `Description`. Localized dropdown entry.
- `KbmSurfaceOption` carries `Value` and `Name`. One surface-mode entry, with no description.
- `KbmSurfaceKind` (enum): `Keyboard`, `Mouse`. The half a mapping row drives, classified by `PadViewModel.KbmSurfaceOf`.
- `SocdKeyOption` carries `Vk` (int) and `Label`. One pickable key.
- `SocdPairItem` (`ObservableObject`) carries `VkA` and `VkB`. Edits reserialize the owner's `SocdPairs`. `KeyOptions` returns `GetKeyOptions()`.
- `KbmSlotConfigData` is the DTO with `[XmlAttribute]` `SlotIndex`, `Surfaces` (default "Both", so files written before #408 read as Both), `SocdMode` (default "Off"), `SocdPairs` (default `DefaultSocdPairs`), and `KeyboardDevice` and `MouseDevice`, written only when set, so a file written before the device pickers reads as Windows input.

---

`SocdSummary` is the SOCD card's value while folded, the mode's name (#574). `RaiseLocalizedChanged()` (internal) rewords the mode names and that value after a language change.

## KeyColorsCardViewModel (#557)

**File:** `KeyColorsCardViewModel.cs`. Implements `IKeyLightsSource`.

The Lighting group's Key Colors card, titled Zone Colors for a device whose lights are zones (`Title` and `Description` read `HasKeys`). It holds the lights of the selected device (`LightMap`), the shift layer being colored, the selection and the color the selection takes. Every change writes straight into the device's `DeviceSlotConfig.KeyLighting`, which saves it and has the dispatcher paint it. `_writing` stops the card from re-reading its own write.

A color goes where it lasts best. A key goes by its HID usage, so the colors carry to any keyboard. A selection that holds every light of a group (all the edge lights, the logo, one zone) colors the group by name. Anything else, a single edge light or a key no source has named, goes by the device's own light number.

| Member | Description |
|--------|-------------|
| `Attach(config, map, layers)` / `Detach()` | Internal. Point the card at a device's config, its `LightMap` and the slot's shift layers (Base first). A new device or map clears the selection and turns Select by Pressing Keys off when the map has no keys. An attach that changes nothing raises nothing. |
| `UpdateLayers(layers)` | Takes the slot's shift layers again after the mapping list added, renamed or removed one, or a language switch rebuilt the layer tabs. |
| `IsVisible` | A config is attached and the map is per-light. |
| `Layers`, `SelectedLayerMask`, `IsBaseLayer`, `HasLayers` | `KeyColorLayerItem` chips (`LayerMask`, `LayerName`, `Color`, `IsBase`, `IsSelected`). The card keeps its own pick, apart from the mapping list's, so choosing a layer to color never changes the layer being mapped. The pick is kept while the layer exists. |
| `BackgroundChoices`, `BackgroundRule` | The Other Lights rule of the layer: `KeyBackgroundRule.BaseLayer` (shift layers only), `Same`, `Off` or `Color`. The choice list is one array for as long as its labels hold, because a ComboBox handed a new list drops its selection and writes the empty selection back. A shift layer shows its own colors over the Base layer's until its rule says otherwise. The picture draws the Base layer's colors on such a layer faded (`BaseColorOf`). |
| `BackgroundRed` / `Green` / `Blue` / `Hex` | The Other Lights color. A hex value that is not six digits, with or without `#`, changes nothing. |
| `PaintRed` / `Green` / `Blue` / `Hex` | The color the selection takes. Setting a channel colors every selected light at once. |
| `PickByPressing` | A key pressed while the picture has focus joins the selection or leaves it (`TogglePressed(usage)`). |
| `HasEdge`, `HasLogo`, `HasKeys`, `HasUnnamedKeys` | Which selection buttons show. `HasUnnamedKeys` is true when keys have no name from any source, which Map Key Lights can supply. |
| Commands | `SelectAllKeysCommand`, `SelectNumberRowCommand`, `SelectFunctionKeysCommand`, `SelectNumberPadCommand`, `SelectArrowsCommand`, `SelectWasdCommand`, `SelectEdgeCommand`, `SelectLogoCommand`, `SelectAllLightsCommand`, `ClearSelectionCommand`, `ClearSelectedColorsCommand`, `ClearLayerCommand`, `ApplyColorCommand`. The key groups are HID usage arrays on the card (`NumberRow`, `FunctionKeys`, `NumberPad`, `Arrows`, `Wasd`). |
| `LightsChanged` | Raised when the selection or a light's color changed, so the picture redraws. |

`IKeyLightsSource` (internal) is what `KeyLightsView` draws and edits: `Map`, `Selection`, `OwnColorOf`, `BaseColorOf`, `BaseLayerName`, `OrderOf`, `LegendOf`, `PickByPressing`, `Toggle`, `SetSelection`, `TogglePressed` and `LightsChanged`. `KeyColorsCardViewModel`, `KeyTargetPickerViewModel` and `MapKeyLightsViewModel` each implement it.

---

**More KeyColorsCardViewModel members:**

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `Config` | `DeviceSlotConfig` (internal) | - | The device the card colors, the one the picture belongs to, or null. |
| `Layer` | `KeyLightingLayer` (internal) | - | The layer being colored as saved, or the empty one it starts as. |
| `BackgroundIsColor` | `bool` | - |  |
| `BackgroundGreen` | `byte` | - |  |
| `BackgroundBlue` | `byte` | - |  |
| `BackgroundHex` | `string` | - | The background color as RRGGBB. A value that is not a six-digit hex color, with or without "#", changes nothing. |
| `HasSelection` | `bool` | - |  |
| `SelectionSummary` | `string` | - |  |
| `PaintGreen` | `byte` | - |  |
| `PaintBlue` | `byte` | - |  |
| `PaintHex` | `string` | - | The selection's color as RRGGBB, for the hex box and the swatches. A value that is not a six-digit hex color, with or without "#", changes nothing. |
| `ColorSelection` | method (internal) | - | Gives every selected light `rgb` on the layer being colored. |
| `ClearSelectedColors` | method (internal) | - | Takes the selected lights' own colors away, so they show what the layer's other lights show. A group the selection holds only part of keeps its color on the lights left out. |
| `ClearLayer` | method (internal) | - | Takes every color off the layer being colored and gives it back the Other Lights rule it starts with. |
| `TryHex` | method (internal, static) | - | RRGGBB or #RRGGBB, the Lighting tab's hex boxes' rule. |

`BackgroundIsColor` is computed: the Other Lights rule is Color. `BackgroundGreen`, `BackgroundBlue`, `PaintGreen` and `PaintBlue` are the green and blue channels beside the red ones the table above names. `HasSelection` is computed (some light is selected), and `SelectionSummary` says which. `KeyBackgroundChoice` is one entry of the Other Lights picker: `Rule` (`KeyBackgroundRule`) and `Label`.

## KeyTargetPickerViewModel (#557)

**File:** `KeyTargetPickerViewModel.cs`. Implements `IKeyLightsSource`.

The key picker of the Set Key Colors and Clear Key Colors macro actions, over `MacroAction.KeyColorTargets` (`MacroAction.KeyTargetPicker` creates it on first read). A macro names keys by HID usage, so it lights the same keys on any keyboard. The picture is `GenericMap()`: a full-size keyboard (ANSI when the input layout's language id is `0x0409`, ISO otherwise, `KeyboardFamilies.FullsizeAnsi` / `FullsizeIso`), one light each for a device's edge, logo, status and other lights, and a zone for every zone any known device has, at least `MinZones` (4). The picked lights show in the action's color, numbered in the order picked, which is the order a Countdown keeps.

| Member | Description |
|--------|-------------|
| `AllLights` | The action names every light (`all`). Setting it clears the picks. |
| `PickByPressing` | Pick keys by pressing them. |
| `SetSelection(indexes)` | Picks the lights in their given order in place of the old picks. The sequence is read before the picks clear, because a drag hands over the picks followed by the lights it covered. |
| `Reload()` | Reads the action's targets again after it changed other than through the picker. A saved target the picture has no light for is kept in `_unplaced` and written back unchanged. |
| Commands | `SelectAllKeysCommand`, `SelectNumberRowCommand`, `SelectFunctionKeysCommand`, `SelectNumberPadCommand`, `SelectArrowsCommand`, `SelectWasdCommand`, `ClearSelectionCommand`, over the same usage arrays as the card. |

The picker watches the action's `LightbarR`, `LightbarG`, `LightbarB` and `KeyColorStyle` and raises `LightsChanged` so the picture redraws in the new color.

---

`Map` (internal) is the `LightMap` the picker draws.

## MapKeyLightsViewModel (#557)

**File:** `MapKeyLightsViewModel.cs`. Implements `IKeyLightsSource` and `IDisposable`. Backs `MapKeyLightsDialog`.

Map Key Lights names the key each light of a device sits under, for a keyboard whose own description leaves keys unnamed or names one wrong. It lights one key light alone, white over black, ahead of every controller's claim (`PeripheralOutputs.SetProbe(path, KeyFrame)`). The key pressed next names it, found by its scan code. The names are kept for the device's model (`LearnedKeyMaps.Set(product, address, usage, moveFromOthers: true)`), so every unit of the model takes them, and an export carries them to another PC. The constructor reads `PeripheralLightMaps.For(path)`, and `PeripheralLightMaps.Changed` (raised on a backend's thread, marshaled to the dispatcher) swaps in the republished map and re-finds the lit light by its address.

| Member | Description |
|--------|-------------|
| `DeviceName`, `Product` | The row's name and the model the names are kept for. |
| `CanLearn` | The map has a product name and at least one key light. |
| `IsListening`, `Current` | A light is lit (`Current >= 0`). |
| `Progress`, `Status` | How many key lights have a name of how many (`MapKeyLights_Progress_Format`), and what to do now (`MapKeyLights_NoLights`, `MapKeyLights_Ready`, `MapKeyLights_Ask_Format`, `MapKeyLights_AskNamed_Format`). |
| `Start()` | Lights the first key light without a name, or the first key light when every one has a name. |
| `Skip()` | The next unnamed key light after the one lit, or the next key light when every one is named. |
| `Back()` | The key light before the one lit, wrapping. |
| `Stop()` | Lights off, the device back to its claims. |
| `Name(usage)` | Internal. Keeps the name for the light lit, then asks about the next unnamed light, or stops when none is left. A key named for another light moves here, since naming a key again corrects it. |
| `Forget()` / `ForgetAll()` | Forget the name learned for the light lit, or for the whole model. |
| `Choose(usages)` | Internal. Picks among the usages Windows reports for one scan key. Two share `0x2B` (ANSI backslash, ISO key left of Enter): the one the device does not name elsewhere wins, else the input layout decides (`0x0409` takes the first). |
| `Dispose()` | Unsubscribes from `PeripheralLightMaps.Changed` and clears the probe. |

A click or a drag on a key light in the picture asks about that light instead of selecting.

---

**More MapKeyLightsViewModel members:**

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `LightsChanged` | `Action` | - |  |
| `ProgressLead` | `string` | - | The progress line in five parts, so the dialog can set its two numbers in tabular figures: the words before the first number, that number, the words between, the second number and the words after, in the order this language's sentence puts them (#574). |
| `ProgressFirst` | `string` | - |  |
| `ProgressMiddle` | `string` | - |  |
| `ProgressSecond` | `string` | - |  |
| `ProgressTail` | `string` | - |  |

`LightsChanged` is an `Action` the dialog raises when the device's lights changed.

## LedStripsCardViewModel (#557)

**File:** `LedStripsCardViewModel.cs`

The Lighting group's LED Strips card: how many LEDs each strip of the selected device has, for a device that drives strips of a length only its user knows (`LightMap.Strips`). The counts live in `DeviceSlotConfig.LedStripCounts`.

| Member | Description |
|--------|-------------|
| `Rows` | `ObservableCollection<LedStripRow>`, one per strip. |
| `Attach(config, map)` / `Detach()` | Internal. An attach for the same config and the same strips (`Number`, `MaxLeds`) changes nothing. A count that goes out republishes the map and comes back here, so the rows stay and a box being typed in keeps its focus. |

`LedStripRow` exposes `Number`, `Maximum`, `Label` (`Pad_Lighting_LedStrips_Header_Format`, refreshed on `Strings.CultureChanged`), `Leds` (`double?`, rounded and clamped to 0-`Maximum`, null from the box's clear button reads 0, written through `DeviceSlotConfig.SetLedStripCount`) and `ResetCountCommand` (back to 0).

---

## ScreenOverlayItem

Documented under [DashboardViewModel: Screen Overlays](#screen-overlays-560).

---

## Custom Telemetry Format Editor (#531)

**File:** `CustomTelemetryFormatEditor.cs`

The Custom Formats dialog (`CustomTelemetryFormatsDialog`) works on copies and writes the list back only on Save, so Cancel leaves the saved formats as they were. See [Game Telemetry Internals](game-telemetry-internals.md).

| Class | Description |
|-------|-------------|
| `TelemetryFormatEdit` | One format. `Name`, `Kind` (`CustomTelemetryKind`: `IsBinary` or `IsJson`), `Length`, `Key`, `BigEndian`, `UseGearValues` with `GearReverse` and `GearNeutral`, and `Fields` (`ObservableCollection<TelemetryFieldEdit>`). `From(CustomTelemetryFormat)`, `ToModel()` and `Copy(name)` move it to and from the model. `Problem(position)` (internal) returns the first problem that would keep the format from reading, or null: a name `CustomTelemetryFormat.IsValidName` rejects (`Telemetry_Formats_ErrorName_Format`, which names the format's list position when it has no name), a variable field with an invalid name, a JSON field with no key, or a binary field whose offset plus `CustomTelemetryField.SizeOf(Type)` runs past a nonzero `Length`. |
| `TelemetryFieldEdit` | One field row, derives `FiniteObservableObject`, so a number that is not finite leaves its box as it was: NaN by the base's rule, infinity too, since no bound here turns it into a number. `Target` (`CustomTelemetryTarget`, `IsVariable`), `Kind` (the owning format's, which decides whether the row shows an offset and a type or a key), `Name`, `Offset`, `Type` (`CustomTelemetryType`), `Key`, `Scale`, `Min`, `Max`, and `Axis`, the axis the field's variable keeps, carried through the edit unseen so a renamed variable keeps its old name's axis. |
| `TelemetryChoice<T>` | A picker item: `Value` and a `Display` read from a delegate, re-raised by `RaiseDisplayChanged()` on a language change. |
| `TelemetryChoices` | The pickers' lists, shared by the dialog and the tests: `Kinds`, `Targets` and `Types`. The binary types read by the names the C# and Rust references write them in, which no language translates. |

`TelemetryChannelOptions` (`TelemetryChannelOptions.cs`) is the Custom Expression variable's telemetry picker: `Items` is one `ObservableCollection<TelemetryChannelOption>` shared by every variable row, holding the standard channels and then the custom variables of every custom format (`Channel`, `Variable`, `Display` from `TelemetryChannelNames.DisplayName`, `Matches(channel, variable)`). It is rebuilt on the UI thread when the formats change and renamed on a language change. `GameTelemetryOption` (`GameTelemetryOption.cs`) is the Game Telemetry page's picker item, described under [Game Telemetry](#game-telemetry-531).

---

## RemoteLinkTrustedPeer

**File:** `RemoteLinkTrustedPeer.cs`

One trusted peer in the Paired PCs list on the Remote Link page (#138), held by `SettingsViewModel.TrustedPeers`. The name is editable (committed on focus loss, persisted to the trust store). The online dot refreshes in place so editing isn't disrupted.

| Property | Type | Description |
|----------|------|-------------|
| `Name` | `string` | Friendly name. Setting it persists the rename via the callback. Empty falls back to the host name. |
| `HostName` | `string` | The peer's machine (NetBIOS or host) name, shown next to the friendly name. |
| `IsOnline` | `bool` | Live-session state. Notifies `StateText`, `CanConnect`. |
| `StateText` | `string` | Computed: the line under the name on the Remote Link page (#574), connected or offline, and gamepad only when this PC limited it. `RefreshText()` (internal) reads it again after a language change. |
| `ReachableHostPort` | `string` | Where the peer is reachable now (host:port from discovery), or null. Notifies `CanConnect`. |
| `CanConnect` | `bool` | Computed: on the LAN but not connected. Shows the Connect button. |
| `FingerprintHex` | `string` | Full key fingerprint. |
| `FingerprintDisplay` | `string` | Computed: short grouped fingerprint, with a gamepad-only suffix when applicable. |
| `PairedUtc` | `string` | Pairing timestamp. |
| `GamepadOnly` | `bool` | Whether the peer is restricted to gamepad input. |
| `AllowRemoteAssignments` | `bool` | Allow Remote Assignment Changes: this peer may assign the devices it shares to this PC's existing virtual controllers. A change raises the permission callback (`SettingsViewModel.PeerAssignmentPermissionChanged`). Turning it off keeps existing assignments. |

| Command | Description |
|---------|-------------|
| `ConnectCommand` | Reconnect to this known peer (no SAS prompt). |
| `RevokeCommand` | Revoke trust (raises the revoke callback with the fingerprint). |
| `AssignmentsCommand` | Assign Shared Devices, shown while the peer is online. Raises the assignments callback with the fingerprint (`SettingsViewModel.PeerAssignmentsRequested`). |

---

## RemoteLinkNearbyPeer

**File:** `RemoteLinkNearbyPeer.cs`

One PadForge PC discovered on the LAN (#138), shown in the "Nearby PCs" list. Immutable. Clicking Pair initiates pairing without IP typing.

| Property | Type | Description |
|----------|------|-------------|
| `Name` | `string` | Discovered machine name. |
| `HostPort` | `string` | Host:port to pair against. |
| `FingerprintHex` | `string` | The peer's key fingerprint. |
| `IsPaired` | `bool` | Already in the trust store. |
| `IsConnected` | `bool` | A live session already exists. |
| `DisplayName` | `string` | Computed: name with a Connected / Paired state suffix. |
| `ButtonLabel` | `string` | Computed: Connected (disabled) / Connect (paired) / Pair (new). |
| `CanPair` | `bool` | Computed: the action button is enabled unless already connected. |

| Command | Description |
|---------|-------------|
| `PairCommand` | Initiates pairing with `HostPort`. |

---

## See Also

- [Architecture Overview](architecture-overview.md): MVVM design philosophy, `CommunityToolkit.Mvvm` usage
- [XAML Views](xaml-views.md): View counterparts: `HomePage`, `PadPage`, `ExtrasPage`, `DevicesPage`, `ProfilesPage`, `SettingsPage`, `AboutPage`
- [Services Layer](services-layer.md): `InputService`, `SettingsService`, `DeviceService` consumed by ViewModels
- [Engine Library](engine-library.md): `Gamepad`, `RawHidState`, `KbmRawState`, `VrRawState`, `MidiRawState`, `PadSetting`
- [Settings and Serialization](settings-and-serialization.md): `SettingsManager` data synced to/from ViewModels by `SettingsService`
- [Profile Import Internals](profile-import-internals.md): the reWASD and DS4Windows import behind the Profiles page Import button
- [On-Screen Keyboard Internals](on-screen-keyboard-internals.md): the Keyboard menu style that `MenuEditorItem.Keyboard.cs` edits
- [Screen Color Internals](screen-color-internals.md): the lighting mode behind the `ScreenColor*` settings on `DeviceSlotConfig`
- [Twitch Chat Internals](twitch-chat-internals.md): the runtime behind `DashboardViewModel`'s Twitch Chat properties
- [Input Pipeline](input-pipeline.md): `InputManager` state reflected in `PadViewModel` output snapshots
- [2D Overlay System](2d-overlay-system.md): `ControllerModel2DView`, `ControllerSchematicView` bound to `PadViewModel`
- [3D Model System](3d-model-system.md): `ControllerModelView` bound to `PadViewModel`

---

*Last updated for PadForge 6.0.0.*
