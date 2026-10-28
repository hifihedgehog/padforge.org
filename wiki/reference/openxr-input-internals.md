# OpenXR Input Internals

*How PadForge reaches an OpenXR runtime, what it asks for, and why it does not use the Khronos loader.*

For the user-facing side see [Head Tracking](../features/head-tracking.md) and [VR Controller Input](../features/vr-controller-input.md).

The code lives in `PadForge.Engine/Common/OpenXr/`:

| File | Responsibility |
| --- | --- |
| `OpenXrRuntimeCatalog.cs` | Finds the installed runtimes by reading the registry and their JSON manifests. |
| `OpenXrInterop.cs` | The negotiation entry point, the structures, and the function-pointer delegates. |
| `OpenXrSession.cs` | Instance, system, session, reference space, event pump, pose reads. |
| `OpenXrActions.cs` | The action set, the suggested bindings, and the per-frame control reads. |
| `OpenXrHandState.cs` | The value type one hand's controls come back in. |
| `OpenXrHeadPoseSource.cs` | The thread that owns the session and publishes poses. |

The device rows are `PadForge.App/Common/Input/HeadTrackerDevice.cs` and `OpenXrHandDevice.cs`.

---

## No Khronos loader

A runtime DLL must export `xrNegotiateLoaderRuntimeInterface`, which hands back `xrGetInstanceProcAddr`. Everything else is a function pointer obtained from that. PadForge performs that handshake itself, about a hundred lines, instead of linking the loader. Two reasons, both structural:

**Runtime selection.** PadForge runs elevated. The Khronos loader deliberately ignores `XR_RUNTIME_JSON` in a high-integrity process (`OpenXR-SDK`, `src/common/platform_utils.hpp`, `PlatformUtilsGetSecureEnv`). Choosing the manifest ourselves makes the runtime choice per-process by construction, with nothing configured globally and nothing to put back afterward. That is what the **OpenXR Runtime** dropdown sets, and it is why picking one never disturbs the machine's active runtime.

**Isolation.** The loader inserts every implicit API layer installed on the machine into the calling process. A background client that only reads poses has no use for them, and a user's layers belong to their game.

---

## Finding the runtimes

`OpenXrRuntimeCatalog` reads `HKLM\SOFTWARE\Khronos\OpenXR\1`:

- The `ActiveRuntime` value is the machine's default manifest path.
- The `AvailableRuntimes` subkey lists every registered manifest.

Each manifest is a JSON file naming the runtime's library. The catalog parses them and marks the one matching `ActiveRuntime` as the default. *System Default* uses that runtime, or the first other registered runtime whose library is on disk when the default's library is missing. Nothing here writes: the machine's active runtime belongs to whatever set it.

A runtime registered only as `ActiveRuntime` drops out of the catalog once another runtime takes the default, because the catalog has no other way to find its manifest. The Dashboard picker still lists it while it is the saved choice, under its manifest's file name (`DashboardViewModel.Repopulate`), and the session reads a saved choice from its manifest path directly (`OpenXrSession.Choose`). The user page covers that case for SteamVR. The picker reads the catalog again each time the input is turned on, the same step that restarts the session.

---

## The session

`OpenXrSession.TryCreate` takes a manifest path, negotiates with the runtime and creates the instance. `TryCreateSession` asks for the headset and creates the session on it, and `DestroySession` takes a lost session down while the instance stays. `TryCreate` also takes an `again` flag, set for the ask the source makes on its own after a retired instance, and hands back what it read when no instance came of it. With the flag set it reads the given manifest alone, never the registered runtimes, and creates no instance on an OpenVR client library (`IsOpenVrClientLibrary`). An overload takes the library loader and the list of registered runtimes, which the tests replace. Two extensions matter.

**`XR_MND_headless` is required.** It is what lets a session run with no graphics binding and no swapchain, so PadForge can read poses without a window, a compositor surface, or a game being open. A runtime that does not offer it is refused, and the status line says *This runtime cannot supply a background session*. SteamVR's OpenXR runtime carries it, so negotiation, instance creation and the extension check run without a headset. The session itself needs one. `TryCreateSession` reads `XR_ERROR_FORM_FACTOR_UNAVAILABLE` from `xrGetSystem` as a headset that is away. On SteamVR that answer is final. On another runtime the source keeps the instance, asks again every 2 s (`RetryIntervalMs`) and reads the instance's events every 100 ms meanwhile (`WaitingPumpIntervalMs`).

