# -*- coding: utf-8 -*-
"""Generate padforge.org/specs.html.

Every entry from the old landing page (29 spec cards + 30 chapter rail
cards) is emitted here by construction, so the marketing page can stay
bold and simple without a single capability going missing. This is the
Apple split: the product page sells, the specifications page proves.
"""
import io, json, html, os, re
from html import unescape

import os.path
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
feats = json.load(io.open(os.path.join(ROOT, "_features.json"), encoding="utf-8"))
rails = json.load(io.open(os.path.join(ROOT, "_rails.json"), encoding="utf-8"))

# One flat pool, de-duplicated on title, rails keeping their eyebrow as the
# term when it is more specific than the headline.
def norm(t):
    # Singular/plural and punctuation collapse, so "Multi-source mappings"
    # and "Multi-source mapping" cannot both ship as separate rows.
    k = re.sub(r'[^a-z0-9 ]', '', t.lower()).strip()
    return re.sub(r's', '', k)

pool = []
seen = {}
def add(title, desc):
    k = norm(title)
    if k in seen:
        # Keep the longer description; merge rather than drop, so no
        # sentence is lost to de-duplication.
        i = seen[k]
        if len(desc) > len(pool[i][1]):
            pool[i] = (pool[i][0], desc)
        return
    seen[k] = len(pool); pool.append((title, desc))

# The two sources describe the same capability under different names: a
# feature card says "Nintendo virtual controller" and a rail says "Nintendo
# output". add() keys on the title, so neither collides and BOTH shipped, and
# the specs page carried seven pairs of rows saying the same thing twice.
#
# MERGE maps a rail eyebrow onto the feature title it duplicates. The rail is
# then added under that title, so add() collapses the pair.
MERGE = {
    "Nintendo output": "Nintendo virtual controller",
    "Touchpad as more than a touchpad": "Touchpad outputs",
    "Bass shakers": "Bass shaker output",
    "Audio through the controller speaker": "Controller speaker audio",
    "Share controllers across your PCs": "Remote Link",
    "Wii controllers, paired in-app": "Wii controllers",
    "A MIDI keyboard as a controller": "MIDI input",
}

# Keeping the longer description drops the shorter one's unique sentences,
# which is a quiet content loss rather than a merge. Where the two sides each
# carry facts the other lacks, the union is written out here once and wins
# over both. A pair not listed here takes the longer of the two.
UNION = {
    # The rail's headline and its body both open with "a virtual Switch Pro
    # Controller", so the concatenation says it twice in one breath.
    "Nintendo virtual controller":
        "The Nintendo slot type creates a virtual Switch Pro Controller "
        "through HIDMaestro. Games and emulators that speak Switch see the "
        "real thing: the full button set, and gyro passed through from your "
        "physical pad.",
    "Touchpad outputs":
        "Map any touchpad, on a DualSense, a DS4, a laptop trackpad, a phone "
        "over the web, or the on-screen overlay, to mouse X/Y with per-axis "
        "sensitivity, invert, and a Trackpad pointer response that moves the "
        "cursor the way a laptop touchpad does. Anchor a virtual analog stick "
        "where your finger lands, or drop a wedge-thresholded D-pad on top. "
        "Pressure-sensitive pads expose per-finger pressure as sources, and "
        "swipe haptics tick the pad as a finger travels. Plus the gesture "
        "stack: 4-way and 8-way swipes, taps, longpress, pinch, rotate, two- "
        "to five-finger gestures, and custom shape templates. Every toggle "
        "saves per pad per slot.",
    "Remote Link":
        "Share a controller, wheel, or HOTAS with the other PadForge PCs on "
        "your network. One plugged into one PC drives a game on another, both "
        "directions at once, and the feedback comes home: rumble, force "
        "feedback, adaptive triggers, lightbar, player LEDs, and speaker "
        "audio all play on the physical device wherever it lives. Pair once "
        "with a six-digit code and trusted PCs reconnect on their own. A "
        "gamepad-only switch keeps a paired PC away from your keyboard, "
        "mouse, and macros. Works on your home network, and across the "
        "internet by swapping connection codes with no VPN needed.",
    "Wii controllers":
        "Pair a Wii Remote without leaving PadForge. Its PIN is six raw bytes "
        "set by the sync button, not text you can type into the Windows "
        "prompt, so PadForge runs the pairing itself: click Pair, press the "
        "red SYNC button, and the controller bonds and reconnects on any "
        "button press. Hold 1 and 2 instead for a temporary pairing. A bare "
        "Wii Remote, Remote plus Nunchuk, Classic Controller, and Wii U Pro "
        "Controller all map as normal pads, with the accelerometer and Motion "
        "Plus gyro feeding the same motion pipeline as a DualSense. The IR "
        "camera drives an on-screen pointer, and a Balance Board reports "
        "weight and lean as mapping sources.",
}

for f in feats: add(f["t"], f["d"])
for r in rails: add(MERGE.get(r["eyebrow"], r["eyebrow"]), r["t"] + " " + r["d"])

for i, (title, desc) in enumerate(pool):
    if title in UNION: pool[i] = (title, UNION[title])

