# Bliss-Box Internals

*How PadForge pairs an API sidecar with each Bliss-Box port's SDL row, and every report it sends and reads.*

For the user-facing side see [Bliss-Box Adapters](../features/bliss-box.md).

Firmware addresses on this page are word addresses in the disassembled GPA 4.86, 3.0 and 2.0 images. The 3.x behavior is read from the 3.0 image, build 034, which reports itself as firmware 3.34. No other 3.x image was on hand, so other 3.x builds are taken to behave the same.

The engine side lives in `PadForge.Engine/Common/BlissBox/`:

| File | Responsibility |
| --- | --- |
| `BlissBoxProtocol.cs` | Report IDs, command builders, the native-channel chunking, and the parsers for reports 17, 21, 22 and 24. |
| `BlissBoxControllers.cs` | Type codes and names, per-type button and axis names for firmware 3.x and 4.x, the DualShock 2 pressure order, and what each type can do. |
| `BlissBoxScreen.cs` | The VMU picture codec and the `.lcd` and `.vms` importers. |
| `BlissBoxControllerPak.cs` | Controller Pak frames, the address checksum and the data CRC. |
| `BlissBoxPsx.cs` | The PlayStation pad poll and its decoder. |
| `BlissBoxSession.cs` | One port's state machine: polls, motors, the VMU picture, the native channel and the jobs. |
| `BlissBoxApi.cs` | The switch as the engine sees it, and the hook that names a port's objects. |

The app side: `PadForge.App/Common/Input/BlissBoxPort.cs` (the HID channel and the worker thread), `BlissBoxRuntime.cs` (the ports, their pairing with SDL rows, the state merge, the object names), `InputManager.BlissBox.cs` (Step 1's phase 1l), `PadForge.App/Services/DreamcastScreenService.cs` (the VMU screens and the ports' saved choices), `InputService.BlissBox.cs` (status lines and the port's Devices page detail pane), `MainWindow.BlissBox.cs` (the port's actions), and the two dialogs `BlissBoxPlayerDialog` and `DreamcastScreenDialog`.

---

## The shape

SDL reads each port's joystick, as it reads any USB joystick. A port is one USB device per player, vendor `0x16D0`, product `0x0D03` plus the player number, so `0x0D04` to `0x0D07`. The bootloaders (`0x0A5F`, `0x04FB`), the 1.x firmware (`0x0A60`) and the "4-Play Fix" IDs (`0x0A61` to `0x0A64`) never match, so nothing talks to an adapter mid-update.

With **Read Bliss-Box Adapters** on, a `BlissBoxPort` opens a second handle on the same HID collection, beside the SDL row, and owns what the joystick report cannot carry. This is the Padix converter's shape (#440): SDL for input, PadForge's own writes for the rest.

### Raw reading

The SDL fork carries SDL_GameControllerDB's mapping for all four IDs, "4Play Adapter", so SDL would open a port as a gamepad. That mapping describes one layout, while the adapter's report follows whatever controller is plugged in. While the switch is on:

- `SdlDeviceWrapper.OpensAsGamepad` skips `SDL_OpenGamepad` for a port (`BlissBoxApi.ReadsRaw`), so the row reads the joystick surface.
- `SdlDeviceWrapper.InputDeviceTypeFor` types the row a Joystick, although `SDL_GetJoystickType` still says gamepad for a mapped device. The gamepad auto-map and the trigger rest rule for axes 2 and 5 then leave it alone.
- Phase 1l reopens any port row open the other way: every Step 1 pass while the switch is on, since a row can open between the switch and the phase, and once more after it goes off. The reopen is Phase 1's replug rebind: a fresh `SdlDeviceWrapper` for the same SDL instance, `UserDevice.LoadFromSdlDevice`, which disposes the old wrapper, and the new wrapper in `_openedSdlInstanceIds`. SDL counts the opens of one joystick, so the device stays open across the swap.

### The channel and the worker

`AnalogKeyboardHidChannel.OpenShared` opens the collection shared for read and write, as hidapi opens it for the API Tool, and falls back to no access rights, which still carries feature reports. The input queue is held to two buffers, since nothing reads it. Feature reports are padded to the collection's feature report length.

One worker thread per port runs `BlissBoxSession.Step` back to back and sleeps for the time `Step` returns, woken early when another thread sets a motor level or queues a job. That serializes every control transfer, as BBAPI.cs's `CT_IO` flag does. The worker opens the channel once a second while it will not open, closes and reopens it after three failed info reads in a row, and on its way out stops both motors, opening the channel once more if it is down, since an adapter that stayed up may still run the last level, then ends every queued job as closed and closes the handle. Closing the channel forgets everything read from the adapter and ends the jobs still queued, since they were asked of the controller that was in the port before, and a job queued while the channel is closed ends as closed at once.

`BlissBoxRuntime.Sync` pairs ports with rows on the poll thread by HID path, instance GUID and SDL instance, opens a port for a new row, and retires a port whose row left or reconnected, disposing it on the thread pool so a transfer in flight never holds up the poll thread. `BlissBoxRuntime.IsRetiring` answers until the port's worker has exited (`BlissBoxPort.Exited`), which holds past the dispose's 3 s wait, so the row's motors go back to SDL only after the port's final stop. A closing session stops asking for a native answer before its next read, so the worker lets go within a transfer. The list is pruned as ports retire. A reconnected row gets a new port because the old session would send the new connection the levels it last held, while the row's new motor snapshot starts at rest. A port that opens hands its motors over from SDL (see [Rumble](#rumble)).

