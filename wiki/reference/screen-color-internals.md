# Screen Color Internals

*How the Screen Color lighting mode reads a display, shrinks it on the GPU, turns an area into a color or a small picture, and hands the result to the lighting paths.*

For the user-facing side see [Screen Color](../features/screen-color.md).

| File | Responsibility |
| --- | --- |
| `PadForge.App/Common/Input/ScreenColor/ScreenColorSource.cs` | The entry point the lighting threads call: one worker per display, results shared by settings, smoothing, the spread picture, test seams. |
| `ScreenCaptureWorker.cs` | `ScreenCaptureWorker`, the thread that reads one display, its states, waits and retirement. `IScreenGrabber`, `ScreenGrabResult`, `ScreenCaptureState`. |
| `ScreenDxgi.cs` | `ScreenDxgi`, the DXGI and Direct3D 11 calls as raw COM slots. `ScreenDownscaler`, the GPU mip-chain reduction. `DesktopDuplicationGrabber`. The `ScreenGrabberWaiting` and `ScreenGrabberUnavailable` exceptions. |
| `WindowsCaptureGrabber.cs` | `WindowsCaptureGrabber`, the Windows.Graphics.Capture path. `ScreenModeWatch`, its once-a-second check for display and HDR changes. |
| `ScreenColorMath.cs` | `ScreenFrame`, `ScreenRect` and `ScreenColorMath`: areas, Average, Most Common, saturation, brightness, smoothing, rotation and the scRGB conversion. Stateless. |
| `PadForge.App/Common/Input/Peripherals/ScreenPicture.cs` | `ScreenPicture`, the spread picture a key frame carries, and `LightPlacement`, where each light of a device sits. |

The settings live on `DeviceSlotConfig` (the `ScreenColor*` properties) and `DeviceSlotConfigData`, and the Lighting tab's panel is in `PadPage.xaml` and `PadPage.xaml.cs`.

---

## Data flow

1. A lighting thread asks `ScreenColorSource.ColorFor(cfg)` for one color, or `PictureFor(cfg)` for the spread picture, at up to 30 calls a second.
2. `WorkerFor(display)` finds or starts the display's `ScreenCaptureWorker` and calls `Touch()` on it. A read is what keeps a capture running.
3. The worker's thread builds a grabber, takes frames, and publishes each `ScreenFrame` with `Volatile.Write`. A frame is made whole and never changed, so the lighting threads read it by reference.
4. The source computes the color or picture for the device's settings from the newest frame, smooths it toward the target, and returns it.

Results are keyed by `ResultKey(Display, Area, Method, Saturation, Brightness, Smoothing)`. Devices with the same settings share one result, so a slot's devices cost one calculation between them. A result no device has asked for in `ForgetMs` (10,000 ms) is dropped the next time a new key is added. The source holds one lock, `s_gate`, only for arithmetic on a picture of a few thousand cells at the most.

`StateOf(display)` reports a worker's state for the Lighting tab without starting or touching one.

---

## The worker

`ScreenCaptureWorker.Start` runs `Run` on a background thread named `PadForge Screen Color`, at `ThreadPriority.BelowNormal`, in the MTA. Each `Step` returns the milliseconds to wait before the next, or -1 once the worker has retired.

| Constant | Value | Meaning |
| --- | --- | --- |
| `IdleStopMs` | 2000 | A worker nothing has read for this long asks the source to retire it. |
| `FrameMs` | 33 | About 30 pictures a second at the most, the top of Aurora's range (`AmbilightLayerHandler.GetIntervalFromFps`). |
| `WorkShare` | 4 | Reading back gets at most a quarter of the time. |
| `GrabTimeoutMs` | 100 | How long one `Grab` waits for a new frame. |
| `RetryMinMs` | 250 | The first wait after a failed build or an ended capture. |
| `RetryMaxMs` | 8000 | The longest wait while neither grabber runs on the PC. |
| `WaitRetryMaxMs` | 1000 | The longest wait while Windows holds the desktop or the capture restarts, Prismatik's `ACCESSDENIED_DESKTOP_RETRY_INTERVAL` (Lightpack `DDuplGrabber.cpp`). |
| `ReturnCheckMs` | 1000 | How often a capture that fell back to the primary display looks for the display it was asked for. |
| `EndsBeforeUnavailable` | 3 | Ends in a row with no picture before the state turns Unavailable. |

