# Build and Publish

Build, publish, and release reference for PadForge.

---

## Solution Structure

```
PadForge.sln
├── PadForge.Engine/          Class library (net10.0-windows)
│   ├── Common/               SDL3 P/Invoke, input types, device wrappers
│   ├── Data/                 PadSetting, UserDevice, UserSetting
│   └── Properties/           AssemblyInfo.cs
│
├── PadForge.App/             WPF application (net10.0-windows10.0.26100.0)
│   ├── Common/               SettingsManager, DriverInstaller, InputManager pipeline
│   ├── Views/                XAML pages and code-behind
│   ├── ViewModels/           MVVM ViewModels
│   ├── Services/             InputService, SettingsService, DeviceService, etc.
│   ├── WebAssets/             HTML/CSS/JS for browser virtual controller
│   ├── Models3D/             3D model classes (Xbox360 / XboxOne / DS4 / DualSense)
│   ├── Models2D/             2D overlay layout classes (5 layouts)
│   ├── 2DModels/             PNG overlay images (DS4/, DualSense/, XBOX360/, XBOXONE/, XBOXSERIES/)
│   ├── 3DModels/             OBJ meshes (DS4/, DualSense/, XBOX360/, XBOXONE/)
│   ├── Converter/            WPF value converters
│   ├── Controls/             Custom controls (RangeSlider)
│   ├── Resources/            Icons, SDL3 DLL, embedded driver installers, localization
│   └── Properties/           AssemblyInfo.cs
│
├── nuget-local/              Local NuGet source (MIDI Services SDK)
├── nuget.config               Registers nuget.org + nuget-local/ as package sources
│
└── tools/
    ├── DsuDiag/              DSU/Cemuhook diagnostic client
    ├── Ds4InputDump/         DS4 raw HID input dump (Sony Report 0x01 passthrough debug)
    ├── vJoy/                 Legacy v2 vJoy SDK / test utilities (kept for reference, unused by v4)
    ├── deploy.ps1            Build + deploy to C:\PadForge
    ├── deploy_and_restart.ps1  Deploy + restart running instance
    ├── capture_*.ps1         Wiki screenshot capture (~20 scripts, one per surface)
    └── (~50 ad-hoc diagnostic / UI-automation scripts, mostly v2 vJoy holdovers)
```

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| .NET SDK | 10.0+ | `net10.0-windows10.0.26100.0` target framework |
| Windows SDK | 10.0.26100.57 | Set via `WindowsSdkPackageVersion` in App csproj |
| Windows | 10/11 x64 | WPF + Windows-specific P/Invoke |
| Visual Studio (optional) | 2022+ | Not required; `dotnet` CLI suffices |

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
| `PadForge.exe` | ~110 MB, single-file self-contained |
| `SDL3.dll` | SDL3 native library (content item) |
| `libusb-1.0.dll` | WinUSB for Switch 2 Pro Controller (content item) |
| `xinput1_4.dll` | OpenXInput-derived shim, SDL's XInput backend (content item) |

