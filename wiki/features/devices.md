# Devices

*Every gamepad, joystick, keyboard, mouse, and touchpad PadForge can see lives on this page as a card.*

![Devices page showing detected controllers with status and slot badges](../images/devices.png)

---

## Page layout

| Area | What it holds |
|------|----------|
| **Left panel** | One card for each detected device |
| **Right panel** | Detail pane for the selected device. Identity, slot assignment, hiding, live raw input. |
| **Header** | **Refresh** button, **Pair** button (Wii controllers, DualShock 3, PS Move / Navigation), **Online** count, **Total** count (includes disconnected) |

---

## Device card list

Physical devices sort first. Merged devices (All Keyboards, All Mice, All Touchpads, All Consumer Controls) sort to the bottom. Within each group, cards sort alphabetically by name, then by Vendor ID, then by Product ID.

### Type filter chips

A row of chips sits above the card list: **ALL**, **GAMEPAD**, **JOYSTICK**, **WHEEL**, **KEYBOARD**, **MOUSE**, **OTHER**. Each chip carries a live count of the devices in that group. Click one to show only that type. Click **ALL** to clear the filter. The active chip lights up in ember orange, and the counts update as devices connect and drop.

GAMEPAD covers standard pads. JOYSTICK covers joysticks and flight sticks. WHEEL covers racing wheels. OTHER holds everything else: touchpads, MIDI devices, NFC readers, and anything unclassified.

<!-- SCREENSHOT: devices-facet-chips -->
![Type filter chips above the device list, each with a live count](../images/devices-facet-chips.png)

### Card layout

Top row:

| Element | Description |
|---------|-------------|
| **Status flame** | The same ember flame the driver cards wear. Filled and glowing for connected, outline only for disconnected. |
| **Device name** | The name the hardware reports (e.g., "Xbox Wireless Controller"). Merged devices show "All Keyboards (Merged)", "All Mice (Merged)", "All Touchpads (Merged)", or "All Consumer Controls (Merged)". |
| **Slot badges** | [Slot](controller-slots.md) numbers the device is assigned to, each with the slot's controller-type icon (a Nintendo slot wears the Switch mark). No badge shows if the device is unassigned. |
| **Remove button** | X. Opens a **Remove Device** confirmation, and the device and its settings are deleted once you click **Remove**. Revealed on hover or keyboard focus. |

Bottom row (one wrapping metadata line):

| Element | Description |
|---------|-------------|
| **Type** | Gamepad, Joystick, Wheel, Flight Stick, First Person, Supplemental, Mouse, Keyboard, Touchpad, NFC Reader, Consumer Control, MIDI Controller, Microphone, Headset Tracker, Handheld Buttons, System Motion, Head Tracker, or plain Device for anything unclassified. |
| **VID:PID** | USB Vendor and Product ID in hex (`054C:0CE6` for DualSense). Omitted for merged and virtual sources that report no ID. |
| **Capabilities** | Axis, button, and POV hat counts plus feature tags: Rumble, Gyro, Accel, Touchpad (a gamepad with a touch surface), and NFC (a Switch controller with a tag reader) |
| **Battery** | A battery glyph and percentage for a connected device that reports a battery level. The glyph switches to a charging variant while the device is charging. |

Devices that report no battery (wired pads without one, most wired sticks and wheels) and offline devices show no battery indicator. A battery-equipped pad on a USB cable shows the charging glyph. The same percentage appears again as a small suffix next to the device name in a slot's assigned-device list, so you can read a controller's charge without opening its card.

### Selecting a card

Click a card. A vertical accent bar appears on the left edge. The detail pane fills in.

### Removing a device

The X button opens a **Remove Device** confirmation. Click **Remove** and the device and all its settings (mappings, slot assignments, hiding) are deleted. The [slot](controller-slots.md) stays. It just becomes unassigned.

If the device is still plugged in, it comes back on the next scan as a fresh device with no settings.

---

## Device detail pane

### Device name and dossier

The detail pane opens with the device name as a large heading. Below it sits the **Device Dossier**, a recessed monospace card that gathers every identity field PadForge holds for the device into one place. A **Copy** button at the top-right of the card copies the whole dossier to the clipboard as text, handy when filing a bug report.

