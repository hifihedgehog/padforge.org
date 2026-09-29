# Bliss-Box Internals

*How PadForge pairs an API sidecar with each Bliss-Box port's SDL row, and every report it sends and reads.*

For the user-facing side see [Bliss-Box Adapters](../features/bliss-box.md).

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

The app side: `PadForge.App/Common/Input/BlissBoxPort.cs` (the HID channel and the worker thread), `BlissBoxRuntime.cs` (the ports, their pairing with SDL rows, the state merge, the object names), `InputManager.BlissBox.cs` (Step 1's phase 1l), `PadForge.App/Services/DreamcastScreenService.cs` (the VMU screens and the ports' saved choices), `InputService.BlissBox.cs` (status lines and the Devices page row), `MainWindow.BlissBox.cs` (the row actions), and the two dialogs `BlissBoxPlayerDialog` and `DreamcastScreenDialog`.

---

## The shape

SDL reads each port's joystick, as it reads any USB joystick. A port is one USB device per player, vendor `0x16D0`, product `0x0D03` plus the player number, so `0x0D04` to `0x0D07`. The bootloaders (`0x0A5F`, `0x04FB`), the 1.x firmware (`0x0A60`) and the "4-Play Fix" IDs (`0x0A61` to `0x0A64`) never match, so nothing talks to an adapter mid-update.

With **Read Bliss-Box Adapters** on, a `BlissBoxPort` opens a second handle on the same HID collection, beside the SDL row, and owns what the joystick report cannot carry. This is the Padix converter's shape (#440): SDL for input, PadForge's own writes for the rest.

### Raw reading

The SDL fork carries SDL_GameControllerDB's mapping for all four IDs, "4Play Adapter", so SDL would open a port as a gamepad. That mapping describes one layout, while the adapter's report follows whatever controller is plugged in. While the switch is on:

- `SdlDeviceWrapper.OpensAsGamepad` skips `SDL_OpenGamepad` for a port (`BlissBoxApi.ReadsRaw`), so the row reads the joystick surface.
- `SdlDeviceWrapper.InputDeviceTypeFor` types the row a Joystick, although `SDL_GetJoystickType` still says gamepad for a mapped device. The gamepad auto-map and the trigger rest rule for axes 2 and 5 then leave it alone.
- Phase 1l reopens any port row open the other way: every cycle while the switch is on, since a row can open between the switch and the phase, and once more after it goes off. The reopen is Phase 1's replug rebind: a fresh `SdlDeviceWrapper` for the same SDL instance, `UserDevice.LoadFromSdlDevice`, which disposes the old wrapper, and the new wrapper in `_openedSdlInstanceIds`. SDL counts the opens of one joystick and one haptic device, so the device stays open across the swap.

### The channel and the worker

`AnalogKeyboardHidChannel.OpenShared` opens the collection shared for read and write, as hidapi opens it for the API Tool, and falls back to no access rights, which still carries feature reports. The input queue is held to two buffers, since nothing reads it. Feature reports are padded to the collection's feature report length.

One worker thread per port runs `BlissBoxSession.Step` back to back and sleeps for the time `Step` returns, woken early when another thread sets a motor level or queues a job. That serializes every control transfer, as BBAPI.cs's `CT_IO` flag does. The worker opens the channel once a second while it will not open, closes and reopens it after three failed info reads in a row, and on its way out stops both motors, ends every queued job as closed and closes the handle. Closing the channel forgets everything read from the adapter and ends the jobs still queued, since they were asked of the controller that was in the port before.

`BlissBoxRuntime.Sync` pairs ports with rows on the poll thread by HID path and instance GUID, opens a port for a new row, and retires a port whose row left, disposing it on the thread pool so a transfer in flight never holds up the poll thread. A port that opens hands its motors over from SDL: any SDL effect stops, and the row's motor cache starts from rest.

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
| A running motor | again every 100 ms, and at once when its level changes |
| The VMU picture | only when it differs from the one the adapter holds, at most once a second |
| The native arrow poll | every 16 ms, only for a PlayStation digital pad on a 3.x adapter with the port's choice on |
| A queued job | on the next step, holding the channel until it ends |

Nothing polls faster than DeviceBuddy (report 17 every 500 ms, report 21 every 50 ms), because BBAPI.cs warns that the adapter skips a controller poll for each control transfer.

