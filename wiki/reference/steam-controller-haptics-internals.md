# Steam Controller Haptics Internals

*How PadForge drives the Steam Controller 2026's four actuators: the native PCM stream over reports 0x86 and 0x88 on the wired pad and the dongle, and the 0x83 tone lane it falls back to over Bluetooth.*

This is the developer-side companion to the haptic-tone section of [Controller Audio](../features/controller-audio.md) and to the HD-haptic tones section of [Controller Audio Internals](controller-audio-internals.md). Issues #371 and #381 (PCM stream), #147 (tone lane).

---

## Files

| File | Role |
|---|---|
| `PadForge.Engine/Haptics/TritonPcmEncoder.cs` | Pure byte assembly for the PCM stream: the 0x86 command, the 0x88 stereo packet, G.711 mu-law, float to s16. No I/O. |
| `PadForge.App/Common/Input/TritonPcmSupport.cs` | `TritonPcmLowPassProvider` (the fourth-order Butterworth ahead of the downsample) and `TritonPcmWriteRing` (the eight-slot overlapped write ring). |
| `PadForge.App/Common/Input/HapticToneService.cs` | The lane itself: transport detection, `ArmTritonPcm` / `DisarmTritonPcm`, `StreamTritonPcmTick`, the idle catch-up drain, teardown, and the 0x83 tone lane the same sink runs on Bluetooth. |
| `PadForge.Engine/Haptics/HapticToneEncoder.cs` | The 0x83 LFO-tone report, the per-note trackpad and grip frequency tables, the wired and Bluetooth actuator sets. |
| `PadForge.App/Common/Input/AudioPassthroughService.cs` | Hands the composite DualSense persona's haptic channels to `HapticToneService.SubmitPersonaHaptics`, ahead of the Sony-target gate. |
| `PadForge.App/ViewModels/DeviceSlotConfig.cs` | `AudioTritonLowPassHz`, the one persisted setting the stream reads. |
| `PadForge.App/ViewModels/PadViewModel.cs` | `SelectedDeviceIsTritonPcm`, which shows the Actuator Low-Pass Cutoff row only for the PCM transports. |

Tests: `PadForge.Tests/TritonPcmTests.cs` (bytes, periods, mu-law golden vectors, the Butterworth response, the arm order, the teardown fence, the retry gate, the ring budget) and `PadForge.Tests/PersonaIdleDrainTests.cs` (the idle drain policy and a repro of the producer-consumer deficit).

---

## Which transport gets which lane

`HapticToneService` opens its own raw HID handle on the Triton's device path and decides the lane from the PID in that path (`HapticToneService.cs`, sink build):

| PID | Transport | Lane | Stream mode |
|---|---|---|---|
| `0x1302` | USB cable | PCM | Mode 0, 8 kHz stereo signed 16-bit |
| `0x1304`, `0x1305` | Proteus / Nereid dongle | PCM | Mode 8, 8 kHz stereo G.711 mu-law |
| `0x1303` | Bluetooth LE | 0x83 tones | none |

`PcmCapable = usbTriton || puckTriton` and `PcmMuLaw = puckTriton`. The dongle is held to mu-law because TritonLib blocks 16-bit on wireless: the dongle's USB interrupt interval halves its bandwidth (`TritonController.cpp:58`). Bluetooth stays on tones because no reference sustains full-rate PCM over direct BLE. Only steam-controller-live-haptics tries it, at reduced rates it marks experimental.

The stream is part of the same firmware jump table as the tone family. Valve's SDL driver enumerates output reports 0x80 through 0x85 (`controller_structs.h`) and stops there. 0x86 and 0x88 sit beyond that enum, which is why an earlier reading of SDL alone concluded the pad had no PCM path.

---

## The reports

### 0x86: stream configure

Four bytes: `[0x86, operation, target, mode]`. Operation 1 disables, 2 enables (`TritonPCMOperation`, `TritonController.h:623-626`). The transport pads the report to the interface's `OutputReportByteLength`, which is what hidapi does internally in every reference.

| Target | Meaning |
|---|---|
| 2 | `INT_BOTH`, both internal (grip) actuators |
| 5 | `TP_BOTH`, both trackpad actuators |

