# External Control Internals

*How a launcher or script drives profiles from outside PadForge: the named pipe, its security descriptor, the command grammar, the held-profile state machine, and the command-line form that maps onto it.*

This is the developer-side companion to the external control section of [Profiles](../guides/profiles.md). Issue #366, asked in discussion #363 by a Playnite plugin author who had been rewriting `PadForge.xml` around each launch.

---

## Files

| File | Role |
|---|---|
| `PadForge.App/Services/ExternalControlService.cs` | The pipe server. Accept loop, security descriptor, line framing. The executor is injected as `Func<string, string>` and the pipe name is a constructor parameter. |
| `PadForge.App/Services/InputService.cs` | `StartExternalControlIfEnabled` / `StopExternalControl`, `ExecuteExternalControlCommand` (the grammar), `ExternalActivate`, `ExternalDeactivate`, `NoteManualProfileSwitch`. |
| `PadForge.App/Services/ForegroundMonitorService.cs` | `CheckForegroundWindow` returns early while the pin is held. |
| `PadForge.App/Common/SettingsManager.cs` | `EnableExternalControl` (persisted opt-in) and `ExternalProfilePinActive` (runtime only). |
| `PadForge.App/App.xaml.cs` | `ParseProfileCommand`, the first-instance deferred apply, and the second-instance pipe forward. |
| `PadForge.App/Views/ProfilesPage.xaml` | The **Allow External Control by Launchers and Scripts** checkbox, under the auto-switch checkbox in the profile management card. |

Tests: `PadForge.Tests/ExternalControlTests.cs`.

---

## Why a pipe

PadForge is manifested `requireAdministrator` (`app.manifest`). A plain `PadForge.exe <args>` from an unelevated launcher pops UAC on every launch, which rules out command-line arguments as the primary interface. A named pipe created by the elevated process carries a Medium default mandatory label, so a Medium-integrity client can connect as long as the DACL allows it.

The pattern mirrors Lenovo Legion Toolkit's `LenovoLegionToolkit.WPF/CLI/IpcServer.cs` (cloned): an elevated WPF app serving `NamedPipeServerStreamAcl.Create` with an `AuthenticatedUserSid` rule, opt-in behind a settings flag, one request-response per connection in a loop. DS4Windows is the cautionary opposite, also cloned: its command lane is `WM_COPYDATA` and it never calls `ChangeWindowMessageFilter`, so once it runs elevated it goes deaf to unelevated senders.

---

## The server

`ExternalControlService.PipeName` is `PadForge.Control`. `CreateServer` builds:

| Parameter | Value |
|---|---|
| Direction | `InOut` |
| Instances | `MaxAllowedServerInstances` |
| Mode | `Byte` |
| Options | `Asynchronous` |
| Buffers | 0 in, 0 out |
| DACL | one rule: Authenticated Users, `ReadWrite`, Allow |

No Everyone, no anonymous. `ExternalControlTests.ThePipeGrantsAuthenticatedUsers` pins the SID and the right.

`Start` runs `AcceptLoop` on a task. Each iteration creates a fresh server stream, waits for one connection, reads one line, runs the executor, writes one line, and disposes the stream. One command per connection. A bad connection never kills the loop. `Stop` cancels the token, connects a throwaway client for 200 ms to nudge a server parked in `WaitForConnectionAsync` (it does not observe the token until a connection arrives), and waits up to 2 s for the loop.

Framing is plain UTF-8. `ReadLineAsync` reads a byte at a time up to 1024 characters, ends on `\n`, drops `\r`, and trims. `WriteLineAsync` appends `\n` and flushes. `ExternalControlTests.TheRequestReadIsCapped` pins the cap.

The server always answers, including on an empty line. An earlier guard skipped the write when the request was empty, and a client that sent a bare newline then blocked in its own read until the pipe closed, which reads as a hung launcher. The executor returning null or throwing yields `error internal`.

The pipe name is a constructor parameter because a pipe name is machine-global. A test that served the production name was answered by the running PadForge and failed carrying the real app's replies. Tests serve a name unique to the test and process.

---

## Lifecycle

The pipe serves while the engine is running, the same gate as the DSU server:

| Event | Effect |
|---|---|
| Engine start, opt-in on | `StartExternalControlIfEnabled` creates and starts the server. |
| Checkbox turned on, engine running | Same. With the engine stopped nothing starts, and the next engine start brings the pipe up. |
| Checkbox turned off | `StopExternalControl` disposes the server, clears the pin, invalidates the foreground cache. |
| Engine stop | `StopExternalControl`, same effects. |
| Reset to Defaults | Opt-in and pin both cleared. |

`ExternalControlTests.ThePipeStarterIsEngineGated` pins the gate.

---

## The grammar

