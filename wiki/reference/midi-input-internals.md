# MIDI Input Internals

*How a MIDI endpoint becomes a mappable input device: the `MidiInputDevice` source, the shared input session, the UMP parser, and the descriptor and coercion path.*

This is the developer-side companion to [MIDI Input](../features/midi-input.md) (the user guide) and issue #128.

---

## Files

| File | Role |
|---|---|
| `PadForge.App/Common/Input/MidiInputDevice.cs` | `MidiInputDevice` (the device) and `MidiInputRuntime` (the shared session and endpoint enumeration). |
| `PadForge.App/Common/Input/MidiBackend.cs`, `MidiBackendInBox.cs`, `MidiBackendAppSdk.cs`, `MidiBackendLegacy.cs` | `IMidiBackend` over the two Windows MIDI Services APIs and the legacy WinMM API. The input side uses its session, connection and enumeration members. |
| `PadForge.Engine/Common/MidiInputState.cs` | The `MidiInputState` sub-state on `CustomInputState`. |
| `PadForge.App/Common/Input/InputManager.Step1.UpdateDevices.cs` | Phase 1e enumeration and registration, `ShutdownMidiInputs` and `ResumeMidiInputs`. |
| `PadForge.App/Common/MappingDisplayResolver.cs` | The MIDI picker block (`AddMidiChoices`). |
| `PadForge.Engine/Common/Mapping/SourceCoercion.cs` | `SourceType.Midi`, the classify and parse helpers, and the three reader branches. |
| `PadForge.Engine/Common/InputTypes.cs` | `InputDeviceType.Midi = 27`. |
| `PadForge.App/Common/Input/MidiVirtualController.cs` | The unrelated MIDI **output** virtual controller. |

---

## MidiInputDevice: an endpoint as an input device

`MidiInputDevice` implements `ISdlInputDevice`, the same contract the SDL gamepads, keyboards, mice, and web and peer devices implement, so the rest of the [Input Pipeline](input-pipeline.md) treats it uniformly. One instance exists per connected MIDI endpoint. `GetInputDeviceType()` returns `InputDeviceType.Midi` (27), which flows into `UserDevice.CapType` and is the field the picker keys on.

It exposes zero gamepad surface: no axes, buttons, hats, or device objects. The entire mappable surface lives in `CustomInputState.Midi`, the same pattern as the touchpad sub-state. Its identity is synthetic. The VID and PID spell "MI" and "MD", the device path is `midi://{endpointId}`, and the instance and product GUIDs are MD5 hashes of the endpoint ID and name. It has no rumble, haptic, or motion.

`Open` pulls the shared session, asks it for a connection with `OnUmp` as the message callback (the backend subscribes to `MessageReceived` before the open), and opens it. Every one of those calls is a WinRT RPC into the MIDI service, and `Open` runs on the polling thread, so the whole body runs on a worker bounded by a 3 s timeout (`OpenTimeoutMs`). A hung open is orphaned and torn down later on its own thread. Under the legacy API the connection is a WinMM port: `midiInOpen` with a function callback, then `midiInStart`, and a start that fails resets and closes the port, as PortMidi does. On the new MIDI stack those WinMM calls go through the MIDI service too, so the same bound applies. `Dispose` detaches the callback and hands the disconnect to `MidiInputRuntime.Disconnect`, which is fire-and-forget on a worker for the same reason: a hung midisrv wedged the whole engine through exactly this lane (live stack, 2026-07-23), and nothing waits on the service from the polling thread anymore. The WinRT callback thread writes state under a lock, and the polling thread reads a pooled copy: `GetCurrentState` fills one of two reused snapshot buffers (`PooledInputStatePair`) via `CopyInto` rather than allocating a fresh clone per poll.

---

## MidiInputRuntime: the shared WM2 session