Rows whose fact the device does not report collapse instead of showing a blank placeholder. A wired pad shows no LINK or SERIAL row. A device with no resolvable HID path shows no PATH row.

<!-- SCREENSHOT: devices-dossier -->
![Device Dossier card with labeled identity rows and a Copy button](../images/devices-dossier.png)

| Row | Description |
|-----|-------------|
| **PRODUCT** | Product name from hardware |
| **TYPE** | Device category |
| **CAPS** | Axis / button / POV counts and feature tags |
| **APP GUID** | The identity string PadForge builds from device path, VID:PID, and serial number. It is what keeps a device's settings across reboots and re-plugs. Marquee-scrolls if long. |
| **SDL GUID** | The 32-character hex string SDL uses to look up the device's mapping. Shown when the device reports one. Marquee-scrolls if long. |
| **PATH** | HID path used for HidHide hiding. Shown for devices that report a resolvable path. A bridged device (such as a DualShock 3 over Bluetooth) shows its connection path here instead. |
| **VID:PID** | Vendor and Product ID in hex |
| **LINK** | Reads **BT** for a Bluetooth connection. Absent for wired and other links. |
| **SERIAL** | The serial number the device reports (a Bluetooth MAC address on most wireless pads). Shown when reported. |
| **BATT** | Battery glyph and percentage. Shown only when the device reports a battery. |

A row of capability icons sits at the bottom of the card: rumble, gyro, and touchpad marks light up for the devices that have them.

### Submit Device Mapping button

Shows in the detail pane for any device PadForge does not already recognize. It is hidden for known gamepads, keyboards, mice, touchpads, MIDI devices, NFC readers, headset motion trackers, Consumer Control devices, microphones, and the Hidden Buttons, System Motion, and Head Tracker rows. Everything else gets the button, so joysticks, wheels, flight sticks, and unclassified HID devices all qualify.

Click it. Your browser opens a GitHub issue pre-filled with every field PadForge can read from the device:

- Device name
- USB Vendor ID (hex)
- USB Product ID (hex)
- SDL GUID (the 32-character hex string SDL uses to look up mappings)
- Axis count
- Button count
- Hat / POV count

You fill in the per-input mapping by hand. Which raw axis index is Left Stick X. Which raw button index is A. Read those off the **raw input** section on this page while pressing each control.

Once the issue is merged, the mapping ships in the app's built-in controller mapping database and auto-loads on every PadForge install. Future users with the same hardware get the device recognized without further setup.

#### Why use the button over a blank template

The blank Device Mapping issue template makes you type the device identification fields yourself. The in-app button reads them straight from PadForge's live SDL3 enumeration, so the SDL GUID can't be mistyped. Use the button when the device is plugged in.

---

## Assigning devices to slots

### Toggle buttons

The **Virtual Controller Assignment** section in the detail pane shows numbered toggles, one per existing [slot](controller-slots.md).

- **Highlighted** = assigned to that slot
- **Normal** = not assigned
- More than one toggle can be on at the same time (see Multi-slot below)

Assigning a device builds a default [mapping](mappings.md) if none exists and updates the slot badges. You stay on the Devices page. Open the slot's config page from the sidebar when you want to tune the mapping.

### Drag and drop

Drag a card from the left panel onto a sidebar slot card. Same result as clicking the toggle.

### What happens on assignment

1. The slot's [virtual controller](controller-slots.md) is created if it does not exist yet
2. A default [mapping](mappings.md) is built for the device type and output type (Xbox, PlayStation, Nintendo, Extended, etc.)
3. For gamepads and joysticks, **Hide from Games (HidHide)** turns on if HidHide is installed
4. Slot badges update right away

Unassigning a device from every slot clears both hiding options.

---

## Multi-slot assignment

One physical device can feed more than one [slot](controller-slots.md) at the same time. Real uses:

- **Two output types at once.** One pad feeding an Xbox slot for the game and an Extended slot for a flight sim overlay.
- **Split button subsets.** Left side mapped to one slot, right side to another.
- **A/B testing.** Compare [deadzone](stick-deadzones.md), sensitivity, or [macro](../guides/macros.md) setups without swapping hardware.
- **MIDI plus gamepad.** Game input and MIDI signals from the same pad.

