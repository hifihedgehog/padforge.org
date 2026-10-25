# Keyboard Screens Internals

*How PadForge finds each keyboard screen, gives it a row, draws on it, which engine draws while Logitech Gaming Software runs, and how the keys beside a screen reach that screen's row.*

For the user-facing side see [Keyboard Screens](../features/keyboard-screens.md).

| File | Responsibility |
| --- | --- |
| `PadForge.App/Services/KeyboardScreenService.cs` | Each screen's mode, kept by its row, the macros' shows, stopwatch and pan, a line for each screen's row and the Settings card's lines. Composes each screen's picture on the UI thread. |
| `PadForge.App/Common/Input/KeyboardScreens/KeyboardScreenHost.cs` | The worker thread that runs every engine, finds the screens, picks the picture LGS shows and deals LGS's keys to the screens. |
| `KeyboardScreenInfo.cs` | One screen: its id, kind, name and model, and its row's identity. |
| `KeyboardScreenFormats.cs` | Screen sizes, wire formats, each kind's key layout and the USB identities. |
| `KeyboardScreenRenderer.cs` | Text, pictures and a lightbar color drawn as pixels at a screen's size. |
| `LgsLcdScreens.cs` | The Logitech screens through LGS's LCD library. |
| `G15HidScreens.cs` | The monochrome screens over HID, without LGS, one per keyboard. |
| `G19UsbScreen.cs` | Each G19 over WinUSB, without LGS (`G19UsbScreen` for one, `G19UsbScreens` for all). |
| `ArxScreen.cs` | The Arx Control applet. |
| `Strike7Screen.cs` | The S.T.R.I.K.E. 7 applet. |
| `KeyboardScreenKeys.cs` | Each screen's held keys, by engine, with the press pulse. |
| `LightbarColors.cs` | The last lightbar color each DualShock 4 and DualSense took. |
| `PadForge.Engine/Common/Logitech/LogitechServerCatalog.cs` | Finds LGS's libraries by their class registrations. |
| `PadForge.Engine/Common/Logitech/LogitechLcdLibrary.cs`, `LogitechArxLibrary.cs` | The LCD and Arx exports. |
| `PadForge.Engine/Common/MadCatz/Strike7Library.cs` | The `Strike7API.dll` exports and callbacks. |

A screen's row is `PadForge.App/Common/Input/KeyboardScreenDevice.cs`, made and retired by the poll thread's sweep in `InputManager.KeyboardScreens.cs`. `KeyboardScreensRuntime.cs` mirrors the Settings switch to the engine and carries the present screens from the host to that sweep. The row's panel on the Devices page is filled by `UpdateKeyboardScreenDeviceRow` in `InputService.KeyboardScreens.cs`.

---

## Screens, kinds and threads

A screen is one physical screen, or one vendor applet, and `KeyboardScreenInfo` names it:

| Screen | Id | Row name |
| --- | --- | --- |
| A monochrome keyboard | `hid:046d:` its PID, then the container ID Windows gives every collection of the keyboard | **Logitech G15 Screen** and the like, from the PID |
| A G19 | `usb:` and the instance ID of its interface 0 | **Logitech G19 Screen** |
| Arx Control | `arx` | **Logitech Arx Control** |
| The S.T.R.I.K.E. 7 | `strike7` | **Mad Catz S.T.R.I.K.E. 7 Screen** |

The container ID groups a keyboard's collections the way the analog keyboards group theirs (`AnalogKeyboardHidRuntime.ContainerId`), so a keyboard is one screen and two keyboards are two. A collection whose devnode names no container is its own screen, by its path. Arx Control and the S.T.R.I.K.E. 7 are one screen each: LGS sends the Arx applet to every phone running the app, and Mad Catz's library reaches the screen through the keyboard's own software.

A kind is a class of screen: Monochrome (160 by 43), Color (320 by 240), Arx (480 by 320, scaled by the phone) and Strike7 (480 by 320). The kind sets a screen's size, its keys and its engine.

The service ticks on the UI thread, where WPF draws: four times a second, on every UI tick (33 ms) while a show plays, and at once after a change. It runs whether or not PadForge has focus, the Dreamcast screens' rule, so a clock keeps time behind a game. Each tick hands the host one picture per present screen with `Publish`, as top-down B, G, R, A pixels at the screen's size, or null when PadForge shows nothing there. A picture equal to the last one changes nothing.

