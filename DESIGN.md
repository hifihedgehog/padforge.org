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

One family, the system's own: Segoe UI Variable, the face PadForge 6 uses
in the app. No web font loads anywhere on the site or in the docs.

```
--font:         'Segoe UI Variable Text', 'Segoe UI', system-ui, -apple-system, Roboto, sans-serif
--font-display: 'Segoe UI Variable Display', then the --font stack
```

Text takes the Text cut. Anything 18px and larger may take the Display
cut, which is drawn for size. On a machine without Segoe UI Variable the
stack falls to the platform's own interface face.

The scale is deliberately extreme. Tracking tightens and leading
compresses as size grows:

| Class | Size | Weight | Tracking | Leading | Use |
|---|---|---|---|---|---|
| `.display-xl` | 3.2 → 9rem | 700 | -0.03em | 0.95 | Hero only. Once per page. |
| `.display-l` | 2.6 → 6rem | 600 | -0.025em | 0.98 | Section headline. |
| `.display-m` | 2 → 3.6rem | 600 | -0.02em | 1.04 | Moment headline inside a section. |
| `.display-s` | 1.5 → 2.1rem | 600 | -0.012em | 1.15 | Spec block heading. |
| `.lede` | 1.1 → 1.45rem | 400 | n/a | 1.5 | The **one** paragraph under a headline. |

Rules, from the app's type rules of 2026-11-17:

- **No monospace for labels, numbers or eyebrows.** Numbers that change or
  stand in columns take tabular figures (`font-variant-numeric:
  tabular-nums`): the stats, the figures, the compare table, run times,
  file sizes. Code in the docs is code and stays monospace (Cascadia Mono,
  then Consolas).
- **No capitals or letter-spacing for emphasis.** Labels are words in
  sentence or title case, as written in the markup. `text-transform:
  uppercase` appears in no stylesheet.
- **12px is the smallest text, 13px the value size.** On the site that is
  0.75rem and 0.8125rem. In the docs the root is 20px, so 0.6rem and
  0.65rem.
- **Curly quotes and the one-character ellipsis** in text.
- `.lede` is capped at `56ch` and is meant to be the only body paragraph
  in a section. If you need a second, you need `specs.html` or a
  `<details>`.
- `.kicker` (`.eyebrow` on the press page, `.pf-kicker` in the docs) is
  one word or a short phrase in the body face, 16px semibold, in ember.
  It names the section. It is not a sentence.

---

## 4. Color

Every color is one of the app's brushes, defined once in `:root` and
named beside its value, the same names `PadForge.App/WebAssets/css/
padforge.css` uses for the web controller. Do not introduce a color that
is not an app brush.

The landing, specs and press pages are dark. The docs have a light and a
dark scheme, each from the app's theme of the same name.

### Dark (the site, and the docs' dark scheme)

| Token | Value | App brush | Use |
|---|---|---|---|
| `--ground` | `#0a0e15` | SteelGroundBrush | The page. |
| `--band` | `#0f1520` | SteelBandBrush | Alternate sections. |
| `--card` | `#121925` | CardBackgroundFillColorDefaultBrush | Cards, tables, chips, callouts. |
| `--card-lift` | `#161e2b` | SteelCardHoverBrush | A card under the pointer. |
| `--raised` | `#18202e` | SteelRaisedBrush | Buttons, table headers, a steel chapter band. |
| `--raised-lift` | `#212c3d` | SteelLiftBrush | A raised button under the pointer. |
| `--segment` | `#263142` | SteelSegmentBrush | The chosen segment of a switch. |
| `--field` | `#0d131d` | SteelFieldBrush | A text field. |
| `--card-edge` | `#263142` | SteelPillLineBrush | A card's edge. |
| `--card-edge-top` | `#2c374a` | EmberTheme.CardEdgeTop | The lit top of a card's edge. |
| `--line` | `#2a3546` | SteelLineBrush | A control's edge. |
| `--line-soft` | `#1e2734` | SteelLineSoftBrush | Rules between rows and sections. |
| `--text-1` | `#eef2f7` | TextFillColorPrimaryBrush | Headlines, names, values. |
| `--text-sub` | `#cfd7e3` | SubRowTextBrush | Body copy. |
| `--text-2` | `#a9b4c4` | TextFillColorSecondaryBrush | Ledes, descriptions, labels. |
| `--text-3` | `#8693a6` | TextFillColorTertiaryBrush | Quiet notes, placeholders. |
| `--selected` | `#ffffff` | SelectedTextBrush | Text on the chosen segment. |
| `--ember` | `#ff6b2c` | EmberBrush | What is live or picked, and the kicker. |
| `--ember-lift` / `--ember-press` | `#ff8450` / `#e85f25` | EmberLiftBrush / EmberPressBrush | The primary button's hover and press. |
| `--ember-hot` | `#ff8a57` | EmberHotBrush | Inline links. |
| `--ember-ink` | `#160a03` | EmberInkBrush | Text on ember. |
| `--ember-pick` / `--ember-edge` | `#1d1611` / `#4a2c1a` | EmberPickBrush / EmberEdgeBrush | A picked card. |
| `--ember-tint` / `--ember-wash` / `--ember-ring` | ember at 10%, 5%, 30% | EmberTintBrush / EmberWashBrush / EmberRingFaintBrush | A hotspot's halo, the PadForge column, a hotspot's ring. |
| `--ember-glow` | ember at 30% | the light around a lit tile (padforge.css) | The main download button, the picked hotspot. |
| `--link-hover` | `#ffb08a` | LinkHoverBrush | A link under the pointer. |
| `--focus` | `#7cc7ea` | ColdBrush | Focus. |
| `--cold-tint` | cold at 10% | ColdTintBrush | The halo of a focused field. |
| (docs) wait | `#f2b84b` | WaitBrush | Warnings and code strings in the docs. |
| `--veil` | ground at 82% | the ground over a picture (padforge.css) | The nav once the page scrolls. |

