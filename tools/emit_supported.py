"""Generate the complete supported-device inventory for padforge.org.

Sources, all read at run time so a rebase regenerates rather than rots:
  controller_list.h   every pad SDL knows by USB identity, with its family
  SDL_gamepad_db.h    every pad with a shipped mapping, by name
  SDL_joystick.c      the wheel, flight stick, throttle, arcade and
                      GameCube adapter tables

Writes:
  wiki/devices/supported.md   the docs compatibility page
  _specs_block.html           the specs.html Devices section, for splicing
"""
import io, re, collections

SDL = r"C:\Users\sonic\OneDrive\Documents\GitHub\SDL3-build\SDL\src\joystick"
SITE = r"C:\Users\sonic\OneDrive\Documents\GitHub\padforge.org"

read = lambda p: io.open(p, encoding="utf-8", errors="replace").read()
CL = read(SDL + r"\controller_list.h")
DB = read(SDL + r"\SDL_gamepad_db.h")
JS = read(SDL + r"\SDL_joystick.c")


# SDL annotates entries in the name itself: platform notes like "(Linux)",
# catalogue notes like "(unlisted)", and whole trailing clauses of commentary.
# Those read as commentary rather than as a product name, so they are trimmed
# for display. A short parenthetical that disambiguates a real variant, like
# Joy-Con (L) or T300RS (PS4 mode), is kept.
DROP_PAREN = re.compile(r"^(linux|mac|macos|osx|windows|unlisted|unconfirmed|untested|"
                        r"wired|wireless \(.*|old|new|v\d+ firmware)$", re.I)


# SDL's comments double as a developer scratchpad. Alongside product names they
# carry URLs, "XXX:" notes, enumeration caveats and placeholders. Those are not
# device names and must not reach a page that claims to list device names.
NOTE_LEAD = re.compile(
    r"\s+(?:--|-)\s*(?:XXX|TODO|FIXME|NOTE)\b.*$|"      # marker notes
    r"\s*\bXXX\s*:.*$|"                                  # XXX: inline
    r"\s+(?:Over\s+BT|On\s+windows|Works\s+otherwise)\b.*$|"
    r"\s+(?:requires|shows\s+up\s+as|this\s+may|maybe)\b.*$",
    re.I)
JUNK = re.compile(r"^\s*$|^unknown\b|\bunknown controller\b|^actually\b", re.I)


def display(name):
    # A URL is a reference, never a product name.
    name = re.sub(r"https?://\S+|\bwww\.\S+", "", name)
    # A double dash always introduces commentary in this file.
    name = re.split(r"\s+--\s+", name, maxsplit=1)[0]
    name = NOTE_LEAD.sub("", name)
    # A single dash introduces commentary when what follows reads like prose.
    tail = re.split(r"\s+-\s+", name, maxsplit=1)
    if len(tail) == 2 and (tail[1][:1].islower() or "," in tail[1]
                           or re.search(r"\bno\b|only|hardcoded|requires|doesn", tail[1], re.I)):
        name = tail[0]

    def drop(m):
        inner = m.group(1).strip()
        if DROP_PAREN.match(inner):
            return ""
        if len(inner) > 14 or "," in inner or re.search(r"\bno\b|only|hardcoded", inner, re.I):
            return ""
        return m.group(0)

    name = re.sub(r"\s*\(([^)]*)\)", drop, name)
    name = re.sub(r"\s{2,}", " ", name).strip(" ,-/")
    return "" if JUNK.search(name) else name



# A few comments name two products in one breath. Split those, so each lands as
# its own row rather than as one 157-character entry.
def expand(name):
    out = []
    for part in name.split(" and the "):
        # Two products only when the vendor is repeated on both sides, as in
        # "PowerA Wired Controller Plus/PowerA Wired Controller GameCube Style".
        # A bare alternation like "Victrix Pro FS PS4/PS5 (PS4 mode)" is ONE
        # label and splitting it produced a row called "PS5 (PS4 mode)".
        if "/" in part:
            left, _, right = (x.strip() for x in part.partition("/"))
            lw, rw = left.split(), right.split()
            if lw and rw and lw[0].lower() == rw[0].lower() and len(lw) > 1 and len(rw) > 1:
                out.extend([left, right])
                continue
        out.append(part.strip())
    return [x for x in out if x]