---

## Reports

A feature report read comes back with the device's first byte where the report ID went, so every parser reads from byte 0. A read that carries a player byte is thrown away when that byte is not the port's player plus 3, the check BBAPI.cs makes on every read.

| Report | Direction | Layout |
| --- | --- | --- |
| 17 | get | type, flags (bit 0 set while the port searches for a controller), firmware major, player + 3, firmware minor |
| 18 | set | the command report: 18, command, 0, 0, up to five parameters, 9 bytes |
| 20 | set | 20, `0x24`, 0, 0, the 192-byte picture in wire order, one spare byte, 197 bytes |
| 21 | get | player + 3, then twelve pressure bytes |
| 22 | get | player + 3, use, size, then the controller's answer |
| 24 | get | player + 3, then the stored picture in wire order |

| Command on report 18 | Parameters |
| --- | --- |
| 4, large motor | type, strength, loop: `0, 0, 0` stops it, `1, strength, 0xFF` runs it |
| 5, small motor | the same |
| 8, player | player + 3, then 1, which resets the port so it returns under the new product ID |
| `0x25`, native channel | a header, then five-byte chunks |

### The cadence

| Work | When |
| --- | --- |
| Report 17 | every 500 ms |
| Report 21 | every 50 ms, only while a DualShock 2 is in the port |
| A running motor | on a GPA again every 100 ms, and a changed level at once. On 3.x, both motors together at most once every 100 ms, a steady level again once a second and a refused write with the next |
| The VMU picture | only when it differs from the one the adapter holds, at most once a second |
| The native arrow poll | 16 ms after each answer, only for a PlayStation digital pad on a 3.x adapter with the port's choice on, until the adapter sends the arrows itself |
| A queued job | on the next step, holding the channel until it ends |

The info and pressure polls run no faster than DeviceBuddy's (report 17 every 500 ms, report 21 every 50 ms), because BBAPI.cs warns that the adapter skips a controller poll for each control transfer. The native arrow poll is faster, and runs only while a port's choice asks for it.

On 3.0 the cost is specific. A write, and a read of report 22, set a flag (`0x090B`, `0x07D6`) that makes the main loop's next pass send its last report again instead of polling the pad (`0x31C6`, `0x31DD`), and a read of report 24 costs three passes (`0x0806`). Reads of reports 17 and 21 cost nothing. A pass sends the report as two interrupt transfers and waits for the host to take each one (`0x35F5` to `0x364A`), so it lasts two host polls. GPA 4.86 handles a write in its USB control path, with no such flag. A picture write holds the pad's input still either way while the adapter stores it: GPA 4.86 writes the EEPROM inside its handler (`0x2D58` calling `0x290B`), and 3.0 flags every 8-byte piece of the transfer.

### The native channel

A message to the controller is a header, `18, 0x25, 0, size high, size low, use, first byte, second byte, 0`, then five-byte chunks, `18, 0x25, position, five bytes, 0`, the last marked with position `0xFF`. Both firmwares keep only the size's low byte (GPA `0x2D20`, 3.0 `0x0954`). The generations place the last chunk differently, so `NativeReports` takes the firmware generation from report 17:

- The 3.0 firmware places a `0xFF` chunk at the previous chunk's position plus five, from RAM it never resets between messages (`0x0967` to `0x096B`), copies five bytes, and keeps every chunk's position as the last one, the `0xFF` chunk's included (`0x0983`). A message whose data fits one chunk goes positioned and then closed by an empty `0xFF` chunk, as BBAPI.cs sends it.
- GPA 4.86 places a `0xFF` chunk that follows the header at position 2, and one that follows a positioned chunk at that position plus five, and copies the size minus that position (`0x2D47` to `0x2DAF`). After a positioned chunk at 2, a message of 3 to 6 bytes makes that count negative, and the copy runs over the adapter's RAM, the player byte at `0x0698` included. So a message whose data fits one chunk goes as a lone `0xFF` chunk, the shape DeviceBuddy gives messages of 3 to 6 bytes.

A message is 252 bytes at most (`BlissBoxProtocol.MaxNativeMessage`), which keeps the 3.0 firmware's five-byte copy of the last chunk inside the first 256 bytes of its buffer at RAM `0x0681`. The longest message PadForge sends is a Controller Pak write, 35 bytes.

A longer message ends with its last data in a `0xFF` chunk after the positioned ones, which both read alike. BBAPI.cs's count drops the last one to three bytes of messages of 28 to 30 bytes and every 25 bytes after, and adds a chunk for some other lengths, which a GPA reads as a negative count. The count here is exact.