After a frame, the wait is `Math.Max(FrameMs - work, work * (WorkShare - 1))`, where `work` is the grabber's `LastWorkMs`. A frame that took 5 ms waits 28 ms. One that took 20 ms waits 60 ms. `NoChange` asks again at once, since `Grab` itself waited.

Retirement is two-sided. `Step` sees `IsIdle` and calls the source's `Retire`, which checks `IsIdle` again under `s_gate` and removes the worker from `s_workers` only if it is still the registered one. A read that arrived at the last moment keeps the worker alive. A stopped engine, a changed profile and a macro that switched a device off the mode all end a worker this way, with no hook of their own.

### States

`ScreenCaptureState` has five values:

| State | Set when | Lighting tab |
| --- | --- | --- |
| `Stopped` | No worker for the display, or it retired | Nothing |
| `Capturing` | A grabber was built, or a frame arrived | Nothing |
| `Waiting` | The build threw `ScreenGrabberWaiting` | `Pad_Lighting_ScreenWaiting` |
| `Restarting` | A capture ended (`Lost` or a throwing `Grab`) for the first or second time in a row | Nothing |
| `Unavailable` | The build threw anything else, or a capture ended the third time in a row | `Pad_Lighting_ScreenUnavailable` |

`NextRetry` doubles the wait from 250 ms each time, up to 1000 ms for `Waiting` and `Restarting` and 8000 ms for `Unavailable`. A frame puts the wait back to 250 ms and the count of ends to zero. A build alone does neither, so a capture that builds and ends again keeps its growing wait. The worker logs a `SCREEN` line to the diagnostic log only when the reason changes.

Neither grabber can tell a held desktop from a mode change when a capture ends: Desktop Duplication answers `DXGI_ERROR_ACCESS_LOST` to both. Only the rebuild's `DuplicateOutput` answers `E_ACCESSDENIED` for the secure desktop. So an end shows nothing, and the rebuild's answer sets the state. Prismatik treats `ACCESS_LOST` the same way, as a frame not ready and a reallocation (`DDuplGrabber.cpp`, `GrabManager.cpp`).

### Returning to the picked display

`ScreenDxgi.FindOutput` gives the primary display when the asked-for one is not attached, and nothing ends that capture when the display comes back. So once every `ReturnCheckMs`, while the grabber's `Output` differs from the asked-for name, the worker asks the source's `CanReadAgain`. It first asks `ScreenDxgi.IsAttached`, which reads `EnumDisplayDevicesW` and costs no DXGI factory, then `ScreenDxgi.Resolves`, which runs DXGI's own walk on a new factory. A display Windows lists but DXGI does not enumerate, such as an indirect or virtual display, would otherwise rebuild the capture onto the primary every second. When both say yes, the worker drops the grabber and builds again. Prismatik compares its screens before every grab the same way (`GrabberBase.cpp`, `isReallocationNeeded`).

---

## Choosing a grabber

`ScreenColorSource.FirstThatRuns` tries `DesktopDuplicationGrabber` first and `WindowsCaptureGrabber` only when the first throws `ScreenGrabberUnavailable`. A `ScreenGrabberWaiting` from the first reaches the worker unchanged: a desktop Windows holds for now is no reason to change ways.

`DesktopDuplicationGrabber` sorts `DuplicateOutput` failures the way Prismatik's `DDuplGrabber::_reallocate` does:

| HRESULT | Value | Becomes |
| --- | --- | --- |
| `DXGI_ERROR_UNSUPPORTED` | `0x887A0004` | Unavailable: the PC cannot duplicate this output, as on many laptops with two GPUs |
| `DXGI_ERROR_NOT_CURRENTLY_AVAILABLE` | `0x887A0022` | Unavailable: the most programs that may duplicate an output already do |
| `E_NOTIMPL` | `0x80004001` | Unavailable |
| Anything else, `E_ACCESSDENIED` among them | | Waiting |

