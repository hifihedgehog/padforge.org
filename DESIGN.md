# padforge.org design guide

The bar is Apple and ASUS ROG. Not "better than the last version": those
two, measured directly. reWASD is the footprint to outmaneuver, never to
copy. Dalit Designs is a reference for craft, ranked below the first two.

This guide exists so future edits extend the system instead of eroding
it. The previous site died by a thousand additions, each individually
reasonable: another card, another paragraph, another grid. Read this
before adding anything.

---

## 1. The one rule

**Show the product. Say less. Prove it elsewhere.**

Every decision below follows from that. When a change is proposed, ask in
order:

1. Does it make the product more visible, or less?
2. Can it be shown instead of described?
3. If it is detail, does it belong on `specs.html` rather than here?

A "yes, but it's only a small paragraph" is how the last site got to
6,656 words on a landing page.

---

## 2. The two-surface split

| Surface | Job | Voice | Density |
|---|---|---|---|
| `index.html` | Sell. Make someone want it. | Short, confident, concrete. | Sparse. One idea per viewport. |
| `specs.html` | Prove. Answer everything. | Plain, complete, unhurried. | Dense, but structured. |
| `/docs/` | Teach. How to actually do it. | Instructional. | Whatever the topic needs. |

This is Apple's own split (product page → tech specs) and it is the
release valve that keeps the product page clean. **When new detail
arrives, it goes to `specs.html` by default.** It only earns a place on
the product page if it changes what the product *is*.

`specs.html` is generated. Do not hand-edit it. See section 9.

---

## 3. Type

Display face is Archivo, body is Instrument Sans, mono is JetBrains Mono.

The scale is deliberately extreme. What separates display type from
scaled-up body type is optical correction, and both directions are
already encoded in the classes:

| Class | Size | Tracking | Leading | Use |
|---|---|---|---|---|
| `.display-xl` | 3.2 → 9rem | -0.038em | 0.92 | Hero only. Once per page. |
| `.display-l` | 2.6 → 6rem | -0.032em | 0.96 | Section headline. |
| `.display-m` | 2 → 3.6rem | -0.026em | 1.03 | Moment headline inside a section. |
| `.display-s` | 1.5 → 2.1rem | -0.018em | 1.15 | Spec block heading. |
| `.lede` | 1.1 → 1.45rem | n/a | 1.5 | The **one** paragraph under a headline. |

Rules:

- **Tracking tightens as size grows. Leading compresses as size grows.**
  If you add a size, follow the curve.
- `.lede` is capped at `46ch` and is meant to be the only body paragraph
  in a section. If you need a second, you need `specs.html` or a
  `<details>`.
- Never set a headline in body face, and never set body copy in Archivo.
- `.kicker` is mono, uppercase, 0.24em tracking. One per section, above
  the headline. It names the section. It is not a sentence.

---

## 4. Color

Defined once in `:root`. Do not introduce new colors in a section.

- **Canvas**: `--bg #06080c`, alternating with `--bg-alt #0d1117`. The
  alternation is what separates sections. Borders are a last resort.
- **Ember** `--ember #f2652a` is the single accent. It marks one thing at
  a time: the primary button, the active state, a kicker, one word in a
  headline. If two ember things compete in a viewport, one is wrong.
