# Menus

*Turn a stick, a touchpad, or any two recorded axes into an on-screen ring or grid of commands.*

<!-- SCREENSHOT: pad-menus (capture post-deploy: Menus tab with a radial menu selected, cell bindings visible) -->

A menu puts a set of commands on an input surface. Engage the surface and a ring or grid appears on screen. Point at a cell and it highlights. Depending on the fire mode, the cell's binding fires on click, on release, or the whole time it is hovered. It is the same idea as Steam Input's radial and touch menus, and configs imported from the [Steam Workshop](steam-workshop-import.md) bring theirs along.

Each slot has its own menu list. Open a slot, switch to the **Menus** tab, and click **Add**. **Remove** and **Duplicate** manage the list.

---

## Style

| Style | How cells are picked |
|---|---|
| **Radial Ring** | By direction. The ring splits into equal wedges, straight up is the first cell, and the wedges run clockwise. Works best on a stick. A radial menu can also carry a **Center Cell**, selected while the stick rests inside the engage deadzone. |
| **Touch Grid** | By position. Cells lay out on a near-square grid, wider than tall (4 cells make 2×2, 12 make 4×3), and your touch point picks the cell under it. Works best on a touchpad. |

---

## Opens With

The **Opens With** picker sets the input that opens and steers the menu. It reads the physical controllers assigned to the slot, never the virtual controller's layout. The cell bindings below are what the menu outputs. A Record button next to the picker captures the host from a live input, and a reset restores the default (**Right Stick**).

| Host | How it engages |
|---|---|
| **Left Stick** / **Right Stick** | When the stick leaves the **Engage Deadzone** (default 25). |
| **Touchpad 1** and up | On touch. A **Pad Half** picker (**Whole Pad**, **Left Half**, **Right Half**) narrows the menu to half the pad, so one pad can carry two menus, the way Steam treats the PS touchpad as two. |
| **Custom Axes** | Record any two axes as **Steer X** and **Steer Y**, then push past the deadzone like a stick. This is how joysticks, wheels, and other non-gamepad devices host menus. |

### Click Input

**Click Input** sets the button the **On Click** and **On Click Release** fire modes read, recordable from any assigned device. Left empty it shows **(host default)**: the stick click for a stick host, the trackpad click for a touchpad. A **Custom Axes** host has no default click, so record one before using those two fire modes.

---

## Fire Mode

| Mode | When a cell fires |
|---|---|
| **On Click** (default) | The hovered cell's binding holds the whole time the host surface is clicked. |
| **On Click Release** | The hovered cell fires once when the click releases. |
| **On Touch Release** | The last hovered cell fires once when you let go: the finger lifts, or the stick returns inside the deadzone. Letting go with nothing hovered dismisses the menu without firing. |
| **While Hovered** | The hovered cell is active the entire time it is hovered. No click needed. |

---

## Cells

**Cells** sets how many cells the menu carries, 1 to 20. For a radial menu that is the ring count, with the optional **Center Cell** on top. Each cell has:

- A **Label**, rendered on the overlay.
- A binding: **None**, a **Keyboard Key**, or a **Controller Button**.

**Controller Button** speaks the slot's own lettering: Xbox letters on an Xbox slot, DualShock symbols on a PlayStation slot, Nintendo letters on a Nintendo slot, and the custom layout's numbered buttons on an Extended slot. Keyboard + Mouse, MIDI, and VR slots have no controller buttons to press, so the choice is not offered there, and a button binding left behind by a slot-type switch shows as **Controller Button (not on this slot type)**.

### Cells as sources

Every cell also fires as a menu-item source, pickable in [Mappings](../features/mappings.md) rows and macro triggers as entries like **Menu 1 Cell 3**. A cell set to **None** still fires this way, so a cell can do real work with no direct binding. A cell driven through a mapping row or macro shows **Used by a mapping or macro** in its binding picker.

A menu imported from the Steam Workshop can carry richer cell behavior (key combos, layer switches, macros). Those arrive wired through the profile's mapping rows and macros automatically, so the cell fires whatever the config authored even though the cell row here shows no direct binding.

---

## The overlay

While a menu is engaged, a click-through overlay draws the ring or grid at the configured spot on the primary monitor, with the hovered cell highlighted in PadForge's ember accent. It never steals focus from the game.

Per-menu appearance controls: **Show Labels**, **Screen Position** (X and Y percent, default centered), **Size** (10–400%), and **Opacity** (5–100%, default 90).

The overlay itself is optional. The [Dashboard](../features/dashboard.md)'s **Overlays** card carries a **Menu Overlay** toggle, on by default. Turn it off and menus still hover and fire, just without the picture, which suits layouts you know by muscle memory. One menu shows at a time: the first one engaged wins until it disengages.

---

## Menus and shift layers

A menu imported from a Steam config that lived on an action layer engages only while that [shift layer](shift-layers.md) is held. Releasing the layer counts as letting go, so an On Touch Release menu commits its hovered cell right there, matching Steam's mode-shift behavior. Menus you add by hand are always available.

---

## Reset buttons

Every setting row on the Menus tab carries a per-field reset, and the overlay card has a reset of its own.

---

## Related pages

- [Steam Workshop Config Import](steam-workshop-import.md): imported radial and touch menus land here.
- [Shift Layers](shift-layers.md): layer-scoped menus and what layer cells become.
- [Button and Axis Mappings](../features/mappings.md): menu cells as mapping sources.
- [Macros](macros.md): menu cells can trigger macros, and imported cells can fire them.
- [Touchpad](../features/touchpad.md): the other things a touchpad surface can do.
- [Dashboard](../features/dashboard.md): the Menu Overlay toggle.

---

*Last updated for PadForge 4.3.0.*
