# Crosshair and Magnifier Internals

*How the crosshairs are drawn in their own click-through windows, and how the magnifier's lens, full-screen zoom and spotlight are built on Windows' Magnification API.*

For the user-facing side see [Crosshair](../features/crosshair.md) and [Magnifier](../features/magnifier.md).

| File | Responsibility |
| --- | --- |
| `PadForge.App/Services/CrosshairData.cs` | `CrosshairData` and `MagnifierData`, the saved settings with their ranges and `Normalize()`. The `CrosshairStyle`, `MagnifierMode`, `MagnifierFollow` and `LensShape` enums, saved by ordinal. `CrosshairChoice`, a line of the Toggle Crosshair macro's box. |
| `PadForge.App/ViewModels/CrosshairItem.cs` | One crosshair's card: its properties in whole pixels, its status, its resets, and `Look`, a fresh copy of its data after every change. |
| `PadForge.App/ViewModels/MagnifierItem.cs` | The magnifier's page: its properties, its status and failure, its resets. |
| `PadForge.App/ViewModels/DashboardViewModel.Crosshairs.cs` | The crosshair list (at least one, up to ten), the magnifier, and their load and snapshot for the settings file. |
| `PadForge.App/Services/InputService.Crosshairs.cs` | Brings the windows into line with the pages and the macros, on the UI thread. |
| `PadForge.App/Views/PixelOverlay.cs` | `PixelOverlay`, a click-through topmost window placed in pixels, and `CrosshairOverlay`, one crosshair's window. |
| `PadForge.App/Controls/CrosshairView.cs` | Draws a crosshair in the display's pixels, for the window and for the card's preview. |
| `PadForge.App/Common/Crosshairs/CrosshairShape.cs` | A crosshair's geometry around its center, and the room it takes. |
| `PadForge.App/Common/Crosshairs/CrosshairPictures.cs` | Reads a picture crosshair's file, with a cache of ten. |
| `PadForge.App/Common/Crosshairs/CrosshairPlace.cs` | `CrosshairPlace` (a crosshair's point and window) and `MagnifierMath` (the lens, its source, the full-screen offsets and the spotlight's hole), all in pixels. |
| `PadForge.App/Common/Crosshairs/DisplayBounds.cs` | The displays' bounds, read from Windows on each call. |
| `PadForge.App/Common/Crosshairs/MagnifierNative.cs` | The Magnification API and the two plain Win32 windows: the lens's host and the spotlight's shade. |
| `PadForge.App/Services/MagnifierService.cs` | The magnifier in its three modes. |
| `PadForge.App/Controls/MagnifierViews.cs` | `LensFrameView`, the lens's border, and `SpotlightHoleView`, the spotlight's circle. |
| `PadForge.App/Common/Input/InputManager.Crosshairs.cs` | The macros' requests, handed from the polling thread to the UI thread. |
| `PadForge.App/Views/ExtrasPage.xaml` | The Crosshair and Magnifier pages (`CrosshairPage`, `MagnifierPage`). |

The design follows three references: Crosshair-Overlay (c-m-w) for the window styles, the polygon ring, the outline and the pixel rounding, the CS:GO crosshair generator (Skarbo/CSGOCrosshair) for the classic cross, and Microsoft's Magnification samples in Windows-classic-samples for the lens and the full-screen zoom.

---

## Settings and state

`CrosshairData` and `MagnifierData` are saved in `AppSettingsData` and in every `ProfileData`, as `<Crosshairs>` (one `<Crosshair Number="n">` each) and `<Magnifier>`. A file or profile with no `<Crosshairs>` reads as one crosshair, off, and one with no `<Magnifier>` as the magnifier's defaults, off. `LoadCrosshairs` drops an entry whose number is outside 1 to 10 or already taken. `CrosshairData.MaxCrosshairs` is 10, reWASD's count.

Each value goes through `Normalize()` on load, so a file edited by hand cannot put a crosshair out of range:

