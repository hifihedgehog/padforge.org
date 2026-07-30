# Macros

*Fire action sequences from controller inputs. Hold a combo, deflect a stick, push the D-pad, or run a macro every frame with no trigger at all.*

![Macros tab showing trigger setup and action list](../images/pad-macros.png)

Each slot has its own macro list. Open a slot, switch to the **Macros** tab, and click **Add**.

---

## Make a macro

1. Open a slot. Click the **Macros** tab.
2. Click **Add** and name the macro.
3. Set a **trigger**. The input combo that fires the macro.
4. Add one or more **actions**. The steps that run when the trigger fires.
5. Pick a **fire mode** and a **repeat mode**.

Each row has an enable checkbox. Unchecked macros stay in your settings but do not fire.

---

## Manage macros

A toolbar on the **Macros** tab moves macros around.

| Button | What it does |
|---|---|
| **Duplicate** | Clones the selected macro inside the same virtual controller. The copy is named `<name> (Copy)`. |
| **Copy** / **Paste** | Copy puts a macro on the system clipboard. Paste drops it into another virtual controller. This works across controllers and survives a restart. |
| **Copy From...** | Pull every macro from another virtual controller in one step. |

A macro fires only from the physical devices assigned to its own virtual controller. A macro copied from another controller no longer fires off a device that controller does not own.

---

## Triggers

