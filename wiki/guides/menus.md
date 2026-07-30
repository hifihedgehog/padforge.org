# Menus

*Turn a stick or touchpad into an on-screen ring or grid. Hover to pick a cell, and a fire mode decides when the pick commits.*

<!-- SCREENSHOT: pad-menus (capture post-deploy: Menus tab with a radial menu selected, cell bindings visible) -->

A menu puts a set of commands on a stick or touchpad surface. Engage the surface and a ring or grid appears on screen. Point at a cell and it highlights. Depending on the fire mode, the cell's binding fires on click, on release, or the whole time it is hovered. It is the same idea as Steam Input's radial and touch menus, and configs imported from the [Steam Workshop](steam-workshop-import.md) bring theirs along.

Each slot has its own menu list. Open a slot, switch to the **Menus** tab, and click **Add**. **Remove** and **Duplicate** manage the list.

---

## Style

| Style | How cells are picked |
|---|---|
| **Radial Ring** | By direction. The ring splits into equal wedges, straight up is the first cell, and the wedges run clockwise. Works best on a stick. A radial menu can also carry a **Center Cell**, selected while the stick rests inside the engage deadzone. |
| **Touch Grid** | By position. Cells lay out on a near-square grid, wider than tall (4 cells make 2×2, 12 make 4×3), and your touch point picks the cell under it. Works best on a touchpad. |

---

## Host Input

The **Host Input** picker sets the surface that drives the menu: **Left Stick**, **Right Stick**, or a touchpad (**Touchpad 1** and up). A Record button next to the picker captures the host from a live input, and a reset restores the default (Right Stick).

- A stick host engages when the stick leaves the **Engage Deadzone** (default 25) and reads the stick click as the menu's click.
- A touchpad host engages on touch and reads the pad click.
- On a single-pad controller (DualSense, DualShock 4) a **Pad Half** picker narrows the host to **Left Half** or **Right Half**, so one pad can carry two menus, the way Steam treats the PS touchpad as two.

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
- A binding: **None**, a **Keyboard Key**, or a **Controller Button** (Xbox naming).

A menu imported from the Steam Workshop can carry richer cell behavior (key combos, layer switches, macros). Those arrive wired through the profile's mapping rows and macros automatically, so the cell fires whatever the config authored even though the cell row here shows no direct binding.

---

## The overlay

While a menu is engaged, a click-through overlay draws the ring or grid at the configured spot on the primary monitor, with the hovered cell highlighted in the system accent color. It never steals focus from the game.

Per-menu appearance controls: **Show Labels**, **Screen Position** (X and Y percent, default centered), **Size** (10–400%), and **Opacity** (5–100%, default 90).

The overlay itself is optional. The [Dashboard](../features/dashboard.md) carries a **Menu Overlay** toggle, on by default. Turn it off and menus still hover and fire, just without the picture, which suits layouts you know by muscle memory. One menu shows at a time: the first one engaged wins until it disengages.

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
- [Macros](macros.md): imported menu cells can fire macros.
- [Touchpad](../features/touchpad.md): the other things a touchpad surface can do.
- [Dashboard](../features/dashboard.md): the Menu Overlay toggle.

---

*Last updated for PadForge 4.1.0.*