### The native channel

A message to the controller is a header, `18, 0x25, 0, size high, size low, use, first byte, second byte, 0`, then five-byte chunks, `18, 0x25, position, five bytes, 0`, the last marked with position `0xFF`. The generations place that last chunk differently, so `NativeReports` takes the firmware generation from report 17:

- The 3.0 firmware places a `0xFF` chunk at the previous chunk's position plus five, from RAM it never resets between messages (`0x0967` to `0x0983`), and copies five bytes. A message whose data fits one chunk goes positioned and then closed by an empty `0xFF` chunk, as BBAPI.cs sends it.
- GPA 4.86 places a `0xFF` chunk that follows the header at position 2, and one that follows a positioned chunk at that position plus five, and copies the size minus that position (`0x2D47` to `0x2DAF`). After a positioned chunk at 2, a message of 3 to 6 bytes makes that count negative, and the copy runs over the adapter's RAM, the player byte at `0x0698` included. So a message whose data fits one chunk goes as a lone `0xFF` chunk, as DeviceBuddy sends it.

A longer message ends with its last data in a `0xFF` chunk after the positioned ones, which both read alike. BBAPI.cs's count drops the last one to three bytes of messages of 28 to 30 bytes and every 25 bytes after, and adds a chunk for some other lengths, which a GPA reads as a negative count. The count here is exact.

The reply is report 22, read up to 20 times 20 ms apart, as BBAPI.cs's `getData` does. A matching player byte with use 0 means the controller gave no answer. The 2.0 firmware frames the channel another way, three message bytes in the header and no use byte (`0x0832` to `0x0862`), so PadForge uses it on 3.0 and later only, which is where the API Tool's memory manager runs too (memManager.cs: "3.0 is required for this feature!").

---

## Input

### Names

`SdlDeviceWrapper.GetDeviceObjects` asks `BlissBoxApi.DeviceObjectsProvider` for a raw-opened port's list, so every place that fills `DeviceObjects` stays in step. `BlissBoxRuntime.NameObjects` renames the joystick's objects for the controller report 17 names, names buttons 20 to 23 as the four arrows, appending any the joystick lacks, and appends the twelve pressure axes for a DualShock 2. The names are invariant English strings that `MappingDisplayResolver.LocalizeObjectName` translates, and `UseRawNumberedNaming` lets a port that names its objects show them.

The tables in `BlissBoxControllers` come from RetroArch's Bliss-Box 4-Play autoconfig files, stamped firmware 3.24, for 3.x, and from DeviceBuddy's controller layouts for 4.x. A layout's bit N is button N, its stream bytes 3 to 10 are axes 0 to 7 (X, Y, Z, Rx, Ry, Rz, slider, dial), and byte 11 is the hat. The sources agree on the PlayStation, Nintendo 64, Saturn, TurboGrafx-16, 3DO and Wii Classic, and differ on the NES's A and B, the SNES's X and Y, the Genesis's C and Z, the Dreamcast's and GameCube's shoulders and the Jaguar's A and C, which is why each generation keeps its own. A 2.x adapter gets no names.

Type codes come from the API Tool's `controllerType[]`, the command-line tool's `getType` and DeviceBuddy's `BlissBox_lookUpName`, with the compatibility list naming the abbreviated ones. Types 0 and 255 are both "None / Atari" in the API Tool, 255 being what an unflashed type byte reads.

### Pressure and arrows

`BlissBoxRuntime.Merge` runs in Step 2 right after SDL's read, ahead of the idle detector and every later consumer. It writes each pressure byte times 257 into the axis at `max(8, declared axes) + i`, where the declared axes are the joystick's own count, and sets buttons 20 to 23 from the native poll. The state is a fresh pooled one each read, so a port that stops publishing leaves them at rest.

The pressure order is the DualShock 2's own, which psx-spx gives and every firmware copies into report 21 unchanged: Right, Left, Up, Down, Triangle, Circle, Cross, Square, L1, R1, L2, R2. The 2.0 firmware stores the pad's reply in order (`0x21F7` to `0x2204`) and copies the pressures across (`0x2313` to `0x231C`), and 3.0 does the same (`0x2646` to `0x2651`). The API Tool's branch for 2.x reads the face buttons from other bytes, which the firmware does not bear out.