A failed `CreateDXGIFactory1`, `D3D11CreateDevice` or an empty desktop also throws `ScreenGrabberUnavailable`.

---

## ScreenDxgi

The DXGI and Direct3D 11 calls go through function pointers to raw vtable slots, numbered by each method's place in the C vtable struct of the Windows SDK 10.0.26100 headers (`d3d11.h`, `dxgi.h`, `dxgi1_2.h`, `dxgi1_5.h`, `dxgi1_6.h`).

- `FindOutput(display, ...)` walks every adapter (`EnumAdapters`, slot 12) and every output (`EnumOutputs`, slot 7), reading `DXGI_OUTPUT_DESC` (`GetDesc`, slot 7): the GDI name at byte 0, `AttachedToDesktop` at 80, `Rotation` at 84, the `HMONITOR` at 88. An attached output whose name matches wins. Otherwise the primary, the attached output at the desktop's origin, is used. A device must come from the adapter its output is connected to (Microsoft, `IDXGIOutput5::DuplicateOutput1`), which is why it walks every adapter, as Prismatik's `DDuplGrabber` does. An overload hands the factory to the caller.
- `IsCurrent(factory)` is `IDXGIFactory1::IsCurrent` (slot 13), false once the adapters or outputs the factory saw have changed. Sunshine asks it on every frame because "This will return false if the HDR state changes" (`src/platform/windows/display_base.cpp:337-341`).
- `CreateDevice(adapter, ...)` is `D3D11CreateDevice` with `D3D_DRIVER_TYPE_UNKNOWN`, no flags and the runtime's feature levels.
- `IsHdr(output)` reads `DXGI_OUTPUT_DESC1` through `IDXGIOutput6::GetDesc1` (slot 27) and compares the color space at byte 100 with `DXGI_COLOR_SPACE_RGB_FULL_G2084_NONE_P2020` (12).
- `SdrWhiteNits(display)` walks the active paths of `QueryDisplayConfig`, matches the source's GDI name (`DISPLAYCONFIG_DEVICE_INFO_GET_SOURCE_NAME`, type 1), and reads `DISPLAYCONFIG_SDR_WHITE_LEVEL` (type 11). The level is in thousandths of 80 nits, so nits are `level * 80 / 1000`. Any failure returns 200 nits.
- `IsAttached(display)` reads `DISPLAY_DEVICEW.StateFlags` at byte 324 for `DISPLAY_DEVICE_ATTACHED_TO_DESKTOP`.

---

## The GPU reduction

`ScreenDownscaler` turns a desktop texture into a few dozen cells on the GPU, the mip chain ScreenCapture.NET builds (`DX11ScreenCapture.PerformCaptureZoneUpdate`), so no full frame reaches the CPU.

For a texture of width `W`, the mip level is the smallest `m` with `W >> m <= MaxCols` (64), and the picture is `max(1, W >> m)` by `max(1, H >> m)`:

| Desktop | Mip level | Picture |
| --- | --- | --- |
| 1920 by 1080 | 5 | 60 by 33 |
| 2560 by 1440 | 6 | 40 by 22 |
| 2560 by 1600 | 6 | 40 by 25 |
| 3840 by 2160 | 6 | 60 by 33 |

`Build` makes two textures in the frame's own format: a scaling texture with `mip + 1` levels, bound as render target and shader resource with `D3D11_RESOURCE_MISC_GENERATE_MIPS`, with a shader resource view on it, and a staging texture of the picture's size with CPU read access. `Read` copies the frame into level 0 (`CopySubresourceRegion`, context slot 46), calls `GenerateMips` (slot 54), copies the chosen level into the staging texture, and maps it with `Map` (slot 14, `D3D11_MAP_READ`), then `Unmap` (slot 15). The textures are rebuilt only when the frame's width, height or format changes. A step the device refuses returns null, which the grabber reports as `Lost`.

