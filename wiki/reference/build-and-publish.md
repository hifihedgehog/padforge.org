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
│   │                         SettingResetButton, TriggerTravelArc)
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
├── PadForge.NativeChecks/    Console helper (net10.0-windows) that PadForge.Tests runs in a child
│                             process against the bundled x64 SDL3.dll
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
    ├── rowmeasure/           WPF width-measurement harness for fixed-size rows, every locale
    ├── deploy.ps1            Copy the published exe to C:\PadForge and restart
    └── *.ps1 / *.py          Screenshot capture, UIA diagnostics, runtime traces, asset
                              generation (see Development Scripts)
```

Line endings are repo-enforced. `.gitattributes` opens with a `* text=auto` rule, so a text file committed from a CRLF working tree is still stored with LF. A CRLF copy of one file once turned a 167-line change into a 12,000-line diff. Two narrower rules set the checkout: the driver INFs under `PadForge.App/Resources` check out with CRLF, because a signed catalog hashes the exact bytes of each INF it covers, and `*.sh` scripts check out with LF, because bash reads a carriage return as part of each command.

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| .NET SDK | 10.0+ | `net10.0-windows10.0.26100.0` target framework |
| Windows SDK | 10.0.26100.57 | Set via `WindowsSdkPackageVersion` in App csproj |
| Windows | 10 or 11 | WPF builds on Windows only. An x64 machine builds both the x64 and the ARM64 exe |
| Visual Studio (optional) | 2022+ | Not required. Its own MSBuild runs on .NET Framework, which lacks the Brotli the art packer needs, so build with the `dotnet` CLI |

Minimum supported OS: Windows 10 1809 (build 17763), set via `SupportedOSPlatformVersion` in the App csproj.

All native DLLs, the HidHide installer, and model assets are checked into the repository. The build downloads nothing beyond the NuGet restore. The Windows MIDI Services SDK installer is fetched from GitHub releases on demand at runtime when the user clicks Install, not at build time.

## Build Commands

### Debug Build

```bash
dotnet build -c Debug
```

Output: `PadForge.App/bin/Debug/net10.0-windows10.0.26100.0/win-x64/`

Suitable for development and debugging. **Not deployable**. Produces about 300 loose files, the self-contained .NET runtime among them, instead of one exe.

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

Output: `PadForge.App/bin/Release/net10.0-windows10.0.26100.0/win-arm64/publish/`, one ~310 MB `PadForge.exe`. It cross-compiles on an x64 machine. With no `-r` the build is x64, so every existing command produces what it always has. See [Building for ARM64](#building-for-arm64) for what differs.

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

Every bundled native binary sits in a folder named for its architecture: `Resources/SDL3/x64` and `Resources/SDL3/arm64`, and the same pair for `OpenXInput` and `VisualCpp`. `Interhaptics` has an `x64` folder only. `NativeBinaryArchitectureTests` reads the PE header of every `.dll` and `.sys` in an `x64` or `arm64` folder under `Resources` and fails when a file's machine type differs from its folder name. It exists because Microsoft's own ARM64 redist folder ships a `vcruntime140_1.dll` that is an x64 image.

A publish for either architecture is refused by the `RequireBundledNatives` target if `SDL3.dll` or `libusb-1.0.dll` is missing from `Resources/SDL3/<arch>`, or `xinput1_4.dll` from `Resources/OpenXInput/<arch>`, and an ARM64 publish if `libvosk.dll` is missing from `Resources/Vosk/arm64`. Those `Content` items are conditioned on `Exists`, so without that target a missing DLL would publish anyway, and the auto build runs no tests that would notice. Without `SDL3.dll` the input engine cannot start. Without `libusb-1.0.dll` wired Switch 2 controllers and the GameCube adapter never open, which is the 4.5.0 regression. Without the fork's `xinput1_4.dll` SDL loads the system one and PadForge reads its own virtual controllers back as input. The same target refuses any runtime other than `win-x64` and `win-arm64`, which would otherwise be handed the x64 libraries. A plain `dotnet build` is let through with a message. `SDL3.dll` and `xinput1_4.dll` come from the forks, the ARM64 pair cross-compiled with `cmake -A ARM64`.

Three features have a native half, and `PadForge.Engine/Common/PlatformSupport.cs` decides each one by the architecture that half follows:

| Feature | Decided by | On ARM64 |
|---|---|---|
| HidHide | Machine architecture (`OSArchitecture`) | A kernel driver has to match the machine, so the choice follows the machine and not the build. An ARM64 machine gets HidHide's ARM64 driver (`Resources/HidHideArm64/HidHide_ARM64.zip`, driver 1.6.280.0), installed with HidHide's tool (`nefconc.exe`, nefcon 1.20.0, ARM64). An x64 machine gets the x64 MSI, which only the x64 build embeds |
| Vosk voice engine | Process architecture (`ProcessArchitecture`) | The ARM64 build bundles `Resources/Vosk/arm64/libvosk.dll`. The Vosk package carries the x64 one. Both builds embed the model |
| Razer Sensa HD haptics | Process architecture | Not available. The Interhaptics SDK ships for Win32 and x64 only, and Razer lists Synapse for x86-64 Windows only. `SensaHapticsService` reports `Unsupported` |

Each rule names the architectures that have the native half and answers false for every other.

`HidHideArm64Installer` performs upstream's documented manual install in the order HidHide's own setup uses: `nefconc install HidHide.inf root\HidHide`, then an upper class filter on HIDClass, XnaComposite and XboxComposite, and on removal the filters first, then the device. A class filter entry that names a driver which is not running can stop every keyboard and mouse from starting. HidHide's x64 setup ships a watchdog service for that and an ARM64 install has none. So the filters are added only after the driver's control device opens, a removal that stops part way with the device node still in tries to put them back, and at startup on an ARM64 machine PadForge takes out a filter entry whose service is gone, or is registered and stopped, which is the watchdog's own condition. nefcon's `remove` takes the device node alone, so the service and the driver package stay, as they do after HidHide's own uninstall. Nothing registers this install with Windows Installer, so "installed" is read from the service, the device node and the HIDClass filter. `HidHideArm64InstallerTests` pins that order and the hashes of both bundled files.

Nobody publishes `libvosk.dll` for Windows ARM64. Vosk's maintainer wrote the recipe for one (vosk-api 1b308a30, `travis/Dockerfile.winaarch64`) and never shipped its output. `tools/build-libvosk-arm64.sh` is that recipe with the same flags and every source pinned to a commit, run from Git Bash with a portable llvm-mingw toolchain. It refuses a build folder that is not empty, because what comes out is shipped. Its header lists each difference from upstream with the reason. The DLL links its C++ runtime statically, so it imports `KERNEL32` and the Universal C Runtime alone, where the x64 one needs three MinGW DLLs beside it. The same recipe aimed at x64 produced recognition output identical to the official x64 library, word timings included. Two runs of the script differ in bytes, so the bundled file is pinned by hash, and `BundledVoskArm64Tests` reads its export and import tables and checks that it exports every function the managed binding calls and imports no DLL the ARM64 build lacks. `PlatformSupportTests` pins both halves of that rule on an x64 bench, because each rule is a pure function of the architecture it is handed. An x64 bench cannot tell a live property wired to the machine from one wired to the process, since both are x64 there, so the same tests also pin that wiring in the source.

Four more features load a library the vendor's own software installs, and PadForge has no gate for them because the load itself answers. `LogitechGkey.dll` comes in x64 and x86 only (`LogitechGKeyCatalog`), and the SteamVR input service loads `bin\win64\openvr_api.dll` (`OpenVrConsumerService`), so an ARM64 process gets neither. The LIGHTSYNC engine and the OpenXR runtime are whatever the registry names, so they work in an ARM64 process only if the vendor registers an ARM64 one. None of these crashes the app. G-keys, LIGHTSYNC and OpenXR each show a status line, and the SteamVR input service logs the failed load and keeps retrying.

One more ARM64 piece lives in the SDL fork. Its Xbox Elite paddle reader (`SDL_XINPUT_PADDLES`) builds for x64 and, since fork commit a1416320e2, for ARM64. It has two routes. The Bluetooth route uses public WinRT calls. The USB and Xbox Wireless Adapter route reads an undocumented format from the Windows GameInput service, so the fork switches it on only where the files behind that format belong to a version family it has read, by product version: `GameInputSvc.exe` and `GameInput.dll` 0.2309.26100 from revision 8875, `Windows.Gaming.Input.dll` 10.0.26100 from 8737 and `drivers\xboxgip.sys` 10.0.26100 from 8972. `GameInputRedist.dll` is optional, and must be major version 3 when it is there. That is Windows 11 24H2 or 25H2 at build 26100.8973 or 26200.8973 (July 28, 2026) or later. On Windows 10 and older Windows 11 the route stays off, and paddles are read over Bluetooth only. The version resource carries no architecture, so one table serves x64 and ARM64. Until fork commit 5df5eff539 the check was five exact file hashes. They matched the Windows updates dated 2026-08-27 to 2026-09-14 with GameInput redistributable 3.3.221.0, and no ARM64 installation (hifihedgehog/SDL#32). When the route stays off, the joystick's `SDL.joystick.xinput.paddle.error` property holds the reason. PadForge does not read it yet.

The reader is C++, so `SDL3.dll` imports `msvcp140.dll` on both architectures, and `vcruntime140_1.dll` on x64, where that file's exception handler exists. Neither `msvcp140.dll` nor `vcruntime140.dll` carries an `Exists` condition, so a missing one stops the build and names it. `BundledSdlRuntimeImportsTests` reads each bundled `SDL3.dll` for the runtime DLLs it names and fails when one is not in that architecture's `Resources/VisualCpp` folder. It was written before the ARM64 reader was delivered and failed on that delivery, which is how the ARM64 `msvcp140.dll` came to be bundled with it.

Vosk's NuGet targets add their win-x64 natives whenever the BUILD machine is Windows, whatever the target. `DropX64OnlyNativesOnArm64` takes them back out of an ARM64 build, which gets its own `libvosk.dll` from a `Content` item. An ARM64 publish without that file is refused by `RequireBundledNatives`.

Drivers follow the machine. HIDMaestro 1.9.0 and BthPS3 3.0.0 each carry an x64 and an ARM64 payload, both builds embed both BthPS3 payloads because the driver is chosen by the machine and not by the build, `Ds3DriverInstaller.SignWinUsbPackage()` builds its catalog for `10_ARM64` on an ARM64 machine, and the Windows MIDI Services download picks the `-arm64` installer there.

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
<Compile Include="..\SharedVersion.cs" Link="Properties\SharedVersion.cs" />
```