The pressure axes rest at 0 and travel one way, so the #443 rule treats them as a trigger: an axis activator on one engages past its threshold in that one direction instead of reading -1 at rest (`BlissBoxRuntime.IsPressureAxis`, used by `InputManager.AxisRestsAtZero`).

The native poll sends a PlayStation pad `0x01, 0x42, 0, 0, 0` and searches the answer for `0x41, 0x5A`. The next byte is active low, with Up in bit 4, Right in bit 5, Down in bit 6 and Left in bit 7, the psx-spx order Linux's `psxpad-spi` reads. The 3.0 firmware's D-pad table drops opposite directions, which is what the poll exists to get around. GPA 4.86 sets the four arrow buttons itself (firmware `0x34A1` to `0x34B9`).

---

## Rumble

`BlissBoxApi.OwnsRumble` is true for a port while the switch is on. Then:

- `SdlDeviceWrapper.HasRumble` is true whatever SDL found, since the adapter's commands drive the motors and the controller in the port can change without a reopen. With the switch off it is SDL's answer again.
- `SdlDeviceWrapper.SetRumble` refuses the port, because SDL's DirectInput path averages both motors into one sine effect.
- Every other site that routes the Padix converter's motors routes a port's too: Step 2's sole-writer write and its unassign stop, `StopAllForceFeedback`, the relayed rumble in `InputService`, and the Identify pulse train.

`BlissBoxSession.Strength` maps PadForge's 0 to 65535 onto the strength byte as `(level + 255) >> 8`, clamped to 1 to 255, with 0 for off. Type 1 reads a strength of 0 as full, so a small level rounds up rather than down to it. The large motor (command 4) takes the low-frequency level and the small motor (command 5) the high-frequency one.

The session keeps the wanted levels, and the worker is woken only when they change. A write the adapter refuses is tried again 100 ms later, not on every step. When the channel drops and reopens, both motors are told their level again, a stop included, since the adapter may have kept the last one. The quiesce that runs on a crash or an abnormal exit waits up to 250 ms for every port to send its stop.

The switch hands the motors over at once rather than on Step 1's next pass: switched on, an effect SDL started on a port stops, and switched off, every open port stops its motors before SDL takes the game's next level. The hand-off in Step 1 takes a row's output gate only when it is free, as Step 2 does, and tries again next pass otherwise. Identify on a port in no slot writes its pulses without recording them in the row's motor snapshot, because a recorded pulse made Step 2 send the row's final zero on the next poll.

---

## The Dreamcast screen

### The picture

PadForge keeps a picture in image order: 48 by 32 pixels, rows top to bottom, 6 bytes a row, the leftmost pixel in a byte's high bit, 1 for dark. The adapter takes it rotated 180 degrees, since the VMU sits upside down in the pad: byte `k` of the image, bit-reversed, is byte `191 - k` on the wire (dLCD.cs `writeToLCD`, and DeviceBuddy draws report 24's pixel `(x, y)` at `(47 - x, 31 - y)`). The transform is its own inverse.

A VMU Animator `.lcd` file has a 16-byte header and 4 bytes of frame information, then one byte per pixel with `0x08` for dark. A `.vms` file keeps the offset of its 32 by 32 icon as a 32-bit little-endian value at byte 16, which is centered with 8 blank pixels either side. Other images are drawn on a white field, scaled down to fit, and cut at half luminance. Text is drawn with Segoe UI Bold, aliased, as large as fits.

### The EEPROM guard

GPA 4.86 runs avr-libc's `eeprom_update_byte` over EEPROM `0x00A0` to `0x015F` for report 20, and the 3.0 firmware writes the same range for command `0x24`, so every picture lands in EEPROM, rated at 100,000 writes. The session writes a picture only when it differs from the one it last read or wrote, and never sooner than 1000 ms after the last write. A clock or play timer changes its digits once a minute.

### The modes

`DreamcastScreenService.Tick` runs on the UI thread from the dashboard timer, whether or not PadForge has focus, at most four times a second. For each port with a Dreamcast pad (types 15 and 16) it waits until the adapter's stored picture has been read, then composes the picture for the port's mode, a macro show taking the screen while it plays. Before the first picture that differs from the adapter's own, it keeps that picture, in wire order, in the port's settings. Adapter mode writes it back and forgets it once the adapter holds it again.

