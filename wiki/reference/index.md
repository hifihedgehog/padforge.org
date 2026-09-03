# Technical Reference

The deep tier. These pages document how PadForge works inside: the
architecture, the polling pipeline, the drivers, and the wire protocols.
Nothing here is required reading for using the app.

## Architecture

| Page | Covers |
| --- | --- |
| [Architecture Overview](architecture-overview.md) | The three projects and how data flows between them |
| [Input Pipeline](input-pipeline.md) | The six-step, 1000 Hz loop from raw input to virtual output |
| [Engine Library](engine-library.md) | PadForge.Engine: the UI-free core |
| [Services Layer](services-layer.md) | The App-side services |
| [ViewModels](viewmodels.md) | The WPF view-model layer |
| [XAML Views](xaml-views.md) | The view layer |
| [Settings and Serialization](settings-and-serialization.md) | PadForge.xml, round-trips, migration |
| [Build and Publish](build-and-publish.md) | Building from source |

## Integrations and drivers

| Page | Covers |
| --- | --- |
| [SDL3 Integration](sdl3-integration.md) | The input backend and the PadForge SDL3 fork |
| [HIDMaestro Deep Dive](hidmaestro-deep-dive.md) | The virtual-controller bus driver |
| [Driver Installation Internals](driver-installation-internals.md) | How install, repair, and removal work |

## Protocols and subsystems

| Page | Covers |
| --- | --- |
| [DSU Motion Server](dsu-motion-server.md) | The Cemuhook motion server |
| [DSU Protocol](dsu-protocol.md) | The wire protocol itself |
| [Remote Link Internals](remote-link-internals.md) | Cross-PC device sharing on the wire |
| [External Control Internals](external-control-internals.md) | The profile control pipe, its command grammar, and the held-profile state |
| [Steam Workshop Import Internals](steam-workshop-import-internals.md) | The VDF parser and config translator |
| [Controller Audio Internals](controller-audio-internals.md) | Speaker and haptic audio paths |
| [Steam Controller Haptics Internals](steam-controller-haptics-internals.md) | The 2026 pad's PCM actuator stream and the tone lane it falls back to |
| [Sensa Haptics Internals](sensa-haptics-internals.md) | Controller rumble as a Razer Sensa HD effect through Interhaptics |
| [Lightbar Mirrors Internals](lightbar-mirrors-internals.md) | A game's lightbar write out to Razer Chroma and Logitech LIGHTSYNC |
| [Virtual VR Controllers Internals](vr-controllers-internals.md) | One slot, a SteamVR hand pair, and the haptic return path |
| [Headset Head Tracking Internals](headset-motion-internals.md) | The descriptor probe and rotation-to-rate synthesis |
| [Head Tracking Internals](head-tracking-internals.md) | The OpenTrack datagram, the FreeTrack heap, and the scaling into six axes |
| [Wheel Force Feedback Internals](wheel-ffb-internals.md) | DirectInput FFB effects |
| [MIDI Input Internals](midi-input-internals.md) | MIDI parsing and routing |
| [Handheld PC Buttons Internals](handheld-buttons-internals.md) | The three delivery paths a hidden button can arrive on, and the learners |
| [Wii Controllers Internals](wii-controllers-internals.md) | Extensions, Motion Plus, IR camera |
| [2D Overlay System](2d-overlay-system.md) | The overlay renderer |
| [3D Model System](3d-model-system.md) | The 3D controller models |

---

*Last updated for PadForge 4.4.0.*
