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

for f in feats: add(f["t"], f["d"])
for r in rails: add(r["eyebrow"], r["t"] + " " + r["d"])

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
   "bass shakers", "controller speaker audio", "audio through the controller speaker"]),
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