The docs page is a step over the pane, as in the app:
ApplicationBackgroundBrush `#0b1018` for the page, SteelPaneBrush
`#0a0e16` for the header, tabs and footer, and SteelPaneLineBrush
`#161e2b` under them.

### Light (the docs' light scheme)

| Token | Value | App brush |
|---|---|---|
| page | `#ffffff` | SteelFieldBrush |
| pane, home cards | `#f3f4f7` | SteelPaneBrush |
| pane line, soft line | `#d6d8de` | SteelPaneLineBrush, SteelLineSoftBrush |
| card edge, line | `#c9cdd6` | SteelPillLineBrush, SteelLineBrush |
| raised | `#e4e7ee` | SteelRaisedBrush |
| raised lift | `#d9dde6` | SteelLiftBrush |
| code well | `#eef0f4` | SteelWellBrush |
| text 1, 2 | `#1a2433`, `#44536b` | TextFillColorPrimaryBrush, TextFillColorSecondaryBrush |
| text 3 | `#6b7a94` | TextFillColorTertiaryBrush. Marks only: 4.34:1 on white, so never text. |
| ember text | `#c24a12` | EmberTextBrush |
| link hover | `#9a3a10` | LinkHoverBrush |
| cold | `#1e6e9f` | ColdBrush |
| wait | `#8f6200` | WaitBrush |

Raw ember `#ff6b2c` is a fill on light (the primary button), never text:
it reads 2.6:1 on white.

### Code in the docs

Keywords cold, strings wait, numbers and constants ember hot (on light,
the link hover brown), comments and punctuation the secondary text, names
the primary text. Code sits on the card in the dark scheme and on the
well in the light one, inside the card edge.

### Old names

The PadForge 5 tokens map onto the brushes like this. A stylesheet that
still names an old token is out of date.

