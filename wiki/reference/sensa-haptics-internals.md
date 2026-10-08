# Sensa Haptics: Internals

*How a virtual controller's rumble becomes a Razer Sensa HD effect: the Razer Sensa row, the Interhaptics bindings, the provider bring-up and its retry sentinel, the worker and the host that runs it, and the level Step 2 hands it.*

The user-facing page is [Mice, Keyboards and Vendor Rows](../features/peripherals.md). This one is for whoever has to change the code. The row runs through the hub and the link pass that the haptic mice and the lighting rows use, and its level is kept the way a haptic mouse's is. [Peripheral Outputs Internals](peripheral-outputs-internals.md) covers both.

| File | Role |
|---|---|
| `PadForge.App/Services/SensaHapticsService.cs` | The bindings and the worker |
| `PadForge.App/Common/Input/Peripherals/PeripheralOutputRow.cs` | The Razer Sensa row |
| `PadForge.App/Common/Input/InputManager.PeripheralRows.cs` | Step 1 phase 1m: the row opens and retires |
| `PadForge.App/Common/Input/Peripherals/PeripheralLinker.cs` | Presence, and the row's `Interhaptics` path |
| `PadForge.App/Common/Input/Peripherals/PeripheralOutputHost.cs` | `SensaLifecycle`: the worker runs while the row is assigned |
| `PadForge.App/Common/Input/Peripherals/PeripheralOutputs.cs` | The row's level and the backend state |
| `PadForge.App/Common/Input/InputManager.Step2.UpdateInputStates.cs` | `ApplyForceFeedback`, which sets the level |
| `PadForge.App/Common/Input/Peripherals/PeripheralRouteText.cs` | The Force Feedback tab's line |
| `PadForge.App/Services/PeripheralSwitchMigration.cs` | The retired Dashboard switch becomes an assignment |
| `PadForge.App/PadForge.App.csproj` | The vendored engine and provider |
| `PadForge.App/Resources/Interhaptics/x64/` | `HAR.dll`, `Interhaptics.RazerProvider.dll` |
| `PadForge.Tests/SensaHapticsTests.cs` | The bench, which runs the real engine |
| `PadForge.Tests/PeripheralOutputsTests.cs` | The row, its level, its route line and the migration |

---

## Why the engine layer

Razer's game-facing surface (the WYVRN SDK) plays only pre-authored named clips and carries no amplitude channel. One layer down is public: the Interhaptics Core SDK, whose parametric API takes an amplitude at runtime. The shipping Unity integration, `WyvrnOfficial/Interhaptics_Unity_CoreSDK`, carries the proven call order, and the bring-up and per-tick calls here mirror it function for function. Teardown differs: Unity's quit path cleans the providers, clears the active and inactive events, then quits, while this worker calls `StopAllEvents`, `ProviderClean`, and `Quit`. The Unity reference makes every call from one thread, and so does this worker.

The two DLLs are vendored from that repository's `Runtime/Plugins/x64`, the same pair every Unity title embedding the SDK redistributes. They ship unmodified inside the executable under the Wyvrn EULA (see the README's third-party section). The csproj includes them as `Content` with `Link` so they land beside the executable, conditioned on the files existing, and the service P/Invokes them lazily so a missing pair degrades to a diag line.

---

## The Razer Sensa row

The engine targets body parts, never one device, so one row stands for every Sensa HD device at once. `PeripheralOutputRow` (`PeripheralOutputRow.cs` line 44) with kind `RazerSensa` is a device with no inputs: name Razer Sensa, path `razersensa://local`, vendor ID `0x5046`, product ID `0x5345`, device type `PeripheralHaptics`, and an id hashed from `pfrazersensa` (`PeripheralOutputRow.IdentityFor` (`PeripheralOutputRow.cs` line 91)), so an assignment of it survives across sessions.

