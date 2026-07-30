# 3D Model System

Renders interactive Xbox and PlayStation controller models from Wavefront OBJ meshes using [HelixToolkit.WPF](https://github.com/helix-toolkit/helix-toolkit). Adapted from [Handheld Companion](https://github.com/Valkirie/HandheldCompanion) (CC BY-NC-SA 4.0).

**Namespace:** `PadForge.Models3D` (model classes), `PadForge.Views` (view)

---

## Architecture Overview

```
ControllerModelBase (abstract)
    |
    +-- ControllerModelXbox360   (Xbox 360 meshes, colors, rotation points)
    +-- ControllerModelXboxOne   (Xbox One / Elite / Adaptive / Series mesh share)
    +-- ControllerModelDS4       (DualShock 4 meshes, colors, rotation points)
    +-- ControllerModelDualSense (DualSense / DualSense Edge meshes)

ControllerModelView (UserControl)
    |
    +-- HelixViewport3D          (3D rendering viewport)
    +-- ModelVisual3D            (hosts the model3DGroup scene graph)
    +-- CompositionTarget.Rendering  (per-frame visual updates)
```

Model classes own geometry and materials. The view class owns the viewport, input handling, and animation. `ControllerModelView.EnsureModel()` instantiates the correct model class and assigns it to `ModelVisual3D.Content`.

---

## ControllerModelBase

**File:** `PadForge.App/Models3D/ControllerModelBase.cs`

Abstract base class. Each subclass defines its own meshes, colors, and rotation points.

```csharp
public abstract class ControllerModelBase : IDisposable
```

### Data Dictionaries

| Field | Type | Description |
|-------|------|-------------|
| `ButtonMap` | `Dictionary<string, List<Model3DGroup>>` | PadSetting name to Model3DGroups for highlighting (supports multi-mesh buttons like button + overlay). |
| `ClickMap` | `Dictionary<Model3DGroup, string>` | Model3DGroup to PadSetting name for hit-test click-to-record. Reverse of ButtonMap. |
| `DefaultMaterials` | `Dictionary<Model3DGroup, Material>` | Original material per group. Restored after highlight/flash. |
| `HighlightMaterials` | `Dictionary<Model3DGroup, Material>` | Accent-colored material per group. Applied on press or flash. |

### Scene Graph

| Field | Type | Description |
|-------|------|-------------|
| `model3DGroup` | `Model3DGroup` | Root scene group containing all child meshes. Assigned to `ModelVisual3D.Content`. |
| `ModelName` | `string` | One of `"XBOX360"`, `"XBOXONE"`, `"DS4"`, `"DualSense"`. Used for embedded resource path resolution. |

### Common Geometry Groups

| Field | Loaded From | Description |
|-------|-------------|-------------|
| `MainBody` | `MainBody.obj` | Main controller body mesh |
| `LeftThumb` | `LeftStickClick.obj` | Left stick click mesh |
| `LeftThumbRing` | `Joystick-Left-Ring.obj` | Left stick ring mesh (torus) |
| `RightThumb` | `RightStickClick.obj` | Right stick click mesh |
| `RightThumbRing` | `Joystick-Right-Ring.obj` | Right stick ring mesh (torus) |
| `LeftShoulderTrigger` | `Shoulder-Left-Trigger.obj` | Left shoulder trigger mesh |
| `RightShoulderTrigger` | `Shoulder-Right-Trigger.obj` | Right shoulder trigger mesh |
| `LeftMotor` | `MotorLeft.obj` | Left rumble motor mesh |
| `RightMotor` | `MotorRight.obj` | Right rumble motor mesh |

### Rotation Parameters

| Field | Type | Description |
|-------|------|-------------|
| `JoystickRotationPointCenterLeftMillimeter` | `Vector3D` | Left stick tilt pivot |
| `JoystickRotationPointCenterRightMillimeter` | `Vector3D` | Right stick tilt pivot |
| `JoystickMaxAngleDeg` | `float` | Max stick tilt angle (degrees) |
| `ShoulderTriggerRotationPointCenterLeftMillimeter` | `Vector3D` | Left trigger rotation pivot |
| `ShoulderTriggerRotationPointCenterRightMillimeter` | `Vector3D` | Right trigger rotation pivot |
| `TriggerMaxAngleDeg` | `float` | Max trigger depression angle (degrees) |
| `UpwardVisibilityRotationAxisLeft/Right` | `Vector3D` | Shoulder visibility correction axis |
| `UpwardVisibilityRotationPointLeft/Right` | `Vector3D` | Shoulder visibility correction origin |

### ButtonFileMap

Maps Handheld Companion `.obj` filenames (using `ButtonFlags` enum names) to PadSetting property names (used by the recording system).

```csharp
protected static readonly Dictionary<string, string> ButtonFileMap = new()
{
    { "B1.obj", "ButtonA" },
    { "B2.obj", "ButtonB" },
    { "B3.obj", "ButtonX" },
    { "B4.obj", "ButtonY" },
    { "L1.obj", "LeftShoulder" },
    { "R1.obj", "RightShoulder" },
    { "Back.obj", "ButtonBack" },
    { "Start.obj", "ButtonStart" },
    { "Special.obj", "ButtonGuide" },
    { "DPadUp.obj", "DPadUp" },
    { "DPadDown.obj", "DPadDown" },
    { "DPadLeft.obj", "DPadLeft" },
    { "DPadRight.obj", "DPadRight" },
    { "LeftStickClick.obj", "LeftThumbButton" },
    { "RightStickClick.obj", "RightThumbButton" },
};
```

### Constructor Flow (Model Loading)

```csharp
protected ControllerModelBase(string modelName)
```

Steps are order-dependent:

1. **Set ModelName**. Determines the embedded-resource folder. One of `"XBOX360"`, `"XBOXONE"`, `"DS4"`, or `"DualSense"`. Picked by `HMaestroProfileCatalog.ResolveAssetFolders` against the slot's `ProfileId` and `OutputType`.
2. **Load common geometry** via `LoadModel()`: MainBody, stick rings, motors, triggers.
3. **Register trigger ClickMap entries**: `LeftShoulderTrigger` -> `"LeftTrigger"`, `RightShoulderTrigger` -> `"RightTrigger"`. Triggers use ClickMap (not ButtonMap) because they are continuous axes, not toggle buttons.
4. **Iterate ButtonFileMap**: Calls `TryLoadModel()` per entry, then `RegisterButton()` to populate both `ButtonMap` and `ClickMap`. Special cases: `LeftStickClick.obj` and `RightStickClick.obj` also set `LeftThumb`/`RightThumb` references for tilt animation.
5. **Add all parts to `model3DGroup.Children`**. Assigned to `ModelVisual3D.Content`.
6. **Subclass constructor continues**. Loads extra meshes (face button overlays, symbol meshes), assigns colored materials, calls `DrawAccentHighlights()` last.

**Note:** Stick rings are NOT in ClickMap. The view handles ring clicks via `IsStickRingHit()` with quadrant-based axis detection, since ring clicks must determine axis direction from click position.

### RegisterButton

```csharp
protected void RegisterButton(string padSettingName, Model3DGroup group)
```

Adds `group` to `ButtonMap[padSettingName]` (creates list if needed) and sets `ClickMap[group] = padSettingName`. This bidirectional mapping enables highlighting (name -> groups) and click detection (group -> name).

### DrawAccentHighlights

```csharp
protected virtual void DrawAccentHighlights()
```

Creates accent-colored `DiffuseMaterial` for all children. Reads the `SystemAccentColorPrimary` resource (a WPF-UI theme `Color`) and wraps it in a `SolidColorBrush`. Falls back to `#FF6B2C` ember orange. The brush stays solid because `GradientHighlight()` lerps its `Color`. `AccentButtonBackground` became an ember gradient in #175, so the highlight now derives from the accent `Color` instead. Called at the end of each subclass constructor.

### Embedded Resource Loading

```csharp
protected Model3DGroup LoadModel(string filename)     // Throws FileNotFoundException
protected Model3DGroup TryLoadModel(string filename)  // Returns null on failure
```

Loads `.obj` meshes from embedded resources via HelixToolkit's `ObjReader`. Searches manifest resource names by **suffix** (`.{ModelName}.{filename}`) to handle MSBuild digit-prefix mangling.

**MSBuild mangling:** `3DModels` becomes `_3DModels` in resource names because MSBuild prefixes digit-leading folder names. Suffix matching avoids hard-coding the prefix.

```csharp
string suffix = $".{ModelName}.{filename}";
foreach (var name in assembly.GetManifestResourceNames())
    if (name.EndsWith(suffix, StringComparison.OrdinalIgnoreCase))
        // Found it
```

### Dispose Pattern

```csharp
public void Dispose()
protected virtual void Dispose(bool disposing)
~ControllerModelBase()
```

Clears all dictionaries and `model3DGroup.Children`. Standard dispose pattern with finalizer. Called by `EnsureModel()` when switching model types.

---

## ControllerModelXbox360

**File:** `PadForge.App/Models3D/ControllerModelXbox360.cs`

```csharp
public class ControllerModelXbox360 : ControllerModelBase
```

Calls `base("XBOX360")`.

### Xbox 360-Specific Mesh Groups

| Field | Loaded From | Description |
|-------|-------------|-------------|
| `MainBodyCharger` | `MainBody-Charger.obj` | Battery pack/charger compartment |
| `SpecialRing` | `SpecialRing.obj` | Guide button ring |
| `SpecialLED` | `SpecialLED.obj` | Guide button LED indicator |
| `LeftShoulderBottom` | `LeftShoulderBottom.obj` | Left bumper bottom piece |
| `RightShoulderBottom` | `RightShoulderBottom.obj` | Right bumper bottom piece |
| `B1Button` | `B1Button.obj` | A button colored overlay |
| `B2Button` | `B2Button.obj` | B button colored overlay |
| `B3Button` | `B3Button.obj` | X button colored overlay |
| `B4Button` | `B4Button.obj` | Y button colored overlay |

### Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| `ColorPlasticBlack` | `#707477` | Default for most parts |
| `ColorPlasticWhite` | `#D4D4D4` | Main body, motors, shoulder bottoms |
| `ColorPlasticSilver` | `#CEDAE1` | Guide button |
| `ColorPlasticGreen` | `#7cb63b` | A button |
| `ColorPlasticRed` | `#ff5f4b` | B button |
| `ColorPlasticBlue` | `#6ac4f6` | X button |
| `ColorPlasticYellow` | `#faa51f` | Y button |

Face button overlays (`B1Button`–`B4Button`) use transparent variants (`Alpha = 150`) so the base button color shows through.

### Rotation Points

| Parameter | Value |
|-----------|-------|
| `JoystickRotationPointCenterLeftMillimeter` | `(-42.231, -6.10, 21.436)` |
| `JoystickRotationPointCenterRightMillimeter` | `(21.013, -6.1, -3.559)` |
| `JoystickMaxAngleDeg` | `19.0` |
| `ShoulderTriggerRotationPointCenterLeftMillimeter` | `(-44.668, 3.087, 39.705)` |
| `ShoulderTriggerRotationPointCenterRightMillimeter` | `(44.668, 3.087, 39.705)` |
| `TriggerMaxAngleDeg` | `16.0` |

### Material Assignment Order

1. Face button overlays (`B1Button`–`B4Button`) get transparent color materials and register into `ButtonMap` alongside base meshes for joint highlighting.
2. `SpecialLED` gets green transparent material.
3. Base face buttons (`B1.obj`–`B4.obj`) get opaque color materials.
4. Guide button gets silver material.
5. White parts: `MainBody`, `LeftMotor`, `RightMotor`, `LeftShoulderBottom`, `RightShoulderBottom`.
6. Remaining parts default to black.
7. `DrawAccentHighlights()` called last.

---

## ControllerModelDS4

**File:** `PadForge.App/Models3D/ControllerModelDS4.cs`

```csharp
public class ControllerModelDS4 : ControllerModelBase
```

Calls `base("DS4")`.

### DS4-Specific Mesh Groups

| Field | Loaded From | Description |
|-------|-------------|-------------|
| `LeftShoulderMiddle` | `Shoulder-Left-Middle.obj` | Left shoulder middle piece |
| `RightShoulderMiddle` | `Shoulder-Right-Middle.obj` | Right shoulder middle piece |
| `Screen` | `Screen.obj` | Touchpad/screen area |
| `MainBodyBack` | `MainBodyBack.obj` | Back panel |
| `AuxPort` | `Aux-Port.obj` | Auxiliary port |
| `Triangle` | `Triangle.obj` | Decorative triangle element |
| `DPadDownArrow` | `DPadDownArrow.obj` | D-pad down arrow indicator |
| `DPadUpArrow` | `DPadUpArrow.obj` | D-pad up arrow indicator |
| `DPadLeftArrow` | `DPadLeftArrow.obj` | D-pad left arrow indicator |
| `DPadRightArrow` | `DPadRightArrow.obj` | D-pad right arrow indicator |

### PlayStation Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| `ColorPlasticBlack` | `#38383A` | Default body color |
| `ColorPlasticWhite` | `#E0E0E0` | Main body, motors, triangle |
| `MaterialPlasticTriangle` | `#66a0a4` | Triangle face button symbol |
| `MaterialPlasticCross` | `#96b2d9` | Cross (X) face button symbol |
| `MaterialPlasticCircle` | `#d66673` | Circle face button symbol |
| `MaterialPlasticSquare` | `#d7bee5` | Square face button symbol |

### Face Button Symbols

DS4 loads separate symbol meshes (`B1-Symbol.obj` through `B4-Symbol.obj`) via `TryLoadModel()`. Each symbol shares its `ButtonMap` entry with the base button mesh for joint highlighting. Symbol meshes get PlayStation-specific colors. Base meshes default to black.

### Touchpad Mapping

The DS4 exposes `Screen.obj` (the touchpad surface) as `Touchpad` and registers `ClickMap[Screen] = "TouchpadClick"`, so the surface is a click-to-record hit target. `Touchpad` is the base-class property the view reads for the touchpad click highlight and finger-sphere preview. DS4 does not override the touchpad inset fractions, so the view uses the defaults (`TouchpadXInsetFrac = 0.03`, `TouchpadZTopInsetFrac = 0.12`, `TouchpadZBottomInsetFrac = 0.12`).

### Rotation Points

| Parameter | Value |
|-----------|-------|
| `JoystickRotationPointCenterLeftMillimeter` | `(-25.5, -5.086, -21.582)` |
| `JoystickRotationPointCenterRightMillimeter` | `(25.5, -5.086, -21.582)` |
| `JoystickMaxAngleDeg` | `19.0` |
| `ShoulderTriggerRotationPointCenterLeftMillimeter` | `(-38.061, 3.09, 26.842)` |
| `ShoulderTriggerRotationPointCenterRightMillimeter` | `(38.061, 3.09, 26.842)` |
| `TriggerMaxAngleDeg` | `16.0` |

---

## ControllerModelXboxOne

**File:** `PadForge.App/Models3D/ControllerModelXboxOne.cs`

```csharp
public class ControllerModelXboxOne : ControllerModelBase
public ControllerModelXboxOne(bool enableShare)
```

Calls `base("XBOXONE")`. Used by Xbox One, Xbox Elite, Xbox Series, and Xbox Adaptive profiles. Handheld Companion has no Xbox Series mesh, so Series profiles borrow this one.

### Xbox One-Specific Mesh Groups

| Field | Loaded From | Description |
|-------|-------------|-------------|
| `MainBodyBack` | `MainBodyBack.obj` | Back shell |
| `MainBodyTop` | `MainBodyTop.obj` | Top shell |
| `MainBodySide` | `MainBodySide.obj` | Side grips |
| `BackSymbol` | `BackSymbol.obj` | View-button glyph |
| `StartSymbol` | `StartSymbol.obj` | Menu-button glyph |
| `BatteryDoor` | `BatteryDoor.obj` | AA-pack door |
| `BatteryDoorInner` | `BatteryDoorInner.obj` | Door interior |
| `SpecialOuter` | `SpecialOuter.obj` | Guide button outer ring |
| `ShareButton` | `ShareButton.obj` | Share button (Series only) |
| `ShareButtonSymbol` | `ShareButtonSymbol.obj` | Share-button glyph |
| `USBPortInner` / `USBPortOuter` | `USBPortInner.obj`, `USBPortOuter.obj` | USB-C port |
| `B1Button`–`B4Button` | `B1-Button.obj`–`B4-Button.obj` | Translucent face-button caps |
| `B1Interior`–`B4Interior` | `B1-Interior.obj`–`B4-Interior.obj` | Face-button interior shells (painted black) |
| `B1Interior2`–`B4Interior2` | `B1-Interior2.obj`–`B4-Interior2.obj` | Inner face-button cores (painted black) |

### Share Button Wiring

The constructor takes a `bool enableShare` argument. `true` is passed only when `ProfileId` starts with `xbox-series-`. Xbox One, Elite, and Adaptive profiles get `false`. When false, the Share mesh stays inert: visible body geometry, no hover, no click, no accent highlight. HM silently drops the Share bit on non-Series profiles, so the mapping UI does not surface it either.

### Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| `ColorPlasticBlack` | `#26272C` | Shoulders, triggers, stick clicks, dpad, guide, USB outer, button-interior shells, symbols |
| `ColorPlasticWhite` | `#D8D7DC` | Main shell, share button face, view/menu faces, default fallback |
| `ColorPlasticGreen` | `#76BA58` | A button (base `B1.obj`) |
| `ColorPlasticRed` | `#FA3D45` | B button (base `B2.obj`) |
| `ColorPlasticBlue` | `#119AE5` | X button (base `B3.obj`) |
| `ColorPlasticYellow` | `#E4D70E` | Y button (base `B4.obj`) |
| `ColorPlasticTransparent` | `#232323` α=50 | Translucent face-button caps over the colored interior |

### Rotation Points

| Parameter | Value |
|-----------|-------|
| `JoystickRotationPointCenterLeftMillimeter` | `(-39.0, -8.0, 22.2)` |
| `JoystickRotationPointCenterRightMillimeter` | `(20.0, -8.0, -1.1)` |
| `JoystickMaxAngleDeg` | `17.0` |
| `ShoulderTriggerRotationPointCenterLeftMillimeter` | `(-44.668, 3.087, 39.705)` |
| `ShoulderTriggerRotationPointCenterRightMillimeter` | `(44.668, 3.087, 39.705)` |
| `TriggerMaxAngleDeg` | `16.0` |

### Material Assignment Order

1. Load Xbox One-specific meshes. Register `ButtonShare` (the `ShareButton` body mesh) if `enableShare`.
2. Paint the base face buttons green / red / blue / yellow via `ButtonMap["ButtonA".."ButtonY"]`. These map to `B1.obj`–`B4.obj`, not the `Interior` meshes.
3. Paint View and Menu faces white.
4. Paint shoulders, triggers, stick clicks, guide, and dpad black.
5. Generic pass: USB outer, `B1Interior`–`B4Interior`, the `Interior2` cores, stick rings, shoulder triggers, and glyph meshes (`ShareButtonSymbol`, `StartSymbol`, `BackSymbol`) go black.
6. Face-button caps get the translucent material.
7. Everything else defaults to white plastic.
8. `DrawAccentHighlights()` called last.

---

## ControllerModelDualSense

**File:** `PadForge.App/Models3D/ControllerModelDualSense.cs`

```csharp
public class ControllerModelDualSense : ControllerModelBase
```

Calls `base("DualSense")`. Used by DualSense and DualSense Edge profiles.

### DualSense-Specific Mesh Groups

| Field | Loaded From | Description |
|-------|-------------|-------------|
| `MainBodyBack` | `MainBodyBack.obj` | Back grip shell |
| `MainBodyFront` | `MainBodyFront.obj` | Front face plate |
| `Touchpad` | `Touchpad.obj` | Central touch surface (split out of upstream `MainBody.obj` so it is its own click-mappable and highlight-able mesh) |
| `AudioJack` | `AudioJack.obj` | 3.5 mm jack |
| `USBPort` | `USBPort.obj` | USB-C port |
| `Charger` | `Charger.obj` | Charging contacts |
| `LED1`, `LED2`, `LED3` | `LED1.obj`–`LED3.obj` | Player-indicator LEDs |
| `ShareSymbol` | `ShareSymbol.obj` | Create-button glyph |
| `MenuSymbol` | `MenuSymbol.obj` | Options-button glyph |
| `B1Button`–`B4Button` | `B1Button.obj`–`B4Button.obj` | Translucent face-button caps |
| `B1ButtonSymbol`–`B4ButtonSymbol` | `B1ButtonSymbol.obj`–`B4ButtonSymbol.obj` | Cross / Circle / Square / Triangle glyphs |
| `DPadUpArrow`, `DPadDownArrow`, `DPadLeftArrow`, `DPadRightArrow` | `DPad*Arrow.obj` | Arrow glyphs on the dpad |
| `DPadUpCover`, `DPadDownCover`, `DPadLeftCover`, `DPadRightCover` | `DPad*Cover.obj` | Translucent dpad covers |

### Touchpad Split

`MainBody.obj` from Handheld Companion is one file with multiple connected components: grip handles, the central front-face area, dpad pieces, and face-button pieces are joined together. `tools/overlay_positions.py` runs a one-time split that writes `MainBody.obj` minus the central front-face component and a separate `Touchpad.obj` with just the touch surface. The DualSense constructor loads both so `MainBody` renders the grip and button areas while `Touchpad` is independently clickable and highlight-able. `ClickMap[Touchpad] = "TouchpadClick"`.

### PlayStation Color Palette

| Name | Hex | Usage |
|------|-----|-------|
| `ColorPlasticBlack` | `#21242E` | Front face plate, audio jack, USB port, stick rings, shoulder triggers |
| `ColorPlasticGrey` | `#7C7F8C` | Share / Menu glyphs, dpad arrows, face-button glyphs |
| `ColorPlasticWhite` | `#DADFE8` | Back shell, default fallback |
| `ColorPlasticTransparent` | `#DADFE8` α=100 | Dpad covers, face-button caps |
| `ColorMetal` | `#5A4928` | Charging contacts |
| `ColorLEDOff` | `#35383E` | Unlit player-indicator LED |
| `AccentButtonBackground` (theme) | accent | Lit player-indicator LEDs (LED1, LED2) |

### Rotation Points

| Parameter | Value |
|-----------|-------|
| `JoystickRotationPointCenterLeftMillimeter` | `(-30.339, -10.7, -1.507)` |
| `JoystickRotationPointCenterRightMillimeter` | `(30.339, -10.7, -1.507)` |
| `JoystickMaxAngleDeg` | `14.0` |
| `ShoulderTriggerRotationPointCenterLeftMillimeter` | `(-65.4, -0.64, 45.8)` |
| `ShoulderTriggerRotationPointCenterRightMillimeter` | `(65.4, -0.64, 45.8)` |
| `TriggerMaxAngleDeg` | `16.0` |

### Uniform Model Scale

Handheld Companion modeled the DualSense larger than the DS4 in raw mesh units (MainBody width 199.9 mm vs 165.7 mm, ~21 % bigger) even though the real-world controllers are nearly the same size. The shared viewport camera is sized for DS4-class meshes, so this class overrides `ModelScale = 165.7 / 199.9`. The view applies the scale at the `ModelVisual3D` level, which scales the controller mesh AND the sibling finger-sphere visuals together so stick highlights and touchpad finger dots stay glued to the correct surface.

### Touchpad Inset Region

The split-out `Touchpad` mesh extends beyond the actual touch-sensitive surface: bounds are roughly X ∈ [−42, 38] (80 mm) and Z ∈ [19, 63] (44 mm) versus the real touch area of ~52 × 32 mm. The class overrides `TouchpadXInsetFrac = 0.175`, `TouchpadZTopInsetFrac = 0.10`, `TouchpadZBottomInsetFrac = 0.02` so the rendered finger dot lands where a real finger would land instead of sliding past the visual edges.

### Material Assignment Order

1. Load DualSense-specific meshes. Insert `Touchpad` into `ClickMap` as `TouchpadClick`.
2. Per `ButtonMap` target: black for shoulders, triggers, stick clicks, and guide. White for everything else.
3. Generic pass: front shell, audio jack, USB, stick rings, and shoulder triggers go black.
4. Share / Menu glyphs, dpad arrows, and face-button glyphs go grey.
5. LED1 and LED2 take the accent material.
6. Charger gets the metal material.
7. LED3 takes the unlit-LED material.
8. Dpad covers and face-button caps get the translucent material.
9. Everything else defaults to white plastic.
10. `DrawAccentHighlights()` called last.

---

## OBJ Mesh Files

### Directory Structure

```
PadForge.App/3DModels/
  XBOX360/         (31 meshes)
    MainBody.obj                             (body)
    MainBody-Charger.obj                     (battery pack)
    Joystick-Left-Ring.obj                   (left stick torus ring)
    Joystick-Right-Ring.obj                  (right stick torus ring)
    MotorLeft.obj, MotorRight.obj            (rumble motors)
    Shoulder-Left-Trigger.obj                (left trigger)
    Shoulder-Right-Trigger.obj               (right trigger)
    SpecialRing.obj, SpecialLED.obj          (guide button ring + LED)
    LeftShoulderBottom.obj                   (left bumper bottom)
    RightShoulderBottom.obj                  (right bumper bottom)
    B1.obj, B2.obj, B3.obj, B4.obj           (base face buttons: A, B, X, Y)
    B1Button.obj, B2Button.obj,              (colored face-button overlays)
      B3Button.obj, B4Button.obj
    L1.obj, R1.obj                           (shoulder bumpers)
    Back.obj, Start.obj, Special.obj         (center buttons)
    DPadUp.obj, DPadDown.obj,                (D-pad directions)
      DPadLeft.obj, DPadRight.obj
    LeftStickClick.obj, RightStickClick.obj  (stick click caps)
  XBOXONE/         (46 meshes)
    MainBody.obj                             (body)
    MainBodyBack.obj, MainBodyTop.obj,       (shell panels)
      MainBodySide.obj
    Joystick-Left-Ring.obj                   (left stick torus ring)
    Joystick-Right-Ring.obj                  (right stick torus ring)
    MotorLeft.obj, MotorRight.obj            (rumble motors)
    Shoulder-Left-Trigger.obj                (left trigger)
    Shoulder-Right-Trigger.obj               (right trigger)
    BatteryDoor.obj, BatteryDoorInner.obj    (AA-pack door)
    SpecialOuter.obj                         (guide button outer ring)
    ShareButton.obj, ShareButtonSymbol.obj   (Series Share button + glyph)
    StartSymbol.obj, BackSymbol.obj          (Menu + View glyphs)
    USBPortInner.obj, USBPortOuter.obj       (USB-C port)
    B1.obj, B2.obj, B3.obj, B4.obj           (base face buttons: A, B, X, Y)
    B1-Button.obj, B2-Button.obj,            (translucent face-button caps)
      B3-Button.obj, B4-Button.obj
    B1-Interior.obj, B2-Interior.obj,        (colored face-button interiors)
      B3-Interior.obj, B4-Interior.obj
    B1-Interior2.obj, B2-Interior2.obj,      (inner cores)
      B3-Interior2.obj, B4-Interior2.obj
    L1.obj, R1.obj                           (shoulder bumpers)
    Back.obj, Start.obj, Special.obj         (View, Menu, Guide buttons)
    DPadUp.obj, DPadDown.obj,                (D-pad directions)
      DPadLeft.obj, DPadRight.obj
    LeftStickClick.obj, RightStickClick.obj  (stick click caps)
  DS4/             (36 meshes)
    MainBody.obj                             (body)
    MainBodyBack.obj                         (back panel)
    Joystick-Left-Ring.obj                   (left stick torus ring)
    Joystick-Right-Ring.obj                  (right stick torus ring)
    MotorLeft.obj, MotorRight.obj            (rumble motors)
    Shoulder-Left-Trigger.obj                (left trigger L2)
    Shoulder-Right-Trigger.obj               (right trigger R2)
    Shoulder-Left-Middle.obj                 (left shoulder middle)
    Shoulder-Right-Middle.obj                (right shoulder middle)
    Screen.obj                               (touchpad area)
    Aux-Port.obj                             (auxiliary port)
    Triangle.obj                             (decorative triangle)
    DPadDownArrow.obj, DPadUpArrow.obj,      (D-pad arrow indicators)
      DPadLeftArrow.obj, DPadRightArrow.obj
    B1.obj, B2.obj, B3.obj, B4.obj           (base face buttons: Cross, Circle, Square, Triangle)
    B1-Symbol.obj, B2-Symbol.obj,            (PlayStation symbol overlays)
      B3-Symbol.obj, B4-Symbol.obj
    L1.obj, R1.obj                           (shoulder bumpers)
    Back.obj, Start.obj, Special.obj         (Share, Options, PS buttons)
    DPadUp.obj, DPadDown.obj,                (D-pad directions)
      DPadLeft.obj, DPadRight.obj
    LeftStickClick.obj, RightStickClick.obj  (stick click caps)
  DualSense/       (49 meshes)
    MainBody.obj                             (body, minus the touchpad area)
    MainBodyBack.obj, MainBodyFront.obj      (back shell, front face plate)
    Touchpad.obj                             (split-out central touch surface)
    Joystick-Left-Ring.obj                   (left stick torus ring)
    Joystick-Right-Ring.obj                  (right stick torus ring)
    MotorLeft.obj, MotorRight.obj            (rumble motors)
    Shoulder-Left-Trigger.obj                (L2 adaptive trigger)
    Shoulder-Right-Trigger.obj               (R2 adaptive trigger)
    AudioJack.obj                            (3.5 mm jack)
    USBPort.obj                              (USB-C port)
    Charger.obj                              (charging contacts)
    LED1.obj, LED2.obj, LED3.obj             (player-indicator LEDs)
    ShareSymbol.obj, MenuSymbol.obj          (Create + Options glyphs)
    B1.obj, B2.obj, B3.obj, B4.obj           (base face buttons: Cross, Circle, Square, Triangle)
    B1Button.obj, B2Button.obj,              (translucent face-button caps)
      B3Button.obj, B4Button.obj
    B1ButtonSymbol.obj, B2ButtonSymbol.obj,  (glyph overlays)
      B3ButtonSymbol.obj, B4ButtonSymbol.obj
    L1.obj, R1.obj                           (shoulder bumpers)
    Back.obj, Start.obj, Special.obj         (Create, Options, PS buttons)
    DPadUp.obj, DPadDown.obj,                (D-pad directions)
      DPadLeft.obj, DPadRight.obj
    DPadUpArrow.obj, DPadDownArrow.obj,      (D-pad arrow glyphs)
      DPadLeftArrow.obj, DPadRightArrow.obj
    DPadUpCover.obj, DPadDownCover.obj,      (translucent dpad covers)
      DPadLeftCover.obj, DPadRightCover.obj
    LeftStickClick.obj, RightStickClick.obj  (stick click caps)
```

All OBJ files are embedded as `EmbeddedResource` in the project file:

```xml
<EmbeddedResource Include="3DModels\**\*.obj" />
```

---

## ControllerModelView

**File:** `PadForge.App/Views/ControllerModelView.xaml`, `ControllerModelView.xaml.cs`

WPF `UserControl` hosting a `HelixViewport3D` for 3D controller visualization. The code-behind spans two partial files: `ControllerModelView.xaml.cs` (~1680 lines: rendering, input, hit testing, flash) and `ControllerModelView.Annotations.cs` (1037 lines: the annotation overlay, see below).

### XAML Structure

```xml
<Grid>
    <helix:HelixViewport3D x:Name="ModelViewPort"
        IsRotationEnabled="False" IsPanEnabled="False"
        IsMoveEnabled="False" IsZoomEnabled="False"
        ShowViewCube="False" ZoomExtentsWhenLoaded="False"
        Background="Transparent" IsManipulationEnabled="False">

        <helix:SunLight />
        <helix:DirectionalHeadLight Brightness="0.35" />

        <!-- Ember rim light (#175) -->
        <ModelVisual3D>
            <ModelVisual3D.Content>
                <DirectionalLight Color="#5A321C" Direction="0,-0.7,0.7" />
            </ModelVisual3D.Content>
        </ModelVisual3D>

        <ModelVisual3D x:Name="ModelVisual3D" />

        <helix:HelixViewport3D.Camera>
            <PerspectiveCamera FieldOfView="55"
                LookDirection="0,0.793,-0.609"
                Position="0,-172,132" UpDirection="0,0,1" />
        </helix:HelixViewport3D.Camera>
    </helix:HelixViewport3D>

    <!-- Annotation overlay (#175): chips, leader lines, trigger bars.
         No Background so empty space stays click-through to the viewport. -->
    <Canvas x:Name="AnnotationCanvas" Visibility="Collapsed" ClipToBounds="True" />

    <!-- Top-right controls: annotation toggle (Tag glyph E8EC) + Reset View -->
    <StackPanel Orientation="Horizontal" HorizontalAlignment="Right"
                VerticalAlignment="Top" Margin="0,8,8,0">
        <ui:Button x:Name="AnnotationToggleButton"
                   Style="{StaticResource EmberIconButton}"
                   Click="AnnotationToggle_Click">
            <TextBlock FontFamily="Segoe MDL2 Assets" Text="&#xE8EC;" />
        </ui:Button>
        <Button x:Name="ResetViewButton" Content="Reset View"
                Click="ResetView_Click" />
    </StackPanel>
</Grid>
```

The camera is wrapped in `<helix:HelixViewport3D.Camera>` rather than being a bare child. The viewport is named `ModelViewPort` (the code-behind reads it for hit testing and projection). The rim light is a third light source (see [Lighting](#lighting)). All built-in HelixToolkit camera controls are disabled. Rotation, zoom, and pan are handled by custom event handlers to avoid conflicts with PadForge's click-to-map and touch gesture handling.

### Events

```csharp
public event EventHandler<string> ControllerElementRecordRequested;
public event EventHandler<bool> AnnotationsToggled;
public event EventHandler<string> AnnotationChipNavigateRequested;
public bool AnnotationsEnabled { get; set; }
```

| Member | Fires when | Payload |
|--------|-----------|---------|
| `ControllerElementRecordRequested` | User clicks a mappable 3D element | PadSetting target name (`"ButtonA"`, `"LeftThumbAxisXNeg"`) |
| `AnnotationsToggled` | User clicks the annotation toggle button | New on/off state (`bool`) |
| `AnnotationChipNavigateRequested` | User clicks an annotation chip | The chip row's `TargetSettingName` |
| `AnnotationsEnabled` | (property, not event) | Session-only overlay on/off. The hosting page pushes the ViewModel state in on bind and writes it back on `AnnotationsToggled`. The setter raises nothing, so the write-back can't loop. |

The last three drive the annotation overlay (see [Annotation Overlay](#annotation-overlay)).

### Private State

| Field | Type | Description |
|-------|------|-------------|
| `_vm` | `PadViewModel` | Bound ViewModel |
| `_currentModel` | `ControllerModelBase` | Active 3D model |
| `_currentModelShareEnabled` | `bool` | Whether the live Xbox One mesh has Share wired. Forces a rebuild on an Xbox One ↔ Xbox Series profile swap within the same asset folder. |
| `_dirty` | `bool` | Render-frame update flag |
| `_triggerAngleLeft/Right` | `float` | Current trigger angles (change detection) |
| `_flashTimer` | `DispatcherTimer` | Map All flash timer (400 ms) |
| `_flashTarget` | `string` | PadSetting name being flashed |
| `_flashOn` | `bool` | Flash toggle state |
| `_arrowVisual` | `ModelVisual3D` | Directional arrow for axis recording |
| `_quadrantRingVisual` | `ModelVisual3D` | Stick ring quadrant highlight |
| `_quadrantRingMaterial` | `DiffuseMaterial` | Quadrant ring material (alpha toggled for flash) |
| `_hoverGroup` | `Model3DGroup` | Hovered button/trigger group |
| `_hoverQuadrant` | `string` | Hover quadrant axis string |
| `_hoverQuadrantVisual` | `ModelVisual3D` | Quadrant wedge overlay for hover |
| `_isLeftDragging` | `bool` | Left-drag active (rotation) |
| `_leftMouseActive` | `bool` | True only while our handler captured the mouse (distinguishes a drag from a plain button click) |
| `_leftDragStart` | `Point` | Left-button down position (drag threshold) |
| `_isRightDragging` | `bool` | Right-drag active (panning) |
| `_rightDragLast` | `Point` | Last mouse position during drag |
| `_modelYaw` | `double` | Yaw rotation (degrees, Z axis) |
| `_modelPitch` | `double` | Pitch rotation (degrees, X axis, clamped &minus;60–60) |
| `_touchDragId` | `int?` | First touch ID (rotation) |
| `_touchSecondId` | `int?` | Second touch ID (pinch-to-zoom) |
| `_touchSecondLast` | `Point` | Last second-touch position |
| `_pinchStartDist` | `double` | Inter-finger distance at pinch start |
| `_pinchMidpoint` | `Point` | Two-finger midpoint for panning |
| `_modelRotation` | `Transform3DGroup` | Persistent scale + rotation on `ModelVisual3D.Transform` |
| `_yawRotation` | `AxisAngleRotation3D` | Yaw: axis (0,0,1) |
| `_pitchRotation` | `AxisAngleRotation3D` | Pitch: axis (1,0,0) |
| `_modelScaleTransform` | `ScaleTransform3D` | Per-model uniform scale, composed into `_modelRotation` (first child) so rotation and scale share one `Transform` assignment. Used for the DualSense down-scale. |
| `_touchpadHighlightMaterial` | `DiffuseMaterial` | Accent-color material (alpha `0xC0`) shown on the touchpad surface while click is held |
| `_touchpadCurrentlyHighlighted` | `bool` | Tracks the current touchpad material swap so it does not churn every frame |
| `_touchpadFinger0Visual` / `_touchpadFinger1Visual` | `ModelVisual3D` | Finger-sphere visuals (orange, blue) parented under `ModelVisual3D` |
| `_touchpadFinger0Transform` / `_touchpadFinger1Transform` | `TranslateTransform3D` | Per-finger position. Parked at `OffsetY = -10000` while the finger is up |

Annotation-overlay fields live in the `ControllerModelView.Annotations.cs` partial and are covered in [Annotation Overlay](#annotation-overlay).

### ViewModel Binding

```csharp
public void Bind(PadViewModel vm)
public void Unbind()
```

`Bind` subscribes to `PropertyChanged`, hooks `CompositionTarget.Rendering`, calls `EnsureModel()`, and rebuilds annotations. `OutputType` or `ProfileId` changes trigger `EnsureModel()` (the `ProfileId` path handles an Xbox One ↔ Xbox Series swap within the same `XBOXONE` asset folder, which must rebuild the mesh to flip Share between inert and live). `CurrentRecordingTarget` changes trigger flash animation and arrow overlays. All other changes set `_dirty`.

### Model Lifecycle

```csharp
private void EnsureModel()
```

Resolves the asset folder via `HMaestroProfileCatalog.ResolveAssetFolders(ProfileId, OutputType)`, which returns one of four model names:

| Profile family | Resolved folder | Model class |
|----------------|-----------------|-------------|
| DualSense / DualSense Edge | `DualSense` | `ControllerModelDualSense` |
| Xbox One, Xbox Elite, Xbox Series, Xbox Adaptive | `XBOXONE` | `ControllerModelXboxOne` |
| DualShock 4 | `DS4` | `ControllerModelDS4` |
| Xbox 360 (fallback) | `XBOX360` | `ControllerModelXbox360` |

When `XBOXONE` is selected, `EnsureModel()` also checks whether the `ProfileId` starts with `xbox-series-`. If it does, `ControllerModelXboxOne` is constructed with `enableShare: true` so the Share mesh becomes click-mappable. Xbox One, Elite, and Adaptive profiles get `enableShare: false` (mesh is rendered but inert).

The model swap is skipped when `_currentModel.ModelName == needed` and the Share-enabled flag has not changed, so re-entrancy from PropertyChanged storms is cheap.

Extended slots route to `ControllerSchematicView` instead of this view, so this control only ever sees Xbox or PlayStation slots in practice. The v2 `ExtendedConfig.Preset` enum that previously gated DS4-vs-Xbox360 model selection on Extended slots was dropped in v3 (commit `d57a725`).

Returns immediately if the current model matches. Otherwise disposes the old model, creates the new one, and assigns to `ModelVisual3D.Content`.

### Render-Frame Update Pipeline

`CompositionTarget.Rendering` handler (~60 fps), gated by `_dirty` flag:

```
OnRendering()
    |
    +-> _dirty check (skip if clean)
    |
    +-> HighlightButtons()          -- swap materials for 16 buttons
    +-> UpdateJoystick() x2         -- tilt left/right stick meshes
    +-> UpdateTrigger() x2          -- rotate left/right trigger meshes
    +-> UpdateTouchpadPreview3D()   -- touchpad highlight + finger spheres
    +-> UpdateAnnotationLevelBars() -- trigger bar heights (no-op if overlay off)
```

`UpdateTouchpadPreview3D()` runs every dirty frame but returns immediately when the current model has no `Touchpad`. `UpdateAnnotationLevelBars()` returns immediately when the overlay is off.

#### HighlightButtons()

Iterates the 16-element `ButtonProperties` array, reads each `PadViewModel` bool via `GetButtonState()`, and swaps between `DefaultMaterials` and `HighlightMaterials`:

```csharp
private static readonly string[] ButtonProperties =
{
    "ButtonA", "ButtonB", "ButtonX", "ButtonY",
    "LeftShoulder", "RightShoulder",
    "ButtonBack", "ButtonStart", "ButtonGuide",
    "ButtonShare",
    "DPadUp", "DPadDown", "DPadLeft", "DPadRight",
    "LeftThumbButton", "RightThumbButton"
};
```

`ButtonShare` only resolves to a mesh on Xbox Series profiles, where `enableShare` registered it in `ButtonMap`. On every other model `ButtonMap.TryGetValue` misses and the entry is skipped. `GetButtonState()` has a matching `"ButtonShare" => _vm.ButtonShare` case.

For each button, iterates all `Model3DGroup` entries in `ButtonMap` (multi-mesh support). Only modifies `GeometryModel3D` children with `DiffuseMaterial`.

#### UpdateJoystick()

```csharp
private void UpdateJoystick(
    short rawX, short rawY,
    Model3DGroup thumbRing, Model3D thumb,
    Vector3D rotationPoint, float maxAngleDeg)
```

1. Normalizes raw values (`short.MaxValue`) to &minus;1–1 range.
2. **Gradient highlight**: Blends default/highlight materials by deflection magnitude via `GradientHighlight()`.
3. **Rotation**: `AxisAngleRotation3D` for X (around Z) and Y (around X), centered at `rotationPoint`. Both ring and thumb meshes share the same `Transform3DGroup`.

#### UpdateTrigger()

```csharp
private void UpdateTrigger(
    double triggerNorm,
    Model3DGroup triggerModel,
    Vector3D rotationPoint,
    float maxAngleDeg,
    ref float prevAngle)
```

1. **Gradient color**: Blends default/highlight materials by trigger value (0–1).
2. **Rotation**: `AxisAngleRotation3D` around X axis at `rotationPoint`. Max angle: `-maxAngleDeg * value`.
3. **Change detection**: Skips update if angle delta < 0.01 degrees.

#### GradientHighlight()

```csharp
private static DiffuseMaterial GradientHighlight(Material defaultMaterial, Material highlightMaterial, float factor)
```

ARGB linear interpolation between default and highlight colors. Creates a new `DiffuseMaterial` per call (no caching; only called when values change).

### Model Rotation and Panning

Turntable rotation (left-drag) and camera panning (right-drag) via Preview (tunneling) events, which fire before HelixToolkit's built-in handlers and mark `e.Handled = true` to prevent double-processing.

| Event | Action |
|-------|--------|
| `PreviewMouseLeftButtonDown` | Record start position, capture mouse for rotation |
| `PreviewMouseLeftButtonUp` | Drag < 5 px -> hit-test for click-to-record; otherwise end drag |
| `PreviewMouseRightButtonDown` | Capture mouse, store start position for panning |
| `PreviewMouseRightButtonUp` | Release capture |
| `PreviewMouseMove` | Left-drag: rotate; right-drag: pan; no button: hover highlight |
| `PreviewMouseWheel` | Zoom camera along look direction |
| `PreviewTouchDown` | First finger: rotation. Second finger: pinch-to-zoom + pan. |
| `PreviewTouchMove` | One finger: rotation. Two fingers: pinch-to-zoom + midpoint pan. |
| `PreviewTouchUp` | Release touch; demote second finger to first if needed |
| `PreviewStylusSystemGesture` | Block WPF press-and-hold / flick gestures |
| `ManipulationStarting` | Cancel WPF manipulation HelixToolkit may re-enable |

Rotation is applied to `ModelVisual3D.Transform` (not the camera), keeping lighting screen-relative:
- **Yaw**: axis `(0,0,1)`, angle = `_modelYaw`
- **Pitch**: axis `(1,0,0)`, angle = `_modelPitch` (clamped &minus;60–+60 degrees)
- **Sensitivity**: 0.5 degrees per pixel. "Reset View" sets both to 0.

**Touch details:**
- **Single finger**: Rotation (same as left-drag), captured via `_touchDragId`.
- **Second finger**: Pinch-to-zoom (inter-finger distance vs `_pinchStartDist`, camera moves along look direction) + pan (midpoint tracking, camera moves perpendicular).
- **Stylus suppression**: WPF press-and-hold (synthesized right-click) and flick gestures blocked via `PreviewStylusSystemGesture`.

### Click-to-Record Hit Testing

```csharp
private void Viewport_PreviewMouseLeftButtonUp(object sender, MouseButtonEventArgs e)
```

1. `Viewport3DHelper.FindHits()` at click position.
2. For each hit `GeometryModel3D`:
   - **Stick ring**: `IsStickRingHit()` checks `LeftThumbRing`/`RightThumbRing`, delegates to `DetermineAxisFromQuadrant()`.
   - **ClickMap**: Walks entries to find the containing `Model3DGroup`.
3. Fires `ControllerElementRecordRequested` with the PadSetting target name.

### Quadrant Detection (Stick Rings)

```csharp
private bool IsStickRingHit(GeometryModel3D hitGeo, Point3D hitPos, out string axis)
```

Checks if hit geometry belongs to a stick ring, then calls:

```csharp
private static string DetermineAxisFromQuadrant(
    Point3D hitPos, Vector3D center, string xAxis, string yAxis)
```

Uses hit position relative to the stick ring's mesh centroid (`IsStickRingHit` passes `MeshCentroid(ring)`, the ring's bounding-box center, not the rotation pivot, which sits off-center on DualSense):
- **Dominant X** (`|deltaX| > |deltaZ|`): Returns `xAxis` or `xAxis + "Neg"` by deltaX sign.
- **Dominant Z**: Returns `yAxis` or `yAxis + "Neg"` by deltaZ sign.
- **Y-axis inversion**: Model Z-up = stick up. `deltaZ >= 0` maps to `yAxis + "Neg"` because Step 3's NegateAxis inverts Y output, so stick-up in-game maps to the positive direction.

### Hover Highlighting

`Viewport_PreviewMouseMove` hit-tests at the cursor on every move:

- **Buttons/triggers**: `ApplyHoverHighlight()` sets highlight material. `RestoreHoverGroup()` restores default (skipped during flash animation).
- **Stick rings**: `ShowHoverQuadrant()` creates a semi-transparent wedge overlay from the ring's mesh triangles, clipped to the target quadrant.
- `ClearHover()` removes all hover state and resets the cursor.
- `Viewport_MouseLeave` also clears hover (and releases dangling right-drag).

### Flash Animation (Map All)

```csharp
private void UpdateFlashTarget(string target)
```

Starts when `CurrentRecordingTarget` changes. A `DispatcherTimer` at 400 ms toggles highlight/default materials:

- **Buttons/triggers**: Swaps materials via `ResolveFlashGroups()`.
- **Stick axes**: `ShowQuadrantRingOverlay()` for the target quadrant + `ShowArrowForTarget()` for direction. `FlashQuadrantRing()` toggles overlay alpha between 200 and 0.
- Stops when `CurrentRecordingTarget` becomes null.

### Arrow Overlay

```csharp
private void ShowArrowForTarget(string target)
private void RemoveArrow()
```

Creates a 3D arrow (`ModelVisual3D`) via `CreateFlatArrow()`:
- Flat box (shaft) + triangular prism (head).
- Positioned at stick center, offset forward (Y = center.Y &minus; 25) for visibility.
- Direction from target: `LeftThumbAxisX` = right, `LeftThumbAxisXNeg` = left, etc.
- Uses the app's accent color.

### Quadrant Ring Overlay

```csharp
private void ShowQuadrantRingOverlay(string target)
private MeshGeometry3D BuildClippedQuadrantMesh(
    Model3DGroup ring, Vector3D center, bool isX, bool isNeg)
```

Builds a highlight overlay from the ring's mesh triangles:
1. Two half-planes at +/&minus;45 degrees isolate one quadrant.
2. **Sutherland-Hodgman clipping**: Clips each triangle against both half-planes via `ClipPolygonByHalfPlane()`.
3. **Torus-outward offset**: `OffsetTorusOutward()` pushes vertices 0.8 mm outward along the tube's radial direction to prevent z-fighting (computes nearest point on torus center circle, offsets along tube normal).
4. Triangulates clipped polygons as fans.

### Touchpad Preview (PlayStation slots)

The view renders a live touchpad preview for any model that exposes a `Touchpad` mesh (DualSense via the split-out `Touchpad.obj`, DS4 via `Screen.obj`).

```csharp
private void BuildTouchpadFingerVisuals()
private static (ModelVisual3D, TranslateTransform3D) CreateFingerSphere(Color color)
private void UpdateTouchpadPreview3D()
private static void PositionFingerSphere(
    TranslateTransform3D t, bool down, float normX, float normY, Rect3D bounds,
    ControllerModelBase model)
```

- **Build** (`BuildTouchpadFingerVisuals`, called from `EnsureModel()`): tears down any prior finger visuals, then, if `_currentModel.Touchpad != null`, builds two finger spheres and the click-highlight material. Skipped for Xbox models (no `Touchpad`).
- **Finger spheres** (`CreateFingerSphere`): a `MeshBuilder.AddSphere` of radius 2.5 (12 slices, 8 stacks). Finger 0 is orange `#FF6600`, finger 1 is blue `#0066FF` (both alpha `0xE6`), matching the 2D touchpad dots. Each sphere is a `ModelVisual3D` child of `ModelVisual3D`, so the model's uniform scale and rotation apply to it. Parked at `OffsetY = -10000` while its finger is up.
- **Click highlight** (`UpdateTouchpadPreview3D`, called every dirty frame): while `TouchpadClickPressed` is true, the touchpad surface geometry's material swaps to `_touchpadHighlightMaterial` (the app accent color at alpha `0xC0`, from `ResolveAccentColor()` reading `AccentFillColorDefaultBrush`, fallback `#2196F3`). Restored to `DefaultMaterials[Touchpad]` on release. The swap is gated by `_touchpadCurrentlyHighlighted` so it does not churn every frame.
- **Finger position** (`PositionFingerSphere`): maps the normalized `TouchpadFingerN(X,Y)` into the `Touchpad.Bounds` box. `normX 0..1` → model X left→right, `normY 0=top` → high model Z, and Y floats the sphere just in front of the surface (`bounds.Y - 1.5`). The touchpad mesh overshoots the real touch-sensitive area, so each model's `TouchpadXInsetFrac` / `TouchpadZTopInsetFrac` / `TouchpadZBottomInsetFrac` inset the mapped rectangle. DualSense overrides these (see [Touchpad Inset Region](#touchpad-inset-region)). DS4 uses the defaults `0.03 / 0.12 / 0.12`.

---

## Annotation Overlay

**File:** `PadForge.App/Views/ControllerModelView.Annotations.cs` (partial class, #175)

A 2D `Canvas` (`AnnotationCanvas`) layered over the viewport labels each mapped control with a chip at the canvas edge, a leader line to the control's projected position on the 3D model, and live input/output readouts. Off by default. State is session-only: the hosting page pushes the ViewModel value in on bind and writes it back on `AnnotationsToggled`, so nothing persists on its own.

Design constraints baked in: no storyboards, no `Effect`s. Every live state change is a plain brush or property swap (the Atom Z8350 floor re-evaluates dozens of chips at 150 ms). Re-projection is timer-driven, never per-frame.

### Constants

| Constant | Value | Meaning |
|----------|-------|---------|
| `AnnotationChipHeight` | `20` | Chip height in DIPs |
| `AnnotationChipGap` | `6` | Minimum vertical gap between stacked chips |
| `AnnotationEdgeMargin` | `8` | Inset from the canvas edge |
| `AnnotationBarHeight` | `36` | Trigger level-bar fill track height |
| `AnnotationBarTrackWidth` | `12` | Trigger level-bar track width |
| `AnnotationDetailMaxRows` | `12` | Wiring rows shown before a `+N` tail |

### Toggle and state

```csharp
public bool AnnotationsEnabled { get; set; }
private void AnnotationToggle_Click(object sender, RoutedEventArgs e)
```

The top-right toggle button (`AnnotationToggleButton`, Segoe MDL2 glyph `E8EC`) flips `AnnotationsEnabled` and raises `AnnotationsToggled`. Setting `AnnotationsEnabled` true starts the 150 ms `DispatcherTimer` and builds the overlay. Setting it false stops the timer, clears the canvas, and collapses it. The setter itself raises no event, so the owner's write-back cannot loop. While enabled the glyph and button border take `ColdBrush`.

### Chips

`RebuildAnnotations()` walks `_vm.Mappings`. For each row with a resolvable anchor (`ButtonMap` first, then the named stick/trigger groups via `ResolveAnnotationAnchor`) it subscribes to the row and, when the row `HasAnySource`, creates a chip. `HasAnySource` rather than `IsMapped` is used so a stateful primary (Ramp / Incremental), whose feeds live on the `PrimaryKindSource` keys, still gets a chip.

Each chip is a steel `Border` holding the output name, a 1px cold `Line` leader to the projected anchor, and a 6px ember `Ellipse` output dot. The chip face shows only the output name. Clicking a chip raises `AnnotationChipNavigateRequested` with the row's `TargetSettingName`. Hovering a chip shows the detail strip.

### Trigger level bars

For each shoulder trigger present, `CreateTriggerBars()` builds a steel track holding two stacked `Rectangle`s: a cold bar (raw selected-device level, `_vm.DeviceLeftTrigger` / `DeviceRightTrigger`) and an ember bar (combined slot output, `_vm.LeftTrigger` / `RightTrigger`). `UpdateAnnotationLevelBars()` sets bar heights every dirty frame from `OnRendering`. The track shows only when both its anchor projects on-canvas and a level is above `0.02`, so an idle empty track never reads as a stray box on the trigger.

### Detail strip and tooltips

`BuildAnnotationDetailContent()` builds a fan-in wiring diagram shared by the chip tooltip and the bottom-docked hover strip: every source feeding the row stacks on the left (each tagged with its device name and class glyph), one arrow points into the ember output name on the right. It caps at `AnnotationDetailMaxRows` rows with a locale-neutral `+N` tail. Long names wrap, never truncate.

### Re-projection cadence

`ProjectAnnotationAnchor()` projects a group's centroid: local → world via the same `ModelVisual3D.Transform` the hit-test path inverts, world → 2D via `Viewport3DHelper.Point3DtoPoint2D`, with a behind-camera cull. `ReprojectAnnotations()` runs the full projection plus a two-pass column layout (downward greedy, then an upward overflow fix) that keeps chips from overlapping.

The 150 ms `AnnotationTick` is the primary re-projection trigger. `CameraChanged` and `SizeChanged` also call `ReprojectAnnotations()`, but the direct `cam.Position` / rotation-angle writes this view uses bypass Helix's `CameraController`, so `CameraChanged` may never fire. The overlay hides during an active drag (`SetAnnotationsDragHidden`) and re-projects once when the drag ends. Only the trigger bar heights update at render rate (from `OnRendering`). The ember output dots flip on the 150 ms `AnnotationTick`. Chip positions move only on re-projection.

<!-- SCREENSHOT: 3d-model-annotation-overlay -->
![3D controller model with the annotation overlay enabled: edge chips, leader lines, and trigger level bars](../images/3d-model-annotation-overlay.png)

---

## Material System

All models use WPF `DiffuseMaterial` with `SolidColorBrush`. Three categories:

| Category | Source | Storage | Usage |
|----------|--------|---------|-------|
| **Default** | Static `Color` fields per subclass (e.g., `ColorPlasticWhite`). Xbox 360 face overlays use `Alpha = 150`. | `DefaultMaterials[group]` | Restored after highlight/flash |
| **Highlight** | `DrawAccentHighlights()` reads `SystemAccentColorPrimary` (WPF-UI theme), falls back to `#FF6B2C` ember. | `HighlightMaterials[group]` | Applied on press or flash |
| **Gradient** | `GradientHighlight()` ARGB-interpolates default/highlight per call. | None (created per call) | Sticks and triggers (proportional) |

Gradient materials are not cached. The dirty flag limits updates to one per render frame, WPF3D materials are lightweight, and gradients only update when values change.

---

## Coordinate System and Transformations

### Model Space

Standard WPF3D right-handed coordinates:

| Axis | Direction |
|------|-----------|
| X | Left (negative) / Right (positive) |
| Y | Forward-backward (camera view axis) |
| Z | Up (positive) / Down (negative) |

### Camera Setup

`PerspectiveCamera`: Position `(0, -172, 132)` (behind and above), LookDirection `(0, 0.793, -0.609)` (forward + slightly down), Z-up, 55-degree FOV.

### Model Rotation Transform

Applied to `ModelVisual3D.Transform` (not the camera) so lighting stays screen-relative.

| Transform | Axis | Source | Clamp |
|-----------|------|--------|-------|
| Yaw | Z (0,0,1) | Left-drag horizontal | None |
| Pitch | X (1,0,0) | Left-drag vertical | &minus;60–+60 degrees |

### Joystick Tilt Transform

`Transform3DGroup` on both ring and thumb meshes:
1. **X tilt**: Around Z axis, proportional to stick X, centered at `JoystickRotationPointCenter{Left/Right}Millimeter`.
2. **Y tilt**: Around X axis, proportional to stick Y, same center.

Both capped at `JoystickMaxAngleDeg` (19 degrees for Xbox 360 and DS4).

### Trigger Rotation Transform

Rotates around X axis at `ShoulderTriggerRotationPointCenter{Left/Right}Millimeter`. Angle: `-TriggerMaxAngleDeg * value` (negative = downward). Skips update if angle delta < 0.01 degrees.

---

## Lighting

Three light sources in XAML:
- **`SunLight`**: HelixToolkit built-in (ambient + directional, world-space).
- **`DirectionalHeadLight`**: Camera-relative at brightness 0.35, prevents dark spots during rotation.
- **Ember rim `DirectionalLight`** (#175): dim warm rim, `Color="#5A321C"`, `Direction="0,-0.7,0.7"` (from behind and below), so the model catches a forge-glow edge. The RGB stays low to keep it a rim rather than a wash.

---

## Performance Considerations

| Technique | Detail |
|-----------|--------|
| **Dirty flag batching** | 16 buttons + 4 axes + 2 triggers + touchpad preview + annotation bars coalesced into one render-frame update. |
| **Trigger change detection** | Skips rotation if angle delta < 0.01 degrees. |
| **No gradient caching** | New `DiffuseMaterial` per call; acceptable since dirty flag limits frequency and WPF3D materials are lightweight. |
| **One-time mesh loading** | OBJ meshes load in the constructor. `EnsureModel()` recreates only when the resolved model name changes or the Xbox One Share flag flips. |
| **Preview events** | Tunneling events prevent double-processing by HelixToolkit and PadForge. |

---

## See Also

- [2D Overlay System](2d-overlay-system.md): `ControllerModel2DView` (PNG overlay alternative to 3D), `ControllerSchematicView`, `KBMPreviewView`, `MidiPreviewView`
- [ViewModels](viewmodels.md): `PadViewModel` properties bound by `ControllerModelView`
- [XAML Views](xaml-views.md): `PadPage` hosts and switches between 3D, 2D, schematic, KBM, and MIDI views
- [Virtual Controllers](../features/virtual-controllers.md): Output type determines which preview view is active
- [Engine Library](engine-library.md): `Gamepad` struct providing button/axis state for 3D animation
- [Build and Publish](build-and-publish.md): 3D OBJ meshes (`3DModels/`) included as `EmbeddedResource` items

---

*Last updated for PadForge 4.0.0*
