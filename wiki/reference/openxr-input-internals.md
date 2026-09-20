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

A runtime DLL exports exactly one entry point, `xrNegotiateLoaderRuntimeInterface`, which hands back `xrGetInstanceProcAddr`. Everything else is a function pointer obtained from that. PadForge performs that handshake itself, about a hundred lines, instead of linking the loader. Two reasons, both structural:

**Runtime selection.** PadForge runs elevated. The Khronos loader deliberately ignores `XR_RUNTIME_JSON` in a high-integrity process (`OpenXR-SDK`, `src/common/platform_utils.hpp`, `PlatformUtilsGetSecureEnv`). Choosing the manifest ourselves makes the runtime choice per-process by construction, with nothing configured globally and nothing to put back afterward. That is what the **OpenXR Runtime** dropdown sets, and it is why picking one never disturbs the machine's active runtime.

**Isolation.** The loader inserts every API layer installed on the machine into the calling process. A background client that only reads poses has no use for them, and a user's layers belong to their game.

---

## Finding the runtimes

`OpenXrRuntimeCatalog` reads `HKLM\SOFTWARE\Khronos\OpenXR\1`:

- The `ActiveRuntime` value is the machine's default manifest path.
- The `AvailableRuntimes` subkey lists every registered manifest.

Each manifest is a JSON file naming the runtime's library. The catalog parses them and marks the one matching `ActiveRuntime` as the default, which is what *System Default* selects. Nothing here writes: the machine's active runtime belongs to whatever set it.

---

## The session

`OpenXrSession.TryCreate` takes a manifest path and walks the whole setup. Two extensions matter.

**`XR_MND_headless` is required.** It is what lets a session run with no graphics binding and no swapchain, so PadForge can read poses without a window, a compositor surface, or a game being open. A runtime that does not offer it is refused, and the status line says *This runtime cannot supply a background session*. SteamVR's OpenXR runtime carries it, which is why the whole path is testable without a headset.

**`XR_KHR_win32_convert_performance_counter_time` is requested when present.** `XrTime` is nanoseconds on a clock the runtime picks, not a clock the caller knows. Pose requests carry a timestamp, so PadForge has to express "now" in the runtime's terms. When the extension is there, the conversion is exact. Without it the value is derived from the performance counter, which is an approximation whose error grows with uptime.

---

## The action set

`OpenXrActions` creates one action per control and suggests a binding for each interaction profile:

- `/interaction_profiles/oculus/touch_controller`
- `/interaction_profiles/valve/index_controller`
- `/interaction_profiles/khr/simple_controller`

The runtime picks whichever matches the attached hardware and reports how many profiles it accepted. Suggesting all three rather than detecting hardware is the OpenXR way round: the runtime knows what is attached and the application does not.

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

`OpenXrHeadPoseSource` owns a thread that creates the session, pumps events, and publishes poses. `Stop` joins it. The publish side is a lock around the latest sample. The read side is the poll thread's device sweep.

---

## Residual

Coexistence with VDXR while another OpenXR client is running has not been exercised on real hardware.

Test coverage is uneven and worth stating plainly. The device rows, the head-pose math, the row status text and the runtime picker have ordinary tests that run on every suite. The negotiation and manifest parsing are covered only by `OpenXrRuntimeProbeTests`, which is gated behind `PADFORGE_OPENXR_PROBE=1` and skips on a normal run, because it would otherwise start a runtime on the build machine. The action layer's thumbstick read is asserted by grepping `OpenXrActions.cs` for the assignment, not by exercising it.

---

## Related pages

- [Head Tracking](../features/head-tracking.md)
- [VR Controller Input](../features/vr-controller-input.md)
- [Head Tracking Internals](head-tracking-internals.md): the UDP and FreeTrack sources on the same device row.
- [Input Pipeline](input-pipeline.md)

---

*Last updated for PadForge 4.5.0.*