Toggle multiple slot buttons in the detail pane. Each slot keeps its own [mapping](mappings.md), so the same physical input can mean different things on different slots.

Slot badges show every assigned slot number at a glance.

---

## Raw input

The bottom of the detail pane shows live hardware data before any [mapping](mappings.md), [deadzone](stick-deadzones.md), or sensitivity work. Updates at the engine polling rate.

### Axes

Each axis row has:

| Element | Description |
|---------|-------------|
| **Name** | Always Axis N, numbered by the axis's real slot. In gamepad mode a pad that lacks a stick or trigger skips those numbers, so gaps are normal (a PS Move Navigation reads Axis 0, 1, 2, then 6, 7, 10). Raw mode numbers densely from 0. The row never switches to friendly names like LX or LT. |
| **Progress bar** | Horizontal, 0-1 range. A centered stick reads ~50%. |
| **Raw value** | Exact integer (0-65535) in monospace |

Look for:

- **Center drift.** The axis does not rest at ~32768 when you let go. Use Calibrate Center on the [Sticks](stick-deadzones.md) tab.
- **Trigger baseline.** Some triggers rest at 0, others at 32768. Depends on hardware and input mode.
- **Dead axes.** Axis never moves. The mapping database may have a bad entry. Try Force Raw Joystick Mode.

### Buttons

Small circles in a wrap layout, labeled by index (0, 1, 2...).

| State | Look |
|-------|------------|
| Released | Dim recessed cell |
| Pressed | Outline and number lit in cold blue, with a glow |

Gamepad mode shows the standard buttons the pad has (0 is A, 1 is B, on through Guide at 10, and a partial pad such as the PS Move Navigation skips the ones it lacks) plus every extended button the pad actually has: Misc1 at 11, paddles at 12–15, touchpad click at 16, Misc2–6 at 17–21. Physical buttons the mapping leaves unclaimed follow from 22 up. Each circle is numbered by its real index, the same number the mapping picker and recorder use, so gaps are normal. A DualSense shows a button 16 for its touchpad click with nothing at 12–15. Raw mode shows every physical button instead, densely numbered from 0. Either way the circles read as numbers, not letters.

Consumer Control and NFC Reader devices replace the numbered grid with named chips (media keys) or named tags. See their sections below.

### Keyboards

A QWERTY layout replaces axes and buttons. Main keys, navigation cluster, arrows, numpad. Keys light up in the same cold blue as the button circles as you press them.

### Mice

A mouse graphic replaces axes and buttons:

- Button presses highlight on the mouse body
- Motion direction shows visually
- Scroll wheel activity reads as scroll intensity

### POV / D-pad

Compass widgets with a direction line, labeled "POV 0", "POV 1", etc.

| State | Look |
|-------|------------|
| Centered | Background circle with center dot, no line |
| Direction pressed | Cold blue line from center toward the pressed direction |

All 8 directions are supported (N, NE, E, SE, S, SW, W, NW). Some specialty controllers report continuous angular values.

### Gyroscope

Shows on devices with a gyro sensor (DualSense, DualShock 4, Switch Pro, others). Rotational velocity. Used by the [DSU Motion Server](../reference/dsu-motion-server.md) for motion-enabled emulators.

| Axis | Motion |
|------|--------|
| **X** | Pitch (forward / backward tilt) |
| **Y** | Yaw (left / right rotation) |
| **Z** | Roll (side-to-side tilt) |

Three decimal places. A still controller reads near 0.000.

A second block, **Aux Gyroscope**, appears for the left Joy-Con of a combined pair. It sits beside the Aux Accelerometer readout, so you can see which half a reading comes from, and it maps as its own source (Left Joy-Con Gyro Pitch, Yaw, and Roll). Only the Joy-Con pair shows one. The Nunchuk has no gyro.

### Accelerometer

Shows on devices with an accelerometer. Linear acceleration:

| Axis | Motion |
|------|--------|
| **X** | Left / right |
| **Y** | Up / down. Gravity registers here, so a still controller reads about 9.8 or -9.8. |
| **Z** | Forward / backward |

