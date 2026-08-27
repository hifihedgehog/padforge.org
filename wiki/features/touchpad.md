# Touchpad

*Per-slot touchpad tuning: continuous output modes (relative mouse, absolute pointer, virtual analog stick, D-pad), synthetic pressure, swipe haptics, and the gesture stack (swipes, taps, longpress, pinch, rotate, shape templates). One physical touchpad in two slots carries two independent configurations.*

![Touchpad tab](../images/pad-touchpad.png)

The **Touchpad** tab appears on any slot whose assigned device exposes a touchpad surface: DualSense, DualSense Edge, DualShock 4, Steam Controller (2015 and 2026), Steam Deck, a [Web Controller](../guides/web-controller.md) client in DS4 or touchpad-only mode, the on-screen [Touchpad Overlay](dashboard.md#touchpad-overlay), or a Windows Precision Touchpad enumerated through the [Devices](devices.md) page.

---

## What lives on this tab

Eight cards, top to bottom:

1. **Stick / D-Pad Output.** Turn a touchpad finger into a virtual analog stick (anchor-relative) and/or a wedge-thresholded D-pad.
2. **Mouse Output.** Sensitivity, invert, jitter reduction, momentum, and the pointer response curve for touchpad-finger → mouse X/Y on a Keyboard / Mouse virtual controller.
3. **Absolute Pointer.** The screen region the Touchpad Pointer sources map onto, which warp the cursor to where your finger sits on the pad.
4. **Synthetic Pressure.** DualShock 2 / DualShock 3-style pressure simulation for pads that report a touch as full pressure.
5. **Swipe Haptics.** A haptic tick each time the finger travels a set distance, like Steam Input's trackpad ticks. Shown only for pads PadForge can pulse.
6. **Gesture Detection.** Master enable, recognize mode (in-box / custom / both), and cooldown between fires.
7. **In-Box Gestures.** Swipes (4-way / 8-way), radial zones, taps, longpress, two-finger swipes, pinch / spread, rotate, three / four / five finger gestures, in-box shape templates.
8. **Custom Gestures.** The profile's saved custom shape templates plus a recorder dialog to capture new ones.

The first three are continuous output modes you bind in the [Button and Axis Mappings](mappings.md) table. Synthetic Pressure reshapes the device's existing Pressure sources rather than adding new ones, and Swipe Haptics is feedback with nothing to bind. The last three drive a per-tick gesture engine whose fires you bind the same way.

On a multi-pad device (Steam Controller, Steam Deck) a **Touchpad Number** selector sits at the top of the tab. Every setting here is kept per touchpad, so each pad carries its own gestures, mouse feel and pointer region, and the selector picks which pad the cards edit. Single-pad devices skip the selector. Synthetic Pressure is the one exception: it is stored per device and ignores the selector.

> **Defaults are off.** Every output mode and gesture toggle starts disabled. Open the tab, flip the master switch, then enable each gesture or output you actually want. Numeric thresholds (cooldown, swipe distance, tap time window, longpress duration, deadzones) keep tuned defaults so a feature works correctly the moment it's turned on. The one on-by-default checkbox is Jitter Reduction on the Mouse Output card, which only shapes motion you've already mapped.

---

## Stick / D-Pad Output

Anchors where your finger first lands. Current position relative to that anchor drives the virtual stick X/Y and (optionally) latched D-pad directions.

| Knob | Default | Effect |
|---|---|---|
| Enable Stick / D-Pad Output | off | Adds **Touchpad Stick X**, **Touchpad Stick Y**, and the four **Touchpad D-Pad Up / Down / Left / Right** entries to the mapping picker. |
| Max Radius | 30% | Distance from anchor (as a fraction of the pad) at which stick output saturates to ±1, 5–50%. Smaller means twitchier, larger means more travel. At 30%, moving the finger 30% of the pad width from where it landed gives full deflection. |
| Inner Deadzone | 2% | Magnitude below this maps stick output to (0, 0), 0–10%. Prevents sub-millimeter finger drift from registering as slow stick input. |
| D-Pad Mode | 4-Way | `Off` skips D-pad output. `4-Way` emits one cardinal at a time (90° wedges). `8-Way` emits two cardinals on diagonals (matches physical D-pads reporting NE / NW / SE / SW). |
| D-Pad Activation | 15% | Minimum distance from anchor for any D-pad direction to fire, 5–50%. Independent of the stick inner deadzone so the tactile D-pad snap dials separately from analog feel. |

Bind **Touchpad Stick X** to a virtual stick X axis to use the surface as a thumbstick. Bind **Touchpad D-Pad Up** to a face button to use it as a tap-pad.

On single-pad controllers (DualSense, DualShock 4) the picker shows these labels with no pad number. A device with more than one pad (Steam Controller, Steam Deck) prefixes each entry with its pad number, for example **Touchpad 1: Stick X**. Pad and finger numbers are 1-based everywhere you see them, and a mapping row's source chip renders the same name as its picker entry, including on imported rows with no device assigned.

---

## Mouse Output

Tunes cursor speed and feel when a touchpad finger is mapped to mouse X/Y on a Keyboard / Mouse virtual controller.

| Knob | Default | Effect |
|---|---|---|
| Mouse Sensitivity X | 1.00 | Multiplier on horizontal touchpad → mouse delta, 0.05–10. 1.0 is the calibrated baseline (a full horizontal pad sweep moves the cursor ~1920 pixels). Below 1.0 = slower cursor, above 1.0 = faster. |
| Mouse Sensitivity Y | 1.00 | Same for vertical motion. |
| Invert Mouse X | off | Finger right moves the cursor left. |
| Invert Mouse Y | off | Finger down moves the cursor up. |
| Jitter Reduction | on | Bends motion below a threshold down a power curve instead of cutting it off, so resting-hand tremor is damped while tiny deliberate movements still register. A deadzone would delete the small motion outright. |
| Momentum | off | The cursor keeps traveling after you lift your finger and coasts to a stop, like a trackball. Flicking across the pad covers ground a finger-length swipe cannot. |
| Response | Simple | How finger speed becomes cursor speed. `Simple` is a flat gain plus the Acceleration knob below. `Trackpad` is the pointer-acceleration curve ported from libinput's touchpad profile, and it also moves the cursor slower than the finger at low speed, which is where a laptop trackpad's fine positioning comes from. |
| Speed Threshold | 130 | Trackpad response only. Finger speed in mm/s where the cursor starts speeding up, 20–600. Lower accelerates sooner. libinput's own default and its single exposed tunable. |
| Pad Width | 69 | Trackpad response only. Physical width of this touchpad in mm, 20–150. Decides whether slow movement can reach the fine-control range at all, so set it near the real size of the pad. |
| Acceleration | 0.00 | Simple response only. Fast drags cover more screen than slow ones over the same distance, 0–5. 0 keeps the cursor speed flat. |
| Momentum Glide | 0.90 | How far the cursor coasts, 0.80–1.00. At 1.00 the coast is frictionless: the cursor keeps its speed until you touch the pad again, like a spun trackball. Time-based, so the glide lasts the same at any polling rate. Editable only while Momentum is on. |
| Fling Boost | 1.00 | Scales how fast a fling launches without changing drag speed, 0.1–5. The sensitivity sliders scale dragging and coasting together, so this is the knob that makes a flick travel further on its own. 1.00 launches at exactly the speed the finger was moving. Momentum only. |
| Fling Threshold | 0.29 | How fast the finger must be moving at lift-off for the cursor to coast, in pad widths per second, 0–2. Below it the cursor stops dead. The default is the Steam Controller driver's own minimum lift velocity, which is what shipped before this knob existed. Momentum only. |
| Max Fling Speed | 0 (off) | Caps how fast a fling can launch, in pad widths per second, 0–30. A quick flick measures around 25. 0 turns the cap off. Momentum only. |
| Stack Flings | off | Each new swipe adds to the momentum already rolling instead of replacing it, so repeated swipes build speed. A tap or a still lift stops everything, which keeps tap-to-stop working. Speed is capped by Max Fling Speed, or a built-in ceiling when the cap is off. Momentum only. |

![The touchpad momentum controls](../images/pad-touchpad-momentum.png)

The same coasting is available on a stick, but only on the **Keyboard + Mouse** slot's mouse stick, which carries its own **Momentum** and **Momentum Glide** so a flick of the stick sends the cursor traveling on the same constant-deceleration physics. A gamepad slot's sticks have no momentum row.

![Stick momentum on the Keyboard and Mouse slot](../images/pad-sticks-momentum.png)

The Speed Threshold and Pad Width rows appear only in `Trackpad` response, the Acceleration row only in `Simple`. They are competing models of the same thing, so the card never shows both at once.

Two plain limitations. First, at the default 69 mm Pad Width (libinput's assumed size for a pad that reports no physical dimensions) a DualShock 4 pad cannot report motion slow enough to reach the curve's fine-control half, so it only ever accelerates. Lowering Pad Width below roughly 54 mm brings the fine-control range within reach. No manufacturer publishes the pad's true size, so this is a calibration you make by feel. Second, the Simple-mode Acceleration slider is the value Steam Workshop imports used to write invisibly: Steam's mouse acceleration landed in the mapping data with no card showing it, so an imported pad felt accelerated with nothing on screen to turn off. It is now a visible knob.

Bind **Touchpad 1 Finger 1 X** to KBM Mouse X (and **Touchpad 1 Finger 1 Y** to Mouse Y) to use the surface as a trackpad. Finger entries stay 1-based in the picker, so the first contact is Finger 1. The KBM virtual controller produces real Windows mouse input. The cursor moves in whatever app has focus, games and desktop apps alike.

---

## Absolute Pointer

The Mouse Output sources above move the cursor relatively, like a laptop touchpad. The **Touchpad 1 Pointer X** and **Touchpad 1 Pointer Y** sources are the absolute alternative: the cursor warps to wherever your finger sits on the pad, the way Steam Input's absolute pointer works. Bind them to Mouse X and Y on a Keyboard / Mouse virtual controller the same way.

- Touch the pad and the cursor jumps to the matching spot on the primary monitor. Slide and it follows 1:1.
- Lift the finger and the cursor stays where it was.
- Devices with a single touchpad (a DualShock 4 or DualSense, for example) also offer **Touchpad 1 Pointer X (Left Half)** and **(Right Half)** variants (and the same pair on Y) that read one half of the pad as the whole surface. A device with two pads already has a real pad per half, so it skips these.
- A row that mixes a pointer source with relative sources (gyro, stick) keeps the relative aim live while no finger is down. The moment a finger lands, the pointer takes over.

The card tunes the screen region the pad maps onto. At the defaults the pad covers the whole primary monitor 1:1.

| Knob | Default | Effect |
|---|---|---|
| Region Width | 1.00 | Width of the screen area this pad maps onto, as a fraction of screen width, 0.05–3.00. 1.00 covers the full width. 0.50 confines the cursor to half the screen. Above 1.00 the region runs wider than the screen, so the cursor reaches the edges before your finger reaches the pad bezel. |
| Region Height | 1.00 | Height of the screen area, as a fraction of screen height. |
| Region Center X | 0.50 | Horizontal placement of that area, 0.00–1.00. 0.00 is the left edge, 0.50 the middle, 1.00 the right edge. |
| Region Center Y | 0.50 | Vertical placement, 0.00–1.00. 0.00 is the top edge, 1.00 the bottom edge. |

Steam Workshop configs that use mouse regions arrive on these sources with the region's position and size carried over, so an imported corner region (a pad mapped to a minimap or a menu strip) shows up here and stays editable. The first edit on this card hands the region to this pad's own settings for good: from then on, Reset restores the full-screen defaults instead of silently bringing the imported rectangle back. See [Steam Workshop Config Import](../guides/steam-workshop-import.md).

---

## Synthetic Pressure

Simulates DualShock 2 / DualShock 3 pressure buttons on pads whose hardware reports a touch as full pressure: DualShock 4, DualSense, and the 2015 Steam Controller.

| Knob | Default | Effect |
|---|---|---|
| Enable Synthetic Pressure | off | Shapes this device's Pressure mapping sources into three steps: no touch reads 0%, a resting touch reads the Touch Pressure Level, and clicking the pad reads 100%. Off keeps raw readings on pads with true analog pressure. |
| Touch Pressure Level | 50% | How much pressure a resting (unclicked) touch reports, 0–100%. 50% leaves an even step up to a full pad click. |

The card is stored per device, not per pad, so the Touchpad Number selector on multi-pad devices does not pivot it. Like every per-device setting, it follows the (slot, device) pair: the same DualSense in two slots carries two independent Synthetic Pressure configurations.

---

## Swipe Haptics

Pulses the controller's haptics as your finger travels across this touchpad, like Steam Input's trackpad ticks. Steam Controllers and the Steam Deck tick the actuator under the pad. DualSense and DualShock 4 pulse the rumble motors in a short burst, and game rumble always wins when it is stronger.

| Knob | Default | Effect |
|---|---|---|
| Enable Swipe Haptics | off | Fires a short haptic tick each time the finger moves a set distance on this pad. Landing a finger or clicking the pad never ticks. |
| Pulse Intensity | 50% | Strength of each tick, 5–100%. |

The card appears only when the selected device has a haptic lane PadForge can pulse: Steam Controller (2015 and 2026), Steam Deck, DualSense, DualSense Edge, and DualShock 4. Laptop trackpads, the on-screen overlay, and web touchpads have nothing to pulse, so the card stays hidden for them.

One honest note: the Steam Deck's left/right tick codes are inferred from the 2015 Steam Controller library and have not been hardware-benched, so the worst case on a Deck is a swapped side.

---

## Gesture Detection

Master controls for the per-tick gesture recognizer.

| Knob | Default | Effect |
|---|---|---|
| Enable Gestures on This Touchpad | off | Master switch. Off skips the recognizer entirely for this slot. |
| Recognize | Both | `In-Box Only` runs the built-in catalog (swipes / taps / longpress / pinch / rotate / in-box shapes). `Custom Only` runs only the profile's saved custom shape templates. `Both` runs everything. |
| Cooldown | 100 ms | Minimum time between consecutive gesture fires from this pad. Prevents bounce-fire when a quick reverse motion would otherwise re-fire the opposite-direction swipe immediately. |

---

## In-Box Gestures

Every toggle here is off by default. Flip the ones you want. Gating is three levels, and all three have to pass before a gesture's entries appear in the mapping picker: **Enable Gestures on This Touchpad** (Gesture Detection card above), a **Recognize** setting that includes the in-box catalog (`In-Box Only` or `Both`), and the gesture's own category toggle. A family is never gated on another family's checkbox.

**Touch spots.** Held buttons for where the pad is being touched: **Left Touch**, **Right Touch**, **Top Touch**, and **Multitouch**. One finger lands in Left, Right, or Top (the top quarter). Two or more fingers hold Multitouch. The left/right split sits at two fifths of the width, the same boundary DS4Windows uses, and exactly one spot is held at a time. The mapped button holds while the finger stays in the zone, releases the moment it lifts, and hands over live when the finger slides across a boundary. Bind them like any button: touchpad left to A, right to B, top to C.

**Tier 1: single-finger fires.** 4-way swipes (Up/Down/Left/Right) and 8-way diagonals (NE/NW/SE/SW). Radial zones (4 / 6 / 8 / 12 sectors with a configurable center dead-zone). Tap, double-tap, triple-tap (with a configurable inter-tap gap). Long-press (configurable hold duration).

**Tier 2: multi-finger.** Two-finger swipes (with angular-tolerance gate to distinguish from pinch / spread). Pinch / spread (relative-distance threshold). Rotate (degrees-of-rotation threshold). Three / four / five-finger gestures on devices that support multi-touch deep enough. Windows PTP carries all five.

**Tier 3: shape templates.** Five built-in shapes (Circle, Square, Triangle, Z, Checkmark). Circle ships with separate clockwise and counter-clockwise bindings so the two directions can drive different mappings. The matcher is scale and position invariant, so a small square in the corner matches the same shape as a large one in the center. Orientation still counts. A square tilted into a diamond, or a Z drawn upside down, reads as a different shape. An adjustable threshold tunes strictness. Lower means fewer false positives, higher means more matches.

Each gesture appears as an entry in the mapping picker. Bind **Swipe Up** to a button to fire on swipe, **Two-Finger Pinch / Spread Axis** to an analog axis to read the continuous pinch magnitude, and so on. On a multi-pad device each entry carries its pad number, for example **Touchpad 1: Swipe Up**.

**Macros.** Every enabled gesture (in-box and custom) is also a macro trigger. In the macro editor's Trigger panel, pick it from the **Add from List** dropdown next to the Record button. The dropdown lists buttons, POV directions, stick and trigger axes, the touchpad click, and whatever gestures are enabled on this tab. Recording deliberately does not capture gestures for macro triggers, so a stray swipe can't overwrite the combo, and re-recording keeps any gesture entries you picked. Gesture triggers work with every trigger mode, including On Release. Mapping rows are the opposite: their Record button does detect an enabled gesture performed while recording, so you can bind a touch spot or swipe without opening the dropdown. The recorder decides when the fingers lift: a swipe, tap, shape, or zone beats a touch spot crossed on the way, and a plain touch-and-lift records the last spot held. Multi-stage gestures (Double Tap, Triple Tap) record as their first stage, so pick those from the dropdown instead.

---

## Custom Gestures

Profile-scoped: captured custom gestures travel with whichever profile is active when they're recorded. Each gesture has a name, finger count, and the recorded finger path(s).

Click **+ Record New Gesture** to open the recorder dialog. The dialog mirrors the live touchpad surface. Trace the gesture once per sample: the **Samples to Capture** dropdown offers 1, 3, or 5, and defaults to 3. The hint under it says it straight: "3 is the standard. More samples = sturdier match, fewer = faster recording." A counter tracks progress, and when the last sample lands the status line reads "All samples captured. Name the gesture and click Save." Name it, click **Save**, and the samples are averaged into one template. Drawing a different finger count from the previous samples clears the stack and starts over. The new gesture appears in the list and shows up in the mapping picker under the name you gave it.

A touchpad-only device (laptop trackpad, web touchpad client, overlay) that isn't currently selected as the active mapping device still drives the recorder, so you can capture a gesture on the touchpad while the slot's primary device is something else.

---

## Two slots on one touchpad

The same physical touchpad assigned to two slots carries two independent gesture engines. Each slot runs the recognizer with its own settings, and each slot's mapping rows see only that slot's fires.

Practical consequence: if you assign a DualSense to slot 0 with 4-way swipes on and to slot 1 with 4-way swipes off, a horizontal swipe fires **Swipe Right** only on slot 0's mapping rows. Slot 1's toggle truly disables 4-way for slot 1. It does not inherit slot 0's behavior. The same per-slot scoping applies to every Stick / D-Pad / Mouse setting on this tab.

Laptop trackpads (Windows Precision Touchpads on the [Devices](devices.md) page) arrive as a system touchpad with no controller behind them, so they carry no touchpad-click button. **Touchpad Click** is left out of their picker entries and their auto-map. DualSense, DualShock 4, web touchpad, and overlay devices report a click of their own and expose it.

---

## Reset buttons

Every setting row carries a per-field **Reset** button (the small reset arrow on the right). Each setting card carries a **Reset All** button in its header that restores the card's defaults in one click.

---

## Credits

Shape matching runs two open-source gesture recognizers on every single-finger shape and keeps whichever one recognizes the stroke (both BSD 3-Clause). The Mouse Output card's Trackpad response is an original C# re-derivation of libinput's touchpad acceleration profile (MIT). Full credits, copyright, and license text are on the in-app **About** page and in the project README.

---

## See also

- [Button and Axis Mappings](mappings.md) for binding touchpad entries to virtual outputs.
- [Virtual Controllers](virtual-controllers.md) for which output types accept touchpad-finger-as-mouse / stick / D-pad.
- [Menus](../guides/menus.md) for hosting an on-screen radial or touch menu on a touchpad.
- [Web Controller](../guides/web-controller.md) for using a phone screen as a touchpad source.
- [Dashboard](dashboard.md) for the [Touchpad Overlay](dashboard.md#touchpad-overlay) (transparent on-screen touchpad surface).
- [Devices](devices.md) for enumerating a laptop trackpad as a touchpad source.

---

*Last updated for PadForge 4.3.2.*
