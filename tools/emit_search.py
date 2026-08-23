"""Emit assets/device-search.js, and prove the matcher before it is ported to JS.

The matching algorithm below is written twice on purpose: once in Python where
it can be tested against real queries, and once in JavaScript in the emitted
file. They are line-for-line equivalent, so a change to one has to be made to
the other.
"""
import io, os, re, sys, json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from emit_supported import fam, mapped, CAT, N, FAM_ORDER, SITE

# ── category table. Order matters: the first category a name lands in wins. ──
CATS = [
    ("wn", "Racing wheel", "Force feedback driven in the wheel's own protocol."),
    ("wh", "Racing wheel", "Recognized as a wheel, with force feedback through the standard path."),
    ("pd", "Pedals", "Read as its own device, with its own rumble output."),
    ("fs", "Flight stick", "Read as its own device, so it can share a slot with a throttle."),
    ("th", "Throttle", "Read as its own device, so it can share a slot with a stick."),
    ("ar", "Arcade stick", "Full button layout, no deadzone handling needed."),
    ("gc", "GameCube adapter", "Each port reads as its own controller."),
    ("x3", "Xbox 360 family", "Gets the Xbox 360 layout and works everywhere that family does."),
    ("x1", "Xbox One and Series family", "Impulse triggers and Guide LED brightness where the pad has them."),
    ("p3", "PlayStation 3 family", "Motion and pressure-sensitive buttons on the pads that have them."),
    ("p4", "PlayStation 4 family", "Gyro, touchpad and lightbar on the pads that have them."),
    ("p5", "PlayStation 5 family", "Gyro, touchpad, adaptive triggers, lightbar, speaker and mic."),
    ("sw", "Nintendo Switch family", "Gyro, rumble and HOME LED on the pads that have them."),
    ("s2", "Nintendo Switch 2 family", "Gyro and rumble, plus the Joy-Con 2 mouse where present."),
    ("st", "Steam family", "Trackpads, gyro and haptics."),
    ("bd", "8BitDo", "Full mapping, including the Ultimate and Pro lines."),
    ("mp", "Gamepad", "Ships with a mapping, so buttons and axes land correctly on plug-in."),
    ("sp", "Specialty device", "Has its own lane in PadForge rather than being read as a joystick."),
]

FAM_CODE = {
    "Xbox 360": "x3", "Xbox One and Series": "x1", "PlayStation 3": "p3",
    "PlayStation 4": "p4", "PlayStation 5": "p5", "Nintendo Switch": "sw",
    "Nintendo Switch 2": "s2", "Steam": "st", "8BitDo": "bd", "Other": "mp",
}

NATIVE_WHEEL = ("logitech", "thrustmaster", "fanatec")

SPECIALTY = [
    "DualSense", "DualSense Edge", "DualShock 4", "DualShock 3",
    "PlayStation Move Motion Controller", "PlayStation Move Navigation Controller",
    "Nintendo Switch Pro Controller", "Nintendo Switch 2 Pro Controller",
    "Joy-Con (L)", "Joy-Con (R)", "Joy-Con pair", "Joy-Con 2",
    "Wii Remote", "Wii Nunchuk", "Wii Classic Controller", "Wii U Pro Controller",
    "Wii MotionPlus", "Wii Balance Board", "Steam Controller", "Steam Deck",
    "3Dconnexion SpaceMouse", "SpaceMouse Pro", "SpaceMouse Wireless",
    "SpaceNavigator", "SpacePilot", "Spaceball 5000",
    "Sony PULSE 3D Wireless Headset", "Sony PULSE Elite", "Sony PULSE Explore",
    "OpenVR controller", "SteamVR controller", "Valve Index controller",
    "Oculus Touch", "HTC Vive controller", "Windows Mixed Reality controller",
    "MIDI keyboard", "MIDI pad controller", "NFC reader", "amiibo",
    "Keyboard", "Mouse", "Precision touchpad", "Trackball", "Microphone",
    "Phone", "Tablet", "iPhone", "Android phone", "Web controller",
]

PEDALS = ["Fanatec ClubSport Pedals V3", "Fanatec CSL Elite Pedals",
          "Fanatec CSL Pedals Loadcell", "Fanatec CSL Pedals Loadcell V2"]

# Extra words a person is likely to type that the shipped name does not contain.
# Substring keyed, first match wins, applied on top of the name and category.
ALIASES = [
    ("gunfighter", "VKB Gunfighter"),
    ("hotas warthog", "Thrustmaster HOTAS"),
    ("t.16000", "Thrustmaster"),
    ("dualsense edge", "PS5 PlayStation 5 Sony"),
    ("dualsense", "PS5 PlayStation 5 Sony"),
    ("dualshock 4", "PS4 DS4 PlayStation 4 Sony"),
    ("dualshock 3", "PS3 DS3 SixAxis PlayStation 3 Sony"),
    ("playstation move", "PSMove Sony wand"),
    ("wii remote", "Wiimote Nintendo"),
    ("wii balance", "Nintendo"),
    ("switch 2 pro", "NSO Nintendo"),
    ("switch pro controller", "NSO Nintendo"),
    ("joy-con", "JoyCon Nintendo"),
    ("steam deck", "Valve handheld"),
    ("steam controller", "Valve"),
    ("spacemouse", "3Dconnexion 6DoF puck CAD"),
    ("spacenavigator", "3Dconnexion 6DoF"),
    ("spacepilot", "3Dconnexion 6DoF"),
    ("spaceball", "3Dconnexion 6DoF"),
    ("pulse 3d", "Sony headset PS5"),
    ("pulse elite", "Sony headset PS5"),
    ("pulse explore", "Sony earbuds PS5"),
    ("openvr", "SteamVR VR virtual reality"),
    ("steamvr", "OpenVR VR virtual reality"),
    ("valve index", "VR SteamVR knuckles"),
    ("oculus touch", "VR Meta Quest"),
    ("htc vive", "VR SteamVR"),
    ("windows mixed reality", "VR WMR"),
    ("precision touchpad", "trackpad laptop"),
    ("nfc reader", "amiibo ACR122U tag"),
    ("web controller", "phone browser wifi"),
    ("midi", "music DAW"),
    ("g29", "Driving Force"),
    ("g920", "Driving Force"),
    ("g923", "Driving Force"),
]