`MidiInputRuntime` is a static class over the `IMidiBackend` the output side starts (`MidiVirtualController.Backend`): the in-box `Windows.Devices.Midi2`, the `Microsoft.Windows.Devices.Midi2` App SDK runtime, or the legacy WinMM API. Its `Session` property lazily creates one input session (`IMidiBackend.CreateInputSession`), but only after `MidiVirtualController.IsAvailable()` returns true, and the create itself runs on a worker bounded by the same 3 s timeout the device open uses, so a wedged service returns null instead of stalling the caller. It never starts an API itself, and returns null when no MIDI API is available. `Disconnect` runs on a worker and is skipped while no session is open: the connection closed with its session (`MidiSession::Close` in `microsoft/MIDI` closes every connection the session holds), and the App SDK runtime may be released by then. `ResetSession` drops the session after its backend was torn down: it takes the session out under the lock and disposes it on a worker, so the polling thread never waits on a dead service, and the next asker gets a session from the current backend. The legacy session tracks its open ports and closes them when it is disposed, the way a Windows MIDI Services session's connections end with it.

`EnumerateEndpoints` asks the backend (`EnumerateNormalEndpoints`), which calls `MidiEndpointDeviceInformation.FindAll` (both APIs default it to all standard endpoints, sorted by name) and keeps only the normal message endpoints (`MidiEndpointDevicePurpose.NormalMessageEndpoint`), skipping the diagnostic endpoints, the in-box synth, and the virtual-device responder twins. PadForge's own MIDI virtual-controller endpoints still appear as inputs (the no-hardware loopback path) because the service publishes a client-visible twin of every virtual device as a normal endpoint. The device-side responder twin is for the hosting application only, and enumerating it is how the input lane used to poke stranded responder corpses every sweep (the MIDI VC lifecycle-wedge fix). `Shutdown` disposes the session and must run before `MidiVirtualController.Shutdown` on app exit.

Under the legacy API, `EnumerateNormalEndpoints` lists the WinMM input ports. WinMM numbers a port by an index that shifts when a device comes or goes, so each port is keyed by its name: the endpoint id is `winmm:` plus the name, and a second port with the same name is "Name (2)", a third "Name (3)", in index order. A port Windows cannot describe is left out. Each open resolves the name to the port's current index.

---

## Message parsing

Each Windows MIDI Services backend's `MessageReceived` handler hands `OnUmp` the message's first UMP word, and for a 64-bit message (type 0x4) its second word from the `MidiMessage64` packet. The legacy backend's callback takes each `MIM_DATA` short message and hands `OnUmp` the same MIDI 1.0 word (`MidiBackendLegacy.ShortMessageToUmp`). It drops system messages and a data byte where the status byte belongs, as PortMidi and RtMidi do. Handler and parser are both wrapped in try-catch so a malformed packet cannot take down the WinRT callback thread. `OnUmp` reads the message-type nibble and handles MIDI 1.0 (32-bit UMP, message type 0x2) and MIDI 2.0 (64-bit UMP, message type 0x4):

| Opcode | Becomes | State write |
|---|---|---|
| Note On (0x9) | A button, on while held | 1.0: `SetNote(note, velocity != 0)`, 2.0: `SetNote(note, true)` |
| Note Off (0x8) | Button release | `SetNote(note, false)` |
| Control Change (0xB) | An absolute 0-127 value | `SetCc(cc, value)` |
| Pitch Bend (0xE) | A 14-bit (MIDI 1.0) or 32-bit (MIDI 2.0) centered axis, both stored as 0-65535 | `SetPitchBend(scaled)` |

On the MIDI 1.0 path velocity decides on versus off (a Note On with velocity 0 is a Note Off), and velocity is never stored as a value. The MIDI 2.0 path is different. A Note On there writes `SetNote(note, true)` regardless of velocity, because a MIDI 2.0 Note On with velocity 0 is a valid note-on, so on the 2.0 branch a note releases only on a Note Off (0x8) or on one of the channel-mode CCs below. Reads are channel-merged (omni). The channel nibble is never inspected, so a note or CC means the same thing on any channel. Channel pressure, polyphonic aftertouch, and program change have no case and are dropped.

The channel-mode CCs get extra handling in the CC path, after their value is written:

- **All Sound Off (CC 120) and All Notes Off (CC 123)** clear every note lane, so a controller that ends a phrase with one of these instead of per-note Note Off does not leave mapped note-buttons latched on.
- **Omni Off/On and Mono/Poly (CCs 124–127)** clear the note lanes too, since each carries All Notes Off semantics per MIDI 1.0. CC 122 (Local Control) clears nothing.
- **Reset All Controllers (CC 121)** applies the RP-015 reset to the lanes this state models: pitch bend recenters, the mod wheel (CC 1) and pedals (CCs 64–67) drop to 0, expression (CC 11) returns to 127, and the RPN and NRPN selectors (CCs 98–101) return to null. Each reset lane's encoder pulse machine is cleared in both directions, so queued detent pulses stop with the reset. Bank, volume, pan, and sound lanes stay put, per RP-015. Without this, a keyboard panic (121 plus 123) released mapped notes but left a mapped Pitch Bend axis frozen off-center.

A Control Change also drives the relative-encoder reader. Only the binary-offset style is decoded (`RelativeCenter` 0x40, 0x41 is one step up, 0x3F is one step down). A delta within `RelativeMax` (16) of center queues that many up pulses on lane `2*cc`, or down pulses on `2*cc+1`. Values outside that band read as an absolute fader and never pulse. Two's-complement encoders (0x01 up, 0x7F down) read as absolute jumps. A signed-bit encoder is misread: values with the sign bit set (0x41 and up) fall inside the band and queue pulses on the up lane whatever their direction, and values without it (0x01 and up) read as an absolute fader. The pulse machine presses each detent for 24 ms then gaps 12 ms, caps the backlog at four pending pulses (so a fast spin drops detents rather than lagging), and tops out near 28 detents per second. `MidiInputState` holds the note, CC, and encoder up and down arrays plus a single pitch-bend value, with a `Clone`, and is null on `CustomInputState` for non-MIDI devices.

---

## Enumeration and teardown (Phase 1e)

`UpdateDevices` calls `UpdateMidiInputDevices` as Phase 1e, alongside the SDL, Raw Input, and Precision Touchpad phases. Enumeration is async. A background task refreshes the cached endpoint list (the WinRT device query is expensive and is kept off the poll loop), and the polling thread consumes the latest snapshot. For each endpoint it either keeps an existing `MidiInputDevice`, or creates one, opens it, and runs it through `FindOrCreateUserDevice` then `LoadFromExternalDevice` then `IsOnline = true`.

Each sweep first compares `MidiVirtualController.Generation` with the generation its inputs belong to (`_midiInputGeneration`). A backend torn down since then, by a runtime install or a MIDI service restart PadForge performed, left the inputs' connections and the shared session talking to nothing, and an endpoint that came back under the same id was never reopened. `DropMidiInputsForNewBackend` marks every input's device offline, neutralizes its mapped outputs, disposes it, clears the failed-open backoff and calls `MidiInputRuntime.ResetSession`, so the sweep opens everything again on the current backend. It is `ShutdownMidiInputs` without the suppression, and it waits on nothing.

Two gates run before any open:

- **Loopback readiness.** A PadForge-shaped endpoint (`MidiEndpointJanitor.IsPadForgeEndpointId`) opens only while the owning `MidiVirtualController` in this process reports its device side ready (`MidiVirtualController.IsReadyEndpointInstance`). A PadForge endpoint with no ready owner is either mid-create or a corpse stranded by a failed service-side teardown, and opening a corpse re-animates it inside the service. It is never reopened. The endpoint janitor removes it instead.
- **Failed-open backoff.** An endpoint whose open failed is skipped for 60 s (`_midiOpenFailedAt`), so a sick service is not re-poked every sweep. The backoff entry is dropped when the endpoint vanishes, so a re-created endpoint starts fresh.

Under the legacy API the sweep lists every input port but opens only the ports a slot has assigned (`IsMidiInputAssigned`, through the identity `MidiInputDevice.InstanceGuidFor` gives an endpoint before its device exists). On the classic MIDI stack, Windows before 24H2 and Legacy API mode, a port serves one program at a time, so opening every port would lock the user's other MIDI programs out of all of them. Each sweep runs `SyncAssignedMidiInput` on the listed ports: a newly assigned port opens, and a port no slot has anymore closes through `MidiInputDevice.Close`. That keeps the device listed and returns its state to rest, so a note held at the close is not still held at the next open. A failed open backs off for 60 s like a first open.