Step 1's phase 1m opens the row while `InputManager.PeripheralRowWanted` (`InputManager.PeripheralRows.cs` line 20) holds: Synapse's Chroma runtime is installed and the process is x64 (`PlatformSupport.SensaAvailable`). `PeripheralLinker.Build` (`PeripheralLinker.cs` line 149) gives it the one `Interhaptics` path, `sensa`, as a vendor row. The user assigns it to a virtual controller like any device, and it gets the Force Feedback tab a gamepad gets, with the controller's rumble reaching it through its own settings.

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

The worker (`SensaHapticsService.Worker` (`SensaHapticsService.cs` line 218)) follows the Unity integration's `HapticDeviceManager` and `HAR.PlayParametricHapticEffect`:

| Step | Calls |
|---|---|
| 1. Engine up | `Har.Init()`. `HAR.dll` runs with no Razer device present. A `DllNotFoundException` or `EntryPointNotFoundException` is caught and logged, and the worker returns. |
| 2. The effect | `AddParametricEffect({0, 1, 1, 1}, 4, null, 0, 65.0, 300.0, null, 0, true)`: a looping constant envelope whose amplitude pairs are time-value (hold 1.0 across a one-second loop), the Unity reference's default 65 to 300 Hz band, no pitch, no transients. Then `AddTargetToEventMarshal(id, [Plus, All, Global], 1)`, `SetEventIntensity(id, 0.0)`, and `PlayEvent(id, -clock.Elapsed.TotalSeconds, 0.0, 0.0)`. The negative-now offset aligns the effect clock with the `ComputeAllEvents` time argument. |
| 3. Provider bring-up | `ProviderInit()` on the retry cadence below. |
| 4. Per tick | Read the row's level. If it changed, `SetEventIntensity(id, amp)`. Then `ComputeAllEvents(clock.Elapsed.TotalSeconds)`, and only when the provider is up and `ProviderIsPresent()` is true, `ProviderRenderHaptics()`. Sleep `tickMs`. |
| 5. Teardown | `StopAllEvents()`, `ProviderClean()` if the provider was up, `Quit()`. |

Rendering gates on both init and presence. `ProviderIsPresent` answers true even when `ProviderInit` failed (bench-measured), and the Unity reference never queries presence for a failed-init provider, so its value there is undefined.

---

## Provider arming and the retry sentinel

The provider is retried every `retryMs` (default 30000) while it is down. The sentinel is seeded one full interval in the past:

```csharp
long lastProviderTry = Environment.TickCount64 - _retryMs;
```

The original code seeded `long.MinValue`. `TickCount64 - long.MinValue` overflows negative, the `>= _retryMs` test never passed, and the retry block silently never entered while the worker looked healthy in its tick loop. A live stack dump found it after log lines only bracketed the hang. `ProviderInitAttempts` counts every attempt, so the first attempt is a tested fact: `SensaHapticsTests.Service_StartsTheEngineAndDegradesWithoutRuntime` asserts it is at least one. No test times the 30-second interval.

`BeforeProviderInit` is an internal static hook that runs on the worker immediately before `ProviderInit`, so a test can hold a worker inside the bring-up window.

On success the worker reports `Active`. The provider stays up for the life of the worker. There is no liveness probe against Synapse after that.

---

## Worker lifecycle

The worker is a dedicated background `Thread` named `SensaHaptics`, not a task. `SensaHapticsService.Start` (`SensaHapticsService.cs` line 192) is a no-op while `_thread` is set. In a process that cannot load the engine (`PlatformSupport.SensaAvailable` is true only for x64), `Start` reports `Unsupported` on the caller's thread and starts no worker. `SensaHapticsService.Stop` (`SensaHapticsService.cs` line 205) sets `_stop`, joins for 3000 ms, and nulls `_thread` regardless, so a worker still inside `ProviderInit` can outlive its service.

That outliving worker is the predecessor-join rule. Its `finally` stops the engine's events, cleans the provider and calls `Har.Quit`, and if it ran under the next instance's engine it would tear that engine down. So every worker's first act is:

```csharp
var prev = Interlocked.Exchange(ref s_lastWorker, Thread.CurrentThread);
if (prev != null && prev != Thread.CurrentThread && prev.IsAlive
    && !prev.Join(_predecessorJoinMs))
{
    Interlocked.CompareExchange(ref s_lastWorker, prev, Thread.CurrentThread);
    PadForge.Engine.SdlDiagLog.WriteLine(
        $"SENSA predecessor join timed out after {_predecessorJoinMs} ms, worker quitting");
    return; // finally reports Stopped.
}
Volatile.Write(ref _engineStarted, 1);
```

The predecessor's teardown lands before the successor inits, never after. `SensaHapticsService.s_lastWorker` (`SensaHapticsService.cs` line 119) is static because the engine it protects is process-wide.

The join is bounded at 10 seconds (`DefaultPredecessorJoinMs`). That is long past any bring-up the provider completes and short enough that a wedged one costs a single wait. On the deadline the successor hands the slot back to the straggler and quits without starting its engine, because starting over a live predecessor is the exact handoff fault the join exists to prevent: that predecessor's `Har.Quit` would tear the engine down underneath it. An unbounded join blocked every later worker and leaked one thread per start.

`SensaHapticsTests.Service_NextWorkerWaitsForAStragglingPredecessor` holds a worker in `BeforeProviderInit`, stops it, starts a second service, and asserts the second worker waits for the first to exit. `Service_GivesUpOnAWedgedPredecessorInsteadOfBlockingForever` keeps the first worker parked past a shortened deadline and asserts the second quits without starting its engine or making a provider attempt, and reports `Stopped`.

The `finally` runs on every exit path, faults included (`SENSA worker fault: {type}`), and reports `Stopped` last.

### The host runs it

`PeripheralOutputHost.SensaLifecycle` (`PeripheralOutputHost.cs` line 289) decides when a worker exists. It runs on every link pass, every 500 ms or sooner when devices change:

- The row is linked (online, with its `sensa` path), it is assigned (`SettingsManager.SlotOrders.GetIdentityPlayerNumber` answers above 0), and no worker runs: the host creates a service, subscribes its report, starts it, and logs `PERIPHERAL Sensa worker started (row assigned)`.
- A worker whose thread ended on its own while the row stays assigned, because `HAR.dll` did not load, `AddParametricEffect` failed, or a straggling predecessor kept the slot, is stopped and started again after `SensaRestartMs` (30000), the worker's own provider retry, so a missing engine does not spin. The state reads `Waiting` meanwhile, and the host logs `PERIPHERAL Sensa worker ended on its own, starting again later`.
- The row leaves its last virtual controller, or goes offline: the host stops the worker (`PERIPHERAL Sensa worker stopped (row unassigned)`), which stops the engine's events and releases the provider, and the state goes to `Idle`.

Only the current worker reports. The report closure drops a state from a service the host has already replaced, and the host unsubscribes it before it disposes a worker, so a stopped worker's last word never lands after its successor's. The closure maps `Active` to `BackendState.Connected` and every other state to `Waiting` through `PeripheralOutputs.SetBackendState` (`PeripheralOutputs.cs` line 254).

---

## The row's level

Step 2 writes the level. The row is a haptic peripheral (`PeripheralOutputs.TakesHaptics` (`PeripheralOutputs.cs` line 186)), so `InputManager.ApplyForceFeedback` (`InputManager.Step2.UpdateInputStates.cs` line 671) makes its force-feedback cache on first use, runs each slot's rumble through the row's own Force Feedback settings on that slot, takes the strongest across the slots it is on, and folds trigger rumble into the motors. On a change it hands the result to `PeripheralOutputs.SetMotors` (`PeripheralOutputs.cs` line 303), which stores the stronger motor over 65535. The engine's silence edges (stop, focus suspend and the crash quiesce) zero the level through `PeripheralOutputs.SilenceHaptics` (`PeripheralOutputs.cs` line 352), and the next Step 2 pass sends again the level a game still asks for.

