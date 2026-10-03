# Bliss-Box Adapters

*Retro controllers in Bliss-Box ports, named and mapped for what is plugged in, with DualShock 2 pressure, rumble, the Dreamcast VMU screen and N64 Controller Pak saves.*

*Added after 4.5.3. Pre-release builds have it, and the next release will.*

A Bliss-Box adapter (the 4-Play, Gamer-Pro and Gamer-Pro jr., and the Advanced models, the GPA) plugs retro controllers into USB. Each port is its own USB joystick, one per player. PadForge reads that joystick like any other, and with **Read Bliss-Box Adapters** on it also talks to each port through the adapter's own API: it learns which controller is plugged in, names its buttons and maps them the way SDL maps that console's pad, reads a DualShock 2's pressure-sensitive buttons, drives rumble with the adapter's motor commands, shows pictures on a Dreamcast pad's VMU, and backs up and restores an N64 Controller Pak.

---

## Turning it on

Open **Settings**, find the **Input Engine** card, and tick **Read Bliss-Box Adapters**. It is off by default.

The line under the checkbox names each port and what is in it, for example *Reading port 1 (DualShock 2), port 2 (no controller).*, or says *No Bliss-Box port found.*

Close the Bliss-Box API Tool and DeviceBuddy while the switch is on, since they talk to the adapter over the same channel.

!!! warning "Map the ports again after turning the switch on or off"
    SDL, the library PadForge reads controllers through, knows the adapter as a "4Play Adapter" gamepad with one fixed button layout. That layout fits one kind of controller. While the switch is on, PadForge reads each port in the adapter's own layout instead, which follows whatever is plugged in, and the port shows as a **Joystick** on the Devices page. The same button then has a different number, so a mapping made with the switch off points at the wrong buttons with it on, and the reverse. Unassign the port from its slot and assign it again to get the default mapping for the way it is read now.

---

## The port on the Devices page

Select a port's card on the [Devices](devices.md) page, and its detail pane carries a line with its player number, the controller in it and the adapter's firmware:

*Bliss-Box port 1 · DualShock 2 · firmware 4.86*

Under the line are the port's actions. Each one appears only when it applies:

| Action | Shows when |
|---|---|
| **Player Number…** | The port answers the API. |
| **Dreamcast Screen…** | A Dreamcast pad is in the port. |
| **Back Up Controller Pak…** and **Restore Controller Pak…** | An N64 controller is in the port of an adapter with firmware 3.0 or later. |
| **Read Arrows One by One** | A PlayStation digital pad or dance mat is in a 3.x adapter's port. |

### Button names

In the mapping picker, the port's buttons and sticks take the names of the controller plugged in: **Cross**, **Circle**, **L2** and **Left Stick X** on a DualShock 2, **A**, **Z Trigger**, **C-Up** and **Stick X** on an N64 controller. Plug in another controller and the names follow it.

The names come from two sources, one per firmware generation: RetroArch's Bliss-Box autoconfig files, written for firmware 3.24, on a 3.x adapter, and DeviceBuddy's controller layouts on a 4.x GPA. They follow the adapter's default button map. If you remapped buttons in the API Tool or chose one of the GPA's alternate maps, the names stay on the default positions, since the adapter does not say which map is active.

Analog triggers follow the firmware itself. A GameCube controller's, a Dreamcast pad's and a Saturn 3D Control Pad's triggers arrive as **Left Trigger** and **Right Trigger** on either generation, 0 when released, and a trigger mapping treats them as a gamepad's: it does not engage at rest.

On a GPA a PlayStation pad has one more button. Hold Select and Start for about two seconds, the adapter's hotkey hold, and the adapter sends a button of its own in place of both. PadForge names it **Guide**, SDL's name for the button that opens a system menu, the PS button on a DualShock 3. A 3.x adapter has no such button.

