# Build and Publish

*Build, publish, and release reference for PadForge.*

---

## Solution Structure

```
PadForge.sln
├── PadForge.Engine/          Class library (net10.0-windows)
│   ├── Common/               SDL3 P/Invoke, input types, device wrappers
│   ├── Data/                 PadSetting, UserDevice, UserSetting
│   ├── Haptics/, Menus/, Mouse/, Touchpad/
│   ├── RemoteLink/           Pairing and transport for the Remote Link feature
│   └── Properties/           AssemblyInfo.cs
│
├── PadForge.App/             WPF application (net10.0-windows10.0.26100.0)
│   ├── Common/               SettingsManager, DriverInstaller, InputManager pipeline
│   ├── Views/                XAML pages and code-behind
│   ├── ViewModels/           MVVM ViewModels
│   ├── Services/             InputService, SettingsService, DeviceService, etc.
│   ├── Themes/               WPF resource dictionaries
│   ├── WebAssets/             HTML/CSS/JS for browser virtual controller
│   ├── VoiceModels/          Embedded Vosk model zip for voice macros
│   ├── ThirdParty/           OpenVR C# binding (openvr_api.cs)
│   ├── Models3D/             3D model classes (Base, DS4, DualSense, DualSenseEdge,
│   │                         SteamController, SteamController2, SteamDeck,
│   │                         Switch2Pro, Xbox360, XboxSeries)
│   ├── Models2D/             2D overlay layouts (11 classes) + colorway table
│   ├── 2DModels/             PNG overlay images, 13 families
│   ├── 3DModels/             OBJ meshes (DS4/, DualSense/, DualSenseEdge/,
│   │                         SteamController/, SteamController2/, SteamDeck/,
│   │                         Switch2Pro/, XBOX360/, XboxSeries/), the Sony and
│   │                         Xbox sets split by colorway subfolder
│   ├── Converter/            WPF value converters
│   ├── Controls/             Custom controls (RangeSlider, CurveEditor, EqCurveControl,
│   │                         TriggerTravelArc)
│   ├── Resources/            Icons, SDL3 DLL, embedded driver installers, localization
│   └── Properties/           AssemblyInfo.cs
│
├── PadForge.SteamWorkshop/   Steam Workshop import client (net10.0-windows)
│   ├── Api/                  SteamKit2 anonymous CM session + direct Steam HTTPS clients
│   ├── Vdf/                  Steam Input VDF parser
│   ├── Model/                Typed config model
│   ├── Translation/          VDF-to-PadForge config translator
│   ├── Cache/, Local/        File-system cache, local Steam discovery
│   └── Properties/           AssemblyInfo.cs
│
├── PadForge.Tests/           xunit suite for App + Engine (net10.0-windows10.0.26100.0)
├── PadForge.SteamWorkshop.Tests/  xunit suite for the Workshop client (offline fixtures + golden translation snapshots)
│
├── nuget-local/              Local NuGet source (MIDI Services SDK)
├── nuget.config               Registers nuget.org + nuget-local/ as package sources
├── .gitattributes             `* text=auto`: every text file is stored with LF
│
└── tools/                    Standalone utilities, NOT part of PadForge.sln
    ├── DsuDiag/              DSU/Cemuhook diagnostic client
    ├── Ds4InputDump/         DS4 raw HID input dump (Sony Report 0x01 passthrough debug)
    ├── PersonaVerify/        WASAPI consumer-side check of HIDMaestro composite USB personas
    ├── SteamWorkshopSmoke/   Manually-run smoke harness for the live Steam network paths
    ├── SteamWorkshopSweep/   Wild-corpus regression sweep for the Workshop config translator
    ├── WdgProbe/             Runs the app's own ACPI _WDG / WMI learner path outside the app
    ├── combomeasure/         WPF width-measurement harness for the Indicator LEDs card combos
    ├── deploy.ps1            Copy the published exe to C:\PadForge and restart
    └── *.ps1 / *.py          Screenshot capture, UIA diagnostics, runtime traces, asset
                              generation (see Development Scripts)
```

Line endings are repo-enforced. `.gitattributes` carries a single `* text=auto` rule, so a text file committed from a CRLF working tree is still stored with LF. A CRLF copy of one file once turned a 167-line change into a 12,000-line diff.

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| .NET SDK | 10.0+ | `net10.0-windows10.0.26100.0` target framework |
| Windows SDK | 10.0.26100.57 | Set via `WindowsSdkPackageVersion` in App csproj |
| Windows | 10/11 x64 | WPF + Windows-specific P/Invoke |
| Visual Studio (optional) | 2022+ | Not required. `dotnet` CLI suffices |

Minimum supported OS: Windows 10 1809 (build 17763), set via `SupportedOSPlatformVersion` in the App csproj.

All native DLLs, the HidHide installer, and model assets are checked into the repository. The build needs no external downloads. The Windows MIDI Services SDK installer is fetched from GitHub releases on demand at runtime when the user clicks Install, not at build time.

## Build Commands

### Debug Build

```bash
dotnet build -c Debug
```

Output: `PadForge.App/bin/Debug/net10.0-windows10.0.26100.0/win-x64/`

Suitable for development and debugging. **Not deployable**. Produces loose DLLs and requires the .NET runtime.

### Release Build

```bash
dotnet build -c Release
```

Output: `PadForge.App/bin/Release/net10.0-windows10.0.26100.0/win-x64/`

Not deployable. Use `dotnet publish` for deployment.

### Publish (Portable Deployment)

```bash
dotnet publish -c Release
# or explicitly:
dotnet publish PadForge.App/PadForge.App.csproj -c Release
```

Output: `PadForge.App/bin/Release/net10.0-windows10.0.26100.0/win-x64/publish/`

| File | Description |
|------|-------------|
| `PadForge.exe` | ~331 MB, single-file self-contained. The only file in the publish directory |

For Windows on ARM (preliminary, since 4.5.1), add the runtime identifier:

```bash
dotnet publish PadForge.App/PadForge.App.csproj -c Release -r win-arm64
```

