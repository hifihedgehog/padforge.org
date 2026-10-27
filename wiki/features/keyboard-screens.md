# Keyboard Screens

*The screens built into Logitech's GamePanel keyboards and the Mad Catz S.T.R.I.K.E. 7, and a phone running Logitech Arx Control: the profile, a clock, play time, a stopwatch, a picture or a DualShock 4 or DualSense lightbar's color, with the keys beside each screen as buttons.*

Several gaming keyboards carry a second screen with a row of keys for it. With **Drive Keyboard Screens** on, each screen gets its own row on the [Devices](devices.md) page. The row's panel sets what that screen shows, and the keys beside it are the row's buttons, so two keyboards with screens keep their own settings and their own keys. A macro can play pictures on a screen, switch its mode, run a stopwatch and pan a map.

---

## The screens

| Device | Screen | Drawn through |
|---|---|---|
| Logitech G15, G15 v2, G510, G510s, G13, Z-10 speakers, GamePanel | 160 by 43, black and white | Logitech Gaming Software, else directly over USB |
| Logitech G19, G19s | 320 by 240, color | Logitech Gaming Software, else directly over USB |
| Logitech Arx Control on a phone | The phone's | Logitech Gaming Software 8.52 or later |
| Mad Catz S.T.R.I.K.E. 7 | The V.E.N.O.M. touchscreen, 480 by 320, color | Mad Catz's Strike7API.dll |

Logitech Gaming Software's LCD Emulator shows what LGS shows on the screens of its kind. It has no row of its own, so it shows nothing when no screen of its kind is plugged in.

---

## Turning it on

Open **Settings**, find the **Keyboard Screens** card and tick **Drive Keyboard Screens**. It is off by default. While the engine runs, the card names only what the feature as a whole is missing, for example:

- *Arx Control: needs Logitech Gaming Software 8.52 or later*
- *S.T.R.I.K.E. 7: needs Strike7API.dll, so download it or choose a copy*
- *Keyboard Screens: no screen found*

The card also holds the S.T.R.I.K.E. 7 library's buttons. Everything about one screen is on that screen's row.

## Each screen's row

The Devices page lists a row for each screen PadForge finds:

| Row | Found |
|---|---|
| **Logitech G15 Screen**, **Logitech G510 Screen** and the like | Each monochrome keyboard plugged in, one row per keyboard |
| **Logitech G19 Screen** | Each G19 plugged in |
| **Logitech Arx Control** | While Logitech Gaming Software's Arx library is installed |
| **Mad Catz S.T.R.I.K.E. 7 Screen** | While Strike7API.dll loads |

Select a row to see its line, for example:

- *Monochrome Screen: through Logitech Gaming Software*
- *Monochrome Screen: directly on the G510*
- *Color Screen: binding WinUSB to the G19's screen*
- *Arx Control: waiting for a phone with Arx Control*
- *S.T.R.I.K.E. 7: pick PadForge on the V.E.N.O.M. screen*

The button under the line opens that screen's dialog. It is named for the kind of screen, the way **Dreamcast Screen…** is: **Monochrome Screen…**, **Color Screen…**, **Arx Control…** or **S.T.R.I.K.E. 7…**.

### Logitech Gaming Software or direct

While Logitech Gaming Software (LGS) runs, PadForge draws the Logitech screens through it as an applet, the way games did, and LGS keeps its own applets beside it. The round applet key switches between them. Without LGS, PadForge writes each screen itself:

- A monochrome screen takes each picture as one USB report, the format libg15 and lcdproc write on Linux.
- The G19's screen is interface 0 of its USB connection. PadForge binds Windows' WinUSB driver to that interface alone, the first time it finds the G19 without LGS, and only when the interface has no driver or the generic HID driver. The G-keys on the other interface stay with Windows. Turning **Drive Keyboard Screens** off gives the interface back to Windows. While Logitech's own driver holds it, the row's line names that driver, and starting LGS draws the screen through LGS. Another program's driver, such as libusbK from Zadig, is left alone, and the line says so.

LGS takes one picture for all of its monochrome screens and one for all of its color screens. With two screens of one kind under LGS, both show the picture set for the first of them in PadForge's order, and each one's line names that screen. Without LGS, every screen shows its own.

When LGS starts, it takes the monochrome screens over. A G19 PadForge bound to WinUSB stays with PadForge until **Drive Keyboard Screens** is turned off, since LGS's driver cannot reach the interface while WinUSB holds it.

### Arx Control

Arx Control is a phone app that shows applets from Logitech Gaming Software 8.52 or later over Wi-Fi. PadForge's applet is one page holding the screen's picture, sent again whenever a phone connects. LGS sends the applet to every phone running the app, so the phones share one row. Its row is there while LGS's Arx library is installed, so it can be set before a phone connects. Logitech removed Arx Control from G HUB in release 2022.7.290502 and stopped offering the app on August 24, 2022, so it needs LGS and a phone that already has the app.

### S.T.R.I.K.E. 7

