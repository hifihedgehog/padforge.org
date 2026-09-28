# Analog Keyboards Internals

*How PadForge finds an analog keyboard, picks the protocol that reads it, and keeps the keyboard the way it found it.*

For the user-facing side see [Analog Keyboards](../features/analog-keyboards.md).

The engine side lives in `PadForge.Engine/Common/AnalogKeyboard/`:

| File or folder | Responsibility |
| --- | --- |
| `AnalogKeyboardRoutes.cs` | The route descriptor and the registry, in the order collections are offered to routes. |
| `AnalogKeyboardSession.cs` | The transport interface, the pass result, the session base class, and the session for the Soup families that push reports. |
| `AnalogKeyboardDeviceInfo.cs` | The metadata a route decides on: attributes, caps, strings, declared report IDs, value caps, SetupAPI strings, sibling collections. |
| `AnalogKeyboardCatalog.cs` | The protocol enum, the Soup family identification, the Razer, DrunkDeer and Keychron catalogs. |
| `AnalogKeyboardParsers.cs`, `AnalogKeyboardPollers.cs` | The Soup and AnalogSense families: Wooting, Razer, DrunkDeer, Keychron and Lemokey, MADLIONS on VIA, Bytech. |
| `AnalogKeyCodes.cs` | The key code space, the Razer, DrunkDeer and Bytech tables, the MADLIONS layouts, names for virtual keys and scan codes. |
| `AnalogKeyboardData.cs` | Loads the JSON tables embedded from `Data/`. |
| `Routes/` | Every other route, one group of files per family. |
| `Data/` | Key tables and model catalogs, one JSON file per group. |

The app side is `PadForge.App/Common/Input/`: `AnalogKeyboardHid.cs` (enumeration and the HID channel), `AnalogKeyboardDevice.cs` (the device row and its reader thread), `AnalogKeyboardRuntime.cs` (the Settings mirror and the per-row key lists), and the analog keyboard phase of `InputManager.Step1.UpdateDevices.cs`. The key depths reach mappings through `CustomInputState.AnalogKeys` and the `Analog Key N` descriptor in `SourceCoercion`.

---

## From collection to row

1. **Sweep.** Every 3 s while **Read Analog Keyboards** is on, a worker enumerates every HID top-level collection and reads its metadata with no traffic to the device: `HIDD_ATTRIBUTES`, `HIDP_CAPS`, the declared report IDs of each type through `HidP_InitializeReportForID`, the input value caps, the product, manufacturer and serial strings, the container ID, and the devnode's SetupAPI manufacturer, friendly name and description. Collections of one physical device (same VID, PID and container ID) are linked as siblings.
2. **Candidates.** Each route's `Matches` looks at the metadata alone. The collections with at least one matching route become candidates, carrying their matching routes in registry order.
3. **Open.** The device tries each candidate route in turn: open the collection the route's way, create its session, run `Start`. The first `Start` that returns true wins. A route never writes to a collection its `Matches` did not accept.
4. **Register.** The poll thread gives the winner a device row. A route with `RegisterOnFirstReport` waits in the queue, listened to, until its first pass produces a key set.
5. **Read.** A reader thread runs `Pass` back to back. After each `Ok` pass it copies the key set to the live state under a lock and notes any key the row's list lacks, so the picker offers it. The poll thread copies the live state into `CustomInputState.AnalogKeys` each cycle.
6. **Retire.** When the collection disappears, the reader fails, the user removes the row or the switch goes off, the row is disposed on the thread pool: the reader finishes its pass, the session's `Stop` puts the keyboard back, and the handle closes. A reader that does not finish within the route's stop budget has its I/O canceled.

### Open results

| Result | Meaning | Next try |
| --- | --- | --- |
| Opened | A route's `Start` succeeded. | none |
| Busy | The collection would not open (another program holds it). | 60 s |
| RetryLater | Every `Start` failed, and a route asks for a timed retry (`StartRetryMs`) whose session did not set `NoStartRetry`. | the route's delay |
| NotSupported | Every matching route talked to the keyboard and none recognized it. | when it is plugged in again |

A row whose reader gave up while the collection is still present also waits 60 s, so a keyboard that stops answering is not reopened every sweep.

---

## The route

`AnalogKeyboardRoute` is a descriptor, not a class to inherit:

| Member | Use |
| --- | --- |
| `Id`, `Protocol` | Stable id for logs and tests, and the family. |
| `Matches(info)` | Metadata-only test. It must never touch the device. |
| `CreateSession(info)` | A fresh session for an accepted collection. |
| `Writable`, `Exclusive` | Open read-write or read-only, shared or not. |
| `OpenFallback` | For an exclusive route: on error 32 or 5, open shared, then with no access rights, which still carries feature reports. HallJoy's ATTACK SHARK ladder. |
| `WriteTimeoutMs`, `TransferTimeoutMs` | Bound one `WriteFile` (default 1000 ms) and one feature or control transfer (default 500 ms). |
| `StaleAfterMs` | Keys read 0 when no pass has produced a key set for this long. On these routes an unanswered pass keeps the last key set until then instead of releasing every key. |
| `StopTimeoutMs` | How long a stop waits for the session's teardown (default 1500 ms). The MCHOSE Mix 87 gets 25 s. |
| `StartRetryMs` | Retry a failed handshake on a timer, the reference's reconnect cadence. |
| `InputBuffers` | `HidD_SetNumInputBuffers` after opening. |
| `Companion(info)` | For a route that commands one collection and reads another: picks the collection to read among the siblings. The sweep leaves a companion alone while its row owns it. |
| `RegisterOnFirstReport` | For a route that recognizes keyboards by their reports alone. |
| `Name(info)`, `Keys(info)` | The row's name and key list before the session knows better. |

## The session

`AnalogKeyboardSession` is the conversation with one keyboard:

- `Start(io)` proves the keyboard is the route's and prepares it: identity handshakes, key map reads, any mode the keyboard must be in. It runs on the sweep worker before the row exists. **`Stop` is called only after a successful `Start`**, so a `Start` that fails after changing the keyboard must undo that itself. A `Start` that failed after a write sets `NoStartRetry`, so the route's timed retry cannot turn into a loop of writes.
- `Pass(io, output, isHeld)` runs one exchange or waits for one report. `output` persists between passes, so a route that hears only changes updates the keys it hears about. `isHeld(code)` says whether Windows sees the key down, which the routes that read a few keys per request use to read pressed keys first.
- `Stop(io)` undoes what `Start` changed, while the handle is still open.
- `ModelName`, `KeyOrder`: the exact model and key list once `Start` knows them.
- `MissLimit`: unanswered passes in a row before the row is given up.

| Pass result | Reader does |
| --- | --- |
| `Ok` | Publishes the key set and counts a report. |
| `Idle` | Nothing new and no miss, as a pushed keyboard at rest. |
| `NoAnswer` | Releases every key, or on a `StaleAfterMs` route keeps them until the window runs out, and counts a miss. |
| `Failed` | Ends the session. |

