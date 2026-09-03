# Head Tracking: Internals

*The OpenTrack UDP datagram, the FreeTrack 2.0 heap, the scaling into six axes, and the row that carries them.*

The user-facing page is [Head Tracking (OpenTrack)](../features/head-tracking.md). This one is for whoever has to change the code.

| File | Role |
|---|---|
| `PadForge.Engine/Common/HeadPose.cs` | Pure decoders and scaling, no Windows calls |
| `PadForge.App/Common/Input/HeadTrackerDevice.cs` | The row: UDP receive thread, FreeTrack polling, silence, status. `FreeTrackReader` lives in the same file. |
| `PadForge.App/Common/Input/HeadTrackingRuntime.cs` | Static mirror of the Dashboard controls the poll thread reads |
| `PadForge.App/ViewModels/DashboardViewModel.cs` | The five properties, their reset commands, and `HeadTrackingStatus` |
| `PadForge.App/Services/InputService.cs` | `BuildHeadTrackerStatus`, `UpdateHeadTrackingStatus`, the Devices row status |
| `PadForge.App/Services/SettingsService.cs` | `AppSettingsData.HeadTracking*`, `ProfileData.EnableHeadTracking` |
| `PadForge.App/Services/WebControllerServer.cs` | `EnsureInboundFirewallRule`, shared with the web controller |
| `PadForge.App/Common/Input/InputManager.Step1.UpdateDevices.cs` | Phase 1i: `UpdateHeadTrackerDevice`, `RetireHeadTrackerRow`, `ShutdownHeadTrackerInputs` |

---

## Identity

| Member | Value |
|---|---|
| `Name` | `Head Tracker (OpenTrack)` |
| `DevicePath` | `headtrack://opentrack` |
| `InstanceGuid` | MD5 of `pfheadtrack:opentrack` |
| `ProductGuid` | MD5 of `pfheadtrack-product` |
| VID:PID | `4854:4F54` ("HT", "OT") |
| `InputDeviceType` | `HeadTracker` = 34 |
| Axes | Six `AbsoluteAxis` objects at `InputIndex` 0 to 5, named Head Yaw, Head Pitch, Head Roll, Head X, Head Y, Head Z, GUIDs X, Y, Z, Rx, Ry, Rz |
| Buttons, hats, rumble, gyro, touchpad | None |

The path is a URI scheme, so `DeviceRowViewModel.IsInternalVirtual` is true and the Devices page draws neither the Input Hiding nor the Input Mode section. `CreateDefaultPadSetting` auto-maps only gamepad capability types, so the row starts unmapped by design.

---

## Lifecycle: Phase 1i

`UpdateHeadTrackerDevice` runs on the poll thread after the handheld phase. Off with nothing to retire, it returns after two volatile reads. Otherwise it retires the row when the toggle went off, the user removed it from the Devices page, or `ConfigVersion` no longer equals `HeadTrackingRuntime.Version`, and opens a fresh one from `FromCurrentSettings` while enabled.

`FromCurrentSettings` reads `Version` first and the settings after it. The setters bump `Version` last, so the other order could capture the new version with the old port and the reconfigured check would never fire again for that change.

`HeadTrackingRuntime` is the static mirror:

| Member | Default | Clamp | Reopens the row |
|---|---|---|---|
| `Enabled` | false | | Retire or open |
| `UdpPort` | 4242 | 1 to 65535 | Yes |
| `FreeTrackEnabled` | true | | Yes |
| `RotationRangeDeg` | 90 | 1 to 180 | No, read live every poll |
| `TranslationRangeCm` | 30 | 1 to 500 | No, read live every poll |

`Open` never blocks. It binds the socket, starts the receive thread, queues the firewall rule on the thread pool, and opens the FreeTrack mapping. The row opens even when both sources fail, so the status line can say why nothing arrives. `Dispose` runs on the poll thread when the sweep retires the row: close the socket first (that is what unblocks `ReceiveFrom`), a 50 ms courtesy join, then the FreeTrack reader.

---

## Source one: OpenTrack UDP

OpenTrack's "UDP over network" output (`proto-udp/ftnoir_protocol_ftn.cpp`) sends `sizeof(double[6])` per pose.

