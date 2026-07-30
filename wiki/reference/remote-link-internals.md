# Remote Link Internals

*How PadForge PCs share devices: UDP discovery, the X25519 and Ed25519 pairing handshake with a six-digit code, the sealed datagram transport, input streaming, and the reverse output relay.*

This is the developer-side companion to [Remote Link](../guides/remote-link.md) (the user guide) and issue #138.

---

## Layout

The engine logic lives in `PadForge.Engine/RemoteLink/` (namespace `PadForge.Engine.RemoteLink`). The App wires it up and provides the capture taps.

| Area | Files |
|---|---|
| Discovery | `LinkDiscovery.cs` |
| Transport and lifecycle | `LinkServer.cs`, `LinkConnection.cs`, `LinkSession.cs`, `TcpControlChannel.cs`, `AntiReplayWindow.cs` |
| Crypto | `LinkHandshake.cs`, `PeerCrypto.cs`, `PeerIdentity.cs`, `IdentityProtector.cs` |
| Trust | `PeerTrustStore.cs`, `PeerTrust.cs` |
| Devices and codecs | `RemotePeerDevice.cs`, `CustomInputStateCodec.cs`, `OutputEffectCodec.cs` |
| App relay and wiring | `PadForge.App/Common/Input/RemoteLinkOutputRouter.cs`, `PadForge.App/Services/InputService.cs`, `SettingsService.cs` |
| Capture taps | `InputManager.Step2/Step4b/Step5/Step1.*.cs`, `SonyEffectWriter.cs`, `AudioPassthroughService.cs` |

The transport is abstracted behind `ILinkControlChannel`, so an in-memory test harness and the TCP socket share one path.

---

## Discovery

`LinkDiscovery` is a UDP broadcast beacon, not mDNS. It binds `IPAddress.Any:27501`, announces every two seconds to `IPAddress.Broadcast:27501`, and prunes a peer after ten seconds of silence. Because it broadcasts, it is same-subnet only. The beacon carries a four-byte magic, a version, the link port, the sender's identity fingerprint (hex), and the self-asserted machine name. A forged beacon can only put a name in the "Nearby PCs" list. The crypto gate still controls admission. The receive loop filters out the PC's own fingerprint and raises `PeersChanged`.

---

## Server, connection, and the sealed transport

`LinkServer` runs a `TcpListener` for the pairing handshake and a UDP socket for data, both on the link port (default 27500). It caps pending handshakes, times them out after three minutes, sends keepalives, and reaps idle connections. A reconnecting peer replaces its prior connection.

It holds a `List<LinkPeerConnection>`, so one PC can be linked to many peers at once. The mesh is many-to-many: pairing is pairwise (one handshake and one six-digit code per pair), but `PushLocalFrame` fans a shared device's input out to every consuming peer, and `PushOutputEffect` and `PushAudio` address the reverse frame by the owning peer's fingerprint so each device's feedback routes back to the right owner. There is no two-PC cap.

`LinkConnection` runs the handshake (initiator or responder) and then owns a `LinkSession`. `LinkSession` seals every datagram: a 14-byte authenticated header (message type and epoch, slot, a 32-bit sequence, a microsecond timestamp) plus ChaCha20-Poly1305 ciphertext and a 16-byte tag. The sequence doubles as the nonce counter, and the two directions use disjoint salts so both peers share one key without a nonce collision. Receive is verify-then-window: check the tag, then run `AntiReplayWindow`, so a forged sequence never advances the replay state. The session hard-stops before the 32-bit sequence wraps and forces a rekey.