The transport (`IAnalogKeyboardTransport`, implemented by `AnalogKeyboardHidChannel` and by the tests' `AnalogKeyboardTestTransport`) works on Windows buffers: byte 0 is the report ID, 0 for an unnumbered report. `Send` is an overlapped `WriteFile` padded to the output length, and it counts only when every byte went out. `SendOutputReport`, `SetFeature` and `GetFeature` are the matching IOCTLs, and `GetFeature` returns the driver's byte count. Every wait is bounded, and a timed-out request is canceled and drained before its buffer is reused.

---

## Key codes

| Range | Meaning |
| --- | --- |
| `0x04` to `0xE7` | HID keyboard usages, named for their US legend |
| `0x3xx` | Consumer keys, Wooting's namespace 3 |
| `0x401` to `0x409` | Vendor keys: `0x403` to `0x405` and `0x408` the references' KEY_OEM_1 to 4, `0x409` Fn |
| `0x470` to `0x472` | The SayoDevice O3C's three keys |
| `0x480` to `0x483` | Wooting split-key aliases: left Space, right Space, center Fn, right Fn |
| `0x600` to `0x6FF` | A key known only by its position: KeyAxis rows and columns, Azoth and Logitech key bytes, libhmk keys without a usage, MADLIONS boards without a key table |

`AnalogKeyInputState` holds up to 64 keys below `CodeCount` (`0x700`). Depth runs from just above 0 to 1.

---

## The routes, in order

A keyboard can match several routes on metadata, so order matters: the first route is HallJoy's first native route, and the last is the listener that takes only what nothing else claims. The order follows HallJoy's `native_analog_backends.def`, then the families HallJoy does not cover, then the Soup and AnalogSense families.

| Route | Keyboards | Identified by | Read by | Reference |
| --- | --- | --- | --- | --- |
| `attackshark-pro` | ATTACK SHARK RY5088 boards, 37 board IDs | VID 3151, FFFF:0002, 65-byte feature, then two matching `8F` board IDs | Feature-report pages `E5 FE 01 page`, 1 ms apart, 150 ms freshness | HallJoy |
| `halljoy-aula-mini60` | AULA MINI 60 HE, HE Pro, HE MAX | 0C45:8032/80A2/80A1 on FF68:0061, device info with manufacturer 0x0166 | Simulation mode `0x66` on, sample stream, `0x67` off at stop | HallJoy |
| `halljoy-mad68-a0` | MADLIONS MAD 68 Pro R | 373B:1109, or a "mad68" product with an `A9` acknowledgement | The A0 stream armed with `A8`/`A9` | HallJoy |
| `halljoy-hex80-0x96` | ATK x QK Hex80 | 373B:1176/1177/1250 on FF60:0061 | `02 96 1C` chunk reads | HallJoy |
| `halljoy-aula-hero` | AULA HERO84 HE, HERO 68 HE, Air, MINI, WIN 68 HE Ultra, HERO 99 HE | 372E:103E, report 9 both ways, UUID from `82 01` | `94 02` selected-key polling | HallJoy |
| `halljoy-addressed-ipi` | IPI QBZ75, Aurora 75, QBZ65, AURORA65, AURORA65W, RAIN65, Aurora75 PRO, flash68 | 372E:105C/106C, UUID | The 09 frame, map and calibration reads, `94 02` polling | HallJoy |
| `halljoy-addressed-generic` | Other keyboards that answer the Addressed probe | FF60:0061 with report ID 9 both ways and 64-byte reports, never Keychron, Lemokey or MADLIONS | Same, after a `94 02` probe | HallJoy, narrowed |
| `halljoy-aula-sparkplayjoy-6x21` | AULA WIN 60 HE MAX and PRO, WIN 68 HE PRO/MAX, HERO 68 HE PRO, GravaStar Mercury V75, Pro and Lite | FFA0:1, a known VID and PID, VID 1CA2 or a family token, then the sync board ID | The 5C frame travel matrix | HallJoy |
| `halljoy-irok-na87-m484` | IROK NA87 Mag, AJAZZ AK820 MAX RGB | 0416:7372 on FF1B:0091, `0D` identity GK8260HERGB or SG8994HERGB V1.13.17 | M484 events or raw rows | HallJoy |
| `keyaxis-0416-7372` | Redragon M68, E-YOOSO HZ-68, Redragon K712 RGB-M | 0416:7372 on FF1B after the NA87 route refuses it | `21 .. 18 02` arm, row/column/depth frames, `18 03` disarm | KeyAxis |
| `halljoy-aula-w669` | AULA WIN 60 HE, WIN 68 HE, KP-TE153, Redragon K673 and K617 HE | FF1B:0091, not 0416:7372, `0D` product or the HID product string | `21 02` subscription, travel events, `21 03` at stop | HallJoy |
| `halljoy-irok-mg75-pro` | IROK MG75 Pro and the JingTai V1 models, 29 identities | FFA0:1, exact VID, PID and product string | The 5C frame | HallJoy |
| `halljoy-chilkey-slice75` | Chilkey Slice75 HE | 1CA3:0701 "SLICE75 HE" | The 5C frame | HallJoy |
| `rongyuan-snapshot` | MonsGeek M1 V5 HE, EPOMAKER G84 HE | 3151:5030 control collection, `8F` board | Feature-report travel pages | HallJoy |
| `rongyuan-stream` | 253 RY5088 rows of many brands | Control collection plus one paired input collection, `8F` board | `1B 01` stream on, report 5 events, `1B 00` at stop | HallJoy |
| `halljoy-neo65` | Neo65 SONIC HE+ ANSI and ISO | E560:EE65/EF65 on FF60:61 | `D0 A6` depth pages | HallJoy |
| `halljoy-steelseries-apex` | SteelSeries Apex Pro, Pro TKL, Pro Gen 3 | 1038:1610/1614/1640 on FFC0:1, firmware 4.16.8 | HallJoy's allowlisted requests | HallJoy |
| `halljoy-mchose-mix87` | MCHOSE Mix87 III | 3837:300D, firmware 1.22 and seven region hashes | Flash debug flag on at start and off at stop, A0 events | HallJoy |
| `halljoy-sparklink` | IROK, CAROTMAS and EWEADN SparkLink boards, 29 PIDs | VID 1CA6, known PIDs, FFB0:1, never 1038 | Device info `01 02`, row travel reads | HallJoy |
| `halljoy-sayo-depth` | SayoDevice O3C and depth-capable Sayo keypads | VID 8089 on FF12:2, 1024-byte output | Depth polls | HallJoy |
| `finalmouse-centerpiece-pro` | Finalmouse Centerpiece Pro | 361D:0200, FF00:0001, input report 4 | `03 02 F0 1D` every 2.5 s, key events | LeiterConsulting's Soup fork |
| `libhmk` | libhmk firmware: HE16, HE60, HE60 v2, M256 WHE | AB50 with AB16/AB60/AB65, FFAB:00AB | Analog info command, keymap from the keyboard | libhmk and hmkconf |
| `halljoy-rog-azoth-96-he` | ASUS ROG Azoth 96 HE | 0B05:1C10 control plus the FFC0:0001 event collection | `51 61` travel notifications | HallJoy's firmware reconnaissance |
| `logitech-pro-x-tkl-rapid` | Logitech PRO X TKL RAPID | 046D:C35B, FF00:0002, report 0x11 | Passive HID++ reports, furthest key only | Sainan's capture notes |
| `nuphy-he` | NuPhy HE boards in NuPhyIO's catalog, 11 PIDs | 19F5, usage 1/0, 64-byte unnumbered reports | debugMode bit per mode with `55` GetFunc/SetFunc, A0 stream, bit restored at stop | NuPhyIO, Soup |
| `madlions-a0` | MADLIONS Nano 68, MAD 68 R and Pro, Fire 68, 31 PIDs | 373B on usage 1/0, AnalogKeys' product list | The same debugMode bit, A0 events | AnalogKeys |
| `soup-wooting-v2`, `soup-wooting-v1` | Every Wooting keyboard | Usage page FF53 or FF54 | Pushed reports | Soup, Wooting Analog SDK |
| `soup-razer-huntsman-v2`, `-v3`, `soup-razer-tartarus-pro` | Razer analog Huntsmans and the Tartarus Pro | Razer PIDs with input report 7, 11 or 6 | Pushed reports while Synapse runs | Soup, Razer's Synapse Web |
| `soup-drunkdeer` | DrunkDeer keyboards | VID 352D with report 4, model from `04 A0 02` | `04 B6 03 01` and three `B7` chunks | Soup, HallJoy |
| `soup-keychron` | 41 Keychron and 2 Lemokey HE boards | FF60:0061 and the catalog | `A9 01`, then `A9 31` on AnalogSense firmware or `A9 30 row col` | Soup, HallJoy |
| `soup-madlions` | MADLIONS MAD60HE, MAD68HE, MAD68R | FF60:0061 and the layout PIDs | `02 96 1C` groups of four | Soup, HallJoy |
| `soup-bytech` | Redragon K709 HE | 372E:105B on FF00 | Report 9 `97 00` with checksum | AnalogSense.js |
| `a0-listen` | Keyboards that push the 0xA0 event unasked (MCHOSE Jet 75) | Usage 1/0, 64-byte unnumbered input, no other route applies | Passive, row on the first event | HallEffectAnalogMapper |

---

## Notes by family

**Razer.** Report 11 carries up to 15 entries of Razer's firmware key ID (IBM key-position numbering) and a big-endian travel. Razer's Synapse Web divides by the model's `eventDataSize`: 65535, or 45864 on the Low-profile Tenkeyless 8KHz (0x02E6). The key table is Synapse Web's `fwID` table. Soup's table swapped Scroll Lock and Pause and read the ANSI backslash position as 0x2A, and Razer's own table and Abbytech's reader agree on 0x7D Scroll Lock, 0x7E Pause, 0x1D backslash and 0x2A the ISO hash key. The 8KHz models share the V3 Pro's interface-1 descriptor byte for byte in OpenRazer's dumps. Every Razer route reads only while Synapse runs.

**DrunkDeer.** Start asks the five known PIDs for their model with `04 A0 02`. A 64-byte answer `04 A0 02 00` names the model by bytes 5 to 7, and a model is taken only from its own PID. Each model reads through its own map from DrunkDeer's Antler layouts. An answer chunk must be 64 bytes, start `04 B7`, carry a chunk number below 3 that the frame has not seen, and the grid assembles in chunk order. A bad frame is a miss, not the end of the session.

**Keychron and Lemokey.** The catalog is HallJoy's 39 identities with Keychron's own matrices, the K6 HE ISO and JIS from paysdelest's Soup fork, and Soup's Lemokey tables. `A9 01` must answer with at least three bytes. On AnalogSense firmware `A9 31` answers `slots / 30 + 1` times, 30 travel bytes each, and on stock firmware `A9 30 row col` answers one key with the travel at byte 6 (analog matrix version 4 and later) or byte 3. Travel under 5 is rest and 235 the bottom.

**Wooting.** The 60HE v2 and 80HE+ report their split Space halves and two Fn keys at matrix positions of their own. The route publishes them under `0x480` to `0x483` as well as Space and Fn, matched under the gamepad-mode mask because the mode changes the product ID's low nibble and not the matrix.

**State that must be undone.** The routes that change a keyboard's state and undo it in `Stop`: AULA MINI 60 (`0x67` after `0x66`), MADLIONS MAD 68 Pro R (a closing `A9`), W669 (`21 03`), IROK NA87 (unsubscribe), RongYuan stream (`1B 00`), KeyAxis (`18 03`), NuPhy HE (each changed mode's debugMode bit restored), MADLIONS A0 (the bit cleared), MCHOSE Mix 87 (the flash flag cleared, with a 25 s stop budget). The ROG Azoth 96 HE's `51 61` has no known disable, so its session sends nothing at stop, as HallJoy's research does. Each also undoes a failed `Start` that had already written, including a write that timed out and may still have landed.

