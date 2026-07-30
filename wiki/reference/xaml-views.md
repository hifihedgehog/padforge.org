# XAML Views Reference

*The main window shell, the page hierarchy, the dialog windows, custom controls, value converters, and how themes switch at runtime.*

> **v4 (2026-07-12):** Updated for the v4 ember restyle (#175). The HIDMaestro SDK surface, OpenXInput shim, thread-pool lifecycle, and bubble-up cascade live on [HIDMaestro Deep Dive](hidmaestro-deep-dive.md). If anything here drifts from the live source, the live source wins.

---

All views live in `PadForge.App/Views/` (`PadForge.Views` namespace), except `MainWindow.xaml` in `PadForge.App/`. Styled with [WPF UI 4.2 (Lepo.Wpf.Ui)](https://github.com/lepoco/wpfui) for Fluent 2 design.

## Contents

- [Application Shell (MainWindow)](#application-shell-mainwindow)
- [DashboardPage](#dashboardpage)
- [PadPage](#padpage)
- [DevicesPage](#devicespage)
- [KBMPreviewView](#kbmpreviewview)
- [MidiPreviewView](#midipreviewview)
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
- Power/type glyph plus a mini type segment: Xbox / PlayStation / Nintendo / Extended / KB+M / MIDI tiles in `VirtualControllerGroups.InOrder`, active type lit, plus a fixed-width "#N" instance token
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

`Popup` with one button per output type, built in `ShowControllerTypePopup`. The six buttons follow `VirtualControllerGroups.InOrder`:

| Button | AutomationId | Icon | Per-type cap |
|--------|--------------|------|--------------|
| Xbox | `AddXbox360Btn` | Xbox SVG | `SettingsManager.MaxXbox360Slots` |
| PlayStation | `AddDS4Btn` | DS4 SVG | `SettingsManager.MaxPlayStationSlots` |
| Nintendo | `AddNintendoBtn` | Switch logo SVG | `SettingsManager.MaxNintendoSlots` |
| Extended | `AddRawBtn` | Joystick SVG | `SettingsManager.MaxExtendedSlots` |
| Keyboard+Mouse | `AddKeyboardMouseBtn` | `E961` glyph | `SettingsManager.MaxKeyboardMouseSlots` |
| MIDI | `AddMidiBtn` | `E8D6` glyph | `SettingsManager.MaxMidiSlots` |

The method counts each type from `Pads[].OutputType` and disables a button (opacity 0.35, "(max N)" tooltip, e.g. `Main_Nintendo_Max_Format` = "Nintendo (max {0})") when the global slot total reaches 16 or that type hits its own per-type cap. MIDI additionally requires Windows MIDI Services. `HasAnyControllerTypeCapacity()` is a separate check: it tallies created slots from `SettingsManager.SlotCreated` and returns true while the total stays under 16 (`MaxPads`). The same six types repeat, in the same order, in the sidebar card's type segment and on the dashboard slot cards.

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
| `ShutdownOverlay` | 1001 | App is closing | `ProgressRing` + "Shutting down" text |
| `StartupOverlay` | 1001 | Orphan-sweep task (`App.OrphanSweepTask`) still running at launch | `ProgressRing` + "Cleaning previous session" text, auto-hidden on completion |

### Composition Root (Code-Behind)

`MainWindow.xaml.cs` is the service wiring hub (~6784 lines). Constructor:

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
| `_driverStatusTimer` | 5s | Polls HidHide and Windows MIDI Services status for hot-plug detection. HIDMaestro is embedded so it has no install/uninstall poll |
| `CompositionTarget.Rendering` | ~60fps | Used by all visualization views (3D, 2D, Schematic, MIDI, KBM, MousePreview) for per-frame visual updates |

---

## DashboardPage

**Files:** `DashboardPage.xaml`, `DashboardPage.xaml.cs`

Engine toggle, slot summary cards, DSU/Web settings, and driver status.

### Layout Structure

```
ScrollViewer (Padding="24,0")
  └─ StackPanel (Margin="0,16,0,16")
       ├─ Page header (icon + title)
       ├─ "Input Engine" section header
       ├─ CardBorder: Engine status card (Grid, 4 columns)
       │   ├─ Col 0: Engine toggle flame `Path` (FlameOuterGeometry, ember when Running, gold when Idle/Stopping, else outline)
       │   ├─ Col 1: EngineStatus text
       │   ├─ Col 2: PollingFrequencyText
       │   └─ Col 3: Online/Total devices count
       ├─ "Virtual Controllers" section header
       ├─ ItemsControl (WrapPanel) → SlotSummaries
       │   └─ DataTemplate: slot card Border (252px wide)
       │       ├─ Row 0: Power btn + Gamepad icon + Slot # + Type buttons (Xbox / PlayStation / Nintendo / Extended / KB+M / MIDI) + Instance label
       │       ├─ Row 1: DeviceName (marquee overflow)
       │       └─ Row 2: StatusText + mapped/connected counts
       ├─ "Add Controller" card (MouseLeftButtonUp → AddControllerRequested)
       ├─ "Services" divider (ServicesHeader, ember tick + hairline rule)
       ├─ "Motion Server" section (DSU)
       │   └─ CardBorder: Enable toggle, port NumberBox, status dot, footer
       ├─ "Web Controller" section
       │   └─ CardBorder: Enable toggle, port NumberBox, status dot, footer
       ├─ "Remote Link" section (#138)
       │   └─ CardBorder: Enable toggle (EnableRemoteLinkCheckBox), auto-reconnect toggle,
       │      port NumberBox + reset, status dot + RemoteLinkStatus text,
       │      identity-protection mode ComboBox, Paired PCs list (rename / connect / revoke
       │      per peer, Revoke All), nearby-unpaired list, connect-by-address box, footer
       ├─ "Overlays" section
       │   └─ CardBorder: Menu Overlay (EnableMenuOverlay), Shift Layer Flyout
       │      (EnableShiftLayerFlyout), Profile Overlay (EnableProfileOverlay) toggles
       ├─ "Touchpad Overlay" section
       │   └─ CardBorder: Enable toggle (EnableTouchpadOverlay), opacity slider,
       │      reset-position button
       └─ "Drivers" section
           └─ CardBorder (Grid, 2 rows × 2 cols)
               ├─ Row 0: HidHide status
               └─ Row 1: MIDI Services status
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
| `WebControllerPort` | `DashboardViewModel` | Web controller port |
| `EnableRemoteLink` / `RemoteLinkPort` / `RemoteLinkConnectHost` | `DashboardViewModel` | Remote Link enable, port, and connect-by-address host (#138) |
| `IsRemoteLinkRunning` / `RemoteLinkStatus` | `DashboardViewModel` | Remote Link status dot and text |
| `RemoteLink` | `DashboardViewModel` | Sub-ViewModel: identity-protection modes, trusted peers, nearby-unpaired list, revoke commands |
| `EnableMenuOverlay` / `EnableShiftLayerFlyout` / `EnableProfileOverlay` | `DashboardViewModel` | Overlays-section toggles |
| `EnableTouchpadOverlay` | `DashboardViewModel` | Touchpad overlay enable |
| `HidHideStatusText` / `MidiServicesStatusText` | `DashboardViewModel` | Driver status text shown on the Dashboard. HIDMaestro is embedded, with status shown on the Settings page only |

### Slot Card DataTemplate Bindings (SlotSummary)

| Binding | Type | Description |
|---------|------|-------------|
| `PadIndex` | `int` | Used as `Tag` for button click routing |
| `SlotNumber` | `string` | Global slot display number |
| `IsEnabled` | `bool` | Controls power toggle color |
| `OutputType` | `VirtualControllerType` | Selects which type button is highlighted (Opacity 1.0 vs 0.3) |
| `TypeInstanceLabel` | `string` | Per-type instance number |
| `DeviceName` | `string` | Physical device name (marquee on overflow) |
| `StatusText` | `string` | e.g. "Active", "Disabled" |
| `MappedDeviceCount` / `ConnectedDeviceCount` | `int` | Mapped/connected counts |
| `IsInitializing` | `bool` | Triggers green opacity flash animation |

### Power Toggle State Machine

The slot power toggle is a flame `Path` (`FlameOuterGeometry`), not a glyph. It keys off `HasMappedDevices` and `IsVirtualControllerConnected`, not a raw device count. Enabled with no mapped devices stays the cold outline (heat needs fuel). There is no HIDMaestro-install state, since the driver is embedded.

| Condition | Flame fill | Tooltip |
|-----------|-----------|---------|
| `IsEnabled=False` | Cold outline (`TextFillColorTertiaryBrush`) | "Disabled" |
| `IsEnabled=True`, no mapped devices | Cold outline | "Active" |
| `IsEnabled=True` + `HasMappedDevices=True` | `EmberBrush` + glow | "Active" |
| above + `IsVirtualControllerConnected=False` | `WaitBrush` gold | "Awaiting Controllers" |
| above + `EngineStateKey="Stopped"` | `WaitBrush` gold | "Engine Stopped" |
| `IsInitializing=True` | `EmberBrush` (flashing) | "Initializing" |

### Type Switch Buttons

5 type buttons per slot card (Xbox, PlayStation, Extended, KB+M, MIDI) using a custom `TypeSwitchButton` style. Dark gray rounded background on hover, transparent border. Active type at Opacity 1.0, inactive at 0.3. Unavailable types (missing prerequisite, e.g. MIDI without Windows MIDI Services) show `Cursor.No` and a tooltip explaining the requirement. Clicks are guarded in code-behind. The power button also uses the `TypeSwitchButton` style for visual consistency.

### UI Automation

| AutomationId | Element | Purpose |
|--------------|---------|---------|
| `EnableWebControllerCheckBox` | CheckBox | Web controller enable toggle |

### Event Handlers (Code-Behind)

| Handler | Event | Action |
|---------|-------|--------|
| `EngineToggle_Click` | Button.Click | Raises `EngineToggleRequested` |
| `AddControllerCard_Click` | Border.MouseLeftButtonUp | Raises `AddControllerRequested` |
| `DeleteSlot_Click` | Button.Click | Raises `DeleteSlotRequested(slotIndex)` |
| `PowerToggle_Click` | Button.Click | Raises `SlotEnabledToggled(slotIndex, !IsEnabled)` |
| `XboxType_Click` | Button.Click | Raises `SlotTypeChangeRequested(slotIndex, Xbox)`. HIDMaestro is embedded so no install gate |
| `DS4Type_Click` | Button.Click | Raises `SlotTypeChangeRequested(slotIndex, PlayStation)` |
| `ExtendedType_Click` | Button.Click | Raises `SlotTypeChangeRequested(slotIndex, Extended)` |
| `KeyboardMouseType_Click` | Button.Click | Raises `SlotTypeChangeRequested(slotIndex, KeyboardMouse)` |
| `MidiType_Click` | Button.Click | Raises `SlotTypeChangeRequested(slotIndex, Midi)` |
| `SlotCard_Loaded` | Border.Loaded | Wires `PreviewMouseLeftButtonDown` for drag start |
| `OnCardMouseDown` | PreviewMouseLeftButtonDown | Records drag start position. Skips if inside a Button |
| `OnDragMove` | PreviewMouseMove | Begins/updates card drag with ghost adorner |
| `OnDragEnd` | PreviewMouseLeftButtonUp | Completes swap/insert or fires `SlotCardClicked` for navigation |
| `OnDragKeyDown` | PreviewKeyDown | Cancels drag on Escape |

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

Per-slot configuration: two-tier tab strip, optional config bars, and 17 tab panels (Tags 0-16). Tier 1 (slot scope) holds Preview, Mappings, Macros, Menus, and Bass Shakers. Tier 2 (device scope) holds the device selector and the capability tabs, most gated on source-device capability.

### Layout Structure

```
Grid (3 rows)
├─ Row 0 (Auto): Two-tier tab strip (StackPanel of two gradient-bordered Borders)
│   ├─ Tier 1 (slot scope, ember underline): slot tabs pushed right (TabStripButton, GroupName="PadTab")
│   │   ├─ RadioButton "Preview" (Tag=0, x:Name="TabController", AutomationId="TabController")
│   │   ├─ RadioButton "Mappings" (Tag=2, AutomationId="MappingsTab")
│   │   ├─ RadioButton "Macros" (Tag=1, AutomationId="MacrosTab")
│   │   └─ RadioButton "Menus" (Tag=15, AutomationId="MenusTab", #9)
│   └─ Tier 2 (device scope, cold underline): scope label + device ComboBox on the left,
│      capability tabs pushed right in a WrapPanel (TabStripButtonCold, GroupName="PadTabDevice")
│       ├─ ComboBox (MappedDevices; item = LivenessFlame Path + Name + battery)
│       ├─ RadioButton "Sticks" (Tag=3, x:Name="TabSticks")
│       ├─ RadioButton "Triggers" (Tag=4, x:Name="TabTriggers")
│       ├─ RadioButton "Force Feedback" (Tag=5, x:Name="TabForceFeedback", gated on hasForceFeedback)
│       ├─ RadioButton "Adaptive Triggers" (Tag=6, x:Name="TabAdaptiveTriggers", gated on hasAdaptiveTriggers)
│       ├─ RadioButton "Lighting" (Tag=7, x:Name="TabLighting", gated on hasLightbar || hasGuideLed)
│       ├─ RadioButton "Gyro" (Tag=8, x:Name="TabGyro", gated on hasGyro)
│       ├─ RadioButton "Impulse Triggers" (Tag=9, x:Name="TabImpulseTriggers", gated on hasRumbleTriggers)
│       ├─ RadioButton "Touchpad" (Tag=10, x:Name="TabTouchpad", gated on hasTouchpad)
│       ├─ RadioButton "Wheel" (Tag=11, x:Name="TabWheel", gated on wheel VID/PID)
│       ├─ RadioButton "Audio" (Tag=12, x:Name="TabAudio", gated on hasAudio)
│       ├─ RadioButton "Pointer" (Tag=13, x:Name="TabPointer", gated on hasIrPointer, #146)
│       └─ RadioButton "Mouse" (Tag=14, x:Name="TabMouse", gated on mouse device, #200)
├─ Row 1 (Auto): Extended config bar OR MIDI config bar (conditionally visible)
│   ├─ ExtendedConfigBar (Visibility=Collapsed unless OutputType==Extended)
│   └─ MidiConfigBar (Visibility=Collapsed unless OutputType==Midi)
├─ Invisible MappingsCountIndicator (for UI Automation)
└─ Row 2 (*): TabControl (hidden header via ControlTemplate), one TabItem per Tag (0-15),
   SelectedIndex bound to SelectedConfigTab
```

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

Two `RadioButton` groups. The slot tier (Preview / Mappings / Macros / Menus) uses `TabStripButton` with `GroupName="PadTab"`. The device tier (Sticks through Mouse) uses `TabStripButtonCold` with `GroupName="PadTabDevice"`. The two groups are independent so WPF never auto-unchecks across tiers. `SyncTabStripSelection()` keeps exactly one tab checked overall (#175 item 18: only the tier owning the active tab shows a highlight). Its slot-tier test is `selected <= 2 || selected == 15`, since Menus (Tag 15) is the appended TabItem's index rather than a tier-2 tag. Each button stores its Tag (0-15) and sets `vm.SelectedConfigTab = Tag` on click via `TabBtn_Click`.

A `TabControl` with hidden header (custom `ControlTemplate` showing only `PART_SelectedContentHost`) provides content switching. `SelectedIndex` is bound to `SelectedConfigTab`.

### Tab Visibility Rules

Tabs hidden by output type and by source-device capability:

| Tab | Xbox / PlayStation / Extended | KB+Mouse | MIDI | Capability gate |
|-----|------------------------------------|----------|------|---|
| Preview | Visible | Visible | Visible | always |
| Macros | Visible | Visible | Visible | always |
| Mappings | Visible | Visible | Visible | always |
| Menus | Visible | Visible | Visible | always (slot scope, #9) |
| Sticks | Visible | Visible (Mouse X/Y + Scroll) | **Hidden** | always within Xbox/PS/Extended |
| Triggers | Visible | **Hidden** | **Hidden** | always within Xbox/PS/Extended |
| Force Feedback | Visible if `hasForceFeedback` | **Hidden** | **Hidden** | selected device's CapType is stick-class (Gamepad / Joystick / Driving / Flight / FirstPerson). Hidden for keyboard / mouse / touchpad / MIDI even on an Xbox/PS/Extended slot |
| Impulse Triggers | Visible if `hasImpulseTriggers` | **Hidden** | **Hidden** | source device has impulse-trigger motors (Xbox One / One S / Elite / Elite Series 2 / Series X\|S, Microsoft VID). Xbox 360 and DualSense excluded |
| Adaptive Triggers | Visible if `hasAdaptiveTriggers` | **Hidden** | **Hidden** | source device is a DualSense or DualSense Edge |
| Lighting | Visible if `hasLightbar \|\| hasGuideLed` | **Hidden** | **Hidden** | a lightbar (DS4 / DualSense family) shows the lightbar cards. A Guide/HOME-button LED shows only the `GuideLedCard`: XInput/GIP Xbox pad over USB or the 2015 Steam Controller (#209), plus the Switch home-LED population (#226: Pro Controller, right Joy-Con, Joy-Con pair, charging grip) |
| Gyro | Visible if `hasGyro` | **Hidden** | **Hidden** | source device has a gyro sensor |
| Pointer | Visible if `hasIrPointer` | **Hidden** | **Hidden** | source device is an IR-capable Wii Remote (#146) |
| Touchpad | Visible if `hasTouchpad` | **Hidden** | **Hidden** | source device has a touchpad (DualSense family, DS4, Steam Controller) |
| Wheel | Visible if `hasWheel \|\| hasGenericWheel` | **Hidden** | **Hidden** | source device is a force-feedback wheel |
| Audio | Visible if `hasAudio` | **Hidden** | **Hidden** | source has a speaker (DualSense / DS4 / Wii Remote) or plays HD haptic tones (Joy-Con, Switch Pro, Steam Controller / Deck, SC 2026) (#147) |
| Mouse | Visible if source is a mouse | **Hidden** | **Hidden** | source device is a mouse (per-device mouse-gesture settings, #200) |

Tag numbers: Preview 0, Macros 1, Mappings 2, Sticks 3, Triggers 4, Force Feedback 5, Adaptive Triggers 6, Lighting 7, Gyro 8, Impulse Triggers 9, Touchpad 10, Wheel 11, Audio 12, Pointer 13, Mouse 14, Menus 15, Bass Shakers 16. Bass Shakers (4.1.0, #236, AutomationId `BassShakersTab`) is slot-tier and gates on SLOT TYPE, not device capability: visible via `RumbleAudioTabVisible` for Xbox, PlayStation, and Nintendo slots plus Extended slots with a force-feedback surface. The Audio tab was speaker-only before 3.6.0. It now shows for any haptic-tone pad as well. The Lighting tab used to be lightbar-only. It now also raises for a device with only a Guide/HOME-button LED (#209, and since #226 the Switch home-LED devices: Pro Controller, right Joy-Con, Joy-Con pair, charging grip): the lightbar cards (`LightbarModeCard`, `LightingLightbarSubtitle`, `LightingPlayerIdleHint`) collapse and the `GuideLedCard` brightness control takes their place.

If the selected tab is hidden, the view auto-switches to Preview (index 0). `SyncTabVisibility()` toggles the device-tier capability tabs from the selected device's capabilities, and also drives the motor activity bars (`MotorBarsGrid`).

### Preview Tab Type Icon

The Preview tab (Tag 0, `x:Name="TabController"`, header text `Pad_Tab_Preview`) shows a dynamic type icon via nested DataTriggers on `OutputType`:
- `Xbox` → `XboxControllerIcon` (Image)
- `PlayStation` → `DS4ControllerIcon` (Image)
- `Extended` → `ExtendedControllerIcon` (Image)
- `Midi` → `E8D6` glyph (music note, TextBlock, Image collapsed)
- `KeyboardMouse` → `E961` glyph (keyboard, TextBlock, Image collapsed)

The DrawingImage resource keys (`XboxControllerIcon`, `DS4ControllerIcon`) keep the v2 short names. One icon represents the whole family regardless of which specific HM profile (Xbox 360 / Xbox One / Series / Elite / Adaptive, or DS4 / DualSense / DualSense Edge) the slot ends up running. `TypeInstanceLabel` shows the per-type instance number (e.g., "2" for the second Xbox slot).

### Multi-Device Selector

Inline `ComboBox` bound to `MappedDevices` / `SelectedMappedDevice`. Each item shows a `LivenessFlame` `Path` (fills ember with a glow when `IsOnline`, outline-only stroke when offline), device `Name` in cold, and its battery percentage when the device reports one (#167). Sits in tier 2 (device scope) on the left, beside the "Device" scope label, ahead of the right-pushed capability tabs.

### UI Automation Properties

| AutomationId | Element | Purpose |
|--------------|---------|---------|
| `TabController` | RadioButton (tab 0) | Preview tab identification. x:Name kept from v2/v3, header text is now "Preview" |
| `MappingsTab` | RadioButton (tab 2) | Mappings tab identification |
| `HMaestroProfileCombo` | ComboBox | HIDMaestro profile selection for Xbox / PlayStation slots. Extended has its own `ExtendedProfileCombo` |
| `ExtendedStickCountBox` | TextBox | Extended slot thumbstick count override |
| `ExtendedTriggerCountBox` | TextBox | Extended slot trigger count override |
| `ExtendedPovCountBox` | TextBox | Extended slot POV count override |
| `ExtendedButtonCountBox` | TextBox | Extended slot button count override |
| `MappingsCountIndicator` | TextBlock (invisible) | `AutomationProperties.Name` bound to `Mappings.Count` |
| `DeadZoneShapeCombo` | ComboBox | Deadzone shape selector (Sticks tab) |
| `SensitivityXCombo` | ComboBox | Sensitivity X preset (Sticks tab) |
| `TriggerPresetCombo` | ComboBox | Trigger sensitivity preset (Triggers tab) |

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
| Extended | Custom HID layout |. | ControllerSchematicView | No |
| Extended | Xbox / DS4 catalog | 2D | ControllerModel2DView | Yes |
| Extended | Xbox / DS4 catalog | 3D | ControllerModelView | Yes |
| Xbox |. | 2D | ControllerModel2DView | Yes |
| Xbox |. | 3D | ControllerModelView | Yes |
| PlayStation |. | 2D | ControllerModel2DView | Yes |
| PlayStation |. | 3D | ControllerModelView | Yes |

**`BindActiveModelView()`**: Unbinds all five views, subscribes the active view's `ControllerElementRecordRequested` event, then calls `Bind(vm)`. All views fire `ControllerElementRecordRequested` with a PadSetting target name for click-to-record.

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
        ├─ Trigger Mode ComboBox (OnPress/OnRelease/WhileHeld/Always/CustomExpression)
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
                ├─ Action Type ComboBox (33 types)
                └─ Type-specific panels (conditional visibility):
```

**Macro Trigger Section:**

| Field | Binding | Visibility |
|-------|---------|------------|
| Fire mode dropdown | `TriggerMode` (SelectedValue) | Always |
| Trigger source | `TriggerSource` | Hidden in Always mode (`IsNotAlwaysMode`) |
| Trigger display | `TriggerDisplayText` / `RecordingLiveText` | Hidden in Always mode |
| Record button | `RecordTriggerCommand` / `RecordTriggerButtonText` | Hidden in Always mode |
| Axis threshold | `TriggerAxisThreshold` (Slider 1-100%) | `UsesAxisTrigger` |
| Axis direction | `TriggerAxisDirectionIndex` (Any/Positive/Negative) | `UsesAxisTrigger` |
| Consume trigger | `ConsumeTriggerButtons` (CheckBox) | Hidden in Always mode |

**Action Type Editor Panels:**

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
          └─ Grid (2 columns)
              ├─ Col 0 (*): Controls
              │   ├─ Range: RangeSlider (dual-thumb, DeadZone/MaxRange 0-100%)
              │   │   + two TextBox edits (dz.max) + two digit edits + reset
              │   ├─ Anti-Deadzone (DzSlider 0-100% + % edit + digit edit + reset)
              │   ├─ "Sensitivity Curve" header + hint text
              │   ├─ Preset ComboBox (CurvePresetNames) + reset
              │   └─ Live value bar (ProgressBar 0-1 + RawDisplay text)
              └─ Col 1 (Auto): CurveEditor (120px, IsSigned=False)
                  └─ CurveString=SensitivityCurve, DeadZone/MaxRange bindings
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
      ├─ Swap Motors CheckBox (SwapMotors)
      ├─ "Test Rumble" Button (TestRumbleCommand)
      ├─ "Motor Activity" header
      ├─ Left Motor live bar (ProgressBar 0-1, LeftMotorDisplay)
      ├─ Right Motor live bar (ProgressBar 0-1, RightMotorDisplay)
      ├─ Separator
      └─ Audio Bass Rumble section
          ├─ "Audio Rumble" header + "Reset All" button + description
          ├─ Enable CheckBox (AudioRumbleEnabled)
          ├─ Sensitivity slider (1-20, AudioRumbleSensitivity, format F1)
          ├─ Bass Cutoff slider (20-200 Hz, AudioRumbleCutoffHz, format F0)
          ├─ Left Motor slider (0-100%, AudioRumbleLeftMotor)
          ├─ Right Motor slider (0-100%, AudioRumbleRightMotor)
          └─ Level meter (ProgressBar 0-1, AudioRumbleLevelMeter)
```

All Audio Rumble controls bind `IsEnabled="{Binding AudioRumbleEnabled}"`. Grayed out when off.

### Gyro Tab (Tab 8). Engage Stick Gate (#120)

Below the Easy-Aim stick threshold, two ComboBoxes gate gyro engagement per stick and per direction. Both use `SelectedValuePath="Tag"` and reset buttons.

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
            └─ Cell Bindings ItemsControl (Cells)
                └─ per cell: Header + Label TextBox (LostFocus)
                    + Binding ComboBox (BindingKindOptions → BindingKind)
                    + key picker (KeyOptions → SelectedKeyVk, visible on ShowKeyPicker)
                    OR button picker (ButtonOptions → SelectedButtonFlag,
                       visible on ShowButtonPicker)
                    + Reset (ResetCellCommand)
```

Every setting row carries the canonical Reset button, and the host row carries Record too (the Aim Engage cluster shape). The record button binds `MenuHostRecordCommand` on the PadViewModel through the TabItem's DataContext because the editor panel's own DataContext is the selected `MenuEditorItem`.

### HIDMaestro Profile Bar

`HMaestroProfileBar` is shown for `Xbox` and `PlayStation` slots. Its visibility is `HasHMaestroProfileBar && !isExtended`. `HasHMaestroProfileBar` is true for Xbox, PlayStation, and Extended, but Extended slots hide this compact bar and use the separate `ExtendedConfigBar` (with its own `ExtendedProfileCombo`) instead. It contains the profile picker only:

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
| 4 | `ExtendedStickCountBox`, `ExtendedTriggerCountBox`, `ExtendedPovCountBox`, `ExtendedButtonCountBox`, `ExtendedTouchpadChk`, `ExtendedRumbleChk` | Layout overrides |

Override rows 3 and 4 are gated by `IsChecked={ElementName=ExtendedCustomizeChk}`, so toggling Customize off restores the catalog profile as-is. `_syncingExtendedConfig` guard prevents recursive updates inside `SyncExtendedConfigBar()`.

### MIDI Config Bar

Visible when `OutputType == Midi`. Centered horizontal `StackPanel`:

| Control | Binding | Range |
|---------|---------|-------|
| Channel TextBox | `MidiConfig.Channel` | 1-16 |
| CC Count TextBox | `MidiConfig.CcCount` | 0-127 (interdependent with StartCc) |
| Start CC TextBox | `MidiConfig.StartCc` | 0-127 |
| Note Count TextBox | `MidiConfig.NoteCount` | 0-127 (interdependent with StartNote) |
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
│   ├─ Refresh Button (RefreshCommand)
│   └─ Online/Total count display
└─ Row 1 (*): Main content (Grid, 2 columns)
    ├─ Col 0 (*): Device card ListBox
    │   └─ ListBoxItem with custom ControlTemplate (4px accent left bar on selection)
    │       └─ Card Border (CornerRadius=8, Padding="12,10")
    │           ├─ Row 0, Col 0: LivenessFlame Path + DeviceName (SemiBold, 13px)
    │           ├─ Row 0-1, Col 1: Slot badges (WrapPanel of numbered badges) or "Unassigned"
    │           ├─ Row 0-1, Col 2: Remove device Button (E711 × icon)
    │           └─ Row 1: DeviceType + VID:PID + CapabilitiesSummary
    └─ Col 1 (340px): Detail panel (Border with ScrollViewer)
        ├─ Device identity section
        │   ├─ DeviceName (16px, SemiBold, wrapping)
        │   ├─ Product name, Type, Capabilities
        │   ├─ Instance GUID (marquee overflow)
        │   ├─ Instance Path (marquee, conditional StringToVisibility)
        │   └─ VID:PID
        ├─ Submit Mapping Button (joysticks only, opens GitHub issue template)
        ├─ Separator
        ├─ VC Assignment section
        │   └─ WrapPanel of ToggleButtons (ActiveSlotItems, ToggleSlotCommand)
        ├─ Separator
        ├─ Input Mode section (gamepads only)
        │   └─ "Force raw joystick mode" CheckBox (ForceRawJoystickMode)
        ├─ Separator
        ├─ Input Hiding section
        │   ├─ "Hide from games (HidHide)" CheckBox (HidHideEnabled)
        │   └─ "Consume mapped inputs" CheckBox (ConsumeInputEnabled, ShowConsumeToggle)
        ├─ Power section (#162, wireless controllers only, ShowIdleDisconnect)
        │   └─ Idle Disconnect minutes TextBox (IdleDisconnectMinutes)
        ├─ Consumer Control named-chip preview (#168, IsConsumerDevice)
        │   └─ ItemsControl → ConsumerButtons (named button chips)
        ├─ NFC named-tag preview (#150)
        │   ├─ Register / Manage NFC Tags Button (RegisterNfcTag_Click, ShowRegisterNfcTag)
        │   └─ ItemsControl → NfcTags (registered named tags)
        ├─ Separator
        └─ Raw Input State section
            ├─ Axes (joysticks/gamepads, hidden for keyboard/mouse)
            │   └─ ItemsControl → ProgressBar per axis (0-1, name + bar + raw value)
            ├─ Buttons (joysticks/gamepads, hidden for keyboard/mouse)
            │   └─ WrapPanel of 24×24 circles, accent fill when pressed
            ├─ Keyboard layout (keyboard devices only)
            │   └─ Viewbox → Canvas (556×136) with positioned key Borders
            ├─ Mouse preview (mouse devices only)
            │   └─ Viewbox → MousePreviewControl
            ├─ D-Pad / POV hats (conditional on RawPovs.Count > 0)
            │   └─ Horizontal StackPanel of compass indicators
            │       ├─ 36×36 Ellipse background + center dot
            │       └─ Accent-colored Line with RotateTransform(AngleDegrees), hidden when IsCentered
            ├─ Gyroscope (HasGyroData, 3-column X/Y/Z grid, Consolas F3 format)
            ├─ Accelerometer (HasAccelData, same layout as gyro)
            └─ Aux Accelerometer (HasAccelAuxData, same layout, the Nunchuk sensor / combined pair's left-half accel, #199)
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

### Device Card Bindings (DeviceRowViewModel)

| Binding | Description |
|---------|-------------|
| `IsOnline` | Drives a `LivenessFlame` `Path` (fills `EmberBrush` with a glow when online, `LivenessFlameBase` outline stroke when offline). The device-name text also dims when offline. |
| `DeviceName` | Bold device name |
| `SlotBadges` | Collection of slot assignment badges |
| `IsUnassigned` | Shows "Unassigned" badge when no slots assigned |
| `DeviceType` | Type string |
| `VendorIdHex` / `ProductIdHex` | Hex VID:PID |
| `CapabilitiesSummary` | e.g. "6 axes, 11 buttons, 1 POV" |
| `BatteryGlyph` / `BatteryText` | Battery indicator (#167): Segoe MDL2 Assets glyph + "78%", hidden when `HasBattery` is false |

### Detail Panel Bindings (SelectedDevice)

| Binding | Description |
|---------|-------------|
| `DeviceName`, `ProductName`, `DeviceType` | Device identity |
| `CapabilitiesSummary` | Capabilities line |
| `InstanceGuid` | GUID (marquee) |
| `HidHideInstancePath` | Instance path (conditional visibility via `StringToVisibility`) |
| `ShowSubmitMapping` | Submit mapping button visibility (joysticks only) |
| `IsGamepad` | Controls Input Mode section visibility |
| `ForceRawJoystickMode` | Force raw toggle |
| `IsHidHideAvailable` | Enables/disables HidHide checkbox |
| `HidHideEnabled` | HidHide toggle |
| `ShowConsumeToggle` | Consume toggle visibility (mouse/keyboard devices) |
| `ConsumeInputEnabled` | Consume toggle |
| `ShowIdleDisconnect` | Power section visibility (wireless controllers, #162) |
| `IdleDisconnectMinutes` | Idle-disconnect countdown minutes |
| `ShowRegisterNfcTag` | Register/Manage NFC Tags button visibility (#150) |
| `RawAxes` | Axis ProgressBar items |
| `RawButtons` | Button circle items |
| `IsKeyboardDevice` / `IsMouseDevice` | Switches between button circles, keyboard canvas, or mouse graphic |

The NFC and Consumer previews bind to the page DataContext (`DevicesViewModel`), not to `SelectedDevice`: `IsNfcDevice` / `NfcTags` and `IsConsumerDevice` / `ConsumerButtons`. Only `ShowRegisterNfcTag`, `ShowIdleDisconnect`, and `IdleDisconnectMinutes` above are `SelectedDevice`-scoped.
| `KeyboardKeys` | QWERTY keyboard layout items |
| `RawPovs` | POV compass items |
| `HasGyroData` / `HasAccelData` / `HasAccelAuxData` | Gyro / accel / aux-accel section visibility |
| `GyroX/Y/Z` / `AccelX/Y/Z` / `AccelAuxX/Y/Z` | Motion sensor values (aux accel is #199) |

### Selection Highlighting

Custom `ListBoxItem` `ControlTemplate`:
- `SelectionBar`. 4px `Border` with accent brush on left edge, `CornerRadius="2"`.
- Toggled by `IsSelected` trigger.
- Content offset 6px right to accommodate the bar.

### Event Handlers (Code-Behind)

| Handler | Trigger | Action |
|---------|---------|--------|
| `RemoveDevice_Click` | Button.Click | Selects device, executes `RemoveDeviceCommand` |
| `HidingToggle_Changed` | CheckBox.Checked/Unchecked | Shows warning flyout for mouse/keyboard enable, clears `LastRawStateDeviceGuid` for rebuild, calls `NotifyDeviceHidingChanged` |
| `ShowHidingWarningFlyout` | (internal) | WPF UI `Flyout` with warning icon, message, Proceed/Cancel buttons. Reverts checkbox immediately, re-checks only on Proceed. |
| `SubmitMapping_Click` | Button.Click | Opens browser to GitHub issue template with device info pre-filled |
| `RegisterNfcTag_Click` | Button.Click | Opens `RegisterNfcTagDialog` for the selected NFC reader (#150) |
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

MIDI note and CC visualization for MIDI virtual controller slots, shown on the PadPage Preview tab.

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

### Layout Structure

```
ScrollViewer (Padding="24,16")
  └─ StackPanel
      ├─ Page header (E713 gear icon + title)
      ├─ Language card (CardBorder)
      │   ├─ Icon F2B7 + "Language" title + description
      │   └─ ComboBox (AvailableLanguages, DisplayMemberPath="NativeName", Width=250)
      ├─ Appearance card
      │   ├─ Icon E790 + "Appearance" title + description
      │   ├─ "Theme" label
      │   ├─ ComboBox (System Default / Light / Dark, SelectedIndex=SelectedThemeIndex)
      │   └─ "Show Tour" Button (Settings_ShowTour, ShowTour_Click) → re-runs the first-run spotlight tour
      ├─ Input Engine card
      │   ├─ Icon E9F5 + title + description
      │   ├─ Auto-start toggle (AutoStartEngine)
      │   ├─ Background polling toggle (EnablePollingOnFocusLoss)
      │   ├─ Polling interval: NumberBox 1-16ms (PollingRateMs)
      │   └─ Hide devices toggle (EnableInputHiding)
      ├─ Window card
      │   ├─ Icon E737 + title + description
      │   ├─ Minimize to tray (MinimizeToTray)
      │   ├─ Start minimized (StartMinimized)
      │   └─ Start at login (StartAtLogin)
      ├─ HidHide Driver card
      │   ├─ Icon ED1A + title + description
      │   ├─ Status: dot + HidHideStatusText + HidHideVersion
      │   ├─ Install/Uninstall buttons (visibility-toggled by IsHidHideInstalled)
      │   └─ Whitelist section (only when installed):
      │       ├─ Title + description
      │       ├─ ListBox of HidHideWhitelistPaths (Consolas, 12px)
      │       └─ Add/Remove buttons
      ├─ HIDMaestro Driver card
      │   ├─ Icon E7FC + title + description
      │   └─ Status: green dot + "Installed" + HIDMaestroVersion (no Install/Uninstall buttons; HIDMaestro is embedded in the binary)
      ├─ Windows MIDI Services card
      │   ├─ Icon E8D6 + title + description
      │   ├─ Status: dot + MidiServicesStatusText + MidiServicesVersion
      │   └─ Install/Uninstall buttons (Install disabled tooltip when IsMidiOsSupported=False)
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
          └─ Grid (140px label + value):
              ├─ App Version (ApplicationVersion)
              ├─ .NET Runtime (RuntimeVersion)
              └─ SDL Version (SdlVersion)
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
| `EnableInputHiding` | CheckBox | Master input hiding toggle |
| `MinimizeToTray` | CheckBox | Minimize to system tray |
| `StartMinimized` | CheckBox | Start app minimized |
| `StartAtLogin` | CheckBox | Start at Windows login |
| `IsHidHideInstalled` | bool | Controls status dot, button visibility, whitelist section |
| `InstallHidHideCommand` / `UninstallHidHideCommand` | ICommand | Driver install/uninstall |
| `HidHideWhitelistPaths` | Collection | Whitelist ListBox items |
| `SelectedWhitelistPath` | object | Selected whitelist item |
| `AddWhitelistPathCommand` / `RemoveWhitelistPathCommand` | ICommand | Whitelist management |
| `IsMidiServicesInstalled` / `IsMidiOsSupported` | bool | MIDI Services status. Controls Install button visibility and disabled-tooltip |
| `SaveCommand` / `ReloadCommand` / `ResetCommand` / `OpenSettingsFolderCommand` | ICommand | Settings file operations |
| `EnableCommunityConfigLookup` / `ShowLegacyWorkshopConfigs` | CheckBox | Steam Workshop opt-in + legacy sub-toggle (#9) |
| `ClearWorkshopCacheCommand` / `CheckWorkshopUpdatesCommand` | ICommand | Workshop cache clear and imported-profile update check |
| `HasUnsavedChanges` | bool | Orange warning visibility |

### Code-Behind

Constructor only. All logic in ViewModel.

---

## ProfilesPage

**Files:** `ProfilesPage.xaml`, `ProfilesPage.xaml.cs`

Per-app profile management.

### Layout Structure

```
ScrollViewer (Padding="24,16")
  └─ StackPanel
      ├─ Page header (E8F1 people icon + title)
      └─ CardBorder
          ├─ Icon E8F1 + "Management" title + description
          ├─ Auto-switch CheckBox (EnableAutoProfileSwitching)
          ├─ Active profile info (ActiveProfileInfo, SemiBold)
          ├─ Profile ListBox (MinHeight=60, MaxHeight=300)
          │   └─ ItemTemplate:
          │       ├─ Profile Name (SemiBold)
          │       ├─ Executables list (trimmed, collapsed when empty)
          │       └─ Type count badges (horizontal StackPanel):
          │           ├─ Xbox badge: Xbox SVG + XboxCount (collapsed when 0)
          │           ├─ PlayStation badge: PS SVG + PlayStationCount (collapsed when 0)
          │           ├─ Extended badge: Joystick SVG + ExtendedCount (collapsed when 0)
          │           ├─ MIDI badge: E8D6 glyph + MidiCount (collapsed when 0)
          │           ├─ KB+M badge: E961 glyph + KbmCount (collapsed when 0)
          │           └─ "No slots" fallback (visible when HasNoSlots=True)
          └─ Action buttons: New / Save As / Edit / Load / Delete
```

### Key Bindings

| Binding | Target | Description |
|---------|--------|-------------|
| `EnableAutoProfileSwitching` | CheckBox | Enables foreground app monitoring |
| `ActiveProfileInfo` | TextBlock | Current active profile name |
| `ProfileItems` | ListBox ItemsSource | Profile list |
| `SelectedProfile` | ListBox SelectedItem | Selected profile |
| `NewProfileCommand` | Button | Create new profile |
| `SaveAsProfileCommand` | Button | Save current config as profile |
| `EditProfileCommand` | Button | Edit profile name/exes |
| `LoadProfileCommand` | Button | Load selected profile |
| `DeleteProfileCommand` | Button | Delete selected profile |

### Profile Item Bindings

| Binding | Description |
|---------|-------------|
| `Name` | Profile name (SemiBold) |
| `Executables` | Comma-separated exe list (collapsed when empty via DataTrigger) |
| `XboxCount` / `PlayStationCount` / `ExtendedCount` / `MidiCount` / `KbmCount` | Per-type counts (badge collapsed when 0) |
| `HasNoSlots` | Shows "No slots" badge when all type counts are zero |

### Controller Shortcuts Card

Added below the profile management card. Provides per-shortcut combo recording and mode selection.

```
CardBorder (Margin="0,20,0,0")
  └─ StackPanel
      ├─ Icon E71B + "Shortcuts" title + description
      ├─ ItemsControl (ItemsSource="{Binding ProfileShortcuts}")
      │   └─ ItemTemplate (Grid, 5 columns):
      │       ├─ Col 0: Mode ComboBox (Next/Previous/Specific/ToggleWindow, Width=155)
      │       ├─ Col 1: Profile ComboBox (Specific only, Width=140, collapsed otherwise)
      │       ├─ Col 2: Device ComboBox (Width=220)
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
| `ShortcutLearn_Click` | Learn button Click | Starts 5-second combo recording for the row's `ProfileShortcutViewModel` |
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
| **Active** | `\uE73E` (checkmark, accent color) | "Active" | `_dismissTimer` 2 s → check offline |
| **Offline** | `\uE7BA` (warning, #FFB900 amber) | "Controllers Offline" | `_dismissTimer` 2 s → slide out + hide |

During the Initializing phase, `StatusIcon` plays a `DoubleAnimation` opacity flash (1.0 → 0.3, 600 ms, `AutoReverse`, `RepeatBehavior.Forever`).

### Public API

| Method / Property | Description |
|-------------------|-------------|
| `CheckInitState` | `Func<(bool anyInitializing, bool allReady)>`. Set by `InputService` |
| `CheckAnyOffline` | `Func<bool>`. Set by `InputService` |
| `ShowProfileName(string name)` | Resets state, shows profile name, starts the state machine |
| `StopTimers()` | Stops both `_dismissTimer` and `_initMonitorTimer`. Called during shutdown |

### Positioning

`ShowFlyout()` centers the window horizontally within `SystemParameters.WorkArea` and positions the bottom edge at `WorkArea.Bottom`. The 14 px bottom margin on `FlyoutPanel` provides the gap above the taskbar.

---

## AboutPage

**Files:** `AboutPage.xaml`, `AboutPage.xaml.cs`

Application identity, description, technologies, and license.

### Layout Structure

```
ScrollViewer (Padding="24,16")
  └─ StackPanel
      ├─ Page header (E946 info icon + title)
      ├─ App identity card (centered, 24px padding)
      │   ├─ "PadForge" (28px, Bold)
      │   ├─ Subtitle (14px)
      │   └─ Tagline (12px)
      ├─ Description card (wrapping text, line height 22)
      ├─ "Built With" section header (E74C checkmark icon)
      ├─ Technologies card (Grid, 164px label + description, 38 rows):
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
      │   └─ ...28 more open-source attributions ($Q / GestureSign recognizers, Concentus, NAudio, BouncyCastle, BthPS3, DsHidMini, libusb, SDL_GameControllerDB, JoyShockMapper, Dolphin, DS4Windows, WiimoteLib, and others)
      ├─ "License" section header (E8D7 icon)
      ├─ License card (12px wrapping text, secondary brush)
      ├─ "Testimony" section header (E734 icon)
      └─ Testimony card (Scripture + doxology, italic)
```

### Code-Behind

Constructor only. All text from localized string bindings.

---

## Dialog Windows

### CopyFromDialog

**Files:** `CopyFromDialog.xaml`, `CopyFromDialog.xaml.cs`

Modal dialog to copy from another slot. Lists every slot that has at least one assigned device. The chosen slot's mapping table is applied wholesale to the target, and every assigned device's per-device tuning carries along through `InputService.BuildPerDeviceSettingsSnapshot` + `ApplyPerDeviceSettingsToSlot`, matched by `InstanceGuid` (perfect round-trip) or `ProductGuid` (same model, different unit).

### ProfileDialog

**Files:** `ProfileDialog.xaml`, `ProfileDialog.xaml.cs`

Modal dialog to create/edit profiles. Fields: profile name, executable list (comma-separated).

### RegisterNfcTagDialog

**Files:** `RegisterNfcTagDialog.xaml`, `RegisterNfcTagDialog.xaml.cs`

Capture-and-name flow for NFC tags (#150). The class extends `Wpf.Ui.Controls.FluentWindow` (`ExtendsContentIntoTitleBar`, `WindowBackdropType="Mica"`). Opened from the Devices page for an NFC reader. Tapping a tag captures its UID, the user names it, and it is added to `NfcTagRegistry`, which surfaces it as a bindable named button on the NFC device. The dialog also lists registered tags with a Remove action.

While open, the dialog subscribes to `NfcReaderService.TagDetected` (from `NfcReaderService.Active`). `OnTagDetected` (~49) fires on the reader's monitor thread and marshals to the UI thread via `Dispatcher.BeginInvoke` before normalizing the UID and enabling `RegisterBtn`. `RegisterButton_Click` (~63) calls `NfcTagRegistry.Register(uid, name)`, then refreshes the list. The subscription is torn down on `Closed`.

| Element | Binding / Handler | Purpose |
|---------|-------------------|---------|
| `StatusText` | localized status strings | Tap prompt, captured, or no-reader message |
| `UidText` | captured UID (Consolas) | Live UID readout |
| `NameBox` | `NameBox_KeyDown` | Tag name entry. Enter registers |
| `RegisterBtn` | `RegisterButton_Click` | Registers the captured tag |
| `TagListBox` | `NfcTagRegistry.Tags` | Registered tags with per-row Remove (`RemoveButton_Click`) |

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

The Steam Workshop config browser (#9). `FluentWindow` (Mica, 1280x760, min 1080x640) with a three-state flow: cold-forge opt-in panel, game-search shelf, game room (config cards plus the translation manifest pane). Search debounces 500 ms. Preset chips re-run the translation live. Art crossfades 240 ms through steel and honors the Windows animation setting. On Save it hands the materialized profile to MainWindow's `AddWorkshopProfile` import sink. Full anatomy on [Steam Workshop Config Import Internals](steam-workshop-import-internals.md).

---

## Value Converters

All converters in `PadForge.App/Converter/` (`PadForge.Converters` namespace). All but one are registered as `StaticResource` in `App.xaml` (lines 760-777). `UppercaseConverter` (key `UpperConverter`) is registered in `ControllerIcons.xaml` instead.

| Converter | Key | Input | Output | Description |
|-----------|-----|-------|--------|-------------|
| `DzShapeNameConverter` | `DzShapeNameConverter` | `int` (shape index) | `string` | Deadzone shape index to localized display name for the Sticks header subtitle. |
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
        <!-- 18 global converter registrations (lines 760-777) -->
    </ResourceDictionary>
</Application.Resources>
```

Ember identity tokens (`ColdBrush`, `EmberBrush`, `SteelGroundBrush`, and their relatives) carry the #175 color language: cold = the physical side (devices, sources, telemetry), ember = the virtual side (outputs, anything live), steel = the ground the two sit on. Green/gold/red stay health-only (`WaitBrush` is the only sanctioned gold). `EmberThemeProbe` / `EmberTheme.ApplyAccent` swap the theme-scoped pairs on a light/dark flip.

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
| `ExtendedControllerIcon` | svgrepo.com (24x24) | Joystick icon |
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
| `SteelGroundBrush` / `SteelCardBrush` / `SteelRaisedBrush` / `SteelLineBrush` | `#0B0E14` / `#111623` / `#1B2333` / `#253049` | Ground, card, raised, hairline |
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

Codes used: `E713` settings, `E790` personalization, `E9F5` processing, `E737` star, `ED1A` shield, `E7FC` gamepad, `E8A5` save, `E9D9` bug, `E8F1` group, `E8B9` photo, `F158` 3D, `E946` info, `E772` devices, `E7E8` power, `E740` full screen, `E710` add, `E711` close, `E72C` undo, `E700` global nav (hamburger), `E8D6` music, `E961` keyboard, `EC05` broadcast, `E774` globe, `ED5D` driver, `F2B7` language, `E8D7` document, `E74C` checkmark, `F404` home, `E7BA` warning.

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

All five visualization views (3D, 2D, Schematic, MIDI, KBM) share this interface:

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
- [2D Overlay System](2d-overlay-system.md): `ControllerModel2DView`, `ControllerSchematicView`, `KBMPreviewView`, `MidiPreviewView`
- [3D Model System](3d-model-system.md): `ControllerModelView` (HelixToolkit 3D viewport)
- [Settings and Serialization](settings-and-serialization.md): `PadSetting` descriptors driving mapping grid UI
- [Virtual Controllers](../features/virtual-controllers.md): Output type selection UI for Xbox, PlayStation, Nintendo, Extended, MIDI, KB+M (all HM-backed types are produced by `HMaestroVirtualController`). The Add Controller popup builds a Nintendo button (Switch logo, AutomationId `AddNintendoBtn`, capacity via `MaxNintendoSlots`) between PlayStation and Extended, the `VirtualControllerGroups.InOrder` visual order.
- [Driver Installation Internals](driver-installation-internals.md): HidHide and Windows MIDI Services install/uninstall triggered from `SettingsPage` (HIDMaestro is embedded. OpenXInput is unpacked next to `PadForge.exe` from the single-file bundle)

---

*Last updated for PadForge 4.1.0.*
