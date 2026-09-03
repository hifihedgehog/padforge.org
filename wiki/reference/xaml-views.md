# XAML Views Reference

*The main window shell, the page hierarchy, the dialog windows, custom controls, value converters, and how themes switch at runtime.*

> **v4 (2026-07-12):** Updated for the v4 ember restyle (#175). The HIDMaestro SDK surface, OpenXInput shim, thread-pool lifecycle, and bubble-up cascade live on [HIDMaestro Deep Dive](hidmaestro-deep-dive.md). If anything here drifts from the live source, the live source wins.

---

All views live in `PadForge.App/Views/` (`PadForge.Views` namespace), except `MainWindow.xaml` in `PadForge.App/`. Shared custom controls sit alongside them in `PadForge.App/Controls/` (`CurveEditor`, `TriggerTravelArc`, plus the code-only `RangeSlider` and `EqCurveControl`) and `PadForge.App/Views/Controls/` (`LabeledShapeIcon`, `ProfilePill`, `TriggerEffectGraph`). Styled with [WPF UI 4.3 (Lepo.Wpf.Ui)](https://github.com/lepoco/wpfui) for Fluent 2 design.

## Contents

- [Application Shell (MainWindow)](#application-shell-mainwindow)
- [DashboardPage](#dashboardpage)
- [PadPage](#padpage)
- [DevicesPage](#devicespage)
- [KBMPreviewView](#kbmpreviewview)
- [MidiPreviewView](#midipreviewview)
- [VRPreviewView](#vrpreviewview)
- [MousePreviewControl](#mousepreviewcontrol)
- [SettingsPage](#settingspage)
- [ProfilesPage](#profilespage)
- [ProfileSwitchOverlay](#profileswitchoverlay)
- [AboutPage](#aboutpage)
- [Dialog Windows](#dialog-windows)
- [Value Converters](#value-converters)
- [Resource Dictionaries and Theming](#resource-dictionaries-and-theming)
- [Common XAML Patterns](#common-xaml-patterns)
- [Code-Behind Patterns](#code-behind-patterns)

---

## Application Shell (MainWindow)

**Files:** `MainWindow.xaml`, `MainWindow.xaml.cs`

Application shell: app branding bar, NavigationView sidebar, page content area, status bar, and driver overlay.

### App Branding Bar

A custom branding bar replaces the traditional title bar. `Grid x:Name="AppBrandingBar"` (48px tall) holds a hamburger `Button` (`PaneToggleBtn`) on the left and a `ui:TitleBar` (`AppTitleBar`) that carries the PadForge icon + name in its header and native minimize/maximize/close with Snap Layout support. The window sets `ExtendsContentIntoTitleBar="True"` and `WindowBackdropType="Mica"`. The full-screen toggle (`FullScreenBtn`) in the title bar's trailing content sets `WindowChrome.IsHitTestVisibleInChrome="True"` so it stays clickable in the non-client area. The hamburger button carries no such attribute.

The window ground is Mica plus a `SteelLayer` (`Grid.RowSpan="3"`, hit-test-invisible): a near-black steel fill with a faint ember wash top-right and a cold wash on the left. `UpdateSteelLayer` collapses it in Light theme. The old `SyncBarBackgrounds` pane-sampling scheme and the `TranslateTransform.Y = -12` gap-closing transform are gone.

### XAML Structure

Three-row `Grid`:
- **Row 0 (auto):** App branding bar (`AppBrandingBar`: hamburger + `ui:TitleBar`).
- **Row 1 (star):** `NavigationView` with page containers in its `ContentOverlay`.
- **Row 2 (auto):** Status bar `Border` (`StatusBarBorder`).
- **Full-window layers (`Grid.RowSpan="3"`):** `SteelLayer` (ground), `DriverOverlay` (ZIndex 1000), `FirstRunOverlay` (ZIndex 900), `ShutdownOverlay` / `StartupOverlay` (ZIndex 1001).

```xml
<Grid>
    <Grid.RowDefinitions>
        <RowDefinition Height="Auto"/>  <!-- Branding bar -->
        <RowDefinition Height="*"/>     <!-- NavigationView -->
        <RowDefinition Height="Auto"/>  <!-- Status bar -->
    </Grid.RowDefinitions>

    <Grid x:Name="SteelLayer" Grid.RowSpan="3" IsHitTestVisible="False"> <!-- ember steel ground --> </Grid>

    <Grid x:Name="AppBrandingBar" Grid.Row="0" Height="48"> <!-- Hamburger Button + ui:TitleBar --> </Grid>

    <ui:NavigationView x:Name="NavView" Grid.Row="1" PaneDisplayMode="Left" OpenPaneLength="244"
                       IsBackButtonVisible="Collapsed" IsPaneToggleVisible="False"
                       AlwaysShowHeader="False" CompactPaneLength="48">
        <ui:NavigationView.FooterMenuItems>
            <ui:NavigationViewItem x:Name="NavSettings" Tag="Settings"/>
            <ui:NavigationViewItem x:Name="NavAbout" Tag="About"/>
        </ui:NavigationView.FooterMenuItems>
        <ui:NavigationView.ContentOverlay>
            <Grid>
                <views:DashboardPage x:Name="DashboardPageView" Visibility="Visible"/>
                <views:PadPage x:Name="PadPageView" Visibility="Collapsed"/>
                <views:DevicesPage x:Name="DevicesPageView" Visibility="Collapsed"/>
                <views:SettingsPage x:Name="SettingsPageView" Visibility="Collapsed"/>
                <views:ProfilesPage x:Name="ProfilesPageView" Visibility="Collapsed"/>
                <views:AboutPage x:Name="AboutPageView" Visibility="Collapsed"/>
            </Grid>
        </ui:NavigationView.ContentOverlay>
    </ui:NavigationView>

    <Border x:Name="StatusBarBorder" Grid.Row="2"> <!-- Status bar (5 columns) --> </Border>
    <Grid x:Name="DriverOverlay" Grid.RowSpan="3" Panel.ZIndex="1000"> <!-- ... --> </Grid>
</Grid>
```

### Navigation Model

No WPF `Frame`-based navigation. All pages are instantiated once and visibility-swapped:

1. `NavView_SelectionChanged` reads the selected item's `Tag` string.
2. All page containers set to `Visibility.Collapsed`.
3. The matching page set to `Visibility.Visible`.
4. For controller slots (tag `"Pad:{index}"`), PadPage's `DataContext` is set to the matching `PadViewModel`.

This preserves control state (scroll position, selected tabs, text fields) across navigation since pages are never destroyed.

### Sidebar Construction

NavigationView items use 48px height and 14px font size. Dashboard, Profiles, and Devices are built programmatically in `BuildNavigationItems()`. Settings and About are declared in XAML as `FooterMenuItems` (`NavSettings` / `NavAbout`) with ember-colored icons, not as `BuildNavigationItems` entries. Items (in order):

| Tag | Content | Icon | Source |
|-----|---------|------|--------|
| `Dashboard` | Dashboard | `F404` FontIcon (home) | `BuildNavigationItems()` |
| `Profiles` | Profiles | `E8F1` FontIcon (people) | `BuildNavigationItems()` |
| `Devices` | Devices | `E772` FontIcon (USB) | `BuildNavigationItems()` |
| `Settings` | Settings | `E713` FontIcon (gear) | XAML footer (`NavSettings`) |
| `About` | About | `E946` FontIcon (info) | XAML footer (`NavAbout`) |

Dynamic controller cards are appended after "Devices" (index 3 onward) via `RebuildControllerSection()`. Each `NavigationViewItem` contains:
- Power/type glyph plus a mini type segment: Xbox / PlayStation / Nintendo / Extended / KB+M / MIDI / VR tiles in `VirtualControllerGroups.InOrder`, active type lit, plus a fixed-width "#N" instance token. The MIDI tile is disabled without Windows MIDI Services and the VR tile without SteamVR, unless the slot already carries that type
- Slot label ("Controller 1", etc.)
- Device name subtitle
- Delete button (visible on hover)

Called on slot create, delete, or reorder. Uses a `_rebuildingControllerSection` guard to prevent re-entrancy during selection changes.

### Sidebar Drag Reordering

Drag controller cards to reorder virtual controller slots:

1. `OnCardDragStart`. `PreviewMouseLeftButtonDown` records start position.
2. `OnNavViewDragMove`. `PreviewMouseMove` checks threshold, then `BeginCardDrag()` creates a `CardDragAdorner` (ghost preview) and `InsertionLineAdorner` (drop indicator).
3. `UpdateDragPosition`. Updates adorner positions, computes target index.
4. `EndCardDrag`. `PreviewMouseLeftButtonUp` completes the swap via `InputService.SwapSlots(padIndexA, padIndexB)`.

### Cross-Panel Device Drag-Drop

Drag devices from the Devices page to a sidebar controller card:
- `DevicesPage` initiates `DragDrop.DoDragDrop()` with a `DataObject` keyed `"DeviceInstanceGuid"` carrying the device's `InstanceGuid` (a `Guid`).
- Sidebar `NavigationViewItem` handlers (`DragOver`, `Drop`) accept the drop and assign the device.

### Add Controller Popup

`Popup` with one button per output type, built in `ShowControllerTypePopup`. Re-invoking the method while the popup is open closes it rather than opening a duplicate, and a reopen inside 300 ms of the last close is suppressed, so the same click cannot dismiss and re-raise it. The seven buttons follow `VirtualControllerGroups.InOrder`:

| Button | AutomationId | Icon | Per-type cap |
|--------|--------------|------|--------------|
| Xbox | `AddXbox360Btn` | Xbox SVG | `SettingsManager.MaxXbox360Slots` (16) |
| PlayStation | `AddDS4Btn` | DS4 SVG | `SettingsManager.MaxPlayStationSlots` (16) |
| Nintendo | `AddNintendoBtn` | Switch logo SVG | `SettingsManager.MaxNintendoSlots` (16) |
| Extended | `AddRawBtn` | Joystick SVG | `SettingsManager.MaxExtendedSlots` (16) |
| Keyboard+Mouse | `AddKeyboardMouseBtn` | `E961` glyph | `SettingsManager.MaxKeyboardMouseSlots` (16) |
| MIDI | `AddMidiBtn` | `E8D6` glyph | `SettingsManager.MaxMidiSlots` (16) |
| VR | `AddVrBtn` | `F119` glyph | `SettingsManager.MaxVrSlots` (1) |

The method counts each type from `Pads[].OutputType` and disables a button (opacity 0.35, "(max N)" tooltip, e.g. `Main_Nintendo_Max_Format` = "Nintendo (max {0})") when the global slot total reaches 16 or that type hits its own per-type cap. MIDI additionally requires Windows MIDI Services (`DriverInstaller.IsMidiServicesInstalled()`) and VR requires SteamVR (`HMaestroVRController.IsAvailable()`). `HasAnyControllerTypeCapacity()` is a separate check: it tallies created slots from `SettingsManager.SlotCreated` and returns true while the total stays under 16 (`MaxPads`). The same seven types repeat, in the same order, in the sidebar card's type segment and on the dashboard slot cards.

### Status Bar

Bottom `Border` (`StatusBarBorder`), five columns:
1. **Status text**. `StatusText` binding (`StatusMessageText`), trimmed with `CharacterEllipsis`. A #175 decay sweep fades it out before clearing (code-behind `BeginAnimation`).
2. **Active-profile pill**. `ProfilePill` (`StatusProfilePill`, #175 item 8). Click opens the switcher flyout. An applied auto-switch flares it.
3. **Device count**. `ConnectedDeviceCount` + localized suffix, cold telemetry mono.
4. **Polling frequency**. `PollingFrequency` formatted `{0:F0}` + " Hz", cold telemetry mono.
5. **Engine indicator**. A flame `Path` (the shared `FlameOuterGeometry`) with DataTriggers on `Dashboard.EngineStateKey`: Running fills ember, Idle/Stopping fills gold (`WaitBrush`), else outline-only. `EngineStatusText` beside it turns `EmberHotBrush` when Running.

### Driver Overlay

Semi-transparent overlay during driver install/uninstall:
- `ProgressRing` spinner + text message (`DriverOverlayText`).
- Blocks all UI (`Grid.RowSpan="3"`, `Panel.ZIndex="1000"`).
- Shown/hidden by `RunDriverOperationAsync()`.

### Full-Window Overlays

Four more full-window layers sit over the content, each a `Grid` with `Grid.RowSpan="3"` and `Visibility="Collapsed"` until shown:

| Layer | ZIndex | Shown when | Contents |
|-------|--------|-----------|----------|
| `SteelLayer` | (bottom, hit-test off) | Dark theme always | Ember steel ground under all content |
| `FirstRunOverlay` | 900 | First-run marker file absent, or re-run from Settings | Welcome panel (`WelcomePanel`) + spotlight tour (`TourCanvas`: `TourHighlight` + `TourTip`) |
| `ShutdownOverlay` | 1001 | App is closing | `ProgressRing` + "Closing PadForge..." text (`Main_ShuttingDown`) |
| `StartupOverlay` | 1001 | Orphan-sweep task (`App.OrphanSweepTask`) still running at launch | `ProgressRing` + "Starting PadForge…" headline (`Main_StartingUp`) + "Cleaning up virtual controllers left from a previous session." detail (`Main_CleaningPreviousSession`), auto-hidden on completion |

### Composition Root (Code-Behind)

`MainWindow.xaml.cs` is the service wiring hub (~8500 lines). Constructor:

1. Creates `MainViewModel` as root and sets `DataContext`.
2. Sets child `DataContext` on Dashboard, Devices, Settings, Profiles pages.
3. Creates services: `SettingsService`, `InputService`, `RecorderService`, `DeviceService`.
4. Wires ViewModel events to services:
   - `StartEngineRequested`/`StopEngineRequested` to `InputService.Start()`/`Stop()`.
   - `SaveRequested`/`ReloadRequested`/`ResetRequested` to `SettingsService`.
   - Driver install/uninstall to `DriverInstaller` via `RunDriverOperationAsync`.
   - `TestRumbleRequested`/`TestLeftMotorRequested`/`TestRightMotorRequested` per pad.
   - Recording flow events per pad/mapping row.
   - Profile management (New, SaveAs, Edit, Load, Delete, RevertToDefault).
   - Device assignment via `DeviceService`.

### Timer Architecture

| Timer | Interval | Purpose |
|-------|----------|---------|
| `DispatcherTimer` | 33ms (~30Hz) | `InputService._uiTimer` fires `UiTimer_Tick` to push engine state into ViewModels |
| `_driverStatusTimer` | 5s | `RefreshHidHideStatus()`, `RefreshMidiServicesStatus()`, and `SweepStatusMessage()`. Started in the constructor and stopped only in `OnClosing`, so the status-bar decay keeps running after the engine stops. Hosting the decay on the engine 30 Hz timer would have burned in "Engine stopped." HIDMaestro is embedded so it has no install/uninstall poll |
| `CompositionTarget.Rendering` | ~60fps | Used by all visualization views (3D, 2D, Schematic, MIDI, KBM, MousePreview) for per-frame visual updates |

---

## DashboardPage

**Files:** `DashboardPage.xaml`, `DashboardPage.xaml.cs`

Engine toggle, slot summary cards, and the service sections.

Section order is pinned by `PadForge.Tests/PageOrderContractTests.cs`. `Dashboard_SectionsRunInTheDecidedOrder` asserts each section title's binding appears once and after the one before it, and that the Services header sits between the slot cards and the Web Controller card. `Dashboard_DriverStatusStripIsGone` asserts the page carries no `ED5D` glyph, no `Dashboard_Drivers` key in the XAML, in `Strings.Designer.cs`, or in any of the ten resx files, and no `HidHideStatusText` / `MidiServicesStatusText` / `SteamVrStatusText` in the page or `DashboardViewModel`. It also asserts the Settings page still binds all three. Those rows live there only.

### Layout Structure

```
ScrollViewer
  └─ StackPanel (Margin="24,16,24,16")
       ├─ Page header (icon + title)
       ├─ "Input Engine" section header (E9F5 glyph)
       ├─ CardBorder: Engine status card (EngineCard, Grid, 4 columns)
       │   ├─ Col 0: Engine toggle flame `Path` (FlameOuterGeometry, ember when Running, gold when Idle/Stopping, else outline)
       │   ├─ Col 1: EngineStatus text
       │   ├─ Col 2: PollingFrequencyText
       │   └─ Col 3: Online/Total devices count
       ├─ "Virtual Controllers" section header (E7FC glyph)
       ├─ ItemsControl (SlotsItemsControl, WrapPanel over a CompositeCollection:
       │   SlotSummaries plus the Add Controller tile in the same wrap flow)
       │   ├─ DataTemplate: slot card Border (252px wide, 5 rows)
       │   │   ├─ Row 0: Power flame btn + "Slot" + SlotNumber
       │   │   ├─ Row 1: Type segment (Xbox / PlayStation / Nintendo / Extended /
       │   │   │    KB+M / MIDI / VR) on a recessed track + "#N" instance label
       │   │   │    + Delete button
       │   │   ├─ Row 2: Device roster (per-device name + battery glyph, marquee
       │   │   │    on overflow) or the DeviceName empty-state line
       │   │   ├─ Row 3: StatusText + mapped/connected counts
       │   │   └─ Row 4: StageLedger chips (per-stage glyphs with hover readout)
       │   └─ Add Controller tile (AddControllerCard, 252px, dashed steel outline,
       │        MouseLeftButtonUp → AddControllerRequested, gated on ShowAddController)
       └─ ServicesSection StackPanel (one panel so the welcome tour can ring
            the whole group as a single target)
            ├─ "Services" divider (ServicesHeader, ember tick + hairline rule)
            ├─ "Web Controller" section (E774 glyph)
            │   └─ CardBorder: Enable toggle (EnableWebControllerCheckBox), port
            │      NumberBox + reset, status flame + WebControllerStatus, QR image +
            │      URL box + copy button (shown on HasWebControllerQr, #296), footer
            ├─ "Remote Link" section (E969 glyph, #138)
            │   └─ CardBorder: Enable toggle (EnableRemoteLinkCheckBox), auto-reconnect toggle,
            │      port NumberBox + reset, status flame + RemoteLinkStatus text,
            │      identity-protection mode ComboBox, Paired PCs list (rename / connect / revoke
            │      per peer, Revoke All), nearby-unpaired list, my-code readout,
            │      connect-by-address box, footer
            ├─ "Head Tracking" section (E77B glyph, #355)
            │   └─ CardBorder: Enable toggle (HeadTrackingEnabled), FreeTrack toggle
            │      (HeadTrackingFreeTrack), a three-row Grid of port / rotation range /
            │      translation range NumberBoxes each with a reset button,
            │      HeadTrackingStatus source line, footer
            ├─ "Motion Server" section (E7AD glyph, DSU)
            │   └─ CardBorder: Enable toggle, port NumberBox, status flame, footer
            ├─ "Lightbar Mirrors" section (E781 glyph)
            │   └─ CardBorder holding two divider-separated rows that forward the same
            │      virtual-pad lightbar color, each with its own strings and status line
            │      ├─ Razer Chroma (EnableChromaLightbar, ChromaStatus, #373)
            │      └─ Logitech LIGHTSYNC (EnableLightsyncLightbar, LightsyncStatus, #382)
            ├─ "Razer Sensa HD Haptics" section (E877 glyph, #374)
            │   └─ CardBorder: Enable toggle (EnableSensaHaptics), SensaStatus, footer
            ├─ "Overlays" section (E700 glyph)
            │   └─ CardBorder: Menu Overlay (EnableMenuOverlay), Shift Layer Flyout
            │      (EnableShiftLayerFlyout), Profile Overlay (EnableProfileOverlay) toggles
            └─ "Touchpad Overlay" section (EDA4 glyph)
                └─ CardBorder: Enable toggle (EnableTouchpadOverlay), opacity slider +
                   NumberBox + reset, reset-position button, status flame +
                   TouchpadOverlayStatus
```

### Key Bindings

| Binding | ViewModel | Description |
|---------|-----------|-------------|
| `EngineStateKey` | `DashboardViewModel` | Drives the engine flame `Path` fill: Running = ember, Idle / Stopping = gold (`WaitBrush`), else outline-only |
| `EngineStatus` | `DashboardViewModel` | Status text next to engine button |
| `PollingFrequencyText` | `DashboardViewModel` | e.g. "998 Hz" |
| `OnlineDevices` / `TotalDevices` | `DashboardViewModel` | Device count display |
| `SlotSummaries` | `DashboardViewModel` | `ObservableCollection<SlotSummary>` for slot cards |
| `ShowAddController` | `DashboardViewModel` | Controls Add Controller card visibility |
| `EnableDsuMotionServer` | `DashboardViewModel` | DSU enable checkbox |
| `DsuMotionServerPort` | `DashboardViewModel` | DSU port NumberBox |
| `DsuServerStatus` | `DashboardViewModel` | DSU status text |
| `EnableWebController` | `DashboardViewModel` | Web controller enable checkbox |
| `WebControllerPort` / `WebControllerStatus` | `DashboardViewModel` | Web controller port and status text |
| `HasWebControllerQr` / `WebControllerQr` / `WebControllerUrl` | `DashboardViewModel` | QR panel visibility, the QR bitmap, and the URL shown beside it (#296) |
| `EnableRemoteLink` / `RemoteLinkPort` / `RemoteLinkConnectHost` | `DashboardViewModel` | Remote Link enable, port, and connect-by-address host (#138) |
| `AutoReconnect` | `DashboardViewModel` | Remote Link auto-reconnect toggle |
| `IsRemoteLinkRunning` / `RemoteLinkStatus` | `DashboardViewModel` | Remote Link status flame and text |
| `RemoteLink` | `DashboardViewModel` | `DashboardViewModel.RemoteLink` is a second reference to the same `SettingsViewModel` instance, not a separate object. It carries the identity-protection modes and hint, the trusted peers, the nearby-unpaired list, and the revoke commands |
| `HeadTrackingEnabled` / `HeadTrackingFreeTrack` | `DashboardViewModel` | Head Tracking enable and FreeTrack toggles (#355) |
| `HeadTrackingUdpPort` / `HeadTrackingRotationRange` / `HeadTrackingTranslationRange` | `DashboardViewModel` | NumberBoxes ranged 1-65535, 1-180, and 1-500, each with a reset command |
| `HeadTrackingStatus` | `DashboardViewModel` | Which head-tracking source is live, or why neither is |
| `EnableChromaLightbar` / `ChromaStatus` | `DashboardViewModel` | Razer Chroma mirror row (#373) |
| `EnableLightsyncLightbar` / `LightsyncStatus` | `DashboardViewModel` | Logitech LIGHTSYNC mirror row (#382) |
| `EnableSensaHaptics` / `SensaStatus` | `DashboardViewModel` | Razer Sensa HD haptics translation (#374) |
| `EnableMenuOverlay` / `EnableShiftLayerFlyout` / `EnableProfileOverlay` | `DashboardViewModel` | Overlays-section toggles |
| `EnableTouchpadOverlay` / `TouchpadOverlayOpacity` / `TouchpadOverlayStatus` | `DashboardViewModel` | Touchpad overlay enable, opacity, and status text |

### Slot Card DataTemplate Bindings (SlotSummary)

| Binding | Type | Description |
|---------|------|-------------|
| `PadIndex` | `int` | Used as `Tag` for button click routing |
| `SlotNumber` | `int` | Global slot display number (1-based) |
| `IsEnabled` | `bool` | Controls power toggle color |
| `OutputType` | `VirtualControllerType` | Selects which type button is highlighted (Opacity 1.0 vs 0.3) |
| `TypeInstanceLabel` | `string` | Per-type instance number |
| `MappedDevices` | `ObservableCollection<PadViewModel.MappedDeviceInfo>` | Row 2 device roster (name + battery glyph, marquee on overflow) |
| `DeviceName` | `string` | Empty-state line, shown only when `MappedDevices.Count` is 0 |
| `StatusText` | `string` | e.g. "Forging", "Disabled", "Idle", "No mapping" |
| `MappedDeviceCount` / `ConnectedDeviceCount` | `int` | Mapped/connected counts |
| `HasMappedDevices` | `bool` | `MappedDeviceCount > 0`. Gates the ember flame and the card's warm rim |
| `IsVirtualControllerConnected` | `bool` | Live VC present. Drops the flame to gold when false |
| `IsSelected` | `bool` | Card whose pad page is in focus keeps the ember glow at rest |
| `IsCreateFailed` | `bool` | VC creation failed. Outranks the awaiting-devices tooltip |
| `IsInitializing` | `bool` | Triggers the ember flash animation (steady ember with reduced motion) |
| `StageLedger` | `ObservableCollection<SlotStageInfo>` | Row 4 stage chips (sticks / triggers / gyro / lighting / touchpad / audio) |

### Power Toggle State Machine

The slot power toggle is a flame `Path` (`FlameOuterGeometry`), not a glyph. It keys off `HasMappedDevices` and `IsVirtualControllerConnected`, not a raw device count. Enabled with no mapped devices stays the cold outline (heat needs fuel). There is no HIDMaestro-install state, since the driver is embedded.

| Condition | Flame fill | Tooltip |
|-----------|-----------|---------|
| `IsEnabled=False` | Cold outline (`TextFillColorTertiaryBrush`) | "Disabled" |
| `IsEnabled=True`, no mapped devices | Cold outline | "Forging" |
| `IsEnabled=True` + `HasMappedDevices=True` | `EmberBrush` + glow | "Forging" |
| above + `IsVirtualControllerConnected=False` | `WaitBrush` gold | "Awaiting devices" |
| above + `EngineStateKey="Stopped"` | `WaitBrush` gold | "Engine stopped" |
| `IsEnabled=True` + `IsCreateFailed=True` | (fill unchanged) | "Virtual controller failed" |
| `IsInitializing=True` | `EmberBrush` (flashing) | "Initializing" |

### Type Switch Buttons

7 type buttons per slot card (Xbox, PlayStation, Nintendo, Extended, KB+M, MIDI, VR) using a custom `TypeSwitchButton` style, seated on a recessed `SegTrackBrush` segment. Dark gray rounded background on hover, transparent border. Active type at Opacity 1.0, inactive at 0.3. Unavailable types (missing prerequisite, e.g. MIDI without Windows MIDI Services, VR without SteamVR) show `Cursor.No` and a tooltip explaining the requirement. Clicks are guarded in code-behind. The power button also uses the `TypeSwitchButton` style for visual consistency.

### UI Automation

| AutomationId | Element | Purpose |
|--------------|---------|---------|
| `EnableWebControllerCheckBox` | CheckBox | Web controller enable toggle |
| `EnableRemoteLinkCheckBox` | CheckBox | Remote Link enable toggle (#138) |

### Event Handlers (Code-Behind)

| Handler | Event | Action |
|---------|-------|--------|
| `EngineToggle_Click` | Button.Click | Raises `EngineToggleRequested` |
| `AddControllerCard_Click` | Border.MouseLeftButtonUp | Raises `AddControllerRequested` |
| `DeleteSlot_Click` | Button.Click | Raises `DeleteSlotRequested(slotIndex)` |
| `PowerToggle_Click` | Button.Click | Raises `SlotEnabledToggled(slotIndex, !IsEnabled)` |
| `XboxType_Click` | Button.Click | Raises `SlotTypeChangeRequested(slotIndex, Xbox)`. HIDMaestro is embedded so no install gate |
| `DS4Type_Click` | Button.Click | Raises `SlotTypeChangeRequested(slotIndex, PlayStation)` |
| `NintendoType_Click` | Button.Click | Raises `SlotTypeChangeRequested(slotIndex, Nintendo)` |
| `ExtendedType_Click` | Button.Click | Raises `SlotTypeChangeRequested(slotIndex, Extended)` |
| `KeyboardMouseType_Click` | Button.Click | Raises `SlotTypeChangeRequested(slotIndex, KeyboardMouse)` |
| `MidiType_Click` | Button.Click | Raises `SlotTypeChangeRequested(slotIndex, Midi)` |
| `VrType_Click` | Button.Click | Raises `SlotTypeChangeRequested(slotIndex, Vr)` (#49) |
| `SlotCard_Loaded` | Border.Loaded | Wires `PreviewMouseLeftButtonDown` for drag start |
| `OnCardMouseDown` | PreviewMouseLeftButtonDown | Records drag start position. Skips if inside a Button |
| `OnDragMove` | PreviewMouseMove | Begins/updates card drag with ghost adorner |
| `OnDragEnd` | PreviewMouseLeftButtonUp | Completes swap/insert or fires `SlotCardClicked` for navigation |
| `OnDragKeyDown` | PreviewKeyDown | Cancels drag on Escape |
| `OnDragCaptureLost` | LostMouseCapture | Cancels the drag when capture is taken away |

### Dashboard Card Drag Reordering

Drag to reorder (same adorner system as sidebar):
- `CardDragAdorner`. Ghost preview from `RenderTargetBitmap` snapshot. Adds 4 physical pixels to bitmap dimensions to prevent clipping at high DPI.
- `InsertionLineAdorner`. Accent-colored vertical line at insertion point.
- **Three zones per card**: left 25% = insert before, middle 50% = swap, right 25% = insert after.
- **Type-group validation**: cross-type drag blocked. Same-type only.
- **Sidebar rebuild suppression**: `RebuildControllerSection()` is suppressed while a card drag is in progress to avoid visual disruption.
- Events: `SlotSwapRequested(PadIndexA, PadIndexB)` and `SlotMoveRequested(SourcePadIndex, TargetVisualPos)`.

---

## PadPage

**Files:** `PadPage.xaml`, `PadPage.xaml.cs`

Per-slot configuration: two-tier tab strip, optional config bars, and 18 tab panels (Tags 0-17). Tier 1 (slot scope) holds Preview, Mappings, Macros, Menus, Bass Shakers, and Output. Tier 2 (device scope) holds the device selector and the capability tabs, most gated on source-device capability.

### Layout Structure

```
Grid (3 rows)
├─ Row 0 (Auto): Two-tier tab strip (StackPanel of two gradient-bordered Borders)
│   ├─ Tier 1 (slot scope, ember underline): scope label + identity chip + preset
│   │   chip on the left, slot tabs pushed right (TabStripButton, GroupName="PadTab")
│   │   ├─ RadioButton "Preview" (Tag=0, x:Name="TabController", AutomationId="TabController")
│   │   ├─ RadioButton "Mappings" (Tag=2, AutomationId="MappingsTab")
│   │   ├─ RadioButton "Macros" (Tag=1, AutomationId="MacrosTab")
│   │   ├─ RadioButton "Menus" (Tag=15, AutomationId="MenusTab", #9)
│   │   ├─ RadioButton "Bass Shakers" (Tag=16, AutomationId="BassShakersTab",
│   │   │    Visibility bound to RumbleAudioTabVisible, #236)
│   │   └─ RadioButton "Output" (Tag=17, AutomationId="OutputTab",
│   │        Visibility bound to OutputTabVisible, #270 follow-up)
│   └─ Tier 2 (device scope, cold underline): scope label + device ComboBox on the left,
│      capability tabs pushed right in a WrapPanel (TabStripButtonCold, GroupName="PadTabDevice")
│       ├─ ComboBox (MappedDevices, item = LivenessFlame Path + Name + battery)
│       ├─ RadioButton "Sticks" (Tag=3, x:Name="TabSticks")
│       ├─ RadioButton "Triggers" (Tag=4, x:Name="TabTriggers")
│       ├─ RadioButton "Force Feedback" (Tag=5, x:Name="TabForceFeedback", gated on hasForceFeedback)
│       ├─ RadioButton "Wheel" (Tag=11, x:Name="TabWheel", gated on wheel VID/PID)
│       ├─ RadioButton "Impulse Triggers" (Tag=9, x:Name="TabImpulseTriggers", gated on hasRumbleTriggers)
│       ├─ RadioButton "Adaptive Triggers" (Tag=6, x:Name="TabAdaptiveTriggers", gated on hasAdaptiveTriggers)
│       ├─ RadioButton "Lighting" (Tag=7, x:Name="TabLighting", gated on hasLightbar || hasGuideLed)
│       ├─ RadioButton "Gyro" (Tag=8, x:Name="TabGyro", gated on any motion sensor, #392)
│       ├─ RadioButton "Touchpad" (Tag=10, x:Name="TabTouchpad", gated on hasTouchpad)
│       ├─ RadioButton "Audio" (Tag=12, x:Name="TabAudio", gated on hasAudio)
│       ├─ RadioButton "Pointer" (Tag=13, x:Name="TabPointer", gated on hasIrPointer, #146)
│       └─ RadioButton "Mouse" (Tag=14, x:Name="TabMouse", gated on mouse device, #200)
├─ Row 1 (Auto): Extended config bar OR MIDI config bar (conditionally visible)
│   ├─ ExtendedConfigBar (Visibility=Collapsed unless OutputType==Extended)
│   └─ MidiConfigBar (Visibility=Collapsed unless OutputType==Midi)
├─ Invisible MappingsCountIndicator (for UI Automation)
└─ Row 2 (*): TabControl (hidden header via ControlTemplate), one TabItem per Tag (0-17),
   SelectedIndex bound to SelectedConfigTab
```

The `HMaestroProfileBar` preset chip sits inline in tier 1 rather than on its own row. The Extended and MIDI config bars are the only Row 1 occupants.

### Custom Styles (UserControl.Resources)

| Style Key | TargetType | Properties |
|-----------|------------|------------|
| `DzLabel` | `TextBlock` | Width=270, vertically centered, `TextFillColorSecondaryBrush`. Used for slider row labels. |
| `DzSlider` | `Slider` | Min=0, Max=100, Width=200, IsSnapToTickEnabled=True, TickFrequency=0.1. |
| `OffsetSlider` | `Slider` | Extends `DzSlider` with Min=-100 (for center offset). |
| `DzValueEdit` | `TextBox` | Width=56, right-aligned, editable percentage value. Neutral hover glow. |
| `DzDigitEdit` | `TextBox` | Width=56, right-aligned, tooltip "Raw axis value". Raw axis value edit. |
| `DzPercent` | `TextBlock` | "%" suffix text, `TextFillColorTertiaryBrush`. |
| `ResetButton` | `ui:Button` | Content glyph `E72C` (undo arrow), ContentTemplate FontSize=12, tooltip "Reset". Based on `EmberIconButton`. Per-row reset. |
| `ResetAllButton` | `ui:Button` | Padding=8,3, FontSize=11, left-aligned, based on `EmberIconButton`. Section-level reset. |
| `TabStripButton` | `RadioButton` | Slot-tier tab. `GroupName="PadTab"`. Checked = `#1AFF6B2C` ember-tint fill, `EmberHotBrush` SemiBold text, 2px ember underline. Hover carries `EmberHoverGlow`. |
| `TabStripButtonCold` | `RadioButton` | Device-tier tab. `GroupName="PadTabDevice"` (own radio group). Checked = `ColdTintBrush` fill, `ColdBrush` SemiBold text, 2px cold underline. Hover carries `ColdHoverGlow`. |

### Custom Tab Strip

Two `RadioButton` groups. The slot tier (Preview / Mappings / Macros / Menus / Bass Shakers / Output) uses `TabStripButton` with `GroupName="PadTab"`. The device tier (Sticks through Mouse) uses `TabStripButtonCold` with `GroupName="PadTabDevice"`. The two groups are independent so WPF never auto-unchecks across tiers. `SyncTabStripSelection()` keeps exactly one tab checked overall (#175 item 18: only the tier owning the active tab shows a highlight). Its slot-tier test is `selected <= 2 || selected == 15 || selected == 16 || selected == 17`, since Menus, Bass Shakers, and Output are appended TabItem indices rather than tier-2 tags. Each button stores its Tag (0-17) and sets `vm.SelectedConfigTab = Tag` on click via `TabBtn_Click`. `ConfigTabControl_PreviewKeyDown` swallows Ctrl+Tab and calls `CycleConfigTab`, which walks the visible RadioButtons of both groups because the header-less `TabControl` template breaks WPF's own Ctrl+Tab handling (discussion #140).

A `TabControl` with hidden header (custom `ControlTemplate` showing only `PART_SelectedContentHost`) provides content switching. `SelectedIndex` is bound to `SelectedConfigTab`.

### Tab Visibility Rules

Tabs hidden by output type and by source-device capability:

| Tab | Xbox / PlayStation / Extended | KB+Mouse | MIDI | Capability gate |
|-----|------------------------------------|----------|------|---|
| Preview | Visible | Visible | Visible | always |
| Macros | Visible | Visible | Visible | always |
| Mappings | Visible | Visible | Visible | always |
| Menus | Visible | Visible | Visible | always (slot scope, #9) |
| Sticks | Visible | Visible (Mouse X/Y + Scroll) | **Hidden** | always within Xbox/PS/Nintendo/Extended |
| Triggers | Visible | **Hidden** | **Hidden** | hidden on an Extended or Nintendo slot whose profile declares no analog triggers (`ExtendedConfig.TriggerCount == 0`, the Switch Pro's digital ZL/ZR), visible otherwise |
| Force Feedback | Visible if `hasForceFeedback` | **Hidden** | **Hidden** | selected device's CapType is stick-class (Gamepad / Joystick / Driving / Flight / FirstPerson). Hidden for keyboard / mouse / touchpad / MIDI even on an Xbox/PS/Extended slot |
| Impulse Triggers | Visible if `hasImpulseTriggers` | **Hidden** | **Hidden** | source device has impulse-trigger motors (Xbox One / One S / Elite / Elite Series 2 / Series X\|S, Microsoft VID). Xbox 360 and DualSense excluded |
| Adaptive Triggers | Visible if `hasAdaptiveTriggers` | **Hidden** | **Hidden** | source device is a DualSense or DualSense Edge |
| Lighting | Visible if `hasLightbar \|\| hasGuideLed` | **Hidden** | **Hidden** | a lightbar (DS4 / DualSense family, the PS Move sphere, or a web controller drawing a DS4 / DualSense) shows the lightbar cards. A Guide/HOME-button LED shows only the `GuideLedCard`: XInput/GIP Xbox pad over USB or the 2015 Steam Controller (#209), plus the Switch home-LED population (#226: Pro Controller, right Joy-Con, Joy-Con pair, charging grip) |
| Gyro | Visible if `hasGyro` | **Hidden** | **Hidden** | source device has any motion sensor (`ud.HasGyro \|\| ud.HasAccel`). On an accelerometer-only device the tab shows with its five gyro-rate cards collapsed (#392) |
| Pointer | Visible if `hasIrPointer` | **Hidden** | **Hidden** | source device is an IR-capable Wii Remote (#146) |
| Touchpad | Visible if `hasTouchpad` | **Hidden** | **Hidden** | source device has a touchpad (DualSense family, DS4, Steam Controller) |
| Wheel | Visible if `hasWheel \|\| hasGenericWheel` | **Hidden** | **Hidden** | source device is a force-feedback wheel |
| Audio | Visible if `hasAudio` | **Hidden** | **Hidden** | source has a speaker (DualSense / DS4 / Wii Remote) or plays HD haptic tones (Joy-Con, Switch Pro, Steam Controller / Deck, SC 2026) (#147) |
| Mouse | Visible if source is a mouse | **Hidden** | **Hidden** | source device is a mouse (per-device mouse-gesture settings, #200) |

VR slots (#49) hide both Sticks and Triggers: the `Vr` lane reads none of the stick or trigger tuning keys those tabs edit.

Tag numbers: Preview 0, Macros 1, Mappings 2, Sticks 3, Triggers 4, Force Feedback 5, Adaptive Triggers 6, Lighting 7, Gyro 8, Impulse Triggers 9, Touchpad 10, Wheel 11, Audio 12, Pointer 13, Mouse 14, Menus 15, Bass Shakers 16, Output 17. Bass Shakers (4.1.0, #236, AutomationId `BassShakersTab`) is slot-tier and gates on SLOT TYPE, not device capability: visible via `RumbleAudioTabVisible` for Xbox, PlayStation, and Nintendo slots plus Extended slots with a force-feedback surface. Output (#270 follow-up, AutomationId `OutputTab`) is slot-tier too and carries the SOCD and Keep Controller Awake cards. `OutputTabVisible` is false only for MIDI and VR slots, which have no output-behavior surface. The Audio tab was speaker-only before 3.6.0. It now shows for any haptic-tone pad as well. The Lighting tab used to be lightbar-only. It now also raises for a device with only a Guide/HOME-button LED (#209, and since #226 the Switch home-LED devices: Pro Controller, right Joy-Con, Joy-Con pair, charging grip): the lightbar cards (`LightbarModeCard`, `LightingLightbarSubtitle`, `LightingPlayerIdleHint`) collapse and the `GuideLedCard` brightness control takes their place.

If the selected tab is hidden, the view auto-switches to Preview (index 0). `SyncTabVisibility()` toggles the device-tier capability tabs from the selected device's capabilities, and also drives the motor activity bars (`MotorBarsGrid`).

### Slot Identity Chip

The Preview tab itself (Tag 0, `x:Name="TabController"`, header text `Pad_Tab_Preview`) is text-only. The type icon lives in the standalone, non-interactive identity chip at the left of tier 1, which stays ember regardless of which tab is checked. It picks its icon via DataTriggers on `OutputType`:

- `Xbox` → `XboxControllerIcon` (Image)
- `PlayStation` → `DS4ControllerIcon` (Image)
- `Nintendo` → `NintendoControllerIcon` (Image)
- `Extended` → `ExtendedControllerIcon` (Image)
- anything else → `GenericControllerIcon` (the Image default)
- `Midi` → `EC4F` glyph (TextBlock, Image collapsed)
- `KeyboardMouse` → `E961` glyph (keyboard, TextBlock, Image collapsed)

The DrawingImage resource keys (`XboxControllerIcon`, `DS4ControllerIcon`) keep the v2 short names. One icon represents the whole family regardless of which specific HM profile (Xbox 360 / Xbox One / Series / Elite / Adaptive, or DS4 / DualSense / DualSense Edge) the slot ends up running. Beside the icon, one `TextBlock` carries `OutputTypeDisplayName` plus a `TypeInstanceLabel` Run in telemetry mono, so the type name and the "#2" token share a baseline.

### Multi-Device Selector

Inline `ComboBox` bound to `MappedDevices` / `SelectedMappedDevice`. Each item shows a `LivenessFlame` `Path` (fills ember with a glow when `IsOnline`, outline-only stroke when offline), device `Name` in cold, and its battery percentage when the device reports one (#167). Sits in tier 2 (device scope) on the left, beside the "Device" scope label, ahead of the right-pushed capability tabs.

### UI Automation Properties

| AutomationId | Element | Purpose |
|--------------|---------|---------|
| `TabController` | RadioButton (tab 0) | Preview tab identification. x:Name kept from v2/v3, header text is now "Preview" |
| `MappingsTab` | RadioButton (tab 2) | Mappings tab identification |
| `HMaestroProfileCombo` | ComboBox | HIDMaestro profile selection for Xbox / PlayStation / Nintendo slots. Extended has its own `ExtendedProfileCombo` (no AutomationId) |
| `RawStickCountBox` | TextBox | Extended slot thumbstick count override |
| `ExtendedTriggerCountBox` | TextBox | Extended slot trigger count override |
| `RawPovCountBox` | TextBox | Extended slot POV count override |
| `RawButtonCountBox` | TextBox | Extended slot button count override |
| `MappingsCountIndicator` | TextBlock (invisible) | `AutomationProperties.Name` bound to `Mappings.Count` |
| `DeadZoneShapeCombo` | ComboBox | Deadzone shape selector (Sticks tab) |
| `SensitivityXCombo` | ComboBox | Sensitivity X preset (Sticks tab) |
| `TriggerPresetCombo` | ComboBox | Trigger sensitivity preset (Triggers tab) |
| `ControllerModelHost` | Grid | Preview tab visualization host |
| `ViewModeToggle` | Button | 2D/3D preview toggle |
| `MacroAddButton` / `MacroRemoveButton` | ui:Button | Macro list add and remove |
| `MenuAddButton` / `MenuRemoveButton` | ui:Button | Menu list add and remove (#9) |
| `MacrosTab` / `MenusTab` / `BassShakersTab` / `OutputTab` | RadioButton | The remaining slot-tier tabs |
| `AssignOfferBanner` | Border | The assign-offer banner raised when a newly seen device matches the slot |
| `AssignOfferAccept` / `AssignOfferDismiss` | ui:Button | Its two answers |

### Event Handlers (Code-Behind)

| Handler | Trigger | Action |
|---------|---------|--------|
| `PadPage_Loaded` | UserControl.Loaded | Calls `ApplyViewMode`, `SyncTabStripSelection`, `SyncExtendedConfigBar`, `SyncMidiConfigBar` |
| `OnDataContextChanged` | DataContextChanged | Unsubscribes old VM, subscribes new VM PropertyChanged, resyncs all |
| `ViewModeToggle_Click` | Button.Click | Toggles `SettingsViewModel.Use2DControllerView`, calls `ApplyViewMode` |
| `TabBtn_Click` | RadioButton.Click | Sets `vm.SelectedConfigTab` from `Tag` |
| `Motor_MouseEnter/Leave` | StackPanel.Mouse | Hover opacity effect (0.7/1.0) |
| `LeftMotor_Click` | StackPanel.MouseLeftButtonDown | `padVm.FireTestLeftMotor()` |
| `RightMotor_Click` | StackPanel.MouseLeftButtonDown | `padVm.FireTestRightMotor()` |
| `MapAllToggle_Click` | Button.Click | Starts Map All, or stops it when already active (button text is `MapAllButtonText`) |
| `CalibrateCenter_Click` | Button.Click | `StickConfigItem.StartCalibration()` |
| `ProfileCombo_PreviewKeyDown` | ComboBox.PreviewKeyDown | Forwards Enter/Esc on `HMaestroProfileCombo` and `ExtendedProfileCombo` to commit / dismiss |
| `ExtendedCustomValue_Changed` | TextBox.LostFocus | Applies clamped Extended layout overrides (sticks/triggers/POVs/buttons) |
| `ExtendedCustomValue_KeyDown` | TextBox.KeyDown(Enter) | Same as LostFocus apply |
| `MidiConfig_Changed` | TextBox.LostFocus | Applies clamped MIDI config, rebuilds mappings if counts change |
| `MidiConfig_KeyDown` | TextBox.KeyDown(Enter) | Same as LostFocus apply |
| `StickPresetX_SelectionChanged` | ComboBox.SelectionChanged | Sets `StickConfigItem.SensitivityCurveX` from preset |
| `StickPresetY_SelectionChanged` | ComboBox.SelectionChanged | Sets `StickConfigItem.SensitivityCurveY` from preset |
| `TriggerPreset_SelectionChanged` | ComboBox.SelectionChanged | Sets `TriggerConfigItem.SensitivityCurve` from preset |
| `AppVolumeProcessDropDown_Opened` | ComboBox.DropDownOpened | `action.RefreshAudioProcessesCommand.Execute()` |
| `DeviceAxisPicker_DropDownOpened` | ComboBox.DropDownOpened | Populates ComboBox with devices assigned to current slot |
| `DeviceAxisIndexPicker_DropDownOpened` | ComboBox.DropDownOpened | Populates ComboBox with axis-type DeviceObjects from selected device |
| `OnPadVmPropertyChanged` | PadViewModel.PropertyChanged | Syncs tab strip on `SelectedConfigTab`, resyncs config bars on `OutputType` |

### Preview Tab (Tab 0). Detailed

```
Grid (3 rows)
├─ Row 0 (*): Controller visualization area
│   ├─ ControllerModelView (3D, HelixToolkit)
│   ├─ ControllerModel2DView (2D overlays, Collapsed by default)
│   ├─ ControllerSchematicView (procedural Extended/HID layout, Collapsed)
│   ├─ MidiPreviewView (MIDI, Collapsed)
│   ├─ KBMPreviewView (KB+Mouse, Collapsed)
│   ├─ VRPreviewView (VR hand pair, Collapsed, #49)
│   └─ ViewModeToggle button (top-left, E8B9↔F158 icon)
├─ Row 1 (Auto): Motor activity bars (MotorBarsGrid, 400px wide, centered)
│   ├─ Col 0: Left Motor ProgressBar (MotorCapsuleTemplate) + label, clickable
│   └─ Col 1: Right Motor ProgressBar + label, clickable
└─ Row 2 (Auto): Map All controls
    ├─ Map All / Stop toggle Button (MapAllPillButton, Content=MapAllButtonText, Click=MapAllToggle_Click). Text flips to "Stop" when IsMapAllActive
    └─ MapAllPromptText (EmberHotBrush, SemiBold, collapsed when null)
```

**View Switching Logic (`ApplyViewMode`):**

| Output Type | HIDMaestro Profile | User Pref | Active View | Toggle Visible |
|-------------|--------------------|-----------|-------------|----------------|
| KeyboardMouse |. |. | KBMPreviewView | No |
| Midi |. |. | MidiPreviewView | No |
| Vr |. |. | VRPreviewView | No |
| Extended | any |. | ControllerSchematicView | No |
| Xbox |. | 2D | ControllerModel2DView | Yes |
| Xbox |. | 3D | ControllerModelView | Yes |
| PlayStation |. | 2D | ControllerModel2DView | Yes |
| PlayStation |. | 3D | ControllerModelView | Yes |
| Nintendo |. | 2D | ControllerModel2DView | Yes |
| Nintendo |. | 3D | ControllerModelView | Yes |

**`BindActiveModelView()`**: Unbinds all six views, subscribes the active view's `ControllerElementRecordRequested` event, then calls `Bind(vm)`. All views fire `ControllerElementRecordRequested` with a PadSetting target name for click-to-record. The 2D view additionally wires `AnnotationChipNavigateRequested` and `AnnotationsToggled`.

**Motor Activity Bars**. Two `ProgressBar` capsules (`MotorBarsGrid`, `MotorCapsuleTemplate`, `Minimum=0`/`Maximum=1`) bound to `LeftMotorDisplay`/`RightMotorDisplay`. The template fills an ember gradient with a leading-edge glow that grows from zero width at 0%. Each capsule is wrapped in a clickable `Grid` for motor test. Hover dims to 0.7 opacity via `Motor_MouseEnter`/`Motor_MouseLeave`.

### Macros Tab (Tab 1). Detailed

```
Grid (3 columns)
├─ Col 0 (250px): Macro list panel
│   ├─ DockPanel.Top: Add/Remove buttons
│   └─ ListBox (Macros, DisplayMemberPath="Name")
├─ Col 1 (Auto): GridSplitter (4px, draggable)
└─ Col 2 (*): Macro editor (ScrollViewer)
    └─ StackPanel (DataContext=SelectedMacro)
        ├─ Name TextBox (UpdateSourceTrigger=PropertyChanged)
        ├─ Enabled CheckBox
        ├─ Fire mode ComboBox, 12 items in strip order: OnPress, SinglePress,
        │   OnRelease, WhileHeld, HoldForMs, ShortPress, DoublePress, TriplePress,
        │   Toggle, Turbo, Always, CustomExpression
        ├─ Trigger Combination panel (hidden when Always mode)
        │   ├─ Trigger Source ComboBox (InputDevice/OutputController)
        │   ├─ Trigger display/recording text + Record button
        │   ├─ Recording hint text
        │   ├─ Axis threshold slider (1-100%, visible when UsesAxisTrigger)
        │   ├─ Axis direction ComboBox (Any/Positive/Negative, visible when UsesAxisTrigger)
        │   └─ Consume trigger buttons CheckBox
        ├─ Always mode description note
        ├─ Custom Expression formula editor (CustomExpression mode): a-z variable chips (gated on VariableCount) plus operator / comparison / logic / function chips
        ├─ Separator
        └─ Action Sequence section
            ├─ Add Action / Remove buttons
            ├─ Actions ListBox (DisplayMemberPath="DisplayText")
            └─ Action editor Border (DataContext=SelectedAction)
                ├─ Action Type ComboBox (grouped, `MacroTypeCatalog.View`)
                └─ Type-specific panels (conditional visibility):
```

**Grouped Action Type Picker.** The picker binds `ItemsSource="{Binding Source={x:Static vm:MacroTypeCatalog.View}}"` with `SelectedValuePath="Type"` and `DisplayMemberPath="Label"`. `MacroTypeCatalog` (`PadForge.App/ViewModels/MacroTypeCatalog.cs`) carries all 56 `MacroActionType` values exactly once, in display order, across eleven category shelves: Virtual Buttons, Virtual Axes & Wheel, Keyboard & Text, Mouse, Timing & Flow, Rumble, Lightbar & LEDs, Sound & Volume, Motion & Pointer, Layers & Overlays, System & Apps. `MacroTypeCatalog.View` is a `ListCollectionView` grouped on `Category`, and the ComboBox draws each shelf through a `GroupStyle.HeaderTemplate`, the arrangement the cross-device input picker uses. Item tooltips ride the `ItemContainerStyle`. The list is one instance for the process lifetime, refilled in place on `Strings.CultureChanged` so an `x:Static`-bound view never strands on a stale list. `PadForge.Tests/MacroTypeCatalogTests.cs` pins the census: every enum member appears exactly once, `Choices.Count` equals `Enum.GetValues<MacroActionType>().Length`, the categories stay eleven contiguous blocks, and the picker still binds `MacroTypeCatalog.View`.

**Macro Trigger Section:**

| Field | Binding | Visibility |
|-------|---------|------------|
| Fire mode dropdown | `TriggerMode` (SelectedValue, `SelectedValuePath="Tag"`) | Always |
| Trigger source | `TriggerSource` | Hidden in Always mode (`IsNotAlwaysMode`) |
| Trigger display | `TriggerDisplayText` / `RecordingLiveText` | Hidden in Always mode |
| Record button | `RecordTriggerCommand` / `RecordTriggerButtonText` | Hidden in Always mode |
| Axis threshold | `TriggerAxisThreshold` (Slider 1-100%) | `UsesAxisTrigger` |
| Axis direction | `TriggerAxisDirectionIndex` (Any/Positive/Negative) | `UsesAxisTrigger` |
| Consume trigger | `ConsumeTriggerButtons` (CheckBox) | Hidden in Always mode |

**Action Type Editor Panels.** One `Visibility` branch per shape, each bound to an `Is*Type` predicate on `MacroAction`. Some branches cover a family (`IsAnyRumbleSetType`, `IsAnyAxisValueType`, `IsAnyMouseButtonType`). The ones below are the shapes worth naming. Grep `Is[A-Za-z]*Type` in `PadPage.xaml` for the full set.

| Action Type | Visible Panel | Key Controls |
|-------------|---------------|-------------|
| `ButtonPress` / `ButtonRelease` | `IsButtonType` | WrapPanel of CheckBox items from `ButtonOptions` |
| `KeyPress` / `KeyRelease` | `IsKeyType` | `KeyString` TextBox (Consolas font), VirtualKey ComboBox picker, Clear button |
| `ButtonPress` / `KeyPress` / `Delay` | `IsDurationType` | `DurationMs` TextBox + "ms" label |
| `AxisSet` | `IsAxisType` | Axis target ComboBox (LStickX/Y, RStickX/Y, LT, RT) + `AxisValue` TextBox |
| `SystemVolume` | `IsSystemVolumeType` | Axis source (Output/Input), axis selector, device picker, volume limit slider, invert toggle, OSD toggle |
| `AppVolume` | `IsAppVolumeType` | Process ComboBox (editable, refreshes on dropdown), axis source, device picker, volume limit, invert toggle |
| `MouseMove` / `MouseScroll` | `IsMouseMoveType` | Axis source (Output/Input), axis selector, device picker, sensitivity slider |
| `MouseButtonPress` / `MouseButtonRelease` | `IsMouseButtonType` | Mouse button ComboBox (Left/Right/Middle/X1/X2) |
| `DisconnectController` | `IsDisconnectControllerType` | Target-mode ComboBox (`DisconnectTarget`: Triggering Device / Specific Device / Slot Devices / All Devices) + specific-device picker ComboBox (`DisconnectDeviceOptions`, gated on `IsDisconnectSpecificDevice`) |
| `SwitchLayer` | `IsSwitchLayerType` | A `CardBorder` with `MacroAction_Type_SwitchLayer` as its title, the `Macro_SwitchLayer_Hint` line, and a 240px ComboBox over the slot's own `LayerTabs` (`SelectedValuePath="LayerMask"`, `DisplayMemberPath="LayerName"`) writing `SwitchLayerMask`. Choices are Base plus every authored layer, the same name/mask pairs the layer-scope picker uses (#377) |

**Device Axis Picker (shared by SystemVolume, AppVolume, MouseMove):**
- Device ComboBox: `DropDownOpened` populates from devices assigned to current slot.
- Axis index ComboBox: `DropDownOpened` populates with `IsAxis` DeviceObjects from selected device.
- Uses `AxisPickerItem` wrapper with `InputIndex` and localized `DisplayName`.

### Mappings Tab (Tab 2). Detailed

```
Grid (4 rows, x:Name="MappingDataGrid" at Row 3)
├─ Row 0 (Auto): Toolbar
│   ├─ "Copy" Button (CopySettingsCommand)
│   ├─ "Paste" Button (PasteSettingsCommand)
│   ├─ "Copy From" Button (CopyFromCommand)
│   ├─ "Map All" Button (MapAllButtonText, Click=MapAllToggle_Click)
│   ├─ "Add Layer" Button (AddShiftLayerButton, Click=AddShiftLayer_Click)
│   ├─ MappingFilterSearchBox (ui:TextBox, MappingInputSearch, find-as-you-type)
│   ├─ MappingDeviceFilterToggle (Filter24 funnel) + Popup (PickerDeviceFilterEntries checkboxes)
│   ├─ Hint text (italic, secondary brush)
│   └─ "Clear All" Button (far end, EmberDestructiveButton, Click=ClearAllMappings_Click → ConfirmDialog)
├─ Row 1 (Auto): ShiftLayerTabStrip (nested layer tabs bound to LayerTabs, hidden when only Base)
├─ Row 2 (Auto): Pipeline-status chips (SHIFT / INV / DZ, click-to-highlight)
└─ Row 3 (*): DataGrid (HorizontalAlignment=Left, every column Width="Auto")
    ├─ Column: "Output" (TargetLabel text)
    ├─ Column: "Source" (grouped ComboBox dropdown)
    ├─ Column: "Value" (CurrentValueText, mono)
    ├─ Column: Record button (ToggleRecordCommand)
    ├─ Column: Clear button (ClearCommand)
    ├─ Column: "Options" (Invert + Half checkboxes)
    └─ Column: "Deadzone" (per-mapping activation threshold, #42)
```

**DataGrid Properties:**
- `AutoGenerateColumns="False"`, `CanUserAddRows="False"`, `CanUserDeleteRows="False"`, `CanUserReorderColumns="False"`, `IsReadOnly="True"`.
- Row style: transparent background, retemplated with a #175 "rowfire" ember underline drawn at the cells' bottom edge. A plain row with no options collapses to a 26px mono compact line and expands to the full editor on click or selection.

**Source Column ComboBox:**
- `ItemsSource="{Binding AvailableInputsView}"`. Grouped `ICollectionView` over the row's `AvailableInputs` (per-device groups via `ComboBox.GroupStyle`).
- `SelectedItem="{Binding SelectedInput, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged}"`.
- `DisplayMemberPath="DisplayName"`.

**Options Column:**
- `Invert` CheckBox. `IsInverted` binding.
- `Half` CheckBox. `IsHalfAxis` binding.

**Picker Filter (#322):**
One search box and one device-visibility popup filter the slot's shared choice view, so every picker on the tab reflects them when opened. Ctrl+F focuses the box through `MappingsTabRoot_PreviewKeyDown` on the tab root.

- `MappingInputSearch` is find-as-you-type and session-only, never persisted. Its setter calls `ApplyMappingPickerFilter()`.
- The search also **filters the grid rows** as well as the dropdown contents: `RowMatchesSearch` matches a row's target label or its selected source's display name. Rows are outputs, so the device-visibility set never hides them. Only typed text does.
- `PickerDeviceFilterEntries` drives the popup's per-device checkboxes. `HiddenPickerDeviceKeys` (device guids plus `"any"` for the device-agnostic group) persists per slot in the settings root, not in profiles.
- `MappingPickerFilterActive` is true while either filter narrows the list, so the funnel reads as engaged.

A view filter changes what a dropdown OFFERS, never what a row's binding holds.

### Sticks Tab (Tab 3). Detailed

```
ScrollViewer
  └─ ItemsControl (ItemsSource=StickConfigs, DataType=StickConfigItem)
      └─ per-stick StackPanel:
          ├─ Title + "Reset All" button
          └─ Grid (2 columns)
              ├─ Col 0 (*): Slider controls
              │   ├─ "Calibrate Center" button (click → StartCalibration)
              │   ├─ Center Offset X (OffsetSlider, -100 to 100, + digit edit + reset)
              │   ├─ Center Offset Y (OffsetSlider + digit edit + reset)
              │   ├─ Deadzone Shape ComboBox (6 shapes)
              │   ├─ Deadzone X (DzSlider + % edit + digit edit + reset)
              │   ├─ Deadzone Y (DzSlider + % edit + digit edit + reset)
              │   ├─ Anti-Deadzone X (DzSlider + % edit + digit edit + reset)
              │   ├─ Anti-Deadzone Y (DzSlider + % edit + digit edit + reset)
              │   ├─ Linear (DzSlider + % edit + reset)
              │   ├─ "Sensitivity Curves" header + hint text
              │   ├─ Sensitivity X (preset ComboBox + reset)
              │   ├─ Sensitivity Y (preset ComboBox + reset)
              │   ├─ Min Range X/Left (1-100, DzSlider + % edit + digit edit + reset)
              │   ├─ Max Range X/Right (1-100, DzSlider + % edit + digit edit + reset)
              │   ├─ Min Range Y/Down (1-100, DzSlider + % edit + digit edit + reset)
              │   └─ Max Range Y/Up (1-100, DzSlider + % edit + digit edit + reset)
              └─ Col 1 (Auto): Live preview panel (MinWidth=216)
                  ├─ Stick position preview (212×212 Border)
                  │   ├─ 200×200 Ellipse background
                  │   ├─ Grid lines (crosshair + quadrant dashes)
                  │   ├─ Deadzone overlays (shape-dependent):
                  │   │   ├─ Axial: yellow cross arms + red center rectangle
                  │   │   ├─ Radial/ScaledRadial: red ellipse
                  │   │   ├─ Sloped/SlopedScaled: yellow wedges (SlopedWedgeGeometryConverter)
                  │   │   └─ Hybrid: yellow wedges + red circle center
                  │   ├─ Anti-deadzone ring (thin ember `#80FF6B2C` ellipse at the
                  │   │  output-floor radius, collapsed while both axes sit at 0)
                  │   └─ Cold-blue stick position dot (9px, `#FF58B6E4`, NormToCanvasConverter)
                  ├─ RawDisplay text (centered, wrapping)
                  └─ CurveEditor pair (X-axis + Y-axis, 96px each)
                      ├─ CurveEditor X: CurveString=SensitivityCurveX, DeadZone/MaxRange bindings
                      └─ CurveEditor Y: CurveString=SensitivityCurveY, DeadZone/MaxRange bindings
```

**Deadzone Shape Options (ComboBox index):**

| Index | Shape | Deadzone Overlay |
|-------|-------|-------------------|
| 0 | Scaled Radial | Red ellipse (`IsRadialShape`) |
| 1 | Radial | Red ellipse (`IsRadialShape`) |
| 2 | Axial | Yellow cross arms + red center rectangle (`IsAxialShape`) |
| 3 | Hybrid | Yellow wedges + red circle (`IsHybridShape`) |
| 4 | Sloped Scaled Axial | Yellow wedges (`HasSlopedWedges`) |
| 5 | Sloped Axial | Yellow wedges (`HasSlopedWedges`) |

**Per-Slider Row Pattern:**
Each parameter row follows this layout:
```
[DzLabel 270px] [Slider 200px] [TextBox 56px] [%] [DigitEdit 56px] [ResetButton]
```
Slider and TextBox both bind to the same property (e.g., `DeadZoneX`) with `Mode=TwoWay`. Digit edit binds to a separate `*Digit` property for raw axis values. Reset buttons use per-property commands (e.g., `ResetDeadZoneXCommand`).

**Independent Axis Range Sliders:**
- `MaxRangeXNeg` / `MaxRangeX`. Left/Right boundaries for X axis (1-100%).
- `MaxRangeY` / `MaxRangeYNeg`. Down/Up boundaries for Y axis (1-100%).

### Triggers Tab (Tab 4). Detailed

```
ScrollViewer
  └─ ItemsControl (ItemsSource=TriggerConfigs, DataType=TriggerConfigItem)
      └─ per-trigger StackPanel:
          ├─ Title + "Reset All" button
          └─ Grid (single column) holding one StackPanel
              ├─ Range: RangeSlider (dual-thumb, DeadZone/MaxRange 0-100%)
              │   + two TextBox edits (dz.max) + two digit edits + reset
              ├─ Anti-Deadzone (DzSlider 0-100% + % edit + digit edit + reset)
              ├─ Separator
              ├─ "Sensitivity Curve" header + hint text
              ├─ Preset ComboBox (120px, `CurvePresetChoices`, the instance accessor
              │   over the static `CurvePresetNames`) + reset
              ├─ CurveEditor (full width, IsFullWidth=True, ChartHeight=150, IsSigned=False)
              │   └─ CurveString=SensitivityCurve, DeadZone/MaxRange/LiveInput bindings
              └─ Live instrument panel (inset Border, Grid)
                  ├─ RAW bar (ProgressBar 0-1, RawNorm, InstrumentBarRaw) + RawDisplay text
                  ├─ OUT bar (ProgressBar 0-1, LiveValue, InstrumentBarOut) + OutDisplay text
                  └─ TriggerTravelArc (RawValue=RawNorm, OutValue=LiveValue, spans both rows)
```

**RangeSlider**. Dual-thumb control for deadzone floor and max range ceiling:
- `LowerValue="{Binding DeadZone}"`. Deadzone threshold.
- `UpperValue="{Binding MaxRange}"`. Max range ceiling.
- The range between thumbs represents the active trigger zone.

### Force Feedback Tab (Tab 5). Detailed

```
ScrollViewer
  └─ StackPanel
      ├─ "Force Feedback / Rumble" header + "Reset All" button
      ├─ Overall Gain slider (0-100%, ForceOverallGain)
      ├─ Left Motor Strength slider (0-100%, LeftMotorStrength)
      ├─ Right Motor Strength slider (0-100%, RightMotorStrength)
      ├─ "Fold Trigger Rumble into Main Motors" CheckBox (FfbTriggerFoldChk, TriggerRumbleFold)
      ├─ "Swap Left and Right Motors" CheckBox (SwapMotors)
      ├─ "Test Rumble" Button (TestRumbleCommand)
      ├─ "Motor Activity" header
      ├─ Left Motor live bar (ProgressBar 0-1, LeftMotorDisplay)
      ├─ Right Motor live bar (ProgressBar 0-1, RightMotorDisplay)
      ├─ "Constant Force" card (F0AD icon + "Reset All" ResetConstantForceCommand + description)
      │   ├─ "Apply Constant Force" CheckBox (ConstantForceEnabled)
      │   ├─ Drag pad (ConstantForcePadBorder, mouse handlers, SignedNormToCanvasConverter)
      │   └─ X / Y sliders + F2 edits + per-axis reset (ConstantForceX / ConstantForceY)
      ├─ Audio Bass Rumble section
      │   ├─ "Audio Rumble" header + "Reset All" button + description
      │   ├─ Enable CheckBox (AudioRumbleEnabled)
      │   ├─ Sensitivity slider (1-20, AudioRumbleSensitivity, format F1)
      │   ├─ Bass Cutoff slider (20-200 Hz, AudioRumbleCutoffHz, format F0)
      │   ├─ Left Motor slider (0-100%, AudioRumbleLeftMotor)
      │   ├─ Right Motor slider (0-100%, AudioRumbleRightMotor)
      │   └─ Level meter (ProgressBar 0-1, AudioRumbleLevelMeter)
      └─ "Trigger Routing" card (E72A icon + "Reset All" ResetTriggerRouteCardCommand + description)
          ├─ Left: source ComboBox, mode ComboBox, scale slider, activator display +
          │   record button (LeftTriggerRouteActivatorRecordCommand, EmberIconButtonHot)
          │   and activator-mode ComboBox, each with its own reset
          └─ Right: the same five rows on the RightTriggerRoute* bindings
```

All Audio Rumble controls bind `IsEnabled="{Binding AudioRumbleEnabled}"`. Grayed out when off.

### Gyro Tab (Tab 8). Detailed

The tab opens on the E7AD page header (`Pad_Gyro_Header` + `Pad_Gyro_Subtitle`), then nine `CardBorder` cards in this order:

| Order | Card | x:Name | Glyph | Shown when |
|-------|------|--------|-------|-----------|
| 1 | Grip (#392) | (unnamed) | `E815` | always |
| 2 | Motion Passthrough | `GyroPassthroughCard` | `E72A` | gyro rate |
| 3 | Motion Steering (#94) | (unnamed) | inline `Path` | always |
| 4 | Tilt | (unnamed) | `E99A` | always |
| 5 | Calibration | `GyroCalibrationCard` | `F272` | gyro rate |
| 6 | Sensitivity | `GyroSensitivityCard` | `E9E9` | gyro rate |
| 7 | Compass Yaw (#271) | `CompassYawCard` | `E707` | Switch 2 magnetometer |
| 8 | Response | `GyroResponseCard` | `F1CB` | gyro rate |
| 9 | Engage (#120) | `GyroEngageCard` | `E7E8` | gyro rate |

The tab raises for any motion sensor, so an accelerometer-only remote reaches Grip, Tilt, and Motion Steering. `SyncTabVisibility()` keeps two flags apart for that: `hasGyro` is `ud.HasGyro || ud.HasAccel` and drives `TabGyro.Visibility`, while `hasGyroRate` is `ud.HasGyro` alone and collapses the five rate cards named above. Before #392 the tab itself was gyro-gated, so an accelerometer-only Wii Remote never saw Tilt.

**Grip card.** One row: a `MotionGripOptions` ComboBox on `MotionGrip` (`SelectedValuePath="Value"`, `DisplayMemberPath="Display"`, 260px) plus `ResetMotionGripCommand`. The four holds are `Pointing` (the default), `Sideways`, `WiiWheel`, and `Upright`, stored as those canonical English identifiers. The grip rotates gyro, accelerometer, and gravity into the game's frame, and the D-pad follows it.

**Engage card (#120).** Below the Easy-Aim stick threshold, two ComboBoxes gate gyro engagement per stick and per direction. Both use `SelectedValuePath="Tag"` and reset buttons.

| Control | Binding | Items (Tag) |
|---------|---------|-------------|
| Engage Stick | `GyroEngageStickSide` | Right / Left / Either |
| Engage Direction | `GyroEngageStickDirection` | Full / X / Y / XNeg / XPos / YNeg / YPos |

Reset buttons run `ResetGyroEngageStickSideCommand` (to Right) and `ResetGyroEngageStickDirectionCommand` (to Full).

### Mappings Tab. Per-Source Motion Sensitivity

Two per-source sensitivity rows render inside the mapping source editor, each gated on the selected source:

- IR Pointer X/Y (#146): visible on `IsIrPointerSource`. Slider + TextBox bound to `IrPointerSensitivity`, reset via `ResetIrPointerSensitivityCommand`.
- Mouse Motion X/Y (#154): visible on `IsMouseMotionSource`. Same `IrPointerSensitivity` binding with its own tooltip string.

### Pointer Tab (Tab 13). IR Camera Tuning (#146)

Wii Remote IR camera tuning. `TabPointer` (Tag 13) is `Visibility="Collapsed"` by default and shown by `SyncTabVisibility()` only when the selected mapped device is an IR-capable Wii Remote (`hasIrPointer`). Hosts the IR sensor-bar position and related pointer tunables.

### Menus Tab (Tab 15). Detailed

Radial / touch menu editor (#9). Slot tier like Macros: menus live on the slot's `MappingSet`. Tag 15 is the appended TabItem's index.

```
Grid (3 columns)
├─ Col 0 (250px): Menu list panel
│   ├─ WrapPanel.Top: Add / Remove / Duplicate buttons
│   │   (AutomationIds "MenuAddButton" / "MenuRemoveButton")
│   └─ ListBox (Menus, SelectedItem=SelectedMenu, DisplayMemberPath="Name",
│      EmberSelectListItem container style)
├─ Col 1 (Auto): GridSplitter (4px, draggable)
└─ Col 2 (*): Empty state OR menu editor
    ├─ Empty state (visible while !HasSelectedMenu): outline flame Path
    │   + Menu_EmptyHint cold guidance text, same shape as Macros
    └─ ScrollViewer (DataContext=SelectedMenu, gated on HasSelectedMenu)
        └─ StackPanel
            ├─ Menu Name TextBox (UpdateSourceTrigger=PropertyChanged) + Enabled CheckBox
            ├─ Style ComboBox (KindOptions → KindIndex: Radial Ring / Touch Grid)
            ├─ Host Input ComboBox (HostOptions → SelectedHost)
            │   + Record button (MenuHostRecordCommand from the TabItem DataContext,
            │     glyph = HostRecordIcon) + Reset (ResetHostCommand)
            ├─ Host Input caption (Menu_HostInput_Caption, always shown)
            ├─ Custom X / Custom Y steer-axis rows (visible on IsCustomHost,
            │   ResetCustomXCommand / ResetCustomYCommand)
            ├─ Click Input row (visible on IsCustomHost, ResetClickCommand)
            ├─ Pad Half ComboBox (HostHalfOptions → HostHalfIndex,
            │   visible on HostIsTouchpad)
            ├─ Fire Mode ComboBox (FireOptions → FireTypeIndex) + Reset
            ├─ Cells NumberBox (1-20 → CellCount)
            │   + Center Cell CheckBox (HasCenter, radial only) + Reset
            ├─ Engage Deadzone Slider + NumberBox (1-95 → EngageDeadzonePercent) + Reset
            ├─ Menu Overlay geometry card (CardBorder, header + ResetGeometryCommand)
            │   ├─ Show Labels CheckBox (ShowLabels)
            │   ├─ Screen Position NumberBox pair (0-100 → PosXPercent / PosYPercent)
            │   ├─ Size NumberBox (10-400 → ScalePercent) + "%"
            │   └─ Opacity NumberBox (5-100 → OpacityPercent) + "%"
            ├─ Cell Bindings ItemsControl (Cells)
            │   └─ per cell: Header + icon indicator (IconImage, or the E8B9
            │       picture glyph on ShowIconGlyph) + Label TextBox (LostFocus)
            │       + Binding ComboBox (BindingKindOptions → BindingKind)
            │       + key picker (KeyOptions → SelectedKeyVk, visible on ShowKeyPicker)
            │       OR button picker (ButtonOptions → SelectedButtonFlag,
            │          visible on ShowButtonPicker)
            │       OR macro picker (MacroOptions → SelectedMacroName,
            │          visible on ShowMacroPicker, #390)
            │       + Choose Icon button (EB9F, MenuCellChooseIcon_Click, #390)
            │       + Reset (ResetCellCommand)
            └─ Icon Packages card (CardBorder, EB9F glyph, #390)
                ├─ Pad_Menus_IconPackages_Header + description
                ├─ Add (IconPackageAdd_Click) / Create (IconPackageCreate_Click) /
                │   Remove (IconPackageRemove_Click) buttons
                ├─ IconPackagesEmptyText (Pad_Menus_IconPackages_Empty)
                └─ IconPackagesList ListBox (MaxHeight 170, EmberSelectListItem,
                    per row: EB9F glyph + Name + Path)
```

Every setting row carries the canonical Reset button, and the host row carries Record too (the Aim Engage cluster shape). The record button binds `MenuHostRecordCommand` on the PadViewModel through the TabItem's DataContext because the editor panel's own DataContext is the selected `MenuEditorItem`.

The four cell pickers each use `ComboBoxWidthBehavior.SizeToItems` with a per-column `WidthGroup` (`MenuCellKindCombos`, `MenuCellKeyCombos`, `MenuCellButtonCombos`, `MenuCellMacroCombos`), so rows stay in column across selections and long locales do not clip.

**Icon Packages block (#390).** Takes the Sound Packages card's shape. A pack is one zip file with the `.pficons` extension holding image entries plus an optional `manifest.json` display name (`PadForge.App/Common/IconPackageManager.cs`). PadForge never extracts a pack: importing one registers its path, and cells reference entries as `pficon://PackName/entry.png` beside loose image paths and Steam binding-icon names. The list and its empty-state text are filled from code-behind (`RefreshIconPackages` sets `IconPackagesList.ItemsSource` from `IconPackageManager.Packages`), and `IconPackageManager.RegistryChanged` re-runs it.

### HIDMaestro Profile Bar

`HMaestroProfileBar` is a `ChipGhost` preset chip inline in tier 1, shown for `Xbox`, `PlayStation`, and `Nintendo` slots. Its visibility is `HasHMaestroProfileBar && !isExtended`. `HasHMaestroProfileBar` is true for Xbox, PlayStation, Nintendo, and Extended, but Extended slots hide this compact chip and use the separate `ExtendedConfigBar` (with its own `ExtendedProfileCombo`) instead. It contains the profile picker only:

| Control | AutomationId | Binding |
|---------|--------------|---------|
| Profile ComboBox | `HMaestroProfileCombo` | `ProfileId`, items from `AvailableProfiles` (HMaestro profile catalog) |

The profile drives identity (VID/PID/product string) and layout (axes/buttons/POVs/touchpad/rumble) for the HM virtual.

### Extended Config Bar

`ExtendedConfigBar` is shown when `OutputType == Extended`. Stacked rows:

| Row | Controls | Notes |
|-----|----------|-------|
| 1 | `ExtendedProfileCombo` + `ExtendedImportBtn` | Profile picker (same `AvailableProfiles` source) plus Import-From-Device |
| 2 | `ExtendedCustomizeChk` + `ExtendedResetDefaultsBtn` | Master toggle for the rows below. Reset reverts to catalog defaults |
| 3 | `ExtendedProductStringBox`, `ExtendedOemOverrideChk`, `ExtendedVidBox`, `ExtendedPidBox` | Identity overrides |
| 4 | `RawStickCountBox`, `ExtendedTriggerCountBox`, `RawPovCountBox`, `RawButtonCountBox`, `ExtendedForceFeedbackChk` | Layout overrides. The count boxes kept their v2 `Raw*` names except triggers |

Override rows 3 and 4 are gated by `IsChecked={ElementName=ExtendedCustomizeChk}`, so toggling Customize off restores the catalog profile as-is. `_syncingExtendedConfig` guard prevents recursive updates inside `SyncExtendedConfigBar()`.

### MIDI Config Bar

Visible when `OutputType == Midi`. Centered horizontal `StackPanel`:

| Control | Binding | Range |
|---------|---------|-------|
| Channel TextBox | `MidiConfig.Channel` | 1-16 |
| CC Count TextBox | `MidiConfig.CcCount` | 0 to 128 − StartCc (clamped against StartCc) |
| Start CC TextBox | `MidiConfig.StartCc` | 0-127 |
| Note Count TextBox | `MidiConfig.NoteCount` | 0 to 128 − StartNote (clamped against StartNote) |
| Start Note TextBox | `MidiConfig.StartNote` | 0-127 |
| Velocity TextBox | `MidiConfig.Velocity` | 0-127 |

All fields have tooltips. `_syncingMidiConfig` guard prevents recursive updates. When CC/Note counts or start numbers change, `vm.RebuildMappings()` regenerates mapping rows.

### Copy From Dialog

Opens `CopyFromDialog`. Picking a source slot copies the whole mapping table plus every assigned device's tuning (deadzones, sensitivity, FFB, impulse triggers, adaptive triggers, lighting, gyro, TouchpadSettings) into the target slot. Each source device matches a target device by `InstanceGuid` first, then `ProductGuid` as a fallback for the same controller model on a different physical unit. Target devices without a source-side match are left alone.

---

## DevicesPage

**Files:** `DevicesPage.xaml`, `DevicesPage.xaml.cs`

All detected input devices with raw input state visualization.

### Layout Structure

```
Grid (Margin="24,16")
├─ Row 0 (Auto): Header
│   ├─ Icon (E772) + Title
│   ├─ Refresh Button (E72C, RefreshCommand)
│   ├─ Pair Button (E702, PairCommand → PairDeviceDialog)
│   └─ Online/Total count display (telemetry mono)
└─ Row 1 (*): Main content (Grid, 2 columns)
    ├─ Col 0 (*): Facet chips + device card ListBox + drag-assign hint
    │   ├─ Row 0: Type facet chips (ALL / GAMEPAD / JOYSTICK / WHEEL / KEYBOARD /
    │   │    MOUSE / OTHER, MouseLeftButtonUp="FacetChip_Click", count per chip)
    │   ├─ Row 1: ListBoxItem with custom ControlTemplate (4px accent left bar on selection)
    │   │   └─ Card Border (CornerRadius=8, Padding="12,10")
    │   │       ├─ Row 0, Col 0: LivenessFlame Path + DeviceName (SemiBold, 13px)
    │   │       ├─ Row 0-1, Col 1: Slot badges (WrapPanel of numbered badges).
    │   │       │    No badges means unassigned. There is no fallback pill
    │   │       ├─ Row 0-1, Col 2: Remove device Button (E711 × icon)
    │   │       └─ Row 1: DeviceType + VID:PID + CapabilitiesSummary
    │   └─ Row 2: Devices_DragAssignHint text
    └─ Col 1 (340px): Detail panel (Border with ScrollViewer)
        ├─ DeviceName headline (CardTitle, wrapping)
        ├─ Device Dossier (#175 competitor item 7): eyebrow + copy Button
        │   (CopyDossier_Click, E8C8) over a recessed telemetry-mono card whose
        │   token rows run PRODUCT / TYPE / CAPS / APP GUID / SDL GUID /
        │   PATH (HidHideInstancePath) / PATH (DossierConnectionPath) / VID:PID /
        │   LINK / SERIAL / BATT. Rows whose fact is absent collapse. LINK reads
        │   "BT" and shows only on IsBluetoothLink
        ├─ Capability chip strip (HasCapabilityIcons): rumble (E877, doubles as the
        │   identify button via IdentifyChip_Click, #293), gyro (E7AD), touchpad (EFA5)
        ├─ Submit Mapping Button (joysticks only, opens GitHub issue template)
        ├─ Register / Manage NFC Tags Button (RegisterNfcTag_Click, ShowRegisterNfcTag, #150)
        ├─ Manage Voice Macros Button (ManageVoicePhrases_Click, ShowManageVoicePhrases, #317)
        ├─ Learn Handheld Buttons Button (LearnHandheldButton_Click,
        │   ShowLearnHandheldButton, #343) + HandheldDaemonWarning line
        ├─ HeadTrackerStatus line (#355, collapsed when empty)
        ├─ Separator
        ├─ VC Assignment section
        │   └─ WrapPanel of ToggleButtons (ActiveSlotItems, ToggleSlotCommand)
        ├─ Input Mode section (ShowInputModeSection)
        │   └─ "Force raw joystick mode" CheckBox (ForceRawJoystickMode)
        ├─ Input Hiding section (ShowInputHidingSection)
        │   ├─ "Hide from games (HidHide)" CheckBox (HidHideEnabled, HidingToggle_Click)
        │   └─ "Consume mapped inputs" CheckBox (ConsumeInputEnabled, ShowConsumeToggle)
        ├─ Separator (ShowInputModeOrHidingSection)
        ├─ Power section (ShowPowerSection)
        │   ├─ Idle Disconnect minutes TextBox (IdleDisconnectMinutes,
        │   │   ShowIdleDisconnect, #162)
        │   └─ Quick Charge CheckBox (QuickChargeEnabled, ShowQuickCharge,
        │       QuickCharge_Click, #372)
        ├─ Separator (ShowRawInputDivider)
        └─ Raw Input State section
            ├─ Axes (joysticks/gamepads, hidden for keyboard/mouse)
            │   └─ ItemsControl → ProgressBar per axis (0-1, name + bar + raw value)
            ├─ Buttons (joysticks/gamepads, hidden for keyboard/mouse)
            │   └─ WrapPanel of 24×24 circles, accent fill when pressed
            ├─ NFC named-tag preview (#150, IsNfcDevice)
            │   └─ ItemsControl → NfcTags (registered named tags)
            ├─ Consumer Control named-chip preview (#168, IsConsumerDevice)
            │   └─ ItemsControl → ConsumerButtons (named button chips)
            ├─ Keyboard layout (keyboard devices only)
            │   └─ Viewbox → Canvas (556×136) with positioned key Borders
            ├─ Mouse preview (mouse devices only)
            │   └─ Viewbox → MousePreviewControl
            ├─ MIDI preview (MIDI input devices)
            │   └─ MidiPreviewView ×2 (MidiNotesPreview, MidiCcPreview)
            ├─ D-Pad / POV hats (conditional on RawPovs.Count > 0)
            │   └─ Horizontal StackPanel of compass indicators
            │       ├─ 36×36 Ellipse background + center dot
            │       └─ Accent-colored Line with RotateTransform(AngleDegrees), hidden when IsCentered
            ├─ Gyroscope (HasGyroData, 3-column X/Y/Z grid, telemetry mono F3 format)
            ├─ Accelerometer (HasAccelData, same layout as gyro)
            ├─ Aux Accelerometer (HasAccelAuxData, same layout, the Nunchuk sensor / combined pair's left-half accel, #199)
            ├─ Aux Gyro (HasGyroAuxData, same layout, the combined pair's left Joy-Con, #252)
            ├─ Touchpad preview (HasTouchpadData, up to 5 contact dots per pad,
            │   TouchpadPreviewBorder, plus Touchpad2PreviewBorder on HasSecondTouchpadData)
            ├─ Handheld hidden buttons (#343, IsHandheldDevice)
            │   └─ Learned button chips, or the Handheld_NoneLearned line
            └─ Voice phrases (#317, ShowVoicePhrases)
                └─ ItemsControl → VoicePhrases (registered phrase chips)
```

### Key Bindings

| Binding | ViewModel | Description |
|---------|-----------|-------------|
| `Devices` | `DevicesViewModel` | Device list collection |
| `SelectedDevice` | `DevicesViewModel` | Currently selected device row |
| `HasSelectedDevice` | `DevicesViewModel` | Controls detail panel visibility |
| `OnlineCount` / `TotalCount` | `DevicesViewModel` | Header device counts |
| `RefreshCommand` | `DevicesViewModel` | Refresh button |
| `ActiveSlotItems` | `DevicesViewModel` | Slot toggle button items |
| `ToggleSlotCommand` | `DevicesViewModel` | Toggle device-to-slot assignment |
| `RemoveDeviceCommand` | `DevicesViewModel` | Remove device from list |
| `SelectedFacet` | `DevicesViewModel` | Active type facet chip. `FacetCountGamepad` and friends fill the per-chip counts |

### Device Card Bindings (DeviceRowViewModel)

| Binding | Description |
|---------|-------------|
| `IsOnline` | Drives a `LivenessFlame` `Path` (fills `EmberBrush` with a glow when online, `LivenessFlameBase` outline stroke when offline). The device-name text also dims when offline. |
| `DeviceName` | Bold device name |
| `SlotBadges` | Collection of slot assignment badges. Absence of badges encodes unassigned (#175 phase 2 item 9 removed the `IsUnassigned` flag and its gray fallback pill) |
| `DeviceType` | Type string |
| `VendorIdHex` / `ProductIdHex` | Hex VID:PID |
| `CapabilitiesSummary` | e.g. "6 axes, 11 buttons, 1 POV" |
| `BatteryGlyph` / `BatteryText` | Battery indicator (#167): Segoe MDL2 Assets glyph + "78%", hidden when `HasBattery` is false |

### Detail Panel Bindings (SelectedDevice)

| Binding | Description |
|---------|-------------|
| `DeviceName`, `ProductName`, `DeviceType` | Device identity (dossier PRODUCT / TYPE rows) |
| `CapabilitiesSummary` | Dossier CAPS row |
| `InstanceGuid` | Dossier APP GUID row |
| `SdlGuid`, `DossierConnectionPath`, `SerialNumber` | Dossier SDL GUID / LINK / SERIAL rows, each collapsed via `StringToVisibility` when empty |
| `HidHideInstancePath` | Dossier PATH row (conditional visibility via `StringToVisibility`) |
| `ShowSubmitMapping` | Submit mapping button visibility (joysticks only) |
| `ShowInputModeSection` | Input Mode section visibility (`IsGamepad && !IsInternalVirtual`) |
| `ShowInputHidingSection` | Input Hiding section visibility (`!IsInternalVirtual`) |
| `ForceRawJoystickMode` | Force raw toggle |
| `IsHidHideAvailable` | Enables/disables HidHide checkbox |
| `HidHideEnabled` | HidHide toggle |
| `ShowConsumeToggle` | Consume toggle visibility (mouse/keyboard devices) |
| `ConsumeInputEnabled` | Consume toggle |
| `ShowPowerSection` | Power section visibility. True when either row below draws |
| `ShowIdleDisconnect` / `IdleDisconnectMinutes` | Idle-disconnect row visibility and its countdown minutes (#162) |
| `ShowQuickCharge` / `QuickChargeEnabled` | Quick Charge row visibility and toggle (#372). Also true on a Sony record the USB cable rebound to its wired path, which is not a disconnect target and is exactly when the feature fires |
| `ShowInputModeOrHidingSection` / `ShowRawInputDivider` | The two conditional separators around the Power section |
| `HasCapabilityIcons` / `HasRumble` / `HasGyro` / `ShowTouchpadCapability` | Capability chip strip and its three chips |
| `ShowLearnHandheldButton` / `HandheldDaemonWarning` / `HasHandheldDaemonWarning` | Learn Handheld Buttons button and the vendor-daemon notice (#343) |
| `ShowRegisterNfcTag` | Register/Manage NFC Tags button visibility (#150) |
| `ShowManageVoicePhrases` | Manage Voice Macros button visibility (#317): a standalone microphone row, or a DualSense / DualSense Edge over Bluetooth where the pad itself carries the phrases. Never for a `peer://` path, since recognition runs on the owner |
| `RawAxes` | Axis ProgressBar items |
| `RawButtons` | Button circle items |
| `IsKeyboardDevice` / `IsMouseDevice` | Switches between button circles, keyboard canvas, or mouse graphic |
| `KeyboardKeys` | QWERTY keyboard layout items |
| `RawPovs` | POV compass items |
| `HasGyroData` / `HasAccelData` / `HasAccelAuxData` / `HasGyroAuxData` | Gyro / accel / aux-accel / aux-gyro section visibility |
| `GyroX/Y/Z` / `AccelX/Y/Z` / `AccelAuxX/Y/Z` | Motion sensor values (aux accel is #199, aux gyro is #252) |
| `HasTouchpadData` / `HasSecondTouchpadData` / `TouchpadLabel` | Touchpad preview visibility for each pad, and the caption |

The raw-state rows above bind to the page DataContext (`DevicesViewModel`), which republishes the selected device's live state. The NFC, Voice, Consumer, and handheld previews do the same: `IsNfcDevice` / `NfcTags`, `ShowVoicePhrases` / `VoicePhrases` (#317, the voice twin of the NFC tag rows), `IsConsumerDevice` / `ConsumerButtons`, and `IsHandheldDevice` (#343). `HeadTrackerStatus` is page-scoped too. Everything under the dossier and the sections below it, including `ShowRegisterNfcTag`, `ShowQuickCharge`, and `IdleDisconnectMinutes`, is `SelectedDevice`-scoped and binds through the `SelectedDevice.` prefix.

### Selection Highlighting

Custom `ListBoxItem` `ControlTemplate`:
- `SelectionBar`. 4px `Border` with accent brush on left edge, `CornerRadius="2"`.
- Toggled by `IsSelected` trigger.
- Content offset 6px right to accommodate the bar.

### Event Handlers (Code-Behind)

| Handler | Trigger | Action |
|---------|---------|--------|
| `RemoveDevice_Click` | Button.Click | Selects device, executes `RemoveDeviceCommand` |
| `FacetChip_Click` | Border.MouseLeftButtonUp | Sets `SelectedFacet` from the chip's `Tag`, filtering the device list |
| `HidingToggle_Click` | CheckBox.Click | Shows warning flyout for mouse/keyboard enable, clears `LastRawStateDeviceGuid` for rebuild, calls `NotifyDeviceHidingChanged` |
| `ShowHidingWarningFlyout` | (internal) | WPF UI `Flyout` with warning icon, message, Proceed/Cancel buttons. Reverts checkbox immediately, re-checks only on Proceed. |
| `SubmitMapping_Click` | Button.Click | Opens browser to GitHub issue template with device info pre-filled |
| `CopyDossier_Click` | Button.Click | Copies the device dossier's token rows to the clipboard |
| `RegisterNfcTag_Click` | Button.Click | Opens `RegisterNfcTagDialog` for the selected NFC reader (#150) |
| `ManageVoicePhrases_Click` | Button.Click | Opens `RegisterVoicePhraseDialog` for the selected microphone-carrying device (#317) |
| `LearnHandheldButton_Click` | Button.Click | Opens `LearnHandheldButtonDialog` for the machine's hidden buttons (#343) |
| `IdentifyChip_Click` | Border.MouseLeftButtonUp | Forwards to `IdentifyDevice_Click`, which calls `InputService.IdentifyDevice(SelectedDevice.InstanceGuid)` to vibrate the pad (#293) |
| `QuickCharge_Click` | CheckBox.Click | Persists the Quick Charge toggle. Click, not Checked, so the binding-driven refresh on a selection change never writes (#372) |
| `IdleDisconnect_LostFocus` | TextBox.LostFocus | Applies the clamped idle-disconnect minutes (#162) |
| `DeviceCard_MouseDown` | PreviewMouseLeftButtonDown | Records drag start position. Skips if inside a Button |
| `DeviceCard_MouseMove` | PreviewMouseMove | Initiates `DragDrop.DoDragDrop` with `DeviceInstanceGuid` data when threshold exceeded |
| `DeviceCard_MouseUp` | PreviewMouseLeftButtonUp | Resets drag state |

### Device Drag to Sidebar

Device cards support drag via mouse events. Drag data is a `DataObject` with key `"DeviceInstanceGuid"` and value `device.InstanceGuid`. Drop on a sidebar controller card assigns the device to that slot.

---

## KBMPreviewView

**Files:** `KBMPreviewView.xaml`, `KBMPreviewView.xaml.cs`

Keyboard and mouse preview for Keyboard+Mouse virtual controller slots, shown on the PadPage Preview tab.

### Layout

Two horizontal `Canvas` areas:

- **KeyboardCanvas**. QWERTY layout built from `KeyboardKeyItem.BuildLayout()`. Each key is a `Border` + `TextBlock`, absolutely positioned. Keys highlight with accent color when pressed in the output state.
- **MouseCanvas**. Stylized mouse graphic: contoured LMB/RMB paths, scroll wheel pill, movement circle with deflection dot, scroll arrows, and X1/X2 side buttons.

### Interaction

All elements are clickable for **click-to-record**. Fires `ControllerElementRecordRequested` with the target name (e.g., `KbmKey41`, `KbmMBtn0`, `KbmMouseX`). Hover highlights use ember (`HoverBrush` `#FFA24D`). Recording targets flash at 400ms with orange (`FlashBrush` `#FFA500`). Pressed keys light ember (`KeyPressedBrush` `#FF6B2C`).

### Rendering

Uses `CompositionTarget.Rendering` with a `_dirty` flag. Per frame:
- Keyboard keys: reads `KbmOutputSnapshot.GetKey()` per VK index, sets accent background on pressed keys.
- Mouse buttons: reads `GetMouseButton()` for LMB/RMB/MMB/X1/X2.
- Movement dot: maps `MouseDeltaX`/`MouseDeltaY` to deflection within the movement circle.
- Scroll arrows: lights up/down arrows based on `ScrollDelta` sign.

### Theme-Aware Brushes

Pre-cached `static readonly` dark and light brush variants for key backgrounds, borders, and text. The full set is rebuilt on theme change, avoiding per-frame `DynamicResource` lookups.

### Tooltip Helper

`MappingLabel()` resolves target setting names to human-readable labels from the mapping table, falling back to the raw name. X1/X2 side button `Rectangle` elements are promoted to named fields for flash support.

---

## MidiPreviewView

**Files:** `MidiPreviewView.xaml`, `MidiPreviewView.xaml.cs`

MIDI note and CC visualization for MIDI virtual controller slots, shown on the PadPage Preview tab. The same control serves the Devices page twice (`MidiNotesPreview`, `MidiCcPreview`) for a physical MIDI input device's raw state.

### Layout

Single `Canvas` (`MidiCanvas`), rebuilt when `MidiSlotConfig` properties change (start note, note count, start CC, CC count):

- **CC Sliders**. Vertical bars, one per CC. Background rectangle + fill rectangle proportional to value (0-127) + CC number label.
- **Piano Keyboard**. Standard chromatic layout: white keys full-height underneath, black keys shorter on top (higher Z-index). White keys show note name + octave (e.g., "C4", "D4").

### Interaction

CC sliders and piano keys are clickable for click-to-record (fires `ControllerElementRecordRequested` with `MidiCC{index}` or `MidiNote{index}`). Hover highlights and 400ms flash timer match other preview views.

### Rendering

Uses `CompositionTarget.Rendering` with a `_dirty` flag. Per frame:
- CC sliders: reads `MidiOutputSnapshot.CcValues[]`, scales fill height to 0-100%.
- Piano keys: reads `MidiOutputSnapshot.Notes[]` boolean array, applies the pressed brush (ember-hot `#FFA24D` for white keys, ember-deep `#C43D0C` for black keys) on active notes.

### Theme-Aware Brushes

Pre-cached `static readonly` dark and light brush variants for CC bar fills, piano key surfaces, and label text. Rebuilt on theme change to avoid per-frame `DynamicResource` overhead.

### Layout Rebuild

The entire canvas is cleared and rebuilt on any `MidiSlotConfig` property change. No partial layout updates.

---

## VRPreviewView

**Files:** `VRPreviewView.xaml`, `VRPreviewView.xaml.cs`

Live preview for a VR slot (#49), shown on the PadPage Preview tab. One VR slot drives both SteamVR hands, so the art is the pair side by side rather than a single controller body.

### Layout

`Viewbox` over a single `Canvas` (`VrCanvas`), built once on `Loaded` from the 2D art in `2DModels/VRCONTROLLER/`. Base art is 975×726, and the twelve elements are positioned in those pixels:

| Element | Targets |
|---------|---------|
| `VRController_L_Stick` / `_R_Stick` | `VrLStick` / `VrRStick` (click plus four directions) |
| `VRController_L_A` / `_R_A` | `VrLA` / `VrRA` (inner press disc, outer touch ring) |
| `VRController_L_B` / `_R_B` | `VrLB` / `VrRB` |
| `VRController_L_System` / `_R_System` | `VrLSystem` / `VrRSystem` (single-target) |
| `VRController_L_Trigger` / `_R_Trigger` | `VrLTrigger` / `VrRTrigger` (body axis, tip band click) |
| `VRController_L_Grip` / `_R_Grip` | `VrLGrip` / `VrRGrip` |

### Rendering

Element tinting follows the `Rectangle` + `ImageBrush` `OpacityMask` idiom the branded 2D packs use: the cutout supplies the shape and one brush supplies the color, so lit, hover, and flash all drive the same layer. Triggers and grips fill bottom-up through a `RectangleGeometry` clip rather than scaling opacity. Stick caps translate up to 14px with deflection, and the stick's tint layer and region highlight share that transform. Frames come from `CompositionTarget.Rendering` against a cached `VrRawState`.

### Interaction

Same click-to-record contract as the other previews, including `Bind(vm)` / `Unbind()` and `ControllerElementRecordRequested`. Every element except System carries more than one target, so each one gets a region highlight: the element's own overlay clipped to the region under the pointer, at the drawn packs' 0.4 hover opacity.

---

## MousePreviewControl

**Files:** `MousePreviewControl.xaml`, `MousePreviewControl.xaml.cs`

Read-only mouse graphic for mouse-type devices on the Devices page detail pane.

### Layout

Built once on `Loaded` into `Canvas` (`MouseCanvas`). Same mouse shape as `KBMPreviewView` but without click-to-record:

- **LMB/RMB**. Contoured `Path` elements flanking the scroll wheel.
- **Scroll wheel**. Rounded `Rectangle` between buttons, with up/down arrow `Polygon` indicators.
- **Movement circle**. `Ellipse` with deflection dot tracking live mouse delta.
- **X1/X2 side buttons**. Small `Rectangle` elements on the left edge.

### Theme-Aware Brushes

Pre-cached `static readonly` dark and light brush variants for mouse body, button fills, and indicator colors. Rebuilt on theme change, consistent with KBMPreviewView and MidiPreviewView.

### Rendering

Uses `CompositionTarget.Rendering` (no dirty flag. Every frame). Reads from `DevicesViewModel`:
- Buttons: `RawButtons[0..4].IsPressed` mapped to LMB, MMB, RMB, X1, X2.
- Movement: `MouseMotionX`/`MouseMotionY` (normalized) to dot deflection.
- Scroll: `MouseScrollIntensity` drives arrow fill, opacity, and scale. Arrows grow and brighten with scroll magnitude.

---

## SettingsPage

**Files:** `SettingsPage.xaml`, `SettingsPage.xaml.cs`

Application settings in vertical `CardBorder` sections.

Card order is pinned by `Settings_CardsRunInTheDecidedOrder` in `PadForge.Tests/PageOrderContractTests.cs`, which asserts each card title's binding appears once and after the one before it.

### Layout Structure

```
ScrollViewer (Padding="24,0")
  └─ StackPanel (Margin="0,16,0,16")
      ├─ Page header (E713 gear icon + title)
      ├─ Language card (CardBorder)
      │   ├─ Icon F2B7 + "Language" title + description
      │   └─ ComboBox (AvailableLanguages, DisplayMemberPath="NativeName", Width=250)
      ├─ Appearance card
      │   ├─ Icon E790 + "Appearance" title + description
      │   ├─ "Theme" label
      │   ├─ ComboBox (System Default / Light / Dark, SelectedIndex=SelectedThemeIndex)
      │   └─ "Show Tour" Button (Settings_ShowTour, ShowTour_Click) → re-runs the first-run spotlight tour
      ├─ Window card
      │   ├─ Icon E737 + title + description
      │   ├─ Minimize to tray (MinimizeToTray)
      │   ├─ Start minimized (StartMinimized)
      │   └─ Start at login (StartAtLogin)
      ├─ Input Engine card
      │   ├─ Icon E9F5 + title + description
      │   ├─ Auto-start toggle (AutoStartEngine)
      │   ├─ Background polling toggle (EnablePollingOnFocusLoss)
      │   ├─ Polling interval: NumberBox 1-16ms (PollingRateMs) + "ms"
      │   ├─ PollingOverrideNote (ember, shown only while the active profile
      │   │   overrides the global value, #365)
      │   └─ HM inactivity timeout: NumberBox 0-3600s
      │      (HmInactivityDestroyTimeoutSeconds, 0 = never)
      ├─ Assignment Prompts card
      │   ├─ Icon E8DE + title + description
      │   ├─ Offer on a new device (AssignOfferNewDevice)
      │   └─ Offer on an empty slot (AssignOfferEmptySlot)
      ├─ Handheld PC Buttons card (#343)
      │   ├─ Icon E7F8 + title + description
      │   └─ Enable toggle (HandheldButtonsEnabled). On, the Devices page gains
      │      the machine's Hidden Buttons row and its System Motion row
      ├─ Battery Alerts card (#293)
      │   ├─ Icon E83F + title + description
      │   ├─ "Notify When Battery Runs Low" toggle (BatteryNotifyEnabled)
      │   ├─ "Notify at or Below" NumberBox 5-50 % (BatteryNotifyThreshold)
      │   ├─ "Also Vibrate the Controller" toggle (BatteryNotifyVibrate)
      │   └─ "Test Notification" Button (TestBatteryNotify_Click)
      ├─ HidHide Driver card
      │   ├─ Icon ED1A + title + description
      │   ├─ Status: flame + HidHideStatusText + HidHideVersion
      │   ├─ Install/Uninstall buttons (visibility-toggled by IsHidHideInstalled)
      │   ├─ Hide devices toggle (EnableInputHiding)
      │   ├─ Keep cloaks between launches toggle (KeepHidHideCloaksBetweenLaunches)
      │   └─ Whitelist section (only when installed):
      │       ├─ Title + description
      │       ├─ ListBox of HidHideWhitelistPaths (Consolas, 12px)
      │       └─ Add/Remove buttons
      ├─ HIDMaestro Driver card
      │   ├─ Icon E7FC + title + description
      │   └─ Status: always-lit ember flame + "Installed" + HIDMaestroVersion (no Install/Uninstall
      │      buttons, because HIDMaestro is embedded in the binary)
      ├─ Windows MIDI Services card
      │   ├─ Icon E8D6 + title + description
      │   ├─ Status: flame + MidiServicesStatusText + MidiServicesVersion
      │   └─ Install/Uninstall buttons (Install disabled tooltip when MidiOsSupported=False)
      ├─ SteamVR card (#49)
      │   ├─ Icon F119 + title + description
      │   ├─ Status: flame + IsSteamVrInstalled state
      │   ├─ Install directory TextBox + Browse button (SteamVrBrowse_Click → SteamVrInstallDir)
      │   └─ Install/Uninstall buttons (InstallSteamVrCommand / UninstallSteamVrCommand)
      ├─ Community Configs card (#9)
      │   ├─ Icon E716 (EmberBrush) + title + description (the endpoint / privacy statement)
      │   ├─ Enable Community Configs checkbox (EnableCommunityConfigLookup)
      │   ├─ Show Legacy Workshop Configs checkbox (ShowLegacyWorkshopConfigs, visible only when enabled)
      │   └─ Clear Cached Configs + Check Imported Profiles for Updates buttons
      ├─ Settings File card
      │   ├─ Icon E8A5 + title + description
      │   ├─ SettingsFilePath (Consolas, wrapping)
      │   ├─ Save / Reload / Reset to Defaults / Open Folder buttons
      │   └─ "Unsaved changes" warning (orange, HasUnsavedChanges)
      └─ Diagnostics card
          ├─ Icon E9D9 + title + description
          ├─ Grid (140px label + value):
          │   ├─ App Version (ApplicationVersion)
          │   ├─ .NET Runtime (RuntimeVersion)
          │   └─ SDL Version (SdlVersion)
          ├─ "Keep a Diagnostics Log" toggle (DiagnosticsLoggingEnabled) (#303)
          ├─ Log folder path readout (DiagnosticsFolderPath)
          └─ "Save Snapshot" + "Open Log Folder" buttons (SaveDiagSnapshot_Click / OpenDiagFolder_Click)
```

### Key Bindings

| Binding | Target | Description |
|---------|--------|-------------|
| `AvailableLanguages` | ComboBox ItemsSource | Language options with `NativeName` display |
| `SelectedLanguage` | ComboBox SelectedItem | Current language |
| `SelectedThemeIndex` | ComboBox SelectedIndex | 0=System, 1=Light, 2=Dark |
| `AutoStartEngine` | CheckBox | Auto-start engine on launch |
| `EnablePollingOnFocusLoss` | CheckBox | Continue polling when app loses focus |
| `PollingRateMs` | NumberBox (1-16) | Polling interval in ms |
| `HmInactivityDestroyTimeoutSeconds` | NumberBox (0-3600) | Seconds of device inactivity before the VC is torn down. 0 means never |
| `EnableInputHiding` | CheckBox | Master input hiding toggle (HidHide card) |
| `KeepHidHideCloaksBetweenLaunches` | CheckBox | Leave cloaks in place across app restarts |
| `MinimizeToTray` | CheckBox | Minimize to system tray |
| `StartMinimized` | CheckBox | Start app minimized |
| `StartAtLogin` | CheckBox | Start at Windows login |
| `BatteryNotifyEnabled` / `BatteryNotifyThreshold` / `BatteryNotifyVibrate` | CheckBox, NumberBox (5-50), CheckBox | Battery Alerts card: low-battery toast on/off, the percent threshold, and the optional controller vibration (#293) |
| `IsHidHideInstalled` | bool | Controls status flame, button visibility, whitelist section |
| `InstallHidHideCommand` / `UninstallHidHideCommand` | ICommand | Driver install/uninstall |
| `HidHideWhitelistPaths` | Collection | Whitelist ListBox items |
| `SelectedWhitelistPath` | object | Selected whitelist item |
| `AddWhitelistPathCommand` / `RemoveWhitelistPathCommand` | ICommand | Whitelist management |
| `IsMidiServicesInstalled` / `MidiOsSupported` | bool | MIDI Services status. Controls Install button visibility and disabled-tooltip. `MidiOsSupported` is the instance forwarder of the static `IsMidiOsSupported`, which a Binding cannot reach |
| `IsSteamVrInstalled` / `IsSteamVrOwned` / `SteamVrInstallDir` | bool, bool, string | SteamVR card status, whether PadForge created the Steam-free install, and its directory (#49) |
| `InstallSteamVrCommand` / `UninstallSteamVrCommand` | ICommand | SteamVR install/uninstall |
| `SaveCommand` / `ReloadCommand` / `ResetCommand` / `OpenSettingsFolderCommand` | ICommand | Settings file operations |
| `EnableCommunityConfigLookup` / `ShowLegacyWorkshopConfigs` | CheckBox | Steam Workshop opt-in + legacy sub-toggle (#9) |
| `ClearWorkshopCacheCommand` / `CheckWorkshopUpdatesCommand` | ICommand | Workshop cache clear and imported-profile update check |
| `HasUnsavedChanges` | bool | Orange warning visibility |
| `DiagnosticsLoggingEnabled` / `DiagnosticsFolderPath` | CheckBox, string | Diagnostics card: continuous engine-event log toggle and the folder it writes to (#303) |

### Code-Behind

Five handlers beyond the constructor. Everything else lives in the ViewModel.

| Handler | Trigger | Action |
|---------|---------|--------|
| `TestBatteryNotify_Click` | Battery Alerts card button | Calls `InputService.TestBatteryNotification()` to fire the low-battery pipeline with a synthetic event (#293) |
| `SaveDiagSnapshot_Click` | Diagnostics card button | `DiagnosticsLogControl.SaveSnapshot()` dumps the in-memory engine event ring to a timestamped file and selects it in Explorer (#303) |
| `OpenDiagFolder_Click` | Diagnostics card button | Creates the diagnostics folder if needed and opens it in Explorer (#303) |
| `ShowTour_Click` | Appearance card button | Calls `MainWindow.StartFirstRunTour()` to re-run the welcome tour (#175) |
| `SteamVrBrowse_Click` | SteamVR card button | `OpenFolderDialog` for the Steam-free SteamVR install directory, writes `SettingsViewModel.SteamVrInstallDir` (#49) |

---

## ProfilesPage

**Files:** `ProfilesPage.xaml`, `ProfilesPage.xaml.cs`

Per-app profile management.

### Layout Structure

```
ScrollViewer (Padding="24,0")
  └─ StackPanel (Margin="0,16,0,16")
      ├─ Page header (E8F1 people icon + title)
      └─ CardBorder
          ├─ Icon E8B7 + "Management" title + description
          ├─ Auto-switch CheckBox (EnableAutoProfileSwitching)
          ├─ FOREGROUND live readout (visible only while auto-switch is on):
          │   mono token + lit flame when IsForegroundMatched + ForegroundExeName,
          │   plus the no-rules hint when NoProfileHasExecutables
          ├─ External Control CheckBox (EnableExternalControl, #366), off by default
          ├─ Drop-zone Grid (AllowDrop, ProfileList_DragEnter/DragOver/DragLeave/Drop
          │   for .pfprofile import, ProfileDropOverlay cue)
          │   └─ Profile card ListBox (ProfileListBox, WrapPanel of steel cards,
          │       MinHeight=92, MaxHeight=452, MouseDoubleClick loads)
          │       └─ ItemTemplate:
          │           ├─ Profile Name (SemiBold) + "Built in" tag on the default
          │           ├─ Executable names (FirstExecutableName, SecondExecutableName,
          │           │   ExtraExecutablesSuffix, each collapsed when empty)
          │           └─ Type count badges (horizontal StackPanel):
          │               ├─ Xbox badge: Xbox SVG + XboxCount (collapsed when 0)
          │               ├─ PlayStation badge: PS SVG + PlayStationCount (collapsed when 0)
          │               ├─ Extended badge: Joystick SVG + ExtendedCount (collapsed when 0)
          │               ├─ MIDI badge: E8D6 glyph + MidiCount (collapsed when 0)
          │               ├─ KB+M badge: E961 glyph + KbmCount (collapsed when 0)
          │               ├─ Nintendo badge: Switch SVG + NintendoCount (collapsed when 0)
          │               ├─ VR badge: F119 glyph + VrCount (collapsed when 0)
          │               └─ "No slots" fallback (visible when HasNoSlots=True)
          └─ Action buttons: New / Save As / Load / Edit / Export / Import /
             Browse Starters / Browse Community / Delete
```

### Key Bindings

| Binding | Target | Description |
|---------|--------|-------------|
| `EnableAutoProfileSwitching` | CheckBox | Enables foreground app monitoring |
| `EnableExternalControl` | CheckBox | Opens the named pipe that lets a launcher or script activate a profile (#366). It sits with the auto-switch and shortcut controls because it is a third way a profile activates, not a global engine service. The `SettingsViewModel` setter mirrors into `SettingsManager.EnableExternalControl`, which `InputService` watches to start or stop `ExternalControlService`. Switching profiles by hand releases the hold a script placed |
| `ForegroundExeName` / `IsForegroundMatched` / `NoProfileHasExecutables` | TextBlock, flame, hint | The FOREGROUND live readout. `SettingsViewModel.ActiveProfileInfo` is set by the services but is not bound on this page. The status bar's `ProfilePill` carries the active-profile name |
| `ProfileItems` | ListBox ItemsSource | Profile list |
| `SelectedProfile` | ListBox SelectedItem | Selected profile. `SelectedProfile.IsDefault` disables Edit and Delete |
| `NewProfileCommand` | Button | Create new profile |
| `SaveAsProfileCommand` | Button | Save current config as profile |
| `EditProfileCommand` | Button | Edit profile name/exes |
| `LoadProfileCommand` | Button | Load selected profile |
| `ExportProfileCommand` / `ImportProfileCommand` | Button | `.pfprofile` export and import |
| `BrowseStarterProfilesCommand` | Button | Opens `StarterProfilesDialog` (#256) |
| `BrowseCommunityConfigsCommand` | Button | Opens `WorkshopBrowseDialog` (#9) |
| `DeleteProfileCommand` | Button | Delete selected profile |

### Profile Item Bindings

| Binding | Description |
|---------|-------------|
| `Name` | Profile name (SemiBold) |
| `IsDefault` | Marks the built-in Default profile. Blocks Edit and Delete |
| `Executables` | Comma-separated exe list backing the card. `HasExecutables` gates the auto-switch hint |
| `FirstExecutableName` / `SecondExecutableName` / `ExtraExecutablesSuffix` | The card renders at most two exe names plus a "+N more" suffix, each collapsed via `StringToVisibility` |
| `XboxCount` / `PlayStationCount` / `ExtendedCount` / `MidiCount` / `KbmCount` / `NintendoCount` / `VrCount` | Per-type counts (badge collapsed when 0) |
| `HasNoSlots` | Shows "No slots" badge when all seven type counts are zero |

### Controller Shortcuts Card

Added below the profile management card. Provides per-shortcut combo recording and mode selection.

```
CardBorder (Margin="0,20,0,0")
  └─ StackPanel
      ├─ Icon E71B + "Shortcuts" title + description
      ├─ ItemsControl (ItemsSource="{Binding ProfileShortcuts}")
      │   └─ ItemTemplate (Grid, 5 columns):
      │       ├─ Col 0: Mode ComboBox (SwitchModes: Next / Previous / Specific /
      │       │    ToggleWindow / ToggleVCsDisabled, Width=290)
      │       ├─ Col 1: Profile ComboBox (ProfileChoices, Specific only, Width=140,
      │       │    collapsed otherwise)
      │       ├─ Col 2: Device ComboBox (DeviceChoices, Width=290)
      │       ├─ Col 3: ButtonComboDisplay TextBlock (fills remaining, marquee-enabled)
      │       └─ Col 4: Action buttons (Learn/Clear/Delete)
      │           ├─ Learn: Click="ShortcutLearn_Click", icon toggles Record/Stop
      │           ├─ Clear: Command="{Binding ClearCommand}", icon E75C
      │           └─ Delete: Command="{Binding DeleteCommand}", icon E74D
      └─ "Add Shortcut" Button (Click="AddShortcut_Click")
```

### Event Handlers (Code-Behind)

| Handler | Trigger | Action |
|---------|---------|--------|
| `ProfileList_MouseDoubleClick` | ListBox.MouseDoubleClick | Executes `LoadProfileCommand` |
| `ProfileList_DragEnter` / `DragOver` / `DragLeave` / `Drop` | Drop-zone Grid | Accepts a dropped `.pfprofile` file for import and drives the `ProfileDropOverlay` cue |
| `ShortcutLearn_Click` | Learn button Click | Starts 5-second combo recording for the row's `ProfileShortcutViewModel` |
| `ProfileChoices_DropDownOpened` / `DeviceChoices_DropDownOpened` | ComboBox.DropDownOpened | Rebuilds the shortcut row's profile and device lists on open |
| `AddShortcut_Click` | "Add Shortcut" button Click | Creates a new `GlobalMacroData`, wraps in `ProfileShortcutViewModel`, adds to list |

### Shortcut Recording State (Code-Behind)

| Field | Type | Description |
|-------|------|-------------|
| `_recordingShortcut` | `ProfileShortcutViewModel` | Currently recording shortcut, or `null` |
| `_recordTimer` | `DispatcherTimer` (33 ms) | Fires `RecordTimer_Tick` during recording |
| `_lastRecordedEntries` | `TriggerButtonEntry[]` | Entries captured so far (saved on stop) |
| `_recordAxisBaselines` | `Dictionary<Guid, int[]>` | Per-device axis snapshots at record start. Deflections exceeding `AxisRecordDeltaThreshold` (0.25) register as axis triggers |
| `RecordTimeoutSeconds` | `const double` (5) | Auto-stop timeout |

---

## ProfileSwitchOverlay

**Files:** `ProfileSwitchOverlay.xaml`, `ProfileSwitchOverlay.xaml.cs`

Win11 volume OSD–style flyout that appears above the taskbar during profile switches. Shows the profile name, then transitions through initializing/active/offline states.

### Window Properties

Non-activating, topmost, transparent-background overlay:
- `WindowStyle="None"`, `AllowsTransparency="True"`, `Topmost="True"`
- `ShowInTaskbar="False"`, `ShowActivated="False"`, `Focusable="False"`
- `WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW` applied via `SetWindowLong` in `OnLoaded`
- `WM_MOUSEACTIVATE` intercepted to return `MA_NOACTIVATE`. Clicks pass through

### Layout Structure

```
Grid (ClipToBounds="True")           ← clips slide animation at taskbar edge
  └─ Grid x:Name="FlyoutPanel" (Margin="10,10,10,14")
      ├─ ShadowBorder (CornerRadius=8, DropShadowEffect BlurRadius=15)
      └─ ContentBorder (CornerRadius=8, Background=#2D2E2E, Border=#141516)
          └─ Grid (Margin="16,13,16,13")
              └─ StackPanel (Horizontal)
                  ├─ StatusIcon (Segoe Fluent Icons, 16px)
                  └─ StatusText (Segoe UI Variable Text, 14px)
```

All color values pixel-measured from the native Win11 volume OSD at 2560x1600 / 150% DPI. Dark and light themes applied dynamically via `ApplyTheme()` using `ApplicationThemeManager.GetAppTheme()`.

### Slide Animation

`FlyoutPanel.RenderTransform` is a `TranslateTransform`. The outer `Grid` uses `ClipToBounds="True"` to hide the panel while it slides:

| Method | Direction | Duration | Easing |
|--------|-----------|----------|--------|
| `SlideIn()` | Y: 80 → 0 | 300 ms | CubicEase (EaseOut) |
| `SlideOut(Action onCompleted)` | Y: 0 → 80 | 250 ms | CubicEase (EaseIn) |

`SlideIn()` snaps `_slideTransform.Y = SlideTravel` (80) synchronously, then defers the animation to `DispatcherPriority.Loaded` so WPF does not coalesce start and end values into a single frame.

### State Machine

The overlay progresses through up to four phases after `ShowProfileName(name)` is called:

```
Profile Name (2s) → Initializing (polling) → Active (2s) → Offline (2s) → Hide
                                                         └─→ Hide (if no offline)
```

| Phase | Icon | Text | Timer |
|-------|------|------|-------|
| **Profile** | `\uE8F1` (people) | Profile name | `_dismissTimer` 2 s → start init monitor |
| **Initializing** | `\uE895` (sync) | "Initializing" | `_initMonitorTimer` 33 ms polling `CheckInitState` |
| **Active** | `\uE73E` (checkmark, accent color) | "Forging" | `_dismissTimer` 2 s → check offline |
| **Offline** | `\uE7BA` (warning, #FFB900 amber) | "One or more controllers offline" | `_dismissTimer` 2 s → slide out + hide |

During the Initializing phase, `StatusIcon` plays a `DoubleAnimation` opacity flash (1.0 → 0.3, 600 ms, `AutoReverse`, `RepeatBehavior.Forever`).

### Public API

| Method / Property | Description |
|-------------------|-------------|
| `CheckInitState` | `Func<(bool anyInitializing, bool allReady)>`. Set by `InputService` |
| `CheckAnyOffline` | `Func<bool>`. Set by `InputService` |
| `ShowProfileName(string name)` | Resets state, shows profile name, starts the state machine |
| `ShowVCsToggle(bool enabled)` | One-shot toast for the master virtual-controller toggle, outside the profile state machine. Checkmark `\uE73E` in Fluent success green `#37C852` when enabled, cancel `\uE7E8` in Fluent critical red `#E81B1C` when disabled, then a 2 s dismiss. Called from `InputService.ShowVCsToggleOverlay` |
| `StopTimers()` | Stops both `_dismissTimer` and `_initMonitorTimer`. Called during shutdown |

### Positioning

`ShowFlyout()` centers the window horizontally within `SystemParameters.WorkArea` and positions the bottom edge at `WorkArea.Bottom`. The 14 px bottom margin on `FlyoutPanel` provides the gap above the taskbar.

---

## AboutPage

**Files:** `AboutPage.xaml`, `AboutPage.xaml.cs`

Application identity, description, technologies, and license.

### Layout Structure

```
ScrollViewer (Padding="24,0")
  └─ StackPanel (Margin="0,16,0,16")
      ├─ Page header (E946 info icon + title)
      ├─ App identity card (centered, 24px padding)
      │   ├─ PadForge-icon.png (120px)
      │   ├─ "PadForge" (28px, Bold, Display face)
      │   ├─ Subtitle (14px)
      │   └─ Tagline (12px)
      ├─ "Testimony" section header (E734 icon)
      ├─ Testimony card (Scripture + doxology, italic)
      ├─ "Overview" section header (E7C3 icon)
      ├─ Description card (wrapping text, line height 22)
      ├─ "Built With" section header (E74C checkmark icon)
      ├─ Technologies card (Grid, 164px label + description, 62 rows):
      │   ├─ .NET 10
      │   ├─ SDL3
      │   ├─ Raw Input
      │   ├─ HIDMaestro
      │   ├─ OpenXInput
      │   ├─ HidHide
      │   ├─ MIDI Services
      │   ├─ HelixToolkit
      │   ├─ WPF UI
      │   ├─ MVVM Toolkit
      │   └─ ...52 more open-source attributions ($Q / GestureSign recognizers, Concentus, NAudio, BouncyCastle, BthPS3, DsHidMini, libusb, SDL_GameControllerDB, JoyShockMapper, SteamKit2, protobuf-net, ZstdSharp, Hitboxer, Dolphin, DS4Windows, WiimoteLib, and others)
      ├─ "License" section header (E8D7 icon)
      └─ License card (12px wrapping text, secondary brush)
```

The 4.4.0 cycle added ten rows at the tail, `Grid.Row` 52 through 61: Interhaptics (Wyvrn), Valve Steam Controller CAD, the MinGW-w64 runtime, TritonLib and Steam Controller haptics research, Colore, the Logitech LED SDK references, opentrack, Lenovo Legion Toolkit, InputPlumber, and linuxmotehook / WiimoteHook.

### Code-Behind

Constructor only. All text from localized string bindings.

---

## Dialog Windows

### CopyFromDialog

**Files:** `CopyFromDialog.xaml`, `CopyFromDialog.xaml.cs`

Modal dialog to copy from another slot (`FluentWindow`, 420x420). Lists one entry per other slot whose mapping table has rows (`InputService.SlotHasAnyMapping` or the donor `PadSetting.HasAnyMapping`), plus one entry per unmapped device that still carries a `PadSetting` with mappings. The target slot itself is skipped. The chosen slot's mapping table is applied wholesale to the target, and every assigned device's per-device tuning carries along through `InputService.BuildPerDeviceSettingsSnapshot` + `ApplyPerDeviceSettingsToSlot`, matched by `InstanceGuid` (perfect round-trip) or `ProductGuid` (same model, different unit).

### ProfileDialog

**Files:** `ProfileDialog.xaml`, `ProfileDialog.xaml.cs`

Modal dialog to create/edit profiles (`FluentWindow`, 500x470). Fields: profile name, executable list (comma-separated).

### StarterProfilesDialog

**Files:** `StarterProfilesDialog.xaml`, `StarterProfilesDialog.xaml.cs`

The bundled starter-profile browser (#256). `FluentWindow` (700x620, min 560x480) opened from the Profiles page "Browse Starters" button. Picking a starter materializes it as a new profile.

### RegisterNfcTagDialog

**Files:** `RegisterNfcTagDialog.xaml`, `RegisterNfcTagDialog.xaml.cs`

Capture-and-name flow for NFC tags (#150). The class extends `Wpf.Ui.Controls.FluentWindow` (`ExtendsContentIntoTitleBar`, `WindowBackdropType="Mica"`, 520x520). Opened from the Devices page for an NFC reader. Tapping a tag captures its UID, the user names it, and it is added to `NfcTagRegistry`, which surfaces it as a bindable named button on the NFC device. The dialog also lists registered tags with a Remove action.

While open, the dialog subscribes to two capture paths: `NfcReaderService.TagDetected` (from `NfcReaderService.Active`) for a standalone reader, and `NfcTagRegistry.ControllerTagDetected` for a controller-borne reader, with `NfcTagRegistry.RegistrationCaptureActive` raised for the dialog's lifetime. `OnTagDetected` fires on the reader's monitor thread and marshals to the UI thread via `Dispatcher.BeginInvoke` before normalizing the UID and enabling `RegisterBtn`. `RegisterButton_Click` calls `NfcTagRegistry.Register(uid, name)`, then refreshes the list. Both subscriptions are torn down on `Closed`.

| Element | Binding / Handler | Purpose |
|---------|-------------------|---------|
| `StatusText` | localized status strings | Tap prompt, captured, or no-reader message |
| `UidText` | captured UID (Consolas) | Live UID readout |
| `NameBox` | `NameBox_KeyDown` | Tag name entry. Enter registers |
| `RegisterBtn` | `RegisterButton_Click` | Registers the captured tag |
| `TagListBox` | `NfcTagRegistry.Tags` | Registered tags with per-row Remove (`RemoveButton_Click`) |

### LearnHandheldButtonDialog

**Files:** `LearnHandheldButtonDialog.xaml`, `LearnHandheldButtonDialog.xaml.cs`

Learner for a handheld PC's hidden buttons (#343), sharing the NFC dialog's head chrome. `FluentWindow` (`ExtendsContentIntoTitleBar`, `WindowBackdropType="Mica"`, 560x640, `ResizeMode="NoResize"`) opened from the Devices page `LearnHandheldButton_Click`.

A learn run is a three-phase timed pass driven by `_phaseTimer` over `HandheldLearnSession`: Idle (the noise floor), Press, then Release, each phase lasting the session's own `IdleMs` / `PressMs` / `ReleaseMs`. `FinishLearn` reads the candidates and the chord keys the session collected, and the user names the winner and registers it. There is no per-model table: the machine teaches the app what its buttons are.

| Element | Binding / Handler | Purpose |
|---------|-------------------|---------|
| `MachineText` / `DaemonText` | code-behind | The detected handheld and the vendor-daemon notice |
| `StartBtn` | `StartButton_Click` | Begins the three-phase pass. Disabled when the row has been retired mid-dialog |
| `StatusText` | phase strings | Which phase is running, or why none can |
| `ChordText` / `CandidateBox` | learn results | The chord the press produced, and the candidate list when the pass finds more than one |
| `NameBox` | `NameBox_KeyDown` | Display name. Enter registers |
| `RegisterBtn` | `RegisterButton_Click` | Adds the learned button to `HandheldButtonRegistry` |
| `ButtonListBox` / `EmptyText` | `RefreshList` | Learned buttons with per-row Remove (`RemoveButton_Click`), and the empty-state line |
| Export / Import | `ExportButton_Click` / `ImportButton_Click` | Carries a learned set between machines |

### RegisterVoicePhraseDialog

**Files:** `RegisterVoicePhraseDialog.xaml`, `RegisterVoicePhraseDialog.xaml.cs`

Voice macro management (#317), modeled on `RegisterNfcTagDialog` and sharing its head chrome. `FluentWindow` (`ExtendsContentIntoTitleBar`, `WindowBackdropType="Mica"`, 640x620, `ResizeMode="NoResize"`) opened from the Devices page `ManageVoicePhrases_Click`. Three bands: the settings row (`EnabledBox`, `ModeBox`, `ConfidenceSlider` clamped 0.5 to 0.99 with a `ConfidenceText` readout), the live `HeardText` readout prefixed with the microphone that heard the phrase, and the type-and-name registration row with a phrase list carrying per-row Remove.

There is no source picker. Phrases live on the devices that carry the microphones, and every reachable microphone runs its own session.

The dialog subscribes to the static `VoiceMacroService.PhraseHeard` event, hops to the UI thread with `Dispatcher.BeginInvoke`, and lights the matching `PhraseRow` for 1400 ms. Only a **firing** recognition lights a row: the engine maps every utterance to its nearest phrase, so lighting on any event made rows claim matches the confidence floor had already refused. The readout line still shows every attempt with its confidence. Each row owns its own `FlashTimer`, restarted per hit so overlapping recognitions extend the light instead of truncating it. `Closed` and the close button both run `Unsubscribe`, which stops every row timer and detaches the handler.

| Element | Binding / Handler | Purpose |
|---------|-------------------|---------|
| `EnabledBox` / `ModeBox` / `ConfidenceSlider` | `Setting_Changed` | Writes `VoiceMacroService.Enabled` / `ListeningMode` / `MinConfidence`, then marks settings dirty |
| `HeardText` | `VoiceMacroService.PhraseHeard` | `[source] text (confidence)`, fired or ignored |
| `PhraseBox` / `NameBox` | `PhraseBox_KeyDown` | Phrase and display name. Enter registers |
| `RegisterBtn` | `RegisterButton_Click` | `VoicePhraseRegistry.Register(phrase, name)`, then refreshes |
| `PhraseListBox` | `_rows` (`PhraseRow`) | Registered phrases with per-row Remove (`RemoveButton_Click`) |

### ConfirmDialog

**Files:** `ConfirmDialog.xaml`, `ConfirmDialog.xaml.cs`

Generic modal confirm. `FluentWindow` with the ember-tick display-face header, a message body, and OK / Cancel buttons. Used ahead of destructive actions across the app.

### ManageProfilesDialog

**Files:** `ManageProfilesDialog.xaml`, `ManageProfilesDialog.xaml.cs`

HIDMaestro profile catalog manager. `FluentWindow` (640x660). Section 1 lists imported profiles (name + id) with Import From File / Export / Delete (Delete wears the destructive chrome and confirms first). Section 2 imports a profile from a connected device.

### PairDeviceDialog

**Files:** `PairDeviceDialog.xaml`, `PairDeviceDialog.xaml.cs`

Wii Remote pairing flow (#116). `FluentWindow` (`WiiPair_Title`) that walks the user through the Bluetooth sync-button handshake.

### PickSoundDialog

**Files:** `PickSoundDialog.xaml`, `PickSoundDialog.xaml.cs`

Sound file chooser for macro sound actions and sound packages. `FluentWindow` (460x480).

### ColorPickerControl

**Files:** `ColorPickerControl.xaml`, `ColorPickerControl.xaml.cs`

HSV color picker `UserControl`. A 200x200 saturation/value square over a hue base layer, plus a hue strip. Feeds the lightbar and RGB color rows. The hue base layer is rebuilt from code-behind on hue change.

### ShiftActivatorDialog

**Files:** `ShiftActivatorDialog.xaml`, `ShiftActivatorDialog.xaml.cs`

Shift-layer editor (`Pad_Shift_DialogTitle`, 600x760). Records the activator combo and configures the layer, including RGB color rows cloned from the Lighting tab's chrome.

### ShiftLayerFlyout

**Files:** `ShiftLayerFlyout.xaml`, `ShiftLayerFlyout.xaml.cs`

Win11 volume-OSD-style flyout that reuses `ProfileSwitchOverlay`'s pixel-measured chrome (bg `#2D2E2E`, border `#141516`, corner radius 8, layered shadow border plus content border so ClearType survives). Stays visible while a shift layer is engaged on the currently-viewed slot, slides out when the slot returns to Base.

### TouchpadGestureRecorderDialog

**Files:** `TouchpadGestureRecorderDialog.xaml`, `TouchpadGestureRecorderDialog.xaml.cs`

Touchpad gesture recorder (#88). `FluentWindow` (640x660) that captures a stroke and saves it as a named gesture template. Inherits theme from `Application.Resources` (no local `ThemesDictionary`) so it tracks the user's light/dark choice.

### TouchpadOverlay

**Files:** `TouchpadOverlay.xaml`, `TouchpadOverlay.xaml.cs`

Transparent, topmost `Window` that mirrors the touchpad surface with live finger dots and a fixed 32px click bar in the bottom row. Repositionable via the surface drag region, stylus press-and-hold / feedback suppressed.

### MenuOverlayWindow

**Files:** `MenuOverlayWindow.xaml`, `MenuOverlayWindow.xaml.cs`

On-screen radial / touch menu HUD (#9). A click-through, never-activated `Window` (`WindowStyle="None"`, `AllowsTransparency`, `Topmost`, `ShowInTaskbar="False"`, `ShowActivated="False"`, `SizeToContent="WidthAndHeight"`) following the ShiftLayerFlyout precedent: `WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TRANSPARENT` applied on Loaded, plus a `WndProc` hook answering `WM_MOUSEACTIVATE` with `MA_NOACTIVATE`, so it never steals focus from the game and never eats a click.

Owned by `InputService`, which pulls `InputManager.ActiveMenuOverlay` on the ~30 Hz UI timer (created lazily on first engage, hidden when no menu is engaged or the Dashboard's `EnableMenuOverlay` is off) and calls `UpdateFromSnapshot`. Content is built in code on a bare `Canvas`: annular wedge `Path` geometries for radial rings (a single slot renders as the full donut), rounded `Rectangle` cells for grids. Geometry rebuilds only when the menu identity or its `GeometrySig` (kind, cell count, center, labels, scale, position, opacity, name, item labels) changes. The per-tick work is the hover restyle: the hovered cell fills with `SystemAccentColorPrimaryBrush` when resolvable, ember orange otherwise. `MaxRenderCells` (64) caps the visual build. A hand-hacked config past that still hovers and commits, the window just refuses to build an unbounded visual. The window is centered at the menu's `PosXPercent` / `PosYPercent` on the primary work area (50/50 = centered), clamped fully on screen. Theme-aware through dark / light brush pairs re-applied on every rebuild.

### RemoteLinkPairDialog

**Files:** `RemoteLinkPairDialog.xaml`, `RemoteLinkPairDialog.xaml.cs`

Remote Link consent screen (#138). `FluentWindow` (460 wide) that shows the short authentication string (`SasText`, compared out of band against the peer screen), the peer `IdentityText`, a consent-warning `InfoBar`, and a `GamepadOnlyCheck` checkbox. Pair accepts. Reject, or closing the window, declines.

### RemoteLinkPasswordDialog

**Files:** `RemoteLinkPasswordDialog.xaml`, `RemoteLinkPasswordDialog.xaml.cs`

Remote Link password prompt (#138). `FluentWindow` (440 wide) with two `PasswordBox` fields (entry + confirm) and an error `InfoBar`. OK submits, Enter in either box submits too.

### WorkshopBrowseDialog

**Files:** `WorkshopBrowseDialog.xaml`, `WorkshopBrowseDialog.xaml.cs`

The Steam Workshop config browser (#9). `FluentWindow` (Mica, 1280x760, min 1080x640) with a three-state flow: cold-forge opt-in panel, game-search shelf, game room (config cards plus the translation manifest pane). Search debounces 500 ms. Preset chips re-run the translation live. Art crossfades 240 ms through steel and honors the Windows animation setting. On Save it hands the materialized profile to MainWindow's `AddWorkshopProfile` import sink. The config card's pad art is `WorkshopControllerPreview` (`Views/WorkshopControllerPreview.xaml`), a `UserControl` wrapping a `Viewbox` over a code-built `Canvas` so callouts stay in the art's own pixel space, which is what `ControllerOverlayLayout`'s coordinates are expressed in. Full anatomy on [Steam Workshop Config Import Internals](steam-workshop-import-internals.md).

---

## Value Converters

All converters in `PadForge.App/Converter/` (`PadForge.Converters` namespace). All but one are registered as `StaticResource` in `App.xaml` (lines 1044-1062). `UppercaseConverter` (key `UpperConverter`) is registered in `ControllerIcons.xaml` instead.

| Converter | Key | Input | Output | Description |
|-----------|-----|-------|--------|-------------|
| `DzShapeNameConverter` | `DzShapeNameConverter` | `int` (shape index) | `string` | Deadzone shape index to localized display name for the Sticks header subtitle. |
| `EqBandTypeNameConverter` | `EqBandTypeNameConverter` | `EqBandType` | `string` | Localized EQ band-type name for the Audio tab band picker. Defaults to Peak, the enum's zero (#347). |
| `BoolToVisibilityConverter` | `BoolToVisibilityConverter` | `bool` | `Visibility` | `true` = Visible, `false` = Collapsed. Parameter `"Invert"` reverses. Supports `ConvertBack`. |
| `HexToBrushConverter` | `HexToBrushConverter` | `string` (ARGB/RGB hex) | `SolidColorBrush` | Parses `#FF8E44AD` / `#8E44AD` to a brush. Empty/invalid falls back to muted gray `#555555` (frozen). Used by the shift-layer tab colored dots. |
| `NormToCanvasConverter` | `NormToCanvasConverter` | `double` (0-1) | `double` | Canvas position, dot-centered. Parameter: `"canvasDim"` or `"canvasDim,dotSize"` (default dot 14). |
| `SignedNormToCanvasConverter` | `SignedNormToCanvasConverter` | `double` (-1..+1) | `double` | Signed canvas position: -1 = left/top edge, 0 = center, +1 = right/bottom. For the Constant Force grid. |
| `PercentToSizeConverter` | `PercentToSizeConverter` | `int`/`double` (0-100) | `double` | Percentage to pixel size. Parameter = max (sign preserved for offsets). For the deadzone ring. |
| `CrossGeometryConverter` | `CrossGeometryConverter` | `MultiBinding(DeadZoneX, DeadZoneY)` | `Geometry` | Cross-shaped path for the axial deadzone overlay. |
| `SlopedWedgeGeometryConverter` | `SlopedWedgeGeometryConverter` | `MultiBinding(DeadZoneX, DeadZoneY)` | `Geometry` | Triangular wedge paths for the sloped deadzone overlay. |
| `NullToCollapsedConverter` | `NullToCollapsedConverter` | `object` | `Visibility` | Non-null = Visible, null = Collapsed. |
| `StringToVisibilityConverter` | `StringToVisibility` | `string` | `Visibility` | Non-null/non-empty = Visible, else Collapsed. |
| `EnumIndexConverter` | `EnumIndexConverter` | `enum` | `int` | Bridges an enum property and `ComboBox.SelectedIndex` (enum values assumed sequential 0..N). Supports `ConvertBack`. |
| `EnumEqualityVisibilityConverter` | `EnumEqualityVisibilityConverter` | `enum` | `Visibility` | Visible when the enum name matches the parameter (case-insensitive, pipe-separated list allowed). Switches per-mode UI sections. |
| `BoolToTriggerShapeKindConverter` | `BoolToTriggerShapeKindConverter` | `bool` (IconRightSide) | `LabeledShapeKind` | `false` = TriggerLeft, `true` = TriggerRight. |
| `RgbToBrushConverter` | `RgbToBrushConverter` | `MultiBinding(R, G, B)` bytes | `SolidColorBrush` | Lightbar preview swatch on the Lighting tab. Falls back to black. |
| `IndexToLetterConverter` | `IndexToLetterConverter` | `int` (0-25) | `string` | 0..25 maps to `a`..`z`. Index >= 26 falls back to `s[N]`. Macro formula chips. |
| `IndexLessThanVisibilityConverter` | `IndexLessThanVisibilityConverter` | `int` (count), param `int` (index) | `Visibility` | Visible when `param < count`. Reveals a per-letter formula chip when its index is within the variable count. |
| `OneBasedIndexConverter` | `OneBasedIndexConverter` | `int` (0-based) | `string` | Renders a 0-based index as its 1-based number. Touchpad-tab pad selector. |
| `ExeIconConverter` | `ExeIconConverter` | `string` (exe path) | `ImageSource` | Extracts the exe's shell icon for profile cards (cached per path, frozen). Returns null when the path is empty/missing. |
| `UppercaseConverter` | `UpperConverter` | `string` | `string` | Uppercases header strings for the ember eyebrow treatment. Registered in `ControllerIcons.xaml`, not `App.xaml`. |

---

## Resource Dictionaries and Theming

### App.xaml Resources

The #175 ember restyle grew `App.xaml` well past the old two-dictionary shell. Merged dictionaries (in order):

```xml
<Application.Resources>
    <ResourceDictionary>
        <ResourceDictionary.MergedDictionaries>
            <ui:ThemesDictionary Theme="Dark"/>     <!-- WPF UI theme, design-time default -->
            <ui:ControlsDictionary/>                <!-- WPF UI control styles -->
            <ResourceDictionary>                    <!-- font families (#175 typography) -->
                <FontFamily x:Key="TelemetryFontFamily">Cascadia Code, Consolas, Segoe UI</FontFamily>
                <FontFamily x:Key="BodyFontFamily">Segoe UI Variable Text, Segoe UI</FontFamily>
                <FontFamily x:Key="DisplayFontFamily">Segoe UI Variable Display, Segoe UI</FontFamily>
            </ResourceDictionary>
            <ResourceDictionary Source="/Resources/ControllerIcons.xaml"/>
            <ResourceDictionary>                    <!-- ember identity tokens (#175) -->
                <!-- Ember*/Cold*/Steel* brushes, WaitBrush, EmberSegGradient,
                     FlameOuterGeometry, LivenessFlameBase, MiniTypeButton styles -->
            </ResourceDictionary>
        </ResourceDictionary.MergedDictionaries>

        <!-- App-level styles (all in the root dictionary): -->
        <!-- implicit ComboBox / Button / CheckBox / TextBox / uictrl:TextBox /
             ToolTip / uictrl:FluentWindow / uictrl:DynamicScrollBar restyles -->
        <!-- keyed: EmberIconButton(+Hot), EmberAccentButton, EmberPrimaryButton,
             EmberDestructiveButton, EmberSelectListItem, EmberSlider,
             InstrumentBarRaw / InstrumentBarOut, EmberFocusVisual, EntranceFade -->
        <!-- 19 global converter registrations (lines 1044-1062) -->
    </ResourceDictionary>
</Application.Resources>
```

Ember identity tokens (`ColdBrush`, `EmberBrush`, `SteelGroundBrush`, `CrucibleCardBrush`, and their relatives) carry the #175 color language: cold = the physical side (devices, sources, telemetry), ember = the virtual side (outputs, anything live), steel = the ground the two sit on. Green/gold/red stay health-only (`WaitBrush` is the only sanctioned gold). `EmberThemeProbe` / `EmberTheme.ApplyAccent` swap the theme-scoped pairs on a light/dark flip.

Theme is applied at runtime via `Wpf.Ui.Appearance.ApplicationThemeManager.Apply(...)` (Light / Dark) or `ApplySystemTheme()`. The `Theme="Dark"` attribute on `ThemesDictionary` is the design-time default.

**App-level control styles (#175):**

| Key (or implicit target) | What it does |
|--------------------------|--------------|
| implicit `ComboBox` / `Button` / `CheckBox` / `TextBox` / `uictrl:TextBox` | 30-32px grid metrics, ember text selection, faint neutral hover glow |
| implicit `ToolTip` / `uictrl:FluentWindow` | Body font, left-aligned tooltip text, dialog font inheritance |
| implicit `uictrl:DynamicScrollBar` | Always-visible track + thumb (stock template fades them in on hover) |
| `EmberIconButton` / `EmberIconButtonHot` | 28x28 icon micro-buttons, cold ring for input actions, ember ring for output-writing actions |
| `EmberAccentButton` / `EmberPrimaryButton` | Ember rim + text affirmative verb (plain `Button` / `uictrl:Button`) |
| `EmberDestructiveButton` | Ember-deep rim + text for destructive confirms |
| `EmberSelectListItem` | Retemplated `ListBoxItem`: ember-tint wash + `#66FF6B2C` rim on select |
| `EmberSlider` | Retemplated single-thumb slider with an ember decrease-side fill |
| `InstrumentBarRaw` / `InstrumentBarOut` | RAW (cold-deep flat) / OUT (ember gradient + glow) telemetry `ProgressBar` retemplates |
| `EmberFocusVisual` (+ `DefaultControlFocusVisualStyle`, `FocusVisualStyleKey`) | Ember keyboard-focus ring app-wide |
| `EntranceFade` | 150ms fade + 6px settle on `Loaded` for page/card roots |

### ControllerIcons.xaml

**File:** `PadForge.App/Resources/ControllerIcons.xaml`

**DrawingImage icons** (sidebar, dashboard, profiles):

| Key | Source | Description |
|-----|--------|-------------|
| `XboxControllerIcon` | svgrepo.com (32x32) | Xbox logo icon |
| `DS4ControllerIcon` | svgrepo.com (32x32) | PlayStation logo icon |
| `NintendoControllerIcon` | Switch logo (32x32 box) | Nintendo family icon |
| `ExtendedControllerIcon` | svgrepo.com, viewBox -4 -2 24 24 | Joystick icon |
| `GenericControllerIcon` | svgrepo.com (512x512, scaled) | Generic gamepad with D-pad and face buttons |
| `KeyboardMouseControllerIcon` | placeholder path | Placeholder so resource lookup succeeds. KB+M actually renders via an MDL2 glyph in code-behind. There is no `MidiControllerIcon`. MIDI uses the `E8D6` MDL2 glyph directly. |

Fills use `DynamicResource TextFillColorPrimaryBrush`. The `GenericControllerIcon` cutouts (D-pad, face buttons) use `SolidBackgroundFillColorSecondaryBrush`.

**Hover-glow effects** (frozen `DropShadowEffect`, shared by every hover trigger and code-behind site): `EmberHoverGlow`, `EmberHoverGlowSmall`, `ColdHoverGlow`, `NeutralHoverGlow`. Static Effect setters only, never animated (Effect animation from style triggers crashes at startup).

**PadPage tab-icon geometries** (Sticks/Triggers tab headers, derived from Zacksly Xbox Series icons, CC BY 3.0): `ZackslyStickOuterRingGeometry`, `ZackslyStickInnerDiscGeometry`, `ZackslyTriggerOuterBodyGeometry`, `ZackslyTriggerOuterBodyRightGeometry`, plus `TouchpadStickIconGeometry` (Segoe Fluent Icons F108 silhouette).

**Shared card and section styles:**

| Key | TargetType | Properties |
|-----|------------|------------|
| `CardBorder` | `Border` | `CardBackgroundFillColorDefaultBrush` background, 8px corner radius, 16px padding, 12px bottom margin, 1px `#253049` stroke that heats to steel-lift on hover (theme-scoped via `EmberThemeProbe`) |
| `CardTitle` | `TextBlock` | 15px Display face, SemiBold |
| `CardSectionTitle` | `TextBlock` | `CardTitle` + 8px bottom margin (divider-separated section title inside a card) |
| `CardSubsectionTitle` | `TextBlock` | SemiBold at body size, 6px bottom margin (one rank below `CardTitle`) |
| `CardDescription` | `TextBlock` | 12px Body face, `TextFillColorSecondaryBrush`, wrap enabled, 8px bottom margin |
| `SectionGlyph` | `TextBlock` | Ember MDL2 glyph, 13px, for page section headers |
| `SectionTitle` | `TextBlock` | 10px Telemetry mono eyebrow, SemiBold, tertiary |
| `ChipCold` / `ChipEmber` / `ChipGhost` | `Border` | Artifact chips: cold = physical fact, ember = virtual fact, ghost = neutral |

### Theme Switching

`SettingsViewModel.SelectedThemeIndex` maps to:
- 0 = System Default (follows Windows setting)
- 1 = Light
- 2 = Dark

Applied via `Wpf.Ui.Appearance.ApplicationThemeManager.Apply(ApplicationTheme.Light|Dark)` or `ApplySystemTheme()` in `OnThemeChanged`. Code subscribes to `ApplicationThemeManager.Changed` to rebuild theme-aware brush caches in the visualization views (KBM, MIDI, Mouse, schematic).

### Ember Identity Brushes

Defined inline in the App.xaml ember-tokens dictionary. Values below are the dark defaults. `EmberTheme.ApplyAccent` swaps the theme-paired ones on a light/dark flip.

| Brush Key | Color | Usage |
|-----------|-------|-------|
| `EmberBrush` / `EmberHotBrush` / `EmberDeepBrush` | `#FF6B2C` / `#FFA24D` / `#C43D0C` | Virtual side: outputs, live state, accent verbs |
| `ColdBrush` / `ColdDeepBrush` / `ColdMutedBrush` | `#58B6E4` / `#2E6A8F` / `#9E58B6E4` | Physical side: devices, sources, telemetry |
| `SteelGroundBrush` / `SteelRaisedBrush` / `SteelLineBrush` / `SteelLineSoftBrush` | `#0B0E14` / `#1B2333` / `#253049` / `#1C2536` | Ground, raised, hairline, soft hairline |
| `CrucibleCardBrush` | `#111623` gradient | Slot-card ground. `EmberTheme` swaps it per theme, and light falls back to the card fill. There is no `SteelCardBrush` key |
| `EmberTintBrush` / `ColdTintBrush` | `#1AFF6B2C` / `#1A58B6E4` | Checked-tab and chip washes |
| `EmberTextBrush` | `#FF6B2C` | Raw-ember text that deepens on white. Theme-paired |
| `WaitBrush` | `#E8B434` | The only sanctioned gold: cooling flames, awaiting-devices |

The `RangeSliderThumbFill` brush from the v3 layout no longer exists.

---

## Common XAML Patterns

### Card-Based Layout

Settings and driver pages use this card pattern:

```xml
<Border Style="{StaticResource CardBorder}">
    <StackPanel>
        <StackPanel Orientation="Horizontal" Margin="0,0,0,4">
            <TextBlock Text="&#xE790;" FontFamily="Segoe MDL2 Assets" FontSize="16"
                       VerticalAlignment="Center" Margin="0,0,8,0"/>
            <TextBlock Text="Card Title" Style="{StaticResource CardTitle}"/>
        </StackPanel>
        <TextBlock Text="Description text." Style="{StaticResource CardDescription}"/>
        <!-- Card content -->
    </StackPanel>
</Border>
```

### Liveness Flame Indicator

Online/offline state renders as a flame `Path`, not a colored dot. The `LivenessFlameBase` style (App.xaml) draws an outline-only flame at rest. Each site adds one `DataTrigger` on `IsOnline` that fills it ember with a glow:

```xml
<Path>
    <Path.Style>
        <Style TargetType="Path" BasedOn="{StaticResource LivenessFlameBase}">
            <Style.Triggers>
                <DataTrigger Binding="{Binding IsOnline}" Value="True">
                    <Setter Property="Fill" Value="{DynamicResource EmberBrush}"/>
                    <Setter Property="Stroke" Value="{x:Null}"/>
                    <Setter Property="Effect">
                        <Setter.Value>
                            <DropShadowEffect Color="#FF6B2C" BlurRadius="8" ShadowDepth="0" Opacity="0.5"/>
                        </Setter.Value>
                    </Setter>
                </DataTrigger>
            </Style.Triggers>
        </Style>
    </Path.Style>
</Path>
```

The engine-state indicator in the status bar uses the same flame with DataTriggers on `EngineStateKey` instead (ember when Running, gold when Idle/Stopping).

### Segoe MDL2 Asset Icons

`Segoe MDL2 Assets` font glyphs instead of image resources:

```xml
<TextBlock Text="&#xE713;" FontFamily="Segoe MDL2 Assets" FontSize="20"/>
```

Codes used: `E713` settings, `E790` personalization, `E9F5` processing, `E737` star, `ED1A` shield, `E7FC` gamepad, `E8A5` save, `E9D9` bug, `E8F1` group, `E8B7` library, `E8B9` photo, `F158` 3D, `E946` info, `E772` devices, `E7E8` power, `E740` full screen, `E710` add, `E711` close, `E72A` forward, `E72C` undo, `E700` global nav (hamburger), `E8D6` music, `EC4F` MIDI, `E961` keyboard, `E774` globe, `EDA4` touchpad, `F119` VR headset, `F2B7` language, `E8C8` copy, `E8D7` document, `E7C3` page, `E74C` checkmark, `E71B` link, `E75C` clear, `E74D` delete, `F404` home, `E7BA` warning, and the section and card glyphs named on this page: `E702` Pair, `E707` Compass Yaw, `E716` Community Configs, `E767` volume, `E77B` Head Tracking, `E781` Lightbar Mirrors, `E7F8` Handheld PC Buttons, `E815` Grip, `E83F` Battery Alerts, `E877` Sensa haptics and the rumble chip, `E8DE` Assignment Prompts, `E969` Remote Link, `E99A` Tilt, `E9E9` Gyro Sensitivity, `EB9F` Icon Packages, `EFA5` touchpad chip, `F0AD` Constant Force, `F1CB` Gyro Response, `F272` Gyro Calibration. `EC05` (broadcast) and `ED5D` (driver) left with the Dashboard's driver status strip and appear nowhere in the app.

### WPF UI NumberBox

Numeric input with inline spin buttons:

```xml
<ui:NumberBox Value="{Binding PollingRateMs, Mode=TwoWay}"
              Minimum="1" Maximum="16"
              SpinButtonPlacementMode="Inline" Width="120"/>
```

### Localized String Bindings

All user-facing text uses localized bindings via `Strings.Instance`:

```xml
<TextBlock Text="{Binding Settings_Title, Source={x:Static strings:Strings.Instance}}"/>
```

Enables runtime language switching without restart.

### MarqueeBehavior for Overflow Text

Long text (device names, GUIDs, paths) uses `MarqueeBehavior.IsEnabled="True"` inside a `ClipToBounds="True"` `Border` for scrolling overflow.

---

## Code-Behind Patterns

### Bind/Unbind Pattern

All six visualization views (3D, 2D, Schematic, MIDI, KBM, VR) share this interface:

```csharp
public void Bind(PadViewModel vm)    // Subscribe to PropertyChanged, hook rendering, load model
public void Unbind()                 // Stop flash, unhook rendering, clear VM reference
```

Lets PadPage switch views cleanly when output type or preference changes.

### CompositionTarget.Rendering with Dirty Flag

Per-frame visual updates via `CompositionTarget.Rendering`, gated by a `_dirty` flag:

```csharp
private bool _dirty;

private void OnRendering(object sender, EventArgs e)
{
    if (!_dirty || _vm == null) return;
    _dirty = false;
    // Update visuals...
}

private void OnVmPropertyChanged(object sender, PropertyChangedEventArgs e)
{
    _dirty = true;  // Coalesce multiple property changes into one render frame
}
```

Batches multiple property changes into one visual update per frame, avoiding redundant work.

### DispatcherTimer Flash Animation

"Map All" recording flow across all views:

```csharp
private DispatcherTimer _flashTimer;
private string _flashTarget;
private bool _flashOn;

private void UpdateFlashTarget(string target)
{
    // Start or stop flash timer based on target
    // Timer callback toggles highlight/default materials at 400ms interval
}
```

### Event Relay Pattern

Code-behind raises events that MainWindow.xaml.cs wires to services, keeping views decoupled:

```csharp
// DashboardPage.xaml.cs
public event EventHandler<int> DeleteSlotRequested;
private void DeleteSlot_Click(object sender, RoutedEventArgs e)
{
    if (sender is Button btn && btn.Tag is int slotIndex)
        DeleteSlotRequested?.Invoke(this, slotIndex);
}

// MainWindow.xaml.cs (wiring)
DashboardPageView.DeleteSlotRequested += (s, idx) => DeleteSlot(idx);
```

### Syncing Guard Pattern

Prevents recursive updates when programmatically setting control values:

```csharp
private bool _syncingExtendedConfig;

private void SyncExtendedConfigBar()
{
    if (DataContext is not PadViewModel vm) return;

    bool isExtended = vm.OutputType == Engine.VirtualControllerType.Extended;

    HMaestroProfileBar.Visibility = (vm.HasHMaestroProfileBar && !isExtended)
        ? Visibility.Visible
        : Visibility.Collapsed;
    ExtendedConfigBar.Visibility = isExtended ? Visibility.Visible : Visibility.Collapsed;

    if (isExtended)
    {
        _syncingExtendedConfig = true;
        SyncExtendedFields(vm);  // populates profile combo + Customize-gated overrides
        _syncingExtendedConfig = false;
    }
}

private void CustomizeToggle_Changed(object sender, RoutedEventArgs e)
{
    if (_syncingExtendedConfig) return;  // Skip when syncing programmatically
    // ... handle user-initiated change ...
}
```

---

## See Also

- [Architecture Overview](architecture-overview.md): Application shell, page hosting, WPF UI theme
- [ViewModels](viewmodels.md): `PadViewModel`, `DashboardViewModel`, `DevicesViewModel`, `SettingsViewModel`
- [Services Layer](services-layer.md): `InputService`, `SettingsService`, `DeviceService` wired in `MainWindow.xaml.cs`
- [2D Overlay System](2d-overlay-system.md): `ControllerModel2DView`, `ControllerSchematicView`, `KBMPreviewView`, `MidiPreviewView`, `VRPreviewView`
- [3D Model System](3d-model-system.md): `ControllerModelView` (HelixToolkit 3D viewport)
- [Settings and Serialization](settings-and-serialization.md): `PadSetting` descriptors driving mapping grid UI
- [Virtual Controllers](../features/virtual-controllers.md): Output type selection UI for Xbox, PlayStation, Nintendo, Extended, KB+M, MIDI, VR (all HM-backed types are produced by `HMaestroVirtualController`, VR by `HMaestroVRController`). The Add Controller popup builds a Nintendo button (Switch logo, AutomationId `AddNintendoBtn`, capacity via `MaxNintendoSlots`) between PlayStation and Extended, and a VR button (`F119` glyph, AutomationId `AddVrBtn`, capacity via `MaxVrSlots` = 1) at the tail, the `VirtualControllerGroups.InOrder` visual order.
- [Driver Installation Internals](driver-installation-internals.md): HidHide and Windows MIDI Services install/uninstall triggered from `SettingsPage` (HIDMaestro is embedded. OpenXInput is unpacked next to `PadForge.exe` from the single-file bundle)

---

*Last updated for PadForge 4.4.0.*