The reply is report 22, read up to 20 times 20 ms apart, as BBAPI.cs's `getData` does. A matching player byte with use 0 means the controller gave no answer, and use 1 with size 0 means the answer is not ready yet. The 3.0 firmware runs the exchange from its main loop (`0x30B9` to `0x30ED`), not inside the transfer, and only in a pass whose flag is clear (`0x30D9`), so a read that comes right after the message can find it not yet run, and the next read comes 20 ms later. The message's write and each read of the answer cost the adapter a poll of its own. GPA 4.86 runs it inside the transfer (`0x2D32` to `0x2D44`) and answers at once. The 2.0 firmware frames the channel another way, three message bytes in the header and no use byte (`0x0832` to `0x0862`), so PadForge uses it on 3.0 and later only, which is where the API Tool's memory manager runs too (memManager.cs: "3.0 is required for this feature!").

---

## Input

### Names

`SdlDeviceWrapper.GetDeviceObjects` asks `BlissBoxApi.DeviceObjectsProvider` for a raw-opened port's list, so every place that fills `DeviceObjects` stays in step. `BlissBoxRuntime.NameObjects` renames the joystick's objects for the controller report 17 names, names the four arrow buttons where the firmware sends them (see [Pressure and arrows](#pressure-and-arrows)) unless the controller's layout names those buttons itself, and appends the twelve pressure axes for a DualShock 2. Arrow buttons the joystick does not declare are appended only for a 3.x PlayStation digital pad, whose arrows PadForge's native poll fills. Both firmwares declare 24 buttons, so on a real adapter nothing is appended. The names are invariant English strings that `MappingDisplayResolver.LocalizeObjectName` translates. `BlissBoxRuntime.NamesObjects`, which `UseRawNumberedNaming` asks, is true for a controller a source lays out and for a DualShock 2, whose pressure axes carry names on every firmware. Any other controller keeps numbered names, as a raw joystick does. The names, the merge and the rest rule follow the row's shape, not the switch: they apply while the row is read raw, until Step 1 reopens it.

The tables in `BlissBoxControllers` come from RetroArch's Bliss-Box 4-Play autoconfig files, stamped firmware 3.24, for 3.x, and from DeviceBuddy's controller layouts for 4.x. A layout's bit N is button N, its stream bytes 3 to 10 are axes 0 to 7 (X, Y, Z, Rx, Ry, Rz, slider, dial), and byte 11 is the hat. The sources agree on the PlayStation, Nintendo 64, Saturn, TurboGrafx-16, 3DO and Wii Classic, and differ on the NES's A and B, the SNES's X and Y, the Genesis's C and Z, the Dreamcast's and GameCube's shoulders and the Jaguar's A and C, which is why each generation keeps its own. A 2.x adapter gets no layout, so its controllers keep numbered names, except a DualShock 2, whose named pressure axes leave its other objects with the joystick's own names (`X Axis`, `Button 3`).

Analog triggers follow the firmware instead. Both generations copy the GameCube's, the Dreamcast pad's and the Saturn 3D pad's triggers into Z and Rz as they come from the pad, 0 released: 3.0 at `0x1042` (GameCube), `0x283B` (Dreamcast) and `0x19A4` to `0x19DC` (Saturn), GPA 4.86 at `0x0F72`, `0x0DEA` and `0x1A73`. The 3.0 image Bliss-Box distributes reports itself as 3.34 and leaves the Slider and Dial at their center (`0x311B`), where RetroArch's GameCube file puts the shoulders with unsigned binds RetroArch ignores. DeviceBuddy's Dreamcast layout leaves the triggers undrawn, beside the digital L and R the GPA sets past `0xC8` (`0x0DB2`).

Type codes come from the API Tool's `controllerType[]`, the command-line tool's `getType` and DeviceBuddy's `BlissBox_lookUpName`, with the compatibility list naming the abbreviated ones. Types 0 and 255 are both "None / Atari" in the API Tool, 255 being what an unflashed type byte reads. The generations number two controllers differently, so `BlissBoxControllers.Name` takes the firmware's major version. GPA 4.86 types an Atari driving controller 12 in its DE-9 driver (`0x2436`) and returns 66 from the same driver (`0x22D7`), which DeviceBuddy calls drivingcontroller and TOWNS. The 3.0 firmware returns 66 for a Wii extension (`0x23A9` to `0x23BB`), which the API Tool calls WII_DRUM, and the API Tool calls 12 PSX_WHEEL. The 2.0 firmware sends a PlayStation pad's ID as its type (`0x219B` to `0x21B1`), where the newer ones turn the neGcon's `0x23` into 51 and the JogCon's `0xE3` into 127 (3.0 `0x253A` to `0x2546`, GPA `0x0A18` to `0x0A2B`), since `0x23` is their Dreamcast Twin Stick (`0x2824`, `0x0E91`). `BlissBoxProtocol.ParseInfo` makes the same two changes for firmware before 3. Every other PlayStation ID passes through on all three, so a PlayStation mouse (`0x12`) reads as type 18, which the tools and PadForge name the GameCube wheel. A type no source names shows as its number, in the user's language.

### Pressure and arrows

`BlissBoxRuntime.Merge` runs in Step 2 right after SDL's read, ahead of the idle detector and every later consumer. It writes each pressure byte times 257 into the axis at `max(8, declared axes) + i`, where the declared axes are the joystick's own count, and adds the native poll's directions to the arrow buttons. The state is a fresh pooled one each read, so a port that stops publishing leaves them at rest. While the adapter searches, the merge puts the last controller's trigger axes at rest instead (`BlissBoxRuntime.RestTriggers`). The searching report holds 0x80 on the axes (3.0 `0x3103` to `0x3117`, GPA `0x28B9` from RAM `0x02F0`), or 0 on Z and Rz in the modes that clear them (3.0 `0x310C`, GPA `0x28C4`), and the rest rule still reads those axes as triggers.

The pressure order is the DualShock 2's own, which psx-spx gives and every firmware copies into report 21 unchanged: Right, Left, Up, Down, Triangle, Circle, Cross, Square, L1, R1, L2, R2. The 2.0 firmware stores the pad's reply in order (`0x21F7` to `0x2204`) and copies the pressures across (`0x2313` to `0x231C`), and 3.0 does the same (`0x2646` to `0x2651`). The API Tool's branch for 2.x reads the face buttons from other bytes, which the firmware does not bear out.

The pressure axes and the analog triggers rest at 0 and travel one way, so the #443 rule treats them as a trigger: an axis activator on one engages past its threshold in that one direction instead of reading -1 at rest. Read raw, a port is a joystick, whose axes otherwise count as centered. `BlissBoxRuntime.RestsAtZero`, which `InputManager.AxisRestsAtZero` calls, asks `BlissBoxControllers.IsTriggerAxis` about the controller in the port, or about the last one identified there through a reopen and while the adapter searches (`BlissBoxSession.KnownInfo`). For up to one report 17 poll after a controller leaves, the adapter already sends its idle 0x80 on the triggers, which the rule reads as half pressed. Until a new port reads report 17 for the first time, a few milliseconds after the switch goes on or the engine starts, the controller's trigger axes count as centered. A Remote Link peer's copy of a port finds no port on that PC. It takes the owner's shape, a joystick while the owner reads the port raw, so its pressure axes rest at 0. The device list does not say which controller is in the owner's port, and the owner sends no object list for a joystick, so the peer names axes 2 and 5 as a gamepad's triggers whatever the pad is. They count as centered there, as for every raw joystick a peer exposes, which is right for a DualShock's axes and wrong for a Dreamcast pad's, Saturn 3D pad's or GameCube controller's triggers. When the owner's switch changes the row's type, the peer registers the device again with the owner's new button and axis sets, so its row takes the new shape (`LinkServer.ReconcileRemoteDevices`, `RemotePeerDevice.RefreshSupportedSets`).

The Saturn racing controller and mission stick report type 8, the 3D pad's (GPA `0x1A1E`). Both firmwares store the pad's third analog byte in Rz and its fourth in Z (3.0 `0x19EB` to `0x19F1`, GPA `0x1A94` and `0x1A75`), and start each of them at 0x80 (3.0 `0x191C` to `0x191F`, GPA RAM `0x02F0` to `0x02F7`). Mednafen's Saturn peripherals send the 3D pad's analog bytes as X, Y, right shoulder, left shoulder, the mission stick's as X, Y, throttle, and the racing controller's wheel alone (`ss/input/3dpad.cpp`, `mission.cpp`, `wheel.cpp`). So the throttle reads as Right Trigger, and an axis the controller does not send stays at 0x80, which the trigger rule reads as half pressed.

Both firmwares turn a D-pad into a hat and drop opposite directions from it, and both send the four directions as buttons of their own once opposite directions have been pressed (`BlissBoxControllers.FirstArrowButton`):

- The 3.0 firmware latches RAM `0x0354` when left and right, or up and down, come in together and from then on ORs the direction bits into the second button byte, buttons 10 to 13 (`0x3295` to `0x32A9`). Every controller takes that path but the NES Zapper, which skips the D-pad code (`0x321E`). The latch clears at power-up (`0x2FAB`), on the path that restarts the main loop (`0x3671`, back to `0x2FD8`), and when a search starts after a controller the search loop found (`0x3163`, gated on `0x0356`, which only the search loop sets, at `0x31AE`). A pad present at power-up is found outside that loop (`0x3096`), so it can leave the latch set for the next one.
- GPA 4.86 latches RAM `0x055E` the same way and writes them into the third button byte, buttons 20 to 23 (`0x34A1` to `0x34B9`). The latch is never set by the Genesis 3-button pad or the FM Towns pad (`0x349B` to `0x34A0`), but once it is on, the arrows go out on every poll (`0x34BC`), those two pads included. It starts at power-up from EEPROM `0x3D` (`0x373A`), which a settings command writes (`0x2CFB` to `0x2D02`), and ends at power-off. Every poll of a ColecoVision controller, Super Action Controller or ColecoVision wheel (types 1, 34 and 79) clears it (`0x23DD`), and that path writes the third button byte itself (`0x23E5`). The Atari driver clears it when it retypes a joystick as a Trak-Ball (`0x2408` to `0x241B`), and the two routines that restore the defaults clear it and store 0 at EEPROM `0x3D` (`0x2C6A` and `0x2C6F`, `0x36A0` and `0x36A5`). The PC-FX pad's own inputs share two of those bits (`0x16AA` to `0x16BD`). PadForge names the arrows for none of the Genesis 3-button, FM Towns and PC-FX pads, and no GPA layout exists for the ColecoVision three.

Only a controller whose layout names a D-pad gets the arrow names. One without a D-pad cannot press opposite directions, and the keypads of the Jaguar and the Atari 5200 sit on buttons 10 to 13 on 3.0 (`0x2099`, `0x1BDA`). A controller with a D-pad that no source lays out keeps numbered names, and the firmware's arrows arrive on those numbered buttons.

The native poll gets the arrows from the first step, before any latch. It sends a PlayStation pad `0x01, 0x42, 0, 0, 0` and searches the answer for `0x41, 0x5A`. The next byte is active low, with Up in bit 4, Right in bit 5, Down in bit 6 and Left in bit 7, the psx-spx order Linux's `psxpad-spi` reads. The merge adds them to buttons 10 to 13, where the 3.0 firmware's own arrows land.

Each request costs the adapter polls of its own (see [The cadence](#the-cadence)), so the poll stops once the adapter's own arrows show on buttons 10 to 13 of the port's report, which for a PlayStation digital pad only the latch sets. The merge reads those buttons before it adds the poll's (`BlissBoxRuntime.ArrowsSent`). `BlissBoxSession.ArrowsLatched` clears when report 17 shows another controller or a search, or when the channel drops. If the firmware kept its latch through that, the merge sees its arrows again and sets the flag again.

---

## Rumble

`BlissBoxApi.OwnsRumble` is true for a port while the switch is on. Then:

- `SdlDeviceWrapper.HasRumble` is true whatever SDL found, since the adapter's commands drive the motors and the controller in the port can change without a reopen. With the switch off it is SDL's answer again.
- `SdlDeviceWrapper.SetRumble` refuses the port, because SDL's DirectInput path averages both motors into one sine effect.
- Every other site that routes the Padix converter's motors routes a port's too: Step 2's sole-writer write and its unassign stop, `StopAllForceFeedback`, the relayed rumble in `InputService`, and the Identify pulse train.

`BlissBoxSession.Strength` maps PadForge's 0 to 65535 onto the strength byte as `(level + 255) >> 8`, clamped to 1 to 255, with 0 for off. Type 1 reads a strength of 0 as full, so a small level rounds up rather than down to it.

`BlissBoxControllers.MotorCount` follows the API Tool's rumble form (rumble.cs):

| Controller | Motors | Commands |
| --- | --- | --- |
| DualShock (115), DualShock 2 (121), neGcon (51), JogCon (127) | 2 | 4 takes the low-frequency level, 5 the high-frequency one |
| GameCube (9), Dreamcast (16), N64 (19), Dreamcast fishing rod (73) | 1 | 4 alone, at the stronger level |
| Everything else | 0 | none |

The form offers the fishing rod a second test, but GPA 4.86 reads the rod through its Dreamcast driver (`0x0DE1`), so it takes one motor. A one-motor pad never gets a level on command 5, because GPA 4.86's Dreamcast driver runs command 5 through the routine at `0x0C2A`, which forces full power whatever strength it is given. On 3.x, command 5 is command 4's alias for these pads (`0x10BC`, `0x2942`, `0x270A`). A pad with no motors gets nothing, because the 3.0 firmware skips its next controller poll after every write (`0x090B`, `0x31C6`). Neither firmware checks the type itself, and the drivers without motors answer commands 4 and 5 with a bare `ret`.

The session keeps the wanted levels, and the worker is woken only when they change. A write the adapter refuses is tried again 100 ms later, not on every step. On 3.x, where every write costs the adapter a controller poll, both motors go out together at most once every 100 ms, the rate the API Tool writes them at, and a change waits for the next of those writes (`BlissBoxSession.WriteMotors`). A game that changes its rumble every frame would otherwise have held the pad's input still. Each write carries the strongest level asked for since the last write that went out when that is above what the motor runs, and the level asked for now otherwise (`BlissBoxSession.Carried3x`), so a pulse between two writes is still felt and a pulse the running motor already covered never holds back a stop. The levels are taken before the write is decided and go back when a write is refused, and a refused write goes again at the next paced write. Writes in one pass cost one poll between them, since the flag is set rather than counted, so a running motor rides along with the other's. The PlayStation, GameCube and N64 drivers count a loop of 255 down once a poll (`0x2500`, `0x0FF5`, `0x29FD`), about 4 s, and the Dreamcast driver never counts one down, so a steady level is sent again once a second (`BlissBoxSession.RumbleHold3xMs`). A GPA takes a change at once and is told again every 100 ms, since its loop of 255 is a 255 ms timer (`0x2A16`).

When the channel drops and reopens, report 17 shows another controller or the same one back, SDL hands a port over, or a GPA stores a picture, each motor is told its level again, a stop included, since the adapter may have kept the last one. Each motor keeps its own flag for that, so one whose write went through is not sent again while the other's keeps failing, and a request made while a write is in flight is kept for the next step. On a GPA a one-motor pad's resend starts with a stop on command 5, which clears a command-5 rumble PadForge never sent, and command 4 right after sets the strength that stop forced to full (`0x0C2C`, `0x0E3D`). The level counts as delivered only when both went through, since a loop left on command 5 keeps the pack powered at every poll once command 4 holds the timer (`0x0E0A` to `0x0E24`). The resend a picture write owes goes out right after the write, in the step or the job that wrote it.

The quiesce that runs on a crash or an abnormal exit stops every port's motors with no pulse still owed (`BlissBoxSession.StopRumble`) and waits up to 250 ms for every port to send the stop. The engine's stop and the quiesce's first sweep stop the ports the same way (`BlissBoxRuntime.StopRumble`). A 3.x pass takes the levels and puts back a refused write's under the same lock as the stop, so a stop never lands between a pass's check and its return, and a pass that took the levels before a stop landed neither carries nor puts back the pulse the stop dropped. The stop is asked again each time the quiesce looks, so a level a writer that had passed the quiesce check sets after the first stop is stopped too. A write the adapter refused keeps its motor out of rest until one goes through, since the channel reports a transfer that outlived its wait as failed although the adapter may have taken it, and a GPA tries a refused write again even at the level it wanted. A row that goes offline drops its port's levels, which the SDL stop there never reaches. Once the quiesce has run, a relayed Remote Link frame is not applied, so a peer's game cannot start a motor again behind it. A port whose adapter is searching counts as stopped, with no controller in it to stop. A motor pass in flight counts as running, since a resend's flag clears as its write starts: `MotorsAtRest` reads the motor fields between two reads of a pass count the worker keeps odd during a pass. A pulse asked for since the last 3.x write counts as running too. A port whose channel reopened counts as running until report 17 is read and the stop goes out, since the adapter may have kept the level and neither firmware ends every rumble on its own. The 3.0 Dreamcast driver never counts down the loop of 0xFF a type-1 command sets (`0x0A89` to `0x0A97`, `0x2858` to `0x285F`), and a GPA's one timer stops only the command that last took it (`0x29F7` to `0x2A14`). A picture write holds the worker for up to 2 s, about 650 ms for a picture that changes every byte, so on a port playing a Dreamcast show the stop can miss the 250 ms.

A change of the switch counts in `BlissBoxRuntime.Generation`, which brings Step 1 forward to the poll thread's next cycle (`InputManager.ConsumeBlissBoxSwitchChange`), so the rows, the ports and the motors move together, in order. The loop keeps its own copy of the generation, so a phase before 1l that throws costs one extra pass, not one every cycle. Switched on, the rows reopen raw and the ports open. Each port's hand-off stops SDL's rumble. That is the only effect SDL runs on a port, since SDL opens no haptic device for one: the fork's database maps all four IDs as a gamepad (`SDL_gamepad_db_community.h:289-292`), and `SDL_IsJoystickHaptic` refuses a gamepad (`SDL_haptic.c:310-311`). A stop SDL refuses leaves that effect running beside the adapter's commands, so the hand-off waits and tries again. The hand-off then gives the port the levels the row last recorded, whichever writer recorded them (Step 2, a relayed frame, or SDL's path before the switch), and tells both motors again (`BlissBoxRuntime.TakeMotors`). On a GPA, SDL's stop can reach a one-motor pad's command-5 routine through DirectInput's effect block (`0x2E8C` to `0x2EC3`), which that resend clears in the port's first step with report 17 read. The row keeps its motor state through the switch's reopen, since a fresh wrapper for the same SDL instance is the same connection (`UserDevice.SameConnection`), so the port and the row's motor snapshot agree and the change detection that gates every later write holds for both. A relayed Remote Link frame follows the row to the fresh wrapper for the same reason, although the exposure keeps the old one until its 2 s refresh. The old wrapper is disposed by then, which clears its instance ID, so it is matched by the instance it was opened on (`SdlDeviceWrapper.ConnectionId`). SDL never reuses an instance ID.

Switched off, the rows reopen through SDL's mapping and every port retires, each sending its final stop, which on a GPA reaches the routines SDL's effect drives. Only once a port's worker has exited does its row give SDL the levels it last recorded, the cache recording them as sent (`ForceFeedbackState.ResendScalar`), since a Remote Link peer sends a steady level once. A stop goes to SDL first, because SDL skips a write that repeats its last levels (`SDL_joystick.c:2287-2290`) and a GPA's final stop can end a level SDL took while the port was retiring. The resend counts as delivered only when SDL took both, and a row is tried again until it does: SDL's record can hold a level the final stop ended, and a later frame's write of the same level then reports success with nothing sent. A row SDL found no motors on takes no level and drops the recorded ones, so a stale level never goes back to the port at the next switch-on. The hand-off and the resend take a row's output gate only when it is free, as Step 2 does. A pending hand-off or resend is tried again every 100 ms (`InputManager.RetryPendingBlissBoxRows`). A port that takes over a retired port's path tells both motors their levels again once the old worker has exited, since that worker's final stop can land after the new port's first write (`BlissBoxRuntime.HandOverToSuccessor`). A switch that went off and on again between two passes still reopens the rows and hands every kept port its level, since SDL's path may have driven it in between.

Step 2 folds the trigger channels into the two body levels when the device's **Fold Trigger Rumble into Main Motors** is on (`ForceFeedbackState.FoldTriggersForDirectWriter`), as `SetDeviceForces` does on SDL's path, for a port and for the Padix converter alike.

Identify on a port in no slot writes its pulses without recording them in the row's motor snapshot, because a recorded pulse made Step 2 send the row's final zero on the next poll. The train ends at the levels the row's snapshot holds, zero unless a Remote Link peer drives the row, whose steady level a zero would end for good. A Remote Link peer's row carries the owner's VID and PID, so Identify never writes a port's path for one, a path that exists only on the other PC. An unmapped peer row buzzes nothing, since the peer device's rumble event has no subscriber. A mapped one buzzes through its slot, whose rumble Remote Link relays to the PC the pad is on.

---

## The Dreamcast screen

### The picture

PadForge keeps a picture in image order: 48 by 32 pixels, rows top to bottom, 6 bytes a row, the leftmost pixel in a byte's high bit, 1 for dark. The adapter takes it rotated 180 degrees, since the VMU sits upside down in the pad: byte `k` of the image, bit-reversed, is byte `191 - k` on the wire (dLCD.cs `writeToLCD`, and DeviceBuddy draws report 24's pixel `(x, y)` at `(47 - x, 31 - y)`). The transform is its own inverse.

A VMU Animator `.lcd` file has a 16-byte header and 4 bytes of frame information, then one byte per pixel with `0x08` for dark. An ICONDATA_VMS file, the `.vms` that holds a VMU's icon alone, keeps the offset of its 32 by 32 icon as a 32-bit little-endian value at byte 16, which is centered with 8 blank pixels either side. Other images are drawn on a white field, scaled down to fit, and cut at half luminance. Text is drawn with Segoe UI Bold, aliased, as large as fits.

### The EEPROM guard

GPA 4.86 runs avr-libc's `eeprom_update_byte` over EEPROM `0x00A0` to `0x015F` for report 20, and the 3.0 firmware writes the same range for command `0x24`, so every picture lands in EEPROM, rated at 100,000 writes. The session writes a picture only when it differs from the one it last read or wrote, and never sooner than 1000 ms after the last write. A clock or play timer changes its digits once a minute. Each step writes the motors, then the picture, then the motors again when a picture went out, so the resend a GPA picture write needs goes out in the same step, and a 3.x motor write never waits on a picture. A job's picture write sends that resend itself. A picture write gets 2000 ms to finish (`BlissBoxSession.ScreenWriteTimeoutMs`) where every other transfer gets the channel's 500 ms: both firmwares store the picture before they end the transfer, and the ATmega32U4 erases and writes a byte in 3.4 ms (its datasheet's Table 5-2), about 650 ms for a picture that changes all 192 bytes. The API Tool waits on hidapi's `hid_send_feature_report` without a limit.

Before GPA 4.86 handles report 20 it calls the controller driver's slot at offset 10 with `0xFF, 10` (`0x2BEF` to `0x2BF9`), as it does for every feature report but `0x0F` and commands `0x25`, 4 and 5. For a Dreamcast pad that slot is the routine at `0x0C2A`, which forces full power and arms a 10 ms rumble. A picture that changes several bytes takes longer than that to store, so whether a frame reaches the jump pack depends on the write. The firmware keeps one pending timer (`0x2A16`), so the call also takes the timer from a command-4 rumble in progress, which would then run at full power with nothing to stop it. The session sends a one-motor pad a stop on command 5 and its level on command 4 right after the write, in the step or the job that wrote it (see [Rumble](#rumble)). The 3.0 firmware makes no such call for its screen command.

### The modes

`DreamcastScreenService.Tick` runs on the UI thread from the UI timer while the engine runs, whether or not PadForge has focus, four times a second, and at once after a port's choices change. It ticks with no port open too. A show belongs to the port instance it started on, as play time does, so it ends with that port, a row that reconnects included, and the engine's stop resets the service once its poll thread and ports have stopped, so a macro cannot queue a show behind the reset (`DreamcastScreenService.Reset`). For each port with a Dreamcast pad (types 15 and 16) it waits until the adapter's stored picture has been read, then composes the picture for the port's mode, a macro show taking the screen while it plays. Before the first picture that differs from the adapter's own, it keeps that picture, in wire order, in the port's settings, and saves the settings file at once rather than after the autosave's quiet time, which a crash, a kill or a reload could beat (`DreamcastScreenService.MayReplace`, `SettingsService.SaveNow`, which raises `AutoSaved` as the timer's save does). Until a save has carried the copy to disk, the port keeps its own picture. The copy is held before the save runs, so a save that throws still holds it, and the hold ends on the next file the settings service writes (`SettingsService.SaveCount`), not on its unsaved flag, which a reload that finds no file clears without writing. Adapter mode writes it back and forgets it once the adapter holds it again. The copy is kept per row, and a port's row is identified by its device path, since SDL reports no serial number for it. An adapter moved to another USB port can come back under another path without its copy, and another adapter that comes up under the first one's path finds that copy as its own.

