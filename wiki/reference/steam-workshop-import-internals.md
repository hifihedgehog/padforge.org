# Steam Workshop Config Import Internals

*The `PadForge.SteamWorkshop` assembly (anonymous Steam clients, VDF parser, typed config model, translator, cache), the engine substrate it rides on (the abstract Gamepad descriptor family, generic per-source Sensitivity, the macro-action family), and the app-side dialog, materializer, and provenance plumbing.*

This is the developer-side companion to [Steam Workshop Config Import](../guides/steam-workshop-import.md) (the user guide) and issue #9.

---

## Files

| File | Role |
|---|---|
| `PadForge.SteamWorkshop/ISteamWorkshopGate.cs` | The opt-in gate every client enforces at construction. |
| `PadForge.SteamWorkshop/Api/SteamWorkshopClient.cs` | SteamKit2 anonymous CM session + `PublishedFile.QueryFiles`. |
| `PadForge.SteamWorkshop/Api/SteamStoreClient.cs` | Anonymous HTTPS game search and app details. |
| `PadForge.SteamWorkshop/Api/SteamCommunityClient.cs` | Creator persona and avatar. |
| `PadForge.SteamWorkshop/Api/SteamRemoteStorageClient.cs` | Batched per-file Workshop metadata. |
| `PadForge.SteamWorkshop/Api/SteamUgcDownloader.cs` | VDF blob download from the config CDN. |
| `PadForge.SteamWorkshop/Api/SteamArtworkClient.cs` | Store artwork with fallback chains and stale-serve. |
| `PadForge.SteamWorkshop/Api/SteamHttp.cs` | The shared `HttpClient` (15 s timeout, `PadForge/{version}` User-Agent). |
| `PadForge.SteamWorkshop/Vdf/VdfParser.cs`, `VdfNode.cs`, `VdfSyntaxException.cs` | Original recursive-descent VDF parser. |
| `PadForge.SteamWorkshop/Model/SteamInputConfig.cs` (+ Group, Preset, Input, Activator, Binding) | Typed Steam Input config model. |
| `PadForge.SteamWorkshop/Translation/ConfigTranslator.cs` | The translator. |
| `PadForge.SteamWorkshop/Translation/TranslationReport.cs`, `TranslationStatus.cs`, `TranslationOptions.cs`, `TranslatedProfile.cs` | Report, status enum, options, neutral output shape. |
| `PadForge.SteamWorkshop/Translation/PhysicalSlotResolver.cs`, `SteamInputVkTable.cs`, `XInputTargetTable.cs` | Steam slot → PadForge source resolution, key and pad-target tables. |
| `PadForge.SteamWorkshop/Cache/SteamWorkshopCache.cs`, `CacheCategory.cs` | File-system cache, TTLs, dual budgets, LRU. |
| `PadForge.SteamWorkshop/Local/LocalWorkshopConfigStore.cs` | Read-only legacy fallback from the local Steam install. |
| `PadForge.App/Views/WorkshopBrowseDialog.xaml(.cs)` | The browse dialog. |
| `PadForge.App/Services/WorkshopProfileMaterializer.cs` | `TranslatedProfile` → `ProfileData`. |
| `PadForge.App/MainWindow.xaml.cs` | Dialog entry, import sink, cache clear, update check. |
| `PadForge.App/Services/SettingsService.cs` | `EnableCommunityConfigLookup`, `ShowLegacyWorkshopConfigs`, `SteamWorkshopSource`. |
| `PadForge.Engine/Common/Mapping/SourceCoercion.cs` | Gamepad alias table, generic Sensitivity, pressure read, the flick stick and touchpad pointer families. |
| `PadForge.Engine/Menus/MenuDefinitionEntry.cs` (+ `MenuEvaluator.cs`, `MenuSelectionMath.cs`) | The menu model translated menus land on. See [Menus](../guides/menus.md) and the engine pages. |
| `PadForge.SteamWorkshop.Tests/` | Parser, client, cache, and translation tests: `TranslationEdgeTests` plus per-wave suites (`WaveOneA`, `WaveTwoA`, `WaveThree`, `WaveFour`, `WaveFourB`, `WaveFourC`) and 30 golden fixtures. |

The assembly targets `net10.0-windows`, references `PadForge.Engine`, and carries a single direct NuGet dependency: `SteamKit2` 3.4.0 (LGPL 2.1). protobuf-net (3.2.56) and ZstdSharp.Port (0.8.7) arrive transitively through it.

---

## The opt-in gate

`ISteamWorkshopGate` exposes one member, `IsCommunityConfigLookupEnabled`. `DelegateSteamWorkshopGate` adapts a `Func<bool>` (the app passes `() => settings.EnableCommunityConfigLookup`). `SteamWorkshopGuard.EnsureEnabled` throws `InvalidOperationException` ("Community config lookup is disabled in PadForge settings...") when the gate is off.

Every client constructor calls the guard first: `SteamWorkshopClient`, `SteamStoreClient`, `SteamCommunityClient`, `SteamRemoteStorageClient`, `SteamUgcDownloader`, `SteamArtworkClient`. With the Settings toggle off, no client can even be built. That is the defense-in-depth layer under the UI-level gating.

---

## Clients

| Client | Transport | Endpoint | Notes |
|---|---|---|---|
| `SteamWorkshopClient` | SteamKit2 CM session (WebSocket over 443) | CM servers via SteamKit2 directory fetch | The only Steam-protocol surface. |
| `SteamStoreClient` | HTTPS GET | `store.steampowered.com/api/storesearch/`, `/api/appdetails` | Game search, app details. |
| `SteamCommunityClient` | HTTPS GET | `steamcommunity.com/profiles/{steamId}?xml=1` | Persona name + avatar URLs. Tolerant XML parse, never throws on missing fields. |
| `SteamRemoteStorageClient` | HTTPS POST | `api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/` | Batched form post (`itemcount`, `publishedfileids[i]`). |
| `SteamUgcDownloader` | HTTPS GET | caller-supplied `file_url` (config CDN) | 10 MB cap, size and HTML-page validation. |
| `SteamArtworkClient` | HTTPS GET | `cdn.cloudflare.steamstatic.com/steam/apps/{appId}/{file}` | Fallback chains, magic-byte image check, 16 MB cap. |

All REST clients share `SteamHttp.Client`: one lazy `HttpClient`, 15-second timeout, `PadForge/{version}` User-Agent, case-insensitive JSON. No API key, no cookies, no tokens anywhere. Creator avatar images are the one fetch outside these clients: the browse dialog downloads the `avatars.fastly.steamstatic.com` URLs from the profile XML on its own `HttpClient` (same timeout, same User-Agent) and caches them under the art budget.

