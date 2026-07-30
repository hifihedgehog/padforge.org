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

`Open` pulls the shared WM2 session, creates an endpoint connection, subscribes to `MessageReceived`, and opens it. `Dispose` unsubscribes and disconnects. The WinRT callback thread writes state under a lock and the polling thread reads a clone, the same discipline the web-controller device uses.

---

## MidiInputRuntime: the shared WM2 session

`MidiInputRuntime` is a static class over `Microsoft.Windows.Devices.Midi2` (Windows MIDI Services). Its `Session` property lazily creates one `MidiSession`, but only after `MidiVirtualController.IsAvailable()` returns true. It never initializes the SDK itself. It rides the runtime the output side brings up, and returns null when Windows MIDI Services is absent.

`EnumerateEndpoints` calls `MidiEndpointDeviceInformation.FindAll` and keeps only the normal message endpoints and the virtual-device responders, skipping the diagnostics endpoints and the in-box synth. Keeping the virtual-device responders is deliberate. It is what lets PadForge's own MIDI virtual-controller endpoints appear as inputs, which is the no-hardware loopback test path. `Shutdown` disposes the session and must run before `MidiVirtualController.Shutdown` on app exit.

---

## Message parsing

`OnMessageReceived` reads the first UMP word and the message-type nibble. The whole body is wrapped in try-catch so a malformed packet cannot take down the WinRT callback thread. It handles MIDI 1.0 (32-bit UMP, message type 0x2) and MIDI 2.0 (64-bit UMP, message type 0x4):

| Opcode | Becomes | State write |
|---|---|---|
| Note On (0x9) | A button, on while held | 1.0: `SetNote(note, velocity != 0)`, 2.0: `SetNote(note, true)` |
| Note Off (0x8) | Button release | `SetNote(note, false)` |
| Control Change (0xB) | An absolute 0-127 value | `SetCc(cc, value)` |
| Pitch Bend (0xE) | A 14-bit (or 16-bit in MIDI 2.0) centered axis | `SetPitchBend(scaled)` |

On the MIDI 1.0 path velocity decides on versus off (a Note On with velocity 0 is a Note Off), and velocity is never stored as a value. The MIDI 2.0 path is different. A Note On there writes `SetNote(note, true)` regardless of velocity, because a MIDI 2.0 Note On with velocity 0 is a valid note-on, so on the 2.0 branch only a Note Off (0x8) releases the note. Reads are channel-merged (omni). The channel nibble is never inspected, so a note or CC means the same thing on any channel. Two channel-mode CCs get extra handling in the CC path: All Sound Off (CC 120) and All Notes Off (CC 123) clear every note lane after their value is written, so a controller that ends a phrase with one of those instead of per-note Note Off does not leave mapped note-buttons latched on. Channel pressure, polyphonic aftertouch, and program change have no case and are dropped.

A Control Change also drives the relative-encoder reader. Only the binary-offset style is decoded (center 0x40, 0x41 is one step up, 0x3F is one step down). A small positive delta queues an up pulse on lane `2*cc` and a small negative delta queues a down pulse on `2*cc+1`. Values outside the band read as an absolute fader and never pulse. The two's-complement and signed-bit encoder styles read as absolute jumps. The pulse machine presses each detent for 24 ms then gaps 12 ms, caps the backlog at four pending pulses (so a fast spin drops detents rather than lagging), and tops out near 28 detents per second. `MidiInputState` holds the note, CC, encoder up and down, and pitch-bend arrays plus a `Clone`, and is null on `CustomInputState` for non-MIDI devices.

---

## Enumeration and teardown (Phase 1e)

`UpdateDevices` calls `UpdateMidiInputDevices` as Phase 1e, alongside the SDL, Raw Input, and Precision Touchpad phases. Enumeration is async. A background task refreshes the cached endpoint list (the WinRT device query is expensive and is kept off the poll loop), and the polling thread consumes the latest snapshot. For each endpoint it either keeps an existing `MidiInputDevice`, or creates one, opens it, and runs it through `FindOrCreateUserDevice` then `LoadFromExternalDevice` then `IsOnline = true`. A vanished endpoint is marked offline and disposed.

`ShutdownMidiInputs` suppresses further enumeration, disposes every open device, and calls `MidiInputRuntime.Shutdown`. The ordering at the Windows MIDI Services uninstall path is load-bearing: `ShutdownMidiInputs` runs first, then the output controller shuts down, then the service is removed, because MIDI input enumeration loads the SDK runtime whenever the service is installed.

---

## Descriptor resolution and coercion

`MappingDisplayResolver.BuildInputChoices` short-circuits for a MIDI device and emits the full namespace directly through `AddMidiChoices`: 128 notes (named, for example note 60 is "C4"), each CC as an absolute fader plus an Up and a Down encoder entry, and pitch bend. There are no device objects and nothing to configure first.

`SourceCoercion` classifies any `"Midi "` descriptor as `SourceType.Midi` and `TryParseMidi` resolves the kind (note, CC, encoder up, encoder down, pitch bend) and index. Three reader branches consume `state.Midi`: `ReadAsBool` for button and POV targets (a CC past its per-source deadzone), `ReadAsBipolar` for axes (a CC as a centered slider), and `ReadAsUnipolar` for triggers. The per-source invert flag is applied on top.

---

## Distinct from the MIDI virtual output

`MidiVirtualController` is the unrelated output path. Its `Type` is `VirtualControllerType.Midi` (a separate enum, value 3, from `InputDeviceType.Midi` which is 27). It creates a Windows MIDI Services virtual device and sends Control Change and Note messages out. The input and output paths meet only at the availability check, at the uninstall teardown, and in the loopback case where one of the output endpoints is what an input slot maps from.

---

## Related pages

- [MIDI Input](../features/midi-input.md): the user guide for this feature.
- [Input Pipeline](input-pipeline.md): where Phase 1e enumeration and the per-device read run.
- [Devices](../features/devices.md): the device card and the live note and CC preview.
- [Button and Axis Mappings](../features/mappings.md): how MIDI sources bind to outputs.
- [Driver Management](../features/driver-management.md): the Windows MIDI Services install.

---

*Last updated for PadForge 4.0.0*
