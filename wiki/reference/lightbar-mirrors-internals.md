# Lightbar Mirrors: Internals

*How a game's lightbar write reaches Razer Chroma and Logitech LIGHTSYNC: the decoded field and its validity gate, the Chroma REST session, the LIGHTSYNC engine loader, and the thread and lifecycle contracts both services keep.*

The user-facing page is [Lightbar Mirrors and Sensa Haptics](../features/lightbar-mirrors.md). This one is for whoever has to change the code.

| File | Role |
|---|---|
| `PadForge.App/Common/Input/HMaestroVirtualController.cs` | The `OutputDecoded` handler that publishes the lightbar color |
| `PadForge.App/Services/ChromaLightbarService.cs` | The Chroma REST session and its worker |
| `PadForge.App/Services/LightsyncLightbarService.cs` | The LIGHTSYNC worker, the `ILogiLedNative` seam, generation and orphan handling |
| `PadForge.App/Services/LogiLedEngineNative.cs` | The production `ILogiLedNative`: registry probe, engine load, cdecl exports |
| `PadForge.App/Services/InputService.cs` | `StartChromaIfEnabled`, `StopChromaService`, `StartLightsyncIfEnabled`, `StopLightsyncService`, status marshaling |
| `PadForge.App/ViewModels/DashboardViewModel.cs` | `EnableChromaLightbar`, `ChromaStatus`, `EnableLightsyncLightbar`, `LightsyncStatus` |
| `PadForge.App/Services/SettingsService.cs` | The global and per-profile legs, `ApplyProfileServiceToggles`, `OnDashboardServiceToggleChanged` |
| `PadForge.App/MainWindow.xaml.cs` | The Dashboard autosave allowlist |
| `PadForge.Tests/ChromaLightbarTests.cs`, `LightsyncLightbarTests.cs`, `ProfileServiceToggleTests.cs` | The benches |

---

## The feed

No parser lives in the mirrors. Every Sony HIDMaestro profile declares a `lightbar` rgb24 field in its output report, and the codec decodes it with the per-transport offsets the profile carries. The `OutputDecoded` handler in `HMaestroVirtualController` reads that field and a family validity bit:

| Preset | Discriminator | Valid when |
|---|---|---|
| DualSense, DualSense Edge | `IsDualSenseVirtual` (Sony VID with the DualSense or Edge PID) | `validFlag1 & 0x04` |
| DualShock 4 | everything else on the Sony path | `validFlag0 & 0x02` |

A valid write calls `ChromaLightbarService.Publish(r, g, b)` and `LightsyncLightbarService.Publish(r, g, b)` back to back. Each `Publish` is one `Volatile.Write` of a packed `0x00RRGGBB` int into a static field (`s_publishedRgb`), initialized to `-1` for "no game write yet". The field is static so the callback needs no service reference and a disabled mirror costs one write per decode. Multiple live Sony slots resolve last-writer-wins. The worker polls the field, so the callback never blocks on I/O.

---

## Ownership and persistence

`InputService.StartChromaIfEnabled` and `StartLightsyncIfEnabled` run at engine start beside `StartExternalControlIfEnabled`, and again from the Dashboard `PropertyChanged` handler when the toggle flips. Each returns without starting when the toggle is off or `_inputManager` is null, and returns when a service is already live. The matching `Stop*Service` calls run at engine stop and on toggle-off. Each start writes a `CHROMA start?` or `LIGHTSYNC start?` diag line naming the toggle, engine, and live-instance state.

The service raises `StateChanged` on its worker. The owner marshals through `_dispatcher.BeginInvoke` and maps the enum onto the resx strings:

| Enum | Dashboard string |
|---|---|
| `ChromaServiceState.Connected` | `Dashboard_ChromaConnected` |
| `ChromaServiceState.WaitingForSynapse` | `Dashboard_ChromaWaiting` |
| `ChromaServiceState.Stopped` | `Common_Stopped` |
| `LightsyncServiceState.Connected` | `Dashboard_LightsyncConnected` |
| `LightsyncServiceState.WaitingForGHub` | `Dashboard_LightsyncWaiting` |
| `LightsyncServiceState.Stopped` | `Common_Stopped` |

Persistence has three legs per toggle:

| Leg | Where | Shape |
|---|---|---|
| Global | `AppSettings.EnableChromaLightbar`, `AppSettings.EnableLightsyncLightbar` | `bool`, default false |
| Per profile | `ProfileData.EnableChromaLightbar`, `ProfileData.EnableLightsyncLightbar` | `bool?`, null = no opinion |
| Autosave | `MainWindow.xaml.cs` Dashboard `PropertyChanged` allowlist | the property name |

