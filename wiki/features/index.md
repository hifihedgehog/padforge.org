# Features

*The reference for every page, section and card in the app: each control, what it
does, and what its numbers mean.*

Where a guide walks one task, these pages document every control you can
touch.

## The app, page by page

The sidebar holds Home, Devices, Profiles and Extras, then one entry for each
virtual controller and **Add Controller**, with Settings and About at its foot.

| Page | Covers |
| --- | --- |
| [Home](dashboard.md) | The engine, the offer for a device nothing uses, the virtual controllers and the extras that are on |
| [Devices](devices.md) | Every detected input device and its capabilities |
| [Controller Slots](controller-slots.md) | The 16 controllers, Add a Controller, the type chip and assignment |
| [Virtual Controllers](virtual-controllers.md) | What games see: Xbox, PlayStation, Nintendo, Extended, Keyboard + Mouse, MIDI, VR |
| [Settings](settings.md) | Application-wide options |
| [Updates](updates.md) | The Updates card on the **Settings** page: automatic checks, one-click installs, and pre-releases |
| [Driver Management](driver-management.md) | The driver cards on the **Settings** page: HIDMaestro status and version, **Install** and **Uninstall** for HidHide, SteamVR and the Windows MIDI Services runtime, and the MIDI API in use. Also **Use Only in PadForge**, which takes a USB keyboard, a USB mouse or a precision touchpad away from Windows |

Profiles have their own guide, [Per-game Profiles](../guides/profiles.md). The
Extras page is a catalog of the optional features, and each one has its page
under [Beyond the controller page](#beyond-the-controller-page).

## The controller page, section by section

A controller's page has a header (its name, its type chip and the devices that
drive it under **Driven by**) and up to six sections. A section shows only
while something in it applies to the controller and the device selected under
**Driven by**. A controller with no gyro, touchpad or pointer has no
**Motion & Touch**.

### Mappings

The first section is named **Mappings** on a gamepad controller, **Keys & Mouse**
on a Keyboard + Mouse controller, **Notes & Controls** on a MIDI controller and
**Hands** on a VR controller. It has two views of one mapping table, **Picture**
and **List**.

| Part | Covers |
| --- | --- |
| [Picture](visualization.md) | The live 2D and 3D controller view. Click a control, then press the input that should drive it |
| [List](mappings.md) | Every mapping row: sources, combine modes, per-source options |
| Output | SOCD cleaning and Keep Controller Awake, the two cards under the picture that shape the output right before it reaches the game. Hidden on MIDI and VR controllers. SOCD is documented on [Mappings](mappings.md) |

### Sticks & Triggers

| Card | Covers |
| --- | --- |
| [Sticks](stick-deadzones.md) | Dead zones, shapes, response curves, max range |
| [Triggers](trigger-deadzones.md) | Trigger travel, dead zones, curves |
| Mouse Gestures | Flick gestures on a physical mouse: hold the gesture button, flick, one action fires on release. No feature page yet |

### Rumble & Haptics

| Card | Covers |
| --- | --- |
| [Force Feedback](force-feedback.md) | Rumble routing and strength |
| [Impulse Triggers](impulse-triggers.md) | Xbox One and Series trigger motors |
| [Adaptive Triggers](adaptive-triggers.md) | DualSense trigger effects |
| [Wheel](wheel.md) | Rotation range, auto-center, and shift LEDs on force feedback wheels |
| [Centering](wheel-centering.md) | What brings a force feedback wheel back to center: a plain spring, or Vehicle mode's torque from a car's steering at its speed, and the Release Test |
| [Bass Shakers](bass-shakers.md) | Game rumble and force feedback routed to an audio output as low-frequency tones for bass shakers and subwoofers. Shown on Xbox, PlayStation, and Nintendo controllers, and on Extended controllers with force feedback |

### Motion & Touch

| Card | Covers |
| --- | --- |
| [Gyro](../guides/gyro.md) | Motion-sensor mapping: calibration, sensitivity, smoothing, engage gates |
| [Touchpad](touchpad.md) | Gestures, pointer, per-pad mouse feel |
| [IR Pointer](../devices/wii-controllers.md) | Wii Remote IR aiming and cursor modes |

### Lights & Sound

