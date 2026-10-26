# Frequently Asked Questions

*The questions people ask most about PadForge, answered in short, with a link to the full story.*

---

## Getting started

### Does PadForge cost anything?

No. PadForge is free, with no subscription, no paid tier and no nag screens. Controllers, adapters, games and any optional third-party software cost what they cost.

### Which versions of Windows does PadForge run on?

Windows 10 and 11 on x64. Every release also carries a preliminary native build for Windows 11 on ARM64, which has not run on ARM64 hardware yet. Razer Sensa HD haptics, Logitech G-keys and the VR headset and controllers through SteamVR are missing from it until their vendors ship ARM64 libraries. More: [Windows on ARM](start/installation.md#windows-on-arm-preliminary).

### Can I stream, record or use PadForge at work?

Yes. Playing games with PadForge, streaming them, recording videos and using it on a work machine draw no license action. The license's NonCommercial term covers the software itself: it stops anyone from redistributing PadForge, modified or not, for profit. The maintainer said so in [discussion #304](https://github.com/hifihedgehog/PadForge/discussions/304), and [LICENSE](https://github.com/hifihedgehog/PadForge/blob/main/LICENSE) holds the full terms.

### Is PadForge portable? What does another PC need?

PadForge is one executable in a ZIP, and it keeps its settings in `PadForge.xml` beside it, so the folder moves as a unit. Drivers do not travel with it. Each PC installs HIDMaestro the first time a virtual controller is created there, and hiding, MIDI, Bluetooth DualShock 3 input and VR each bring their own installs. More: [Requirements](start/installation.md#requirements).

### Can PadForge import my DS4Windows, reWASD or SimHub setup?

No. PadForge imports its own profile packages and translates supported Steam community layouts, but it reads no DS4Windows, reWASD or SimHub file. Rebuild the setup in PadForge one game at a time, and keep the old tool until the new setup does everything the game needs. More: [Switching from Another Tool](guides/switching.md).

### I hid my controller, but the game sees no controller at all. What should I check?

An empty slot creates nothing. Start the engine, turn the slot on and assign an online device to it, then reopen any game that only looks for controllers at startup. A failed HIDMaestro setup leaves "Error: Failed to initialize HIDMaestro." in the status bar, and it runs again when you turn the slot off and on, change its type or profile, or reconnect its controller. More: [Extended Controllers Not Working](troubleshooting.md#extended-controllers-not-working).

### Does an automatic update replace PadForge while it is running?

No. With **Install Updates Automatically** on, PadForge downloads the update and installs it at the next launch. **Install and Restart** installs it now and restarts. Versions 4.5.3 and later update from the Updates card in Settings, while 4.5.2 and older need one manual download. More: [Updates](features/updates.md#the-switches).

### What is the difference between Close to System Tray and Always Show in System Tray?

**Close to System Tray** keeps PadForge running when you close the window with the X or Alt+F4. **Always Show in System Tray** keeps the tray icon there while the window is open, so **Exit** in its menu is always one click away. Use **Exit** in the tray menu to quit for real. More: [Settings](features/settings.md#window).

### Are Idle Disconnect and Inactivity Timeout the same timer?

No. **Idle Disconnect** is a per-device setting, in minutes, that tells a supported controller to switch off its radio after sitting idle. **Inactivity Timeout** is a global setting, in seconds, for how long a virtual controller stays after every device assigned to it goes offline. Set it to 0 to keep the virtual controller indefinitely. The slot's setup survives either way, and the virtual controller returns when a device does. More: [Inactivity Timeout](features/settings.md#inactivity-timeout).

### What should I save before resetting PadForge?

Copy `PadForge.xml` and export the profile you are working on first, then note what the symptom looks like. **Reset to Defaults** removes every virtual controller, mapping and saved profile without asking, and once it is gone nobody can tell what caused the problem. When PadForge cannot read `PadForge.xml` at startup, it keeps a copy named `PadForge.xml.unreadable-` plus the date and time beside it and starts with defaults. More: [Settings Not Saving](troubleshooting.md#settings-not-saving).

### There is no crash.log. What helps a bug report?

Click **Save Snapshot** right after the problem happens, or turn on **Keep a Diagnostics Log** before reproducing a longer one. Add the PadForge build, the controller and how it connects, the virtual preset, the active profile, and the game or program that misbehaved. A missing crash.log does not mean nothing went wrong. More: [Logs and diagnostics](troubleshooting.md#logs-and-diagnostics).

---

## Devices and virtual controllers

### Do sixteen slots mean sixteen Xbox controllers in every game?

No. Sixteen is the total across every slot type: Xbox, PlayStation, Nintendo, Extended, Keyboard + Mouse, MIDI and VR. A game that uses XInput sees only the first four Xbox controllers, while SDL and DirectInput games see all of them. More: [Slot limits](features/controller-slots.md#slot-limits).

### Why does Steam or Windows still react to a controller after Hide from Games is on?

Hiding applies when a program opens a device, so a program that already had the controller open keeps it. When PadForge hides a USB controller that is already connected, it reconnects it in Windows so those programs lose it. A Bluetooth controller, or a receiver that carries several controllers, stays with whatever opened it until it next connects, so reconnect that one yourself. **Keep Devices Cloaked Between Launches** keeps the hides in place while PadForge is closed. More: [Input hiding](features/devices.md#input-hiding).

### Do I have to hide a whole keyboard to remap a few keys?

No. **Consume Mapped Inputs** swallows only the keys and mouse buttons you mapped and leaves the rest working. Windows does not say which keyboard a key came from, so consuming a key consumes it on every keyboard. PadForge's own output is never consumed. More: [Input hiding](features/devices.md#input-hiding).

### Does picking a preset unlock every control on my controller?

No. The preset decides what the game sees. What PadForge can read from your controller depends on the controller and how it connects. A matching name on both sides does not by itself carry pressure, touch, paddles, motion or feedback through, so check the controls you need. More: [Controller Slots](features/controller-slots.md).

### A virtual controller works in a tester but not in an older game. What should I check?

Older games can bind one joystick by its position in the list, or expect particular DirectInput axes. Keep the exact preset and, on an Extended slot, the same axes, triggers, buttons and hats. Choosing the preferred device in `joy.cpl` has fixed some games. More: [Virtual Controller Not Appearing in Games](troubleshooting.md#virtual-controller-not-appearing-in-games).

### Does Force Raw Joystick Mode lower latency?

No. It exists to skip a standard gamepad layout that reads a device wrong, and to show its raw buttons and axes. It also turns off auto-mapping, so existing mappings can land on the wrong inputs. Turn it off again if a controller starts misbehaving after you enabled it. More: [Force Raw Joystick Mode](features/devices.md#force-raw-joystick-mode).

### I removed a controller and it came back without its mappings. Why?

**Remove Device** deletes that device's mappings, assignments and hiding settings, and a device that is still connected shows up again at the next scan as a new record. To keep a controller's setup while it is away, unplug it instead. PadForge remembers an offline device. More: [Removing a device](features/devices.md#removing-a-device).

### Does a controller's Player Number light mean the game sees it as player one?

No. The light follows PadForge's numbering of its virtual controllers. Games number XInput controllers themselves, and other controllers on the PC can change that order. More: [Lighting](features/lighting.md#indicator-leds-dualsense).

### Does hiding a device in the mapping picker delete its bindings?

No. The picker's device filter only narrows the inputs offered, and the mappings stay as they are. The filter is saved per slot, outside profiles. The search box filters rows for the current session only. More: [Mappings](features/mappings.md).

### What do the Xbox Elite paddles need?

Over USB or the Xbox Wireless Adapter, the paddles read through Windows' GameInput service, which needs Windows 11 24H2 or 25H2 at build 26100.8973 or 26200.8973 or later. The GameInput redistributable is not needed. An Elite Series 2 over Bluetooth uses its own path on any Windows, and the first Elite has no Bluetooth. Each paddle is its own input, separate from the Xbox buttons. More: [Xbox Elite Paddles Do Nothing](troubleshooting.md#xbox-elite-paddles-do-nothing).

### Can my mouse or keyboard light up and rumble with a virtual controller?

Yes, once it is assigned to a virtual controller on the Devices page. Check **Control This Device’s Lighting** on its **Lighting** tab and it takes the controller's lighting. PadForge lights Logitech, Razer and SteelSeries devices itself while their own software is closed, and through that software while it runs. It also lights any device Windows Dynamic Lighting can drive, while Dynamic Lighting is off for that device. Rumble reaches the Logitech MX Master 4, the SteelSeries Rival 500, 700 and 710 through SteelSeries GG, and Logitech's iFeel mice after a driver switch, which stops Windows using the mouse as a pointer until its driver is restored. More: [Mice, Keyboards and Vendor Rows](features/peripherals.md).

### Does a MIDI slot need Windows MIDI Services?

No. Without it, PadForge uses the legacy MIDI API that every Windows has, and each MIDI slot sends to an existing port you pick on the slot's page. With it, each MIDI slot gets its own port that any music app can open, named PadForge MIDI 1, PadForge MIDI 2 and so on. Microsoft removed its runtime installers on October 1, 2026, so on Windows 11 24H2 and later, until Windows carries the API itself, **Install** on the Windows MIDI Services card in Settings adds PadForge's own build of the runtime. More: [Windows MIDI Services](features/driver-management.md#windows-midi-services).

---

## Mappings

### Why is there no Triggers tab on a Keyboard + Mouse slot?

That tab tunes the analog triggers a virtual gamepad sends, and a Keyboard + Mouse slot sends none. When a physical trigger drives a key, set where it presses with the row's **Axis-to-Button Deadzone**. More: [Axis-to-Button Deadzone](features/mappings.md#axis-to-button-deadzone).

### Button 0 maps to the first virtual button. Is that off by one?

No. Raw source names count from zero, while virtual outputs follow the numbering Windows and games show, which starts at one. Check which output actually presses before reading the labels as a mistake. More: [Clone Device 1:1](features/mappings.md#clone-device-11).

### Why does an (Any Device) Gamepad row ignore my mouse, raw joystick or head tracker?

**Gamepad** sources name inputs by their role on a standard gamepad, so only devices PadForge recognizes as gamepads answer them. A keyboard, a mouse, an unmapped joystick or a pad in Force Raw Joystick Mode does not. Head trackers, microphones, pens, VR controllers and G-keys have named inputs of their own. More: [Gamepad sources](features/mappings.md#gamepad-sources).

### How do I make a touchpad act like a thumbstick that recenters on release?

Turn on **Stick / D-Pad Output** on the Touchpad tab and map **Touchpad Stick X** and **Y** to the stick. Where the finger lands becomes the center, and moving away from it pushes the stick. **Max Radius** and **Inner Deadzone** set its travel and rest. More: [Touchpad](features/touchpad.md).

### Should mouse steering use Mouse Speed, Mouse Position or Ramp?

**Mouse Speed** reads how fast the mouse moves. **Mouse Position** reads where the cursor sits relative to the center of the main screen, reaching full deflection at 10% of the screen width by default. **Ramp** ignores the mouse and moves the axis while its Up or Down key is held. Each one gives a resting mouse a different meaning, so pick the one that matches the game. More: [Mappings](features/mappings.md).

### Why does an axis picked as a Ramp or Incremental key do nothing?

Those modes read their own Up and Down keys, and a key has to be an on/off input: a button, a hat direction, a stick ring, a gesture, a menu cell, a MIDI note or CC, and the like. The pickers offer only inputs that work as keys, so a stick, trigger or slider is not listed. A key saved by an older version from such an axis reads nothing until you pick a new one. More: [Source kinds](features/mappings.md#source-kinds).

### Does Rapid Trigger change my keyboard's firmware?

No. It is a mode on a mapping row that reads how deep the key is. One **Distance**, 1 to 50 percent of travel and 10 by default, sets both the release and the next press. Separate press and release distances and Continuous Rapid Trigger are not offered. More: [Source kinds](features/mappings.md#source-kinds).

### How can one press hold aim without a macro or a shift layer?

Set the aim row's **Primary Mode** to **Toggle**. One press holds the output and the next lets it go. A trigger holds a full pull, a button stays pressed, and a stick holds full deflection. The hold ends when the row stops running, such as when its layer closes or its device goes offline. More: [Source kinds](features/mappings.md#source-kinds).

### My mapping grid is blank. Were my mappings erased?

Not necessarily. Save `PadForge.xml` and note the active profile before you reset or import anything. Then check which slot and device are selected, and whether the output still works. A blank grid has come from a stale picker, from parked settings, and from real data loss, and only the saved file tells them apart. More: [What a profile holds](guides/profiles.md#what-a-profile-holds).

### Does copying a slot keep every row across controller types and PCs?

Between slots with the same layout, such as an Xbox slot and a PlayStation slot, everything copies: rows, layers, menus and SOCD pairs. Between different layouts, the Base layer's bindings carry over by position or by role, and the target keeps its own layers, menus and SOCD pairs. A Bass Shakers route copied to another PC stays silent until you pick one of that PC's audio outputs. More: [Copy, Paste, Copy From](features/mappings.md#copy-paste-copy-from).

---

## Macros, layers and profiles

### How do I send a keyboard shortcut from a controller chord in one game only?

Load that game's profile, add a macro on its slot, and pick the chord as the trigger, from the virtual controller or from the assigned devices. Add a **Key Press** action with the shortcut. Macros belong to their profile, so the shortcut runs only while that profile is active. **Consume Trigger Buttons** keeps the chord's buttons out of the game. More: [Triggers](guides/macros.md#triggers).

### Why does On Single Press wait when On Press does not?

**On Press** fires as soon as the trigger goes down. **On Single Press** waits through the **Press Window**, 442 ms by default, to be sure no second press is coming. **On Short Press** fires on release before the **Hold Time**, and **On Long Press** fires once the hold passes it, 500 ms by default. Pair a Short and a Long macro on one trigger to get tap and hold. More: [Fire modes](guides/macros.md#fire-modes).

### Can autofire keep going after I let go of the trigger?

Yes. Use a **Toggle Button**, **Toggle Key**, **Toggle Mouse Button** or **Toggle Axis** action with **Pulse While Latched**. One press starts the repeating output and the next stops it. **Repeat While Held** and the **Turbo** fire mode stop when you let go. More: [Toggle Button / Toggle Key](guides/macros.md#toggle-button-toggle-key).

### Why does Text Block type in a chat box but not move my character?

**Text Block** sends text as characters, which chat boxes accept and many games' movement controls ignore, since those read the keys' up and down state. Use **Key Press** for keys a game reads as controls. More: [Text Block](guides/macros.md#text-block).

### Can Limit Mouse Region keep a game's cursor inside its rectangle?

Not against the game. **Limit Mouse Region** and **Fix Mouse Position** move the cursor back every frame, and a game that moves the cursor too can fight them. More: [Limit Mouse Region](guides/macros.md#limit-mouse-region).

### What does Switch Layer do when it goes back to Base?

Switching to Base releases toggled and sticky layers. A Hold activator that is still held engages its layer again on the next update. More: [Switch Layer](guides/macros.md#switch-layer).

### A Hold layer driven by a trigger stays on at rest. Is that normal?

No. A Hold layer should follow its input. Check the activator's source, threshold, **Mode**, **Delay** and **Fire on Release**, and remember that a trigger rests at zero while a stick rests at its center. More: [Activator kinds](guides/shift-layers.md#activator-kinds).

### Can one profile cover many games?

Yes. Add each game's executable to one profile and turn on auto-switching. The profile loads when any of them comes to the front, and Default returns for everything else. More: [Auto-switch on app focus](guides/profiles.md#auto-switch-on-app-focus).

### Should a launcher like Playnite edit PadForge.xml to pick a profile?

No. Turn on **Allow External Control by Launchers and Scripts** on the Profiles page, and have the launcher send `activate <name>` to PadForge's `PadForge.Control` pipe before the game starts and `deactivate` after it closes. Auto-switching leaves the profile alone until then. More: [External control from launchers and scripts](guides/profiles.md#external-control-from-launchers-and-scripts).

### Can two players switch profiles independently?

No. A profile holds every slot, mapping, macro and menu at once, so switching it changes them together. Two players can still use different slots with different mappings inside one profile. More: [What a profile holds](guides/profiles.md#what-a-profile-holds).

### Does a profile's polling rate change each controller's rate?

No. It replaces the engine's polling interval while the profile is active, and every slot shares that loop. A controller's own USB report rate does not change. More: [Polling rate override](guides/profiles.md#polling-rate-override).

---

## Motion and gyro

### The gyro moves on screen, but holding the aim trigger does not turn the camera. What is missing?

The engage trigger decides when gyro is on, and the mapping table decides where it goes. Map the gyro to **Mouse X** and **Y** for a mouse-aimed game, or to the aiming stick for a controller-aimed one. With both **Easy Aim** and an aim engage set, both have to be active. More: [Output routing](guides/gyro.md#output-routing).

### Which input keeps steering while I hold the controller tilted?

**Gyro Tilt X** and **Y**. They hold their deflection for as long as the controller stays tilted, across a range of angles you set. **Gyro Pitch**, **Yaw** and **Roll** report turning speed and fall back to zero when the turning stops. More: [Gyro Tilt](guides/gyro.md#gyro-tilt).

### Does a Nintendo virtual controller need a physical gyro?

No. **Motion Pitch**, **Yaw** and **Roll** rows make motion from any input, a stick or buttons included. The game gets it through presets whose reports carry motion. The plain Switch 2 Pro preset carries none, while **Nintendo Switch 2 Pro Controller: Full** carries both sensors for Steam and SDL built with libusb. More: [Motion Pitch, Yaw and Roll](features/mappings.md#motion-pitch-yaw-and-roll).

### Are Momentum and Flick Stick the same thing?

No. **Momentum** lets the mouse cursor coast after a flick on a touchpad or a mouse stick. **Flick Stick** turns the camera to wherever the stick points and keeps turning as the stick rolls around its rim, and it needs the game's **Dots per 360** calibrated. More: [Flick Stick](features/stick-deadzones.md#flick-stick).

### Does reading an OpenXR headset put input into my VR game?

No. PadForge reads the headset and its controllers through the OpenXR runtime as input for your mappings. It does not create a headset or join a VR game's session. A Quest on Link has to go through SteamVR's runtime. More: [Setting up an OpenXR headset](features/head-tracking.md#setting-up-an-openxr-headset).

---

## Rumble, triggers and audio

### Does the rumble meter prove the motor moved?

No. The meter shows what PadForge sends. **Test Rumble** on the device is the check that the motor itself moves. More: [Force Feedback](features/force-feedback.md).

### Body motors work, but the Xbox trigger motors get nothing from the game. Why?

The game has to send trigger rumble, and the slot has to carry it. That needs an Xbox One, Elite or Series virtual profile, since the Xbox 360 path carries the body motors only. The controller you hold also needs trigger motors. More: [Impulse Triggers](features/impulse-triggers.md).

### Can Xbox trigger motors play DualSense adaptive trigger effects?

Partly. **Translate Adaptive Trigger Vibrations**, a per-device setting that is off by default, plays a virtual DualSense's vibration effects on an Xbox controller's trigger motors. Resistance effects have nothing to play on and are left out. More: [Impulse Triggers](features/impulse-triggers.md).

### How do a game's own DualSense haptics differ from audio mirroring?

A game that supports the DualSense sends its own haptics and speaker sound to a virtual DualSense that carries audio. Mirroring is separate: it captures a Windows audio output and plays that sound on the controller. Speaker sound, rumble, trigger effects and haptics are separate things to check. More: [Mirror a Windows audio output](features/controller-audio.md#mirror-a-windows-audio-output).

### Will a longer Bluetooth audio buffer fix every crackle?

No. **Bluetooth Audio Buffer Length** sets the DualSense's Bluetooth buffer, shared by speaker, haptics and microphone. Mirroring and other paths have their own queues. Work out which sound path crackles before changing it. More: [DualSense headset jack](features/controller-audio.md#dualsense-headset-jack).

### Why does Bluetooth drop when I plug in USB, with Quick Charge off?

A DualSense connected over both Bluetooth and USB mutes its USB audio, so PadForge drops the Bluetooth link once when it sets up wired audio. **Quick Charge** is separate: it drops Bluetooth when the controller starts charging. More: [DualSense headset jack](features/controller-audio.md#dualsense-headset-jack).

### Do Bass Shakers play the soundtrack or simulator telemetry?

Neither. Bass Shakers turns the rumble and force feedback a game sends to a virtual controller into tones on an audio output you pick. On a DualSense (PS5): Full or DualSense Edge (PS5): Full virtual controller, it also follows the haptics a game plays through the controller's audio. Macro rumble stays on the controller. More: [Rumble to Audio card](features/bass-shakers.md#rumble-to-audio-card).

### Why does Constant Force pull my wheel to one side?

**Constant Force** applies a fixed push in one direction, wherever the wheel points. **Auto Centering Strength** on the Wheel tab is the spring that returns it. On the generic force feedback path the two share one effect, so turning on Constant Force stops the spring. More: [Constant Force](features/force-feedback.md#constant-force).

### Why do Keyboard + Mouse and MIDI slots have a Force Feedback tab?

The tab also drives the physical device assigned to the slot. **Audio Bass Rumble** turns the PC's sound into rumble, and **Test Rumble** checks the device, neither of which needs a game. A haptic mouse or the Razer Sensa row gets the tab too. More: [Audio Bass Rumble](features/force-feedback.md#audio-bass-rumble).

---

## Phones, browsers and Remote Link

### Are Browser Gamepad, phone motion and Web Menus the same thing?

No. **Browser Gamepad** forwards a controller paired to the phone. Phone motion reads the phone's own sensors and needs the HTTPS address. **Web Menus** shows a slot's Touch Grid menus as tiles to tap. More: [Browser Gamepad](guides/web-controller.md#browser-gamepad-a-controller-paired-to-the-phone).

### Why does the phone page say Motion needs HTTPS?

Browsers give sensor readings only to pages on a secure connection. PadForge serves the controller over HTTPS whenever it can bind its self-signed certificate to the port. If the binding fails it falls back to plain HTTP, where everything works except phone motion and Browser Gamepad's keep-the-screen-on request, and the Dashboard card says why under its status line. When another program's certificate holds the port, choosing another port brings HTTPS back. A page opened at the plain HTTP address while PadForge also serves HTTPS shows **Motion: open over HTTPS** instead, and tapping it opens the same layout on the secure address. More: [Phone motion](guides/web-controller.md#phone-motion).

### Can the streaming PC assign its web controller to slots on the gaming PC?

Yes, once the gaming PC turns on **Allow Remote Assignment Changes** for that PC. The streaming PC can then move its shared devices between the gaming PC's existing slots. It cannot create controllers, switch profiles or edit mappings. A Web Menus phone is not shared. More: [Assign devices from the other PC](guides/remote-link.md#assign-devices-from-the-other-pc).

### Can two PCs use one Remote Link identity by copying the PadForge folder?

No. A copied identity moves pairings to a new PC, but two PCs running the same identity at the same time cannot see each other. Give each running PC its own identity. More: [Identity protection](guides/remote-link.md#identity-protection).

### Does Remote Link need a port forward or a PadForge server?

No. On a local network the PCs find each other by broadcast. Over the internet, a connection code lets them try a direct path, and n0's free public relays carry the session when no direct path works. A connection code only finds the other PC. The pairing check decides trust. More: [Remote Link](guides/remote-link.md).

### Does Gamepad Only block every non-gamepad action from a remote PC?

No. It blocks keyboard and mouse output, scrolling, cursor moves and VR slots for that PC. **Run Program** and MIDI still work. More: [Staying safe: gamepad-only](guides/remote-link.md#staying-safe-gamepad-only).

---

## Steam community layouts

### Does PadForge pick the best settings for every game automatically?

No. You choose a Steam community layout, check how it translated, and save it as a PadForge profile. That profile can then switch in by the game's executable like any other. More: [Steam Workshop Config Import](guides/steam-workshop-import.md).

### Does Clean in the import report mean the layout was played?

No. **Clean** means a binding translated with the same behavior. It says nothing about a game session, and some tuning values, such as mouse smoothing and trackball friction, are dropped without a note. Test the actions you need. More: [The translation manifest](guides/steam-workshop-import.md#the-translation-manifest).

### What does PadForge send to Steam when Community Configs is on?

Your search text, the ids of the games, configs and creators involved, and PadForge's version. Steam's anonymous logon adds the OS type, a language and a machine id built from hashes of Windows and hardware identifiers. No Steam account or sign-in is used, and nothing goes out until you search or open something. More: [Steam Workshop Config Import](guides/steam-workshop-import.md).

---

## Voice macros

### Do Voice Macros download a model or need the internet?

No. The English Vosk model ships inside PadForge and unpacks on the PC the first time it is used. Windows speech recognition stands in while it unpacks. More: [Voice Macros](features/voice-macros.md).

### Why can't a spoken phrase hold a button?

A recognized phrase is a 175 ms press, not a held key. To make a phrase change something that stays changed, use it as a **Toggle** layer activator. The model is US English, so a word outside its vocabulary cannot fire. More: [Voice Macros](features/voice-macros.md).

---

*Last updated for PadForge 5.1.0.*