CATS = [
 ("mapping", "Mapping and control", [
   "multi-source mappings", "multi-source mapping", "shift layers", "starter profiles",
   "socd cleaning", "stick-assisted triggers", "mouse gestures", "media keys as inputs",
   "macros with action sequences", "per-app profiles", "six deadzone shapes",
   "unknown hardware welcome"]),
 ("virtual", "Virtual controllers", [
   "nintendo virtual controller", "nintendo output", "virtual vr controllers",
   "midi virtual output", "hide physical controllers", "steam workshop config import"]),
 ("feel", "Feel and feedback", [
   "native wheel force feedback", "force feedback both ways", "impulse triggers",
   "trigger motors that feel the game", "adaptive triggers and lightbar",
   "dualsense effects in any game", "guide led brightness", "bass shaker output",
   "bass shakers", "controller speaker audio", "audio through the controller speaker",
   "headphone dsp chain"]),
 ("motion", "Motion", [
   "gyro at steam input parity", "flick stick", "headset head tracking",
   "dsu motion server", "motion to emulators", "wii pointer modes",
   "joy-con 2 optical mouse"]),
 ("touch", "Touch and pointer", [
   "touchpad outputs", "touchpad as more than a touchpad", "on-screen touchpad overlay",
   "mouse as a source", "3d and 2d visualization"]),
 ("connect", "Devices and connectivity", [
   "remote link", "share controllers across your pcs", "phone-as-controller",
   "midi input", "a midi keyboard as a controller", "midi from a gamepad",
   "nfc tag triggers", "wii controllers", "wii controllers, paired in-app",
   "dualshock 3, paired in-app", "battery and idle disconnect", "1000 hz polling"]),
]

used = set()
def take(keys):
    out = []
    for k in keys:
        for t, d in pool:
            if t.lower() == k and t.lower() not in used:
                used.add(t.lower()); out.append((t, d))
    return out

sections = [(cid, title, take(keys)) for cid, title, keys in CATS]
leftovers = [(t, d) for t, d in pool if t.lower() not in used]
if leftovers:
    sections.append(("more", "Also included", leftovers))

def esc(x): return html.escape(unescape(x), quote=False)

rows = []
for cid, title, items in sections:
    body = "\n".join(
        '                <div class="spec-row">\n'
        '                    <dt>%s</dt>\n'
        '                    <dd>%s</dd>\n'
        '                </div>' % (esc(t), esc(d)) for t, d in items)
    rows.append(
'''        <section class="spec-block" id="%s">
            <h2 class="display-s spec-h reveal">%s</h2>
            <dl class="spec-list reveal" data-d="1">
%s
            </dl>
        </section>''' % (cid, esc(title), body))

CMP = io.open(os.path.join(ROOT, "_cmp_full.html"), encoding="utf-8").read().strip()
CMP_SECTION = (
'        <section class="spec-block" id="comparison">\n'
'            <h2 class="display-s spec-h reveal">Full comparison</h2>\n'
'            <p class="spec-note reveal">Every capability, against the tools people '
'usually reach for. The product page carries a shortened version of this table.</p>\n'
'            <div class="cmp-wrap reveal" data-d="1">\n'
'                <div class="cmp-scroll">\n'
'                    ' + CMP + '\n'
'                </div>\n'
'            </div>\n'
'        </section>')
rows.append(CMP_SECTION)

# The complete FAQ, verbatim from the previous page. The product page keeps
# a short set for the common questions; every answer survives here in full,
# which is the whole point of the split.
faq = json.load(io.open(os.path.join(ROOT, "_faq.json"), encoding="utf-8"))
faq = [f for f in faq if f["q"].lower() != "feature by feature"]   # table wrapper, not a question
faq_rows = "\n".join(
    '                <details class="detail">\n'
    '                    <summary>%s</summary>\n'
    '                    <div class="detail-body">%s</div>\n'
    '                </details>' % (esc(f["q"]), esc(f["a"])) for f in faq)
rows.append(
'        <section class="spec-block" id="faq">\n'
'            <h2 class="display-s spec-h reveal">Questions, answered in full</h2>\n'
'            <div class="details reveal" data-d="1">\n'
+ faq_rows + '\n'
'            </div>\n'
'        </section>')

nav_links = "\n".join(
    '                <a href="#%s">%s</a>' % (cid, esc(title)) for cid, title, _ in sections)
nav_links += '\n                <a href="#comparison">Full comparison</a>'
nav_links += '\n                <a href="#faq">Questions</a>'

page = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PadForge specifications: every capability, in full</title>
    <meta name="description" content="The complete PadForge capability list: mapping, virtual controllers, force feedback, motion, touch, connectivity, and platform details.">
    <link rel="icon" type="image/png" href="assets/icon.png">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700;800;900&family=Instrument+Sans:ital,wght@0,400;0,500;0,600;1,400&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="style.css?v=v6">
    <script>document.documentElement.classList.add('js');</script>
</head>
<body>

