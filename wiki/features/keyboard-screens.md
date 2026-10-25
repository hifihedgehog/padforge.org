# Keyboard Screens

*The screens built into Logitech's GamePanel keyboards and the Mad Catz S.T.R.I.K.E. 7, and a phone running Logitech Arx Control: the profile, a clock, play time, a stopwatch, a picture or a DualShock 4 or DualSense lightbar's color, with the keys beside the screens as buttons.*

Several gaming keyboards carry a second screen with a row of keys for it. With **Drive Keyboard Screens** on, PadForge draws on each one, a mode at a time, and the keys beside the screens become buttons you can map. A macro can play pictures on a screen, switch its mode, run a stopwatch and pan a map.

---

## The screens

| Device | Screen | Drawn through |
|---|---|---|
| Logitech G15, G15 v2, G510, G510s, G13, Z-10 speakers, GamePanel | 160 by 43, black and white | Logitech Gaming Software, else directly over USB |
| Logitech G19, G19s | 320 by 240, color | Logitech Gaming Software, else directly over USB |
| Logitech Gaming Software's LCD Emulator | Both of the above | Logitech Gaming Software |
| Logitech Arx Control on a phone | The phone's | Logitech Gaming Software 8.52 or later |
| Mad Catz S.T.R.I.K.E. 7 | The V.E.N.O.M. touchscreen, 480 by 320, color | Mad Catz's Strike7API.dll |

Each kind of screen (monochrome, color, Arx Control and S.T.R.I.K.E. 7) has its own mode, and every screen of a kind shows the same picture.

---

## Turning it on

Open **Settings**, find the **Keyboard Screens** card and tick **Drive Keyboard Screens**. It is off by default. While the engine runs, a line for each kind of screen says what draws it, for example:

- *Monochrome Screen: through Logitech Gaming Software*
- *Monochrome Screen: directly on the G510*
- *Color Screen: binding WinUSB to the G19's screen*
- *Arx Control: waiting for a phone with Arx Control*
- *S.T.R.I.K.E. 7: pick PadForge on the V.E.N.O.M. screen*

The card's **Monochrome Screen…**, **Color Screen…**, **Arx Control…** and **S.T.R.I.K.E. 7…** buttons open each kind's dialog.

### Logitech Gaming Software or direct

While Logitech Gaming Software (LGS) runs, PadForge draws the Logitech screens through it as an applet, the way games did, and LGS keeps its own applets beside it. The round applet key switches between them. Without LGS, PadForge writes the screens itself:

- A monochrome screen takes each picture as one USB report, the format libg15 and lcdproc write on Linux.
- The G19's screen is interface 0 of its USB connection. PadForge binds Windows' WinUSB driver to that interface alone, the first time it finds the G19 without LGS, and only when the interface has no driver or the generic HID driver. The G-keys on the other interface stay with Windows. Turning **Drive Keyboard Screens** off gives the interface back to Windows. While another program's driver holds it, the status line names that driver, and starting LGS draws the screen through LGS.

When LGS starts, it takes the monochrome screens over. A G19 PadForge bound to WinUSB stays with PadForge until **Drive Keyboard Screens** is turned off, since LGS's driver cannot reach the interface while WinUSB holds it.

### Arx Control

Arx Control is a phone app that shows applets from Logitech Gaming Software 8.52 or later over Wi-Fi. PadForge's applet is one page holding the screen's picture, sent again whenever a phone connects. Logitech removed Arx Control from G HUB in release 2022.7.290502 and stopped offering the app on August 24, 2022, so it needs LGS and a phone that already has the app.

### S.T.R.I.K.E. 7

The S.T.R.I.K.E. 7 draws through Mad Catz's Strike7API.dll, which talks to the keyboard's own software, so that software has to be running. PadForge does not ship the library. **Download Strike7API.dll** fetches Mad Catz's SDK from AIDA64's server, where AIDA64 points its users for the same file, checks the download against its known SHA-256 and keeps only the 64-bit library in PadForge's temporary folder. PadForge checks that copy again each time it loads it. **Choose Strike7API.dll…** uses a copy you already have instead.

The library needs Microsoft's Visual C++ 2008 runtime. When the status line says so, **Install Visual C++ 2008 Runtime** downloads Microsoft's redistributable, checks Microsoft's signature on it and installs it.

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
| **Lightbar Color** | The color of the lightbar on the DualShock 4 or DualSense in the lowest slot that has one. This is the default. |

Text is drawn as large as it fits, dark on a monochrome screen's backlight and light on a color screen's black. A monochrome screen cuts a picture to black and white at half brightness, and shows a lightbar color's brightness as a dot pattern.

**Lightbar Color** follows the color PadForge sends the controller, whatever sets it: the Lighting tab, a game or a macro. Until a color has reached a lightbar, PadForge shows nothing on the screen, and the status line says it is waiting for one.

### The dialog

Each kind's dialog sets its mode and shows a preview drawn the way the screen draws it. **Chosen Picture** takes any picture Windows can open, such as PNG, JPEG, BMP or GIF. A picture larger than the screen shows a window of the screen's size, and **Pan** sets where that window sits, in the picture's pixels, for a map. **Profile Picture** takes a picture for the active profile, and each profile keeps its own.

---

## The screen keys

With **Drive Keyboard Screens** on, the [Devices](devices.md) page carries a **Keyboard Screen Keys** row. Its buttons are the keys beside every screen in one fixed layout, so a mapping keeps its key whichever way PadForge reads it:

| Button | Key |
|---|---|
| **Screen Key 1** to **Screen Key 4** | The four keys under a monochrome screen, left to right |
| **Applet Key** | The round key beside a monochrome screen |
| **Screen Left**, **Screen Right**, **Screen OK**, **Screen Cancel**, **Screen Up**, **Screen Down**, **Screen Menu** | The G19's keys beside its screen |
| **Screen Settings** | The G19's settings key |

Under LGS, the screen keys reach PadForge only while its applet is the one on the screen, LGS's own rule, so a screen whose keys you map needs a mode other than **Off**. LGS keeps the applet key and the G19's settings key for itself. PadForge reads the applet key from the keyboard directly, and the settings key only while it draws the G19 itself. A tap shorter than one poll still presses the button once.

---

## Macros

| Action | Settings |
|---|---|
| **Show Keyboard Screen** | The kind of screen, up to eight pictures, a frame time and a repeat count. The pictures play over the mode, which returns when they end. |
| **Keyboard Screen Mode** | The kind of screen and the mode to switch it to. The mode stays as the screen's setting. |
| **Stopwatch** | **Start or Pause Stopwatch**, or **Reset Stopwatch**, which stops it at zero. One stopwatch serves every screen. |
| **Pan Keyboard Screen Picture** | Left, right, up or down, and a step in pixels. Every screen showing a chosen picture larger than itself moves, and the window stops at the picture's edges. |

See [Macros](../guides/macros.md) and the technical page, [Keyboard Screens Internals](../reference/keyboard-screens-internals.md).

---

*Last updated for PadForge 5.1.0.*