def aliases_for(name):
    low = name.lower()
    for key, extra in ALIASES:
        if key in low:
            return extra
    return ""


# SDL annotates some entries in the name itself ("Victrix Pro FS (PS4
# peripheral but no trackpad/lightbar)"). Those read as commentary, not as a
# product name, so they are trimmed for display. A short parenthetical that
# disambiguates a real variant, like Joy-Con (L), is kept.
def display(name):
    tail = re.split(r"\s+-\s+", name, maxsplit=1)
    if len(tail) == 2 and (tail[1][:1].islower() or "," in tail[1]
                           or re.search(r"\bno\b|only|hardcoded", tail[1], re.I)):
        name = tail[0]
    name = name.strip()
    def drop(m):
        inner = m.group(1)
        if len(inner) > 14 or "," in inner or re.search(r"\bno\b|only|hardcoded", inner, re.I):
            return ""
        return m.group(0)
    name = re.sub(r"\s*\(([^)]*)\)", drop, name).strip()
    return re.sub(r"\s{2,}", " ", name).strip(" ,-")


def build():
    seen = {}

    def add(name, code):
        key = display(name).strip()
        if key and key.lower() not in seen:
            seen[key.lower()] = (key, code)

    for n in CAT["wheels"]:
        add(n, "wn" if n.lower().startswith(NATIVE_WHEEL) else "wh")
    for n in PEDALS:
        add(n, "pd")
    for n in CAT["sticks"]:
        add(n, "fs")
    for n in CAT["throttles"]:
        add(n, "th")
    for n in CAT["arcade"]:
        add(n, "ar")
    for n in CAT["gamecube"]:
        add(n, "gc")
    for n in SPECIALTY:
        add(n, "sp")
    for f in FAM_ORDER:
        for n in sorted(fam.get(f, ())):
            add(n, FAM_CODE.get(f, "mp"))
    for n in sorted(mapped):
        add(n, "mp")

    out = []
    for name, code in sorted(seen.values(), key=lambda t: t[0].lower()):
        extra = " ".join(x for x in (CAT_TITLE.get(code, ""), aliases_for(name)) if x)
        out.append((name, code, extra))
    return out


CAT_TITLE = {c: t for c, t, _ in CATS}


# ── the matcher, Python side ────────────────────────────────────────────────
def norm(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def search(rows, q, limit=14):
    nq = norm(q)
    if len(nq) < 2:
        return []
    toks = nq.split()
    hits = []
    for name, code, extra in rows:
        hay = " " + norm(name + " " + extra) + " "
        if not all(t in hay for t in toks):
            continue
        if norm(name) == nq:
            rank = 0
        elif hay.startswith(" " + nq):
            rank = 1
        elif (" " + nq) in hay:
            rank = 2
        elif all((" " + t) in hay for t in toks):
            rank = 3
        else:
            rank = 4
        hits.append((rank, len(name), name, code))
    hits.sort(key=lambda h: (h[0], h[1], h[2].lower()))
    return [(n, c) for _, _, n, c in hits[:limit]]


if __name__ == "__main__":
    rows = build()
    print("device rows:", len(rows), file=sys.stderr)

    if "--test" in sys.argv:
        for q in ["g29", "dualsense", "moza r9", "warthog", "8bitdo ultimate",
                  "t300", "hori", "vkb", "spacemouse", "xbox elite", "switch pro",
                  "qanba", "simucube 2", "yawman", "wiimote", "pulse 3d",
                  "asdfghjkl", "x"]:
            r = search(rows, q)
            print("\n%-18s -> %d" % (q, len(r)))
            for n, c in r[:5]:
                print("      %-46s [%s]" % (n, c))
        sys.exit(0)

    cats = {c: {"t": t, "d": d} for c, t, d in CATS}
    js = []
    js.append("/* Generated. Source of truth is the SDL fork's own device tables;\n"
              "   regenerate with tools/emit_search.py rather than editing by hand. */\n")
    js.append("window.PF_CATS = " + json.dumps(cats, ensure_ascii=False, separators=(",", ":")) + ";\n")
    js.append("window.PF_DEVICES = " + json.dumps([[n, c, e] for n, c, e in rows],
                                                  ensure_ascii=False, separators=(",", ":")) + ";\n")
    out = os.path.join(SITE, "assets", "device-search.js")
    io.open(out, "w", encoding="utf-8", newline="\n").write("".join(js))
    print("wrote", out, "(%d rows)" % len(rows), file=sys.stderr)