Values are in meters per second squared. Gravity always shows up, so whichever axis points up or down sits near 9.8 or -9.8 at rest. Unlike the gyro, the accelerometer does not settle to zero when the controller is still.

A second block, **Aux Accelerometer**, appears when a device carries a second sensor: the Nunchuk's own accelerometer, or the left Joy-Con of a combined pair. Same three axes. It maps as its own source.

---

## Touchpads

PadForge reads two kinds of touch surfaces on the Devices page.

- **Gamepad touchpads.** The touch surfaces on DualShock 4, DualSense, Steam Controller, and Steam Deck. SDL3 reports them as part of the gamepad. They show up in the raw input view with contact position and finger count.
- **Windows Precision Touchpad.** Laptop trackpads and external precision touchpads. PadForge treats each one as its own device card with a live touch preview. These trackpads have no physical click button, so no click input appears for them in the mapping picker or auto-map.

Surface count comes from SDL. Most pads report one. The Steam Controller 2026, the Steam Deck, and the 2015 Steam Controller each report two. A multi-surface device shows a separate live preview per pad, labeled **Touchpad 1** and **Touchpad 2** in the raw input view. The Devices page draws at most those two previews. Every surface still maps.

Pressure maps too. Each finger gets a Touchpad N Finger M Pressure source in the mapping picker, and pads that report a touch as full pressure (DualShock 4, DualSense, Steam Controller 2015) can shape it with the per-device **Enable Synthetic Pressure** option on the [Touchpad](touchpad.md) tab.

