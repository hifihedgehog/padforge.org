# Sensa Haptics: Internals

*How controller rumble becomes a Razer Sensa HD effect: the Interhaptics bindings, the provider bring-up and its retry sentinel, the worker lifecycle, and the rumble lane that feeds it.*

The user-facing page is [Lightbar Mirrors and Sensa Haptics](../features/lightbar-mirrors.md). This one is for whoever has to change the code.

| File | Role |
|---|---|
| `PadForge.App/Services/SensaHapticsService.cs` | The bindings, the worker, the publish surface |
| `PadForge.App/Common/Input/InputManager.Step5.VirtualDevices.cs` | `UpdateSensaLane`, the per-tick feed |
| `PadForge.App/Common/Input/InputManager.cs` | The call site, after `UpdateRumbleAudioLane` in the poll loop |
| `PadForge.App/Services/InputService.cs` | `StartSensaIfEnabled`, `StopSensaService`, status marshaling |
| `PadForge.App/PadForge.App.csproj` | The vendored engine and provider |
| `PadForge.App/Resources/Interhaptics/x64/` | `HAR.dll`, `Interhaptics.RazerProvider.dll` |
| `PadForge.Tests/SensaHapticsTests.cs` | The bench, which runs the real engine |

---

## Why the engine layer

Razer's game-facing surface (the WYVRN SDK) plays only pre-authored named clips and carries no amplitude channel. One layer down is public: the Interhaptics Core SDK, whose parametric API takes an amplitude at runtime. The shipping Unity integration, `WyvrnOfficial/Interhaptics_Unity_CoreSDK`, carries the proven call order, and every native call here mirrors it function for function. The Unity reference makes every call from one thread, and so does this worker.

The two DLLs are vendored from that repository's `Runtime/Plugins/x64`, the same pair every Unity title embedding the SDK redistributes. They ship unmodified inside the executable under the Wyvrn EULA (see the README's third-party section). The csproj includes them as `Content` with `Link` so they land beside the executable, conditioned on the files existing, and the service P/Invokes them lazily so a missing pair degrades to a diag line.

---

## Bindings

The `Har` class mirrors `HAR.Native.cs` from the Unity SDK verbatim: same names, same signatures, default marshaling. The DLL name is `HAR`.

| Export | Signature | Used for |
|---|---|---|
| `Init` | `bool ()` | Engine up |
| `Quit` | `void ()` | Engine down |
| `AddParametricEffect` | `int (double[] amplitude, int amplitudeSize, double[] pitch, int pitchSize, double freqMin, double freqMax, double[] transient, int transientSize, bool isLooping)` | Creates the one effect. Returns `-1` on failure. |
| `AddTargetToEventMarshal` | `void (int id, CommandData[] target, int size)` | Targets the effect at the whole body |
| `SetEventIntensity` | `void (int id, double intensity)` | The live rumble amplitude |
| `PlayEvent` | `void (int id, double vibrationOffset, double textureOffset, double stiffnessOffset)` | Starts the effect |
| `ComputeAllEvents` | `void (double curTime)` | Advances the engine clock |
| `StopAllEvents` | `void ()` | Teardown |

The `Provider` class carries the Razer provider trio plus the render call, names verbatim from `RazerSensaProvider.cs`. The DLL name is `Interhaptics.RazerProvider`.

| Export | Signature |
|---|---|
| `ProviderInit` | `bool ()` |
| `ProviderIsPresent` | `bool ()` |
| `ProviderClean` | `bool ()` |
| `ProviderRenderHaptics` | `void ()` |

The provider is a thin bridge to Synapse's installed Interhaptics runtime: it locates `RzInterHaptics.dll` through the registry and signals the mixer's global event (a strings-level read of the shipped DLL). Without Synapse, `ProviderInit` fails cleanly.

`CommandData` is `Interhaptics.HapticBodyMapping.CommandData`, three `int` enums laid out sequentially and blittable:

```csharp
[StructLayout(LayoutKind.Sequential)]
internal struct CommandData
{
    public int Sign;   // Operator: Plus = 1
    public int Group;  // GroupID: All = 0
    public int Side;   // LateralFlag: Global = 0
}
```

---

## Call order

The worker follows the Unity integration's `HapticDeviceManager` and `HAR.PlayParametricHapticEffect`:

| Step | Calls |
|---|---|
| 1. Engine up | `Har.Init()`. `HAR.dll` runs with no Razer device present. A `DllNotFoundException` or `EntryPointNotFoundException` is caught and logged, and the worker returns. |
| 2. The effect | `AddParametricEffect({0, 1, 1, 1}, 4, null, 0, 65.0, 300.0, null, 0, true)`: a looping constant envelope whose amplitude pairs are time-value (hold 1.0 across a one-second loop), the Unity reference's default 65 to 300 Hz band, no pitch, no transients. Then `AddTargetToEventMarshal(id, [Plus, All, Global], 1)`, `SetEventIntensity(id, 0.0)`, and `PlayEvent(id, -clock.Elapsed.TotalSeconds, 0.0, 0.0)`. The negative-now offset aligns the effect clock with the `ComputeAllEvents` time argument. |
| 3. Provider bring-up | `ProviderInit()` on the retry cadence below. |
| 4. Per tick | Read the published amplitude. If it changed, `SetEventIntensity(id, amp)`. Then `ComputeAllEvents(clock.Elapsed.TotalSeconds)`, and only when the provider is up and `ProviderIsPresent()` is true, `ProviderRenderHaptics()`. Sleep `tickMs`. |
| 5. Teardown | `StopAllEvents()`, `ProviderClean()` if the provider was up, `Quit()`. |

Rendering gates on both init and presence. `ProviderIsPresent` answers true even when `ProviderInit` failed (bench-measured), and the Unity reference never queries presence for a failed-init provider, so its value there is undefined.

---

## Provider arming and the retry sentinel

The provider is retried every `retryMs` (default 30000) while it is down. The sentinel is seeded one full interval in the past:

```csharp
long lastProviderTry = Environment.TickCount64 - _retryMs;
```

The original code seeded `long.MinValue`. `TickCount64 - long.MinValue` overflows negative, the `>= _retryMs` test never passed, and the retry block silently never entered while the worker looked healthy in its tick loop. A live stack dump found it after log lines only bracketed the hang. `ProviderInitAttempts` counts every attempt so the cadence is a tested fact: `SensaHapticsTests.Service_ArmsPublisherAndDegradesWithoutRuntime` asserts it is at least one.

`BeforeProviderInit` is an internal static hook that runs on the worker immediately before `ProviderInit`, so a test can hold a worker inside the bring-up window.

On success the worker reports `Active`. The provider stays up for the life of the worker. There is no liveness probe against Synapse after that.

---

## Worker lifecycle

The worker is a dedicated background `Thread` named `SensaHaptics`, not a task. `Start` is a no-op while `_thread` is set. `Stop` sets `_stop`, joins for 3000 ms, and nulls `_thread` regardless, so a worker still inside `ProviderInit` can outlive its service.

That outliving worker is the predecessor-join rule. Its `finally` disarms the publisher, zeroes the amplitude, and calls `Har.Quit`, and if it ran under the next instance's engine it would tear that engine down. So every worker's first act is:

```csharp
var prev = Interlocked.Exchange(ref s_lastWorker, Thread.CurrentThread);
if (prev != null && prev != Thread.CurrentThread && prev.IsAlive) prev.Join();
Volatile.Write(ref s_publisherArmed, 1);
```

The predecessor's teardown lands before the successor arms and inits, never after. `s_lastWorker` is static because the publisher flag it protects is. `SensaHapticsTests.Service_NextWorkerWaitsForAStragglingPredecessor` holds a worker in `BeforeProviderInit`, stops it, starts a second service, and asserts the second worker waits for the first to exit.

| Static | Purpose |
|---|---|
| `s_amplitudeBits` | The published amplitude, 0..1, as float bits |
| `s_publisherArmed` | Nonzero while a worker runs |
| `s_lastWorker` | The most recent worker thread |

The `finally` runs on every exit path, faults included (`SENSA worker fault: {type}`), and reports `Stopped` last.

---

## Rumble to haptic

`InputManager.UpdateSensaLane` runs once per poll tick inside the non-idle loop, right after `UpdateRumbleAudioLane`, and after `UpdateVirtualDevices` so a slot destroyed this tick publishes zero the same tick. Its first line is the cheap exit:

```csharp
if (!PadForge.Services.SensaHapticsService.PublisherArmed) return;
```

For every slot up to `MaxPads` it takes the slot's inbound rumble pack (`GetInboundRumblePack`) and max-merges it with the live `VibrationStates[slot]` through `LfeOutputState.MaxMerge`, the same authority the rumble-to-audio lane reads, so test rumble counts. The pack is four `ushort` voices:

| Bits | Voice |
|---|---|
| 0-15 | Left motor |
| 16-31 | Right motor |
| 32-47 | Left trigger motor |
| 48-63 | Right trigger motor |

`PackToAmplitude` returns the loudest voice divided by 65535. The lane keeps the maximum across slots and calls `PublishAmplitude`, which clamps to 0..1 and stores the float bits with one volatile write. `SensaHapticsTests.PackToAmplitude_TakesTheLoudestVoice` and `PublishAmplitude_Clamps` pin both.

The worker reads the bits every `tickMs` (default 16) and calls `SetEventIntensity` only on change. Intensity is the whole translation: one effect, one target, one amplitude. There is no stereo targeting and no pitch mapping.

---

## Ownership and persistence

`InputService.StartSensaIfEnabled` runs at engine start and on toggle-on, returning when the toggle is off, `_inputManager` is null, or a service is live. `StopSensaService` disposes the service at engine stop and on toggle-off, and writes `Common_Stopped` to `SensaStatus`. `StateChanged` is marshaled through `_dispatcher.BeginInvoke`:

| Enum | Dashboard string |
|---|---|
| `SensaServiceState.Active` | `Dashboard_SensaActive` |
| `SensaServiceState.WaitingForRuntime` | `Dashboard_SensaWaiting` |
| `SensaServiceState.Stopped` | `Common_Stopped` |

Persistence follows the lightbar mirrors leg for leg: `AppSettings.EnableSensaHaptics` (global `bool`, default false), `ProfileData.EnableSensaHaptics` (`bool?`, null = no opinion, applied by `SettingsService.ApplyProfileServiceToggles`, authored by `OnDashboardServiceToggleChanged`), and the `MainWindow` Dashboard autosave allowlist. See [Lightbar Mirrors Internals](lightbar-mirrors-internals.md#ownership-and-persistence) for the rule and its test.

---

## Diag lines

| Line | When |
|---|---|
| `SENSA start? enabled=... engine=... live=...` | Every start attempt |
| `SENSA worker: calling HAR.Init` | Worker entry |
| `SENSA HAR.dll not found` | `DllNotFoundException` on `Init` |
| `SENSA HAR entry point missing` | `EntryPointNotFoundException` on `Init` |
| `SENSA HAR.Init => {bool}` | After `Init` |
| `SENSA HAR.Init failed or HAR.dll missing` | Worker returning without an engine |
| `SENSA AddParametricEffect returned -1` | Effect creation failed |
| `SENSA provider init => {bool}` | Every provider attempt |
| `SENSA worker fault: {exception type}` | Any unhandled exception in the worker |

---

## Tests

`SensaHapticsTests.cs` executes the real Razer-shipped engine end to end with no device present. This is the strongest hardware-free evidence available, and preferable to a mock wherever a vendor engine is separable from its device bridge.

| Test | What it proves |
|---|---|
| `RealEngine_FullLifecycle` | `Init`, effect creation, targeting, intensity, compute, and `Quit` against the shipped `HAR.dll` |
| `RealEngine_SurvivesReinit` | `Init` after `Quit`, the engine-restart path |
| `Provider_DegradesCleanlyWithoutSynapse` | `ProviderInit` returns false with no runtime, no exception |
| `PackToAmplitude_TakesTheLoudestVoice` | The four-voice max |
| `PublishAmplitude_Clamps` | The 0..1 clamp |
| `Service_ArmsPublisherAndDegradesWithoutRuntime` | Publisher armed while running, `WaitingForRuntime` reported, at least one provider attempt |
| `Service_NextWorkerWaitsForAStragglingPredecessor` | The predecessor-join rule |
| `FeedAndSiblingContracts` | The Step 5 call site and the persistence legs |

Live rendering on Sensa hardware was not verified by the maintainer.

---

*Last updated for PadForge 4.4.0.*