| Old token | Old value | Now |
|---|---|---|
| `--bg` | `#06080c` | `--ground` `#0a0e15` |
| `--bg-raise` | `#0a0d12` | `--card` `#121925` (the compare table) |
| `--bg-alt` | `#0d1117` | `--band` `#0f1520` |
| `--panel` | `#12171f` | `--card` `#121925` |
| `--panel-hi` | `#171d27` | `--card-lift` `#161e2b` |
| `--border` | `#212a36` | `--card-edge` `#263142`, or `--line` `#2a3546` on a control |
| `--border-soft` | `#19202a` | `--line-soft` `#1e2734` |
| `--hairline` | white at 7% | `--line-soft` `#1e2734` |
| `--ember` | `#f2652a` | `--ember` `#ff6b2c` |
| `--ember-bright` | `#ff7d3d` | `--ember-lift` `#ff8450` for fills, `--ember-hot` `#ff8a57` for links |
| `--ember-deep` | `#d9531c` | `--ember-press` `#e85f25` |
| `--ember-glow` | `#f2652a` at 38% | `--ember-glow`, ember at 30% |
| `--ember-glow-soft` | `#f2652a` at 12% | `--ember-tint`, ember at 10% |
| `--grad-ember` | a three-stop gradient | flat `--ember` |
| `--telemetry` | `#6fc3d6` | `--focus` `#7cc7ea` (ColdBrush), for focus only |
| `--telemetry-dim` | `#4d8a9a` | `--text-3` `#8693a6` |
| `--brand-xbox`, `--brand-ps`, `--brand-nin`, `--brand-steam` | four brand colors | removed: a manifest row is a card with no colored bar |
| `--text-hi` | `#f7f9fc` | `--text-1` `#eef2f7` |
| `--text` | `#d4dae3` | `--text-sub` `#cfd7e3` |
| `--text-muted` | `#929fb0` | `--text-2` `#a9b4c4` |
| `--text-dim` | `#5d6877` | `--text-3` `#8693a6` (the old value failed AA) |
| `--font-body`, `--font-display`, `--font-mono` | Instrument Sans, Archivo, JetBrains Mono | `--font`, `--font-display`, no monospace |

**Color in a product shot comes from the product**, never from a filter
or an overlay.

## 5. Shapes and light

**Shapes.** A button is a pill whose corner is half its height (the app's
sidebar controller pill is 38 tall with corner 19). `--pill` is `999px`,
which a browser clamps to exactly half the height. Cards sit on `--card`
with the card edge and its lit top (`--card-edge-top`), corner `--radius`
12px. A panel that holds a table or a card's worth of copy takes
`--radius-lg` 16px. Buttons are raised steel with one flat edge
(`.btn-ghost`). The primary button is filled ember with ember ink
(`.btn-primary`), the app's primary button. A picked card takes ember
pick on an ember edge (`.dg-step.on`). The chosen segment of a switch
takes the segment steel with white text (`.film-pick.on`). A search field
is a pill on the field steel.

**Light means something.** Ember marks what is live or picked, cold blue
marks focus, and nothing else is colored:

- A glow sits only on a live or picked thing: the main download button
  (`.btn-primary`, not the small one in the nav) and the picked hotspot
  (`.hot.on`). Nothing else on the site glows.
- No colored bloom behind a product, a diagram or the download section.
  The app's screens carry their own light, the forging pills and the
  title bar's warmth, and that is the only light on them.
- Depth comes from the card edge, the lit top of an edge, and a long, soft
  contact shadow under a staged screen. Never a hard drop shadow.
- Focus is a 2px cold outline, 3px clear of the control, on every
  focusable thing.

---

## 6. Rhythm and composition

**The failure mode this replaced: five identical chapters in a row.**
Kicker, headline, one screenshot, three columns of gray text, repeat. It
made a rich product read as a spec dump.

The rule now: **no two consecutive sections share a shape.** The current
order alternates deliberately:

1. Hero: centered headline, one large staged program screen
2. Manifest: sticky copy left, a long list of capability cards right, the names in one column
3. Chapter band: one word, full bleed, poster scale
4. Finishes: centered, the program screen morphing its finish
5. The controller: asymmetric two-column, copy left / diagram right
6. Stats: typographic band, four figures across and the fifth centered under them
7. Remap: split, copy left / media bleeding off the right edge
8. Feel: centered headline, full-bleed media
9. Motion: split, **flipped** (media bleeding off the left)
10. Anywhere: centered, full-bleed media
11. Compare: table
12. Gallery: grid
13. Download: centered
14. FAQ: list

Chapter bands (`.chapter`) separate the acts: MAP, FEEL, MOVE, REACH.
One word at poster scale on a full-bleed band. `.chapter-ember` is flat
ember with ember ink, the forge's own color. `.chapter-raised` is raised
steel and `.chapter-steel` is the card on its edge, both with the word in
the primary text. They are the reason a long scroll reads as chapters
rather than an unbroken list, and the ember band is the one place a full
field of accent color is correct.

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

The rig is `.rig` / `.rig-in` in `style.css`, and it is made of three
things, none of which are optional. Drop one and it stops reading as an
object:

1. **Perspective, not a flat rectangle.** `rotateY(-13deg) rotateX(5deg)`
   on a 2400px perspective. `.rig-r` mirrors it, `.rig-soft` halves it.
   Under 900px the angle stands down and the screen goes flat, because
   the angle is a presentation device and never a legibility tax.