---

## Data files

Every table is generated from its reference and checked against a second extraction. None is hand-typed.

| File | Holds | From |
| --- | --- | --- |
| `rongyuan.json` | ATTACK SHARK profiles, snapshot and stream catalogs, 330 tables | HallJoy `attackshark_pro_native_model.h`, `rongyuan_snapshot_protocol.h`, `rongyuan_stream_protocol.h` |
| `aulaevents.json` | MINI 60 and W669 models and tables | HallJoy `aula_mini60_*`, `aula_w669_*` |
| `addressed.json` | IPI and HERO models and tables | HallJoy `ipi_*`, `aula_hero84he_*` |
| `jingtai.json` | JingTai V1 identities, Slice75, AULA RM boards | HallJoy `mg75_pro_protocol.h`, `jingtai_v1_profiles.h`, `slice75_protocol.h`, `aula_win60he_protocol.h` |
| `madlions.json` | MAD 68 Pro R, Hex80, NA87 and AJAZZ tables | HallJoy `mad68pr_*`, `hex80_*`, `irok_na87_*` |
| `neoapexmix.json` | Neo65 tables, Apex sensor map, Mix87 fingerprints | HallJoy `neo65_protocol.h`, `steelseries_apex_protocol.h`, `mchose_mix87_protocol.h` |
| `sparksayo.json` | SparkLink models, O3C keys | HallJoy `sparklink_model_profiles.h`, `sayo_o3c_protocol.h` |
| `nuphy.json` | NuPhy HE models, MADLIONS A0 models, the Nano 68 Pro table | NuPhyIO's device catalog, AnalogKeys |
| `others.json` | Centerpiece Pro and libhmk tables | LeiterConsulting's Soup fork, libhmk, TinyUSB |
| `keychron.json` | 43 Keychron and Lemokey boards | HallJoy `keychron_layout_identities.h` and its reviewed catalog matrices |
| `drunkdeer.json` | Generic and seven per-model DrunkDeer maps | HallJoy `halljoy_drunkdeer_maps.h`, the UAP overlay's generic table |