The host keeps the latest picture per screen and runs every engine on one worker thread, `PadForge.KeyboardScreens`, every 20 ms and at once when a picture arrives. Each engine's pass has its own exception handler, so one that throws leaves the others drawing. After each pass the host lists the present screens in id order and publishes the list for the rows when it changes. Every vendor library call is made on that thread. The vendors' callbacks arrive on their own threads and only set flags or queue events. The monochrome keys arrive on the HID readers' threads, and each G19's keys on a reader thread of their own.

---

## Which engine draws

When LGS's LCD library loads and `LogiLcdInit` succeeds, LGS draws every Logitech screen it sees and the direct writers stand down. Two programs writing one screen would fight, and LGS owns its screens while it runs. Without LGS, each Logitech screen present gets its own picture through its direct writer, and the init is tried again every 10 seconds. Arx and the S.T.R.I.K.E. 7 run beside either.

Two functions decide it, and each has a test:

- `MonoDrawsDirectly(lgsActive, lgsSeesMono)` returns `!lgsActive || !lgsSeesMono`. Under LGS, the HID writer draws only while LGS sees no monochrome screen.
- `G19MayBind(lgsActive)` returns `!lgsActive`. A G19's screen interface is never bound to WinUSB while LGS holds the applet.

A G19 already on PadForge's WinUSB binding is drawn directly either way, since LGS's driver cannot reach the interface then. When LGS takes the applet, the HID writer forgets what it wrote, so a screen switched to Off later does not blank a screen LGS now draws.

LGS's library names no device (`LogitechLCDLib.h`), so LGS takes one picture for all of its monochrome screens and one for all of its color screens. Logitech's older lgLcd library could open one device by index (`lgLcdEnumerate`, `lgLcdOpen`), but its SDK marks those calls deprecated as of version 3, and it ships only as a static C library, which zzattack's Logitech-LCD project rebuilds into a DLL of its own. LgLCD.Net and zzattack's wrapper both open by type. The host gives it the picture of each kind's leading screen, the first in id order (`Leader`). With more than one screen of a kind, `SharedLeader` names that screen, and every one of their rows' lines says whose picture shows. LGS's LCD Emulator shows the same picture LGS sends the screens of its kind, and has no row.

---

## LGS's LCD library

`LogitechServerCatalog` lists every existing path that the class registration `{D0E790A5-01A7-49AE-AE0B-E986BDD0C21B}` names in its `ServerBinary` key, the 64-bit registration first. Logitech's static library, `LogitechLCDLib.lib`, reads that key inside `LogiLcdInit`. henninglive/logitech-lcd reads the same class and then falls back to the bare DLL name along the PATH. PadForge loads only the registered paths, as Logitech's library does.

`LogitechLcdLibrary` tries each path until one loads and resolves all seven exports, and the module stays mapped for the life of the process. A failed load is tried again after 30 seconds. The header's functions return a C++ `bool`, so each return is marshaled as one byte.

`LgsLcdScreens` registers the applet only for the kinds whose leading screen has a picture, so a kind set to Off stays with LGS's own applets, and a change in that set registers the applet again. It calls `LogiLcdUpdate` on every pass, as logitech-lcd's examples call it every frame. A monochrome picture goes out as 160 by 43 bytes, a pixel lit at 128 or more, and a color picture as 320 by 240 B, G, R, A pixels. After 2 seconds with nothing to show, the applet shuts down, so a mode changed in passing does not take it down and up again. `LogiLcdIsConnected` is read once a second for the rows' lines.

LGS reports the screen keys only to the applet in front, and it keeps the round applet key and the G19's settings key for itself. The button flags are `LogitechLCDLib.h`'s: `0x0001` to `0x0008` for the four monochrome keys, and `0x0100` to `0x4000` for the G19's Left, Right, OK, Cancel, Up, Down and Menu. LGS does not say which keyboard a key came from either, so `LgsLcdScreens` hands its flags to the host, which deals them (`DealLgsKeys`): a monochrome key goes to each keyboard whose own HID reader saw that key held, or go down within 350 ms (twice the pulse), and to the leading monochrome screen when none did. A color key goes to the leading G19.

---

## The monochrome screens over HID

The G15, G15 v2, G510, G510s, G13, Z-10 and GamePanel take a frame as one 992-byte output report. Byte 0 is report ID 3 and bytes 1 to 31 are zero. From byte 32 come six bands of eight rows, one byte per column of a band, with the band's top row in bit 0 and a set bit lighting the pixel. That is libg15's `dumpPixmapIntoLCDFormat`, and lcdproc, G15Interface and ecraven/g13 build the same bytes. The five rows of the last band below row 42 stay dark. A pixel lights where the picture's luminance is below half, the Dreamcast screen's threshold.

