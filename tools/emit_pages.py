"""Emit wiki/devices/supported.md and the specs.html Devices block.

Run from anywhere: python tools/emit_pages.py
Reads the SDL fork's tables through emit_supported, so a rebase regenerates
rather than leaving the lists to rot.
"""
import io, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emit_supported import fam, mapped, CAT, N, FAM_ORDER, lines, SITE

Q = '"'


def md():
    L = [
        "# Supported Devices",
        "",
        "*Every controller, wheel, stick and adapter PadForge knows by name, in one place.*",
        "",
        "PadForge recognizes **{union}** devices by their USB identity: {pads} gamepads, "
        "{wheels} racing wheels, {sticks} flight sticks, {throttles} throttles, {arcade} arcade "
        "sticks and {gamecube} GameCube adapters. Behind those sit **{mapped}** shipped gamepad "
        "mappings and 225 device profiles.".format(**N),
        "",
        '!!! tip "Not on this list?"',
        "    It very likely still works. Anything Windows enumerates as an input device can be read",
        "    as a mapping source, including generic DirectInput joysticks, keyboards, mice, touchpads",
        "    and MIDI gear. This list is where the **names, the correct button layout and the extra",
        "    capabilities** come from, not the boundary of what PadForge accepts. A pad that is not",
        "    listed appears as a generic controller and maps the same way.",
        "",
        "---",
        "",
        "## Gamepads",
        "",
        "Grouped by the family each pad reports as. A third-party pad in an Xbox 360 or PlayStation 4",
        "family gets that family's layout and works everywhere that family does.",
        "",
    ]
    for f in FAM_ORDER:
        if fam.get(f):
            L += ["### {0} ({1})".format(f, len(fam[f])), "", lines(fam[f]), ""]
    L += [
        "### With a shipped mapping ({0})".format(len(mapped)),
        "",
        "Pads carrying a mapping in the database, so their buttons and axes land in the right places",
        "the moment they are plugged in.",
        "",
        lines(mapped),
        "",
        "---",
        "",
        "## Racing wheels ({0})".format(len(CAT["wheels"])),
        "",
        "**Driven in the wheel's own protocol**, with rotation range, autocenter and the LED strip on",
        "the wheels that have them: the Logitech, Thrustmaster and Fanatec models. Everything else is",
        "recognized as a wheel and takes force feedback through the standard path. See",
        "[Force Feedback](../features/force-feedback.md).",
        "",
        lines(CAT["wheels"]),
        "",
        "**Pedals.** Fanatec ClubSport V3, CSL Elite, CSL Loadcell and CSL Loadcell V2, each with its",
        "own rumble output. Pedal sets that enumerate separately are read as their own device, so they",
        "feed a slot alongside the wheel.",
        "",
        "---",
        "",
        "## Flight controls",
        "",
        "### Sticks ({0})".format(len(CAT["sticks"])),
        "",
        lines(CAT["sticks"]),
        "",
        "### Throttles ({0})".format(len(CAT["throttles"])),
        "",
        lines(CAT["throttles"]),
        "",
        "A stick, a throttle and a set of pedals each read as their own device and can feed one virtual",
        "controller together, so a button on the throttle chords with a button on the stick.",
        "",
        "---",
        "",
        "## Arcade sticks ({0})".format(len(CAT["arcade"])),
        "",
        lines(CAT["arcade"]),
        "",
        "---",
        "",
        "## GameCube adapters ({0})".format(len(CAT["gamecube"])),
        "",
        lines(CAT["gamecube"]),
        "",
        "---",
        "",
        "## Beyond gamepads",
        "",
        "PadForge reads these as mapping sources too. Each has its own lane rather than being treated",
        "as a generic joystick.",
        "",
        "| Device | What PadForge reads | More |",
        "| --- | --- | --- |",
        "| **DualSense, DualSense Edge** | Gyro, accelerometer, touchpad, adaptive triggers, lightbar, player LEDs, speaker, microphone, mute button, Edge paddles and Fn buttons | [Adaptive Triggers](../features/adaptive-triggers.md) |",
        "| **DualShock 4** | Gyro, accelerometer, touchpad, lightbar, speaker | [Lighting](../features/lighting.md) |",
        "| **DualShock 3** | Motion, pressure-sensitive buttons, pairing over USB | [DualShock 3](dualshock-3.md) |",
        "| **PlayStation Move, Navigation** | Gyro, accelerometer, the lit sphere, analog trigger and d-pad pressure | [PlayStation Move](ps-move.md) |",
        "| **Switch Pro, Switch 2 Pro** | Gyro, accelerometer, HOME LED, rumble, NFC on the pads that have it | [Wii Controllers](wii-controllers.md) |",
        "| **Joy-Con, Joy-Con 2** | Per-half motion, HD Rumble, the right Joy-Con IR camera brightness, the Joy-Con 2 optical mouse, combined-pair motion | [Wii Controllers](wii-controllers.md) |",
        "| **Wii Remote, Nunchuk, Classic, Wii U Pro** | Motion, Motion Plus, the IR pointer, the extension port, the speaker | [Wii Controllers](wii-controllers.md) |",
        "| **Wii Balance Board** | Total weight and lean on both axes | [Wii Controllers](wii-controllers.md) |",
        "| **Steam Controller, Steam Deck** | Trackpads, gyro, haptics | [Touchpad](../features/touchpad.md) |",
        "| **Xbox One, Elite, Series** | Impulse triggers, Guide LED brightness, paddles | [Impulse Triggers](../features/impulse-triggers.md) |",
        "| **3Dconnexion SpaceMouse** | All six axes of the puck, as ordinary mapping sources | [SpaceMouse](spacemouse.md) |",
        "| **VR controllers** | Any OpenVR controller through SteamVR, as a slot with hand roles | [VR Controllers](../features/vr-controllers.md) |",
        "| **Sony wireless headsets** | Head rotation as a motion source | [Headset Motion](../features/headset-motion.md) |",
        "| **MIDI keyboards and pad controllers** | Notes, Control Change, pitch bend and encoders | [MIDI Input](../features/midi-input.md) |",
        "| **NFC readers** | Registered tags as button sources | [NFC Tags](../features/nfc-tags.md) |",
        "| **Keyboards and mice** | Every key, button, wheel and motion axis, per device | [Mappings](../features/mappings.md) |",
        "| **Precision touchpads** | Multi-touch contacts, gestures, per-pad settings | [Touchpad](../features/touchpad.md) |",
        "| **Trackballs** | Motion with momentum | [Input Precision](../features/input-precision.md) |",
        "| **Microphones** | Spoken phrases as macro triggers | [Voice Macros](../features/voice-macros.md) |",
        "| **Phones and tablets** | A browser gamepad over Wi-Fi, no app install | [Web Controller](../guides/web-controller.md) |",
        "| **Another PC's controllers** | Any device above, shared over the network or the internet | [Remote Link](../guides/remote-link.md) |",
        "",
        "---",
        "",
        "*Last updated for PadForge 4.3.1.*",
        "",
    ]
    return "\n".join(L)