| Card | Covers |
| --- | --- |
| [Lighting](lighting.md) | Light bars, LED rings, player lamps, and per-key colors on keyboards |
| [Screen Color](screen-color.md) | A lighting mode that follows the colors on your screen: one color for a lightbar, or the screen spread across a keyboard's keys |
| [Audio](controller-audio.md) | Controller speakers and headset routing |

### Macros & Menus

| Part | Covers |
| --- | --- |
| [Macros](../guides/macros.md) | Action sequences fired by combos, sticks, or every frame |
| [Menus](../guides/menus.md) | On-screen ring, grid and hotbar menus driven by a stick or touchpad |
| [On-Screen Keyboard](on-screen-keyboard.md) | A menu style that types into any Windows program from a controller: a grid, two split halves or a daisy wheel, opened by any input you pick |

## Beyond the controller page

| Feature | Covers |
| --- | --- |
| [NFC Tags](nfc-tags.md) | Tag registration on the Devices page, taps as macro triggers |
| [Voice Macros](voice-macros.md) | Spoken phrases as buttons: offline recognition on any microphone, the DualSense’s included |
| [Handheld PC Buttons](handheld-buttons.md) | Rear paddles and menu keys on a handheld gaming PC, learned by pressing them, plus the machine's own gyroscope |
| [Flydigi Apex](flydigi-apex.md) | The Flydigi Apex 4, Apex 5 and Apex 6 Pro: trigger effects, rumble, lighting and the controller's screen |
| [MIDI Input](midi-input.md) | MIDI devices on the Devices page: notes, knobs, and pitch bend as mapping sources |
| [Logitech G-Keys](logitech-g-keys.md) | The G-keys and extra mouse buttons on Logitech gaming gear as mapping sources |
| [Analog Keyboards](analog-keyboards.md) | How far every key is pressed on analog and Hall effect keyboards, as mapping sources |
| [Bliss-Box Adapters](bliss-box.md) | Retro controllers in Bliss-Box ports: their button names, DualShock 2 pressure, rumble, the Dreamcast screen and N64 Controller Pak saves |
| [Keyboard Screens](keyboard-screens.md) | The screens on Logitech GamePanel keyboards, the Mad Catz S.T.R.I.K.E. 7 and Logitech Arx Control, and the keys beside them as buttons |
| [Screen Overlay](screen-overlay.md) | A picture, a timer, the time or a lightbar's color shown above other windows on any PC, set on its page in Extras |
| [Crosshair](crosshair.md) | Crosshairs of your own over a game: a cross, a circle, a dot or a picture, set on its page in Extras |
| [Magnifier](magnifier.md) | A zoom lens, a full-screen zoom or a spotlight over a game, set on its page in Extras |
| [Twitch Chat](twitch-chat.md) | The people watching your stream play a controller by typing commands in chat, with the controller shown on stream |
| [Novint Falcon](novint-falcon.md) | The Falcon's handle as a stick, its grip buttons, and a game's rumble and force feedback as force on the handle |
| [Game Mods](game-mods.md) | Adaptive triggers, lightbar, player lights and mute light set by game mods made for DSX |
| [Game Telemetry](game-telemetry.md) | The speed, RPM, gear and pedals driving games send, as a device row, macro triggers and adaptive trigger effects |
| [Input Precision](input-precision.md) | Polling rate, resolution, and latency across the whole pipeline |
| [Virtual VR Controllers](vr-controllers.md) | A SteamVR left and right hand pair driven from one controller |
| [VR Controller Input](vr-controller-input.md) | The headset's pose and both hand controllers read as mapping sources through OpenXR |
| [Headset Head Tracking](headset-motion.md) | Head rotation from a Sony headset as a motion source |
| [Head Tracking (OpenTrack)](head-tracking.md) | A head pose from OpenTrack or FreeTrack as six mappable axes |
| [Mice, Keyboards and Vendor Rows](peripherals.md) | Lighting and rumble for the mice and keyboards assigned to a virtual controller, and the Razer Chroma, Logitech LIGHTSYNC, SteelSeries GG, Razer Sensa, ASUS Aura, MSI Mystic Light and Corsair iCUE rows |

*Last updated for PadForge 6.0.0.*