The custom gamepad mapping database ships embedded in the assembly, not as a loose file. See [gamecontrollerdb_padforge.txt](#gamecontrollerdb_padforgetxt) under Embedded Resources.

> **Critical:** Always use `dotnet publish` for deployment, never `dotnet build`. The project is configured for single-file self-contained publish. `dotnet build` produces non-functional multi-file output.

## Single-File Publish Configuration

The App csproj defines these publish properties:

```xml
<!-- Single-file portable publish: dotnet publish -c Release -->
<PropertyGroup>
  <RuntimeIdentifier>win-x64</RuntimeIdentifier>
  <PublishSingleFile>true</PublishSingleFile>
  <SelfContained>true</SelfContained>
  <IncludeNativeLibrariesForSelfExtract>true</IncludeNativeLibrariesForSelfExtract>
  <EnableCompressionInSingleFile>true</EnableCompressionInSingleFile>
  <DebugType>embedded</DebugType>
</PropertyGroup>
```

| Property | Value | Effect |
|----------|-------|--------|
| `RuntimeIdentifier` | `win-x64` | Targets 64-bit Windows only |
| `PublishSingleFile` | `true` | Bundles all managed assemblies into one exe |
| `SelfContained` | `true` | Embeds .NET 10 runtime (no install needed on target) |
| `IncludeNativeLibrariesForSelfExtract` | `true` | Packs native DLLs into the exe. Extracted to temp dir at runtime |
| `EnableCompressionInSingleFile` | `true` | Compresses the bundle to reduce exe size |
| `DebugType` | `embedded` | Embeds debug symbols in assemblies (no `.pdb` files); preserves stack traces for crash diagnostics |

**Note:** `RuntimeIdentifier` is set unconditionally (not only during publish), so `dotnet build` also targets `win-x64` and produces a RID-specific output folder.

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

The Engine targets `net10.0-windows` (no specific SDK version needed). SDL3 and system interop use raw `[DllImport]` P/Invoke; the only NuGet references are the Remote Link crypto packages (see below).

### Assembly Versioning

App and Engine share one version via `SharedVersion.cs` at the repo root. Both csproj files link it in:

```xml
<Compile Include="..\SharedVersion.cs">
  <Link>Properties\SharedVersion.cs</Link>
</Compile>
```

`SharedVersion.cs` carries `AssemblyVersion` and `AssemblyFileVersion`. The two assemblies cannot drift apart because they compile against the same file. `Properties/AssemblyInfo.cs` in each project carries the other assembly metadata (title, copyright, COM GUID, theme info) and explicitly does **not** carry version attributes. Both projects set `<GenerateAssemblyInfo>false</GenerateAssemblyInfo>` so the build does not regenerate either file.

**Important:** Edit `SharedVersion.cs` to bump the version. Never re-introduce `AssemblyVersion` to `Properties/AssemblyInfo.cs`. It would override the shared version on whichever assembly carries it and the drift guard breaks. GitHub Releases use git tag names (e.g., `v4.0.0`) as the user-facing version, but the binary's `AssemblyVersion` should match. The current shared version is `4.0.0.0`.

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
| **Microsoft.Windows.Devices.Midi2** | 1.0.16-rc.3.7 | **nuget-local/** | Windows MIDI Services SDK for virtual MIDI device creation |

`HIDMaestro.Core` (the virtual Xbox / PlayStation controller client) is a project `<Reference>` with a `HintPath` into `Resources/HIDMaestro/`, not a NuGet package. It is currently v1.3.17.

### PadForge.Engine

| Package | Version | Purpose |
|---|---|---|
| **BouncyCastle.Cryptography** | 2.6.2 | X25519 / Ed25519 / ChaCha20-Poly1305 for Remote Link pairing and transport, on the Win10 1809 floor where the in-box AEAD is gated to Win11 22000+ |
| **System.Security.Cryptography.ProtectedData** | 10.0.9 | DPAPI at-rest protection for Remote Link peer identity keys |

All SDL3 and system interop still uses raw `[DllImport]` P/Invoke.

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

### SDL3.dll and libusb-1.0.dll

```xml
<Content Include="Resources\SDL3\x64\SDL3.dll" Link="SDL3.dll"
         Condition="Exists('Resources\SDL3\x64\SDL3.dll')">
  <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
</Content>
<Content Include="Resources\SDL3\x64\libusb-1.0.dll" Link="libusb-1.0.dll"
         Condition="Exists('Resources\SDL3\x64\libusb-1.0.dll')">
  <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
</Content>
```

- **`Link="SDL3.dll"`**. Flattens to output root (next to `PadForge.exe`) instead of preserving the subdirectory path.
- **`Condition="Exists(...)"`**. Build succeeds even if the DLL is absent (e.g., fresh clone).
- **SDL3.dll** is a **custom fork** built from `SDL3-build/SDL/` with WinUSB support for Switch 2 Pro Controller. See [SDL3 Integration](sdl3-integration.md) for build instructions.
- **libusb-1.0.dll** provides WinUSB access for Switch 2 Pro Controller communication.

Source location: `PadForge.App/Resources/SDL3/x64/`

### xinput1_4.dll (OpenXInput shim)

```xml
<Content Include="Resources\OpenXInput\x64\xinput1_4.dll" Link="xinput1_4.dll"
         Condition="Exists('Resources\OpenXInput\x64\xinput1_4.dll')">
  <CopyToOutputDirectory>PreserveNewest</CopyToOutputDirectory>
</Content>
```

- **OpenXInput-derived.** Forked from `Nemirtingas/OpenXInput` with a HIDMaestro classifier added to the enumeration step so HM virtuals are skipped during slot assignment.
- **Replaces the system `xinput1_4.dll` via DLL search order.** The application directory is searched before `System32` for non-KnownDLLs, so when SDL3 calls `LoadLibrary("xinput1_4.dll")` this local copy resolves first and SDL's XInput backend uses it instead of Microsoft's.
- **`devobj.dll` is deliberately not shipped alongside it.** A stub `devobj.dll` would pre-empt `System32\devobj.dll` for the whole process and crash `setupapi.dll` during HID class enumeration. `xinput1_4.dll`'s `devobj.dll` import resolves from `System32` unaided. See [Driver Installation Internals](driver-installation-internals.md).

Source location: `PadForge.App/Resources/OpenXInput/x64/`

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
<EmbeddedResource Include="Resources\HidHide_1.5.230_x64.exe" />
```

| Resource | Purpose |
|----------|---------|
| `HidHide_1.5.230_x64.exe` | HidHide installer. Hides physical controllers from other applications |

The HIDMaestro user-mode driver is **not** managed by `DriverInstaller`. The driver binaries, INF, profiles, and signing tools all ship inside `HIDMaestro.Core.dll` (referenced as a `<Reference>`, so it's bundled into the single-file EXE). `InputManager` calls `HMContext.InstallDriver()` on first start (from `EnsureHMaestroContext()` in `PadForge.App/Common/Input/`), which registers the driver with Windows through `pnputil` from inside PadForge's already-elevated process. No separate installer EXE. The OpenXInput shim (`xinput1_4.dll` only) ships as `<Content>` and is bundled into the single-file EXE via `IncludeNativeLibrariesForSelfExtract`. `devobj.dll` is deliberately not shipped. See [Driver Installation Internals](driver-installation-internals.md) for why a bundled stub would crash HID class enumeration. The Windows MIDI Services SDK is downloaded from the GitHub releases API on demand when the user clicks Install, then run with `/install /quiet /norestart`.

PadForge v2's vJoy and ViGEmBus installers are no longer bundled. v4 detects either driver on first launch and offers to uninstall via the legacy driver cleanup dialog. See [Driver Installation Internals](driver-installation-internals.md).

### BthPS3 / DS3 Bluetooth Drivers (EmbeddedResource)

```xml
<EmbeddedResource Include="Resources\BthPS3\**\*.*">
  <LogicalName>BthPS3.%(RecursiveDir)%(Filename)%(Extension)</LogicalName>
</EmbeddedResource>
```

Microsoft-signed BthPS3 + BthPS3PSM drivers (nefarius release) and the DS3 WinUSB INF, embedded so the single-file app can install them at DualShock 3 pairing time with no MSI and no external installer. `Ds3DriverInstaller.ExtractDrivers()` walks every manifest resource whose name starts with `BthPS3.`, strips that prefix, and drops the files under `%TEMP%\PadForge\BthPS3Drivers\` before running `pnputil`. The explicit `LogicalName` preserves the subdirectory layout inside the manifest name.

| Directory | Contents |
|-----------|----------|
| `Resources/BthPS3/BthPS3_x64/` | `BthPS3.inf`/`.sys`/`.cat` (profile driver) + `BthPS3_PDO_NULL_Device.inf`/`.cat` (raw PDO extension) |
| `Resources/BthPS3/BthPS3PSM_x64/` | `BthPS3PSM.inf`/`.sys`/`.cat` (L2CAP PSM filter) |
| `Resources/BthPS3/WinUSB/` | `ds3_winusb.inf`/`.cat` (DS3-over-USB WinUSB binding) |

### 3D Model Assets (EmbeddedResource)

```xml
<!-- 3D controller model assets (adapted from Handheld Companion, CC BY-NC-SA 4.0) -->
<EmbeddedResource Include="3DModels\**\*.obj" />
```

OBJ mesh files for 3D controller visualization. Loaded at runtime via `ControllerModelBase.LoadModel()`.

| Directory | Contents |
|-----------|----------|
| `3DModels/XBOX360/` | 31 OBJ files (Xbox 360 controller parts) |
| `3DModels/XBOXONE/` | 46 OBJ files (Xbox One parts, shared with Elite / Series / Adaptive) |
| `3DModels/DS4/` | 36 OBJ files (DualShock 4 controller parts) |
| `3DModels/DualSense/` | 49 OBJ files (DualSense parts, Touchpad split for click-mapping) |

### Web Controller Assets (EmbeddedResource)

```xml
<!-- Web controller frontend assets (embedded, served by WebControllerServer) -->
<EmbeddedResource Include="WebAssets\**\*" />
```

HTML/CSS/JS for the browser-based virtual controller. Served by the embedded Kestrel web server at runtime.

| File | Purpose |
|------|---------|
| `WebAssets/index.html` | Landing page |
| `WebAssets/controller.html` | Virtual gamepad UI |
| `WebAssets/touchpad.html` | Touchpad surface UI |
| `WebAssets/css/controller.css` | Gamepad styling |
| `WebAssets/js/controller_client.js` | WebSocket client logic |
| `WebAssets/js/nipplejs.min.js` | Virtual joystick library |

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

The default `Strings.resx` uses `PublicResXFileCodeGenerator` to produce `Strings.Designer.cs` for strongly-typed access via `Strings.PropertyName`. Satellite `.resx` files follow standard .NET localization conventions and compile into satellite assemblies automatically.

### 2D Model Assets (Resource)

```xml
<!-- 2D controller model assets (Gamepad-Asset-Pack by AL2009man, MIT license) -->
<Resource Include="2DModels\**\*.png" />
```

PNG overlay images for 2D controller schematic view (`DS4/`, `DualSense/`, `XBOX360/`, `XBOXONE/`, `XBOXSERIES/`). Uses `Resource` (not `EmbeddedResource`) so they load as WPF pack URIs (`pack://application:,,,/2DModels/...`).

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

### Build Steps

1. **Checkout**. `actions/checkout@v5`, `fetch-depth: 0` (full history for commit counting)
2. **Setup .NET**. `actions/setup-dotnet@v5`, `dotnet-version: 10.x`
3. **Publish**. `dotnet publish PadForge.App/PadForge.App.csproj -c Release`
4. **Upload artifact**. `actions/upload-artifact@v7`, publish directory as `PadForge_r{COMMIT_COUNT}@{COMMIT_SHORT}`

### Automatic Releases (push to v4-dev only)

On push (not PR), the workflow creates two GitHub releases keyed off the branch ref name:

| Release | Behavior |
|---------|----------|
| **`archive-v4-dev`** | Accumulates every build as `PadForge_r{N}@{SHA}.zip`. Uses `--clobber` for the latest upload. Preserves the tag across builds. Rolls to a new part when full (see below). |
| **`latest-v4-dev`** | Recreated on every push (old release deleted first). Contains `PadForge.zip` with the most recent build. The "always current" download link. |

Both are marked `--prerelease` and cross-link to each other in their notes.

**Rolling archive parts.** GitHub caps a release at 1000 assets. The workflow watches the active archive and, once it reaches 999 assets, creates the next numbered part (`archive-v4-dev-2`, `archive-v4-dev-3`, and so on) targeting the current commit. Each new part's notes link back to the previous part, and `latest-v4-dev` points at whichever part is currently active.

### Artifact Naming

Format: `PadForge_r{COMMIT_COUNT}@{7-char COMMIT_SHA}` (e.g., `PadForge_r342@f35bb36`)

### Environment Variables

```yaml
env:
  DOTNET_NOLOGO: true
  DOTNET_CLI_TELEMETRY_OPTOUT: true
```

### Formal Releases

Created manually via `gh release create` with a version tag (e.g., `v4.0.0`, `v4.0.0-beta1`). See [Release Workflow](#release-workflow) below.

## Deployment

PadForge is portable. No installer required.

### Local Deployment

Copy the publish output to any folder:
```bash
cp PadForge.App/bin/Release/net10.0-windows10.0.26100.0/win-x64/publish/PadForge.exe C:\PadForge\PadForge.exe
```

Required companion files (placed automatically by `dotnet publish`):

| File | Required | Purpose |
|------|----------|---------|
| `SDL3.dll` | Yes | SDL3 native library |
| `libusb-1.0.dll` | Yes | WinUSB for Switch 2 Pro Controller |
| `xinput1_4.dll` | Yes | OpenXInput-derived XInput shim |

The gamepad mapping database is embedded in the assembly, so no `.txt` file sits alongside the exe. All three DLLs are folded into the single-file bundle on publish, so a single-file deploy is one `PadForge.exe`.

### Development Deploy Scripts

```bash
tools/deploy.ps1              # Build, publish, copy to C:\PadForge
tools/deploy_and_restart.ps1  # Deploy + kill running instance + restart
```

### First Run

PadForge creates `PadForge.xml` alongside the executable to store settings, mappings, and profiles.

PadForge always requests administrator privileges on startup (declared in `app.manifest` as `requireAdministrator`). HIDMaestro / HidHide / MIDI Services management runs inside the already-elevated process.

## Release Workflow

### 1. Update Version (if needed)

- Edit `SharedVersion.cs` at the repo root. Updates `AssemblyVersion` and `AssemblyFileVersion` for both App and Engine in one place.

### 2. Build

```bash
dotnet publish -c Release
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

### 5. Create Binary Zip

```bash
cd PadForge.App/bin/Release/net10.0-windows10.0.26100.0/win-x64/publish
zip -r PadForge-vX.Y.Z-win-x64.zip .
```

### 6. Create GitHub Release

```bash
gh release create vX.Y.Z --title "PadForge vX.Y.Z" --notes "Release notes here"
gh release upload vX.Y.Z PadForge-vX.Y.Z-win-x64.zip
```

Use `--prerelease` for beta/RC releases. Use `--latest` for the default download.

## Diagnostic Tools (`tools/`)

Standalone diagnostic utilities and development scripts.

| Tool | Command | Framework | Dependencies | Purpose |
|------|---------|-----------|--------------|---------|
| **DsuDiag** | `cd tools/DsuDiag && dotnet run` | net8.0 | None | Real-time DSU/Cemuhook UDP client for verifying gyro/accel axis mapping |
| **Ds4InputDump** | `cd tools/Ds4InputDump && dotnet run` | net10.0-windows | None (raw HID) | Dumps DS4 raw HID input frames. Used to validate Sony Report 0x01 passthrough on PlayStation virtual controllers |

The v2 `vJoy/Test` and `vJoy/FfbTest` utilities are still in the repo under `tools/vJoy/` for historical reference. They target the deprecated vJoy stack and are not part of the v4 toolchain.

### Development Scripts

| Script | Purpose |
|--------|---------|
| `deploy.ps1` | Build + publish + copy to `C:\PadForge` |
| `deploy_and_restart.ps1` | Deploy + kill running instance + restart |
| `capture_*.ps1` | ~20 per-surface wiki screenshot scripts (e.g. `capture_all.ps1`, `capture_pads*.ps1`, `capture_macros.ps1`, `capture_3d_2d.ps1`, `capture_3d_web.ps1`, `capture_extra_slots.ps1`). One per major UI surface. `capture_all_wrapper.ps1` runs them in sequence. |

A handful of `*vjoy*` scripts (`cleanup_vjoy.ps1`, `check_vjoy_state.ps1`, etc.) are v2 holdovers kept for diagnosing legacy installs the cleanup dialog encounters. The remaining ~50 scripts are ad-hoc UI automation and screenshot utilities.

## Troubleshooting Build Issues

| Issue | Cause | Fix |
|-------|-------|-----|
| `SDL3.dll` not found at runtime | DLL not in `Resources\SDL3\x64\` | Download from SDL3 releases or build from fork |
| MIDI package not found | `nuget.config` missing or `nuget-local/` folder missing | Ensure both are present at solution root |
| Missing WPF types | Using `dotnet build` instead of `dotnet publish` for deployment | Always use `dotnet publish -c Release` for deployment |
| `System.Drawing` ambiguity | WinForms implicit usings conflict with WPF | Ensure `<Using Remove="System.Drawing" />` is in csproj |
| HelixToolkit errors | Package restore failed | Run `dotnet restore` first |
| Large exe size (~110 MB) | Expected. Self-contained with bundled .NET runtime | `EnableCompressionInSingleFile` already enabled |
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

Last updated for PadForge 4.0.0