No extension list Khronos has published for Meta's PC runtime, the one a Quest uses over Link, holds it. Khronos's [OpenXR-Inventory](https://github.com/KhronosGroup/OpenXR-Inventory) has lists for versions 1.82.0, 1.92.0, 1.104.0 and 1.205.0, ordinary and developer mode (`runtimes/meta_pc.json`, `runtimes/meta_pc_dev_mode.json`), and none for later versions. SteamVR's entry (`runtimes/valve_steamvr.json`, 2.14.4) holds it, and SteamVR's runtime works with a Quest over Link and Air Link, per the [VirtualDesktop-OpenXR wiki](https://github.com/mbucchia/VirtualDesktop-OpenXR/wiki). So a Quest on Link reads through SteamVR. That route has not been run with a headset.

**`XR_KHR_win32_convert_performance_counter_time` is requested when present.** `XrTime` is nanoseconds on a clock the runtime picks, not a clock the caller knows. Pose requests carry a timestamp, so PadForge has to express "now" in the runtime's terms. When the extension is there, the conversion is exact. Without it the value is derived from the performance counter, which is an approximation whose error grows with uptime.

---

## The action set

`OpenXrActions` creates one action per control and suggests a binding for each interaction profile:

- `/interaction_profiles/oculus/touch_controller`
- `/interaction_profiles/valve/index_controller`
- `/interaction_profiles/khr/simple_controller`

The runtime accepts the suggestions it can serve and binds whichever profile matches the attached hardware. PadForge counts the accepted suggestions and logs the number. Suggesting all three rather than detecting hardware is the OpenXR way round: the runtime knows what is attached and the application does not.

`Read` fills an `OpenXrHandState` per hand: the pose, the thumbstick as a vector2, the trigger and squeeze as floats, and four booleans.

---

## The device rows

Each hand is one `OpenXrHandDevice`, an `ISdlInputDevice` like any synthetic row.

**Axis layout.** Ten axes. The six pose axes come first and in the Head Tracker row's order, so a user who has mapped a head axis finds the hand's equivalent at the same index. The names differ: the head row says `Head Yaw` and the hand row says `Controller Yaw`. Then `Thumbstick X`/`Y`, then `Trigger` and `Grip`.

**Separate identities.** Left and right have different `InstanceGuid` *and* different `ProductGuid`. The instance seeds are `pfopenxrhand:left` and `pfopenxrhand:right`, the product seeds `pfopenxrhand-product:left` and `-product:right`. Sharing a product GUID would let offline-product adoption hand the left row the right row's mappings after a row is deleted and re-created.

**Vendor and product IDs.** VID `0x1209`, the pid.codes open-source vendor ID, with PIDs `0x2874` (left) and `0x2875` (right).

**Silence returns to rest.** A sample older than `SilenceMs` (1000) returns every axis to rest and releases every button. This is the Head Tracker row's failsafe, for the same reason: a controller that goes to sleep or drops out of tracking mid-game must not leave a stick held. One that is set down and still tracked keeps reporting, and its axes follow it.

**Own-vocabulary rows answer no Any Device source.** `AnswersAnyDeviceSources` is false, the rule [discussion #431](../features/devices.md) established. A row whose axes are named "Controller Yaw" must not satisfy a mapping asking a generic "Axis 0".

**Trigger and Grip are unipolar.** `IsUnipolarActivatorSource` in `InputManager.Step3.MappingSetEval.cs` returns true for axes 8 and 9 on a `VrController`, so an Axis Past Threshold activator reads them as resting at zero rather than at center. Without that branch the activator engages the moment it is saved, which is [discussion #443](../features/mappings.md) on a new device type.

---

## Per-axis ranges

The six pose axes take a shared rotation range and a shared translation range, and each axis can pin its own. The stored value is the pin, and zero means "follow the shared range". The getter returns the pin, never the resolved range, so a box the user typed 45 into reads 45 and a box they never touched reads 0 whatever the shared range is set to. Reading back the resolved value would make a zero impossible to display and would rewrite the user's field behind them.

The ranges are applied in the shared state fill, so every source that feeds these axes gets them.

---

## Threading

`OpenXrHeadPoseSource` owns a thread that creates the session, pumps events, and publishes poses. On a runtime other than SteamVR the same thread waits for a headset, replaces a session the runtime lost, and asks for a new instance after the runtime retired one. [Head Tracking Internals](head-tracking-internals.md#the-status-line) has the rules. `Stop` joins it for up to 2 s. It cancels under the gate every state write of the loop takes (`Show`), so a thread that outlives the join changes nothing the source shows. The publish side is a lock around the latest sample. The read side is each row's `GetCurrentState`, called from the poll thread's input-state step (`InputManager.Step2.UpdateInputStates.cs`).

---

## Residual

Coexistence with VDXR while another OpenXR client is running has not been exercised on real hardware.

What SteamVR does when it quits is read from its `vrclient_x64.dll` (SteamVR 2.17.10), not seen in a run. On its quit event it asks each session to exit, and an instance with no session gets `XrEventDataInstanceLossPending` with a loss time an hour out. That library is also the OpenVR client library, which keeps one client per process for OpenVR and OpenXR callers alike. It never moves a session to `XR_SESSION_STATE_LOSS_PENDING`. For those three reasons the source keeps no instance without a session on SteamVR and creates none on its own (`OpenXrSession.IsOpenVrClientLibrary`).

Test coverage is uneven and worth stating plainly. The device rows, the head-pose math, the row status text and the runtime picker have ordinary tests that run on every suite. `OpenXrSessionScriptedRuntimeTests` runs the real `OpenXrSession` on a scripted runtime in every suite run: the manifest choice, the instance, the session, the event pump and the recovery. `OpenXrSessionRecoveryTests` plays the source's loop over a scripted link the same way. Loading a runtime's library and the negotiation call itself (`OpenXrSession.LoadRuntime`) are covered only by `OpenXrRuntimeProbeTests`, which is gated behind `PADFORGE_OPENXR_PROBE=1`. Without it, each test returns early and reports a pass, because running it would start a runtime on the build machine. A test reaches no runtime: the test assembly closes `VrRuntimeGate` for its whole process (`VrRuntimeOffLimits`), so the opener the app uses (`OpenXrSession.TryCreate`), its library loader (`LoadRuntime`) and the resolver that loads SteamVR's `openvr_api.dll` throw in a test. Only the runtime probe opens the gate, by its name, and only with the variable set. In the app the gate is always open. On a `Failed` or `NoRuntime` source the probe fails with the source's last log line, which names the call and the runtime's answer. The action layer's thumbstick read is asserted by grepping `OpenXrActions.cs` for the assignment, not by exercising it.

---

## Related pages

- [Head Tracking](../features/head-tracking.md)
- [VR Controller Input](../features/vr-controller-input.md)
- [Head Tracking Internals](head-tracking-internals.md): the UDP and FreeTrack sources on the same device row.
- [Input Pipeline](input-pipeline.md)

---

*Last updated for PadForge 5.2.0.*