`G15HidScreens` scans every 3 seconds for HID interfaces whose path carries Logitech's VID and a monochrome PID, with the devnode of each for its container. It probes each collection through an open that asks for no access, as `VendorHidRuntime` does, and keeps the verdict until the path goes. The collections of one container are one keyboard. The keyboard's collection whose output report is 992 bytes is its screen, written through `RawHidOutput`, the wheel writers' path, with that keyboard's own picture. A collection of any other output length is never written. Every collection with input reports, except a keyboard or mouse collection that Windows keeps for itself, gets a `VendorHidReader`, and its keys reach that keyboard's row. When a keyboard's picture goes away without LGS, one blank frame clears its screen, since nothing else draws it.

The keys come from each model's input report, as Linux's hid-lg-g15 and libg15 decode them:

| Model | Report ID | Keys 1 to 4 | Applet key |
| --- | --- | --- | --- |
| G15, Z-10, GamePanel | 2 | bit 7 of bytes 2 to 5 | bit 7 of byte 8 |
| G15 v2 | 2 | bits 1 to 4 of byte 2 | bit 7 of byte 2 |
| G510, G510s | 3 | bits 1 to 4 of byte 4 | bit 0 of byte 4 |
| G13 | 1 | bits 1 to 4 of byte 6 | bit 0 of byte 6 |

The kernel does not bind the GamePanel, so its row rests on libg15, which reads it with the G15's 9-byte decoder. Linux hands over each report at its own length, and both decoders check that length. Windows pads every read to the longest input report of the collection, so here a report is told by its ID and needs at least its own length.

While LGS draws, the readers pass on the applet key alone, and keep each keyboard's held keys and the time each went down for LGS's keys to be dealt by.

---

## The G19 over WinUSB

The G19's screen is interface 0 of `046D:C229`. Frames go to bulk OUT endpoint `0x02`, and the display keys come from interrupt IN endpoint `0x81` (gnome15's pylibg19 and G19USB). A frame is a 512-byte header and 320 by 240 RGB565 pixels, low byte first, column by column with x outer and y inner, 154,112 bytes in all. The header's first 16 bytes are fixed, and every later byte is its own index modulo 256, libg19's header as both references copy it.

`G19UsbScreens` lists the USB nodes every 5 seconds and keeps a `G19UsbScreen` for each interface 0 of `046D:C229`, by its instance ID. A G19 that leaves takes its screen and its keys with it. Each `G19UsbScreen` looks at its own node:

- On WinUSB with PadForge's device interface, it opens the interface and draws that G19's picture.
- On no driver or the generic HID driver, and only while LGS is not active, it binds WinUSB through `VendorUsbDriverInstaller`, the installer behind PadForge's other WinUSB bindings: one INF that names the VID, PID and MI the way libwdi writes them. The bind takes seconds, so it runs on its own task while the other screens keep drawing. A failed bind is tried again after a minute.
- On any other driver, LGS's or another program's WinUSB binding, it leaves the interface alone, and the row's line names the driver.

Interface 1, the G-keys, stays with Windows throughout.

The open follows `Ds3DirectService`'s USB path: an overlapped handle, `WinUsb_Initialize`, the pipes found by ID and type, and a transfer timeout on each. A frame write gets 1000 ms, gnome15's and G19USB's timeout. A key read gets 100 ms, so the reader notices a closed screen. A failed frame write closes the screen, and the next look opens it again.

The display keys arrive as a 2-byte report whose byte 1 is always `0x80`. Bits 0 to 7 of byte 0 are Settings, Cancel, Menu, OK, Right, Left, Down and Up.

Turning **Drive Keyboard Screens** off resets the service, which closes the handles, and `G19UsbScreen.Restore` then gives every G19's interface 0 back to Windows when it sits on PadForge's package. The restore takes seconds, so it runs off the UI thread.

---

## Arx Control

`LogitechArxLibrary` loads from the class registration `{267CEDC5-DC30-4155-818B-C023A80AEA78}`, which Logitech's `LogitechGArxControlLib.lib` reads in `LoadFunctionPointers`. The callback takes an event type, a value, an argument and a context, and LGS receives it inside a two-pointer context structure that it keeps for the session. PadForge pins that structure for the session and makes the delegate once per library object, which is never dropped.