# ── controller_list.h: identity + family + label ────────────────────────────
FAMILY = {
    "XBox360Controller": "Xbox 360",
    "XBoxOneController": "Xbox One and Series",
    "XBoxEliteController": "Xbox One and Series",
    "PS3Controller": "PlayStation 3",
    "PS4Controller": "PlayStation 4",
    "XInputPS4Controller": "PlayStation 4",
    "PS5Controller": "PlayStation 5",
    "PS5EdgeController": "PlayStation 5",
    "SwitchProController": "Nintendo Switch",
    "SwitchInputOnlyController": "Nintendo Switch",
    "XInputSwitchController": "Nintendo Switch",
    "SwitchJoyConLeft": "Nintendo Switch",
    "SwitchJoyConRight": "Nintendo Switch",
    "SwitchJoyConPair": "Nintendo Switch",
    "Switch2ProController": "Nintendo Switch 2",
    "Switch2InputOnlyController": "Nintendo Switch 2",
    "SteamController": "Steam",
    "SteamControllerV2": "Steam",
    "SteamControllerNeptune": "Steam",
    "SteamControllerTriton": "Steam",
    "HoriSteamController": "Steam",
    "8BitDoController": "8BitDo",
    "MobileTouch": "Other",
    "UnknownNonSteamController": "Other",
}
fam = collections.defaultdict(set)
for line in CL.splitlines():
    if line.strip().startswith("//"):
        continue
    m = re.search(r'MAKE_CONTROLLER_ID\(\s*0x[0-9a-fA-F]+\s*,\s*0x[0-9a-fA-F]+\s*\)\s*,'
                  r'\s*k_eControllerType_(\w+)\s*,\s*(NULL|"([^"]*)")\s*\}\s*,?\s*(?://\s*(.*))?$', line)
    if not m:
        continue
    typ, _, name, comment = m.groups()
    label = (name or "").strip() or (comment or "").strip()
    label = re.sub(r"\s*\(.*?only.*?\)\s*$", "", label, flags=re.I).strip()
    for one in expand(display(label)):
        fam[FAMILY.get(typ, "Other")].add(one)

# ── SDL_gamepad_db.h: shipped mappings, by name ─────────────────────────────
mapped = set()
for line in DB.splitlines():
    m = re.match(r'\s*"([0-9a-fA-F]{32}),([^,]+),', line)
    if m:
        n = m.group(2).strip()
        for one in expand(display(n)):
            if one != "*":
                mapped.add(one)

# ── SDL_joystick.c category tables ──────────────────────────────────────────
def table(name):
    m = re.search(re.escape(name) + r"\[\]\s*=\s*\{(.*?)\n\};", JS, re.S)
    out = []
    for line in m.group(1).splitlines():
        mm = re.search(r"MAKE_VIDPID\([^)]*\)\s*,\s*//\s*(.+?)\s*$", line)
        if mm:
            out.append(mm.group(1))
    return out

def clean(n):
    n = re.sub(r"\s*\([^)]*\)", "", n).strip()
    n = re.sub(r"\s+(Wheelbase|Wheel Base)$", "", n).strip()
    n = re.sub(r",\s*Inc\.?", "", n).strip()
    n = re.sub(r"^DragonRise .*Wired Wheel.*$", "DragonRise Wired Wheel", n)
    return n

CAT = {k: sorted({clean(v) for v in table(t)}, key=str.lower) for k, t in [
    ("wheels", "initial_wheel_devices"),
    ("sticks", "initial_flightstick_devices"),
    ("throttles", "initial_throttle_devices"),
    ("arcade", "initial_arcadestick_devices"),
    ("gamecube", "initial_gamecube_devices"),
]}

def ids(t):
    m = re.search(re.escape(t) + r"\[\]\s*=\s*\{(.*?)\n\};", JS, re.S)
    return {(a.lower(), b.lower()) for a, b in re.findall(
        r"MAKE_VIDPID\(\s*(0x[0-9a-fA-F]+)\s*,\s*(0x[0-9a-fA-F]+)\s*\)", m.group(1))}

cl_ids = set(re.findall(r"MAKE_CONTROLLER_ID\(\s*(0x[0-9a-fA-F]+)\s*,\s*(0x[0-9a-fA-F]+)\s*\)", CL))
cl_ids = {(a.lower(), b.lower()) for a, b in cl_ids}
union = cl_ids | ids("initial_wheel_devices") | ids("initial_flightstick_devices") \
        | ids("initial_throttle_devices") | ids("initial_arcadestick_devices") \
        | ids("initial_gamecube_devices")

N = {
    "union": len(union),
    "pads": len(cl_ids),
    "wheels": len(ids("initial_wheel_devices")),
    "sticks": len(ids("initial_flightstick_devices")),
    "throttles": len(ids("initial_throttle_devices")),
    "arcade": len(ids("initial_arcadestick_devices")),
    "gamecube": len(ids("initial_gamecube_devices")),
    "mapped": len(mapped),
}

FAM_ORDER = ["Xbox 360", "Xbox One and Series", "PlayStation 3", "PlayStation 4",
             "PlayStation 5", "Nintendo Switch", "Nintendo Switch 2", "Steam",
             "8BitDo", "Other"]

def lines(names):
    return ", ".join(sorted(names, key=str.lower))

if __name__ == "__main__":
    import json
    print(json.dumps({"counts": N,
                      "families": {k: len(v) for k, v in fam.items()},
                      "cat": {k: len(v) for k, v in CAT.items()},
                      "mapped": len(mapped)}, indent=1))