The 0x86 target table is not the 0x83 side table. The encodings are swapped between the two reports (`dissector.lua:167-174` against `264-275`), so the code never shares an enum across them.

Two hazards the encoder pins in comments. The same 0x86 value used as the type byte inside feature report 0x01 is the factory-reset command (`TritonController.h:230`). `TritonPcmEncoder` builds output reports only. And reconfiguring a running stream is rejected, reported in 0x44 bit 6 (`dissector.lua:158`), which is why the arm sequence disables first.

### Modes

Twelve discrete values, {8, 4, 2, 1} kHz by {s16, s8, G.711 mu-law} (`steam-controller-stuff readme.md:107-119`). PadForge ships two: mode 0 wired, mode 8 dongle. The iczero readme says 8 kHz is invalid on trackpad targets. Every working tool, and the requester's pad, run 8 kHz on target 5 anyway. Recorded, not obeyed.

### 0x88: stereo sample data

A fixed 64-byte layout, de-interleaved:

| Offset | Content |
|---|---|
| 0 | `0x88` |
| 1 | Bytes per channel: 30 in 16-bit mode, 31 in the 8-bit modes |
| 2..32 | Left channel area |
| 33..63 | Right channel area |

The right area always starts at 33, even in 16-bit mode where only 30 of each area's 31 bytes carry samples. Samples are little-endian s16 (`TritonController.cpp:67-71`) or one mu-law byte per frame (`64-65`).

| Mode | Frames per packet | Packet period |
|---|---|---|
| 16-bit | 15 | 1875 us |
| mu-law | 31 | 3875 us |

`PacketPeriodMicroseconds` is `frames * 1_000_000 / 8000` (`TritonController.cpp:88`).

A short final packet pads the tail of each channel area with the mode's true silence value: `0x00` for 16-bit, `0xFF` for mu-law. TritonLib pads mu-law tails with zero, which decodes to -8031 and clicks at every track end (`TritonController.cpp:109`, their bug). G.711 silence is the encoding of sample 0, and that is `0xFF`. The length byte stays the mode's full per-channel count so every packet represents a whole period, silence included.

### Mu-law

`MuLawEncode` is the standard Sun/G.711 encoder written from the algorithm: bias `0x84`, clip 32635, complemented output. Silence encodes to `0xFF`, positive full scale to `0x80`, negative full scale to `0x00`. Byte-identical to the encoders in live-haptics `haptics.cpp:91-99` and sc2ds `main.cpp:96-110`. One divergence on purpose: -32768 is clamped to -32767 first, because the C references negate an int16 in place and overflow on that one value. `FloatToS16` hard-clips and turns a NaN or infinity into silence rather than full-scale noise.

### 0x44: stream status

An input report carrying per-actuator stream state. PadForge does not read it. There is no flow control on the stream. If long streams ever drift, iczero's leaky-bucket in live-haptics is the sketch.

---

## The stream loop

The haptic sink thread ticks at 100 Hz (`TickHz`), 80 frames per tick at the 8 kHz stream rate (`PcmFramesPerTick`). A PCM-capable sink never reads the mono tone chain. It reads the stereo `MacroMixer` through its own chain, built at sink construction:

```
MacroMixer (48 kHz stereo)
  -> TritonPcmLowPassProvider (cutoff, default 250 Hz)
  -> SincResamplingSampleProvider to 8 kHz
```

Only one chain is ever read at runtime, so the pull model's single-reader rule holds.

### Mix, not arbitrate

The `MacroMixer` is the sum every source already feeds. On a PCM sink that means the persona's haptic channels (`PersonaBuf`, fed by `SubmitPersonaHaptics` from HIDMaestro's pacing thread, scaled by Haptics Gain 25 to 300%), macro sounds, and the system-audio mirror behind its engage gate. The stream consumes the mix and nothing is silenced by it. The requester's original limitation, exclusive ownership of the actuators by one source, dissolves into mixing.