Arx Control's row is there while the library loads, so it can be set before a phone connects, even to Off. The applet is one page holding one picture. The page goes out with `LogiArxAddContentAs` and `LogiArxSetIndex` right after the init, as the SDK's ARX_Test sample and LogitechStuff's CSRadar send theirs, and again on every phone arrival (event `0x08`), as ArxWidgetManager's widgets do. Each new picture goes out through `LogiArxAddImageFromBitmap` under one of two names in turn, `screen0.png` and `screen1.png`, and `LogiArxSetTagPropertyById` then points the page's image at it, so the app never reads a picture that is still being replaced. The bitmap is B, G, R, A, the order in the SDK guide's figure on page 12. LGS compresses each picture to PNG and sends it over Wi-Fi, so a new picture goes out at most every 250 ms.

After 2 seconds with nothing to show, `LogiArxShutdown` ends the applet.

---

## The S.T.R.I.K.E. 7

Mad Catz's `Strike7API.dll` reaches the keyboard's own software over a named pipe. The call order is the SDK's (`STRIKE7 API v2_2.pdf`, page 2, and its C example, `Program.cpp`). The active, inactive, touch and reset events are registered for every applet of the process (applet ID 0), and `OpenApplet` then registers the applet with its name, a 100 by 70 icon in B, G, R, A and the device list `{0x0738A109, 0}`. An applet may draw only between its active event, when the user picks it on the V.E.N.O.M. screen, and its inactive event, when the user presses the home key. `AppletDraw` followed by `AppletUpdateScreen` draws the whole 480 by 320 screen, at most every 50 ms.

The S.T.R.I.K.E. 7's row is there while the library loads. The applet is open only while the screen has something to show, so its icon leaves the V.E.N.O.M. screen when the screen is set to Off. A finger dragged across the screen pans a chosen picture the way Mad Catz's map applet scrolls its map: each touch event moves the picture by the distance from the last one, until the finger lifts.

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

`Compose` turns a screen's mode into a picture at its kind's size:

- Profile Name, Profile Number, Clock (`HH:mm`), Play Time and Stopwatch draw text with `RenderText`: Segoe UI Bold, centered, from the screen's height down one pixel at a time until it fits. A monochrome screen gets aliased black text on white with no margin, cut to one bit at half luminance. A color screen gets white on black inside a margin of a twentieth of its width.
- Chosen Picture draws the picture at its own size with `RenderWindow`. Where the picture is larger than the screen, a screen-sized window shows it from the pan position, held to the picture's edges. Where it is smaller, it is centered.
- Profile Picture draws the active profile's picture with `RenderFitted`, scaled down to fit and centered, never scaled up. Without a picture it shows the profile's name.
- Lightbar Color fills the screen with the color through `RenderColor`. A monochrome screen shows the color's luminance, by the BT.601 weights, through a 4 by 4 Bayer matrix: white lights no pixel, black lights all and a mid gray half.

Each screen keeps its last composed picture and what it shows, and draws again only when that changes, since a frame of the larger screens is over half a megabyte and the tick runs four times a second. Pictures are read through a 16 MB cap and decoded no larger than 2048 pixels on a side by `BoundedBitmap`. A picture that fails to load is not read again until a screen's settings change.

Play Time counts from when the active profile switched in, and starts over when the engine starts.

### Lightbar Color

`UserEffectsDispatcher` records each pad's color in `LightbarColors`, by device and slot, where it builds the final DualShock 4 or DualSense effect bytes. It records only a frame that asserts the bar: a DualShock 4 frame always does (bits 1 and 2 of `validFlag0`), and a DualSense frame does when bit 2 of `validFlag1` is set. The screen therefore shows the color the pad took, whatever set it. A screen shows the color of the lowest slot among the slots its row feeds, or among all slots when its row feeds none, whose device is still online and mapped to that slot, and a device that left is forgotten. With two keyboards in two slots, each shows its own player's color. Until a color is on record, the screen shows nothing and its row's line says it waits for one. The record clears when the engine stops or the feature is switched off.

---

## Macros

The four actions are appended at the end of `MacroActionType`, 58 to 61: Show Keyboard Screen, Keyboard Screen Mode, Stopwatch and Pan Keyboard Screen Picture. Each fires once and advances, the Dreamcast screen's shape, and sits in both of `EvaluateMacros`' dispatch switches. They queue requests for the service with the macro's slot, at most 64 waiting and none while the feature is off, and the service applies them on its next tick to the screens whose rows feed that slot (`Feeding`, by each row's `UserSetting.MapTo`), the Show Dreamcast Screen macro's rule.