A `DXGI_FORMAT_B8G8R8A8_UNORM` frame (87) is read byte by byte. A `DXGI_FORMAT_R16G16B16A16_FLOAT` frame (10) is read as half floats through `ScreenColorMath.ScRgbToRgb`. The cells then pass through `ScreenColorMath.Oriented` with the output's rotation.

---

## Desktop Duplication

`DesktopDuplicationGrabber` builds a device on the output's adapter. On an HDR output it reads the SDR white level once, at the build, and asks `IDXGIOutput5::DuplicateOutput1` (slot 26) for `R16G16B16A16_FLOAT` and then `B8G8R8A8_UNORM`. On an SDR output it asks for `B8G8R8A8_UNORM` alone. A process that is not per-monitor DPI aware gets `DXGI_ERROR_UNSUPPORTED` from `DuplicateOutput1`, so the older `IDXGIOutput1::DuplicateOutput` (slot 22) follows it. The rotation comes from `DXGI_OUTDUPL_DESC` at byte 28 (`GetDesc`, slot 7).

`Grab` calls `AcquireNextFrame` (slot 8) with the 100 ms timeout:

- `DXGI_ERROR_WAIT_TIMEOUT` (`0x887A0027`) is `NoChange`.
- Any other failure, `ACCESS_LOST` from a mode change, an HDR switch or the secure desktop among them, is `Lost`.
- A frame whose `LastPresentTime` is 0 only moved the pointer, ScreenCapture.NET's test (`DX11ScreenCapture.CaptureScreen`), and is `NoChange`.

`ReleaseFrame` (slot 14) runs after every acquired frame. A Desktop Duplication frame carries no pointer.

---

## Windows.Graphics.Capture

`WindowsCaptureGrabber` is for a PC where Desktop Duplication cannot run. A laptop with two GPUs is the usual case: alienfx-tools documents it (`Doc/alienfx-gui.md`), and Sunshine keeps this path for it (`src/platform/windows/display_wgc.cpp`).

The build needs Windows 10 build 18362 (version 1903) and `GraphicsCaptureSession.IsSupported()`. It finds the output and keeps the factory, makes a Direct3D 11 device on the output's adapter, wraps it with `CreateDirect3D11DeviceFromDXGIDevice`, and makes the capture item with `IGraphicsCaptureItemInterop::CreateForMonitor` (slot 4) on the output's `HMONITOR`. A refused `CreateForMonitor` throws `ScreenGrabberWaiting`. Any other failure throws `ScreenGrabberUnavailable`.

`PoolFormat(hdr, ...)` picks the pool's format: `R16G16B16A16Float` with the display's SDR white level on an HDR display, since 8-bit color there comes out clipped (Microsoft, Screen capture), as Sunshine does for scRGB (`src/platform/windows/frame_contract.cpp`, `select_wgc_capture_format`). On SDR it is `B8G8R8A8UIntNormalized`. The pool is `Direct3D11CaptureFramePool.CreateFreeThreaded` with 2 buffers at the item's size.

`TurnOffBorderAndPointer` sets `IsCursorCaptureEnabled` to false on build 19041 and later. On build 20348 and later it asks `GraphicsCaptureAccess.RequestAccessAsync(Borderless)` and sets `IsBorderRequired` to false. A refusal is logged and the capture runs with the border.

`Grab`:

- The item's `Closed` event, or `ScreenModeWatch.Changed()`, returns `Lost`.
- `Newest(_pool.TryGetNextFrame)` takes every queued frame and keeps the newest, disposing the rest. The pool queues its frames, so one call alone hands over the oldest, a grab period behind. Sunshine keeps only the newest the same way (`display_wgc.cpp`, `on_frame_arrived`).
- No frame sleeps `Math.Min(timeoutMs, 16)` and returns `NoChange`.
- A frame whose `ContentSize` differs from the pool's size returns `Lost`.
- The surface's texture comes from `IDirect3DDxgiInterfaceAccess::GetInterface` (slot 3) and goes through the same `ScreenDownscaler` with identity rotation (`DXGI_MODE_ROTATION_IDENTITY`, 1). This API hands over a rotated display already turned, as Sunshine's `display_wgc.cpp` notes.