### SteamWorkshopClient: the anonymous CM session

Configuration: `SteamConfiguration.Create(b => b.WithProtocolTypes(ProtocolTypes.WebSocket).WithDirectoryFetch(true))`. WebSocket rides port 443, which passes firewalls that block Steam's classic CM ports. `EnsureLoggedOnAsync` connects, then `SteamUser.LogOnAnonymous()`, with 15-second timeouts on both stages (`ConnectTimeout`, `LogonTimeout`) and a `SemaphoreSlim` making the logon idempotent. A background task pumps `CallbackManager.RunWaitCallbacks` every 100 ms and never lets an exception escape.

Search goes through `SteamUnifiedMessages` → `PublishedFile.QueryFiles` with:

- `appid = 241100` (`ControllerConfigsAppId`): the query filters on the *consumer* app, Steam's controller-configs bucket. This is `appid`, not `creator_appid`.
- `filetype = 15` (`MatchingFileTypeControllerBindings`, Steamworks' `k_PFI_MatchingFileType_ControllerBindings`): the QueryFiles matching-file-type enum, a different enum from the per-item `EWorkshopFileType.ControllerBinding = 12`. Without it the query returns nothing.
- a required `app` kv-tag (`required_kv_tags`, key `app`, value = the target game's app id): every config carries it, and it scopes the 241100 bucket down to one game.
- `requiredtags` for the dialog's controller filter chips,
- `return_vote_data`, `return_tags`, `return_kv_tags`, `return_short_description`, `return_metadata`, `return_details`, `return_playtime_stats = 30`.

The shape was grounded live against the CM (smoke harness, 2026-07-13): Skyrim SE returns 155,694 items under `appid = 241100` + `filetype = 15` + the `app` kv-tag, and zero under `appid = game`.

The browse dialog requests `EPublishedFileQueryType.RankedByVote` (30 per page for the list, a 1-per-page probe for the shelf's config counts). Defaults on `SearchAsync` are `RankedByTotalUniqueSubscriptions`, page 1, 30 per page.

Client-side politeness: an in-memory single-flight map keyed by cache key, and a 100 ms minimum spacing between outbound requests (`MinRequestSpacing`). Responses cache 24 h as protobuf bytes.

### SteamUgcDownloader validation

Rejects an empty `file_url` (`ArgumentException`, the legacy marker), a declared or streamed size past `MaxVdfBytes` (10 MB, matching the parser cap), a size that misses the expected `file_size`, and an HTML error page masquerading as a VDF (leading-tag sniff). Strips a UTF-8 BOM before decoding.

### SteamArtworkClient

Two fallback chains, tried in order until a fetch succeeds:

- Portrait: `library_600x900.jpg` → `capsule_616x353.jpg` → `header.jpg`
- Hero: `library_hero.jpg` → `header.jpg`

Reads ride `TryGetBytesStaleOk` with the 7-day art TTL. A fresh hit returns immediately. A stale hit re-fetches, and on `HttpRequestException` / `IOException` / timeout serves the stale copy instead, so offline browsing keeps its art. A definitive CDN 404 returns null and lets the chain degrade. Every payload passes a magic-byte check (JPEG, PNG, GIF, WEBP) and a 16 MB cap before caching. Art is hotlinked at runtime and never rehosted or bundled.

---

## VDF parser

`VdfParser.Parse` / `TryParse` is an original recursive-descent implementation. Hard limits: `DefaultMaxDepth = 32` nesting levels, `MaxInputBytes = 10 MB` (measured as UTF-8 bytes). It rejects binary VDF up front: a NUL first byte or the literal `VBKV` magic throws "Binary VDF (VBKV) is not supported."

Handled: quoted and unquoted tokens, duplicate keys (preserved in order, exposed via `Multi(key)` since real configs repeat `"group"` and `"preset"`), `//` line and `/* */` block comments, escape sequences (`\"`, `\\`, `\n`, `\t`, `\r`, with unknown escapes passing through literally), empty objects and values, embedded Unicode, a leading BOM, and Valve's `[$WIN32]`-style conditionals (skipped).

`VdfNode` is null-safe: the indexer returns a `Missing` sentinel instead of null, key lookup is case-insensitive, and typed accessors (`AsInt`, `AsDouble`, `AsBool`) parse with `InvariantCulture`. `VdfSyntaxException` carries offset, line, and column.

---

## Typed model

`SteamInputConfig.FromVdf` accepts the document root or the `controller_mappings` node directly and validates structure into `SteamInputConfig` → `SteamInputGroup` / `SteamInputPreset` → `SteamInputInput` → `SteamInputActivator` → `SteamInputBinding`. Malformed structure throws `SteamInputConfigException`.

The version gate rejects anything below 3 with the exact reason: "Steam Input config version {N} (pre-2017 schema). Translator targets version 3 only." A missing or non-numeric `version` is also rejected. Current Workshop configs are version 3, and the grammar has not moved.

---

## ConfigTranslator

`Translate(config, options)` produces a `TranslatedProfile`: two `MappingSet`s (`XboxMappingSet`, `KbmMappingSet`), a macro list, a menu list (`Menus`, `MenuDefinitionEntry` objects from `PadForge.Engine.Menus`), a name and description, slot-demand flags (`NeedsXboxSlot`, `NeedsKbmSlot`), and a `TranslationReport`. It never touches `ProfileData`. That is the materializer's job. The Xbox demand flag is true for rows (identity bindings and matched-side analog passthroughs included, since they emit rows now), activators, or macros whose triggers read the Xbox slot's combined output. A macro riding a device-free `InputDevice` trigger (paddle, touchpad, gyro) demands no Xbox slot on its own. An `Identities.Count` clause remains as belt-and-braces for the row-cap edge. The KbM flag is true for its own rows or activators, and for menus when no Xbox slot is demanded, so every import with a menu has a slot to carry it. The materializer creates only the demanded slots, Xbox first when present so macro trigger pad indices hold, so a pure keyboard layout imports as a single KbM pad. It stamps `MappingSet.Authoritative` on both sets it places and clones each menu onto every created slot's `MappingSet.Menus`.

`TranslationOptions` has exactly four fields: `FileId` (feeds deterministic layer names), `PreferredLanguage` (default `"english"`, for localized title fallback), `ProfileNameOverride`, and `IncludedPresetIds`, the preset filter the dialog's chips re-run translation with (null means all).

### Translator version history

`TranslationReport.CurrentTranslatorVersion` is **26**. Each report stamps the version it was produced under, and the summary digest leads with it. Every bump is summarized in the doc comment above the constant in `TranslationReport.cs`, which is the authoritative changelog. The bumps:

| Version | Commit | What it added |
|---|---|---|
| 1 | `1087f9bb` | Initial translator: authoritative sets, identity rows, matched-side analog passthroughs, split routing, presets and layers, MOUSE_POSITION warp macros. |
| 2 | `8667de96` (wave 1) | `single_button` and `gyro_to_mouse` modes, Steam Controller digital-trigger switch members, `#token` localized titles, inner deadzone, `set_led` lightbar and Guide-LED macros, `Long_Press` layer carries, the named-drop vocabulary (haptic, response curve, gyro button mask, activator delay, interruptible, player number, lizard mode, scroll gesture). |
| 3 | `86fd8ef6` (wave 2) | `Long_Press` key and button macros, xinput `hold_repeats` turbo macros, activator `toggle` latches (`ToggleVcButton` / `ToggleKey`), `camera_reset` as gyro recenter, `mouse_region` cursor-clamp macros. |
| 4 | `6196fa89` (wave 3) | Device-free `InputDevice` macro triggers (retired most `NoDeviceFreeTrigger` skips), DS4 and DualSense trackpad halves as region-windowed sources, `four_buttons`-on-trackpad quadrant collapse, per-row touchpad mouse sensitivity (retired `TouchpadTuningNotPerRow`). |
| 5 | `caa347dc` (wave 4a) | `flickstick` mode as the Flick Stick source on `KbmMouseX`, with the group's `sensitivity` landing on `ParamFlickCountsPer360`. |
| 6 | `495c8cc0` (wave 4b) | Trackpad `mouse_region` as Clean absolute `Touchpad {p} Pointer X/Y` rows (region geometry on `ParamPointerCenter` / `ParamPointerExtent`). Retired `AbsoluteMouseApproximated`: `absolute_mouse` is relative in Steam too, so the relative rows are faithful and Clean. |
| 7 | `b006ee7e` (wave 4c) | `radial_menu` and `touch_menu` as first-class `MenuDefinitionEntry` menus with the on-screen overlay. Retired the `RadialMenuNeedsOverlay` / `TouchMenuNeedsOverlay` skips and the two-cell touch-spot approximation. |
| 8 | | Group axis inversion: `invert_x` / `invert_y` flip the emitted mouse-axis source's Invert flag on every mode whose engine read honors it. |
| 9 | | `mouse_joystick` emits right-stick axis rows instead of KbM mouse. Unmerged `CHANGE_PRESET` lowers to a Latch of the target layer. |
| 10 | | Gap closure G1-G15: activator `haptic_intensity` as RumblePulse macros, `button_capture` to the raw SDL MISC1 source, `2dscroll` onto one-shot swipe gestures. |
| 11 | | Response-curve channel: Steam's curve cluster (`curve_exponent` preset and friends) lands on emitted stick axis pairs as per-source params. |
| 12 | | Stick-hosted swipe and wheel: `2dscroll` on a stick lowers each `dpad_*` member's one-shot bindings onto tap macros on the member's wedge read. |
| 13 | | Vocabulary census against Steam's own serializer: `LSTICK_`/`RSTICK_` direction params lower to bipolar thumb-axis rows. |
| 14 | | Self-arming gesture reads: `TrackpadFeatureRequired` retires whole, authoritative slots' mapped gesture descriptors self-enable the gesture gate. |
| 15 | | The swipe / flick skip family closes: gyro-hosted `2dscroll` lowers onto one-shot tap macros on signed gyro-rate halves. `MouseWheelTap` action lands. |
| 16 | | `mouse_delta` builds on the new one-shot `MouseNudge` macro through the engine's accumulate-and-flush mouse lane. `CycleTapList` lands. |
| 17 | | `Double_Press` activators on any host lower to macros on the engine's new DoublePress trigger. Stick `mouse_region` engages on a deflection ring. |
| 18 | | The response-cluster and gate/latch waves: the curve/range shaping seam widens to every analog lane, click gates ride `GateDescriptor`, and the latch/turbo family completes (`ToggleMouseButton` / `ToggleVcAxis` / `RepeatVcAxisWhileHeld` / `ToggleWheel`). |
| 19 | | Audit-2 semantics: the gyro-hosted `mouse_joystick` rotation matrix stays orthogonal against the yaw-frame flip, `mouse_wheel` `hold_repeats` lowers to repeats. |
| 20 | | `CHANGE_PRESET` sentinel ids (32766 next / 32765 previous) lower as one Cycle activator through every action set in authored order. |
| 21 | | Menu cell icons carry: authored icon names ride `MenuItemDefinition.Icon`, resolved against the local Steam client's binding-icon art. |
| 22 | | The Skyrim notes: `gyro_ratchet_button_mask` lowers onto a slot-level clutch lane grounded per bit against Steam's `k_eGamepadButtonBitMask`. |
| 23 | | `gyro_button` engage arm gains the full bitmask enum, indexing the same table as the ratchet grounding. |
| 24 | | The mass-sweep top four: `button_macro0..4` resolve as the device's extra buttons (bits 32-39, capability-gated). |
| 25 | | Wild-corpus round 2: serializer-vocabulary switch members resolve, `always_on_action` lowers onto the constant-true source with `LayerMask` scoping, radial menus host on the physical dpad / face diamond, `deadzone_shape` lands per source. |
| 26 | | Wild-corpus round 3: the gravity-lean channel ("Gyro Lean X/Y"), capsense reads, trackpad edge members on the finger-ring read, trackpad-hosted flickstick, hotbar grids, In-Menu Sensitivity, and the precise `MobileTouchSurfaceOnly` / `ChordWithoutPartner` classes. |

Versions 8 through 26 land across the 4.1.0 cycle. Commit hashes for each ride the doc comment in `TranslationReport.cs`, one block per bump.

The Nintendo face-button folding (`7cfc8be3`, labels folded to positions for Switch-authored configs via `PhysicalSlotResolver.UsesNintendoLabels`) did not bump the version: it changed slot resolution, not report shape.

### Split-config routing

Every binding lands by nature, not by a user-chosen slot. `xinput_button` targets go to the Xbox set (`ButtonA`, `DPadUp`, `LeftTrigger`, `LeftThumbAxisX`...). Key, mouse-button, mouse-move, and scroll targets go to the KbM set (`KbmKey##`, `KbmMBtn0-4`, `KbmMouseX/Y`, `KbmScroll`, `KbmScrollH`). One config routinely fills both.

### Identity bindings, matched analogs, and authoritative sets

An `xinput_button` binding whose resolved source already maps to that target through the device automap (no soft-press, no click gate) is an identity. Every identity emits an explicit row. In `Finalize`, an identity whose `(slot, layer, target)` gained a real row from some other binding is re-absorbed onto that row as an extra source. The rest materialize as rows of their own. Both paths report Clean `RowEmitted`.

Matched-side implicit analog outputs get the same treatment. A `trigger` group with no `output_trigger` redirect passes the analog pull through in Steam without any binding object, and a `joystick_move` group with no `output_joystick` redirect passes the stick through the same way. `Finalize` materializes each as an explicit full-axis row ("Gamepad LeftTrigger" → `LeftTrigger`, "Gamepad LeftStickX/Y" → `LeftThumbAxisX/Y`, right side likewise), one Clean `RowEmitted` per row. The analog source lands first, so a trigger's click identity absorbs behind it, and such rows keep the axis default combine (max-abs) rather than Sum, keeping the pull a clean analog read. These rows only materialize when the Xbox side is in play through bindings at all: a pure keyboard/mouse config keeps zero Xbox rows and no Xbox pad, and a macro-only config keeps its zero-row set on the whole-set passthrough.

The rows must be explicit because imported sets are authoritative (`MappingSet.Authoritative`, stamped by the materializer). `MergeMappingSetsFromLegacy` contributes nothing to an authoritative set when a device is assigned: no sources injected into existing rows, no automap rows appended. Departed-device source cleanup and the empty-row drop still run. That merge was the double-mapping bug: the imported rows spelled a binding out, then the assigned device's auto-mapped legacy descriptors landed on top and the input fired twice.

One deliberate exception: a set with zero rows (a macro-only import) still rides the whole-set legacy passthrough at runtime. The assigned pad automaps wholesale and the macros trigger from that combined output.

Older imports carried two report entries this design retires: the per-preset Clean `DefaultAutomapPassthrough` aggregate (identities emitted zero rows then) and the Partial `AutomapAlsoActive` warning (the automap no longer asserts alongside an authoritative set, so there is nothing to warn about). Both reason keys stay renderable for reports serialized before the change.

### Presets and layers

The first preset by id becomes the literal layer `"Base"`. Every other preset becomes `"Layer_{FileId}_{presetId}"`. An `active modeshift` group becomes `"Layer_{FileId}_{presetId}_MS_{slotToken}_{groupId}"`. Activator emission (`ShiftActivator.Mode` strings are exact):

| Steam Input construct | ShiftActivator |
|---|---|
| `mode_shift` | `Mode = "Hold"` (`"Toggle"` when the activator carries `toggle = 1`), `InheritUnmapped = true` |
| `controller_action HOLD_LAYER` | `Mode = "Hold"` (`"Toggle"` with `toggle = 1`), `InheritUnmapped = true` |
| `controller_action ADD_LAYER` | `Mode = "Toggle"`, `InheritUnmapped = true` |
| `controller_action REMOVE_LAYER` | No activator. Partial `RemoveLayerApproximated` (approximated as toggle-off). |
| `controller_action CHANGE_PRESET` | `Mode = "Custom"` with `JumpToLayer` |
| Same-input CHANGE_PRESET pairs | Merged to `Mode = "Cycle"` (`CycleLayers` ordinal-sorted, `CycleIncludeBase` when a jump targeted Base) |
| `Long_Press` layer switch | The carrying activator gains `DelayMs` from `long_press_time` (v2). |

Activators duplicate onto whichever mapping set(s) actually contain the layer's rows. `Kind` is always `"Button"` (trigger pulls gate at `AxisThreshold = 0.5`). Since wave 4c, activators evaluate with their true slot index, so an activator descriptor can read slot-scoped families such as menu-item fires.

### Group and activator settings honored

> **Currency note (4.1.0).** This table records the v7-era state. Waves v18 through v26 consumed most of the drops listed below: click gates now ride `MappingSource.GateDescriptor` on every source, the latch/turbo family completed, response curves land on every analog lane, and the haptic / double-press / ratchet clusters all build. The authoritative per-setting status is the version changelog above plus `ConfigTranslator.cs` at HEAD.

The v1 translator read six setting keys. The waves widened that considerably:

| Setting | Handling |
|---|---|
| `sensitivity` | Mouse-output groups: `ratio = clamp(sens / baseline, 0.05, 20.0)` with `StickMouseBaseline = 80`, `TrackpadMouseBaseline = 50`. Stick family → per-source `Sensitivity`; gyro family → `GyroSensitivity`; touchpad-finger family → per-row `Sensitivity` (since v4). On a `flickstick` group it is Steam's Dots Per 360° and lands on `ParamFlickCountsPer360`. On a menu it is In-Menu Sensitivity, dropped as Partial `MenuTuningDropped`. |
| `hold_repeats` + `repeat_rate` | `key_press` → a `RepeatKeyWhileHeld` macro. `xinput_button` → a `RepeatVcButtonWhileHeld` turbo macro (since v3), except identity and trigger-axis targets where the row keeps and the repeat drops (Partial `RepeatDropped`). `repeat_rate` clamps 10–1000 ms into the macro interval. |
| `toggle` | On an activator: a `ToggleVcButton` / `ToggleKey` latch macro, or `Mode = "Toggle"` on a layer carry (since v3). No latch for the output → Partial `ToggleDropped`. |
| `long_press_time` | Carries into the activator `DelayMs` on long-press layer switches. |
| `deadzone_inner_radius` | Group deadzone. Also feeds a menu's `EngageDeadzonePercent`. |
| `requires_click` | Trackpad d-pad wedges gain an AND-combined `"Touchpad {p} Click"` gate source. Dropped (Partial `ClickGateDropped`) when a second source joins the target. |
| `output_trigger` | Crossed side emits an axis row to the opposite trigger. Matched side emits its own full-axis passthrough row via the `Finalize` matched-analog pass, with any click identity absorbed behind the analog source. |
| `output_joystick` | Crossed stick emits `{dst}ThumbAxisX/Y` rows. Matched stick emits its own axis pair via the matched-analog pass. Trackpad-as-stick emits them as Partial `TrackpadFeatureRequired`. |
| `mouse_region` geometry | `position_x/y`, `scale`, `sensitivity_horiz_scale`, `sensitivity_vert_scale` land on the pointer-source region params (trackpad host) or the clamp-macro geometry (stick and gyro hosts). `teleport_*` and `edge_binding_*` → Partial `MouseRegionTuningDropped`. |
| Menu keys | `touchmenu_button_fire_type` (clamped 0–3), `touch_menu_position_x/_y`, `touch_menu_scale`, `touch_menu_opacity`, `touch_menu_show_labels`, `touch_menu_button_count`. |
| Named drops | `haptic_intensity` aggregates into Partial `HapticIntensityDropped`. Response-curve and range keys → `ResponseCurveNotSupported`. `gyro_button` masks → `GyroButtonMaskDropped`. `delay_start` / `delay_end` → `ActivatorDelayDropped`. `interruptable` → `InterruptibleDropped`. Flick stick's `edge_binding_radius`, `mouse_smoothing`, `rotation`, `transition_time` → `FlickStickTuningDropped`. |

`trackball`, `mouse_dampening_trigger`, and double-tap timing are still not referenced and fall through silently (double-press activators are skipped whole).

### MOUSE_POSITION coordinates

The translator keeps Steam's normalized 16-bit space: `NormalizedX/Y = clamp(x, 0, 65535)`. The materializer converts to primary-monitor physical pixels: `round(n / 65535 * (screen - 1))` clamped to the screen, using `GetSystemMetrics(SM_CXSCREEN/SM_CYSCREEN)`. The result feeds a `MoveMouseToScreenPosition` macro action (one cursor warp on fire).

### Determinism and caps

Same config + same options = identical output, asserted by test. Ordering: presets ascending by id; group entries by `(slotToken, groupId)`; inputs by name; final rows by `(Kbm, Base-first, Layer, Target)` ordinal; activators by `(LayerMask, Descriptor, Mode)` with a dedup key. Constants: `MaxRowsPerSlot = 5000` per slot class (exceeding it emits Error `RowCapExceeded` and stops adding rows for that slot), `MaxReferenceDepth = 4` for `reference`-mode group chains (cycles and overruns emit Error `ReferenceCycle`). All emitted sources carry an empty `DeviceGuid`.

---

## TranslationReport

`TranslationStatus`: `Clean = 0`, `Partial = 1`, `Skipped = 2`, `Error = 3`. Entries carry `Status`, `ReasonKey`, `ReasonArgs`, `SourcePath`, `Binding` (raw binding text), and `Emitted` (an unlocalized diagnostic trace like `KbmKey57 <- Touchpad 0 DPadUp`). The report also counts rows, macros, menus (`MenuCount`), and activators per set, and `ToSummaryString()` renders the provenance digest (`v7 rows:x0+k46 macros:2 menus:1 layers:3 clean:48 partial:6 skipped:23 errors:0`).

Reason keys are resx keys in the `Workshop_Tr_*` namespace, resolved at display time so the manifest localizes. Early waves kept retired keys defined for old reports, but from v15 onward a wave that retires a key DELETES the key and its locale strings (each deletion is named in the version changelog above), so the live vocabulary is exactly the `Workshop_Tr_*` set in `Strings.resx` at HEAD. A report serialized under an older version can reference a deleted key, which renders as the raw key name. The family taxonomy below is the v7-era snapshot and reads as historical structure, not the current key list:

### Emission (Clean)

| Key | Trigger |
|---|---|
| `Workshop_Tr_RowEmitted` | A mapping-row source emitted normally. |
| `Workshop_Tr_ShiftLayerEmitted` | A shift activator emitted (`layer: {name}`). |
| `Workshop_Tr_MenuEmitted` | A radial or touch menu emitted (`{count}` bound cells). v7. |
| `Workshop_Tr_MacroEmitted` | A macro emitted on a device-free `InputDevice` trigger with no feature gate. v4. |
| `Workshop_Tr_ToggleLatchEmitted` | An activator `toggle` latch emitted (`latches {output}`). Clean when descriptor-triggered, Partial when it rides the Xbox combined output. v3. |

### Approximations and caveats (Partial)

| Key | Trigger |
|---|---|
| `Workshop_Tr_TrackpadFeatureRequired` | Trackpad wedge / trackpad-as-stick / touch-spot rows that need a touchpad feature enabled (`Touchpad joystick output` or `Touchpad touch spots`). |
| `Workshop_Tr_SoftPressApproximated` | `soft_press` becomes a plain press threshold (a 15% deadzone on an analog trigger pull). Sources that need a touchpad feature report `TrackpadFeatureRequired` instead. |
| `Workshop_Tr_MacroTriggerViaXboxOutput` | A macro whose trigger reads the Xbox slot's combined output (autofire, key-on-release, or cursor warp on a standard pad button). |
| `Workshop_Tr_RepeatDropped` | `xinput_button` with `hold_repeats` on an identity or trigger-axis target: row kept, turbo dropped. Other targets get a turbo macro instead (v3). |
| `Workshop_Tr_RemoveLayerApproximated` | `REMOVE_LAYER` approximated as toggle-off. |
| `Workshop_Tr_ClickGateDropped` | A `requires_click` gate abandoned when a second source joined the target. |
| `Workshop_Tr_LongPressKeyTap` | A `Long_Press` key: taps at the threshold where Steam holds until release. v3. |
| `Workshop_Tr_ToggleDropped` | An activator `toggle` with no latch for that output. v3. |
| `Workshop_Tr_CameraResetApproximated` | `camera_reset` approximated as a gyro recenter. v3. |
| `Workshop_Tr_MouseRegionApproximated` | A stick- or gyro-hosted `mouse_region` approximated as a centered cursor clamp while the surface is held (`{scale}%`, region center `{x}%, {y}%`). v3. Trackpad hosts go Clean via the pointer family instead (v6). |
| `Workshop_Tr_MouseRegionTuningDropped` | `teleport_*` / `edge_binding_*` mouse-region keys dropped. v3. |
| `Workshop_Tr_TouchQuadrantApproximated` | `four_buttons` cells share the hosting touch surface (no per-cell zones). v4. |
| `Workshop_Tr_TrackpadHalfApproximated` | A binding hosted on one half of the touchpad where PadForge reads the whole pad. v4. |
| `Workshop_Tr_MenuIconsDropped` | Menu cells with icons render text labels (`{count}` cells). v7. |
| `Workshop_Tr_MenuTuningDropped` | In-menu `sensitivity` and other unsupported menu tuning. v7. |
| `Workshop_Tr_FlickStickTuningDropped` | Flick stick keys with no PadForge equivalent (`edge_binding_radius`, `mouse_smoothing`, `rotation`, `transition_time`). v5. |
| `Workshop_Tr_SetLedDefaultApproximated` | A restore-default `set_led` approximated as clearing the override. v2. |
| `Workshop_Tr_HapticIntensityDropped` | Per-config aggregate of dropped haptic-feedback settings (`{count}` bindings). v2. |
| `Workshop_Tr_ResponseCurveNotSupported` | Response curve and range settings dropped (`{keys}`). v2. |
| `Workshop_Tr_GyroButtonMaskDropped` | `gyro_button` engage masks dropped (gyro engage is per pad in PadForge). v2. |
| `Workshop_Tr_ActivatorDelayDropped` | `delay_start` / `delay_end` press delays dropped. v2. |
| `Workshop_Tr_InterruptibleDropped` | A non-interruptible press behaves as a normal press. v2. |
| `Workshop_Tr_MissingModeShiftGroup`, `Workshop_Tr_MissingPreset`, `Workshop_Tr_ActivatorInputNotSupported`, `Workshop_Tr_ShiftLayerEmpty`, `Workshop_Tr_PresetHasNoActivator` | Layer and preset-switch diagnostics: dangling references, activator sources that cannot drive a layer (gesture-gated wedges, gyro), layers that produced no rows, presets nothing switches to. |

### Skipped

| Key | Trigger |
|---|---|
| `Workshop_Tr_GameActionsNotSupported` | Per-preset aggregate of `game_action` bindings (`{count}` in-game actions, Steam-only). |
| `Workshop_Tr_SteamSystemAction` | `SCREENSHOT`, `SYSTEM_KEY_1`, `SHOW_KEYBOARD`. |
| `Workshop_Tr_PlayerNumberActionNotSupported`, `Workshop_Tr_LizardModeActionNotSupported` | Steam-client actions with no equivalent. v2. |
| `Workshop_Tr_ScrollWheelModeNotSupported` | The `scrollwheel` group mode (circular scrolling). Its `click` member still translates. |
| `Workshop_Tr_ScrollGestureModeNotSupported` | The `2dscroll` directional-swipe mode. v2. |
| `Workshop_Tr_MenuEmpty` | A menu with no bound cells. v7. |
| `Workshop_Tr_MenuSurfaceNotSupported` | A menu hosted on anything but a stick or trackpad (`{host}`). v7. |
| `Workshop_Tr_FlickStickSurfaceNotSupported` | A trackpad-hosted `flickstick` (PadForge flick stick reads a physical stick). v5. |
| `Workshop_Tr_LongPressNotSupported` | Residual only: a `Long_Press` that is not a key, button, or layer switch (for example a trigger-axis target). |
| `Workshop_Tr_DoublePressNotSupported`, `Workshop_Tr_ReleaseActivatorNotSupported` | Unsupported activators. A `release` on a mouse or pad button skips. On a `key_press` it becomes an on-release macro instead. |
| `Workshop_Tr_EdgeInputNotSupported` | An `edge` input on a non-trigger slot. |
| `Workshop_Tr_NoDeviceFreeTrigger` | Residual only: a `mouse_region` hosted on a stick or gyro with nothing to engage it. Paddle-, touchpad-, and gyro-hosted macros translate via device-free triggers since v4. |
| `Workshop_Tr_UnknownBindingType`, `Workshop_Tr_UnknownKey`, `Workshop_Tr_UnsupportedKey`, `Workshop_Tr_UnknownMouseButton`, `Workshop_Tr_UnknownXInputButton`, `Workshop_Tr_UnknownPhysicalInput`, `Workshop_Tr_UnknownGroupMode`, `Workshop_Tr_UnknownActivatorType`, `Workshop_Tr_UnsupportedControllerAction` | Unknown-token family: forward-compat catch-alls so translator drift degrades to labeled skips, never a crash. |

### Errors

| Key | Trigger |
|---|---|
| `Workshop_Tr_MissingGroup` | A preset references an absent group id. |
| `Workshop_Tr_ReferenceCycle` | `reference` chain cycles, dangles, or exceeds depth 4. |
| `Workshop_Tr_RowCapExceeded` | A slot class would pass 5000 rows. |

### Legacy, render-only

These keys are no longer emitted. They stay defined so reports serialized under older translator versions keep rendering:

| Key | Retired | Why |
|---|---|---|
| `Workshop_Tr_DefaultAutomapPassthrough` | v1 cycle | Identity bindings emit explicit rows now. |
| `Workshop_Tr_AutomapAlsoActive` | v1 cycle | Authoritative sets retired the condition. |
| `Workshop_Tr_TouchpadTuningNotPerRow` | v4 | Touchpad mouse sensitivity applies per row now. |
| `Workshop_Tr_AbsoluteMouseApproximated` | v6 | `absolute_mouse` is relative in Steam too. The relative rows are faithful and report Clean. |
| `Workshop_Tr_TouchMenuNeedsOverlay`, `Workshop_Tr_RadialMenuNeedsOverlay` | v7 | Menus import as on-screen menus. |
| `Workshop_Tr_MouseRegionNotSupported` | v3/v6 | Mouse regions route to pointer rows, clamp macros, or the `NoDeviceFreeTrigger` residual. |

One constant (`TriggerThresholdApproximated`) is defined and localized but has never been emitted. `mouse_wheel` scroll bindings are not skipped. They emit `KbmScroll`/`KbmScrollH` rows. Empty bindings and `EMPTY_SUB_COMMAND` drop silently.

---

## Cache

`SteamWorkshopCache` roots at `%LOCALAPPDATA%\PadForge\SteamWorkshopCache` with two independent budgets: `DefaultGeneralBudgetBytes = 50 MB` (everything but art) and `DefaultArtBudgetBytes = 60 MB` (art). Categories:

| Category | Directory | TTL | Budget group |
|---|---|---|---|
| `Games` | `games/` | 24 h | General |
| `Search` | `search/` | 24 h | General |
| `Vdf` | `vdf/` | none (immutable per file id + `time_updated`, evicted by LRU only) | General |
| `Personas` | `personas/` | 7 d | General |
| `Art` | `art/` | 7 d, stale-ok | Art |

Writes are atomic (temp file + `File.Move` overwrite under a lock), then the budget is enforced by deleting least-recently-accessed files first. TTL freshness rides last-write time, LRU recency rides last-access time, both stamped from an injectable clock for tests. `TryGetBytes` deletes an expired entry. `TryGetBytesStaleOk` (the art path) reports staleness but keeps the entry so the artwork client can serve it on network failure. Keys sanitize to `[0-9A-Za-z._-]` or fall back to a SHA-256 hex name. `Clear()` backs the Settings button.

---

## Local legacy fallback

`LocalWorkshopConfigStore` is the no-network path for configs whose `file_url` is absent (pre-2017) or dead. Read-only, never writes. Resolution order:

1. Steam install path from `HKCU\Software\Valve\Steam\SteamPath`, falling back to `HKLM\SOFTWARE\WOW6432Node\Valve\Steam\InstallPath`.
2. Library roots from `steamapps/libraryfolders.vdf` (or `config/libraryfolders.vdf`), parsed with the same VDF parser. Both the current object shape and the pre-2021 flat shape are handled, and non-numeric keys are skipped.
3. Per library: `steamapps/workshop/content/241100/{publishedFileId}/`, preferring `controller_configuration.vdf` (SteamPipe-manifest items) and falling back to `*_legacy.bin` (pre-manifest UGC, ordinal-smallest name for determinism). Both payloads are text VDF.

Files past the parser's 10 MB cap are refused. The layout was grounded against Valve's Workshop implementation guide and a live install (86/86 subscribed items readable, 45 valid v3 configs).

---

## Provenance and the update check

`SteamWorkshopSource` (in `SettingsService.cs`, serialized as the `<SteamWorkshopSource>` element on `ProfileData.WorkshopSource`) carries `PublishedFileId`, `AppId`, `GameName`, `Title`, `TimeUpdated` (unix seconds at import), `ImportedAt` (UTC), and `TranslationSummary` (the report digest). Null on every non-imported profile.

Provenance is identity-scoped, like `Name` and `Id`. The runtime snapshot copiers exclude it by design: guard comments pin that at `SettingsService.UpdateActiveProfileSnapshot` and the `InputService` snapshot copy-back (both `SaveActiveProfileState` and its 250 ms autosave twin). `SnapshotCurrentProfile` never captures it, which is what makes a **Save As** fork user-authored with no Workshop link. Compaction preserves it (`Compaction_PreservesProvenance`).

The update check (`OnCheckWorkshopUpdates` in `MainWindow.xaml.cs`) short-circuits with a status line when the opt-in is off, collects profiles with a nonzero `PublishedFileId`, and issues one batched `GetPublishedFileDetails` POST over the distinct ids. Only per-item `Result == 1` responses count (removed or banned items stay unreported). Stale means `fresh.time_updated > stored TimeUpdated`, strictly. Clean runs end in a status line. Stale runs raise a message box whose primary button reopens the browse dialog. It is not surfaced anywhere else in the UI: provenance is persisted-but-invisible metadata whose only consumer is this check.

---

## App-side wiring

### WorkshopBrowseDialog

A `FluentWindow` (Mica, 1280×760) with a three-state flow (`WsState`): `Cold` (opt-in off, showing the endpoint list and an enable button), `Search` (game shelf), `Browse` (game room). Search debounces 500 ms, requires 2+ characters, and takes the top 12 store matches. The manifest pane has exactly five mutually exclusive fills: idle, loading, legacy, error, result. Only result shows the import footer. Preset chips re-run the translation with a new `IncludedPresetIds` set. Art crossfades 240 ms through steel (120 out, swap, 120 in), honors the Windows animation setting, and decodes off the UI thread. Legacy selection tries `LocalWorkshopConfigStore` before showing the subscribe prompt, and the same fallback fires for dead CDN URLs.

### WorkshopProfileMaterializer

`Materialize(translated, source)` builds the `ProfileData`. It creates only the slots the translation demands (`NeedsXboxSlot` / `NeedsKbmSlot`), packed from slot 0 with the Xbox VC first when present: a split config lands Xbox at slot 0 and keyboard/mouse at slot 1, while a pure keyboard/mouse config imports as a single KbM VC at slot 0. Each created slot is enabled with the default HIDMaestro profile id for its type and its translated mapping set attached. Every other slot stays empty. Device assignments stay empty on purpose, so the abstract Gamepad descriptors resolve on whatever the user assigns. Macros land on `PadIndex = 0` (the Xbox slot, which macros always demand via `NeedsXboxSlot`) with `OutputController` triggers. Name falls back to `"Workshop Profile"`. When provenance is supplied it stamps `ImportedAt` and `TranslationSummary`.

The import sink (`AddWorkshopProfile` in `MainWindow.xaml.cs`) mirrors the `.pfprofile` import path: dedup the display name, append to `Profiles`, build the list card, `MarkDirty()`, and optionally `LoadProfile` for Save and Apply.

---

## Engine substrate (shipped with the import, usable everywhere)

### The abstract Gamepad descriptor family

`SourceCoercion.GamepadAliasTable` defines exactly 25 members. A descriptor is the literal string `"Gamepad " + member`. Evaluation folds it to the canonical per-device form via `CanonicalDescriptor`, so persisted and displayed descriptors keep the portable name while reads ride the proven `Button`/`Axis`/`POV` path. SDL's gamepad normalization is what makes the canonical indices stable across recognized pads.

| Descriptor | Canonical | Descriptor | Canonical |
|---|---|---|---|
| `Gamepad ButtonA` | `Button 0` | `Gamepad DPadUp` | `POV 0 Up` |
| `Gamepad ButtonB` | `Button 1` | `Gamepad DPadDown` | `POV 0 Down` |
| `Gamepad ButtonX` | `Button 2` | `Gamepad DPadLeft` | `POV 0 Left` |
| `Gamepad ButtonY` | `Button 3` | `Gamepad DPadRight` | `POV 0 Right` |
| `Gamepad LeftShoulder` | `Button 4` | `Gamepad LeftStickX` | `Axis 0` |
| `Gamepad RightShoulder` | `Button 5` | `Gamepad LeftStickY` | `Axis 1` |
| `Gamepad ButtonBack` | `Button 6` | `Gamepad LeftTrigger` | `Axis 2` |
| `Gamepad ButtonStart` | `Button 7` | `Gamepad RightStickX` | `Axis 3` |
| `Gamepad LeftStick` | `Button 8` | `Gamepad RightStickY` | `Axis 4` |
| `Gamepad RightStick` | `Button 9` | `Gamepad RightTrigger` | `Axis 5` |
| `Gamepad ButtonGuide` | `Button 10` | `Gamepad Paddle1` | `Button 12` |
| `Gamepad Paddle2` | `Button 13` | `Gamepad Paddle3` | `Button 14` |
| `Gamepad Paddle4` | `Button 15` | | |

Paddles follow SDL's physical naming (Paddle1 = right paddle 1, Paddle2 = left paddle 1, Paddle3 = right paddle 2, Paddle4 = left paddle 2). Gyro and touchpad members deliberately stay on the existing `Gyro ...` / `Touchpad ...` descriptors, which already resolve per device. The family does not rename them. The picker offers the family only for `CapType == Gamepad` devices not in raw-numbered naming, rendered through `Mapping_Gamepad_Format` ("Gamepad {0}") with the shared `DevObj_*` member labels.

**Empty-DeviceGuid contract.** `MappingSource.DeviceGuid` defaults to `""`, documented as "first available device on the VC," resolved per frame in Step 3. The Workshop translator emits every source with an empty guid. Two seams enforce the contract off the happy path:

- The multi-source contribution builders in `InputManager.Step3.MappingSetEval.cs` (`BuildCustomContribsForBipolarAxis` / `Trigger` / `Button`, plus `EvaluateStickTrim`) resolve an empty guid to the state of the device currently being evaluated instead of a null lookup that silently contributed 0.
- The gesture-provider invocations in `SourceCoercion` (`ReadAsBool` / `ReadAsBipolar` / `ReadAsUnipolar`) pass the caller-resolved guid, because the gesture providers key on a concrete `(slot, device, pad)` triple and a bare empty guid always missed.

### Generic per-source Sensitivity

`MappingSource.Sensitivity` is an `[XmlAttribute]` defaulting to 1.0 (a legacy 0 reads as 1.0 through `PerSourceSensitivity`). `IsGenericSensitivityDescriptor` gates it to sources whose canonical descriptor starts with `Axis` or `Slider`, which includes the Gamepad stick and trigger aliases and excludes the gyro / mouse-position / IR families that carry their own multipliers inside their own readers (no double scaling, one slider per source).

Three application sites in `SourceCoercion`, all clamped after scaling:

1. `ReadAsBipolar`: axis value × sensitivity, clamped to ±1.
2. `ReadAsUnipolar`: trigger value × sensitivity, clamped to 0..1.
3. `ReadAsBool` (the axis-to-button threshold read): the raw value scales before the threshold comparison. Half-axis scales deviation from center, full-axis and slider scale magnitude from zero, and sensitivity 1.0 leaves every comparison bit-identical. Without this site the slider had no effect on axis-to-button rows.

The editor slider runs 0.1–5.0 (`MappingItem` clamps), label `Mapping_Sensitivity`.

### Touchpad finger pressure

The `Touchpad {p} Finger {f} Pressure` descriptor existed in the engine. Phase A put it in the picker (`Mapping_TouchpadFingerPressure_Format`, one entry per pad × finger, gated on `HasTouchpad || IsTouchpad`, finger counts from the live SDL snapshot or the persisted capability). It reads `FingerPressure[f]` as a unipolar 0..1 level and bypasses the touchpad delta path. Values arrive from SDL's per-finger pressure on gamepad touchpads (pads without a force sensor report full on contact). The PTP reader and the touchpad overlay report binary 0/1 while a finger is down. The Workshop translator never emits this descriptor (its trackpad `soft_press` rides the click and touch descriptors as `SoftPressApproximated`). It exists for hand-built mappings.

### The macro-action family

Appended to `MacroActionType` (the enum is append-only because the clipboard serializes ints): `MoveMouseToScreenPosition = 33`, `RepeatKeyWhileHeld = 34`, `RepeatVcButtonWhileHeld = 35`, `ToggleVcButton = 36`, `ToggleKey = 37`, `GyroRecenter = 38`.

- `MoveMouseToScreenPosition`: `MouseX` / `MouseY` (primary-monitor pixels, clamped to the screen), executed as one `CursorControlService.MoveCursorTo` warp. Editor: two numeric fields plus **Pick on screen** (3-second countdown, then captures the live cursor).
- `RepeatKeyWhileHeld`: the shared key picker plus `IntervalMs` (clamped 10–1000, default 100). A continuous action: while the trigger holds, it sends a full key-down/key-up pulse per parsed key each time the interval elapses, first pulse immediately.
- `RepeatVcButtonWhileHeld` (v3): the virtual-controller twin, pulsing an Xbox button on the interval (Steam's xinput `hold_repeats` turbo).
- `ToggleVcButton` / `ToggleKey` (v3): press-to-latch, press-again-to-release, for Steam's activator `toggle` setting.
- `GyroRecenter` (v3): Steam's `camera_reset`, approximated as a gyro recenter.

The translator also reuses existing actions: `LightbarColor` / `LightbarColorClear` / `GuideLedBrightness` for `set_led` (v2, with HSV saturation and brightness folded by the materializer) and `MouseLimitRegion` for stick- and gyro-hosted mouse regions (v3). The translator's neutral shape is `TranslatedMacroAction`, a ten-member 0-based enum in `TranslatedProfile.cs` that the materializer lowers onto `MacroActionType`.

All dispatch in the gamepad-state and Extended raw-state switches of `InputManager.Step4b.EvaluateMacros.cs`, carry the DTO triple in `SettingsService`, and follow the `Is*Type` editor-visibility pattern in `MacroItem.cs`.

---

## Tests

`PadForge.SteamWorkshop.Tests` covers the parser (syntax, caps, VBKV), the clients (gate throws, downloader validation, artwork stale-serve), the cache (TTL, budgets, atomicity), the local store (library parsing, both file shapes), and the translator through `TranslationEdgeTests`, the per-wave suites (`WaveOneATranslationTests` through `WaveFourCTranslationTests`), and 30 golden fixtures (`Golden/{fileId}.golden.txt`, re-blessed via `PADFORGE_BLESS_GOLDEN=1` so translator changes surface as reviewable diffs). `PadForge.Tests/WorkshopProvenanceTests.cs` pins the provenance XML round-trip, the materializer stamp, and compaction preservation.

---

## Related pages

- [Steam Workshop Config Import](../guides/steam-workshop-import.md): the user guide for this feature.
- [Button and Axis Mappings](../features/mappings.md): the Gamepad sources and the Sensitivity slider as the user sees them.
- [Shift Layers](../guides/shift-layers.md): the activator modes the translator emits.
- [Menus](../guides/menus.md): what a translated `MenuDefinitionEntry` looks like in the UI.
- [Macros](../guides/macros.md): the translated actions in the editor.
- [Settings and Serialization](settings-and-serialization.md): `ProfileData`, the settings file, and where provenance persists.
- [Services Layer](services-layer.md): `InputService` profile loading the import path reuses.
- [Engine Library](engine-library.md): `MappingSource`, `MappingSet`, and the coercion layer.

---

*Last updated for PadForge 4.1.0*