| Value | Range | Default |
|---|---|---|
| Offset X, Y | -4000 to 4000 px | 0 |
| Length | 0 to 200 | 10 |
| Thickness | 1 to 40 | 2 |
| Gap | -20 to 200 | 4 |
| Outline thickness | 1 to 10 | 1 |
| Radius | 2 to 400 | 12 |
| Sides | 3 to 64 | 64 |
| Dot size | 1 to 100 | 4 |
| Picture width, height | 1 to 8000 | 64 |
| Rotation | 0 to 359 | 0 |
| Magnifier zoom | 1.25 to 16 | 2 |
| Lens width, height | 80 to 2000 | 400 |
| Border thickness | 1 to 20 | 4 |
| Spotlight size | 40 to 2000 | 400 |
| Spotlight dim | 0.1 to 0.95 | 0.6 |

A display is saved by its Windows name (`\\.\DISPLAY2`), as Screen Color saves one. Empty is the primary display.

`CrosshairItem` holds its values in whole pixels and builds a new `Look` after every change. The window and the preview both draw from `Look`, so a change reaches both at once. `MagnifierItem.LensShape` sets the height to the width when the shape turns round, and `LensWidth` keeps the two equal while it is round, so a round lens stays a circle. `MagnifierItem.Load` sets the shape before the sizes, so a saved rectangle keeps its height.

A change raises `Crosshairs` or `Magnifier` on `DashboardViewModel`. `InputService.OnDashboardPropertyChanged` (`InputService.cs` line 11782) answers with `ScheduleCrosshairSync` or `ScheduleMagnifierSync`, which queue one sync on the dispatcher however many changes arrive.

---

## Crosshair windows

`PixelOverlay` (`PixelOverlay.cs` line 27) is a WPF window with no border, a transparent background, `Topmost` on and no taskbar button. `OnSourceInitialized` (`PixelOverlay.cs` line 90) adds `WS_EX_NOACTIVATE`, `WS_EX_TOOLWINDOW` and `WS_EX_TRANSPARENT` before it first shows, and the window answers `WM_MOUSEACTIVATE` with `MA_NOACTIVATE`. These are the styles Crosshair-Overlay gives its window (`Window.hpp`, `uUninteractableExtendedStyle`). The window never takes the focus and every click goes through it.

`PlaceAt` (`PixelOverlay.cs` line 112) places it with `SetWindowPos` in pixels rather than through `Left` and `Top` in DIPs, and places it a second time when WPF resized it on a move to a display of another scale. What it draws lands on whole pixels on a display of any scale.

`CrosshairOverlay` (`PixelOverlay.cs` line 149) is one crosshair's window. It covers only what the crosshair draws: `CrosshairPlace.Window` (`CrosshairPlace.cs` line 25) takes the shape's bounds around the point `CrosshairPlace.Center` (`CrosshairPlace.cs` line 15) gives, adds a pixel on each side for a smoothed edge, and cuts the result to the display. The point is the display's center rounded half away from zero, as Crosshair-Overlay's `GetOverlayCenter` rounds, plus the offset floored, as its `DrawOverlay` floors `flOffset`. A window with no area hides, which is the card's **Off its display**.

`ShowLook` (`PixelOverlay.cs` line 189) takes a look. When the look is the one it already has, it calls `CrosshairView.Reload`, so a picture is read again at every show. `WM_DISPLAYCHANGE` and a DPI change call `PlaceAgain`, which places the window again and raises `ShownOrHiddenByDisplays` when the change hid or showed it. `SyncCrosshairs` subscribes to that, so the card's status follows a display change. `OnClosed` (`PixelOverlay.cs` line 172) sets a flag that `PlaceAgain` checks, so a display change queued before the window closed does nothing after it.

`DisplayBounds.Of` (`DisplayBounds.cs` line 72) reads the displays with `EnumDisplayMonitors` and `GetMonitorInfo` on each call. WinForms' `Screen` keeps its list until its own notice of a change arrives, which can come after `WM_DISPLAYCHANGE`. A name that is not connected gives the primary display.

---

## Drawing a crosshair

`CrosshairShape.Of` (`CrosshairShape.cs` line 46) builds the shape around (0, 0):

- **Cross**: four arms, each a thickness wide and a length long, beginning half the thickness plus the gap from the center, as the CS:GO generator's `updateCrosshair` draws them. T Shape drops the top arm. The center dot is a thickness square.
- **Circle**: Crosshair-Overlay's polygon (`Drawing.cpp`, `STYLE_POLYGON`), its sides on the radius with the first vertex straight above the center.
- **Dot**: a filled dot.
- **Image**: a rectangle of the picture's drawn size, centered.

