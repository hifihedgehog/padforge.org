# A Five-Minute Remap

*Change what a button does. The walkthrough swaps A and B, and the same
moves cover any rebind you will ever make.*

You need a virtual controller with a physical pad assigned to it. That is
[Your First Controller](first-controller.md).

---

## 1. Open the mapping table

On the [Dashboard](../features/dashboard.md), click the slot's card to
open its configuration, then open the **Mappings** tab. One table drives
the whole slot: each row is one output the game sees, grouped into
Buttons, Left Stick, Right Stick, Triggers, and D-Pad.

![Button and axis mapping grid with source, value, and record columns](../images/pad-mappings.png)

## 2. Record the first swap

1. Find the **A** row under Buttons.
2. Click **Record** on that row. The button changes to "Recording..." and
   the row pulses blue.
3. Press **B** on your physical pad.

PadForge captures the press, fills in the source, and stops recording.
The A output is now driven by the physical B button.

> **Tip:** Press only the input you want. Wiggling a stick while pressing
> a button can catch the stick instead.

## 3. Record the other half

Do the same on the **B** row: click **Record**, press **A** on the pad.
The swap is complete.

## 4. Verify on the spot

Press A and B on the pad and watch the **Value** column. Each press lights
the swapped row in real time, and what you see there is exactly what the
game gets. No save step, no apply step. Your mapping persists in
`PadForge.xml` next to the executable.

---

## When recording grabs the wrong input

Use the source dropdown instead. Each source has a cascading dropdown:
pick the device, then the exact input ("B", "Axis 3", "POV 0 Up").
Picking an input assigns it on the spot, same result as recording. The
blank entry at the top clears the source, and the row's **Clear** button
resets the whole row.

## When you want to remap everything

**Map All**, on the Controller tab or the Mappings tab toolbar, walks
every row in order: it highlights a row, prompts for the matching input,
captures it, and moves on. The fastest way to set up an unrecognized
device (a generic joystick, an arcade encoder) from scratch.

---

## Where to go next

- Multiple sources on one row, invert and half-axis options, and combine
  modes: [Button and Axis Mappings](../features/mappings.md).
- A second binding set on the same pad, held or toggled:
  [Shift Layers](../guides/shift-layers.md).
- Timed sequences on one press: [Macros](../guides/macros.md).
