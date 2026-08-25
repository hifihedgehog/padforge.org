# Head Tracking (OpenTrack)

*A head pose from OpenTrack, or from anything that speaks its output formats, as six axes you can map like a stick.*

[OpenTrack](https://github.com/opentrack/opentrack) turns a webcam, an IR clip, a phone, or an eye tracker into a head pose: three rotations and three translations. On Windows its outputs are FreeTrack, TrackIR emulation, mouse movement, UDP, and a few sim-specific bridges. None of them is a gamepad. PadForge reads two of those outputs and turns the pose into a device row with six axes, so head yaw can drive a virtual controller's right stick while both thumbs stay on the face buttons.

---

## Turning it on

Open **Settings** and turn on **Enable Head Tracking Input**. A **Head Tracker** row appears on the [Devices](devices.md) page with six axes:

| Axis | What it reads | Full deflection |
| --- | --- | --- |
| Head Yaw | turning left and right | Rotation Range |
| Head Pitch | nodding up and down | Rotation Range |
| Head Roll | tilting toward a shoulder | Rotation Range |
| Head X | sliding left and right | Translation Range |
| Head Y | rising and ducking | Translation Range |
| Head Z | leaning in and back | Translation Range |

Every axis rests at center. **Rotation Range** (degrees, default 90) and **Translation Range** (centimeters, default 30) set how far the head has to move for an axis to reach its end. The vertical axes are stored the way a stick reports them, up at the low end, so mapping Head Pitch onto a stick's Y axis needs no inversion.

With the toggle off, nothing runs: no device row, no socket, no shared memory, no thread.

---

## Setting up OpenTrack

Two outputs work, and both can be on at once.

**UDP over network.** In OpenTrack's Output list choose *UDP over network*, open its settings, and set the address to 127.0.0.1 (OpenTrack's default is 192.168.0.2, which is another machine) and the port to the one shown under **UDP Port** in PadForge (default 4242). Click Start. The Head Tracker row's details pane changes from "Waiting for a tracker" to "Receiving over UDP from 127.0.0.1".

**freetrack 2.0 Enhanced.** If a game already reads FreeTrack from OpenTrack, keep that output and leave **Also Read FreeTrack 2.0 Shared Memory** on in PadForge. PadForge reads the same `FT_SharedMem` block the game does, so both see the pose. The details pane says "Receiving from FreeTrack shared memory".

Phone trackers and other programs that send the OpenTrack UDP format can point straight at PadForge on the same port. PadForge adds an inbound firewall rule for the port when the row opens.

When OpenTrack stops, or the camera loses the face for a second, the axes return to center so a stick is never left pinned. The row stays online, so mappings can be made before the tracker is started.

---

## Mapping it

On the Pad page, pick **Head Yaw** as the source of the right stick's X axis and set a deadzone on that mapping for the angle you want ignored. Deadzone, curve, and inversion are the ordinary per-mapping controls, the same ones a physical stick gets. OpenTrack's own mapping curves still apply first, so a curve shaped in OpenTrack arrives already shaped.

The six axes bind anywhere an axis does: stick and trigger outputs, mouse movement, macro triggers, formulas, and auto-profile conditions.

---

## What it does not do

TrackIR's NPClient interface is a DLL the game loads by game ID, not a stream anything can subscribe to. Games that only speak TrackIR keep using OpenTrack's own output for that.

Two listeners cannot share one UDP port. If OpenTrack's own *UDP* tracker input is set to the same port, the details pane says the port is in use, and one of them needs a different port.
