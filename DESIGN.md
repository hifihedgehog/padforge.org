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

## 4. Colour

Defined once in `:root`. Do not introduce new colours in a section.

- **Canvas**: `--bg #06080c`, alternating with `--bg-alt #0d1117`. The
  alternation is what separates sections. Borders are a last resort.
- **Ember** `--ember #f2652a` is the single accent. It marks one thing at
  a time: the primary button, the active state, a kicker, one word in a
  headline. If two ember things compete in a viewport, one is wrong.
- **Telemetry cyan** `--telemetry` is for technical labels only (spec
  eyebrow text, the diagram's kicker). Never for a call to action.
- Text runs `--text-hi` → `--text` → `--text-muted` → `--text-dim`. Use
  the dimmest one that still reads.
- **Colour in a product shot comes from the product**, never from a
  filter or an overlay.

## 5. Light and depth

The look is dark, but never flat. Three devices, already in the CSS:

1. **Radial bloom behind a product** (`.hero-stage::before`,
   `.morph-stage::before`, `.diagram::before`). A soft ember or cyan
   radial, blurred 46-52px, sitting behind the subject. This is what
   makes a controller feel lit rather than pasted.
2. **Contact shadow on the product** (`drop-shadow(0 44px 70px ...)`).
   Long, soft, and low-opacity.
3. **Hairlines**, `--hairline` at 7% white, for structure. A full
   `--border` is heavier and is for panels that must read as objects.

Never use a flat fill where a gradient reads as light, and never use a
hard drop shadow.

---

## 6. Rhythm and composition

**The failure mode this replaced: five identical chapters in a row.**
Kicker, headline, one screenshot, three columns of grey text, repeat. It
made a rich product read as a spec dump.

The rule now: **no two consecutive sections share a shape.** The current
order alternates deliberately:

1. Hero: centred, full-bleed product
2. Finishes: centred, product morph
3. The controller: asymmetric two-column, copy left / diagram right
4. Stats: four-up typographic band
5. Remap: split, copy left / media right
6. Feel: centred headline, full-bleed media
7. Motion: split, **flipped** (media left)
8. Anywhere: centred, full-bleed media
9. Compare: table
10. Gallery: grid
11. Download: centred
12. FAQ: list

If you add a section, look at its neighbours and pick a shape neither of
them uses.

Vertical rhythm comes from `--pad-section` (6-13rem). Do not reduce it to
fit more in. Whitespace is the luxury signal. Crowding is the tell.

---

## 7. Imagery

This is where the biggest win came from, and it is the easiest thing to
regress.

**Product renders** (`assets/render/pad-*.jpg`): the app's own 3D preview,
cropped free of the window chrome by
`tools/extract_renders.py`. These are the site's product photography and
they should be used **large**. The crop boundary is measured, not guessed:
the appearance picker ends at 0.178 of the source height and the
controller's shoulders begin at 0.180, so the crop starts at 0.1785.

**The schematic plate** (`assets/render/dualsense-plate-dark.png`):
generated from the app's light-mode 2D overlay art by inverting luminance
onto a steel ramp. It belongs to the dark canvas. The raw white art does
not, and dropping the white plate onto the page punches a hole in it.

**App screenshots**: crop to the region that carries the idea, at roughly
1.3:1, and let it fill its column. A full window shrunk into a figure is
unreadable, and an unreadable screenshot is decoration pretending to be
evidence. Detail crops live in `assets/detail/`.

Rule of thumb: **if you cannot read the screenshot at the size it ships
at, crop it or cut it.**

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
- Reveal-on-scroll is staggered with `data-d="1..5"` (90ms steps).
- **`.reveal` is gated on `.js`.** Content is visible by default and JS
  opts into animating it. The opposite order ships a blank page the one
  time a script fails. Never invert this.
- `prefers-reduced-motion` is honoured. Keep it that way.
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
   Use `_capture.html` (generated copy with `min-height` on the hero
   neutralised), because a `100svh` hero fills a tall capture window and
   reads as an empty page.
2. **Check every asset resolves.** No broken `src`.
3. **Run the retention diff** if you removed or moved copy: extract the
   visible text of the previous commit and of the new `index.html` +
   `specs.html`, and compare word counts and distinctive terms. Loss must
   be deliberate and stated, never accidental.
4. **Check div balance** after any structural edit. An unbalanced tag
   silently nests a column inside its neighbour and the layout collapses
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
- Do not introduce a colour, a font, or an easing curve that is not in
  `:root`.
- Do not hand-edit `specs.html`.
- Do not hide content behind JS by default.
- Do not repeat the previous section's shape.
