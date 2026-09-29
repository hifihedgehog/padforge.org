# Bliss-Box Adapters

*Retro controllers in Bliss-Box ports, named for what is plugged in, with DualShock 2 pressure, rumble, the Dreamcast VMU screen and N64 Controller Pak saves.*

*Added after 4.5.3. Pre-release builds have it, and the next release will.*

A Bliss-Box adapter (the 4-Play, Gamer-Pro and Gamer-Pro jr., and the Advanced models, the GPA) plugs retro controllers into USB. Each port is its own USB joystick, one per player. PadForge reads that joystick like any other, and with **Read Bliss-Box Adapters** on it also talks to each port through the adapter's own API: it learns which controller is plugged in and names its buttons, reads a DualShock 2's pressure-sensitive buttons, drives rumble with the adapter's motor commands, shows pictures on a Dreamcast pad's VMU, and backs up and restores an N64 Controller Pak.

---

## Turning it on

Open **Settings**, find the **Input Engine** card, and tick **Read Bliss-Box Adapters**. It is off by default.

The line under the checkbox names each port and what is in it, for example *Reading port 1 (DualShock 2), port 2 (no controller).*, or says *No Bliss-Box port found.*

Close the Bliss-Box API Tool and DeviceBuddy while the switch is on, since they talk to the adapter over the same channel.

!!! warning "Map the ports again after turning the switch on or off"
    SDL, the library PadForge reads controllers through, knows the adapter as a "4Play Adapter" gamepad with one fixed button layout. That layout fits one kind of controller. While the switch is on, PadForge reads each port in the adapter's own layout instead, which follows whatever is plugged in, and the port shows as a **Joystick** on the Devices page. The same button then has a different number, so a mapping made with the switch off points at the wrong buttons with it on, and the reverse.

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

A controller that neither source lays out keeps numbered names (**Button 3**, **Axis 1**), and so does every controller on a 2.x adapter. A DualShock 2's pressure axes carry names on every firmware, so on a 2.x adapter its other axes show the joystick's own names (**X Axis**, **Y Axis**) instead of numbers.

| Adapter | Controllers with named buttons |
|---|---|
| 3.x | Atari joystick, ColecoVision, Dreamcast, GameCube, Genesis 3-button and 6-button, Nintendo 64, Neo Geo, NES, PlayStation digital pad, DualShock, DualShock 2, Saturn pad and 3D Control Pad, SNES, TurboGrafx-16, 3DO, Wii Classic Controller |
| 4.x (GPA) | All of the 3.x list except the ColecoVision, plus the Atari 5200, Atari paddles, Master System paddle, Arkanoid, Bally Astrocade, Gemini paddles, Pippin, CD-i, Dreamcast ASCII pad, PC gameport joystick, Jaguar, Wii Nunchuk, TurboGrafx-16 6-button pad, PlayStation flight stick, PlayStation pad, FM Towns pad, Virtual Boy and XE-1 AP |

---

## DualShock 2 pressure

A DualShock 2's twelve pressure-sensitive buttons (the four D-pad directions, the four face buttons, L1, R1, L2 and R2) arrive as twelve extra axes named for their buttons: **Cross Pressure**, **D-Pad Up Pressure**, **R2 Pressure** and so on. Each reads 0 at rest and full at the bottom of the press.

Put one on a trigger and the press depth is the trigger pull. Put one on a button and it presses once the depth passes the row's **Axis-to-Button Deadzone**, so a light touch and a full press can do different things. The buttons themselves still work as ordinary buttons.

Select the port's card and a **DualShock 2 Pressure** panel in its detail pane shows each button's depth as a bar and a percentage.

PadForge asks for the pressures every 50 ms, DeviceBuddy's own rate, and only while a DualShock 2 is in the port. On firmware 3.0 and a GPA the request costs the adapter none of its own controller reads.

---

## Rumble

A port's rumble goes through the adapter's own motor commands, for the controllers Bliss-Box's API Tool rumbles:

| Controller | Motors |
|---|---|
| DualShock, DualShock 2, neGcon, JogCon | Two. The game's low-frequency motor drives the large one and the high-frequency motor the small one, each at its own strength. |
| GameCube controller, Dreamcast pad, N64 controller, Dreamcast fishing rod | One, at the stronger of the game's two levels. |

