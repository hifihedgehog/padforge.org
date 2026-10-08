# Mice, Keyboards and Vendor Rows

*A mouse or keyboard assigned to a virtual controller takes that controller's lighting and rumble on its own Lighting and Force Feedback tabs, the way a DualSense does. Vendor rows reach the headsets, mousepads, speakers and Razer Sensa HD gear that PadForge does not read.*

---

## Setting one up

A mouse or keyboard assigned to a virtual controller becomes one of its output devices. It gets a **Lighting** tab when PadForge has a way to light it and a **Force Feedback** tab when it can vibrate.

1. On the [Devices](devices.md) page, select the mouse or keyboard and click a virtual controller's number under **Virtual Controller Assignment**.
2. Open that virtual controller from the sidebar and pick the device in the assigned-devices dropdown.
3. On the **Lighting** tab, check **Control This Device’s Lighting** and pick a mode. Rumble is on from the start, as it is for a gamepad.

Settings belong to one virtual controller and one device, so a keyboard on two virtual controllers keeps separate settings for each. Assignments and both tabs' settings belong to the active [profile](../guides/profiles.md), as a gamepad's do. The row that **Read Analog Keyboards** adds for an analog keyboard counts as a keyboard here.

| Brand | How it lights | One color for each | Rumble |
|---|---|---|---|
| Logitech, while neither G HUB nor Logitech Gaming Software runs | Straight over HID++, for mice and keyboards whose only RGB feature is HID++ 0x8070 | Device | MX Master 4, straight over HID++ |
| Logitech, while G HUB or Logitech Gaming Software runs | Through that program's LED engine, for mice and keyboards that report lighting over HID++ | Kind: keyboard, mouse, mousepad, headset, speaker | MX Master 4, straight over HID++ |
| Razer | Through Razer Synapse | Kind: keyboard, mouse, headset, mousepad, keypad, Chroma Link | Sensa HD devices, through the Razer Sensa row |
| SteelSeries | Through SteelSeries GG | Kind: mouse, keyboard, headset | Rival 500, 700 and 710, through SteelSeries GG |

A Razer mouse or keyboard gets its Lighting tab once Razer Synapse is installed, and a SteelSeries one once SteelSeries GG is installed. PadForge finds Logitech devices over HID++ by the features they report, with no model list, and a device it found keeps its tabs while it sleeps. The MX Master 4 gets its Force Feedback tab once PadForge finds its haptic motor, and a Rival 500, 700 or 710 once GG is installed.

---

## Lighting

### Taking over a device's lighting

A mouse or keyboard's Lighting tab opens with a **Control This Device’s Lighting** checkbox, off by default. Assigning a keyboard for its keys never repaints it: until the box is checked, this virtual controller leaves the device's lighting alone. The checkbox's tooltip reads: *Off stops this virtual controller from lighting the device. A vendor row, or another device of its kind lit through the same software, can still set its color. A Set Chroma Color macro on this virtual controller still paints a Razer device.*

The vendor rows have no checkbox. Assigning one is enough.

A device that nothing lights any more goes back to its own lighting, and so does every device when PadForge's input engine stops. PadForge reaches Synapse, G HUB, Logitech Gaming Software and GG only while something assigned needs them.

### Modes

The tab's lightbar card is the one a DualSense gets, without the controller art: all fourteen base modes and the **Input Reactive** overlay. The macro lightbar actions reach the device too. [Lighting](lighting.md) covers every mode and setting. On a mouse or keyboard:

| Mode | What the device shows |
|---|---|
| Player Number (Default) | The virtual controller's player color |
| Off | The device stays dark. To give it back to its own software, uncheck Control This Device’s Lighting instead |
| Battery: Gradient by Charge Level | A Logitech device's charge, read over HID++ whichever software lights it. Razer and SteelSeries software report no charge to PadForge, so their devices and the vendor rows hold the Full Battery color |

### A game's lightbar

On a virtual DualSense, DualSense Edge or DualShock 4, a game that writes the lightbar takes over every device the virtual controller lights, the way it does on a DualSense:

- For 1.5 seconds after each write, the game's color shows over the tab's mode and over a macro's lightbar color.
- A device left at Player Number, with the Input Reactive overlay off and no macro color running, then keeps the game's last color until 15 seconds pass with no output from the game. Then the player color returns.
- A device set to any other mode goes back to it 1.5 seconds after the last write.

