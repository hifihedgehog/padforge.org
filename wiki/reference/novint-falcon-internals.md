# Novint Falcon Internals

*How PadForge finds Force Dimension's library, opens each Falcon, renders the feel and the game's force on a haptic thread per Falcon, and installs Force Dimension's driver.*

For the user-facing side see [Novint Falcon](../features/novint-falcon.md).

| File | Responsibility |
| --- | --- |
| `PadForge.Engine/Common/ForceDimension/ForceDimensionCatalog.cs` | Lists the `dhd64.dll` copies to try, in load order, and the SDK folders. |
| `PadForge.Engine/Common/ForceDimension/ForceDimensionLibrary.cs` | Loads the library and binds its exports. |
| `PadForge.Engine/Common/ForceDimension/IFalconLink.cs` | The calls PadForge makes, which tests answer with a scripted Falcon. |
| `PadForge.App/Common/Input/InputManager.Falcon.cs` | The sweep that opens Falcons, the rows, the hand-off from the poll thread and the stops. |
| `PadForge.App/Common/Input/Falcon/FalconDevice.cs` | One Falcon: its row, its haptic thread, the calibration sweep and the stored reach. |
| `PadForge.App/Common/Input/Falcon/FalconController.cs` | One pass of the force loop, free of I/O: the feel, the game's force, the caps and the fade. |
| `PadForge.App/Common/Input/Falcon/FalconFeels.cs` | The Joystick and Aim feels. |
| `PadForge.App/Common/Input/Falcon/FalconGameForces.cs` | Rumble as kick and shake, and a game's effects as force. |
| `PadForge.App/Common/Input/Falcon/FalconSettings.cs` | A slot's Falcon settings and the game's force, as the haptic thread reads them. |
| `PadForge.App/Common/Input/Falcon/FalconRuntime.cs` | The Settings switch, the picked library and the loaded one, and what the last sweep found. |
| `PadForge.App/Services/InputService.Falcon.cs` | The Settings card's library and no-Falcon lines, each Falcon row's line and reach on the Devices page, and the pad page's settings. |
| `PadForge.App/MainWindow.Falcon.cs` | The card's buttons, and Calibrate Reach from a Falcon row on the Devices page. |

The behavior and its constants come from two programs that drive the Falcon through the same library: FalconJoystick for the Joystick feel and FalconJoyForce for the Aim feel and the rumble. Each constant in the code names the line of the program it comes from. Neither program carries a license, so PadForge takes their behavior and constants as facts and its code is its own.

---

## The library