The HallJoy tables come from HallJoy's commit 378f9fe. The JSON is embedded as `PadForge.Engine.Common.AnalogKeyboard.Data.<file>`, and an edited table needs `dotnet clean` before publishing, or the single-file build can carry the old copy.

---

## Tests

Each group has its own file in `PadForge.Tests`: `AnalogKeyboardRongYuanTests`, `AnalogKeyboardAulaEventsTests`, `AnalogKeyboardAddressedTests`, `AnalogKeyboardJingTaiTests`, `AnalogKeyboardMadlionsTests`, `AnalogKeyboardNeoApexMixTests`, `AnalogKeyboardSparkSayoTests`, `AnalogKeyboardOtherTests`, `AnalogKeyboardNuPhyTests`, `AnalogKeyboardSoupFamilyTests` and `AnalogKeyboardProtocolTests`. They drive each session through `AnalogKeyboardTestTransport`, a scripted keyboard that logs every write and answers from byte fixtures: request frames byte for byte, handshakes and their refusals, parsing and normalization with the references' own test vectors, and the writes each `Stop` sends. `AnalogKeySourceTests` covers the device row, the picker and the key names. `AnalogKeyboardSoupFamilyTests` also pins the registry order.

No test runs against a keyboard. Hardware status for each family is whatever its reference records, and PadForge's own reading of every family is unverified on hardware.

---

*Last updated for PadForge 4.5.3.*