The outline is the shape drawn with a pen twice the outline thickness wide, under the fill, so the fill covers the pen's inner half. This matches Crosshair-Overlay drawing its larger outline quads before the crosshair. The rotation turns everything about the center.

`CrosshairView` (`CrosshairView.cs` line 26) draws in the display's own pixels: it undoes the display's scale, moves to `Origin`, and pushes one opacity for the whole crosshair, as the CS:GO generator sets one opacity on the crosshair's group. Smooth Edges off sets `EdgeMode.Aliased` and `BitmapScalingMode.NearestNeighbor`. The card's preview sets `Fit`, which centers the crosshair and shrinks it by `FitScale` (`CrosshairView.cs` line 159) when it is larger than the box, never enlarging it.

`CrosshairPictures.Load` (`CrosshairPictures.cs` line 32) reads the whole file into memory first, so it never holds the file open, and decodes it with WPF's `BitmapDecoder`: PNG, GIF, BMP, ICO, TIFF, JPEG, and WebP through Windows' codec. A file with several frames gives its largest. The picture is frozen and cached by path and write time. The cache keeps ten pictures and drops the one read longest ago.

---

## Syncing the windows

`SyncCrosshairs` (`InputService.Crosshairs.cs` line 70) closes the windows of crosshairs that were removed, hides the windows of crosshairs that are off, makes a window for a crosshair that is on and has none, and hands each its look. It sets `IsRunning` from the window's visibility, and the problem from why it is hidden: `NoPicture` for a picture that cannot be read, `OffDisplay` otherwise. Running it again changes nothing. When the magnifier is up, it gives the lens the new set of windows to leave out and, for a magnifier that follows a crosshair, schedules a magnifier sync.

`TickCrosshairs` (`InputService.Crosshairs.cs` line 146) runs on every UI tick while the engine runs, ungated by focus, since a game holds the focus. It takes the macros' requests and the Magnifier (While Held) macro's hold. Once a second it calls `MagnifierService.Tend` and then each crosshair's `KeepOnTop`, in that order, so the crosshairs end up above the lens and the spotlight. `KeepOnTop` is the Screen Overlay's check: back on top when another program's visible window is above it.

`OpenCrosshairs` (`InputService.Crosshairs.cs` line 205) runs when the engine starts. `CloseCrosshairs` (`InputService.Crosshairs.cs` line 187) runs when it stops: the windows close rather than hide, which prevents a hang at shutdown, and the magnifier closes.

---

## Macros

| Action | Ordinal | Kind |
|---|---|---|
| `ToggleCrosshair` | 68 | One-shot. `MacroAction.CrosshairNumber` 0 is every crosshair, 1 to 10 one. |
| `ToggleMagnifier` | 69 | One-shot. |
| `MagnifierWhileHeld` | 70 | Continuous. |