Force Dimension's license allows use and grants no right to redistribute, so PadForge loads the copy the user installed. `ForceDimensionCatalog.Candidates` lists every copy that exists, in order: the picked file, then for each SDK folder its `bin\dhd64.dll` and `lib\dhd64.dll`, then System32. `SdkRoots` reads the folders from the `FDSDK` environment variable, which Force Dimension's Python binding has users set, from the uninstall entries whose display name holds "Force Dimension" (`InstallLocation`, or Inno Setup's `Inno Setup: App Path`, in both registry views), and from each `sdk-*` folder under Program Files' `Force Dimension` or `ForceDimension` folder, newest version first.

`ForceDimensionLibrary.TryLoad` loads the first candidate that loads and binds 17 exports, all or none, with `__stdcall` delegates and the device ID as a signed byte, as `dhdc.h` declares them. A library missing one export is refused, so a call never lands on a missing entry. It is never freed, since the haptic threads hold its function pointers. Its reasons are `gate` (the test host's vendor gate), `platform` (a process that is not x64), `missing`, `load` and `exports`. `FalconRuntime.Acquire` tries again 30 seconds after a failed load.

---

## The sweep and the rows

With the switch on, `UpdateFalconDevices` starts `FalconSweep` on a worker every 3 seconds and registers what the sweep queued, on the poll thread. The sweep asks `dhdGetDeviceCount`, which counts devices other programs hold too, and opens each index with `dhdOpenID`. A device already open returns the ID it opened with, so an ID PadForge holds is skipped. A device whose system type is not 60 (`DHD_DEVICE_FALCON`) is closed and its index skipped until the count changes. A refused open with error 20 (`DHD_ERROR_DEVICE_IN_USE`) counts as held by another program.

With no Falcon open, the sweep reads the USB nodes with ID 0403:CB48 and their services, and when one has no driver, finds the SDK's driver package. `FalconRuntime.Status` carries all of it to the Settings card, which reads it on the dashboard tick. The card shows the library and, when no Falcon opened, why. It names no Falcon: each open Falcon's line, its homing prompt for 20 seconds and then its rate, is on its row's detail pane on the Devices page (`UpdateFalconDeviceRow`).

A row's identity comes from the serial number: an MD5 GUID of `pffalcon-serial-N` and the path `falcon://N`, or the enumeration index for a Falcon with none. A row is retired when the switch goes off, when its haptic thread detaches after three failed reads in a row, and when the user removes it. Engine stop disposes every Falcon synchronously, which sets zero force and closes each one, as FalconJoyForce does on exit.

The row's axes are signed values moved to 0 to 65535 by subtracting `short.MinValue`, as `SdlDeviceWrapper` moves SDL's. Up/Down is inverted, so up reads low as on a gamepad's Y axis, and the right stick's Y mapping lifts the stick when the handle rises. The row answers no (Any Device) source, the head tracker's rule, since a Falcon at rest reads centered on every axis.

---

## The haptic thread

Each Falcon runs its own thread at the highest priority, as Force Dimension's multithread example runs one per device. It is unpaced: the library's calls hold it near 1 kHz, as they hold FalconJoyForce's loop, and its time step comes from a `Stopwatch`, since a fixed 1 ms tick corrupts the filters. Each pass reads the position and the buttons, sets the standard gravity and the maximum force when either changed, runs `FalconController.Step`, sets the force and publishes the reading. The rate `dhdGetComFreq` reports is read once a second.

The poll thread hands each Falcon its first assigned slot's settings and the combined force in `HandFalconForce`, after Trigger Rumble Fold, as Step 2 hands every direct writer. `FalconDevice.Publish` compares the settings strings and the force field by field and makes a new hand-off only when one changed, so a steady pass allocates nothing. The haptic thread reads the hand-off once per pass. A Falcon in no slot gets the unassigned hand-off: gravity compensation and nothing else.

---

## The force

`FalconController.Step` computes, in newtons on Force Dimension's axes (X toward the player, Y right, Z up):

1. The feel's force on the left/right and up/down plane: the Joystick spring, end stop and damping, or the Aim wall, ridge, nudge and friction and stiction assists.
2. The rumble: the kick along +X, or the shake in the plane, scaled by **Kick Strength** or **Shake Strength** and **Overall Gain**.
3. The preload, 1.6 N along +X, in the Aim feel while its button is held.
4. A game's effect, at the force limit times **Overall Gain**.

The plane is then capped at 7.8 N or the force limit, whichever is lower, In/Out at the limit, and the whole force at the limit, FalconJoyForce's order. Last, the fade multiplies everything: it climbs from 0 to 1 over half a second after the Falcon opens, its slot takes it, or its feel changes.

### The feels

The Joystick feel follows FalconJoystick: the stick is the offset over the reach, full at 0.85 with the direction kept, and the force is 3 N times **Centering Spring** at full deflection, plus an end stop past 0.85 that builds as the 2.3rd power to 8 N less the spring, plus 4 N per meter per second of radial damping, which may cut the pull and never turns it into a push. The velocity is a six-sample window low-passed at 30 Hz.

The Aim feel follows FalconJoyForce: each axis estimates velocity in a six-sample window with a two-sample term, filtered with a cutoff from 9 to 55 Hz by speed, 35 times faster on release, and zeroed after 10 still frames. The stick blends three zones (sensitivity 22, 18 and 12, curves 0.80, 0.88 and 0.95) across 4, 25 and 150 mm/s, and at very low speed blends toward the offset from a 1.2 Hz reference, times 4. A flick carries on for a moment after a fast move. Past 0.81 of the reach the push latches for at least 150 ms in the nearest cardinal direction, from 0.64 to 6.0 by how far past, half speed vertically, until the handle comes back inside 0.76. The wall builds from 0.78 to 0.95 as the 2.3rd power to 8 N, with damping that rises toward the push border on the way out. A 1.4 N ridge sits in the 0.12 before the border, released once crossed until the handle is 0.02 back inside, where a 1.3 N nudge fires once.

### Rumble

FalconJoyForce reads rumble as packets from its Pico. PadForge has the slot's motor levels each poll, so a level above zero is rumble arriving and a rise of 0.02 is a new shot. While the Kick button is held, and for 250 ms after, the live level (3.4 per motor) drives the kick: 8 N at a level of 4 on a 0.65 curve, at least 4.5 N, sustained above 0.5, and decaying between 0.25 and 0.75 per millisecond by level, with a 12 Hz release. Strong rumble adds a lateral texture. Otherwise the motors (5.5 each) drive the shake, held between 3.2 and 9 N, its direction wandering every 140 ms at a 5 Hz slew, attack 7 Hz and release 3 Hz, and silent through a kick's whole tail. A firing kick slows the aim to 0.4 and bleeds the aim's velocity, harder downward, so the kick does not read as aim.

### A game's effects

A constant, ramp or periodic effect's direction names where the force comes from, as SDL's haptic API and USB force feedback devices define it, and as PadForge's HID decoder reads it. The force pushes the other way, `toward = from + π`, with Y = magnitude × sin(toward) and Z = magnitude × cos(toward), so an effect from the east pushes the handle left. Periodic shapes are sampled as the wheel path samples them.

A spring, damper, friction or inertia acts on Left/Right with condition axis 0 and on Up/Down with axis 1, whose DirectInput Y grows toward the player, so it reads the handle's up/down reversed. A single axis acts on both. A full damper is 20 N per meter per second, CHAI3D's maximum linear damping for the Falcon, full inertia is 0.2 kg on the acceleration low-passed at 30 Hz, and friction ramps to zero below 5 mm/s so a still handle does not chatter. Each side's saturation holds the result, as on the SDL path. A game's spring takes the Joystick spring's place while it plays.

---

## Calibration

`BeginCalibration` starts a four-second sweep on the haptic thread, which rests the forces and tracks each axis's travel. Each axis's reach is 95% of half its travel, kept only between 25 and 120 mm, FalconJoyForce's F11 sweep. The sweep starts from **Calibrate Reach** in the Falcon row's detail pane on the Devices page, since the reach belongs to the device and every slot it feeds. The window stores it on the Falcon's record as `x,y,z` in millimeters, and a row takes it when it opens. A sweep cut short by the Falcon closing reports no axis. The pane's line gives the reach in use each time the row is selected, until a sweep replaces it, and a sweep running keeps its own line.

---

## The driver

Force Dimension's `drivers\usb\fdhusb.inf` binds `USB\VID_0403&PID_CB48` to WinUSB with interface GUID `{CB5DAA55-DC1A-4f2d-8F76-14CEE032832A}`. SDK 3.17.7's installer holds two variants, and only DriverVer 3.18.00.03 names a catalog, `fdhusb.cat`, signed by Force Dimension. `DriverInstaller.FalconDriverPackage` offers a package only when its `[Version]` section names a catalog that sits beside it, since Windows refuses a third-party package with none.

`InstallFalconDriver` runs only when every Falcon node has no driver, the rule `VendorUsbDriverInstaller` keeps for every device: a node on any driver stays as it is. It stocks the package with `DiInstallDriver`, where Windows may ask the user to trust Force Dimension, forces it onto the hardware ID with `UpdateDriverForPlugAndPlayDevices`, as the DualShock 3 and vendor USB binds do, and counts as done when every node reports WINUSB.

---

## Stops and the test host

Stopping the engine, losing focus with the pause on, and Stop All Force Feedback silence the game's force and keep the feel. The crash and exit quiesce stops each haptic thread within 150 ms, which sets zero force and closes the device, and a thread still inside a call gets a zero force sent from the quiescing thread, since the library is thread-safe. Force Dimension's watchdog turns the forces off when the host goes quiet, which covers a killed process.

In the test host the library refuses to load (`VendorProgramGate`), the sweep opens no device (`DirectDeviceAccess.RefusesAll`), and the driver install refuses (`DriverInstaller.OffLimitsForTest`, with `VendorUsbDriverInstaller.NoDriverChangesForTest` under it). The tests drive `FalconDevice` with a scripted `IFalconLink`.

---

*Last updated for PadForge 5.1.0.*