A trigger can mix buttons, axes, and D-pad directions. All of them must be active at the same time. Combo entries can come from more than one physical controller. A left-hand pad and a right-hand pad can fire one shared macro. A trigger can also be a single gesture (see [Gesture triggers](#gesture-triggers) below).

### Trigger source

You pick where the trigger reads its inputs:

| Source | Reads from | Use when |
|---|---|---|
| **Output Controller** | The virtual controller after mapping (A, B, X, Y, LB, LT, etc.) | Most setups. The trigger keeps working when you swap physical devices. |
| **Input Device** | Raw inputs on one specific physical controller | The button is outside the standard 11 (touchpad click, pressure buttons, flight-stick extras), or you want a device-specific combo. |

An **Input Device** source also reaches devices that are not gamepads. An NFC reader shows an **Any NFC Tag** button plus one button per tag you have registered. A media device shows its named media keys (Play/Pause, Mute, and the rest). Tap a registered tag or press a media key to fire the macro, the same way a button press does.

An Input Device trigger does not have to name a specific device. Entries picked from the **(Any device)** group fire from whichever assigned device provides that input, and they render with an "(Any device)" chip. Profiles imported from the [Steam Workshop](steam-workshop-import.md) use these for macros triggered by paddles, touchpads, and gyro, which never pass through the virtual pad's output.

### Record a trigger

1. Click **Record Trigger**.
2. Hold the buttons you want.
3. Push a stick or pull a trigger past the threshold to add an axis input.
4. Tap a D-pad direction to add a hat input.
5. Click **Stop** when the inputs you want are listed.

### Trigger input types

| Type | Behavior |
|---|---|
| Button | Pressed buttons go into the combo. LB + A means both held. |
| Axis | Fires when the stick or trigger crosses the threshold. Each axis entry has its own **Invert**, **Half**, **Bidirectional**, and **Deadzone** options, the same set the merge-mapping editor uses on axis-to-button sources. **Half** by itself picks one side of center (Invert flips which side). **Half** plus **Bidirectional** fires past the deadzone on either side. This lets you bind separate macros to left-stick-left and left-stick-right, or one macro to "deflected past N percent in any direction". |
| D-pad / POV hat | Fires when the hat matches the recorded direction. The match is a 45-degree sector, so "Up" also catches small diagonals. |

A mixed example: LB + Right Stick X (Positive) + D-pad Up. All three must hold for the macro to fire.

### Axis threshold

When the trigger has an axis, a threshold slider appears (1 to 100 percent, default 50). The axis must cross that percent to count.

- 10 percent. A tiny push fires the macro.
- 90 percent. You need to push almost all the way.
- With a direction filter, the threshold only applies to that half of the axis.

### Gesture triggers

A trigger can be a touchpad gesture or a mouse gesture instead of a button combo. You pick these from a list, not by recording. Recording deliberately skips gestures so a stray swipe cannot overwrite the combo.

1. Click **Add from List** next to **Record Trigger**.
2. The dropdown lists buttons, POV directions, stick and trigger axes, the touchpad click, and every gesture enabled on the slot.
3. Pick the gesture you want. It joins the trigger the same as a recorded input.

<!-- SCREENSHOT: macro-add-from-list -->
![The Add from List dropdown showing gestures alongside buttons and axes](../images/macro-add-from-list.png)

Touchpad gestures (swipes, taps, pinch, rotate, shape templates) appear only after you enable them on the [Touchpad](../features/touchpad.md) tab. Mouse gestures (flick left, right, up, down, or a plain click) appear once you enable them for that mouse, including the gestures armed by a **Custom** activation input. Gesture triggers work with every fire mode, including On Release.

---

## Custom Expression trigger mode

Pick **Custom Expression** in the Trigger picker when the shape you want is bigger than a fixed combo. Chords across two pads. "Press this only if that other thing isn't pressed." Axes crossing a threshold that depends on another axis. Anything you can write as a small expression.

### Variables

Add as many variables as the formula needs. Each one becomes a letter: `a` for the first, `b` for the second, then `c`, `d`, `e`, and as many more as you add. The formula refers to those letters.

Each variable binds to one of two things:

- An **Input Device** input: any button, POV direction, or axis on any physical device assigned to the slot.
- An **Output Controller** channel: any button or axis on the slot's combined virtual controller output. The macro reacts to what the slot is emitting after merge, so a macro can fire on its own virtual controller's behavior.

Click **Record** on a variable row, push the input you want it to follow, and PadForge fills it in. Click **Clear** to wipe a binding.

### Trigger Formula

The **Trigger Formula** text box accepts:

- Variables: `a`, `b`, `c`, … (or the indexed form `s[0]`, `s[1]`, …).
- Math operators: `+`, `-`, `*`, `/`.
- Comparisons: `<`, `>`, `<=`, `>=`, `==`, `!=`.
- Logic: `&&` (and), `||` (or), `!` (not), `?:` (if/else).
- Functions: `abs`, `min`, `max`, `clamp`, `sign`, `lerp`, `round`, `sqrt`.

### Starter recipes

| Recipe | What it does |
|---|---|
| a alone | Fire when variable a goes from 0 to 1. |
| a and b | Fire only when both a AND b are active (chord). |
| a or b | Fire when either a OR b is active. |
| a but not b | Fire when a is active and b is NOT active. |
| Axis past 50% | Fire when stick axis a is deflected more than 50% from rest. |

Click a recipe to drop it into the formula box.

### How it fires

Rising-edge detection. The macro fires once when the formula's value crosses 0.5 going up. It does not fire again until the value drops below 0.5 and rises past it.

Boolean variables (button held, POV match) read as 0 or 1. A trigger axis reads 0 at rest and 1 fully pulled. A stick axis reads 0.5 at rest, falling toward 0 as you push one way and rising toward 1 as you push the other. A chord of two buttons crosses 0.5 when both go high.

A stick sits at 0.5 at rest, which already meets the fire threshold, so a bare stick variable is active before you touch it. To fire on stick deflection, measure distance from center. `abs(a - 0.5)` reaches 0.25 once the stick passes halfway in either direction, so `abs(a - 0.5) > 0.25` fires past that point. The **Axis past 50%** recipe writes that formula for you.

See [Button and Axis Mappings](../features/mappings.md) for the cross-device input picker the variable rows share with the rest of the app, and for the operator palette the Trigger Formula box uses.

---

## Fire modes

| Mode | When it fires |
|---|---|
| **On Press** | Once, the moment the trigger becomes active. Good for one-shot commands and toggles. |
| **On Release** | Once, the moment the trigger releases. Good for charged shots. |
| **While Held** | Every frame while the trigger is active. Good for turbo fire and live mouse control. |
| **Always** | Every frame, with no trigger. Good for stick-to-mouse and a permanent volume knob. |

---

## Actions

Actions run in list order, top to bottom, each time the macro fires.

### Button Press / Button Release

Press or release a virtual controller button. Button Press has a duration in milliseconds and auto-releases.

- Names follow the slot's output type (Xbox labels, PlayStation labels, or numbered buttons for Extended Custom).
- Select more than one button to fire them together.

### Key Press / Key Release

Send a keyboard keystroke. The game sees it as a real key.

- Combos work (Ctrl+C, Ctrl+Alt+Delete, etc.). Keys press in order and release in reverse.
- Type the combo string or pick from the dropdown.

### Text Block

Type a block of plain text as keystrokes. It sends Unicode, so accents, CJK, and emoji all type regardless of keyboard layout. Newlines press Enter. A pasted tab character presses Tab.

- **Text.** The text to type.
- **Char delay (ms).** Milliseconds between characters, 0 to 1000. 0 types the whole block in one batch. Raise it if a game drops fast input.

Use Key Press for key combos like Ctrl+C. Use Text Block for literal text.

### Repeat Key While Held

Keyboard autofire. While the macro's trigger is held, the key presses and releases on a fixed beat.

- **Key.** Picked with the same dropdown as Key Press.
- **Interval.** Milliseconds between presses, 10 to 1000, default 100. The first press fires the moment the trigger engages, the next each time the interval elapses.

Pair it with the **While Held** fire mode. Where the Until Release repeat mode loops a whole action sequence, Repeat Key While Held taps one key on its own clock and mixes with other actions in the same macro.

### Repeat Button While Held

Controller-button autofire, the virtual-pad twin of Repeat Key While Held. While the macro's trigger is held, the picked button pulses on and off at the interval. Imported Steam configs use it for turbo on pad buttons.

### Toggle Button / Toggle Key

Each fire latches or unlatches a controller button or a key. A latched output stays held until the next fire or until the macro is disabled. Imported Steam configs use these for their toggle presses.

### Run Program

Launch a program or file. You choose what runs.

- **Program.** The path to the program or file.
- **Arguments.** Optional command-line arguments.
- **Working directory.** Optional. The folder the program treats as its current directory, not the folder the program file sits in. Blank uses the default.

The launch is fire-and-forget, so the rest of the macro does not wait for it.

### Delay

Pause the sequence for the given number of milliseconds.

### Axis Set

Force a virtual controller axis to a fixed value.

| Axis | Value range |
|---|---|
| Stick (LX, LY, RX, RY) | -32768 to 32767. 0 is center. |
| Trigger (LT, RT) | 0 to 32767. 0 is released. |

### System Volume

Map an axis to Windows master volume. Updates every frame.

- **Axis.** Which axis drives volume.
- **Invert.** Release-to-louder.
- **Show volume OSD.** The Windows volume flyout. On by default. Updates at about 5 Hz so it does not spam.
- **Volume Limit.** Caps the maximum. 30 to 50 percent is a safe start for protecting your ears.

### App Volume

Same as System Volume, but it drives one app in the Windows audio mixer.

- **Process name.** The app to control (Spotify, Firefox, Discord). The dropdown lists apps that are playing audio right now.
- The other options match System Volume.

### Play Sound / Stop Sounds

Play a sound file through the slot's audio output. A Sony pad or Wii Remote plays it through the speaker. A haptic-tone pad plays it as a single vibrating tone. With no sound-capable device on the slot, it falls back to the PC's default output.

- **Sound.** The file to play (.wav, .mp3, .m4a, .aac, .wma, or .flac).
- **Volume.** Scales the file against the slot's master volume.
- **Loop.** Repeat until a **Stop Sounds** action, or (for While Held / Until Release macros) the trigger's release. One-shots play to the end.

**Stop Sounds** ends every macro sound on the slot. Pair it with a looping Play Sound to stop it from another macro. See [Controller Audio](../features/controller-audio.md) for the output device picker and sound packages.

### Mouse Move

Map an axis to cursor movement. Updates every frame.

- **Sensitivity** (1 to 100). Pixels per frame at full deflection. 10 to 15 is a good start.
- X axes move horizontally, Y axes move vertically.
- Sub-pixel accumulation keeps the cursor smooth at low sensitivity.

### Mouse Button Press / Mouse Button Release

Press or release a mouse button. Press has a duration in milliseconds and auto-releases. Buttons: Left, Right, Middle, X1 (Back), X2 (Forward).

### Mouse Scroll

Map an axis to scroll wheel movement. Updates every frame.

- **Sensitivity.** Scroll units per frame at full deflection. 3 to 5 is a good start.
- Stick Y scrolls in both directions. Triggers scroll one way.

### Recenter Mouse

Snap the cursor to the center of the primary monitor in one press.

- **Mode.** Which axes snap: X+Y, X only, or Y only.

### Fix Mouse Position

A toggle that pins the cursor at a fixed coordinate. Fire once to pin, fire again to release.

- **Mode.** Which axes the pin holds.
- **Pin X / Pin Y.** The coordinate to hold.

### Limit Mouse Region

A toggle that fences the cursor inside an inset rectangle. Fire once to clamp, fire again to release.

- **Mode.** Which axes the clamp applies to.
- **Inset X / Inset Y.** How far in from each screen edge the fence sits.

These three pair with the **Mouse Position X / Y** mapping sources (see [Button and Axis Mappings](../features/mappings.md)). While a pin or clamp is active, PadForge writes the cursor every frame, so a game that also moves the cursor can fight it. The action editor notes this.

### Move Mouse to Position

Warp the cursor to a fixed screen spot in one press. One jump, no pinning: the cursor is free again the instant it lands.

- **Mouse X / Mouse Y.** The target coordinate in pixels on the primary monitor.
- **Pick on screen.** Click it, then place the cursor where you want it. The button counts down three seconds ("Capturing in 3...") and captures the spot into the two fields.

Good for map pings, minimap clicks, and menu buttons that always live at the same spot. Community configs imported from the [Steam Workshop](steam-workshop-import.md) use this action for their cursor-warp bindings.

### Lightbar Color

Push an RGB color to every Sony pad on the slot as a temporary override. The override beats the base lightbar mode and the Input Reactive overlay. Game-driven writes still win at the packet level.

Two hold modes:

- **Reactive.** Run at full brightness, then fade to black over the Fade window. Good for damage flashes and kill confirms.
- **Sticky.** Hold the color at full brightness until a **Lightbar Color Clear** action or a fresh override replaces it. Good for armed / disarmed markers.

Available on slots that have at least one Sony pad (DualShock 4, DualSense, DualSense Edge).

### Lightbar Color Clear

Drop any active macro lightbar override on the slot. The base mode and Input Reactive overlay come back.

### Lightbar Mode Set

Change the slot's base lightbar mode to a specific value (Static, Rainbow, Audio Pulse, etc.). Every Sony pad on the slot renders the new mode with its own palette and decay settings.

### Lightbar Mode Cycle

Step through an ordered list of base lightbar modes. Each fire advances one step. The list wraps at the end.

### Rumble

Drive the slot's physical rumble from a macro. Per-motor strength from 0 to 100 percent, so a macro can hit one motor by itself or both together. Two hold modes match Lightbar Color:

- **Reactive.** Run at full strength across the Hold window, then fade to zero across the Fade window. Good for hit / shoot / confirm pulses.
- **Sticky.** Hold at full strength until a **Stop Rumble** action runs. Good for armed states and click-and-hold sustain.

Macro rumble combines with game rumble by taking the stronger of the two, so macro feedback always reaches the motors. It drives every rumble-capable pad on the slot, whatever the brand.

### Stop Rumble

End any active macro rumble override on the slot, no matter which motor was running. Pair this with a Sticky Rumble action to give the macro a clean release.

### Rumble Trigger Override

Drive the trigger motors directly from a macro. This is the macro counterpart to the [Trigger Routing](../features/force-feedback.md#trigger-routing) card, sending strength straight to the trigger channel: Xbox impulse triggers or DualSense Adaptive Trigger Vibration.

### Stop Trigger Vibration

End any active Rumble Trigger Override on the slot. Pair it with a Rumble Trigger Override the way Stop Rumble pairs with a Sticky Rumble action.

### Toggle Touchpad Overlay

Toggles the on-screen [Touchpad Overlay](../features/dashboard.md#touchpad-overlay) visibility. Each fire flips it: open if closed, close if open. Useful for binding a controller chord to "show me a touchpad on screen for the next gesture" without leaving the game.

### Set Gyro Engaged

Drives the slot's macro gyro-engage bit, OR-combined with the [Gyro](gyro.md) tab's Aim Engage button at the evaluator. Three modes:

| Mode | Effect |
|---|---|
| **Toggle** | Each fire flips the slot's macro-engaged bit. |
| **On** | Forces the bit true. |
| **Off** | Forces the bit false. |

Per slot, volatile (resets on profile switch and app restart). Lets a macro hold gyro on for one trigger pull then release it without rebinding the engage button. Combines with the Aim Engage button via OR. Either source can engage. Both must release to disengage.

### Gyro Recenter

Zeroes the pad's accumulated gyro aim references on press. Smoothing history clears, the Motion Lean neutral re-captures, and the gravity estimate re-seeds from the controller's current pose. Imported Steam configs use it for their camera-reset bindings.

### Cycle Pointer Modes / Set Pointer Mode

Change the Wii pointer mode for every IR-capable remote on the slot. This is the same Pointer Mode (Mouse, FPS Mouse, 4:3 Border, 16:9 Border) you set on the [Wii Controllers](../devices/wii-controllers.md) tab.

- **Cycle Pointer Modes.** Check the modes you want in the list. Each fire advances to the next checked mode. The list wraps at the end. The cycle position resets on app restart.
- **Set Pointer Mode.** Sets one fixed mode.

### Set Guide LED Brightness

Set the brightness of the glowing Guide or Home button, 0 to 100 percent, for every capable controller on the slot. 0 turns the LED off.

- Xbox One and later pads accept it over USB only. Bluetooth is ignored.
- The 2015 Steam Controller accepts it on any connection.
- Switch pads with a HOME button LED (Pro Controller, right Joy-Con, combined pair, charging grip) accept it on any connection.

The write is transient and not saved. Pair two of these actions to flash the LED when a macro starts and restore it when the macro ends. The [Lighting](../features/lighting.md) tab's Guide Button LED setting reasserts on its next update.

### Disconnect Controller

Turn off a Bluetooth controller. PadForge drops the link, and the controller goes to sleep once the link is gone. Good for a chord or button combo that puts a controller to sleep without reaching for it.

Pick a **Target**:

| Target | What it turns off |
|---|---|
| **Triggering Device** | The controller (or controllers) that fired this macro's trigger. |
| **Specific Device** | One controller you pick from a dropdown. |
| **All Devices on This Slot** | Every Bluetooth controller mapped to this pad's slot. |
| **All Bluetooth Devices** | Every Bluetooth controller PadForge knows. |

Works on Bluetooth controllers only. A USB-wired controller is skipped, and disconnecting a charging controller over Bluetooth doesn't interrupt its charge.

![The Disconnect Controller action with the Target dropdown](../images/macro-disconnect.png)

### Axis source for continuous actions

System Volume, App Volume, Mouse Move, and Mouse Scroll all read from one of two sources:

| Source | What you get |
|---|---|
| **Output Controller** (default) | The virtual controller's combined output after deadzone, range, and inversion. Device-independent. |
| **Input Device** | Raw input on one specific physical controller. Pick the device and axis from dropdowns. |

Pick **Input Device** when the axis is unmapped (a throttle lever you want for volume) or you want to skip the deadzone and curve math.

### Axis options

- **Invert axis.** Reverse the direction. Volume: release-to-louder. Mouse: opposite cursor.
- **Show volume OSD.** The Windows volume flyout. System Volume only. On by default.

### Build the sequence

1. Click **Add Action** and pick the type.
2. Set it up (button, key, delay, etc.).
3. Add more rows. They run top to bottom.
4. Use the delete icon to remove a row.

Quick melee combo:

1. Button Press: Y (50 ms)
2. Delay: 100 ms
3. Button Press: B (50 ms)

Stick-to-mouse aiming (Always mode):

1. Mouse Move: Right Stick X, sensitivity 15
2. Mouse Move: Right Stick Y, sensitivity 15

---

## Repeat modes

| Mode | Behavior |
|---|---|
| **Once** | Runs one time. |
| **Fixed Count** | Runs N times in a row. |
| **Until Release** | Loops while the trigger is held. Requires **While Held**. |

Fixed Count and Until Release both have a **Repeat Delay** in milliseconds between runs.

Turbo fire: While Held plus Until Release, Button Press A (50 ms), repeat delay 50 ms. A presses every 100 ms (about 10 times a second) while held.

---

## Consume trigger buttons

On by default. The trigger's buttons are stripped from the virtual controller output, so the game only sees the macro's actions.

| State | Game sees |
|---|---|
| On (default) | Macro output only. LB + RB are hidden. |
| Off | The trigger buttons and the macro output, both. |

Consume only applies to buttons on the Output Controller source. Input Device triggers are not part of the combined gamepad state, so there is nothing to consume.

---

## How actions run together

| Type | Actions | Behavior |
|---|---|---|
| Sequential | Button Press / Release, Key Press / Release, Mouse Button Press / Release, Move Mouse to Position, Delay, Axis Set | One at a time, top to bottom. |
| Continuous | System Volume, App Volume, Mouse Move, Mouse Scroll, Repeat Key While Held, Repeat Button While Held | Every frame, all in parallel. |

Both types mix in one macro. Two Mouse Move actions (X and Y) run in parallel while a Button Press in the same list runs in sequence next to them.

---

## Recipes

### Left Trigger as a volume knob

- Fire mode: Always
- Action: System Volume. Axis: Left Trigger. Volume Limit 50 percent. OSD on.

Always mode means there is no trigger combo. The Volume Limit prevents an accidental blast.

### Right Stick as a mouse cursor

- Fire mode: Always
- Actions:
  1. Mouse Move: Right Stick X, sensitivity 15
  2. Mouse Move: Right Stick Y, sensitivity 15

Lower sensitivity gives you precision. Higher gives you speed. Pair this with the bumper recipe below for full mouse control.

### Bumpers as mouse clicks

| Macro | Fire mode | Trigger | Action |
|---|---|---|---|
| Left Click | On Press | LB | Mouse Button Press: Left (50 ms) |
| Right Click | On Press | RB | Mouse Button Press: Right (50 ms) |

### Turbo fire

- Fire mode: While Held
- Trigger: Right Trigger axis, threshold 50 percent
- Repeat: Until Release, delay 50 ms
- Action: Button Press: A (30 ms)

A presses about every 80 ms (30 ms press plus 50 ms delay) while the trigger is past 50 percent. Release to stop.

### Per-app music volume

- Fire mode: While Held
- Trigger: LB
- Consume trigger buttons: On
- Action: App Volume. Axis: Left Stick Y. Process: Spotify. Volume Limit 80 percent.

Hold LB and move the left stick up or down to set Spotify volume. The game never sees LB. The level stays where you leave it.

### Quick chat combo

- Fire mode: On Press
- Trigger: D-pad Down + A
- Actions:
  1. Key Press: T (50 ms). Opens chat.
  2. Delay: 100 ms
  3. Key Press: G (50 ms)
  4. Delay: 50 ms
  5. Key Press: G (50 ms)
  6. Delay: 50 ms
  7. Key Press: Return (50 ms). Sends the message.

Increase the delays if the game needs more time between keystrokes.

---

## Extended Custom button support

Extended slots set to **Custom** support up to 128 buttons. The trigger recorder and the Button Press dropdown grow to match the slot's button count. Xbox, PlayStation, and gamepad-shaped HIDMaestro profiles use the standard button names.

---

## Tips

- Delays under 10 ms may not register in some games. Start at 50 ms and work down.
- Test in the actual game. Timing needs change per title.
- Mixing button and axis inputs in one trigger cuts down on accidental fires.
- Mouse sensitivity 10 to 15 for cursor work. 3 to 5 for scrolling.
- Macros save per profile. Different games can have different macro lists through [Profiles](profiles.md).

---

## Limitations

- Macro lightbar overrides do not override what the game writes at the packet level. A game that drives the lightbar each frame wins.
- Macro rumble takes the stronger of the macro and game strength, so a game holding a motor at full strength masks a weaker macro pulse.
- Input Device triggers cannot use **Consume trigger buttons**. The raw input layer is upstream of the combined gamepad state.

---

## Related pages

- [Button and Axis Mappings](../features/mappings.md): set up base mappings before you add macros.
- [Controller Slots](../features/controller-slots.md): every slot has its own macro list.
- [Controller Audio](../features/controller-audio.md): the Play Sound action, output device picker, and sound packages.
- [Devices](../features/devices.md): pick the physical device for Input Device triggers.
- [Force Feedback](../features/force-feedback.md): rumble and vibration settings the macro layers over.
- [Profiles](profiles.md): Macros save per profile, so each game can have its own set.
- [Steam Workshop Config Import](steam-workshop-import.md): imported community configs arrive with cursor-warp, autofire, toggle, and long-press macros pre-built.
- [Troubleshooting](../troubleshooting.md): fixes for macros that do not fire.

---

*Last updated for PadForge 4.1.0*
