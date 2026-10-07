# Haptic Mice

*One Dashboard toggle that plays the rumble games send to PadForge's virtual controllers on mice with a vibration motor: the Logitech MX Master 4 and the SteelSeries Rival 500, 700 and 710.*

---

## Where it lives

The **Haptic Mice** section sits under the Services header on the [Dashboard](dashboard.md), after Razer Sensa HD Haptics and before Overlays. It has one checkbox, **Send Rumble to Haptic Mice**, off by default, with a status line under it. The service runs only while the input engine runs: turning the engine on starts it when the toggle is on, and turning the engine off stops it.

| Status text | Meaning |
|---|---|
| *Sending rumble to MX Master 4* | PadForge found the mouse and plays rumble on it. Each mouse it found is named, and *SteelSeries GG* appears once GG has accepted PadForge's rumble event. |
| *Sending rumble to MX Master 4 (haptic feedback is off in Logi Options+)* | The mouse answers, but its own haptic feedback is turned off, so it plays nothing. Turn haptic feedback on in Logi Options+. |
| *No haptic mouse found. Retrying.* | Nothing answered yet. PadForge looks for a Logitech mouse every 5 seconds and for SteelSeries GG every 15. |
| *Stopped* | The toggle is off or the engine is stopped. |

The footer under the checkbox reads: *The MX Master 4 works over its Logi Bolt receiver or Bluetooth. Rival mice need SteelSeries GG running.*

---

## What feeds it

The same rumble [Razer Sensa HD Haptics](lightbar-mirrors.md#razer-sensa-hd-haptics) reads: the loudest of a slot's four rumble voices (left motor, right motor, left trigger motor, right trigger motor) across every slot, from the game's inbound rumble merged with the live vibration state, so test rumble counts too.

Neither mouse takes a continuous strength, so PadForge turns the rumble into three levels:

| Loudest voice | Level | MX Master 4 | Rival 500, 700 and 710 |
|---|---|---|---|
| Under 5% | Off | Nothing | Nothing |
| 5% to 32% | Light | Subtle collision | A 30 ms pulse 5 times a second |
| 33% to 65% | Medium | Damp collision | A 55 ms pulse 7 times a second |
| 66% and up | Strong | Sharp collision | An 80 ms pulse 10 times a second |

A level falls back only when rumble drops 2 to 3 points below the threshold that raised it, so rumble hovering on a boundary does not flicker between levels.

On the MX Master 4 the waveform repeats every 250 ms at the faintest rumble and every 80 ms at full strength, with the interval shrinking smoothly in between. New rumble plays its first pulse at once. The waveform names are Logitech's own: its Actions SDK calls sharp collision a "High-intensity impact simulation", damp collision a "Medium-intensity impact with gradual decay" and subtle collision "Low-intensity feedback for light contact events". When the mouse does not list a level's waveform, PadForge plays the nearest one it does list.

---

## Logitech MX Master 4

PadForge talks to the mouse in HID++, Logitech's own protocol, the way Solaar and LiveHaptics do. It needs neither Logi Options+ nor a plugin, and it runs beside Options+ when Options+ is installed.

| Needs | Detail |
|---|---|
| Connection | The mouse's Logi Bolt receiver, or Bluetooth. |
| Settings | Haptic feedback turned on in Logi Options+. PadForge never changes the mouse's haptic settings, so the strength set in Options+ scales every pulse. |

PadForge finds any Logitech device that reports the haptic feature, with no model list. Logitech's Actions SDK names the MX Master 4 as the only such device today.

A mouse that goes to sleep stops answering. PadForge checks each mouse every 30 seconds while nothing rumbles, takes one that does not answer off the list, and finds it again within about 15 seconds of waking.

---

## SteelSeries Rival 500, 700 and 710

These vibrate through the GameSense server inside SteelSeries GG. PadForge registers as a GameSense game named PadForge, with one event, RUMBLE, and a tactile handler that plays the pulses in the table above.

| Needs | Detail |
|---|---|
| Software | SteelSeries GG, running. PadForge reads GG's address from its `coreProps.json` file and looks again every 15 seconds while GG is not running. |
| Hardware | A Rival 500, 700 or 710, the mice GameSense drives with tactile alerts. |

The status names *SteelSeries GG* rather than the mouse, since GameSense does not tell a program which mice are connected. PadForge appears in GG under its own name, and its RUMBLE event can be customized there like any GameSense event.

PadForge sends GG a new value only when the level changes, and a keepalive every 10 seconds while rumble holds. When the toggle goes off, it ends its GameSense game, and GG's own effects come back at once.

---

## TouchSense mice

Logitech's iFeel Mouse and iFeel MouseMan, and the other mice built on Immersion's TouchSense, cannot vibrate on 64-bit Windows. Their vibration command is an output report in the mouse's own HID collection, and Windows holds every mouse collection for itself: it refuses an output report from any other program, with or without administrator rights. Only a kernel driver can reach that report, and Logitech never released its TouchSense drivers for 64-bit Windows.

---

## Profiles

The toggle rides the active [profile](../guides/profiles.md) the way the Sensa toggle does.

| Situation | What happens |
|---|---|
| You change the toggle while a named profile is active | That profile records the new value as its opinion. |
| You switch to a profile that has an opinion | The toggle follows it, on or off. |
| You switch to a profile with no opinion | The toggle stays where it is. |
| You change the toggle with no named profile active | Only the global setting changes. |

A profile has no opinion until you give it one, so a profile saved before this feature existed never turns it off behind your back.

---

## Limitations

- The MX Master 4 plays fixed waveforms, not a continuous buzz. Strength shows as which waveform plays and how often.
- Each mouse has one motor, so the left and right motors and the trigger motors merge into one strength, and rumble from every slot merges too.
- No source documents how long each MX Master 4 waveform lasts. The 80 ms floor between pulses is the cooldown the mxhaptics mod ships for its impact events.
- Neither family was verified on the hardware by the maintainer. The MX Master 4 path was built against Solaar, OpenLogi and LiveHaptics, tested against a scripted mouse, and checked against a real Logitech receiver. The Rival path was built against SteelSeries' GameSense documentation and tested against a local stand-in for GG.

---

## Related pages

- [Dashboard](dashboard.md): the page the section lives on.
- [Force Feedback](force-feedback.md): the rumble PadForge sends to the physical controllers.
- [Lightbar Mirrors and Sensa Haptics](lightbar-mirrors.md): the Razer Sensa translation, which reads the same rumble.
- [Profiles](../guides/profiles.md): how per-game profiles record a toggle.
- [Haptic Mice Internals](../reference/mouse-haptics-internals.md): the HID++ frames, the GameSense client and the worker.

---

*Last updated for PadForge 5.0.0.*
