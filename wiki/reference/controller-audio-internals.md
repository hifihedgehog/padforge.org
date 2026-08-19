# Controller Audio Internals

*How `AudioPassthroughService` drives the DualSense and DualShock 4 speaker: the per-device sink model, the WASAPI loopback mirror, the USB and Bluetooth transports, and the Opus and SBC encoders.*

This is the developer-side companion to [Controller Audio](../features/controller-audio.md) (the user guide) and issue #83.

---

## Files

| File | Role |
|---|---|
| `PadForge.App/Common/Input/AudioPassthroughService.cs` | The core. Sinks, captures, the worker and Bluetooth threads, USB and BT transports, Opus encode, remote-audio hooks, and the composite USB persona feed. `internal static class`. |
| `PadForge.App/Common/Input/Ds4SbcEncoder.cs` | Clean-room SBC encoder for DualShock 4 Bluetooth audio. |
| `PadForge.App/Common/Input/SoundMacroService.cs` | Macro sound decode and playback. Feeds the per-slot sink mixers, including the Wii speaker and HD-haptic tone sinks. |
| `PadForge.App/Common/Input/WiiSpeakerService.cs` | The Wii Remote speaker sink. Real 8-bit PCM at 2 kHz over raw HID. `internal static class`. See [Wii Controllers Internals](wii-controllers-internals.md). |
| `PadForge.App/Common/Input/HapticToneService.cs` | The HD-haptic tone sink for Switch and Steam controllers (#147). Reduces the macro mix to a tone and encodes per family. `internal static class`. |
| `PadForge.Engine/Haptics/HapticToneReducer.cs` | PCM-to-tone reduction: one (dominant frequency, amplitude) pair per rumble tick. |
| `PadForge.Engine/Haptics/HapticToneEncoder.cs` | Per-family wire-byte encoders for the tone requests. |
| `PadForge.App/Common/Input/UserEffectsDispatcher.cs` | Asserts the DualSense firmware speaker path and the master-volume byte on each output report. |
| `PadForge.App/Common/Input/RemoteLinkOutputRouter.cs` | The `ShipAudio` (speaker PCM) and `ShipHapticTone` (tone pair) producer side of the [Remote Link](remote-link-internals.md) relay. |
| `PadForge.App/Services/InputService.cs` | Wires the config provider and the `SendAudio` / `OnRemoteAudioReceived` delegates. |

Dependencies: `Concentus` (pure-C# Opus) and `NAudio.Wasapi` (loopback capture, `WasapiOut`, mixers, Media Foundation decode).

Identity constants at the top of the service: `Rate = 48000`, `SonyVid = 0x054C`, `Ds5Pids = {0x0CE6, 0x0DF2}` (DualSense, DualSense Edge), `Ds4Pids = {0x05C4, 0x09CC, 0x0BA0}` (DualShock 4 v1, v2, and the Sony USB wireless adaptor).

---

## The sink model

One `Sink` exists per speaker-capable pad, held in `Dictionary<Guid, Sink> _sinks` keyed by device InstanceGuid under `_lock`. Keying on the device, not the slot, is deliberate: a slot holding two DualSense gets two independent sinks with independent Opus sequence counters. Per-device runtime state is never `static`, which is the rule that fixed the garbled-audio bug when two DualSense shared a counter.

Each sink carries its audio graph (`MacroMixer`, a 48 kHz stereo `MixingSampleProvider`, plus `Source`, the mixer-and-loopback combiner), its transport (`IWavePlayer Player` for USB, or `IntPtr BtHandle` plus a `BtWritePool Tx` for Bluetooth), and its per-lane encoder state. The DualSense lane holds `Ds5OpusEncoder`, `Ds5Seq` (the report sequence nibble), and `Ds5PktCounter`. The DualShock 4 lane holds `Ds4Sbc`, the pending-sample buffer, the SBC frame queue, and the resampler carry.

`BtWritePool` is a fixed 8-slot overlapped non-blocking HID write pool (`WriteFile` with `FILE_FLAG_OVERLAPPED`). `TrySend` returns immediately. Saturation drops the frame, an I/O error flags a hard fail. The kernel HID IRP queue is the jitter buffer, roughly 80 ms in flight across the eight slots.

---

## Threads

Two threads, started by `EnsureThreads_NoLock`:

1. **`WorkerThreadMain`** ("PadForge.AudioWorker") is the single owner of all device I/O. It waits on `_workSignal` or wakes every five seconds and runs `ReconcileOnWorker`. Sink build and teardown, capture start and stop, and the `CreateFile` on Bluetooth handles all happen here and only here.
2. **`BtThreadMain`** ("PadForge.BtAudio", highest priority) runs the Bluetooth cadence loop. It never does transport I/O of its own beyond `Tx.TrySend`. On a transport error it sets `TransportFailed` and lets the worker rebuild.

The worker reconcile runs five phases to keep I/O outside the lock: build the desired-sink list (phase 1, no lock), diff against `_sinks` (phase 2, under lock, no I/O), build and dispose transports (phase 3, unlocked), reconcile captures (phase 4), then notify `SoundMacroService` and sweep expired vendor-audio tests (phase 5). The desired-sink list walks the 16 slots through `EnumerateAssignedSonyPads` and `FindOnlineSonyDevice`, which gates on `IsOnline`, a non-empty `DevicePath`, the Sony VID, and a DualSense or DualShock 4 PID. Bluetooth is detected by the HID-over-BT service GUID in the device path. A wired DualShock 4 is skipped because it has no USB audio interface. The Sony USB wireless adaptor (`0x0BA0`) is the one exception and keeps its sink.

`BtThreadMain` runs at `CadenceMs = 10 + 2/3` (10.667 ms) and pulls 512 frames per tick. It applies a small ring-cushion drift trim, runs a two-second idle gate, and dispatches `Ds4BtTick` or `SendDs5BtFrame`. Timing uses `timeBeginPeriod(1)` and a high-resolution waitable timer. A late tick is skipped, never repaid, because the firmware drops back-to-back bursts.

---

## System-audio mirror (WASAPI loopback)

`CaptureEntry` wraps one `WasapiLoopbackCapture` plus a half-second ring, stored in `Dictionary<string, CaptureEntry> _captures` keyed by endpoint ID. `ReconcileCapturesOnWorker` resolves the default render endpoint once, maps each passthrough-on sink's `MirrorSourceId` (empty string means follow the default, re-resolved every pass) to a wanted endpoint, starts the missing captures, and points each sink at its `CaptureEntry`. A pad's own endpoint is excluded so the mirror never feeds the pad back into itself.

`StartCaptureEntry` opens the device, rejects a non-active endpoint, and on each `DataAvailable` converts any source rate and format to 48 kHz stereo float into the ring. `SinkSource.Read` holds a per-sink cursor over the shared ring, resyncs only on a genuine stall, and adds the loopback samples on top of the macro mix at full scale. Volume lives in the firmware byte, not the samples.

---

## Macro sounds

`SoundMacroService` decodes WAV, MP3, M4A, AAC, WMA, and FLAC through `MediaFoundationReader` (or a streaming reader for `pfsound://` package refs), resamples to 48 kHz stereo, and caches the PCM under a 128 MB LRU cap.

`StartPlacements` is the routing core. It calls `AudioPassthroughService.GetSlotSinkMixers(slot, out pendingActivation, deviceFilter)`, which returns the `MacroMixer` of every live sink on the slot (optionally filtered to one device GUID). When the slot has eligible speaker pads whose sinks are not live yet, `pendingActivation` is true, the worker is signalled, and the caller drops the sound rather than leak it to the PC speakers. Macro demand itself is never latched in the audio service: the worker re-reads it every pass through `SlotWantsMacroAudioProvider`, which `InputService` wires to `SoundMacroService.SnapshotWantsControllerAudio` over the slot's macro snapshot. When the slot has no controller sink and no device filter, it falls back to a per-slot system-default `WasapiOut`, where the volume is applied in the sample domain instead.

`PlayTestBeep(slot, deviceGuid)` routes an 880 Hz, 200 ms tone through `StartPlacements` with a device filter, so the Audio-tab test hits only the selected device and never fans out to the slot's other pads.

---

## USB transport

The USB branch of `BuildTransportOnWorker` reads the HID interface's PnP container ID through cfgmgr32, then matches a render `MMDevice` whose container ID is the same. If that endpoint is disabled in Windows it re-enables it through `IPolicyConfig`, then restores the prior default if Windows promoted the pad to default. `UsbFrameProvider` shapes each frame through `MapMirrorChannels`, which reads the device's Audio Output Path once per `Read`. Automatic and Speaker Only silence channel 0 and put the mono program mix `(L+R) * 0.5` on channel 1 (the firmware speaker tap). Headphones (Stereo) puts L on channel 0 and R on channel 1. The mono headset paths put the downmix on channel 0, with channel 1 either silent or a copy for the split path. Follow Headphone Jack resolves to one of the others in `ResolveOutputPath` before the shaper sees it. Channels 2 and 3 are the pad's voice-coil actuators: zero unless a composite persona is feeding them. Playback is `WasapiOut` in shared mode with event sync at 30 ms latency.

---

## DualSense Bluetooth (Opus over report 0x35)

Constants: 480 samples per Opus frame (10 ms at 48 kHz), 200 bytes per frame (hard CBR at 160 kbps), and a 334-byte report. `CreateDs5OpusEncoder` builds a Concentus encoder configured `OPUS_APPLICATION_AUDIO`, 160000 bps, CBR, pre-created at transport build so the first frame does not pay construction cost.

Each tick time-compresses the 512-frame pull to 480 samples, then `SendDs5BtFrame` encodes it and assembles the 0x35 report: byte 0 is the report ID, byte 1 carries the sequence nibble (`Ds5Seq` advances mod 16), a 0x11 session-header packet carries `Ds5PktCounter` and the mic-session byte, and an audio-lane packet carries the 200-byte Opus payload. The last four bytes are a reflected CRC32 pre-seeded with the `0xA2` Sony Bluetooth output prefix. The firmware contract from the issue #83 hardware experiment is one report per tick, never bursts.

Over Bluetooth the sink is addressed by packet ID, not by the firmware's output-path register. `Ds5BtAudioLanePid` returns `0x13` for the internal speaker (Automatic and Speaker Only) and `0x16` for every headset path. One report ID gets one stream: `Ds5BtWantsBothLanes` returns false, because two 0x35 reports per tick sharing one sequence counter made each lane's stream see jumps of two and warble. Every path except Headphones (Stereo) folds the frame to mono before encoding (`Ds5BtFrameNeedsMonoFold`), because the mono speaker taps one channel of a stereo stream rather than downmixing it.

---

## DualShock 4 Bluetooth (SBC over report 0x17)

`Ds4SbcEncoder` is a clean-room SBC encoder written from the A2DP specification Appendix B, with no libsbc or GPL lineage. Fixed config is 32 kHz, 8 subbands, 16 blocks, joint stereo, SNR allocation, bitpool 48, producing 109-byte frames. The spec's segment-folded analysis window is un-folded at the analysis matrix, and the filterbank conventions were pinned against ffmpeg's decoder at roughly 76 and 67 dB round-trip SNR.

At transport build the DualShock 4 branch sends a one-shot 0x11 control report to enable the audio path and set headphone and speaker volume bytes. `Ds4BtTick` folds the frame to mono (this lane always routes to the internal speaker, which taps one channel), resamples 48 kHz to 32 kHz with a persistent phase and a sample carry across ticks, encodes each complete 256-sample block to an SBC frame into a queue bounded at 12 frames, and drains it preferring the four-frame 0x17 report and falling back to the two-frame 0x14. It wakes at four buffered frames. Unlike the DualSense cadence, the DualShock 4 path is availability-driven and allows bursts. Byte 5 of the report selects the internal speaker (`0x02`, against `0x24` for the headset jack), and bytes 3 and 4 carry a 16-bit frame counter that advances by frames-per-report.

---

## Composite USB persona lanes

A slot whose virtual controller is a composite USB persona has a real Windows endpoint the game renders into. HIDMaestro delivers that PCM as four-channel windows (speaker L/R, haptic L/R) on its pacing thread, and `AttachPersonaFeed` routes it to the slot's physical Sony pads. The feed's presence is itself sink demand, so a composite slot builds its pads' transports with passthrough off and no macros.

The speaker channels land in `_personaSpeakerRings` and are summed into each sink's render path inside `SinkSource.Read`, so they ride the same Opus and shared-mode WASAPI transports as macros and the system mirror. The haptic channels land in `_personaHapticRings` and split by transport. On USB they are the pad's UAC channels 2 and 3. On Bluetooth they get their own 142-byte report 0x32 carrying packets 0x11 and 0x12, built by `BuildDs5BtHapticReport`, decimated 16:1 from the 48 kHz tick to 3 kHz stereo s8 by block mean. The 0x32 stream keeps its own sequence and packet counters (`Ds5HapticSeq`, `Ds5HapticPktCounter`), separate from the 0x35 pair, for the same reason the per-device split exists: the firmware tracks sequence per stream. It never folds into the speaker report, because no reference emits packets 0x12 and 0x13 together.

The microphone runs the other way. On USB it is the pad's own container-matched capture endpoint. On Bluetooth a parallel synchronous HID handle reads the pad's input reports, one 71-byte Opus packet per report, decoded as mono at 48 kHz. Decoding it as stereo on the strength of the packet's TOC byte produced full-scale noise on the consumer side, so `BtMicChannels` stays 1. Mic-open is not latched in firmware, so `Ds5MicSessionByte` rides byte 4 of the 0x11 header on every audio report and has to track the live session, otherwise a steady close byte re-closes the mic the persona just opened. The decoded Bluetooth mic frames also tee to `VoiceMacroService.SubmitPadMic48k` when that pad has a recognition session (#317), pre-gain, so the pad's voice phrases hear what the pad hears rather than what `MicGain` shaped for Windows.

---

## Master volume as the firmware speaker byte

Master volume is never scaled into the samples on the controller path. For the DualSense it is asserted on every output report in `UserEffectsDispatcher`. When the device wants the speaker path, the dispatcher sets the valid flags, writes `speakerVolume` mapped from the 0-100% master onto the firmware's `0x3D` to `0x64` window (0 mutes), and sets the speaker pre-gain byte. It also routes the audio-control flags to the internal speaker, but only when the resolved Audio Output Path is Automatic. An explicit path owns that byte and its enable bit, and the #83 block keeps just the volume half. When the sink tears down, a one-shot restores the headphone path, again only when no explicit path is forced. `SetSlotVolume` retunes live because the byte is read per report. The DualShock 4 path has no per-tick volume byte. Its volumes are fixed in the one-shot enable report.

---

## HD-haptic tones (#147)

*Playing macro sounds as tones through a controller's haptic actuators: the reduce step, the per-family encoders, and where the fidelity ceiling sits.*

Some controllers have no speaker but do have haptic actuators: LRAs (linear resonant actuators) on the Nintendo pads, haptic transducers on the Steam pads. `HapticToneService` treats them as a tone generator. A Switch Joy-Con L/R, a combined Joy-Con pair, Switch Pro, Steam Controller 2015, Steam Deck, or Steam Controller 2026 (Triton) assigned to a slot becomes an output sink whose `MacroMixer` is returned to `SoundMacroService` alongside the Sony and Wii sinks, so a macro Play Sound fans out to it with no macro-layer change. `FamilyOf` sorts the device by VID and PID against the SDL `controller_list.h` table, so every transport and revision of a family (wired, BLE, dongle) is caught rather than a hand-picked PID subset. Switch 2 is excluded: no reference plays an audible tone on its actuator, so it gets no Audio tab.

`FamilyOf` maps the paired-set PID `0x2008` to `Family.JoyConPair`, the id SDL reports when it combines two Joy-Cons by default (issue #184). That set has no HID path of its own to open: SDL's `nintendo_joycons_combined` is a synthetic placeholder, not a real `\\?\HID#...` path, so `CreateFileW` on it fails. `BuildSink` calls `SelectPairChildPaths` to resolve both real child paths (Left `0x2006` as primary, Right `0x2007` as second) and drives **both coils** (#223). `OpenPairSecondChild` opens the second child on its own handle, timer, probed write path, and `OutputReportByteLength`, and runs the init subcommands (`0x03` arg `0x30` input-report mode, `0x48` arg `0x01` enable vibration) on it. A pair that resolves only one child degrades to single-coil and `RetryPairSecondHandles` picks the missing coil up on the 3-second reconcile.

Side routing follows the slot's merged vibration snapshot: left motor active plays the left coil, right the right, both or neither play both. A side stays hot for `PairSideHoldMs = 300` ms after its motor drops so packet-rate motor flap does not strobe the tone, and a side going cold gets one neutral half before silence. The Audio-tab Test button and remote-driven sinks bypass the routing and always play both coils. Two simultaneous pairs no longer stack on one set of children: `ResolveUnclaimedPairChildren` walks `FirstUnclaimed` over the paths no other live pair sink already holds, so each physical Joy-Con gets exactly one writer. Residual on record: nothing at this layer proves the left it picks is the physical partner of the right it picks, because SDL owns the pairing and exposes only the combined device with an empty serial.

An LRA reproduces one frequency at a time: a tone with an amplitude envelope, not PCM. A pad with more than one actuator (a Pro or Joy-Con pair has two coils, the 2015 Steam Controller has two haptics, the Steam Controller 2026 has four LRAs, two trackpads and two grips) still plays that single mono tone. The extra actuators do not buy stereo or fidelity. Beeps, alerts, and melodic cues land. Speech and music do not. Each tick the service collapses the macro mix to one tone:

- `HapticToneReducer` (`PadForge.Engine/Haptics/HapticToneReducer.cs`) reads the dominant frequency from the normalized autocorrelation peak over the playable lag range, and the amplitude from windowed RMS. Below a silence RMS the amplitude is 0. An unvoiced burst holds the last pitch so the coil does not jump around.
- `HapticToneEncoder` (`PadForge.Engine/Haptics/HapticToneEncoder.cs`) turns that `(frequency, amplitude)` pair into the exact wire bytes each family expects. The bytes are grounded in the cloned references (joycon-singer, SteamControllerSinger, SteamHapticsSinger, Nintendo_Switch_Reverse_Engineering). The C# is original.

The encoders differ by family:

| Family | Wire form | Notes |
|---|---|---|
| Joy-Con L/R, Pro, combined pair | `0x10` HD Rumble payload, 4-byte group | `EncodeJoyConRumble`: closed-form log2 frequency and two-segment log amplitude. Frequency folded into the `[41, 626]` Hz LF band. The combined pair writes each child's own packet on its own handle, side-routed by the active motor (#223). |
| Steam Controller 2015, Steam Deck | `0x8F` square-wave feature blob, 64 bytes | `EncodeSteamClassic`: period and repeat from the note frequency. Pitch-only, no gain byte. The Deck reuses the 2015 encoder. |
| Steam Controller 2026 (Triton) | `0x83` LFO-tone OUTPUT report, 10 bytes | `EncodeTritonTone`: frequency `u16` LE plus a signed `gain_db` byte (0 dB unity, floored at -40). Never the 2015 `0x8F` feature report. Grips are driven through a per-note map so they match trackpad pitch. |

Why raw HID and not SDL rumble: the bundled SDL fork's Switch and Steam drivers hard-code the rumble carrier and vary only amplitude, so tone playback needs the same raw-HID writer pattern the Wii and Sony speaker paths use. The one exception is the 2015 Steam Controller, whose `0x8F` feature blob is forwarded through `SDL_SendGamepadEffect` (with a raw `HidD_SetFeature` fallback when SDL did not open it as a gamepad). The Joy-Con, Deck, and Triton tone lanes each write their own raw HID handle.

### High-tone cut and fold (#202)

An LRA loses fidelity above its resonance, and a loud high pitch on a wrist-worn coil is unpleasant. `HapticToneService` filters the reduced pitch upstream of the family switch, so every encoder sees the same clamped pair. Three settings, held in `ToneFilterOff` / `ToneFilterCut` / `ToneFilterFold` (0, 1, 2): off passes everything, cut and fold act above a limit. The `(mode, limitHz)` pair is resolved per (slot, device) through `ToneFilterProvider` and re-read by each sink at about 4 Hz on its own stream thread.

- **Cut** zeroes the amplitude above the limit. It re-emits the last passing pitch rather than the cut pitch. The pitch-only `0x8F` square (Steam 2015 and Deck) never reads amplitude, so a cut tick carrying the beep pitch would re-arm the square at the exact frequency the user cut.
- **Fold** octave-halves the pitch into the pass band, keeping the pitch class.

`ApplyToneFilter` clamps the user limit to `100..1300` Hz and carries a boundary-hysteresis latch (a Schmitt trigger). The reducer measures pitch on the integer-lag grid `ReduceRate / lag`, so a tone near the limit lands on one of two adjacent grid pitches, and per-tick noise flips which one wins. A bare `>` turns that flip into an octave flap at the tick rate. Once engaged, the tie's lower grid member stays engaged, so the pair folds together instead of alternating folded and unfolded. Disengage needs the measurement a full grid step below the limit. The filter runs on the Test button too, so the test never lies about the setting. Owner-side Remote Link frames are exempt, because the consumer applied its own filter before shipping.

### System-audio mirror and engage gate (#185)

Like the Sony sink, the Wii and haptic-tone sinks carry their own system-audio mirror. `WiiSpeakerService.ReconcileMirrors` and `HapticToneService.ReconcileMirrors` read the same `PassthroughConfigProvider` and add a `WasapiLoopbackCapture` onto the sink's `MacroMixer`, so a mirrored Windows output plays through the Wii speaker, or through a haptic pad reduced to a pitch-following tone.

On the haptic path that mirror can gate. When `ReconcileMirrors` starts a mirror, `StartMirror` wraps only the mirror's sample provider in a `GatedMirrorSampleProvider` bound to a per-(slot, device) `EngageCell`. The gate has three modes: Always (default, the cell stays engaged), Input (engaged while a chosen descriptor is held, an empty descriptor reads as always-on), and Rumble (engaged while any of the slot's four vibration motors is nonzero). `InputManager.UpdateHapticMirrorEngageStates` settles every cell once per poll and applies a release-delay hold through `HoldEngaged`, clamped to `0..10000` ms, so the tone does not clip off the instant the source drops. The gate wraps the mirror input alone. Macro sounds and the Test button bypass it and always play.

---

## Wii Remote speaker

*The one PCM sink among the tone paths.*

The Wii Remote has a real speaker, not haptic coils, so its macro-audio output is genuine 8-bit PCM at 2 kHz, not a reduced tone. It is driven by `WiiSpeakerService` (`PadForge.App/Common/Input/WiiSpeakerService.cs`) on its own raw HID handle, following the same per-slot sink model and `MacroMixer` handoff to `SoundMacroService` as the Sony path here and the tone path above. The full protocol lives in [Wii Controllers Internals](wii-controllers-internals.md). It is listed here because it is the third macro-audio sink family `SoundMacroService.StartPlacements` fans into, after the Sony sinks and the tone sinks, and it shares the sink model. Its wire format is PCM speaker reports, distinct from the `HapticToneEncoder` tone bytes.

---

## Remote Link audio

On the receive (owner) side, `InputService` subscribes to the link server's audio event, resolves the exposed slot to a local source device, and calls `AudioPassthroughService.FeedRemoteAudio`. That writes the incoming s16 48 kHz stereo PCM into a `RemoteAudioRing` and marks the device's remote-audio demand. The worker then builds a real Bluetooth or USB sink for it, and `SinkSource.Read` drains the ring instead of loopback and macros, so the relayed audio reaches the physical pad speaker.

On the produce (consumer) side, a `peer://` pad becomes a sink with no local transport. The Bluetooth thread's peer lane calls `ShipPeerAudioTick`, which pulls the same per-pad mix, converts to s16, and flushes exact 1024-byte blocks through `RemoteLinkOutputRouter.ShipAudio`. The PCM is shipped full-scale. The volume is the owner's firmware byte. See [Remote Link Internals](remote-link-internals.md) for the wire side.

### Haptic-tone relay (#138 x #147)

A haptic pad relays a tone pair, not PCM. On the consumer side a `peer://` haptic sink runs its mixer and reducer as usual, then the stream loop ships the reduced `(frequency, amplitude)` pair through `RemoteLinkOutputRouter.ShipHapticTone` instead of writing hardware. The wire form is `OutputEffectCodec.EncodeHapticTone`, a small tone frame, distinct from the s16 PCM block the speaker relay sends. Silent steady state is deduped. A playing tone ships every tick, because the owner's hangover expiry needs the refresh.

On the owner side `InputService` hands each received frame to `HapticToneService.ApplyRemoteTone`, which sets the direct-drive override on the device's sink (the same idiom as the Test tone). When the owner maps that device to no local slot, `ApplyRemoteTone` builds a `RemoteDriven` sink on demand, queued off the UDP receive thread so the raw HID open never blocks, and `Reconcile` reaps it once frames stop arriving. The owner is a pure transcoder: it re-encodes to the device's wire bytes but does not re-apply the tone filter or the slot volume, since the consumer already did both.

---

## Related pages

- [Controller Audio](../features/controller-audio.md): the user guide for this feature.
- [Services Layer](services-layer.md): where `AudioPassthroughService` sits among the engine services.
- [Input Pipeline](input-pipeline.md): the polling loop that feeds device state, and the Sony effect dispatch.
- [Remote Link Internals](remote-link-internals.md): the relay that carries this audio between two PCs.
- [Wii Controllers Internals](wii-controllers-internals.md): the Wii Remote speaker sink and its PCM protocol.
- [Macros](../guides/macros.md): the Play Sound action that feeds the sink mixers.

---

*Last updated for PadForge 4.3.0.*