`InputService.ExecuteExternalControlCommand` runs off the UI thread and marshals every state touch through the dispatcher. Verbs and replies are fixed ASCII, never localized, since this is a machine interface (`ExternalControlTests.TheGrammarIsNeverLocalized`). The first space splits verb from argument, so a profile name may contain spaces. The verb is lowercased.

| Request | Reply |
|---|---|
| `activate <profile name or id>` | `ok <name>` with the profile's stored name, or `error unknown-profile` |
| `activate` with no argument | `error empty` |
| `deactivate` | `ok default` |
| `query` | `ok <name> pinned`, `ok <name> unpinned`, or `ok default unpinned` |
| empty or whitespace line | `error empty` |
| anything else | `error unknown-command` |
| executor threw or returned null | `error internal` |

`ExternalActivate` resolves the argument by id first, then by case-insensitive name. It sets the pin before the switch so the foreground monitor cannot race the apply. If the target is already active it returns `ok <name>` without switching. Otherwise it saves the outgoing profile's state, sets `ActiveProfileId`, applies the profile, runs `ResetRuntimeStateForProfileSwitch` (the choke point every switch lane funnels through, which also resolves the [per-profile polling rate](settings-and-serialization.md#profiledata)), and updates the status bar. `ExternalDeactivate` clears the pin, invalidates the foreground monitor's cache, and if a named profile was active saves its state and applies Default.

---

## The held-profile state machine

`SettingsManager.ExternalProfilePinActive` is a static bool, never persisted (`ExternalControlTests.ThePinIsNeverPersisted`). While it is true, `ForegroundMonitorService.CheckForegroundWindow` returns before reading the foreground window, after the auto-switch enable check.

Without the pin the requester's case fails: focusing the game fires the foreground rule, or the no-match default revert, and undoes what the launcher chose. The pre-existing manual-override latch cannot substitute, because a different foreground match clears it by design.

| Transition | Where |
|---|---|
| Set | `ExternalActivate`, before the switch |
| Cleared by the script | `ExternalDeactivate` |
| Cleared by the user | `NoteManualProfileSwitch`, called ahead of a manual load from the Profiles page. The user outranks a script. |
| Cleared by lifecycle | `StopExternalControl` (checkbox off, engine stop), Reset to Defaults, app restart |

Whenever the pin drops, the monitor's dedup cache is invalidated (`InvalidateCache`), because it holds pre-pin state and a still-focused matched game must re-fire its rule on the next check. `ExternalControlTests.PinReleaseInvalidatesTheForegroundCache` and `AManualSwitchReleasesThePin` pin both halves.

The pin proof on the live bench needed a same-window positive control: with no pin, focusing the matched executable auto-switched and closing it reverted, so the monitor was demonstrably firing. With the pin held, the same open-and-close left the profile untouched.

---

## The command-line form

`App.ParseProfileCommand` maps arguments onto the same grammar:

| Argument | Command |
|---|---|
| `--profile "Name"` | `activate Name` |
| `--default-profile` | `deactivate` |

First instance: the command is stored as `PendingProfileCommand` and applied once at the tail of `InputService.Start`, directly in-process through `ExecuteExternalControlCommand`. That works with the pipe off, since the pipe is for driving an already-running instance. `ClearPendingProfileCommand` runs first so an engine restart does not re-apply it.

Second instance: `OnStartup` sees the single-instance mutex taken. With a profile argument present it forwards the command over the pipe (`TryForwardExternalCommand`, 2 s connect timeout), prints the reply to the console, and exits with no "already running" box. If the pipe is not being served (external control off) it prints `error not-connected`. `ExternalControlTests.ASecondInstanceForwardsInsteadOfNagging` and `TheCommandLineMapsOntoTheSameGrammar` pin it.

Because the exe is elevated, this form prompts UAC when called from a normal process. The docs steer launchers to the pipe and keep the exe form for elevated scripts and Task Scheduler jobs.

---

## Persistence

`AppSettingsData.EnableExternalControl`, `[XmlElement]`, default false. Every pre-#366 settings file deserializes to false, so the pipe stays off until asked (`ExternalControlIsOffUntilAsked`). The flag rides all four sibling persistence sites in `SettingsService`: load into the view model and `SettingsManager`, apply from the view model, build for save, and clear on Reset to Defaults (`TheOptInRidesEverySiblingSite`). The pin is not in the file.

---

## Related pages

- [Profiles](../guides/profiles.md): the user-side commands and the Playnite, LaunchBox, and PowerShell recipes.
- [Settings and Serialization](settings-and-serialization.md): `EnableExternalControl` in `AppSettingsData`.
- [Services Layer](services-layer.md): where `InputService` and `ForegroundMonitorService` sit.

---

*Last updated for PadForge 4.4.0.*
