# Logitech G-Keys

*The G-keys on a Logitech keyboard, and the extra buttons on a Logitech mouse, as a device row you can map and put in macros.*

A G-key is not a keyboard key. It sends nothing until you program it in Logitech's own software, and the usual way to make one useful elsewhere is to have it type some real key, which burns a keycode, fires in every program on the machine, and puts two remappers in series.

PadForge reads the G-keys directly through Logitech's G-key SDK instead. They arrive as their own device row, bind through the same grid every other device uses, and never reach any other program.

---

## Turning it on

Open **Settings**, find the **Input Engine** card, and tick **Read Logitech G-Keys**. It is off by default, because turning it on loads a third-party library and opens a session with the Logitech software.

A **Logitech G-Keys** row then appears on the [Devices](devices.md) page.

### What you need

Logitech Gaming Software 8.55 or later, running. The SDK ships with it.

One more step matters: in Logitech Gaming Software, set the **PadForge** profile to **Persistent**. Without it, the SDK only feeds whichever program is in the foreground, so your G-keys work in PadForge's own window and nowhere else.

---

## Reading the status line

Under the checkbox is a line saying exactly which of six situations the machine is in, so a quiet G-key is never a mystery.

| Status | What to do |
| --- | --- |
| *No Logitech G-key SDK on this machine. It installs with Logitech Gaming Software 8.55 or later.* | Install Logitech Gaming Software. |
| *The G-key SDK is registered but its file is gone. Reinstall Logitech Gaming Software.* | Reinstall it. |
| *Found the G-key SDK and could not load it.* | Usually an architecture mismatch or a damaged install. |
| *That library is not the G-key SDK this expects.* | Something else is registered under the SDK's key. |
| *The G-key SDK refused to start. Logitech Gaming Software is usually not running.* | Start Logitech Gaming Software. |
| *Connected, no key seen yet. Set the PadForge profile to Persistent in Logitech Gaming Software.* | Do that, then press a G-key. |
| *Running, N key events* | Working. The count rises as you press keys. |

The line is empty while the feature is off.

---

## What the row exposes

102 buttons, in a fixed layout:

- **G1 through G29, in each of M1, M2 and M3.** 87 buttons. One physical G-key carries three bindings, which is what the M-state keys are for. The row names them *G5 (M2)* and so on.
- **Mouse buttons 6 through 20.** 15 buttons, for the extra buttons on a Logitech mouse.

Every one of the 102 is listed even on a keyboard with six G-keys, because the SDK has no way to report how many a given device has. Finding the right entry is what the **Record** button is for: press it, press the key, and it binds.

The layout is fixed rather than derived from the attached hardware, so a saved mapping keeps pointing at the same key when you plug in a different Logitech keyboard.

---

## Mapping it

The row binds anywhere a button does, including [macros](mappings.md) and [menus](mappings.md). An **Any Device** source never reads it, so pick the G-Keys row by name.

A tap can begin and end between two of PadForge's polls, so a press is held asserted briefly after it arrives. A macro sees the edge either way.

---

## Limitations

This runs against Logitech's own library, and nothing here has been exercised against real Logitech hardware or software. The wire format comes from `LogitechGkeyLib.h` in the SDK and was cross-checked against [Mumble](https://github.com/mumble-voip/mumble)'s long-running implementation, so the decoding is grounded, but the library loading and calling back on a live machine is unverified.

G HUB is not Logitech Gaming Software. The G-key SDK ships with Logitech Gaming Software, and a machine running only G HUB may not register it.

---

## Related pages

- [Settings](settings.md): the Input Engine card.
- [Devices](devices.md): the Logitech G-Keys row.
- [Lightbar Mirrors](lightbar-mirrors.md): the other Logitech integration, LIGHTSYNC lighting.
- [Logitech G-Keys Internals](../reference/logitech-g-keys-internals.md): the event word, the library search, and the lifecycle, for whoever has to change the code.

---

*Last updated for PadForge 4.5.0.*