A controller that neither source lays out keeps numbered names (**Button 3**, **Axis 1**), and so does every controller on a 2.x adapter. A DualShock 2's pressure axes carry names on every firmware, so on a 2.x adapter its other axes show the joystick's own names (**X Axis**, **Y Axis**) instead of numbers.

| Adapter | Controllers with named inputs |
|---|---|
| 3.x | Atari joystick, ColecoVision, Dreamcast, GameCube, Genesis 3-button and 6-button, Jaguar, Nintendo 64, Neo Geo, NES, PlayStation digital pad, DualShock, DualShock 2, Saturn pad and 3D Control Pad, SNES, TurboGrafx-16, 3DO, Wii Classic Controller |
| 4.x (GPA) | All of the 3.x list except the ColecoVision, plus the Atari 5200, Atari paddles, Master System paddle, Arkanoid, Bally Astrocade, Gemini paddles, Pippin, CD-i, Dreamcast ASCII pad, PC gameport joystick, Wii Nunchuk, TurboGrafx-16 6-button pad, PlayStation flight stick, PlayStation pad, FM Towns pad, Virtual Boy and XE-1 AP |

---

## Default mapping

With the switch on, assigning a port to a slot maps the controller in it the way SDL, the library PadForge reads controllers through, maps that console's pad. A DualShock 2 maps as SDL maps a DualShock 3: Cross presses the virtual controller's bottom face button (A on an Xbox slot, Cross on a PlayStation slot), Circle the right one, Square the left and Triangle the top. L2 and R2 pull the triggers, and Select, Start and the GPA's Guide button press Back, Start and Guide.

Each controller follows SDL's own mapping for its console's pad where SDL has one: its PS3 driver for the PlayStation pads, its mappings for Nintendo's Switch Online NES, SNES, N64 and Genesis controllers, its GameCube adapter mapping, and its Wii driver for the Classic Controller and the Nunchuk. SDL maps a pad without a diamond of four face buttons by its letters, so an NES or N64 controller's A is the bottom button wherever it sits. The pads SDL has no mapping for follow RetroArch's Bliss-Box autoconfig files.

| Controller | Bottom | Right | Left | Top | Also |
|---|---|---|---|---|---|
| PlayStation pads | Cross | Circle | Square | Triangle | L2 and R2 are the triggers and Select is Back. On a GPA, the Select and Start button is Guide |
| SNES | B | A | Y | X | L and R are the shoulder buttons |
| NES | A | B | | | |
| Nintendo 64 | A | B | C-Down | C-Left | C-Up is Back, C-Right is Misc 2 and Z is the left trigger |
| Genesis | A | B | X | Y | C is the right shoulder, Z the left and Mode the right trigger |
| GameCube | A | X | B | Y | Z is the right shoulder, L and R are the triggers and the C-stick is the right stick |
| Wii Classic Controller | B | A | Y | X | ZL and ZR are the triggers, minus is Back and plus is Start. On a GPA, Home is Guide |
| Wii Nunchuk | | | | | C is the left shoulder and Z the left trigger |
| Dreamcast | A | B | X | Y | L and R are the triggers |
| Saturn | A | B | X | Y | Z is the left shoulder and C the right, L and R are the triggers |
| Neo Geo | A | B | C | D | |
| TurboGrafx-16 | II | I | | | Run is Start |
| 3DO | B | C | A | | X is Back and P is Start |
| Jaguar | B | C | A | | Option is Back and Pause is Start |
| Atari joystick | Fire | | | | |
| ColecoVision | Right fire | Left fire | | | |

Sticks and the D-pad land on the virtual controller's sticks and D-pad, and Start on Start, wherever a controller has them. A controller with named buttons that no source places gets no default mapping: the Atari 5200 controller, the paddle and dial controllers, the Bally Astrocade controller, the Pippin, CD-i and FM Towns pads, the PC gameport joystick, the Virtual Boy and the XE-1 AP. Neither does a controller without named buttons, which includes every controller on a 2.x adapter. On a GPA the Neo Geo pad's four buttons stay unmapped, since DeviceBuddy leaves them unlabeled.