Any other controller is sent nothing, since every motor command costs a 3.x adapter one of its own controller reads. SDL's rumble stays off these ports while the switch is on, because it blends both motors into one effect. **Fold Trigger Rumble into Main Motors** on the Pad page folds the game's trigger rumble into these motors, as it does on any controller without trigger motors.

On a GPA a running motor is told again every 100 ms, as the API Tool does to hold rumble on, and a new level goes out at once. On a 3.x adapter, where each command costs a controller read, both motors are sent their levels together at most once every 100 ms, so a game that changes its rumble every frame never holds the controller's input still. A send carries the strongest level the game asked for since the last one when that is stronger than what the motor runs, so a short hit between two sends is still felt. A change can take up to 100 ms to arrive there, a steady level is sent again once a second, and a send the adapter refused goes again with the next. When the game stops the motors, when you unassign the controller, and when PadForge stops, the motors are told to stop. A controller plugged into the port takes the game's current level.

The motors change hands on the input engine's next cycle after you turn the switch on or off. Turned on, SDL's rumble stops and the adapter takes the game's current level. Turned off, each port sends its last stop, and SDL then takes the level over.

---

## Dance mats and the arrows

A dance mat presses left and right, or up and down, at once. A D-pad cannot, and the hat the adapter reads a D-pad as cannot show it. So once opposite directions have been pressed together, the adapter also sends the four directions as buttons of their own, which the mapping picker lists as **Up Arrow**, **Down Arrow**, **Left Arrow** and **Right Arrow**. Map those, not the hat. A 3.x adapter keeps sending them until it starts a new search after a controller its own search found. A controller already plugged in when the adapter powered up is found another way, so the arrows it turned on keep coming for the next controller too, until that one is unplugged. A GPA keeps sending them until it powers off, until a ColecoVision controller, Super Action Controller or ColecoVision wheel is plugged in, until it reads an Atari port as a Trak-Ball, or until its settings go back to their defaults. It sends them from power-up when its stored setting for them is on. A GPA never turns them on for the Genesis 3-button pad or the FM Towns pad, and the PC-FX pad's own buttons share their bits, so PadForge names them for none of the three, and only for a controller whose layout has a D-pad.

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

Pictures come from a BMP or PNG, a VMU Animator `.lcd` file (its first frame) or a Dreamcast `.vms` save's icon. They are cut to the VMU's 48 by 32 black and white pixels.

The adapter keeps its picture in its own memory and rewrites it each time a new one arrives, and that memory wears with writes. So PadForge writes a picture only when it differs from the one the adapter holds, and never sooner than a second after the last one. Before it first replaces the adapter's own picture, PadForge keeps a copy and saves it to the settings file at once. The VMU keeps the adapter's picture until that save has reached the disk.

---

## N64 Controller Pak

**Back Up Controller Pak…** saves the whole pak in the port's N64 controller to a 32 KB `.mpk` file, the format N64 emulators read. **Restore Controller Pak…** writes such a file back, replacing every save on the pak, after you confirm. The status line shows the progress.

Every block carries a checksum. A backup reads a block up to three times before it stops, and a restore gives up once more than 16 writes are rejected, the API Tool's limit. A Rumble Pak holds no saves and is refused. Controller Pak transfers need adapter firmware 3.0 or later. While a backup, a restore or a player change runs on a port, the buttons that start them wait until it ends.

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
- On a GPA, every picture write also starts the Dreamcast driver's 10 ms full-power rumble, for DeviceBuddy's writes as for PadForge's. PadForge stops it right after each write and gives a running rumble its strength back, so a jump pack may give a short buzz when the picture changes.
- The Saturn racing controller and mission stick report as a Saturn 3D Control Pad. The mission stick's throttle arrives as **Right Trigger**, and an axis a controller does not send stays at its midpoint, which reads as a half-pressed trigger: **Left Trigger** on the mission stick, both triggers on the racing controller.
- For up to half a second after a GameCube, Dreamcast or Saturn 3D pad leaves its port, its triggers read as half pressed, until the adapter reports the port empty.
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