The nullable leg is the Dashboard rule stated 2026-09-02: a plain `bool` deserializes to false in every profile saved before the field existed, and the first profile switch turned the mirror off. `SettingsService.ApplyProfileServiceToggles(profile)` applies only a non-null leg, under `_applyingServiceToggles` so the apply never records itself. `OnDashboardServiceToggleChanged` records a user change into the active named profile. The snapshot refresh writes a leg only when it is already non-null. No snapshot builder invents an opinion, so the default snapshot and a Save As copy start with none. `ProfileServiceToggleTests` pins each of these: old XML reads as null, null leaves the toggle, apply does not author, and the runtime mirrors never invent an opinion.

---

## Razer Chroma

### The REST session

Synapse serves the Chroma REST API on `http://localhost:54235` (`ChromaLightbarService.DefaultEndpoint`). The endpoint is constructor-injectable because the production port is machine-global and a test that talked to it would reach a real Synapse.

| Step | Call | Body | Notes |
|---|---|---|---|
| Register | `POST {endpoint}/razer/chromasdk` | `InitBody` | The app-info JSON: title `PadForge`, description, author `hifihedgehog` with contact `https://padforge.org`, `device_supported` listing all six categories, category `application`. The response carries `sessionid` and `uri`. |
| Heartbeat | `PUT {uri}/heartbeat` | none | Every 1000 ms (`heartbeatMs`). The session dies after 15 seconds without a command. The PUT has no body, matching Colore's no-data overload. A non-success status breaks the loop and re-registers. |
| Effect | `PUT {uri}/{category}` | `{"effect":"CHROMA_STATIC","param":{"color":N}}` | One PUT per category, in the order keyboard, mouse, headset, mousepad, keypad, chromalink. PUT applies at once. POST would create an effect id for later application. |
| Close | `DELETE {uri}` | none | Bounded to one second, best effort. |

URIs are joined by string concatenation. The session URI has no trailing slash, and `new Uri(base, relative)` would replace its last segment.

### Color framing

The Chroma integer is BGR: `R + (G << 8) + (B << 16)`. `ToBgr(int rgb)` converts the packed `0x00RRGGBB`:

```csharp
internal static int ToBgr(int rgb)
    => ((rgb >> 16) & 0xFF) | (rgb & 0xFF00) | ((rgb & 0xFF) << 16);
```

`ChromaLightbarTests.ToBgr_MatchesTheChromaWireFormat` pins the vectors.

### Result codes

The REST server answers HTTP 200 with a `result` integer even when it rejects an effect, so `SendStaticAsync` reads the body. `TryReadResult` requires a JSON object with a numeric `result`. Anything else is a rejection.

| Result | Treatment |
|---|---|
| `0` | Accepted |
| `1167` (`ResultDeviceNotConnected`) | Accepted. No device sits behind that category. A mirror addressing all six categories counts it as fine. |
| Any other value, an unparsable body, or a non-success status | Rejected |

A rejection in one category does not stop the remaining categories. `SendStaticAsync` returns true only when every category accepted, and only then does the loop advance `lastSent`. A rejected color is retried on the next poll instead of being held until the game writes a new one. The first rejection of a push is logged once per distinct `category result=code` pair (`_lastRejectLogged`), cleared when a push is accepted in full.

### Timing and retry

| Constant | Value | Purpose |
|---|---|---|
| `heartbeatMs` | 1000 | Heartbeat cadence |
| `pollMs` | 100 | How often the worker reads `s_publishedRgb` |
| `retryMs` | 30000 | Wait after a failed or dropped session |
| `DefaultHttpTimeoutMs` | 5000 | `HttpClient.Timeout` |

`HttpClient` signals its own timeout as `TaskCanceledException`, an `OperationCanceledException` subclass. The init call catches it with `when (ct.IsCancellationRequested)`, so only a Stop leaves the loop. A slow init (a cold Synapse answering late) stays on the retry path and reports `WaitingForSynapse` instead of `Stopped`. `ChromaLightbarTests.SlowInit_IsRetriedNotStopped` pins it.

### Diag lines

| Line | When |
|---|---|
| `CHROMA start? enabled=... engine=... live=...` | Every start attempt |
| `CHROMA state=...` | Every state transition |
| `CHROMA effect rejected: {category ...}, retrying on the next poll` | First rejection per distinct category and code |

---

## Logitech LIGHTSYNC

### The shim

