# Bass Shakers

*The Bass Shakers tab routes the game rumble and force feedback a virtual
controller receives to an audio output as low-frequency tones, for bass
shakers and subwoofers.*

<!-- SCREENSHOT: pad-bass-shakers -->
![The Bass Shakers tab with the Rumble to Audio card and its four voices](../images/pad-bass-shakers.png)

The tab is per slot. It works with Xbox, DualShock 4 / DualSense, and
Nintendo Switch Pro virtual controllers, plus Extended virtual controllers
with force feedback, such as racing wheels. Game feedback and Test Rumble play through the audio output. Macro rumble stays on the controller.

---

## Rumble to Audio card

| Control | What it does |
| --- | --- |
| **Route Rumble to an Audio Output** | Plays the game rumble and force feedback this virtual controller receives as low-frequency tones on the selected audio output. Turning it off keeps every setting. |
| **Output Device** | The playback device that receives the rumble tones. System default follows the Windows default playback device. If the selected device disappears, audio stays off until it returns. |
| **Channel Mode** | **Mono (All Channels)** plays every voice on all speaker channels. **Controller Stereo** splits them like the controller: low motor and left trigger on the left channel, high motor and right trigger on the right. |
| **Master Gain** | Overall loudness applied after each voice's own gain. Keep headroom so the four voices do not clip when they play together. |

A status line under the card reads "Audio output is not running." while
the routing is off, "Playing to {device}." while it runs, and warns when
the selected output device is unavailable. Bluetooth audio devices add
noticeable latency, and the card says so.

---

## Voices

Four feedback channels each get their own row: **Low Motor**,
**High Motor**, **Left Trigger**, and **Right Trigger**.

| Per-voice control | What it does |
| --- | --- |
| Enable | Plays this feedback channel as a tone. Gain and frequency stay set while it is off. |
| Frequency | Tone frequency for this channel, 20–120 Hz. |
| Gain | Loudness of this channel before master gain. |
| Level meter | Live bar showing what this channel is playing right now. |
| **Test** | Plays this channel's tone for 1.5 seconds at its set gain. |

Default frequencies: 40 Hz low motor, 80 Hz high motor, 60 Hz on both
triggers. Every voice starts enabled at 100% gain. Master Gain starts at
50%.

## Frequency Sweep

**Frequency Sweep** sweeps a tone from 20 to 120 Hz over eight seconds on
the low motor routing. Note where your shaker responds strongest and set
the voice frequencies there. **Stop** ends a running test or sweep.

Every control has a reset button, and the Rumble to Audio card header
carries a **Reset All** for the whole card.

---

## Related pages

- [Force Feedback](force-feedback.md) covers rumble on the physical pad,
  including audio-bass-driven rumble (the opposite direction: audio into
  motors).
- [Controller Audio](controller-audio.md) covers the controller's own
  speaker and haptic-tone audio.

*Last updated for PadForge 4.3.2.*