- **Telemetry cyan** `--telemetry` is for technical labels only (spec
  eyebrow text, the diagram's kicker). Never for a call to action.
- Text runs `--text-hi` → `--text` → `--text-muted` → `--text-dim`. Use
  the dimmest one that still reads.
- **Color in a product shot comes from the product**, never from a
  filter or an overlay.

## 5. Light and depth

The look is dark, but never flat. Three devices, already in the CSS:

1. **Radial bloom behind a product** (`.stage::before`,
   `.diagram::before`). A soft ember or cyan radial, blurred 30-50px,
   sitting behind the subject. This is what makes a machine feel lit
   rather than pasted onto the page.
2. **Contact shadow plus a long floor throw**, two shadows on the rig.
   Long, soft, and low-opacity.
3. **Hairlines**, `--hairline` at 7% white, for structure. A full
   `--border` is heavier and is for panels that must read as objects.

Never use a flat fill where a gradient reads as light, and never use a
hard drop shadow.

---

## 6. Rhythm and composition

**The failure mode this replaced: five identical chapters in a row.**
Kicker, headline, one screenshot, three columns of gray text, repeat. It
made a rich product read as a spec dump.

The rule now: **no two consecutive sections share a shape.** The current
order alternates deliberately:

1. Hero: centered headline, one large staged program screen
2. Manifest: sticky copy left, a long accent-barred capability list right
3. Chapter band: one word, full bleed, poster scale
4. Finishes: centered, the program screen morphing its finish
5. The controller: asymmetric two-column, copy left / diagram right
6. Stats: four-up typographic band
7. Remap: split, copy left / media bleeding off the right edge
8. Feel: centered headline, full-bleed media
9. Motion: split, **flipped** (media bleeding off the left)
10. Anywhere: centered, full-bleed media
11. Compare: table
12. Gallery: grid
13. Download: centered
14. FAQ: list

Chapter bands (`.chapter`) separate the acts: MAP, FEEL, MOVE, REACH.
One word at poster scale on a saturated full-bleed band, alternating
ember, cyan and steel. They are the reason a long scroll reads as
chapters rather than an unbroken list, and they are the one place a
saturated field of accent color is correct.

If you add a section, look at its neighbors and pick a shape neither of
them uses.

Vertical rhythm comes from `--pad-section` (6-13rem). Do not reduce it to
fit more in. Whitespace is the luxury signal. Crowding is the tell.

**Nothing may be absolutely positioned against the hero's bottom edge.**
The hero carries `min-height: 100svh`, but its content (headline, lede,
buttons, a full-width staged screen, the trust strip) is much taller than that on
every real viewport, so the hero's bottom is nowhere near the fold. A
"Scroll" cue pinned there did not sit at the fold where it would have
meant something. It landed on top of the trust strip and printed as
ghosted, overlapping text that reads exactly like a font bug. The cue is
gone, and the rule stands: the hero overflows the fold on purpose, which
is itself the invitation to scroll.

---

## 7. Imagery

This is where the biggest win came from, and it is the easiest thing to
regress.

**The rig** is how every app screen is presented. PadForge's product is
the application, so the application gets photographed like hardware:
the WHOLE window, staged on a lit surface, turned slightly toward the
reader.

The rig is `.rig` / `.rig-in` in `style.css`, and it is made of five
things, none of which are optional. Drop one and it stops reading as an
object:

1. **Perspective, not a flat rectangle.** `rotateY(-13deg) rotateX(5deg)`
   on a 2400px perspective. `.rig-r` mirrors it, `.rig-soft` halves it.
   Under 900px the angle stands down and the screen goes flat, because
   the angle is a presentation device and never a legibility tax.
2. **A rim light.** `0 0 0 1px rgba(255,255,255,0.10)` plus a brighter
   inset top edge. PadForge's UI is nearly the same value as the page,
   so without a rim the window dissolves into the canvas.
3. **A contact shadow and a long floor throw.** Two shadows, not one.
4. **A glass sheen**, a shallow diagonal highlight across the panel.
5. **A bloom behind it** (`.stage`), ember by default and `.stage-cy`
   for the cyan sections.

**Never crop the app down to one panel.** The version this replaced
lifted the 3D controller preview out of the window, blurred a backdrop
in behind it, and shipped that as the product shot. The owner's verdict
was "hamfisted with blurred features, it looks like trash", and it was
right: cropping to one control throws away the product in order to
feature a piece of it, and the blur announces that something was
removed. Show the whole program screen. If it is too small to read, the
layout is wrong, not the screenshot. Split moments bleed their media
column past the container edge for exactly this reason.

**Match the window's real curvature, and let it scale.** The captures are
taken at 200% display scale, which is measurable rather than assumed: a
1 DIP UI hairline is exactly 2px wide in the source. So the window is
1280 logical px across, and Windows 11's 8 DIP corner is 16px of a
2560px image, or 0.625% of the width. `.rig-in` therefore rounds at
`0.625cqw` with `container-type: inline-size` on `.rig`, which holds that
ratio at every displayed size. A fixed pixel radius cannot: the old 14px
was too round everywhere and grotesquely too round on the gallery tiles,
which display the same window at half the size. Verified by rendering the
same shot at 1280px and 640px and measuring the rendered arc: 8px and
4px.

Note the captures themselves have SQUARE corners, because the harness
grabs the window rect and the trim removes the invisible resize border.
The curvature is ours to draw, which is exactly why it has to be right.

**Trim the capture margin before staging anything.** The harness bakes an
11px pure-black margin around each window on the left, right and top. It
is invisible on a dark page right up until the screen is staged as an
object: the rig rounds its own box and draws a rim light on it, so with
the margin present that rim traces the edge of the BLACK BORDER rather
than the edge of the window, and you get a rounded frame with a square
window floating 11px inside it. `tools/trim_shots.py` measures and crops
it, is idempotent, and must be run after every capture pass.

**A capture must contain one window and nothing else.** The two browser
shots included a strip of the PadForge window sitting behind them, which
is invisible in a flat thumbnail and reads as a second window bleeding
out of the first once staged. Crop a desktop capture to its own window
border before it goes near a rig.

**A machine is never cut to buy size.** An earlier version let the split
moments bleed past the viewport edge to win pixels, which sliced the
right third off the window and threw away the exact thing the staging
exists to show. Size comes from a wider column and a wider container,
and detail comes from click-to-zoom. Nothing on the page may clip a
window.

**Chips** (`.rig-chip`) pin a short line onto a staged screen. They must
sit over dead space, never over the UI they describe, and they must say
something the screenshot cannot say on its own. A chip that repeats a
number already legible in the screenshot is noise on the product: the
hero originally had three, all repeating the dashboard's own readouts,
and removing them made it stronger.

**Rotated planes project wider than their layout box.** Every stage that
holds a rig needs bounded width with real margin, or the near edge runs
off the viewport. This has been fixed twice: once on the hero, once on
the finishes section.

**The schematic plate** (`assets/render/dualsense-plate-dark.png`):
generated from the app's light-mode 2D overlay art by inverting luminance
onto a steel ramp. It belongs to the dark canvas. The raw white art does
not, and dropping the white plate onto the page punches a hole in it.

**App screenshots**: every one is **clickable** (`.zoom` plus the
lightbox), which is what resolves the old tension between showing a
screenshot large enough to read and keeping the page calm. Show it at a
comfortable size, let the reader open it for detail.

Cropping rules:

- A crop takes the **full width of the content pane** (0.155 to 0.998) and
  only trims vertically. Cropping horizontally chops cards off at their
  right edge, which reads as broken.
- **If a tab has little content, do not crop it at all.** The Wheel tab
  is one small card in a large empty pane: any crop is either a letterbox
  strip or mostly emptiness, so it ships as the whole window.
- Detail crops live in `assets/detail/`.

Rule of thumb: **if a crop would cut through anything, widen it or ship
the whole window.**

---

## 8. The annotated controller

`#controller` is the centrepiece and the answer to "show, don't tell".

- Hotspot positions are **derived from the app's own generated overlay
  geometry** (`PadForge.App/Models2D/ControllerOverlayLayout.cs`, base
  1467×816). They are percentages of that base, so a ring sits exactly on
  the control it names. If the art changes, re-derive. Do not eyeball.
- **One callout is visible at a time.** That is what lets each label sit
  near its own control without colliding.
- Callouts point **inward**. A label that points outward escapes the
  diagram box and lands in the copy column.
- The label carries a blurred panel so it stays legible over the product
  as well as over the backdrop. Never rely on what happens to be behind.
- Below 780px the callouts stand down. The caption list already carries
  the same text.

---

## 9. Content rules

- **`specs.html` is generated** by `tools/build_specs.py` from
  `_features.json`, `_rails.json`, `_faq.json`, and `_cmp_full.html`.
  Edit the data or the generator, then re-run. Hand edits get overwritten.
- **Nothing is deleted to make room.** When the product page tightens,
  the text moves to `specs.html` or a `<details>`. The check that matters
  is the retention diff in section 11.
- **Progressive disclosure** (`.details` / `.detail`) is the tool for
  keeping depth on the product page without paying for it visually.
- No inventory labels in UI copy. A toggle says what it opens, never how
  many rows it holds.
- House prose rules apply: no em-dash pseudo-colons, no stray semicolons,
  no rule-of-three padding, no "not just X but Y", American English.
- **Claims are the owner's to confirm.** Example already corrected: most
  games *do* need HidHide, and saying otherwise reads as advice to skip a
  driver most people want.

---

## 10. Motion

- Easing is `cubic-bezier(0.16, 1, 0.3, 1)` at ~0.9s. Slow and eased
  reads expensive. Fast reads cheap.
- **Nothing that contains an image may move on hover or click.** Lifting
  a screenshot on hover, or zooming a product render on selection, reads
  as the page twitching. Hover changes color, border, or brightness.
  Selection cross-fades opacity only. Small chips (swatches) may scale
  slightly; images never do.
- Reveal-on-scroll is staggered with `data-d="1..5"` (90ms steps).
- **`.reveal` is gated on `.js`.** Content is visible by default and JS
  opts into animating it. The opposite order ships a blank page the one
  time a script fails. Never invert this.
- `prefers-reduced-motion` is honored. Keep it that way.
- Auto-advancing components (colourway morph, diagram tour) pause when
  off-screen and stop on interaction.

---

## 11. Before you ship

1. **Look at it.** Render and open the image. A capture harness proves
   nothing on its own.
   ```
   msedge --headless=new --disable-gpu --hide-scrollbars \
          --window-size=1512,13000 --virtual-time-budget=6000 \
          --screenshot=out.png file:///.../\_capture.html
   ```
   Use `_capture.html` (`tools/make_capture.py`), because a `100svh`
   hero fills a tall capture window and reads as an empty page. The
   harness neutralises the hero's `min-height`, forces the `.reveal`
   state, and freezes every transition, animation, and `will-change`, so
   a transition photographed mid-flight cannot masquerade as a layout
   bug. **The harness collapses the hero, so anything positioned against
   the hero's bottom edge moves under capture.** When a capture shows
   overlapping text, rule that out before blaming fonts: retag the
   suspect strings with sentinels (`QQQ+ WWWWWW XXXXXXXX`) and
   re-capture. The overlapping glyphs then spell out which element is
   actually on top, which is how the "Scroll" collision was found after
   font-swap, compositing, and device-scale theories had all been
   disproved.
2. **Check every asset resolves.** No broken `src`.
3. **Run the retention diff** if you removed or moved copy: extract the
   visible text of the previous commit and of the new `index.html` +
   `specs.html`, and compare word counts and distinctive terms. Loss must
   be deliberate and stated, never accidental.
4. **Check div balance** after any structural edit. An unbalanced tag
   silently nests a column inside its neighbor and the layout collapses
   to one column, which looks like a CSS bug and is not.
5. **Check it at 780px and 400px.** The callouts stand down, the diagram
   moves above the copy, the nav links collapse.

---

## 12. What not to do

Every item here has already happened once.

- Do not add a grid of text cards. That is what the rebuild removed.
- Do not put a full app window in a small figure.
- Do not use the light 2D plate art on a dark section.
- Do not let a second paragraph creep in under a `.lede`.
- Do not introduce a color, a font, or an easing curve that is not in
  `:root`.
- Do not hand-edit `specs.html`.
- Do not hide content behind JS by default.
- Do not repeat the previous section's shape.
- Do not move an image on hover or click.
- Do not crop a screenshot horizontally through its content.
- Do not crop the app down to one panel and blur the rest.
- Do not put a chip over the UI it is describing.
- Do not put a rig in a stage without bounded width.
- Do not stage an untrimmed screenshot.
- Do not round a window with a fixed pixel radius.
- Do not stage a capture with another window visible in it.
- Do not clip a window to make it bigger.
- Do not anchor anything to the hero's bottom edge.