<nav class="nav" id="nav">
    <div class="container-wide nav-in">
        <a class="nav-brand" href="index.html"><img src="assets/icon.png" alt="" width="27" height="27">PadForge</a>
        <div class="nav-links">
            <a href="index.html#controller">The controller</a>
            <a href="index.html#remap">Remap</a>
            <a href="index.html#compare">Compare</a>
            <a href="specs.html">Specifications</a>
            <a href="/docs/">Docs</a>
        </div>
        <a href="https://github.com/hifihedgehog/PadForge/releases/latest" class="btn btn-primary btn-sm" target="_blank" rel="noopener">Download</a>
    </div>
</nav>

<header class="spec-hero">
    <div class="container">
        <p class="kicker reveal">Specifications</p>
        <h1 class="display-l reveal" data-d="1">Everything, in full.</h1>
        <p class="lede reveal" data-d="2">
            The complete capability list. The <a href="index.html">product page</a> shows
            what PadForge feels like; this page proves what it does. Each entry is
            covered at length in the <a href="/docs/">documentation</a>.
        </p>
    </div>
</header>

<div class="container spec-wrap">
    <aside class="spec-nav">
        <div class="spec-nav-in">
            <p class="mono-tag">Contents</p>
%s
        </div>
    </aside>
    <main class="spec-main">
%s
    </main>
</div>

<footer class="footer">
    <div class="container">
        <div class="footer-grid">
            <a class="footer-brand" href="index.html"><img src="assets/icon.png" alt="" width="26" height="26">PadForge</a>
            <div class="footer-links">
                <a href="index.html">Overview</a>
                <a href="specs.html">Specifications</a>
                <a href="/docs/">Docs</a>
                <a href="https://github.com/hifihedgehog/PadForge" target="_blank" rel="noopener">GitHub</a>
            </div>
        </div>
        <div class="footer-note">
            <span>Licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" target="_blank" rel="noopener" style="color:var(--text-muted)">CC BY-NC-SA 4.0</a></span>
            <span>Powered by HIDMaestro</span>
        </div>
    </div>
</footer>

<script>
(function () {
    "use strict";
    var io = new IntersectionObserver(function (es) {
        es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); } });
    }, { rootMargin: "0px 0px -8%% 0px", threshold: 0.04 });
    document.querySelectorAll(".reveal").forEach(function (el) { io.observe(el); });

    var nav = document.getElementById("nav");
    addEventListener("scroll", function () { nav.classList.toggle("stuck", scrollY > 40); }, { passive: true });

    /* Mark the section currently in view in the contents rail. */
    var links = [].slice.call(document.querySelectorAll(".spec-nav a"));
    var blocks = links.map(function (a) { return document.getElementById(a.getAttribute("href").slice(1)); });
    new IntersectionObserver(function (es) {
        es.forEach(function (e) {
            if (!e.isIntersecting) return;
            var i = blocks.indexOf(e.target);
            links.forEach(function (l, n) { l.classList.toggle("on", n === i); });
        });
    }, { rootMargin: "-20%% 0px -70%% 0px" }).observe ? blocks.forEach(function (b) {
        new IntersectionObserver(function (es) {
            es.forEach(function (e) {
                if (!e.isIntersecting) return;
                var i = blocks.indexOf(e.target);
                links.forEach(function (l, n) { l.classList.toggle("on", n === i); });
            });
        }, { rootMargin: "-20%% 0px -70%% 0px" }).observe(b);
    }) : null;
})();
</script>
</body>
</html>
''' % (nav_links, "\n\n".join(rows))

io.open(os.path.join(ROOT, "specs.html"), "w", encoding="utf-8", newline="\n").write(page)
total = sum(len(i) for _, _, i in sections)
print("specs.html written: %d entries across %d sections" % (total, len(sections)))
for cid, title, items in sections:
    print("  %-26s %d" % (title, len(items)))

# The page shipped seven pairs of rows saying the same thing twice, because
# the two source files title one capability two ways and add() keys on the
# title. MERGE fixes the pairs that exist; this refuses to ship new ones.
# Word-overlap rather than exact text, because the duplicates were never
# identical, only redundant.
import itertools as _it
def _words(s):
    return set(re.findall(r"[a-z0-9]{4,}", re.sub(r"<[^>]+>", " ", s).lower()))
_dupes = []
for (_t1, _d1), (_t2, _d2) in _it.combinations(pool, 2):
    _w1, _w2 = _words(_d1), _words(_d2)
    if not _w1 or not _w2:
        continue
    _j = len(_w1 & _w2) / len(_w1 | _w2)
    if _j > 0.32:
        _dupes.append((_j, _t1, _t2))
if _dupes:
    print()
    print("REFUSING TO SHIP: %d row pair(s) say the same thing twice." % len(_dupes))
    for _j, _a, _b in sorted(_dupes, reverse=True):
        print("   %.2f overlap: %r and %r" % (_j, _a, _b))
    print()
    print("Add the rail's eyebrow to MERGE so the pair collapses onto one")
    print("title, and give it a UNION entry when each side carries a fact the")
    print("other lacks. Raising the threshold is not the fix.")
    raise SystemExit(1)
