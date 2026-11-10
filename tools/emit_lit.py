"""The keyboards, mice, headsets and other lit devices PadForge lights directly, by USB identity.

Source: tools/data/lit-devices.tsv, one row per identity (vendor, product, name, source), which
PadForge's PluginInventoryTests.WriteTheLitDevices writes from the lighting families' own tables.
Regenerate it at each release from the PadForge repo:

    set PADFORGE_LIGHTING_DEVICES_TSV=<this repo>\\tools\\data\\lit-devices.tsv
    dotnet test PadForge.Tests -c Release --filter FullyQualifiedName~WriteTheLitDevices

A few SignalRGB plugins carry one title for many models ("Logitech Modern Device"), so the model
name comes from the plugin's own product table in the plugin clones beside this repo, read at run
time. RENAME fixes names that are a file or class name rather than a product's.
"""
import collections, io, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
GITHUB = os.path.dirname(os.path.dirname(HERE))
TSV = os.path.join(HERE, "data", "lit-devices.tsv")
PLUGIN_ROOTS = [os.path.join(GITHUB, "signal-plugins-beta", "Plugins"), os.path.join(GITHUB, "signal-plugins", "Plugins")]

# Plugin titles that cover many models, with the vendor the model name takes.
GENERIC = {
    "Logitech Modern Device": "Logitech",
    "Logitech Headset Controller": "Logitech",
    "Razer Modern Mouse": "Razer",
    "Razer Modern Keyboard": "Razer",
    "Razer Kraken Headset Controller": "Razer",
    "Razer Nari Headset Controller": "Razer",
    "Corsair Bragi Device": "Corsair",
}

# Names that are a file, a class or a code rather than a product's name.
RENAME = {
    "massdrop_alt_default": "Massdrop ALT",
    "CNVS": "HYTE CNVS",
    "AcerNitroHidKeyboardController": "Acer Nitro keyboard",
    "MK25047": "Yunzii MK25047",
    "AL68_Keyboard": "Yunzii AL68",
    "P SABRE L": "Corsair Sabre RGB Laser",
    "P KATAR": "Corsair Katar",
    "P K63 NRGB": "Corsair K63",
    "Launch Configurable Keyboard (launch_1)": "System76 Launch",
    "Monsgeek M1_V5 ISO": "MonsGeek M1 V5 ISO",
    "Monsgeek M1_V5 ANSI": "MonsGeek M1 V5 ANSI",
    "Monsgeek M1_V3": "MonsGeek M1 V3",
    "an_achronism tetromino QMK Keyboard": "anachronism Tetromino QMK Keyboard",
    "Unknown Tan67 QMK Keyboard": "Tan67 QMK Keyboard",
    "Laptop 16 RGB Macropad": "Framework Laptop 16 RGB Macropad",
    "ite 8291": "ITE 8291 laptop keyboard",
    "ite8291r3 ctl": "ITE 8291 rev 3 laptop keyboard",
    "glorious model o eternal": "Glorious Model O Eternal",
    "logitech g9": "Logitech G9",
    "logitech g9x Original": "Logitech G9x Original",
    "roccat kone emp": "ROCCAT Kone EMP",
    "redragon k667 QMK Keyboard": "Redragon K667 QMK Keyboard",
    "kbdfans Kbdpadmk3 QMK Keyboard": "KBDfans KBDPad MKIII QMK Keyboard",
    "sinowealth 0027": "Sinowealth mouse 0027",
    "sinowealth 0051": "Sinowealth mouse 0051",
    "MadCatz Cyborg Gaming Light": "Mad Catz Cyborg Gaming Light",
    "CoolerMaster SK622 Keyboard": "Cooler Master SK622 Keyboard",
    "CoolerMaster SK650 Keyboard": "Cooler Master SK650 Keyboard",
    "DesignedbyGG Ironclad V3 ISO QMK+VIA": "Designed by GG Ironclad V3 ISO QMK+VIA",
}

