# Keyboard Screens Internals

*How PadForge draws on the keyboard screens, which engine draws while Logitech Gaming Software runs, and how the keys beside the screens reach a device row.*

For the user-facing side see [Keyboard Screens](../features/keyboard-screens.md).

| File | Responsibility |
| --- | --- |
| `PadForge.App/Services/KeyboardScreenService.cs` | The modes, the macros' shows, stopwatch and pan, and the status lines. Composes each kind's picture on the UI thread. |
| `PadForge.App/Common/Input/KeyboardScreens/KeyboardScreenHost.cs` | The worker thread that runs every engine and reports what draws each kind. |
| `KeyboardScreenFormats.cs` | Screen sizes, wire formats, the key layout and the USB identities. |
| `KeyboardScreenRenderer.cs` | Text, pictures and a lightbar color drawn as pixels at a screen's size. |
| `LgsLcdScreens.cs` | The Logitech screens through LGS's LCD library. |
| `G15HidScreens.cs` | The monochrome screens over HID, without LGS. |
| `G19UsbScreen.cs` | The G19 over WinUSB, without LGS. |
| `ArxScreen.cs` | The Arx Control applet. |
| `Strike7Screen.cs` | The S.T.R.I.K.E. 7 applet. |
| `KeyboardScreenKeys.cs` | The keys every engine reads, merged, with the press pulse. |
| `LightbarColors.cs` | The last lightbar color each DualShock 4 and DualSense took. |
| `PadForge.Engine/Common/Logitech/LogitechServerCatalog.cs` | Finds LGS's libraries by their class registrations. |
| `PadForge.Engine/Common/Logitech/LogitechLcdLibrary.cs`, `LogitechArxLibrary.cs` | The LCD and Arx exports. |
| `PadForge.Engine/Common/MadCatz/Strike7Library.cs` | The `Strike7API.dll` exports and callbacks. |

The device row is `PadForge.App/Common/Input/KeyboardScreenKeysDevice.cs`. `KeyboardScreensRuntime.cs` mirrors the Settings switch to the engine.

---

## Kinds and threads

A kind is a class of screen: Monochrome (160 by 43), Color (320 by 240), Arx (480 by 320, scaled by the phone) and Strike7 (480 by 320). Every screen of a kind shows that kind's picture.

The service ticks on the UI thread, where WPF draws: four times a second, on every UI tick (33 ms) while a show plays, and at once after a change. It runs whether or not PadForge has focus, the Dreamcast screens' rule, so a clock keeps time behind a game. Each tick hands the host one picture per kind with `Publish`, as top-down B, G, R, A pixels at the screen's size, or null when PadForge shows nothing there. A picture equal to the last one changes nothing.

The host keeps the latest picture per kind and runs every engine on one worker thread, `PadForge.KeyboardScreens`, every 20 ms and at once when a picture arrives. Each engine's pass has its own exception handler, so one that throws leaves the others drawing. Every vendor library call is made on that thread. The vendors' callbacks arrive on their own threads and only set flags or queue events. The monochrome keys arrive on the HID readers' threads, and the G19's keys on a reader thread of their own.

---

## Which engine draws

When LGS's LCD library loads and `LogiLcdInit` succeeds, LGS draws every Logitech screen it sees and the direct writers stand down. Two programs writing one screen would fight, and LGS owns its screens while it runs. Without LGS, each Logitech screen present gets a direct writer, and the init is tried again every 10 seconds. Arx and the S.T.R.I.K.E. 7 run beside either.

Two functions decide it, and each has a test:

- `MonoDrawsDirectly(lgsActive, hasFrame, lgsSeesMono)` returns `!lgsActive || (hasFrame && !lgsSeesMono)`. Under LGS, the HID writer draws only on a monochrome screen LGS does not see.
- `G19MayBind(lgsActive)` returns `!lgsActive`. The G19's screen interface is never bound to WinUSB while LGS holds the applet.

A G19 already on PadForge's WinUSB binding is drawn directly either way, since LGS's driver cannot reach the interface then. When LGS takes the applet, the HID writer forgets what it wrote, so a kind switched to Off later does not blank a screen LGS now draws.

---

## LGS's LCD library

`LogitechServerCatalog` lists every existing path that the class registration `{D0E790A5-01A7-49AE-AE0B-E986BDD0C21B}` names in its `ServerBinary` key, the 64-bit registration first. Logitech's static library, `LogitechLCDLib.lib`, reads that key inside `LogiLcdInit`. henninglive/logitech-lcd reads the same class and then falls back to the bare DLL name along the PATH. PadForge loads only the registered paths, as Logitech's library does.

`LogitechLcdLibrary` tries each path until one loads and resolves all seven exports, and the module stays mapped for the life of the process. A failed load is tried again after 30 seconds. The header's functions return a C++ `bool`, so each return is marshaled as one byte.

