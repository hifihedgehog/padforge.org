# Logitech G-Keys Internals

*How PadForge finds the G-key SDK, decodes its event word, and keeps a held key honest.*

For the user-facing side see [Logitech G-Keys](../features/logitech-g-keys.md).

The code lives in `PadForge.Engine/Common/Logitech/`:

| File | Responsibility |
| --- | --- |
| `LogitechGKeyCatalog.cs` | Finds `LogitechGkey.dll` and reports why it could not. |
| `LogitechGKeyInterop.cs` | The exported functions, the callback signature, and the event word. |
| `LogitechGKeyMap.cs` | The fixed 102-button layout and the two-way index mapping. |
| `LogitechGKeySource.cs` | Load, init, callback, the two held-state queries, teardown. |

The device row is `PadForge.App/Common/Input/LogitechGKeysDevice.cs`, which also owns the pulse and the resync. `LogitechGKeysRuntime.cs` is the Settings-to-engine mirror, written by `SettingsViewModel.GKeysEnabled`.

---

## The event word

The SDK passes one 32-bit word by value. `LogitechGkeyLib.h` declares it as C bitfields under `#pragma pack(push, 1)`:

| Field | Bits | Meaning |
| --- | --- | --- |
| `keyIdx` | 8 | G-key or mouse button number |
| `keyDown` | 1 | held or released |
| `mState` | 2 | 1, 2 or 3 for M1, M2, M3 |
| `mouse` | 1 | the event came from a mouse |
| `reserved1` | 4 | |
| `reserved2` | 16 | |

That totals 32, so PadForge reads the word whole and masks it rather than describing it to the marshaler, which has no bitfield of its own.

**Logitech's own C# sample gets this wrong and must not be copied.** Its `Doc\C#Instructions.pdf` declares the word as a `ushort`, half the width the header defines, so its `reserved2` shift of 16 can only ever yield zero. It also reads `mouse` as `(complete >> 11) & 15` where the field is one bit wide, folding three reserved bits into the answer, which can read a keyboard event as a mouse event. The header is what the DLL was compiled against, so the header wins. This was cross-checked against [Mumble](https://github.com/mumble-voip/mumble)'s `GKey.cpp`, which has decoded it correctly in production for years.

---

## Finding the library

`LogitechGKeyCatalog` builds a candidate list and tries each in order: the SDK's registered CLSID, whose `ServerBinary` value is the DLL path, then the default install path. That is the order Mumble's `GKey.cpp` uses.

**Existing and loading are different questions.** An earlier cut returned the first path that existed, which strands an x86 registration on an x64 host: the file is there, and it will never load. The catalog hands back candidates and the source tries each until one loads, which is again what Mumble does.

The source has five failure states: no SDK, a registered path whose file is gone, a load failure, a library that is not this SDK, and an init the SDK refused. Each gets its own status line. Two more lines cover running-but-silent and running-with-keys, for seven in all, so a quiet G-key always has a stated reason rather than silence.

---

## Callback, not polling

The SDK offers both. PadForge registers the callback, because the row would otherwise have to make 102 cross-DLL calls per cycle, across the SDK's two query exports, to find one press. The callback runs on the SDK's own thread, as its header states, so the handler does nothing but take a short lock and set a flag. Nothing blocking may run on Logitech's dispatch path.

### The pulse

A G-key tap can begin and end between two of PadForge's polls. A press therefore asserts its button for at least `PulseMs` (175), so a macro sees the edge. This is the handheld button row's rule, adopted for the same reason.

### The resync

Events alone cannot be trusted to close a press. The SDK only feeds an application whose Logitech profile is active, so a key held while PadForge loses that profile never delivers its release, and the button would stay asserted for the life of the session. Unplugging the keyboard mid-press reaches the same state.

`ResyncHeld` asks the SDK what is actually held and clears anything the events got wrong. It runs every `ResyncIntervalMs` (250) rather than every poll, because it is 102 cross-DLL calls and has no business running at the poll rate. It only clears. A press still arrives by callback, because the poll can fall between a press and its release and the pulse is what carries that edge.

---

## Teardown

`Teardown` never frees the module and always calls `LogiGkeyShutdown`, both matching Mumble.

Freeing the library risks a callback in flight during dispose landing in unmapped memory. Mumble does not unload on success either, and one mapped library for the life of the process is the cheaper trade. Calling shutdown unconditionally covers the case where init fails *after* the SDK has already stored the callback pointer: skipping shutdown there leaves it holding a pointer into a delegate that is about to be collected.

---

## The button layout

102 buttons, fixed rather than derived from attached hardware:

- `KeyboardCount` = `MaxGKeys` (29) × `MaxMStates` (3) = 87
- `MouseCount` = buttons 6 through 20 = 15

Mouse buttons 1 through 5 are excluded because Windows already delivers them.

The layout is fixed so a saved mapping keeps pointing at the same key when a different Logitech keyboard is plugged in. The SDK has no way to ask how many G-keys a device has, which is also why `SupportedButtonIndices` is null rather than a filtered array: gating would be a guess.

Names come from the SDK where it supplies one. A keyboard name gets the M-state appended, because the SDK's name carries no mode and M1, M2 and M3 would otherwise all read "G5". A mouse name has no mode and is used unchanged.

---

## The row

`LogitechGKeysDevice` is an `ISdlInputDevice` shaped like `HandheldButtonsDevice`: extra hardware buttons that are not a gamepad, surfaced as a synthetic row so they bind through the grid every other device uses.

Synthetic identity follows the handheld row's convention: VID `0x4C47` ("LG") and PID `0x474B` ("GK").

The row attaches whether or not the SDK starts, so the Devices list can carry the reason. A row that vanishes tells the user nothing about why.

Buttons are written every poll, pressed or not, so a released key produces its falling edge.

---

## Residual

No Logitech hardware or software is on the bench, so the library loading and calling back is unverified. The wire format is grounded in the SDK header and Mumble's implementation.

Test coverage is uneven. The decode, the button map and the pulse have real behavioral tests. The resync has only a wiring assertion that reads this file and checks the call is present, because the path needs a live source in the `Running` state and the test seam cannot supply one.

---

## Related pages

- [Logitech G-Keys](../features/logitech-g-keys.md)
- [Lightbar Mirrors Internals](lightbar-mirrors-internals.md): the other Logitech SDK PadForge loads.
- [Handheld PC Buttons Internals](handheld-buttons-internals.md): the row shape this one copies.
- [Input Pipeline](input-pipeline.md)

---

*Last updated for PadForge 4.5.0.*