2. **A rim.** The card edge all the way around, `--card-edge`, with its lit
   top `--card-edge-top` as an inset line. PadForge's UI is nearly the
   same value as the page, so without a rim the window dissolves into the
   ground.
3. **A contact shadow and a long floor throw.** Two shadows, not one.

The PadForge 5 rig also carried a glass sheen and an ember bloom behind
it. Both were light used as decoration, and PadForge 6 keeps light for
what is live or picked, so both are gone, and `.stage-cy` with them. `.stage`
stays in the markup as a wrapper and draws nothing.

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

**Chips** (`.rig-chip`) pin a short line onto a staged screen. A chip is a pill on the card. They must
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

`#controller` is the centerpiece and the answer to "show, don't tell".

- Hotspot positions are **derived from the app's own generated overlay
  geometry** (`PadForge.App/Models2D/ControllerOverlayLayout.cs`, base
  1467×816). They are percentages of that base, so a ring sits exactly on
  the control it names. If the art changes, re-derive. Do not eyeball.
- **One callout is visible at a time.** That is what lets each label sit
  near its own control without colliding.
- Callouts point **inward**. A label that points outward escapes the
  diagram box and lands in the copy column.
- The label sits on a card with its edge so it stays legible over the
  product as well as over the backdrop. Never rely on what happens to be
  behind.
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
  slightly. Images never do.
- Reveal-on-scroll is staggered with `data-d="1..5"` (90ms steps).
- **`.reveal` is gated on `.js`.** Content is visible by default and JS
  opts into animating it. The opposite order ships a blank page the one
  time a script fails. Never invert this.
- `prefers-reduced-motion` is honored. Keep it that way.
- Auto-advancing components (colorway morph, diagram tour) pause when
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
   harness neutralizes the hero's `min-height`, forces the `.reveal`
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
2. **Check every asset resolves and states its size.** No broken `src`.
   After the screenshots change, run
   `python tools/stamp_image_sizes.py index.html specs.html press/index.html`:
   each `<img>` carries its file's width and height, so a lazy image
   holds its room before it arrives and the page does not grow under
   the reader. `--check` reports a stale tag and changes nothing.
3. **Run the retention diff** if you removed or moved copy: extract the
   visible text of the previous commit and of the new `index.html` +
   `specs.html`, and compare word counts and distinctive terms. Loss must
   be deliberate and stated, never accidental.
4. **Check div balance** after any structural edit. An unbalanced tag
   silently nests a column inside its neighbor and the layout collapses
   to one column, which looks like a CSS bug and is not.
5. **Check it at 780px and 400px.** The callouts stand down, the diagram
   moves above the copy, the nav links collapse. Nothing may scroll
   sideways at 400px, and no text may run past the 16px gutter.
6. **Check contrast.** Every text token on every ground it sits on meets
   WCAG AA, 4.5:1, and the focus ring meets 3:1. Compute the ratio, do not
   judge it by eye. A new token or a new ground adds its row to the check.
7. **Check it with reduced motion and with scripts off.** Every section
   must show in both. `.reveal` is gated on `.js`, and reduced motion
   forces it visible.
8. **Check the docs in both schemes.** Code blocks, tables, notes, the
   search box with results open, and the navigation tabs, in light and
   in dark. Build into a scratch folder with `python -m mkdocs build -d
   <scratch>`, never into `docs/` for a look.
9. **Sweep the type rules.** No `text-transform: uppercase`, no
   `letter-spacing` on a label, no monospace outside code, nothing under
   12px, no web font link in any page or in `wiki/overrides/main.html`.

---

## 12. What not to do

Every item here has already happened once.

- Do not add a grid of text cards. That is what the rebuild removed.
- Do not put a full app window in a small figure.
- Do not use the light 2D plate art on a dark section.
- Do not let a second paragraph creep in under a `.lede`.
- Do not introduce a color, a font, or an easing curve that is not in
  `:root`, and no color that is not an app brush.
- Do not load a web font. The family is the system's Segoe UI Variable.
- Do not set a label, a number or an eyebrow in monospace, and do not
  uppercase or letter-space a word for emphasis.
- Do not put text under 12px.
- Do not glow anything that is not live or picked, and do not put a
  colored bloom behind a product.
- Do not color a row, a bar or a chip to tell it apart from its
  neighbors. Color says live, picked, focus or waiting.
- Do not use a gradient for a button or a band. Ember is flat.
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