`LgsLcdScreens` registers the applet only for the kinds that have a picture, so a kind set to Off stays with LGS's own applets, and a change in that set registers the applet again. It calls `LogiLcdUpdate` on every pass, as logitech-lcd's examples call it every frame. A monochrome picture goes out as 160 by 43 bytes, a pixel lit at 128 or more, and a color picture as 320 by 240 B, G, R, A pixels. After 2 seconds with nothing to show, the applet shuts down, so a mode changed in passing does not take it down and up again. `LogiLcdIsConnected` is read once a second for the status line.

LGS reports the screen keys only to the applet in front, and it keeps the round applet key and the G19's settings key for itself. The button flags are `LogitechLCDLib.h`'s: `0x0001` to `0x0008` for the four monochrome keys, and `0x0100` to `0x4000` for the G19's Left, Right, OK, Cancel, Up, Down and Menu.

---

## The monochrome screens over HID

The G15, G15 v2, G510, G510s, G13, Z-10 and GamePanel take a frame as one 992-byte output report. Byte 0 is report ID 3 and bytes 1 to 31 are zero. From byte 32 come six bands of eight rows, one byte per column of a band, with the band's top row in bit 0 and a set bit lighting the pixel. That is libg15's `dumpPixmapIntoLCDFormat`, and lcdproc, G15Interface and ecraven/g13 build the same bytes. The five rows of the last band below row 42 stay dark. A pixel lights where the picture's luminance is below half, the Dreamcast screen's threshold.

`G15HidScreens` scans every 3 seconds for HID interfaces whose path carries Logitech's VID and a monochrome PID. It probes each collection through an open that asks for no access, as `VendorHidRuntime` does, and keeps the verdict until the path goes. The collection whose output report is 992 bytes is the screen, written through `RawHidOutput`, the wheel writers' path. A collection of any other output length is never written. Every collection with input reports, except a keyboard or mouse collection that Windows keeps for itself, gets a `VendorHidReader` for the keys. When the picture goes away without LGS, one blank frame clears the screen, since nothing else draws it.

The keys come from each model's input report, as Linux's hid-lg-g15 and libg15 decode them:

| Model | Report ID | Keys 1 to 4 | Applet key |
| --- | --- | --- | --- |
| G15, Z-10, GamePanel | 2 | bit 7 of bytes 2 to 5 | bit 7 of byte 8 |
| G15 v2 | 2 | bits 1 to 4 of byte 2 | bit 7 of byte 2 |
| G510, G510s | 3 | bits 1 to 4 of byte 4 | bit 0 of byte 4 |
| G13 | 1 | bits 1 to 4 of byte 6 | bit 0 of byte 6 |

The kernel does not bind the GamePanel, so its row rests on libg15, which reads it with the G15's 9-byte decoder. Linux hands over each report at its own length, and both decoders check that length. Windows pads every read to the longest input report of the collection, so here a report is told by its ID and needs at least its own length.

While LGS draws, the readers pass on the applet key alone. LGS hands the other four to the applet in front.

---

## The G19 over WinUSB

The G19's screen is interface 0 of `046D:C229`. Frames go to bulk OUT endpoint `0x02`, and the display keys come from interrupt IN endpoint `0x81` (gnome15's pylibg19 and G19USB). A frame is a 512-byte header and 320 by 240 RGB565 pixels, low byte first, column by column with x outer and y inner, 154,112 bytes in all. The header's first 16 bytes are fixed, and every later byte is its own index modulo 256, libg19's header as both references copy it.

`G19UsbScreen` looks for interface 0 every 5 seconds:

- On WinUSB with PadForge's device interface, it opens the interface and draws.
- On no driver or the generic HID driver, and only while LGS is not active, it binds WinUSB through `VendorUsbDriverInstaller`, the installer behind PadForge's other WinUSB bindings: one INF that names the VID, PID and MI the way libwdi writes them. The bind takes seconds, so it runs on its own task while the other screens keep drawing. A failed bind is tried again after a minute.
- On any other driver, LGS's or another program's WinUSB binding, it leaves the interface alone, and the status line names the driver.

Interface 1, the G-keys, stays with Windows throughout.

The open follows `Ds3DirectService`'s USB path: an overlapped handle, `WinUsb_Initialize`, the pipes found by ID and type, and a transfer timeout on each. A frame write gets 1000 ms, gnome15's and G19USB's timeout. A key read gets 100 ms, so the reader notices a closed screen. A failed frame write closes the screen, and the next look opens it again.

The display keys arrive as a 2-byte report whose byte 1 is always `0x80`. Bits 0 to 7 of byte 0 are Settings, Cancel, Menu, OK, Right, Left, Down and Up.