`SharedVersion.cs` carries `AssemblyVersion` and `AssemblyFileVersion`. The assemblies cannot drift apart because they compile against the same file. `Properties/AssemblyInfo.cs` in the App and the Engine carries the other assembly metadata (title, copyright, COM GUID, and theme info in the App). The SteamWorkshop one carries only `InternalsVisibleTo`. None of them carries version attributes. Every project sets `<GenerateAssemblyInfo>false</GenerateAssemblyInfo>` so the build does not regenerate either file.

**Important:** Edit `SharedVersion.cs` to bump the version. Never re-introduce `AssemblyVersion` to `Properties/AssemblyInfo.cs`. It would override the shared version on whichever assembly carries it and the drift guard breaks. GitHub Releases use git tag names (e.g., `v4.4.0`) as the user-facing version, but the binary's `AssemblyVersion` should match. The current shared version is `4.5.3.0`.

### Build Identity

Every build between two releases carries the same version, so the App also stamps the commit it was built from. The `StampBuildIdentity` target in the App csproj runs before `CoreCompile`, reads `git`, and writes `PadForgeBuildIdentity.g.cs` into the intermediate folder with three `AssemblyMetadata` attributes: the commit count (`PadForgeBuildNumber`), the seven-character hash (`PadForgeCommit`) and the full hash (`PadForgeCommitSha`). It stamps them only in a full, non-shallow clone of this repository whose `HEAD` holds `PadForge.App/PadForge.App.csproj`. A shallow clone, a tree with no git, or a checkout nested inside another repository stamps nothing. The target clears the three properties before it reads git, so a `/p:` override on the command line does not reach the exe.