A vanished endpoint is marked offline, disposed, and has its mapped outputs neutralized. Step 3 keeps the last OutputState for an offline device, so a note or CC held at the moment of the unplug would otherwise stay stamped on the slot's combined output.

`CloseMidiInputsForEndpoint` closes any open loopback input connections to one PadForge MIDI endpoint, and the ordering is the contract: the loopback client connections must close before that endpoint's device-side teardown, because tearing down a virtual endpoint while this process still holds a client connection to it is the deterministic midisrv wedge (bench 2026-07-23). Callers demote the endpoint's registry claim first (`MidiVirtualController.MarkClosing`) so the scanner cannot reopen it in that window. Closing neutralizes the device's mapped outputs too, so held notes and CCs release.

`ShutdownMidiInputs` suppresses further enumeration, disposes every open device, and calls `MidiInputRuntime.Shutdown`. The ordering at the App SDK runtime's uninstall path is load-bearing: `ShutdownMidiInputs` runs first, then `MidiVirtualController.SuppressForUninstall` latches the runtime off and disposes its initializer while the service still exists, then the runtime is removed, because MIDI input enumeration loads the runtime whenever it is the API in use. Neither runs while the in-box API or the legacy API is in use. `ResumeMidiInputs` lifts the suppression once the uninstaller exits, and the next sweep enumerates through whichever API the next probe picks. After the runtime installs, `InputService.SwitchMidiApi` runs `ShutdownMidiInputs`, `MidiVirtualController.ResetAvailability` and `ResumeMidiInputs`, so input reopens through the runtime.

---

## Descriptor resolution and coercion

`MappingDisplayResolver.BuildInputChoices` short-circuits for a MIDI device and emits the full namespace directly through `AddMidiChoices`: 128 notes (named, for example note 60 is "C4"), each CC as an absolute fader plus an Up and a Down encoder entry, and pitch bend. There are no device objects and nothing to configure first.

`SourceCoercion` classifies any `"Midi "` descriptor as `SourceType.Midi` and `TryParseMidi` resolves the kind (note, CC, encoder up, encoder down, pitch bend) and index. Three reader branches consume `state.Midi`: `ReadAsBool` for button and POV targets (a CC past its per-source deadzone), `ReadAsBipolar` for axes (a CC as a centered slider), and `ReadAsUnipolar` for triggers. The per-source invert flag is applied on top.

`ReadHardwareBoolDescriptor` reads MIDI as on/off for the Up and Down keys of an Incremental or Ramped source and the Invert on Hold mirror (`ReadMidiBool`): a note held, an encoder detent's 24 ms pulse, or a CC at `MidiCcOnValue` (64) and above, the value where MIDI's on/off controllers turn on and where the Button row's default threshold lands. Pitch bend reads false there. `IsMidiKeyDescriptor` names the same families for the Up and Down pickers and for `MacroItem.TryBuildTriggerEntry`, which turns them into descriptor trigger entries. The recorder takes a note, a detent or a CC for an Up, Down or modifier field, and never pitch bend.

---

## Distinct from the MIDI virtual output

`MidiVirtualController` is the unrelated output path. Its `Type` is `VirtualControllerType.Midi` (a separate enum, value 3, from `InputDeviceType.Midi` which is 27). It creates a Windows MIDI Services virtual device, or under the legacy API opens the output port the slot picked, and sends Control Change and Note messages out. The input and output paths meet only at the availability check, at the uninstall teardown, and on the loopback path, where the input scanner opens an output endpoint's client-visible twin only while its owning controller reports ready.

---

## Related pages

- [MIDI Input](../features/midi-input.md): the user guide for this feature.
- [Input Pipeline](input-pipeline.md): where Phase 1e enumeration and the per-device read run.
- [Devices](../features/devices.md): the device card and the live note and CC preview.
- [Button and Axis Mappings](../features/mappings.md): how MIDI sources bind to outputs.
- [Driver Management](../features/driver-management.md#windows-midi-services): where Windows MIDI Services comes from.

---

*Last updated for PadForge 5.0.0.*