No game writes a lightbar to the other virtual controller types, so there the tab's own settings set the color.

### Which software lights which device

Logitech mice and keyboards whose only RGB feature is HID++ 0x8070 light straight over HID++ while neither G HUB nor Logitech Gaming Software runs. PadForge takes the lighting from the device's onboard effect while it lights the device, and hands it back afterward. While G HUB or Logitech Gaming Software runs, that program owns the devices, so they light through its LED engine instead, one color for each kind. PadForge loads the engine the program installed and ships no Logitech code. When PadForge starts painting through the engine, it saves the program's lighting, and it restores that lighting when it stops. Other Logitech mice and keyboards that report lighting over HID++ light through the LED engine, so their Lighting tab shows while G HUB or Logitech Gaming Software runs.

Razer devices light through the Chroma REST server that Razer Synapse runs, one color for each Chroma category: keyboard, mouse, headset, mousepad, keypad and Chroma Link. A Tartarus, Orbweaver or Nostromo lights as a keypad.

SteelSeries devices light through GameSense in SteelSeries GG, one color for each device type: mouse, keyboard and headset. PadForge shows up in GG as a game named PadForge.

### Shared lighting

Synapse, G HUB, Logitech Gaming Software and GG take one color for each kind of device and show it on every device of that kind. Two Razer mice on two virtual controllers show one color between them. When more than one assigned device or vendor row lights the same kind:

1. A device lit from its own Lighting tab beats a vendor row, whatever the virtual controller numbers.
2. Otherwise the lower-numbered virtual controller sets the color.

A device on two virtual controllers follows the same rule: the lower-numbered one sets its color. Devices lit straight over HID++ do not share a color. Each shows the one its own virtual controller sets.

---

## Rumble

A mouse that can vibrate takes its virtual controller's rumble through the Force Feedback tab a gamepad gets, and [Force Feedback](force-feedback.md) covers its settings. Macro rumble reaches it too, and **Test Rumble** plays on the selected device. Each of these devices plays one strength at a time: the stronger of the left and right motors, after the tab's settings. A device on several virtual controllers takes the strongest rumble among them.

| Rumble strength | MX Master 4 | Rival 500, 700 and 710 |
|---|---|---|
| Under 5% | Nothing | Nothing |
| 5% to 32% | Subtle collision waveform | A 30 ms pulse 5 times a second |
| 33% to 65% | Damp collision waveform | A 55 ms pulse 7 times a second |
| 66% and up | Sharp collision waveform | An 80 ms pulse 10 times a second |

A level drops back only once rumble falls 2 to 3 points below the threshold that raised it, so rumble that hovers on a boundary does not flicker between levels.

### Logitech MX Master 4

PadForge plays Logitech's own haptic waveforms on the mouse over HID++ (feature 0x19B0). No Logitech software is needed, and any other Logitech device that reports the same feature plays the same way. The waveform repeats every 250 ms at the faintest rumble and every 80 ms at full strength, and new rumble plays its first pulse at once. When the mouse lacks a level's waveform, PadForge plays the nearest one it has.

PadForge never changes the mouse's haptic settings. With haptic feedback turned off in Logi Options+, the mouse plays nothing until you turn it back on there.

### SteelSeries Rival 500, 700 and 710

These vibrate through the tactile handler in SteelSeries GG, which has to be running. GG drives every tactile Rival at once, so the Rival on the lowest-numbered virtual controller sets the rumble for all of them. When no Rival is assigned any more, the motor stops at once. Two seconds after no Rival is assigned and no virtual controller lights a SteelSeries device or the SteelSeries GG row, PadForge ends its GameSense game and GG's own effects come back.

### Razer Sensa HD

The Razer Sensa row plays rumble on Razer Sensa HD devices such as the Wolverine V3 Pro, the Kraken V4 Pro and the Freyja. It appears on the Devices page once Razer Synapse is installed. Assign it to a virtual controller and it takes that controller's rumble on its Force Feedback tab. Its engine runs only while the row is assigned.