A Show Dreamcast Screen action queues a show from the poll thread, up to 16 waiting, and the next tick starts it on every Dreamcast pad in a port whose device is assigned to the macro's slot. A show with no port open is dropped. Each frame lasts its frame time, at least 1000 ms, from the moment the adapter holds it (`DreamcastShow`), so the EEPROM guard's second between writes never drops a frame. A frame that has not arrived after 5 s counts from when it became current, so a port that refuses writes cannot hold a show forever. The tick wakes a port's worker when the picture it wants changes.

### Saved state

`AppSettings.BlissBoxEnabled`, `AppSettings.BlissBoxPorts` (one `Port` per device: `Device`, `ScreenMode`, `Picture`, `NativeArrows`, `AdapterPicture`, dropped when every value is its default) and `AppSettings.DefaultProfileDreamcastPicture`. Reset to Defaults keeps each port's `AdapterPicture` (`BlissBoxPortData.KeepAdapterPictures`), the only copy of a picture PadForge replaced. A player change writes that picture back before it sends the command and drops the port's entry, since the port returns as a new device. Exporting the Default profile carries its picture, which lives in the settings file rather than on its snapshot. A named profile keeps its picture in `ProfileData.DreamcastPicture`, which no state save copies over. The macro action saves `DreamcastFrames` (base64 pictures joined by commas, eight at most), `DreamcastFrameMs` and `DreamcastRepeat`. `DreamcastScreenMode` is saved by name.

---

## The Controller Pak

Every transfer rides the native channel as the Joybus command the pak takes. The frames and checksums are the API Tool's (memManager.cs `memManagerLoadData`, `getN64Data`, `writeToPort`, `getCrc5`, `getCrc8`), and the checksums give the same values as libdragon's `joybus_accessory_calculate_addr_checksum` and `joybus_accessory_calculate_data_crc`.

| Command | Message | Answer |
| --- | --- | --- |
| Status | `0x00` | two identity bytes and a status byte, whose low two bits are 1 (present) or 3 (present and changed) when a pak is in |
| Read | `0x02`, address field | 32 data bytes, then their CRC-8 |
| Write | `0x03`, address field, 32 bytes | the CRC-8 the pak computed over what it stored |

The address field is the block's byte address, `block × 32`, with a CRC-5 of the 11-bit block number in its low five bits (generator `0x15`). The data CRC is a CRC-8 with generator `0x85`. A CRC that comes back inverted means no pak answered. Block 0 reading `0x80` with CRC `0xB8` is a Rumble Pak, the API Tool's "Looks like a rumble pack!" test.

A backup checks the firmware, the controller, the status and block 0, then reads 1024 blocks, each up to three times. A block that never answers fails as no reply, and one whose CRC keeps failing as a bad block. A restore writes each block until the pak confirms it, and gives up once more than 16 writes have failed, the API Tool's limit, reporting no reply when the write that reached the limit drew no answer. Both stop before their next message to the controller when the port closes. A job queued once the port is closing ends at once, and one still queued when the channel drops ends as closed. `BlissBoxSession.Busy` holds the Devices page's player and pak buttons while a job is queued or running.

A player change is sent without checking its result, as BBAPI.cs does: both firmwares reset from inside the command's handler, before the transfer completes (3.0 detaches USB at `0x08EB`, GPA 4.86 jumps to its reset at `0x2CE2`), so Windows can report the write as failed although it took.

---

## Tests

`BlissBoxProtocolTests` builds every report byte for byte, runs every parser against the references' layouts, checks the picture codec against the API Tool's "BLISS BOX" example, the checksums against libdragon's values, and the native chunking under both firmware rules. `BlissBoxSessionTests` drives a session against a scripted adapter with an N64 controller and a pak behind its native channel: the poll cadence, the motor writer's timing, the EEPROM guard, the native arrow poll, and the Controller Pak backup and restore with their failure paths. `BlissBoxAppTests` covers the names per controller and their translations, the object list and the state merge, the rumble routing, the raw open, the settings, the screen service's pictures and the macro action.

No test runs against an adapter. PadForge's reading of every report is unverified on hardware.

---

*Last updated for PadForge 4.5.3.*