Play time counts from the tick that first finds the pad in its port. A pad the port loses and finds again within 10 s keeps its start (`DreamcastScreenService.TrackPad`, `PlayStart`), so the adapter searching for a moment, or the channel reopening, is not a new session. A port that closes and opens again starts over.

A Show Dreamcast Screen action queues a show from the poll thread, up to 16 waiting, and the next tick starts it on every Dreamcast pad in a port whose device is assigned to the macro's slot. A show with no port open is dropped, and one queued as the last port closes is dropped by the next tick. Each frame lasts its frame time, at least 1000 ms, from the moment the adapter holds it (`DreamcastShow`), so the EEPROM guard's second between writes never drops a frame. A frame that has not arrived after 5 s counts from when it became current, so a port that refuses writes cannot hold a show forever. The tick wakes a port's worker when the picture it wants changes.

### Saved state

`AppSettings.BlissBoxEnabled`, `AppSettings.BlissBoxPorts` (one `Port` per device: `Device`, `ScreenMode`, `Picture`, `NativeArrows`, `AdapterPicture`, dropped when every value is its default) and `AppSettings.DefaultProfileDreamcastPicture`. On load, `BlissBoxPortData.Normalize` drops a picture that does not decode to 192 bytes, since a copy of the adapter's own that could never be written back would block a new copy, the restore and the entry's cleanup for good, and then drops an entry left at every default before it counts the device as seen, so an empty entry never hides a real one after it. Reset to Defaults keeps each port's `AdapterPicture` (`BlissBoxPortData.KeepAdapterPictures`), the only copy of a picture PadForge replaced. A player change writes that picture back before it sends the command and drops the port's entry, since the port returns as a new device. Exporting the Default profile carries its picture, which lives in the settings file rather than on its snapshot. A named profile keeps its picture in `ProfileData.DreamcastPicture`, which no state save copies over. The macro action saves `DreamcastFrames` (base64 pictures joined by commas, eight at most), `DreamcastFrameMs` and `DreamcastRepeat`. `DreamcastScreenMode` is saved by name.