### ScreenModeWatch

Windows.Graphics.Capture sends no word of a mode change, so an HDR switch would leave an 8-bit pool clipping or a float pool on its old format. `ScreenModeWatch.Changed()` runs at most once every `ReturnCheckMs` (1000 ms). It returns true, which rebuilds the capture, when `IsCurrent` on the kept factory is false or the output's HDR state differs from the one the pool was built for. On an HDR display it rereads the SDR white level and keeps it, since the pool's format still fits. Sunshine asks `IsCurrent` on every frame (`display_base.cpp:337-341`) and rereads the white level once a second (`display_base.cpp:955-964`, `display.h:324`).

---

## HDR and SDR white

`ScreenColorMath.ScRgbToRgb(r, g, b, sdrWhiteNits)` scales linear scRGB by `80 / max(sdrWhiteNits, 1)`, since scRGB's 1.0 is 80 nits, and encodes each channel with the sRGB curve (`12.92 * x` up to 0.0031308, then `1.055 * x^(1/2.4) - 0.055`). The display's SDR white maps to full white, which is what the desktop's ordinary colors are drawn against. A value at or above 1.0 after scaling clips to 255. A negative value, which scRGB uses for colors outside sRGB's gamut, and NaN clip to 0.

Desktop Duplication reads the white level when its grabber is built. An HDR switch ends that capture with `ACCESS_LOST`, and the rebuild reads it again. Windows.Graphics.Capture rereads it every second through `ScreenModeWatch`. An 8-bit frame goes unconverted, and its grabbers pass 80 nits, which goes unused.

---

## ScreenColorMath

`RectOf(area, left, top, width, height)` gives the part of the display each `ScreenColorArea` covers. Top Left to Bottom Right and Center are a third on each side. Custom clamps left and top to 0 to 99 percent, and the right and bottom edges to at least one percent past them and at most 100, so a custom area never leaves the display and never comes to nothing. `CellRange` turns a rectangle into the cells it touches, at least one, with a slack of 0.0001 so an edge on a cell boundary does not take the next cell.

`Average` is the rounded mean of the cells.

`MostCommon` follows alienfx-tools' Prevailing calculation beside its Medium one (`alienfx-gui/CaptureHelper.cpp`), which takes the majority of exact colors. A small averaged picture rarely repeats an exact color, so this one votes by hue:

- 12 hue buckets of 30 degrees, offset so each primary sits in the middle of one. A red does not split in two across the wrap at 0.
- A cell with saturation under 0.2 or value under 0.1 (`NeutralSaturation`, `NeutralValue`) goes in a 13th, neutral bucket with weight 0.05 (`NeutralWeight`).
- Any other cell weighs `saturation * value`.
- The result is the weighted mean of the heaviest bucket's cells, or black when every weight is 0.

`Saturate(rgb, percent)` moves a color from or toward its gray with RazerAmbilight's `ApplySaturation` weights (`Ambilight/Util/ImageManipulation.cs`): 0.3086, 0.6094 and 0.0820. `Dim(rgb, percent)` scales each channel.

`SmoothingStep(elapsedMs, percent)` is `1 - exp(-elapsedMs / (percent * SmoothingMsPerPercent))` with `SmoothingMsPerPercent` = 1. It is a time constant and not a share per frame, so a fade takes as long at any update rate. It does the job of OpenRGB's Smoothness (OpenRGBEffectsPlugin `Effects/Ambient/Ambient.cpp`). A setting of 0 returns 1, and no elapsed time returns 0.

`Oriented(cols, rows, cells, rotation)` turns a surface into the display's orientation for `DXGI_MODE_ROTATION` 2 (90 degrees), 3 (180) and 4 (270), the way ScreenCapture.NET's `CopyRotate90`, `CopyRotate180` and `CopyRotate270` do. A rotated display's duplicated surface stays unrotated (Microsoft, Desktop Duplication API, Rotating the desktop image).