The worker reads it through `SensaHapticsService.RowAmplitude` (`SensaHapticsService.cs` line 150), which is `PeripheralOutputs.AmplitudeOf` for the row's id, every `tickMs` (default 16), clamps it to 0..1, and calls `SetEventIntensity` only on change. Intensity is the whole translation: one effect, one target, one amplitude. There is no stereo targeting and no pitch mapping.

---

## The status line

The Force Feedback tab's line comes from `PeripheralRouteText.Haptics` (`PeripheralRouteText.cs` line 20):

| Condition | Line |
|---|---|
| The row has its path and the state is not `Waiting` | `Pad_ForceFeedback_RouteSensa`: "Rumble plays on your Razer Sensa HD devices through Razer Synapse." |
| The row has its path and the state is `Waiting` | `Pad_ForceFeedback_RouteSensaWaiting`: "Waiting for Sensa HD Haptics in Razer Synapse 4. Set the device’s Haptic Source to Sensa HD Games in Synapse." |
| The row's record says haptics and the row has no path, in an x64 process | `Pad_ForceFeedback_RouteSensaWaiting` |
| The same in an ARM64 process | `Common_NotAvailableOnArm64` |

`SensaServiceState` (`SensaHapticsService.cs` line 10) keeps its four values, `Stopped`, `WaitingForRuntime`, `Active` and `Unsupported`, and the host folds them into the backend state as above. An ARM64 process never opens the row, so its line comes from the record alone.

---

## Persistence and migration

There is no switch. The row is a device like any other: its assignments and its Force Feedback settings per virtual controller persist with the settings and ride profiles as entries.

The Dashboard's Razer Sensa section and its switch are gone. `AppSettingsData.EnableSensaHaptics` (`SettingsService.cs` line 6704) and the profile's `bool?` opinion, `ProfileData.EnableSensaHaptics` (`SettingsService.cs` line 7675), are read once by `PeripheralSwitchMigration` and never written, since `ShouldSerializeEnableSensaHaptics` returns false on both. `PeripheralSwitchMigration.Switches` (`PeripheralSwitchMigration.cs` line 49) lists the switch, and `PeripheralSwitchMigration.Run` (`PeripheralSwitchMigration.cs` line 193) turns one that was on into an assignment of the Razer Sensa row:

- In the live settings when the active profile's opinion, else the global value, was on.
- In the default profile's stored state, while a named profile is active, and in each stored profile, each by its own opinion, else the global value.
- In a profile file exported before #494 and imported on its own (`PeripheralSwitchMigration.MigrateImported` (`PeripheralSwitchMigration.cs` line 63)), by its own opinion.

The row goes to the first created virtual controller in display order, the slot with the smallest displayed player number (`PeripheralSwitchMigration.FirstDisplayedSlot` (`PeripheralSwitchMigration.cs` line 70)). A topology with no created slot gets nothing. The row's record is created offline when the file has none (`PeripheralSwitchMigration.NewRowRecord` (`PeripheralSwitchMigration.cs` line 170)), so the assignment exists before the row first opens. Every opinion is cleared once read, so the migration runs once per file. Where the engine cannot load, the switch is not `Available`: nothing is assigned and the switch only clears.

---

## Diag lines

