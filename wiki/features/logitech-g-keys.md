# Logitech G-Keys

*The G-keys on a Logitech keyboard, and the extra buttons on a Logitech mouse, as a device row you can map and put in macros.*

A G-key is not a keyboard key. It sends nothing until you program it in Logitech's own software, and the usual way to make one useful elsewhere is to have it type some real key, which burns a keycode, fires in every program on the machine, and puts two remappers in series.

PadForge reads the G-keys directly through Logitech's G-key SDK instead. They arrive as their own device row, bind through the same grid every other device uses, and never reach any other program.

---

## Turning it on

Open **Settings**, find the **Input Engine** card, and tick **Read Logitech G-Keys**. It is off by default, because turning it on loads a third-party library and opens a session with the Logitech software.

A **Logitech G-Keys** row then appears on the [Devices](devices.md) page.

### What you need

Logitech Gaming Software 8.55 or later, running. The SDK ships with it, and G HUB does not include it.

Two more steps matter, and both happen in Logitech's software rather than in PadForge.

Give each key the **G-key** command. Once PadForge has run with this setting on, Logitech Gaming Software has a profile for PadForge with a G-key command in its command list. Drag that command onto every G-key and extra mouse button you want PadForge to read. A key without it keeps running whatever Logitech's software has on it and never reaches PadForge.

Then make that profile the **persistent profile**. Logitech Gaming Software lets you nominate one, which keeps receiving G-keys no matter which program is in front. Without it the SDK only feeds whichever program has focus, so your G-keys work in PadForge's own window and nowhere else.

While the PadForge profile is persistent, Logitech Gaming Software ignores every other profile, including the profiles linked to your games, so a game's own G-key assignments stop applying. To clear it, right-click the PadForge profile in the Profiles area and select **Set As Persistent** again to remove the check mark.

A G600 or G300 mouse also has to be out of on-board mode. The SDK reads neither mouse while it is in that mode.

Logitech's profiles are unrelated to PadForge's own [profiles](../guides/profiles.md), which are a different thing that lives on the Profiles page.

---

## Reading the status line

Under the checkbox is a line saying exactly which of seven situations the machine is in, so a quiet G-key is never a mystery.

| Status | What to do |
| --- | --- |
| *No Logitech G-key SDK on this machine. It installs with Logitech Gaming Software 8.55 or later.* | Install Logitech Gaming Software. |
| *The G-key SDK is registered but its file is gone. Reinstall Logitech Gaming Software.* | Reinstall it. |
| *Found the G-key SDK and could not load it.* | Usually an architecture mismatch or a damaged install. |
| *That library is not the G-key SDK this expects.* | Something else is registered under the SDK's key. |
| *The G-key SDK refused to start. Logitech Gaming Software is usually not running.* | Start Logitech Gaming Software. |
| *Connected, no key seen yet. In Logitech Gaming Software, drag the G-key command onto each key in the PadForge profile, and make that profile persistent.* | Do both, then press a G-key. |
| *Running, {0} key events* | Working, with the count in place of `{0}`. It rises as you press keys. |

The line is empty while the feature is off.

---

## What the row exposes

102 buttons, in a fixed layout:

- **G1 through G29, in each of M1, M2 and M3.** 87 buttons. One physical G-key carries three bindings, which is what the M-state keys are for. The row names them *G5 (M2)* and so on.
- **Mouse buttons 6 through 20.** 15 buttons, for the extra buttons on a Logitech mouse.

Every one of the 102 is listed even on a keyboard with six G-keys, because the SDK has no way to report how many a given device has. Finding the right entry is what the **Record** button is for: press it, press the key, and it binds.

While the SDK is not running, PadForge retires the row and opens a fresh one every five seconds to retry it. Both happen in the same pass, so the row stays in the Devices list.

The layout is fixed rather than derived from the attached hardware, so a saved mapping keeps pointing at the same key when you plug in a different Logitech keyboard.

---

## Mapping it

The row binds anywhere a button does, including [macros](../guides/macros.md) and [menus](../guides/menus.md). An **(Any Device)** source never reads it, so pick the G-Keys row by name.

A tap can begin and end between two of PadForge's polls, so a press is held asserted briefly after it arrives. A macro sees the edge either way.

---

## Limitations

This runs against Logitech's own library, and nothing here has been exercised against real Logitech hardware or software. The wire format comes from `LogitechGkeyLib.h` in the SDK, so the decoding is grounded, and the library search and shutdown follow [Mumble](https://github.com/mumble-voip/mumble)'s long-running implementation, but the library loading and calling back on a live machine is unverified.

G-keys need Logitech Gaming Software, and G HUB alone cannot supply them. Logitech has released no G-key SDK for G HUB. Its [developer page](https://www.logitechg.com/en-us/programs/partner-developer-lab) offers a Steering Wheel SDK and an LED Illumination SDK. G HUB 2026.6 installs an LED SDK and lists a wheel SDK and a Trueforce SDK among its packages, and none of them is for G-keys.

---

## Related pages

- [Settings](settings.md): the Input Engine card.
- [Devices](devices.md): the Logitech G-Keys row.
- [Lightbar Mirrors](lightbar-mirrors.md): LIGHTSYNC lighting, the other Logitech SDK PadForge loads.
- [Logitech G-Keys Internals](../reference/logitech-g-keys-internals.md): the event word, the library search, and the lifecycle, for whoever has to change the code.

---

*Last updated for PadForge 5.0.0.*