The N64 follows SDL's mapping exactly. Its C buttons do not form a right stick, and C-Right lands on Misc 2, which only the Switch 2 Pro's C button takes. Bind them yourself if a game wants them elsewhere.

A port assigned while it is empty or unplugged gets its default mapping once PadForge can place its controls: with the switch on, when the adapter reports a controller in the port, and with the switch off, when the port connects. Until then the slot shows nothing from the port. A row you set, record or clear in the meantime keeps what you gave it, and the rest fill in. **Clear All**, **Paste** and **Copy From...** on the slot, and turning on **Force Raw Joystick Mode** for the port, cancel the pending mapping. A change to the **DualShock 3 (SIXAXIS): Full** preset while the port's DualShock 2 is unplugged fills its pressure rows the same way once it is back.

A slot mapped with a controller in the port keeps that mapping when you plug in a different kind of controller. To map the new one fresh, unassign the port from the slot and assign it again.

---

## DualShock 2 pressure

A DualShock 2's twelve pressure-sensitive buttons (the four D-pad directions, the four face buttons, L1, R1, L2 and R2) arrive as twelve extra axes named for their buttons: **Cross Pressure**, **D-Pad Up Pressure**, **R2 Pressure** and so on. Each reads 0 at rest and full at the bottom of the press.

Put one on a trigger and the press depth is the trigger pull. Put one on a button and it presses once the depth passes the row's **Axis-to-Button Deadzone**, so a light touch and a full press can do different things. The buttons themselves still work as ordinary buttons.

Select the port's card and a **DualShock 2 Pressure** panel in its detail pane shows each button's depth as a bar and a percentage.

PadForge asks for the pressures every 50 ms, DeviceBuddy's own rate, and only while a DualShock 2 is in the port. On firmware 3.0 and a GPA the request costs the adapter none of its own controller reads.

On a PlayStation slot running the **DualShock 3 (SIXAXIS): Full** preset, the default mapping puts ten of them on the slot's [pressure rows](mappings.md#button-pressure), all but L2 and R2, whose pressure is the trigger pull. The default L2 and R2 rows read the L2 and R2 buttons, which arrive with every report. For an analog pull, pick **L2 Pressure** and **R2 Pressure** on those rows instead.

---

## Rumble

A port's rumble goes through the adapter's own motor commands, for the controllers that have motors:

| Controller | Motors |
|---|---|
| DualShock, DualShock 2 | Two. The game's low-frequency motor drives the large one and the high-frequency motor the small one, each at its own strength. |
| GameCube controller, Dreamcast pad, N64 controller, Dreamcast fishing rod | One, at the stronger of the game's two levels. |

Any other controller is sent nothing, since every motor command costs a 3.x adapter one of its own controller reads. That includes the neGcon, which has no motor, and the JogCon, whose force feedback the adapter does not drive. SDL's rumble stays off these ports while the switch is on, because it blends both motors into one effect. **Fold Trigger Rumble into Main Motors** on the Pad page folds the game's trigger rumble into these motors, as it does on any controller without trigger motors.

On a GPA a running motor is told again every 100 ms, as the API Tool does to hold rumble on, and a new level goes out at once. On a 3.x adapter, where each command costs a controller read, both motors are sent their levels together at most once every 100 ms, so a game that changes its rumble every frame never holds the controller's input still. A send carries the strongest level the game asked for since the last one when that is stronger than what the motor runs, so a short hit between two sends is still felt. A change can take up to 100 ms to arrive there, a steady level is sent again once a second, and a send the adapter refused goes again with the next. When the game stops the motors, when you unassign the controller, and when PadForge stops, the motors are told to stop. A controller plugged into the port takes the game's current level.

The motors change hands on the input engine's next cycle after you turn the switch on or off. Turned on, SDL's rumble stops and the adapter takes the game's current level. Turned off, each port sends its last stop, and SDL then takes the level over.

---

## Dance mats and the arrows