`BuildIdentity.Display` turns the stamp into the text the Diagnostics card's App Version shows, for example `4.5.3 (r3682@176208e)`, or the version alone when nothing was stamped. The in-app updater orders dev builds by the commit count. See [Updates Internals](updates-internals.md#build-identity).

## NuGet Dependencies

### PadForge.App

| Package | Version | Source | Purpose |
|---------|---------|--------|---------|
| **CommunityToolkit.Mvvm** | 8.2.2 | nuget.org | MVVM: `ObservableObject`, `RelayCommand` |
| **Concentus** | 2.2.2 | nuget.org | Pure-C# Opus encoder and decoder for the DualSense Bluetooth speaker and microphone streams |
| **HelixToolkit.Core.Wpf** | 2.27.3 | nuget.org | 3D viewport rendering (OBJ model loading, camera, lighting) |
| **Microsoft.Windows.Devices.Midi2** | 1.0.16-rc.3.7 | **nuget-local/** | Windows MIDI Services SDK for virtual MIDI device creation |
| **NAudio.Wasapi** | 2.2.1 | nuget.org | WASAPI capture, playback and endpoint enumeration, Media Foundation decode, and mixing through its NAudio.Core dependency: the controller speaker mirror, macro sounds, voice-macro microphones, bass shakers, and bass-driven rumble detection |
| **Nefarius.Utilities.DeviceManagement** | 5.2.0 | nuget.org | Driver-store install, class filters, and USB CyclePort for the DualShock 3 Bluetooth stack (same library BthPS3's own installer uses) |
| **System.Management** | 10.0.11 | nuget.org | WMI queries behind the handheld hidden-button learner (ACPI `_WDG` event classes) |
| **System.Speech** | 10.0.0 | nuget.org | SAPI recognizer behind the voice-macro trigger (#317) |
| **Vosk** | 0.3.38 | nuget.org | Offline recognizer for voice macros (Apache-2.0, Alpha Cephei). Phrase-list grammar with an `[unk]` bucket, so non-phrase audio decodes as unknown. Its targets file also copies `libvosk.dll` and the MinGW runtime into the output |
| **WPF-UI** | 4.3.0 | nuget.org | Fluent Design theme for WPF (dark mode, NavigationView, controls) |

`HIDMaestro.Core` (the virtual controller client) is a project `<Reference>` with a `HintPath` into `Resources/HIDMaestro/`, not a NuGet package. The shipped DLL reports file version `1.9.0.0`, and the csproj comment naming the shipped build says v1.9.0. That comment is hand-maintained, so when the two disagree the DLL's own file version is the authority.

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
| **System.Security.Cryptography.ProtectedData** | 10.0.9 | DPAPI at-rest protection for this PC's Remote Link identity key |

All SDL3 and system interop still uses raw `[DllImport]` P/Invoke.

### Test Projects

`PadForge.Tests` and `PadForge.SteamWorkshop.Tests` both reference coverlet.collector 6.0.4, Microsoft.NET.Test.Sdk 17.14.1, xunit 2.9.3, and xunit.runner.visualstudio 3.1.4. `PadForge.Tests` also references Jint 4.16.2, a JavaScript interpreter its touchpad web-page tests run the page script in.

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
| `msvcp140.dll` | `<Content>`, `Resources/VisualCpp/<arch>/` | `SDL3.dll`, for its C++ Elite paddle reader | Yes |
| `vcruntime140_1.dll` | `<Content>`, `Resources/VisualCpp/x64/` | The x64 `SDL3.dll`. It holds an exception handler that exists for the x64 ABI alone | No |
| `HAR.dll` | `<Content>`, `Resources/Interhaptics/x64/` | `SensaHapticsService` (#374), P/Invoked lazily | No |
| `Interhaptics.RazerProvider.dll` | `<Content>`, `Resources/Interhaptics/x64/` | Loaded by `HAR.dll` as its Razer Sensa backend | No |
| `libvosk.dll` | x64: Vosk 0.3.38 package targets. ARM64: `<Content>`, `Resources/Vosk/arm64/` | `Vosk.dll`, behind `VoskVoiceEngine` (#317) | Yes |
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
- **Replaces the system `xinput1_4.dll` via DLL search order.** In a loose build the DLL sits in the application directory, which Windows searches before `System32` for non-KnownDLLs. In the single-file exe it is extracted to `%TEMP%\.net\PadForge\<hash>\`, and `App.OnStartup` passes that folder to `SetDllDirectory`, which also puts it ahead of `System32`. Either way, when SDL3 calls `LoadLibrary("xinput1_4.dll")` this copy resolves first and SDL's XInput backend uses it instead of Microsoft's.
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
| `HidHide_1.5.230_x64.exe` | HidHide setup for x64 machines. Hides physical controllers from other applications. Embedded in the x64 build only, since only that build can run on an x64 machine |
| `HidHideArm64/HidHide_ARM64.zip` | HidHide's Microsoft-signed ARM64 driver package (driver 1.6.280.0), byte for byte as upstream publishes it. Embedded in both builds, because the driver is chosen by the machine and not by the build |
| `HidHideArm64/nefconc.exe` | nefcon 1.20.0, the ARM64 console build. HidHide's own install tool, which `HidHideArm64Installer` runs as a native child process. Embedded in both builds |

The HIDMaestro user-mode driver is **not** managed by `DriverInstaller`. The driver binaries, INF, profiles, and signing tools all ship inside `HIDMaestro.Core.dll` (referenced as a `<Reference>`, so it's bundled into the single-file EXE). `InputManager` calls `HMContext.InstallDriver()` on first start (from `EnsureHMaestroContext()` in `PadForge.App/Common/Input/`), which registers the driver with Windows through `pnputil` from inside PadForge's already-elevated process. No separate installer EXE. The OpenXInput shim (`xinput1_4.dll` only) ships as `<Content>` and is bundled into the single-file EXE via `IncludeNativeLibrariesForSelfExtract`. `devobj.dll` is deliberately not shipped. See [Driver Installation Internals](driver-installation-internals.md) for why a bundled stub would crash HID class enumeration. The Windows MIDI Services SDK is downloaded from the GitHub releases API on demand when the user clicks Install, then run with `/install /quiet /norestart`.

PadForge v2's vJoy and ViGEmBus installers are no longer bundled. v4 detects either driver on first launch and offers to uninstall via the legacy driver cleanup dialog. See [Driver Installation Internals](driver-installation-internals.md).

### BthPS3 / DS3 Bluetooth Drivers (EmbeddedResource)

```xml
<EmbeddedResource Include="Resources\BthPS3\**\*.*">
  <LogicalName>BthPS3.%(RecursiveDir)%(Filename)%(Extension)</LogicalName>
</EmbeddedResource>
```

Microsoft-signed BthPS3 + BthPS3PSM drivers (nefarius release) and the DS3 WinUSB INF, embedded so the single-file app can install them at DualShock 3 pairing time with no MSI and no external installer. `Ds3DriverInstaller.ExtractDrivers()` walks every manifest resource whose name starts with `BthPS3.`, strips that prefix, and drops the files under `%TEMP%\PadForge\BthPS3Drivers\` before running `pnputil`. The explicit `LogicalName` preserves the subdirectory layout inside the manifest name. The two 3.0.0 INFs that carry a binary, `BthPS3.inf` and `BthPS3PSM.inf`, each name both architectures, `[SourceDisksFiles.amd64]` and `[SourceDisksFiles.arm64]`, and Windows installs the binary that matches the machine, so both builds of PadForge embed both.

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

The Sony and Xbox families are split one folder per colorway. The counts below are one colorway's full part set. Not every colorway folder carries its own (see `SharedGeometry` under Packed Art).

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
| `3DModels/**/*.png` | `.pngbr` | Inflates the IDAT data and re-emits it as one IDAT of stored deflate blocks, then Brotli over the whole file |
| `VoiceModels/*.zip` | `.zipbr` | Re-emits the zip entries stored, then Brotli over the archive |

The PNG and zip cases both follow the same rule: store first, compress once.
Deflating data that is already deflated costs size, so the packer strips the
inner compression and lets Brotli see the raw bytes. That is where most of the
saving comes from. Opaque atlases skip the whole path because they ship as
JPEG.

Two traps the target handles explicitly. Packing is incremental on file
timestamps, so art that has not changed is not repacked and only the first
build pays. And each packed file is named for the resource it becomes, so its
name carries dots. MSBuild reads the segment before the extension as a culture
when it matches one. `Switch2Pro/GL.obj` became
`PadForge._3DModels.Switch2Pro.GL.objbr`, whose `GL` is Galician, and that mesh
was routed into a satellite assembly and disappeared from the pad. The
`EmbeddedResource` items carry `WithCulture="false"` for that reason.

A separate `SharedGeometry` table in `ControllerModelBase` names twelve
colorways whose meshes match a sibling colorway's. Each one keeps only the
meshes that differ, none for most of them, and loads the rest from the
sibling, which drops 352 duplicate meshes from the bundle. Eight Xbox Series
skins (Sonic and the seven Razer editions) carry no meshes at all: they load the
Carbon set whole and bring only their own shell texture.

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
| `WebAssets/gamepad.html` | Browser Gamepad page: forwards a controller paired to the phone or built into the handheld |
| `WebAssets/css/controller.css` | Gamepad styling |
| `WebAssets/js/controller_client.js` | WebSocket client logic |
| `WebAssets/js/custom_client.js` | Custom layout client logic |
| `WebAssets/js/gamepad_client.js` | Gamepad API reader and WebSocket forwarding for the Browser Gamepad page |
| `WebAssets/js/fullscreen.js` | Fullscreen toggle for the web controller pages, added where the browser supports element fullscreen |
| `WebAssets/js/nipplejs.min.js` | Virtual joystick library |

### Voice Model (EmbeddedResource)

`VoiceModels/vosk-model-small-en-us-0.15.zip`, the offline Vosk recognizer model behind voice macros (#317). The `EmbedPackedArt` target above repacks it to about 35 MB. It ships inside the exe rather than downloading on first use, so voice macros work on a machine with no internet. Vosk loads a model from a folder, so once voice macros are on and have phrases, `VoskModelStore` unpacks it to `%TEMP%\PadForge\voice-models` and loads it from there.

### License Notices (EmbeddedResource)

```xml
<EmbeddedResource Include="..\LICENSE" LogicalName="PadForge.ThirdPartyNotices.txt" />
```

The repository's `LICENSE`, which carries PadForge's license, the third-party licenses and attributions, and their full license texts, is embedded as `PadForge.ThirdPartyNotices.txt`, so the notices travel inside the single-file exe. No code reads it.

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

1. **Checkout**. `actions/checkout@v5`, `fetch-depth: 0` (full history for commit counting, which the [build identity](#build-identity) stamp also needs)
2. **Setup .NET**. `actions/setup-dotnet@v5`, `dotnet-version: 10.x`
3. **Get build info**. Commit count and 7-character SHA, exported as job outputs. It runs before Publish so that a failed publish cannot leave its copy of those outputs blank
4. **Publish**. `dotnet publish PadForge.App/PadForge.App.csproj -c Release`, plus `-r win-arm64` for the ARM64 leg
5. **Upload artifact**. `actions/upload-artifact@v7`, publish directory as `PadForge_r{COMMIT_COUNT}@{COMMIT_SHORT}`, with `-arm64` appended for ARM64

### Archive job (push only)

`archive` puts every build into the rolling archive. It runs under `!cancelled()`, so a failed ARM64 build does not stop it and a canceled run publishes nothing. It cannot publish without x64: the x64 artifact download is its first step and fails before any release is touched. It sits in no concurrency group and takes no lock, because the archive must never lose a build, and runs for different commits upload files with different names.

1. **Download x64 build**, then **Download ARM64 build** with `continue-on-error`. `actions/download-artifact@v8`
2. **Package release zips**. Deletes any `*.pdb`, then `7z a -mx=9` over each publish directory into `PadForge_r{N}@{SHA}.zip` and `PadForge_r{N}@{SHA}-arm64.zip`. With no ARM64 build, x64 is released alone
3. **Release rolling dev archive**. Uploads the zips to the active archive part with `--clobber`, rolling to a new part first when the active one is full

### Latest job (push only)

`latest` rewrites `latest-v4-dev`. It runs only after a successful `archive` job, on `ubuntu-latest`, in a concurrency group per branch: one run publishes, one waits, and a third that arrives replaces the waiting one.

1. **Decide whether this commit should be published**. Builds do not finish in push order, so the job asks the branch as it is now. A commit that a force-push left out of the branch's history is skipped, and so is a commit older than the one already published. An API error fails the job and leaves the published release untouched
2. **Fetch this build from the archive**. Downloads the zips the archive job uploaded and renames them `PadForge.zip` and `PadForge-arm64.zip`, so nothing is compressed twice
3. **Stage, then swap**. Deletes staging drafts that dead runs left, creates the new release as a draft titled `PadForge r{N}@{SHA}` with its zips attached, and checks that every file uploaded. Only then does it delete the old release, move the `latest-v4-dev` tag to this commit, and publish the draft under that tag. It reads the release back and fails if the files or the commit differ

### Automatic Releases (push to v4-dev only)

On push (not PR), the workflow maintains two GitHub releases keyed off the branch ref name:

| Release | Behavior |
|---------|----------|
| **`archive-v4-dev`** | Accumulates every build as `PadForge_r{N}@{SHA}.zip` and `PadForge_r{N}@{SHA}-arm64.zip`. Uploads with `--clobber`. Preserves the tag across builds. Rolls to a new part when full (see below). |
| **`latest-v4-dev`** | Replaced when a push's build is newer than the published one. Titled `PadForge r{N}@{SHA}`, with `PadForge.zip` (x64) and `PadForge-arm64.zip` from that build. The "always current" download link. The replacement is built as a draft and swapped in only once it holds every file, so a failed upload never leaves the link without a download. |

Both are pre-releases. The notes of `latest-v4-dev` link to the archive part that holds its build and to the run's log, and the first archive part's notes link to `latest-v4-dev`.

The in-app updater's pre-release channel reads `latest-v{major}-dev`: it takes the build number from the title `PadForge r{N}@{SHA}` and picks `PadForge.zip` or `PadForge-arm64.zip` by name. A comment in `build.yml` says so. Renaming the tag, the title format, or either zip breaks that channel for every installed copy. See [Updates Internals](updates-internals.md#couplings).

**Rolling archive parts.** GitHub caps a release at 1000 assets. A push adds up to two assets, so the workflow watches the active archive and, once it reaches 990 assets, creates the next numbered part (`archive-v4-dev-2`, `archive-v4-dev-3`, and so on) targeting the current commit. The count is read without a lock, so runs that overlap all see the same number, and 990 leaves room for five of them at once. Each new part's notes link back to the previous part.

### Artifact Naming

Format: `PadForge_r{COMMIT_COUNT}@{7-char COMMIT_SHA}` (e.g., `PadForge_r342@f35bb36`), with `-arm64` appended for the ARM64 build

### Environment Variables

```yaml
env:
  DOTNET_NOLOGO: true
  DOTNET_CLI_TELEMETRY_OPTOUT: true
```

### Formal Releases

Created manually via `gh release create` with a version tag (e.g., `v4.4.0`, `v4.4.0-beta1`). The in-app updater's release channel reads GitHub's latest release and accepts only a `vX.Y.Z` tag with no suffix, so a suffixed tag is never offered as an update. See [Release Workflow](#release-workflow) below.

## Deployment

PadForge is portable. No installer required.

### Local Deployment

Copy the publish output to any folder:
```bash
cp PadForge.App/bin/Release/net10.0-windows10.0.26100.0/win-x64/publish/PadForge.exe C:\PadForge\PadForge.exe
```

There are no companion files. Every native library (`SDL3.dll`, `libusb-1.0.dll`, `xinput1_4.dll`, the Visual C++ runtime, `HAR.dll`, `Interhaptics.RazerProvider.dll`, `libvosk.dll`, and the MinGW runtime) is folded into the single-file bundle on publish and extracted to `%TEMP%\.net\PadForge\<hash>\` at first launch. The gamepad mapping database is embedded in the assembly, so no `.txt` file sits alongside the exe either. A deploy is one `PadForge.exe`.

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

Each publish directory holds one file, so the 4.5.3 assets are `PadForge-v4.5.3-win-x64.zip` and `PadForge-v4.5.3-win-arm64.zip`, each containing `PadForge.exe` and nothing else. Only the x64 exe can be run on an x64 bench.

The in-app updater finds a release by these names: a `vX.Y.Z` tag with no suffix, zips ending in `-win-x64.zip` and `-win-arm64.zip`, and `PadForge.exe` at the root of each zip. It offers an asset only when GitHub reports a SHA-256 `digest` for it. See [Updates Internals](updates-internals.md#couplings).

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
| **rowmeasure** | `cd tools/rowmeasure && dotnet run` | net10.0-windows (WPF) | WPF-UI 4.3.0 | The same measurement for the fixed-size rows the 2026-09-15 audit flagged: the Profiles shortcut row, the raw hat strip, the equalizer row and the gesture recorder's hint, in every locale |
| **PersonaVerify** | `dotnet run --project tools/PersonaVerify -- [diagLogPath]` | net10.0-windows10.0.26100.0 | NAudio 2.2.1 | Consumer-side integration check for HIDMaestro composite USB personas. Measures at the persona's own WASAPI endpoints instead of trusting PadForge's internal counters, which read healthy while Windows received full-scale noise. Also renders four channels (speaker on 1/2, authored haptics on 3/4) so the haptics lane is exercised with no game running. Pass a `PADFORGE_DIAG` log path for the log-backed checks. The audio checks run without it |
| **WdgProbe** | `dotnet run --project tools/WdgProbe -- [seconds]` | net10.0-windows | PadForge.Engine, System.Management 10.0.11 | Runs the handheld hidden-button learner's own path outside the app (#343): dumps the firmware ACPI `_WDG` table, lists the WMI event classes that pass the gate, then subscribes and prints every event for the given seconds. Compiles the app's `AcpiWmi.cs` and `WmiEventRuntime.cs` directly, so it cannot drift from what PadForge does |

The v2 vJoy SDK utilities and the ad-hoc vJoy diagnostic scripts were deleted during the 4.1.0 cycle (dead-feature cleanup: `tools/` went from ~128 entries to 16, and has grown back to 37 with the capture, tracing, and asset-generation scripts). Nothing in `tools/` targets the deprecated vJoy stack anymore.

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
| `capture_colorways.ps1` | Captures the themed-colorway shots by writing `PadForge.xml` state (`SlotModel3DAppearances`, `Use2DControllerView`, slot types) rather than driving the appearance picker, which is one of the two least reliable UI paths for automation |
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
| `verify_site_carousel.ps1` | Opens the padforge.org page (the local repository copy by default) in a visible browser and screenshots the finish carousel twice, 11 seconds apart by default, to prove it advances. Headless cannot answer this, because the carousel pauses on `document.hidden` |
| `overlay_positions.py` | Generates 2D overlay positions from labeled Gamepad-Asset-Pack SVGs. Positions are generated, never placed by eye |
| `gen_2d_colorways.py` | Emits the 2D colorway art for the five stock families plus the derived DualSense Edge set. Only sprites that differ from the default are written |
| `gen_dualsense_edge_art.py` | Extends the DualSense 2D set into `2DModels/DUALSENSEEDGE`, adding the four extra controls as floating tiles |
| `gen_switchpro_s2_art.py` | Extends the Switch Pro 2D set into `2DModels/SWITCH2PRO`, adding the C button and the GL/GR grip buttons. Runs before `overlay_positions.py`, which reads the base it writes |
| `gen_mouse_art.py` | Renders the vendored mouse SVG into the layers the KBM preview composites |

## Troubleshooting Build Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `SDL3.dll` missing (a publish is refused, a plain build prints a message) | DLL not in `Resources\SDL3\<arch>\` | Build it from the PadForge SDL fork. An upstream SDL3 release lacks the fork's HIDMaestro filter, Switch 2 Pro driver and PS5 status bytes |
| MIDI package not found | `nuget.config` missing or `nuget-local/` folder missing | Ensure both are present at solution root |
| Missing WPF types | Using `dotnet build` instead of `dotnet publish` for deployment | Always use `dotnet publish -c Release` for deployment |
| `System.Drawing` ambiguity | WinForms implicit usings conflict with WPF | Ensure `<Using Remove="System.Drawing" />` is in csproj |
| HelixToolkit errors | Package restore failed | Run `dotnet restore` first |
| Large exe size (~331 MB x64, ~310 MB ARM64) | Expected. Self-contained with bundled .NET runtime, WPF native libs, the HIDMaestro SDK, and every embedded mesh, driver, and asset | `EnableCompressionInSingleFile` already enabled |
| CI build fails | .NET 10 SDK not available in runner | Check that the `actions/setup-dotnet` step still resolves `dotnet-version: 10.x` |
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
- [Updates Internals](updates-internals.md): the build identity stamp and the release names the in-app updater reads

---

*Last updated for PadForge 4.5.3.*
