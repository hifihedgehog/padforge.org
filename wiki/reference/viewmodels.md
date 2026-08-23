# ViewModels Reference

*Every ViewModel class in PadForge: what it backs, what it exposes, and how state flows between the UI and the services layer.*

> **v4 (2026-07-12):** Refreshed for v4. Remote Link (`DashboardViewModel` + `SettingsViewModel`, and the `RemoteLinkTrustedPeer` / `RemoteLinkNearbyPeer` rows), the per-(slot, device) `DeviceSlotConfig` (renamed from `PlayStationSlotConfig`), `KbmSlotConfig` (SOCD / Snap Tap), multi-source mapping rows (`MappingSourceItem`), the mouse-gesture partial, and the Ember dashboard vocabulary all landed since the v3 rewrite. The HIDMaestro SDK surface, OpenXInput shim, thread-pool lifecycle, and bubble-up cascade live on [HIDMaestro Deep Dive](hidmaestro-deep-dive.md). If anything here drifts from the live source, the live source wins.
>
> **v4.1 (2026-07-30):** The Nintendo output type (#215) joins the family. `PadViewModel` gains the Bass Shakers tab (#236), the slot SOCD card (#240), the flick rotation offset, gyro Acceleration, and the macro Layer dropdown. `MacroItem` carries the #238 / #253 fire-mode wave and per-macro layer scope (#254). Mapping rows and sources gain Flip Output, per-source Acceleration, and the #251 axis-latch macro actions. The Touchpad partial grows the libinput pointer Response, momentum, and pointer-region cards. `DeviceSlotConfig` adds synthetic touch pressure (#239) and the Switch home-LED lane (#226).
>
> **v4.2:** The VR output type (#49) lands as `VirtualControllerType.Vr` (6), with a `VrControllerIcon` sidebar entry, a `VrOutputSnapshot`, and a SteamVR row in both driver-status surfaces (`DashboardViewModel.IsSteamVrInstalled`, plus the install / uninstall pair on `SettingsViewModel`). The pad page grows two slot-tier tabs: Bass Shakers at index 16 and Output at index 17 (SOCD plus Keep Controller Awake). `DeviceSlotConfig` gains headphone-jack volume, the DualSense audio-output path, and persona haptics, with `MacroActionType.HeadphoneVolumeUp` / `HeadphoneVolumeDown` (52 / 53) driving the volume. Sony headset head trackers get their own device class (`HeadsetMotion`, #188). `RawHidState` replaced the old `ExtendedRawState`, so the Extended snapshot is now `RawHidOutputSnapshot`.
>
> **v4.3:** The mapping picker gains one shared per-slot choice list plus a search box and device-visibility filter (#322 / discussion #302), both on `PadViewModel`. Voice macros (#317) add the `"Microphone"` device class, the Voice Macros preview on `DevicesViewModel`, `DeviceRowViewModel.ShowManageVoicePhrases`, and `MacroActionType.VoiceListenWhileHeld` (54). `MacroAction` grows the pressure-scaled turbo block (#290). `StickConfigItem` grows stick trackball momentum (#291), the touchpad partial grows the shared momentum knobs, and `PadViewModel` grows the Gyro Tilt envelope (#292). The Dashboard's web-controller card gains a URL and QR (#296), its SteamVR row goes tiered (#287), and Settings gains the low-battery notification trio (#293).

---

All ViewModels live in `PadForge.App/ViewModels/` (`PadForge.ViewModels` namespace). Built on [CommunityToolkit.Mvvm](https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/) (`ObservableObject`, `RelayCommand`).

---

## ViewModelBase

**File:** `ViewModelBase.cs`

Abstract base class for all ViewModels. Extends `ObservableObject` (`INotifyPropertyChanged`, `SetProperty`).

```csharp
public abstract class ViewModelBase : ObservableObject
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

## NavControllerItemViewModel

**File:** `MainViewModel.cs` (defined alongside MainViewModel)

Sidebar entry for one virtual controller. Shows controller type icon, slot number, and per-type instance label.

| Property | Type | Description |
|----------|------|-------------|
| `PadIndex` | `int` | Zero-based pad slot index (0–15). Read-only. |
| `Tag` | `string` | Navigation tag (`"Pad1"`–`"Pad16"`). Computed as `$"Pad{PadIndex + 1}"`. |
| `SlotNumber` | `int` | 1-based controller number among active slots. |
| `InstanceLabel` | `string` | Per-type instance label (e.g., `"1"`, `"2"`). |
| `IconKey` | `string` | Resource key for controller type icon (e.g., `"XboxControllerIcon"`, `"DS4ControllerIcon"`, `"NintendoControllerIcon"`, `"ExtendedControllerIcon"`, `"MidiControllerIcon"`, `"KeyboardMouseControllerIcon"`, `"VrControllerIcon"`). |
| `IsEnabled` | `bool` | Virtual controller enabled. |
| `ConnectedDeviceCount` | `int` | Mapped physical devices connected. |
| `MappedDeviceCount` | `int` | Physical devices assigned to this slot in config, connected or not. Lets the mini card split "assigned but awaiting" (idle) from "nothing assigned" (cold), the same split the Dashboard card makes. Added by commit `2006ac6b`. |
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
| `Dashboard` | `DashboardViewModel` | Dashboard overview ViewModel. |
| `Devices` | `DevicesViewModel` | Devices list ViewModel. |
| `Settings` | `SettingsViewModel` | Application settings ViewModel. |

### Navigation Properties

| Property | Type | Description |
|----------|------|-------------|
| `SelectedNavTag` | `string` | Current nav tag: `"Dashboard"`, `"Pad1"`–`"Pad16"`, `"Profiles"`, `"Devices"`, `"Settings"`, `"About"`. Also notifies `IsPadPageSelected` and `SelectedPadIndex`. |
| `IsPadPageSelected` | `bool` | True if a Pad page (Pad1–Pad16) is selected. Computed. |
| `SelectedPadIndex` | `int` | Zero-based pad index for the selected Pad page, or -1. Computed. |
| `SelectedPad` | `PadViewModel` | PadViewModel for the selected Pad page, or null. Computed. |

### App-wide Status Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `StatusText` | `string` | `"Ready"` | Status bar text. Plain writes are info-class and decay after ~5 s (`StatusDecayMs`). Every write restamps the decay window. |
| `IsEngineRunning` | `bool` | `false` | Polling loop active. Calls `RefreshEngineStatus()`. |
| `HasActiveSlots` | `bool` | `false` | Any virtual controller slots exist. Calls `RefreshEngineStatus()`. |
| `EngineStatusText` | `string` | - | Computed localized text: `Engine_Forging` (`"Forging"`, engine running with active slots) / `Common_Idle` (`"Idle"`, running with no created slots) / `Common_Stopped` (`"Stopped"`). Note: this is the localized display text. `DashboardViewModel.EngineStateKey` carries the non-localized `"Running"` / `"Idle"` / `"Stopped"` key for XAML DataTriggers. |
| `EngineStatusBrush` | `Brush` | - | Computed: Red (#F44336) = Stopped, Amber (#FFB300) = Idle (engine running, no created slots), Green (#4CAF50) = running with active slots (the Forging state). Frozen (thread-safe). |
| `PollingFrequency` | `double` | `0` | Current polling frequency in Hz. |
| `ConnectedDeviceCount` | `int` | `0` | Connected input device count. |

### Commands

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `StartEngineCommand` | `!IsEngineRunning` | Raises `StartEngineRequested`. Wired by MainWindow code-behind. |
| `StopEngineCommand` | `IsEngineRunning` | Raises `StopEngineRequested`. |

### Events

| Event | Args | Description |
|-------|------|-------------|
| `StartEngineRequested` | `EventArgs` | Start engine. |
| `StopEngineRequested` | `EventArgs` | Stop engine. |
| `NavControllerItemsRefreshed` | `EventArgs` | Raised after `RefreshNavControllerItems()` completes. MainWindow uses this instead of `CollectionChanged` to avoid rapid sidebar rebuilds. |

### Key Methods

| Method | Description |
|--------|-------------|
| `RefreshNavControllerItems()` | Rebuilds sidebar entries from `SettingsManager.SlotCreated[]`. Computes per-type instance numbers and updates each pad's `Title`, `SlotLabel`, `TypeInstanceLabel`. Raises `NavControllerItemsRefreshed` only when the active-slot set changed (add / remove / reorder). Property-only changes (icon, label, enabled) update in place without the event. |
| `RefreshEngineStatus()` | Notifies `EngineStatusText` and `EngineStatusBrush`. |
| `RefreshCommands()` | Notifies `CanExecuteChanged` on start/stop commands. Call after `IsEngineRunning` changes. |
| `SetStatus(string, bool persist = false)` | Writes the status bar with an explicit class. `persist: true` (failures, prompts a later write always terminates) exempts the message from the decay sweep until the next write. |
| `ClearDecayedStatus()` | Clears a decayed info message. Re-checks `IsStatusDecayDue` first, so a write that lands mid-sweep wins. Called from MainWindow's 5 s driver-status timer. |

---

## DashboardViewModel

**File:** `DashboardViewModel.cs`
**DataContext for:** Dashboard page

Overview of all controller slots, engine status, connected devices, and driver status.

### Slot Summaries

| Property | Type | Description |
|----------|------|-------------|
| `SlotSummaries` | `ObservableCollection<SlotSummary>` | Cards for created slots. Rebuilt by `RefreshActiveSlots()`. |
| `ShowAddController` | `bool` | "Add Controller" visible (any type has capacity). |

### Engine Status

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `EngineStatus` | `string` | `"Stopped"` | Localized engine status. |
| `EngineStateKey` | `string` | `"Stopped"` | Non-localized state key (`"Running"`, `"Stopped"`, `"Idle"`) for XAML DataTriggers. |
| `PollingFrequency` | `double` | `0` | Polling frequency in Hz. Also notifies `PollingFrequencyText`. |
| `PollingFrequencyText` | `string` | - | Computed: formatted frequency (e.g., `"987.3 Hz"`) or dash when zero. |

### Device Counts

| Property | Type | Description |
|----------|------|-------------|
| `TotalDevices` | `int` | Total detected devices (online + offline). |
| `OnlineDevices` | `int` | Currently connected devices. |
| `MappedDevices` | `int` | Devices with an active slot mapping. |

### Driver Status

HIDMaestro is bundled with PadForge as a managed SDK and ships with the executable, so the dashboard does not surface an install/uninstall row for it. HidHide, Windows MIDI Services, and SteamVR are optional system components and have their own rows.

| Property | Type | Description |
|----------|------|-------------|
| `IsHidHideInstalled` | `bool` | HidHide installed. Notifies `HidHideStatusText`. |
| `HidHideStatusText` | `string` | Computed: `"Installed"` / `"Not Installed"`. |
| `IsMidiServicesInstalled` | `bool` | Windows MIDI Services installed. Notifies `MidiServicesStatusText`. |
| `MidiServicesStatusText` | `string` | Computed: `"Installed"` / `"Not Installed"`. |
| `IsSteamVrInstalled` | `bool` | SteamVR present, which gates the VR slot type (#49). Kept current by MainWindow's periodic status refresh alongside the MIDI Services flag. Notifies `SteamVrStatusText`. |
| `IsSteamVrRunning` | `bool` | The background VR consumer is connected to a running SteamVR (#287). Notifies `SteamVrStatusText`. |
| `IsVrDriverConnected` | `bool` | A VR slot's OpenVR driver is connected in SteamVR (the SDK's `DriverConnected`, #287). Notifies `SteamVrStatusText`. |
| `AreVrControllersLive` | `bool` | A VR slot's virtual hands are registered and live in SteamVR (the SDK's `ControllersLive`, #287). Notifies `SteamVrStatusText`. |
| `SteamVrStatusText` | `string` | Computed, tiered (#287), deepest true state wins: `"Not Installed"`, then `Vr_Status_ControllersLive`, `Vr_Status_DriverConnected`, `Vr_Status_Running`, falling back to `"Installed"`. |

### DSU Motion Server

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `EnableDsuMotionServer` | `bool` | `false` | DSU (cemuhook) motion server enabled. |
| `DsuMotionServerPort` | `int` | `26760` | UDP port. Clamped to 1024–65535. |
| `DsuServerStatus` | `string` | `"Stopped"` | DSU server status. |
| `IsDsuServerRunning` | `bool` | `false` | Serving truth for the DSU card flame (#175): the actual server lifecycle, not the enable checkbox. Set by InputService at the same points that write `DsuServerStatus`. |

| Command | Description |
|---------|-------------|
| `ResetDsuPortCommand` | Resets `DsuMotionServerPort` to 26760. |

### Web Controller Server

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `EnableWebController` | `bool` | `false` | Web controller server enabled. |
| `WebControllerPort` | `int` | `8080` | HTTP/WebSocket port. Clamped to 1024–65535. |
| `WebControllerStatus` | `string` | `"Stopped"` | Web controller server status. |
| `IsWebControllerRunning` | `bool` | `false` | Serving truth for the Web Controller card flame (#175): actual server lifecycle, not the enable checkbox. Set by InputService alongside `WebControllerStatus`. |
| `WebControllerClientCount` | `int` | `0` | Connected web controller clients. |
| `WebControllerUrl` | `string` | `null` | The live server URL, `https://` when the secure lane bound (#296). Empty when stopped. |
| `WebControllerQr` | `ImageSource` | `null` | QR of `WebControllerUrl` so a phone opens the controller by scanning (#296). Null when stopped, which hides the image. |
| `HasWebControllerQr` | `bool` | `false` | Whether a QR is available. Drives its visibility. |

| Command | Description |
|---------|-------------|
| `ResetWebPortCommand` | Resets `WebControllerPort` to 8080. |
| `CopyWebControllerUrlCommand` | Copies `WebControllerUrl` to the clipboard. No-op when empty. |

### Remote Link (#138)

Peer-to-peer controller relay over the LAN. The Dashboard hosts the server toggles and the outbound-connect box. The paired-peer manager and identity-protection state live on `SettingsViewModel` and are surfaced here through the `RemoteLink` reference below.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `RemoteLink` | `SettingsViewModel` | - | The Settings VM, set once at startup. Holds `TrustedPeers`, `NearbyUnpaired`, and the identity-protection block so the Dashboard's Remote Link section can show paired peers, identity mode, and nearby PCs in one place. |
| `EnableRemoteLink` | `bool` | `false` | Whether the Remote Link server is listening for paired peers. |
| `AutoReconnect` | `bool` | `true` | When a paired PC appears on the LAN, establish the link without a click. |
| `RemoteLinkPort` | `int` | `27500` | TCP control + UDP data port. Clamped to 1024–65535. |
| `RemoteLinkStatus` | `string` | `"Stopped"` | Remote Link server status text. |
| `IsRemoteLinkRunning` | `bool` | `false` | Serving truth for the Remote Link card flame (#175): true only while the link server object is live. The status text can carry identity-unlock errors while the server never started, so the flame keys on this, not the text or the enable checkbox. |
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
| `ConnectToPeerRequested` | `string` | User asked to connect/pair with a typed host[:port]. |

### Touchpad Overlay (3.2)

On-screen transparent touchpad window that drives the DS4 / DualSense touchpad on the assigned PlayStation slot.

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
| `TouchpadOverlayStatus` | `string` | - | Localized status string (`"Running"` / `"Stopped"`). |

| Command | Description |
|---------|-------------|
| `ResetOpacityCommand` | Resets opacity to default 0.25. |
| `ResetTouchpadOverlayPositionCommand` | Raises `ResetTouchpadOverlayPositionRequested`. `InputService` recenters the live overlay (or seeds defaults if not open) and clears persisted `Left` / `Top`. |

| Event | Description |
|-------|-------------|
| `ResetTouchpadOverlayPositionRequested` | Recenter request from the UI. |

### Key Methods

| Method | Description |
|--------|-------------|
| `RefreshActiveSlots(IList<int>, bool)` | Rebuilds `SlotSummaries` for active slots. Updates display labels, re-applies the remembered focus selection, sets `ShowAddController`. Called by InputService. |
| `SetSelectedPad(int)` | Marks the slot whose pad page is in focus so its card wears the selection glow. `-1` clears it. The index is remembered, so a later `RefreshActiveSlots` rebuild re-applies the flag to fresh summaries. |

---

### SlotSummary

**File:** `DashboardViewModel.cs` (nested class)

Summary card for one virtual controller slot on the Dashboard.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `PadIndex` | `int` | - | Zero-based slot index. Read-only. |
| `SlotLabel` | `string` | - | Display label (e.g., `"Virtual Controller 1"`). |
| `MappedDevices` | `ObservableCollection<PadViewModel.MappedDeviceInfo>` | `null` | Live reference to the pad's mapped-device list, so the crucible card renders a per-device roster with battery glyphs (#175). Set by InputService. Same-reference sets are no-ops. |
| `DeviceName` | `string` | `"No device"` | Primary mapped device name. |
| `BatteryText` | `string` | `""` | Battery of the first mapped device reporting one, e.g. `"78%"`. Empty otherwise (#175, issue #167 lane). |
| `IsActive` | `bool` | `false` | Has at least one online mapped device. |
| `IsSelected` | `bool` | `false` | Whether this slot's pad page is the one currently in focus. Drives the persistent selection glow on the card. Set by `DashboardViewModel.SetSelectedPad`, not the same as `IsActive`. |
| `IsVirtualControllerConnected` | `bool` | `false` | Virtual controller connected. Notifies `StatusText`. |
| `IsInitializing` | `bool` | `false` | Virtual controller initializing. Notifies `StatusText`. |
| `IsCreateFailed` | `bool` | `false` | The slot's latest create attempt failed (engine createFailed latch). Its own status: a failed slot with online devices is neither forging nor awaiting devices. Notifies `StatusText`. |
| `MappedDeviceCount` | `int` | `0` | Devices mapped to this slot. Notifies `HasMappedDevices` and `StatusText`. |
| `HasMappedDevices` | `bool` | - | Computed: `MappedDeviceCount > 0`. Ember heat gating (#175): cards with zero mappings stay cold (no ember rim, no glow, steel seg tile) even when enabled. |
| `ConnectedDeviceCount` | `int` | `0` | Mapped devices connected. |
| `StatusText` | `string` | `"Idle"` | Ember status vocabulary (#175). For an enabled, non-initializing slot the getter checks three branches in order. A failed create returns `Main_VcFailed` first. Then zero mappings returns `Dashboard_StatusCold` (`"Cold"`). It returns `Main_AwaitingDevices` (`"Awaiting devices"`) for a mapped slot with nothing connected once the live VC is gone. While the VC survives the inactivity grace (60 s default), a device dropout must not flap the card to awaiting. Every other case passes through the engine-assigned setter value: `Main_Active` (`"Forging"`) when a device is online, `Common_Idle` (`"Idle"`), `Common_Disabled` (`"Disabled"`), or `Main_Initializing` (`"Initializing"`). The old `"No mapping"` string is intercepted by the Cold branch. |
| `IsEnabled` | `bool` | `true` | Slot enabled for output. |
| `SlotNumber` | `int` | `1` | 1-based controller number among active slots. |
| `TypeInstanceLabel` | `string` | `"1"` | Per-type instance label. |
| `OutputType` | `VirtualControllerType` | `Xbox` | Virtual controller output type. (XML on-disk name is `"Microsoft"` via `[XmlEnum]` for v2/early-v3 back-compat. In-code identifier is `Xbox`.) |
| `StageLedger` | `ObservableCollection<SlotStageInfo>` | empty | Pipeline stage ledger (#175 item 10): one entry per configuration stage the slot's assigned devices actually have (sticks / triggers / gyro / lighting / touchpad / audio), in that order. Rebuilt per slot by `InputService.RefreshSlotStageLedger` on its 1 s slow lane. Entries mutate in place when membership is unchanged so the card doesn't re-template. |

### SlotStageInfo

**File:** `DashboardViewModel.cs`

One stage entry in a slot card's pipeline heat ledger (#175 item 10).

| Property | Type | Description |
|----------|------|-------------|
| `Kind` | `string` | Stable stage identity (`"Sticks"`..`"Audio"`). Membership comparisons key on this so in-place updates are possible. Read-only. |
| `Glyph` | `string` | Segoe font glyph for the font stages (same characters as the matching tab page headers). Empty for shape stages. Read-only. |
| `IsStickShape` | `bool` | True for the Sticks entry. Rendered with the Zacksly stick ring + disc geometries instead of a font glyph. Read-only. |
| `IsTriggerShape` | `bool` | True for the Triggers entry. Rendered with the Zacksly trigger body geometry. Read-only. |
| `IsHot` | `bool` | True when the stage carries a non-default configuration on any assigned device. Ember when hot, ashen steel when inert. |
| `Summary` | `string` | Composite change key for the tooltip readout (all lines joined). Empty when inert, which disables the tooltip. Notifies `HasSummary`. |
| `HasSummary` | `bool` | Computed: tooltip gate, no tooltip on inert stages. |
| `SummaryLines` | `ObservableCollection<StageSummaryLine>` | Per-device readout lines for the hover tooltip, in binding order. Devices still at defaults read STOCK. |

### StageSummaryLine

**File:** `DashboardViewModel.cs`

One tooltip line of a stage's readout: device-class glyph, device name, then mono value tokens.

| Property | Type | Description |
|----------|------|-------------|
| `DeviceGlyph` | `string` | Device-class glyph. Empty for slot-level lines. |
| `DeviceName` | `string` | Body-face device name, carrying its trailing `"  ·  "` separator. Empty for slot-level lines like the audio master volume. |
| `Tokens` | `string` | Mono value tokens. |

---

## SettingsViewModel

**File:** `SettingsViewModel.cs`
**DataContext for:** Settings page

Application-level settings: theme, language, drivers, profiles, and engine configuration.

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
| `AvailableLanguages` | `ObservableCollection<CultureInfo>` | UI languages: en, de, fr, ja, ko, zh-Hans, pt-BR, es, it, nl. |
| `SelectedLanguage` | `CultureInfo` | Current UI language. Applies immediately via `Strings.ChangeCulture()`. Defaults to current culture or English. |

| Member | Type | Description |
|--------|------|-------------|
| `LanguageCode` | `string` | Persisted language code for serialization. |
| `SetLanguageFromCode(string)` | method | Sets language from persisted code on startup without raising `CultureChanged`. |
| `ResetLanguageToSystemDefault()` | method | Sets `SelectedLanguage` back to the OS UI culture (or English when unsupported). |

### Driver Status: HIDMaestro

HIDMaestro is shipped as an embedded managed SDK (`HIDMaestro.Core`, bundled at `Resources/HIDMaestro/HIDMaestro.Core.dll`). The user-mode driver still needs to be registered with Windows once. That happens inside the engine via `HMContext.InstallDriver()` (called from `InputManager.Step5.VirtualDevices.cs:EnsureHMaestroContext`), not through `DriverInstaller`. The SettingsViewModel exposes a read-only version string read from the bundled assembly at startup.

| Property | Type | Description |
|----------|------|-------------|
| `HIDMaestroVersion` | `string` | HIDMaestro SDK version. Initialized from the embedded `HIDMaestro.Core` assembly via `GetEmbeddedHidMaestroVersion()`. |

### Driver Status: HidHide

| Property | Type | Description |
|----------|------|-------------|
| `IsHidHideInstalled` | `bool` | HidHide installed. |
| `HidHideStatusText` | `string` | Computed: `"Installed"` / `"Not Installed"`. |
| `HidHideVersion` | `string` | HidHide version. |
| `HidHideWhitelistPaths` | `ObservableCollection<string>` | Whitelisted application paths. |
| `SelectedWhitelistPath` | `string` | Selected whitelist path. Refreshes `RemoveWhitelistPathCommand`. |

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `InstallHidHideCommand` | `!IsHidHideInstalled` | Raises `InstallHidHideRequested`. |
| `UninstallHidHideCommand` | `IsHidHideInstalled && !HasAnyHidHideDevices()` | Raises `UninstallHidHideRequested`. |
| `AddWhitelistPathCommand` | `IsHidHideInstalled` | Raises `AddWhitelistPathRequested`. |
| `RemoveWhitelistPathCommand` | `SelectedWhitelistPath != null` | Removes selected path, raises `WhitelistChanged`. |

| Event | Description |
|-------|-------------|
| `InstallHidHideRequested` | Install HidHide. |
| `UninstallHidHideRequested` | Uninstall HidHide. |
| `AddWhitelistPathRequested` | Add whitelist path (opens file dialog). |
| `WhitelistChanged` | Whitelist was modified (add or remove). |

### Driver Status: Windows MIDI Services

| Property | Type | Description |
|----------|------|-------------|
| `IsMidiServicesInstalled` | `bool` | Windows MIDI Services available. |
| `MidiServicesStatusText` | `string` | Computed: `"Installed"` / `"Not Installed"`. |
| `MidiServicesVersion` | `string` | MIDI Services version. |
| `IsMidiOsSupported` | `bool` | Static: `true` if OS build >= 26100 (Win11 24H2). |
| `MidiOsSupported` | `bool` | Instance forwarder over the static above. A XAML `Binding` path resolves against the DataContext instance and cannot reach a static member, so SettingsPage binds this one. Never raises `PropertyChanged` because the OS build cannot change while the app runs. |

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `InstallMidiServicesCommand` | `!IsMidiServicesInstalled && IsMidiOsSupported` | Raises `InstallMidiServicesRequested`. |
| `UninstallMidiServicesCommand` | `IsMidiServicesInstalled && !HasAnyMidiSlots()` | Raises `UninstallMidiServicesRequested`. |

### Driver Status: SteamVR (#49)

The VR slot type needs SteamVR present. PadForge can install it Steam-free through steamcmd, and it only offers to remove the copy it created itself.

| Property | Type | Description |
|----------|------|-------------|
| `IsSteamVrInstalled` | `bool` | A SteamVR install of either shape is present (Steam client, or the Steam-free steamcmd one). Notifies `SteamVrStatusText` and `ShowSteamVrUninstall`. |
| `SteamVrStatusText` | `string` | Computed, tiered like the Dashboard row (#287): `"Not Installed"`, then controllers-live / driver-connected / running read off `HMaestroVRController.GlobalDriverStatus()` and `OpenVrConsumerService.ServerConnected`, falling back to `"Installed"`. |
| `SteamVrInstallDir` | `string` | Where the Steam-free install will land (seeded from `DriverInstaller.SteamVrInstallDir`). Not persisted by PadForge: after a successful install the HIDMaestro path hint is the durable record. |
| `IsSteamVrOwned` | `bool` | The present install is the Steam-free one PadForge created. A Steam-client install is never PadForge's to remove. |
| `ShowSteamVrUninstall` | `bool` | Computed: `IsSteamVrInstalled && IsSteamVrOwned`. |

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
| `RefreshSteamVrStatus()` | Raises the SteamVR row's change notification. Called by MainWindow's status refresh beside the Dashboard tier push, since `SteamVrStatusText` reads live statics. |

### Driver Uninstall Guards

| Member | Type | Description |
|--------|------|-------------|
| `HasAnyMidiSlots` | `Func<bool>` | Set by MainWindow. True if any slot uses MIDI. Blocks `UninstallMidiServicesCommand`. |
| `HasAnyVrSlots` | `Func<bool>` | Set by MainWindow. True if any created slot is a VR slot. Blocks `UninstallSteamVrCommand`. |
| `HasAnyHidHideDevices` | `Func<bool>` | Set by MainWindow. True if any device has HidHide enabled. Blocks `UninstallHidHideCommand`. |
| `RefreshDriverGuards()` | method | Re-evaluates uninstall `CanExecute` for HidHide, MIDI Services, and SteamVR. Call after slot creation/deletion/type changes. |

### Engine Settings

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `AutoStartEngine` | `bool` | `true` | Auto-start engine on launch. |
| `MinimizeToTray` | `bool` | `false` | Minimize to system tray instead of taskbar. |
| `BatteryNotifyEnabled` | `bool` | `true` | Low-battery notification master toggle (#293). |
| `BatteryNotifyThreshold` | `int` | `15` | Percent at or below which the edge-triggered notification fires. Clamped 5–50. |
| `BatteryNotifyVibrate` | `bool` | `false` | Also buzz the device on the low-battery edge, using the identify pulse train. |
| `StartMinimized` | `bool` | `false` | Start minimized. |
| `StartAtLogin` | `bool` | `false` | Auto-start at login. |
| `EnablePollingOnFocusLoss` | `bool` | `true` | Continue polling on focus loss. |
| `PollingRateMs` | `int` | `1` | Polling interval in ms. Clamped to 1–16. |
| `HmInactivityDestroyTimeoutSeconds` | `int` | `60` | Seconds the engine waits for any mapped device to return online before tearing down the live HM virtual controller and freeing its kernel slot. Clamped to 0–3600. `0` disables the timeout. The slot's configuration (mappings, profile, position, enabled state) is preserved end-to-end. Only the live VC is destroyed. Once mapped devices come back online, the VC recreates automatically at the same visual position. Surviving Xbox HM VCs at higher visual positions bubble down to keep xinputhid indices contiguous after the teardown. |
| `EnableInputHiding` | `bool` | `true` | Master switch for device hiding (HidHide + input hooks). |
| `KeepHidHideCloaksBetweenLaunches` | `bool` | `false` | When true, HidHide cloaks stay asserted after PadForge exits so other apps still see the physical devices hidden. When false (default), cloaks clear on shutdown. |

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
| `SdlVersion` | `string` | SDL3 version. |
| `ApplicationVersion` | `string` | Application version. |
| `RuntimeVersion` | `string` | .NET runtime version. |

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
| `BrowseCommunityConfigsCommand` | `RelayCommand` | | The Profiles-page entry. No CanExecute gate: with the opt-in off the dialog opens on its cold state and offers the enable step. |
| `BrowseStarterProfilesCommand` | `RelayCommand` | | Opens the starter-profile gallery (#256) through `BrowseStarterProfilesRequested`. Always enabled: the catalog ships in the box, so there is no opt-in and no network. |

### Remote Link Peer Manager (#138)

The trusted-peer list and identity-protection mode live here. The Dashboard's Remote Link section binds them through `DashboardViewModel.RemoteLink`.

| Property | Type | Description |
|----------|------|-------------|
| `TrustedPeers` | `ObservableCollection<RemoteLinkTrustedPeer>` | Trusted paired PCs, shown in the Settings peer manager. |
| `NearbyUnpaired` | `ObservableCollection<RemoteLinkNearbyPeer>` | PadForge PCs discovered on the LAN that aren't paired yet. |
| `HasNearbyUnpaired` | `bool` | Computed: `NearbyUnpaired.Count > 0`. |
| `IdentityProtectionModes` | `IReadOnlyList<string>` | Dropdown options in index order: 0 Secure, 1 password-portable, 2 open-portable. |
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
| `IdentityProtectionModeChangeRequested` | `int` | User picked a different protection mode (new index). |

| Method | Description |
|--------|-------------|
| `RefreshTrustedPeers(IEnumerable<PeerTrust>, IReadOnlyCollection<string>)` | Rebuilds `TrustedPeers` from the trust store. Called on pair / revoke / rename, not for online refresh. |
| `UpdatePeerOnlineStatus(IReadOnlyCollection<string>)` | Updates each peer's online dot in place from the live connection set. |
| `UpdatePeerReachability(IReadOnlyDictionary<string,string>)` | Updates each paired peer's reachable host:port in place from LAN discovery. |
| `SetNearbyUnpaired(IEnumerable<RemoteLinkNearbyPeer>)` | Replaces the nearby-unpaired list. |
| `SetIdentityProtectionModeSilently(int)` | Sets the mode without raising the change request (init from settings, or revert a cancelled switch). |

### First-Run, Window, and Foreground State

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ForegroundExeName` | `string` | `"-"` | Foreground exe filename the auto-switch monitor last saw (#175 item 8). Runtime-only, fed at 1 Hz by InputService's UI timer, never persisted. |
| `IsForegroundMatched` | `bool` | `false` | True while the foreground exe matches a profile. Runtime-only. |
| `NoProfileHasExecutables` | `bool` | - | Computed: no profile carries an executable match rule (#175 item 8). |
| `LegacyDriverCleanupOffered` | `bool` | `false` | True after the v3 first-run cleanup wizard has been shown. Persists so the dialog appears once. |
| `FirstRunTourCompleted` | `bool` | `false` | True once the first-run welcome tour is completed or skipped. Replaces the pre-v4 beside-exe marker file. |
| `MainWindowLeft` / `Top` | `double` | `-1` | Main window position (profile-independent). |
| `MainWindowWidth` / `Height` | `double` | `1100` / `720` | Main window size. |
| `MainWindowState` | `int` | `0` | Persisted window state (normal / maximized). |
| `MainWindowFullScreen` | `bool` | `false` | Full-screen flag. |

### Profiles

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `EnableAutoProfileSwitching` | `bool` | `false` | Auto-profile switching enabled. |
| `ProfileItems` | `ObservableCollection<ProfileListItem>` | empty | Profile entries for UI list. |
| `ProfileShortcuts` | `ObservableCollection<ProfileShortcutViewModel>` | empty | Profile-switch shortcut rows for the ProfilesPage shortcuts card. |
| `SelectedProfile` | `ProfileListItem` | `null` | Selected profile. Refreshes delete/edit/load/export commands. |
| `ActiveProfileInfo` | `string` | `"Default"` | Active profile display text. |

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `NewProfileCommand` | always | Raises `NewProfileRequested`. |
| `SaveAsProfileCommand` | always | Raises `SaveAsProfileRequested`. |
| `DeleteProfileCommand` | `SelectedProfile != null && !IsDefault` | Raises `DeleteProfileRequested`. |
| `EditProfileCommand` | `SelectedProfile != null && !IsDefault` | Raises `EditProfileRequested`. |
| `LoadProfileCommand` | `SelectedProfile != null` | Raises `LoadProfileRequested` or `RevertToDefaultRequested` if default. |
| `ExportProfileCommand` | `SelectedProfile != null` | Raises `ExportProfileRequested`. Exports the selected profile as a `.pfprofile`. The Default entry exports a snapshot of the current settings. |
| `ImportProfileCommand` | always | Raises `ImportProfileRequested`. Imports a `.pfprofile`. |

| Event | Description |
|-------|-------------|
| `RevertToDefaultRequested` | Revert to default profile. |
| `NewProfileRequested` | Create new empty profile. |
| `SaveAsProfileRequested` | Save current settings as profile. |
| `DeleteProfileRequested` | Delete selected profile. |
| `EditProfileRequested` | Edit selected profile metadata. |
| `LoadProfileRequested` | Load selected profile. |
| `ExportProfileRequested` | Export selected profile to a `.pfprofile`. |
| `ImportProfileRequested` | Import a `.pfprofile`. |

The delete / edit / load / export commands refresh their own `CanExecute` inline in the `SelectedProfile` setter. There is no separate refresh method.

---

### ProfileListItem

**File:** `SettingsViewModel.cs` (nested class)

Display item for a profile in the Settings list.

| Property | Type | Description |
|----------|------|-------------|
| `Id` | `string` | Profile identifier. |
| `IsActive` | `bool` | Whether this profile is the currently active one. Drives the lit flame in the Profiles list (#175). |
| `Name` | `string` | Display name. |
| `Executables` | `string` | Comma-separated exe names for auto-switch (display form). Notifies `HasExecutables`, `AutoSwitchRuleSummary`. |
| `ExecutablePaths` | `string` | Pipe-separated full executable paths (the ForegroundMonitorService match source). Feeds the card's exe icon and mono exe line (#175). |
| `FirstExecutablePath` | `string` | Computed: full path of the first executable, or null. The card's icon converter `File.Exists`-gates this. |
| `FirstExecutableName` | `string` | Computed: file name of the first executable, or null. |
| `SecondExecutableName` | `string` | Computed: file name of the second executable, or null. The card face shows up to two names before the `+N` marker. |
| `ExtraExecutablesSuffix` | `string` | Computed: locale-neutral `"+N"` marker for rules beyond the two shown names, or null. |
| `HasExecutables` | `bool` | Computed: the profile carries any executable match rule. Half of the auto-switch chip gate (#175). |
| `AutoSwitchRuleSummary` | `string` | Computed: exe-match rule summary for the cold auto-switch chip, the display exe list under a localized prefix. |
| `TopologyLabel` | `string` | Slot topology summary. |
| `HasNoSlots` | `bool` | Computed: all type counts are zero. |
| `XboxCount` | `int` | Number of Xbox slots in this profile. |
| `PlayStationCount` | `int` | Number of PlayStation slots. |
| `NintendoCount` | `int` | Number of Nintendo slots (#215). |
| `ExtendedCount` | `int` | Number of Extended slots. |
| `MidiCount` | `int` | Number of MIDI slots. |
| `KbmCount` | `int` | Number of Keyboard+Mouse slots. |
| `VrCount` | `int` | Number of VR slots (#49). |
| `IsDefault` | `bool` | Computed: true if `Id == "__default__"`. |

| Constant | Value | Description |
|----------|-------|-------------|
| `DefaultProfileId` | `"__default__"` | Sentinel ID for the Default profile. |

---

## DevicesViewModel

**File:** `DevicesViewModel.cs`
**DataContext for:** Devices page

All detected input devices (online and offline) with raw input state for the selected device.

### Device List

| Property | Type | Description |
|----------|------|-------------|
| `Devices` | `ObservableCollection<DeviceRowViewModel>` | All known devices. Updated by InputService on change. |
| `SelectedDevice` | `DeviceRowViewModel` | Selected device. Notifies `HasSelectedDevice`, refreshes slot buttons and command state. |
| `HasSelectedDevice` | `bool` | Computed: `SelectedDevice != null`. |

### Device Counts

| Property | Type | Description |
|----------|------|-------------|
| `TotalCount` | `int` | Total detected devices. |
| `OnlineCount` | `int` | Connected devices. |

### Type Facet Filter (#175)

Chip row above the device list that filters by device class. The chips bind their labels to the count properties. Clicking one sets `SelectedFacet`.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `SelectedFacet` | `string` | `"ALL"` | Active facet token: `ALL` / `GAMEPAD` / `JOYSTICK` / `WHEEL` / `KEYBOARD` / `MOUSE` / `OTHER`. Locale-neutral literals the chip DataTriggers key off. The setter routes through `SetFacet`. |
| `FacetCountGamepad` | `int` | `0` | Rows behind the GAMEPAD chip (the stick classes: Gamepad / FirstPerson / Supplemental). |
| `FacetCountJoystick` | `int` | `0` | Rows behind the JOYSTICK chip (joysticks + flight sticks). |
| `FacetCountWheel` | `int` | `0` | Rows behind the WHEEL chip. |
| `FacetCountKeyboard` | `int` | `0` | Rows behind the KEYBOARD chip. |
| `FacetCountMouse` | `int` | `0` | Rows behind the MOUSE chip. |
| `FacetCountOther` | `int` | `0` | Rows behind the OTHER chip (touchpads, MIDI, NFC, microphones, consumer collections, unclassified). |

| Method | Description |
|--------|-------------|
| `SetFacet(string)` | Applies the facet filter to the default collection view the ListBox binds through, so the XAML keeps a plain `ItemsSource="{Binding Devices}"`. `ALL` clears the filter. No-op when the token is unchanged or empty. |

The ALL chip binds `TotalCount`. `RefreshCounts()` recomputes every facet count and re-runs the active filter so rows whose type key changed in place re-bucket.

### Raw Input State Display (for selected device)

| Property | Type | Description |
|----------|------|-------------|
| `RawAxes` | `ObservableCollection<AxisDisplayItem>` | Axis values (progress bars). |
| `RawButtons` | `ObservableCollection<ButtonDisplayItem>` | Button states (circles). |
| `RawPovs` | `ObservableCollection<PovDisplayItem>` | POV hat values (compass). |
| `KeyboardKeys` | `ObservableCollection<KeyboardKeyItem>` | Keyboard layout items. |
| `IsKeyboardDevice` | `bool` | Selected device is a keyboard. |
| `IsMouseDevice` | `bool` | Selected device is a mouse. |
| `IsTouchpadDevice` | `bool` | Selected device exposes a touchpad surface (DS4 / DualSense / Steam Controller / Steam Deck / overlay touchpad). |
| `IsMidiDevice` | `bool` | Selected device is a MIDI input (#128). Drives the live piano / CC preview off `LiveMidi`. |
| `IsNfcDevice` | `bool` | Selected device is an NFC reader (#150). Populates `NfcTags`. |
| `IsMicrophoneDevice` | `bool` | Selected device is a standalone microphone (#317). Hides the numbered button grid, since every button it has is a named phrase. |
| `ShowVoicePhrases` | `bool` | Selected device carries voice phrases (a microphone row, or a Bluetooth DualSense whose embedded mic is not a system device). Drives the Voice Macros section, the voice twin of the NFC Tags section. |
| `VoicePhrases` | `ObservableCollection<NfcTagDisplayItem>` | Named phrase rows for the live preview (#317): "Any Phrase" plus each registered phrase. Reuses the NFC row item. Rebuilt by `RebuildVoicePhrases(int)`. |
| `VoiceButtonBase` | `int` | Raw-button base the current device's phrase buttons sit at (0 on a microphone row, the reserved pad range on a DualSense). `-1` when none. Private setter. |
| `IsConsumerDevice` | `bool` | Selected device is a Consumer Control collection (#168). Populates `ConsumerButtons`. |
| `IsHeadsetMotionDevice` | `bool` | Selected device is a Sony headset head tracker (#188). Collapses the raw Axes / Buttons sections, since a motion-only source has neither and the gyro readout is its whole preview. |
| `NfcTags` | `ObservableCollection<NfcTagDisplayItem>` | Registered-tag rows for the NFC preview. Rebuilt by `RebuildNfcTags()`. |
| `ConsumerButtons` | `ObservableCollection<ConsumerButtonDisplayItem>` | Named media-key chips for the Consumer Control preview. |
| `LiveMidi` | `MidiInputState` | Latest MIDI input snapshot the piano / CC preview polls. Plain property, no change notification. |
| `HasTouchpadData` | `bool` | At least one finger is currently in contact. |
| `TouchpadX0`–`TouchpadX4` / `TouchpadY0`–`TouchpadY4` | `double` | Per-finger normalized position (0.0–1.0) on the first pad. Five contacts, not two. |
| `TouchpadDown0`–`TouchpadDown4` | `bool` | Per-finger contact state. |
| `HasSecondTouchpadData` | `bool` | The device exposes a second pad (Steam Controller / Steam Deck). Switches the labels to `TouchpadLabel` / `Touchpad2Label`. |
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

### Dynamic Slot Assignment Buttons

| Property | Type | Description |
|----------|------|-------------|
| `ActiveSlotItems` | `ObservableCollection<SlotButtonItem>` | Slot toggle buttons. Only includes created/active slots. |

### Commands

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `RefreshCommand` | always | Raises `RefreshRequested`. Force-refreshes device list. |
| `PairCommand` | always | Raises `PairRequested`. Opens the Bluetooth pairing flow for controllers that need an in-app pairing ceremony (Wii controllers, #116). |
| `AssignToSlotCommand` | `HasSelectedDevice` | `RelayCommand<int>`. Raises `AssignToSlotRequested` with slot index (0–15). |
| `ToggleSlotCommand` | `HasSelectedDevice` | `RelayCommand<int>`. Toggles slot assignment. Raises `ToggleSlotRequested`. |
| `HideDeviceCommand` | `HasSelectedDevice` | Raises `HideDeviceRequested` with the selected device's InstanceGuid. The row itself stays in the collection until the service refreshes the list. |
| `RemoveDeviceCommand` | `HasSelectedDevice` | Removes the row from `Devices`, clears `SelectedDevice`, raises `RemoveDeviceRequested`, then `RefreshCounts()`. |

### Events

| Event | Args | Description |
|-------|------|-------------|
| `RefreshRequested` | `EventArgs` | Refresh requested. |
| `PairRequested` | `EventArgs` | User opened the Bluetooth pairing flow (#116). |
| `AssignToSlotRequested` | `int` | Slot index. |
| `ToggleSlotRequested` | `int` | Slot index. |
| `HideDeviceRequested` | `Guid` | Instance GUID. |
| `RemoveDeviceRequested` | `Guid` | Instance GUID. |
| `DeviceHidingChanged` | `Guid` | HidHide or ConsumeInput toggle changed. |

### Key Methods

| Method | Description |
|--------|-------------|
| `RebuildRawStateCollections(IReadOnlyList<int> axisIndices, IReadOnlyList<int> buttonIndices, int povCount, bool isKeyboard, bool isMouse, bool isTouchpad, bool isMidi, bool isNfc, IReadOnlyList<ConsumerButtonDisplayItem> consumerButtons, bool isHeadsetMotion, int voiceButtonBase, bool isMicrophone)` | Rebuilds axis/button/POV collections for a new device. `axisIndices` is the sparse list of axis slots the device actually exposes (from `SupportedAxisIndices` / `CapAxisIndices` through `InputService.ResolveAxisIndices`), so each `AxisDisplayItem.Index` is the real `state.Axis[]` slot and its label reads `Axis {slot}`, gaps included. `buttonIndices` is the sparse list of button positions the device actually exposes (each item's value is stored verbatim as both `Index` and `DisplayNumber`). The class-flag booleans default to `false`, `consumerButtons` to `null`, and `voiceButtonBase` to `-1`. Handles keyboard, mouse, touchpad, MIDI, NFC, Consumer Control, headset-motion, and voice-phrase cases. |
| `ClearRawState()` | Clears all raw state display data, including the class flags and the NFC / voice / Consumer collections. |
| `RebuildNfcTags()` | Repopulates `NfcTags` from the registered-tag store. |
| `RebuildVoicePhrases(int)` | Repopulates `VoicePhrases` from `VoicePhraseRegistry` at the passed button base. A negative base clears the list. |
| `RefreshSlotButtons()` | Rebuilds `ActiveSlotItems` from created slots and selected device assignments. |
| `RefreshAllSlotBadges()` | Re-derives every row's `SlotBadges` after a slot set changes. |
| `FindByGuid(Guid)` | Finds a `DeviceRowViewModel` by instance GUID. |
| `RefreshCounts()` | Updates `TotalCount` and `OnlineCount`, recomputes every facet count, and re-runs the active filter. |
| `NotifyDeviceHidingChanged(Guid)` | Raises `DeviceHidingChanged`. |

### Internal State

| Member | Type | Description |
|--------|------|-------------|
| `LastRawStateDeviceGuid` | `Guid` | Tracks which device's collections are populated. Prevents unnecessary rebuilds. |

---

### SlotButtonItem

**File:** `DevicesViewModel.cs`

Single slot toggle button on the Devices page.

| Property | Type | Description |
|----------|------|-------------|
| `PadIndex` | `int` | Zero-based slot index (0–15). |
| `SlotNumber` | `int` | 1-based number among active slots. |
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
| `DisplayNumber` | `int` | Consecutive 0..N-1 shown to the user. The XAML binds `DisplayNumber`, not `Index`. |
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

| Constant | Value | Description |
|----------|-------|-------------|
| `LayoutWidth` | `556` | Canvas width for the keyboard layout. |
| `LayoutHeight` | `136` | Canvas height for the keyboard layout. |

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

---

## DeviceRowViewModel

**File:** `DeviceRowViewModel.cs`

Single device row on the Devices page. Shows identification, status, capabilities, and input hiding controls.

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

### Battery (#167)

Battery indicator on the device row. Sourced from SDL by InputService's slow lane.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `BatteryPercent` | `int` | `-1` | Battery percentage. `-1` when the device reports none (wired, unknown, or offline). Notifies `HasBattery`, `BatteryText`, `BatteryGlyph`. |
| `BatteryCharging` | `bool` | `false` | True while the device reports charging or charged. Notifies `BatteryGlyph`. |
| `HasBattery` | `bool` | - | Computed: `BatteryPercent >= 0`. Gates whether the indicator renders. |
| `BatteryText` | `string` | - | Computed: `"78%"`, or empty when `BatteryPercent < 0`. |
| `BatteryGlyph` | `string` | - | Computed: Segoe MDL2 Assets battery glyph bucketed to the nearest tenth. Discharging: Battery0–Battery9 = U+E850–U+E859, Battery10 = U+E83F. Charging: BatteryCharging0–8 = U+E85A–U+E862, BatteryCharging9 = U+E83E, BatteryCharging10 = U+EA93. |

### Power / Idle Disconnect (#162)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ShowIdleDisconnect` | `bool` | `false` | Computed: the device is a Bluetooth-pathed / power-off target. Gates the Power section. |
| `IdleDisconnectMinutes` | `int` | `0` | Idle countdown in minutes, `0` = off. Clamped `>= 0`. Persisted to UserDevice in seconds through the hiding-toggle channel. |

### Device-Class Flags

| Property | Type | Description |
|----------|------|-------------|
| `IsMidiDevice` | `bool` | Computed: `DeviceTypeKey == "Midi"`. Drives the live piano / CC preview (#128). |
| `IsHeadsetMotionDevice` | `bool` | Computed: `DeviceTypeKey == "HeadsetMotion"`. True for Sony headset head trackers (#188). Collapses the raw Axes / Buttons preview, which a motion-only source has neither of, and gates the repair action. |
| `ShowRegisterNfcTag` | `bool` | Computed: shows the Register / Manage NFC Tags button (#150). True for a standalone PC/SC reader (`DeviceTypeKey == "Nfc"`) and for a Switch right Joy-Con / combined pair / Pro Controller (VID 057E, PID 2007 / 2008 / 2009) on a Bluetooth link, whose own reader registers through the same dialog (#241). Always false on a `peer://` row: the tap event never crosses the link, so registration belongs to the owner. |
| `ShowManageVoicePhrases` | `bool` | Computed: shows the Manage Voice Macros button (#317). True for a `"Microphone"` row, and for a DualSense (VID 054C, PID 0CE6 / 0DF2) on a Bluetooth link, where the embedded mic is not a system device. Same `peer://` exclusion as the NFC button. |
| `HasNfcCapabilityChip` | `bool` | Computed: the device is a Switch controller carrying an NFC reader (VID 057E, PID 2007 / 2008 / 2009). A hardware fact, not the transport-gated arming state, so it reads true over USB too. A standalone PC/SC reader is excluded, its device type already says NFC. |
| `IsBluetoothLink` | `bool` | Computed by `DeviceTransport.IsBluetooth` from the device path and VID:PID. |

### Capabilities

| Property | Type | Description |
|----------|------|-------------|
| `AxisCount` | `int` | Number of axes. |
| `ButtonCount` | `int` | Number of buttons. |
| `PovCount` | `int` | Number of POV hat switches. |
| `DeviceTypeKey` | `string` | English type key: `"Gamepad"`, `"Joystick"`, `"Wheel"`, `"FlightStick"`, `"FirstPerson"`, `"Supplemental"`, `"Mouse"`, `"Keyboard"`, `"Touchpad"`, `"Midi"`, `"Nfc"`, `"Microphone"`, `"ConsumerControl"`, `"HeadsetMotion"`. Anything else falls back to the generic "Device" label. Notifies `DeviceType`. |
| `DeviceType` | `string` | Computed: localized type from `DeviceTypeKey`. |
| `HasRumble` | `bool` | Supports rumble. |
| `HasGyro` | `bool` | Has gyroscope. |
| `HasAccel` | `bool` | Has accelerometer. |
| `HasTouchpad` | `bool` | Exposes a touchpad surface. |
| `ShowTouchpadCapability` | `bool` | Computed: `HasTouchpad` and the device is not itself a touchpad, so a touchpad row does not advertise itself twice. |
| `HasCapabilityIcons` | `bool` | Computed: `HasRumble \|\| HasGyro \|\| ShowTouchpadCapability`. Gates the icon strip. |
| `CapabilitiesSummary` | `string` | Computed: e.g., `"6 axes, 11 buttons, 1 POV, Rumble, Gyro"`. |

### Slot Assignment

| Property | Type | Description |
|----------|------|-------------|
| `AssignedSlots` | `List<int>` | Assigned pad slot indices (0–15). Set via `SetAssignedSlots()`. |
| `SlotBadges` | `ObservableCollection<SlotBadge>` | Slot badges for XAML (icon + number). Rebuilt by `SetAssignedSlots()`. Absence of badges encodes "unassigned". The old `IsUnassigned` flag and its gray fallback pill were removed in #175 (phase 2 item 9). |

| Method | Description |
|--------|-------------|
| `SetAssignedSlots(List<int>)` | Replaces assigned slots, rebuilds `SlotBadges` with sequential numbering, notifies UI. |

### Input Hiding Toggles

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `HidHideEnabled` | `bool` | `false` | Hidden via HidHide (driver-level). |
| `ConsumeInputEnabled` | `bool` | `false` | Mapped inputs consumed via low-level hooks. |
| `ForceRawJoystickMode` | `bool` | `false` | Bypass SDL gamepad remapping. Read raw joystick indices. |
| `IsHidHideAvailable` | `bool` | `false` | HidHide installed (controls toggle IsEnabled). |
| `ShowConsumeToggle` | `bool` | - | Computed: real keyboards and mice only (`(Keyboard or Mouse) && !IsInternalVirtual`). Consumption suppresses the source at the raw/descriptor layer, which only exists for a real Windows HID device. |
| `IsInternalVirtual` | `bool` | - | Computed: true for PadForge-internal virtual sources, identified by URI-scheme `DevicePath` (`web://`, `overlay://`, `midi://`, `peer://`, `nfc://`, `mic://`). Covers web controllers, the touchpad overlay, MIDI-input devices, Remote Link peers, NFC readers, and microphone endpoints. HidHide can't blacklist non-HID paths, so the "Hide from games" toggle hides itself for these. |
| `ShowInputHidingSection` | `bool` | - | Computed: `!IsInternalVirtual`. Drives the Input Hiding section visibility. |
| `ShowInputModeSection` | `bool` | - | Computed: `IsGamepad && !IsInternalVirtual`. Drives the Input Mode (Force Raw Joystick) section visibility. |
| `ShowInputModeOrHidingSection` | `bool` | - | Computed: union of the two above. Gates the separator between Slot Assignment and the hiding/mode sections so a virtual device doesn't leave a dangling divider. |

### Device Path

| Property | Type | Description |
|----------|------|-------------|
| `DevicePath` | `string` | Device path (diagnostics). |
| `HidHideInstancePath` | `string` | HID instance path for HidHide blacklisting. |

### Display Helpers

| Property | Type | Description |
|----------|------|-------------|
| `IsGamepad` | `bool` | Computed: true if `DeviceTypeKey == "Gamepad"`. |
| `ShowSubmitMapping` | `bool` | Computed: the device can have a community mapping submitted. True for everything except `"Gamepad"`, `"Mouse"`, `"Keyboard"`, `"Touchpad"`, `"Midi"`, `"Nfc"`, `"HeadsetMotion"`, `"Microphone"`, and `"ConsumerControl"`. |

| Method | Description |
|--------|-------------|
| `NotifyDisplayChanged()` | Refreshes computed properties (`StatusText`, `CapabilitiesSummary`, `VendorIdHex`, `ProductIdHex`, `HasVidPid`). |

### SlotBadge

**File:** `DeviceRowViewModel.cs`

Slot assignment badge (icon + number).

| Property | Type | Description |
|----------|------|-------------|
| `SlotIndex` | `int` | Zero-based pad slot index. |
| `SlotNumber` | `int` | Sequential global number (1-based among created slots). |
| `VcType` | `VirtualControllerType` | The slot's output type, which picks the badge art below. |
| `TypeGeometry` / `TypeGlyph` | `Geometry` / `string` | Branded icon path, or the Segoe glyph for the types with no path (`SlotTypeIconMap`). |

---

## PadViewModel

**Files:** `PadViewModel.cs`, `PadViewModel.Touchpad.cs` (partial added in v3.3 for Touchpad-tab properties), `PadViewModel.Mouse.cs` (partial added for the #200 mouse-gesture tab), `PadViewModel.AudioDsp.cs` (partial added in 4.3.2 for the #347 Audio DSP chain)
**DataContext for:** Pad page (one per virtual controller slot)

The largest ViewModel. One per virtual controller slot (16 total). Handles output type, multi-device selection, mapping grid, deadzone/sensitivity, macros, force feedback, Touchpad-tab settings, and live state display.

### Identity and Type

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `PadIndex` | `int` | - | Zero-based slot index (0–15). Read-only. |
| `SlotNumber` | `int` | `PadIndex + 1` | 1-based number among active slots. |
| `SlotLabel` | `string` | - | Display label (e.g., `"Virtual Controller 1"`). |
| `OutputType` | `VirtualControllerType` | `Xbox` | Output type. Resets deadzones, rebuilds mappings/stick/trigger configs, syncs macro button style. |
| `TypeInstanceLabel` | `string` | `"1"` | Per-type instance label. Set by `RefreshNavControllerItems`. |
| `OutputTypeIndex` | `int` | - | ComboBox SelectedIndex, a plain cast over `OutputType`: `0`=Xbox, `1`=PlayStation, `2`=Extended, `3`=Midi, `4`=KeyboardMouse, `5`=Nintendo, `6`=Vr. The setter ignores any value `Enum.IsDefined` rejects. |
| `OutputTypeDisplayName` | `string` | - | Computed: localized type name for the tier-1 header. Re-raised on `OutputType` and culture changes. |
| `ConfigItemDirtyCallback` | `Action` | `null` | Called on config item change. Wired to `SettingsService.MarkDirty()`. |

### Extended Configuration

| Property | Type | Description |
|----------|------|-------------|
| `ExtendedConfig` | `ExtendedSlotConfig` | Per-slot Extended config (preset, axis/button/POV counts). Drives the HID descriptor handed to HIDMaestro for Extended slots. Only meaningful when `OutputType == Extended`. Subscribes to `PropertyChanged` for dynamic rebuilds. |

### MIDI Configuration

| Property | Type | Description |
|----------|------|-------------|
| `MidiConfig` | `MidiSlotConfig` | Per-slot MIDI config (channel, CC/note mappings). Only meaningful when `OutputType == Midi`. |

### Per-(Slot, Device) Lighting / Adaptive Trigger Configuration

Drives the Adaptive Triggers and Lighting tabs. Keyed per physical device, so two devices on one slot each carry their own lighting/trigger config. See [DeviceSlotConfig](#deviceslotconfig).

| Property | Type | Description |
|----------|------|-------------|
| `DeviceConfig` | `DeviceSlotConfig` | The Adaptive Triggers / Lighting tab's currently-bound config, following `SelectedMappedDevice`. The setter re-attaches its `PropertyChanged` forwarder (`ActiveDeviceConfigPropertyChanged`) on swap. |
| `PerDeviceSlotConfigs` | `IReadOnlyDictionary<Guid, DeviceSlotConfig>` | Per-device configs keyed by InstanceGuid. The empty-Guid key holds a fallback used before any device is mapped. |

| Method | Description |
|--------|-------------|
| `GetOrCreateDeviceConfig(Guid)` | Returns the per-device config, creating a fresh default entry if none exists. Empty Guid returns the anchor config. |
| `EnumerateDeviceSlotConfigs()` | Snapshot of every per-device config on the slot. Used by macro fan-out. |
| `EnsureDeviceSlotConfigsForMappedDevices()` | Adds a default config entry for every currently-mapped device. |

### Keyboard + Mouse Configuration (#205)

| Property | Type | Description |
|----------|------|-------------|
| `KbmConfig` | `KbmSlotConfig` | Per-slot SOCD / Snap Tap config. Always present, only meaningful when `OutputType == KeyboardMouse`. See [KbmSlotConfig](#kbmslotconfig). |

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

| Property | Type | Description |
|----------|------|-------------|
| `Name` | `string` | Device display name. |
| `InstanceGuid` | `Guid` | Device instance GUID. |
| `IsOnline` | `bool` | Device connected. Refreshed every dashboard tick so an offline roster line dims instead of rendering cold (#175 phase 2 item 14). |
| `BatteryText` | `string` | `"78%"` while the device reports a battery, else empty (#167). Shown per item in the Pad-page device dropdown. |
| `BatteryGlyph` | `string` | Segoe MDL2 battery glyph for the crucible card roster (#175). Same bucketing as `DeviceRowViewModel.BatteryGlyph`. Notifies `HasBattery`. |
| `HasBattery` | `bool` | Computed: `BatteryGlyph` is non-empty. |
| `TransportGlyph` | `string` | Segoe MDL2 transport glyph for the roster (#175): Bluetooth links carry `E702`, wired stays unmarked. Notifies `HasTransportGlyph`. |
| `HasTransportGlyph` | `bool` | Computed: `TransportGlyph` is non-empty. |
| `TypeGlyph` | `string` | Segoe MDL2 device-class glyph (#175), sourced from `DeviceTypeGlyph.For`. Defaults to the controller glyph (U+E7FC) until InputService resolves the device. |

### XInput Output State (Controller Visualizer)

Combined slot output values, updated at 30 Hz by `UpdateFromEngineState()`. Bound to the 2D/3D controller visualizer.

**Buttons (all `bool`):**

`ButtonA`, `ButtonB`, `ButtonX`, `ButtonY`, `LeftShoulder`, `RightShoulder`, `ButtonBack`, `ButtonStart`, `LeftThumbButton`, `RightThumbButton`, `ButtonGuide`, `DPadUp`, `DPadDown`, `DPadLeft`, `DPadRight`

Family extras on the same lane, each driving the 2D overlay and 3D mesh accent for the pads that carry the button: `ButtonShare` (Xbox Series), `ButtonMute` (DualSense mic mute), `LeftFunction` / `RightFunction` (DualSense Edge Fn), `ButtonC`, `LeftPaddle` / `RightPaddle` (Switch 2 Pro C, GL, GR, written by the raw bridge from wire indices 20, 19, 18).

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

**Per-device values (selected device only, for stick/trigger tab previews):**

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
| `MappingSet` | `MappingSet` | Per-virtual-controller mapping store (multi-source rows, shift layers, activators). Drives `Mappings` on layer / activator change. New in 3.2. See [Button and Axis Mappings](../features/mappings.md) and [Shift Layers](../guides/shift-layers.md). |
| `ActiveLayerMask` | `string` | Active shift layer mask. `Base` when no layer is engaged. UI rebinds the mapping grid on change. |
| `LayerTabs` | `ObservableCollection<ShiftLayerInfo>` | Tab strip entries above the mapping grid, one per layer (Base + each shift layer). Populated by `RebuildLayerTabs` from the slot's `ShiftActivators`. |
| `HasShiftLayers` | `bool` | True when at least one shift activator is authored (i.e. at least one tab beyond Base). |

| Event | Description |
|-------|-------------|
| `MappingsRebuilt` | Raised after `RebuildMappings()` completes so InputService can reload descriptors. |
| `LayerActivated` | Raised when `ActiveLayerMask` changes. Subscribers reload per-row source data so the DataGrid reflects the active layer's rows. |

### Slot-Level Picker Lists and Mapping Picker Filter (#322, discussion #302)

Slot-wide cross-device choice lists, plus the one search box and device-visibility set applied as the filter of the shared views every picker on the slot binds. A view filter changes what a dropdown offers, never what a row's binding holds, so saved selections survive filtering.

| Property | Type | Description |
|----------|------|-------------|
| `SlotAvailableInputs` | `ObservableCollection<InputChoice>` | Slot-level cross-device choice list, so the Gyro tab's Aim Engage picker and any other slot-wide picker binds without proxy-walking `Mappings`. Populated by `InputService.PopulateAvailableInputs`. |
| `SlotAvailableInputsView` | `ICollectionView` | Grouped view over the list, keyed on `InputChoice.DeviceLabel` for the picker's GroupStyle header. |
| `SlotMacroTriggerChoices` | `ObservableCollection<InputChoice>` | The subset of `SlotAvailableInputs` that converts to a `MacroItem.TriggerInputEntry` (raw buttons, POV directions, gamepad-layout axes, touchpad click, touchpad gestures), for the macro trigger dropdown (#177). |
| `SlotMacroTriggerChoicesView` | `ICollectionView` | Grouped view over the macro-trigger list, same `DeviceLabel` grouping. |
| `MappingInputSearch` | `string` | Find-as-you-type over the picker list. Session state, never persisted. Setting it re-applies the filter. |
| `PickerDeviceFilterEntries` | `ObservableCollection<PickerDeviceFilterEntry>` | The device-filter popup's rows, one per device group currently in the picker. |
| `MappingPickerFilterActive` | `bool` | Computed: any hidden device or non-empty search. Lets the funnel button read as engaged. |

| Method / Event | Description |
|----------------|-------------|
| `RebuildPickerDeviceFilterEntries()` | Rebuilds the popup rows from the shared list's current device groups, preserving each group's shown / hidden state. Called after every picker repopulation. |
| `SetHiddenPickerDeviceKeys(IEnumerable<string>)` | Restores the persisted hidden set on settings load. |
| `GetHiddenPickerDeviceKeysJoined()` | The persisted form: hidden keys, semicolon-joined. Stored per slot in the settings root, not in profiles. |
| `PickerDeviceFilterChanged` | Raised when the hidden set changes so the settings service can mark dirty and persist. |

The search filters both sides: the dropdown's offered choices, and the mapping grid's own rows. A row matches when its target label or its selected source's display name carries the text. Rows are outputs, so the device-visibility set never hides them, only typed text does.

`PickerDeviceFilterEntry` is one popup row: `Key` (device guid, or `"any"` for the device-agnostic group), `Label`, and a two-way `IsShown` whose setter toggles the owner's hidden set.

### Per-Device Test Routing (3.2)

Not a ViewModel property. `InputManager.TestRumbleTargetGuid` is a `Guid[MaxPads]` array holding, per slot, the InstanceGuid of the device currently visible in the per-device tabs (Impulse Triggers, Force Feedback, Adaptive Triggers, Lighting). InputService's test-send methods (`SendTestImpulseTrigger` and its siblings) set the slot's entry to the device GUID the pad page passed, and clear it back to `Guid.Empty` when the pulse ends. Test / Probe actions on those tabs gate on `target == Empty || ud.InstanceGuid == target` so only the selected physical pad fires, and `UserEffectsDispatcher.TestRumbleTargetGuidProvider` carries the same gate into the dispatcher branches that emit physical effects from those tabs (for example auto-routed impulse-to-AT vibration).

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

Per-(active device, pad-index) touchpad-tab settings. Same Load / Sync / guard rhythm as the gyro tuning partial: `Load*` reads `PadSetting.TouchpadSettings[]` into VM fields under the `_loadingTouchpadGestures` guard, setters push back through `PushIfNotLoading`, and `InputService` calls the sync method on the live polling rhythm so the gesture engine sees changes at once. Setter clamps in parentheses below.

**Active pad pivot** (devices with two pads, Steam Controller / Deck):

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `SelectedTouchpadIndex` | `int` | `0` | Which pad on the active device the tab edits (0..`MaxTouchpadIndex`-1). Changing it reloads VM fields from the matching `TouchpadSettings` entry. |
| `MaxTouchpadIndex` | `int` | `1` | Touchpad count on the active device (`0` when none). Private setter. |
| `HasMultipleTouchpads` | `bool` | - | Computed: `MaxTouchpadIndex > 1`. Shows the pad pivot. |
| `TouchpadIndexOptions` | `IEnumerable<int>` | - | `0..MaxTouchpadIndex-1` for the pivot ComboBox. |

**Detection card:**

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TouchpadGesturesEnabled` | `bool` | `false` | Master switch for the tab. |
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

**Reset commands:** every setting row carries a `Reset<Property>Command` that restores its default above, plus per-card `ResetTouchpadDetectionCardCommand`, `ResetTouchpadInBoxCardCommand`, `ResetTouchpadJoystickCardCommand`, `ResetTouchpadMouseCardCommand`, `ResetTouchpadPointerCardCommand`, `ResetTouchpadSwipeHapticsCardCommand`, and `ResetTouchpadSyntheticPressureCardCommand`. Defaults mirror `TouchpadGestureSettings.Default()`, so Reset to Defaults round-trips the tab by construction.

| Method | Description |
|--------|-------------|
| `LoadTouchpadGestureSettingsForActiveDevice()` | Reads the per-(device, pad) entry into VM fields under the load guard so setters don't ping-pong back. |
| `SyncTouchpadGestureSettingsToActiveDevice()` | Writes VM fields into the entry, creating it on first touch. No-op while loading, which stops an external `PropertyChanged` caller from clobbering not-yet-loaded fields. |
| `RecomputeTouchpadCountForActiveDevice(int)` | Sets `MaxTouchpadIndex` from the active device. `0` hides the tab. |
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

**Custom activation input (#216).** The recorded cross-device descriptor + owning device GUID that arm the Custom gesture session while held. Same pair shape, picker projection, and record flow as the Gyro tab's Aim Engage cluster, scoped per (slot, mouse device) with the rest of the card.

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
| `LoadMouseGestureSettingsForActiveDevice()` | Loads the active mouse device's gesture settings into the VM. Missing settings load as defaults, so Reset to Defaults resets this tab by construction. |
| `SyncMouseGestureSettingsToActiveDevice()` | Writes the VM fields into the active mouse device's entry, creating it on first touch. No-op while loading. |

### Force Feedback / Rumble

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `ForceOverallGain` | `int` | `100` | 0–100 | Overall FFB gain %. |
| `LeftMotorStrength` | `int` | `100` | 0–100 | Left motor strength %. |
| `RightMotorStrength` | `int` | `100` | 0–100 | Right motor strength %. |
| `SwapMotors` | `bool` | `false` | - | Swap left/right motor assignment. |
| `LeftMotorDisplay` | `double` | `0` | 0–1 | Live left motor level (post-scaling). |
| `RightMotorDisplay` | `double` | `0` | 0–1 | Live right motor level. |

**Audio Bass Rumble (per-device):**

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `AudioRumbleEnabled` | `bool` | `false` | - | Audio-driven rumble from system bass frequencies. |
| `AudioRumbleSensitivity` | `double` | `4.0` | 1–20 | Bass detection sensitivity multiplier. |
| `AudioRumbleCutoffHz` | `double` | `80.0` | 20–200 | Low-pass cutoff (Hz) for bass extraction. |
| `AudioRumbleLeftMotor` | `int` | `100` | 0–100 | Left motor strength for audio rumble. |
| `AudioRumbleRightMotor` | `int` | `100` | 0–100 | Right motor strength for audio rumble. |
| `AudioRumbleLevelMeter` | `double` | `0` | - | Live audio bass level meter. |

**Reset commands:** `ResetForceAllCommand`, `ResetOverallGainCommand`, `ResetLeftMotorCommand`, `ResetRightMotorCommand`, `ResetAudioRumbleAllCommand`, `ResetAudioSensitivityCommand`, `ResetAudioCutoffCommand`, `ResetAudioLeftMotorCommand`, `ResetAudioRightMotorCommand`.

**Constant Force (per-device, FFB-capable + scalar-rumble pads):**

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `ConstantForceEnabled` | `bool` | `false` | - | Apply a continuous force vector until toggled off. Resumes after game/macro forces stop. |
| `ConstantForceX` | `double` | `0` | −1.0–1.0 | X component of the force vector. |
| `ConstantForceY` | `double` | `0` | −1.0–1.0 | Y component (+ = up in the UI grid). |

### Audio DSP Chain (#347)

Audio-tab surface over the per-device crossfeed / EQ / limiter fields on `DeviceSlotConfig` (see the DeviceSlotConfig section below). Lives in `PadViewModel.AudioDsp.cs`. The cards are gated on `SelectedDeviceHasDspChain`.

| Member | Type | Description |
|--------|------|-------------|
| `SelectedDeviceHasDspChain` | `bool` (computed, `PadViewModel.cs`) | True when the selected device is a Sony pad whose audio rides an `AudioPassthroughService` sink, the only place the chain runs: DualSense family, or a DualShock 4 over Bluetooth. |
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

### Impulse Triggers Tab (3.2)

Per-pad-per-slot per-trigger-motor effects. Tab visible only when the selected device reports `HasRumbleTriggers`: SDL's `SDL_PROP_JOYSTICK_CAP_TRIGGER_RUMBLE_BOOLEAN` or a Microsoft impulse-trigger PID (`XboxControllerIdentity.IsImpulseTriggerDevice`). Xbox One and later pads.

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `ImpulseOverallGain` | `int` | `100` | 0–100 | Master scale for the trigger-motor pipeline. |
| `ImpulseLeftStrength` | `int` | `100` | 0–100 | Left trigger motor scale. |
| `ImpulseRightStrength` | `int` | `100` | 0–100 | Right trigger motor scale. |
| `ImpulseSwapTriggers` | `bool` | `false` | - | Swap left/right trigger motor assignment. |

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
| `AudioRumbleTriggersSensitivity` | `double` | `4.0` | 1.0–20.0 | Bass intensity multiplier (trigger channel). |
| `AudioRumbleTriggersCutoffHz` | `double` | `80.0` | 20–200 | Low-pass cutoff (trigger channel). |
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

### Gyro Tilt Envelope (#292)

Per-(slot, device) lens over the "Gyro Tilt X/Y" sources, the same shape as Flick Stick below. The save pipeline stamps these onto every tilt source (`ApplyGyroTiltParamsToRow`, the Motion Steering push pattern) and persists them in the PadSetting extended-mapping bag under `GyroTilt*` keys.

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `GyroTiltRangeDeg` | `double` | `25` | 1–180 | Physical tilt in degrees that reaches full deflection. 25 is the modal Steam-corpus maximum. The clamp admits the corpus outliers while the slider tops at 90. |
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
| `FlickOnEngage` | `bool` | `false` | - | Fire a flick immediately when evaluation starts with the stick already past threshold (the shift-layer engage case). Off arms at the current angle and only tracks rotation. |

**Reset commands:** one per row (`ResetFlickCountsPer360Command`, `ResetFlickTimeCommand`, `ResetFlickThresholdCommand`, `ResetFlickSnapModeCommand`, `ResetFlickSnapStrengthCommand`, `ResetFlickForwardDeadzoneCommand`, `ResetFlickSmoothingCommand`, `ResetFlickOnEngageCommand`) plus the card-level `ResetFlickStickCardCommand`.

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

Drive the `ItemsControl`-based Sticks and Triggers tabs. Gamepad presets: 2 sticks, 2 triggers. Custom Extended: N sticks, M triggers. KBM: 2 items (Mouse Movement, Scroll Wheel).

| Property | Type | Description |
|----------|------|-------------|
| `StickConfigs` | `ObservableCollection<StickConfigItem>` | Stick config items. Rebuilt by `RebuildStickConfigs()`. |
| `TriggerConfigs` | `ObservableCollection<TriggerConfigItem>` | Trigger config items. Rebuilt by `RebuildTriggerConfigs()`. |

| Method | Description |
|--------|-------------|
| `RebuildStickConfigs()` | Rebuilds stick configs for current output type. |
| `RebuildTriggerConfigs()` | Rebuilds trigger configs. KBM has none. |
| `SyncStickItemFromVm(StickConfigItem)` | Pushes VM deadzone properties into a stick item. |
| `SyncTriggerItemFromVm(TriggerConfigItem)` | Pushes VM trigger properties into a trigger item. |
| `SyncAllConfigItemsFromVm()` | Syncs all items from VM. Called after settings load/paste. |
| `ResetAllSettings()` | Resets per-slot settings to defaults. Called on slot deletion. |

### Macros

| Property | Type | Description |
|----------|------|-------------|
| `Macros` | `ObservableCollection<MacroItem>` | Macros for this slot. |
| `SelectedMacro` | `MacroItem` | Selected macro. Notifies `HasSelectedMacro`, refreshes remove command. |
| `HasSelectedMacro` | `bool` | Computed: `SelectedMacro != null`. |

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `AddMacroCommand` | always | Adds a new macro with auto-numbered name. |
| `RemoveMacroCommand` | `HasSelectedMacro` | Removes the selected macro. |

### Bass Shakers (#236)

The per-slot Bass Shakers tab surface, MappingSet-backed like Menus and persisted through the same dirty callback. `RumbleAudioTabVisible` gates the tab on slot type: Xbox, PlayStation, and Nintendo always, plus Extended slots whose surface carries force feedback (Customize on: the ForceFeedbackEnabled checkbox decides; Customize off: the catalog profile descriptor must carry a PID FFB block). The card binds `RumbleAudioEnabled`, `RumbleAudioEndpointId` (output device picker), `RumbleAudioChannelMode` (Mono / Controller Stereo), `RumbleAudioMasterGain`, and `RumbleAudioVoices`, an `ObservableCollection` of the four per-channel voice rows (Low Motor, High Motor, Left Trigger, Right Trigger: enable, 20–120 Hz frequency, gain, per-voice Test). The frequency sweep and Stop live beside the voices. Everything writes into `MappingSet.RumbleAudio` (`RumbleAudioConfig`), so the routing travels with profiles and Copy / Paste.

### Output tab: Slot SOCD (#245) and Keep Controller Awake

Both cards live on the Output tab (index 17). `OutputTabVisible` is a slot-type gate: every type except MIDI and VR, the two with no output-behavior surface at all.

Controller-button SOCD is distinct from `KbmSlotConfig`'s key SOCD (#205). `SocdCardVisible` and `KbmSocdCardVisible` are mutually exclusive by slot type. The card binds `SocdMode` over `MappingSet.SocdMode` (`AvailableSlotSocdModes`: Off / Last Wins / First Wins / Neutral), and `SocdPairItems` (`SlotSocdPairItem`) edits the opposing button pairs from `SocdButtonOptions`. The engine applies the cleaning to the combined output right before submit, on both the Gamepad bitmap and the raw-HID button words.

Keep Controller Awake holds a stick off-center so a console-style pad never idles out. Like the Bass Shakers config, it lives on the slot's `MappingSet` and every setter fires `ConfigItemDirtyCallback`.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `KeepAwakeCardVisible` | `bool` | - | Computed: Xbox and PlayStation slots only. |
| `KeepAwakeEnabled` | `bool` | `false` | Card master switch, over `MappingSet.KeepAwakeEnabled`. |
| `KeepAwakeAxis` | `string` | `"LX"` | Held axis, locale-stable: `LX`, `LY`, `RX`, `RY`. The default is stored as an empty string, so the getter substitutes `"LX"`. |
| `AvailableKeepAwakeAxes` | `IReadOnlyList<GyroLabeledOption>` | - | Axis picker options, reusing the stick-axis strings the mapping grid already localizes. |
| `KeepAwakeDeflection` | `int` | `25` | Held deflection percent, clamped 1–90. A persisted `0` means unset and reads as the engine default 25, so the card always shows the effective number. |

| Command | Description |
|---------|-------------|
| `ResetKeepAwakeAxisCommand` | Back to `"LX"`. |
| `ResetKeepAwakeDeflectionCommand` | Back to 25. |
| `ResetKeepAwakeCardCommand` | Disabled, axis and deflection back to their unset defaults, then `ReloadKeepAwake()`. |

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
| `MenuHostRecordCommand` | always | Raises `MenuHostRecordRequested`. |

| Event | Description |
|-------|-------------|
| `MenuHostRecordRequested` | Record button on the menu host picker. MainWindow runs the freeform recorder and folds the recorded descriptor onto a host choice (`MenuEditorItem.TryApplyRecordedHost`), the Aim Engage record shape. |

| Method | Description |
|--------|-------------|
| `ReloadMenus()` | Rebuilds `Menus` from the slot's live `MappingSet`. Called from `RebuildMappings()`, so profile applies, Workshop imports, output-type changes, and Reset to Defaults all refresh the tab. |

### Active Config Tab

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `SelectedConfigTab` | `int` | `0` | Always-visible: 0=Preview (the `TabController` RadioButton, `Tag="0"`, binds `Pad_Tab_Preview` = "Preview"), 1=Macros, 2=Mappings, 3=Sticks, 4=Triggers, 5=Force Feedback. Visibility-gated on the active source device's capability flags: 6=Adaptive Triggers (HasAdaptiveTriggers), 7=Lighting (HasLightbar), 8=Gyro (HasGyro), 9=Impulse Triggers (HasRumbleTriggers), 10=Touchpad (HasTouchpad), 11=Wheel, 12=Audio (`AudioTabIndex`), 13=Pointer (IR-capable Wii Remote, #146), 14=Mouse (source device is a mouse, #200). Slot-scope like tabs 0–2: 15=Menus (#9, always visible), 16=Bass Shakers (`BassShakersTabIndex`, gated on `RumbleAudioTabVisible`), 17=Output (`OutputTabIndex`, gated on `OutputTabVisible`). Tag values match the `RadioButton.Tag` strings on the PadPage tab strip. Entering 12 re-derives the sound-macro list and the mirror endpoints. Entering 16 re-enumerates render endpoints and re-seeds the voice rows. A gate that closes under the current selection evicts it back to tab 0. |

### Commands

| Command | CanExecute | Description |
|---------|-----------|-------------|
| `TestRumbleCommand` | `IsDeviceOnline` | Raises `TestRumbleRequested`. |
| `ClearMappingsCommand` | always | Clears all mapping source descriptors. |
| `CopySettingsCommand` | `HasSelectedDevice` | Raises `CopySettingsRequested`. |
| `PasteSettingsCommand` | `HasSelectedDevice` | Raises `PasteSettingsRequested`. |
| `CopyFromCommand` | `HasSelectedDevice` | Raises `CopyFromRequested`. |
| `MapAllCommand` | `HasSelectedDevice && !IsMapAllActive && SelectedMappedDevice.IsOnline` | Starts sequential "Map All" recording. |

### Map All System

| Property | Type | Description |
|----------|------|-------------|
| `IsMapAllActive` | `bool` | Map All recording in progress. |
| `MapAllCurrentIndex` | `int` | Current mapping row index during Map All. |
| `MapAllCurrentTarget` | `string` | Target setting name being recorded. |
| `MapAllPromptText` | `string` | Descriptive text shown on Controller tab during Map All (e.g., `"Press: A (1/21)"`). |
| `CurrentRecordingTarget` | `string` | `TargetSettingName` being recorded. Drives controller-tab flashing. |
| `MapAllRecordingNeg` | `bool` | Recording negative direction of a bidirectional axis. |

| Event | Args | Description |
|-------|------|-------------|
| `TestRumbleRequested` | `EventArgs` | Test rumble requested. |
| `TestLeftMotorRequested` | `EventArgs` | Test left motor only. Fired via `FireTestLeftMotor()`. |
| `TestRightMotorRequested` | `EventArgs` | Test right motor only. Fired via `FireTestRightMotor()`. |
| `CopySettingsRequested` | `EventArgs` | Copy settings to clipboard. |
| `PasteSettingsRequested` | `EventArgs` | Paste settings from clipboard. |
| `CopyFromRequested` | `EventArgs` | Copy from another device. |
| `MapAllRecordRequested` | `MappingItem` | Request recording for the current Map All item. |
| `MapAllCancelRequested` | `EventArgs` | Cancel an in-progress Map All recording. |

### State Update Methods

| Method | Description |
|--------|-------------|
| `UpdateFromEngineState(Gamepad, Vibration, Vibration selectedDeviceVibration = null)` | Updates combined slot output at 30 Hz. The optional third argument drives the selected device's own motor bars. |
| `UpdateDeviceState(Gamepad)` | Updates per-device stick/trigger values for tab previews. |
| `UpdateFromTouchpadState(in TouchpadState)` | Mirrors the combined touchpad state onto the `TouchpadFinger*` / `TouchpadClickPressed` preview properties. |
| `UpdateFromRawHidState(RawHidState)` | Publishes the combined raw-HID output for the Extended schematic. Skips the notification when axes, hardware axes, buttons, and POVs all match the last snapshot, so an idle slot does not re-arm a repaint at 30 Hz. On a Nintendo slot it also projects the raw state onto the Gamepad-shaped preview properties. |
| `UpdateFromMidiRawState(MidiRawState)` | Updates MIDI preview snapshot. |
| `OnMapAllItemCompleted()` | Advances Map All to next item after 500 ms delay. |
| `StopMapAll()` | Stops Map All, clears state, raises `MapAllCancelRequested`. |
| `RefreshCommands()` | Refreshes `CanExecute` for all commands. |

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

Single mapping row linking a physical input to an output target in the Pad page mapping grid.

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
| `AvailableInputs` | `ObservableCollection<InputChoice>` | Source dropdown choices, spanning every device assigned to the slot. Populated by InputService once per VC slot, not per device-dropdown change. Since #322 every row on a slot points at the ONE shared list (`UseSharedAvailableInputs`), so a keyboard-and-mouse tab switch no longer rebuilds a private copy and a grouped view per row. |
| `AvailableInputsView` | `ICollectionView` | The grouped view the XAML ComboBox binds to. `GroupDescriptions` carries one `PropertyGroupDescription` on `InputChoice.DeviceLabel`, so the picker renders one dropdown with device-name headers. The default view is one object per collection, so on the shared list every row lands on the same view and the grouping is configured once. |
| `SelectedInput` | `InputChoice` | Selected dropdown input. Updates `SourceDescriptor`. Empty sentinel triggers `ClearCommand`. Suppression flag prevents re-entrancy, and is held across the shared-list rebuild (`BeginSharedListRebuild` / `EndSharedListRebuild`) so a live ComboBox cannot write its own selection back through the TwoWay binding. |

| Event | Description |
|-------|-------------|
| `InputSelectedFromDropdown` | Input selected from dropdown (for display text resolution). |

### Recording

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `IsRecording` | `bool` | `false` | Recording mode active. Notifies `RecordButtonText`. |
| `RecordButtonText` | `string` | - | Computed: `"Record"` or `"Recording..."`. |

### Live Value Display

| Property | Type | Description |
|----------|------|-------------|
| `CurrentValueText` | `string` | Source input raw value. Updated at 30 Hz when visible. |

### Per-Mapping Deadzone

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `MappingDeadZone` | `int` | `50` | Axis activation threshold, clamped 1–100%. Input below this percentage is ignored for this mapping row. `0` is disallowed because it used to read as "unset" and silently reverted to 50. |
| `IsDeadZoneApplicable` | `bool` | - | Computed: true for axis-based mappings where a per-mapping deadzone is meaningful. |

| Command | Description |
|---------|-------------|
| `ResetDeadZoneCommand` | Resets `MappingDeadZone` to 50. |

`PadViewModel.ClearAllMappings` resets all mapping deadzones to 50.

### Options

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `IsInverted` | `bool` | `false` | Axis inverted. Calls `RebuildDescriptor()` to toggle `"I"` prefix. |
| `IsHalfAxis` | `bool` | `false` | Upper half of axis range only. Calls `RebuildDescriptor()` to toggle `"H"` prefix. |
| `IsBidirectional` | `bool` | `false` | With `IsHalfAxis`, fires on absolute deflection past the deadzone, either side of center. Persisted through `PadSetting.MappingBidirectional`, not a descriptor prefix, because the I/H prefixes are already spoken for. |
| `IsInvertApplicable` | `bool` | - | Computed: `!(IsHalfAxis && IsBidirectional)`. Mirroring around center already covers both directions. |
| `InvertOutput` | `bool` | `false` | Flip Output: invert what the row writes, for the half-axis reads where `Invert` is consumed as the half selector. Round-trips to `MappingSource.InvertOutput`. |
| `IsInvertOutputApplicable` | `bool` | - | Computed by the engine's own `InvertConsumedByHalfAxisRead` predicate against the prefix-stripped primary. Gates the Flip Output checkbox. |
| `ParamAccel` | `double` | `0` | Per-row acceleration exponent, clamped 0.0–5.0. Has `ResetParamAccelCommand`. Gated by `IsParamAccelApplicable`, which excludes the gravity-tilt family: those are position reads whose engine path applies only the curve / range channel (#292). |
| `GyroSensitivity` | `double` | `1.0` | Primary-source gyro multiplier, clamped 0.1–10. Gated by `IsGyroSource`, which excludes the gravity-tilt family. |
| `IsGyroLeanSource` | `bool` | - | Computed: the primary is a gravity-lean read (`"Gyro Lean X"` / `"Gyro Lean Y"`, #292). Gates the lean row's dial, which binds `Sensitivity`. |
| `MouseCursorSensitivity` | `double` | `1.0` | Primary-source cursor sensitivity, clamped 0.1–5. Gated by `IsMouseCursorSource`. |
| `IrPointerSensitivity` | `double` | `1.0` | Primary-source Wii IR-pointer sensitivity, clamped 0.1–5. Gated by `IsIrPointerSource`. |
| `Sensitivity` | `double` | `1.0` | Generic per-source knob for a plain Axis / Slider read, clamped 0.1–5. Gated by `IsGenericSensitivitySource`, mutually exclusive with the specialized gates above, and reused as the Gyro Lean dial under `IsGyroLeanSource`. |

### Commands

| Command | Description |
|---------|-------------|
| `ToggleRecordCommand` | Toggles recording. Raises `StartRecordingRequested` or `StopRecordingRequested`. |
| `ClearCommand` | Clears source, neg descriptor, resets `IsInverted`/`IsHalfAxis`. |
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
| `IsMultiSource` | `bool` | - | Computed: `ExtraSources.Count > 0` or the primary is not a trivial Direct source. |
| `VariableCount` | `int` | - | Computed: source-variable count the combine formula can reference (`1 + ExtraSources.Count`). |
| `CombineMode` | `string` | `""` | Per-row combine mode. Empty = per-target-type default (MaxAbs for axes, OR for buttons). Named modes: `MaxAbs`, `Sum`, `Average`, `OR`, `AND`, `XOR`, `StickTrim`, `Custom`. |
| `CombineExpression` | `string` | `""` | Custom formula, only meaningful when `CombineMode == "Custom"`. |
| `IsCustomCombine` | `bool` | - | Computed: `CombineMode == "Custom"`. |
| `ShouldShowCustomExpression` | `bool` | - | Computed: `IsMultiSource && IsCustomCombine`. |
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

Values: `Buttons`, `DPad`, `Triggers`, `LeftStick`, `RightStick`, `Touchpad`, `Motion`. `Motion` covers the bundled motion-passthrough rows (`MotionGyro` / `MotionAccel` targets), auto-created on Sony-class slots for every assigned gyro or accel-capable device and rendered as one combined Motion row when both sub-channels come from the same source. `Touchpad` rows are the one category `IsRecordable` excludes.

---

## MappingSourceItem

**File:** `MappingSourceItem.cs`

One source row within a multi-source `MappingItem` (#61). Represents a single `Engine.Data.MappingSource`, bound by the RowDetailsTemplate inside the Mappings DataGrid.

### Kind

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Kind` | `string` | `"Direct"` | Source kind: `Direct`, `Incremental`, `InvertOnHold`, `Ramped`. Notifies the `Is*Kind` computed flags. |
| `IsIncrementalKind` / `IsInvertOnHoldKind` / `IsRampedKind` | `bool` | - | Computed per-kind flags. |
| `UsesUpDownKeys` | `bool` | - | Computed: Incremental or Ramped (authored via an Up/Down key pair). |
| `IsKindDescriptorless` | `bool` | - | Computed: kinds where the main Descriptor/flags are unused (Incremental, InvertOnHold, Ramped). |
| `HasAnyBoundFeed` | `bool` | - | Computed: whether any input feeds this source, per kind. Mirrors the engine's SourceEvaluator dispatch. |

`KindOptions` (static) is the culture-cached list of `KindChoice { Value, Name }` for the Kind dropdown, keeping backend identifiers out of the UI.

### Source

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `DeviceGuid` | `string` | `""` | Device this source reads from. Empty = the picker's "(Any device)" group. |
| `DeviceLabel` | `string` | `""` | Friendly device name, shown inline below the per-source picker. |
| `DisplayDeviceLabel` | `string` | - | Computed device label honoring the "(Any device)" contract: a concrete-guid source prefers `SelectedInput.DeviceLabel` (recovers the friendly name when the stored label wasn't hydrated), an empty-guid source keeps its own label and never borrows a concrete device from a descriptor-only picker fallback. Read by the grid subtitle, the annotation overlays, and the pipeline-chip tooltip. |
| `Descriptor` | `string` | `""` | Input descriptor. Notifies the source-class flags below. |
| `SelectedInput` | `InputChoice` | `null` | Cross-device picker selection. Setting it writes both `DeviceGuid` and `Descriptor` in one shot. |
| `IsGyroSource` / `IsMouseCursorSource` / `IsIrPointerSource` / `IsMouseMotionSource` | `bool` | - | Computed from the descriptor prefix. Gate the matching per-source sensitivity sliders. `IsGyroSource` excludes the gravity-tilt family (#292). |
| `IsGyroLeanSource` | `bool` | - | Computed: the gravity-lean pair (`"Gyro Lean X"` / `"Gyro Lean Y"`, #292). Gates the lean row's dial, which binds `Sensitivity`, the field `ReadGyroLean` scales by. |
| `IsParamAccelApplicable` | `bool` | - | Computed: gates the per-source Acceleration slider. The continuous-source family minus the gravity-tilt pairs, whose engine path never applies `ParamAccel` (#292). |
| `IsButtonClassDescriptor` | `bool` | - | Computed: descriptor is button / POV / touchpad-click (bool-yielding). |
| `DirectionBadge` | `string` | - | Computed: `"→ +"` / `"← −"` for button-class sources, per `Invert`. Empty otherwise. |

### Options and per-source deadzone

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Invert` | `bool` | `false` | Axis / direction inverted. |
| `HalfAxis` | `bool` | `false` | Upper half of the range only. |
| `IsHalfAxisApplicable` | `bool` | - | Computed: Half applies to continuous-range sources (Axis, Slider, Touchpad X/Y/Pressure, Gyro, Mouse Motion). |
| `Bidirectional` | `bool` | `false` | With `HalfAxis`, fires on absolute deflection past the deadzone (either side of center). |
| `DeadZone` | `int` | `50` | Per-source axis-to-button threshold. Clamped 1–100 (0 is disallowed because it read as "unset"). |
| `IsDeadZoneApplicable` | `bool` | - | Computed: the source is an axis/slider (or an engine-owned continuous family) AND the parent target is a discrete output. |
| `ParentTargetIsDiscrete` | `bool` | `false` | Set by the parent `MappingItem` so `IsDeadZoneApplicable` knows the target class. |

### Kind parameters

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ParamUp` / `ParamDown` | `string` | `""` | Up / Down key descriptors for Incremental and Ramped. |
| `ParamRate` | `double` | `0.5` | Incremental step rate. |
| `ParamSticky` | `bool` | `true` | Incremental sticky hold. |
| `ParamMin` / `ParamMax` | `double` | `0` / `1` | Incremental output bounds. |
| `ParamModifier` | `string` | `""` | InvertOnHold modifier key descriptor. |
| `ParamAttackTime` | `double` | `0.30` | Ramped attack seconds (#111). Clamped 0–5. |
| `ParamReleaseTime` | `double` | `0.30` | Ramped release seconds (#111). Clamped 0–5. |
| `ParamAutocenter` | `bool` | `true` | Ramped: release ramps back to zero (#111). |
| `ParamReverseMultiplier` | `double` | `4.0` | Ramped reverse speed-up (#111). Clamped 1–10. |
| `GyroSensitivity` | `double` | `1.0` | Per-source gyro multiplier (Gyro descriptors). Clamped 0.1–10. |
| `MouseCursorSensitivity` | `double` | `1.0` | Per-source cursor sensitivity (#107, Mouse Position). Clamped 0.1–5. |
| `IrPointerSensitivity` | `double` | `1.0` | Per-source Wii IR-pointer sensitivity (#146). Clamped 0.1–5. |

### Per-source recording

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `IsRecording` | `bool` | `false` | Recording mode active. Notifies the record text/icon and the per-Param recording flags. |
| `RecordButtonText` / `RecordButtonIcon` | `string` | - | Computed record-button label / Segoe MDL2 glyph. |
| `IsRecordingParamUp` / `Down` / `Modifier` | `bool` | - | Computed: which Param field's record is armed, so only that button swaps to its Stop glyph. |

| Command | Description |
|---------|-------------|
| `ToggleRecordCommand` | Toggles primary-source recording (raises `StartRecordingRequested` / `StopRecordingRequested`). |
| `RecordParamUpCommand` / `RecordParamDownCommand` / `RecordParamModifierCommand` | Toggle recording for a specific Param field (raise `StartParamRecordingRequested` with a `ParamRecordTarget`). |
| `ClearCommand` | Resets descriptor + flags + deadzone to defaults, keeping the row in `ExtraSources`. |
| `ResetDeadZoneCommand`, `ResetGyroSensitivityCommand`, `ResetMouseCursorSensitivityCommand`, `ResetIrPointerSensitivityCommand` | Per-control resets. |

| Method | Description |
|--------|-------------|
| `ToDomain()` | Builds a domain `Engine.Data.MappingSource` from the VM. |
| `FromDomain(MappingSource)` | Static: populates a new VM from a domain source. |
| `SyncSelectedInputFromState(IEnumerable<InputChoice>)` | Syncs the picker selection from the current `(DeviceGuid, Descriptor)` pair. |

`ParamRecordTarget` (enum): `Up`, `Down`, `Modifier`.

---

## ShiftLayerInfo

**File:** `ShiftLayerInfo.cs`

VM wrapper around a single `Engine.Data.ShiftActivator`. Populates the nested tab strip on the Mappings tab (`PadViewModel.LayerTabs`) and the per-layer context-menu commands.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `LayerMask` | `string` | `"Base"` | Engine-side layer identity (matches `MappingRow.LayerMask`). |
| `LayerName` | `string` | `"Base"` | User-visible display name. |
| `Color` | `string` | `""` | v2 per-layer color hint, `"#AARRGGBB"` or empty. |
| `IsActive` | `bool` | `false` | True when this layer's tab is selected (the one being authored). |
| `IsBase` | `bool` | - | Computed: `LayerMask == "Base"`. The Base tab never shows delete / configure / rename. |

---

## MacroItem

**File:** `MacroItem.cs`

A trigger combination of inputs that produces a sequence of output actions. Evaluated between Step 3 (mapping) and Step 4 (combining).

### Identity

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Name` | `string` | `"New Macro"` | User-facing name. |
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

### Trigger Condition (Raw Device Button)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TriggerDeviceGuid` | `Guid` | `Guid.Empty` | Trigger source device. `Empty` = legacy Xbox bitmask. |
| `TriggerRawButtons` | `int[]` | `[]` | Raw button indices. All must be pressed. |
| `UsesRawTrigger` | `bool` | - | Computed: `TriggerDeviceGuid != Empty && TriggerRawButtons.Length > 0`. |

### Trigger Condition (POV Hat)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TriggerPovs` | `string[]` | `[]` | POV hat triggers as `"povIndex:centidegrees"` (e.g., `"0:0"` for POV 0 Up). |
| `UsesPovTrigger` | `bool` | - | Computed: `TriggerPovs.Length > 0`. |

### Trigger Condition (Axis)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TriggerAxisTargets` | `MacroAxisTarget[]` | `[]` | Axes that must all exceed threshold. Not serialized. |
| `TriggerAxisTargetList` | `string` | `null` | Serializable comma-separated form. |
| `TriggerAxisThreshold` | `int` | `50` | Threshold % (1–100). |
| `UsesAxisTrigger` | `bool` | - | Computed: `TriggerAxisTargets.Length > 0`. |
| `TriggerAxisDirections` | `MacroAxisDirection[]` | `[]` | Direction filter per axis. Parallel array. Not serialized. |
| `TriggerAxisDirectionList` | `string` | `null` | Serializable comma-separated form. |
| `TriggerAxisDirectionIndex` | `int` | - | UI index for direction (0=Any, 1=Positive, 2=Negative). Sets all uniformly. |

### Trigger Condition (Descriptor / Device-Free) (#9)

Descriptor entries carry the trigger shapes that have no raw-entry form: engine-read descriptors (`"Gyro Pitch"`, `"Touchpad 0 Finger 0 Down"`, `"Menu {id} Item {k}"`) evaluated through `SourceCoercion`'s button read with the same per-(device, slot) tuning a mapping row gets. Entry-list only, picked from the trigger dropdown, never recorded.

| Member | Type | Default | Description |
|--------|------|---------|-------------|
| `TriggerInputEntry.SourceDescriptor` | `string` | `null` | The engine-read descriptor on a trigger-entry row. Serialized through the pipe-joined `TriggerInputs` spec as `in:{guid}:sd:{descriptor}` (same tail escaping as gestures). |
| `TriggerInputEntry.DescriptorSource` | `MappingSource` | - | Cached wrapper for the descriptor so the 1 kHz trigger evaluation never allocates. Null when the entry isn't a descriptor entry. |
| `UsesDescriptorTrigger` | `bool` | - | Computed: any trigger entry carries a `SourceDescriptor`. |

An entry with `DeviceGuid == Guid.Empty` is device-free: the evaluator resolves it against whatever device sits on the macro's slot, and `TriggerDisplayText` renders it under the localized "(Any device)" sentinel (the same group the mapping picker uses).

### Trigger Options

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `TriggerMode` | `MacroTriggerMode` | `OnPress` | Twelve modes, ordinals pinned: `OnPress` (0), `OnRelease` (1), `WhileHeld` (2), `Always` (3), `CustomExpression` (4, v3.2), `HoldForMs` (5, On Long Press), `DoublePress` (6), `TriplePress` (7), `SinglePress` (8), `Toggle` (9), `Turbo` (10), `ShortPress` (11, On Short Press, #253). |
| `TriggerHoldMs` | `int` | `500` | (#244) Hold threshold shared by `HoldForMs` and `ShortPress`, the tap-vs-hold pair. Has its own Reset command. |
| `TriggerDoublePressMs` | `int` | `442` | (#244) Multi-press window for the Single / Double / Triple modes. Has its own Reset command. |
| `LayerMask` | `string` | `""` | (#253/#254) Per-macro shift-layer scope. Empty = fires on any layer. A layer name limits the macro to that layer, Base included. Bound to the Layer dropdown (`Macro_Layer` / `Macro_Layer_Any` strings), gated like mapping rows. |
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
| `RepeatMode` | `MacroRepeatMode` | `Once` | How actions repeat: `Once`, `FixedCount`, `UntilRelease`. |
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
| `AddActionCommand` | Adds a new `MacroAction` with default type `ButtonPress`. |
| `RemoveActionCommand` | Removes selected action (CanExecute: `SelectedAction != null`). |

| Event | Description |
|-------|-------------|
| `RecordTriggerRequested` | Trigger recording toggled. |

---

### MacroAction

**File:** `MacroItem.cs` (nested class)

Single action in a macro's sequence.

### Core Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `Type` | `MacroActionType` | `ButtonPress` | Action type. Notifies all `Is*Type` properties. |
| `DurationMs` | `int` | `50` | Hold/delay duration (ms). Min 0. |
| `DisplayText` | `string` | - | Computed: readable action summary. |

### Type-Check Properties (all computed, not serialized)

One `Is*Type` flag per action family, plus the rolled-up families the editor gates whole panels on (`IsAnyRumbleType`, `IsAnyAxisValueType`, `IsAnyVcButtonType`, `IsAnyKeyType`, and the rest). A representative set: `IsButtonType`, `IsKeyType`, `IsDurationType`, `IsAxisType`, `IsSystemVolumeType`, `IsAppVolumeType`, `IsMouseMoveType`, `IsMouseButtonType`, `IsContinuousAxisType`, `IsDeviceAxisSource`, `IsOutputAxisSource`.

### Button Action Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `ButtonFlags` | `ushort` | `0` | Xbox bitmask for gamepad presets. |
| `ButtonStyle` | `MacroButtonStyle` | `Xbox360` | Display name style. Not serialized. |
| `CustomButtonCount` | `int` | `11` | Numbered style button count. Not serialized. |
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
| `FormatKeyString(int[])` | Formats VK codes into `"{Key1}{Key2}..."` string. |

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
| `MouseAccumulator` | `float` | `0` | Fractional pixel accumulator for sub-pixel precision. |

### Axis Source Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `AxisSource` | `MacroAxisSource` | `OutputController` | Axis value source. |
| `SourceDeviceGuid` | `Guid` | `Guid.Empty` | InputDevice source: physical device GUID. |
| `SourceDeviceAxisIndex` | `int` | `-1` | InputDevice source: axis index in `InputState.Axis[]`. |

### Pressure-Scaled Turbo (#290)

Applies to the repeat-interval action family (`RepeatKeyWhileHeld`, `RepeatVcButtonWhileHeld`, the toggles pulsing under `PulseWhileLatched`, and the rest of the `IsRepeatIntervalType` set). While the gate is on, the repeat rate follows a physical analog source (DS3 button pressure, any trigger) instead of the fixed `IntervalMs`. `IntervalMs` becomes the fast end (full press) and `SlowIntervalMs` the slow end, interpolated in rate space so a light press is a defined slow rate.

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
| `DisconnectDeviceOptions` | `List<MacroDisconnectDeviceOption>` | - | Computed on read (`[XmlIgnore]`). Every known device on a Bluetooth path (`BluetoothLinkHelper.IsDisconnectTarget`). Populates the Specific-device picker. |

---

### Supporting Enums (MacroItem.cs)

**MacroTriggerMode** (ordinals pinned): `OnPress` (0), `OnRelease` (1), `WhileHeld` (2), `Always` (3), `CustomExpression` (4, v3.2), `HoldForMs` (5, On Long Press), `DoublePress` (6), `TriplePress` (7), `SinglePress` (8, deferred single), `Toggle` (9), `Turbo` (10), `ShortPress` (11, On Short Press, #253. Shares `TriggerHoldMs` with `HoldForMs` to compose tap-vs-hold on one button)

**MacroTriggerSource:** `InputDevice`, `OutputController`

**MacroRepeatMode:** `Once`, `FixedCount`, `UntilRelease`

**MacroActionType** (append-only, since the clipboard serializes these as ints, so members are never reordered): `ButtonPress`, `ButtonRelease`, `KeyPress`, `KeyRelease`, `Delay`, `AxisSet`, `SystemVolume`, `AppVolume`, `MouseMove`, `MouseButtonPress`, `MouseButtonRelease`, `MouseScroll`, `ToggleTouchpadOverlay` (v3.2), `LightbarColor` / `LightbarColorClear` / `LightbarModeSet` / `LightbarModeCycle` (v3.1+), `SetGyroEngaged` (#120), `Rumble` / `RumbleStop` (v3.1+), `RumbleTrigger` / `RumbleTriggerStop` (#102), `PlaySound` / `SoundStop` (#83), `MouseRecenter` (#108), `MouseFixPosition` (#109), `MouseLimitRegion` (#110), `DisconnectController` (#162), `RunProgram` (launch an external program/file), `TextBlock` (#201, Unicode text injection), `PointerModeCycle` / `PointerModeSet` (#203, Wii pointer mode), `GuideLedBrightness` (#209), `MoveMouseToScreenPosition` (33, #9), `RepeatKeyWhileHeld` (34), `RepeatVcButtonWhileHeld` (35), `ToggleVcButton` (36), `ToggleKey` (37), `GyroRecenter` (38), `AxisHold` (39), `MouseWheelTap` (40), `MouseNudge` (41), `CycleTapList` (42), `ToggleMouseButton` (43), `ToggleVcAxis` (44), `RepeatVcAxisWhileHeld` (45), `ToggleWheel` (46), `AxisAdd` (47, #237), `ComboBreak` (48, #237), `AxisSetLatched` (49, #251), `AxisLatchRelease` (50, #251), `AxisScale` (51, #251), `HeadphoneVolumeUp` (52), `HeadphoneVolumeDown` (53), `VoiceListenWhileHeld` (54, #317). The volume pair steps `DeviceSlotConfig.HeadphoneVolume` by 10% and clamps at the ends, persisting like any other Audio-tab edit. The append-only rule is stated in code beside the enum.

**MacroDisconnectTarget** (#162): `TriggeringDevice` (0), `SpecificDevice` (1), `SlotDevices` (2), `AllDevices` (3). Picks the disconnect victim: the trigger's device(s), one picked device, every Bluetooth device on the pad's slot, or every Bluetooth device PadForge knows.

**MacroLightbarHoldMode:** `Reactive`, `Sticky` (v3.1)

**MacroLightbarColorSource:** `Fixed`, `RandomHue`, `PaletteStep` (v3.1)

**MacroRumbleHoldMode:** `Reactive`, `Sticky` (v3.1)

**MacroMouseButton:** `Left`, `Right`, `Middle`, `X1`, `X2`

**MacroAxisTarget:** `None`, `LeftStickX`, `LeftStickY`, `RightStickX`, `RightStickY`, `LeftTrigger`, `RightTrigger`

**MacroAxisDirection:** `Any`, `Positive`, `Negative`

**MacroAxisSource:** `OutputController`, `InputDevice`

**MacroButtonStyle:** `Xbox360`, `DualShock4`, `Numbered`

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

### Identity and shape

| Property | Type | Description |
|----------|------|-------------|
| `Name` | `string` | User-facing name. |
| `Enabled` | `bool` | Menu active. |
| `KindIndex` | `int` | `0` = Radial, `1` = Grid (combo index = enum value). Switching to Grid forces `HasCenter = false`, both rebuild `Cells`. |
| `IsRadial` | `bool` | Computed: `Kind == MenuKind.Radial`. Gates the Center Cell checkbox. |
| `KindOptions` | `IReadOnlyList<MenuIntOption>` | Style combo items (`Menu_Style_*` resx). Instance accessor over a static backing field on purpose: WPF `{Binding}` resolves against the DataContext instance and never finds static properties. |
| `CellCount` | `int` | Cell count, clamped 1–20. Rebuilds `Cells`. |
| `HasCenter` | `bool` | Radial only: adds the center cell (index 0, Steam's "Radial Menu Center Button"), selected while inside the deadzone. Rebuilds `Cells`. |
| `FireTypeIndex` | `int` | Fire mode, clamped 0–3 over `FireOptions` (`Menu_Fire_*` resx): 0 On Click, 1 On Click Release, 2 On Touch Release, 3 While Hovered. |
| `EngageDeadzonePercent` | `int` | Engage deadzone, clamped 1–95. |

### Host surface

| Property | Type | Description |
|----------|------|-------------|
| `HostOptions` | `IReadOnlyList<MenuHostOption>` | The five built-in host surfaces: `Gamepad LeftStick`, `Gamepad RightStick`, `Touchpad 0`, `Touchpad 1` (labels from `Menu_Host_*` resx, touchpads displayed 1-based as "Touchpad 1" / "Touchpad 2"), and `Custom` for the devices the named surfaces cannot describe (joysticks, wheels, anything not detected as a gamepad). An authored descriptor outside that grammar is appended as its own entry so the selection never silently lies. Never gated on assignment or online state, because imported profiles land on slots with nothing assigned yet. |
| `SelectedHost` | `MenuHostOption` | Selected host. Defaults to the right stick when the stored descriptor matches nothing. Selecting a non-touchpad host resets `HostHalf` to 0. |
| `HostIsTouchpad` | `bool` | Computed from `SelectedHost`. Shows the Pad Half row. |
| `IsCustomHost` | `bool` | Computed: the Custom host is selected, which swaps in the `CustomX` / `CustomY` / `Click` pickers (`CustomXChoices`, `CustomXSelected`, `CustomXSubtitle`, and their Y and click twins) and their own record buttons. |
| `HostHalfOptions` / `HostHalfIndex` | list / `int` | Pad Half picker for touchpad hosts: 0 Whole Pad, 1 Left Half, 2 Right Half. Clamped 0–2. |
| `HostRecording` / `HostRecordIcon` | `bool` / `string` | Freeform-recorder state for the host record button: Stop glyph (`E71A`) while recording, Record (`E7C8`) while idle, mirroring the Aim Engage record button. |

| Method | Description |
|--------|-------------|
| `TryApplyRecordedHost(string)` | Folds a freeform-recorded descriptor onto a host choice: stick axis / click reads pick the stick, touchpad-family reads pick the pad. Returns false when the recorded input has no host surface (buttons, gyro, keys). |

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

**Per-row resets** (canon: every setting row has one): `ResetHostCommand` (right stick, whole pad, custom descriptors cleared), `ResetHostHalfCommand` (whole pad), `ResetStyleCommand` (Radial), `ResetFireCommand` (On Click), `ResetCellsCommand` (4 cells, no center), `ResetGeometryCommand` (50/50, scale 100%, opacity 90%, labels on), `ResetDeadzoneCommand` (25), plus `ResetCustomXCommand` / `ResetCustomYCommand` / `ResetClickCommand` for the Custom host's three inputs.

### MenuCellItem

**File:** `MenuEditorItem.cs`

One cell row in the menu editor: label + one direct binding (none / keyboard key / virtual-controller button). The `_item` reference is null until the cell has content.

| Property | Type | Description |
|----------|------|-------------|
| `Index` / `IsCenter` | `int` / `bool` | Cell position. `Header` renders "Center" or the localized "Cell {n}". |
| `Label` | `string` | Cell label. Setting it materializes the item entry, clearing it drops an otherwise-empty entry. |
| `HasIcon` / `IconName` / `IconImage` / `ShowIconGlyph` | `bool` / `string` / `ImageSource` / `bool` | Cell icon: the stored name, the resolved image, and the glyph fallback used when the name resolves to no image. |
| `BindingKind` | `int` | `0` none, `1` keyboard key, `2` VC button, derived from which field is set. Selecting a kind seeds a default (Space / `Gamepad.A`) and zeroes the other field. |
| `ShowKeyPicker` / `ShowButtonPicker` | `bool` | Computed from `BindingKind`. |
| `SelectedKeyVk` | `int` | Virtual-key code, choices from `KbmSlotConfig.GetKeyOptions()`. |
| `SelectedButtonFlag` | `int` | Xbox-family button flag, labels mirrored from the macro editor's `MacroButtonNames` table. |
| `ResetCellCommand` | `RelayCommand` | Clears label and binding (which drops the item entry). |

### MenuHostOption / MenuIntOption

**File:** `MenuEditorItem.cs`

`MenuHostOption` is one pickable host surface (`Descriptor`, `Label`, `IsTouchpad`). `MenuIntOption` is a generic labeled int option used by the style / half / fire / binding-kind / button combos (`Value`, `Label`). The key picker reuses `SocdKeyOption` from `KbmSlotConfig` instead. Both option types override `ToString()` with the label.

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
| `TriggerDeviceGuid` | `Guid` | Two-way selection target. `Guid.Empty` is the localized "Any device" sentinel. Getter/setter proxy `Data.TriggerDeviceGuid` and invoke the save callback on change. |
| `DeviceChoices` | `ObservableCollection<DeviceChoice>` | Persistent dropdown items: the "Any device" sentinel plus one per online, named `SettingsManager.UserDevices` entry. |
| `RebuildDeviceChoices()` | method | Rebuilds `DeviceChoices` in place from `SettingsManager.UserDevices`. Called from the page's DropDownOpened handler so newly-connected / disconnected devices surface without a row teardown. |

`ProfileChoice` and `DeviceChoice` are the same mutable-wrapper pattern as `SwitchProfileModeItem`: a stable key (`ProfileId` / `DeviceGuid`) plus a `DisplayName` that updates in place on culture change, with `ToString()` returning `DisplayName`. Selection is unaffected by a language switch because no item is added or removed.

### Button Combo Display

| Property | Type | Description |
|----------|------|-------------|
| `ButtonComboDisplay` | `string` (computed) | Human-readable trigger combo. Joins entries with " + ", resolving each to a friendly name (e.g., "A (Xbox Controller) + LT+ (Xbox Controller)"). During recording, appends countdown. |

Name resolution helpers:
- `ResolveButtonName(int index, Guid deviceGuid)`. Gamepad-type devices use standard names (A, B, X, Y, LB, RB, Back, Start, LS, RS, Guide) for indices 0–10. Keyboard devices resolve via `VirtualKey` enum. Others fall back to "Button N".
- `ResolveAxisName(int index, Guid deviceGuid, AxisTriggerDirection direction)`. Gamepad axes use LX/LY/LT/RX/RY/RT names with +/– suffix. Others use "Axis N+/–".
- `ResolveDeviceName(Guid deviceGuid)`. Returns `ResolvedName` from `UserDevices`, or `null` for `Guid.Empty`.

### Recording State

| Property | Type | Description |
|----------|------|-------------|
| `IsRecording` | `bool` | `true` during Learn mode. Raises `LearnButtonText` and `LearnButtonIcon`. |
| `RecordingCountdown` | `int` | Seconds remaining. Raises `ButtonComboDisplay` on change. |
| `LearnButtonText` | `string` (computed) | `"Recording..."` (`Profiles_ShortcutLearning`) or `"Record"` (`Profiles_ShortcutLearn`) |
| `LearnButtonIcon` | `string` (computed) | `\uE71A` (Stop) or `\uE7C8` (Record) |

| Method | Description |
|--------|-------------|
| `SetLearnedButtons(TriggerButtonEntry[] entries)` | Saves captured entries to `Data.TriggerEntries`, clears recording state, invokes save callback. |
| `CancelRecording()` | Clears `IsRecording` without saving. |
| `NotifyComboChanged()` | Raises `ButtonComboDisplay` for live display during recording. |

### Commands

| Command | Action |
|---------|--------|
| `DeleteCommand` | Invokes `_deleteCallback`. Removes this shortcut from the list. |
| `ClearCommand` | Sets `Data.TriggerEntries = null`, updates display, saves. |

---

## StickConfigItem

**File:** `StickConfigItem.cs`

One thumbstick section in the Sticks tab. Gamepad presets: 0 = Left, 1 = Right. Custom Extended: 0..N per `ThumbstickCount`.

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
| `CurvePresetNames` | `string[]` of available curve preset display names. Rebuilt on culture change. |

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
| `RawX` | `short` | `0` | Processed raw X. Notifies `RawDisplay`. |
| `RawY` | `short` | `0` | Processed raw Y. |
| `RawDisplay` | `string` | - | Computed: `"X: -1234 (50.0%)  Y: 5678 (58.7%)"`. |
| `LiveInputX` | `double` | `0` | CurveEditor X input (0–1). |
| `LiveInputY` | `double` | `0` | CurveEditor Y input. |

### Reset Commands

`ResetAllCommand`, `ResetDeadZoneShapeCommand`, `ResetCenterOffsetXCommand`, `ResetCenterOffsetYCommand`, `ResetDeadZoneXCommand`, `ResetDeadZoneYCommand`, `ResetAntiDeadZoneXCommand`, `ResetAntiDeadZoneYCommand`, `ResetLinearCommand`, `ResetSensitivityXCommand`, `ResetSensitivityYCommand`, `ResetMaxRangeXCommand`, `ResetMaxRangeYCommand`, `ResetMaxRangeXNegCommand`, `ResetMaxRangeYNegCommand`

### Static Methods

| Method | Description |
|--------|-------------|
| `ApplyCurve(double, string)` | Applies spline LUT curve to a magnitude. Used by preview and Extended raw output. |
| `BuildTriggerCurvePoints(string, double, double, int, int)` | Builds 0–1 curve points for trigger charts with deadzone flattened. Returns `PointCollection`. |

---

## TriggerConfigItem

**File:** `TriggerConfigItem.cs`

One trigger section in the Triggers tab. Gamepad presets: 0 = Left, 1 = Right. Custom Extended: 0..N per `TriggerCount`.

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
| `CurvePresetNames` | `string[]` of available curve preset display names. Rebuilt on culture change. |

### Live Preview

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `LiveValue` | `double` | `0` | Processed trigger value (0.0–1.0). |
| `RawValue` | `ushort` | `0` | Processed raw value. Notifies `RawDisplay`. |
| `RawDisplay` | `string` | - | Computed: formatted display `"32768 (50.0%)"`. |
| `LiveInputForCurve` | `double` | `0` | Live input for CurveEditor binding. |

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

The v2 `ExtendedPreset` enum (`Xbox360` / `DualShock4` / `Custom`) and the `ApplyPresetDefaults()` method that paired with it were dropped in v3 (commit `d57a725`). v3 picks layouts from the 225+ HIDMaestro profile catalog instead, with `Customize` as the single boolean that gates user overrides on top of the catalog profile.

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

Per-slot MIDI output configuration: CC/note counts, starting numbers, channel, and velocity.

| Property | Type | Default | Range | Description |
|----------|------|---------|-------|-------------|
| `Channel` | `int` | `1` | 1–16 | MIDI channel (1-based). |
| `CcCount` | `int` | `6` | 0–`128 - StartCc` | CC output count. |
| `StartCc` | `int` | `1` | 0–127 | Starting CC number. Re-clamps `CcCount`. |
| `NoteCount` | `int` | `11` | 0–`128 - StartNote` | Note output count. |
| `StartNote` | `int` | `60` | 0–127 | Starting note number. Re-clamps `NoteCount`. |
| `Velocity` | `byte` | `127` | 0–127 | Note velocity for button presses. |

| Method | Description |
|--------|-------------|
| `GetCcNumbers()` | Returns `int[]` of sequential CC numbers from `StartCc`. |
| `GetNoteNumbers()` | Returns `int[]` of sequential note numbers from `StartNote`. |

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

---

## DeviceSlotConfig

**File:** `DeviceSlotConfig.cs`

Per-(slot, device) output configuration. Renamed from `PlayStationSlotConfig` in commit `3fd97c89`. It is not PlayStation-only. Drives the Adaptive Triggers and Lighting tabs. Held per physical device on a slot (`PadViewModel.PerDeviceSlotConfigs`), so two devices on one slot each carry their own config. Parallel to `ExtendedSlotConfig` and `MidiSlotConfig`: `ObservableObject` with a paired `[XmlAttribute]` data record.

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
| `LightbarEnabled` | `bool` | `false` | Master toggle for the user-configured base color. Off leaves whatever the game last wrote. |

### Audio mirror / speaker passthrough (#83)

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `AudioPassthroughEnabled` | `bool` | `false` | Mirror the system audio to this pad's built-in speaker (per device). |
| `AudioMirrorSourceId` | `string` | `""` | MMDevice ID of the render endpoint to capture. Empty = the system default. |

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
| `AudioPersonaHapticsEnabled` | `bool` | `false` | Render the virtual DualSense's authored haptic audio (persona UAC channels 3/4) on this device's actuators through the haptic-tone chain. Off by default because the derived tones only approximate the designer's track. |
| `AudioPersonaHapticsGain` | `int` | `100` | Input gain percent (25–300) applied before the tone reducer, so a quiet authored track can still reach the actuators. |

Reset commands: `ResetPersonaHapticsCommand`, `ResetPersonaHapticsGainCommand` (both on `PadViewModel`, alongside the Audio tab's other row resets).

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
| `HeadphoneVolume` | `int` | `100` | Headphone-jack hardware volume percent, clamped 0–100. Maps onto the DS5 output report's VolumeHeadphones byte over Sony's own scePad window. `0%` writes `0x00`. Owned by the Audio-tab card and the `HeadphoneVolumeUp` / `HeadphoneVolumeDown` macro actions. |
| `AudioOutputPath` | `AudioOutputPath` | `Automatic` | Where the DualSense plays its audio (output report byte 7 bits 4–5). |
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
| `ClearMacroOverride()` | method | - | Releases a Sticky override. |

### Mic LED

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `MicLedMode` | `MicLedMode` | `Off` | Mic-mute LED state. Notifies `IsMicLedFollowDevice`. |
| `MicLedFollowDeviceId` | `string` | `""` | CoreAudio endpoint id polled by `FollowDeviceMute`. |
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
| `GuideLedMode` | `GuideLedMode` | `DeviceDefault` | DeviceDefault never writes, Fixed holds `GuideLedBrightness`, Battery tracks battery percent. Xbox One+ pads take the GIP LED command over `\\.\XboxGIP` (USB only). The 2015 Steam Controller takes SDL's home-LED hint. Notifies `IsGuideLedFixed`. |
| `IsGuideLedFixed` | `bool` | - | Computed: mode is `Fixed`. Gates the brightness slider. |
| `GuideLedBrightness` | `int` | `100` | Fixed-mode brightness percent. Clamped 0–100. Writers scale it onto each device's range. |

### Lightbar mode and animation

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `LightbarMode` | `LightbarMode` | `PlayerNumber` | Base lightbar effect. Idle modes (Off, Static) only work on config change. Animated modes run the dispatcher's ~30 Hz timer. |
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

### Enums and helper classes (DeviceSlotConfig.cs)

**AdaptiveTriggerMode:** `Off`(0), `Feedback`(1), `Weapon`(2), `Vibration`(3), `MultiplePositionFeedback`(4), `SlopeFeedback`(5), `MultiplePositionVibration`(6). Sony's seven PS5 SDK effect modes.

**AudioOutputPath:** `Automatic`(0), `StereoHeadset`(1), `MonoHeadset`(2), `HeadsetAndSpeaker`(3), `SpeakerOnly`(4), `FollowHeadphoneJack`(5). Values 1–4 map to firmware paths 0–3, the four names in duaLib's scePad surface. `Automatic` writes nothing and keeps the #83 behavior: firmware routing, with PadForge forcing the speaker only while it plays sounds there. `FollowHeadphoneJack` tracks the pad's own jack detect. The jack bit is read by `AudioPassthroughService`'s sink-owned `JackWatch` on either transport (USB input report 0x01 or Bluetooth 0x31, the duaLib PluggedHeadphones status bit), independent of any persona lane. Plugged resolves to `StereoHeadset`, unplugged to `SpeakerOnly`, and no reading to the default. Persisted numerically, so the members are append-only.

**MicLedMode:** `Off`(0), `Solid`(1), `Pulse`(2), `FollowDeviceMute`(3).

**PlayerLedMode:** `Off`(0), `Player1`(1), `Player2`(2), `Player3`(3), `Player4`(4), `All`(5), `PlayerNumber`(6, default). Sequential to map 1:1 with the dropdown.

**PlayerLedBrightness:** `High`(0), `Medium`(1), `Low`(2).

**GuideLedMode** (#209): `DeviceDefault`(0), `Fixed`(1), `Battery`(2).

**LightbarMode:** `Off`(0), `Static`(1), `Breathing`(2), `Rainbow`(3), `ColorCycle`(4), `AudioPulse`(5), `AudioPulseRandom`(6), `AudioPulseRainbow`(7), `AudioThresholds`(8), `AudioGradient`(9), `AudioCrossFade`(10), `InputReactive`(11, legacy), `InputReactiveCycle`(12, legacy), `InputReactiveFixed`(13, legacy), `Battery`(14), `Strobe`(15), `PlayerNumber`(16, default). Legacy 11–13 stay in the enum for XML round-trip and are migrated to `InputReactiveMode` on load.

**InputReactiveMode:** `Off`(0), `Random`(1), `Cycle`(2), `Fixed`(3).

**AudioLightbarMode:** `Pulse`(0), `Thresholds`(1), `Gradient`(2), `CrossFade`(3).

**MicLedDeviceItem:** `Id` (CoreAudio endpoint string), `Display` (label, prefixed `[In]` / `[Out]`).

**LightbarPaletteEntry** (`ObservableObject`): `R`, `G`, `B` (byte), `Hex` (two-way `"RRGGBB"` shim, `[XmlIgnore]`).

### DeviceSlotConfigData

Serializable DTO. All scalar properties are `[XmlAttribute]`. The two palettes are `[XmlArray]`. Key defaults: `LeftEndPosition`/`RightEndPosition` = 255, `LeftStrength`/`RightStrength` = 200, `LeftFrequency`/`RightFrequency` = 10, `LightbarBlue` = 0xFF, `AudioMirrorEngageMode` = "Always", `AudioMirrorEngageReleaseMs` = 500, `AudioToneFilterMode` = "Off", `AudioToneLimitHz` = 800, `AudioPersonaHapticsEnabled` = false, `AudioPersonaHapticsGain` = 100, `HeadphoneVolume` = 100 (a missing attribute on legacy XML keeps the initializer, so old configs load at full volume, the pre-feature effective behavior), `Ds5AudioBufferLength` = 48, `AudioOutputPath` = Automatic, `AudioCrossfeedLevel` = 0, `AudioCrossfeedCutHz` = 700, `AudioCrossfeedFeedDb` = 4.5, `AudioEqEnabled` = false, `AudioEqBands` = "", `AudioEqPreampDb` = 0, `AudioLimiterEnabled` = true, `AudioLimiterCeiling` = 98, `GuideLedMode` = DeviceDefault, `GuideLedBrightness` = 100, `LightbarMode` = Off (the DTO default, migrated to PlayerNumber via `LightingRev`), `PlayerLedMode` = Off (likewise). It also carries a `DeviceGuid` (per-device key, empty = a legacy slot-level entry the loader fans out) and `LightingRev` (schema revision: 0 predates the PlayerNumber default and triggers the Off→PlayerNumber lift on load). `LightbarPaletteEntryData` is the palette element (`R`, `G`, `B` byte attributes).

---

## KbmSlotConfig

**File:** `KbmSlotConfig.cs`

Per-slot keyboard + mouse output config (discussion #205, SOCD / Snap Tap). Same per-slot lane as `MidiSlotConfig`: lives on `PadViewModel.KbmConfig`, referenced into the engine by InputService, persisted as `KbmSlotConfigData`.

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `SocdMode` | `string` | `"Off"` | Resolution mode: `Off`, `LastWins`, `Neutral`, `FirstWins`. Stored locale-stable. |
| `SocdPairs` | `string` | `"87:83\|65:68\|38:40\|37:39"` | Pipe-separated `"vkA:vkB"` decimal pairs (the `DefaultSocdPairs` constant: W/S, A/D, Up/Down, Left/Right). |
| `SocdPairItems` | `ObservableCollection<SocdPairItem>` | - | Editable projection of `SocdPairs` for the pair editor. |
| `AvailableSocdModes` | `IReadOnlyList<SocdModeOption>` | - | Culture-cached dropdown items. |

| Constant | Value |
|----------|-------|
| `DefaultSocdPairs` | `"87:83\|65:68\|38:40\|37:39"` |

| Command | Description |
|---------|-------------|
| `AddSocdPairCommand` | Appends a fresh W/S pair. |
| `RemoveSocdPairCommand` | `RelayCommand<SocdPairItem>`. Removes the passed pair. |
| `ResetSocdCommand` | Resets `SocdMode` to Off and `SocdPairs` to `DefaultSocdPairs` in place. |

| Static Method | Description |
|---------------|-------------|
| `GetKeyOptions()` | Culture-cached `SocdKeyOption` list, the same key set and labels as the KBM mapping targets. |

**Companion classes:**
- `SocdModeOption` carries `Value` (engine-stable), `Name`, and `Description`. Localized dropdown entry.
- `SocdKeyOption` carries `Vk` (int) and `Label`. One pickable key.
- `SocdPairItem` (`ObservableObject`) carries `VkA` and `VkB`. Edits reserialize the owner's `SocdPairs`. `KeyOptions` returns `GetKeyOptions()`.
- `KbmSlotConfigData` is the DTO with `[XmlAttribute]` `SlotIndex`, `SocdMode` (default "Off"), and `SocdPairs` (default `DefaultSocdPairs`).

---

## RemoteLinkTrustedPeer

**File:** `RemoteLinkTrustedPeer.cs`

One trusted peer in the Settings paired-peer manager (#138). The name is editable (committed on focus loss, persisted to the trust store). The online dot refreshes in place so editing isn't disrupted.

| Property | Type | Description |
|----------|------|-------------|
| `Name` | `string` | Friendly name. Setting it persists the rename via the callback. Empty falls back to the host name. |
| `HostName` | `string` | The peer's machine name. `HasHostName` gates showing it. |
| `IsOnline` | `bool` | Live-session state. Notifies `OnlineText`, `CanConnect`. |
| `OnlineText` | `string` | Computed localized "Online" / "Offline". |
| `ReachableHostPort` | `string` | Where the peer is reachable now (host:port from discovery), or null. Notifies `CanConnect`. |
| `CanConnect` | `bool` | Computed: on the LAN but not connected. Shows the Connect button. |
| `FingerprintHex` | `string` | Full key fingerprint. |
| `FingerprintDisplay` | `string` | Computed: short grouped fingerprint, with a gamepad-only suffix when applicable. |
| `PairedUtc` | `string` | Pairing timestamp. |
| `GamepadOnly` | `bool` | Whether the peer is restricted to gamepad input. |

| Command | Description |
|---------|-------------|
| `ConnectCommand` | Reconnect to this known peer (no SAS prompt). |
| `RevokeCommand` | Revoke trust (raises the revoke callback with the fingerprint). |

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
- [XAML Views](xaml-views.md): View counterparts: `DashboardPage`, `PadPage`, `DevicesPage`, `SettingsPage`
- [Services Layer](services-layer.md): `InputService`, `SettingsService`, `DeviceService` consumed by ViewModels
- [Engine Library](engine-library.md): `Gamepad`, `RawHidState`, `KbmRawState`, `VrRawState`, `MidiRawState`, `PadSetting`
- [Settings and Serialization](settings-and-serialization.md): `SettingsManager` data synced to/from ViewModels by `SettingsService`
- [Input Pipeline](input-pipeline.md): `InputManager` state reflected in `PadViewModel` output snapshots
- [2D Overlay System](2d-overlay-system.md): `ControllerModel2DView`, `ControllerSchematicView` bound to `PadViewModel`
- [3D Model System](3d-model-system.md): `ControllerModelView` bound to `PadViewModel`

---

*Last updated for PadForge 4.3.2.*
