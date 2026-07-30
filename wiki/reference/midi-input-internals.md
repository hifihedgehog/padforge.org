# MIDI Input Internals

*How a Windows MIDI endpoint becomes a mappable input device: the `MidiInputDevice` source, the Windows MIDI Services runtime, the UMP parser, and the descriptor and coercion path.*

This is the developer-side companion to [MIDI Input](../features/midi-input.md) (the user guide) and issue #128.

---

## Files

| File | Role |
|---|---|
| `PadForge.App/Common/Input/MidiInputDevice.cs` | `MidiInputDevice` (the device) and `MidiInputRuntime` (the WM2 session and endpoint enumeration). |
| `PadForge.Engine/Common/MidiInputState.cs` | The `MidiInputState` sub-state on `CustomInputState`. |
| `PadForge.App/Common/Input/InputManager.Step1.UpdateDevices.cs` | Phase 1e enumeration and registration, and `ShutdownMidiInputs`. |
| `PadForge.App/Common/MappingDisplayResolver.cs` | The MIDI picker block (`AddMidiChoices`). |
| `PadForge.Engine/Common/Mapping/SourceCoercion.cs` | `SourceType.Midi`, the classify and parse helpers, and the three reader branches. |
| `PadForge.Engine/Common/InputTypes.cs` | `InputDeviceType.Midi = 27`. |
| `PadForge.App/Common/Input/MidiVirtualController.cs` | The unrelated MIDI **output** virtual controller. |

---

## MidiInputDevice: an endpoint as an input device

`MidiInputDevice` implements `ISdlInputDevice`, the same contract the SDL gamepads, keyboards, mice, and web and peer devices implement, so the rest of the [Input Pipeline](input-pipeline.md) treats it uniformly. One instance exists per connected MIDI endpoint. `GetInputDeviceType()` returns `InputDeviceType.Midi` (27), which flows into `UserDevice.CapType` and is the field the picker keys on.

It exposes zero gamepad surface: no axes, buttons, hats, or device objects. The entire mappable surface lives in `CustomInputState.Midi`, the same pattern as the touchpad sub-state. Its identity is synthetic. The VID and PID spell "MI" and "MD", the device path is `midi://{endpointId}`, and the instance and product GUIDs are MD5 hashes of the endpoint ID and name. It has no rumble, haptic, or motion.

`Open` pulls the shared WM2 session, creates an endpoint connection, subscribes to `MessageReceived`, and opens it. Every one of those calls is a WinRT RPC into the MIDI service, and `Open` runs on the polling thread, so the whole body runs on a worker bounded by a 3 s timeout (`OpenTimeoutMs`). A hung open is orphaned and torn down later on its own thread. `Dispose` unsubscribes and hands the disconnect to `MidiInputRuntime.Disconnect`, which is fire-and-forget on a worker for the same reason: a hung midisrv wedged the whole engine through exactly this lane (live stack, 2026-07-23), and nothing waits on the service from the polling thread anymore. The WinRT callback thread writes state under a lock, and the polling thread reads a pooled copy: `GetCurrentState` fills one of two reused snapshot buffers (`PooledInputStatePair`) via `CopyInto` rather than allocating a fresh clone per poll.

---

## MidiInputRuntime: the shared WM2 session

`MidiInputRuntime` is a static class over `Microsoft.Windows.Devices.Midi2` (Windows MIDI Services). Its `Session` property lazily creates one `MidiSession`, but only after `MidiVirtualController.IsAvailable()` returns true. It never initializes the SDK itself. It rides the runtime the output side brings up, and returns null when Windows MIDI Services is absent.

`EnumerateEndpoints` calls `MidiEndpointDeviceInformation.FindAll` and keeps only the normal message endpoints (`MidiEndpointDevicePurpose.NormalMessageEndpoint`), skipping the diagnostic endpoints, the in-box synth, and the virtual-device responder twins. PadForge's own MIDI virtual-controller endpoints still appear as inputs (the no-hardware loopback path) because the service publishes a client-visible twin of every virtual device as a normal endpoint. The device-side responder twin is for the hosting application only, and enumerating it is how the input lane used to poke stranded responder corpses every sweep (the MIDI VC lifecycle-wedge fix). `Shutdown` disposes the session and must run before `MidiVirtualController.Shutdown` on app exit.

---

## Message parsing

`OnMessageReceived` reads the first UMP word and the message-type nibble. The whole body is wrapped in try-catch so a malformed packet cannot take down the WinRT callback thread. It handles MIDI 1.0 (32-bit UMP, message type 0x2) and MIDI 2.0 (64-bit UMP, message type 0x4):

| Opcode | Becomes | State write |
|---|---|---|
| Note On (0x9) | A button, on while held | 1.0: `SetNote(note, velocity != 0)`, 2.0: `SetNote(note, true)` |
| Note Off (0x8) | Button release | `SetNote(note, false)` |
| Control Change (0xB) | An absolute 0-127 value | `SetCc(cc, value)` |
| Pitch Bend (0xE) | A 14-bit (or 16-bit in MIDI 2.0) centered axis | `SetPitchBend(scaled)` |

On the MIDI 1.0 path velocity decides on versus off (a Note On with velocity 0 is a Note Off), and velocity is never stored as a value. The MIDI 2.0 path is different. A Note On there writes `SetNote(note, true)` regardless of velocity, because a MIDI 2.0 Note On with velocity 0 is a valid note-on, so on the 2.0 branch only a Note Off (0x8) releases the note. Reads are channel-merged (omni). The channel nibble is never inspected, so a note or CC means the same thing on any channel. Channel pressure, polyphonic aftertouch, and program change have no case and are dropped.

The channel-mode CCs get extra handling in the CC path, after their value is written:

- **All Sound Off (CC 120) and All Notes Off (CC 123)** clear every note lane, so a controller that ends a phrase with one of these instead of per-note Note Off does not leave mapped note-buttons latched on.
- **Omni Off/On and Mono/Poly (CCs 124–127)** clear the note lanes too, since each carries All Notes Off semantics per MIDI 1.0. CC 122 (Local Control) clears nothing.
- **Reset All Controllers (CC 121)** applies the RP-015 reset to the lanes this state models: pitch bend recenters, the mod wheel (CC 1) and pedals (CCs 64–67) drop to 0, expression (CC 11) returns to 127, and the RPN and NRPN selectors (CCs 98–101) return to null. Each reset lane's encoder pulse machine is cleared in both directions, so queued detent pulses stop with the reset. Bank, volume, pan, and sound lanes stay put, per RP-015. Without this, a keyboard panic (121 plus 123) released mapped notes but left a mapped Pitch Bend axis frozen off-center.

A Control Change also drives the relative-encoder reader. Only the binary-offset style is decoded (center 0x40, 0x41 is one step up, 0x3F is one step down). A small positive delta queues an up pulse on lane `2*cc` and a small negative delta queues a down pulse on `2*cc+1`. Values outside the band read as an absolute fader and never pulse. The two's-complement and signed-bit encoder styles read as absolute jumps. The pulse machine presses each detent for 24 ms then gaps 12 ms, caps the backlog at four pending pulses (so a fast spin drops detents rather than lagging), and tops out near 28 detents per second. `MidiInputState` holds the note, CC, encoder up and down, and pitch-bend arrays plus a `Clone`, and is null on `CustomInputState` for non-MIDI devices.

---

## Enumeration and teardown (Phase 1e)

`UpdateDevices` calls `UpdateMidiInputDevices` as Phase 1e, alongside the SDL, Raw Input, and Precision Touchpad phases. Enumeration is async. A background task refreshes the cached endpoint list (the WinRT device query is expensive and is kept off the poll loop), and the polling thread consumes the latest snapshot. For each endpoint it either keeps an existing `MidiInputDevice`, or creates one, opens it, and runs it through `FindOrCreateUserDevice` then `LoadFromExternalDevice` then `IsOnline = true`.

Two gates run before any open:

- **Loopback readiness.** A PadForge-shaped endpoint (`MidiEndpointJanitor.IsPadForgeEndpointId`) opens only while the owning `MidiVirtualController` in this process reports its device side ready (`MidiVirtualController.IsReadyEndpointInstance`). A PadForge endpoint with no ready owner is either mid-create or a corpse stranded by a failed service-side teardown, and opening a corpse re-animates it inside the service. It is never reopened. The endpoint janitor removes it instead.
- **Failed-open backoff.** An endpoint whose open failed is skipped for 60 s (`_midiOpenFailedAt`), so a sick service is not re-poked every sweep. The backoff entry is dropped when the endpoint vanishes, so a re-created endpoint starts fresh.

A vanished endpoint is marked offline, disposed, and has its mapped outputs neutralized. Step 3 keeps the last OutputState for an offline device, so a note or CC held at the moment of the unplug would otherwise stay stamped on the slot's combined output.

`CloseMidiInputsForEndpoint` closes any open loopback input connections to one PadForge MIDI endpoint, and the ordering is the contract: the loopback client connections must close before that endpoint's device-side teardown, because tearing down a virtual endpoint while this process still holds a client connection to it is the deterministic midisrv wedge (bench 2026-07-23). Callers demote the endpoint's registry claim first (`MidiVirtualController.MarkClosing`) so the scanner cannot reopen it in that window. Closing neutralizes the device's mapped outputs too, so held notes and CCs release.

`ShutdownMidiInputs` suppresses further enumeration, disposes every open device, and calls `MidiInputRuntime.Shutdown`. The ordering at the Windows MIDI Services uninstall path is load-bearing: `ShutdownMidiInputs` runs first, then the output controller shuts down, then the service is removed, because MIDI input enumeration loads the SDK runtime whenever the service is installed.

---

## Descriptor resolution and coercion

`MappingDisplayResolver.BuildInputChoices` short-circuits for a MIDI device and emits the full namespace directly through `AddMidiChoices`: 128 notes (named, for example note 60 is "C4"), each CC as an absolute fader plus an Up and a Down encoder entry, and pitch bend. There are no device objects and nothing to configure first.

`SourceCoercion` classifies any `"Midi "` descriptor as `SourceType.Midi` and `TryParseMidi` resolves the kind (note, CC, encoder up, encoder down, pitch bend) and index. Three reader branches consume `state.Midi`: `ReadAsBool` for button and POV targets (a CC past its per-source deadzone), `ReadAsBipolar` for axes (a CC as a centered slider), and `ReadAsUnipolar` for triggers. The per-source invert flag is applied on top.

---

## Distinct from the MIDI virtual output

`MidiVirtualController` is the unrelated output path. Its `Type` is `VirtualControllerType.Midi` (a separate enum, value 3, from `InputDeviceType.Midi` which is 27). It creates a Windows MIDI Services virtual device and sends Control Change and Note messages out. The input and output paths meet only at the availability check, at the uninstall teardown, and on the loopback path, where the input scanner opens an output endpoint's client-visible twin only while its owning controller reports ready.

---

## Related pages

- [MIDI Input](../features/midi-input.md): the user guide for this feature.
- [Input Pipeline](input-pipeline.md): where Phase 1e enumeration and the per-device read run.
- [Devices](../features/devices.md): the device card and the live note and CC preview.
- [Button and Axis Mappings](../features/mappings.md): how MIDI sources bind to outputs.
- [Driver Management](../features/driver-management.md): the Windows MIDI Services install.

---

*Last updated for PadForge 4.1.0.*