| Line | When |
|---|---|
| `PERIPHERAL Sensa worker started (row assigned)` | The host started a worker |
| `PERIPHERAL Sensa worker stopped (row unassigned)` | The row left its last virtual controller |
| `PERIPHERAL Sensa worker ended on its own, starting again later` | The worker ended while the row stayed assigned |
| `SENSA predecessor join timed out after {n} ms, worker quitting` | The predecessor join hit its deadline |
| `SENSA worker: calling HAR.Init` | Worker entry, after the predecessor join |
| `SENSA HAR.dll not found` | `DllNotFoundException` on `Init` |
| `SENSA HAR entry point missing` | `EntryPointNotFoundException` on `Init` |
| `SENSA HAR.Init => {bool}` | After `Init` |
| `SENSA HAR.Init failed or HAR.dll missing` | Worker returning without an engine |
| `SENSA AddParametricEffect returned -1` | Effect creation failed |
| `SENSA provider init => {bool}` | Every provider attempt |
| `SENSA worker fault: {exception type}` | Any unhandled exception in the worker |
| `CFG #494 migrated a global switch: RazerSensa row assigned to slot {n}` | The migration assigned the row in the live settings |
| `CFG #494 migrated a profile switch: RazerSensa row assigned to slot {n} in '{profile}'` | The migration assigned the row in a stored or imported profile |

---

## Tests

`SensaHapticsTests.cs` executes the real Razer-shipped engine end to end with no device present. This is the strongest hardware-free evidence available, and preferable to a mock wherever a vendor engine is separable from its device bridge.

| Test | What it proves |
|---|---|
| `RealEngine_FullLifecycle` | `Init`, effect creation, targeting, intensity, compute, and `Quit` against the shipped `HAR.dll` |
| `RealEngine_SurvivesReinit` | `Init` after `Quit`, the engine-restart path |
| `Provider_DegradesCleanlyWithoutSynapse` | The provider calls do not throw, with or without Synapse. When `ProviderInit` succeeds, `ProviderClean` returns true |
| `Service_StartsTheEngineAndDegradesWithoutRuntime` | The engine starts, a state is reported before `Stopped` (`WaitingForRuntime` on a bench without Synapse), and at least one provider attempt is made, with the level from an injected source |
| `Service_ReportsUnsupportedAndStartsNoWorkerWhereTheEngineCannotLoad` | The ARM64 branch: `Unsupported` raised once on the caller's thread, no worker |
| `Service_NextWorkerWaitsForAStragglingPredecessor` | The predecessor-join rule |
| `Service_GivesUpOnAWedgedPredecessorInsteadOfBlockingForever` | The bounded join: the successor quits without starting its engine |
| `TheWorkerStreamsTheRowsLevel_AndTheGlobalSwitchIsGone` | Source pins: the worker reads the row's level, the Step 5 lane and the Dashboard card are gone, the switch's two legs are read-only, and the host runs the worker only while the row is assigned |
| `TheKoreanStringsSpellHaptic` | The Korean Sensa strings spell haptic the way every other Korean string does |

`PeripheralOutputsTests.cs` covers the row's side:

| Test | What it proves |
|---|---|
| `PeripheralLinkingTests.TheSensaRowTakesInterhapticsOnlyWhereTheEngineRuns` | The row's `sensa` path, and none without the engine |
| `PeripheralLinkingTests.TheSensaRowOpensOnlyWithSynapseAndTheEngine` | Phase 1m's condition |
| `PeripheralLinkingTests.TheVendorRowsKeepTheirIdentities_AndTheirTypeFollowsTheirOutput` | The row's id, product GUID and device type |
| `PeripheralOutputsFacadeTests.TheSensaWorkerStreamsItsRowsLevel` | `RowAmplitude` reads what `SetMotors` stored |
| `PeripheralOutputsFacadeTests.TheForceFeedbackLineNamesTheDeviceItsRowReaches` | The Sensa lines, the ARM64 one included |
| `PeripheralSwitchMigrationTests` | The switch's migration: the ruling slot, each profile's own value, the live settings, the default topology, a row this PC cannot open, imported profiles |
| `PeripheralWiringTests.Step2HandsAHapticRowItsLevel_TheSoleWriterWay`, `EverySilenceEdgeSilencesThePeripheralsToo` | Step 2's branch and the silence edges, by source |

Live rendering on Sensa hardware was not verified by the maintainer.

---

*Last updated for PadForge 5.0.0.*