The official SDK ships games `LogitechLedEnginesWrapper.dll`. Its entire loader, proven by PE import and string-table inspection of the committed binaries in the cloned references, is: read the default value of `HKLM\SOFTWARE\Classes\CLSID\{a6519e67-7632-4375-afdf-caa889744403}\ServerBinary`, `LoadLibraryW` the LED engine G HUB or LGS registered there, and `GetProcAddress` the undecorated cdecl `LogiLed*` names. `LogiLedEngineNative` does the same from managed code, so PadForge redistributes nothing of Logitech's. The lighting functions are the family the shim resolves by identical name with no translation.

Two cautions for anyone re-verifying: the registry path is the wrapper's only embedded wide string, so a byte-level grep for the ASCII form false-negatives. And the key is read from HKLM's 64-bit view, the same view Aurora and Artemis read.

### `TryLoad`

| Step | Failure detail |
|---|---|
| Open `ServerBinaryKey`, read the default value | `ServerBinary key absent` |
| `File.Exists(path)` | `engine missing: {path}` |
| `FileVersionInfo.FileDescription` must equal `Logitech Gaming LED SDK` (`EngineFileDescription`, Aurora's validation) | `engine description '...' unexpected` or `engine version info unreadable` |
| `LoadLibraryExW(path, 0, LOAD_WITH_ALTERED_SEARCH_PATH)` (`0x8`), so the engine's own directory joins its dependency resolution | `LoadLibrary failed ({error}) for {path}` |
| Resolve the three required exports | `required LogiLed exports missing` (the module is freed) |

### Exports

| Export | Required | Delegate | Notes |
|---|---|---|---|
| `LogiLedInit` | yes | `byte ()` | Fallback when `InitWithName` is absent |
| `LogiLedSetLighting` | yes | `byte (int r, int g, int b)` | Percent 0-100 per channel |
| `LogiLedShutdown` | yes | `void ()` | |
| `LogiLedInitWithName` | no | `byte (IntPtr ansiName)` | ANSI `char*`, called with `"PadForge"` via `StringToHGlobalAnsi`. Old engines carry 13 exports and lack it. |
| `LogiLedSetTargetDevice` | no | `byte (int target)` | `LogiDeviceTypeAll = 7` (MONOCHROME 1, RGB 2, PERKEY_RGB 4). Absent counts as success. |
| `LogiLedSaveCurrentLighting` | no | `byte ()` | Absent counts as success. |
| `LogiLedRestoreLighting` | no | `byte ()` | Absent is skipped. |

Every delegate is `[UnmanagedFunctionPointer(CallingConvention.Cdecl)]`. The official header's manglings carry `YA` in both bitnesses, so cdecl on x64 and x86 alike. Returns are one-byte C++ `bool`, marshaled as `byte` and compared `!= 0`. Both C# reference wrappers declare a four-byte `BOOL` there and carry that width mismatch silently. `Unload` nulls every delegate before `FreeLibrary`, so a stray call lands on a null check instead of a freed code page.

### Percent scaling

The engine takes whole percent. `ToPercent` rounds, never truncates:

```csharp
internal static int ToPercent(int channel)
    => (int)Math.Round(Math.Clamp(channel, 0, 255) * 100.0 / 255.0);
```

Aurora truncates and loses up to a percent per channel. `LightsyncLightbarTests.ToPercent_RoundsAndClamps` carries vectors that discriminate rounding from truncation (2 to 1, 130 to 51).

### The session

`LoopAsync` runs on a thread-pool task and makes every native call itself.

| Phase | What happens | Timing |
|---|---|---|
| Presence gate | `SoftwarePresent()` scans for `lghub_agent`, `lgs`, or `LCore`. Absent: report `WaitingForGHub`, wait, loop. No engine load happens on a machine without the software. | `retryMs` 30000 |
| Presence settle | On the first pass after the host appeared, wait before touching the engine. Init immediately after a G HUB start succeeds but does nothing. | `presenceSettleMs` 5000 |
| Load and init | `TryLoad`, then `Init`. A refused init unloads and retries. | `retryMs` on failure |
| Init settle | Logitech's own guidance, via Aurora: wait between init and the first lighting call. | `settleMs` 100 |
| Arm | `SetTargetAll`, `SaveCurrent`, report `Connected`. | |
| Stream | Poll `s_publishedRgb`. Send when the color changed or `livenessMs` elapsed since the last send. `SetTargetAll` is re-asserted before every send because the target mask is sticky process-global state. | `pollMs` 100, `livenessMs` 5000 |
| Fail streak | Three consecutive false returns from `SetLighting` log `LIGHTSYNC send failing, reinitializing` and break to teardown. A dead G HUB announces itself only through failing calls, and the periodic re-send is what surfaces them while the game holds one color. | |
| Teardown | `RestoreAndShutdown` (restore first, then shutdown, each swallowed), then `Unload`. Not stopping: report `WaitingForGHub`, wait `retryMs`, loop. | `stopWaitMs` 3000 on Stop |

There is no keep-alive in the SDK. A set color persists.

### Generation token and orphans

Native calls are unbounded. `Init` during a G HUB cold start can sit for the 14 seconds Artemis waits out. `Stop` cancels, waits `stopWaitMs`, and when the wait expires it publishes the task into `s_orphan`, logs `LIGHTSYNC stop timed out after ... ms, worker orphaned inside the SDK`, and returns. The owner disposes and recreates the service on re-enable, so the orphan belongs to a dead instance.

Two static fields make that safe. `s_generation` increments on every `Start`, and each worker captures the value it started under. `Superseded(generation)` is true once a newer Start exists. A superseded worker drops its `StateChanged` reports (its closure targets the Dashboard the live instance now owns) and skips `RestoreAndShutdown` at both teardown sites, since `LogiLedShutdown` is process-global and would kill the newer session. It still unloads its own module handle. The next worker's first act is to wait for `s_orphan` to complete before loading the engine, reporting `WaitingForGHub` and logging `LIGHTSYNC waiting for the orphaned worker of the previous session to leave the SDK` while it does, then clears the slot with a `CompareExchange`. `LightsyncLightbarTests.OrphanedWorker_NeverShutsDownOrReportsOverTheNewSession` and `OrphanedStreamingWorker_SkipsRestoreShutdownAtThePostSessionTeardown` pin both teardown sites.

### Diag lines

| Line | When |
|---|---|
| `LIGHTSYNC start? enabled=... engine=... live=...` | Every start attempt |
| `LIGHTSYNC state=...` | Every state transition from a live worker |
| `LIGHTSYNC superseded worker dropped state=...` | A report an orphan would have made |
| `LIGHTSYNC load failed: {detail}` | `TryLoad` returned false |
| `LIGHTSYNC send failing, reinitializing` | Third consecutive failed send |
| `LIGHTSYNC stop timed out after {n} ms, worker orphaned inside the SDK` | Stop's wait expired |
| `LIGHTSYNC waiting for the orphaned worker of the previous session to leave the SDK` | A new worker found a live orphan |

---

## Thread and lifecycle contracts

| Contract | Chroma | LIGHTSYNC |
|---|---|---|
| Worker | `Task.Run(LoopAsync)` | `Task.Run(LoopAsync)` |
| Publisher | The HM `OutputDecoded` callback, one volatile write | Same callback, one volatile write |
| Native or network calls | All on the worker, through one `HttpClient` | All on the worker. Every reference serializes SDK calls, and the Rust binding wraps the whole API in a process mutex. |
| `StateChanged` | Raised on the worker. The owner marshals. | Raised on the worker, gated by `Superseded`. The owner marshals. |
| `Stop` | Cancel, wait 3000 ms, dispose the token source | Cancel, wait `stopWaitMs`, orphan on expiry |
| `Dispose` | `Stop`, then dispose the `HttpClient`. Idempotent through `_disposed`. | `Stop`. Idempotent through `_disposed`. |
| Second `Start` on a live instance | No-op (`_cts != null`) | No-op (`_cts != null`) |
| Session end on the server side | Heartbeat non-success breaks to `DELETE` and re-register | Three failed sends break to restore, shutdown, unload |

---

## Tests

Neither service was run against Razer or Logitech software by the maintainer. The benches stand in.

| Test file | What it drives |
|---|---|
| `ChromaLightbarTests.cs` | An in-process `HttpListener` fake Chroma server. Pins the init body field for field, six category PUTs with exact JSON and BGR integers, change-only sending, heartbeat cadence, refused and slow init on the retry path, a rejected PUT retried on the next poll, and the teardown DELETE. `FeedAndSiblingContracts` counts the persistence legs against the web-controller sibling. |
| `LightsyncLightbarTests.cs` | A scripted `ILogiLedNative` fake. Pins init order, percent conversion, change-only plus liveness sends, no-software retry without an engine load, refused-init unload, fail-streak re-init and recovery, and both orphan teardown sites. |
| `ProfileServiceToggleTests.cs` | The nullable profile legs for all four service toggles, and `LightbarMirrors_OneSection_OneGlyph_TwoRows` for the Dashboard shape. |

---

*Last updated for PadForge 4.4.0.*
