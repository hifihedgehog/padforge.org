# XAML Views Reference

*The main window shell, the pages and their sections, the dialog windows, custom controls, value converters, and how themes switch at runtime.*

> **PadForge 6:** This page describes the interface PadForge 6 rebuilt in place (#574): the sidebar, Home, the controller page's six sections, Extras, Devices, Profiles, Settings, About and the dialogs. The HIDMaestro SDK surface, the OpenXInput shim, the thread-pool lifecycle and the bubble-up cascade are on [HIDMaestro Deep Dive](hidmaestro-deep-dive.md). Where this page and the source disagree, the source is right.

---

All views live in `PadForge.App/Views/` (`PadForge.Views` namespace), except `MainWindow.xaml` in `PadForge.App/`. Shared controls are in `PadForge.App/Controls/` and `PadForge.App/Views/Controls/` (see [Custom Controls](#custom-controls)), shared styles in `App.xaml` and `PadForge.App/Resources/` (see [Resource Dictionaries and Theming](#resource-dictionaries-and-theming)). The window and its controls are built on [WPF UI 4.3 (Lepo.Wpf.Ui)](https://github.com/lepoco/wpfui).

## Contents

- [Application Shell (MainWindow)](#application-shell-mainwindow)
- [HomePage](#homepage)
- [PadPage](#padpage)
- [ExtrasPage](#extraspage)
- [DevicesPage](#devicespage)
- [KBMPreviewView](#kbmpreviewview)
- [MidiPreviewView](#midipreviewview)
- [VRPreviewView](#vrpreviewview)
- [MousePreviewControl](#mousepreviewcontrol)
- [SettingsPage](#settingspage)
- [ProfilesPage](#profilespage)
- [ProfileSwitchOverlay](#profileswitchoverlay)
- [AboutPage](#aboutpage)
- [SearchPanel](#searchpanel)
- [Dialog Windows](#dialog-windows)
- [Custom Controls](#custom-controls)
- [Value Converters](#value-converters)
- [Resource Dictionaries and Theming](#resource-dictionaries-and-theming)
- [Common XAML Patterns](#common-xaml-patterns)
- [Code-Behind Patterns](#code-behind-patterns)

---

## Application Shell (MainWindow)

**Files:** `MainWindow.xaml`, `MainWindow.xaml.cs`, and the partial files `MainWindow.BlissBox.cs`, `MainWindow.Falcon.cs`, `MainWindow.FlydigiScreen.cs` and `MainWindow.KeyboardScreens.cs`. The sidebar and title bar templates and their line icons are in `Resources/Shell.xaml`.

The window is a `ui:FluentWindow` (`ExtendsContentIntoTitleBar="True"`, `WindowBackdropType="Mica"`, 1100 by 720, at least 900 by 600) in the body face at 13 (`BodyFontFamily`). It holds a title bar, the sidebar with the page area beside it, and four full-window overlays. There is no status bar. A message shows on a line over the page area's lower corner, and the engine's state, the live count and the polling rate stand in the engine block at the sidebar's foot.

### XAML Structure

A two-row `Grid`:

```
Grid
├─ SteelLayer (Grid.RowSpan 2, hit-test off): one Border on SteelGroundBrush
├─ Row 0: AppBrandingBar (Grid, 52 tall)
│   ├─ Border on SteelWindowBrush with a SteelPaneLineBrush hairline under it
│   ├─ TitleWarmth (TitleWarmthBrush, opacity 1 while Dashboard.EngineStateKey is Running)
│   └─ ui:TitleBar AppTitleBar (52 tall)
│       ├─ Header: AppBrandingBorder (PadForge-icon.png at 24, "PadForge" at 14 SemiBold)
│       ├─ CenterContent: TitleSearchBox (ClickBorder, style TitleSearchBox, 34 tall, MaxWidth 560)
│       └─ TrailingContent: TitleProfilePill (ProfilePill) + FullScreenBtn (StateToggleButton, 40 by 32)
├─ Row 1: ui:NavigationView NavView (Template PadNavigationViewTemplate, OpenPaneLength 264)
│   ├─ MenuItems: built in code (BuildNavigationItems)
│   ├─ FooterMenuItems: NavSettings, NavAbout
│   ├─ PaneFooter: EngineFootHalo > EngineFoot (the engine block)
│   └─ ContentOverlay Grid
│       ├─ StatusMessageLine (ZIndex 10, hit-test off)
│       ├─ HomePageView, PadPageView, DevicesPageView, ExtrasPageView,
│       │  SettingsPageView, ProfilesPageView, AboutPageView
│       ├─ AddControllerHost (ShellDialog, ZIndex 5, FrameMaxWidth 760) > AddControllerView
│       └─ SearchHost (ShellDialog, ZIndex 5, FrameMaxWidth 660, ClosesOnGroundPress) > SearchPanelView
├─ DriverOverlay (RowSpan 2, ZIndex 1000)
├─ ShutdownOverlay (RowSpan 2, ZIndex 1001)
└─ StartupOverlay (RowSpan 2, ZIndex 1001)
```

`UpdateSteelLayer` collapses `SteelLayer` in the Light theme, where the window's own backdrop shows.

### Title Bar

`AppTitleBar` is wpf-ui's `TitleBar`, which supplies minimize, maximize and close with Snap Layout support. A style in its resources sizes those three buttons 40 by 32 with a top margin of 10, so they center in the 52 of the bar. `CloseClicked` and `MaximizeClicked` go to `TitleBar_CloseClicked` and `TitleBar_MaximizeClicked`, and a press on `AppBrandingBorder` goes to `BrandingBar_MouseDown`.

- `TitleSearchBox` (AutomationId `TitleSearchBox`) is a `ClickBorder` that opens Search. It shows a `SearchLineGeometry` icon, the placeholder `Search_Placeholder` ("Search settings, devices and profiles") and a key chip (`KeyChip`, `TitleSearchShortcut`) whose text `ShowSearchShortcut` sets to `Key_Control` + " K". It is marked `WindowChrome.IsHitTestVisibleInChrome`, so only the box takes the pointer and the bar on either side still drags the window.
- `TitleProfilePill` (`Views/Controls/ProfilePill`, AutomationId `ProfilePillStatusBar`) is the active-profile pill. A click opens `ShowProfileSwitcherPopup` under it, and `InputService.AutoProfileSwitchApplied` flares it. A second click inside `TouchClickDebounceMs` is dropped.
- `FullScreenBtn` (`StateToggleButton`, name `Main_FullScreen`) runs `FullScreenBtn_Click`. Its icon is `FullScreenIcon`, a `GlyphText` in Segoe Fluent Icons.

### Navigation Model

No WPF `Frame`-based navigation. Every page is created once and visibility-swapped, which keeps scroll positions, open cards and text fields across navigation:

1. `NavView_SelectionChanged` closes the type bar, returns while `_rebuildingControllerSection` is set, and passes the selected item's `Tag` to `NavigateToTag`.
2. `NavigateToTag` closes Add a Controller and Search when the tag changes, sets `MainViewModel.SelectedNavTag`, redraws the pills (`RefreshControllerSelectionVisuals`) and shows the one page whose tag matches: `Home`, `Devices`, `Extras`, `Profiles`, `Settings`, `About`, or `Pad{N}` (1-based, so `Pad1` is the first slot).
3. Arriving at Extras from another page calls `ExtrasPageView.ShowCatalog()`, so Extras opens on its catalog.
4. For a controller tag it calls `Dashboard.SetSelectedPad(index)` and `BindPadPage`, which copies the slot's stored rows into its view model inside `SettingsService.MirrorOnly` (so a visit marks nothing changed) and sets `PadPageView.DataContext`.
5. It tells `InputService` which pages are visible (`IsDevicesPageVisible`, `IsPadPageVisible`, `IsHomePageVisible`, `IsProfilesPageVisible`).

`ActivateNavItem` is where a click, a key press and UI Automation's Invoke on an entry land. The `AddController` tag opens Add a Controller. Any other entry closes Add a Controller and Search and marks itself active.

### Sidebar Construction

`Resources/Shell.xaml` holds the sidebar's two templates. `PadNavigationViewTemplate` draws the pane at `OpenPaneLength` on `SteelPaneBrush` with a `SteelPaneLineBrush` edge, its entries in `PART_MenuItemsItemsControl` inside `PART_ScrollViewer`, and the foot (`PART_FooterMenuItemsItemsControl` and the `PaneFooter`) under them. The scroll viewer has a margin of -12 at each side and the list 12 back, so the light around a pill is not clipped at the pane's edges. Both lists are `NavItemsControl`s (AutomationIds `NavigationItems` and `NavigationFooterItems`), whose entries offer Invoke and SelectionItem to UI Automation. There is no back button, pane toggle or icon rail. `PadNavigationViewItemTemplate` draws an entry: a `MainBorder` with corner 8, a 3 by 18 ember `PickBar` at its leading edge while the entry is active, and the icon in the tertiary text color, ember while active. A style in `NavView.Resources` makes each entry 40 tall with 2 under it, at 14, in the secondary text color and SemiBold primary while active.

`BuildNavigationItems()` adds four entries and a label, in this order. Settings and About are declared in XAML as `FooterMenuItems`.

| Tag | Content | Icon (`DecorativeStrokeIcon` geometry) | AutomationId | Source |
|-----|---------|------|--------------|--------|
| `Home` | `Home_Title` ("Home") | `NavHomeGeometry` | `Nav_Dashboard` | `BuildNavigationItems()` |
| `Devices` | `Devices_Title` ("Devices") | `NavDevicesGeometry` | `Nav_Devices` | `BuildNavigationItems()` |
| `Profiles` | `Profiles_Title` ("Profiles") | `NavProfilesGeometry` | `Nav_Profiles` | `BuildNavigationItems()` |
| `Extras` | `Extras_Title` ("Extras") | `NavExtrasGeometry` | `Nav_Extras` | `BuildNavigationItems()` |
| (none) | `Home_Controllers` ("Controllers"), a `TextBlock` | none | `Nav_ControllersLabel` | `BuildNavigationItems()` |
| `Settings` | `Settings_Title` ("Settings") | `NavSettingsGeometry` | `Nav_Settings` | XAML footer (`NavSettings`) |
| `About` | `About_Title` ("About") | `NavAboutGeometry` | `Nav_About` | XAML footer (`NavAbout`) |

`SetNavAutomationId` gives every entry `Nav_` plus its tag. Home keeps the Dashboard's id, `Nav_Dashboard`, and `HomePageView` keeps `DashboardPageView`, since UI tools pair `Nav_<tag>` with `<tag>PageView`. The Controllers label is a heading at level 2 for a screen reader and takes no click or selection. `OnCultureChanged` rewrites the five texts and the two footer entries and rebuilds the controller entries.

`RebuildControllerSection()` removes every item from `ControllerInsertIndex` (5, the index after the label) onward and adds one entry per `MainViewModel.NavControllerItems` item, then the Add Controller entry while `HasAnyControllerTypeCapacity()` is true. It runs on `NavControllerItemsRefreshed` (queued at Background priority, so wpf-ui's items repeater finishes its layout first), on a slot's `OutputType` change, on a culture change and after the engine starts or stops. The `_rebuildingControllerSection` flag stops re-entry and makes `NavView_SelectionChanged` ignore the intermediate selections. A rebuild asked for during a pill drag is queued (`_rebuildPendingAfterDrag`) and `EndCardDrag` replays it. After the rebuild the saved selection tag is marked active again (`SetNavActiveByTag`), or Home when that tag is gone, unless Add a Controller or Search is open.

### Controller Pill

`CreateControllerNavItem` makes the entry and `UpdateControllerNavItemContent` builds its content, a `Border` pill with corner `PillCorner` (19, half its height), `MinHeight` 38, padding 4,0,12,0 and a 1 px outline. The row inside reads, from the start:

| Part | Built as | Notes |
|------|----------|-------|
| Power | `StateToggleButton`, 28 by 28, AutomationId `Nav_SlotPower`, name `Common_Enabled` | A 16 px flame (`BuildFlameGlyph`, `FlameOuterGeometry`). `OnSidebarPowerToggle` |
| Slot number | `TextBlock`, 12 in the body face, tabular figures, 16 wide | The global slot number |
| Type chip | `Button`, 20 by 20, style `MiniTypeButtonActiveStyle`, AutomationId `Nav_SlotTypeChip` | The type's logo (`Path` at 13) or MDL2 glyph at 13. Background `EmberBrush` while the pill is lit, `SteelLineBrush` otherwise. Ink `EmberInkBrush` when lit. A click calls `ShowTypeBar(menuItem, PlacementMode.Right, padIndex, typeChip)` |
| Instance | `TextBlock`, "#N", 12, tabular figures, 22 wide | A fixed box, so stacked pills line up |
| Preset | `MarqueeLabel` at 13 | `NavControllerItemViewModel.PresetName`. Trims at rest and scrolls while the pointer is on the pill |
| Delete | `ui:Button`, 22 by 22, style `EmberIconButtonHot`, AutomationId `Nav_DeleteSlot`, tooltip `Main_DeleteVC` | Laid over the row's end on a host that paints the pill's ground. Shown while the pointer is on the pill or the button has keyboard focus. A touch shows it when its tap ends, so the tap that reveals it cannot delete. `OnSidebarDeleteSlot` |

`ComputeFlameHeat` sets the pill's heat. Lit (ember) when enabled and initializing, or enabled with devices mapped while the engine runs, the virtual controller is connected and `MainViewModel.HasActiveSlots` holds. Cooling (gold, `WaitBrush`) when enabled with devices mapped but the engine is stopped, the virtual controller is not connected, or the engine is idle with the controller parked. Cold (outline) when disabled or nothing is mapped. The power tooltip follows the same order: `Common_Disabled` ("Disabled"), `Main_Initializing` ("Initializing"), `Dashboard_NoDevice` ("No device"), `Main_EngineStopped` ("Engine stopped"), `Main_VcFailed` ("Virtual controller failed"), `Main_AwaitingDevices` ("Awaiting devices"), `Common_Idle` ("Idle"), `Main_Active` ("Forging"). While initializing, the flame flashes (opacity 1 to 0.15, 500 ms, reversing) unless `SystemParameters.ClientAreaAnimation` is off.

The selected pill has an `EmberBrush` outline on `EmberPickBrush`. The others take `PillOutlineKey(lit, cooling)`: `EmberRingSoftBrush` while forging, `WaitRingBrush` while waiting, `SteelPillLineBrush` while cold. A forging pill rests on `EmberWashBrush`, and every unselected pill lifts to `SteelPaneHoverBrush` under the pointer. A disabled pill stands at opacity 0.6 and a cold one at 0.72. A `Halo` under the row lights a forging pill (`Radius` = `PillLightReach`, 12, strength 0.18 with a rim of 0.35 when selected, 0.07 otherwise). The entry's accessible name is `AccessibleNames.SlotTitle(slotNumber)` and its help text the Preset. A rebuild puts keyboard focus back on the button that had it.

The Add Controller entry (`BuildAddControllerNavItem`, tag `AddController`, AutomationId `Nav_AddController`, name `Main_AddController`) is a small twin of Home's Add Controller tile: a dashed outline, a plus sign and the words.

### Type Bar

`ShowTypeBar(anchor, placement, slot, opener)` shows one slot's seven types in a `Popup` (`StaysOpen="False"`), on a `SteelRaisedBrush` surface with a `SteelPillLineBrush` edge and a separate shadow element behind it. A pill's chip opens it to the right of the pill. A Home card's type tile opens it under the card (`PlacementMode.Bottom`, centered under the card). Calling it while the bar is open closes it, and a reopen on the same anchor within 300 ms of a close is ignored, so the click that dismisses the bar cannot raise it again. A press anywhere outside the bar closes it, and `KeyboardPopup.Wire` returns focus to `opener`.

`AddRetypeButtons` fills it with `SegmentButton`s, AutomationId `RetypeBtn_` plus the type, in this order: Xbox, PlayStation, Nintendo, Extended, KeyboardMouse, Midi, Vr. The slot's current type is `IsSelected`, styled `MiniTypeButtonActiveStyle` on `EmberBrush` with dark ink, and a click on it only closes the bar. A click on another type closes the bar and calls `ChangeSlotType(padIndex, type)`. MIDI is unavailable while `SettingsViewModel.IsMidiAvailable` is false (tooltip `Main_MIDI_NotRunning`), and VR while `HMaestroVRController.IsAvailable()` is false (`Main_VR_RequiresSteamVR`) or `SettingsManager.CanSlotTakeType` finds no room (`Main_VR_Max_Format`, "VR (max {0})"). An unavailable choice is disabled, its icon at opacity 0.35, and its tooltip shows while disabled.

### Add a Controller

Add a Controller is a dialog over the page area, not a popup. `OpenAddController(device, opener)` closes the type bar and Search, sets `AddControllerView.DataContext` to `BuildAddController(device)`, opens `AddControllerHost` (a `ShellDialog`, AutomationId `AddControllerDialog`), clears the sidebar's active entry, takes the pages out of the Tab order (`SetPagesTabStop(false)`) and focuses the first choice. The pages stay drawn under it, since a collapsed controller page unloads its views. Home's Add Controller tile, the sidebar's Add Controller entry, Home's offer (Use It), Home's first page (its link to the other types), the Devices page's New Controller and Search's action all open it.

`Views/AddControllerView.xaml` shows the title `AddController_Title` ("Add a Controller"), the subtitle `AddController_Subtitle`, a full notice (`AddController_Full`) while 16 controllers exist, a close button (`AddController_Close`), and three groups:

| Group | AutomationId | Panel | Content |
|-------|--------------|-------|---------|
| Driven By (`AddController_DrivenBy`) | `AddController_DrivenBy` | `FlexLinePanel` | Shown while there is a device to offer: the device given, or every connected game controller no controller uses (`InputService.UnusedGameControllers`), then Choose Later. Ids `AddController_Device_N` and `AddController_ChooseLater` |
| Common (`AddController_Common`) | `AddController_Common` | `TileGridPanel`, least 150, at most 3 columns | Xbox, PlayStation, Nintendo |
| More Outputs (`AddController_MoreOutputs`) | `AddController_More` | `TileGridPanel`, least 120, at most 4 columns | Keyboard + Mouse, Extended, MIDI, VR |

Each type tile (`TypeTileButton`, `TypeTile_Click`) keeps the AutomationId of the PadForge 5 popup button it replaced: `AddXbox360Btn`, `AddDS4Btn`, `AddNintendoBtn`, `AddRawBtn`, `AddKeyboardMouseBtn`, `AddMidiBtn`, `AddVrBtn` (`ControllerTypeChoice.AddButtonId`). `ControllerTypeChoice.For` makes a tile unavailable when 16 controllers exist (`InputManager.MaxPads`), when its type is at its own cap (`SettingsManager.MaxXbox360Slots`, `MaxPlayStationSlots`, `MaxNintendoSlots`, `MaxExtendedSlots`, `MaxKeyboardMouseSlots` and `MaxMidiSlots` are 16, `MaxVrSlots` is 1), when MIDI has no running API, or when VR has no SteamVR. Its tooltip then says why (`Main_*_Max_Format`, `Main_MIDI_NotRunning`, `Main_VR_RequiresSteamVR`), and its line reads `AddController_MidiNotRunning`, `AddController_VrNeedsSteamVr` or `AddController_VrOnlyOne` in place of what the type is for. A tile click raises `TypeChosen`, and `CreateController` makes the slot, assigns the Driven By device when one was picked, and opens the new slot's page (`FindLastSlotOfType`). The foot reads `AddController_Foot` ("To change the type later, click the type chip on the controller. It takes one click.").

`HasAnyControllerTypeCapacity()` counts `SettingsManager.SlotCreated` and is true while fewer than 16 slots exist. Every type's cap but VR's equals that total.

### Search

`SearchHost` holds `SearchPanelView` (see [SearchPanel](#searchpanel)). `WireSearch` makes the `SearchService`, `SearchViewModel` and `SearchNavigator`, builds the index once the window is idle after loading, and wires the box, the window's `PreviewKeyDown` (Ctrl+K opens Search from anywhere, `Window_SearchKey`) and a press outside the dialog (`Window_SearchOutsidePress` closes it, except on the box). `OpenSearch` refuses while an input is being recorded or an overlay covers the window, binds the controller page to the first made slot when it is bound to none, and opens the dialog. It reads what shows first: `SearchService.RefreshAvailability(otherControllers: false)` takes the other pages and the controller the page is bound to, the query runs, and Search shows. `ReadOtherControllersLater` then reads every other made controller at Background priority, in the sidebar's order. Each is bound through `BindPadPage`, the step a visit takes (its stored rows mirrored in, its selected device's inputs refreshed), with `PadPage.ReadingForSearch` set so the picture stays on the bound controller, and the page is bound back before anything draws. A setting the bound controller has stays its own, and one it lacks is offered once, on the first controller that has it, with that controller's name in its second line. The query then runs again and keeps the picked result while it is still listed. The late read is skipped once Search has closed or a newer read has begun. A mapping row's option is read from the controller's own rows (`Mappings`), so it is found while the picture shows and the table holds no rows.

### Sidebar Drag Reordering

Drag a pill to reorder virtual controller slots:

1. `OnCardDragStart` (the pill's `PreviewMouseLeftButtonDown`) records the start position.
2. `OnNavViewDragMove` (NavView `PreviewMouseMove`) starts the drag past `SystemParameters.MinimumHorizontalDragDistance` or its vertical twin. `BeginCardDrag()` makes a `CardDragAdorner` (a bitmap snapshot of the pill that follows the pointer) and an `InsertionLineAdorner`.
3. The target comes from the pointer's height on a pill: the top and bottom 25% insert, the middle 50% swaps. A pointer more than 20 px outside the pill column clears the indicators, so a drag into the page area does nothing.
4. `OnNavViewDragEnd` (NavView `PreviewMouseLeftButtonUp`) calls `EndCardDrag`. A swap calls `InputService.SwapSlots(srcPad, tgtPad)`. An insert within the same type group calls `InputService.MoveSlot(srcPad, groupLocalPosition)`. `OnNavViewDragKeyDown` cancels on Escape.

### Device Drop on a Pill

The Devices page starts `DragDrop.DoDragDrop()` with a `DataObject` keyed `"DeviceInstanceGuid"` holding the device's `InstanceGuid`. Each pill sets `AllowDrop` and handles `DragOver`, `DragLeave` and `Drop` (`OnSidebarCardDragOver`, `OnSidebarCardDragLeave`, `OnSidebarCardDrop`), and the drop assigns the device to the pill's slot.

### Engine Block

The sidebar's `PaneFooter` is the engine block, under Settings and About: `EngineFootHalo` (lit while `Dashboard.EngineStateKey` is Running) around `EngineFoot` (`MinHeight` 60, corner 12, `SteelFootBrush`, an `EmberRingSoftBrush` edge and a warm radial wash while running). Its `DataContext` is set to `MainViewModel` by name in the constructor, since the footer is not in the window's tree until wpf-ui's template takes it in.

| Element | Binding | Behavior |
|---------|---------|----------|
| `EngineFootRing` (38 by 38, corner 19) with `EngineFootFlame` (`FlameOuterGeometry`, 15) | `Dashboard.EngineStateKey` | Running: ember ring on `EmberTintBrush` and an ember flame. Idle or Stopping: gold ring and flame (`WaitBrush`). Stopped: `SteelLineBrush` ring and an outline flame. Its `Halo` breathes while running |
| `EngineFootState` (AutomationId `EngineFootState`) | `EngineStatusText` | 14 SemiBold |
| `EngineFootLine` | `Dashboard.LiveLine` | `Shell_Foot_Live_Format` ("Live: {0} of {1}"), 12 |
| `EngineFootRate` | `Dashboard.PollingRateLead`, `PollingRateNumber`, `PollingRateTail` | Three runs in the order the language's format puts them, the number at 18 SemiBold in `DisplayFontFamily`. `ColdBrush` while running, disabled text color otherwise. Its accessible name is `Dashboard.PollingFrequencyText` |

### Message Line

`StatusMessageLine` replaced the status bar. It is a `Border` (`SteelRaisedBrush`, corner 6, `MaxWidth` 720) at the page area's lower left, drawn over the pages with `Panel.ZIndex` 10 and hit-test off, collapsed while `StatusText` is empty or null. `StatusMessageText` is a polite live region. `SweepStatusMessage` clears a message whose decay is due (`MainViewModel.IsStatusDecayDue`), after a 250 ms fade when animations are on. A message that reports a failure stays until the next one.

### Overlays

| Layer | ZIndex | Shown when | Contents |
|-------|--------|-----------|----------|
| `SteelLayer` | bottom, hit-test off | Dark theme | `SteelGroundBrush` under all content |
| `DriverOverlay` | 1000 | A driver install or removal runs (`RunDriverOperationAsync`) | `ProgressRing` + `DriverOverlayText` in the `CardTitle` style |
| `ShutdownOverlay` | 1001 | The app is closing | `ProgressRing` + `Main_ShuttingDown` ("Closing PadForge…") |
| `StartupOverlay` | 1001 | `App.OrphanSweepTask` is still running at launch | `ProgressRing` + `Main_StartingUp` ("Starting PadForge…") + `Main_CleaningPreviousSession` ("Cleaning up virtual controllers left from a previous session.") |

Each overlay is a `#CC000000` scrim under a centered card (corner 8, padding 32,24). PadForge 6 has no first-run overlay or welcome tour: Home's first page takes their place (see [HomePage](#homepage)).

### Composition Root (Code-Behind)

`MainWindow.xaml.cs` (about 9,200 lines) wires services to view models. The constructor:

1. Creates `MainViewModel` and sets it as the window's `DataContext` and `EngineFootHalo`'s.
2. Sets the pages' `DataContext`: Home and Extras get `Dashboard`, Devices gets `Devices`, Settings, Profiles and About get `Settings`, and the controller page gets `Pads[0]` until navigation re-points it (with no pad context its whole binding tree would fail at startup). It calls `PadPageView.BindSlotState(Dashboard)` and `PadPageView.BindSteamVrState(Settings)`.
3. Creates `SettingsService`, `InputService`, `RecorderService` and `DeviceService`, and hands `InputService` to the Devices, Settings and Profiles pages and the recorder to `PadPage`.
4. Wires view-model and page events to the services:
   - Home's events: engine toggle (`InputService.Start` and `Stop`, the stop run on the thread pool after `ShowEngineStopping`), power toggles and deletes, the type tile (`ShowTypeBar`), drags (`SwapSlots`, `MoveSlot`), the Add Controller tile and the offer (`OpenAddController`), Add Device (the Devices page), an extra in use (`ExtrasPageView.Show(key)`) and Open Extras.
   - The controller page's `SlotEnabledToggled`, `DeleteRequested` and `AddDeviceRequested`. The Profiles page's `ControllerOpenRequested`.
   - Settings commands: save, reload and reset through `SettingsService`, driver installs and removals through `RunDriverOperationAsync`.
   - Per pad: `TestRumbleRequested` and the recording flow.
   - Profile import: `ImportProfileFile(path, owner)` reads a `.pfprofile`, or runs `ForeignConfigImporter.Translate` on another tool's config and shows the [ImportConfigDialog](#importconfigdialog), which lands the profile through `AddWorkshopProfile`.
   - Screen Overlays: `MainWindow.KeyboardScreens.cs` answers `Dashboard.ChooseScreenOverlayContentRequested` with `ConfigureScreenOverlay`, which opens [KeyboardScreenDialog](#keyboardscreendialog). The same file opens a keyboard screen's dialog from its Devices panel.
   - `MainWindow.BlissBox.cs` opens [BlissBoxPlayerDialog](#blissboxplayerdialog) and [DreamcastScreenDialog](#dreamcastscreendialog). `MainWindow.FlydigiScreen.cs` opens [FlydigiScreenDialog](#flydigiscreendialog) from a Flydigi Apex pad's panel. `MainWindow.Falcon.cs` holds the Novint Falcon card's and row's buttons.
   - Keyboard, mouse and touchpad driver switches: `Views.KeepDriverDialog.Show` after the switch, `KeepDriverSeconds` = 15 ([KeepDriverDialog](#keepdriverdialog)).

### Timer Architecture

| Timer | Interval | Purpose |
|-------|----------|---------|
| `InputService._uiTimer` (`DispatcherTimer` at Render priority) | 33 ms (`UiTimerIntervalMs`) | `UiTimer_Tick` pushes engine state into the view models. Runs while the engine runs |
| `_driverStatusTimer` | 5 s | `RefreshHidHideStatus()`, `RefreshHIDMaestroStatus()`, `InputService.RetryOwedGiveBacks()`, `RefreshBthPS3Status()`, `RefreshMidiServicesStatus()` and `SweepStatusMessage()`. Started once and stopped only on close, so the message line keeps decaying after the engine stops |
| `CompositionTarget.Rendering` | each frame | The preview views (`ControllerModelView`, `ControllerModel2DView`, `ControllerSchematicView`, `KBMPreviewView`, `MidiPreviewView`, `VRPreviewView`, `MousePreviewControl`) draw per frame |

---

## HomePage

**Files:** `Views/HomePage.xaml`, `Views/HomePage.xaml.cs`, `Views/HomePage.Cards.cs`

Home replaced the Dashboard. Its `DataContext` is `DashboardViewModel`, the Dashboard's view model, whose Home parts are in `DashboardViewModel.Home.cs`, `DashboardViewModel.Cards.cs` and `DashboardViewModel.FirstRun.cs`. The services the Dashboard carried moved to [ExtrasPage](#extraspage). Home raises an event for each click and `MainWindow` answers it.

### Layout Structure

```
ScrollViewer HomeScroll
└─ Grid HomeGround
    ├─ FirstRunPanel (StackPanel, MaxWidth 720, AutomationId Home_FirstRun): shown while no controller exists
    │   ├─ FirstRunDeviceCard (Home_FirstRun_Device): the controller PadForge sees, or that it sees none,
    │   │    FirstRunCardTitle + FirstRunCardLine (polite live text), FirstRunStart (Common_Start, Home_FirstRun_Start)
    │   ├─ FirstRunTitle (heading 1) + FirstRunBody
    │   ├─ FirstRunTypes (ItemsControl, Home_FirstRun_Types): three FirstRunTypeTile tiles,
    │   │    Xbox, PlayStation, Keyboard + Mouse (Home_FirstRun_Xbox, _PlayStation, _KeyboardMouse)
    │   ├─ MoreTypesLine with MoreTypesLink (MoreTypes_Click): the other four types, in Add a Controller
    │   └─ the foot: pairing (PairLink_Click, the Devices page) and ready-made profiles
    │        (ProfileLink_Click, Get Profiles on its starters)
    └─ HomeContent (StackPanel, Margin 36,26,36,36): shown once a controller exists
        ├─ HomeTitle (heading 1)
        ├─ EngineCard (Border, corner 12): EngineHalo, EngineWash, the engine flame in its ring,
        │    EngineStatusLine + EngineDevicesLine, EngineStats
        ├─ HomeOffer (Border, WaitWellBrush, AutomationId HomeOffer): shown on HasHomeOffer
        ├─ Controllers head: ControllersHeading + ControllersCount, CardsChoice
        ├─ SlotsItemsControl (TileGridPanel): one card per SlotSummary + the Add Controller tile
        └─ Extras in use: ExtrasHeading, ExtrasInUseRows (TileGridPanel of ExtraTile), ExtrasFoot
```

`DashboardViewModel.IsFirstRun` (`SlotSummaries.Count == 0`) chooses between the first page and the rest. A first-page tile raises `FirstRunTypeChosen`, and `MainWindow.CreateController` makes that controller driven by `Dashboard.FirstRunDeviceGuid`.

### Engine Card

| Element | Binding | Behavior |
|---------|---------|----------|
| `EngineCard` | `EngineStateKey` | `CardStrokeColorDefaultBrush` edge, `EmberRingSoftBrush` while Running. `EngineHalo` (radius 50, strength 0.07, rim 0.14) and `EngineWash` light while Running |
| `EngineFlame` | `IsEngineOn`, `EngineStateKey` | `StateToggleButton`, 76 by 76, name `Dashboard_InputEngine` ("Input Engine"), `EngineToggle_Click` raises `EngineToggleRequested`. The flame is ember while Running and gold while Idle or Stopping, and flashes gold while stopping when animations are on. `EngineRingHalo` breathes while Running |
| `EngineStatusLine` | `EngineStatus` | One word at 32 in `DisplayFontFamily`, a polite live region |
| `EngineDevicesLine` | `HeroLine` | What the state means, at 14 |
| `EngineRate` | `PollingFrequencyText` (accessible name) | The rate in runs, cold blue while one is measured, label `Home_Stat_PollingRate` ("Polling rate") |
| `EngineLive` | `LiveControllers`, `LiveLine` | Label `Home_Stat_ControllersLive` ("Controllers live") |
| `EngineDevices` | `OnlineDevices` | At 28 SemiBold, label `Home_Stat_DevicesConnected` ("Devices connected") |

`EngineStats` is a `FlexLinePanel` (gap 36), so the three numbers wrap on a narrow page. The engine card has no worded start button. The flame is its only switch.

### Offer Band

`HomeOffer` shows while `HasHomeOffer` is true: a device PadForge has just met that is connected and on no virtual controller (Settings > Assignment Prompts). `HomeOfferLine` (polite) is three runs, `HomeOfferLead`, the device's name in SemiBold, and the tail. `HomeOfferUse` (`EmberPrimaryButton`, `Home_Offer_Use`, "Use It", AutomationId `HomeOfferUse`) raises `HomeOfferUseRequested`, which opens Add a Controller for the device. `HomeOfferDismiss` (`QuietButton`, `Pad_AssignOffer_Dismiss`, "Not Now", AutomationId `HomeOfferDismiss`) runs `DismissHomeOfferCommand`.

### Controller Cards

`SlotsItemsControl` shows a `CompositeCollection`: a `CollectionContainer` (`SlotsCollectionContainer`, handed `SlotSummaries` in `DataContextChanged`, since a container outside the visual tree cannot bind) and the Add Controller tile. The panel is a `TileGridPanel` with `Gap` = `HomePage.CardGap` (16). A typed `DataTemplate` for `SlotSummary` picks `SlotCardDetailed` or `SlotCardCompact`, so the tile, a `UIElement`, never meets a card template.

`CardsChoice` sets the size: three `SegmentRadio` buttons, `Home_Cards_Detailed`, `Home_Cards_Compact` and `Home_Cards_Auto` (AutomationIds `Home_Cards_Detailed`, `Home_Cards_Compact`, `Home_Cards_Auto`), bound to `DashboardViewModel.HomeCards` and handled by `Cards_Checked`. Auto (tooltip "Detailed while the cards fit the window, compact once they would run past it") is detailed while the detailed grid ends inside the window. `HomePage.Cards.cs` measures that (`ReadCardsFit`), with least widths `DetailedCardMinWidth` 470 and `CompactCardMinWidth` 300.

A detailed card (`SlotCardDetailed`) is a `Border` in `SlotCardEdge` tagged with `PadIndex`, with a `SlotCardHalo` around it:

| Part | Element | Binding and behavior |
|------|---------|----------------------|
| Type tile | `Button` in `SlotTypeTile`, 34 by 34, AutomationId `Dash_SlotTypeChip` | `TypeGeometry` (a `Path` at 20) or `TypeGlyph` (MDL2 at 18). `TypeChip_Click` finds the card `Border` with the slot's tag and raises `SlotTypeChipClicked(slotIndex, card, chip)`. `MainWindow` opens the type bar under the card |
| Title | `TextBlock` in `SlotTypeName` at 18, AutomationId `Dash_SlotTitle`, then "#N" from `TypeInstanceLabel` | The type's name, quiet on a cold controller |
| Preset | `MarqueeLabel` | `PresetName`. Scrolls while the pointer is on the card |
| State pill | `StateToggleButton` in `StatePill`, AutomationId `Dash_SlotPower`, name `Common_Enabled`, tooltip `Home_Card_Power` | A `SlotFlame` path and `StateWord` (polite). `PowerToggle_Click` raises `SlotEnabledToggled(slotIndex, !SettingsManager.SlotEnabled[slotIndex])`, inverting the live setting rather than the summary |
| Delete | `ui:Button` in `CardCloseButton`, AutomationId `Dash_DeleteSlot`, tooltip `Main_DeleteVC` | Always there, quiet until the pointer is on it. `DeleteSlot_Click` raises `DeleteSlotRequested` |
| Stage | `ClickBorder` in `SlotStageEdge`, basis 204, 140 tall, AutomationId `Dash_SlotStage`, name `Dashboard_SlotCard_Configure` | The picture (below). `OpenSlot_Click` raises `SlotCardClicked`, the keyboard's way to the page |
| Driven by | `Pad_DrivenBy` ("Driven by") over an `ItemsControl` on `MappedDevices` (`DrivenByRow`) | Each row: a `DeviceLight` (ember while the device sends input, steel while connected and quiet, hollow while not connected), the name in `DeviceNameText`, and the link and battery or the words for a device that is not connected |
| No device | `Mapping_NoDeviceMapped` ("No device mapped") + `Pad_AddDevice` ("Add Device", AutomationId `Dash_AddDevice`) | Shown while `HasMappedDevices` is false. `AddDevice_Click` raises `AddDeviceRequested` (the Devices page) |
| Wait hint | `WaitHint` (polite) | What a waiting controller waits for, collapsed when empty |
| Foot | `StageLedger` chips (AutomationId `Dash_StageChips`) + mapped and connected counts | One chip per stage the slot runs |

A click anywhere on the card opens the page, through the drag code's `OnDragEnd`. A compact card (`SlotCardCompact`) has the picture in a strip across the top, the type tile (`SlotTypeTileCompact`), the title, number and preset, the state as a flame in a round button (`StateRound`), the first device with how many more there are, and the stage chips with Delete at their end. It has no Add Device button and no wait hint, and keeps the click, drag, type tile and power actions.

`SlotSummary.Heat` is one word that never changes with the language: `Forging` while the controller is live or being made, `Waiting` while it is enabled with devices but the engine is stopped or its virtual controller is not there, `Cold` while it is disabled or has no device. The card's edge, halo, flame and picture switch on it. `StateWord` reads, in order: `Common_Disabled` ("Disabled"), `Main_Initializing` ("Initializing"), `Main_VcFailed` ("Virtual controller failed"), `Dashboard_StatusCold` ("Cold"), `Main_EngineStopped` ("Engine stopped"), `Main_AwaitingDevices` ("Awaiting devices"), `Main_Active` ("Forging").

### Stage Pictures

The stage's `SlotPictureBox` stacks, bottom to top:

| Layer | Element | Shown when |
|-------|---------|-----------|
| Gray picture | `DecorativeImage` on `PictureGray` (`SlotPictureGray`) | Always, so a card that is not forging stands dim and gray |
| Color picture | `DecorativeImage` on `Picture` (`SlotPictureColor`) | While the controller forges |
| Moving model | `LiveStage` (`CardLiveStage`) | `Heat` is Forging and `ShowsLiveModel` is true: the 3D model the still was drawn from, its sticks and triggers turned and what is held lit |
| Moving 2D art | `LiveArtStage` (`CardLiveArt`) | `Heat` is Forging and `ShowsLiveArt` is true: the layers of the 2D art, each stick shifted, each trigger filled and each held button shown |
| Held glow | `HeldGlow` (`CardHeldGlow`) | `Heat` is Forging and `PictureMoves` is false: a still picture lights what is held |
| Type mark | the type's geometry or a 68 px glyph | `HasPicture` is false |

The picture is the controller page's own view: a 3D still while the page shows 3D, the 2D art while it shows 2D (`StagePictures`, `ControllerStill`). The moving model shows only where WPF draws 3D on the graphics card, and `OnRenderTierChanged` tells the view model when `RenderCapability.Tier` changes, as a remote desktop session can.

### Add Controller Tile

`AddControllerCard` is a `ClickBorder` (corner 12, `MinHeight` = `HomePage.AddTileMinHeight`, 132) with a dashed `Rectangle` (`DashLineBrush`, dash 4 3), a `PlusLineGeometry` icon and `Main_AddController` ("Add Controller"). It shows while `ShowAddController` is true. A click, Enter or Space runs `AddControllerCard_Click`, which raises `AddControllerRequested`. `AddControllerCardElement` exposes it so Add a Controller can return focus to it.

### Extras in Use

`ExtrasInUseRows` is a `TileGridPanel` (least 300, gap 16) of `ExtraTile`s in `HomeExtraTile`, one per extra, in the Extras page's order: Web Controller (`EnableWebController`, its action `Home_ShowQr`, "Show QR"), Head Tracking (`HeadTrackingAnyEnabled`), Game Telemetry, Twitch Chat, Remote Link, Motion Server (`EnableDsuMotionServer`), Game Mods, Overlays (`OverlaysAnyEnabled`), Touchpad Overlay, Screen Overlay (`ScreenOverlaysAnyEnabled`), Crosshair (`CrosshairsAnyEnabled`) and Magnifier (`MagnifierEnabled`), the twelve keys of `ExtrasPage.Keys`. The section's heading is `Home_ExtrasInUse`. A tile shows while its extra's switch is on, with the extra's status line, and is lit while the engine runs (`Heat.IsLive` on `IsEngineOn`). `ExtraInUse_OpenRequested` raises `ExtraOpenRequested(key)`, which opens that extra's page. `ExtrasFoot` holds `ExtrasLine` while `ShowsExtrasRestLine` is true (how many others there are, its middle run `ExtrasLink` a link to the Extras page), or, while `ShowsExtrasIntro` is true, the Extras page's subtitle (`ExtrasIntroLine`, `Extras_Subtitle`) and `OpenExtrasButton` (`Home_OpenExtras`, AutomationId `Home_OpenExtras`). With every extra on it shows nothing.

### Event Handlers (Code-Behind)

| Handler | Event | Raises |
|---------|-------|--------|
| `EngineToggle_Click` | `EngineFlame` Click | `EngineToggleRequested` |
| `AddControllerCard_Click` | `AddControllerCard` Click | `AddControllerRequested` |
| `HomeOfferUse_Click` | `HomeOfferUse` Click | `HomeOfferUseRequested(device, anchor)` |
| `OpenSlot_Click` | stage Click | `SlotCardClicked(slotIndex)` |
| `AddDevice_Click` | Add Device Click | `AddDeviceRequested` |
| `DeleteSlot_Click` | Delete Click | `DeleteSlotRequested(slotIndex)` |
| `PowerToggle_Click` | state pill Click | `SlotEnabledToggled(slotIndex, !SlotEnabled[slotIndex])` |
| `TypeChip_Click` | type tile Click | `SlotTypeChipClicked(slotIndex, card, chip)` |
| `ExtraInUse_OpenRequested` | `ExtraTile.OpenRequested` | `ExtraOpenRequested(key)` |
| `OpenExtras_Click` | `OpenExtrasButton` and the foot's link | `OpenExtrasRequested` |
| `FirstRunTile_Click`, `MoreTypes_Click`, `PairLink_Click`, `ProfileLink_Click`, `FirstRunStart_Click` | the first page | `FirstRunTypeChosen`, `FirstRunMoreTypesRequested`, `FirstRunPairRequested`, `FirstRunProfileRequested`, the engine start |
| `Cards_Checked` | `CardsChoice` | sets `HomeCards` |
| `SlotCard_Loaded`, `OnCardMouseDown`, `OnDragMove`, `OnDragEnd`, `OnDragKeyDown`, `OnDragCaptureLost` | the card `Border` | the drag below, or `SlotCardClicked` for a click |

### Card Drag Reordering

`WireDragHandlers` runs on `Loaded`. A drag uses the same adorner pair as the sidebar (`CardDragAdorner`, `InsertionLineAdorner`), with zones across a card's width: the left 25% inserts before, the middle 50% swaps, the right 25% inserts after. A drag across type groups is refused (`GetSlotOutputType`, `IsInsertionInSameTypeGroup`). The drop raises `SlotSwapRequested(PadIndexA, PadIndexB)` or `SlotMoveRequested(SourcePadIndex, TargetVisualPos)` with a position inside the source's type group, and `MainWindow` calls `InputService.SwapSlots` or `MoveSlot` and marks the settings dirty. Escape and a lost capture cancel.

---

## PadPage

**Files:** `Views/PadPage.xaml`, `Views/PadPage.xaml.cs`, `Views/PadPage.SettingResets.cs`. Its view model is `PadViewModel`, whose section logic is `ViewModels/PadViewModel.Sections.cs`.

The controller page, one per virtual controller slot, bound by `MainWindow.BindPadPage` to the selected `PadViewModel`. PadForge 6 replaced the two tiers of up to fourteen tabs with a header and six sections. The old tab numbers live on: `PadViewModel.SelectedConfigTab` still holds a tab from 0 to 17, and `PadViewModel.Sections.cs` maps each tab to its section. A tab of a stacked section is now a group of cards in that section's scrolling column.

### Layout Structure

```
Grid (2 rows)
├─ Row 0 (Auto): the header (StackPanel, Margin 36,22,36,0)
│   ├─ Line 1: PadTypeHalo > PadTypeTile (46 by 46, corner 12), PadTitle (heading 1),
│   │    HMaestroProfileBar (the Preset), SteamVrState (VR slots), SlotPowerHost, PadMoreButton
│   ├─ Line 2: DrivenByLabel, DrivenByList (a pill per device), AddDeviceButton
│   ├─ AssignOfferBanner (shown while an assignment offer stands)
│   └─ SectionStrip (WrapPanel of six RadioButtons over a SteelLineSoftBrush hairline)
└─ Row 1 (*): ContentTabControl (header-less, SelectedIndex = SelectedSection)
    ├─ Section 0: Buttons (MappingsTabRoot)
    ├─ Section 1: SticksSectionScroll
    ├─ Section 2: RumbleSectionScroll
    ├─ Section 3: MotionSectionScroll
    ├─ Section 4: LightsSectionScroll
    └─ Section 5: MacrosSectionScroll
```

`ContentTabControl` (`Controls/ContentTabControl.cs`) is a `TabControl` whose template is only `PART_SelectedContentHost`, so only the selected section is in the visual tree, and whose UI Automation peer lists the selected section's content. The page's gutters are 36 at each side.

### Header

| Element | AutomationId | Binding and behavior |
|---------|--------------|----------------------|
| `PadTypeTile` in `PadTypeHalo` | | The slot type's logo or glyph (`TypeGeometry`, `TypeGlyph`), as its Home card and pill show it |
| `PadTitle` | | Heading level 1: the type's name and which one of that type |
| `HMaestroProfileBar` | | Collapsed until code-behind shows it. The Preset label, `HMaestroProfileCombo` (AutomationId `HMaestroProfileCombo`, its items `PresetChoices`) with a `SettingResetButton` for `ProfileId`, or on a Keyboard + Mouse slot `KbmSurfacesCombo` (AutomationId `KbmSurfacesCombo`) with a reset for `KbmSurfaces`. `ProfileCombo_PreviewKeyDown` makes Enter and Escape commit or dismiss |
| `SteamVrState` / `SteamVrStateText` | `Pad_SteamVrState` | A VR slot's SteamVR state (`ShowSteamVrState`), bound through `BindSteamVrState(SettingsViewModel)` |
| `SlotPowerButton` in `SlotPowerHalo` | `Pad_SlotPower` | A `StateToggleButton` bound to the slot's `SlotSummary` (`SelectedSlotSummary`, set by `BindSlotState(DashboardViewModel)`): the flame and `SlotStateWord` (`StateWord`, polite). `SlotPower_Click` raises `SlotEnabledToggled` with the inverse of `SettingsManager.SlotEnabled` |
| `PadMoreButton` | `Pad_More` | `MoreMenu_Click` opens its menu: `Common_Copy` (`CopySettingsCommand`), `Common_Paste` (`PasteSettingsCommand`), `Pad_CopyFrom` ("Copy From…", `CopyFromCommand`, opens [CopyFromDialog](#copyfromdialog)), `Pad_ClearAll` (`ClearAllMappings_Click`), and `Main_DeleteVC` (`DeleteController_Click`, AutomationId `Pad_DeleteController`, raises `DeleteRequested`) |
| `DrivenByList` | `Pad_DrivenByList` | A `ListBox` on `MappedDevices`, one pill per device (`MinHeight` 34, `MaxWidth` 460, corner 17). The selected pill is the device whose settings the page shows (`SelectedMappedDevice`). A device that is not connected is quiet with a dashed outline, a low battery gives a gold edge, and a light beside the name is ember while the device sends input |
| `AddDeviceButton` | `Pad_AddDevice` | `AddDevice_Click` raises `AddDeviceRequested`, and `MainWindow` opens the Devices page |
| `AssignOfferBanner` | `AssignOfferBanner` | The assignment offer (Settings > Assignment Prompts), with `AssignOfferAccept` and `AssignOfferDismiss` |

### Sections

`SectionStrip` holds six `RadioButton`s in the `SectionStripButton` style (group `PadSection`, an ember underline in a `Halo` when checked, 0.35 of it under the pointer), each with a `Section*Geometry` icon from `Resources/Shell.xaml`. `Tag` is the section's number.

| Tag | Button | AutomationId | Label | Content | Tabs (groups) |
|-----|--------|--------------|-------|---------|---------------|
| 0 | `SectionButtons` | `Section_Buttons` | `FirstSectionName`: `Pad_Mappings` ("Mappings") on a controller, `Pad_Section_KeysMouse` ("Keys & Mouse") on Keyboard + Mouse, `Pad_Section_NotesControls` ("Notes & Controls") on MIDI, `Pad_Section_Hands` ("Hands") on VR | `MappingsTabRoot` | 0 picture, 2 list, 17 output |
| 1 | `SectionSticks` | `Section_Sticks` | `Pad_Section_Sticks` ("Sticks & Triggers") | `SticksSectionScroll` | 3 `TabSticks`, 4 `TabTriggers`, 14 `TabMouse` |
| 2 | `SectionRumble` | `Section_Rumble` | `Pad_Section_Rumble` ("Rumble & Haptics") | `RumbleSectionScroll` | 5 `TabForceFeedback`, 9 `TabImpulseTriggers`, 6 `TabAdaptiveTriggers`, 11 `TabWheel`, 16 `TabBassShakers` |
| 3 | `SectionMotion` | `Section_Motion` | `Pad_Section_Motion` ("Motion & Touch") | `MotionSectionScroll` | 8 `TabGyro`, 10 `TabTouchpad`, 13 `TabPointer` |
| 4 | `SectionLights` | `Section_Lights` | `Pad_Section_Lights` ("Lights & Sound") | `LightsSectionScroll` | 7 `TabLighting`, 12 `TabAudio` |
| 5 | `SectionMacros` | `Section_Macros` | `Pad_Section_Macros` ("Macros & Menus") | `MacrosSectionScroll` | 1 macros, 15 menus |

Sections 1 to 4 are stacked (`PadViewModel.IsStackedSection`): their groups stand one under another in one column, and `PadPage.TabOfGroupName` maps each group's `x:Name` to its tab. Sections 0 and 5 show one part at a time under a part switch. Buttons has Picture and List (`TabController` and `TabMappings`, AutomationIds `TabController` and `MappingsTab`, labels `Pad_View_Picture` and `Pad_View_List`). Macros & Menus has `TabMacros` and `TabMenus` (AutomationIds `MacrosTab` and `MenusTab`), which are the heads of the two lists.

How a section is chosen:

- `SectionBtn_Click` and `SectionBtn_Checked` call `GoToSection`. The Checked handler is there because UI Automation's Select checks a radio button without a click.
- `GoToSection` opens the section on the tab it last showed (`PadViewModel.LastTabOfSection`), or on its first available tab when that one has gone, keeping the column's scroll.
- `GoToTab` sets `SelectedConfigTab`. A jump from Search (`OpenTab`, `OpenSection`) brings the group's heading to the top (`ScrollGroupToTop`).
- `SyncSectionSelection` checks the header button of the selected section and the part buttons, by name. `_syncingStrip` keeps the Checked handlers out while it does.
- `ConfigTabControl_PreviewKeyDown` takes Ctrl+Tab and Ctrl+Shift+Tab and calls `CycleSection`, which steps through the sections that show, wrapping. WPF's own Ctrl+Tab would throw on the header-less template (discussion #140).
- `MappingsTabRoot_PreviewKeyDown` takes Ctrl+F: it switches Buttons to the list and focuses `MappingFilterSearchBox`.

### Section and Group Visibility

`SyncTabVisibility()` shows or collapses each group from the slot's type and the selected device's capabilities. `SyncSectionVisibility()` then collapses a section's header button when none of its tabs is available (`FirstAvailableTab` returns -1), so a controller with no gyro, touchpad or IR pointer has no Motion & Touch. `IsTabAvailable` reads `OutputTabVisible` for tab 17, `RumbleAudioTabVisible` for tab 16, and a group's own `Visibility` for the rest. `EnsureSelectedTabAvailable` moves a selection off a tab that has gone, to the first available tab of its section, else to the picture.

| Group | Shown when |
|-------|-----------|
| `TabSticks` | Not a MIDI or VR slot, and the selected row is not output-only |
| `TabTriggers` | Not a MIDI, Keyboard + Mouse or VR slot, not an Extended or Nintendo slot whose profile declares no analog triggers (`ExtendedConfig.TriggerCount == 0`), and the row is not output-only |
| `TabMouse` | The selected device is a mouse (`UserDevice.IsMouse`) |
| `TabForceFeedback` | The device's `CapType` is Gamepad, Joystick, Driving, Flight, FirstPerson or NovintFalcon, or it is a haptic mouse, keyboard or the Razer Sensa row (`PeripheralOutputs.IsHapticPeripheral`) |
| `TabImpulseTriggers` | `UserDevice.HasRumbleTriggers`, or a Flydigi Apex pad (`FlydigiApexService.ModelOf`) |
| `TabAdaptiveTriggers` | A DualSense (product 0x0CE6) or DualSense Edge (0x0DF2), or a Flydigi Apex pad |
| `TabWheel` | The wheel facts report a native wheel, or a wheel card (`hasWheel` or `hasGenericWheel`). `WheelCard` shows on a native wheel only |
| `TabBassShakers` | `RumbleAudioTabVisible`: Xbox, PlayStation and Nintendo slots, and Extended slots with a force-feedback surface |
| `TabGyro` | Any motion sensor (`HasGyro` or `HasAccel`). On an accelerometer-only device the gyroscope cards collapse |
| `TabTouchpad` | `UserDevice.HasTouchpad` |
| `TabPointer` | `UserDevice.HasIrCamera` (a Wii Remote's IR camera) |
| `TabLighting` | A lightbar (DualSense family, DualShock 4, PS Move, or a web controller drawing one), a Guide or HOME LED, or a lit mouse, keyboard or vendor lighting row |
| `TabAudio` | A DualSense, DualSense Edge or DualShock 4 speaker, a Wii Remote speaker (`WiiSpeakerService.DeviceHasSpeaker`), or a device that plays haptic tones (`HapticToneService.DeviceHasHaptics`) |
| Output (tab 17) | `OutputTabVisible`: false on MIDI and VR slots |

`OnPeripheralOutputsChanged` runs the sync again when `PeripheralOutputs.LinksChanged`, `StatusChanged` or `ClaimsChanged`, `FlydigiApexService.Changed` or `PeripheralLightMaps.Changed` fire. `PadPage_Loaded` subscribes these and `SdlDeviceWrapper.RumbleFoundAfterOpen`, and `PadPage_Unloaded` drops them.

### View Mode

The picture in the first section (`FirstSectionName`: Mappings on a gamepad slot) is one of six views in `PictureHost` (AutomationId `ControllerModelHost`). `ApplyViewMode` picks it:

| Slot | Active view | `ViewModeToggle` |
|------|-------------|------------------|
| Keyboard + Mouse | `KBMPreview` ([KBMPreviewView](#kbmpreviewview)) | Hidden |
| MIDI | `MidiPreview` ([MidiPreviewView](#midipreviewview)) | Hidden |
| Extended without dedicated art (`HMaestroProfileCatalog.HasDedicatedArt` false) | `ControllerSchematic` | Hidden |
| VR | `VRPreview` ([VRPreviewView](#vrpreviewview)) | Hidden |
| Any other, `SettingsViewModel.Use2DControllerView` true | `ControllerModel2D` | Shown, icon `F158`, tooltip `Pad_SwitchTo3D` |
| Any other, 3D | `ControllerModel3D` | Shown, icon `E8B9`, tooltip `Pad_SwitchTo2D` |

`ViewModeToggle_Click` flips `Use2DControllerView` and calls `ApplyViewMode`, which then runs `SyncTabVisibility`, `BindActiveModelView` and a pick-ring sync. `BindActiveModelView` unbinds every view and binds the active one, which raises `ControllerElementRecordRequested` for click-to-record (`OnModelRecordRequested`). The 2D and 3D views also raise `AnnotationsToggled` and `AnnotationChipNavigateRequested`. `TouchSensors` (`TouchSensorStrip`) stands over the picture on a Valve slot and is collapsed on every other (see [TouchSensorStrip](2d-overlay-system.md#touchsensorstrip)).

### Buttons Section

The first section maps every control of the virtual controller. One mapping table, two views of it.

```
Grid MappingsTabRoot (3 rows)
├─ ButtonsCardHead (Border, corner 10,10,0,0) > ButtonsTopRow (HeadRowPanel)
│   ├─ ButtonsTopLeft: Picture / List switch (SegmentTrack), ShiftLayerTrack with
│   │    ShiftLayerTabStrip (a ShiftLayerTabChip per PadViewModel.LayerTabs entry) and
│   │    AddShiftLayerButton, PictureHint over the picture
│   └─ ButtonsTopRight: ListTools (MappingFilterSearchBox, MappingDeviceFilterToggle,
│        MappingSurfaceScopeBox), Map All, ListMoreButton (Pad_ListMore)
├─ ListChipsRow: the pipeline chips, and the tips (TipHeader, TipLine)
└─ ButtonsScroll > ButtonsPage (rows set by SyncButtonsLayout)
    ├─ ButtonsCardBody (the card's sides and foot, behind the rows)
    ├─ PictureGround > PictureHost (ControllerModelHost): the six views, TouchSensors,
    │    PickRingLayer (PickRingBand, PickRing), ViewModeToggle
    ├─ PictureLineRow > PictureLine (Pad_PictureLine): the line a recording shows,
    │    ListeningStopButton (Pad_ListeningStop)
    ├─ PictureBar: PickedHead (PickedLetGo, PickedNameText, PickedKindText), PickedBlocks,
    │    PickedLines (the picked control's rows)
    ├─ ListHead (ListHeadLine, ListHeadCells) and MappingDataGrid (the list)
    ├─ ListCellsScroll
    ├─ KbmDeviceBar, ExtendedConfigBar, MidiConfigBar, VrFootNote
    └─ OutputGroup (AutomationId OutputTab): SocdFoldCard, KbmSocdFoldCard, KeepAwakeFoldCard
```

#### Picture View

The picture keeps its height, and the picked control's rows and the output cards sit under it in a page that scrolls (`SyncButtonsLayout`). A click on a control in the picture picks it (`PictureHost_PreviewMouseLeftButtonDown`, `PictureHost_MouseLeftButtonUp`): `PadViewModel.PickedTarget` names it, the ember `PickRing` stands around it, and `PictureBar` shows its name (`PickedName`), kind (`PickedKind`, such as `Pad_Kind_FaceButton`) and rows (`PickedRow`). A click that lands on no control lets go of the pick, as do `PickedLetGo` (`PickedLetGo_Click`) and Escape (`PadPage_KeyDown`, unless a text box owns the key). `PictureLine` shows while a recording listens, with `ListeningStopButton`. `PictureHint` says how to map a control (`PictureHintText`, in the words of the slot's picture).

#### List View

`MappingDataGrid` (name `Pad_Mappings`) lists every row, grouped (`ListGroupTitle`, `ListGroup_Toggled`). A row's template (`DGR_Border`) holds `RowLine` and `RowCells`, a `CombineTag`, `RowChevron`, the live `Rowfire`, and `RowBody`, which opens under the row with its sources. `MappingRow_PreviewMouseLeftButtonDown`, `MappingRowToggle_Click` and `MappingRow_PreviewKeyDown` open and close a row, and `RecordFlash` flashes while it records. The list fills the page and scrolls its own rows (`MappingDataGrid_PreviewMouseWheel`, `MappingDataGrid_ScrollChanged`).

- The filter box `MappingFilterSearchBox` and the device-visibility popup (`MappingDeviceFilterToggle`, `DeviceFilterPopup_Opened`, `DeviceFilterPopup_KeyDown`) filter the slot's shared choice view, so every picker offers less without changing any binding (#322).
- `MappingSurfaceScopeBox` narrows a Keyboard + Mouse slot that drives both halves to its keyboard or mouse rows (`KbmSurfaceScopeVisible`).
- Map All (`MapAllButtonText`, `MapAllToggle_Click`) starts Map All, or stops it while it runs. On a VR slot `VrFootNote` reads `Pad_Vr_MapAllSkipsTouch`.
- `ListMoreButton` (`Pad_ListMore`) opens the first four items of the header's More menu through the same commands.
- The pipeline chips in `ListChipsRow` (`PipelineChip_Click`) name each transform that rewires the slot's input: Curve, Gyro, Shift Layers, Inverted and Deadzone. A chip shows while its pipeline has configuration, its flame fills while an owning row is live, and a click scrolls to the owning row, cycling through several. Shift Layers cycles the layer chips instead.
- The layer chips (`ShiftLayerTab_Click`, `AddShiftLayer_Click`) hide while only Base exists. Each chip's context menu runs Configure, Rename, Copy, Paste, Clear and Delete (`ShiftLayer_Configure_Click`, `ShiftLayer_Rename_Click` with `RenameLayerPopup`, `ShiftLayer_Copy_Click`, `ShiftLayer_Paste_Click`, `ShiftLayer_Clear_Click`, `ShiftLayer_Delete_Click`).

#### Source Lines and Shaping

A row's sources stand in `SourceLine` templates (`SourceLinePanel`). Under each source the `SourceShaping` template shows its gates and shaping, each with a `SettingResetButton`:

| Row | String | Binding | Shown when |
|-----|--------|---------|-----------|
| Only While | `Mapping_Gate` | `GatePick` (a picker over `SlotAvailableInputsView`) with `GateText` drawn inside it (`PickerWords`), `ResetGateDescriptorCommand` | `HasGate` |
| And While | `Mapping_Gate2` | `Gate2Pick` with `Gate2Text` inside it, `ResetGate2DescriptorCommand` | `HasGate2` |
| Curve | `Mapping_SourceCurve` | `ParamCurveExponent` (0 to 5, step 0.05), `ResetParamCurveExponentCommand` | `IsShapingShown` |
| Outer Range | `Mapping_SourceOuterRange` | `ParamRangeOuterPercent` | `IsShapingShown` |
| Anti-Deadzone | `Mapping_SourceAntiDeadzone` | `ParamAntiDeadzonePercent` | `IsShapingShown` |
| Deadzone Shape | `Mapping_SourceDeadZoneShape` | `ParamStickDeadZoneShape` | `IsShapingShown` |
| Inner Deadzone | `Mapping_SourceInnerDeadzone` | `ParamStickDeadZoneInnerPercent` | `IsShapingShown` |

The template's data is the source's `ShapingHolder`: the row or an added source, or the row's mode holder when the first source reads keys. The values are `MappingSource.ParamCurveExponent`, `ParamRangeOuter`, `ParamAntiDeadzone`, `ParamStickDeadZoneShape`, `ParamStickDeadZoneInner`, `GateDescriptor` and `Gate2Descriptor`.

#### Slot Bars

| Bar | Shown on | Contents |
|-----|----------|----------|
| `KbmDeviceBar` | Keyboard + Mouse (`ShowKbmFoot`) | `KbmKeyboardDeviceCombo` and `KbmMouseDeviceCombo` (bound to `KbmConfig.AvailableKeyboardDevices` / `AvailableMouseDevices`), each with its reset (`Reset_PadViewModel_KbmKeyboardDevice`, `Reset_PadViewModel_KbmMouseDevice`) |
| `ExtendedConfigBar` | Extended, picture view (`ShowExtendedCard`) | `ExtendedResetDefaultsBtn`, `ExtendedImportBtn`, `ExtendedCloneBtn`, `ExtendedCustomizeChk` and the custom rows: `ExtendedProductStringBox`, `ExtendedOemOverrideChk`, `ExtendedVidBox`, `ExtendedPidBox`, `RawStickCountBox`, `ExtendedTriggerCountBox`, `RawPovCountBox`, `RawButtonCountBox`, `ExtendedForceFeedbackChk`. `ExtendedCustomValue_Changed` and `_KeyDown` apply clamped values on LostFocus and Enter |
| `MidiConfigBar` | MIDI, picture view (`ShowMidiCard`) | `MidiOutputPortBox` (AutomationId `MidiOutputPortBox`, reset `Reset_PadViewModel_MidiOutputPortBox`), `MidiChannelBox`, and under `MidiMore` (`Pad_More_Midi`) `MidiCcCountBox`, `MidiStartCcBox`, `MidiNoteCountBox`, `MidiStartNoteBox`, `MidiVelocityBox`. `MidiOutputPortBox_DropDownOpened` reads the ports again, `MidiOutputPortBox_SelectionChanged` writes the pick through `MidiConfig.ChooseOutputPort`, `MidiConfig_Changed` and `_KeyDown` apply clamped values and rebuild the mappings when counts change |
| `VrFootNote` | VR, picture view (`ShowVrFoot`) | `Pad_Vr_MapAllSkipsTouch` |

#### Output Cards

`OutputGroup` (a `GroupBox` in `BareGroupBox`, AutomationId `OutputTab`, name `Pad_Tab_Output`) shows under the picture while `ShowOutputGroup` is true. It holds three `FoldCard`s in a `FoldList`: `SocdFoldCard` (`Pad_Socd_FoldTitle`, "SOCD", state key `Pad.Output.Socd`, the gamepad SOCD pairs of `MappingSet.SocdMode` and `SocdPairs`, hidden on Keyboard + Mouse and MIDI), `KbmSocdFoldCard` (the same title, `Pad.Output.KbmSocd`, its Keyboard + Mouse twin) and `KeepAwakeFoldCard` (`Pad_KeepAwake_Card_Header`, "Keep Controller Awake", `Pad.Output.KeepAwake`).

### Sticks Section

`SticksSectionScroll` defines the section's row styles in its resources: `DzLabel` (150 wide, wrapping), `DzFirstLabel` (the first rows' label column, `FirstRowLabelWidth`), `DzSlider` (0 to 100, ticks of 0.1, on `EmberSlider`), `OffsetSlider` (from -100), `DzValueEdit`, `DzDigitEdit` (58 wide, tooltip `Pad_RawAxisValue`), `DzPercent` and `CardSubsectionTitle`. `PadPage.SizeFirstRows` sets `FirstRowLabelWidth` (96 to 150), `FirstRowSettingsMost` and `StickLiveLeast` for the language.

| Group | Cards |
|-------|-------|
| `TabSticks` | One card per stick (an `ItemsControl` over the stick configs, title `HeroCardTitle` from the item): a head with Reset All and a summary over a `PartBodyPanel` of the first settings and the live view, with the `CurveEditor` charts below. The settings hold the center point (`CalibrateCenter_Click`), deadzone, range, the steering modes (with the Stick Deadzone row `Pad_Steering_StickDeadZone`, `SteerStickDeadZone`, 0 to 90) and the sensitivity curves (`StickPresetX_SelectionChanged`, `StickPresetY_SelectionChanged`, `StickPresetBoth_SelectionChanged`, `SensitivityXCombo`, `DeadZoneShapeCombo`). Then `BothSticksCard` (`Pad_BothSticks_Header`, "Both Sticks"), `LockFeedbackCard` (`Pad_Steering_LockFeedback`, "Steering Lock Feedback", shown while a lock channel exists) and `FlickStickCard` (`Pad_FlickStick_Header`, "Flick Stick", Keyboard + Mouse slots only) |
| `TabTriggers` | One card per trigger: a `PartBodyPanel` with the Range slider (`RangeSlider`), Anti-Deadzone and Sensitivity (`TriggerPreset_SelectionChanged`, `TriggerPresetCombo`) beside a `CurveEditor` chart, and a `MoreRow` (state key from `TriggerConfigItem.MoreStateKey`) with the typed range and raw values |
| `TabMouse` | `Pad_MouseGestures_Header` ("Mouse Gestures"), a mouse's per-device gesture settings |

### Rumble Section

| Group | Cards |
|-------|-------|
| `TabForceFeedback` | `FalconCard` (`Pad_Falcon_Header`, "Novint Falcon", `SyncFalconCard`), the Force Feedback card (`Pad_ForceFeedback_Header`) with its motor activity rows (`Pad_MotorActivity`: `DeviceLeftMotorDisplay` and `DeviceRightMotorDisplay` as live bars, a click on a bar runs `LeftMotor_Click` or `RightMotor_Click` to test that motor) and the constant-force pad (`ConstantForcePad_MouseLeftButtonDown`, `_MouseMove`, `_MouseLeftButtonUp`), `AudioRumbleFoldCard` (`Settings_AudioRumble`, "Audio Rumble", `Pad.Rumble.Audio`) and `TriggerRoutingFoldCard` (`Pad_TriggerRouting_Header`, "Trigger Routing", `Pad.Rumble.TriggerRouting`). `PeripheralHapticsRoute` says where a haptic peripheral's rumble comes from |
| `TabImpulseTriggers` | The Impulse Triggers card (`Pad_ImpulseTriggers_Header`, its title's tooltip `Pad_ImpulseTriggers_Subtitle` or, on a Flydigi pad, `Pad_ImpulseTriggers_Subtitle_Flydigi`) with live trigger-motor bars, and `AudioTriggerRumbleFoldCard` (`Pad_AudioTriggerRumble_Header`, "Audio Bass Trigger Rumble") |
| `TabAdaptiveTriggers` | The Adaptive Triggers card (`Pad_AdaptiveTriggers_Header`), its effect cards and `TriggerEffectGraph` previews |
| `TabWheel` | `WheelCard` (`Pad_Wheel`, "Wheel", native wheels) and `CenteringCard` (`Pad_Centering`, "Centering"): Mode with Vehicle (`CenteringIsVehicle`, `CenteringVehicleAvailable`), Speed (From the Game or Fixed Speed), Grip (Dry, Wet, Snow, Ice), Steering Weight, Power Assist, On-Center Feel, Damping, Friction (shown on `CenteringFrictionShown`, hidden on a wheel with no friction effect, `CenteringFrictionNm` 0 to 1.5), Peak Torque, Torque Stiffness, Linearity, Wheel Range (`CenteringWheelRangeShown`), the Steering Torque chart (`SteeringTorqueChart`) and live readout (`CenteringLiveShown`, `SyncCenteringLiveTimer`), and Release Test (`Pad_Centering_ReleaseTest`, `CenteringReleaseTest_Click`, which opens [ReleaseTestDialog](#releasetestdialog)) |
| `TabBassShakers` | `Pad_RumbleAudio_Header` ("Bass Shakers"), the slot's audio endpoints (`RumbleAudioEndpoint_DropDownOpened` fills the picker) and live meters (`SyncBassShakerMeterTimer`, `UpdateBassShakerMeters`) |

### Motion Section

| Group | Cards |
|-------|-------|
| `TabGyro` | `GyroCard` (`Pad_Gyro_Header`, "Gyro"), `GyroPassthroughCard`, `GyroCalibrationCard`, `GyroSensitivityCard`, then fold cards: `GyroGripCard` (`Pad_Gyro_Grip_Header`, "Grip"), `GyroEngageCard` (`Pad_Gyro_Engage_Header`, "Engage"), `GyroResponseCard` ("Response Shaping"), `GyroSpaceCard` ("Reference Frame"), `MotionSteeringFoldCard` ("Motion Steering"), `GyroTiltFoldCard` ("Gyro Tilt"), `GyroSimulationCard` ("Pitch and Roll Simulation", shown where the pad's gyro is simulated) and `CompassYawCard` ("Compass", shown on a Switch 2 controller with a magnetometer). The gyroscope cards collapse on an accelerometer-only device |
| `TabTouchpad` | `TouchpadCard` (`Pad_Touchpad_Header`, "Touchpad"), then fold cards: `TouchpadStickFoldCard` ("Stick / D-Pad Output"), `TouchpadPointerFoldCard` ("Absolute Pointer"), `SyntheticPressureFoldCard` ("Synthetic Pressure"), `SwipeHapticsFoldCard` ("Swipe Haptics"), `GestureDetectionFoldCard` ("Gesture Detection"), `InBoxGesturesFoldCard` ("In-Box Gestures") and `CustomGesturesFoldCard` ("Custom Gestures", recorded through [TouchpadGestureRecorderDialog](#touchpadgesturerecorderdialog)) |
| `TabPointer` | `IrPointerCard` (`Pad_Pointer_Header`, "IR Pointer"), a Wii Remote's IR camera tuning |

The Engage card holds the gyro's activation rows, each with its reset: `Settings_GyroAimEngageMode` (Hold, Toggle, Release to Aim), then Layer (`Pad_GyroActivation_Layer`, which only picks the layer the rows below show, so it stores nothing and has no reset, shown while `HasShiftLayers`), Gyro On (`Pad_GyroActivation`, `GyroActivationMode`), Gyro On Buttons (`Pad_GyroActivation_Buttons`, a list over `GyroActivationButtons`, shown while `GyroActivationUsesButtons`), Needs (`Pad_GyroActivation_Needs`, `GyroActivationNeeds`) and Re-Center When Gyro Turns On (`Pad_GyroRecenterOnEngage`, `GyroRecenterOnEngage`). They edit `PadSetting.GyroActivation` through `PadViewModel.GyroActivation.cs`.

### Lights Section

| Group | Cards |
|-------|-------|
| `TabLighting` | `LightingCard` (`Pad_Lighting_Header`, "Lighting"), `LightbarModeCard` (the mode picker, shown for a lightbar or a lit peripheral), `IndicatorLedsCard` ("Indicator LEDs", DualSense family), `PeripheralLightingCard` ("Lighting Control", a lit peripheral that is not a vendor lighting row), `GuideLedCard` ("Guide Button LED"), `LedStripsCard` ("LED Strips") and `KeyColorsCard` (its title from `KeyColors.Title`) |
| `TabAudio` | `AudioCard` (`Pad_Audio_Header`, "Audio"), then `CrossfeedFoldCard` ("Crossfeed"), `ParametricEqFoldCard` ("Parametric EQ"), `LimiterFoldCard` ("Limiter"), `SoundMacrosFoldCard` ("Sound Macros") and `SoundPackagesFoldCard` ("Sound Packages") |

On a mouse, keyboard or vendor lighting row, `LightbarModeCard` stays, the DualShock 4 and DualSense preview art collapses, and the peripheral parts show. `SyncKeyColorsCard` and `SyncLedStripsCard` attach `KeyColors` and `LedStrips` for the lighting row and show or collapse their cards. `KeyColorLayer_Click` sets `KeyColors.SelectedLayerMask`, `KeyColorSwatch_Click` sets `KeyColors.PaintHex` from the swatch's `Tag`, and `KeyColorsHexBox_KeyDown` pushes the hex box on Enter. The lightbar's own hex box and swatches run `LightbarHexBox_KeyDown`, `LightbarHexBox_LostFocus` and `LightbarSwatch_Click`, and `SyncLightbarPreview` draws its preview. `ScreenColorDisplayBox_SelectionChanged` writes the Screen Color display to `DeviceConfig.ScreenColorDisplay`, and `SyncScreenColorStatus` refreshes the display list and status line on a one-second timer while Screen Color shows.

### Macros Section

`MacrosSectionScroll` holds two columns that wrap: `MacrosListCard` (the macro list `MacroList` with `MacroAddButton` and `MacroListMoreButton`, and the menu list `MenuList` with `MenuAddButton`, each list's head being its part switch, `TabMacros` or `TabMenus`) and `MacrosEditorColumn` with `MacrosEditorCard`, whose own header-less `ContentTabControl` shows the macro editor (`MacroEditorHost`, bound to `SelectedMacro`) or the menu editor. A dot before each list entry is ember while the macro or menu is on. Under the menu editor stands `IconPackagesFoldCard` (`Pad_Menus_IconPackages_Header`, "Icon Packages").

The macro editor's head carries `MacroMoreButton` (`Pad_More_Macro`), the trigger recorder (`MacroClearTrigger`, `MacroTriggerPick_PreviewKeyDown`, `MacroTriggerPick_SelectionChanged`) and `MacroRemoveButton`. Its action steps drag to reorder (`ActionsList_PreviewMouseLeftButtonDown`, `_PreviewMouseMove`, `_DragOver`, `_Drop`, `_PreviewKeyDown`). The menu editor carries `MenuMoreButton` (`Pad_More_Menu`), `MenuRemoveButton`, the cells (`MenuAddCell`, `MenuRemoveCell`, `MenuCellChooseIcon_Click` opening [IconPicker](#iconpicker)), the Hotbar style's rows (`MenuHotbar_Show`, `MenuHotbar_Previous`, `MenuHotbar_Next`, `MenuHotbar_Fire`, `MenuHotbar_Recenter`, `MenuHotbar_Wrap`, `MenuHotbar_DismissOnFire`) and the Keyboard style's rows (`MenuKeyboard_OpensWith`, `MenuKeyboard_EngageDeadzone`), each with a reset `Reset_MenuEditorItem_*` or `Reset_MenuCellItem_*`.

### Resources and Styles

`UserControl.Resources` (about 2,000 lines) holds the page's shared styles and templates. Among them: `ResetButton` and `ResetButtonTight` (per-row reset), `SectionStripButton`, `SectionIcon` and `SectionIconShape`, `ListHeadSwitch`, `ListHeadButton`, `RowIconButton`, `RowActionButton`, `ShiftLayerTabChip`, `LineGroup`, `LineLabel`, `LineSlider`, `LinePicker`, `LineInputPicker`, `InputGroupHead`, `SourceLine`, `SourceModeSettings`, `SourceDials`, `SourceShaping`, `MappingRowPanel`, `FormulaChipStyle`, `FormulaPresetStyle`, `ListCellsPanelTemplate`, `ListCell`, `ListColumnHead`, `StepItem`, `StepButton`, `CellItem`, `CardNumberBox`, `LiveNumber`, `FieldValueEdit`, `FieldUnit`, `BareGroupBox` and the `AtMode*` steering-lock templates. `ResetAllButton` is in `App.xaml`.

### UI Automation Ids

| AutomationId | Element |
|--------------|---------|
| `Section_Buttons`, `Section_Sticks`, `Section_Rumble`, `Section_Motion`, `Section_Lights`, `Section_Macros` | The six section buttons |
| `TabController`, `MappingsTab` | Buttons' Picture and List |
| `MacrosTab`, `MenusTab` | Macros & Menus' two parts |
| `OutputTab` | The output cards' group |
| `Pad_SlotPower`, `Pad_More`, `Pad_DeleteController`, `Pad_DrivenByList`, `Pad_AddDevice`, `Pad_SteamVrState` | The header |
| `HMaestroProfileCombo`, `KbmSurfacesCombo` | The Preset pickers |
| `AssignOfferBanner`, `AssignOfferAccept`, `AssignOfferDismiss` | The assignment offer |
| `ControllerModelHost`, `ViewModeToggle`, `TouchSensors` | The picture |
| `Pad_ListMore`, `Pad_PictureLine`, `Pad_ListeningStop`, `Pad_PickedLetGo` | The first section's tools |
| `KbmKeyboardDeviceCombo`, `KbmMouseDeviceCombo`, `RawStickCountBox`, `ExtendedTriggerCountBox`, `RawPovCountBox`, `RawButtonCountBox`, `MidiOutputPortBox` | The slot bars |
| `DeadZoneShapeCombo`, `SensitivityXCombo`, `TriggerPresetCombo` | Sticks & Triggers |
| `MacroList`, `MacroAddButton`, `MacroRemoveButton`, `MenuList`, `MenuAddButton`, `MenuRemoveButton` | Macros & Menus |
| `Reset_{Class}_{Property}_{n}` | `SettingResetButton`s, the numeric suffix keeping each unique |

### Event Handlers (Code-Behind)

| Handler | Trigger | Action |
|---------|---------|--------|
| `PadPage_Loaded` | Loaded | `SizeFirstRows`, `ApplyViewMode`, `SyncSectionSelection`, the Extended and MIDI bar syncs, the lightbar, Screen Color and audio hex syncs, the sound and icon package registries, the Bass Shakers and Centering timers, and the peripheral subscriptions |
| `OnDataContextChanged` | DataContextChanged | Moves the view-model subscriptions to the new pad and syncs everything |
| `OnPadVmPropertyChanged` | `PadViewModel.PropertyChanged` | Follows `SelectedConfigTab`, `OutputType` and the other properties the page draws from |
| `SectionBtn_Click`, `SectionBtn_Checked` | Section buttons | `GoToSection` |
| `TabBtn_Click`, `TabBtn_Checked` | Part buttons | `GoToTab` |
| `ConfigTabControl_PreviewKeyDown` | Ctrl+Tab | `CycleSection` |
| `SlotPower_Click`, `AddDevice_Click`, `DeleteController_Click`, `MoreMenu_Click`, `ClearAllMappings_Click` | Header | As in the header table |
| `ViewModeToggle_Click` | `ViewModeToggle` | Flips `Use2DControllerView`, `ApplyViewMode` |
| `MapAllToggle_Click` | Map All | Starts or stops Map All |
| `PictureHost_*`, `PickedLetGo_Click`, `ListeningStop_Click` | The picture | Picks a control, lets go, stops listening |
| `PipelineChip_Click` | Pipeline chips | Scrolls to the owning row |
| `CalibrateCenter_Click` | A stick's center row | `StickConfigItem.StartCalibration()` |
| `LeftMotor_Click`, `RightMotor_Click` | The Force Feedback card's motor activity rows | Test the device's motor |
| `CenteringReleaseTest_Click` | Release Test | Opens [ReleaseTestDialog](#releasetestdialog) |
| `AppVolumeProcessDropDown_Opened`, `DeviceAxisPicker_DropDownOpened`, `DeviceAxisIndexPicker_DropDownOpened`, `MicLedDevicePicker_DropDownOpened`, `MirrorSource_DropDownOpened` | Pickers | Fill the picker when it opens |
| `ResetExtendedSetting_Click`, `ResetMidiSetting_Click` | Bar resets | Reset the field named by the button's `Tag` (`PadPage.SettingResets.cs`) |

### Copy From Dialog

`CopyFromCommand` opens [CopyFromDialog](#copyfromdialog). See there.

---

## ExtrasPage

**Files:** `Views/ExtrasPage.xaml`, `Views/ExtrasPage.xaml.cs`, with `Controls/ExtraTile.cs` and `Controls/ExtraMarks.cs`

Extras holds the optional features the Dashboard's Services section held in PadForge 5: a catalog of tiles, and one page per extra. Its `DataContext` is `DashboardViewModel`, the same instance as Home's, so an extra's switch on its tile, on its page and on Home's Extras in Use is one setting. The crosshair and magnifier parts of the view model are `DashboardViewModel.Crosshairs.cs`.

### Layout Structure

```
ScrollViewer PageScroll
└─ StackPanel (Margin 36,26,36,36)
    ├─ CatalogView (ExtraTile.OpenRequested = Tile_OpenRequested, Heat.IsLive = IsEngineOn)
    │   ├─ CatalogHead: Extras_Title (heading 1), Extras_Subtitle, OnCountText (Extras_OnCount)
    │   ├─ Extras_Group_Play ("More Ways to Play"): TileGridPanel of four tiles
    │   ├─ Extras_Group_Send ("Send It Elsewhere"): three tiles
    │   └─ Extras_Group_Screen ("On Screen"): five tiles
    └─ one StackPanel per extra, named <Key>Page, Collapsed until shown
```

Each group is a `TileGridPanel` (`MinItemWidth` 240, gap 14, `FillRows`, `Balance`, so four tiles that do not fit one row stand two and two). `OnCountText` is three runs (`ExtrasOnLead`, `ExtrasOnNumber` in the display face, `ExtrasOnTail`), its accessible name `ExtrasOnSpoken`, built from `Extras_OnCount_Format` ("{0} of {1} on").

| Group | Tile (`x:Name`) | Key | Title | On while |
|-------|-----------------|-----|-------|----------|
| More Ways to Play | `WebControllerTile` | `WebController` | `Dashboard_WebController` ("Web Controller") | `EnableWebController` |
| | `HeadTrackingTile` | `HeadTracking` | `Dashboard_HeadTracking` ("Head Tracking") | `HeadTrackingAnyEnabled` |
| | `GameTelemetryTile` | `GameTelemetry` | `Dashboard_GameTelemetry` ("Game Telemetry") | `EnableGameTelemetry` |
| | `TwitchChatTile` | `TwitchChat` | `Dashboard_TwitchChat` ("Twitch Chat") | `EnableTwitchChat` |
| Send It Elsewhere | `RemoteLinkTile` | `RemoteLink` | `Dashboard_RemoteLink` ("Remote Link") | `EnableRemoteLink` |
| | `MotionServerTile` | `MotionServer` | `Dashboard_MotionServer` ("Motion Server") | `EnableDsuMotionServer` |
| | `GameModsTile` | `GameMods` | `Dashboard_GameMods` ("Game Mods") | `EnableGameModServer` |
| On Screen | `OverlaysTile` | `Overlays` | `Dashboard_Overlays` ("Overlays") | `OverlaysAnyEnabled` |
| | `TouchpadOverlayTile` | `TouchpadOverlay` | `Dashboard_TouchpadOverlay` ("Touchpad Overlay") | `EnableTouchpadOverlay` |
| | `ScreenOverlayTile` | `ScreenOverlay` | `Dashboard_ScreenOverlay` ("Screen Overlay") | `ScreenOverlaysAnyEnabled` |
| | `CrosshairTile` | `Crosshair` | `Extras_Crosshair_Title` ("Crosshair") | `CrosshairsAnyEnabled` |
| | `MagnifierTile` | `Magnifier` | `Extras_Magnifier_Title` ("Magnifier") | `MagnifierEnabled` |

`ExtrasPage.Keys` lists the twelve keys in this order, and Home's Extras in Use follows it. An `ExtraTile` carries the extra's switch (its `IsOn` is the extra's own setting), a glyph, a line, the live status in place of the word On, and is lit while its extra is on and the engine runs. A click anywhere else on a tile raises the routed `ExtraTile.OpenRequested`, handled once for the catalog by `Tile_OpenRequested`.

### Navigation

| Member | What it does |
|--------|--------------|
| `Show(key)` | Shows `<key>Page` and collapses the catalog and the other pages, or shows the catalog for null. An unknown key changes nothing and returns false. Sets `CurrentExtra` and scrolls to the top |
| `ShowCatalog()` | Shows the catalog and puts keyboard focus on the tile of the extra the user came from |
| `Tile_OpenRequested` | Opens the tile's page and moves focus to the page's first control |
| `Back_Click` | Each page's crumb (`Extras_Back_<Key>`, the `ExtrasCrumb` style: the word Extras, a slash, then the extra's title) returns to the catalog |
| `BackCommand` | Alt+Left and the keyboard's Back key return to the catalog while a page shows. Backspace does not, since it would leave a page from a read-only address box |
| `OnPreviewMouseDown` | The mouse's Back button (XButton1) returns to the catalog |

`MainWindow` calls `ShowCatalog()` when the user arrives at Extras from another page, and `Show(key)` when Home's Extras in Use opens an extra.

### Extra Pages

Each page has the crumb, a head with an `ExtraBadge` (the extra's glyph, steel while off and warm while on) and the title at heading level 1, a status card with a `StatusFlame` (outline while off, gold while on and waiting, ember while it works), the cards of its settings, and often a `MoreRow` (`Extras_More_<Key>`) for the less used ones. Every setting keeps its reset button.

| Page | Settings and controls (bindings on `DashboardViewModel`) |
|------|-----------------------------------------------------------|
| `WebControllerPage` | `EnableWebControllerCheckBox` (`EnableWebController`), the address with `WebController_CopyAddress` (`CopyWebControllerUrlCommand`), the QR and the phones list (`WebControllerPhones`, `WebController_Phones`). Under More: `WebControllerPort` (`ResetWebPortCommand`), `EnableWebControllerPlainHttpCheckBox`, `WebControllerPlainHttpPort` (`ResetWebPlainPortCommand`), `WebControllerPlainHttpLocalOnlyCheckBox`, `WebControllerAccessCodeBox`, `NewWebAccessCodeButton` (`NewWebAccessCodeCommand`) and `WebController_CopyPlainAddress` (`CopyWebControllerPlainUrlCommand`) |
| `HeadTrackingPage` | `HeadTrackingSwitch` (`HeadTrackingAnyEnabled`), Set Neutral (`HeadTrackingRecenterCommand`), the sources `HeadTrackingUdpCheckBox`, `HeadTrackingFreeTrackCheckBox`, `HeadTrackingOpenXrCheckBox` with Reset All (`Extras_ResetAll_HeadTrackingSources`), the ranges `HeadTrackingRotationRange` and `HeadTrackingTranslationRange` with Reset All (`Extras_ResetAll_HeadTrackingRange`). Under More: `HeadTrackingUdpPort`, `HeadTrackingOpenXrRuntimeCombo` (`OpenXrRuntimes`, `SelectedOpenXrRuntime`) and the six per-axis ranges `HeadTrackingRangeYaw` to `HeadTrackingRangeZ`. Its note links to Devices (`Extras_Link_HeadTracking`, `DevicesLink_Click`) |
| `GameTelemetryPage` | `EnableGameTelemetry`, the game picker (`GameTelemetryOptions`, `SelectedGameTelemetryOption`). Under More: `GameTelemetryPort`, `GameTelemetryForwardPort`, `GameTelemetryFullSpeed`, and Custom Formats… (`GameTelemetryFormatsButton_Click`, which opens [CustomTelemetryFormatsDialog](#customtelemetryformatsdialog) over `GameTelemetryFormats` and writes back its `Result`). Its note links to Devices (`Extras_Link_GameTelemetry`) |
| `TwitchChatPage` | `EnableTwitchChat`, the channel, the `!claim` approval (`TwitchChatClaimApprovalIndex`), Manage Chat Commands (`TwitchChat_ManageCommands`, `ManageChatCommands_Click`, [ChatCommandsDialog](#chatcommandsdialog)), the streamer's buttons (`TwitchChatPauseCommand`, which reads Pause or Resume on `TwitchChatPaused`, `TwitchChatSkipCommand`, `TwitchChatClearCommand`, `TwitchChatEndClaimCommand`) and the broadcast picture's address (`TwitchChat_CopyAddress`, `CopyTwitchChatDisplayUrlCommand`) |
| `RemoteLinkPage` | `EnableRemoteLinkCheckBox` (`EnableRemoteLink`), the paired PCs (`RemoteLink.TrustedPeers`: rename through `PeerRename_Click` and `PeerName_KeyDown`, `AllowRemoteAssignments`, `ConnectCommand`, `AssignmentsCommand`, `RevokeCommand`) and Revoke All (`RemoteLink.RevokeAllPeersCommand`), nearby PCs (`RemoteLink.NearbyUnpaired`, `PairCommand`), this PC's code (`CopyRemoteLinkCodeCommand`). Under More: `AutoReconnect`, `RemoteLinkPort`, the pairing identity (`RemoteLink.IdentityProtectionModes`, `RemoteLink.IdentityProtectionModeIndex`) and connect by address (`ConnectToPeerCommand`). `RemoteLink` is the `SettingsViewModel` instance |
| `MotionServerPage` | `EnableDsuMotionServer`. Under More: `DsuMotionServerPort` (`ResetDsuPortCommand`) |
| `GameModsPage` | `EnableGameModServer`. Under More: `GameModServerPort` (`ResetGameModPortCommand`) and `GameModDsxStandIn` |
| `OverlaysPage` | `OverlaysSwitch` (`OverlaysAnyEnabled`) with Reset All (`Extras_ResetAll_Overlays`, `ResetOverlaysCommand`), and `EnableMenuOverlay`, `EnableShiftLayerFlyout`, `EnableProfileOverlay`, each with a preview (`OverlaysPreviewMenu`, `OverlaysPreviewShift`, `OverlaysPreviewProfile`). Its note links to Macros & Menus (`Extras_Link_Overlays`, `MenusLink_Click`, which opens the first controller's menus) |
| `TouchpadOverlayPage` | `EnableTouchpadOverlay`, `TouchpadOverlayOpacity` (`ResetOpacityCommand`), Reset Position (`ResetTouchpadOverlayPositionCommand`) and Reset All (`Extras_ResetAll_TouchpadOverlay`) |
| `ScreenOverlayPage` | Add Overlay (`ScreenOverlay_Add`, `AddScreenOverlayCommand`) and one group per `ScreenOverlays` item: Enabled, Opacity, Choose What It Shows… (`ChooseCommand`), Reset Position, Remove and Reset All, with AutomationIds set from the item (`EnableId`, `OpacityId`, `ChooseId`, `ResetPositionId`, `RemoveId`, `ResetAllId`) |
| `CrosshairPage` | Add (`Crosshair_Add`, `AddCrosshairCommand`) and one group per `Crosshairs` item: Enabled, Style (`StyleNames`, `StyleIndex`), Display (`DisplayChoices`, `Display`), Length, Radius, Sides, Thickness, Gap, Center Dot, T Shape, Dot Size, a picture (`CrosshairPicture_Click`, `OwnSizeCommand`, `KeepProportions`), Opacity, Outline and its thickness, Rotation and Smooth Edges |
| `MagnifierPage` | Bound to `Magnifier` (a `MagnifierItem`): `Magnifier_Enable`, Reset All (`Extras_ResetAll_Magnifier`), `Magnifier_Mode`, `Magnifier_Follow`, `Magnifier_Display`, `Magnifier_Zoom` (`ZoomPercent`), `Magnifier_Shape`, `Magnifier_LensWidth` and the height, the border and its thickness, and the spotlight's size and dim |

The Screen Overlay's Choose What It Shows… raises `ChooseScreenOverlayContentRequested`, which `MainWindow.ConfigureScreenOverlay` answers with [KeyboardScreenDialog](#keyboardscreendialog). `FollowDisplays` refreshes the display lists while the page is visible.

`ScreenOverlayItem` (`ViewModels/ScreenOverlayItem.cs`) is one overlay. Its `Number` is its identity and stays when another overlay is removed, so a macro that names overlay 3 keeps meaning the same window. A new overlay takes the lowest free number (`DashboardViewModel.AddScreenOverlay`), up to `KeyboardScreenInfo.MaxOverlays` (8). The window itself is [ScreenOverlay](#screenoverlay).

---

## DevicesPage

**Files:** `Views/DevicesPage.xaml`, `Views/DevicesPage.xaml.cs`. Its view model is `DevicesViewModel` (with `DevicesViewModel.List.cs` and `DevicesViewModel.Board.cs`), each row a `DeviceRowViewModel`.

The list of every device PadForge knows, and a panel for the picked one. `DevicesPage.InputService` is a static reference `MainWindow` sets, which the gyro calibration and other per-device buttons reach through.

### Layout Structure

```
Grid PageRoot
├─ HeaderRow: DevicesTitle, DevicesSubtitle, PairButton (Devices_Pair, PairCommand),
│    RefreshButton (Devices_Refresh, RefreshCommand)
├─ FilterRow: DeviceSearchBox (Devices_Search, SearchText), ShowSegments, ConnectionSegments
└─ BodyScroll > BodyGrid (columns: the list, PanelColumn 408)
    ├─ DeviceListCard (CardBorder)
    │   ├─ ListHead: MainHeading and the column heads Devices_Detail_Link, Devices_Detail_Battery,
    │   │    Devices_UsedBy
    │   ├─ NoMatchLine (Devices_NoMatch)
    │   ├─ MainList (Devices_List_Main, ItemsSource MainView, grouped)
    │   ├─ NotConnectedFold (Devices_Fold_NotConnected, state key Devices.NotConnected)
    │   │    > NotConnectedList (Devices_List_NotConnected)
    │   └─ the drag hint (Devices_DragAssignHint)
    └─ PanelScroll (Devices_PanelScroll) > DevicePanel
        ├─ EmptyCard: shown while no device is picked
        └─ SelectedPanel
            ├─ IdentityCard: DeviceStage (150 tall), the name, LinkTile, BatteryTile, Used By
            ├─ TestCard: Test Inputs
            ├─ SettingsCard: the device's settings
            └─ DetailsCard (FoldList) > DetailsFold (Devices_Details, state key Devices.Details)
```

The show filter (`ShowSegments`) is a `SegmentTrack` of `SegmentRadio`s on `DevicesViewModel.Filter`: All, Gamepad, Joystick, Wheel, Keyboard, Mouse and Other (`Devices_Filter_All` to `Devices_Filter_Other`, the `DeviceFilter` enum, handled by `Filter_Checked`). The connection filter (`ConnectionSegments`) picks All, Connected or Not Connected (`Devices_Connection_All`, `_Connected`, `_NotConnected`, `Connection_Checked`). `MainView` is a `ListCollectionView` grouped by `DeviceRowViewModel.Section` (`PropertyGroupDescription`, `CustomSort = DevicesViewModel.SectionOrder`), so its parts stand in the show filter's order. The three lists share a size scope for the Link, Battery and Used By columns, and `DevicesViewModel.ShowLinkColumn` and `ShowBatteryColumn` drop a column no row fills.

The table has two forms. `ListCard_SizeChanged` sets the inherited attached property `DevicesPage.IsWideTable` on the list card when its width is at least `TableMin` (696). Under that a row shows its link and battery after its type, and the head keeps Used By alone.

### Device Row

`DeviceRowTemplate` (data type `DeviceRowViewModel`) in a `DeviceRowContainer` item style. Every row is 64 tall under the container's hairline. The row is an unnamed `Border` carrying three handlers (`DeviceCard_MouseDown`, `DeviceCard_MouseMove`, `DeviceCard_MouseUp`), which the accessibility allowlist keys by type and handler, so it must stay unnamed. A row shows the device's kind in a 36 by 36 tile (`Tile`, lit while the device sends input, `IsSending`), its name (`RowName`) with its type under it (`RowType`), the link (`LinkCell`, `DeviceLinkFact`), the battery (`BatteryCell`, `DeviceBatteryFact`), the slots that use it, Use It (`UseItButton`, `Devices_UseIt`, `Home_Offer_Use`) for a device no controller uses, and the remove button (`RowRemoveButton`, `Devices_RemoveRow`, `RemoveDevice_Click`) on every row of both lists, at opacity 0 until the pointer is on the row or the button has keyboard focus. `UseIt_Click` raises `NewControllerRequested` with the row's device, which opens Add a Controller. The picked row has an ember bar (`Bar`) and wash.

### Device Panel

| Card | Contents |
|------|----------|
| `IdentityCard` | `DeviceStage`: the device's picture (a still or the 2D art, set through `DevicesViewModel.SetPicture`) or its kind glyph. The name and type, Test Rumble (`TestRumbleButton`, `Devices_TestRumble`, `Pad_TestRumble`, shown while `SelectedDevice.HasRumble`, whose `IdentifyDevice_Click` rumbles the device so the user can tell which one it is), `LinkTile` and `BatteryTile` (`DeviceTile` style), and Used By: the slot chips (`UsedByChip`), led by a `ListLabel`, and New Controller (`NewControllerChip`, `Devices_UsedBy_New`, `NewController_Click`, which raises `NewControllerRequested` and opens Add a Controller with the device picked). `NumberUsedBy` gives the chips their place in the list for a screen reader |
| `TestCard` | Test Inputs. A gamepad shows `GamepadTest` (the stick rings in a `NamedPicture`, the trigger levels, and `PressedLine`, a chip per held button from `TestPressed`), and the full readout `RawFullView` under `TestMore` (`Devices_More_TestInputs`, shown on `ShowGamepadTest`). Any other device shows `RawFullView` as the card's body (`PlaceRawView`). The readout holds `MousePreviewControl` for a mouse, two `MidiPreviewView`s (`MidiNotesPreview`, `MidiCcPreview`) for a MIDI input, and the touchpad and Falcon previews (`TouchpadPreviewBorder`, `FalconPreviewBorder`) |
| `SettingsCard` | `Devices_SettingsCard`, shown on `ShowSettingsCard`, with Reset All (`ResetAllSettingsButton`, `Devices_ResetAll`, `ResetSettingsCardCommand`, shown on `HasResettableSettings`). The device's settings: hiding (`HidingToggle_Click`), power and quick charge (`QuickCharge_Click`), the driver switches (`DriverBind_Click`, `DriverRestore_Click`), native arrows (`NativeArrows_Click`), gun calibration (`GunCalibrate_Click`, reset `Reset_DeviceRowViewModel_GunCalibration`), then the device's tools, and Remove (`Devices_Remove`) |
| `DetailsFold` | The device's identifiers, with Copy Details (`Devices_CopyDetails`, `CopyDossier_Click`) and Submit Mapping (`Devices_SubmitMapping`, `SubmitMapping_Click`) |

Device-specific buttons open their dialogs: `RegisterNfcTag_Click` ([RegisterNfcTagDialog](#registernfctagdialog)), `LearnHandheldButton_Click` ([LearnHandheldButtonDialog](#learnhandheldbuttondialog)), `ManageVoicePhrases_Click` ([RegisterVoicePhraseDialog](#registervoicephrasedialog)), `ManageChatCommands_Click` ([ChatCommandsDialog](#chatcommandsdialog)), `MapKeyLights_Click` ([MapKeyLightsDialog](#mapkeylightsdialog)), `KeyboardScreen_Click` ([KeyboardScreenDialog](#keyboardscreendialog)), `FlydigiScreen_Click` ([FlydigiScreenDialog](#flydigiscreendialog)), `BlissBoxPlayer_Click` ([BlissBoxPlayerDialog](#blissboxplayerdialog)) and `DreamcastScreen_Click` ([DreamcastScreenDialog](#dreamcastscreendialog)). Others act in place: `FalconCalibrate_Click`, `ReadAsICade_Click`, `ReadAsKeyboard_Click`, `PakBackup_Click`, `PakRestore_Click`, `UsioTaiko_Click`, `UsioTekken_Click` and `ClearModEffects_Click`.

### Device Drag to a Pill

`DeviceCard_MouseMove` starts `DragDrop.DoDragDrop(card, data, DragDropEffects.Link)` past the drag threshold, with a `DataObject("DeviceInstanceGuid", device.InstanceGuid)`. A drop on a sidebar pill assigns the device to that slot (see [Device Drop on a Pill](#device-drop-on-a-pill)).

---

## KBMPreviewView

**Files:** `Views/KBMPreviewView.xaml`, `Views/KBMPreviewView.xaml.cs`

The picture of a Keyboard + Mouse slot in the controller page's first section, Keys & Mouse.

### Layout

Two `Canvas` areas:

- `KeyboardCanvas`: the layout from `KeyboardKeyItem.BuildLayout()`. Each key is a `Border` and a `TextBlock`, absolutely placed, lit while the key is down in the output state.
- `MouseCanvas`: a mouse with contoured left and right button paths, a scroll wheel, a movement circle with a deflection dot, scroll arrows, and the X1 and X2 side buttons.

### Interaction

Every element records on a click: `ControllerElementRecordRequested` fires with the target name (`KbmKey41`, `KbmMBtn0`, `KbmMouseX`). Hover uses `HoverBrush` (#FFA24D), a recording target flashes at 400 ms in `FlashBrush` (#FFA500), and a pressed key lights in `KeyPressedBrush` (#FF6B2C). `MappingLabel()` resolves a target's name to its label from the mapping table for the tooltip.

### Rendering

`CompositionTarget.Rendering` with a `_dirty` flag. Per frame: keys from `KbmOutputSnapshot.GetKey()` per virtual-key index, the buttons from `GetMouseButton()`, the dot from `MouseDeltaX` and `MouseDeltaY`, and the scroll arrows from the sign of `ScrollDelta`. Dark and light brush pairs are frozen statics, and the layout is rebuilt when the theme changes.

---

## MidiPreviewView

**Files:** `Views/MidiPreviewView.xaml`, `Views/MidiPreviewView.xaml.cs`

The picture of a MIDI slot in its first section, Notes & Controls. The Devices page uses the same control twice (`MidiNotesPreview`, `MidiCcPreview`) for a MIDI input device's raw state.

### Layout

One `Canvas` (`MidiCanvas`), cleared and rebuilt when the slot's start note, note count, start CC or CC count changes:

- CC sliders: one vertical bar per CC, its fill proportional to the value (0 to 127), with the CC number under it.
- Piano: white keys full height, black keys shorter on top. White keys show the note and octave ("C4").

### Interaction and Rendering

CC sliders and keys record on a click (`MidiCC{index}`, `MidiNote{index}`), with the 400 ms flash. `CompositionTarget.Rendering` with a `_dirty` flag reads `MidiOutputSnapshot.CcValues[]` and `Notes[]`, and a held note lights in `WhiteKeyPressedBrush` (#FFA24D) or `BlackKeyPressedBrush` (#C43D0C).

---

## VRPreviewView

**Files:** `Views/VRPreviewView.xaml`, `Views/VRPreviewView.xaml.cs`

The picture of a VR slot (#49) in its first section, Hands. One VR slot drives both SteamVR hands, so the art is the pair side by side.

### Layout

A `Viewbox` over one `Canvas` (`VrCanvas`), built on `Loaded` from the art in `2DModels/VRCONTROLLER/`. The base art is 975 by 726, and twelve elements stand in those pixels:

| Element | Targets |
|---------|---------|
| `VRController_L_Stick` / `_R_Stick` | `VrLStick` / `VrRStick` (click and four directions) |
| `VRController_L_A` / `_R_A` | `VrLA` / `VrRA` (inner press disc, outer touch ring) |
| `VRController_L_B` / `_R_B` | `VrLB` / `VrRB` |
| `VRController_L_System` / `_R_System` | `VrLSystem` / `VrRSystem` |
| `VRController_L_Trigger` / `_R_Trigger` | `VrLTrigger` / `VrRTrigger` (body axis, tip band click) |
| `VRController_L_Grip` / `_R_Grip` | `VrLGrip` / `VrRGrip` |

### Rendering and Interaction

Each element is tinted through a `Rectangle` with an `ImageBrush` `OpacityMask`, so lit, hover and flash drive one layer. Triggers and grips fill from the bottom through a `RectangleGeometry` clip. A stick cap moves up to 14 px with deflection. Frames come from `CompositionTarget.Rendering` against a cached `VrRawState`. Every element but System carries more than one target, so the region under the pointer lights at 0.4 opacity. The flash ticks at 450 ms.

---

## MousePreviewControl

**Files:** `Views/MousePreviewControl.xaml`, `Views/MousePreviewControl.xaml.cs`

A read-only mouse in the Devices page's Test Inputs for a mouse. `BuildMouse()` builds it on `Loaded` into `MouseCanvas`, the same mouse shape as `KBMPreviewView` without click-to-record, and again when the theme changes. `CompositionTarget.Rendering` reads `DevicesViewModel` every frame: `RawButtons[0..4].IsPressed` for the left, middle, right, X1 and X2 buttons, `MouseMotionX` and `MouseMotionY` for the dot, and `MouseScrollIntensity` for the arrows, which grow and brighten with the scroll.

---

## SettingsPage

**Files:** `Views/SettingsPage.xaml`, `Views/SettingsPage.xaml.cs`, with `Controls/SettingRow.cs`, `Controls/SettingItem.cs` and `Controls/SettingSearch.cs`. Its `DataContext` is `SettingsViewModel`.

### Layout Structure

```
ScrollViewer
└─ PageColumn (StackPanel, Margin 36,26,36,36, MaxWidth 1040, HorizontalAlignment Left)
    ├─ SettingsTitle (heading 1) + SettingsSearchBox (Settings_Search, SettingsSearchText)
    └─ Grid: GroupList (190) | gap | GroupsHost (822)
        ├─ GroupList: GroupGeneral, GroupInput, GroupHardware, GroupDrivers, GroupData
        └─ GroupsHost: GeneralGroup, InputGroup, HardwareGroup, DriversGroup, DataGroup,
             SearchNoneLine (Settings_SearchNone)
```

The page reads in one column of 1040 at the page's start, a `StackPanel` with `MaxWidth` rather than a capped star column, which takes a device pixel past its cap under layout rounding. The group list's five buttons (AutomationIds `Settings_Group_General`, `_Input`, `_Hardware`, `_Drivers`, `_Data`) each carry an icon through the attached `SettingsPage.GroupIcon` (`NavSettingsGeometry`, `NavDevicesGeometry`, `ChipLineGeometry`, `DownloadLineGeometry`, `ShieldLineGeometry`) and the sidebar's ember pick bar. `Group_Checked` shows one group, and `SyncGroupButtons` keeps the buttons in step.

| Group | Panel | Cards |
|-------|-------|-------|
| `Settings_Group_General` ("General") | `GeneralGroup` | Language (`Settings_Language`), Appearance (`Settings_Appearance`), Window (`Settings_Window`), Updates (`Settings_Updates`, which opens on its status and shows PadForge's version before any check) |
| `Settings_Group_Input` ("Input") | `InputGroup` | Input Engine (`Settings_InputEngine`: `AutoStartEngine`, the Polling Rate row, `EnablePollingOnFocusLoss`, the inactivity timeout `HmInactivityDestroyTimeoutSeconds`, 0 to 3600, `Settings_SecondsZeroNever`), Assignment Prompts (`Settings_AssignOffer`), Battery Alerts (`Settings_BatteryNotify`, `TestBatteryNotify_Click`) |
| `Settings_Group_Hardware` ("Hardware") | `HardwareGroup` | Hardware Support (`Settings_HardwareSupport`): analog keyboards, Bliss-Box, the Novint Falcon, Flydigi enhanced mode, G-keys, handheld buttons and keyboard screens |
| `Settings_Group_Drivers` ("Drivers") | `DriversGroup` | One row per driver in the `DriverName` and `DriverLine` styles: HidHide (`Settings_HidHide`), HIDMaestro (`Settings_HIDMaestro`), BthPS3 (`Settings_BthPS3`), Windows MIDI Services (`Settings_MidiServices`, `MidiRuntimeInstallButton`, `MidiRuntimeUninstallButton`) and SteamVR (`Settings_SteamVR`, `SteamVrBrowse_Click`), then the HidHide Options fold (`HidHideOptions`, AutomationId `Settings_HidHideOptions`) with `Settings_HideDevices`, `Settings_KeepCloaksBetweenLaunches` and the application list as a block |
| `Settings_Group_Data` ("Data & Privacy") | `DataGroup` | Community Configs (`Settings_CommunityConfigs`), Settings File (`Settings_SettingsFile`), Diagnostics (`Settings_Diagnostics`: `SaveDiagSnapshot_Click`, `OpenDiagFolder_Click`) |

The Polling Rate row is a `ui:NumberBox` on `PollingRateHz`, 60 to 10000. Its tooltip is `Settings_PollingRateTooltip_Format` filled with `PollingWakesPerSecond`, how often this PC wakes the poll loop, and `PollingOverrideNote` stands under it while the active profile carries a polling override, naming the profile and its rate.

### Rows and Search

A setting is a `SettingRow` in a `SettingItem`. In the Ends layout (the inherited attached `SettingRow.Ends`, with `Aside` and `EndsWidths`) the label takes the room, the controls stand at the row's end with the reset last, and what a setting reports stands before its switch and gives way first. `SettingItem` draws the hairline over a row (`Rule`).

`SettingSearch` drives the box: each group panel names its group (`SettingSearch.Group`) and each card its title (`SettingSearch.Card`), and each `SettingItem` shows or hides by whether its text holds the query. While a query stands, every group with a match shows under its own heading, and `SearchNoneLine` (`Settings_SearchNone_Format`) says when nothing matches. Without one, only the selected group shows. `ApplyView` runs this, queued by `QueueApply` on a change of the query, the language or the page's visibility. `Reveal(part)` opens the group and the fold that hold a part, which the app's own Search uses (`SearchNavigator`). `Page_PreviewKeyDown` and `SearchBox_PreviewKeyDown` handle the box's keys.

### Code-Behind

| Handler | Action |
|---------|--------|
| `Group_Checked` | Shows the checked group |
| `TestBatteryNotify_Click` | Shows a battery alert |
| `SaveDiagSnapshot_Click`, `OpenDiagFolder_Click` | Dump the engine event ring to a file (#303) and open its folder |
| `SteamVrBrowse_Click` | Picks SteamVR's folder |

`SettingsPage.InputService` is a static reference `MainWindow` sets. Driver installs and removals are commands on `SettingsViewModel` that `MainWindow` runs through `RunDriverOperationAsync` under the driver overlay. `RebuildControllerSection` calls `SettingsViewModel.RefreshDriverGuards()`, which keeps a driver's removal disabled while slots of its type exist.

---

## ProfilesPage

**Files:** `Views/ProfilesPage.xaml`, `Views/ProfilesPage.xaml.cs`. Its `DataContext` is `SettingsViewModel`.

### Layout Structure

```
ScrollViewer
└─ StackPanel
    ├─ ProfilesHead: ProfilesTitle, HeadButtons
    │   ├─ GetProfilesButton (Profiles_GetProfiles, GetProfilesCommand)
    │   └─ NewProfileButton (Profiles_NewProfile, NewProfileCommand)
    ├─ ProfileGridHost > ProfileListBox (TileGridPanel, MinItemWidth 470, gap 16)
    │   ├─ ProfilesCollectionContainer: one ProfileCard per profile
    │   └─ DropTile (Profiles_DropTile, DropTile_Click)
    ├─ ProfileDropOverlay
    ├─ StartersHead: StartersTitle, SeeAllStarters (Profiles_SeeAllStarters)
    ├─ StarterTiles (TileGridPanel, MinItemWidth 230, gap 12, FillRows, Balance)
    └─ WaysRow (TileGridPanel, MinItemWidth 300, gap 16, FillRows)
        ├─ AutoSwitchCard: InFrontLine, InFrontDot (Profiles_InFront), Profiles_AutoSwitch
        ├─ ShortcutsCard: ProfileShortcuts, Profiles_AddShortcut, Profiles_ResetShortcuts
        └─ ExternalControlCard > ExternalControlFold (Profiles_ExternalControl)
```

### Profile Card

A `ProfileCard` shows, in `CardRows`, the profile's name (with `Profiles_BuiltIn` on the default profile), the games that switch to it (`GameLead`, `GameNames`, `GameTail`, or `Profiles_Card_NoGame`), and a row of controller pictures (`CardStills`, a `StillRowPanel` over the profile's `Controllers`), or `Profiles_NoSlots` when it has none. `MoreControllers` counts the pictures the row left out (`StillRowPanel.HiddenCount`). A picture on the active profile's card opens that controller's page (`ProfileStill_Click`, AutomationId `Profiles_Still`, raising `ControllerOpenRequested`). Load is `Profiles_Load` (`LoadProfileCommand`). The active card is lit (`ActiveLight`, a `Halo`, and `ActiveWash`). More (`Profiles_More`, `CardMore_Click`) opens Edit, Save As, Save Here, Export and Delete (`Profiles_Menu_Edit`, `_SaveAs`, `_SaveHere`, `_Export`, `_Delete`, all through `ProfileMenu_Click`). `ProfileCard_MouseLeftButtonDown` handles a click on the card.

The drop tile takes what is left of its row (`TileGridPanel.TakesRest`) and is a slim band when alone. A click runs `GetProfilesCommand` with "File", which opens Get Profiles on its file tab, and a file dropped anywhere on the list (`ProfileList_DragEnter`, `DragOver`, `DragLeave`, `Drop`, which show `ProfileDropOverlay`) is imported through the page's `ImportProfileFile` action, which `MainWindow` sets to `ImportProfileFromFile`. A file is importable when it is a `.pfprofile` or `ForeignConfigImporter.HandlesFile` takes it (`IsImportableFile`).

### Starters

`ShowStarters` fills `StarterTiles` with `ProfilesPage.StarterTileCount` (4) starters, and `TileGridPanel.Balance` keeps four from standing three and one. `StarterTile_Click` (AutomationId `Profiles_Starter`) adds the starter as a new profile without loading it, once per click. See All (`Profiles_SeeAllStarters`) runs `GetProfilesCommand` with "Starters", which opens Get Profiles on its Starters tab.

### Shortcuts and Automatic Switching

`AutoSwitchCard` holds the automatic switching setting (`Profiles_AutoSwitch`) and the line naming the program in front (`InFrontLine`, `InFrontDot`), with no Reset All. `ShortcutsCard` lists `ProfileShortcuts`, one `ShortcutLine` each:

| Part | AutomationId | Binding |
|------|--------------|---------|
| Mode | `Shortcut_Mode` | `SwitchModes` |
| Profile | `Shortcut_Profile` | `ProfileChoices` (`ProfileChoices_DropDownOpened` refreshes it) |
| Combo | `Shortcut_Combo` | `ComboParts`, one key a button, a key naming its device only where the row's device does not |
| Record | `Shortcut_Record` | `ShortcutLearn_Click` |
| Clear | `Shortcut_Clear` | `ClearCommand` |
| Device | `Shortcut_Device` | `DeviceChoices` (`DeviceChoices_DropDownOpened`) |
| Delete | `Shortcut_Delete` | `DeleteCommand` |

Add Shortcut (`Profiles_AddShortcut`, `AddShortcut_Click`) and Reset (`Profiles_ResetShortcuts`, `ResetShortcutsCommand`) sit on the card. `OnShortcutsChanged` saves them (`MainWindow.SaveProfileShortcuts`).

Recording a combo (`ShortcutLearn_Click`) listens on a timer (`RecordTimer_Tick`) for up to `RecordTimeoutSeconds` (5). An axis counts as pressed past `AxisRecordDeltaThreshold` (0.25). `StopRecording` keeps what was held, and `CancelRecording` drops it.

### Get Profiles

**Files:** `Views/GetProfilesDialog.xaml`, `Views/GetProfilesDialog.xaml.cs`, and `Views/CommunityConfigsPanel.xaml` for its Community tab.

`GetProfilesDialog` replaced the starter browser and the Workshop browser of PadForge 5. It is a [DialogWindow](#dialog-windows) at the wide size (`IsWide`, `ShowClose`, resizable, 680 by 568, at least 560 by 480) titled `GetProfiles_Title`, with three tabs: Starters (`GetProfiles_Starters`, `StarterList`, a double click adds one), Community (`GetProfiles_Community`, `CommunityPanel`, the Steam Workshop configs) and From a File (`GetProfiles_File`, `FileDropZone`, AutomationId `GetProfiles_FileDrop`, with `FileProblemText` for a refused file). A search field (`SearchBox`) filters the open tab. The foot holds Cancel (`GetProfiles_Cancel`), Save and Apply (`GetProfiles_SaveApply`), Save (`GetProfiles_Save`) and Import (`GetProfiles_Import`). Whatever lands is an ordinary profile, registered through `ProfileSink` (`MainWindow.AddWorkshopProfile`, which names it uniquely and, with true, loads it). `ProfileFileResult` carries a file's outcome back. `MainWindow.ShowGetProfiles(tab)` opens it, on `SettingsViewModel.GetProfilesRequested` (the Profiles page's Get Profiles, See All and drop tile) and from Home's first page on its starters.

---

## ProfileSwitchOverlay

**Files:** `Views/ProfileSwitchOverlay.xaml`, `Views/ProfileSwitchOverlay.xaml.cs`

A flyout in the style of the Windows 11 volume display, over the taskbar while a profile switches. It shows the profile's name, then the controllers' state.

### Window Properties

A non-activating, topmost, transparent window: `WindowStyle="None"`, `AllowsTransparency="True"`, `Topmost="True"`, `ShowInTaskbar="False"`, `ShowActivated="False"`, `Focusable="False"`, `SizeToContent="WidthAndHeight"`. `OnLoaded` adds `WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW` through `SetWindowLong`, and the window answers `WM_MOUSEACTIVATE` with `MA_NOACTIVATE`.

### Layout Structure

```
Grid (ClipToBounds="True")
  └─ FlyoutPanel (Margin 10,10,10,14)
      ├─ ShadowBorder (CornerRadius 8, DropShadowEffect BlurRadius 15)
      └─ ContentBorder (CornerRadius 8)
          └─ StatusIcon (Segoe Fluent Icons, 16) + StatusText (14, the body face)
```

`ApplyTheme()` sets the colors from `ApplicationThemeManager.GetAppTheme()`: dark #2D2E2E with a #141516 edge, light #EFEFEF with a #D0D0D0 edge and #1A1A1A text.

### Slide Animation

| Method | Direction | Duration | Easing |
|--------|-----------|----------|--------|
| `SlideIn()` | Y: 80 to 0 | 300 ms | `CubicEase`, EaseOut |
| `SlideOut(Action onCompleted)` | Y: 0 to 80 | 250 ms | `CubicEase`, EaseIn |

`SlideIn()` sets the transform to `SlideTravel` (80) at once and starts the animation at `DispatcherPriority.Loaded`, so WPF does not merge the start and end into one frame.

### State Machine

```
Profile name (2 s) → Initializing (polling) → Active (2 s) → Offline (2 s) → hide
                                                           └→ hide (none offline)
```

| Phase | Icon | Text | Timer |
|-------|------|------|-------|
| Profile | `E8F1` | The profile's name | `_dismissTimer`, 2 s |
| Initializing | `E895` | `Main_Initializing` ("Initializing") | `_initMonitorTimer`, 33 ms, polling `CheckInitState` |
| Active | `E73E` | `Main_Active` ("Forging") | `_dismissTimer`, 2 s |
| Offline | `E7BA` in #FFB900 | `Main_ControllersOffline` ("One or more controllers offline") | `_dismissTimer`, 2 s |

While Initializing, `StatusIcon` flashes (opacity 1 to 0.3, 600 ms, reversing).

### Public API

| Member | Description |
|--------|-------------|
| `CheckInitState` | `Func<(bool anyInitializing, bool allReady)>`, set by `InputService` |
| `CheckAnyOffline` | `Func<bool>`, set by `InputService` |
| `ShowProfileName(string)` | Starts the state machine |
| `ShowVCsToggle(bool)` | A one-shot notice for the master virtual-controller switch, outside the state machine: `E73E` in #37C852 with `Main_VCsEnabled`, or `E7E8` in #E81B1C with `Main_VCsDisabled`, then a 2 s dismiss. `InputService.ShowVCsToggleOverlay` calls it |
| `StopTimers()` | Stops both timers, at shutdown |

`ShowFlyout()` centers the window in `SystemParameters.WorkArea` with its bottom edge at the work area's, and the panel's bottom margin of 14 leaves the gap over the taskbar.

---

## AboutPage

**Files:** `Views/AboutPage.xaml`, `Views/AboutPage.xaml.cs`. Its `DataContext` is `SettingsViewModel`, for the version and the update commands Settings has.

### Layout Structure

```
ScrollViewer
└─ PageColumn (StackPanel, MaxWidth 1040, HorizontalAlignment Left)
    ├─ AboutTitle (heading 1)
    ├─ PadForgeCard: the version (About_Version), AboutSubLine with the update state
    │   (About_UpdateStatus), Documentation (About_Documentation), GitHub (About_GitHub),
    │   Release Notes (About_ReleaseNotes, OpenReleaseNotesCommand), Check for Updates
    │   (About_CheckForUpdates, CheckForUpdatesNowCommand), the description and tagline
    ├─ the invitation, with InviteLine
    └─ Built With (CardBorder): the heading (About_BuiltWith), CreditsSearch (About_CreditsSearch),
        CreditsList (one CreditRow per credit), NoCreditMatch, ShowAllCreditsRow > ShowAllCreditsButton
        (About_ShowAllCredits)
```

`PageColumn` keeps the page in one column of 1040 whatever the credits search leaves. Each credit is a `CreditRow` with a name (`CreditName`), a line (`CreditDesc`) and its license on a chip (`CreditChip`), all through `BidiText.Text`, in English name order. Bouncy Castle's chip reads `About_License_Mit`.

### Code-Behind

| Member | Action |
|--------|--------|
| `ApplyCreditsView()` | Without a query, shows the first `FirstCredits` (5) rows, or every row while the list is open. With a query, shows every row whose name, line or license holds it, hides the button's row, and shows `About_NoCreditMatch_Format` when none does |
| `ShowAllCredits_Click` | Opens or folds the list (`About_ShowAllCredits`, `About_ShowFewerCredits`) |
| `CreditsSearch_TextChanged` | Runs `ApplyCreditsView` |
| `BuildInviteLine` | Builds `InviteLine` from `About_TestimonyInvite` with the marker `ComeUntoChrist.org` as a link, again on each change of language. `OnInviteNavigate` opens it |
| `Documentation_Click`, `GitHub_Click` | Open the documentation and the repository |

---

## SearchPanel

**Files:** `Views/SearchPanel.xaml`, `Views/SearchPanel.xaml.cs`, with `Search/SearchService.cs`, `SearchNavigator`, `SearchIndexBuilder` and `ViewModels/SearchViewModel`. Shell wiring is under [Search](#search).

Search opens over the page area in `SearchHost`, a `ShellDialog` (AutomationId `SearchPanel`, `FrameMaxWidth` 660, `ClosesOnGroundPress`), from the title bar's box or Ctrl+K. Its `DataContext` is the `SearchViewModel`.

| Element | AutomationId | Role |
|---------|--------------|------|
| `QueryRow` with `SearchQueryBox` and `SearchPlaceholder` | `SearchQueryBox` | The query |
| `SearchCloseChip` | `SearchCloseChip` | The Esc key label, which closes Search (`CloseChip_Click`) |
| `SearchResultsList` | `SearchResultsList` | `ResultsView`, the results grouped by `SearchResult.GroupLabel`. `Result_MouseUp` opens one |
| `SearchNoResults` | | Shown when nothing matches |
| `SearchFoot` with `MoveHint`, `OpenHint`, `AnywhereHint` | | `KeyHint` lines from `Search_Hint_Move_Format` ("{0} {1} to move"), `Search_Hint_Open_Format` ("{0} to open") and `Search_Hint_Anywhere_Format` ("{0} from anywhere") |
| `SearchAnnouncement` | | A live region for a screen reader |

`Panel_PreviewKeyDown` moves through the results with Up and Down (one) and Page Up and Page Down (five), opens with Enter, and on Ctrl+K selects the query's words. `FocusQuery` puts the focus in the box with its words selected, and `FitTo(height)` caps the list at the room the host has. Until `SearchService.BuildIndex` finishes, Search answers with pages, controllers, devices, profiles and the documentation. Settings and actions join once the index is built. `SearchNavigator.Open` goes to a result: a page by its tag, the result's own controller's page (`SearchResult.Pad`) and its section or group (`PadPage.OpenSection`, `PadPage.OpenTab`), a mapping row's option on the first row that has it, in the List view with the List's own search cleared when the picture shows, a setting by revealing it (`SettingsPage.Reveal`), or Add a Controller.

---

## Dialog Windows

Every PadForge dialog is a `DialogWindow` (`Views/DialogWindow.cs`), a `Wpf.Ui.Controls.FluentWindow`: a title, a line under it (`Subtitle`), the dialog's own content, and a foot of buttons (`Foot`, a `FlexLinePanel` in the `DialogFootPanel` style) over a hairline, on the card fill. Its style and template (`DialogWindowTemplate`) are in `Resources/Dialogs.xaml`, which every dialog merges into its own resources before `InitializeComponent`, so a dialog lists its resources directly under `DialogWindow.Resources` and never inside a `ResourceDictionary` element. The style gives a dialog Mica, the body face at 14, `ResizeMode="NoResize"`, no taskbar button, `SizeToContent="Height"` and a width of 560. `IsWide` makes it the 680 dialog with a 20 title and more room, and `ShowClose` puts an X at the head's end, which closes with no result as Escape does. `ScrollsBody` scrolls the body once the window reaches its cap. A press on the window's ground drags it, except on anything clickable, which the hand cursor marks. `DialogSettingResets.cs` holds the per-setting resets of the dialogs that have them. The dictionary also holds the dialogs' shared parts: `DialogButton`, `DialogPrimaryButton`, `DialogDangerButton`, `DialogQuietButton`, `DialogTextBox`, `DialogSelect`, `DialogList`, `DialogListItem`, `DialogStatTile`, `DialogCountdownBar`, `DialogMoreRow` and the rest.

| Dialog | Title | Opened by |
|--------|-------|-----------|
| `BlissBoxPlayerDialog` | `BlissBoxPlayer_Title` ("Player Number") | `MainWindow.BlissBox.cs`, a Bliss-Box port's row |
| `ChatCommandsDialog` | `TwitchChat_DialogTitle` ("Chat Commands") | The Twitch Chat page on Extras, and the Devices page |
| `ConfirmDialog` | the caller's | `ConfirmDialog.Show` across the app, ahead of a destructive or driver action |
| `CopyFromDialog` | `CopyFrom_Title` ("Copy From") | The controller page's Copy From… and the macro copy |
| `CustomTelemetryFormatsDialog` | `Telemetry_Formats_Title` ("Custom Formats") | The Game Telemetry page on Extras |
| `DreamcastScreenDialog` | `DreamcastScreen_Title` ("Dreamcast Screen") | `MainWindow.BlissBox.cs` |
| `FlydigiScreenDialog` | `FlydigiScreen_Title` ("Controller Screen") | `MainWindow.FlydigiScreen.cs`, a Flydigi Apex pad's Devices panel |
| `GetProfilesDialog` | `GetProfiles_Title` ("Get Profiles") | `MainWindow.ShowGetProfiles` (see [Get Profiles](#get-profiles)) |
| `ImportConfigDialog` | `Import_DialogTitle` ("Import Profile") | `MainWindow.ImportProfileFile`, for another tool's config |
| `KeepDriverDialog` | `Devices_DriverKeepTitle` and its mouse and touchpad forms | `MainWindow` after a driver switch |
| `KeyboardScreenDialog` | the screen's name | `MainWindow.KeyboardScreens.cs` |
| `LearnHandheldButtonDialog` | `Handheld_Title` ("Hidden Buttons") | The Devices page |
| `ManageProfilesDialog` | `ManageProfiles_Title` ("Controller Presets") | The controller page |
| `MapKeyLightsDialog` | `MapKeyLights_Title` ("Map Key Lights") | The Devices page |
| `PairDeviceDialog` | `WiiPair_Title` ("Pair a Wii Remote") | `DevicesViewModel.PairRequested` |
| `PickSoundDialog` | `PickSound_Title` ("Pick a Sound") | The controller page's sound actions and packages |
| `ProfileDialog` | `ProfileDialog_SaveAs` ("Save As Profile") | `MainWindow`, for a new profile, Save As and Edit |
| `RegisterNfcTagDialog` | `Nfc_Title` ("NFC Tags") | The Devices page |
| `RegisterVoicePhraseDialog` | `Voice_Title` ("Voice Macros") | The Devices page |
| `ReleaseTestDialog` | `Pad_Centering_ReleaseTest` ("Release Test") | The Centering card |
| `RemoteAssignmentsDialog` | `RemoteLink_AssignmentTitle_Format` | `InputService`, a paired PC's Assign Shared Devices |
| `RemoteLinkPairDialog` | `RemoteLink_PairTitle` ("Pair with Another PC?") | `InputService`, a pairing request |
| `RemoteLinkPasswordDialog` | `RemoteLink_PasswordSetTitle` ("Set a Password") | `InputService` |
| `ShiftActivatorDialog` | `Pad_Shift_DialogTitle` ("Shift Layer") | The controller page's layer chips |
| `TouchpadGestureRecorderDialog` | `Recorder_Title` ("Record a Gesture") | The Custom Gestures card |
| `UninstallBthPS3Dialog` | `BthPS3Uninstall_Title` ("Uninstall BthPS3") | `MainWindow`, the BthPS3 removal |
| `UninstallHIDMaestroDialog` | `HIDMaestroUninstall_Title` ("Uninstall HIDMaestro") | `MainWindow`, the HIDMaestro removal |

PadForge 6 removed `StarterProfilesDialog` and `WorkshopBrowseDialog`. Their content is the Starters and Community tabs of `GetProfilesDialog`.

### CopyFromDialog

**Files:** `Views/CopyFromDialog.xaml`, `Views/CopyFromDialog.xaml.cs`

Copies another slot's settings, or its macros, to this one. `MainWindow` builds its `DeviceEntry` list: one entry per other slot whose mapping table has rows (`InputService.SlotHasAnyMapping`), and one per device that is on no slot but still carries a `PadSetting` with mappings. The target slot is skipped. A settings copy applies the source's table and carries each assigned device's tuning through `InputService.BuildPerDeviceSettingsSnapshot` and `ApplyPerDeviceSettingsToSlot`, matched by `InstanceGuid` or, for the same model, `ProductGuid`. A macro copy gives each copied hold pair a fresh identifier past the highest the slot uses.

### ProfileDialog

**Files:** `Views/ProfileDialog.xaml`, `Views/ProfileDialog.xaml.cs`

Creates or edits a profile: `NameBox`, the games that switch to it (`GamesHead`, `GamesLine`, `AddRunningGameButton`, `BrowseButton`), and under More (`ProfileMore`) the profile's polling rate (`PollingRateBox`). `SaveButton` saves.

### RegisterNfcTagDialog

**Files:** `Views/RegisterNfcTagDialog.xaml`, `Views/RegisterNfcTagDialog.xaml.cs`

Captures and names NFC tags (#150). Tapping a tag captures its UID, the user names it, and it is added to `NfcTagRegistry`, which offers it as a named button on the NFC device. The dialog lists the registered tags with a Remove each. While open it listens on `NfcReaderService.TagDetected` for a standalone reader and `NfcTagRegistry.ControllerTagDetected` for a controller's reader, with `NfcTagRegistry.RegistrationCaptureActive` raised for its lifetime. `OnTagDetected` runs on the reader's thread and moves to the UI thread with `Dispatcher.BeginInvoke`. Both subscriptions end on `Closed`.

| Element | Handler | Purpose |
|---------|---------|---------|
| `StatusText` | | Tap prompt, captured, or no reader |
| `UidText` | | The captured UID |
| `NameBox` | `NameBox_KeyDown` | The tag's name. Enter registers |
| `RegisterBtn` | `RegisterButton_Click` | `NfcTagRegistry.Register(uid, name)` |
| `TagListBox` | `RemoveButton_Click` | Registered tags |

### LearnHandheldButtonDialog

**Files:** `Views/LearnHandheldButtonDialog.xaml`, `Views/LearnHandheldButtonDialog.xaml.cs`

Learns a handheld PC's hidden buttons (#343), from the Devices page's `LearnHandheldButton_Click`. A run is three timed phases driven by `_phaseTimer` over a `HandheldLearnSession`: Idle (the noise floor), Press and Release, each lasting the session's `IdleMs`, `PressMs` or `ReleaseMs`. `FinishLearn` reads the candidates and the chord the session collected, and the user names the button and registers it. There is no per-model table.

| Element | Handler | Purpose |
|---------|---------|---------|
| `DaemonBox` / `DaemonText` | | The vendor daemon notice |
| `SourceRow` / `SourceLabel` | | Where the button was read |
| `StartBtn`, `LiveDot`, `StatusText` | `StartButton_Click` | Starts the pass, and which phase runs |
| `ChordText` / `CandidateBox` | | The chord the press made, and the candidates when there are several |
| `NameBox` | `NameBox_KeyDown` | The name. Enter registers |
| `RegisterBtn` | `RegisterButton_Click` | Adds the button to `HandheldButtonRegistry` |
| `ButtonListBox` / `EmptyText` | `RefreshList`, `RemoveButton_Click` | Learned buttons, and the empty line |
| Export / Import | `ExportButton_Click` / `ImportButton_Click` | Carry a learned set between machines |

### RegisterVoicePhraseDialog

**Files:** `Views/RegisterVoicePhraseDialog.xaml`, `Views/RegisterVoicePhraseDialog.xaml.cs`

Voice macros (#317), from the Devices page's `ManageVoicePhrases_Click`. Three bands: the settings (`EnabledBox`, `ModeBox`, `ConfidenceSlider` from 0.5 to 0.99 with `ConfidenceText`), the live `HeardText` with the microphone that heard the phrase, and registration with the phrase list. There is no source picker: phrases live on the devices that carry the microphones, and every microphone runs its own session.

The dialog listens on `VoiceMacroService.PhraseHeard` and lights the matching row for 1400 ms, only for a recognition that fires. The readout shows every attempt with its confidence. Each row's `FlashTimer` restarts per hit. `Closed` and the close button both run `Unsubscribe`.

| Element | Handler | Purpose |
|---------|---------|---------|
| `EnabledBox` / `ModeBox` / `ConfidenceSlider` | `Setting_Changed` | Write `VoiceMacroService.Enabled`, `ListeningMode` and `MinConfidence`, and mark the settings dirty |
| `HeardText` | `VoiceMacroService.PhraseHeard` | `[source] text (confidence)` |
| `PhraseBox` / `NameBox` | `PhraseBox_KeyDown` | The phrase and its name. Enter registers |
| `RegisterBtn` | `RegisterButton_Click` | `VoicePhraseRegistry.Register(phrase, name)` |
| `PhraseListBox` | `RemoveButton_Click` | Registered phrases |

### ConfirmDialog

**Files:** `Views/ConfirmDialog.xaml`, `Views/ConfirmDialog.xaml.cs`

The confirm. `ConfirmDialog.Show(owner, title, message, actionText, detail)` returns true when the action was chosen. A destructive form wears the danger button.

### ManageProfilesDialog

**Files:** `Views/ManageProfilesDialog.xaml`, `Views/ManageProfilesDialog.xaml.cs`

The HIDMaestro profile catalog. It lists imported profiles (name and id) with Import From File, Export and Delete (Delete confirms first). A row HIDMaestro left out of the pickers carries a third line, `ImportedProfileRow.Problem`: HIDMaestro's reason and the JSON path for a refused file, or the missing HID descriptor. A second part imports a profile from a connected device. An import HIDMaestro would refuse is not stored, and `ImportFailedText` gives the reason.

### UninstallHIDMaestroDialog

**Files:** `Views/UninstallHIDMaestroDialog.xaml`, `Views/UninstallHIDMaestroDialog.xaml.cs`

The removal of HIDMaestro from the PC (#518). Cancel holds the default and the focus. `Confirm(owner, preview, out includeUsbip)` runs the preview it is handed (`HIDMaestroRemoval.Preview` on a worker) on load and on each change of the usbip-win2 check box, with a progress line meanwhile, then lists each item as location, kind and, for one kept or not read, the reason (`RowsFor`). Refresh reads the PC again. Uninstall opens only while `CanRemove` holds. `ShowReport(owner, report, statusLine)` reuses the window with Close alone to list what a removal could not take. A preview that ends after the window closed, or after a newer one started, is dropped (`_generation`).

### UninstallBthPS3Dialog

**Files:** `Views/UninstallBthPS3Dialog.xaml`, `Views/UninstallBthPS3Dialog.xaml.cs`

The removal of BthPS3, built as `UninstallHIDMaestroDialog` is, without the usbip-win2 option. `Confirm(owner, preview)` runs `BthPS3Removal.Preview` on load and on Refresh, then lists each item as location, kind (`BthPS3Removal.KindText`) and, for one kept, the reason (`RowsFor`). The line above the list (`NoteFor`) says what holds the removal, that DsHidMini keeps the drivers, or that nothing is left. Uninstall opens only while `CanRemove` holds. `ShowReport` lists what a removal could not take.

### PairDeviceDialog

**Files:** `Views/PairDeviceDialog.xaml`, `Views/PairDeviceDialog.xaml.cs`

Wii Remote pairing (#116), from the Devices page's Pair (`DevicesViewModel.PairRequested`): it walks the user through the sync-button handshake. Its resets are in `DialogSettingResets.cs`.

### PickSoundDialog

**Files:** `Views/PickSoundDialog.xaml`, `Views/PickSoundDialog.xaml.cs`

The sound picker for a macro's sound action and for a sound package's entries, built with the items the controller page hands it.

### ColorPickerControl

**Files:** `Views/ColorPickerControl.xaml`, `Views/ColorPickerControl.xaml.cs`

An HSV color picker `UserControl`: a 200 by 200 saturation and value square over a hue layer, and a hue strip. It feeds the lightbar and RGB color rows. The hue layer is rebuilt in code on a change of hue.

### ShiftActivatorDialog

**Files:** `Views/ShiftActivatorDialog.xaml`, `Views/ShiftActivatorDialog.xaml.cs`

The shift-layer editor. It records the activator combo and sets up the layer, with RGB color rows in the Lights section's style. The square button left of the name shows the layer's icon, a picture (`IconPickerImage`) when the reference resolves and the glyph (`IconPickerGlyph`) otherwise, both through `MenuIconResolver.ResolveLayerIcon`, and opens [IconPicker](#iconpicker). The emoji catalog (`EmojiCatalog`, `EmojiCategory`) is in this file, and the picker reads it.

### ShiftLayerFlyout

**Files:** `Views/ShiftLayerFlyout.xaml`, `Views/ShiftLayerFlyout.xaml.cs`

A flyout in `ProfileSwitchOverlay`'s chrome (dark #2D2E2E with a #141516 edge, corner 8, a shadow border under a content border). It stays while a shift layer is engaged on the slot being viewed and slides out when the slot returns to Base. `ShowLayer` draws the layer's icon through `MenuIconResolver.ResolveLayerIcon`: a picture that resolves fills `StatusImage`, a single glyph shows in `StatusIcon`, and anything else shows ⇧. The Overlays page on Extras turns it on (`EnableShiftLayerFlyout`).

### TouchpadGestureRecorderDialog

**Files:** `Views/TouchpadGestureRecorderDialog.xaml`, `Views/TouchpadGestureRecorderDialog.xaml.cs`

Records a touchpad stroke as a named gesture template (#88). `PadPage.OnRecordTouchpadGestureRequested` opens it for the device.

### TouchpadOverlay

**Files:** `Views/TouchpadOverlay.xaml`, `Views/TouchpadOverlay.xaml.cs`

A transparent, topmost `Window` (500 by 250, at least 150 by 80, titled `Dashboard_TouchpadOverlayWindowTitle`) that mirrors the touchpad with live finger dots and a 32 tall click bar. It moves by its surface and takes no focus when shown. `Surface_LostMouseCapture` and `ResizeGrip_LostMouseCapture` end a drag whose release never arrives. `MoveToMonitor`, `EnsureOnScreen` and `GetCurrentMonitor` forward to `OverlayPlacement`. Its settings are on the Touchpad Overlay page on Extras.

### MenuOverlayWindow

**Files:** `Views/MenuOverlayWindow.xaml`, `Views/MenuOverlayWindow.xaml.cs`

The on-screen radial and grid menu (#9). A click-through window that never activates (`WindowStyle="None"`, `AllowsTransparency`, `Topmost`, `ShowInTaskbar="False"`, `ShowActivated="False"`, `SizeToContent="WidthAndHeight"`), with `WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TRANSPARENT` on `Loaded` and a `WndProc` hook answering `WM_MOUSEACTIVATE` with `MA_NOACTIVATE`.

`InputService` owns it: on the UI timer it reads `InputManager.ActiveMenuOverlay` (the window is made on the first engage and hidden while no menu is engaged or `EnableMenuOverlay` is off) and calls `UpdateFromSnapshot`. The content is built in code on a `Canvas`: ring wedges for a radial menu, rounded cells for a grid, one row for a Hotbar menu. Geometry is rebuilt only when the menu or its `GeometrySig` changes, and each tick restyles the hovered cell. `MaxRenderCells` (64) caps the build. The window centers on the menu's `PosXPercent` and `PosYPercent` of the primary work area, clamped on screen.

### IconPicker

**Files:** `Views/IconPicker.xaml`, `Views/IconPicker.xaml.cs`

The shared icon picker (#471), a `UserControl` in a `Popup` under the button that opened it (`PlacementMode.Bottom`, `StaysOpen="False"`). Menu cell rows (`MenuCellChooseIcon_Click`) and the shift-layer dialog open it through `IconPickerHost.Open(anchor, currentIcon, clearLabel, apply, showPackage)`. Two tabs:

- Emoji (`IconPicker_Emoji`): a category bar named by `EmojiCategory.DisplayName` and a grid over `ShiftActivatorDialog.EmojiCatalog`.
- Images (`IconPicker_Images`): every registered icon package's entries as 40 by 40 buttons grouped by package, `IconPicker_NoPackages` when there is none, and Browse Files… at the foot. Thumbnails decode into an 80 by 80 box (`BoundedBitmap`) from one read of each archive. A package gives the picker its first `IconPackageManager.MaxPickerIcons` (2,048) image entries and at most `MaxPickerBytes` (128 MB) of entry bytes, and the picker holds at most `IconPicker.MaxThumbnails` across every package.

The current choice wears the tab's ember (`IsCurrent`), and the picker opens on its tab. The clear button takes the caller's label. A pick raises `IconChosen` (an empty string clears), closes the popup and returns focus to the opener. Escape closes it. Browse Files… runs `IconPickerHost.BrowseFromDisk`, which takes PNG, JPEG, GIF and BMP images and `.pficons` packages.

### RemoteLinkPairDialog

**Files:** `Views/RemoteLinkPairDialog.xaml`, `Views/RemoteLinkPairDialog.xaml.cs`

The Remote Link consent screen (#138), from `InputService` on a pairing request: the short authentication string (`SasText`, compared out of band with the other PC's screen), the peer's identity (`IdentityText`), and two check boxes, `GamepadOnlyCheck` and `AssignmentsCheck`. `PairButton` accepts. `RejectButton`, or closing the window, declines.

### RemoteLinkPasswordDialog

**Files:** `Views/RemoteLinkPasswordDialog.xaml`, `Views/RemoteLinkPasswordDialog.xaml.cs`

The Remote Link password prompt (#138): `PwBox`, and `ConfirmBox` in `ConfirmRow` when a password is set, with `ErrorText`. `OkButton` submits, and Enter in either box does too.

### RemoteAssignmentsDialog

**Files:** `Views/RemoteAssignmentsDialog.xaml`, `Views/RemoteAssignmentsDialog.xaml.cs`

Remote device assignment (#138), titled `RemoteLink_AssignmentTitle_Format` with the peer's name and opened by `InputService` from a paired PC's Assign Shared Devices. `DevicesBox` lists the devices this PC shares with that peer. Picking one queries the other PC (`LinkAssignmentChannel.QueryAsync`), and `SlotsList` shows its virtual controllers as check boxes, with `ProfileText` naming its active profile. A change sends `SetAsync` with the last reply's revision, so a change made on the other PC in between comes back `Stale`. `StatusText` carries the busy, denied, timeout and no-slot messages. `RefreshButton` reloads.

### CustomTelemetryFormatsDialog

**Files:** `Views/CustomTelemetryFormatsDialog.xaml`, `Views/CustomTelemetryFormatsDialog.xaml.cs`

The custom telemetry formats (#531), from the Game Telemetry page's Custom Formats…. A wide dialog of 1040 by 680. `FormatList` on the left lists the formats with Add, Duplicate and Delete. `EditorPanel` on the right edits the selected one: its name, its packets (binary or JSON), length and byte order for binary, the Required Key for JSON, the gear values, and its fields (name, target, offset or key, type, scale, min, max). The dialog edits copies (`TelemetryFormatEdit`), so Cancel keeps the saved list. Save shows the first problem in `ProblemText` and stays open, or sets `Result` and closes. A duplicate name is a problem. New formats take the first free name from `UniqueName`. Detail on [Game Telemetry Internals](game-telemetry-internals.md).

### ImportConfigDialog

**Files:** `Views/ImportConfigDialog.xaml`, `Views/ImportConfigDialog.xaml.cs`

The preview before another tool's profile joins the list (#561). A wide dialog with an X, titled `Import_DialogTitle` ("Import Profile"), opened by `MainWindow.ImportProfileFile` when `ForeignConfigImporter.Translate` accepts a file that is not a `.pfprofile`: from Get Profiles' file tab or a file dropped on the Profiles page. A refused file never reaches the dialog. The constructor takes the file path and the `ForeignImportResult`.

From the top: `SourceText` (the file and the tool), three stat tiles (`StatCleanTile`, `StatPartialTile`, `StatSkippedTile`, from the report's counts), the rows that need a look (`NeedsLookBlock`, `NeedsLookList`: skipped, then partial), the clean rows (`CleanBlock`, `CleanList`), and `NoteText`. `PreviewName` asks `SettingsManager.UniqueProfileName`, so the preview and the landed name agree. `NoteText` joins the notes the result calls for: `Import_NothingToImport` when `HasSlots` is false, else what the profile starts and runs, `Import_NoteController` when it reads a controller, and the merged keyboard and mouse notes. Nothing the file names runs before the user accepts.

`BuildRows` turns the `TranslationReport` into `ImportReportRow` items, each a source path, an arrow and the PadForge binding, with the reason under it (`ReasonText`, which falls back to the raw string on a `FormatException`). Import (`ImportButton`, `Import_Confirm`) is disabled while `HasSlots` is false. It calls `ImportSink(profile, false)`, which `MainWindow` sets to `AddWorkshopProfile`, and `ImportedProfileName` carries the name back for the message line. The translators are on [Profile Import Internals](profile-import-internals.md).

### ChatCommandsDialog

**Files:** `Views/ChatCommandsDialog.xaml`, `Views/ChatCommandsDialog.xaml.cs`

The Twitch Chat word list (#555), from the Twitch Chat page on Extras and from the Devices page. The `TwitchChat_DialogHint` line, a Word box (`WordBox`, Enter adds) with Add, `MessageText` as a polite live region, the Words list (`WordListBox`, each row `!word` with Remove), Restore Usual Words and Close.

Every change goes through the static `ChatCommandRegistry`: `Check` returns a `WordProblem` (`TooLong` past `MaxWordLength` = 20, `Characters`, `EndsInTime`, `Reserved`), `Normalize`, `Add` (negative at `MaxWords` = 128), `Remove`, `RestoreUsualWords` and `Words`. `ProblemText` maps a problem to its `TwitchChat_Problem_*` string. See [Twitch Chat Internals](twitch-chat-internals.md).

### MapKeyLightsDialog

**Files:** `Views/MapKeyLightsDialog.xaml`, `Views/MapKeyLightsDialog.xaml.cs`

Names a keyboard's lights one at a time (#557), from the Devices page's Map Key Lights with the device's `OutputPath` and name. 820 wide, over a `MapKeyLightsViewModel`. The body holds the intro, the progress line, Start, Back, Skip, Forget and Stop, a `KeyLightsView` picture, the `MapKeyLights_NoLightHint` line, `NoteText`, and a foot with Export…, Import…, Forget All and Close. The view model lights one light, and the user presses the key under it.

While `IsListening` the window takes `PreviewKeyDown` and `PreviewKeyUp` itself. A key is found by its scan code (`ComponentDispatcher.CurrentKeyboardMessage`, then `KeyLightsView.ScanKey`), so the physical key is the one named on any layout. `NameFrom` resolves the code through `KbmHidKeyMap.UsagesOfScanKey`. AltGr's synthetic Left Ctrl is ignored (`KeyLightsView.IsAltGrLeftControl`). Names persist per product in `LearnedKeyMaps`. Import names another model's file in `MapKeyLights_ImportedOtherFormat`, and a file with no product reads `MapKeyLights_ImportNotAFile`.

### KeepDriverDialog

**Files:** `Views/KeepDriverDialog.xaml`, `Views/KeepDriverDialog.xaml.cs`

The Keep prompt after a keyboard, mouse or precision touchpad is switched to PadForge alone (#549), shown by `KeepDriverDialog.Show(owner, deviceName, seconds, mouse, touchpad)` with `KeepDriverSeconds` = 15. Titled `Devices_DriverKeepTitle` ("Keep This Keyboard in PadForge?"), `Devices_DriverKeepTitle_Mouse` or `Devices_TouchpadKeepTitle`. Windows stops typing or moving the pointer with the device at the switch, so the prompt undoes itself: only Keep keeps it, and Give It Back, Esc, the close button and the end of the countdown all return the device. Give It Back holds the focus.

A 250 ms `DispatcherTimer` reads the seconds left from a `Stopwatch` deadline set on `Loaded` (`RemainingAt`), so a busy UI thread cannot stretch the wait. `CountdownText` reads `Devices_DriverKeepCountdown_Format`. A Keep click after the deadline changes nothing (`KeepButton_Click` checks `RemainingAt` again).

### BlissBoxPlayerDialog

**Files:** `Views/BlissBoxPlayerDialog.xaml`, `Views/BlissBoxPlayerDialog.xaml.cs`

Sets a Bliss-Box port's player number (#469). Cancel holds the default and the focus. The adapter stores the number and reconnects under that player's product ID, which Windows sees as a new device (`BlissBoxPlayer_Message`). `DetailText` carries the port's line, `PlayerBox` picks 1 to 4, and `ActionButton` sets it. `Show` returns the player, or 0 when canceled. See [Bliss-Box Internals](bliss-box-internals.md).

### DreamcastScreenDialog

**Files:** `Views/DreamcastScreenDialog.xaml`, `Views/DreamcastScreenDialog.xaml.cs`

What a Dreamcast pad's VMU shows in a Bliss-Box port (#469). It works on a copy: nothing reaches the port or the profile until Save, and `Show` returns a `Result(Mode, Picture, ProfilePicture)` or null. `ModeBox` lists `DreamcastScreenMode`: The Adapter’s Picture, Profile Name, Profile Number, Profile Picture, Clock, Play Time, Chosen Picture. `PreviewImage` is drawn by `DreamcastScreenService.Preview` from the composition the service writes. `PickPicture` imports a file and warns with `DreamcastScreen_ImportFailed` when it cannot.

### FlydigiScreenDialog

**Files:** `Views/FlydigiScreenDialog.xaml`, `Views/FlydigiScreenDialog.xaml.cs`

Sends a picture to a Flydigi Apex pad's screen (#586), from the pad's Devices panel through `MainWindow.FlydigiScreen.cs`. `Show(owner, device, model, binding, ...)` opens it for the pad. `SourceBox` picks what the screen shows (`FlydigiScreenSource`: Picture, ProfilePicture, ProfileName or ProfileNumber), `FitBox` how it fits (`FlydigiScreen_Fit_Label`), with `ChoosePictureButton` and, for the profile's picture, `ChooseProfilePictureButton` and `RemoveProfilePictureButton`. `PreviewImage` is drawn from the frames that go out, decoded back, so it shows what the pad gets, and `SizeText` gives its size. Nothing reaches the pad until Send (`SendButton`), with `SendProgress` and `StatusText`. A send that fails reads one of the `FlydigiScreen_Fail_*` lines, among them `FlydigiScreen_Fail_NotWired` ("Connect the controller by cable. Its screen takes a picture over USB only."), `FlydigiScreen_Fail_PortDidNotOpen`, `FlydigiScreen_Fail_NoReply`, `FlydigiScreen_Fail_TooManyFrames`, `FlydigiScreen_Fail_Busy` and `FlydigiScreen_Fail_Fault` ("The send stopped on an error in PadForge. The log file has the details."). The source and fit are the dialog's own and saved nowhere. The profile's picture is the active profile's.

### ReleaseTestDialog

**Files:** `Views/ReleaseTestDialog.xaml`, `Views/ReleaseTestDialog.xaml.cs`

The Release Test's window (#588), from the Centering card's Release Test (`PadPage.CenteringReleaseTest_Click`). The test runs on the polling thread inside the wheel's force feedback pass (`WheelCenteringRuntime`). This window starts it with the Centering card's settings, reads its progress every `PollMs` (50 ms), and draws the result in `Chart`, a `ReleaseTraceChart` of the wheel's angle after each release before the test (`ReleaseTest_Before`) and with the measurement (`ReleaseTest_After`). `Figures` show the measured friction, inertia and damping (`FrictionFigure`, `InertiaFigure`, `DampingFigure`), and `ResultText` says what came of it. `StartBtn`, `StopBtn`, `RunAgainBtn` and `ApplyBtn` drive it. Apply keeps the measurement in `Result`, a `WheelCalibration`, and the card takes it when `ShowDialog` returns true. The test's own steps are on [Wheel Centering Internals](wheel-centering-internals.md).

### KeyboardScreenDialog

**Files:** `Views/KeyboardScreenDialog.xaml`, `Views/KeyboardScreenDialog.xaml.cs`

What one keyboard screen, or one Screen Overlay, shows (#519, #560): 700 wide, opened from the screen's row on the Devices page (`KeyboardScreen_Click`) and, for an overlay, from Choose What It Shows… on the Screen Overlay page on Extras (`MainWindow.ConfigureScreenOverlay`). Titled by `KeyboardScreenService.ScreenName(screen)`. It works on a copy until Save, and `Show` returns a `Result(Mode, Picture, PanX, PanY, ProfilePicture, Zoom, LightbarSlot)` or null.

`ModeBox` lists every `KeyboardScreenMode` through `KeyboardScreenService.ModeName`: Off, Profile Name, Profile Number, Profile Picture, Clock, Play Time, Chosen Picture, Stopwatch and Lightbar Color. The hint is `ModeHint` for a screen and `OverlayHint` for an overlay. The preview takes the screen's own shape (`KeyboardScreenFormats.SizeOf`) as large as a box of 286 by 176 holds (`PreviewSize`, `PreviewWidth`, `PreviewHeight`), scaled nearest-neighbor for a monochrome screen. For an overlay it is a `ScreenOverlayContentView` (`OverlayPreview`) in the shape of the overlay's window, 320 by 240 when none is given. By mode: Choose Picture…, Zoom (`ZoomBox`, 100 to `KeyboardScreenData.MaxZoom` = 2000, an overlay with a picture), Pan X and Pan Y (held to `PanLimits`), and a Slot picker for Lightbar Color on an overlay.

### OnScreenKeyboardWindow

**Files:** `Views/OnScreenKeyboardWindow.xaml`, `Views/OnScreenKeyboardWindow.xaml.cs`

The On-Screen Keyboard (#566), the window a Keyboard-style menu draws. A borderless, transparent, topmost `Window` (`SizeToContent="WidthAndHeight"`, `ShowActivated="False"`, `Focusable="False"`) with `WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW` on `Loaded` and the `MA_NOACTIVATE` hook, but without `WS_EX_TRANSPARENT`, so a mouse or touch screen can press its keys while the window being typed into keeps focus. `InputService.OnScreenKeyboard.cs` owns it, reads `InputManager.OnScreenKeyboardView` on the UI timer and calls `UpdateFromView`. Its `moved` and `resized` callbacks write the menu's Screen Position and Size, so the menu editor in Macros & Menus shows the change.

Keys are 42 with a gap of 5 (`KeyUnit`, `Gap`), built in code from the `OskView` snapshot: `Build` runs when the shape changes and `Restyle` recolors on other ticks. The grip resizes between `MinScalePercent` (10) and `MaxScalePercent` (400). `Place` centers the window on the menu's position in the work area, clamped with `EdgeMargin`, and `BuildHints` makes the hint line. The window keeps left-to-right order in every language (`UiLanguage.KeepLeftToRight`). Engine side: [On-Screen Keyboard Internals](on-screen-keyboard-internals.md).

### ScreenOverlay

**Files:** `Views/ScreenOverlay.xaml`, `Views/ScreenOverlay.xaml.cs`, `Views/ScreenOverlayContentView.cs`, `Views/OverlayPlacement.cs`

What a keyboard screen shows, in a borderless window on the PC's display (#560). A `Window` (`AllowsTransparency`, `Topmost`, `ShowActivated="False"`, 320 by 240, at least 80 by 60) titled `Dashboard_ScreenOverlayWindowTitle`, with `WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW`, so a macro that shows it in a game takes no focus. `InputService.KeyboardScreens.cs` keeps one window per overlay number and `SyncScreenOverlays` brings them in line with `DashboardViewModel.ScreenOverlays`, the list the Screen Overlay page on Extras edits.

While another program is in front (`SetArranging(false)`) the window carries `WS_EX_TRANSPARENT`, so clicks reach the program beneath. While PadForge is in front (`SetArranging(true)`) it takes input and shows its ember outline and corner grip. A gesture in progress holds its state (`InGesture`). The right button or one finger drags the window, the left button pans a zoomed picture (`PanDragged`), the grip resizes, and both raise `PositionChanged`, which writes the item's place and size. `KeepOnTop` re-asserts the window's place over other programs' windows once a second (PadForge's own are skipped through `IsOurWindow`). `SetContentOpacity` lands on the content alone. `ShowContent` sets `EmptyHint` from the blank reason, shown only while arranging.

`ScreenOverlayContentView` is a `FrameworkElement` that draws a `ScreenOverlayContent` in `OnRender`, in the overlay and in the dialog's preview: a color fills the bounds, a picture scales to fit with its proportions kept and pans within `PanLimits`, and text is white on black, as large as fits. `OverlayPlacement` holds the DPI-safe placement the Touchpad Overlay and the Screen Overlay share: `NoPlace`, `HasPlace`, `MoveToMonitor`, `EnsureOnScreen`, `IsOnScreen` and `GetCurrentMonitor`.

---

## Custom Controls

All in `PadForge.App/Controls/` (`PadForge.Controls` namespace) unless noted. Many exist to give UI Automation an accurate peer without changing a pixel for a mouse user. The others are the panels and parts the PadForge 6 boards are built from.

### Buttons and Inputs

| Control | File | What it does |
|---------|------|--------------|
| `ClickBorder` | `ClickBorder.cs` | A `Border` that acts as a button (chips, swatches, tiles, the title bar's search box). Raises `Click` where its mouse handler ran, and from Enter, Space or a screen reader's Invoke. Its peer reports invoke, selection and toggle |
| `SegmentButton` | `SegmentButton.cs` | A `Button` that is one choice of a set, such as the type bar's types. Its peer reports a radio button whose state is `IsSelected` |
| `StateToggleButton` | `StateToggleButton.cs` | A `Button` that turns something on and off (a slot's power, the engine, full screen). `IsOn` drives a toggle peer |
| `AvailabilityButton` | `AvailabilityButton.cs` | A `Button` that stays clickable and unchanged while its choice is unavailable. Its handler then does nothing and its peer reports it unavailable |
| `SettingResetButton` | `SettingResetButton.cs` | The per-setting reset button, a `Wpf.Ui.Controls.Button` with the icon style and a localized `SettingLabel` |
| `RangeSlider` | `RangeSlider.cs` | The two-thumb slider. Each thumb is a `RangeThumb`, a Tab stop that the arrow keys, Page Up, Page Down, Home and End move, read by `RangeThumbPeer` as a slider named by the range |
| `SearchField` | `SearchField.cs` | A 34 tall search field with a magnifier and a placeholder, styled in `Resources/Shell.xaml` (`SearchFieldInput`) |
| `CurveEditor` | `CurveEditor.xaml` | The response-curve editor of the stick and trigger cards |
| `EqCurveControl` | `EqCurveControl.cs` | The graphic EQ's log-frequency curve with one handle per band (#347), drawn in `OnRender` |
| `SwitchLook` | `SwitchLook.cs` | How a `CheckBox` in the `SwitchCheckBox` style draws as a switch while it stays a check box |

### Panels and Layout

| Control | File | What it does |
|---------|------|--------------|
| `FlexLinePanel` | `FlexLinePanel.cs` | A line of parts that wraps. Each part has a `Basis` and may `Grow`, `AtEnd` puts a part at the line's end, and `EndsApart` spreads the two ends |
| `TileGridPanel` | `TileGridPanel.cs` | Rows of equal columns: as many as fit at `MinItemWidth` with `Gap` between, each an equal share, so a row ends flush with the edge. `FillRows`, `MaxColumns`, `Balance` (four never stand three and one) and `TakesRest` (a part takes what its row leaves) |
| `HeadRowPanel` | `HeadRowPanel.cs` | A card head in two parts, leading and trailing, on one line while both fit and one under the other when not (`LeadingMinWidth`) |
| `PartBodyPanel` | `PartBodyPanel.cs` | A part card's body: the settings most people change beside the live view, stacked when the card is narrow (`SettingsWidth`) |
| `SettingRow` | `SettingRow.cs` | One setting's row: label, control, value, and what belongs at its far end (the reset, a Test button). `Reach` caps how far the parts spread (default 660), and the Ends layout (`Ends`, `Aside`, `EndsWidths`) puts the controls at the row's end |
| `SettingItem` | `SettingItem.cs` | One thing the Settings search shows or hides, with the hairline over it (`Rule`) |
| `SettingSearch` | `SettingSearch.cs` | The Settings page's search: `Group` and `Card` names, `Words`, `Filter` and `Clear` |
| `FoldList` | `FoldList.cs` | One card that lists parts which fold to a line each, with a hairline between them, drawing the card's fill, edge and corners itself |
| `FoldPart`, `FoldCard`, `MoreRow` | `FoldPart.cs` | An `Expander` that remembers whether it is open (`StateKey`, kept by `CardFoldState` in the settings file). `FoldCard` folds to one line (chevron, header, hint, value, `Switch`, `HeaderAction`), and `MoreRow` is the More row at a card's foot |
| `ShownPart` | `ShownPart.cs` | A part made when it first shows, and kept, collapsed, after |
| `ListCellsPanel`, `ListTagPanel`, `SourceLinePanel`, `SourceBox` | | The mappings list's cells, an input's line in a cell, a source's line and its box |
| `StillRowPanel` | `StillRowPanel.cs` | The row of controller pictures on a profile's card, at one size that shrinks to fit |
| `LeadItems` | `LeadItems.cs` | Parts a panel makes from a list and stands before its own, as a macro trigger's inputs stand before Record |
| `ShellDialog` | `ShellDialog.cs` | A dialog drawn over the page area (Add a Controller, Search): `FrameMaxWidth`, `ClosesOnGroundPress`, `Open(opener)`, `Close(returnFocus)`, `CloseRequested` |
| `ContentTabControl` | `ContentTabControl.cs` | A header-less `TabControl` whose peer lists the selected content, for a page that draws its own tabs |
| `NavItemsControl` | `NavItemsControl.cs` | The sidebar's lists, whose entries offer Invoke and SelectionItem to UI Automation (`NavItemAutomationPeer`) |
| `PickTemplateSelector` | `PickTemplateSelector.cs` | The two looks of a picker's choice: name and line in the open list, the name alone in the closed box |

### Light, State and Pictures

| Control | File | What it does |
|---------|------|--------------|
| `Halo` | `Halo.cs` | The light around something live: a soft halo behind its child, outside its rounded edge. `IsLit` fades it in and out, `Breathes` makes it rise and fall, `Radius`, `Strength` and `Rim` shape it, and it honors the system's animation setting |
| `Heat` | `Heat.cs` | The inherited attached `Heat.IsLive`: whether what an element shows belongs to something live, read by the shared parts inside a card |
| `Appear` | `Appear.cs` | Fades an element in when what it shows arrives, such as a Home card's picture |
| `BatteryMeter` | `BatteryMeter.cs` | A battery drawn as a meter, colored by state |
| `LevelBar` | `LevelBar.cs` | A thin bar for a live level, drawn in one pass |
| `ExtraTile` | `ExtraTile.cs` | An extra's tile: switch, glyph, title, line, status, the routed `OpenRequested`, and a second button that opens the page (`HomeExtraTile` on Home) |
| `ExtraBadge`, `StatusFlame` | `ExtraMarks.cs` | The square at the head of an extra's page, and the flame of its status card |
| `LiveStage`, `LiveArtStage` | `LiveStage.cs`, `LiveArtStage.cs` | A Home card's controller, moving: the 3D model its still was drawn from, or the layers of its 2D art |
| `HeldGlow` | `HeldGlow.cs` | The ember glow over each held control on a Home card's still picture |
| `GyroHorizon`, `CenterBar`, `TouchSurface` | `LiveViews.cs` | The gyro card's horizon dial, a rate bar that grows from its middle, and the touchpad card's live view |
| `SteeringTorqueChart`, `ReleaseTraceChart` | `SteeringCharts.cs` | The Centering card's torque chart and the Release Test's trace (#588) |
| `CrosshairView` | `CrosshairView.cs` | One crosshair, drawn in the display's pixels (#585) |
| `LensFrameView`, `SpotlightHoleView` | `MagnifierViews.cs` | The magnifier's lens border and spotlight hole (#585) |
| `MarqueeLabel` | `MarqueeLabel.cs` | One line that trims at rest and, while `Active`, scrolls a text too long for it. The whole text is the tooltip. The moving copy starts at its text's first letter, a Latin name at the left edge and an Arabic or Hebrew one at the right, in a window of either direction. The pills and cards use it for the Preset |
| `KindIcon` | `KindIcon.cs` | A device kind's icon: an MDL2 glyph, or a line drawing for a wheel or a joystick |
| `KeyHint` | `KeyHint.cs` | A hint with keys drawn as key labels, at Search's foot |
| `NamedPicture` | `NamedPicture.cs` | A drawing that tells a screen reader what it shows |
| `ListLabel` | `ListLabel.cs` | A label that leads a list's entries as one of its items (Used By on the Devices page), whose peer is neither a control nor a content element |
| `GlyphText` | `GlyphText.cs` | A `TextBlock` for an icon glyph (Segoe MDL2 Assets or Segoe Fluent Icons), outside the control view |
| `DecorativeFontIcon`, `DecorativeSymbolIcon`, `DecorativeStrokeIcon`, `DecorativeImage` | `DecorativeIcons.cs`, `DecorativeImage.cs` | Icons and images that only decorate, hidden from screen readers (`DecorativeIconPeer`). `DecorativeStrokeIcon` draws one geometry on a 24 by 24 grid with a round stroke in its inherited `Foreground`, which is how the sidebar's entries take their quiet and ember colors |
| `BaseStyle` | `BaseStyle.cs` | Gives a control subclass the implicit style its base class has |
| `HeldModifiers` | `HeldModifiers.cs` | The modifier keys held now, for a control that reads its own keys |
| `TriggerTravelArc` | `TriggerTravelArc.xaml` | The trigger travel gauge |

`Views/Controls/` holds `LabeledShapeIcon` (the labeled shape icon), `ProfilePill` (the title bar's profile pill) and `TriggerEffectGraph` (the adaptive-trigger effect graph). Code-only views in `Views/`: `KeyLightsView` (the Key Colors picture), `ScreenOverlayContentView`, `OverlayPlacement`, `TouchSensorStrip`, `TagLight`, `LegendColumn`, `WorkshopControllerPreview` and `GunCalibrationScreen`.

---

## Value Converters

All in `PadForge.App/Converter/` (`PadForge.Converters` namespace). `App.xaml` registers them as `StaticResource`s: `ResetAllNameConverter` with the Reset All button style, the rest together after the styles. `PadPage.xaml` registers `FractionToPercentConverter`, which lives in `PadPage.xaml.cs`.

| Converter | Key | Description |
|-----------|-----|-------------|
| `BoolToVisibilityConverter` | `BoolToVisibilityConverter` | `true` Visible, `false` Collapsed. Parameter `Invert` reverses. Two-way |
| `NullToCollapsedConverter` | `NullToCollapsedConverter` | Non-null Visible, null Collapsed |
| `StringToVisibilityConverter` | `StringToVisibility` | Non-empty Visible, else Collapsed |
| `EnumIndexConverter` | `EnumIndexConverter` | An enum and `ComboBox.SelectedIndex`, values assumed 0 to N. Two-way |
| `EnumEqualityVisibilityConverter` | `EnumEqualityVisibilityConverter` | Visible when the enum's name matches the parameter (case-insensitive, `|`-separated) |
| `EnumEqualityConverter` | `EnumEqualityConverter` | Its bool twin, one way: drives `IsChecked` on the segment radios (Home's Cards, the Devices filters) |
| `DzShapeNameConverter` | `DzShapeNameConverter` | A deadzone shape index to its localized name |
| `EqBandTypeNameConverter` | `EqBandTypeNameConverter` | An `EqBandType` to its localized name |
| `HexToBrushConverter` | `HexToBrushConverter` | `#AARRGGBB` or `#RRGGBB` to a brush, gray #555555 when empty or invalid |
| `RgbToBrushConverter` | `RgbToBrushConverter` | `MultiBinding(R, G, B)` to a brush, black on failure |
| `NormToCanvasConverter` | `NormToCanvasConverter` | 0 to 1 to a canvas position, dot-centered. Parameter `canvasDim` or `canvasDim,dotSize` |
| `SignedNormToCanvasConverter` | `SignedNormToCanvasConverter` | -1 to +1 to a canvas position, for the constant-force pad |
| `PercentToSizeConverter` | `PercentToSizeConverter` | 0 to 100 to a size, the parameter the maximum |
| `CrossGeometryConverter`, `SlopedWedgeGeometryConverter` | same | `MultiBinding(DeadZoneX, DeadZoneY)` to the axial cross and the sloped wedges of the deadzone overlay |
| `BoolToTriggerShapeKindConverter` | `BoolToTriggerShapeKindConverter` | `false` TriggerLeft, `true` TriggerRight |
| `IndexToLetterConverter` | `IndexToLetterConverter` | 0 to 25 to `a` to `z`, `s[N]` past that, for formula chips |
| `IndexLessThanVisibilityConverter` | `IndexLessThanVisibilityConverter` | Visible while the parameter is below the count |
| `OneBasedIndexConverter` | `OneBasedIndexConverter` | A 0-based index as its 1-based number |
| `LogScaleConverter` | `LogScaleConverter` | A whole number from 1 to the parameter on a 0 to 100 slider by its logarithm |
| `CultureLanguageConverter` | `CultureLanguageConverter` | A culture to the `XmlLanguage` a language picker row declares (`UiLanguage.Declared`) |
| `BytePercentConverter` | `BytePercentConverter` | A byte setting (0 to 255) as a whole percent, and back |
| `BracketPartConverter` | `BracketPartConverter` | Part 0, 1 or 2 of a string around its first pair of square brackets, so a sentence of the strings table draws its bracketed words as a link (the Extras notes) |
| `ResetAllNameConverter` | `ResetAllNameConverter` | A Reset All button's accessible name from its words and tooltip |
| `OnOffTextConverter` | `OnOffTextConverter` | A folded card's state, On or Off, from one or more flags |
| `AnyOnConverter` | `AnyOnConverter` | Whether any flag is on, for a feature line's ember icon |
| `FormatTextConverter` | `FormatTextConverter` | Values, then the format they go into, from the strings table |
| `OneOrManyFormatConverter` | `OneOrManyFormatConverter` | A count with its noun in the one or many form |
| (made in `HomeExtraTile`) | `SoftBreakAddressConverter` | A status line with a zero-width break place after each `://` and before each port's colon, so a wrapped address breaks there and never inside a number. The tile's `AutomationProperties.ItemStatus` keeps the plain string |
| `ShownNamesConverter` | `ShownNamesConverter` | A fold's hint naming only the rows the fold shows |
| `OptionTextConverter`, `IndexTextConverter` | same | A folded card's line for a value picked from a list, by value or by place |
| `FractionToPercentConverter` | `FractionToPercentConverter` (PadPage) | A 0 to 1 setting as 0 to 100, two-way, for the touchpad rows |

The fold converters are in `FoldSummaryConverters.cs`. Each takes a strings-table string as one of its values, so a change of language reads the line again.

---

## Resource Dictionaries and Theming

### App.xaml Resources

`App.xaml` merges, in order: `ui:ThemesDictionary Theme="Dark"` (the design-time default), `ui:ControlsDictionary`, a dictionary of the two font families, `Resources/ControllerIcons.xaml`, `Resources/Shell.xaml`, then the ember tokens dictionary (the brushes, `MiniTypeButtonActiveStyle`, `FlameOuterGeometry`, `LivenessFlameBase`). The root dictionary holds the app's own styles and the converters. Every dialog merges `Resources/Dialogs.xaml` itself (see [Dialog Windows](#dialog-windows)).

PadForge 6 uses one family for every word and number, Segoe UI Variable: `BodyFontFamily` ("Segoe UI Variable Text, Segoe UI") for body sizes and `DisplayFontFamily` ("Segoe UI Variable Display, Segoe UI") from 18 up. There is no monospace face. A number that changes or stands in a column keeps the body face and sets `Typography.NumeralAlignment="Tabular"`, and its cold color marks it as measured. The fonts merge ahead of `ControllerIcons.xaml`, since its `StaticResource` font references see only earlier dictionaries.

| Key (or implicit target) | What it does |
|--------------------------|--------------|
| `EmberIconButton` / `EmberIconButtonHot` | Icon buttons. Hot is the sidebar pill's delete X |
| `ResetAllButton` | A card's Reset All, its accessible name from `ResetAllNameConverter` |
| `CardCloseButton` | A card's X (Home's delete, the Devices row's remove) |
| `EmberAccentButton`, `EmberPrimaryButton`, `EmberOutlineButton` | The affirmative buttons (Home's Use It is `EmberPrimaryButton`) |
| `EmberDestructiveButton` | Destructive confirms |
| `QuietButton`, `LinkButton` | A quiet worded button, and a link drawn as a button |
| `EmberSelectListItem` | A `ListBoxItem` with an ember wash when selected |
| `EmberSlider` | The single-thumb slider with an ember fill |
| `InstrumentBarRaw` / `InstrumentBarOut` | The raw and output level `ProgressBar`s |
| `EmberFocusVisual` | The ember keyboard-focus ring |
| `EntranceFade` | A short fade on `Loaded` for page and card roots |
| `MiniTypeButtonActiveStyle` | A type chip's tile: the pill's chip and the type bar's lit choice, its `Background` set by the caller (`EmberBrush` or `SteelLineBrush`) |
| `LivenessFlameBase` | An outline flame at rest, which a site fills ember while its device is online |

### ControllerIcons.xaml

`Resources/ControllerIcons.xaml` holds the shared card, chip and part styles and the stick and trigger geometries:

| Key | What it is |
|-----|------------|
| `CardBorder` | The card: `CardBackgroundFillColorDefaultBrush`, corner 12, padding 20,14,12,12, bottom margin 16, a 1 px `CardStrokeColorDefaultBrush` edge |
| `CardTitle` | 16 SemiBold in the body face |
| `HeroCardTitle` | 18 SemiBold in the display face, a part card's title |
| `CardSubsectionTitle`, `CardDescription` | A card's subheading and its description |
| `SectionTitle` | 13 SemiBold, secondary, heading level 2 |
| `PageSectionTitle` | 15 SemiBold, primary, heading level 2 (Home's Controllers, the Extras groups) |
| `StatLabel` | 12 SemiBold, tertiary, the label under a number |
| `StatePill` | The state pill: a flame and the state's word, the controller's switch |
| `ChipEmber`, `ChipGhost`, `ChipSteel` | Chips |
| `SegmentTrack`, `SegmentRadio` | A segmented choice (Home's Cards, the Devices filters) |
| `FoldHeaderToggle`, `MoreHeaderToggle`, `MoreCardRow`, `CardFoldList` | The fold parts' looks |
| `PartIconGlyph`, `PartTray`, `PartLine`, `LiveWell`, `CardFootLink` | A part card's pieces |
| `LegendPill`, `LegendPillEmber`, `LegendPillCold` | The legend tags |
| `StageGlyphText`, `StageGlyphShape`, `StageChipTemplate` | A card's stage chips |
| `SwitchCheckBox` | A `CheckBox` drawn as a switch |
| `TypeTileButton`, `TypeTileFocusVisual` | Add a Controller's type tiles |
| `HomeExtraTile`, `ExtraTileOpenButton` | Home's extra tiles |
| `ZackslyStickOuterRingGeometry`, `ZackslyStickInnerDiscGeometry`, `ZackslyStickGeometry`, `ZackslyTriggerOuterBodyGeometry`, `ZackslyTriggerOuterBodyRightGeometry`, `SteeringWheelGeometry`, `TouchpadStickIconGeometry` | Stick, trigger, wheel and touchpad icon geometries |

### Shell.xaml

`Resources/Shell.xaml` holds the sidebar's two templates (see [Sidebar Construction](#sidebar-construction)), the line icons (`NavHomeGeometry`, `NavDevicesGeometry`, `NavProfilesGeometry`, `NavExtrasGeometry`, `NavSettingsGeometry`, `NavAboutGeometry`, `SectionButtonsGeometry`, `SectionRumbleGeometry`, `SectionMotionGeometry`, `SectionLightsGeometry`, `SectionMacrosGeometry`, `SearchLineGeometry`, `PlusLineGeometry`, `CloseLineGeometry`, `BluetoothLineGeometry`, `UsbLineGeometry` and others), the key chip (`KeyChip`, `KeyChipText`), the title bar's search box style (`TitleSearchBox`) and the search field (`SearchFieldInput`). `Themes/Generic.xaml` holds the range slider's thumb (`RangeSliderThumbStyle`, `RangeSliderThumbFocus`).

### Theme Switching

`SettingsViewModel.SelectedThemeIndex`: 0 follows Windows, 1 is Light, 2 is Dark. `MainWindow.OnThemeChanged` calls `ApplicationThemeManager.Apply(ApplicationTheme.Light)`, `Apply(ApplicationTheme.Dark)` or `ApplySystemTheme()`, then `EmberTheme.ApplyAccent()` and `UpdateSteelLayer()`, which shows `SteelLayer` in Dark only. Code that builds visuals takes its brushes by resource reference (`SetResourceReference`), so a theme change recolors them without a rebuild. The KBM, MIDI and mouse previews rebuild their visuals when the theme changes. The light theme keeps the system's Mica with white cards: its surfaces were not redesigned for PadForge 6.

### Ember Identity Brushes

The ember tokens dictionary in `App.xaml` defines the dark values. `EmberTheme.ApplyAccent` (`Common/EmberTheme.cs`) sets the theme-paired ones on each change.

| Brush Key | Dark value | Usage |
|-----------|-----------|-------|
| `EmberBrush` / `EmberHotBrush` / `EmberDeepBrush` | #FF6B2C / #FF8A57 / #C43D0C | The virtual side: outputs, live state, marks and fills |
| `EmberTextBrush` | #FF6B2C | Words in ember. Light theme #C24A12, so the text keeps its contrast on white |
| `EmberTintBrush` / `EmberWashBrush` / `EmberPickBrush` / `EmberInkBrush` | #1AFF6B2C / #0DFF6B2C / #1D1611 / #160A03 | Washes, the picked pill's fill, dark ink on an ember tile |
| `ColdBrush` / `ColdTintBrush` | #7CC7EA / #1A7CC7EA | The physical side: devices, sources, measured numbers |
| `SteelWindowBrush` / `SteelGroundBrush` / `SteelPaneBrush` / `SteelFootBrush` / `SteelRaisedBrush` | #070A10 / #0A0E15 / #0A0E16 / #101722 / #18202E | The title bar, the window's ground, the sidebar, the engine block, raised surfaces |
| `SteelLineBrush` / `SteelLineSoftBrush` / `DashLineBrush` | #2A3546 / #1E2734 / #344154 | Hairlines and the dashed Add Controller outline |
| `WaitBrush` | #F2B84B | The only gold: waiting flames. Light theme #8F6200 |

Green, gold and red are for health alone, and `WaitBrush` is the one gold. `ThemeContrastTests` holds the text colors to 4.5 to 1 in both themes and scans every XAML file for words in the raw ember.

---

## Common XAML Patterns

### Card-Based Layout

```xml
<Border Style="{StaticResource CardBorder}">
    <StackPanel>
        <TextBlock Text="{Binding Settings_InputEngine, Source={x:Static strings:Strings.Instance}}"
                   Style="{StaticResource CardTitle}"/>
        <controls:SettingRow MinHeight="44">
            <TextBlock Text="{Binding Settings_PollingRate, Source={x:Static strings:Strings.Instance}}"/>
            <ui:NumberBox Value="{Binding PollingRateHz, Mode=TwoWay, UpdateSourceTrigger=PropertyChanged}"
                          Minimum="60" Maximum="10000"/>
            <!-- the setting's reset -->
        </controls:SettingRow>
    </StackPanel>
</Border>
```

A card that folds stands in a `FoldList` as one or more `FoldCard`s, and a card's less used settings sit under a `MoreRow`.

### Liveness Flame and Light

Online and offline state renders as a flame `Path`, not a colored dot. `LivenessFlameBase` draws an outline flame at rest, and a site adds a `DataTrigger` that fills it with `EmberBrush` while the device is online. A slot's flame follows its heat: ember while forging, gold (`WaitBrush`) while waiting, the outline while cold. A live element stands in a `Halo` whose `IsLit` is bound to that state.

### Icons

The shell's icons are line geometries drawn by `DecorativeStrokeIcon` (`Resources/Shell.xaml`). Segoe MDL2 Assets glyphs remain for the types that have no logo (Keyboard + Mouse `E961`, MIDI `E8D6`, VR `F119`), the extras' glyphs, the cards' part icons and many buttons, drawn by `GlyphText` or `KindIcon`.

### WPF UI NumberBox

Every `ui:NumberBox` binds with `UpdateSourceTrigger=PropertyChanged`. WPF UI writes `Value` back on `LostFocus`, and the spin buttons step without focusing the box, so a box bound without the trigger saved nothing from its arrows (#511). A box bound to a port adds `Delay=1000`, because a port change restarts its server. `NumberBoxCommitTests` holds every box in the app to both rules.

### Localized String Bindings

All user-facing text binds through `Strings.Instance`:

```xml
<TextBlock Text="{Binding Settings_Title, Source={x:Static strings:Strings.Instance}}"/>
```

The language switches at runtime without a restart. Code-built text reads `Strings.Instance` and is rebuilt on `Strings.CultureChanged` or `OnCultureChanged`. A sentence whose middle is a link or a set-off value is three runs on one line of markup (a lead, the value, a tail), since a line break between runs adds a space.

### Overflow Text

A long name (a Preset, a device) is a `MarqueeLabel`: it trims at rest and scrolls while its `Active` is bound to the card's or pill's `IsMouseOver`.

---

## Code-Behind Patterns

### Bind/Unbind Pattern

The six preview views (`ControllerModelView`, `ControllerModel2DView`, `ControllerSchematicView`, `MidiPreviewView`, `KBMPreviewView`, `VRPreviewView`) share:

```csharp
public void Bind(PadViewModel vm)    // subscribe, hook rendering, load the model
public void Unbind()                 // stop the flash, unhook rendering, drop the view model
```

`PadPage.BindActiveModelView` unbinds all six and binds the active one.

### CompositionTarget.Rendering with Dirty Flag

Per-frame updates through `CompositionTarget.Rendering`, gated by a `_dirty` flag that property changes set, so several changes make one update per frame:

```csharp
private bool _dirty;

private void OnRendering(object sender, EventArgs e)
{
    if (!_dirty || _vm == null) return;
    _dirty = false;
    // update visuals
}
```

### DispatcherTimer Flash Animation

A view flashes the control Map All or a recording waits on with a `DispatcherTimer`: 400 ms in the 3D, 2D, schematic, KBM and MIDI views, 450 ms in the VR preview.

### Event Relay Pattern

Pages raise events that `MainWindow.xaml.cs` wires to services, so a view knows no service:

```csharp
// HomePage.xaml.cs
public event EventHandler<int> DeleteSlotRequested;
private void DeleteSlot_Click(object sender, RoutedEventArgs e)
{
    if (sender is Button btn && btn.Tag is int slotIndex)
        DeleteSlotRequested?.Invoke(this, slotIndex);
}

// MainWindow.xaml.cs
HomePageView.DeleteSlotRequested += (s, slotIndex) => DeleteSlotDeferred(slotIndex);

private void DeleteSlotDeferred(int slotIndex)
{
    Dispatcher.BeginInvoke(new Action(() =>
    {
        if (_viewModel.SelectedPadIndex == slotIndex)
            SelectNavItemByTag("Home");
        bool hadActiveVc = _inputService.IsHmVcAt(slotIndex);
        var info = _deviceService.DeleteSlot(slotIndex);
        _inputService.OnSlotDeleted(slotIndex, info.Type, info.OldGroupPosition,
            deletedSlotHadActiveVc: hadActiveVc);
        _viewModel.Devices.RefreshSlotButtons();
        _inputService.RefreshDeviceList();
    }));
}
```

The controller page's Delete (`PadPageView.DeleteRequested`) and the pill's X run the same `DeleteSlotDeferred`.

### Syncing Guard Pattern

A flag keeps a handler out while code sets the control it handles:

```csharp
private bool _syncingExtendedConfig;

private void SyncExtendedConfigBar()
{
    if (DataContext is not PadViewModel vm) return;
    bool isExtended = vm.OutputType == Engine.VirtualControllerType.Extended;
    bool isKbm = vm.OutputType == Engine.VirtualControllerType.KeyboardMouse;

    HMaestroProfileBar.Visibility = (vm.HasHMaestroProfileBar || isKbm)
        ? Visibility.Visible : Visibility.Collapsed;
    HMaestroProfileCombo.Visibility = isKbm ? Visibility.Collapsed : Visibility.Visible;
    KbmSurfacesCombo.Visibility = isKbm ? Visibility.Visible : Visibility.Collapsed;

    if (isExtended)
    {
        _syncingExtendedConfig = true;
        SyncExtendedFields(vm);
        _syncingExtendedConfig = false;
    }
}

private void ExtendedCustomize_Toggled(object sender, RoutedEventArgs e)
{
    if (_syncingExtendedConfig) return;
    if (DataContext is not PadViewModel vm || vm.ExtendedConfig == null) return;
    vm.ExtendedConfig.Customize = ExtendedCustomizeChk.IsChecked == true;
}
```

`PadPage` uses the same idea for the section strip (`_syncingStrip`) and the Screen Color display (`_syncingScreenDisplay`).

---

## See Also

- [Architecture Overview](architecture-overview.md): Application shell, page hosting, WPF UI theme
- [ViewModels](viewmodels.md): `PadViewModel`, `DashboardViewModel` (Home and Extras), `DevicesViewModel`, `SettingsViewModel`
- [Services Layer](services-layer.md): `InputService`, `SettingsService`, `DeviceService` wired in `MainWindow.xaml.cs`
- [2D Overlay System](2d-overlay-system.md): `ControllerModel2DView`, `ControllerSchematicView`, `KBMPreviewView`, `MidiPreviewView`, `VRPreviewView`
- [3D Model System](3d-model-system.md): `ControllerModelView` (HelixToolkit 3D viewport) and the stills Home's cards show
- [Profile Import Internals](profile-import-internals.md): The translators and report behind `ImportConfigDialog`
- [Steam Workshop Config Import Internals](steam-workshop-import-internals.md): The Community tab of Get Profiles
- [On-Screen Keyboard Internals](on-screen-keyboard-internals.md): The engine side of `OnScreenKeyboardWindow` and the Keyboard menu style
- [Screen Color Internals](screen-color-internals.md): The capture and color math behind the Lights section's Screen Color mode
- [Twitch Chat Internals](twitch-chat-internals.md): The chat reader, the command words and the claim rules behind `ChatCommandsDialog`
- [Wheel Centering Internals](wheel-centering-internals.md): The engine behind the Centering card and `ReleaseTestDialog`
- [Settings and Serialization](settings-and-serialization.md): `PadSetting` descriptors behind the mapping rows, and the open cards the settings file keeps
- [Peripheral Outputs Internals](peripheral-outputs-internals.md): The links, claims and backend states the Lights and Rumble route lines read
- [Virtual Controllers](../features/virtual-controllers.md): The seven output types Add a Controller and the type bar offer (all HIDMaestro-backed types are produced by `HMaestroVirtualController`, VR by `HMaestroVRController`)
- [Driver Installation Internals](driver-installation-internals.md): HidHide, BthPS3 and Windows MIDI Services installs and removals, run from `SettingsPage` (HIDMaestro is embedded)

---

*Last updated for PadForge 6.0.0.*
