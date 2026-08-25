# Handheld PC Buttons

*The rear paddles, menu keys, and wheels a handheld gaming PC hides from every game. Press each one once to learn it, then map it like any other button.*

Handheld gaming PCs (Legion Go, ROG Ally, GPD Win, OneXPlayer, AYANEO, AYN, Zotac Zone, MSI Claw) and gaming laptops carry buttons the operating system never presents as part of a controller. The firmware delivers them one of three ways: as a keyboard combination typed by an embedded keyboard (Ctrl+Win+F17, Win+D, F21 through F24), as bits and codes inside a vendor-defined HID report on the same USB device as the gamepad, or as a vendor WMI event (a Legion laptop's Vantage key). Either way a game sees a keystroke at best, and the vendor's own tool is the only thing that can remap them.

PadForge learns them on your machine. There is no table of models inside the app and no release needed for a handheld that ships tomorrow.

---

## Turning it on

Open **Settings** and turn on **Enable Handheld PC Buttons**. Two rows appear on the [Devices](devices.md) page:

| Row | What it is |
| --- | --- |
| **Hidden Buttons** (named after your machine) | Every button you have learned, each a named, bindable button |
| **Motion** (named after your machine) | The machine's own gyroscope and accelerometer, for handhelds whose motion sensor sits in the tablet rather than in the controller halves |

With the toggle off, nothing runs: no device rows, no keyboard hook, no vendor HID handles, no sensor subscription. A desktop that never uses this pays nothing for it.

---

## Learning a button

Select the **Hidden Buttons** row and click **Learn / Manage Hidden Buttons**. The dialog walks one press:

1. **Start Learning**. For one second, keep your hands off the machine while PadForge reads the idle state of every vendor report, so bytes that move on their own (motion sensor words, counters) can never become a button.
2. **Press the hidden button** when asked, then let go. A tap or a hold both work, and a key that only reports on a short tap (a Legion laptop's Smart Connect key) needs the tap.
3. **Release** it if you were holding it.

Whatever the press changed is shown under **Source**: the key combination the firmware typed, the report field that flipped, or both. Some buttons do both (the Legion Go's Desktop button sets a report bit and types Win+D), and PadForge records both halves under one button so the keystroke is swallowed while the report keeps the state. If a report changed in more than one place, pick the field from the list. Give the button a name and click **Register**.

Repeat for every paddle and key. Each learned button keeps the index it was given for good, so a binding made today survives buttons added or removed later.

---

## How the two paths behave

**Key combinations** go through PadForge's low-level keyboard and mouse hooks. A learned combination is swallowed before the shell sees it, so Win+D no longer minimizes your desktop and F24 no longer reaches the game as a key. A key that is only the start of a combination is held back for 100 ms. If the rest never arrives, it is replayed, so typing F11 by itself still types F11. Modifier keys are never held back. A combination containing Win gets the AutoHotkey treatment (a reserved mask key) so releasing Win does not open the Start menu.

**Report fields** are read from the vendor HID collection directly, with shared access, so the vendor's own tool keeps working beside PadForge. A bit that flips on press and flips back on release is a held button, whichever way it flips. A code that appears only while the key is down (the ROG Ally shape) is a button that releases 150 ms after its last report. Only the collections your learned buttons name are kept open. During a learn pass, every vendor collection on the machine is watched.

**System events** cover the third kind of key: one the firmware reports to the vendor's WMI provider rather than to any keyboard or HID device. Lenovo's Vantage and Smart Connect keys on a Legion laptop arrive only this way, as a `LENOVO_UTILITY_EVENT` with a press code. During a learn pass PadForge subscribes to the event classes the firmware itself declares (the ACPI-WMI `_WDG` table lists every event GUID the machine's firmware can raise, on any brand), and an event that fires while the key is held or when it is released becomes a button, unless it keeps firing at rest (a periodic status event). Some keys report on release (the Legion laptop's Smart Connect key), so a short press when asked is what learns them. One early press does not spoil the pass. Event classes owned by other drivers are never touched. An event is a press with no release, so the button pulses for 175 ms. The same rule covers laptops as well as handhelds: a special key is a special key.

A learned button asserts for at least 175 ms, so a firmware tap that lasts two milliseconds still registers on a macro poll.

---

## Binding

A learned button binds anywhere a real button does: the mapping grid, macro triggers, shift layers, formulas, auto-profile switching, and the recorders all offer it by the name you gave it.

## Watching it live

The **Hidden Buttons** row's details pane lists every learned button and lights each one while it is down. If the vendor's daemon (Legion Space, Armoury Crate, MSI Center M, Zotac's quick settings, AYASpace) is running, the pane says so: that tool keeps reacting to the same buttons until you close it.

## Sharing a set

**Export** writes the learned set to a small JSON file, and **Import** reads one in. One owner's learn pass seeds every machine of that model.

---

## Motion

The **Motion** row feeds the same gyro pipeline every controller uses: gyro aim, tilt steering, calibration, and axis signs all apply. Readings are converted from the Windows sensor units (degrees per second, g) to the frame PadForge's motion code expects. The Steam Deck needs none of this: its paddles and motion sensor already arrive through SDL3.

---

## Limitations, stated plainly

- Learning needs the vendor's own tool to leave the buttons alone during the press. On some machines (ROG Ally M1 and M2, Zotac paddles) the vendor tool reprograms which keys the buttons type, so learn them with that tool in the state you will play in.
- A vendor report that only arrives while its tool holds the device open exclusively cannot be read. PadForge opens with shared access and reports a collection it could not open in the diagnostics log.
- Firmware-side mode commands (gyro enable, controller reset) are not sent. The machine is read as the vendor's driver leaves it.
- The frame mapping for the Motion row follows the Windows sensor axes for a machine held upright facing you. It has not been validated on handheld hardware.

*Last updated for PadForge 4.4.0.*
