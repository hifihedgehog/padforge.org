# Switching from Another Tool

*Moving a working setup from Steam Input, DS4Windows, reWASD or SimHub to PadForge, one game at a time, with a way back at every step.*

Move one game at a time. Keep the old tool, its configuration and the game's bindings until PadForge does everything the game needs, and decide up front which jobs stay with the old tool. These steps follow PadForge's documentation and the other tools' own guides. No full migration was run while writing them, so test each step in your own setup.

Start from what the game should receive: a button, an axis, a key, a motion stream or a feedback effect. A setting with a similar name in two programs is only a place to start. What matters is what happens when you press, hold, release, change layers and reconnect.

<figure class="pf-video">
<video controls playsinline preload="none" width="1920" height="1080"
       poster="/assets/video/padforge-tutorial-switching-from-another-tool-poster.jpg"
       aria-label="Video: switching from another tool, recorded live in PadForge 5.2.1">
<source src="/assets/video/padforge-tutorial-switching-from-another-tool.mp4" type="video/mp4">
<track kind="captions" srclang="en" label="English" src="/assets/video/padforge-tutorial-switching-from-another-tool.vtt" default>
</video>
<figcaption>Export for a backup, Browse Community Configs for a Steam layout, HidHide's Hide Devices from Games, and the controller to rebuild on, recorded live in PadForge 5.2.1 in 59 seconds. The narration is a generated voice, with English captions. <a href="/assets/video/padforge-tutorial-switching-from-another-tool-transcript.txt">Read the transcript</a>.</figcaption>
</figure>

---

## Before you start

### Write down the old setup

| Record | What to note | Why |
|---|---|---|
| Input | The controller model, and USB, Bluetooth or the adapter it uses | To reconnect the same way |
| Output | The controller type the game sees, Xbox, PlayStation or a custom shape | To give the game the identity it bound |
| Automation | Rules that load a layout when a game starts, startup tasks, tray agents | So the old layout cannot come back unnoticed |
| Feedback | Rumble settings, audio outputs and the game's own settings | To compare the same effect in both setups |

Also note the game's executable, its in-game bindings and the old tool's exact version.

### Back up both sides

Back up the old tool the way its documentation describes. For PadForge, export the profile you are working on (**Export…** on the Profiles page), then exit PadForge from its tray icon before copying its folder and `PadForge.xml`. With **Close to System Tray** on, closing the window leaves PadForge running. An exported profile and a copy of the folder protect different things, so keep both.

Keep these backups private. An exported layout can hold program paths, sound packages and references to other files. Note HidHide's allowed programs and hidden devices separately, since importing a profile does not restore them. More: [Share and back up profiles](profiles.md#share-and-back-up-profiles).

### Install only what this game needs

| What the game needs | What PadForge uses | What to check |
|---|---|---|
| A gamepad | HIDMaestro, installed with the first virtual controller | The game sees the controller you picked |
| The physical pad hidden | HidHide, with PadForge allowed | PadForge still reads the pad |
| Keyboard and mouse output | Windows input, or one of HIDMaestro's keyboard and mouse models | The game accepts it |
| A DualShock 3 over Bluetooth | BthPS3, installed at the first pairing | The pad pairs and reads |
| MIDI | Windows MIDI Services, or the legacy MIDI API with an existing port | Which one the Settings card names |
| VR hands | SteamVR | The game accepts the virtual hands |