Output: `PadForge.App/bin/Release/net10.0-windows10.0.26100.0/win-arm64/publish/`, one ~269 MB `PadForge.exe`. It cross-compiles on an x64 machine. With no `-r` the build is x64, so every existing command produces what it always has. See [Building for ARM64](#building-for-arm64) for what differs.

`SDL3.dll`, `libusb-1.0.dll`, `xinput1_4.dll`, `HAR.dll`, `Interhaptics.RazerProvider.dll` and the three Visual C++ runtime files are `<Content>` items in the App csproj, and the Vosk package's own targets add `libvosk.dll` plus the MinGW runtime it links against (`libgcc_s_seh-1.dll`, `libstdc++-6.dll`, `libwinpthread-1.dll`). A plain x64 `dotnet build` drops all twelve beside the output assembly. On publish they are folded into the bundle by `IncludeNativeLibrariesForSelfExtract`, and the publish directory holds `PadForge.exe` alone.

The custom gamepad mapping database ships embedded in the assembly, not as a loose file. See [gamecontrollerdb_padforge.txt](#gamecontrollerdb_padforgetxt) under Embedded Resources.

> **Critical:** Always use `dotnet publish` for deployment, never `dotnet build`. The project is configured for single-file self-contained publish. `dotnet build` produces non-functional multi-file output.

### Run Tests

```bash
dotnet test -c Release
```

Runs both xunit suites in the solution:

| Project | Covers | Notes |
|---------|--------|-------|
| `PadForge.Tests` | App + Engine | References the same pre-built `HIDMaestro.Core.dll` the App uses (the FFB decoder tests construct SDK types) |
| `PadForge.SteamWorkshop.Tests` | Workshop client | Offline only: VDF fixtures under `Fixtures/`, hand-reviewed translation snapshots under `Golden/`. No test touches the live Steam network |

The live Steam network paths are exercised by the manually-run `tools/SteamWorkshopSmoke` harness instead.

## Single-File Publish Configuration

The App csproj defines these publish properties:

```xml
<!-- Single-file portable publish: dotnet publish -c Release -->
<PropertyGroup>
  <RuntimeIdentifiers>win-x64;win-arm64</RuntimeIdentifiers>
  <RuntimeIdentifier Condition="'$(RuntimeIdentifier)' == ''">win-x64</RuntimeIdentifier>
  <NativeArch Condition="'$(RuntimeIdentifier)' == 'win-arm64'">arm64</NativeArch>
  <NativeArch Condition="'$(NativeArch)' == ''">x64</NativeArch>
  <PublishSingleFile>true</PublishSingleFile>
  <SelfContained>true</SelfContained>
  <IncludeNativeLibrariesForSelfExtract>true</IncludeNativeLibrariesForSelfExtract>
  <EnableCompressionInSingleFile>true</EnableCompressionInSingleFile>
  <DebugType>embedded</DebugType>
</PropertyGroup>
```

| Property | Value | Effect |
|----------|-------|--------|
| `RuntimeIdentifiers` | `win-x64;win-arm64` | The two architectures the project restores and builds for |
| `RuntimeIdentifier` | `win-x64` unless `-r` says otherwise | x64 stays the default, so an unadorned command builds what it always has |
| `NativeArch` | `x64` or `arm64` | The resource folder the native DLLs for this build come from. Every architecture-specific `<Content>` item is keyed on it |
| `PublishSingleFile` | `true` | Bundles all managed assemblies into one exe |
| `SelfContained` | `true` | Embeds .NET 10 runtime (no install needed on target) |
| `IncludeNativeLibrariesForSelfExtract` | `true` | Packs native DLLs into the exe. Extracted to temp dir at runtime |
| `EnableCompressionInSingleFile` | `true` | Compresses the bundle to reduce exe size |
| `DebugType` | `embedded` | Embeds debug symbols in assemblies (no `.pdb` files). Preserves stack traces for crash diagnostics |

**Note:** `RuntimeIdentifier` sits in a plain `PropertyGroup` with no publish-only condition, so `dotnet build` also targets `win-x64` and produces a RID-specific output folder.

### Building for ARM64

Preliminary since 4.5.1. Nothing on this path has run on ARM64 hardware: the bench is x64 and cannot execute ARM64 code, so the checks are static.

Every bundled native binary sits in a folder named for its architecture: `Resources/SDL3/x64` and `Resources/SDL3/arm64`, and the same pair for `OpenXInput` and `VisualCpp`. `Interhaptics` has an `x64` folder only. `NativeBinaryArchitectureTests` reads the PE header of every `.dll` and `.sys` in those folders and fails when a file's machine type differs from its folder name. It exists because Microsoft's own ARM64 redist folder ships a `vcruntime140_1.dll` that is an x64 image.

An ARM64 publish is refused by the `RequireArm64Natives` target if `Resources/SDL3/arm64/SDL3.dll` or `Resources/OpenXInput/arm64/xinput1_4.dll` is missing. Both `Content` items are conditioned on `Exists`, so without that target a missing DLL would publish an exe whose input engine cannot start. A plain `dotnet build -r win-arm64` is let through with a message. Both DLLs come from the forks, cross-compiled with `cmake -A ARM64`.

Three features have no ARM64 native half, and `PadForge.Engine/Common/PlatformSupport.cs` decides each one:

| Feature | Decided by | Why |
|---|---|---|
| HidHide | Machine architecture (`OSArchitecture`) | A kernel driver cannot run emulated, and upstream publishes an x64 package only. The installer is not embedded in an ARM64 build |
| Vosk voice engine | Process architecture (`ProcessArchitecture`) | libvosk ships for Windows x64 only. `VoskModelStore` never starts, and voice macros run on the SAPI recognizer. The model, about 36 MB packed, is left out of the ARM64 art pack |
| Razer Sensa HD haptics | Process architecture | The Interhaptics SDK ships for Win32 and x64 only. `SensaHapticsService` reports `Unsupported` |

The x64 build running emulated on ARM64 Windows loses HidHide alone. The ARM64 build loses all three. `PlatformSupportTests` pins both halves of that rule on an x64 bench, because each rule is a pure function of the architecture it is handed.

A fourth gap is decided in the SDL fork. Its Xbox Elite paddle reader (`SDL_XINPUT_PADDLES`) requires `SDL_CPU_X64` and switches itself off for any other target, so the ARM64 `SDL3.dll` reads no Elite paddles. That is also why the ARM64 build bundles `vcruntime140.dll` alone: the x64 `SDL3.dll` imports `msvcp140.dll` and `vcruntime140_1.dll` for that C++ reader, and the ARM64 one imports neither.

Vosk's NuGet targets add their win-x64 natives whenever the BUILD machine is Windows, whatever the target. `DropX64OnlyNativesOnArm64` takes them back out of an ARM64 build.

Drivers follow the machine. HIDMaestro 1.9.0 and BthPS3 3.0.0 each carry an x64 and an ARM64 payload, the x64 build embeds both BthPS3 payloads because an emulated x64 PadForge still installs the ARM64 driver, `Ds3DriverInstaller.SignWinUsbPackage()` builds its catalog for `10_ARM64` on an ARM64 machine, and the Windows MIDI Services download picks the `-arm64` installer there.

## Project Configuration Details

### PadForge.App.csproj

```xml
<PropertyGroup>
  <OutputType>WinExe</OutputType>
  <TargetFramework>net10.0-windows10.0.26100.0</TargetFramework>
  <SupportedOSPlatformVersion>10.0.17763.0</SupportedOSPlatformVersion>
  <WindowsSdkPackageVersion>10.0.26100.57</WindowsSdkPackageVersion>
  <RootNamespace>PadForge</RootNamespace>
  <AssemblyName>PadForge</AssemblyName>
  <UseWPF>true</UseWPF>
  <UseWindowsForms>true</UseWindowsForms>  <!-- For NotifyIcon system tray -->
  <LangVersion>latest</LangVersion>
  <Nullable>disable</Nullable>
  <ImplicitUsings>enable</ImplicitUsings>
  <GenerateAssemblyInfo>false</GenerateAssemblyInfo>  <!-- Manual AssemblyInfo.cs -->
</PropertyGroup>
```

Key settings:

| Property | Value | Purpose |
|----------|-------|---------|
| `TargetFramework` | `net10.0-windows10.0.26100.0` | .NET 10 + Windows SDK 26100 (Win 11 24H2). Enables WinRT APIs. |
| `SupportedOSPlatformVersion` | `10.0.17763.0` | Minimum OS: Windows 10 1809 |
| `WindowsSdkPackageVersion` | `10.0.26100.57` | Pins Windows SDK NuGet package version |
| `UseWindowsForms` | `true` | `NotifyIcon` system tray only (not WinForms UI) |
| `GenerateAssemblyInfo` | `false` | Uses manual `Properties/AssemblyInfo.cs` |
| `Nullable` | `disable` | Nullable reference types not used |

**WinForms implicit using removal**. Prevents `System.Drawing` / `System.Windows.Forms` ambiguity with WPF types:
```xml
<ItemGroup>
  <Using Remove="System.Drawing" />
  <Using Remove="System.Windows.Forms" />
</ItemGroup>
```

### PadForge.Engine.csproj

```xml
<PropertyGroup>
  <AllowUnsafeBlocks>true</AllowUnsafeBlocks>
  <TargetFramework>net10.0-windows</TargetFramework>
  <RootNamespace>PadForge.Engine</RootNamespace>
  <AssemblyName>PadForge.Engine</AssemblyName>
  <LangVersion>latest</LangVersion>
  <Nullable>disable</Nullable>
  <ImplicitUsings>enable</ImplicitUsings>
  <GenerateAssemblyInfo>false</GenerateAssemblyInfo>
  <DebugType>embedded</DebugType>
</PropertyGroup>
```

The Engine targets `net10.0-windows` (no specific SDK version needed). SDL3 and system interop use raw `[DllImport]` P/Invoke. The only NuGet references are the Remote Link crypto packages (see below).

### Assembly Versioning

App, Engine, and SteamWorkshop share one version via `SharedVersion.cs` at the repo root. All three csproj files link it in:

```xml
<Compile Include="..\SharedVersion.cs">
  <Link>Properties\SharedVersion.cs</Link>
</Compile>
```

`SharedVersion.cs` carries `AssemblyVersion` and `AssemblyFileVersion`. The assemblies cannot drift apart because they compile against the same file. `Properties/AssemblyInfo.cs` in each project carries the other assembly metadata (title, copyright, COM GUID, theme info) and explicitly does **not** carry version attributes. Every project sets `<GenerateAssemblyInfo>false</GenerateAssemblyInfo>` so the build does not regenerate either file.

**Important:** Edit `SharedVersion.cs` to bump the version. Never re-introduce `AssemblyVersion` to `Properties/AssemblyInfo.cs`. It would override the shared version on whichever assembly carries it and the drift guard breaks. GitHub Releases use git tag names (e.g., `v4.4.0`) as the user-facing version, but the binary's `AssemblyVersion` should match. The current shared version is `4.5.0.0`.

## NuGet Dependencies

### PadForge.App

| Package | Version | Source | Purpose |
|---------|---------|--------|---------|
| **WPF-UI** | 4.3.0 | nuget.org | Fluent Design theme for WPF (dark mode, NavigationView, controls) |
| **HelixToolkit.Core.Wpf** | 2.27.3 | nuget.org | 3D viewport rendering (OBJ model loading, camera, lighting) |
| **CommunityToolkit.Mvvm** | 8.2.2 | nuget.org | MVVM: `ObservableObject`, `RelayCommand`, `[ObservableProperty]` |
| **Concentus** | 2.2.2 | nuget.org | Pure-C# Opus encoder for the DualSense Bluetooth speaker stream |
| **NAudio.Wasapi** | 2.2.1 | nuget.org | WASAPI loopback audio capture for bass-driven rumble detection |
| **Nefarius.Utilities.DeviceManagement** | 5.2.0 | nuget.org | Driver-store install, class filters, and USB CyclePort for the DualShock 3 Bluetooth stack (same library BthPS3's own installer uses) |
| **System.Speech** | 10.0.0 | nuget.org | SAPI recognizer behind the voice-macro trigger (#317) |
| **Vosk** | 0.3.38 | nuget.org | Offline recognizer for voice macros (Apache-2.0, Alpha Cephei). Phrase-list grammar with an `[unk]` bucket, so non-phrase audio decodes as unknown. Its targets file also copies `libvosk.dll` and the MinGW runtime into the output |
| **System.Management** | 10.0.11 | nuget.org | WMI queries behind the handheld hidden-button learner (ACPI `_WDG` event classes) |
| **Microsoft.Windows.Devices.Midi2** | 1.0.16-rc.3.7 | **nuget-local/** | Windows MIDI Services SDK for virtual MIDI device creation |

`HIDMaestro.Core` (the virtual Xbox / PlayStation controller client) is a project `<Reference>` with a `HintPath` into `Resources/HIDMaestro/`, not a NuGet package. The shipped DLL reports file version `1.7.2.0`. The DLL's own file version is the authority, because the csproj comment naming the shipped build is hand-maintained and drifts: at this commit that comment still says v1.7.1.

The App also holds `<ProjectReference>`s to `PadForge.Engine` and `PadForge.SteamWorkshop`.

### PadForge.SteamWorkshop

| Package | Version | Purpose |
|---|---|---|
| **SteamKit2** | 3.4.0 | Steam protocol client (LGPL-2.1-only) for the anonymous CM session behind Workshop config lookup. Pinned exactly: Valve adjusts the Steam protocol periodically and SteamKit2 catches up in point releases |

The Workshop client is the #9 community config import feature. Every client constructor checks `ISteamWorkshopGate` and throws when the user has not opted in, so no network work can happen until the "Enable Community Configs" toggle in Settings (backed by `EnableCommunityConfigLookup`) is on.

### PadForge.Engine

| Package | Version | Purpose |
|---|---|---|
| **BouncyCastle.Cryptography** | 2.6.2 | X25519 / Ed25519 / ChaCha20-Poly1305 for Remote Link pairing and transport, on the Win10 1809 floor where the in-box AEAD is gated to Win11 22000+ |
| **System.Security.Cryptography.ProtectedData** | 10.0.9 | DPAPI at-rest protection for Remote Link peer identity keys |

All SDL3 and system interop still uses raw `[DllImport]` P/Invoke.

### Test Projects

`PadForge.Tests` and `PadForge.SteamWorkshop.Tests` both reference xunit 2.9.3, xunit.runner.visualstudio 3.1.4, Microsoft.NET.Test.Sdk 17.14.1, and coverlet.collector 6.0.4.

### Local NuGet Source (`nuget-local/`)

The Windows MIDI Services SDK is not on nuget.org. The `.nupkg` is stored locally:

```
nuget-local/Microsoft.Windows.Devices.Midi2.1.0.16-rc.3.7.nupkg
```

`nuget.config` at the solution root registers this folder as a package source:

```xml
<configuration>
  <packageSources>
    <add key="nuget.org" value="https://api.nuget.org/v3/index.json" />
    <add key="local" value="nuget-local" />
  </packageSources>
</configuration>
```

Both `nuget.config` and `nuget-local/` must be present alongside `PadForge.sln` for `dotnet restore` to succeed.

## Native DLLs (Content Items)

Declared as `<Content>` + `CopyToOutputDirectory`, which puts them in `bin/.../publish/` alongside `PadForge.exe` during a non-single-file build. With `PublishSingleFile=true` plus `IncludeNativeLibrariesForSelfExtract=true` (both set in the csproj) the same files get folded into the single-file bundle and extracted to `%TEMP%\.net\PadForge\<hash>\` at first launch. Either way the user never has to drop a DLL alongside the EXE. Single-file deploy is one file.

The full native set in the bundle:

`<arch>` is `x64` or `arm64`, picked by `$(NativeArch)`.

| Library | Origin | Caller | In the ARM64 build |
|---|---|---|:-:|
| `SDL3.dll` | `<Content>`, `Resources/SDL3/<arch>/` | `SDL3Minimal.cs` | Yes |
| `libusb-1.0.dll` | `<Content>`, `Resources/SDL3/<arch>/` | SDL3's HIDAPI backend, loaded at run time by the file name compiled into `SDL3.dll` | Yes |
| `xinput1_4.dll` | `<Content>`, `Resources/OpenXInput/<arch>/` | SDL3's XInput backend, and `BluetoothLinkHelper` for ordinals 108 / 103 | Yes |
| `vcruntime140.dll` | `<Content>`, `Resources/VisualCpp/<arch>/` | `SDL3.dll` | Yes |
| `msvcp140.dll`, `vcruntime140_1.dll` | `<Content>`, `Resources/VisualCpp/x64/` | The x64 `SDL3.dll`, for its C++ Elite paddle reader | No |
| `HAR.dll` | `<Content>`, `Resources/Interhaptics/x64/` | `SensaHapticsService` (#374), P/Invoked lazily | No |
| `Interhaptics.RazerProvider.dll` | `<Content>`, `Resources/Interhaptics/x64/` | Loaded by `HAR.dll` as its Razer Sensa backend | No |
| `libvosk.dll` | Vosk 0.3.38 package targets | `Vosk.dll`, behind `VoskVoiceEngine` (#317) | No |
| `libgcc_s_seh-1.dll`, `libstdc++-6.dll`, `libwinpthread-1.dll` | Vosk 0.3.38 package targets | MinGW runtime `libvosk.dll` links against | No |

### SDL3.dll and libusb-1.0.dll

```xml
<Content Include="Resources\SDL3\$(NativeArch)\SDL3.dll" Link="SDL3.dll"
         Condition="Exists('Resources\SDL3\$(NativeArch)\SDL3.dll')">
  <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
</Content>
<Content Include="Resources\SDL3\$(NativeArch)\libusb-1.0.dll" Link="libusb-1.0.dll"
         Condition="Exists('Resources\SDL3\$(NativeArch)\libusb-1.0.dll')">
  <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
</Content>
```

- **`Link="SDL3.dll"`**. Flattens to output root (next to `PadForge.exe`) instead of preserving the subdirectory path.
- **`Condition="Exists(...)"`**. Build succeeds even if the DLL is absent (e.g., fresh clone).
- **SDL3.dll** is a **custom fork** with WinUSB support for Switch 2 Pro Controller. The fork tree is not inside the PadForge repository. It lives in a sibling `SDL3-build/SDL/` checkout, and only the built DLL is committed here. See [SDL3 Integration](sdl3-integration.md) for build instructions.
- **libusb-1.0.dll** provides WinUSB access for Switch 2 Pro Controller communication. The x64 copy is upstream's `VS2022/MS64` build and the ARM64 copy is upstream's `MinGW-llvm-aarch64` build, both 1.0.29 and both unmodified.
- **SDL loads libusb by a file name compiled into `SDL3.dll`**, and that name has to be a file bundled beside it. The fork's build reads the name off libusb's import library with `dumpbin`. When a Visual Studio update removed the `dumpbin` its build cache pointed at, the fallback was the import library's own name, and the seven x64 DLLs delivered September 10 to 15, 2026 asked Windows for `libusb-1.0.lib`. libusb never loaded, so in PadForge 4.5.0 a wired Switch 2 Pro Controller, Joy-Con 2 or Switch 2 GameCube controller did not work, because `SDL_hidapi_switch2.c` starts each of them through libusb and returns false without it, and the GameCube adapter, which SDL reaches through libusb alone, was never seen. The fork's configure now stops on a name that is not a DLL, and `BundledSdlLibusbNameTests` checks the delivered bytes from PadForge's side for both architectures.

Source location: `PadForge.App/Resources/SDL3/<arch>/`

### xinput1_4.dll (OpenXInput shim)

```xml
<Content Include="Resources\OpenXInput\$(NativeArch)\xinput1_4.dll" Link="xinput1_4.dll"
         Condition="Exists('Resources\OpenXInput\$(NativeArch)\xinput1_4.dll')">
  <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
</Content>
```

- **OpenXInput-derived.** Forked from `Nemirtingas/OpenXInput` with a HIDMaestro classifier added to the enumeration step so HM virtuals are skipped during slot assignment.
- **Replaces the system `xinput1_4.dll` via DLL search order.** The application directory is searched before `System32` for non-KnownDLLs, so when SDL3 calls `LoadLibrary("xinput1_4.dll")` this local copy resolves first and SDL's XInput backend uses it instead of Microsoft's.
- **`devobj.dll` is deliberately not shipped alongside it.** A stub `devobj.dll` would pre-empt `System32\devobj.dll` for the whole process and crash `setupapi.dll` during HID class enumeration. `xinput1_4.dll`'s `devobj.dll` import resolves from `System32` unaided. See [Driver Installation Internals](driver-installation-internals.md).

Source location: `PadForge.App/Resources/OpenXInput/<arch>/`. The ARM64 DLL links the C runtime statically and has the same export table as the x64 one, down to the unnamed ordinals 100 to 104, 108 and 109.

## Embedded Resources

Compiled into the assembly. **Not** visible as separate files in the output.

### gamecontrollerdb_padforge.txt

```xml
<EmbeddedResource Include="gamecontrollerdb_padforge.txt" />
```

Custom SDL gamepad mapping database with PadForge-specific entries (e.g., DualShock 3 via DsHidMini SDF). Embedded under the manifest name `PadForge.gamecontrollerdb_padforge.txt` and streamed to SDL from memory at startup by `InputManager.LoadEmbeddedGamepadMappings()`, one `SDL_AddGamepadMapping` call per line. It is no longer copied to the output folder. Community mappings can be submitted via the GitHub issue template.

Source location: `PadForge.App/gamecontrollerdb_padforge.txt`

### Driver Installers (EmbeddedResource)

```xml
<EmbeddedResource Include="Resources\HidHide_1.5.230_x64.exe"
                  Condition="'$(NativeArch)' == 'x64'" />
```

| Resource | Purpose |
|----------|---------|
| `HidHide_1.5.230_x64.exe` | HidHide installer. Hides physical controllers from other applications. x64 build only: an ARM64 build cannot use it, and its 8 MB stays out of that exe |

The HIDMaestro user-mode driver is **not** managed by `DriverInstaller`. The driver binaries, INF, profiles, and signing tools all ship inside `HIDMaestro.Core.dll` (referenced as a `<Reference>`, so it's bundled into the single-file EXE). `InputManager` calls `HMContext.InstallDriver()` on first start (from `EnsureHMaestroContext()` in `PadForge.App/Common/Input/`), which registers the driver with Windows through `pnputil` from inside PadForge's already-elevated process. No separate installer EXE. The OpenXInput shim (`xinput1_4.dll` only) ships as `<Content>` and is bundled into the single-file EXE via `IncludeNativeLibrariesForSelfExtract`. `devobj.dll` is deliberately not shipped. See [Driver Installation Internals](driver-installation-internals.md) for why a bundled stub would crash HID class enumeration. The Windows MIDI Services SDK is downloaded from the GitHub releases API on demand when the user clicks Install, then run with `/install /quiet /norestart`.

PadForge v2's vJoy and ViGEmBus installers are no longer bundled. v4 detects either driver on first launch and offers to uninstall via the legacy driver cleanup dialog. See [Driver Installation Internals](driver-installation-internals.md).

### BthPS3 / DS3 Bluetooth Drivers (EmbeddedResource)

```xml
<EmbeddedResource Include="Resources\BthPS3\**\*.*">
  <LogicalName>BthPS3.%(RecursiveDir)%(Filename)%(Extension)</LogicalName>
</EmbeddedResource>
```

Microsoft-signed BthPS3 + BthPS3PSM drivers (nefarius release) and the DS3 WinUSB INF, embedded so the single-file app can install them at DualShock 3 pairing time with no MSI and no external installer. `Ds3DriverInstaller.ExtractDrivers()` walks every manifest resource whose name starts with `BthPS3.`, strips that prefix, and drops the files under `%TEMP%\PadForge\BthPS3Drivers\` before running `pnputil`. The explicit `LogicalName` preserves the subdirectory layout inside the manifest name. Each 3.0.0 INF names both architectures, `[SourceDisksFiles.amd64]` and `[SourceDisksFiles.arm64]`, and Windows installs the binary that matches the machine, so both builds of PadForge embed both.

| Directory | Contents |
|-----------|----------|
| `Resources/BthPS3/BthPS3/` | `BthPS3.inf`/`.cat` (profile driver) + `BthPS3_PDO_NULL_Device.inf`/`.cat` (raw PDO extension), with `x64/BthPS3.sys` and `ARM64/BthPS3.sys` |
| `Resources/BthPS3/BthPS3PSM/` | `BthPS3PSM.inf`/`.cat` (L2CAP PSM filter), with `x64/BthPS3PSM.sys` and `ARM64/BthPS3PSM.sys` |
| `Resources/BthPS3/WinUSB/` | `ds3_winusb.inf` only (DS3-over-USB WinUSB binding). The matching `ds3_winusb.cat` is not checked in. `Ds3DriverInstaller.SignWinUsbPackage()` regenerates and signs it against this machine's certificate every run, because a stale catalog left by an earlier run still chains and would hand `pnputil` hashes that no longer match the INF |

### 3D Model Assets (EmbeddedResource)

```xml
<!-- 3D controller model assets (adapted from Handheld Companion, CC BY-NC-SA 4.0;
     Switch2Pro set split from the purchased hado CGTrader model) -->
<EmbeddedResource Include="3DModels\**\*.jpg" />
```

Only the opaque texture atlases are embedded directly, as JPEG, because JPEG is already compressed. Everything else goes through the `EmbedPackedArt` target described below. Loaded at runtime via `ControllerModelBase.LoadModel()`.

The Sony and Xbox families are split one folder per colorway, and each colorway holds a full part set. The counts below are per colorway.

| Directory | Colorways | Contents |
|-----------|-----------|----------|
| `3DModels/XBOX360/` | none, flat | 31 OBJ files (Xbox 360 controller parts) |
| `3DModels/XboxSeries/` | 21 (Carbon, Starfield, Robot, Sonic, and so on) | 32 OBJ files each, 34 for Starfield |
| `3DModels/DS4/` | 2 (JetBlack, MagmaRed) | 37 OBJ files each |
| `3DModels/DualSense/` | 10 (White, Midnight, SpiderMan2, and so on) | 32 OBJ files each, Touchpad split for click-mapping |
| `3DModels/DualSenseEdge/` | 1 (Edge) | 40 OBJ files |
| `3DModels/Switch2Pro/` | none, flat | 32 OBJ files |
| `3DModels/SteamDeck/` | none, flat | 46 OBJ files |
| `3DModels/SteamController/` | none, flat | 33 OBJ files (2015 Steam Controller) |
| `3DModels/SteamController2/` | none, flat | 29 OBJ files (2026 Steam Controller) |

The two Steam Controller sets are meshed from Valve's own STEP releases by `tools/steam_controller_2015_mesh.py` and `tools/steam_controller_2026_mesh.py`. Two follow-up scripts fix up what the conversion left wrong: `steam_controller_2026_pads.py` gives each 2026 trackpad only its own surface, and `steam_deck_stick_well.py` opens the Deck's capped stick wells.

There is no Xbox One mesh set and no `ControllerModelXboxOne` class. The Series mesh serves Xbox One, Elite, and Adaptive, and the Switch 2 Pro mesh serves both Switch generations. `ControllerModelView` passes a `wantExtraControls` flag so a borrowing profile gets inert meshes for controls it does not have.

### Packed Art (EmbedPackedArt target)

Meshes, transparent atlases and the speech model are too big to ship raw and
compress badly inside the single-file bundle, which deflates each resource on
its own. The `EmbedPackedArt` target runs an inline `PackAssets` task before
`PrepareForBuild` and rewrites all three into Brotli streams:

| Source | Packed as | What the packer does |
|---|---|---|
| `3DModels/**/*.obj` | `.objbr` | Brotli over the mesh text |
| `3DModels/**/*.png` | `.pngbr` | Re-emits each IDAT chunk as a stored deflate block, then Brotli over the whole file |
| `VoiceModels/*.zip` | `.zipbr` | Re-emits the zip entries stored, then Brotli over the archive |

The PNG and zip cases both follow the same rule: store first, compress once.
Deflating data that is already deflated costs size, so the packer strips the
inner compression and lets Brotli see the raw bytes. That is where most of the
saving comes from. Opaque atlases skip the whole path because they ship as
JPEG.

Two traps the target handles explicitly. Packing is incremental on file
timestamps, so art that has not changed is not repacked and only the first
build pays. And each packed file is named for the resource it becomes, so its
name carries dots; MSBuild reads the segment before the extension as a culture
when it matches one. `Switch2Pro/GL.obj` became
`PadForge._3DModels.Switch2Pro.GL.objbr`, whose `GL` is Galician, and that mesh
was routed into a satellite assembly and disappeared from the pad. The
`EmbeddedResource` items carry `WithCulture="false"` for that reason.

A separate `SharedGeometry` table names twelve donor meshes that identical
parts in other sets point at instead of carrying their own copy, which drops
352 duplicate meshes from the bundle.

### Web Controller Assets (EmbeddedResource)

```xml
<!-- Web controller frontend assets (embedded, served by WebControllerServer) -->
<EmbeddedResource Include="WebAssets\**\*" />
```

HTML/CSS/JS for the browser-based virtual controller. Served at runtime by `WebControllerServer`, which runs an `HttpListener` accept loop, not Kestrel.

| File | Purpose |
|------|---------|
| `WebAssets/index.html` | Landing page |
| `WebAssets/controller.html` | Virtual gamepad UI |
| `WebAssets/touchpad.html` | Touchpad surface UI |
| `WebAssets/custom.html` | Custom controller builder UI |
| `WebAssets/css/controller.css` | Gamepad styling |
| `WebAssets/js/controller_client.js` | WebSocket client logic |
| `WebAssets/js/custom_client.js` | Custom layout client logic |
| `WebAssets/js/nipplejs.min.js` | Virtual joystick library |

### Voice Model (EmbeddedResource)

`VoiceModels/vosk-model-small-en-us-0.15.zip`, the offline Vosk recognizer model behind voice macros (#317). The `EmbedPackedArt` target below repacks it to about 35 MB. It ships inside the exe rather than downloading on first use, so voice macros work on a machine with no internet and nothing is written into LocalAppData unasked.

### Localization Strings (EmbeddedResource)

```xml
<EmbeddedResource Update="Resources\Strings\Strings.resx">
  <Generator>PublicResXFileCodeGenerator</Generator>
  <LastGenOutput>Strings.Designer.cs</LastGenOutput>
</EmbeddedResource>
```

Resource files for multilingual UI support:

| File | Language |
|------|----------|
| `Strings.resx` | English (default/fallback) |
| `Strings.de.resx` | German |
| `Strings.es.resx` | Spanish |
| `Strings.fr.resx` | French |
| `Strings.it.resx` | Italian |
| `Strings.ja.resx` | Japanese |
| `Strings.ko.resx` | Korean |
| `Strings.nl.resx` | Dutch |
| `Strings.pt-BR.resx` | Brazilian Portuguese |
| `Strings.zh-Hans.resx` | Simplified Chinese |

The csproj carries `PublicResXFileCodeGenerator` metadata on `Strings.resx`, but the checked-in `Strings.Designer.cs` is hand-written. It implements `INotifyPropertyChanged` and a weak `CultureChanged` event so live language switching refreshes XAML bindings, which no generator emits. Access is through the singleton: `Strings.Instance.PropertyName`. Satellite `.resx` files follow standard .NET localization conventions and compile into satellite assemblies automatically.

### 2D Model Assets (Resource)

```xml
<!-- 2D controller model assets (Gamepad-Asset-Pack by AL2009man, MIT license) -->
<Resource Include="2DModels\**\*.png" />
```

PNG overlay images for the 2D controller schematic view. Thirteen families: `DS4/`, `DualSense/`, `DUALSENSEEDGE/`, `MOUSE/`, `STEAMCONTROLLER/`, `STEAMCONTROLLER2/`, `STEAMDECK/`, `SWITCH2PRO/`, `SWITCHPRO/`, `VRCONTROLLER/`, `XBOX360/`, `XBOXONE/`, `XBOXSERIES/`. Uses `Resource` (not `EmbeddedResource`) so they load as WPF pack URIs (`pack://application:,,,/2DModels/...`).

The matching overlay layouts live in `Models2D/ControllerOverlayLayout.cs` as eleven static classes: `Xbox360Layout`, `DS4Layout`, `DualSenseLayout`, `DualSenseEdgeLayout`, `XboxOneSLayout`, `XboxSeriesXLayout`, `SwitchProLayout`, `Switch2ProLayout`, `SteamDeckLayout`, `SteamControllerLayout`, `SteamController2Layout`.

### Other Resources

```xml
<Resource Include="Resources\PadForge.ico" />
<Resource Include="Resources\PadForge-logo.png" />
<Resource Include="Resources\PadForge-icon.png" />
```

| Resource | Purpose |
|----------|---------|
| `PadForge.ico` | Application icon. Declared as `<Resource>`. The taskbar/exe icon is wired separately via `<ApplicationIcon>Resources\PadForge.ico</ApplicationIcon>` in the main PropertyGroup |
| `PadForge-logo.png` | Brand wordmark image (About page, headers) |
| `PadForge-icon.png` | Brand app-icon image |
| `Resources/ControllerIcons.xaml` | XAML vector icon definitions (resource dictionary) |

## CI/CD (GitHub Actions)

Workflow: `.github/workflows/build.yml`

### Triggers

```yaml
on:
  push:
    branches: [v4-dev]
  pull_request:
    branches: [v4-dev]
  workflow_dispatch:
```

Runs on every push/PR to `v4-dev` and on manual trigger.

### Build job (one per architecture)

A matrix runs `win-x64` and `win-arm64` side by side on `windows-latest`. Nearly all of a build is the art pack and each architecture packs its own, so two publishes in one job would double the wall clock. `fail-fast` is off: a broken ARM64 build shows red on the run and does not cancel the x64 build the dev feed depends on. x64 keeps every name it has always had, and ARM64 adds `-arm64`.

1. **Checkout**. `actions/checkout@v5`, `fetch-depth: 0` (full history for commit counting)
2. **Setup .NET**. `actions/setup-dotnet@v5`, `dotnet-version: 10.x`
3. **Get build info**. Commit count and 7-character SHA, exported as job outputs. It runs before Publish so that a failed publish cannot leave its copy of those outputs blank
4. **Publish**. `dotnet publish PadForge.App/PadForge.App.csproj -c Release`, plus `-r win-arm64` for the ARM64 leg
5. **Upload artifact**. `actions/upload-artifact@v7`, publish directory as `PadForge_r{COMMIT_COUNT}@{COMMIT_SHORT}`, with `-arm64` appended for ARM64

### Release job (push only)

One job writes the dev feed, because the `latest-<branch>` step deletes and recreates a release and two jobs doing that at once would race. It runs under `!cancelled()`, so a failed ARM64 build does not stop it and a canceled run publishes nothing. It cannot publish without x64: the x64 artifact download is its first step and fails before any release is touched.

1. **Download x64 build**, then **Download ARM64 build** with `continue-on-error`. `actions/download-artifact@v8`
2. **Package release zips**. Deletes any `*.pdb`, then `7z a -mx=9` over each publish directory into `PadForge.zip` and `PadForge-arm64.zip`, each copied a second time as `PadForge_r{N}@{SHA}.zip` and `PadForge_r{N}@{SHA}-arm64.zip`. With no ARM64 build, x64 is released alone

### Automatic Releases (push to v4-dev only)

On push (not PR), the workflow creates two GitHub releases keyed off the branch ref name:

| Release | Behavior |
|---------|----------|
| **`archive-v4-dev`** | Accumulates every build as `PadForge_r{N}@{SHA}.zip` and `PadForge_r{N}@{SHA}-arm64.zip`. Uses `--clobber` for the latest upload. Preserves the tag across builds. Rolls to a new part when full (see below). |
| **`latest-v4-dev`** | Recreated on every push (old release deleted first). Contains `PadForge.zip` (x64) and `PadForge-arm64.zip` with the most recent build. The "always current" download link. The step aborts before the delete if `release/PadForge.zip` is missing or empty, because the delete takes the tag with it and the upload is the only thing that puts a download back. |

Both are marked `--prerelease` and cross-link to each other in their notes.

**Rolling archive parts.** GitHub caps a release at 1000 assets. A push adds up to two assets, so the workflow watches the active archive and, once it reaches 998 assets, creates the next numbered part (`archive-v4-dev-2`, `archive-v4-dev-3`, and so on) targeting the current commit. Each new part's notes link back to the previous part, and `latest-v4-dev` points at whichever part is currently active.

### Artifact Naming

Format: `PadForge_r{COMMIT_COUNT}@{7-char COMMIT_SHA}` (e.g., `PadForge_r342@f35bb36`), with `-arm64` appended for the ARM64 build

### Environment Variables

```yaml
env:
  DOTNET_NOLOGO: true
  DOTNET_CLI_TELEMETRY_OPTOUT: true
```

### Formal Releases

Created manually via `gh release create` with a version tag (e.g., `v4.4.0`, `v4.4.0-beta1`). See [Release Workflow](#release-workflow) below.

## Deployment

PadForge is portable. No installer required.

### Local Deployment

Copy the publish output to any folder:
```bash
cp PadForge.App/bin/Release/net10.0-windows10.0.26100.0/win-x64/publish/PadForge.exe C:\PadForge\PadForge.exe
```

There are no companion files. Every native library (`SDL3.dll`, `libusb-1.0.dll`, `xinput1_4.dll`, `HAR.dll`, `Interhaptics.RazerProvider.dll`, `libvosk.dll`, and the MinGW runtime) is folded into the single-file bundle on publish and extracted to `%TEMP%\.net\PadForge\<hash>\` at first launch. The gamepad mapping database is embedded in the assembly, so no `.txt` file sits alongside the exe either. A deploy is one `PadForge.exe`.

### Development Deploy Script

```bash
tools/deploy.ps1   # Kill running instance, copy the published exe to C:\PadForge, relaunch
```

The script does not build. Run `dotnet publish -c Release` first. It checks for the published exe before stopping anything, so a missing build never leaves the machine without a running PadForge.

### First Run

PadForge creates `PadForge.xml` alongside the executable to store settings, mappings, and profiles. An unhandled exception appends to `crash.log` in the same directory (`App.xaml.cs`, `AppDomain.CurrentDomain.BaseDirectory`). Those two files are the only ones PadForge is allowed to write beside the exe.

PadForge always requests administrator privileges on startup (declared in `app.manifest` as `requireAdministrator`). HIDMaestro / HidHide / MIDI Services management runs inside the already-elevated process.

## Release Workflow

### 1. Update Version (if needed)

- Edit `SharedVersion.cs` at the repo root. Updates `AssemblyVersion` and `AssemblyFileVersion` for App, Engine, and SteamWorkshop in one place.

### 2. Build

```bash
dotnet publish PadForge.App/PadForge.App.csproj -c Release
dotnet publish PadForge.App/PadForge.App.csproj -c Release -r win-arm64
```

### 3. Deploy and Test

```bash
cp PadForge.App/bin/Release/net10.0-windows10.0.26100.0/win-x64/publish/PadForge.exe C:\PadForge\PadForge.exe
```

Run `C:\PadForge\PadForge.exe` and verify functionality.

### 4. Commit and Push

```bash
git add -A
git commit -m "Release vX.Y.Z"
git push
```

### 5. Create Binary Zips

```bash
cd PadForge.App/bin/Release/net10.0-windows10.0.26100.0/win-x64/publish
zip -r PadForge-vX.Y.Z-win-x64.zip .
cd ../../win-arm64/publish
zip -r PadForge-vX.Y.Z-win-arm64.zip .
```

Each publish directory holds one file, so the 4.5.1 assets are `PadForge-v4.5.1-win-x64.zip` and `PadForge-v4.5.1-win-arm64.zip`, each containing `PadForge.exe` and nothing else. Only the x64 exe can be run on an x64 bench.

### 6. Create GitHub Release

```bash
gh release create vX.Y.Z --title "PadForge vX.Y.Z" --notes "Release notes here"
gh release upload vX.Y.Z PadForge-vX.Y.Z-win-x64.zip PadForge-vX.Y.Z-win-arm64.zip
```

Use `--prerelease` for beta/RC releases. Use `--latest` for the default download.

## Diagnostic Tools (`tools/`)

Standalone diagnostic utilities and development scripts. None of the tool projects are in `PadForge.sln`. Build and run each from its own folder.

| Tool | Command | Framework | Dependencies | Purpose |
|------|---------|-----------|--------------|---------|
| **DsuDiag** | `cd tools/DsuDiag && dotnet run` | net8.0 | None | Real-time DSU/Cemuhook UDP client for verifying gyro/accel axis mapping |
| **Ds4InputDump** | `cd tools/Ds4InputDump && dotnet run` | net10.0-windows | None (raw HID) | Dumps DS4 raw HID input frames. Used to validate Sony Report 0x01 passthrough on PlayStation virtual controllers |
| **SteamWorkshopSmoke** | `cd tools/SteamWorkshopSmoke && dotnet run` | net10.0-windows | PadForge.SteamWorkshop | Manually-run smoke harness for the live Steam network paths. The test suite has no live-network tests, so this is the end-to-end check against real Steam endpoints |
| **SteamWorkshopSweep** | `cd tools/SteamWorkshopSweep && dotnet run` | net10.0-windows | PadForge.SteamWorkshop | Mass wild-corpus regression sweep for the Workshop config translator: harvests top-by-vote configs for every game in `games.csv`, caches the VDFs, translates everything, and reports reason keys outside the lockdown-approved set |
| **combomeasure** | `cd tools/combomeasure && dotnet run` | net10.0-windows (WPF) | WPF-UI 4.3.0 | Renders the real WPF-UI ComboBox with the app's style and font, then reads back `ActualWidth` per option per locale for the Indicator LEDs card combos |
| **PersonaVerify** | `dotnet run --project tools/PersonaVerify -- [diagLogPath]` | net10.0-windows10.0.26100.0 | NAudio 2.2.1 | Consumer-side integration check for HIDMaestro composite USB personas. Measures at the persona's own WASAPI endpoints instead of trusting PadForge's internal counters, which read healthy while Windows received full-scale noise. Also renders four channels (speaker on 1/2, authored haptics on 3/4) so the haptics lane is exercised with no game running. Pass a `PADFORGE_DIAG` log path for the log-backed checks. The audio checks run without it |
| **WdgProbe** | `dotnet run --project tools/WdgProbe -- [seconds]` | net10.0-windows | PadForge.Engine, System.Management 10.0.11 | Runs the handheld hidden-button learner's own path outside the app (#343): dumps the firmware ACPI `_WDG` table, lists the WMI event classes that pass the gate, then subscribes and prints every event for the given seconds. Compiles the app's `AcpiWmi.cs` and `WmiEventRuntime.cs` directly, so it cannot drift from what PadForge does |

The v2 vJoy SDK utilities and the ad-hoc vJoy diagnostic scripts were deleted during the 4.1.0 cycle (dead-feature cleanup: `tools/` went from ~128 entries to 16, and has grown back to 35 with the capture, tracing, and asset-generation scripts). Nothing in `tools/` targets the deprecated vJoy stack anymore.

### Development Scripts

| Script | Purpose |
|--------|---------|
| `deploy.ps1` | Kill running instance, copy the published exe to `C:\PadForge`, relaunch |
| `kill_padforge.ps1` | Elevated kill of a running PadForge instance |
| `diag-sweep.ps1` | Runtime self-diagnostics harvest: deploys the fresh build, launches with `PADFORGE_DIAG` armed, walks every page via UI Automation so lazily realized templates evaluate their bindings. Must run elevated or UIA sees zero elements |
| `capture_all.ps1` | Captures all wiki/README screenshots in one run: backs up `PadForge.xml`, injects test data, drives the UI. `capture_all_wrapper.ps1` runs it elevated with logging |
| `prep_xml_for_capture.ps1` | Preps `PadForge.xml` with 5 slot types and sample macros for screenshot runs. `prep_xml_for_capture_wrapper.ps1` adds logging |
| `convert_screenshots.ps1` | Converts and renames captured wiki images into `screenshots/` |
| `add_slots_via_ui.ps1` | Restores a `PadForge.xml` backup, then adds slot types via UI Automation |
| `capture_colorways.ps1` | Captures the themed-colorway shots by writing `PadForge.xml` state (`Model3DAppearances`, `Use2DControllerView`, slot types) rather than driving the appearance picker, which is one of the two least reliable UI paths for automation |
| `capture_vr.ps1` | Same state-injection approach, for the VR controller shots |
| `capture_web.ps1` | Recaptures the two Web Controller shots against a proven-live server. Refuses to capture until an HTTP 200 comes back, after both shots shipped as Edge's "localhost refused to connect" page |
| `capture_mouse_gestures.ps1` | Recaptures the Mouse tab shot alone, with the same seven-slot topology the rest of the gallery shows. Two minutes instead of the full run's twenty five |
| `mirror_screenshots.py` | Mirrors captured screenshots into the repo and the website. Any destination without a source is an error, not a note, because every stale picture this project shipped came from a mirror step that skipped one silently |
| `btaudio-trace.ps1` | Launches the deployed build with the diagnostic mirror armed and tails the `BTAUDIO` heartbeat, one line per second per pad while the DualSense Bluetooth stream thread lives. Its absence is a finding: the thread stopped |
| `button-trace.ps1` | Tails `BTNSURFACE` and `BTNEDGE` to answer why a mapped button does nothing. `gp=0 raw=1` is SDL's gamepad mapping dropping it, `gp=0 raw=0` is nothing arriving from the pad |
| `effect-trace.ps1` | Tails `DS5EFFECT` for ghost adaptive triggers after a game exits: enqueues, queue depth and drops, and whether writes are still going out |
| `steam_controller_2015_mesh.py` | Converts Valve's 2015 Steam Controller STEP assembly into PadForge's per-part OBJs. Meshes the CAD rather than decimating the vendor STLs |
| `steam_controller_2026_mesh.py` | Converts Valve's 2026 Steam Controller STEP into per-part OBJs. Valve shipped one merged solid, so the parts are found in the geometry |
| `steam_controller_2026_pads.py` | Splits the 2026 trackpad meshes into connected components and keeps only each pad's own surface, so hovering a trackpad stops lighting a rear paddle |
| `steam_deck_stick_well.py` | Cuts the disc capping each Steam Deck stick well and drops a dark socket behind it, so the stick has an opening under it |
| `probe_macro_list.ps1` | Dumps control type, class, and name of everything on the Macros tab, so the capture harness's macro-presence gate can match on what UI Automation really exposes |
| `verify_site_carousel.ps1` | Opens padforge.org in a visible browser and screenshots the finish carousel twice seconds apart to prove it advances. Headless cannot answer this, because the carousel pauses on `document.hidden` |
| `overlay_positions.py` | Generates 2D overlay positions from labeled Gamepad-Asset-Pack SVGs. Positions are generated, never placed by eye |
| `gen_2d_colorways.py` | Emits the 2D colorway art for the five stock families plus the derived DualSense Edge set. Only sprites that differ from the default are written |
| `gen_dualsense_edge_art.py` | Extends the DualSense 2D set into `2DModels/DUALSENSEEDGE`, adding the four extra controls as floating tiles |
| `gen_switchpro_s2_art.py` | Extends the Switch Pro 2D set into `2DModels/SWITCH2PRO`, adding the C button and the GL/GR grip buttons. Runs before `overlay_positions.py`, which reads the base it writes |
| `gen_mouse_art.py` | Renders the vendored mouse SVG into the layers the KBM preview composites |

## Troubleshooting Build Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `SDL3.dll` not found at runtime | DLL not in `Resources\SDL3\x64\` | Download from SDL3 releases or build from fork |
| MIDI package not found | `nuget.config` missing or `nuget-local/` folder missing | Ensure both are present at solution root |
| Missing WPF types | Using `dotnet build` instead of `dotnet publish` for deployment | Always use `dotnet publish -c Release` for deployment |
| `System.Drawing` ambiguity | WinForms implicit usings conflict with WPF | Ensure `<Using Remove="System.Drawing" />` is in csproj |
| HelixToolkit errors | Package restore failed | Run `dotnet restore` first |
| Large exe size (~350 MB) | Expected. Self-contained with bundled .NET runtime, WPF native libs, the HIDMaestro SDK, and every embedded mesh, driver, and asset | `EnableCompressionInSingleFile` already enabled |
| CI build fails | .NET 10 SDK not available in runner | Check `actions/setup-dotnet` version supports .NET 10 preview |
| `HIDMaestro.Core` reference fails to resolve | `Resources/HIDMaestro/HIDMaestro.Core.dll` missing or wrong build | Drop a Release-build `HIDMaestro.Core.dll` from a tagged HIDMaestro release into `Resources/HIDMaestro/` |

---

## See Also

- [Architecture Overview](architecture-overview.md): Solution structure, dependencies, design philosophy
- [Engine Library](engine-library.md): Shared data types, SDL3 P/Invoke, device wrappers
- [Settings and Serialization](settings-and-serialization.md): XML persistence, data models
- [SDL3 Integration](sdl3-integration.md): Custom SDL3 fork, build instructions
- [Driver Installation Internals](driver-installation-internals.md): Driver lifecycle (HIDMaestro, HidHide, MIDI Services) and legacy v2 cleanup
- [HIDMaestro Deep Dive](hidmaestro-deep-dive.md): HM SDK surface, OpenXInput shim, four-surface filtering architecture
- [DSU Protocol Implementation](dsu-protocol.md): `DsuDiag` diagnostic tool in `tools/`

---

*Last updated for PadForge 4.5.1.*