---

## The Controller Pak

Every transfer rides the native channel as the Joybus command the pak takes. The frames and checksums are the API Tool's (memManager.cs `memManagerLoadData`, `getN64Data`, `writeToPort`, `getCrc5`, `getCrc8`), and the checksums give the same values as libdragon's `joybus_accessory_calculate_addr_checksum` and `joybus_accessory_calculate_data_crc`.

| Command | Message | Answer |
| --- | --- | --- |
| Status | `0x00` | two identity bytes and a status byte, whose low two bits are 1 (present) or 3 (present and changed) when a pak is in |
| Read | `0x02`, address field | 32 data bytes, then their CRC-8 |
| Write | `0x03`, address field, 32 bytes | the CRC-8 the pak computed over what it stored |

The address field is the block's byte address, `block × 32`, with a CRC-5 of the 11-bit block number in its low five bits (generator `0x15`). The data CRC is a CRC-8 with generator `0x85`. A CRC that comes back inverted means no pak answered. Block 0 reading `0x80` with CRC `0xB8` is a Rumble Pak, the API Tool's "Looks like a rumble pack!" test.

A backup checks the firmware, the controller, the status and block 0, then reads 1024 blocks, each up to three times. A block that never answers fails as no reply, and one whose CRC keeps failing as a bad block. A read that comes back without its 33 bytes is no answer: the 3.0 Joybus routine returns early for such a read (`0x0FA8`), leaving the message in its buffer, and report 22 then reads the command byte as a size and answers with the two address bytes after it (`0x07D3`), while a GPA answers with none (`0x2874`). A restore writes each block until the pak confirms it, and gives up once more than 16 writes have failed, the API Tool's limit, reporting no reply when the write that reached the limit drew no answer. Both stop before their next message to the controller when the port closes. A job queued once the port is closing ends at once, and one still queued when the channel drops ends as closed. `BlissBoxSession.Busy` holds the Devices page's player and pak buttons while a job is queued or running.