The row plays through the Interhaptics engine and its Razer provider, which ship unmodified inside PadForge, and through Razer Synapse 4 with Sensa HD Haptics. In Synapse, set the device's Haptic Source to Sensa HD Games. A Wolverine V3 Pro renders Sensa only on a PC, in PC mode, with firmware v2.02 or later ([Razer's firmware updater](https://mysupport.razer.com/app/answers/detail/a_id/14630)). Hold Function, Menu and A together for two seconds to switch it to PC mode.

Sensa takes one strength and plays it as one looping effect in the 65 to 300 Hz band, the same on every Sensa device.

### Mice that cannot vibrate

Mice built on Immersion TouchSense, such as Logitech's iFeel mice, cannot vibrate through PadForge. Their vibration report sits in the mouse's own HID collection, which Windows keeps to itself.

---

## Vendor rows

Four rows on the [Devices](devices.md) page stand for output a vendor's software delivers to devices PadForge does not read. Each appears once its software is installed, with **Lighting** or **Haptics** as its type. A row has no inputs, so it adds nothing of its own to a virtual controller's mappings. Assigned to a virtual controller, it takes that controller's lighting on its Lighting tab, or its rumble on its Force Feedback tab.

| Row | Appears once this is installed | What it reaches |
|---|---|---|
| Razer Chroma | Razer Synapse | Every Chroma category that no assigned Razer device lights from its own Lighting tab: headsets, mousepads and Chroma Link strips, and Razer mice, keyboards and keypads while no virtual controller lights a Razer device of that kind |
| Logitech LIGHTSYNC | G HUB or Logitech Gaming Software | Every LED engine kind that no assigned Logitech device lights from its own Lighting tab: headsets, mousepads and speakers, and Logitech mice and keyboards while no virtual controller lights a Logitech device of that kind. Also, in one color, the devices Logitech's LED SDK manual lists without zones: the G710+, G600, G510, G110, G19, G105, G300, G11, G13 and G15 |
| SteelSeries GG | SteelSeries GG | Headsets, and SteelSeries mice and keyboards while no virtual controller lights a SteelSeries device of that kind |
| Razer Sensa | Razer Synapse, in the x64 build | Rumble on Razer Sensa HD devices, covered under Rumble above |

A lighting row lights only while its software runs, and its tab says it is waiting until then. A device lit from its own Lighting tab outranks a vendor row on its kind, whatever the virtual controller numbers. A vendor row removed from the Devices page comes back while its software stays installed.

---

## The route line

Both tabs carry a line in the accent color that says where the output goes and, when it does not arrive, why. On the Lighting tab it sits above the mode card, and with the checkbox off it shows only when something else lights the device. On the Force Feedback tab it sits at the top.

| The Lighting tab reads | When |
|---|---|
| *Colors go through Razer Synapse.* | The device lights through Synapse. Through Logitech's LED engine or GG, the line names the program that runs instead: Logitech G HUB, Logitech Gaming Software or SteelSeries GG. |
| *Colors go straight to* and the device's name | The device lights straight over HID++. |
| *Waiting for SteelSeries GG. Colors show once it runs.* | The software that lights the device does not answer. |
| *Razer Synapse lights every device of this kind at once, so the one on Virtual Controller 1 sets their color.* | Another device of the same kind sets the color. |
| *Razer Synapse lights every device of this kind at once, so the Razer Chroma row on Virtual Controller 1 sets their color.* | The checkbox is off, and a vendor row lights this kind of device. |
| *Virtual Controller 1 also lights this device, and its color shows.* | The same device, or the same vendor row, is lit from a lower-numbered virtual controller too. |
| *Virtual Controller 1 lights this device.* | The checkbox is off here, and another virtual controller lights the device. |
| *Another row of this device on this virtual controller sets its color.* | A device lit over HID++ has two rows on this virtual controller, such as a mouse row and a keyboard row, and the other one sets the color. |
| *Another row of this device on this virtual controller lights it.* | This row's checkbox is off, and another row of the same HID++ device on this virtual controller lights it. |
| *This device has not answered yet. Its colors show once it wakes up.* | A Logitech device is asleep or unplugged. |
| *The Logitech LED engine on this PC cannot light this kind of device.* | The LED engine G HUB or Logitech Gaming Software installed lacks the call this kind of device needs, or will not load while that program runs. The Logitech LIGHTSYNC row reads it too when the engine will not load. In the ARM64 build, an engine that will not load reads *Not Available on ARM64* instead. |
| *Lights the devices Razer Synapse reaches that no assigned device lights on its own, such as headsets, mousepads and Chroma Link strips.* | The Razer Chroma row, while Synapse answers. The Logitech LIGHTSYNC row names Logitech G HUB or Logitech Gaming Software, whichever runs, with headsets, mousepads and speakers, and the SteelSeries GG row names SteelSeries GG with headsets. |
| *Waiting for Razer Synapse. Once it runs, this row lights the devices it reaches that no assigned device lights on its own, such as headsets, mousepads and Chroma Link strips.* | The Razer Chroma row, while Synapse does not answer. |

| The Force Feedback tab reads | When |
|---|---|
| *Rumble plays through the tactile handler in SteelSeries GG.* | A Rival, while GG answers. |
| *SteelSeries GG drives every tactile Rival at once, so the one on Virtual Controller 1 sets their rumble.* | A Rival on a lower-numbered virtual controller sets the rumble. |
| *Waiting for SteelSeries GG. Rumble plays once GG runs.* | A Rival, while GG does not answer. |
| *This device has not answered yet. Its rumble plays once it wakes up.* | A Logitech haptic mouse is asleep or unplugged. |
| *Rumble plays on your Razer Sensa HD devices through Razer Synapse.* | The Razer Sensa row, once its engine reaches Synapse's Sensa runtime. |
| *Waiting for Sensa HD Haptics in Razer Synapse 4. Set the device’s Haptic Source to Sensa HD Games in Synapse.* | The Razer Sensa row cannot reach Synapse's Sensa runtime. |

On an MX Master 4 the line names the mouse and says its rumble plays as haptic pulses, or that its haptic feedback is turned off in Logi Options+.

---

## Set Chroma Color

The **Set Chroma Color** macro action paints the Razer devices assigned to its virtual controller and every other Razer device of their kinds. With the Razer Chroma row assigned there, it paints every Razer device. While it runs, it paints over any virtual controller's Lighting tab, even on a device whose Control This Device’s Lighting checkbox is off. It lets go within 120 ms of the action ending. When macros on two virtual controllers paint the same kind of device, the lower-numbered virtual controller wins. It needs Razer Synapse running. See [Macros](../guides/macros.md#set-chroma-color).

---

## Remote Link

A haptic mouse or keyboard shared from another PC over [Remote Link](../guides/remote-link.md) gets a Force Feedback tab, and its rumble plays on the PC it is plugged into. Its lighting stays with that PC, and so do the vendor rows.

---

## The old Dashboard switches

Earlier versions mirrored a game's lightbar to Razer Chroma and Logitech LIGHTSYNC from the Dashboard's Lightbar Mirrors section, and sent rumble to Sensa HD devices from its Razer Sensa HD Haptics section. Both sections are gone, along with their settings. PadForge turns a switch that was on into an assignment the first time it loads your settings:

- A Razer Chroma or Logitech LIGHTSYNC mirror that was on assigns its row to the first virtual controller, in display order, set to a DualSense, DualSense Edge or DualShock 4. With no such virtual controller, the row stays unassigned.
- In the x64 build, a Sensa switch that was on assigns the Razer Sensa row to the lowest-numbered virtual controller.

The same happens in each saved profile where a switch was on, and in a profile file from an earlier version when you import it. A migrated lighting row starts at Player Number, so it shows the game's lightbar the way the mirror did, and the controller's player color while no game writes one.

---

## On ARM64

The ARM64 build has no Razer Sensa row, because Razer ships no ARM64 engine. Logitech's LED engine lights devices there only if G HUB or Logitech Gaming Software installs an ARM64 version of it.

---

## Related pages

- [Lighting](lighting.md): every mode and setting on the Lighting tab.
- [Force Feedback](force-feedback.md): the Force Feedback tab's settings and Test Rumble.
- [Devices](devices.md): assigning a device to a virtual controller.
- [Macros](../guides/macros.md): Set Chroma Color and the lightbar actions.
- [Analog Keyboards](analog-keyboards.md): analog keyboard rows, which count as keyboards here.
- [Profiles](../guides/profiles.md): how a profile carries assignments and tab settings.
- [Remote Link](../guides/remote-link.md): sharing devices with another PC.
- [Peripheral Outputs Internals](../reference/peripheral-outputs-internals.md): the HID++, Chroma, LED engine, GameSense and Interhaptics paths, for whoever changes the code.

---

*Last updated for PadForge 5.0.0.*
