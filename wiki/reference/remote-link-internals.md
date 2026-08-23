# Remote Link Internals

*How PadForge PCs share devices: UDP discovery, the X25519 and Ed25519 pairing handshake with a six-digit code, the sealed datagram transport, input streaming, the reverse output relay, and the internet lane that reaches a peer with no VPN and no port forward.*

This is the developer-side companion to [Remote Link](../guides/remote-link.md) (the user guide), issue #138, and issue #294.

---

## Layout

The engine logic lives in `PadForge.Engine/RemoteLink/` (namespace `PadForge.Engine.RemoteLink`). The App wires it up and provides the capture taps.

| Area | Files |
|---|---|
| Discovery | `LinkDiscovery.cs` |
| Transport and lifecycle | `LinkServer.cs`, `LinkConnection.cs`, `LinkSession.cs`, `TcpControlChannel.cs`, `UdpControlChannel.cs`, `AntiReplayWindow.cs` |
| Internet lane (#294) | `LinkCode.cs`, `StunClient.cs`, `NatProfile.cs`, `PortPredictor.cs`, `HolePuncher.cs`, `PunchedConnection.cs`, `RendezvousProtocol.cs`, `IrohRelayClient.cs`, `Dht/` |
| Crypto | `LinkHandshake.cs`, `PeerCrypto.cs`, `PeerIdentity.cs`, `IdentityProtector.cs` |
| Trust | `PeerTrustStore.cs`, `PeerTrust.cs` |
| Devices and codecs | `RemotePeerDevice.cs`, `CustomInputStateCodec.cs`, `OutputEffectCodec.cs` |
| App relay and wiring | `PadForge.App/Common/Input/RemoteLinkOutputRouter.cs`, `PadForge.App/Services/InputService.cs`, `SettingsService.cs` |
| Capture taps | `InputManager.Step2/Step4b/Step5/Step1.*.cs`, `PlayStationEffectWriter.cs`, `HapticToneService.cs`, `AudioPassthroughService.cs` |

The transport is abstracted behind `ILinkControlChannel`, so an in-memory test harness, the TCP socket (`TcpControlChannel`), and the punched UDP path (`UdpControlChannel`) share one path.

---

## Discovery

`LinkDiscovery` is a UDP broadcast beacon, not mDNS. It binds `IPAddress.Any:27501`, announces every two seconds to `IPAddress.Broadcast:27501`, and prunes a peer after ten seconds of silence. Because it broadcasts, it is same-subnet only. The beacon carries a four-byte magic, a version, the link port, the sender's identity fingerprint (hex), and the self-asserted machine name. A forged beacon can only put a name in the **Nearby PCs (Not Paired)** list. The crypto gate still controls admission. The receive loop filters out the PC's own fingerprint and raises `PeersChanged`. The discovered-peer table caps at 256 entries so a beacon flood with rotating fingerprints cannot grow it without bound. A known peer keeps refreshing and is never evicted by the cap.

Discovery is a convenience, not the only way in. The Dashboard also carries a manual "Or Connect by Address (Advanced)" field with a "Pair / Connect" button, which raises `DashboardViewModel.ConnectToPeerRequested` into `InputService.OnConnectToPeerRequested`. That handler enables and starts the link server if it is off, splits an optional `:port` suffix off the typed host (falling back to the configured link port), builds the exposed-device list, and calls `LinkServer.ConnectAsync`. The auto-reconnect dial below runs through the same handler, so a hand-typed address and a discovered peer take an identical path across a subnet boundary.

The same field also accepts a connection code, which is the internet lane (#294). `LinkCode.LooksLikeCode` sorts the two apart before anything else: a host or `host:port` always contains a dot or a colon, a code never does.

---

## Server, connection, and the sealed transport

`LinkServer` runs a `TcpListener` for the pairing handshake and a UDP socket for data, both on the link port (default 27500). It caps pending handshakes, times them out after three minutes, sends keepalives, and reaps idle connections. A reconnecting peer replaces its prior connection.

It holds a `List<LinkPeerConnection>`, so one PC can be linked to many peers at once. The mesh is many-to-many: pairing is pairwise (one handshake and one six-digit code per pair), but `PushLocalFrame` fans a shared device's input out to every consuming peer, and `PushOutputEffect` and `PushAudio` address the reverse frame by the owning peer's fingerprint so each device's feedback routes back to the right owner. There is no two-PC cap.

`LinkConnection` runs the handshake (initiator or responder) and then owns a `LinkSession`. `LinkSession` seals every datagram: a 14-byte authenticated header (message type and epoch, slot, a 32-bit sequence, a microsecond timestamp) plus ChaCha20-Poly1305 ciphertext and a 16-byte tag. The sequence doubles as the nonce counter, and the two directions use disjoint salts so both peers share one key without a nonce collision. Receive is verify-then-window: check the tag, then run `AntiReplayWindow`, so a forged sequence never advances the replay state. The session hard-stops before the 32-bit sequence wraps and forces a rekey.

`LinkMessageType` values: `Input` (an absolute device-state frame, owner to consumer), `Keepalive`, `Output` (a tagged effect frame, consumer to owner), `Audio` (a speaker PCM block), `DeviceList` (the owner's exposed-device set, resent on change and every two seconds for hot-plug sync), `SourceDemand` (a consumer-to-owner report that a live mapping on the consumer polls a demand-gated source on this device, #241, see below), and `PathOffer` (either side's current candidate endpoints, sent over a relayed session only so a relay-started session can upgrade to a direct path, #294). A legacy `Haptic` type is superseded by `Output` and unused. The initial device lists are also exchanged during the handshake under a separate control key. Each V1 device entry carries the stable slot, a stable id, the name, VID and PID, capability counts, a capability bitmask, and the input-device type. The capability bitmask packs eight flags into one byte: `HasRumble` (value 1), `HasRumbleTriggers` (2), `HasGyro` (4), `HasAccel` (8), `HasTouchpad` (16), `HasHaptic` (32) so a remote wheel or FFB stick's force-feedback pipeline runs, `Online` (64) so active/inactive propagates, and `HasAccelAux` (128) so an aux/left-side accelerometer (Nunchuk, left Joy-Con, #199) exposes. `HasAccelAux` (value 128) exhausts the caps byte, so the capabilities that arrived later ride a second capability byte in the `0xE4` device-list tail below rather than another bit.

### The source-demand lane (#241)

Demand latches are machine-local. `SourceCoercion` stamps them where the mapping evaluates, so a consumer's NFC binding could never arm the owner's reader on its own. The `SourceDemand` datagram closes that gap. Payload byte 0 is the demand kind, and 1 means NFC reader.

- The consumer ships demand (`RemoteLinkOutputRouter.ShipNfcDemand`) for every online reader-capable `peer://` device while its own NFC demand latch is fresh or tag registration is capturing. The router rate-bounds it to one datagram per device per second, since the owner treats each arrival as a fresh stamp.
- The owner (`InputService.OnRemoteSourceDemandReceived`) resolves the link slot to the shared device and stamps a per-device wall-clock mark. The arming cadence reads that mark exactly like the local latch, inside the same ten-second demand window, so the same teardown and Bluetooth gate apply.
- There is no off message. A lapsed demand is the off signal, matching the local latch's own expiry contract.

### Device-list metadata extension

After the V1 records, `EncodeDeviceList` appends a metadata extension marked by a magic byte (`0xE2`), one section per V1 record in the same order. It carries the serial number, the touchpad shape (`NumTouchpads` plus a finger count per pad), and the forwarded `DeviceObjects` (the owner's named inputs: `Name`, `InputIndex`, `Offset`, an `ObjectType` flags word, and the `ObjectTypeGuid`). So serial, touchpad shape, and named inputs now cross the link, and a remote device lists on the Devices page and in the mapping picker identically to a local one.

The extension uses the same appended-tail compatibility as the input codec. An old decoder reads its `count` V1 records and never looks at the tail. A new decoder facing an old sender finds no magic byte. A malformed extension tail falls back to the V1 result: any parse failure resets every extension-carried field on every record, so a mid-record throw leaves no half-applied garbage, and the consumer synthesizes generic names as before.

Objects are forwarded only for device types whose names the consumer cannot synthesize locally: Consumer Control, NFC, and Microphone (#317, whose buttons are named from the owner's own phrase registry). The push travels as one UDP datagram into a 4 KB receive buffer on old peers, so the encoder budgets the payload (a 3800-byte floor). Once it nears that floor the remaining devices get empty object sections and the consumer falls back to synthesized names for them, rather than the whole list becoming undeliverable. The budget targets old peers only: the current receive loop (`LinkServer.UdpLoopAsync`) takes datagrams into a 64 KB buffer, the UDP maximum, so an oversized frame can no longer vanish into a receive error.

Six more tails follow the `0xE2` extension, each marked by its own magic byte and appended in order:

| Magic | Tail | Carries |
|---|---|---|
| `0xE3` (`DeviceListExtV2Magic`) | Raw button count | One clamped byte per device: `RawButtonCount`, so the consumer's mapping picker offers the device's native buttons past the 22 standardized gamepad slots. `RemotePeerDeviceInfo.RawButtonCount` and `RemotePeerDevice.SupportedButtonIndices` carry it through the pipeline. |
| `0xE4` (`DeviceListExtV3Magic`) | Second capability byte | The post-exhaustion capability flags: `HasNfcReader` (value 1, #241), `HasGyroAux` (2, #252), and `HasExtraGenericAxes` (4, #193 over the wire). |
| `0xE5` (`DeviceListExtV4Magic`) | Raw axis count | One clamped byte per device: `RawAxisCount`, the axis twin of `RawButtonCount`, so a remote fight stick's or DS3's extra analog axes list in the picker. |
| `0xE6` (`DeviceListExtV5Magic`) | Sender machine name | One string for the whole list, not per device. Device rows are suffixed with the owning peer's name, and that name used to arrive only through LAN discovery, so the code and punch paths left every remote device unlabeled. |
| `0xE7` (`DeviceListExtV6Magic`) | Supported button set | Per device: `[maskLen][maskLen bytes]`, an LSB-first bitmask over button indices. `maskLen` 0 means dense (every index below the raw count). `NumButtons` is the standardized 22-slot space, not a physical count, so only the owner knows which of slots 11-21 exist. |
| `0xE8` (`DeviceListExtV7Magic`) | Supported axis set plus SDL GUID | Per device: the same bitmask shape over axis indices, then the `SdlGuid` string. `NumAxes` is pinned to 6 for every SDL gamepad, so without this a stickless pad advertised phantom stick axes and the default profile auto-bound to them. |

Each tail decodes only after everything before it parsed cleanly, under its own `try`/`catch`. A malformed tail costs only its own fields and marks the cursor unreliable, so later tails are skipped rather than misread. An old peer that stops earlier simply leaves the fields at their defaults (flags false, counts zero).

The periodic push also refreshes an already-registered device in place. `ReconcileRemoteDevices` keys by the stable device id and copies the relayed metadata (serial, touchpad shape, `DeviceObjects`), the v1 capability flags plus `HasGyroAux` and `HasNfcReader`, and the axis, button, and hat counts and input-device type onto the existing record, so a capability that appears after connect (a Joy-Con pair joining, a reader arming rule flipping) reaches the consumer without a re-register. `HasExtraGenericAxes` and the `0xE3`, `0xE5`, `0xE7`, and `0xE8` tail fields (raw counts, supported index sets, SDL GUID) are set only at first registration and are not refreshed in place.

---

## Reaching a peer over the internet (#294)

Everything above is one subnet. #294 adds internet reach with no VPN, no port forward, and no PadForge-run server. Nothing in the handshake or the sealed data plane changes. Only how the two sockets find each other does, and every lane ends in the same `LinkConnection` handshake over an `ILinkControlChannel`.

**Learning our own address.** `StunClient` sends RFC 5389 Binding requests (magic cookie `0x2112A442`) from the very socket `LinkServer` already bound, because a NAT mapping is per socket and a fresh socket would learn a different one. It queries three free servers from two operators (`stun.l.google.com:19302`, `stun.cloudflare.com:3478`, `stun.nextcloud.com:3478`). `LinkServer.ProbePublicEndpointAsync` drives it, `LinkServer.Nat` holds the verdict, and `StartNatKeepalive` holds the mapping open, since a measured Verizon CGNAT mapping dies after 40 seconds idle. `PublicEndpointChanged` fires when the mapping moves.

**Classifying the NAT.** `NatProfile.Classify` reads the external ports several STUN servers reported, in probe order. All equal means `Cone`. Differing but stepping by a small consistent delta means `SymmetricSequential` (measured: Verizon 5G CGNAT increments by 2). Erratic means `SymmetricRandom`, the residual that truly needs a relay. `IsPunchable` is true for the first two.

**Codes.** `LinkCode` uses Crockford base32 (no I, L, O, U) so a code reads aloud unambiguously, and it comes in two shapes. A short code is `ShortCodeLength` (8) characters and is an opaque rendezvous key. A long self-contained code packs 28 bytes (version, flags, public endpoint, private endpoint, an 8-byte fingerprint prefix, an expiry in minutes, and the NAT kind plus delta) and is emitted grouped in fives. The code is not a secret and authenticates nobody. The fingerprint prefix only buys an early mismatch abort, and the SAS plus Ed25519 handshake still gates trust. `TwoWayPunchNonce` derives the shared 16-byte punch nonce from both fingerprint prefixes in sorted order, and `IsHandshakeInitiator` gives the lexicographically smaller fingerprint the initiator role, so the two sides agree with no extra exchange.

**Predicting ports.** `PortPredictor.BuildSprayTargets` puts the peer's raw advertised endpoints first (a cone peer or a shared LAN connects with no prediction), then, for a sequential-symmetric peer, a forward window of `DefaultWindowSteps` (512) delta-steps on its public IP, each surrounded by a `DefaultNeighbourhood` (2) radius to absorb jitter from other subscribers on the same CGNAT pool. De-duplicated on the full address string, since `MapToIPv4` on a real IPv6 candidate keeps only four bytes and silently dropped distinct v6 candidates.

**Punching.** `HolePuncher` sprays authenticated probes at every candidate simultaneously so both NATs open. A probe is `ProbeLen` (25) bytes: `TagPing` `0xC2` or `TagPong` `0xC3`, then `PrefixLen` (8) bytes of the sender's fingerprint, then the 16-byte nonce. Carrying the sender prefix is what lets an unsolicited receiver derive the shared nonce and answer without the user clicking anything. `MaxProbeBudget` caps a call at 20,000 probes. Candidate order is private first, then IPv6 direct, then the public STUN endpoint. `PunchedConnection` then runs the unmodified handshake over the won path, both sides spraying and listening, and yields the same `LinkConnectionResult` the TCP path produces.

**The reliable channel over UDP.** `UdpControlChannel` is `ILinkControlChannel` over datagrams: a stop-and-wait-per-message ARQ, `TagData` `0xC0` and `TagAck` `0xC1`, each followed by a big-endian u32 channel id and u32 sequence. The channel id derives from the punch nonce, so a delayed datagram from a previous attempt on the same endpoint pair can never occupy a fresh channel's sequence space. These tags demux cleanly from sealed data, whose first byte is `(type << 4) | epoch` with type 1 through 8. A send that faults or is canceled poisons the channel rather than leaving the peer's expected sequence unknowable.

**Signaling.** A punch needs both sides sending at once, and an idle host cannot answer probes its own router drops. `Dht.CodeRendezvous` supplies the missing channel over the public BitTorrent DHT. Everything is derived from the host's code by HKDF: a seed to an Ed25519 signing key, a BEP 44 salt, a ChaCha20-Poly1305 key, and `target = SHA1(pub || salt)`. The caller puts an encrypted "I am calling, here are my addresses" record there, the host polls its own slot on a 5-second timer (`InputService.PollCodeRendezvousAsync`) and punches back. The record is encrypted, so DHT nodes never see endpoints, and the code itself is never published.

**Presence for paired peers.** `Dht.PresenceRecord` and `Dht.PresenceService` keep a paired peer findable after either side moves. The slot is keyed off the pairwise 32-byte rendezvous capability established at pairing and stored on `PeerTrust`, never off the Ed25519 public key, because BEP 44 publishes that key in the clear to every storage node. One slot per pair per direction. `Dht.DhtPresenceStore` does the iterative Kademlia lookup (`K` 8, `Alpha` 8, `MaxRounds` 20, read-only per BEP 43) against `router.bittorrent.com`, `dht.transmissionbt.com`, `router.utorrent.com` (all port 6881) and `dht.libtorrent.org:25401`. A publish counts as healthy at 8 or more acks. Republish is 30 to 45 minutes with jitter against a roughly 2-hour BEP 44 expiry. `Dht.RemoteLinkInternetService` is the policy loop that ties it together, driven from `InputService` on a 60-second maintain tick.

**Relay fallback.** Where both sides sit behind symmetric or carrier-grade NAT there is no direct path at all, so `IrohRelayClient` speaks the open iroh relay protocol to the free n0 relays (`use1-1`, `usw1-1`, `euc1-1`, `aps1-1` at `.relay.n0.iroh.link`). WebSocket to `wss://host/relay` with subprotocol `iroh-relay-v2`, then a challenge and response handshake signing `blake3::derive_key("iroh-relay handshake v1 challenge signature", challenge)` with an ephemeral Ed25519 key. A peer is addressed by that key, so no IP, port, or NAT is involved. `LinkServer` layers a HELLO exchange on top (`TagRelayHello` `0xC4`, `TagRelayHelloAck` `0xC5`) so a caller knows someone is listening before it starts the handshake. PadForge hosts nothing and the relay only ever sees ciphertext, since the payload is already sealed by the unchanged handshake and `LinkSession` AEAD.

**Lane order on a code connect.** `InputService.OnConnectToPeerRequested` arms the relay (`EnsureDialRelayAsync`), publishes the DHT call request, tries `LinkServer.ConnectByPunchAsync` with a 20-second punch timeout, and on failure dials the relay identity the host's code derives (`ConnectByCodeRelayAsync`, 45 seconds). A paired peer reconnecting instead uses `ConnectByIdentityRelayAsync` (25 seconds) against the stable identity relay, which needs no DHT lookup and no direct path. A session that started on the relay does not stay there: `PathOffer` datagrams exchange fresh candidates over the relay, which is the ideal signal for a punch since both peers are already reachable and authenticated there.

---

## Pairing handshake

`LinkHandshake` is an authenticated key exchange in four messages: commit, reveal from the responder, reveal from the initiator, confirm. It runs unmodified over whichever `ILinkControlChannel` won, TCP on the LAN or `UdpControlChannel` on a punched or relayed path.

- **Ephemeral X25519 per side** gives forward secrecy.
- **Commit before reveal.** The commit is `SHA256` over the commit label, the ephemeral public key, a nonce, the capabilities, and the static public key. Binding the static key into the commit closes the one SAS input a relay attacker could otherwise grind. The responder recomputes and checks it with a constant-time compare before trusting the reveal.
- **Ed25519 static-key signatures over the transcript hash.** The transcript hash is `SHA256` over the three handshake messages, each field length-prefixed so boundaries are unambiguous. Both sides sign it and verify the other. Capabilities and version are folded into the signed transcript, so a downgrade fails at the signature check.
- **Six-digit SAS.** A hash of the transcript reduced modulo one million, formatted to six digits. It is compared out of band on first pairing only.
- **Session key** via HKDF over the shared secret, salted by the transcript hash. The connection then derives separate control and data keys.
- **Fail-closed.** Every malformed, out-of-order, or unauthenticated input throws, and no device is created on a failed handshake.

Admission runs `PeerTrustStore.Decide(peerStaticKey)`. First contact prompts the user (the `RemoteLinkPairDialog`). A known key reconnects with no prompt, and the signature still proves possession.

---

## Trust and identity

`PeerTrust` persists per peer as XML attributes: the pinned Ed25519 public key (an identity, not a secret), the name, the self-asserted host name, the pairing time, a reconnect-enabled flag (default true), the gamepad-only flag, and `RendezvousCapabilityBase64` (the 32-byte pairwise DHT rendezvous capability from #294, empty for peers paired before the internet lane existed). The fingerprint is the SHA-256 of the public key.

`PeerTrustStore` is the in-memory authority. `Decide` returns first-contact (unknown, never auto-trusted), known-auto-select, or known-manual. Lookups use a constant-time compare. An unknown key defaults to gamepad-only restricted, which is the fail-safe.

`IdentityProtector` stores this PC's own identity in one of three modes. **Secure** (the default) wraps the private key with DPAPI at machine scope, so any Windows user on the PC can use it but it does not move to another machine. **Portable, password protected** wraps it with PBKDF2-SHA256 (600,000 iterations) and AES-256-GCM. **Portable, open** stores it in the clear. The blob is self-describing, with a version and mode header. `LoadOrMint` mints only when the store is empty or corrupt and never overwrites a locked identity, so a password prompt or a wrong-machine state is surfaced to the caller rather than clobbered. A mode switch re-wraps the same key, so the fingerprint and all pairings survive.

---

## Input streaming (owner to consumer)

On the owner, a stream timer running near 125 Hz calls `LinkServer.PushLocalFrame` per exposed device, which encodes the state through `CustomInputStateCodec` and seals an `Input` datagram. The codec is absolute: every frame is the full state through a present-block bitmask with neutral-omit, so packet loss self-heals and a centered idle pad is three bytes.

On the consumer, the device list yields a `RemotePeerDevice` per exposed device. The link server's `DeviceConnected` event calls `InputManager.RegisterPeerDevice`, which runs it through `FindOrCreateUserDevice` and `LoadFromExternalDevice`. A `RemotePeerDevice` is an `ISdlInputDevice`, so it flows through the normal six-step pipeline like any local source. Inbound `Input` datagrams decode into a back buffer that swaps under a lock, newest-wins by timestamp. After a three-second stale window the device reads as offline and releases any held inputs. The device identity is salted by the peer fingerprint, but not through the path. `DevicePath` uses an eight-character short form (`peer://{Short(fingerprint)}/{deviceId}`), which alone would collide across peers whose fingerprints share a first eight hex chars. The full fingerprint salts the collision-safe identity: `InstanceGuid` is an MD5 over `pflink-dev:{fingerprint}:{deviceId}` and `ProductGuid` an MD5 over `pflink-prod:{fingerprint}:{VID}:{PID}:{type}`. So two peers sharing the same controller model never alias through the non-peer-namespaced `ProductGuid` reconnect fallback.

### Present-block table

A 16-bit present-block bitmask (`Block`, a `[Flags]` enum in `CustomInputStateCodec`) leads the payload. A block appears only when its data is non-neutral, and the decoder resets to neutral first and applies only the blocks the frame carries. Sixteen blocks are defined, and `Nfc` at bit 15 exhausts the u16 mask:

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
| 14 | `CapSense` | Capsense touch channels (stick tops and grips, SDL fork API): one byte, one bit per channel |
| 15 | `Nfc` | NFC tag buttons (#241): a span byte plus a button bitmask |

`Battery` sends when the percent is known or the pad reports charging, and always carries both the percent byte and the charging flag, so a "charging, percent unknown" pad keeps its flag on the wire. Battery crosses the link.

`CapSense` carries four wire channels (`CapSenseWireSlots`, low bit = channel 0) and sends only when something is touched, so an all-untouched frame omits the block. `Nfc` is variable-length: a span byte (stored as span minus one, so a tag on button 255 still fits) then `ceil(span/8)` bitmask bytes. Button 0 is "Any NFC Tag" and is registry-independent, so it is always meaningful remotely. Per-tag buttons resolve against the consumer's own `NfcTagRegistry`, the shared-config assumption every remote binding already makes. The demand that arms the owner's reader travels the other way, on the source-demand lane above.

Bits 9–15 are the post-3.5.0 additions, appended strictly after every older block. That ordering is what keeps mixed-version peers compatible without a `Version` bump: an old decoder reads its known blocks in order, never reaches the new bits, and its final `o <= payload.Length` check tolerates the trailing bytes. A new decoder facing an old sender simply finds those bits clear.

### The `0xE6` extension tail

Bit 15 fills the present mask, so post-`Nfc` blocks ride an appended extension rather than a widened mask (widening would move the payload start and break every peer): the `ExtMagic` byte (`0xE6`, unrelated to the device-list tail that shares the value, since the two live in different frames), a u16 extension mask, then the payloads in `BlockExt` order. The read is positional, a "maybe" read, never a required one. The tail exists only when the magic byte is the next thing in the frame, so a peer that predates it never writes one, and a frame that ends before it is complete. It is the same appended-tail compatibility rule the device-list tails use.

The first extension block is `BlockExt.GyroAux` (#252): the gyro triple of a combined pair's left Joy-Con, capability-gated like `Gyro`, `Accel`, and `AccelAux` because a zeroed reading is a still controller, not an absent sensor. Decode fails closed on a non-finite float, resetting the frame to neutral so a hostile NaN never reaches the tuning chain. On the consumer the block feeds the aux gyro sources and `SourceCoercion.GravityProviderAux` on the tuning path, and the `HasGyroAux` capability (the `0xE4` device-list tail) gates discoverability, mirroring a local left Joy-Con.

---

## Reverse output relay (consumer game to owner hardware)

The consumer runs the full config-applied output pipeline for a `peer://` device. The final hardware write fails (the handle is zero), so each write chokepoint hands its config-baked payload to `RemoteLinkOutputRouter` instead:

- `ShipSonyEffect` (in `PlayStationEffectWriter`) strips the report id and encodes the DualSense or DualShock 4 effect body.
- `ShipVibration` (Step 2) encodes the full `Vibration` (motors, impulse triggers, directional and condition force).
- `ShipWheel` (Step 2) encodes a semantic wheel frame (force, condition, periodic, range, auto-center, RPM-LED mask).
- `ShipHapticTone` (in `HapticToneService`) encodes the HD haptic tone (#147): one (dominant frequency Hz, amplitude 0..1) pair per rumble tick, slot volume already applied.
- `ShipPlayerIndex` encodes the consumer's winning 1-based player number (the smallest displayed number across the slots the pad feeds) for a shared Nintendo pad (`0x057E`), Bluetooth DS3 (`0x054C`/`0x0268`), or PS Move (`0x054C`/`0x03D5`, whose owner-side lane routes the number into the sphere's default color, #277). #191. A DualSense or DualShock 4 peer carries its player LED in the Sony effect body, so it never ships this kind.
- `ShipGuideLed` encodes the consumer's configured Guide/Home LED brightness (0-100 percent) for a shared Xbox GIP pad, 2015 Steam Controller (#209), or Switch HOME-LED pad (Pro Controller, right Joy-Con, pair, charging grip, #226). It has `ShipPlayerIndex`'s shape, dedups per path, and addresses one peer device by its path.
- `ShipAudio` (in `AudioPassthroughService`) ships the speaker PCM block on the `Audio` datagram.

`OutputEffectCodec.Kind` has six values: `SonyEffect = 1`, `Vibration = 2`, `Wheel = 3`, `HapticTone = 4`, `PlayerIndex = 5`, `GuideLed = 6`.

The router maps the `peer://` path to a target (owner fingerprint and link slot, fixed at connect) and sends through `PushOutputEffect` or `PushAudio`. Dedup varies per channel. Sony effects, scalar vibration, wheel frames, player index, and Guide LED dedup exact repeats. A vibration frame with directional or condition data always ships. The haptic tone dedups only the silent steady state, because an active tone must ship every rumble tick to keep refreshing the owner's hangover expiry.

On the owner, the `OutputReceived` handler `OnRemoteOutputReceived` decodes the frame, resolves the link slot to the physical source device, takes the sole-writer lease (except for a `PlayerIndex` or `GuideLed` frame, see below), and applies by kind: a Sony effect through `SDL_SendGamepadEffect`, a vibration through `ForceFeedbackState.SetDeviceForces`, a wheel frame through `ApplyRemoteWheel` (which re-encodes with the owner's own vendor writers, see [Wheel Force Feedback Internals](wheel-ffb-internals.md)), a haptic tone (`HapticToneHz`/`HapticToneAmp`) re-encoded by the owner's own per-family writer (Joy-Con HD Rumble, Steam 0x8f, Triton 0x83, Deck), a player index through `SetPlayerIndex` (0-based) for a Nintendo pad (VID `0x057E`), `Ds3DirectService.TrySetPlayerNumber` for a Bluetooth DS3 (`0x054C`/`0x0268`), or `PsMoveDirectService.TrySetPlayerNumber` for a PS Move (`0x054C`/`0x03D5`), a Guide/Home LED brightness through `XboxGipGuideLedWriter.TrySetBrightness` for an Xbox GIP pad, `SteamHomeLedSetter.TrySet` for a 2015 Steam Controller, or `SwitchHomeLedSetter.TrySet` for a Switch HOME-LED pad (the same writers and gate order as the local apply path), and audio through `AudioPassthroughService.FeedRemoteAudio` (see [Controller Audio Internals](controller-audio-internals.md)). The vibration apply has two special cases. A Fanatec pedal re-routes to its raw-HID pedal-rumble writer. An Xbox One+ impulse-trigger pad, gated by `XboxControllerIdentity.IsImpulseTriggerDevice`, records through `TryRecordXboxImpulseSnapshot` and writes all four channels (large and small plus LT and RT) via `XboxImpulseHidWriter.Write`, with SDL rumble suppressed so the impulse triggers fire. The owner synthesizes nothing here: for the wheel and the haptic tone it is a transport transcoder that re-frames the semantic payload with the writer that owns the real hardware.

**Sole-writer guard.** A device can be both shared out and mapped locally, and output cannot merge. An inbound relay frame stamps the local path with a three-second lease, and the owner's local chokepoints skip their own writes while the lease is fresh. A device that is only lent out (not also mapped locally) has no local writer, so there is no contention. A `PlayerIndex` or `GuideLed` frame is exempt from the lease. Both are cosmetic LED updates, not effect claims, so neither blanks a locally-mapped device's rumble or lightbar for the lease window.

---

## Gamepad-only enforcement

`InputManager.SetDeviceRestricted` populates the restricted-device set from each peer's gamepad-only flag, set before the device goes online. `IsSlotRestricted(slot)` is true when any online restricted device maps to that slot, and it early-outs when no peer is restricted (`RestrictedSnapshot` returns null and the caches rebuild only when the set changes). Five chokepoints honor it:

- The KBM virtual controller (Step 5) submits a neutral state for a restricted slot, releasing anything held.
- The VR controller pair (Step 5) submits a default `VrRawState` for a restricted slot, so a gamepad-only peer never reaches SteamVR.
- Macros (Step 4b) are restricted when the slot is restricted or a restricted device is a macro trigger.
- The five Win32 `SendInput` emitters (key, text, mouse move, mouse button, scroll, in Step 4b) early-return while the macro slot is restricted.
- The menu overlay's key lane (`CollectMenuDirectOutputs`) suppresses key cells per restricted device via `RestrictedSnapshot()`. It deliberately gates per device, not per slot, so a restricted peer sharing a slot does not mute a local controller's key cells.

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

*Last updated for PadForge 4.3.2.*