Two things are synthesized into the stream instead of being sent as their own reports. The Audio-tab test tone and a Remote Link relayed tone render as a sine at the requested frequency and amplitude. A touchpad swipe tick becomes a 160 Hz sine (`PcmPulseHz`) with a decaying envelope, `PulseAmp * 0.6` max-wins with whatever envelope is still ringing, because racing a 0x82 click against an active stream is an interaction no reference documents. `PulseAmp` is read then zeroed on consumption, so a lowered slider takes effect on the next swipe (the 09-02 audit's F13).

### Arm and disarm

`StreamTritonPcmTick` marks `PcmLastContentMs` whenever a tick's peak is audible. The stream is wanted while a test tone is active or within `PcmHangoverMs` (2000 ms) of the last content. Wanted and not armed arms. Not wanted and armed disarms, so an idle pad costs nothing on the wire.

`ArmTritonPcm` (`HapticToneService.cs`) sends, in order:

1. 0x86 disable target 2
2. 0x86 disable target 5
3. sleep 10 ms
4. 0x86 enable target 2 with the transport's mode
5. 0x86 enable target 5 with the transport's mode

The leading disables make the enables idempotent, since a running stream rejects reconfiguration. This is TritonLib's own sequence (`TritonController.cpp:284-302`). `TritonPcmTests.ServiceContracts_ArmDispatchTeardownAndPulses` pins the order. A successful arm clears the pending buffer and the retry stamp. `DisarmTritonPcm` sends the disable pair with mode 0, the live-haptics teardown shape.

While armed the stream is fed continuously, silence included. The firmware's underrun recovery can itself fail (fwstrings 3849-3854), so starving it is not an option. The 2 s idle teardown and the ~12 ms re-arm bound the cost.

### The 250 ms re-arm gate

A failed arm used to retry on every loop iteration: four writes, a sleep, and a log line, up to five times per idle wake. `PcmArmRetryGapMs` is 250. `ShouldRetryPcmArm(nowMs, lastFailMs)` is true when no arm has failed yet or the last failure is at least 250 ms old. The failure log is edge-gated: one `TRITONPCM arm FAILED` line per streak, one `arm ok, failure streak ended` line when it ends. `TritonPcmTests.ArmRetryGate_WaitsAfterAFailure` pins it.

### Pending frames and the packet budget

Encoded s16 frames land in `PcmPending`, capped at `PcmPendingCapFrames` = 320 frames (40 ms), drop-oldest, with a drop counter for the diagnostic line. Each tick then packs whole packets from the pending buffer and submits them to the ring.

The budget is the reason the ring has eight slots. In 16-bit mode a tick produces 80 frames and a packet carries 15, so a tick submits 5.33 packets, six on the ticks where the fraction carries. The first ring had four slots, so the fifth and sixth submit were refused every tick, `PcmPending` pinned at its cap, and a quarter of every second was dropped (the audit's F18). `TritonPcmWriteRing.Slots` is 8: six plus two of completion-jitter headroom. Mu-law is easier, 80 / 31 = 2.58 packets per tick. `TritonPcmTests.WriteRing_HoldsATickOfPackets` pins the arithmetic.

### The overlapped write ring

`TritonPcmWriteRing` keeps up to eight 0x88 reports in flight through overlapped `WriteFile`, so the submission cadence is set by the pacing clock and not by per-write completion latency. This answers the requester's dongle measurement: synchronous writes sustained about 250 reports a second against a needed 258, so latency grew about 31 ms every second. With queued URBs the USB stack fills every interrupt-pipe slot, which no reference tool could do through synchronous hidapi writes. The shape follows `AudioPassthroughService.BtWritePool`: pre-pinned buffers, one event per slot, harvest completed slots on the next submit, leak rather than free anything the kernel may still touch. Only the sink's stream thread calls it.

`TrySubmit` returns false when every slot is busy, and the caller keeps the frames pending for the next tick. A hard write failure consumes the report and counts it (`HardFailures`), so a dead handle degrades to counted drops instead of a stalled stream.

A zero event handle from `CreateEventW` would leave a slot unreclaimable forever, and the ring would go silent once every slot had been used. The constructor throws in that case after releasing what it built. The sink catches it, disarms, logs `TRITONPCM ring FAILED ... falling back to 0x83`, and clears `PcmCapable`, so the pad plays tones for the rest of the session instead of nothing. `TritonPcmTests.WriteRing_RefusesAZeroEvent` drives that path through the injectable event factory.

### The low-pass

`TritonPcmLowPassProvider` is two cascaded RBJ biquads per channel with the standard fourth-order Q split (0.5411961, 1.3065630), applied at the 48 kHz mix rate before the sinc downsample, so content above the cutoff never reaches the wire. The default 250 Hz is the requester's hardware-measured threshold on their unit for where the actuators start to be audible as sound rather than felt as vibration. It is a setting because that is one unit's measurement, not a device specification. `SetCutoff` clamps to 60..1000 and rebuilds the four filters. It is called only from the reading thread, between reads, on the same 250 ms configuration cadence that refreshes the tone filter. The tests pin -3 dB at the cutoff, a steep slope above it, and a flat band well below it.

The #202 high-tone Cut and Fold settings are not applied on the PCM transports. `ApplyToneFilter` runs only on the `!PcmCapable` branch. The low-pass replaces their purpose there.

### The idle catch-up drain

The 09-01 follow-up. At idle the sink thread reads one 10 ms mixer block, then sleeps on the 15 ms coarse timer, which rounds to about 16 ms of wall time (idle deliberately avoids `timeBeginPeriod`). A producer that writes in wall-clock time, the persona feed at 10 ms of audio every 10 ms, outran that reader by roughly a third. `PersonaBuf` is a 250 ms `BufferedWaveProvider` with `DiscardOnBufferOverflow`, which drops new data and keeps the oldest, the worst polarity for latency. It pinned at cap in under a second, and every haptic onset then queued behind stale audio upstream of where the 40 ms `PcmPending` cap could reach. `MirrorBuf` has the identical shape at 500 ms.

`IdleCatchUpDrain` runs on each idle wake while `PersonaOn || MirrorOn`: while the deepest wall-clock-fed buffer holds more than `IdleDrainKeepMs` (15 ms), consume another block, up to `IdleDrainMaxBlocks` (5) per wake, and stop the moment a drained block carries content. Nothing is discarded blind. On a PCM sink the drain block is the full `StreamTritonPcmTick`, so an onset buried in backlog arms and submits in the wake it is found. On a tone sink the drain peak-checks and marks `LastContentMs` so the next iteration streams. `IdleDrainBlocks` counts the extra blocks for the diagnostic.

The transferable rule: every wall-clock producer feeding a pull-based mixer needs its drain rate matched at every consumer cadence, idle included. A drop-oldest cap on an output queue bounds nothing that accumulates in an input-stage buffer.

### Teardown

`TeardownSink` for `Family.Steam2026` raises the `TornDown` fence first, then disarms the stream if armed, disposes the ring, and sends the 0x83 stop on the lane's actuator set. `ArmTritonPcm` reads the fence before its first config write, so a stream thread that outlived the 3 s join can never re-enable the stream after the disable pair. The audit flipped the old order (disarm, then fence) and the contract test with it.

### Diagnostics

With `PADFORGE_DIAG` armed or the diagnostics log on:

| Line | Cadence | Fields |
|---|---|---|
| `HAPTICDIAG triton-build` | sink build | `usb`, `puck`, output and feature caps, path tail |
| `TRITONPCM arm` / `disarm` | each edge | mode, targets, mu-law, `outLen` |
| `TRITONPCM arm FAILED` / `arm ok, failure streak ended` | streak edges | |
| `TRITONPCM stream` | 5 s while armed | `pendingFrames`, `dropped`, `hardFail`, `lp`, `personaMs`, `idleDrained` |
| `HAPTICBUF` | 5 s | `personaMs`, `mirrorMs`, `idleDrained` |
| `TRITONPCM ring FAILED` | once | the exception, then the 0x83 fallback |

---

## Persona haptics reach every actuator sink

`AudioPassthroughService` receives the composite DualSense persona's four-channel PCM from HIDMaestro's pacing thread. Before #381 the haptic-channel submit sat after the Sony-target early return, so a slot whose only physical device was a Steam Controller or Switch pad had no Sony audio targets and returned before the submit: persona haptics never reached any actuator sink on such a slot (the requester's routing find in discussion #371). The submit now runs first, one volatile mask read when the feature is off. `TritonPcmTests.PersonaSubmit_RunsBeforeTheSonyTargetGate` pins the order.

---

## The 0x83 tone lane

Bluetooth, and the fallback when the ring cannot build. The full history lives in the HD-haptic tones section of [Controller Audio Internals](controller-audio-internals.md). The facts the PCM lane shares a sink with:

- `MsgHapticLfoTone`, output report 0x83, ten bytes with the id: `[0x83, actuator index, gain, frequency u16 LE, duration u16 LE, lfo_freq u16, lfo_depth u8]`. Actuator ids are 0 and 1 (trackpads), 3 and 4 (grips), index 2 skipped. Duration `0x7FFF` sustains. The stop form sets the gain byte to `0x80`.
- Gain is dB, signed, 0 = unity. `AmpToGainDb` maps amplitude to 0 dB at full scale and `20 log10(amp)` below, floored at -40, never positive.
- Grips are driven through the per-note trackpad-to-grip frequency tables (`TritonTrackpadHz`, `TritonGripHz`, 128 entries each, ported from SteamHapticsSinger), so a grip sounds the same pitch as a trackpad across the range.
- Bluetooth arms all four actuators with a leading zero 0x80 rumble clear, which resets the haptic engine out of the wedged state a burst flood leaves it in. Re-arms are capped at one per 40 ms, SDL's own resend interval.
- The wired pad cannot cleanly render four simultaneous 0x83 tones, a firmware limit settled with a standalone probe. Wired drives the pair {0, 3} (`TritonActuatorsWired`). This matters only when a wired pad falls back from PCM.
- Write style is `WriteFile` on the interrupt pipe for wired and dongle (wired firmware refuses `SET_REPORT`, error 31) and `HidD_SetOutputReport` over Bluetooth. Each report is padded to the queried `OutputReportByteLength`.

---

## References

Cloned beside the repository and read in full. The line numbers are the ones the code cites.

| Reference | What it grounds |
|---|---|
| TritonLib, `src/TritonController.cpp:55-135`, `264-303`, `include/TritonController.h:230`, `623-626` | 0x86 operations and the arm sequence, frames per packet, packet period, the 16-bit wireless block, the factory-reset collision |
| steam-controller-live-haptics, `haptics.cpp:79-99`, `202-218`, `555-570` | mu-law tables and encoder, the 0x88 layout, the disable-pair teardown, the underrun lesson |
| sc2ds, `main.cpp:88-110`, `467-491` | second mu-law encoder, second 0x88 layout |
| steam-controller-stuff, `dissector.lua:63-201`, `readme.md:59-135` | firmware-derived report and mode tables, 0x44 bit 6, the 0x86 versus 0x83 target tables |
| SDL, `src/joystick/hidapi/steam/controller_structs.h` | the 0x80-0x85 tone family enum, `MsgHapticLfoTone`, `MsgHapticRumble` |
| SteamHapticsSinger, `main.cpp:24-37`, `252-285` | the 0x83 byte layout, 0 dB as the reference gain, the trackpad and grip note tables |
| OpenPuck, `PROTOCOL.md 9.1`, `haptics.cpp` | the dongle relays output reports 0x80-0x86 to the pad's slot |
| SteamlessController, `SteamController.cpp:337-359`, `HidDevice.cpp:181-220` | the one-report-per-40 ms write discipline, the overlapped `WriteFile` idiom |

The requester (discussion #371) ran the shipped stream on hardware: native PCM works and the mixer resolved the swipe and mirror conflicts. The 09-01 idle-drain fix and the 09-02 audit changes are pinned by tests and arithmetic, not by a bench run.

---

## Related pages

- [Controller Audio](../features/controller-audio.md): the user guide, including the Actuator Low-Pass Cutoff row.
- [Controller Audio Internals](controller-audio-internals.md): the sink model, the tone reducer, and the rest of the HD-haptic tone lane.
- [Remote Link Internals](remote-link-internals.md): how a relayed tone reaches this sink.

---

*Last updated for PadForge 4.4.0.*