A dance mat presses left and right, or up and down, at once. A D-pad cannot, and the hat the adapter reads a D-pad as cannot show it. So once opposite directions have been pressed together, the adapter also sends the four directions as buttons of their own, which the mapping picker lists as **Up Arrow**, **Down Arrow**, **Left Arrow** and **Right Arrow**. Map those, not the hat. A 3.x adapter keeps sending them until it starts a new search after a controller its own search found. A controller already plugged in when the adapter powered up is found another way, so the arrows it turned on keep coming for the next controller too, until that one is unplugged. While such an adapter searches an empty port, it reports all four arrows held, and PadForge clears them once it reads that the adapter is searching, within half a second unless the port is storing a picture. A GPA keeps sending them until it powers off, until a ColecoVision controller, Super Action Controller or ColecoVision wheel is plugged in, until it reads an Atari port as a Trak-Ball, or until its settings go back to their defaults. It sends them from power-up when its stored setting for them is on. A GPA never turns them on for the Genesis 3-button pad or the FM Towns pad, and the PC-FX pad's own buttons share their bits, so PadForge names them for none of the three, and only for a controller whose layout has a D-pad. On a 3.x adapter the Jaguar's keypad sits on those four buttons, so there they keep the keypad's names.

On a 3.x adapter, select a PlayStation dance mat's card and tick **Read Arrows One by One**, and PadForge asks the pad for its four directions itself, through the adapter's native channel, so the arrows work from the first step. The requests run back to back, 16 ms apart, and the adapter skips most of its own reads of the pad while they do. Once opposite directions have been pressed and the adapter sends the arrows itself, PadForge stops asking, until another controller is plugged in.

---

## Dreamcast screen

**Dreamcast Screen…** chooses what the VMU in a Dreamcast pad shows. The dialog previews the picture as the VMU draws it.

| Show | The VMU shows |
|---|---|
| **The Adapter's Picture** | The picture the adapter keeps. PadForge writes nothing, and puts back the picture it found if it wrote one since. |
| **Profile Name** | The active profile's name, following each profile switch. |
| **Profile Number** | The active profile's place in the profile list. The Default profile is 0. |
| **Profile Picture** | The active profile's own picture, or its name when it has none. Each profile keeps its own. |
| **Clock** | The time of day, rewritten once a minute. |
| **Play Time** | The hours and minutes since PadForge found the pad, rewritten once a minute. A pad out of its port for more than ten seconds starts again from zero. |
| **Chosen Picture** | A picture you choose. |

Pictures come from a BMP or PNG, a VMU Animator `.lcd` file (its first frame) or a Dreamcast icon file (ICONDATA_VMS, a `.vms` that holds only an icon). A game save's `.vms` does not import. They are cut to the VMU's 48 by 32 black and white pixels.

The adapter keeps its picture in its own memory and rewrites it each time a new one arrives, and that memory wears with writes. So PadForge writes a picture only when it differs from the one the adapter holds, and never sooner than a second after the last one. Before it first replaces the adapter's own picture, PadForge keeps a copy and saves it to the settings file at once. The VMU keeps the adapter's picture until that save has written the copy to the settings file.

---

## N64 Controller Pak

**Back Up Controller Pak…** saves the whole pak in the port's N64 controller to a 32 KB `.mpk` file, the format N64 emulators read. **Restore Controller Pak…** writes such a file back, replacing every save on the pak, after you confirm. The status line shows the progress.

Every block carries a checksum. A backup reads a block up to three times before it stops, and a restore gives up once more than 16 writes are rejected, the API Tool's limit. A Rumble Pak holds no saves and is refused. Controller Pak transfers need adapter firmware 3.0 or later. While a backup, a restore or a player change runs on a port, the port's buttons wait until it ends, and after a player change they stay off until the port comes back as a new device.

---

## Player number