def row(dt, dd):
    return ('                <div class="spec-row">\n'
            '                    <dt>' + dt + '</dt>\n'
            '                    <dd>' + dd + '</dd>\n'
            '                </div>\n')


def dim(n):
    return ' <span style=' + Q + 'opacity:.6' + Q + '>(' + str(n) + ')</span>'


def html():
    h = ['        <section class="spec-block" id="hardware">\n',
         '            <h2 class="display-s spec-h reveal">Devices, by name</h2>\n',
         '            <p class="reveal" data-d="1" style="max-width:74ch; margin-bottom:2rem">'
         'PadForge recognizes <b>{union}</b> devices by their USB identity: {pads} gamepads, '
         '{wheels} racing wheels, {sticks} flight sticks, {throttles} throttles, {arcade} arcade '
         'sticks and {gamecube} GameCube adapters, with <b>{mapped}</b> shipped gamepad mappings '
         'and 225 device profiles behind them. Anything not named here still works as a generic '
         'input device, so this is where the names, the correct layout and the extra capabilities '
         'come from rather than the limit of what PadForge reads.</p>\n'.format(**N),
         '            <dl class="spec-list reveal" data-d="1">\n']
    for f in FAM_ORDER:
        if fam.get(f):
            h.append(row(f + ' pads' + dim(len(fam[f])), lines(fam[f])))
    h.append(row('Pads with a shipped mapping' + dim(len(mapped)), lines(mapped)))
    h.append(row('Racing wheels' + dim(len(CAT['wheels'])),
                 "<b>Driven in the wheel's own protocol:</b> the Logitech, Thrustmaster and Fanatec "
                 "models, with rotation range, autocenter and the LED strip. <b>Recognized and mapped, "
                 "force feedback through the standard path:</b> everything else. " + lines(CAT['wheels'])))
    h.append(row('Pedals', 'Fanatec ClubSport V3, CSL Elite, CSL Loadcell and CSL Loadcell V2, each '
                           'with its own rumble output.'))
    h.append(row('Flight sticks' + dim(len(CAT['sticks'])), lines(CAT['sticks'])))
    h.append(row('Throttles' + dim(len(CAT['throttles'])), lines(CAT['throttles'])))
    h.append(row('Arcade sticks' + dim(len(CAT['arcade'])), lines(CAT['arcade'])))
    h.append(row('GameCube adapters' + dim(len(CAT['gamecube'])), lines(CAT['gamecube'])))
    h.append(row('Beyond gamepads',
                 'DualSense and Edge, DualShock 4 and 3, PlayStation Move and Navigation, Switch Pro '
                 'and Switch 2 Pro, Joy-Con and Joy-Con 2, Wii Remote with Nunchuk, Classic and Wii U '
                 'Pro, Wii Balance Board, Steam Controller and Steam Deck, Xbox One, Elite and Series, '
                 '3Dconnexion SpaceMouse, any OpenVR controller through SteamVR, Sony wireless headsets '
                 'for head rotation, MIDI keyboards and pad controllers, NFC readers, keyboards, mice, '
                 'precision touchpads, trackballs, microphones for voice macros, phones over the '
                 'browser, and any of these shared from another PC over Remote Link.'))
    h.append('            </dl>\n')
    h.append('        </section>\n\n')
    return ''.join(h)


io.open(os.path.join(SITE, 'wiki', 'devices', 'supported.md'), 'w',
        encoding='utf-8', newline='\r\n').write(md())
io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '_specs_block.html'), 'w',
        encoding='utf-8', newline='\r\n').write(html())
print('wrote wiki/devices/supported.md and _specs_block.html')