# Vendors whose name is two words, or that names spell more than one way, for the page's
# vendor rows. Matched on the start of a name, case ignored, longest first.
VENDORS = ["Cooler Master", "Das Keyboard", "Royal Kludge", "Red Square", "Lian Li", "Raspberry Pi",
           "Work Louder", "Rama Works", "Controller Works", "Mars Gaming", "Attack Shark", "Dark Project",
           "Magic Force", "Laser Ninja", "Synth Labs", "Alpaca Keyboards", "Designed by GG", "Dream Cheeky",
           "Mad Catz", "Turtle Beach", "BY Tech", "Anne Pro", "Sound BlasterX", "ASUS", "KBDfans", "MonsGeek",
           "KBDCraft", "Thermaltake", "Yunzii", "Logitech", "Glorious", "Redragon", "ROCCAT", "Sinowealth",
           "SteelSeries", "HyperX", "Razer", "Corsair", "Keychron", "Lenovo", "Wooting", "Cherry"]
VENDOR_OF = {"Sound BlasterX": "Creative", "Anne Pro": "Obinslab"}


def vendor(name):
    low = name.lower()
    for v in sorted(VENDORS, key=len, reverse=True):
        if low.startswith(v.lower() + " ") or low == v.lower():
            return VENDOR_OF.get(v, v)
    return name.split()[0]

# Identities whose plugin table names no model: Logitech's wireless receivers, which light the
# mouse or keyboard paired to them, and the POWERPLAY mat, which the Modern Device plugin special-cases.
BY_ID = {(0x046D, 0xC53A): "Logitech POWERPLAY"}
BY_ID.update({(0x046D, p): "Logitech wireless receiver" for p in (0xC539, 0xC541, 0xC543, 0xC545, 0xC547, 0xC548, 0xC54D)})

# A plugin's product table: "c081" : "G900", 0x006B: "Abyssus Essential", or 0x0A5C: { name: "G633".
_MODEL = re.compile(r'(?:"([0-9a-fA-F]{4})"|0x([0-9a-fA-F]{4}))\s*:\s*"([^"]+)"')
_MODEL_OBJ = re.compile(r'0x([0-9a-fA-F]{4})\s*:\s*\{\s*(?://[^\n]*\s*)?name\s*:\s*"([^"]+)"')
_tables = {}


def _plugin_models(rel):
    """The product table of one plugin, product id to model name, or {} with no clone."""
    if rel not in _tables:
        models = {}
        for root in PLUGIN_ROOTS:
            path = os.path.join(root, rel.replace("/", os.sep))
            if os.path.isfile(path):
                text = io.open(path, encoding="utf-8", errors="replace").read()
                for a, b, name in _MODEL.findall(text):
                    models.setdefault(int(a or b, 16), name.strip())
                for a, name in _MODEL_OBJ.findall(text):
                    models.setdefault(int(a, 16), name.strip())
                break
        _tables[rel] = models
    return _tables[rel]


def _clean(vid, pid, name, source):
    if (vid, pid) in BY_ID:
        return BY_ID[(vid, pid)]
    if name in GENERIC:
        model = _plugin_models(source).get(pid)
        if model:
            vendor = GENERIC[name]
            name = model if model.lower().startswith(vendor.lower()) else vendor + " " + model
    name = RENAME.get(name, name)
    # SignalRGB's Keychron plugins misspell the brand in five titles.
    name = re.sub(r"^Keychon\b", "Keychron", name)
    return re.sub(r"\s{2,}", " ", name.replace("_", " ")).strip()


def _read():
    lit = {}
    for line in io.open(TSV, encoding="utf-8"):
        cells = line.rstrip("\r\n").split("\t")
        if len(cells) < 4:
            continue
        vid, pid = int(cells[0], 16), int(cells[1], 16)
        lit.setdefault((vid, pid), _clean(vid, pid, cells[2], cells[3]))
    return lit


LIT = _read()
# Case first, then the name itself, so two names that differ only in case keep one order
# from run to run (a set's order changes with Python's hash seed).
LIT_NAMES = sorted(set(LIT.values()), key=lambda s: (s.lower(), s))

if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    print("identities", len(LIT), "names", len(LIT_NAMES))
    left = [n for n in LIT_NAMES if n in GENERIC]
    print("generic titles left:", collections.Counter(n for n in LIT.values() if n in GENERIC))
