# Flydigi Apex Controllers

*Trigger effects, rumble, grip haptics, lights and the screen on a Flydigi Apex 4, Apex 5 and Apex 6 Pro.*

SDL reads a Flydigi Apex pad's buttons, sticks and motion, as it reads any Flydigi controller. PadForge also opens the pad's vendor interface beside SDL and asks the pad what it is. Once the pad answers as one of the three models below, PadForge drives its triggers, its rumble, its lights and its screen itself.

No Flydigi pad was run with this build. Everything on this page follows the byte layouts and timings of open-source tools whose authors ran them on the pads (see [Flydigi Apex Internals](../reference/flydigi-apex-internals.md)), and PadForge's tests run them against scripted pads.

---

## Which pads

| Model | IDs | Connection |
|---|---|---|
| **Apex 4** | 04B4:2412 | Cable or dongle, in DInput mode |
| **Apex 5** | 37D7:2501 | Cable or receiver |
| **Apex 6 Pro** | 37D7:2502 | Cable or receiver |

The Apex 4 shares its IDs with the Vader 3 and Vader 4, and the Apex 6 Pro shares its IDs with the plain Apex 6, so the IDs alone decide nothing. PadForge asks the pad for its device type and goes by the answer. A pad that answers as something else, a Vader or a plain Apex 6 (device type 0x95), stays what it was before: read and rumbled by SDL, with none of the features below. An Apex 6 Pro is taken only when it reports voice coils in both its grips and its triggers.

An Apex 4 in Xbox mode is an Xbox 360 controller to Windows, and PadForge drives none of this in that mode. Switch it to DInput mode with its own switch.

A pad that does not answer is asked again after 5 seconds, then every 30 seconds. Until it answers, SDL reads and rumbles it. PadForge keeps the model a pad answered with on its device record, so its cards stay on the controller page while the pad sleeps.

---

## Trigger effects

The **Adaptive Triggers** and **Impulse Triggers** cards show in the controller page's **Rumble & Haptics** section for a slot the pad is assigned to. Each trigger shows the first of these that is present:

1. A game's trigger effect on the slot's virtual DualSense.
2. A [game mod's](game-mods.md) hold.
3. A macro's trigger effect.
4. The **Impulse Triggers** levels, as a vibration in that trigger.
5. The [steering lock's](wheel.md) pulse and resistance, on a trigger the Adaptive Triggers card leaves off.
6. The **Adaptive Triggers** card's own effect.

A game that clears its effect gets 100 ms before PadForge's own layers show through. Games set and clear effects many times a second, and releasing the trigger on each clear makes it flutter.

**Apex 4 and Apex 5.** The triggers resist. Each DualSense effect becomes one of the pad's five modes: off, constant resistance, a vibration, a band that gives way, or a hard stop, using the table Flydigi Space Station uses for its own DualSense mode. The pad holds one effect per trigger, so on an Apex 5 three kinds of effect are played from the PC as the trigger moves: a bow that breaks at the end of its draw, effects whose ten zones differ in strength, and the Galloping and Machine rhythms. An Apex 4 plays the plain table.

The Apex 4 acknowledges no trigger command, so PadForge sends each change again after 100 and 500 ms. Each change stalls the Apex 4's sticks for about 50 ms, so changes are rationed: a change of mode goes out at once with no two closer than 100 ms, and a change of strength waits 150 ms after the last change when it moved by more than a quarter, 500 ms otherwise.

**Apex 6 Pro.** The triggers are voice coils. They vibrate and do not resist, so each effect plays as a vibration that follows what the effect does: a burst where a weapon breaks, a build-up and a release for a bow, a carrier whose strength follows the zones, and a rhythm for Galloping and Machine. The pad plays one signal on its triggers. Two different effects at once are summed and sent to both triggers.

The **Translate Adaptive Trigger Vibrations** switch on the Impulse Triggers card is hidden for these pads, since they take the whole effect.

---

## Rumble

The game's rumble reaches the grips through PadForge's own connection to the pad, the same writer that sends the trigger effects, so one writer paces every packet. An Apex 4 gets its writes at least 25 ms apart and two rumbles 10 ms apart. An Apex 5 on its receiver gets its writes 10 ms apart, and rumble 30 ms after a trigger write. SDL takes the rumble back when PadForge's connection to the pad closes.

An Apex 6 Pro's grips are voice coils too. PadForge streams to the pad while a trigger effect or grip haptics play. While the stream runs, the grips play haptics or the rumble, and the pad's own rumble is off. The rumble then plays as a 65 Hz tone in the left grip for the low motor and a 150 Hz tone in the right grip for the high one. After three quiet seconds the stream stops and the motors go back to the pad, and SDL's rumble drives them again.

---

## Apex 6 Pro grip haptics

**Play DualSense Haptics on This Controller**, on the Audio card in the controller page's **Lights & Sound** section, plays a game's DualSense haptic track on the Apex 6 Pro's grips as the track itself, not as tones made from it. Macro sounds go there the same way. The samples go out at 1,000 a second behind a 400 Hz filter. The high-tone filter is not shown for this pad, since nothing is reduced to a tone. See [Controller Audio](controller-audio.md).

---

## Lights

The pad's lights are on the Lighting card in the controller page's **Lights & Sound** section, on the pad's own row, with the modes every lit device has ([Lighting](lighting.md)).

| Model | Lights | What a color does |
|---|---|---|
| **Apex 4** | Four groups | Shows at once in DInput mode and is gone when the pad is switched off. A color goes out at most once a second. |
| **Apex 5** | Twelve lights | Changes the pad's working copy of its light block, which the pad drops when it sleeps. Two pictures go out no closer than 80 ms apart. |
| **Apex 6 Pro** | One color | Is stored by the pad and kept through power-off. |

The Apex 6 Pro stores every color it is sent, so PadForge sends a color only once it has held for 1.5 seconds, skips one within 12 a channel of the color the pad holds, and sends no more than 300 in one run of PadForge. Changing colors, such as a cycle or colors that follow sound, change it at most once every 1.5 seconds. Before its first write PadForge saves the pad's own lighting in the settings file, and when PadForge lets go of the lights it writes that lighting back. A run that ends without the write-back leaves the copy, and the next run writes it back if the pad still shows the color PadForge left.

An Apex 5 whose Switch profile bank is active is left alone, and so is one that names two different profile slots when asked twice. When PadForge lets go of an Apex 5's lights it writes back the block it read and applies the pad's profile again.

While Flydigi Space Station's service runs, it drives these pads' lights, and PadForge leaves them to it.

---

## Controller Screen

The Apex 4 and Apex 5 have a 160 by 80 color screen, and so does an Apex 6 Pro whose feature byte says it has one. Select the pad's row on the [Devices](devices.md) page and click **Controller Screen…** in its panel. The button shows only while PadForge has its connection to the pad.

**Show** picks what goes to the screen:

| Show | The screen shows |
|---|---|
| **Chosen Picture** | A PNG, JPEG, BMP or animated GIF you choose with **Choose Picture…**. |
| **Profile Picture** | The active profile's picture, or its name when it has none, as it is when you send. **Choose Picture for** *profile*… and **Remove Profile Picture** change the profile's picture. |
| **Profile Name** | The active profile's name as it is when you send. |
| **Profile Number** | The active profile's place in the profile list. The Default profile is 0. |

**Fit** sets how a picture meets the screen: **Fill the Screen** cuts off what does not fit, **Show the Whole Picture** leaves black bars, and **Stretch to the Screen** takes the screen's shape. The preview shows the frames that go out, decoded back. A line under it gives the frame count and about how long the send takes. Nothing reaches the pad until you click **Send**. The pad keeps the picture until the next send, through profile switches too.

| Model | Frames at most | Time per frame |
|---|---|---|
| **Apex 4** | 35 | About 4.5 s |
| **Apex 5** | 255 | About 25 s |
| **Apex 6 Pro** | 150 | About 7.3 s |

A GIF with more frames than the pad holds is cut, and the line says how many frames were left out. The pad takes one frame time for the whole picture, so a GIF plays at its first frame's delay.

The screen takes a picture by cable only. A pad on its receiver or dongle gets *Connect the controller by cable. Its screen takes a picture over USB only.*

**Apex 5 and Apex 6 Pro.** PadForge switches the pad's screen chip to its update mode. A USB serial port appears beside the pad, PadForge writes the picture through it, and the pad restarts on its own about 15 seconds after the picture is in. The status line then reads *Sent. The controller shows the picture once it has restarted.*

**Apex 4.** The screen takes a picture in Xbox mode only. Before the send PadForge asks you to confirm, and to unplug every other Xbox 360 controller, since the driver change moves every device with those IDs. PadForge then switches the pad to Xbox mode, checks that it came back as the one new Xbox 360 device and that its USB product string names Flydigi, moves it from Windows' Xbox driver to WinUSB, and checks that it answers as an Apex 4 before anything else is sent. After the send, whether it finished, was stopped or got no answer, PadForge switches the pad back to DInput mode and gives it back to Windows' Xbox driver. A send that a crash cut off is given back the next time PadForge starts.

Each Send uses PadForge's connection to the pad as it is at that moment. A send makes the pad leave and come back, so a second send from the same dialog uses the new connection.

Closing the dialog while a send runs asks first, then stops the send. A send stopped partway leaves the screen waiting: switch the pad off and on with its own switch before you send again.

### When a send fails

Each failure has its own line in the dialog:

| The dialog says | What happened |
|---|---|
| The screen's port did not appear. | The serial port never showed up within 30 seconds. |
| More than one controller screen is waiting for a picture. | Two update ports are present, so PadForge does not know which is this pad's. |
| The screen’s port did not open. Close Flydigi Space Station and send again. | The port refused to open while Flydigi Space Station runs. Without Space Station running, the line asks you to switch the pad off and on instead. |
| The screen stopped answering. | The pad's screen chip gave no reply. |
| The screen refused the picture. | The chip answered a step with a refusal. |
| The screen asked for the picture at an address PadForge does not write to. | An Apex 6 Pro named a picture address PadForge will not erase, so nothing was written. |
| The controller did not take the command that readies it. | The command that starts the send was not written. |
| The controller did not come back as an Xbox 360 controller. | An Apex 4 did not reappear in Xbox mode within 10 seconds. |
| Unplug every other Xbox 360 controller and send again. | Another Xbox 360 device is plugged in. |
| The controller in Xbox mode did not answer as an Apex 4. | The pad's product string or its device type did not match. |
| Windows did not move the controller to WinUSB. | The driver change failed. |
| The picture was sent, but the controller did not switch back to DInput mode. | The switch back was refused. Use the pad's own switch. |
| The picture has more frames than this controller’s screen holds. | The picture is over the limit in the table above. |
| A picture is already going to this controller. | A send to the same pad is still running. |
| The send stopped on an error in PadForge. | The log file has the details. |

---

## Flydigi Space Station

Space Station's service talks to the pad over the same vendor interface. While it runs, the pad's replies can go to it instead of PadForge, so the pad may never answer PadForge's identity request, and none of the features above turn on. The Devices page names the Flydigi programs that are running on the pad's panel. Close Space Station while you use PadForge.

---

## Limits

- No Flydigi pad was run with this build. The byte layouts and timings come from tools whose authors ran them on the pads.
- The screen takes a picture by cable only.
- An Apex 4 send switches the pad to Xbox mode and moves it to WinUSB for the send, and needs every other Xbox 360 controller unplugged. The check that the pad in Xbox mode names Flydigi in its product string rests on no reference: none records that string.
- No reference ran the Apex 5 or Apex 6 Pro screen upload on Windows. It relies on Windows' own serial driver taking the update port.
- The Apex 6 Pro stores each light write, so its color changes at most once every 1.5 seconds and 300 times a run.
- The plain Apex 6 (device type 0x95) is refused, as both references that drive the Apex 6 refuse it.
- Flydigi Space Station holds the pad's replies while it runs.
- An Apex 4's lights are lost when the pad is switched off, and an Apex 5's when it sleeps.
- A GIF frame that asks for the previous frame back after it shows (disposal method 3) is drawn as one that leaves itself in place.

---

## Related pages

- [Adaptive Triggers](adaptive-triggers.md): the effects the triggers play.
- [Impulse Triggers](impulse-triggers.md): the per-trigger levels.
- [Lighting](lighting.md): the light modes.
- [Controller Audio](controller-audio.md): the DualSense haptic track.
- [Devices](devices.md): the Controller Screen button.
- [Flydigi Apex Internals](../reference/flydigi-apex-internals.md): the three protocols, the session, the lights and both screen paths.

---

*Last updated for PadForge 6.0.0.*