The composite Sony, Nintendo and Valve presets also use usbip-win2's virtual USB host controller, which HIDMaestro installs with the first such controller, with no prompt and no USB restart. That is separate from the old tool's ViGEm, vJoy or VIIPER driver. More: [Requirements](../start/installation.md#requirements) and [Driver Management](../features/driver-management.md).

---

## Give every input one owner

Start the game with the old tool stopped and only PadForge's output on. Otherwise the game can read your physical controller and the virtual one, or two virtual ones, and a menu that moves twice per press is the sign.

1. Check the controller on the [Devices](../features/devices.md) page before you touch any mapping.
2. With HidHide, make sure PadForge is allowed and the physical pad is hidden from the game. A copy of PadForge in another folder needs its own entry.
3. Hide the pad before the game starts. A program that already has the pad open keeps it until the pad reconnects.
4. Leave the old tool's drivers installed during the trial. Closing a program, turning off a mapping and uninstalling a driver are different things, and uninstalling is not an easy way back.

To remap a few keys without hiding a whole keyboard, use **Consume Mapped Inputs (Hooks)**. It swallows only the mapped keys and mouse buttons, on every keyboard and mouse at once, since Windows does not say which device a key came from. More: [Input hiding](../features/devices.md#input-hiding).

## Rebuild in layers

Build from the bottom up, and save after each stage that works:

1. Add the controller type the game needs on the Dashboard, assign your physical controller, and check its live values on Devices.
2. Map the plain controls first: buttons, sticks at rest and full travel, each trigger on its own.
3. Add [shift layers](shift-layers.md). Test entering and leaving each one before you hang actions on it.
4. Add [macros](macros.md) last. Decide whether each macro's trigger is the virtual controller's output or the physical device's own input. An extra button on your pad can be a trigger even when the virtual controller has no button for it.

Match the behavior, not the numbers. **On Press** fires at once, while **On Single Press** waits to rule out a double press. A row in **Toggle** mode holds its output until the next press. A latched macro that pulses and a **Repeat Key While Held** action stop at different moments. Copy the old sensitivity values only as notes for calibrating again. More: [Fire modes](macros.md#fire-modes).

A pedal that only changes what other buttons do belongs in a layer activator, and the buttons whose meaning changes belong on that layer. Test the pedal alone, the button alone, both together, and both orders of release.

---

## From Steam Input

### Capture the layout

Note the game's Steam Input override and the exact layout it uses. Write down every action set, action set layer, mode shift, gyro engage, menu, chord, and long or double press, plus the game's own bindings page. List Steam overlay and client commands separately from game controls.

Separate ordinary outputs from Steam's native game actions. A binding that ends in a key press or a gamepad button can move to PadForge. A named action that only a Steam Input game understands has no PadForge equivalent, so keep Steam Input for it if the game offers no ordinary binding.

### Import it or rebuild it

PadForge can translate a Steam community layout. Turn on **Community Configs** in Settings, after reading what it sends to Steam, and browse from the Profiles page. A private layout you do not want to publish is a manual rebuild. More: [Steam Workshop Config Import](steam-workshop-import.md).

Read every **Clean**, **Partial** and **Skipped** line before you save. Extra action sets become shift layers, and translated outputs can create Xbox and Keyboard + Mouse slots, so assign your controller to the slots the import made. The report is a translation account, not a play test: native game actions and some Steam client commands are skipped, and mouse smoothing, movement threshold and trackball friction can drop without a note. More: [The translation manifest](steam-workshop-import.md#the-translation-manifest).

| Steam Input | In PadForge | Test |
|---|---|---|
| A button or axis binding | A mapping row | Rest, full travel and release |
| An extra action set | A shift layer | Entering, priority and leaving |
| A chord or timed press | A macro trigger and fire mode | The press window, interruptions and release |
| A native game action | No equivalent | Keep Steam Input if the game has no ordinary binding |

### Test it, then keep it or go back

Turn off the game's Steam Input override before launching, so Steam and PadForge do not both remap the controller. Some games want Steam Input on for their own DualSense features, so check the game's guidance.

Test normal play, menus, every action set change, gyro engage and recenter, radial and touch menus, and tap against hold. Test entering and leaving gameplay, since a game can change action sets on its own.

To go back, leave the game, exit PadForge from the tray, restore your hiding choices and the game's Steam Input override, and select the original layout. Keep the PadForge profile for later.

---

## From DS4Windows

### Know your build

DS4Windows comes in several forks. Note where yours came from and its exact version, and whether it runs on ViGEm or on the newer VIIPER backend. Back up its profiles, settings and Auto Profiles as its documentation describes. Write down the output type, touchpad mode, gyro mode, special actions, deadzones, trigger curves, HidHide permissions, and any DSU server and port an emulator reads motion from.

For the trial, close the game and exit DS4Windows, plus any separate VIIPER tray program your fork runs. Keep the drivers installed. PadForge's HIDMaestro carries its own usbip-win2 host controller and moves only one it installed itself, so another program's driver keeps its version.

### Rebuild it

Make a new PadForge profile and start from the controller type the game expects. Xbox, a plain PlayStation preset and a Full Sony preset with audio each carry different things to the game. A Full preset does not give your controller a touchpad, pressure buttons or adaptive triggers it does not have.

Rebuild buttons and sticks first, then the touchpad, then gyro, then shift modifiers, and special actions as macros. A gyro engage only opens the gate. The gyro still needs somewhere to go, such as **Mouse X** and **Y** or the aiming stick. More: [Output routing](gyro.md#output-routing).

For an emulator that reads motion over DSU, turn on the DSU server and keep the emulator's host, port, slot and sensor settings. PadForge serves slots 1 to 4 while the engine runs, whatever the slot's preset. More: [DSU Motion Server](../reference/dsu-motion-server.md).

| DS4Windows | In PadForge | Watch for |
|---|---|---|
| A special action | A macro on the slot | Whether the trigger is the physical pad or the virtual output |
| A shift modifier | A layer activator | Held, toggled and release behavior |
| Gyro to mouse | Gyro mapped to Mouse X and Y | Engage and destination are separate |
| Auto Profiles | A profile's game executables | A window-title rule has no exact match |

### Test it, then keep it or go back

Check that one press makes one action, both triggers return to rest, touchpad touches release, gyro turns the right way, and macros stop when they should. Restart the game after changing the controller type it sees. Test ordinary rumble, trigger motors, adaptive resistance, speaker sound and haptics one at a time, when the game uses them.

To go back, leave the game, exit PadForge from the tray, restore the HidHide permissions, and start your DS4Windows build and its backend again with the saved profile.

---

## From reWASD

### Capture the config

Back up the `.rewasd` config and its profile folder, from **Open file location** in reWASD's options. In reWASD a profile is a folder and a config holds the mappings, so note both names. Open every activator, layer and sub-config, and write down the device groups and their members, the virtual output type, shortcuts, combos, muted controls and Autodetect rules.

For the trial, use reWASD's [Tray Agent](https://help.rewasd.com/interface/tray-agent.html) to turn **Remap** off for all devices, then exit reWASD so [Autodetect](https://help.rewasd.com/basic-functions/autodetect.html) cannot load a config when the game gains focus. PadForge has no `.rewasd` importer, so this is a rebuild. Keep the old config untouched.

### Rebuild it

Assign every physical device in the old group to the PadForge slot and check each one alone. Several devices can feed one virtual controller. More: [Mappings](../features/mappings.md).

Rebuild the main controls before layers and combos. Use a mapping row for plain remaps and thresholds, a shift layer for alternate controls, and a macro for sequences and timed presses. Check that the original key a control used is suppressed, separately from checking the new output.

If the old setup used reWASD's virtual keyboard or mouse, a Keyboard + Mouse slot can type and point through one of HIDMaestro's 51 keyboard and 52 mouse models instead of Windows input. Those models have not yet been run against a game, so test the game with each path. More: [Controller Slots](../features/controller-slots.md).

For a soft press and a full press on an analog key, decide whether the soft action should stay on at full depth. The [Analog Keyboards](../features/analog-keyboards.md) page shows both ways.

| reWASD | In PadForge | Match |
|---|---|---|
| A device group | Several devices on one slot | Which device sends what, and pressing them together |
| A shift or activator | A layer and its activator | Entering, releasing, what carries over, priority |
| A combo | Macro actions and a fire mode | Timing, repeat, interruption and latches |
| A muted original control | Consume Mapped Inputs (Hooks) or hiding | The exact original input |

### Test it, then keep it or go back

Test each device alone, then a chord across devices. Check sticks and triggers at rest, partway and at full travel. Turn on the profile's game executables only after loading it by hand works, then move focus in and out of the game and check that the old reWASD config does not come back.

To go back, leave the game, exit PadForge from the tray, restore hiding and startup settings, open reWASD, select the saved config and turn **Remap** on.

---

## From SimHub

### Decide which signal you want

PadForge's [Bass Shakers](../features/bass-shakers.md) turns the rumble and force feedback a game sends to a virtual controller into tones on an audio output. SimHub's ShakeIt makes effects from telemetry such as RPM, suspension or wheel slip. Those are different signals. Move only the effects that should follow game rumble, and keep telemetry effects, dashboards and other SimHub work in SimHub.

Back up SimHub's folder and effect profiles, and export its sound card mappings on their own, since SimHub's [copy guide](https://github.com/SHWotever/SimHub/wiki/Copy-Simhub-configuration-to-another-computer) says they do not travel with the effect profiles. Note the playback device, channels, gains, frequencies and amplifier settings.

### Set up a separate trial

Use one dedicated shaker output for the comparison, and turn off SimHub's output for it while you test.

1. Build the virtual controller the game will use. Xbox is the starting point for gamepad rumble. A wheel needs an Extended layout the game binds, and the game has to send force effects to it.
2. On the slot's Bass Shakers tab, turn on **Route Rumble to an Audio Output**, pick the **Output Device** and **Channel Mode**, and start with low software and amplifier gain.
3. Use a voice's **Test** or the **Frequency Sweep** to check the route before starting the game.

PadForge offers Mono and Controller Stereo routing. A multichannel SimHub setup needs its own channel plan.

### Test it, then keep it or go back

The test tones play on their own and do not move the incoming feedback meters. After the tone works, trigger a repeatable game event and watch the meters while you feel the shaker. Run the old and new setups separately for the same event.

If feedback stops when you touch the keyboard or mouse, the game may have switched input methods. **Keep Controller Awake** works around that in some games. More: [Controller Slots](../features/controller-slots.md).

To go back, turn off PadForge's audio routing, restore the game's bindings, and turn SimHub's saved sound device and channel map back on.

---

## Motion and feedback are separate routes

For each advanced need, write down the whole route: the physical source, how it connects, the PadForge source, the virtual preset, what the game reads, and the expected result. A gyro can move in PadForge while the chosen preset carries no motion to the game, and a DSU emulator can get motion while the game gets none.

Check ordinary rumble, Xbox trigger motors, DualSense trigger resistance, speaker sound and haptics one at a time. The Xbox 360 preset carries no trigger motor effects. Playing adaptive trigger vibrations on Xbox trigger motors does not recreate trigger resistance. Audio mirroring captures a Windows output, while a Full Sony preset gives the game its own controller speaker, so note which one the game uses before chasing silence. More: [Impulse Triggers](../features/impulse-triggers.md) and [Controller Audio](../features/controller-audio.md).

## Moving a profile to another PC

Export the finished profile and check what travels with it. The sound and icon packages its macros and menus use go along. Loose images, programs and executable paths do not. Import adds the profile without loading it, and adds a number if the name is taken.

Before loading it on the other PC, install what it needs and reconnect the controllers, then check the assignments, audio outputs and game paths. Remote Link identity travels separately: a copied identity can move a pairing, but two PCs running the same identity at once cannot see each other. More: [Identity protection](remote-link.md#identity-protection).

Keep a copy of the profile before opening it in an older PadForge. An older build that does not know a newer mode, such as Rapid Trigger or Toggle, can lose that row's input when it saves.

## Checklist

| Check | Do | Pass when |
|---|---|---|
| One input | Press and release once | One action and a clean release |
| Axis range | Rest, partway, full travel | The expected center, range and direction |
| Layers | Enter, use and leave each one | Nothing stays held that should not |
| Macros | Fire, interrupt, disconnect | No key, button or axis left held |
| Feedback | Trigger one known game event | The motor, speaker or trigger responds |
| Profile | Load it, switch focus, restart | The right profile loads and keeps its setup |
| Reconnect | Reconnect the controller | The same route comes back |
| Way back | Restore the old setup | The original behavior returns |

Mark a check "not tested" when you lack the hardware or the game. When a required behavior fails, stop adding and keep the last working stage, or restore the old setup. Click **Save Snapshot** right after a failure and note the time and the exact step. More: [Logs and diagnostics](../troubleshooting.md#logs-and-diagnostics).

---

*Last updated for PadForge 5.2.0.*