Turning **Drive Keyboard Screens** off resets the service, which closes the handle, and `G19UsbScreen.Restore` then gives interface 0 back to Windows when it sits on PadForge's package. The restore takes seconds, so it runs off the UI thread.

---

## Arx Control

`LogitechArxLibrary` loads from the class registration `{267CEDC5-DC30-4155-818B-C023A80AEA78}`, which Logitech's `LogitechGArxControlLib.lib` reads in `LoadFunctionPointers`. The callback takes an event type, a value, an argument and a context, and LGS receives it inside a two-pointer context structure that it keeps for the session. PadForge pins that structure for the session and makes the delegate once per library object, which is never dropped.

The applet is one page holding one picture. The page goes out with `LogiArxAddContentAs` and `LogiArxSetIndex` right after the init, as the SDK's ARX_Test sample and LogitechStuff's CSRadar send theirs, and again on every phone arrival (event `0x08`), as ArxWidgetManager's widgets do. Each new picture goes out through `LogiArxAddImageFromBitmap` under one of two names in turn, `screen0.png` and `screen1.png`, and `LogiArxSetTagPropertyById` then points the page's image at it, so the app never reads a picture that is still being replaced. The bitmap is B, G, R, A, the order in the SDK guide's figure on page 12. LGS compresses each picture to PNG and sends it over Wi-Fi, so a new picture goes out at most every 250 ms.

After 2 seconds with nothing to show, `LogiArxShutdown` ends the applet.

---

## The S.T.R.I.K.E. 7

Mad Catz's `Strike7API.dll` reaches the keyboard's own software over a named pipe. The call order is the SDK's (`STRIKE7 API v2_2.pdf`, page 2, and its C example, `Program.cpp`). The active, inactive, touch and reset events are registered for every applet of the process (applet ID 0), and `OpenApplet` then registers the applet with its name, a 100 by 70 icon in B, G, R, A and the device list `{0x0738A109, 0}`. An applet may draw only between its active event, when the user picks it on the V.E.N.O.M. screen, and its inactive event, when the user presses the home key. `AppletDraw` followed by `AppletUpdateScreen` draws the whole 480 by 320 screen, at most every 50 ms.

The applet is open only while the kind has something to show, so its icon leaves the V.E.N.O.M. screen when the kind is set to Off. A finger dragged across the screen pans a chosen picture the way Mad Catz's map applet scrolls its map: each touch event moves the picture by the distance from the last one, until the finger lifts.

The library is x64 code, so the ARM64 build reports it unavailable and never tries to load it. It links MSVCR90 and MSVCP90 through a manifest dependency on `Microsoft.VC90.CRT` 9.0.21022.8, and a load that fails while that runtime is missing from the side-by-side store names the runtime as the reason.

**Download Strike7API.dll** fetches Mad Catz's SDK, strike7_api 1.1, from AIDA64's server, checks it, extracts one file, checks that, and keeps it in the temp folder:

| Item | Value |
| --- | --- |
| SDK | `https://download.aida64.com/users/strike7_api_1_1.zip`, 6,972,426 bytes |
| SDK SHA-256 | `A54950780B23196659D063643B8D787B5EFA08EB93098354D66FC8C2F591108D` |
| Entry kept | `STRIKE7 API V1_1/API/x64/Strike7API.dll` |
| Library SHA-256 | `86808D4FCE73E05D06CE01A1269D8FD711F45B8A31A6BE0AF648DCF8F1E9194C` |
| Kept at | `%TEMP%\PadForge\strike7\Strike7API.dll` |

The engine checks the kept copy's hash again before it loads it, so a damaged copy is reported and never loaded. A copy picked with **Choose Strike7API.dll…** loads as it is. **Install Visual C++ 2008 Runtime** downloads Microsoft's 2008 SP1 redistributable for x64, checks its Microsoft signature, runs it with `/q`, and counts it done only once the runtime is in the side-by-side store.

---

## What a mode shows

`Compose` turns a kind's mode into a picture:

- Profile Name, Profile Number, Clock (`HH:mm`), Play Time and Stopwatch draw text with `RenderText`: Segoe UI Bold, centered, from the screen's height down one pixel at a time until it fits. A monochrome screen gets aliased black text on white with no margin, cut to one bit at half luminance. A color screen gets white on black inside a margin of a twentieth of its width. Rendered text is cached by kind and string, up to 64 entries.
- Chosen Picture draws the picture at its own size with `RenderWindow`. Where the picture is larger than the screen, a screen-sized window shows it from the pan position, held to the picture's edges. Where it is smaller, it is centered.
- Profile Picture draws the active profile's picture with `RenderFitted`, scaled down to fit and centered, never scaled up. Without a picture it shows the profile's name.
- Lightbar Color fills the screen with the color through `RenderColor`. A monochrome screen shows the color's luminance, by the BT.601 weights, through a 4 by 4 Bayer matrix: white lights no pixel, black lights all and a mid gray half.