`LinkMessageType` values: `Input` (an absolute device-state frame, owner to consumer), `Keepalive`, `Output` (a tagged effect frame, consumer to owner), `Audio` (a speaker PCM block), and `DeviceList` (the owner's exposed-device set, resent on change and every two seconds for hot-plug sync). A legacy `Haptic` type is superseded by `Output` and unused. The initial device lists are also exchanged during the handshake under a separate control key. Each V1 device entry carries the stable slot, a stable id, the name, VID and PID, capability counts, a capability bitmask, and the input-device type. The capability bitmask packs eight flags into one byte: `HasRumble` (value 1), `HasRumbleTriggers` (2), `HasGyro` (4), `HasAccel` (8), `HasTouchpad` (16), `HasHaptic` (32) so a remote wheel or FFB stick's force-feedback pipeline runs, `Online` (64) so active/inactive propagates, and `HasAccelAux` (128) so an aux/left-side accelerometer (Nunchuk, left Joy-Con, #199) exposes. `HasAccelAux` (value 128) exhausts the caps byte. The next capability needs a wire-format extension, not another bit.

### Device-list metadata extension

After the V1 records, `EncodeDeviceList` appends a metadata extension marked by a magic byte (`0xE2`), one section per V1 record in the same order. It carries the serial number, the touchpad shape (`NumTouchpads` plus a finger count per pad), and the forwarded `DeviceObjects` (the owner's named inputs: `Name`, `InputIndex`, `Offset`, an `ObjectType` flags word, and the `ObjectTypeGuid`). So serial, touchpad shape, and named inputs now cross the link, and a remote device lists on the Devices page and in the mapping picker identically to a local one.

The extension uses the same appended-tail compatibility as the input codec. An old decoder reads its `count` V1 records and never looks at the tail. A new decoder facing an old sender finds no magic byte. A malformed extension tail falls back to the V1 result: any parse failure resets every extension-carried field on every record, so a mid-record throw leaves no half-applied garbage, and the consumer synthesizes generic names as before.

Objects are forwarded only for device types whose names the consumer cannot synthesize locally: Consumer Control and NFC. The push travels as one UDP datagram into a 4 KB receive buffer on old peers, so the encoder budgets the payload (a 3800-byte floor). Once it nears that floor the remaining devices get empty object sections and the consumer falls back to synthesized names for them, rather than the whole list becoming undeliverable.

A second tail follows the `0xE2` extension, marked by its own magic byte (`DeviceListExtV2Magic`, `0xE3`): one clamped byte per device carrying `RawButtonCount`. It has its own magic and its own decode `try`/`catch`, and it decodes only once the V1 tail parsed cleanly. So an old peer that stops after the `0xE2` tail ignores it, and a malformed v2 tail costs only the button counts, never the already-decoded V1 metadata. The count lets the consumer offer the device's native buttons past the 22 standardized gamepad slots in its mapping picker. `RemotePeerDeviceInfo.RawButtonCount` and `RemotePeerDevice.SupportedButtonIndices` carry it through the pipeline.

---

## Pairing handshake

`LinkHandshake` is an authenticated key exchange over TCP, in four messages: commit, reveal from the responder, reveal from the initiator, confirm.

- **Ephemeral X25519 per side** gives forward secrecy.
- **Commit before reveal.** The commit is `SHA256` over the commit label, the ephemeral public key, a nonce, the capabilities, and the static public key. Binding the static key into the commit closes the one SAS input a relay attacker could otherwise grind. The responder recomputes and checks it with a constant-time compare before trusting the reveal.
- **Ed25519 static-key signatures over the transcript hash.** The transcript hash is `SHA256` over the three handshake messages, each field length-prefixed so boundaries are unambiguous. Both sides sign it and verify the other. Capabilities and version are folded into the signed transcript, so a downgrade fails at the signature check.
- **Six-digit SAS.** A hash of the transcript reduced modulo one million, formatted to six digits. It is compared out of band on first pairing only.
- **Session key** via HKDF over the shared secret, salted by the transcript hash. The connection then derives separate control and data keys.
- **Fail-closed.** Every malformed, out-of-order, or unauthenticated input throws, and no device is created on a failed handshake.

Admission runs `PeerTrustStore.Decide(peerStaticKey)`. First contact prompts the user (the `RemoteLinkPairDialog`). A known key reconnects with no prompt, and the signature still proves possession.

---

## Trust and identity

`PeerTrust` persists per peer as XML attributes: the pinned Ed25519 public key (an identity, not a secret), the name, the self-asserted host name, the pairing time, a reconnect-enabled flag (default true), and the gamepad-only flag. The fingerprint is the SHA-256 of the public key.

`PeerTrustStore` is the in-memory authority. `Decide` returns first-contact (unknown, never auto-trusted), known-auto-select, or known-manual. Lookups use a constant-time compare. An unknown key defaults to gamepad-only restricted, which is the fail-safe.

`IdentityProtector` stores this PC's own identity in one of three modes. **Secure** (the default) wraps the private key with DPAPI at machine scope, so any Windows user on the PC can use it but it does not move to another machine. **Portable, password protected** wraps it with PBKDF2-SHA256 (600,000 iterations) and AES-256-GCM. **Portable, open** stores it in the clear. The blob is self-describing, with a version and mode header. `LoadOrMint` mints only when the store is empty or corrupt and never overwrites a locked identity, so a password prompt or a wrong-machine state is surfaced to the caller rather than clobbered. A mode switch re-wraps the same key, so the fingerprint and all pairings survive.

---

## Input streaming (owner to consumer)

On the owner, a stream timer running near 125 Hz calls `LinkServer.PushLocalFrame` per exposed device, which encodes the state through `CustomInputStateCodec` and seals an `Input` datagram. The codec is absolute: every frame is the full state through a present-block bitmask with neutral-omit, so packet loss self-heals and a centered idle pad is three bytes.

On the consumer, the device list yields a `RemotePeerDevice` per exposed device. The link server's `DeviceConnected` event calls `InputManager.RegisterPeerDevice`, which runs it through `FindOrCreateUserDevice` and `LoadFromExternalDevice`. A `RemotePeerDevice` is an `ISdlInputDevice`, so it flows through the normal six-step pipeline like any local source. Inbound `Input` datagrams decode into a back buffer that swaps under a lock, newest-wins by timestamp. After a three-second stale window the device reads as offline and releases any held inputs. The device identity is salted by the peer fingerprint, but not through the path. `DevicePath` uses an eight-character short form (`peer://{Short(fingerprint)}/{deviceId}`), which alone would collide across peers whose fingerprints share a first eight hex chars. The full fingerprint salts the collision-safe identity: `InstanceGuid` is an MD5 over `pflink-dev:{fingerprint}:{deviceId}` and `ProductGuid` an MD5 over `pflink-prod:{fingerprint}:{VID}:{PID}:{type}`. So two peers sharing the same controller model never alias through the non-peer-namespaced `ProductGuid` reconnect fallback.

### Present-block table

A 16-bit present-block bitmask (`Block`, a `[Flags]` enum in `CustomInputStateCodec`) leads the payload. A block appears only when its data is non-neutral, and the decoder resets to neutral first and applies only the blocks the frame carries. Fourteen blocks are defined:

| Bit | Block | Carries |
|---|---|---|
| 0 | `Axis` | Stick and trigger axes (non-neutral only) |
| 1 | `Sliders` | Slider axes |
| 2 | `Povs` | POV hats |
| 3 | `Buttons` | Button bitmask |
| 4 | `Gyro` | Gyro triple (capability-gated) |
| 5 | `Accel` | Accel triple (capability-gated) |
| 6 | `Battery` | Percent byte plus the charging flag byte |
| 7 | `Touchpad` | Per-pad finger contacts |
| 8 | `Midi` | Notes, CC, pitch bend |
| 9 | `Ir` | Wii IR pointer X/Y (#146) |
| 10 | `JoyConIr` | Joy-Con NIR intensity (#151) |
| 11 | `JoyCon2Mouse` | Joy-Con 2 mouse deltas DX/DY (#154) |
| 12 | `AccelAux` | Aux/left-side accel triple (Nunchuk, left Joy-Con) (#199) |
| 13 | `MouseRaw` | Unclamped Raw Input mouse counts DX/DY (#200) |

`Battery` sends when the percent is known or the pad reports charging, and always carries both the percent byte and the charging flag, so a "charging, percent unknown" pad keeps its flag on the wire. Battery crosses the link.

Bits 9-13 are the post-3.5.0 additions, appended strictly after every older block. That ordering is what keeps mixed-version peers compatible without a `Version` bump: an old decoder reads its known blocks in order, never reaches the new bits, and its final `o <= payload.Length` check tolerates the trailing bytes. A new decoder facing an old sender simply finds those bits clear.

---

## Reverse output relay (consumer game to owner hardware)

The consumer runs the full config-applied output pipeline for a `peer://` device. The final hardware write fails (the handle is zero), so each write chokepoint hands its config-baked payload to `RemoteLinkOutputRouter` instead:

- `ShipSonyEffect` (in `SonyEffectWriter`) strips the report id and encodes the DualSense or DualShock 4 effect body.
- `ShipVibration` (Step 2) encodes the full `Vibration` (motors, impulse triggers, directional and condition force).
- `ShipWheel` (Step 2) encodes a semantic wheel frame (force, condition, periodic, range, auto-center, RPM-LED mask).
- `ShipHapticTone` encodes the HD haptic tone (#147): one (dominant frequency Hz, amplitude 0..1) pair per rumble tick, slot volume already applied.
- `ShipPlayerIndex` encodes the consumer's winning 1-based player number (the smallest displayed number across the slots the pad feeds) for non-Sony shared pads (Nintendo, BT DS3, #191). A DualSense or DualShock 4 peer carries its player LED in the Sony effect body, so it never ships this kind.
- `ShipGuideLed` encodes the consumer's configured Guide/Home LED brightness (0-100 percent) for a shared Xbox GIP pad, 2015 Steam Controller (#209), or Switch HOME-LED pad (Pro Controller, right Joy-Con, pair, charging grip, #226). It has `ShipPlayerIndex`'s shape, dedups per path, and addresses one peer device by its path.
- `ShipAudio` (in `AudioPassthroughService`) ships the speaker PCM block on the `Audio` datagram.

`OutputEffectCodec.Kind` has six values: `SonyEffect = 1`, `Vibration = 2`, `Wheel = 3`, `HapticTone = 4`, `PlayerIndex = 5`, `GuideLed = 6`.

The router maps the `peer://` path to a target (owner fingerprint and link slot, fixed at connect), dedups exact repeats per channel, and sends through `PushOutputEffect` or `PushAudio`.

On the owner, the `OutputReceived` handler `OnRemoteOutputReceived` decodes the frame, resolves the link slot to the physical source device, takes the sole-writer lease (except for a `PlayerIndex` or `GuideLed` frame, see below), and applies by kind: a Sony effect through `SDL_SendGamepadEffect`, a vibration through `ForceFeedbackState.SetDeviceForces`, a wheel frame through `ApplyRemoteWheel` (which re-encodes with the owner's own vendor writers, see [Wheel Force Feedback Internals](wheel-ffb-internals.md)), a haptic tone (`HapticToneHz`/`HapticToneAmp`) re-encoded by the owner's own per-family writer (Joy-Con HD Rumble, Steam 0x8f, Triton 0x83, Deck), a player index through `SetPlayerIndex` (0-based) for a Nintendo pad (VID `0x057E`) or `Ds3DirectService.TrySetPlayerNumber` for a Bluetooth DS3 (`0x054C`/`0x0268`), a Guide/Home LED brightness through `XboxGipGuideLedWriter.TrySetBrightness` for an Xbox GIP pad, `SteamHomeLedSetter.TrySet` for a 2015 Steam Controller, or `SwitchHomeLedSetter.TrySet` for a Switch HOME-LED pad (the same writers and gate order as the local apply path), and audio through `AudioPassthroughService.FeedRemoteAudio` (see [Controller Audio Internals](controller-audio-internals.md)). The vibration apply has two special cases. A Fanatec pedal re-routes to its raw-HID pedal-rumble writer. An Xbox One+ impulse-trigger pad, gated by `XboxControllerIdentity.IsImpulseTriggerDevice`, records through `TryRecordXboxImpulseSnapshot` and writes all four channels (large and small plus LT and RT) via `XboxImpulseHidWriter.Write`, with SDL rumble suppressed so the impulse triggers fire. The owner synthesizes nothing here: for the wheel and the haptic tone it is a transport transcoder that re-frames the semantic payload with the writer that owns the real hardware.

**Sole-writer guard.** A device can be both shared out and mapped locally, and output cannot merge. An inbound relay frame stamps the local path with a three-second lease, and the owner's local chokepoints skip their own writes while the lease is fresh. A device that is only lent out (not also mapped locally) has no local writer, so there is no contention. A `PlayerIndex` or `GuideLed` frame is exempt from the lease. Both are cosmetic LED updates, not effect claims, so neither blanks a locally-mapped device's rumble or lightbar for the lease window.

---

## Gamepad-only enforcement

`InputManager.SetDeviceRestricted` populates the restricted-device set from each peer's gamepad-only flag, set before the device goes online. `IsSlotRestricted(slot)` is true when any online restricted device maps to that slot, and it early-outs when no peer is restricted. Three chokepoints honor it:

- The KBM virtual controller (Step 5) submits a neutral state for a restricted slot, releasing anything held.
- Macros (Step 4b) are restricted when the slot is restricted or a restricted device is a macro trigger.
- The five Win32 `SendInput` emitters (key, text, mouse move, mouse button, scroll, in Step 4b) early-return while the macro slot is restricted.

So a gamepad-only peer can drive gamepad slots but never reach the keyboard, mouse, or scroll.

---

## Remote devices and disconnect

A `peer://` device relays its owner's real VID and PID, so a linked pad can look like a Bluetooth or Switch 2 controller that the disconnect action would otherwise target. But the disconnecting machine has no radio link to it, so the action could only no-op. `BluetoothLinkHelper.IsDisconnectTarget(devicePath, vendorId, productId)` returns false first for any `peer://` path, before the Switch 2 and Bluetooth-path checks. The macro evaluator uses that gate, so a linked remote device is never a disconnect target (issue #162).

---

## Settings and auto-reconnect

`AppSettingsData` persists `RemoteLinkIdentityPrivate` and `RemoteLinkIdentityPublic`, `RemoteLinkIdentityProtection` (default Secure), `RemoteLinkPeers` (the `PeerTrust` array), `EnableRemoteLink`, `RemoteLinkAutoReconnect` (default true), and `RemoteLinkPort` (default 27500, clamped to 1024-65535). These load into a runtime record on `SettingsService` and into the Dashboard view model.

The auto-reconnect dial runs when a peer is discovered. It requires a trusted entry with reconnect enabled, skips a peer already connected, applies a lower-fingerprint-dials rule so only one side initiates, and throttles per peer with a five-second cooldown. A passing peer triggers a connect with the PC's exposed devices.

---

## Related pages

- [Remote Link](../guides/remote-link.md): the user guide for this feature.
- [Input Pipeline](input-pipeline.md): a `RemotePeerDevice` is an `ISdlInputDevice` and runs through the normal six steps.
- [Wheel Force Feedback Internals](wheel-ffb-internals.md): the owner re-encodes a relayed wheel frame with the vendor writers.
- [Controller Audio Internals](controller-audio-internals.md): the relayed speaker audio path.
- [Services Layer](services-layer.md): `InputService` wiring and the auto-reconnect dial.
- [Settings and Serialization](settings-and-serialization.md): the persisted Remote Link fields.

---

*Last updated for PadForge 4.1.0*