The S.T.R.I.K.E. 7 draws through Mad Catz's Strike7API.dll, which talks to the keyboard's own software, so that software has to be running. PadForge does not ship the library. **Download Strike7API.dll** on the Settings card fetches Mad Catz's SDK from AIDA64's server, where AIDA64 points its users for the same file, checks the download against its known SHA-256 and keeps only the 64-bit library in PadForge's temporary folder. PadForge checks that copy again each time it loads it. **Choose Strike7API.dll…** uses a copy you already have instead. A download that finishes takes the place of a copy you chose, and one that fails leaves your choice as it was.

The library needs Microsoft's Visual C++ 2008 runtime, and PadForge loads it once the runtime is there. When the row's line says so, **Install Visual C++ 2008 Runtime** on the Settings card downloads Microsoft's redistributable, checks Microsoft's signature on it and installs it.

PadForge's applet shows on the V.E.N.O.M. screen as an icon. Pick it there to show PadForge's picture, and the home key leaves it. On a picture larger than the screen, drag a finger across the screen to move the picture.

The ARM64 build of PadForge draws the Logitech screens directly. It cannot drive Arx Control or the S.T.R.I.K.E. 7, whose libraries are 64-bit x86 code.

---

## What a screen shows

| Mode | Shows |
|---|---|
| **Off** | Nothing from PadForge. Its applet leaves the screen, and under LGS the screen stays with LGS's applets. |
| **Profile Name** | The active profile's name |
| **Profile Number** | 0 for the Default profile, else the profile's place in the list |
| **Profile Picture** | The active profile's screen picture, else its name |
| **Clock** | The time of day |
| **Play Time** | Hours and minutes since the active profile switched in. A profile tied to a game's program switches in when the game starts, so the count is that session. The count also starts over when the engine starts. |
| **Chosen Picture** | A picture you choose, at its own size |
| **Stopwatch** | The stopwatch the Stopwatch macro runs |
| **Lightbar Color** | The color of the lightbar on the DualShock 4 or DualSense in the lowest slot this screen's row feeds, or in the lowest slot of all when the row feeds none. This is the default. |

Text is drawn as large as it fits, dark on a monochrome screen's backlight and light on a color screen's black. A monochrome screen cuts a picture to black and white at half brightness, and shows a lightbar color's brightness as a dot pattern.

**Lightbar Color** follows the color PadForge sends the controller, whatever sets it: the Lighting tab, a game or a macro. With two keyboards in two slots, each screen shows its own player's color. Until a color has reached a lightbar, PadForge shows nothing on the screen, and the row's line says it is waiting for one.

### The dialog

A screen's dialog sets its mode and shows a preview drawn the way the screen draws it. **Chosen Picture** takes any picture Windows can open, such as PNG, JPEG, BMP or GIF. A picture larger than the screen shows a window of the screen's size, and **Pan** sets where that window sits, in the picture's pixels, for a map. **Profile Picture** takes a picture for the active profile, and each profile keeps its own, which every screen in that mode shows.

---

## The screen keys

Each screen's row carries the keys beside that screen, in one fixed layout per kind, so a mapping keeps its key whichever way PadForge reads it:

| Row | Buttons |
|---|---|
| A monochrome screen | **Screen Key 1** to **Screen Key 4**, the four keys under the screen left to right, and **Applet Key**, the round key beside it |
| A G19 | **Screen Left**, **Screen Right**, **Screen OK**, **Screen Cancel**, **Screen Up**, **Screen Down**, **Screen Menu** and **Screen Settings** |
| Arx Control, the S.T.R.I.K.E. 7 | None |

Under LGS, the screen keys reach PadForge only while its applet is the one on the screen, LGS's own rule, so a screen whose keys you map needs a mode other than **Off**. LGS keeps the applet key and the G19's settings key for itself. PadForge reads the applet key from the keyboard directly, and the settings key only while it draws the G19 itself. A monochrome screen LGS does not see is one PadForge draws, and PadForge then reads all five of its keys from the keyboard. LGS does not say which keyboard a key came from, so PadForge gives a monochrome key to the keyboard whose own key report saw it go down, and to the first monochrome screen when none did. A G19 key under LGS goes to the first G19. A tap shorter than one poll still presses the button once.

---

## Macros

A keyboard screen macro reaches the screens whose rows are in the macro's slot, the way a Show Dreamcast Screen macro reaches the Dreamcast pads in its slot. Add a screen's row to a slot to aim that slot's macros at it.

| Action | Settings |
|---|---|
| **Show Keyboard Screen** | The kind of screen, up to eight pictures, a frame time and a repeat count. The pictures play on each screen of that kind in the slot, over its mode, which returns when they end. |
| **Keyboard Screen Mode** | The kind of screen and the mode to switch it to. The mode stays as each screen's setting. |
| **Stopwatch** | **Start or Pause Stopwatch**, or **Reset Stopwatch**, which stops it at zero. One stopwatch serves every screen. |
| **Pan Keyboard Screen Picture** | Left, right, up or down, and a step in pixels. Each screen in the slot showing a chosen picture larger than itself moves, and the window stops at the picture's edges. |

See [Macros](../guides/macros.md) and the technical page, [Keyboard Screens Internals](../reference/keyboard-screens-internals.md).

---

*Last updated for PadForge 5.1.0.*