| Fact | Value |
|---|---|
| Datagram | 48 bytes, six little-endian doubles |
| Order | `TX, TY, TZ, Yaw, Pitch, Roll` (opentrack `enum Axis`) |
| Units | Translation in centimeters, rotation in degrees |
| Signs | Positive yaw moves OpenTrack's mouse output right, positive pitch moves it up (`proto-mouse` invert table) |
| Short datagram | Dropped |
| Long datagram | First 48 bytes read, the rest ignored, as OpenTrack's own UDP tracker does |
| NaN or infinity in any field | The whole datagram is dropped (`tracker-udp` rule) |

The socket is IPv4 UDP bound to `IPAddress.Any` on the port, with `ExclusiveAddressUse` so a second listener on the same port (OpenTrack's own UDP tracker) surfaces as a bind failure instead of stealing half the datagrams, and `SIO_UDP_CONNRESET` cleared so an ICMP port-unreachable does not throw out of the next receive (the DSU server's rule). The receive thread is `PadForge.HeadTrackerUdp`, a 256-byte buffer, and after ten consecutive socket errors it sleeps 50 ms between retries. A bind failure sets `UdpBindFailed`.

The peer is recorded as `address:port` of the last sender, and a change of peer bumps `StatusVersion`.

---

## Source two: FreeTrack 2.0 shared memory

`FreeTrackReader` is the client side of `freetrackclient.c`.

| Fact | Value |
|---|---|
| Mapping name | `FT_SharedMem` |
| Size | 108 bytes: `FTData` (92) + `GameID` + an 8-byte table + `GameID2` (`freetrackclient/fttypes.h`) |
| Mutex | `FT_Mutext`, waited 16 ms per read |
| Open | `MemoryMappedFile.CreateOrOpen`, so launch order does not matter |

`TryDecodeFreeTrackHeap` inverts OpenTrack's writer (`proto-ft/ftnoir_protocol_ft.cpp`):

| Offset | Field | Into the pose |
|---|---|---|
| 0 | `DataID`, u32 | Increments once per written pose |
| 12 | Yaw, float radians | `-yaw × 180/π` |
| 16 | Pitch, float radians | `-pitch × 180/π` |
| 20 | Roll, float radians | `roll × 180/π` |
| 24, 28, 32 | X, Y, Z, float millimeters | `/ 10` |

Non-finite floats reject the read. The heap is polled from `GetCurrentState`, on the poll thread, and only a `DataID` change is a pose. The first read is a baseline: the heap keeps the last pose of a previous run, and a stale mapping must not move the axes. When the mutex cannot be created the reader reads unlocked, which the reference client does not do (its `FTGetData` copies nothing then). A torn pose was judged a better answer than none for a source whose only job is to report one. A mapping that fails to open sets `FreeTrackFailed`.

The two sources carry the same pose from the same tracker, so interleaving them is harmless.

---

## Scaling into axes

`HeadPose.ToAxis(value, range)`:

```
f = clamp(value / range, -1, 1)
f >= 0: round(32768 + f × 32767)
f <  0: round(32768 + f × 32768)
```

So −range reads 0, rest reads 32768 (`AxisCenter`, the `CustomInputState` center, not the arithmetic midpoint), +range reads 65535, beyond either end clamps, and a non-positive range or a NaN reads rest.

`FillAxes` applies the signs:

| Axis | Source | Sign |
|---|---|---|
| 0 Yaw | `pose[Yaw]` | as sent, right reads high |
| 1 Pitch | `-pose[Pitch]` | stick orientation, up at the low end |
| 2 Roll | `pose[Roll]` | as sent |
| 3 X | `pose[TX]` | as sent, right reads high |
| 4 Y | `-pose[TY]` | stick orientation, up at the low end |
| 5 Z | `pose[TZ]` | as sent |

The two ranges are read from `HeadTrackingRuntime` on every poll, so a range edit applies without reopening the row.

---

## Silence

`SilenceMs` = 1000. `GetCurrentState` compares the last pose's tick against now. Older than that, or no pose ever, and the axes read center and `Source` drops to `None` with a `StatusVersion` bump. The row stays attached, so mappings can be made before the tracker starts. A tracker that stops (OpenTrack closed, the camera lost the face) therefore recenters the stick within a second.

---

## The status line

`InputService.BuildHeadTrackerStatus` turns the device into text, verbatim from `Strings.resx`:

| Condition | Text |
|---|---|
| `Source` is `Udp` | `Receiving over UDP from {peer}.` |
| `Source` is `FreeTrack` | `Receiving from FreeTrack shared memory.` |
| Neither, `UdpBindFailed` | `UDP port {port} is in use by another program.` plus ` The FreeTrack shared memory could not be opened either.` when `FreeTrackFailed` |
| Neither, `FreeTrackFailed` | `Waiting for a tracker on UDP port {port}. The FreeTrack shared memory could not be opened.` |
| Neither | `Waiting for a tracker on UDP port {port}.` |

The same text lands in two places, each rebuilt only when `StatusVersion` moves. The Devices row's line comes from `UpdateDevicesRawState`, the preview loop, keyed on the device instance plus its version (a reopen restarts the version at 0, so a version-only key kept a retired device's line). The Dashboard's `HeadTrackingStatus` comes from `UpdateHeadTrackingStatus` on the dashboard tick and reads `Stopped` (`Common_Stopped`) while the feature is off, the engine is down, or the row has not opened.

---

## The firewall rule

`WebControllerServer.EnsureInboundFirewallRule("PadForge Head Tracking", "UDP", port)` runs `netsh advfirewall firewall delete rule name=...` then `add rule ... dir=in action=allow protocol=UDP localport=<port>`. Delete-then-add needs no parsing of netsh's localized output, is idempotent, and clears the pile-up a port change used to leave behind. It is queued on the thread pool from `Open`, since netsh can block for seconds, and it is best effort.

---

## Settings and the profile leg

Global, in `AppSettingsData`: `HeadTrackingEnabled` (false), `HeadTrackingUdpPort` (4242), `HeadTrackingFreeTrack` (true), `HeadTrackingRotationRange` (90), `HeadTrackingTranslationRange` (30). A stored zero for the port or a range reads as the default on load.

`ProfileData.EnableHeadTracking` is `bool?`, the same nullable authored contract as the Chroma, LIGHTSYNC, and Sensa mirrors. A profile with an opinion sets `Dashboard.HeadTrackingEnabled` on apply. A profile saved before the field exists reads as no opinion and leaves the global value standing. A user change of the toggle while a profile is active records into that profile, and the save path refreshes an existing opinion from the Dashboard. Only the enable rides profiles. The port, the FreeTrack toggle, and the two ranges stay global.

---

## Diagnostics lines

| Line | When |
|---|---|
| `Head tracker: listening on UDP port <port>` | Bind succeeded |
| `Head tracker: UDP port <port> bind failed: <message>` | Bind failed |
| `Head tracker: FreeTrack shared memory open` | Mapping opened |
| `Head tracker: FreeTrack mapping failed <message>` | Mapping failed |
| `Head tracker: pose #<n> via <Udp|FreeTrack> yaw= pitch= roll= x= y= z=` | Poses 1, 2, 4, ... 64, then every 4096th |

---

## Tests

`HeadTrackerTests` pins the UDP layout and order, the NaN and infinity drop, the short and long datagram rules, the FreeTrack offsets and sign inversions, `ToAxis` at rest, the ends, the clamp, and a bad range, the stick-orientation vertical axes, a UDP pose landing on the axes with its peer named, the one-second silence recenter, the FreeTrack baseline-then-DataID rule, an online row at rest before any pose, six named axes at indices 0 to 5, and the type ordinal pinned past `SystemMotion`.

---

## Evidence status

Confirmed by reading and by the replay tests: the datagram layout, the heap offsets, the sign inversions of OpenTrack's FreeTrack writer, and the scaling. Not yet run against a live OpenTrack. Roll and the three translations pass through with the sign the tracker sends, and whether that matches a user's expectation on real hardware is unconfirmed. Sharing of the `FT_SharedMem` mapping between an elevated PadForge and a medium-integrity OpenTrack is reasoned from the reference client, not tested.

---

## Related

- [Head Tracking (OpenTrack)](../features/head-tracking.md) for the user-facing page
- [Headset Head Tracking Internals](headset-motion-internals.md) for the other head source, which is rotation only
- [Input Pipeline](input-pipeline.md) for where Phase 1i sits

---

*Last updated for PadForge 4.4.0.*