**Player Number…** sets the port's player number, 1 to 4. The adapter stores it and reconnects as that player, which Windows sees as a new device, so assign and map the port again once it comes back. If PadForge had put a picture on the port's VMU, it puts the adapter's own back first, and the returning port starts with the adapter's picture and none of the old port's choices.

If the adapter refuses its own picture back, PadForge leaves the player number alone. If the adapter still answers as the old player a moment after the change, the change did not take. Either way the port keeps its number and its choices, and the status line says the adapter kept its player number.

---

## Macros

**Show Dreamcast Screen**, in the **Lightbar & LEDs** group, plays one to eight pictures on the VMU of every Dreamcast pad in a Bliss-Box port that feeds the macro's slot. Add pictures with **Add Picture…**, click one to remove it, and set the **Frame Time** (a second at least) and the **Repeat Count**. Each picture shows for its frame time from the moment the VMU has it, so a show runs a little longer than the frame time multiplied by the number of pictures and the repeat count. A picture the port has not taken within five seconds counts its time from when its turn began, so a port that refuses pictures cannot hold a show forever. When the pictures finish, each port goes back to its own screen setting. See [Macros](../guides/macros.md#show-dreamcast-screen).

---

## Limitations

- No Bliss-Box adapter has been read live by the maintainer. Every report was built from Bliss-Box LLC's API Tool, DeviceBuddy and the adapters' firmware, and tested against a scripted adapter.
- Light guns read their trigger and buttons. Aiming needs a CRT television, and the Bliss-Box compatibility list pairs the Zapper with MiSTer.
- The adapter gives an empty port and an Atari joystick the same type code, so an empty port can show as an Atari joystick.
- VMU saves cannot be read: Dreamcast accessories do not answer the adapter's native channel. PlayStation and GameCube memory cards plug into the console, not the controller cable, so the adapter never sees them.
- Storing a new picture holds the controller's input still while the adapter writes it, up to about two thirds of a second when every byte changes. A clock or play time pauses the pad briefly once a minute, and a macro show at each picture.
- The adapter's picture memory is rated for 100,000 writes. A clock or play time rewrites its last digit once a minute, which reaches that rating after about ten weeks of display around the clock, and a looping macro show at a picture a second reaches it in about a day.
- The VMU keeps the last picture PadForge showed after PadForge closes or the switch goes off. Choose **The Adapter's Picture** to put the adapter's own back.
- On a GPA, every picture write also arms the Dreamcast driver's 10 ms full-power rumble, for DeviceBuddy's writes as for PadForge's. Storing a picture that changes more than a few bytes takes longer than that, so the pulse ends before it reaches the pack. A rumble already running is different: the write takes over its timer and runs the pack at full power until PadForge sends its level again, right after the write.
- The Saturn racing controller and mission stick report as a Saturn 3D Control Pad. The mission stick's throttle arrives as **Right Trigger**, and an axis a controller does not send stays at its midpoint, which reads as a half-pressed trigger: **Left Trigger** on the mission stick, both triggers on the racing controller.
- For up to half a second after a GameCube, Dreamcast or Saturn 3D pad leaves its port, longer while the port is storing a picture, its triggers read as half pressed, until the adapter reports the port empty.
- PadForge keeps a copy of the adapter's own picture from the first time it replaces it, and Reset to Defaults keeps that copy. A picture sent to the adapter from DeviceBuddy or the API Tool after that is replaced without a copy.
- The adapter's own settings, its modes, button mapper, turbo, hotkey and stick range, stay with the API Tool and DeviceBuddy.

---

## Related pages

- [Settings](settings.md): the Input Engine card and its Read Bliss-Box Adapters switch.
- [Devices](devices.md): the port's card, its detail pane and its actions.
- [Button and Axis Mappings](mappings.md): deadzones and the Axis-to-Button Deadzone that a pressure button presses past.
- [Macros](../guides/macros.md): the Show Dreamcast Screen action.
- [Bliss-Box Internals](../reference/bliss-box-internals.md): every report and rule, for whoever has to change the code.

---

*Last updated for PadForge 4.5.3.*