`ColorFor` applies Most Common or Average, then `Saturate`, then `Dim`, then the smoothing. The first frame a result sees sets its color at once, so a light does not fade up from black. Before that frame the color is black. While a capture waits or restarts, the newest frame stays, so the light keeps its last color.

---

## The spread picture

`PictureFor` cuts the area into at most `PictureMaxCols` by `PictureMaxRows` (32 by 16) cells. `Crop` splits the area's cell range into that many parts with integer bounds, so every cell of the area lands in exactly one part and no edge goes missing, and each part gets the device's method, saturation and brightness. Each cell then smooths on its own. The source returns the same `ScreenPicture` instance while no cell changes (`SameCells`), so a device with nothing new to show gets no write.

`ScreenPicture` is immutable and compares by content, with its hash computed once. `At(across, down)` finds the cell under a place from 0 to 1.

`LightPlacement.Of(map)` gives each light of a device a place, worked out once per `LightMap`:

1. Lights with reported positions (`LightInfo.HasPosition`, such as a LampArray's) are placed by the center of each light within the bounding box of all of them.
2. A keyboard with no positions uses the QMK layout that holds the most of its key usages (`BestLayout`), the smaller of two that hold as many: full-size ANSI, ISO and extended, TKL, 75%, 65%, 65% with blocker, 60%, HHKB, HHKB JIS and the Keychron Q6. A usage the layout draws twice puts its lights on the first.
3. Zones and edge lights still without a place are spread from left to right at mid height.

A light with no place has NaN coordinates and takes the device's one color.

---

## Where the colors go

The one color comes from `Ds5EffectSynthesizer.ComputeLightbarColor`, whose `LightbarMode.ScreenColor` case calls `ScreenColorSource.ColorFor`. Every lit device shares that core through `Ds4EffectSynthesizer.ResolveLightbarRgb`: the DualSense and DualSense Edge, the DualShock 4, the PS Move sphere, the Web Controller's drawn lightbar, and mice, keyboards and lighting rows through `PeripheralLightingColor.Resolve`.

The picture goes to peripherals only. In `UserEffectsDispatcher`, when a device's mode is Screen Color, `ScreenColorSpread` is on and the base mode shows (no fresh game color, no macro override, no Input Reactive pulse), `PictureFor` is attached to the device's key frame with `KeyFrame.WithPicture`. `LightRenderer.Render` then gives each light its own color first, then its key's or group's, then the picture's cell at its place, then the fill. A background a frame sets covers the picture. A game's lightbar, a game mod's color, a macro color and the Input Reactive pulse cover the spread because it is the base mode's color light by light.

`UserEffectsDispatcher.ColorKeepsChanging(mode, baseModeShows)` is true for Screen Color while the base mode shows, and `PeripheralOutputs.SetLighting` carries it in the claim as `KeepsChanging`. A HID lighting model that stores each picture (`HoldMs` above 0) is sent nothing while it is true, in `HidLightingBackend.Paint`, and keeps showing its last picture. `SteelSeriesDirectBackend` treats its two headsets that store pictures the same way. A keyboard that also has a LampArray interface takes the changing colors through `LampArrayBackend`, which sends no lamp twice inside the device's minimum update interval (HID Usage Tables 1.6, section 26.3). See [Peripheral Outputs Internals](peripheral-outputs-internals.md).

`UserEffectsDispatcher.IsAnimated` counts Screen Color among the modes that keep the effects timer running.

---

## The Lighting tab

The panel shows under the **Mode** box when it is set to Screen Color. Its rows bind to `DeviceSlotConfig`. The Display box has no binding: `PadPage.ShowScreenDisplays` fills it from `ScreenDisplayChoice.ListFor(saved)`, the primary first, then each `System.Windows.Forms.Screen` by its number, then the saved display when it is not connected. A list swapped under a two-way binding clears the selection and writes that back into the setting, so the box follows the MIDI port box's pattern instead. `ScreenDisplayChoice.ToString` returns the line's words, so a screen reader reads them.

`SyncScreenColorStatus` runs on a one-second `DispatcherTimer` while the tab shows the mode. It refreshes the Display box and shows the Waiting or Unavailable line from `ScreenColorSource.StateOf`. The spread checkbox shows only while the Key Colors card does (`KeyColors.IsVisible`), on a device with more than one light. The tab's preview draws a gradient from `#58B6E4` to `#E48A58` and reads nothing, so it never keeps a capture running.

---

## Settings

| Property | Default | Range |
| --- | --- | --- |
| `LightbarMode` | | `ScreenColor` = 17, appended after `PlayerNumber` |
| `ScreenColorDisplay` | empty (the primary) | A GDI name such as `\\.\DISPLAY2` |
| `ScreenColorArea` | `WholeScreen` | `ScreenColorArea`, 0 to 10 |
| `ScreenColorLeft`, `ScreenColorTop` | 25 | 0 to 99 |
| `ScreenColorWidth`, `ScreenColorHeight` | 50 | 1 to 100 |
| `ScreenColorMethod` | `MostCommon` | `MostCommon` = 0, `Average` = 1 |
| `ScreenColorSaturation` | 100 | 0 to 200 |
| `ScreenColorBrightness` | 100 | 0 to 100 |
| `ScreenColorSmoothing` | 30 | 0 to 100 |
| `ScreenColorSpread` | true | |

The setters clamp to the ranges, and each has a reset command. `DeviceSlotConfigData` saves them as XML attributes of the same names with the same defaults, so a file from before the mode reads as the defaults.

---

## Tests

`PadForge.Tests/ScreenColorTests.cs` holds the behavior:

| Class | Covers |
| --- | --- |
| `ScreenColorMathTests` | The areas, the custom clamp, `CellRange`, Average, Most Common on dark, gray and red-wrap scenes, saturation, brightness, the smoothing time constant, rotation, the scRGB conversion, `ColorKeepsChanging` |
| `ScreenCaptureWorkerTests` | Start and retire, the pace, `NoChange`, a lost capture and its rebuild, the state a rebuild answers, Unavailable at the third end, the waits and their limits, the return to the picked display |
| `ScreenGrabberOrderTests` | The first grabber when it runs, the second when it cannot, a wait that changes nothing, the newest pool frame, the float pool on HDR, the HDR-switch rebuild, `ScreenModeWatch` |
| `ScreenColorSourceTests` | One capture per display, shared results, the return check, the spread method, black before the first picture, smoothing over time, the order of steps, each area, the last color through a rebuild, `StateOf`, retirement, the picture's size, coverage, identity and smoothing, the test host reading nothing |
| `LightPlacementTests` | Reported positions, layouts, zones and edges, the best layout |
| `ScreenPictureRenderTests` | The picture under each light, key and group colors over it, a background over it, frame equality |
| `ScreenColorSpreadClaimTests` | The claim's picture and `KeepsChanging`, spread off, other modes, a game or macro color over the picture, unchanged pictures waking nothing |
| `ScreenColorSettingsTests` | The mode number, the defaults, the settings round trip, an older file, the resets, the ranges |
| `ScreenColorMacroTests` | The mode in a macro cycle |
| `ScreenDisplayListTests` | The Display box's list, a gone display, the words a screen reader hears, a language change, selection |

The tests drive the worker through `ScriptedGrabber` and the source's seams (`GrabberSeam`, `ListedSeam`, `ResolvesSeam`, `ClockSeam`, `StartSeam`). `TestHostFences` sets `ScreenColorSource.OffLimitsForTest` for the whole test process, so a test without a seam starts no capture of the real screen.

---

## Related pages

- [Screen Color](../features/screen-color.md)
- [Peripheral Outputs Internals](peripheral-outputs-internals.md): the backends that take the colors and pictures.
- [Input Pipeline](input-pipeline.md)

---

*Last updated for PadForge 5.3.0.*