- Show Keyboard Screen carries up to eight frames as base64 PNGs, each fitted to the kind's size when it is added, a frame time of at least 100 ms and a repeat count. The show plays on each screen of that kind in the slot, over its mode, and hands the screen back when it ends.
- Keyboard Screen Mode writes the mode of each screen of that kind in the slot to the settings, where it stays.
- Stopwatch starts, pauses or resets the one stopwatch every screen shares. It keeps its time across engine restarts.
- Pan Keyboard Screen Picture moves the window of each screen in the slot over its chosen picture by the step, 16 pixels by default, and stops at the picture's edges.

---

## Settings

`AppSettings` holds `KeyboardScreensEnabled` (off by default), `Strike7LibraryPath` (absent for PadForge's download) and the `KeyboardScreens` list. The list holds one `Screen` element per screen whose choices differ from the defaults, the way `BlissBoxPorts` keeps a Dreamcast pad's: a `Device` attribute holding the row's InstanceGuid, `Mode` (Lightbar Color by default), `Picture`, `PanX` and `PanY`. Loading drops an entry with no readable device and a second entry for one device, puts an unknown mode back to the default and a negative pan to zero. Each profile keeps its own `KeyboardScreenPicture`, which every screen in Profile Picture mode shows, and the Default profile's is `DefaultProfileKeyboardScreenPicture`.

The Settings card holds the switch, the S.T.R.I.K.E. 7 library's buttons and lines for the feature as a whole (`SubsystemLines`): Arx Control's or the S.T.R.I.K.E. 7's library while neither has a row, and no screen found when there is no row at all. It sets nothing for one screen and names none. Each screen's line and dialog are on its row's panel.

---

## The rows

`KeyboardScreenDevice` is an `ISdlInputDevice` shaped like `LogitechGKeysDevice`: a synthetic row per screen, device type 42, VID `0x4B53` ("KS"), and a PID per kind: `0x4B4D` ("KM"), `0x4B43` ("KC"), `0x4B41` ("KA") and `0x4B37` ("K7"). Its InstanceGuid is an MD5 of the screen's id, the same each time the screen is found. Its buttons are the kind's one fixed layout whichever engine reads a key, so a saved mapping keeps its key:

| Kind | Button index | Key |
| --- | --- | --- |
| Monochrome | 0 to 3 | The four keys under the screen |
| Monochrome | 4 | The applet key |
| Color | 0 to 6 | The G19's Left, Right, OK, Cancel, Up, Down and Menu |
| Color | 7 | The G19's settings key |
| Arx, Strike7 | none | |

Each engine reports a screen's held keys to `KeyboardScreenKeys` under the screen's id and its own name, `hid`, `g19` or `lgs`, and the screen's row reads their union, so two keyboards stay apart. A key that goes down stays asserted for at least 175 ms, the G-key row's pulse, so a tap between two polls still gives a macro its edge. The poll thread's sweep makes a row for each screen the host publishes and retires a row whose screen left, the Falcons' shape, and a row the user removes from the Devices page comes back while its screen is still there. Like the G-keys, a row numbers its own buttons from 0, so it never answers an (Any Device) mapping.

The row's panel on the Devices page shows the screen's line and a button named for its kind, which opens the screen's dialog (`ConfigureKeyboardScreen` in `MainWindow.KeyboardScreens.cs`), the Dreamcast Screen button's place.

---

## Residual

No keyboard with a screen, phone with Arx Control or S.T.R.I.K.E. 7 is on the bench, so none of the drawing or key paths has run against hardware or vendor software. The HID report is checked byte for byte against a line-for-line port of libg15's `dumpPixmapIntoLCDFormat`, and the G19 frame against G19USB's header and `ConvertBitmapToRGB565`. The key decoders, each screen's identity, the keys of two screens kept apart, the leading screen LGS shows, the macros' slot rule, the light bar by slot, the hand-off rules, the pulse, the renderer, the shows, the stopwatch, the pan limits, the settings round trip and the macro ordinals have behavioral tests. Every vendor library refuses to load in the test host, and fence tests check that each library load and each G19's device open ask their gate first. That Windows gives each keyboard's collections one container, and two keyboards two, is Windows' container rule as the analog keyboards rely on it, not measured on these models.

---

## Related pages

- [Keyboard Screens](../features/keyboard-screens.md)
- [Logitech G-Keys Internals](logitech-g-keys-internals.md): the row shape this one copies, and the other LGS library PadForge loads.
- [Peripheral Outputs Internals](peripheral-outputs-internals.md): mice, keyboards and lit units that take a virtual controller's lighting.
- [Input Pipeline](input-pipeline.md)

---

*Last updated for PadForge 5.1.0.*
