# Troubleshooting

*Common problems and how to fix them. If your issue is not on this page, check [GitHub Issues](https://github.com/hifihedgehog/PadForge/issues).*

![Settings page where most troubleshooting starts (driver install, polling interval, language)](images/settings.png)

Related pages: [Installation](start/installation.md), [Settings](features/settings.md), [Driver Management](features/driver-management.md), [Devices](features/devices.md).

---

## No Devices Detected

**The [Devices](features/devices.md) page is empty or the [Dashboard](features/dashboard.md) shows "0/0 devices online"**

1. Try a different USB port. Use one directly on the computer, not a hub.
2. Try a different cable. Some cables are charge-only.
3. Restart PadForge. Some devices need a fresh launch.
4. Check Windows Device Manager. If the device does not appear under "Human Interface Devices" or "Sound, video and game controllers," the issue is the device or its driver.
5. For Bluetooth controllers, pair and connect in Windows Bluetooth settings before starting PadForge.
6. If HidHide is installed, another tool may have cloaked the device. PadForge adds itself to the HidHide whitelist automatically while **"Hide Devices from Games"** is on in [Settings](features/settings.md). With that toggle off, decloak the device in the HidHide Configuration Client, or turn the toggle on and let PadForge manage hiding.
7. Close other controller tools (DS4Windows, BetterJoy, reWASD, x360ce). They may intercept access.
8. A DualShock 3 pairs through PadForge itself, with no separate driver tool to install. Connect it by USB, click **Pair** on the [Devices](features/devices.md) page, and follow the dialog. When it finishes, unplug the pad and press the PS button to connect over Bluetooth. It then streams with rumble and the player-number LED.

---

## Controller Detected but Not Mapping

**The controller appears on [Devices](features/devices.md) but produces no output or wrong output on the virtual controller.**

1. Unknown or unusual controllers may need manual mapping.
2. Assign the device to a slot. Select at least one numbered toggle on the [Devices](features/devices.md) page.
3. Map inputs manually via **Record** on the [Mappings](features/mappings.md) tab for each button and axis.
4. Enable **"Force Raw Joystick Mode (Bypass Gamepad Remapping)"** on the [Devices](features/devices.md) page if SDL3's remapping produces wrong outputs. Re-record all mappings afterward.
5. Check live input on the Devices page. If axes and buttons do not respond there, the issue is at the driver or HID level.
6. Check the source dropdown on each mapping row. Confirm it points to the correct input device.

---

## Virtual Controller Not Appearing in Games

**A slot is created and a device assigned, but games do not detect the virtual controller.**

1. Install **HIDMaestro** from [Settings](features/settings.md) for Xbox, PlayStation, Nintendo, or Extended output.
2. Install **Windows MIDI Services** from [Settings](features/settings.md) for MIDI output.
3. Confirm the slot is enabled. The power icon on the Dashboard card should be green.
4. Confirm the engine is running. The Dashboard should show "Running" with a green icon.
5. Restart the game. Some games only scan for controllers at startup.
6. Check the game's input settings. Some games require manual controller selection.
7. For Extended controllers, verify in `joy.cpl` (Win+R > `joy.cpl`). If controllers are not listed, see "Extended Controllers Not Working" below.

---

## Nintendo Slot Not Seen by a Game

**A Nintendo virtual controller is active but the game does not react to it.**

1. Install **HIDMaestro** from [Settings](features/settings.md). The Nintendo output rides the same driver as Xbox, PlayStation, and Extended.
2. Games see the slot as the picked Nintendo profile, a **Nintendo Switch Pro Controller** or a **Nintendo Switch 2 Pro Controller**. XInput-only games never read either one. Use an Xbox slot for those.
3. Steam Input detects it as a Pro Controller with Nintendo glyphs. For games without native Switch Pro support, let Steam Input translate it, or switch the slot to Xbox output.
4. Gyro and accelerometer pass through from the assigned pad, so emulators and Steam Input gyro read real motion.
5. Face buttons follow Nintendo lettering, so A sits on the right and B on the bottom. Prompts that look swapped against an Xbox pad are the Switch layout working as intended.
6. The Nintendo slot has no Customize surface. It deploys a catalog profile as-is. The profile picker offers **Nintendo Switch Pro Controller** (the default) and **Nintendo Switch 2 Pro Controller**.

---

## Double Input in Games

**Every press registers twice, menus scroll too fast, or the game shows two controllers.**

The game is reading both the physical controller and PadForge's virtual controller.

1. Install **HidHide** from [Settings](features/settings.md).
2. Enable **"Hide Devices from Games"** on the [Settings](features/settings.md) page.
3. On the [Devices](features/devices.md) page, enable **"Hide from Games (HidHide)"** per device.
4. PadForge always whitelists itself, so it keeps seeing hidden devices. Add other apps (emulators, tools) that need a hidden device under **Whitelisted Applications** on [Settings](features/settings.md).
5. Restart the game after changing HidHide settings.
6. Check the game's controller settings. Disable the physical controller and keep the virtual one.
7. If using Steam, disable Steam Input for the game or close Steam entirely.
8. BLE controllers (e.g., Xbox via Bluetooth) are properly hidden by HidHide on current PadForge builds. If peek-through still happens, check that the per-device **"Hide from Games (HidHide)"** toggle is on and that **"Hide Devices from Games"** is enabled in the HidHide section of [Settings](features/settings.md).

---

## Rumble Not Working

**No vibration from the physical controller when games send force feedback.**

1. Set **Overall Gain** above 0% on the [Force Feedback](features/force-feedback.md) tab.
2. Set both **left motor** and **right motor** strength above 0%.
3. Click **Test Rumble** to verify hardware support. No vibration means the device lacks rumble motors or driver support.
4. Confirm a device is assigned to the slot and connected (green status dot).
5. Check rumble support on the Devices page capabilities list. Devices without native rumble attempt haptic fallback, but results vary.
6. Try a different game. Not all games use force feedback.
7. Close other controller software (Steam Input, DS4Windows, reWASD) that may intercept rumble.
8. A DualShock 3 rumbles once it is paired through PadForge's **Pair** flow on the [Devices](features/devices.md) page. Rumble is native over that connection. A DS3 running through some other driver may not pass rumble.
9. For Extended output, the game must send HID PID 1.0 force feedback. See "Force Feedback Not Working" below.

---

## Audio Rumble Not Working

**Audio Rumble is enabled but the controller does not vibrate, or the Level meter stays flat.**

1. Confirm audio plays through the system default render device. The Level meter should show activity.
2. Level meter flat during playback? Toggle **Enable Audio Rumble** off and on to restart WASAPI capture.
3. Set **Overall Gain** above 0%. It applies to audio rumble too.
4. Increase **sensitivity** (default 4, try 8-12, range 1-20).
5. Raise **Bass Cutoff (Hz)** (default 80, range 20-200) to capture more mid-bass.
6. Set both motor scale sliders above 0%.
7. Click **Test Rumble**. No vibration means the device lacks rumble motors.
8. Some apps (DAWs, certain games) open audio in exclusive mode, blocking WASAPI loopback.
9. At least one audio output device must be active in Windows Sound settings.

---

## Bass Shakers Output Silent

**"Route Rumble to an Audio Output" is on but nothing plays on the shaker or subwoofer.**

1. Check the status line on the **Bass Shakers** tab. "Audio output is not running." means the routing is off or the engine is stopped. "The selected output device is unavailable. Audio stays off until it returns." means the chosen **Output Device** disappeared. Pick another or reconnect it.
2. The feature works with Xbox, DualShock 4 / DualSense, and Nintendo Switch Pro virtual controllers, plus Extended virtual controllers with force feedback, such as racing wheels. Other slot types have no game feedback to route.
3. Game feedback and **Test Rumble** play through the audio output. Macro rumble stays on the controller by design. Test Rumble on the Force Feedback tab is therefore a valid audio-path check, as are the per-voice **Test** buttons and **Frequency Sweep** on the Bass Shakers tab.
4. Set **Master Gain** above zero and enable at least one voice with its own gain above zero.
5. Run **Frequency Sweep** (20 to 120 Hz over eight seconds) and note where the shaker responds strongest, then set the voice frequencies there.
6. Bluetooth audio devices add noticeable latency. Use a wired output if the thump lags the game.

---

## Extended Controllers Not Working

**Extended (HIDMaestro) controllers do not appear in games or `joy.cpl`.**

1. Accept the UAC prompt at PadForge startup. PadForge always runs as administrator. Canceling the prompt blocks startup entirely, so the engine never initializes HIDMaestro.
2. Verify the HIDMaestro driver shows "Installed" on the [Settings](features/settings.md) page.
3. Check `joy.cpl` (Win+R > `joy.cpl`). If empty, create an Extended slot on the Dashboard first.
4. Restart PadForge after installing HIDMaestro.
5. If a slot stays stuck on "Initializing," check the **Inactivity Timeout** in [Settings](features/settings.md). After the timeout, a slot whose mapped devices stay offline has its live virtual controller torn down to free its kernel slot. The slot configuration (mappings, profile, position) is preserved. The virtual controller recreates automatically when the devices return online.

---

## Force Feedback Not Working

**Games send force feedback but the physical controller does not vibrate on an Extended slot.**

1. Confirm the game sends **HID PID 1.0** force feedback. Most native DirectInput FFB games do. XInput-only games do not. Use Xbox or PlayStation output for XInput rumble.
2. Set **Overall Gain** above 0% on the [Force Feedback](features/force-feedback.md) tab.
3. Set motor strength sliders above 0%.
4. Click **Test Rumble** to confirm the physical controller supports rumble.
5. HIDMaestro Extended profiles publish constant, ramp, periodic (sine, square, triangle, sawtooth), and condition (spring, damper, inertia, friction) effects. Effect types outside that set may not produce rumble.
6. Restart the game. Some games only initialize FFB at startup.

---

## MIDI Not Available

**The MIDI button in the "Add Controller" popup is dimmed and does nothing, with the tooltip "MIDI (requires Windows MIDI Services)".**

1. Install **Windows MIDI Services** from [Settings](features/settings.md).
2. Windows MIDI Services requires **Windows 11 24H2 (build 26100) or later**. Earlier Windows 11 builds and any Windows 10 build are unsupported by Microsoft's SDK.
3. Restart PadForge after installing.
4. Verify the "Windows MIDI Services" service is running (Win+R > `services.msc`).
5. "Failed to create MIDI session" means the SDK initialized but cannot reach the service. Restart the service or reboot.

---

## No MIDI Output

**A MIDI slot is active but no messages reach the DAW or synthesizer.**

1. In the DAW, look for **"PadForge MIDI N"** in the MIDI input list.
2. Set the receiving app to read from the PadForge MIDI endpoint.
3. Confirm the engine is running and the slot is enabled (green power icon).
4. Match the MIDI channel (1-16) between PadForge and the receiving app.
5. Verify CC numbers (axes) and note numbers (buttons) match what the receiving app expects.
6. Use a MIDI monitor (MIDI-OX or Windows MIDI Services console) to confirm PadForge is sending. If messages appear there but not in the DAW, the issue is DAW configuration.

---

## My Macro Doesn't Fire

**A macro trigger is configured but pressing the trigger does nothing.**

1. All trigger components must be active **simultaneously**. Partial presses do not fire.
2. For axis triggers, the input must exceed the configured **threshold percentage**.
3. Check the macro's **Layer**. "Any layer" fires regardless of the engaged layer. Base and named layers fire only while that layer is engaged, exactly like a mapping row. A macro scoped to a shift layer is inert the whole time that layer is off.
4. Check the trigger mode. Several fire by design only on a specific press shape:
   - **On Long Press** fires after the trigger is held for the **Hold Time**. A quick tap does nothing.
   - **On Short Press** fires on release before the Hold Time elapses. Holding past it fires nothing.
   - **On Single Press**, **On Double Press**, and **On Triple Press** wait out the **Press Window** and fire only on the matching press count.
   - **Turbo** repeats only while the trigger is held.
5. Confirm the macro's enable checkbox is checked.
6. Confirm the engine is running and the slot is enabled.
7. If the trigger source is "Input Device" but no device is assigned, there is nothing to read. Switch to "Output Controller" or assign a device.
8. Check for conflicting macros with overlapping triggers on the same slot.

---

## Mouse Actions from Macros Aren't Working

**A macro with Mouse Move, Mouse Button, or Mouse Scroll produces no visible effect.**

1. Match the axis source. "Output Controller" reads mapped output, "Input Device" reads the physical device directly.
2. Adjust the **sensitivity slider** if movement is too fast or too slow.
3. Confirm the trigger is firing (see "My Macro Doesn't Fire" above).
4. Anti-cheat software may block simulated mouse input.

---

## Macro Won't Stop Running

**A macro keeps firing after the trigger is released, or runs with no trigger at all.**

1. A macro set to **Always** fires every frame while the slot is active. No trigger required. That is its design.
2. A macro set to **Toggle** latches: the first press turns the actions on, and holds and repeats stay active until the second press. Tap the trigger again to release it.
3. Uncheck the macro's enable checkbox to stop it.
4. Delete the macro if it is no longer needed.
5. Disable the slot (power icon on the Dashboard card) to stop all its macros.

---

## Keyboard+Mouse Not Working

**A Keyboard+Mouse slot is active but key presses or mouse movement do not appear in games.**

1. Verify the slot type is Keyboard+Mouse on the Dashboard card.
2. Assign physical inputs to keyboard keys or mouse buttons on the Mappings tab.
3. Adjust mouse sensitivity on the Sticks tab or macro action settings.
4. Anti-cheat software (EAC, BattlEye, Vanguard) may block simulated input.
5. Confirm the engine is running and the slot is enabled.

---

## Settings Not Saving

**Changes revert after restart or the settings file does not update.**

1. Wait for autosave. PadForge saves after changes settle. Unexpected closes may lose recent edits.
2. Click **Save** on the [Settings](features/settings.md) page to force an immediate save.
3. Confirm PadForge has write access to its folder. `PadForge.xml` lives next to the executable. "Error saving settings" in the status bar indicates a permissions issue.
4. Click **"Open Folder"** on Settings and verify `PadForge.xml` exists and is not read-only.
5. Add a PadForge exception if antivirus software blocks file writes.
6. If "Error loading settings" appears on startup, the XML is corrupted. Delete `PadForge.xml` and restart. PadForge creates fresh defaults. Or click **"Reset to Defaults."**
7. If the folder is synced by OneDrive, Dropbox, or similar, concurrent access across machines can corrupt the file. Move PadForge to a non-synced folder.

---

## App Won't Start or UAC Prompt Issues

**PadForge does not start, closes immediately, or shows a UAC prompt every time.**

1. UAC is expected. PadForge always runs as administrator. HIDMaestro driver registration, HidHide whitelist edits, and the polling loop all run in that one elevated process.
2. Clicking "No" on UAC blocks startup. Windows does not start an administrator-required app when the user declines the prompt. Run PadForge again and accept the prompt.
3. PadForge allows only one instance. Check Task Manager for existing PadForge processes.
4. Check for `crash.log` next to `PadForge.exe`. It appears only after a crash and records the error. Attach it to a bug report.
5. PadForge ships as a single self-contained `PadForge.exe` with the .NET runtime and SDL3 embedded. Nothing needs installing separately. If startup still fails with no `crash.log`, the download may be truncated or corrupt. Re-download `PadForge.exe` from the [release page](https://github.com/hifihedgehog/PadForge/releases).

---

## High CPU Usage

**PadForge uses significant CPU, causing fan noise or slowdowns.**

1. Increase the **polling interval** in [Settings](features/settings.md) > Input Engine. Default is 1 ms (~1000 Hz). Try 4 ms (~250 Hz) or 8 ms (~125 Hz) for casual use.
2. Disable **"Continue Polling When Window Loses Focus"** if PadForge is only needed during gameplay.
3. Remove unused virtual controller slots.
4. Disable **Audio Rumble** on unused slots (runs WASAPI capture and real-time DSP).

---

## DSU Motion Not Working in Emulator

**The emulator does not receive gyroscope or accelerometer data.**

1. Enable **"Enable DSU Motion Server (CemuHook Motion Provider Protocol)"** on the [Dashboard](features/dashboard.md): Status should show "Listening on :26760".
2. Match the port (default 26760) between PadForge and the emulator. "Port 26760 in use" means another app (BetterJoy, DS4Windows) is on that port.
3. Use `127.0.0.1` as the server address. PadForge binds to loopback only.
4. Confirm the controller has motion sensors on the [Devices](features/devices.md) page. Any controller PadForge reads gyroscope or accelerometer data from feeds the DSU server: DualSense, DualShock 4, DualShock 3, Switch Pro, Switch 2 Pro, Joy-Cons, and the Wii Remote all report motion.
5. DSU protocol supports slots 1-4 only. Assign the motion device to one of those slots.
6. The DSU server binds to loopback only, so no firewall rule is involved. An emulator on another machine cannot reach it at all.
7. In the emulator's motion settings, add a DSU server at `127.0.0.1` with the matching port and select the correct slot.

---

## Web Controller Not Connecting

**The browser shows "Disconnected" or cannot reach the web controller URL.**

1. Enable the web controller on the [Dashboard](features/dashboard.md): Status should show "Running" with a URL.
2. Both devices must be on the same Wi-Fi or LAN network.
3. PadForge creates a firewall rule automatically.
4. "Port 8080 in use" means another app occupies that port. Change the port in the **Web Controller** section of the [Dashboard](features/dashboard.md).
5. "Access denied for port 8080 (run as admin)" means Windows reserved it or another service holds it. Change the web controller port on the [Dashboard](features/dashboard.md) to a free one.
6. Rotate the browser device to **landscape** orientation.
7. Try Chrome, Firefox, or Edge if WebSocket issues occur.

---

## Web Controller drops on iOS Safari After Tab Switch

**On iPhone or iPad Safari, the web controller shows "Disconnected" after locking the screen, switching tabs, or returning from another app.**

iOS Safari kills WebSocket connections when the page loses focus. The web controller page detects the dropped socket, shows "Disconnected. Tap to reconnect.", and retries every three seconds, or the moment the tab comes back to the foreground. If it does not come back, do this:

1. Tap the page to bring it back into focus.
2. Pull down to refresh, or close the tab and reopen the URL.
3. Keep Safari in the foreground while playing. Background-tab WebSockets are not reliable on iOS.
4. Add the page to the Home Screen as a PWA for a more stable foreground session.

---

## Remote Link PC Not Appearing

**A second PC runs Remote Link but does not show up under "Nearby PCs (Not Paired)."**

1. Enable **Remote Link** on both PCs from the [Dashboard](features/dashboard.md). A PC only announces itself while it is on.
2. Both PCs must be on the same local network. Discovery is a same-subnet broadcast, so a separate guest network, VLAN, or Wi-Fi band hides them from each other.
3. Some networks block broadcast. Open **Or Connect by Address (Advanced)**, enter the other PC's address and port, and click **Pair / Connect**.
4. Allow PadForge through the firewall on each PC. For per-port rules, open UDP 27501 for discovery and TCP 27500 (or your changed listening port) for the connection.
5. For play across the internet, swap connection codes. Copy **This PC's Code** on the [Dashboard](features/dashboard.md), have the other person paste it into their Connect box while you paste theirs, then you both click **Pair / Connect**. That opens a direct path with no VPN and no port forwarding. Broadcast discovery does not cross the internet, so the code is how the two PCs find each other. If PadForge warns that the network cannot make direct connections (a mobile hotspot or carrier-grade NAT), fall back to a VPN like Tailscale and connect by address.

---

## Remote Link Pairing Fails

**Pairing does not complete, or the six-digit codes differ on the two screens.**

1. Check that the two codes match before confirming. A mismatch means the PCs did not reach each other directly. Cancel and retry.
2. Confirm on both PCs. Pairing needs both sides to accept.
3. A failed handshake creates no device and shares nothing. Start pairing again from one side.
4. A PC you revoked cannot reconnect until you pair it again.

---

## Shared Device Not Showing After Pairing

**Two PCs are paired but the owner's controller does not appear in the consumer's device list.**

1. Confirm the pairing is active. Each PC lists the other under **Paired PCs** on the [Dashboard](features/dashboard.md).
2. Remote Link shares controllers, wheels, and HOTAS hardware, not arbitrary USB devices.
3. On the consumer, assign the shared device to a [slot](features/controller-slots.md) and map it like a local controller.
4. Auto-reconnect is on by default. With it off, the PCs do not relink on their own after a drop. Turn it back on in the Remote Link settings, or re-pair.

---

## Remote Link Feedback or Keyboard Not Working

**A shared device drives the game, but rumble, LEDs, or keyboard output do not reach the owner PC.**

1. Feedback returns only for what the physical device supports: rumble, Xbox trigger rumble, wheel force feedback, adaptive triggers, lightbar, player LEDs, Guide button LED brightness, speaker audio, and HD haptic tones. A device without a given feature shows nothing for it.
2. Keyboard, mouse, and macros from a shared device are blocked when **Limit This PC to Gamepad Input Only** was ticked for that paired PC (its row under Paired PCs shows "gamepad only"). To allow them, revoke the PC and pair again with the box unticked.
3. See [Force Feedback](features/force-feedback.md), [Impulse Triggers](features/impulse-triggers.md), [Lighting](features/lighting.md), and [Controller Audio](features/controller-audio.md) for the per-feature setup, which also applies over the link.

---

## Profile Not Switching Automatically

**Auto-profile switching is enabled but PadForge does not switch when the game is in the foreground.**

1. Confirm **"Auto-Switch Profiles Based on Foreground Application"** is checked on the [Profiles](guides/profiles.md) section.
2. Verify the executable path matches (case-insensitive, full path). Use the file browser button to avoid typos.
3. For games launchable from multiple locations, separate paths with the pipe character (`|`).
4. Add the game's own executable, not the launcher's (Steam, Epic, etc.).
5. PadForge always runs elevated, so it can read the foreground path of elevated games. If a protected process still is not detected, add the game executable that actually owns the window.
6. Save after configuring. Profile data must persist to `PadForge.xml`.

---

## Community Configs (Steam Workshop) Issues

**"Steam Is Unreachable" in the Browse Community Configs dialog.**

1. Check your internet connection and click **Retry**.
2. Corporate or school networks sometimes block Steam. The connection uses standard HTTPS (port 443).
3. Already-imported profiles keep working offline. They live on this PC.

**An imported profile double-inputs or fights the original Steam config.**

The imported profile replaces what the Steam config did. Disable Steam Input for the game (Steam > game properties > Controller), or close Steam, and cloak the physical pad on the [Devices](features/devices.md) page.

**An imported profile does nothing in game.**

1. Assign your physical controller to both of the profile's pads. Imports ship with no device assignments.
2. Confirm the profile is active (load it, or add the game's executable via **Edit** for auto-switch).

See [Steam Workshop Config Import](guides/steam-workshop-import.md) for the full feature guide.

---

## Sensitivity Curves Not Responding

**A sensitivity curve is set but stick or trigger output seems unaffected.**

1. Check the correct axis. X (horizontal) and Y (vertical) have independent curves.
2. If the preset is "Linear," no modification is applied. Select a different preset or add custom points.
3. Click **Reset** to restore Linear, then apply a new preset to verify functionality.
4. A large deadzone leaves little range for the curve to affect. Reduce the deadzone to test.
5. Custom control points placed nearly linearly produce no visible change. Spread them further apart.
6. Per-direction max range settings may cause asymmetric behavior. Review them on the Sticks tab.
7. Non-default deadzone shapes (Axial, Hybrid, Sloped) interact differently with curves. Try Scaled Radial to isolate the issue.

---

## Steam Controller Conflicts

**Controller behaves unexpectedly, is not detected, or rumble stops. Especially Switch Pro or Switch 2 Pro.**

1. Disable **Steam Input** for the specific controller in Steam > Settings > Controller.
2. Close Steam entirely if not in use.
3. Switch 2 Pro Controller. Steam may lock the WinUSB interface. Close Steam before connecting, or disable Switch controller support in Steam.

---

## Buttons Map to Wrong Outputs

**Buttons do not match expected positions, trigger two inputs, or produce no input.**

1. Enable **"Force Raw Joystick Mode (Bypass Gamepad Remapping)"** on the [Devices](features/devices.md) page to bypass SDL3's remapping.
2. Re-record all mappings manually with **Record** on the [Mappings](features/mappings.md) tab.
3. Verify in `joy.cpl` that buttons work correctly at the Windows level.
4. Known affected devices: certain third-party controllers with non-standard HID layouts.

---

## Opposite Buttons Cancel Each Other

**Two opposite directions held together and one, or both, vanish from the game.**

1. That is SOCD cleaning doing its job. The **Simultaneous Opposite Cardinal Directions (SOCD)** card on the **Output** tab resolves paired buttons held at once.
2. The **Mode** decides the outcome. **Last Wins (Snap Tap)**: the most recent press wins, and releasing it re-presses the still-held partner. **Neutral**: holding both releases both until one is let go. **First Wins**: the earlier press keeps winning until it is released.
3. The rule applies to the slot's final combined output, so physical, mapped, and macro presses are all cleaned.
4. To turn it off, set the Mode to **Off** or remove the pair under **Button Pairs**.
5. Keyboard+Mouse slots have their own SOCD card with **Key Pairs**, applied to the slot's virtual keyboard output.

---

## Force Raw Joystick Mode

**Buttons map wrong, trigger double inputs, or shoulder/trigger/stick-click inputs are missing.**

SDL3's gamepad mapping does not match the device's HID report layout (common with some third-party controllers).

1. Go to the **Devices** page.
2. Select the problematic device.
3. Enable **"Force Raw Joystick Mode (Bypass Gamepad Remapping)"** in the Input Mode section.
4. Go to the **Mappings** tab and manually record each button.
5. Auto-mapping is unavailable in raw mode, but raw indices will be correct.

---

## Mouse or Keyboard Input Issues

**Mouse buttons don't register, mouse movement is barely visible, or mouse axes can't be recorded.**

1. Mouse buttons map like any other input. On the Mappings tab, click **Record** on a row and press the mouse button.
2. Mouse axes show relative deltas, not absolute positions. Fast movements produce larger values.
3. When recording a mouse axis mapping, move the mouse in the desired direction. Detection is instant.
4. PadForge does not automatically consume mouse or keyboard inputs. Enable **"Consume Mapped Inputs (Hooks)"** or **"Hide from Games (HidHide)"** manually if needed (a warning appears before enabling).

---

## Stick Drift After Calibration

**The stick drifts even after setting deadzones.**

1. Go to the **Sticks** tab.
2. Leave the stick at rest. Do not touch it.
3. Click **Calibrate Center**.
4. PadForge measures the actual rest position and applies an offset so the deadzone centers correctly.

---

## Flick Stick Doesn't Turn the Camera

**A Flick Stick source is selected but sweeping the stick does not rotate the view.**

1. Map **"Flick Stick (Right Stick)"** to **Mouse X** from the input dropdown in Mappings, on any layer. Flick Stick produces mouse movement, so it needs a Mouse X row to land on.
2. Point the stick and the camera turns to match. Sweep the rim to fine-turn.
3. The game's camera must follow the mouse. Flick Stick drives the camera through mouse input, not a stick axis.
4. Tune it on the **Sticks** tab under **Flick Stick**. "Flick Stick (Left Stick)" and per-touchpad variants are available from the same dropdown.

---

## Volume Macro Issues

**Volume changes direction is wrong, or the OSD appears when it should not.**

1. Wrong direction. Enable **Invert Axis** on the volume action settings.
2. Unwanted OSD. Disable **Show Volume OSD** on the volume action.
3. Volume not changing. Confirm the trigger fires (see "My Macro Doesn't Fire" above).

---

## Shift Layer Won't Engage or Won't Turn Off

**The activator input is set but the layer never turns on, a long press never registers, or a toggled layer stays stuck on.**

1. Check the **Mode**. Hold keeps the layer on only while the activator is held. Toggle and Latch flip the layer on a press and keep it on until you press again. Sticky (one-shot) turns the layer on with a tap, then drops it the moment you use a mapped input on the layer and release. Cycle steps through an ordered list of layers, one per press.
2. Check the **Delay**. In Hold mode it is a debounce: the activator must stay held that long before the layer changes. In Toggle, Latch, or Sticky mode a non-zero Delay turns the activator into a long press, so the layer flips only when the hold crosses that time and a quick tap does nothing. Lower the Delay to 0 if a tap should register.
3. Check **Fire on Release**. With it on, the activator waits until the button is let go before firing, so it looks dead the whole time the button is held. If a hold delay is set, the press must last that long for the release to count.
4. For an **Axis** activator, the input must cross the threshold. Default is 0.5 of full deflection.
5. For a **Chord** activator, both inputs must hold at the same time.
6. The activator can live on a different physical device than the slot it shifts. Confirm that device is online.
7. Last engaged wins on conflicts. If a different slot's activator fired more recently, that layer is active instead.
8. Look at the engaged-layer flyout at the bottom of the screen. If it never appears, the activator never registered the input.

**A toggled layer won't turn off.**

1. Tap the activator again to release a Toggle layer.
2. Set **Auto-Cancel After Inactivity** (Toggle mode) so the layer drops itself after an idle stretch. It is 0 (off) by default. Enter a time in milliseconds. The layer turns back off after that long with none of its own mapped inputs active, and the timer restarts on every layer input.

---

## Impulse Triggers Tab Not Visible

**The Impulse Triggers tab is missing on a slot you expected to have it.**

1. The tab only appears when the assigned physical pad has trigger motors. Xbox One, Xbox Elite (Series 1 / Series 2), and Xbox Series X|S pads have them. Xbox 360 and most third-party pads do not.
2. The tab is per pad per slot. Pick the right physical device in the assigned-devices dropdown.
3. A DualSense does not get this tab. Its trigger motors are driven from the Adaptive Triggers tab instead. Xbox impulse data a game sends routes there automatically as trigger vibration, gentler than Xbox impulse-trigger motors. If the buzz feels weak, raise the Vibration effect strength on the Adaptive Triggers tab.

---

## Custom Expression Macro Won't Fire

**A Custom Expression macro is set up but the formula never crosses 0.5.**

1. Open the formula editor and watch the **live preview value** while you press the variable inputs. A button or trigger variable that never moves off 0, or a stick variable that never moves off 0.5, is not bound.
2. Each variable needs a recorded input. Click **Record** on a variable row and press the input.
3. The macro fires on the **rising edge** (0 → over 0.5). It does not refire until the value drops below 0.5 and rises past it again.
4. Buttons and POV directions read as 0 or 1. Triggers read 0 at rest up to 1 fully pressed. A stick axis reads 0.5 at rest and moves toward 0 or 1 as you push it, so a resting stick showing 0.5 is normal, not a binding failure.
5. Verify the formula syntax. Parse status under the formula box shows **✓ valid** or **parse error**.

---

## Touchpad Overlay Doesn't Drive the DS4 / DualSense Touchpad

**The Touchpad Overlay window is enabled but touch input doesn't reach the game.**

1. The overlay drives the touchpad on the assigned **PlayStation** slot only. Confirm the slot type is PlayStation, not Xbox or Extended.
2. The slot needs at least one mapped device. The overlay forwards finger contacts. The slot needs to exist for them to land somewhere.
3. If the slot's source is a real DualSense or DS4, that pad passes its own touchpad through to the game, and that takes priority over the overlay. Remove or hide the physical pad from the slot to let the overlay drive the touchpad instead.

---

## Touchpad Pressure Reads in Steps

**A touchpad's Pressure source jumps between 0%, one fixed level, and 100% instead of reading smoothly.**

1. That is **Synthetic Pressure**. On pads that report a touch as full pressure (DualShock 4, DualSense, Steam Controller 2015), it shapes the Pressure sources into three steps: no touch reads 0%, a resting touch reads the Touch Pressure Level, and a pad click reads 100%.
2. Turn off **"Enable Synthetic Pressure"** in the device's touchpad settings to return to raw readings.
3. A pad without a true pressure sensor reports touch as full pressure by hardware. Synthetic Pressure is the only way to get graded values out of it. Smooth analog pressure needs a pad that actually senses it.

---

## NFC Reader Not Detected

**A USB NFC reader is plugged in but does not appear as a device, or the NFC Tags dialog says no reader is detected.**

1. PadForge reads through the Windows **Smart Card** service (`SCardSvr`) over the PC/SC stack. Open `services.msc` and confirm "Smart Card" is running. Windows stops it automatically when the last reader is unplugged.
2. Use a **PC/SC contactless reader (CCID)**, such as the ACR122U. Readers without a PC/SC driver do not enumerate.
3. A reader plugged in after launch is picked up automatically. PadForge retries roughly every 5 seconds, so wait a moment.
4. Register a tag before mapping it: open the **NFC Tags** dialog via **Register / Manage NFC Tags**, tap the tag on the reader, name it, click **Register**. Each registered tag becomes a bindable button.
5. An unregistered tag only pulses the "Any NFC Tag" button, not a per-tag button. Register the specific tag to bind it on its own.
6. PadForge reads only the tag **UID** (NTAG21x, MIFARE, amiibo all work). It does not read tag memory, authenticate sectors, or write tags.

---

## Media Keys (Consumer Control) Not Mapping

**Play/Pause, volume, or other media keys on a keyboard or remote do not show up as a mappable source.**

1. The keyboard or remote must expose a media-key device. Windows presents a keyboard's media-key row as a separate Consumer Control device. A basic keyboard without a media row exposes none and is not enumerated.
2. Media keys arrive on a separate path from normal keys. Pick the media-key device itself as the mapping source, not the keyboard.
3. Consumer Control is an **input source only**. PadForge cannot suppress media keys, so they still reach the OS even when mapped. There is no "consume" option for them.
4. Standard media keys have stable mappings. An uncommon usage gets a session-only "Consumer 0xNNNN" slot whose index is not stable across restarts, so re-record those after an update.

---

## Wii Remote IR Pointer Not Working

**A Wii Remote is connected but the IR Pointer source stays centered or does not aim.**

1. The IR pointer needs a **sensor bar or any IR light source** in view of the remote's camera. It reads the two sensor-bar dots. With no dots visible it reports centered.
2. A powered USB sensor bar or a pair of IR emitters both drive it. The bar only needs to emit IR, it carries no data.
3. Aim the remote at the bar. When the camera loses the dots the source relaxes to center and re-acquires when a dot returns.
4. Map **IR Pointer X** and **IR Pointer Y** to stick axes. Tune sensor-bar position, vertical offset, and smoothing on the Pointer tab. Sensitivity is per source, on the mapping row itself.
5. A right Joy-Con's **IR Brightness** source is different. It reports a single cover/proximity value, not an X/Y pointer.

---

## Joy-Con 2 Mouse Not Working

**A Joy-Con 2 is connected but its optical mouse sensor produces no Mouse Motion output.**

1. The sensor rides the custom SDL fork's BLE Switch 2 driver, which is embedded inside `PadForge.exe`. Release builds always carry it. Only a source build running against a stock `SDL3.dll` lacks the driver, and there the source stays silent with no error.
2. Connect the Joy-Con 2 over Bluetooth. The mouse data comes through the wireless Switch 2 path.
3. Map **Mouse Motion X** and **Mouse Motion Y** to stick axes or scroll. Adjust the per-source Sensitivity if the cursor moves too fast or slow.

---

## Battery Level Not Showing

**A controller's battery glyph or percentage is missing on the Devices page.**

1. Battery shows only when the device reports a level. Many wired controllers and some Bluetooth pads report nothing, so no indicator appears.
2. The reading refreshes about every 5 seconds, not every frame. Give it a moment after connecting.
3. An offline device shows no battery. Confirm the green status dot first.
4. If SDL cannot read the battery for the device, PadForge cannot either. There is no manual override.

---

## Controller Won't Auto-Disconnect When Idle

**The idle auto-disconnect timeout is set but the controller never disconnects, or it disconnects too soon.**

1. Idle Disconnect is **off by default** (0). Set a timeout in minutes on the device's Power section to enable it.
2. It only affects **Bluetooth** controllers. A wired (USB) controller has no radio link to drop, so it stays connected even with a timeout set.
3. Xbox, Valve (Steam Controller), and Switch 2 pads receive a direct power-off. Sony pads, the Wii Remote, and other Bluetooth controllers drop their Bluetooth link instead, which needs the controller to report a valid MAC address (Bluetooth pads do). A pad that reports none stays connected.
4. Aiming with the Wii IR pointer or Joy-Con 2 mouse counts as activity, so you are not disconnected mid-use.
5. Charging does not pause the countdown. An idle pad disconnects even while charging, and dropping Bluetooth does not interrupt the charge.

---

## HD Haptic Tones Sound Wrong or Garbled

**Audio routed to a controller's haptic actuator plays beeps fine but speech and music come through as buzz.**

1. This is a hardware limit, not a bug. These controllers (Nintendo Joy-Con and Switch Pro, Steam Controller 2015, Steam Deck, Steam Controller 2026) reproduce sound through haptic actuators, not a speaker.
2. A haptic actuator plays one frequency at a time. PadForge reduces the audio to that one dominant tone plus a volume envelope each tick. Simple alert tones and melodic cues survive. Speech and full music do not.
3. Joy-Con and Pro tones fold into roughly 41-626 Hz. A note outside that band is shifted by whole octaves until it fits, so it keeps its pitch class but not its register. The 2015 Steam Controller and Steam Deck play pitch only, with no working volume, so they feel flatter.
4. DualSense and DualShock 4 do not use this path. They play through their actual speaker. A Wii Remote likewise uses its speaker.
5. Switch 2 (Joy-Con 2, Pro Controller 2) does not play haptic tones. Its actuator is driven for rumble feel only.

---

## Logs and diagnostics

PadForge writes no log files on its own. A healthy session leaves nothing on disk unless you ask for it. Next to `PadForge.exe`:

- `PadForge.xml` holds your settings.
- `crash.log` appears only after a crash. It records the error plus a tail of recent internal diagnostics. This is the file to attach to a bug report.

If PadForge has not crashed there is no `crash.log`, and that is normal.

**Capturing a trace.** For a problem that is hard to reproduce, open **Settings** and find the **Diagnostics** card.

- **Save Snapshot** writes the engine's most recent events to a timestamped file and shows it in Explorer. It works even with logging off, because those events are always held in memory, so it is the right button right after something goes wrong.
- **Keep a Diagnostics Log** records continuously to `diagnostics.log` instead. It stays on across restarts, so use it for something that only appears minutes into a session or on a PadForge that starts with Windows. Turn it back off when you are done.

Both land in the folder PadForge runs from, and the card shows the path.

`PADFORGE_DIAG` still works for benches: set it to a file path before launching and the same trace goes there for that session only.

---

## Quick Reference

| Symptom | Fix |
|---|---|
| No devices | Check USB, cable, Device Manager |
| Detected but no mapping | Assign to slot, check source dropdown |
| No virtual controller in game | Install HIDMaestro / MIDI Services |
| Nintendo slot not in game | Install HIDMaestro. XInput-only games need an Xbox slot |
| Double input | Install HidHide, enable "Hide Devices from Games" |
| BLE controller not hidden | Enable per-device "Hide from Games" and "Hide Devices from Games" in Settings |
| Wrong button mapping | Force Raw Joystick Mode, re-record |
| Opposite buttons vanish | SOCD cleaning. Set Mode to Off or remove the pair |
| No rumble | Overall Gain > 0%, motor strength > 0%, Test Rumble |
| Audio bass rumble flat | Check audio playing, raise sensitivity |
| Bass shakers silent | Check the Bass Shakers status line. Game feedback and Test Rumble route to audio, macro rumble does not |
| Extended controller not in joy.cpl | Install HIDMaestro, verify driver status, restart PadForge |
| Extended FFB silent | Game must send HID PID 1.0 effects, check gain |
| MIDI button dimmed | Install Windows MIDI Services (Win 11 24H2 or later) |
| No MIDI output | Select "PadForge MIDI N" in DAW input |
| No motion in emulator | Enable DSU server, match port, use 127.0.0.1 |
| DSU port in use | Close conflicting app or change port |
| Web controller disconnected | Same network, check firewall, change the port on the Dashboard |
| iOS Safari drops the web controller | Keep Safari in the foreground or install the page as a PWA |
| Remote Link PC not appearing | Same network, enable on both, allow firewall, or connect by address |
| Remote Link pairing fails | Codes must match on both screens, then retry the handshake |
| Remote Link device missing after pairing | Check the pairing is active, assign the shared device to a slot |
| Remote Link feedback or keys missing | Device must support the feature, untick gamepad-only for keys |
| No NFC reader detected | Start the Smart Card service, use a PC/SC (CCID) reader |
| Media keys not mapping | Keyboard needs a media-key device, input only, no suppress |
| Wii IR pointer centered | Aim at a sensor bar or IR source, map IR Pointer X/Y |
| Joy-Con 2 mouse silent | Connect over Bluetooth, map Mouse Motion X/Y |
| Battery not showing | Wired/unsupported devices report none, refreshes every 5 s |
| Won't auto-disconnect when idle | Bluetooth only, off by default, set timeout in minutes |
| Haptic tone garbled on speech/music | Single actuator plays one tone, only beeps and cues survive |
| Profile not switching | Verify exe path, enable auto-switching |
| Sensitivity curve no effect | Check axis (X vs Y), preset not Linear |
| Settings lost | Wait for autosave, check file permissions |
| UAC prompt every launch | Expected. PadForge always runs as administrator. |
| App crashes on start | Check `crash.log` next to PadForge.exe, re-download the exe |
| High CPU | Increase polling interval in Settings |
| Steam conflict | Disable Steam Input or close Steam |
| Macro doesn't fire | All triggers simultaneous, check threshold, mode, and Layer |
| Mouse macro not working | Check axis source, adjust sensitivity |
| Macro won't stop | A Toggle macro releases on the second press. Otherwise disable the macro or slot |
| Keyboard+Mouse not working | Check slot type, add mappings |
| Mouse buttons not registering | Record the button on a mapping row |
| Stick drift after deadzone | Calibrate Center on Sticks tab |
| Flick Stick not turning camera | Map Flick Stick (Right Stick) to Mouse X |
| Volume macro wrong direction | Enable Invert Axis |
| Volume OSD unwanted | Disable Show Volume OSD |
| DualShock 3 not connecting | Pair through PadForge, unplug, press PS over Bluetooth |
| Shift layer stuck or won't engage | Check mode, Delay, Fire on Release, axis threshold, activator online. A Toggle layer releases on a second tap or via Auto-Cancel |
| Impulse Triggers tab missing | Slot needs an Xbox One/Elite/Series pad. DualSense uses the Adaptive Triggers tab |
| Custom Expression macro silent | Watch live preview value. Rising-edge means it must cross 0.5 |
| Touchpad Overlay no input in game | Slot must be PlayStation type. A real DualSense or DS4 in the slot overrides the overlay |
| Touchpad pressure in steps | Synthetic Pressure is on. Turn it off for raw readings |

---

## Related Pages

- [Installation](start/installation.md): First-time setup guide
- [Settings](features/settings.md): Engine and driver configuration
- [Driver Management](features/driver-management.md): Driver installation
- [Dashboard](features/dashboard.md): Engine and driver status
- [Controller Slots](features/controller-slots.md): Virtual controller creation and management
- [Devices](features/devices.md): Device detection and input state
- [Button and Axis Mappings](features/mappings.md): Input mapping configuration
- [Stick Deadzones](features/stick-deadzones.md): Thumbstick deadzone and calibration
- [Trigger Deadzones](features/trigger-deadzones.md): Trigger range and deadzone
- [Force Feedback](features/force-feedback.md): Rumble configuration
- [Macros](guides/macros.md): Triggers and actions
- [Profiles](guides/profiles.md): Per-application profiles
- [DSU Motion Server](reference/dsu-motion-server.md): Motion data for emulators
- [Web Controller](guides/web-controller.md): Browser-based virtual controller
- [Remote Link](guides/remote-link.md): Share a controller between PCs, on your network or across the internet

---

*Last updated for PadForge 4.3.2.*