A player change does not trust the write's result: both firmwares reset from inside the command's handler, before the transfer completes (3.0 detaches USB at `0x08EB`, GPA 4.86 jumps to its reset at `0x2CE2`), so Windows can report the write as failed although it took. BBAPI.cs sends it without checking. PadForge reads report 17 afterward instead, up to three times 100 ms apart: an adapter that reset answers nothing on the old handle, and one that still answers as the port's player never got the command, so the job fails as `PlayerUnchanged`. The three reads keep one failed read on a port that kept its number from passing for the reset. The job fails the same way, without sending the command, when the adapter refuses its own picture back, and a port that is closing, or starts closing while the picture waits out the EEPROM guard, sends neither.

---

## Tests

`BlissBoxProtocolTests` builds every report byte for byte, runs every parser against the references' layouts, checks the picture codec against the API Tool's "BLISS BOX" example, the checksums against libdragon's values, and the native chunking under models of both firmware listings. `BlissBoxSessionTests` drives a session against a scripted adapter that answers as either generation does, with an N64 controller and a pak behind its native channel, a not-ready first read after each message, the 3.x echo of an unanswered read, the reset a player change causes, and GPA 4.86's Dreamcast motor routines (the shared strength, each command's loop and the one timer): the poll cadence, the motor model and writer's timing, the 3.x pacing with its peak and its refresh, a write in flight, the EEPROM guard, the native arrow poll, the player change, and the Controller Pak backup and restore with their failure paths. `BlissBoxAppTests` covers the names per controller and their translations, the object list and the state merge, the rumble routing, the raw open, the settings, the screen service's pictures and the macro action.

No test runs against an adapter. PadForge's reading of every report is unverified on hardware.

---

*Last updated for PadForge 4.5.3.*