The macros run on the polling thread, and the windows belong to the UI thread. `RequestCrosshairToggle` sets a bit per crosshair's number in `InputManager.ToggleCrosshairMask`, bit 0 for every crosshair, and `ToggleCrosshairs` (`InputService.Crosshairs.cs` line 170) takes and clears it: with bit 0, any crosshair on turns them all off and none on turns them all on, the rule the Screen Overlays follow. `ToggleMagnifier` sets `ToggleMagnifierRequested`, which flips the magnifier's switch. `MagnifierWhileHeld` calls `NoteMagnifierHeld` once a frame while held, which pushes `_magnifierHeldUntil` 100 ms ahead (`MagnifierHoldMs`, Voice Listen While Held's beat). `MagnifierHeld` is true until that time passes, so a release needs no call of its own.

The reWASD import maps its commands 101 to 110 to `ToggleCrosshair` with that number less 100, and 120 to `ToggleCrosshair` with 0, each reported Partial with `Import_Tr_Crosshair` (`RewasdTranslator.cs`).

---

## The magnifier

`MagnifierService` (`MagnifierService.cs` line 32) runs on the UI thread. `SyncMagnifier` (`InputService.Crosshairs.cs` line 120) calls `Show` while the switch is on or a Magnifier (While Held) macro is held, and `Hide` otherwise, then raises each crosshair window that is up. `Show` (`MagnifierService.cs` line 114) calls `MagInitialize` once, and a change of mode hides the old mode's windows before the new one starts.

`Aim` (`MagnifierService.cs` line 96) picks the display and the point: the first crosshair that is on (its display's center plus its offset), or the chosen display's center. Following the pointer, `Follow` (`MagnifierService.cs` line 370) reads `GetCursorPos` and `DisplayBounds.At` each frame instead. The frame is WPF's `CompositionTarget.Rendering`, hooked by `Frames` only while a lens or a mode that follows the pointer shows.

### Lens

`MagnifierNative.CreateLens` (`MagnifierNative.cs` line 226) does what Microsoft's windowed sample's `SetupMagnifier` does. A host window of the class `PadForgeMagnifierHost`, `WS_EX_TOPMOST | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW`, holds a `WC_MAGNIFIER` child with `MS_SHOWMAGNIFIEDCURSOR`, zoomed by `MagSetWindowTransform` with the zoom on the matrix's diagonal. The host answers `WM_NCHITTEST` with `HTTRANSPARENT`. A round lens is cut by `CreateEllipticRgn`, so the corners of its square show nothing.

Each frame `ShowSource` (`MagnifierNative.cs` line 273) sets the area to magnify with `MagSetWindowSource` and invalidates the control, as the sample's `UpdateMagWindow` does on its 16 ms timer. `MagnifierMath.Source` (`CrosshairPlace.cs` line 59) makes that area the lens's size divided by the zoom, centered on the point and kept on the display. `MagnifierMath.Lens` (`CrosshairPlace.cs` line 46) keeps the lens itself on the display.

The border is a `PixelOverlay` holding a `LensFrameView`, around the lens and one pixel into it, so its smoothed inner edge covers the region's stepped curve. `RefreshLeftOut` (`MagnifierService.cs` line 212) passes the crosshair windows and the border to `MagSetWindowFilterList` in exclude mode, so the lens leaves them out of what it magnifies.

### Full Screen

`Follow` calls `MagnifierNative.SetFullScreen` (`MagnifierNative.cs` line 118), which is `MagSetFullscreenTransform`, as the full-screen sample's `SetZoom` calls it. `MagnifierMath.FullScreenOffset` (`CrosshairPlace.cs` line 86) gives the offsets that bring the point to the display's center, kept so the view shows only that display. The call repeats only when the offsets or the zoom change. A refusal ends in `Fail`, which hides everything and sets `Failure` to `Extras_Magnifier_Failed`. `Hide` sets the zoom back to 1 at 0, 0.

Windows' full-screen magnifier has no filter list, so it zooms the crosshair windows too. One process at a time holds it: while another does, `MagSetFullscreenTransform` returns false and the other's zoom stays. Windows ends a process's zoom when the process exits. The test host sets `MagnifierNative.OffLimitsForTest`, and `SetFullScreen` then calls the test's `FullScreenSeam` instead of Windows, since a real call changes the whole desktop.

### Spotlight

`ArrangeSpotlight` (`MagnifierService.cs` line 307) makes the shade: a black window of the host class over the display, with `SetLayeredWindowAttributes` alpha `SpotlightHoleView.ShadeAlpha(dim)`, which is the dim times 255. `FollowSpotlight` (`MagnifierService.cs` line 327) cuts a square of the circle's size out of the shade with `SetWindowRgn` and places a `PixelOverlay` in the square. Its `SpotlightHoleView` fills the square with the same shade except for a circle with a smoothed edge. The two windows meet on whole pixels, so the circle's edge is the only curve drawn. Where the square meets the display's edge it is cut to the display. At a dim of 0.6 the display outside the circle keeps 40% of its brightness.

### Staying on top and closing

`Tend` (`MagnifierService.cs` line 193) runs once a second while the magnifier is up. It aims again, follows when the display or the point moved, and puts each of its windows back above another program's window. `Close` (`MagnifierService.cs` line 181) hides the magnifier and calls `MagUninitialize`, as both samples end. It runs when the engine stops and when PadForge closes.

---

## Limits

- A game in exclusive full screen owns the display, and the crosshairs, the lens and the spotlight do not show over it.
- The lens and the spotlight follow one display. The lens's area to magnify is kept on that display.
- No test drives Windows' full-screen zoom: the fence keeps the test host's calls away from it.

---

*Last updated for PadForge 6.0.0.*