A third and fourth source live elsewhere: [Web Controller](../guides/web-controller.md) clients in touchpad-only or DS4-with-touchpad mode, and the on-screen [Touchpad Overlay](dashboard.md#touchpad-overlay). All four feed the same per-slot configuration on the [Touchpad](touchpad.md) tab.

---

## MIDI devices

A connected MIDI keyboard, pad controller, or control surface shows up here as its own device card. Select it and the detail pane shows a live preview: a piano that lights the notes you play and vertical sliders that follow the knobs and faders. Its notes, Control Change knobs, pitch bend, and encoder dials map like any button or axis.

MIDI input needs Windows 11 24H2 (build 26100) or later, the same Windows MIDI Services the MIDI virtual controller uses. See [MIDI Input](midi-input.md) for the full list of what maps.

---

## Consumer Control devices

Media keys show up here as their own device card, typed **Consumer Control**. A keyboard's media row, a standalone media remote, and a headset's media buttons all land here.

![Consumer Control device detail pane with named media chips](../images/devices-consumer.png)

Select the card and the detail pane shows named button chips instead of the numbered-button grid: Play/Pause, Mute, Volume Up, Volume Down, Next Track, Previous Track, and the rest of the media keys the device reports. A chip lights up in cold blue while its key is held.

Each named media key maps as a [source](mappings.md) and works as a [macro](../guides/macros.md) trigger. These devices have no sticks or triggers. **Consume Mapped Inputs** does not apply to them, so that toggle is left out.

---

## NFC readers

A contactless smart-card / NFC reader (PC/SC class, such as an ACR122U) shows up as a device card typed **NFC Reader**.

![NFC Reader detail pane with the Register / Manage NFC Tags button](../images/devices-nfc.png)

The detail pane has a **Register / Manage NFC Tags** button. It opens a dialog where you tap a tag to capture it, then give the tag a name. Each registered tag becomes its own button you can [map](mappings.md), alongside an **Any NFC Tag** button that any tag triggers. The pane lists your named tags and highlights the one you just tapped.

The deep how-to (registering, naming, and mapping tags) lives on [NFC Tags](nfc-tags.md).

---

## Machine and tracker rows

Three rows on this page come from the PC itself or from a program on it, not from a plugged-in device. Each has no HID path, so the Input Mode and Input Hiding sections are left out of its detail pane, and none of them offers **Submit Device Mapping**.

| Row | Type | Where it is turned on | What it carries |
|-----|------|----------------------|-----------------|
| *Your machine* **Hidden Buttons** | Handheld Buttons | **Enable Handheld PC Buttons** in [Settings](settings.md) | One button per paddle or key you have learned, at a stable index. The detail pane lists them by name and lights each one while it is down. A **Learn / Manage Hidden Buttons** button opens the learn dialog. |
| *Your machine* **Motion** | System Motion | The same Settings toggle. Appears only when Windows reports a gyroscope. | The machine's gyroscope and accelerometer as a motion source |
| **Head Tracker (OpenTrack)** | Head Tracker | **Enable Head Tracking Input** on the [Dashboard](dashboard.md) | Six absolute axes, Head Yaw through Head Z, with a status line that says which source is live |

The machine name in the first two rows is the product name the firmware reports, or the family name when the product name is a bare model code. See [Handheld PC Buttons](handheld-buttons.md) and [Head Tracking](head-tracking.md) for setup.

---

## Pairing a controller

The header has a **Pair** button next to **Refresh**. It opens the **Pair a Controller** dialog. A **Controller Family** selector offers three families: **Nintendo Wii**, **Sony DualShock 3**, and **PlayStation Move / Navigation**.

The Wii family walks a Wii Remote, Nunchuk, Classic Controller, or Wii U Pro Controller through Bluetooth pairing. The Windows pairing wizard can't pair these on its own, since their PIN is raw bytes rather than a typed code, so PadForge runs the handshake itself. See [Wii Controllers](../devices/wii-controllers.md) for the pairing steps and the per-controller button layouts.

The DualShock 3 family pairs over USB: connect the controller with a cable, click **Pair**, and PadForge writes this PC into the controller. Unplug it and press the PS button to connect over Bluetooth. See [DualShock 3](../devices/dualshock-3.md).

The PlayStation Move / Navigation family pairs over USB the same way. PadForge writes this PC into the controller, saves the Move's motion calibration, and registers it. Unplug it and press the PS button to connect over Bluetooth.

Once paired, a controller appears as a normal device card here, with the same slot assignment, hiding, and live raw input as any other pad.

---

## Input hiding

When a physical device feeds a [slot](controller-slots.md), games can see both devices and double up the input. PadForge offers two ways to stop that, set per device.

### Hide from Games (HidHide)

Hides the physical device at the OS level using [HidHide](https://github.com/nefarius/HidHide). The device disappears from every non-whitelisted app the moment you toggle the option. PadForge is whitelisted automatically. The setting persists across restarts. Best for gamepads, joysticks, racing wheels, and flight sticks. The toggle is grayed out if HidHide is not installed. Install it from [Driver Management](driver-management.md).

PadForge hides every interface of the device that HidHide can filter, including the XInput node of a controller built into a USB composite device, such as a handheld PC's controller or a pad on the Xbox 360 wireless receiver. An interface that appears on this page as its own connected device, such as a handheld's touchpad, follows its own checkbox. Leave that checkbox off and the interface stays visible while the pad is hidden. An offline card does not count: only a connected row with hiding off keeps its interface out of the pad's hide list.

Hiding is not permanent and does not reach into Windows itself. HidHide blocks only programs that open the device after the entry lands, and only programs that are not on the whitelist. Windows' own drivers keep using a hidden touchpad or keyboard, so the cursor still moves. A game that opened the controller before you hid it keeps it until the controller reconnects. PadForge removes its entries when it exits and puts them back when its engine starts. On a handheld the built-in controller never reconnects, so turn on **Keep Devices Cloaked Between Launches** in [Settings](settings.md) and reboot once to have the controller hidden before any game or launcher can open it.

You can whitelist more apps in [Settings](settings.md) so they can still see hidden devices (streaming overlays, secondary remappers, etc.).

### Consume Mapped Inputs (Hooks)

Suppresses only the specific keys or mouse buttons [mapped](mappings.md) to a virtual controller output. Unmapped keys still type. The cursor still moves. No driver needed. Windows low-level input hooks handle it. The toggle only shows for keyboards and mice.

### Which to use

| Situation | Method |
|----------|--------|
| Xbox / PlayStation / Switch controller | Hide from Games |
| Racing wheel or flight stick | Hide from Games |
| Keyboard with a few keys mapped | Consume Mapped Inputs |
| Mouse with side buttons mapped | Consume Mapped Inputs |
| Hide a keyboard entirely | Hide from Games (read the warnings) |

### Auto-enable defaults

| Device type | Hide from Games | Consume Mapped Inputs |
|-------------|----------------|----------------------|
| Gamepad / Joystick / Wheel / Flight Stick | Auto-enabled (if HidHide is installed) | Not shown |
| Keyboard | Off | Off |
| Mouse | Off | Off |

Keyboards and mice **do not** auto-enable any hiding. Blocking them by accident makes the PC hard to use.

Unassigning a device from every slot clears both hiding options.

### Safety warnings

PadForge shows a confirmation flyout when you turn on hiding for a keyboard, mouse, or Consumer Control device:

- **HidHide on keyboard.** Every app loses keyboard access. "All Keyboards (Merged)" affects every connected keyboard.
- **HidHide on mouse.** Every app outside PadForge loses mouse control. "All Mice (Merged)" affects every connected mouse.
- **HidHide on a Consumer Control device (media keys).** The media collection sits on a physical keyboard, so cloaking it hides that whole keyboard from every app. You get the same keyboard warning.
- **Consume on keyboard.** Mapped keys stop working in other apps while PadForge runs.
- **Consume on mouse.** Mapped buttons (possibly left / right click) are suppressed.

Click **Cancel** to back out or **Proceed** to confirm.

### Master switch

The global **Hide Devices from Games** toggle in [Settings](settings.md) (under HidHide Driver) is the master on / off. With it off, no hiding or suppression runs, no matter what each device is set to. Flipping it back on restores every per-device setting.

---

## Power

Wireless controllers get a **Power** section in the detail pane. It draws when either of its two controls applies to the device: **Idle Disconnect** for any pad PadForge can tell to disconnect, and **Disconnect Bluetooth When Plugged In over USB** for a pad that reports its Bluetooth address as its serial number, which keeps that checkbox on the card while the pad is on a cable.

![Power section with Idle Disconnect timer and battery indicator](../images/devices-power.png)

### Idle Disconnect

Sets how long a controller can sit with no input before PadForge tells it to disconnect. The controller sleeps and saves battery. The value is in minutes, and the suffix reads **minutes (0 = never)**. Set it to 0 to leave the controller on.

Idle Disconnect drops the Bluetooth link. Over a USB cable there's no radio link to drop, so nothing happens. Charging doesn't hold it off. Dropping Bluetooth doesn't interrupt the charge, so an idle pad left on a charger still disconnects. It targets any Bluetooth-linked pad (Sony, gen-1 Switch Pro and Joy-Cons, Wii Remote, and the rest), Xbox controllers on the XInput driver, the Switch 2 family, and the combined gen-1 Joy-Con pair, where PadForge drops both halves' links. A pad reaching this PC through [Remote Link](../guides/remote-link.md) is excluded. This machine holds no radio link to it.

### Quick Charge

A Bluetooth pad that you plug in to charge keeps its radio link up, and the radio keeps drawing from the battery you are trying to fill. **Disconnect Bluetooth When Plugged In over USB** drops that link the moment the pad reports it is charging. Off by default, saved per device.

<!-- SCREENSHOT: devices-quick-charge -->
![Power section with the Disconnect Bluetooth When Plugged In over USB checkbox](../images/devices-quick-charge.png)

The trigger is the pad's own charging report, read from SDL's battery state about once a second. Any power source that makes the pad report charging counts, a PC port and a wall charger alike. The drop fires once, on the change from not charging to charging:

| Situation | What happens |
|-----------|--------------|
| Pad is on Bluetooth, cable goes in | The Bluetooth link is dropped. On a PC port the pad carries on over USB. On a wall charger it goes quiet and charges. |
| You re-pair Bluetooth while the cable stays in | Left alone. The pad already reads charging, so there is no change to act on until the next unplug. |
| You turn the checkbox on while already plugged in | Nothing until the next unplug and replug. |
| PadForge starts with the cable already in | Nothing. The first reading only seeds the check. |

A Sony pad reports the same Bluetooth address as its serial number over both links, so PadForge holds one device card for it, and a cable rebinds that card to the USB path. That is why the checkbox stays on the card while the pad is wired, and why the drop can still find the radio link: it is addressed by that serial. A pad that was never paired makes that a lookup that finds nothing.

The checkbox appears for any pad Idle Disconnect can target, plus any device whose serial number parses as a nonzero Bluetooth address. In a diagnostics log every outcome prints a `QUICKCHARGE` line, so a silent log means the charging change never arrived or the checkbox was off.

---

## Force Raw Joystick Mode

By default, PadForge uses SDL3's gamepad layer for known gamepads. SDL3 translates raw button and axis indices into a standard layout (A/B/X/Y, LX/LY, LT/RT) via a built-in controller database.

**Force Raw Joystick Mode** skips that translation and reads raw hardware indices straight, the same values Windows Game Controllers (joy.cpl) shows.

### Turn it on when

| Symptom | Why |
|---------|-------------|
| Buttons map to the wrong outputs | SDL3's mapping does not match the device |
| Some buttons read no input | SDL3 ate the button and sent it to a slot that does not match |
| Extra buttons go missing | The mapping consumed physical buttons, so they never surface in gamepad mode |
| Works in joy.cpl but not PadForge | SDL3 mapping is wrong |
| Off-brand or niche gamepads | Budget controllers, retro adapters, arcade sticks often have wrong database entries |
| DsHidMini SDF mode | DualShock 3 via SDF needs raw mode. SDL3 drops some buttons. |

### How to turn it on

1. Select the device card
2. In the detail pane, find the **Input Mode** section (gamepad-type devices only. The section is hidden for sources with no Windows HID path: web controller clients, the touchpad overlay, MIDI devices, NFC readers, microphones, the Hidden Buttons, System Motion, and Head Tracker rows, and pads reaching this PC over Remote Link.)
3. Check **Force Raw Joystick Mode (Bypass Gamepad Remapping)**
4. Saved right away. Persists across restarts.

### What changes

- Axis count can change. The raw layer often exposes more axes than the six the gamepad layer reports. Rows stay labeled Axis 0, Axis 1, and so on in both modes.
- Button count can rise. Raw mode exposes every physical button, including any the gamepad layer folded away. Circles stay labeled by number in both modes.
- Auto-mapping is off. Record each [mapping](mappings.md) by hand from the Record button.
- The raw input display updates right away

### When not to use it

If the controller works fine in gamepad mode, raw mode gains you nothing. Gamepad mode gives you friendly names and a default mapping.

The toggle only shows for devices SDL3 recognizes as gamepads. Devices already running as raw joysticks (flight sticks, wheels, generic HID) always use raw indices.

---

## Reconnection and GUID persistence

PadForge identifies devices with deterministic GUIDs so they survive reboots, re-plugs, and port changes.

### How the GUID is built

| Priority | Source | Stability |
|----------|--------|-----------|
| 1 | **Serial number** (e.g., Bluetooth MAC address) | Stable across reboots, re-pairing, and port changes |
| 2 | **Device path** | Stable for the same USB port. Changes if you switch ports. |
| 3 | **SDL instance ID** + VID:PID | Can change on every reconnect |

### What that means

- **Bluetooth controllers** (DualSense, DualShock 4, Switch Pro). GUID stays the same across reboots and re-pairs. Settings stick.
- **Wired USB controllers.** GUID stays the same on the same USB port. A different port makes a new GUID. The old settings stay on the offline (gray) card.
- **[Profiles](../guides/profiles.md).** A profile falls back to VID:PID. If a profile was saved with a device that now has a different identity (a port change, for example), PadForge matches by VID:PID so the profile still applies.

### Offline device cards

Disconnected devices stay in the list with an unlit status flame.

- Every mapping, slot assignment, and setting is kept
- Reconnect with the same GUID and everything comes back
- Remove with the X button if you no longer need it (a **Remove Device** confirmation asks first)
- Offline cards cost nothing at runtime. Stored settings only.

---

## Stick calibration

### Center offset

Fixes center drift: a stick that does not rest in the middle.

1. Go to the **Sticks** tab on the controller's config page (see [Stick Deadzones](stick-deadzones.md))
2. Click **Calibrate Center** while the stick is at rest (do not touch it)
3. PadForge samples hardware values for ~500 ms and calculates the offset

The offset is applied before deadzone processing, which keeps the deadzone circle centered on the real rest position.

### Max range

Sets the maximum physical travel (0-100%) that maps to full output. If the stick cannot reach the corners, lower the max range so full output is reachable within the stick's actual travel.

---

## Troubleshooting

### Device does not appear

- Click **Refresh** to re-scan
- Confirm the device shows up in Device Manager or joy.cpl
- For Bluetooth controllers, check pairing in Windows Bluetooth settings
- For a Wii controller, pair it with the header **Pair** button, not Windows Bluetooth settings. See [Wii Controllers](../devices/wii-controllers.md).
- PadForge filters out its own [virtual controllers](controller-slots.md) (HIDMaestro outputs) on purpose
- Some devices need a manufacturer driver

### Device appears but shows no input

- Check the raw input section. Are axes, buttons, and POVs drawn?
- If they show but never change, try **Force Raw Joystick Mode**
- For Bluetooth devices, confirm a stable connection (lit status flame)

### Buttons missing or mapped wrong

- Turn on **Force Raw Joystick Mode (Bypass Gamepad Remapping)** to skip SDL3's mapping
- Compare PadForge's raw input view with joy.cpl
- For an unmapped joystick-type device, click **Submit Device Mapping** to contribute a mapping

### Double input in games

- Turn on **Hide from Games (HidHide)** on the device, or **Consume Mapped Inputs (Hooks)** for keyboards and mice
- Confirm the master **Hide Devices from Games** toggle in [Settings](settings.md) is on
- Confirm HidHide is installed via [Driver Management](driver-management.md)

### Settings lost after reconnecting

- A wired controller on a different USB port gets a new GUID. Old settings stay on the offline (gray) card. Plug back into the original port, or reconfigure on the new card.
- Bluetooth controllers keep their GUID via MAC address. Settings persist.

### Center drift after calibration

- Make sure the stick was completely at rest during calibration
- For bad drift, the stick may be worn out. Raise the [deadzone](stick-deadzones.md) on the Sticks tab to cover it.

### HidHide toggle grayed out or missing

- **Grayed out**: HidHide is not installed. Install via [Driver Management](driver-management.md) and restart PadForge.
- **Missing**: the device has no Windows HID path to hide (web controller clients, the touchpad overlay, MIDI devices, NFC readers, microphones, the Hidden Buttons, System Motion, and Head Tracker rows, pads reaching this PC over Remote Link). HidHide cannot cloak what is not a HID device, so the section is left out instead of shown disabled.

---

## Related pages

- [Controller Slots](controller-slots.md): create slots before assigning devices.
- [Wii Controllers](../devices/wii-controllers.md): pair a Wii Remote, Nunchuk, Classic Controller, or Wii U Pro Controller from the header Pair button.
- [DualShock 3](../devices/dualshock-3.md): pair a DualShock 3 over USB from the same Pair button.
- [Button and Axis Mappings](mappings.md): map inputs after assigning a device.
- [Stick Deadzones](stick-deadzones.md): calibrate center offset and deadzones.
- [Macros](../guides/macros.md): automated actions triggered by device inputs.
- [Force Feedback](force-feedback.md): device rumble and haptic capabilities.
- [MIDI Input](midi-input.md): map a MIDI keyboard or control surface that appears here.
- [NFC Tags](nfc-tags.md): register, name, and map tags read by an NFC Reader device.
- [Handheld PC Buttons](handheld-buttons.md): learn the paddles and keys behind the Hidden Buttons row.
- [Head Tracking](head-tracking.md): set up OpenTrack for the Head Tracker row.
- [DSU Motion Server](../reference/dsu-motion-server.md): Gyro and accel data for motion-enabled emulators.
- [Profiles](../guides/profiles.md): device connections persist across profile switches.
- [Dashboard](dashboard.md): connected device counts at a glance.
- [Settings](settings.md): master device hiding toggle.
- [Driver Management](driver-management.md): HIDMaestro and HidHide driver installation.
- [Troubleshooting](../troubleshooting.md): general troubleshooting guide.

---

*Last updated for PadForge 4.4.0.*