Pictures are read through a 16 MB cap and decoded no larger than 2048 pixels on a side by `BoundedBitmap`. A picture that fails to load is not read again until the screen's settings change.

Play Time counts from when the active profile switched in, and starts over when the engine starts.

### Lightbar Color

`UserEffectsDispatcher` records each pad's color in `LightbarColors`, by device and slot, where it builds the final DualShock 4 or DualSense effect bytes. It records only a frame that asserts the bar: a DualShock 4 frame always does (bits 1 and 2 of `validFlag0`), and a DualSense frame does when bit 2 of `validFlag1` is set. The screen therefore shows the color the pad took, whatever set it. The service shows the color of the lowest slot whose device is still online and mapped to that slot, and forgets a device that left. Until a color is on record, the kind shows nothing and its status line says it waits for one. The record clears when the engine stops or the feature is switched off.

---

## Macros

The four actions are appended at the end of `MacroActionType`, 58 to 61: Show Keyboard Screen, Keyboard Screen Mode, Stopwatch and Pan Keyboard Screen Picture. Each fires once and advances, the Dreamcast screen's shape, and sits in both of `EvaluateMacros`' dispatch switches. They queue requests for the service, at most 64 waiting and none while the feature is off, and the service applies them on its next tick.

- Show Keyboard Screen carries up to eight frames as base64 PNGs, each fitted to the kind's size when it is added, a frame time of at least 100 ms and a repeat count. The show plays over the mode and hands the screen back when it ends.
- Keyboard Screen Mode writes the kind's mode to the settings, where it stays.
- Stopwatch starts, pauses or resets the one stopwatch every screen shares. It keeps its time across engine restarts.
- Pan Keyboard Screen Picture moves every kind's window over its chosen picture by the step, 16 pixels by default, and stops at the picture's edges.

---

## Settings

`AppSettings` holds `KeyboardScreensEnabled` (off by default), `Strike7LibraryPath` (absent for PadForge's download) and the `KeyboardScreens` list. The list holds one `Screen` element per kind that differs from the defaults: a `Kind` attribute, `Mode` (Lightbar Color by default), `Picture`, `PanX` and `PanY`. Loading drops undefined kinds and duplicates, puts an unknown mode back to the default and a negative pan to zero. Each profile keeps its own `KeyboardScreenPicture`, and the Default profile's is `DefaultProfileKeyboardScreenPicture`.

---

## The row

`KeyboardScreenKeysDevice` is an `ISdlInputDevice` shaped like `LogitechGKeysDevice`: a synthetic row of 13 buttons, device type 42, VID `0x4B53` ("KS") and PID `0x4B4B` ("KK"). Its buttons are one fixed layout whichever engine reads a key, so a saved mapping keeps its key:

| Button index | Key |
| --- | --- |
| 0 to 3 | The four keys under a monochrome screen |
| 4 | The applet key |
| 5 to 11 | The G19's Left, Right, OK, Cancel, Up, Down and Menu |
| 12 | The G19's settings key |

Each engine reports its held keys to `KeyboardScreenKeys` under its own name, `lgs`, `g19` or `hid:` and the collection's path, and the row reads their union, so a G15 and a G19 on one PC both reach it. A key that goes down stays asserted for at least 175 ms, the G-key row's pulse, so a tap between two polls still gives a macro its edge. The poll thread creates the row while the feature is on and retires it when the feature goes off, the G-key row's lifecycle. Like the G-keys, the row numbers its own buttons from 0, so it never answers an (Any Device) mapping.

---

## Residual

No keyboard with a screen, phone with Arx Control or S.T.R.I.K.E. 7 is on the bench, so none of the drawing or key paths has run against hardware or vendor software. The HID report is checked byte for byte against a line-for-line port of libg15's `dumpPixmapIntoLCDFormat`, and the G19 frame against G19USB's header and `ConvertBitmapToRGB565`. The key decoders, the hand-off rules, the pulse, the renderer, the shows, the stopwatch, the pan limits, the settings round trip and the macro ordinals have behavioral tests. Every vendor library refuses to load in the test host, and fence tests check that each library load and the G19's device open ask their gate first.

---

## Related pages

- [Keyboard Screens](../features/keyboard-screens.md)
- [Logitech G-Keys Internals](logitech-g-keys-internals.md): the row shape this one copies, and the other LGS library PadForge loads.
- [Peripheral Outputs Internals](peripheral-outputs-internals.md): mice, keyboards and lit units that take a virtual controller's lighting.
- [Input Pipeline](input-pipeline.md)

---

*Last updated for PadForge 5.1.0.*
